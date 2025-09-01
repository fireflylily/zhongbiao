"""
内容生成器
根据匹配结果生成技术方案内容
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
try:
    from ..utils.llm_client import get_llm_client
    from ..matchers.exact_matcher import get_exact_matcher
    from ..matchers.semantic_matcher import get_semantic_matcher
    from ..config import (
        EXACT_MATCH_THRESHOLD, REWRITE_THRESHOLD, GENERATE_THRESHOLD,
        CONTENT_GENERATION_PROMPT, CONTENT_REWRITE_PROMPT
    )
except ImportError:
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent))
    from utils.llm_client import get_llm_client
    from matchers.exact_matcher import get_exact_matcher
    from matchers.semantic_matcher import get_semantic_matcher
    from config import (
        EXACT_MATCH_THRESHOLD, REWRITE_THRESHOLD, GENERATE_THRESHOLD,
        CONTENT_GENERATION_PROMPT, CONTENT_REWRITE_PROMPT
    )

class ContentGenerator:
    """内容生成器类"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.llm_client = get_llm_client()
        self.exact_matcher = get_exact_matcher()
        self.semantic_matcher = get_semantic_matcher()
    
    def generate_proposal_content(self, 
                                 outline: Dict[str, Any],
                                 match_results: List[Dict[str, Any]],
                                 product_features: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        生成完整的技术方案内容
        
        Args:
            outline: 技术方案大纲
            match_results: 需求与功能匹配结果
            product_features: 产品功能列表
            
        Returns:
            生成的方案内容
        """
        self.logger.info("开始生成技术方案内容")
        
        proposal = {
            'title': outline.get('title', '技术方案'),
            'sections': [],
            'generation_stats': {
                'total_sections': 0,
                'generated_sections': 0,
                'reused_content': 0,
                'ai_generated': 0
            }
        }
        
        # 为每个章节生成内容
        for section in outline.get('sections', []):
            section_content = self._generate_section_content(
                section, match_results, product_features
            )
            proposal['sections'].append(section_content)
            
            # 更新统计
            self._update_generation_stats(proposal['generation_stats'], section_content)
        
        proposal['generation_stats']['total_sections'] = len(proposal['sections'])
        
        self.logger.info(f"技术方案内容生成完成: {proposal['generation_stats']}")
        return proposal
    
    def _generate_section_content(self, 
                                 section: Dict[str, Any],
                                 match_results: List[Dict[str, Any]],
                                 product_features: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        为单个章节生成内容
        
        Args:
            section: 章节信息
            match_results: 匹配结果
            product_features: 产品功能列表
            
        Returns:
            章节内容
        """
        section_title = section.get('title', '')
        self.logger.info(f"生成章节内容: {section_title}")
        
        section_content = {
            'title': section_title,
            'level': section.get('level', 1),
            'weight': section.get('weight', ''),
            'content': '',
            'subsections': [],
            'generation_method': 'unknown'
        }
        
        # 查找相关的匹配结果
        related_matches = self._find_related_matches(section, match_results)
        
        # 生成章节介绍
        section_intro = self._generate_section_intro(section, related_matches)
        section_content['content'] = section_intro
        
        # 生成子章节内容
        for subsection in section.get('subsections', []):
            subsection_content = self._generate_subsection_content(
                subsection, related_matches, product_features, section_title
            )
            section_content['subsections'].append(subsection_content)
        
        return section_content
    
    def _generate_subsection_content(self, 
                                   subsection: Dict[str, Any],
                                   related_matches: List[Dict[str, Any]],
                                   product_features: List[Dict[str, Any]],
                                   parent_title: str) -> Dict[str, Any]:
        """生成子章节内容"""
        subsection_title = subsection.get('title', '')
        
        subsection_content = {
            'title': subsection_title,
            'level': subsection.get('level', 2),
            'content': '',
            'generation_method': 'unknown'
        }
        
        # 查找最相关的匹配
        best_match = self._find_best_match_for_subsection(subsection_title, related_matches)
        
        if best_match:
            content, method = self._generate_content_based_on_match(
                best_match, subsection_title, parent_title
            )
            subsection_content['content'] = content
            subsection_content['generation_method'] = method
        else:
            # 没有匹配，基于要点生成内容
            content = self._generate_content_from_points(
                subsection.get('points', []), subsection_title, parent_title
            )
            subsection_content['content'] = content
            subsection_content['generation_method'] = 'from_points'
        
        return subsection_content
    
    def _find_related_matches(self, 
                            section: Dict[str, Any], 
                            match_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """查找与章节相关的匹配结果"""
        section_title = section.get('title', '').lower()
        requirements_mapping = section.get('requirements_mapping', [])
        
        related_matches = []
        
        # 基于需求映射查找
        for match in match_results:
            if match.get('requirement_id') in requirements_mapping:
                related_matches.append(match)
        
        # 基于标题关键词查找
        if len(related_matches) < 2:  # 如果匹配数量不够，扩展搜索
            for match in match_results:
                if match in related_matches:
                    continue
                
                requirement = match.get('requirement', {})
                req_text = f"{requirement.get('title', '')} {requirement.get('content', '')}".lower()
                
                # 简单关键词匹配
                if any(word in req_text for word in section_title.split() if len(word) > 2):
                    related_matches.append(match)
                    if len(related_matches) >= 5:  # 限制数量
                        break
        
        # 按匹配分数排序
        related_matches.sort(
            key=lambda x: x.get('match_score', x.get('semantic_score', 0)), 
            reverse=True
        )
        
        return related_matches[:3]  # 最多返回3个相关匹配
    
    def _find_best_match_for_subsection(self, 
                                      subsection_title: str, 
                                      related_matches: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """为子章节找到最佳匹配"""
        if not related_matches:
            return None
        
        subsection_title_lower = subsection_title.lower()
        
        # 寻找标题最相关的匹配
        best_match = None
        best_score = 0.0
        
        for match in related_matches:
            feature = match.get('feature')
            if not feature:
                continue
            
            feature_text = f"{feature.get('title', '')} {feature.get('description', '')}".lower()
            
            # 计算相关性分数
            score = 0.0
            for word in subsection_title_lower.split():
                if len(word) > 2 and word in feature_text:
                    score += 1.0
            
            # 加上原始匹配分数
            original_score = match.get('match_score', match.get('semantic_score', 0))
            total_score = score * 0.6 + original_score * 0.4
            
            if total_score > best_score:
                best_score = total_score
                best_match = match
        
        return best_match if best_score > 0.1 else related_matches[0]  # 返回最佳匹配或第一个
    
    def _generate_content_based_on_match(self, 
                                       match: Dict[str, Any], 
                                       subsection_title: str,
                                       parent_title: str) -> Tuple[str, str]:
        """基于匹配结果生成内容"""
        match_score = match.get('match_score', match.get('semantic_score', 0))
        match_type = match.get('match_type', 'unknown')
        requirement = match.get('requirement', {})
        feature = match.get('feature', {})
        
        # 根据匹配分数决定生成策略
        if match_score >= EXACT_MATCH_THRESHOLD:
            # 直接复用产品功能描述
            content = self._reuse_feature_content(feature, requirement, subsection_title)
            return content, 'direct_reuse'
            
        elif match_score >= REWRITE_THRESHOLD:
            # 改写产品功能描述
            content = self._rewrite_feature_content(
                feature, requirement, subsection_title, parent_title
            )
            return content, 'rewrite'
            
        else:
            # AI生成新内容
            content = self._generate_ai_content(
                requirement, feature, subsection_title, parent_title
            )
            return content, 'ai_generate'
    
    def _reuse_feature_content(self, 
                             feature: Dict[str, Any], 
                             requirement: Dict[str, Any],
                             subsection_title: str) -> str:
        """直接复用产品功能内容"""
        content = feature.get('description', '')
        
        if not content:
            content = feature.get('title', '')
        
        # 如果内容太短，添加一些补充说明
        if len(content) < 100:
            content += f"\\n\\n本系统在{subsection_title}方面具备完善的解决方案，能够满足相关技术要求。"
        
        return content
    
    def _rewrite_feature_content(self, 
                               feature: Dict[str, Any], 
                               requirement: Dict[str, Any],
                               subsection_title: str,
                               parent_title: str) -> str:
        """改写产品功能内容"""
        original_content = feature.get('description', feature.get('title', ''))
        target_requirement = requirement.get('content', requirement.get('title', ''))
        
        if self.llm_client:
            try:
                rewritten_content = self.llm_client.rewrite_content(
                    original_content=original_content,
                    target_requirement=target_requirement,
                    section_title=subsection_title
                )
                
                if rewritten_content:
                    return rewritten_content
            except Exception as e:
                self.logger.warning(f"内容改写失败: {e}")
        
        # 回退到简单改写
        return self._simple_rewrite_content(original_content, subsection_title, parent_title)
    
    def _generate_ai_content(self, 
                           requirement: Dict[str, Any],
                           feature: Optional[Dict[str, Any]],
                           subsection_title: str,
                           parent_title: str) -> str:
        """使用AI生成新内容"""
        if not self.llm_client:
            return self._generate_fallback_content(subsection_title, parent_title)
        
        try:
            requirement_text = requirement.get('content', requirement.get('title', ''))
            feature_text = feature.get('description', '') if feature else ''
            
            content = self.llm_client.generate_content(
                requirement=requirement_text,
                product_features=feature_text,
                section_title=subsection_title
            )
            
            if content:
                return content
            
        except Exception as e:
            self.logger.warning(f"AI内容生成失败: {e}")
        
        # 回退到默认内容
        return self._generate_fallback_content(subsection_title, parent_title)
    
    def _generate_content_from_points(self, 
                                    points: List[str], 
                                    subsection_title: str,
                                    parent_title: str) -> str:
        """基于要点生成内容"""
        if not points:
            return self._generate_fallback_content(subsection_title, parent_title)
        
        content_parts = [f"在{subsection_title}方面，本方案主要包括以下内容：\\n"]
        
        for i, point in enumerate(points[:5], 1):  # 最多5个要点
            content_parts.append(f"{i}. {point}：提供完整的{point.lower()}解决方案，确保技术先进性和实用性。")
        
        content_parts.append(f"\\n通过以上{subsection_title}设计，能够有效支撑{parent_title}的整体目标实现。")
        
        return '\\n'.join(content_parts)
    
    def _simple_rewrite_content(self, original_content: str, subsection_title: str, parent_title: str) -> str:
        """简单改写内容"""
        if not original_content:
            return self._generate_fallback_content(subsection_title, parent_title)
        
        # 简单的文本替换和修饰
        content = original_content
        
        # 添加开头
        if not content.startswith(('在', '本', '我们', '系统')):
            content = f"在{subsection_title}方面，{content}"
        
        # 添加结尾
        if not content.endswith('。'):
            content += '。'
        
        content += f"这一设计充分体现了{parent_title}的技术优势和实用性。"
        
        return content
    
    def _generate_fallback_content(self, subsection_title: str, parent_title: str) -> str:
        """生成回退内容"""
        templates = [
            f"本方案在{subsection_title}方面采用先进的技术架构和设计理念，确保系统的稳定性、可靠性和可扩展性。",
            f"针对{subsection_title}的要求，我们提供完整的解决方案，包括详细的设计、实施和优化策略。",
            f"在{subsection_title}的实现上，本方案结合行业最佳实践，提供高效、安全的技术实现方案。"
        ]
        
        import random
        base_content = random.choice(templates)
        
        additional_content = f"\\n\\n具体包括：\\n- 完整的{subsection_title}设计方案\\n- 详细的技术实现路径\\n- 有效的质量保障措施\\n- 持续的优化改进机制"
        
        return base_content + additional_content
    
    def _generate_section_intro(self, section: Dict[str, Any], related_matches: List[Dict[str, Any]]) -> str:
        """生成章节介绍"""
        section_title = section.get('title', '')
        section_weight = section.get('weight', '')
        
        intro = f"## {section_title}\\n\\n"
        
        if section_weight:
            intro += f"本章节在技术评分中占{section_weight}，是技术方案的重要组成部分。"
        
        if related_matches:
            intro += f"本章节将重点阐述{section_title}的设计理念、技术实现和关键特性。"
        else:
            intro += f"本章节提供{section_title}的完整解决方案。"
        
        return intro
    
    def _update_generation_stats(self, stats: Dict[str, int], section_content: Dict[str, Any]):
        """更新生成统计"""
        for subsection in section_content.get('subsections', []):
            method = subsection.get('generation_method', 'unknown')
            
            if method == 'direct_reuse':
                stats['reused_content'] += 1
            elif method in ['rewrite', 'ai_generate']:
                stats['ai_generated'] += 1
            
            stats['generated_sections'] += 1
    
    def export_to_text(self, proposal: Dict[str, Any]) -> str:
        """导出为纯文本格式"""
        text_parts = []
        
        # 标题
        text_parts.append(f"# {proposal.get('title', '技术方案')}\\n")
        
        # 章节内容
        for section in proposal.get('sections', []):
            # 章节标题
            level = section.get('level', 1)
            title_prefix = '#' * (level + 1)
            text_parts.append(f"{title_prefix} {section.get('title', '')}\\n")
            
            # 章节内容
            if section.get('content'):
                text_parts.append(f"{section['content']}\\n")
            
            # 子章节
            for subsection in section.get('subsections', []):
                sub_level = subsection.get('level', 2)
                sub_prefix = '#' * (sub_level + 1)
                text_parts.append(f"{sub_prefix} {subsection.get('title', '')}\\n")
                
                if subsection.get('content'):
                    text_parts.append(f"{subsection['content']}\\n")
        
        return '\\n'.join(text_parts)
    
    def generate_match_report(self, match_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成匹配度报告"""
        report = {
            'total_requirements': len(set(m['requirement_id'] for m in match_results if m.get('requirement_id'))),
            'matched_requirements': 0,
            'unmatched_requirements': 0,
            'match_distribution': {
                'exact_match': 0,
                'high_match': 0,
                'medium_match': 0,
                'low_match': 0,
                'no_match': 0
            },
            'average_match_score': 0.0,
            'details': []
        }
        
        total_score = 0.0
        req_matches = {}
        
        # 按需求分组
        for match in match_results:
            req_id = match.get('requirement_id')
            if req_id:
                if req_id not in req_matches:
                    req_matches[req_id] = []
                req_matches[req_id].append(match)
        
        # 分析每个需求的匹配情况
        for req_id, matches in req_matches.items():
            best_match = max(matches, key=lambda x: x.get('match_score', x.get('semantic_score', 0)))
            match_score = best_match.get('match_score', best_match.get('semantic_score', 0))
            match_type = best_match.get('match_type', 'no_match')
            
            if match_score > 0:
                report['matched_requirements'] += 1
            else:
                report['unmatched_requirements'] += 1
            
            # 统计匹配类型
            if match_type in report['match_distribution']:
                report['match_distribution'][match_type] += 1
            
            total_score += match_score
            
            # 添加详细信息
            requirement = best_match.get('requirement', {})
            feature = best_match.get('feature', {})
            
            report['details'].append({
                'requirement_id': req_id,
                'requirement_title': requirement.get('title', ''),
                'feature_title': feature.get('title', '') if feature else 'N/A',
                'match_score': match_score,
                'match_type': match_type
            })
        
        # 计算平均分数
        if req_matches:
            report['average_match_score'] = total_score / len(req_matches)
        
        return report


# 全局内容生成器实例
_content_generator = None

def get_content_generator() -> ContentGenerator:
    """获取全局内容生成器实例"""
    global _content_generator
    if _content_generator is None:
        _content_generator = ContentGenerator()
    return _content_generator