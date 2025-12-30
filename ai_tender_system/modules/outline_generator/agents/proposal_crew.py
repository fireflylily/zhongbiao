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
from datetime import datetime
from typing import Dict, List, Any, Optional, Generator, Callable
from dataclasses import dataclass, field
from enum import Enum

# 导入重试策略和任务管理器
from ..retry_policy import RetryPolicy, RetryConfig
from ..task_manager import TechProposalTaskManager, PHASE_ORDER, get_task_manager

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

    # 项目信息
    project_name: str = ''  # 项目名称
    customer_name: str = ''  # 客户名称（招标方）

    # 内容风格
    content_style: Dict = field(default_factory=lambda: {
        "tables": "适量",
        "flowcharts": "适量",
        "images": "少量"
    })

    # 重试配置
    max_retries: int = 3  # 单个阶段最大重试次数
    retry_base_delay: float = 2.0  # 重试基础延迟(秒)
    retry_backoff_factor: float = 2.0  # 重试退避因子


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
        """转换为字典(摘要，用于进度展示)"""
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

    def to_full_dict(self) -> Dict:
        """转换为完整字典(用于断点恢复)"""
        return {
            "phase": self.phase.value,
            "start_time": self.start_time,
            "scoring_points": self.scoring_points,
            "product_match_result": self.product_match_result,
            "scoring_strategy": self.scoring_strategy,
            "materials": self.materials,
            "outline": self.outline,
            "proposal_content": self.proposal_content,
            "review_result": self.review_result,
            "iteration_count": self.iteration_count,
            "iteration_history": self.iteration_history,
            "error": self.error
        }


class ProposalCrew:
    """
    技术方案生成协调器

    协调多个智能体完成端到端的技术方案生成任务。
    """

    def __init__(self, config: CrewConfig = None, task_manager: TechProposalTaskManager = None):
        """
        初始化协调器

        Args:
            config: 协作器配置
            task_manager: 任务管理器(可选，用于断点续传)
        """
        self.config = config or CrewConfig()
        self.state = CrewState()
        self.logger = logging.getLogger(__name__)

        # 任务管理器(可选)
        self.task_manager = task_manager

        # 当前任务ID(用于断点续传)
        self.current_task_id: Optional[str] = None

        # 初始化重试策略
        self.retry_policy = RetryPolicy(RetryConfig(
            max_attempts=self.config.max_retries,
            base_delay=self.config.retry_base_delay,
            backoff_factor=self.config.retry_backoff_factor
        ))

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
            # 阶段1: 提取评分点（带细粒度进度）
            yield {"phase": "scoring_extraction", "status": "running", "message": "提取评分点..."}
            # 模拟分步骤进度：分析不同评分维度
            scoring_steps = ["技术架构", "项目管理", "服务保障", "人员配置", "实施方案"]
            completed_steps = []
            for i, step in enumerate(scoring_steps):
                yield {
                    "phase": "scoring_extraction",
                    "status": "running",
                    "detail": {
                        "step": i + 1,
                        "totalSteps": len(scoring_steps),
                        "stepName": f"分析{step}评分维度",
                        "subItems": completed_steps.copy()
                    }
                }
                completed_steps.append(step)
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

            # 阶段2: 产品能力匹配（带细粒度进度）
            if not self.config.skip_product_matching:
                yield {"phase": "product_matching", "status": "running", "message": "产品能力匹配..."}
                # 获取评分点作为匹配步骤
                match_steps = [p.get('name', f'评分点{i+1}') for i, p in enumerate(self.state.scoring_points[:8])]
                completed_matches = []
                for i, step in enumerate(match_steps):
                    yield {
                        "phase": "product_matching",
                        "status": "running",
                        "detail": {
                            "step": i + 1,
                            "totalSteps": len(match_steps),
                            "stepName": f"匹配: {step[:15]}...",
                            "subItems": completed_matches.copy()
                        }
                    }
                    completed_matches.append(step[:10])
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

            # 阶段3: 制定评分策略（带细粒度进度）
            yield {"phase": "strategy_planning", "status": "running", "message": "制定评分策略..."}
            strategy_steps = ["分析竞争优势", "识别风险点", "制定得分策略", "生成建议"]
            completed_strategy = []
            for i, step in enumerate(strategy_steps):
                yield {
                    "phase": "strategy_planning",
                    "status": "running",
                    "detail": {
                        "step": i + 1,
                        "totalSteps": len(strategy_steps),
                        "stepName": step,
                        "subItems": completed_strategy.copy()
                    }
                }
                completed_strategy.append(step)
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

            # 阶段4: 检索历史素材（带细粒度进度）
            if not self.config.skip_material_retrieval:
                yield {"phase": "material_retrieval", "status": "running", "message": "检索历史素材..."}
                retrieval_steps = ["技术方案素材", "案例素材", "资质证书", "团队介绍", "服务承诺"]
                completed_retrieval = []
                for i, step in enumerate(retrieval_steps):
                    yield {
                        "phase": "material_retrieval",
                        "status": "running",
                        "detail": {
                            "step": i + 1,
                            "totalSteps": len(retrieval_steps),
                            "stepName": f"检索{step}",
                            "subItems": completed_retrieval.copy()
                        }
                    }
                    completed_retrieval.append(step)
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

            # 阶段5: 生成大纲（带细粒度进度）
            yield {"phase": "outline_generation", "status": "running", "message": "生成大纲..."}
            outline_steps = ["分析文档结构", "规划章节框架", "分配页面预算", "生成详细大纲"]
            completed_outline = []
            for i, step in enumerate(outline_steps):
                yield {
                    "phase": "outline_generation",
                    "status": "running",
                    "detail": {
                        "step": i + 1,
                        "totalSteps": len(outline_steps),
                        "stepName": step,
                        "subItems": completed_outline.copy()
                    }
                }
                completed_outline.append(step)
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

            # 阶段6: 撰写内容（逐章节输出，带流式预览）
            yield {"phase": "content_writing", "status": "running", "message": "撰写内容..."}

            # 获取章节总数用于进度显示
            outline_chapters = self.state.outline.get('outline', [])
            total_chapters = len(outline_chapters)

            # 使用流式撰写
            for chunk in self.content_writer_agent.write_proposal_stream(
                outline=self.state.outline,
                materials=self.state.materials,
                tender_doc=tender_doc,
                company_profile=self.config.company_profile,
                content_style=self.config.content_style,
                project_name=self.config.project_name,
                customer_name=self.config.customer_name
            ):
                if chunk.get('type') == 'progress':
                    chapter_index = chunk.get('chapter_index', 0)
                    chapter_title = chunk.get('chapter_title', '')
                    # 发送章节进度和detail
                    yield {
                        "phase": "content_writing",
                        "status": "running",
                        "event": "chapter_progress",
                        "chapter_index": chapter_index,
                        "total_chapters": chunk.get('total_chapters', total_chapters),
                        "chapter_title": chapter_title,
                        "detail": {
                            "step": chapter_index + 1,
                            "totalSteps": total_chapters,
                            "stepName": f"撰写: {chapter_title[:20]}",
                            "subItems": []
                        },
                        # 发送章节开始信息用于预览
                        "content": {
                            "chapterNumber": str(chapter_index + 1),
                            "chapterTitle": chapter_title
                        }
                    }
                elif chunk.get('type') == 'content_chunk':
                    # 流式内容片段（用于实时预览）
                    yield {
                        "phase": "content_writing",
                        "status": "running",
                        "content": {
                            "chapterNumber": str(chunk.get('chapter_index', 0) + 1),
                            "chapterTitle": chunk.get('chapter_title', ''),
                            "contentChunk": chunk.get('content', ''),
                            "wordCount": chunk.get('word_count', 0)
                        }
                    }
                elif chunk.get('type') == 'chapter':
                    chapter_content = chunk.get('chapter_content', {})
                    # 添加 chapter_number 以便前端正确索引
                    chapter_index = chunk.get('chapter_index', 0)
                    chapter_content['chapter_number'] = str(chapter_index + 1)

                    # 章节完成，通知前端清空预览
                    yield {
                        "phase": "content_writing",
                        "status": "running",
                        "event": "chapter_complete",
                        "chapter": chapter_content,
                        "content": {
                            "chapterNumber": str(chapter_index + 1),
                            "isComplete": True
                        }
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

            # 阶段7: 专家评审（带细粒度进度）
            if self.config.enable_expert_review:
                yield {"phase": "expert_review", "status": "running", "message": "专家评审..."}
                review_steps = ["技术方案评审", "完整性检查", "合规性验证", "评分计算"]
                completed_review = []
                for i, step in enumerate(review_steps):
                    yield {
                        "phase": "expert_review",
                        "status": "running",
                        "detail": {
                            "step": i + 1,
                            "totalSteps": len(review_steps),
                            "stepName": step,
                            "subItems": completed_review.copy()
                        }
                    }
                    completed_review.append(step)
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
            content_style=self.config.content_style,
            project_name=self.config.project_name,
            customer_name=self.config.customer_name
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

    # =========================
    # 断点续传支持方法
    # =========================

    def _get_phase_method(self, phase: str, tender_doc: str, page_count: int) -> Callable:
        """获取阶段执行方法"""
        phase_methods = {
            "scoring_extraction": lambda: self._run_scoring_extraction(tender_doc),
            "product_matching": lambda: self._run_product_matching(tender_doc),
            "strategy_planning": lambda: self._run_strategy_planning(),
            "material_retrieval": lambda: self._run_material_retrieval(),
            "outline_generation": lambda: self._run_outline_generation(tender_doc, page_count),
            "content_writing": lambda: self._run_content_writing(tender_doc),
            "expert_review": lambda: self._run_expert_review(tender_doc),
        }
        return phase_methods.get(phase)

    def _should_skip_phase(self, phase: str) -> bool:
        """判断是否应该跳过某阶段"""
        if phase == "product_matching" and self.config.skip_product_matching:
            return True
        if phase == "material_retrieval" and self.config.skip_material_retrieval:
            return True
        if phase == "expert_review" and not self.config.enable_expert_review:
            return True
        return False

    def _execute_phase_with_retry(
        self,
        phase: str,
        tender_doc: str,
        page_count: int,
        on_retry: Callable = None
    ) -> bool:
        """
        带重试的阶段执行

        Args:
            phase: 阶段名称
            tender_doc: 招标文件
            page_count: 目标页数
            on_retry: 重试回调

        Returns:
            是否成功
        """
        phase_method = self._get_phase_method(phase, tender_doc, page_count)
        if not phase_method:
            self.logger.error(f"未知阶段: {phase}")
            return False

        start_time = datetime.now()
        agent_name = self._get_agent_name_for_phase(phase)

        try:
            # 使用重试策略执行
            self.retry_policy.execute_with_retry(
                phase_method,
                on_retry=on_retry
            )

            # 记录执行日志
            if self.task_manager and self.current_task_id:
                end_time = datetime.now()
                duration_ms = int((end_time - start_time).total_seconds() * 1000)
                self.task_manager.log_agent_execution(
                    task_id=self.current_task_id,
                    agent_name=agent_name,
                    phase_name=phase,
                    status="success",
                    start_time=start_time,
                    end_time=end_time,
                    duration_ms=duration_ms
                )

            return True

        except Exception as e:
            # 记录失败日志
            if self.task_manager and self.current_task_id:
                end_time = datetime.now()
                duration_ms = int((end_time - start_time).total_seconds() * 1000)
                self.task_manager.log_agent_execution(
                    task_id=self.current_task_id,
                    agent_name=agent_name,
                    phase_name=phase,
                    status="failed",
                    start_time=start_time,
                    end_time=end_time,
                    duration_ms=duration_ms,
                    error_message=str(e)
                )

            raise

    def _get_agent_name_for_phase(self, phase: str) -> str:
        """获取阶段对应的智能体名称"""
        mapping = {
            "scoring_extraction": "ScoringPointAgent",
            "product_matching": "ProductMatchAgent",
            "strategy_planning": "ScoringStrategyAgent",
            "material_retrieval": "MaterialRetrieverAgent",
            "outline_generation": "OutlineArchitectAgent",
            "content_writing": "ContentWriterAgent",
            "expert_review": "ExpertReviewAgent",
            "iteration": "ContentWriterAgent"
        }
        return mapping.get(phase, "UnknownAgent")

    def run_stream_with_recovery(
        self,
        task_id: str,
        tender_doc: str,
        page_count: int = 100
    ) -> Generator[Dict[str, Any], None, None]:
        """
        支持断点恢复的流式运行

        Args:
            task_id: 任务ID
            tender_doc: 招标文件内容
            page_count: 目标页数

        Yields:
            各阶段进度和结果
        """
        self.current_task_id = task_id

        if not self.task_manager:
            self.task_manager = get_task_manager()

        # 加载任务信息
        task = self.task_manager.get_task(task_id)
        if not task:
            yield {"phase": "error", "status": "error", "error": f"任务 {task_id} 不存在"}
            return

        # 获取已完成的阶段
        completed_phases = set(self.task_manager.get_completed_phases(task_id))

        # 恢复已保存的状态
        saved_state = self.task_manager.load_state(task_id)
        if saved_state:
            self.resume_from_state(saved_state)
            yield {
                "phase": "init",
                "status": "resumed",
                "message": f"从 {len(completed_phases)} 个已完成阶段恢复",
                "task_id": task_id,
                "completed_phases": list(completed_phases)
            }
        else:
            self.state = CrewState()
            self.state.start_time = time.time()

        # 启动任务
        self.task_manager.start_task(task_id)

        # 定义阶段执行顺序
        phases_to_run = [
            "scoring_extraction",
            "product_matching",
            "strategy_planning",
            "material_retrieval",
            "outline_generation",
            "content_writing",
            "expert_review"
        ]

        try:
            for phase in phases_to_run:
                # 检查是否应该跳过
                if self._should_skip_phase(phase):
                    yield {"phase": phase, "status": "skipped", "message": f"跳过 {phase}"}
                    continue

                # 检查是否已完成
                if phase in completed_phases:
                    yield {
                        "phase": phase,
                        "status": "skipped",
                        "message": f"{phase} 已完成，跳过",
                        "recovered": True
                    }
                    continue

                # 发送开始事件
                yield {"phase": phase, "status": "running", "message": f"开始执行 {phase}..."}

                # 重试回调
                def on_retry(attempt, error, delay):
                    # 这里可以yield重试事件，但Generator不支持嵌套yield
                    self.logger.warning(f"阶段 {phase} 第{attempt}次失败，{delay}秒后重试: {error}")

                # 执行阶段
                try:
                    self._execute_phase_with_retry(phase, tender_doc, page_count, on_retry)

                    # 更新任务状态
                    self.task_manager.update_phase(task_id, phase, "success")

                    # 保存中间状态
                    self.task_manager.save_state(task_id, self.state.to_full_dict())

                    # 发送完成事件
                    yield {
                        "phase": phase,
                        "status": "complete",
                        "result": self._get_phase_result(phase)
                    }

                except Exception as e:
                    # 更新任务状态为失败
                    self.task_manager.update_phase(task_id, phase, "failed", error=str(e))
                    self.task_manager.save_state(task_id, self.state.to_full_dict())

                    yield {
                        "phase": phase,
                        "status": "error",
                        "error": str(e),
                        "can_resume": True,
                        "task_id": task_id
                    }
                    return

            # 迭代优化(如果需要)
            if self.config.enable_expert_review:
                iteration_count = 0
                while (self.state.review_result.get('overall_score', 0) < self.config.min_review_score
                       and iteration_count < self.config.max_iterations):
                    iteration_count += 1
                    yield {
                        "phase": "iteration",
                        "status": "running",
                        "message": f"第{iteration_count}轮优化...",
                        "iteration": iteration_count
                    }
                    self._run_iteration()
                    self._run_expert_review(tender_doc)
                    yield {
                        "phase": "iteration",
                        "status": "complete",
                        "iteration": iteration_count,
                        "result": {"new_score": self.state.review_result.get('overall_score', 0)}
                    }

            # 完成任务
            self.state.phase = CrewPhase.COMPLETE
            self.task_manager.complete_task(
                task_id,
                final_score=self.state.review_result.get('overall_score')
            )

            yield {
                "phase": "complete",
                "status": "complete",
                "task_id": task_id,
                "result": self._build_final_result()
            }

        except Exception as e:
            import traceback
            self.state.phase = CrewPhase.ERROR
            self.state.error = str(e)
            self.task_manager.fail_task(task_id, str(e))

            yield {
                "phase": "error",
                "status": "error",
                "error": str(e),
                "traceback": traceback.format_exc()[:500],
                "can_resume": True,
                "task_id": task_id
            }

    def _get_phase_result(self, phase: str) -> Dict:
        """获取阶段执行结果摘要"""
        results = {
            "scoring_extraction": {
                "count": len(self.state.scoring_points),
                "dimensions": self._summarize_scoring_dimensions()
            },
            "product_matching": {
                "coverage_rate": self.state.product_match_result.get('summary', {}).get('coverage_rate', 0),
                "matched_count": self.state.product_match_result.get('summary', {}).get('matched_count', 0)
            },
            "strategy_planning": {
                "estimated_score": self.state.scoring_strategy.get('estimated_score', 0),
                "highlights": len(self.state.scoring_strategy.get('highlights', []))
            },
            "material_retrieval": {
                "package_count": len(self.state.materials.get('material_packages', [])),
                "total_materials": self.state.materials.get('total_materials', 0)
            },
            "outline_generation": {
                "chapter_count": self.state.outline.get('chapter_count', 0),
                "total_words": self.state.outline.get('total_words', 0)
            },
            "content_writing": {
                "chapter_count": len(self.state.proposal_content.get('chapters', [])),
                "total_words": self.state.proposal_content.get('total_words', 0)
            },
            "expert_review": {
                "overall_score": self.state.review_result.get('overall_score', 0),
                "pass_recommendation": self.state.review_result.get('pass_recommendation', False)
            }
        }
        return results.get(phase, {})


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
