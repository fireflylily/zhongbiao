#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Azure Form Recognizer 文档解析器
功能：
- 使用 Azure 文档智能服务解析文档结构
- 提取标题、段落、表格
- 作为解析对比工具的第5种方法
"""

import os
import time
import tempfile
import subprocess
from typing import List, Dict, Optional
from pathlib import Path

from common import get_module_logger, get_config
from .structure_parser import ChapterNode

logger = get_module_logger("azure_parser")

# 尝试导入docx2pdf转换库
try:
    from docx2pdf import convert as docx_to_pdf_convert
    DOCX2PDF_AVAILABLE = True
except ImportError:
    DOCX2PDF_AVAILABLE = False
    logger.warning("docx2pdf 未安装，将尝试使用其他方法转换")

try:
    from azure.ai.formrecognizer import DocumentAnalysisClient
    from azure.core.credentials import AzureKeyCredential
    AZURE_AVAILABLE = True
except ImportError:
    logger.warning("Azure Form Recognizer SDK 未安装，Azure解析功能不可用")
    logger.warning("请运行: pip install azure-ai-formrecognizer")
    AZURE_AVAILABLE = False


class AzureDocumentParser:
    """Azure Form Recognizer 文档解析器"""

    def __init__(self):
        """初始化 Azure 解析器"""
        self.config = get_config()
        self.logger = get_module_logger("azure_parser")

        if not AZURE_AVAILABLE:
            raise ImportError("Azure Form Recognizer SDK 未安装")

        # 从环境变量获取配置
        self.endpoint = os.getenv('AZURE_FORM_RECOGNIZER_ENDPOINT', '')
        self.key = os.getenv('AZURE_FORM_RECOGNIZER_KEY', '')

        if not self.endpoint or not self.key:
            raise ValueError("Azure Form Recognizer 未配置，请设置 AZURE_FORM_RECOGNIZER_ENDPOINT 和 AZURE_FORM_RECOGNIZER_KEY")

        # 创建客户端
        self.client = DocumentAnalysisClient(
            endpoint=self.endpoint,
            credential=AzureKeyCredential(self.key)
        )

        self.logger.info(f"Azure Form Recognizer 初始化完成: {self.endpoint}")

    # 大文件分批处理配置
    # Azure prebuilt-read 模型限制：单次最大 4MB
    # 扫描PDF每页约 200-500KB，安全起见每批最多 10 页
    MAX_PAGES_PER_BATCH = int(os.getenv('AZURE_OCR_BATCH_SIZE', '10'))  # 每批最多10页
    MAX_FILE_SIZE_MB = 4  # 单次上传最大4MB（Azure限制）

    def extract_text_only(self, pdf_path: str) -> Dict[int, str]:
        """
        使用 Azure Form Recognizer 提取 PDF 全文（OCR功能）

        替代本地 PaddleOCR，速度更快且无需本地计算资源。
        使用 prebuilt-read 模型专门进行文字识别。
        大文件自动分批处理，避免超时。

        Args:
            pdf_path: PDF文件路径

        Returns:
            Dict[int, str]: {页码(从0开始): 该页识别的文本}
        """
        import fitz  # PyMuPDF

        try:
            self.logger.info(f"Azure OCR 开始处理: {pdf_path}")
            start_time = time.time()

            # 检查文件大小和页数
            file_size_mb = os.path.getsize(pdf_path) / (1024 * 1024)
            doc = fitz.open(pdf_path)
            total_pages = len(doc)
            doc.close()

            # 判断是否需要分批处理
            need_batch = file_size_mb > self.MAX_FILE_SIZE_MB or total_pages > self.MAX_PAGES_PER_BATCH

            if need_batch:
                self.logger.info(f"📦 大文件检测: {file_size_mb:.1f}MB, {total_pages}页 → 启用分批处理")
                return self._extract_text_batched(pdf_path, total_pages)
            else:
                return self._extract_text_single(pdf_path)

        except Exception as e:
            self.logger.error(f"Azure OCR 失败: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return {}

    def _extract_text_single(self, pdf_path: str) -> Dict[int, str]:
        """单次处理整个PDF（小文件）"""
        start_time = time.time()

        with open(pdf_path, 'rb') as f:
            document_bytes = f.read()

        poller = self.client.begin_analyze_document(
            "prebuilt-read",
            document_bytes
        )

        result = poller.result()
        elapsed = time.time() - start_time

        page_texts = {}
        if result.pages:
            for page in result.pages:
                page_num = page.page_number - 1
                lines = []
                for line in page.lines or []:
                    lines.append(line.content)
                page_texts[page_num] = '\n'.join(lines)

        total_chars = sum(len(text) for text in page_texts.values())
        self.logger.info(f"Azure OCR 完成: {len(page_texts)} 页, {total_chars} 字符, 耗时 {elapsed:.2f}s")

        return page_texts

    def _extract_text_batched(self, pdf_path: str, total_pages: int) -> Dict[int, str]:
        """分批处理大PDF文件"""
        import fitz
        import tempfile
        import gc

        all_results = {}
        batch_size = self.MAX_PAGES_PER_BATCH
        total_batches = (total_pages + batch_size - 1) // batch_size

        start_time = time.time()

        for batch_idx in range(total_batches):
            start_page = batch_idx * batch_size
            end_page = min(start_page + batch_size, total_pages)
            batch_num = batch_idx + 1

            self.logger.info(f"📄 处理第 {batch_num}/{total_batches} 批（页面 {start_page+1}-{end_page}）")

            try:
                # 提取当前批次的页面到临时PDF
                doc = fitz.open(pdf_path)
                temp_doc = fitz.open()  # 创建空PDF

                for page_num in range(start_page, end_page):
                    temp_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)

                # 保存临时PDF
                with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
                    temp_path = tmp_file.name
                    temp_doc.save(temp_path)

                temp_doc.close()
                doc.close()

                # 调用Azure API处理临时PDF
                with open(temp_path, 'rb') as f:
                    document_bytes = f.read()

                poller = self.client.begin_analyze_document(
                    "prebuilt-read",
                    document_bytes
                )
                result = poller.result()

                # 提取文本，注意页码偏移
                if result.pages:
                    for page in result.pages:
                        # 临时PDF中的页码从1开始，需要转换为原始页码
                        original_page_num = start_page + page.page_number - 1
                        lines = []
                        for line in page.lines or []:
                            lines.append(line.content)
                        all_results[original_page_num] = '\n'.join(lines)

                # 清理临时文件
                os.unlink(temp_path)

                # 强制垃圾回收
                gc.collect()

            except Exception as e:
                self.logger.error(f"批次 {batch_num} 处理失败: {e}")
                # 继续处理下一批，不中断整个流程

        elapsed = time.time() - start_time
        total_chars = sum(len(text) for text in all_results.values())
        self.logger.info(f"✅ Azure OCR 分批处理完成: {len(all_results)}/{total_pages} 页, "
                        f"{total_chars} 字符, 耗时 {elapsed:.2f}s")

        return all_results

    async def ocr_pdf(self, pdf_path: str, page_numbers: Optional[List[int]] = None) -> Dict[int, str]:
        """
        异步接口：使用 Azure Form Recognizer 进行 OCR

        与 OCRParser.ocr_pdf 接口兼容，可作为直接替代。

        Args:
            pdf_path: PDF文件路径
            page_numbers: 要识别的页码列表（从0开始），None表示全部页面

        Returns:
            Dict[int, str]: {页码: 识别文本}
        """
        import asyncio

        # Azure API 是同步的，在线程池中运行
        loop = asyncio.get_event_loop()
        all_results = await loop.run_in_executor(None, self.extract_text_only, pdf_path)

        # 如果指定了页码，只返回指定页面
        if page_numbers is not None:
            return {p: all_results.get(p, '') for p in page_numbers if p in all_results}

        return all_results

    def _convert_docx_to_pdf(self, docx_path: str) -> Optional[str]:
        """
        将 Word 文档转换为 PDF

        Args:
            docx_path: Word文档路径

        Returns:
            PDF文件路径，失败返回None
        """
        try:
            self.logger.info(f"开始转换 Word 到 PDF: {docx_path}")

            # 创建临时PDF文件
            # 注意：LibreOffice 会使用输入文件的基础名称（去掉扩展名）+ .pdf
            temp_dir = tempfile.gettempdir()
            pdf_filename = Path(docx_path).stem + '.pdf'  # 不再添加后缀，LibreOffice会自动处理
            pdf_path = Path(temp_dir) / pdf_filename

            # 方法1: 使用 docx2pdf (Windows/Mac)
            if DOCX2PDF_AVAILABLE:
                self.logger.info("使用 docx2pdf 转换...")
                docx_to_pdf_convert(docx_path, str(pdf_path))
                if pdf_path.exists():
                    self.logger.info(f"转换成功: {pdf_path}")
                    return str(pdf_path)

            # 方法2: 使用 LibreOffice (Linux/Mac/Windows)
            self.logger.info("尝试使用 LibreOffice 转换...")

            # 尝试不同的 LibreOffice 命令名
            for cmd in ['soffice', 'libreoffice']:
                try:
                    result = subprocess.run(
                        [cmd, '--headless', '--convert-to', 'pdf', '--outdir', temp_dir, docx_path],
                        capture_output=True,
                        timeout=30
                    )

                    if result.returncode == 0 and pdf_path.exists():
                        self.logger.info(f"LibreOffice ({cmd}) 转换成功: {pdf_path}")
                        return str(pdf_path)
                except FileNotFoundError:
                    continue

            # 方法3: 使用 unoconv (需要安装)
            self.logger.info("尝试使用 unoconv 转换...")
            result = subprocess.run(
                ['unoconv', '-f', 'pdf', '-o', str(pdf_path), docx_path],
                capture_output=True,
                timeout=30
            )

            if result.returncode == 0 and pdf_path.exists():
                self.logger.info(f"unoconv 转换成功: {pdf_path}")
                return str(pdf_path)

            self.logger.error("所有转换方法均失败")
            return None

        except subprocess.TimeoutExpired:
            self.logger.error("文档转换超时")
            return None
        except Exception as e:
            self.logger.error(f"文档转换失败: {e}")
            return None

    def parse_document_structure(self, doc_path: str) -> Dict:
        """
        使用 Azure Form Recognizer 解析文档结构

        Args:
            doc_path: 文档路径（支持 .docx 自动转换，.pdf 直接处理）

        Returns:
            {
                "success": True/False,
                "chapters": [ChapterNode.to_dict(), ...],
                "statistics": {...},
                "error": "错误信息"
            }
        """
        pdf_to_cleanup = None  # 用于清理临时PDF文件

        try:
            self.logger.info(f"开始使用 Azure 解析文档: {doc_path}")

            # 检查文件格式并处理
            file_ext = Path(doc_path).suffix.lower()
            actual_doc_path = doc_path

            if file_ext == '.docx':
                # .docx 文件自动转换为 PDF
                self.logger.info("检测到 Word 文档，开始自动转换为 PDF...")
                pdf_path = self._convert_docx_to_pdf(doc_path)

                if not pdf_path:
                    return {
                        "success": False,
                        "chapters": [],
                        "statistics": {},
                        "error": "Word转PDF失败。请安装转换工具:\n- pip install docx2pdf\n或\n- 安装 LibreOffice",
                        "method_name": "Azure Form Recognizer"
                    }

                actual_doc_path = pdf_path
                pdf_to_cleanup = pdf_path
                self.logger.info(f"转换成功，使用 PDF: {pdf_path}")

            # 读取文档（现在是PDF格式）
            with open(actual_doc_path, 'rb') as f:
                document_bytes = f.read()

            # 调用 Azure API - 使用 prebuilt-layout 模型
            self.logger.info("调用 Azure Form Recognizer API...")
            start_time = time.time()

            poller = self.client.begin_analyze_document(
                "prebuilt-layout",  # 使用预构建的布局分析模型
                document_bytes
            )

            result = poller.result()
            elapsed = time.time() - start_time

            self.logger.info(f"Azure API 调用完成，耗时 {elapsed:.2f}s")

            # 解析结果
            chapters = self._extract_chapters_from_azure_result(result)

            # 统计
            stats = {
                'total_chapters': len(chapters),
                'total_words': sum(ch.word_count for ch in chapters),
                'total_pages': len(result.pages) if result.pages else 0,
                'total_paragraphs': len(result.paragraphs) if result.paragraphs else 0,
                'total_tables': len(result.tables) if result.tables else 0,
                'api_elapsed': round(elapsed, 3)
            }

            self.logger.info(f"Azure 解析完成: {stats['total_chapters']} 个章节")

            return {
                "success": True,
                "chapters": [ch.to_dict() for ch in chapters],
                "statistics": stats,
                "method_name": "Azure Form Recognizer"
            }

        except Exception as e:
            self.logger.error(f"Azure 文档解析失败: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return {
                "success": False,
                "chapters": [],
                "statistics": {},
                "error": str(e),
                "method_name": "Azure Form Recognizer"
            }
        finally:
            # 清理临时PDF文件
            if pdf_to_cleanup and Path(pdf_to_cleanup).exists():
                try:
                    Path(pdf_to_cleanup).unlink()
                    self.logger.info(f"已清理临时PDF文件: {pdf_to_cleanup}")
                except Exception as e:
                    self.logger.warning(f"清理临时文件失败: {e}")

    def _extract_chapters_from_azure_result(self, result) -> List[ChapterNode]:
        """
        从 Azure 解析结果中提取章节结构

        策略：
        1. 使用 paragraphs 中的 role='title' 或 role='sectionHeading'
        2. 根据字体大小和样式判断层级
        3. 提取每个章节的内容
        """
        chapters = []

        if not result.paragraphs:
            self.logger.warning("Azure 结果中没有段落数据")
            return chapters

        # 查找所有标题段落
        title_paragraphs = []
        for i, para in enumerate(result.paragraphs):
            # Azure 会标记段落角色
            role = para.role if hasattr(para, 'role') else None

            # 判断是否为标题
            is_title = (
                role in ['title', 'sectionHeading', 'heading'] or
                self._is_title_by_style(para)
            )

            if is_title:
                title_paragraphs.append({
                    'index': i,
                    'content': para.content,
                    'role': role,
                    'bounding_box': para.bounding_regions[0].polygon if para.bounding_regions else None
                })

        self.logger.info(f"Azure 识别到 {len(title_paragraphs)} 个标题段落")

        # 构建章节
        for i, title_para in enumerate(title_paragraphs):
            # 确定章节范围（到下一个标题之前）
            start_idx = title_para['index']
            end_idx = title_paragraphs[i + 1]['index'] - 1 if i + 1 < len(title_paragraphs) else len(result.paragraphs) - 1

            # 提取内容
            content_paras = result.paragraphs[start_idx + 1:end_idx + 1]
            content_text = '\n'.join(p.content for p in content_paras)
            word_count = len(content_text.replace(' ', '').replace('\n', ''))

            # 预览文本
            preview_lines = []
            for p in content_paras[:5]:
                text = p.content.strip()
                if text:
                    preview_lines.append(text[:100] + ('...' if len(text) > 100 else ''))
                if len(preview_lines) >= 5:
                    break
            preview_text = '\n'.join(preview_lines) if preview_lines else "(无内容)"

            # 判断层级（简化：根据标题位置）
            level = self._determine_level(title_para, i)

            chapter = ChapterNode(
                id=f"azure_{i}",
                level=level,
                title=title_para['content'],
                para_start_idx=start_idx,
                para_end_idx=end_idx,
                word_count=word_count,
                preview_text=preview_text,
                auto_selected=False,
                skip_recommended=False,
                content_tags=['azure_detected']
            )

            chapters.append(chapter)

        return chapters

    def _is_title_by_style(self, paragraph) -> bool:
        """
        根据样式判断是否为标题

        Azure 会提供字体大小、加粗等样式信息
        """
        # 检查是否有样式信息
        if not hasattr(paragraph, 'spans') or not paragraph.spans:
            return False

        # 简化判断：内容较短且可能是标题格式
        content = paragraph.content.strip()

        # 长度判断
        if len(content) > 100 or len(content) < 2:
            return False

        # 编号模式判断
        import re
        title_patterns = [
            r'^第[一二三四五六七八九十\d]+[章节部分]',
            r'^\d+\.\s',
            r'^\d+\.\d+\s',
            r'^[一二三四五六七八九十]+、',
        ]

        for pattern in title_patterns:
            if re.match(pattern, content):
                return True

        return False

    def _determine_level(self, title_para: Dict, index: int) -> int:
        """
        判断标题层级

        简化策略：
        - 第一个标题通常是一级
        - 根据编号模式判断
        """
        content = title_para['content']
        import re

        # 第X部分/第X章 → Level 1
        if re.match(r'^第[一二三四五六七八九十\d]+[部分章]', content):
            return 1

        # X.Y 格式 → Level 2
        if re.match(r'^\d+\.\d+\s', content):
            return 2

        # X.Y.Z 格式 → Level 3
        if re.match(r'^\d+\.\d+\.\d+\s', content):
            return 3

        # X. 格式 → Level 1
        if re.match(r'^\d+\.\s', content):
            return 1

        # 默认 Level 2
        return 2


def is_azure_available() -> bool:
    """检查 Azure Form Recognizer 是否可用"""
    if not AZURE_AVAILABLE:
        return False

    endpoint = os.getenv('AZURE_FORM_RECOGNIZER_ENDPOINT', '')
    key = os.getenv('AZURE_FORM_RECOGNIZER_KEY', '')

    return bool(endpoint and key)


if __name__ == "__main__":
    # 测试代码
    if is_azure_available():
        print("Azure Form Recognizer 配置已就绪")
        parser = AzureDocumentParser()
        print(f"端点: {parser.endpoint}")
    else:
        print("Azure Form Recognizer 未配置或SDK未安装")
        print("请设置环境变量:")
        print("  - AZURE_FORM_RECOGNIZER_ENDPOINT")
        print("  - AZURE_FORM_RECOGNIZER_KEY")
        print("并安装SDK: pip install azure-ai-formrecognizer")
