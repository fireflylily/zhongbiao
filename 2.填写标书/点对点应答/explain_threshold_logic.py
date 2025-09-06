#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def explain_threshold_logic():
    """解释阈值逻辑的工作原理"""
    
    print("=== 阈值调整解释 ===\n")
    
    # 模拟Run #18的情况
    run_text = "层711室）提交下述文件正本一份及副本       份："
    total_length = len(run_text)
    
    # 替换部分：'层711室）' (5个字符)
    replacement_part = "层711室）"
    replacement_overlap = len(replacement_part)
    
    # 计算占比
    replacement_ratio = replacement_overlap / total_length
    
    print(f"Run #18 文本分析：")
    print(f"完整文本: '{run_text}'")
    print(f"总长度: {total_length} 个字符")
    print(f"替换部分: '{replacement_part}' ({replacement_overlap} 个字符)")
    print(f"占比: {replacement_overlap}/{total_length} = {replacement_ratio:.2%}")
    
    print(f"\n=== 格式选择逻辑对比 ===")
    
    # 原来的30%阈值
    old_threshold = 0.30
    print(f"\n🔴 原来的阈值 (30%):")
    print(f"判断条件: {replacement_ratio:.2%} > {old_threshold:.0%} ?")
    if replacement_ratio > old_threshold:
        print(f"结果: True → 使用替换格式（斜体+下划线）✅")
    else:
        print(f"结果: False → 使用原始格式（正常）❌")
        print(f"问题: '室）' 这两个字没有下划线！")
    
    # 新的15%阈值
    new_threshold = 0.15
    print(f"\n🟢 调整后的阈值 (15%):")
    print(f"判断条件: {replacement_ratio:.2%} > {new_threshold:.0%} ?")
    if replacement_ratio > new_threshold:
        print(f"结果: True → 使用替换格式（斜体+下划线）✅")
        print(f"效果: 整个run都有统一格式！")
    else:
        print(f"结果: False → 使用原始格式（正常）❌")
    
    print(f"\n=== 阈值选择的考虑因素 ===")
    print(f"✅ 15% 阈值的优点:")
    print(f"   - 更敏感：即使少量替换文本也能被识别")
    print(f"   - 格式一致性更好")
    print(f"   - 减少格式断层问题")
    
    print(f"\n⚠️ 过低阈值的风险:")
    print(f"   - 如果设为5%，可能会过度应用替换格式")
    print(f"   - 需要在准确性和一致性之间平衡")
    
    print(f"\n📊 各种阈值的效果对比:")
    for threshold in [0.05, 0.10, 0.15, 0.20, 0.30, 0.50]:
        result = "使用替换格式" if replacement_ratio > threshold else "使用原始格式"
        status = "✅" if (replacement_ratio > threshold) else "❌"
        print(f"   {threshold:.0%} 阈值: {result} {status}")

if __name__ == "__main__":
    explain_threshold_logic()