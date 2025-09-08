"""
精确匹配引擎
基于关键词、短语和文本相似度进行精确匹配
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple, Set
from difflib import SequenceMatcher
try:
    from ..config import EXACT_MATCH_THRESHOLD, MIN_PARAGRAPH_LENGTH
except ImportError:
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent))
    from config import EXACT_MATCH_THRESHOLD, MIN_PARAGRAPH_LENGTH

class ExactMatcher:
    """精确匹配引擎类"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # 停用词列表
        self.stop_words = {
            '的', '了', '在', '是', '有', '和', '与', '或', '及', '等', '各', '个',
            '一', '二', '三', '四', '五', '六', '七', '八', '九', '十',
            '能够', '可以', '应该', '需要', '具有', '支持', '实现', '提供'
        }
        
        # 技术术语权重
        self.tech_term_weights = {
            'api': 2.0, '接口': 2.0, '协议': 2.0, '算法': 2.0,
            '数据库': 1.5, '存储': 1.5, '网络': 1.5, '安全': 1.5,
            '性能': 1.5, '并发': 1.5, '分布式': 2.0, '云计算': 2.0
        }
    
    def match_requirements_with_features(self, 
                                       requirements: List[Dict[str, Any]], 
                                       features: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        匹配需求和产品功能
        
        Args:
            requirements: 需求列表
            features: 产品功能列表
            
        Returns:
            匹配结果列表
        """
        self.logger.info(f"开始精确匹配: {len(requirements)} 个需求 vs {len(features)} 个功能")
        
        matches = []
        
        for req in requirements:
            req_matches = []
            
            for feature in features:
                # 计算匹配分数
                match_score = self._calculate_match_score(req, feature)
                
                if match_score > 0.1:  # 最低匹配阈值
                    req_matches.append({
                        'requirement_id': req['id'],
                        'feature_id': feature['id'],
                        'match_score': match_score,
                        'match_type': self._determine_match_type(match_score),
                        'match_details': self._get_match_details(req, feature),
                        'requirement': req,
                        'feature': feature
                    })
            
            # 按匹配分数排序
            req_matches.sort(key=lambda x: x['match_score'], reverse=True)
            
            # 添加最佳匹配
            if req_matches:
                best_match = req_matches[0]
                best_match['is_best_match'] = True
                matches.extend(req_matches[:5])  # 只保留前5个匹配结果
            else:
                # 没有匹配的需求
                matches.append({
                    'requirement_id': req['id'],
                    'feature_id': None,
                    'match_score': 0.0,
                    'match_type': 'no_match',
                    'match_details': {'reason': '未找到匹配的功能'},
                    'requirement': req,
                    'feature': None,
                    'is_best_match': True
                })
        
        self.logger.info(f"精确匹配完成: 生成 {len(matches)} 个匹配结果")
        return matches
    
    def find_exact_text_matches(self, 
                               query_text: str, 
                               target_texts: List[str],
                               min_similarity: float = 0.8) -> List[Dict[str, Any]]:
        """
        查找精确文本匹配
        
        Args:
            query_text: 查询文本
            target_texts: 目标文本列表
            min_similarity: 最小相似度阈值
            
        Returns:
            匹配结果列表
        """
        matches = []
        
        query_clean = self._clean_text(query_text)
        query_words = self._extract_keywords(query_clean)
        
        for i, target_text in enumerate(target_texts):
            target_clean = self._clean_text(target_text)
            
            # 计算文本相似度
            similarity = SequenceMatcher(None, query_clean, target_clean).ratio()
            
            if similarity >= min_similarity:
                matches.append({
                    'index': i,
                    'text': target_text,
                    'similarity': similarity,
                    'match_type': 'exact_text'
                })
            else:
                # 检查关键词匹配
                keyword_match = self._calculate_keyword_match(query_words, target_clean)
                if keyword_match >= min_similarity:
                    matches.append({
                        'index': i,
                        'text': target_text,
                        'similarity': keyword_match,
                        'match_type': 'keyword_match'
                    })
        
        # 按相似度排序
        matches.sort(key=lambda x: x['similarity'], reverse=True)
        return matches
    
    def _calculate_match_score(self, requirement: Dict[str, Any], feature: Dict[str, Any]) -> float:
        """
        计算需求和功能的匹配分数
        
        Args:
            requirement: 需求信息
            feature: 功能信息
            
        Returns:
            匹配分数 (0-1)
        """
        total_score = 0.0
        
        # 1. 标题匹配 (权重: 0.4)
        title_score = self._calculate_text_similarity(
            requirement.get('title', ''),
            feature.get('title', '')
        )
        total_score += title_score * 0.4
        
        # 2. 内容匹配 (权重: 0.4)
        content_score = self._calculate_text_similarity(
            requirement.get('content', ''),
            feature.get('description', '')
        )
        total_score += content_score * 0.4
        
        # 3. 关键词匹配 (权重: 0.2)
        keyword_score = self._calculate_keyword_overlap(requirement, feature)
        total_score += keyword_score * 0.2
        
        return min(total_score, 1.0)  # 确保分数不超过1.0
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """计算两段文本的相似度"""
        if not text1 or not text2:
            return 0.0
        
        # 清理文本
        clean_text1 = self._clean_text(text1)
        clean_text2 = self._clean_text(text2)
        
        # 基于序列匹配的相似度
        seq_similarity = SequenceMatcher(None, clean_text1, clean_text2).ratio()
        
        # 基于关键词交集的相似度
        words1 = self._extract_keywords(clean_text1)
        words2 = self._extract_keywords(clean_text2)
        
        if not words1 or not words2:
            return seq_similarity
        
        # 计算加权Jaccard相似度
        intersection = 0.0
        union_size = len(set(words1) | set(words2))
        
        for word in set(words1) & set(words2):
            weight = self.tech_term_weights.get(word.lower(), 1.0)
            intersection += weight
        
        jaccard_similarity = intersection / union_size if union_size > 0 else 0.0
        
        # 综合相似度
        combined_similarity = (seq_similarity * 0.6 + jaccard_similarity * 0.4)
        
        return combined_similarity
    
    def _calculate_keyword_overlap(self, requirement: Dict[str, Any], feature: Dict[str, Any]) -> float:
        """计算关键词重叠度"""
        # 提取需求关键词
        req_keywords = set()
        req_text = f"{requirement.get('title', '')} {requirement.get('content', '')}"
        req_keywords.update(self._extract_keywords(req_text))
        
        # 提取功能关键词
        feature_keywords = set()
        feature_text = f"{feature.get('title', '')} {feature.get('description', '')}"
        feature_keywords.update(self._extract_keywords(feature_text))
        
        # 添加预定义关键词
        if 'keywords' in feature:
            feature_keywords.update(feature['keywords'])
        
        if not req_keywords or not feature_keywords:
            return 0.0
        
        # 计算加权交集
        intersection_weight = 0.0
        for keyword in req_keywords & feature_keywords:
            weight = self.tech_term_weights.get(keyword.lower(), 1.0)
            intersection_weight += weight
        
        # 计算加权并集
        union_weight = 0.0
        for keyword in req_keywords | feature_keywords:
            weight = self.tech_term_weights.get(keyword.lower(), 1.0)
            union_weight += weight
        
        return intersection_weight / union_weight if union_weight > 0 else 0.0
    
    def _clean_text(self, text: str) -> str:
        """清理文本"""
        if not text:
            return ""
        
        # 转换为小写
        text = text.lower()
        
        # 移除标点符号和特殊字符
        text = re.sub(r'[^\w\s\u4e00-\u9fff]', ' ', text)
        
        # 移除多余空格
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        if not text:
            return []
        
        # 分词
        words = text.split()
        
        # 过滤关键词
        keywords = []
        for word in words:
            word = word.strip()
            if (len(word) >= 2 and 
                word not in self.stop_words and
                not word.isdigit()):
                keywords.append(word)
        
        return keywords
    
    def _determine_match_type(self, match_score: float) -> str:
        """确定匹配类型"""
        if match_score >= EXACT_MATCH_THRESHOLD:
            return 'exact_match'  # 精确匹配，可直接复用
        elif match_score >= 0.5:
            return 'high_match'   # 高度匹配，需要少量修改
        elif match_score >= 0.3:
            return 'medium_match' # 中等匹配，需要改写
        elif match_score >= 0.1:
            return 'low_match'    # 低匹配，需要重写
        else:
            return 'no_match'     # 无匹配
    
    def _get_match_details(self, requirement: Dict[str, Any], feature: Dict[str, Any]) -> Dict[str, Any]:
        """获取匹配详情"""
        details = {
            'matched_keywords': [],
            'title_similarity': 0.0,
            'content_similarity': 0.0,
            'confidence': 'low'
        }
        
        # 计算各部分相似度
        details['title_similarity'] = self._calculate_text_similarity(
            requirement.get('title', ''),
            feature.get('title', '')
        )
        
        details['content_similarity'] = self._calculate_text_similarity(
            requirement.get('content', ''),
            feature.get('description', '')
        )
        
        # 找到匹配的关键词
        req_keywords = set(self._extract_keywords(
            f"{requirement.get('title', '')} {requirement.get('content', '')}"
        ))
        feature_keywords = set(self._extract_keywords(
            f"{feature.get('title', '')} {feature.get('description', '')}"
        ))
        
        details['matched_keywords'] = list(req_keywords & feature_keywords)
        
        # 确定置信度
        avg_similarity = (details['title_similarity'] + details['content_similarity']) / 2
        if avg_similarity >= 0.8:
            details['confidence'] = 'high'
        elif avg_similarity >= 0.6:
            details['confidence'] = 'medium'
        else:
            details['confidence'] = 'low'
        
        return details
    
    def _calculate_keyword_match(self, query_words: List[str], target_text: str) -> float:
        """计算关键词匹配度"""
        if not query_words:
            return 0.0
        
        target_words = self._extract_keywords(target_text)
        if not target_words:
            return 0.0
        
        # 计算匹配的关键词权重
        matched_weight = 0.0
        total_weight = 0.0
        
        for word in query_words:
            weight = self.tech_term_weights.get(word.lower(), 1.0)
            total_weight += weight
            
            if word in target_words:
                matched_weight += weight
        
        return matched_weight / total_weight if total_weight > 0 else 0.0
    
    def find_phrase_matches(self, phrases: List[str], text: str) -> List[Dict[str, Any]]:
        """
        在文本中查找短语匹配
        
        Args:
            phrases: 要查找的短语列表
            text: 目标文本
            
        Returns:
            匹配结果列表
        """
        matches = []
        text_lower = text.lower()
        
        for phrase in phrases:
            phrase_lower = phrase.lower()
            
            # 精确匹配
            if phrase_lower in text_lower:
                # 找到所有匹配位置
                start = 0
                while True:
                    pos = text_lower.find(phrase_lower, start)
                    if pos == -1:
                        break
                    
                    matches.append({
                        'phrase': phrase,
                        'position': pos,
                        'context': self._get_context(text, pos, len(phrase)),
                        'match_type': 'exact_phrase'
                    })
                    start = pos + 1
            
            # 模糊匹配（允许小的差异）
            else:
                words = phrase_lower.split()
                if len(words) > 1:
                    # 检查是否所有词都在文本中
                    all_words_found = all(word in text_lower for word in words)
                    if all_words_found:
                        matches.append({
                            'phrase': phrase,
                            'position': -1,
                            'context': text[:100] + "...",
                            'match_type': 'fuzzy_phrase'
                        })
        
        return matches
    
    def _get_context(self, text: str, position: int, phrase_length: int, context_size: int = 50) -> str:
        """获取匹配短语的上下文"""
        start = max(0, position - context_size)
        end = min(len(text), position + phrase_length + context_size)
        
        context = text[start:end]
        
        # 标记匹配的部分
        if position >= 0:
            relative_pos = position - start
            before = context[:relative_pos]
            matched = context[relative_pos:relative_pos + phrase_length]
            after = context[relative_pos + phrase_length:]
            context = f"{before}**{matched}**{after}"
        
        return context
    
    def batch_match(self, 
                   requirements: List[Dict[str, Any]], 
                   features: List[Dict[str, Any]],
                   batch_size: int = 10) -> List[Dict[str, Any]]:
        """
        批量匹配处理
        
        Args:
            requirements: 需求列表
            features: 功能列表
            batch_size: 批处理大小
            
        Returns:
            匹配结果列表
        """
        all_matches = []
        
        # 分批处理
        for i in range(0, len(requirements), batch_size):
            batch_reqs = requirements[i:i + batch_size]
            batch_matches = self.match_requirements_with_features(batch_reqs, features)
            all_matches.extend(batch_matches)
            
            self.logger.info(f"已处理批次 {i//batch_size + 1}: {len(batch_reqs)} 个需求")
        
        return all_matches


# 全局匹配器实例
_exact_matcher = None

def get_exact_matcher() -> ExactMatcher:
    """获取全局精确匹配器实例"""
    global _exact_matcher
    if _exact_matcher is None:
        _exact_matcher = ExactMatcher()
    return _exact_matcher