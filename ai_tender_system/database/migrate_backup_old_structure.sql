-- ===================================================================
-- 备份旧数据结构（重构前）
-- 文件：migrate_backup_old_structure.sql
-- 说明：此脚本在重构前备份所有受影响的表
-- 作者：AI Tender System
-- 日期：2025-11-07
-- ===================================================================

-- 说明：
-- 1. 此脚本应该在开始重构前运行
-- 2. 如果备份表已存在，将先删除再重新创建
-- 3. 备份表命名规则：原表名 + _backup 后缀
-- 4. 备份后的数据可用于回滚或数据验证

BEGIN TRANSACTION;

-- ===================================================================
-- 第一部分：删除已存在的备份表（如果有）
-- ===================================================================

DROP TABLE IF EXISTS tender_hitl_tasks_backup;
DROP TABLE IF EXISTS tender_processing_tasks_backup;
DROP TABLE IF EXISTS tender_document_chunks_backup;
DROP TABLE IF EXISTS tender_requirements_backup;
DROP TABLE IF EXISTS tender_document_chapters_backup;
DROP TABLE IF EXISTS tender_filter_review_backup;
DROP TABLE IF EXISTS tender_requirements_draft_backup;
DROP TABLE IF EXISTS tender_processing_logs_backup;
DROP TABLE IF EXISTS tender_user_actions_backup;

-- ===================================================================
-- 第二部分：创建备份表并复制数据
-- ===================================================================

-- 1. 备份 tender_hitl_tasks
CREATE TABLE tender_hitl_tasks_backup AS
SELECT * FROM tender_hitl_tasks;

SELECT '✓ tender_hitl_tasks 已备份 (' || COUNT(*) || ' 条记录)' as status
FROM tender_hitl_tasks_backup;

-- 2. 备份 tender_processing_tasks
CREATE TABLE tender_processing_tasks_backup AS
SELECT * FROM tender_processing_tasks;

SELECT '✓ tender_processing_tasks 已备份 (' || COUNT(*) || ' 条记录)' as status
FROM tender_processing_tasks_backup;

-- 3. 备份 tender_document_chunks
CREATE TABLE tender_document_chunks_backup AS
SELECT * FROM tender_document_chunks;

SELECT '✓ tender_document_chunks 已备份 (' || COUNT(*) || ' 条记录)' as status
FROM tender_document_chunks_backup;

-- 4. 备份 tender_requirements
CREATE TABLE tender_requirements_backup AS
SELECT * FROM tender_requirements;

SELECT '✓ tender_requirements 已备份 (' || COUNT(*) || ' 条记录)' as status
FROM tender_requirements_backup;

-- 5. 备份 tender_document_chapters
CREATE TABLE tender_document_chapters_backup AS
SELECT * FROM tender_document_chapters;

SELECT '✓ tender_document_chapters 已备份 (' || COUNT(*) || ' 条记录)' as status
FROM tender_document_chapters_backup;

-- 6. 备份 tender_filter_review
CREATE TABLE tender_filter_review_backup AS
SELECT * FROM tender_filter_review;

SELECT '✓ tender_filter_review 已备份 (' || COUNT(*) || ' 条记录)' as status
FROM tender_filter_review_backup;

-- 7. 备份 tender_requirements_draft
CREATE TABLE tender_requirements_draft_backup AS
SELECT * FROM tender_requirements_draft;

SELECT '✓ tender_requirements_draft 已备份 (' || COUNT(*) || ' 条记录)' as status
FROM tender_requirements_draft_backup;

-- 8. 备份 tender_processing_logs
CREATE TABLE tender_processing_logs_backup AS
SELECT * FROM tender_processing_logs;

SELECT '✓ tender_processing_logs 已备份 (' || COUNT(*) || ' 条记录)' as status
FROM tender_processing_logs_backup;

-- 9. 备份 tender_user_actions
CREATE TABLE tender_user_actions_backup AS
SELECT * FROM tender_user_actions;

SELECT '✓ tender_user_actions 已备份 (' || COUNT(*) || ' 条记录)' as status
FROM tender_user_actions_backup;

-- ===================================================================
-- 第三部分：备份完成统计
-- ===================================================================

SELECT '========================================' as separator;
SELECT '备份完成汇总' as title;
SELECT '========================================' as separator;
SELECT
    (SELECT COUNT(*) FROM tender_hitl_tasks_backup) as hitl_tasks,
    (SELECT COUNT(*) FROM tender_processing_tasks_backup) as processing_tasks,
    (SELECT COUNT(*) FROM tender_document_chunks_backup) as document_chunks,
    (SELECT COUNT(*) FROM tender_requirements_backup) as requirements,
    (SELECT COUNT(*) FROM tender_document_chapters_backup) as document_chapters,
    (SELECT COUNT(*) FROM tender_filter_review_backup) as filter_review,
    (SELECT COUNT(*) FROM tender_requirements_draft_backup) as requirements_draft,
    (SELECT COUNT(*) FROM tender_processing_logs_backup) as processing_logs,
    (SELECT COUNT(*) FROM tender_user_actions_backup) as user_actions;

COMMIT;

-- 备份完成！
-- 下一步：运行 migrate_to_new_structure.sql 进行数据迁移
