#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大纲生成器 - 阶段2
根据需求分析结果生成技术方案应答大纲
"""

import json
import re
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime

# 导入公共模块
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from common import get_module_logger, get_prompt_manager
from common.llm_client import create_llm_client


class OutlineGenerator:
    """大纲生成器"""

    def __init__(self, model_name: str = "gpt-4o-mini", api_key: Optional[str] = None):
        """
        初始化大纲生成器

        Args:
            model_name: LLM模型名称
            api_key: API密钥（可选）
        """
        self.logger = get_module_logger("outline_generator")
        self.prompt_manager = get_prompt_manager()
        self.llm_client = create_llm_client(model_name, api_key)

        self.logger.info(f"大纲生成器初始化完成，使用模型: {model_name}")

    def generate_outline(self, analysis_result: Dict[str, Any], project_name: str = "") -> Dict[str, Any]:
        """
        生成技术方案大纲

        Args:
            analysis_result: 需求分析结果
            project_name: 项目名称（可选）

        Returns:
            大纲结构字典
        """
        try:
            self.logger.info("开始生成技术方案大纲...")

            # 1. 调用AI生成大纲
            outline_data = self._generate_outline_with_ai(analysis_result)

            # 2. 后处理大纲
            outline_data = self._post_process_outline(outline_data, project_name)

            # 3. 生成应答建议
            outline_data = self._generate_response_suggestions(outline_data, analysis_result)

            self.logger.info("技术方案大纲生成完成")
            return outline_data

        except Exception as e:
            self.logger.error(f"大纲生成失败: {e}", exc_info=True)
            raise

    def _generate_outline_with_ai(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        使用AI生成大纲结构

        Args:
            analysis: 需求分析结果

        Returns:
            大纲数据
        """
        try:
            # 获取大纲生成提示词
            prompt_template = self.prompt_manager.get_prompt(
                'outline_generation',
                'generate_outline'
            )

            if not prompt_template:
                raise ValueError("未找到generate_outline提示词")

            # 将分析结果转为JSON字符串
            analysis_json = json.dumps(analysis, ensure_ascii=False, indent=2)

            # 生成提示词
            prompt = prompt_template.format(analysis=analysis_json)

            # 调用LLM (增加max_tokens以确保返回完整的大纲JSON)
            response = self.llm_client.call(
                prompt=prompt,
                temperature=0.7,
                max_tokens=4000,  # 增加到4000以支持完整的大纲生成
                max_retries=3,
                purpose="大纲生成"
            )

            # 解析JSON响应
            outline = self._parse_json_response(response)

            if not outline:
                raise ValueError("AI返回的大纲为空或格式错误")

            return outline

        except Exception as e:
            self.logger.error(f"AI大纲生成失败: {e}")
            raise

    def _parse_json_response(self, response: str) -> Optional[Dict]:
        """
        解析JSON响应（容错处理）

        Args:
            response: AI响应文本

        Returns:
            解析后的字典，失败返回None
        """
        if not response or not response.strip():
            return None

        # 移除markdown代码块标记
        response = re.sub(r'^```json\s*', '', response.strip())
        response = re.sub(r'\s*```$', '', response.strip())

        # 查找JSON对象
        json_start = response.find('{')
        json_end = response.rfind('}') + 1

        if json_start != -1 and json_end > json_start:
            json_str = response[json_start:json_end]

            try:
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                self.logger.warning(f"JSON解析失败: {e}")
                self.logger.warning(f"原始JSON（前500字符）: {json_str[:500]}")
                self.logger.warning(f"原始JSON（后500字符）: {json_str[-500:]}")

                # 尝试多种修复策略
                json_str_fixed = json_str

                try:
                    # 策略1: 移除尾部的逗号
                    json_str_fixed = re.sub(r',\s*([\]}])', r'\1', json_str_fixed)

                    # 策略2: 修复缺失逗号的情况 (在 } 或 ] 后面紧跟 " 的情况)
                    json_str_fixed = re.sub(r'([\]}])\s*"', r'\1,"', json_str_fixed)

                    # 策略3: 修复缺失逗号的情况 (在 " 后面紧跟 " 的情况)
                    json_str_fixed = re.sub(r'"\s*"', r'","', json_str_fixed)

                    # 策略4: 修复双逗号
                    json_str_fixed = re.sub(r',,+', r',', json_str_fixed)

                    result = json.loads(json_str_fixed)
                    self.logger.info("JSON修复成功")
                    return result
                except Exception as fix_error:
                    self.logger.error(f"JSON修复失败: {fix_error}")
                    # 保存失败的JSON到文件以便调试
                    try:
                        import tempfile
                        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                            f.write(json_str)
                            self.logger.error(f"原始JSON已保存到: {f.name}")
                    except (OSError, IOError) as e:
                        self.logger.error(f"无法保存调试JSON文件: {e}")
                    return None

        return None

    def _post_process_outline(self, outline: Dict[str, Any], project_name: str) -> Dict[str, Any]:
        """
        后处理大纲数据

        Args:
            outline: 原始大纲
            project_name: 项目名称

        Returns:
            处理后的大纲
        """
        try:
            # 设置项目名称
            if project_name:
                outline['outline_title'] = f"{project_name} 技术方案应答大纲"

            # 确保必要字段存在
            if 'generation_time' not in outline:
                outline['generation_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            if 'chapters' not in outline:
                outline['chapters'] = []

            if 'total_chapters' not in outline:
                outline['total_chapters'] = len(outline.get('chapters', []))

            # 添加元数据
            outline['_metadata'] = {
                'generator_version': '1.0.0',
                'model_used': self.llm_client.model_name,
                'generation_timestamp': outline['generation_time']
            }

            # 规范化章节编号
            outline['chapters'] = self._normalize_chapter_numbers(outline['chapters'])

            return outline

        except Exception as e:
            self.logger.error(f"大纲后处理失败: {e}")
            return outline

    def _normalize_chapter_numbers(self, chapters: List[Dict]) -> List[Dict]:
        """
        规范化章节编号

        Args:
            chapters: 章节列表

        Returns:
            规范化后的章节列表
        """
        chapter_counters = [0, 0, 0]  # 1级、2级、3级计数器

        for chapter in chapters:
            level = chapter.get('level', 1)

            if level == 1:
                chapter_counters[0] += 1
                chapter_counters[1] = 0
                chapter_counters[2] = 0
                chapter['chapter_number'] = str(chapter_counters[0])

            elif level == 2:
                chapter_counters[1] += 1
                chapter_counters[2] = 0
                chapter['chapter_number'] = f"{chapter_counters[0]}.{chapter_counters[1]}"

            elif level == 3:
                chapter_counters[2] += 1
                chapter['chapter_number'] = (
                    f"{chapter_counters[0]}.{chapter_counters[1]}.{chapter_counters[2]}"
                )

            # 处理子章节
            if 'subsections' in chapter and chapter['subsections']:
                chapter['subsections'] = self._normalize_subsection_numbers(
                    chapter['subsections'],
                    chapter['chapter_number']
                )

        return chapters

    def _normalize_subsection_numbers(
        self, subsections: List[Dict], parent_number: str
    ) -> List[Dict]:
        """
        规范化子章节编号

        Args:
            subsections: 子章节列表
            parent_number: 父章节编号

        Returns:
            规范化后的子章节列表
        """
        for i, subsection in enumerate(subsections, start=1):
            subsection['chapter_number'] = f"{parent_number}.{i}"
            subsection['level'] = parent_number.count('.') + 2

        return subsections

    def _generate_response_suggestions(
        self, outline: Dict[str, Any], analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        为大纲章节生成应答建议

        Args:
            outline: 大纲数据
            analysis: 需求分析结果

        Returns:
            增强后的大纲
        """
        try:
            self.logger.info("生成应答建议...")

            # 获取应答建议提示词
            prompt_template = self.prompt_manager.get_prompt(
                'outline_generation',
                'generate_response_suggestions'
            )

            if not prompt_template:
                self.logger.warning("未找到generate_response_suggestions提示词，跳过")
                return outline

            # 为每个需求类别生成建议
            for category in analysis.get('requirement_categories', []):
                category_name = category.get('category', '')
                keywords = ', '.join(category.get('keywords', []))
                priority = category.get('priority', 'medium')
                summary = category.get('summary', '')

                # 生成提示词
                prompt = prompt_template.format(
                    category=category_name,
                    requirement=summary,
                    priority=priority,
                    keywords=keywords
                )

                try:
                    # 调用LLM（不重试，避免超时）
                    response = self.llm_client.call(
                        prompt=prompt,
                        temperature=0.7,
                        max_retries=1,
                        purpose="应答建议生成"
                    )

                    # 解析并附加到category
                    suggestion = self._parse_json_response(response)
                    if suggestion:
                        category['response_suggestion'] = suggestion

                except Exception as e:
                    self.logger.warning(f"生成'{category_name}'应答建议失败: {e}")
                    continue

            return outline

        except Exception as e:
            self.logger.error(f"生成应答建议失败: {e}")
            return outline

    def get_chapter_tree(self, outline: Dict[str, Any]) -> List[str]:
        """
        获取章节树（文本格式）

        Args:
            outline: 大纲数据

        Returns:
            章节树列表
        """
        lines = []

        for chapter in outline.get('chapters', []):
            indent = '  ' * (chapter.get('level', 1) - 1)
            chapter_num = chapter.get('chapter_number', '')
            title = chapter.get('title', '')

            lines.append(f"{indent}{chapter_num} {title}")

            # 递归处理子章节
            for subsection in chapter.get('subsections', []):
                sub_indent = '  ' * (subsection.get('level', 2) - 1)
                sub_num = subsection.get('chapter_number', '')
                sub_title = subsection.get('title', '')

                lines.append(f"{sub_indent}{sub_num} {sub_title}")

        return lines

    def export_outline_summary(self, outline: Dict[str, Any]) -> str:
        """
        导出大纲摘要（Markdown格式）

        Args:
            outline: 大纲数据

        Returns:
            Markdown文本
        """
        lines = [
            f"# {outline.get('outline_title', '技术方案应答大纲')}",
            "",
            f"**生成时间**: {outline.get('generation_time', '')}",
            f"**总章节数**: {outline.get('total_chapters', 0)}",
            f"**预计页数**: {outline.get('estimated_pages', 0)}",
            "",
            "## 章节结构",
            ""
        ]

        # 添加章节树
        lines.extend(self.get_chapter_tree(outline))

        return "\n".join(lines)
