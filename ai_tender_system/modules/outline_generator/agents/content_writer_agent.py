#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
内容撰写智能体 - ContentWriterAgent

基于大纲结构和检索到的素材，生成技术方案的具体内容：
1. 逐章节生成内容
2. 整合素材，确保内容有据可查
3. 控制字数，符合目标要求
4. 保持语言风格一致性

设计原则：
- 内容基于真实素材，不编造
- 技术描述专业、准确
- 语言风格统一、正式
- 支持流式生成
"""

import json
import logging
from typing import Dict, List, Any, Optional, Generator

from .base_agent import BaseAgent


class ContentWriterAgent(BaseAgent):
    """
    内容撰写智能体

    在大纲生成之后运行，逐章节生成技术方案内容。
    """

    def __init__(self, model_name: str = "gpt-4o-mini"):
        """
        初始化内容撰写智能体

        Args:
            model_name: LLM 模型名称
        """
        super().__init__(model_name)
        self.prompt_module = 'content_writer_agent'

    def generate(
        self,
        outline: Dict[str, Any],
        materials: Dict[str, Any],
        tender_doc: str,
        company_profile: Dict = None,
        content_style: Dict = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        生成完整技术方案内容

        Args:
            outline: 大纲结构（来自 OutlineArchitectAgent）
            materials: 检索到的素材（来自 MaterialRetrieverAgent）
            tender_doc: 招标文件内容
            company_profile: 公司信息（可选）
            content_style: 内容风格配置

        Returns:
            完整的技术方案内容
        """
        return self.write_proposal(
            outline=outline,
            materials=materials,
            tender_doc=tender_doc,
            company_profile=company_profile or {},
            content_style=content_style or {}
        )

    def write_proposal(
        self,
        outline: Dict[str, Any],
        materials: Dict[str, Any],
        tender_doc: str,
        company_profile: Dict = None,
        content_style: Dict = None,
        project_name: str = '',
        customer_name: str = ''
    ) -> Dict[str, Any]:
        """
        撰写完整技术方案

        Args:
            outline: 大纲结构
            materials: 素材
            tender_doc: 招标文件
            company_profile: 公司信息
            content_style: 内容风格
            project_name: 项目名称（从数据库获取）
            customer_name: 客户名称/招标方（从数据库获取）

        Returns:
            {
                "chapters": [...],          # 章节内容列表
                "total_words": 72000,       # 实际总字数
                "material_usage": {...},    # 素材使用情况
                "quality_metrics": {...}    # 质量指标
            }
        """
        self.logger.info("【内容撰写智能体】开始撰写技术方案...")

        content_style = content_style or {}
        company_profile = company_profile or {}

        # 准备素材索引
        material_index = self._prepare_material_index(materials)

        # 提取项目背景信息（优先使用传入的参数）
        project_context = self._extract_project_context(
            tender_doc[:5000],
            project_name=project_name,
            customer_name=customer_name
        )

        # 逐章节生成内容
        chapters = []
        total_words = 0
        material_usage = {}

        outline_chapters = outline.get('outline', [])

        for i, chapter in enumerate(outline_chapters):
            self.logger.info(f"  撰写章节 {i + 1}/{len(outline_chapters)}: {chapter.get('title', '')}")

            chapter_content = self._write_chapter(
                chapter=chapter,
                material_index=material_index,
                project_context=project_context,
                company_profile=company_profile,
                content_style=content_style,
                chapter_index=i
            )

            chapters.append(chapter_content)
            total_words += chapter_content.get('actual_words', 0)

            # 记录素材使用
            for material_id in chapter_content.get('used_materials', []):
                material_usage[material_id] = material_usage.get(material_id, 0) + 1

        # 计算质量指标
        quality_metrics = self._calculate_quality_metrics(
            chapters=chapters,
            outline=outline,
            material_usage=material_usage
        )

        result = {
            "chapters": chapters,
            "total_words": total_words,
            "material_usage": material_usage,
            "quality_metrics": quality_metrics
        }

        self.logger.info(
            f"【内容撰写智能体】技术方案撰写完成: "
            f"{len(chapters)}个章节, "
            f"共{total_words}字, "
            f"使用{len(material_usage)}个素材"
        )

        return result

    def write_proposal_stream(
        self,
        outline: Dict[str, Any],
        materials: Dict[str, Any],
        tender_doc: str,
        company_profile: Dict = None,
        content_style: Dict = None,
        project_name: str = '',
        customer_name: str = ''
    ) -> Generator[Dict[str, Any], None, None]:
        """
        流式撰写技术方案

        Args:
            outline: 大纲结构
            materials: 素材
            tender_doc: 招标文件
            company_profile: 公司信息
            content_style: 内容风格
            project_name: 项目名称（从数据库获取）
            customer_name: 客户名称/招标方（从数据库获取）

        Yields:
            章节内容（逐章节输出）
        """
        content_style = content_style or {}
        company_profile = company_profile or {}

        material_index = self._prepare_material_index(materials)
        project_context = self._extract_project_context(
            tender_doc[:5000],
            project_name=project_name,
            customer_name=customer_name
        )

        outline_chapters = outline.get('outline', [])
        total_chapters = len(outline_chapters)

        for i, chapter in enumerate(outline_chapters):
            # 发送进度信息
            yield {
                "type": "progress",
                "chapter_index": i,
                "total_chapters": total_chapters,
                "chapter_title": chapter.get('title', ''),
                "status": "writing"
            }

            # 生成章节内容
            chapter_content = self._write_chapter(
                chapter=chapter,
                material_index=material_index,
                project_context=project_context,
                company_profile=company_profile,
                content_style=content_style,
                chapter_index=i
            )

            # 发送章节内容
            yield {
                "type": "chapter",
                "chapter_index": i,
                "chapter_content": chapter_content
            }

        # 发送完成信息
        yield {
            "type": "complete",
            "total_chapters": total_chapters
        }

    def _prepare_material_index(self, materials: Dict[str, Any]) -> Dict[str, Dict]:
        """
        准备素材索引（按ID索引）

        Args:
            materials: 素材数据

        Returns:
            素材索引字典
        """
        index = {}

        for package in materials.get('material_packages', []):
            for material in package.get('materials', []):
                material_id = material.get('excerpt_id') or material.get('id')
                if material_id:
                    index[str(material_id)] = {
                        'id': material_id,
                        'title': material.get('chapter_title') or material.get('title'),
                        'content': material.get('content', ''),
                        'content_preview': material.get('content_preview', ''),
                        'quality_score': material.get('quality_score', 0),
                        'source_doc': package.get('source_doc', ''),
                        'category': package.get('category', '')
                    }

        return index

    def _extract_project_context(
        self,
        tender_doc: str,
        project_name: str = '',
        customer_name: str = ''
    ) -> Dict[str, str]:
        """
        从招标文件提取项目背景信息，优先使用传入的参数

        Args:
            tender_doc: 招标文件内容
            project_name: 项目名称（从数据库获取，优先使用）
            customer_name: 客户名称（从数据库获取，优先使用）

        Returns:
            项目背景信息
        """
        # 优先使用传入的参数
        context = {
            'project_name': project_name,
            'customer_name': customer_name,
            'project_type': '',
            'key_requirements': []
        }

        # 如果没有传入项目名称，尝试从文档提取
        if not context['project_name'] and '项目名称' in tender_doc:
            start = tender_doc.find('项目名称')
            end = tender_doc.find('\n', start)
            if end > start:
                context['project_name'] = tender_doc[start:end].replace('项目名称', '').strip(': ：')

        # 如果没有传入客户名称，尝试从文档提取
        if not context['customer_name']:
            for keyword in ['采购人', '招标人', '甲方']:
                if keyword in tender_doc:
                    start = tender_doc.find(keyword)
                    end = tender_doc.find('\n', start)
                    if end > start:
                        context['customer_name'] = tender_doc[start:end].replace(keyword, '').strip(': ：')
                        break

        # 记录提取结果
        self.logger.info(f"项目背景信息: project_name={context['project_name']}, customer_name={context['customer_name']}")

        return context

    def _write_chapter(
        self,
        chapter: Dict,
        material_index: Dict[str, Dict],
        project_context: Dict,
        company_profile: Dict,
        content_style: Dict,
        chapter_index: int
    ) -> Dict[str, Any]:
        """
        撰写单个章节

        Args:
            chapter: 章节大纲
            material_index: 素材索引
            project_context: 项目背景
            company_profile: 公司信息
            content_style: 内容风格
            chapter_index: 章节序号

        Returns:
            章节内容
        """
        title = chapter.get('title', '')
        target_words = chapter.get('target_words', 2000)
        scoring_points = chapter.get('scoring_points', [])
        chapter_materials = chapter.get('materials', [])

        # 收集该章节可用的素材内容
        available_materials = []
        for mat_ref in chapter_materials:
            mat_id = str(mat_ref.get('id', ''))
            if mat_id in material_index:
                available_materials.append(material_index[mat_id])

        # 构建提示词
        prompt = self._build_chapter_prompt(
            title=title,
            target_words=target_words,
            scoring_points=scoring_points,
            materials=available_materials,
            project_context=project_context,
            company_profile=company_profile,
            content_style=content_style,
            children=chapter.get('children', [])
        )

        # 调用LLM生成内容
        response = self._call_llm(prompt, response_format="json_object")
        result = self._parse_json_response(response)

        content = result.get('content', '')
        sections = result.get('sections', [])

        # 如果有子章节，递归生成
        child_contents = []
        if chapter.get('children'):
            for child in chapter['children']:
                child_content = self._write_chapter(
                    chapter=child,
                    material_index=material_index,
                    project_context=project_context,
                    company_profile=company_profile,
                    content_style=content_style,
                    chapter_index=chapter_index
                )
                child_contents.append(child_content)

        # 计算实际字数
        actual_words = len(content)
        for child in child_contents:
            actual_words += child.get('actual_words', 0)

        return {
            "id": chapter.get('id', ''),
            "title": title,
            "level": chapter.get('level', 1),
            "content": content,
            "sections": sections,
            "children": child_contents,
            "target_words": target_words,
            "actual_words": actual_words,
            "scoring_points": scoring_points,
            "used_materials": [m.get('id') for m in available_materials],
            "quality_indicators": result.get('quality_indicators', {})
        }

    def _build_chapter_prompt(
        self,
        title: str,
        target_words: int,
        scoring_points: List[str],
        materials: List[Dict],
        project_context: Dict,
        company_profile: Dict,
        content_style: Dict,
        children: List[Dict]
    ) -> str:
        """构建章节内容生成提示词"""

        # 准备素材文本
        materials_text = ""
        if materials:
            materials_text = "\n\n## 可参考的素材\n"
            for i, mat in enumerate(materials[:5], 1):  # 最多5个素材
                materials_text += f"""
### 素材{i}: {mat.get('title', '')}
来源: {mat.get('source_doc', '')}
内容:
{mat.get('content', mat.get('content_preview', ''))[:1500]}

"""

        # 准备子章节提示
        children_text = ""
        if children:
            children_text = "\n\n## 子章节结构\n"
            for child in children:
                children_text += f"- {child.get('id', '')}: {child.get('title', '')} (目标{child.get('target_words', 500)}字)\n"

        # 内容风格说明
        style_text = ""
        if content_style:
            style_text = f"""
## 内容风格要求
- 表格使用: {content_style.get('tables', '适量')}
- 流程图: {content_style.get('flowcharts', '适量')}
- 配图: {content_style.get('images', '少量')}
"""

        prompt = f"""你是一位专业的技术方案撰写专家，请为以下章节撰写内容。

## 章节信息
- 章节标题: {title}
- 目标字数: {target_words}字
- 关联评分点: {', '.join(scoring_points) if scoring_points else '无特定评分点'}

## 项目背景
- 项目名称: {project_context.get('project_name', '(待填写)')}
- 客户名称: {project_context.get('customer_name', '(待填写)')}
{materials_text}
{children_text}
{style_text}

## 撰写要求

1. **标题格式（重要）**:
   - **禁止在内容开头重复章节标题**（系统会自动添加标题）
   - 直接从正文内容开始撰写
   - 子节标题使用纯文本格式，不要使用 Markdown 的 # 或 ## 格式
   - 子节标题格式示例："4.1 系统架构"（不是 "#### 4.1 系统架构"）

2. **内容质量**:
   - 必须基于提供的素材进行整合和改写
   - 禁止编造不存在的功能或承诺
   - 技术描述要专业、准确
   - 语言风格要正式、统一

3. **结构要求**:
   - 如果有子章节，只生成本级章节的引导内容（约200字）
   - 如果没有子章节，生成完整的章节内容
   - 内容要有逻辑性和层次感

4. **字数控制**:
   - 严格控制在目标字数的±10%范围内
   - 确保内容充实，避免空洞的套话

5. **评分点覆盖**:
   - 确保关联的评分点在内容中得到充分响应
   - 突出产品优势和差异化价值

## 输出格式

```json
{{
    "content": "章节正文内容...",
    "sections": [
        {{
            "title": "小节标题",
            "content": "小节内容..."
        }}
    ],
    "quality_indicators": {{
        "material_usage_rate": 0.8,
        "scoring_point_coverage": 0.9,
        "professionalism": "high"
    }}
}}
```

请生成章节内容。"""

        return prompt

    def _calculate_quality_metrics(
        self,
        chapters: List[Dict],
        outline: Dict,
        material_usage: Dict
    ) -> Dict[str, Any]:
        """
        计算质量指标

        Args:
            chapters: 生成的章节列表
            outline: 原始大纲
            material_usage: 素材使用情况

        Returns:
            质量指标
        """
        # 计算字数达成率
        target_total = outline.get('total_words', 0)
        actual_total = sum(ch.get('actual_words', 0) for ch in chapters)
        word_achievement = actual_total / target_total if target_total > 0 else 0

        # 计算素材使用率
        total_materials_available = len(material_usage)
        materials_used = sum(1 for count in material_usage.values() if count > 0)
        material_usage_rate = materials_used / total_materials_available if total_materials_available > 0 else 0

        # 计算章节完成率
        total_chapters = len(outline.get('outline', []))
        completed_chapters = len([ch for ch in chapters if ch.get('content')])
        completion_rate = completed_chapters / total_chapters if total_chapters > 0 else 0

        return {
            "word_achievement": round(word_achievement, 2),
            "actual_words": actual_total,
            "target_words": target_total,
            "material_usage_rate": round(material_usage_rate, 2),
            "completion_rate": round(completion_rate, 2),
            "chapter_count": len(chapters),
            "average_chapter_words": actual_total // len(chapters) if chapters else 0
        }

    def rewrite_chapter(
        self,
        chapter: Dict,
        feedback: str,
        materials: List[Dict] = None
    ) -> Dict[str, Any]:
        """
        根据反馈重写章节

        Args:
            chapter: 当前章节内容
            feedback: 反馈意见
            materials: 补充素材（可选）

        Returns:
            重写后的章节
        """
        prompt = f"""请根据以下反馈重写章节内容。

## 当前章节
标题: {chapter.get('title', '')}
内容:
{chapter.get('content', '')[:3000]}

## 反馈意见
{feedback}

## 要求
1. 保持原有内容的合理部分
2. 针对反馈进行改进
3. 保持字数在目标范围内（{chapter.get('target_words', 2000)}字左右）
4. 确保评分点覆盖不下降

请返回JSON格式的重写内容。"""

        response = self._call_llm(prompt, response_format="json_object")
        result = self._parse_json_response(response)

        if result.get('content'):
            chapter['content'] = result['content']
            chapter['actual_words'] = len(result['content'])
            chapter['rewritten'] = True

        return chapter

    def enhance_with_tables(
        self,
        chapter: Dict,
        table_type: str = "comparison"
    ) -> Dict[str, Any]:
        """
        为章节添加表格

        Args:
            chapter: 章节内容
            table_type: 表格类型（comparison, features, timeline, etc.）

        Returns:
            增强后的章节
        """
        prompt = f"""请为以下章节内容生成一个合适的表格。

## 章节内容
{chapter.get('content', '')[:2000]}

## 表格类型
{table_type}

## 要求
1. 表格内容要与章节主题相关
2. 表格格式使用Markdown
3. 表格要有标题和说明
4. 数据要准确、有意义

请返回JSON格式的结果，包含table_markdown和table_caption字段。"""

        response = self._call_llm(prompt, response_format="json_object")
        result = self._parse_json_response(response)

        if result.get('table_markdown'):
            # 将表格添加到内容中
            table_content = f"\n\n{result.get('table_caption', '')}\n\n{result['table_markdown']}\n\n"
            chapter['content'] = chapter.get('content', '') + table_content
            chapter['tables'] = chapter.get('tables', []) + [{
                'type': table_type,
                'markdown': result['table_markdown'],
                'caption': result.get('table_caption', '')
            }]

        return chapter
