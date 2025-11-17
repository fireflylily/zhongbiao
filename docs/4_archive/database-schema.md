# 数据库架构设计

## 📊 概述

本文档详细描述了AI标书系统的数据库架构设计，包括SQLite关系数据库和FAISS向量索引的混合存储方案。

## 🏗️ 整体架构

### 存储分层
```
数据存储层
├── SQLite关系数据库
│   ├── 元数据存储
│   ├── 业务数据管理
│   └── 关系维护
└── FAISS向量索引
    ├── 文档嵌入向量
    ├── 分块内容向量
    └── 语义搜索索引
```

## 📋 SQLite数据库设计

### 核心表结构

#### 1. 产品文档表 (product_documents)
```sql
CREATE TABLE product_documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(255) NOT NULL,                    -- 文档标题
    category ENUM('tech', 'impl', 'service', 'cases') NOT NULL, -- 分类
    subcategory VARCHAR(100),                       -- 子分类
    file_path VARCHAR(500) NOT NULL,                -- 文件路径
    file_type VARCHAR(20) NOT NULL,                 -- 文件类型
    file_size INTEGER,                              -- 文件大小(字节)
    security_level ENUM('public', 'internal', 'confidential', 'secret') DEFAULT 'internal',
    status ENUM('processing', 'active', 'archived', 'error') DEFAULT 'processing',
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),                        -- 上传用户
    tags TEXT,                                      -- 标签(JSON数组)
    description TEXT,                               -- 文档描述
    version VARCHAR(20) DEFAULT '1.0',              -- 版本号
    language VARCHAR(10) DEFAULT 'zh-CN',           -- 语言
    page_count INTEGER,                             -- 页数
    word_count INTEGER,                             -- 字数
    checksum VARCHAR(64),                           -- 文件校验和
    UNIQUE(file_path)
);
```

#### 2. 文档内容块表 (document_chunks)
```sql
CREATE TABLE document_chunks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL,                   -- 关联文档ID
    chunk_index INTEGER NOT NULL,                  -- 分块索引
    content TEXT NOT NULL,                         -- 分块内容
    content_type ENUM('text', 'table', 'image', 'list') DEFAULT 'text',
    page_number INTEGER,                           -- 所在页码
    chunk_size INTEGER,                            -- 分块大小
    chunk_hash VARCHAR(64),                        -- 内容哈希
    vector_id INTEGER,                             -- FAISS向量ID
    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES product_documents(id) ON DELETE CASCADE,
    INDEX idx_document_chunks_doc_id (document_id),
    INDEX idx_document_chunks_vector_id (vector_id)
);
```

#### 3. 文档元数据表 (document_metadata)
```sql
CREATE TABLE document_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL,                  -- 关联文档ID
    key_name VARCHAR(100) NOT NULL,               -- 元数据键名
    key_value TEXT,                               -- 元数据值
    data_type ENUM('string', 'number', 'boolean', 'date', 'json') DEFAULT 'string',
    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES product_documents(id) ON DELETE CASCADE,
    INDEX idx_metadata_doc_key (document_id, key_name)
);
```

#### 4. 搜索日志表 (search_logs)
```sql
CREATE TABLE search_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query_text TEXT NOT NULL,                     -- 搜索查询
    query_type ENUM('vector', 'keyword', 'hybrid') NOT NULL, -- 搜索类型
    result_count INTEGER,                         -- 结果数量
    response_time_ms INTEGER,                     -- 响应时间(毫秒)
    user_id VARCHAR(100),                         -- 用户ID
    session_id VARCHAR(100),                      -- 会话ID
    filters TEXT,                                 -- 过滤条件(JSON)
    search_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_search_logs_time (search_time),
    INDEX idx_search_logs_user (user_id)
);
```

#### 5. 文档标签表 (document_tags)
```sql
CREATE TABLE document_tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tag_name VARCHAR(100) NOT NULL UNIQUE,        -- 标签名称
    tag_description TEXT,                         -- 标签描述
    tag_color VARCHAR(7),                         -- 标签颜色(HEX)
    usage_count INTEGER DEFAULT 0,               -- 使用次数
    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_tags_name (tag_name)
);
```

#### 6. 文档标签关联表 (document_tag_relations)
```sql
CREATE TABLE document_tag_relations (
    document_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (document_id, tag_id),
    FOREIGN KEY (document_id) REFERENCES product_documents(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES document_tags(id) ON DELETE CASCADE
);
```

### 扩展业务表

#### 7. 企业信息表 (companies) - 现有表扩展
```sql
-- 基于现有表结构，添加新字段
ALTER TABLE companies ADD COLUMN doc_access_level INTEGER DEFAULT 1; -- 文档访问级别
ALTER TABLE companies ADD COLUMN preferred_categories TEXT;           -- 偏好文档分类(JSON)
ALTER TABLE companies ADD COLUMN last_doc_access TIMESTAMP;          -- 最后文档访问时间
```

#### 8. 项目管理表 (projects)
```sql
CREATE TABLE projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_name VARCHAR(200) NOT NULL,           -- 项目名称
    project_code VARCHAR(50) UNIQUE,              -- 项目编码
    company_id INTEGER,                           -- 关联企业ID
    description TEXT,                             -- 项目描述
    status ENUM('planning', 'active', 'completed', 'cancelled') DEFAULT 'planning',
    start_date DATE,                              -- 开始日期
    end_date DATE,                                -- 结束日期
    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id),
    INDEX idx_projects_company (company_id)
);
```

#### 9. 项目文档关联表 (project_documents)
```sql
CREATE TABLE project_documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,                 -- 项目ID
    document_id INTEGER NOT NULL,                -- 文档ID
    usage_type ENUM('reference', 'template', 'output') NOT NULL, -- 使用类型
    added_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (project_id, document_id),
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (document_id) REFERENCES product_documents(id) ON DELETE CASCADE
);
```

## 🔍 FAISS向量索引设计

### 向量存储结构
```python
# 向量索引配置
VECTOR_CONFIGS = {
    'dimension': 384,                    # sentence-transformers维度
    'index_type': 'IndexFlatIP',        # 内积距离索引
    'metric_type': 'METRIC_INNER_PRODUCT', # 内积相似度
    'nlist': 100,                       # 聚类中心数量
    'nprobe': 10,                       # 搜索聚类数量
    'storage_path': 'data/vector_indexes/'
}
```

### 向量文件组织
```
data/vector_indexes/
├── documents.index                     # 文档级向量索引
├── chunks.index                        # 分块级向量索引
├── metadata.json                       # 索引元数据
├── id_mapping.json                     # ID映射关系
└── backup/                            # 备份目录
    ├── documents_20250927.index
    └── chunks_20250927.index
```

### 向量ID映射
```json
{
  "documents": {
    "faiss_id_0": {"db_id": 1, "doc_title": "产品技术规格书"},
    "faiss_id_1": {"db_id": 2, "doc_title": "实施方案模板"}
  },
  "chunks": {
    "faiss_id_0": {"db_id": 1, "chunk_index": 0, "doc_id": 1},
    "faiss_id_1": {"db_id": 2, "chunk_index": 0, "doc_id": 1}
  }
}
```

## 📈 性能优化设计

### 索引策略
```sql
-- 文档搜索优化
CREATE INDEX idx_docs_category_status ON product_documents(category, status);
CREATE INDEX idx_docs_upload_time ON product_documents(upload_time DESC);
CREATE INDEX idx_docs_security_level ON product_documents(security_level);
CREATE INDEX idx_docs_full_text ON product_documents(title, description);

-- 分块搜索优化
CREATE INDEX idx_chunks_content_type ON document_chunks(content_type);
CREATE INDEX idx_chunks_size ON document_chunks(chunk_size);

-- 元数据搜索优化
CREATE INDEX idx_metadata_composite ON document_metadata(key_name, key_value);

-- 搜索日志分析
CREATE INDEX idx_search_performance ON search_logs(query_type, response_time_ms);
```

### 分区策略
```sql
-- 按时间分区存储大量日志数据
CREATE TABLE search_logs_202509 AS SELECT * FROM search_logs WHERE search_time >= '2025-09-01' AND search_time < '2025-10-01';
CREATE TABLE search_logs_202510 AS SELECT * FROM search_logs WHERE search_time >= '2025-10-01' AND search_time < '2025-11-01';
```

## 🔒 安全和权限设计

### 数据安全分级
```sql
-- 安全级别枚举值含义
-- 'public': 公开文档，所有用户可访问
-- 'internal': 内部文档，授权用户可访问
-- 'confidential': 机密文档，高级权限用户可访问
-- 'secret': 绝密文档，特定用户可访问

-- 用户访问控制表
CREATE TABLE user_document_permissions (
    user_id VARCHAR(100) NOT NULL,
    document_id INTEGER NOT NULL,
    permission_type ENUM('read', 'write', 'delete') NOT NULL,
    granted_by VARCHAR(100),
    granted_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    PRIMARY KEY (user_id, document_id, permission_type),
    FOREIGN KEY (document_id) REFERENCES product_documents(id) ON DELETE CASCADE
);
```

### 审计日志
```sql
CREATE TABLE audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id VARCHAR(100) NOT NULL,
    action_type ENUM('upload', 'download', 'delete', 'search', 'view') NOT NULL,
    resource_type ENUM('document', 'chunk', 'index') NOT NULL,
    resource_id INTEGER,
    action_details TEXT,                   -- JSON格式详细信息
    ip_address VARCHAR(45),               -- IPv4/IPv6地址
    user_agent TEXT,                      -- 用户代理信息
    action_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_audit_user_time (user_id, action_time),
    INDEX idx_audit_action_type (action_type)
);
```

## 🔄 数据同步和备份

### 自动备份策略
```sql
-- 创建备份作业表
CREATE TABLE backup_jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_name VARCHAR(100) NOT NULL,
    backup_type ENUM('full', 'incremental', 'vector_only') NOT NULL,
    schedule_cron VARCHAR(50),            -- Cron表达式
    last_run_time TIMESTAMP,
    next_run_time TIMESTAMP,
    status ENUM('active', 'paused', 'failed') DEFAULT 'active',
    backup_path VARCHAR(500),
    retention_days INTEGER DEFAULT 30,
    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 数据一致性维护
```sql
-- 向量索引同步状态表
CREATE TABLE vector_sync_status (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL,
    last_vector_update TIMESTAMP,
    vector_count INTEGER,
    sync_status ENUM('synced', 'pending', 'error') DEFAULT 'pending',
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    FOREIGN KEY (document_id) REFERENCES product_documents(id),
    INDEX idx_sync_status (sync_status)
);
```

## 📊 统计和分析表

### 使用统计
```sql
CREATE TABLE usage_statistics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stat_date DATE NOT NULL,
    document_uploads INTEGER DEFAULT 0,
    searches_performed INTEGER DEFAULT 0,
    unique_users INTEGER DEFAULT 0,
    avg_response_time_ms FLOAT,
    total_storage_mb FLOAT,
    vector_index_size_mb FLOAT,
    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(stat_date)
);
```

### 文档热度分析
```sql
CREATE TABLE document_popularity (
    document_id INTEGER NOT NULL,
    view_count INTEGER DEFAULT 0,
    download_count INTEGER DEFAULT 0,
    search_hit_count INTEGER DEFAULT 0,
    last_accessed TIMESTAMP,
    popularity_score FLOAT,              -- 综合热度评分
    updated_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (document_id),
    FOREIGN KEY (document_id) REFERENCES product_documents(id) ON DELETE CASCADE
);
```

## 🚀 初始化脚本

### 数据库初始化
```sql
-- 创建初始数据
INSERT INTO document_tags (tag_name, tag_description, tag_color) VALUES
('核心产品', '公司核心产品相关文档', '#FF6B6B'),
('技术规格', '产品技术规格和参数', '#4ECDC4'),
('实施指南', '产品实施和部署指南', '#45B7D1'),
('客户案例', '成功客户案例和经验', '#96CEB4'),
('服务支持', '售后服务和技术支持', '#FFEAA7');

-- 创建默认项目
INSERT INTO projects (project_name, project_code, description, status) VALUES
('默认项目', 'DEFAULT', '系统默认项目，用于通用文档管理', 'active');

-- 初始化统计表
INSERT INTO usage_statistics (stat_date, document_uploads, searches_performed, unique_users)
VALUES (DATE('now'), 0, 0, 0);
```

## 🔧 维护操作

### 定期清理
```sql
-- 清理过期搜索日志
DELETE FROM search_logs WHERE search_time < datetime('now', '-90 days');

-- 清理未使用的标签
DELETE FROM document_tags WHERE usage_count = 0 AND created_time < datetime('now', '-30 days');

-- 更新文档热度评分
UPDATE document_popularity SET popularity_score =
    (view_count * 1.0 + download_count * 2.0 + search_hit_count * 0.5) /
    (julianday('now') - julianday(last_accessed) + 1);
```

### 数据完整性检查
```sql
-- 检查孤立的文档块
SELECT c.* FROM document_chunks c
LEFT JOIN product_documents d ON c.document_id = d.id
WHERE d.id IS NULL;

-- 检查缺失的向量索引
SELECT d.* FROM product_documents d
LEFT JOIN document_chunks c ON d.id = c.document_id
WHERE d.status = 'active' AND c.id IS NULL;
```

---

**维护状态**: 🟢 积极维护中
**最后更新**: 2025年9月27日
**版本**: v1.0