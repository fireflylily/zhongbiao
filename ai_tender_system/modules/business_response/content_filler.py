#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
内容填充器 - 实际执行填充操作

功能：
1. 填充组合字段
2. 填充括号字段
3. 填充冒号字段
4. 填充空格字段
5. 填充日期字段

作者：AI Tender System
版本：2.0
日期：2025-10-19
"""

import re
from typing import Dict, Any, List
from docx.text.paragraph import Paragraph

from .field_classifier import FieldClassifier
from .field_recognizer import FieldRecognizer
from .utils import WordDocumentUtils


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

            # 🔍 调试日志：输出字段识别结果
            self.logger.info(f"  [fill_bracket_field] field_name='{field_name}', std_field='{std_field}'")

            # ✅ 新增：使用 should_fill 检查局部上下文（括号前后30字符）
            # 避免整个段落检查导致误判
            start_pos = max(0, match['start'] - 30)
            end_pos = min(len(full_text), match['end'] + 30)
            context_text = full_text[start_pos:end_pos]

            # 🔍 调试日志：输出 should_fill 的输入和输出
            should_fill_result = FieldClassifier.should_fill(context_text, std_field)
            self.logger.info(f"  [fill_bracket_field] should_fill(context='{context_text}', std_field='{std_field}') = {should_fill_result}")

            if not should_fill_result:
                self.logger.info(f"    跳过签字/文档字段: {context_text}")
                continue

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
