-- =====================================================
-- 阶段2迁移：合并 tender_hitl_tasks 到 tender_projects
-- 目标：统一项目数据，消除不必要的表关联
-- =====================================================

-- 第一步：在 tender_projects 表中添加 HITL 工作流字段
-- =====================================================

-- 添加步骤1字段
ALTER TABLE tender_projects ADD COLUMN step1_status VARCHAR(20) DEFAULT 'pending';
ALTER TABLE tender_projects ADD COLUMN step1_completed_at TIMESTAMP;
ALTER TABLE tender_projects ADD COLUMN step1_data TEXT;  -- JSON格式

-- 添加步骤2字段
ALTER TABLE tender_projects ADD COLUMN step2_status VARCHAR(20) DEFAULT 'pending';
ALTER TABLE tender_projects ADD COLUMN step2_completed_at TIMESTAMP;
ALTER TABLE tender_projects ADD COLUMN step2_data TEXT;  -- JSON格式

-- 添加步骤3字段
ALTER TABLE tender_projects ADD COLUMN step3_status VARCHAR(20) DEFAULT 'pending';
ALTER TABLE tender_projects ADD COLUMN step3_completed_at TIMESTAMP;
ALTER TABLE tender_projects ADD COLUMN step3_data TEXT;  -- JSON格式

-- 添加全局HITL状态字段
ALTER TABLE tender_projects ADD COLUMN hitl_current_step INTEGER DEFAULT 1;
ALTER TABLE tender_projects ADD COLUMN hitl_overall_status VARCHAR(20) DEFAULT NULL;  -- NULL表示未开始HITL流程

-- 添加成本预估字段
ALTER TABLE tender_projects ADD COLUMN hitl_estimated_cost FLOAT DEFAULT 0.0;
ALTER TABLE tender_projects ADD COLUMN hitl_estimated_words INTEGER DEFAULT 0;


-- 第二步：数据迁移
-- =====================================================
-- 将 tender_hitl_tasks 中的数据迁移到 tender_projects

UPDATE tender_projects
SET
    step1_status = (SELECT step1_status FROM tender_hitl_tasks WHERE tender_hitl_tasks.project_id = tender_projects.project_id),
    step1_completed_at = (SELECT step1_completed_at FROM tender_hitl_tasks WHERE tender_hitl_tasks.project_id = tender_projects.project_id),
    step1_data = (SELECT step1_data FROM tender_hitl_tasks WHERE tender_hitl_tasks.project_id = tender_projects.project_id),

    step2_status = (SELECT step2_status FROM tender_hitl_tasks WHERE tender_hitl_tasks.project_id = tender_projects.project_id),
    step2_completed_at = (SELECT step2_completed_at FROM tender_hitl_tasks WHERE tender_hitl_tasks.project_id = tender_projects.project_id),
    step2_data = (SELECT step2_data FROM tender_hitl_tasks WHERE tender_hitl_tasks.project_id = tender_projects.project_id),

    step3_status = (SELECT step3_status FROM tender_hitl_tasks WHERE tender_hitl_tasks.project_id = tender_projects.project_id),
    step3_completed_at = (SELECT step3_completed_at FROM tender_hitl_tasks WHERE tender_hitl_tasks.project_id = tender_projects.project_id),
    step3_data = (SELECT step3_data FROM tender_hitl_tasks WHERE tender_hitl_tasks.project_id = tender_projects.project_id),

    hitl_current_step = (SELECT current_step FROM tender_hitl_tasks WHERE tender_hitl_tasks.project_id = tender_projects.project_id),
    hitl_overall_status = (SELECT overall_status FROM tender_hitl_tasks WHERE tender_hitl_tasks.project_id = tender_projects.project_id),

    hitl_estimated_cost = (SELECT estimated_cost FROM tender_hitl_tasks WHERE tender_hitl_tasks.project_id = tender_projects.project_id),
    hitl_estimated_words = (SELECT estimated_words FROM tender_hitl_tasks WHERE tender_hitl_tasks.project_id = tender_projects.project_id)
WHERE EXISTS (
    SELECT 1 FROM tender_hitl_tasks WHERE tender_hitl_tasks.project_id = tender_projects.project_id
);


-- 第三步：数据验证
-- =====================================================
-- 验证迁移是否成功（检查记录数是否一致）

SELECT
    '数据迁移验证' as check_type,
    (SELECT COUNT(*) FROM tender_hitl_tasks) as hitl_tasks_count,
    (SELECT COUNT(*) FROM tender_projects WHERE hitl_overall_status IS NOT NULL) as projects_with_hitl_count,
    CASE
        WHEN (SELECT COUNT(*) FROM tender_hitl_tasks) = (SELECT COUNT(*) FROM tender_projects WHERE hitl_overall_status IS NOT NULL)
        THEN '✅ 迁移成功'
        ELSE '❌ 迁移失败，记录数不匹配'
    END as validation_result;

-- 显示详细的迁移统计
SELECT
    'HITL状态分布' as stat_type,
    hitl_overall_status,
    COUNT(*) as count
FROM tender_projects
WHERE hitl_overall_status IS NOT NULL
GROUP BY hitl_overall_status;


-- 第四步：删除旧表
-- =====================================================
-- ⚠️ 警告：执行此步骤前请确保数据迁移成功并已备份！

-- 删除相关视图
DROP VIEW IF EXISTS v_hitl_progress;

-- 删除相关索引（会随表自动删除，但为清晰起见列出）
-- DROP INDEX IF EXISTS idx_hitl_current_step;
-- DROP INDEX IF EXISTS idx_hitl_overall_status;

-- 删除 tender_hitl_tasks 表
-- DROP TABLE IF EXISTS tender_hitl_tasks;

-- 注意：上面的DROP TABLE命令已被注释，需要手动确认后执行


-- 第五步：创建新的索引（优化查询性能）
-- =====================================================

CREATE INDEX IF NOT EXISTS idx_projects_hitl_status ON tender_projects(hitl_overall_status);
CREATE INDEX IF NOT EXISTS idx_projects_hitl_step ON tender_projects(hitl_current_step);
CREATE INDEX IF NOT EXISTS idx_projects_step1_status ON tender_projects(step1_status);
CREATE INDEX IF NOT EXISTS idx_projects_step2_status ON tender_projects(step2_status);
CREATE INDEX IF NOT EXISTS idx_projects_step3_status ON tender_projects(step3_status);


-- 第六步：更新触发器
-- =====================================================
-- tender_projects 的 updated_at 触发器已存在，无需修改


-- =====================================================
-- 迁移完成检查清单
-- =====================================================
--
-- [ ] 1. 备份数据库
-- [ ] 2. 执行第一步（添加字段）
-- [ ] 3. 执行第二步（数据迁移）
-- [ ] 4. 执行第三步（验证数据）
-- [ ] 5. 验证应用程序功能正常
-- [ ] 6. 手动执行第四步（删除旧表）
-- [ ] 7. 更新代码中的所有SQL查询
-- [ ] 8. 全面测试
--
-- =====================================================
