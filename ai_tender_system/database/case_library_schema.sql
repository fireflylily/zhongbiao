-- 案例库数据库表结构
-- 创建时间: 2025-10-17
-- 描述: 独立的案例库管理系统，用于管理客户案例、合同信息和附件

-- 1. 案例库主表
-- 字段说明：
--   case_title = contract_name (案例标题即合同名称)
--   customer_name = party_a_name = party_a_customer_name (客户名称即甲方名称)
--   party_b_name 和 party_b_company_name 可从company表获取
CREATE TABLE IF NOT EXISTS case_studies (
    case_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    product_id INTEGER,  -- 关联产品(可选)

    -- 基本信息
    case_title VARCHAR(255) NOT NULL,  -- 案例标题/合同名称（统一字段）
    case_number VARCHAR(100),  -- 案例编号/合同编号（统一字段）
    customer_name VARCHAR(255) NOT NULL,  -- 甲方客户名称（统一字段）
    industry VARCHAR(100),  -- 所属行业

    -- 合同信息
    contract_name VARCHAR(255),  -- 合同名称（等同于case_title）
    contract_type VARCHAR(50) NOT NULL,  -- 合同类型: 订单/合同
    final_customer_name VARCHAR(255),  -- 最终客户名称(订单类型时填写)
    contract_amount VARCHAR(100),  -- 合同金额（支持数字或文字描述，如"100万元"、"百万级"）
    contract_start_date DATE,  -- 合同开始日期
    contract_end_date DATE,  -- 合同结束日期
    party_a_customer_name VARCHAR(255),  -- 甲方客户名称（等同于customer_name）
    party_b_company_name VARCHAR(255),  -- 乙方公司名称（可从company表获取）

    -- 甲方客户详细信息
    party_a_name VARCHAR(255),  -- 甲方名称（等同于customer_name）
    party_a_address TEXT,  -- 甲方地址
    party_a_contact_name VARCHAR(100),  -- 甲方联系人姓名
    party_a_contact_phone VARCHAR(50),  -- 甲方联系电话
    party_a_contact_email VARCHAR(100),  -- 甲方联系邮箱

    -- 乙方公司详细信息
    party_b_name VARCHAR(255),  -- 乙方名称（可从company表获取）
    party_b_address TEXT,  -- 乙方地址
    party_b_contact_name VARCHAR(100),  -- 乙方联系人姓名
    party_b_contact_phone VARCHAR(50),  -- 乙方联系电话
    party_b_contact_email VARCHAR(100),  -- 乙方联系邮箱

    -- 案例状态
    case_status VARCHAR(50) DEFAULT 'success',  -- 成功/进行中/待验收

    -- 时间戳
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (company_id) REFERENCES companies(company_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- 2. 案例附件表
CREATE TABLE IF NOT EXISTS case_attachments (
    attachment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id INTEGER NOT NULL,

    -- 文件信息
    file_name VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_type VARCHAR(20),  -- pdf/doc/docx/jpg/png
    file_size INTEGER,

    -- 附件类型
    attachment_type VARCHAR(50),  -- contract:合同 acceptance:验收证明 testimony:客户证明 photo:项目照片 other:其他
    attachment_description TEXT,  -- 附件说明

    -- 时间戳
    uploaded_by VARCHAR(100),
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (case_id) REFERENCES case_studies(case_id) ON DELETE CASCADE
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_case_studies_company ON case_studies(company_id);
CREATE INDEX IF NOT EXISTS idx_case_studies_product ON case_studies(product_id);
CREATE INDEX IF NOT EXISTS idx_case_studies_customer ON case_studies(customer_name);
CREATE INDEX IF NOT EXISTS idx_case_studies_industry ON case_studies(industry);
CREATE INDEX IF NOT EXISTS idx_case_studies_status ON case_studies(case_status);
CREATE INDEX IF NOT EXISTS idx_case_studies_contract_type ON case_studies(contract_type);
CREATE INDEX IF NOT EXISTS idx_case_studies_dates ON case_studies(contract_start_date, contract_end_date);
CREATE INDEX IF NOT EXISTS idx_case_studies_party_a_customer ON case_studies(party_a_customer_name);
CREATE INDEX IF NOT EXISTS idx_case_studies_party_b_company ON case_studies(party_b_company_name);
CREATE INDEX IF NOT EXISTS idx_case_attachments_case ON case_attachments(case_id);
