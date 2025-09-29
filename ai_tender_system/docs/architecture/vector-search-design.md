# 向量搜索设计方案

## 🎯 概述

本文档详细描述了AI标书系统的向量搜索引擎设计，基于FAISS（Facebook AI Similarity Search）实现高性能的语义搜索功能。

## 🏗️ 系统架构

### 整体设计
```
向量搜索引擎
├── 文档处理层
│   ├── 文档分块 (Chunking)
│   ├── 文本提取 (Text Extraction)
│   └── 内容清洗 (Content Cleaning)
├── 向量化层
│   ├── 模型加载 (Model Loading)
│   ├── 文本编码 (Text Encoding)
│   └── 向量标准化 (Vector Normalization)
├── 索引管理层
│   ├── FAISS索引 (Index Management)
│   ├── 向量存储 (Vector Storage)
│   └── 元数据映射 (Metadata Mapping)
└── 搜索服务层
    ├── 查询处理 (Query Processing)
    ├── 相似度计算 (Similarity Calculation)
    ├── 结果排序 (Result Ranking)
    └── 混合搜索 (Hybrid Search)
```

## 🔧 核心组件设计

### 1. 文档处理模块

#### 文档分块策略
```python
class DocumentChunker:
    def __init__(self):
        self.chunk_size = 512          # 每块最大字符数
        self.chunk_overlap = 50        # 块间重叠字符数
        self.min_chunk_size = 100      # 最小块大小

    def chunk_document(self, content: str, doc_type: str) -> List[Chunk]:
        """
        智能文档分块，根据文档类型使用不同策略
        """
        if doc_type == 'structured':
            return self._chunk_by_structure(content)
        elif doc_type == 'technical':
            return self._chunk_by_semantics(content)
        else:
            return self._chunk_by_sliding_window(content)

    def _chunk_by_structure(self, content: str) -> List[Chunk]:
        """基于文档结构分块（标题、段落等）"""
        pass

    def _chunk_by_semantics(self, content: str) -> List[Chunk]:
        """基于语义边界分块"""
        pass

    def _chunk_by_sliding_window(self, content: str) -> List[Chunk]:
        """滑动窗口分块"""
        pass
```

#### 内容预处理
```python
class ContentPreprocessor:
    def __init__(self):
        self.stopwords = set(['的', '了', '在', '是', '有', '和'])

    def preprocess(self, text: str) -> str:
        """
        文本预处理流水线
        """
        # 1. 清理特殊字符
        text = self._clean_special_chars(text)

        # 2. 标准化空白字符
        text = self._normalize_whitespace(text)

        # 3. 处理数字和日期
        text = self._normalize_numbers_dates(text)

        # 4. 移除过短文本
        if len(text.strip()) < 10:
            return ""

        return text
```

### 2. 向量化模块

#### 模型配置
```python
EMBEDDING_CONFIG = {
    'model_name': 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2',
    'model_path': 'models/embedding_model/',
    'dimension': 384,
    'max_seq_length': 512,
    'device': 'cpu',  # 或 'cuda' 如果有GPU
    'batch_size': 32,
    'normalize_embeddings': True
}
```

#### 向量编码器
```python
class VectorEncoder:
    def __init__(self, config: dict):
        self.model = SentenceTransformer(config['model_name'])
        self.dimension = config['dimension']
        self.batch_size = config['batch_size']
        self.device = config['device']

    def encode_texts(self, texts: List[str]) -> np.ndarray:
        """
        批量文本向量化
        """
        # 分批处理避免内存溢出
        all_embeddings = []
        for i in range(0, len(texts), self.batch_size):
            batch_texts = texts[i:i + self.batch_size]
            batch_embeddings = self.model.encode(
                batch_texts,
                device=self.device,
                normalize_embeddings=True,
                show_progress_bar=True
            )
            all_embeddings.append(batch_embeddings)

        return np.vstack(all_embeddings)

    def encode_single(self, text: str) -> np.ndarray:
        """
        单文本向量化（用于搜索查询）
        """
        return self.model.encode([text], normalize_embeddings=True)[0]
```

### 3. FAISS索引管理

#### 索引类型选择
```python
class IndexManager:
    def __init__(self, dimension: int):
        self.dimension = dimension
        self.index_configs = {
            'flat': self._create_flat_index,      # 精确搜索，小数据集
            'ivf': self._create_ivf_index,        # 近似搜索，中等数据集
            'hnsw': self._create_hnsw_index,      # 高性能搜索，大数据集
            'pq': self._create_pq_index           # 压缩存储，内存限制
        }

    def create_index(self, index_type: str, data_size: int) -> faiss.Index:
        """
        根据数据规模选择合适的索引类型
        """
        if data_size < 10000:
            return self._create_flat_index()
        elif data_size < 100000:
            return self._create_ivf_index()
        else:
            return self._create_hnsw_index()

    def _create_flat_index(self) -> faiss.Index:
        """创建精确搜索索引"""
        return faiss.IndexFlatIP(self.dimension)

    def _create_ivf_index(self, nlist: int = 100) -> faiss.Index:
        """创建IVF索引（倒排文件索引）"""
        quantizer = faiss.IndexFlatIP(self.dimension)
        index = faiss.IndexIVFFlat(quantizer, self.dimension, nlist)
        return index

    def _create_hnsw_index(self, M: int = 32) -> faiss.Index:
        """创建HNSW索引（层次导航小世界）"""
        index = faiss.IndexHNSWFlat(self.dimension, M)
        index.hnsw.efConstruction = 200
        index.hnsw.efSearch = 100
        return index
```

#### 索引操作
```python
class VectorIndex:
    def __init__(self, index_path: str, dimension: int):
        self.index_path = index_path
        self.dimension = dimension
        self.index = None
        self.id_mapping = {}  # FAISS ID -> 数据库ID映射

    def build_index(self, vectors: np.ndarray, doc_ids: List[int]):
        """
        构建向量索引
        """
        # 创建索引
        self.index = faiss.IndexFlatIP(self.dimension)

        # 添加向量
        self.index.add(vectors.astype('float32'))

        # 建立ID映射
        for i, doc_id in enumerate(doc_ids):
            self.id_mapping[i] = doc_id

        # 保存索引
        self.save_index()

    def add_vectors(self, vectors: np.ndarray, doc_ids: List[int]):
        """
        增量添加向量
        """
        if self.index is None:
            self.load_index()

        start_idx = self.index.ntotal
        self.index.add(vectors.astype('float32'))

        # 更新ID映射
        for i, doc_id in enumerate(doc_ids):
            self.id_mapping[start_idx + i] = doc_id

        self.save_index()

    def search(self, query_vector: np.ndarray, k: int = 10) -> Tuple[List[float], List[int]]:
        """
        向量搜索
        """
        if self.index is None:
            self.load_index()

        # 执行搜索
        scores, faiss_ids = self.index.search(
            query_vector.reshape(1, -1).astype('float32'), k
        )

        # 转换为数据库ID
        doc_ids = [self.id_mapping.get(fid, -1) for fid in faiss_ids[0]]

        return scores[0].tolist(), doc_ids

    def save_index(self):
        """保存索引到磁盘"""
        faiss.write_index(self.index, self.index_path)

        # 保存ID映射
        mapping_path = self.index_path.replace('.index', '_mapping.json')
        with open(mapping_path, 'w', encoding='utf-8') as f:
            json.dump(self.id_mapping, f, ensure_ascii=False, indent=2)

    def load_index(self):
        """从磁盘加载索引"""
        if os.path.exists(self.index_path):
            self.index = faiss.read_index(self.index_path)

            # 加载ID映射
            mapping_path = self.index_path.replace('.index', '_mapping.json')
            if os.path.exists(mapping_path):
                with open(mapping_path, 'r', encoding='utf-8') as f:
                    self.id_mapping = {int(k): v for k, v in json.load(f).items()}
```

### 4. 搜索服务模块

#### 混合搜索引擎
```python
class HybridSearchEngine:
    def __init__(self, vector_index: VectorIndex, db_connection):
        self.vector_index = vector_index
        self.db = db_connection
        self.encoder = VectorEncoder(EMBEDDING_CONFIG)

    def search(self, query: str, filters: dict = None, k: int = 10) -> List[SearchResult]:
        """
        混合搜索：向量搜索 + 关键词搜索
        """
        # 1. 向量搜索
        vector_results = self._vector_search(query, k * 2)

        # 2. 关键词搜索
        keyword_results = self._keyword_search(query, filters, k * 2)

        # 3. 结果融合
        merged_results = self._merge_results(vector_results, keyword_results)

        # 4. 重新排序
        final_results = self._rerank_results(merged_results, query)

        return final_results[:k]

    def _vector_search(self, query: str, k: int) -> List[VectorSearchResult]:
        """向量语义搜索"""
        # 向量化查询
        query_vector = self.encoder.encode_single(query)

        # 搜索最相似向量
        scores, doc_ids = self.vector_index.search(query_vector, k)

        # 构建结果
        results = []
        for score, doc_id in zip(scores, doc_ids):
            if doc_id != -1:  # 有效ID
                results.append(VectorSearchResult(
                    doc_id=doc_id,
                    similarity_score=float(score),
                    search_type='vector'
                ))

        return results

    def _keyword_search(self, query: str, filters: dict, k: int) -> List[KeywordSearchResult]:
        """关键词搜索"""
        # 构建SQL查询
        sql = """
        SELECT d.id, d.title, d.category, d.description,
               GROUP_CONCAT(c.content, ' ') as content
        FROM product_documents d
        LEFT JOIN document_chunks c ON d.id = c.document_id
        WHERE d.status = 'active'
        """

        params = []

        # 添加关键词条件
        if query.strip():
            keywords = query.split()
            keyword_conditions = []
            for keyword in keywords:
                keyword_conditions.append(
                    "(d.title LIKE ? OR d.description LIKE ? OR c.content LIKE ?)"
                )
                params.extend([f'%{keyword}%'] * 3)

            if keyword_conditions:
                sql += " AND (" + " OR ".join(keyword_conditions) + ")"

        # 添加过滤条件
        if filters:
            if 'category' in filters:
                sql += " AND d.category = ?"
                params.append(filters['category'])
            if 'security_level' in filters:
                sql += " AND d.security_level = ?"
                params.append(filters['security_level'])

        sql += " GROUP BY d.id ORDER BY d.upload_time DESC LIMIT ?"
        params.append(k)

        # 执行查询
        cursor = self.db.execute(sql, params)
        results = []
        for row in cursor.fetchall():
            results.append(KeywordSearchResult(
                doc_id=row[0],
                title=row[1],
                category=row[2],
                description=row[3],
                content=row[4],
                search_type='keyword'
            ))

        return results

    def _merge_results(self, vector_results: List, keyword_results: List) -> List[SearchResult]:
        """结果融合算法"""
        # 使用加权融合
        vector_weight = 0.7
        keyword_weight = 0.3

        merged = {}

        # 处理向量搜索结果
        for i, result in enumerate(vector_results):
            doc_id = result.doc_id
            # 计算位置权重（排名越前权重越高）
            position_weight = 1.0 / (i + 1)
            score = result.similarity_score * vector_weight * position_weight

            merged[doc_id] = SearchResult(
                doc_id=doc_id,
                vector_score=result.similarity_score,
                keyword_score=0.0,
                final_score=score,
                search_types=['vector']
            )

        # 处理关键词搜索结果
        for i, result in enumerate(keyword_results):
            doc_id = result.doc_id
            position_weight = 1.0 / (i + 1)
            keyword_score = position_weight  # 关键词匹配得分
            score = keyword_score * keyword_weight

            if doc_id in merged:
                # 更新现有结果
                merged[doc_id].keyword_score = keyword_score
                merged[doc_id].final_score += score
                merged[doc_id].search_types.append('keyword')
            else:
                # 新增结果
                merged[doc_id] = SearchResult(
                    doc_id=doc_id,
                    vector_score=0.0,
                    keyword_score=keyword_score,
                    final_score=score,
                    search_types=['keyword']
                )

        return list(merged.values())

    def _rerank_results(self, results: List[SearchResult], query: str) -> List[SearchResult]:
        """结果重排序"""
        # 根据最终得分排序
        results.sort(key=lambda x: x.final_score, reverse=True)

        # 可以添加更复杂的重排序逻辑，比如：
        # 1. 考虑文档新鲜度
        # 2. 考虑文档质量评分
        # 3. 考虑用户历史偏好

        return results
```

### 5. 查询优化模块

#### 查询扩展
```python
class QueryExpansion:
    def __init__(self):
        self.synonyms = self._load_synonyms()

    def expand_query(self, query: str) -> str:
        """
        查询扩展：添加同义词、相关词
        """
        words = query.split()
        expanded_words = set(words)

        for word in words:
            # 添加同义词
            if word in self.synonyms:
                expanded_words.update(self.synonyms[word])

        return ' '.join(expanded_words)

    def _load_synonyms(self) -> dict:
        """加载同义词词典"""
        # 可以从文件或数据库加载
        return {
            '软件': ['系统', '程序', '应用'],
            '硬件': ['设备', '机器', '装置'],
            '服务': ['支持', '维护', '保障']
        }
```

#### 查询意图识别
```python
class QueryIntentClassifier:
    def __init__(self):
        self.intent_patterns = {
            'technical': ['技术', '规格', '参数', '配置'],
            'implementation': ['实施', '部署', '安装', '配置'],
            'service': ['服务', '支持', '维护', '培训'],
            'case': ['案例', '经验', '客户', '项目']
        }

    def classify_intent(self, query: str) -> str:
        """
        识别查询意图，优化搜索策略
        """
        for intent, keywords in self.intent_patterns.items():
            if any(keyword in query for keyword in keywords):
                return intent
        return 'general'
```

## 📊 性能优化策略

### 1. 索引优化
```python
# 索引配置优化
OPTIMIZATION_CONFIG = {
    'index_training_size': 50000,      # 训练样本数量
    'nlist': 1024,                     # 聚类中心数量（√n）
    'nprobe': 32,                      # 搜索时探索的聚类数
    'efConstruction': 200,             # HNSW构建参数
    'efSearch': 100,                   # HNSW搜索参数
    'use_gpu': False,                  # 是否使用GPU加速
    'omp_num_threads': 4              # OpenMP线程数
}
```

### 2. 缓存策略
```python
class SearchCache:
    def __init__(self, cache_size: int = 1000):
        self.cache = LRUCache(cache_size)
        self.hit_count = 0
        self.miss_count = 0

    def get(self, query_hash: str) -> Optional[List[SearchResult]]:
        """获取缓存结果"""
        result = self.cache.get(query_hash)
        if result:
            self.hit_count += 1
        else:
            self.miss_count += 1
        return result

    def put(self, query_hash: str, results: List[SearchResult]):
        """缓存搜索结果"""
        self.cache.put(query_hash, results)

    def get_hit_ratio(self) -> float:
        """获取缓存命中率"""
        total = self.hit_count + self.miss_count
        return self.hit_count / total if total > 0 else 0.0
```

### 3. 批量处理
```python
class BatchProcessor:
    def __init__(self, batch_size: int = 100):
        self.batch_size = batch_size

    def process_documents_batch(self, documents: List[Document]):
        """批量处理文档"""
        for i in range(0, len(documents), self.batch_size):
            batch = documents[i:i + self.batch_size]
            self._process_batch(batch)

    def _process_batch(self, batch: List[Document]):
        """处理单个批次"""
        # 1. 批量分块
        all_chunks = []
        for doc in batch:
            chunks = self.chunker.chunk_document(doc.content, doc.type)
            all_chunks.extend(chunks)

        # 2. 批量向量化
        texts = [chunk.content for chunk in all_chunks]
        vectors = self.encoder.encode_texts(texts)

        # 3. 批量索引
        self.index.add_vectors(vectors, [chunk.doc_id for chunk in all_chunks])
```

## 🔍 搜索API设计

### RESTful API接口
```python
from flask import Flask, request, jsonify

app = Flask(__name__)
search_engine = HybridSearchEngine()

@app.route('/api/search', methods=['POST'])
def search_documents():
    """
    文档搜索API
    """
    data = request.get_json()

    # 参数验证
    query = data.get('query', '').strip()
    if not query:
        return jsonify({'error': '查询不能为空'}), 400

    k = min(data.get('k', 10), 100)  # 限制最大返回数量
    filters = data.get('filters', {})
    search_type = data.get('search_type', 'hybrid')  # vector, keyword, hybrid

    try:
        # 执行搜索
        results = search_engine.search(
            query=query,
            filters=filters,
            k=k,
            search_type=search_type
        )

        # 格式化返回结果
        response = {
            'query': query,
            'total': len(results),
            'results': [result.to_dict() for result in results],
            'search_time_ms': results.search_time_ms if hasattr(results, 'search_time_ms') else 0
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/search/suggest', methods=['GET'])
def search_suggestions():
    """
    搜索建议API
    """
    query = request.args.get('q', '').strip()
    if len(query) < 2:
        return jsonify({'suggestions': []})

    # 基于历史搜索和文档标题生成建议
    suggestions = search_engine.get_suggestions(query, limit=10)

    return jsonify({'suggestions': suggestions})
```

## 📈 监控和分析

### 性能监控
```python
class SearchMetrics:
    def __init__(self):
        self.query_count = 0
        self.total_response_time = 0.0
        self.slow_queries = []

    def record_search(self, query: str, response_time_ms: float, result_count: int):
        """记录搜索指标"""
        self.query_count += 1
        self.total_response_time += response_time_ms

        # 记录慢查询
        if response_time_ms > 1000:  # 超过1秒
            self.slow_queries.append({
                'query': query,
                'response_time_ms': response_time_ms,
                'result_count': result_count,
                'timestamp': datetime.now()
            })

    def get_average_response_time(self) -> float:
        """获取平均响应时间"""
        return self.total_response_time / self.query_count if self.query_count > 0 else 0.0
```

### 搜索分析
```python
class SearchAnalyzer:
    def __init__(self, db_connection):
        self.db = db_connection

    def analyze_search_patterns(self) -> dict:
        """分析搜索模式"""
        # 热门查询
        popular_queries = self.db.execute("""
            SELECT query_text, COUNT(*) as freq
            FROM search_logs
            WHERE search_time >= datetime('now', '-7 days')
            GROUP BY query_text
            ORDER BY freq DESC
            LIMIT 10
        """).fetchall()

        # 无结果查询
        zero_result_queries = self.db.execute("""
            SELECT query_text, COUNT(*) as freq
            FROM search_logs
            WHERE result_count = 0
            AND search_time >= datetime('now', '-7 days')
            GROUP BY query_text
            ORDER BY freq DESC
            LIMIT 10
        """).fetchall()

        return {
            'popular_queries': popular_queries,
            'zero_result_queries': zero_result_queries
        }
```

## 🚀 部署和运维

### 索引构建脚本
```bash
#!/bin/bash
# build_indexes.sh

echo "开始构建向量索引..."

# 1. 备份现有索引
if [ -f "data/vector_indexes/documents.index" ]; then
    cp data/vector_indexes/documents.index data/vector_indexes/backup/documents_$(date +%Y%m%d).index
fi

# 2. 构建新索引
python scripts/build_vector_index.py --input data/knowledge_base.db --output data/vector_indexes/

# 3. 验证索引
python scripts/verify_index.py --index_path data/vector_indexes/documents.index

echo "向量索引构建完成!"
```

### 健康检查
```python
class HealthChecker:
    def __init__(self, search_engine):
        self.search_engine = search_engine

    def check_health(self) -> dict:
        """系统健康检查"""
        health_status = {
            'overall': 'healthy',
            'components': {}
        }

        # 检查向量索引
        try:
            test_vector = np.random.random(384).astype('float32')
            self.search_engine.vector_index.search(test_vector, 1)
            health_status['components']['vector_index'] = 'healthy'
        except Exception as e:
            health_status['components']['vector_index'] = f'unhealthy: {str(e)}'
            health_status['overall'] = 'unhealthy'

        # 检查数据库连接
        try:
            self.search_engine.db.execute("SELECT 1").fetchone()
            health_status['components']['database'] = 'healthy'
        except Exception as e:
            health_status['components']['database'] = f'unhealthy: {str(e)}'
            health_status['overall'] = 'unhealthy'

        return health_status
```

---

**维护状态**: 🟢 积极维护中
**最后更新**: 2025年9月27日
**版本**: v1.0