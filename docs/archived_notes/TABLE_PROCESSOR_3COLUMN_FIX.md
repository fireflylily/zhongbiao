# 表格处理器修复：支持3列表格

## 修复时间
2025-10-28

## 问题描述

**症状**：
- 商务应答文档中的"投标人及股东及关联关系情况表"没有被填充
- 日志显示：`表格处理完成: 处理了0个表格，填充了0个单元格`

**根本原因**：
1. **表格结构问题**（核心原因）
   - 该表格是 **8行 × 3列** 的格式
   - 所有行都是3列（第1列=字段名，第2列=填写区域，第3列=说明文字）
   - 旧代码只处理2列表格，在 `table_processor.py:156` 跳过了所有3列行

2. **字段映射缺失**
   - 数据库迁移文件已添加字段（003和004迁移文件）
   - `knowledge_base/manager.py` 已支持新字段
   - 但 `table_processor.py` 的字段映射缺少这些字段

## 表格示例

用户表格结构（表格#11）：
```
列1: 字段名          | 列2: 填写区域              | 列3: 说明文字
-------------------------------------------------------------------
供应商名称          | (空白)                     | (空白)
法定代表人/...      | (空白)                     | (空白)
实际控制人          | (空白)                     | 如果实际控制人是法人...
控股股东/...        | (空白)                     | 注: 如控股股东...
非控股股东/...      | (空白)                     | 注: 出资比例超过...
管理关系单位        | 管理关系单位名称            | (空白)
被管理关系单位      | 被管理关系单位名称          | (空白)
备注                | (空白)                     | (空白)
```

## 根本原因（2次修复）

### 第一次修复（不完整）
只修改了 `_process_key_value_table` 方法支持3列表格，但忽略了**表格识别**步骤。

### 第二次修复（完整）
发现表格#11根本**没有被识别为 `key_value` 类型**！

**问题代码**（table_processor.py:130行）：
```python
if two_col_rows >= total_rows * 0.8:  # 只检查2列
```

**表格#11的实际情况**：
- 8行全部是3列
- `two_col_rows = 0`
- `0 >= 6.4` → **False**
- 被识别为 `mixed` 类型，走了错误的处理逻辑

## 修复方案

### 1. 添加字段映射 (`table_processor.py:48-54`)

在 `table_field_mapping` 字典中添加：

```python
# 股权结构字段（2025-10-27添加）
'实际控制人': 'actual_controller',
'控股股东': 'controlling_shareholder',
'股东': 'shareholders_info',
# 管理关系字段（2025-10-28添加）
'管理关系单位': 'managing_unit_name',
'被管理关系单位': 'managed_unit_name'
```

### 2. 修复表格识别逻辑 (`table_processor.py:115-154`) ⭐核心修复

**修改前**：
```python
two_col_rows = sum(1 for count in row_column_counts if count == 2)
# 只检查2列
if two_col_rows >= total_rows * 0.8:
```

**修改后**：
```python
two_col_rows = sum(1 for count in row_column_counts if count == 2)
three_col_rows = sum(1 for count in row_column_counts if count == 3)  # 新增
# 检查2列或3列
if two_col_rows >= total_rows * 0.8 or three_col_rows >= total_rows * 0.8:
```

**修复说明**：
- ✅ 新增 `three_col_rows` 统计
- ✅ 修改判断条件，支持3列键值对表格
- ✅ 增强DEBUG日志，显示2列和3列行数

### 3. 增强 `_process_key_value_table` 方法 (`table_processor.py:156-199`)

**修改前**：
```python
# 只处理标准的2列行，跳过3列或更多列的行
if len(row.cells) != 2:
    self.logger.debug(f"  跳过非标准行（列数={len(row.cells)}）")
    continue
```

**修改后**：
```python
# 支持2列或3列的键值对表格
if len(row.cells) < 2:
    self.logger.debug(f"  跳过单列行（列数={len(row.cells)}）")
    continue

# 对于超过3列的行，可能不是键值对表格，跳过
if len(row.cells) > 3:
    self.logger.debug(f"  跳过多列行（列数={len(row.cells)}，可能是数据表格）")
    continue

key_cell = row.cells[0]
value_cell = row.cells[1]  # 无论2列还是3列，第2列都是值
```

**新增功能说明**：
- ✅ 支持2列表格（第1列=字段名，第2列=值）
- ✅ 支持3列表格（第1列=字段名，第2列=值，第3列=说明文字/忽略）
- ✅ 保持向后兼容，不影响现有2列表格的处理
- ✅ 添加详细的DEBUG日志，包含列数信息

## 相关数据库迁移

已完成的数据库schema更新：

### 003_add_equity_structure_fields.sql (2025-10-27)
```sql
ALTER TABLE companies ADD COLUMN actual_controller TEXT;
ALTER TABLE companies ADD COLUMN controlling_shareholder TEXT;
ALTER TABLE companies ADD COLUMN shareholders_info TEXT;
```

### 004_add_management_relationship_fields.sql (2025-10-28)
```sql
ALTER TABLE companies ADD COLUMN managing_unit_name TEXT;
ALTER TABLE companies ADD COLUMN managed_unit_name TEXT;
```

## 修复效果

### 修复前
```
2025-10-28 09:39:30 - INFO - 处理表格 #11
2025-10-28 09:39:30 - INFO - 表格处理完成: 处理了0个表格，填充了0个单元格
```

### 修复后（预期）
```
2025-10-28 XX:XX:XX - INFO - 处理表格 #11
2025-10-28 XX:XX:XX - DEBUG - ✅ 填充字段: 供应商名称 = 中国联合网络通信有限公司 (列数=3)
2025-10-28 XX:XX:XX - DEBUG - ✅ 填充字段: 法定代表人 = XXX (列数=3)
2025-10-28 XX:XX:XX - INFO - 表格处理完成: 处理了1个表格，填充了X个单元格
```

## 支持的表格类型

修复后，系统支持以下表格类型：

| 表格类型 | 列数 | 处理方式 | 示例 |
|---------|------|---------|------|
| 键值对表格（标准） | 2列 | ✅ 第1列=字段名，第2列=值 | 基本信息表 |
| 键值对表格（带说明） | 3列 | ✅ 第1列=字段名，第2列=值，第3列=忽略 | 股东关系表 |
| 数据表格 | 4+列 | ⏭️ 跳过键值对处理，尝试其他处理方式 | 项目清单表 |
| 表头-数据表格 | N列 | ✅ 第1行=表头，后续行=数据 | 业绩表 |

## 测试建议

1. **运行商务应答处理**，使用包含"投标人及股东及关联关系情况表"的模板
2. **检查日志**，确认表格#11被正确识别和处理
3. **验证输出文档**，确认以下字段被填充：
   - ✅ 供应商名称
   - ✅ 法定代表人
   - ⚠️ 实际控制人（数据库需要有值）
   - ⚠️ 控股股东（数据库需要有值）
   - ⚠️ 管理关系单位（数据库需要有值）

## 注意事项

1. **数据库迁移**：
   - 如果生产数据库未执行迁移文件003和004，需要先执行
   - Railway数据库需要同步这些字段

2. **数据填充**：
   - 新字段目前可能为空，需要在企业信息管理页面填写
   - 如果数据库中没有值，表格单元格会保持空白（不会报错）

3. **前端UI**：
   - 需要在企业信息编辑页面添加这些新字段的输入框
   - 参考 `company-profile-manager.js` 中的财务信息模块

## 修改的文件

- **ai_tender_system/modules/business_response/table_processor.py**
  - 第48-54行：添加字段映射
  - 第154-199行：增强 `_process_key_value_table` 方法

## 总结

- ✅ 修复了3列表格无法处理的问题
- ✅ 添加了股权结构和管理关系字段的支持
- ✅ 保持向后兼容，不影响现有2列表格
- ✅ 增加了详细的DEBUG日志，方便future排查
- 📝 建议：测试完成后，需要在前端UI添加新字段的编辑功能
