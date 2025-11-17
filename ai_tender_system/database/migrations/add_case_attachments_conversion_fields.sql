-- 添加PDF/Word转换相关字段到 case_attachments 表
-- 执行日期: 2025-11-17
-- 功能: 支持案例附件（PDF和Word）自动转换为图片

-- 添加原始文件类型字段
ALTER TABLE case_attachments
ADD COLUMN original_file_type VARCHAR(10) DEFAULT NULL;

-- 添加转换后的图片信息（JSON格式）
ALTER TABLE case_attachments
ADD COLUMN converted_images TEXT DEFAULT NULL;

-- 添加转换配置和元信息（JSON格式）
ALTER TABLE case_attachments
ADD COLUMN conversion_info TEXT DEFAULT NULL;

-- 添加转换时间戳
ALTER TABLE case_attachments
ADD COLUMN conversion_date TIMESTAMP DEFAULT NULL;

-- 创建索引以加快查询
CREATE INDEX IF NOT EXISTS idx_case_att_original_type ON case_attachments(original_file_type);

-- 添加注释说明
-- original_file_type: 原始文件类型（PDF, DOCX, DOC, JPG等）
-- converted_images: JSON数组，存储转换后的图片路径和信息
--   示例: [{"page_num": 1, "file_path": "/path/to/page_001.png", "width": 1600, "height": 2000}, ...]
--   PDF: 多页PDF转换为多张图片
--   Word: 提取Word文档中的所有图片
-- conversion_info: JSON对象，存储转换配置和元数据
--   示例: {"total_pages": 3, "total_images": 5, "output_dir": "/path/to/output", "dpi": 200, "format": "PNG"}
-- conversion_date: 文档转换的时间戳
