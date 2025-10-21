#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能文档填写器 - SmartDocumentFiller
基于规则引擎和模式识别的通用文档填写解决方案

特性：
1. 自动识别5种填空模式
2. 智能字段映射和变体识别
3. 保持原文档格式
4. 详细的匹配和填充日志
5. 模块化、可扩展的设计

作者：AI Tender System
版本：2.0
日期：2025-10-19
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from docx import Document
from docx.text.paragraph import Paragraph

# 导入公共模块
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from common import get_module_logger

# 导入Word文档工具
from .utils import WordDocumentUtils


class SmartDocumentFiller:
    """智能文档填写器主类"""

    def __init__(self):
        self.logger = get_module_logger("smart_filler")

        # 初始化子模块
        self.pattern_matcher = PatternMatcher()
        self.field_recognizer = FieldRecognizer()
        self.content_filler = ContentFiller(self.logger)

        self.logger.info("智能文档填写器初始化完成")

    def fill_document(self,
                     doc: Document,
                     data: Dict[str, Any]) -> Dict[str, Any]:
        """
        填写文档主方法

        Args:
            doc: Word文档对象
            data: 数据字典，包含所有需要填充的信息

        Returns:
            填充统计信息
        """
        # 标准化数据键名（兼容旧数据格式）
        data = self._normalize_data_keys(data)

        stats = {
            'total_filled': 0,
            'pattern_counts': {},
            'unfilled_fields': [],
            'errors': []
        }

        self.logger.info("="*60)
        self.logger.info("开始智能文档填充")
        self.logger.info(f"可用数据字段: {list(data.keys())}")
        self.logger.info("="*60)

        # 处理所有段落
        for para_idx, paragraph in enumerate(doc.paragraphs):
            if not paragraph.text.strip():
                continue

            # 匹配并填充
            result = self._process_paragraph(paragraph, data, para_idx)

            # 更新统计
            if result['filled']:
                stats['total_filled'] += 1
                pattern = result['pattern']
                stats['pattern_counts'][pattern] = stats['pattern_counts'].get(pattern, 0) + 1
            elif result['unfilled_fields']:
                stats['unfilled_fields'].extend(result['unfilled_fields'])

            if result['errors']:
                stats['errors'].extend(result['errors'])

        # 输出统计报告
        self._print_stats(stats)

        return stats

    def _process_paragraph(self,
                          paragraph: Paragraph,
                          data: Dict[str, Any],
                          para_idx: int) -> Dict[str, Any]:
        """
        处理单个段落

        Returns:
            {
                'filled': bool,
                'pattern': str,
                'unfilled_fields': list,
                'errors': list
            }
        """
        text = paragraph.text.strip()
        result = {
            'filled': False,
            'pattern': None,
            'unfilled_fields': [],
            'errors': []
        }

        self.logger.debug(f"段落#{para_idx}: {text[:80]}")

        # 2. 按优先级尝试填充
        # 注意：每次填充后重新检测模式，因为文本已改变，位置信息会失效
        filled_patterns = []

        for pattern_type in ['combo', 'bracket', 'date', 'colon']:
            try:
                # 每次都重新检测当前文本的模式
                # 注意：不要strip，因为位置信息必须与paragraph.text一致
                text = paragraph.text
                patterns = self.pattern_matcher.detect_patterns(text)

                if pattern_type not in patterns or not patterns[pattern_type]:
                    continue

                self.logger.debug(f"  尝试 {pattern_type} 模式，检测到 {len(patterns[pattern_type])} 个匹配")

                # date模式特殊处理：避免与colon冲突
                if pattern_type == 'colon' and 'date' in filled_patterns:
                    # 如果date已经填充，跳过colon中的日期字段
                    colon_has_date = any('日期' in m['field'] for m in patterns['colon'])
                    if colon_has_date:
                        self.logger.debug("  跳过colon模式中的日期字段（已由date模式处理）")
                        patterns['colon'] = [m for m in patterns['colon'] if '日期' not in m['field']]
                        if not patterns['colon']:
                            continue

                filled = self._fill_by_pattern(
                    paragraph,
                    text,
                    pattern_type,
                    patterns[pattern_type],
                    data
                )

                if filled:
                    filled_patterns.append(pattern_type)
                    self.logger.info(f"  ✅ 使用 {pattern_type} 模式成功填充")

            except Exception as e:
                error_msg = f"段落#{para_idx} 填充失败({pattern_type}): {e}"
                self.logger.error(error_msg)
                result['errors'].append(error_msg)

        # 如果有任何模式填充成功
        if filled_patterns:
            result['filled'] = True
            result['pattern'] = '+'.join(filled_patterns)  # 记录使用了哪些模式
            return result

        # 3. 记录未填充的字段
        if patterns:
            for pattern_type, matches in patterns.items():
                for match in matches:
                    result['unfilled_fields'].append({
                        'para_idx': para_idx,
                        'text': text[:100],
                        'pattern': pattern_type,
                        'field': match
                    })

        return result

    def _fill_by_pattern(self,
                        paragraph: Paragraph,
                        text: str,
                        pattern_type: str,
                        matches: List,
                        data: Dict[str, Any]) -> bool:
        """根据模式类型填充"""

        if pattern_type == 'combo':
            return self.content_filler.fill_combo_field(paragraph, text, matches, data)

        elif pattern_type == 'bracket':
            return self.content_filler.fill_bracket_field(paragraph, text, matches, data)

        elif pattern_type == 'colon':
            return self.content_filler.fill_colon_field(paragraph, text, matches, data)

        elif pattern_type == 'date':
            return self.content_filler.fill_date_field(paragraph, text, matches, data)

        return False

    def _normalize_data_keys(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        标准化数据键名，兼容旧格式

        将旧的字段名映射到新的标准字段名:
        - fixedPhone -> phone
        - registeredAddress -> address
        - officeAddress -> address
        等等
        """
        normalized = data.copy()

        # 字段名映射表（旧名 -> 新名）
        # 按优先级顺序：先检查高优先级的源
        key_mappings = {
            'fixedPhone': 'phone',
            'mobilePhone': 'mobile',
            'contactPhone': 'phone',
        }

        # 多源映射（按优先级）
        multi_source_mappings = {
            'address': ['address', 'officeAddress', 'registeredAddress'],  # 优先使用officeAddress
            'phone': ['phone', 'fixedPhone', 'mobilePhone'],
        }

        # 应用单键映射
        for old_key, new_key in key_mappings.items():
            if old_key in normalized and new_key not in normalized:
                normalized[new_key] = normalized[old_key]
                self.logger.debug(f"键名映射: {old_key} -> {new_key}")

        # 应用多源映射（找到第一个有值的源）
        for target_key, source_keys in multi_source_mappings.items():
            if target_key not in normalized or not normalized.get(target_key):
                for source_key in source_keys:
                    if source_key in normalized and normalized.get(source_key):
                        normalized[target_key] = normalized[source_key]
                        self.logger.debug(f"多源映射: {source_key} -> {target_key} (值: {normalized[target_key]})")
                        break

        return normalized

    def _print_stats(self, stats: Dict[str, Any]):
        """打印统计报告"""
        self.logger.info("="*60)
        self.logger.info("填充统计报告")
        self.logger.info("="*60)
        self.logger.info(f"总填充数: {stats['total_filled']}")

        if stats['pattern_counts']:
            self.logger.info("按模式统计:")
            for pattern, count in stats['pattern_counts'].items():
                self.logger.info(f"  - {pattern}: {count}")

        if stats['unfilled_fields']:
            self.logger.warning(f"未填充字段数: {len(stats['unfilled_fields'])}")
            for uf in stats['unfilled_fields'][:10]:  # 只显示前10个
                self.logger.warning(f"  - 段落#{uf['para_idx']}: {uf['field']}")

        if stats['errors']:
            self.logger.error(f"错误数: {len(stats['errors'])}")
            for err in stats['errors'][:5]:  # 只显示前5个
                self.logger.error(f"  - {err}")


class PatternMatcher:
    """模式匹配器 - 识别文档中的各种填空模式"""

    def detect_patterns(self, text: str) -> Dict[str, List]:
        """
        检测文本中的所有模式

        Returns:
            {
                'combo': [...],      # 组合字段
                'bracket': [...],    # 括号占位符
                'colon': [...],      # 冒号填空
                'date': [...]        # 日期格式
            }
        """
        patterns = {}

        # 1. 组合字段模式：（xxx、yyy）
        combo_matches = self._match_combo_pattern(text)
        if combo_matches:
            patterns['combo'] = combo_matches

        # 2. 括号占位符：（xxx）
        bracket_matches = self._match_bracket_pattern(text)
        if bracket_matches:
            patterns['bracket'] = bracket_matches

        # 3. 冒号填空：xxx：___
        colon_matches = self._match_colon_pattern(text)
        if colon_matches:
            patterns['colon'] = colon_matches

        # 4. 日期格式
        date_matches = self._match_date_pattern(text)
        if date_matches:
            patterns['date'] = date_matches

        return patterns

    def _match_combo_pattern(self, text: str) -> List[Dict]:
        """匹配组合字段：（xxx、yyy）或（xxx、yyy、zzz）"""
        pattern = r'[（(]([^）)]+[、，][^）)]+)[）)]'
        matches = []

        for match in re.finditer(pattern, text):
            combo_text = match.group(1)

            # 过滤掉明显不是字段的组合
            if any(skip in combo_text for skip in ['如有', '如果', '包括', '或者']):
                continue

            # 分割组合字段
            fields = re.split(r'[、，]', combo_text)
            fields = [f.strip() for f in fields]

            matches.append({
                'full_match': match.group(0),
                'fields': fields,
                'start': match.start(),
                'end': match.end()
            })

        return matches

    def _match_bracket_pattern(self, text: str) -> List[Dict]:
        """匹配括号占位符：（xxx）"""
        pattern = r'[（(]([^）)]+)[）)]'
        matches = []

        for match in re.finditer(pattern, text):
            field_name = match.group(1).strip()

            # 过滤掉组合字段（已在combo中处理）
            if '、' in field_name or '，' in field_name:
                continue

            # 清理提示性前缀（如"请填写"、"请输入"等）
            prompt_prefixes = ['请填写', '请输入', '待填写', '填写', '输入']
            for prefix in prompt_prefixes:
                if field_name.startswith(prefix):
                    field_name = field_name[len(prefix):].strip()
                    break

            # 过滤掉明显不是字段的内容
            skip_keywords = ['如有', '如果', 'www.', 'http', '说明', '注意', '备注']
            if any(skip in field_name for skip in skip_keywords):
                continue

            # 如果清理后字段名太短或为空，跳过
            if len(field_name) < 2:
                continue

            matches.append({
                'full_match': match.group(0),
                'field': field_name,
                'start': match.start(),
                'end': match.end()
            })

        return matches

    def _match_colon_pattern(self, text: str) -> List[Dict]:
        """匹配冒号填空：xxx：___  或 xxx：（空白）或 xxx："""
        # 匹配冒号后有下划线、空白或直接结束的情况（放宽匹配条件）
        pattern = r'([^：:\n]{2,20})[:：]\s*([_\s]*|$)'
        matches = []

        for match in re.finditer(pattern, text):
            original_field_name = match.group(1).strip()

            # 提取纯字段名（移除括号等）用于数据匹配
            clean_field_name = re.sub(r'[（(][^）)]*[）)]', '', original_field_name).strip()

            # 过滤掉太短或明显不是字段的内容
            if len(clean_field_name) < 2:
                continue

            matches.append({
                'full_match': match.group(0),
                'field': clean_field_name,  # 清理后的字段名（用于数据匹配）
                'original_field': original_field_name,  # 原始字段名（包含括号，用于替换）
                'start': match.start(),
                'end': match.end()
            })

        return matches

    def _match_date_pattern(self, text: str) -> List[Dict]:
        """匹配日期格式：____年____月____日"""
        patterns = [
            r'日期\s*[:：]?\s*[_\s]*年[_\s]*月[_\s]*日',
            r'[_\s]*年[_\s]*月[_\s]*日',  # 更宽松的匹配
        ]

        matches = []
        for pattern in patterns:
            for match in re.finditer(pattern, text):
                # 只匹配包含"年月日"的部分
                matches.append({
                    'full_match': match.group(0),
                    'field': 'date',
                    'start': match.start(),
                    'end': match.end()
                })
                return matches  # 只取第一个匹配

        return matches


class FieldRecognizer:
    """字段识别器 - 识别字段名称并映射到数据"""

    def __init__(self):
        # 字段变体库：统一映射
        self.field_variants = {
            # 供应商名称
            'companyName': [
                '供应商名称', '供应商全称', '投标人名称', '公司名称',
                '单位名称', '应答人名称', '企业名称'
            ],

            # 项目信息
            'projectName': ['项目名称', '采购项目名称', '招标项目名称'],
            'projectNumber': ['项目编号', '采购编号', '招标编号', '项目号', '编号'],

            # 采购方信息
            'purchaserName': ['采购人', '采购人名称', '招标人', '招标人名称', '甲方', '甲方名称'],

            # 联系方式
            'address': ['地址', '注册地址', '办公地址', '联系地址', '通讯地址'],
            'phone': ['电话', '联系电话', '固定电话', '电话号码'],
            'email': ['电子邮件', '电子邮箱', '邮箱', 'email', 'Email', 'E-mail', 'E-Mail'],
            'fax': ['传真', '传真号码', '传真号'],
            'postalCode': ['邮编', '邮政编码', '邮码'],

            # 人员信息
            'legalRepresentative': [
                '法定代表人', '法人代表', '法人', '法人姓名', '姓名',
                '法定代表人姓名', '法定代表人名称', '负责人', '负责人姓名'
            ],
            'legalRepresentativePosition': ['法人职位', '法定代表人职位', '法人职务'],
            'legalRepresentativeGender': ['性别', '法人性别', '法定代表人性别'],
            'legalRepresentativeAge': ['年龄', '法人年龄', '法定代表人年龄'],
            'representativeName': ['供应商被授权人姓名', '被授权人姓名', '授权人姓名', '供应商代表', '供应商代表姓名', '代表姓名', '代表人'],
            'representativeTitle': ['职务', '职称', '职务职称', '职位'],

            # 公司基本信息
            'establishDate': ['成立时间', '成立日期', '注册日期', '注册时间'],
            'businessScope': ['经营范围', '业务范围', '经营内容'],
            'registeredCapital': ['注册资本', '注册资金'],
            'socialCreditCode': ['统一社会信用代码', '社会信用代码', '信用代码'],
            'companyType': ['公司类型', '企业类型', '组织形式', '单位性质', '企业性质'],
            'businessTerm': ['经营期限', '营业期限', '经营年限'],

            # 日期
            'date': ['日期', 'date'],
        }

        # 反向映射：从变体到标准字段名
        self.reverse_map = {}
        for standard_name, variants in self.field_variants.items():
            for variant in variants:
                self.reverse_map[variant.lower()] = standard_name

    def recognize_field(self, field_text: str) -> Optional[str]:
        """
        识别字段名称，返回标准字段名

        Args:
            field_text: 原始字段文本

        Returns:
            标准字段名，如 'companyName', 'projectName' 等
        """
        field_text = field_text.strip().lower()

        # 移除常见后缀
        field_text = re.sub(r'（[^）]*）', '', field_text)  # 移除括号
        field_text = field_text.replace('（盖章）', '').replace('（公章）', '')
        field_text = field_text.replace('（签字）', '').replace('（签名）', '')
        field_text = field_text.strip()

        # 查找匹配
        return self.reverse_map.get(field_text)

    def recognize_combo_fields(self, fields: List[str]) -> List[Optional[str]]:
        """识别组合字段"""
        return [self.recognize_field(f) for f in fields]


class ContentFiller:
    """内容填充器 - 实际执行填充操作"""

    def __init__(self, logger):
        self.logger = logger
        self.field_recognizer = FieldRecognizer()

    def fill_combo_field(self,
                        paragraph: Paragraph,
                        text: str,
                        matches: List[Dict],
                        data: Dict[str, Any]) -> bool:
        """填充组合字段（使用run精确替换）"""
        if not matches:
            return False

        # 构建段落的run映射（只构建一次）
        full_text, runs, char_to_run_map = WordDocumentUtils.build_paragraph_text_map(paragraph)
        filled_count = 0

        # 处理所有组合字段（从后往前，这样位置不会失效）
        for match in reversed(matches):
            fields = match['fields']

            # 识别字段名
            standard_fields = self.field_recognizer.recognize_combo_fields(fields)

            # 获取值
            values = []
            all_found = True
            for std_field in standard_fields:
                if std_field and std_field in data:
                    values.append(str(data[std_field]))
                else:
                    all_found = False
                    break

            if not all_found:
                continue  # 跳过这个组合字段

            # 构建替换文本
            replacement = '、'.join(values)
            # 使用run精确替换（从后往前处理，不需要重新构建映射）
            success = WordDocumentUtils.apply_replacement_to_runs(
                runs, char_to_run_map, match, replacement, self.logger
            )
            if success:
                filled_count += 1
                self.logger.info(f"    组合字段填充: {fields} → {replacement}")

        return filled_count > 0

    def fill_bracket_field(self,
                          paragraph: Paragraph,
                          text: str,
                          matches: List[Dict],
                          data: Dict[str, Any]) -> bool:
        """填充括号字段（使用run精确替换）"""
        if not matches:
            return False

        # 构建段落的run映射（只构建一次）
        full_text, runs, char_to_run_map = WordDocumentUtils.build_paragraph_text_map(paragraph)
        filled_count = 0

        # 从后往前替换（避免位置偏移，不需要重新构建映射）
        for match in reversed(matches):
            field_name = match['field']
            std_field = self.field_recognizer.recognize_field(field_name)

            if std_field and std_field in data:
                value = str(data[std_field])

                # 跳过空值（避免填充空白内容）
                if not value or value.strip() == '':
                    self.logger.debug(f"  跳过空值字段: {field_name}")
                    continue

                # 保留括号格式：（xxx） → （数据值）
                replacement = f"（{value}）"

                # 使用run精确替换
                success = WordDocumentUtils.apply_replacement_to_runs(
                    runs, char_to_run_map, match, replacement, self.logger
                )
                if success:
                    filled_count += 1
                    self.logger.info(f"    括号字段填充: {field_name} → （{value}）")

        return filled_count > 0

    def fill_colon_field(self,
                        paragraph: Paragraph,
                        text: str,
                        matches: List[Dict],
                        data: Dict[str, Any]) -> bool:
        """填充冒号字段（使用run精确替换）"""
        if not matches:
            return False

        # 构建段落的run映射（只构建一次）
        full_text, runs, char_to_run_map = WordDocumentUtils.build_paragraph_text_map(paragraph)
        filled_count = 0

        # 从后往前处理（避免位置偏移）
        for match in reversed(matches):
            field_name = match['field']  # 清理后的字段名（用于数据匹配）
            original_field_name = match.get('original_field', field_name)  # 原始字段名（包含括号）
            std_field = self.field_recognizer.recognize_field(field_name)

            if std_field and std_field in data:
                value = str(data[std_field])

                # 跳过空值（避免填充空白内容）
                if not value or value.strip() == '':
                    self.logger.debug(f"  跳过空值字段: {original_field_name}")
                    continue

                # 特殊处理：如果是日期字段，格式化为中文格式
                if std_field == 'date':
                    value = self._format_date(value)

                # 保留冒号，移除下划线
                colon = '：' if '：' in match['full_match'] else ':'

                # 检查后面是否紧跟着其他字段，如果是则添加空格分隔
                next_char_pos = match['end']
                trailing_space = ''
                if next_char_pos < len(full_text):
                    # 检查后面是否有汉字（表示可能是下一个字段）
                    next_chars = full_text[next_char_pos:next_char_pos+5]
                    if next_chars and any('\u4e00' <= c <= '\u9fff' for c in next_chars[:2]):
                        trailing_space = '  '  # 添加两个空格分隔

                # 使用原始字段名（保留括号后缀如"（加盖公章）"）
                replacement = f"{original_field_name}{colon}{value}{trailing_space}"
                # 使用run精确替换
                success = WordDocumentUtils.apply_replacement_to_runs(
                    runs, char_to_run_map, match, replacement, self.logger
                )
                if success:
                    filled_count += 1
                    self.logger.info(f"    冒号字段填充: {original_field_name} → {value}")

        return filled_count > 0

    def fill_date_field(self,
                       paragraph: Paragraph,
                       text: str,
                       matches: List[Dict],
                       data: Dict[str, Any]) -> bool:
        """填充日期字段（使用run精确替换）"""
        if not matches or 'date' not in data:
            return False

        # 构建段落的run映射
        full_text, runs, char_to_run_map = WordDocumentUtils.build_paragraph_text_map(paragraph)

        date_value = str(data['date'])
        formatted_date = self._format_date(date_value)

        # 替换整个日期模式
        match = matches[0]

        # 检查前面是否有"日期："
        prefix_start = max(0, match['start'] - 10)
        prefix_text = full_text[prefix_start:match['start']]

        if '日期' in prefix_text:
            # 找到"日期："的位置
            date_label_pos = full_text.rfind('日期', 0, match['start'])
            colon_pos = full_text.find('：', date_label_pos, match['start'])
            if colon_pos == -1:
                colon_pos = full_text.find(':', date_label_pos, match['start'])

            if colon_pos != -1:
                # 从冒号后开始替换整个日期部分
                replacement_match = {
                    'start': colon_pos + 1,
                    'end': match['end'],
                    'text': full_text[colon_pos+1:match['end']]
                }
                success = WordDocumentUtils.apply_replacement_to_runs(
                    runs, char_to_run_map, replacement_match, formatted_date, self.logger
                )
            else:
                # 从"日期"后开始替换
                replacement_match = {
                    'start': date_label_pos,
                    'end': match['end'],
                    'text': full_text[date_label_pos:match['end']]
                }
                success = WordDocumentUtils.apply_replacement_to_runs(
                    runs, char_to_run_map, replacement_match, f"日期：{formatted_date}", self.logger
                )
        else:
            # 没有前缀，直接替换
            success = WordDocumentUtils.apply_replacement_to_runs(
                runs, char_to_run_map, match, formatted_date, self.logger
            )

        if success:
            self.logger.info(f"    日期填充: {formatted_date}")
        return success

    def _format_date(self, date_str: str) -> str:
        """格式化日期"""
        # 移除空格
        date_str = re.sub(r'\s+', '', date_str)

        # 尝试匹配常见格式
        patterns = [
            (r'(\d{4})-(\d{1,2})-(\d{1,2})', r'\1年\2月\3日'),
            (r'(\d{4})/(\d{1,2})/(\d{1,2})', r'\1年\2月\3日'),
            (r'(\d{4})\.(\d{1,2})\.(\d{1,2})', r'\1年\2月\3日'),
        ]

        for pattern, replacement in patterns:
            if re.match(pattern, date_str):
                return re.sub(pattern, replacement, date_str)

        # 已经是中文格式
        if '年' in date_str and '月' in date_str:
            return date_str

        return date_str

    def _update_paragraph(self, paragraph: Paragraph, new_text: str):
        """更新段落文本，保持格式"""
        if paragraph.runs:
            first_run = paragraph.runs[0]
            # 保存格式
            font = first_run.font
            bold = font.bold
            italic = font.italic
            underline = font.underline
            font_size = font.size
            font_name = font.name

            # 清空段落
            paragraph.clear()

            # 添加新文本
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
            paragraph.text = new_text


# 向后兼容：提供与旧API相同的接口
class InfoFillerV2(SmartDocumentFiller):
    """InfoFiller V2 - 基于 SmartDocumentFiller 的兼容层"""

    def fill_info(self, doc: Document, company_info: Dict[str, Any],
                  project_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        兼容旧版本的 fill_info 接口
        """
        # 合并数据
        data = {**company_info, **project_info}

        # 调用新方法
        stats = self.fill_document(doc, data)

        # 转换为旧格式
        return {
            'total_replacements': stats['total_filled'],
            'replacement_rules': stats['pattern_counts'].get('bracket', 0),
            'fill_rules': stats['pattern_counts'].get('colon', 0),
            'combination_rules': stats['pattern_counts'].get('combo', 0),
            'skipped_fields': 0,
            'none': len(stats['unfilled_fields'])
        }
