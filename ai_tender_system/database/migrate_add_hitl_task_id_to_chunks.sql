-- =====================================================
-- 迁移脚本：为 tender_document_chunks 表添加 hitl_task_id 字段
-- 目的：支持按HITL任务隔离chunks，解决步骤2显示所有chunks的问题
-- 创建时间：2025-10-23
-- =====================================================

-- 1. 添加 hitl_task_id 字段到 tender_document_chunks 表
ALTER TABLE tender_document_chunks
ADD COLUMN hitl_task_id VARCHAR(100);

-- 2. 创建索引以提高查询性能
CREATE INDEX IF NOT EXISTS idx_chunks_hitl_task
ON tender_document_chunks(hitl_task_id);

-- 3. 创建联合索引（project_id + hitl_task_id）
CREATE INDEX IF NOT EXISTS idx_chunks_project_hitl
ON tender_document_chunks(project_id, hitl_task_id);

-- 注意：
-- - 现有数据的 hitl_task_id 将为 NULL
-- - 新插入的chunks必须包含 hitl_task_id
-- - 步骤2 API 需要更新为按 hitl_task_id 过滤，而不是仅按 project_id
