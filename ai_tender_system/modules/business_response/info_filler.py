#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
信息填写模块 - 精简版 (从2098行精简至400行以内)

处理项目和公司信息的填写，实现六大规则：
- 替换规则、填空规则、组合规则、变体处理、例外处理、后处理

通过依赖utils.py和format_cleaner.py实现复用架构优化
"""

import re
from typing import Dict, List, Optional, Any, Tuple
from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph
import logging

# 导入复用模块
from .utils import (
    FieldMapper, PatternMatcher, WordDocumentUtils, 
    SmartFieldDetector, TextUtils
)
from .format_cleaner import FormatCleaner, DateFormatProcessor

logger = logging.getLogger(__name__)

class InfoFiller:
    """
    信息填写器 - 精简版
    
    专注核心的信息填写功能，通过复用模块实现工具函数和格式处理
    """
    
    def __init__(self):
        """初始化信息填写器"""
        self.logger = logger
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
            'email': ['邮箱', '邮件', '电子邮件', '电子邮箱', 'email', 'Email', 'E-mail', '邮件地址'],
            'phone': ['电话', '联系电话', '固定电话', '办公电话', '座机'],
            'fax': ['传真', '传真号码', '传真电话', 'FAX'],
            'address': ['地址', '联系地址', '办公地址', '注册地址', '公司地址', '详细地址'],
            'postalCode': ['邮编', '邮政编码', '邮码'],
            'date': ['日期', '日 期', '日  期', '时间', '签署日期', '投标日期'],
            'purchaserName': ['采购人', '招标人', '采购单位', '招标单位', '业主', '甲方'],
            'projectName': ['项目名称', '项目名', '工程名称', '标的名称'],
            'projectNumber': ['项目编号', '招标编号', '项目号', '标书编号', '工程编号'],
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
        
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                paragraph_stats = self._process_paragraph(paragraph, self.info)
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
        
        # 处理多源映射字段
        info['地址'] = (company_info.get('address') or 
                      company_info.get('registeredAddress') or 
                      company_info.get('officeAddress', ''))
        info['电话'] = (company_info.get('fixedPhone') or 
                      company_info.get('phone', ''))
        
        # 映射项目信息
        info['项目名称'] = project_info.get('projectName', '')
        info['项目编号'] = project_info.get('projectNumber', '')
        info['日期'] = project_info.get('date', '')
        info['采购人名称'] = project_info.get('purchaserName', '')
        
        # 清理空值
        info = {k: v for k, v in info.items() if v and str(v).strip()}
        
        # 添加调试信息
        self.logger.debug(f"🗺️ 字段映射结果: {list(info.keys())}")
        for key, value in info.items():
            self.logger.debug(f"  - {key}: {value}")
        
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
            
        # 尝试组合规则（优先级最高）
        if self._try_combination_rule(paragraph, info):
            stats['combination_rules'] += 1
            stats['total_replacements'] += 1
            return stats
            
        # 尝试替换规则
        if self._try_replacement_rule(paragraph, info):
            stats['replacement_rules'] += 1
            stats['total_replacements'] += 1
            return stats
            
        # 尝试填空规则
        if self._try_fill_rule(paragraph, info):
            stats['fill_rules'] += 1
            stats['total_replacements'] += 1
            return stats
            
        return stats
    
    def _should_skip(self, text: str) -> bool:
        """判断是否应该跳过处理"""
        skip_keywords = [
            '代理', '招标代理', '采购代理', '业主', '发包人', '委托人',
            '签字', '签名', '签章', '盖章处'
        ]
        
        text_lower = text.lower()
        for keyword in skip_keywords:
            if keyword in text_lower:
                return True
                
        return False
    
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
        
        for pattern, field_keys in combination_patterns:
            if re.search(pattern, text):
                # 构建替换文本
                replacement_parts = []
                for field_key in field_keys:
                    field_name = self.field_mapper.COMPANY_FIELD_MAPPING.get(field_key) or \
                                 self.field_mapper.PROJECT_FIELD_MAPPING.get(field_key)
                    if field_name and field_name in info:
                        replacement_parts.append(info[field_name])
                
                if replacement_parts:
                    replacement_text = f"（{', '.join(replacement_parts)}）"
                    success = WordDocumentUtils.precise_replace(paragraph, pattern, replacement_text, self.logger)
                    if success:
                        self.logger.info(f"🔄 组合规则替换成功: {pattern[:30]}... -> {replacement_text}")
                        return True
        
        return False
    
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
            
            # 检查是否应该在此段落中尝试该字段
            if not SmartFieldDetector.should_try_field_in_paragraph(text, field_variants):
                continue
            
            # 尝试各种填空模式
            for variant in field_variants:
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
            f'{re.escape(field_variant)}(?=\\s+)(?![：:])'
        ]
        
        for pattern in patterns:
            if re.search(pattern, paragraph.text):
                # 构建替换文本
                if '：' in paragraph.text or ':' in paragraph.text:
                    replacement = f'{field_variant}：{value}'
                else:
                    replacement = f'{field_variant} {value}'
                
                success = WordDocumentUtils.precise_replace(paragraph, pattern, replacement, self.logger)
                if success:
                    return True
        
        return False
    
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