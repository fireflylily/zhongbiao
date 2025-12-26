-- 标书素材库数据库表结构
-- 创建时间: 2024
-- 描述: 用于存储历史中标标书的优秀片段，供AI生成技术方案时参考

-- ============================================================================
-- 1. 标书文档表（整份标书）
-- ============================================================================
-- 用途：存储上传的历史标书文档信息
CREATE TABLE IF NOT EXISTS tender_documents (
    tender_doc_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,

    -- 基本信息
    doc_name VARCHAR(255) NOT NULL,           -- 标书名称
    project_name VARCHAR(255),                -- 投标项目名称
    customer_name VARCHAR(255),               -- 招标方名称
    industry VARCHAR(100),                    -- 所属行业
    project_type VARCHAR(100),                -- 项目类型

    -- 投标信息
    bid_date DATE,                            -- 投标日期
    bid_amount DECIMAL(15,2),                 -- 投标金额

    -- 结果信息（关键！用于筛选优质素材）
    bid_result VARCHAR(50) DEFAULT 'unknown', -- 投标结果: won(中标)/lost(未中标)/unknown
    final_score DECIMAL(5,2),                 -- 最终得分
    technical_score DECIMAL(5,2),             -- 技术分
    commercial_score DECIMAL(5,2),            -- 商务分
    score_rank INTEGER,                       -- 得分排名

    -- 文件信息
    file_path VARCHAR(500),                   -- 文件存储路径
    file_name VARCHAR(255),                   -- 原始文件名
    file_type VARCHAR(20),                    -- 文件类型: docx/pdf/doc
    file_size INTEGER,                        -- 文件大小(字节)

    -- 处理状态
    parse_status VARCHAR(20) DEFAULT 'pending',   -- 解析状态: pending/parsing/completed/failed
    chunk_status VARCHAR(20) DEFAULT 'pending',   -- 片段提取状态
    parse_error TEXT,                             -- 解析错误信息

    -- 文档统计
    total_pages INTEGER,                      -- 总页数
    total_chapters INTEGER,                   -- 总章节数
    total_words INTEGER,                      -- 总字数

    -- 标签和元数据
    tags TEXT,                                -- JSON数组：标签
    metadata TEXT,                            -- JSON：其他元数据
    -- 示例 metadata: {"original_outline": [...], "key_chapters": [...]}

    -- 关联产品（可选）
    related_products TEXT,                    -- JSON数组：相关产品ID列表

    -- 备注
    notes TEXT,                               -- 备注说明

    -- 上传信息
    uploaded_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);

-- ============================================================================
-- 2. 标书章节/片段表（核心素材）
-- ============================================================================
-- 用途：存储从标书中提取的章节片段，这是生成技术方案的核心素材
CREATE TABLE IF NOT EXISTS tender_excerpts (
    excerpt_id INTEGER PRIMARY KEY AUTOINCREMENT,
    tender_doc_id INTEGER NOT NULL,
    company_id INTEGER NOT NULL,

    -- 章节信息
    chapter_number VARCHAR(50),               -- 章节号，如"3.1.2"
    chapter_title VARCHAR(255),               -- 章节标题
    chapter_level INTEGER DEFAULT 1,          -- 章节级别 1-4
    parent_excerpt_id INTEGER,                -- 父章节ID（用于构建目录树）

    -- 内容
    content TEXT NOT NULL,                    -- 章节内容（纯文本）
    content_html TEXT,                        -- 章节内容（带格式，可选）
    word_count INTEGER,                       -- 字数

    -- 质量评估（关键！用于优先检索高质量素材）
    quality_score INTEGER DEFAULT 0,          -- 质量评分 0-100
    is_highlighted BOOLEAN DEFAULT FALSE,     -- 是否为精选片段
    quality_notes TEXT,                       -- 质量评估说明

    -- 分类标签（用于检索匹配）
    category VARCHAR(100),                    -- 内容分类：技术架构/实施方案/安全保障/运维服务/项目管理/...
    subcategory VARCHAR(100),                 -- 子分类
    keywords TEXT,                            -- JSON数组：关键词

    -- 评分点关联（核心！用于按评分点检索素材）
    scoring_points TEXT,                      -- JSON数组：可响应的评分点类型
    -- 示例: ["系统架构设计", "高可用方案", "数据安全", "运维保障"]

    -- 能力标签关联
    capability_tag_ids TEXT,                  -- JSON数组：关联的能力标签ID

    -- 向量检索
    vector_embedding BLOB,                    -- 向量嵌入
    embedding_model VARCHAR(50),              -- 嵌入模型
    vector_status VARCHAR(20) DEFAULT 'pending', -- 向量化状态

    -- 来源追溯
    source_page_start INTEGER,                -- 原文档起始页码
    source_page_end INTEGER,                  -- 原文档结束页码
    source_position TEXT,                     -- JSON：在原文档中的详细位置

    -- 使用统计
    usage_count INTEGER DEFAULT 0,            -- 被引用次数
    last_used_at TIMESTAMP,                   -- 最后使用时间

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (tender_doc_id) REFERENCES tender_documents(tender_doc_id) ON DELETE CASCADE,
    FOREIGN KEY (company_id) REFERENCES companies(company_id),
    FOREIGN KEY (parent_excerpt_id) REFERENCES tender_excerpts(excerpt_id) ON DELETE SET NULL
);

-- ============================================================================
-- 3. 评分点响应模板表
-- ============================================================================
-- 用途：存储常见评分点的响应模板和结构建议
CREATE TABLE IF NOT EXISTS scoring_response_templates (
    template_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER,                       -- NULL表示通用模板

    -- 评分点信息
    scoring_point_type VARCHAR(100) NOT NULL, -- 评分点类型，如"技术架构"
    scoring_point_name VARCHAR(255),          -- 评分点名称
    scoring_point_description TEXT,           -- 评分点描述/评分标准

    -- 响应模板
    response_template TEXT NOT NULL,          -- 响应模板内容
    response_structure TEXT,                  -- JSON：推荐的响应结构
    -- 示例: {"sections": ["概述", "设计原则", "架构图", "技术选型", "优势说明"]}

    -- 关键要素
    required_elements TEXT,                   -- JSON数组：必须包含的要素
    -- 示例: ["架构图", "技术参数", "成功案例"]
    recommended_data TEXT,                    -- JSON数组：推荐引用的数据类型
    -- 示例: ["性能指标", "客户数量", "处理量"]

    -- 关联素材
    example_excerpt_ids TEXT,                 -- JSON数组：示例素材ID

    -- 质量信息
    usage_count INTEGER DEFAULT 0,            -- 使用次数
    avg_score DECIMAL(5,2),                   -- 平均得分（历史使用后的反馈）
    success_rate DECIMAL(5,2),                -- 中标率

    -- 状态
    is_active BOOLEAN DEFAULT TRUE,
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);

-- ============================================================================
-- 4. 素材使用记录表
-- ============================================================================
-- 用途：记录素材的使用情况，用于优化推荐和统计
CREATE TABLE IF NOT EXISTS excerpt_usage_logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    excerpt_id INTEGER NOT NULL,
    company_id INTEGER NOT NULL,

    -- 使用上下文
    tender_project_id INTEGER,                -- 使用的招标项目
    chapter_title VARCHAR(255),               -- 用于的章节
    usage_type VARCHAR(50),                   -- 使用方式: reference/quote/adapt

    -- 使用效果
    was_modified BOOLEAN DEFAULT FALSE,       -- 是否被修改
    user_rating INTEGER,                      -- 用户评分 1-5

    -- 操作信息
    used_by VARCHAR(100),
    used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (excerpt_id) REFERENCES tender_excerpts(excerpt_id) ON DELETE CASCADE,
    FOREIGN KEY (company_id) REFERENCES companies(company_id),
    FOREIGN KEY (tender_project_id) REFERENCES tender_projects(project_id) ON DELETE SET NULL
);

-- ============================================================================
-- 5. 内容分类字典表
-- ============================================================================
-- 用途：定义素材的分类体系
CREATE TABLE IF NOT EXISTS excerpt_categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER,                       -- NULL表示通用分类

    category_code VARCHAR(50) NOT NULL,       -- 分类代码
    category_name VARCHAR(100) NOT NULL,      -- 分类名称
    parent_category_id INTEGER,               -- 父分类

    description TEXT,                         -- 分类描述
    example_keywords TEXT,                    -- JSON数组：示例关键词

    category_order INTEGER DEFAULT 999,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (company_id) REFERENCES companies(company_id),
    FOREIGN KEY (parent_category_id) REFERENCES excerpt_categories(category_id)
);

-- ============================================================================
-- 索引
-- ============================================================================

-- 标书文档表索引
CREATE INDEX IF NOT EXISTS idx_tender_docs_company ON tender_documents(company_id);
CREATE INDEX IF NOT EXISTS idx_tender_docs_result ON tender_documents(bid_result);
CREATE INDEX IF NOT EXISTS idx_tender_docs_industry ON tender_documents(industry);
CREATE INDEX IF NOT EXISTS idx_tender_docs_date ON tender_documents(bid_date);
CREATE INDEX IF NOT EXISTS idx_tender_docs_status ON tender_documents(parse_status);
CREATE INDEX IF NOT EXISTS idx_tender_docs_score ON tender_documents(technical_score DESC);

-- 标书片段表索引
CREATE INDEX IF NOT EXISTS idx_excerpts_tender ON tender_excerpts(tender_doc_id);
CREATE INDEX IF NOT EXISTS idx_excerpts_company ON tender_excerpts(company_id);
CREATE INDEX IF NOT EXISTS idx_excerpts_category ON tender_excerpts(category);
CREATE INDEX IF NOT EXISTS idx_excerpts_subcategory ON tender_excerpts(subcategory);
CREATE INDEX IF NOT EXISTS idx_excerpts_quality ON tender_excerpts(quality_score DESC);
CREATE INDEX IF NOT EXISTS idx_excerpts_highlighted ON tender_excerpts(is_highlighted);
CREATE INDEX IF NOT EXISTS idx_excerpts_parent ON tender_excerpts(parent_excerpt_id);
CREATE INDEX IF NOT EXISTS idx_excerpts_vector_status ON tender_excerpts(vector_status);
CREATE INDEX IF NOT EXISTS idx_excerpts_usage ON tender_excerpts(usage_count DESC);

-- 评分点模板表索引
CREATE INDEX IF NOT EXISTS idx_templates_type ON scoring_response_templates(scoring_point_type);
CREATE INDEX IF NOT EXISTS idx_templates_company ON scoring_response_templates(company_id);
CREATE INDEX IF NOT EXISTS idx_templates_active ON scoring_response_templates(is_active);
CREATE INDEX IF NOT EXISTS idx_templates_usage ON scoring_response_templates(usage_count DESC);

-- 使用记录表索引
CREATE INDEX IF NOT EXISTS idx_usage_logs_excerpt ON excerpt_usage_logs(excerpt_id);
CREATE INDEX IF NOT EXISTS idx_usage_logs_company ON excerpt_usage_logs(company_id);
CREATE INDEX IF NOT EXISTS idx_usage_logs_project ON excerpt_usage_logs(tender_project_id);

-- 分类字典表索引
CREATE INDEX IF NOT EXISTS idx_categories_company ON excerpt_categories(company_id);
CREATE INDEX IF NOT EXISTS idx_categories_parent ON excerpt_categories(parent_category_id);
CREATE INDEX IF NOT EXISTS idx_categories_code ON excerpt_categories(category_code);

-- ============================================================================
-- 初始化常用分类数据
-- ============================================================================
INSERT OR IGNORE INTO excerpt_categories (category_code, category_name, description, category_order) VALUES
('project_understanding', '项目理解', '对招标项目背景、目标、需求的理解和分析', 1),
('technical_architecture', '技术架构', '系统整体架构设计、技术选型、架构图', 2),
('detailed_design', '详细设计', '功能模块设计、接口设计、数据库设计', 3),
('implementation_plan', '实施方案', '项目实施计划、部署方案、里程碑', 4),
('security_solution', '安全方案', '信息安全、数据安全、网络安全方案', 5),
('operation_maintenance', '运维保障', '运维服务、监控告警、应急响应', 6),
('project_management', '项目管理', '项目组织、进度管理、质量管理、风险管理', 7),
('training_transfer', '培训交付', '培训方案、知识转移、文档交付', 8),
('team_qualification', '团队资质', '项目团队介绍、人员资质、组织架构', 9),
('case_experience', '项目经验', '类似项目案例、成功经验、客户评价', 10),
('company_strength', '公司实力', '公司介绍、资质证书、荣誉奖项', 11),
('after_sales_service', '售后服务', '质保承诺、服务响应、服务网点', 12);
