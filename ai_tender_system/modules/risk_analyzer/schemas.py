#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
风险分析数据结构定义
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional
from datetime import datetime


@dataclass
class RiskItem:
    """风险项数据类"""
    location: str           # 条款位置（如：第三章 2.1节）
    requirement: str        # 具体要求内容
    suggestion: str         # 避坑建议
    risk_level: str = 'medium'  # high/medium/low
    risk_type: str = ''     # 废标条款/资质要求/技术参数/商务条款/隐性风险
    source_chunk: int = 0   # 来源分块索引
    confidence: float = 0.8 # 置信度

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
            confidence=data.get('confidence', 0.8)
        )


@dataclass
class RiskAnalysisResult:
    """分析结果数据类"""
    risk_items: List[RiskItem] = field(default_factory=list)
    summary: str = ''
    risk_score: int = 0  # 0-100，越高风险越大
    total_chunks: int = 0
    analyzed_chunks: int = 0
    model_name: str = 'deepseek-v3'
    total_tokens: int = 0
    analysis_time: float = 0.0  # 分析耗时（秒）

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
            'statistics': self.get_statistics()
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

    @classmethod
    def from_dict(cls, data: Dict) -> 'RiskAnalysisResult':
        risk_items = [RiskItem.from_dict(item) for item in data.get('risk_items', [])]
        return cls(
            risk_items=risk_items,
            summary=data.get('summary', ''),
            risk_score=data.get('risk_score', 0),
            total_chunks=data.get('total_chunks', 0),
            analyzed_chunks=data.get('analyzed_chunks', 0),
            model_name=data.get('model_name', 'deepseek-v3'),
            total_tokens=data.get('total_tokens', 0),
            analysis_time=data.get('analysis_time', 0.0)
        )


@dataclass
class RiskTask:
    """风险分析任务"""
    task_id: str
    openid: str = ''
    user_id: Optional[int] = None
    file_id: str = ''
    original_filename: str = ''
    file_size: int = 0

    # 任务状态
    status: str = 'pending'  # pending/parsing/analyzing/completed/failed
    progress: int = 0        # 0-100
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
            'model_name': self.model_name
        }
