# AI智慧标书系统 - API使用文档

## 概述

本文档详细记录了AI智慧标书系统的API架构、接口规范和使用方式。系统采用Flask后端 + HTML/JavaScript前端架构，提供完整的招标文档处理、公司管理、商务应答等功能。

## 系统架构

```
Frontend (HTML/JS) ←→ Flask API ←→ Business Modules ←→ External APIs
     ↓                    ↓              ↓              ↓
- tender_info.js    - Flask Routes  - TenderExtractor  - LLM APIs
- company_selection.js - API Endpoints - P2P Processor   - File Processing
- business_response.js - Static Routes - Doc Processor   - Image Upload
- tech_proposal.js     - Error Handling                  
- point_to_point.js                                     
- word-editor.js                                        
```

## 后端API接口详细规范

### 1. 系统状态与配置接口

#### 1.1 健康检查
- **路径**: `GET /api/health`
- **描述**: 系统健康状态检查
- **响应示例**:
```json
{
  "status": "healthy",
  "version": "2.0.0", 
  "timestamp": "2025-09-11T10:30:00.000Z",
  "tender_info_available": true,
  "point_to_point_available": true
}
```

#### 1.2 获取API配置
- **路径**: `GET /api/config`
- **描述**: 获取系统API配置信息（隐藏敏感信息）
- **响应示例**:
```json
{
  "success": true,
  "config": {
    "api_endpoint": "https://api.deepseek.com/v1/chat/completions",
    "model_name": "deepseek-chat",
    "max_completion_tokens": 4000,
    "has_api_key": true
  }
}
```

#### 1.3 API密钥管理
- **获取默认密钥**: `GET /api/get-default-api-key`
  - 返回前10位API密钥用于验证
- **保存密钥**: `POST /api/save-key`
  - 请求体: `{"api_key": "your_api_key"}`
  - 响应: `{"success": true, "message": "API密钥保存成功"}`

### 2. 文件处理接口

#### 2.1 通用文件上传
- **路径**: `POST /upload`
- **描述**: 支持多种文件类型上传
- **请求参数**:
  - `file`: 文件对象（multipart/form-data）
  - `type`: 文件类型（可选，默认tender_info）
- **响应示例**:
```json
{
  "success": true,
  "filename": "tender_document.pdf",
  "file_path": "/path/to/upload/tender_document.pdf",
  "message": "文件上传成功"
}
```

#### 2.2 文件下载
- **路径**: `GET /download/<filename>`
- **描述**: 从output目录下载生成的文件
- **响应**: 文件流（as_attachment=True）

### 3. 招标信息提取接口

#### 3.1 完整信息提取
- **路径**: `POST /extract-tender-info`
- **描述**: 一次性提取招标文档中的所有信息
- **请求参数**:
  - `file`: 招标文档文件
  - `api_key`: API密钥（可选，优先使用环境变量）
- **响应示例**:
```json
{
  "success": true,
  "data": {
    "tenderer": "某某政府采购中心",
    "agency": "招标代理公司",
    "project_name": "智慧城市建设项目",
    "project_number": "ZB2024-001",
    "bidding_method": "公开招标",
    "bidding_location": "某某市政府",
    "bidding_time": "2024年12月15日 09:00",
    "winner_count": "1",
    "business_license": {
      "required": true,
      "description": "有效营业执照副本"
    },
    "technical_scoring_items": [
      {
        "name": "技术方案完整性",
        "weight": "20分",
        "criteria": "方案完整性和可行性评分",
        "source": "技术评分标准第1条"
      }
    ]
  },
  "message": "招标信息提取成功"
}
```

#### 3.2 分步信息提取
- **路径**: `POST /extract-tender-info-step`
- **描述**: 分步骤提取招标信息
- **请求参数**:
  - `step`: 提取步骤（"1", "2", "3"）
  - `file_path`: 文件路径
  - `api_key`: API密钥
- **步骤说明**:
  - 步骤1：基本信息（项目名称、招标人等）
  - 步骤2：资质要求分析
  - 步骤3：技术评分标准

### 4. 公司管理接口

#### 4.1 公司列表
- **路径**: `GET /api/companies`
- **描述**: 获取所有公司配置
- **响应示例**:
```json
{
  "success": true,
  "companies": [
    {
      "id": "comp001",
      "companyName": "某某科技有限公司",
      "created_at": "2024-09-01T10:00:00",
      "updated_at": "2024-09-10T15:30:00"
    }
  ]
}
```

#### 4.2 公司详细信息
- **路径**: `GET /api/companies/<company_id>`
- **描述**: 获取指定公司的详细信息
- **响应**: 包含完整公司信息的JSON对象

#### 4.3 创建公司
- **路径**: `POST /api/companies`
- **请求体**:
```json
{
  "companyName": "新公司名称",
  "legalRepresentative": "法定代表人",
  "registeredAddress": "注册地址",
  "socialCreditCode": "统一社会信用代码"
}
```

#### 4.4 更新公司
- **路径**: `PUT /api/companies/<company_id>`
- **请求体**: 包含需要更新的字段

#### 4.5 删除公司
- **路径**: `DELETE /api/companies/<company_id>`
- **响应**: `{"success": true, "message": "公司删除成功"}`

### 5. 公司资质文件管理

#### 5.1 获取资质文件列表
- **路径**: `GET /api/companies/<company_id>/qualifications`
- **响应**: 公司所有资质文件信息

#### 5.2 上传资质文件
- **路径**: `POST /api/companies/<company_id>/qualifications/upload`
- **请求**: multipart/form-data，包含多个资质文件
- **参数**:
  - `qualifications[<key>]`: 资质文件
  - `qualification_names`: 自定义资质名称映射（JSON字符串）

#### 5.3 下载资质文件
- **路径**: `GET /api/companies/<company_id>/qualifications/<qualification_key>/download`
- **响应**: 文件流

### 6. 商务应答处理接口

#### 6.1 处理商务应答
- **路径**: `POST /process-business-response`
- **描述**: 基于公司信息和模板生成商务应答文档
- **请求参数**:
  - `file`: 商务应答模板文件
  - `company_name`: 公司名称
  - `company_address`: 公司地址
  - `legal_person`: 法定代表人
  - `contact_info`: 联系信息
- **响应示例**:
```json
{
  "success": true,
  "message": "商务应答处理完成",
  "download_url": "/download/business_response_xxx.docx",
  "filename": "business_response_xxx.docx",
  "processing_steps": {
    "text": {"success": true, "message": "文本替换完成", "count": 15},
    "tables": {"success": true, "message": "表格处理完成", "count": 3},
    "images": {"success": true, "message": "图片插入完成", "count": 5}
  },
  "statistics": {
    "text_replacements": 15,
    "tables_processed": 3,
    "fields_filled": 25,
    "images_inserted": 5
  }
}
```

### 7. 文档与表格处理接口

#### 7.1 文档处理
- **路径**: `POST /api/document/process`
- **请求体**:
```json
{
  "file_path": "/path/to/document",
  "options": {
    "extract_text": true,
    "process_tables": true
  }
}
```

#### 7.2 表格分析
- **路径**: `POST /api/table/analyze`
- **请求体**:
```json
{
  "table_data": {
    "headers": ["列1", "列2"],
    "rows": [["值1", "值2"]]
  }
}
```

#### 7.3 表格处理
- **路径**: `POST /api/table/process`
- **请求体**:
```json
{
  "table_data": {},
  "options": {
    "fill_company_info": true,
    "apply_formatting": true
  }
}
```

### 8. 技术方案生成接口

#### 8.1 生成技术方案
- **路径**: `POST /generate-proposal`
- **描述**: 基于招标文件和产品文档生成技术方案
- **请求参数**:
  - `techTenderFile`: 招标文件
  - `productFile`: 产品文档
- **状态**: 功能正在迁移中
- **响应**: 
```json
{
  "success": false,
  "message": "技术方案生成功能正在迁移中"
}
```

### 9. 商务文件管理

#### 9.1 获取商务文件列表
- **路径**: `GET /api/business-files`
- **描述**: 获取output目录中的商务应答文件列表
- **响应示例**:
```json
{
  "success": true,
  "files": [
    {
      "name": "business_response_20240911.docx",
      "size": 1048576,
      "created": "2024-09-11T10:30:00",
      "modified": "2024-09-11T10:35:00",
      "path": "/path/to/output/business_response_20240911.docx"
    }
  ]
}
```

### 10. 项目配置接口

#### 10.1 获取项目配置
- **路径**: `GET /api/project-config`
- **描述**: 读取招标信息提取模块生成的项目配置
- **响应示例**:
```json
{
  "success": true,
  "projectInfo": {
    "projectName": "智慧城市建设项目",
    "projectNumber": "ZB2024-001",
    "tenderer": "政府采购中心",
    "agency": "招标代理公司",
    "biddingMethod": "公开招标",
    "biddingLocation": "市政府大楼",
    "biddingTime": "2024-12-15 09:00"
  }
}
```

## 前端组件API调用映射

### 1. tender_info.js - 招标信息提取

**主要API调用**:
- `/extract-tender-info` - 完整信息提取
- `/extract-tender-info-step` - 分步提取

**关键函数**:
- `submitTenderExtraction()` - 提交提取任务
- `performStepwiseExtraction()` - 执行分步提取
- `displayBasicInfo()`, `displayQualificationRequirements()`, `displayTechnicalScoring()` - 结果展示

**数据流**:
```
用户上传文件 → 文件验证 → API调用 → 进度显示 → 结果解析 → 分类展示
```

### 2. company_selection.js - 公司管理

**主要API调用**:
- `/api/companies` - CRUD操作
- `/api/companies/<id>/qualifications/*` - 资质管理
- `/api/project-config` - 项目信息

**关键功能**:
- 公司信息表单管理
- 资质文件上传下载
- 表单状态跟踪（FormStateManager）
- 标签切换拦截机制

**状态管理**:
- 使用FormStateManager跟踪未保存更改
- 支持拖拽和粘贴图片上传
- 自动保存状态到StateManager

### 3. business_response.js - 商务应答

**主要API调用**:
- `/process-business-response` - 商务应答处理
- `/api/companies` - 获取公司列表
- `/api/project-config` - 项目信息

**处理流程**:
```
选择模板 → 选择公司 → 填写项目信息 → 提交处理 → 进度跟踪 → 结果下载
```

**特色功能**:
- 处理步骤可视化显示
- 统计信息展示
- 文档预览功能

### 4. point_to_point.js - 点对点应答

**主要API调用**:
- `/upload` - 文件上传处理

**功能特点**:
- 简化的文件处理流程
- 拖拽上传支持
- 进度条显示

### 5. tech_proposal.js - 技术方案

**主要API调用**:
- `/generate-proposal` - 技术方案生成

**当前状态**: 功能正在迁移，API返回占位响应

### 6. word-editor.js - Word编辑器

**主要API调用**:
- `/api/editor/load-document` - 加载Word文档
- `/api/editor/save-document` - 保存为Word文档
- `/api/editor/upload-image` - 图片上传

**特色功能**:
- 集成TinyMCE富文本编辑器
- Word文档导入导出
- 图片粘贴上传
- 实时保存提示

## 通用JavaScript工具库

### common.js - 公共功能

**核心功能**:
- `showNotification()` - 通知显示
- `downloadFile()` - 文件下载
- `setupDragDrop()` - 拖拽上传
- `apiRequest()` - API请求封装
- `enablePasteImageUpload()` - 图片粘贴上传

### state-manager.js - 状态管理

**主要功能**:
- 跨页面状态保持
- localStorage操作封装
- URL参数管理
- 页面间消息传递

**状态键定义**:
```javascript
KEYS: {
  API_KEY: 'ai_tender_api_key_encrypted',
  COMPANY_ID: 'current_company_id', 
  UPLOAD_FILES: 'upload_files_info',
  PAGE_CONTEXT: 'page_context'
}
```

## 外部API集成

### 1. LLM服务集成
- **默认服务**: DeepSeek API
- **端点**: `https://api.deepseek.com/v1/chat/completions`
- **模型**: `deepseek-chat`
- **用途**: 招标信息智能提取
- **认证**: Bearer Token

### 2. 文档处理服务
- **内部实现**: 基于Python-docx等库
- **支持格式**: .docx, .doc, .pdf
- **功能**: 文档读取、解析、生成

### 3. 图片处理服务
- **功能**: 图片上传、格式转换
- **支持格式**: jpg, png, pdf等
- **集成点**: 资质文件上传、编辑器图片

## API使用模式和最佳实践

### 1. 错误处理模式
```javascript
fetch('/api/endpoint')
  .then(response => {
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    return response.json();
  })
  .then(data => {
    if (!data.success) {
      throw new Error(data.error || data.message || '未知错误');
    }
    // 处理成功响应
  })
  .catch(error => {
    console.error('API调用失败:', error);
    showNotification('操作失败: ' + error.message, 'error');
  });
```

### 2. 文件上传模式
```javascript
const formData = new FormData();
formData.append('file', file);
formData.append('company_id', companyId);

fetch('/api/upload-endpoint', {
  method: 'POST',
  body: formData
})
```

### 3. 进度显示模式
```javascript
// 显示进度条
progressBar.style.display = 'block';
const progressInterval = setInterval(() => {
  progress += Math.random() * 15;
  if (progress > 90) progress = 90;
  progressBar.style.width = progress + '%';
}, 200);

// API调用完成后清理
clearInterval(progressInterval);
progressBar.style.width = '100%';
```

### 4. 状态管理模式
```javascript
// 保存状态
StateManager.setCompanyId(companyId);
StateManager.setPageContext({
  tenderInfoExtracted: true,
  extractedData: result
});

// 读取状态
const companyId = StateManager.getCompanyId();
const pageContext = StateManager.getPageContext();
```

## 安全考虑

### 1. API密钥管理
- 环境变量优先
- 前端显示脱敏（仅前10位）
- 加密存储到localStorage

### 2. 文件上传安全
- 文件类型验证
- 文件大小限制
- 安全文件名处理
- 路径遍历防护

### 3. 跨域和CSRF
- CORS配置
- 文件上传使用multipart/form-data
- 状态验证

## 性能优化

### 1. 异步处理
- 长时间操作使用进度条
- 超时控制（默认2分钟）
- 请求取消支持

### 2. 缓存策略
- 公司列表缓存
- 状态管理器本地存储
- 静态资源缓存

### 3. 错误恢复
- 自动重试机制（最多3次）
- 网络错误友好提示
- 状态恢复能力

## API调用流程图

```mermaid
graph TB
    A[用户操作] --> B[前端验证]
    B --> C[构建请求]
    C --> D[发送API请求]
    D --> E[Flask路由处理]
    E --> F[业务逻辑处理]
    F --> G[外部API调用]
    G --> H[结果处理]
    H --> I[响应返回]
    I --> J[前端结果处理]
    J --> K[UI更新]
    
    F --> L[文件处理]
    F --> M[数据库操作]
    L --> H
    M --> H
```

## 常见问题和解决方案

### 1. API密钥问题
- **问题**: 提示"API密钥未配置"
- **解决**: 检查环境变量DEFAULT_API_KEY或在页面中手动设置

### 2. 文件上传失败
- **问题**: 文件上传超时或失败
- **解决**: 检查文件大小（限制10MB）、网络连接、文件格式

### 3. 跨页面状态丢失
- **问题**: 切换页面后选择的公司信息丢失
- **解决**: 使用StateManager保存状态，检查localStorage

### 4. 进度条不显示
- **问题**: 长时间操作没有进度提示
- **解决**: 检查progressBar元素是否存在，确认事件监听正确绑定

## 总结

本API系统采用现代Web架构，提供了完整的招标文档处理能力。主要特点：

1. **完整的REST API设计**：覆盖所有业务功能
2. **智能文档处理**：集成LLM进行信息提取
3. **用户友好的界面**：丰富的交互反馈
4. **健壮的错误处理**：全面的异常捕获和用户提示
5. **灵活的状态管理**：支持跨页面数据保持
6. **安全的文件处理**：完善的文件上传下载机制

开发者可以基于这套API快速构建招标相关的应用功能，系统提供了良好的扩展性和维护性。