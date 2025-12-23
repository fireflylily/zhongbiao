# 新建项目功能设计方案

## 📋 需求概述

### 业务流程
```
用户上传标书
  ↓
系统解析章节结构（一次性完成，作为后续工作的基石）
  ↓
步骤1: 确认并分类标书章节
  - 项目信息部分（提取项目名称、编号、投标日期等）
  - 应答文件格式章节（商务应答模板）
  - 技术需求部分（点对点应答和技术方案生成）
  ↓
步骤2: 确认项目基本信息（AI自动提取 + 人工确认）
  ↓
步骤3: 开始后续处理
  - 商务应答（基于应答文件格式）
  - 技术方案（基于技术需求）
  - 点对点应答（基于技术需求）
```

### 核心原则
1. **章节边界是基石**: 一次解析，全程使用，保证一致性
2. **章节分类是关键**: 不同类型章节用于不同的后续处理
3. **避免重复计算**: 统计数据和实际提取内容必须一致

---

## 🗄️ 数据模型设计

### 1. 章节分类新增字段

在 `tender_document_chapters` 表中新增字段：

```sql
ALTER TABLE tender_document_chapters ADD COLUMN chapter_type VARCHAR(50) DEFAULT 'other';
-- 可选值:
-- 'project_info'        - 项目信息部分
-- 'response_template'   - 应答文件格式
-- 'technical_requirement' - 技术需求
-- 'other'               - 其他章节

ALTER TABLE tender_document_chapters ADD COLUMN usage_purpose TEXT;
-- JSON格式，记录章节用途，例如:
-- {"extract_project_info": true, "business_template": true, "technical_p2p": true}

ALTER TABLE tender_document_chapters ADD COLUMN content_extracted BOOLEAN DEFAULT FALSE;
-- 标记内容是否已提取（避免重复提取）

ALTER TABLE tender_document_chapters ADD COLUMN extracted_content_path VARCHAR(500);
-- 提取后的内容文件路径（如果需要单独存储）
```

### 2. 项目信息提取结果表

```sql
CREATE TABLE IF NOT EXISTS project_extracted_info (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,

    -- 提取来源
    source_chapter_ids TEXT,  -- JSON数组，来源章节ID列表

    -- 提取的信息（对应 tender_projects 的字段）
    extracted_project_name VARCHAR(255),
    extracted_project_number VARCHAR(100),
    extracted_tenderer VARCHAR(255),
    extracted_agency VARCHAR(255),
    extracted_bidding_method VARCHAR(100),
    extracted_bidding_location VARCHAR(255),
    extracted_bidding_time VARCHAR(100),
    extracted_budget_amount VARCHAR(100),
    extracted_winner_count VARCHAR(50),

    -- 联系人信息
    extracted_tenderer_contact TEXT,  -- JSON: {name, phone, email}
    extracted_agency_contact TEXT,    -- JSON: {name, phone, email}

    -- AI提取元数据
    ai_confidence FLOAT,  -- 整体置信度
    ai_extraction_method VARCHAR(50),  -- 提取方法 (regex/llm/hybrid)
    extraction_details TEXT,  -- JSON格式，每个字段的置信度和来源

    -- 人工确认状态
    confirmed BOOLEAN DEFAULT FALSE,
    confirmed_by VARCHAR(100),
    confirmed_at TIMESTAMP,

    -- 元数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (project_id) REFERENCES tender_projects(project_id) ON DELETE CASCADE
);

CREATE INDEX idx_extracted_info_project ON project_extracted_info(project_id);
```

### 3. 章节内容缓存表（避免重复提取）

```sql
CREATE TABLE IF NOT EXISTS chapter_content_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chapter_id INTEGER NOT NULL,
    project_id INTEGER NOT NULL,

    -- 内容
    full_content TEXT NOT NULL,  -- 完整文本内容
    word_count INTEGER,          -- 实际字数

    -- 提取信息
    extraction_method VARCHAR(50),  -- 提取方法 (direct/with_tables)
    extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- 元数据
    content_hash VARCHAR(64),  -- 内容哈希值，用于检测变更

    FOREIGN KEY (chapter_id) REFERENCES tender_document_chapters(chapter_id) ON DELETE CASCADE,
    FOREIGN KEY (project_id) REFERENCES tender_projects(project_id) ON DELETE CASCADE,

    UNIQUE(chapter_id)  -- 每个章节只缓存一次
);

CREATE INDEX idx_content_cache_project ON chapter_content_cache(project_id);
CREATE INDEX idx_content_cache_chapter ON chapter_content_cache(chapter_id);
```

---

## 🔄 完整业务流程设计

### 阶段1: 上传文档并解析章节（一次性完成）

#### API: `POST /api/tender-processing/parse-structure`

**请求参数**:
```json
{
  "file": "<Word文档>",
  "company_id": 123,
  "project_id": null,  // 可选，为空时自动创建
  "methods": ["toc_exact"],  // 优先使用精确匹配
  "fallback": true
}
```

**返回数据**:
```json
{
  "success": true,
  "project_id": 456,
  "chapters": [
    {
      "id": "ch_0",
      "level": 1,
      "title": "第一部分 招标公告",
      "para_start_idx": 38,
      "para_end_idx": 103,
      "word_count": 2669,
      "preview_text": "...",
      "auto_selected": true,
      "skip_recommended": false,
      "suggested_type": "project_info",  // 🆕 AI建议的章节类型
      "children": []
    },
    {
      "id": "ch_3",
      "level": 1,
      "title": "第四部分 投标文件格式",
      "para_start_idx": 200,
      "para_end_idx": 350,
      "word_count": 5000,
      "suggested_type": "response_template"
    },
    {
      "id": "ch_4",
      "level": 1,
      "title": "第五部分 技术需求书",
      "para_start_idx": 351,
      "para_end_idx": 500,
      "word_count": 8000,
      "suggested_type": "technical_requirement"
    }
  ],
  "statistics": {
    "total_chapters": 6,
    "total_words": 21212,
    "auto_selected": 3
  },
  "ai_suggestions": {
    "project_info_chapters": ["ch_0"],
    "response_template_chapters": ["ch_3"],
    "technical_requirement_chapters": ["ch_4", "ch_5"]
  }
}
```

**后端处理**:
1. ✅ 解析文档结构（仅一次）
2. ✅ 保存所有章节到数据库，包括 `para_start_idx`, `para_end_idx`, `word_count`
3. 🆕 **AI智能分类**: 根据章节标题和内容预览，建议章节类型
4. 🆕 返回章节分类建议给前端

---

### 阶段2: 用户确认并分类章节

#### API: `POST /api/tender-processing/confirm-chapters`

**请求参数**:
```json
{
  "project_id": 456,
  "chapter_classifications": [
    {
      "chapter_id": "ch_0",
      "is_selected": true,
      "chapter_type": "project_info",
      "usage_purpose": {
        "extract_project_info": true
      }
    },
    {
      "chapter_id": "ch_3",
      "is_selected": true,
      "chapter_type": "response_template",
      "usage_purpose": {
        "business_template": true
      }
    },
    {
      "chapter_id": "ch_4",
      "is_selected": true,
      "chapter_type": "technical_requirement",
      "usage_purpose": {
        "technical_p2p": true,
        "technical_proposal": true
      }
    }
  ]
}
```

**返回数据**:
```json
{
  "success": true,
  "summary": {
    "total_selected": 3,
    "project_info_chapters": 1,
    "response_template_chapters": 1,
    "technical_requirement_chapters": 2,
    "total_words": 15669
  }
}
```

**后端处理**:
1. 更新章节的 `is_selected`, `chapter_type`, `usage_purpose`
2. 🚫 **不重新解析文档**，使用已保存的章节边界
3. 更新 `tender_projects.step1_status = 'completed'`
4. 更新 `tender_projects.step1_completed_at`

---

### 阶段3: 提取章节内容并缓存（按需提取）

#### API: `POST /api/tender-processing/extract-chapter-content`

**请求参数**:
```json
{
  "project_id": 456,
  "chapter_ids": ["ch_0", "ch_3", "ch_4"],
  "force_refresh": false  // 是否强制重新提取（默认使用缓存）
}
```

**返回数据**:
```json
{
  "success": true,
  "chapters": [
    {
      "chapter_id": "ch_0",
      "title": "第一部分 招标公告",
      "content": "完整文本内容...",
      "word_count": 2669,
      "from_cache": false
    }
  ],
  "total_words": 15669
}
```

**后端处理**:
```python
def extract_chapter_content(project_id, chapter_ids, force_refresh=False):
    db = get_knowledge_base_db()

    # 获取项目文档路径
    project = db.execute_query(
        "SELECT tender_document_path FROM tender_projects WHERE project_id = ?",
        (project_id,), fetch_one=True
    )
    doc_path = project['tender_document_path']

    # 获取章节边界信息（从数据库，不重新解析）
    chapters = db.execute_query("""
        SELECT chapter_id, chapter_node_id, title,
               para_start_idx, para_end_idx, word_count
        FROM tender_document_chapters
        WHERE project_id = ? AND chapter_node_id IN ({})
    """.format(','.join(['?']*len(chapter_ids))),
    [project_id] + chapter_ids)

    doc = Document(doc_path)
    results = []

    for chapter in chapters:
        # 检查缓存
        if not force_refresh:
            cached = db.execute_query("""
                SELECT full_content, word_count
                FROM chapter_content_cache
                WHERE chapter_id = ?
            """, (chapter['chapter_id'],), fetch_one=True)

            if cached:
                results.append({
                    "chapter_id": chapter['chapter_node_id'],
                    "title": chapter['title'],
                    "content": cached['full_content'],
                    "word_count": cached['word_count'],
                    "from_cache": True
                })
                continue

        # 🎯 关键：使用保存的边界信息，不重新解析
        content_paras = doc.paragraphs[
            chapter['para_start_idx']:chapter['para_end_idx']+1
        ]
        content = '\n'.join(p.text for p in content_paras)
        word_count = len(content.replace(' ', '').replace('\n', ''))

        # 保存到缓存
        db.execute_query("""
            INSERT OR REPLACE INTO chapter_content_cache
            (chapter_id, project_id, full_content, word_count, extraction_method)
            VALUES (?, ?, ?, ?, 'direct')
        """, (chapter['chapter_id'], project_id, content, word_count))

        results.append({
            "chapter_id": chapter['chapter_node_id'],
            "title": chapter['title'],
            "content": content,
            "word_count": word_count,
            "from_cache": False
        })

    return {"success": True, "chapters": results}
```

---

### 阶段4: 提取项目信息（AI自动提取）

#### API: `POST /api/tender-processing/extract-project-info`

**请求参数**:
```json
{
  "project_id": 456
}
```

**返回数据**:
```json
{
  "success": true,
  "extracted_info": {
    "project_name": "XX系统采购项目",
    "project_number": "GXTC-C-251590031",
    "tenderer": "XX有限公司",
    "agency": "国信招标集团",
    "bidding_time": "2025年08月12日 17:00",
    "budget_amount": "500000",
    "winner_count": "2家"
  },
  "extraction_details": {
    "project_name": {"confidence": 0.95, "source": "第一部分 招标公告"},
    "project_number": {"confidence": 1.0, "source": "第一部分 招标公告"}
  }
}
```

**后端处理**:
1. 查询 `chapter_type='project_info'` 的章节
2. 从缓存读取章节内容（如果没有缓存，先调用提取接口）
3. 使用AI或正则表达式提取项目信息
4. 保存到 `project_extracted_info` 表
5. **不更新** `tender_projects` 表（等待用户确认）

---

### 阶段5: 用户确认项目信息

#### API: `POST /api/tender-processing/confirm-project-info`

**请求参数**:
```json
{
  "project_id": 456,
  "confirmed_info": {
    "project_name": "XX系统采购项目（修改版）",
    "project_number": "GXTC-C-251590031",
    "tenderer": "XX有限公司",
    // ... 其他字段
  }
}
```

**后端处理**:
1. 更新 `tender_projects` 表的项目信息字段
2. 更新 `project_extracted_info.confirmed = TRUE`
3. 更新 `tender_projects.step2_status = 'completed'`

---

## 🎨 前端交互设计

### 步骤1: 章节确认界面

```vue
<template>
  <div class="chapter-confirmation">
    <h2>步骤1: 确认并分类章节</h2>

    <!-- 统计信息 -->
    <el-card class="stats-card">
      <div>识别章节数: {{ statistics.total_chapters }}</div>
      <div>总字数: {{ statistics.total_words }}</div>
    </el-card>

    <!-- 章节分类选择 -->
    <div class="chapter-list">
      <div v-for="chapter in chapters" :key="chapter.id" class="chapter-item">
        <el-checkbox v-model="chapter.is_selected">
          {{ chapter.title }}
        </el-checkbox>

        <!-- 章节类型选择 -->
        <el-select
          v-model="chapter.chapter_type"
          :disabled="!chapter.is_selected"
          placeholder="选择章节用途"
        >
          <el-option label="项目信息部分" value="project_info" />
          <el-option label="应答文件格式" value="response_template" />
          <el-option label="技术需求部分" value="technical_requirement" />
          <el-option label="其他" value="other" />
        </el-select>

        <!-- 预览 -->
        <div class="preview">{{ chapter.preview_text }}</div>
        <div class="meta">字数: {{ chapter.word_count }}</div>
      </div>
    </div>

    <el-button @click="confirmChapters" type="primary">
      确认章节分类
    </el-button>
  </div>
</template>
```

### 步骤2: 项目信息确认界面

```vue
<template>
  <div class="project-info-confirmation">
    <h2>步骤2: 确认项目信息</h2>

    <el-alert type="info">
      以下信息由AI自动提取，请仔细核对
    </el-alert>

    <el-form :model="projectInfo" label-width="120px">
      <el-form-item label="项目名称">
        <el-input v-model="projectInfo.project_name" />
        <span class="confidence">
          置信度: {{ extractionDetails.project_name.confidence * 100 }}%
        </span>
      </el-form-item>

      <el-form-item label="项目编号">
        <el-input v-model="projectInfo.project_number" />
      </el-form-item>

      <!-- 其他字段... -->

      <el-button @click="confirmProjectInfo" type="primary">
        确认信息
      </el-button>
    </el-form>
  </div>
</template>
```

---

## 📊 数据一致性保证

### 关键策略

1. **唯一解析源**:
   - 章节解析只在上传时进行一次
   - 所有后续操作使用数据库中保存的 `para_start_idx`, `para_end_idx`

2. **内容缓存**:
   - 提取的章节内容保存到 `chapter_content_cache`
   - 避免重复读取文档

3. **字数统计一致性**:
   ```python
   # 解析时计算
   word_count = len(content.replace(' ', '').replace('\n', ''))

   # 提取时使用相同算法
   word_count = len(content.replace(' ', '').replace('\n', ''))
   ```

4. **版本控制**:
   - 如果文档需要重新上传，清空所有章节和缓存数据
   - 重新执行完整流程

---

## 🔧 实施步骤

### Phase 1: 数据库改造
- [ ] 添加章节分类字段
- [ ] 创建 `project_extracted_info` 表
- [ ] 创建 `chapter_content_cache` 表

### Phase 2: 后端API实现
- [ ] 优化 `parse-structure` API（添加AI分类建议）
- [ ] 实现 `confirm-chapters` API
- [ ] 实现 `extract-chapter-content` API（使用缓存）
- [ ] 实现 `extract-project-info` API
- [ ] 实现 `confirm-project-info` API

### Phase 3: 前端界面
- [ ] 章节确认和分类界面
- [ ] 项目信息确认界面
- [ ] 流程进度指示器

### Phase 4: 测试验证
- [ ] 单元测试：章节内容提取一致性
- [ ] 集成测试：完整流程测试
- [ ] 性能测试：缓存命中率

---

## ✅ 优势总结

| 特性 | 当前方案 | 新方案 |
|------|---------|--------|
| **章节解析** | 可能重复 | ✅ 仅一次 |
| **字数统计** | 可能不一致 | ✅ 完全一致 |
| **章节分类** | ❌ 无 | ✅ 三种类型 |
| **内容缓存** | ❌ 无 | ✅ 有 |
| **性能** | 慢（重复解析） | ✅ 快（缓存） |
| **数据一致性** | 差 | ✅ 好 |
| **业务流程** | 不清晰 | ✅ 清晰明确 |

---

## 🎯 核心改进点

1. **章节边界作为基石**: 一次解析，全程复用
2. **章节智能分类**: 自动建议 + 人工确认
3. **内容提取优化**: 使用缓存，避免重复读取
4. **AI辅助提取**: 自动提取项目信息，提高效率
5. **数据一致性**: 统计数据和实际内容完全一致

---

## 📝 使用示例

```python
# 1. 上传并解析
response = requests.post('/api/tender-processing/parse-structure',
    files={'file': document},
    data={'company_id': 123})

project_id = response.json()['project_id']
chapters = response.json()['chapters']

# 2. 用户在前端确认章节分类
classifications = [
    {"chapter_id": "ch_0", "is_selected": True, "chapter_type": "project_info"},
    {"chapter_id": "ch_4", "is_selected": True, "chapter_type": "technical_requirement"}
]

requests.post('/api/tender-processing/confirm-chapters',
    json={'project_id': project_id, 'chapter_classifications': classifications})

# 3. 提取项目信息
info = requests.post('/api/tender-processing/extract-project-info',
    json={'project_id': project_id})

# 4. 用户确认信息
requests.post('/api/tender-processing/confirm-project-info',
    json={'project_id': project_id, 'confirmed_info': info.json()['extracted_info']})

# 5. 后续处理（商务应答、技术方案等）
# 使用缓存的章节内容，不需要重新解析
```
