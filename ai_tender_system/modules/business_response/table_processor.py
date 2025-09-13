#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
表格处理模块 - 处理商务应答模板中的表格填写
"""

import re
from typing import Dict, Any, List, Optional
from docx import Document
from docx.table import Table, _Cell

# 导入公共模块
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
from common import get_module_logger

class TableProcessor:
    """表格处理器"""
    
    def __init__(self):
        self.logger = get_module_logger("table_processor")
        
        # 表格中的关键字段映射
        self.table_field_mapping = {
            '供应商名称': 'companyName',
            '投标人名称': 'companyName',
            '公司名称': 'companyName',
            '法定代表人': 'legalRepresentative',
            '注册资本': 'registeredCapital',
            '成立日期': 'establishDate',
            '统一社会信用代码': 'socialCreditCode',
            '注册地址': 'registeredAddress',
            '联系地址': 'address',
            '联系人': 'contactPerson',
            '联系电话': 'phone',
            '电子邮箱': 'email',
            '传真': 'fax',
            '开户银行': 'bankName',
            '银行账号': 'bankAccount',
            '税号': 'taxNumber',
            '资质等级': 'qualification',
            '项目名称': 'projectName',
            '项目编号': 'projectNumber',
            '投标报价': 'bidPrice',
            '交货期': 'deliveryTime',
            '质保期': 'warrantyPeriod'
        }
    
    def process_tables(self, doc: Document, company_info: Dict[str, Any], 
                       project_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理文档中的所有表格
        
        Args:
            doc: Word文档对象
            company_info: 公司信息
            project_info: 项目信息
            
        Returns:
            处理统计信息
        """
        stats = {
            'tables_processed': 0,
            'cells_filled': 0,
            'fields_matched': []
        }
        
        # 合并所有信息
        all_info = {**company_info, **project_info}
        
        for table_idx, table in enumerate(doc.tables):
            self.logger.info(f"处理表格 #{table_idx + 1}")
            result = self._process_single_table(table, all_info)
            
            if result['cells_filled'] > 0:
                stats['tables_processed'] += 1
                stats['cells_filled'] += result['cells_filled']
                stats['fields_matched'].extend(result['fields_matched'])
        
        self.logger.info(f"表格处理完成: 处理了{stats['tables_processed']}个表格，"
                        f"填充了{stats['cells_filled']}个单元格")
        
        return stats
    
    def _process_single_table(self, table: Table, info: Dict[str, Any]) -> Dict[str, Any]:
        """处理单个表格"""
        result = {
            'cells_filled': 0,
            'fields_matched': []
        }
        
        # 分析表格结构
        table_type = self._analyze_table_structure(table)
        
        if table_type == 'key_value':
            # 键值对表格（左边是字段名，右边是值）
            result = self._process_key_value_table(table, info)
        elif table_type == 'header_data':
            # 表头-数据表格（第一行是表头，后续行是数据）
            result = self._process_header_data_table(table, info)
        elif table_type == 'mixed':
            # 混合型表格
            result = self._process_mixed_table(table, info)
        
        return result
    
    def _analyze_table_structure(self, table: Table) -> str:
        """分析表格结构类型"""
        if not table.rows:
            return 'empty'
        
        # 检查是否为键值对表格
        if len(table.columns) == 2:
            # 检查第一列是否包含字段名
            first_col_texts = [row.cells[0].text.strip() for row in table.rows]
            field_count = sum(1 for text in first_col_texts 
                            if any(field in text for field in self.table_field_mapping.keys()))
            if field_count > len(table.rows) * 0.5:
                return 'key_value'
        
        # 检查是否为表头-数据表格
        if len(table.rows) > 1:
            first_row_texts = [cell.text.strip() for cell in table.rows[0].cells]
            field_count = sum(1 for text in first_row_texts 
                            if any(field in text for field in self.table_field_mapping.keys()))
            if field_count > len(table.columns) * 0.3:
                return 'header_data'
        
        return 'mixed'
    
    def _process_key_value_table(self, table: Table, info: Dict[str, Any]) -> Dict[str, Any]:
        """处理键值对类型的表格"""
        result = {
            'cells_filled': 0,
            'fields_matched': []
        }
        
        for row in table.rows:
            if len(row.cells) >= 2:
                key_cell = row.cells[0]
                value_cell = row.cells[1]
                
                key_text = key_cell.text.strip()
                
                # 查找匹配的字段
                for field_name, field_key in self.table_field_mapping.items():
                    if field_name in key_text:
                        value = info.get(field_key, '')
                        if value and self._should_fill_cell(value_cell):
                            self._fill_cell(value_cell, str(value))
                            result['cells_filled'] += 1
                            result['fields_matched'].append(field_name)
                            self.logger.debug(f"填充字段: {field_name} = {value}")
                            break
        
        return result
    
    def _process_header_data_table(self, table: Table, info: Dict[str, Any]) -> Dict[str, Any]:
        """处理表头-数据类型的表格"""
        result = {
            'cells_filled': 0,
            'fields_matched': []
        }
        
        if len(table.rows) < 2:
            return result
        
        # 分析表头
        header_row = table.rows[0]
        column_mapping = {}
        
        for col_idx, cell in enumerate(header_row.cells):
            header_text = cell.text.strip()
            for field_name, field_key in self.table_field_mapping.items():
                if field_name in header_text:
                    column_mapping[col_idx] = field_key
                    break
        
        # 填充数据行
        for row_idx in range(1, len(table.rows)):
            row = table.rows[row_idx]
            for col_idx, field_key in column_mapping.items():
                if col_idx < len(row.cells):
                    value = info.get(field_key, '')
                    if value and self._should_fill_cell(row.cells[col_idx]):
                        self._fill_cell(row.cells[col_idx], str(value))
                        result['cells_filled'] += 1
                        
                        # 记录字段名
                        for field_name, key in self.table_field_mapping.items():
                            if key == field_key:
                                result['fields_matched'].append(field_name)
                                break
        
        return result
    
    def _process_mixed_table(self, table: Table, info: Dict[str, Any]) -> Dict[str, Any]:
        """处理混合型表格"""
        result = {
            'cells_filled': 0,
            'fields_matched': []
        }
        
        # 遍历所有单元格，查找并填充
        for row in table.rows:
            for cell_idx, cell in enumerate(row.cells):
                cell_text = cell.text.strip()
                
                # 检查是否包含字段名和占位符
                for field_name, field_key in self.table_field_mapping.items():
                    if field_name in cell_text:
                        # 检查是否有占位符
                        if re.search(r'[_\s]{3,}|[:：]\s*$', cell_text):
                            value = info.get(field_key, '')
                            if value:
                                # 替换占位符
                                new_text = self._replace_placeholder(cell_text, str(value))
                                self._update_cell_text(cell, new_text)
                                result['cells_filled'] += 1
                                result['fields_matched'].append(field_name)
                                break
                        # 检查下一个单元格是否为空（可能是值单元格）
                        elif cell_idx + 1 < len(row.cells):
                            next_cell = row.cells[cell_idx + 1]
                            if self._should_fill_cell(next_cell):
                                value = info.get(field_key, '')
                                if value:
                                    self._fill_cell(next_cell, str(value))
                                    result['cells_filled'] += 1
                                    result['fields_matched'].append(field_name)
                                    break
        
        return result
    
    def _should_fill_cell(self, cell: _Cell) -> bool:
        """判断单元格是否应该被填充"""
        text = cell.text.strip()
        
        # 空单元格或只有占位符的单元格
        if not text or re.match(r'^[_\s]*$', text):
            return True
        
        # 包含占位符的单元格
        if re.search(r'_{3,}', text):
            return True
        
        return False
    
    def _fill_cell(self, cell: _Cell, value: str):
        """填充单元格"""
        # 清空单元格
        for paragraph in cell.paragraphs:
            paragraph.clear()
        
        # 添加新值
        if cell.paragraphs:
            cell.paragraphs[0].add_run(value)
        else:
            cell.add_paragraph(value)
    
    def _update_cell_text(self, cell: _Cell, new_text: str):
        """更新单元格文本，保持格式"""
        if cell.paragraphs and cell.paragraphs[0].runs:
            # 保存第一个run的格式
            first_run = cell.paragraphs[0].runs[0]
            font_properties = {
                'bold': first_run.font.bold,
                'italic': first_run.font.italic,
                'underline': first_run.font.underline,
                'size': first_run.font.size,
                'name': first_run.font.name
            }
            
            # 清空并重新设置文本
            cell.paragraphs[0].clear()
            new_run = cell.paragraphs[0].add_run(new_text)
            
            # 恢复格式
            for prop, value in font_properties.items():
                if value is not None:
                    setattr(new_run.font, prop, value)
        else:
            # 直接设置文本
            if cell.paragraphs:
                cell.paragraphs[0].text = new_text
            else:
                cell.add_paragraph(new_text)
    
    def _replace_placeholder(self, text: str, value: str) -> str:
        """替换文本中的占位符"""
        # 替换下划线占位符
        text = re.sub(r'_{3,}', value, text)
        
        # 替换冒号后的空白
        text = re.sub(r'([:：])\s*$', f'\\1{value}', text)
        
        # 替换连续空格
        if re.search(r'\s{3,}', text):
            text = re.sub(r'\s{3,}', value, text)
        
        return text