"""
语义匹配引擎
基于词向量和语义相似度进行匹配（当前使用简化实现，后续可集成embedding模型）
"""

import re
import logging
import math
from typing import List, Dict, Any, Optional, Tuple, Set
from collections import Counter, defaultdict
try:
    from ..config import SEMANTIC_SIMILARITY_THRESHOLD
except ImportError:
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent))
    from config import SEMANTIC_SIMILARITY_THRESHOLD

class SemanticMatcher:
    """语义匹配引擎类"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # 语义相似词典（简化版，实际使用中可替换为词向量模型）
        self.semantic_dict = self._build_semantic_dict()
        
        # TF-IDF相关
        self.idf_cache = {}
        self.document_freq = defaultdict(int)
        self.total_docs = 0
        
        # 停用词
        self.stop_words = {
            '的', '了', '在', '是', '有', '和', '与', '或', '及', '等', '各', '个',
            '一', '二', '三', '四', '五', '六', '七', '八', '九', '十', '能够',
            '可以', '应该', '需要', '具有', '支持', '实现', '提供', '包括', '包含'
        }
    
    def _build_semantic_dict(self) -> Dict[str, List[str]]:
        """构建语义相似词典"""
        return {
            # 数据相关
            '数据': ['信息', '资料', '内容', '记录', 'data'],
            '存储': ['保存', '储存', '持久化', 'storage', 'store'],
            '查询': ['搜索', '检索', '查找', 'query', 'search'],
            '分析': ['解析', '处理', '计算', 'analysis', 'analyze'],
            
            # 系统相关
            '系统': ['平台', '软件', '应用', 'system', 'platform'],
            '架构': ['结构', '框架', '设计', 'architecture', 'framework'],
            '接口': ['api', '界面', '端口', 'interface'],
            '服务': ['功能', '模块', '组件', 'service', 'module'],
            
            # 网络相关
            '网络': ['通信', '连接', '传输', 'network', 'communication'],
            '协议': ['标准', '规范', 'protocol', 'standard'],
            '安全': ['保护', '防护', '加密', 'security', 'protection'],
            
            # 性能相关
            '性能': ['效率', '速度', '响应', 'performance', 'efficiency'],
            '并发': ['同时', '并行', '多线程', 'concurrent', 'parallel'],
            '吞吐量': ['处理量', '容量', 'throughput', 'capacity'],
            
            # 功能相关
            '管理': ['控制', '维护', '操作', 'management', 'control'],
            '配置': ['设置', '参数', '选项', 'configuration', 'setting'],
            '监控': ['监测', '观察', '跟踪', 'monitoring', 'tracking'],
            '报表': ['报告', '统计', '图表', 'report', 'chart'],
            
            # 技术相关
            '算法': ['方法', '技术', '策略', 'algorithm', 'method'],
            '模型': ['模式', '样式', '模板', 'model', 'pattern'],
            '集成': ['整合', '融合', '对接', 'integration', 'merge'],
            '部署': ['安装', '配置', '发布', 'deployment', 'install']
        }
    
    def semantic_match(self, 
                      requirements: List[Dict[str, Any]], 
                      features: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        语义匹配需求和功能
        
        Args:
            requirements: 需求列表
            features: 功能列表
            
        Returns:
            匹配结果列表
        """
        self.logger.info(f"开始语义匹配: {len(requirements)} 个需求 vs {len(features)} 个功能")
        
        # 构建文档语料库
        all_texts = []
        for req in requirements:
            all_texts.append(f"{req.get('title', '')} {req.get('content', '')}")
        for feature in features:
            all_texts.append(f"{feature.get('title', '')} {feature.get('description', '')}")
        
        # 计算IDF
        self._calculate_idf(all_texts)
        
        matches = []
        
        for req in requirements:
            req_matches = []
            req_vector = self._text_to_vector(f"{req.get('title', '')} {req.get('content', '')}")
            
            for feature in features:
                feature_vector = self._text_to_vector(f"{feature.get('title', '')} {feature.get('description', '')}")
                
                # 计算语义相似度
                similarity = self._cosine_similarity(req_vector, feature_vector)
                
                # 结合语义扩展
                semantic_similarity = self._calculate_semantic_similarity(req, feature)
                
                # 综合相似度
                combined_similarity = (similarity * 0.7 + semantic_similarity * 0.3)
                
                if combined_similarity >= 0.1:  # 最低阈值
                    req_matches.append({
                        'requirement_id': req['id'],
                        'feature_id': feature['id'],
                        'semantic_score': combined_similarity,
                        'similarity_details': {
                            'vector_similarity': similarity,
                            'semantic_similarity': semantic_similarity,
                            'confidence': self._assess_confidence(combined_similarity)
                        },
                        'match_type': self._determine_semantic_match_type(combined_similarity),
                        'requirement': req,
                        'feature': feature
                    })
            
            # 按相似度排序
            req_matches.sort(key=lambda x: x['semantic_score'], reverse=True)
            
            # 添加最佳匹配
            if req_matches:
                best_match = req_matches[0]
                best_match['is_best_match'] = True
                matches.extend(req_matches[:3])  # 只保留前3个匹配结果
            else:
                # 没有匹配的需求
                matches.append({
                    'requirement_id': req['id'],
                    'feature_id': None,
                    'semantic_score': 0.0,
                    'similarity_details': {'reason': '未找到语义匹配的功能'},
                    'match_type': 'no_semantic_match',
                    'requirement': req,
                    'feature': None,
                    'is_best_match': True
                })
        
        self.logger.info(f"语义匹配完成: 生成 {len(matches)} 个匹配结果")
        return matches
    
    def _calculate_idf(self, documents: List[str]):
        """计算IDF值"""
        self.total_docs = len(documents)
        word_doc_count = defaultdict(int)
        
        for doc in documents:
            words = set(self._extract_words(doc))
            for word in words:
                word_doc_count[word] += 1
        
        # 计算IDF
        for word, doc_count in word_doc_count.items():
            self.idf_cache[word] = math.log(self.total_docs / (doc_count + 1))
    
    def _text_to_vector(self, text: str) -> Dict[str, float]:
        """将文本转换为TF-IDF向量"""
        if not text:
            return {}
        
        words = self._extract_words(text)
        if not words:
            return {}
        
        # 计算TF
        word_count = Counter(words)
        total_words = len(words)
        
        vector = {}
        for word, count in word_count.items():
            tf = count / total_words
            idf = self.idf_cache.get(word, 0)
            vector[word] = tf * idf
        
        return vector
    
    def _cosine_similarity(self, vector1: Dict[str, float], vector2: Dict[str, float]) -> float:
        """计算两个向量的余弦相似度"""
        if not vector1 or not vector2:
            return 0.0
        
        # 计算点积
        dot_product = 0.0
        for word in set(vector1.keys()) & set(vector2.keys()):
            dot_product += vector1[word] * vector2[word]
        
        # 计算模长
        norm1 = math.sqrt(sum(val ** 2 for val in vector1.values()))
        norm2 = math.sqrt(sum(val ** 2 for val in vector2.values()))
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def _calculate_semantic_similarity(self, requirement: Dict[str, Any], feature: Dict[str, Any]) -> float:
        """计算语义相似度（基于语义词典）"""
        req_text = f"{requirement.get('title', '')} {requirement.get('content', '')}"
        feature_text = f"{feature.get('title', '')} {feature.get('description', '')}"
        
        req_words = set(self._extract_words(req_text))
        feature_words = set(self._extract_words(feature_text))
        
        # 直接匹配
        direct_matches = len(req_words & feature_words)
        
        # 语义匹配
        semantic_matches = 0
        for req_word in req_words:
            if req_word in self.semantic_dict:
                similar_words = set(self.semantic_dict[req_word])
                if similar_words & feature_words:
                    semantic_matches += 1
        
        # 反向语义匹配
        for feature_word in feature_words:
            if feature_word in self.semantic_dict:
                similar_words = set(self.semantic_dict[feature_word])
                if similar_words & req_words:
                    semantic_matches += 1
        
        total_unique_words = len(req_words | feature_words)
        if total_unique_words == 0:
            return 0.0
        
        # 语义相似度 = (直接匹配 + 语义匹配) / 总词数
        similarity = (direct_matches + semantic_matches * 0.7) / total_unique_words
        return min(similarity, 1.0)
    
    def _extract_words(self, text: str) -> List[str]:
        """提取词汇"""
        if not text:
            return []
        
        # 清理文本
        text = re.sub(r'[^\w\s\u4e00-\u9fff]', ' ', text.lower())
        words = text.split()
        
        # 过滤停用词和短词
        filtered_words = []
        for word in words:
            if (len(word) >= 2 and 
                word not in self.stop_words and 
                not word.isdigit()):
                filtered_words.append(word)
        
        return filtered_words
    
    def _determine_semantic_match_type(self, similarity: float) -> str:
        """确定语义匹配类型"""
        if similarity >= SEMANTIC_SIMILARITY_THRESHOLD:
            return 'high_semantic_match'
        elif similarity >= 0.5:
            return 'medium_semantic_match'
        elif similarity >= 0.3:
            return 'low_semantic_match'
        else:
            return 'weak_semantic_match'
    
    def _assess_confidence(self, similarity: float) -> str:
        """评估匹配置信度"""
        if similarity >= 0.8:
            return 'very_high'
        elif similarity >= 0.6:
            return 'high'
        elif similarity >= 0.4:
            return 'medium'
        elif similarity >= 0.2:
            return 'low'
        else:
            return 'very_low'
    
    def find_semantic_clusters(self, texts: List[str], min_cluster_size: int = 2) -> List[List[int]]:
        """
        基于语义相似度对文本进行聚类
        
        Args:
            texts: 文本列表
            min_cluster_size: 最小聚类大小
            
        Returns:
            聚类结果，每个聚类包含文本索引列表
        """
        n = len(texts)
        if n < min_cluster_size:
            return []
        
        # 计算相似度矩阵
        similarity_matrix = [[0.0] * n for _ in range(n)]
        
        for i in range(n):
            vector_i = self._text_to_vector(texts[i])
            for j in range(i + 1, n):
                vector_j = self._text_to_vector(texts[j])
                similarity = self._cosine_similarity(vector_i, vector_j)
                similarity_matrix[i][j] = similarity
                similarity_matrix[j][i] = similarity
        
        # 简单聚类算法
        clusters = []
        used = set()
        
        for i in range(n):
            if i in used:
                continue
            
            cluster = [i]
            used.add(i)
            
            for j in range(i + 1, n):
                if j in used:
                    continue
                
                # 计算与聚类的平均相似度
                avg_similarity = sum(similarity_matrix[i][j] for i in cluster) / len(cluster)
                
                if avg_similarity >= SEMANTIC_SIMILARITY_THRESHOLD:
                    cluster.append(j)
                    used.add(j)
            
            if len(cluster) >= min_cluster_size:
                clusters.append(cluster)
        
        return clusters
    
    def expand_query_with_semantics(self, query: str) -> List[str]:
        """
        使用语义词典扩展查询
        
        Args:
            query: 原始查询
            
        Returns:
            扩展后的查询词列表
        """
        words = self._extract_words(query)
        expanded_words = set(words)  # 包含原始词汇
        
        for word in words:
            if word in self.semantic_dict:
                expanded_words.update(self.semantic_dict[word])
        
        return list(expanded_words)
    
    def calculate_document_similarity(self, doc1: str, doc2: str) -> Dict[str, float]:
        """
        计算两个文档的详细相似度信息
        
        Args:
            doc1: 文档1
            doc2: 文档2
            
        Returns:
            相似度详细信息
        """
        # 向量相似度
        vector1 = self._text_to_vector(doc1)
        vector2 = self._text_to_vector(doc2)
        vector_sim = self._cosine_similarity(vector1, vector2)
        
        # 语义相似度
        words1 = set(self._extract_words(doc1))
        words2 = set(self._extract_words(doc2))
        
        semantic_sim = self._calculate_semantic_overlap(words1, words2)
        
        # 词汇重叠度
        if len(words1 | words2) > 0:
            jaccard_sim = len(words1 & words2) / len(words1 | words2)
        else:
            jaccard_sim = 0.0
        
        # 综合相似度
        combined_sim = (vector_sim * 0.4 + semantic_sim * 0.4 + jaccard_sim * 0.2)
        
        return {
            'vector_similarity': vector_sim,
            'semantic_similarity': semantic_sim,
            'jaccard_similarity': jaccard_sim,
            'combined_similarity': combined_sim,
            'common_words': list(words1 & words2),
            'total_unique_words': len(words1 | words2)
        }
    
    def _calculate_semantic_overlap(self, words1: Set[str], words2: Set[str]) -> float:
        """计算两个词汇集合的语义重叠度"""
        if not words1 or not words2:
            return 0.0
        
        semantic_matches = 0
        total_words = len(words1 | words2)
        
        # 直接匹配
        direct_matches = len(words1 & words2)
        
        # 语义匹配
        for word1 in words1:
            if word1 in self.semantic_dict:
                similar_words = set(self.semantic_dict[word1])
                if similar_words & words2:
                    semantic_matches += 1
        
        return (direct_matches + semantic_matches * 0.7) / total_words if total_words > 0 else 0.0
    
    def get_semantic_suggestions(self, word: str, max_suggestions: int = 5) -> List[str]:
        """
        获取词汇的语义建议
        
        Args:
            word: 输入词汇
            max_suggestions: 最大建议数
            
        Returns:
            语义相关词汇列表
        """
        suggestions = []
        
        # 直接查找
        if word.lower() in self.semantic_dict:
            suggestions.extend(self.semantic_dict[word.lower()][:max_suggestions])
        
        # 反向查找
        for key, values in self.semantic_dict.items():
            if word.lower() in [v.lower() for v in values] and key not in suggestions:
                suggestions.append(key)
                if len(suggestions) >= max_suggestions:
                    break
        
        return suggestions[:max_suggestions]


# 全局语义匹配器实例
_semantic_matcher = None

def get_semantic_matcher() -> SemanticMatcher:
    """获取全局语义匹配器实例"""
    global _semantic_matcher
    if _semantic_matcher is None:
        _semantic_matcher = SemanticMatcher()
    return _semantic_matcher