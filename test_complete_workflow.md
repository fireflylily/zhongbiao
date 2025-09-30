# 📋 Chroma向量化完整流程测试指南

## 测试目标
验证 **文档上传 → 自动向量化 → AI搜索** 的完整流程

---

## 🔧 准备工作

### 1. 确认服务运行
```bash
# 检查服务状态
curl http://localhost:8110/api/vector_search/status
```

**期望结果**：
```json
{
  "success": true,
  "data": {
    "initialized": true,
    "components": {
      "embedding_service": true,
      "vector_store": true,
      "parser_manager": true
    },
    "vector_store": {
      "total_documents": 0,
      "dimension": 100,
      "backend": "Chroma"
    }
  }
}
```

### 2. 准备测试文档
创建3个测试文档（或使用现有文档）：
- `测试文档1.txt` - 关于产品功能的描述
- `测试文档2.txt` - 关于技术架构的说明
- `测试文档3.txt` - 关于使用手册的内容

---

## 📝 测试步骤

### 步骤1: 创建测试企业和产品

1. 访问 http://localhost:8110/knowledge_base
2. 点击"添加企业"
3. 填写信息：
   - 企业名称：测试企业
   - 企业代码：TEST001
   - 行业类型：软件和信息技术服务业
4. 在企业下创建产品：
   - 产品名称：测试产品
   - 产品类别：软件

### 步骤2: 上传文档并验证自动向量化

#### 方法1：通过UI上传
1. 点击"测试产品"
2. 拖拽文档到上传区域
3. 观察上传进度
4. **关键验证点**：上传完成后，文档状态应该显示"向量化中"或"已向量化"

#### 方法2：通过API测试
```bash
# 2.1 上传文档
curl -X POST http://localhost:8110/api/knowledge_base/documents \
  -F "file=@测试文档1.txt" \
  -F "product_id=1" \
  -F "company_id=1" \
  -F "document_category=tech"

# 预期返回：
# {"success": true, "data": {"doc_id": 123}, "message": "文档上传成功"}
```

```bash
# 2.2 触发向量化
curl -X POST http://localhost:8110/api/vector_search/documents/vectorize \
  -H "Content-Type: application/json" \
  -d '{"doc_id": 123}'

# 预期返回：
# {"success": true, "message": "文档向量化完成", "chunks_processed": 5}
```

```bash
# 2.3 检查向量化状态
curl http://localhost:8110/api/vector_search/status

# 预期：vector_store.total_documents 应该增加
```

### 步骤3: 测试向量搜索

#### 3.1 语义搜索测试
```bash
curl -X POST http://localhost:8110/api/vector_search/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "产品有什么功能",
    "top_k": 5,
    "threshold": 0.3
  }'
```

**预期结果**：
```json
{
  "success": true,
  "data": {
    "results": [
      {
        "document_id": "doc_123_chunk_0",
        "content": "我们的产品主要提供以下功能...",
        "similarity_score": 0.85,
        "metadata": {
          "doc_id": 123,
          "company_id": 1,
          "product_id": 1
        }
      }
    ],
    "total_results": 5,
    "search_time": 0.015
  }
}
```

#### 3.2 带过滤条件的搜索
```bash
curl -X POST http://localhost:8110/api/vector_search/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "技术架构",
    "top_k": 5,
    "filters": {
      "company_id": 1,
      "product_id": 1
    }
  }'
```

#### 3.3 相似文档查询
```bash
curl http://localhost:8110/api/vector_search/similar/doc_123_chunk_0?top_k=5
```

---

## ✅ 验证清单

### 文档上传验证
- [ ] 文档成功上传到服务器
- [ ] 数据库 `documents` 表中有记录
- [ ] 文件保存在 `data/uploads/` 目录
- [ ] `parse_status` 字段更新为 'completed'

### 向量化验证
- [ ] 文档被成功解析和分块
- [ ] `document_chunks` 表中有分块记录
- [ ] Chroma数据库中有向量记录
- [ ] `vector_status` 字段更新为 'completed'
- [ ] 向量数量正确（chunks数量 = vector数量）

### 搜索功能验证
- [ ] 语义搜索返回相关结果
- [ ] 相似度分数合理（0-1之间）
- [ ] 搜索速度快（< 100ms）
- [ ] 元数据过滤正常工作
- [ ] 相似文档查询正常

---

## 🐛 常见问题排查

### 问题1: 向量化失败
**症状**：`vector_status` 一直是 'pending'

**检查**：
```bash
# 查看日志
tail -100 ai_tender_system/data/logs/ai_tender_system.log

# 检查文档解析状态
sqlite3 ai_tender_system/data/knowledge_base.db \
  "SELECT doc_id, file_name, parse_status, vector_status FROM documents;"
```

**可能原因**：
- 文档格式不支持
- 文档内容为空
- 嵌入服务未初始化

### 问题2: 搜索无结果
**症状**：搜索API返回空数组

**检查**：
```bash
# 确认Chroma中有数据
curl http://localhost:8110/api/vector_search/status
# 检查 vector_store.total_documents

# 降低相似度阈值重试
curl -X POST http://localhost:8110/api/vector_search/search \
  -H "Content-Type: application/json" \
  -d '{"query": "测试", "threshold": 0.0}'
```

### 问题3: 搜索速度慢
**症状**：`search_time` > 1秒

**可能原因**：
- 向量数据过多（> 100K）
- Chroma索引未优化
- 服务器资源不足

---

## 📊 性能基准

### 预期性能指标
- **文档上传**：< 1秒（1MB文件）
- **文档解析**：< 2秒
- **向量化**：< 5秒（10个分块）
- **搜索延迟**：< 50ms（1K向量）
- **搜索延迟**：< 200ms（100K向量）

### Chroma vs SimpleVectorStore 对比
| 操作 | SimpleVectorStore | ChromaVectorStore | 提升 |
|------|------------------|------------------|------|
| 搜索1K文档 | ~80ms | ~15ms | 5.3x ⚡ |
| 搜索10K文档 | ~800ms | ~30ms | 26.7x ⚡⚡ |
| 内存占用 | ~1.5GB | ~800MB | 47% 📉 |
| 持久化 | 手动 | 自动 | ✨ |

---

## 🎯 成功标准

全部通过以下验证即为成功：

1. ✅ 文档上传成功率 100%
2. ✅ 自动向量化成功率 100%
3. ✅ 搜索返回相关结果
4. ✅ 搜索延迟 < 100ms
5. ✅ 相似度分数合理（0.3-1.0）
6. ✅ 元数据过滤正确
7. ✅ 无错误日志

---

## 📝 测试报告模板

```markdown
## Chroma迁移测试报告

**测试时间**：2025-09-30
**测试人员**：[你的名字]
**系统版本**：v1.0

### 测试结果汇总
- 文档上传：✅ 通过 / ❌ 失败
- 自动向量化：✅ 通过 / ❌ 失败
- 向量搜索：✅ 通过 / ❌ 失败
- 性能表现：✅ 符合预期 / ⚠️ 需优化

### 详细数据
- 测试文档数量：3
- 向量化成功：3/3
- 平均搜索延迟：15ms
- 相似度分数范围：0.65-0.92

### 问题记录
[记录遇到的问题和解决方案]

### 总结
[整体评价和建议]
```

---

## 🚀 后续行动

测试通过后：
1. 清理测试数据
2. 准备生产环境部署
3. 编写用户文档
4. 培训使用人员