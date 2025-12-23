# Heading 1样式保护修复

## 问题概述

用户报告："word大纲识别法，为什么没有识别出 第三部分 评标办法来？"

经过详细调查发现：
1. 段落259 "评标办法" **确实被识别了**（通过Heading 1样式）
2. 但被智能层级分析器从Level 1错误修正为Level 3
3. 导致它成为"第二部分 → 六、保密"的子章节，而不是独立的根章节

## 根本原因

### 文档结构

```
段落29:  '第三部分 评标办法\t22'       # 目录项（Normal样式，不会被识别）
段落121: '第三部分 评标办法\t'         # 目录列表（Normal样式，不会被识别）
段落259: '评标办法'                   # 真正的标题（Heading 1样式）✓
```

**关键点**：段落259的文本是 `'评标办法'`，**没有**"第三部分"前缀。

### 处理流程问题

| 阶段 | Level | 位置 | 说明 |
|------|-------|------|------|
| 1. 识别阶段 | 1 | - | 通过Heading 1样式正确识别 ✓ |
| 2. 智能层级分析 | **3** | - | 被误判为三级标题 ✗ |
| 3. 树形构建 | 3 | 第2层 | 成为"六、保密"的子章节 ✗ |
| 4. 最终结果 | 3 | 第2层 | 用户看不到独立的"评标办法"章节 ✗ |

## 修复方案

### 方案A：保护Heading样式的原始Level（已实施）

**原理**：如果段落使用了明确的Heading 1样式，应该尊重Word的样式定义，不要轻易修改其层级。

**修改内容**：

#### 1. 在ChapterNode中添加字段

```python
@dataclass
class ChapterNode:
    # ... existing fields ...
    detection_method: str = None  # 检测方法（如"样式Heading 1"）
    original_level: int = None   # 原始检测到的层级
```

#### 2. 记录检测方法和原始层级

在 `_parse_chapters_by_outline_level` 方法中：

```python
chapter = ChapterNode(
    # ... existing params ...
    detection_method=detection_method,  # 记录检测方法
    original_level=level if level > 0 else 1  # 记录原始层级
)
```

#### 3. 在智能层级分析中保护Heading 1样式

在 `parse_by_outline_level` 方法中：

```python
# 更新章节层级（但保护Heading样式检测的章节）
protected_count = 0
for i, level in enumerate(corrected_levels):
    ch = chapters[i]

    # 🆕 方案A：如果章节是通过Heading 1样式检测的，保持原始Level 1
    if ch.detection_method and 'Heading 1' in ch.detection_method:
        if ch.level != 1:  # 如果被修正了
            self.logger.info(
                f"🛡️ 保护Heading 1样式: '{ch.title}' 保持Level 1 "
                f"(智能分析建议Level {level})"
            )
            protected_count += 1
        # 强制保持Level 1
        ch.level = 1
    else:
        # 普通章节接受智能分析的修正
        ch.level = level

if protected_count > 0:
    self.logger.info(f"✅ 保护了 {protected_count} 个Heading 1样式的章节")
```

## 修复效果

### 修复前

```
第二部分 投标人须知前附表及投标人须知 (Level 1)
  └─ 六、保密 (Level 2)
      └─ 评标办法 (Level 3) ← 错误位置
```

根章节列表：
```
1. 第一部分 招标公告
2. 第二部分 投标人须知前附表及投标人须知
4. 第四部分 合同主要条款及格式  ← 跳过了"第三部分"
5. 第五部分 采购需求书
6. 第六部分 附件
```

### 修复后

```
评标办法 (Level 1) ← 正确成为根节点
```

根章节列表：
```
1. 第一部分 招标公告
2. 第二部分 投标人须知前附表及投标人须知
3. 评标办法                      ← 正确出现
4. 第四部分 合同主要条款及格式
5. 第五部分 采购需求书
6. 第六部分 附件
```

测试结果：
```
✅ 找到段落259！
   深度: 第0层           ← 根节点
   路径: 评标办法
   Level: 1             ← 保持Level 1
   跳过推荐: False       ← 不再被跳过
   自动选中: True
```

## 影响范围

### 受益的场景

1. **使用Heading样式的标准文档**
   - Word文档中明确使用Heading 1、Heading 2等样式
   - 现在会严格尊重这些样式定义

2. **标题文本较短的章节**
   - 如"评标办法"、"附件"、"说明"等短标题
   - 之前可能被误判为子章节
   - 现在只要是Heading 1就保持为一级标题

3. **缺少编号前缀的章节**
   - 如缺少"第X部分"前缀的章节
   - 之前依赖智能分析可能误判
   - 现在依赖明确的Word样式

### 不受影响的场景

1. **使用大纲级别标记的文档**
   - 继续使用Microsoft官方的 `<w:outlineLvl>` API
   - 优先级高于样式检测

2. **未使用Heading样式的文档**
   - 依然使用智能层级分析
   - 不受此修复影响

## 代码变更摘要

### 修改文件

- `ai_tender_system/modules/tender_processing/structure_parser.py`

### 新增字段

- `ChapterNode.detection_method`: 记录检测方法
- `ChapterNode.original_level`: 记录原始层级

### 核心逻辑

在智能层级分析阶段，对于通过"样式Heading 1"检测的章节，强制保持Level 1，不接受智能分析的修正。

### 日志输出

新增日志：
```
🛡️ 保护Heading 1样式: '评标办法' 保持Level 1 (智能分析建议Level 3)
✅ 保护了 1 个Heading 1样式的章节
```

## 测试验证

### 测试文档

- 文件：`ai_tender_system/data/parser_debug/acba754e-c1c5-40b0-a002-5ac7573f3866.docx`（哈银消金招标文件）
- 关键段落：段落259 "评标办法"（Heading 1样式）

### 测试结果

✅ **所有测试通过**

1. 段落259正确识别为Level 1
2. 段落259成为根章节（第0层）
3. 段落259不被标记为"跳过推荐"
4. 根章节列表完整，包含6个根节点

## 潜在改进

### 后续可考虑

1. **扩展到Heading 2、Heading 3**
   - 目前只保护Heading 1
   - 可以扩展到保护所有Heading样式

2. **提供配置选项**
   - 允许用户选择是否启用样式保护
   - 某些文档可能需要完全依赖智能分析

3. **改进智能层级分析算法**
   - 让算法更好地识别一级标题特征
   - 减少对Heading样式的依赖

## 相关文档

- `PARAGRAPH_259_ANALYSIS.md`: 详细调查报告
- `test_tree_building.py`: 测试脚本
- `tree_building_debug.log`: 调试日志

## 提交说明

修复了Word大纲识别法中智能层级分析器错误修正Heading 1样式章节层级的问题。

**症状**：使用Heading 1样式的章节（如"评标办法"）被错误地修正为Level 3，成为其他章节的子章节。

**修复**：在智能层级分析阶段，保护所有通过"样式Heading 1"检测的章节，强制保持Level 1。

**影响**：提高了对标准Word文档样式的尊重度，确保Heading 1样式的章节始终作为一级标题。
