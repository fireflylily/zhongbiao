#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""模板智能体 - 使用固定模板生成方案"""

from typing import Dict, List, Any

from .base_agent import BaseAgent


class TemplateAgent(BaseAgent):
    """
    模板智能体

    核心职责:
    1. 提供多种预定义模板
    2. 将招标需求映射到模板章节
    3. 快速生成符合固定格式的方案

    使用场景:
    - 企业有自己的标准技术方案模板
    - 需要生成符合特定行业规范的方案
    - 快速起草初稿，后续人工调整
    """

    # 预定义模板库
    TEMPLATES = {
        "政府采购标准": {
            "name": "政府采购标准模板",
            "description": "适用于政府采购项目的标准5章结构",
            "chapters": [
                {"title": "第一章 总体设计方案", "page_ratio": 0.20},
                {"title": "第二章 需求应答", "page_ratio": 0.30},
                {"title": "第三章 技术指标", "page_ratio": 0.20},
                {"title": "第四章 实施方案", "page_ratio": 0.20},
                {"title": "第五章 服务承诺", "page_ratio": 0.10}
            ]
        },
        "软件开发项目": {
            "name": "软件开发项目模板",
            "description": "适用于软件开发和信息化项目",
            "chapters": [
                {"title": "第一章 项目概述", "page_ratio": 0.10},
                {"title": "第二章 需求分析", "page_ratio": 0.15},
                {"title": "第三章 系统设计", "page_ratio": 0.20},
                {"title": "第四章 开发实施", "page_ratio": 0.15},
                {"title": "第五章 测试方案", "page_ratio": 0.15},
                {"title": "第六章 部署上线", "page_ratio": 0.10},
                {"title": "第七章 运维保障", "page_ratio": 0.10},
                {"title": "第八章 培训交付", "page_ratio": 0.05}
            ]
        },
        "ISO质量体系": {
            "name": "ISO质量体系模板",
            "description": "适用于质量管理体系认证项目",
            "chapters": [
                {"title": "第一章 质量方针与目标", "page_ratio": 0.15},
                {"title": "第二章 质量目标", "page_ratio": 0.15},
                {"title": "第三章 过程控制", "page_ratio": 0.25},
                {"title": "第四章 文档管理", "page_ratio": 0.15},
                {"title": "第五章 持续改进", "page_ratio": 0.15},
                {"title": "第六章 管理评审", "page_ratio": 0.15}
            ]
        }
    }

    def __init__(self, model_name: str = "gpt-4o-mini"):
        super().__init__(model_name)
        self.prompt_module = 'template_agent'

    def generate(self, tender_doc: str, template_name: str = "政府采购标准",
                 page_count: int = 200, content_style: Dict = None) -> Dict:
        """
        使用模板生成技术方案

        Args:
            tender_doc: 招标文档文本
            template_name: 模板名称（"政府采购标准" | "软件开发项目" | "ISO质量体系"）
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

        # ========== 第1步: 加载模板 ==========
        template = self._load_template(template_name)

        # ========== 第2步: 智能映射需求到模板章节 ==========
        self.logger.info(f"【模板智能体】使用模板: {template['name']}")

        mapped_outline = self._map_requirements_to_template(
            template,
            tender_doc,
            page_count
        )

        # ========== 第3步: 逐章生成内容 ==========
        chapters = []
        for chapter_plan in mapped_outline['chapters']:
            chapter_content = self._generate_template_chapter(
                tender_doc=tender_doc,
                chapter_plan=chapter_plan,
                content_style=content_style
            )
            chapters.append(chapter_content)

        return {
            "outline": mapped_outline,
            "chapters": chapters,
            "metadata": {
                "generation_mode": "使用固定模板",
                "template_name": template['name'],
                "total_chapters": len(chapters),
                "total_pages": sum(c['allocated_pages'] for c in mapped_outline['chapters']),
                "word_count": sum(c['word_count'] for c in chapters)
            }
        }

    def _load_template(self, template_name: str) -> Dict:
        """
        加载预定义模板

        Args:
            template_name: 模板名称

        Returns:
            模板字典

        Raises:
            ValueError: 模板不存在
        """
        if template_name not in self.TEMPLATES:
            available = ', '.join(self.TEMPLATES.keys())
            raise ValueError(
                f"未知模板: {template_name}。可用模板: {available}"
            )

        return self.TEMPLATES[template_name]

    def _map_requirements_to_template(self, template: Dict,
                                     tender_doc: str,
                                     page_count: int) -> Dict:
        """
        智能映射：将招标需求映射到模板章节

        核心逻辑:
        1. 使用 LLM 分析招标文档
        2. 为每个模板章节提取相关的需求点
        3. 生成 content_hints

        Args:
            template: 模板字典
            tender_doc: 招标文档
            page_count: 目标页数

        Returns:
            映射后的大纲
        """
        chapters = []

        for i, template_chapter in enumerate(template['chapters']):
            allocated_pages = int(page_count * template_chapter['page_ratio'])

            # 使用 LLM 提取该章节的相关需求
            content_hints = self._extract_hints_for_chapter(
                chapter_title=template_chapter['title'],
                tender_doc=tender_doc
            )

            chapters.append({
                "chapter_number": i + 1,
                "title": template_chapter['title'],
                "allocated_pages": allocated_pages,
                "content_hints": content_hints,
                "template_based": True
            })

        return {
            "chapters": chapters,
            "template_name": template['name'],
            "total_pages": page_count
        }

    def _extract_hints_for_chapter(self, chapter_title: str,
                                   tender_doc: str) -> List[str]:
        """
        为模板章节提取相关需求点

        示例:
        章节: "第二章 需求应答"
        → AI提取: ["功能性需求", "性能需求", "安全需求", "可靠性需求"]

        Args:
            chapter_title: 章节标题
            tender_doc: 招标文档

        Returns:
            要点列表
        """
        # 构建提示词
        prompt = f"""请从以下招标文档中，提取与【{chapter_title}】相关的需求点。

【招标文档】
{tender_doc[:10000]}

【输出格式】
请以JSON格式返回，格式如下：
{{
  "content_hints": [
    "要点1",
    "要点2",
    "要点3"
  ]
}}

【要求】
1. 提取与章节主题相关的具体需求
2. 每个要点简洁明了（10-20字）
3. 数量: 3-8个要点
4. 如果招标文档中没有明确相关内容，则根据章节标题推断合理要点"""

        try:
            # 调用 LLM
            response = self._call_llm(prompt, response_format="json_object")

            # 解析返回的要点列表
            hints_data = self._parse_json_response(response)
            hints = hints_data.get('content_hints', [])

            self.logger.info(
                f"为章节 '{chapter_title}' 提取到 {len(hints)} 个要点"
            )

            return hints

        except Exception as e:
            self.logger.warning(f"提取要点失败: {e}，使用默认要点")
            # 返回默认要点
            return [f"{chapter_title}的具体实施方案"]

    def _generate_template_chapter(self, tender_doc: str,
                                   chapter_plan: Dict,
                                   content_style: Dict) -> Dict:
        """
        生成模板章节内容

        Args:
            tender_doc: 招标文档
            chapter_plan: 章节计划
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

        # 构建提示词
        hints_text = '\n'.join([f"  - {hint}" for hint in content_hints]) if content_hints else "  - 根据章节标题自由发挥"

        prompt = f"""为"{chapter_plan['title']}"撰写 {target_words}字 技术方案内容。

【章节定位】
这是使用固定模板生成的章节，属于标准技术方案的一部分。

【核心要点】
{hints_text}

【招标文档背景】
{tender_doc[:5000]}

【撰写要求】
1. 符合"{chapter_plan['title']}"章节的常规内容结构
2. 结合招标文档的具体需求
3. 字数: {target_words}字左右（±10%）
4. 专业、规范、逻辑清晰
5. 体现公司实力和技术能力

请直接输出方案内容，不需要输出章节标题。"""

        # 调用 LLM 生成
        response = self._call_llm(prompt)
        generated_content = response.strip()

        return {
            "title": chapter_plan['title'],
            "content": generated_content,
            "word_count": len(generated_content),
            "allocated_pages": allocated_pages,
            "template_based": True
        }

    @classmethod
    def list_templates(cls) -> List[Dict]:
        """
        列出所有可用模板

        Returns:
            模板列表
            [
                {
                    "template_id": "政府采购标准",
                    "name": "政府采购标准模板",
                    "description": "...",
                    "chapters_count": 5,
                    "chapters": ["第一章 总体设计方案", ...]
                },
                ...
            ]
        """
        return [
            {
                "template_id": key,
                "name": template['name'],
                "description": template.get('description', ''),
                "chapters_count": len(template['chapters']),
                "chapters": [c['title'] for c in template['chapters']]
            }
            for key, template in cls.TEMPLATES.items()
        ]
