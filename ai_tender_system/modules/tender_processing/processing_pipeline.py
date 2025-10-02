#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
标书智能处理流程协调器
功能：
- 整合三步流程：分块 -> 筛选 -> 提取
- 进度追踪
- 异步处理支持
- 错误恢复机制
"""

import uuid
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Callable
from pathlib import Path
from dataclasses import dataclass

from common import get_module_logger, get_config
from common.database import get_knowledge_base_db

from .chunker import DocumentChunker
from .filter import TenderFilter
from .requirement_extractor import RequirementExtractor

logger = get_module_logger("processing_pipeline")


@dataclass
class ProcessingProgress:
    """处理进度数据类"""
    step: str  # chunking/filtering/extraction
    status: str  # pending/processing/completed/failed
    total_items: int = 0
    processed_items: int = 0
    success_items: int = 0
    failed_items: int = 0
    progress_percentage: float = 0.0
    estimated_time_remaining: int = 0  # 秒

    def to_dict(self) -> Dict:
        return {
            'step': self.step,
            'status': self.status,
            'total_items': self.total_items,
            'processed_items': self.processed_items,
            'success_items': self.success_items,
            'failed_items': self.failed_items,
            'progress_percentage': self.progress_percentage,
            'estimated_time_remaining': self.estimated_time_remaining
        }


class TenderProcessingPipeline:
    """标书智能处理流程协调器"""

    def __init__(self, project_id: int, document_text: str,
                 filter_model: str = 'gpt-4o-mini',
                 extract_model: str = 'yuanjing-deepseek-v3',
                 progress_callback: Optional[Callable] = None):
        """
        初始化处理流程

        Args:
            project_id: 项目ID
            document_text: 文档全文
            filter_model: 筛选模型
            extract_model: 提取模型
            progress_callback: 进度回调函数 callback(progress: ProcessingProgress)
        """
        self.project_id = project_id
        self.document_text = document_text
        self.filter_model = filter_model
        self.extract_model = extract_model
        self.progress_callback = progress_callback

        # 生成任务ID
        self.task_id = f"task_{project_id}_{uuid.uuid4().hex[:8]}"

        # 初始化组件
        self.chunker = DocumentChunker(max_chunk_size=800, overlap_size=100)
        self.filter = TenderFilter(model_name=filter_model, max_workers=5)
        self.extractor = RequirementExtractor(model_name=extract_model, max_workers=3)

        # 数据库
        self.db = get_knowledge_base_db()

        # 处理结果
        self.chunks = []
        self.filter_results = []
        self.requirements = []

        # 统计信息
        self.total_cost = 0.0
        self.total_api_calls = 0
        self.start_time = None
        self.end_time = None

        logger.info(f"初始化处理流程 - 任务ID: {self.task_id}, 项目ID: {project_id}")

    def _update_progress(self, step: str, status: str, processed: int = 0, total: int = 0):
        """
        更新进度

        Args:
            step: 当前步骤
            status: 状态
            processed: 已处理数量
            total: 总数量
        """
        progress = ProcessingProgress(
            step=step,
            status=status,
            total_items=total,
            processed_items=processed,
            success_items=processed,
            progress_percentage=processed / total * 100 if total > 0 else 0
        )

        # 估算剩余时间
        if processed > 0 and self.start_time:
            elapsed = time.time() - self.start_time
            avg_time_per_item = elapsed / processed
            remaining_items = total - processed
            progress.estimated_time_remaining = int(avg_time_per_item * remaining_items)

        # 调用回调
        if self.progress_callback:
            self.progress_callback(progress)

        # 更新数据库
        self._update_task_in_db(step, status, progress.progress_percentage)

        logger.info(f"进度更新 - {step}: {processed}/{total} ({progress.progress_percentage:.1f}%)")

    def _update_task_in_db(self, current_step: str, status: str, progress: float):
        """更新任务状态到数据库"""
        try:
            self.db.update_processing_task(
                task_id=self.task_id,
                current_step=current_step,
                overall_status=status,
                progress_percentage=progress
            )
        except Exception as e:
            logger.warning(f"更新任务状态失败: {e}")

    def _save_chunks_to_db(self, chunks: List) -> bool:
        """保存分块到数据库"""
        try:
            chunks_data = []
            for chunk in chunks:
                chunk_dict = chunk.to_dict()
                chunk_dict['project_id'] = self.project_id
                chunks_data.append(chunk_dict)

            success = self.db.batch_create_tender_chunks(chunks_data)
            if success:
                logger.info(f"成功保存 {len(chunks_data)} 个分块到数据库")
            return success
        except Exception as e:
            logger.error(f"保存分块失败: {e}")
            return False

    def _update_filter_results_in_db(self, filter_results: List) -> bool:
        """更新筛选结果到数据库"""
        try:
            # 获取数据库中的分块（带chunk_id）
            db_chunks = self.db.get_tender_chunks(self.project_id)

            # 建立索引映射
            chunk_id_map = {chunk['chunk_index']: chunk['chunk_id'] for chunk in db_chunks}

            # 更新筛选结果
            for result in filter_results:
                chunk_index = result.chunk_id
                chunk_id = chunk_id_map.get(chunk_index)

                if chunk_id:
                    self.db.update_chunk_filter_result(
                        chunk_id=chunk_id,
                        is_valuable=result.is_valuable,
                        confidence=result.confidence,
                        model=self.filter_model
                    )

            logger.info(f"成功更新 {len(filter_results)} 个分块的筛选结果")
            return True
        except Exception as e:
            logger.error(f"更新筛选结果失败: {e}")
            return False

    def _save_requirements_to_db(self, requirements: List) -> bool:
        """保存提取的要求到数据库"""
        try:
            # 获取数据库中的分块（获取chunk_id映射）
            db_chunks = self.db.get_tender_chunks(self.project_id, valuable_only=True)
            chunk_id_map = {chunk['chunk_index']: chunk['chunk_id'] for chunk in db_chunks}

            requirements_data = []
            for req in requirements:
                req_dict = req.to_dict()
                req_dict['project_id'] = self.project_id

                # 这里简化处理，实际需要追踪每个要求来自哪个chunk
                # 可以在提取时记录chunk_id
                req_dict['chunk_id'] = None

                req_dict['extraction_model'] = self.extract_model
                requirements_data.append(req_dict)

            success = self.db.batch_create_tender_requirements(requirements_data)
            if success:
                logger.info(f"成功保存 {len(requirements_data)} 个要求到数据库")
            return success
        except Exception as e:
            logger.error(f"保存要求失败: {e}")
            return False

    def step1_chunking(self) -> bool:
        """
        步骤1：文档分块

        Returns:
            success: 是否成功
        """
        logger.info("=" * 60)
        logger.info("步骤1：文档分块")
        logger.info("=" * 60)

        try:
            self._update_progress('chunking', 'processing', 0, 1)

            # 执行分块
            self.chunks = self.chunker.chunk_document(
                text=self.document_text,
                metadata={'project_id': self.project_id}
            )

            # 保存到数据库
            if not self._save_chunks_to_db(self.chunks):
                raise Exception("保存分块到数据库失败")

            # 更新任务统计
            self.db.update_processing_task(
                task_id=self.task_id,
                total_chunks=len(self.chunks)
            )

            self._update_progress('chunking', 'completed', 1, 1)

            logger.info(f"✅ 分块完成 - 共生成 {len(self.chunks)} 个分块")
            return True

        except Exception as e:
            logger.error(f"❌ 分块失败: {e}")
            self._update_progress('chunking', 'failed', 0, 1)
            return False

    def step2_filtering(self) -> bool:
        """
        步骤2：AI筛选

        Returns:
            success: 是否成功
        """
        logger.info("=" * 60)
        logger.info("步骤2：AI快速筛选")
        logger.info("=" * 60)

        try:
            # 准备筛选数据
            chunks_for_filter = [chunk.to_dict() for chunk in self.chunks]

            # 进度回调
            def filter_progress(processed, total):
                self._update_progress('filtering', 'processing', processed, total)

            self._update_progress('filtering', 'processing', 0, len(chunks_for_filter))

            # 执行筛选
            self.filter_results = self.filter.filter_chunks_parallel(
                chunks=chunks_for_filter,
                progress_callback=filter_progress
            )

            # 更新数据库
            if not self._update_filter_results_in_db(self.filter_results):
                raise Exception("更新筛选结果到数据库失败")

            # 统计
            valuable_count = sum(1 for r in self.filter_results if r.is_valuable)
            filter_rate = (len(self.filter_results) - valuable_count) / len(self.filter_results) * 100

            # 更新任务统计
            self.db.update_processing_task(
                task_id=self.task_id,
                valuable_chunks=valuable_count
            )

            # 累计成本
            filter_stats = self.filter.get_statistics()
            self.total_cost += filter_stats['total_cost']
            self.total_api_calls += filter_stats['total_api_calls']

            self._update_progress('filtering', 'completed', len(self.filter_results), len(self.filter_results))

            logger.info(f"✅ 筛选完成")
            logger.info(f"   保留: {valuable_count} ({100-filter_rate:.1f}%)")
            logger.info(f"   过滤: {len(self.filter_results) - valuable_count} ({filter_rate:.1f}%)")
            logger.info(f"   成本: ${filter_stats['total_cost']:.4f}")

            return True

        except Exception as e:
            logger.error(f"❌ 筛选失败: {e}")
            self._update_progress('filtering', 'failed', 0, len(self.chunks))
            return False

    def step3_extraction(self) -> bool:
        """
        步骤3：精准提取

        Returns:
            success: 是否成功
        """
        logger.info("=" * 60)
        logger.info("步骤3：精准要求提取")
        logger.info("=" * 60)

        try:
            # 获取高价值分块
            valuable_chunks = [
                chunk.to_dict()
                for i, chunk in enumerate(self.chunks)
                if i < len(self.filter_results) and self.filter_results[i].is_valuable
            ]

            if not valuable_chunks:
                logger.warning("没有高价值分块，跳过提取步骤")
                self._update_progress('extraction', 'completed', 0, 0)
                return True

            # 进度回调
            def extract_progress(processed, total):
                self._update_progress('extraction', 'processing', processed, total)

            self._update_progress('extraction', 'processing', 0, len(valuable_chunks))

            # 执行提取
            self.requirements = self.extractor.extract_chunks_parallel(
                chunks=valuable_chunks,
                progress_callback=extract_progress
            )

            # 保存到数据库
            if not self._save_requirements_to_db(self.requirements):
                raise Exception("保存要求到数据库失败")

            # 更新任务统计
            self.db.update_processing_task(
                task_id=self.task_id,
                total_requirements=len(self.requirements)
            )

            # 累计成本
            extract_stats = self.extractor.get_statistics()
            self.total_cost += extract_stats['total_cost']
            self.total_api_calls += extract_stats['total_api_calls']

            self._update_progress('extraction', 'completed', len(valuable_chunks), len(valuable_chunks))

            logger.info(f"✅ 提取完成")
            logger.info(f"   处理分块: {len(valuable_chunks)}")
            logger.info(f"   提取要求: {len(self.requirements)}")
            logger.info(f"   成本: ${extract_stats['total_cost']:.4f}")

            return True

        except Exception as e:
            logger.error(f"❌ 提取失败: {e}")
            self._update_progress('extraction', 'failed', 0, len(self.chunks))
            return False

    def run(self) -> Dict:
        """
        运行完整的三步处理流程

        Returns:
            result: 处理结果
        """
        logger.info("🚀 启动标书智能处理流程")
        logger.info(f"   任务ID: {self.task_id}")
        logger.info(f"   项目ID: {self.project_id}")
        logger.info(f"   文档长度: {len(self.document_text)} 字符")

        self.start_time = time.time()

        # 创建任务记录
        try:
            self.db.create_processing_task(
                project_id=self.project_id,
                task_id=self.task_id,
                pipeline_config={
                    'filter_model': self.filter_model,
                    'extract_model': self.extract_model
                }
            )
        except Exception as e:
            logger.warning(f"创建任务记录失败: {e}")

        # 执行三步流程
        steps = [
            ('chunking', self.step1_chunking),
            ('filtering', self.step2_filtering),
            ('extraction', self.step3_extraction)
        ]

        overall_success = True

        for step_name, step_func in steps:
            success = step_func()
            if not success:
                overall_success = False
                logger.error(f"流程在步骤 {step_name} 失败，终止处理")
                break

        self.end_time = time.time()
        total_time = self.end_time - self.start_time

        # 更新任务状态
        final_status = 'completed' if overall_success else 'failed'
        self.db.update_processing_task(
            task_id=self.task_id,
            overall_status=final_status,
            progress_percentage=100.0 if overall_success else 0.0
        )

        # 生成结果报告
        result = {
            'success': overall_success,
            'task_id': self.task_id,
            'project_id': self.project_id,
            'statistics': {
                'total_chunks': len(self.chunks),
                'valuable_chunks': sum(1 for r in self.filter_results if r.is_valuable),
                'filtered_chunks': sum(1 for r in self.filter_results if not r.is_valuable),
                'total_requirements': len(self.requirements),
                'mandatory_requirements': sum(1 for r in self.requirements if r.constraint_type == 'mandatory'),
                'optional_requirements': sum(1 for r in self.requirements if r.constraint_type == 'optional'),
                'scoring_requirements': sum(1 for r in self.requirements if r.constraint_type == 'scoring'),
            },
            'cost': {
                'total_cost': self.total_cost,
                'total_api_calls': self.total_api_calls,
                'filter_cost': self.filter.total_cost,
                'extraction_cost': self.extractor.total_cost
            },
            'performance': {
                'total_time': total_time,
                'total_time_formatted': f"{int(total_time // 60)}分{int(total_time % 60)}秒"
            }
        }

        # 输出最终报告
        logger.info("=" * 60)
        logger.info("📊 处理完成 - 最终报告")
        logger.info("=" * 60)
        logger.info(f"状态: {'✅ 成功' if overall_success else '❌ 失败'}")
        logger.info(f"总耗时: {result['performance']['total_time_formatted']}")
        logger.info(f"总分块: {result['statistics']['total_chunks']}")
        logger.info(f"保留分块: {result['statistics']['valuable_chunks']}")
        logger.info(f"提取要求: {result['statistics']['total_requirements']}")
        logger.info(f"  - 强制性: {result['statistics']['mandatory_requirements']}")
        logger.info(f"  - 可选: {result['statistics']['optional_requirements']}")
        logger.info(f"  - 加分项: {result['statistics']['scoring_requirements']}")
        logger.info(f"总成本: ${self.total_cost:.4f}")
        logger.info(f"API调用: {self.total_api_calls} 次")
        logger.info("=" * 60)

        return result

    def run_step(self, step: int) -> Dict:
        """
        运行指定步骤（用于分步交互式处理）

        Args:
            step: 步骤编号 (1=分块, 2=筛选, 3=提取)

        Returns:
            result: 步骤执行结果
        """
        logger.info(f"🔹 执行步骤 {step}")

        if not hasattr(self, 'start_time') or self.start_time is None:
            self.start_time = time.time()

        # 如果是第一步，创建任务记录
        if step == 1:
            try:
                self.db.create_processing_task(
                    project_id=self.project_id,
                    task_id=self.task_id,
                    pipeline_config={
                        'filter_model': self.filter_model,
                        'extract_model': self.extract_model
                    }
                )
            except Exception as e:
                logger.warning(f"创建任务记录失败: {e}")

        # 执行对应步骤
        success = False
        step_name = ''

        if step == 1:
            step_name = 'chunking'
            success = self.step1_chunking()
        elif step == 2:
            step_name = 'filtering'
            success = self.step2_filtering()
        elif step == 3:
            step_name = 'extraction'
            success = self.step3_extraction()
        else:
            logger.error(f"无效的步骤编号: {step}")
            return {'success': False, 'error': f'无效的步骤编号: {step}'}

        # 构建返回结果
        result = {
            'success': success,
            'task_id': self.task_id,
            'project_id': self.project_id,
            'step': step,
            'step_name': step_name
        }

        # 根据步骤返回相应数据
        if step == 1:
            # 分块完成，返回分块统计
            result['statistics'] = {
                'total_chunks': len(self.chunks),
                'chunks_preview': [
                    {
                        'chunk_id': c.chunk_index,
                        'chunk_type': c.chunk_type,
                        'content_preview': c.content[:100] + '...' if len(c.content) > 100 else c.content,
                        'section_title': c.metadata.get('section_title', ''),
                        'token_count': c.metadata.get('token_count', 0)
                    }
                    for c in self.chunks[:20]  # 只返回前20个分块预览
                ]
            }
        elif step == 2:
            # 筛选完成，返回筛选统计
            result['statistics'] = {
                'total_chunks': len(self.chunks),
                'valuable_chunks': sum(1 for r in self.filter_results if r.is_valuable),
                'filtered_chunks': sum(1 for r in self.filter_results if not r.is_valuable),
                'filter_rate': f"{(sum(1 for r in self.filter_results if not r.is_valuable) / len(self.filter_results) * 100):.1f}%" if self.filter_results else "0%"
            }
        elif step == 3:
            # 提取完成，返回要求统计
            result['statistics'] = {
                'total_requirements': len(self.requirements),
                'mandatory_requirements': sum(1 for r in self.requirements if r.constraint_type == 'mandatory'),
                'optional_requirements': sum(1 for r in self.requirements if r.constraint_type == 'optional'),
                'scoring_requirements': sum(1 for r in self.requirements if r.constraint_type == 'scoring'),
            }

        # 计算成本和时间
        current_time = time.time()
        elapsed_time = current_time - self.start_time

        result['cost'] = {
            'total_cost': self.total_cost,
            'total_api_calls': self.total_api_calls,
        }

        result['performance'] = {
            'elapsed_time': elapsed_time,
            'elapsed_time_formatted': f"{int(elapsed_time // 60)}分{int(elapsed_time % 60)}秒"
        }

        logger.info(f"步骤 {step} {'✅ 完成' if success else '❌ 失败'}")

        return result


if __name__ == '__main__':
    # 测试代码
    sample_document = """
第一章 项目概述

本项目旨在建设一个智能标书处理系统，实现标书的智能分析和要求提取。

第二章 投标人资格要求

2.1 基本资格
投标方必须具有建筑工程施工总承包一级及以上资质，并提供有效的资质证书复印件。

2.2 业绩要求
投标方应具有3年以上类似项目实施经验。提供3个以上成功案例可获得加分。

第三章 技术要求

3.1 系统架构
系统应采用微服务架构，支持水平扩展。建议使用容器化部署。

3.2 性能指标
系统并发用户数不得少于1000人，响应时间应在3秒以内。

第四章 商务条款

4.1 价格要求
投标总价不得超过预算上限500万元。

4.2 付款方式
按照里程碑付款，验收合格后30日内支付。
"""

    def progress_callback(progress):
        print(f"[{progress.step}] {progress.status} - {progress.progress_percentage:.1f}%")

    # 创建流程实例
    pipeline = TenderProcessingPipeline(
        project_id=1,
        document_text=sample_document,
        filter_model='gpt-4o-mini',
        extract_model='yuanjing-deepseek-v3',
        progress_callback=progress_callback
    )

    # 运行流程
    result = pipeline.run()

    print("\n" + "=" * 60)
    print("处理结果:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
