-- 公司资质文件表
-- 用于存储公司的各类资质证书和文件信息

CREATE TABLE IF NOT EXISTS company_qualifications (
    qualification_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,

    -- 资质类型和名称
    qualification_key VARCHAR(50) NOT NULL,  -- 资质标识键（如：business_license, iso9001）
    qualification_name VARCHAR(255) NOT NULL, -- 资质名称（如：营业执照，ISO9001证书）
    custom_name VARCHAR(255),                 -- 用户自定义名称（用于自定义资质）

    -- 文件信息
    original_filename VARCHAR(500) NOT NULL,  -- 原始文件名
    safe_filename VARCHAR(500) NOT NULL,      -- 安全存储文件名
    file_path VARCHAR(1000) NOT NULL,         -- 文件存储路径
    file_size INTEGER,                        -- 文件大小（字节）
    file_type VARCHAR(50),                    -- 文件类型（pdf, png, jpg等）

    -- 多文件支持字段
    file_version VARCHAR(50),                 -- 文件版本/年份标识（如：2023、2024、v1.0）
    file_sequence INTEGER DEFAULT 1,          -- 同一资质的文件排序序号
    is_primary BOOLEAN DEFAULT TRUE,          -- 是否为主文件

    -- 资质有效期
    issue_date DATE,                          -- 颁发日期
    expire_date DATE,                         -- 过期日期
    is_valid BOOLEAN DEFAULT TRUE,            -- 是否有效

    -- 审核状态
    verify_status VARCHAR(20) DEFAULT 'pending', -- 验证状态：pending/verified/rejected
    verify_time TIMESTAMP,                    -- 验证时间
    verify_by VARCHAR(100),                   -- 验证人
    verify_note TEXT,                         -- 验证备注

    -- 元数据
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    upload_by VARCHAR(100),                   -- 上传人
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- 索引和约束
    FOREIGN KEY (company_id) REFERENCES companies(company_id) ON DELETE CASCADE
    -- 注意：移除了 UNIQUE (company_id, qualification_key) 约束以支持多文件
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_company_qualifications_company ON company_qualifications(company_id);
CREATE INDEX IF NOT EXISTS idx_company_qualifications_expire ON company_qualifications(expire_date);
CREATE INDEX IF NOT EXISTS idx_company_qualifications_status ON company_qualifications(verify_status);
-- 新增：支持多文件查询的复合索引
CREATE INDEX IF NOT EXISTS idx_company_qual_key_seq ON company_qualifications(company_id, qualification_key, file_sequence);

-- 预定义的资质类型表（可选，用于规范化管理）
CREATE TABLE IF NOT EXISTS qualification_types (
    type_id INTEGER PRIMARY KEY AUTOINCREMENT,
    type_key VARCHAR(50) NOT NULL UNIQUE,     -- 资质标识键
    type_name VARCHAR(255) NOT NULL,          -- 资质类型名称
    category VARCHAR(50),                     -- 分类：基础资质/行业资质/认证证书/其他
    is_required BOOLEAN DEFAULT FALSE,        -- 是否必需
    allow_multiple_files BOOLEAN DEFAULT FALSE, -- 是否允许上传多个文件
    version_label VARCHAR(50),                -- 版本标签名称（如：年份、版本号、专利号）
    description TEXT,                          -- 描述
    sort_order INTEGER DEFAULT 0,             -- 排序
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 插入预定义的资质类型
-- 格式：(type_key, type_name, category, is_required, allow_multiple_files, version_label, sort_order)
INSERT OR IGNORE INTO qualification_types (type_key, type_name, category, is_required, allow_multiple_files, version_label, sort_order) VALUES
    -- 单文件资质（默认）
    ('business_license', '营业执照', '基础资质', TRUE, FALSE, NULL, 1),
    ('bank_permit', '开户许可证', '基础资质', FALSE, FALSE, NULL, 4),
    ('legal_id_front', '法人身份证正面', '基础资质', FALSE, FALSE, NULL, 5),
    ('legal_id_back', '法人身份证反面', '基础资质', FALSE, FALSE, NULL, 6),
    ('auth_id_front', '被授权人身份证正面', '基础资质', FALSE, FALSE, NULL, 7),
    ('auth_id_back', '被授权人身份证反面', '基础资质', FALSE, FALSE, NULL, 8),
    -- 已移除法人授权委托书（改为使用被授权人身份证）
    -- ('authorization_letter', '法人授权委托书', '基础资质', FALSE, FALSE, NULL, 9),
    ('basic_telecom_permit', '基础电信业务许可证', '行业资质', FALSE, FALSE, NULL, 9),
    ('value_added_telecom_permit', '增值电信业务许可证', '行业资质', FALSE, FALSE, NULL, 10),
    ('iso9001', 'ISO9001质量管理体系认证', '认证证书', FALSE, FALSE, NULL, 10),
    ('iso20000', 'ISO20000信息技术服务管理体系认证', '认证证书', FALSE, FALSE, NULL, 12),
    ('iso27001', 'ISO27001信息安全管理体系认证', '认证证书', FALSE, FALSE, NULL, 13),
    ('cmmi', 'CMMI认证', '认证证书', FALSE, FALSE, NULL, 14),
    ('itss', 'ITSS信息技术服务标准认证', '认证证书', FALSE, FALSE, NULL, 15),
    ('safety_production', '安全生产许可证', '行业资质', FALSE, FALSE, NULL, 16),
    -- 多文件资质（允许上传多个）
    ('software_copyright', '软件著作权登记证书', '行业资质', FALSE, TRUE, '软著名称', 17),
    ('patent_certificate', '专利证书', '行业资质', FALSE, TRUE, '专利号', 18),
    ('audit_report', '财务审计报告', '财务资质', FALSE, TRUE, '年份', 19),
    -- 信用证明类资质（负面清单查询证明）
    ('credit_china_check', '信用中国查询证明', '信用证明', FALSE, FALSE, NULL, 20),
    ('tax_violation_check', '重大税收违法案件查询证明', '信用证明', FALSE, FALSE, NULL, 21),
    ('gov_procurement_check', '政府采购严重违法失信查询证明', '信用证明', FALSE, FALSE, NULL, 22);

-- 资质文件访问日志表（用于审计）
CREATE TABLE IF NOT EXISTS qualification_access_logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    qualification_id INTEGER NOT NULL,
    company_id INTEGER NOT NULL,
    action_type VARCHAR(50) NOT NULL,         -- upload/download/view/update/delete
    user_id VARCHAR(100),
    user_role VARCHAR(50),
    ip_address VARCHAR(50),
    user_agent TEXT,
    access_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (qualification_id) REFERENCES company_qualifications(qualification_id),
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);