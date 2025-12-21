#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档结构解析器 - 用于 HITL 1 (人工章节选择)
功能：
- 解析 Word 文档的目录结构
- 识别章节层级（H1/H2/H3）
- 基于白名单自动推荐章节
- 提供章节预览文本
"""

import re
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from docx import Document
from docx.oxml import CT_Tbl, CT_P
from difflib import SequenceMatcher

from common import get_module_logger
from common.utils import resolve_file_path
from .level_analyzer import LevelAnalyzer

logger = get_module_logger("structure_parser")


@dataclass
class ChapterNode:
    """章节节点数据类"""
    id: str                      # 唯一ID，如 "ch_1_2_3"
    level: int                   # 层级：1=H1, 2=H2, 3=H3
    title: str                   # 章节标题
    para_start_idx: int          # 起始段落索引
    para_end_idx: int            # 结束段落索引（可能为None）
    word_count: int              # 字数统计
    preview_text: str            # 预览文本（前5行）
    auto_selected: bool          # 是否自动选中（白名单匹配）
    skip_recommended: bool       # 是否推荐跳过（黑名单匹配）
    content_tags: List[str] = None  # 内容标签（基于内容关键词检测）
    content_sample: str = None   # 内容样本（用于合同识别，1500-2000字）
    children: List['ChapterNode'] = None  # 子章节列表

    def __post_init__(self):
        if self.children is None:
            self.children = []
        if self.content_tags is None:
            self.content_tags = []

    def to_dict(self) -> Dict:
        """转换为字典（用于JSON序列化）"""
        data = asdict(self)
        data['children'] = [child.to_dict() for child in self.children]
        return data


class DocumentStructureParser:
    """文档结构解析器"""

    def __init__(self):
        """初始化解析器"""
        self.logger = get_module_logger("structure_parser")

        # ========================================
        # 新增：编号模式（用于识别章节锚点）（改进4：扩展编号模式）
        # ========================================
        self.NUMBERING_PATTERNS = [
            # 中文部分/章节编号
            r'^第[一二三四五六七八九十百\d]+部分\s*',
            r'^第[一二三四五六七八九十百\d]+章\s*',
            r'^第[一二三四五六七八九十百\d]+节\s*',
            # 数字编号
            r'^\d+\.\s*',           # 1.
            r'^\d+\.\d+\s*',        # 1.1
            r'^\d+\.\d+\.\d+\s*',   # 1.1.1
            r'^\d+\.\d+\.\d+\.\d+\s*',  # 1.1.1.1（四级编号，改进4新增）
            # 中文序号
            r'^[一二三四五六七八九十]+、\s*',
            r'^（[一二三四五六七八九十]+）\s*',
            r'^\([一二三四五六七八九十]+\)\s*',
            # 字母编号
            r'^[A-Z]\.\s*',
            r'^[a-z]\.\s*',
            r'^\([A-Za-z]\)\s*',
            # 罗马数字
            r'^[IVX]+\.\s*',
            r'^[ivx]+\.\s*',
            # 附件/附表编号（改进4新增）
            r'^附件[一二三四五六七八九十\d]+[:：]\s*',  # 附件1: 或 附件一：
            r'^附表[一二三四五六七八九十\d]+[:：]\s*',  # 附表1: 或 附表一：
            r'^附录[一二三四五六七八九十\d]+[:：]\s*',  # 附录1: 或 附录一：
        ]

        # 白名单：自动选中的关键词（改进2：扩展关键词库）
        self.WHITELIST_KEYWORDS = [
            # 投标要求类
            "投标须知", "供应商须知", "投标人须知", "资格要求", "资质要求",
            "响应人须知",  # 新增：竞争性谈判常用
            "投标邀请", "谈判邀请", "采购邀请", "招标公告", "项目概况",
            "磋商邀请",  # 新增：竞争性磋商常用
            "单一来源", "竞争性谈判", "询价公告",
            # 技术要求类
            "技术要求", "技术需求", "需求书", "技术规格", "技术参数", "性能指标", "项目需求",
            "需求说明", "技术标准", "功能要求", "技术规范", "技术方案",
            "采购需求", "服务要求", "服务内容", "服务范围",  # 新增：服务类项目常用
            # 商务要求类
            "商务要求", "商务条款", "付款方式", "交付要求", "质保要求",
            "价格要求", "报价要求",
            "合同主要条款", "付款条款", "结算方式",  # 新增：合同相关（但在白名单中）
            # 评分标准类
            "评分标准", "评标办法", "评分细则", "打分标准", "综合评分",
            "评审标准", "评审办法",
            "评价方法", "打分细则",  # 新增：评分相关变体
        ]

        # 黑名单：推荐跳过的关键词（优先级高于白名单）
        self.BLACKLIST_KEYWORDS = [
            # 合同类（包含"合同"但非要求类的标题）
            "合同条款", "合同文本", "合同范本", "合同格式", "合同协议",
            "通用条款", "专用条款", "合同主要条款", "合同草稿", "拟签合同",
            "服务合同", "采购合同", "买卖合同", "销售合同", "施工合同",
            "分包合同", "劳务合同", "租赁合同", "委托合同", "代理合同",
            # 合同元信息
            "合同编号", "合同双方", "甲方", "乙方", "丙方",
            "签订地点", "签订日期", "有效期", "合同期限",
            # 项目和公司信息
            "项目名称", "项目编号", "公司名称", "公司简介", "企业信息",
            "采购人信息", "供应商信息", "投标人信息",
            # 目录结构
            "目录", "索引", "章节目录", "内容目录",
            # 格式类
            "投标文件格式", "文件格式", "格式要求", "编制要求", "封装要求",
            "响应文件格式", "资料清单", "包装要求", "密封要求",
            # 法律声明类
            "法律声明", "免责声明", "投标承诺", "廉政承诺", "保密协议",
            "诚信承诺", "声明函", "授权书", "委托书",
            # 附件类
            "附件", "附表", "附录", "样表", "模板", "格式范本", "空白表格",
            # 说明性文字
            "填写说明", "填表说明", "使用说明", "注意事项", "特别说明",
            "备注", "参考样本", "示例", "仅供参考",
        ]

        # 标题样式名称映射（中英文）
        self.HEADING_STYLES = {
            1: ['Heading 1', '标题 1', 'heading 1', '1级标题'],
            2: ['Heading 2', '标题 2', 'heading 2', '2级标题'],
            3: ['Heading 3', '标题 3', 'heading 3', '3级标题'],
        }

    def parse_document_structure(
        self,
        doc_path: str,
        methods: Optional[List[str]] = None,
        fallback: bool = True
    ) -> Dict:
        """
        解析文档结构 - 总调用器

        支持指定解析方法或使用默认智能策略

        Args:
            doc_path: Word文档路径
            methods: 可选，指定要使用的解析方法列表，按优先级顺序尝试
                    可选值: ['toc_exact', 'semantic_anchors', 'style', 'hybrid',
                            'azure', 'outline_level', 'gemini']
                    默认None表示使用智能策略（根据文档特征自动选择）
            fallback: 可选，是否启用回退机制（当前方法失败时尝试下一个）
                     默认True

        Returns:
            {
                "success": True/False,
                "chapters": [ChapterNode.to_dict(), ...],
                "statistics": {
                    "total_chapters": 10,
                    "auto_selected": 5,
                    "skip_recommended": 3,
                    "total_words": 15000
                },
                "method": "使用的解析方法名称",
                "error": "错误信息（如果失败）"
            }
        """
        # 方法映射表
        method_map = {
            'toc_exact': self.parse_by_toc_exact,
            'azure': self.parse_by_azure,
            'outline_level': self.parse_by_outline_level,
            'gemini': self.parse_by_gemini
        }

        try:
            self.logger.info(f"开始解析文档结构: {doc_path}")

            # ⭐️ 文件格式检测：不支持旧版.doc格式
            if doc_path.lower().endswith('.doc'):
                error_message = (
                    "暂不支持旧版 .doc 格式文档的章节解析。\n\n"
                    "请按以下步骤操作：\n"
                    "1. 使用 Microsoft Word 或 WPS Office 打开该文件\n"
                    '2. 点击"文件" → "另存为"\n'
                    '3. 在"保存类型"中选择 "Word 文档 (*.docx)"\n'
                    "4. 保存后重新上传 .docx 文件\n\n"
                    "提示：.docx 格式兼容性更好，推荐使用。"
                )
                self.logger.error(f".doc 文件不支持: {doc_path}")
                raise ValueError(error_message)

            # 场景1: 用户指定了具体方法
            if methods is not None:
                self.logger.info(f"使用指定方法: {methods}, fallback={fallback}")

                for method_name in methods:
                    if method_name not in method_map:
                        self.logger.warning(f"未知方法: {method_name}，跳过")
                        continue

                    self.logger.info(f"尝试方法: {method_name}")
                    result = method_map[method_name](doc_path)

                    # 判断成功标准
                    if result.get('success'):
                        # 检查是否识别到足够的章节
                        chapters = result.get('chapters', [])
                        if len(chapters) >= 1:  # 至少识别到1个章节
                            self.logger.info(f"方法 {method_name} 成功，识别到 {len(chapters)} 个章节")
                            return result
                        else:
                            self.logger.warning(f"方法 {method_name} 未识别到章节")

                    # 如果不启用fallback，直接返回结果（即使失败）
                    if not fallback:
                        self.logger.info(f"fallback=False，直接返回 {method_name} 的结果")
                        return result

                    # 否则继续尝试下一个方法
                    self.logger.warning(f"方法 {method_name} 失败或效果不佳，尝试下一个方法")

                # 所有方法都失败
                return {
                    "success": False,
                    "chapters": [],
                    "statistics": {},
                    "error": f"所有指定方法({methods})都失败",
                    "method": "none"
                }

            # 场景2: 默认智能策略（优化版：精确识别 → 大纲识别）
            self.logger.info("使用优化策略：精确识别 → 大纲识别")

            # 1️⃣ 首先尝试精确识别（基于目录）
            result = self.parse_by_toc_exact(doc_path)

            if result['success'] and len(result.get('chapters', [])) >= 1:
                # 精确识别成功
                self.logger.info("✅ 精确识别成功")
                return result
            else:
                # 2️⃣ 精确识别失败（无目录或解析失败），回退到大纲识别
                self.logger.info("⚠️ 精确识别失败，回退到大纲识别")
                result = self.parse_by_outline_level(doc_path)
                return result

        except Exception as e:
            self.logger.error(f"文档结构解析失败: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return {
                "success": False,
                "chapters": [],
                "statistics": {},
                "error": str(e),
                "method": "error"
            }

    # ============================================
    # 独立解析方法 - 可单独调用或组合使用
    # ============================================

    def parse_by_toc_exact(self, doc_path: str) -> Dict:
        """
        方法0: 精确匹配(基于目录)

        直接使用目录项精确匹配正文位置,速度快、准确率高

        Args:
            doc_path: Word文档路径

        Returns:
            {
                "success": True/False,
                "chapters": [...],
                "statistics": {...},
                "method": "toc_exact"
            }
        """
        try:
            doc_path_abs = resolve_file_path(doc_path)
            if not doc_path_abs:
                raise FileNotFoundError(f"无法解析文件路径: {doc_path}")

            doc = Document(str(doc_path_abs))

            # 检测目录
            toc_idx = self._find_toc_section(doc)
            if toc_idx is None:
                return {
                    "success": False,
                    "error": "未检测到目录,无法使用精确匹配方法",
                    "chapters": [],
                    "statistics": {},
                    "method": "toc_exact"
                }

            toc_items, toc_end_idx = self._parse_toc_items(doc, toc_idx)
            if not toc_items:
                return {
                    "success": False,
                    "error": "目录解析失败",
                    "chapters": [],
                    "statistics": {},
                    "method": "toc_exact"
                }

            # 使用精确匹配
            chapters = self._locate_chapters_by_toc(doc, toc_items, toc_end_idx)
            chapter_tree = self._build_chapter_tree(chapters)
            chapter_tree = self._propagate_skip_status(chapter_tree)
            stats = self._calculate_statistics(chapter_tree)

            return {
                "success": True,
                "chapters": [ch.to_dict() for ch in chapter_tree],
                "statistics": stats,
                "method": "toc_exact"
            }

        except Exception as e:
            self.logger.error(f"精确匹配解析失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "chapters": [],
                "statistics": {},
                "method": "toc_exact"
            }

    def parse_by_outline_level(self, doc_path: str) -> Dict:
        """
        方法5: Word大纲级别识别

        使用Word文档大纲级别(Outline Level)识别章节

        Args:
            doc_path: Word文档路径

        Returns:
            {
                "success": True/False,
                "chapters": [...],
                "statistics": {...},
                "method": "outline_level"
            }
        """
        try:
            doc_path_abs = resolve_file_path(doc_path)
            if not doc_path_abs:
                raise FileNotFoundError(f"无法解析文件路径: {doc_path}")

            doc = Document(str(doc_path_abs))

            # 1. 基于Word大纲级别识别章节
            chapters = self._parse_chapters_by_outline_level(doc)

            # 2. 🆕 使用智能层级分析器修正层级(与精确识别保持一致)
            if chapters:
                from modules.tender_processing.level_analyzer import LevelAnalyzer

                # 转换为类似目录项的格式
                toc_like_items = [
                    {'title': ch.title, 'level': ch.level}
                    for ch in chapters
                ]

                # 使用contextual方法智能分析层级
                analyzer = LevelAnalyzer()
                corrected_levels = analyzer.analyze_toc_hierarchy_contextual(toc_like_items)

                # 更新章节层级
                for i, level in enumerate(corrected_levels):
                    chapters[i].level = level

                # 统计日志
                from collections import Counter
                level_dist = Counter(corrected_levels)
                self.logger.info(f"✅ 智能层级分析完成,修正 {len(chapters)} 个章节: {dict(level_dist)}")

            # 3. 后续处理(定位内容、构建树、统计)
            chapters = self._locate_chapter_content(doc, chapters)
            chapter_tree = self._build_chapter_tree(chapters)
            chapter_tree = self._propagate_skip_status(chapter_tree)
            stats = self._calculate_statistics(chapter_tree)

            return {
                "success": True,
                "chapters": [ch.to_dict() for ch in chapter_tree],
                "statistics": stats,
                "method": "outline_level"
            }

        except Exception as e:
            self.logger.error(f"大纲级别识别失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "chapters": [],
                "statistics": {},
                "method": "outline_level"
            }

    def parse_by_azure(self, doc_path: str) -> Dict:
        """
        方法4: Azure Form Recognizer解析

        使用Azure AI服务识别文档结构

        Args:
            doc_path: Word文档路径

        Returns:
            {
                "success": True/False,
                "chapters": [...],
                "statistics": {...},
                "method": "azure"
            }
        """
        try:
            # 检查Azure解析器是否可用
            try:
                from modules.tender_processing.azure_parser import AzureDocumentParser, is_azure_available

                if not is_azure_available():
                    return {
                        "success": False,
                        "error": "Azure Form Recognizer未配置或SDK未安装",
                        "chapters": [],
                        "statistics": {},
                        "method": "azure"
                    }

                doc_path_abs = resolve_file_path(doc_path)
                if not doc_path_abs:
                    raise FileNotFoundError(f"无法解析文件路径: {doc_path}")

                # 使用Azure解析器
                azure_parser = AzureDocumentParser()
                result = azure_parser.parse_document_structure(str(doc_path_abs))
                return result

            except ImportError as e:
                return {
                    "success": False,
                    "error": f"Azure解析器不可用: {str(e)}",
                    "chapters": [],
                    "statistics": {},
                    "method": "azure"
                }

        except Exception as e:
            self.logger.error(f"Azure解析失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "chapters": [],
                "statistics": {},
                "method": "azure"
            }

    def parse_by_gemini(self, doc_path: str) -> Dict:
        """
        方法6: Gemini AI解析

        使用Google Gemini AI模型识别文档结构

        Args:
            doc_path: Word文档路径

        Returns:
            {
                "success": True/False,
                "chapters": [...],
                "statistics": {...},
                "method": "gemini"
            }
        """
        try:
            # 检查Gemini解析器是否可用
            try:
                from modules.tender_processing.parsers.gemini_parser import GeminiParser

                gemini_parser = GeminiParser()

                if not gemini_parser.is_available():
                    return {
                        "success": False,
                        "error": "Gemini API密钥未配置",
                        "chapters": [],
                        "statistics": {},
                        "method": "gemini"
                    }

                doc_path_abs = resolve_file_path(doc_path)
                if not doc_path_abs:
                    raise FileNotFoundError(f"无法解析文件路径: {doc_path}")

                # 使用Gemini解析器
                result = gemini_parser.parse_structure(str(doc_path_abs))

                # 确保chapters是dict格式
                if result.get('success') and result.get('chapters'):
                    chapters = result['chapters']
                    if chapters and hasattr(chapters[0], 'to_dict'):
                        result['chapters'] = [ch.to_dict() if hasattr(ch, 'to_dict') else ch for ch in chapters]

                return result

            except ImportError as e:
                return {
                    "success": False,
                    "error": f"Gemini解析器不可用: {str(e)} (pip install google-generativeai)",
                    "chapters": [],
                    "statistics": {},
                    "method": "gemini"
                }

        except Exception as e:
            self.logger.error(f"Gemini解析失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "chapters": [],
                "statistics": {},
                "method": "gemini"
            }

    def _is_title_page_content(self, para_idx: int, para_text: str, total_paras: int) -> bool:
        """
        判断是否为标题页内容 (优化5: 过滤标题页)

        规则:
        1. 位于前10个段落
        2. 不包含章节编号
        3. 字体很大但没有"第X章"等关键词
        4. 包含"公司"、"项目"等纯名称特征

        Args:
            para_idx: 段落索引
            para_text: 段落文本
            total_paras: 文档总段落数

        Returns:
            True 表示应该被过滤
        """
        # 只检查前10段
        if para_idx >= 10:
            return False

        # 包含章节编号则不是标题页
        if re.match(r'^第[一二三四五六七八九十\d]+[章节部分]', para_text):
            return False

        if re.match(r'^\d+\.\s', para_text):
            return False

        # 纯公司名称模式
        if re.match(r'^.{2,50}(有限公司|股份有限公司|集团有限公司|集团)$', para_text):
            self.logger.debug(f"标题页过滤: 识别为公司名称 '{para_text}'")
            return True

        # 纯项目名称模式 (不包含"项目需求"、"项目要求"等)
        if re.match(r'^.{5,50}项目$', para_text) and '需求' not in para_text and '要求' not in para_text and '概况' not in para_text:
            self.logger.debug(f"标题页过滤: 识别为项目名称 '{para_text}'")
            return True

        # 纯年份项目模式 (如 "2025年XX项目")
        if re.match(r'^\d{4}年.{5,50}项目$', para_text) and '需求' not in para_text:
            self.logger.debug(f"标题页过滤: 识别为年份项目名称 '{para_text}'")
            return True

        # 纯文档名称模式 (如 "采购需求文件"但没有编号)
        if re.match(r'^.{2,15}(文件|文档|材料|资料)$', para_text) and para_idx < 5:
            # 进一步判断: 如果后面紧跟"第一章"等，则是标题页
            if para_idx + 1 < total_paras:
                next_para_match = False
                for i in range(para_idx + 1, min(para_idx + 3, total_paras)):
                    # 检查后续段落是否包含章节标记
                    # 这里只检查文本，不需要读取实际段落对象
                    pass  # 暂时保留简化逻辑
            self.logger.debug(f"标题页过滤: 识别为文档名称 '{para_text}'")
            return True

        return False

    def _is_valid_chapter_title(self, text: str) -> bool:
        """
        判断文本是否是合法的章节标题 (过滤列表项、说明性内容等)

        Args:
            text: 段落文本

        Returns:
            True 表示可能是章节标题，False 表示应该被过滤
        """
        if not text or len(text.strip()) == 0:
            return False

        # 1. 过滤纯编号（如 "1"、"1.1"）
        if re.match(r'^[\d\.]+$', text):
            return False

        # 2. 过滤纯列表项标记（如 "1."、"2."、"(1)"）
        if re.match(r'^[\d]+\.$', text):  # "1." "2."
            return False
        if re.match(r'^\([\d]+\)$', text):  # "(1)" "(2)"
            return False
        if re.match(r'^[一二三四五六七八九十]+、$', text):  # "一、" "二、"
            return False

        # 3. 过滤说明性内容的特征关键词
        note_keywords = ['注：', '注:', '说明：', '说明:', '备注：', '备注:']
        if any(text.startswith(kw) for kw in note_keywords):
            # "注："本身可能不是章节，但如果后面有内容可能是
            # 如果只有"注："两个字，肯定不是章节标题
            if len(text) <= 4:
                return False

        # 4. 过滤超长内容（章节标题一般不超过50个字符）
        # 但允许包含长条款编号的章节（如 "7.3 双方均应当..."）
        if len(text) > 100:  # 超过100字符肯定不是标题
            return False

        # 5. 过滤纯列表项格式（开头是编号+简短内容）
        # 例如: "1.以上响应文件的构成为必须包含的内容..."
        if re.match(r'^[\d]+\.[\u4e00-\u9fa5]{2,}', text):
            # 如果匹配 "数字.中文"，且没有明确的章节特征词，则可能是列表项
            # 检查是否包含章节特征词
            chapter_markers = ['章', '节', '部分', '第', '条款', '要求', '标准', '方法', '原则']
            if not any(marker in text for marker in chapter_markers):
                # 进一步检查：如果内容很长（>20字符），可能是说明性列表项
                if len(text) > 30:
                    return False

        # 6. 特殊过滤：排除纯条款编号（如 "1.1.1"、"2.3.4.5"）
        if re.match(r'^[\d]+\.[\d]+\.[\d]+(\.[\d]+)*$', text):
            return False

        # 7. 特殊过滤：排除以条款编号开头且过长的内容
        # 例如: "7.3 双方均应当严格按照相关法律法规..."（这不是章节标题）
        if re.match(r'^[\d]+\.[\d]+\s+', text) and len(text) > 50:
            return False

        return True

    def _parse_chapters_by_outline_level(self, doc: Document) -> List[ChapterNode]:
        """
        方法五：基于Word大纲级别（outlineLevel）识别章节

        使用微软官方的大纲级别API，支持0-8级标题识别，
        包含3层精细过滤规则和Heading样式备用检测。

        Args:
            doc: python-docx Document 对象

        Returns:
            章节列表（扁平结构，未构建树）
        """
        import re

        chapters = []
        chapter_counter = 0

        self.logger.info("使用方法五：大纲级别识别（增强版）")

        # 直接从Word文档提取标题 - 使用微软官方的大纲级别API
        for para_idx, paragraph in enumerate(doc.paragraphs):
            is_heading = False
            level = 0
            detection_method = ""

            # ⭐ 优先级1: 检查大纲级别 (Outline Level) - 微软官方语义标记
            # 这是Word导航窗格和大纲视图使用的结构，准确度最高
            try:
                pPr = paragraph._element.pPr
                if pPr is not None:
                    outlineLvl = pPr.outlineLvl
                    if outlineLvl is not None:
                        outline_level_val = int(outlineLvl.val)
                        # Word大纲级别: 0-8表示标题(0=一级), 9表示正文
                        if outline_level_val <= 8:
                            # 🔧 添加过滤规则，排除噪音内容
                            text = paragraph.text.strip()
                            should_skip = False

                            # 过滤1: 跳过文档前30段的封面/元数据（Level 0）
                            if para_idx < 30 and outline_level_val == 0:
                                metadata_keywords = ['项目编号', '招标人', '代理机构', '联系人', '联系方式',
                                                    '地址', '电话', '传真', '邮编', '网址', 'http']
                                if any(kw in text for kw in metadata_keywords):
                                    should_skip = True
                                    self.logger.debug(f"过滤封面: 段落{para_idx} '{text[:30]}'")

                            # 过滤2: 跳过Level 3-4的长条款内容
                            if not should_skip and outline_level_val >= 3:
                                # 形如 "1.1 这是一个很长的说明文字..." 的是条款，不是标题
                                if re.match(r'^\d+\.\d+\s+.{15,}', text):
                                    should_skip = True
                                    self.logger.debug(f"过滤条款: 段落{para_idx} '{text[:30]}'")

                            # 过滤3: 标题长度限制（超过50字的通常不是标题）
                            if not should_skip and len(text) > 50:
                                # 除非有明确的章节编号
                                if not re.match(r'^第[一二三四五六七八九十\d]+[章部分]', text):
                                    should_skip = True
                                    self.logger.debug(f"过滤长文本: 段落{para_idx} '{text[:30]}'")

                            if not should_skip:
                                is_heading = True
                                level = outline_level_val + 1  # 转换: 0→1级, 1→2级, ...
                                detection_method = f"大纲级别{outline_level_val}"
            except (AttributeError, TypeError, ValueError):
                pass  # 没有大纲级别，继续其他方法

            # 优先级2: 检查标准Heading样式 (备用方案)
            if not is_heading:
                style_name = paragraph.style.name if paragraph.style else ""

                # 只接受标准的Heading样式（精确匹配，避免误识别）
                if style_name.startswith('Heading '):  # 'Heading 1', 'Heading 2'
                    match = re.search(r'Heading (\d+)', style_name)
                    if match:
                        is_heading = True
                        level = int(match.group(1))
                        detection_method = f"样式{style_name}"
                elif style_name.startswith('标题 '):  # '标题 1', '标题 2'
                    match = re.search(r'标题 (\d+)', style_name)
                    if match:
                        is_heading = True
                        level = int(match.group(1))
                        detection_method = f"样式{style_name}"

            if is_heading and paragraph.text.strip():
                title = paragraph.text.strip()

                # 判断是否匹配白/黑名单
                auto_selected = self._matches_whitelist(title)
                skip_recommended = self._matches_blacklist(title)

                if skip_recommended:
                    auto_selected = False

                chapter = ChapterNode(
                    id=f"docx_{chapter_counter}",
                    level=level if level > 0 else 1,
                    title=title,
                    para_start_idx=para_idx,
                    para_end_idx=None,  # 稍后计算
                    word_count=0,       # 稍后计算
                    preview_text="",    # 稍后提取
                    auto_selected=auto_selected,
                    skip_recommended=skip_recommended,
                    content_tags=['docx_native', detection_method]
                )

                chapters.append(chapter)
                chapter_counter += 1

                self.logger.debug(
                    f"识别标题: 段落{para_idx} [{detection_method}] '{title[:50]}' "
                    f"{'✅自动选中' if auto_selected else '❌跳过' if skip_recommended else '⚪默认'}"
                )

        self.logger.info(f"✅ 方法五识别完成：找到 {len(chapters)} 个标题")
        return chapters

    def _get_heading_level(self, paragraph) -> int:
        """
        获取段落的标题层级 (优化6: 添加前置过滤和大纲级别检查)

        Args:
            paragraph: python-docx Paragraph 对象

        Returns:
            0: 不是标题
            1-3: 标题层级
        """
        text = paragraph.text.strip()

        # ⚠️ 方法0：前置过滤 - 排除明显不是章节的内容
        if not self._is_valid_chapter_title(text):
            return 0

        # ⭐ 方法1：大纲级别判断（最可靠，优先级最高）
        try:
            pPr = paragraph._element.pPr
            if pPr is not None:
                outlineLvl = pPr.outlineLvl
                if outlineLvl is not None:
                    level = int(outlineLvl.val)
                    if level <= 2:  # 0=一级, 1=二级, 2=三级
                        self.logger.debug(f"✓ 大纲级别识别: Level {level} → '{text[:30]}'")
                        return level + 1  # 转换为1-3
        except (AttributeError, TypeError):
            pass  # 没有大纲级别，继续其他方法

        # 方法2：通过样式名判断 (优先，最可靠)
        if paragraph.style and paragraph.style.name:
            style_name = paragraph.style.name
            for level, style_names in self.HEADING_STYLES.items():
                if any(sn.lower() in style_name.lower() for sn in style_names):
                    return level

        # 方法3：通过 XML 样式属性判断（更准确）
        try:
            pPr = paragraph._element.pPr
            if pPr is not None:
                pStyle = pPr.pStyle
                if pStyle is not None:
                    style_val = pStyle.val
                    if 'heading1' in style_val.lower() or style_val.lower() == '1':
                        return 1
                    elif 'heading2' in style_val.lower() or style_val.lower() == '2':
                        return 2
                    elif 'heading3' in style_val.lower() or style_val.lower() == '3':
                        return 3
        except (AttributeError, TypeError):
            pass  # XML属性不可用时使用其他方法

        # 方法4：通过文本格式启发式判断 (优化: 收集所有run的信息)
        if paragraph.runs:
            # 收集所有run的字体信息
            sizes = []
            bold_count = 0

            for run in paragraph.runs:
                if run.font.size:
                    sizes.append(run.font.size.pt)
                if run.bold:
                    bold_count += 1

            # 至少一半的run是加粗，才认为是标题
            if sizes and bold_count >= len(paragraph.runs) / 2:
                avg_size = sum(sizes) / len(sizes)

                # 调整阈值: 更灵活的判断 (降低阈值以提高识别率)
                if avg_size >= 16:  # 16pt+ → Level 1 (原18pt)
                    return 1
                elif avg_size >= 13:  # 13-15pt → Level 2 (原15pt)
                    return 2
                elif avg_size >= 10:  # 10-12pt → Level 3 (原12pt)
                    return 3

        # 方法5：通过编号模式判断 (增强fallback机制)
        # 一级标题模式
        if re.match(r'^第[一二三四五六七八九十\d]+[章部分]', text):
            return 1
        if re.match(r'^\d+\.\s+\S', text) and not re.match(r'^\d+\.\d+', text):  # 1. xxx (不包含1.1)
            return 1

        # 二级标题模式 (如果文本较短且有编号)
        if re.match(r'^\d+\.\d+\s+\S', text) and not re.match(r'^\d+\.\d+\.\d+', text):
            if len(text.strip()) <= 100:  # 长度限制
                return 2

        # 三级标题模式
        if re.match(r'^\d+\.\d+\.\d+\s+\S', text):
            if len(text.strip()) <= 100:
                return 3

        return 0

    def _clean_title_v2(self, title: str, aggressive=False) -> str:
        """
        分阶段清理标题文本 (优化3: 温和/激进两种模式)

        Args:
            title: 原始标题
            aggressive: 是否使用激进清理模式

        Returns:
            清理后的标题
        """
        if not aggressive:
            # 温和清理: 只删除明显的编号和空格
            cleaned = re.sub(r'^\d+\.\s*', '', title)  # 删除 "1. "
            cleaned = re.sub(r'^\d+\.\d+\s*', '', cleaned)  # 删除 "1.1 "
            cleaned = re.sub(r'^\d+\.\d+\.\d+\s*', '', cleaned)  # 删除 "1.1.1 "
            cleaned = re.sub(r'^第[一二三四五六七八九十\d]+[章节部分]\s*', '', cleaned)  # 删除 "第一章 "
            cleaned = re.sub(r'\s+', '', cleaned)  # 删除空格
            return cleaned
        else:
            # 激进清理: 删除所有编号、符号和空格
            cleaned = title
            cleaned = re.sub(r'^[一二三四五六七八九十]+、\s*', '', cleaned)
            cleaned = re.sub(r'^\([一二三四五六七八九十\d]+\)\s*', '', cleaned)
            cleaned = re.sub(r'^\d+[-\.]\d*\s*', '', cleaned)
            cleaned = re.sub(r'^[A-Za-z]+\.\s*', '', cleaned)
            cleaned = re.sub(r'^第[一二三四五六七八九十\d]+[章节部分]\s*', '', cleaned)
            cleaned = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9]', '', cleaned)  # 只保留中英文数字
            return cleaned

    def fuzzy_match_title_v2(self, title1: str, title2: str, threshold=0.7) -> float:
        """
        模糊匹配标题，支持多级清理尝试 (优化3: 分阶段匹配)

        Args:
            title1: 标题1
            title2: 标题2
            threshold: 相似度阈值

        Returns:
            相似度得分 (0.0-1.0)
        """
        # Level 1: 原始比较
        if title1 == title2:
            return 1.0

        # Level 2: 温和清理后比较
        clean1 = self._clean_title_v2(title1, aggressive=False)
        clean2 = self._clean_title_v2(title2, aggressive=False)

        if clean1 == clean2:
            return 0.95

        if clean1 in clean2 or clean2 in clean1:
            return 0.90

        # Level 3: 激进清理后比较
        aggr1 = self._clean_title_v2(title1, aggressive=True)
        aggr2 = self._clean_title_v2(title2, aggressive=True)

        if aggr1 == aggr2:
            return 0.85

        if aggr1 in aggr2 or aggr2 in aggr1:
            shorter = aggr1 if len(aggr1) <= len(aggr2) else aggr2
            longer = aggr2 if len(aggr1) <= len(aggr2) else aggr1
            return len(shorter) / len(longer) * 0.80  # 包含匹配，根据长度比例打分

        # Level 4: SequenceMatcher相似度
        similarity = SequenceMatcher(None, aggr1, aggr2).ratio()

        return similarity

    def _matches_whitelist(self, title: str) -> bool:
        """检查标题是否匹配白名单"""
        return any(keyword in title for keyword in self.WHITELIST_KEYWORDS)

    def _matches_blacklist(self, title: str) -> bool:
        """检查标题是否匹配黑名单"""
        # 1. 关键词匹配
        if any(keyword in title for keyword in self.BLACKLIST_KEYWORDS):
            return True

        # 2. 特殊模式匹配
        special_patterns = [
            # 匹配纯公司名称章节（如 "中国光大银行股份有限公司"、"XXX公司"）
            r'^.{2,30}(有限公司|股份有限公司|集团有限公司|集团)$',
            # 匹配甲乙丙方开头的章节
            r'^(甲方|乙方|丙方)[:：]',
            # 匹配纯项目名称章节（如 "XXX项目"，但不包括 "项目需求"、"项目概况" 等）
            r'^.{1,20}项目$',  # 以"项目"结尾，前面是项目名称
            # 匹配合同编号格式章节
            r'.*编号[:：].{0,50}$',  # 包含 "编号:" 或 "编号："
        ]

        for pattern in special_patterns:
            if re.match(pattern, title.strip()):
                return True

        # 3. 匹配空白或极短章节（< 3个字符，可能是格式错误）
        if len(title.strip()) < 3:
            return True

        return False

    def _calculate_contract_density(self, text: str) -> float:
        """
        计算文本的合同密度（合同特征词出现频率）

        Args:
            text: 待分析的文本内容

        Returns:
            合同密度（0-1之间的浮点数）
        """
        if not text or len(text) < 100:  # 文本太短，无法判断
            return 0.0

        # 定义合同特征词及其权重
        contract_keywords = {
            # 强合同特征（权重 x3）
            '甲方': 3, '乙方': 3, '丙方': 3,
            # 中等合同特征（权重 x2）
            '违约金': 2, '违约责任': 2, '履约保证金': 2, '本合同': 2,
            '合同生效': 2, '合同终止': 2, '合同解除': 2,
            # 弱合同特征（权重 x1）
            '付款': 1, '验收': 1, '保密': 1, '争议': 1,
            '仲裁': 1, '管辖': 1, '双方': 1, '签订': 1
        }

        # 计算加权出现次数
        total_weight = 0
        for keyword, weight in contract_keywords.items():
            count = text.count(keyword)
            total_weight += count * weight

        # 计算密度（每1000字符的加权关键词出现次数）
        text_length = len(text)
        density = (total_weight / text_length) * 1000

        # 归一化到0-1之间（假设密度>50就是100%的合同）
        normalized_density = min(density / 50.0, 1.0)

        return normalized_density

    def _is_contract_chapter(self, title: str, content_sample: str = None) -> tuple:
        """
        判断章节是否为合同章节（增强版：结合标题、内容、排除规则）

        Args:
            title: 章节标题
            content_sample: 章节内容样本（可选）

        Returns:
            (is_contract, density, reason): 是否为合同章节、合同密度、判断理由
        """
        # 🆕 0. 排除规则优先（避免误判）
        exclude_keywords = [
            "投标人须知", "供应商须知", "投标邀请", "投标须知", "招标须知",
            "附件", "投标文件格式", "响应文件格式", "投标文件组成", "谈判响应文件格式",
            "用户需求", "需求书", "技术要求", "技术规格", "技术需求书", "技术需求",
            "评分", "评审", "评标", "开标", "报价", "投标报价",
            "投标邀请函", "采购邀请", "谈判邀请"
        ]

        for exclude_kw in exclude_keywords:
            if exclude_kw in title:
                self.logger.debug(f"  ⛔ 排除章节: '{title}' - 匹配排除关键词'{exclude_kw}'")
                return (False, 0.0, f"排除规则: '{exclude_kw}'")

        # 1. 基于标题的强合同标识（保留原有逻辑）
        strong_contract_keywords = [
            "合同条款", "合同文本", "合同范本", "合同格式", "合同协议",
            "通用条款", "专用条款", "合同主要条款", "合同草稿", "拟签合同",
            "服务合同", "采购合同", "买卖合同", "销售合同", "施工合同",
            "分包合同", "劳务合同", "租赁合同", "委托合同", "代理合同",
        ]

        for keyword in strong_contract_keywords:
            if keyword in title:
                return (True, 1.0, f"标题强匹配: '{keyword}'")

        # 2. 基于内容的合同密度检测（🆕 提高阈值，降低误判）
        if content_sample:
            density = self._calculate_contract_density(content_sample)

            # 🆕 高密度阈值：从5%提高到10%
            high_density_threshold = 0.10

            if density > high_density_threshold:
                # 高密度需要标题验证，避免误判"引用合同内容"的章节
                title_has_contract_kw = any(kw in title for kw in ["合同", "协议", "条款", "甲方", "乙方"])

                if title_has_contract_kw:
                    return (True, density, f"高密度+标题验证: {density:.1%}")
                else:
                    # 密度高但标题不像合同，可能是引用合同内容
                    self.logger.debug(f"  ⚠️  高密度({density:.1%})但标题不匹配: '{title}'")
                    return (False, density, f"高密度但标题不匹配: {density:.1%}")

        # 3. 弱合同标识（标题模糊但可能是合同）- 保留原有逻辑
        weak_contract_patterns = [
            r'(第[一二三四五六七八九十\d]+部分|附件\d*)[^\u4e00-\u9fa5]*(协议|条款|权利|义务)',
            r'双方.*权利.*义务',
            r'甲.*乙.*方',
        ]

        import re
        for pattern in weak_contract_patterns:
            if re.search(pattern, title):
                # 如果有内容样本，进一步验证
                if content_sample:
                    density = self._calculate_contract_density(content_sample)
                    # 🆕 提高弱匹配的密度阈值：从3%提高到5%
                    if density > 0.05:
                        return (True, density, f"标题弱匹配+内容验证: {density:.1%}")

        return (False, 0.0, "非合同章节")

    def _extract_content_sample(self, doc: Document, para_start_idx: int, para_end_idx: int, sample_size: int = 2000) -> str:
        """
        提取章节内容样本（用于合同识别）

        Args:
            doc: Word文档对象
            para_start_idx: 起始段落索引
            para_end_idx: 结束段落索引
            sample_size: 样本大小（字符数）

        Returns:
            内容样本字符串
        """
        if para_end_idx is None or para_end_idx <= para_start_idx:
            return ""

        # 提取章节内容（跳过标题本身）
        content_paras = doc.paragraphs[para_start_idx + 1 : para_end_idx + 1]

        # 合并文本
        sample_text = ""
        for para in content_paras:
            text = para.text.strip()
            if text:
                sample_text += text + "\n"
                if len(sample_text) >= sample_size:
                    break

        # 截取指定长度
        return sample_text[:sample_size]

    def _calculate_paragraph_contract_score(self, doc: Document, para_idx: int, window_size: int = 20) -> float:
        """
        计算段落周围的合同密度分数（滑动窗口）

        用于在识别章节时快速判断该段落是否位于合同区域内

        Args:
            doc: Word文档对象
            para_idx: 段落索引
            window_size: 窗口大小（检查前后N个段落，默认20）

        Returns:
            合同密度分数 (0.0-1.0)
        """
        # 计算窗口范围（前后各一半）
        half_window = window_size // 2
        start_idx = max(0, para_idx - half_window)
        end_idx = min(len(doc.paragraphs), para_idx + half_window + 1)

        # 提取窗口内的文本
        window_text = ""
        for i in range(start_idx, end_idx):
            para_text = doc.paragraphs[i].text.strip()
            if para_text:
                window_text += para_text + "\n"

        # 使用现有的合同密度计算方法
        density = self._calculate_contract_density(window_text)

        return density

    def _detect_contract_cluster_in_chapter(self, doc: Document, start_idx: int, end_idx: int) -> Optional[Dict]:
        """
        检测章节内的合同段落聚集区（精确定位起始位置）

        策略：
        1. 用50段滑动窗口扫描整个章节
        2. 找到第一个合同密度>20%的区域
        3. 从该区域向前精确定位聚集区起点（找到第一个包含合同特征的段落）

        Args:
            doc: Word文档对象
            start_idx: 章节起始段落索引
            end_idx: 章节结束段落索引

        Returns:
            如果发现聚集区：{'start': int, 'end': int, 'density': float}
            否则返回 None
        """
        # 🆕 参数验证：防止 end_idx 为 None 或无效值
        if end_idx is None or start_idx is None:
            self.logger.debug(f"  ⚠️  参数无效: start_idx={start_idx}, end_idx={end_idx}，跳过合同聚集区检测")
            return None

        if end_idx <= start_idx:
            self.logger.debug(f"  ⚠️  章节范围无效: start_idx={start_idx}, end_idx={end_idx}，跳过合同聚集区检测")
            return None

        if end_idx - start_idx < 50:
            # 章节太短，不需要检测
            return None

        window_size = 50  # 窗口大小：50个段落
        density_threshold = 0.2  # 密度阈值：20%
        step_size = 10  # 滑动步长：每次移动10段

        # 滑动窗口扫描
        for i in range(start_idx, end_idx - window_size, step_size):
            window_end = min(i + window_size, end_idx)

            # 提取窗口内文本
            window_text = ""
            for j in range(i, window_end):
                if j < len(doc.paragraphs):
                    para_text = doc.paragraphs[j].text.strip()
                    if para_text:
                        window_text += para_text + "\n"

            # 计算合同密度
            density = self._calculate_contract_density(window_text)

            if density > density_threshold:
                # 找到高密度区域，向前精确定位起点
                cluster_start = i

                # 向前查找第一个包含强合同特征的段落
                strong_contract_keywords = ['甲方', '乙方', '本合同', '合同的组成', '合同组成']

                for j in range(i, start_idx - 1, -1):  # 向前查找
                    if j < len(doc.paragraphs):
                        para_text = doc.paragraphs[j].text.strip()
                        if any(kw in para_text for kw in strong_contract_keywords):
                            cluster_start = j
                        else:
                            # 找到不含合同特征的段落，停止
                            break

                # 确定聚集区结束位置（向后扫描，找到密度降低的位置）
                cluster_end = end_idx
                for j in range(window_end, end_idx, 10):
                    check_end = min(j + 50, end_idx)
                    check_text = "\n".join(
                        doc.paragraphs[k].text.strip()
                        for k in range(j, check_end)
                        if k < len(doc.paragraphs) and doc.paragraphs[k].text.strip()
                    )
                    check_density = self._calculate_contract_density(check_text)

                    if check_density < density_threshold:
                        cluster_end = j - 1
                        break

                # 🆕 计算聚集区占章节的比例
                chapter_length = end_idx - start_idx
                cluster_length = cluster_end - cluster_start
                cluster_ratio = cluster_length / chapter_length if chapter_length > 0 else 0

                # 🆕 占比过高（>80%）：可能整章都是合同，不拆分
                if cluster_ratio > 0.8:
                    self.logger.info(
                        f"  ⚠️  合同聚集区占比过高({cluster_ratio:.1%})，不拆分章节 "
                        f"(段落{cluster_start}-{cluster_end}, 可能整章都是合同或误判)"
                    )
                    return None

                # 🆕 占比过低（<20%）：可能是误判（只是引用了部分合同内容）
                if cluster_ratio < 0.2:
                    self.logger.info(
                        f"  ⚠️  合同聚集区占比过低({cluster_ratio:.1%})，可能是误判 "
                        f"(段落{cluster_start}-{cluster_end}, 只是引用了部分合同内容)"
                    )
                    return None

                # 占比适中（20%-80%），执行拆分
                self.logger.info(
                    f"检测到合同聚集区: 段落{cluster_start}-{cluster_end} "
                    f"(章节范围:{start_idx}-{end_idx}, 合同密度:{density:.1%}, 占比:{cluster_ratio:.1%})"
                )

                return {
                    'start': cluster_start,
                    'end': cluster_end,
                    'density': density,
                    'ratio': cluster_ratio
                }

        return None

    def _calculate_dynamic_threshold(self, toc_items_count: int, doc_paragraph_count: int) -> float:
        """
        根据文档特征动态计算相似度阈值

        Args:
            toc_items_count: 目录项数量
            doc_paragraph_count: 文档总段落数

        Returns:
            相似度阈值 (0.60-0.80)
        """
        # 基础阈值根据目录项数量决定（降低5%以提高容错率）
        if toc_items_count < 10:
            base_threshold = 0.70  # 少量章节，降低阈值从0.75到0.70
        elif toc_items_count < 20:
            base_threshold = 0.65  # 中等章节数，降低阈值从0.70到0.65
        else:
            base_threshold = 0.60  # 大量章节，降低阈值从0.65到0.60

        # 根据文档复杂度微调 (段落数越多，文档越复杂，可适当放宽)
        doc_complexity = min(1.0, doc_paragraph_count / 1000)  # 标准化到0-1
        adjusted_threshold = base_threshold + (doc_complexity * 0.05)

        # 限制在合理范围内（上限从0.80降低到0.75）
        final_threshold = min(0.75, max(0.55, adjusted_threshold))

        self.logger.info(f"动态阈值计算: 目录项={toc_items_count}, 段落数={doc_paragraph_count}, "
                        f"基础阈值={base_threshold}, 调整后={final_threshold:.2f}")

        return final_threshold

    def _find_toc_section(self, doc: Document) -> Optional[int]:
        """
        查找文档中的目录部分 (优化版: 扩展关键词 + SDT支持)

        Args:
            doc: Word文档对象

        Returns:
            目录起始段落索引，如果未找到则返回None
        """
        # 优化2: 扩展目录关键词列表
        TOC_KEYWORDS = [
            # 中文
            "目录", "目  录", "索引", "章节目录", "内容目录",
            # 英文
            "contents", "table of contents", "catalogue", "index"
        ]

        # 第零轮: 检测SDT容器中的TOC域（Word自动目录）
        try:
            body = doc.element.body
            ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

            # 查找所有SDT元素
            sdt_elements = body.findall('.//w:sdt', namespaces=ns)

            for sdt in sdt_elements:
                # 检查是否是TOC类型的SDT
                docpart = sdt.find('.//w:docPartObj/w:docPartGallery', namespaces=ns)
                if docpart is not None:
                    gallery_val = docpart.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val')
                    if gallery_val == 'Table of Contents':
                        # 找到TOC SDT,获取其中第一个段落的索引
                        sdt_paras = sdt.findall('.//w:p', namespaces=ns)
                        if sdt_paras:
                            # 找到SDT中第一个段落在doc.paragraphs中的索引
                            first_sdt_para = sdt_paras[0]
                            for idx, para in enumerate(doc.paragraphs[:100]):
                                if para._element == first_sdt_para:
                                    self.logger.info(f"检测到Word TOC域（SDT容器），目录起始于段落 {idx}")
                                    return idx
        except Exception as e:
            self.logger.debug(f"SDT检测失败（正常情况）: {e}")
            pass

        # 第一轮: 检测显式目录标题
        for i, para in enumerate(doc.paragraphs[:50]):  # 只检查前50段
            text = para.text.strip()

            # 跳过空段落
            if not text:
                continue

            # 检测目录标题 (使用扩展关键词列表)
            text_lower = text.lower()
            for keyword in TOC_KEYWORDS:
                if text_lower == keyword.lower() or text.replace(" ", "") == keyword.replace(" ", ""):
                    self.logger.info(f"检测到目录标题 (关键词: '{keyword}')，位于段落 {i}: {text}")
                    return i

            # 检测TOC域（Word自动生成的目录）
            # 通过检查段落的XML来识别
            try:
                xml_str = para._element.xml.decode() if isinstance(para._element.xml, bytes) else str(para._element.xml)
                if 'TOC' in xml_str and 'fldChar' in xml_str:
                    self.logger.info(f"检测到Word TOC域，位于段落 {i}")
                    return i
            except (AttributeError, UnicodeDecodeError, TypeError):
                pass  # 无法获取XML或解析失败时跳过该段落

        self.logger.info("未检测到目录，将使用标题样式识别方案")
        return None

    def _detect_toc_level(self, para, title: str) -> int:
        """
        检测目录项的层级

        Args:
            para: python-docx Paragraph 对象
            title: 标题文本

        Returns:
            1-3: 标题层级
        """
        # 方法1：通过段落缩进判断
        try:
            if para.paragraph_format.left_indent:
                indent_pt = para.paragraph_format.left_indent.pt
                if indent_pt > 40:
                    return 3
                elif indent_pt > 20:
                    return 2
        except (AttributeError, TypeError):
            pass  # 无法获取缩进信息时使用其他方法

        # 方法2：通过标题编号格式判断
        # 三级：1.1.1, 1.1.1.1 等
        if re.match(r'^\d+\.\d+\.\d+', title):
            return 3
        # 二级：1.1, 1.2 等
        elif re.match(r'^\d+\.\d+[^\d]', title):
            return 2
        # 一级：第X部分、1.、2.、一、二、等
        elif re.match(r'^(第[一二三四五六七八九十\d]+部分|第[一二三四五六七八九十\d]+章|\d+\.|[一二三四五六七八九十]+、)', title):
            return 1

        # 默认1级
        return 1

    def _parse_toc_items(self, doc: Document, toc_start_idx: int) -> Tuple[List[Dict], int]:
        """
        解析目录项（改进3：确保 toc_end_idx > toc_start_idx）

        Args:
            doc: Word文档对象
            toc_start_idx: 目录起始段落索引

        Returns:
            (目录项列表, 目录结束索引)
            目录项列表格式：[{'title': '...', 'page_num': 1, 'level': 1}, ...]
        """
        toc_items = []
        consecutive_non_toc = 0  # 连续非目录项计数
        toc_end_idx = toc_start_idx  # 目录结束位置

        # ⭐️ 目录项数量限制（避免扫描过远）
        MAX_TOC_ITEMS = 100

        for i in range(toc_start_idx + 1, min(toc_start_idx + 100, len(doc.paragraphs))):
            para = doc.paragraphs[i]
            text = para.text.strip()

            # 跳过空行
            if not text:
                continue

            # 尝试匹配目录项格式
            # 格式1: "标题文本    页码" (多个空格)
            match = re.match(r'^(.+?)\s{2,}(\d+)$', text)
            if not match:
                # 格式2: "标题文本....页码" (点号填充)
                match = re.match(r'^(.+?)\.{2,}(\d+)$', text)
            if not match:
                # 格式3: "标题文本\t页码" (制表符)
                match = re.match(r'^(.+?)\t+(\d+)$', text)

            if match:
                title = match.group(1).strip()
                page_num = int(match.group(2))

                # ⭐️ 重复检测：如果与第一项重复，说明扫描到正文了
                # 使用模糊匹配代替严格相等，以应对文本略有差异的情况
                if toc_items:
                    first_title = toc_items[0]['title']
                    similarity = self.fuzzy_match_title_v2(title, first_title)
                    if similarity >= 0.70:  # 70%以上相似度认为是重复
                        self.logger.info(f"检测到重复目录项（与第1项相似度{similarity:.0%}），目录解析结束")
                        self.logger.debug(f"  第1项: '{first_title}' vs 当前: '{title}'")
                        break

                # ⭐️ 数量限制检查
                if len(toc_items) >= MAX_TOC_ITEMS:
                    self.logger.info(f"目录项已达上限({MAX_TOC_ITEMS})，停止解析")
                    break

                # 检测层级
                level = self._detect_toc_level(para, title)

                toc_items.append({
                    'title': title,
                    'page_num': page_num,
                    'level': level
                })

                self.logger.debug(f"目录项 [{level}级]: {title} -> 第{page_num}页")

                # 更新目录结束位置
                toc_end_idx = i
                # 重置计数
                consecutive_non_toc = 0
            else:
                # 新增：尝试识别无页码的简单目录项
                # 特征1：有统一缩进（目录项通常缩进对齐）
                has_indent = (para.paragraph_format.left_indent and
                              para.paragraph_format.left_indent > 200000)

                # 特征2：匹配章节模式
                is_chapter_pattern = (
                    re.match(r'^第[一二三四五六七八九十\d]+章', text) or
                    re.match(r'^第[一二三四五六七八九十\d]+部分', text) or
                    text in ['竞争性磋商公告', '招标公告', '采购公告', '谈判公告', '询价公告']
                )

                # 如果满足条件，作为无页码目录项
                if (has_indent or is_chapter_pattern) and len(text) < 50 and not text.startswith('项目'):
                    title = text.strip()

                    # ⭐️ 重复检测：如果与第一项重复，说明扫描到正文了
                    # 使用模糊匹配代替严格相等，以应对文本略有差异的情况
                    if toc_items:
                        first_title = toc_items[0]['title']
                        similarity = self.fuzzy_match_title_v2(title, first_title)
                        if similarity >= 0.70:  # 70%以上相似度认为是重复
                            self.logger.info(f"检测到重复目录项（与第1项相似度{similarity:.0%}），目录解析结束")
                            self.logger.debug(f"  第1项: '{first_title}' vs 当前: '{title}'")
                            break

                    # ⭐️ 数量限制检查
                    if len(toc_items) >= MAX_TOC_ITEMS:
                        self.logger.info(f"目录项已达上限({MAX_TOC_ITEMS})，停止解析")
                        break

                    page_num = -1  # 标记为无页码
                    level = self._detect_toc_level(para, title)

                    toc_items.append({
                        'title': title,
                        'page_num': page_num,
                        'level': level
                    })

                    self.logger.debug(f"目录项(无页码) [{level}级]: {title}")
                    toc_end_idx = i
                    consecutive_non_toc = 0
                    continue  # 成功识别，继续下一个

                # 非目录项
                consecutive_non_toc += 1
                # 连续5行不匹配，认为目录结束
                if consecutive_non_toc >= 5 and len(toc_items) > 0:
                    self.logger.info(f"目录解析完成，共 {len(toc_items)} 项，结束于段落 {toc_end_idx}")
                    break
                # 新增：如果找到了目录项但遇到空行后的Heading样式，认为目录结束
                if (len(toc_items) > 0 and consecutive_non_toc >= 2 and
                    para.style and para.style.name.startswith('Heading')):
                    self.logger.info(f"检测到Heading样式，目录结束于段落 {toc_end_idx}")
                    break

        # 改进3：确保 toc_end_idx 严格大于 toc_start_idx
        if toc_end_idx == toc_start_idx:
            # 如果没有找到任何目录项，至少向后移动1个段落
            toc_end_idx = toc_start_idx + 1
            self.logger.warning(f"未解析到目录项，将目录结束位置设为 {toc_end_idx}（避免逻辑错误）")

        # 使用层级分析器修正层级（基于统计频率的上下文分析）
        if toc_items:
            self.logger.info(f"⚡️ 开始使用contextual方法分析 {len(toc_items)} 个TOC项的层级")
            analyzer = LevelAnalyzer()
            corrected_levels = analyzer.analyze_toc_hierarchy_contextual(toc_items)
            for i, level in enumerate(corrected_levels):
                toc_items[i]['level'] = level

            from collections import Counter
            level_dist = Counter(corrected_levels)
            self.logger.info(f"使用contextual方法修正层级，分布: {dict(level_dist)}")

        # 🆕 轻量级合同潜在标记（基于标题关键词）
        if toc_items:
            # 排除规则：这些章节不应被标记为合同
            exclude_keywords = [
                "投标人须知", "供应商须知", "投标邀请", "投标须知", "招标须知",
                "附件", "投标文件格式", "响应文件格式", "投标文件组成", "谈判响应文件格式",
                "用户需求", "需求书", "技术要求", "技术规格", "技术需求书", "技术需求",
                "评分", "评审", "评标", "开标", "报价", "投标报价",
                "投标邀请函", "采购邀请", "谈判邀请"
            ]

            # 合同关键词：只有包含这些关键词才标记为潜在合同
            contract_keywords = [
                "合同条款", "合同文本", "合同范本", "合同协议", "合同格式",
                "通用条款", "专用条款", "拟签合同", "合同草稿", "合同主要条款"
            ]

            contract_potential_count = 0
            for item in toc_items:
                title = item['title']

                # 排除规则优先
                is_excluded = any(kw in title for kw in exclude_keywords)
                is_contract_potential = any(kw in title for kw in contract_keywords)

                # 只有在不被排除且包含合同关键词时才标记
                item['is_contract_potential'] = is_contract_potential and not is_excluded

                if item['is_contract_potential']:
                    contract_potential_count += 1
                    self.logger.debug(f"  🏷️  潜在合同章节: '{title}'")
                elif is_excluded:
                    self.logger.debug(f"  ⛔ 排除章节: '{title}' (匹配排除规则)")

            if contract_potential_count > 0:
                self.logger.info(f"🏷️  标记了 {contract_potential_count} 个潜在合同章节")

        return toc_items, toc_end_idx

    def _find_paragraph_by_title(self, doc: Document, title: str, start_idx: int = 0) -> Optional[int]:
        """
        在文档中搜索与标题匹配的段落

        Args:
            doc: Word文档对象
            title: 要搜索的标题文本
            start_idx: 开始搜索的段落索引

        Returns:
            段落索引，如果未找到则返回None
        """
        def aggressive_normalize(text: str) -> str:
            """激进文本规范化：移除所有分隔符、前缀、空格"""
            # 移除"附件-"、"附件:"等前缀
            text = re.sub(r'^附件[-:：]?', '', text)
            # 移除连字符、下划线、制表符
            text = re.sub(r'[-_\t]+', '', text)
            # 移除所有空格
            text = re.sub(r'\s+', '', text)
            return text

        def extract_core_keywords(text: str) -> str:
            """提取核心关键词：去除编号和常见前缀"""
            # 移除编号
            text = re.sub(r'^(第[一二三四五六七八九十\d]+部分|第[一二三四五六七八九十\d]+章|\d+\.|\d+\.\d+|[一二三四五六七八九十]+、)\s*', '', text)
            # 移除"附件"前缀
            text = re.sub(r'^附件[-:：]?', '', text)
            # 移除分隔符
            text = re.sub(r'[-_\t]+', '', text)
            # 移除空格
            text = re.sub(r'\s+', '', text)
            return text

        def calculate_similarity(str1: str, str2: str) -> float:
            """计算两个字符串的相似度（基于包含关系）"""
            if not str1 or not str2:
                return 0.0

            shorter = str1 if len(str1) <= len(str2) else str2
            longer = str2 if len(str1) <= len(str2) else str1

            # 检查shorter是否被longer包含
            if shorter in longer:
                return len(shorter) / len(longer)

            # 检查部分重叠
            max_overlap = 0
            for i in range(len(shorter)):
                for j in range(i + 1, len(shorter) + 1):
                    substr = shorter[i:j]
                    if substr in longer and len(substr) > max_overlap:
                        max_overlap = len(substr)

            return max_overlap / max(len(str1), len(str2))

        # 清理标题（移除多余空格）
        clean_title = re.sub(r'\s+', '', title)

        # 激进规范化的标题
        aggressive_title = aggressive_normalize(title)

        # 提取核心关键词
        core_keywords = extract_core_keywords(aggressive_title)

        self.logger.info(f"搜索标题: '{title}' (清理后: '{clean_title}', 核心: '{core_keywords}'), 从段落 {start_idx} 开始")

        # 候选匹配列表（用于诊断）
        candidates = []

        for i in range(start_idx, len(doc.paragraphs)):
            para = doc.paragraphs[i]
            para_text = para.text.strip()

            if not para_text:
                continue

            # 清理段落文本
            clean_para = re.sub(r'\s+', '', para_text)

            # 激进规范化的段落
            aggressive_para = aggressive_normalize(para_text)

            # 段落核心关键词
            para_keywords = extract_core_keywords(aggressive_para)

            # Level 1: 完全匹配或包含匹配
            if clean_title == clean_para or clean_title in clean_para:
                self.logger.info(f"  ✓ 找到匹配 (Level 1-完全): 段落 {i}: '{para_text}'")
                return i

            # Level 2: 激进规范化后的完全匹配
            if aggressive_title == aggressive_para or aggressive_title in aggressive_para:
                self.logger.info(f"  ✓ 找到匹配 (Level 2-规范化): 段落 {i}: '{para_text}'")
                return i

            # 检查标题和段落是否包含"第X部分"（用于Level 3和Level 4约束）
            title_has_part_number = bool(re.search(r'第[一二三四五六七八九十\d]+部分', title))
            para_has_part_number = bool(re.search(r'第[一二三四五六七八九十\d]+部分', para_text))

            # Level 3: 去除编号后的匹配
            # 支持多种编号格式：第X部分、第X章、1.、1.1、一、等
            title_without_number = re.sub(r'^(第[一二三四五六七八九十\d]+部分|第[一二三四五六七八九十\d]+章|\d+\.|\d+\.\d+|[一二三四五六七八九十]+、)\s*', '', clean_title)
            para_without_number = re.sub(r'^(第[一二三四五六七八九十\d]+部分|第[一二三四五六七八九十\d]+章|\d+\.|\d+\.\d+|[一二三四五六七八九十]+、)\s*', '', clean_para)

            if title_without_number and para_without_number and title_without_number == para_without_number:
                # 如果TOC标题有"第X部分"，则段落也必须有"第X部分"（避免匹配到TOC内的编号内容）
                if title_has_part_number and not para_has_part_number:
                    pass  # 跳过，不匹配
                else:
                    self.logger.info(f"  ✓ 找到匹配 (Level 3-去编号): 段落 {i}: '{para_text}'")
                    return i

            # Level 4: 核心关键词匹配（长度≥4字）
            # 特别检查：如果原标题包含"第X部分",则段落也必须包含"第X部分"

            if len(core_keywords) >= 4 and len(para_keywords) >= 4:
                # 双向包含检查
                if core_keywords in para_keywords or para_keywords in core_keywords:
                    # 如果标题有"第X部分",则段落也必须有,且段落应该是短标题(≤50字)
                    if title_has_part_number:
                        if para_has_part_number and len(para_text) <= 50:
                            self.logger.info(f"  ✓ 找到匹配 (Level 4-关键词+部分编号): 段落 {i}: '{para_text}' (核心词: '{para_keywords}')")
                            return i
                    else:
                        # 标题没有"第X部分",普通关键词匹配
                        self.logger.info(f"  ✓ 找到匹配 (Level 4-关键词): 段落 {i}: '{para_text}' (核心词: '{para_keywords}')")
                        return i

            # Level 4.5: 部分子串匹配（解决TOC与实际文本部分差异问题）
            # 例如：TOC="单一来源采购谈判邀请" vs 实际="单一来源采购邀请" (少"谈判")
            if len(core_keywords) >= 6 and title_has_part_number:
                # 从长到短尝试提取子串
                for substr_len in range(len(core_keywords), 5, -1):
                    substr = core_keywords[:substr_len]
                    if substr in para_keywords and len(substr) >= 6:
                        # 找到大部分匹配，验证段落格式
                        if para_has_part_number and len(para_text) <= 50:
                            match_ratio = len(substr) / len(core_keywords)
                            self.logger.info(f"  ✓ 找到匹配 (Level 4.5-部分子串{match_ratio:.0%}): 段落 {i}: '{para_text}' (匹配: '{substr}')")
                            return i
                        break  # 找到但格式不对，不继续尝试更短的

            # Level 5: 相似度匹配（相似度≥80%，更严格）
            if len(core_keywords) >= 4:
                similarity = calculate_similarity(core_keywords, para_keywords)
                if similarity >= 0.8:  # 提高阈值从70%到80%
                    self.logger.info(f"  ✓ 找到匹配 (Level 5-相似度{similarity:.0%}): 段落 {i}: '{para_text}'")
                    return i

                # 记录高相似度候选
                if similarity >= 0.6:  # 候选阈值也相应提高
                    candidates.append((i, para_text, similarity, core_keywords, para_keywords))

            # Level 6: 宽松关键词匹配（至少6字标题）
            if len(title_without_number) >= 6:
                # 检查段落是否包含标题去除编号后的大部分内容
                if title_without_number in clean_para:
                    self.logger.info(f"  ✓ 找到匹配 (Level 6-宽松): 段落 {i}: '{para_text}'")
                    return i

            # 额外尝试：将"第X部分"转换为"X."进行匹配
            # 例如："第一部分 单一来源采购谈判邀请" 也可以匹配 "1.单一来源采购谈判邀请"
            def convert_chinese_to_number(text):
                """将第一/第二/第三等转换为1/2/3"""
                mapping = {'一': '1', '二': '2', '三': '3', '四': '4', '五': '5',
                          '六': '6', '七': '7', '八': '8', '九': '9', '十': '10'}
                # 匹配"第X部分"格式
                match = re.match(r'^第([一二三四五六七八九十]+)部分(.*)$', text)
                if match:
                    num = mapping.get(match.group(1), match.group(1))
                    return f"{num}.{match.group(2)}"
                return text

            # Level 7: 转换编号后匹配
            converted_title = convert_chinese_to_number(clean_title)
            if converted_title != clean_title and clean_para.startswith(converted_title[:3]):
                # 转换后的标题开头与段落匹配
                converted_para_without_num = re.sub(r'^\d+\.', '', clean_para)
                converted_title_without_num = re.sub(r'^\d+\.', '', converted_title)
                if converted_title_without_num == converted_para_without_num:
                    self.logger.info(f"  ✓ 找到匹配 (Level 7-转换编号): 段落 {i}: '{para_text}'")
                    return i

            # 收集低相似度候选（用于诊断）
            if i < start_idx + 100 and len(para_text) > 5 and len(para_text) < 100:
                # 检查是否部分匹配
                if title_without_number and para_without_number:
                    # 如果标题去编号后的内容部分出现在段落中
                    if len(title_without_number) >= 3:
                        if title_without_number[:4] in para_without_number or para_without_number[:4] in title_without_number:
                            if not any(c[0] == i for c in candidates):  # 避免重复
                                candidates.append((i, para_text, 0.4, title_without_number, para_without_number))

        # 未找到，输出诊断信息
        self.logger.warning(f"未找到标题匹配: '{title}'")
        if candidates:
            # 按相似度排序
            candidates.sort(key=lambda x: x[2] if isinstance(x[2], float) else 0.3, reverse=True)
            self.logger.info(f"  可能的候选段落 (前{min(5, len(candidates))}个，按相似度排序):")
            for idx, text, sim, title_key, para_key in candidates[:5]:
                sim_str = f"{sim:.0%}" if isinstance(sim, float) else "低"
                self.logger.info(f"    段落 {idx} (相似度{sim_str}): '{text[:50]}...' ")
                self.logger.info(f"      标题核心: '{title_key}' vs 段落核心: '{para_key}'")

        return None

    def _detect_numbering_pattern(self, text: str) -> Optional[Tuple[str, int]]:
        """
        检测段落的编号模式

        Args:
            text: 段落文本

        Returns:
            (编号前缀, 层级) 或 None
            例如: ("2.1.", 2), ("2.1.1.", 3), ("一、", 1)
        """
        patterns = [
            (r'^(\d+\.\d+\.\d+\.)\s*', 3),  # 2.1.1.
            (r'^(\d+\.\d+\.)\s*', 2),       # 2.1.
            (r'^(\d+\.)\s*', 1),            # 2.
            (r'^([一二三四五六七八九十]+、)\s*', 1),  # 一、
            (r'^(\([一二三四五六七八九十]+\))\s*', 2),  # (一)
        ]

        for pattern, level in patterns:
            match = re.match(pattern, text)
            if match:
                return (match.group(1), level)
        return None

    def _is_bold_subtitle(self, paragraph) -> bool:
        """
        判断段落是否为加粗的子标题

        Args:
            paragraph: Word段落对象

        Returns:
            是否为加粗子标题
        """
        text = paragraph.text.strip()

        # 排除空段落
        if not text:
            return False

        # 排除过长的段落(子标题通常较短)
        if len(text) > 50:
            return False

        # 排除编号开头的段落(已通过编号模式识别)
        if re.match(r'^\d+\.', text):
            return False

        # 检查是否有加粗的run
        has_bold = False
        if paragraph.runs:
            # 至少有一个run是加粗的,且加粗内容占比较大
            bold_chars = sum(len(r.text) for r in paragraph.runs if r.bold)
            total_chars = len(text)
            has_bold = bold_chars > total_chars * 0.5  # 加粗内容超过50%

        return has_bold

    def _parse_subsections_in_range(self, doc: Document, start_idx: int, end_idx: int,
                                     parent_level: int, parent_id: str) -> List[ChapterNode]:
        """
        在指定段落范围内识别子章节 (增强版)

        识别策略:
        1. 样式标题: Heading 1/2/3等样式
        2. 编号模式: 2.1., 2.1.1., 一、等
        3. 加粗子标题: 加粗且较短的段落

        Args:
            doc: Word文档对象
            start_idx: 起始段落索引
            end_idx: 结束段落索引
            parent_level: 父章节层级
            parent_id: 父章节ID

        Returns:
            子章节列表
        """
        subsections = []
        counter = 0

        # 记录上一个编号,用于检测编号重置
        last_numbering = None

        for para_idx in range(start_idx + 1, end_idx + 1):
            if para_idx >= len(doc.paragraphs):
                break

            paragraph = doc.paragraphs[para_idx]
            text = paragraph.text.strip()

            if not text:
                continue

            level = self._get_heading_level(paragraph)
            is_subsection = False
            recognition_type = ""

            # 策略1: 样式标题 (原有逻辑)
            if level > 0 and level > parent_level:
                is_subsection = True
                recognition_type = f"样式{level}级"

            # 策略2: 编号模式识别
            elif not is_subsection:
                numbering_result = self._detect_numbering_pattern(text)
                if numbering_result:
                    numbering_prefix, numbering_level = numbering_result

                    # 检测编号重置(例如 2.1.6 -> 2.1.1 表示新的子章节组)
                    if last_numbering and numbering_prefix < last_numbering:
                        self.logger.debug(f"  ⚠️  检测到编号重置: {last_numbering} -> {numbering_prefix}")

                    last_numbering = numbering_prefix

                    # 编号层级应该比父层级深
                    if numbering_level > parent_level:
                        is_subsection = True
                        recognition_type = f"编号{numbering_prefix}"

            # 策略3: 加粗子标题识别
            elif not is_subsection and self._is_bold_subtitle(paragraph):
                is_subsection = True
                recognition_type = "加粗子标题"
                # 加粗子标题视为比父层级深1级
                level = parent_level + 1

            # 如果识别为子章节,创建节点
            if is_subsection:
                title = text

                # 判断是否匹配白/黑名单
                auto_selected = self._matches_whitelist(title)
                skip_recommended = self._matches_blacklist(title)

                if skip_recommended:
                    auto_selected = False

                subsection = ChapterNode(
                    id=f"{parent_id}_{counter}",
                    level=level if level > 0 else parent_level + 1,
                    title=title,
                    para_start_idx=para_idx,
                    para_end_idx=None,  # 稍后计算
                    word_count=0,       # 稍后计算
                    preview_text="",    # 稍后提取
                    auto_selected=auto_selected,
                    skip_recommended=skip_recommended
                )

                subsections.append(subsection)
                counter += 1

                self.logger.debug(
                    f"  └─ 找到子章节 [{recognition_type}]: {title} "
                    f"{'✅自动选中' if auto_selected else '❌跳过' if skip_recommended else '⚪默认'}"
                )

        # 计算每个子章节的范围
        for i, subsection in enumerate(subsections):
            # 确定子章节结束位置
            if i + 1 < len(subsections):
                subsection.para_end_idx = subsections[i + 1].para_start_idx - 1
            else:
                subsection.para_end_idx = end_idx

            # 提取子章节内容
            content_paras = doc.paragraphs[subsection.para_start_idx + 1 : subsection.para_end_idx + 1]
            content_text = '\n'.join(p.text for p in content_paras)
            subsection.word_count = len(content_text.replace(' ', '').replace('\n', ''))

            # 提取预览文本
            preview_lines = []
            for p in content_paras[:5]:
                text = p.text.strip()
                if text:
                    preview_lines.append(text[:100] + ('...' if len(text) > 100 else ''))
                if len(preview_lines) >= 5:
                    break

            subsection.preview_text = '\n'.join(preview_lines) if preview_lines else "(无内容)"

        return subsections

    def _locate_chapters_by_toc(self, doc: Document, toc_items: List[Dict], toc_end_idx: int) -> List[ChapterNode]:
        """
        根据目录项定位章节在文档中的位置，并构建树形结构

        核心改进: 完全使用TOC中已识别的层级信息，不再重新检测子章节
        这样可以保留 analyze_toc_hierarchy_contextual() 的精确分析结果

        Args:
            doc: Word文档对象
            toc_items: 目录项列表（已包含精确的层级信息）
            toc_end_idx: 目录结束的段落索引

        Returns:
            章节树（只包含根节点，子节点在children属性中）
        """
        # 步骤1: 定位所有TOC项在文档中的位置
        all_chapters = []
        last_found_idx = toc_end_idx + 1
        self.logger.info(f"⭐ 开始定位 {len(toc_items)} 个TOC项的位置（目录结束于段落 {toc_end_idx}）")

        for i, item in enumerate(toc_items):
            title = item['title']
            level = item['level']

            # 在文档中查找标题位置
            para_idx = self._find_paragraph_by_title(doc, title, last_found_idx)

            if para_idx is None:
                self.logger.warning(f"⚠️  未找到目录项: [{level}级] {title}")
                continue

            # 记录找到的章节（暂不确定结束位置）
            all_chapters.append({
                'toc_index': i,
                'title': title,
                'level': level,
                'para_idx': para_idx,
                'para_end_idx': None  # 稍后计算
            })

            last_found_idx = para_idx + 1
            self.logger.debug(f"  ✓ 找到 [{level}级] {title} (段落 {para_idx})")

        # 步骤2: 计算每个章节的结束位置
        for i, chapter_info in enumerate(all_chapters):
            # 结束位置 = 下一个章节的起始位置 - 1
            if i + 1 < len(all_chapters):
                chapter_info['para_end_idx'] = all_chapters[i + 1]['para_idx'] - 1
            else:
                chapter_info['para_end_idx'] = len(doc.paragraphs) - 1

        # 🆕 步骤2.5: 重型合同检测（仅处理标记为潜在合同的章节）
        contract_chapters_to_insert = []  # 存储需要插入的合同章节
        contract_check_count = 0
        contract_confirmed_count = 0

        for i, chapter_info in enumerate(all_chapters):
            toc_item = toc_items[chapter_info['toc_index']]

            # 🎯 只对标记为潜在合同的章节执行重型检测
            if toc_item.get('is_contract_potential', False):
                contract_check_count += 1
                self.logger.info(f"  🔍 对潜在合同章节执行重型检测: '{chapter_info['title']}'")

                para_idx = chapter_info['para_idx']
                para_end_idx = chapter_info['para_end_idx']

                # 重型作业1: 提取完整内容样本（2000字）
                content_sample = self._extract_content_sample(
                    doc, para_idx, para_end_idx, sample_size=2000
                )

                # 重型作业2: 计算精确的合同密度
                is_contract, density, reason = self._is_contract_chapter(
                    chapter_info['title'],
                    content_sample
                )

                if is_contract:
                    contract_confirmed_count += 1
                    chapter_info['is_contract_confirmed'] = True
                    chapter_info['skip_recommended'] = True
                    self.logger.info(f"  ✓ 合同章节确认: '{chapter_info['title']}' - {reason}")

                    # 重型作业3: 检测合同聚集区（用于章节拆分）
                    contract_cluster = self._detect_contract_cluster_in_chapter(
                        doc, para_idx, para_end_idx
                    )

                    if contract_cluster:
                        # 占比已在检测方法中限制（20%-80%），这里直接处理
                        cluster_start = contract_cluster['start']
                        cluster_end = contract_cluster['end']
                        cluster_ratio = contract_cluster['ratio']

                        # 检查是否满足拆分条件
                        min_content_length = 1000
                        min_paragraph_gap = 5

                        if cluster_start > para_idx + min_paragraph_gap:
                            # 计算前半部分字数
                            front_content = "\n".join(
                                doc.paragraphs[j].text.strip()
                                for j in range(para_idx + 1, cluster_start)
                                if j < len(doc.paragraphs)
                            )
                            front_word_count = len(front_content.replace(' ', '').replace('\n', ''))

                            if front_word_count >= min_content_length:
                                self.logger.warning(
                                    f"✂️  准备拆分章节: '{chapter_info['title']}' "
                                    f"→ 正常部分({para_idx}-{cluster_start-1}, {front_word_count}字) "
                                    f"+ 合同部分({cluster_start}-{para_end_idx}, 占比{cluster_ratio:.1%})"
                                )

                                # 截断原章节（只保留合同之前的部分）
                                chapter_info['para_end_idx'] = cluster_start - 1

                                # 创建合同章节（记录待插入）
                                contract_chapter = {
                                    'toc_index': chapter_info['toc_index'] + 0.5,  # 标记为插入的章节
                                    'title': '[检测到的合同条款-需人工确认]',
                                    'level': chapter_info['level'],  # 与原章节同级
                                    'para_idx': cluster_start,
                                    'para_end_idx': para_end_idx,
                                    'is_contract_confirmed': True,
                                    'skip_recommended': True
                                }

                                # 记录待插入位置（插入到原章节后面）
                                contract_chapters_to_insert.append((i + 1, contract_chapter))
                            else:
                                self.logger.info(
                                    f"  ⏭️  跳过拆分: '{chapter_info['title']}' - "
                                    f"前半部分内容不足({front_word_count}字 < {min_content_length}字)"
                                )
                        else:
                            self.logger.info(
                                f"  ⏭️  跳过拆分: '{chapter_info['title']}' - "
                                f"合同聚集区起点太靠前(段落{cluster_start})"
                            )
                else:
                    self.logger.info(f"  ✗ 非合同章节: '{chapter_info['title']}' - {reason}")
            else:
                # 非潜在合同章节，跳过重型检测
                self.logger.debug(f"  ⏭️  跳过重型检测: '{chapter_info['title']}'")

        # 插入拆分出的合同章节（倒序插入，避免索引偏移）
        for insert_pos, contract_chapter in reversed(contract_chapters_to_insert):
            all_chapters.insert(insert_pos, contract_chapter)
            self.logger.info(
                f"  ➕ 插入合同章节: '{contract_chapter['title']}' "
                f"(段落{contract_chapter['para_idx']}-{contract_chapter['para_end_idx']})"
            )

        if contract_check_count > 0:
            self.logger.info(
                f"🔍 重型检测完成: 检测了 {contract_check_count} 个潜在章节，确认 {contract_confirmed_count} 个合同章节，"
                f"拆分出 {len(contract_chapters_to_insert)} 个合同章节"
            )

        # 步骤3: 创建所有ChapterNode对象
        chapter_nodes = []
        for chapter_info in all_chapters:
            para_idx = chapter_info['para_idx']
            para_end_idx = chapter_info['para_end_idx']

            # 提取章节内容
            content_paras = doc.paragraphs[para_idx + 1 : para_end_idx + 1]
            content_text = '\n'.join(p.text for p in content_paras)
            word_count = len(content_text.replace(' ', '').replace('\n', ''))

            # 提取预览文本
            preview_lines = []
            for p in content_paras[:5]:
                text = p.text.strip()
                if text:
                    preview_lines.append(text[:100] + ('...' if len(text) > 100 else ''))
                if len(preview_lines) >= 5:
                    break
            preview_text = '\n'.join(preview_lines) if preview_lines else "(无内容)"

            # 判断是否匹配白/黑名单
            auto_selected = self._matches_whitelist(chapter_info['title'])
            skip_recommended = self._matches_blacklist(chapter_info['title'])

            # 🆕 使用合同检测结果（优先级高于黑名单）
            if chapter_info.get('skip_recommended'):
                skip_recommended = True
            if skip_recommended:
                auto_selected = False

            node = ChapterNode(
                id=f"ch_{chapter_info['toc_index']}",
                level=chapter_info['level'],  # ⭐ 使用TOC中的层级，不重新检测
                title=chapter_info['title'],
                para_start_idx=para_idx,
                para_end_idx=para_end_idx,
                word_count=word_count,
                preview_text=preview_text,
                auto_selected=auto_selected,
                skip_recommended=skip_recommended
            )

            chapter_nodes.append(node)

        # 步骤4: 构建树形结构（基于level属性）
        root_chapters = self._build_chapter_tree(chapter_nodes)

        self.logger.info(f"✅ 成功构建章节树: {len(root_chapters)} 个根章节")
        return root_chapters

    def _build_chapter_tree(self, chapters: List[ChapterNode]) -> List[ChapterNode]:
        """
        根据章节的level属性构建树形结构

        Args:
            chapters: 扁平的章节列表（按文档顺序排列）

        Returns:
            根章节列表（子章节在children属性中）
        """
        if not chapters:
            return []

        root_chapters = []
        stack = []  # 用于追踪父节点的栈

        for chapter in chapters:
            # 弹出所有层级 >= 当前章节的节点（它们不是当前章节的祖先）
            while stack and stack[-1].level >= chapter.level:
                stack.pop()

            # 如果栈为空，说明是根节点
            if not stack:
                root_chapters.append(chapter)
            else:
                # 否则，当前章节是栈顶节点的子节点
                parent = stack[-1]
                if parent.children is None:
                    parent.children = []
                parent.children.append(chapter)

            # 将当前章节压入栈
            stack.append(chapter)

        # 统计树形结构
        def count_by_level(nodes, level_counts=None):
            if level_counts is None:
                level_counts = {}
            for node in nodes:
                level_counts[node.level] = level_counts.get(node.level, 0) + 1
                if node.children:
                    count_by_level(node.children, level_counts)
            return level_counts

        level_dist = count_by_level(root_chapters)
        self.logger.info(f"📊 章节层级分布: {dict(sorted(level_dist.items()))}")

        return root_chapters

    def _locate_chapter_content(self, doc: Document, chapters: List[ChapterNode]) -> List[ChapterNode]:
        """
        定位每个章节的内容范围

        Args:
            doc: Word 文档对象
            chapters: 章节列表

        Returns:
            更新后的章节列表（包含 para_end_idx、word_count、preview_text）
        """
        # ⭐️ 关键修复：按段落索引排序，确保章节顺序与文档物理顺序一致
        # 防止索引倒置问题（如 para_start_idx=542 > para_end_idx=62）
        chapters_sorted = sorted(chapters, key=lambda ch: ch.para_start_idx)
        self.logger.info(f"章节已按段落索引排序，共 {len(chapters_sorted)} 个章节")

        total_paras = len(doc.paragraphs)

        # 🆕 用于收集需要插入的合同章节
        contract_chapters_to_insert = []

        for i, chapter in enumerate(chapters_sorted):
            # 确定章节结束位置（下一个同级或更高级标题的前一个段落）
            next_start = total_paras  # 默认到文档末尾

            for j in range(i + 1, len(chapters_sorted)):
                if chapters_sorted[j].level <= chapter.level:
                    next_start = chapters_sorted[j].para_start_idx
                    break

            chapter.para_end_idx = next_start - 1

            # 提取章节内容（包括段落和表格）
            content_text, preview_text = self._extract_chapter_content_with_tables(
                doc, chapter.para_start_idx, chapter.para_end_idx
            )

            # 计算字数
            chapter.word_count = len(content_text.replace(' ', '').replace('\n', ''))
            chapter.preview_text = preview_text if preview_text else "(无内容)"

            # 【新增】对于level 1-2的章节，提取内容样本并进行合同识别
            if chapter.level <= 2:
                # 提取内容样本用于合同识别
                chapter.content_sample = self._extract_content_sample(
                    doc, chapter.para_start_idx, chapter.para_end_idx, sample_size=2000
                )

                # 基于内容进行合同识别
                is_contract, density, reason = self._is_contract_chapter(
                    chapter.title, chapter.content_sample
                )

                if is_contract:
                    # 更新skip_recommended标记
                    if not chapter.skip_recommended:  # 避免重复标记
                        chapter.skip_recommended = True
                        chapter.auto_selected = False
                        self.logger.info(
                            f"  ✓ 合同章节识别: '{chapter.title}' - {reason}"
                        )
                    else:
                        self.logger.debug(
                            f"  ✓ 合同章节已标记: '{chapter.title}' - {reason}"
                        )

            # 🆕 新增：检测章节内是否有合同聚集区（用于拆分章节）
            contract_cluster = self._detect_contract_cluster_in_chapter(
                doc, chapter.para_start_idx, chapter.para_end_idx
            )

            if contract_cluster:
                cluster_start = contract_cluster['start']
                cluster_end = contract_cluster['end']
                density = contract_cluster['density']

                # 确保聚集区起点在章节内且有足够的前置内容
                min_content_length = 1000  # 前半部分至少1000字

                if cluster_start > chapter.para_start_idx + 5:  # 至少跳过5个段落
                    # 计算前半部分的字数
                    front_content = "\n".join(
                        doc.paragraphs[j].text.strip()
                        for j in range(chapter.para_start_idx + 1, cluster_start)
                        if j < len(doc.paragraphs)
                    )
                    front_word_count = len(front_content.replace(' ', '').replace('\n', ''))

                    if front_word_count >= min_content_length:
                        self.logger.warning(
                            f"⚠️ 章节将被拆分: '{chapter.title}' "
                            f"→ 正常部分({chapter.para_start_idx}-{cluster_start-1}, {front_word_count}字) "
                            f"+ 合同部分({cluster_start}-{cluster_end}, 密度{density:.1%})"
                        )

                        # 截断当前章节（只保留合同之前的部分）
                        original_end = chapter.para_end_idx
                        chapter.para_end_idx = cluster_start - 1

                        # 重新计算缩短后的章节内容
                        content_text, preview_text = self._extract_chapter_content_with_tables(
                            doc, chapter.para_start_idx, chapter.para_end_idx
                        )
                        chapter.word_count = len(content_text.replace(' ', '').replace('\n', ''))
                        chapter.preview_text = preview_text

                        # 🆕 创建合同章节（标记为待插入）
                        contract_chapter = ChapterNode(
                            id=f"ch_{i}_contract",  # 临时ID，后续会重新分配
                            level=chapter.level,  # 与原章节同级
                            title="[检测到的合同条款-需人工确认]",
                            para_start_idx=cluster_start,
                            para_end_idx=original_end,
                            word_count=0,
                            preview_text="",
                            auto_selected=False,
                            skip_recommended=True  # 标记为推荐跳过
                        )

                        # 计算合同章节内容
                        contract_content, contract_preview = self._extract_chapter_content_with_tables(
                            doc, contract_chapter.para_start_idx, contract_chapter.para_end_idx
                        )
                        contract_chapter.word_count = len(contract_content.replace(' ', '').replace('\n', ''))
                        contract_chapter.preview_text = contract_preview

                        # 添加到待插入列表（记录插入位置）
                        contract_chapters_to_insert.append((i + 1, contract_chapter))

                        self.logger.info(
                            f"✂️ 章节拆分完成: "
                            f"正常部分({chapter.para_start_idx}-{chapter.para_end_idx}, {chapter.word_count}字) "
                            f"+ 合同部分({contract_chapter.para_start_idx}-{contract_chapter.para_end_idx}, {contract_chapter.word_count}字)"
                        )
                    else:
                        self.logger.info(
                            f"跳过拆分: '{chapter.title}' 前半部分内容不足({front_word_count}字 < {min_content_length}字)"
                        )
                else:
                    self.logger.info(
                        f"跳过拆分: '{chapter.title}' 合同聚集区起点太靠前(段落{cluster_start})"
                    )

        # 🆕 插入所有检测到的合同章节
        if contract_chapters_to_insert:
            # 按插入位置倒序插入（避免索引偏移）
            for insert_pos, contract_chapter in reversed(contract_chapters_to_insert):
                chapters_sorted.insert(insert_pos, contract_chapter)

            self.logger.info(f"已插入 {len(contract_chapters_to_insert)} 个合同章节")

            # 🆕 重新分配章节ID，确保ID连续
            for idx, ch in enumerate(chapters_sorted):
                ch.id = f"ch_{idx}"

            self.logger.info(f"章节ID已重新分配，当前共 {len(chapters_sorted)} 个章节")

        return chapters_sorted

    def _extract_chapter_content_with_tables(self, doc: Document, para_start_idx: int, para_end_idx: int) -> tuple:
        """
        提取章节内容,包括段落和表格

        Args:
            doc: Word文档对象
            para_start_idx: 起始段落索引
            para_end_idx: 结束段落索引

        Returns:
            (完整内容文本, 预览文本)
        """
        # 构建段落索引到body元素索引的映射
        para_count = 0
        start_body_idx = None
        end_body_idx = None

        for body_idx, element in enumerate(doc.element.body):
            if isinstance(element, CT_P):
                if para_count == para_start_idx and start_body_idx is None:
                    start_body_idx = body_idx
                if para_count == para_end_idx:
                    end_body_idx = body_idx
                    break
                para_count += 1

        if start_body_idx is None:
            return "", ""

        if end_body_idx is None:
            end_body_idx = len(doc.element.body) - 1

        # 提取内容(跳过章节标题,从start+1开始)
        content_parts = []
        preview_lines = []
        preview_limit = 5

        for body_idx in range(start_body_idx + 1, end_body_idx + 1):
            element = doc.element.body[body_idx]

            if isinstance(element, CT_P):
                # 段落
                from docx.text.paragraph import Paragraph
                para = Paragraph(element, doc)
                text = para.text.strip()
                if text:
                    content_parts.append(text)
                    # 添加到预览
                    if len(preview_lines) < preview_limit:
                        preview_lines.append(text[:100] + ('...' if len(text) > 100 else ''))

            elif isinstance(element, CT_Tbl):
                # 表格
                from docx.table import Table
                table = Table(element, doc)

                # 提取表格文本
                table_text_parts = []
                table_preview_parts = []

                for row_idx, row in enumerate(table.rows):
                    row_data = []
                    for cell in row.cells:
                        cell_text = '\n'.join(p.text.strip() for p in cell.paragraphs if p.text.strip())
                        row_data.append(cell_text)

                    if any(cell.strip() for cell in row_data):  # 非空行
                        row_text = ' | '.join(row_data)
                        table_text_parts.append(row_text)

                        # 添加到预览(表格的前几行)
                        if len(preview_lines) < preview_limit and row_idx < 3:
                            table_preview_parts.append(row_text[:100] + ('...' if len(row_text) > 100 else ''))

                if table_text_parts:
                    # 添加表格标识
                    table_content = f"[表格]\n" + '\n'.join(table_text_parts)
                    content_parts.append(table_content)

                    # 添加表格预览
                    if len(preview_lines) < preview_limit:
                        preview_lines.append("[表格]")
                        preview_lines.extend(table_preview_parts[:preview_limit - len(preview_lines)])

        full_content = '\n'.join(content_parts)
        preview_text = '\n'.join(preview_lines)

        return full_content, preview_text

    def _build_chapter_tree(self, chapters: List[ChapterNode]) -> List[ChapterNode]:
        """
        构建章节层级树

        Args:
            chapters: 扁平章节列表

        Returns:
            根级章节列表（包含子章节）
        """
        if not chapters:
            return []

        # 使用栈来构建树
        root_chapters = []
        stack = []  # [(level, chapter), ...]

        for chapter in chapters:
            # 弹出所有层级 >= 当前章节层级的节点
            while stack and stack[-1][0] >= chapter.level:
                stack.pop()

            if not stack:
                # 当前是根级章节
                root_chapters.append(chapter)
            else:
                # 当前是子章节，添加到父章节的 children
                parent = stack[-1][1]
                parent.children.append(chapter)
                # 更新子章节ID（包含父级ID）
                chapter.id = f"{parent.id}_{len(parent.children)}"

            # 将当前章节入栈
            stack.append((chapter.level, chapter))

        return root_chapters

    def _propagate_skip_status(self, chapter_tree: List[ChapterNode]) -> List[ChapterNode]:
        """
        递归传播父章节的 skip_recommended 状态到子章节
        如果父章节被跳过，则所有子章节及其后代都应该被跳过

        Args:
            chapter_tree: 章节树

        Returns:
            更新后的章节树
        """
        propagated_count = 0

        def propagate_recursive(chapter: ChapterNode):
            """递归传播跳过状态"""
            nonlocal propagated_count

            # 如果当前章节被标记为跳过，传播到所有子章节和后代
            if chapter.skip_recommended:
                for child in chapter.children:
                    if not child.skip_recommended:  # 避免重复计数
                        child.skip_recommended = True
                        child.auto_selected = False
                        propagated_count += 1
                        self.logger.debug(f"  └─ 传播skip状态: {chapter.title} -> {child.title}")
                    # 递归传播到所有后代
                    propagate_recursive(child)
            else:
                # 即使当前章节不被跳过，也要递归检查子章节
                # （因为子章节可能自己匹配黑名单）
                for child in chapter.children:
                    propagate_recursive(child)

        # 遍历所有根级章节
        for root_chapter in chapter_tree:
            propagate_recursive(root_chapter)

        if propagated_count > 0:
            self.logger.info(f"黑名单状态传播完成: 共传播到 {propagated_count} 个子章节")

        return chapter_tree

    def _calculate_statistics(self, chapter_tree: List[ChapterNode]) -> Dict:
        """
        计算统计信息

        Args:
            chapter_tree: 章节树

        Returns:
            统计字典
        """
        stats = {
            "total_chapters": 0,
            "auto_selected": 0,
            "skip_recommended": 0,
            "total_words": 0,
            "estimated_processing_cost": 0.0
        }

        def traverse(chapters):
            for ch in chapters:
                stats["total_chapters"] += 1
                if ch.auto_selected:
                    stats["auto_selected"] += 1
                if ch.skip_recommended:
                    stats["skip_recommended"] += 1
                stats["total_words"] += ch.word_count

                # 递归遍历子章节
                if ch.children:
                    traverse(ch.children)

        traverse(chapter_tree)

        # 估算处理成本（基于字数）
        # 假设：1000字 ≈ 1500 tokens ≈ $0.002（GPT-4o-mini）
        stats["estimated_processing_cost"] = (stats["total_words"] / 1000) * 0.002

        return stats

    def get_selected_chapter_content(self, doc_path: str, selected_chapter_ids: List[str]) -> Dict:
        """
        根据用户选择的章节ID，提取对应的文本内容

        Args:
            doc_path: Word 文档路径
            selected_chapter_ids: 选中的章节ID列表，如 ["ch_0", "ch_1_2"]

        Returns:
            {
                "success": True/False,
                "chapters": [
                    {
                        "id": "ch_0",
                        "title": "第一章 项目概述",
                        "content": "完整章节文本内容...",
                        "word_count": 1500
                    },
                    ...
                ],
                "total_words": 8000
            }
        """
        try:
            # 重新解析文档（获取完整章节信息）
            result = self.parse_document_structure(doc_path)
            if not result["success"]:
                return result

            chapters = self._flatten_chapters(result["chapters"])

            # 打开文档
            doc = Document(doc_path)

            # 提取选中章节的内容
            selected_chapters = []
            total_words = 0

            for chapter_dict in chapters:
                if chapter_dict["id"] in selected_chapter_ids:
                    # 提取内容
                    start_idx = chapter_dict["para_start_idx"]
                    end_idx = chapter_dict["para_end_idx"]

                    content_paras = doc.paragraphs[start_idx : end_idx + 1]
                    content = '\n'.join(p.text for p in content_paras)

                    selected_chapters.append({
                        "id": chapter_dict["id"],
                        "title": chapter_dict["title"],
                        "content": content,
                        "word_count": len(content.replace(' ', '').replace('\n', ''))
                    })

                    total_words += selected_chapters[-1]["word_count"]

            self.logger.info(f"提取了 {len(selected_chapters)} 个章节，共 {total_words} 字")

            return {
                "success": True,
                "chapters": selected_chapters,
                "total_words": total_words
            }

        except Exception as e:
            self.logger.error(f"提取章节内容失败: {e}")
            return {
                "success": False,
                "chapters": [],
                "total_words": 0,
                "error": str(e)
            }

    def export_chapter_to_docx(self, doc_path: str, chapter_id: str,
                              output_path: str = None) -> Dict:
        """
        将指定章节导出为独立的Word文档（保留原始格式）

        Args:
            doc_path: 原始Word文档路径
            chapter_id: 章节ID (如 "ch_4")
            output_path: 输出文件路径（可选，默认临时目录）

        Returns:
            {
                "success": True,
                "file_path": "/path/to/exported.docx",
                "chapter_title": "第五部分 响应文件格式",
                "word_count": 1500
            }
        """
        try:
            from docx import Document
            from tempfile import NamedTemporaryFile
            from copy import deepcopy

            # 1. 解析文档结构，定位目标章节
            result = self.parse_document_structure(doc_path)
            if not result["success"]:
                return result

            chapters = self._flatten_chapters(result["chapters"])
            target_chapter = None

            for ch in chapters:
                if ch["id"] == chapter_id:
                    target_chapter = ch
                    break

            if not target_chapter:
                return {
                    "success": False,
                    "error": f"未找到章节ID: {chapter_id}"
                }

            # 2. 打开原始文档
            source_doc = Document(doc_path)

            # 3. 创建新文档
            new_doc = Document()

            # 4. 复制章节内容（保留格式）
            para_start = target_chapter["para_start_idx"]
            para_end = target_chapter.get("para_end_idx")

            if para_end is None:
                para_end = len(source_doc.paragraphs) - 1

            self.logger.info(f"导出章节: {target_chapter['title']}")
            self.logger.info(f"段落范围: {para_start} - {para_end}")

            # 复制段落（使用深拷贝保留格式）
            for i in range(para_start, min(para_end + 1, len(source_doc.paragraphs))):
                source_para = source_doc.paragraphs[i]

                # 使用XML深拷贝（最佳格式保留）
                # 导入段落的完整XML节点
                new_para_element = deepcopy(source_para._element)
                new_doc.element.body.append(new_para_element)

            # 5. 保存到临时文件或指定路径
            if output_path is None:
                # 使用临时文件
                temp_file = NamedTemporaryFile(
                    delete=False,
                    suffix='.docx',
                    prefix='chapter_template_'
                )
                output_path = temp_file.name
                temp_file.close()

            new_doc.save(output_path)

            self.logger.info(f"章节已导出: {output_path}")

            return {
                "success": True,
                "file_path": output_path,
                "chapter_title": target_chapter["title"],
                "word_count": target_chapter.get("word_count", 0),
                "para_count": para_end - para_start + 1
            }

        except Exception as e:
            self.logger.error(f"导出章节失败: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return {
                "success": False,
                "error": str(e)
            }

    def export_multiple_chapters_to_docx(self, doc_path: str, chapter_ids: List[str], output_path: str = None) -> Dict:
        """
        将多个章节导出为单个Word文档

        Args:
            doc_path: 源文档路径
            chapter_ids: 章节ID列表
            output_path: 输出路径（可选）

        Returns:
            {
                "success": bool,
                "file_path": str,
                "chapter_titles": List[str],
                "chapter_count": int
            }
        """
        from docx import Document
        from tempfile import NamedTemporaryFile
        from copy import deepcopy

        try:
            # 使用智能路径解析（兼容多种环境）
            resolved_path = resolve_file_path(doc_path)
            if not resolved_path:
                return {"success": False, "error": f"文档路径解析失败: {doc_path}"}

            doc_path = str(resolved_path)  # 使用解析后的绝对路径

            # 解析文档结构
            result = self.parse_document_structure(doc_path)
            chapters = self._flatten_chapters(result["chapters"])

            # ⭐ 关键修复：过滤掉父章节已被选中的子章节，避免重复导出
            filtered_chapter_ids = self._filter_redundant_chapters(chapter_ids)
            if len(filtered_chapter_ids) < len(chapter_ids):
                removed_count = len(chapter_ids) - len(filtered_chapter_ids)
                self.logger.info(f"去重完成：移除了 {removed_count} 个冗余子章节")
                self.logger.info(f"  原始章节列表: {chapter_ids}")
                self.logger.info(f"  去重后章节列表: {filtered_chapter_ids}")

            # 按ID查找目标章节并按原文档顺序排序
            target_chapters = []
            for ch in chapters:
                if ch["id"] in filtered_chapter_ids:
                    target_chapters.append(ch)

            if not target_chapters:
                return {"success": False, "error": "未找到指定章节"}

            # 打开源文档
            source_doc = Document(doc_path)
            # 使用源文档作为模板，保留所有样式和页面设置
            new_doc = Document(doc_path)

            # 清空模板文档的所有body内容（段落+表格），保留样式定义、页面设置、页眉页脚等
            for element in list(new_doc.element.body):
                element.getparent().remove(element)

            chapter_titles = []

            # 依次复制每个章节
            for i, chapter in enumerate(target_chapters):
                chapter_titles.append(chapter["title"])

                # 添加章节标题（除第一个章节外，其他章节前加分页符）
                if i > 0:
                    new_doc.add_page_break()

                # 复制章节内容（包括段落和表格）
                para_start = chapter["para_start_idx"]
                para_end = chapter.get("para_end_idx", len(source_doc.paragraphs) - 1)

                # 构建段落索引到body索引的映射
                para_count = 0
                start_body_idx = None
                end_body_idx = None

                for body_idx, element in enumerate(source_doc.element.body):
                    if isinstance(element, CT_P):
                        if para_count == para_start and start_body_idx is None:
                            start_body_idx = body_idx
                        if para_count == para_end:
                            end_body_idx = body_idx
                            break
                        para_count += 1

                # 复制范围内的所有元素（段落+表格）
                if start_body_idx is not None and end_body_idx is not None:
                    for body_idx in range(start_body_idx, end_body_idx + 1):
                        element = source_doc.element.body[body_idx]
                        new_element = deepcopy(element)
                        new_doc.element.body.append(new_element)

            # 保存到临时文件
            if output_path is None:
                temp_file = NamedTemporaryFile(delete=False, suffix='.docx', prefix='chapters_template_')
                output_path = temp_file.name
                temp_file.close()

            new_doc.save(output_path)

            logger.info(f"批量导出成功: {len(target_chapters)}个章节 -> {output_path}")

            return {
                "success": True,
                "file_path": output_path,
                "chapter_titles": chapter_titles,
                "chapter_count": len(target_chapters)
            }

        except Exception as e:
            logger.error(f"批量导出失败: {str(e)}")
            return {"success": False, "error": str(e)}

    def _flatten_chapters(self, chapter_dicts: List[Dict]) -> List[Dict]:
        """将章节树扁平化为列表"""
        flat = []

        def traverse(chapters):
            for ch in chapters:
                flat.append(ch)
                if ch.get("children"):
                    traverse(ch["children"])

        traverse(chapter_dicts)
        return flat

    def _filter_redundant_chapters(self, chapter_ids: List[str]) -> List[str]:
        """
        过滤掉父章节已被选中的子章节，避免重复导出

        例如：如果同时选择了 ch_3 和 ch_3_2，则只保留 ch_3

        Args:
            chapter_ids: 原始章节ID列表

        Returns:
            去重后的章节ID列表
        """
        filtered_ids = []

        for chapter_id in chapter_ids:
            # 检查是否有父章节已在列表中
            has_parent_selected = False

            # 分析章节ID的层级结构（ch_3_2_1 -> ["ch_3", "ch_3_2", "ch_3_2_1"]）
            parts = chapter_id.split('_')
            for i in range(1, len(parts)):
                # 构建可能的父章节ID
                parent_id = '_'.join(parts[:i+1])
                if parent_id != chapter_id and parent_id in chapter_ids:
                    has_parent_selected = True
                    self.logger.debug(f"跳过子章节 {chapter_id}，因为父章节 {parent_id} 已被选中")
                    break

            # 如果没有父章节被选中，保留该章节
            if not has_parent_selected:
                filtered_ids.append(chapter_id)

        return filtered_ids

    # ========================================
    # 新增：基于语义锚点的解析方法
    # ========================================

    def remove_leading_patterns(self, text: str) -> Tuple[str, int]:
        """
        移除文本开头的编号模式，返回纯净文本和推测的层级（改进4：支持更多编号格式）

        Args:
            text: 原始文本

        Returns:
            (纯净文本, 层级)
            层级判断：
            - "第X部分" / "第X章" -> 1
            - "1." / "一、" -> 1
            - "1.1" -> 2
            - "1.1.1" -> 3
            - "1.1.1.1" -> 4 (改进4新增)
            - "附件X:" / "附表X:" -> 1 (改进4新增)
        """
        text = text.strip()
        original_text = text
        level = 1  # 默认层级

        # 移除所有空格和制表符（标准化）
        text_normalized = re.sub(r'\s+', '', text)

        # 检测层级并移除编号（改进4：增加四级编号和附件编号支持）
        if re.match(r'^第[一二三四五六七八九十百\d]+部分', text):
            level = 1
            text = re.sub(r'^第[一二三四五六七八九十百\d]+部分\s*', '', text)
        elif re.match(r'^第[一二三四五六七八九十百\d]+章', text):
            level = 1
            text = re.sub(r'^第[一二三四五六七八九十百\d]+章\s*', '', text)
        elif re.match(r'^\d+\.\d+\.\d+\.\d+', text_normalized):
            level = 4  # 改进4：四级编号
            text = re.sub(r'^\d+\.\d+\.\d+\.\d+\s*', '', text)
        elif re.match(r'^\d+\.\d+\.\d+', text_normalized):
            level = 3
            text = re.sub(r'^\d+\.\d+\.\d+\s*', '', text)
        elif re.match(r'^\d+\.\d+[^\d]', text_normalized):
            level = 2
            text = re.sub(r'^\d+\.\d+\s*', '', text)
        elif re.match(r'^\d+\.', text_normalized):
            level = 1
            text = re.sub(r'^\d+\.\s*', '', text)
        elif re.match(r'^[一二三四五六七八九十]+、', text):
            level = 1
            text = re.sub(r'^[一二三四五六七八九十]+、\s*', '', text)
        elif re.match(r'^（[一二三四五六七八九十]+）', text):
            level = 2
            text = re.sub(r'^（[一二三四五六七八九十]+）\s*', '', text)
        elif re.match(r'^\([一二三四五六七八九十]+\)', text):
            level = 2
            text = re.sub(r'^\([一二三四五六七八九十]+\)\s*', '', text)
        elif re.match(r'^附件[一二三四五六七八九十\d]+[:：]', text):
            level = 1  # 改进4：附件编号
            text = re.sub(r'^附件[一二三四五六七八九十\d]+[:：]\s*', '', text)
        elif re.match(r'^附表[一二三四五六七八九十\d]+[:：]', text):
            level = 1  # 改进4：附表编号
            text = re.sub(r'^附表[一二三四五六七八九十\d]+[:：]\s*', '', text)
        elif re.match(r'^附录[一二三四五六七八九十\d]+[:：]', text):
            level = 1  # 改进4：附录编号
            text = re.sub(r'^附录[一二三四五六七八九十\d]+[:：]\s*', '', text)

        # 移除常见分隔符
        text = text.strip().strip('：:').strip()

        self.logger.debug(f"移除编号: '{original_text}' -> '{text}' (层级{level})")

        return text, level

    def fuzzy_match_title(self, text: str, target: str, threshold: float = 0.75) -> float:
        """
        计算两个标题的相似度

        Args:
            text: 待匹配文本
            target: 目标文本（来自目录）
            threshold: 相似度阈值

        Returns:
            相似度分数 (0-1)，大于等于 threshold 视为匹配
        """
        # 标准化：移除所有空格
        text_clean = re.sub(r'\s+', '', text)
        target_clean = re.sub(r'\s+', '', target)

        # 完全匹配
        if text_clean == target_clean:
            return 1.0

        # 包含匹配
        if text_clean in target_clean or target_clean in text_clean:
            shorter = min(len(text_clean), len(target_clean))
            longer = max(len(text_clean), len(target_clean))
            return shorter / longer

        # 使用 SequenceMatcher 计算相似度
        similarity = SequenceMatcher(None, text_clean, target_clean).ratio()

        # 部分子串匹配（解决"单一来源采购谈判邀请" vs "单一来源采购邀请"）
        if similarity < threshold and len(target_clean) >= 6:
            # 尝试从长到短的子串
            for length in range(len(target_clean), 5, -1):
                substr = target_clean[:length]
                if substr in text_clean:
                    match_ratio = length / len(target_clean)
                    if match_ratio >= 0.6:  # 至少60%匹配
                        return match_ratio

        # 特殊处理：目标以"书"/"表"等单字结尾，正文可能没有
        # 例如："技术需求书" vs "技术需求"，"XX表" vs "XX"
        if len(target_clean) > 3 and target_clean[-1] in ['书', '表', '单', '册', '函']:
            target_without_suffix = target_clean[:-1]
            if text_clean == target_without_suffix or text_clean in target_without_suffix:
                return 0.95  # 高分但不是满分
            # 计算去掉后缀后的相似度
            suffix_similarity = SequenceMatcher(None, text_clean, target_without_suffix).ratio()
            if suffix_similarity > similarity:
                return suffix_similarity

        return similarity

    def is_section_anchor(self, paragraph, toc_targets: List[str], start_idx: int = 0) -> Tuple[bool, Optional[str], int, str]:
        """
        判断段落是否是章节锚点

        Args:
            paragraph: docx Paragraph 对象
            toc_targets: 目录标题列表（已清理）
            start_idx: 当前段落在文档中的索引（用于跳过目录区域）

        Returns:
            (是否匹配, 匹配的目标标题, 层级, 匹配原因)
        """
        para_text = paragraph.text.strip()

        # 跳过空行或太短的段落
        if not para_text or len(para_text) < 3:
            return False, None, 0, "空行或太短"

        # 跳过明显的非标题内容（如长段落）
        if len(para_text) > 100:
            return False, None, 0, "段落过长"

        # A. 移除编号，获取纯净文本和层级
        clean_text, detected_level = self.remove_leading_patterns(para_text)

        # 关键改进：只匹配一级章节（"第X部分"格式）
        # 这样可以避免将目录内的二三级标题误识别为章节
        has_part_number = bool(re.match(r'^第[一二三四五六七八九十\d]+部分', para_text))

        # B. 语义匹配：与目录目标进行模糊匹配
        best_match = None
        best_score = 0.0
        best_target = None

        for target in toc_targets:
            # 也移除目标的编号
            target_clean, _ = self.remove_leading_patterns(target)

            score = self.fuzzy_match_title(clean_text, target_clean, threshold=0.75)

            if score > best_score:
                best_score = score
                best_target = target
                best_match = target_clean

        # 判断是否匹配成功（需要更严格的条件）
        # 策略：
        # 1. 超高相似度(≥0.90) - 直接接受
        # 2. 高相似度(≥0.80) + 格式匹配
        # 3. 中等相似度(≥0.70) + 有"第X部分"格式

        if best_score >= 0.90:
            # 超高相似度，直接接受（即使没有"第X部分"）
            reason = f"超高相似度匹配 {best_score:.0%} -> '{best_target}'"
            self.logger.info(f"  ✓ 锚点识别成功: 段落 {start_idx}: '{para_text}' ({reason})")
            return True, best_target, detected_level, reason
        elif best_score >= 0.80:
            # 高相似度，需要额外验证
            target_has_part = bool(re.search(r'第[一二三四五六七八九十\d]+部分', best_target))

            # 如果目标有"第X部分"，优先匹配有编号的段落
            # 但如果段落没有"第X部分"，也接受（可能是文档格式错误）
            if target_has_part and has_part_number:
                reason = f"语义匹配 {best_score:.0%} + 部分编号 -> '{best_target}'"
            elif target_has_part and not has_part_number:
                # 段落没有"第X部分"编号，但相似度够高，可能是格式错误
                # 只在相似度>=0.85时接受
                if best_score < 0.85:
                    return False, None, 0, f"目标有部分编号但段落无，且相似度不够高（{best_score:.0%}）"
                reason = f"语义匹配 {best_score:.0%}（段落缺编号） -> '{best_target}'"
            else:
                reason = f"语义匹配 {best_score:.0%} -> '{best_target}'"

            self.logger.info(f"  ✓ 锚点识别成功: 段落 {start_idx}: '{para_text}' ({reason})")
            return True, best_target, detected_level, reason
        elif best_score >= 0.70 and has_part_number:
            # 中等相似度，但有"第X部分"格式，也接受
            reason = f"语义匹配 {best_score:.0%} + 部分编号 -> '{best_target}'"
            self.logger.info(f"  ✓ 锚点识别成功: 段落 {start_idx}: '{para_text}' ({reason})")
            return True, best_target, detected_level, reason

        # C. 辅助：检查是否有 Heading 样式（作为次要依据）
        heading_level = self._get_heading_level(paragraph)
        if heading_level > 0:
            # 即使目录中没有，但如果是 Heading 样式且有编号格式，也可能是章节
            # 但只接受一级标题（Heading 1）
            if heading_level == 1 and any(re.match(pattern, para_text) for pattern in self.NUMBERING_PATTERNS):
                reason = f"Heading{heading_level}样式+编号格式"
                self.logger.info(f"  ✓ 锚点识别成功（样式）: 段落 {start_idx}: '{para_text}' ({reason})")
                return True, clean_text, heading_level, reason

        return False, None, 0, f"无匹配（最佳相似度{best_score:.0%}）"

    def _calculate_content_start_idx(self, doc: Document, toc_end_idx: int, toc_items_count: int) -> int:
        """
        计算正文起始位置（简化版：直接从目录结束后开始）

        策略：
        目录已通过重复检测正确结束，直接从目录结束位置的下一段开始搜索即可

        Args:
            doc: Word文档对象
            toc_end_idx: 目录结束段落索引
            toc_items_count: 目录项数量（保留参数以兼容调用）

        Returns:
            正文起始段落索引
        """
        # ⭐️ 最简单策略：目录结束后直接开始搜索
        # 理由：
        # 1. 目录重复检测已确保目录正确结束
        # 2. 目录后可能只有分页符或几行空白
        # 3. 跳过太多段会错过真实章节（如"竞争性磋商公告"）
        min_start = toc_end_idx + 1

        self.logger.info(f"正文起始位置: 目录结束于段落{toc_end_idx}, 从段落{min_start}开始搜索")

        # 直接返回min_start，让语义锚点算法自己去找章节
        # 不再做复杂的智能检测，避免跳过真实章节
        return min_start

    def _is_metadata_section_title(self, title: str) -> bool:
        """
        判断标题是否为元数据章节（不应作为正文章节）（改进5：扩展元数据模式）

        Args:
            title: 章节标题

        Returns:
            是否为元数据章节
        """
        metadata_patterns = [
            # 文档结构相关
            r'.*文件构成.*',
            r'.*招标文件组成.*',
            r'.*文档组成.*',
            r'.*采购文件清单.*',
            r'.*文档说明.*',
            r'.*文件说明.*',
            r'.*文件目录.*',
            r'.*文件清单.*',
            # 项目信息相关（改进5新增）
            r'^项目编号.*',
            r'^项目名称.*',
            r'.*项目概况表.*',
            r'.*项目信息表.*',
            # 目录类（改进5新增）
            r'^目\s*录$',
            r'^contents$',
            r'^索\s*引$',
            # 前言、序言类（改进5新增）
            r'^前\s*言$',
            r'^序\s*言$',
            r'^引\s*言$',
            # 其他元数据（改进5新增）
            r'.*编制说明.*',
            r'.*阅读说明.*',
            r'.*文档版本.*',
            r'.*版本历史.*',
        ]

        for pattern in metadata_patterns:
            if re.match(pattern, title, re.IGNORECASE):
                return True
        return False

    def _is_file_composition_section(self, doc: Document, para_idx: int, toc_targets: List[str]) -> bool:
        """
        检测当前段落是否为"文件构成"部分（连续的章节标题列表，无实际内容）

        特征：
        1. 段落文本匹配某个目录项
        2. 前后段落也是连续的章节标题
        3. 章节标题之间无内容或只有极少内容
        4. 前置段落包含"由...组成"、"文件构成"等关键词

        Bug修复: 需要同时满足"有关键词"和"连续标题"两个条件，避免误判真实章节

        Args:
            doc: Word文档对象
            para_idx: 当前段落索引
            toc_targets: 目录标题列表

        Returns:
            是否为文件构成部分
        """
        # 方法1: 检查前置段落是否包含"文件构成"相关关键词
        composition_keywords = [
            '由下述部分组成', '由以下部分组成', '文件构成', '包括以下部分',
            '包括下列部分', '由下列部分组成', '文件包括', '文件由',
            '由以下文件组成', '包含以下文件', '谈判文件'
        ]

        has_composition_keyword = False
        # 检查前5个段落（扩大范围）
        for i in range(max(0, para_idx - 5), para_idx):
            prev_text = doc.paragraphs[i].text.strip()
            if any(keyword in prev_text for keyword in composition_keywords):
                self.logger.debug(f"检测到文件构成关键词: 段落{i} 含 '{prev_text[:50]}'")
                has_composition_keyword = True
                break

        # 方法2: 检查当前段落及前后区域是否有连续的章节标题且之间无内容
        check_range = 5
        consecutive_titles = 0
        title_positions = []  # 记录标题位置

        for i in range(max(0, para_idx - check_range), min(len(doc.paragraphs), para_idx + check_range + 1)):
            para_text = doc.paragraphs[i].text.strip()

            # 检查是否为章节标题格式（扩展：包含数字列表格式）
            is_chapter_title = bool(
                re.match(r'^第[一二三四五六七八九十\d]+部分', para_text) or
                re.match(r'^第[一二三四五六七八九十\d]+章', para_text) or
                re.match(r'^\d+[\.\、][\u4e00-\u9fa5]{3,20}$', para_text)  # 匹配 "1.xxx" 或 "2、xxx" 格式
            )

            if is_chapter_title:
                consecutive_titles += 1
                title_positions.append(i)

        # 方法3: 检查标题之间是否有实质内容
        has_content_between_titles = False
        if len(title_positions) >= 2:
            # 检查任意两个相邻标题之间的段落
            for j in range(len(title_positions) - 1):
                start_pos = title_positions[j]
                end_pos = title_positions[j + 1]

                # 计算之间的内容字数
                content_chars = 0
                for k in range(start_pos + 1, end_pos):
                    content_chars += len(doc.paragraphs[k].text.strip())

                # 如果任意两个标题之间有超过100字的内容，说明不是文件构成列表
                if content_chars > 100:
                    has_content_between_titles = True
                    self.logger.debug(f"检测到标题间有实质内容: 段落{start_pos}-{end_pos}之间有{content_chars}字")
                    break

        # 判断逻辑：需要同时满足以下条件才判定为文件构成
        # 1. 有"文件构成"关键词 AND
        # 2. 有3个以上连续标题 AND
        # 3. 标题之间没有实质内容
        is_composition = (
            has_composition_keyword and
            consecutive_titles >= 3 and
            not has_content_between_titles
        )

        if is_composition:
            self.logger.debug(
                f"确认为文件构成: 段落{para_idx}, "
                f"有关键词={has_composition_keyword}, "
                f"连续标题={consecutive_titles}, "
                f"无实质内容={not has_content_between_titles}"
            )

        return is_composition

    def _detect_content_tags(self, content_text: str) -> List[str]:
        """
        检测章节内容标签

        基于内容关键词匹配，检测章节包含的信息类型

        Args:
            content_text: 章节内容文本

        Returns:
            标签列表（可能包含多个标签）
        """
        tags = []
        content_lower = content_text.lower()

        # 定义标签及其关键词
        tag_rules = {
            "评分办法": ["评分办法", "评分标准", "评审办法", "打分", "评分细则", "综合评分"],
            "评分表": ["前附表", "评分表", "附表", "评审表"],
            "供应商资质": ["供应商资质", "资质要求", "资格要求", "投标人资格", "供应商须知",
                       "投标须知", "民事责任", "商业信誉", "技术能力"],
            "文件格式": ["文件格式", "格式要求", "编制要求", "装订要求", "响应文件编制"],
            "技术需求": ["技术规范", "技术说明", "技术需求", "技术要求", "技术参数",
                       "性能指标", "功能要求", "需求说明"]
        }

        # 检测每个标签
        for tag, keywords in tag_rules.items():
            for keyword in keywords:
                if keyword in content_lower:
                    tags.append(tag)
                    break  # 匹配到一个关键词即可，不需要继续检查该标签的其他关键词

        return tags

    def _extract_chapter_content(self, doc: Document, chapter: ChapterNode):
        """
        提取章节内容、字数和预览文本

        Args:
            doc: Word文档对象
            chapter: 章节节点（会被修改）
        """
        # 提取内容（从标题的下一段开始）
        content_paras = doc.paragraphs[chapter.para_start_idx + 1 : chapter.para_end_idx + 1]

        # 计算字数
        content_text = '\n'.join(p.text for p in content_paras)
        chapter.word_count = len(content_text.replace(' ', '').replace('\n', ''))

        # 提取预览文本（前5行，每行最多100字符）
        preview_lines = []
        for p in content_paras[:5]:
            text = p.text.strip()
            if text:
                preview_lines.append(text[:100] + ('...' if len(text) > 100 else ''))
            if len(preview_lines) >= 5:
                break

        chapter.preview_text = '\n'.join(preview_lines) if preview_lines else "(无内容)"

        # 检测内容标签
        chapter.content_tags = self._detect_content_tags(content_text)

        # 【新增】对于level 1-2的章节，提取内容样本并进行合同识别
        if chapter.level <= 2 and chapter.para_end_idx and chapter.para_end_idx > chapter.para_start_idx:
            # 提取内容样本用于合同识别
            chapter.content_sample = self._extract_content_sample(
                doc, chapter.para_start_idx, chapter.para_end_idx, sample_size=2000
            )

            # 基于内容进行合同识别
            is_contract, density, reason = self._is_contract_chapter(
                chapter.title, chapter.content_sample
            )

            if is_contract:
                # 更新skip_recommended标记
                if not chapter.skip_recommended:  # 避免重复标记
                    chapter.skip_recommended = True
                    chapter.auto_selected = False
                    self.logger.info(
                        f"  ✓ 合同章节识别: '{chapter.title}' - {reason}"
                    )
                else:
                    self.logger.debug(
                        f"  ✓ 合同章节已标记: '{chapter.title}' - {reason}"
                    )


if __name__ == '__main__':
    # 测试代码
    import sys

    if len(sys.argv) > 1:
        doc_path = sys.argv[1]
    else:
        print("用法: python structure_parser.py <word文档路径>")
        sys.exit(1)

    parser = DocumentStructureParser()
    result = parser.parse_document_structure(doc_path)

    if result["success"]:
        print(f"\n✅ 解析成功！")
        print(f"统计信息: {result['statistics']}")
        print(f"\n章节结构:")

        def print_tree(chapters, indent=0):
            for ch in chapters:
                prefix = "  " * indent
                status = "✅" if ch["auto_selected"] else "❌" if ch["skip_recommended"] else "⚪"
                print(f"{prefix}{status} [{ch['level']}级] {ch['title']} ({ch['word_count']}字)")
                if ch.get("children"):
                    print_tree(ch["children"], indent + 1)

        print_tree(result["chapters"])
    else:
        print(f"\n❌ 解析失败: {result.get('error')}")
