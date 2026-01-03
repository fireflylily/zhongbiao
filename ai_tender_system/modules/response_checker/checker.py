#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
应答文件自检查器 - 核心检查引擎

实现28项清单式检查：
1. 完整性检查（3项）
2. 签字盖章检查（3项）
3. 页码检查（2项）
4. 索引表检查（2项）
5. 法人身份证检查（3项）
6. 被授权人身份证检查（3项）
7. 营业执照检查（3项）
8. 应答日期检查（2项）
9. 报价检查（3项）
10. 业绩检查（4项）
"""

import time
import uuid
import json
import re
from typing import List, Dict, Optional, Callable, Tuple, Any
from pathlib import Path
from datetime import datetime
import logging

from .schemas import (
    ResponseCheckResult, CheckCategory, CheckItem,
    ExtractedInfo, CheckCategoryType, CATEGORY_NAMES, CHECK_ITEMS_DEFINITION
)
from .prompt_manager import ResponseCheckPromptManager, PromptType
from .extractors import (
    IDCardExtractor, BusinessLicenseExtractor,
    SealDetector, PriceExtractor, DateExtractor
)

logger = logging.getLogger(__name__)


class ResponseChecker:
    """
    应答文件自检查器

    采用清单式检查，每条检查项标记"符合/不符合"状态
    """

    def __init__(self, model_name: str = 'deepseek-v3'):
        """
        初始化检查器

        Args:
            model_name: AI模型名称
        """
        self.model_name = model_name
        self.llm = None
        self.parser = None
        self.prompt_manager = ResponseCheckPromptManager()

        # 初始化各类提取器
        self.id_extractor = IDCardExtractor()
        self.license_extractor = BusinessLicenseExtractor()
        self.seal_detector = SealDetector()
        self.price_extractor = PriceExtractor()
        self.date_extractor = DateExtractor()

        logger.info(f"应答自检查器初始化完成，模型: {model_name}")

    def _init_llm(self):
        """延迟初始化LLM客户端"""
        if self.llm is None:
            try:
                from common.llm_client import LLMClient
                self.llm = LLMClient(self.model_name)
                # 为提取器设置LLM
                self.id_extractor.llm = self.llm
                self.license_extractor.llm = self.llm
                self.seal_detector.llm = self.llm
                self.price_extractor.llm = self.llm
            except Exception as e:
                logger.warning(f"LLM客户端初始化失败: {e}")

    def _init_parser(self):
        """延迟初始化文档解析器"""
        if self.parser is None:
            try:
                from modules.document_parser.parser_manager import ParserManager
                self.parser = ParserManager()
            except Exception as e:
                logger.warning(f"文档解析器初始化失败: {e}")

    def check(self,
              file_path: str,
              progress_callback: Optional[Callable[[int, str], None]] = None,
              category_callback: Optional[Callable[[CheckCategory], None]] = None
              ) -> ResponseCheckResult:
        """
        执行应答文件自检查

        Args:
            file_path: 应答文件路径
            progress_callback: 进度回调 (progress: int, message: str)
            category_callback: 类别完成回调 (category: CheckCategory)

        Returns:
            ResponseCheckResult: 检查结果
        """
        start_time = time.time()

        result = ResponseCheckResult(
            task_id=str(uuid.uuid4()),
            file_path=file_path,
            file_name=Path(file_path).name,
            check_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            model_name=self.model_name
        )

        try:
            # 初始化组件
            self._init_llm()
            self._init_parser()

            # ========== Stage 1: 文档解析 ==========
            if progress_callback:
                progress_callback(5, "正在解析文档...")

            text, total_pages = self._parse_document(file_path)
            result.total_pages = total_pages

            logger.info(f"文档解析完成: {len(text)}字符, {total_pages}页")

            # ========== Stage 2: 信息提取 ==========
            if progress_callback:
                progress_callback(10, "正在提取关键信息...")

            result.extracted_info = self._extract_info(text)
            logger.info("关键信息提取完成")

            # ========== Stage 3: 分类检查 ==========
            check_configs = [
                (CheckCategoryType.COMPLETENESS, 15, self._check_completeness),
                (CheckCategoryType.SIGNATURE_SEAL, 23, self._check_signature_seal),
                (CheckCategoryType.PAGE_NUMBER, 31, self._check_page_number),
                (CheckCategoryType.INDEX_TABLE, 39, self._check_index_table),
                (CheckCategoryType.LEGAL_PERSON_ID, 47, self._check_legal_person_id),
                (CheckCategoryType.AUTHORIZED_ID, 55, self._check_authorized_id),
                (CheckCategoryType.BUSINESS_LICENSE, 63, self._check_business_license),
                (CheckCategoryType.RESPONSE_DATE, 71, self._check_response_date),
                (CheckCategoryType.PRICE_CHECK, 79, self._check_price),
                (CheckCategoryType.PERFORMANCE, 87, self._check_performance),
            ]

            for category_type, progress, check_func in check_configs:
                category_name = CATEGORY_NAMES[category_type]

                if progress_callback:
                    progress_callback(progress, f"正在进行{category_name}...")

                try:
                    category = check_func(text, result.extracted_info, total_pages)
                    category.calculate_counts()
                    result.categories.append(category)

                    # 类别完成回调
                    if category_callback:
                        category_callback(category)

                    logger.debug(f"{category_name}完成: 通过{category.pass_count}项, 不通过{category.fail_count}项")

                except Exception as e:
                    logger.warning(f"{category_name}失败: {e}")
                    # 创建默认类别结果
                    category = self._create_default_category(category_type)
                    result.categories.append(category)

            # ========== Stage 4: 结果汇总 ==========
            if progress_callback:
                progress_callback(95, "正在生成检查报告...")

            result.calculate_statistics()
            result.analysis_time = time.time() - start_time

            if progress_callback:
                progress_callback(100, "检查完成")

            logger.info(f"应答自检查完成: 共{result.total_items}项, "
                       f"符合{result.pass_count}项, 不符合{result.fail_count}项, "
                       f"耗时{result.analysis_time:.2f}s")

            return result

        except Exception as e:
            logger.error(f"应答自检查失败: {e}")
            raise

    def _parse_document(self, file_path: str) -> Tuple[str, int]:
        """
        解析文档

        Returns:
            (文本内容, 总页数)
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {path}")

        # 使用解析器解析文档
        if self.parser:
            text = self.parser.parse_document_simple(str(path))
        else:
            # 备用方案：直接读取文本
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()

        # 估算页数
        total_pages = max(1, len(text) // 1500)

        return text, total_pages

    def _extract_info(self, text: str) -> ExtractedInfo:
        """
        提取关键信息
        """
        info = ExtractedInfo()

        # 1. 提取身份证信息
        if self.llm:
            id_results = self.id_extractor.extract_with_ai(text)
        else:
            id_results = self.id_extractor.extract(text)

        if id_results.get('legal_person'):
            lp = id_results['legal_person']
            info.legal_person_name = lp.get('name', '')
            info.legal_person_id_number = lp.get('id_number', '')
            info.legal_person_id_expiry = lp.get('expiry_date', '')
            info.legal_person_birth_date = lp.get('birth_date', '')

        if id_results.get('authorized_person'):
            ap = id_results['authorized_person']
            info.authorized_person_name = ap.get('name', '')
            info.authorized_person_id_number = ap.get('id_number', '')
            info.authorized_person_id_expiry = ap.get('expiry_date', '')
            info.authorized_person_birth_date = ap.get('birth_date', '')

        # 2. 提取营业执照信息
        if self.llm:
            license_info = self.license_extractor.extract_with_ai(text)
        else:
            license_info = self.license_extractor.extract_from_text(text)

        if license_info:
            info.company_name = license_info.get('company_name', '')
            info.unified_credit_code = license_info.get('credit_code', '')
            info.license_expiry = license_info.get('expiry_date', '')
            info.license_company_name = license_info.get('company_name', '')
            info.license_credit_code = license_info.get('credit_code', '')

        # 3. 提取报价信息
        if self.llm:
            price_info = self.price_extractor.extract_with_ai(text)
        else:
            price_info = self.price_extractor.extract_from_text(text)

        if price_info:
            info.total_price_upper = price_info.get('total_upper', '')
            info.total_price_lower = price_info.get('total_lower', 0.0)
            info.unit_prices = price_info.get('unit_prices', [])
            info.max_limit_price = price_info.get('max_limit', 0.0)

        # 4. 提取日期信息
        date_info = self.date_extractor.extract_all(text)
        info.response_dates = date_info.get('response_dates', [])
        info.authorization_valid_period = date_info.get('auth_period', '')
        info.bid_deadline = date_info.get('bid_deadline', '')

        return info

    # ========== 各类别检查方法 ==========

    def _check_completeness(self, text: str, info: ExtractedInfo, page_count: int) -> CheckCategory:
        """完整性检查"""
        category = CheckCategory(
            category_id=CheckCategoryType.COMPLETENESS.value,
            category_name=CATEGORY_NAMES[CheckCategoryType.COMPLETENESS]
        )

        # 使用AI检查
        items = self._ai_check(
            PromptType.COMPLETENESS,
            CheckCategoryType.COMPLETENESS,
            document_content=text[:15000]
        )

        category.items = items
        return category

    def _check_signature_seal(self, text: str, info: ExtractedInfo, page_count: int) -> CheckCategory:
        """签字盖章检查"""
        category = CheckCategory(
            category_id=CheckCategoryType.SIGNATURE_SEAL.value,
            category_name=CATEGORY_NAMES[CheckCategoryType.SIGNATURE_SEAL]
        )

        # 使用AI检查
        items = self._ai_check(
            PromptType.SEAL,
            CheckCategoryType.SIGNATURE_SEAL,
            document_content=text[:15000],
            page_count=page_count
        )

        category.items = items
        return category

    def _check_page_number(self, text: str, info: ExtractedInfo, page_count: int) -> CheckCategory:
        """页码检查"""
        category = CheckCategory(
            category_id=CheckCategoryType.PAGE_NUMBER.value,
            category_name=CATEGORY_NAMES[CheckCategoryType.PAGE_NUMBER]
        )

        # 使用AI检查
        items = self._ai_check(
            PromptType.PAGE,
            CheckCategoryType.PAGE_NUMBER,
            document_content=text[:10000]
        )

        category.items = items
        return category

    def _check_index_table(self, text: str, info: ExtractedInfo, page_count: int) -> CheckCategory:
        """索引表检查"""
        category = CheckCategory(
            category_id=CheckCategoryType.INDEX_TABLE.value,
            category_name=CATEGORY_NAMES[CheckCategoryType.INDEX_TABLE]
        )

        # 使用AI检查
        items = self._ai_check(
            PromptType.INDEX,
            CheckCategoryType.INDEX_TABLE,
            document_content=text[:15000]
        )

        category.items = items
        return category

    def _check_legal_person_id(self, text: str, info: ExtractedInfo, page_count: int) -> CheckCategory:
        """法人身份证检查"""
        category = CheckCategory(
            category_id=CheckCategoryType.LEGAL_PERSON_ID.value,
            category_name=CATEGORY_NAMES[CheckCategoryType.LEGAL_PERSON_ID]
        )

        items = []
        definitions = CHECK_ITEMS_DEFINITION[CheckCategoryType.LEGAL_PERSON_ID]

        # 1. 身份证在有效期内
        item1 = CheckItem(
            item_id=definitions[0]['id'],
            category=category.category_name,
            name=definitions[0]['name']
        )

        if info.legal_person_id_expiry:
            expiry_check = self.id_extractor.check_expiry(info.legal_person_id_expiry)
            if expiry_check['is_valid']:
                if expiry_check['days_left'] < 30:
                    item1.status = "符合"
                    item1.detail = f"身份证有效，剩余{expiry_check['days_left']}天，建议及时更新"
                else:
                    item1.status = "符合"
                    item1.detail = f"身份证有效期至{info.legal_person_id_expiry}"
            else:
                item1.status = "不符合"
                item1.detail = f"身份证已过期：{info.legal_person_id_expiry}"
                item1.suggestion = "请更换有效期内的法人身份证"
        else:
            item1.status = "无法判断"
            item1.detail = "未识别到法人身份证有效期信息"
            item1.suggestion = "请确保法人身份证清晰可读"

        items.append(item1)

        # 2. 姓名与文档中一致
        item2 = CheckItem(
            item_id=definitions[1]['id'],
            category=category.category_name,
            name=definitions[1]['name']
        )

        if info.legal_person_name:
            # 检查姓名在文档中出现次数
            count = text.count(info.legal_person_name)
            if count >= 2:
                item2.status = "符合"
                item2.detail = f"法人姓名'{info.legal_person_name}'在文档中出现{count}次"
            else:
                item2.status = "无法判断"
                item2.detail = f"法人姓名'{info.legal_person_name}'在文档中仅出现{count}次"
                item2.suggestion = "请核对文档中法人姓名是否一致"
        else:
            item2.status = "无法判断"
            item2.detail = "未识别到法人姓名"

        items.append(item2)

        # 3. 年龄合理
        item3 = CheckItem(
            item_id=definitions[2]['id'],
            category=category.category_name,
            name=definitions[2]['name']
        )

        if info.legal_person_birth_date:
            age = self.id_extractor.calculate_age(info.legal_person_birth_date)
            if 18 <= age <= 80:
                item3.status = "符合"
                item3.detail = f"法人年龄{age}岁，在合理范围内"
            else:
                item3.status = "不符合"
                item3.detail = f"法人年龄{age}岁，不在18-80岁合理范围内"
                item3.suggestion = "请核对法人身份证信息"
        else:
            item3.status = "无法判断"
            item3.detail = "未识别到法人出生日期"

        items.append(item3)

        category.items = items
        return category

    def _check_authorized_id(self, text: str, info: ExtractedInfo, page_count: int) -> CheckCategory:
        """被授权人身份证检查"""
        category = CheckCategory(
            category_id=CheckCategoryType.AUTHORIZED_ID.value,
            category_name=CATEGORY_NAMES[CheckCategoryType.AUTHORIZED_ID]
        )

        items = []
        definitions = CHECK_ITEMS_DEFINITION[CheckCategoryType.AUTHORIZED_ID]

        # 检查是否有被授权人
        has_authorization = '授权' in text or '委托' in text

        # 1. 身份证在有效期内
        item1 = CheckItem(
            item_id=definitions[0]['id'],
            category=category.category_name,
            name=definitions[0]['name']
        )

        if info.authorized_person_id_expiry:
            expiry_check = self.id_extractor.check_expiry(info.authorized_person_id_expiry)
            if expiry_check['is_valid']:
                item1.status = "符合"
                item1.detail = f"身份证有效期至{info.authorized_person_id_expiry}"
            else:
                item1.status = "不符合"
                item1.detail = f"身份证已过期：{info.authorized_person_id_expiry}"
                item1.suggestion = "请更换有效期内的被授权人身份证"
        elif has_authorization:
            item1.status = "无法判断"
            item1.detail = "有授权委托书但未识别到被授权人身份证有效期"
            item1.suggestion = "请确保被授权人身份证清晰可读"
        else:
            item1.status = "符合"
            item1.detail = "无授权委托，法人亲自投标"

        items.append(item1)

        # 2. 姓名与授权书一致
        item2 = CheckItem(
            item_id=definitions[1]['id'],
            category=category.category_name,
            name=definitions[1]['name']
        )

        if info.authorized_person_name:
            count = text.count(info.authorized_person_name)
            if count >= 2:
                item2.status = "符合"
                item2.detail = f"被授权人姓名'{info.authorized_person_name}'在文档中出现{count}次"
            else:
                item2.status = "无法判断"
                item2.detail = "被授权人姓名出现次数较少"
                item2.suggestion = "请核对授权委托书与身份证姓名是否一致"
        elif has_authorization:
            item2.status = "无法判断"
            item2.detail = "未识别到被授权人姓名"
        else:
            item2.status = "符合"
            item2.detail = "无授权委托，法人亲自投标"

        items.append(item2)

        # 3. 年龄合理
        item3 = CheckItem(
            item_id=definitions[2]['id'],
            category=category.category_name,
            name=definitions[2]['name']
        )

        if info.authorized_person_birth_date:
            age = self.id_extractor.calculate_age(info.authorized_person_birth_date)
            if 18 <= age <= 80:
                item3.status = "符合"
                item3.detail = f"被授权人年龄{age}岁"
            else:
                item3.status = "不符合"
                item3.detail = f"被授权人年龄{age}岁，不在合理范围内"
                item3.suggestion = "请核对被授权人身份证信息"
        elif has_authorization:
            item3.status = "无法判断"
            item3.detail = "未识别到被授权人出生日期"
        else:
            item3.status = "符合"
            item3.detail = "无授权委托，法人亲自投标"

        items.append(item3)

        category.items = items
        return category

    def _check_business_license(self, text: str, info: ExtractedInfo, page_count: int) -> CheckCategory:
        """营业执照检查"""
        category = CheckCategory(
            category_id=CheckCategoryType.BUSINESS_LICENSE.value,
            category_name=CATEGORY_NAMES[CheckCategoryType.BUSINESS_LICENSE]
        )

        items = []
        definitions = CHECK_ITEMS_DEFINITION[CheckCategoryType.BUSINESS_LICENSE]

        # 1. 营业执照在有效期内
        item1 = CheckItem(
            item_id=definitions[0]['id'],
            category=category.category_name,
            name=definitions[0]['name']
        )

        if info.license_expiry:
            if info.license_expiry == "长期":
                item1.status = "符合"
                item1.detail = "营业执照为长期有效"
            else:
                expiry_check = self.license_extractor.check_expiry(info.license_expiry)
                if expiry_check['is_valid']:
                    item1.status = "符合"
                    item1.detail = f"营业执照有效期至{info.license_expiry}"
                else:
                    item1.status = "不符合"
                    item1.detail = f"营业执照已过期：{info.license_expiry}"
                    item1.suggestion = "请提供有效期内的营业执照"
        else:
            item1.status = "无法判断"
            item1.detail = "未识别到营业执照有效期信息"

        items.append(item1)

        # 2. 公司名称全文一致
        item2 = CheckItem(
            item_id=definitions[1]['id'],
            category=category.category_name,
            name=definitions[1]['name']
        )

        if info.company_name:
            count = text.count(info.company_name)
            if count >= 3:
                item2.status = "符合"
                item2.detail = f"公司名称'{info.company_name}'在文档中一致出现"
            else:
                item2.status = "无法判断"
                item2.detail = "公司名称出现次数较少，请人工核对"
                item2.suggestion = "请核对文档中所有公司名称是否完全一致"
        else:
            item2.status = "无法判断"
            item2.detail = "未识别到公司名称"

        items.append(item2)

        # 3. 统一社会信用代码一致
        item3 = CheckItem(
            item_id=definitions[2]['id'],
            category=category.category_name,
            name=definitions[2]['name']
        )

        if info.unified_credit_code:
            count = text.count(info.unified_credit_code)
            if count >= 2:
                item3.status = "符合"
                item3.detail = f"统一社会信用代码'{info.unified_credit_code}'一致"
            else:
                item3.status = "无法判断"
                item3.detail = "统一社会信用代码出现次数较少"
                item3.suggestion = "请核对文档中信用代码是否一致"
        else:
            item3.status = "无法判断"
            item3.detail = "未识别到统一社会信用代码"

        items.append(item3)

        category.items = items
        return category

    def _check_response_date(self, text: str, info: ExtractedInfo, page_count: int) -> CheckCategory:
        """应答日期检查"""
        category = CheckCategory(
            category_id=CheckCategoryType.RESPONSE_DATE.value,
            category_name=CATEGORY_NAMES[CheckCategoryType.RESPONSE_DATE]
        )

        items = []
        definitions = CHECK_ITEMS_DEFINITION[CheckCategoryType.RESPONSE_DATE]

        # 1. 文档中所有应答日期一致
        item1 = CheckItem(
            item_id=definitions[0]['id'],
            category=category.category_name,
            name=definitions[0]['name']
        )

        date_consistency = self.date_extractor.check_date_consistency(info.response_dates)
        if date_consistency['is_consistent']:
            item1.status = "符合"
            item1.detail = date_consistency.get('message', '应答日期一致')
            if 'date' in date_consistency:
                item1.detail = f"应答日期一致：{date_consistency['date']}"
        else:
            if info.response_dates:
                item1.status = "不符合"
                item1.detail = f"发现多个不同日期：{', '.join(info.response_dates)}"
                item1.suggestion = "请统一所有应答日期"
            else:
                item1.status = "无法判断"
                item1.detail = "未识别到应答日期"

        items.append(item1)

        # 2. 授权有效期覆盖投标日期
        item2 = CheckItem(
            item_id=definitions[1]['id'],
            category=category.category_name,
            name=definitions[1]['name']
        )

        auth_validity = self.date_extractor.check_auth_period_validity(
            info.authorization_valid_period,
            info.bid_deadline
        )

        if auth_validity['is_valid']:
            item2.status = "符合"
            item2.detail = auth_validity.get('message', '授权有效期覆盖投标日期')
        else:
            item2.status = "不符合"
            item2.detail = auth_validity.get('message', '授权有效期问题')
            item2.suggestion = "请确保授权有效期覆盖投标截止日期"

        items.append(item2)

        category.items = items
        return category

    def _check_price(self, text: str, info: ExtractedInfo, page_count: int) -> CheckCategory:
        """报价检查"""
        category = CheckCategory(
            category_id=CheckCategoryType.PRICE_CHECK.value,
            category_name=CATEGORY_NAMES[CheckCategoryType.PRICE_CHECK]
        )

        items = []
        definitions = CHECK_ITEMS_DEFINITION[CheckCategoryType.PRICE_CHECK]

        # 1. 大小写金额一致
        item1 = CheckItem(
            item_id=definitions[0]['id'],
            category=category.category_name,
            name=definitions[0]['name']
        )

        amount_check = self.price_extractor.check_amount_consistency(
            info.total_price_upper,
            info.total_price_lower
        )

        if amount_check['is_consistent']:
            item1.status = "符合"
            item1.detail = f"大写：{info.total_price_upper}，小写：{info.total_price_lower}元"
        else:
            if info.total_price_upper and info.total_price_lower:
                item1.status = "不符合"
                item1.detail = f"大写：{info.total_price_upper}，小写：{info.total_price_lower}元"
                item1.suggestion = "请核对并统一大小写金额"
            else:
                item1.status = "无法判断"
                item1.detail = amount_check.get('message', '未完整识别报价金额')

        items.append(item1)

        # 2. 单价×数量=总价 计算正确
        item2 = CheckItem(
            item_id=definitions[1]['id'],
            category=category.category_name,
            name=definitions[1]['name']
        )

        calc_check = self.price_extractor.check_calculation(
            info.unit_prices,
            info.total_price_lower
        )

        if calc_check['is_correct']:
            item2.status = "符合"
            item2.detail = calc_check.get('message', '计算正确')
        else:
            item2.status = "不符合"
            item2.detail = calc_check.get('message', '计算错误')
            item2.suggestion = "请核对单价明细计算"

        items.append(item2)

        # 3. 报价未超过最高限价
        item3 = CheckItem(
            item_id=definitions[2]['id'],
            category=category.category_name,
            name=definitions[2]['name']
        )

        limit_check = self.price_extractor.check_max_limit(
            info.total_price_lower,
            info.max_limit_price
        )

        if limit_check['is_within_limit']:
            item3.status = "符合"
            item3.detail = limit_check.get('message', '报价未超过最高限价')
        else:
            item3.status = "不符合"
            item3.detail = limit_check.get('message', '报价超过最高限价')
            item3.suggestion = "请调整报价，确保不超过最高限价"

        items.append(item3)

        category.items = items
        return category

    def _check_performance(self, text: str, info: ExtractedInfo, page_count: int) -> CheckCategory:
        """业绩检查"""
        category = CheckCategory(
            category_id=CheckCategoryType.PERFORMANCE.value,
            category_name=CATEGORY_NAMES[CheckCategoryType.PERFORMANCE]
        )

        # 使用AI检查
        items = self._ai_check(
            PromptType.PERFORMANCE,
            CheckCategoryType.PERFORMANCE,
            document_content=text[:20000]
        )

        category.items = items
        return category

    # ========== 辅助方法 ==========

    def _ai_check(self, prompt_type: PromptType, category_type: CheckCategoryType, **kwargs) -> List[CheckItem]:
        """
        使用AI进行检查

        Args:
            prompt_type: 提示词类型
            category_type: 检查类别类型
            **kwargs: 提示词参数

        Returns:
            检查项列表
        """
        definitions = CHECK_ITEMS_DEFINITION[category_type]
        category_name = CATEGORY_NAMES[category_type]

        if not self.llm:
            # 无LLM时返回默认结果
            return self._create_default_items(definitions, category_name)

        try:
            # 构建提示词
            prompt = self.prompt_manager.get_prompt(prompt_type, **kwargs)
            config = self.prompt_manager.get_config(prompt_type)

            # 调用LLM
            response = self.llm.call(
                prompt=prompt,
                system_prompt=config['system_prompt'],
                temperature=config['temperature'],
                max_tokens=config['max_tokens']
            )

            # 解析响应
            items = self._parse_ai_response(response, definitions, category_name)
            return items

        except Exception as e:
            logger.warning(f"AI检查失败: {e}")
            return self._create_default_items(definitions, category_name)

    def _parse_ai_response(self, response: str, definitions: List[Dict], category_name: str) -> List[CheckItem]:
        """
        解析AI响应

        Args:
            response: AI响应
            definitions: 检查项定义
            category_name: 类别名称

        Returns:
            检查项列表
        """
        if not response:
            return self._create_default_items(definitions, category_name)

        # 清理markdown代码块
        response = response.strip()
        if response.startswith('```'):
            response = re.sub(r'^```json?\s*', '', response)
            response = re.sub(r'\s*```$', '', response)

        try:
            data = json.loads(response)
            ai_items = data.get('items', [])

            items = []
            for i, definition in enumerate(definitions):
                item = CheckItem(
                    item_id=definition['id'],
                    category=category_name,
                    name=definition['name']
                )

                # 匹配AI返回的结果
                if i < len(ai_items):
                    ai_item = ai_items[i]
                    item.status = ai_item.get('status', '无法判断')
                    item.detail = ai_item.get('detail', '')
                    item.location = ai_item.get('location', '')
                    item.suggestion = ai_item.get('suggestion', '')
                else:
                    item.status = "无法判断"
                    item.detail = "AI未返回此项检查结果"

                items.append(item)

            return items

        except json.JSONDecodeError as e:
            logger.warning(f"JSON解析失败: {e}")
            return self._create_default_items(definitions, category_name)

    def _create_default_items(self, definitions: List[Dict], category_name: str) -> List[CheckItem]:
        """
        创建默认检查项

        Args:
            definitions: 检查项定义
            category_name: 类别名称

        Returns:
            检查项列表
        """
        items = []
        for definition in definitions:
            item = CheckItem(
                item_id=definition['id'],
                category=category_name,
                name=definition['name'],
                status="无法判断",
                detail="需要人工核对",
                suggestion="请人工检查此项"
            )
            items.append(item)
        return items

    def _create_default_category(self, category_type: CheckCategoryType) -> CheckCategory:
        """
        创建默认类别结果

        Args:
            category_type: 类别类型

        Returns:
            检查类别
        """
        category = CheckCategory(
            category_id=category_type.value,
            category_name=CATEGORY_NAMES[category_type]
        )

        definitions = CHECK_ITEMS_DEFINITION[category_type]
        category.items = self._create_default_items(definitions, category.category_name)
        category.calculate_counts()

        return category
