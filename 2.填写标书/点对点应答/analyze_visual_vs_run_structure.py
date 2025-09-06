#!/usr/bin/env python3
"""
分析视觉效果与run结构的差异
探究为什么肉眼看不出区别，但run结构却不同
检查是否因为换行、格式标记等隐藏因素导致run分割
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
        logging.FileHandler('visual_vs_run_analysis.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def analyze_hidden_formatting_differences(file_path: str):
    """分析隐藏的格式差异，解释为什么看起来相同但run结构不同"""
    logger.info("=" * 80)
    logger.info(f"分析隐藏格式差异: {file_path}")
    logger.info("=" * 80)
    
    try:
        doc = Document(file_path)
        
        # 查找项目名称和采购编号段落
        project_para = None
        tender_para = None
        
        for i, paragraph in enumerate(doc.paragraphs):
            text = paragraph.text.strip()
            if '（项目名称）' in text:
                project_para = (i, paragraph)
            elif '（采购编号）' in text:
                tender_para = (i, paragraph)
        
        if project_para and tender_para:
            logger.info("\n🔍 详细对比项目名称vs采购编号的格式差异:")
            logger.info("=" * 60)
            
            # 分析项目名称段落
            logger.info(f"\n📋 项目名称段落 #{project_para[0]}:")
            analyze_paragraph_formatting(project_para[1], "项目名称")
            
            # 分析采购编号段落  
            logger.info(f"\n📋 采购编号段落 #{tender_para[0]}:")
            analyze_paragraph_formatting(tender_para[1], "采购编号")
            
            # 对比分析
            logger.info("\n" + "=" * 60)
            logger.info("🎯 深度对比分析:")
            logger.info("=" * 60)
            compare_paragraphs(project_para[1], tender_para[1])
            
    except Exception as e:
        logger.error(f"分析失败: {e}", exc_info=True)

def analyze_paragraph_formatting(paragraph, field_name):
    """详细分析段落的格式信息"""
    text = paragraph.text
    logger.info(f"完整文本: {text}")
    logger.info(f"文本长度: {len(text)} 字符")
    logger.info(f"Run数量: {len(paragraph.runs)}")
    
    # 检查段落级别属性
    alignment = paragraph.alignment
    line_spacing = paragraph.paragraph_format.line_spacing
    space_before = paragraph.paragraph_format.space_before
    space_after = paragraph.paragraph_format.space_after
    
    logger.info(f"段落属性: 对齐={alignment}, 行距={line_spacing}, 前距={space_before}, 后距={space_after}")
    
    # 详细分析每个run
    target_pattern = f"（{field_name}）"
    logger.info(f"\n  寻找目标文本: '{target_pattern}'")
    
    for j, run in enumerate(paragraph.runs):
        if not run.text:
            continue
            
        # 字符级别分析
        char_analysis = []
        for char in run.text:
            if char == '\n':
                char_analysis.append("\\n(换行)")
            elif char == '\r':
                char_analysis.append("\\r(回车)")
            elif char == '\t':
                char_analysis.append("\\t(制表符)")
            elif char == ' ':
                char_analysis.append("Space(空格)")
            elif ord(char) == 0x00A0:
                char_analysis.append("NBSP(不换行空格)")
            elif ord(char) == 0x3000:
                char_analysis.append("中文空格")
            else:
                char_analysis.append(char)
        
        # 格式属性
        font_name = run.font.name
        font_size = run.font.size
        bold = run.font.bold
        italic = run.font.italic
        underline = run.font.underline
        color = run.font.color.rgb if run.font.color.rgb else "默认"
        
        # 特殊标记
        highlight = ""
        if target_pattern in run.text:
            highlight = f" ⭐ 包含完整{field_name}!"
        elif field_name in run.text:
            highlight = f" ⚠️ 包含部分{field_name}"
        elif '（' in run.text and '）' not in run.text:
            highlight = " 🔍 只有左括号"
        elif '）' in run.text and '（' not in run.text:
            highlight = " 🔍 只有右括号"
            
        logger.info(f"    Run {j+1}: '{run.text}'")
        logger.info(f"        字符分析: {char_analysis}")
        logger.info(f"        格式: 字体={font_name}, 大小={font_size}, 粗体={bold}, 斜体={italic}, 下划线={underline}, 颜色={color}{highlight}")
        
        # 检查是否有特殊字符
        special_chars = []
        for i, char in enumerate(run.text):
            if ord(char) > 127 and char not in '（）项目名称采购编号':
                special_chars.append(f"位置{i}: '{char}'(U+{ord(char):04X})")
        if special_chars:
            logger.info(f"        特殊字符: {special_chars}")

def compare_paragraphs(project_para, tender_para):
    """对比两个段落的差异"""
    logger.info("对比项目名称vs采购编号段落:")
    
    # Run数量对比
    logger.info(f"Run数量: 项目名称={len(project_para.runs)}, 采购编号={len(tender_para.runs)}")
    
    # 查找目标run
    project_target_run = None
    tender_target_runs = []
    
    for i, run in enumerate(project_para.runs):
        if '（项目名称）' in run.text:
            project_target_run = (i, run)
            break
    
    for i, run in enumerate(tender_para.runs):
        if '（' in run.text or '采购' in run.text or '编号' in run.text or '）' in run.text:
            if any(char in run.text for char in ['（', '采购', '编号', '）']):
                tender_target_runs.append((i, run))
    
    logger.info(f"\n项目名称目标run: {'找到' if project_target_run else '未找到'}")
    if project_target_run:
        logger.info(f"  Run #{project_target_run[0]+1}: '{project_target_run[1].text}'")
        logger.info(f"  斜体: {project_target_run[1].font.italic}")
    
    logger.info(f"\n采购编号相关runs: {len(tender_target_runs)}个")
    for i, (run_idx, run) in enumerate(tender_target_runs):
        logger.info(f"  Run #{run_idx+1}: '{run.text}' (斜体: {run.font.italic})")
    
    # 推断原因
    logger.info(f"\n🎯 推断分析:")
    if project_target_run and len(tender_target_runs) > 1:
        logger.info("✅ 项目名称: 完整文本在单个run中，可能是一次性输入并设置格式")
        logger.info("⚠️ 采购编号: 文本跨多个run，可能的原因:")
        logger.info("   1. 分步输入: 先输入'（'，再输入'采购编号'，再输入'）'")
        logger.info("   2. 格式变化: 在输入过程中改变了格式设置")
        logger.info("   3. 复制粘贴: 从不同来源复制粘贴，保留了原有的run结构")
        logger.info("   4. Word自动格式: Word自动识别并应用了不同的格式")
        logger.info("   5. 编辑历史: 多次编辑导致run边界产生")
        
        # 检查是否有换行符或特殊字符
        has_linebreaks = any('\n' in run.text or '\r' in run.text for _, run in tender_target_runs)
        if has_linebreaks:
            logger.info("   ⚠️ 发现换行符! 这可能是导致run分割的主要原因")
        else:
            logger.info("   ℹ️ 未发现换行符，可能是格式设置导致的run分割")

if __name__ == "__main__":
    original_file = "/Users/lvhe/Library/Mobile Documents/com~apple~CloudDocs/Work/智慧足迹2025/05投标项目/AI标书/项目/1-中邮保险/中邮保险商务应答格式_测试.docx"
    
    if os.path.exists(original_file):
        analyze_hidden_formatting_differences(original_file)
    else:
        logger.error(f"文档不存在: {original_file}")