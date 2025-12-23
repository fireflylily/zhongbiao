# 章节解析改进实施路线图

## 📋 执行摘要

**目标**: 将章节解析准确率从当前的 74.2% (方法3) / 238% (方法2) 提升至 **95%+ 自动准确 + 100% 最终准确**

**策略**: 三层验证体系
- **Layer 1**: 智能混合解析（自动）
- **Layer 2**: 边界验证和修正（自动）
- **Layer 3**: 人工可视化校验（辅助）

**预期收益**:
- ✅ 章节识别准确率: 95%+
- ✅ 字数统计准确率: 95-100%
- ✅ 人工校验时间: 减少 80% (从20分钟降至4分钟)
- ✅ 后续工作基础稳固: 100% (经人工确认)

---

## 🎯 Phase 1: 核心算法改进 (优先级: 高)

### 1.1 增强版精确匹配 (基于目录)

**文件**: `ai_tender_system/modules/tender_processing/structure_parser.py`

**改进点**:

#### ✅ 实现模糊匹配函数

```python
def _fuzzy_match_title(self, doc: Document, title: str, start_idx: int,
                       similarity_threshold: float = 0.85) -> Optional[int]:
    """
    模糊匹配章节标题

    Args:
        doc: Word文档对象
        title: 目标标题（来自目录）
        start_idx: 开始搜索的段落索引
        similarity_threshold: 相似度阈值 (0.0-1.0)

    Returns:
        匹配到的段落索引，未找到返回None

    匹配策略:
        1. 完全匹配: title == para.text
        2. 规范化匹配: normalize(title) == normalize(para.text)
        3. 相似度匹配: similarity(title, para.text) >= threshold
    """
    normalized_target = self._normalize_title(title)

    for idx in range(start_idx, len(doc.paragraphs)):
        para = doc.paragraphs[idx]
        para_text = para.text.strip()

        # 完全匹配
        if title == para_text:
            logger.debug(f"完全匹配: '{title}' at para {idx}")
            return idx

        # 规范化匹配
        normalized_para = self._normalize_title(para_text)
        if normalized_target == normalized_para:
            logger.info(f"规范化匹配: '{title}' → '{para_text}' at para {idx}")
            return idx

        # 相似度匹配
        similarity = SequenceMatcher(None, normalized_target, normalized_para).ratio()
        if similarity >= similarity_threshold:
            logger.info(
                f"模糊匹配: '{title}' → '{para_text}' "
                f"(相似度: {similarity:.2%}) at para {idx}"
            )
            return idx

    logger.warning(f"未找到匹配: '{title}' (搜索范围: {start_idx}-{len(doc.paragraphs)})")
    return None

def _normalize_title(self, text: str) -> str:
    """
    标题规范化

    规则:
    1. 移除所有空白字符（空格、全角空格、制表符）
    2. 移除常见标点符号（冒号、逗号、句号）
    3. 统一大小写（转小写）
    4. 移除编号后的冒号（如 "第一部分：" → "第一部分"）
    """
    import re

    # 移除空白和标点
    text = re.sub(r'[\s\u3000\t：:、，。]', '', text)

    # 转小写
    text = text.lower()

    return text
```

**测试用例**:
```python
def test_fuzzy_matching():
    """测试模糊匹配的各种场景"""
    test_cases = [
        # (目录标题, 正文标题, 预期匹配)
        ("第三部分 评标办法", "第三部分评标办法", True),      # 空格差异
        ("第三部分 评标办法", "第三部分：评标办法", True),   # 标点差异
        ("第三部分 评标办法", "第三部份 评标办法", True),    # 错别字
        ("第一章 项目概述", "1. 项目概述", False),           # 编号格式不同
    ]

    for toc_title, body_title, expected in test_cases:
        result = parser._fuzzy_match_title(doc, toc_title, 0)
        assert (result is not None) == expected
```

**工作量**: 2-3小时

---

#### ✅ 增强 `parse_by_toc_exact` 方法

**修改位置**: `structure_parser.py:1200` (大约位置，需要查找 `parse_by_toc_exact` 方法)

**改进方案**:

```python
def parse_by_toc_exact(self, doc: Document, force_parse: bool = False) -> Tuple[List[ChapterNode], Dict]:
    """
    基于目录的精确匹配解析 (增强版)

    改进点:
    1. 使用多策略匹配（完全匹配 → 模糊匹配）
    2. 记录匹配状态（matched, fuzzy_matched, not_found）
    3. 返回未匹配章节列表（供后续处理）
    """
    # 1. 检测目录区域
    toc_info = self._find_toc_section(doc)
    if not toc_info:
        logger.warning("未检测到目录，无法使用精确匹配")
        return [], {"status": "no_toc"}

    toc_start_idx, toc_end_idx = toc_info['start_idx'], toc_info['end_idx']

    # 2. 提取目录项
    toc_items = self._parse_toc_items(doc, toc_start_idx, toc_end_idx)
    logger.info(f"从目录中提取了 {len(toc_items)} 个章节")

    # 3. 匹配正文中的章节位置（🆕 增强匹配）
    chapters = []
    match_stats = {
        'total': len(toc_items),
        'exact_matched': 0,
        'fuzzy_matched': 0,
        'not_found': 0,
        'not_found_list': []
    }

    for item in toc_items:
        title = item['title']

        # 🆕 多策略匹配
        para_idx = self._find_chapter_in_body(
            doc,
            title,
            start_idx=toc_end_idx + 1,
            use_fuzzy=True  # 启用模糊匹配
        )

        if para_idx is not None:
            chapter = ChapterNode(
                id=f"ch_{len(chapters) + 1}",
                level=item.get('level', 1),
                title=title,
                para_start_idx=para_idx,
                para_end_idx=None,  # 稍后计算
                word_count=0,
                preview_text="",
                auto_selected=False,
                skip_recommended=False,
                content_tags=[]
            )

            # 记录匹配方式
            if para_idx == self._exact_match(doc, title, toc_end_idx + 1):
                match_stats['exact_matched'] += 1
                chapter.content_tags.append('exact_match')
            else:
                match_stats['fuzzy_matched'] += 1
                chapter.content_tags.append('fuzzy_match')

            chapters.append(chapter)
        else:
            # 未匹配到
            match_stats['not_found'] += 1
            match_stats['not_found_list'].append(title)
            logger.warning(f"未找到章节: {title}")

            # 🆕 仍然创建节点，但标记为未找到
            chapter = ChapterNode(
                id=f"ch_{len(chapters) + 1}_not_found",
                level=item.get('level', 1),
                title=title,
                para_start_idx=None,
                para_end_idx=None,
                word_count=0,
                preview_text="[未找到匹配内容]",
                auto_selected=False,
                skip_recommended=True,
                content_tags=['not_found', 'needs_manual_review']
            )
            chapters.append(chapter)

    # 4. 计算章节边界和字数
    chapters = self._calculate_chapter_boundaries(chapters, doc)

    # 5. 返回结果和统计
    logger.info(
        f"匹配完成: {match_stats['exact_matched']} 精确, "
        f"{match_stats['fuzzy_matched']} 模糊, "
        f"{match_stats['not_found']} 未找到"
    )

    return chapters, {
        'status': 'success',
        'method': 'toc_exact_enhanced',
        'match_stats': match_stats
    }

def _find_chapter_in_body(self, doc: Document, title: str, start_idx: int,
                           use_fuzzy: bool = True) -> Optional[int]:
    """
    在正文中查找章节位置（组合多种匹配策略）
    """
    # 策略1: 完全匹配
    idx = self._exact_match(doc, title, start_idx)
    if idx is not None:
        return idx

    # 策略2: 模糊匹配（如果启用）
    if use_fuzzy:
        idx = self._fuzzy_match_title(doc, title, start_idx, similarity_threshold=0.85)
        if idx is not None:
            return idx

    # 策略3: 模式匹配（基于编号）
    # TODO: 实现基于编号模式的智能匹配
    # 例如: "第三部分 评标办法" → 搜索以 "第三部分" 或 "三、" 开头的段落

    return None
```

**工作量**: 4-5小时

---

### 1.2 过滤式大纲识别 (无目录时)

**改进点**:

#### ✅ 实现伪章节过滤函数

```python
def _is_real_chapter_title(self, text: str, para_idx: int, doc: Document) -> bool:
    """
    判断是否为真正的章节标题（过滤伪标题）

    Args:
        text: 段落文本
        para_idx: 段落索引
        doc: 文档对象

    Returns:
        True: 真正的章节标题
        False: 伪标题（应过滤）

    过滤规则:
        1. 长度过短或过长
        2. 以冒号结尾的字段标题（如"项目名称："）
        3. 不包含章节编号标记
        4. 样式不符合章节样式
    """
    text = text.strip()

    # 规则1: 长度检查
    if len(text) < 2 or len(text) > 100:
        logger.debug(f"过滤: 长度不合适 ({len(text)}字) - '{text[:20]}...'")
        return False

    # 规则2: 排除字段标题（冒号结尾）
    if re.match(r'^[^：:]{2,15}[：:]$', text):
        logger.debug(f"过滤: 字段标题 - '{text}'")
        return False

    # 规则3: 必须包含章节编号标记
    has_numbering = False
    for pattern in self.NUMBERING_PATTERNS:
        if re.search(pattern, text):
            has_numbering = True
            break

    if not has_numbering:
        logger.debug(f"过滤: 无章节编号 - '{text}'")
        return False

    # 规则4: 样式检查（可选）
    # 检查是否有加粗、字号等格式特征
    para = doc.paragraphs[para_idx]
    if para.runs:
        first_run = para.runs[0]
        is_bold = first_run.bold
        font_size = first_run.font.size

        # 章节标题通常是加粗且字号较大
        # 这是一个辅助判断，不作为决定性条件
        if is_bold or (font_size and font_size.pt >= 14):
            logger.debug(f"样式提示: 可能是章节 (加粗={is_bold}, 字号={font_size})")

    logger.debug(f"✓ 识别为真章节: '{text}'")
    return True
```

**测试用例**:
```python
def test_chapter_title_filtering():
    """测试章节标题过滤"""
    test_cases = [
        # (文本, 预期结果)
        ("第一部分 招标公告", True),           # 真章节
        ("1.1 项目概述", True),               # 真章节
        ("项目名称：", False),                # 字段标题
        ("招标编号：", False),                # 字段标题
        ("这是一段很长的描述性文字...", False),  # 普通段落
        ("附件1：技术规格书", True),          # 真章节（附件）
    ]

    for text, expected in test_cases:
        result = parser._is_real_chapter_title(text, 0, doc)
        assert result == expected, f"Failed for: {text}"
```

**工作量**: 3-4小时

---

#### ✅ 修正重复计算问题

**问题根源**: `_calculate_statistics` 递归累加父子章节字数

**解决方案**:

```python
def _calculate_statistics(self, chapter_tree: List[ChapterNode]) -> Dict:
    """
    计算统计信息（修正版：避免重复计数）

    策略:
    - 只统计叶子节点的字数（无子章节的章节）
    - 或者统计根节点时排除已被子章节覆盖的内容
    """
    stats = {
        "total_chapters": 0,
        "total_words": 0,
        "avg_words_per_chapter": 0,
        "max_level": 0,
        "chapters_by_level": {}
    }

    def traverse(chapters, current_level=1):
        """递归遍历章节树"""
        for ch in chapters:
            stats["total_chapters"] += 1
            stats["max_level"] = max(stats["max_level"], current_level)

            # 更新层级统计
            level_key = f"level_{current_level}"
            stats["chapters_by_level"][level_key] = \
                stats["chapters_by_level"].get(level_key, 0) + 1

            # 🆕 修正: 只统计叶子节点字数
            if not ch.children:
                # 叶子节点: 统计全部内容
                stats["total_words"] += ch.word_count
            else:
                # 非叶子节点: 只统计标题到第一个子章节之间的内容
                # 这部分已在 calculate_leaf_content_only 中处理
                intro_word_count = self._calculate_intro_content(ch)
                stats["total_words"] += intro_word_count

            # 递归处理子章节
            if ch.children:
                traverse(ch.children, current_level + 1)

    traverse(chapter_tree)

    if stats["total_chapters"] > 0:
        stats["avg_words_per_chapter"] = stats["total_words"] // stats["total_chapters"]

    return stats

def _calculate_intro_content(self, chapter: ChapterNode) -> int:
    """
    计算非叶子节点的引导内容字数

    引导内容 = 章节标题后 到 第一个子章节前 的内容
    """
    if not chapter.children:
        return chapter.word_count

    # 计算范围: para_start_idx 到 children[0].para_start_idx - 1
    start = chapter.para_start_idx
    end = chapter.children[0].para_start_idx - 1

    if end <= start:
        return 0

    # 这里需要访问原始文档来计算字数
    # 为了避免重新读取，建议在解析时就计算好
    return 0  # 暂时返回0，实际应该计算
```

**工作量**: 2-3小时

---

### 1.3 混合解析策略

**实现函数**:

```python
def parse_document_structure(self, file_path: str, methods: List[str] = None,
                              fallback: bool = True,
                              enable_hybrid: bool = True) -> Dict:
    """
    解析文档结构（支持混合策略）

    Args:
        file_path: 文档路径
        methods: 使用的解析方法列表 ['toc_exact', 'outline_level']
        fallback: 是否启用降级策略
        enable_hybrid: 是否启用混合解析（🆕）

    Returns:
        解析结果字典，包含章节树和统计信息
    """
    doc = Document(file_path)

    # 🆕 混合解析模式
    if enable_hybrid:
        logger.info("🔄 启用混合解析策略")

        # 步骤1: 尝试基于目录的精确匹配
        toc_chapters, toc_meta = self.parse_by_toc_exact(doc, force_parse=False)

        if toc_meta.get('status') == 'success':
            not_found_count = toc_meta['match_stats']['not_found']

            if not_found_count == 0:
                # 完美匹配，直接返回
                logger.info("✅ 目录精确匹配成功，无需混合")
                return self._build_result(toc_chapters, toc_meta, doc)

            else:
                # 部分匹配失败，启用混合策略
                logger.warning(f"⚠️  {not_found_count} 个章节未匹配，启用混合策略")

                # 步骤2: 使用大纲级别补充
                outline_chapters, outline_meta = self.parse_by_outline_level(
                    doc,
                    filter_pseudo_titles=True  # 🆕 启用过滤
                )

                # 步骤3: 智能合并
                merged_chapters = self._smart_merge_chapters(
                    toc_chapters,
                    outline_chapters,
                    toc_meta['match_stats']['not_found_list']
                )

                # 步骤4: 边界验证和修正
                validated_chapters, issues = self._validate_and_fix_boundaries(
                    merged_chapters,
                    doc
                )

                return self._build_result(validated_chapters, {
                    'status': 'hybrid_success',
                    'method': 'toc_exact + outline_level',
                    'toc_matched': toc_meta['match_stats']['exact_matched'] +
                                   toc_meta['match_stats']['fuzzy_matched'],
                    'outline_補充': not_found_count,
                    'validation_issues': issues
                }, doc)

        else:
            # 无目录，降级到大纲级别
            logger.info("📋 未检测到目录，使用过滤式大纲识别")
            outline_chapters, outline_meta = self.parse_by_outline_level(
                doc,
                filter_pseudo_titles=True
            )
            return self._build_result(outline_chapters, outline_meta, doc)

    # 原有逻辑保持不变...
    else:
        # 旧的单一方法解析逻辑
        pass

def _smart_merge_chapters(self, toc_chapters: List[ChapterNode],
                          outline_chapters: List[ChapterNode],
                          not_found_titles: List[str]) -> List[ChapterNode]:
    """
    智能合并两种方法的解析结果

    策略:
    1. TOC匹配的章节优先
    2. 对于未匹配的章节，从outline_chapters中查找最佳匹配
    3. 保持原有顺序
    """
    merged = []

    for toc_ch in toc_chapters:
        if 'not_found' in toc_ch.content_tags:
            # 从大纲级别结果中查找匹配
            best_match = self._find_best_outline_match(
                toc_ch.title,
                outline_chapters
            )

            if best_match:
                logger.info(f"🔗 混合匹配成功: '{toc_ch.title}' ← {best_match.title}")
                toc_ch.para_start_idx = best_match.para_start_idx
                toc_ch.para_end_idx = best_match.para_end_idx
                toc_ch.word_count = best_match.word_count
                toc_ch.preview_text = best_match.preview_text
                toc_ch.content_tags.remove('not_found')
                toc_ch.content_tags.append('hybrid_matched')
                toc_ch.skip_recommended = False
            else:
                logger.warning(f"❌ 仍未找到匹配: '{toc_ch.title}'")

        merged.append(toc_ch)

    return merged

def _find_best_outline_match(self, toc_title: str,
                              outline_chapters: List[ChapterNode]) -> Optional[ChapterNode]:
    """
    从大纲级别结果中查找最佳匹配

    使用模糊匹配算法
    """
    normalized_target = self._normalize_title(toc_title)
    best_match = None
    best_similarity = 0.0

    for outline_ch in outline_chapters:
        normalized_outline = self._normalize_title(outline_ch.title)
        similarity = SequenceMatcher(None, normalized_target, normalized_outline).ratio()

        if similarity > best_similarity:
            best_similarity = similarity
            best_match = outline_ch

    # 只返回相似度 >= 0.75 的匹配
    if best_similarity >= 0.75:
        logger.debug(f"找到匹配: '{toc_title}' → '{best_match.title}' (相似度: {best_similarity:.2%})")
        return best_match

    return None
```

**工作量**: 5-6小时

---

## 🔧 Phase 2: 边界验证和修正 (优先级: 高)

### 2.1 自动边界验证

**文件**: `ai_tender_system/modules/tender_processing/structure_parser.py`

**实现函数**:

```python
def _validate_and_fix_boundaries(self, chapters: List[ChapterNode],
                                  doc: Document,
                                  expected_total_words: Optional[int] = None) -> Tuple[List[ChapterNode], List[Dict]]:
    """
    验证和修正章节边界

    检查项:
    1. 章节间无重叠
    2. 章节间无大间隙
    3. 字数合理性（非0）
    4. 总字数匹配（如果提供了预期值）

    Returns:
        (修正后的章节列表, 问题列表)
    """
    issues = []

    # 检查1: 重叠和间隙
    for i in range(len(chapters) - 1):
        current = chapters[i]
        next_ch = chapters[i + 1]

        if current.para_start_idx is None or next_ch.para_start_idx is None:
            continue

        # 检查重叠
        if current.para_end_idx and current.para_end_idx >= next_ch.para_start_idx:
            issues.append({
                'type': 'OVERLAP',
                'severity': 'error',
                'chapter_index': i,
                'chapter_title': current.title,
                'description': f"章节 '{current.title}' 的结束位置 ({current.para_end_idx}) "
                               f"超过了下一章节 '{next_ch.title}' 的起始位置 ({next_ch.para_start_idx})",
                'auto_fix': 'adjust_end_idx'
            })

            # 自动修正
            logger.warning(f"🔧 自动修正重叠: '{current.title}' end_idx {current.para_end_idx} → {next_ch.para_start_idx - 1}")
            current.para_end_idx = next_ch.para_start_idx - 1

        # 检查间隙
        elif current.para_end_idx:
            gap = next_ch.para_start_idx - current.para_end_idx - 1
            if gap > 5:  # 间隙超过5个段落
                gap_content = '\n'.join(
                    p.text for p in doc.paragraphs[current.para_end_idx + 1:next_ch.para_start_idx]
                    if p.text.strip()
                )

                if gap_content:
                    issues.append({
                        'type': 'GAP',
                        'severity': 'warning',
                        'chapter_index': i,
                        'location': f"章节 '{current.title}' 和 '{next_ch.title}' 之间",
                        'gap_size': gap,
                        'gap_content_preview': gap_content[:200] + ('...' if len(gap_content) > 200 else ''),
                        'description': f"存在 {gap} 个段落的间隙，可能遗漏了内容"
                    })

    # 检查2: 0字章节
    for i, chapter in enumerate(chapters):
        if chapter.word_count == 0 and chapter.title not in ['封面', '目录', '扉页']:
            issues.append({
                'type': 'ZERO_WORDS',
                'severity': 'error',
                'chapter_index': i,
                'chapter_title': chapter.title,
                'description': f"章节 '{chapter.title}' 字数为0，可能边界错误或匹配失败",
                'needs_manual_review': True
            })

    # 检查3: 总字数验证
    if expected_total_words:
        total_calculated = sum(ch.word_count for ch in chapters if ch.word_count)
        diff = total_calculated - expected_total_words
        diff_percent = abs(diff) / expected_total_words * 100

        if diff_percent > 10:  # 差异超过10%
            issues.append({
                'type': 'TOTAL_MISMATCH',
                'severity': 'error',
                'calculated_words': total_calculated,
                'expected_words': expected_total_words,
                'difference': diff,
                'difference_percent': diff_percent,
                'description': f"总字数差异过大: 计算 {total_calculated} vs 预期 {expected_total_words} "
                               f"(差异 {diff_percent:.1f}%)"
            })

    logger.info(f"边界验证完成: 发现 {len(issues)} 个问题")
    return chapters, issues
```

**工作量**: 4-5小时

---

### 2.2 后端API增强

**文件**: `ai_tender_system/web/blueprints/api_parser_debug_bp.py`

**新增API端点**:

```python
@api_parser_debug_bp.route('/api/parser-debug/validate-boundaries', methods=['POST'])
def validate_chapter_boundaries():
    """
    验证章节边界（提供预期字数）

    Request:
    {
        "test_id": 123,
        "expected_total_words": 28600  # 从Word文档统计获取
    }

    Response:
    {
        "status": "success",
        "validation_result": {
            "total_chapters": 6,
            "calculated_words": 21212,
            "expected_words": 28600,
            "match_percentage": 74.2,
            "issues": [
                {
                    "type": "ZERO_WORDS",
                    "severity": "error",
                    "chapter_title": "第三部分 评标办法",
                    "description": "..."
                }
            ]
        }
    }
    """
    data = request.json
    test_id = data.get('test_id')
    expected_words = data.get('expected_total_words')

    # 获取解析结果
    test = ParserDebugTest.get_by_id(test_id)
    result = json.loads(test.result_data)

    # 执行验证
    parser = DocumentStructureParser()
    doc = Document(test.document_path)

    chapters = [ChapterNode(**ch) for ch in result['chapters']]
    validated_chapters, issues = parser._validate_and_fix_boundaries(
        chapters,
        doc,
        expected_total_words=expected_words
    )

    # 计算匹配度
    total_calculated = sum(ch.word_count for ch in validated_chapters)
    match_percentage = (total_calculated / expected_words * 100) if expected_words else 100

    return jsonify({
        'status': 'success',
        'validation_result': {
            'total_chapters': len(validated_chapters),
            'calculated_words': total_calculated,
            'expected_words': expected_words,
            'match_percentage': round(match_percentage, 1),
            'issues': issues
        }
    })
```

**工作量**: 3-4小时

---

## 🎨 Phase 3: 人工校验界面 (优先级: 中)

### 3.1 边界调整组件

**文件**: `frontend/src/components/ChapterBoundaryEditor.vue` (新建)

**功能**:
1. 可视化显示章节边界
2. 手动调整起止段落索引
3. 实时预览内容
4. 实时计算字数
5. 显示验证问题

**实现骨架** (见 CHAPTER_PARSING_IMPROVEMENT.md 第 448-634 行)

**工作量**: 8-10小时

---

### 3.2 集成到解析对比页面

**文件**: `frontend/src/views/Debug/ParserComparison.vue`

**修改点**:

```vue
<template>
  <div class="parser-comparison">
    <!-- 原有对比卡片 -->

    <!-- 🆕 边界校验面板 -->
    <el-collapse v-model="activePanel" v-if="showBoundaryEditor">
      <el-collapse-item title="章节边界校验和调整" name="boundary">
        <ChapterBoundaryEditor
          :chapters="selectedMethodResult.chapters"
          :expected-words="expectedTotalWords"
          :total-paragraphs="documentTotalParagraphs"
          @boundaries-confirmed="onBoundariesConfirmed"
        />
      </el-collapse-item>
    </el-collapse>
  </div>
</template>

<script setup>
import ChapterBoundaryEditor from '@/components/ChapterBoundaryEditor.vue'

const showBoundaryEditor = ref(false)
const expectedTotalWords = ref(null)

// 从Word文档获取预期字数
async function loadExpectedWordCount() {
  const response = await api.getDocumentStats(documentId)
  expectedTotalWords.value = response.total_words
}

function onBoundariesConfirmed(adjustedChapters) {
  // 保存调整后的章节边界
  api.saveChapterBoundaries(testId, adjustedChapters)
  ElMessage.success('章节边界已确认')
}
</script>
```

**工作量**: 4-5小时

---

## 📊 Phase 4: 测试和优化 (优先级: 高)

### 4.1 准备测试数据集

**目标**: 收集 10-15 个真实标书文档

**分类**:
- 有目录文档: 5个
- 无目录文档: 5个
- 特殊格式文档: 3-5个（复杂目录、多层级、附件多等）

**测试指标**:
- 章节识别准确率 (%)
- 字数统计准确率 (%)
- 边界准确性 (人工验证)
- 性能 (解析时间)

**工作量**: 4-6小时（包括数据收集和人工标注）

---

### 4.2 自动化测试脚本

**文件**: `tests/test_structure_parser_accuracy.py` (新建)

```python
#!/usr/bin/env python3
"""
结构解析器准确性测试
"""
import pytest
from ai_tender_system.modules.tender_processing.structure_parser import DocumentStructureParser

# 测试数据集（人工标注的真实标书）
TEST_DOCUMENTS = [
    {
        'file_path': '/path/to/doc1.docx',
        'expected_chapters': 6,
        'expected_total_words': 28600,
        'has_toc': True,
        'chapter_titles': ['第一部分 招标公告', '第二部分 投标人须知', ...]
    },
    # ... 更多测试文档
]

@pytest.mark.parametrize("doc_info", TEST_DOCUMENTS)
def test_parsing_accuracy(doc_info):
    """测试解析准确率"""
    parser = DocumentStructureParser()
    result = parser.parse_document_structure(
        doc_info['file_path'],
        enable_hybrid=True
    )

    # 验证章节数量
    assert len(result['chapters']) == doc_info['expected_chapters'], \
        f"章节数量不匹配: {len(result['chapters'])} vs {doc_info['expected_chapters']}"

    # 验证总字数（允许5%误差）
    total_words = result['statistics']['total_words']
    expected_words = doc_info['expected_total_words']
    diff_percent = abs(total_words - expected_words) / expected_words * 100

    assert diff_percent <= 5, \
        f"字数差异过大: {total_words} vs {expected_words} (差异 {diff_percent:.1f}%)"

    # 验证章节标题
    parsed_titles = [ch['title'] for ch in result['chapters']]
    for expected_title in doc_info['chapter_titles']:
        assert any(
            SequenceMatcher(None, expected_title, parsed_title).ratio() >= 0.9
            for parsed_title in parsed_titles
        ), f"未找到匹配标题: {expected_title}"

def test_performance():
    """测试解析性能"""
    import time

    parser = DocumentStructureParser()

    for doc_info in TEST_DOCUMENTS:
        start_time = time.time()
        result = parser.parse_document_structure(doc_info['file_path'])
        elapsed = time.time() - start_time

        # 解析时间应 < 5秒
        assert elapsed < 5.0, f"解析时间过长: {elapsed:.2f}s"
```

**工作量**: 6-8小时

---

## 📅 实施时间表

### Sprint 1 (第1-2周): 核心算法改进

| 任务 | 工作量 | 负责人 | 状态 |
|------|--------|--------|------|
| 1.1.1 模糊匹配函数 | 2-3h | - | ⏳ 待开始 |
| 1.1.2 增强 parse_by_toc_exact | 4-5h | - | ⏳ 待开始 |
| 1.2.1 伪章节过滤 | 3-4h | - | ⏳ 待开始 |
| 1.2.2 修正重复计算 | 2-3h | - | ⏳ 待开始 |
| 1.3 混合解析策略 | 5-6h | - | ⏳ 待开始 |
| **小计** | **16-21h** | | |

### Sprint 2 (第3周): 边界验证

| 任务 | 工作量 | 负责人 | 状态 |
|------|--------|--------|------|
| 2.1 自动边界验证 | 4-5h | - | ⏳ 待开始 |
| 2.2 后端API增强 | 3-4h | - | ⏳ 待开始 |
| **小计** | **7-9h** | | |

### Sprint 3 (第4-5周): 人工校验界面

| 任务 | 工作量 | 负责人 | 状态 |
|------|--------|--------|------|
| 3.1 边界调整组件 | 8-10h | - | ⏳ 待开始 |
| 3.2 集成到解析对比页面 | 4-5h | - | ⏳ 待开始 |
| **小计** | **12-15h** | | |

### Sprint 4 (第6周): 测试和优化

| 任务 | 工作量 | 负责人 | 状态 |
|------|--------|--------|------|
| 4.1 准备测试数据集 | 4-6h | - | ⏳ 待开始 |
| 4.2 自动化测试 | 6-8h | - | ⏳ 待开始 |
| 4.3 问题修复和优化 | 8-10h | - | ⏳ 待开始 |
| **小计** | **18-24h** | | |

**总工作量**: 53-69小时 (约 1.5-2 个月，按每周 20 小时计算)

---

## 🎯 成功指标

### 量化目标

| 指标 | 当前值 | 目标值 | 验证方式 |
|------|--------|--------|----------|
| **字数准确率** | 74.2% (方法3) | **95%+** | 自动测试 (与Word统计对比) |
| **章节识别率** | 50% (3/6章节0字) | **100%** | 人工验证 |
| **0字章节比例** | 50% | **< 5%** | 自动检测 |
| **人工校验时间** | ~20分钟/文档 | **< 5分钟** | 时间测量 |
| **问题自动检测率** | 0% | **100%** | 验证覆盖所有已知问题类型 |

### 验收标准

#### Phase 1 验收:
- [ ] 模糊匹配通过率 >= 90% (测试用例)
- [ ] 伪章节过滤准确率 >= 95%
- [ ] 混合解析字数准确率 >= 85%

#### Phase 2 验收:
- [ ] 边界验证覆盖所有问题类型（重叠、间隙、0字、总数）
- [ ] 自动修正成功率 >= 80%

#### Phase 3 验收:
- [ ] 界面可用性测试通过（5名用户测试）
- [ ] 手动调整后字数匹配度 >= 98%

#### Phase 4 验收:
- [ ] 10个测试文档的平均准确率 >= 95%
- [ ] 解析时间 < 5秒/文档
- [ ] 0 critical bugs

---

## 🚀 快速开始

### 开发环境设置

```bash
# 1. 创建功能分支
git checkout -b feature/chapter-parsing-improvement

# 2. 安装依赖（如有新增）
pip install -r requirements.txt

# 3. 运行现有测试（确保基础功能正常）
pytest tests/test_structure_parser.py

# 4. 开始开发...
```

### 开发顺序建议

```
第1步: 实现模糊匹配函数 (_fuzzy_match_title, _normalize_title)
  ↓
第2步: 实现伪章节过滤 (_is_real_chapter_title)
  ↓
第3步: 增强 parse_by_toc_exact
  ↓
第4步: 修正统计计算 (_calculate_statistics)
  ↓
第5步: 实现混合策略 (_smart_merge_chapters)
  ↓
第6步: 实现边界验证 (_validate_and_fix_boundaries)
  ↓
第7步: 后端API
  ↓
第8步: 前端界面
  ↓
第9步: 集成测试
```

---

## 📝 注意事项

### 风险和缓解措施

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|----------|
| 现有功能回归 | 高 | 中 | 完善单元测试，保持向后兼容 |
| 性能下降 | 中 | 低 | 性能基准测试，优化算法 |
| 新引入bug | 高 | 中 | 代码审查，自动化测试 |
| 文档格式多样性 | 高 | 高 | 收集更多样本，迭代优化 |

### 开发规范

1. **代码审查**: 所有改动需要PR和审查
2. **测试覆盖**: 新增代码测试覆盖率 >= 80%
3. **文档更新**: 同步更新API文档和用户手册
4. **日志记录**: 关键路径添加详细日志（DEBUG/INFO级别）
5. **错误处理**: 所有异常情况都有友好提示

---

## 📚 参考资料

- [原始问题分析](/Users/lvhe/Downloads/zhongbiao/zhongbiao/CHAPTER_PARSING_IMPROVEMENT.md)
- [项目创建流程设计](/Users/lvhe/Downloads/zhongbiao/zhongbiao/PROJECT_CREATION_DESIGN.md)
- [现有解析器代码](ai_tender_system/modules/tender_processing/structure_parser.py)
- [层级分析器](ai_tender_system/modules/tender_processing/level_analyzer.py)

---

**最后更新**: 2025-12-22
**负责人**: [待分配]
**状态**: 📋 规划中
