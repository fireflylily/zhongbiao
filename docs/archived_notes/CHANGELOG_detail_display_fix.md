# 详细要求显示完整性修复

## 问题描述

在"资格要求"tab页中,部分详细要求(如"财务要求")的`detail`字段显示不完整,以`...`结尾被截断。

**示例:**
```
单位除外)；供应商具有良好的商业信誉和健全的财务会计制度(供应商提供近1年的经第三方机构审计的财务审计报告(每份报告应至少包含1)审计报告正文,2)资产负债表,3)利润表或收入费用表(事业单位提供)...
```

## 根本原因

在`ai_tender_system/modules/tender_info/extractor.py`的`extract_qualification_requirements_by_keywords`方法中(line 350),`description`字段被硬编码限制为**最多100个字符**:

```python
description = description_parts[0][:100] + "..." if len(description_parts[0]) > 100 else description_parts[0]
```

这导致:
1. 提取时就被截断,存入数据库的数据不完整
2. 前端显示的是已截断的数据
3. 重要的资格要求信息丢失

## 解决方案

### 1. 后端修改

**文件:** `ai_tender_system/modules/tender_info/extractor.py` (line 347-351)

**修改前:**
```python
# 生成描述
description = f"需要提供{found_keywords[0]}"
if description_parts:
    description = description_parts[0][:100] + "..." if len(description_parts[0]) > 100 else description_parts[0]
```

**修改后:**
```python
# 生成描述(提高字符限制到500,保留更多上下文信息)
description = f"需要提供{found_keywords[0]}"
if description_parts:
    # 移除"..."后缀,因为前端会处理长文本显示
    description = description_parts[0][:500] if len(description_parts[0]) > 500 else description_parts[0]
```

**改进点:**
- 将字符限制从100提高到500
- 移除自动添加的`...`后缀
- 保留更完整的上下文信息

### 2. 前端修改

**文件:** `ai_tender_system/web/static/js/pages/tender-processing-step3-enhanced.js`

#### 2.1 新增辅助函数

在文件末尾添加了两个新函数(line 1104-1189):

```javascript
/**
 * 格式化detail文本,对于长文本添加展开/收起功能
 * @param {string} text - 要显示的文本
 * @param {number} maxLength - 默认显示的最大长度(默认150字符)
 * @returns {string} 格式化后的HTML
 */
function formatDetailTextWithToggle(text, maxLength = 150) {
    // 如果文本长度<=maxLength,直接返回
    // 否则生成"展开/收起"按钮的HTML
}

/**
 * 切换detail文本的展开/收起状态
 * @param {string} id - 元素ID前缀
 * @param {Event} event - 点击事件
 */
function toggleDetailText(id, event) {
    // 切换展开/收起状态
}
```

**功能特性:**
- 长文本(>150字符)默认只显示前150字符
- **智能截断算法**:按标点符号优先级截断
  - **最高优先级**: 句号（。）
  - **高优先级**: 分号（；;）、感叹号（！）、问号（？）
  - **中优先级**: 逗号（，,）
  - **低优先级**: 顿号（、）、右括号（）)）
  - 支持中英文标点符号
  - 在最后一个优先级最高的标点符号之后截断
  - 最少保留50%的内容(防止过早截断)
- 提供"展开/收起"链接切换显示
- 使用Bootstrap图标(<i class="bi bi-chevron-down"></i>)增强视觉效果
- HTML自动转义,防止XSS攻击

#### 2.2 修改显示逻辑

修改了两个函数中的detail显示:

**函数1:** `displayEligibilityChecklistFromAPI` (line 1049-1052)
**函数2:** `displayEligibilityChecklist` (line 979-982)

```javascript
// 使用新的格式化函数处理detail字段,支持展开/收起
const formattedDetail = req.summary && req.detail && req.detail !== req.summary
    ? `<div class="small text-secondary mt-1">${formatDetailTextWithToggle(req.detail, 150)}</div>`
    : '';

html += `
    <div class="fw-medium">${req.summary || formatDetailTextWithToggle(req.detail, 150)}</div>
    ${formattedDetail}
`;
```

## 使用效果

### 修复前
- 详细要求被截断为100字符
- 显示`...`但无法展开查看完整内容
- 信息丢失

### 修复后
- 后端保存最多500字符的上下文
- 前端默认显示150字符,超过部分显示"展开"链接
- 点击"展开"查看完整内容,点击"收起"折叠回去
- 短文本(<150字符)直接完整显示

### 界面示例

**长文本(默认状态):**
```
单位除外)；供应商具有良好的商业信誉和健全的财务会计制度(供应商提供近1年的经第三方机构审计的财务审计报告(每份报告应至少包含1)审计报告正文,2)资产负债表,3)利润表或收入... ▼ 展开
```

**长文本(展开后):**
```
单位除外)；供应商具有良好的商业信誉和健全的财务会计制度(供应商提供近1年的经第三方机构审计的财务审计报告(每份报告应至少包含1)审计报告正文,2)资产负债表,3)利润表或收入费用表(事业单位提供)4)现金流量表(事业单位免提供)5)所有者权益变动表(事业单位免提供)、6)财务报表附注等,上述6项完整内容齐全)(提供加盖公章的复印件);(事业单位提供加盖公章的财务报表复印件) ▲ 收起
```

**短文本:**
```
供应商须提供有效营业执照
```
(无展开/收起链接,直接完整显示)

## 重要提示

### 已存储数据的处理

**已存储的数据无法自动恢复**,因为数据库中的`detail`字段已被截断为100字符。

**解决方法:**
1. 找到原始招标文档
2. 在系统中重新执行"AI提取资格要求"
3. 新提取的数据将包含完整的detail字段(最多500字符)

### 测试方法

1. 打开测试页面验证功能:
   ```bash
   open test_detail_display.html
   ```

2. 在实际系统中测试:
   - 进入"标书智能处理 - HITL流程"
   - 选择章节并进入步骤3
   - 点击"AI提取资格要求"
   - 查看"资格要求"tab页
   - 验证长文本的展开/收起功能

## 修改文件清单

1. ✅ `ai_tender_system/modules/tender_info/extractor.py` (line 347-351)
2. ✅ `ai_tender_system/web/static/js/pages/tender-processing-step3-enhanced.js` (新增line 1104-1189, 修改line 979-982, 1049-1052)
3. ✅ `test_detail_display.html` (新增测试页面)

## 版本信息

- 修复日期: 2025-10-08
- 修复人员: Claude Code
- 影响版本: v1.0+
- 修复类型: Bug Fix + Enhancement
