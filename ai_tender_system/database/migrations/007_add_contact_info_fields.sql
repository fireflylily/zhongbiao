-- =====================================================
-- 添加联系人和联系方式字段到 tender_projects 表
-- 创建时间: 2025-11-09
-- 功能: 支持提取和存储招标方和代理机构的联系人信息
-- =====================================================

-- 1. 添加招标方联系人字段
ALTER TABLE tender_projects
ADD COLUMN tenderer_contact_person VARCHAR(100);

-- 2. 添加招标方联系方式字段
ALTER TABLE tender_projects
ADD COLUMN tenderer_contact_method VARCHAR(255);

-- 3. 添加代理机构联系人字段
ALTER TABLE tender_projects
ADD COLUMN agency_contact_person VARCHAR(100);

-- 4. 添加代理机构联系方式字段
ALTER TABLE tender_projects
ADD COLUMN agency_contact_method VARCHAR(255);
