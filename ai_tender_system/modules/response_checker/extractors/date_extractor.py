#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日期信息提取器

提取文档中的日期信息并检查一致性
"""

import re
from typing import Dict, List, Any, Set
from datetime import datetime
import logging

from .base_extractor import BaseExtractor

logger = logging.getLogger(__name__)


class DateExtractor(BaseExtractor):
    """
    日期信息提取器

    支持提取：
    - 应答日期/投标日期
    - 授权有效期
    - 投标截止日期
    """

    # 日期正则表达式
    DATE_PATTERNS = [
        # YYYY年MM月DD日
        re.compile(r'(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日'),
        # YYYY-MM-DD
        re.compile(r'(\d{4})-(\d{1,2})-(\d{1,2})'),
        # YYYY/MM/DD
        re.compile(r'(\d{4})/(\d{1,2})/(\d{1,2})'),
        # YYYY.MM.DD
        re.compile(r'(\d{4})\.(\d{1,2})\.(\d{1,2})'),
    ]

    # 应答日期上下文关键词
    RESPONSE_DATE_KEYWORDS = [
        '投标日期', '应答日期', '递交日期', '提交日期',
        '本投标文件', '投标人', '日期：', '日期:'
    ]

    # 授权有效期关键词
    AUTH_PERIOD_KEYWORDS = [
        '授权有效期', '委托期限', '授权期限', '有效期'
    ]

    def __init__(self, llm_client=None):
        super().__init__(llm_client)

    def extract(self, content: Any) -> Dict[str, Any]:
        """
        从文本提取日期信息

        Args:
            content: 文本内容

        Returns:
            日期信息字典
        """
        if not isinstance(content, str):
            return {}

        return self.extract_all(content)

    def extract_all(self, text: str) -> Dict[str, Any]:
        """
        提取所有日期信息

        Args:
            text: 文档文本

        Returns:
            日期信息
        """
        result = {
            'response_dates': [],       # 应答日期列表
            'auth_period': '',          # 授权有效期
            'bid_deadline': '',         # 投标截止日期
            'all_dates': []             # 所有识别到的日期
        }

        # 提取所有日期
        all_dates = self._extract_all_dates(text)
        result['all_dates'] = list(all_dates)

        # 提取应答日期
        result['response_dates'] = self._extract_response_dates(text)

        # 提取授权有效期
        result['auth_period'] = self._extract_auth_period(text)

        # 提取投标截止日期
        result['bid_deadline'] = self._extract_bid_deadline(text)

        return result

    def _extract_all_dates(self, text: str) -> Set[str]:
        """
        提取文档中所有日期

        Args:
            text: 文档文本

        Returns:
            日期集合
        """
        dates = set()

        for pattern in self.DATE_PATTERNS:
            matches = pattern.findall(text)
            for match in matches:
                year, month, day = match
                # 标准化日期格式
                try:
                    date_str = f"{year}年{int(month)}月{int(day)}日"
                    # 验证日期有效性
                    datetime(int(year), int(month), int(day))
                    dates.add(date_str)
                except (ValueError, TypeError):
                    continue

        return dates

    def _extract_response_dates(self, text: str) -> List[str]:
        """
        提取应答日期

        Args:
            text: 文档文本

        Returns:
            应答日期列表
        """
        response_dates = []

        for keyword in self.RESPONSE_DATE_KEYWORDS:
            if keyword in text:
                # 在关键词附近查找日期
                idx = text.find(keyword)
                context = text[idx:min(len(text), idx + 200)]

                for pattern in self.DATE_PATTERNS:
                    match = pattern.search(context)
                    if match:
                        year, month, day = match.groups()
                        try:
                            date_str = f"{year}年{int(month)}月{int(day)}日"
                            datetime(int(year), int(month), int(day))
                            if date_str not in response_dates:
                                response_dates.append(date_str)
                        except (ValueError, TypeError):
                            continue
                        break

        return response_dates

    def _extract_auth_period(self, text: str) -> str:
        """
        提取授权有效期

        Args:
            text: 文档文本

        Returns:
            授权有效期
        """
        # 查找授权有效期范围
        auth_range_pattern = re.compile(
            r'(?:授权有效期|委托期限|授权期限)[：:为]?\s*'
            r'(\d{4})[年.\-](\d{1,2})[月.\-](\d{1,2})日?\s*'
            r'[至到\-~]\s*'
            r'(\d{4})[年.\-](\d{1,2})[月.\-](\d{1,2})日?'
        )

        match = auth_range_pattern.search(text)
        if match:
            start = f"{match.group(1)}年{match.group(2)}月{match.group(3)}日"
            end = f"{match.group(4)}年{match.group(5)}月{match.group(6)}日"
            return f"{start}至{end}"

        # 查找"与投标有效期一致"等表述
        if re.search(r'(?:授权|委托).*?(?:与|同).*?(?:投标|有效期).*?一致', text):
            return "与投标有效期一致"

        return ""

    def _extract_bid_deadline(self, text: str) -> str:
        """
        提取投标截止日期

        Args:
            text: 文档文本

        Returns:
            投标截止日期
        """
        deadline_keywords = ['投标截止', '递交截止', '截止时间', '开标时间']

        for keyword in deadline_keywords:
            if keyword in text:
                idx = text.find(keyword)
                context = text[idx:min(len(text), idx + 100)]

                for pattern in self.DATE_PATTERNS:
                    match = pattern.search(context)
                    if match:
                        year, month, day = match.groups()
                        try:
                            date_str = f"{year}年{int(month)}月{int(day)}日"
                            datetime(int(year), int(month), int(day))
                            return date_str
                        except (ValueError, TypeError):
                            continue
                        break

        return ""

    def check_date_consistency(self, dates: List[str]) -> Dict[str, Any]:
        """
        检查日期一致性

        Args:
            dates: 日期列表

        Returns:
            检查结果
        """
        if not dates:
            return {
                'is_consistent': False,
                'message': '未识别到应答日期'
            }

        unique_dates = list(set(dates))

        if len(unique_dates) == 1:
            return {
                'is_consistent': True,
                'message': '应答日期一致',
                'date': unique_dates[0]
            }
        else:
            return {
                'is_consistent': False,
                'message': f'发现{len(unique_dates)}个不同的应答日期',
                'dates': unique_dates
            }

    def check_auth_period_validity(self, auth_period: str, bid_deadline: str) -> Dict[str, Any]:
        """
        检查授权有效期是否覆盖投标日期

        Args:
            auth_period: 授权有效期
            bid_deadline: 投标截止日期

        Returns:
            检查结果
        """
        if not auth_period:
            return {
                'is_valid': False,
                'message': '未识别到授权有效期'
            }

        if auth_period == "与投标有效期一致":
            return {
                'is_valid': True,
                'message': '授权有效期与投标有效期一致'
            }

        if not bid_deadline:
            return {
                'is_valid': True,
                'message': '未识别到投标截止日期，跳过检查'
            }

        # 解析授权有效期
        try:
            # 提取结束日期
            end_match = re.search(r'至(\d{4})年(\d{1,2})月(\d{1,2})日', auth_period)
            if not end_match:
                return {
                    'is_valid': True,
                    'message': '无法解析授权有效期，跳过检查'
                }

            auth_end = datetime(
                int(end_match.group(1)),
                int(end_match.group(2)),
                int(end_match.group(3))
            )

            # 解析投标截止日期
            deadline_match = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', bid_deadline)
            if not deadline_match:
                return {
                    'is_valid': True,
                    'message': '无法解析投标截止日期，跳过检查'
                }

            deadline = datetime(
                int(deadline_match.group(1)),
                int(deadline_match.group(2)),
                int(deadline_match.group(3))
            )

            if auth_end >= deadline:
                return {
                    'is_valid': True,
                    'message': '授权有效期覆盖投标日期',
                    'auth_end': auth_end.strftime('%Y年%m月%d日'),
                    'bid_deadline': deadline.strftime('%Y年%m月%d日')
                }
            else:
                return {
                    'is_valid': False,
                    'message': '授权有效期早于投标截止日期',
                    'auth_end': auth_end.strftime('%Y年%m月%d日'),
                    'bid_deadline': deadline.strftime('%Y年%m月%d日')
                }

        except Exception as e:
            logger.warning(f"检查授权有效期失败: {e}")
            return {
                'is_valid': True,
                'message': '日期解析异常，跳过检查'
            }
