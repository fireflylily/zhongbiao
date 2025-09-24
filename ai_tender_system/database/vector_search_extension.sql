-- AI标书系统向量搜索扩展表结构
-- 创建时间: 2024-09-24
-- 描述: 扩展现有数据库以支持向量搜索和语义检索功能

-- 1. 向量模型配置表
CREATE TABLE IF NOT EXISTS vector_models (
    model_id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_name VARCHAR(255) NOT NULL UNIQUE,
    model_type VARCHAR(50) NOT NULL, -- sentence-transformer/openai/custom/simple
    model_path VARCHAR(500),
    dimension INTEGER NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT FALSE,
    performance_metrics TEXT, -- JSON: 模型性能指标
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. 向量索引状态表
CREATE TABLE IF NOT EXISTS vector_indexes (
    index_id INTEGER PRIMARY KEY AUTOINCREMENT,
    index_name VARCHAR(255) NOT NULL UNIQUE,
    model_id INTEGER NOT NULL,
    index_type VARCHAR(50) DEFAULT 'flat', -- flat/ivf/hnsw
    dimension INTEGER NOT NULL,
    vector_count INTEGER DEFAULT 0,
    index_status VARCHAR(20) DEFAULT 'building', -- building/ready/updating/error
    index_file_path VARCHAR(500),
    metadata_file_path VARCHAR(500),
    build_time FLOAT DEFAULT 0.0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (model_id) REFERENCES vector_models(model_id)
);

-- 3. 文档向量表 (替代原有的document_chunks表中的vector_embedding字段)
CREATE TABLE IF NOT EXISTS document_vectors (
    vector_id INTEGER PRIMARY KEY AUTOINCREMENT,
    chunk_id INTEGER NOT NULL UNIQUE,
    model_id INTEGER NOT NULL,
    vector_data BLOB NOT NULL, -- 序列化的向量数据
    vector_norm REAL, -- 向量的L2范数，用于优化相似度计算
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chunk_id) REFERENCES document_chunks(chunk_id) ON DELETE CASCADE,
    FOREIGN KEY (model_id) REFERENCES vector_models(model_id)
);

-- 4. 搜索历史表
CREATE TABLE IF NOT EXISTS search_history (
    search_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    query_text TEXT NOT NULL,
    query_vector BLOB, -- 查询向量
    model_id INTEGER,
    search_type VARCHAR(50) DEFAULT 'semantic', -- semantic/keyword/hybrid
    filter_conditions TEXT, -- JSON: 搜索过滤条件
    result_count INTEGER DEFAULT 0,
    top_k INTEGER DEFAULT 10,
    threshold REAL DEFAULT 0.0,
    search_time REAL, -- 搜索耗时(秒)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (model_id) REFERENCES vector_models(model_id)
);

-- 5. 搜索结果表
CREATE TABLE IF NOT EXISTS search_results (
    result_id INTEGER PRIMARY KEY AUTOINCREMENT,
    search_id INTEGER NOT NULL,
    chunk_id INTEGER NOT NULL,
    doc_id INTEGER NOT NULL,
    similarity_score REAL NOT NULL,
    rank_position INTEGER NOT NULL,
    result_snippet TEXT, -- 结果摘要片段
    highlight_info TEXT, -- JSON: 高亮信息
    FOREIGN KEY (search_id) REFERENCES search_history(search_id) ON DELETE CASCADE,
    FOREIGN KEY (chunk_id) REFERENCES document_chunks(chunk_id),
    FOREIGN KEY (doc_id) REFERENCES documents(doc_id)
);

-- 6. 向量化任务队列表
CREATE TABLE IF NOT EXISTS vectorization_tasks (
    task_id INTEGER PRIMARY KEY AUTOINCREMENT,
    doc_id INTEGER NOT NULL,
    task_type VARCHAR(50) DEFAULT 'new', -- new/update/reindex
    model_id INTEGER NOT NULL,
    priority INTEGER DEFAULT 5, -- 1-10，数字越小优先级越高
    status VARCHAR(20) DEFAULT 'pending', -- pending/processing/completed/failed/cancelled
    progress REAL DEFAULT 0.0, -- 任务进度 0-100
    chunks_total INTEGER DEFAULT 0,
    chunks_processed INTEGER DEFAULT 0,
    error_message TEXT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (doc_id) REFERENCES documents(doc_id) ON DELETE CASCADE,
    FOREIGN KEY (model_id) REFERENCES vector_models(model_id)
);

-- 7. 相似文档关联表
CREATE TABLE IF NOT EXISTS similar_documents (
    relation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_doc_id INTEGER NOT NULL,
    target_doc_id INTEGER NOT NULL,
    similarity_score REAL NOT NULL,
    model_id INTEGER NOT NULL,
    computed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_verified BOOLEAN DEFAULT FALSE, -- 是否经过人工验证
    FOREIGN KEY (source_doc_id) REFERENCES documents(doc_id) ON DELETE CASCADE,
    FOREIGN KEY (target_doc_id) REFERENCES documents(doc_id) ON DELETE CASCADE,
    FOREIGN KEY (model_id) REFERENCES vector_models(model_id),
    UNIQUE(source_doc_id, target_doc_id, model_id)
);

-- 8. 文档标签表
CREATE TABLE IF NOT EXISTS document_tags (
    tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
    tag_name VARCHAR(100) NOT NULL UNIQUE,
    tag_category VARCHAR(50), -- category/type/domain/security
    tag_color VARCHAR(7) DEFAULT '#007bff', -- 标签颜色(hex)
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 9. 文档标签关联表
CREATE TABLE IF NOT EXISTS document_tag_relations (
    relation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    doc_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    confidence REAL DEFAULT 1.0, -- 标签置信度 0-1
    is_auto_tagged BOOLEAN DEFAULT FALSE, -- 是否自动标记
    tagged_by INTEGER, -- 标记用户ID
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (doc_id) REFERENCES documents(doc_id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES document_tags(tag_id),
    FOREIGN KEY (tagged_by) REFERENCES users(user_id),
    UNIQUE(doc_id, tag_id)
);

-- 10. 系统性能监控表
CREATE TABLE IF NOT EXISTS system_metrics (
    metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_name VARCHAR(100) NOT NULL,
    metric_value REAL NOT NULL,
    metric_unit VARCHAR(20), -- seconds/mb/count/percentage
    component VARCHAR(50), -- embedding/vectorstore/search/parsing
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 添加新的索引优化性能
CREATE INDEX IF NOT EXISTS idx_vector_models_active ON vector_models(is_active);
CREATE INDEX IF NOT EXISTS idx_vector_indexes_status ON vector_indexes(index_status);
CREATE INDEX IF NOT EXISTS idx_document_vectors_chunk ON document_vectors(chunk_id);
CREATE INDEX IF NOT EXISTS idx_document_vectors_model ON document_vectors(model_id);
CREATE INDEX IF NOT EXISTS idx_search_history_user ON search_history(user_id, created_at);
CREATE INDEX IF NOT EXISTS idx_search_history_query ON search_history(query_text);
CREATE INDEX IF NOT EXISTS idx_search_results_search ON search_results(search_id, rank_position);
CREATE INDEX IF NOT EXISTS idx_vectorization_tasks_status ON vectorization_tasks(status, priority);
CREATE INDEX IF NOT EXISTS idx_vectorization_tasks_doc ON vectorization_tasks(doc_id);
CREATE INDEX IF NOT EXISTS idx_similar_documents_source ON similar_documents(source_doc_id, similarity_score DESC);
CREATE INDEX IF NOT EXISTS idx_document_tags_name ON document_tags(tag_name);
CREATE INDEX IF NOT EXISTS idx_document_tag_relations_doc ON document_tag_relations(doc_id);
CREATE INDEX IF NOT EXISTS idx_document_tag_relations_tag ON document_tag_relations(tag_id);
CREATE INDEX IF NOT EXISTS idx_system_metrics_component ON system_metrics(component, recorded_at);

-- 更新原有表结构
-- 为documents表添加向量化相关字段
ALTER TABLE documents ADD COLUMN vector_model_id INTEGER REFERENCES vector_models(model_id);
ALTER TABLE documents ADD COLUMN chunk_count INTEGER DEFAULT 0;
ALTER TABLE documents ADD COLUMN vector_quality_score REAL; -- 向量化质量评分

-- 为document_chunks表添加增强字段
ALTER TABLE document_chunks ADD COLUMN content_hash VARCHAR(64); -- 内容哈希，用于重复检测
ALTER TABLE document_chunks ADD COLUMN token_count INTEGER; -- token数量
ALTER TABLE document_chunks ADD COLUMN content_summary TEXT; -- 内容摘要
ALTER TABLE document_chunks ADD COLUMN extracted_entities TEXT; -- JSON: 提取的实体信息

-- 插入默认向量模型配置
INSERT OR IGNORE INTO vector_models (model_name, model_type, dimension, description, is_active) VALUES
('simple-embedding-100', 'simple', 100, '简化版嵌入模型，用于开发测试', TRUE),
('sentence-transformer-384', 'sentence-transformer', 384, 'SentenceTransformer多语言模型', FALSE),
('openai-ada-002', 'openai', 1536, 'OpenAI text-embedding-ada-002模型', FALSE);

-- 插入默认向量索引
INSERT OR IGNORE INTO vector_indexes (index_name, model_id, index_type, dimension, index_status) VALUES
('default_simple_index', 1, 'flat', 100, 'ready');

-- 插入常用文档标签
INSERT OR IGNORE INTO document_tags (tag_name, tag_category, tag_color, description) VALUES
('技术方案', 'category', '#007bff', '技术解决方案相关文档'),
('产品介绍', 'category', '#28a745', '产品介绍和规格说明'),
('商务文件', 'category', '#ffc107', '商务和合同相关文档'),
('资质证书', 'category', '#17a2b8', '企业资质和认证文档'),
('安全相关', 'type', '#dc3545', '涉及安全和保密的文档'),
('财务文档', 'type', '#6f42c1', '财务报告和预算文档'),
('人员信息', 'type', '#fd7e14', '人力资源相关文档'),
('重要', 'domain', '#dc3545', '重要级别文档'),
('常用', 'domain', '#28a745', '经常使用的文档'),
('归档', 'domain', '#6c757d', '已归档的历史文档');

-- 插入系统配置更新
INSERT OR IGNORE INTO knowledge_base_configs (config_key, config_value, config_type, description) VALUES
('vector_search_enabled', 'true', 'boolean', '是否启用向量搜索功能'),
('default_vector_model_id', '1', 'integer', '默认使用的向量模型ID'),
('search_result_cache_ttl', '3600', 'integer', '搜索结果缓存生存时间(秒)'),
('max_search_results', '100', 'integer', '最大搜索结果数量'),
('similarity_threshold', '0.3', 'float', '相似度阈值'),
('auto_reindex_interval', '86400', 'integer', '自动重建索引间隔(秒)'),
('enable_search_analytics', 'true', 'boolean', '是否启用搜索分析'),
('max_concurrent_vectorization', '3', 'integer', '最大并发向量化任务数'),
('vector_cache_size', '1000', 'integer', '向量缓存大小');

-- 创建视图便于查询
CREATE VIEW IF NOT EXISTS document_search_view AS
SELECT
    d.doc_id,
    d.filename,
    d.original_filename,
    d.file_type,
    d.document_category,
    d.privacy_classification,
    d.parse_status,
    d.vector_status,
    d.chunk_count,
    d.vector_quality_score,
    vm.model_name as vector_model,
    vm.dimension as vector_dimension,
    c.company_name,
    p.product_name,
    GROUP_CONCAT(dt.tag_name, ',') as tags
FROM documents d
LEFT JOIN companies c ON d.library_id IN (
    SELECT library_id FROM document_libraries dl
    JOIN products pr ON dl.owner_id = pr.product_id AND dl.owner_type = 'product'
    WHERE pr.company_id = c.company_id
)
LEFT JOIN products p ON d.library_id IN (
    SELECT library_id FROM document_libraries dl
    WHERE dl.owner_id = p.product_id AND dl.owner_type = 'product'
)
LEFT JOIN vector_models vm ON d.vector_model_id = vm.model_id
LEFT JOIN document_tag_relations dtr ON d.doc_id = dtr.doc_id
LEFT JOIN document_tags dt ON dtr.tag_id = dt.tag_id
WHERE d.parse_status = 'completed' AND d.vector_status = 'completed'
GROUP BY d.doc_id;