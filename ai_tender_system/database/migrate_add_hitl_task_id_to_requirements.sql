-- =====================================================
-- 迁移脚本：为 tender_requirements 表添加 hitl_task_id 字段
-- 目的：支持按HITL任务隔离需求，解决步骤3显示所有需求的问题
-- =====================================================

-- 1. 添加 hitl_task_id 字段
ALTER TABLE tender_requirements
ADD COLUMN hitl_task_id VARCHAR(100);

-- 2. 创建索引以提高查询性能
CREATE INDEX IF NOT EXISTS idx_requirements_hitl_task
ON tender_requirements(hitl_task_id);

-- 3. 创建联合索引（project_id + hitl_task_id）
CREATE INDEX IF NOT EXISTS idx_requirements_project_hitl
ON tender_requirements(project_id, hitl_task_id);

-- 注意：
-- - 现有数据的 hitl_task_id 将为 NULL
-- - 新插入的需求必须包含 hitl_task_id
-- - 步骤3 API 需要更新为按 hitl_task_id 过滤，而不是仅按 project_id
