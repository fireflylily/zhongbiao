#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
信息填写模块 - 精简版 (从2098行精简至400行以内)

处理项目和公司信息的填写，实现六大规则：
- 替换规则、填空规则、组合规则、变体处理、例外处理、后处理

通过依赖utils.py和format_cleaner.py实现复用架构优化
"""

import re
import sys
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph
import logging

# 添加路径以导入公共模块
sys.path.append(str(Path(__file__).parent.parent.parent))

# 导入复用模块
from .utils import (
    FieldMapper, PatternMatcher, WordDocumentUtils,
    SmartFieldDetector, TextUtils
)
from .format_cleaner import FormatCleaner, DateFormatProcessor
from common import get_module_logger


class InfoFiller:
    """
    信息填写器 - 精简版
    
    专注核心的信息填写功能，通过复用模块实现工具函数和格式处理
    """
    
    def __init__(self):
        """初始化信息填写器"""
        self.logger = get_module_logger("info_filler")
        self.field_mapper = FieldMapper()
        self.pattern_matcher = PatternMatcher()
        self.format_cleaner = FormatCleaner()
        self.info = {}  # 统一信息字典
        
        # 字段变体映射 (核心配置)
        self.field_variants = self._create_field_variants()
        
    def _create_field_variants(self) -> Dict[str, List[str]]:
        """创建字段变体映射"""
        return {
            # 供应商名称变体 (12种)
            'companyName': [
                '供应商名称', '供应商全称', '投标人名称', '公司名称', 
                '单位名称', '应答人名称', '供应商名称（盖章）',
                '供应商名称（公章）', '公司名称（盖章）',
                '投标人名称（盖章）', '投标人名称（公章）',
                '单位名称（盖章）', '单位名称（公章）'
            ],
            # 其他字段变体
            'email': ['邮箱', '邮件', '电子邮件', '电子邮箱', 'email', 'Email', 'E-mail', 'E-Mail', '邮件地址'],
            'phone': ['电话', '联系电话', '固定电话', '办公电话', '座机', '电话号码', '联系方式'],
            'fax': ['传真', '传真号码', '传真电话', 'FAX', '传真号', 'fax', 'Fax'],
            'address': ['地址', '联系地址', '办公地址', '注册地址', '公司地址', '详细地址', '通讯地址', '供应商地址'],
            'postalCode': ['邮政编码', '邮编', '邮码'],
            'date': ['日期', '日 期', '日  期', '日   期', '日    期', '日     期', '时间', '签署日期', '投标日期'],
            'purchaserName': ['采购人', '招标人', '采购单位', '招标单位', '业主', '甲方'],
            'projectName': ['项目名称', '项目名', '工程名称', '标的名称', '采购项目名称', '招标项目名称'],
            'projectNumber': ['项目编号', '采购编号', '招标编号', '项目号', '标书编号', '工程编号'],
            # 备份版本中的重要字段
            'establishDate': ['成立时间', '成立日期', '注册时间', '注册日期'],
            'businessScope': ['经营范围', '业务范围', '经营项目'],
            'legalRepresentative': ['法定代表人', '法人代表', '法人'],
            'authorizedPersonName': ['供应商代表姓名', '授权代表姓名', '代表姓名', '授权代表'],
            'position': ['职务', '职位', '职称'],
        }
    
    def fill_info(self, doc: Document, company_info: Dict[str, Any], 
                  project_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        填写文档信息 - 主处理流程
        
        Args:
            doc: Word文档对象
            company_info: 公司信息字典
            project_info: 项目信息字典
            
        Returns:
            处理统计信息字典
        """
        self.logger.info("🛠 统一字段映射初始化: 32 个字段")
        
        # 创建统一字段映射
        self.info = self._create_unified_field_mapping(company_info, project_info)
        
        # 初始化统计
        stats = {
            'total_replacements': 0,
            'replacement_rules': 0,
            'fill_rules': 0, 
            'combination_rules': 0,
            'skipped_fields': 0,
            'none': 0
        }
        
        # 处理段落
        self.logger.info(f"📊 开始处理文档: {len([p for p in doc.paragraphs if p.text.strip()])} 个非空段落, 0 个表格")
        
        for i, paragraph in enumerate(doc.paragraphs):
            if paragraph.text.strip():
                self.logger.info(f"🔍 [调试] 处理段落 {i+1}: {paragraph.text.strip()[:100]}...")
                paragraph_stats = self._process_paragraph(paragraph, self.info)
                if paragraph_stats['total_replacements'] > 0:
                    self.logger.info(f"🎉 [调试] 段落 {i+1} 处理成功: {paragraph_stats}")
                for key, value in paragraph_stats.items():
                    stats[key] = stats.get(key, 0) + value
        
        # 处理表格（简化版）
        for table in doc.tables:
            table_stats = self._process_table(table, self.info)
            for key, value in table_stats.items():
                stats[key] = stats.get(key, 0) + value
        
        # 后处理：清理多余的占位符和装饰性格式
        self._apply_post_processing(doc)
        
        # 日志输出
        self.logger.info(f"📊 文档处理统计: {stats}")
        self.logger.info(f"✅ 成功处理了 {stats['total_replacements']} 个字段")
        self.logger.info(f"  - 填空规则: {stats['fill_rules']} 个")
        self.logger.info(f"  - 组合规则: {stats['combination_rules']} 个")
        
        return stats
    
    def _create_unified_field_mapping(self, company_info: Dict[str, Any],
                                     project_info: Dict[str, Any]) -> Dict[str, str]:
        """创建统一的字段映射"""
        # 添加调试信息：显示输入的company_info数据
        self.logger.info(f"🔍 [调试] 输入的company_info数据: {company_info}")
        self.logger.info(f"🔍 [调试] 输入的project_info数据: {project_info}")

        info = {}
        
        # 映射公司信息 - 直接使用原有的字段名映射
        info['公司名称'] = company_info.get('companyName', '')
        info['邮箱'] = company_info.get('email', '')
        info['传真'] = company_info.get('fax', '')
        info['邮政编码'] = company_info.get('postalCode', '')
        info['成立时间'] = company_info.get('establishDate', '')
        info['经营范围'] = company_info.get('businessScope', '')
        info['法定代表人'] = company_info.get('legalRepresentative', '')
        info['被授权人姓名'] = company_info.get('authorizedPersonName', '')
        info['被授权人职务'] = company_info.get('authorizedPersonPosition', '')
        info['法定代表人职位'] = company_info.get('legalRepresentativePosition', '')
        
        # 处理多源映射字段
        info['地址'] = (company_info.get('address') or 
                      company_info.get('registeredAddress') or 
                      company_info.get('officeAddress', ''))
        info['电话'] = (company_info.get('fixedPhone') or
                      company_info.get('phone', ''))

        # 调试电话字段映射
        self.logger.info(f"🔍 [调试] 电话字段映射: fixedPhone={company_info.get('fixedPhone')}, phone={company_info.get('phone')}, 最终值={info['电话']}")
        
        # 映射项目信息
        info['项目名称'] = project_info.get('projectName', '')
        info['项目编号'] = project_info.get('projectNumber', '')
        info['日期'] = project_info.get('date', '')
        info['采购人名称'] = project_info.get('purchaserName', '')
        
        # 清理空值
        info = {k: v for k, v in info.items() if v and str(v).strip()}
        
        # 添加调试信息
        self.logger.info(f"🗺️ 字段映射结果: {list(info.keys())}")
        for key, value in info.items():
            self.logger.info(f"  - {key}: {value}")
        
        return info
    
    def _process_paragraph(self, paragraph: Paragraph, info: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理段落 - 核心业务逻辑
        
        Args:
            paragraph: Word段落对象
            info: 信息字典
            
        Returns:
            处理统计信息
        """
        stats = {'total_replacements': 0, 'replacement_rules': 0, 'fill_rules': 0, 'combination_rules': 0}
        
        # 跳过处理
        if self._should_skip(paragraph.text):
            return stats
            
        processed = False
        final_type = 'none'

        # 1. 尝试组合替换规则
        if self._try_combination_rule(paragraph, info):
            processed = True
            final_type = 'combination_rules'
            stats['combination_rules'] += 1
            stats['total_replacements'] += 1

        # 2. 尝试单字段替换规则（即使组合规则已处理，也要尝试）
        if self._try_replacement_rule(paragraph, info):
            processed = True
            # 如果已经有组合规则，保持组合规则类型，否则设为替换规则
            if final_type == 'none':
                final_type = 'replacement_rules'
                stats['replacement_rules'] += 1
                stats['total_replacements'] += 1

        # 3. 尝试填空规则（仅在前两个都没有处理时才尝试）
        if not processed and self._try_fill_rule(paragraph, info):
            processed = True
            final_type = 'fill_rules'
            stats['fill_rules'] += 1
            stats['total_replacements'] += 1

        return stats
    
    def _should_skip(self, text: str) -> bool:
        """判断是否应该跳过处理"""
        import re

        # 使用精确匹配模式，避免误跳过合法填空字段
        skip_patterns = [
            r'签字\s*[：:]?\s*$',      # 签字: 或 签字（行尾）
            r'签字处',                 # 签字处
            r'签名\s*[：:]?\s*$',      # 签名: 或 签名（行尾）
            r'签名处',                 # 签名处
            r'签章\s*[：:]?\s*$',      # 签章: 或 签章（行尾）
            r'盖章处',                 # 盖章处
        ]

        # 简单关键词匹配（保持原有逻辑）
        simple_keywords = [
            '招标代理', '采购代理', '业主', '发包人', '委托人'
        ]

        text_lower = text.lower()

        # 检查精确模式
        for pattern in skip_patterns:
            if re.search(pattern, text_lower):
                return True

        # 检查简单关键词
        for keyword in simple_keywords:
            if keyword in text_lower:
                return True

        return False

    def _detect_position_context(self, paragraph_text: str) -> str:
        """
        检测段落中的职位上下文，区分被授权人职务和法定代表人职位

        Args:
            paragraph_text: 段落文本

        Returns:
            'authorized_person': 被授权人上下文
            'legal_representative': 法定代表人上下文（默认）
        """
        try:
            if not paragraph_text or not isinstance(paragraph_text, str):
                self.logger.warning(f"⚠️  职位上下文检测：无效的段落文本输入")
                return 'legal_representative'

            text = paragraph_text.strip()
            if not text:
                self.logger.warning(f"⚠️  职位上下文检测：段落文本为空")
                return 'legal_representative'

            # 被授权人上下文关键字模式 (增强版)
            authorized_person_patterns = [
                r'授权.*?代表.*?[职位务称]',          # "授权代表职务"
                r'为我方.*?授权.*?代表',             # "为我方授权代表"
                r'为我方代表.*?[职位务称]',           # "为我方代表职务"
                r'参加.*?代表.*?[职位务称]',          # "参加投标代表职务"
                r'授权.*?[（(].*?[）)].*?[职位务称]',   # "授权（张三）职务"
                r'被授权.*?[职位务称]',              # "被授权人职务"
                r'商务代表.*?[职位务称]',             # "商务代表职务"
                r'授权.*?[（(].*?姓名.*?职[位务称]',   # "授权（姓名、职位）"
                r'为我方.*?授权.*?[（(].*?职[位务称]', # "为我方授权（职位、职称）"
            ]

            # 法定代表人上下文关键字模式
            legal_representative_patterns = [
                r'法定代表人.*?职位',           # "法定代表人职位"
                r'法人.*?职位',                # "法人职位"
                r'系.*?法定代表人.*?职位',      # "系我公司法定代表人职位"
                r'公司.*?法定代表人.*?职位',    # "公司法定代表人职位"
            ]

            self.logger.debug(f"🔍 检测职位上下文: '{text[:100]}{'...' if len(text) > 100 else ''}'")

            # 检查被授权人上下文
            try:
                for pattern in authorized_person_patterns:
                    if re.search(pattern, text):
                        self.logger.info(f"✅ 识别为被授权人上下文: '{pattern}' 匹配")
                        return 'authorized_person'
            except re.error as e:
                self.logger.error(f"❌ 被授权人模式匹配正则表达式错误: {e}")

            # 检查法定代表人上下文
            try:
                for pattern in legal_representative_patterns:
                    if re.search(pattern, text):
                        self.logger.info(f"✅ 识别为法定代表人上下文: '{pattern}' 匹配")
                        return 'legal_representative'
            except re.error as e:
                self.logger.error(f"❌ 法定代表人模式匹配正则表达式错误: {e}")

            # 默认情况：如果没有明确上下文，使用法定代表人
            return 'legal_representative'

        except Exception as e:
            self.logger.error(f"❌ 职位上下文检测发生异常: {e}")
            return 'legal_representative'

    def _try_combination_rule(self, paragraph: Paragraph, info: Dict[str, Any]) -> bool:
        """尝试应用组合替换规则"""
        text = paragraph.text
        
        # 组合规则模式
        combination_patterns = [
            # (供应商名称、地址)
            (r'[（(]\s*(?:供应商名称|公司名称|单位名称)[、，]\s*(?:地址|联系地址)\s*[）)]',
             ['companyName', 'address']),
            # (项目名称、项目编号)
            (r'[（(]\s*(?:项目名称|工程名称)[、，]\s*(?:项目编号|招标编号)\s*[）)]',
             ['projectName', 'projectNumber']),
            # (联系电话、邮箱)
            (r'[（(]\s*(?:联系电话|电话)[、，]\s*(?:邮箱|电子邮件)\s*[）)]',
             ['phone', 'email'])
        ]

        # 智能职位组合处理 - 支持上下文识别
        position_pattern = r'[（(]\s*职[位务称]\s*[、，]\s*职[位务称]\s*[）)]'
        if re.search(position_pattern, text):
            self.logger.debug(f"🎯 检测到职位组合模式: '{text[:50]}...'")

            try:
                # 智能识别上下文
                context = self._detect_position_context(text)
                self.logger.debug(f"🧠 上下文识别结果: {context}")

                # 根据上下文选择数据源
                if context == 'authorized_person':
                    position = info.get('被授权人职务', '') or info.get('authorizedPersonPosition', '')
                    if position:
                        self.logger.info(f"📝 使用被授权人职务: '{position}'")
                    else:
                        self.logger.warning(f"⚠️ 被授权人职务为空，尝试法定代表人职位")
                        position = info.get('法定代表人职位', '') or info.get('legalRepresentativePosition', '')
                        if position:
                            self.logger.info(f"📝 回退使用法定代表人职位: '{position}'")
                else:  # legal_representative
                    position = info.get('法定代表人职位', '') or info.get('legalRepresentativePosition', '')
                    if position:
                        self.logger.info(f"📝 使用法定代表人职位: '{position}'")
                    else:
                        self.logger.warning(f"⚠️ 法定代表人职位为空，尝试被授权人职务")
                        position = info.get('被授权人职务', '') or info.get('authorizedPersonPosition', '')
                        if position:
                            self.logger.info(f"📝 回退使用被授权人职务: '{position}'")

                if position:
                    replacement = f"（{position}、{position}）"
                    # 使用精确格式处理引擎进行智能职位组合替换
                    if WordDocumentUtils.precise_replace(paragraph, position_pattern, replacement, self.logger):
                        self.logger.info(f"智能职位组合替换: （职位、职称） → （{position}、{position}）")
                        return True
                else:
                    self.logger.warning(f"⚠️ 所有职位数据源都为空，跳过处理")

            except Exception as e:
                self.logger.error(f"❌ 职位组合替换发生异常: {e}")

        # 智能姓名职位组合处理
        name_position_pattern = r'[（(]\s*姓名\s*[、，]\s*职[位务称]\s*[）)]'
        if re.search(name_position_pattern, text):
            self.logger.debug(f"🎯 检测到姓名职位组合模式: '{text[:50]}...'")

            try:
                # 智能识别上下文
                context = self._detect_position_context(text)
                self.logger.debug(f"🧠 上下文识别结果: {context}")

                # 根据上下文选择数据源
                if context == 'authorized_person':
                    name = info.get('被授权人姓名', '') or info.get('authorizedPersonName', '')
                    position = info.get('被授权人职务', '') or info.get('authorizedPersonPosition', '')
                    if name and position:
                        self.logger.info(f"📝 使用被授权人信息: '{name}', '{position}'")
                    elif not name:
                        name = info.get('法定代表人', '') or info.get('legalRepresentativeName', '')
                        if name:
                            self.logger.warning(f"⚠️ 被授权人姓名为空，使用法定代表人: '{name}'")
                    elif not position:
                        position = info.get('法定代表人职位', '') or info.get('legalRepresentativePosition', '')
                        if position:
                            self.logger.warning(f"⚠️ 被授权人职务为空，使用法定代表人职位: '{position}'")
                else:  # legal_representative
                    name = info.get('法定代表人', '') or info.get('legalRepresentativeName', '')
                    position = info.get('法定代表人职位', '') or info.get('legalRepresentativePosition', '')
                    if name and position:
                        self.logger.info(f"📝 使用法定代表人信息: '{name}', '{position}'")
                    elif not name:
                        name = info.get('被授权人姓名', '') or info.get('authorizedPersonName', '')
                        if name:
                            self.logger.warning(f"⚠️ 法定代表人姓名为空，使用被授权人: '{name}'")
                    elif not position:
                        position = info.get('被授权人职务', '') or info.get('authorizedPersonPosition', '')
                        if position:
                            self.logger.warning(f"⚠️ 法定代表人职位为空，使用被授权人职务: '{position}'")

                if name and position:
                    replacement = f"（{name}、{position}）"
                    if WordDocumentUtils.precise_replace(paragraph, name_position_pattern, replacement, self.logger):
                        self.logger.info(f"智能姓名职位组合替换: （姓名、职位） → （{name}、{position}）")
                        return True
                else:
                    self.logger.warning(f"⚠️ 姓名或职位数据为空: 姓名={name}, 职位={position}")

            except Exception as e:
                self.logger.error(f"❌ 姓名职位组合替换发生异常: {e}")
        
        # 处理所有组合模式，而不是处理一个就返回
        processed_any = False

        for pattern, field_keys in combination_patterns:
            if re.search(pattern, text):
                # 构建替换文本
                replacement_parts = []

                # 直接映射字段
                field_mapping = {
                    'companyName': '公司名称',
                    'address': '地址',
                    'projectName': '项目名称',
                    'projectNumber': '项目编号',
                    'phone': '电话',
                    'email': '邮箱'
                }

                for field_key in field_keys:
                    field_name = field_mapping.get(field_key)
                    if field_name and field_name in info:
                        replacement_parts.append(info[field_name])

                if replacement_parts:
                    replacement_text = f"（{', '.join(replacement_parts)}）"
                    success = WordDocumentUtils.precise_replace(paragraph, pattern, replacement_text, self.logger)
                    if success:
                        self.logger.info(f"🔄 组合规则替换成功: {pattern[:30]}... -> {replacement_text}")
                        processed_any = True

        return processed_any
    
    def _try_replacement_rule(self, paragraph: Paragraph, info: Dict[str, Any]) -> bool:
        """尝试应用括号替换规则"""
        text = paragraph.text
        
        # 括号替换规则
        for field_name, value in info.items():
            if not value:
                continue
                
            # 获取字段变体 - 直接使用字段名进行映射
            field_mapping = {
                '公司名称': self.field_variants['companyName'],
                '邮箱': self.field_variants['email'], 
                '电话': self.field_variants['phone'],
                '传真': self.field_variants['fax'],
                '地址': self.field_variants['address'],
                '邮政编码': self.field_variants['postalCode'],
                '日期': self.field_variants['date'],
                '采购人名称': self.field_variants['purchaserName'],
                '项目名称': self.field_variants['projectName'],
                '项目编号': self.field_variants['projectNumber']
            }
            field_variants = field_mapping.get(field_name, [])
            
            if not field_variants:
                continue
                
            # 构建括号匹配模式
            variants_pattern = '|'.join(re.escape(variant) for variant in field_variants)
            bracket_pattern = f'[（(]\\s*(?:{variants_pattern})\\s*[）)]'
            
            if re.search(bracket_pattern, text):
                replacement_text = f'（{value}）'
                success = WordDocumentUtils.precise_replace(paragraph, bracket_pattern, replacement_text, self.logger)
                if success:
                    self.logger.info(f"🔄 括号替换成功: {field_name} -> {value}")
                    return True
        
        return False
    
    def _try_fill_rule(self, paragraph: Paragraph, info: Dict[str, Any]) -> bool:
        """尝试应用填空规则"""
        text = paragraph.text
        
        # 填空规则处理
        for field_name, value in info.items():
            if not value:
                self.logger.info(f"🔍 [调试] 跳过空字段: {field_name}")
                continue

            self.logger.info(f"🔍 [调试] 尝试填空字段: {field_name} = {value}")
                
            # 获取字段变体 - 直接使用字段名进行映射
            field_mapping = {
                '公司名称': self.field_variants['companyName'],
                '邮箱': self.field_variants['email'], 
                '电话': self.field_variants['phone'],
                '传真': self.field_variants['fax'],
                '地址': self.field_variants['address'],
                '邮政编码': self.field_variants['postalCode'],
                '日期': self.field_variants['date'],
                '采购人名称': self.field_variants['purchaserName'],
                '项目名称': self.field_variants['projectName'],
                '项目编号': self.field_variants['projectNumber']
            }
            field_variants = field_mapping.get(field_name, [])
            
            if not field_variants:
                continue
            
            # 检查是否应该在此段落中尝试该字段
            if not SmartFieldDetector.should_try_field_in_paragraph(text, field_variants):
                self.logger.info(f"🔍 [调试] 跳过字段 {field_name} 在段落: {text[:50]}...")
                continue
            
            # 尝试各种填空策略
            for variant in field_variants:
                self.logger.info(f"🔍 [调试] 尝试字段变体: {variant} 在段落: {paragraph.text[:50]}...")

                # 策略1：括号格式替换（优先级最高）
                if self._try_bracket_strategy(paragraph, variant, value):
                    self.logger.info(f"🔄 括号格式成功: {field_name} -> {value}")
                    return True

                # 策略2：插入式替换
                if self._try_insert_strategy(paragraph, variant, value):
                    self.logger.info(f"🔄 插入式成功: {field_name} -> {value}")
                    return True

                # 策略3：纯空格替换
                if self._try_space_only_strategy(paragraph, variant, value):
                    self.logger.info(f"🔄 纯空格成功: {field_name} -> {value}")
                    return True

                # 策略4：公章格式替换
                if self._try_stamp_strategy(paragraph, variant, value):
                    self.logger.info(f"🔄 公章格式成功: {field_name} -> {value}")
                    return True

                # 策略5：传统填空模式（保留原有逻辑）
                if self._try_fill_patterns(paragraph, variant, value):
                    self.logger.info(f"🔄 填空规则成功: {field_name} -> {value}")
                    return True
        
        return False
    
    def _try_fill_patterns(self, paragraph: Paragraph, field_variant: str, value: str) -> bool:
        """尝试各种填空模式"""
        patterns = [
            # 模式1: 字段名：___
            f'{re.escape(field_variant)}\\s*[：:]\\s*_+',
            # 模式2: 字段名：
            f'{re.escape(field_variant)}\\s*[：:]\\s*$',
            # 模式3: 字段名：___ (混合)
            f'{re.escape(field_variant)}\\s*[：:]\\s*[_\\s]*$',
            # 模式4: 字段名 (插入式)
            f'{re.escape(field_variant)}(?=\\s+)(?![：:])',
            # 模式5: 致：字段名 格式
            f'致\\s*[：:]\\s*{re.escape(field_variant)}\\s*$'
        ]
        
        for pattern in patterns:
            if re.search(pattern, paragraph.text):
                # 构建替换文本
                if '致' in pattern:
                    # 特殊处理"致："格式
                    replacement = f'致：{value}'
                elif '：' in paragraph.text or ':' in paragraph.text:
                    replacement = f'{field_variant}：{value}'
                else:
                    replacement = f'{field_variant} {value}'

                success = WordDocumentUtils.precise_replace(paragraph, pattern, replacement, self.logger)
                if success:
                    return True
        
        return False

    def _try_bracket_strategy(self, paragraph: Paragraph, variant: str, value: str) -> bool:
        """策略1：括号格式替换 - 处理（字段名）→（替换值）格式"""
        # 快速检查：如果段落中根本没有括号，直接返回
        if '（' not in paragraph.text and '(' not in paragraph.text:
            return False

        bracket_pattern = rf'[（(]\s*{re.escape(variant)}\s*[）)]'
        match = re.search(bracket_pattern, paragraph.text)
        if not match:
            return False

        self.logger.info(f"🎯 策略1(括号格式)匹配成功 - 字段: {variant}")
        self.logger.info(f"📝 匹配模式: {bracket_pattern}")
        self.logger.info(f"✅ 匹配内容: '{match.group()}'")

        replacement = f"（{value}）"
        return WordDocumentUtils.precise_replace(paragraph, bracket_pattern, replacement, self.logger)

    def _try_insert_strategy(self, paragraph: Paragraph, variant: str, value: str) -> bool:
        """策略2：插入式替换 - 直接在字段名后插入内容"""
        # 快速检查：只有字段名后直接跟冒号才拒绝
        if re.search(rf'{re.escape(variant)}\s*[:：]', paragraph.text):
            # 如果字段名后直接跟冒号，不是插入式格式
            return False

        # 检查是否匹配插入式模式：字段名后面跟空格但不跟冒号
        insert_pattern = rf'{re.escape(variant)}(?=\s+)(?![:：])'
        match = re.search(insert_pattern, paragraph.text)
        if not match:
            return False

        self.logger.info(f"🎯 策略2(插入式)匹配成功 - 字段: {variant}")
        replacement = f'{variant} {value}'
        return WordDocumentUtils.precise_replace(paragraph, insert_pattern, replacement, self.logger)

    def _try_space_only_strategy(self, paragraph: Paragraph, variant: str, value: str) -> bool:
        """策略3：纯空格替换 - 处理只有空格无下划线的情况"""
        # 快速检查：必须包含冒号并且以空格结尾
        if not re.search(r'[:：]\s+$', paragraph.text):
            return False

        space_pattern = rf'({re.escape(variant)}\s*[:：])\s+$'
        match = re.search(space_pattern, paragraph.text)
        if not match:
            return False

        self.logger.info(f"🎯 策略3(纯空格)匹配成功 - 字段: {variant}")
        replacement = rf'\1{value}'
        return WordDocumentUtils.precise_replace(paragraph, space_pattern, replacement, self.logger)

    def _try_stamp_strategy(self, paragraph: Paragraph, variant: str, value: str) -> bool:
        """策略4：公章格式替换 - 保留公章括号"""
        # 快速检查：如果段落中没有"章"字，不可能是公章格式
        if '章' not in paragraph.text:
            return False

        stamp_pattern = rf'(?P<prefix>{re.escape(variant)}\s*[:：]\s*)(?P<spaces>[_\s]+)(?P<stamp>[（(][^）)]*章[^）)]*[）)])'
        match = re.search(stamp_pattern, paragraph.text)
        if not match:
            return False

        self.logger.info(f"🎯 策略4(公章格式)匹配成功 - 字段: {variant}")
        replacement = rf'\g<prefix>{value}\g<stamp>'
        return WordDocumentUtils.precise_replace(paragraph, stamp_pattern, replacement, self.logger)

    def _process_table(self, table: Table, info: Dict[str, Any]) -> Dict[str, Any]:
        """处理表格（简化版）"""
        stats = {'total_replacements': 0}
        
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    if paragraph.text.strip():
                        cell_stats = self._process_paragraph(paragraph, info)
                        for key, value in cell_stats.items():
                            stats[key] = stats.get(key, 0) + value
        
        return stats
    
    def _apply_post_processing(self, doc: Document):
        """应用后处理机制"""
        # 清理装饰性格式
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                self._clean_decorative_formats_only(paragraph)
        
        # 处理年月日格式填充
        if 'date' in self.info:
            DateFormatProcessor.process_date_format_filling(
                doc, self.info['date'], WordDocumentUtils, self.logger
            )
    
    def _clean_decorative_formats_only(self, paragraph):
        """仅清理装饰性格式"""
        original_text = paragraph.text
        
        # 检查是否包含填充内容
        contains_filled_content = False
        
        # 检查公司信息
        for value in self.info.values():
            if value and str(value) in original_text:
                contains_filled_content = True
                break
        
        # 如果不包含填充内容，进行基础清理
        if not contains_filled_content:
            cleaned_text = self.format_cleaner.clean_text(original_text, {
                'clean_dates': True,
                'optimize_decorative': True,
                'normalize_whitespace': True
            })
            
            if cleaned_text != original_text:
                # 使用精确格式处理进行后处理清理
                escaped_original = re.escape(original_text.strip())
                success = WordDocumentUtils.precise_replace(paragraph, escaped_original, cleaned_text.strip(), self.logger)
                if not success:
                    # 后备方案
                    paragraph.text = cleaned_text.strip()

# 向后兼容
class BusinessInfoFiller(InfoFiller):
    """向后兼容的类名别名"""
    pass