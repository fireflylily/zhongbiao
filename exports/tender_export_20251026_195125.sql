-- Database export: tender
-- Export date: 2025-10-26T19:51:25.713842
-- Source: /Users/lvhe/Downloads/zhongbiao/zhongbiao/ai_tender_system/data/tender.db

-- Disable foreign key checks during import
PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;

CREATE TABLE tender_document_chapters (
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
CREATE TABLE tender_document_chunks (
    chunk_id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    chunk_index INTEGER NOT NULL,  -- 块的顺序索引
    chunk_type VARCHAR(50) NOT NULL,  -- title/paragraph/table/list
    content TEXT NOT NULL,
    metadata TEXT,  -- JSON格式: {section_title, page_number, token_count, parent_section}

    -- 筛选字段
    is_valuable BOOLEAN DEFAULT NULL,  -- NULL=未筛选, TRUE=高价值, FALSE=低价值
    filter_confidence FLOAT DEFAULT NULL,  -- 筛选置信度 0.0-1.0
    filtered_at TIMESTAMP DEFAULT NULL,
    filter_model VARCHAR(50) DEFAULT NULL,  -- 使用的筛选模型

    -- 元数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, hitl_task_id VARCHAR(100),

    FOREIGN KEY (project_id) REFERENCES tender_projects(project_id) ON DELETE CASCADE
);
CREATE TABLE tender_filter_review (
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
CREATE TABLE tender_hitl_tasks (
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
CREATE TABLE tender_processing_logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    task_id VARCHAR(100) UNIQUE,  -- 唯一任务ID（用于前端查询进度）

    -- 流程步骤
    step VARCHAR(20) NOT NULL,  -- chunking/filtering/extraction/completed/failed
    status VARCHAR(20) NOT NULL DEFAULT 'pending',  -- pending/processing/completed/failed/cancelled

    -- 进度信息
    total_items INTEGER DEFAULT 0,  -- 总项目数
    processed_items INTEGER DEFAULT 0,  -- 已处理项目数
    success_items INTEGER DEFAULT 0,  -- 成功项目数
    failed_items INTEGER DEFAULT 0,  -- 失败项目数

    -- 成本统计
    cost_estimation FLOAT DEFAULT 0.0,  -- 预估成本（美元）
    actual_cost FLOAT DEFAULT 0.0,  -- 实际成本（美元）
    api_calls INTEGER DEFAULT 0,  -- API调用次数
    total_tokens INTEGER DEFAULT 0,  -- 总token消耗

    -- 时间统计
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    estimated_duration INTEGER,  -- 预估耗时（秒）
    actual_duration INTEGER,  -- 实际耗时（秒）

    -- 错误信息
    error_message TEXT,
    error_details TEXT,  -- JSON格式的详细错误信息

    -- 元数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (project_id) REFERENCES tender_projects(project_id) ON DELETE CASCADE
);
CREATE TABLE tender_processing_tasks (
    task_id VARCHAR(100) PRIMARY KEY,
    project_id INTEGER NOT NULL,

    -- 任务配置
    pipeline_config TEXT,  -- JSON格式的流程配置
    options TEXT,  -- JSON格式的处理选项

    -- 任务状态
    overall_status VARCHAR(20) DEFAULT 'pending',  -- pending/running/completed/failed/cancelled
    current_step VARCHAR(20),  -- 当前执行的步骤
    progress_percentage FLOAT DEFAULT 0.0,  -- 总体进度百分比

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
CREATE TABLE tender_requirements (
    requirement_id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    chunk_id INTEGER,  -- 来源分块ID，可为NULL（合并多个块的要求）

    -- 要求分类
    constraint_type VARCHAR(20) NOT NULL,  -- mandatory（强制性）/optional（可选）/scoring（加分项）
    category VARCHAR(50) NOT NULL,  -- qualification（资质）/technical（技术）/commercial（商务）/service（服务）
    subcategory VARCHAR(100),  -- 子类别，如：证书类型、技术指标类型

    -- 要求内容
    detail TEXT NOT NULL,  -- 具体要求描述
    summary VARCHAR(200),  -- 简洁摘要（60字以内），方便快速浏览
    source_location VARCHAR(255),  -- 来源位置（章节标题、页码）
    priority VARCHAR(10) DEFAULT 'medium',  -- high/medium/low

    -- AI提取元数据
    extraction_confidence FLOAT DEFAULT NULL,  -- 提取置信度
    extraction_model VARCHAR(50) DEFAULT NULL,  -- 使用的提取模型
    extracted_at TIMESTAMP DEFAULT NULL,

    -- 验证和审核
    is_verified BOOLEAN DEFAULT FALSE,  -- 人工验证标记
    verified_by VARCHAR(100),
    verified_at TIMESTAMP,
    notes TEXT,  -- 审核备注

    -- 元数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (project_id) REFERENCES tender_projects(project_id) ON DELETE CASCADE,
    FOREIGN KEY (chunk_id) REFERENCES tender_document_chunks(chunk_id) ON DELETE SET NULL
);
CREATE TABLE tender_requirements_draft (
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
CREATE TABLE tender_user_actions (
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
CREATE INDEX idx_chunks_project_id ON tender_document_chunks(project_id);
CREATE INDEX idx_chunks_project_index ON tender_document_chunks(project_id, chunk_index);
CREATE INDEX idx_chunks_valuable ON tender_document_chunks(project_id, is_valuable);
CREATE INDEX idx_chunks_type ON tender_document_chunks(chunk_type);
CREATE INDEX idx_requirements_project_id ON tender_requirements(project_id);
CREATE INDEX idx_requirements_type ON tender_requirements(project_id, constraint_type);
CREATE INDEX idx_requirements_category ON tender_requirements(project_id, category);
CREATE INDEX idx_requirements_priority ON tender_requirements(priority);
CREATE INDEX idx_requirements_verified ON tender_requirements(is_verified);
CREATE INDEX idx_logs_project_id ON tender_processing_logs(project_id);
CREATE INDEX idx_logs_task_id ON tender_processing_logs(task_id);
CREATE INDEX idx_logs_step_status ON tender_processing_logs(step, status);
CREATE INDEX idx_logs_created_at ON tender_processing_logs(created_at DESC);
CREATE INDEX idx_tasks_project_id ON tender_processing_tasks(project_id);
CREATE INDEX idx_tasks_status ON tender_processing_tasks(overall_status);
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
CREATE VIEW v_processing_statistics AS
SELECT
    t.project_id,
    t.task_id,
    t.overall_status,
    t.progress_percentage,
    t.total_chunks,
    t.valuable_chunks,
    t.total_requirements,
    -- 成本汇总
    SUM(l.actual_cost) as total_cost,
    SUM(l.api_calls) as total_api_calls,
    SUM(l.total_tokens) as total_tokens,
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
LEFT JOIN tender_processing_logs l ON t.task_id = l.task_id
GROUP BY t.task_id;
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
CREATE INDEX idx_chapters_project_task ON tender_document_chapters(project_id, task_id);
CREATE INDEX idx_chapters_selected ON tender_document_chapters(is_selected);
CREATE INDEX idx_chapters_node_id ON tender_document_chapters(chapter_node_id);
CREATE INDEX idx_filter_review_project_task ON tender_filter_review(project_id, task_id);
CREATE INDEX idx_filter_review_chunk ON tender_filter_review(chunk_id);
CREATE INDEX idx_filter_review_decision ON tender_filter_review(ai_decision);
CREATE INDEX idx_draft_project_task ON tender_requirements_draft(project_id, task_id);
CREATE INDEX idx_draft_requirement ON tender_requirements_draft(requirement_id);
CREATE INDEX idx_draft_published ON tender_requirements_draft(is_published);
CREATE INDEX idx_hitl_project ON tender_hitl_tasks(project_id);
CREATE INDEX idx_hitl_task ON tender_hitl_tasks(task_id);
CREATE INDEX idx_hitl_current_step ON tender_hitl_tasks(current_step);
CREATE INDEX idx_hitl_overall_status ON tender_hitl_tasks(overall_status);
CREATE INDEX idx_actions_project ON tender_user_actions(project_id);
CREATE INDEX idx_actions_task ON tender_user_actions(task_id);
CREATE INDEX idx_actions_type ON tender_user_actions(action_type);
CREATE INDEX idx_actions_created ON tender_user_actions(created_at DESC);
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
    WHERE hitl_task_id = NEW.hitl_task_id;
END;
CREATE VIEW v_hitl_progress AS
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
CREATE VIEW v_chapter_selection_stats AS
SELECT
    task_id,
    COUNT(*) as total_chapters,
    SUM(CASE WHEN is_selected = 1 THEN 1 ELSE 0 END) as selected_count,
    SUM(CASE WHEN auto_selected = 1 THEN 1 ELSE 0 END) as auto_selected_count,
    SUM(CASE WHEN skip_recommended = 1 THEN 1 ELSE 0 END) as skip_recommended_count,
    SUM(CASE WHEN is_selected = 1 THEN word_count ELSE 0 END) as selected_words
FROM tender_document_chapters
GROUP BY task_id;
CREATE INDEX idx_chunks_hitl_task
ON tender_document_chunks(hitl_task_id);
CREATE INDEX idx_chunks_project_hitl
ON tender_document_chunks(project_id, hitl_task_id);
DELETE FROM "sqlite_sequence";

COMMIT;
PRAGMA foreign_keys=ON;
