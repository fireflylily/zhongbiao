"""
质量保证和审查机制
对生成的技术方案进行综合质量评估和审查
"""

import logging
from typing import Dict, Any, List, Optional
import json
import time

try:
    from ..utils.llm_client import get_llm_client
    from ..config import MIN_QUALITY_SCORE, OPTIMIZATION_THRESHOLD
except ImportError:
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent))
    from utils.llm_client import get_llm_client
    from config import MIN_QUALITY_SCORE, OPTIMIZATION_THRESHOLD

class QualityReviewer:
    """质量审查器类"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.llm_client = get_llm_client()
    
    def comprehensive_quality_review(self, 
                                   proposal: Dict[str, Any],
                                   requirements: List[Dict[str, Any]],
                                   scoring_criteria: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        对完整技术方案进行综合质量审查
        
        Args:
            proposal: 生成的技术方案
            requirements: 原始需求
            scoring_criteria: 评分标准
            
        Returns:
            质量审查报告
        """
        self.logger.info("开始进行技术方案综合质量审查")
        
        review_report = {
            'overall_score': 0.0,
            'review_timestamp': time.time(),
            'section_reviews': [],
            'compliance_check': {},
            'quality_dimensions': {},
            'improvement_suggestions': [],
            'approval_status': 'pending',
            'reviewer_notes': ''
        }
        
        try:
            # 1. 章节级质量评估
            section_scores = []
            for section in proposal.get('sections', []):
                section_review = self._review_section_quality(section, requirements)
                review_report['section_reviews'].append(section_review)
                if section_review['score'] > 0:
                    section_scores.append(section_review['score'])
            
            # 2. 需求合规性检查
            review_report['compliance_check'] = self._check_requirements_compliance(
                proposal, requirements
            )
            
            # 3. 评分标准对应性检查
            review_report['scoring_alignment'] = self._check_scoring_alignment(
                proposal, scoring_criteria
            )
            
            # 4. 多维度质量评估
            review_report['quality_dimensions'] = self._assess_quality_dimensions(proposal)
            
            # 5. 计算总体得分
            dimension_scores = list(review_report['quality_dimensions'].values())
            compliance_score = review_report['compliance_check'].get('compliance_rate', 0) * 10
            
            all_scores = section_scores + dimension_scores + [compliance_score]
            review_report['overall_score'] = sum(all_scores) / len(all_scores) if all_scores else 0
            
            # 6. 生成改进建议
            review_report['improvement_suggestions'] = self._generate_improvement_suggestions(
                review_report
            )
            
            # 7. 确定审核状态
            review_report['approval_status'] = self._determine_approval_status(
                review_report['overall_score']
            )
            
            self.logger.info(f"质量审查完成，总体得分: {review_report['overall_score']:.1f}")
            
        except Exception as e:
            self.logger.error(f"质量审查失败: {e}")
            review_report['error'] = str(e)
        
        return review_report
    
    def _review_section_quality(self, 
                              section: Dict[str, Any], 
                              requirements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """评估单个章节质量"""
        section_title = section.get('title', '')
        
        section_review = {
            'section_title': section_title,
            'score': 0.0,
            'subsection_scores': [],
            'issues': [],
            'strengths': []
        }
        
        try:
            subsection_scores = []
            total_quality_score = 0.0
            quality_count = 0
            
            for subsection in section.get('subsections', []):
                subsection_score = subsection.get('quality_score', 0.0)
                if subsection_score > 0:
                    subsection_scores.append(subsection_score)
                    total_quality_score += subsection_score
                    quality_count += 1
                
                # 检查子章节质量问题
                if subsection_score < MIN_QUALITY_SCORE:
                    section_review['issues'].append(f"子章节 '{subsection.get('title', '')}' 质量不达标 ({subsection_score:.1f})")
                elif subsection_score >= OPTIMIZATION_THRESHOLD:
                    section_review['strengths'].append(f"子章节 '{subsection.get('title', '')}' 质量优秀 ({subsection_score:.1f})")
            
            # 计算章节平均得分
            if quality_count > 0:
                section_review['score'] = total_quality_score / quality_count
                section_review['subsection_scores'] = subsection_scores
            
            # 检查内容完整性
            if not section.get('content') and not section.get('subsections'):
                section_review['issues'].append("章节内容为空")
            
            # 检查章节长度
            total_content_length = len(section.get('content', ''))
            for subsection in section.get('subsections', []):
                total_content_length += len(subsection.get('content', ''))
            
            if total_content_length < 500:
                section_review['issues'].append(f"章节内容过短 ({total_content_length} 字符)")
            elif total_content_length > 8000:
                section_review['issues'].append(f"章节内容过长 ({total_content_length} 字符)")
            else:
                section_review['strengths'].append("章节长度适中")
            
        except Exception as e:
            section_review['error'] = str(e)
            self.logger.warning(f"章节质量评估失败 {section_title}: {e}")
        
        return section_review
    
    def _check_requirements_compliance(self, 
                                     proposal: Dict[str, Any], 
                                     requirements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """检查需求合规性"""
        compliance_check = {
            'total_requirements': len(requirements),
            'covered_requirements': 0,
            'compliance_rate': 0.0,
            'uncovered_requirements': [],
            'coverage_details': []
        }
        
        try:
            # 提取方案中的所有文本内容
            proposal_text = self._extract_all_proposal_text(proposal)
            
            # 检查每个需求的覆盖情况
            for req in requirements:
                req_id = req.get('id', '')
                req_title = req.get('title', '')
                req_content = req.get('content', '')
                
                # 简单的关键词匹配检查
                coverage_score = self._calculate_requirement_coverage(
                    req_title + ' ' + req_content, proposal_text
                )
                
                coverage_detail = {
                    'requirement_id': req_id,
                    'requirement_title': req_title,
                    'coverage_score': coverage_score,
                    'is_covered': coverage_score > 0.3
                }
                
                compliance_check['coverage_details'].append(coverage_detail)
                
                if coverage_detail['is_covered']:
                    compliance_check['covered_requirements'] += 1
                else:
                    compliance_check['uncovered_requirements'].append({
                        'id': req_id,
                        'title': req_title
                    })
            
            # 计算合规率
            if compliance_check['total_requirements'] > 0:
                compliance_check['compliance_rate'] = (
                    compliance_check['covered_requirements'] / compliance_check['total_requirements']
                )
            
        except Exception as e:
            compliance_check['error'] = str(e)
            self.logger.warning(f"需求合规性检查失败: {e}")
        
        return compliance_check
    
    def _check_scoring_alignment(self, 
                               proposal: Dict[str, Any], 
                               scoring_criteria: List[Dict[str, Any]]) -> Dict[str, Any]:
        """检查与评分标准的对应性"""
        alignment_check = {
            'total_criteria': len(scoring_criteria),
            'aligned_criteria': 0,
            'alignment_rate': 0.0,
            'missing_criteria': [],
            'alignment_details': []
        }
        
        try:
            proposal_sections = [s.get('title', '') for s in proposal.get('sections', [])]
            
            for criterion in scoring_criteria:
                criterion_title = criterion.get('title', '')
                criterion_weight = criterion.get('weight', 0)
                
                # 检查是否有对应章节
                is_aligned = any(
                    self._calculate_text_similarity(criterion_title, section_title) > 0.5
                    for section_title in proposal_sections
                )
                
                alignment_detail = {
                    'criterion_title': criterion_title,
                    'weight': criterion_weight,
                    'is_aligned': is_aligned,
                    'matched_sections': []
                }
                
                if is_aligned:
                    alignment_check['aligned_criteria'] += 1
                    # 找到匹配的章节
                    for section_title in proposal_sections:
                        if self._calculate_text_similarity(criterion_title, section_title) > 0.5:
                            alignment_detail['matched_sections'].append(section_title)
                else:
                    alignment_check['missing_criteria'].append({
                        'title': criterion_title,
                        'weight': criterion_weight
                    })
                
                alignment_check['alignment_details'].append(alignment_detail)
            
            # 计算对应率
            if alignment_check['total_criteria'] > 0:
                alignment_check['alignment_rate'] = (
                    alignment_check['aligned_criteria'] / alignment_check['total_criteria']
                )
            
        except Exception as e:
            alignment_check['error'] = str(e)
            self.logger.warning(f"评分标准对应性检查失败: {e}")
        
        return alignment_check
    
    def _assess_quality_dimensions(self, proposal: Dict[str, Any]) -> Dict[str, float]:
        """多维度质量评估"""
        dimensions = {
            'content_richness': 0.0,      # 内容丰富度
            'technical_depth': 0.0,       # 技术深度
            'structure_clarity': 0.0,     # 结构清晰度
            'language_quality': 0.0,      # 语言质量
            'innovation_level': 0.0       # 创新程度
        }
        
        try:
            sections = proposal.get('sections', [])
            if not sections:
                return dimensions
            
            # 内容丰富度评估
            total_content_length = sum(
                len(self._extract_section_text(section))
                for section in sections
            )
            dimensions['content_richness'] = min(10.0, total_content_length / 2000)
            
            # 结构清晰度评估
            total_subsections = sum(
                len(section.get('subsections', []))
                for section in sections
            )
            structure_score = len(sections) * 2 + total_subsections * 0.5
            dimensions['structure_clarity'] = min(10.0, structure_score)
            
            # 技术深度、语言质量、创新程度需要AI评估
            if self.llm_client:
                ai_assessment = self._ai_assess_quality_dimensions(proposal)
                if ai_assessment:
                    dimensions.update(ai_assessment)
            else:
                # 基于内容生成统计的估算
                stats = proposal.get('generation_stats', {})
                avg_quality = stats.get('average_quality_score', 0)
                
                dimensions['technical_depth'] = min(10.0, avg_quality)
                dimensions['language_quality'] = min(10.0, avg_quality * 0.9)
                dimensions['innovation_level'] = min(10.0, avg_quality * 0.8)
            
        except Exception as e:
            self.logger.warning(f"质量维度评估失败: {e}")
        
        return dimensions
    
    def _ai_assess_quality_dimensions(self, proposal: Dict[str, Any]) -> Optional[Dict[str, float]]:
        """使用AI评估质量维度"""
        try:
            # 提取方案内容摘要
            proposal_summary = self._create_proposal_summary(proposal)
            
            assessment_prompt = f"""
你是一个资深的技术方案评审专家。请对以下技术方案进行多维度质量评估：

技术方案摘要：
{proposal_summary}

请从以下维度评分（1-10分）：
1. technical_depth: 技术深度和专业性
2. language_quality: 语言表达的专业性和规范性
3. innovation_level: 技术方案的创新程度

输出JSON格式：
{{
    "technical_depth": 分数,
    "language_quality": 分数,
    "innovation_level": 分数
}}
"""
            
            result = self.llm_client.chat_completion(
                prompt=assessment_prompt,
                max_tokens=300,
                temperature=0.3
            )
            
            if result:
                try:
                    assessment = json.loads(result)
                    return {k: float(v) for k, v in assessment.items() if k in ['technical_depth', 'language_quality', 'innovation_level']}
                except json.JSONDecodeError:
                    self.logger.warning("AI质量评估结果解析失败")
            
        except Exception as e:
            self.logger.warning(f"AI质量维度评估失败: {e}")
        
        return None
    
    def _generate_improvement_suggestions(self, review_report: Dict[str, Any]) -> List[str]:
        """生成改进建议"""
        suggestions = []
        
        try:
            overall_score = review_report.get('overall_score', 0)
            
            # 基于整体得分的建议
            if overall_score < 6.0:
                suggestions.append("整体质量需要显著提升，建议重新生成或大幅修改")
            elif overall_score < 8.0:
                suggestions.append("质量达到基本要求，建议优化关键章节")
            else:
                suggestions.append("质量良好，可考虑细节优化")
            
            # 基于章节质量的建议
            section_reviews = review_report.get('section_reviews', [])
            low_quality_sections = [
                sr for sr in section_reviews 
                if sr.get('score', 0) < MIN_QUALITY_SCORE
            ]
            
            if low_quality_sections:
                section_names = [sr.get('section_title', '') for sr in low_quality_sections]
                suggestions.append(f"以下章节质量不达标，需要重点改进: {', '.join(section_names)}")
            
            # 基于合规性的建议
            compliance = review_report.get('compliance_check', {})
            compliance_rate = compliance.get('compliance_rate', 0)
            
            if compliance_rate < 0.8:
                uncovered = compliance.get('uncovered_requirements', [])
                if uncovered:
                    suggestions.append(f"需要补充对以下需求的响应: {[req.get('title', '') for req in uncovered[:3]]}")
            
            # 基于评分标准对应性的建议
            alignment = review_report.get('scoring_alignment', {})
            if alignment.get('alignment_rate', 0) < 0.9:
                missing = alignment.get('missing_criteria', [])
                if missing:
                    suggestions.append(f"缺少对应评分项的章节: {[crit.get('title', '') for crit in missing[:3]]}")
            
            # 基于质量维度的建议
            dimensions = review_report.get('quality_dimensions', {})
            for dimension, score in dimensions.items():
                if score < 6.0:
                    dimension_names = {
                        'content_richness': '内容丰富度',
                        'technical_depth': '技术深度',
                        'structure_clarity': '结构清晰度',
                        'language_quality': '语言质量',
                        'innovation_level': '创新程度'
                    }
                    suggestions.append(f"需要提升{dimension_names.get(dimension, dimension)}")
            
        except Exception as e:
            self.logger.warning(f"生成改进建议失败: {e}")
            suggestions.append("质量评估过程中出现异常，建议人工审核")
        
        return suggestions[:10]  # 最多10条建议
    
    def _determine_approval_status(self, overall_score: float) -> str:
        """确定审核状态"""
        if overall_score >= 8.5:
            return 'excellent'
        elif overall_score >= 7.0:
            return 'approved'
        elif overall_score >= 5.5:
            return 'conditional_approval'
        else:
            return 'rejected'
    
    def _extract_all_proposal_text(self, proposal: Dict[str, Any]) -> str:
        """提取方案中的所有文本"""
        text_parts = []
        
        for section in proposal.get('sections', []):
            text_parts.append(section.get('content', ''))
            for subsection in section.get('subsections', []):
                text_parts.append(subsection.get('content', ''))
        
        return ' '.join(text_parts)
    
    def _extract_section_text(self, section: Dict[str, Any]) -> str:
        """提取章节中的所有文本"""
        text_parts = [section.get('content', '')]
        
        for subsection in section.get('subsections', []):
            text_parts.append(subsection.get('content', ''))
        
        return ' '.join(text_parts)
    
    def _create_proposal_summary(self, proposal: Dict[str, Any]) -> str:
        """创建方案摘要"""
        summary_parts = [f"标题: {proposal.get('title', '')}"]
        
        for section in proposal.get('sections', [])[:5]:  # 只取前5个章节
            section_title = section.get('title', '')
            section_content = self._extract_section_text(section)
            summary_parts.append(f"章节: {section_title} - {section_content[:200]}...")
        
        return '\n'.join(summary_parts)
    
    def _calculate_requirement_coverage(self, requirement_text: str, proposal_text: str) -> float:
        """计算需求覆盖度"""
        if not requirement_text or not proposal_text:
            return 0.0
        
        # 简单的关键词匹配算法
        req_words = set(requirement_text.lower().split())
        proposal_words = set(proposal_text.lower().split())
        
        if not req_words:
            return 0.0
        
        # 计算交集比例
        intersection = req_words.intersection(proposal_words)
        coverage = len(intersection) / len(req_words)
        
        return min(1.0, coverage * 2)  # 放大系数
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """计算文本相似度"""
        if not text1 or not text2:
            return 0.0
        
        # 简单的Jaccard相似度
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0


# 全局质量审查器实例
_quality_reviewer = None

def get_quality_reviewer() -> QualityReviewer:
    """获取全局质量审查器实例"""
    global _quality_reviewer
    if _quality_reviewer is None:
        _quality_reviewer = QualityReviewer()
    return _quality_reviewer

def set_quality_reviewer(reviewer: QualityReviewer):
    """设置全局质量审查器实例"""
    global _quality_reviewer
    _quality_reviewer = reviewer