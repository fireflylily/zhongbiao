"""
产品文档解析器
解析技术说明书，提取产品功能和特性描述
"""

import re
import logging
from typing import List, Dict, Any, Optional, Set
try:
    from ..utils.file_utils import get_file_utils
    from ..config import MIN_PARAGRAPH_LENGTH
except ImportError:
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent))
    from utils.file_utils import get_file_utils
    from config import MIN_PARAGRAPH_LENGTH

class ProductParser:
    """产品文档解析器类"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.file_utils = get_file_utils()
        
        # 产品功能关键词
        self.feature_keywords = [
            '功能', '特性', '特点', '优势', '能力', '支持',
            '提供', '实现', '具备', '包含', '涵盖', '拥有'
        ]
        
        # 技术关键词
        self.tech_keywords = [
            '架构', '技术', '算法', '协议', '接口', 'api',
            '数据库', '存储', '网络', '安全', '性能', '集成'
        ]
        
        # 规格参数关键词
        self.spec_keywords = [
            '参数', '规格', '指标', '配置', '要求', '标准',
            '容量', '速度', '精度', '范围', '限制'
        ]
    
    def parse_product_document(self, file_path: str) -> Dict[str, Any]:
        """
        解析产品文档
        
        Args:
            file_path: 产品文档路径
            
        Returns:
            解析结果字典，包含功能、特性、技术规格等
        """
        self.logger.info(f"开始解析产品文档: {file_path}")
        
        # 读取文件
        file_data = self.file_utils.read_file(file_path)
        if 'error' in file_data:
            return {'error': file_data['error']}
        
        # 提取文本内容
        text_content = self.file_utils.extract_text_content(file_data)
        if not text_content:
            return {'error': '无法提取文档文本内容'}
        
        # 分割为章节
        sections = self.file_utils.split_into_sections(text_content)
        
        # 提取产品信息
        product_info = self._extract_product_info(sections, text_content)
        features = self._extract_features(sections, text_content)
        technical_specs = self._extract_technical_specs(sections, text_content)
        advantages = self._extract_advantages(sections, text_content)
        
        # 构建功能索引
        feature_index = self._build_feature_index(features)
        
        result = {
            'file_path': file_path,
            'file_type': file_data.get('type', 'unknown'),
            'total_sections': len(sections),
            'product_info': product_info,
            'features': features,
            'technical_specs': technical_specs,
            'advantages': advantages,
            'feature_index': feature_index,
            'sections': sections
        }
        
        self.logger.info(f"产品文档解析完成，发现 {len(features)} 个功能特性")
        return result
    
    def _extract_product_info(self, sections: List[Dict[str, Any]], full_text: str) -> Dict[str, Any]:
        """
        提取产品基本信息
        
        Args:
            sections: 章节列表
            full_text: 完整文本
            
        Returns:
            产品基本信息
        """
        product_info = {
            'name': '',
            'version': '',
            'description': '',
            'category': ''
        }
        
        # 查找产品名称和版本
        name_patterns = [
            r'产品名称[:：]\s*([^\\n]+)',
            r'系统名称[:：]\s*([^\\n]+)',
            r'软件名称[:：]\s*([^\\n]+)',
            r'([^\\n]*系统|[^\\n]*平台|[^\\n]*软件)\\s*v?\d+\\.\\d+',
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                product_info['name'] = match.group(1).strip()
                break
        
        # 查找版本信息
        version_patterns = [
            r'版本[:：]\s*([v\d\.]+)',
            r'Version[:：]\s*([v\d\.]+)',
            r'v(\d+\.\d+[\.\d]*)',
        ]
        
        for pattern in version_patterns:
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                product_info['version'] = match.group(1).strip()
                break
        
        # 查找产品描述（通常在开头几个段落）
        for section in sections[:3]:  # 只检查前3个章节
            if section['level'] <= 2:  # 高级别章节
                content = section['content']
                if len(content) > MIN_PARAGRAPH_LENGTH and not product_info['description']:
                    # 取第一个长段落作为描述
                    paragraphs = [p.strip() for p in content.split('\\n') if len(p.strip()) > MIN_PARAGRAPH_LENGTH]
                    if paragraphs:
                        product_info['description'] = paragraphs[0]
                        break
        
        # 产品分类推断
        text_lower = full_text.lower()
        if any(keyword in text_lower for keyword in ['大数据', '数据分析', '数据处理']):
            product_info['category'] = '大数据平台'
        elif any(keyword in text_lower for keyword in ['云计算', '云平台', 'saas']):
            product_info['category'] = '云计算平台'
        elif any(keyword in text_lower for keyword in ['人工智能', 'ai', '机器学习']):
            product_info['category'] = 'AI平台'
        elif any(keyword in text_lower for keyword in ['物联网', 'iot', '传感器']):
            product_info['category'] = '物联网平台'
        else:
            product_info['category'] = '软件平台'
        
        return product_info
    
    def _extract_features(self, sections: List[Dict[str, Any]], full_text: str) -> List[Dict[str, Any]]:
        """
        提取产品功能特性
        
        Args:
            sections: 章节列表
            full_text: 完整文本
            
        Returns:
            功能特性列表
        """
        features = []
        
        # 查找功能相关章节
        feature_sections = []
        for section in sections:
            title_lower = section['title'].lower()
            content_lower = section['content'].lower()
            
            # 检查标题是否包含功能关键词
            title_match = any(keyword in title_lower for keyword in self.feature_keywords)
            # 检查内容功能关键词密度
            feature_density = sum(1 for keyword in self.feature_keywords if keyword in content_lower)
            
            if title_match or feature_density >= 3:
                feature_sections.append(section)
        
        # 如果没有找到明确的功能章节，使用全部章节
        if not feature_sections:
            feature_sections = [s for s in sections if len(s['content']) > MIN_PARAGRAPH_LENGTH]
        
        # 提取功能特性
        feature_id = 1
        for section in feature_sections:
            section_features = self._parse_feature_items(section['content'], section['title'])
            
            for feature in section_features:
                features.append({
                    'id': f"FEAT_{feature_id:03d}",
                    'title': feature['title'],
                    'description': feature['description'],
                    'category': feature.get('category', '通用功能'),
                    'keywords': feature.get('keywords', []),
                    'source_section': section['title'],
                    'technical_level': feature.get('technical_level', 'normal')
                })
                feature_id += 1
        
        return features
    
    def _extract_technical_specs(self, sections: List[Dict[str, Any]], full_text: str) -> List[Dict[str, Any]]:
        """
        提取技术规格参数
        
        Args:
            sections: 章节列表
            full_text: 完整文本
            
        Returns:
            技术规格列表
        """
        specs = []
        
        # 查找技术规格章节
        spec_sections = []
        for section in sections:
            title_lower = section['title'].lower()
            content_lower = section['content'].lower()
            
            # 检查是否为技术规格章节
            title_match = any(keyword in title_lower for keyword in self.spec_keywords + self.tech_keywords)
            content_match = sum(1 for keyword in self.spec_keywords if keyword in content_lower)
            
            if title_match or content_match >= 2:
                spec_sections.append(section)
        
        # 提取技术规格
        for section in spec_sections:
            section_specs = self._parse_spec_items(section['content'])
            specs.extend(section_specs)
        
        return specs
    
    def _extract_advantages(self, sections: List[Dict[str, Any]], full_text: str) -> List[Dict[str, Any]]:
        """
        提取产品优势
        
        Args:
            sections: 章节列表
            full_text: 完整文本
            
        Returns:
            产品优势列表
        """
        advantages = []
        advantage_keywords = ['优势', '优点', '特色', '亮点', '创新', '领先']
        
        # 查找优势相关章节
        advantage_sections = []
        for section in sections:
            title_lower = section['title'].lower()
            
            if any(keyword in title_lower for keyword in advantage_keywords):
                advantage_sections.append(section)
        
        # 提取优势点
        for section in advantage_sections:
            section_advantages = self._parse_advantage_items(section['content'])
            advantages.extend(section_advantages)
        
        # 如果没有明确的优势章节，从其他内容中推断
        if not advantages:
            advantages = self._infer_advantages_from_features(full_text)
        
        return advantages
    
    def _parse_feature_items(self, content: str, section_title: str) -> List[Dict[str, Any]]:
        """
        解析功能特性项目
        
        Args:
            content: 章节内容
            section_title: 章节标题
            
        Returns:
            功能特性列表
        """
        features = []
        
        # 按段落分割内容
        paragraphs = [p.strip() for p in content.split('\\n') if len(p.strip()) > MIN_PARAGRAPH_LENGTH]
        
        for paragraph in paragraphs:
            # 尝试识别功能描述
            if self._is_feature_description(paragraph):
                title = self._extract_feature_title(paragraph)
                description = paragraph
                category = self._categorize_feature(paragraph, section_title)
                keywords = self._extract_keywords(paragraph)
                technical_level = self._assess_technical_level(paragraph)
                
                features.append({
                    'title': title,
                    'description': description,
                    'category': category,
                    'keywords': keywords,
                    'technical_level': technical_level
                })
        
        return features
    
    def _parse_spec_items(self, content: str) -> List[Dict[str, Any]]:
        """解析技术规格项目"""
        specs = []
        
        # 匹配规格参数模式
        patterns = [
            r'([^：:]+)[:：]\s*([^\\n]+)',  # 参数名：值
            r'([^\\n]*(?:容量|速度|内存|cpu|磁盘)[^\\n]*)',  # 硬件规格
            r'([^\\n]*(?:并发|tps|qps|响应时间)[^\\n]*)',  # 性能指标
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                if len(match.groups()) == 2:
                    name, value = match.groups()
                    specs.append({
                        'name': name.strip(),
                        'value': value.strip(),
                        'type': self._classify_spec_type(name)
                    })
                else:
                    specs.append({
                        'name': '技术规格',
                        'value': match.group(1).strip(),
                        'type': 'general'
                    })
        
        return specs
    
    def _parse_advantage_items(self, content: str) -> List[Dict[str, Any]]:
        """解析产品优势项目"""
        advantages = []
        
        # 按段落分析优势
        paragraphs = [p.strip() for p in content.split('\\n') if len(p.strip()) > MIN_PARAGRAPH_LENGTH]
        
        for paragraph in paragraphs:
            if any(keyword in paragraph for keyword in ['领先', '先进', '创新', '优势', '特色']):
                title = self._extract_advantage_title(paragraph)
                advantages.append({
                    'title': title,
                    'description': paragraph,
                    'impact': self._assess_advantage_impact(paragraph)
                })
        
        return advantages
    
    def _build_feature_index(self, features: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """
        构建功能特性索引，用于快速匹配
        
        Args:
            features: 功能特性列表
            
        Returns:
            关键词到功能ID的映射字典
        """
        index = {}
        
        for feature in features:
            feature_id = feature['id']
            
            # 添加标题关键词
            title_words = self._extract_keywords(feature['title'])
            for word in title_words:
                if word not in index:
                    index[word] = []
                index[word].append(feature_id)
            
            # 添加描述关键词
            desc_words = feature.get('keywords', [])
            for word in desc_words:
                if word not in index:
                    index[word] = []
                if feature_id not in index[word]:
                    index[word].append(feature_id)
        
        return index
    
    def _is_feature_description(self, text: str) -> bool:
        """判断文本是否为功能描述"""
        text_lower = text.lower()
        feature_indicators = sum(1 for keyword in self.feature_keywords if keyword in text_lower)
        return feature_indicators >= 1 and len(text) > MIN_PARAGRAPH_LENGTH
    
    def _extract_feature_title(self, text: str) -> str:
        """提取功能标题"""
        # 取第一个句子或短语作为标题
        sentences = re.split(r'[。；;]', text)
        if sentences:
            title = sentences[0].strip()
            # 限制标题长度
            if len(title) > 40:
                title = title[:37] + "..."
            return title
        return text[:30] + "..." if len(text) > 30 else text
    
    def _categorize_feature(self, text: str, section_title: str) -> str:
        """功能分类"""
        text_lower = text.lower()
        
        # 基于section标题分类
        section_lower = section_title.lower()
        if '数据' in section_lower:
            return '数据功能'
        elif '安全' in section_lower:
            return '安全功能'
        elif '界面' in section_lower or 'ui' in section_lower:
            return '界面功能'
        elif '管理' in section_lower:
            return '管理功能'
        
        # 基于内容分类
        if any(keyword in text_lower for keyword in ['数据', '存储', '查询', '分析']):
            return '数据功能'
        elif any(keyword in text_lower for keyword in ['安全', '权限', '认证', '加密']):
            return '安全功能'
        elif any(keyword in text_lower for keyword in ['界面', '显示', '图表', '报表']):
            return '界面功能'
        elif any(keyword in text_lower for keyword in ['配置', '管理', '监控', '维护']):
            return '管理功能'
        else:
            return '通用功能'
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        keywords = set()
        
        # 使用正则提取技术术语
        tech_terms = re.findall(r'[A-Za-z]+(?:[A-Za-z0-9]*[A-Za-z]+)*', text)
        for term in tech_terms:
            if len(term) > 2:
                keywords.add(term.lower())
        
        # 提取中文关键词
        chinese_words = re.findall(r'[\u4e00-\u9fff]+', text)
        for word in chinese_words:
            if len(word) >= 2:
                keywords.add(word)
        
        return list(keywords)[:10]  # 限制关键词数量
    
    def _assess_technical_level(self, text: str) -> str:
        """评估技术水平"""
        text_lower = text.lower()
        
        # 高技术水平指标
        high_tech_indicators = ['算法', '机器学习', '人工智能', 'ai', '深度学习', 'api', '分布式', '云原生']
        # 中等技术水平指标
        medium_tech_indicators = ['数据库', '网络', '协议', '架构', '框架', '集成']
        
        high_score = sum(1 for indicator in high_tech_indicators if indicator in text_lower)
        medium_score = sum(1 for indicator in medium_tech_indicators if indicator in text_lower)
        
        if high_score >= 2:
            return 'high'
        elif high_score >= 1 or medium_score >= 2:
            return 'medium'
        else:
            return 'basic'
    
    def _classify_spec_type(self, name: str) -> str:
        """分类规格类型"""
        name_lower = name.lower()
        
        if any(keyword in name_lower for keyword in ['cpu', '内存', '磁盘', '存储', '容量']):
            return 'hardware'
        elif any(keyword in name_lower for keyword in ['并发', 'tps', 'qps', '响应', '性能']):
            return 'performance'
        elif any(keyword in name_lower for keyword in ['网络', '带宽', '协议', '端口']):
            return 'network'
        else:
            return 'general'
    
    def _extract_advantage_title(self, text: str) -> str:
        """提取优势标题"""
        sentences = re.split(r'[。；;]', text)
        if sentences:
            return sentences[0].strip()[:30]
        return text[:30]
    
    def _assess_advantage_impact(self, text: str) -> str:
        """评估优势影响力"""
        text_lower = text.lower()
        
        high_impact_words = ['领先', '首创', '创新', '突破', '行业第一']
        medium_impact_words = ['优秀', '先进', '高效', '稳定', '可靠']
        
        if any(word in text_lower for word in high_impact_words):
            return 'high'
        elif any(word in text_lower for word in medium_impact_words):
            return 'medium'
        else:
            return 'normal'
    
    def _infer_advantages_from_features(self, text: str) -> List[Dict[str, Any]]:
        """从功能描述中推断优势"""
        advantages = []
        
        # 查找包含优势词汇的句子
        sentences = re.split(r'[。；;]', text)
        advantage_words = ['领先', '先进', '创新', '高效', '稳定', '可靠', '优秀', '强大']
        
        for sentence in sentences:
            if any(word in sentence for word in advantage_words) and len(sentence) > MIN_PARAGRAPH_LENGTH:
                advantages.append({
                    'title': sentence[:30],
                    'description': sentence,
                    'impact': self._assess_advantage_impact(sentence)
                })
        
        return advantages[:5]  # 限制推断的优势数量
    
    def search_features_by_keywords(self, features: List[Dict[str, Any]], 
                                   keywords: List[str]) -> List[Dict[str, Any]]:
        """
        根据关键词搜索功能特性
        
        Args:
            features: 功能特性列表
            keywords: 搜索关键词
            
        Returns:
            匹配的功能特性列表
        """
        matched_features = []
        
        for feature in features:
            # 计算匹配分数
            score = 0
            feature_text = f"{feature['title']} {feature['description']}".lower()
            feature_keywords = feature.get('keywords', [])
            
            for keyword in keywords:
                keyword_lower = keyword.lower()
                # 标题匹配权重更高
                if keyword_lower in feature['title'].lower():
                    score += 3
                # 描述匹配
                elif keyword_lower in feature['description'].lower():
                    score += 2
                # 关键词匹配
                elif any(keyword_lower in fk.lower() for fk in feature_keywords):
                    score += 1
            
            if score > 0:
                feature_copy = feature.copy()
                feature_copy['match_score'] = score
                matched_features.append(feature_copy)
        
        # 按匹配分数排序
        matched_features.sort(key=lambda x: x['match_score'], reverse=True)
        return matched_features


# 全局解析器实例
_product_parser = None

def get_product_parser() -> ProductParser:
    """获取全局产品文档解析器实例"""
    global _product_parser
    if _product_parser is None:
        _product_parser = ProductParser()
    return _product_parser