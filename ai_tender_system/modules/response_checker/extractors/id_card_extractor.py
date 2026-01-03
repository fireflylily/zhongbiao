#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
身份证信息提取器

从文档图片中识别并提取身份证信息
"""

import re
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

from .base_extractor import BaseExtractor

logger = logging.getLogger(__name__)


class IDCardExtractor(BaseExtractor):
    """
    身份证信息提取器

    支持提取：
    - 姓名
    - 身份证号
    - 有效期
    - 出生日期（从身份证号推算）
    """

    # 身份证号码正则
    ID_PATTERN = re.compile(r'[1-9]\d{5}(?:18|19|20)\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01])\d{3}[\dXx]')

    # 有效期正则
    EXPIRY_PATTERN = re.compile(r'(\d{4})[.\-年](\d{1,2})[.\-月](\d{1,2})日?[-~至](\d{4})[.\-年](\d{1,2})[.\-月](\d{1,2})日?')
    EXPIRY_LONG_PATTERN = re.compile(r'(\d{4})[.\-年](\d{1,2})[.\-月](\d{1,2})日?[-~至]长期')

    def __init__(self, llm_client=None):
        super().__init__(llm_client)

    def extract(self, content: Any) -> Dict[str, Any]:
        """
        从文本内容提取身份证信息

        Args:
            content: 文本内容

        Returns:
            包含法人和被授权人身份证信息的字典
        """
        if not isinstance(content, str):
            return {}

        result = {
            'legal_person': self._extract_person_info(content, 'legal'),
            'authorized_person': self._extract_person_info(content, 'authorized')
        }

        return result

    def extract_from_text(self, text: str) -> Dict[str, Any]:
        """
        从文本提取身份证信息
        """
        result = {}

        # 提取身份证号
        id_numbers = self.ID_PATTERN.findall(text)
        if id_numbers:
            result['id_numbers'] = list(set(id_numbers))

            # 从第一个身份证号推算出生日期
            first_id = id_numbers[0]
            birth_date = self._parse_birth_date(first_id)
            if birth_date:
                result['birth_date'] = birth_date

        # 提取有效期
        expiry_match = self.EXPIRY_PATTERN.search(text)
        if expiry_match:
            expiry_date = f"{expiry_match.group(4)}年{expiry_match.group(5)}月{expiry_match.group(6)}日"
            result['expiry_date'] = expiry_date
        else:
            long_match = self.EXPIRY_LONG_PATTERN.search(text)
            if long_match:
                result['expiry_date'] = "长期"

        return result

    def extract_with_ai(self, text: str, images: List[Dict] = None) -> Dict[str, Any]:
        """
        使用AI提取身份证信息

        Args:
            text: 文档文本
            images: 图片列表

        Returns:
            提取的身份证信息
        """
        if not self.llm:
            return self.extract_from_text(text)

        prompt = """请从以下文档内容中提取身份证相关信息。

## 文档内容
{text}

## 需要提取的信息
1. 法定代表人/法人：
   - 姓名
   - 身份证号
   - 身份证有效期
   - 出生日期

2. 被授权人/委托代理人：
   - 姓名
   - 身份证号
   - 身份证有效期
   - 出生日期

## 输出格式（严格JSON）
```json
{{
  "legal_person": {{
    "name": "姓名",
    "id_number": "身份证号",
    "expiry_date": "有效期截止日期，格式：YYYY年MM月DD日",
    "birth_date": "出生日期，格式：YYYY年MM月DD日"
  }},
  "authorized_person": {{
    "name": "姓名",
    "id_number": "身份证号",
    "expiry_date": "有效期截止日期",
    "birth_date": "出生日期"
  }}
}}
```

如果某项信息未找到，对应字段留空字符串。
请只返回JSON，不要添加其他说明。
""".format(text=text[:10000])

        try:
            response = self.llm.call(
                prompt=prompt,
                system_prompt="你是一个专业的文档信息提取助手，擅长从投标文件中提取身份证信息。",
                temperature=0.1,
                max_tokens=1000
            )

            # 解析JSON响应
            response = response.strip()
            if response.startswith('```'):
                response = re.sub(r'^```json?\s*', '', response)
                response = re.sub(r'\s*```$', '', response)

            return json.loads(response)

        except Exception as e:
            logger.warning(f"AI提取身份证信息失败: {e}")
            return self.extract_from_text(text)

    def _extract_person_info(self, text: str, person_type: str) -> Dict[str, Any]:
        """
        提取指定类型人员的身份信息

        Args:
            text: 文本内容
            person_type: 'legal' 或 'authorized'

        Returns:
            人员身份信息
        """
        info = {
            'name': '',
            'id_number': '',
            'expiry_date': '',
            'birth_date': ''
        }

        # 根据上下文关键词定位
        if person_type == 'legal':
            keywords = ['法定代表人', '法人代表', '法人']
        else:
            keywords = ['被授权人', '授权代表', '委托代理人', '投标代表']

        # 查找相关上下文
        for keyword in keywords:
            if keyword in text:
                # 在关键词附近查找身份证号
                idx = text.find(keyword)
                context = text[max(0, idx - 200):min(len(text), idx + 500)]

                # 提取身份证号
                id_match = self.ID_PATTERN.search(context)
                if id_match:
                    info['id_number'] = id_match.group()
                    info['birth_date'] = self._parse_birth_date(info['id_number'])

                # 提取有效期
                expiry_match = self.EXPIRY_PATTERN.search(context)
                if expiry_match:
                    info['expiry_date'] = f"{expiry_match.group(4)}年{expiry_match.group(5)}月{expiry_match.group(6)}日"
                else:
                    long_match = self.EXPIRY_LONG_PATTERN.search(context)
                    if long_match:
                        info['expiry_date'] = "长期"

                break

        return info

    def _parse_birth_date(self, id_number: str) -> str:
        """
        从身份证号解析出生日期

        Args:
            id_number: 18位身份证号

        Returns:
            出生日期字符串
        """
        if len(id_number) != 18:
            return ''

        try:
            year = id_number[6:10]
            month = id_number[10:12]
            day = id_number[12:14]
            return f"{year}年{month}月{day}日"
        except Exception:
            return ''

    def calculate_age(self, birth_date: str) -> int:
        """
        计算年龄

        Args:
            birth_date: 出生日期（格式：YYYY年MM月DD日）

        Returns:
            年龄
        """
        try:
            # 解析日期
            for fmt in ['%Y年%m月%d日', '%Y-%m-%d', '%Y/%m/%d']:
                try:
                    birth = datetime.strptime(birth_date, fmt)
                    today = datetime.now()
                    age = today.year - birth.year
                    if today.month < birth.month or (today.month == birth.month and today.day < birth.day):
                        age -= 1
                    return age
                except ValueError:
                    continue
            return -1
        except Exception:
            return -1

    def check_expiry(self, expiry_date: str) -> Dict[str, Any]:
        """
        检查身份证是否过期

        Args:
            expiry_date: 有效期截止日期

        Returns:
            检查结果：is_valid, days_left
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
