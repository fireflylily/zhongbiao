#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试字段处理问题
"""
import re
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_field_pattern_matching():
    """测试字段模式匹配"""
    
    # 模拟的文档内容
    test_cases = [
        "电话：_____________",  # 标准格式
        "电话:_____________",   # 英文冒号
        "电话                    电子邮件",  # 双字段表格
        "联系电话：010-63271000",  # 已填充
        "电话：010-63271000",    # 已填充，简单格式
    ]
    
    field_value = "010-63271000"
    field_name = "电话"
    
    # 测试模式
    pattern = rf'({field_name}[:：]\s*)([_\s]*)'
    
    logger.info("=== 字段模式匹配测试 ===")
    logger.info(f"目标值: {field_value}")
    logger.info(f"字段名: {field_name}")
    logger.info(f"正则模式: {pattern}")
    
    for i, text in enumerate(test_cases):
        logger.info(f"\n--- 测试案例 {i+1}: '{text}' ---")
        
        match = re.search(pattern, text)
        if match:
            logger.info(f"✅ 匹配成功:")
            logger.info(f"  - 完整匹配: '{match.group(0)}'")
            logger.info(f"  - 捕获组1: '{match.group(1)}'")
            logger.info(f"  - 捕获组2: '{match.group(2)}'")
            
            # 执行替换
            new_text = re.sub(pattern, rf'\1{field_value}', text)
            logger.info(f"  - 替换结果: '{text}' -> '{new_text}'")
            
            # 检查是否有异常字符
            if 'A0' in new_text or '1' in new_text[:3]:
                logger.error(f"❌ 发现异常字符! 可能的问题在正则替换中")
        else:
            logger.info("❌ 模式不匹配")
    
    # 测试双字段表格处理
    logger.info(f"\n=== 双字段表格处理测试 ===")
    table_text = "电话                    电子邮件"
    logger.info(f"测试文本: '{table_text}'")
    
    # 双字段模式
    dual_pattern = r'(电话|联系电话)(\s{8,})(电子邮件|电子邮箱|邮箱)'
    match = re.search(dual_pattern, table_text)
    if match:
        logger.info(f"✅ 双字段匹配成功:")
        logger.info(f"  - 电话字段: '{match.group(1)}'")
        logger.info(f"  - 空格区域: '{match.group(2)}' (长度: {len(match.group(2))})")
        logger.info(f"  - 邮件字段: '{match.group(3)}'")
        
        # 模拟处理
        phone_text = f"{match.group(1)}：{field_value}"
        email_text = f"{match.group(3)}：lvhe@smartsteps.com"
        optimal_spaces = max(20, len(match.group(2)) - (len(phone_text) - len(match.group(1))))
        space_str = ' ' * optimal_spaces
        result = f"{phone_text}{space_str}{email_text}"
        
        logger.info(f"  - 处理结果: '{result}'")
    else:
        logger.info("❌ 双字段模式不匹配")

def test_run_level_processing():
    """测试Run级别的文本处理"""
    logger.info(f"\n=== Run级别处理模拟 ===")
    
    # 模拟有问题的Run文本
    problematic_runs = [
        "010-63271000",  # 纯数字
        "电话：010-63271000",  # 完整格式
        "电话：",  # 只有标签
        "010",  # 部分数字
        "_____________",  # 占位符
    ]
    
    field_value = "010-63271000"
    field_name = "电话"
    pattern = rf'({field_name}[:：]\s*)([_\s]*)'
    
    for run_text in problematic_runs:
        logger.info(f"\n处理Run文本: '{run_text}'")
        
        # 检查是否包含字段名和冒号
        has_field_and_colon = field_name in run_text and (':' in run_text or '：' in run_text)
        logger.info(f"  - 包含字段名和冒号: {has_field_and_colon}")
        
        if has_field_and_colon:
            old_text = run_text
            new_text = re.sub(pattern, rf'\1{field_value}', run_text)
            logger.info(f"  - 替换: '{old_text}' -> '{new_text}'")
            
            if new_text != old_text:
                logger.info(f"  - ✅ 替换成功")
            else:
                logger.info(f"  - ⚠️  替换后无变化")

if __name__ == "__main__":
    test_field_pattern_matching()
    test_run_level_processing()