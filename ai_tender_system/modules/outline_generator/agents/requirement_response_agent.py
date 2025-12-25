#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""需求应答智能体 - 按招标书目录动态生成方案"""

import json
import re
from typing import Dict, List, Any, Optional

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
                 content_style: Dict = None,
                 optimize_outline: bool = True) -> Dict:
        """
        按招标书需求生成技术方案

        工作流程:
        1. 需求分析 → requirement_categories[]
        2. AI优化大纲 → outline (新增，默认启用)
        3. 逐章生成内容 → chapters[]
        4. 验证完整性 → coverage_rate

        Args:
            tender_doc: 招标文档文本
            page_count: 目标页数
            content_style: 内容风格配置
            optimize_outline: 是否启用AI大纲优化（默认True）

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

        # ========== 第2步: 大纲生成（AI优化 或 1:1映射） ==========
        if optimize_outline and len(requirement_categories) > 0:
            self.logger.info("【需求应答智能体】启用AI大纲优化...")
            outline = self._optimize_outline_with_ai(
                requirement_categories,
                page_count,
                tender_doc,
                content_style
            )
        else:
            # 降级到原有的1:1映射逻辑
            self.logger.info("【需求应答智能体】使用1:1映射生成大纲...")
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

    def _optimize_outline_with_ai(self, requirement_categories: List[Dict],
                                   page_count: int,
                                   tender_doc: str,
                                   content_style: Dict) -> Dict:
        """
        使用AI优化大纲结构

        优化内容:
        1. 智能合并相关需求类别
        2. 按业务逻辑优化章节顺序
        3. 润色章节标题（更专业）
        4. 可选添加"项目理解与总体设计"引导章节

        Args:
            requirement_categories: 需求分类列表
            page_count: 目标页数
            tender_doc: 招标文档文本
            content_style: 内容风格

        Returns:
            优化后的大纲字典
        """
        # 构建需求分类的简化表示（减少token消耗）
        categories_summary = []
        for cat in requirement_categories:
            categories_summary.append({
                "category": cat.get('category', ''),
                "priority": cat.get('priority', 'normal'),
                "key_points": cat.get('key_points', [])[:10],  # 限制要点数量
                "keywords": cat.get('keywords', [])[:5]
            })

        prompt = f"""你是一位资深的技术方案架构师。请根据以下需求分类，设计一份专业的技术方案大纲。

【需求分类】（共{len(requirement_categories)}个类别）
{json.dumps(categories_summary, ensure_ascii=False, indent=2)}

【招标项目概述】
{tender_doc[:3000]}

【目标页数】{page_count}页

【优化要求】
1. **智能合并**: 可以合并相关性强的需求类别（如"数据安全"和"安全合规"可合并为"安全保障方案"）
2. **逻辑排序**: 按业务逻辑排列章节顺序（核心业务需求在前，运维支撑服务在后）
3. **标题润色**: 章节标题要专业、简洁（去掉"需求"后缀，如"数据服务需求"→"数据服务方案"）
4. **引导章节**: 添加"项目理解与总体设计"作为第一章（占比约10%页数），用于阐述对项目的整体理解和技术架构
5. **需求溯源**: 每个章节必须标注对应的原始需求类别（source_categories），不能凭空创造内容

【严禁添加】
- 商务条款章节（服务期限、违约责任、知识产权、保密条款等）
- 与招标需求无关的通用章节（如"公司简介"、"资质证明"等）

【返回格式】必须是有效的JSON
{{
  "optimized_chapters": [
    {{
      "chapter_number": 1,
      "title": "项目理解与总体设计",
      "source_categories": [],
      "allocated_pages": {int(page_count * 0.1)},
      "description": "阐述对项目的整体理解和技术架构设计",
      "content_hints": ["项目背景理解", "总体技术架构", "技术路线选择"]
    }},
    {{
      "chapter_number": 2,
      "title": "数据服务方案",
      "source_categories": ["数据服务需求", "API接口需求"],
      "allocated_pages": 50,
      "description": "详细说明数据服务的技术实现方案",
      "content_hints": ["三要素验证", "在网状态查询", "号码归属地查询"]
    }}
  ],
  "optimization_notes": "合并了'数据服务需求'和'API接口需求'为'数据服务方案'，新增'项目理解与总体设计'章节"
}}"""

        try:
            response = self._call_llm(prompt)
            result = self._parse_outline_response(response)

            if result and 'optimized_chapters' in result:
                chapters = result['optimized_chapters']

                # 补充每个章节的完整content_hints（从原始需求类别中获取）
                for chapter in chapters:
                    source_cats = chapter.get('source_categories', [])
                    if source_cats:
                        # 合并来源类别的所有key_points
                        all_hints = []
                        for cat in requirement_categories:
                            if cat.get('category') in source_cats:
                                all_hints.extend(cat.get('key_points', []))
                        if all_hints:
                            chapter['content_hints'] = all_hints

                self.logger.info(
                    f"AI大纲优化完成，共 {len(chapters)} 章。"
                    f"优化说明: {result.get('optimization_notes', 'N/A')}"
                )

                return {
                    "chapters": chapters,
                    "total_chapters": len(chapters),
                    "total_pages": page_count,
                    "optimization_notes": result.get('optimization_notes', '')
                }
            else:
                self.logger.warning("AI大纲优化返回格式异常，降级到1:1映射")
                return self._generate_dynamic_outline(
                    requirement_categories, page_count, content_style
                )

        except Exception as e:
            self.logger.error(f"AI大纲优化失败: {e}，降级到1:1映射")
            return self._generate_dynamic_outline(
                requirement_categories, page_count, content_style
            )

    def _parse_outline_response(self, response: str) -> Optional[Dict]:
        """
        解析AI返回的大纲JSON

        Args:
            response: AI响应文本

        Returns:
            解析后的字典，失败返回None
        """
        if not response or not response.strip():
            return None

        # 移除可能的markdown代码块标记
        response = re.sub(r'^```json\s*', '', response.strip())
        response = re.sub(r'\s*```$', '', response.strip())

        # 尝试查找JSON对象
        json_start = response.find('{')
        json_end = response.rfind('}') + 1

        if json_start != -1 and json_end > json_start:
            json_str = response[json_start:json_end]

            try:
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                self.logger.warning(f"JSON解析失败: {e}")
                return None

        return None

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
