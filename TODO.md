# 待改进事项 (TODO)

## 优先级说明
- 🔴 **高优先级** - 影响核心功能，需要尽快处理
- 🟡 **中优先级** - 改善用户体验或代码质量
- 🟢 **低优先级** - 优化性改进，不影响使用

---

## 🟡 1. 资质配置共用重构

### 问题描述
当前系统中有两处维护资质类型定义和关键词配置，存在重复维护问题：

1. **资质提取器** (`modules/tender_info/extractor.py`)
   - 从招标文档提取资质要求
   - 定义了约18种资质类型
   - 每种资质有5-20个关键词

2. **资质匹配器** (`modules/business_response/qualification_matcher.py`)
   - 商务应答时识别模板占位符
   - 定义了21种资质类型
   - 每种资质有2-10个关键词

### 导致的问题
- 重复维护，增加工作量
- 可能出现命名不一致（如 `_license` vs `_permit`）
- 关键词覆盖范围不同
- 添加新资质需要修改多处

### 改进方案
创建统一的资质配置模块 `common/qualification_config.py`：

```python
QUALIFICATION_TYPES = {
    'business_license': {
        'name': '营业执照',
        'category': '基础资质',
        'keywords': ['营业执照', '三证合一', '统一社会信用代码', ...],
        'priority': 'high',
        'display_title': '营业执照',
        'db_category': '基础资质'
    },
    # ... 合并后约30种资质类型
}
```

提供适配函数：
- `get_qualification_keywords()` - 返回 extractor 需要的格式
- `get_qualification_mapping()` - 返回 matcher 需要的格式
- `get_all_types()` - 返回完整列表

### 实施步骤
1. 创建 `common/qualification_config.py`
2. 合并两套资质定义（取并集）
3. 合并关键词（每种资质取最全的）
4. 重构 `extractor.py` - 移除 `_get_qualification_keywords()`
5. 重构 `qualification_matcher.py` - 移除 `QUALIFICATION_MAPPING`
6. 测试验证两个模块功能正常

### 预计工作量
2-3 小时

### 优先级
🟡 中优先级

### 相关文件
- `ai_tender_system/modules/tender_info/extractor.py`
- `ai_tender_system/modules/business_response/qualification_matcher.py`
- `ai_tender_system/modules/business_response/document_scanner.py`

---

## 🔴 2. 资质显示数据不完整问题

### 问题描述
当前项目49的资质数据库中：
- 已保存 22 项资质
- 但只有 6 项有描述（标记为必需）
- 其他 16 项描述为空（标记为可选）

实际上代码已经能提取 12-13 项资质，但数据库中是旧数据。

### 改进方案
1. 清理项目49的旧资质数据
2. 重新运行 AI 提取资格要求
3. 验证所有资质正确显示

### 预计工作量
10-15 分钟

### 优先级
🔴 高优先级（影响当前使用）

---

## 🟡 3. 页面布局优化

### 已完成
- ✅ PageHeader 返回按钮与标题在同一行
- ✅ 减小整体页面空间占用（padding、margin、字体）
- ✅ Tab 顺序调整（文档与章节移到最后）
- ✅ 身份证正反面合并显示

### 待优化
- 考虑响应式布局优化（移动端适配）
- 表格列宽自适应

---

## 🔴 4. 授权书文本模式智能填写

### 问题描述
授权书中包含复杂的多占位符文本模式，需要智能识别并填充多个相关字段。

### 典型文本格式
```
本授权书声明：注册于              的              公司的在下面签署的
   （陈忠岳、客户经理）    代表本公司授权在下面签署的
   （被授权人的姓名、职务）    为本公司的合法代理人
```

### 需要填充的占位符
1. **注册地** - `注册于              的`
   - 填充：公司注册地址（如"北京市"）

2. **公司名称** - `              公司`
   - 填充：完整公司名称

3. **法定代表人信息** - `（陈忠岳、客户经理）`
   - 填充：法定代表人姓名 + 职务
   - 格式：`（张三、总经理）`

4. **被授权人信息** - `（被授权人的姓名、职务）`
   - 填充：被授权人姓名 + 职务
   - 格式：`（李四、项目经理）`

5. **授权有效期** - `有效期至              `
   - 填充：有效期日期或"长期有效"

### 当前状态
- ✅ 已支持授权书位置识别
- ❌ 复杂文本模式未处理
- ❌ 缺少注册地、法人职务等字段
- ❌ 缺少授权有效期字段

### 改进目标
1. **数据库字段扩展** - 添加注册地、法人职务、被授权人信息、授权有效期等字段
2. **复杂模式识别** - 识别授权书中的多占位符组合模式
3. **智能填充** - 正确解析并填充每个占位符
4. **前端UI** - 添加所有相关字段的编辑界面

### 涉及数据库字段
```sql
-- companies表需要补充的字段：
ALTER TABLE companies ADD COLUMN registered_location TEXT;           -- 注册地
ALTER TABLE companies ADD COLUMN legal_representative_position TEXT; -- 法定代表人职务
ALTER TABLE companies ADD COLUMN authorized_person_name TEXT;        -- 被授权人姓名
ALTER TABLE companies ADD COLUMN authorized_person_position TEXT;    -- 被授权人职务
ALTER TABLE companies ADD COLUMN authorization_validity_period TEXT; -- 授权有效期
```

### 复杂模式识别策略
```python
# 智能填充器需要支持的模式：
patterns = {
    # 模式1：注册于{空格}的{空格}公司
    'company_registration': r'注册于\s{3,20}的\s{3,20}公司',

    # 模式2：括号内的示例文本（需要替换）
    'legal_rep_example': r'（[^）]*、[^）]*）',  # 如：（陈忠岳、客户经理）

    # 模式3：被授权人的姓名、职务
    'authorized_person_hint': r'（被授权人的姓名、职务）',

    # 模式4：有效期
    'validity_period': r'有效期至\s{3,20}',
}

# 填充逻辑：
# 1. 识别模式类型
# 2. 提取占位符位置
# 3. 按正确格式填充
```

### 字段映射设计
```python
field_mapping = {
    'registeredLocation': 'registered_location',              # 注册地
    'legalRepresentative': 'legal_representative',            # 法人姓名
    'legalRepresentativePosition': 'legal_representative_position',  # 法人职务
    'authorizedPersonName': 'authorized_person_name',         # 被授权人姓名
    'authorizedPersonPosition': 'authorized_person_position', # 被授权人职务
    'authorizationValidityPeriod': 'authorization_validity_period',  # 授权有效期
}
```

### 实施步骤
1. 分析授权书的各种文本模式
2. 数据库添加所需字段
3. 后端API支持新字段的读写
4. 前端UI添加字段编辑界面
5. 智能填充器实现复杂模式识别
6. 处理特殊格式（如括号内的示例文本替换）
7. 测试多种授权书模板

### 技术难点
1. **括号内示例文本处理** - 需要识别并替换示例（如"陈忠岳、客户经理" → "张三、总经理"）
2. **空格占位符长度不定** - 需要灵活匹配
3. **字段组合** - 多个字段需要正确组合（姓名+职务）

### 预计工作量
3-4 小时

### 优先级
🔴 高优先级（实际业务需求，授权书必填项）

### 相关文件
- `ai_tender_system/database/company_schema.sql`
- `ai_tender_system/web/blueprints/api_companies_bp.py`
- `frontend/src/views/Knowledge/components/CompanyBasicTab.vue`
- `ai_tender_system/modules/business_response/smart_filler.py`

---

## 🔴 5. 网络安全审查承诺声明填写

### 问题描述
商务应答文档中包含网络安全审查承诺声明，需要自动填充项目名称和相关信息，但当前系统未处理此类占位符。

### 典型文本格式
```
我司承诺在             项目采购中我司提供的产品及服务不涉及影响或可能影响国家安全，
满足《网络安全审查办法》及采购方相应的申报网络安全审查的相关要求，
所投产品可通过网络安全审查，具体情况说明如下
```

### 需要填充的占位符
1. **项目名称** - 空格占位符应该填充为具体项目名称
   - 示例：`在【项目名称】项目采购中`
   - 当前：`在             项目采购中`（未填充）

2. **具体情况说明** - 可能需要填充公司的网络安全资质说明
   - 如：等保三级认证情况
   - 如：已通过的网络安全审查记录

### 改进目标
1. **占位符识别** - 智能识别"在____项目"等空格占位符模式
2. **自动填充** - 填充项目名称到承诺声明中
3. **扩展支持** - 支持填充网络安全相关说明（可选）

### 涉及模块
1. **智能填充器** (`modules/business_response/smart_filler.py`)
   - 添加空格占位符模式识别
   - 支持正则匹配：`在\s{3,20}项目`
   - 填充为：`在【项目名称】项目`

2. **数据库**（可选，如需填充说明）
   - 在公司信息中添加 `network_security_statement` 字段
   - 存储标准的网络安全说明文本

### 典型占位符模式
```python
patterns = {
    '项目名称空格': r'在\s{3,20}项目',  # 匹配：在             项目
    '日期空格': r'于\s{3,20}年',        # 匹配：于             年
    '单位名称空格': r'：\s{3,20}（',    # 匹配：公司：             （
}
```

### 实施步骤
1. 研究现有模板中网络安全承诺的表述格式
2. 在 `smart_filler.py` 添加空格占位符识别
3. 测试验证项目名称正确填充
4. （可选）添加网络安全说明字段和填充逻辑
5. 更新文档

### 预计工作量
1-2 小时

### 优先级
🔴 高优先级（实际业务需求，影响文档完整性）

### 相关文件
- `ai_tender_system/modules/business_response/smart_filler.py`
- 商务应答模板文档（需分析占位符格式）

### 扩展需求（可选）
- 支持自定义网络安全说明模板
- 支持从等保三级证书自动提取信息
- 支持多种承诺声明格式

---

## 🔴 6. 保证金退款信息自动填写

### 问题描述
商务应答文档中的"保证金退款信息"部分需要填写退款金额和银行账号信息，当前系统未自动处理这些字段。

### 典型字段
1. **保证金退款金额**
   - 占位符格式：`保证金退款金额：           元`
   - 或：`退款金额：人民币           元（大写：                    ）`

2. **银行账号信息**
   - 开户银行：`开户银行：                    `
   - 银行账号：`银行账号：                    `
   - 账户名称：`户名：                        `

### 当前状态
- ❌ 保证金金额未自动填充
- ❌ 银行账号信息未自动填充
- ✅ 公司基本信息中已有部分银行信息字段（`bank_name`, `bank_account`）

### 改进目标
1. **保证金金额计算**
   - 从项目信息中提取保证金金额
   - 支持自动计算（如：合同金额的1%、2%等）
   - 支持固定金额

2. **银行信息填充**
   - 从公司信息数据库读取银行账号
   - 自动填充开户行、账号、户名

3. **金额大写转换**
   - 自动将阿拉伯数字转换为中文大写
   - 如：`12000` → `壹万贰仟元整`

### 涉及模块

1. **数据库字段扩展**
   ```sql
   -- companies表可能需要补充：
   ALTER TABLE companies ADD COLUMN account_holder_name TEXT;  -- 账户名称（如果与公司名称不同）

   -- tender_projects表可能需要补充：
   ALTER TABLE tender_projects ADD COLUMN deposit_amount REAL;  -- 保证金金额
   ALTER TABLE tender_projects ADD COLUMN deposit_ratio REAL;   -- 保证金比例（可选）
   ```

2. **智能填充器** (`smart_filler.py`)
   - 添加保证金相关占位符识别
   - 支持模式：
     - `保证金.*金额`
     - `退款.*金额`
     - `开户.*银行`
     - `银行.*账号`

3. **工具函数**
   ```python
   def number_to_chinese_currency(amount: float) -> str:
       """将数字转换为中文大写金额"""
       # 12000.00 → "壹万贰仟元整"
   ```

### 实施步骤
1. 分析现有模板中保证金字段的表述格式
2. 数据库添加保证金和银行账号相关字段
3. 后端API支持保证金信息的读写
4. 前端UI添加保证金信息编辑
5. 智能填充器添加字段识别和填充
6. 实现金额大写转换工具
7. 测试验证

### 字段映射设计
```python
field_mapping = {
    'depositAmount': 'deposit_amount',           # 保证金金额
    'depositAmountChinese': 'deposit_amount_chinese',  # 大写金额（自动计算）
    'bankName': 'bank_name',                     # 开户行
    'bankAccount': 'bank_account',               # 银行账号
    'accountHolderName': 'account_holder_name',  # 户名
}
```

### 预计工作量
2-3 小时

### 优先级
🔴 高优先级（实际业务需求，投标必填项）

### 相关文件
- `ai_tender_system/database/company_schema.sql`
- `ai_tender_system/database/tender_processing_schema.sql`
- `ai_tender_system/modules/business_response/smart_filler.py`
- `ai_tender_system/web/blueprints/api_companies_bp.py`
- `frontend/src/views/Knowledge/components/CompanyBasicTab.vue`

---

## 🟡 7. 生成投标PPT功能

### 功能描述
自动从投标文档（商务应答、技术方案等）生成投标演示PPT

### 核心需求
1. **内容提取**
   - 从商务应答文档提取关键信息
   - 从技术方案提取技术亮点
   - 提取公司资质和案例

2. **PPT生成**
   - 使用python-pptx库生成PPT
   - 模板化设计（可配置主题）
   - 自动排版和美化

3. **内容结构**
   - 封面页（项目名称、公司LOGO）
   - 公司介绍（简介、资质）
   - 技术方案（架构、特色）
   - 项目案例（业绩展示）
   - 团队介绍（核心人员）
   - 结束页（联系方式）

### 技术实现
1. **后端API** (`/api/ppt/generate`)
   ```python
   def generate_bid_ppt(project_id):
       # 1. 提取项目数据
       # 2. 提取公司资质
       # 3. 提取案例和人员
       # 4. 生成PPT文件
       return ppt_file_path
   ```

2. **前端页面**
   - 在标书管理详情页添加"生成PPT"按钮
   - 支持预览和下载
   - 可选：自定义模板和内容

3. **依赖库**
   - `python-pptx` - PPT生成
   - `Pillow` - 图片处理

### 实施步骤
1. 安装依赖：`pip install python-pptx`
2. 创建PPT生成模块 (`modules/ppt_generator/`)
3. 设计PPT模板（布局、配色）
4. 实现数据提取和填充逻辑
5. 添加API接口
6. 前端集成（按钮、预览、下载）
7. 测试和优化

### 预计工作量
4-6 小时

### 优先级
🟡 中优先级（增值功能）

### 相关技术参考
- python-pptx文档: https://python-pptx.readthedocs.io/
- PPT模板设计参考: 投标汇报PPT模板

---

## 🟡 5. 日期字段字体一致性问题

### 问题描述
在商务应答文档中填充日期时，数字的字体与周围文字不一致

### 具体表现
- 日期字段：`2025年12月08日`
- 年月日汉字：使用文档默认字体（如宋体）
- 数字部分：可能使用了不同字体（如Times New Roman、Arial等）

### 原因分析
Word文档中的数字默认可能使用西文字体，而汉字使用中文字体，导致：
- 视觉效果不统一
- 可能影响专业性

### 改进方案
在 `smart_filler.py` 或 `info_filler.py` 填充日期字段时：
1. 检测原始段落的字体设置
2. 设置填充内容的字体与原文一致
3. 或统一使用指定字体（如"宋体"）

```python
# 填充时设置字体
run.font.name = '宋体'  # 中文字体
run.font.size = Pt(12)  # 保持原字号
run._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')  # 东亚字体
run._element.rPr.rFonts.set(qn('w:ascii'), '宋体')     # ASCII字符也用宋体
```

### 实施步骤
1. 定位日期填充代码位置
2. 添加字体统一处理逻辑
3. 测试多种文档模板
4. 验证字体一致性

### 预计工作量
30分钟 - 1小时

### 优先级
🟡 中优先级（影响文档美观度）

### 相关文件
- `ai_tender_system/modules/business_response/smart_filler.py`
- `ai_tender_system/modules/business_response/info_filler.py`（如果使用）

---

## 🔴 6. 保证金金额的提取和填写

### 问题描述
商务应答文档中需要填写投标保证金金额（大写），但当前系统未处理此字段。

### 典型文本格式
```
保证金金额（大写）____________________元；
或
投标保证金：人民币（大写）__________元整
```

### 需要实现的功能
1. **提取保证金金额**
   - 从招标文档中提取保证金金额（数字）
   - 从项目信息中读取保证金金额

2. **金额转换**
   - 数字转大写金额
   - 示例：`123456.78` → `壹拾贰万叁仟肆佰伍拾陆元柒角捌分`
   - 示例：`50000` → `伍万元整`

3. **自动填充**
   - 识别保证金占位符模式
   - 填充大写金额到文档中

### 涉及模块
1. **数据库**
   - 在 `tender_projects` 表中添加 `bid_bond_amount` 字段（如果没有）
   - 存储保证金金额（数字格式）

2. **招标信息提取器** (`modules/tender_info/extractor.py`)
   - 添加保证金金额提取规则
   - 支持常见表述：
     - "投标保证金：XX万元"
     - "保证金金额：XX元"
     - "需缴纳保证金XX元"

3. **智能填充器** (`modules/business_response/smart_filler.py`)
   - 添加保证金占位符识别
   - 实现数字转大写金额函数
   - 支持占位符模式：
     - `保证金金额（大写）{空格}元`
     - `人民币（大写）{空格}元整`
     - `bidBondAmount` 等camelCase占位符

### 金额转换实现
```python
def number_to_chinese(amount: float) -> str:
    """
    将数字金额转换为中文大写

    Args:
        amount: 金额数字（如 123456.78）

    Returns:
        中文大写金额（如"壹拾贰万叁仟肆佰伍拾陆元柒角捌分"）
    """
    # 中文数字
    chinese_nums = ['零', '壹', '贰', '叁', '肆', '伍', '陆', '柒', '捌', '玖']
    # 单位
    units = ['', '拾', '佰', '仟', '万', '拾', '佰', '仟', '亿']
    # 实现转换逻辑...
```

### 实施步骤
1. 实现数字转大写金额函数（可复用现有库如 `cn2an`）
2. 在数据库中添加保证金金额字段
3. 在招标信息提取时识别保证金金额
4. 在智能填充器中添加保证金占位符识别
5. 测试各种金额格式的转换
6. 验证填充效果

### 预计工作量
2-3 小时

### 优先级
🔴 高优先级（实际业务需求，投标必填项）

### 相关文件
- `ai_tender_system/modules/business_response/smart_filler.py`
- `ai_tender_system/modules/tender_info/extractor.py`
- `ai_tender_system/database/tender_processing_schema.sql`

### 技术参考
- cn2an库：`pip install cn2an` - 中文数字转换
- 或自行实现金额转大写逻辑

---

## 🟡 7. 项目编号默认值优化

### 问题描述
当前创建新项目时，项目编号字段会自动生成默认值（如 `PRJ-1732776505`），但实际业务中项目编号应该由用户根据实际情况填写，不应有预设值。

### 当前行为
```javascript
projectNumber: `PRJ-${Date.now()}`  // 自动生成时间戳编号
```

### 期望行为
```javascript
projectNumber: ''  // 默认为空，由用户填写
```

### 影响页面
- 商务应答页面（新建项目模式）
- 技术方案页面（新建项目模式）
- 点对点应答页面（新建项目模式）
- 标书管理页面（创建项目）

### 改进方案
1. **前端修改** - 移除默认值生成逻辑
   - `Response.vue` - 新建项目时 `projectNumber` 默认为空字符串
   - `TechProposal.vue` - 同上
   - `PointToPoint.vue` - 同上
   - `Management.vue` - 项目创建表单默认为空

2. **表单验证**（可选）
   - 如果项目编号是必填项，添加非空验证
   - 或保持可选，允许用户后续填写

3. **占位符优化**
   - 将 placeholder 从 `PRJ-...` 改为更友好的提示
   - 如：`请输入项目编号（如：PRJ-2024-001）`

### 实施步骤
1. 查找所有使用 `PRJ-${Date.now()}` 的位置
2. 改为空字符串 `''`
3. 优化 placeholder 提示文本
4. 测试新建项目流程
5. 确认不影响现有项目

### 预计工作量
15-30 分钟

### 优先级
🟡 中优先级（用户体验优化）

### 相关文件
- `frontend/src/views/Business/Response.vue`
- `frontend/src/views/Business/TechProposal.vue`
- `frontend/src/views/Business/PointToPoint.vue`
- `frontend/src/views/Tender/Management.vue`

---

## 🟢 8. 其他待优化项

### 代码质量
- [ ] 添加单元测试覆盖
- [ ] 完善错误处理和日志
- [ ] 代码注释补充

### 性能优化
- [ ] 前端代码分割（减少 chunk 大小）
- [ ] 图片压缩和懒加载
- [ ] API 响应缓存

### 用户体验
- [ ] 加载状态优化
- [ ] 错误提示更友好
- [ ] 操作反馈及时性

---

## 更新记录

- 2025-11-28: 添加"保证金退款信息自动填写"任务项（🔴高优先级）
- 2025-11-28: 添加"日期字段字体一致性"任务项（🟡中优先级）
- 2025-11-28: 添加"网络安全审查承诺声明填写"任务项（🔴高优先级）
- 2025-11-28: 更新"授权书文本模式智能填写"任务（🔴高优先级，包含注册地、法人职务、被授权人、有效期等多字段）
- 2025-11-28: 添加"生成投标PPT功能"任务项（🟡中优先级）
- 2025-11-28: 完成图片加载性能优化（Base64→外部链接，提升80%）
- 2025-11-28: 修复政府采购资质识别错误
- 2025-11-28: 添加资质处理详情表格展示
- 2025-11-27: 创建待改进事项文档
- 2025-11-27: 完成页面布局优化
- 2025-11-27: 统一资质 key 命名（使用 `_permit` 后缀）
