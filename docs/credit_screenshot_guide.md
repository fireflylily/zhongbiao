# 信用中国自动截图功能使用指南

## 功能概述

系统已集成信用中国网站自动截图功能,可以自动访问信用中国网站,查询企业信用信息并截图保存到公司资质库。

支持的信用查询类型:
- ✅ 失信被执行人名单查询
- ✅ 重大税收违法案件当事人名单查询
- ✅ 政府采购严重违法失信行为记录查询

## 使用方法

### 方式一: 前端一键获取(推荐)

1. **进入公司详情页面**
   - 导航到 "知识库" → "公司管理"
   - 选择要获取信用证明的公司
   - 点击进入公司详情页

2. **点击自动获取按钮**
   - 切换到 "资质信息" 标签页
   - 在 "信用资质证明" 分类下,找到 "自动获取信用证明" 按钮
   - 点击按钮开始自动获取

3. **等待处理完成**
   - 系统会自动访问信用中国网站
   - 依次查询3种信用信息
   - 自动截图并保存到资质库
   - 完成后显示成功数量

4. **查看结果**
   - 截图完成后会自动刷新资质列表
   - 可以在对应的资质卡片中查看截图
   - 支持下载和删除操作

### 方式二: API调用

如果需要批量处理或集成到其他系统,可以直接调用API:

```bash
# 获取单个公司的所有信用证明
curl -X POST http://localhost:8110/api/browser/creditchina/screenshot/all \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "某某科技有限公司",
    "company_id": 1
  }'
```

详细API文档请参考: `docs/browser_automation_api.md`

## 功能特点

### ✅ 自动化流程

1. **自动导航**: 自动打开信用中国网站
2. **智能填表**: 自动填写公司名称
3. **自动查询**: 自动点击查询按钮
4. **等待加载**: 智能等待页面加载完成
5. **全屏截图**: 自动截取完整页面
6. **自动保存**: 截图保存到uploads目录
7. **自动关联**: 自动关联到公司资质库

### 📊 批量处理

- 一键获取3种信用证明
- 并发执行,提高效率
- 统一管理,集中展示

### 🔄 实时反馈

- 加载状态显示
- 成功/失败计数
- 详细错误信息
- 自动刷新列表

## 技术实现

### 后端架构

```
┌─────────────────────────────────────────┐
│  API层 (api_browser_automation_bp.py)  │
│  - 接收前端请求                          │
│  - 参数验证                             │
│  - 返回结果                             │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  服务层 (browser_automation.py)         │
│  - 生成截图配置                          │
│  - 管理查询类型                          │
│  - 文件命名规则                          │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  浏览器层 (Playwright)                   │
│  - 启动浏览器                            │
│  - 页面导航                             │
│  - 元素操作                             │
│  - 截图保存                             │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  数据层 (database)                       │
│  - 插入资质记录                          │
│  - 关联公司ID                           │
│  - 记录文件信息                          │
└─────────────────────────────────────────┘
```

### 前端集成

```vue
<!-- QualificationTab.vue -->
<el-button
  v-if="category.key === 'credit'"
  type="primary"
  :loading="autoFetchLoading"
  @click="handleAutoFetchCredit"
>
  <el-icon><Download /></el-icon>
  自动获取信用证明
</el-button>
```

## 环境要求

### 基础环境(已满足)

- ✅ Python 3.8+
- ✅ Flask Web框架
- ✅ Vue 3前端
- ✅ SQLite数据库

### 浏览器自动化(可选)

如需服务端执行实际截图,需安装Playwright:

```bash
# 安装Playwright
pip3 install playwright

# 安装浏览器
playwright install chromium
```

**注意**:
- 如果未安装Playwright,系统仍可正常工作
- API会返回截图配置信息
- 可在客户端使用其他工具执行截图

## 文件存储

截图文件保存位置:
```
ai_tender_system/data/uploads/
├── 20251123_104558_dishonest_executor_测试公司.png
├── 20251123_104559_tax_violation_check_测试公司.png
└── 20251123_104600_gov_procurement_creditchina_测试公司.png
```

文件命名格式: `{时间戳}_{查询类型}_{公司名称}.png`

## 数据库记录

截图自动关联到 `company_qualifications` 表:

| 字段 | 说明 |
|------|------|
| company_id | 公司ID |
| qualification_key | 资质类型(如: dishonest_executor) |
| file_path | 文件绝对路径 |
| original_filename | 原始文件名 |
| file_size | 文件大小(字节) |
| upload_date | 上传时间 |

## 常见问题

### Q: 点击按钮后没有反应?

A: 检查以下几点:
1. 确认公司名称已填写
2. 查看浏览器控制台是否有错误
3. 检查网络连接是否正常
4. 确认后端服务是否运行

### Q: 提示"Playwright未安装"?

A: 这是正常提示,有两种处理方式:
1. 安装Playwright: `pip3 install playwright && playwright install chromium`
2. 继续使用,系统会返回配置信息供其他工具使用

### Q: 截图失败怎么办?

A: 可能的原因:
1. 信用中国网站不可访问
2. 网站页面结构变化
3. 网络连接问题
4. 验证码拦截

解决方法:
- 检查网站是否可访问
- 查看日志获取详细错误信息
- 联系技术人员更新选择器配置

### Q: 能否自定义查询类型?

A: 可以,编辑 `browser_automation.py`:

```python
QUERY_TYPES = {
    # 添加新的查询类型
    'custom_query': {
        'name': '自定义查询',
        'url': 'https://目标网站',
        'search_selector': 'input选择器',
        'search_button': 'button选择器',
        'result_selector': '结果选择器'
    }
}
```

## 最佳实践

### 1. 定期更新

建议每年或每半年重新获取一次信用证明,保证资质信息的时效性。

### 2. 批量处理

对于多个公司,可以使用API批量处理:

```python
import requests

companies = [
    {"id": 1, "name": "公司A"},
    {"id": 2, "name": "公司B"},
    {"id": 3, "name": "公司C"}
]

for company in companies:
    response = requests.post(
        'http://localhost:8110/api/browser/creditchina/screenshot/all',
        json={
            'company_name': company['name'],
            'company_id': company['id']
        }
    )
    print(f"{company['name']}: {response.json()}")
```

### 3. 错误处理

建议添加重试机制和错误通知:

```javascript
async function autoFetchWithRetry(companyName, companyId, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      const response = await axios.post('/api/browser/creditchina/screenshot/all', {
        company_name: companyName,
        company_id: companyId
      })

      if (response.data.success) {
        return response.data
      }
    } catch (error) {
      if (i === maxRetries - 1) throw error
      await new Promise(resolve => setTimeout(resolve, 2000 * (i + 1)))
    }
  }
}
```

## 更新日志

### v1.0.0 (2025-11-23)

- ✅ 初始版本发布
- ✅ 支持3种信用查询类型
- ✅ 前端一键获取功能
- ✅ 自动关联资质库
- ✅ 完整的API接口

## 后续计划

- [ ] 支持更多政府网站查询
- [ ] 添加验证码识别功能
- [ ] 支持定时自动更新
- [ ] 添加查询历史记录
- [ ] 导出批量报告功能

## 技术支持

如有问题或建议,请联系开发团队或提交issue。

相关文档:
- [浏览器自动化API文档](browser_automation_api.md)
- [系统架构文档](../README.md)
