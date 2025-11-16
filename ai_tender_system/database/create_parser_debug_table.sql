-- 目录解析调试测试表
-- 用于存储不同解析方法的对比测试结果

CREATE TABLE IF NOT EXISTS parser_debug_tests (
    -- 主键和标识
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id TEXT UNIQUE NOT NULL,
    filename TEXT NOT NULL,
    file_path TEXT NOT NULL,

    -- 时间戳
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    annotation_time TIMESTAMP,

    -- 文档基本信息
    total_paragraphs INTEGER,
    has_toc BOOLEAN DEFAULT 0,
    toc_items_count INTEGER DEFAULT 0,
    toc_start_idx INTEGER,
    toc_end_idx INTEGER,

    -- 解析结果（JSON格式存储各方法的完整结果）
    semantic_result TEXT,      -- 方法1: 语义锚点解析结果
    old_toc_result TEXT,       -- 方法2: 旧目录定位结果
    style_result TEXT,         -- 方法3: 样式识别结果
    outline_result TEXT,       -- 方法4: 大纲级别结果

    -- 性能指标（秒）
    semantic_elapsed REAL,
    old_toc_elapsed REAL,
    style_elapsed REAL,
    outline_elapsed REAL,

    -- 识别结果统计
    semantic_chapters_count INTEGER DEFAULT 0,
    old_toc_chapters_count INTEGER DEFAULT 0,
    style_chapters_count INTEGER DEFAULT 0,
    outline_chapters_count INTEGER DEFAULT 0,

    -- 人工标注（正确答案）
    ground_truth TEXT,         -- JSON格式的正确章节列表
    annotator TEXT,            -- 标注人
    ground_truth_count INTEGER DEFAULT 0,

    -- 准确率指标（自动计算，基于ground_truth）
    semantic_precision REAL,   -- 精确率
    semantic_recall REAL,      -- 召回率
    semantic_f1 REAL,          -- F1分数

    old_toc_precision REAL,
    old_toc_recall REAL,
    old_toc_f1 REAL,

    style_precision REAL,
    style_recall REAL,
    style_f1 REAL,

    outline_precision REAL,
    outline_recall REAL,
    outline_f1 REAL,

    -- 最佳方法（自动判定）
    best_method TEXT,          -- semantic/old_toc/style/outline
    best_f1_score REAL,

    -- 备注
    notes TEXT
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_parser_tests_document_id ON parser_debug_tests(document_id);
CREATE INDEX IF NOT EXISTS idx_parser_tests_upload_time ON parser_debug_tests(upload_time DESC);
CREATE INDEX IF NOT EXISTS idx_parser_tests_has_ground_truth ON parser_debug_tests(ground_truth IS NOT NULL);

-- 创建视图：测试结果概览
CREATE VIEW IF NOT EXISTS v_parser_debug_summary AS
SELECT
    document_id,
    filename,
    upload_time,
    has_toc,
    toc_items_count,

    -- 识别数量对比
    semantic_chapters_count,
    old_toc_chapters_count,
    style_chapters_count,
    outline_chapters_count,

    -- 性能对比
    semantic_elapsed,
    old_toc_elapsed,
    style_elapsed,
    outline_elapsed,

    -- 准确率对比（如果有标注）
    CASE WHEN ground_truth IS NOT NULL THEN semantic_f1 ELSE NULL END AS semantic_f1,
    CASE WHEN ground_truth IS NOT NULL THEN old_toc_f1 ELSE NULL END AS old_toc_f1,
    CASE WHEN ground_truth IS NOT NULL THEN style_f1 ELSE NULL END AS style_f1,
    CASE WHEN ground_truth IS NOT NULL THEN outline_f1 ELSE NULL END AS outline_f1,

    -- 最佳方法
    best_method,
    best_f1_score,

    -- 是否已标注
    CASE WHEN ground_truth IS NOT NULL THEN 1 ELSE 0 END AS has_ground_truth,
    annotator
FROM parser_debug_tests
ORDER BY upload_time DESC;
