#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
内容清洗器
清理文档解析结果中的噪音和格式问题
"""

import re
from typing import Dict, List, Tuple
from dataclasses import dataclass

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from common.logger import get_module_logger

logger = get_module_logger("document_parser.content_cleaner")


@dataclass
class CleaningResult:
    """清洗结果数据类"""
    cleaned_content: str
    removed_elements: List[str]
    cleaning_stats: Dict
    quality_score: float


class ContentCleaner:
    """内容清洗器"""

    def __init__(self):
        self.logger = logger

        # 噪音模式定义
        self.noise_patterns = [
            # 页眉页脚模式
            r'第\s*\d+\s*页\s*共\s*\d+\s*页',
            r'Page\s+\d+\s+of\s+\d+',
            r'^\s*-\s*\d+\s*-\s*$',

            # 冗余空白
            r'\n\s*\n\s*\n+',  # 多个空行
            r'[ \t]+\n',        # 行尾空白
            r'\n[ \t]+',        # 行首空白

            # 特殊字符清理
            r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]',  # 控制字符
            r'[  ]+',  # 全角半角空格混用

            # PDF解析常见问题
            r'(?m)^[^a-zA-Z\u4e00-\u9fff\d\s]*$',  # 纯符号行

            # OCR错误模式
            r'[Il1]{3,}',  # 连续的I、l、1
            r'[Oo0]{3,}',  # 连续的O、o、0
        ]

        # 保留模式（不应该被删除的重要内容）
        self.preserve_patterns = [
            r'\d+[．.]\d+[．.]\d+',  # 版本号
            r'\d{4}[-/]\d{1,2}[-/]\d{1,2}',  # 日期
            r'[A-Z]{2,}\d+',  # 型号编码
            r'http[s]?://[^\s]+',  # URL
            r'\w+@\w+\.\w+',  # 邮箱
        ]

    def clean_content(self, content: str, document_type: str = "general") -> str:
        """
        清洗文档内容

        Args:
            content: 原始文档内容
            document_type: 文档类型（pdf, word, txt等）

        Returns:
            str: 清洗后的内容
        """
        if not content or not content.strip():
            return ""

        self.logger.info(f"开始内容清洗: type={document_type}, length={len(content)}")

        # 执行清洗步骤
        result = self._perform_cleaning(content, document_type)

        self.logger.info(f"内容清洗完成: "
                        f"原长度={len(content)}, "
                        f"新长度={len(result.cleaned_content)}, "
                        f"质量评分={result.quality_score:.2f}")

        return result.cleaned_content

    def _perform_cleaning(self, content: str, document_type: str) -> CleaningResult:
        """执行内容清洗的核心方法"""
        cleaned_content = content
        removed_elements = []
        stats = {'operations': []}

        # 1. 基础清理
        cleaned_content, basic_removed = self._basic_cleaning(cleaned_content)
        removed_elements.extend(basic_removed)
        stats['operations'].append('basic_cleaning')

        # 2. 格式标准化
        cleaned_content = self._normalize_format(cleaned_content)
        stats['operations'].append('format_normalization')

        # 3. 噪音移除
        cleaned_content, noise_removed = self._remove_noise(cleaned_content)
        removed_elements.extend(noise_removed)
        stats['operations'].append('noise_removal')

        # 4. 文档类型特定清理
        if document_type == "pdf":
            cleaned_content = self._clean_pdf_artifacts(cleaned_content)
        elif document_type == "word":
            cleaned_content = self._clean_word_artifacts(cleaned_content)

        # 5. 最终优化
        cleaned_content = self._final_optimization(cleaned_content)
        stats['operations'].append('final_optimization')

        # 6. 计算质量评分
        quality_score = self._calculate_quality_score(content, cleaned_content)

        return CleaningResult(
            cleaned_content=cleaned_content,
            removed_elements=removed_elements,
            cleaning_stats=stats,
            quality_score=quality_score
        )

    def _basic_cleaning(self, content: str) -> Tuple[str, List[str]]:
        """基础清理"""
        removed_elements = []

        # 移除控制字符
        original_content = content
        content = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', content)
        if len(content) != len(original_content):
            removed_elements.append("控制字符")

        # 统一换行符
        content = re.sub(r'\r\n|\r', '\n', content)

        # 移除不必要的BOM
        content = content.lstrip('\ufeff')

        return content, removed_elements

    def _normalize_format(self, content: str) -> str:
        """格式标准化"""
        # 统一空格（全角转半角）
        content = content.replace('　', ' ')  # 全角空格转半角

        # 统一标点符号
        punctuation_map = {
            '，': '，', '。': '。', '？': '？', '！': '！',
            '；': '；', '：': '：', '"': '"', '"': '"',
            "'": "'", "'": "'", '（': '（', '）': '）'
        }

        for old, new in punctuation_map.items():
            content = content.replace(old, new)

        # 规范化数字和字母
        # 全角数字和字母转半角
        full_to_half = str.maketrans(
            '０１２３４５６７８９ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ',
            '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
        )
        content = content.translate(full_to_half)

        return content

    def _remove_noise(self, content: str) -> Tuple[str, List[str]]:
        """移除噪音内容"""
        removed_elements = []

        for pattern in self.noise_patterns:
            # 检查是否匹配保留模式
            matches = re.findall(pattern, content)
            if matches:
                # 验证匹配的内容是否应该保留
                preserved_matches = []
                for match in matches:
                    should_preserve = False
                    for preserve_pattern in self.preserve_patterns:
                        if re.search(preserve_pattern, match):
                            should_preserve = True
                            break

                    if not should_preserve:
                        content = content.replace(match, '')
                        removed_elements.append(f"噪音: {match[:20]}...")
                    else:
                        preserved_matches.append(match)

        return content, removed_elements

    def _clean_pdf_artifacts(self, content: str) -> str:
        """清理PDF特有的解析问题"""
        # 修复单词断行问题
        content = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', content)

        # 修复页面分割导致的断句
        content = re.sub(r'([a-zA-Z])\s*\n\s*([a-z])', r'\1 \2', content)

        # 移除PDF页面标记
        content = re.sub(r'--- 第\d+页 ---\n?', '', content)

        # 修复表格分割线问题
        content = re.sub(r'\n\s*[─-]{5,}\s*\n', '\n', content)

        return content

    def _clean_word_artifacts(self, content: str) -> str:
        """清理Word文档特有问题"""
        # 移除多余的分页符
        content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)

        # 清理样式残留
        content = re.sub(r'\s+', ' ', content)  # 多个空格合并

        return content

    def _final_optimization(self, content: str) -> str:
        """最终优化"""
        # 合并多个空行
        content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)

        # 清理行首行尾空白
        lines = content.split('\n')
        cleaned_lines = [line.strip() for line in lines]

        # 移除空行（但保留段落分割）
        optimized_lines = []
        prev_empty = False
        for line in cleaned_lines:
            if line:
                optimized_lines.append(line)
                prev_empty = False
            elif not prev_empty:
                optimized_lines.append('')
                prev_empty = True

        content = '\n'.join(optimized_lines)

        # 最终的首尾空白清理
        content = content.strip()

        return content

    def _calculate_quality_score(self, original: str, cleaned: str) -> float:
        """计算清洗质量评分"""
        if not original:
            return 0.0

        # 基础指标
        length_ratio = len(cleaned) / len(original) if original else 0

        # 内容完整性评分
        completeness_score = 0.8 if 0.7 <= length_ratio <= 1.0 else 0.5

        # 格式质量评分
        format_score = 0.0

        # 检查是否有过多空行
        empty_line_ratio = cleaned.count('\n\n\n') / max(1, cleaned.count('\n'))
        if empty_line_ratio < 0.1:
            format_score += 0.3

        # 检查中英文混排问题
        if re.search(r'[\u4e00-\u9fff][a-zA-Z]|[a-zA-Z][\u4e00-\u9fff]', cleaned):
            format_score += 0.2  # 有中英文说明内容丰富

        # 检查标点符号规范性
        punct_issues = len(re.findall(r'[。，！？][a-zA-Z]|[.,:!?][\u4e00-\u9fff]', cleaned))
        if punct_issues == 0:
            format_score += 0.2

        # 可读性评分
        readability_score = 0.0

        # 平均句子长度合理性
        sentences = re.split(r'[。！？.!?]', cleaned)
        if sentences:
            avg_sentence_length = sum(len(s.strip()) for s in sentences) / len(sentences)
            if 10 <= avg_sentence_length <= 200:  # 合理的句子长度
                readability_score += 0.3

        # 段落结构合理性
        paragraphs = cleaned.split('\n\n')
        if 2 <= len(paragraphs) <= 100:  # 合理的段落数量
            readability_score += 0.2

        total_score = (completeness_score + format_score + readability_score) / 3
        return min(1.0, max(0.0, total_score))

    def analyze_content_quality(self, content: str) -> Dict:
        """分析内容质量"""
        if not content:
            return {'error': '内容为空'}

        analysis = {
            'length': len(content),
            'lines': len(content.split('\n')),
            'paragraphs': len([p for p in content.split('\n\n') if p.strip()]),
            'chinese_chars': len(re.findall(r'[\u4e00-\u9fff]', content)),
            'english_words': len(re.findall(r'[a-zA-Z]+', content)),
            'numbers': len(re.findall(r'\d+', content)),
            'punctuation': len(re.findall(r'[，。！？；：""''（）]', content)),
            'quality_issues': []
        }

        # 检测质量问题
        if analysis['length'] < 100:
            analysis['quality_issues'].append('内容过短')

        if analysis['chinese_chars'] == 0 and analysis['english_words'] == 0:
            analysis['quality_issues'].append('没有有效文本内容')

        # 检查空行过多
        empty_lines = content.count('\n\n\n')
        if empty_lines > analysis['lines'] * 0.3:
            analysis['quality_issues'].append('空行过多')

        # 检查重复内容
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        unique_lines = set(lines)
        if len(lines) > 10 and len(unique_lines) / len(lines) < 0.8:
            analysis['quality_issues'].append('可能存在重复内容')

        return analysis