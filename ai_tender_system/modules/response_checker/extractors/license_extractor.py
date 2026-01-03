#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
营业执照信息提取器

从文档中识别并提取营业执照信息
"""

import re
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

from .base_extractor import BaseExtractor

logger = logging.getLogger(__name__)


class BusinessLicenseExtractor(BaseExtractor):
    """
    营业执照信息提取器

    支持提取：
    - 公司名称
    - 统一社会信用代码
    - 营业期限/有效期
    - 法定代表人
    """

    # 统一社会信用代码正则（18位）
    CREDIT_CODE_PATTERN = re.compile(r'[0-9A-HJ-NPQRTUWXY]{2}\d{6}[0-9A-HJ-NPQRTUWXY]{10}')

    # 公司名称正则
    COMPANY_PATTERN = re.compile(r'([\u4e00-\u9fa5]{2,}(?:有限公司|股份有限公司|有限责任公司|集团|公司))')

    # 有效期正则
    LICENSE_EXPIRY_PATTERN = re.compile(
        r'(?:营业期限|经营期限|有效期)[：:]\s*(\d{4})[年.\-](\d{1,2})[月.\-](\d{1,2})日?[至到\-~](\d{4})[年.\-](\d{1,2})[月.\-](\d{1,2})日?'
    )
    LICENSE_LONG_PATTERN = re.compile(
        r'(?:营业期限|经营期限|有效期)[：:]\s*(\d{4})[年.\-](\d{1,2})[月.\-](\d{1,2})日?[至到\-~](?:长期|永久|无固定期限)'
    )

    def __init__(self, llm_client=None):
        super().__init__(llm_client)

    def extract(self, content: Any) -> Dict[str, Any]:
        """
        从文本内容提取营业执照信息

        Args:
            content: 文本内容或图片列表

        Returns:
            营业执照信息字典
        """
        if isinstance(content, str):
            return self.extract_from_text(content)
        elif isinstance(content, list):
            # 图片列表，需要OCR处理
            return {}
        return {}

    def extract_from_text(self, text: str) -> Dict[str, Any]:
        """
        从文本提取营业执照信息
        """
        result = {
            'company_name': '',
            'credit_code': '',
            'expiry_date': '',
            'legal_person': ''
        }

        # 提取统一社会信用代码
        credit_codes = self.CREDIT_CODE_PATTERN.findall(text)
        if credit_codes:
            result['credit_code'] = credit_codes[0]

        # 提取公司名称
        companies = self.COMPANY_PATTERN.findall(text)
        if companies:
            # 优先选择最长的公司名称
            result['company_name'] = max(companies, key=len)

        # 提取有效期
        expiry_match = self.LICENSE_EXPIRY_PATTERN.search(text)
        if expiry_match:
            result['expiry_date'] = f"{expiry_match.group(4)}年{expiry_match.group(5)}月{expiry_match.group(6)}日"
        else:
            long_match = self.LICENSE_LONG_PATTERN.search(text)
            if long_match:
                result['expiry_date'] = "长期"

        return result

    def extract_with_ai(self, text: str) -> Dict[str, Any]:
        """
        使用AI提取营业执照信息

        Args:
            text: 文档文本

        Returns:
            营业执照信息
        """
        if not self.llm:
            return self.extract_from_text(text)

        prompt = """请从以下文档内容中提取营业执照相关信息。

## 文档内容
{text}

## 需要提取的信息
1. 公司名称（完整全称）
2. 统一社会信用代码（18位）
3. 营业期限/有效期截止日期
4. 法定代表人姓名

## 输出格式（严格JSON）
```json
{{
  "company_name": "公司全称",
  "credit_code": "统一社会信用代码",
  "expiry_date": "有效期截止日期，格式：YYYY年MM月DD日，或'长期'",
  "legal_person": "法定代表人姓名"
}}
```

如果某项信息未找到，对应字段留空字符串。
请只返回JSON，不要添加其他说明。
""".format(text=text[:10000])

        try:
            response = self.llm.call(
                prompt=prompt,
                system_prompt="你是一个专业的文档信息提取助手，擅长从投标文件中提取营业执照信息。",
                temperature=0.1,
                max_tokens=500
            )

            # 解析JSON响应
            response = response.strip()
            if response.startswith('```'):
                response = re.sub(r'^```json?\s*', '', response)
                response = re.sub(r'\s*```$', '', response)

            return json.loads(response)

        except Exception as e:
            logger.warning(f"AI提取营业执照信息失败: {e}")
            return self.extract_from_text(text)

    def check_expiry(self, expiry_date: str) -> Dict[str, Any]:
        """
        检查营业执照是否过期

        Args:
            expiry_date: 有效期截止日期

        Returns:
            检查结果
        """
        if not expiry_date or expiry_date == "长期":
            return {'is_valid': True, 'days_left': 9999}

        try:
            for fmt in ['%Y年%m月%d日', '%Y-%m-%d', '%Y/%m/%d', '%Y.%m.%d']:
                try:
                    expiry = datetime.strptime(expiry_date, fmt)
                    days_left = (expiry - datetime.now()).days
                    return {
                        'is_valid': days_left >= 0,
                        'days_left': max(0, days_left)
                    }
                except ValueError:
                    continue
            return {'is_valid': True, 'days_left': 9999}
        except Exception:
            return {'is_valid': True, 'days_left': 9999}

    def check_company_name_consistency(self, license_name: str, doc_names: List[str]) -> Dict[str, Any]:
        """
        检查公司名称一致性

        Args:
            license_name: 营业执照上的公司名称
            doc_names: 文档中出现的公司名称列表

        Returns:
            一致性检查结果
        """
        if not license_name:
            return {'is_consistent': False, 'message': '未识别到营业执照公司名称'}

        # 规范化名称
        license_name_normalized = license_name.strip().replace(' ', '')

        for doc_name in doc_names:
            doc_name_normalized = doc_name.strip().replace(' ', '')
            if license_name_normalized == doc_name_normalized:
                return {'is_consistent': True, 'message': '公司名称一致'}

        return {
            'is_consistent': False,
            'message': f'公司名称不一致：营业执照为"{license_name}"',
            'license_name': license_name,
            'doc_names': doc_names
        }

    def check_credit_code_consistency(self, license_code: str, doc_codes: List[str]) -> Dict[str, Any]:
        """
        检查统一社会信用代码一致性

        Args:
            license_code: 营业执照上的信用代码
            doc_codes: 文档中出现的信用代码列表

        Returns:
            一致性检查结果
        """
        if not license_code:
            return {'is_consistent': False, 'message': '未识别到营业执照信用代码'}

        license_code = license_code.strip().upper()

        for doc_code in doc_codes:
            doc_code = doc_code.strip().upper()
            if license_code == doc_code:
                return {'is_consistent': True, 'message': '统一社会信用代码一致'}

        return {
            'is_consistent': False,
            'message': f'统一社会信用代码不一致：营业执照为"{license_code}"',
            'license_code': license_code,
            'doc_codes': doc_codes
        }
