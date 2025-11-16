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
                'old_toc': {...},
                'style': {...},
                'outline': {...},
                'azure': {...}  # 可选
            }
        """
        results = {}

        # 方法1: 语义锚点解析
        results['semantic'] = self._run_with_timing(
            self._run_semantic_anchors,
            "语义锚点解析"
        )

        # 方法2: 旧目录定位
        results['old_toc'] = self._run_with_timing(
            self._run_old_toc_locate,
            "旧目录定位"
        )

        # 方法3: 样式识别
        results['style'] = self._run_with_timing(
            self._run_style_detection,
            "样式识别"
        )

        # 方法4: 大纲级别识别
        results['outline'] = self._run_with_timing(
            self._run_outline_detection,
            "大纲级别识别"
        )

        # 方法5: Azure Form Recognizer（如果可用）
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
                    # 递归累加所有子章节的字数
                    def sum_word_count(node):
                        total = node.word_count
                        for child in node.children:
                            total += sum_word_count(child)
                        return total

                    chapter.word_count = sum_word_count(chapter)
                    logger.info(f"  └─ 识别到 {len(subsections)} 个子章节（总字数: {chapter.word_count}）")

            # 构建树形结构
            chapter_tree = self.parser._build_chapter_tree(chapters)

            return {
                'success': True,
                'method_name': '语义锚点解析',
                'chapters': [ch.to_dict() for ch in chapter_tree],
                'statistics': {
                    'total_chapters': len(chapters),
                    'total_words': sum(ch.word_count for ch in chapters),
                    'toc_items_count': len(toc_items),
                    'match_rate': len(chapters) / len(toc_items) if toc_items else 0
                }
            }
        except Exception as e:
            logger.error(f"语义锚点解析失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise

    def _run_old_toc_locate(self) -> Dict:
        """方法2: 强制使用旧的目录定位方案"""
        if not self.has_toc:
            return {
                'success': False,
                'error': '文档无目录，无法使用旧目录定位',
                'chapters': [],
                'method_name': '旧目录定位'
            }

        try:
            toc_items, toc_end_idx = self.parser._parse_toc_items(self.doc, self.toc_start_idx)

            chapters = self.parser._locate_chapters_by_toc(
                self.doc, toc_items, toc_end_idx
            )

            # 构建树形结构
            chapter_tree = self.parser._build_chapter_tree(chapters)

            return {
                'success': True,
                'method_name': '旧目录定位',
                'chapters': [ch.to_dict() for ch in chapter_tree],
                'statistics': {
                    'total_chapters': len(chapters),
                    'total_words': sum(ch.word_count for ch in chapters),
                    'toc_items_count': len(toc_items),
                    'match_rate': len(chapters) / len(toc_items) if toc_items else 0
                }
            }
        except Exception as e:
            logger.error(f"旧目录定位失败: {e}")
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

            return {
                'success': True,
                'method_name': '样式识别',
                'chapters': [ch.to_dict() for ch in chapter_tree],
                'statistics': {
                    'total_chapters': len(chapters),
                    'total_words': sum(ch.word_count for ch in chapters)
                }
            }
        except Exception as e:
            logger.error(f"样式识别失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise

    def _run_outline_detection(self) -> Dict:
        """方法4: 纯大纲级别识别（实验性）"""
        try:
            # 只使用大纲级别识别标题
            chapters = []
            for i, para in enumerate(self.doc.paragraphs):
                # 尝试获取大纲级别
                try:
                    pPr = para._element.pPr
                    if pPr is not None:
                        outlineLvl = pPr.outlineLvl
                        if outlineLvl is not None:
                            level = int(outlineLvl.val) + 1  # 0->1, 1->2, 2->3
                            if level <= 3:
                                text = para.text.strip()
                                if text and len(text) <= 100:
                                    chapter = ChapterNode(
                                        id=f"outline_{i}",
                                        level=level,
                                        title=text,
                                        para_start_idx=i,
                                        para_end_idx=i,
                                        word_count=0,
                                        preview_text="",
                                        auto_selected=False,
                                        skip_recommended=False
                                    )
                                    chapters.append(chapter)
                except (AttributeError, TypeError):
                    continue

            # 定位内容
            chapters = self.parser._locate_chapter_content(self.doc, chapters)

            # 构建树形结构
            chapter_tree = self.parser._build_chapter_tree(chapters)

            return {
                'success': True,
                'method_name': '大纲级别识别',
                'chapters': [ch.to_dict() for ch in chapter_tree],
                'statistics': {
                    'total_chapters': len(chapters),
                    'total_words': sum(ch.word_count for ch in chapters)
                }
            }
        except Exception as e:
            logger.error(f"大纲级别识别失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise

    def _run_azure_parser(self) -> Dict:
        """方法5: Azure Form Recognizer 解析"""
        try:
            azure_parser = AzureDocumentParser()
            result = azure_parser.parse_document_structure(self.doc_path)
            return result
        except Exception as e:
            logger.error(f"Azure 解析失败: {e}")
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
                semantic_result, old_toc_result, style_result, outline_result, azure_result,
                semantic_elapsed, old_toc_elapsed, style_elapsed, outline_elapsed, azure_elapsed,
                semantic_chapters_count, old_toc_chapters_count,
                style_chapters_count, outline_chapters_count, azure_chapters_count
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
            json.dumps(results['old_toc'], ensure_ascii=False),
            json.dumps(results['style'], ensure_ascii=False),
            json.dumps(results['outline'], ensure_ascii=False),
            json.dumps(results['azure'], ensure_ascii=False),
            results['semantic']['performance']['elapsed'],
            results['old_toc']['performance']['elapsed'],
            results['style']['performance']['elapsed'],
            results['outline']['performance']['elapsed'],
            results['azure']['performance']['elapsed'],
            len(results['semantic'].get('chapters', [])),
            len(results['old_toc'].get('chapters', [])),
            len(results['style'].get('chapters', [])),
            len(results['outline'].get('chapters', [])),
            len(results['azure'].get('chapters', []))
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
            'old_toc': json.loads(row['old_toc_result']) if row['old_toc_result'] else None,
            'style': json.loads(row['style_result']) if row['style_result'] else None,
            'outline': json.loads(row['outline_result']) if row['outline_result'] else None,
            'azure': json.loads(row['azure_result']) if row.get('azure_result') else None,
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
                'old_toc': {
                    'precision': row['old_toc_precision'],
                    'recall': row['old_toc_recall'],
                    'f1_score': row['old_toc_f1']
                },
                'style': {
                    'precision': row['style_precision'],
                    'recall': row['style_recall'],
                    'f1_score': row['style_f1']
                },
                'outline': {
                    'precision': row['outline_precision'],
                    'recall': row['outline_recall'],
                    'f1_score': row['outline_f1']
                },
                'azure': {
                    'precision': row.get('azure_precision'),
                    'recall': row.get('azure_recall'),
                    'f1_score': row.get('azure_f1')
                } if row.get('azure_precision') else None,
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
            "SELECT semantic_result, old_toc_result, style_result, outline_result, azure_result FROM parser_debug_tests WHERE document_id = ?",
            (document_id,),
            fetch_one=True
        )

        if not row:
            return jsonify({'success': False, 'error': '测试记录不存在'}), 404

        # 解析各方法的结果
        semantic_chapters = json.loads(row['semantic_result'])['chapters'] if row['semantic_result'] else []
        old_toc_chapters = json.loads(row['old_toc_result'])['chapters'] if row['old_toc_result'] else []
        style_chapters = json.loads(row['style_result'])['chapters'] if row['style_result'] else []
        outline_chapters = json.loads(row['outline_result'])['chapters'] if row['outline_result'] else []
        azure_chapters = json.loads(row['azure_result'])['chapters'] if row.get('azure_result') else []

        # 计算各方法的准确率
        semantic_acc = ParserDebugger.calculate_accuracy(semantic_chapters, chapters)
        old_toc_acc = ParserDebugger.calculate_accuracy(old_toc_chapters, chapters)
        style_acc = ParserDebugger.calculate_accuracy(style_chapters, chapters)
        outline_acc = ParserDebugger.calculate_accuracy(outline_chapters, chapters)
        azure_acc = ParserDebugger.calculate_accuracy(azure_chapters, chapters) if azure_chapters else None

        # 找出最佳方法
        all_f1 = {
            'semantic': semantic_acc['f1_score'],
            'old_toc': old_toc_acc['f1_score'],
            'style': style_acc['f1_score'],
            'outline': outline_acc['f1_score']
        }
        if azure_acc:
            all_f1['azure'] = azure_acc['f1_score']
        best_method = max(all_f1, key=all_f1.get)
        best_f1_score = all_f1[best_method]

        # 更新数据库
        update_params = [
            json.dumps(chapters, ensure_ascii=False),
            annotator,
            datetime.now().isoformat(),
            len(chapters),
            semantic_acc['precision'], semantic_acc['recall'], semantic_acc['f1_score'],
            old_toc_acc['precision'], old_toc_acc['recall'], old_toc_acc['f1_score'],
            style_acc['precision'], style_acc['recall'], style_acc['f1_score'],
            outline_acc['precision'], outline_acc['recall'], outline_acc['f1_score'],
        ]

        # 如果有 Azure 结果，添加其准确率
        if azure_acc:
            update_params.extend([azure_acc['precision'], azure_acc['recall'], azure_acc['f1_score']])

        update_params.extend([best_method, best_f1_score, document_id])

        if azure_acc:
            db.execute_query("""
                UPDATE parser_debug_tests SET
                    ground_truth = ?, annotator = ?, annotation_time = ?, ground_truth_count = ?,
                    semantic_precision = ?, semantic_recall = ?, semantic_f1 = ?,
                    old_toc_precision = ?, old_toc_recall = ?, old_toc_f1 = ?,
                    style_precision = ?, style_recall = ?, style_f1 = ?,
                    outline_precision = ?, outline_recall = ?, outline_f1 = ?,
                    azure_precision = ?, azure_recall = ?, azure_f1 = ?,
                    best_method = ?, best_f1_score = ?
                WHERE document_id = ?
            """, tuple(update_params))
        else:
            db.execute_query("""
                UPDATE parser_debug_tests SET
                    ground_truth = ?, annotator = ?, annotation_time = ?, ground_truth_count = ?,
                    semantic_precision = ?, semantic_recall = ?, semantic_f1 = ?,
                    old_toc_precision = ?, old_toc_recall = ?, old_toc_f1 = ?,
                    style_precision = ?, style_recall = ?, style_f1 = ?,
                    outline_precision = ?, outline_recall = ?, outline_f1 = ?,
                    best_method = ?, best_f1_score = ?
                WHERE document_id = ?
            """, tuple(update_params))

        accuracy_result = {
            'semantic': semantic_acc,
            'old_toc': old_toc_acc,
            'style': style_acc,
            'outline': outline_acc,
            'best_method': best_method,
            'best_f1_score': best_f1_score
        }

        if azure_acc:
            accuracy_result['azure'] = azure_acc

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
                'old_toc': json.loads(row['old_toc_result']) if row['old_toc_result'] else None,
                'style': json.loads(row['style_result']) if row['style_result'] else None,
                'outline': json.loads(row['outline_result']) if row['outline_result'] else None,
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
                'old_toc': {
                    'precision': row['old_toc_precision'],
                    'recall': row['old_toc_recall'],
                    'f1_score': row['old_toc_f1']
                },
                'style': {
                    'precision': row['style_precision'],
                    'recall': row['style_recall'],
                    'f1_score': row['style_f1']
                },
                'outline': {
                    'precision': row['outline_precision'],
                    'recall': row['outline_recall'],
                    'f1_score': row['outline_f1']
                },
                'best_method': row['best_method'],
                'best_f1_score': row['best_f1_score']
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
