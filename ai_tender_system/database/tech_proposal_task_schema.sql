-- =====================================================
-- 技术方案生成任务管理Schema
-- 支持断点续传、重试机制、任务状态持久化
-- =====================================================

-- 1. 技术方案任务表
CREATE TABLE IF NOT EXISTS tech_proposal_tasks (
    task_id VARCHAR(50) PRIMARY KEY,  -- UUID格式
    project_id INTEGER NOT NULL,
    company_id INTEGER,

    -- 任务配置
    generation_mode VARCHAR(50),  -- quality_first/by_scoring_point/by_outline
    ai_model VARCHAR(100),
    crew_config TEXT,  -- JSON: CrewConfig完整配置
    tender_file_path VARCHAR(500),
    page_count INTEGER DEFAULT 200,

    -- 任务状态
    overall_status VARCHAR(20) DEFAULT 'pending',  -- pending/running/completed/failed/cancelled
    current_phase VARCHAR(50),  -- 当前执行的阶段
    progress_percentage FLOAT DEFAULT 0.0,

    -- 阶段执行记录
    phases_completed TEXT,  -- JSON: ["scoring_extraction", "product_matching", ...]
    phase_results TEXT,     -- JSON: {phase: {status, start_time, end_time, result_summary}}

    -- 重试信息
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    last_error TEXT,
    last_error_time TIMESTAMP,

    -- 恢复信息
    can_resume BOOLEAN DEFAULT TRUE,  -- 是否可恢复
    saved_state TEXT,  -- JSON: CrewState序列化数据

    -- 结果信息
    output_files TEXT,  -- JSON: [file_path, ...]
    final_score FLOAT,  -- 专家评审最终得分

    -- 时间信息
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    expires_at TIMESTAMP,  -- 恢复过期时间 (created_at + 24小时)

    FOREIGN KEY (project_id) REFERENCES tender_projects(project_id) ON DELETE CASCADE
);

-- 任务表索引
CREATE INDEX IF NOT EXISTS idx_tech_tasks_project ON tech_proposal_tasks(project_id);
CREATE INDEX IF NOT EXISTS idx_tech_tasks_status ON tech_proposal_tasks(overall_status);
CREATE INDEX IF NOT EXISTS idx_tech_tasks_created ON tech_proposal_tasks(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_tech_tasks_resumable ON tech_proposal_tasks(can_resume, overall_status, expires_at);


-- 2. 智能体执行日志表
CREATE TABLE IF NOT EXISTS agent_execution_logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id VARCHAR(50) NOT NULL,

    -- 智能体信息
    agent_name VARCHAR(100) NOT NULL,  -- ScoringPointAgent, ContentWriterAgent等
    phase_name VARCHAR(50) NOT NULL,   -- scoring_extraction, content_writing等

    -- 执行状态
    status VARCHAR(20) NOT NULL,  -- pending/running/success/failed/retrying/skipped
    attempt_number INTEGER DEFAULT 1,

    -- 执行时间
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    duration_ms INTEGER,

    -- 输入输出摘要
    input_summary TEXT,   -- JSON: 输入数据摘要(截断)
    output_summary TEXT,  -- JSON: 输出数据摘要(截断)

    -- 错误信息
    error_message TEXT,
    error_traceback TEXT,

    -- 重试信息
    retry_delay_ms INTEGER,  -- 下次重试延迟

    -- 元数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (task_id) REFERENCES tech_proposal_tasks(task_id) ON DELETE CASCADE
);

-- 日志表索引
CREATE INDEX IF NOT EXISTS idx_agent_logs_task ON agent_execution_logs(task_id);
CREATE INDEX IF NOT EXISTS idx_agent_logs_phase ON agent_execution_logs(phase_name);
CREATE INDEX IF NOT EXISTS idx_agent_logs_status ON agent_execution_logs(status);
CREATE INDEX IF NOT EXISTS idx_agent_logs_created ON agent_execution_logs(created_at DESC);


-- 3. 更新触发器：自动设置过期时间
CREATE TRIGGER IF NOT EXISTS set_task_expires_at
AFTER INSERT ON tech_proposal_tasks
BEGIN
    UPDATE tech_proposal_tasks
    SET expires_at = datetime(NEW.created_at, '+24 hours')
    WHERE task_id = NEW.task_id AND expires_at IS NULL;
END;


-- 4. 更新触发器：任务完成时更新can_resume
CREATE TRIGGER IF NOT EXISTS update_task_on_complete
AFTER UPDATE OF overall_status ON tech_proposal_tasks
WHEN NEW.overall_status IN ('completed', 'cancelled')
BEGIN
    UPDATE tech_proposal_tasks
    SET can_resume = FALSE,
        completed_at = CURRENT_TIMESTAMP
    WHERE task_id = NEW.task_id;
END;


-- =====================================================
-- 视图：可恢复的任务列表
-- =====================================================
CREATE VIEW IF NOT EXISTS v_resumable_tasks AS
SELECT
    t.task_id,
    t.project_id,
    t.company_id,
    t.generation_mode,
    t.overall_status,
    t.current_phase,
    t.progress_percentage,
    t.phases_completed,
    t.retry_count,
    t.last_error,
    t.created_at,
    t.started_at,
    t.expires_at,
    -- 计算剩余恢复时间(秒)
    CAST((julianday(t.expires_at) - julianday('now')) * 86400 AS INTEGER) as seconds_until_expire
FROM tech_proposal_tasks t
WHERE t.can_resume = TRUE
  AND t.overall_status IN ('failed', 'pending')
  AND t.expires_at > datetime('now')
ORDER BY t.created_at DESC;


-- =====================================================
-- 视图：任务执行统计
-- =====================================================
CREATE VIEW IF NOT EXISTS v_task_execution_stats AS
SELECT
    t.task_id,
    t.project_id,
    t.overall_status,
    t.progress_percentage,
    -- 阶段统计
    (SELECT COUNT(*) FROM agent_execution_logs l WHERE l.task_id = t.task_id AND l.status = 'success') as successful_phases,
    (SELECT COUNT(*) FROM agent_execution_logs l WHERE l.task_id = t.task_id AND l.status = 'failed') as failed_phases,
    (SELECT COUNT(*) FROM agent_execution_logs l WHERE l.task_id = t.task_id AND l.status = 'skipped') as skipped_phases,
    -- 重试统计
    (SELECT SUM(l.attempt_number - 1) FROM agent_execution_logs l WHERE l.task_id = t.task_id) as total_retries,
    -- 耗时统计
    (SELECT SUM(l.duration_ms) FROM agent_execution_logs l WHERE l.task_id = t.task_id) as total_duration_ms,
    -- 时间信息
    t.created_at,
    t.started_at,
    t.completed_at
FROM tech_proposal_tasks t;
