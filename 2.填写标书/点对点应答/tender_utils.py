#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
标书处理工具函数集
包含日期格式化、文本处理等独立工具函数
"""

import re
import logging
from datetime import datetime
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


def format_chinese_date(date_str: str) -> str:
    """
    将英文日期格式(YYYY-MM-DD)转换为中文日期格式(YYYY年M月D日)
    例如：2000-04-21 -> 2000年4月21日
    
    Args:
        date_str: 输入的日期字符串，格式为YYYY-MM-DD
        
    Returns:
        str: 中文格式的日期字符串
    """
    if not date_str or not isinstance(date_str, str):
        return ''
    
    try:
        # 尝试多种日期格式
        for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%Y.%m.%d', '%Y年%m月%d日']:
            try:
                dt = datetime.strptime(date_str.strip(), fmt)
                # 转换为中文格式，去掉月份和日期的前导零
                return f"{dt.year}年{dt.month}月{dt.day}日"
            except ValueError:
                continue
        
        # 如果所有格式都不匹配，返回原始字符串
        return date_str
    except Exception as e:
        logger.warning(f"日期格式转换失败: {e}")
        return date_str


def extract_project_info_field(project_info: dict, field_name: str) -> str:
    """
    从项目信息字典中提取指定字段的值
    
    Args:
        project_info: 项目信息字典
        field_name: 要提取的字段名
        
    Returns:
        str: 字段值，如果不存在则返回空字符串
    """
    if not project_info or not isinstance(project_info, dict):
        return ""
    
    # 字段映射关系
    field_mapping = {
        'tenderer': ['tenderer', '采购人', '招标人'],
        'bidding_method': ['bidding_method', '招标方式', '采购方式'],
        'agency': ['agency', '代理机构', '招标代理'],
        'project_name': ['project_name', '项目名称'],
        'project_number': ['project_number', '项目编号', 'tender_no']
    }
    
    # 获取可能的字段名列表
    possible_fields = field_mapping.get(field_name, [field_name])
    
    # 尝试获取字段值
    for field in possible_fields:
        if field in project_info:
            value = project_info[field]
            if value and str(value).strip():
                return str(value).strip()
    
    return ""


def clean_placeholder_keep_separator(content: str, has_next_label: bool) -> str:
    """
    清理占位符但保留分隔符
    
    Args:
        content: 要清理的内容
        has_next_label: 是否有下一个标签
        
    Returns:
        str: 清理后的内容
    """
    if not content:
        return content
    
    # 定义占位符模式
    placeholder_patterns = [
        r'[_\-\u2014]+',  # 下划线、短横线、长横线
        r'[\s]{3,}',      # 3个或以上空格
        r'[＿]+',         # 全角下划线
        r'[——]+',         # 中文破折号
    ]
    
    # 逐个替换占位符
    result = content
    for pattern in placeholder_patterns:
        if has_next_label:
            # 如果有下一个标签，保留一个空格作为分隔
            result = re.sub(pattern, ' ', result)
        else:
            # 如果没有下一个标签，完全删除占位符
            result = re.sub(pattern, '', result)
    
    # 清理多余的空格
    result = re.sub(r'\s+', ' ', result)
    
    return result.strip()


def get_replacement_type(pattern_str: str) -> str:
    """
    根据模式字符串判断替换类型
    
    Args:
        pattern_str: 正则表达式模式字符串
        
    Returns:
        str: 替换类型，如 'company_name', 'project_name', 'tender_number'
    """
    if not pattern_str:
        return 'unknown'
    
    # 公司名称相关关键词
    company_keywords = [
        '供应商名称', '供应商全称', '投标人名称', 
        '公司名称', '单位名称', '采购人', 
        '供应商住址', '供应商地址', '公司地址', '注册地址'
    ]
    
    # 项目名称相关关键词
    project_keywords = ['项目名称']
    
    # 项目编号相关关键词
    number_keywords = ['采购编号', '招标编号', '项目编号', '编号']
    
    # 检查模式中包含的关键词
    for keyword in company_keywords:
        if keyword in pattern_str:
            return 'company_name'
    
    for keyword in project_keywords:
        if keyword in pattern_str:
            return 'project_name'
    
    for keyword in number_keywords:
        if keyword in pattern_str:
            return 'tender_number'
    
    return 'unknown'


def normalize_text(text: str) -> str:
    """
    标准化文本，去除多余空格和特殊字符
    
    Args:
        text: 输入文本
        
    Returns:
        str: 标准化后的文本
    """
    if not text:
        return ""
    
    # 替换全角空格为半角空格
    text = text.replace('\u3000', ' ')
    text = text.replace('\u00A0', ' ')  # 不间断空格
    
    # 替换制表符为空格
    text = text.replace('\t', ' ')
    
    # 替换多个连续空格为单个空格
    text = re.sub(r'\s+', ' ', text)
    
    # 去除首尾空格
    return text.strip()


def is_placeholder(text: str) -> bool:
    """
    判断文本是否为占位符
    
    Args:
        text: 要检查的文本
        
    Returns:
        bool: 如果是占位符返回True，否则返回False
    """
    if not text:
        return False
    
    # 占位符模式
    placeholder_patterns = [
        r'^[_\-\u2014]+$',    # 只包含下划线、短横线、长横线
        r'^[\s]+$',           # 只包含空格
        r'^[＿]+$',           # 只包含全角下划线
        r'^[——]+$',           # 只包含中文破折号
        r'^[\.]+$',           # 只包含点
    ]
    
    # 检查是否匹配任何占位符模式
    for pattern in placeholder_patterns:
        if re.match(pattern, text):
            return True
    
    return False


def merge_adjacent_spaces(text: str) -> str:
    """
    合并相邻的空格，但保留必要的单个空格
    
    Args:
        text: 输入文本
        
    Returns:
        str: 处理后的文本
    """
    if not text:
        return ""
    
    # 合并多个空格为单个空格
    result = re.sub(r' {2,}', ' ', text)
    
    # 处理中英文之间的空格（可选，根据需要启用）
    # result = re.sub(r'([\u4e00-\u9fa5])\s+([\u4e00-\u9fa5])', r'\1\2', result)
    
    return result