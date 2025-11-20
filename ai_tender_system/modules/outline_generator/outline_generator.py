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
from concurrent.futures import ThreadPoolExecutor, as_completed

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

            # 3. 生成应答建议 - 已禁用以加快生成速度（该数据未被后续流程使用）
            # outline_data = self._generate_response_suggestions(outline_data, analysis_result)
            self.logger.info("⚡ 跳过应答建议生成（加速模式，预计节省5-10分钟）")

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

            # 强制覆盖生成时间为当前实际时间（不使用LLM返回的示例时间）
            outline['generation_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            if 'chapters' not in outline:
                outline['chapters'] = []

            # 重新计算章节数（以实际章节为准）
            outline['total_chapters'] = len(outline.get('chapters', []))

            # 重新计算预计页数（基于章节数，每章约10页）
            chapter_count = outline['total_chapters']
            outline['estimated_pages'] = max(30, chapter_count * 10)

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
        规范化章节编号（使用中文格式）

        Args:
            chapters: 章节列表

        Returns:
            规范化后的章节列表
        """
        # 中文数字映射（支持1-20）
        chinese_numbers = ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十',
                          '十一', '十二', '十三', '十四', '十五', '十六', '十七', '十八', '十九', '二十']

        chapter_counters = [0, 0, 0]  # 1级、2级、3级计数器

        for chapter in chapters:
            level = chapter.get('level', 1)

            if level == 1:
                chapter_counters[0] += 1
                chapter_counters[1] = 0
                chapter_counters[2] = 0
                # ✅ 1级使用中文编号：一、二、三
                if chapter_counters[0] <= len(chinese_numbers):
                    chapter['chapter_number'] = chinese_numbers[chapter_counters[0] - 1]
                else:
                    chapter['chapter_number'] = str(chapter_counters[0])

            elif level == 2:
                chapter_counters[1] += 1
                chapter_counters[2] = 0
                # ✅ 2级使用括号中文编号：（一）、（二）、（三）
                if chapter_counters[1] <= len(chinese_numbers):
                    chapter['chapter_number'] = f"（{chinese_numbers[chapter_counters[1] - 1]}）"
                else:
                    chapter['chapter_number'] = f"（{chapter_counters[1]}）"

            elif level == 3:
                chapter_counters[2] += 1
                # ✅ 3级使用阿拉伯数字：1、2、3
                chapter['chapter_number'] = str(chapter_counters[2])

            # 处理子章节
            if 'subsections' in chapter and chapter['subsections']:
                chapter['subsections'] = self._normalize_subsection_numbers(
                    chapter['subsections'],
                    chapter['chapter_number'],
                    chapter_counters[0]  # 传递父章节的计数器
                )

        return chapters

    def _normalize_subsection_numbers(
        self, subsections: List[Dict], parent_number: str, parent_index: int = 0
    ) -> List[Dict]:
        """
        规范化子章节编号（使用中文格式）

        Args:
            subsections: 子章节列表
            parent_number: 父章节编号
            parent_index: 父章节的索引（用于判断层级）

        Returns:
            规范化后的子章节列表
        """
        # 中文数字映射
        chinese_numbers = ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十',
                          '十一', '十二', '十三', '十四', '十五', '十六', '十七', '十八', '十九', '二十']

        for i, subsection in enumerate(subsections, start=1):
            # 判断当前子章节的层级
            # 如果父章节是中文数字（如"一"），则子章节用（一）、（二）
            # 如果父章节是括号中文（如"（一）"），则子章节用1、2、3

            if parent_number in chinese_numbers:
                # 父章节是1级（一、二、三），子章节用2级（一）、（二）、（三）
                if i <= len(chinese_numbers):
                    subsection['chapter_number'] = f"（{chinese_numbers[i - 1]}）"
                else:
                    subsection['chapter_number'] = f"（{i}）"
                subsection['level'] = 2
            elif parent_number.startswith('（') and parent_number.endswith('）'):
                # 父章节是2级（一）、（二），子章节用3级 1、2、3
                subsection['chapter_number'] = str(i)
                subsection['level'] = 3
            else:
                # 默认逻辑（向后兼容）
                subsection['chapter_number'] = f"{parent_number}.{i}"
                subsection['level'] = 2

        return subsections

    def _generate_single_suggestion(
        self, category: Dict[str, Any], prompt_template: str
    ) -> Optional[Dict[str, Any]]:
        """
        为单个需求类别生成应答建议（用于并发调用）

        Args:
            category: 需求类别数据
            prompt_template: 提示词模板

        Returns:
            生成的建议字典，失败返回None
        """
        try:
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

            # 调用LLM
            response = self.llm_client.call(
                prompt=prompt,
                temperature=0.7,
                max_retries=1,
                purpose=f"应答建议生成: {category_name}"
            )

            # 解析响应
            suggestion = self._parse_json_response(response)
            if suggestion:
                self.logger.info(f"✓ 成功生成'{category_name}'的应答建议")
                return suggestion
            else:
                self.logger.warning(f"⚠️  '{category_name}'应答建议解析失败")
                return None

        except Exception as e:
            self.logger.warning(f"❌ 生成'{category_name}'应答建议失败: {e}")
            return None

    def _generate_response_suggestions(
        self, outline: Dict[str, Any], analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        为大纲章节生成应答建议（并发版本）

        Args:
            outline: 大纲数据
            analysis: 需求分析结果

        Returns:
            增强后的大纲
        """
        try:
            self.logger.info("生成应答建议（并发模式）...")

            # 获取应答建议提示词
            prompt_template = self.prompt_manager.get_prompt(
                'outline_generation',
                'generate_response_suggestions'
            )

            if not prompt_template:
                self.logger.warning("未找到generate_response_suggestions提示词，跳过")
                return outline

            categories = analysis.get('requirement_categories', [])
            if not categories:
                self.logger.info("无需求类别，跳过应答建议生成")
                return outline

            # 并发生成所有类别的应答建议
            self.logger.info(f"开始并发生成 {len(categories)} 个类别的应答建议...")

            with ThreadPoolExecutor(max_workers=5) as executor:
                # 提交所有任务
                future_to_category = {
                    executor.submit(self._generate_single_suggestion, category, prompt_template): category
                    for category in categories
                }

                # 收集结果
                completed_count = 0
                failed_count = 0

                for future in as_completed(future_to_category):
                    category = future_to_category[future]
                    try:
                        # 设置120秒超时
                        suggestion = future.result(timeout=120)
                        if suggestion:
                            category['response_suggestion'] = suggestion
                            completed_count += 1
                        else:
                            failed_count += 1
                    except Exception as e:
                        category_name = category.get('category', '未知类别')
                        self.logger.warning(f"处理'{category_name}'结果时出错: {e}")
                        failed_count += 1

            self.logger.info(
                f"应答建议生成完成: 成功 {completed_count}个, 失败 {failed_count}个, "
                f"总计 {len(categories)}个"
            )

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
