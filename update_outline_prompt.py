#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""更新outline_generation.json提示词，禁止添加通用商务章节"""

import json
from pathlib import Path

# 读取JSON文件
json_path = Path("ai_tender_system/prompts/outline_generation.json")
with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# 获取当前的generate_outline提示词
prompt = data['prompts']['generate_outline']

# 查找并替换目标文本
old_text = """⚠️ 重要原则：动态生成章节，不使用固定模板
- 禁止使用固定的5章结构（总体设计、需求应答、技术指标、实施方案、服务承诺）
- 必须根据需求分析结果动态创建章节
- 1级章节标题 = requirement_categories[].category
- 2级章节标题 = requirement_categories[].key_points（去掉★、▲等标记）"""

new_text = """⚠️ 重要原则：动态生成章节，不使用固定模板
- 禁止使用固定的5章结构（总体设计、需求应答、技术指标、实施方案、服务承诺）
- ❌ 严禁添加需求分析中未提及的通用商务章节（如：服务期限、不可抗力、违约责任、知识产权、保密条款、争议解决、付款方式等）
- ❌ 严禁添加标准合同条款章节，技术方案只应答招标文件中的技术需求和功能需求
- ✅ 必须根据需求分析结果动态创建章节，一一对应
- ✅ 1级章节标题 = requirement_categories[].category（必须严格对应）
- ✅ 2级章节标题 = requirement_categories[].key_points（去掉★、▲等标记）
- ✅ 如果需求分析只有3个类别，就只生成3章；如果有8个类别，就生成8章
- ✅ 章节数量 = requirement_categories的数量，不多不少"""

if old_text in prompt:
    prompt = prompt.replace(old_text, new_text)
    data['prompts']['generate_outline'] = prompt

    # 更新版本号
    data['version'] = '2.2.0'
    data['updated_at'] = '2025-12-18'
    data['description'] = '技术方案应答大纲生成模块的提示词配置 - 支持动态需求分类和灵活章节结构，严禁添加通用商务条款'

    # 写回文件
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("✅ 提示词更新成功！")
    print(f"版本：{data['version']}")
    print(f"更新时间：{data['updated_at']}")
    print("\n新增禁止规则：")
    print("- 严禁添加通用商务章节（服务期限、不可抗力等）")
    print("- 严禁添加标准合同条款")
    print("- 必须严格按照需求分析结果生成章节")
else:
    print("❌ 未找到目标文本，无法更新")
