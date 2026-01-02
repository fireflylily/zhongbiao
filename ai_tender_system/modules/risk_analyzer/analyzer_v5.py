#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
风险分析器 5.0 版本 - 专家接力式分析流水线

实现流程：
1. 目录解析 (提示词 A) → 识别排除章节
2. 智能切片 → 目录感知 + 智能降级
3. 风险提取 (提示词 B) → 提取★条款和废标项
4. Todo 生成 (提示词 C) → 生成具体操作建议
5. 双向对账 (提示词 D) → 检查应答合规性（可选）
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

from .schemas import RiskItem, RiskAnalysisResult, TodoItem
from .prompt_manager import PromptManager, PromptType
from .toc_extractor import TocExtractor, TocResult
from .smart_chunker import SmartChunker, DocumentChunk

logger = get_module_logger("risk_analyzer.v5")


class RiskAnalyzerV5:
    """
    风险分析器 5.0 版本

    特性：
    - 目录感知切片：有目录时精准切片，无目录时智能降级
    - 专家接力式提示词：A→B→C 接力处理
    - 增量结果回调：每分析完一个切片就回调
    - 完整的 5.0 字段支持
    """

    def __init__(self, model_name: str = 'deepseek-v3', chunk_size: int = 5000):
        """
        初始化分析器

        Args:
            model_name: AI 模型名称
            chunk_size: 分块大小（字符数）
        """
        self.model_name = model_name
        self.chunk_size = chunk_size

        self.llm = LLMClient(model_name)
        self.parser = ParserManager()
        self.prompt_manager = PromptManager()
        self.toc_extractor = TocExtractor(use_ai=True, model_name=model_name)

        self.total_tokens = 0

        logger.info(f"风险分析器 5.0 初始化完成，模型: {model_name}")

    def analyze(self,
                file_path: str,
                progress_callback: Optional[Callable[[int, str], None]] = None,
                item_callback: Optional[Callable[[List['RiskItem']], None]] = None
                ) -> RiskAnalysisResult:
        """
        分析招标文件风险（5.0 完整流程）

        Args:
            file_path: 文件路径
            progress_callback: 进度回调 (progress: int, message: str)
            item_callback: 增量结果回调

        Returns:
            RiskAnalysisResult: 分析结果
        """
        start_time = time.time()

        try:
            # ========== Stage 1: 解析文档 ==========
            if progress_callback:
                progress_callback(5, "正在解析文档...")

            text = self._parse_document(file_path)

            if not text or len(text.strip()) < 100:
                raise ValueError("文档内容为空或过短")

            logger.info(f"文档解析完成，总字符数: {len(text)}")

            # ========== Stage 2: 目录解析 (提示词 A) ==========
            if progress_callback:
                progress_callback(10, "正在分析目录结构...")

            toc_result = self.toc_extractor.extract(text)
            has_toc = toc_result.has_toc

            if has_toc:
                logger.info(f"目录解析成功，发现 {len(toc_result.entries)} 个章节，"
                           f"排除 {len(toc_result.exclude_chapters)} 个合同章节")
            else:
                logger.info("未识别到目录结构，将使用智能降级策略")

            # ========== Stage 3: 智能切片 ==========
            if progress_callback:
                progress_callback(15, "正在智能切片...")

            chunker = SmartChunker(toc_result=toc_result, chunk_size=self.chunk_size)
            chunks = chunker.chunk_document(text)
            total_chunks = len(chunks)

            logger.info(f"智能切片完成，共 {total_chunks} 个切片")

            # ========== Stage 4: 风险提取 (提示词 B) ==========
            if progress_callback:
                progress_callback(20, "正在提取风险项...")

            all_risk_items = []

            for i, chunk in enumerate(chunks):
                progress = 20 + int((i + 1) / total_chunks * 55)

                if progress_callback:
                    progress_callback(progress, f"正在分析: {chunk.title}")

                try:
                    items = self._analyze_chunk(chunk, has_toc=has_toc, chunk_index=i)
                    all_risk_items.extend(items)

                    logger.debug(f"切片 {i+1}/{total_chunks} ({chunk.title}) "
                                f"发现 {len(items)} 个风险项")

                    # 增量回调
                    if item_callback and items:
                        item_callback(items)

                except Exception as e:
                    logger.warning(f"分析切片 {i+1} 失败: {e}")
                    continue

            # ========== Stage 5: Todo 生成 (提示词 C) ==========
            if progress_callback:
                progress_callback(80, "正在生成操作建议...")

            if all_risk_items:
                todos = self._generate_todos(all_risk_items)
                # 将 todo 合并到对应的 risk_item
                self._merge_todos(all_risk_items, todos)

            # ========== Stage 6: 合并去重 ==========
            if progress_callback:
                progress_callback(90, "正在整理结果...")

            unique_items = self._deduplicate_items(all_risk_items)

            # ========== Stage 7: 生成总结和评分 ==========
            summary = self._generate_summary(unique_items)
            risk_score = self._calculate_risk_score(unique_items)

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
                analysis_time=analysis_time,
                has_toc=has_toc,
                exclude_chapters=toc_result.exclude_chapters if has_toc else []
            )

            logger.info(f"风险分析 5.0 完成，发现 {len(unique_items)} 个风险项，"
                       f"耗时 {analysis_time:.2f}s")

            return result

        except Exception as e:
            logger.error(f"风险分析失败: {e}")
            raise

    def _parse_document(self, file_path: str) -> str:
        """解析文档"""
        path = Path(file_path)
        if not path.is_absolute():
            from common.config import get_config
            config = get_config()
            base_dir = config.get_path('base')
            path = Path(base_dir) / file_path

        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {path}")

        return self.parser.parse_document_simple(str(path))

    def _analyze_chunk(self,
                       chunk: DocumentChunk,
                       has_toc: bool,
                       chunk_index: int) -> List[RiskItem]:
        """分析单个切片（使用提示词 B）"""
        if not chunk.content or len(chunk.content.strip()) < 50:
            return []

        # 获取提示词配置
        prompt = self.prompt_manager.get_prompt(
            PromptType.BID_EVALUATOR,
            chapter_title=chunk.title,
            chapter_content=chunk.content,
            has_toc=has_toc
        )

        config = self.prompt_manager.get_config(PromptType.BID_EVALUATOR)

        try:
            response = self.llm.call(
                prompt=prompt,
                system_prompt=config['system_prompt'],
                temperature=config['temperature'],
                max_tokens=config['max_tokens'],
                purpose=config['purpose']
            )

            # 解析响应
            items_data = self._parse_json_response(response)

            if not isinstance(items_data, dict) or 'items' not in items_data:
                if isinstance(items_data, list):
                    items_list = items_data
                else:
                    return []
            else:
                items_list = items_data.get('items', [])

            # 转换为 RiskItem 对象
            return [
                RiskItem(
                    location=item.get('location', ''),
                    requirement=item.get('requirement', ''),
                    suggestion=item.get('suggestion', self._get_default_suggestion(item)),
                    risk_level=item.get('risk_level', 'medium'),
                    risk_type=item.get('risk_type', ''),
                    source_chunk=chunk_index,
                    # 5.0 新增字段
                    original_text=item.get('original_text', ''),
                    position_index=item.get('position_index', ''),
                    deep_analysis=item.get('deep_analysis', '')
                )
                for item in items_list
                if item.get('requirement')
            ]

        except Exception as e:
            logger.error(f"切片分析失败: {e}")
            return []

    def _generate_todos(self, risk_items: List[RiskItem]) -> List[TodoItem]:
        """生成 Todo 操作（使用提示词 C）"""
        if not risk_items:
            return []

        # 准备风险项 JSON
        risk_items_json = json.dumps(
            [item.to_dict() for item in risk_items[:20]],  # 限制数量
            ensure_ascii=False,
            indent=2
        )

        prompt = self.prompt_manager.get_prompt(
            PromptType.TODO_GENERATOR,
            risk_items_json=risk_items_json
        )

        config = self.prompt_manager.get_config(PromptType.TODO_GENERATOR)

        try:
            response = self.llm.call(
                prompt=prompt,
                system_prompt=config['system_prompt'],
                temperature=config['temperature'],
                max_tokens=config['max_tokens'],
                purpose=config['purpose']
            )

            data = self._parse_json_response(response)
            todos_data = data.get('todos', []) if isinstance(data, dict) else []

            return [TodoItem.from_dict(t) for t in todos_data]

        except Exception as e:
            logger.warning(f"Todo 生成失败: {e}")
            return []

    def _merge_todos(self, risk_items: List[RiskItem], todos: List[TodoItem]):
        """将 Todo 合并到对应的 RiskItem"""
        for todo in todos:
            idx = todo.risk_item_index
            if 0 <= idx < len(risk_items):
                risk_items[idx].todo_action = todo.action

    def _get_default_suggestion(self, item: Dict) -> str:
        """生成默认的避坑建议"""
        risk_type = item.get('risk_type', '')
        if '废标' in risk_type or '★' in risk_type:
            return "务必满足此条款要求，否则可能导致废标"
        elif '资质' in risk_type:
            return "确认资质证书有效期，准备彩色扫描件"
        elif '技术' in risk_type:
            return "仔细核对技术参数，确保满足所有指标要求"
        else:
            return "仔细阅读要求，确保完整响应"

    def _parse_json_response(self, response: str) -> Dict:
        """解析 AI 响应中的 JSON"""
        if not response or not response.strip():
            return {}

        # 清理 markdown 代码块
        response = re.sub(r'^\s*```json\s*', '', response.strip())
        response = re.sub(r'\s*```\s*$', '', response.strip())

        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass

        # 尝试提取 JSON 对象
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

        # 尝试提取 JSON 数组
        json_match = re.search(r'\[[\s\S]*\]', response)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

        return {}

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

        # 按风险等级排序
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
            summary_parts.append(f"🔴高风险 {high_count} 项")
        if medium_count > 0:
            summary_parts.append(f"🟡中风险 {medium_count} 项")
        if low_count > 0:
            summary_parts.append(f"🔵低风险 {low_count} 项")

        summary = "，".join(summary_parts) + "。"

        if high_count > 0:
            summary += "请重点关注高风险条款，这些可能直接导致废标！"
        else:
            summary += "建议逐项核对，确保投标文件满足所有要求。"

        return summary

    def _calculate_risk_score(self, items: List[RiskItem]) -> int:
        """计算风险评分（0-100）"""
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
def analyze_document_v5(file_path: str,
                        model_name: str = 'deepseek-v3',
                        progress_callback: Optional[Callable[[int, str], None]] = None
                        ) -> RiskAnalysisResult:
    """
    便捷函数：使用 5.0 版本分析文档风险

    Args:
        file_path: 文件路径
        model_name: AI 模型名称
        progress_callback: 进度回调

    Returns:
        RiskAnalysisResult
    """
    analyzer = RiskAnalyzerV5(model_name=model_name)
    return analyzer.analyze(file_path, progress_callback)
