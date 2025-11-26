-- 为users表添加password字段
-- 创建时间: 2025-11-25
-- 描述: 添加密码字段以支持用户修改密码功能

-- 1. 添加password字段
ALTER TABLE users ADD COLUMN password VARCHAR(255);

-- 注意：密码应该使用bcrypt等哈希算法加密后存储
-- 默认密码将通过Python脚本迁移：
-- - admin用户: admin123 (已加密)
-- - 其他用户: {username}123 (已加密)
