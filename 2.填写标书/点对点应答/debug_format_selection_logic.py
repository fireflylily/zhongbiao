#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def debug_format_selection_logic():
    """调试格式选择逻辑"""
    
    # 模拟实际的文本区域
    before_text = "根据贵方为（项目名称）项目采购采购货物及服务的竞争性磋商公告（采购编号），签字代表（姓名、职务）经正式授权并代表供应商"
    replacement_text = "智慧足迹数据科技有限公司、北京市东城区王府井大街200号七层711室"
    after_text = "提交下述文件正本一份及副本       份："
    
    new_full_text = before_text + "（" + replacement_text + "）" + after_text
    
    # 计算区域边界
    before_end = len(before_text) + 1  # +1 for "（"
    replacement_start = before_end
    replacement_end = before_end + len(replacement_text)
    
    print(f"文本区域分析:")
    print(f"总长度: {len(new_full_text)}")
    print(f"前部分结束: {before_end}")
    print(f"替换部分: {replacement_start} - {replacement_end}")
    print(f"后部分开始: {replacement_end + 1}")  # +1 for "）"
    
    print(f"\n替换文本内容: '{replacement_text}'")
    print(f"替换文本长度: {len(replacement_text)}")
    
    # 模拟Run #18的情况
    print(f"\n=== Run #18 分析 ===")
    run18_text = "层711室）提交下述文件正本一份及副本       份："
    print(f"Run #18 文本: '{run18_text}'")
    print(f"Run #18 长度: {len(run18_text)}")
    
    # 计算Run #18在新文本中的位置
    run18_start = new_full_text.find("层711室）")
    run18_end = run18_start + len(run18_text)
    
    print(f"Run #18 位置: {run18_start} - {run18_end}")
    
    # 应用格式选择逻辑
    current_text_pos = run18_start
    text_end_pos = run18_end
    run_text_length = len(run18_text)
    
    # 计算重叠
    before_overlap = max(0, min(text_end_pos, before_end) - current_text_pos)
    replacement_overlap = max(0, min(text_end_pos, replacement_end) - max(current_text_pos, replacement_start))
    after_overlap = max(0, text_end_pos - max(current_text_pos, replacement_end + 1))  # +1 for "）"
    
    print(f"\n重叠分析:")
    print(f"与前部分重叠: {before_overlap}")
    print(f"与替换部分重叠: {replacement_overlap}")
    print(f"与后部分重叠: {after_overlap}")
    
    print(f"\n格式选择逻辑:")
    if replacement_overlap > before_overlap and replacement_overlap > after_overlap:
        print(f"❌ 主要在替换区域，应该使用斜体+下划线")
    elif before_overlap >= after_overlap:
        print(f"✅ 主要在前部分，使用原始格式")
    else:
        print(f"✅ 主要在后部分，使用原始格式")
    
    # 跨区域检查
    if replacement_overlap > 0 and (before_overlap > 0 or after_overlap > 0):
        replacement_ratio = replacement_overlap / run_text_length
        print(f"\n跨区域分析:")
        print(f"替换部分占比: {replacement_ratio:.2f}")
        if replacement_ratio > 0.3:
            print(f"❌ 占比超过30%，应该使用替换格式（斜体+下划线）")
        else:
            print(f"✅ 占比不足30%，使用原始格式")
    
    print(f"\n问题分析:")
    print(f"Run #18 包含 '层711室）' 这部分应该是替换文本的一部分")
    print(f"但我们的逻辑把它归类为后部分文本")
    print(f"需要调整边界计算，考虑右括号 '）'")

if __name__ == "__main__":
    debug_format_selection_logic()