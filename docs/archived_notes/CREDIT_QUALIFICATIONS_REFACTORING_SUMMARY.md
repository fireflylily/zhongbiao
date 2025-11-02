# 信用资质重构总结

## 概述

将原有的3个混合信用资质拆分为4个独立资质，以更准确地匹配招标文件中的资格要求。

## 背景

原有系统将信用相关资质合并为3个类别：
- `credit_china_check` - 信用中国查询
- `tax_violation_check` - 税收违法检查
- `gov_procurement_check` - 政府采购检查

但实际招标文件中要求的是4个独立的查询截图：
1. 失信被执行人名单查询（信用中国）
2. 重大税收违法案件当事人名单查询（信用中国）
3. 政府采购严重违法失信查询（信用中国）
4. 政府采购严重违法失信行为信息记录查询（中国政府采购网）

## 新资质结构

### 资质定义

| 资质Key | 资质名称 | 查询网站 | 优先级 |
|---------|----------|----------|--------|
| `dishonest_executor` | 失信被执行人名单（信用中国） | www.creditchina.gov.cn | high |
| `tax_violation_check` | 重大税收违法案件当事人名单（信用中国） | www.creditchina.gov.cn | high |
| `gov_procurement_creditchina` | 政府采购严重违法失信（信用中国） | www.creditchina.gov.cn | high |
| `gov_procurement_ccgp` | 政府采购严重违法失信行为信息记录（政府采购网） | www.ccgp.gov.cn | high |

## 修改的文件

### 1. 后端资质匹配器

**文件**: `ai_tender_system/modules/business_response/qualification_matcher.py`

**修改内容**:
- **行 86-112**: 添加4个新资质定义到 `QUALIFICATION_MAPPING` 字典
  ```python
  'dishonest_executor': {
      'keywords': ['失信被执行人', '失信被执行人名单'],
      'priority': 'high',
      'category': '信用证明'
  },
  'tax_violation_check': {
      'keywords': ['重大税收违法', '重大税收违法案件当事人名单', '税收违法案件'],
      'priority': 'high',
      'category': '信用证明'
  },
  'gov_procurement_creditchina': {
      'keywords': ['信用中国', 'creditchina.gov.cn', '政府采购严重违法失信'],
      'priority': 'high',
      'category': '信用证明'
  },
  'gov_procurement_ccgp': {
      'keywords': ['中国政府采购网', 'ccgp.gov.cn', '政府采购严重违法失信行为信息记录'],
      'priority': 'high',
      'category': '信用证明'
  }
  ```

- **行 360-362**: 更新 `build_image_config_from_match` 方法中的资质列表
  ```python
  elif qual_key in ['iso9001', 'iso20000', 'iso27001',
                   'cmmi', 'itss', 'safety_production',
                   'software_copyright', 'patent_certificate',
                   'basic_telecom_permit', 'value_added_telecom_permit',
                   'dishonest_executor', 'tax_violation_check',
                   'gov_procurement_creditchina', 'gov_procurement_ccgp',
                   'level_protection']:
  ```

### 2. 图片处理模块

**文件**: `ai_tender_system/modules/business_response/image_handler.py`

**修改内容**:
- **行 34-37**: 添加图片关键词映射
  ```python
  'dishonest_executor': ['失信被执行人', '失信被执行人名单'],
  'tax_violation_check': ['重大税收违法', '税收违法案件当事人名单'],
  'gov_procurement_creditchina': ['政府采购严重违法失信', '政府采购信用记录'],
  'gov_procurement_ccgp': ['政府采购严重违法失信行为信息记录', '政府采购网查询']
  ```

- **行 48-51**: 添加默认图片尺寸
  ```python
  'dishonest_executor': (Inches(6), Inches(4)),
  'tax_violation_check': (Inches(6), Inches(4)),
  'gov_procurement_creditchina': (Inches(6), Inches(4)),
  'gov_procurement_ccgp': (Inches(6), Inches(4))
  ```

### 3. 前端资质管理器

**文件**: `ai_tender_system/web/static/js/pages/knowledge-base/company-profile-manager.js`

**修改内容**:
- **行 294-299**: 更新 `calculateQualificationProgress` 方法中的标准资质类型数组
  ```javascript
  const standardQualificationTypes = [
      'business_license', 'company_seal', 'iso9001', 'iso20000', 'iso27001',
      'cmmi', 'itss', 'level_protection',
      'dishonest_executor', 'tax_violation_check',
      'gov_procurement_creditchina', 'gov_procurement_ccgp'
  ];
  ```

- **行 953-956**: 更新资质卡片配置
  ```javascript
  // 信用资质（与后端 qualification_matcher.py 保持一致）
  { key: 'dishonest_executor', name: '失信被执行人名单（信用中国）', icon: 'bi-shield-x', category: 'credit' },
  { key: 'tax_violation_check', name: '重大税收违法案件当事人名单（信用中国）', icon: 'bi-exclamation-triangle', category: 'credit' },
  { key: 'gov_procurement_creditchina', name: '政府采购严重违法失信（信用中国）', icon: 'bi-flag', category: 'credit' },
  { key: 'gov_procurement_ccgp', name: '政府采购严重违法失信行为信息记录（政府采购网）', icon: 'bi-check-circle', category: 'credit' },
  ```

### 4. AI提取器

**文件**: `ai_tender_system/modules/tender_info/extractor.py`

**修改内容**:
- **行 263-282**: 更新 `_get_qualification_keywords` 方法中的关键词映射
  ```python
  # 信用资质类（4个独立资质，与后端 qualification_matcher.py 保持一致）
  'dishonest_executor': [
      '失信被执行人', '失信名单', '失信被执行人名单',
      '不得被列入失信', '未被列入失信', '失信黑名单'
  ],
  'tax_violation_check': [
      '重大税收违法', '重大税收违法案件当事人名单',
      '重大税收违法失信主体', '税收违法', '税收黑名单',
      '不得被列入.*重大税收违法', '未被列入.*重大税收违法'
  ],
  'gov_procurement_creditchina': [
      '信用中国', 'www.creditchina.gov.cn', 'creditchina.gov.cn',
      '政府采购严重违法失信', '信用中国.*政府采购',
      '不得被列入.*政府采购.*信用中国'
  ],
  'gov_procurement_ccgp': [
      '中国政府采购网', 'www.ccgp.gov.cn', 'ccgp.gov.cn',
      '政府采购严重违法失信行为信息记录', '政府采购网.*违法',
      '不得被列入.*政府采购网'
  ],
  ```

- **行 1156-1170**: 更新 `extract_supplier_eligibility_checklist` 方法中的检查清单映射
  ```python
  # 信用资质检查（4个独立资质）
  5: 'dishonest_executor',              # 失信被执行人名单
  5.1: 'tax_violation_check',           # 重大税收违法案件当事人名单
  6: 'gov_procurement_creditchina',     # 政府采购严重违法失信（信用中国）
  6.5: 'gov_procurement_ccgp',          # 政府采购严重违法失信行为信息记录（政府采购网）
  ```

### 5. 数据库迁移

**文件**: `ai_tender_system/database/migrations/005_migrate_credit_qualifications.sql`

**迁移逻辑**:
1. 创建备份表 `company_qualifications_backup_20251028`
2. 将旧资质key迁移到新key：
   - `credit_dishonest` → `dishonest_executor`
   - `credit_corruption` (包含"税收") → `tax_violation_check`
   - `credit_corruption` (其他) → `gov_procurement_creditchina`
   - `credit_tax` → `gov_procurement_creditchina` (使用 file_sequence+1 避免冲突)
   - `credit_procurement` → `gov_procurement_ccgp`

**迁移结果**:
- 公司1 (ID=1):
  - 失信被执行人 × 1
  - 政府采购（信用中国）× 2 (file_sequence: 1, 2)
  - 政府采购（政府采购网）× 1

- 公司2 (ID=2):
  - 失信被执行人 × 1
  - 重大税收违法 × 1
  - 政府采购（信用中国）× 1
  - 政府采购（政府采购网）× 1

## 关键设计决策

### 1. 为什么拆分为4个独立资质？

**原因**:
- 招标文件明确要求4个不同网站的查询截图
- creditchina.gov.cn 和 ccgp.gov.cn 是不同的网站系统
- 每个资质有独立的查询结果和证明文件

### 2. 命名约定

**原则**:
- 使用描述性的英文命名，不使用通用词如 `credit_xxx`
- 后缀体现查询来源网站（`_creditchina` vs `_ccgp`）
- 前端、后端、AI提取器保持完全一致的命名

### 3. 文件类型

所有4个资质均为**图片文件**（PNG/JPG），而非Word文档或承诺函。这是因为：
- 企业需要在网站上实际查询并截图
- 截图包含查询日期和网站水印，具有时效性
- 比承诺函更具证明力

## 系统完整性验证

### 前后端一致性检查

✅ **后端匹配器** (`qualification_matcher.py`):
- `dishonest_executor`
- `tax_violation_check`
- `gov_procurement_creditchina`
- `gov_procurement_ccgp`

✅ **图片处理** (`image_handler.py`):
- 4个资质均已添加到 `image_keywords`
- 4个资质均已添加到 `default_sizes`

✅ **前端管理器** (`company-profile-manager.js`):
- 资质卡片定义与后端一致
- 标准资质进度计算包含4个资质

✅ **AI提取器** (`extractor.py`):
- 关键词映射与后端一致
- 检查清单映射支持4个资质

✅ **数据库**:
- 旧资质key已全部迁移
- 无遗留的旧key记录

## 测试建议

### 1. 单元测试

- [ ] 测试 `QualificationMatcher.extract_required_qualifications` 能否正确识别4个资质
- [ ] 测试 `ImageHandler` 能否正确插入4个资质的图片
- [ ] 测试前端资质卡片是否正确显示

### 2. 集成测试

- [ ] 上传一个包含4个信用资质要求的招标文件
- [ ] 验证AI提取器能否正确提取4个资质需求
- [ ] 验证商务应答生成时能否正确匹配和插入4个资质图片

### 3. 数据库验证

```sql
-- 验证所有旧key已迁移
SELECT qualification_key, COUNT(*)
FROM company_qualifications
WHERE qualification_key IN ('credit_dishonest', 'credit_corruption', 'credit_tax', 'credit_procurement')
GROUP BY qualification_key;
-- 应该返回 0 行

-- 验证新key已正确创建
SELECT company_id, qualification_key, file_sequence, original_filename
FROM company_qualifications
WHERE qualification_key IN ('dishonest_executor', 'tax_violation_check', 'gov_procurement_creditchina', 'gov_procurement_ccgp')
ORDER BY company_id, qualification_key, file_sequence;
-- 应该返回 8 行（公司1有4个，公司2有4个）
```

## 向后兼容性

**数据库迁移**: ✅ 完全兼容
- 已执行的迁移保留了所有原始数据
- 备份表 `company_qualifications_backup_20251028` 可用于回滚
- 使用 `file_sequence` 自动递增避免冲突

**API接口**: ⚠️ 需要注意
- 前端需要使用新的资质key进行查询和上传
- 旧的资质key将无法匹配到任何数据
- 建议在生产环境部署前进行充分测试

## 后续工作

1. **前端UI优化**
   - [ ] 在资质上传页面添加帮助说明，指导用户如何获取4个查询截图
   - [ ] 区分信用中国的3个资质和政府采购网的1个资质

2. **文档更新**
   - [x] 更新系统文档，说明4个信用资质的区别
   - [ ] 编写用户操作手册，指导如何查询和上传资质

3. **性能优化**
   - [ ] 评估是否需要为信用资质添加过期提醒（如90天后需重新查询）

## 总结

本次重构成功地将信用资质从3个混合类型重构为4个独立、明确的资质类型，覆盖了：
- ✅ 后端匹配逻辑 (qualification_matcher.py)
- ✅ 图片处理逻辑 (image_handler.py)
- ✅ 前端UI管理 (company-profile-manager.js)
- ✅ AI需求提取 (extractor.py)
- ✅ 数据库迁移 (005_migrate_credit_qualifications.sql)

系统现在能够准确匹配招标文件中的4个独立信用资质要求，提升了商务应答的准确性和合规性。

---

**迁移执行日期**: 2025-10-28
**影响的记录数**: 8条（2家公司，每家4个信用资质）
**向后兼容性**: 需要前端同步更新，旧key已废弃
**回滚方案**: 使用备份表 `company_qualifications_backup_20251028` 恢复
