-- 产品能力索引数据库表结构
-- 创建时间: 2024
-- 描述: 用于存储产品能力标签和AI自动提取的能力索引，支持招标需求匹配

-- ============================================================================
-- 1. 核心能力标签表（人工定义，每企业独立）
-- ============================================================================
-- 用途：定义产品线/能力大类，如"风控产品"、"实修"、"免密"等
-- 特点：支持层级结构，每个企业独立维护自己的标签体系
CREATE TABLE IF NOT EXISTS product_capability_tags (
    tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,           -- 每企业独立的标签体系

    -- 标签基本信息
    tag_name VARCHAR(100) NOT NULL,        -- 标签名称，如"风控产品"、"实修"
    tag_code VARCHAR(50) NOT NULL,         -- 标签代码，如"risk_control"、"repair"
    parent_tag_id INTEGER,                 -- 父标签ID，支持层级结构

    -- 标签描述
    description TEXT,                      -- 标签描述
    example_keywords TEXT,                 -- 示例关键词(JSON数组)，用于指导AI提取
    -- 示例: ["风控", "反欺诈", "信用评估", "风险监控"]

    -- 显示和状态
    tag_order INTEGER DEFAULT 999,         -- 显示顺序
    tag_level INTEGER DEFAULT 1,           -- 层级深度 1=一级 2=二级...
    is_active BOOLEAN DEFAULT TRUE,        -- 是否启用

    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (company_id) REFERENCES companies(company_id),
    FOREIGN KEY (parent_tag_id) REFERENCES product_capability_tags(tag_id),
    UNIQUE(company_id, tag_code)
);

-- ============================================================================
-- 2. 产品能力索引表（AI自动提取）
-- ============================================================================
-- 用途：存储从产品文档中AI自动提取的具体能力描述
-- 特点：每个能力关联到原文档，支持向量检索，可人工审核
CREATE TABLE IF NOT EXISTS product_capabilities_index (
    capability_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,

    -- 来源追溯（关键！确保每个能力都有据可查）
    doc_id INTEGER NOT NULL,               -- 来源文档ID
    chunk_id INTEGER,                      -- 来源chunk ID（精确定位）

    -- 能力描述（AI提取）
    capability_name VARCHAR(200) NOT NULL, -- 能力名称，如"实时风控决策"
    capability_type VARCHAR(50),           -- 能力类型: function/interface/service/support
    capability_description TEXT,           -- 能力详细描述
    original_text TEXT,                    -- 原文摘录（作为证据）

    -- 量化指标（如果有）
    metrics TEXT,                          -- JSON: {"response_time": "<50ms", "qps": "10000"}

    -- 关联标签
    tag_id INTEGER,                        -- 关联的核心能力标签

    -- AI提取元数据
    extraction_model VARCHAR(50),          -- 使用的模型，如"gpt-4o-mini"
    confidence_score FLOAT DEFAULT 0.0,    -- 提取置信度 0-1
    extracted_at TIMESTAMP,                -- 提取时间

    -- 向量索引（用于语义搜索）
    capability_embedding BLOB,             -- 能力描述的向量嵌入
    embedding_model VARCHAR(50),           -- 嵌入模型

    -- 人工审核
    verified BOOLEAN DEFAULT FALSE,        -- 是否已人工验证
    verified_by VARCHAR(100),              -- 审核人
    verified_at TIMESTAMP,                 -- 审核时间
    verification_note TEXT,                -- 审核备注

    -- 状态
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (company_id) REFERENCES companies(company_id),
    FOREIGN KEY (doc_id) REFERENCES documents(doc_id) ON DELETE CASCADE,
    FOREIGN KEY (chunk_id) REFERENCES document_chunks(chunk_id) ON DELETE SET NULL,
    FOREIGN KEY (tag_id) REFERENCES product_capability_tags(tag_id) ON DELETE SET NULL
);

-- ============================================================================
-- 3. 能力关键词表（辅助搜索）
-- ============================================================================
-- 用途：存储能力的同义词、相关词，提升搜索召回率
CREATE TABLE IF NOT EXISTS capability_keywords (
    keyword_id INTEGER PRIMARY KEY AUTOINCREMENT,
    capability_id INTEGER NOT NULL,

    -- 关键词信息
    keyword VARCHAR(100) NOT NULL,         -- 关键词
    keyword_type VARCHAR(50),              -- 类型: synonym/related/technical/industry
    weight FLOAT DEFAULT 1.0,              -- 权重
    source VARCHAR(20) DEFAULT 'manual',   -- 来源: ai_extracted/manual

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (capability_id) REFERENCES product_capabilities_index(capability_id) ON DELETE CASCADE
);

-- ============================================================================
-- 4. 能力匹配历史表（用于学习优化）
-- ============================================================================
-- 用途：记录招标需求与能力的匹配历史，收集用户反馈，用于持续优化
CREATE TABLE IF NOT EXISTS capability_match_history (
    match_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,

    -- 匹配上下文
    tender_project_id INTEGER,             -- 招标项目ID（可选）
    session_id VARCHAR(100),               -- 会话ID（用于追踪同一次匹配）

    -- 需求信息
    requirement_text TEXT NOT NULL,        -- 招标需求原文
    requirement_type VARCHAR(50),          -- 需求类型: functional/technical/performance

    -- 匹配结果
    matched_capability_id INTEGER,         -- 匹配到的能力ID
    match_score FLOAT,                     -- 匹配分数 0-1
    match_method VARCHAR(50),              -- 匹配方法: semantic/keyword/hybrid
    match_rank INTEGER,                    -- 在结果中的排名

    -- 用户反馈（关键！用于优化）
    user_feedback VARCHAR(20),             -- 反馈: correct/incorrect/partial
    feedback_note TEXT,                    -- 反馈说明
    feedback_by VARCHAR(100),              -- 反馈人
    feedback_at TIMESTAMP,                 -- 反馈时间

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (company_id) REFERENCES companies(company_id),
    FOREIGN KEY (tender_project_id) REFERENCES tender_projects(project_id) ON DELETE SET NULL,
    FOREIGN KEY (matched_capability_id) REFERENCES product_capabilities_index(capability_id) ON DELETE SET NULL
);

-- ============================================================================
-- 5. 能力不支持清单表（明确边界）
-- ============================================================================
-- 用途：明确记录产品不支持的能力，避免AI编造
CREATE TABLE IF NOT EXISTS capability_limitations (
    limitation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    tag_id INTEGER,                        -- 关联的能力标签（可选）

    -- 不支持的能力描述
    limitation_name VARCHAR(200) NOT NULL, -- 不支持的能力名称
    limitation_description TEXT,           -- 详细说明

    -- 替代方案（如果有）
    alternative_solution TEXT,             -- 替代方案说明

    -- 状态
    is_active BOOLEAN DEFAULT TRUE,
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (company_id) REFERENCES companies(company_id),
    FOREIGN KEY (tag_id) REFERENCES product_capability_tags(tag_id) ON DELETE SET NULL
);

-- ============================================================================
-- 索引
-- ============================================================================

-- 标签表索引
CREATE INDEX IF NOT EXISTS idx_capability_tags_company ON product_capability_tags(company_id);
CREATE INDEX IF NOT EXISTS idx_capability_tags_parent ON product_capability_tags(parent_tag_id);
CREATE INDEX IF NOT EXISTS idx_capability_tags_code ON product_capability_tags(tag_code);
CREATE INDEX IF NOT EXISTS idx_capability_tags_active ON product_capability_tags(is_active);

-- 能力索引表索引
CREATE INDEX IF NOT EXISTS idx_capabilities_company ON product_capabilities_index(company_id);
CREATE INDEX IF NOT EXISTS idx_capabilities_doc ON product_capabilities_index(doc_id);
CREATE INDEX IF NOT EXISTS idx_capabilities_chunk ON product_capabilities_index(chunk_id);
CREATE INDEX IF NOT EXISTS idx_capabilities_tag ON product_capabilities_index(tag_id);
CREATE INDEX IF NOT EXISTS idx_capabilities_verified ON product_capabilities_index(verified);
CREATE INDEX IF NOT EXISTS idx_capabilities_active ON product_capabilities_index(is_active);
CREATE INDEX IF NOT EXISTS idx_capabilities_confidence ON product_capabilities_index(confidence_score DESC);

-- 关键词表索引
CREATE INDEX IF NOT EXISTS idx_capability_keywords_cap ON capability_keywords(capability_id);
CREATE INDEX IF NOT EXISTS idx_capability_keywords_word ON capability_keywords(keyword);

-- 匹配历史表索引
CREATE INDEX IF NOT EXISTS idx_match_history_company ON capability_match_history(company_id);
CREATE INDEX IF NOT EXISTS idx_match_history_capability ON capability_match_history(matched_capability_id);
CREATE INDEX IF NOT EXISTS idx_match_history_project ON capability_match_history(tender_project_id);
CREATE INDEX IF NOT EXISTS idx_match_history_feedback ON capability_match_history(user_feedback);
CREATE INDEX IF NOT EXISTS idx_match_history_session ON capability_match_history(session_id);

-- 不支持清单索引
CREATE INDEX IF NOT EXISTS idx_limitations_company ON capability_limitations(company_id);
CREATE INDEX IF NOT EXISTS idx_limitations_tag ON capability_limitations(tag_id);
