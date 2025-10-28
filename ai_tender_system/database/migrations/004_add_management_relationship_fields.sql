-- 为 companies 表添加管理关系字段
-- 创建时间: 2025-10-28
-- 描述: 在财务信息模块中添加管理关系单位名称和被管理关系单位名称

-- 1. 管理关系单位名称（本公司管理的单位）
ALTER TABLE companies ADD COLUMN managing_unit_name TEXT;

-- 2. 被管理关系单位名称（管理本公司的单位）
ALTER TABLE companies ADD COLUMN managed_unit_name TEXT;
