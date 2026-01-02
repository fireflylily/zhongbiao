#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
双向对账引擎 - 检查投标应答是否合规
使用提示词 D（合规审计法务）进行对账
"""

import json
import re
from typing import List, Dict, Optional, Callable
from pathlib import Path

import sys
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from common.logger import get_module_logger
from common.llm_client import LLMClient
from modules.document_parser.parser_manager import ParserManager

from .schemas import RiskItem, ReconcileResult
from .prompt_manager import PromptManager, PromptType

logger = get_module_logger("risk_analyzer.reconciler")


class Reconciler:
    """
    双向对账引擎

    对照招标文件要求检查投标应答的符合性
    """

    def __init__(self, model_name: str = 'deepseek-v3'):
        """
        初始化对账引擎

        Args:
            model_name: AI 模型名称
        """
        self.model_name = model_name
        self.llm = LLMClient(model_name)
        self.parser = ParserManager()
        self.prompt_manager = PromptManager()

        logger.info(f"双向对账引擎初始化完成，模型: {model_name}")

    def reconcile(self,
                  risk_items: List[RiskItem],
                  response_file_path: str,
                  progress_callback: Optional[Callable[[int, str], None]] = None
                  ) -> List[ReconcileResult]:
        """
        执行双向对账

        Args:
            risk_items: 风险项列表
            response_file_path: 应答文件路径
            progress_callback: 进度回调

        Returns:
            对账结果列表
        """
        if not risk_items:
            logger.warning("没有风险项需要对账")
            return []

        # 1. 解析应答文件
        if progress_callback:
            progress_callback(5, "正在解析应答文件...")

        response_text = self._parse_document(response_file_path)

        if not response_text or len(response_text.strip()) < 100:
            raise ValueError("应答文件内容为空或过短")

        logger.info(f"应答文件解析完成，总字符数: {len(response_text)}")

        # 2. 逐项对账
        results = []
        total_items = len(risk_items)

        for i, risk_item in enumerate(risk_items):
            progress = 10 + int((i + 1) / total_items * 85)

            if progress_callback:
                progress_callback(progress, f"正在对账第 {i+1}/{total_items} 项...")

            try:
                result = self._reconcile_item(risk_item, response_text, i)
                results.append(result)

                # 更新风险项的合规状态
                risk_item.compliance_status = result.compliance_status
                risk_item.compliance_note = result.overall_assessment
                risk_item.match_score = result.match_score
                risk_item.response_text = result.response_content[:500]  # 限制长度

                logger.debug(f"风险项 {i+1} 对账完成: {result.compliance_status}")

            except Exception as e:
                logger.warning(f"对账第 {i+1} 项失败: {e}")
                results.append(ReconcileResult(
                    risk_item_id=i,
                    compliance_status='unknown',
                    overall_assessment=f"对账失败: {str(e)}"
                ))

        if progress_callback:
            progress_callback(100, "对账完成")

        # 3. 生成对账汇总
        self._log_summary(results)

        return results

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

    def _reconcile_item(self,
                        risk_item: RiskItem,
                        response_text: str,
                        item_index: int) -> ReconcileResult:
        """对账单个风险项"""
        # 1. 在应答文件中查找相关内容
        related_content = self._find_related_content(risk_item, response_text)

        # 2. 构建提示词
        prompt = self.prompt_manager.get_prompt(
            PromptType.COMPLIANCE_AUDITOR,
            bid_requirement=self._format_requirement(risk_item),
            response_content=related_content
        )

        config = self.prompt_manager.get_config(PromptType.COMPLIANCE_AUDITOR)

        # 3. 调用 AI
        response = self.llm.call(
            prompt=prompt,
            system_prompt=config['system_prompt'],
            temperature=config['temperature'],
            max_tokens=config['max_tokens'],
            purpose=config['purpose']
        )

        # 4. 解析结果
        return self._parse_reconcile_response(response, item_index, related_content, risk_item)

    def _find_related_content(self, risk_item: RiskItem, response_text: str) -> str:
        """在应答文件中查找与风险项相关的内容"""
        # 提取关键词
        keywords = self._extract_keywords(risk_item)

        if not keywords:
            return "(未找到相关内容)"

        # 搜索包含关键词的段落
        paragraphs = response_text.split('\n\n')
        related = []
        scores = []

        for para in paragraphs:
            para = para.strip()
            if len(para) < 20:
                continue

            # 计算匹配分数
            score = 0
            for kw in keywords:
                if kw in para:
                    score += 1

            if score > 0:
                related.append((score, para))

        # 按分数排序，取前3个最相关的段落
        related.sort(key=lambda x: x[0], reverse=True)
        top_related = [para for score, para in related[:3]]

        if top_related:
            return '\n\n'.join(top_related)

        # 如果没找到，尝试更宽松的搜索
        return self._fuzzy_search(risk_item, response_text)

    def _extract_keywords(self, risk_item: RiskItem) -> List[str]:
        """提取风险项的关键词"""
        keywords = []

        # 从 requirement 提取
        text = risk_item.requirement + ' ' + risk_item.original_text

        # 提取中文词语
        chinese_words = re.findall(r'[\u4e00-\u9fa5]{2,8}', text)

        # 过滤常见词
        stop_words = {'应当', '必须', '需要', '要求', '提供', '具有', '满足', '符合',
                      '招标', '投标', '文件', '单位', '项目', '内容', '进行', '相关'}

        keywords = [w for w in chinese_words if w not in stop_words and len(w) >= 2]

        # 去重并限制数量
        seen = set()
        unique_keywords = []
        for kw in keywords:
            if kw not in seen:
                seen.add(kw)
                unique_keywords.append(kw)
                if len(unique_keywords) >= 10:
                    break

        return unique_keywords

    def _fuzzy_search(self, risk_item: RiskItem, response_text: str) -> str:
        """模糊搜索相关内容"""
        # 使用风险类型相关的关键词
        risk_type = risk_item.risk_type

        if '资质' in risk_type:
            search_terms = ['资质', '证书', '许可', '认证', '资格']
        elif '技术' in risk_type:
            search_terms = ['技术', '参数', '规格', '性能', '指标']
        elif '商务' in risk_type:
            search_terms = ['价格', '报价', '付款', '交付', '质保']
        else:
            search_terms = ['响应', '承诺', '声明', '说明']

        paragraphs = response_text.split('\n\n')
        for para in paragraphs:
            if any(term in para for term in search_terms):
                return para[:1000]

        return "(未找到相关内容，请人工核查)"

    def _format_requirement(self, risk_item: RiskItem) -> str:
        """格式化招标要求"""
        parts = []

        if risk_item.risk_type:
            parts.append(f"【{risk_item.risk_type}】")

        if risk_item.location:
            parts.append(f"位置: {risk_item.location}")

        parts.append(f"要求: {risk_item.requirement}")

        if risk_item.original_text:
            parts.append(f"原文: {risk_item.original_text[:300]}")

        return '\n'.join(parts)

    def _parse_reconcile_response(self,
                                   response: str,
                                   item_index: int,
                                   response_content: str,
                                   risk_item: RiskItem) -> ReconcileResult:
        """解析对账响应"""
        if not response:
            return ReconcileResult(
                risk_item_id=item_index,
                compliance_status='unknown',
                overall_assessment="AI 响应为空"
            )

        # 清理 markdown 代码块
        response = re.sub(r'^\s*```json\s*', '', response.strip())
        response = re.sub(r'\s*```\s*$', '', response.strip())

        try:
            data = json.loads(response)

            return ReconcileResult(
                risk_item_id=item_index,
                bid_requirement=risk_item.requirement,
                response_content=response_content[:500],
                compliance_status=data.get('compliance_status', 'unknown'),
                match_score=data.get('match_score', 0.0),
                issues=data.get('issues', []),
                overall_assessment=data.get('overall_assessment', ''),
                fix_suggestion=self._extract_fix_suggestion(data),
                fix_priority=data.get('fix_priority', 'normal')
            )

        except json.JSONDecodeError:
            logger.warning("对账响应 JSON 解析失败")
            return ReconcileResult(
                risk_item_id=item_index,
                compliance_status='unknown',
                overall_assessment="响应解析失败"
            )

    def _extract_fix_suggestion(self, data: Dict) -> str:
        """提取修复建议"""
        issues = data.get('issues', [])
        if issues:
            suggestions = [issue.get('suggestion', '') for issue in issues if issue.get('suggestion')]
            return '; '.join(suggestions[:3])
        return ''

    def _log_summary(self, results: List[ReconcileResult]):
        """记录对账汇总"""
        total = len(results)
        compliant = sum(1 for r in results if r.compliance_status == 'compliant')
        non_compliant = sum(1 for r in results if r.compliance_status == 'non_compliant')
        partial = sum(1 for r in results if r.compliance_status == 'partial')

        logger.info(f"双向对账完成: 共 {total} 项, "
                   f"🟢通过 {compliant}, 🔴不通过 {non_compliant}, 🟡部分符合 {partial}")


# 便捷函数
def reconcile_response(risk_items: List[RiskItem],
                       response_file_path: str,
                       model_name: str = 'deepseek-v3',
                       progress_callback: Optional[Callable[[int, str], None]] = None
                       ) -> List[ReconcileResult]:
    """
    便捷函数：执行双向对账

    Args:
        risk_items: 风险项列表
        response_file_path: 应答文件路径
        model_name: AI 模型名称
        progress_callback: 进度回调

    Returns:
        对账结果列表
    """
    reconciler = Reconciler(model_name=model_name)
    return reconciler.reconcile(risk_items, response_file_path, progress_callback)
