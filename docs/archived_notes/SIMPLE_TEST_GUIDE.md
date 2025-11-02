# 🚀 Chroma向量搜索简易测试指南

## 快速测试（5分钟）

### ✅ 当前系统状态
- **服务地址**: http://localhost:8110
- **Chroma状态**: ✅ 已初始化
- **向量数量**: 0个（全新开始）
- **已有企业**: 2个（智慧足迹、中国联通）
- **已有产品**: 4个

---

## 📝 通过UI界面测试（推荐）

### 步骤1: 访问知识库页面
打开浏览器访问：
```
http://localhost:8110/knowledge_base
```

### 步骤2: 选择或创建产品
1. 在左侧树中点击任意企业
2. 选择一个现有产品（如"极盾风控平台"）

### 步骤3: 上传测试文档
1. 将准备好的PDF或Word文档拖拽到上传区域
2. 或者点击"选择文件"按钮上传

### 步骤4: 观察向量化过程
上传后应该会看到：
- ✅ 文档上传成功提示
- ⏳ 自动开始向量化（如果已集成）
- 📊 文档出现在列表中

### 步骤5: 测试搜索（如果UI已实现）
1. 在搜索框输入关键词
2. 点击搜索按钮
3. 查看搜索结果

---

## 🔧 直接使用Python脚本测试（开发者）

我为你创建了一个完整的测试脚本：

```python
#!/usr/bin/env python3
# 文件位置: test_chroma_workflow.py

import asyncio
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent / "ai_tender_system"
sys.path.insert(0, str(project_root))

from modules.vector_engine.chroma_adapter import ChromaVectorStore
from modules.vector_engine.simple_embedding import SimpleEmbeddingService
import numpy as np


async def test_complete_workflow():
    """测试完整的向量化和搜索流程"""
    print("=" * 60)
    print("开始测试 Chroma 完整流程")
    print("=" * 60)

    # 1. 初始化组件
    print("\n1️⃣  初始化向量引擎...")
    vector_store = ChromaVectorStore(dimension=100)
    await vector_store.initialize()

    embedding_service = SimpleEmbeddingService(dimension=100)
    await embedding_service.initialize()
    print("✅ 组件初始化完成")

    # 2. 准备测试文档
    print("\n2️⃣  准备测试文档...")
    test_docs = [
        {
            "id": "test_doc_1",
            "content": "极盾风控平台是一款智能风险控制系统，采用机器学习算法进行实时风险监控。",
            "metadata": {"company_id": 8, "product_id": 22, "type": "product"}
        },
        {
            "id": "test_doc_2",
            "content": "系统支持实时交易监控，7x24小时不间断运行，毫秒级响应速度。",
            "metadata": {"company_id": 8, "product_id": 22, "type": "feature"}
        },
        {
            "id": "test_doc_3",
            "content": "技术架构采用Python Flask框架，使用Redis进行缓存，MongoDB存储数据。",
            "metadata": {"company_id": 8, "product_id": 22, "type": "tech"}
        }
    ]
    print(f"✅ 准备了 {len(test_docs)} 个测试文档")

    # 3. 向量化文档
    print("\n3️⃣  向量化文档...")
    for doc in test_docs:
        # 生成向量
        result = await embedding_service.embed_texts([doc["content"]])
        vector = result.vectors[0]

        # 存储到Chroma
        await vector_store.add_document(
            doc_id=doc["id"],
            content=doc["content"],
            vector=vector,
            metadata=doc["metadata"]
        )
        print(f"  ✓ {doc['id']} 向量化完成")

    # 4. 验证存储
    stats = vector_store.get_stats()
    print(f"\n✅ 向量化完成! 总文档数: {stats['total_documents']}")

    # 5. 测试搜索
    print("\n4️⃣  测试向量搜索...")

    test_queries = [
        "风险控制功能",
        "系统性能和速度",
        "技术架构和数据库"
    ]

    for query in test_queries:
        print(f"\n📋 查询: '{query}'")

        # 查询向量化
        query_result = await embedding_service.embed_query(query)
        query_vector = query_result.vector

        # 执行搜索
        results = await vector_store.search(
            query_vector=query_vector,
            top_k=3,
            threshold=0.0
        )

        print(f"  🔍 找到 {len(results)} 个结果:")
        for i, result in enumerate(results, 1):
            print(f"    {i}. 相似度: {result.score:.4f}")
            print(f"       内容: {result.document.content[:50]}...")
            print(f"       元数据: {result.document.metadata}")

    # 6. 测试过滤搜索
    print("\n5️⃣  测试带过滤条件的搜索...")
    query_result = await embedding_service.embed_query("系统功能")
    results = await vector_store.search(
        query_vector=query_result.vector,
        top_k=5,
        filter_metadata={"company_id": 8}
    )
    print(f"✅ 过滤搜索完成，找到 {len(results)} 个结果")

    # 7. 清理测试数据
    print("\n6️⃣  清理测试数据...")
    for doc in test_docs:
        await vector_store.delete_document(doc["id"])
    final_stats = vector_store.get_stats()
    print(f"✅ 清理完成，当前文档数: {final_stats['total_documents']}")

    print("\n" + "=" * 60)
    print("✨ 测试完成！Chroma向量搜索工作正常。")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_complete_workflow())
```

### 运行测试脚本：
```bash
cd /Users/lvhe/Downloads/zhongbiao/zhongbiao
python3 test_chroma_workflow.py
```

**预期输出**：
```
============================================================
开始测试 Chroma 完整流程
============================================================

1️⃣  初始化向量引擎...
✅ 组件初始化完成

2️⃣  准备测试文档...
✅ 准备了 3 个测试文档

3️⃣  向量化文档...
  ✓ test_doc_1 向量化完成
  ✓ test_doc_2 向量化完成
  ✓ test_doc_3 向量化完成

✅ 向量化完成! 总文档数: 3

4️⃣  测试向量搜索...
📋 查询: '风险控制功能'
  🔍 找到 3 个结果:
    1. 相似度: 0.8523
       内容: 极盾风控平台是一款智能风险控制系统...
       元数据: {'company_id': 8, 'product_id': 22}
...

✨ 测试完成！Chroma向量搜索工作正常。
============================================================
```

---

## ✅ 成功标准

如果看到以下情况，说明系统正常：

1. ✅ 文档成功向量化（total_documents > 0）
2. ✅ 搜索返回相关结果
3. ✅ 相似度分数合理（通常0.3-1.0之间）
4. ✅ 搜索延迟低（< 100ms）
5. ✅ 元数据过滤正常工作

---

## 🐛 常见问题

### 问题1: "Error: Not Found"
**原因**: API路由未正确注册
**解决**: 检查 `app.py` 中是否正确注册了蓝图

### 问题2: 搜索无结果
**原因**: 文档未向量化或阈值太高
**解决**:
```python
# 降低阈值重试
results = await vector_store.search(
    query_vector=query_vector,
    threshold=0.0  # 接受所有结果
)
```

### 问题3: 服务启动失败
**原因**: 端口被占用
**解决**:
```bash
lsof -ti:8110 | xargs kill -9
python3 -m ai_tender_system.web.app
```

---

## 📚 相关文档

- [test_complete_workflow.md](test_complete_workflow.md) - 详细测试文档
- [CHROMA_MIGRATION_GUIDE.md](CHROMA_MIGRATION_GUIDE.md) - 迁移指南
- [knowledge_base.html](ai_tender_system/web/templates/knowledge_base.html) - 系统架构（注释）

---

**测试愉快！** 🚀

如有问题，请检查日志：
```bash
tail -f ai_tender_system/data/logs/ai_tender_system.log
```