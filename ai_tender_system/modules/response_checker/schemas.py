#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
应答文件自检查数据结构定义

采用清单式检查，每条检查项标记"符合/不符合"状态
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum


class CheckStatus(Enum):
    """检查状态"""
    PASS = "符合"
    FAIL = "不符合"
    UNKNOWN = "无法判断"
    PENDING = "待检查"


class CheckCategoryType(Enum):
    """检查类别类型"""
    COMPLETENESS = "completeness"           # 完整性检查
    SIGNATURE_SEAL = "signature_seal"       # 签字盖章检查
    PAGE_NUMBER = "page_number"             # 页码检查
    INDEX_TABLE = "index_table"             # 索引表检查
    LEGAL_PERSON_ID = "legal_person_id"     # 法人身份证检查
    AUTHORIZED_ID = "authorized_id"         # 被授权人身份证检查
    BUSINESS_LICENSE = "business_license"   # 营业执照检查
    RESPONSE_DATE = "response_date"         # 应答日期检查
    PRICE_CHECK = "price_check"             # 报价检查
    PERFORMANCE = "performance"             # 业绩检查


# 检查类别中文名称映射
CATEGORY_NAMES = {
    CheckCategoryType.COMPLETENESS: "完整性检查",
    CheckCategoryType.SIGNATURE_SEAL: "签字盖章检查",
    CheckCategoryType.PAGE_NUMBER: "页码检查",
    CheckCategoryType.INDEX_TABLE: "索引表检查",
    CheckCategoryType.LEGAL_PERSON_ID: "法人身份证检查",
    CheckCategoryType.AUTHORIZED_ID: "被授权人身份证检查",
    CheckCategoryType.BUSINESS_LICENSE: "营业执照检查",
    CheckCategoryType.RESPONSE_DATE: "应答日期检查",
    CheckCategoryType.PRICE_CHECK: "报价检查",
    CheckCategoryType.PERFORMANCE: "业绩检查",
}


# 各类别的检查项定义
CHECK_ITEMS_DEFINITION = {
    CheckCategoryType.COMPLETENESS: [
        {"id": "completeness_1", "name": "所有表格单元格已填写完整"},
        {"id": "completeness_2", "name": "所有横线填写处已填写"},
        {"id": "completeness_3", "name": "所有勾选项已勾选"},
    ],
    CheckCategoryType.SIGNATURE_SEAL: [
        {"id": "seal_1", "name": "公章清晰完整"},
        {"id": "seal_2", "name": "骑缝章连续无遗漏"},
        {"id": "seal_3", "name": "每处需签字处均已手写签名"},
    ],
    CheckCategoryType.PAGE_NUMBER: [
        {"id": "page_1", "name": "包含目录页"},
        {"id": "page_2", "name": "页码连续正确"},
    ],
    CheckCategoryType.INDEX_TABLE: [
        {"id": "index_1", "name": "包含索引表"},
        {"id": "index_2", "name": "索引页码与实际一致"},
    ],
    CheckCategoryType.LEGAL_PERSON_ID: [
        {"id": "legal_id_1", "name": "身份证在有效期内"},
        {"id": "legal_id_2", "name": "姓名与文档中一致"},
        {"id": "legal_id_3", "name": "年龄合理（18-80岁）"},
    ],
    CheckCategoryType.AUTHORIZED_ID: [
        {"id": "auth_id_1", "name": "身份证在有效期内"},
        {"id": "auth_id_2", "name": "姓名与授权书一致"},
        {"id": "auth_id_3", "name": "年龄合理（18-80岁）"},
    ],
    CheckCategoryType.BUSINESS_LICENSE: [
        {"id": "license_1", "name": "营业执照在有效期内"},
        {"id": "license_2", "name": "公司名称全文一致"},
        {"id": "license_3", "name": "统一社会信用代码一致"},
    ],
    CheckCategoryType.RESPONSE_DATE: [
        {"id": "date_1", "name": "文档中所有应答日期一致"},
        {"id": "date_2", "name": "授权有效期覆盖投标日期"},
    ],
    CheckCategoryType.PRICE_CHECK: [
        {"id": "price_1", "name": "大小写金额一致"},
        {"id": "price_2", "name": "单价×数量=总价 计算正确"},
        {"id": "price_3", "name": "报价未超过最高限价"},
    ],
    CheckCategoryType.PERFORMANCE: [
        {"id": "perf_1", "name": "包含合同首页"},
        {"id": "perf_2", "name": "包含盖章页"},
        {"id": "perf_3", "name": "包含合同日期页"},
        {"id": "perf_4", "name": "包含甲乙方信息页"},
    ],
}


@dataclass
class CheckItem:
    """
    单条检查项
    """
    item_id: str = ""                   # 检查项ID
    category: str = ""                  # 所属类别
    name: str = ""                      # 检查项名称
    status: str = "待检查"              # 符合 / 不符合 / 无法判断
    detail: str = ""                    # 详细说明（不符合时说明原因）
    location: str = ""                  # 问题位置（如：P12）
    suggestion: str = ""                # 修改建议（不符合时）

    # AI分析相关
    ai_confidence: float = 0.0          # AI置信度 0-1

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CheckItem':
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

    def get_status_icon(self) -> str:
        """获取状态图标"""
        icon_map = {
            "符合": "✅",
            "不符合": "❌",
            "无法判断": "⚠️",
            "待检查": "⏳"
        }
        return icon_map.get(self.status, "⏳")

    def is_pass(self) -> bool:
        return self.status == "符合"

    def is_fail(self) -> bool:
        return self.status == "不符合"


@dataclass
class CheckCategory:
    """
    检查类别
    """
    category_id: str = ""               # 类别ID
    category_name: str = ""             # 类别名称
    items: List[CheckItem] = field(default_factory=list)  # 该类别下的检查项
    pass_count: int = 0                 # 符合数量
    fail_count: int = 0                 # 不符合数量
    unknown_count: int = 0              # 无法判断数量

    def to_dict(self) -> Dict[str, Any]:
        return {
            'category_id': self.category_id,
            'category_name': self.category_name,
            'items': [item.to_dict() for item in self.items],
            'pass_count': self.pass_count,
            'fail_count': self.fail_count,
            'unknown_count': self.unknown_count,
            'total_count': len(self.items),
            'status_icon': self.get_status_icon()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CheckCategory':
        items = [CheckItem.from_dict(item) for item in data.get('items', [])]
        return cls(
            category_id=data.get('category_id', ''),
            category_name=data.get('category_name', ''),
            items=items,
            pass_count=data.get('pass_count', 0),
            fail_count=data.get('fail_count', 0),
            unknown_count=data.get('unknown_count', 0)
        )

    def calculate_counts(self):
        """计算各状态数量"""
        self.pass_count = sum(1 for item in self.items if item.status == "符合")
        self.fail_count = sum(1 for item in self.items if item.status == "不符合")
        self.unknown_count = sum(1 for item in self.items if item.status == "无法判断")

    def get_status_icon(self) -> str:
        """获取类别状态图标"""
        if self.fail_count > 0:
            return "❌"
        elif self.unknown_count > 0:
            return "⚠️"
        else:
            return "✅"

    def get_summary(self) -> str:
        """获取类别汇总"""
        total = len(self.items)
        if self.fail_count > 0:
            return f"❌{self.pass_count}/{total}"
        else:
            return f"✅{self.pass_count}/{total}"


@dataclass
class ExtractedInfo:
    """
    从文档提取的信息（用于一致性比对）
    """
    # 公司信息
    company_name: str = ""
    unified_credit_code: str = ""

    # 法人信息
    legal_person_name: str = ""
    legal_person_id_number: str = ""
    legal_person_id_expiry: str = ""
    legal_person_birth_date: str = ""

    # 被授权人信息
    authorized_person_name: str = ""
    authorized_person_id_number: str = ""
    authorized_person_id_expiry: str = ""
    authorized_person_birth_date: str = ""

    # 营业执照信息
    license_expiry: str = ""
    license_company_name: str = ""
    license_credit_code: str = ""

    # 应答日期信息
    response_dates: List[str] = field(default_factory=list)
    authorization_valid_period: str = ""
    bid_deadline: str = ""              # 投标截止日期

    # 报价信息
    total_price_upper: str = ""         # 大写金额
    total_price_lower: float = 0.0      # 小写金额
    unit_prices: List[Dict] = field(default_factory=list)  # 单价明细
    max_limit_price: float = 0.0        # 最高限价

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExtractedInfo':
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class ResponseCheckResult:
    """
    完整检查结果
    """
    # 基本信息
    task_id: str = ""
    file_name: str = ""
    file_path: str = ""
    check_time: str = ""                # 检查时间

    # 检查结果
    categories: List[CheckCategory] = field(default_factory=list)

    # 提取的信息
    extracted_info: ExtractedInfo = field(default_factory=ExtractedInfo)

    # 统计信息
    total_items: int = 0                # 总检查项数
    pass_count: int = 0                 # 符合数量
    fail_count: int = 0                 # 不符合数量
    unknown_count: int = 0              # 无法判断数量

    # 处理信息
    model_name: str = "deepseek-v3"
    analysis_time: float = 0.0          # 分析耗时（秒）
    total_pages: int = 0                # 文档总页数

    def to_dict(self) -> Dict[str, Any]:
        return {
            'task_id': self.task_id,
            'file_name': self.file_name,
            'file_path': self.file_path,
            'check_time': self.check_time,
            'categories': [cat.to_dict() for cat in self.categories],
            'extracted_info': self.extracted_info.to_dict(),
            'statistics': {
                'total_items': self.total_items,
                'pass_count': self.pass_count,
                'fail_count': self.fail_count,
                'unknown_count': self.unknown_count
            },
            'model_name': self.model_name,
            'analysis_time': self.analysis_time,
            'total_pages': self.total_pages
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ResponseCheckResult':
        categories = [CheckCategory.from_dict(cat) for cat in data.get('categories', [])]
        extracted_info = ExtractedInfo.from_dict(data.get('extracted_info', {}))
        stats = data.get('statistics', {})

        return cls(
            task_id=data.get('task_id', ''),
            file_name=data.get('file_name', ''),
            file_path=data.get('file_path', ''),
            check_time=data.get('check_time', ''),
            categories=categories,
            extracted_info=extracted_info,
            total_items=stats.get('total_items', 0),
            pass_count=stats.get('pass_count', 0),
            fail_count=stats.get('fail_count', 0),
            unknown_count=stats.get('unknown_count', 0),
            model_name=data.get('model_name', 'deepseek-v3'),
            analysis_time=data.get('analysis_time', 0.0),
            total_pages=data.get('total_pages', 0)
        )

    def calculate_statistics(self):
        """计算统计信息"""
        self.total_items = 0
        self.pass_count = 0
        self.fail_count = 0
        self.unknown_count = 0

        for category in self.categories:
            category.calculate_counts()
            self.total_items += len(category.items)
            self.pass_count += category.pass_count
            self.fail_count += category.fail_count
            self.unknown_count += category.unknown_count

    def get_summary(self) -> str:
        """获取检查总结"""
        parts = [f"共{self.total_items}项"]
        parts.append(f"✅符合 {self.pass_count}项")
        if self.fail_count > 0:
            parts.append(f"❌不符合 {self.fail_count}项")
        if self.unknown_count > 0:
            parts.append(f"⚠️无法判断 {self.unknown_count}项")
        return "，".join(parts)

    def get_failed_items(self) -> List[CheckItem]:
        """获取所有不符合的检查项"""
        failed = []
        for category in self.categories:
            for item in category.items:
                if item.status == "不符合":
                    failed.append(item)
        return failed


@dataclass
class ResponseCheckTask:
    """
    应答自检任务
    """
    task_id: str = ""
    openid: str = ""
    user_id: Optional[int] = None

    # 文件信息
    file_id: str = ""
    file_path: str = ""
    original_filename: str = ""
    file_size: int = 0

    # 任务状态
    status: str = "pending"             # pending/parsing/checking/completed/failed
    progress: int = 0                   # 0-100
    current_step: str = ""              # 当前步骤描述
    current_category: str = ""          # 当前检查类别
    error_message: str = ""

    # 检查结果
    result: Optional[ResponseCheckResult] = None

    # 时间戳
    created_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # AI模型
    model_name: str = "deepseek-v3"

    def to_dict(self) -> Dict[str, Any]:
        return {
            'task_id': self.task_id,
            'openid': self.openid,
            'user_id': self.user_id,
            'file_id': self.file_id,
            'file_path': self.file_path,
            'original_filename': self.original_filename,
            'file_size': self.file_size,
            'status': self.status,
            'progress': self.progress,
            'current_step': self.current_step,
            'current_category': self.current_category,
            'error_message': self.error_message,
            'result': self.result.to_dict() if self.result else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'model_name': self.model_name
        }

    def get_status_text(self) -> str:
        """获取状态文本"""
        status_map = {
            'pending': '等待中',
            'parsing': '正在解析文档',
            'checking': '正在检查',
            'completed': '检查完成',
            'failed': '检查失败'
        }
        return status_map.get(self.status, self.status)
