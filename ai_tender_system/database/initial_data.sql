-- AI标书系统知识库初始数据脚本
-- 创建时间: 2025-09-28
-- 描述: 仅在首次数据库初始化时执行的初始数据插入
-- 注意: 此脚本只有在数据库中没有对应数据时才应该执行

-- 检查并插入默认公司数据
INSERT OR IGNORE INTO companies (company_name, company_code, industry_type, description) VALUES
('中国联合网络通信有限公司', 'UNICOM', 'telecommunications', '中国领先的综合通信服务提供商');

-- 插入公司信息库配置（仅当公司ID=1存在时）
INSERT OR IGNORE INTO company_profiles (company_id, profile_type, profile_name, description, privacy_level)
SELECT 1, 'basic', '基础信息', '公司基本信息和对外资料', 1
WHERE EXISTS (SELECT 1 FROM companies WHERE company_id = 1)
UNION ALL
SELECT 1, 'qualification', '资质证书', '各类业务资质和认证证书', 2
WHERE EXISTS (SELECT 1 FROM companies WHERE company_id = 1)
UNION ALL
SELECT 1, 'personnel', '人员信息', '员工信息和人力资源资料', 3
WHERE EXISTS (SELECT 1 FROM companies WHERE company_id = 1)
UNION ALL
SELECT 1, 'financial', '财务文档', '财务报告和审计资料', 4
WHERE EXISTS (SELECT 1 FROM companies WHERE company_id = 1);

-- 插入默认产品数据（仅当公司ID=1存在时）
INSERT OR IGNORE INTO products (company_id, product_name, product_code, product_category, description)
SELECT 1, '5G核心网产品', '5G_CORE', 'communication', '5G核心网解决方案'
WHERE EXISTS (SELECT 1 FROM companies WHERE company_id = 1)
UNION ALL
SELECT 1, '云计算平台', 'CLOUD_PLATFORM', 'cloud', '企业级云计算服务平台'
WHERE EXISTS (SELECT 1 FROM companies WHERE company_id = 1)
UNION ALL
SELECT 1, '大数据平台', 'BIG_DATA', 'bigdata', '大数据分析和处理平台'
WHERE EXISTS (SELECT 1 FROM companies WHERE company_id = 1);

-- 插入默认用户角色
INSERT OR IGNORE INTO user_roles (role_name, role_description, privacy_level_access, can_upload, can_delete, can_modify_privacy, can_manage_users) VALUES
('普通用户', '只能访问公开文档', 1, 0, 0, 0, 0),
('内部员工', '可访问公开和内部文档', 2, 1, 0, 0, 0),
('项目经理', '可访问机密级别文档', 3, 1, 1, 1, 0),
('高级管理', '可访问所有级别文档', 4, 1, 1, 1, 1);

-- 插入系统配置
INSERT OR IGNORE INTO knowledge_base_configs (config_key, config_value, config_type, description) VALUES
('max_file_size', '100', 'integer', '文档上传最大大小(MB)'),
('supported_file_types', '["pdf", "doc", "docx", "txt", "xls", "xlsx", "ppt", "pptx"]', 'json', '支持的文件类型'),
('vector_model_name', 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2', 'string', '向量化模型名称'),
('chunk_size', '1000', 'integer', '文档分块大小'),
('chunk_overlap', '200', 'integer', '分块重叠大小'),
('privacy_retention_days', '2555', 'integer', '隐私文档保留天数(7年)'),
('audit_log_retention_days', '2555', 'integer', '审计日志保留天数(7年)'),
('auto_encrypt_level', '3', 'integer', '自动加密的隐私级别阈值'),
('session_timeout', '7200', 'integer', '会话超时时间(秒)'),
('max_concurrent_uploads', '5', 'integer', '最大并发上传数'),
('enable_document_watermark', 'true', 'boolean', '是否启用文档水印'),
('db_initialized', 'true', 'boolean', '数据库是否已完成初始化');

-- 记录初始化完成标记
INSERT OR REPLACE INTO knowledge_base_configs (config_key, config_value, config_type, description) VALUES
('initial_data_loaded', 'true', 'boolean', '初始数据是否已加载完成');