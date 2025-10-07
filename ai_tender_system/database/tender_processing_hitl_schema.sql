-- =====================================================
-- 标书智能处理系统 - HITL（Human-in-the-Loop）扩展Schema
-- 支持三步人工确认流程
-- =====================================================

-- 1. 文档章节表（用于步骤1：章节选择）
CREATE TABLE IF NOT EXISTS tender_document_chapters (
    chapter_id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    task_id VARCHAR(100) NOT NULL,

    -- 章节信息
    chapter_node_id VARCHAR(50) NOT NULL,  -- 如 "ch_1_2_3"
    level INTEGER NOT NULL,  -- 1-3 层级
    title VARCHAR(500) NOT NULL,
    para_start_idx INTEGER NOT NULL,  -- 起始段落索引
    para_end_idx INTEGER,  -- 结束段落索引
    word_count INTEGER DEFAULT 0,
    preview_text TEXT,  -- 预览文本

    -- 选择状态
    is_selected BOOLEAN DEFAULT FALSE,  -- 用户是否选中
    auto_selected BOOLEAN DEFAULT FALSE,  -- 自动推荐选中
    skip_recommended BOOLEAN DEFAULT FALSE,  -- 推荐跳过

    -- 父子关系
    parent_chapter_id INTEGER,  -- 父章节ID

    -- 元数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (project_id) REFERENCES tender_projects(project_id) ON DELETE CASCADE,
    FOREIGN KEY (parent_chapter_id) REFERENCES tender_document_chapters(chapter_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_chapters_project_task ON tender_document_chapters(project_id, task_id);
CREATE INDEX IF NOT EXISTS idx_chapters_selected ON tender_document_chapters(is_selected);
CREATE INDEX IF NOT EXISTS idx_chapters_node_id ON tender_document_chapters(chapter_node_id);


-- 2. 筛选复核表（用于步骤2：AI筛选复核）
CREATE TABLE IF NOT EXISTS tender_filter_review (
    review_id INTEGER PRIMARY KEY AUTOINCREMENT,
    chunk_id INTEGER NOT NULL,
    project_id INTEGER NOT NULL,
    task_id VARCHAR(100) NOT NULL,

    -- 原始筛选结果
    ai_decision VARCHAR(20) NOT NULL,  -- 'REQUIREMENT' 或 'NON-REQUIREMENT'
    ai_confidence FLOAT,  -- AI 置信度 0.0-1.0
    ai_reasoning TEXT,  -- AI 判断理由

    -- 人工复核
    user_decision VARCHAR(20),  -- 用户决策: 'keep', 'restore', 'discard'
    reviewed_by VARCHAR(100),  -- 复核人
    reviewed_at TIMESTAMP,
    review_notes TEXT,  -- 复核备注

    -- 元数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (chunk_id) REFERENCES tender_document_chunks(chunk_id) ON DELETE CASCADE,
    FOREIGN KEY (project_id) REFERENCES tender_projects(project_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_filter_review_project_task ON tender_filter_review(project_id, task_id);
CREATE INDEX IF NOT EXISTS idx_filter_review_chunk ON tender_filter_review(chunk_id);
CREATE INDEX IF NOT EXISTS idx_filter_review_decision ON tender_filter_review(ai_decision);


-- 3. 要求编辑草稿表（用于步骤3：可编辑表格）
CREATE TABLE IF NOT EXISTS tender_requirements_draft (
    draft_id INTEGER PRIMARY KEY AUTOINCREMENT,
    requirement_id INTEGER,  -- NULL 表示新增的要求
    project_id INTEGER NOT NULL,
    task_id VARCHAR(100) NOT NULL,

    -- 草稿内容（与 tender_requirements 字段一致）
    constraint_type VARCHAR(20) NOT NULL,
    category VARCHAR(50) NOT NULL,
    subcategory VARCHAR(100),
    detail TEXT NOT NULL,
    source_location VARCHAR(255),
    priority VARCHAR(10) DEFAULT 'medium',

    -- 编辑操作
    operation VARCHAR(20) NOT NULL,  -- 'add'（新增）/ 'edit'（编辑）/ 'delete'（删除）
    edited_by VARCHAR(100),
    edited_at TIMESTAMP,

    -- 草稿状态
    is_published BOOLEAN DEFAULT FALSE,  -- 是否已发布（写入正式表）
    published_at TIMESTAMP,

    -- 元数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (requirement_id) REFERENCES tender_requirements(requirement_id) ON DELETE CASCADE,
    FOREIGN KEY (project_id) REFERENCES tender_projects(project_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_draft_project_task ON tender_requirements_draft(project_id, task_id);
CREATE INDEX IF NOT EXISTS idx_draft_requirement ON tender_requirements_draft(requirement_id);
CREATE INDEX IF NOT EXISTS idx_draft_published ON tender_requirements_draft(is_published);


-- 4. HITL 任务状态表（跨步骤状态追踪）
CREATE TABLE IF NOT EXISTS tender_hitl_tasks (
    hitl_task_id VARCHAR(100) PRIMARY KEY,
    project_id INTEGER NOT NULL,
    task_id VARCHAR(100) NOT NULL,  -- 关联主处理任务

    -- 步骤状态
    step1_status VARCHAR(20) DEFAULT 'pending',  -- pending/in_progress/completed/skipped
    step1_completed_at TIMESTAMP,
    step1_data TEXT,  -- JSON: 步骤1的选择结果

    step2_status VARCHAR(20) DEFAULT 'pending',
    step2_completed_at TIMESTAMP,
    step2_data TEXT,  -- JSON: 步骤2的复核结果

    step3_status VARCHAR(20) DEFAULT 'pending',
    step3_completed_at TIMESTAMP,
    step3_data TEXT,  -- JSON: 步骤3的编辑结果

    -- 全局状态
    current_step INTEGER DEFAULT 1,  -- 1, 2, 3
    overall_status VARCHAR(20) DEFAULT 'in_progress',  -- in_progress/completed/cancelled

    -- 成本预估
    estimated_cost FLOAT DEFAULT 0.0,
    estimated_words INTEGER DEFAULT 0,

    -- 元数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (project_id) REFERENCES tender_projects(project_id) ON DELETE CASCADE,
    FOREIGN KEY (task_id) REFERENCES tender_processing_tasks(task_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_hitl_project ON tender_hitl_tasks(project_id);
CREATE INDEX IF NOT EXISTS idx_hitl_task ON tender_hitl_tasks(task_id);
CREATE INDEX IF NOT EXISTS idx_hitl_current_step ON tender_hitl_tasks(current_step);
CREATE INDEX IF NOT EXISTS idx_hitl_overall_status ON tender_hitl_tasks(overall_status);


-- 5. 用户操作日志表（审计追踪）
CREATE TABLE IF NOT EXISTS tender_user_actions (
    action_id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    task_id VARCHAR(100),
    user_id VARCHAR(100),  -- 用户ID（可选）

    -- 操作信息
    action_type VARCHAR(50) NOT NULL,  -- 'chapter_selected', 'chunk_restored', 'requirement_edited' 等
    action_step INTEGER,  -- 1, 2, 3
    action_data TEXT,  -- JSON: 操作详细数据

    -- 元数据
    ip_address VARCHAR(50),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (project_id) REFERENCES tender_projects(project_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_actions_project ON tender_user_actions(project_id);
CREATE INDEX IF NOT EXISTS idx_actions_task ON tender_user_actions(task_id);
CREATE INDEX IF NOT EXISTS idx_actions_type ON tender_user_actions(action_type);
CREATE INDEX IF NOT EXISTS idx_actions_created ON tender_user_actions(created_at DESC);


-- 6. 更新触发器
CREATE TRIGGER IF NOT EXISTS update_chapters_timestamp
AFTER UPDATE ON tender_document_chapters
BEGIN
    UPDATE tender_document_chapters
    SET updated_at = CURRENT_TIMESTAMP
    WHERE chapter_id = NEW.chapter_id;
END;

CREATE TRIGGER IF NOT EXISTS update_filter_review_timestamp
AFTER UPDATE ON tender_filter_review
BEGIN
    UPDATE tender_filter_review
    SET updated_at = CURRENT_TIMESTAMP
    WHERE review_id = NEW.review_id;
END;

CREATE TRIGGER IF NOT EXISTS update_draft_timestamp
AFTER UPDATE ON tender_requirements_draft
BEGIN
    UPDATE tender_requirements_draft
    SET updated_at = CURRENT_TIMESTAMP
    WHERE draft_id = NEW.draft_id;
END;

CREATE TRIGGER IF NOT EXISTS update_hitl_tasks_timestamp
AFTER UPDATE ON tender_hitl_tasks
BEGIN
    UPDATE tender_hitl_tasks
    SET updated_at = CURRENT_TIMESTAMP
    WHERE hitl_task_id = NEW.hitl_task_id;
END;


-- =====================================================
-- 视图：HITL 进度概览
-- =====================================================

CREATE VIEW IF NOT EXISTS v_hitl_progress AS
SELECT
    h.hitl_task_id,
    h.project_id,
    h.task_id,
    h.current_step,
    h.overall_status,

    -- 步骤1统计
    (SELECT COUNT(*) FROM tender_document_chapters
     WHERE task_id = h.task_id) as total_chapters,
    (SELECT COUNT(*) FROM tender_document_chapters
     WHERE task_id = h.task_id AND is_selected = 1) as selected_chapters,

    -- 步骤2统计
    (SELECT COUNT(*) FROM tender_filter_review r
     JOIN tender_document_chunks c ON r.chunk_id = c.chunk_id
     WHERE r.task_id = h.task_id AND r.ai_decision = 'NON-REQUIREMENT') as filtered_chunks,
    (SELECT COUNT(*) FROM tender_filter_review r
     WHERE r.task_id = h.task_id AND r.user_decision = 'restore') as restored_chunks,

    -- 步骤3统计
    (SELECT COUNT(*) FROM tender_requirements_draft
     WHERE task_id = h.task_id) as draft_requirements,
    (SELECT COUNT(*) FROM tender_requirements_draft
     WHERE task_id = h.task_id AND is_published = 1) as published_requirements,

    -- 时间统计
    h.created_at,
    h.updated_at,
    CASE
        WHEN h.step3_completed_at IS NOT NULL
        THEN CAST((julianday(h.step3_completed_at) - julianday(h.created_at)) * 86400 AS INTEGER)
        ELSE NULL
    END as total_duration_seconds

FROM tender_hitl_tasks h;


-- =====================================================
-- 视图：章节选择统计
-- =====================================================

CREATE VIEW IF NOT EXISTS v_chapter_selection_stats AS
SELECT
    task_id,
    COUNT(*) as total_chapters,
    SUM(CASE WHEN is_selected = 1 THEN 1 ELSE 0 END) as selected_count,
    SUM(CASE WHEN auto_selected = 1 THEN 1 ELSE 0 END) as auto_selected_count,
    SUM(CASE WHEN skip_recommended = 1 THEN 1 ELSE 0 END) as skip_recommended_count,
    SUM(CASE WHEN is_selected = 1 THEN word_count ELSE 0 END) as selected_words
FROM tender_document_chapters
GROUP BY task_id;
