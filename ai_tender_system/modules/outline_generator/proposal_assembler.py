#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
方案组装器 - 阶段4
组装最终的技术方案文档
"""

from typing import Dict, List, Any, Optional, Tuple, Generator
from pathlib import Path
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

# 导入公共模块
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from common import get_module_logger, get_prompt_manager
from common.llm_client import create_llm_client


class ProposalAssembler:
    """方案组装器"""

    def __init__(self, model_name: str = "gpt-4o-mini", api_key: Optional[str] = None, use_batch_generation: bool = True):
        """
        初始化方案组装器

        Args:
            model_name: LLM模型名称
            api_key: API密钥（可选）
            use_batch_generation: 是否使用批量生成（默认True）
        """
        self.logger = get_module_logger("proposal_assembler")
        self.prompt_manager = get_prompt_manager()
        self.llm_client = create_llm_client(model_name, api_key)
        self.use_batch_generation = use_batch_generation
        self.logger.info(
            f"方案组装器初始化完成，使用模型: {model_name}, "
            f"批量生成: {'开启' if use_batch_generation else '关闭'}"
        )

    def assemble_proposal(
        self,
        outline: Dict[str, Any],
        analysis: Dict[str, Any],
        matched_docs: Dict[str, List[Dict]],
        options: Optional[Dict[str, bool]] = None
    ) -> Dict[str, Any]:
        """
        组装技术方案

        Args:
            outline: 大纲数据
            analysis: 需求分析结果
            matched_docs: 匹配的产品文档
            options: 生成选项

        Returns:
            方案数据
        """
        try:
            self.logger.info("开始组装技术方案...")

            if options is None:
                options = {}

            proposal = {
                'metadata': {
                    'title': outline.get('outline_title', '技术方案'),
                    'generation_time': outline.get('generation_time', ''),
                    'total_chapters': outline.get('total_chapters', 0),
                    'estimated_pages': outline.get('estimated_pages', 0)
                },
                'chapters': [],
                'attachments': []
            }

            # 组装主要章节
            proposal['chapters'] = self._assemble_chapters(
                outline.get('chapters', []),
                analysis,
                matched_docs
            )

            # 组装附件列表
            if options.get('include_analysis', False):
                proposal['attachments'].append({
                    'type': 'analysis',
                    'title': '需求分析报告',
                    'data': analysis
                })

            if options.get('include_mapping', False):
                proposal['attachments'].append({
                    'type': 'mapping',
                    'title': '需求匹配表',
                    'data': self._create_mapping_table(analysis, matched_docs)
                })

            if options.get('include_summary', False):
                proposal['attachments'].append({
                    'type': 'summary',
                    'title': '生成报告',
                    'data': self._create_summary_report(proposal, analysis, matched_docs)
                })

            self.logger.info("技术方案组装完成")
            return proposal

        except Exception as e:
            self.logger.error(f"方案组装失败: {e}", exc_info=True)
            raise

    def assemble_proposal_stream(
        self,
        outline: Dict[str, Any],
        analysis: Dict[str, Any],
        matched_docs: Dict[str, List[Dict]],
        options: Optional[Dict[str, bool]] = None
    ) -> Generator[Dict[str, Any], None, None]:
        """
        流式组装技术方案（Generator版本）
        每生成一个章节的内容就yield给调用者

        Args:
            outline: 大纲数据
            analysis: 需求分析结果
            matched_docs: 匹配的产品文档
            options: 生成选项

        Yields:
            Dict: 包含章节信息和内容的字典
                {'type': 'chapter_start', 'chapter': {...}}
                {'type': 'content_chunk', 'chunk': 'text...'}
                {'type': 'chapter_end', 'chapter': {...}}
                {'type': 'completed', 'proposal': {...}}
        """
        try:
            self.logger.info("开始流式组装技术方案...")

            if options is None:
                options = {}

            # 初始化方案结构
            proposal = {
                'metadata': {
                    'title': outline.get('outline_title', '技术方案'),
                    'generation_time': outline.get('generation_time', ''),
                    'total_chapters': outline.get('total_chapters', 0),
                    'estimated_pages': outline.get('estimated_pages', 0)
                },
                'chapters': [],
                'attachments': []
            }

            chapters = outline.get('chapters', [])
            total_matched_docs = sum(len(docs) for docs in matched_docs.values())

            # 如果没有产品文档匹配，使用流式AI生成
            if total_matched_docs == 0:
                self.logger.info(f"无产品文档匹配，开始并发流式生成 {len(chapters)} 个章节...")

                # ✅ 并发生成所有主章节（不包括子章节）
                with ThreadPoolExecutor(max_workers=3) as executor:
                    # 提交所有章节生成任务
                    future_to_chapter = {
                        executor.submit(self._generate_chapter_stream_safe, ch, analysis): ch
                        for ch in chapters
                    }

                    # 按完成顺序处理结果（谁先完成先处理谁）
                    completed_chapters = {}
                    for future in as_completed(future_to_chapter, timeout=None):
                        original_chapter = future_to_chapter[future]

                        try:
                            # ✅ 单章节120秒超时保护
                            chapter_num, chapter_title, content = future.result(timeout=130)

                            # 推送章节开始事件
                            yield {
                                'type': 'chapter_start',
                                'chapter_number': chapter_num,
                                'chapter_title': chapter_title
                            }

                            # 推送内容（一次性推送）
                            yield {
                                'type': 'content_chunk',
                                'chapter_number': chapter_num,
                                'chunk': content
                            }

                            # 推送章节完成事件
                            yield {
                                'type': 'chapter_end',
                                'chapter_number': chapter_num,
                                'chapter_title': chapter_title
                            }

                            # 保存结果
                            completed_chapters[chapter_num] = (original_chapter, content)

                        except TimeoutError as e:
                            # 超时降级
                            chapter_title = original_chapter.get('title', '')
                            chapter_num = original_chapter.get('chapter_number', '')
                            self.logger.error(f"章节'{chapter_title}'生成超时(130秒)，使用模板")

                            template = self._generate_template_content(original_chapter)
                            completed_chapters[chapter_num] = (original_chapter, template)

                            yield {
                                'type': 'chapter_timeout',
                                'chapter_number': chapter_num,
                                'chapter_title': chapter_title,
                                'message': f'章节超时，已使用模板'
                            }
                        except Exception as e:
                            chapter_title = original_chapter.get('title', '')
                            self.logger.error(f"章节'{chapter_title}'生成失败: {e}")

                # ✅ 按原始顺序组装章节（保持文档结构）
                for chapter in chapters:
                    chapter_num = chapter.get('chapter_number', '')

                    if chapter_num in completed_chapters:
                        original_chapter, content = completed_chapters[chapter_num]

                        assembled_chapter = {
                            'chapter_number': chapter_num,
                            'level': chapter.get('level', 1),
                            'title': chapter.get('title', ''),
                            'description': chapter.get('description', ''),
                            'response_strategy': chapter.get('response_strategy', ''),
                            'content_hints': chapter.get('content_hints', []),
                            'response_tips': chapter.get('response_tips', []),
                            'suggested_references': chapter.get('suggested_references', []),
                            'evidence_needed': chapter.get('evidence_needed', []),
                            'ai_generated_content': content,
                            'subsections': []
                        }

                        # 处理子章节（串行，因为子章节通常较少）
                        if 'subsections' in chapter and chapter['subsections']:
                            self.logger.info(f"开始生成 {len(chapter['subsections'])} 个子章节...")

                            for subsection in chapter['subsections']:
                                subsection_num = subsection.get('chapter_number', '')
                                subsection_title = subsection.get('title', '')

                                # 推送子章节开始
                                yield {
                                    'type': 'subsection_start',
                                    'chapter_number': chapter_num,
                                    'subsection_number': subsection_num,
                                    'subsection_title': subsection_title
                                }

                                # 生成子章节
                                _, _, sub_content = self._generate_chapter_stream_safe(subsection, analysis)

                                # 推送内容
                                yield {
                                    'type': 'content_chunk',
                                    'chapter_number': subsection_num,
                                    'chunk': sub_content
                                }

                                # 组装子章节
                                assembled_subsection = {
                                    'chapter_number': subsection_num,
                                    'level': subsection.get('level', 2),
                                    'title': subsection_title,
                                    'description': subsection.get('description', ''),
                                    'response_strategy': subsection.get('response_strategy', ''),
                                    'content_hints': subsection.get('content_hints', []),
                                    'response_tips': subsection.get('response_tips', []),
                                    'suggested_references': subsection.get('suggested_references', []),
                                    'evidence_needed': subsection.get('evidence_needed', []),
                                    'ai_generated_content': sub_content
                                }

                                assembled_chapter['subsections'].append(assembled_subsection)

                                # 推送子章节完成
                                yield {
                                    'type': 'subsection_end',
                                    'chapter_number': chapter_num,
                                    'subsection_number': subsection_num,
                                    'subsection_title': subsection_title
                                }

                        proposal['chapters'].append(assembled_chapter)
            else:
                # 有匹配文档时，使用非流式方法
                proposal['chapters'] = self._assemble_chapters(chapters, analysis, matched_docs)

            # 组装附件
            if options.get('include_analysis', False):
                proposal['attachments'].append({
                    'type': 'analysis',
                    'title': '需求分析报告',
                    'data': analysis
                })

            if options.get('include_mapping', False):
                proposal['attachments'].append({
                    'type': 'mapping',
                    'title': '需求匹配表',
                    'data': self._create_mapping_table(analysis, matched_docs)
                })

            if options.get('include_summary', False):
                proposal['attachments'].append({
                    'type': 'summary',
                    'title': '生成报告',
                    'data': self._create_summary_report(proposal, analysis, matched_docs)
                })

            # 推送完成事件
            yield {
                'type': 'completed',
                'proposal': proposal
            }

            self.logger.info("流式技术方案组装完成")

        except Exception as e:
            self.logger.error(f"流式方案组装失败: {e}", exc_info=True)
            yield {
                'type': 'error',
                'error': str(e)
            }

    def _generate_batch_chapters_content(
        self, chapters: List[Dict], analysis: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        批量生成多个章节的AI内容（减少LLM调用次数）

        Args:
            chapters: 章节列表
            analysis: 需求分析结果

        Returns:
            {chapter_number: ai_content} 的字典
        """
        try:
            if not chapters:
                return {}

            self.logger.info(f"开始批量生成 {len(chapters)} 个章节的内容...")

            # 构建批量提示词
            chapters_info = []
            for chapter in chapters:
                chapter_info = {
                    'chapter_number': chapter.get('chapter_number', ''),
                    'title': chapter.get('title', ''),
                    'description': chapter.get('description', ''),
                    'content_hints': chapter.get('content_hints', []),
                    'response_tips': chapter.get('response_tips', [])
                }
                chapters_info.append(chapter_info)

            # 构建批量生成提示词
            prompt = f"""请为技术方案的以下章节批量生成详细内容。每个章节独立生成，互不影响。

章节列表:
{json.dumps(chapters_info, ensure_ascii=False, indent=2)}

要求:
1. 每个章节内容专业、详实，符合技术方案的标准
2. 突出技术先进性和可行性
3. 语言简洁明了，逻辑清晰
4. 每个章节字数控制在800-1500字
5. 使用中文撰写

请以JSON格式返回结果，格式如下:
{{
  "chapters": [
    {{
      "chapter_number": "1",
      "title": "章节标题",
      "content": "章节详细内容..."
    }},
    ...
  ]
}}

请生成所有章节的内容:"""

            # 调用LLM（增加max_tokens以支持多个章节）
            chapter_count = len(chapters)
            max_tokens = min(12000, 2000 * chapter_count)  # 每章节约2000 tokens，最多12000

            self.logger.info(f"批量生成配置: max_tokens={max_tokens}, 章节数={chapter_count}")

            response = self.llm_client.call(
                prompt=prompt,
                temperature=0.7,
                max_tokens=max_tokens,
                max_retries=2,
                purpose=f"批量章节内容生成 ({chapter_count}章)"
            )

            # 解析响应
            if not response:
                self.logger.warning("批量生成返回空响应")
                return {}

            # 提取JSON
            import re
            response = re.sub(r'^```json\s*', '', response.strip())
            response = re.sub(r'\s*```$', '', response.strip())

            json_start = response.find('{')
            json_end = response.rfind('}') + 1

            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                try:
                    result = json.loads(json_str)
                    generated_chapters = result.get('chapters', [])

                    # 构建结果字典
                    content_map = {}
                    for gen_chapter in generated_chapters:
                        chapter_num = gen_chapter.get('chapter_number', '')
                        content = gen_chapter.get('content', '')
                        if chapter_num and content:
                            content_map[chapter_num] = content

                    self.logger.info(f"✓ 批量生成成功，生成了 {len(content_map)} 个章节的内容")
                    return content_map

                except json.JSONDecodeError as e:
                    self.logger.error(f"批量生成JSON解析失败: {e}")
                    return {}
            else:
                self.logger.warning("批量生成响应中未找到有效JSON")
                return {}

        except Exception as e:
            self.logger.error(f"批量生成章节内容失败: {e}")
            return {}

    def _generate_chapter_with_content(
        self, chapter: Dict, analysis: Dict[str, Any]
    ) -> Tuple[Dict, Optional[str]]:
        """
        为单个章节生成AI内容（用于并发调用）

        Args:
            chapter: 章节信息
            analysis: 需求分析结果

        Returns:
            (组装后的章节基础结构, AI生成的内容或None)
        """
        assembled_chapter = {
            'chapter_number': chapter.get('chapter_number', ''),
            'level': chapter.get('level', 1),
            'title': chapter.get('title', ''),
            'description': chapter.get('description', ''),
            'response_strategy': chapter.get('response_strategy', ''),
            'content_hints': chapter.get('content_hints', []),
            'response_tips': chapter.get('response_tips', []),
            'suggested_references': chapter.get('suggested_references', []),
            'evidence_needed': chapter.get('evidence_needed', []),
            'subsections': []
        }

        # 生成AI内容
        ai_content = self._generate_chapter_content_with_ai(chapter, analysis)
        return assembled_chapter, ai_content

    def _assemble_chapters(
        self,
        chapters: List[Dict],
        analysis: Dict[str, Any],
        matched_docs: Dict[str, List[Dict]]
    ) -> List[Dict]:
        """
        组装章节内容（并发版本）

        Args:
            chapters: 大纲章节列表
            analysis: 需求分析
            matched_docs: 匹配的文档

        Returns:
            组装后的章节列表
        """
        assembled_chapters = []
        total_matched_docs = sum(len(docs) for docs in matched_docs.values())

        # 如果没有匹配到产品文档，使用AI生成章节内容
        if total_matched_docs == 0:
            # 选择生成模式：批量生成 vs 并发生成
            if self.use_batch_generation and len(chapters) > 2:
                # 批量生成模式（适合3个以上章节）
                self.logger.info(f"使用批量生成模式，一次性生成 {len(chapters)} 个章节的AI内容...")

                batch_content_map = self._generate_batch_chapters_content(chapters, analysis)

                # 按原顺序组装章节
                for chapter in chapters:
                    chapter_num = chapter.get('chapter_number', '')
                    assembled_chapter = {
                        'chapter_number': chapter_num,
                        'level': chapter.get('level', 1),
                        'title': chapter.get('title', ''),
                        'description': chapter.get('description', ''),
                        'response_strategy': chapter.get('response_strategy', ''),
                        'content_hints': chapter.get('content_hints', []),
                        'response_tips': chapter.get('response_tips', []),
                        'suggested_references': chapter.get('suggested_references', []),
                        'evidence_needed': chapter.get('evidence_needed', []),
                        'subsections': []
                    }

                    # 添加批量生成的内容
                    ai_content = batch_content_map.get(chapter_num)
                    if ai_content:
                        assembled_chapter['ai_generated_content'] = ai_content
                        self.logger.info(f"✓ 章节'{chapter.get('title')}'已添加批量生成内容")
                    else:
                        self.logger.warning(f"⚠️  章节'{chapter.get('title')}'批量生成失败，尝试单独生成")
                        # 批量生成失败，单独生成
                        fallback_content = self._generate_chapter_content_with_ai(chapter, analysis)
                        if fallback_content:
                            assembled_chapter['ai_generated_content'] = fallback_content

                    # 处理子章节
                    if 'subsections' in chapter and chapter['subsections']:
                        assembled_chapter['subsections'] = self._assemble_subsections(
                            chapter['subsections'],
                            analysis,
                            matched_docs
                        )

                    assembled_chapters.append(assembled_chapter)
            else:
                # 并发生成模式（适合少量章节或禁用批量生成）
                self.logger.info(f"使用并发生成模式，并发生成 {len(chapters)} 个章节的AI内容...")

                with ThreadPoolExecutor(max_workers=5) as executor:
                    # 提交所有章节的生成任务
                    future_to_chapter = {
                        executor.submit(self._generate_chapter_with_content, ch, analysis): ch
                        for ch in chapters
                    }

                    # 收集结果
                    chapter_results = {}
                    completed_count = 0
                    failed_count = 0

                    for future in as_completed(future_to_chapter):
                        original_chapter = future_to_chapter[future]
                        try:
                            assembled_chapter, ai_content = future.result(timeout=150)
                            chapter_results[id(original_chapter)] = (assembled_chapter, ai_content)

                            if ai_content:
                                chapter_title = original_chapter.get('title', '未知章节')
                                self.logger.info(f"✓ 章节'{chapter_title}'AI内容生成成功")
                                completed_count += 1
                            else:
                                failed_count += 1
                        except Exception as e:
                            chapter_title = original_chapter.get('title', '未知章节')
                            self.logger.warning(f"❌ 章节'{chapter_title}'AI内容生成失败: {e}")
                            # 创建基础结构
                            chapter_results[id(original_chapter)] = ({
                                'chapter_number': original_chapter.get('chapter_number', ''),
                                'level': original_chapter.get('level', 1),
                                'title': original_chapter.get('title', ''),
                                'description': original_chapter.get('description', ''),
                                'response_strategy': original_chapter.get('response_strategy', ''),
                                'content_hints': original_chapter.get('content_hints', []),
                                'response_tips': original_chapter.get('response_tips', []),
                                'suggested_references': original_chapter.get('suggested_references', []),
                                'evidence_needed': original_chapter.get('evidence_needed', []),
                                'subsections': []
                            }, None)
                            failed_count += 1

                self.logger.info(
                    f"章节AI内容生成完成: 成功 {completed_count}个, 失败 {failed_count}个, "
                    f"总计 {len(chapters)}个"
                )

                # 按原顺序组装章节（保持顺序很重要）
                for chapter in chapters:
                    assembled_chapter, ai_content = chapter_results.get(id(chapter), ({}, None))
                    if ai_content:
                        assembled_chapter['ai_generated_content'] = ai_content

                    # 处理子章节（子章节同样并发生成）
                    if 'subsections' in chapter and chapter['subsections']:
                        assembled_chapter['subsections'] = self._assemble_subsections(
                            chapter['subsections'],
                            analysis,
                            matched_docs
                        )

                    assembled_chapters.append(assembled_chapter)
        else:
            # 有匹配文档时，使用原串行逻辑（不生成AI内容）
            for chapter in chapters:
                assembled_chapter = {
                    'chapter_number': chapter.get('chapter_number', ''),
                    'level': chapter.get('level', 1),
                    'title': chapter.get('title', ''),
                    'description': chapter.get('description', ''),
                    'response_strategy': chapter.get('response_strategy', ''),
                    'content_hints': chapter.get('content_hints', []),
                    'response_tips': chapter.get('response_tips', []),
                    'suggested_references': chapter.get('suggested_references', []),
                    'evidence_needed': chapter.get('evidence_needed', []),
                    'subsections': []
                }

                # 处理子章节
                if 'subsections' in chapter and chapter['subsections']:
                    assembled_chapter['subsections'] = self._assemble_subsections(
                        chapter['subsections'],
                        analysis,
                        matched_docs
                    )

                assembled_chapters.append(assembled_chapter)

        return assembled_chapters

    def _assemble_subsections(
        self,
        subsections: List[Dict],
        analysis: Dict[str, Any],
        matched_docs: Dict[str, List[Dict]]
    ) -> List[Dict]:
        """
        组装子章节（并发版本）

        Args:
            subsections: 子章节列表
            analysis: 需求分析
            matched_docs: 匹配的文档

        Returns:
            组装后的子章节列表
        """
        assembled = []
        total_matched_docs = sum(len(docs) for docs in matched_docs.values())

        # 如果没有匹配到产品文档，使用AI并发生成子章节内容
        if total_matched_docs == 0 and subsections:
            self.logger.info(f"并发生成 {len(subsections)} 个子章节的AI内容...")

            with ThreadPoolExecutor(max_workers=5) as executor:
                # 提交所有子章节的生成任务
                future_to_subsection = {
                    executor.submit(self._generate_chapter_with_content, sub, analysis): sub
                    for sub in subsections
                }

                # 收集结果
                subsection_results = {}
                completed_count = 0

                for future in as_completed(future_to_subsection):
                    original_subsection = future_to_subsection[future]
                    try:
                        assembled_sub, ai_content = future.result(timeout=150)
                        subsection_results[id(original_subsection)] = (assembled_sub, ai_content)

                        if ai_content:
                            sub_title = original_subsection.get('title', '未知子章节')
                            self.logger.info(f"✓ 子章节'{sub_title}'AI内容生成成功")
                            completed_count += 1
                    except Exception as e:
                        sub_title = original_subsection.get('title', '未知子章节')
                        self.logger.warning(f"❌ 子章节'{sub_title}'AI内容生成失败: {e}")
                        # 创建基础结构
                        subsection_results[id(original_subsection)] = ({
                            'chapter_number': original_subsection.get('chapter_number', ''),
                            'level': original_subsection.get('level', 2),
                            'title': original_subsection.get('title', ''),
                            'description': original_subsection.get('description', ''),
                            'response_strategy': original_subsection.get('response_strategy', ''),
                            'content_hints': original_subsection.get('content_hints', []),
                            'response_tips': original_subsection.get('response_tips', []),
                            'suggested_references': original_subsection.get('suggested_references', []),
                            'evidence_needed': original_subsection.get('evidence_needed', [])
                        }, None)

            self.logger.info(f"子章节AI内容生成完成: 成功 {completed_count}个, 总计 {len(subsections)}个")

            # 按原顺序组装子章节
            for subsection in subsections:
                assembled_sub, ai_content = subsection_results.get(id(subsection), ({}, None))
                if ai_content:
                    assembled_sub['ai_generated_content'] = ai_content
                assembled.append(assembled_sub)
        else:
            # 有匹配文档时，使用原串行逻辑（不生成AI内容）
            for subsection in subsections:
                assembled_sub = {
                    'chapter_number': subsection.get('chapter_number', ''),
                    'level': subsection.get('level', 2),
                    'title': subsection.get('title', ''),
                    'description': subsection.get('description', ''),
                    'response_strategy': subsection.get('response_strategy', ''),
                    'content_hints': subsection.get('content_hints', []),
                    'response_tips': subsection.get('response_tips', []),
                    'suggested_references': subsection.get('suggested_references', []),
                    'evidence_needed': subsection.get('evidence_needed', [])
                }
                assembled.append(assembled_sub)

        return assembled

    def _create_mapping_table(
        self,
        analysis: Dict[str, Any],
        matched_docs: Dict[str, List[Dict]]
    ) -> List[Dict]:
        """
        创建需求匹配表

        Args:
            analysis: 需求分析
            matched_docs: 匹配的文档

        Returns:
            匹配表数据
        """
        mapping_table = []

        for category in analysis.get('requirement_categories', []):
            category_code = category.get('category_code', '')
            category_name = category.get('category', '')

            # 获取该类别匹配的文档
            docs = matched_docs.get(category_code, [])

            for point in category.get('key_points', []):
                row = {
                    'category': category_name,
                    'requirement': point,
                    'matched_docs': [doc['title'] for doc in docs[:2]],  # 最多2个
                    'match_status': '已匹配' if docs else '待匹配'
                }
                mapping_table.append(row)

        return mapping_table

    def _create_summary_report(
        self,
        proposal: Dict[str, Any],
        analysis: Dict[str, Any],
        matched_docs: Dict[str, List[Dict]]
    ) -> Dict[str, Any]:
        """
        创建生成报告

        Args:
            proposal: 方案数据
            analysis: 需求分析
            matched_docs: 匹配的文档

        Returns:
            报告数据
        """
        summary = analysis.get('document_summary', {})

        total_matched_docs = sum(len(docs) for docs in matched_docs.values())

        report = {
            'generation_info': {
                'title': proposal['metadata']['title'],
                'generation_time': proposal['metadata']['generation_time'],
                'total_chapters': proposal['metadata']['total_chapters']
            },
            'requirements_summary': {
                'total_requirements': summary.get('total_requirements', 0),
                'mandatory_count': summary.get('mandatory_count', 0),
                'optional_count': summary.get('optional_count', 0),
                'complexity_level': summary.get('complexity_level', 'medium')
            },
            'matching_summary': {
                'total_documents_matched': total_matched_docs,
                'categories_with_matches': len(matched_docs),
                'match_rate': self._calculate_match_rate(analysis, matched_docs)
            }
        }

        return report

    def _calculate_match_rate(
        self,
        analysis: Dict[str, Any],
        matched_docs: Dict[str, List[Dict]]
    ) -> float:
        """
        计算匹配成功率

        Args:
            analysis: 需求分析
            matched_docs: 匹配的文档

        Returns:
            匹配率（0-100）
        """
        total_categories = len(analysis.get('requirement_categories', []))

        if total_categories == 0:
            return 0.0

        matched_categories = len([
            cat for cat in analysis.get('requirement_categories', [])
            if matched_docs.get(cat.get('category_code', ''))
        ])

        return round((matched_categories / total_categories) * 100, 2)

    def _generate_chapter_content_with_ai(
        self,
        chapter: Dict[str, Any],
        analysis: Dict[str, Any]
    ) -> Optional[str]:
        """
        使用AI生成章节内容（带降级策略）

        Args:
            chapter: 章节信息
            analysis: 需求分析结果

        Returns:
            生成的章节内容，失败返回模板内容
        """
        chapter_title = chapter.get('title', '')
        chapter_desc = chapter.get('description', '')
        content_hints = chapter.get('content_hints', [])
        response_tips = chapter.get('response_tips', [])

        # 策略1: 精简提示词生成（重试2次）
        try:
            # ✅ 精简提示词：只保留核心要点
            core_hints = content_hints[:3] if content_hints else []
            hints_text = '、'.join(core_hints) if core_hints else chapter_desc

            prompt = f"""为"{chapter_title}"生成800字专业技术方案。

核心要点：{hints_text}

要求：专业、清晰、突出技术优势、中文、纯文本格式（不使用Markdown标记如##、**等）"""

            # 调用LLM
            self.logger.info(f"为章节'{chapter_title}'生成AI内容（精简模式）...")
            response = self.llm_client.call(
                prompt=prompt,
                temperature=0.7,
                max_tokens=1500,  # 从2000降到1500
                max_retries=2,
                purpose=f"章节内容生成: {chapter_title}"
            )

            if response and response.strip():
                self.logger.info(f"章节'{chapter_title}'AI内容生成成功，长度: {len(response)}")
                return response.strip()

        except Exception as e:
            self.logger.warning(f"策略1(完整生成)失败: {e}，尝试策略2(简化生成)")

        # 策略2: 简化提示词生成（重试1次）
        try:
            simplified_prompt = f"""为"{chapter_title}"生成800字技术方案内容。

要点: {', '.join(content_hints[:3])}

要求: 专业、清晰、中文"""

            response = self.llm_client.call(
                prompt=simplified_prompt,
                temperature=0.7,
                max_tokens=1500,
                max_retries=1,
                purpose=f"章节内容简化生成: {chapter_title}"
            )

            if response and response.strip():
                self.logger.info(f"章节'{chapter_title}'简化生成成功")
                return response.strip()

        except Exception as e:
            self.logger.warning(f"策略2(简化生成)失败: {e}，使用策略3(模板内容)")

        # 策略3: 返回模板内容（兜底）
        self.logger.error(f"章节'{chapter_title}'所有生成策略失败，使用模板内容")
        return self._generate_template_content(chapter)

    def generate_chapter_content_stream(
        self,
        chapter: Dict[str, Any],
        analysis: Dict[str, Any]
    ) -> Generator[str, None, None]:
        """
        使用AI流式生成章节内容（Generator版本，带降级策略和精简提示词）

        Args:
            chapter: 章节信息
            analysis: 需求分析结果

        Yields:
            str: 生成的文本片段
        """
        chapter_title = chapter.get('title', '')
        chapter_desc = chapter.get('description', '')
        content_hints = chapter.get('content_hints', [])

        # ✅ 统一使用精简提示词
        core_hints = content_hints[:3] if content_hints else []
        hints_text = '、'.join(core_hints) if core_hints else chapter_desc

        prompt = f"""为"{chapter_title}"生成800字专业技术方案。

核心要点：{hints_text}

要求：专业、清晰、突出技术优势、中文、纯文本格式（不使用Markdown标记如##、**等）"""

        # 策略1: 流式生成（超时120秒）
        try:
            self.logger.info(f"为章节'{chapter_title}'流式生成AI内容（精简+纯文本模式）...")

            for chunk in self.llm_client.call_stream(
                prompt=prompt,
                temperature=0.7,
                max_tokens=1500,  # 降到1500
                timeout=120,
                purpose=f"章节内容流式生成: {chapter_title}"
            ):
                yield chunk

            self.logger.info(f"章节'{chapter_title}'流式生成完成")
            return

        except Exception as e:
            self.logger.warning(f"策略1(流式生成)失败: {e}，尝试策略2(非流式生成)")

        # 策略2: 非流式生成
        try:
            self.logger.info(f"章节'{chapter_title}'使用非流式生成...")

            response = self.llm_client.call(
                prompt=prompt,  # 使用相同的精简提示词
                temperature=0.7,
                max_tokens=1500,
                max_retries=1,
                purpose=f"章节内容非流式生成: {chapter_title}"
            )

            if response and response.strip():
                self.logger.info(f"章节'{chapter_title}'非流式生成成功")
                yield response.strip()
                return

        except Exception as e:
            self.logger.warning(f"策略2(非流式生成)失败: {e}，使用策略3(模板内容)")

        # 策略3: 模板内容（兜底）
        self.logger.error(f"章节'{chapter_title}'所有生成策略失败，使用模板内容")
        template_content = self._generate_template_content(chapter)
        yield template_content

    def _generate_chapter_stream_safe(
        self,
        chapter: Dict[str, Any],
        analysis: Dict[str, Any]
    ) -> Tuple[str, str, str]:
        """
        安全地生成单个章节（用于并发调用）
        将Generator转为完整字符串，带超时保护

        Args:
            chapter: 章节信息
            analysis: 需求分析结果

        Returns:
            (chapter_number, chapter_title, content)
        """
        try:
            chapter_num = chapter.get('chapter_number', '')
            chapter_title = chapter.get('title', '')

            # 收集流式生成的内容
            content_parts = []
            for chunk in self.generate_chapter_content_stream(chapter, analysis):
                content_parts.append(chunk)

            content = ''.join(content_parts)
            return (chapter_num, chapter_title, content)

        except Exception as e:
            self.logger.error(f"章节'{chapter.get('title')}'生成失败: {e}")
            # 返回模板内容
            template = self._generate_template_content(chapter)
            return (chapter.get('chapter_number', ''), chapter.get('title', ''), template)

    def _generate_template_content(self, chapter: Dict[str, Any]) -> str:
        """
        生成模板内容（降级策略的兜底方案）

        Args:
            chapter: 章节信息

        Returns:
            模板内容
        """
        chapter_title = chapter.get('title', '')
        chapter_desc = chapter.get('description', '')
        content_hints = chapter.get('content_hints', [])

        template = f"""【本章节内容生成超时，请根据以下要点手动补充】

本章节说明：{chapter_desc}

需要包含的要点：
"""
        for i, hint in enumerate(content_hints, 1):
            template += f"\n{i}. {hint}"

        template += "\n\n【请在此处补充详细内容】"

        return template
