#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
报价信息提取器

提取文档中的报价相关信息
"""

import re
import json
from typing import Dict, List, Any, Optional, Tuple
from decimal import Decimal, InvalidOperation
import logging

from .base_extractor import BaseExtractor

logger = logging.getLogger(__name__)


class PriceExtractor(BaseExtractor):
    """
    报价信息提取器

    支持提取：
    - 大写金额
    - 小写金额
    - 单价明细
    - 最高限价
    """

    # 大写金额正则
    UPPER_PRICE_PATTERN = re.compile(
        r'[人民币￥¥]?\s*([零壹贰叁肆伍陆柒捌玖拾佰仟万亿]+元[零壹贰叁肆伍陆柒捌玖角分整]*)'
    )

    # 小写金额正则
    LOWER_PRICE_PATTERN = re.compile(
        r'[￥¥]?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?)\s*(?:元|万元)?'
    )

    # 最高限价正则
    MAX_LIMIT_PATTERN = re.compile(
        r'(?:最高限价|控制价|预算金额|预算价)[：:为]?\s*[￥¥]?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?)\s*(?:元|万元)?'
    )

    # 中文数字映射
    CHINESE_NUM_MAP = {
        '零': 0, '壹': 1, '贰': 2, '叁': 3, '肆': 4,
        '伍': 5, '陆': 6, '柒': 7, '捌': 8, '玖': 9
    }

    CHINESE_UNIT_MAP = {
        '拾': 10, '佰': 100, '仟': 1000, '万': 10000, '亿': 100000000
    }

    def __init__(self, llm_client=None):
        super().__init__(llm_client)

    def extract(self, content: Any) -> Dict[str, Any]:
        """
        从文本提取报价信息

        Args:
            content: 文本内容

        Returns:
            报价信息字典
        """
        if not isinstance(content, str):
            return {}

        return self.extract_from_text(content)

    def extract_from_text(self, text: str) -> Dict[str, Any]:
        """
        从文本提取报价信息
        """
        result = {
            'total_upper': '',      # 大写金额
            'total_lower': 0.0,     # 小写金额
            'unit_prices': [],      # 单价明细
            'max_limit': 0.0        # 最高限价
        }

        # 提取大写金额
        upper_matches = self.UPPER_PRICE_PATTERN.findall(text)
        if upper_matches:
            # 选择最长的大写金额（通常是总价）
            result['total_upper'] = max(upper_matches, key=len)

        # 提取小写金额
        lower_matches = self.LOWER_PRICE_PATTERN.findall(text)
        if lower_matches:
            # 转换为数值并选择最大的（通常是总价）
            amounts = []
            for match in lower_matches:
                try:
                    value = float(match.replace(',', ''))
                    if '万元' in text[text.find(match):text.find(match) + len(match) + 5]:
                        value *= 10000
                    amounts.append(value)
                except ValueError:
                    continue
            if amounts:
                result['total_lower'] = max(amounts)

        # 提取最高限价
        max_match = self.MAX_LIMIT_PATTERN.search(text)
        if max_match:
            try:
                value = float(max_match.group(1).replace(',', ''))
                # 检查是否是万元
                context = text[max_match.start():max_match.end() + 10]
                if '万元' in context or '万' in context:
                    value *= 10000
                result['max_limit'] = value
            except ValueError:
                pass

        return result

    def extract_with_ai(self, text: str) -> Dict[str, Any]:
        """
        使用AI提取报价信息

        Args:
            text: 文档文本

        Returns:
            报价信息
        """
        if not self.llm:
            return self.extract_from_text(text)

        prompt = """请从以下投标文档内容中提取报价相关信息。

## 文档内容
{text}

## 需要提取的信息
1. 投标总价（大写）
2. 投标总价（小写，转换为数字）
3. 最高限价/控制价（如有）
4. 报价明细表中的单价信息（如有）

## 输出格式（严格JSON）
```json
{{
  "total_upper": "大写金额，如：壹佰贰拾叁万肆仟伍佰陆拾元整",
  "total_lower": 1234560.00,
  "max_limit": 1500000.00,
  "unit_prices": [
    {{"item": "项目名称", "unit_price": 100.00, "quantity": 10, "subtotal": 1000.00}}
  ]
}}
```

注意：
- 金额统一使用元为单位（如果原文是万元，请转换）
- 如果某项信息未找到，对应字段使用空字符串或0
- unit_prices如果无法提取，返回空数组

请只返回JSON，不要添加其他说明。
""".format(text=text[:15000])

        try:
            response = self.llm.call(
                prompt=prompt,
                system_prompt="你是一个专业的投标报价分析专家，擅长从投标文件中提取报价信息。",
                temperature=0.1,
                max_tokens=1500
            )

            # 解析JSON响应
            response = response.strip()
            if response.startswith('```'):
                response = re.sub(r'^```json?\s*', '', response)
                response = re.sub(r'\s*```$', '', response)

            return json.loads(response)

        except Exception as e:
            logger.warning(f"AI提取报价信息失败: {e}")
            return self.extract_from_text(text)

    def parse_chinese_number(self, chinese: str) -> float:
        """
        将中文大写金额转换为数字

        Args:
            chinese: 中文大写金额

        Returns:
            数值金额
        """
        if not chinese:
            return 0.0

        try:
            # 移除"人民币"、"元"、"整"等字符
            chinese = chinese.replace('人民币', '').replace('元', '').replace('整', '')
            chinese = chinese.replace('角', '').replace('分', '')

            result = 0
            temp = 0
            billion = 0

            for char in chinese:
                if char in self.CHINESE_NUM_MAP:
                    temp = self.CHINESE_NUM_MAP[char]
                elif char in self.CHINESE_UNIT_MAP:
                    unit = self.CHINESE_UNIT_MAP[char]
                    if unit == 100000000:  # 亿
                        result = (result + temp) * unit
                        billion = result
                        result = 0
                        temp = 0
                    elif unit == 10000:  # 万
                        result = (result + temp) * unit
                        temp = 0
                    else:
                        result += temp * unit
                        temp = 0

            result += temp + billion
            return float(result)

        except Exception as e:
            logger.warning(f"解析中文金额失败: {chinese}, 错误: {e}")
            return 0.0

    def check_amount_consistency(self, upper: str, lower: float) -> Dict[str, Any]:
        """
        检查大小写金额一致性

        Args:
            upper: 大写金额
            lower: 小写金额

        Returns:
            检查结果
        """
        if not upper and lower == 0:
            return {
                'is_consistent': False,
                'message': '未识别到报价金额'
            }

        if not upper:
            return {
                'is_consistent': False,
                'message': '未识别到大写金额'
            }

        if lower == 0:
            return {
                'is_consistent': False,
                'message': '未识别到小写金额'
            }

        # 解析大写金额
        upper_value = self.parse_chinese_number(upper)

        if upper_value == 0:
            return {
                'is_consistent': False,
                'message': f'无法解析大写金额：{upper}'
            }

        # 比较（允许1元的误差）
        if abs(upper_value - lower) < 1:
            return {
                'is_consistent': True,
                'message': '大小写金额一致',
                'upper_value': upper_value,
                'lower_value': lower
            }
        else:
            return {
                'is_consistent': False,
                'message': f'大小写金额不一致',
                'upper': upper,
                'upper_value': upper_value,
                'lower_value': lower,
                'difference': abs(upper_value - lower)
            }

    def check_calculation(self, unit_prices: List[Dict], total: float) -> Dict[str, Any]:
        """
        检查单价计算是否正确

        Args:
            unit_prices: 单价明细列表
            total: 报价总价

        Returns:
            检查结果
        """
        if not unit_prices:
            return {
                'is_correct': True,
                'message': '无单价明细，跳过计算检查',
                'calculated_total': 0,
                'stated_total': total
            }

        calculated_total = 0
        for item in unit_prices:
            unit_price = item.get('unit_price', 0)
            quantity = item.get('quantity', 0)
            subtotal = item.get('subtotal', 0)

            # 检查小计是否正确
            expected_subtotal = unit_price * quantity
            if abs(expected_subtotal - subtotal) > 0.01:
                return {
                    'is_correct': False,
                    'message': f'项目"{item.get("item", "")}"的小计计算错误',
                    'expected': expected_subtotal,
                    'actual': subtotal
                }

            calculated_total += subtotal

        # 比较总价（允许1元误差）
        if abs(calculated_total - total) < 1:
            return {
                'is_correct': True,
                'message': '单价计算正确',
                'calculated_total': calculated_total,
                'stated_total': total
            }
        else:
            return {
                'is_correct': False,
                'message': '单价合计与总价不符',
                'calculated_total': calculated_total,
                'stated_total': total,
                'difference': abs(calculated_total - total)
            }

    def check_max_limit(self, total: float, max_limit: float) -> Dict[str, Any]:
        """
        检查报价是否超过最高限价

        Args:
            total: 投标总价
            max_limit: 最高限价

        Returns:
            检查结果
        """
        if max_limit == 0:
            return {
                'is_within_limit': True,
                'message': '未识别到最高限价，跳过检查'
            }

        if total == 0:
            return {
                'is_within_limit': False,
                'message': '未识别到投标报价'
            }

        if total <= max_limit:
            return {
                'is_within_limit': True,
                'message': '报价未超过最高限价',
                'total': total,
                'max_limit': max_limit,
                'remaining': max_limit - total
            }
        else:
            return {
                'is_within_limit': False,
                'message': '报价超过最高限价',
                'total': total,
                'max_limit': max_limit,
                'excess': total - max_limit
            }
