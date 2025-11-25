#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模式匹配器 - 识别文档中的各种填空模式

支持的模式：
1. combo - 组合字段：（xxx、yyy）或（xxx和yyy）或[xxx、yyy、zzz]
2. bracket - 括号占位符：（xxx）、(xxx)、[xxx]
3. colon - 冒号填空：xxx：___  或 xxx：（空白）或 xxx：
4. space_fill - 空格填空：字段名 + 多个空格（无冒号）
5. date - 日期格式：____年____月____日 或 XXXX年X月X日

作者：AI Tender System
版本：2.0
日期：2025-10-19
"""

import re
import logging
from typing import Dict, List, Optional

from .field_classifier import FieldClassifier


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
                # 文档材料类关键词 - 精确化，避免过滤"身份证号"
                '身份证复印件', '身份证扫描件', '提供身份证',  # 精确化
                '复印件', '证明', '原件', '扫描件', '附件', '材料', '文件'
            ]
            # 特殊处理：如果包含"身份证号"，不过滤（这是数据字段）
            if '身份证号' in field_name or '身份证号码' in field_name:
                pass  # 不过滤
            elif any(skip in field_name for skip in skip_keywords):
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
        """匹配冒号填空：xxx：___  或 xxx：（空白）或 xxx：

        ⚠️ 重要测试用例（修改代码前必须验证所有用例！）：

        测试用例1: 基本填充
        输入：响应人名称：____________
        期望：识别为未填充 → 填充公司名称 ✅

        测试用例2: 带格式标记
        输入：响应人名称（盖公章）：____________
        期望：识别为未填充 → 填充公司名称 + 保留格式标记 ✅

        测试用例3: 已填充字段
        输入：响应人名称：中国联合网络通信有限公司
        期望：识别为已填充 → 跳过 ✅

        测试用例4: 横向多字段（关键！）
        输入：响应人名称：____________ 货币单位：人民币元
        期望：只匹配到"响应人名称：____________"
        结果：填充后 = "响应人名称：中国联合网络通信有限公司 货币单位：人民币元"
        ⚠️ 不能删除"货币单位：人民币元"！

        测试用例5: 个人签字字段
        输入：法定代表人（签字）：
        期望：识别到签字标记 → 不填充（由FieldClassifier处理）✅

        测试用例6: 日期字段
        输入：日期：____年____月____日
        期望：由date模式专门处理 ✅

        正则表达式说明：
        - 使用非贪婪匹配 (.*?) 避免匹配到下一个字段
        - 前瞻断言：遇到"中文+冒号"或行尾时停止
        - 这样可以正确处理横向多字段情况
        """
        logger = logging.getLogger("ai_tender_system.smart_filler")

        # 使用非贪婪匹配，遇到下一个"字段名："时停止
        pattern = r'([^：:\n]{2,20})[:：]\s*(.*?)(?=[\u4e00-\u9fa5]{2,}[:：]|$)'
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
                    # 检查是否包含"字段名：值"格式（说明混入了其他字段）
                    elif re.search(r'[\u4e00-\u9fa5]+[：:]', content_without_placeholder):
                        # 包含其他字段（如"货币单位：人民币元"），不是当前字段的内容
                        # 判定为未填充，继续处理
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
                # 文档材料类关键词 - 精确化，避免过滤"身份证号"
                '身份证复印件', '身份证扫描件', '提供身份证',  # 精确化
                '复印件', '证明', '原件', '扫描件', '附件', '材料', '文件'
            ]
            # 特殊处理：如果包含"身份证号"，不过滤（这是数据字段）
            if '身份证号' in clean_field_name or '身份证号码' in clean_field_name:
                pass  # 不过滤
            elif any(skip in clean_field_name for skip in skip_keywords):
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
