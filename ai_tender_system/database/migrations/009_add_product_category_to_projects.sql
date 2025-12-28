-- 迁移脚本：为招标项目表添加产品分类字段
-- 版本：009
-- 日期：2025-12-28
-- 说明：在新建项目时支持选择产品分类

-- 添加产品分类ID字段
ALTER TABLE tender_projects ADD COLUMN product_category_id INTEGER;

-- 添加产品分类名称（冗余存储便于查询展示）
ALTER TABLE tender_projects ADD COLUMN product_category_name VARCHAR(100);

-- 添加具体产品项（JSON数组，支持多选）
ALTER TABLE tender_projects ADD COLUMN product_items TEXT;

-- 添加索引
CREATE INDEX IF NOT EXISTS idx_tender_projects_product_category
ON tender_projects(product_category_id);
