#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析段落#30处理过程中run结构的变化
基于日志分析采购编号处理对run结构的影响
"""

print("段落#30 Run结构变化分析")
print("=" * 60)

print("\n阶段1: 初始状态")
print("段落文本: '供应商名称：                          采购编号：                   '")
print("推测的初始run结构:")
print("  可能的run结构 (基于日志推测):")
print("  - Run 0: '供应商'")
print("  - Run 1: '名称：'") 
print("  - Run 2: '                          '  # 长空格")
print("  - Run 3: '采购'")
print("  - Run 4: '编号：'")
print("  - Run 5: '                   '  # 空格占位符")

print("\n阶段2: 采购编号处理")
print("匹配到规则: 所有编号类统一填写规则")
print("调用方法: 智能替换 (第二层替换)")
print("替换目标: '采购编号： ' -> '采购编号：GXTC-C-251590031'")
print("受影响的run: [6, 7, 8] (日志显示)")

print("\n从日志分析:")
print("- 第二层替换开始: '采购编号： ' -> '采购编号：GXTC-C-251590031'")
print("- 为run 6应用目标格式，内容='采购编号：GXTC-C-251590031'")
print("- Run 6: '采购编号：GXTC-C-251590031'")
print("- Run 7: ''")
print("- Run 8: '      '")

print("\n阶段3: 全局占位符清理后")
print("清理前: '供应商名称：                          采购编号：GXTC-C-251590031                  '")
print("清理后: '供应商名称：   采购编号：GXTC-C-251590031  '")
print("说明: 全局占位符清理删除了中间的长空格")

print("\n处理后的推测run结构:")
print("  - Run 0: '供应商'")
print("  - Run 1: '名称：'")
print("  - Run 2: '   '  # 剩余空格")
print("  - Run 3: [空] or 其他")
print("  - Run 6: '采购编号：GXTC-C-251590031'")
print("  - Run 7: [空]")
print("  - Run 8: '  '")

print("\n阶段4: 供应商名称处理")
print("匹配到规则: 通用投标供应商名称填空 - 支持部分匹配")
print("调用: _handle_cross_run_text (尝试跨run处理分散的文本)")
print("问题: 找到'供应商'在run0，将公司名称插入其中")
print("结果: Run 0变成: '供应商： 中国联合网络通信有限公司'")
print("Run 1仍然是: '名称：'")

print("\n最终错误结果:")
print("'供应商： 中国联合网络通信有限公司名称：采购编号：GXTC-C-251590031'")

print("\n" + "=" * 60)
print("问题根本原因分析:")
print("1. 采购编号处理使用了'智能替换(第二层替换)'，修改了run结构")
print("2. 全局占位符清理进一步改变了run结构")
print("3. 供应商名称处理时，'供应商名称'已经被分散到不同的runs中")
print("4. _handle_cross_run_text方法找到'供应商'run，错误地在中间插入公司名称")
print("5. 导致'供应商名称'被拆分为'供应商 [公司名] 名称'")

print("\n解决方案:")
print("需要修复_handle_cross_run_text方法，正确识别和重构跨run的完整标签")