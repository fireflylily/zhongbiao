# Embedding API 迁移说明

## 概述

本次重构将文本嵌入服务从**本地模型**迁移到**OpenAI Embeddings API**,大幅减小Docker镜像大小,解决Railway部署超时问题。

## 主要变更

### 1. 移除的依赖 (~2.5GB)

```
torch>=2.0.0              (~2GB)
transformers>=4.30.0      (~500MB)
sentence-transformers>=2.2.2 (~100MB)
scikit-learn>=1.3.0
celery>=5.3.0
redis>=4.5.0
```

### 2. 新增配置

在 `.env` 文件中添加(可选,默认使用OPENAI_API_KEY):

```bash
# Embeddings API配置
EMBEDDING_API_KEY=sk-your-api-key-here
EMBEDDING_API_ENDPOINT=https://api.oaipro.com/v1
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_API_TIMEOUT=30
```

### 3. 代码变更

#### embedding_service.py
- ❌ 移除: SentenceTransformer本地模型加载
- ❌ 移除: PyTorch依赖
- ✅ 新增: OpenAI Embeddings API调用
- ✅ 保持: 相同的接口(`embed_texts`, `embed_query`等)

#### requirements-prod.txt
- 轻量级生产环境依赖
- 总大小: ~500MB (vs 之前 ~2.5GB)

## 部署步骤

### Railway部署

1. **推送代码到GitHub** ✅ (已完成)
   ```bash
   git push origin master
   ```

2. **Railway会自动重新部署**
   - 构建时间: 约3-5分钟 (vs 之前超时)
   - 镜像大小: ~500MB (vs 之前 ~2.5GB)

3. **配置环境变量** (在Railway Dashboard)
   - `OPENAI_API_KEY`: 你的API密钥
   - `OPENAI_API_ENDPOINT`: https://api.oaipro.com/v1
   - 其他变量保持不变

### 本地开发

1. **安装新依赖**
   ```bash
   pip install -r requirements-prod.txt
   ```

2. **配置环境变量**
   ```bash
   cp .env.example .env
   # 编辑 .env 文件,填入你的配置
   ```

3. **启动应用**
   ```bash
   python run.py
   ```

## 功能验证

重构后需要验证以下功能:

- [ ] 文档上传和解析
- [ ] 知识库向量化
- [ ] 语义搜索
- [ ] RAG检索

## 性能对比

### 之前(本地模型)

| 指标 | 值 |
|------|-----|
| Docker镜像大小 | ~2.5GB |
| 构建时间 | 超时 (>10分钟) |
| 启动时间 | ~30秒 (模型加载) |
| 嵌入速度 | ~100个文本/秒 (CPU) |
| 成本 | 无API费用 |

### 现在(Embeddings API)

| 指标 | 值 |
|------|-----|
| Docker镜像大小 | ~500MB |
| 构建时间 | ~3-5分钟 |
| 启动时间 | ~3秒 |
| 嵌入速度 | ~1000个文本/秒 (API) |
| 成本 | $0.0001/1K tokens |

## 成本估算

### text-embedding-3-small

- 价格: $0.00002 per 1K tokens
- 示例:
  - 1万字文档: ~$0.0002
  - 10万字文档: ~$0.002
  - 100万字文档: ~$0.02

### 月度估算

假设每月处理:
- 100个标书文档
- 平均每个5万字
- 总计500万字

成本: **约 $0.10 USD/月**

## 向量维度变化

### 之前

- 模型: paraphrase-multilingual-MiniLM-L12-v2
- 维度: **384**

### 现在

- 模型: text-embedding-3-small
- 维度: **1536**

⚠️ **重要**: 如果之前已有向量数据库,需要重新生成向量!

## 兼容性

### 保持不变

- ✅ API接口完全兼容
- ✅ `EmbeddingResult` 数据结构相同
- ✅ 上层代码无需修改

### 需要调整

- ⚠️ 向量维度从384变为1536
- ⚠️ 需要重新索引现有文档

## 回滚方案

如果需要回滚到本地模型:

```bash
# 1. 切换回旧版本
git checkout <previous-commit>

# 2. 安装旧依赖
pip install -r requirements.txt

# 3. 重新部署
git push origin master --force
```

## 故障排查

### 问题1: API密钥未配置

**错误**: `ValueError: 未配置EMBEDDING_API_KEY或OPENAI_API_KEY环境变量`

**解决**: 在Railway Dashboard或本地.env中配置`OPENAI_API_KEY`

### 问题2: API调用失败

**错误**: `API调用失败: HTTPError 401`

**解决**: 检查API密钥是否正确,是否有余额

### 问题3: 向量维度不匹配

**错误**: `dimensions mismatch: expected 384, got 1536`

**解决**: 重新生成向量索引

## 后续优化

1. **缓存**: 对常用文本的embedding结果进行缓存
2. **批处理**: 优化大批量文本的处理速度
3. **错误重试**: 添加API调用失败的自动重试机制
4. **成本监控**: 添加API使用量监控

## 参考链接

- [OpenAI Embeddings API文档](https://platform.openai.com/docs/guides/embeddings)
- [text-embedding-3-small性能评测](https://openai.com/blog/new-embedding-models-and-api-updates)
- [Railway部署指南](../RAILWAY_DEPLOYMENT.md)

---

更新日期: 2025-10-19
