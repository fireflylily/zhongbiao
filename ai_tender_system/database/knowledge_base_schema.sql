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

    -- 基本信息
    establish_date DATE, -- 成立日期
    legal_representative VARCHAR(100), -- 法定代表人
    legal_representative_position VARCHAR(100), -- 法定代表人职务
    social_credit_code VARCHAR(50), -- 统一社会信用代码
    registered_capital VARCHAR(100), -- 注册资本
    company_type VARCHAR(100), -- 公司类型
    registered_address TEXT, -- 注册地址
    business_scope TEXT, -- 经营范围

    -- 联系信息
    fixed_phone VARCHAR(50), -- 固定电话
    fax VARCHAR(50), -- 传真
    postal_code VARCHAR(20), -- 邮编
    email VARCHAR(255), -- 电子邮箱
    office_address TEXT, -- 办公地址

    -- 规模信息
    employee_count INTEGER, -- 员工人数规模

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
    privacy_level INTEGER DEFAULT 1, -- 1:公开🌐 2:内部🏢 3:机密🔒 4:绝密🚫
    is_shared BOOLEAN DEFAULT FALSE,
    share_scope VARCHAR(50), -- company/category/custom
    share_products TEXT, -- JSON数组: 共享的产品ID列表
    access_control_enabled BOOLEAN DEFAULT TRUE, -- 是否启用访问控制
    auto_classification BOOLEAN DEFAULT TRUE, -- 是否自动分类文档
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
    privacy_classification INTEGER DEFAULT 1, -- 1:公开🌐 2:内部🏢 3:机密🔒 4:绝密🚫
    access_roles TEXT, -- JSON数组: 访问角色列表
    tags TEXT, -- JSON数组: 文档标签
    metadata TEXT, -- JSON: 文档元数据
    document_category VARCHAR(50) DEFAULT 'tech', -- tech:技术🔧 impl:实施📋 service:服务🛠️
    applicable_products TEXT, -- JSON数组: 适用产品ID列表
    security_classification VARCHAR(20) DEFAULT 'normal', -- normal/confidential/secret/top_secret

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

-- 注意：初始数据插入已移至单独的数据初始化脚本
-- 此架构文件仅包含表结构定义，避免重复执行时插入重复数据

-- 9. 用户角色表
CREATE TABLE IF NOT EXISTS user_roles (
    role_id INTEGER PRIMARY KEY AUTOINCREMENT,
    role_name VARCHAR(50) NOT NULL UNIQUE,
    role_description TEXT,
    privacy_level_access INTEGER DEFAULT 1, -- 最高可访问隐私级别
    can_upload BOOLEAN DEFAULT FALSE,
    can_delete BOOLEAN DEFAULT FALSE,
    can_modify_privacy BOOLEAN DEFAULT FALSE,
    can_manage_users BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 10. 用户表
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(255),
    role_id INTEGER NOT NULL,
    company_id INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES user_roles(role_id),
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);

-- 11. 文档访问权限表
CREATE TABLE IF NOT EXISTS document_permissions (
    permission_id INTEGER PRIMARY KEY AUTOINCREMENT,
    doc_id INTEGER NOT NULL,
    user_id INTEGER,
    role_id INTEGER,
    permission_type VARCHAR(20) NOT NULL, -- read/download/modify/delete
    granted_by INTEGER, -- 授权人user_id
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (doc_id) REFERENCES documents(doc_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (role_id) REFERENCES user_roles(role_id),
    FOREIGN KEY (granted_by) REFERENCES users(user_id)
);

-- 注意：默认用户角色和系统配置数据已移至单独的数据初始化脚本

-- 12. 招标项目表
CREATE TABLE IF NOT EXISTS tender_projects (
    project_id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_name VARCHAR(255),
    project_number VARCHAR(100),
    tenderer VARCHAR(255), -- 招标方
    agency VARCHAR(255), -- 代理机构
    bidding_method VARCHAR(100), -- 招标方式
    bidding_location VARCHAR(255), -- 招标地点
    bidding_time VARCHAR(100), -- 招标时间
    tender_document_path VARCHAR(500), -- 标书文件路径
    original_filename VARCHAR(255), -- 原始文件名
    company_id INTEGER, -- 关联公司ID
    status VARCHAR(20) DEFAULT 'draft', -- draft/active/completed
    created_by VARCHAR(100) DEFAULT 'system',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(company_id),
    UNIQUE(company_id, project_name, project_number) -- 防止同一公司创建重复项目
);

CREATE INDEX IF NOT EXISTS idx_tender_projects_company ON tender_projects(company_id);
CREATE INDEX IF NOT EXISTS idx_tender_projects_status ON tender_projects(status);

