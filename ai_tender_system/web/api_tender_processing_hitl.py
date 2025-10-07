#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
标书智能处理 HITL API路由
支持三步人工确认流程
"""

import json
import re
import uuid
from datetime import datetime
from flask import request, jsonify, send_file, render_template
from pathlib import Path

from common import get_module_logger
from common.database import get_knowledge_base_db

# 导入结构解析器
import sys
sys.path.append(str(Path(__file__).parent.parent))
from modules.tender_processing.structure_parser import DocumentStructureParser

logger = get_module_logger("api_hitl")


def register_hitl_routes(app):
    """注册 HITL API 路由"""

    # 获取数据库连接
    db = get_knowledge_base_db()

    # ============================================
    # 页面路由
    # ============================================

    @app.route('/tender-processing-hitl')
    def tender_processing_hitl_page():
        """渲染HITL流程页面"""
        return render_template('tender_processing_hitl.html')

    # ============================================
    # 步骤1：章节选择相关API
    # ============================================

    @app.route('/api/tender-processing/parse-structure', methods=['POST'])
    def parse_document_structure():
        """
        解析文档结构（步骤1的第一步）

        请求参数（FormData）：
        - file: Word文档文件
        - project_id: 项目ID

        返回：
        {
            "success": True/False,
            "task_id": "hitl_xxx",
            "chapters": [...],  # 章节树
            "statistics": {...}
        }
        """
        try:
            # 获取参数
            project_id = request.form.get('project_id')
            if not project_id:
                return jsonify({'success': False, 'error': '缺少project_id参数'}), 400

            # 检查文件
            if 'file' not in request.files:
                return jsonify({'success': False, 'error': '未上传文件'}), 400

            file = request.files['file']
            if not file.filename:
                return jsonify({'success': False, 'error': '文件名为空'}), 400

            # 保存文件到临时目录
            from core.storage_service import storage_service
            file_metadata = storage_service.store_file(
                file_obj=file,
                original_name=file.filename,
                category='tender_processing',
                business_type='tender_hitl_document'
            )

            file_path = file_metadata.file_path
            logger.info(f"文件已保存: {file_path}")

            # 解析文档结构
            parser = DocumentStructureParser()
            result = parser.parse_document_structure(file_path)

            if not result["success"]:
                return jsonify(result), 500

            # 创建 HITL 任务
            hitl_task_id = f"hitl_{uuid.uuid4().hex[:12]}"
            task_id = f"task_{uuid.uuid4().hex[:12]}"

            # 保存章节到数据库
            chapter_ids = _save_chapters_to_db(
                db, result["chapters"], project_id, task_id, hitl_task_id
            )

            # 创建 HITL 任务记录
            db.execute_query("""
                INSERT INTO tender_hitl_tasks (
                    hitl_task_id, project_id, task_id,
                    step1_status, step1_data,
                    estimated_words, estimated_cost
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                hitl_task_id, project_id, task_id,
                'in_progress',
                json.dumps({'file_path': file_path, 'file_name': file.filename}),
                result["statistics"].get("total_words", 0),
                result["statistics"].get("estimated_processing_cost", 0.0)
            ))

            logger.info(f"HITL任务已创建: {hitl_task_id}")

            return jsonify({
                'success': True,
                'task_id': hitl_task_id,
                'chapters': result["chapters"],
                'statistics': result["statistics"]
            })

        except Exception as e:
            logger.error(f"解析文档结构失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/tender-processing/select-chapters', methods=['POST'])
    def submit_chapter_selection():
        """
        提交章节选择结果（步骤1的第二步）

        请求参数（JSON）：
        {
            "task_id": "hitl_xxx",
            "selected_chapter_ids": ["ch_0", "ch_1", ...]
        }

        返回：
        {
            "success": True/False,
            "selected_count": 5,
            "selected_words": 8000,
            "estimated_cost": 0.016
        }
        """
        try:
            data = request.get_json()
            hitl_task_id = data.get('task_id')
            selected_ids = data.get('selected_chapter_ids', [])

            if not hitl_task_id:
                return jsonify({'success': False, 'error': '缺少task_id参数'}), 400

            db = get_knowledge_base_db()

            # 更新章节选择状态
            for chapter_id in selected_ids:
                db.execute_query("""
                    UPDATE tender_document_chapters
                    SET is_selected = 1, updated_at = CURRENT_TIMESTAMP
                    WHERE chapter_node_id = ? AND task_id IN (
                        SELECT task_id FROM tender_hitl_tasks WHERE hitl_task_id = ?
                    )
                """, (chapter_id, hitl_task_id))

            # 记录用户操作
            db.execute_query("""
                INSERT INTO tender_user_actions (
                    project_id, task_id, action_type, action_step, action_data
                ) SELECT project_id, hitl_task_id, 'chapter_selected', 1, ?
                FROM tender_hitl_tasks WHERE hitl_task_id = ?
            """, (json.dumps({'selected_ids': selected_ids}), hitl_task_id))

            # 统计选中章节
            stats = db.execute_query("""
                SELECT
                    COUNT(*) as selected_count,
                    SUM(word_count) as selected_words
                FROM tender_document_chapters c
                JOIN tender_hitl_tasks h ON c.task_id = h.task_id
                WHERE h.hitl_task_id = ? AND c.is_selected = 1
            """, (hitl_task_id,), fetch_one=True)

            selected_words = stats['selected_words'] or 0
            estimated_cost = (selected_words / 1000) * 0.002  # 假设成本

            # 读取原有的step1_data,保留file_path
            existing_data = db.execute_query("""
                SELECT step1_data FROM tender_hitl_tasks
                WHERE hitl_task_id = ?
            """, (hitl_task_id,), fetch_one=True)

            # 合并step1_data,保留file_path
            step1_data = {}
            if existing_data and existing_data.get('step1_data'):
                step1_data = json.loads(existing_data['step1_data'])

            # 更新选择信息
            step1_data.update({
                'selected_ids': selected_ids,
                'selected_count': stats['selected_count']
            })

            # 更新 HITL 任务状态
            db.execute_query("""
                UPDATE tender_hitl_tasks
                SET step1_status = 'completed',
                    step1_completed_at = CURRENT_TIMESTAMP,
                    step1_data = ?,
                    estimated_words = ?,
                    estimated_cost = ?
                WHERE hitl_task_id = ?
            """, (
                json.dumps(step1_data),
                selected_words,
                estimated_cost,
                hitl_task_id
            ))

            logger.info(f"步骤1完成: 选中 {stats['selected_count']} 个章节, {selected_words} 字")

            # ========== 新增：提取选中章节内容并分块 ==========
            # 获取文档路径
            task_data = db.execute_query("""
                SELECT step1_data FROM tender_hitl_tasks
                WHERE hitl_task_id = ?
            """, (hitl_task_id,), fetch_one=True)

            if task_data and task_data.get('step1_data'):
                step1_data = json.loads(task_data['step1_data'])
                doc_path = step1_data.get('file_path')

                if doc_path:
                    # 提取选中章节的内容
                    parser = DocumentStructureParser()
                    content_result = parser.get_selected_chapter_content(doc_path, selected_ids)

                    if content_result.get('success'):
                        # 对每个选中章节的内容进行分块
                        from ai_tender_system.modules.tender_processing.chunker import DocumentChunker
                        chunker = DocumentChunker(max_chunk_size=800, overlap_size=100)

                        chunk_index = 0
                        for chapter_data in content_result.get('chapters', []):
                            chapter_content = chapter_data.get('content', '')
                            chapter_title = chapter_data.get('title', '')

                            # 分块处理
                            chunks = chunker.chunk_document(
                                chapter_content,
                                metadata={'chapter_title': chapter_title}
                            )

                            # 保存分块到数据库
                            project_id = db.execute_query("""
                                SELECT project_id FROM tender_hitl_tasks
                                WHERE hitl_task_id = ?
                            """, (hitl_task_id,), fetch_one=True)['project_id']

                            for chunk in chunks:
                                db.execute_query("""
                                    INSERT INTO tender_document_chunks (
                                        project_id, hitl_task_id, chunk_index, chunk_type,
                                        content, metadata
                                    ) VALUES (?, ?, ?, ?, ?, ?)
                                """, (
                                    project_id,
                                    hitl_task_id,
                                    chunk_index,
                                    chunk.chunk_type,
                                    chunk.content,
                                    json.dumps(chunk.metadata)
                                ))
                                chunk_index += 1

                        logger.info(f"成功分块: 共 {chunk_index} 个文本块")

                        # ========== AI筛选处理 ==========
                        # 对每个文本块进行AI价值判断
                        from ai_tender_system.modules.tender_processing.filter import TenderFilter
                        content_filter = TenderFilter()

                        # 查询所有分块
                        chunks_to_filter = db.execute_query("""
                            SELECT chunk_id, content, chunk_type
                            FROM tender_document_chunks
                            WHERE hitl_task_id = ?
                            ORDER BY chunk_index
                        """, (hitl_task_id,))

                        filtered_count = 0
                        for chunk in chunks_to_filter:
                            # 使用AI判断块的价值
                            filter_result = content_filter.filter_chunk(chunk)

                            is_valuable = filter_result.is_valuable
                            confidence = filter_result.confidence

                            # 更新块的筛选状态
                            db.execute_query("""
                                UPDATE tender_document_chunks
                                SET is_valuable = ?,
                                    filter_confidence = ?,
                                    filtered_at = CURRENT_TIMESTAMP
                                WHERE chunk_id = ?
                            """, (
                                1 if is_valuable else 0,
                                confidence,
                                chunk['chunk_id']
                            ))

                            if not is_valuable:
                                filtered_count += 1

                        logger.info(f"AI筛选完成: 过滤掉 {filtered_count}/{chunk_index} 个低价值块")
                        # ========== AI筛选处理结束 ==========

                        # 更新任务状态到步骤2
                        db.execute_query("""
                            UPDATE tender_hitl_tasks
                            SET current_step = 2,
                                step2_status = 'in_progress'
                            WHERE hitl_task_id = ?
                        """, (hitl_task_id,))

                        logger.info(f"任务状态已更新到步骤2")
            # ========== 分块处理结束 ==========

            return jsonify({
                'success': True,
                'selected_count': stats['selected_count'],
                'selected_words': selected_words,
                'estimated_cost': estimated_cost
            })

        except Exception as e:
            logger.error(f"提交章节选择失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/tender-processing/export-chapter/<task_id>/<chapter_id>', methods=['GET'])
    def export_chapter_as_template(task_id, chapter_id):
        """
        导出单个章节为Word文档模板（步骤1功能扩展）

        Args:
            task_id: HITL任务ID (如 "hitl_abc123")
            chapter_id: 章节ID (如 "ch_4")

        Returns:
            Word文档文件流 (application/vnd.openxmlformats-officedocument.wordprocessingml.document)

        使用示例:
            GET /api/tender-processing/export-chapter/hitl_abc123/ch_4
            => 下载: 第五部分_响应文件格式_模板_20251006.docx
        """
        try:
            from datetime import datetime
            from flask import send_file
            import re

            db = get_knowledge_base_db()

            # 1. 查询HITL任务，获取原始文档路径
            task_data = db.execute_query("""
                SELECT step1_data FROM tender_hitl_tasks
                WHERE hitl_task_id = ?
            """, (task_id,), fetch_one=True)

            if not task_data:
                return jsonify({'success': False, 'error': '任务不存在'}), 404

            step1_data = json.loads(task_data['step1_data'])
            doc_path = step1_data.get('file_path')

            if not doc_path or not Path(doc_path).exists():
                return jsonify({'success': False, 'error': '原始文档不存在'}), 404

            # 2. 调用结构解析器导出章节
            from modules.tender_processing.structure_parser import DocumentStructureParser
            parser = DocumentStructureParser()
            result = parser.export_chapter_to_docx(doc_path, chapter_id)

            if not result['success']:
                return jsonify(result), 500

            # 3. 返回文件流
            output_path = result['file_path']
            chapter_title = result['chapter_title']

            # 生成下载文件名（移除特殊字符）
            safe_title = re.sub(r'[^\w\s-]', '', chapter_title).strip()
            safe_title = re.sub(r'[\s]+', '_', safe_title)  # 空格转下划线
            download_name = f"{safe_title}_应答模板_{datetime.now().strftime('%Y%m%d')}.docx"

            logger.info(f"导出章节模板: {chapter_title} -> {download_name}")

            return send_file(
                output_path,
                mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                as_attachment=True,
                download_name=download_name
            )

        except Exception as e:
            logger.error(f"导出章节失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/tender-processing/export-chapters/<task_id>', methods=['POST'])
    def export_multiple_chapters(task_id):
        """批量导出多个章节为单个Word文档"""
        try:
            data = request.get_json()
            chapter_ids = data.get('chapter_ids', [])

            if not chapter_ids:
                return jsonify({"error": "未提供章节ID"}), 400

            # 查询任务信息获取文档路径
            task_data = db.execute_query("""
                SELECT step1_data FROM tender_hitl_tasks
                WHERE hitl_task_id = ?
            """, (task_id,), fetch_one=True)

            if not task_data:
                return jsonify({"error": "任务不存在"}), 404

            step1_data = json.loads(task_data['step1_data'])
            doc_path = step1_data.get('file_path')

            # 调用parser批量导出
            parser = DocumentStructureParser()
            result = parser.export_multiple_chapters_to_docx(doc_path, chapter_ids)

            if not result['success']:
                return jsonify({"error": result.get('error', '导出失败')}), 500

            output_path = result['file_path']
            chapter_titles = result.get('chapter_titles', [])

            # 生成文件名
            safe_titles = '_'.join(chapter_titles[:3])  # 最多3个标题
            if len(chapter_titles) > 3:
                safe_titles += f'_等{len(chapter_titles)}章节'
            safe_titles = re.sub(r'[^\w\s-]', '', safe_titles).strip()
            download_name = f"{safe_titles}_应答模板_{datetime.now().strftime('%Y%m%d')}.docx"

            logger.info(f"批量导出章节模板: {len(chapter_ids)}个章节 -> {download_name}")

            return send_file(
                output_path,
                mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                as_attachment=True,
                download_name=download_name
            )

        except Exception as e:
            logger.error(f"批量导出章节失败: {str(e)}")
            return jsonify({"error": str(e)}), 500

    # ============================================
    # 步骤2：章节要求预览相关API
    # ============================================

    @app.route('/api/tender-processing/chapter-requirements/<task_id>', methods=['GET'])
    def get_chapter_requirements_summary(task_id):
        """
        获取各章节的要求聚合信息（步骤2）

        按章节分组统计AI提取的要求数量

        返回：
        {
            "success": True,
            "chapters": [
                {
                    "chapter_id": 123,
                    "title": "第一章 项目概述",
                    "word_count": 1500,
                    "is_selected": True,
                    "requirement_stats": {
                        "total": 15,
                        "mandatory": 10,
                        "scoring": 3,
                        "optional": 2
                    }
                },
                ...
            ],
            "summary": {
                "total_chapters": 10,
                "selected_chapters": 8,
                "total_requirements": 50
            }
        }
        """
        try:
            db = get_knowledge_base_db()

            # 获取任务关联的project_id
            hitl_task = db.execute_query("""
                SELECT project_id, task_id FROM tender_hitl_tasks
                WHERE hitl_task_id = ?
            """, (task_id,), fetch_one=True)

            if not hitl_task:
                return jsonify({'success': False, 'error': '任务不存在'}), 404

            # 获取所有章节（步骤1选中的章节）
            chapters = db.execute_query("""
                SELECT
                    chapter_id,
                    title,
                    word_count,
                    is_selected,
                    level
                FROM tender_document_chapters
                WHERE task_id = ?
                ORDER BY chapter_node_id
            """, (task_id,))

            # 为每个章节统计要求数量
            chapter_list = []
            total_requirements = 0

            for chapter in chapters:
                # 统计该章节的要求数量（通过source_location匹配章节标题）
                req_stats = db.execute_query("""
                    SELECT
                        constraint_type,
                        COUNT(*) as count
                    FROM tender_requirements
                    WHERE hitl_task_id = ?
                      AND source_location LIKE ?
                    GROUP BY constraint_type
                """, (task_id, f"%{chapter['title']}%"))

                # 构建统计数据
                stats = {'total': 0, 'mandatory': 0, 'scoring': 0, 'optional': 0}
                for stat in req_stats:
                    count = stat['count']
                    stats['total'] += count
                    stats[stat['constraint_type']] = count

                total_requirements += stats['total']

                chapter_list.append({
                    'chapter_id': chapter['chapter_id'],
                    'title': chapter['title'],
                    'word_count': chapter['word_count'] or 0,
                    'is_selected': bool(chapter['is_selected']),
                    'level': chapter['level'],
                    'requirement_stats': stats
                })

            # 汇总统计
            selected_count = sum(1 for c in chapter_list if c['is_selected'])

            return jsonify({
                'success': True,
                'chapters': chapter_list,
                'summary': {
                    'total_chapters': len(chapter_list),
                    'selected_chapters': selected_count,
                    'total_requirements': total_requirements
                }
            })

        except Exception as e:
            logger.error(f"获取章节要求汇总失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/tender-processing/filtered-blocks/<task_id>', methods=['GET'])
    def get_filtered_blocks(task_id):
        """
        获取被AI筛选掉的文本块（步骤2）

        返回：
        {
            "success": True,
            "filtered_blocks": [
                {
                    "chunk_id": 123,
                    "content": "...",
                    "ai_decision": "NON-REQUIREMENT",
                    "ai_confidence": 0.85,
                    "ai_reasoning": "这是描述性文本"
                },
                ...
            ],
            "statistics": {
                "total_filtered": 50,
                "high_confidence": 40,
                "low_confidence": 10
            }
        }
        """
        try:
            db = get_knowledge_base_db()

            # 获取任务关联的project_id
            hitl_task = db.execute_query("""
                SELECT project_id, task_id FROM tender_hitl_tasks
                WHERE hitl_task_id = ?
            """, (task_id,), fetch_one=True)

            if not hitl_task:
                return jsonify({'success': False, 'error': '任务不存在'}), 404

            # 获取被过滤的块（只查询当前HITL任务的数据）
            filtered_blocks = db.execute_query("""
                SELECT
                    c.chunk_id,
                    c.content,
                    c.chunk_type,
                    c.is_valuable,
                    c.filter_confidence,
                    r.ai_decision,
                    r.ai_confidence,
                    r.ai_reasoning,
                    r.user_decision,
                    r.reviewed_at
                FROM tender_document_chunks c
                LEFT JOIN tender_filter_review r ON c.chunk_id = r.chunk_id
                WHERE c.hitl_task_id = ? AND c.is_valuable = 0
                ORDER BY c.chunk_index
            """, (task_id,))

            # 统计（处理None值）
            high_conf = sum(1 for b in filtered_blocks if (b.get('ai_confidence') or 0) >= 0.7)
            low_conf = len(filtered_blocks) - high_conf

            return jsonify({
                'success': True,
                'filtered_blocks': filtered_blocks,
                'statistics': {
                    'total_filtered': len(filtered_blocks),
                    'high_confidence': high_conf,
                    'low_confidence': low_conf
                }
            })

        except Exception as e:
            logger.error(f"获取筛选块失败: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/tender-processing/update-chapter-selection', methods=['POST'])
    def update_chapter_selection_step2(task_id):
        """
        更新章节筛选状态（步骤2）

        允许用户在步骤2取消某些章节，该章节的要求不会出现在步骤3

        请求参数（JSON）：
        {
            "task_id": "hitl_xxx",
            "chapter_ids": [123, 456, ...],  // 选中的章节ID
            "deselected_chapter_ids": [789, ...]  // 取消选中的章节ID
        }

        返回：
        {
            "success": True,
            "selected_count": 8,
            "deselected_count": 2
        }
        """
        try:
            data = request.get_json()
            hitl_task_id = data.get('task_id')
            selected_ids = data.get('chapter_ids', [])
            deselected_ids = data.get('deselected_chapter_ids', [])

            if not hitl_task_id:
                return jsonify({'success': False, 'error': '缺少task_id'}), 400

            db = get_knowledge_base_db()

            # 更新选中状态
            if selected_ids:
                placeholders = ','.join(['?' for _ in selected_ids])
                db.execute_query(f"""
                    UPDATE tender_document_chapters
                    SET is_selected = 1, updated_at = CURRENT_TIMESTAMP
                    WHERE chapter_id IN ({placeholders})
                """, selected_ids)

            # 更新取消选中状态
            if deselected_ids:
                placeholders = ','.join(['?' for _ in deselected_ids])
                db.execute_query(f"""
                    UPDATE tender_document_chapters
                    SET is_selected = 0, updated_at = CURRENT_TIMESTAMP
                    WHERE chapter_id IN ({placeholders})
                """, deselected_ids)

            # 记录用户操作
            db.execute_query("""
                INSERT INTO tender_user_actions (
                    project_id, task_id, action_type, action_step, action_data
                ) SELECT project_id, hitl_task_id, 'chapter_reselection', 2, ?
                FROM tender_hitl_tasks WHERE hitl_task_id = ?
            """, (json.dumps({
                'selected_count': len(selected_ids),
                'deselected_count': len(deselected_ids)
            }), hitl_task_id))

            logger.info(f"步骤2更新章节选择: 选中{len(selected_ids)}个, 取消{len(deselected_ids)}个")

            return jsonify({
                'success': True,
                'selected_count': len(selected_ids),
                'deselected_count': len(deselected_ids)
            })

        except Exception as e:
            logger.error(f"更新章节选择失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/tender-processing/restore-blocks', methods=['POST'])
    def restore_filtered_blocks():
        """
        恢复被误判的文本块（步骤2）

        请求参数（JSON）：
        {
            "task_id": "hitl_xxx",
            "chunk_ids": [123, 456, ...]
        }

        返回：
        {
            "success": True,
            "restored_count": 3
        }
        """
        try:
            data = request.get_json()
            hitl_task_id = data.get('task_id')
            chunk_ids = data.get('chunk_ids', [])

            if not hitl_task_id or not chunk_ids:
                return jsonify({'success': False, 'error': '参数不完整'}), 400

            db = get_knowledge_base_db()

            # 恢复块（标记为高价值）
            for chunk_id in chunk_ids:
                db.execute_query("""
                    UPDATE tender_document_chunks
                    SET is_valuable = 1, updated_at = CURRENT_TIMESTAMP
                    WHERE chunk_id = ?
                """, (chunk_id,))

                # 记录复核操作
                db.execute_query("""
                    INSERT OR REPLACE INTO tender_filter_review (
                        chunk_id, project_id, task_id,
                        ai_decision, user_decision, reviewed_by, reviewed_at
                    ) SELECT
                        ?, project_id, hitl_task_id, 'NON-REQUIREMENT', 'restore', 'user', CURRENT_TIMESTAMP
                    FROM tender_hitl_tasks WHERE hitl_task_id = ?
                """, (chunk_id, hitl_task_id))

            # 记录用户操作
            db.execute_query("""
                INSERT INTO tender_user_actions (
                    project_id, task_id, action_type, action_step, action_data
                ) SELECT project_id, hitl_task_id, 'chunk_restored', 2, ?
                FROM tender_hitl_tasks WHERE hitl_task_id = ?
            """, (json.dumps({'chunk_ids': chunk_ids}), hitl_task_id))

            logger.info(f"恢复了 {len(chunk_ids)} 个被过滤的块")

            return jsonify({
                'success': True,
                'restored_count': len(chunk_ids)
            })

        except Exception as e:
            logger.error(f"恢复块失败: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    # ============================================
    # 步骤3：可编辑表格相关API
    # ============================================

    @app.route('/api/tender-processing/requirements/<task_id>', methods=['GET'])
    def get_task_requirements(task_id):
        """
        获取HITL任务的所有要求及统计信息（步骤3）

        注意：现在按 task_id（hitl_task_id）过滤，而不是 project_id
        这确保只显示当前任务中选中章节提取的需求

        返回：
        {
            "success": True,
            "requirements": [{...}, ...],
            "summary": [
                {"constraint_type": "mandatory", "count": 10},
                {"constraint_type": "optional", "count": 5},
                {"constraint_type": "scoring", "count": 3}
            ]
        }
        """
        try:
            db = get_knowledge_base_db()

            # 获取当前HITL任务的所有要求（按hitl_task_id过滤）
            requirements = db.execute_query("""
                SELECT * FROM tender_requirements
                WHERE hitl_task_id = ?
                ORDER BY requirement_id
            """, (task_id,))

            # 统计各类型数量
            summary = db.execute_query("""
                SELECT
                    constraint_type,
                    COUNT(*) as count
                FROM tender_requirements
                WHERE hitl_task_id = ?
                GROUP BY constraint_type
            """, (task_id,))

            logger.info(f"加载HITL任务 {task_id} 的 {len(requirements)} 个要求")

            return jsonify({
                'success': True,
                'requirements': requirements,
                'summary': summary
            })

        except Exception as e:
            logger.error(f"获取任务要求失败: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/tender-processing/requirements/<int:req_id>', methods=['PATCH'])
    def update_requirement(req_id):
        """
        编辑单个要求（步骤3）

        请求参数（JSON）：
        {
            "constraint_type": "mandatory",
            "category": "technical",
            "detail": "更新后的内容",
            ...
        }

        返回：
        {
            "success": True,
            "requirement_id": 123
        }
        """
        try:
            data = request.get_json()
            task_id = data.get('task_id')  # 可选

            if not data:
                return jsonify({'success': False, 'error': '缺少更新数据'}), 400

            db = get_knowledge_base_db()

            # 构建更新SQL
            update_fields = []
            params = []

            allowed_fields = [
                'constraint_type', 'category', 'subcategory',
                'detail', 'source_location', 'priority'
            ]

            for field in allowed_fields:
                if field in data:
                    update_fields.append(f"{field} = ?")
                    params.append(data[field])

            if not update_fields:
                return jsonify({'success': False, 'error': '没有可更新的字段'}), 400

            params.append(req_id)

            # 执行更新
            db.execute_query(f"""
                UPDATE tender_requirements
                SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
                WHERE requirement_id = ?
            """, tuple(params))

            # 如果提供了task_id，记录到草稿表
            if task_id:
                db.execute_query("""
                    INSERT INTO tender_requirements_draft (
                        requirement_id, project_id, task_id,
                        constraint_type, category, subcategory, detail, source_location, priority,
                        operation, edited_by, edited_at
                    ) SELECT
                        ?, project_id, ?, constraint_type, category, subcategory,
                        detail, source_location, priority, 'edit', 'user', CURRENT_TIMESTAMP
                    FROM tender_requirements
                    WHERE requirement_id = ?
                """, (req_id, task_id, req_id))

            logger.info(f"要求 {req_id} 已更新")

            return jsonify({
                'success': True,
                'requirement_id': req_id
            })

        except Exception as e:
            logger.error(f"更新要求失败: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/tender-processing/requirements/batch', methods=['POST'])
    def batch_requirement_operations():
        """
        批量操作要求（步骤3）

        请求参数（JSON）：
        {
            "task_id": "hitl_xxx",
            "operations": [
                {"action": "add", "data": {...}},
                {"action": "delete", "requirement_id": 123},
                ...
            ]
        }

        返回：
        {
            "success": True,
            "results": [...]
        }
        """
        try:
            data = request.get_json()
            task_id = data.get('task_id')
            operations = data.get('operations', [])

            if not task_id or not operations:
                return jsonify({'success': False, 'error': '参数不完整'}), 400

            db = get_knowledge_base_db()
            results = []

            for op in operations:
                action = op.get('action')

                if action == 'add':
                    # 添加新要求（包含hitl_task_id）
                    req_data = op.get('data', {})
                    db.execute_query("""
                        INSERT INTO tender_requirements (
                            project_id, constraint_type, category, subcategory,
                            detail, source_location, priority, hitl_task_id
                        ) SELECT
                            project_id, ?, ?, ?, ?, ?, ?, ?
                        FROM tender_hitl_tasks WHERE hitl_task_id = ?
                    """, (
                        req_data.get('constraint_type'),
                        req_data.get('category'),
                        req_data.get('subcategory'),
                        req_data.get('detail'),
                        req_data.get('source_location'),
                        req_data.get('priority', 'medium'),
                        task_id,  # 设置hitl_task_id
                        task_id   # WHERE条件
                    ))
                    results.append({'action': 'add', 'success': True})

                elif action == 'delete':
                    # 删除要求
                    req_id = op.get('requirement_id')
                    db.execute_query("""
                        DELETE FROM tender_requirements
                        WHERE requirement_id = ?
                    """, (req_id,))
                    results.append({'action': 'delete', 'requirement_id': req_id, 'success': True})

            return jsonify({
                'success': True,
                'results': results
            })

        except Exception as e:
            logger.error(f"批量操作失败: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/tender-processing/export-draft/<task_id>', methods=['GET'])
    def export_draft_requirements(task_id):
        """
        导出草稿要求（步骤3）

        返回：Excel 文件
        """
        try:
            import pandas as pd
            from io import BytesIO

            db = get_knowledge_base_db()

            # 获取草稿要求
            drafts = db.execute_query("""
                SELECT * FROM tender_requirements_draft
                WHERE task_id = ?
                ORDER BY created_at DESC
            """, (task_id,))

            if not drafts:
                return jsonify({'success': False, 'error': '没有草稿数据'}), 404

            # 转换为 DataFrame
            df = pd.DataFrame(drafts)

            # 生成 Excel
            output = BytesIO()
            df.to_excel(output, index=False, sheet_name='草稿要求')
            output.seek(0)

            return send_file(
                output,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name=f'requirements_draft_{task_id}.xlsx'
            )

        except Exception as e:
            logger.error(f"导出草稿失败: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500


# ============================================
# 辅助函数
# ============================================

def _save_chapters_to_db(db, chapters, project_id, task_id, hitl_task_id, parent_id=None):
    """递归保存章节树到数据库"""
    chapter_ids = []

    for chapter in chapters:
        # 插入章节
        chapter_db_id = db.execute_query("""
            INSERT INTO tender_document_chapters (
                project_id, task_id, chapter_node_id, level, title,
                para_start_idx, para_end_idx, word_count, preview_text,
                is_selected, auto_selected, skip_recommended, parent_chapter_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            project_id, task_id, chapter['id'], chapter['level'], chapter['title'],
            chapter['para_start_idx'], chapter.get('para_end_idx'),
            chapter.get('word_count', 0), chapter.get('preview_text', ''),
            False, chapter.get('auto_selected', False),
            chapter.get('skip_recommended', False), parent_id
        ))

        # execute_query 已经返回 lastrowid
        chapter_ids.append(chapter_db_id)

        # 递归保存子章节
        if chapter.get('children'):
            child_ids = _save_chapters_to_db(
                db, chapter['children'], project_id, task_id, hitl_task_id, chapter_db_id
            )
            chapter_ids.extend(child_ids)

    return chapter_ids
