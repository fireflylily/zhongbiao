-- 迁移：允许项目在创建时不关联公司
-- 日期：2025-11-21
-- 目的：支持先创建项目，后续再关联公司的业务流程

-- SQLite 不支持直接修改约束，需要重建表
-- 步骤：
-- 1. 创建新表（修改后的约束）
-- 2. 复制数据
-- 3. 删除旧表
-- 4. 重命名新表
-- 5. 重建索引

-- 1. 创建新表（移除旧的唯一约束，添加新的部分唯一约束）
CREATE TABLE IF NOT EXISTS tender_projects_new (
    project_id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_name VARCHAR(255),
    project_number VARCHAR(100),
    tenderer VARCHAR(255),
    agency VARCHAR(255),
    bidding_method VARCHAR(100),
    bidding_location VARCHAR(255),
    bidding_time VARCHAR(100),
    tender_document_path VARCHAR(500),
    original_filename VARCHAR(255),
    company_id INTEGER,
    qualifications_data TEXT,
    scoring_data TEXT,
    winner_count VARCHAR(50),
    authorized_person_name VARCHAR(100),
    authorized_person_id VARCHAR(18),
    authorized_person_position VARCHAR(100),
    status VARCHAR(20) DEFAULT 'draft',
    created_by VARCHAR(100) DEFAULT 'system',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    -- 保留外键约束
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
    -- 注意：移除了 UNIQUE(company_id, project_name, project_number) 约束
    -- 我们将通过应用层逻辑来控制唯一性
);

-- 2. 复制所有数据到新表
INSERT INTO tender_projects_new (
    project_id, project_name, project_number, tenderer, agency,
    bidding_method, bidding_location, bidding_time,
    tender_document_path, original_filename, company_id,
    qualifications_data, scoring_data, winner_count,
    authorized_person_name, authorized_person_id, authorized_person_position,
    status, created_by, created_at, updated_at
)
SELECT
    project_id, project_name, project_number, tenderer, agency,
    bidding_method, bidding_location, bidding_time,
    tender_document_path, original_filename, company_id,
    qualifications_data, scoring_data, winner_count,
    authorized_person_name, authorized_person_id, authorized_person_position,
    status, created_by, created_at, updated_at
FROM tender_projects;

-- 3. 删除旧表
DROP TABLE tender_projects;

-- 4. 重命名新表
ALTER TABLE tender_projects_new RENAME TO tender_projects;

-- 5. 重建索引
CREATE INDEX IF NOT EXISTS idx_tender_projects_company ON tender_projects(company_id);
CREATE INDEX IF NOT EXISTS idx_tender_projects_status ON tender_projects(status);

-- 6. 为未关联公司的项目创建部分唯一索引
-- 当 company_id 为 NULL 时，project_name 和 project_number 的组合应该唯一
CREATE UNIQUE INDEX IF NOT EXISTS idx_tender_projects_unique_no_company
ON tender_projects(project_name, project_number)
WHERE company_id IS NULL;

-- 7. 为已关联公司的项目创建部分唯一索引
-- 当 company_id 不为 NULL 时，company_id, project_name, project_number 的组合应该唯一
CREATE UNIQUE INDEX IF NOT EXISTS idx_tender_projects_unique_with_company
ON tender_projects(company_id, project_name, project_number)
WHERE company_id IS NOT NULL;
