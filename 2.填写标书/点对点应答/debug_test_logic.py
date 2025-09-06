#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试测试逻辑
"""

# 模拟处理后的文本
text = "根据贵方为（项目名称）项目采购采购货物及服务的竞争性磋商代表（姓名、职务）经正式授权并代表供应商（智慧足迹数据科技有限公司、北京市东城区王府井大街200号七层711室）提交下述文件正本一份及副本       份："

company_name = "智慧足迹数据科技有限公司"

print(f"原始文本: {text}")
print(f"公司名称: {company_name}")
print()

# 检查1: 部分替换错误
check1 = "供应商（智慧足迹数据科技有限提交" in text or "供应商（智慧足迹数据科技有限" in text
print(f"检查1 - 部分替换错误: {check1}")

# 检查2: 正确完整替换
check2a = company_name in text
check2b = "供应商名称、地址" not in text  
check2c = "北京市东城区王府井大街200号七层711室" in text
check2 = check2a and check2b and check2c
print(f"检查2 - 正确完整替换: {check2}")
print(f"  - 包含公司名称: {check2a}")
print(f"  - 不包含原占位符: {check2b}")
print(f"  - 包含地址: {check2c}")

# 检查3: 内容分散但正确
check3a = "智慧足迹数据科技有限公司" in text
check3b = "北京市东城区王府井大街200号七层711室" in text
check3c = "供应商名称、地址" not in text
check3 = check3a and check3b and check3c
print(f"检查3 - 内容分散但正确: {check3}")
print(f"  - 包含完整公司名称: {check3a}")
print(f"  - 包含完整地址: {check3b}")
print(f"  - 不包含原占位符: {check3c}")

print()
if not check1 and (check2 or check3):
    print("✅ 测试应该通过！")
else:
    print("❌ 测试会失败")
    print(f"  check1={check1}, check2={check2}, check3={check3}")