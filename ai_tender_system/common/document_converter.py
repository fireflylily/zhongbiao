#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Word文档与HTML互转工具

功能：
1. Word (docx) → HTML（用于编辑器加载）
2. HTML → Word (docx)（用于保存编辑内容）

依赖：
- mammoth: Word转HTML（保留格式）
- python-docx: HTML转Word
- BeautifulSoup4: HTML解析
"""

import os
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

try:
    import mammoth
    MAMMOTH_AVAILABLE = True
except ImportError:
    MAMMOTH_AVAILABLE = False
    print("警告: mammoth未安装，Word转HTML功能将不可用。请运行: pip install mammoth")

try:
    from docx import Document
    from docx.shared import Pt, RGBColor, Inches
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    PYTHON_DOCX_AVAILABLE = True
except ImportError:
    PYTHON_DOCX_AVAILABLE = False
    print("警告: python-docx未安装，HTML转Word功能将不可用。请运行: pip install python-docx")

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False
    print("警告: beautifulsoup4未安装，HTML解析功能受限。请运行: pip install beautifulsoup4")


class DocumentConverter:
    """文档格式转换器"""

    def __init__(self, config: Optional[Any] = None):
        """
        初始化转换器

        Args:
            config: 配置对象（可选）
        """
        self.config = config

    def word_to_html(self, docx_path: str) -> str:
        """
        将Word文档转换为HTML

        Args:
            docx_path: Word文档路径

        Returns:
            HTML字符串

        Raises:
            ImportError: mammoth未安装
            FileNotFoundError: 文件不存在
            Exception: 转换失败
        """
        if not MAMMOTH_AVAILABLE:
            raise ImportError("mammoth未安装，请运行: pip install mammoth")

        if not os.path.exists(docx_path):
            raise FileNotFoundError(f"文件不存在: {docx_path}")

        try:
            print(f"[DocumentConverter] 开始转换Word为HTML: {docx_path}")

            with open(docx_path, "rb") as docx_file:
                # 使用mammoth转换，保留样式
                result = mammoth.convert_to_html(
                    docx_file,
                    style_map="""
                    p[style-name='Heading 1'] => h1:fresh
                    p[style-name='Heading 2'] => h2:fresh
                    p[style-name='Heading 3'] => h3:fresh
                    p[style-name='Heading 4'] => h4:fresh
                    p[style-name='标题 1'] => h1:fresh
                    p[style-name='标题 2'] => h2:fresh
                    p[style-name='标题 3'] => h3:fresh
                    table => table.tender-table
                    """
                )

            html_content = result.value

            # 添加基础样式
            html_with_style = f"""
<div class="document-content">
{html_content}
</div>
            """

            # 输出警告信息（如果有）
            if result.messages:
                print(f"[DocumentConverter] 转换警告: {len(result.messages)}条")
                for msg in result.messages[:5]:  # 只输出前5条
                    print(f"  - {msg}")

            print(f"[DocumentConverter] Word转HTML完成，长度: {len(html_with_style)}")

            return html_with_style

        except Exception as e:
            print(f"[DocumentConverter] Word转HTML失败: {e}")
            raise Exception(f"Word转HTML失败: {str(e)}")

    def html_to_word(
        self,
        html_content: str,
        output_path: Optional[str] = None,
        project_id: Optional[int] = None,
        document_type: str = 'document'
    ) -> str:
        """
        将HTML内容转换为Word文档

        Args:
            html_content: HTML内容
            output_path: 输出文件路径（可选，自动生成）
            project_id: 项目ID（用于生成文件名）
            document_type: 文档类型（business_response / point_to_point / tech_proposal）

        Returns:
            生成的Word文档路径

        Raises:
            ImportError: 依赖库未安装
            Exception: 转换失败
        """
        if not PYTHON_DOCX_AVAILABLE:
            raise ImportError("python-docx未安装，请运行: pip install python-docx")

        if not BS4_AVAILABLE:
            raise ImportError("beautifulsoup4未安装，请运行: pip install beautifulsoup4")

        try:
            print(f"[DocumentConverter] 开始转换HTML为Word")

            # 解析HTML
            soup = BeautifulSoup(html_content, 'html.parser')

            # 创建Word文档
            doc = Document()

            # 设置默认字体
            doc.styles['Normal'].font.name = '宋体'
            doc.styles['Normal'].font.size = Pt(12)

            # 遍历HTML元素，转换为Word
            self._parse_html_to_docx(soup, doc)

            # 生成输出路径
            if not output_path:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename_map = {
                    'business_response': f'商务应答_{timestamp}.docx',
                    'point_to_point': f'点对点应答_{timestamp}.docx',
                    'tech_proposal': f'技术方案_{timestamp}.docx'
                }
                filename = filename_map.get(document_type, f'文档_{timestamp}.docx')

                # 使用config获取输出目录
                if self.config:
                    output_dir = self.config.get_path('output')
                else:
                    # 降级方案：使用相对路径
                    output_dir = Path(__file__).parent.parent / 'data' / 'outputs'

                output_dir.mkdir(parents=True, exist_ok=True)
                output_path = str(output_dir / filename)

            # 保存文档
            doc.save(output_path)

            print(f"[DocumentConverter] HTML转Word完成: {output_path}")

            return output_path

        except Exception as e:
            print(f"[DocumentConverter] HTML转Word失败: {e}")
            raise Exception(f"HTML转Word失败: {str(e)}")

    def _parse_html_to_docx(self, soup: BeautifulSoup, doc: Document):
        """
        递归解析HTML并添加到Word文档

        Args:
            soup: BeautifulSoup对象
            doc: Word文档对象
        """
        # 查找body内容，如果没有就用根元素
        body = soup.find('body') or soup
        content_div = body.find('div', class_='document-content') or body

        for element in content_div.children:
            if not element.name:  # 跳过文本节点
                continue

            # 标题
            if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                level = int(element.name[1])
                heading_map = {
                    1: 'Heading 1',
                    2: 'Heading 2',
                    3: 'Heading 3',
                    4: 'Heading 4'
                }
                style = heading_map.get(level, 'Heading 1')

                paragraph = doc.add_heading(element.get_text(), level=level)

            # 段落
            elif element.name == 'p':
                paragraph = doc.add_paragraph(element.get_text())
                self._apply_paragraph_style(element, paragraph)

            # 列表
            elif element.name in ['ul', 'ol']:
                self._parse_list(element, doc, ordered=(element.name == 'ol'))

            # 表格
            elif element.name == 'table':
                self._parse_table(element, doc)

            # 水平线
            elif element.name == 'hr':
                doc.add_paragraph('─' * 50)

            # 引用
            elif element.name == 'blockquote':
                paragraph = doc.add_paragraph(element.get_text())
                paragraph.style = 'Quote'

            # div（递归处理）
            elif element.name == 'div':
                # 创建段落或递归处理子元素
                text = element.get_text(strip=True)
                if text:
                    doc.add_paragraph(text)

    def _apply_paragraph_style(self, html_element: Any, paragraph: Any):
        """应用段落样式"""
        style = html_element.get('style', '')

        # 解析样式
        if 'text-align: center' in style or 'text-align:center' in style:
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        elif 'text-align: right' in style or 'text-align:right' in style:
            paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT

        # 处理颜色等其他样式（简化处理）
        if 'color:' in style:
            # 提取颜色值（简化）
            pass

    def _parse_list(self, list_element: Any, doc: Document, ordered: bool = False):
        """解析列表元素"""
        for li in list_element.find_all('li', recursive=False):
            text = li.get_text(strip=True)
            if text:
                paragraph = doc.add_paragraph(text, style='List Bullet' if not ordered else 'List Number')

    def _parse_table(self, table_element: Any, doc: Document):
        """解析表格元素"""
        rows = table_element.find_all('tr')
        if not rows:
            return

        # 确定列数
        max_cols = max(len(row.find_all(['th', 'td'])) for row in rows)

        # 创建表格
        table = doc.add_table(rows=len(rows), cols=max_cols)
        table.style = 'Table Grid'

        # 填充表格
        for row_idx, tr in enumerate(rows):
            cells = tr.find_all(['th', 'td'])
            for col_idx, cell in enumerate(cells):
                if col_idx < max_cols:
                    table.cell(row_idx, col_idx).text = cell.get_text(strip=True)

                    # 表头加粗
                    if cell.name == 'th':
                        for paragraph in table.cell(row_idx, col_idx).paragraphs:
                            for run in paragraph.runs:
                                run.bold = True


# 工具函数
def convert_word_to_html(docx_path: str) -> str:
    """
    便捷函数：Word转HTML

    Args:
        docx_path: Word文档路径

    Returns:
        HTML字符串
    """
    converter = DocumentConverter()
    return converter.word_to_html(docx_path)


def convert_html_to_word(
    html_content: str,
    output_path: Optional[str] = None,
    **kwargs
) -> str:
    """
    便捷函数：HTML转Word

    Args:
        html_content: HTML内容
        output_path: 输出路径
        **kwargs: 其他参数

    Returns:
        生成的Word文档路径
    """
    converter = DocumentConverter()
    return converter.html_to_word(html_content, output_path, **kwargs)


if __name__ == '__main__':
    # 测试代码
    converter = DocumentConverter()

    # 测试Word转HTML
    test_docx = '/path/to/test.docx'
    if os.path.exists(test_docx):
        html = converter.word_to_html(test_docx)
        print(f"转换成功，HTML长度: {len(html)}")
        print(html[:500])

    # 测试HTML转Word
    test_html = """
    <h1>测试文档</h1>
    <h2>第一章</h2>
    <p>这是一段测试内容。</p>
    <table>
        <tr><th>列1</th><th>列2</th></tr>
        <tr><td>数据1</td><td>数据2</td></tr>
    </table>
    """
    output = converter.html_to_word(test_html, 'test_output.docx')
    print(f"HTML转Word成功: {output}")
