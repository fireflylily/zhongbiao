#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
内置解析器 - 包装现有的DocumentStructureParser

此解析器调用现有的structure_parser.py,保持代码隔离
"""

import sys
from pathlib import Path
from typing import Dict
import time

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from common import get_module_logger
from . import BaseStructureParser, ParserMetrics


class BuiltinParser(BaseStructureParser):
    """内置解析器 - 基于现有的多方法回退机制"""

    def __init__(self):
        super().__init__()
        self.logger = get_module_logger("parsers.builtin")
        self._legacy_parser = None

    def _get_legacy_parser(self):
        """延迟加载现有解析器(避免循环导入)"""
        if self._legacy_parser is None:
            from ..structure_parser import DocumentStructureParser
            self._legacy_parser = DocumentStructureParser()
        return self._legacy_parser

    def parse_structure(self, doc_path: str) -> Dict:
        """解析文档结构

        使用现有的DocumentStructureParser实现
        """
        start_time = time.time()

        try:
            self.logger.info(f"[内置解析器] 开始解析: {doc_path}")

            # 调用现有解析器
            parser = self._get_legacy_parser()
            result = parser.parse_document_structure(doc_path)

            # 计算性能指标
            parse_time = time.time() - start_time
            chapters_found = len(result.get('chapters', []))

            metrics = ParserMetrics(
                parser_name="builtin",
                parse_time=parse_time,
                chapters_found=chapters_found,
                success=result.get('success', False),
                error_message=result.get('error', ''),
                confidence_score=self._calculate_confidence(result),
                api_cost=0.0  # 内置解析器无API成本
            )

            # 添加指标到结果（转换为字典格式）
            result['metrics'] = {
                "parse_time": metrics.parse_time,
                "chapters_found": metrics.chapters_found,
                "confidence_score": metrics.confidence_score,
                "api_cost": metrics.api_cost
            }

            self.logger.info(
                f"[内置解析器] 完成: 找到{chapters_found}个章节, "
                f"耗时{parse_time:.2f}秒"
            )

            return result

        except Exception as e:
            parse_time = time.time() - start_time
            error_msg = str(e)
            self.logger.error(f"[内置解析器] 失败: {error_msg}")

            return {
                "success": False,
                "chapters": [],
                "statistics": {},
                "error": error_msg,
                "metrics": {
                    "parse_time": parse_time,
                    "chapters_found": 0,
                    "confidence_score": 0.0,
                    "api_cost": 0.0
                }
            }

    def _calculate_confidence(self, result: Dict) -> float:
        """计算解析置信度

        基于识别的章节数量和结构完整性评分
        """
        if not result.get('success'):
            return 0.0

        chapters = result.get('chapters', [])
        if not chapters:
            return 0.0

        # 评分因素:
        # 1. 章节数量(3-20个为正常范围)
        chapter_count = len(chapters)
        if chapter_count < 3:
            count_score = 30.0
        elif 3 <= chapter_count <= 20:
            count_score = 100.0
        else:
            count_score = max(50.0, 100.0 - (chapter_count - 20) * 2)

        # 2. 自动选中比例(白名单匹配率)
        auto_selected = sum(1 for ch in chapters if ch.get('auto_selected', False))
        selection_rate = (auto_selected / chapter_count) * 100 if chapter_count > 0 else 0
        selection_score = min(100.0, selection_rate * 2)  # 50%匹配即满分

        # 3. 层级结构完整性
        has_level1 = any(ch.get('level') == 1 for ch in chapters)
        has_level2 = any(ch.get('level') == 2 for ch in chapters)
        structure_score = 0.0
        if has_level1:
            structure_score += 50.0
        if has_level2:
            structure_score += 50.0

        # 加权平均
        confidence = (count_score * 0.4 + selection_score * 0.4 + structure_score * 0.2)

        return round(confidence, 1)

    def is_available(self) -> bool:
        """内置解析器始终可用"""
        return True

    def get_parser_info(self) -> Dict:
        """获取解析器信息"""
        return {
            "name": "builtin",
            "display_name": "内置解析器",
            "description": (
                "基于样式、大纲级别和编号模式的多方法解析器\n"
                "• 优势: 免费、快速、无需API\n"
                "• 劣势: 依赖文档样式规范性\n"
                "• 适用: 格式规范的标准招标文档"
            ),
            "requires_api": False,
            "cost_per_page": 0.0,
            "available": True,
            "methods": [
                "目录精确匹配",
                "大纲级别识别",
                "标题样式识别",
                "语义锚点匹配",
                "编号模式识别"
            ]
        }


# 注册解析器
from . import ParserFactory
ParserFactory.register_parser('builtin', BuiltinParser)
