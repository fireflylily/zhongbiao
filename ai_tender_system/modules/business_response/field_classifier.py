#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
字段分类器 - 根据字段类型决定处理策略

核心规则：
1. 单位盖章填名称 - 单位/公司字段即使有盖章标记也要填充
2. 个人签字留空白 - 个人字段有签字/盖章标记则不填充

作者：AI Tender System
版本：2.0
日期：2025-10-19
"""


class FieldClassifier:
    """字段分类器 - 根据字段类型决定处理策略

    核心规则：
    1. 单位盖章填名称 - 单位/公司字段即使有盖章标记也要填充
    2. 个人签字留空白 - 个人字段有签字/盖章标记则不填充
    """

    # 单位/公司相关字段（可能出现盖章）
    UNIT_FIELDS = {
        'companyName',      # 供应商名称、公司名称
        'supplierName',     # 供应商
        'vendorName',       # 投标人
        'purchaserName',    # 采购人（可能需要盖章）
    }

    # 个人相关字段（可能出现签字/盖章）
    PERSON_FIELDS = {
        'legalRepresentative',      # 法定代表人
        'representativeName',       # 授权代表人、被授权人
        'authorizedPerson',         # 被授权人
        'representativeTitle',      # 职务（与个人相关）
        'authorizedPersonId',       # 身份证号（与个人相关）
    }

    # 格式标记定义
    SEAL_MARKERS = [
        '（盖章）', '（公章）', '（盖公章）', '(盖章)', '(公章)', '(盖公章)',
        '（盖单位章）', '（盖企业章）', '（加盖公章）', '（加盖单位公章）',  # 新增：单位盖章变体
        '(盖单位章)', '(盖企业章)', '(加盖公章)', '(加盖单位公章)'  # 半角版本
    ]
    SIGNATURE_MARKERS = ['（签字）', '（签名）', '(签字)', '(签名)', '（签章）', '(签章)']
    COMBO_MARKERS = ['（签字或盖章）', '（签字及盖章）', '（签字并盖章）',
                     '(签字或盖章)', '(签字及盖章)', '(签字并盖章)']
    ALL_MARKERS = SEAL_MARKERS + SIGNATURE_MARKERS + COMBO_MARKERS

    @classmethod
    def classify_field(cls, standard_field: str) -> str:
        """分类字段

        Args:
            standard_field: 标准字段名（如 'companyName', 'legalRepresentative'）

        Returns:
            字段类型：'unit' | 'person' | 'general'
        """
        if not standard_field:
            return 'general'

        if standard_field in cls.UNIT_FIELDS:
            return 'unit'
        elif standard_field in cls.PERSON_FIELDS:
            return 'person'
        else:
            return 'general'

    @classmethod
    def should_fill(cls, field_text: str, standard_field: str) -> bool:
        """判断是否应该填充字段

        核心规则：
        - 个人字段 + 签字/盖章标记 = 不填充（留空白供手写）
        - 单位字段 + 任何标记 = 填充（需要填公司名）
        - 其他字段 = 正常填充
        - 未识别字段 + 人员关键词 + 签字标记 = 不填充（如"法定代表人或委托代理人（签字）"）
        - 文档清单项（包含"身份证"、"复印件"等） = 不填充

        Args:
            field_text: 原始字段文本（如 "法定代表人（签字或盖章）"）
            standard_field: 标准字段名（如 'legalRepresentative'）

        Returns:
            是否应该填充
        """
        # ⚠️ 关键修复：即使 std_field 是 None，也要检查签字/文档关键词
        # 这样可以正确处理"法定代表人或委托代理人（签字）"等复合字段

        # 1. 检查是否包含签字/盖章标记
        has_signature_marker = any(marker in field_text for marker in cls.ALL_MARKERS)

        # 2. 检查是否包含人员相关关键词
        person_keywords = ['法定代表人', '法人', '授权代表', '委托代理人', '代理人', '被授权人', '代表']
        has_person_keyword = any(keyword in field_text for keyword in person_keywords)

        # 3. 如果同时包含人员关键词和签字标记，不填充（无论是否识别）
        if has_person_keyword and has_signature_marker:
            return False

        # 4. 检查是否包含文档材料关键词（文档清单项）
        # ⚠️ 修复：精确匹配文档材料，不要过滤"身份证号"等数据字段
        document_keywords = [
            '身份证复印件', '身份证扫描件', '身份证原件',  # 身份证材料（精确）
            '提供身份证', '附身份证',  # 提交材料的表述
            '复印件', '证明', '原件', '扫描件', '附件', '材料清单', '提供材料'
        ]
        # 特殊处理：如果包含"身份证号"或"身份证号码"，不过滤（这是数据字段）
        if '身份证号' in field_text or '身份证号码' in field_text:
            pass  # 不过滤，允许填充
        elif any(keyword in field_text for keyword in document_keywords):
            return False

        # 如果 std_field 是 None（未识别字段），默认不填充（安全策略）
        if not standard_field:
            return False

        field_type = cls.classify_field(standard_field)

        # 个人字段：检查是否有签字/盖章标记
        if field_type == 'person':
            # 任何签字/盖章标记都不填充
            has_marker = any(marker in field_text for marker in cls.ALL_MARKERS)
            return not has_marker  # 有标记则不填充，留空白

        # 单位字段和普通字段都填充
        return True

    @classmethod
    def extract_format_marker(cls, text: str) -> str:
        """提取格式标记

        Args:
            text: 文本（可能包含格式标记）

        Returns:
            找到的格式标记，如 "（盖章）"，没有则返回空字符串
        """
        for marker in cls.ALL_MARKERS:
            if marker in text:
                return marker
        return ""

    @classmethod
    def should_preserve_marker(cls, standard_field: str, marker: str) -> bool:
        """判断是否应该保留格式标记

        规则：
        - 单位字段 + 盖章/公章标记 = 保留（填充后仍需盖章）
        - 其他情况不保留

        Args:
            standard_field: 标准字段名
            marker: 格式标记

        Returns:
            是否保留标记
        """
        field_type = cls.classify_field(standard_field)

        # 单位字段保留盖章/公章标记
        if field_type == 'unit' and marker in cls.SEAL_MARKERS:
            return True

        return False

    @classmethod
    def is_format_marker(cls, text: str) -> bool:
        """判断文本是否只是格式标记

        Args:
            text: 要判断的文本

        Returns:
            是否为纯格式标记
        """
        # 去除空格后检查
        clean_text = text.strip()
        return clean_text in cls.ALL_MARKERS
