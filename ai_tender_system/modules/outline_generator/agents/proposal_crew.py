#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
技术方案生成协调器 - ProposalCrew

负责编排所有智能体的协作流程，实现端到端的技术方案生成：

完整流程（Quality-First模式）:
1. ScoringPointAgent - 提取评分点
2. ProductMatchAgent - 产品能力匹配
3. ScoringStrategyAgent - 制定评分策略
4. MaterialRetrieverAgent - 检索历史素材
5. OutlineArchitectAgent - 生成大纲结构
6. ContentWriterAgent - 撰写方案内容
7. ExpertReviewAgent - 专家评审
8. (可选) 根据评审结果迭代优化

设计原则：
- 流程可配置，支持跳过某些步骤
- 支持流式输出，实时展示进度
- 错误处理和回退机制
- 支持断点续传
"""

import json
import logging
import time
from typing import Dict, List, Any, Optional, Generator, Callable
from dataclasses import dataclass, field
from enum import Enum

# 导入所有智能体
from .scoring_point_agent import ScoringPointAgent
from .product_match_agent import ProductMatchAgent
from .scoring_strategy_agent import ScoringStrategyAgent
from .material_retriever_agent import MaterialRetrieverAgent
from .outline_architect_agent import OutlineArchitectAgent
from .content_writer_agent import ContentWriterAgent
from .expert_review_agent import ExpertReviewAgent


class CrewPhase(Enum):
    """协作流程阶段"""
    INIT = "init"
    SCORING_EXTRACTION = "scoring_extraction"
    PRODUCT_MATCHING = "product_matching"
    STRATEGY_PLANNING = "strategy_planning"
    MATERIAL_RETRIEVAL = "material_retrieval"
    OUTLINE_GENERATION = "outline_generation"
    CONTENT_WRITING = "content_writing"
    EXPERT_REVIEW = "expert_review"
    ITERATION = "iteration"
    COMPLETE = "complete"
    ERROR = "error"


@dataclass
class CrewConfig:
    """协作器配置"""
    # 模型配置
    model_name: str = "gpt-4o-mini"

    # 流程控制
    skip_product_matching: bool = False
    skip_material_retrieval: bool = False
    enable_expert_review: bool = True
    max_iterations: int = 2  # 最大优化迭代次数

    # 质量阈值
    min_review_score: float = 70.0  # 最低评审分数
    target_word_count: int = 70000  # 目标字数

    # 公司信息
    company_id: int = 1
    company_profile: Dict = field(default_factory=dict)

    # 内容风格
    content_style: Dict = field(default_factory=lambda: {
        "tables": "适量",
        "flowcharts": "适量",
        "images": "少量"
    })


@dataclass
class CrewState:
    """协作器状态"""
    phase: CrewPhase = CrewPhase.INIT
    start_time: float = 0.0

    # 各阶段结果
    scoring_points: List[Dict] = field(default_factory=list)
    product_match_result: Dict = field(default_factory=dict)
    scoring_strategy: Dict = field(default_factory=dict)
    materials: Dict = field(default_factory=dict)
    outline: Dict = field(default_factory=dict)
    proposal_content: Dict = field(default_factory=dict)
    review_result: Dict = field(default_factory=dict)

    # 迭代信息
    iteration_count: int = 0
    iteration_history: List[Dict] = field(default_factory=list)

    # 错误信息
    error: str = ""

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "phase": self.phase.value,
            "iteration_count": self.iteration_count,
            "has_scoring_points": len(self.scoring_points) > 0,
            "has_product_match": bool(self.product_match_result),
            "has_strategy": bool(self.scoring_strategy),
            "has_materials": bool(self.materials.get('material_packages')),
            "has_outline": bool(self.outline.get('outline')),
            "has_content": bool(self.proposal_content.get('chapters')),
            "has_review": bool(self.review_result),
            "error": self.error
        }


class ProposalCrew:
    """
    技术方案生成协调器

    协调多个智能体完成端到端的技术方案生成任务。
    """

    def __init__(self, config: CrewConfig = None):
        """
        初始化协调器

        Args:
            config: 协作器配置
        """
        self.config = config or CrewConfig()
        self.state = CrewState()
        self.logger = logging.getLogger(__name__)

        # 初始化所有智能体
        self._init_agents()

    def _init_agents(self):
        """初始化所有智能体"""
        model = self.config.model_name

        self.scoring_point_agent = ScoringPointAgent(model_name=model)
        self.product_match_agent = ProductMatchAgent(model_name=model)
        self.scoring_strategy_agent = ScoringStrategyAgent(model_name=model)
        self.material_retriever_agent = MaterialRetrieverAgent(model_name=model)
        self.outline_architect_agent = OutlineArchitectAgent(model_name=model)
        self.content_writer_agent = ContentWriterAgent(model_name=model)
        self.expert_review_agent = ExpertReviewAgent(model_name=model)

    def run(
        self,
        tender_doc: str,
        page_count: int = 100,
        callback: Callable[[Dict], None] = None
    ) -> Dict[str, Any]:
        """
        运行完整流程（同步模式）

        Args:
            tender_doc: 招标文件内容
            page_count: 目标页数
            callback: 进度回调函数

        Returns:
            最终结果
        """
        self.state = CrewState()
        self.state.start_time = time.time()

        try:
            # 阶段1: 提取评分点
            self._notify(callback, "scoring_extraction", "开始提取评分点...")
            self._run_scoring_extraction(tender_doc)

            # 阶段2: 产品能力匹配
            if not self.config.skip_product_matching:
                self._notify(callback, "product_matching", "开始产品能力匹配...")
                self._run_product_matching(tender_doc)

            # 阶段3: 制定评分策略
            self._notify(callback, "strategy_planning", "制定评分策略...")
            self._run_strategy_planning()

            # 阶段4: 检索历史素材
            if not self.config.skip_material_retrieval:
                self._notify(callback, "material_retrieval", "检索历史素材...")
                self._run_material_retrieval()

            # 阶段5: 生成大纲
            self._notify(callback, "outline_generation", "生成技术方案大纲...")
            self._run_outline_generation(tender_doc, page_count)

            # 阶段6: 撰写内容
            self._notify(callback, "content_writing", "撰写技术方案内容...")
            self._run_content_writing(tender_doc)

            # 阶段7: 专家评审
            if self.config.enable_expert_review:
                self._notify(callback, "expert_review", "专家评审中...")
                self._run_expert_review(tender_doc)

                # 阶段8: 迭代优化（如果评分不达标）
                while (self.state.review_result.get('overall_score', 0) < self.config.min_review_score
                       and self.state.iteration_count < self.config.max_iterations):
                    self._notify(callback, "iteration", f"第{self.state.iteration_count + 1}轮优化...")
                    self._run_iteration()

            self.state.phase = CrewPhase.COMPLETE
            self._notify(callback, "complete", "技术方案生成完成！")

        except Exception as e:
            self.state.phase = CrewPhase.ERROR
            self.state.error = str(e)
            self.logger.error(f"ProposalCrew执行错误: {e}")
            self._notify(callback, "error", f"执行错误: {e}")

        return self._build_final_result()

    def run_stream(
        self,
        tender_doc: str,
        page_count: int = 100
    ) -> Generator[Dict[str, Any], None, None]:
        """
        运行完整流程（流式模式）

        Args:
            tender_doc: 招标文件内容
            page_count: 目标页数

        Yields:
            各阶段进度和结果
        """
        self.state = CrewState()
        self.state.start_time = time.time()

        try:
            # 阶段1: 提取评分点
            yield {"phase": "scoring_extraction", "status": "running", "message": "提取评分点..."}
            self._run_scoring_extraction(tender_doc)
            yield {
                "phase": "scoring_extraction",
                "status": "complete",
                "result": {
                    "count": len(self.state.scoring_points),
                    "scoring_points": self.state.scoring_points,
                    "dimensions": self._summarize_scoring_dimensions()
                }
            }

            # 阶段2: 产品能力匹配
            if not self.config.skip_product_matching:
                yield {"phase": "product_matching", "status": "running", "message": "产品能力匹配..."}
                self._run_product_matching(tender_doc)
                yield {
                    "phase": "product_matching",
                    "status": "complete",
                    "result": {
                        "summary": self.state.product_match_result.get('summary', {}),
                        "coverage_rate": self.state.product_match_result.get('summary', {}).get('coverage_rate', 0),
                        "matched_count": self.state.product_match_result.get('summary', {}).get('matched_count', 0),
                        "requirement_coverage": self.state.product_match_result.get('requirement_coverage', [])[:10]
                    }
                }
            else:
                yield {"phase": "product_matching", "status": "skipped", "message": "跳过产品匹配"}

            # 阶段3: 制定评分策略
            yield {"phase": "strategy_planning", "status": "running", "message": "制定评分策略..."}
            self._run_strategy_planning()
            yield {
                "phase": "strategy_planning",
                "status": "complete",
                "result": {
                    "estimated_score": self.state.scoring_strategy.get('estimated_score', 0),
                    "confidence": self.state.scoring_strategy.get('confidence', 0),
                    "highlights": self.state.scoring_strategy.get('highlights', [])[:5],
                    "risks": self.state.scoring_strategy.get('risks', [])[:5],
                    "recommendations": self.state.scoring_strategy.get('recommendations', [])[:3]
                }
            }

            # 阶段4: 检索历史素材
            if not self.config.skip_material_retrieval:
                yield {"phase": "material_retrieval", "status": "running", "message": "检索历史素材..."}
                self._run_material_retrieval()
                yield {
                    "phase": "material_retrieval",
                    "status": "complete",
                    "result": {
                        "package_count": len(self.state.materials.get('material_packages', [])),
                        "total_materials": self.state.materials.get('total_materials', 0),
                        "categories": self._summarize_material_categories()
                    }
                }
            else:
                yield {"phase": "material_retrieval", "status": "skipped", "message": "跳过素材检索"}

            # 阶段5: 生成大纲
            yield {"phase": "outline_generation", "status": "running", "message": "生成大纲..."}
            self._run_outline_generation(tender_doc, page_count)
            yield {
                "phase": "outline_generation",
                "status": "complete",
                "result": {
                    "chapter_count": self.state.outline.get('chapter_count', 0),
                    "total_words": self.state.outline.get('total_words', 0),
                    "outline": self.state.outline.get('outline', []),
                    "material_coverage": self.state.outline.get('material_coverage', 0),
                    "scoring_coverage": self.state.outline.get('scoring_coverage', 0)
                }
            }

            # 阶段6: 撰写内容（逐章节输出）
            yield {"phase": "content_writing", "status": "running", "message": "撰写内容..."}

            # 使用流式撰写
            for chunk in self.content_writer_agent.write_proposal_stream(
                outline=self.state.outline,
                materials=self.state.materials,
                tender_doc=tender_doc,
                company_profile=self.config.company_profile,
                content_style=self.config.content_style
            ):
                if chunk.get('type') == 'progress':
                    yield {
                        "phase": "content_writing",
                        "status": "running",
                        "event": "chapter_progress",
                        "chapter_index": chunk.get('chapter_index', 0),
                        "total_chapters": chunk.get('total_chapters', 1),
                        "chapter_title": chunk.get('chapter_title', '')
                    }
                elif chunk.get('type') == 'chapter':
                    yield {
                        "phase": "content_writing",
                        "status": "running",
                        "event": "chapter_complete",
                        "chapter": chunk.get('chapter_content')
                    }

            # 重新获取完整内容
            self._run_content_writing(tender_doc)
            yield {
                "phase": "content_writing",
                "status": "complete",
                "result": {
                    "chapter_count": len(self.state.proposal_content.get('chapters', [])),
                    "total_words": self.state.proposal_content.get('total_words', 0),
                    "quality_metrics": self.state.proposal_content.get('quality_metrics', {})
                }
            }

            # 阶段7: 专家评审
            if self.config.enable_expert_review:
                yield {"phase": "expert_review", "status": "running", "message": "专家评审..."}
                self._run_expert_review(tender_doc)
                yield {
                    "phase": "expert_review",
                    "status": "complete",
                    "result": {
                        "overall_score": self.state.review_result.get('overall_score', 0),
                        "pass_recommendation": self.state.review_result.get('pass_recommendation', False),
                        "dimension_scores": self.state.review_result.get('dimension_scores', []),
                        "strengths": self.state.review_result.get('strengths', [])[:5],
                        "weaknesses": self.state.review_result.get('weaknesses', [])[:5],
                        "improvement_suggestions": self.state.review_result.get('improvement_suggestions', [])[:5],
                        "critical_issues": self.state.review_result.get('critical_issues', [])
                    }
                }

                # 阶段8: 迭代优化（如果评分不达标且启用迭代）
                iteration_count = 0
                while (self.state.review_result.get('overall_score', 0) < self.config.min_review_score
                       and iteration_count < self.config.max_iterations):
                    iteration_count += 1
                    yield {
                        "phase": "iteration",
                        "status": "running",
                        "message": f"第{iteration_count}轮优化...",
                        "iteration": iteration_count,
                        "max_iterations": self.config.max_iterations,
                        "current_score": self.state.review_result.get('overall_score', 0),
                        "target_score": self.config.min_review_score
                    }
                    self._run_iteration()
                    # 重新评审
                    self._run_expert_review(tender_doc)
                    yield {
                        "phase": "iteration",
                        "status": "complete",
                        "iteration": iteration_count,
                        "result": {
                            "new_score": self.state.review_result.get('overall_score', 0),
                            "improved": self.state.review_result.get('overall_score', 0) > self.config.min_review_score
                        }
                    }
            else:
                yield {"phase": "expert_review", "status": "skipped", "message": "跳过专家评审"}

            self.state.phase = CrewPhase.COMPLETE
            yield {
                "phase": "complete",
                "status": "complete",
                "result": self._build_final_result()
            }

        except Exception as e:
            import traceback
            self.state.phase = CrewPhase.ERROR
            error_msg = str(e) if str(e) else '未知错误'
            self.state.error = error_msg
            error_trace = traceback.format_exc()
            self.logger.error(f"ProposalCrew执行错误: {error_msg}\n{error_trace}")
            yield {
                "phase": "error",
                "status": "error",
                "error": error_msg,
                "message": f"执行错误: {error_msg}",
                "traceback": error_trace[:500] if error_trace else ''
            }

    def _run_scoring_extraction(self, tender_doc: str):
        """执行评分点提取"""
        self.state.phase = CrewPhase.SCORING_EXTRACTION
        result = self.scoring_point_agent.extract_scoring_points(tender_doc)
        # extract_scoring_points 返回 List[Dict]，不是字典
        self.state.scoring_points = result if isinstance(result, list) else []
        self.logger.info(f"提取到{len(self.state.scoring_points)}个评分维度")

    def _run_product_matching(self, tender_doc: str):
        """执行产品能力匹配"""
        self.state.phase = CrewPhase.PRODUCT_MATCHING
        self.state.product_match_result = self.product_match_agent.analyze_and_match(
            tender_doc=tender_doc,
            company_id=self.config.company_id
        )
        coverage = self.state.product_match_result.get('summary', {}).get('coverage_rate', 0)
        self.logger.info(f"产品能力覆盖率: {coverage:.0%}")

    def _run_strategy_planning(self):
        """执行评分策略规划"""
        self.state.phase = CrewPhase.STRATEGY_PLANNING
        self.state.scoring_strategy = self.scoring_strategy_agent.analyze_and_strategize(
            scoring_points=self.state.scoring_points,
            product_match_result=self.state.product_match_result
        )
        estimated = self.state.scoring_strategy.get('estimated_score', 0)
        self.logger.info(f"预估得分: {estimated}")

    def _run_material_retrieval(self):
        """执行素材检索"""
        self.state.phase = CrewPhase.MATERIAL_RETRIEVAL
        self.state.materials = self.material_retriever_agent.retrieve_materials(
            scoring_strategy=self.state.scoring_strategy,
            company_id=self.config.company_id
        )
        count = len(self.state.materials.get('material_packages', []))
        self.logger.info(f"检索到{count}个素材包")

    def _run_outline_generation(self, tender_doc: str, page_count: int):
        """执行大纲生成"""
        self.state.phase = CrewPhase.OUTLINE_GENERATION
        self.state.outline = self.outline_architect_agent.build_outline(
            scoring_strategy=self.state.scoring_strategy,
            materials=self.state.materials,
            tender_doc=tender_doc,
            page_count=page_count,
            content_style=self.config.content_style
        )
        chapters = len(self.state.outline.get('outline', []))
        self.logger.info(f"生成{chapters}个一级章节")

    def _run_content_writing(self, tender_doc: str):
        """执行内容撰写"""
        self.state.phase = CrewPhase.CONTENT_WRITING
        self.state.proposal_content = self.content_writer_agent.write_proposal(
            outline=self.state.outline,
            materials=self.state.materials,
            tender_doc=tender_doc,
            company_profile=self.config.company_profile,
            content_style=self.config.content_style
        )
        words = self.state.proposal_content.get('total_words', 0)
        self.logger.info(f"撰写完成，共{words}字")

    def _run_expert_review(self, tender_doc: str):
        """执行专家评审"""
        self.state.phase = CrewPhase.EXPERT_REVIEW
        self.state.review_result = self.expert_review_agent.review_proposal(
            proposal_content=self.state.proposal_content,
            scoring_points=self.state.scoring_points,
            scoring_strategy=self.state.scoring_strategy,
            tender_doc=tender_doc
        )
        score = self.state.review_result.get('overall_score', 0)
        self.logger.info(f"评审得分: {score}")

    def _run_iteration(self):
        """执行优化迭代"""
        self.state.phase = CrewPhase.ITERATION
        self.state.iteration_count += 1

        # 获取改进建议
        suggestions = self.state.review_result.get('improvement_suggestions', [])
        critical_issues = self.state.review_result.get('critical_issues', [])

        # 记录迭代历史
        self.state.iteration_history.append({
            "iteration": self.state.iteration_count,
            "before_score": self.state.review_result.get('overall_score', 0),
            "suggestions_applied": len(suggestions),
            "critical_issues": len(critical_issues)
        })

        # 根据建议重写相关章节
        for suggestion in suggestions[:3]:  # 最多处理3个建议
            target = suggestion.get('target', '')
            for chapter in self.state.proposal_content.get('chapters', []):
                if target in chapter.get('title', ''):
                    self.content_writer_agent.rewrite_chapter(
                        chapter=chapter,
                        feedback=suggestion.get('suggestion', '') + "\n" + suggestion.get('action', '')
                    )

        self.logger.info(f"第{self.state.iteration_count}轮优化完成")

    def _notify(self, callback: Callable, phase: str, message: str):
        """发送进度通知"""
        if callback:
            callback({
                "phase": phase,
                "message": message,
                "state": self.state.to_dict()
            })

    def _summarize_scoring_dimensions(self) -> List[Dict]:
        """
        汇总评分维度信息

        Returns:
            评分维度摘要列表
        """
        dimensions = {}
        for point in self.state.scoring_points:
            dim_name = point.get('dimension', '其他')
            if dim_name not in dimensions:
                dimensions[dim_name] = {
                    "name": dim_name,
                    "count": 0,
                    "total_score": 0,
                    "items": []
                }
            dimensions[dim_name]["count"] += 1
            dimensions[dim_name]["total_score"] += point.get('score', 0)
            dimensions[dim_name]["items"].append(point.get('name', ''))

        return list(dimensions.values())

    def _summarize_material_categories(self) -> List[Dict]:
        """
        汇总素材分类信息

        Returns:
            素材分类摘要列表
        """
        categories = {}
        for package in self.state.materials.get('material_packages', []):
            cat_name = package.get('category', '通用素材')
            if cat_name not in categories:
                categories[cat_name] = {
                    "name": cat_name,
                    "count": 0,
                    "materials": []
                }
            categories[cat_name]["count"] += 1
            mat_name = package.get('name', package.get('title', ''))
            if mat_name:
                categories[cat_name]["materials"].append(mat_name)

        return list(categories.values())

    def _build_final_result(self) -> Dict[str, Any]:
        """构建最终结果"""
        elapsed = time.time() - self.state.start_time

        return {
            "success": self.state.phase == CrewPhase.COMPLETE,
            "elapsed_time": round(elapsed, 2),

            # 评分相关
            "scoring_points": self.state.scoring_points,
            "scoring_strategy": self.state.scoring_strategy,

            # 内容相关
            "outline": self.state.outline,
            "proposal_content": self.state.proposal_content,

            # 评审相关
            "review_result": self.state.review_result,

            # 元数据
            "metadata": {
                "phase": self.state.phase.value,
                "iteration_count": self.state.iteration_count,
                "total_words": self.state.proposal_content.get('total_words', 0),
                "chapter_count": len(self.state.proposal_content.get('chapters', [])),
                "material_count": len(self.state.materials.get('material_packages', [])),
                "final_score": self.state.review_result.get('overall_score', 0),
                "pass_recommendation": self.state.review_result.get('pass_recommendation', False)
            },

            # 错误信息
            "error": self.state.error if self.state.error else None
        }

    def get_state(self) -> Dict[str, Any]:
        """获取当前状态"""
        return self.state.to_dict()

    def resume_from_state(self, saved_state: Dict) -> bool:
        """
        从保存的状态恢复

        Args:
            saved_state: 保存的状态数据

        Returns:
            是否成功恢复
        """
        try:
            # 恢复各阶段结果
            if saved_state.get('scoring_points'):
                self.state.scoring_points = saved_state['scoring_points']
            if saved_state.get('product_match_result'):
                self.state.product_match_result = saved_state['product_match_result']
            if saved_state.get('scoring_strategy'):
                self.state.scoring_strategy = saved_state['scoring_strategy']
            if saved_state.get('materials'):
                self.state.materials = saved_state['materials']
            if saved_state.get('outline'):
                self.state.outline = saved_state['outline']
            if saved_state.get('proposal_content'):
                self.state.proposal_content = saved_state['proposal_content']

            # 恢复阶段
            phase_str = saved_state.get('phase', 'init')
            self.state.phase = CrewPhase(phase_str)

            self.logger.info(f"成功从阶段 {phase_str} 恢复状态")
            return True

        except Exception as e:
            self.logger.error(f"恢复状态失败: {e}")
            return False


def create_proposal_crew(
    model_name: str = "gpt-4o-mini",
    company_id: int = 1,
    company_profile: Dict = None,
    content_style: Dict = None,
    **kwargs
) -> ProposalCrew:
    """
    创建技术方案协调器的便捷函数

    Args:
        model_name: 模型名称
        company_id: 公司ID
        company_profile: 公司信息
        content_style: 内容风格
        **kwargs: 其他配置参数

    Returns:
        ProposalCrew实例
    """
    config = CrewConfig(
        model_name=model_name,
        company_id=company_id,
        company_profile=company_profile or {},
        content_style=content_style or {}
    )

    # 应用其他配置
    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)

    return ProposalCrew(config)
