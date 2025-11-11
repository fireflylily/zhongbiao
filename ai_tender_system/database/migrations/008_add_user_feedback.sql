-- 用户反馈表
-- 用于记录用户在使用系统过程中提交的问题和意见

CREATE TABLE IF NOT EXISTS user_feedbacks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    -- 反馈内容
    content TEXT NOT NULL,

    -- 用户信息
    username TEXT,
    user_id INTEGER,

    -- 上下文信息
    project_id INTEGER,
    project_name TEXT,
    company_id INTEGER,
    company_name TEXT,

    -- 页面路径（用于记录用户在哪个页面提交的反馈）
    page_route TEXT,
    page_title TEXT,

    -- 反馈类型（bug、建议、其他）
    feedback_type TEXT DEFAULT 'general',

    -- 状态（pending、processing、resolved、closed）
    status TEXT DEFAULT 'pending',

    -- 优先级（low、medium、high）
    priority TEXT DEFAULT 'medium',

    -- 处理信息
    assigned_to TEXT,
    resolution TEXT,
    resolved_at TIMESTAMP,

    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- 外键约束
    FOREIGN KEY (project_id) REFERENCES tender_projects(id) ON DELETE SET NULL
);

-- 创建索引以提高查询性能
CREATE INDEX IF NOT EXISTS idx_user_feedbacks_username ON user_feedbacks(username);
CREATE INDEX IF NOT EXISTS idx_user_feedbacks_project_id ON user_feedbacks(project_id);
CREATE INDEX IF NOT EXISTS idx_user_feedbacks_status ON user_feedbacks(status);
CREATE INDEX IF NOT EXISTS idx_user_feedbacks_created_at ON user_feedbacks(created_at);
CREATE INDEX IF NOT EXISTS idx_user_feedbacks_feedback_type ON user_feedbacks(feedback_type);

-- 创建更新时间触发器
CREATE TRIGGER IF NOT EXISTS update_user_feedbacks_timestamp
AFTER UPDATE ON user_feedbacks
FOR EACH ROW
BEGIN
    UPDATE user_feedbacks SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;
