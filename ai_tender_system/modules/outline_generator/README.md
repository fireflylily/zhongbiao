# 技术方案大纲生成器

## 功能概述

从技术需求文档自动生成结构化的技术方案应答大纲，包含章节结构、应答建议、产品文档推荐等内容。

## 核心功能

### 阶段1：需求分析（RequirementAnalyzer）
- 解析技术需求文档（Word/PDF/Excel）
- AI提取需求列表并分类
- 标注优先级（★高优/▲关键/普通）
- 提取关键词用于后续匹配

### 阶段2：大纲生成（OutlineGenerator）
- 根据需求分析生成章节结构（1-3级标题）
- 为每个章节生成应答建议
- 提供填写提示和内容提示
- 推荐需要提供的证明材料

### 阶段3：产品文档匹配（ProductMatcher）
- 从知识库搜索相关产品文档
- 根据关键词计算相关度
- 推荐最相关的2-5份文档
- 说明引用方式和关键章节

### 阶段4：方案组装（ProposalAssembler）
- 组装完整的技术方案结构
- 整合需求、大纲、匹配文档
- 生成附件（需求分析报告、匹配表、生成报告）

### Word导出（WordExporter）
- 导出主技术方案Word文档
- 导出需求分析报告（可选）
- 导出需求匹配表Excel（可选）
- 导出生成报告文本文件（可选）

## API使用

### 端点：POST `/api/generate-proposal`

**请求参数（multipart/form-data）：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| tender_file | File | 是 | 技术需求文档（.doc/.docx/.pdf/.xlsx/.xls） |
| product_file | File | 否 | 产品文档（暂未使用） |
| company_id | String | 否 | 公司ID（用于过滤知识库） |
| output_prefix | String | 否 | 输出文件名前缀（默认"技术方案"） |
| includeAnalysis | Boolean | 否 | 是否生成需求分析报告（默认false） |
| includeMapping | Boolean | 否 | 是否生成需求匹配表（默认false） |
| includeSummary | Boolean | 否 | 是否生成生成报告（默认false） |

**响应格式：**

```json
{
  "success": true,
  "requirements_count": 50,
  "features_count": 0,
  "sections_count": 5,
  "matches_count": 45,
  "output_files": {
    "proposal": "/downloads/技术方案_20250115_103000.docx",
    "analysis": "/downloads/技术方案_需求分析_20250115_103000.docx",
    "mapping": "/downloads/技术方案_需求匹配表_20250115_103000.xlsx",
    "summary": "/downloads/技术方案_生成报告_20250115_103000.txt"
  }
}
```

## 代码示例

### Python示例

```python
from modules.outline_generator import (
    RequirementAnalyzer,
    OutlineGenerator,
    ProductMatcher,
    ProposalAssembler,
    WordExporter
)

# 1. 需求分析
analyzer = RequirementAnalyzer()
analysis_result = analyzer.analyze_document("需求文档.docx")

# 2. 大纲生成
outline_gen = OutlineGenerator()
outline_data = outline_gen.generate_outline(
    analysis_result,
    project_name="XX项目"
)

# 3. 产品文档匹配
matcher = ProductMatcher()
matched_docs = matcher.match_documents(
    analysis_result.get('requirement_categories', []),
    company_id=1
)

# 4. 方案组装
assembler = ProposalAssembler()
proposal = assembler.assemble_proposal(
    outline_data,
    analysis_result,
    matched_docs,
    options={
        'include_analysis': True,
        'include_mapping': True,
        'include_summary': True
    }
)

# 5. 导出Word
exporter = WordExporter()
exporter.export_proposal(proposal, "技术方案.docx")
exporter.export_analysis_report(analysis_result, "需求分析.docx")
```

### cURL示例

```bash
curl -X POST http://localhost:5000/api/generate-proposal \
  -F "tender_file=@需求文档.docx" \
  -F "output_prefix=XX项目技术方案" \
  -F "company_id=1" \
  -F "includeAnalysis=true" \
  -F "includeMapping=true" \
  -F "includeSummary=true"
```

## 输出文件说明

### 1. 技术方案.docx（主文档）

```
技术方案应答大纲

生成时间: 2025-01-15 10:30:00
总章节数: 5
预计页数: 60

1 技术方案总体设计
  【本章说明】本章从整体架构、技术选型、设计理念三个维度阐述技术方案
  【应答策略】建议从系统架构图入手，展示分层设计和模块化思想

  1.1 需求理解与分析
    【内容提示】
    • 【AI分析】本项目核心需求包括：
    • - 用户角色权限管理（★高优先级）
    • - 数据可视化大屏（▲需提供演示视频）

    【应答建议】
    • 重点说明对用户权限管理的理解
    • 针对数据可视化，说明支持的图表类型

    【建议引用文档】
    • 2-权限管理模块.docx - 包含权限管理的详细功能说明

    【需提供证明材料】
    （暂无）

2 功能需求应答
  ...

3 技术指标响应
  ...
```

### 2. 需求分析报告.docx（可选）

- 文档摘要（总需求数、强制需求、可选需求）
- 需求分类（按类别列出需求）
- 关键需求清单

### 3. 需求匹配表.xlsx（可选）

| 序号 | 需求类别 | 具体需求 | 匹配产品文档 | 匹配状态 |
|------|---------|---------|-------------|---------|
| 1 | 功能性需求 | 用户角色权限管理 | 2-权限管理模块.docx | 已匹配 |
| 2 | 非功能性需求 | 支持≥1000并发用户 | 1-系统架构设计.docx | 已匹配 |

### 4. 生成报告.txt（可选）

```
============================================================
技术方案生成报告
============================================================

一、生成信息
  方案标题: XX项目技术方案应答大纲
  生成时间: 2025-01-15 10:30:00
  总章节数: 5

二、需求统计
  总需求数: 50
  强制需求: 30
  可选需求: 15
  复杂度: high

三、匹配统计
  匹配文档数: 12
  匹配类别数: 4
  匹配成功率: 80.0%
```

## 配置说明

### 提示词配置

提示词存储在 `prompts/outline_generation.json`：

- `analyze_requirements`: 需求分析提示词
- `generate_outline`: 大纲生成提示词
- `generate_response_suggestions`: 应答建议提示词
- `recommend_product_docs`: 文档推荐提示词

### 环境变量

在 `.env` 文件中配置：

```bash
# LLM API配置
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini

# 文件路径配置
UPLOAD_DIR=data/uploads
OUTPUT_DIR=data/output
```

## 测试

运行测试脚本：

```bash
python3 test_outline_generator.py
```

## 注意事项

1. **文档格式**：目前支持 .doc, .docx, .pdf, .xlsx, .xls 格式
2. **文件大小**：建议单个文件不超过50MB
3. **处理时间**：根据文档大小和复杂度，处理时间约2-5分钟
4. **LLM调用**：需要配置有效的LLM API密钥
5. **知识库依赖**：产品文档匹配功能依赖知识库，建议先上传产品文档到知识库

## 常见问题

### Q1: 为什么没有匹配到产品文档？
A: 可能原因：
- 知识库中没有相关产品文档
- 公司ID过滤导致找不到文档
- 需求关键词与产品文档标题/摘要不匹配

解决方法：
- 先上传产品文档到知识库
- 不指定company_id，搜索所有文档
- 优化产品文档的标题和摘要

### Q2: 生成的大纲不够详细怎么办？
A: 可以调整提示词配置：
- 修改 `prompts/outline_generation.json` 中的提示词
- 增加更多应答建议和填写提示
- 调整LLM的temperature参数

### Q3: 如何自定义章节结构？
A: 修改大纲生成提示词中的建议结构：
- 编辑 `generate_outline` 提示词
- 指定期望的章节层级和标题
- 调整章节顺序和内容

## 版本历史

- v1.0.0 (2025-01-15): 初始版本发布
  - 实现4阶段处理流程
  - 支持多种文档格式
  - AI驱动的需求分析和大纲生成
  - 知识库集成的产品文档匹配
  - Word/Excel导出功能
