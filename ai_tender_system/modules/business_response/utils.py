#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
商务应答共享工具模块 - 核心复用组件

提供所有business_response模块共享的工具函数和算法：
- 格式保持算法 (Format Preservation)
- 占位符处理工具 (Placeholder Tools)  
- 正则模式匹配引擎 (Pattern Engine)
- 字段映射管理器 (Field Mapper)
- 文本处理工具集 (Text Utils)

设计理念：通过集中管理共享算法，提升代码复用率40-50%，减少重复实现
"""

import re
from typing import Dict, List, Optional, Tuple, Any, Union
import logging

logger = logging.getLogger(__name__)

# =====================================
# 1. 字段映射管理器 (Field Mapper)
# =====================================

class FieldMapper:
    """统一的字段映射和转换规则管理"""
    
    # 公司信息字段映射 (直接映射)
    COMPANY_FIELD_MAPPING = {
        'companyName': '公司名称',
        'email': '邮箱', 
        'fax': '传真',
        'postalCode': '邮政编码',
        'establishDate': '成立时间',
        'businessScope': '经营范围',
        'legalRepresentative': '法定代表人',
        'authorizedPersonName': '被授权人姓名'
    }
    
    # 多源映射字段 (按优先级顺序)
    MULTI_SOURCE_MAPPING = {
        'address': ['address', 'registeredAddress', 'officeAddress'],
        'phone': ['fixedPhone', 'phone']
    }
    
    # 智能映射字段 (需上下文识别)
    SMART_MAPPING = {
        'authorizedPersonPosition': '被授权人职务',
        'legalRepresentativePosition': '法定代表人职位'
    }
    
    # 项目信息字段映射
    PROJECT_FIELD_MAPPING = {
        'projectName': '项目名称',
        'projectNumber': '项目编号', 
        'date': '日期',
        'purchaserName': '采购人名称'
    }
    
    @classmethod
    def get_field_value(cls, data: Dict[str, Any], field_key: str) -> Optional[str]:
        """
        获取字段值，支持多源映射和回退策略
        
        Args:
            data: 数据字典
            field_key: 字段键名
            
        Returns:
            字段值或None
        """
        # 直接映射
        if field_key in data and data[field_key]:
            return str(data[field_key]).strip()
            
        # 多源映射
        if field_key in cls.MULTI_SOURCE_MAPPING:
            for source_key in cls.MULTI_SOURCE_MAPPING[field_key]:
                if source_key in data and data[source_key]:
                    return str(data[source_key]).strip()
                    
        return None
    
    @classmethod
    def get_unified_field_mapping(cls) -> Dict[str, str]:
        """获取统一的字段映射字典"""
        mapping = {}
        mapping.update(cls.COMPANY_FIELD_MAPPING)
        mapping.update(cls.SMART_MAPPING)
        mapping.update(cls.PROJECT_FIELD_MAPPING)
        return mapping

# =====================================
# 2. 正则模式匹配引擎 (Pattern Engine)  
# =====================================

class PatternMatcher:
    """统一的模式匹配引擎"""
    
    # 供应商名称变体 (14种)
    SUPPLIER_NAME_VARIANTS = [
        '供应商名称', '供应商全称', '投标人名称', '公司名称',
        '单位名称', '应答人名称', '投标单位', '承包商名称',
        '服务商名称', '厂商名称', '乙方名称', '项目实施方',
        '响应人名称', '响应人全称'  # 新增：响应人名称变体
    ]
    
    # 括号替换模式
    BRACKET_PATTERNS = {
        'supplier': r'[（(]\s*(?:' + '|'.join(SUPPLIER_NAME_VARIANTS) + r')\s*[）)]',
        'purchaser': r'[（(]\s*采购人\s*[）)]',
        'project_name': r'[（(]\s*项目名称\s*[）)]',  
        'project_number': r'[（(]\s*(?:项目编号|招标编号|项目号)\s*[）)]',
        'combination': r'[（(]\s*([^）)]+)\s*[）)]'
    }
    
    # 填空模式 (6种)
    FILL_PATTERNS = {
        'underline': r'([^：:\s]+)\s*[：:]\s*_{2,}',  # 字段名：___
        'colon': r'([^：:\s]+)\s*[：:]\s*$',          # 字段名：
        'mixed': r'([^：:\s]+)\s*[：:]\s*[_\s]+',     # 字段名：___ (混合)
        'period': r'([^：:\s]+)\s*[：:]\s*_{2,}\s*[。.]', # 字段名：___.
        'space': r'([^：:\s]+)(?=\s+)(?![：:])',      # 字段名 (无冒号)
        'space_under': r'([^：:\s]+)\s+_{2,}'         # 字段名 ___
    }
    
    @classmethod
    def find_bracket_matches(cls, text: str, pattern_type: str) -> List[Tuple[str, int, int]]:
        """
        查找括号模式匹配
        
        Args:
            text: 要搜索的文本
            pattern_type: 模式类型 ('supplier', 'purchaser', etc.)
            
        Returns:
            匹配结果列表 [(匹配文本, 开始位置, 结束位置)]
        """
        if pattern_type not in cls.BRACKET_PATTERNS:
            return []
            
        pattern = cls.BRACKET_PATTERNS[pattern_type]
        matches = []
        
        for match in re.finditer(pattern, text):
            matches.append((match.group(0), match.start(), match.end()))
            
        return matches
    
    @classmethod
    def find_fill_matches(cls, text: str, field_name: str) -> List[Tuple[str, int, int, str]]:
        """
        查找填空模式匹配
        
        Args:
            text: 要搜索的文本
            field_name: 要匹配的字段名
            
        Returns:
            匹配结果列表 [(匹配文本, 开始位置, 结束位置, 模式类型)]
        """
        matches = []
        
        for pattern_name, pattern in cls.FILL_PATTERNS.items():
            # 为特定字段名自定义模式
            field_pattern = pattern.replace(r'([^：:\s]+)', re.escape(field_name))
            
            for match in re.finditer(field_pattern, text):
                matches.append((match.group(0), match.start(), match.end(), pattern_name))
                
        return matches

# =====================================
# 3. 格式保持算法 (Format Preservation)
# =====================================

class FormatPreserver:
    """文本格式保持算法集合"""
    
    @staticmethod
    def preserve_text_format(original: str, replacement: str, 
                           preserve_case: bool = True,
                           preserve_spacing: bool = True) -> str:
        """
        保持原文本格式的智能替换
        
        Args:
            original: 原始文本
            replacement: 替换内容  
            preserve_case: 是否保持大小写格式
            preserve_spacing: 是否保持空格格式
            
        Returns:
            格式化后的替换文本
        """
        if not original or not replacement:
            return replacement
            
        result = replacement
        
        # 保持大小写格式
        if preserve_case and original.strip():
            if original.isupper():
                result = result.upper()
            elif original.islower():
                result = result.lower()
            elif original.istitle():
                result = result.title()
        
        # 保持前后空格格式
        if preserve_spacing:
            leading_spaces = len(original) - len(original.lstrip())
            trailing_spaces = len(original) - len(original.rstrip())
            
            result = ' ' * leading_spaces + result.strip() + ' ' * trailing_spaces
            
        return result
    
    @staticmethod
    def extract_format_info(text: str) -> Dict[str, Any]:
        """
        提取文本格式信息
        
        Args:
            text: 输入文本
            
        Returns:
            格式信息字典
        """
        return {
            'leading_spaces': len(text) - len(text.lstrip()),
            'trailing_spaces': len(text) - len(text.rstrip()),
            'is_upper': text.isupper(),
            'is_lower': text.islower(),
            'is_title': text.istitle(),
            'has_punctuation': bool(re.search(r'[。，！？；：""''（）【】]', text)),
            'encoding': 'utf-8'
        }
    
    @staticmethod
    def apply_format_info(text: str, format_info: Dict[str, Any]) -> str:
        """
        应用格式信息到文本
        
        Args:
            text: 要格式化的文本
            format_info: 格式信息字典
            
        Returns:
            格式化后的文本
        """
        result = text.strip()
        
        # 应用大小写格式
        if format_info.get('is_upper', False):
            result = result.upper()
        elif format_info.get('is_lower', False):
            result = result.lower()
        elif format_info.get('is_title', False):
            result = result.title()
        
        # 应用空格格式
        leading = ' ' * format_info.get('leading_spaces', 0)
        trailing = ' ' * format_info.get('trailing_spaces', 0)
        
        return leading + result + trailing

# =====================================
# 4. 占位符处理工具 (Placeholder Tools)
# =====================================

class PlaceholderProcessor:
    """占位符检测和处理工具"""
    
    # 占位符模式
    PLACEHOLDER_PATTERNS = {
        'underscore': r'_{2,}',                    # 下划线占位符
        'space': r'\s{3,}',                       # 空格占位符
        'mixed': r'[_\s]{3,}',                    # 混合占位符
        'bracket': r'[（(][^）)]*[）)]',           # 括号占位符
        'punctuation': r'[。，：；]{2,}'           # 标点符号占位符
    }
    
    @classmethod
    def detect_placeholders(cls, text: str) -> List[Dict[str, Any]]:
        """
        检测文本中的占位符
        
        Args:
            text: 要检测的文本
            
        Returns:
            占位符信息列表
        """
        placeholders = []
        
        for placeholder_type, pattern in cls.PLACEHOLDER_PATTERNS.items():
            for match in re.finditer(pattern, text):
                placeholders.append({
                    'type': placeholder_type,
                    'text': match.group(0),
                    'start': match.start(),
                    'end': match.end(),
                    'length': len(match.group(0))
                })
        
        # 按位置排序        
        return sorted(placeholders, key=lambda x: x['start'])
    
    @classmethod
    def clean_placeholders(cls, text: str, replacement_map: Dict[str, str] = None) -> str:
        """
        清理文本中的占位符
        
        Args:
            text: 要清理的文本
            replacement_map: 替换映射，如 {'___': '内容', '   ': ' '}
            
        Returns:
            清理后的文本
        """
        result = text
        default_replacements = {
            '___': '',
            '    ': '  ',  # 多个空格替换为两个空格
            '。。': '。',   # 重复标点符号
            '，，': '，'
        }
        
        replacements = replacement_map or default_replacements
        
        for old, new in replacements.items():
            result = result.replace(old, new)
            
        return result

# =====================================
# 5. 文本处理工具集 (Text Utils)  
# =====================================

class TextUtils:
    """通用文本处理工具集合"""
    
    @staticmethod
    def normalize_whitespace(text: str, preserve_newlines: bool = True) -> str:
        """
        标准化空白字符
        
        Args:
            text: 输入文本
            preserve_newlines: 是否保持换行符
            
        Returns:
            标准化后的文本
        """
        if preserve_newlines:
            # 保持换行，但规范化其他空白字符
            lines = text.split('\n')
            normalized_lines = []
            for line in lines:
                # 将多个连续空格/制表符替换为单个空格
                normalized = re.sub(r'[ \t]+', ' ', line.strip())
                normalized_lines.append(normalized)
            return '\n'.join(normalized_lines)
        else:
            # 全部空白字符标准化为单个空格
            return re.sub(r'\s+', ' ', text.strip())
    
    @staticmethod
    def extract_field_value(pattern: str, text: str, group: int = 1) -> Optional[str]:
        """
        使用正则表达式提取字段值
        
        Args:
            pattern: 正则表达式模式
            text: 要搜索的文本
            group: 要提取的组号
            
        Returns:
            提取的值或None
        """
        match = re.search(pattern, text)
        if match and len(match.groups()) >= group:
            return match.group(group).strip()
        return None
    
    @staticmethod
    def safe_replace(text: str, old: str, new: str, count: int = -1) -> Tuple[str, int]:
        """
        安全的文本替换，返回替换次数
        
        Args:
            text: 原始文本
            old: 要替换的文本
            new: 新文本
            count: 最大替换次数，-1表示全部替换
            
        Returns:
            (替换后的文本, 实际替换次数)
        """
        if count == -1:
            replaced_count = text.count(old)
            result = text.replace(old, new)
        else:
            replaced_count = 0
            result = text
            for _ in range(count):
                if old in result:
                    result = result.replace(old, new, 1)
                    replaced_count += 1
                else:
                    break
        
        return result, replaced_count
    
    @staticmethod
    def find_context_around(text: str, target: str, context_length: int = 50) -> Dict[str, str]:
        """
        查找目标字符串周围的上下文
        
        Args:
            text: 要搜索的文本
            target: 目标字符串  
            context_length: 上下文长度
            
        Returns:
            上下文信息字典
        """
        index = text.find(target)
        if index == -1:
            return {'before': '', 'target': target, 'after': '', 'found': False}
            
        start = max(0, index - context_length)
        end = min(len(text), index + len(target) + context_length)
        
        return {
            'before': text[start:index],
            'target': target,
            'after': text[index + len(target):end],
            'found': True,
            'position': index
        }

# =====================================
# 6. 统一配置和常量
# =====================================

class BusinessResponseConstants:
    """商务应答模块常量定义"""
    
    # 日志配置
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # 文档处理常量
    MAX_FIELD_LENGTH = 1000
    DEFAULT_ENCODING = 'utf-8'
    
    # 性能优化常量
    BATCH_SIZE = 100
    CACHE_SIZE = 500

# 初始化日志
def setup_logging():
    """设置日志配置"""
    logging.basicConfig(
        level=logging.INFO,
        format=BusinessResponseConstants.LOG_FORMAT
    )

# 模块初始化时设置日志
setup_logging()

# =====================================
# 6. Word文档处理工具集 (Word Document Utils)
# =====================================

class WordDocumentUtils:
    """Word文档处理的专用工具集合"""
    
    @staticmethod
    def build_paragraph_text_map(paragraph):
        """
        构建段落的文本到Run映射
        
        Args:
            paragraph: Word段落对象
            
        Returns:
            tuple: (文本内容, Run列表, 字符到Run的映射列表)
        """
        full_text = ""
        runs = []
        char_to_run_map = []

        for run_idx, run in enumerate(paragraph.runs):
            run_text = run.text
            runs.append(run)

            # 记录每个字符属于哪个run
            for _ in range(len(run_text)):
                char_to_run_map.append(run_idx)

            full_text += run_text

        return full_text, runs, char_to_run_map
    
    @staticmethod
    def apply_replacement_to_runs(runs, char_to_run_map, match, replacement_text, logger=None, clean_format=True):
        """
        将替换应用到涉及的Run中，保持格式

        Args:
            runs: Run对象列表
            char_to_run_map: 字符到Run的映射
            match: 匹配字典，包含start、end、text
            replacement_text: 替换文本
            logger: 日志对象
            clean_format: 是否清理格式（移除下划线/删除线/高亮/背景色），默认True

        Returns:
            bool: 是否替换成功
        """
        start_pos = match['start']
        end_pos = match['end']

        # 找出涉及的Run范围
        if start_pos >= len(char_to_run_map) or end_pos > len(char_to_run_map):
            if logger:
                logger.warning(f"警告：匹配位置超出范围，跳过 {match['text']}")
            return False

        start_run_idx = char_to_run_map[start_pos]
        end_run_idx = char_to_run_map[end_pos - 1] if end_pos > 0 else start_run_idx

        if logger:
            logger.debug(f"匹配范围：Run {start_run_idx} 到 Run {end_run_idx}")

        # 构建每个Run的字符偏移映射
        run_char_offsets = {}
        current_offset = 0
        for i, run in enumerate(runs):
            run_char_offsets[i] = current_offset
            current_offset += len(run.text)

        # 计算需要修改的Run及其新内容
        for run_idx in range(start_run_idx, end_run_idx + 1):
            if run_idx >= len(runs):
                continue

            run = runs[run_idx]
            run_start_in_full = run_char_offsets[run_idx]

            # 计算这个Run中需要替换的部分
            replace_start_in_run = max(0, start_pos - run_start_in_full)
            replace_end_in_run = min(len(run.text), end_pos - run_start_in_full)

            old_run_text = run.text

            if run_idx == start_run_idx and run_idx == end_run_idx:
                # 替换完全在一个Run内
                new_run_text = (old_run_text[:replace_start_in_run] +
                              replacement_text +
                              old_run_text[replace_end_in_run:])
            elif run_idx == start_run_idx:
                # 开始Run：保留前缀，加上替换文本
                new_run_text = old_run_text[:replace_start_in_run] + replacement_text
            elif run_idx == end_run_idx:
                # 结束Run：只保留后缀
                new_run_text = old_run_text[replace_end_in_run:]
            else:
                # 中间Run：完全清空
                new_run_text = ""

            run.text = new_run_text

            # 🆕 格式清理：移除占位符格式，保留基本样式
            if clean_format and new_run_text:  # 只清理有内容的Run
                try:
                    # 移除下划线、删除线、高亮、背景色
                    run.font.underline = None
                    run.font.strike = None
                    if hasattr(run.font, 'highlight_color'):
                        run.font.highlight_color = None
                    # 保留：字体名称、大小、粗体、斜体、颜色
                    if logger:
                        logger.debug(f"  清理Run {run_idx}格式：移除下划线/删除线/高亮")
                except Exception as e:
                    if logger:
                        logger.debug(f"  清理Run {run_idx}格式时出现异常（可忽略）: {e}")

            if logger:
                logger.debug(f"Run {run_idx}: '{old_run_text}' -> '{new_run_text}'")

        return True
    
    @staticmethod
    def find_cross_run_matches(full_text: str, pattern: str):
        """
        在跨Run文本中查找模式匹配
        
        Args:
            full_text: 完整的段落文本
            pattern: 正则表达式模式
            
        Returns:
            list: 匹配结果列表，每个包含start、end、text
        """
        matches = []
        for match in re.finditer(pattern, full_text):
            matches.append({
                'start': match.start(),
                'end': match.end(),
                'text': match.group(),
                'groups': match.groups() if match.groups() else ()
            })
        return matches
    
    @staticmethod
    def copy_font_format(source_run, target_run):
        """
        复制字体格式从源Run到目标Run
        
        Args:
            source_run: 源Run对象
            target_run: 目标Run对象
        """
        try:
            # 基本字体属性
            if source_run.font.name:
                target_run.font.name = source_run.font.name
            if source_run.font.size:
                target_run.font.size = source_run.font.size
                
            # 字体样式
            target_run.font.bold = source_run.font.bold
            target_run.font.italic = source_run.font.italic
            target_run.font.underline = source_run.font.underline
            
            # 字体颜色
            if source_run.font.color:
                target_run.font.color.rgb = source_run.font.color.rgb
                
        except Exception as e:
            logger.debug(f"字体格式复制时出现异常: {e}")
    
    @staticmethod
    def analyze_paragraph_format(paragraph, pattern: str):
        """
        分析段落中目标模式的格式信息
        
        Args:
            paragraph: Word段落对象
            pattern: 要分析的模式
            
        Returns:
            dict: 格式分析结果
        """
        full_text, runs, char_to_run_map = WordDocumentUtils.build_paragraph_text_map(paragraph)
        matches = WordDocumentUtils.find_cross_run_matches(full_text, pattern)
        
        if not matches:
            return None
            
        match = matches[0]  # 取第一个匹配
        start_pos = match['start']
        
        if start_pos < len(char_to_run_map):
            run_idx = char_to_run_map[start_pos]
            if run_idx < len(runs):
                template_run = runs[run_idx]
                return {
                    'font_name': template_run.font.name,
                    'font_size': template_run.font.size,
                    'bold': template_run.font.bold,
                    'italic': template_run.font.italic,
                    'underline': template_run.font.underline,
                    'run_index': run_idx
                }
        
        return None
    
    @staticmethod
    def precise_replace(paragraph, pattern: str, replacement: str, logger=None) -> bool:
        """
        在段落中精确替换文本，保持格式
        
        Args:
            paragraph: Word段落对象
            pattern: 正则表达式模式
            replacement: 替换文本
            logger: 日志对象
            
        Returns:
            bool: 是否替换成功
        """
        try:
            full_text, runs, char_to_run_map = WordDocumentUtils.build_paragraph_text_map(paragraph)
            
            if not full_text:
                return False
                
            matches = WordDocumentUtils.find_cross_run_matches(full_text, pattern)
            
            if not matches:
                return False
            
            # 从后往前替换，避免位置偏移问题
            for match in reversed(matches):
                success = WordDocumentUtils.apply_replacement_to_runs(
                    runs, char_to_run_map, match, replacement, logger
                )
                if not success:
                    return False
            
            if logger:
                logger.debug(f"精确替换成功: '{pattern}' -> '{replacement}'")
            
            return True
            
        except Exception as e:
            if logger:
                logger.error(f"精确替换时出现错误: {e}")
            return False

# =====================================
# 7. 智能字段检测器 (Smart Field Detector)
# =====================================

class SmartFieldDetector:
    """智能字段检测和上下文分析"""
    
    # 职位上下文关键词
    POSITION_CONTEXT_KEYWORDS = {
        'authorized_person': ['被授权人', '授权代表', '代表人', '项目经理', '负责人'],
        'legal_representative': ['法定代表人', '法人代表', '法人', '董事长', '总经理'],
        'general': ['职务', '职位', '岗位', '职称']
    }
    
    @classmethod
    def detect_position_context(cls, paragraph_text: str) -> str:
        """
        检测职位字段的上下文，判断是被授权人职务还是法定代表人职位
        
        Args:
            paragraph_text: 段落文本
            
        Returns:
            str: 'authorized_person', 'legal_representative', 或 'general'
        """
        text_lower = paragraph_text.lower()
        
        # 检查被授权人相关关键词
        for keyword in cls.POSITION_CONTEXT_KEYWORDS['authorized_person']:
            if keyword in text_lower:
                return 'authorized_person'
        
        # 检查法定代表人相关关键词
        for keyword in cls.POSITION_CONTEXT_KEYWORDS['legal_representative']:
            if keyword in text_lower:
                return 'legal_representative'
                
        return 'general'
    
    @classmethod
    def should_try_field_in_paragraph(cls, paragraph_text: str, field_variants: list) -> bool:
        """
        预检查段落是否可能包含相关字段（原始版本逻辑）

        Args:
            paragraph_text: 段落文本
            field_variants: 字段变体列表

        Returns:
            bool: 是否值得尝试处理这个段落
        """
        import logging
        logger = logging.getLogger("ai_tender_system.business_response")

        # 注意：不要strip()，因为需要保留空格来检测空格格式
        text = paragraph_text

        # 第1步：空段落检查
        if not text or not text.strip():
            return False

        # 第2步：字段相关性检查 - 必须包含字段变体
        contains_field = any(variant in text for variant in field_variants)
        if not contains_field:
            return False

        # 第3步：格式标识符检查 - 放宽检查条件以支持更多格式
        field_indicators = [
            r'[:：]',           # 冒号格式：地址：、电话：
            r'[（(].*[）)]',     # 括号格式：（地址）、（公章）
            r'_+',              # 下划线格式：___
            r'\s{3,}',          # 多空格格式：传真
            r'致\s*[：:]',       # 致：格式
            r'[。，,\.]',        # 标点符号格式
            r'\d',              # 包含数字
            r'[年月日]',         # 日期格式
        ]
        has_format = any(re.search(indicator, text) for indicator in field_indicators)

        # 放宽条件：如果段落较短且包含字段名，也允许处理
        is_short_with_field = len(text.strip()) < 100 and contains_field

        if not has_format and not is_short_with_field:
            logger.debug(f"❌ [SmartFieldDetector] 段落无格式标识符且非短段落: '{text[:50]}...'")
            return False

        # 简化的调试信息
        logger.debug(f"✅ [SmartFieldDetector] 段落通过检查: 包含字段变体且有格式标识符 - '{text[:50]}...'")
        return True

# =====================================
# 8. 数据字段规范化工具 (Data Normalization)
# =====================================

def normalize_data_keys(data: Dict[str, Any], logger=None) -> Dict[str, Any]:
    """
    规范化数据字段名（统一命名规则）

    支持两种命名风格的转换：
    1. 驼峰命名 (fixedPhone, officeAddress) → 标准字段 (phone, address)
    2. 下划线命名 (fixed_phone, office_address) → 标准字段 (phone, address)

    用途：确保从数据库读取的数据能被smart_filler和table_processor正确识别

    Args:
        data: 原始数据字典
        logger: 日志对象（可选）

    Returns:
        规范化后的数据字典
    """
    normalized = data.copy()

    # 字段名映射表（旧名 → 新名）
    key_mappings = {
        # 驼峰命名映射
        'fixedPhone': 'phone',
        'mobilePhone': 'mobile',
        'contactPhone': 'phone',
        'registeredAddress': 'address',
        'officeAddress': 'address',

        # 下划线命名映射（数据库原始字段名）
        'fixed_phone': 'phone',
        'mobile_phone': 'mobile',
        'contact_phone': 'phone',
        'postal_code': 'postalCode',
        'registered_address': 'address',
        'office_address': 'address',
        'authorized_person_id': 'authorizedPersonId',  # 被授权人身份证号
    }

    # 应用单键映射
    for old_key, new_key in key_mappings.items():
        if old_key in normalized and new_key not in normalized:
            normalized[new_key] = normalized[old_key]
            if logger:
                logger.debug(f"键名映射: {old_key} → {new_key}")

    # 多源映射（按优先级）
    multi_source_mappings = {
        'address': ['address', 'officeAddress', 'registeredAddress',
                    'office_address', 'registered_address'],
        'phone': ['phone', 'fixedPhone', 'mobilePhone',
                  'fixed_phone', 'mobile_phone'],
    }

    for target_key, source_keys in multi_source_mappings.items():
        if target_key not in normalized or not normalized.get(target_key):
            for source_key in source_keys:
                if source_key in normalized and normalized.get(source_key):
                    normalized[target_key] = normalized[source_key]
                    if logger:
                        logger.debug(f"多源映射: {source_key} → {target_key}")
                    break

    return normalized

# 导出主要类和函数
__all__ = [
    'FieldMapper',
    'PatternMatcher',
    'FormatPreserver',
    'PlaceholderProcessor',
    'TextUtils',
    'WordDocumentUtils',
    'SmartFieldDetector',
    'BusinessResponseConstants',
    'normalize_data_keys'  # 新增
]