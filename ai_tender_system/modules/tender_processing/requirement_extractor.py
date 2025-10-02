#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高精度要求提取器
功能：
- 使用高精度模型（GPT-4）提取结构化要求
- JSON Mode输出
- 分类提取（强制性/可选/加分项）
"""

import json
import requests
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed

from common import get_module_logger, get_config

logger = get_module_logger("requirement_extractor")


@dataclass
class TenderRequirement:
    """标书要求数据类"""
    constraint_type: str  # mandatory/optional/scoring
    category: str  # qualification/technical/commercial/service
    subcategory: Optional[str] = None
    detail: str = ""
    source_location: str = ""
    priority: str = "medium"  # high/medium/low
    extraction_confidence: float = 0.0

    def to_dict(self) -> Dict:
        return asdict(self)


class RequirementExtractor:
    """高精度要求提取器"""

    def __init__(self, model_name: str = 'yuanjing-deepseek-v3', max_workers: int = 3):
        """
        初始化提取器

        Args:
            model_name: 使用的AI模型名称（建议使用高精度模型）
            max_workers: 并行处理的最大线程数
        """
        self.model_name = model_name
        self.max_workers = max_workers
        self.config = get_config()

        # 获取模型配置
        self.model_config = self.config.get_model_config(model_name)

        # 统计信息
        self.total_processed = 0
        self.total_requirements = 0
        self.total_cost = 0.0
        self.total_api_calls = 0

    def get_extraction_prompt(self, chunk_content: str, chunk_type: str, section_title: str = "") -> str:
        """
        构建提取提示词

        Args:
            chunk_content: 分块内容
            chunk_type: 分块类型
            section_title: 所属章节标题

        Returns:
            prompt: 提示词
        """
        # 加载提示词模板
        prompts_file = self.config.get_path('base') / 'prompts' / 'tender_processing.json'

        try:
            with open(prompts_file, 'r', encoding='utf-8') as f:
                prompts = json.load(f)
                extract_template = prompts.get('extract_requirements', '')
        except Exception as e:
            logger.warning(f"加载提示词文件失败，使用默认提示词: {e}")
            extract_template = """从以下招标文本中提取所有对投标方的要求，以JSON格式返回。

章节标题：{section_title}
文本类型：{chunk_type}
文本内容：
{chunk_content}

请提取所有要求，并按以下JSON格式返回（必须是有效的JSON数组）：
[
  {{
    "constraint_type": "mandatory|optional|scoring",
    "category": "qualification|technical|commercial|service",
    "subcategory": "具体子类别（如：资质证书、技术参数、价格要求等）",
    "detail": "要求的具体描述",
    "source_location": "来源位置（章节标题或页码）",
    "priority": "high|medium|low",
    "extraction_confidence": 0.0-1.0
  }}
]

分类说明：
- constraint_type: mandatory（强制性，必须满足）/ optional（可选，建议满足）/ scoring（加分项，影响评分）
- category: qualification（资质类）/ technical（技术类）/ commercial（商务类）/ service（服务类）
- priority: high（关键要求）/ medium（一般要求）/ low（次要要求）

如果文本中没有明确的要求，请返回空数组[]。"""

        prompt = extract_template.format(
            section_title=section_title or "无",
            chunk_type=chunk_type,
            chunk_content=chunk_content
        )

        return prompt

    def call_ai_api(self, prompt: str, use_json_mode: bool = True) -> tuple[str, float]:
        """
        调用AI API进行提取

        Args:
            prompt: 提示词
            use_json_mode: 是否使用JSON Mode

        Returns:
            response: AI响应
            cost: API调用成本
        """
        try:
            # 构建请求
            if 'yuanjing' in self.model_name:
                # 联通元景系列模型
                headers = {
                    'Authorization': f"Bearer {self.model_config['access_token']}",
                    'Content-Type': 'application/json'
                }

                payload = {
                    'model': self.model_config['model_name'],
                    'messages': [
                        {
                            'role': 'system',
                            'content': '你是一个专业的招标文件分析助手，擅长提取结构化的投标要求。请严格按照JSON格式输出。'
                        },
                        {
                            'role': 'user',
                            'content': prompt
                        }
                    ],
                    'max_tokens': self.model_config.get('max_tokens', 2000),
                    'temperature': 0.1,  # 降低随机性，提高准确性
                }

                # 部分模型支持JSON Mode
                if use_json_mode:
                    payload['response_format'] = {'type': 'json_object'}

                url = f"{self.model_config['base_url']}/chat/completions"

            else:
                # OpenAI系列模型
                headers = {
                    'Authorization': f"Bearer {self.model_config.get('api_key', '')}",
                    'Content-Type': 'application/json'
                }

                payload = {
                    'model': self.model_config.get('model_name', self.model_name),
                    'messages': [
                        {
                            'role': 'system',
                            'content': '你是一个专业的招标文件分析助手，擅长提取结构化的投标要求。请严格按照JSON格式输出。'
                        },
                        {
                            'role': 'user',
                            'content': prompt
                        }
                    ],
                    'max_tokens': 2000,
                    'temperature': 0.1
                }

                # GPT-4支持JSON Mode
                if use_json_mode and 'gpt-4' in self.model_name:
                    payload['response_format'] = {'type': 'json_object'}

                url = self.model_config.get('api_endpoint', 'https://api.oaipro.com/v1/chat/completions')

            # 发送请求
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=self.model_config.get('timeout', 60)
            )

            response.raise_for_status()
            result = response.json()

            # 解析响应
            content = result['choices'][0]['message']['content'].strip()

            # 计算成本（简化估算）
            # DeepSeek-V3约为 $0.00027/1K input tokens, $0.0011/1K output tokens
            usage = result.get('usage', {})
            input_tokens = usage.get('prompt_tokens', 0)
            output_tokens = usage.get('completion_tokens', 0)

            if 'deepseek' in self.model_name:
                cost = (input_tokens * 0.00027 + output_tokens * 0.0011) / 1000
            else:
                # GPT-4约为 $0.03/1K input tokens, $0.06/1K output tokens
                cost = (input_tokens * 0.03 + output_tokens * 0.06) / 1000

            self.total_api_calls += 1
            self.total_cost += cost

            return content, cost

        except Exception as e:
            logger.error(f"AI API调用失败: {e}")
            return "", 0.0

    def parse_extraction_response(self, response: str) -> List[TenderRequirement]:
        """
        解析提取响应

        Args:
            response: AI响应文本（JSON格式）

        Returns:
            requirements: 要求列表
        """
        requirements = []

        if not response:
            return requirements

        try:
            # 尝试解析JSON
            # 有时模型会返回包含```json```标记的内容，需要清理
            response_clean = response.strip()

            # 移除markdown代码块标记
            if response_clean.startswith('```'):
                lines = response_clean.split('\n')
                response_clean = '\n'.join(lines[1:-1] if len(lines) > 2 else lines)
                response_clean = response_clean.replace('```json', '').replace('```', '').strip()

            # 解析JSON
            data = json.loads(response_clean)

            # 处理两种可能的格式
            if isinstance(data, list):
                items = data
            elif isinstance(data, dict) and 'requirements' in data:
                items = data['requirements']
            else:
                logger.warning(f"意外的JSON格式: {type(data)}")
                items = []

            # 转换为TenderRequirement对象
            for item in items:
                try:
                    req = TenderRequirement(
                        constraint_type=item.get('constraint_type', 'optional'),
                        category=item.get('category', 'technical'),
                        subcategory=item.get('subcategory'),
                        detail=item.get('detail', ''),
                        source_location=item.get('source_location', ''),
                        priority=item.get('priority', 'medium'),
                        extraction_confidence=float(item.get('extraction_confidence', 0.8))
                    )

                    # 验证必填字段
                    if req.detail:
                        requirements.append(req)
                except Exception as e:
                    logger.warning(f"解析单个要求失败: {e}, 数据: {item}")
                    continue

        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {e}")
            logger.debug(f"响应内容: {response[:500]}...")

        return requirements

    def extract_chunk(self, chunk: Dict) -> List[TenderRequirement]:
        """
        提取单个分块的要求

        Args:
            chunk: 分块数据

        Returns:
            requirements: 要求列表
        """
        chunk_id = chunk.get('chunk_id', 0)
        chunk_content = chunk.get('content', '')
        chunk_type = chunk.get('chunk_type', 'paragraph')
        metadata = chunk.get('metadata', {})
        section_title = metadata.get('section_title', '')

        logger.debug(f"正在提取分块 {chunk_id} 的要求...")

        # 生成提示词
        prompt = self.get_extraction_prompt(chunk_content, chunk_type, section_title)

        # 调用AI API
        response, cost = self.call_ai_api(prompt, use_json_mode=True)

        # 解析响应
        requirements = self.parse_extraction_response(response)

        # 为每个要求添加来源信息
        for req in requirements:
            if not req.source_location:
                req.source_location = section_title or f"分块 {chunk_id}"

        # 更新统计
        self.total_processed += 1
        self.total_requirements += len(requirements)

        logger.debug(f"分块 {chunk_id} 提取到 {len(requirements)} 个要求")

        return requirements

    def extract_chunks_parallel(self, chunks: List[Dict],
                                progress_callback: Optional[callable] = None) -> List[TenderRequirement]:
        """
        并行批量提取要求

        Args:
            chunks: 分块列表（经过筛选的高价值分块）
            progress_callback: 进度回调函数 callback(processed, total)

        Returns:
            requirements: 所有提取的要求列表
        """
        logger.info(f"开始并行提取 {len(chunks)} 个分块的要求，使用 {self.max_workers} 个线程...")

        all_requirements = []
        processed = 0

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有任务
            future_to_chunk = {
                executor.submit(self.extract_chunk, chunk): chunk
                for chunk in chunks
            }

            # 收集结果
            for future in as_completed(future_to_chunk):
                try:
                    requirements = future.result()
                    all_requirements.extend(requirements)

                    processed += 1
                    if progress_callback:
                        progress_callback(processed, len(chunks))

                except Exception as e:
                    chunk = future_to_chunk[future]
                    logger.error(f"提取分块 {chunk.get('chunk_id')} 失败: {e}")

        logger.info(f"提取完成！")
        logger.info(f"  处理分块: {processed}")
        logger.info(f"  提取要求: {len(all_requirements)}")
        logger.info(f"  API调用: {self.total_api_calls} 次")
        logger.info(f"  总成本: ${self.total_cost:.4f}")

        # 按类型统计
        stats = self._get_requirements_stats(all_requirements)
        logger.info(f"  强制性: {stats['mandatory']} | 可选: {stats['optional']} | 加分项: {stats['scoring']}")

        return all_requirements

    def _get_requirements_stats(self, requirements: List[TenderRequirement]) -> Dict:
        """获取要求统计信息"""
        stats = {
            'total': len(requirements),
            'mandatory': 0,
            'optional': 0,
            'scoring': 0,
            'by_category': {}
        }

        for req in requirements:
            # 按类型统计
            if req.constraint_type == 'mandatory':
                stats['mandatory'] += 1
            elif req.constraint_type == 'optional':
                stats['optional'] += 1
            elif req.constraint_type == 'scoring':
                stats['scoring'] += 1

            # 按类别统计
            category = req.category
            stats['by_category'][category] = stats['by_category'].get(category, 0) + 1

        return stats

    def get_statistics(self) -> Dict:
        """获取提取统计信息"""
        return {
            'total_processed': self.total_processed,
            'total_requirements': self.total_requirements,
            'total_api_calls': self.total_api_calls,
            'total_cost': self.total_cost,
            'model_name': self.model_name,
            'avg_requirements_per_chunk': self.total_requirements / self.total_processed if self.total_processed > 0 else 0
        }


if __name__ == '__main__':
    # 测试代码
    test_chunks = [
        {
            'chunk_id': 1,
            'chunk_type': 'paragraph',
            'content': '投标方必须具有建筑工程施工总承包一级及以上资质，并提供有效的资质证书复印件。',
            'metadata': {'section_title': '第二章 投标人资格要求'}
        },
        {
            'chunk_id': 2,
            'chunk_type': 'paragraph',
            'content': '投标方应具有3年以上类似项目实施经验，提供3个成功案例可获得加分。',
            'metadata': {'section_title': '第三章 评分标准'}
        }
    ]

    extractor = RequirementExtractor(model_name='yuanjing-deepseek-v3', max_workers=2)

    def progress_callback(processed, total):
        print(f"进度: {processed}/{total} ({processed/total*100:.1f}%)")

    requirements = extractor.extract_chunks_parallel(test_chunks, progress_callback)

    print("\n提取结果:")
    for i, req in enumerate(requirements, 1):
        print(f"\n{i}. 【{req.constraint_type}】{req.category}/{req.subcategory}")
        print(f"   详情: {req.detail}")
        print(f"   来源: {req.source_location}")
        print(f"   优先级: {req.priority} | 置信度: {req.extraction_confidence:.2f}")

    print(f"\n统计信息: {extractor.get_statistics()}")
