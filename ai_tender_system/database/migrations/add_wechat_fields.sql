-- 微信小程序用户字段迁移
-- 执行时间: 2025-01
-- 描述: 为 users 表添加微信小程序相关字段

-- 添加 openid 字段（微信用户唯一标识）
ALTER TABLE users ADD COLUMN openid TEXT UNIQUE;

-- 添加 unionid 字段（微信开放平台统一标识）
ALTER TABLE users ADD COLUMN unionid TEXT;

-- 添加微信会话密钥
ALTER TABLE users ADD COLUMN wechat_session_key TEXT;

-- 添加微信昵称
ALTER TABLE users ADD COLUMN nickname TEXT;

-- 添加微信头像
ALTER TABLE users ADD COLUMN avatar_url TEXT;

-- 创建 openid 索引
CREATE INDEX IF NOT EXISTS idx_users_openid ON users(openid);
