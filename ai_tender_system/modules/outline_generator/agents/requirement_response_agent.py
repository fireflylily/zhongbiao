#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""需求应答智能体 - 按招标书目录动态生成方案"""

from typing import Dict, List, Any

from .base_agent import BaseAgent


class RequirementResponseAgent(BaseAgent):
    """
    需求应答智能体

    核心职责:
    1. 智能分析招标文档需求（调用 RequirementAnalyzer）
    2. 根据需求分类动态生成章节
    3. 确保章节与需求一一对应，不添加额外章节
    4. 保证表格内容完整传递（v2.2.0修复）

    对应现有功能:
    - outline_generation.json:analyze_requirements
    - outline_generation.json:generate_outline 的"动态生成章节"原则
    - 继承 v2.2.0 的所有修复
    """

    def __init__(self, model_name: str = "gpt-4o-mini"):
        super().__init__(model_name)
        self.prompt_module = 'requirement_response_agent'

        # 延迟导入避免循环依赖
        from ..requirement_analyzer import RequirementAnalyzer
        self.analyzer = RequirementAnalyzer(model_name=model_name)

    def generate(self, tender_doc: str, page_count: int = 200,
                 content_style: Dict = None) -> Dict:
        """
        按招标书需求生成技术方案

        工作流程:
        1. 需求分析 → requirement_categories[]
        2. 动态生成大纲 → outline
        3. 逐章生成内容 → chapters[]
        4. 验证完整性 → coverage_rate

        Args:
            tender_doc: 招标文档文本
            page_count: 目标页数
            content_style: 内容风格配置

        Returns:
            {
                "outline": {...},
                "chapters": [...],
                "metadata": {...}
            }
        """
        content_style = content_style or {
            'tables': '适量',
            'flowcharts': '流程图',
            'images': '少量'
        }

        self.logger.info("【需求应答智能体】开始分析招标文档...")

        # ========== 第1步: 需求分析 ==========
        analysis_result = self.analyzer.analyze_document(tender_doc)
        requirement_categories = analysis_result.get('requirement_categories', [])

        self.logger.info(
            f"需求分析完成，识别出 {len(requirement_categories)} 个需求类别"
        )

        # ========== 第2步: 动态生成大纲 ==========
        outline = self._generate_dynamic_outline(
            requirement_categories,
            page_count,
            content_style
        )

        # ========== 第3步: 逐章生成内容 ==========
        chapters = []
        for chapter_plan in outline['chapters']:
            chapter_content = self._generate_chapter_content(
                tender_doc=tender_doc,
                chapter_plan=chapter_plan,
                analysis_result=analysis_result,
                content_style=content_style
            )
            chapters.append(chapter_content)

        # ========== 第4步: 验证完整性 ==========
        verification_result = self._verify_completeness(
            chapters,
            requirement_categories
        )

        return {
            "outline": outline,
            "chapters": chapters,
            "metadata": {
                "generation_mode": "按招标书目录写",
                "requirement_categories_count": len(requirement_categories),
                "total_pages": verification_result['estimated_pages'],
                "coverage_rate": verification_result['coverage_rate'],
                "word_count": sum(c['word_count'] for c in chapters)
            }
        }

    def _generate_dynamic_outline(self, requirement_categories: List[Dict],
                                  page_count: int,
                                  content_style: Dict) -> Dict:
        """
        动态生成大纲 - 严格遵循需求分类

        核心原则 (v2.2.0):
        - ❌ 严禁使用固定5章结构（总体设计、需求应答、技术指标、实施方案、服务承诺）
        - ❌ 严禁添加通用商务章节（服务期限、不可抗力、违约责任等）
        - ✅ 章节数量 = requirement_categories 的数量，不多不少
        - ✅ 1级章节标题 = requirement_categories[].category
        - ✅ 2级章节标题 = requirement_categories[].key_points

        Args:
            requirement_categories: 需求分类列表
            page_count: 目标页数
            content_style: 内容风格

        Returns:
            大纲字典
        """
        # 按需求优先级分配页数
        total_priority = sum(
            self._get_priority_weight(cat.get('priority', 'normal'))
            for cat in requirement_categories
        )

        chapters = []
        for i, category in enumerate(requirement_categories):
            priority_weight = self._get_priority_weight(
                category.get('priority', 'normal')
            )
            allocated_pages = int(page_count * priority_weight / total_priority)

            # 获取 content_hints（来自 key_points）
            content_hints = category.get('key_points', [])

            chapters.append({
                "chapter_number": i + 1,
                "title": category['category'],  # 1级章节标题
                "description": category.get('description', ''),
                "allocated_pages": allocated_pages,
                "content_hints": content_hints,  # ✅ 保留所有要点，不截断
                "keywords": category.get('keywords', []),
                "priority": category.get('priority', 'normal')
            })

        self.logger.info(
            f"动态大纲生成完成，共 {len(chapters)} 章 "
            f"(需求类别数: {len(requirement_categories)})"
        )

        return {
            "chapters": chapters,
            "total_chapters": len(chapters),
            "total_pages": page_count
        }

    def _get_priority_weight(self, priority: str) -> int:
        """获取优先级权重"""
        weights = {
            'critical': 3,  # 关键需求，分配3倍页数
            'high': 2,      # 重要需求，分配2倍页数
            'normal': 1,    # 普通需求，分配1倍页数
            'low': 0.5      # 次要需求，分配0.5倍页数
        }
        return weights.get(priority, 1)

    def _generate_chapter_content(self, tender_doc: str,
                                  chapter_plan: Dict,
                                  analysis_result: Dict,
                                  content_style: Dict) -> Dict:
        """
        生成单章内容 - 确保所有 content_hints 都被体现

        继承 v2.2.0 修复:
        - ✅ 保留所有 content_hints，不截断
        - ✅ 提示词明确要求"完整性"
        - ✅ 扩展字数限制（800-1500字）

        Args:
            tender_doc: 招标文档
            chapter_plan: 章节计划
            analysis_result: 需求分析结果
            content_style: 内容风格

        Returns:
            章节内容字典
        """
        content_hints = chapter_plan.get('content_hints', [])
        allocated_pages = chapter_plan.get('allocated_pages', 10)

        # 计算目标字数
        target_words = self.calculate_word_count(
            allocated_pages,
            content_style
        )

        # 构建提示词（继承 proposal_assembler.py 的逻辑）
        prompt = self._build_chapter_prompt(
            chapter_title=chapter_plan['title'],
            chapter_desc=chapter_plan.get('description', ''),
            content_hints=content_hints,  # ✅ 全部传递，不截断
            target_words=target_words,
            tender_doc=tender_doc[:5000],  # 项目上下文
            content_style=content_style
        )

        # 调用 LLM 生成
        response = self._call_llm(prompt)
        generated_content = response.strip()

        return {
            "title": chapter_plan['title'],
            "content": generated_content,
            "word_count": len(generated_content),
            "expected_hints_count": len(content_hints),
            "allocated_pages": allocated_pages
        }

    def _build_chapter_prompt(self, chapter_title: str, chapter_desc: str,
                             content_hints: List[str], target_words: int,
                             tender_doc: str, content_style: Dict) -> str:
        """
        构建章节生成提示词

        继承 proposal_assembler.py:_build_advanced_prompt 的优化

        Args:
            chapter_title: 章节标题
            chapter_desc: 章节描述
            content_hints: 内容要点列表
            target_words: 目标字数
            tender_doc: 招标文档
            content_style: 内容风格

        Returns:
            完整提示词
        """
        # 格式化要点列表
        if content_hints:
            hints_list = '\n'.join([f"  - {hint}" for hint in content_hints])
            if len(content_hints) > 10:
                hints_list += f"\n\n（共 {len(content_hints)} 项要点，请在方案中全部体现，可按类别分组说明）"
        else:
            hints_list = f"  - {chapter_desc}"

        # 内容风格指导
        style_guide = self._get_style_guide(content_style)

        prompt = f"""为"{chapter_title}"撰写 {target_words}字 技术方案应答内容。

【核心要点】
{hints_list}

【项目背景】
{tender_doc}

【撰写要求】
1. **完整性要求（最重要）**: 必须涵盖【核心要点】中列出的所有项，不得遗漏任何一项细节指标
2. **针对性**: 紧密结合招标文档的具体需求，避免泛泛而谈
3. **专业性**: 使用行业术语，体现技术深度
4. **逻辑性**: 结构清晰，层次分明
5. **字数要求**: {target_words}字左右（允许±10%浮动）
6. **内容结构**:
   - 开头段落: 简要概述本章要解决的核心问题
   - 中间段落: 分 ① ② ③ 列举具体解决方案或能力证明（如要点多，可按类别分组）
   - 结尾段落: 总结优势或承诺

{style_guide}

请直接输出方案内容，不需要输出章节标题。"""

        return prompt

    def _get_style_guide(self, content_style: Dict) -> str:
        """生成内容风格指导"""
        guides = []

        if content_style.get('tables') in ['适量', '大量']:
            guides.append("- 适当使用表格展示结构化数据（如：功能清单、技术参数对比）")

        if content_style.get('flowcharts') != '无':
            guides.append("- 对于流程性内容，可标注【此处插入流程图】")

        if content_style.get('images') != '无':
            guides.append("- 对于架构设计、拓扑图等，可标注【此处插入示意图】")

        return '\n'.join(guides) if guides else ''

    def _verify_completeness(self, chapters: List[Dict],
                            requirement_categories: List[Dict]) -> Dict:
        """
        验证完整性

        Args:
            chapters: 生成的章节列表
            requirement_categories: 需求类别列表

        Returns:
            验证结果
        """
        # 收集所有期望的要点
        expected_hints = []
        for category in requirement_categories:
            expected_hints.extend(category.get('key_points', []))

        # 简化的覆盖率检查
        covered_count = 0
        for hint in expected_hints:
            for chapter in chapters:
                if hint in chapter['content']:
                    covered_count += 1
                    break

        coverage_rate = covered_count / len(expected_hints) if expected_hints else 1.0

        # 估算页数
        total_words = sum(c['word_count'] for c in chapters)
        estimated_pages = int(total_words / 700)  # 700字/页

        self.logger.info(f"验证完成，覆盖率: {coverage_rate:.1%}")

        return {
            "estimated_pages": estimated_pages,
            "coverage_rate": coverage_rate
        }
