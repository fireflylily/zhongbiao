# 文档结构解析 - 文件构成误识别修复

## 问题描述

招标文档中常见的"招标文件构成"部分（仅列出章节标题，无实际内容）被误识别为真实章节，导致：
- 所有章节显示0字
- 实际内容全部归入最后一个"附件"章节
- 用户无法正确筛选需要的章节

## 问题示例

```
第一部分 招标公告 (0字)          ← 误识别
第二部分 投标人须知 (0字)         ← 误识别  
第三部分 评标办法 (0字)          ← 误识别
...
第六部分 附件 (18134字)          ← 所有内容都在这里
```

## 根本原因

1. 文档结构：段落119-124只包含章节标题（"文件构成"），无内容
2. 真实章节从段落130+开始
3. 系统虽检测到智能起点104，但搜索时仍匹配到119-124的标题
4. 章节范围计算：每个章节的结束=下一章节的开始-1，导致连续标题=0内容

## 修复方案

### 1. 新增 `_is_file_composition_section()` 方法

```python
def _is_file_composition_section(self, doc, para_idx, toc_targets):
    """检测是否为文件构成部分（连续章节标题）"""
    check_range = 5
    consecutive_titles = 0
    
    for i in range(max(0, para_idx - check_range), 
                   min(len(doc.paragraphs), para_idx + check_range + 1)):
        para_text = doc.paragraphs[i].text.strip()
        is_chapter_title = bool(
            re.match(r'^第[一二三四五六七八九十\d]+部分', para_text) or
            re.match(r'^第[一二三四五六七八九十\d]+章', para_text)
        )
        if is_chapter_title:
            consecutive_titles += 1
    
    # 周围有3+个连续章节标题 = 文件构成
    return consecutive_titles >= 3
```

### 2. 修改章节匹配逻辑

在 `_parse_chapters_by_semantic_anchors()` 中：
- 找到匹配后，**立即检测**是否为文件构成
- 如果是，跳过该区域，向后10段重新搜索
- 找到新匹配后，再次验证不是文件构成

### 3. 关键改进点

**修复前**:
```python
if best_match_idx < min_search_start:  # ❌ 只检查位置
    if self._is_file_composition_section(...):
        ...
```

**修复后**:
```python
if self._is_file_composition_section(doc, best_match_idx, ...):  # ✅ 直接检测
    self.logger.warning("⚠ 跳过文件构成部分")
    # 向后10段重新搜索
    for para_idx in range(best_match_idx + 10, len(doc.paragraphs)):
        ...
        if score >= 0.70 and not self._is_file_composition_section(...):
            # 找到真实章节
            break
```

## 预期效果

修复后：
- ✅ 自动跳过"文件构成"部分
- ✅ 正确识别真实章节内容
- ✅ 每个章节都包含实际文字
- ✅ 日志显示"⚠ 跳过文件构成部分"

## 测试方法

1. 重新解析问题文档
2. 查看章节列表，确认无0字章节
3. 检查日志: `ai_tender_system/data/logs/structure_parser.log`
4. 验证跳过文件构成的警告信息

## 修改文件

- `ai_tender_system/modules/tender_processing/structure_parser.py`
  - 第1764-1802行: 新增 `_is_file_composition_section()` 方法
  - 第1893-1931行: 修改章节匹配逻辑，添加文件构成检测

## 影响范围

- 仅影响包含"文件构成"部分的招标文档
- 不影响正常结构的文档
- 向后兼容，无破坏性变更

