#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复JavaScript语法错误的脚本
"""

import re

# 读取HTML文件
with open('../../web页面/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 删除所有API相关的JavaScript代码
# 1. 删除API相关的事件监听器
api_patterns = [
    r'saveApiBtn\.addEventListener\([^}]*\}\);',
    r'loadApiBtn\.addEventListener\([^}]*\}\);',
    r'toggleApiBtn\.addEventListener\([^}]*\}\);',
    r'document\.getElementById\(["\']manageApiBtn["\']\)\.addEventListener\([^}]*\}\);',
    r'document\.getElementById\(["\']backupCurrentBtn["\']\)\.addEventListener\([^}]*\}\);',
    r'document\.getElementById\(["\']testApiBtn["\']\)\.addEventListener\([^}]*\}\);',
]

for pattern in api_patterns:
    content = re.sub(pattern, '// API功能已移除', content, flags=re.DOTALL)

# 2. 删除API相关的函数定义
function_patterns = [
    r'function loadBackupList\(\)[^}]*\}',
    r'function restoreApiKey\([^}]*\}',
    r'function encryptApiKey\([^}]*\}',
    r'function decryptApiKey\([^}]*\}',
]

for pattern in function_patterns:
    content = re.sub(pattern, '// API函数已移除', content, flags=re.DOTALL)

# 3. 确保companySelect相关的代码正常工作
# 检查loadCompanyList函数是否存在并且完整
if 'function loadCompanyList()' in content and 'updateCompanySelect(data.companies)' in content:
    print("✅ loadCompanyList函数完整")
else:
    print("❌ loadCompanyList函数有问题")

# 写入修复后的文件
with open('../../web页面/index_fixed.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("修复完成，生成文件: index_fixed.html")