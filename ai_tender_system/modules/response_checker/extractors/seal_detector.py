#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
公章和签名检测器

检测文档中的公章、骑缝章和手写签名
"""

import re
import json
from typing import Dict, List, Any, Optional
import logging

from .base_extractor import BaseExtractor

logger = logging.getLogger(__name__)


class SealDetector(BaseExtractor):
    """
    公章和签名检测器

    检测内容：
    - 公章是否存在且清晰
    - 骑缝章是否连续
    - 手写签名是否完整
    """

    def __init__(self, llm_client=None):
        super().__init__(llm_client)

    def extract(self, content: Any) -> Dict[str, Any]:
        """
        检测公章和签名

        Args:
            content: 文本内容

        Returns:
            检测结果
        """
        return {
            'has_seal': False,
            'seal_clear': False,
            'has_signature': False,
            'issues': []
        }

    def detect_with_ai(self, text: str, page_count: int = 0) -> Dict[str, Any]:
        """
        使用AI分析文档中的签字盖章情况

        Args:
            text: 文档文本内容
            page_count: 文档页数

        Returns:
            检测结果
        """
        if not self.llm:
            return self._detect_from_text(text)

        prompt = """请分析以下投标文档内容，检查签字盖章情况。

## 文档内容
{text}

## 文档页数
{page_count}页

## 检查要点
1. 公章检查：
   - 文档中是否提到有公章/印章
   - 公章位置是否合理（如：投标函、授权书、报价表等关键页）
   - 是否有缺少公章的提示

2. 骑缝章检查：
   - 文档是否需要骑缝章
   - 是否有骑缝章相关说明

3. 签名检查：
   - 法定代表人签名位置是否应有签名
   - 被授权人签名位置是否应有签名
   - 是否有签名缺失的迹象

## 输出格式（严格JSON）
```json
{{
  "seal_check": {{
    "status": "符合/不符合/无法判断",
    "detail": "检查说明",
    "locations_need_seal": ["需要盖章的位置列表"]
  }},
  "seam_seal_check": {{
    "status": "符合/不符合/无法判断",
    "detail": "检查说明"
  }},
  "signature_check": {{
    "status": "符合/不符合/无法判断",
    "detail": "检查说明",
    "locations_need_signature": ["需要签名的位置列表"]
  }}
}}
```

注意：
- 如果文档内容中能明确判断签字盖章情况，给出明确状态
- 如果无法从文本判断，返回"无法判断"
- 重点关注投标函、授权委托书、报价表等关键文档

请只返回JSON，不要添加其他说明。
""".format(text=text[:15000], page_count=page_count)

        try:
            response = self.llm.call(
                prompt=prompt,
                system_prompt="你是一个专业的投标文件审核专家，擅长检查文档的签字盖章情况。",
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
            logger.warning(f"AI检测签字盖章失败: {e}")
            return self._detect_from_text(text)

    def _detect_from_text(self, text: str) -> Dict[str, Any]:
        """
        从文本分析签字盖章情况

        Args:
            text: 文档文本

        Returns:
            检测结果
        """
        result = {
            'seal_check': {
                'status': '无法判断',
                'detail': '需要人工核对公章',
                'locations_need_seal': []
            },
            'seam_seal_check': {
                'status': '无法判断',
                'detail': '需要人工核对骑缝章'
            },
            'signature_check': {
                'status': '无法判断',
                'detail': '需要人工核对签名',
                'locations_need_signature': []
            }
        }

        # 检查是否有签名/盖章相关关键词
        seal_keywords = ['公章', '印章', '盖章', '加盖']
        signature_keywords = ['签名', '签字', '签章', '手写']

        # 检查需要盖章的位置
        seal_locations = []
        if '投标函' in text:
            seal_locations.append('投标函')
        if '授权委托书' in text or '授权书' in text:
            seal_locations.append('授权委托书')
        if '报价' in text:
            seal_locations.append('报价表')
        if '投标保证金' in text:
            seal_locations.append('投标保证金相关文件')

        if seal_locations:
            result['seal_check']['locations_need_seal'] = seal_locations

        # 检查需要签名的位置
        signature_locations = []
        if '法定代表人' in text or '法人代表' in text:
            signature_locations.append('法定代表人签名处')
        if '被授权人' in text or '授权代表' in text:
            signature_locations.append('被授权人签名处')

        if signature_locations:
            result['signature_check']['locations_need_signature'] = signature_locations

        return result

    def check_seal_requirements(self, text: str) -> List[Dict[str, Any]]:
        """
        检查文档中的盖章要求

        Args:
            text: 文档文本

        Returns:
            盖章要求列表
        """
        requirements = []

        # 检查常见的盖章要求描述
        patterns = [
            (r'(?:须|应|需要?)(?:加盖|盖有).*?(?:公章|印章)', '公章要求'),
            (r'(?:每页|逐页).*?(?:盖章|加盖)', '每页盖章要求'),
            (r'骑缝章', '骑缝章要求'),
            (r'(?:法定代表人|法人).*?(?:签字|签名|签章)', '法人签名要求'),
            (r'(?:授权代表|被授权人).*?(?:签字|签名)', '授权代表签名要求'),
        ]

        for pattern, req_type in patterns:
            matches = re.findall(pattern, text)
            if matches:
                requirements.append({
                    'type': req_type,
                    'matches': matches[:3]  # 最多保留3个匹配
                })

        return requirements
