#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
案例文档智能提取器
从DOC/PDF文档中提取案例信息
"""

import os
import json
import asyncio
from pathlib import Path
from typing import Dict, Optional, Any
from datetime import datetime

import sys
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from common.logger import get_module_logger
from common.llm_client import LLMClient
from modules.document_parser.parser_manager import ParserManager, DocumentType

logger = get_module_logger("case_library.document_extractor")


class CaseDocumentExtractor:
    """案例文档智能提取器"""

    def __init__(self, model_name: str = "gpt-4o-mini"):
        """
        初始化提取器

        Args:
            model_name: 使用的AI模型名称
        """
        self.parser_manager = ParserManager()
        self.llm_client = LLMClient(model_name=model_name)
        self.logger = logger

        self.logger.info(f"案例文档提取器初始化完成，使用模型: {model_name}")

    async def extract_from_file(self, file_path: str) -> Dict[str, Any]:
        """
        从文件提取案例信息

        Args:
            file_path: 文档文件路径

        Returns:
            Dict: 提取的案例信息
        """
        try:
            self.logger.info(f"开始提取案例文档: {file_path}")

            # 1. 解析文档获取文本
            text = await self._parse_document(file_path)

            if not text or len(text.strip()) < 100:
                raise ValueError("文档内容太少，无法提取有效信息")

            self.logger.info(f"文档解析成功，文本长度: {len(text)}")

            # 2. 使用AI提取结构化信息
            case_info = await self._extract_case_info(text)

            self.logger.info(f"案例信息提取成功: {case_info.get('case_title', 'Unknown')}")

            return case_info

        except Exception as e:
            self.logger.error(f"提取案例信息失败: {e}", exc_info=True)
            raise

    async def _parse_document(self, file_path: str) -> str:
        """
        解析文档获取文本内容

        Args:
            file_path: 文档文件路径

        Returns:
            str: 文档文本内容
        """
        try:
            # 判断文件类型
            file_ext = os.path.splitext(file_path)[1].lower()

            if file_ext == '.pdf':
                doc_type = DocumentType.PDF
            elif file_ext in ['.docx', '.doc']:
                doc_type = DocumentType.WORD if file_ext == '.docx' else DocumentType.DOC
            elif file_ext == '.txt':
                doc_type = DocumentType.TXT
            else:
                raise ValueError(f"不支持的文件类型: {file_ext}")

            self.logger.info(f"解析文档类型: {doc_type.value}")

            # 获取对应的解析器
            parser = self.parser_manager._get_parser(doc_type)

            # 解析文档 (await if it's a coroutine)
            content = parser.parse(file_path)
            if asyncio.iscoroutine(content):
                content = await content

            # 如果返回的是字典（包含content字段）
            if isinstance(content, dict):
                text = content.get('content', '')
            # 如果返回的是元组 (text, metadata)
            elif isinstance(content, tuple):
                text = content[0]
            else:
                text = str(content)

            return text

        except Exception as e:
            self.logger.error(f"文档解析失败: {e}", exc_info=True)
            raise

    async def _extract_case_info(self, text: str) -> Dict[str, Any]:
        """
        使用LLM提取案例信息

        Args:
            text: 文档文本内容

        Returns:
            Dict: 提取的案例信息
        """
        try:
            # 调试: 显示文档文本前500字符
            self.logger.debug(f"📄 文档文本长度: {len(text)} 字符")
            self.logger.debug(f"📄 文档文本前500字符: {text[:500]}")

            # 构建提取prompt
            prompt = self._build_extraction_prompt(text)

            # 调用LLM
            self.logger.info("调用AI模型提取案例信息...")
            response = self.llm_client.call(
                prompt=prompt,
                temperature=0.1,  # 低温度保证稳定性
                purpose="案例信息提取"
            )

            # 调试: 显示AI返回的原始响应
            self.logger.debug(f"🤖 AI返回原始响应长度: {len(response)} 字符")
            self.logger.debug(f"🤖 AI返回原始响应(前1000字符): {response[:1000]}")

            # 解析JSON响应
            case_info = self._parse_llm_response(response)

            # 调试: 统计非空字段
            non_null_fields = {k: v for k, v in case_info.items() if v is not None and v != '' and v != 'null'}
            null_fields = [k for k, v in case_info.items() if v is None or v == '' or v == 'null']

            self.logger.info(f"✅ AI成功提取 {len(non_null_fields)}/25 个非空字段")
            if len(non_null_fields) > 0:
                self.logger.debug(f"📊 非空字段列表: {list(non_null_fields.keys())}")
                # 显示关键字段的值
                key_fields = ['case_title', 'customer_name', 'contract_amount', 'industry']
                for field in key_fields:
                    if field in non_null_fields:
                        self.logger.debug(f"  - {field}: {non_null_fields[field]}")

            if len(null_fields) > 0:
                self.logger.warning(f"⚠️  空值字段数量: {len(null_fields)}")
                self.logger.debug(f"⚠️  空值字段列表: {null_fields}")

            return case_info

        except Exception as e:
            self.logger.error(f"AI提取失败: {e}", exc_info=True)
            raise

    def _build_extraction_prompt(self, text: str) -> str:
        """
        构建AI提取Prompt

        Args:
            text: 文档文本

        Returns:
            str: Prompt文本
        """
        # 限制文本长度避免超token
        max_length = 8000
        truncated_text = text[:max_length] if len(text) > max_length else text

        prompt = f"""你是一个专业的案例信息提取助手。请从以下文档中提取案例信息，返回严格的JSON格式。

文档内容：
{truncated_text}

请提取以下字段（如果文档中没有则返回null）：

【基本信息】
- case_title: 案例标题/项目名称
- case_number: 案例编号/项目编号
- customer_name: 客户名称
- industry: 所属行业（从以下选项中选择：政府/教育/医疗/金融/能源/交通/制造业/其他）

【合同信息】
- contract_name: 合同名称
- contract_type: 合同类型（只能是"合同"或"订单"）
- final_customer_name: 最终客户名称（仅订单类型时填写）
- contract_amount: 合同金额（万元，仅返回数字，不要单位）
- contract_start_date: 开始日期（格式：YYYY-MM-DD）
- contract_end_date: 结束日期（格式：YYYY-MM-DD）
- party_a_customer_name: 甲方客户名称
- party_b_company_name: 乙方公司名称

【甲方信息】
- party_a_name: 甲方名称
- party_a_address: 甲方地址
- party_a_contact_name: 联系人姓名
- party_a_contact_phone: 联系电话
- party_a_contact_email: 联系邮箱

【乙方信息】
- party_b_name: 乙方名称
- party_b_address: 乙方地址
- party_b_contact_name: 联系人姓名
- party_b_contact_phone: 联系电话
- party_b_contact_email: 联系邮箱

【其他】
- case_status: 案例状态（从以下选项中选择：success/进行中/待验收）

返回格式示例：
{{
  "case_title": "XX市政府云平台建设项目",
  "case_number": "XM-2024-001",
  "customer_name": "XX市政府",
  "industry": "政府",
  "contract_name": "云平台建设合同",
  "contract_type": "合同",
  "final_customer_name": null,
  "contract_amount": 500.00,
  "contract_start_date": "2024-01-01",
  "contract_end_date": "2024-12-31",
  "party_a_customer_name": "XX市政府",
  "party_b_company_name": "XX科技有限公司",
  "party_a_name": "XX市政府",
  "party_a_address": "XX市XX区XX路123号",
  "party_a_contact_name": "张三",
  "party_a_contact_phone": "010-12345678",
  "party_a_contact_email": "zhangsan@gov.cn",
  "party_b_name": "XX科技有限公司",
  "party_b_address": "XX市XX区XX路456号",
  "party_b_contact_name": "李四",
  "party_b_contact_phone": "010-87654321",
  "party_b_contact_email": "lisi@company.com",
  "case_status": "success"
}}

重要提示：
1. 只返回JSON格式的数据，不要任何其他文字说明
2. 金额只返回数字，不要单位符号（如"万元"、"元"）
3. 日期格式必须是：YYYY-MM-DD
4. 找不到的字段必须返回null（不是空字符串）
5. contract_type只能是"合同"或"订单"
6. industry必须从给定选项中选择
7. case_status必须从给定选项中选择
8. 确保返回的是有效的JSON格式
"""

        return prompt

    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """
        解析LLM返回的JSON响应

        Args:
            response: LLM返回的文本

        Returns:
            Dict: 解析后的案例信息
        """
        try:
            # 去除可能的markdown标记
            cleaned_response = response.strip()
            if cleaned_response.startswith('```json'):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.startswith('```'):
                cleaned_response = cleaned_response[3:]
            if cleaned_response.endswith('```'):
                cleaned_response = cleaned_response[:-3]

            cleaned_response = cleaned_response.strip()

            # 解析JSON
            case_info = json.loads(cleaned_response)

            # 验证和清理数据
            case_info = self._validate_and_clean_data(case_info)

            return case_info

        except json.JSONDecodeError as e:
            self.logger.error(f"JSON解析失败: {e}")
            self.logger.error(f"原始响应: {response}")
            raise ValueError(f"AI返回的数据格式不正确: {e}")

    def _validate_and_clean_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证和清理提取的数据

        Args:
            data: 原始提取数据

        Returns:
            Dict: 清理后的数据
        """
        # 定义所有字段
        all_fields = [
            'case_title', 'case_number', 'customer_name', 'industry',
            'contract_name', 'contract_type', 'final_customer_name',
            'contract_amount', 'contract_start_date', 'contract_end_date',
            'party_a_customer_name', 'party_b_company_name',
            'party_a_name', 'party_a_address', 'party_a_contact_name',
            'party_a_contact_phone', 'party_a_contact_email',
            'party_b_name', 'party_b_address', 'party_b_contact_name',
            'party_b_contact_phone', 'party_b_contact_email',
            'case_status'
        ]

        cleaned_data = {}

        for field in all_fields:
            value = data.get(field)

            # 将 null 保持为 None，空字符串转为 None
            if value is None or value == '' or value == 'null':
                cleaned_data[field] = None
            else:
                cleaned_data[field] = value

        # 特殊处理：合同金额转换为数字
        if cleaned_data.get('contract_amount'):
            try:
                # 移除可能的非数字字符
                amount_str = str(cleaned_data['contract_amount']).replace(',', '').replace('万', '').replace('元', '')
                cleaned_data['contract_amount'] = float(amount_str)
            except (ValueError, TypeError):
                cleaned_data['contract_amount'] = None

        # 特殊处理：日期格式验证
        for date_field in ['contract_start_date', 'contract_end_date']:
            if cleaned_data.get(date_field):
                # 简单验证日期格式 YYYY-MM-DD
                date_str = str(cleaned_data[date_field])
                if len(date_str) == 10 and date_str.count('-') == 2:
                    try:
                        datetime.strptime(date_str, '%Y-%m-%d')
                    except ValueError:
                        self.logger.warning(f"日期格式不正确: {date_field} = {date_str}")
                        cleaned_data[date_field] = None
                else:
                    cleaned_data[date_field] = None

        return cleaned_data


# 测试代码
if __name__ == "__main__":
    import asyncio

    async def test_extractor():
        extractor = CaseDocumentExtractor()

        # 测试文件路径
        test_file = "/path/to/test/case.pdf"

        if os.path.exists(test_file):
            result = await extractor.extract_from_file(test_file)
            print("提取结果:")
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"测试文件不存在: {test_file}")

    asyncio.run(test_extractor())
