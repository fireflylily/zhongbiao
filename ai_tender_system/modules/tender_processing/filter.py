#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI快速筛选器
功能：
- 使用低成本模型（GPT-3.5）快速判断分块价值
- 并行批量处理
- 过滤掉约80%的无关内容
"""

import asyncio
import aiohttp
import json
from typing import List, Dict, Tuple, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass

from common import get_module_logger, get_config

logger = get_module_logger("tender_filter")


@dataclass
class FilterResult:
    """筛选结果数据类"""
    chunk_id: int
    is_valuable: bool
    confidence: float
    reason: str = ""

    def to_dict(self) -> Dict:
        return {
            'chunk_id': self.chunk_id,
            'is_valuable': self.is_valuable,
            'confidence': self.confidence,
            'reason': self.reason
        }


class TenderFilter:
    """AI快速筛选器"""

    def __init__(self, model_name: str = 'gpt-4o-mini', max_workers: int = 5):
        """
        初始化筛选器

        Args:
            model_name: 使用的AI模型名称（建议使用低成本模型）
            max_workers: 并行处理的最大线程数
        """
        self.model_name = model_name
        self.max_workers = max_workers
        self.config = get_config()

        # 获取模型配置
        self.model_config = self.config.get_model_config(model_name)

        # 统计信息
        self.total_processed = 0
        self.total_valuable = 0
        self.total_cost = 0.0
        self.total_api_calls = 0

    def get_filter_prompt(self, chunk_content: str, chunk_type: str, section_title: str = "") -> str:
        """
        构建筛选提示词

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
                filter_template = prompts.get('filter_chunk', '')
        except Exception as e:
            logger.warning(f"加载提示词文件失败，使用默认提示词: {e}")
            filter_template = """判断以下文本是否包含对投标方的【强制性要求】或【潜在加分项】。

章节标题：{section_title}
文本类型：{chunk_type}
文本内容：
{chunk_content}

请只回复 'YES' 或 'NO'，以及简短的理由（不超过20字）。
格式：YES/NO|理由"""

        prompt = filter_template.format(
            section_title=section_title or "无",
            chunk_type=chunk_type,
            chunk_content=chunk_content
        )

        return prompt

    def call_ai_api(self, prompt: str) -> Tuple[str, float]:
        """
        调用AI API进行筛选

        Args:
            prompt: 提示词

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
                            'role': 'user',
                            'content': prompt
                        }
                    ],
                    'max_tokens': 100,  # 筛选只需要简短回答
                    'temperature': 0.3  # 降低随机性
                }

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
                            'role': 'user',
                            'content': prompt
                        }
                    ],
                    'max_tokens': 100,
                    'temperature': 0.3
                }

                url = self.model_config.get('api_endpoint', 'https://api.oaipro.com/v1/chat/completions')

            # 发送请求
            import requests
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=self.model_config.get('timeout', 30)
            )

            response.raise_for_status()
            result = response.json()

            # 解析响应
            content = result['choices'][0]['message']['content'].strip()

            # 计算成本（简化估算）
            # GPT-4o-mini约为 $0.00015/1K input tokens, $0.0006/1K output tokens
            usage = result.get('usage', {})
            input_tokens = usage.get('prompt_tokens', 0)
            output_tokens = usage.get('completion_tokens', 0)

            cost = (input_tokens * 0.00015 + output_tokens * 0.0006) / 1000

            self.total_api_calls += 1
            self.total_cost += cost

            return content, cost

        except Exception as e:
            logger.error(f"AI API调用失败: {e}")
            return "", 0.0

    def parse_filter_response(self, response: str) -> Tuple[bool, float, str]:
        """
        解析筛选响应

        Args:
            response: AI响应文本

        Returns:
            is_valuable: 是否有价值
            confidence: 置信度
            reason: 理由
        """
        # 默认值
        is_valuable = False
        confidence = 0.5
        reason = ""

        if not response:
            return is_valuable, confidence, "API调用失败"

        # 解析响应
        # 格式1：YES/NO|理由
        if '|' in response:
            parts = response.split('|', 1)
            decision = parts[0].strip().upper()
            reason = parts[1].strip() if len(parts) > 1 else ""
        else:
            # 格式2：直接YES或NO
            decision = response.strip().upper()
            reason = ""

        # 判断价值
        if 'YES' in decision or '是' in decision or '有' in decision:
            is_valuable = True
            confidence = 0.8
        elif 'NO' in decision or '否' in decision or '无' in decision:
            is_valuable = False
            confidence = 0.8
        else:
            # 不确定的情况，保守起见认为有价值
            is_valuable = True
            confidence = 0.5
            reason = "响应格式不明确，保守保留"

        return is_valuable, confidence, reason

    def filter_chunk(self, chunk: Dict) -> FilterResult:
        """
        筛选单个分块

        Args:
            chunk: 分块数据

        Returns:
            result: 筛选结果
        """
        chunk_id = chunk.get('chunk_id', 0)
        chunk_content = chunk.get('content', '')
        chunk_type = chunk.get('chunk_type', 'paragraph')
        metadata = chunk.get('metadata', {})
        section_title = metadata.get('section_title', '')

        # 特殊处理：标题和表格默认保留
        if chunk_type in ['title', 'table']:
            logger.debug(f"分块 {chunk_id} 是{chunk_type}，默认保留")
            return FilterResult(
                chunk_id=chunk_id,
                is_valuable=True,
                confidence=1.0,
                reason=f"{chunk_type}默认保留"
            )

        # 生成提示词（包含章节标题信息）
        prompt = self.get_filter_prompt(chunk_content, chunk_type, section_title)

        # 调用AI API
        response, cost = self.call_ai_api(prompt)

        # 解析响应
        is_valuable, confidence, reason = self.parse_filter_response(response)

        # 更新统计
        self.total_processed += 1
        if is_valuable:
            self.total_valuable += 1

        logger.debug(f"分块 {chunk_id}: {'保留' if is_valuable else '过滤'} (置信度: {confidence:.2f})")

        return FilterResult(
            chunk_id=chunk_id,
            is_valuable=is_valuable,
            confidence=confidence,
            reason=reason
        )

    def filter_chunks_parallel(self, chunks: List[Dict],
                               progress_callback: Optional[callable] = None) -> List[FilterResult]:
        """
        并行批量筛选分块

        Args:
            chunks: 分块列表
            progress_callback: 进度回调函数 callback(processed, total)

        Returns:
            results: 筛选结果列表
        """
        logger.info(f"开始并行筛选 {len(chunks)} 个分块，使用 {self.max_workers} 个线程...")

        results = []
        processed = 0

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有任务
            future_to_chunk = {
                executor.submit(self.filter_chunk, chunk): chunk
                for chunk in chunks
            }

            # 收集结果
            for future in as_completed(future_to_chunk):
                try:
                    result = future.result()
                    results.append(result)

                    processed += 1
                    if progress_callback:
                        progress_callback(processed, len(chunks))

                except Exception as e:
                    chunk = future_to_chunk[future]
                    logger.error(f"筛选分块 {chunk.get('chunk_id')} 失败: {e}")

                    # 出错时保守保留
                    results.append(FilterResult(
                        chunk_id=chunk.get('chunk_id', 0),
                        is_valuable=True,
                        confidence=0.5,
                        reason=f"处理出错: {str(e)}"
                    ))

        # 按chunk_id排序
        results.sort(key=lambda x: x.chunk_id)

        # 输出统计信息
        valuable_count = sum(1 for r in results if r.is_valuable)
        filter_rate = (len(results) - valuable_count) / len(results) * 100 if results else 0

        logger.info(f"筛选完成！")
        logger.info(f"  总分块数: {len(results)}")
        logger.info(f"  保留分块: {valuable_count} ({100-filter_rate:.1f}%)")
        logger.info(f"  过滤分块: {len(results) - valuable_count} ({filter_rate:.1f}%)")
        logger.info(f"  API调用: {self.total_api_calls} 次")
        logger.info(f"  总成本: ${self.total_cost:.4f}")

        return results

    def get_statistics(self) -> Dict:
        """获取筛选统计信息"""
        filter_rate = (self.total_processed - self.total_valuable) / self.total_processed * 100 \
            if self.total_processed > 0 else 0

        return {
            'total_processed': self.total_processed,
            'total_valuable': self.total_valuable,
            'total_filtered': self.total_processed - self.total_valuable,
            'filter_rate': filter_rate,
            'total_api_calls': self.total_api_calls,
            'total_cost': self.total_cost,
            'model_name': self.model_name
        }


if __name__ == '__main__':
    # 测试代码
    test_chunks = [
        {
            'chunk_id': 1,
            'chunk_type': 'title',
            'content': '第一章 项目概述'
        },
        {
            'chunk_id': 2,
            'chunk_type': 'paragraph',
            'content': '本项目旨在建设一个智能标书处理系统。'
        },
        {
            'chunk_id': 3,
            'chunk_type': 'paragraph',
            'content': '投标方必须具有建筑工程施工总承包一级及以上资质。'
        },
        {
            'chunk_id': 4,
            'chunk_type': 'paragraph',
            'content': '本文档仅供参考，最终解释权归招标方所有。'
        }
    ]

    filter_engine = TenderFilter(model_name='gpt-4o-mini', max_workers=2)

    def progress_callback(processed, total):
        print(f"进度: {processed}/{total} ({processed/total*100:.1f}%)")

    results = filter_engine.filter_chunks_parallel(test_chunks, progress_callback)

    print("\n筛选结果:")
    for result in results:
        print(f"  分块 {result.chunk_id}: {'保留' if result.is_valuable else '过滤'} "
              f"(置信度: {result.confidence:.2f}) - {result.reason}")

    print(f"\n统计信息: {filter_engine.get_statistics()}")
