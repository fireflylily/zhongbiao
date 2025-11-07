-- ===================================================================
-- 数据库重构：去掉 hitl_task_id 和 task_id，只保留 project_id
-- 文件：migrate_to_new_structure.sql
-- 说明：此脚本将所有表重构为以 project_id 为主键的扁平化结构
-- 作者：AI Tender System
-- 日期：2025-11-07
-- ===================================================================

-- 重要说明：
-- 1. 运行此脚本前，请先运行 migrate_backup_old_structure.sql 备份数据
-- 2. 此脚本会删除旧表并创建新表，然后迁移数据
-- 3. 迁移策略：每个 project_id 只保留最新的一条任务记录（按 created_at 排序）
-- 4. 如需回滚，可以从备份表恢复数据

BEGIN TRANSACTION;

-- ===================================================================
-- 第一部分：删除旧结构
-- ===================================================================

SELECT '========================================' as separator;
SELECT '开始删除旧表结构...' as status;
SELECT '========================================' as separator;

-- 删除视图
DROP VIEW IF EXISTS v_processing_statistics;
DROP VIEW IF EXISTS v_requirements_summary;
DROP VIEW IF EXISTS v_hitl_progress;
DROP VIEW IF EXISTS v_chapter_selection_stats;

-- 删除触发器
DROP TRIGGER IF EXISTS update_chunks_timestamp;
DROP TRIGGER IF EXISTS update_requirements_timestamp;
DROP TRIGGER IF EXISTS update_logs_timestamp;
DROP TRIGGER IF EXISTS update_chapters_timestamp;
DROP TRIGGER IF EXISTS update_filter_review_timestamp;
DROP TRIGGER IF EXISTS update_draft_timestamp;
DROP TRIGGER IF EXISTS update_hitl_tasks_timestamp;

-- 删除索引（会随表自动删除，但显式删除更清晰）
DROP INDEX IF EXISTS idx_chunks_project_id;
DROP INDEX IF EXISTS idx_chunks_project_index;
DROP INDEX IF EXISTS idx_chunks_valuable;
DROP INDEX IF EXISTS idx_chunks_type;
DROP INDEX IF EXISTS idx_chunks_hitl_task;
DROP INDEX IF EXISTS idx_chunks_project_hitl;
DROP INDEX IF EXISTS idx_requirements_project_id;
DROP INDEX IF EXISTS idx_requirements_type;
DROP INDEX IF EXISTS idx_requirements_category;
DROP INDEX IF EXISTS idx_requirements_priority;
DROP INDEX IF EXISTS idx_requirements_verified;
DROP INDEX IF EXISTS idx_requirements_hitl_task;
DROP INDEX IF EXISTS idx_requirements_project_hitl;
DROP INDEX IF EXISTS idx_logs_project_id;
DROP INDEX IF EXISTS idx_logs_task_id;
DROP INDEX IF EXISTS idx_logs_step_status;
DROP INDEX IF EXISTS idx_logs_created_at;
DROP INDEX IF EXISTS idx_tasks_project_id;
DROP INDEX IF EXISTS idx_tasks_status;
DROP INDEX IF EXISTS idx_chapters_project_task;
DROP INDEX IF EXISTS idx_chapters_selected;
DROP INDEX IF EXISTS idx_chapters_node_id;
DROP INDEX IF EXISTS idx_filter_review_project_task;
DROP INDEX IF EXISTS idx_filter_review_chunk;
DROP INDEX IF EXISTS idx_filter_review_decision;
DROP INDEX IF EXISTS idx_draft_project_task;
DROP INDEX IF EXISTS idx_draft_requirement;
DROP INDEX IF EXISTS idx_draft_published;
DROP INDEX IF EXISTS idx_hitl_project;
DROP INDEX IF EXISTS idx_hitl_task;
DROP INDEX IF EXISTS idx_hitl_current_step;
DROP INDEX IF EXISTS idx_hitl_overall_status;
DROP INDEX IF EXISTS idx_actions_project;
DROP INDEX IF EXISTS idx_actions_task;
DROP INDEX IF EXISTS idx_actions_type;
DROP INDEX IF EXISTS idx_actions_created;

-- 删除表（注意顺序：先删除有外键依赖的子表）
DROP TABLE IF EXISTS tender_user_actions;
DROP TABLE IF EXISTS tender_requirements_draft;
DROP TABLE IF EXISTS tender_filter_review;
DROP TABLE IF EXISTS tender_document_chapters;
DROP TABLE IF EXISTS tender_hitl_tasks;
DROP TABLE IF EXISTS tender_processing_logs;
DROP TABLE IF EXISTS tender_processing_tasks;
DROP TABLE IF EXISTS tender_requirements;
DROP TABLE IF EXISTS tender_document_chunks;

SELECT '✓ 旧表结构已删除' as status;

-- ===================================================================
-- 第二部分：创建新表结构（使用 project_id 作为主键）
-- ===================================================================

SELECT '========================================' as separator;
SELECT '开始创建新表结构...' as status;
SELECT '========================================' as separator;

-- 1. 文档分块表（新结构）
CREATE TABLE tender_document_chunks (
    chunk_id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,  -- ✅ 直接关联项目
    chunk_index INTEGER NOT NULL,
    chunk_type VARCHAR(50) NOT NULL,  -- title/paragraph/table/list
    content TEXT NOT NULL,
    metadata TEXT,  -- JSON: {section_title, page_number, token_count, parent_section}

    -- 筛选字段
    is_valuable BOOLEAN DEFAULT NULL,  -- NULL=未筛选, TRUE=高价值, FALSE=低价值
    filter_confidence FLOAT DEFAULT NULL,
    filtered_at TIMESTAMP DEFAULT NULL,
    filter_model VARCHAR(50) DEFAULT NULL,

    -- 元数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (project_id) REFERENCES tender_projects(project_id) ON DELETE CASCADE
);

CREATE INDEX idx_chunks_project_id ON tender_document_chunks(project_id);
CREATE INDEX idx_chunks_project_index ON tender_document_chunks(project_id, chunk_index);
CREATE INDEX idx_chunks_valuable ON tender_document_chunks(project_id, is_valuable);
CREATE INDEX idx_chunks_type ON tender_document_chunks(chunk_type);

SELECT '✓ tender_document_chunks 表已创建' as status;

-- 2. 提取的要求表（新结构）
CREATE TABLE tender_requirements (
    requirement_id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,  -- ✅ 直接关联项目
    chunk_id INTEGER,

    -- 要求分类
    constraint_type VARCHAR(20) NOT NULL,  -- mandatory/optional/scoring
    category VARCHAR(50) NOT NULL,  -- qualification/technical/commercial/service
    subcategory VARCHAR(100),

    -- 要求内容
    detail TEXT NOT NULL,
    summary VARCHAR(200),
    source_location VARCHAR(255),
    priority VARCHAR(10) DEFAULT 'medium',

    -- AI提取元数据
    extraction_confidence FLOAT DEFAULT NULL,
    extraction_model VARCHAR(50) DEFAULT NULL,
    extracted_at TIMESTAMP DEFAULT NULL,

    -- 验证和审核
    is_verified BOOLEAN DEFAULT FALSE,
    verified_by VARCHAR(100),
    verified_at TIMESTAMP,
    notes TEXT,

    -- 元数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (project_id) REFERENCES tender_projects(project_id) ON DELETE CASCADE,
    FOREIGN KEY (chunk_id) REFERENCES tender_document_chunks(chunk_id) ON DELETE SET NULL
);

CREATE INDEX idx_requirements_project_id ON tender_requirements(project_id);
CREATE INDEX idx_requirements_type ON tender_requirements(project_id, constraint_type);
CREATE INDEX idx_requirements_category ON tender_requirements(project_id, category);
CREATE INDEX idx_requirements_priority ON tender_requirements(priority);
CREATE INDEX idx_requirements_verified ON tender_requirements(is_verified);

SELECT '✓ tender_requirements 表已创建' as status;

-- 3. 处理日志表（新结构）
CREATE TABLE tender_processing_logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL UNIQUE,  -- ✅ project_id 改为 UNIQUE（一个项目一条日志）

    -- 流程步骤
    step VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',

    -- 进度信息
    total_items INTEGER DEFAULT 0,
    processed_items INTEGER DEFAULT 0,
    success_items INTEGER DEFAULT 0,
    failed_items INTEGER DEFAULT 0,

    -- 成本统计
    cost_estimation FLOAT DEFAULT 0.0,
    actual_cost FLOAT DEFAULT 0.0,
    api_calls INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,

    -- 时间统计
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    estimated_duration INTEGER,
    actual_duration INTEGER,

    -- 错误信息
    error_message TEXT,
    error_details TEXT,

    -- 元数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (project_id) REFERENCES tender_projects(project_id) ON DELETE CASCADE
);

CREATE INDEX idx_logs_project_id ON tender_processing_logs(project_id);
CREATE INDEX idx_logs_step_status ON tender_processing_logs(step, status);
CREATE INDEX idx_logs_created_at ON tender_processing_logs(created_at DESC);

SELECT '✓ tender_processing_logs 表已创建' as status;

-- 4. 处理任务表（新结构，project_id 作为主键）
CREATE TABLE tender_processing_tasks (
    project_id INTEGER PRIMARY KEY,  -- ✅ 改为主键（一个项目一个任务）

    -- 任务配置
    pipeline_config TEXT,
    options TEXT,

    -- 任务状态
    overall_status VARCHAR(20) DEFAULT 'pending',
    current_step VARCHAR(20),
    progress_percentage FLOAT DEFAULT 0.0,

    -- 结果摘要
    total_chunks INTEGER DEFAULT 0,
    valuable_chunks INTEGER DEFAULT 0,
    total_requirements INTEGER DEFAULT 0,

    -- 时间信息
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,

    FOREIGN KEY (project_id) REFERENCES tender_projects(project_id) ON DELETE CASCADE
);

CREATE INDEX idx_tasks_status ON tender_processing_tasks(overall_status);

SELECT '✓ tender_processing_tasks 表已创建' as status;

-- 5. 文档章节表（新结构）
CREATE TABLE tender_document_chapters (
    chapter_id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,  -- ✅ 只保留 project_id

    -- 章节信息
    chapter_node_id VARCHAR(50) NOT NULL,
    level INTEGER NOT NULL,
    title VARCHAR(500) NOT NULL,
    para_start_idx INTEGER NOT NULL,
    para_end_idx INTEGER,
    word_count INTEGER DEFAULT 0,
    preview_text TEXT,

    -- 选择状态
    is_selected BOOLEAN DEFAULT FALSE,
    auto_selected BOOLEAN DEFAULT FALSE,
    skip_recommended BOOLEAN DEFAULT FALSE,

    -- 父子关系
    parent_chapter_id INTEGER,

    -- 元数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (project_id) REFERENCES tender_projects(project_id) ON DELETE CASCADE,
    FOREIGN KEY (parent_chapter_id) REFERENCES tender_document_chapters(chapter_id) ON DELETE CASCADE
);

CREATE INDEX idx_chapters_project ON tender_document_chapters(project_id);
CREATE INDEX idx_chapters_selected ON tender_document_chapters(is_selected);
CREATE INDEX idx_chapters_node_id ON tender_document_chapters(chapter_node_id);

SELECT '✓ tender_document_chapters 表已创建' as status;

-- 6. 筛选复核表（新结构）
CREATE TABLE tender_filter_review (
    review_id INTEGER PRIMARY KEY AUTOINCREMENT,
    chunk_id INTEGER NOT NULL,
    project_id INTEGER NOT NULL,  -- ✅ 只保留 project_id

    -- 原始筛选结果
    ai_decision VARCHAR(20) NOT NULL,
    ai_confidence FLOAT,
    ai_reasoning TEXT,

    -- 人工复核
    user_decision VARCHAR(20),
    reviewed_by VARCHAR(100),
    reviewed_at TIMESTAMP,
    review_notes TEXT,

    -- 元数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (chunk_id) REFERENCES tender_document_chunks(chunk_id) ON DELETE CASCADE,
    FOREIGN KEY (project_id) REFERENCES tender_projects(project_id) ON DELETE CASCADE
);

CREATE INDEX idx_filter_review_project ON tender_filter_review(project_id);
CREATE INDEX idx_filter_review_chunk ON tender_filter_review(chunk_id);
CREATE INDEX idx_filter_review_decision ON tender_filter_review(ai_decision);

SELECT '✓ tender_filter_review 表已创建' as status;

-- 7. 要求编辑草稿表（新结构）
CREATE TABLE tender_requirements_draft (
    draft_id INTEGER PRIMARY KEY AUTOINCREMENT,
    requirement_id INTEGER,
    project_id INTEGER NOT NULL,  -- ✅ 只保留 project_id

    -- 草稿内容
    constraint_type VARCHAR(20) NOT NULL,
    category VARCHAR(50) NOT NULL,
    subcategory VARCHAR(100),
    detail TEXT NOT NULL,
    source_location VARCHAR(255),
    priority VARCHAR(10) DEFAULT 'medium',

    -- 编辑操作
    operation VARCHAR(20) NOT NULL,  -- add/edit/delete
    edited_by VARCHAR(100),
    edited_at TIMESTAMP,

    -- 草稿状态
    is_published BOOLEAN DEFAULT FALSE,
    published_at TIMESTAMP,

    -- 元数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (requirement_id) REFERENCES tender_requirements(requirement_id) ON DELETE CASCADE,
    FOREIGN KEY (project_id) REFERENCES tender_projects(project_id) ON DELETE CASCADE
);

CREATE INDEX idx_draft_project ON tender_requirements_draft(project_id);
CREATE INDEX idx_draft_requirement ON tender_requirements_draft(requirement_id);
CREATE INDEX idx_draft_published ON tender_requirements_draft(is_published);

SELECT '✓ tender_requirements_draft 表已创建' as status;

-- 8. HITL 任务状态表（新结构，project_id 作为主键）
CREATE TABLE tender_hitl_tasks (
    project_id INTEGER PRIMARY KEY,  -- ✅ 改为主键（一个项目一个 HITL 任务）

    -- 步骤状态
    step1_status VARCHAR(20) DEFAULT 'pending',
    step1_completed_at TIMESTAMP,
    step1_data TEXT,

    step2_status VARCHAR(20) DEFAULT 'pending',
    step2_completed_at TIMESTAMP,
    step2_data TEXT,

    step3_status VARCHAR(20) DEFAULT 'pending',
    step3_completed_at TIMESTAMP,
    step3_data TEXT,

    -- 全局状态
    current_step INTEGER DEFAULT 1,
    overall_status VARCHAR(20) DEFAULT 'in_progress',

    -- 成本预估
    estimated_cost FLOAT DEFAULT 0.0,
    estimated_words INTEGER DEFAULT 0,

    -- 元数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (project_id) REFERENCES tender_projects(project_id) ON DELETE CASCADE
);

CREATE INDEX idx_hitl_current_step ON tender_hitl_tasks(current_step);
CREATE INDEX idx_hitl_overall_status ON tender_hitl_tasks(overall_status);

SELECT '✓ tender_hitl_tasks 表已创建' as status;

-- 9. 用户操作日志表（新结构）
CREATE TABLE tender_user_actions (
    action_id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,  -- ✅ 只保留 project_id
    user_id VARCHAR(100),

    -- 操作信息
    action_type VARCHAR(50) NOT NULL,
    action_step INTEGER,
    action_data TEXT,

    -- 元数据
    ip_address VARCHAR(50),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (project_id) REFERENCES tender_projects(project_id) ON DELETE CASCADE
);

CREATE INDEX idx_actions_project ON tender_user_actions(project_id);
CREATE INDEX idx_actions_type ON tender_user_actions(action_type);
CREATE INDEX idx_actions_created ON tender_user_actions(created_at DESC);

SELECT '✓ tender_user_actions 表已创建' as status;

-- ===================================================================
-- 第三部分：创建触发器
-- ===================================================================

CREATE TRIGGER update_chunks_timestamp
AFTER UPDATE ON tender_document_chunks
BEGIN
    UPDATE tender_document_chunks
    SET updated_at = CURRENT_TIMESTAMP
    WHERE chunk_id = NEW.chunk_id;
END;

CREATE TRIGGER update_requirements_timestamp
AFTER UPDATE ON tender_requirements
BEGIN
    UPDATE tender_requirements
    SET updated_at = CURRENT_TIMESTAMP
    WHERE requirement_id = NEW.requirement_id;
END;

CREATE TRIGGER update_logs_timestamp
AFTER UPDATE ON tender_processing_logs
BEGIN
    UPDATE tender_processing_logs
    SET updated_at = CURRENT_TIMESTAMP
    WHERE log_id = NEW.log_id;
END;

CREATE TRIGGER update_chapters_timestamp
AFTER UPDATE ON tender_document_chapters
BEGIN
    UPDATE tender_document_chapters
    SET updated_at = CURRENT_TIMESTAMP
    WHERE chapter_id = NEW.chapter_id;
END;

CREATE TRIGGER update_filter_review_timestamp
AFTER UPDATE ON tender_filter_review
BEGIN
    UPDATE tender_filter_review
    SET updated_at = CURRENT_TIMESTAMP
    WHERE review_id = NEW.review_id;
END;

CREATE TRIGGER update_draft_timestamp
AFTER UPDATE ON tender_requirements_draft
BEGIN
    UPDATE tender_requirements_draft
    SET updated_at = CURRENT_TIMESTAMP
    WHERE draft_id = NEW.draft_id;
END;

CREATE TRIGGER update_hitl_tasks_timestamp
AFTER UPDATE ON tender_hitl_tasks
BEGIN
    UPDATE tender_hitl_tasks
    SET updated_at = CURRENT_TIMESTAMP
    WHERE project_id = NEW.project_id;
END;

SELECT '✓ 触发器已创建' as status;

-- ===================================================================
-- 第四部分：数据迁移（从备份表迁移到新表）
-- ===================================================================

SELECT '========================================' as separator;
SELECT '开始数据迁移（保留每个项目的最新记录）...' as status;
SELECT '========================================' as separator;

-- 策略：对于每个 project_id，只保留 created_at 最大的那条记录

-- 1. 迁移 tender_hitl_tasks
INSERT INTO tender_hitl_tasks (
    project_id, step1_status, step1_completed_at, step1_data,
    step2_status, step2_completed_at, step2_data,
    step3_status, step3_completed_at, step3_data,
    current_step, overall_status, estimated_cost, estimated_words,
    created_at, updated_at
)
SELECT
    h.project_id, h.step1_status, h.step1_completed_at, h.step1_data,
    h.step2_status, h.step2_completed_at, h.step2_data,
    h.step3_status, h.step3_completed_at, h.step3_data,
    h.current_step, h.overall_status, h.estimated_cost, h.estimated_words,
    h.created_at, h.updated_at
FROM tender_hitl_tasks_backup h
INNER JOIN (
    SELECT project_id, MAX(created_at) as max_created
    FROM tender_hitl_tasks_backup
    GROUP BY project_id
) latest ON h.project_id = latest.project_id AND h.created_at = latest.max_created;

SELECT '✓ tender_hitl_tasks 迁移完成 (' || CHANGES() || ' 条记录)' as status;

-- 2. 迁移 tender_processing_tasks
INSERT INTO tender_processing_tasks (
    project_id, pipeline_config, options, overall_status, current_step,
    progress_percentage, total_chunks, valuable_chunks, total_requirements,
    created_at, started_at, completed_at
)
SELECT
    t.project_id, t.pipeline_config, t.options, t.overall_status, t.current_step,
    t.progress_percentage, t.total_chunks, t.valuable_chunks, t.total_requirements,
    t.created_at, t.started_at, t.completed_at
FROM tender_processing_tasks_backup t
INNER JOIN (
    SELECT project_id, MAX(created_at) as max_created
    FROM tender_processing_tasks_backup
    GROUP BY project_id
) latest ON t.project_id = latest.project_id AND t.created_at = latest.max_created;

SELECT '✓ tender_processing_tasks 迁移完成 (' || CHANGES() || ' 条记录)' as status;

-- 3. 迁移 tender_processing_logs
INSERT INTO tender_processing_logs (
    log_id, project_id, step, status, total_items, processed_items,
    success_items, failed_items, cost_estimation, actual_cost, api_calls,
    total_tokens, started_at, completed_at, estimated_duration, actual_duration,
    error_message, error_details, created_at, updated_at
)
SELECT
    l.log_id, l.project_id, l.step, l.status, l.total_items, l.processed_items,
    l.success_items, l.failed_items, l.cost_estimation, l.actual_cost, l.api_calls,
    l.total_tokens, l.started_at, l.completed_at, l.estimated_duration, l.actual_duration,
    l.error_message, l.error_details, l.created_at, l.updated_at
FROM tender_processing_logs_backup l
INNER JOIN (
    SELECT project_id, MAX(created_at) as max_created
    FROM tender_processing_logs_backup
    GROUP BY project_id
) latest ON l.project_id = latest.project_id AND l.created_at = latest.max_created;

SELECT '✓ tender_processing_logs 迁移完成 (' || CHANGES() || ' 条记录)' as status;

-- 4. 迁移 tender_document_chunks（根据 hitl_task_id 关联到最新任务）
INSERT INTO tender_document_chunks (
    chunk_id, project_id, chunk_index, chunk_type, content, metadata,
    is_valuable, filter_confidence, filtered_at, filter_model,
    created_at, updated_at
)
SELECT
    c.chunk_id, c.project_id, c.chunk_index, c.chunk_type, c.content, c.metadata,
    c.is_valuable, c.filter_confidence, c.filtered_at, c.filter_model,
    c.created_at, c.updated_at
FROM tender_document_chunks_backup c
WHERE c.hitl_task_id IN (
    SELECT h.hitl_task_id
    FROM tender_hitl_tasks_backup h
    INNER JOIN (
        SELECT project_id, MAX(created_at) as max_created
        FROM tender_hitl_tasks_backup
        GROUP BY project_id
    ) latest ON h.project_id = latest.project_id AND h.created_at = latest.max_created
)
OR c.hitl_task_id IS NULL;

SELECT '✓ tender_document_chunks 迁移完成 (' || CHANGES() || ' 条记录)' as status;

-- 5. 迁移 tender_requirements（根据 hitl_task_id 关联到最新任务）
INSERT INTO tender_requirements (
    requirement_id, project_id, chunk_id, constraint_type, category, subcategory,
    detail, summary, source_location, priority, extraction_confidence,
    extraction_model, extracted_at, is_verified, verified_by, verified_at,
    notes, created_at, updated_at
)
SELECT
    r.requirement_id, r.project_id, r.chunk_id, r.constraint_type, r.category, r.subcategory,
    r.detail, r.summary, r.source_location, r.priority, r.extraction_confidence,
    r.extraction_model, r.extracted_at, r.is_verified, r.verified_by, r.verified_at,
    r.notes, r.created_at, r.updated_at
FROM tender_requirements_backup r
WHERE r.hitl_task_id IN (
    SELECT h.hitl_task_id
    FROM tender_hitl_tasks_backup h
    INNER JOIN (
        SELECT project_id, MAX(created_at) as max_created
        FROM tender_hitl_tasks_backup
        GROUP BY project_id
    ) latest ON h.project_id = latest.project_id AND h.created_at = latest.max_created
)
OR r.hitl_task_id IS NULL;

SELECT '✓ tender_requirements 迁移完成 (' || CHANGES() || ' 条记录)' as status;

-- 6. 迁移 tender_document_chapters（根据 task_id 关联到最新任务）
INSERT INTO tender_document_chapters (
    chapter_id, project_id, chapter_node_id, level, title, para_start_idx,
    para_end_idx, word_count, preview_text, is_selected, auto_selected,
    skip_recommended, parent_chapter_id, created_at, updated_at
)
SELECT
    ch.chapter_id, ch.project_id, ch.chapter_node_id, ch.level, ch.title, ch.para_start_idx,
    ch.para_end_idx, ch.word_count, ch.preview_text, ch.is_selected, ch.auto_selected,
    ch.skip_recommended, ch.parent_chapter_id, ch.created_at, ch.updated_at
FROM tender_document_chapters_backup ch
WHERE ch.task_id IN (
    SELECT t.task_id
    FROM tender_processing_tasks_backup t
    INNER JOIN (
        SELECT project_id, MAX(created_at) as max_created
        FROM tender_processing_tasks_backup
        GROUP BY project_id
    ) latest ON t.project_id = latest.project_id AND t.created_at = latest.max_created
);

SELECT '✓ tender_document_chapters 迁移完成 (' || CHANGES() || ' 条记录)' as status;

-- 7. 迁移 tender_filter_review（根据 task_id 关联到最新任务）
INSERT INTO tender_filter_review (
    review_id, chunk_id, project_id, ai_decision, ai_confidence, ai_reasoning,
    user_decision, reviewed_by, reviewed_at, review_notes, created_at, updated_at
)
SELECT
    fr.review_id, fr.chunk_id, fr.project_id, fr.ai_decision, fr.ai_confidence, fr.ai_reasoning,
    fr.user_decision, fr.reviewed_by, fr.reviewed_at, fr.review_notes, fr.created_at, fr.updated_at
FROM tender_filter_review_backup fr
WHERE fr.task_id IN (
    SELECT t.task_id
    FROM tender_processing_tasks_backup t
    INNER JOIN (
        SELECT project_id, MAX(created_at) as max_created
        FROM tender_processing_tasks_backup
        GROUP BY project_id
    ) latest ON t.project_id = latest.project_id AND t.created_at = latest.max_created
);

SELECT '✓ tender_filter_review 迁移完成 (' || CHANGES() || ' 条记录)' as status;

-- 8. 迁移 tender_requirements_draft（根据 task_id 关联到最新任务）
INSERT INTO tender_requirements_draft (
    draft_id, requirement_id, project_id, constraint_type, category, subcategory,
    detail, source_location, priority, operation, edited_by, edited_at,
    is_published, published_at, created_at, updated_at
)
SELECT
    rd.draft_id, rd.requirement_id, rd.project_id, rd.constraint_type, rd.category, rd.subcategory,
    rd.detail, rd.source_location, rd.priority, rd.operation, rd.edited_by, rd.edited_at,
    rd.is_published, rd.published_at, rd.created_at, rd.updated_at
FROM tender_requirements_draft_backup rd
WHERE rd.task_id IN (
    SELECT t.task_id
    FROM tender_processing_tasks_backup t
    INNER JOIN (
        SELECT project_id, MAX(created_at) as max_created
        FROM tender_processing_tasks_backup
        GROUP BY project_id
    ) latest ON t.project_id = latest.project_id AND t.created_at = latest.max_created
);

SELECT '✓ tender_requirements_draft 迁移完成 (' || CHANGES() || ' 条记录)' as status;

-- 9. 迁移 tender_user_actions（保留所有记录，task_id 字段已删除）
INSERT INTO tender_user_actions (
    action_id, project_id, user_id, action_type, action_step, action_data,
    ip_address, user_agent, created_at
)
SELECT
    ua.action_id, ua.project_id, ua.user_id, ua.action_type, ua.action_step, ua.action_data,
    ua.ip_address, ua.user_agent, ua.created_at
FROM tender_user_actions_backup ua;

SELECT '✓ tender_user_actions 迁移完成 (' || CHANGES() || ' 条记录)' as status;

-- ===================================================================
-- 第五部分：重建视图
-- ===================================================================

SELECT '========================================' as separator;
SELECT '开始重建视图...' as status;
SELECT '========================================' as separator;

-- 视图1：处理统计概览（新版本）
CREATE VIEW v_processing_statistics AS
SELECT
    t.project_id,
    t.overall_status,
    t.progress_percentage,
    t.total_chunks,
    t.valuable_chunks,
    t.total_requirements,
    -- 成本汇总
    l.actual_cost as total_cost,
    l.api_calls as total_api_calls,
    l.total_tokens as total_tokens,
    -- 时间汇总
    t.created_at,
    t.started_at,
    t.completed_at,
    CASE
        WHEN t.completed_at IS NOT NULL AND t.started_at IS NOT NULL
        THEN CAST((julianday(t.completed_at) - julianday(t.started_at)) * 86400 AS INTEGER)
        ELSE NULL
    END as duration_seconds
FROM tender_processing_tasks t
LEFT JOIN tender_processing_logs l ON t.project_id = l.project_id;

SELECT '✓ v_processing_statistics 视图已创建' as status;

-- 视图2：要求分类统计
CREATE VIEW v_requirements_summary AS
SELECT
    project_id,
    constraint_type,
    category,
    COUNT(*) as count,
    COUNT(CASE WHEN is_verified = 1 THEN 1 END) as verified_count,
    AVG(extraction_confidence) as avg_confidence
FROM tender_requirements
GROUP BY project_id, constraint_type, category;

SELECT '✓ v_requirements_summary 视图已创建' as status;

-- 视图3：HITL 进度概览（新版本）
CREATE VIEW v_hitl_progress AS
SELECT
    h.project_id,
    h.current_step,
    h.overall_status,

    -- 步骤1统计
    (SELECT COUNT(*) FROM tender_document_chapters
     WHERE project_id = h.project_id) as total_chapters,
    (SELECT COUNT(*) FROM tender_document_chapters
     WHERE project_id = h.project_id AND is_selected = 1) as selected_chapters,

    -- 步骤2统计
    (SELECT COUNT(*) FROM tender_filter_review r
     JOIN tender_document_chunks c ON r.chunk_id = c.chunk_id
     WHERE r.project_id = h.project_id AND r.ai_decision = 'NON-REQUIREMENT') as filtered_chunks,
    (SELECT COUNT(*) FROM tender_filter_review r
     WHERE r.project_id = h.project_id AND r.user_decision = 'restore') as restored_chunks,

    -- 步骤3统计
    (SELECT COUNT(*) FROM tender_requirements_draft
     WHERE project_id = h.project_id) as draft_requirements,
    (SELECT COUNT(*) FROM tender_requirements_draft
     WHERE project_id = h.project_id AND is_published = 1) as published_requirements,

    -- 时间统计
    h.created_at,
    h.updated_at,
    CASE
        WHEN h.step3_completed_at IS NOT NULL
        THEN CAST((julianday(h.step3_completed_at) - julianday(h.created_at)) * 86400 AS INTEGER)
        ELSE NULL
    END as total_duration_seconds

FROM tender_hitl_tasks h;

SELECT '✓ v_hitl_progress 视图已创建' as status;

-- 视图4：章节选择统计（新版本）
CREATE VIEW v_chapter_selection_stats AS
SELECT
    project_id,
    COUNT(*) as total_chapters,
    SUM(CASE WHEN is_selected = 1 THEN 1 ELSE 0 END) as selected_count,
    SUM(CASE WHEN auto_selected = 1 THEN 1 ELSE 0 END) as auto_selected_count,
    SUM(CASE WHEN skip_recommended = 1 THEN 1 ELSE 0 END) as skip_recommended_count,
    SUM(CASE WHEN is_selected = 1 THEN word_count ELSE 0 END) as selected_words
FROM tender_document_chapters
GROUP BY project_id;

SELECT '✓ v_chapter_selection_stats 视图已创建' as status;

-- ===================================================================
-- 第六部分：迁移完成统计
-- ===================================================================

SELECT '========================================' as separator;
SELECT '迁移完成汇总' as title;
SELECT '========================================' as separator;

SELECT
    '✓ 新表结构' as category,
    (SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name LIKE 'tender_%') as count;

SELECT
    '✓ tender_hitl_tasks' as table_name,
    (SELECT COUNT(*) FROM tender_hitl_tasks) as records;

SELECT
    '✓ tender_processing_tasks' as table_name,
    (SELECT COUNT(*) FROM tender_processing_tasks) as records;

SELECT
    '✓ tender_document_chunks' as table_name,
    (SELECT COUNT(*) FROM tender_document_chunks) as records;

SELECT
    '✓ tender_requirements' as table_name,
    (SELECT COUNT(*) FROM tender_requirements) as records;

SELECT
    '✓ tender_document_chapters' as table_name,
    (SELECT COUNT(*) FROM tender_document_chapters) as records;

SELECT
    '✓ tender_filter_review' as table_name,
    (SELECT COUNT(*) FROM tender_filter_review) as records;

SELECT
    '✓ tender_requirements_draft' as table_name,
    (SELECT COUNT(*) FROM tender_requirements_draft) as records;

SELECT
    '✓ tender_processing_logs' as table_name,
    (SELECT COUNT(*) FROM tender_processing_logs) as records;

SELECT
    '✓ tender_user_actions' as table_name,
    (SELECT COUNT(*) FROM tender_user_actions) as records;

SELECT '========================================' as separator;
SELECT '✓ 数据库重构完成！' as status;
SELECT '备份表保留在数据库中（以 _backup 后缀标识）' as note;
SELECT '如需回滚，请使用备份表恢复数据' as note2;
SELECT '========================================' as separator;

COMMIT;

-- 重构完成！
-- 下一步：修改 Python 代码以使用新的数据库结构
