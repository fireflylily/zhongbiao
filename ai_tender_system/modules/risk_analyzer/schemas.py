#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
风险分析数据结构定义 - 标书宝 5.0 升级版
新增字段：original_text, position_index, todo_action, deep_analysis, compliance_status 等
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional
from datetime import datetime


@dataclass
class RiskItem:
    """
    风险项数据类 - 5.0 升级版

    新增字段：
    - original_text: 招标文件原文
    - position_index: 位置索引（如 P12, 第三章2.1）
    - todo_action: 具体 Todo 操作
    - deep_analysis: 问题深度解析
    - compliance_status: 合规状态（对账后填充）
    - compliance_note: 合规备注
    - response_text: 应答文件对应内容
    """
    # 基础字段（原有）
    location: str                   # 条款位置（如：第三章 2.1节）
    requirement: str                # 具体要求内容（精炼总结）
    suggestion: str                 # 避坑建议
    risk_level: str = 'medium'      # high/medium/low
    risk_type: str = ''             # 废标条款/★条款/资质要求/技术参数/商务条款/隐性风险
    source_chunk: int = 0           # 来源分块索引
    confidence: float = 0.8         # 置信度

    # 5.0 新增字段
    original_text: str = ''         # 招标文件原文摘录
    position_index: str = ''        # 位置索引（P12, 第三章2.1）
    todo_action: str = ''           # 具体 Todo 操作
    deep_analysis: str = ''         # 问题深度解析

    # 双向对账字段
    compliance_status: str = ''     # compliant/non_compliant/partial/unknown
    compliance_note: str = ''       # 合规备注
    response_text: str = ''         # 应答文件对应内容
    match_score: float = 0.0        # 匹配度 0-1

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'RiskItem':
        return cls(
            location=data.get('location', ''),
            requirement=data.get('requirement', ''),
            suggestion=data.get('suggestion', ''),
            risk_level=data.get('risk_level', 'medium'),
            risk_type=data.get('risk_type', ''),
            source_chunk=data.get('source_chunk', 0),
            confidence=data.get('confidence', 0.8),
            # 5.0 新增字段
            original_text=data.get('original_text', ''),
            position_index=data.get('position_index', ''),
            todo_action=data.get('todo_action', ''),
            deep_analysis=data.get('deep_analysis', ''),
            # 双向对账字段
            compliance_status=data.get('compliance_status', ''),
            compliance_note=data.get('compliance_note', ''),
            response_text=data.get('response_text', ''),
            match_score=data.get('match_score', 0.0)
        )

    def get_risk_level_emoji(self) -> str:
        """获取风险等级 emoji"""
        emoji_map = {
            'high': '🔴',
            'medium': '🟡',
            'low': '🔵'
        }
        return emoji_map.get(self.risk_level, '🟡')

    def get_compliance_emoji(self) -> str:
        """获取合规状态 emoji"""
        emoji_map = {
            'compliant': '🟢',
            'non_compliant': '🔴',
            'partial': '🟡',
            'unknown': '⚪'
        }
        return emoji_map.get(self.compliance_status, '⚪')


@dataclass
class ReconcileResult:
    """
    双向对账结果 - 5.0 新增
    """
    risk_item_id: int = 0           # 关联的风险项索引
    bid_requirement: str = ''       # 招标要求
    response_content: str = ''      # 应答内容
    compliance_status: str = ''     # compliant/non_compliant/partial
    match_score: float = 0.0        # 匹配度 0-1
    issues: List[Dict] = field(default_factory=list)  # 问题列表
    overall_assessment: str = ''    # 总体评估
    fix_suggestion: str = ''        # 修复建议
    fix_priority: str = 'normal'    # urgent/normal/optional

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'ReconcileResult':
        return cls(
            risk_item_id=data.get('risk_item_id', 0),
            bid_requirement=data.get('bid_requirement', ''),
            response_content=data.get('response_content', ''),
            compliance_status=data.get('compliance_status', ''),
            match_score=data.get('match_score', 0.0),
            issues=data.get('issues', []),
            overall_assessment=data.get('overall_assessment', ''),
            fix_suggestion=data.get('fix_suggestion', ''),
            fix_priority=data.get('fix_priority', 'normal')
        )


@dataclass
class RiskAnalysisResult:
    """分析结果数据类 - 5.0 升级版"""
    risk_items: List[RiskItem] = field(default_factory=list)
    summary: str = ''
    risk_score: int = 0             # 0-100，越高风险越大
    total_chunks: int = 0
    analyzed_chunks: int = 0
    model_name: str = 'deepseek-v3'
    total_tokens: int = 0
    analysis_time: float = 0.0      # 分析耗时（秒）

    # 5.0 新增
    has_toc: bool = False           # 是否有目录
    exclude_chapters: List[str] = field(default_factory=list)  # 排除的章节
    reconcile_results: List[ReconcileResult] = field(default_factory=list)  # 对账结果

    def to_dict(self) -> Dict:
        return {
            'risk_items': [item.to_dict() for item in self.risk_items],
            'summary': self.summary,
            'risk_score': self.risk_score,
            'total_chunks': self.total_chunks,
            'analyzed_chunks': self.analyzed_chunks,
            'model_name': self.model_name,
            'total_tokens': self.total_tokens,
            'analysis_time': self.analysis_time,
            'statistics': self.get_statistics(),
            # 5.0 新增
            'has_toc': self.has_toc,
            'exclude_chapters': self.exclude_chapters,
            'reconcile_results': [r.to_dict() for r in self.reconcile_results],
            'reconcile_summary': self.get_reconcile_summary()
        }

    def get_statistics(self) -> Dict:
        """获取风险统计"""
        high_count = sum(1 for item in self.risk_items if item.risk_level == 'high')
        medium_count = sum(1 for item in self.risk_items if item.risk_level == 'medium')
        low_count = sum(1 for item in self.risk_items if item.risk_level == 'low')

        return {
            'total_items': len(self.risk_items),
            'high_risk_count': high_count,
            'medium_risk_count': medium_count,
            'low_risk_count': low_count
        }

    def get_reconcile_summary(self) -> Dict:
        """获取对账汇总"""
        if not self.reconcile_results:
            return {}

        compliant = sum(1 for r in self.reconcile_results if r.compliance_status == 'compliant')
        non_compliant = sum(1 for r in self.reconcile_results if r.compliance_status == 'non_compliant')
        partial = sum(1 for r in self.reconcile_results if r.compliance_status == 'partial')

        return {
            'total_checked': len(self.reconcile_results),
            'compliant': compliant,
            'non_compliant': non_compliant,
            'partial': partial,
            'compliance_rate': compliant / len(self.reconcile_results) if self.reconcile_results else 0
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'RiskAnalysisResult':
        risk_items = [RiskItem.from_dict(item) for item in data.get('risk_items', [])]
        reconcile_results = [ReconcileResult.from_dict(r) for r in data.get('reconcile_results', [])]
        return cls(
            risk_items=risk_items,
            summary=data.get('summary', ''),
            risk_score=data.get('risk_score', 0),
            total_chunks=data.get('total_chunks', 0),
            analyzed_chunks=data.get('analyzed_chunks', 0),
            model_name=data.get('model_name', 'deepseek-v3'),
            total_tokens=data.get('total_tokens', 0),
            analysis_time=data.get('analysis_time', 0.0),
            has_toc=data.get('has_toc', False),
            exclude_chapters=data.get('exclude_chapters', []),
            reconcile_results=reconcile_results
        )


@dataclass
class RiskTask:
    """风险分析任务 - 5.0 升级版"""
    task_id: str
    openid: str = ''
    user_id: Optional[int] = None
    file_id: str = ''
    original_filename: str = ''
    file_size: int = 0

    # 任务状态
    status: str = 'pending'         # pending/parsing/analyzing/reconciling/completed/failed
    progress: int = 0               # 0-100
    current_step: str = ''
    error_message: str = ''

    # 解析信息
    total_text_length: int = 0
    chunk_count: int = 0

    # 分析结果
    result: Optional[RiskAnalysisResult] = None

    # 时间戳
    created_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # AI 模型信息
    model_name: str = 'deepseek-v3'

    # 5.0 新增字段
    file_path: str = ''             # 招标文件路径
    response_file_path: str = ''    # 应答文件路径
    response_file_name: str = ''    # 应答文件名
    has_toc: bool = False           # 是否有目录
    analysis_mode: str = 'bid_only' # bid_only / bid_response_reconcile

    def to_dict(self) -> Dict:
        return {
            'task_id': self.task_id,
            'openid': self.openid,
            'user_id': self.user_id,
            'file_id': self.file_id,
            'original_filename': self.original_filename,
            'file_size': self.file_size,
            'status': self.status,
            'progress': self.progress,
            'current_step': self.current_step,
            'error_message': self.error_message,
            'total_text_length': self.total_text_length,
            'chunk_count': self.chunk_count,
            'result': self.result.to_dict() if self.result else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'model_name': self.model_name,
            # 5.0 新增
            'file_path': self.file_path,
            'response_file_path': self.response_file_path,
            'response_file_name': self.response_file_name,
            'has_toc': self.has_toc,
            'analysis_mode': self.analysis_mode
        }


@dataclass
class TodoItem:
    """Todo 操作项 - 5.0 新增"""
    risk_item_index: int = 0        # 关联的风险项索引
    action: str = ''                # 动作描述
    assignee_type: str = ''         # 商务/技术/法务/财务/项目经理
    priority: str = 'P1'            # P0/P1/P2
    checklist: List[str] = field(default_factory=list)  # 子步骤
    deadline_hint: str = ''         # 时间节点提示
    warning: str = ''               # 特别注意事项

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'TodoItem':
        return cls(
            risk_item_index=data.get('risk_item_index', 0),
            action=data.get('action', ''),
            assignee_type=data.get('assignee_type', ''),
            priority=data.get('priority', 'P1'),
            checklist=data.get('checklist', []),
            deadline_hint=data.get('deadline_hint', ''),
            warning=data.get('warning', '')
        )

    def get_priority_emoji(self) -> str:
        """获取优先级 emoji"""
        emoji_map = {
            'P0': '🔴',
            'P1': '🟡',
            'P2': '🔵'
        }
        return emoji_map.get(self.priority, '🟡')
