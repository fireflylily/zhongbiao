#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查测试结果中的电子邮箱字段
"""

import logging
from docx import Document

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_email_fields():
    """检查测试结果中的电子邮箱字段"""
    
    result_file = "./test_result_20250908_122849.docx"
    
    try:
        doc = Document(result_file)
        logger.info(f"检查文件: {result_file}")
        
        email_paragraphs = []
        duplicate_issues = []
        
        for para_idx, paragraph in enumerate(doc.paragraphs):
            para_text = paragraph.text.strip()
            
            # 查找包含电子邮箱相关字段的段落
            if any(keyword in para_text for keyword in ['电子邮箱', '电子邮件', '邮箱']):
                email_paragraphs.append((para_idx, para_text))
                
                # 检查重复标签
                email_box_count = para_text.count('电子邮箱')
                email_count = para_text.count('电子邮件')
                mailbox_count = para_text.count('邮箱')
                
                if email_box_count > 1 or email_count > 1:
                    duplicate_issues.append({
                        'paragraph': para_idx,
                        'text': para_text,
                        'email_box_count': email_box_count,
                        'email_count': email_count,
                        'mailbox_count': mailbox_count
                    })
        
        logger.info(f"找到 {len(email_paragraphs)} 个包含邮箱字段的段落")
        
        for para_idx, para_text in email_paragraphs:
            logger.info(f"段落 #{para_idx}: '{para_text}'")
        
        if duplicate_issues:
            logger.error(f"发现 {len(duplicate_issues)} 个重复标签问题:")
            for issue in duplicate_issues:
                logger.error(f"  段落 #{issue['paragraph']}: {issue['text']}")
                logger.error(f"    电子邮箱:{issue['email_box_count']}次, 电子邮件:{issue['email_count']}次")
        else:
            logger.info("✓ 未发现电子邮箱重复标签问题")
            
        # 特别检查是否有用户报告的问题格式
        problem_patterns = [
            '电话13800138000电子邮箱  电子邮箱service@chinaunicom.cn',
            '电子邮箱  电子邮箱',
            '电子邮件  电子邮件'
        ]
        
        found_patterns = []
        for para_idx, para_text in email_paragraphs:
            for pattern in problem_patterns:
                if pattern in para_text:
                    found_patterns.append((para_idx, para_text, pattern))
        
        if found_patterns:
            logger.error("发现用户报告的问题格式:")
            for para_idx, para_text, pattern in found_patterns:
                logger.error(f"  段落 #{para_idx}: '{para_text}' (匹配: {pattern})")
        else:
            logger.info("✓ 未发现用户报告的问题格式")
            
    except Exception as e:
        logger.error(f"检查失败: {e}")

if __name__ == "__main__":
    check_email_fields()