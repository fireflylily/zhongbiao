# 浏览器自动化API使用文档

## 概述

浏览器自动化服务提供了自动访问信用中国网站并截图的功能,可以自动获取企业的信用证明文件。

## API接口

### 1. 获取可用查询类型

**接口**: `GET /api/browser/creditchina/query-types`

**描述**: 获取所有支持的信用查询类型列表

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "key": "dishonest_executor",
      "name": "失信被执行人",
      "url": "https://www.creditchina.gov.cn/xinyongxinxixiangqing/index.html?entityType=1"
    },
    {
      "key": "tax_violation_check",
      "name": "重大税收违法案件当事人名单",
      "url": "https://www.creditchina.gov.cn/xinyongxinxixiangqing/index.html?entityType=1"
    },
    {
      "key": "gov_procurement_creditchina",
      "name": "政府采购严重违法失信",
      "url": "https://www.creditchina.gov.cn/xinyongxinxixiangqing/index.html?entityType=1"
    }
  ]
}
```

### 2. 截取单个信用查询结果

**接口**: `POST /api/browser/creditchina/screenshot`

**描述**: 截取指定公司的某一类信用查询结果

**请求参数**:
```json
{
  "company_name": "公司名称",
  "query_type": "查询类型(dishonest_executor|tax_violation_check|gov_procurement_creditchina)",
  "company_id": 123  // 可选,用于自动关联到公司资质库
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "file_path": "/path/to/screenshot.png",
    "filename": "20251123_104558_dishonest_executor_测试公司.png",
    "query_type": "dishonest_executor",
    "query_name": "失信被执行人",
    "company_name": "测试公司",
    "screenshot_url": "/api/files/serve/uploads/20251123_104558_dishonest_executor_测试公司.png",
    "note": "浏览器自动化功能需要在支持MCP的环境中运行"
  }
}
```

### 3. 批量截取信用查询结果

**接口**: `POST /api/browser/creditchina/screenshot/batch`

**描述**: 批量截取指定公司的多个信用查询结果

**请求参数**:
```json
{
  "company_name": "公司名称",
  "query_types": ["dishonest_executor", "tax_violation_check", "gov_procurement_creditchina"],
  "company_id": 123  // 可选
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "company_name": "测试公司",
    "results": [
      {
        "success": true,
        "file_path": "/path/to/screenshot1.png",
        "filename": "...",
        "query_type": "dishonest_executor",
        "query_name": "失信被执行人",
        "screenshot_url": "/api/files/serve/uploads/..."
      },
      // ... 更多结果
    ],
    "stats": {
      "total": 3,
      "succeeded": 3,
      "failed": 0
    }
  }
}
```

### 4. 截取所有信用查询结果

**接口**: `POST /api/browser/creditchina/screenshot/all`

**描述**: 一键截取指定公司的所有类型信用查询结果

**请求参数**:
```json
{
  "company_name": "公司名称",
  "company_id": 123  // 可选
}
```

**响应**: 与批量截取接口相同

## 使用示例

### curl命令示例

```bash
# 1. 获取查询类型列表
curl -X GET http://localhost:8110/api/browser/creditchina/query-types

# 2. 截取失信被执行人查询结果
curl -X POST http://localhost:8110/api/browser/creditchina/screenshot \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "某某科技有限公司",
    "query_type": "dishonest_executor",
    "company_id": 1
  }'

# 3. 批量截取多个查询结果
curl -X POST http://localhost:8110/api/browser/creditchina/screenshot/batch \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "某某科技有限公司",
    "query_types": ["dishonest_executor", "tax_violation_check"],
    "company_id": 1
  }'

# 4. 截取所有查询结果
curl -X POST http://localhost:8110/api/browser/creditchina/screenshot/all \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "某某科技有限公司",
    "company_id": 1
  }'
```

### JavaScript示例

```javascript
// 获取查询类型
async function getQueryTypes() {
  const response = await fetch('/api/browser/creditchina/query-types');
  const data = await response.json();
  console.log('可用查询类型:', data.data);
  return data.data;
}

// 截取单个查询结果
async function captureScreenshot(companyName, queryType, companyId = null) {
  const response = await fetch('/api/browser/creditchina/screenshot', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      company_name: companyName,
      query_type: queryType,
      company_id: companyId
    })
  });

  const result = await response.json();
  if (result.success) {
    console.log('截图成功:', result.data);
    return result.data;
  } else {
    console.error('截图失败:', result.error);
    throw new Error(result.error);
  }
}

// 批量截取
async function captureBatchScreenshots(companyName, queryTypes, companyId = null) {
  const response = await fetch('/api/browser/creditchina/screenshot/batch', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      company_name: companyName,
      query_types: queryTypes,
      company_id: companyId
    })
  });

  const result = await response.json();
  return result;
}

// 使用示例
async function main() {
  try {
    // 获取查询类型
    const types = await getQueryTypes();

    // 截取失信被执行人查询
    const screenshot = await captureScreenshot(
      '测试公司',
      'dishonest_executor',
      1
    );

    console.log('截图URL:', screenshot.screenshot_url);
  } catch (error) {
    console.error('操作失败:', error);
  }
}
```

## 技术实现

### 架构说明

1. **服务层** (`ai_tender_system/services/browser_automation.py`)
   - `CreditChinaScreenshotService`: 核心服务类
   - 提供截图配置生成和管理功能
   - 定义查询类型映射表

2. **API层** (`ai_tender_system/web/blueprints/api_browser_automation_bp.py`)
   - 提供RESTful API接口
   - 处理HTTP请求和响应
   - 调用Playwright MCP工具执行浏览器操作

3. **浏览器自动化**
   - 使用Playwright MCP工具
   - 自动导航到信用中国网站
   - 填写搜索表单
   - 等待结果加载
   - 截图保存

### 查询类型映射

系统支持的查询类型及其配置:

| 查询类型 | 名称 | 资质键 |
|---------|------|--------|
| `dishonest_executor` | 失信被执行人 | dishonest_executor |
| `tax_violation_check` | 重大税收违法案件当事人名单 | tax_violation_check |
| `gov_procurement_creditchina` | 政府采购严重违法失信 | gov_procurement_creditchina |

### 文件命名规则

截图文件名格式: `{时间戳}_{查询类型}_{公司名称}.png`

示例: `20251123_104558_dishonest_executor_测试公司.png`

## 注意事项

1. **MCP环境要求**: 浏览器自动化功能需要在支持MCP(Model Context Protocol)的环境中运行,否则仅返回配置信息。

2. **网站可用性**: 信用中国网站可能会更新页面结构,可能需要调整选择器配置。

3. **验证码处理**: 如果网站启用验证码,需要额外的处理逻辑。

4. **性能考虑**: 批量截图会依次执行多个查询,可能需要较长时间。

5. **文件存储**: 截图文件保存在 `ai_tender_system/data/uploads/` 目录下。

## 扩展开发

### 添加新的查询类型

在 `browser_automation.py` 中的 `QUERY_TYPES` 字典添加新配置:

```python
QUERY_TYPES = {
    # ... 现有配置
    'new_query_type': {
        'name': '新查询类型名称',
        'url': 'https://目标网站URL',
        'search_selector': 'input选择器',
        'search_button': 'button选择器',
        'result_selector': '结果区域选择器'
    }
}
```

### 添加新的查询网站

可以创建新的服务类,参照 `CreditChinaScreenshotService` 的实现,支持其他政府网站的自动查询和截图。

## 故障排查

### 常见问题

1. **API返回404**: 检查蓝图是否正确注册到Flask应用
2. **截图失败**: 检查网站是否可访问,选择器是否正确
3. **文件路径错误**: 确认uploads目录存在且有写权限

### 日志查看

查看日志了解详细错误信息:

```bash
# 查看浏览器自动化服务日志
tail -f logs/browser_automation.log

# 查看API日志
tail -f logs/web.api_browser_automation.log
```

## 更新历史

- **2025-11-23**: 初始版本,支持信用中国三种查询类型的自动截图
