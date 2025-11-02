# RAG知识库完整实施方案

## 📋 项目概述

本方案将LangChain + Chroma方案完整集成到AI标书系统中，实现：
- ✅ 文档自动向量化存储
- ✅ AI智能检索和问答
- ✅ 无缝集成到现有知识库UI

---

## 🚀 第一步：安装依赖

### 1.1 安装RAG相关Python包

```bash
cd /Users/lvhe/Downloads/zhongbiao/zhongbiao
pip install -r requirements_rag.txt
```

**依赖说明：**
- `langchain`: RAG框架核心
- `chromadb`: 轻量级向量数据库
- `sentence-transformers`: Embedding模型运行时
- `text2vec`: 中文Embedding模型
- `pypdf`, `python-docx`: 文档解析

### 1.2 下载中文Embedding模型

首次运行时会自动下载模型，或手动下载：

```python
from sentence_transformers import SentenceTransformer

# 下载模型（约400MB）
model = SentenceTransformer('shibing624/text2vec-base-chinese')
```

---

## 📁 第二步：目录结构

已创建的文件：

```
ai_tender_system/
├── knowledge_base/
│   ├── rag_engine.py          # RAG引擎核心模块
│   ├── rag_api.py              # RAG API接口
│   └── ...
├── web/
│   ├── app.py                  # 主应用（已注册RAG API）
│   ├── static/js/pages/knowledge-base/
│   │   ├── rag-integration.js  # RAG前端集成模块
│   │   └── ...
│   └── templates/
│       └── knowledge_base.html # 知识库页面（已添加AI检索UI）
├── data/
│   └── chroma_db/              # 向量数据库存储目录（自动创建）
└── requirements_rag.txt         # RAG依赖列表
```

---

## ⚙️ 第三步：配置和启动

### 3.1 启动服务

```bash
# 停止旧服务
lsof -ti:8110 | xargs kill -9 2>/dev/null || true

# 启动新服务
python3 -m ai_tender_system.web.app
```

### 3.2 验证RAG服务状态

访问：http://127.0.0.1:8110/api/rag/status

响应示例：
```json
{
    "success": true,
    "available": true,
    "stats": {
        "total_chunks": 0,
        "persist_directory": ".../data/chroma_db"
    }
}
```

---

## 🎯 第四步：使用方法

### 4.1 前端UI操作

1. **打开知识库页面**: http://127.0.0.1:8110/knowledge_base

2. **启动AI智能检索**:
   - 点击左侧企业树顶部的 ⭐ 图标（"AI智能检索"按钮）
   - 或直接在主内容区看到检索框

3. **上传文档（自动向量化）**:
   - 上传企业资质、产品文档等文件
   - 系统会自动调用向量化API
   - 显示"正在建立智能索引..."提示

4. **执行智能检索**:
   - 在检索框输入问题，如："公司有哪些ISO认证？"
   - 点击"智能搜索"按钮
   - 查看检索结果和相关度分数

### 4.2 API接口调用

#### 4.2.1 手动向量化文档

```bash
curl -X POST http://127.0.0.1:8110/api/rag/vectorize_document \
-H "Content-Type: application/json" \
-d '{
  "file_path": "/path/to/document.pdf",
  "metadata": {
    "company_id": 8,
    "document_id": 123,
    "document_type": "qualification",
    "document_name": "ISO9001证书.pdf"
  }
}'
```

响应：
```json
{
  "success": true,
  "file_path": "/path/to/document.pdf",
  "chunks_count": 15,
  "vector_ids": ["id1", "id2", ...]
}
```

#### 4.2.2 智能检索

```bash
curl -X POST http://127.0.0.1:8110/api/rag/search \
-H "Content-Type: application/json" \
-d '{
  "query": "公司的ISO认证有哪些？",
  "company_id": 8,
  "k": 5
}'
```

响应：
```json
{
  "success": true,
  "query": "公司的ISO认证有哪些？",
  "results": [
    {
      "content": "本公司已获得ISO9001、ISO27001、ISO20000三项体系认证...",
      "score": 0.92,
      "metadata": {
        "company_id": 8,
        "document_name": "ISO证书.pdf",
        "document_type": "qualification"
      },
      "source": "ISO证书.pdf"
    }
  ],
  "count": 5
}
```

#### 4.2.3 删除文档向量

```bash
curl -X DELETE http://127.0.0.1:8110/api/rag/delete_document \
-H "Content-Type: application/json" \
-d '{
  "document_id": 123,
  "company_id": 8
}'
```

---

## 🔧 第五步：集成到文档上传流程

### 5.1 修改文档上传成功回调

在文档上传成功后，自动调用向量化：

```javascript
// 文档上传成功后
async function onDocumentUploaded(response) {
    const docInfo = {
        file_path: response.file_path,
        company_id: currentCompanyId,
        product_id: currentProductId,
        document_id: response.document_id,
        document_type: response.document_type,
        document_name: response.file_name
    };

    // 自动向量化
    await window.ragIntegration.vectorizeDocument(docInfo);
}
```

### 5.2 在document-manager.js中集成

找到文档上传成功的回调函数，添加：

```javascript
if (window.ragIntegration) {
    await window.ragIntegration.vectorizeDocument({
        file_path: uploadedFilePath,
        company_id: this.currentCompanyId,
        product_id: this.currentProductId,
        document_id: documentId,
        document_type: docType,
        document_name: fileName
    });
}
```

---

## 📊 第六步：监控和维护

### 6.1 查看向量数据库统计

```bash
sqlite3 ai_tender_system/data/chroma_db/chroma.sqlite3
.tables
SELECT COUNT(*) FROM embeddings;
```

### 6.2 清理向量数据库

```python
# 清空所有向量数据
rm -rf ai_tender_system/data/chroma_db/*
```

### 6.3 日志监控

查看RAG相关日志：

```bash
tail -f ai_tender_system/data/logs/web_app.log | grep -i "rag\|vector\|embedding"
```

---

## 🎨 第七步：自定义和优化

### 7.1 调整文本切分参数

编辑 `rag_engine.py` 第43行：

```python
self.text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,      # 增大可以保留更多上下文
    chunk_overlap=50,    # 增大重叠可以提高连贯性
    length_function=len,
    separators=["\n\n", "\n", "。", "！", "？", "；", "，", " ", ""]
)
```

### 7.2 切换Embedding模型

如果免费模型效果不够好，可以切换为API：

```python
# 使用通义千问Embedding API
from langchain.embeddings import DashScopeEmbeddings

self.embeddings = DashScopeEmbeddings(
    model="text-embedding-v2",
    dashscope_api_key="your-api-key"
)
```

### 7.3 添加大模型问答

当前只实现了检索，如需生成式问答：

```python
from langchain.chains import RetrievalQA
from langchain.llms import Tongyi  # 或其他LLM

llm = Tongyi(dashscope_api_key="your-api-key")
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=self.vectorstore.as_retriever(search_kwargs={"k": 3})
)

answer = qa_chain.run("公司有哪些ISO认证？")
```

---

## ❓ 常见问题

### Q1: 提示"RAG服务不可用"？

**A:** 检查依赖是否安装：
```bash
pip list | grep langchain
pip list | grep chromadb
```

### Q2: 向量化速度很慢？

**A:** 首次运行需要下载模型（400MB），耐心等待。后续会很快。

### Q3: 检索结果不准确？

**A:** 可能原因：
1. 文档内容太少
2. 查询方式不对（尽量用自然语言）
3. 需要调整chunk_size参数

### Q4: 想要批量导入已有文档？

**A:** 创建批量导入脚本：

```python
import os
import glob
from ai_tender_system.knowledge_base.rag_engine import get_rag_engine

engine = get_rag_engine()
pdf_files = glob.glob("/path/to/docs/**/*.pdf", recursive=True)

for pdf in pdf_files:
    result = engine.add_document(
        file_path=pdf,
        metadata={"company_id": 8}
    )
    print(f"✅ {pdf}: {result['chunks_count']} chunks")
```

---

## 🎉 完成检查清单

- [ ] 依赖已安装（`pip install -r requirements_rag.txt`）
- [ ] 服务已启动并运行在8110端口
- [ ] RAG状态API返回 `available: true`
- [ ] 知识库页面可以看到"AI智能检索"按钮（⭐图标）
- [ ] 上传文档后显示"正在建立智能索引"提示
- [ ] 可以执行智能检索并看到结果
- [ ] 检索结果显示相关度分数和高亮关键词

---

## 📞 技术支持

如遇到问题，请检查：

1. **日志文件**: `ai_tender_system/data/logs/web_app.log`
2. **浏览器控制台**: 按F12查看JavaScript错误
3. **API响应**: 使用Postman测试API接口

**联系方式**: [根据实际情况填写]

---

## 🔄 后续升级路径

### 阶段1: 基础功能（当前）
- ✅ 文档向量化
- ✅ 智能检索

### 阶段2: 增强功能
- [ ] 添加大模型生成式问答
- [ ] 支持多轮对话
- [ ] 添加检索结果重排序

### 阶段3: 高级功能
- [ ] 迁移到云端向量数据库（性能更好）
- [ ] 添加文档去重
- [ ] 支持图片OCR
- [ ] 实现语义缓存

---

**版本**: v1.0
**更新日期**: 2025-09-30
**作者**: Claude Code Assistant