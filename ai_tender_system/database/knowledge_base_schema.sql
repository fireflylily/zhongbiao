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
    legal_representative_gender VARCHAR(10), -- 法定代表人性别
    legal_representative_age INTEGER, -- 法定代表人年龄
    social_credit_code VARCHAR(50), -- 统一社会信用代码
    registered_capital VARCHAR(100), -- 注册资本
    company_type VARCHAR(100), -- 公司类型
    registered_address TEXT, -- 注册地址
    business_scope TEXT, -- 经营范围

    -- 被授权人信息
    authorized_person_name VARCHAR(100), -- 被授权人姓名
    authorized_person_id VARCHAR(18), -- 被授权人身份证号
    authorized_person_gender VARCHAR(10), -- 被授权人性别
    authorized_person_position VARCHAR(100), -- 被授权人职位
    authorized_person_title VARCHAR(100), -- 被授权人职称
    authorized_person_age INTEGER, -- 被授权人年龄

    -- 联系信息
    fixed_phone VARCHAR(50), -- 固定电话
    fax VARCHAR(50), -- 传真
    postal_code VARCHAR(20), -- 邮编
    email VARCHAR(255), -- 电子邮箱
    office_address TEXT, -- 办公地址

    -- 规模信息
    employee_count INTEGER, -- 员工人数规模

    -- 财务信息
    bank_name VARCHAR(255), -- 开户银行
    bank_account VARCHAR(100), -- 银行账号

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
    qualifications_data TEXT, -- 资质要求数据(JSON格式)
    scoring_data TEXT, -- 评分信息数据(JSON格式)
    winner_count VARCHAR(50), -- 中标人数量
    authorized_person_name VARCHAR(100), -- 被授权人姓名
    authorized_person_id VARCHAR(18), -- 被授权人身份证号
    authorized_person_position VARCHAR(100), -- 被授权人职位
    status VARCHAR(20) DEFAULT 'draft', -- draft/active/completed
    created_by VARCHAR(100) DEFAULT 'system',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(company_id),
    UNIQUE(company_id, project_name, project_number) -- 防止同一公司创建重复项目
);

CREATE INDEX IF NOT EXISTS idx_tender_projects_company ON tender_projects(company_id);
CREATE INDEX IF NOT EXISTS idx_tender_projects_status ON tender_projects(status);

-- 13. 文档目录表 (Table of Contents)
CREATE TABLE IF NOT EXISTS document_toc (
    toc_id INTEGER PRIMARY KEY AUTOINCREMENT,
    doc_id INTEGER NOT NULL,                    -- 关联文档ID
    heading_level INTEGER NOT NULL,             -- 标题级别(1/2/3/4)
    heading_text TEXT NOT NULL,                 -- 标题完整文本
    section_number VARCHAR(50),                 -- 章节号(如"3.1.101"、"第一章")
    keywords TEXT,                              -- JSON数组:提取的关键词(接口编号、产品名等)
    page_number INTEGER,                        -- 页码
    parent_toc_id INTEGER,                      -- 父级目录ID(构建树形结构)
    sequence_order INTEGER,                     -- 在文档中的顺序
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (doc_id) REFERENCES documents(doc_id) ON DELETE CASCADE,
    FOREIGN KEY (parent_toc_id) REFERENCES document_toc(toc_id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_toc_doc ON document_toc(doc_id);
CREATE INDEX IF NOT EXISTS idx_toc_heading_text ON document_toc(heading_text);
CREATE INDEX IF NOT EXISTS idx_toc_section_number ON document_toc(section_number);
CREATE INDEX IF NOT EXISTS idx_toc_parent ON document_toc(parent_toc_id);

-- 14. 目录解析调试测试表 (用于解析方法对比工具)
CREATE TABLE IF NOT EXISTS parser_debug_tests (
    -- 主键和标识
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id TEXT UNIQUE NOT NULL,
    filename TEXT NOT NULL,
    file_path TEXT NOT NULL,

    -- 时间戳
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    annotation_time TIMESTAMP,

    -- 文档基本信息
    total_paragraphs INTEGER,
    has_toc BOOLEAN DEFAULT 0,
    toc_items_count INTEGER DEFAULT 0,
    toc_start_idx INTEGER,
    toc_end_idx INTEGER,

    -- 解析结果（JSON格式存储各方法的完整结果）
    semantic_result TEXT,      -- 方法1: 语义锚点解析结果
    old_toc_result TEXT,       -- 方法2: 旧目录定位结果
    style_result TEXT,         -- 方法3: 样式识别结果
    outline_result TEXT,       -- 方法4: 大纲级别结果
    azure_result TEXT,         -- 方法5: Azure Form Recognizer结果
    hybrid_result TEXT,        -- 方法3(新): 混合启发式识别
    docx_native_result TEXT,   -- 方法5(新): python-docx原生提取

    -- 性能指标（秒）
    semantic_elapsed REAL,
    old_toc_elapsed REAL,
    style_elapsed REAL,
    outline_elapsed REAL,
    azure_elapsed REAL,
    hybrid_elapsed REAL,
    docx_native_elapsed REAL,

    -- 识别结果统计
    semantic_chapters_count INTEGER DEFAULT 0,
    old_toc_chapters_count INTEGER DEFAULT 0,
    style_chapters_count INTEGER DEFAULT 0,
    outline_chapters_count INTEGER DEFAULT 0,
    azure_chapters_count INTEGER DEFAULT 0,
    hybrid_chapters_count INTEGER DEFAULT 0,
    docx_native_chapters_count INTEGER DEFAULT 0,

    -- 人工标注（正确答案）
    ground_truth TEXT,         -- JSON格式的正确章节列表
    annotator TEXT,            -- 标注人
    ground_truth_count INTEGER DEFAULT 0,

    -- 准确率指标（自动计算，基于ground_truth）
    semantic_precision REAL,   -- 精确率
    semantic_recall REAL,      -- 召回率
    semantic_f1 REAL,          -- F1分数

    old_toc_precision REAL,
    old_toc_recall REAL,
    old_toc_f1 REAL,

    style_precision REAL,
    style_recall REAL,
    style_f1 REAL,

    outline_precision REAL,
    outline_recall REAL,
    outline_f1 REAL,

    azure_precision REAL,
    azure_recall REAL,
    azure_f1 REAL,

    hybrid_precision REAL,
    hybrid_recall REAL,
    hybrid_f1 REAL,

    docx_native_precision REAL,
    docx_native_recall REAL,
    docx_native_f1 REAL,

    -- 最佳方法（自动判定）
    best_method TEXT,          -- semantic/old_toc/style/outline/azure/hybrid/docx_native
    best_f1_score REAL,

    -- 备注
    notes TEXT
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_parser_tests_document_id ON parser_debug_tests(document_id);
CREATE INDEX IF NOT EXISTS idx_parser_tests_upload_time ON parser_debug_tests(upload_time DESC);
CREATE INDEX IF NOT EXISTS idx_parser_tests_has_ground_truth ON parser_debug_tests(ground_truth IS NOT NULL);

-- 创建视图：测试结果概览
CREATE VIEW IF NOT EXISTS v_parser_debug_summary AS
SELECT
    document_id,
    filename,
    upload_time,
    has_toc,
    toc_items_count,

    -- 识别数量对比(只包含实际使用的字段)
    semantic_chapters_count,
    style_chapters_count,
    hybrid_chapters_count,
    azure_chapters_count,
    docx_native_chapters_count,

    -- 性能对比
    semantic_elapsed,
    style_elapsed,
    hybrid_elapsed,
    azure_elapsed,
    docx_native_elapsed,

    -- 准确率对比（如果有标注）
    CASE WHEN ground_truth IS NOT NULL THEN semantic_f1 ELSE NULL END AS semantic_f1,
    CASE WHEN ground_truth IS NOT NULL THEN style_f1 ELSE NULL END AS style_f1,
    CASE WHEN ground_truth IS NOT NULL THEN hybrid_f1 ELSE NULL END AS hybrid_f1,
    CASE WHEN ground_truth IS NOT NULL THEN azure_f1 ELSE NULL END AS azure_f1,
    CASE WHEN ground_truth IS NOT NULL THEN docx_native_f1 ELSE NULL END AS docx_native_f1,

    -- 最佳方法
    best_method,
    best_f1_score,

    -- 是否已标注
    CASE WHEN ground_truth IS NOT NULL THEN 1 ELSE 0 END AS has_ground_truth,
    annotator
FROM parser_debug_tests
ORDER BY upload_time DESC;

