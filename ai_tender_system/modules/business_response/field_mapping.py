#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一字段映射模块 - 为商务应答模块提供统一的字段映射规则
包含字段映射规则、字段变体、数据源优先级等配置

基于代码分析，这是一个AI标书系统的信息填写模块。以下是现有的
  字段映射、填写规则和替换规则的详细展示：

  🗺️ 字段映射 (field_mapping_rules)

  公司信息字段（直接映射）

  - companyName: 公司名称
  - email: 邮箱
  - fax: 传真
  - postalCode: 邮政编码
  - establishDate: 成立时间
  - businessScope: 经营范围
  - legalRepresentative: 法定代表人
  - authorizedPersonName: 被授权人姓名

  公司信息字段（多源映射 - 按优先级顺序）

  - address: ['address', 'registeredAddress', 'officeAddress']
  - phone: ['fixedPhone', 'phone']

  职位字段（智能映射 - 需上下文识别）

  - authorizedPersonPosition: 被授权人职务
  - legalRepresentativePosition: 法定代表人职位

  项目信息字段

  - projectName: 项目名称
  - projectNumber: 项目编号
  - date: 日期
  - purchaserName: 采购人名称

"""

from typing import Dict, Any, List, Optional
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
from common import get_module_logger


class FieldMapping:
    """统一字段映射配置类"""

    def __init__(self):
        self.logger = get_module_logger("field_mapping")

        # ==================== 核心映射规则 ====================

        # 1. 字段映射规则 - 定义字段名与数据源的映射关系（按优先级顺序）
        self.field_mapping_rules = {
            # 公司信息字段 (直接映射)
            'companyName': ['companyName'],
            'email': ['email'],
            'fax': ['fax'],
            'postalCode': ['postalCode'],
            'establishDate': ['establishDate'],
            'businessScope': ['businessScope'],
            'legalRepresentative': ['legalRepresentative'],
            'authorizedPersonName': ['authorizedPersonName'],
            'registeredCapital': ['registeredCapital'],
            'socialCreditCode': ['socialCreditCode'],
            'bankName': ['bankName'],
            'bankAccount': ['bankAccount'],
            'taxNumber': ['taxNumber'],
            'contactPerson': ['contactPerson'],
            'qualification': ['qualification'],

            # 公司信息字段 (多源映射 - 按优先级顺序)
            'address': ['address', 'registeredAddress', 'officeAddress'],
            'phone': ['fixedPhone', 'phone'],
            'registeredAddress': ['registeredAddress', 'address'],

            # 职位字段 (智能映射 - 需要上下文识别)
            'authorizedPersonPosition': ['authorizedPersonPosition'],
            'legalRepresentativePosition': ['legalRepresentativePosition'],

            # 项目信息字段 (直接映射)
            'projectName': ['projectName'],
            'projectNumber': ['projectNumber'],
            'date': ['date'],
            'bidPrice': ['bidPrice'],
            'deliveryTime': ['deliveryTime'],
            'warrantyPeriod': ['warrantyPeriod'],

            # 项目信息字段 (多源映射)
            'purchaserName': ['purchaserName', 'projectOwner']
        }

        # 2. 字段变体 - 文档中可能出现的不同写法
        self.field_variants = {
            'email': ['邮箱', '邮件', '电子邮件', '电子邮箱', 'email', 'Email', 'E-mail', 'E-Mail'],
            'phone': ['电话', '联系电话', '固定电话', '电话号码', '联系方式'],
            'fax': ['传真', '传真号码', '传真号', 'fax', 'Fax'],
            'address': ['地址', '注册地址', '办公地址', '联系地址', '通讯地址', '供应商地址', '公司地址'],
            'registeredAddress': ['注册地址', '工商注册地址', '企业注册地址'],
            'postalCode': ['邮政编码', '邮编', '邮码'],
            'establishDate': ['成立时间', '成立日期', '注册时间', '注册日期', '成立日期'],
            'businessScope': ['经营范围', '业务范围', '经营项目'],
            'legalRepresentative': ['法定代表人', '法人代表', '法人', '法定代表人姓名'],
            'authorizedPersonName': ['供应商代表姓名', '授权代表姓名', '代表姓名', '授权代表', '被授权人姓名', '被授权人'],
            'position': ['职务', '职位', '职称'],
            'registeredCapital': ['注册资本', '注册资金', '注册资本金'],
            'socialCreditCode': ['统一社会信用代码', '社会信用代码', '信用代码', '营业执照号'],
            'contactPerson': ['联系人', '联系人姓名', '项目联系人'],
            'bankName': ['开户银行', '开户行', '银行名称', '基本户开户行'],
            'bankAccount': ['银行账号', '银行账户', '账号', '基本户账号'],
            'taxNumber': ['税号', '纳税人识别号', '税务登记号'],
            'qualification': ['资质等级', '资质', '资质证书'],
            'projectName': ['项目名称', '采购项目名称', '招标项目名称', '项目'],
            'projectNumber': ['项目编号', '采购编号', '招标编号', '项目号', '标号'],
            'bidPrice': ['投标报价', '报价', '投标价格', '投标金额'],
            'deliveryTime': ['交货期', '交货时间', '供货期', '交付时间'],
            'warrantyPeriod': ['质保期', '质保时间', '保修期', '售后服务期'],
            'date': ['日期', '日 期', '日  期', '日   期', '日    期', '日     期']
        }

        # 3. 供应商名称的变体（特殊处理）
        self.company_name_variants = [
            '供应商名称', '供应商全称', '投标人名称', '公司名称',
            '单位名称', '应答人名称', '供应商名称（盖章）',
            '供应商名称（公章）', '公司名称（盖章）', '投标人名称（盖章）',
            '投标人名称（公章）', '单位名称（盖章）', '单位名称（公章）',
            '投标单位', '承包人', '乙方', '乙方名称'
        ]

        # 4. 供应商名称的扩展匹配模式（支持带公章、盖章的变体）
        self.company_name_extended_patterns = [
            r'供应商名称(?:\s*[（(][^）)]*[公盖]章[^）)]*[）)])?',  # 供应商名称（加盖公章）
            r'供应商全称(?:\s*[（(][^）)]*[公盖]章[^）)]*[）)])?',
            r'投标人名称(?:\s*[（(][^）)]*[公盖]章[^）)]*[）)])?',  # 投标人名称（公章）
            r'公司名称(?:\s*[（(][^）)]*[公盖]章[^）)]*[）)])?',
            r'单位名称(?:\s*[（(][^）)]*[公盖]章[^）)]*[）)])?',
            r'应答人名称(?:\s*[（(][^）)]*[公盖]章[^）)]*[）)])?',
        ]

        # 5. 采购人信息字段（使用项目信息填充）
        self.purchaser_variants = [
            '采购人', '采购人名称', '采购单位', '采购方',
            '招标人', '招标人名称', '招标单位', '招标方',
            '甲方', '甲方名称', '业主', '业主单位'
        ]

        # 6. 需要跳过的关键词
        self.skip_keywords = [
            '代理', '招标代理', '采购代理',
            '业主代表', '发包人', '委托人'
        ]

        # 7. 需要跳过的签字相关词
        self.signature_keywords = ['签字', '签名', '签章', '盖章处']

        # 8. 表格专用字段映射（用于table_processor）
        self.table_field_mapping = self._generate_table_field_mapping()

    def _generate_table_field_mapping(self) -> Dict[str, str]:
        """
        生成表格专用的字段映射
        将常用的字段变体映射到标准字段名
        """
        table_mapping = {}

        # 从field_variants生成反向映射（所有变体都映射到字段key）
        for field_key, variants in self.field_variants.items():
            for variant in variants:
                table_mapping[variant] = field_key

        # 添加供应商名称的特殊映射
        for variant in self.company_name_variants:
            table_mapping[variant] = 'companyName'

        # 添加采购人名称映射
        for variant in self.purchaser_variants:
            table_mapping[variant] = 'purchaserName'

        return table_mapping

    def create_unified_mapping(self, company_info: Dict[str, Any],
                               project_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建统一的字段映射表

        Args:
            company_info: 公司信息字典
            project_info: 项目信息字典

        Returns:
            统一的字段映射字典，所有字段都映射到标准化的值
        """
        # 合并原始数据
        raw_data = {**company_info, **project_info}
        unified_mapping = {}

        self.logger.debug(f"🔧 开始创建统一字段映射")
        self.logger.debug(f"🔧 原始数据键: {list(raw_data.keys())}")

        # 遍历所有映射规则
        for target_field, source_fields in self.field_mapping_rules.items():
            value = None

            # 按优先级顺序查找值 (第一个非空值)
            for source_field in source_fields:
                if source_field in raw_data:
                    candidate_value = raw_data[source_field]
                    if candidate_value and str(candidate_value).strip():  # 非空且非空白
                        value = candidate_value
                        self.logger.debug(f"🔧 字段映射: {target_field} ← {source_field} = '{value}'")
                        break

            # 存储映射结果 (即使是None也要存储，避免KeyError)
            unified_mapping[target_field] = value or ''

            if not value:
                self.logger.debug(f"⚠️ 字段映射: {target_field} ← 无有效数据源 (尝试了 {source_fields})")

        # 添加其他未配置映射规则的字段 (直接透传)
        for key, value in raw_data.items():
            if key not in unified_mapping:
                unified_mapping[key] = value
                self.logger.debug(f"🔧 直接映射: {key} = '{value}'")

        self.logger.info(f"🔧 统一字段映射完成: {len(unified_mapping)} 个字段")
        self.logger.debug(f"🔧 映射结果预览: {list(unified_mapping.keys())}")

        return unified_mapping

    def get_field_value(self, field_name: str, data_dict: Dict[str, Any]) -> Optional[str]:
        """
        根据字段名从数据字典中获取值

        Args:
            field_name: 字段名（可以是标准名或变体名）
            data_dict: 数据字典

        Returns:
            字段值，如果找不到返回None
        """
        # 首先尝试直接获取
        if field_name in data_dict:
            return data_dict[field_name]

        # 尝试通过映射规则获取
        if field_name in self.field_mapping_rules:
            for source_field in self.field_mapping_rules[field_name]:
                if source_field in data_dict and data_dict[source_field]:
                    return data_dict[source_field]

        # 尝试通过变体反向查找
        for field_key, variants in self.field_variants.items():
            if field_name in variants and field_key in data_dict:
                return data_dict[field_key]

        return None

    def get_field_variants(self, field_key: str) -> List[str]:
        """
        获取字段的所有变体

        Args:
            field_key: 标准字段名

        Returns:
            字段的所有变体列表
        """
        if field_key == 'companyName':
            return self.company_name_variants
        elif field_key == 'purchaserName':
            return self.purchaser_variants
        else:
            return self.field_variants.get(field_key, [field_key])

    def get_table_mapping(self) -> Dict[str, str]:
        """
        获取表格专用的字段映射

        Returns:
            表格字段映射字典
        """
        return self.table_field_mapping

    def is_skip_field(self, text: str) -> bool:
        """
        检查是否应该跳过该字段

        Args:
            text: 要检查的文本

        Returns:
            True if should skip, False otherwise
        """
        # 检查是否包含需要跳过的关键词
        for keyword in self.skip_keywords:
            if keyword in text and "签字代表" not in text:  # 排除"签字代表"等合法词汇
                return True

        # 检查是否包含签字相关词
        for keyword in self.signature_keywords:
            if keyword in text and "签字代表" not in text and "代表签字" not in text:
                return True

        return False

    def get_all_supported_fields(self) -> Dict[str, List[str]]:
        """
        获取所有支持的字段列表（用于文档或API展示）

        Returns:
            分类的字段列表
        """
        return {
            'company_fields': [
                'companyName', 'address', 'registeredAddress', 'officeAddress',
                'phone', 'fixedPhone', 'email', 'fax', 'postalCode',
                'legalRepresentative', 'authorizedPersonName',
                'socialCreditCode', 'registeredCapital',
                'establishDate', 'bankName', 'bankAccount', 'taxNumber',
                'businessScope', 'contactPerson', 'qualification'
            ],
            'project_fields': [
                'projectName', 'projectNumber', 'date', 'bidPrice',
                'deliveryTime', 'warrantyPeriod', 'purchaserName'
            ],
            'position_fields': [
                'authorizedPersonPosition', 'legalRepresentativePosition'
            ]
        }


# 创建单例实例供其他模块使用
_field_mapping_instance = None

def get_field_mapping() -> FieldMapping:
    """获取字段映射单例实例"""
    global _field_mapping_instance
    if _field_mapping_instance is None:
        _field_mapping_instance = FieldMapping()
    return _field_mapping_instance