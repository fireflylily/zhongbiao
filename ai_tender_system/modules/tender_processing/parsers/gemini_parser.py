#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gemini AI解析器 - 使用Google Gemini多模态模型解析文档结构

优势:
- 直接理解PDF文档
- 支持结构化JSON输出
- 理解语义,不只是识别样式
- 支持多语言和复杂布局

注意:
- Gemini API不支持.docx格式,会自动转换为PDF
"""

import os
import sys
import json
import time
import tempfile
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from common import get_module_logger
from . import BaseStructureParser, ParserMetrics
from ..level_analyzer import LevelAnalyzer

# 尝试导入docx2pdf转换库
try:
    from docx2pdf import convert as docx_to_pdf_convert
    DOCX2PDF_AVAILABLE = True
except ImportError:
    DOCX2PDF_AVAILABLE = False


class GeminiParser(BaseStructureParser):
    """Gemini AI文档结构解析器"""

    def __init__(self):
        super().__init__()
        self.logger = get_module_logger("parsers.gemini")
        self.api_key = os.getenv("GEMINI_API_KEY")

        # 方案B: 模型配置优化
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash-002")

        # 方案C: Context Caching配置
        self.enable_cache = os.getenv("GEMINI_ENABLE_CACHE", "true").lower() == "true"
        self.cache_ttl = int(os.getenv("GEMINI_CACHE_TTL", "3600"))

        # 方案A: 重试配置
        self.max_retries = int(os.getenv("GEMINI_MAX_RETRIES", "3"))
        self.retry_delay = int(os.getenv("GEMINI_RETRY_DELAY", "2"))

        # 初始化层级分析器
        self.level_analyzer = LevelAnalyzer()

        # 方案C: 缓存管理器(字典: 文件哈希 -> 缓存信息)
        self.cache_manager = {}

        # 价格配置(元/百万token) - 更新为Flash 1.5定价
        self.pricing = {
            "gemini-1.5-flash-002": {"input": 0.015, "output": 0.06, "cache": 0.0015},  # Flash 1.5(推荐)
            "gemini-2.0-flash": {"input": 0.015, "output": 0.06, "cache": 0.00375},     # Flash 2.0
            "gemini-2.5-pro": {"input": 0.25, "output": 1.0, "cache": 0.025},           # Pro版
        }

        self.logger.info(
            f"[Gemini] 初始化完成: model={self.model_name}, "
            f"cache={self.enable_cache}, ttl={self.cache_ttl}s, "
            f"max_retries={self.max_retries}"
        )

    def _convert_docx_to_pdf(self, docx_path: str) -> Optional[str]:
        """
        将 Word 文档转换为 PDF（复用自 Azure Parser）

        Args:
            docx_path: Word文档路径

        Returns:
            PDF文件路径，失败返回None
        """
        try:
            self.logger.info(f"[Gemini] 开始转换 Word 到 PDF: {docx_path}")

            # 创建临时PDF文件
            # 注意：LibreOffice 会使用输入文件的基础名称（去掉扩展名）+ .pdf
            temp_dir = tempfile.gettempdir()
            pdf_filename = Path(docx_path).stem + '.pdf'  # 不再添加后缀，LibreOffice会自动处理
            pdf_path = Path(temp_dir) / pdf_filename

            # 方法1: 使用 docx2pdf (Windows/Mac)
            if DOCX2PDF_AVAILABLE:
                self.logger.info("[Gemini] 使用 docx2pdf 转换...")
                docx_to_pdf_convert(docx_path, str(pdf_path))
                if pdf_path.exists():
                    self.logger.info(f"[Gemini] 转换成功: {pdf_path}")
                    return str(pdf_path)

            # 方法2: 使用 LibreOffice (Linux/Mac/Windows)
            self.logger.info("[Gemini] 尝试使用 LibreOffice 转换...")

            # 尝试不同的 LibreOffice 命令名
            for cmd in ['soffice', 'libreoffice']:
                try:
                    result = subprocess.run(
                        [cmd, '--headless', '--convert-to', 'pdf', '--outdir', temp_dir, docx_path],
                        capture_output=True,
                        timeout=30
                    )

                    if result.returncode == 0 and pdf_path.exists():
                        self.logger.info(f"[Gemini] LibreOffice ({cmd}) 转换成功: {pdf_path}")
                        return str(pdf_path)
                except FileNotFoundError:
                    continue

            # 方法3: 使用 unoconv (需要安装)
            self.logger.info("[Gemini] 尝试使用 unoconv 转换...")
            result = subprocess.run(
                ['unoconv', '-f', 'pdf', '-o', str(pdf_path), docx_path],
                capture_output=True,
                timeout=30
            )

            if result.returncode == 0 and pdf_path.exists():
                self.logger.info(f"[Gemini] unoconv 转换成功: {pdf_path}")
                return str(pdf_path)

            self.logger.error("[Gemini] 所有转换方法均失败")
            return None

        except subprocess.TimeoutExpired:
            self.logger.error("[Gemini] 文档转换超时")
            return None
        except Exception as e:
            self.logger.error(f"[Gemini] 文档转换失败: {e}")
            return None

    def _get_file_hash(self, file_path: str) -> str:
        """
        计算文件SHA256哈希值(用于缓存键)

        Args:
            file_path: 文件路径

        Returns:
            文件的SHA256哈希值
        """
        import hashlib
        with open(file_path, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()

    def _get_or_create_cache(self, uploaded_file, doc_hash: str) -> Optional[str]:
        """
        获取或创建文档缓存

        Args:
            uploaded_file: 已上传的Gemini文件对象
            doc_hash: 文档哈希值

        Returns:
            缓存名称,如果不启用缓存则返回None
        """
        if not self.enable_cache:
            return None

        # 检查是否有该文档的有效缓存
        if doc_hash in self.cache_manager:
            cached_info = self.cache_manager[doc_hash]
            # 检查缓存是否过期
            if time.time() - cached_info['created_at'] < self.cache_ttl:
                cache_name = cached_info['cache_name']
                self.logger.info(f"[Gemini缓存] 命中缓存: {cache_name}")
                return cache_name
            else:
                self.logger.info(f"[Gemini缓存] 缓存已过期,将创建新缓存")
                del self.cache_manager[doc_hash]

        # 创建新缓存
        try:
            import google.generativeai as genai

            self.logger.info(f"[Gemini缓存] 创建新缓存: model={self.model_name}, ttl={self.cache_ttl}s")

            cache = genai.caching.CachedContent.create(
                model=self.model_name,
                display_name=f"tender_doc_{doc_hash[:8]}",
                system_instruction="你是一个专业的招标文档分析专家,擅长提取文档的章节结构",
                contents=[uploaded_file],
                ttl=f"{self.cache_ttl}s"
            )

            # 保存缓存信息
            self.cache_manager[doc_hash] = {
                'cache_name': cache.name,
                'created_at': time.time(),
                'file_uri': uploaded_file.uri
            }

            self.logger.info(
                f"[Gemini缓存] 缓存创建成功: {cache.name}, "
                f"过期时间: {self.cache_ttl}s"
            )

            return cache.name

        except Exception as e:
            self.logger.warning(f"[Gemini缓存] 创建缓存失败: {e}, 将使用普通模式")
            return None

    def parse_structure(self, doc_path: str) -> Dict:
        """使用Gemini解析文档结构"""
        start_time = time.time()
        pdf_to_cleanup = None  # 用于清理临时PDF文件

        try:
            self.logger.info(f"[Gemini解析器] 开始解析: {doc_path}")

            # 检查依赖
            if not self.is_available():
                raise ValueError(
                    "Gemini API未配置\n"
                    "请在.env文件添加: GEMINI_API_KEY=your_key\n"
                    "获取密钥: https://ai.google.dev/"
                )

            # 导入Gemini SDK
            import google.generativeai as genai

            # 配置API
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(self.model_name)

            # 检查文件格式并处理
            file_ext = Path(doc_path).suffix.lower()
            actual_doc_path = doc_path

            if file_ext == '.docx':
                # .docx 文件自动转换为 PDF（Gemini API不支持.docx）
                self.logger.info("[Gemini] 检测到 Word 文档，开始自动转换为 PDF...")
                pdf_path = self._convert_docx_to_pdf(doc_path)

                if not pdf_path:
                    return {
                        "success": False,
                        "chapters": [],
                        "statistics": {},
                        "error": (
                            "Word转PDF失败。Gemini API不支持.docx格式，需要转换为PDF。\n"
                            "请安装转换工具:\n"
                            "- pip install docx2pdf\n"
                            "或\n"
                            "- 安装 LibreOffice"
                        ),
                        "method_name": "Gemini AI解析器"
                    }

                actual_doc_path = pdf_path
                pdf_to_cleanup = pdf_path
                self.logger.info(f"[Gemini] 转换成功，使用 PDF: {pdf_path}")

            # 上传文档（现在是PDF格式）
            self.logger.info(f"[Gemini] 上传文档到Gemini...")
            uploaded_file = genai.upload_file(actual_doc_path)
            self.logger.info(f"[Gemini] 文档已上传,URI: {uploaded_file.uri}")

            # 方案C: 获取或创建文档缓存
            doc_hash = self._get_file_hash(actual_doc_path)
            cache_name = self._get_or_create_cache(uploaded_file, doc_hash)

            # 构造Prompt
            prompt = self._build_prompt()

            # 方案A: 带重试机制的Gemini调用
            response = None
            last_error = None

            for attempt in range(self.max_retries):
                try:
                    self.logger.info(
                        f"[Gemini] 调用模型: {self.model_name} "
                        f"(尝试 {attempt+1}/{self.max_retries})"
                    )

                    # 根据是否有缓存选择调用方式
                    if cache_name:
                        # 使用缓存模式
                        response = model.generate_content(
                            [prompt],  # 只发送prompt,文档在缓存中
                            config=genai.GenerationConfig(
                                cached_content=cache_name,  # 引用缓存
                                response_mime_type="application/json",
                                temperature=0.1
                            )
                        )
                        self.logger.info("[Gemini] 使用缓存模式调用成功")
                    else:
                        # 普通模式
                        response = model.generate_content(
                            [uploaded_file, prompt],  # 直接发送文档
                            generation_config=genai.GenerationConfig(
                                response_mime_type="application/json",
                                temperature=0.1
                            )
                        )
                        self.logger.info("[Gemini] 使用普通模式调用成功")

                    # 成功,跳出重试循环
                    break

                except Exception as e:
                    error_msg = str(e)
                    last_error = e

                    # 检测429错误(Resource exhausted)
                    if "429" in error_msg or "Resource exhausted" in error_msg:
                        if attempt < self.max_retries - 1:
                            # 指数退避: 2s, 4s, 8s
                            delay = self.retry_delay * (2 ** attempt)
                            self.logger.warning(
                                f"[Gemini] 遇到429配额限制错误, {delay}秒后重试 "
                                f"(第{attempt+1}/{self.max_retries}次)"
                            )
                            time.sleep(delay)
                            continue
                        else:
                            self.logger.error(
                                f"[Gemini] 重试{self.max_retries}次后仍失败,放弃"
                            )
                            raise e
                    else:
                        # 非429错误,直接抛出
                        raise e

            # 如果所有重试都失败
            if response is None:
                raise last_error or Exception("Gemini调用失败")

            # 解析响应
            gemini_result = json.loads(response.text)
            self.logger.debug(f"[Gemini] 原始响应: {json.dumps(gemini_result, ensure_ascii=False, indent=2)}")

            # 转换为系统格式
            chapters = self._convert_gemini_to_chapters(gemini_result)

            # 后处理：修正层级（使用LevelAnalyzer）
            chapters = self._postprocess_gemini_levels(chapters)

            # 计算统计信息
            statistics = self._calculate_statistics(chapters)

            # 计算成本(考虑缓存token折扣)
            token_count = response.usage_metadata.total_token_count if hasattr(response, 'usage_metadata') else 1000
            cached_token_count = 0
            if cache_name and hasattr(response, 'usage_metadata'):
                # 如果使用了缓存,获取缓存token数量
                cached_token_count = getattr(response.usage_metadata, 'cached_content_token_count', 0)
            api_cost = self._calculate_cost(token_count, cached_token_count)

            # 计算性能指标
            parse_time = time.time() - start_time
            metrics = ParserMetrics(
                parser_name="gemini",
                parse_time=parse_time,
                chapters_found=len(chapters),
                success=True,
                confidence_score=95.0,  # Gemini通常有很高的置信度
                api_cost=api_cost
            )

            self.logger.info(
                f"[Gemini解析器] 完成: 找到{len(chapters)}个章节, "
                f"耗时{parse_time:.2f}秒, 成本≈{api_cost:.4f}元"
            )

            return {
                "success": True,
                "chapters": [ch.to_dict() if hasattr(ch, 'to_dict') else ch for ch in chapters],
                "statistics": statistics,
                "method_name": "Gemini AI解析器",
                "performance": {
                    "elapsed": parse_time,
                    "api_cost": api_cost,
                    "token_count": token_count
                },
                "gemini_metadata": {
                    "model": self.model_name,
                    "token_count": token_count,
                    "file_uri": uploaded_file.uri
                }
            }

        except Exception as e:
            parse_time = time.time() - start_time
            error_msg = str(e)
            self.logger.error(f"[Gemini解析器] 失败: {error_msg}")

            return {
                "success": False,
                "chapters": [],
                "statistics": {},
                "error": error_msg,
                "method_name": "Gemini AI解析器",
                "performance": {
                    "elapsed": parse_time
                }
            }
        finally:
            # 清理临时PDF文件
            if pdf_to_cleanup and Path(pdf_to_cleanup).exists():
                try:
                    Path(pdf_to_cleanup).unlink()
                    self.logger.info(f"[Gemini] 已清理临时PDF文件: {pdf_to_cleanup}")
                except Exception as e:
                    self.logger.warning(f"[Gemini] 清理临时文件失败: {e}")

    def _build_prompt(self) -> str:
        """构造Gemini Prompt"""
        return """
你是一个专业的招标文档分析专家。请仔细分析这份招标文档,提取其完整的章节结构。

任务要求:
1. 识别所有一级、二级、三级标题(章、节、条)
2. 判断每个章节是否属于"重要章节"(投标须知、技术要求、商务要求、评分标准等)
3. 标记应该跳过的章节(合同条款、附件清单、目录、封面等)
4. 记录每个章节的起始页码(如果可识别)

重要章节关键词(应标记auto_selected=true):
- 投标须知、供应商须知、响应人须知
- 技术要求、技术需求、需求书、技术规格、性能指标
- 商务要求、商务条款、付款方式、交付要求
- 评分标准、评标办法、评分细则、打分标准

应跳过的章节关键词(应标记skip_recommended=true):
- 合同条款、合同文本、合同范本、合同格式
- 目录、索引、附件清单、附表
- 封面、声明、授权书、承诺书

返回JSON格式:
{
  "chapters": [
    {
      "level": 1,
      "title": "第一章 投标须知",
      "auto_selected": true,
      "skip_recommended": false,
      "page_start": 5,
      "word_count": 1200,
      "children": [
        {
          "level": 2,
          "title": "1.1 项目概况",
          "auto_selected": false,
          "skip_recommended": false,
          "page_start": 5,
          "word_count": 300,
          "children": []
        }
      ]
    }
  ]
}

注意事项:
1. 保持完整的层级结构(parent-children关系)
2. level: 1=一级标题, 2=二级标题, 3=三级标题
3. 如果无法确定页码,page_start设为0
4. word_count: 估算该章节的字数(不包括空格和换行符),如果无法估算设为0
5. children是数组,即使为空也要包含[]
6. 只返回JSON,不要有任何其他解释文字
"""

    def _convert_gemini_to_chapters(self, gemini_result: Dict) -> List:
        """将Gemini返回的JSON转换为ChapterNode对象"""
        from ..structure_parser import ChapterNode

        def convert_chapter(ch_data: Dict, parent_id: str = "", idx: int = 0) -> ChapterNode:
            """递归转换章节"""
            # 生成章节ID
            if parent_id:
                chapter_id = f"{parent_id}_{idx}"
            else:
                chapter_id = f"ch_{idx}"

            # 创建ChapterNode
            chapter = ChapterNode(
                id=chapter_id,
                level=ch_data.get('level', 1),
                title=ch_data.get('title', '未命名章节'),
                para_start_idx=ch_data.get('page_start', 0),  # 使用页码作为索引
                para_end_idx=None,  # Gemini无法提供
                word_count=ch_data.get('word_count', 0),  # 从Gemini返回的数据中获取
                preview_text="",  # 需要后续提取
                auto_selected=ch_data.get('auto_selected', False),
                skip_recommended=ch_data.get('skip_recommended', False),
                children=[]
            )

            # 递归处理子章节
            children_data = ch_data.get('children', [])
            for child_idx, child_data in enumerate(children_data):
                child = convert_chapter(child_data, chapter_id, child_idx)
                chapter.children.append(child)

            return chapter

        # 转换所有顶层章节
        chapters = []
        for idx, ch_data in enumerate(gemini_result.get('chapters', [])):
            chapter = convert_chapter(ch_data, "", idx)
            chapters.append(chapter)

        return chapters

    def _calculate_statistics(self, chapters: List) -> Dict:
        """计算章节统计信息"""
        def count_chapters(chs):
            total = len(chs)
            auto_selected = sum(1 for ch in chs if ch.auto_selected)
            skip_recommended = sum(1 for ch in chs if ch.skip_recommended)
            total_words = sum(ch.word_count for ch in chs)

            # 递归统计子章节
            for ch in chs:
                if ch.children:
                    child_stats = count_chapters(ch.children)
                    total += child_stats['total_chapters']
                    auto_selected += child_stats['auto_selected']
                    skip_recommended += child_stats['skip_recommended']
                    total_words += child_stats['total_words']

            return {
                'total_chapters': total,
                'auto_selected': auto_selected,
                'skip_recommended': skip_recommended,
                'total_words': total_words
            }

        stats = count_chapters(chapters)

        return stats

    def _postprocess_gemini_levels(self, chapters: List) -> List:
        """
        对Gemini返回的章节进行层级后处理修正

        Gemini在PDF上工作，可能丢失Word的格式信息，
        我们使用LevelAnalyzer基于编号格式进行修正

        Args:
            chapters: Gemini解析的ChapterNode列表

        Returns:
            层级修正后的章节列表
        """
        if not chapters:
            return chapters

        self.logger.info("[Gemini后处理] 开始修正章节层级...")

        # 步骤1: 扁平化提取所有章节
        flat_items = []

        def flatten(chs, depth=0):
            for ch in chs:
                flat_items.append({
                    'title': ch.title,
                    'chapter': ch,
                    'original_level': ch.level
                })
                if ch.children:
                    flatten(ch.children, depth + 1)

        flatten(chapters)

        self.logger.info(f"[Gemini后处理] 扁平化了 {len(flat_items)} 个章节")

        # 步骤2: 使用LevelAnalyzer整体分析层级
        corrected_levels = self.level_analyzer.analyze_toc_hierarchy(flat_items)

        # 步骤3: 应用修正后的层级
        correction_count = 0
        for i, item in enumerate(flat_items):
            original = item['original_level']
            corrected = corrected_levels[i]

            if original != corrected:
                correction_count += 1
                self.logger.debug(
                    f"[Gemini后处理] 修正: '{item['title'][:30]}...' "
                    f"({original}级 -> {corrected}级)"
                )

            item['chapter'].level = corrected

        self.logger.info(
            f"[Gemini后处理] 完成: 修正了 {correction_count}/{len(flat_items)} 个章节的层级"
        )

        return chapters

    def _calculate_cost(self, token_count: int, cached_token_count: int = 0) -> float:
        """计算API调用成本(支持缓存token折扣)

        Args:
            token_count: 总token数
            cached_token_count: 缓存token数(享受90%折扣)

        Returns:
            成本(元)
        """
        model_pricing = self.pricing.get(
            self.model_name,
            self.pricing["gemini-1.5-flash-002"]  # 默认使用Flash 1.5定价
        )

        # 计算非缓存token数量
        regular_token_count = token_count - cached_token_count

        # 假设输入输出token比例为 7:3
        regular_input_tokens = regular_token_count * 0.7
        regular_output_tokens = regular_token_count * 0.3

        # 常规token成本
        regular_cost = (
            (regular_input_tokens / 1_000_000) * model_pricing["input"] +
            (regular_output_tokens / 1_000_000) * model_pricing["output"]
        )

        # 缓存token成本(仅输入token享受折扣)
        cache_cost = 0
        if cached_token_count > 0 and "cache" in model_pricing:
            cache_cost = (cached_token_count / 1_000_000) * model_pricing["cache"]
            self.logger.info(
                f"[Gemini成本] 缓存token: {cached_token_count}, "
                f"节省: ¥{(cached_token_count / 1_000_000) * (model_pricing['input'] - model_pricing['cache']):.4f}"
            )

        total_cost = regular_cost + cache_cost

        return round(total_cost, 4)

    def is_available(self) -> bool:
        """检查Gemini API是否可用"""
        if not self.api_key:
            return False

        try:
            import google.generativeai
            return True
        except ImportError:
            self.logger.warning("[Gemini] google-generativeai未安装,运行: pip install google-generativeai")
            return False

    def get_parser_info(self) -> Dict:
        """获取解析器信息"""
        return {
            "name": "gemini",
            "display_name": "Gemini AI",
            "description": (
                "基于Google Gemini多模态大模型的智能文档解析\n"
                f"• 模型: {self.model_name}\n"
                "• 优势: 理解语义、支持复杂布局、多语言、结构化输出\n"
                "• 劣势: 需要API密钥、有一定成本\n"
                "• 适用: 格式不规范、复杂布局的文档\n"
                "• 支持: PDF直接处理，Word自动转换为PDF"
            ),
            "requires_api": True,
            "cost_per_page": 0.01,  # 估算
            "available": self.is_available(),
            "model": self.model_name,
            "capabilities": [
                "直接理解PDF",
                "自动转换Word→PDF",
                "语义理解",
                "结构化输出",
                "多语言支持",
                "复杂布局识别"
            ]
        }


# 注册解析器
from . import ParserFactory
ParserFactory.register_parser('gemini', GeminiParser)
