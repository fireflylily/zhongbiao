#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大纲架构智能体 - OutlineArchitectAgent

基于评分策略和检索到的素材，生成技术方案的详细目录结构：
1. 生成四级目录骨架
2. 为每个章节标注素材引用
3. 分配各章节的目标字数
4. 标注重点章节和得分点

设计原则：
- 目录结构覆盖所有评分点
- 素材引用有据可查
- 字数分配符合权重
"""

import json
import logging
from typing import Dict, List, Any, Optional

from .base_agent import BaseAgent


class OutlineArchitectAgent(BaseAgent):
    """
    大纲架构智能体

    在评分策略和素材检索之后运行，为内容撰写提供详细骨架。
    """

    def __init__(self, model_name: str = "gpt-4o-mini"):
        """
        初始化大纲架构智能体

        Args:
            model_name: LLM 模型名称
        """
        super().__init__(model_name)
        self.prompt_module = 'outline_architect_agent'

    def generate(
        self,
        scoring_strategy: Dict[str, Any],
        materials: Dict[str, Any],
        tender_doc: str,
        page_count: int = 100,
        content_style: Dict = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        生成技术方案大纲

        Args:
            scoring_strategy: 评分策略（来自 ScoringStrategyAgent）
            materials: 检索到的素材（来自 MaterialRetrieverAgent）
            tender_doc: 招标文件内容
            page_count: 目标页数
            content_style: 内容风格配置

        Returns:
            详细大纲结构
        """
        return self.build_outline(
            scoring_strategy=scoring_strategy,
            materials=materials,
            tender_doc=tender_doc,
            page_count=page_count,
            content_style=content_style or {}
        )

    def build_outline(
        self,
        scoring_strategy: Dict[str, Any],
        materials: Dict[str, Any],
        tender_doc: str,
        page_count: int = 100,
        content_style: Dict = None
    ) -> Dict[str, Any]:
        """
        构建详细大纲

        Args:
            scoring_strategy: 评分策略
            materials: 检索到的素材
            tender_doc: 招标文件内容
            page_count: 目标页数
            content_style: 内容风格

        Returns:
            {
                "outline": [...],           # 四级目录结构
                "total_words": 70000,       # 总字数
                "chapter_count": 8,         # 一级章节数
                "material_coverage": 0.85,  # 素材覆盖率
                "scoring_coverage": 0.95,   # 评分点覆盖率
                "metadata": {...}
            }
        """
        self.logger.info("【大纲架构智能体】开始构建技术方案大纲...")

        content_style = content_style or {}

        # 计算目标字数
        total_words = self.calculate_word_count(page_count, content_style)

        # 第1步: 提取评分策略中的维度和重点
        dimension_strategies = scoring_strategy.get('dimension_strategies', [])
        highlights = scoring_strategy.get('highlights', [])
        content_allocation = scoring_strategy.get('content_allocation', {})

        # 第2步: 整理素材库
        material_packages = materials.get('material_packages', [])
        material_index = self._build_material_index(material_packages)

        # 第3步: 生成初始大纲框架
        outline_draft = self._generate_outline_structure(
            dimension_strategies=dimension_strategies,
            tender_doc=tender_doc,
            total_words=total_words,
            content_allocation=content_allocation
        )

        # 第4步: 为各章节标注素材引用
        outline_with_materials = self._assign_materials(
            outline=outline_draft,
            material_index=material_index
        )

        # 第5步: 优化字数分配
        final_outline = self._optimize_word_allocation(
            outline=outline_with_materials,
            total_words=total_words,
            dimension_strategies=dimension_strategies
        )

        # 统计覆盖率
        material_coverage = self._calculate_material_coverage(final_outline, material_index)
        scoring_coverage = self._calculate_scoring_coverage(final_outline, dimension_strategies)

        result = {
            "outline": final_outline,
            "total_words": total_words,
            "chapter_count": len(final_outline),
            "material_coverage": material_coverage,
            "scoring_coverage": scoring_coverage,
            "metadata": {
                "page_count": page_count,
                "content_style": content_style,
                "dimension_count": len(dimension_strategies),
                "material_package_count": len(material_packages)
            }
        }

        self.logger.info(
            f"【大纲架构智能体】大纲生成完成: "
            f"{len(final_outline)}个一级章节, "
            f"目标{total_words}字, "
            f"素材覆盖率{material_coverage:.0%}, "
            f"评分点覆盖率{scoring_coverage:.0%}"
        )

        return result

    def _build_material_index(self, material_packages: List[Dict]) -> Dict[str, List[Dict]]:
        """
        构建素材索引，按类别组织

        Args:
            material_packages: 素材包列表

        Returns:
            按类别组织的素材索引
        """
        index = {}

        for package in material_packages:
            category = package.get('category', 'other')
            if category not in index:
                index[category] = []

            # 添加素材及其元数据
            for material in package.get('materials', []):
                index[category].append({
                    'id': material.get('excerpt_id') or material.get('id'),
                    'title': material.get('chapter_title') or material.get('title'),
                    'content_preview': material.get('content_preview', '')[:200],
                    'quality_score': material.get('quality_score', 0),
                    'source_doc': package.get('source_doc', ''),
                    'scoring_point': package.get('scoring_point', '')
                })

        return index

    def _generate_outline_structure(
        self,
        dimension_strategies: List[Dict],
        tender_doc: str,
        total_words: int,
        content_allocation: Dict
    ) -> List[Dict]:
        """
        生成大纲结构

        Args:
            dimension_strategies: 评分维度策略
            tender_doc: 招标文件
            total_words: 目标字数
            content_allocation: 内容分配建议

        Returns:
            大纲结构列表
        """
        # 构建提示词
        prompt = self._build_outline_prompt(
            dimension_strategies=dimension_strategies,
            tender_doc=tender_doc[:8000],  # 限制长度
            total_words=total_words,
            content_allocation=content_allocation
        )

        # 调用LLM生成大纲
        response = self._call_llm(prompt, response_format="json_object")
        result = self._parse_json_response(response)

        outline = result.get('outline', [])

        # 如果LLM返回为空，使用默认模板
        if not outline:
            self.logger.warning("LLM未返回有效大纲，使用默认模板")
            outline = self._get_default_outline(dimension_strategies, total_words)

        return outline

    def _build_outline_prompt(
        self,
        dimension_strategies: List[Dict],
        tender_doc: str,
        total_words: int,
        content_allocation: Dict
    ) -> str:
        """构建大纲生成提示词"""

        # 整理评分维度信息
        dimensions_text = ""
        for i, dim in enumerate(dimension_strategies, 1):
            dimensions_text += f"""
{i}. {dim.get('dimension', '未知维度')} (权重: {dim.get('weight', 0)}分)
   - 得分预估: {dim.get('estimated_score', 0)}/{dim.get('weight', 0)}
   - 策略: {dim.get('strategy', '')}
   - 重点: {', '.join(dim.get('key_points', [])[:3])}
"""

        prompt = f"""你是一位资深的技术方案架构师，请根据以下信息生成技术方案的详细目录结构。

## 招标文件摘要
{tender_doc[:3000]}

## 评分维度及策略
{dimensions_text}

## 内容分配建议
{json.dumps(content_allocation, ensure_ascii=False, indent=2) if content_allocation else '无特殊要求'}

## 要求

1. **目录层级**: 生成4级目录结构
   - 第1级: 主章节（如"第一章 项目理解与总体方案"）
   - 第2级: 子章节
   - 第3级: 小节
   - 第4级: 具体内容点

2. **目标字数**: 总计约 {total_words} 字

3. **覆盖要求**:
   - 必须覆盖所有评分维度
   - 高权重维度分配更多篇幅
   - 每个评分点都应有对应章节

4. **结构规范**:
   - 每个章节包含: id, title, level, target_words, scoring_points, children
   - scoring_points: 关联的评分点名称列表
   - 章节编号使用标准格式（1, 1.1, 1.1.1, 1.1.1.1）

## 输出格式

```json
{{
    "outline": [
        {{
            "id": "1",
            "title": "第一章 项目理解与总体方案",
            "level": 1,
            "target_words": 8000,
            "scoring_points": ["技术方案完整性", "需求理解"],
            "children": [
                {{
                    "id": "1.1",
                    "title": "项目背景分析",
                    "level": 2,
                    "target_words": 2000,
                    "scoring_points": ["需求理解"],
                    "children": [...]
                }}
            ]
        }}
    ]
}}
```

请生成完整的技术方案目录结构。"""

        return prompt

    def _get_default_outline(self, dimension_strategies: List[Dict], total_words: int) -> List[Dict]:
        """获取默认大纲模板"""

        # 标准技术方案章节
        default_chapters = [
            ("项目理解与需求分析", 0.10, ["需求理解"]),
            ("总体解决方案", 0.15, ["技术方案"]),
            ("详细技术方案", 0.25, ["技术方案", "功能设计"]),
            ("系统架构设计", 0.12, ["架构设计"]),
            ("安全保障方案", 0.10, ["安全方案"]),
            ("项目实施方案", 0.10, ["实施方案"]),
            ("运维服务方案", 0.08, ["售后服务"]),
            ("项目管理方案", 0.05, ["项目管理"]),
            ("公司实力与成功案例", 0.05, ["企业资质", "项目经验"]),
        ]

        outline = []
        for i, (title, ratio, points) in enumerate(default_chapters, 1):
            chapter_words = int(total_words * ratio)
            outline.append({
                "id": str(i),
                "title": f"第{self._num_to_chinese(i)}章 {title}",
                "level": 1,
                "target_words": chapter_words,
                "scoring_points": points,
                "children": []
            })

        return outline

    def _num_to_chinese(self, num: int) -> str:
        """数字转中文"""
        chinese_nums = ['零', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十']
        if num <= 10:
            return chinese_nums[num]
        elif num < 20:
            return f"十{chinese_nums[num - 10]}" if num > 10 else "十"
        else:
            return str(num)

    def _assign_materials(
        self,
        outline: List[Dict],
        material_index: Dict[str, List[Dict]]
    ) -> List[Dict]:
        """
        为大纲章节分配素材引用

        Args:
            outline: 大纲结构
            material_index: 素材索引

        Returns:
            带素材引用的大纲
        """
        def assign_to_chapter(chapter: Dict) -> Dict:
            """递归为章节分配素材"""
            chapter = chapter.copy()

            # 根据章节标题和评分点匹配素材
            title = chapter.get('title', '')
            scoring_points = chapter.get('scoring_points', [])

            matched_materials = []

            # 按评分点匹配
            for point in scoring_points:
                point_lower = point.lower()
                for category, materials in material_index.items():
                    for material in materials:
                        if (point_lower in material.get('title', '').lower() or
                            point_lower in material.get('scoring_point', '').lower()):
                            if material not in matched_materials:
                                matched_materials.append(material)

            # 按章节标题关键词匹配
            title_keywords = self._extract_keywords(title)
            for keyword in title_keywords:
                for category, materials in material_index.items():
                    for material in materials:
                        if keyword in material.get('title', ''):
                            if material not in matched_materials:
                                matched_materials.append(material)

            # 限制每个章节的素材数量
            matched_materials = sorted(
                matched_materials,
                key=lambda x: x.get('quality_score', 0),
                reverse=True
            )[:5]

            chapter['materials'] = matched_materials
            chapter['material_count'] = len(matched_materials)

            # 递归处理子章节
            if chapter.get('children'):
                chapter['children'] = [
                    assign_to_chapter(child) for child in chapter['children']
                ]

            return chapter

        return [assign_to_chapter(ch) for ch in outline]

    def _extract_keywords(self, title: str) -> List[str]:
        """从标题提取关键词"""
        # 移除常见前缀
        prefixes = ['第一章', '第二章', '第三章', '第四章', '第五章',
                    '第六章', '第七章', '第八章', '第九章', '第十章']
        for prefix in prefixes:
            title = title.replace(prefix, '')

        # 提取有意义的词
        keywords = []
        keyword_patterns = [
            '方案', '设计', '架构', '实施', '运维', '安全', '管理',
            '需求', '分析', '服务', '保障', '系统', '技术', '项目',
            '团队', '案例', '经验', '资质'
        ]

        for pattern in keyword_patterns:
            if pattern in title:
                keywords.append(pattern)

        return keywords

    def _optimize_word_allocation(
        self,
        outline: List[Dict],
        total_words: int,
        dimension_strategies: List[Dict]
    ) -> List[Dict]:
        """
        优化字数分配

        Args:
            outline: 大纲结构
            total_words: 目标总字数
            dimension_strategies: 评分维度策略

        Returns:
            优化后的大纲
        """
        # 计算当前分配的总字数
        current_total = sum(ch.get('target_words', 0) for ch in outline)

        if current_total == 0:
            # 如果没有分配字数，按平均分配
            avg_words = total_words // len(outline) if outline else 0
            for ch in outline:
                ch['target_words'] = avg_words
            return outline

        # 按比例调整
        ratio = total_words / current_total if current_total > 0 else 1

        def adjust_words(chapter: Dict) -> Dict:
            chapter = chapter.copy()
            chapter['target_words'] = int(chapter.get('target_words', 0) * ratio)

            if chapter.get('children'):
                chapter['children'] = [adjust_words(child) for child in chapter['children']]

            return chapter

        return [adjust_words(ch) for ch in outline]

    def _calculate_material_coverage(
        self,
        outline: List[Dict],
        material_index: Dict[str, List[Dict]]
    ) -> float:
        """计算素材覆盖率"""
        total_materials = sum(len(materials) for materials in material_index.values())
        if total_materials == 0:
            return 0.0

        used_material_ids = set()

        def collect_materials(chapter: Dict):
            for material in chapter.get('materials', []):
                used_material_ids.add(material.get('id'))
            for child in chapter.get('children', []):
                collect_materials(child)

        for ch in outline:
            collect_materials(ch)

        return len(used_material_ids) / total_materials if total_materials > 0 else 0.0

    def _calculate_scoring_coverage(
        self,
        outline: List[Dict],
        dimension_strategies: List[Dict]
    ) -> float:
        """计算评分点覆盖率"""
        all_scoring_points = set()
        for dim in dimension_strategies:
            all_scoring_points.add(dim.get('dimension', ''))
            for point in dim.get('key_points', []):
                all_scoring_points.add(point)

        if not all_scoring_points:
            return 1.0

        covered_points = set()

        def collect_points(chapter: Dict):
            for point in chapter.get('scoring_points', []):
                covered_points.add(point)
            for child in chapter.get('children', []):
                collect_points(child)

        for ch in outline:
            collect_points(ch)

        # 计算覆盖率（模糊匹配）
        covered_count = 0
        for target in all_scoring_points:
            target_lower = target.lower()
            for covered in covered_points:
                if target_lower in covered.lower() or covered.lower() in target_lower:
                    covered_count += 1
                    break

        return covered_count / len(all_scoring_points) if all_scoring_points else 1.0

    def refine_outline(
        self,
        outline: Dict[str, Any],
        feedback: str
    ) -> Dict[str, Any]:
        """
        根据反馈优化大纲

        Args:
            outline: 当前大纲
            feedback: 用户或审核反馈

        Returns:
            优化后的大纲
        """
        prompt = f"""请根据以下反馈优化技术方案大纲。

## 当前大纲
{json.dumps(outline.get('outline', [])[:3], ensure_ascii=False, indent=2)}
... (共{outline.get('chapter_count', 0)}个章节)

## 反馈意见
{feedback}

## 要求
1. 保持原有结构的合理部分
2. 针对反馈进行调整
3. 确保评分点覆盖率不下降
4. 返回完整的优化后大纲

请返回JSON格式的优化后大纲。"""

        response = self._call_llm(prompt, response_format="json_object")
        result = self._parse_json_response(response)

        if result.get('outline'):
            outline['outline'] = result['outline']
            outline['refined'] = True

        return outline
