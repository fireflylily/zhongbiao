# API接口设计规范

## 📋 概述

本文档详细描述了AI标书系统的RESTful API接口设计，包括产品文档管理、向量搜索、企业管理等核心功能的API规范。

## 🌐 API设计原则

### 1. RESTful规范
- 使用HTTP动词表示操作：GET（查询）、POST（创建）、PUT（更新）、DELETE（删除）
- 使用名词表示资源，避免动词
- 使用HTTP状态码表示操作结果
- 支持JSON格式数据交换

### 2. 统一响应格式
```json
{
    "success": true,
    "code": 200,
    "message": "操作成功",
    "data": {},
    "timestamp": "2025-09-27T10:30:00Z",
    "trace_id": "abc123-def456-ghi789"
}
```

### 3. 错误处理
```json
{
    "success": false,
    "code": 400,
    "message": "请求参数错误",
    "error": {
        "type": "ValidationError",
        "details": "title字段不能为空"
    },
    "timestamp": "2025-09-27T10:30:00Z",
    "trace_id": "abc123-def456-ghi789"
}
```

## 📁 产品文档管理API

### 1. 文档上传

#### 上传单个文档
```http
POST /api/documents
Content-Type: multipart/form-data

form-data:
- file: [文件]
- title: "产品技术规格书"
- category: "tech"
- subcategory: "hardware"
- description: "详细的硬件技术规格说明"
- tags: ["核心产品", "技术规格"]
- security_level: "internal"
```

**响应示例:**
```json
{
    "success": true,
    "code": 201,
    "message": "文档上传成功",
    "data": {
        "document_id": 123,
        "title": "产品技术规格书",
        "category": "tech",
        "file_path": "/uploads/documents/123_tech_spec.pdf",
        "status": "processing",
        "upload_time": "2025-09-27T10:30:00Z"
    }
}
```

#### 批量上传文档
```http
POST /api/documents/batch
Content-Type: multipart/form-data

form-data:
- files: [文件数组]
- metadata: [
    {
        "filename": "spec1.pdf",
        "title": "规格书1",
        "category": "tech"
    },
    {
        "filename": "guide1.docx",
        "title": "实施指南1",
        "category": "impl"
    }
]
```

### 2. 文档查询

#### 获取文档列表
```http
GET /api/documents?page=1&size=20&category=tech&status=active&tags=核心产品
```

**查询参数:**
- `page`: 页码，默认1
- `size`: 每页数量，默认20，最大100
- `category`: 文档分类过滤
- `subcategory`: 子分类过滤
- `status`: 状态过滤（processing, active, archived, error）
- `security_level`: 安全级别过滤
- `tags`: 标签过滤，支持多个
- `created_after`: 创建时间过滤（开始）
- `created_before`: 创建时间过滤（结束）
- `sort`: 排序字段（upload_time, title, file_size）
- `order`: 排序方向（asc, desc）

**响应示例:**
```json
{
    "success": true,
    "data": {
        "documents": [
            {
                "id": 123,
                "title": "产品技术规格书",
                "category": "tech",
                "subcategory": "hardware",
                "file_type": "pdf",
                "file_size": 2048576,
                "security_level": "internal",
                "status": "active",
                "upload_time": "2025-09-27T10:30:00Z",
                "tags": ["核心产品", "技术规格"],
                "description": "详细的硬件技术规格说明",
                "page_count": 25,
                "word_count": 5680
            }
        ],
        "pagination": {
            "page": 1,
            "size": 20,
            "total": 156,
            "pages": 8
        }
    }
}
```

#### 获取文档详情
```http
GET /api/documents/{document_id}
```

**响应示例:**
```json
{
    "success": true,
    "data": {
        "id": 123,
        "title": "产品技术规格书",
        "category": "tech",
        "subcategory": "hardware",
        "file_path": "/uploads/documents/123_tech_spec.pdf",
        "file_type": "pdf",
        "file_size": 2048576,
        "security_level": "internal",
        "status": "active",
        "upload_time": "2025-09-27T10:30:00Z",
        "last_updated": "2025-09-27T10:30:00Z",
        "created_by": "admin",
        "tags": ["核心产品", "技术规格"],
        "description": "详细的硬件技术规格说明",
        "version": "1.0",
        "language": "zh-CN",
        "page_count": 25,
        "word_count": 5680,
        "checksum": "sha256:abc123...",
        "chunks": [
            {
                "id": 456,
                "chunk_index": 0,
                "content": "第一章 产品概述...",
                "content_type": "text",
                "page_number": 1,
                "chunk_size": 512
            }
        ],
        "metadata": {
            "author": "技术部",
            "created_date": "2025-09-20",
            "department": "研发中心"
        }
    }
}
```

### 3. 文档更新

#### 更新文档信息
```http
PUT /api/documents/{document_id}
Content-Type: application/json

{
    "title": "更新后的标题",
    "description": "更新后的描述",
    "tags": ["新标签1", "新标签2"],
    "security_level": "confidential"
}
```

#### 替换文档文件
```http
PUT /api/documents/{document_id}/file
Content-Type: multipart/form-data

form-data:
- file: [新文件]
- version: "2.0"
```

### 4. 文档删除

#### 删除单个文档
```http
DELETE /api/documents/{document_id}
```

#### 批量删除文档
```http
DELETE /api/documents/batch
Content-Type: application/json

{
    "document_ids": [123, 456, 789]
}
```

## 🔍 搜索API

### 1. 文档搜索

#### 混合搜索
```http
POST /api/search
Content-Type: application/json

{
    "query": "云计算解决方案",
    "search_type": "hybrid",
    "k": 10,
    "filters": {
        "category": ["tech", "impl"],
        "security_level": ["public", "internal"],
        "tags": ["云计算"],
        "date_range": {
            "start": "2025-01-01",
            "end": "2025-09-27"
        }
    },
    "highlight": true,
    "explain": false
}
```

**请求参数:**
- `query`: 搜索查询字符串（必需）
- `search_type`: 搜索类型（hybrid, vector, keyword）
- `k`: 返回结果数量，默认10，最大100
- `filters`: 过滤条件
- `highlight`: 是否高亮显示匹配内容
- `explain`: 是否返回搜索解释信息

**响应示例:**
```json
{
    "success": true,
    "data": {
        "query": "云计算解决方案",
        "search_type": "hybrid",
        "total": 15,
        "search_time_ms": 85,
        "results": [
            {
                "document_id": 123,
                "title": "企业云计算解决方案",
                "category": "tech",
                "subcategory": "cloud",
                "description": "完整的企业级云计算解决方案",
                "score": {
                    "final": 0.92,
                    "vector": 0.89,
                    "keyword": 0.95
                },
                "highlights": [
                    "企业级<em>云计算</em><em>解决方案</em>提供完整的服务体系",
                    "基于Docker容器的<em>云计算</em>架构设计"
                ],
                "chunks": [
                    {
                        "id": 456,
                        "content": "云计算解决方案概述...",
                        "score": 0.88,
                        "page_number": 1
                    }
                ]
            }
        ],
        "aggregations": {
            "categories": {
                "tech": 8,
                "impl": 5,
                "service": 2
            },
            "security_levels": {
                "public": 10,
                "internal": 5
            }
        }
    }
}
```

#### 向量相似搜索
```http
POST /api/search/similar
Content-Type: application/json

{
    "document_id": 123,
    "k": 10,
    "exclude_self": true
}
```

#### 搜索建议
```http
GET /api/search/suggest?q=云计算&limit=10
```

**响应示例:**
```json
{
    "success": true,
    "data": {
        "suggestions": [
            "云计算解决方案",
            "云计算架构设计",
            "云计算安全方案",
            "混合云部署"
        ]
    }
}
```

### 2. 搜索分析

#### 搜索统计
```http
GET /api/search/analytics?period=7d
```

**响应示例:**
```json
{
    "success": true,
    "data": {
        "period": "7d",
        "total_searches": 1256,
        "unique_queries": 458,
        "avg_response_time_ms": 125,
        "popular_queries": [
            {"query": "云计算", "count": 45},
            {"query": "AI解决方案", "count": 32}
        ],
        "zero_result_queries": [
            {"query": "区块链实施", "count": 8}
        ],
        "category_distribution": {
            "tech": 45.2,
            "impl": 32.1,
            "service": 15.8,
            "cases": 6.9
        }
    }
}
```

## 🏢 企业管理API

### 1. 企业信息

#### 获取企业列表
```http
GET /api/companies?page=1&size=20&status=active
```

#### 获取企业详情
```http
GET /api/companies/{company_id}
```

#### 创建企业
```http
POST /api/companies
Content-Type: application/json

{
    "name": "北京科技有限公司",
    "code": "BJ001",
    "contact_person": "张三",
    "contact_phone": "13800138000",
    "contact_email": "zhangsan@company.com",
    "address": "北京市朝阳区...",
    "business_scope": "软件开发",
    "doc_access_level": 2
}
```

### 2. 企业资质管理

#### 获取企业资质
```http
GET /api/companies/{company_id}/qualifications
```

#### 上传资质文件
```http
POST /api/companies/{company_id}/qualifications
Content-Type: multipart/form-data

form-data:
- qualification_type: "business_license"
- file: [文件]
- description: "营业执照"
```

## 📊 项目管理API

### 1. 项目信息

#### 创建项目
```http
POST /api/projects
Content-Type: application/json

{
    "project_name": "智慧城市项目",
    "project_code": "SC2025001",
    "company_id": 123,
    "description": "智慧城市综合解决方案项目",
    "start_date": "2025-10-01",
    "end_date": "2025-12-31"
}
```

#### 关联文档到项目
```http
POST /api/projects/{project_id}/documents
Content-Type: application/json

{
    "document_ids": [123, 456, 789],
    "usage_type": "reference"
}
```

### 2. 项目文档生成

#### 生成标书文档
```http
POST /api/projects/{project_id}/generate-document
Content-Type: application/json

{
    "template_type": "technical_proposal",
    "requirements": {
        "technical_specs": "云计算平台技术要求",
        "implementation_plan": "分三阶段实施",
        "service_level": "7x24小时支持"
    },
    "reference_documents": [123, 456],
    "output_format": "pdf"
}
```

## 📈 统计分析API

### 1. 系统统计

#### 获取系统概览
```http
GET /api/analytics/overview
```

**响应示例:**
```json
{
    "success": true,
    "data": {
        "documents": {
            "total": 1568,
            "by_category": {
                "tech": 456,
                "impl": 387,
                "service": 298,
                "cases": 427
            },
            "by_status": {
                "active": 1450,
                "processing": 65,
                "archived": 48,
                "error": 5
            }
        },
        "storage": {
            "total_size_mb": 15680.5,
            "vector_index_size_mb": 1250.8
        },
        "usage": {
            "searches_today": 256,
            "uploads_today": 12,
            "active_users": 45
        }
    }
}
```

### 2. 使用分析

#### 获取使用趋势
```http
GET /api/analytics/usage?period=30d&metric=searches
```

## 🔧 系统管理API

### 1. 健康检查

#### 系统健康状态
```http
GET /api/health
```

**响应示例:**
```json
{
    "success": true,
    "data": {
        "status": "healthy",
        "timestamp": "2025-09-27T10:30:00Z",
        "components": {
            "database": {
                "status": "healthy",
                "response_time_ms": 12
            },
            "vector_index": {
                "status": "healthy",
                "index_size": 1568,
                "response_time_ms": 25
            },
            "storage": {
                "status": "healthy",
                "available_space_gb": 450.5
            }
        }
    }
}
```

### 2. 配置管理

#### 获取系统配置
```http
GET /api/admin/config
```

#### 更新系统配置
```http
PUT /api/admin/config
Content-Type: application/json

{
    "search": {
        "max_results": 100,
        "default_search_type": "hybrid"
    },
    "upload": {
        "max_file_size_mb": 50,
        "allowed_types": [".pdf", ".docx", ".pptx", ".xlsx"]
    }
}
```

## 🔐 认证和授权

### 1. 认证方式

#### API Key认证
```http
GET /api/documents
Authorization: Bearer your-api-key-here
```

#### JWT Token认证
```http
POST /api/auth/login
Content-Type: application/json

{
    "username": "admin",
    "password": "password123"
}
```

**响应:**
```json
{
    "success": true,
    "data": {
        "access_token": "eyJhbGciOiJIUzI1NiIs...",
        "refresh_token": "dGhpcyBpcyBhIHJlZnJlc2g...",
        "expires_in": 3600,
        "user": {
            "id": 1,
            "username": "admin",
            "role": "administrator"
        }
    }
}
```

### 2. 权限控制

#### 角色权限
- `administrator`: 所有权限
- `manager`: 文档管理、企业管理
- `operator`: 文档上传、搜索
- `viewer`: 仅查看和搜索

#### 资源访问控制
- 基于安全级别的文档访问
- 基于企业归属的数据隔离
- 基于项目的资源访问

## 📝 API版本管理

### 版本策略
- URL版本控制：`/api/v1/documents`
- Header版本控制：`API-Version: v1`
- 向后兼容：保持旧版本至少6个月

### 版本变更
- v1.0: 基础功能API
- v1.1: 增加批量操作支持
- v1.2: 增加高级搜索功能
- v2.0: 重构搜索API（不兼容更新）

---

**维护状态**: 🟢 积极维护中
**最后更新**: 2025年9月27日
**版本**: v1.0