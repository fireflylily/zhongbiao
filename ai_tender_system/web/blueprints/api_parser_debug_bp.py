#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
目录解析方法对比调试 API
功能：
- 上传标书文档并运行所有解析方法
- 对比不同解析方法的准确率
- 支持人工标注正确答案
- 计算准确率指标（P/R/F1）
"""

import os
import json
import uuid
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename
from docx import Document

from common import get_module_logger, get_config
from common.database import get_knowledge_base_db
from modules.tender_processing.structure_parser import DocumentStructureParser, ChapterNode

# 尝试导入 Azure 解析器
try:
    from modules.tender_processing.azure_parser import AzureDocumentParser, is_azure_available
    AZURE_PARSER_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Azure 解析器不可用: {e}")
    AZURE_PARSER_AVAILABLE = False

    def is_azure_available():
        return False

logger = get_module_logger("api_parser_debug")

api_parser_debug_bp = Blueprint('api_parser_debug', __name__, url_prefix='/api/parser-debug')


class ParserDebugger:
    """解析方法对比调试器"""

    def __init__(self, doc_path: str):
        """
        初始化调试器

        Args:
            doc_path: Word文档路径
        """
        self.doc_path = doc_path
        self.parser = DocumentStructureParser()
        self.doc = Document(doc_path)

        # 文档信息
        self.total_paragraphs = len(self.doc.paragraphs)
        self.has_toc = False
        self.toc_items_count = 0
        self.toc_start_idx = None
        self.toc_end_idx = None

        # 计算文档总字数 (去除空格)
        self.total_chars = sum(len(p.text.replace(' ', '').replace('\t', '')) for p in self.doc.paragraphs)

        # 预先检测目录
        self._detect_toc_info()

    def _detect_toc_info(self):
        """检测目录信息"""
        try:
            toc_idx = self.parser._find_toc_section(self.doc)
            if toc_idx is not None:
                self.has_toc = True
                self.toc_start_idx = toc_idx
                toc_items, toc_end_idx = self.parser._parse_toc_items(self.doc, toc_idx)
                self.toc_items_count = len(toc_items)
                self.toc_end_idx = toc_end_idx
                logger.info(f"检测到目录: {self.toc_items_count} 项，位于段落 {toc_idx}-{toc_end_idx}")
        except Exception as e:
            logger.warning(f"目录检测失败: {e}")

    def get_document_info(self) -> Dict:
        """获取文档基本信息"""
        return {
            'filename': Path(self.doc_path).name,
            'total_paragraphs': self.total_paragraphs,
            'total_chars': self.total_chars,  # 文档总字数
            'has_toc': self.has_toc,
            'toc_items_count': self.toc_items_count,
            'toc_start_idx': self.toc_start_idx,
            'toc_end_idx': self.toc_end_idx
        }

    def run_all_methods(self) -> Dict:
        """
        运行所有解析方法

        Returns:
            {
                'semantic': {...},
                'style': {...},
                'hybrid': {...},
                'azure': {...},  # 可选
                'docx_native': {...}
            }
        """
        results = {}

        # 方法1: 语义锚点解析
        results['semantic'] = self._run_with_timing(
            self._run_semantic_anchors,
            "语义锚点解析"
        )

        # 方法2: 样式识别(增强)
        results['style'] = self._run_with_timing(
            self._run_style_detection,
            "样式识别"
        )

        # 方法3: 混合启发式识别
        results['hybrid'] = self._run_with_timing(
            self._run_hybrid_detection,
            "混合启发式识别"
        )

        # 方法4: Azure Form Recognizer（如果可用）
        if is_azure_available() and AZURE_PARSER_AVAILABLE:
            results['azure'] = self._run_with_timing(
                self._run_azure_parser,
                "Azure Form Recognizer"
            )
        else:
            results['azure'] = {
                'success': False,
                'error': 'Azure Form Recognizer 未配置或SDK未安装',
                'chapters': [],
                'method_name': 'Azure Form Recognizer',
                'performance': {'elapsed': 0}
            }

        # 方法5: Word大纲级别识别
        results['docx_native'] = self._run_with_timing(
            self._run_docx_native,
            "Word大纲级别识别"
        )

        return results

    def _run_with_timing(self, method_func, method_name: str) -> Dict:
        """
        运行方法并计时

        Args:
            method_func: 要运行的方法
            method_name: 方法名称（用于日志）

        Returns:
            包含结果和性能指标的字典
        """
        logger.info(f"开始运行: {method_name}")
        start_time = time.time()

        try:
            result = method_func()
            elapsed = time.time() - start_time

            result['performance'] = {
                'elapsed': round(elapsed, 3),
                'elapsed_formatted': f"{elapsed:.3f}s"
            }

            logger.info(f"{method_name} 完成，耗时 {elapsed:.3f}s")
            return result

        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"{method_name} 失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'chapters': [],
                'performance': {'elapsed': round(elapsed, 3)}
            }

    def _run_semantic_anchors(self) -> Dict:
        """方法1: 强制使用语义锚点解析（包含子章节识别）"""
        if not self.has_toc:
            return {
                'success': False,
                'error': '文档无目录，无法使用语义锚点解析',
                'chapters': [],
                'method_name': '语义锚点解析'
            }

        try:
            toc_items, toc_end_idx = self.parser._parse_toc_items(self.doc, self.toc_start_idx)
            toc_targets = [item['title'] for item in toc_items]

            chapters = self.parser._parse_chapters_by_semantic_anchors(
                self.doc, toc_targets, toc_end_idx
            )

            # ⭐ 关键修复：为每个章节识别子章节（与旧目录定位方法保持一致）
            for i, chapter in enumerate(chapters):
                logger.info(f"正在识别章节 '{chapter.title}' 的子章节...")
                subsections = self.parser._parse_subsections_in_range(
                    self.doc,
                    chapter.para_start_idx,
                    chapter.para_end_idx,
                    chapter.level,
                    f"sem_{i}"
                )

                if subsections:
                    chapter.children = subsections
                    # 注意：不需要累加子章节字数，因为父章节的word_count已经包含了
                    # 其段落范围内的所有内容（包括子章节所在的段落）
                    logger.info(f"  └─ 识别到 {len(subsections)} 个子章节（父章节字数: {chapter.word_count}）")

            # 构建树形结构
            chapter_tree = self.parser._build_chapter_tree(chapters)

            # 计算统计信息
            total_detected_words = sum(ch.word_count for ch in chapters)
            coverage_rate = total_detected_words / self.total_chars if self.total_chars > 0 else 0

            # 覆盖率警告：如果识别字数少于文档总字数的60%,可能有问题
            coverage_warning = None
            if coverage_rate < 0.60:
                coverage_warning = f"⚠️ 覆盖率仅{coverage_rate:.1%},可能漏识别了章节"
                logger.warning(f"语义锚点解析 - {coverage_warning}")

            return {
                'success': True,
                'method_name': '语义锚点解析',
                'chapters': [ch.to_dict() for ch in chapter_tree],
                'statistics': {
                    'total_chapters': len(chapters),
                    'total_words': total_detected_words,
                    'document_total_chars': self.total_chars,
                    'coverage_rate': round(coverage_rate, 4),
                    'coverage_warning': coverage_warning,
                    'toc_items_count': len(toc_items),
                    'match_rate': len(chapters) / len(toc_items) if toc_items else 0
                }
            }
        except Exception as e:
            logger.error(f"语义锚点解析失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise

    def _run_style_detection(self) -> Dict:
        """方法3: 强制使用样式识别方案"""
        try:
            # 直接使用样式解析
            chapters = self.parser._parse_chapters_from_doc(self.doc)
            chapters = self.parser._locate_chapter_content(self.doc, chapters)

            # 构建树形结构
            chapter_tree = self.parser._build_chapter_tree(chapters)

            # 计算统计信息
            total_detected_words = sum(ch.word_count for ch in chapters)
            coverage_rate = total_detected_words / self.total_chars if self.total_chars > 0 else 0

            # 覆盖率警告
            coverage_warning = None
            if coverage_rate < 0.60:
                coverage_warning = f"⚠️ 覆盖率仅{coverage_rate:.1%},可能漏识别了章节"
                logger.warning(f"样式识别 - {coverage_warning}")

            return {
                'success': True,
                'method_name': '样式识别',
                'chapters': [ch.to_dict() for ch in chapter_tree],
                'statistics': {
                    'total_chapters': len(chapters),
                    'total_words': total_detected_words,
                    'document_total_chars': self.total_chars,
                    'coverage_rate': round(coverage_rate, 4),
                    'coverage_warning': coverage_warning
                }
            }
        except Exception as e:
            logger.error(f"样式识别失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise

    def _run_hybrid_detection(self) -> Dict:
        """方法3: 混合启发式识别 - 综合多种特征判断标题"""
        import re

        try:
            chapters = []

            for i, para in enumerate(self.doc.paragraphs):
                text = para.text.strip()

                # 基础过滤: 跳过空行和过长文本
                if not text or len(text) > 150 or len(text) < 2:
                    continue

                # 计算多维度得分
                score = 0

                # 特征1: 编号模式识别 (30分)
                numbering_patterns = [
                    (r'^第[一二三四五六七八九十\d]+[章部分]', 30),  # 第X章/部分
                    (r'^\d+\.\s+\S', 25),  # 1. xxx
                    (r'^\d+\.\d+\s+\S', 20),  # 1.1 xxx
                    (r'^\d+\.\d+\.\d+\s+\S', 15),  # 1.1.1 xxx
                    (r'^[一二三四五六七八九十]+、', 20),  # 一、xxx
                    (r'^\([一二三四五六七八九十\d]+\)', 15),  # (一)
                ]

                for pattern, points in numbering_patterns:
                    if re.match(pattern, text):
                        score += points
                        break

                # 特征2: 字体大小和加粗 (25分)
                if para.runs:
                    sizes = []
                    bold_count = 0
                    total_runs = len(para.runs)

                    for run in para.runs:
                        if run.font.size:
                            sizes.append(run.font.size.pt)
                        if run.bold:
                            bold_count += 1

                    # 加粗比例
                    if bold_count >= total_runs * 0.5:
                        score += 10

                    # 字体大小
                    if sizes:
                        avg_size = sum(sizes) / len(sizes)
                        if avg_size >= 16:
                            score += 15
                        elif avg_size >= 13:
                            score += 10
                        elif avg_size >= 10:
                            score += 5

                # 特征3: 段落缩进 (20分)
                try:
                    if para.paragraph_format.left_indent:
                        indent_pt = para.paragraph_format.left_indent.pt
                        # 缩进越小越可能是标题
                        if indent_pt == 0:
                            score += 20
                        elif indent_pt <= 10:
                            score += 10
                        elif indent_pt <= 20:
                            score += 5
                except (AttributeError, TypeError):
                    # 无缩进信息时默认给一些分数
                    score += 10

                # 特征4: 内容长度 (15分)
                text_len = len(text)
                if text_len <= 30:
                    score += 15
                elif text_len <= 50:
                    score += 10
                elif text_len <= 80:
                    score += 5

                # 特征5: 位置特征 (10分)
                # 文档前部的短文本更可能是标题
                if i < len(self.doc.paragraphs) * 0.1:  # 前10%
                    score += 10
                elif i < len(self.doc.paragraphs) * 0.3:  # 前30%
                    score += 5

                # 判断阈值: 60分以上认为是标题
                if score >= 60:
                    # 判断层级
                    level = self._determine_level_by_text(text)

                    chapter = ChapterNode(
                        id=f"hybrid_{i}",
                        level=level,
                        title=text,
                        para_start_idx=i,
                        para_end_idx=i,
                        word_count=0,
                        preview_text="",
                        auto_selected=False,
                        skip_recommended=False,
                        content_tags=[f'score_{score}']
                    )
                    chapters.append(chapter)
                    logger.debug(f"混合识别标题 (得分{score}): {text[:50]}")

            # 定位内容
            chapters = self.parser._locate_chapter_content(self.doc, chapters)

            # 构建树形结构
            chapter_tree = self.parser._build_chapter_tree(chapters)

            # 计算统计信息
            total_detected_words = sum(ch.word_count for ch in chapters)
            coverage_rate = total_detected_words / self.total_chars if self.total_chars > 0 else 0

            # 覆盖率警告
            coverage_warning = None
            if coverage_rate < 0.60:
                coverage_warning = f"⚠️ 覆盖率仅{coverage_rate:.1%},可能漏识别了章节"
                logger.warning(f"混合启发式识别 - {coverage_warning}")

            return {
                'success': True,
                'method_name': '混合启发式识别',
                'chapters': [ch.to_dict() for ch in chapter_tree],
                'statistics': {
                    'total_chapters': len(chapters),
                    'total_words': total_detected_words,
                    'document_total_chars': self.total_chars,
                    'coverage_rate': round(coverage_rate, 4),
                    'coverage_warning': coverage_warning
                }
            }
        except Exception as e:
            logger.error(f"混合启发式识别失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise

    def _determine_level_by_text(self, text: str) -> int:
        """根据文本内容判断标题层级"""
        import re

        # 一级标题: 第X章/部分, 单个数字
        if re.match(r'^第[一二三四五六七八九十\d]+[章部分]', text):
            return 1
        if re.match(r'^\d+\.\s+\S', text) and not re.match(r'^\d+\.\d+', text):
            return 1

        # 二级标题: X.Y格式
        if re.match(r'^\d+\.\d+\s+\S', text) and not re.match(r'^\d+\.\d+\.\d+', text):
            return 2

        # 三级标题: X.Y.Z格式
        if re.match(r'^\d+\.\d+\.\d+\s+\S', text):
            return 3

        # 默认二级
        return 2

    def _run_azure_parser(self) -> Dict:
        """方法4: Azure Form Recognizer 解析"""
        try:
            azure_parser = AzureDocumentParser()
            result = azure_parser.parse_document_structure(self.doc_path)
            return result
        except Exception as e:
            logger.error(f"Azure 解析失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise

    def _run_docx_native(self) -> Dict:
        """方法5: Word大纲级别识别（微软官方API）"""
        import re

        try:
            headings = []

            # 直接从Word文档提取标题 - 使用微软官方的大纲级别API
            for idx, para in enumerate(self.doc.paragraphs):
                is_heading = False
                level = 0
                detection_method = ""

                # ⭐ 优先级1: 检查大纲级别 (Outline Level) - 微软官方语义标记
                # 这是Word导航窗格和大纲视图使用的结构，准确度最高
                try:
                    pPr = para._element.pPr
                    if pPr is not None:
                        outlineLvl = pPr.outlineLvl
                        if outlineLvl is not None:
                            outline_level_val = int(outlineLvl.val)
                            # Word大纲级别: 0-8表示标题(0=一级), 9表示正文
                            if outline_level_val <= 8:
                                # 🔧 添加过滤规则，排除噪音内容
                                text = para.text.strip()
                                should_skip = False

                                # 过滤1: 跳过文档前30段的封面/元数据（Level 0）
                                if idx < 30 and outline_level_val == 0:
                                    metadata_keywords = ['项目编号', '招标人', '代理机构', '联系人', '联系方式',
                                                        '地址', '电话', '传真', '邮编', '网址', 'http']
                                    if any(kw in text for kw in metadata_keywords):
                                        should_skip = True
                                        logger.debug(f"过滤封面: 段落{idx} '{text[:30]}'")

                                # 过滤2: 跳过Level 3-4的长条款内容
                                if not should_skip and outline_level_val >= 3:
                                    # 形如 "1.1 这是一个很长的说明文字..." 的是条款，不是标题
                                    if re.match(r'^\d+\.\d+\s+.{15,}', text):
                                        should_skip = True
                                        logger.debug(f"过滤条款: 段落{idx} '{text[:30]}'")

                                # 过滤3: 标题长度限制（超过50字的通常不是标题）
                                if not should_skip and len(text) > 50:
                                    # 除非有明确的章节编号
                                    if not re.match(r'^第[一二三四五六七八九十\d]+[章部分]', text):
                                        should_skip = True
                                        logger.debug(f"过滤长文本: 段落{idx} '{text[:30]}'")

                                if not should_skip:
                                    is_heading = True
                                    level = outline_level_val + 1  # 转换: 0→1级, 1→2级, ...
                                    detection_method = f"大纲级别{outline_level_val}"
                except (AttributeError, TypeError, ValueError):
                    pass  # 没有大纲级别，继续其他方法

                # 优先级2: 检查标准Heading样式 (备用方案)
                if not is_heading:
                    style_name = para.style.name if para.style else ""

                    # 只接受标准的Heading样式（精确匹配，避免误识别）
                    if style_name.startswith('Heading '):  # 'Heading 1', 'Heading 2'
                        match = re.search(r'Heading (\d+)', style_name)
                        if match:
                            is_heading = True
                            level = int(match.group(1))
                            detection_method = f"样式{style_name}"
                    elif style_name.startswith('标题 '):  # '标题 1', '标题 2'
                        match = re.search(r'标题 (\d+)', style_name)
                        if match:
                            is_heading = True
                            level = int(match.group(1))
                            detection_method = f"样式{style_name}"

                if is_heading and para.text.strip():
                    headings.append({
                        'index': idx,
                        'text': para.text.strip(),
                        'level': level if level > 0 else 1,
                        'detection_method': detection_method
                    })
                    logger.debug(f"识别标题: 段落{idx} [{detection_method}] '{para.text.strip()[:50]}'")

            if not headings:
                return {
                    'success': False,
                    'error': 'Word文档中未找到标题（未设置大纲级别，也未使用Heading样式）',
                    'chapters': [],
                    'method_name': 'Word大纲级别识别',
                    'statistics': {
                        'total_chapters': 0,
                        'detection_note': '文档未使用Word标准标题结构'
                    }
                }

            logger.info(f"✅ 基于大纲级别识别到 {len(headings)} 个标题")

            # 构建章节结构
            chapters = []
            for i, heading in enumerate(headings):
                # 确定章节范围
                start_idx = heading['index']
                end_idx = headings[i + 1]['index'] - 1 if i + 1 < len(headings) else self.total_paragraphs - 1

                # 提取章节内容
                content_paras = self.doc.paragraphs[start_idx + 1:end_idx + 1]
                content_text = '\n'.join(p.text for p in content_paras if p.text.strip())
                word_count = len(content_text.replace(' ', '').replace('\n', ''))

                # 生成预览文本
                preview_lines = []
                for p in content_paras[:5]:
                    text = p.text.strip()
                    if text:
                        preview_lines.append(text[:100] + ('...' if len(text) > 100 else ''))
                    if len(preview_lines) >= 5:
                        break
                preview_text = '\n'.join(preview_lines) if preview_lines else "(无内容)"

                # 创建章节节点
                chapter = ChapterNode(
                    id=f"docx_{i}",
                    level=heading['level'],
                    title=heading['text'],
                    para_start_idx=start_idx,
                    para_end_idx=end_idx,
                    word_count=word_count,
                    preview_text=preview_text,
                    auto_selected=False,
                    skip_recommended=False,
                    content_tags=['docx_native', heading.get('detection_method', 'unknown')]
                )

                chapters.append(chapter)

            # 构建树形结构
            chapter_tree = self.parser._build_chapter_tree(chapters)

            # 计算统计信息
            total_detected_words = sum(ch.word_count for ch in chapters)
            coverage_rate = total_detected_words / self.total_chars if self.total_chars > 0 else 0

            # 覆盖率警告
            coverage_warning = None
            if coverage_rate < 0.60:
                coverage_warning = f"⚠️ 覆盖率仅{coverage_rate:.1%},可能漏识别了章节"
                logger.warning(f"Word大纲级别识别 - {coverage_warning}")

            # 统计检测方法分布
            detection_stats = {}
            for h in headings:
                method = h.get('detection_method', 'unknown')
                detection_stats[method] = detection_stats.get(method, 0) + 1

            return {
                'success': True,
                'method_name': 'Word大纲级别识别',
                'chapters': [ch.to_dict() for ch in chapter_tree],
                'statistics': {
                    'total_chapters': len(chapters),
                    'total_words': total_detected_words,
                    'document_total_chars': self.total_chars,
                    'coverage_rate': round(coverage_rate, 4),
                    'coverage_warning': coverage_warning,
                    'detection_methods': detection_stats  # 记录使用了哪些检测方法
                }
            }
        except Exception as e:
            logger.error(f"Word大纲级别识别失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise

    @staticmethod
    def calculate_accuracy(detected_chapters: List[Dict], ground_truth_chapters: List[Dict]) -> Dict:
        """
        计算准确率指标

        Args:
            detected_chapters: 检测到的章节列表
            ground_truth_chapters: 正确答案章节列表

        Returns:
            {
                'precision': 0.0-1.0,
                'recall': 0.0-1.0,
                'f1_score': 0.0-1.0,
                'matched_count': int,
                'detected_count': int,
                'ground_truth_count': int,
                'details': [...]
            }
        """
        if not ground_truth_chapters:
            return {
                'precision': 0.0,
                'recall': 0.0,
                'f1_score': 0.0,
                'matched_count': 0,
                'detected_count': len(detected_chapters),
                'ground_truth_count': 0
            }

        # 扁平化章节列表（包含子章节）
        def flatten_chapters(chapters_list):
            flat = []
            for ch in chapters_list:
                flat.append(ch)
                if 'children' in ch and ch['children']:
                    flat.extend(flatten_chapters(ch['children']))
            return flat

        detected_flat = flatten_chapters(detected_chapters)
        truth_flat = flatten_chapters(ground_truth_chapters)

        # 规范化标题（用于匹配）
        def normalize_title(title: str) -> str:
            import re
            # 移除所有空格、编号
            cleaned = re.sub(r'^\d+\.\s*', '', title)
            cleaned = re.sub(r'^\d+\.\d+\s*', '', cleaned)
            cleaned = re.sub(r'^第[一二三四五六七八九十\d]+[章节部分]\s*', '', cleaned)
            cleaned = re.sub(r'\s+', '', cleaned)
            return cleaned.lower()

        # 构建真实答案的标题集合
        truth_titles = {normalize_title(ch['title']): ch for ch in truth_flat}
        detected_titles = {normalize_title(ch['title']): ch for ch in detected_flat}

        # 计算匹配
        matched_titles = set(truth_titles.keys()) & set(detected_titles.keys())
        matched_count = len(matched_titles)

        # 计算指标
        precision = matched_count / len(detected_flat) if detected_flat else 0.0
        recall = matched_count / len(truth_flat) if truth_flat else 0.0
        f1_score = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

        # 详细匹配信息
        details = []
        for title in truth_titles.keys():
            if title in matched_titles:
                details.append({
                    'title': truth_titles[title]['title'],
                    'status': 'matched',
                    'detected': True
                })
            else:
                details.append({
                    'title': truth_titles[title]['title'],
                    'status': 'missed',
                    'detected': False
                })

        # 检测多余的（误检）
        for title in detected_titles.keys():
            if title not in matched_titles:
                details.append({
                    'title': detected_titles[title]['title'],
                    'status': 'false_positive',
                    'detected': True
                })

        return {
            'precision': round(precision, 4),
            'recall': round(recall, 4),
            'f1_score': round(f1_score, 4),
            'matched_count': matched_count,
            'detected_count': len(detected_flat),
            'ground_truth_count': len(truth_flat),
            'details': details
        }


@api_parser_debug_bp.route('/upload', methods=['POST'])
def upload_document():
    """
    上传文档并运行所有解析方法

    请求:
        - file: .docx文件
        - methods: 要运行的方法列表（可选，默认全部）

    响应:
        {
            "success": true,
            "document_id": "uuid",
            "document_info": {...},
            "results": {...}
        }
    """
    try:
        # 检查文件
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': '没有上传文件'}), 400

        file = request.files['file']
        if not file.filename:
            return jsonify({'success': False, 'error': '文件名为空'}), 400

        if not file.filename.endswith('.docx'):
            return jsonify({'success': False, 'error': '仅支持 .docx 格式文件'}), 400

        # 保存文件
        document_id = str(uuid.uuid4())
        filename = secure_filename(file.filename)

        config = get_config()
        upload_dir = config.get_path('data') / 'parser_debug'
        upload_dir.mkdir(parents=True, exist_ok=True)

        file_path = upload_dir / f"{document_id}_{filename}"
        file.save(str(file_path))

        logger.info(f"文件已保存: {file_path}")

        # 创建调试器并运行所有方法
        debugger = ParserDebugger(str(file_path))
        document_info = debugger.get_document_info()
        results = debugger.run_all_methods()

        # 保存到数据库
        db = get_knowledge_base_db()
        db.execute_query("""
            INSERT INTO parser_debug_tests (
                document_id, filename, file_path,
                total_paragraphs, has_toc, toc_items_count, toc_start_idx, toc_end_idx,
                semantic_result, style_result, hybrid_result, azure_result, docx_native_result,
                semantic_elapsed, style_elapsed, hybrid_elapsed, azure_elapsed, docx_native_elapsed,
                semantic_chapters_count, style_chapters_count, hybrid_chapters_count, azure_chapters_count, docx_native_chapters_count
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            document_id,
            filename,
            str(file_path),
            document_info['total_paragraphs'],
            document_info['has_toc'],
            document_info['toc_items_count'],
            document_info['toc_start_idx'],
            document_info['toc_end_idx'],
            json.dumps(results['semantic'], ensure_ascii=False),
            json.dumps(results['style'], ensure_ascii=False),
            json.dumps(results['hybrid'], ensure_ascii=False),
            json.dumps(results['azure'], ensure_ascii=False),
            json.dumps(results['docx_native'], ensure_ascii=False),
            results['semantic']['performance']['elapsed'],
            results['style']['performance']['elapsed'],
            results['hybrid']['performance']['elapsed'],
            results['azure']['performance']['elapsed'],
            results['docx_native']['performance']['elapsed'],
            len(results['semantic'].get('chapters', [])),
            len(results['style'].get('chapters', [])),
            len(results['hybrid'].get('chapters', [])),
            len(results['azure'].get('chapters', [])),
            len(results['docx_native'].get('chapters', []))
        ))

        return jsonify({
            'success': True,
            'document_id': document_id,
            'document_info': document_info,
            'results': results
        })

    except Exception as e:
        logger.error(f"上传处理失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500


@api_parser_debug_bp.route('/<document_id>', methods=['GET'])
def get_test_result(document_id):
    """
    获取测试结果

    响应:
        {
            "success": true,
            "document_info": {...},
            "results": {...},
            "ground_truth": {...},
            "accuracy": {...}
        }
    """
    try:
        db = get_knowledge_base_db()
        row = db.execute_query(
            "SELECT * FROM parser_debug_tests WHERE document_id = ?",
            (document_id,),
            fetch_one=True
        )

        if not row:
            return jsonify({'success': False, 'error': '测试记录不存在'}), 404

        # 解析结果
        results = {
            'semantic': json.loads(row['semantic_result']) if row['semantic_result'] else None,
            'style': json.loads(row['style_result']) if row['style_result'] else None,
            'hybrid': json.loads(row['hybrid_result']) if row.get('hybrid_result') else None,
            'azure': json.loads(row['azure_result']) if row.get('azure_result') else None,
            'docx_native': json.loads(row['docx_native_result']) if row.get('docx_native_result') else None,
        }

        document_info = {
            'filename': row['filename'],
            'total_paragraphs': row['total_paragraphs'],
            'has_toc': bool(row['has_toc']),
            'toc_items_count': row['toc_items_count'],
            'upload_time': row['upload_time']
        }

        ground_truth = json.loads(row['ground_truth']) if row['ground_truth'] else None

        # 如果有ground_truth，返回准确率数据
        accuracy = None
        if ground_truth:
            accuracy = {
                'semantic': {
                    'precision': row['semantic_precision'],
                    'recall': row['semantic_recall'],
                    'f1_score': row['semantic_f1']
                },
                'style': {
                    'precision': row['style_precision'],
                    'recall': row['style_recall'],
                    'f1_score': row['style_f1']
                },
                'hybrid': {
                    'precision': row.get('hybrid_precision'),
                    'recall': row.get('hybrid_recall'),
                    'f1_score': row.get('hybrid_f1')
                } if row.get('hybrid_precision') else None,
                'azure': {
                    'precision': row.get('azure_precision'),
                    'recall': row.get('azure_recall'),
                    'f1_score': row.get('azure_f1')
                } if row.get('azure_precision') else None,
                'docx_native': {
                    'precision': row.get('docx_native_precision'),
                    'recall': row.get('docx_native_recall'),
                    'f1_score': row.get('docx_native_f1')
                } if row.get('docx_native_precision') else None,
                'best_method': row['best_method'],
                'best_f1_score': row['best_f1_score']
            }

        return jsonify({
            'success': True,
            'document_id': document_id,
            'document_info': document_info,
            'results': results,
            'ground_truth': ground_truth,
            'accuracy': accuracy
        })

    except Exception as e:
        logger.error(f"获取测试结果失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_parser_debug_bp.route('/<document_id>/ground-truth', methods=['POST'])
def save_ground_truth(document_id):
    """
    保存人工标注的正确答案

    请求:
        {
            "chapters": [...],  # 正确的章节列表
            "annotator": "用户名"
        }

    响应:
        {
            "success": true,
            "accuracy": {...}  # 自动计算的准确率
        }
    """
    try:
        data = request.get_json()
        if not data or 'chapters' not in data:
            return jsonify({'success': False, 'error': '缺少章节数据'}), 400

        chapters = data['chapters']
        annotator = data.get('annotator', 'unknown')

        # 获取现有测试结果
        db = get_knowledge_base_db()
        row = db.execute_query(
            "SELECT semantic_result, style_result, hybrid_result, azure_result, docx_native_result FROM parser_debug_tests WHERE document_id = ?",
            (document_id,),
            fetch_one=True
        )

        if not row:
            return jsonify({'success': False, 'error': '测试记录不存在'}), 404

        # 解析各方法的结果
        semantic_chapters = json.loads(row['semantic_result'])['chapters'] if row['semantic_result'] else []
        style_chapters = json.loads(row['style_result'])['chapters'] if row['style_result'] else []
        hybrid_chapters = json.loads(row['hybrid_result'])['chapters'] if row.get('hybrid_result') else []
        azure_chapters = json.loads(row['azure_result'])['chapters'] if row.get('azure_result') else []
        docx_native_chapters = json.loads(row['docx_native_result'])['chapters'] if row.get('docx_native_result') else []

        # 计算各方法的准确率
        semantic_acc = ParserDebugger.calculate_accuracy(semantic_chapters, chapters)
        style_acc = ParserDebugger.calculate_accuracy(style_chapters, chapters)
        hybrid_acc = ParserDebugger.calculate_accuracy(hybrid_chapters, chapters) if hybrid_chapters else None
        azure_acc = ParserDebugger.calculate_accuracy(azure_chapters, chapters) if azure_chapters else None
        docx_native_acc = ParserDebugger.calculate_accuracy(docx_native_chapters, chapters) if docx_native_chapters else None

        # 找出最佳方法
        all_f1 = {
            'semantic': semantic_acc['f1_score'],
            'style': style_acc['f1_score'],
        }
        if hybrid_acc:
            all_f1['hybrid'] = hybrid_acc['f1_score']
        if azure_acc:
            all_f1['azure'] = azure_acc['f1_score']
        if docx_native_acc:
            all_f1['docx_native'] = docx_native_acc['f1_score']
        best_method = max(all_f1, key=all_f1.get)
        best_f1_score = all_f1[best_method]

        # 更新数据库
        update_params = [
            json.dumps(chapters, ensure_ascii=False),
            annotator,
            datetime.now().isoformat(),
            len(chapters),
            semantic_acc['precision'], semantic_acc['recall'], semantic_acc['f1_score'],
            style_acc['precision'], style_acc['recall'], style_acc['f1_score'],
        ]

        # 如果有 hybrid 结果，添加其准确率
        if hybrid_acc:
            update_params.extend([hybrid_acc['precision'], hybrid_acc['recall'], hybrid_acc['f1_score']])
        else:
            update_params.extend([None, None, None])

        # 如果有 Azure 结果，添加其准确率
        if azure_acc:
            update_params.extend([azure_acc['precision'], azure_acc['recall'], azure_acc['f1_score']])
        else:
            update_params.extend([None, None, None])

        # 如果有 docx_native 结果，添加其准确率
        if docx_native_acc:
            update_params.extend([docx_native_acc['precision'], docx_native_acc['recall'], docx_native_acc['f1_score']])
        else:
            update_params.extend([None, None, None])

        update_params.extend([best_method, best_f1_score, document_id])

        db.execute_query("""
            UPDATE parser_debug_tests SET
                ground_truth = ?, annotator = ?, annotation_time = ?, ground_truth_count = ?,
                semantic_precision = ?, semantic_recall = ?, semantic_f1 = ?,
                style_precision = ?, style_recall = ?, style_f1 = ?,
                hybrid_precision = ?, hybrid_recall = ?, hybrid_f1 = ?,
                azure_precision = ?, azure_recall = ?, azure_f1 = ?,
                docx_native_precision = ?, docx_native_recall = ?, docx_native_f1 = ?,
                best_method = ?, best_f1_score = ?
            WHERE document_id = ?
        """, tuple(update_params))

        accuracy_result = {
            'semantic': semantic_acc,
            'style': style_acc,
            'best_method': best_method,
            'best_f1_score': best_f1_score
        }

        if hybrid_acc:
            accuracy_result['hybrid'] = hybrid_acc
        if azure_acc:
            accuracy_result['azure'] = azure_acc
        if docx_native_acc:
            accuracy_result['docx_native'] = docx_native_acc

        return jsonify({
            'success': True,
            'accuracy': accuracy_result
        })

    except Exception as e:
        logger.error(f"保存ground truth失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500


@api_parser_debug_bp.route('/history', methods=['GET'])
def get_history():
    """
    获取历史测试列表

    查询参数:
        - limit: 返回数量限制（默认20）
        - has_ground_truth: 是否只返回已标注的（可选）

    响应:
        {
            "success": true,
            "tests": [...]
        }
    """
    try:
        limit = request.args.get('limit', 20, type=int)
        has_ground_truth = request.args.get('has_ground_truth', type=bool)

        db = get_knowledge_base_db()

        sql = "SELECT * FROM v_parser_debug_summary"
        params = []

        if has_ground_truth is not None:
            sql += " WHERE has_ground_truth = ?"
            params.append(1 if has_ground_truth else 0)

        sql += " LIMIT ?"
        params.append(limit)

        rows = db.execute_query(sql, tuple(params))

        tests = []
        for row in rows:
            tests.append(dict(row))

        return jsonify({
            'success': True,
            'tests': tests,
            'total': len(tests)
        })

    except Exception as e:
        logger.error(f"获取历史记录失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_parser_debug_bp.route('/<document_id>/delete', methods=['DELETE'])
def delete_test(document_id):
    """删除测试记录"""
    try:
        db = get_knowledge_base_db()

        # 获取文件路径并删除文件
        row = db.execute_query(
            "SELECT file_path FROM parser_debug_tests WHERE document_id = ?",
            (document_id,),
            fetch_one=True
        )

        if row and row['file_path']:
            file_path = Path(row['file_path'])
            if file_path.exists():
                file_path.unlink()
                logger.info(f"已删除文件: {file_path}")

        # 删除数据库记录
        db.execute_query(
            "DELETE FROM parser_debug_tests WHERE document_id = ?",
            (document_id,)
        )

        return jsonify({'success': True})

    except Exception as e:
        logger.error(f"删除测试记录失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_parser_debug_bp.route('/export/<document_id>', methods=['GET'])
def export_comparison_report(document_id):
    """
    导出对比报告（JSON格式）

    响应:
        完整的JSON报告文件
    """
    try:
        db = get_knowledge_base_db()
        row = db.execute_query(
            "SELECT * FROM parser_debug_tests WHERE document_id = ?",
            (document_id,),
            fetch_one=True
        )

        if not row:
            return jsonify({'success': False, 'error': '测试记录不存在'}), 404

        # 构建完整报告
        report = {
            'document_id': document_id,
            'filename': row['filename'],
            'upload_time': row['upload_time'],
            'document_info': {
                'total_paragraphs': row['total_paragraphs'],
                'has_toc': bool(row['has_toc']),
                'toc_items_count': row['toc_items_count']
            },
            'results': {
                'semantic': json.loads(row['semantic_result']) if row['semantic_result'] else None,
                'style': json.loads(row['style_result']) if row['style_result'] else None,
                'hybrid': json.loads(row['hybrid_result']) if row.get('hybrid_result') else None,
                'azure': json.loads(row['azure_result']) if row.get('azure_result') else None,
                'docx_native': json.loads(row['docx_native_result']) if row.get('docx_native_result') else None,
            },
            'ground_truth': json.loads(row['ground_truth']) if row['ground_truth'] else None,
            'accuracy': None
        }

        # 如果有标注，添加准确率数据
        if row['ground_truth']:
            report['accuracy'] = {
                'semantic': {
                    'precision': row['semantic_precision'],
                    'recall': row['semantic_recall'],
                    'f1_score': row['semantic_f1']
                },
                'style': {
                    'precision': row['style_precision'],
                    'recall': row['style_recall'],
                    'f1_score': row['style_f1']
                },
                'best_method': row['best_method'],
                'best_f1_score': row['best_f1_score']
            }

            # 添加hybrid结果(如果存在)
            if row.get('hybrid_precision'):
                report['accuracy']['hybrid'] = {
                    'precision': row['hybrid_precision'],
                    'recall': row['hybrid_recall'],
                    'f1_score': row['hybrid_f1']
                }

            # 添加azure结果(如果存在)
            if row.get('azure_precision'):
                report['accuracy']['azure'] = {
                    'precision': row['azure_precision'],
                    'recall': row['azure_recall'],
                    'f1_score': row['azure_f1']
                }

            # 添加docx_native结果(如果存在)
            if row.get('docx_native_precision'):
                report['accuracy']['docx_native'] = {
                    'precision': row['docx_native_precision'],
                    'recall': row['docx_native_recall'],
                    'f1_score': row['docx_native_f1']
                }

        # 保存为临时JSON文件
        config = get_config()
        temp_dir = config.get_path('data') / 'temp'
        temp_dir.mkdir(parents=True, exist_ok=True)

        report_file = temp_dir / f"parser_comparison_{document_id}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        return send_file(
            report_file,
            as_attachment=True,
            download_name=f"parser_comparison_{row['filename']}.json",
            mimetype='application/json'
        )

    except Exception as e:
        logger.error(f"导出报告失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# 注册蓝图到应用（需要在app.py中调用）
def register_parser_debug_bp(app):
    """注册解析调试蓝图"""
    app.register_blueprint(api_parser_debug_bp)
    logger.info("解析调试API已注册")
