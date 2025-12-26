#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
需求分析器 - 阶段1
从技术需求文档中提取和分析需求
"""

import json
import re
from typing import Dict, List, Any, Optional
from pathlib import Path

# 导入公共模块
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from common import get_module_logger, get_prompt_manager
from common.llm_client import create_llm_client
from modules.document_parser import ParserManager


class RequirementAnalyzer:
    """需求分析器"""

    def __init__(self, model_name: str = "gpt-4o-mini", api_key: Optional[str] = None):
        """
        初始化需求分析器

        Args:
            model_name: LLM模型名称
            api_key: API密钥（可选）
        """
        self.logger = get_module_logger("requirement_analyzer")
        self.prompt_manager = get_prompt_manager()
        self.llm_client = create_llm_client(model_name, api_key)
        self.parser_manager = ParserManager()

        self.logger.info(f"需求分析器初始化完成，使用模型: {model_name}")

    def analyze_document(self, file_path_or_text: str) -> Dict[str, Any]:
        """
        分析技术需求文档

        Args:
            file_path_or_text: 需求文档路径或文本内容

        Returns:
            分析结果字典
        """
        try:
            self.logger.info(f"开始分析需求文档: {file_path_or_text[:100] if len(file_path_or_text) > 100 else file_path_or_text}...")

            # 1. 解析文档内容 - 自动判断是文件路径还是文本
            # 改进判断逻辑: 检查是否为有效文件路径
            from pathlib import Path

            # 使用try-except避免文件名过长导致OSError
            is_file_path = False
            try:
                path_obj = Path(file_path_or_text)
                # 如果路径存在且是文件,则解析
                if path_obj.exists() and path_obj.is_file():
                    is_file_path = True
            except (OSError, ValueError):
                # 文件名过长或路径无效,视为文本内容
                is_file_path = False

            if is_file_path:
                self.logger.info(f"检测到输入为文件路径,尝试解析: {file_path_or_text}")
                document_text = self._parse_document(file_path_or_text)
            else:
                # 否则视为文本内容
                self.logger.info("检测到输入为文本内容，直接使用")
                document_text = file_path_or_text

            # 2. AI分析需求
            analysis_result = self._analyze_requirements(document_text)

            # 3. 后处理和验证
            processed_result = self._post_process_analysis(analysis_result)

            self.logger.info("需求文档分析完成")
            return processed_result

        except Exception as e:
            self.logger.error(f"需求文档分析失败: {e}", exc_info=True)
            raise

    def _parse_document(self, file_path: str) -> str:
        """
        解析文档内容

        Args:
            file_path: 文档路径

        Returns:
            文档文本内容
        """
        try:
            self.logger.info("解析文档内容...")

            # 使用文档解析管理器（简化同步版本）
            text = self.parser_manager.parse_document_simple(file_path)

            if not text or not text.strip():
                raise ValueError("文档内容为空")

            self.logger.info(f"文档解析成功，内容长度: {len(text)} 字符")
            return text

        except Exception as e:
            self.logger.error(f"文档解析失败: {e}")
            raise

    def _analyze_requirements(self, text: str) -> Dict[str, Any]:
        """
        使用AI分析需求

        Args:
            text: 文档文本

        Returns:
            AI分析结果
        """
        try:
            self.logger.info("调用AI分析需求...")

            # 获取分析提示词
            prompt_template = self.prompt_manager.get_prompt(
                'outline_generation',
                'analyze_requirements'
            )

            if not prompt_template:
                raise ValueError("未找到analyze_requirements提示词")

            # 限制文本长度（避免超过token限制）
            max_length = 15000  # 约15000字符
            if len(text) > max_length:
                self.logger.warning(f"文档过长，截取前{max_length}字符")
                text = text[:max_length] + "\n...[文档内容过长，已截断]"

            # 生成提示词
            prompt = prompt_template.format(text=text)

            # 调用LLM（增加max_tokens以支持复杂JSON输出）
            # 注意: 某些模型(如gpt-4o-mini)不支持自定义temperature,使用默认值
            response = self.llm_client.call(
                prompt=prompt,
                max_tokens=4000,  # 增加到4000以支持完整的需求分析JSON
                max_retries=3,
                purpose="需求分析"
            )

            # 解析JSON响应
            analysis_result = self._parse_json_response(response)

            if not analysis_result:
                raise ValueError("AI返回的分析结果为空或格式错误")

            self.logger.info("AI需求分析完成")
            return analysis_result

        except Exception as e:
            self.logger.error(f"AI需求分析失败: {e}")
            raise

    def _parse_json_response(self, response: str) -> Optional[Dict]:
        """
        解析JSON响应（增强容错处理）

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
                self.logger.warning(f"JSON解析失败(第一次尝试): {e}")

                # 尝试修复常见的JSON格式问题
                try:
                    # 修复尾随逗号问题: ,} 或 ,]
                    fixed_json = re.sub(r',\s*}', '}', json_str)
                    fixed_json = re.sub(r',\s*]', ']', fixed_json)

                    # 尝试解析修复后的JSON
                    result = json.loads(fixed_json)
                    self.logger.info("JSON修复成功（移除尾随逗号）")
                    return result
                except json.JSONDecodeError as e2:
                    self.logger.warning(f"JSON解析失败(修复后): {e2}")
                    return None

        return None

    def _post_process_analysis(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        后处理分析结果

        Args:
            analysis: 原始分析结果

        Returns:
            处理后的分析结果
        """
        try:
            # 确保必要的字段存在
            if 'document_summary' not in analysis:
                analysis['document_summary'] = {
                    'total_requirements': 0,
                    'mandatory_count': 0,
                    'optional_count': 0,
                    'complexity_level': 'medium'
                }

            if 'requirement_categories' not in analysis:
                analysis['requirement_categories'] = []

            if 'suggested_outline_structure' not in analysis:
                analysis['suggested_outline_structure'] = []

            # 统计信息
            total_requirements = sum(
                cat.get('requirements_count', 0)
                for cat in analysis.get('requirement_categories', [])
            )

            if total_requirements > 0:
                analysis['document_summary']['total_requirements'] = total_requirements

            # 添加元数据
            analysis['_metadata'] = {
                'analyzer_version': '1.0.0',
                'model_used': self.llm_client.model_name,
                'analysis_timestamp': self._get_timestamp()
            }

            return analysis

        except Exception as e:
            self.logger.error(f"后处理失败: {e}")
            return analysis

    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def extract_requirements_list(self, analysis: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        从分析结果中提取需求列表

        Args:
            analysis: 分析结果

        Returns:
            需求列表
        """
        requirements = []

        for category in analysis.get('requirement_categories', []):
            category_name = category.get('category', '未分类')
            category_code = category.get('category_code', 'unknown')
            priority = category.get('priority', 'medium')

            for point in category.get('key_points', []):
                requirements.append({
                    'category': category_name,
                    'category_code': category_code,
                    'requirement': point,
                    'priority': priority,
                    'keywords': category.get('keywords', [])
                })

        return requirements

    def get_summary(self, analysis: Dict[str, Any]) -> str:
        """
        生成分析摘要

        Args:
            analysis: 分析结果

        Returns:
            摘要文本
        """
        summary = analysis.get('document_summary', {})
        categories = analysis.get('requirement_categories', [])

        lines = [
            "# 需求分析摘要",
            "",
            f"- 总需求数: {summary.get('total_requirements', 0)}",
            f"- 强制需求: {summary.get('mandatory_count', 0)}",
            f"- 可选需求: {summary.get('optional_count', 0)}",
            f"- 复杂度: {summary.get('complexity_level', 'medium')}",
            "",
            "## 需求分类",
            ""
        ]

        for cat in categories:
            lines.append(
                f"- {cat.get('category', '未分类')}: "
                f"{cat.get('requirements_count', 0)}项 "
                f"(优先级: {cat.get('priority', 'medium')})"
            )

        return "\n".join(lines)
