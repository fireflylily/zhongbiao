#!/usr/bin/env python3
"""
分析处理前文档的run结构
专门查看项目名称区域和采购编号区域的run分布
验证我们对格式差异的分析结论
"""

import os
import sys
from pathlib import Path
from docx import Document
import logging
import re

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('original_document_runs_analysis.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def analyze_original_document_runs(file_path: str):
    """详细分析原始文档中项目名称和采购编号区域的run结构"""
    logger.info("=" * 80)
    logger.info(f"分析原始文档run结构: {file_path}")
    logger.info("=" * 80)
    
    try:
        doc = Document(file_path)
        project_name_paragraphs = []
        tender_no_paragraphs = []
        
        # 查找包含项目名称和采购编号的段落
        for i, paragraph in enumerate(doc.paragraphs):
            text = paragraph.text.strip()
            if not text:
                continue
                
            # 查找项目名称相关段落
            if '（项目名称）' in text or '项目名称' in text:
                project_name_paragraphs.append((i, paragraph, text))
                
            # 查找采购编号相关段落  
            if '（采购编号）' in text or '采购编号' in text:
                tender_no_paragraphs.append((i, paragraph, text))
        
        # 详细分析项目名称区域
        logger.info("\n🎯 项目名称区域Run结构分析:")
        logger.info("=" * 50)
        for para_idx, paragraph, text in project_name_paragraphs:
            logger.info(f"\n段落 #{para_idx}: {text[:100]}...")
            logger.info(f"完整文本: {text}")
            logger.info(f"Run数量: {len(paragraph.runs)}")
            
            # 检查哪个run包含"（项目名称）"
            contains_project_name = False
            for j, run in enumerate(paragraph.runs):
                if run.text:
                    font_info = f"字体={run.font.name}, 大小={run.font.size}, 粗体={run.font.bold}, 斜体={run.font.italic}"
                    highlight = ""
                    if '（项目名称）' in run.text:
                        highlight = " ⭐ 包含完整项目名称!"
                        contains_project_name = True
                    elif '项目名称' in run.text:
                        highlight = " ⚠️ 包含部分项目名称"
                    logger.info(f"    Run {j+1}: '{run.text}' [{font_info}]{highlight}")
                    
            if contains_project_name:
                logger.info("✅ 项目名称在单个run中 → 可以成功使用单run替换")
            else:
                logger.info("⚠️ 项目名称跨多个run → 需要使用跨run处理")
        
        # 详细分析采购编号区域
        logger.info("\n🎯 采购编号区域Run结构分析:")
        logger.info("=" * 50)
        for para_idx, paragraph, text in tender_no_paragraphs:
            logger.info(f"\n段落 #{para_idx}: {text[:100]}...")
            logger.info(f"完整文本: {text}")
            logger.info(f"Run数量: {len(paragraph.runs)}")
            
            # 检查哪个run包含"（采购编号）"
            contains_tender_no = False
            for j, run in enumerate(paragraph.runs):
                if run.text:
                    font_info = f"字体={run.font.name}, 大小={run.font.size}, 粗体={run.font.bold}, 斜体={run.font.italic}"
                    highlight = ""
                    if '（采购编号）' in run.text:
                        highlight = " ⭐ 包含完整采购编号!"
                        contains_tender_no = True
                    elif '采购编号' in run.text:
                        highlight = " ⚠️ 包含部分采购编号"
                    elif '（' in run.text and '采购编号' not in run.text:
                        highlight = " 🔍 包含左括号"
                    elif '）' in run.text and '采购编号' not in run.text:
                        highlight = " 🔍 包含右括号"
                    logger.info(f"    Run {j+1}: '{run.text}' [{font_info}]{highlight}")
                    
            if contains_tender_no:
                logger.info("✅ 采购编号在单个run中 → 可以成功使用单run替换")
            else:
                logger.info("⚠️ 采购编号跨多个run → 需要使用跨run处理")
        
        # 总结分析
        logger.info("\n" + "=" * 80)
        logger.info("🔍 Run结构分析总结:")
        logger.info("=" * 80)
        
        project_single_run = any(
            any('（项目名称）' in run.text for run in para[1].runs) 
            for para in project_name_paragraphs
        )
        
        tender_single_run = any(
            any('（采购编号）' in run.text for run in para[1].runs) 
            for para in tender_no_paragraphs
        )
        
        logger.info(f"项目名称在单run中: {'✅ 是' if project_single_run else '❌ 否'}")
        logger.info(f"采购编号在单run中: {'✅ 是' if tender_single_run else '❌ 否'}")
        
        if project_single_run and not tender_single_run:
            logger.info("\n🎯 结论验证:")
            logger.info("✅ 项目名称可以单run替换，不影响格式")  
            logger.info("⚠️ 采购编号必须跨run处理，可能影响格式")
            logger.info("🔍 这解释了为什么项目名称处理完美，而采购编号影响了周围文字格式!")
        elif not project_single_run and not tender_single_run:
            logger.info("\n🎯 结论:")
            logger.info("⚠️ 两者都需要跨run处理，但项目名称可能有其他优势")
        else:
            logger.info("\n🎯 结论:")
            logger.info("需要进一步分析具体处理差异")
            
    except Exception as e:
        logger.error(f"分析文档失败: {e}", exc_info=True)

def compare_with_processed_document():
    """对比处理前后的文档结构变化"""
    logger.info("\n" + "=" * 80)
    logger.info("对比处理前后的文档结构变化")
    logger.info("=" * 80)
    
    original_file = "/Users/lvhe/Library/Mobile Documents/com~apple~CloudDocs/Work/智慧足迹2025/05投标项目/AI标书/项目/1-中邮保险/中邮保险商务应答格式_测试.docx"
    processed_file = "/Users/lvhe/Library/Mobile Documents/com~apple~CloudDocs/Work/智慧足迹2025/05投标项目/AI标书/程序/2.填写标书/点对点应答/outputs/docx-商务应答-20250906_101512.docx"
    
    logger.info("处理前后对比分析将帮助我们理解:")
    logger.info("1. 项目名称为什么能保持格式不变")
    logger.info("2. 采购编号为什么影响了周围文字格式")
    logger.info("3. 验证我们的run结构分析是否正确")

if __name__ == "__main__":
    original_file = "/Users/lvhe/Library/Mobile Documents/com~apple~CloudDocs/Work/智慧足迹2025/05投标项目/AI标书/项目/1-中邮保险/中邮保险商务应答格式_测试.docx"
    
    if os.path.exists(original_file):
        analyze_original_document_runs(original_file)
        compare_with_processed_document()
    else:
        logger.error(f"原始文档不存在: {original_file}")
        logger.info("请确认文件路径是否正确")