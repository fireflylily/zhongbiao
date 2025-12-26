# 质量优先的技术方案生成系统 - 完整实施方案

> 目标：生成100页高质量技术方案，从"AI创作"转向"AI整合"

## 一、方案概述

### 核心改进
1. **素材驱动** - AI基于已有素材整合，而非凭空创作
2. **产品边界** - 明确"能做什么/不能做什么"，避免编造
3. **迭代优化** - 专家评审 + 修订循环，直到达标
4. **多企业支持** - 设计时考虑未来服务其他企业

---

## 二、知识库架构

### 整体架构

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           知识库架构                                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐         │
│  │   标书素材库     │  │  产品能力索引    │  │   产品文档库     │         │
│  │  (新建)         │  │  (新建)         │  │  (已有,增强)    │         │
│  ├─────────────────┤  ├─────────────────┤  ├─────────────────┤         │
│  │ • 历史中标标书   │  │ • 能力标签(人工) │  │ • 技术文档      │         │
│  │ • 优秀章节片段   │  │ • 能力索引(AI)  │  │ • 产品手册      │         │
│  │ • 评分点响应模板 │  │ • 功能边界      │  │ • 功能说明      │         │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘         │
│           │                    │                    │                   │
│           └────────────────────┼────────────────────┘                   │
│                                │                                        │
│                    ┌───────────▼───────────┐                           │
│                    │    向量检索引擎        │                           │
│                    │  (ChromaDB/已有)      │                           │
│                    └───────────────────────┘                           │
└─────────────────────────────────────────────────────────────────────────┘
```

### 知识库优先级

| 优先级 | 知识库 | 说明 | 工作量 |
|--------|--------|------|--------|
| 🔴 P0 | **标书素材库** | 历史中标标书的优秀章节 | 2周 |
| 🔴 P0 | **产品能力索引** | 产品能做什么/不能做什么 | 1.5周 |
| 🟡 P1 | **产品文档库增强** | 已有基础，增加能力标注 | 3天 |
| ⬜ 跳过 | ~~案例库增强~~ | 保留现有合同信息即可 | - |

---

## 三、产品能力体系设计（核心新增模块）

### 设计原则
- **文档驱动** - AI自动从产品文档提取能力，低维护成本
- **多企业支持** - 每个企业独立的能力标签体系
- **可追溯** - 每个能力都关联到原文档

### 数据模型

```sql
-- 1. 核心能力标签表（人工定义，每企业独立）
CREATE TABLE product_capability_tags (
    tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,           -- 每企业独立
    tag_name VARCHAR(100) NOT NULL,        -- 如"风控产品"、"实修"
    tag_code VARCHAR(50) NOT NULL,
    parent_tag_id INTEGER,                 -- 支持层级
    description TEXT,
    example_keywords TEXT,                 -- 示例关键词(JSON)
    tag_order INTEGER DEFAULT 999,         -- 显示顺序
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(company_id),
    FOREIGN KEY (parent_tag_id) REFERENCES product_capability_tags(tag_id),
    UNIQUE(company_id, tag_code)
);

-- 2. 产品能力索引表（AI自动提取）
CREATE TABLE product_capabilities_index (
    capability_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,

    -- 来源追溯
    doc_id INTEGER NOT NULL,               -- 来源文档
    chunk_id INTEGER,                      -- 来源chunk

    -- 能力描述
    capability_name VARCHAR(200) NOT NULL, -- 能力名称(AI提取)
    capability_type VARCHAR(50),           -- 功能/接口/服务/支持能力
    capability_description TEXT,           -- 能力描述(AI提取)
    original_text TEXT,                    -- 原文摘录(证据)

    -- 关联标签
    tag_id INTEGER,                        -- 关联核心能力标签

    -- AI提取元数据
    extraction_model VARCHAR(50),          -- 使用的模型
    confidence_score FLOAT,                -- 提取置信度
    extracted_at TIMESTAMP,

    -- 向量索引
    capability_embedding BLOB,

    -- 人工审核
    verified BOOLEAN DEFAULT FALSE,
    verified_by VARCHAR(100),
    verified_at TIMESTAMP,

    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (company_id) REFERENCES companies(company_id),
    FOREIGN KEY (doc_id) REFERENCES documents(doc_id),
    FOREIGN KEY (chunk_id) REFERENCES document_chunks(chunk_id),
    FOREIGN KEY (tag_id) REFERENCES product_capability_tags(tag_id)
);

-- 3. 能力关键词表（辅助搜索）
CREATE TABLE capability_keywords (
    keyword_id INTEGER PRIMARY KEY AUTOINCREMENT,
    capability_id INTEGER NOT NULL,
    keyword VARCHAR(100) NOT NULL,
    keyword_type VARCHAR(50),              -- 同义词/相关词/技术术语/行业术语
    source VARCHAR(20),                    -- ai_extracted/manual
    FOREIGN KEY (capability_id) REFERENCES product_capabilities_index(capability_id) ON DELETE CASCADE
);

-- 4. 能力匹配历史表（用于学习优化）
CREATE TABLE capability_match_history (
    match_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    tender_project_id INTEGER,
    requirement_text TEXT,                 -- 招标需求原文
    matched_capability_id INTEGER,
    match_score FLOAT,
    match_method VARCHAR(50),              -- semantic/keyword/hybrid

    -- 用户反馈
    user_feedback VARCHAR(20),             -- correct/incorrect/partial
    feedback_note TEXT,
    feedback_by VARCHAR(100),
    feedback_at TIMESTAMP,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(company_id),
    FOREIGN KEY (tender_project_id) REFERENCES tender_projects(project_id),
    FOREIGN KEY (matched_capability_id) REFERENCES product_capabilities_index(capability_id)
);

-- 索引
CREATE INDEX idx_capability_tags_company ON product_capability_tags(company_id);
CREATE INDEX idx_capability_tags_parent ON product_capability_tags(parent_tag_id);

CREATE INDEX idx_capabilities_company ON product_capabilities_index(company_id);
CREATE INDEX idx_capabilities_doc ON product_capabilities_index(doc_id);
CREATE INDEX idx_capabilities_tag ON product_capabilities_index(tag_id);
CREATE INDEX idx_capabilities_verified ON product_capabilities_index(verified);

CREATE INDEX idx_capability_keywords_cap ON capability_keywords(capability_id);

CREATE INDEX idx_match_history_company ON capability_match_history(company_id);
CREATE INDEX idx_match_history_capability ON capability_match_history(matched_capability_id);
```

### 工作流程

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     产品能力索引构建流程                                  │
└─────────────────────────────────────────────────────────────────────────┘

【初始化】人工定义核心标签（一次性，20-30个）
    │
    │  示例：风控产品、实修、免密、位置服务...
    ▼
【文档上传】上传产品文档（持续）
    │
    ▼
【自动提取】AI能力提取器（自动）
    │  输入: document_chunks
    │  输出: 能力描述 + 置信度 + 原文
    ▼
【索引构建】存入 product_capabilities_index
    │
    ▼
【可选审核】人工验证关键能力
```

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     招标需求匹配流程                                      │
└─────────────────────────────────────────────────────────────────────────┘

招标需求 → ProductMatchAgent → 能力索引搜索
                │
                ▼
        ┌───────────────────────────────────────┐
        │ 匹配结果：                              │
        │                                        │
        │ ✅ 支持：能力描述 + 原文证据 + 文档链接  │
        │ ⚠️ 部分支持：相关但不完全匹配           │
        │ ❌ 不支持/需确认：未找到匹配能力         │
        └───────────────────────────────────────┘
                │
                ▼
        后续智能体只能引用"支持"的能力
```

### 多企业支持设计

```
┌─────────────────────────────────────────────────────────────────────────┐
│  企业A（当前公司）            │  企业B（其他客户）                       │
├─────────────────────────────────────────────────────────────────────────┤
│  核心标签:                    │  核心标签:                              │
│  ├── 风控产品                 │  ├── 智能制造                            │
│  │   ├── 反欺诈              │  │   ├── 设备监控                        │
│  │   ├── 实修                │  │   └── 预测维护                        │
│  │   └── 免密                │  ├── MES系统                            │
│  └── 位置服务                 │  └── 工业物联网                          │
│           ↓                   │           ↓                             │
│  上传自己的产品文档            │  上传自己的产品文档                       │
│           ↓                   │           ↓                             │
│  AI自动提取能力               │  AI自动提取能力                          │
└─────────────────────────────────────────────────────────────────────────┘

关键设计：
- product_capability_tags.company_id 隔离各企业标签
- product_capabilities_index.company_id 隔离各企业能力
- 标签完全由企业自定义，不预设行业分类
```

---

## 四、标书素材库设计

### 数据模型

```sql
-- 1. 标书文档表（整份标书）
CREATE TABLE IF NOT EXISTS tender_documents (
    tender_doc_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,

    -- 基本信息
    doc_name VARCHAR(255) NOT NULL,           -- 标书名称
    project_name VARCHAR(255),                -- 投标项目名称
    customer_name VARCHAR(255),               -- 招标方名称
    industry VARCHAR(100),                    -- 所属行业
    bid_date DATE,                            -- 投标日期

    -- 结果信息
    bid_result VARCHAR(50),                   -- won(中标)/lost(未中标)/unknown
    final_score DECIMAL(5,2),                 -- 最终得分
    technical_score DECIMAL(5,2),             -- 技术分
    commercial_score DECIMAL(5,2),            -- 商务分

    -- 文件信息
    file_path VARCHAR(500),
    file_type VARCHAR(20),
    file_size INTEGER,

    -- 处理状态
    parse_status VARCHAR(20) DEFAULT 'pending',
    chunk_status VARCHAR(20) DEFAULT 'pending',

    -- 标签和元数据
    tags TEXT,                                -- JSON数组
    metadata TEXT,                            -- JSON

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);

-- 2. 标书章节/片段表（核心）
CREATE TABLE IF NOT EXISTS tender_excerpts (
    excerpt_id INTEGER PRIMARY KEY AUTOINCREMENT,
    tender_doc_id INTEGER NOT NULL,
    company_id INTEGER NOT NULL,

    -- 章节信息
    chapter_number VARCHAR(50),               -- 章节号，如"3.1.2"
    chapter_title VARCHAR(255),               -- 章节标题
    chapter_level INTEGER DEFAULT 1,          -- 章节级别 1-4

    -- 内容
    content TEXT NOT NULL,                    -- 章节内容（纯文本）
    content_html TEXT,                        -- 章节内容（带格式）
    word_count INTEGER,                       -- 字数

    -- 质量评估
    quality_score INTEGER DEFAULT 0,          -- 质量评分 0-100
    is_highlighted BOOLEAN DEFAULT FALSE,     -- 是否为精选片段

    -- 分类标签
    category VARCHAR(100),                    -- 内容分类
    subcategory VARCHAR(100),                 -- 子分类
    keywords TEXT,                            -- JSON数组：关键词

    -- 评分点关联
    scoring_points TEXT,                      -- JSON数组：可响应的评分点类型

    -- 向量检索
    vector_embedding BLOB,
    vector_status VARCHAR(20) DEFAULT 'pending',

    -- 来源追溯
    source_page INTEGER,
    source_position TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (tender_doc_id) REFERENCES tender_documents(tender_doc_id),
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);

-- 3. 评分点响应模板表
CREATE TABLE IF NOT EXISTS scoring_response_templates (
    template_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER,

    -- 评分点信息
    scoring_point_type VARCHAR(100) NOT NULL,
    scoring_point_name VARCHAR(255),
    scoring_point_description TEXT,

    -- 响应模板
    response_template TEXT NOT NULL,
    response_structure TEXT,                  -- JSON

    -- 关键要素
    required_elements TEXT,                   -- JSON数组
    recommended_data TEXT,                    -- JSON数组

    -- 质量信息
    usage_count INTEGER DEFAULT 0,
    avg_score DECIMAL(5,2),

    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);

-- 索引
CREATE INDEX idx_tender_docs_company ON tender_documents(company_id);
CREATE INDEX idx_tender_docs_result ON tender_documents(bid_result);
CREATE INDEX idx_tender_docs_industry ON tender_documents(industry);

CREATE INDEX idx_excerpts_tender ON tender_excerpts(tender_doc_id);
CREATE INDEX idx_excerpts_company ON tender_excerpts(company_id);
CREATE INDEX idx_excerpts_category ON tender_excerpts(category);
CREATE INDEX idx_excerpts_quality ON tender_excerpts(quality_score DESC);
CREATE INDEX idx_excerpts_highlighted ON tender_excerpts(is_highlighted);

CREATE INDEX idx_templates_type ON scoring_response_templates(scoring_point_type);
CREATE INDEX idx_templates_company ON scoring_response_templates(company_id);
```

---

## 五、智能体架构

### 完整流程

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      质量驱动的智能体架构                                 │
└─────────────────────────────────────────────────────────────────────────┘

招标文件
    │
    ▼
┌──────────────────┐
│ ProductMatchAgent │ ← 新增！流程最前端
│ (产品匹配智能体)   │
├──────────────────┤
│ • 提取招标需求     │
│ • 匹配产品能力     │
│ • 识别：能/不能    │
│ • 输出：产品边界   │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ ScoringStrategy  │
│ Agent            │
├──────────────────┤
│ • 提取评分项       │
│ • 基于产品能力     │
│   判断得分可能性   │
│ • 输出：评分攻略   │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ MaterialRetriever│
│ Agent            │
├──────────────────┤
│ • 按评分点检索素材 │
│ • 限定在匹配产品   │
│   的文档范围内     │
│ • 输出：素材包     │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ OutlineArchitect │
│ Agent            │
├──────────────────┤
│ • 生成四级目录     │
│ • 标注素材引用     │
│ • 输出：详细骨架   │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ ContentWriter    │
│ Agent            │
├──────────────────┤
│ • 基于素材整合内容 │
│ • 只引用已有能力   │
│ • 输出：章节初稿   │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ ExpertReview     │
│ Agent            │
├──────────────────┤
│ • 多维度评分       │
│ • 识别薄弱章节     │
│ • 输出：评审报告   │
└────────┬─────────┘
         │
         ▼
      评分 < 85?
         │
    Yes ─┴─ No
         │    │
         ▼    │
┌──────────────────┐    │
│ RevisionAgent    │    │
├──────────────────┤    │
│ • 针对性修改       │    │
│ • 补充遗漏响应     │    │
└────────┬─────────┘    │
         │              │
         └──────────────┘
                        │
                        ▼
              ┌──────────────────┐
              │ PolishAgent      │
              ├──────────────────┤
              │ • 统一文风术语    │
              │ • 消除重复        │
              │ • 格式检查        │
              └────────┬─────────┘
                       │
                       ▼
                📄 高质量技术方案
```

### ProductMatchAgent 输入输出

```python
# 输入
{
    "tender_requirements": "招标文件提取的需求列表",
    "company_id": 1
}

# 输出
{
    "matched_products": ["风控产品", "位置服务"],
    "requirement_coverage": [
        {
            "requirement": "实时风控决策，响应时间<100ms",
            "status": "supported",
            "capability": "支持实时风控，响应时间<50ms",
            "evidence": "来自《风控引擎技术白皮书》第3章",
            "doc_id": 127
        },
        {
            "requirement": "区块链存证",
            "status": "not_supported",
            "note": "当前产品不支持，建议说明替代方案"
        }
    ],
    "risk_points": [
        "区块链存证需求无法满足，可能影响得分"
    ]
}
```

---

## 六、实施计划

### 第一阶段：基础设施（2.5周）

#### Week 1：标书素材库
| 天数 | 任务 | 产出 |
|------|------|------|
| Day 1-2 | 创建数据库表结构 | tender_library_schema.sql |
| Day 3-4 | 标书上传和解析功能 | TenderDocumentParser |
| Day 5-7 | 章节提取和向量化 | ExcerptExtractor |

#### Week 2：产品能力索引
| 天数 | 任务 | 产出 |
|------|------|------|
| Day 1-2 | 创建能力索引表结构 | capability_schema.sql |
| Day 3-4 | AI能力提取器 | CapabilityExtractor |
| Day 5-7 | 能力向量索引和搜索 | CapabilitySearcher |

#### Week 3 前半：产品文档库增强
| 天数 | 任务 | 产出 |
|------|------|------|
| Day 1-2 | 增加能力标注字段 | 表结构迁移 |
| Day 3 | 能力提取集成到文档上传流程 | 自动提取能力 |

### 第二阶段：智能体重构（2周）

#### Week 3 后半 + Week 4
| 天数 | 任务 | 产出 |
|------|------|------|
| Day 1-2 | ProductMatchAgent | 新文件 |
| Day 3-4 | ScoringStrategyAgent | 新文件 |
| Day 5-6 | MaterialRetrieverAgent | 新文件 |
| Day 7-8 | ContentWriterAgent 改造 | 改造现有 |
| Day 9-10 | ExpertReviewAgent + RevisionAgent | 新文件 |

#### Week 5
| 天数 | 任务 | 产出 |
|------|------|------|
| Day 1-2 | PolishAgent | 新文件 |
| Day 3-4 | ProposalCrew 总协调器 | 新文件 |
| Day 5 | 端到端流程测试 | 测试报告 |

### 第三阶段：集成优化（0.5周）
| 天数 | 任务 | 产出 |
|------|------|------|
| Day 1-2 | 性能优化（并发、缓存） | 性能报告 |
| Day 3 | 前端集成 | UI更新 |

**总工期：约5周**

---

## 七、关键代码结构

```
ai_tender_system/
├── modules/
│   ├── outline_generator/
│   │   ├── agents/
│   │   │   ├── base_agent.py              # 已有
│   │   │   ├── product_match_agent.py     # 新建 ⭐
│   │   │   ├── scoring_strategy_agent.py  # 新建
│   │   │   ├── material_retriever_agent.py # 新建
│   │   │   ├── content_writer_agent.py    # 改造
│   │   │   ├── expert_review_agent.py     # 新建
│   │   │   ├── revision_agent.py          # 新建
│   │   │   ├── polish_agent.py            # 新建
│   │   │   └── proposal_crew.py           # 新建
│   │   └── ...
│   │
│   ├── product_capability/                 # 新建模块 ⭐
│   │   ├── __init__.py
│   │   ├── capability_extractor.py        # AI能力提取
│   │   ├── capability_indexer.py          # 能力索引构建
│   │   ├── capability_searcher.py         # 能力搜索匹配
│   │   └── tag_manager.py                 # 核心标签管理
│   │
│   ├── tender_library/                     # 新建模块
│   │   ├── __init__.py
│   │   ├── tender_document_parser.py      # 标书解析
│   │   ├── excerpt_extractor.py           # 章节提取
│   │   ├── excerpt_annotator.py           # 质量标注
│   │   └── material_retriever.py          # 素材检索
│   │
│   └── knowledge_base/
│       └── rag_engine.py                  # 增强
│
├── database/
│   ├── tender_library_schema.sql          # 新建
│   ├── capability_schema.sql              # 新建 ⭐
│   └── migrations/
│
└── web/
    └── blueprints/
        ├── api_tender_library_bp.py       # 新建
        └── api_capability_bp.py           # 新建 ⭐
```

---

## 八、维护分工

| 内容 | 维护者 | 频率 |
|------|--------|------|
| 核心能力标签 | 产品经理 | 季度或产品线变化时 |
| 产品文档 | 技术团队 | 产品发布时上传 |
| 能力索引 | **系统自动** | 文档上传时自动提取 |
| 历史标书 | 标书团队 | 中标后上传 |
| 关键能力审核 | 产品经理 | 按需（高频能力优先） |

---

## 九、预期效果

| 维度 | 当前 | 改进后 |
|------|------|--------|
| 评分点覆盖率 | ~70% | ~95% |
| 专业深度 | 中等（套话多） | 高（有数据支撑） |
| 产品功能准确性 | 低（可能编造） | 高（有能力边界） |
| 可信度 | 低（无案例） | 高（有证据链接） |
| 整体得分预期 | 70-75分 | 85-90分 |

---

## 十、案例库说明

> ✅ **决定**：案例库保持现状，不做技术内容增强。
>
> **原因**：
> - 案例的技术内容可以从**标书素材库**中获取（历史中标标书本身就包含案例描述）
> - 现有合同信息足够填写招标要求的案例表格
> - 节省开发工作量，聚焦核心功能

**现有案例库用途**：
- 填写招标文件中的"业绩表"（客户名、合同金额、签约日期）
- 提供案例数量统计（"我司已完成XX个同类项目"）

**技术内容来源**：
- 从标书素材库检索"项目经验"相关章节
- 历史中标标书中通常有详细的项目案例描述
