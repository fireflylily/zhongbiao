-- ============================================================
-- 应答文件自检查模块数据库表结构
-- ============================================================

-- 应答文件自检任务表
CREATE TABLE IF NOT EXISTS response_check_tasks (
    task_id TEXT PRIMARY KEY,
    openid TEXT,
    user_id INTEGER,

    -- 文件信息
    file_id TEXT NOT NULL,
    file_path TEXT,
    original_filename TEXT NOT NULL,
    file_size INTEGER DEFAULT 0,
    total_pages INTEGER DEFAULT 0,

    -- 任务状态
    status TEXT DEFAULT 'pending',      -- pending/parsing/checking/completed/failed
    progress INTEGER DEFAULT 0,
    current_step TEXT DEFAULT '',
    current_category TEXT DEFAULT '',
    error_message TEXT DEFAULT '',

    -- 提取的信息（JSON格式）
    extracted_info TEXT DEFAULT '{}',

    -- 检查结果（JSON格式）
    check_categories TEXT DEFAULT '[]',

    -- 汇总统计
    total_items INTEGER DEFAULT 0,
    pass_count INTEGER DEFAULT 0,
    fail_count INTEGER DEFAULT 0,
    unknown_count INTEGER DEFAULT 0,

    -- AI模型信息
    model_name TEXT DEFAULT 'deepseek-v3',
    analysis_time REAL DEFAULT 0,

    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_response_check_openid ON response_check_tasks(openid);
CREATE INDEX IF NOT EXISTS idx_response_check_user_id ON response_check_tasks(user_id);
CREATE INDEX IF NOT EXISTS idx_response_check_status ON response_check_tasks(status);
CREATE INDEX IF NOT EXISTS idx_response_check_created ON response_check_tasks(created_at DESC);
