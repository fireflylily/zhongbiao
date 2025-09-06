#!/usr/bin/env python3
"""
修复采购编号处理的格式保持问题
优化精确跨run替换，确保更好地保持原有格式层次
"""

import os
import sys
from pathlib import Path
from docx import Document
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('fix_tender_format.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def analyze_original_tender_paragraph():
    """分析原始文档中采购编号段落的格式结构"""
    original_file = "/Users/lvhe/Library/Mobile Documents/com~apple~CloudDocs/Work/智慧足迹2025/05投标项目/AI标书/项目/1-中邮保险/中邮保险商务应答格式_测试.docx"
    
    logger.info("🔍 分析原始文档中的采购编号段落格式")
    logger.info("="*80)
    
    if not os.path.exists(original_file):
        logger.error(f"原始文件不存在: {original_file}")
        return None
    
    try:
        doc = Document(original_file)
        
        # 查找包含"采购编号"的段落
        for i, paragraph in enumerate(doc.paragraphs):
            if '采购编号' in paragraph.text and '根据贵方购采购货物' in paragraph.text:
                logger.info(f"📋 找到原始采购编号段落 #{i}:")
                logger.info(f"  文本: {paragraph.text}")
                logger.info(f"  Run数量: {len(paragraph.runs)}")
                
                # 详细分析每个run的格式
                format_map = {}
                for run_idx, run in enumerate(paragraph.runs):
                    if run.text:
                        format_key = (
                            bool(run.font.bold) if run.font.bold is not None else False,
                            bool(run.font.italic) if run.font.italic is not None else False,
                            bool(run.font.underline) if run.font.underline is not None else False
                        )
                        
                        if format_key not in format_map:
                            format_map[format_key] = []
                        format_map[format_key].append((run_idx, run.text))
                        
                        # 标记包含采购编号的run
                        marker = ""
                        if '采购编号' in run.text:
                            marker = " 🎯 包含'采购编号'"
                        elif '（' in run.text and len(run.text.strip()) <= 3:
                            marker = " 🔗 左括号"
                        elif '）' in run.text and len(run.text.strip()) <= 3:
                            marker = " 🔗 右括号"
                        
                        logger.info(f"    Run {run_idx+1}: '{run.text}'{marker}")
                        logger.info(f"        格式: 粗体={format_key[0]}, 斜体={format_key[1]}, 下划线={format_key[2]}")
                
                # 分析格式分布
                logger.info(f"\n  📊 格式分组:")
                for format_key, runs in format_map.items():
                    bold, italic, underline = format_key
                    logger.info(f"    格式(粗体={bold}, 斜体={italic}, 下划线={underline}): {len(runs)}个run")
                    for run_idx, text in runs:
                        logger.info(f"      Run {run_idx+1}: '{text}'")
                
                return {
                    'paragraph': paragraph,
                    'format_map': format_map,
                    'paragraph_index': i
                }
        
        logger.warning("未找到包含采购编号的段落")
        return None
        
    except Exception as e:
        logger.error(f"分析原始文档失败: {e}", exc_info=True)
        return None

def suggest_format_preservation_improvement():
    """建议格式保持的改进方案"""
    logger.info("\n" + "="*80)
    logger.info("💡 采购编号格式保持改进方案")
    logger.info("="*80)
    
    original_info = analyze_original_tender_paragraph()
    
    if original_info:
        format_map = original_info['format_map']
        
        logger.info("\n🎯 当前问题:")
        logger.info("1. 采购编号跨多个run，需要跨run处理")
        logger.info("2. 精确跨run替换将所有run合并为1个run")
        logger.info("3. 虽然技术上格式一致，但丢失了原有的格式层次")
        
        logger.info("\n🔧 改进方案:")
        logger.info("1. 增强精确跨run替换的格式智能性")
        logger.info("2. 在合并run时，保持更细粒度的格式区分")
        logger.info("3. 特别关注括号、关键词等的格式保持")
        
        # 如果原始文档有格式差异，提供具体建议
        if len(format_map) > 1:
            logger.info("\n📋 原始文档格式层次丰富，需要特殊处理:")
            for i, (format_key, runs) in enumerate(format_map.items()):
                bold, italic, underline = format_key
                logger.info(f"  格式组 {i+1}: 粗体={bold}, 斜体={italic}, 下划线={underline}")
                logger.info(f"    涉及 {len(runs)} 个run")
        else:
            logger.info("\n✅ 原始文档格式相对简单，当前处理方式基本合适")
    
    logger.info("\n🎯 建议的优化策略:")
    logger.info("1. 在_precise_cross_run_replace方法中增强格式保持逻辑")
    logger.info("2. 避免将所有内容合并到单一run，保持原有的格式边界")
    logger.info("3. 特别处理括号和关键词的格式")

def main():
    logger.info("🔧 采购编号格式保持问题修复分析")
    logger.info("="*80)
    
    suggest_format_preservation_improvement()
    
    logger.info("\n🎉 分析完成！基于分析结果来优化精确跨run替换逻辑")

if __name__ == "__main__":
    main()