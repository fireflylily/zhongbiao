-- 数据库迁移: 将 old_toc 字段重命名为 hybrid
-- 创建时间: 2025-01-16
-- 描述: 删除方法二(旧目录定位),改为方法三(混合启发式)

-- Step 1: 创建新的表结构
CREATE TABLE IF NOT EXISTS parser_debug_tests_new (
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
    style_result TEXT,         -- 方法2: 样式识别结果
    hybrid_result TEXT,        -- 方法3: 混合启发式结果
    azure_result TEXT,         -- 方法4: Azure Form Recognizer结果

    -- 性能指标（秒）
    semantic_elapsed REAL,
    style_elapsed REAL,
    hybrid_elapsed REAL,
    azure_elapsed REAL,

    -- 识别结果统计
    semantic_chapters_count INTEGER DEFAULT 0,
    style_chapters_count INTEGER DEFAULT 0,
    hybrid_chapters_count INTEGER DEFAULT 0,
    azure_chapters_count INTEGER DEFAULT 0,

    -- 人工标注（正确答案）
    ground_truth TEXT,         -- JSON格式的正确章节列表
    annotator TEXT,            -- 标注人
    ground_truth_count INTEGER DEFAULT 0,

    -- 准确率指标（自动计算，基于ground_truth）
    semantic_precision REAL,   -- 精确率
    semantic_recall REAL,      -- 召回率
    semantic_f1 REAL,          -- F1分数

    style_precision REAL,
    style_recall REAL,
    style_f1 REAL,

    hybrid_precision REAL,
    hybrid_recall REAL,
    hybrid_f1 REAL,

    azure_precision REAL,
    azure_recall REAL,
    azure_f1 REAL,

    -- 最佳方法（自动判定）
    best_method TEXT,          -- semantic/style/hybrid/azure
    best_f1_score REAL,

    -- 备注
    notes TEXT
);

-- Step 2: 迁移现有数据 (跳过old_toc和outline字段)
INSERT INTO parser_debug_tests_new (
    id, document_id, filename, file_path,
    upload_time, annotation_time,
    total_paragraphs, has_toc, toc_items_count, toc_start_idx, toc_end_idx,
    semantic_result, style_result, azure_result,
    semantic_elapsed, style_elapsed, azure_elapsed,
    semantic_chapters_count, style_chapters_count, azure_chapters_count,
    ground_truth, annotator, ground_truth_count,
    semantic_precision, semantic_recall, semantic_f1,
    style_precision, style_recall, style_f1,
    azure_precision, azure_recall, azure_f1,
    best_method, best_f1_score,
    notes
)
SELECT
    id, document_id, filename, file_path,
    upload_time, annotation_time,
    total_paragraphs, has_toc, toc_items_count, toc_start_idx, toc_end_idx,
    semantic_result, style_result, azure_result,
    semantic_elapsed, style_elapsed, azure_elapsed,
    semantic_chapters_count, style_chapters_count, azure_chapters_count,
    ground_truth, annotator, ground_truth_count,
    semantic_precision, semantic_recall, semantic_f1,
    style_precision, style_recall, style_f1,
    azure_precision, azure_recall, azure_f1,
    -- 更新best_method: 将old_toc改为hybrid
    CASE
        WHEN best_method = 'old_toc' THEN 'semantic'  -- 旧方法二结果作为语义锚点
        WHEN best_method = 'outline' THEN 'hybrid'    -- 旧方法四作为新的混合方法
        ELSE best_method
    END as best_method,
    best_f1_score,
    notes
FROM parser_debug_tests;

-- Step 3: 删除旧表
DROP TABLE parser_debug_tests;

-- Step 4: 重命名新表
ALTER TABLE parser_debug_tests_new RENAME TO parser_debug_tests;

-- Step 5: 重新创建索引
CREATE INDEX IF NOT EXISTS idx_parser_tests_document_id ON parser_debug_tests(document_id);
CREATE INDEX IF NOT EXISTS idx_parser_tests_upload_time ON parser_debug_tests(upload_time DESC);
CREATE INDEX IF NOT EXISTS idx_parser_tests_has_ground_truth ON parser_debug_tests(ground_truth IS NOT NULL);

-- Step 6: 删除并重新创建视图
DROP VIEW IF EXISTS v_parser_debug_summary;

CREATE VIEW v_parser_debug_summary AS
SELECT
    document_id,
    filename,
    upload_time,
    has_toc,
    toc_items_count,

    -- 识别数量对比
    semantic_chapters_count,
    style_chapters_count,
    hybrid_chapters_count,
    azure_chapters_count,

    -- 性能对比
    semantic_elapsed,
    style_elapsed,
    hybrid_elapsed,
    azure_elapsed,

    -- 准确率对比（如果有标注）
    CASE WHEN ground_truth IS NOT NULL THEN semantic_f1 ELSE NULL END AS semantic_f1,
    CASE WHEN ground_truth IS NOT NULL THEN style_f1 ELSE NULL END AS style_f1,
    CASE WHEN ground_truth IS NOT NULL THEN hybrid_f1 ELSE NULL END AS hybrid_f1,
    CASE WHEN ground_truth IS NOT NULL THEN azure_f1 ELSE NULL END AS azure_f1,

    -- 最佳方法
    best_method,
    best_f1_score,

    -- 是否已标注
    CASE WHEN ground_truth IS NOT NULL THEN 1 ELSE 0 END AS has_ground_truth,
    annotator
FROM parser_debug_tests
ORDER BY upload_time DESC;

-- 迁移完成
