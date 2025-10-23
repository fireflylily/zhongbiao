-- 添加工作经历字段到resumes表
-- 日期: 2025-10-23

-- 添加work_experience字段（如果不存在）
-- SQLite不支持IF NOT EXISTS语法，所以我们用一个更安全的方式
-- 如果字段已存在，这个语句会失败但不会损坏数据库

ALTER TABLE resumes ADD COLUMN work_experience TEXT;

-- 注意：如果字段已存在，上面的语句会报错，这是正常的
-- 可以忽略错误或者手动检查字段是否存在
