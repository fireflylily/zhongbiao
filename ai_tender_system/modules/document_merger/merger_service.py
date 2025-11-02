# ai_tender_system/modules/document_merger/merger_service.py

import os
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION

class DocumentMergerService:
    def __init__(self):
        pass

    def merge_documents(
        self, 
        business_doc_path: str, 
        p2p_doc_path: str, 
        tech_doc_path: str, 
        output_dir: str, 
        project_name: str,
        style_option: str = "business_style",
        progress_callback=None
    ) -> dict:
        """
        Merges three Word documents into one, applies formatting, generates TOC, and an index file.
        """
        if progress_callback:
            progress_callback("开始文件融合...")

        # 1. 创建主文档
        if style_option == "business_style":
            # 以商务应答文件为模板创建主文档
            main_document = Document(business_doc_path)
            # 清空除样式外的所有内容，以便重新填充
            for i in range(len(main_document.paragraphs) - 1, -1, -1):
                p = main_document.paragraphs[i]
                if p.text.strip(): # Only remove non-empty paragraphs
                    p._element.getparent().remove(p._element)
            for i in range(len(main_document.tables) - 1, -1, -1):
                main_document.tables[i]._element.getparent().remove(main_document.tables[i]._element)
            
            # Add a new paragraph to ensure the document is not empty after clearing
            main_document.add_paragraph()

        else: # standard_style
            main_document = Document()
            self._apply_standard_styles(main_document)

        # 2. 合并内容
        merged_content_paths = [
            ("商务应答文件", business_doc_path),
            ("点对点应答文件", p2p_doc_path),
            ("技术方案文件", tech_doc_path)
        ]

        for i, (doc_type, doc_path) in enumerate(merged_content_paths):
            if progress_callback:
                progress_callback(f"正在合并 {doc_type}...")
            self._append_document_content(main_document, doc_path, style_option, progress_callback)
            if i < len(merged_content_paths) - 1:
                # Add a section break between documents for better separation
                main_document.add_section(WD_SECTION.NEW_PAGE)

        # 3. 格式化 (如果选择标准样式，已在创建时应用；如果选择商务样式，则保持原样)
        if style_option == "standard_style":
            if progress_callback:
                progress_callback("正在应用标准格式...")
            # Additional formatting passes if needed, but primary styles are set at creation
            pass

        # 4. 生成目录
        if progress_callback:
            progress_callback("正在生成目录...")
        self._generate_toc(main_document)

        # 5. 生成索引文件 (简化版)
        if progress_callback:
            progress_callback("正在生成索引文件...")
        index_file_path = self._generate_index_file(main_document, output_dir, project_name)

        # 保存最终文档
        output_docx_name = f"{project_name}_最终标书.docx"
        output_docx_path = os.path.join(output_dir, output_docx_name)
        main_document.save(output_docx_path)

        if progress_callback:
            progress_callback("文件融合完成！")

        return {
            "merged_document_path": output_docx_path,
            "index_file_path": index_file_path
        }

    def _append_document_content(self, main_doc, source_doc_path, style_option, progress_callback=None):
        """
        Appends content from a source document to the main document.
        """
        source_doc = Document(source_doc_path)
        for element in source_doc.element.body:
            main_doc.element.body.append(element)

        # If standard style, re-apply styles after appending
        if style_option == "standard_style":
            self._apply_standard_styles_to_appended_content(main_doc, source_doc_path, progress_callback)

    def _apply_standard_styles(self, doc):
        """
        Applies standard styles to the document.
        """
        # Default paragraph style
        style = doc.styles['Normal']
        font = style.font
        font.name = '仿宋'
        font.size = Pt(14) # 四号
        paragraph_format = style.paragraph_format
        paragraph_format.line_spacing = 1.5

        # Heading 1 style
        style = doc.styles['Heading 1']
        font = style.font
        font.name = '仿宋'
        font.size = Pt(16) # 三号
        font.bold = True

        # Heading 2 style
        style = doc.styles['Heading 2']
        font = style.font
        font.name = '仿宋'
        font.size = Pt(16) # 三号
        font.bold = False # Ensure not bold if inherited

        # Heading 3 style
        style = doc.styles['Heading 3']
        font = style.font
        font.name = '仿宋'
        font.size = Pt(14) # 四号
        font.bold = True

    def _apply_standard_styles_to_appended_content(self, main_doc, source_doc_path, progress_callback=None):
        """
        Iterates through the newly appended content and applies standard styles.
        This is a simplified approach and might need more sophisticated logic
        to correctly identify heading levels from the appended content.
        """
        # This is a placeholder. A more robust solution would involve parsing
        # the source document's structure before appending or using more advanced
        # heuristics to determine heading levels in the main_doc after appending.
        # For now, we'll just ensure all paragraphs get the 'Normal' style
        # and rely on the user to manually adjust headings if needed.
        # Or, a more complex logic would be needed to infer heading levels.

        # A more advanced approach would involve iterating through the elements
        # of the source_doc and applying styles based on their original style or content.
        # For simplicity and initial implementation, we'll apply default styles.

        # Example of a very basic heuristic for headings (needs refinement):
        # Iterate through paragraphs, if a paragraph looks like a heading, apply heading style
        # This part is highly dependent on the structure of the input documents.
        # For now, we'll assume basic text and let the user refine headings.

        # For demonstration, let's just ensure all paragraphs have the 'Normal' style
        # and then try to identify some headings based on simple text patterns.
        # This is a very naive approach and will likely need significant improvement.
        
        # This part is tricky because docx.element.body.append(element) copies raw XML.
        # Re-applying styles correctly requires re-parsing or careful manipulation.
        # For a first pass, we'll focus on ensuring the base styles are there.

        # A more robust solution would involve iterating through the paragraphs
        # of the *main_doc* after appending and applying styles based on content heuristics.
        # For now, we'll leave this as a known limitation for the first iteration.
        pass # Placeholder for more sophisticated style application


    def _generate_toc(self, doc):
        """
        Inserts a TOC field into the document. User needs to update it manually in Word.
        """
        paragraph = doc.add_paragraph()
        run = paragraph.add_run()
        fldChar = run._element.new_child(qn('w:fldChar'))
        fldChar.set(qn('w:fldCharType'), 'begin')
        instrText = run._element.new_child(qn('w:instrText'))
        instrText.set(qn('xml:space'), 'preserve')
        instrText.text = 'TOC \o "1-3" \h \z \u'
        fldChar2 = run._element.new_child(qn('w:fldChar'))
        fldChar2.set(qn('w:fldCharType'), 'end')

        # Add a title for the TOC
        doc.add_heading('目录', level=1)
        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_paragraph('\n') # Add some space

    def _generate_index_file(self, doc, output_dir, project_name):
        """
        Generates a simplified keyword index file (TXT).
        This is a placeholder and needs actual keyword extraction logic.
        """
        index_content = ["关键词索引", "--------------------"]
        # Placeholder for actual keyword extraction and page/section mapping
        # For now, just a dummy entry
        index_content.append("- 示例关键词: 参见 [章节名称] (需要实现)")

        index_file_name = f"{project_name}_索引.txt"
        index_file_path = os.path.join(output_dir, index_file_name)
        with open(index_file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(index_content))
        return index_file_path

# Helper function for TOC (from python-docx examples)
from docx.oxml.ns import qn


