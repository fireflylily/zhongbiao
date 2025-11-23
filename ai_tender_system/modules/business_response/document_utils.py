#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档操作工具类
提供Word文档的底层操作方法
"""

import os
from pathlib import Path
from docx.table import Table
from docx.text.paragraph import Paragraph
from lxml.etree import QName

# 导入公共模块
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from common import get_module_logger, resolve_file_path


class DocumentUtils:
    """文档操作工具类"""

    def __init__(self):
        self.logger = get_module_logger("document_utils")

    def resolve_file_path(self, file_path: str) -> str:
        """
        解析文件路径（支持相对路径和绝对路径）

        使用公共的resolve_file_path函数处理路径解析
        """
        if not file_path:
            return file_path

        resolved = resolve_file_path(file_path)
        if resolved:
            self.logger.debug(f"路径解析: {file_path} -> {resolved}")
            return str(resolved)
        else:
            self.logger.warning(f"无法解析文件路径: {file_path}")
            return file_path

    def insert_paragraph_after(self, target_para, clean_format=True):
        """在目标段落后插入新段落

        Args:
            target_para: 目标段落对象
            clean_format: 是否清理新段落格式（移除下划线/删除线/高亮），默认True

        Returns:
            新创建的段落对象
        """
        try:
            # 使用底层XML操作在目标段落后插入新段落
            # 注意：makeelement 需要使用 QName 来指定带命名空间的标签
            w_namespace = target_para._element.nsmap.get('w', 'http://schemas.openxmlformats.org/wordprocessingml/2006/main')
            new_p_element = target_para._element.makeelement(QName(w_namespace, 'p'), nsmap=target_para._element.nsmap)
            target_para._element.addnext(new_p_element)

            # 将新创建的 XML 元素包装为 Paragraph 对象并返回
            parent = target_para._parent
            new_paragraph = Paragraph(new_p_element, parent)

            # 🆕 格式清理：清理新段落的格式污染
            if clean_format:
                try:
                    # 清理段落中所有Run的格式
                    for run in new_paragraph.runs:
                        run.font.underline = None
                        run.font.strike = None
                        if hasattr(run.font, 'highlight_color'):
                            run.font.highlight_color = None
                    self.logger.debug("清理新段落格式：移除下划线/删除线/高亮")
                except Exception as e:
                    self.logger.debug(f"清理新段落格式时出现异常（可忽略）: {e}")

            return new_paragraph

        except Exception as e:
            # 输出详细错误信息用于调试
            self.logger.error(f"❌ 在段落后插入新段落失败: {e}")
            self.logger.error(f"  目标段落文本: '{target_para.text[:100] if target_para.text else ''}'")
            self.logger.error(f"  父容器类型: {type(target_para._parent).__name__}")
            self.logger.error(f"  段落对象: {target_para}")
            raise

    def find_next_table_after_paragraph(self, paragraph):
        """查找段落后面的第一个表格

        Args:
            paragraph: 目标段落对象

        Returns:
            Table对象，如果没有找到返回None
        """
        try:
            # 获取段落的XML元素
            para_element = paragraph._element

            # 遍历段落后面的兄弟元素
            for sibling in para_element.itersiblings():
                # 检查是否是表格元素 (<w:tbl>)
                if sibling.tag.endswith('}tbl'):
                    # 找到表格，包装成Table对象返回
                    parent = paragraph._parent
                    table = Table(sibling, parent)
                    return table
                # 如果遇到段落或其他元素，停止搜索
                elif sibling.tag.endswith('}p'):
                    # 遇到其他段落，说明表格不是紧跟着的
                    break

            return None

        except Exception as e:
            self.logger.error(f"查找段落后表格失败: {e}")
            return None
