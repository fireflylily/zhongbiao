#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
方案组装器 - 阶段4
组装最终的技术方案文档
"""

from typing import Dict, List, Any, Optional
from pathlib import Path

# 导入公共模块
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from common import get_module_logger


class ProposalAssembler:
    """方案组装器"""

    def __init__(self):
        """初始化方案组装器"""
        self.logger = get_module_logger("proposal_assembler")
        self.logger.info("方案组装器初始化完成")

    def assemble_proposal(
        self,
        outline: Dict[str, Any],
        analysis: Dict[str, Any],
        matched_docs: Dict[str, List[Dict]],
        options: Optional[Dict[str, bool]] = None
    ) -> Dict[str, Any]:
        """
        组装技术方案

        Args:
            outline: 大纲数据
            analysis: 需求分析结果
            matched_docs: 匹配的产品文档
            options: 生成选项

        Returns:
            方案数据
        """
        try:
            self.logger.info("开始组装技术方案...")

            if options is None:
                options = {}

            proposal = {
                'metadata': {
                    'title': outline.get('outline_title', '技术方案'),
                    'generation_time': outline.get('generation_time', ''),
                    'total_chapters': outline.get('total_chapters', 0),
                    'estimated_pages': outline.get('estimated_pages', 0)
                },
                'chapters': [],
                'attachments': []
            }

            # 组装主要章节
            proposal['chapters'] = self._assemble_chapters(
                outline.get('chapters', []),
                analysis,
                matched_docs
            )

            # 组装附件列表
            if options.get('include_analysis', False):
                proposal['attachments'].append({
                    'type': 'analysis',
                    'title': '需求分析报告',
                    'data': analysis
                })

            if options.get('include_mapping', False):
                proposal['attachments'].append({
                    'type': 'mapping',
                    'title': '需求匹配表',
                    'data': self._create_mapping_table(analysis, matched_docs)
                })

            if options.get('include_summary', False):
                proposal['attachments'].append({
                    'type': 'summary',
                    'title': '生成报告',
                    'data': self._create_summary_report(proposal, analysis, matched_docs)
                })

            self.logger.info("技术方案组装完成")
            return proposal

        except Exception as e:
            self.logger.error(f"方案组装失败: {e}", exc_info=True)
            raise

    def _assemble_chapters(
        self,
        chapters: List[Dict],
        analysis: Dict[str, Any],
        matched_docs: Dict[str, List[Dict]]
    ) -> List[Dict]:
        """
        组装章节内容

        Args:
            chapters: 大纲章节列表
            analysis: 需求分析
            matched_docs: 匹配的文档

        Returns:
            组装后的章节列表
        """
        assembled_chapters = []

        for chapter in chapters:
            assembled_chapter = {
                'chapter_number': chapter.get('chapter_number', ''),
                'level': chapter.get('level', 1),
                'title': chapter.get('title', ''),
                'description': chapter.get('description', ''),
                'response_strategy': chapter.get('response_strategy', ''),
                'content_hints': chapter.get('content_hints', []),
                'response_tips': chapter.get('response_tips', []),
                'suggested_references': chapter.get('suggested_references', []),
                'evidence_needed': chapter.get('evidence_needed', []),
                'subsections': []
            }

            # 处理子章节
            if 'subsections' in chapter and chapter['subsections']:
                assembled_chapter['subsections'] = self._assemble_subsections(
                    chapter['subsections'],
                    analysis,
                    matched_docs
                )

            assembled_chapters.append(assembled_chapter)

        return assembled_chapters

    def _assemble_subsections(
        self,
        subsections: List[Dict],
        analysis: Dict[str, Any],
        matched_docs: Dict[str, List[Dict]]
    ) -> List[Dict]:
        """
        组装子章节

        Args:
            subsections: 子章节列表
            analysis: 需求分析
            matched_docs: 匹配的文档

        Returns:
            组装后的子章节列表
        """
        assembled = []

        for subsection in subsections:
            assembled_sub = {
                'chapter_number': subsection.get('chapter_number', ''),
                'level': subsection.get('level', 2),
                'title': subsection.get('title', ''),
                'description': subsection.get('description', ''),
                'response_strategy': subsection.get('response_strategy', ''),
                'content_hints': subsection.get('content_hints', []),
                'response_tips': subsection.get('response_tips', []),
                'suggested_references': subsection.get('suggested_references', []),
                'evidence_needed': subsection.get('evidence_needed', [])
            }

            assembled.append(assembled_sub)

        return assembled

    def _create_mapping_table(
        self,
        analysis: Dict[str, Any],
        matched_docs: Dict[str, List[Dict]]
    ) -> List[Dict]:
        """
        创建需求匹配表

        Args:
            analysis: 需求分析
            matched_docs: 匹配的文档

        Returns:
            匹配表数据
        """
        mapping_table = []

        for category in analysis.get('requirement_categories', []):
            category_code = category.get('category_code', '')
            category_name = category.get('category', '')

            # 获取该类别匹配的文档
            docs = matched_docs.get(category_code, [])

            for point in category.get('key_points', []):
                row = {
                    'category': category_name,
                    'requirement': point,
                    'matched_docs': [doc['title'] for doc in docs[:2]],  # 最多2个
                    'match_status': '已匹配' if docs else '待匹配'
                }
                mapping_table.append(row)

        return mapping_table

    def _create_summary_report(
        self,
        proposal: Dict[str, Any],
        analysis: Dict[str, Any],
        matched_docs: Dict[str, List[Dict]]
    ) -> Dict[str, Any]:
        """
        创建生成报告

        Args:
            proposal: 方案数据
            analysis: 需求分析
            matched_docs: 匹配的文档

        Returns:
            报告数据
        """
        summary = analysis.get('document_summary', {})

        total_matched_docs = sum(len(docs) for docs in matched_docs.values())

        report = {
            'generation_info': {
                'title': proposal['metadata']['title'],
                'generation_time': proposal['metadata']['generation_time'],
                'total_chapters': proposal['metadata']['total_chapters']
            },
            'requirements_summary': {
                'total_requirements': summary.get('total_requirements', 0),
                'mandatory_count': summary.get('mandatory_count', 0),
                'optional_count': summary.get('optional_count', 0),
                'complexity_level': summary.get('complexity_level', 'medium')
            },
            'matching_summary': {
                'total_documents_matched': total_matched_docs,
                'categories_with_matches': len(matched_docs),
                'match_rate': self._calculate_match_rate(analysis, matched_docs)
            }
        }

        return report

    def _calculate_match_rate(
        self,
        analysis: Dict[str, Any],
        matched_docs: Dict[str, List[Dict]]
    ) -> float:
        """
        计算匹配成功率

        Args:
            analysis: 需求分析
            matched_docs: 匹配的文档

        Returns:
            匹配率（0-100）
        """
        total_categories = len(analysis.get('requirement_categories', []))

        if total_categories == 0:
            return 0.0

        matched_categories = len([
            cat for cat in analysis.get('requirement_categories', [])
            if matched_docs.get(cat.get('category_code', ''))
        ])

        return round((matched_categories / total_categories) * 100, 2)
