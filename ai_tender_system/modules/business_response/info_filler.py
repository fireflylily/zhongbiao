#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
信息填写模块 - 处理项目和公司信息的填写
实现六大规则：替换规则、填空规则、组合规则、变体处理、例外处理、后处理

 1. 供应商名称处理（支持4种规则）
      - 替换规则：（供应商名称）→（公司名）
      - 填空规则：供应商名称：___ → 
    供应商名称：公司名
      - 组合规则：（供应商名称、地址）→（公司
    名、地址）
      - 变体处理：公司名称、应答人名称、供应
    商名称（盖章）等
    2. 其他信息字段（仅填空规则）
      - 电话、邮箱、地址、邮编、传真
      - 支持标签变体（邮箱/电子邮件）
      - 支持格式变化（冒号、空格、占位符）
    3. 例外处理
      - 跳过"签字"相关字段
      - 智能日期处理
      - 识别并跳过采购人/招标人信息
    4. 格式保持
      - 继承第一个字符的格式
      - 保持原有文档样式

"""

import re
from typing import Dict, Any, List, Optional, Tuple
from docx import Document
from docx.text.paragraph import Paragraph
from docx.table import Table, _Cell

# 导入公共模块
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
from common import get_module_logger

class InfoFiller:
    """信息填写处理器"""
    
    def __init__(self):
        self.logger = get_module_logger("info_filler")
        
        # 供应商名称的变体
        self.company_name_variants = [
            '供应商名称', '供应商全称', '投标人名称', '公司名称', 
            '单位名称', '应答人名称', '供应商名称（盖章）', 
            '供应商名称（公章）', '公司名称（盖章）', '投标人（盖章）'
        ]
        
        # 其他字段的变体映射
        self.field_variants = {
            'email': ['电子邮件', '电子邮箱', '邮箱', 'email', 'Email', 'E-mail'],
            'phone': ['电话', '联系电话', '固定电话', '电话号码', '联系方式'],
            'fax': ['传真', '传真号码', '传真号', 'fax', 'Fax'],
            'address': ['地址', '注册地址', '办公地址', '联系地址', '通讯地址', '供应商地址', '公司地址'],
            'postalCode': ['邮政编码', '邮编', '邮码'],
            'legalRepresentative': ['法定代表人', '法人代表', '法人'],
            'authorizedPersonName': ['供应商代表姓名', '授权代表姓名', '代表姓名', '授权代表'],
            'projectName': ['项目名称', '采购项目名称', '招标项目名称'],
            'projectNumber': ['项目编号', '采购编号', '招标编号', '项目号']
        }
        
        # 需要跳过的关键词（招标人信息，但不包括采购人）
        self.skip_keywords = [
            '招标人', '甲方', '代理', '招标代理',
            '采购代理', '业主', '发包人', '委托人'
        ]
        
        # 采购人信息字段（使用项目信息填充）
        self.purchaser_variants = ['采购人', '采购人名称', '采购单位']
        
        # 需要跳过的签字相关词
        self.signature_keywords = ['签字', '签名', '签章', '盖章处']
        
    def fill_info(self, doc: Document, company_info: Dict[str, Any], 
                  project_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        填写信息主方法
        
        Args:
            doc: Word文档对象
            company_info: 公司信息字典
            project_info: 项目信息字典（包含项目名称、编号、日期等）
            
        Returns:
            处理统计信息
        """
        stats = {
            'total_replacements': 0,
            'replacement_rules': 0,
            'fill_rules': 0,
            'combination_rules': 0,
            'skipped_fields': 0,
            'none': 0  # 添加对未处理段落的统计
        }
        
        # 合并所有信息
        all_info = {**company_info, **project_info}
        
        # 处理所有段落
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                result = self._process_paragraph(paragraph, all_info)
                stats['total_replacements'] += result['count']
                
                # 安全地更新统计信息
                result_type = result['type']
                if result_type in stats:
                    if result_type == 'skipped':
                        stats[result_type] += 1
                    else:
                        stats[result_type] += result['count']
                else:
                    # 如果类型不存在，记录为'none'
                    stats['none'] += result['count']
        
        # 处理表格
        for table in doc.tables:
            result = self._process_table(table, all_info)
            stats['total_replacements'] += result['count']
            stats['fill_rules'] += result['count']
        
        # 后处理：清理多余的占位符
        self._post_process(doc)
        
        self.logger.info(f"信息填写完成: {stats}")
        return stats
    
    def _process_paragraph(self, paragraph: Paragraph, info: Dict[str, Any]) -> Dict[str, Any]:
        """处理单个段落"""
        result = {'count': 0, 'type': 'none'}
        para_text = paragraph.text.strip()
        
        # 检查是否需要跳过
        if self._should_skip(para_text):
            self.logger.debug(f"跳过段落: {para_text[:50]}")
            return {'count': 0, 'type': 'skipped'}
        
        # 1. 尝试组合替换规则
        if self._try_combination_rule(paragraph, info):
            return {'count': 1, 'type': 'combination_rules'}
        
        # 2. 尝试单字段替换规则
        if self._try_replacement_rule(paragraph, info):
            return {'count': 1, 'type': 'replacement_rules'}
        
        # 3. 尝试填空规则
        if self._try_fill_rule(paragraph, info):
            return {'count': 1, 'type': 'fill_rules'}
        
        return result
    
    def _should_skip(self, text: str) -> bool:
        """检查是否应该跳过该文本"""
        # 检查是否包含采购人/招标人等关键词
        for keyword in self.skip_keywords:
            if keyword in text:
                return True
        
        # 检查是否包含签字相关词
        for keyword in self.signature_keywords:
            if keyword in text:
                return True
        
        return False
    
    def _try_combination_rule(self, paragraph: Paragraph, info: Dict[str, Any]) -> bool:
        """
        尝试组合替换规则
        如：（供应商名称、地址）→（公司名、地址）
        """
        text = paragraph.text
        
        # 组合模式1：供应商名称、地址
        pattern1 = r'[（(]\s*供应商名称\s*[、，]\s*地址\s*[）)]'
        if re.search(pattern1, text):
            company_name = info.get('companyName', '')
            address = info.get('address', '') or info.get('registeredAddress', '')
            if company_name and address:
                replacement = f"（{company_name}、{address}）"
                new_text = re.sub(pattern1, replacement, text)
                self._update_paragraph_text(paragraph, new_text)
                self.logger.info(f"组合替换: 供应商名称、地址")
                return True
        
        # 组合模式2：项目名称、项目编号
        pattern2 = r'[（(]\s*项目名称\s*[、，]\s*项目编号\s*[）)]'
        if re.search(pattern2, text):
            project_name = info.get('projectName', '')
            project_number = info.get('projectNumber', '')
            if project_name and project_number:
                replacement = f"（{project_name}、{project_number}）"
                new_text = re.sub(pattern2, replacement, text)
                self._update_paragraph_text(paragraph, new_text)
                self.logger.info(f"组合替换: 项目名称、项目编号")
                return True
        
        return False
    
    def _try_replacement_rule(self, paragraph: Paragraph, info: Dict[str, Any]) -> bool:
        """
        尝试单字段替换规则
        如：（供应商名称）→（公司名）、（采购人）→（项目采购人）
        支持单段落中的多个字段替换
        """
        text = paragraph.text
        new_text = text
        replacement_count = 0
        
        # 处理供应商名称类
        for variant in self.company_name_variants:
            pattern = rf'[（(]\s*{re.escape(variant)}\s*[）)]'
            if re.search(pattern, new_text):
                company_name = info.get('companyName', '')
                if company_name:
                    replacement = f"（{company_name}）"
                    new_text = re.sub(pattern, replacement, new_text)
                    self.logger.info(f"替换规则: {variant} → {company_name}")
                    replacement_count += 1
        
        # 处理采购人信息
        for variant in self.purchaser_variants:
            pattern = rf'[（(]\s*{re.escape(variant)}\s*[）)]'
            if re.search(pattern, new_text):
                purchaser_name = info.get('purchaserName', '') or info.get('projectOwner', '')
                if purchaser_name:
                    replacement = f"（{purchaser_name}）"
                    new_text = re.sub(pattern, replacement, new_text)
                    self.logger.info(f"替换规则: {variant} → {purchaser_name}")
                    replacement_count += 1
        
        # 处理其他字段
        for field_key, variants in self.field_variants.items():
            for variant in variants:
                pattern = rf'[（(]\s*{re.escape(variant)}\s*[）)]'
                if re.search(pattern, new_text):
                    value = info.get(field_key, '')
                    if value:
                        replacement = f"（{value}）"
                        new_text = re.sub(pattern, replacement, new_text)
                        self.logger.info(f"替换规则: {variant} → {value}")
                        replacement_count += 1
        
        # 如果有替换，更新段落文本
        if replacement_count > 0:
            self._update_paragraph_text(paragraph, new_text)
            return True
        
        return False
    
    def _try_fill_rule(self, paragraph: Paragraph, info: Dict[str, Any]) -> bool:
        """
        尝试填空规则
        如：供应商名称：______ → 供应商名称：公司名
        """
        text = paragraph.text
        
        # 处理供应商名称类的填空
        for variant in self.company_name_variants:
            # 多种填空格式
            patterns = [
                rf'{re.escape(variant)}\s*[:：]\s*[_\s]*$',  # 冒号后跟下划线或空格
                rf'{re.escape(variant)}\s*[:：]\s*[_\s]+[。\.]',  # 冒号后跟下划线，以句号结束
                rf'{re.escape(variant)}\s+[_\s]+$',  # 空格后跟下划线
            ]
            
            for pattern in patterns:
                if re.search(pattern, text):
                    company_name = info.get('companyName', '')
                    if company_name:
                        # 保持原有格式，只替换占位符部分
                        new_text = re.sub(r'[_\s]+', company_name, text)
                        self._update_paragraph_text(paragraph, new_text)
                        self.logger.info(f"填空规则: {variant} 填入 {company_name}")
                        return True
        
        # 处理采购人信息的填空
        for variant in self.purchaser_variants:
            patterns = [
                rf'{re.escape(variant)}\s*[:：]\s*[_\s]*$',
                rf'{re.escape(variant)}\s*[:：]\s*[_\s]+[。\.]',
                rf'{re.escape(variant)}\s+[_\s]+$',
            ]
            
            for pattern in patterns:
                if re.search(pattern, text):
                    purchaser_name = info.get('purchaserName', '') or info.get('projectOwner', '')
                    if purchaser_name:
                        new_text = re.sub(r'[_\s]+', purchaser_name, text)
                        self._update_paragraph_text(paragraph, new_text)
                        self.logger.info(f"填空规则: {variant} 填入 {purchaser_name}")
                        return True
        
        # 处理其他字段的填空
        for field_key, variants in self.field_variants.items():
            for variant in variants:
                patterns = [
                    rf'{re.escape(variant)}\s*[:：]\s*[_\s]*$',
                    rf'{re.escape(variant)}\s*[:：]\s*[_\s]+[。\.]',
                    rf'{re.escape(variant)}\s+[_\s]+$',
                ]
                
                for pattern in patterns:
                    if re.search(pattern, text):
                        value = info.get(field_key, '')
                        if value:
                            new_text = re.sub(r'[_\s]+', value, text)
                            self._update_paragraph_text(paragraph, new_text)
                            self.logger.info(f"填空规则: {variant} 填入 {value}")
                            return True
        
        # 特殊处理日期
        date_pattern = r'日\s*期\s*[:：]?\s*[_\s]*年[_\s]*月[_\s]*日'
        if re.search(date_pattern, text):
            date_text = info.get('date', '')
            if date_text:
                # 格式化日期
                formatted_date = self._format_date(date_text)
                new_text = re.sub(date_pattern, f'日期：{formatted_date}', text)
                self._update_paragraph_text(paragraph, new_text)
                self.logger.info(f"日期填空: {formatted_date}")
                return True
        
        return False
    
    def _process_table(self, table: Table, info: Dict[str, Any]) -> Dict[str, Any]:
        """处理表格中的信息填写"""
        count = 0
        
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    if self._try_fill_rule(paragraph, info):
                        count += 1
                    elif self._try_replacement_rule(paragraph, info):
                        count += 1
        
        return {'count': count}
    
    def _format_date(self, date_str: str) -> str:
        """格式化日期字符串"""
        # 移除多余的空格
        date_str = re.sub(r'\s+', '', date_str)
        
        # 尝试匹配常见日期格式
        patterns = [
            (r'(\d{4})-(\d{1,2})-(\d{1,2})', r'\1年\2月\3日'),
            (r'(\d{4})/(\d{1,2})/(\d{1,2})', r'\1年\2月\3日'),
            (r'(\d{4})\.(\d{1,2})\.(\d{1,2})', r'\1年\2月\3日'),
        ]
        
        for pattern, replacement in patterns:
            if re.match(pattern, date_str):
                return re.sub(pattern, replacement, date_str)
        
        # 如果已经是中文格式，直接返回
        if '年' in date_str and '月' in date_str and '日' in date_str:
            return date_str
        
        # 默认返回原字符串
        return date_str
    
    def _update_paragraph_text(self, paragraph: Paragraph, new_text: str):
        """更新段落文本，保持格式"""
        # 保存第一个run的格式
        if paragraph.runs:
            first_run = paragraph.runs[0]
            # 保存格式属性
            font = first_run.font
            bold = font.bold
            italic = font.italic
            underline = font.underline
            font_size = font.size
            font_name = font.name
            
            # 清空段落
            paragraph.clear()
            
            # 添加新文本并恢复格式
            new_run = paragraph.add_run(new_text)
            if bold is not None:
                new_run.font.bold = bold
            if italic is not None:
                new_run.font.italic = italic
            if underline is not None:
                new_run.font.underline = underline
            if font_size:
                new_run.font.size = font_size
            if font_name:
                new_run.font.name = font_name
        else:
            # 如果没有runs，直接设置文本
            paragraph.text = new_text
    
    def _post_process(self, doc: Document):
        """后处理：清理多余的占位符和格式"""
        for paragraph in doc.paragraphs:
            text = paragraph.text
            
            # 清理多余的下划线
            text = re.sub(r'_{3,}', '', text)
            
            # 清理多余的空格（保留表格对齐所需的空格）
            if not re.search(r'\s{8,}', text):  # 不是表格式布局
                text = re.sub(r'\s{3,}', '  ', text)
            
            # 清理多余的冒号
            text = re.sub(r'[:：]{2,}', '：', text)
            
            # 标准化冒号
            text = re.sub(r':', '：', text)
            
            # 去除多余的年月日标识
            text = re.sub(r'(\d{4}年\d{1,2}月\d{1,2}日)\s*年\s*月\s*日', r'\1', text)
            
            if text != paragraph.text:
                self._update_paragraph_text(paragraph, text.strip())