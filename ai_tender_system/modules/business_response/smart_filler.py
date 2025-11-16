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

        # ✅ 专门检测 purchaserName 字段
        if 'purchaserName' in data:
            self.logger.info(f"✅ 检测到purchaserName字段: {data.get('purchaserName')}")
        else:
            self.logger.warning("⚠️  未检测到purchaserName字段")

        # ✅ 专门检测 companyName 字段（响应人名称映射到此字段）
        if 'companyName' in data:
            self.logger.info(f"✅ 检测到companyName字段: {data.get('companyName')}")
            self.logger.info(f"   → 此字段应填充到: 响应人名称/应答人名称/供应商名称等")
        else:
            self.logger.warning("⚠️  未检测到companyName字段")

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

        # 处理所有表格
        self.logger.info("开始处理表格...")
        table_para_idx = len(doc.paragraphs)  # 表格段落从这个索引开始编号
        for table_idx, table in enumerate(doc.tables):
            self.logger.debug(f"处理表格#{table_idx}")
            for row_idx, row in enumerate(table.rows):
                for cell_idx, cell in enumerate(row.cells):
                    for cell_para_idx, paragraph in enumerate(cell.paragraphs):
                        if not paragraph.text.strip():
                            continue

                        # 匹配并填充（使用统一的段落处理逻辑）
                        para_id = f"table{table_idx}_row{row_idx}_cell{cell_idx}_para{cell_para_idx}"
                        result = self._process_paragraph(paragraph, data, table_para_idx)
                        table_para_idx += 1

                        # 更新统计
                        if result['filled']:
                            stats['total_filled'] += 1
                            pattern = result['pattern']
                            stats['pattern_counts'][pattern] = stats['pattern_counts'].get(pattern, 0) + 1
                            self.logger.debug(f"  表格填充成功: {para_id}")
                        elif result['unfilled_fields']:
                            stats['unfilled_fields'].extend(result['unfilled_fields'])

                        if result['errors']:
                            stats['errors'].extend(result['errors'])

        # 过滤未填充字段，排除误识别内容
        if stats['unfilled_fields']:
            filtered_unfilled = self._filter_invalid_fields(stats['unfilled_fields'])
            stats['filtered_unfilled_fields'] = filtered_unfilled  # 添加过滤后的字段
            stats['original_unfilled_count'] = len(stats['unfilled_fields'])  # 保留原始数量用于调试
        else:
            stats['filtered_unfilled_fields'] = []
            stats['original_unfilled_count'] = 0

        # 输出统计报告
        self._print_stats(stats)

        # 后处理：清理多余占位符
        # self._post_process(doc)

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

        for pattern_type in ['combo', 'bracket', 'date', 'colon', 'space_fill']:
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

        elif pattern_type == 'space_fill':
            return self.content_filler.fill_space_field(paragraph, text, matches, data)

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

        # 过滤未填充字段：排除明显的误识别内容
        if stats['unfilled_fields']:
            filtered_unfilled = self._filter_invalid_fields(stats['unfilled_fields'])

            if filtered_unfilled:
                self.logger.warning(f"真正未填充字段数: {len(filtered_unfilled)}")
                for uf in filtered_unfilled[:10]:  # 只显示前10个
                    self.logger.warning(f"  - 段落#{uf['para_idx']}: {uf['field']}")

            # 显示过滤掉的误识别数量
            filtered_count = len(stats['unfilled_fields']) - len(filtered_unfilled)
            if filtered_count > 0:
                self.logger.debug(f"过滤掉的误识别字段数: {filtered_count}")

        if stats['errors']:
            self.logger.error(f"错误数: {len(stats['errors'])}")
            for err in stats['errors'][:5]:  # 只显示前5个
                self.logger.error(f"  - {err}")

    def _filter_invalid_fields(self, unfilled_fields: List[Dict]) -> List[Dict]:
        """
        过滤掉明显不是数据字段的误识别内容

        Args:
            unfilled_fields: 原始未填充字段列表

        Returns:
            过滤后的列表（仅包含真正的数据字段）
        """
        # 排除关键词：说明性文字、标题、提示
        exclude_keywords = [
            # 说明性文字
            '行贿犯罪记录', '时间从', '以相关', '以中国', '本条', '即增值税',
            '我公司', '我方', '本投标', '有关的一切', '请寄', '通讯',
            # 提示性文字
            '盖章', '签字', '公章', '签名',
            # 格式和标题
            '格式', '附件', '正本', '副本', '电子版',
            # 条款标题
            '情况', '承诺', '声明', '说明', '注意', '备注',
            # 网址和特殊字符
            'http', 'www.', '://','满足招标','见附件',
            # 文档材料类关键词（文档清单项）
            '身份证', '复印件', '证明', '原件', '扫描件', '材料', '文件'
        ]

        # 过滤逻辑
        filtered = []
        for field_info in unfilled_fields:
            field = field_info.get('field', '')

            # 如果是字典（bracket、colon模式），取field字段
            if isinstance(field, dict):
                field_text = field.get('field', '')
            else:
                field_text = str(field)

            # 检查是否包含排除关键词
            should_exclude = any(keyword in field_text for keyword in exclude_keywords)

            # 检查长度（字段名通常不超过15个字符）
            if not should_exclude and len(field_text) > 15:
                should_exclude = True

            if not should_exclude:
                filtered.append(field_info)

        return filtered

    def _post_process(self, doc: Document):
        """
        后处理：清理多余的占位符和格式

        Args:
            doc: Word文档对象
        """
        self.logger.info("开始后处理：清理多余占位符")
        cleaned_count = 0

        for paragraph in doc.paragraphs:
            text = paragraph.text

            # 清理多余的下划线
            text = re.sub(r'_{3,}', '', text)

            # 清理多余的空格（保留表格对齐所需的空格）
            # 改进：只在真正的表格布局时跳过清理
            is_table_layout = False
            if re.search(r'\s{8,}', text):
                # 检查是否是真正的表格布局：
                # 1. 整行都是空格（纯对齐行）
                if text.strip() == '':
                    is_table_layout = True
                # 2. 有多组8+空格分隔（表格列分隔）
                elif len(re.findall(r'\s{8,}', text)) >= 2:
                    is_table_layout = True
                # 3. 如果包含实际内容（汉字、括号、标点），即使有长空格也应清理
                elif re.search(r'[\u4e00-\u9fa5（）()：:，。、]', text):
                    is_table_layout = False
                else:
                    is_table_layout = True

            if not is_table_layout:
                text = re.sub(r'\s{3,}', '  ', text)

            # 清理多余的冒号
            text = re.sub(r'[:：]{2,}', '：', text)

            # 标准化冒号
            text = re.sub(r':', '：', text)

            # 去除多余的年月日标识
            text = re.sub(r'(\d{4}年\d{1,2}月\d{1,2}日)\s*年\s*月\s*日', r'\1', text)

            if text != paragraph.text:
                self._update_paragraph_text(paragraph, text.strip())
                cleaned_count += 1

        self.logger.info(f"后处理完成，清理了 {cleaned_count} 个段落")

    def _update_paragraph_text(self, paragraph: Paragraph, new_text: str):
        """
        更新段落文本，保持原有格式

        Args:
            paragraph: 段落对象
            new_text: 新文本内容
        """
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


class FieldClassifier:
    """字段分类器 - 根据字段类型决定处理策略

    核心规则：
    1. 单位盖章填名称 - 单位/公司字段即使有盖章标记也要填充
    2. 个人签字留空白 - 个人字段有签字/盖章标记则不填充
    """

    # 单位/公司相关字段（可能出现盖章）
    UNIT_FIELDS = {
        'companyName',      # 供应商名称、公司名称
        'supplierName',     # 供应商
        'vendorName',       # 投标人
        'purchaserName',    # 采购人（可能需要盖章）
    }

    # 个人相关字段（可能出现签字/盖章）
    PERSON_FIELDS = {
        'legalRepresentative',      # 法定代表人
        'representativeName',       # 授权代表人、被授权人
        'authorizedPerson',         # 被授权人
        'representativeTitle',      # 职务（与个人相关）
        'authorizedPersonId',       # 身份证号（与个人相关）
    }

    # 格式标记定义
    SEAL_MARKERS = [
        '（盖章）', '（公章）', '（盖公章）', '(盖章)', '(公章)', '(盖公章)',
        '（盖单位章）', '（盖企业章）', '（加盖公章）', '（加盖单位公章）',  # 新增：单位盖章变体
        '(盖单位章)', '(盖企业章)', '(加盖公章)', '(加盖单位公章)'  # 半角版本
    ]
    SIGNATURE_MARKERS = ['（签字）', '（签名）', '(签字)', '(签名)', '（签章）', '(签章)']
    COMBO_MARKERS = ['（签字或盖章）', '（签字及盖章）', '（签字并盖章）',
                     '(签字或盖章)', '(签字及盖章)', '(签字并盖章)']
    ALL_MARKERS = SEAL_MARKERS + SIGNATURE_MARKERS + COMBO_MARKERS

    @classmethod
    def classify_field(cls, standard_field: str) -> str:
        """分类字段

        Args:
            standard_field: 标准字段名（如 'companyName', 'legalRepresentative'）

        Returns:
            字段类型：'unit' | 'person' | 'general'
        """
        if not standard_field:
            return 'general'

        if standard_field in cls.UNIT_FIELDS:
            return 'unit'
        elif standard_field in cls.PERSON_FIELDS:
            return 'person'
        else:
            return 'general'

    @classmethod
    def should_fill(cls, field_text: str, standard_field: str) -> bool:
        """判断是否应该填充字段

        核心规则：
        - 个人字段 + 签字/盖章标记 = 不填充（留空白供手写）
        - 单位字段 + 任何标记 = 填充（需要填公司名）
        - 其他字段 = 正常填充
        - 未识别字段 + 人员关键词 + 签字标记 = 不填充（如"法定代表人或委托代理人（签字）"）
        - 文档清单项（包含"身份证"、"复印件"等） = 不填充

        Args:
            field_text: 原始字段文本（如 "法定代表人（签字或盖章）"）
            standard_field: 标准字段名（如 'legalRepresentative'）

        Returns:
            是否应该填充
        """
        # ⚠️ 关键修复：即使 std_field 是 None，也要检查签字/文档关键词
        # 这样可以正确处理"法定代表人或委托代理人（签字）"等复合字段

        # 1. 检查是否包含签字/盖章标记
        has_signature_marker = any(marker in field_text for marker in cls.ALL_MARKERS)

        # 2. 检查是否包含人员相关关键词
        person_keywords = ['法定代表人', '法人', '授权代表', '委托代理人', '代理人', '被授权人', '代表']
        has_person_keyword = any(keyword in field_text for keyword in person_keywords)

        # 3. 如果同时包含人员关键词和签字标记，不填充（无论是否识别）
        if has_person_keyword and has_signature_marker:
            return False

        # 4. 检查是否包含文档材料关键词（文档清单项）
        document_keywords = ['身份证', '复印件', '证明', '原件', '扫描件', '附件', '材料', '文件']
        if any(keyword in field_text for keyword in document_keywords):
            return False

        # 如果 std_field 是 None（未识别字段），默认不填充（安全策略）
        if not standard_field:
            return False

        field_type = cls.classify_field(standard_field)

        # 个人字段：检查是否有签字/盖章标记
        if field_type == 'person':
            # 任何签字/盖章标记都不填充
            has_marker = any(marker in field_text for marker in cls.ALL_MARKERS)
            return not has_marker  # 有标记则不填充，留空白

        # 单位字段和普通字段都填充
        return True

    @classmethod
    def extract_format_marker(cls, text: str) -> str:
        """提取格式标记

        Args:
            text: 文本（可能包含格式标记）

        Returns:
            找到的格式标记，如 "（盖章）"，没有则返回空字符串
        """
        for marker in cls.ALL_MARKERS:
            if marker in text:
                return marker
        return ""

    @classmethod
    def should_preserve_marker(cls, standard_field: str, marker: str) -> bool:
        """判断是否应该保留格式标记

        规则：
        - 单位字段 + 盖章/公章标记 = 保留（填充后仍需盖章）
        - 其他情况不保留

        Args:
            standard_field: 标准字段名
            marker: 格式标记

        Returns:
            是否保留标记
        """
        field_type = cls.classify_field(standard_field)

        # 单位字段保留盖章/公章标记
        if field_type == 'unit' and marker in cls.SEAL_MARKERS:
            return True

        return False

    @classmethod
    def is_format_marker(cls, text: str) -> bool:
        """判断文本是否只是格式标记

        Args:
            text: 要判断的文本

        Returns:
            是否为纯格式标记
        """
        # 去除空格后检查
        clean_text = text.strip()
        return clean_text in cls.ALL_MARKERS


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
                'space_fill': [...], # 空格填空（字段名 + 多个空格）
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

        # 4. 空格填空：字段名 + 多个空格（新增）
        space_fill_matches = self._match_space_fill_pattern(text)
        if space_fill_matches:
            patterns['space_fill'] = space_fill_matches

        # 5. 日期格式
        date_matches = self._match_date_pattern(text)
        if date_matches:
            patterns['date'] = date_matches

        return patterns

    def _detect_abbreviation_field(self, text_inside_bracket: str) -> Optional[str]:
        """
        检测是否是带空格占位符的简写字段

        判断规则：
        1. 必须有足够的空格占位符（≥5个）
        2. 去除空格后核心文本≤3个字
        3. 核心文本匹配简写映射表

        Examples:
            "                 项目"  → 'projectName' ✅
            "该项目"                 → None ❌
            "公司章程"               → None ❌

        Args:
            text_inside_bracket: 括号内的文本（包含可能的空格）

        Returns:
            标准字段名，如 'projectName'，如果不是简写则返回 None
        """
        # 计算空格数量
        stripped = text_inside_bracket.strip()
        total_spaces = len(text_inside_bracket) - len(stripped)

        # 关键条件1：必须有足够的空格（说明是占位符）
        if total_spaces < 5:
            return None

        # 关键条件2：核心文本必须很短（≤3字）
        if len(stripped) > 3:
            return None

        # 简写映射表
        abbr_map = {
            '项目': 'projectName',
            '编号': 'projectNumber',
            '公司': 'companyName',
            '单位': 'companyName',
            '地址': 'address',
            '电话': 'phone',
            '邮箱': 'email',
            '传真': 'fax',
        }

        return abbr_map.get(stripped)

    def _match_combo_pattern(self, text: str) -> List[Dict]:
        """匹配组合字段：（xxx、yyy）或（xxx和yyy）或[xxx、yyy、zzz]

        支持三种括号类型：
        - 全角括号：（项目名称、招标编号）
        - 半角圆括号：(项目名称、招标编号)
        - 半角方括号：[项目名称、招标编号]

        支持四种分隔符：
        - 顿号：、
        - 逗号：，
        - 和字：和
        - 及字：及
        """
        # 扩展正则以支持"和"、"及"连接词
        pattern = r'[（(\[]([^）)\]]+(?:[、，和及][^）)\]]+)+)[）)\]]'
        matches = []

        for match in re.finditer(pattern, text):
            combo_text = match.group(1)

            # 过滤掉明显不是字段的组合
            if any(skip in combo_text for skip in ['如有', '如果', '包括', '或者']):
                continue

            # 分割组合字段（支持多种分隔符）
            fields = re.split(r'[、，和及]', combo_text)
            fields = [f.strip() for f in fields if f.strip()]  # 过滤空字段

            # 至少需要2个字段才算组合字段
            if len(fields) < 2:
                continue

            matches.append({
                'full_match': match.group(0),
                'fields': fields,
                'start': match.start(),
                'end': match.end()
            })

        return matches

    def _match_bracket_pattern(self, text: str) -> List[Dict]:
        """匹配括号占位符：（xxx）、(xxx)、[xxx]

        支持三种括号类型：
        - 全角括号：（项目名称）
        - 半角圆括号：(项目名称)
        - 半角方括号：[项目名称]
        """
        pattern = r'[（(\[]([^）)\]]+)[）)\]]'
        matches = []

        for match in re.finditer(pattern, text):
            # 🆕 Step 1: 先尝试简写字段检测（使用原始括号内文本）
            text_inside_bracket = match.group(1)  # 包含空格的原始文本
            abbr_field = self._detect_abbreviation_field(text_inside_bracket)

            if abbr_field:
                # 匹配到简写字段，直接添加到结果
                matches.append({
                    'full_match': match.group(0),
                    'field': text_inside_bracket.strip(),  # 显示用（如"项目"）
                    'standard_field': abbr_field,  # 直接提供标准字段名
                    'is_abbreviation': True,  # 标记为简写
                    'start': match.start(),
                    'end': match.end()
                })
                continue  # 跳过常规字段识别流程

            # Step 2: 常规字段识别流程
            field_name = text_inside_bracket.strip()

            # 过滤掉组合字段（已在combo中处理）
            if '、' in field_name or '，' in field_name:
                continue

            # 清理提示性前缀（如"请填写"、"请输入"等）
            prompt_prefixes = ['请填写', '请输入', '待填写', '填写', '输入']
            original_field_name = field_name
            for prefix in prompt_prefixes:
                if field_name.startswith(prefix):
                    field_name = field_name[len(prefix):].strip()
                    break

            # ✅ 新增：清理冒号和后面的占位符（空格/下划线/文字占位符）
            # 匹配 "字段名：占位符" 的格式
            # 支持的占位符：空格、下划线、XXX、xxx、待填、待填写、请填写等
            # 只匹配冒号后面是占位符的情况，不会影响实际内容（如"成立日期：2020-01-01"）
            colon_match = re.match(r'^([^：:]+)[：:]\s*([_\s]*|XXX|xxx|待填|待填写|请填写|待确定|暂无)?$', field_name)
            if colon_match:
                field_name = colon_match.group(1).strip()

            # 过滤掉明显不是字段的内容
            skip_keywords = [
                '如有', '如果', 'www.', 'http', '说明', '注意', '备注',
                # 文档材料类关键词
                '身份证', '复印件', '证明', '原件', '扫描件', '附件', '材料', '文件'
            ]
            if any(skip in field_name for skip in skip_keywords):
                continue

            # 如果清理后字段名太短或为空，跳过
            if len(field_name) < 2:
                continue

            # ✅ 改进：检测是否包含占位符（冒号后跟3个以上空格或下划线）
            # 如果包含占位符，说明是待填写字段，不应跳过
            has_placeholder = bool(re.search(r'[：:]\s*[_\s]{3,}', original_field_name))

            # ✅ 关键检测：判断括号内是字段名还是实际内容
            # 只有当超过8字符、未清理任何内容、且不包含占位符时，才跳过
            # 常见字段名如"项目名称"、"公司名称"、"法定代表人"等通常不超过8字符
            if len(original_field_name) > 8 and original_field_name == field_name and not has_placeholder:
                # 如果超过8字符，很可能是实际内容（如公司全称、长项目名等），跳过
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
        # 修改正则：正确处理冒号后的内容（包括括号内的中文）
        # 策略：先匹配冒号前的字段名，然后捕获冒号后到行尾或下一个字段的内容
        # 使用正向前瞻来识别下一个字段（2个以上中文字符后跟冒号）
        import logging
        logger = logging.getLogger("ai_tender_system.smart_filler")

        pattern = r'([^：:\n]{2,20})[:：]\s*(.*)(?=(?:\s{2,}[\u4e00-\u9fa5]{2,}[:：])|$)'
        matches = []

        for match in re.finditer(pattern, text):
            original_field_name = match.group(1).strip()
            after_colon = match.group(2).strip()  # 冒号后的内容

            # 提取纯字段名（移除括号等）用于数据匹配
            clean_field_name = re.sub(r'[（(][^）)]*[）)]', '', original_field_name).strip()

            # 过滤掉太短或明显不是字段的内容
            if len(clean_field_name) < 2:
                continue

            # ✅ 关键检测：判断冒号后是否已有实际内容
            if after_colon:
                # 去除下划线、空格等占位符
                content_without_placeholder = re.sub(r'[_\s]+', '', after_colon)

                # 🆕 增强检测：区分"真实内容"、"格式标记"和"下一个字段名"
                if len(content_without_placeholder) > 0:
                    # 检查是否只是格式标记
                    if FieldClassifier.is_format_marker(content_without_placeholder):
                        # 是格式标记（如"（盖章）"），不是内容，应该继续处理
                        pass
                    # 如果内容以冒号结尾，说明是下一个字段名（如"邮政编码："），不算已填写
                    elif content_without_placeholder.endswith(('：', ':')):
                        # 这是横向多字段格式，继续处理当前字段
                        pass
                    else:
                        # 可能是真正的内容，但需要进一步检查
                        # 去除格式标记后再判断
                        real_content = content_without_placeholder
                        for marker in FieldClassifier.ALL_MARKERS:
                            real_content = real_content.replace(marker, '')

                        # 🆕 检查是否是说明性文字占位符（2025-11-15新增）
                        # 识别类似"注: 如控股股东/投资人为自然人需提供姓名和身份证号"的说明文字
                        instruction_patterns = [
                            r'^注[:：]',                    # 以"注:"开头
                            r'^说明[:：]',                  # 以"说明:"开头
                            r'^备注[:：]',                  # 以"备注:"开头
                            r'^提示[:：]',                  # 以"提示:"开头
                            r'^如果.*需要?提供',            # "如果...需提供"或"如果...需要提供"
                            r'需要?提供.*身份证',           # 包含"需提供...身份证"
                            r'如.*为.*人.*需',              # "如...为自然人需..."或"如...为法人需..."
                            r'如.*人.*提供',                # "如...人...提供"
                        ]

                        is_instruction = any(re.search(p, real_content) for p in instruction_patterns)

                        # 如果不是说明性文字，且去除格式标记后还有内容（超过2个字符），才认为是已填写
                        if not is_instruction and real_content.strip() and len(real_content.strip()) > 2:
                            # 真正的内容，跳过已填写的字段
                            logger.debug(f"  [_match_colon_pattern] 跳过已填写字段: '{clean_field_name}', 内容='{real_content[:30]}...'")
                            continue
                        elif is_instruction:
                            # 是说明性文字占位符，应该继续处理
                            logger.debug(f"  [_match_colon_pattern] 识别到说明性占位符: '{real_content[:50]}...'")
                            pass

            # 调试：打印匹配的内容
            logger.debug(f"  [_match_colon_pattern] 匹配到: full_match='{match.group(0)}', after_colon='{after_colon}'")

            matches.append({
                'full_match': match.group(0),
                'field': clean_field_name,  # 清理后的字段名（用于数据匹配）
                'original_field': original_field_name,  # 原始字段名（包含括号，用于替换）
                'after_colon': after_colon,  # 保存冒号后的内容（可能包含格式标记）
                'start': match.start(),
                'end': match.end()
            })

        return matches

    def _match_space_fill_pattern(self, text: str) -> List[Dict]:
        """
        匹配空格填空模式：字段名 + 多个空格（无冒号）

        示例：
        - "地址                                          "
        - "电话                                           电子函件                                "
        - "投标人名称（盖章）                             "

        注意：
        - 字段名长度在2-20个字之间（支持带括号的字段）
        - 后面至少5个连续空格（避免误匹配普通文本）
        - 排除已有冒号的字段（由colon模式处理）
        """
        # 匹配：2-20个汉字/字母/括号 + 至少5个空格
        # 支持带括号的字段名，如"投标人名称（盖章）"
        # 使用负向后查看断言确保后面没有冒号
        pattern = r'([\u4e00-\u9fa5a-zA-Z/（）()]{2,20})(?![：:])(\s{5,})'
        matches = []

        for match in re.finditer(pattern, text):
            field_name = match.group(1).strip()
            spaces = match.group(2)

            # 清理括号后缀（如"（盖章）"、"（公章）"等）用于数据匹配
            # 注意：保留原始字段名用于文档替换
            clean_field_name = re.sub(r'[（(][^）)]*[）)]', '', field_name).strip()

            # 跳过明显不是字段的内容
            skip_keywords = [
                '本条', '时间从', '以相关', '我公司', '如有', '如果', '见附件', '满足',
                # 文档材料类关键词
                '身份证', '复印件', '证明', '原件', '扫描件', '附件', '材料', '文件'
            ]
            if any(skip in clean_field_name for skip in skip_keywords):
                continue

            # 跳过清理后字段名太短的
            if len(clean_field_name) < 2:
                continue

            # 跳过数字和特殊字符开头的（检查清理后的字段名）
            if clean_field_name[0].isdigit() or clean_field_name[0] in ['：', ':']:
                continue

            # 检查是否在冒号之前（避免与colon模式冲突）
            # 如果这个字段后面紧跟着冒号，应该由colon模式处理
            next_char_pos = match.end()
            if next_char_pos < len(text) and text[next_char_pos] in ['：', ':']:
                continue

            matches.append({
                'full_match': match.group(0),
                'field': clean_field_name,  # 用于数据匹配的清理后字段名
                'original_field': field_name,  # 保留括号的原始字段名（用于替换）
                'start': match.start(),
                'end': match.end()
            })

        return matches

    def _match_date_pattern(self, text: str) -> List[Dict]:
        """
        匹配日期格式：
        - ____年____月____日 (下划线占位符)
        - XXXX年X月X日 (字母X占位符)
        - 日期：____年____月____日
        - 日期：XXXX年X月X日
        """
        patterns = [
            # 带"日期："前缀的模式
            r'日期\s*[:：]?\s*[_\s]*年[_\s]*月[_\s]*日',  # 日期：____年____月____日
            r'日期\s*[:：]?\s*[X]{1,4}年[X]{1,2}月[X]{1,2}日',  # 日期：XXXX年X月X日
            # 不带前缀的模式
            r'[_\s]+年[_\s]+月[_\s]+日',  # ____年____月____日（多个占位符）
            r'[X]{1,4}年[X]{1,2}月[X]{1,2}日',  # XXXX年X月X日
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
                '供应商', '供应商名称', '供应商全称',  # 添加"供应商"简写
                '投标人', '投标人名称', '投标人全称',  # 添加"投标人"简写
                '公司名称', '单位名称', '应答人名称', '企业名称',
                '响应人', '响应人名称', '响应人全称'  # 添加"响应人"简写
            ],

            # 项目信息
            'projectName': ['项目名称', '采购项目名称', '招标项目名称'],
            'projectNumber': ['项目编号', '采购编号', '招标编号', '项目号', '编号'],

            # 采购方信息
            'purchaserName': ['采购人', '采购人名称', '招标人', '招标人名称', '甲方', '甲方名称'],

            # 联系方式
            'address': ['地址', '注册地址', '办公地址', '联系地址', '通讯地址', '供应商地址', '公司地址'],
            'phone': ['电话', '联系电话', '固定电话', '电话号码'],
            'email': ['电子邮件', '电子邮箱', '邮箱', 'email', 'Email', 'E-mail', 'E-Mail', '电子函件'],
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

            # 被授权人信息（扩展变体）
            'representativeName': [
                '供应商被授权人姓名', '被授权人姓名', '授权人姓名',
                '供应商代表', '供应商代表姓名', '代表姓名', '代表人',
                '签字人姓名', '签字人',  # 新增：签字人
                '全权代表姓名', '全权代表',  # 新增：全权代表
                '授权代表', '授权代表姓名',  # 新增：授权代表
                '被授权代表', '被授权代表姓名'  # 新增：被授权代表
            ],
            'representativeTitle': [
                '职务', '职称', '职务职称', '职位',
                '签字人职务', '签字人职称',  # 新增：签字人职务/职称
                '全权代表职务', '全权代表职称',  # 新增：全权代表职务/职称
                '代表职务', '代表职称',  # 新增：代表职务/职称
                '被授权人职务', '被授权人职称'  # 新增：被授权人职务/职称
            ],
            'authorizedPersonId': ['被授权人身份证', '授权人身份证', '身份证号', '身份证号码', '被授权人身份证号', '授权人身份证号'],

            # 公司基本信息
            'establishDate': [
                '成立时间', '成立日期', '注册日期', '注册时间',
                '成立和或注册日期', '成立和/或注册日期'  # 新增：处理特殊格式
            ],
            'businessScope': ['经营范围', '业务范围', '经营内容'],
            'registeredCapital': ['注册资本', '注册资金', '实收资本'],
            'socialCreditCode': ['统一社会信用代码', '社会信用代码', '信用代码'],
            'companyType': ['公司类型', '企业类型', '组织形式', '单位性质', '企业性质'],
            'businessTerm': ['经营期限', '营业期限', '经营年限'],

            # 日期
            'date': [
                '日期', 'date',
                '签字日期', '签署日期', '落款日期'  # 新增：处理各种签署日期格式
            ],

            # 股权结构字段（2025-10-30添加，2025-11-09增强）
            'actual_controller': [
                '实际控制人', '实际控制人姓名', '实际控制人名称',
                '实控人', '实控人姓名'
            ],
            'controlling_shareholder': [
                '控股股东', '控股股东名称', '控股股东及出资比例',
                '第一大股东', '最大股东',
                '供应商的控股股东/投资人名称及出资比例',  # 🆕 支持长字段名
                '供应商的控股股东'  # 支持部分匹配
            ],
            'shareholders_info': [
                '股东', '股东信息', '股东名称', '投资人信息',
                '股东及出资比例', '投资人名称及出资比例',
                '供应商的控股股东', '供应商的非控股股东',
                '供应商的非控股股东/投资人名称及出资比例',  # 🆕 支持长字段名
                '股权结构'
            ],

            # 管理关系字段（2025-10-30添加）
            'managing_unit_name': [
                '管理关系单位', '管理关系单位名称',
                '下属单位', '下级单位', '分支机构'
            ],
            'managed_unit_name': [
                '被管理关系单位', '被管理关系单位名称',
                '上级单位', '主管单位', '隶属单位'
            ],
        }

        # 反向映射：从变体到标准字段名
        self.reverse_map = {}
        for standard_name, variants in self.field_variants.items():
            for variant in variants:
                self.reverse_map[variant.lower()] = standard_name

    def recognize_field(self, field_text: str, enable_logging=False) -> Optional[str]:
        """
        识别字段名称，返回标准字段名

        Args:
            field_text: 原始字段文本
            enable_logging: 是否启用详细日志（用于诊断）

        Returns:
            标准字段名，如 'companyName', 'projectName' 等
        """
        original_field_text = field_text

        # ✅ 关键检查：如果原始字段包含签字/盖章相关关键词，通常需要跳过
        # 根据规则："法定代表人，授权代表人，后面带有"签字"字样的，不需要做填空规则或替换格式"
        signature_keywords = ['签字', '签名', '签章', '盖章处']  # 注意：不包括单独的"盖章"，因为有些字段如"单位名称（盖章）"需要填充

        # 特殊处理：对于以下关键人员字段，如果包含签字相关词，则跳过
        person_fields = ['法定代表人', '法人代表', '法人', '授权代表', '授权人', '被授权人', '代表人', '负责人']

        # 检查是否包含签字相关关键词
        has_signature_keyword = any(keyword in original_field_text for keyword in signature_keywords)

        # 特殊检查："（签字或盖章）"这种格式也要跳过
        if '签字或盖章' in original_field_text or '签字及盖章' in original_field_text or '签字并盖章' in original_field_text:
            has_signature_keyword = True

        # 检查是否是人员字段
        is_person_field = any(field in original_field_text for field in person_fields)

        # 如果是签字/盖章相关的人员字段，返回None表示跳过
        if has_signature_keyword and is_person_field:
            if enable_logging:
                from common import get_module_logger
                logger = get_module_logger("field_recognizer")
                logger.info(f"⚠️  跳过签字/盖章字段: '{original_field_text}'")
            return None

        field_text = field_text.strip().lower()

        # 移除常见后缀
        field_text = re.sub(r'（[^）]*）', '', field_text)  # 移除括号
        field_text = field_text.replace('（盖章）', '').replace('（公章）', '')
        field_text = field_text.replace('（签字）', '').replace('（签名）', '')
        field_text = field_text.strip()

        # ✅ 关键修复：移除字段名中的所有空格
        # 处理如"日      期"（日和期之间有多个空格）的情况
        field_text = re.sub(r'\s+', '', field_text)

        # 查找匹配
        std_field = self.reverse_map.get(field_text)

        # ✅ 诊断日志：特别关注"响应人名称"相关字段
        if enable_logging or '响应' in original_field_text or '应答' in original_field_text:
            if std_field:
                # 找到匹配 - 输出info日志
                pass  # 由ContentFiller输出成功日志
            else:
                # 未找到匹配 - 输出warning日志
                from common import get_module_logger
                logger = get_module_logger("field_recognizer")
                logger.warning(f"⚠️  字段识别失败: '{original_field_text}' → (清理后) '{field_text}' → 未匹配")

        return std_field

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

            # 检测并保持原括号类型
            full_match = match['full_match']
            if '（' in full_match:
                bracket_open, bracket_close = '（', '）'
            elif '[' in full_match:
                bracket_open, bracket_close = '[', ']'
            else:
                bracket_open, bracket_close = '(', ')'

            # 构建替换文本（保持原括号类型）
            replacement = f"{bracket_open}{'、'.join(values)}{bracket_close}"
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

            # 🆕 支持简写字段：如果是简写，直接使用提供的standard_field
            if match.get('is_abbreviation'):
                std_field = match.get('standard_field')
                self.logger.info(f"    识别到简写字段: {field_name} → {std_field}")
            else:
                # 常规字段识别
                std_field = self.field_recognizer.recognize_field(field_name)

            if std_field and std_field in data:
                value = str(data[std_field])

                # 跳过空值（避免填充空白内容）
                if not value or value.strip() == '':
                    self.logger.debug(f"  跳过空值字段: {field_name}")
                    continue

                # 检测并保持原括号类型
                full_match = match['full_match']
                if '（' in full_match:
                    bracket_open, bracket_close = '（', '）'
                elif '[' in full_match:
                    bracket_open, bracket_close = '[', ']'
                else:
                    bracket_open, bracket_close = '(', ')'

                # 保留括号格式并保持原括号类型
                replacement = f"{bracket_open}{value}{bracket_close}"

                # 使用run精确替换
                success = WordDocumentUtils.apply_replacement_to_runs(
                    runs, char_to_run_map, match, replacement, self.logger
                )
                if success:
                    filled_count += 1
                    self.logger.info(f"    括号字段填充: {field_name} → {replacement}")

        return filled_count > 0

    def fill_colon_field(self,
                        paragraph: Paragraph,
                        text: str,
                        matches: List[Dict],
                        data: Dict[str, Any]) -> bool:
        """填充冒号字段（使用run精确替换）

        增强功能：
        1. 使用FieldClassifier判断是否填充
        2. 正确处理格式标记（盖章、签字等）
        3. 单位盖章字段保留标记，个人签字字段跳过
        """
        if not matches:
            return False

        # 构建段落的run映射（只构建一次）
        full_text, runs, char_to_run_map = WordDocumentUtils.build_paragraph_text_map(paragraph)
        filled_count = 0

        # 从后往前处理（避免位置偏移）
        for match in reversed(matches):
            field_name = match['field']  # 清理后的字段名（用于数据匹配）
            original_field_name = match.get('original_field', field_name)  # 原始字段名（包含括号）
            after_colon = match.get('after_colon', '')  # 冒号后的内容（可能包含格式标记）
            std_field = self.field_recognizer.recognize_field(field_name)

            # ⚠️  关键修复：将冒号后的内容也传入should_fill，以便检测签字标记
            # 例如："法定代表人（负责人）或其委托代理人：                 （签字）"
            # original_field_name只包含冒号前的部分，after_colon包含"（签字）"
            full_field_text = f"{original_field_name}：{after_colon}" if after_colon else original_field_name

            # 使用FieldClassifier判断是否应该填充
            if not FieldClassifier.should_fill(full_field_text, std_field):
                # 个人签字字段不填充
                self.logger.info(f"    跳过签字字段: {full_field_text}")
                continue

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

                # 提取并处理格式标记
                format_marker = ''
                if after_colon:
                    # 调试日志：查看after_colon的内容
                    self.logger.debug(f"  after_colon内容: '{after_colon}'")
                    # 从after_colon中提取格式标记
                    marker = FieldClassifier.extract_format_marker(after_colon)
                    self.logger.debug(f"  提取的格式标记: '{marker}'")
                    if marker and FieldClassifier.should_preserve_marker(std_field, marker):
                        # 确保格式标记前有适当的空格
                        format_marker = f"{marker}"
                        self.logger.info(f"  保留格式标记: {marker}")
                    else:
                        self.logger.debug(f"  不保留格式标记，marker={marker}, should_preserve={FieldClassifier.should_preserve_marker(std_field, marker) if marker else False}")

                # 检查后面是否紧跟着其他字段，如果是则添加空格分隔
                next_char_pos = match['end']
                trailing_space = ''
                if next_char_pos < len(full_text):
                    # 检查后面是否有汉字（表示可能是下一个字段）
                    next_chars = full_text[next_char_pos:next_char_pos+5]
                    if next_chars and any('\u4e00' <= c <= '\u9fff' for c in next_chars[:2]):
                        trailing_space = '  '  # 添加两个空格分隔

                # 构建替换文本：保留原始字段名、冒号、值、格式标记
                replacement = f"{original_field_name}{colon}{value}{format_marker}{trailing_space}"

                # 使用run精确替换
                success = WordDocumentUtils.apply_replacement_to_runs(
                    runs, char_to_run_map, match, replacement, self.logger
                )
                if success:
                    filled_count += 1
                    self.logger.info(f"    冒号字段填充: {original_field_name} → {value}{format_marker}")

        return filled_count > 0

    def fill_space_field(self,
                        paragraph: Paragraph,
                        text: str,
                        matches: List[Dict],
                        data: Dict[str, Any]) -> bool:
        """填充空格填空字段（使用run精确替换）

        增强功能：
        1. 使用FieldClassifier判断是否填充
        2. 正确处理格式标记（盖章、签字等）
        """
        if not matches:
            return False

        # 构建段落的run映射（只构建一次）
        full_text, runs, char_to_run_map = WordDocumentUtils.build_paragraph_text_map(paragraph)
        filled_count = 0

        # 从后往前处理（避免位置偏移）
        for match in reversed(matches):
            field_name = match['field']  # 清理后的字段名
            original_field_name = match.get('original_field', field_name)  # 原始字段名（可能包含括号）
            std_field = self.field_recognizer.recognize_field(field_name)

            # 使用FieldClassifier判断是否应该填充
            if not FieldClassifier.should_fill(original_field_name, std_field):
                # 个人签字字段不填充
                self.logger.info(f"    跳过签字字段: {original_field_name}")
                continue

            if std_field and std_field in data:
                value = str(data[std_field])

                # 跳过空值（避免填充空白内容）
                if not value or value.strip() == '':
                    self.logger.debug(f"  跳过空值字段: {field_name}")
                    continue

                # 提取格式标记（如果有）
                format_marker = FieldClassifier.extract_format_marker(original_field_name)
                if format_marker and FieldClassifier.should_preserve_marker(std_field, format_marker):
                    # 单位字段保留盖章标记
                    replacement = f"{field_name}{format_marker}  {value}"
                else:
                    # 普通字段或不需要保留标记
                    replacement = f"{field_name}  {value}"

                # 使用run精确替换
                success = WordDocumentUtils.apply_replacement_to_runs(
                    runs, char_to_run_map, match, replacement, self.logger
                )
                if success:
                    filled_count += 1
                    self.logger.info(f"    空格填空字段填充: {original_field_name} → {value}")

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
            # ✅ 提取"年月日"部分，删除后面的时间信息
            # 匹配格式：2025年08月27日下午14:30整（北京时间） → 2025年08月27日
            date_match = re.match(r'(\d{4}年\d{1,2}月\d{1,2}日)', date_str)
            if date_match:
                return date_match.group(1)  # 只返回"年月日"部分
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
