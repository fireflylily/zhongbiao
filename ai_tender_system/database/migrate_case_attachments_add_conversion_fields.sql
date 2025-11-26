-- 为 case_attachments 表添加PDF/Word转图片支持字段
-- 创建时间: 2025-11-26
-- 说明: 添加converted_images等字段以支持附件图片插入功能

-- 1. 添加 original_file_type 字段（原始文件类型）
ALTER TABLE case_attachments ADD COLUMN original_file_type VARCHAR(20);

-- 2. 添加 converted_images 字段（转换后的图片列表）
ALTER TABLE case_attachments ADD COLUMN converted_images TEXT;

-- 3. 添加 conversion_info 字段（转换信息）
ALTER TABLE case_attachments ADD COLUMN conversion_info TEXT;

-- 4. 添加 conversion_date 字段（转换时间）
ALTER TABLE case_attachments ADD COLUMN conversion_date TIMESTAMP;

-- 验证修改
PRAGMA table_info(case_attachments);

-- 输出成功消息
SELECT '✅ case_attachments 表结构更新完成' as message;
SELECT '新增字段:' as info;
SELECT '  - original_file_type: 原始文件类型' as field1;
SELECT '  - converted_images: 转换后的图片列表（JSON）' as field2;
SELECT '  - conversion_info: 转换信息（JSON）' as field3;
SELECT '  - conversion_date: 转换时间' as field4;
