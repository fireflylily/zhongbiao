-- 标书宝 5.0 数据库升级脚本
-- 为 risk_analysis_tasks 表添加新字段

-- 添加 5.0 新增字段
ALTER TABLE risk_analysis_tasks ADD COLUMN IF NOT EXISTS response_file_path TEXT DEFAULT '';
ALTER TABLE risk_analysis_tasks ADD COLUMN IF NOT EXISTS response_file_name TEXT DEFAULT '';
ALTER TABLE risk_analysis_tasks ADD COLUMN IF NOT EXISTS has_toc INTEGER DEFAULT 0;
ALTER TABLE risk_analysis_tasks ADD COLUMN IF NOT EXISTS analysis_mode TEXT DEFAULT 'bid_only';
ALTER TABLE risk_analysis_tasks ADD COLUMN IF NOT EXISTS exclude_chapters TEXT DEFAULT '[]';
ALTER TABLE risk_analysis_tasks ADD COLUMN IF NOT EXISTS reconcile_results TEXT DEFAULT '[]';

-- 如果数据库不支持 IF NOT EXISTS，使用以下替代方式（SQLite）:
-- 检查列是否存在的存储过程在 SQLite 中不可用，所以使用 Python 脚本执行
