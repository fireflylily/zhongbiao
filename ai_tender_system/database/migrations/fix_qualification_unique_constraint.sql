-- =====================================================
-- 数据库迁移脚本: 修复资质文件UNIQUE约束
-- 日期: 2025-10-25
-- 目的: 支持多文件资质上传(如多年份审计报告)
-- =====================================================

-- 步骤1: 创建临时表,复制数据
CREATE TABLE company_qualifications_new (
    qualification_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,

    -- 资质类型和名称
    qualification_key VARCHAR(50) NOT NULL,  -- 资质标识键
    qualification_name VARCHAR(255) NOT NULL,
    custom_name VARCHAR(255),                 -- 用户自定义名称

    -- 文件信息
    original_filename VARCHAR(500) NOT NULL,
    safe_filename VARCHAR(500) NOT NULL,
    file_path VARCHAR(1000) NOT NULL,
    file_size INTEGER,
    file_type VARCHAR(50),

    -- 资质有效期
    issue_date DATE,
    expire_date DATE,
    is_valid BOOLEAN DEFAULT TRUE,

    -- 审核状态
    verify_status VARCHAR(20) DEFAULT 'pending',
    verify_time TIMESTAMP,
    verify_by VARCHAR(100),
    verify_note TEXT,

    -- 元数据
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    upload_by VARCHAR(100),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    file_version VARCHAR(50),          -- 文件版本(如年份:2023)
    file_sequence INTEGER DEFAULT 1,    -- 文件序号
    is_primary BOOLEAN DEFAULT TRUE,    -- 是否为主文件

    -- 外键约束
    FOREIGN KEY (company_id) REFERENCES companies(company_id) ON DELETE CASCADE,

    -- 新的UNIQUE约束: 同一公司、同一资质类型、不同序号可以共存
    UNIQUE (company_id, qualification_key, file_sequence)
);

-- 步骤2: 复制数据
INSERT INTO company_qualifications_new
SELECT * FROM company_qualifications;

-- 步骤3: 删除旧表
DROP TABLE company_qualifications;

-- 步骤4: 重命名新表
ALTER TABLE company_qualifications_new RENAME TO company_qualifications;

-- 步骤5: 重建索引
CREATE INDEX idx_company_qualifications_company ON company_qualifications(company_id);
CREATE INDEX idx_company_qualifications_expire ON company_qualifications(expire_date);
CREATE INDEX idx_company_qualifications_status ON company_qualifications(verify_status);
CREATE INDEX idx_company_qual_key_seq ON company_qualifications(company_id, qualification_key, file_sequence);

-- 完成
