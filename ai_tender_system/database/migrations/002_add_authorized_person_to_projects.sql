-- 迁移：为 tender_projects 表添加被授权人字段
-- 日期：2025-10-26
-- 目的：支持在项目级别记录被授权人信息

-- SQLite每次只能添加一个列
ALTER TABLE tender_projects ADD COLUMN authorized_person_name VARCHAR(100);
ALTER TABLE tender_projects ADD COLUMN authorized_person_id VARCHAR(18);
ALTER TABLE tender_projects ADD COLUMN authorized_person_position VARCHAR(100);

-- 为现有项目从关联公司复制被授权人信息
UPDATE tender_projects
SET
    authorized_person_name = (
        SELECT authorized_person_name
        FROM companies
        WHERE companies.company_id = tender_projects.company_id
    ),
    authorized_person_id = (
        SELECT authorized_person_id
        FROM companies
        WHERE companies.company_id = tender_projects.company_id
    ),
    authorized_person_position = (
        SELECT authorized_person_position
        FROM companies
        WHERE companies.company_id = tender_projects.company_id
    )
WHERE company_id IS NOT NULL;
