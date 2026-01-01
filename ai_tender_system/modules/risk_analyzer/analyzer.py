#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
风险分析器核心模块
复用现有的 ParserManager 和 LLMClient 实现招标文件风险识别
"""

import json
import time
import re
from typing import List, Dict, Optional, Callable
from pathlib import Path

import sys
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from common.logger import get_module_logger
from common.llm_client import LLMClient
from modules.document_parser.parser_manager import ParserManager
from modules.document_parser.text_splitter import IntelligentTextSplitter

from .schemas import RiskItem, RiskAnalysisResult

logger = get_module_logger("risk_analyzer")


class RiskAnalyzer:
    """风险分析器 - 核心业务逻辑，可被小程序和Web端共用"""

    # 系统提示词
    SYSTEM_PROMPT = """你是一个资深的招标文件审查专家，专门帮助投标方识别招标文件中的废标风险和关键条款。

你需要从招标文本中识别以下类型的风险：
1. 废标条款：明确标注星号(*)的强制要求，不满足将直接废标
2. 资质要求：对投标方资质、证书的硬性要求
3. 技术参数：带有明确数值要求的技术指标
4. 商务条款：价格、付款、交付时间等关键商务要求
5. 隐性风险：容易被忽视但可能导致扣分或废标的条款

请以严格的JSON格式输出分析结果。"""

    # 分析提示词模板
    ANALYZE_PROMPT = """请分析以下招标文本片段，提取所有风险项：

{text}

请以JSON数组格式输出，每个风险项包含：
[
  {{
    "location": "条款位置（如：第三章 2.1节）",
    "requirement": "具体要求内容",
    "suggestion": "投标方应对建议",
    "risk_level": "high/medium/low",
    "risk_type": "废标条款/资质要求/技术参数/商务条款/隐性风险"
  }}
]

判断风险等级的标准：
- high: 带星号(*)的强制要求、明确的废标条款、必备资质
- medium: 重要的技术参数、商务条款、评分相关要求
- low: 一般性要求、建议性条款

如果该片段中没有明确的风险项，请返回空数组 []。
只返回JSON数组，不要添加其他文字说明。"""

    def __init__(self, model_name: str = 'deepseek-v3', chunk_size: int = 5000):
        """
        初始化分析器

        Args:
            model_name: AI模型名称，默认 deepseek-v3
            chunk_size: 分块大小（字符数），默认 5000
        """
        self.model_name = model_name
        self.chunk_size = chunk_size
        self.llm = LLMClient(model_name)
        self.parser = ParserManager()
        self.splitter = IntelligentTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=200,
            min_chunk_size=500,
            max_chunk_size=8000
        )
        self.total_tokens = 0

        logger.info(f"风险分析器初始化完成，模型: {model_name}, 分块大小: {chunk_size}")

    def analyze(self,
                file_path: str,
                progress_callback: Optional[Callable[[int, str], None]] = None,
                item_callback: Optional[Callable[[List['RiskItem']], None]] = None
                ) -> RiskAnalysisResult:
        """
        分析招标文件风险

        Args:
            file_path: 文件路径（绝对路径或相对于 data 目录的路径）
            progress_callback: 进度回调函数 (progress: int, message: str)
            item_callback: 增量结果回调函数，每分析完一个 chunk 调用一次

        Returns:
            RiskAnalysisResult: 分析结果
        """
        start_time = time.time()

        try:
            # 1. 解析文档
            if progress_callback:
                progress_callback(5, "正在解析文档...")

            text = self._parse_document(file_path)

            if not text or len(text.strip()) < 100:
                raise ValueError("文档内容为空或过短")

            logger.info(f"文档解析完成，总字符数: {len(text)}")

            # 2. 分块处理
            if progress_callback:
                progress_callback(10, "正在分块处理...")

            chunks = self._split_text(text)
            total_chunks = len(chunks)
            logger.info(f"文档分块完成，共 {total_chunks} 块")

            # 3. 逐块分析
            all_risk_items = []

            for i, chunk in enumerate(chunks):
                chunk_content = chunk.get('content', '') if isinstance(chunk, dict) else str(chunk)

                if progress_callback:
                    progress = 10 + int((i + 1) / total_chunks * 80)
                    progress_callback(progress, f"正在分析第 {i+1}/{total_chunks} 块...")

                try:
                    items = self._analyze_chunk(chunk_content, chunk_index=i)
                    all_risk_items.extend(items)
                    logger.debug(f"第 {i+1} 块分析完成，发现 {len(items)} 个风险项")

                    # 增量回调：每分析完一个 chunk 就通知调用方
                    if item_callback and items:
                        item_callback(items)

                except Exception as e:
                    logger.warning(f"分析第 {i+1} 块时出错: {e}")
                    continue

            # 4. 合并去重
            if progress_callback:
                progress_callback(95, "正在整理结果...")

            unique_items = self._deduplicate_items(all_risk_items)

            # 5. 生成总结和评分
            summary = self._generate_summary(unique_items)
            risk_score = self._calculate_risk_score(unique_items)

            # 6. 计算耗时
            analysis_time = time.time() - start_time

            if progress_callback:
                progress_callback(100, "分析完成")

            result = RiskAnalysisResult(
                risk_items=unique_items,
                summary=summary,
                risk_score=risk_score,
                total_chunks=total_chunks,
                analyzed_chunks=total_chunks,
                model_name=self.model_name,
                total_tokens=self.total_tokens,
                analysis_time=analysis_time
            )

            logger.info(f"风险分析完成，发现 {len(unique_items)} 个风险项，耗时 {analysis_time:.2f}s")

            return result

        except Exception as e:
            logger.error(f"风险分析失败: {e}")
            raise

    def _parse_document(self, file_path: str) -> str:
        """解析文档，提取文本内容"""
        # 处理路径
        path = Path(file_path)
        if not path.is_absolute():
            # 相对路径，尝试从项目根目录查找
            from common.config import get_config
            config = get_config()
            base_dir = config.get_path('base')
            path = Path(base_dir) / file_path

        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {path}")

        # 使用 ParserManager 解析
        return self.parser.parse_document_simple(str(path))

    def _split_text(self, text: str) -> List[Dict]:
        """分割文本为多个块"""
        # 使用固定大小策略，适合风险识别场景
        chunks = self.splitter.split_text(
            content=text,
            strategy='fixed_size'
        )
        return chunks

    def _analyze_chunk(self, chunk_text: str, chunk_index: int = 0) -> List[RiskItem]:
        """分析单个文本块，提取风险项"""
        if not chunk_text or len(chunk_text.strip()) < 50:
            return []

        prompt = self.ANALYZE_PROMPT.format(text=chunk_text)

        try:
            response = self.llm.call(
                prompt=prompt,
                system_prompt=self.SYSTEM_PROMPT,
                temperature=0.3,
                max_tokens=2000,
                purpose="风险项提取"
            )

            # 解析 JSON 响应
            items_data = self._parse_json_response(response)

            if not isinstance(items_data, list):
                return []

            return [
                RiskItem(
                    location=item.get('location', ''),
                    requirement=item.get('requirement', ''),
                    suggestion=item.get('suggestion', ''),
                    risk_level=item.get('risk_level', 'medium'),
                    risk_type=item.get('risk_type', ''),
                    source_chunk=chunk_index
                )
                for item in items_data
                if item.get('requirement')  # 过滤空项
            ]

        except json.JSONDecodeError as e:
            logger.warning(f"JSON解析失败: {e}")
            return []
        except Exception as e:
            logger.error(f"AI调用失败: {e}")
            return []

    def _parse_json_response(self, response: str) -> List[Dict]:
        """解析 AI 响应中的 JSON"""
        if not response or not response.strip():
            return []

        # 清理 markdown 代码块
        response = re.sub(r'^\s*```json\s*', '', response.strip())
        response = re.sub(r'\s*```\s*$', '', response.strip())

        # 尝试直接解析
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass

        # 尝试提取 JSON 数组
        json_match = re.search(r'\[[\s\S]*\]', response)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

        return []

    def _deduplicate_items(self, items: List[RiskItem]) -> List[RiskItem]:
        """去重风险项"""
        seen = set()
        unique = []

        for item in items:
            # 使用 requirement 的前80字符作为去重键
            key = item.requirement[:80] if len(item.requirement) > 80 else item.requirement
            key = key.strip().lower()

            if key and key not in seen:
                seen.add(key)
                unique.append(item)

        # 按风险等级排序（高风险在前）
        level_order = {'high': 0, 'medium': 1, 'low': 2}
        unique.sort(key=lambda x: level_order.get(x.risk_level, 1))

        return unique

    def _generate_summary(self, items: List[RiskItem]) -> str:
        """生成风险总结"""
        if not items:
            return "未发现明显的废标风险项。建议仔细阅读招标文件，确保满足所有要求。"

        high_count = sum(1 for item in items if item.risk_level == 'high')
        medium_count = sum(1 for item in items if item.risk_level == 'medium')
        low_count = sum(1 for item in items if item.risk_level == 'low')

        summary_parts = [f"共发现 {len(items)} 个风险项"]

        if high_count > 0:
            summary_parts.append(f"高风险 {high_count} 项")
        if medium_count > 0:
            summary_parts.append(f"中风险 {medium_count} 项")
        if low_count > 0:
            summary_parts.append(f"低风险 {low_count} 项")

        summary = "，".join(summary_parts) + "。"

        if high_count > 0:
            summary += "请重点关注高风险条款，这些可能直接导致废标。"
        else:
            summary += "建议逐项核对，确保投标文件满足所有要求。"

        return summary

    def _calculate_risk_score(self, items: List[RiskItem]) -> int:
        """
        计算风险评分（0-100，越高风险越大）

        评分规则：
        - 高风险项：每项 +15 分
        - 中风险项：每项 +8 分
        - 低风险项：每项 +3 分
        - 最高 100 分
        """
        if not items:
            return 0

        score = 0
        for item in items:
            if item.risk_level == 'high':
                score += 15
            elif item.risk_level == 'medium':
                score += 8
            else:
                score += 3

        return min(100, score)


# 便捷函数
def analyze_document(file_path: str,
                     model_name: str = 'deepseek-v3',
                     progress_callback: Optional[Callable[[int, str], None]] = None
                     ) -> RiskAnalysisResult:
    """
    便捷函数：分析文档风险

    Args:
        file_path: 文件路径
        model_name: AI模型名称
        progress_callback: 进度回调

    Returns:
        RiskAnalysisResult
    """
    analyzer = RiskAnalyzer(model_name=model_name)
    return analyzer.analyze(file_path, progress_callback)
