-- 添加 LLM智能层级分析 字段到 parser_debug_tests 表
-- 用于存储 LLM 层级分析的测试结果

-- 添加 LLM 层级分析结果字段
ALTER TABLE parser_debug_tests ADD COLUMN llm_level_result TEXT;
ALTER TABLE parser_debug_tests ADD COLUMN llm_level_elapsed REAL;
ALTER TABLE parser_debug_tests ADD COLUMN llm_level_chapters_count INTEGER DEFAULT 0;

-- 添加 LLM 层级分析准确率字段
ALTER TABLE parser_debug_tests ADD COLUMN llm_level_precision REAL;
ALTER TABLE parser_debug_tests ADD COLUMN llm_level_recall REAL;
ALTER TABLE parser_debug_tests ADD COLUMN llm_level_f1 REAL;

-- 重新创建summary视图以包含LLM层级分析列
DROP VIEW IF EXISTS v_parser_debug_summary;

CREATE VIEW v_parser_debug_summary AS
SELECT
    document_id,
    filename,
    upload_time,
    has_toc,
    toc_items_count,

    -- 识别数量对比（所有8种方法）
    toc_exact_chapters_count,
    semantic_chapters_count,
    style_chapters_count,
    hybrid_chapters_count,
    azure_chapters_count,
    docx_native_chapters_count,
    gemini_chapters_count,
    llm_level_chapters_count,

    -- 性能对比
    toc_exact_elapsed,
    semantic_elapsed,
    style_elapsed,
    hybrid_elapsed,
    azure_elapsed,
    docx_native_elapsed,
    gemini_elapsed,
    llm_level_elapsed,

    -- 准确率对比（如果有标注）
    CASE WHEN ground_truth IS NOT NULL THEN toc_exact_f1 ELSE NULL END AS toc_exact_f1,
    CASE WHEN ground_truth IS NOT NULL THEN semantic_f1 ELSE NULL END AS semantic_f1,
    CASE WHEN ground_truth IS NOT NULL THEN style_f1 ELSE NULL END AS style_f1,
    CASE WHEN ground_truth IS NOT NULL THEN hybrid_f1 ELSE NULL END AS hybrid_f1,
    CASE WHEN ground_truth IS NOT NULL THEN azure_f1 ELSE NULL END AS azure_f1,
    CASE WHEN ground_truth IS NOT NULL THEN docx_native_f1 ELSE NULL END AS docx_native_f1,
    CASE WHEN ground_truth IS NOT NULL THEN gemini_f1 ELSE NULL END AS gemini_f1,
    CASE WHEN ground_truth IS NOT NULL THEN llm_level_f1 ELSE NULL END AS llm_level_f1,

    -- 最佳方法
    best_method,
    best_f1_score,

    -- 是否已标注
    CASE WHEN ground_truth IS NOT NULL THEN 1 ELSE 0 END AS has_ground_truth,
    annotator
FROM parser_debug_tests
ORDER BY upload_time DESC;
