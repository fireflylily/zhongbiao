#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速修复JavaScript addEventListener错误
"""

import re

# 读取HTML文件
with open('../../web页面/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 修复所有不安全的addEventListener调用
patterns_to_fix = [
    r"document\.getElementById\('([^']+)'\)\.addEventListener\(",
    r'document\.getElementById\("([^"]+)"\)\.addEventListener\(',
]

def fix_addeventlistener(match):
    element_id = match.group(1)
    return f"""const {element_id}Element = document.getElementById('{element_id}');
        if ({element_id}Element) {{
            {element_id}Element.addEventListener("""

for pattern in patterns_to_fix:
    content = re.sub(pattern, fix_addeventlistener, content)

# 写入修复后的内容
with open('../../web页面/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ 已修复所有不安全的addEventListener调用")