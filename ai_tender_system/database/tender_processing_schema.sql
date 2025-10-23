-- =====================================================
-- 标书智能处理系统数据库Schema
-- 三步处理流程：文档分块 -> AI筛选 -> 精准提取
-- =====================================================

-- 1. 文档分块表
CREATE TABLE IF NOT EXISTS tender_document_chunks (
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
    hitl_task_id VARCHAR(100),  -- HITL任务ID，用于按任务隔离chunks

    -- 元数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (project_id) REFERENCES tender_projects(project_id) ON DELETE CASCADE
);

-- 为分块表创建索引
CREATE INDEX IF NOT EXISTS idx_chunks_project_id ON tender_document_chunks(project_id);
CREATE INDEX IF NOT EXISTS idx_chunks_project_index ON tender_document_chunks(project_id, chunk_index);
CREATE INDEX IF NOT EXISTS idx_chunks_valuable ON tender_document_chunks(project_id, is_valuable);
CREATE INDEX IF NOT EXISTS idx_chunks_type ON tender_document_chunks(chunk_type);
CREATE INDEX IF NOT EXISTS idx_chunks_hitl_task ON tender_document_chunks(hitl_task_id);
CREATE INDEX IF NOT EXISTS idx_chunks_project_hitl ON tender_document_chunks(project_id, hitl_task_id);


-- 2. 提取的要求表
CREATE TABLE IF NOT EXISTS tender_requirements (
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
    hitl_task_id VARCHAR(100),  -- HITL任务ID，用于按任务隔离需求

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

-- 为要求表创建索引
CREATE INDEX IF NOT EXISTS idx_requirements_project_id ON tender_requirements(project_id);
CREATE INDEX IF NOT EXISTS idx_requirements_type ON tender_requirements(project_id, constraint_type);
CREATE INDEX IF NOT EXISTS idx_requirements_category ON tender_requirements(project_id, category);
CREATE INDEX IF NOT EXISTS idx_requirements_priority ON tender_requirements(priority);
CREATE INDEX IF NOT EXISTS idx_requirements_verified ON tender_requirements(is_verified);
CREATE INDEX IF NOT EXISTS idx_requirements_hitl_task ON tender_requirements(hitl_task_id);
CREATE INDEX IF NOT EXISTS idx_requirements_project_hitl ON tender_requirements(project_id, hitl_task_id);


-- 3. 处理日志表
CREATE TABLE IF NOT EXISTS tender_processing_logs (
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

-- 为日志表创建索引
CREATE INDEX IF NOT EXISTS idx_logs_project_id ON tender_processing_logs(project_id);
CREATE INDEX IF NOT EXISTS idx_logs_task_id ON tender_processing_logs(task_id);
CREATE INDEX IF NOT EXISTS idx_logs_step_status ON tender_processing_logs(step, status);
CREATE INDEX IF NOT EXISTS idx_logs_created_at ON tender_processing_logs(created_at DESC);


-- 4. 处理任务表（用于异步任务管理）
CREATE TABLE IF NOT EXISTS tender_processing_tasks (
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

CREATE INDEX IF NOT EXISTS idx_tasks_project_id ON tender_processing_tasks(project_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tender_processing_tasks(overall_status);


-- 5. 更新触发器（自动更新updated_at字段）
CREATE TRIGGER IF NOT EXISTS update_chunks_timestamp
AFTER UPDATE ON tender_document_chunks
BEGIN
    UPDATE tender_document_chunks
    SET updated_at = CURRENT_TIMESTAMP
    WHERE chunk_id = NEW.chunk_id;
END;

CREATE TRIGGER IF NOT EXISTS update_requirements_timestamp
AFTER UPDATE ON tender_requirements
BEGIN
    UPDATE tender_requirements
    SET updated_at = CURRENT_TIMESTAMP
    WHERE requirement_id = NEW.requirement_id;
END;

CREATE TRIGGER IF NOT EXISTS update_logs_timestamp
AFTER UPDATE ON tender_processing_logs
BEGIN
    UPDATE tender_processing_logs
    SET updated_at = CURRENT_TIMESTAMP
    WHERE log_id = NEW.log_id;
END;


-- =====================================================
-- 视图：处理统计概览
-- =====================================================

CREATE VIEW IF NOT EXISTS v_processing_statistics AS
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


-- =====================================================
-- 视图：要求分类统计
-- =====================================================

CREATE VIEW IF NOT EXISTS v_requirements_summary AS
SELECT
    project_id,
    constraint_type,
    category,
    COUNT(*) as count,
    COUNT(CASE WHEN is_verified = 1 THEN 1 END) as verified_count,
    AVG(extraction_confidence) as avg_confidence
FROM tender_requirements
GROUP BY project_id, constraint_type, category;
