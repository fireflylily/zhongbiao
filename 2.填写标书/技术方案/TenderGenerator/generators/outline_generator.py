"""
大纲生成器
基于评分标准生成技术方案大纲
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple
try:
    from ..utils.llm_client import get_llm_client
    from ..config import OUTLINE_PROMPT
except ImportError:
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent))
    from utils.llm_client import get_llm_client
    from config import OUTLINE_PROMPT

class OutlineGenerator:
    """大纲生成器类"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.llm_client = get_llm_client()
        
        # 章节优先级权重
        self.section_priorities = {
            '技术架构': 1.0,
            '功能实现': 0.9,
            '技术方案': 0.9,
            '系统设计': 0.8,
            '安全方案': 0.8,
            '性能保障': 0.7,
            '实施方案': 0.7,
            '项目管理': 0.6,
            '服务支持': 0.5,
            '培训方案': 0.4,
            '其他': 0.3
        }
        
        # 常见章节模板
        self.section_templates = {
            '技术架构': {
                'subsections': [
                    '总体架构设计',
                    '技术选型说明',
                    '架构优势分析',
                    '扩展性设计'
                ]
            },
            '功能实现': {
                'subsections': [
                    '核心功能实现',
                    '业务流程设计',
                    '数据处理方案',
                    '用户界面设计'
                ]
            },
            '系统设计': {
                'subsections': [
                    '系统架构',
                    '数据库设计',
                    '接口设计',
                    '安全设计'
                ]
            },
            '安全方案': {
                'subsections': [
                    '安全架构',
                    '权限管理',
                    '数据安全',
                    '网络安全'
                ]
            },
            '性能保障': {
                'subsections': [
                    '性能设计',
                    '负载均衡',
                    '缓存策略',
                    '监控方案'
                ]
            }
        }
    
    def generate_outline(self, 
                        scoring_criteria: List[Dict[str, Any]], 
                        requirements: List[Dict[str, Any]],
                        use_ai: bool = True) -> Dict[str, Any]:
        """
        生成技术方案大纲
        
        Args:
            scoring_criteria: 评分标准列表
            requirements: 需求列表
            use_ai: 是否使用AI生成
            
        Returns:
            大纲数据
        """
        self.logger.info(f"开始生成技术方案大纲: {len(scoring_criteria)} 个评分项")
        
        if use_ai and self.llm_client:
            outline = self._generate_outline_with_ai(scoring_criteria, requirements)
        else:
            outline = self._generate_outline_rule_based(scoring_criteria, requirements)
        
        # 验证和优化大纲
        outline = self._validate_and_optimize_outline(outline)
        
        self.logger.info(f"大纲生成完成: {len(outline.get('sections', []))} 个主要章节")
        return outline
    
    def _generate_outline_with_ai(self, 
                                 scoring_criteria: List[Dict[str, Any]], 
                                 requirements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """使用AI生成大纲"""
        try:
            # 准备评分标准文本
            scoring_text = self._format_scoring_criteria(scoring_criteria)
            
            # 准备需求文本
            requirements_text = self._format_requirements(requirements)
            
            # 调用AI生成大纲
            outline_data = self.llm_client.generate_outline(scoring_text, requirements_text)
            
            if outline_data and 'outline' in outline_data:
                return {
                    'title': '技术方案',
                    'sections': outline_data['outline'],
                    'generation_method': 'ai',
                    'total_sections': len(outline_data['outline'])
                }
            else:
                self.logger.warning("AI生成大纲失败，使用规则基础方法")
                return self._generate_outline_rule_based(scoring_criteria, requirements)
                
        except Exception as e:
            self.logger.error(f"AI生成大纲出错: {e}")
            return self._generate_outline_rule_based(scoring_criteria, requirements)
    
    def _generate_outline_rule_based(self, 
                                   scoring_criteria: List[Dict[str, Any]], 
                                   requirements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """基于规则生成大纲"""
        sections = []
        
        # 按评分标准生成章节
        for i, criterion in enumerate(scoring_criteria):
            section_title = criterion.get('title', f'技术方案 {i+1}')
            section_weight = criterion.get('weight', '10分')
            max_score = criterion.get('max_score', 10)
            
            # 清理章节标题
            clean_title = self._clean_section_title(section_title)
            
            # 生成子章节
            subsections = self._generate_subsections(criterion, requirements)
            
            section = {
                'level': 1,
                'title': clean_title,
                'weight': section_weight,
                'max_score': max_score,
                'priority': self._calculate_section_priority(clean_title, max_score),
                'subsections': subsections,
                'requirements_mapping': self._map_requirements_to_section(clean_title, requirements)
            }
            
            sections.append(section)
        
        # 排序章节
        sections.sort(key=lambda x: x['priority'], reverse=True)
        
        # 添加标准章节（如果缺失）
        sections = self._ensure_standard_sections(sections, requirements)
        
        return {
            'title': '技术方案',
            'sections': sections,
            'generation_method': 'rule_based',
            'total_sections': len(sections)
        }
    
    def _format_scoring_criteria(self, scoring_criteria: List[Dict[str, Any]]) -> str:
        """格式化评分标准文本"""
        text_parts = []
        
        for criterion in scoring_criteria:
            title = criterion.get('title', '未知项目')
            weight = criterion.get('weight', '未知')
            description = criterion.get('description', '')
            
            part = f"评分项目: {title} ({weight})\\n"
            if description:
                part += f"要求: {description}\\n"
            
            text_parts.append(part)
        
        return '\\n'.join(text_parts)
    
    def _format_requirements(self, requirements: List[Dict[str, Any]]) -> str:
        """格式化需求文本"""
        text_parts = []
        
        # 按类别分组需求
        req_by_category = {}
        for req in requirements:
            category = req.get('category', '功能需求')
            if category not in req_by_category:
                req_by_category[category] = []
            req_by_category[category].append(req)
        
        # 格式化输出
        for category, reqs in req_by_category.items():
            text_parts.append(f"\\n{category}:")
            for req in reqs[:5]:  # 限制每类需求数量
                title = req.get('title', '未知需求')
                text_parts.append(f"- {title}")
        
        return '\\n'.join(text_parts)
    
    def _clean_section_title(self, title: str) -> str:
        """清理章节标题"""
        # 去除评分相关字符
        title = re.sub(r'[（(][^)）]*[分][)）]', '', title)
        title = re.sub(r'\\d+分.*', '', title)
        
        # 去除序号
        title = re.sub(r'^[\\d\\.、]+', '', title)
        
        # 去除多余空格和标点
        title = re.sub(r'[：:]', '', title)
        title = title.strip()
        
        # 标题标准化
        title_mapping = {
            '技术架构方案': '技术架构',
            '功能需求实现': '功能实现',
            '系统架构设计': '系统设计',
            '安全保障方案': '安全方案',
            '性能技术方案': '性能保障',
            '实施计划': '实施方案',
            '项目组织': '项目管理',
            '售后服务': '服务支持'
        }
        
        return title_mapping.get(title, title) if title else '技术方案'
    
    def _generate_subsections(self, 
                            criterion: Dict[str, Any], 
                            requirements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """生成子章节"""
        section_title = criterion.get('title', '')
        clean_title = self._clean_section_title(section_title)
        
        subsections = []
        
        # 使用模板生成子章节
        if clean_title in self.section_templates:
            template_subsections = self.section_templates[clean_title]['subsections']
            for i, subsection_title in enumerate(template_subsections):
                subsections.append({
                    'level': 2,
                    'title': subsection_title,
                    'points': self._generate_subsection_points(subsection_title, requirements)
                })
        else:
            # 基于评分标准描述生成子章节
            description = criterion.get('description', '')
            if description:
                subsections = self._extract_subsections_from_description(description)
            
            # 如果没有子章节，生成默认的
            if not subsections:
                subsections = [
                    {
                        'level': 2,
                        'title': f'{clean_title}方案',
                        'points': ['方案概述', '技术实现', '优势特点']
                    },
                    {
                        'level': 2,
                        'title': f'{clean_title}实施',
                        'points': ['实施步骤', '关键技术', '质量保证']
                    }
                ]
        
        return subsections
    
    def _generate_subsection_points(self, subsection_title: str, requirements: List[Dict[str, Any]]) -> List[str]:
        """生成子章节要点"""
        points = []
        
        # 基于子章节标题生成要点
        if '架构' in subsection_title:
            points = ['整体架构设计', '技术选型', '组件划分', '接口定义']
        elif '功能' in subsection_title:
            points = ['功能模块设计', '业务流程', '数据处理', '用户交互']
        elif '安全' in subsection_title:
            points = ['安全策略', '访问控制', '数据加密', '威胁防护']
        elif '性能' in subsection_title:
            points = ['性能指标', '优化策略', '监控方案', '扩展能力']
        elif '实施' in subsection_title:
            points = ['实施计划', '资源配置', '风险控制', '质量管理']
        else:
            points = ['方案设计', '技术实现', '关键特性', '预期效果']
        
        # 结合相关需求
        related_reqs = self._find_related_requirements(subsection_title, requirements)
        for req in related_reqs[:2]:  # 最多添加2个相关需求
            req_title = req.get('title', '')[:20]  # 限制长度
            if req_title not in points:
                points.append(req_title)
        
        return points[:6]  # 限制要点数量
    
    def _calculate_section_priority(self, title: str, max_score: int) -> float:
        """计算章节优先级"""
        base_priority = self.section_priorities.get(title, 0.5)
        score_weight = min(max_score / 20.0, 1.0)  # 分数权重
        
        return base_priority * 0.7 + score_weight * 0.3
    
    def _map_requirements_to_section(self, section_title: str, requirements: List[Dict[str, Any]]) -> List[str]:
        """将需求映射到章节"""
        mapped_reqs = []
        
        # 关键词映射
        keyword_mapping = {
            '技术架构': ['架构', '技术', '系统', '设计'],
            '功能实现': ['功能', '业务', '模块', '实现'],
            '安全方案': ['安全', '权限', '认证', '加密'],
            '性能保障': ['性能', '效率', '响应', '并发'],
            '系统设计': ['系统', '数据库', '接口', '集成']
        }
        
        section_keywords = keyword_mapping.get(section_title, [section_title])
        
        for req in requirements:
            req_text = f"{req.get('title', '')} {req.get('content', '')}".lower()
            
            if any(keyword in req_text for keyword in section_keywords):
                mapped_reqs.append(req['id'])
        
        return mapped_reqs[:5]  # 限制映射数量
    
    def _ensure_standard_sections(self, sections: List[Dict[str, Any]], requirements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """确保包含标准章节"""
        existing_titles = {s['title'] for s in sections}
        standard_sections = ['技术架构', '功能实现', '安全方案']
        
        for standard_title in standard_sections:
            if standard_title not in existing_titles:
                # 添加缺失的标准章节
                section = {
                    'level': 1,
                    'title': standard_title,
                    'weight': '10分',
                    'max_score': 10,
                    'priority': self.section_priorities.get(standard_title, 0.5),
                    'subsections': self._generate_subsections(
                        {'title': standard_title, 'description': ''}, 
                        requirements
                    ),
                    'requirements_mapping': self._map_requirements_to_section(standard_title, requirements),
                    'is_standard': True
                }
                sections.append(section)
        
        return sections
    
    def _extract_subsections_from_description(self, description: str) -> List[Dict[str, Any]]:
        """从描述中提取子章节"""
        subsections = []
        
        # 查找列表项
        list_items = re.findall(r'[\\d]+[、.]([^\\n]+)', description)
        if not list_items:
            list_items = re.findall(r'[（(][\\d]+[）)]([^\\n]+)', description)
        
        for i, item in enumerate(list_items[:4]):  # 最多4个子章节
            item = item.strip()
            if len(item) > 3:
                subsections.append({
                    'level': 2,
                    'title': item[:30],  # 限制标题长度
                    'points': ['方案说明', '技术实现', '关键特性']
                })
        
        return subsections
    
    def _find_related_requirements(self, subsection_title: str, requirements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """查找相关需求"""
        related = []
        title_lower = subsection_title.lower()
        
        for req in requirements:
            req_text = f"{req.get('title', '')} {req.get('content', '')}".lower()
            
            # 简单关键词匹配
            if any(word in req_text for word in title_lower.split() if len(word) > 1):
                related.append(req)
        
        return related[:3]  # 限制相关需求数量
    
    def _validate_and_optimize_outline(self, outline: Dict[str, Any]) -> Dict[str, Any]:
        """验证和优化大纲"""
        sections = outline.get('sections', [])
        
        # 验证章节结构
        validated_sections = []
        for section in sections:
            if self._is_valid_section(section):
                validated_sections.append(section)
        
        # 确保章节数量合理
        if len(validated_sections) < 3:
            self.logger.warning("大纲章节数量过少，添加标准章节")
            # 添加基本章节
        elif len(validated_sections) > 10:
            self.logger.warning("大纲章节数量过多，保留前10个")
            validated_sections = validated_sections[:10]
        
        # 重新编号
        for i, section in enumerate(validated_sections):
            section['order'] = i + 1
        
        outline['sections'] = validated_sections
        outline['total_sections'] = len(validated_sections)
        
        return outline
    
    def _is_valid_section(self, section: Dict[str, Any]) -> bool:
        """验证章节是否有效"""
        required_fields = ['title', 'level']
        
        for field in required_fields:
            if field not in section:
                return False
        
        # 标题不能为空
        if not section['title'].strip():
            return False
        
        # 级别必须合理
        if section['level'] not in [1, 2, 3]:
            return False
        
        return True
    
    def export_outline_to_dict(self, outline: Dict[str, Any]) -> Dict[str, Any]:
        """导出大纲为字典格式"""
        export_data = {
            'title': outline.get('title', '技术方案'),
            'generation_method': outline.get('generation_method', 'unknown'),
            'total_sections': outline.get('total_sections', 0),
            'sections': []
        }
        
        for section in outline.get('sections', []):
            section_data = {
                'order': section.get('order', 0),
                'title': section.get('title', ''),
                'level': section.get('level', 1),
                'weight': section.get('weight', ''),
                'max_score': section.get('max_score', 0),
                'subsections': []
            }
            
            for subsection in section.get('subsections', []):
                subsection_data = {
                    'title': subsection.get('title', ''),
                    'level': subsection.get('level', 2),
                    'points': subsection.get('points', [])
                }
                section_data['subsections'].append(subsection_data)
            
            export_data['sections'].append(section_data)
        
        return export_data


# 全局大纲生成器实例
_outline_generator = None

def get_outline_generator() -> OutlineGenerator:
    """获取全局大纲生成器实例"""
    global _outline_generator
    if _outline_generator is None:
        _outline_generator = OutlineGenerator()
    return _outline_generator