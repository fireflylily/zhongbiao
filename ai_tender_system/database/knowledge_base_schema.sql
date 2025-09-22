-- AI标书系统知识库数据库表结构
-- 创建时间: 2024-09-22
-- 描述: 企业信息库和产品知识库管理系统

-- 1. 公司信息表
CREATE TABLE IF NOT EXISTS companies (
    company_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_name VARCHAR(255) NOT NULL UNIQUE,
    company_code VARCHAR(50) UNIQUE,
    industry_type VARCHAR(100),
    description TEXT,
    security_level INTEGER DEFAULT 1, -- 1:普通 2:保密 3:机密
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. 企业信息库表
CREATE TABLE IF NOT EXISTS company_profiles (
    profile_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    profile_type VARCHAR(50) NOT NULL, -- basic/qualification/personnel/financial
    profile_name VARCHAR(255) NOT NULL,
    description TEXT,
    privacy_level INTEGER DEFAULT 1, -- 1:公开 2:内部 3:机密 4:绝密
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);

-- 3. 产品信息表
CREATE TABLE IF NOT EXISTS products (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    product_code VARCHAR(50),
    product_category VARCHAR(100), -- communication/cloud/bigdata
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(company_id),
    UNIQUE(company_id, product_code)
);

-- 4. 文档库表
CREATE TABLE IF NOT EXISTS document_libraries (
    library_id INTEGER PRIMARY KEY AUTOINCREMENT,
    owner_type VARCHAR(20) NOT NULL, -- product/company_profile
    owner_id INTEGER NOT NULL, -- product_id 或 profile_id
    library_name VARCHAR(255) NOT NULL,
    library_type VARCHAR(50) NOT NULL, -- tech/impl/service/qualification/personnel/financial
    privacy_level INTEGER DEFAULT 1,
    is_shared BOOLEAN DEFAULT FALSE,
    share_scope VARCHAR(50), -- company/category/custom
    share_products TEXT, -- JSON数组: 共享的产品ID列表
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. 文档表
CREATE TABLE IF NOT EXISTS documents (
    doc_id INTEGER PRIMARY KEY AUTOINCREMENT,
    library_id INTEGER NOT NULL,
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_type VARCHAR(20) NOT NULL, -- pdf/doc/docx
    file_size INTEGER,
    privacy_classification INTEGER DEFAULT 1, -- 隐私级别
    access_roles TEXT, -- JSON数组: 访问角色列表
    tags TEXT, -- JSON数组: 文档标签
    metadata TEXT, -- JSON: 文档元数据

    -- 处理状态
    upload_status VARCHAR(20) DEFAULT 'uploaded', -- uploaded/processing/completed/failed
    parse_status VARCHAR(20) DEFAULT 'pending', -- pending/parsing/completed/failed
    vector_status VARCHAR(20) DEFAULT 'pending', -- pending/processing/completed/failed

    -- 加密和安全
    encryption_required BOOLEAN DEFAULT FALSE,
    encryption_status VARCHAR(20) DEFAULT 'none', -- none/encrypted
    audit_required BOOLEAN DEFAULT FALSE,

    -- 时间戳
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    parsed_at TIMESTAMP NULL,
    vectorized_at TIMESTAMP NULL,
    last_accessed TIMESTAMP NULL,

    FOREIGN KEY (library_id) REFERENCES document_libraries(library_id)
);

-- 6. 文档分块表 (用于向量检索)
CREATE TABLE IF NOT EXISTS document_chunks (
    chunk_id INTEGER PRIMARY KEY AUTOINCREMENT,
    doc_id INTEGER NOT NULL,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    content_type VARCHAR(50), -- text/table/image
    page_number INTEGER,
    position_info TEXT, -- JSON: 在文档中的位置信息
    vector_embedding BLOB, -- 向量嵌入 (序列化后的numpy数组)
    metadata TEXT, -- JSON: 分块元数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (doc_id) REFERENCES documents(doc_id),
    UNIQUE(doc_id, chunk_index)
);

-- 7. 访问审计日志表
CREATE TABLE IF NOT EXISTS access_audit_logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id VARCHAR(100), -- 用户标识
    user_role VARCHAR(50), -- 用户角色
    action_type VARCHAR(50) NOT NULL, -- view/download/upload/delete/modify
    resource_type VARCHAR(50) NOT NULL, -- document/library/profile
    resource_id INTEGER NOT NULL,
    privacy_level INTEGER,
    access_granted BOOLEAN,
    access_reason TEXT,
    ip_address VARCHAR(45),
    user_agent TEXT,
    session_id VARCHAR(100),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 8. 系统配置表
CREATE TABLE IF NOT EXISTS knowledge_base_configs (
    config_id INTEGER PRIMARY KEY AUTOINCREMENT,
    config_key VARCHAR(100) NOT NULL UNIQUE,
    config_value TEXT,
    config_type VARCHAR(20) DEFAULT 'string', -- string/json/integer/boolean
    description TEXT,
    is_sensitive BOOLEAN DEFAULT FALSE,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引优化查询性能
CREATE INDEX IF NOT EXISTS idx_companies_name ON companies(company_name);
CREATE INDEX IF NOT EXISTS idx_products_company ON products(company_id);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(product_category);
CREATE INDEX IF NOT EXISTS idx_libraries_owner ON document_libraries(owner_type, owner_id);
CREATE INDEX IF NOT EXISTS idx_libraries_type ON document_libraries(library_type);
CREATE INDEX IF NOT EXISTS idx_documents_library ON documents(library_id);
CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(parse_status, vector_status);
CREATE INDEX IF NOT EXISTS idx_documents_privacy ON documents(privacy_classification);
CREATE INDEX IF NOT EXISTS idx_chunks_doc ON document_chunks(doc_id);
CREATE INDEX IF NOT EXISTS idx_audit_user ON access_audit_logs(user_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_resource ON access_audit_logs(resource_type, resource_id);

-- 插入初始数据
INSERT OR IGNORE INTO companies (company_name, company_code, industry_type, description) VALUES
('中国联合网络通信有限公司', 'UNICOM', 'telecommunications', '中国领先的综合通信服务提供商');

INSERT OR IGNORE INTO company_profiles (company_id, profile_type, profile_name, description, privacy_level) VALUES
(1, 'basic', '基础信息', '公司基本信息和对外资料', 1),
(1, 'qualification', '资质证书', '各类业务资质和认证证书', 2),
(1, 'personnel', '人员信息', '员工信息和人力资源资料', 3),
(1, 'financial', '财务文档', '财务报告和审计资料', 4);

INSERT OR IGNORE INTO products (company_id, product_name, product_code, product_category, description) VALUES
(1, '5G核心网产品', '5G_CORE', 'communication', '5G核心网解决方案'),
(1, '云计算平台', 'CLOUD_PLATFORM', 'cloud', '企业级云计算服务平台'),
(1, '大数据平台', 'BIG_DATA', 'bigdata', '大数据分析和处理平台');

-- 插入系统配置
INSERT OR IGNORE INTO knowledge_base_configs (config_key, config_value, config_type, description) VALUES
('max_file_size', '100', 'integer', '文档上传最大大小(MB)'),
('supported_file_types', '["pdf", "doc", "docx"]', 'json', '支持的文件类型'),
('vector_model_name', 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2', 'string', '向量化模型名称'),
('chunk_size', '1000', 'integer', '文档分块大小'),
('chunk_overlap', '200', 'integer', '分块重叠大小'),
('privacy_retention_days', '2555', 'integer', '隐私文档保留天数(7年)'),
('audit_log_retention_days', '2555', 'integer', '审计日志保留天数(7年)');

COMMIT;