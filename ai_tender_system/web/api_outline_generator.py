#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
技术方案大纲生成API
提供技术方案生成的Web接口
"""

import os
import json
import traceback
from datetime import datetime
from pathlib import Path
from flask import Blueprint, request, jsonify, send_file, Response, stream_with_context
from werkzeug.utils import secure_filename

# 导入核心模块
import sys
sys.path.append(str(Path(__file__).parent.parent))
from common import get_module_logger, get_config
from modules.outline_generator import (
    RequirementAnalyzer,
    OutlineGenerator,
    ProductMatcher,
    ProposalAssembler,
    WordExporter
)

# 创建蓝图
api_outline_bp = Blueprint('api_outline', __name__, url_prefix='/api')

# 全局变量
logger = get_module_logger("api_outline_generator")
config = get_config()

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {'doc', 'docx', 'pdf', 'xlsx', 'xls'}


def allowed_file(filename: str) -> bool:
    """检查文件扩展名是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@api_outline_bp.route('/generate-proposal', methods=['POST'])
def generate_proposal():
    """
    生成技术方案API

    请求参数（multipart/form-data）:
    - tender_file: 技术需求文档文件
    - product_file: 产品文档文件（可选）
    - company_id: 公司ID（可选）
    - output_prefix: 输出文件名前缀（可选，默认"技术方案"）
    - include_analysis: 是否包含需求分析报告（可选，默认false）
    - include_mapping: 是否生成需求匹配表（可选，默认false）
    - include_summary: 是否生成生成报告（可选，默认false）

    返回:
    {
        "success": true,
        "requirements_count": 50,
        "sections_count": 5,
        "matches_count": 45,
        "output_files": {
            "proposal": "/downloads/xxx.docx",
            "analysis": "/downloads/xxx.docx",
            "mapping": "/downloads/xxx.xlsx",
            "summary": "/downloads/xxx.txt"
        }
    }
    """
    try:
        logger.info("收到技术方案生成请求")

        # 1. 验证请求 - 支持两种文件来源：直接上传或从HITL传递
        use_hitl_file = request.form.get('use_hitl_technical_file', 'false').lower() == 'true'
        project_id = request.form.get('hitl_task_id') or request.form.get('project_id')

        if use_hitl_file and project_id:
            # 使用HITL传递的技术需求文件
            logger.info(f"使用HITL项目的技术需求文件: project_id={project_id}")

            # 在technical_files目录下搜索项目目录（不依赖日期）
            technical_files_base = config.get_path('data') / 'uploads' / 'technical_files'

            # 递归查找项目目录
            tender_path = None
            for year_dir in technical_files_base.glob('*'):
                if not year_dir.is_dir():
                    continue
                for month_dir in year_dir.glob('*'):
                    if not month_dir.is_dir():
                        continue
                    project_dir = month_dir / str(project_id)
                    if project_dir.exists():
                        # 查找技术需求文件（第一个文件）
                        technical_files = list(project_dir.glob('*.*'))
                        if technical_files:
                            tender_path = technical_files[0]
                            logger.info(f"找到HITL技术需求文件: {tender_path.name}, 路径: {tender_path}")
                            break
                if tender_path:
                    break

            if not tender_path:
                return jsonify({
                    'success': False,
                    'error': f'未找到项目的技术需求文件: project_id={project_id}'
                }), 400
        else:
            # 使用上传的文件
            if 'tender_file' not in request.files:
                return jsonify({
                    'success': False,
                    'error': '缺少技术需求文档文件'
                }), 400

            tender_file = request.files['tender_file']

            if tender_file.filename == '':
                return jsonify({
                    'success': False,
                    'error': '未选择技术需求文档文件'
                }), 400

            if not allowed_file(tender_file.filename):
                return jsonify({
                    'success': False,
                    'error': '不支持的文件格式，请上传 .doc, .docx, .pdf, .xlsx 或 .xls 文件'
                }), 400

            # 保存上传的文件
            upload_dir = config.get_path('uploads')
            upload_dir.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            tender_filename = secure_filename(f"{timestamp}_{tender_file.filename}")
            tender_path = upload_dir / tender_filename

            tender_file.save(str(tender_path))
            logger.info(f"需求文档已保存: {tender_path}")

        # 2. 获取参数
        company_id = request.form.get('companyId')
        project_name = request.form.get('projectName', '')  # 获取项目名称
        output_prefix = request.form.get('output_prefix', '技术方案')

        options = {
            'include_analysis': request.form.get('includeAnalysis', 'false').lower() == 'true',
            'include_mapping': request.form.get('includeMapping', 'false').lower() == 'true',
            'include_summary': request.form.get('includeSummary', 'false').lower() == 'true'
        }

        logger.info(f"生成选项: {options}")

        # 4. 阶段1：需求分析
        logger.info("开始阶段1：需求分析...")
        analyzer = RequirementAnalyzer()
        analysis_result = analyzer.analyze_document(str(tender_path))

        logger.info("需求分析完成")

        # 5. 阶段2：大纲生成
        logger.info("开始阶段2：大纲生成...")
        outline_gen = OutlineGenerator()
        outline_data = outline_gen.generate_outline(
            analysis_result,
            project_name=output_prefix
        )

        logger.info("大纲生成完成")

        # 6. 阶段3：产品文档匹配
        logger.info("开始阶段3：产品文档匹配...")
        matcher = ProductMatcher()
        matched_docs = matcher.match_documents(
            analysis_result.get('requirement_categories', []),
            company_id=int(company_id) if company_id else None
        )

        logger.info(f"产品文档匹配完成，共匹配 {sum(len(v) for v in matched_docs.values())} 份文档")

        # 7. 阶段4：方案组装
        logger.info("开始阶段4：方案组装...")
        assembler = ProposalAssembler()
        proposal = assembler.assemble_proposal(
            outline_data,
            analysis_result,
            matched_docs,
            options
        )

        logger.info("方案组装完成")

        # 8. 导出文件
        logger.info("开始导出文件...")
        exporter = WordExporter()

        output_dir = config.get_path('output')
        output_dir.mkdir(parents=True, exist_ok=True)

        output_files = {}

        # 智能文件命名：有项目名称时使用"项目名_类型_时间"，无项目名称时使用"前缀_时间"
        if project_name:
            proposal_filename = f"{project_name}_技术方案_{timestamp}.docx"
            analysis_filename = f"{project_name}_需求分析_{timestamp}.docx"
            mapping_filename = f"{project_name}_需求匹配表_{timestamp}.xlsx"
            summary_filename = f"{project_name}_生成报告_{timestamp}.txt"
        else:
            proposal_filename = f"{output_prefix}_{timestamp}.docx"
            analysis_filename = f"{output_prefix}_需求分析_{timestamp}.docx"
            mapping_filename = f"{output_prefix}_需求匹配表_{timestamp}.xlsx"
            summary_filename = f"{output_prefix}_生成报告_{timestamp}.txt"

        # 导出主方案
        proposal_path = output_dir / proposal_filename
        exporter.export_proposal(proposal, str(proposal_path))
        output_files['proposal'] = f"/api/downloads/{proposal_filename}"

        logger.info(f"主方案已导出: {proposal_path}")

        # 导出附件
        if options['include_analysis']:
            analysis_path = output_dir / analysis_filename
            exporter.export_analysis_report(analysis_result, str(analysis_path))
            output_files['analysis'] = f"/api/downloads/{analysis_filename}"

            logger.info(f"需求分析报告已导出: {analysis_path}")

        if options['include_mapping']:
            mapping_path = output_dir / mapping_filename

            mapping_data = []
            for attachment in proposal.get('attachments', []):
                if attachment['type'] == 'mapping':
                    mapping_data = attachment['data']
                    break

            exporter.export_mapping_table(mapping_data, str(mapping_path))
            output_files['mapping'] = f"/api/downloads/{mapping_filename}"

            logger.info(f"需求匹配表已导出: {mapping_path}")

        if options['include_summary']:
            summary_path = output_dir / summary_filename

            summary_data = {}
            for attachment in proposal.get('attachments', []):
                if attachment['type'] == 'summary':
                    summary_data = attachment['data']
                    break

            exporter.export_summary_report(summary_data, str(summary_path))
            output_files['summary'] = f"/api/downloads/{summary_filename}"

            logger.info(f"生成报告已导出: {summary_path}")

        # 9. 统计信息
        requirements_count = analysis_result.get('document_summary', {}).get('total_requirements', 0)
        sections_count = len(outline_data.get('chapters', []))
        matches_count = sum(len(docs) for docs in matched_docs.values())

        # 10. 返回结果
        response = {
            'success': True,
            'requirements_count': requirements_count,
            'features_count': 0,  # 暂时为0
            'sections_count': sections_count,
            'matches_count': matches_count,
            'output_files': output_files
        }

        logger.info("技术方案生成成功")
        return jsonify(response)

    except Exception as e:
        logger.error(f"技术方案生成失败: {e}", exc_info=True)
        error_trace = traceback.format_exc()

        return jsonify({
            'success': False,
            'error': str(e),
            'trace': error_trace if config.get('debug', False) else None
        }), 500


@api_outline_bp.route('/generate-proposal-stream', methods=['POST'])
def generate_proposal_stream():
    """
    生成技术方案API（流式SSE版本）
    实时推送生成进度

    请求参数（multipart/form-data）:
    - tender_file: 技术需求文档文件
    - product_file: 产品文档文件（可选）
    - outputPrefix: 输出文件名前缀
    - companyId: 公司ID
    - projectName: 项目名称（可选，从HITL传递）
    - technicalFileTaskId: HITL任务ID（可选）
    - includeAnalysis: 是否包含需求分析
    - includeMapping: 是否生成匹配表
    - includeSummary: 是否生成总结报告

    返回: text/event-stream
    """

    def generate_events():
        """生成SSE事件流"""
        try:
            # 发送初始进度
            yield f"data: {json.dumps({'stage': 'init', 'progress': 0, 'message': '准备生成技术方案...'}, ensure_ascii=False)}\n\n"

            # 1. 参数解析（复用原有逻辑）
            yield f"data: {json.dumps({'stage': 'init', 'progress': 5, 'message': '解析请求参数...'}, ensure_ascii=False)}\n\n"

            tender_file = request.files.get('tender_file')
            product_file = request.files.get('product_file')
            output_prefix = request.form.get('outputPrefix', '技术方案')
            company_id = request.form.get('companyId')
            project_name = request.form.get('projectName', '')
            project_id = request.form.get('technicalFileTaskId', '') or request.form.get('projectId', '')

            # 生成选项
            options = {
                'include_analysis': request.form.get('includeAnalysis', 'false').lower() == 'true',
                'include_mapping': request.form.get('includeMapping', 'false').lower() == 'true',
                'include_summary': request.form.get('includeSummary', 'false').lower() == 'true'
            }

            # 2. 获取技术需求文件路径
            if project_id:
                # 从HITL项目加载
                yield f"data: {json.dumps({'stage': 'init', 'progress': 10, 'message': f'从投标项目加载技术需求文件 (project_id={project_id})...'}, ensure_ascii=False)}\n\n"

                # 搜索HITL技术需求文件
                technical_files_base = config.get_path('upload') / 'technical_files'
                tender_path = None

                logger.info(f"搜索HITL项目文件, project_id: {project_id}, 搜索路径: {technical_files_base}")

                for year_dir in technical_files_base.glob('*'):
                    if not year_dir.is_dir():
                        continue
                    logger.debug(f"检查年份目录: {year_dir}")
                    for month_dir in year_dir.glob('*'):
                        if not month_dir.is_dir():
                            continue
                        logger.debug(f"检查月份目录: {month_dir}")
                        project_dir = month_dir / str(project_id)
                        logger.debug(f"检查项目目录: {project_dir}, 是否存在: {project_dir.exists()}")
                        if project_dir.exists():
                            # 查找技术需求文件（第一个文件）
                            technical_files = list(project_dir.glob('*.*'))
                            logger.debug(f"找到的文件: {technical_files}")
                            if technical_files:
                                tender_path = technical_files[0]
                                logger.info(f"找到HITL技术需求文件: {tender_path.name}, 路径: {tender_path}")
                                break
                    if tender_path:
                        break

                if not tender_path:
                    # 添加详细的错误信息
                    logger.error(f'未找到项目的技术需求文件: project_id={project_id}')
                    logger.error(f'搜索路径: {technical_files_base}')
                    # 列出所有可用的项目目录
                    available_projects = []
                    for year_dir in technical_files_base.glob('*'):
                        if year_dir.is_dir():
                            for month_dir in year_dir.glob('*'):
                                if month_dir.is_dir():
                                    for proj_dir in month_dir.glob('*'):
                                        if proj_dir.is_dir():
                                            available_projects.append(str(proj_dir))
                    logger.error(f'可用的项目目录: {available_projects}')
                    raise ValueError(f'未找到项目的技术需求文件: project_id={project_id}')
            elif tender_file:
                # 上传文件
                yield f"data: {json.dumps({'stage': 'init', 'progress': 10, 'message': '保存上传的技术需求文件...'}, ensure_ascii=False)}\n\n"
                if not allowed_file(tender_file.filename):
                    raise ValueError('文件类型不支持')

                upload_dir = config.get_path('uploads') / 'tender_processing' / datetime.now().strftime('%Y/%m')
                upload_dir.mkdir(parents=True, exist_ok=True)

                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = secure_filename(f"{timestamp}_{tender_file.filename}")
                tender_path = upload_dir / filename
                tender_file.save(str(tender_path))
            else:
                raise ValueError('未提供技术需求文档文件')

            # 3. 阶段1：需求分析
            yield f"data: {json.dumps({'stage': 'analysis', 'progress': 15, 'message': '🔍 正在分析技术需求文档...'}, ensure_ascii=False)}\n\n"

            analyzer = RequirementAnalyzer()
            analysis_result = analyzer.analyze_document(str(tender_path))

            yield f"data: {json.dumps({'stage': 'analysis', 'progress': 30, 'message': '✓ 需求分析完成'}, ensure_ascii=False)}\n\n"

            # 发送完整的需求分析结果供前端展示
            try:
                # 确保analysis_result可以被JSON序列化
                analysis_result_serializable = json.loads(json.dumps(analysis_result, ensure_ascii=False, default=str))
                yield f"data: {json.dumps({'stage': 'analysis_completed', 'analysis_result': analysis_result_serializable}, ensure_ascii=False)}\n\n"
            except Exception as e:
                logger.warning(f"无法序列化需求分析结果: {e}, 跳过前端展示")
                # 继续执行,不影响后续流程

            # 4. 阶段2：大纲生成
            yield f"data: {json.dumps({'stage': 'outline', 'progress': 35, 'message': '📝 正在生成技术方案大纲...'}, ensure_ascii=False)}\n\n"

            outline_gen = OutlineGenerator()
            outline_data = outline_gen.generate_outline(
                analysis_result,
                project_name=output_prefix
            )

            yield f"data: {json.dumps({'stage': 'outline', 'progress': 55, 'message': '✓ 大纲生成完成'}, ensure_ascii=False)}\n\n"

            # 发送完整的大纲数据供前端展示
            try:
                # 确保outline_data可以被JSON序列化
                outline_data_serializable = json.loads(json.dumps(outline_data, ensure_ascii=False, default=str))
                yield f"data: {json.dumps({'stage': 'outline_completed', 'outline_data': outline_data_serializable}, ensure_ascii=False)}\n\n"
            except Exception as e:
                logger.warning(f"无法序列化大纲数据: {e}, 跳过前端展示")
                # 继续执行,不影响后续流程

            # 5. 阶段3：产品文档匹配
            yield f"data: {json.dumps({'stage': 'matching', 'progress': 60, 'message': '🔗 正在匹配产品文档...'}, ensure_ascii=False)}\n\n"

            matcher = ProductMatcher()
            matched_docs = matcher.match_documents(
                analysis_result.get('requirement_categories', []),
                company_id=int(company_id) if company_id else None
            )

            matches_count = sum(len(v) for v in matched_docs.values())
            yield f"data: {json.dumps({'stage': 'matching', 'progress': 70, 'message': f'✓ 文档匹配完成（匹配到 {matches_count} 份文档）'}, ensure_ascii=False)}\n\n"

            # 6. 阶段4：方案组装
            yield f"data: {json.dumps({'stage': 'assembly', 'progress': 75, 'message': '⚙️ 正在组装技术方案...'}, ensure_ascii=False)}\n\n"

            assembler = ProposalAssembler()
            proposal = assembler.assemble_proposal(
                outline_data,
                analysis_result,
                matched_docs,
                options
            )

            yield f"data: {json.dumps({'stage': 'assembly', 'progress': 85, 'message': '✓ 方案组装完成'}, ensure_ascii=False)}\n\n"

            # 7. 导出文件
            yield f"data: {json.dumps({'stage': 'export', 'progress': 90, 'message': '💾 正在导出文件...'}, ensure_ascii=False)}\n\n"

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_dir = config.get_path('output')
            output_dir.mkdir(parents=True, exist_ok=True)

            exporter = WordExporter()
            output_files = {}

            # 文件命名
            if project_name:
                proposal_filename = f"{project_name}_技术方案_{timestamp}.docx"
                analysis_filename = f"{project_name}_需求分析_{timestamp}.docx"
                mapping_filename = f"{project_name}_需求匹配表_{timestamp}.xlsx"
                summary_filename = f"{project_name}_生成报告_{timestamp}.txt"
            else:
                proposal_filename = f"{output_prefix}_{timestamp}.docx"
                analysis_filename = f"{output_prefix}_需求分析_{timestamp}.docx"
                mapping_filename = f"{output_prefix}_需求匹配表_{timestamp}.xlsx"
                summary_filename = f"{output_prefix}_生成报告_{timestamp}.txt"

            # 导出主方案
            proposal_path = output_dir / proposal_filename
            exporter.export_proposal(proposal, str(proposal_path))
            output_files['proposal'] = f"/api/downloads/{proposal_filename}"

            # 导出附件
            if options['include_analysis']:
                analysis_path = output_dir / analysis_filename
                exporter.export_analysis_report(analysis_result, str(analysis_path))
                output_files['analysis'] = f"/api/downloads/{analysis_filename}"

            if options['include_mapping']:
                mapping_path = output_dir / mapping_filename
                mapping_data = []
                for attachment in proposal.get('attachments', []):
                    if attachment['type'] == 'mapping':
                        mapping_data = attachment['data']
                        break
                exporter.export_mapping_table(mapping_data, str(mapping_path))
                output_files['mapping'] = f"/api/downloads/{mapping_filename}"

            if options['include_summary']:
                summary_path = output_dir / summary_filename
                summary_data = {}
                for attachment in proposal.get('attachments', []):
                    if attachment['type'] == 'summary':
                        summary_data = attachment['data']
                        break
                exporter.export_summary_report(summary_data, str(summary_path))
                output_files['summary'] = f"/api/downloads/{summary_filename}"

            # 统计信息
            requirements_count = analysis_result.get('document_summary', {}).get('total_requirements', 0)
            sections_count = len(outline_data.get('chapters', []))

            # 8. 完成
            result = {
                'stage': 'completed',
                'progress': 100,
                'message': '✅ 技术方案生成成功！',
                'success': True,
                'requirements_count': requirements_count,
                'features_count': 0,
                'sections_count': sections_count,
                'matches_count': matches_count,
                'output_file': str(proposal_path),  # ✅ 添加文件系统完整路径，与商务应答/点对点应答保持一致
                'output_files': output_files  # 保留下载URL字典
            }

            yield f"data: {json.dumps(result, ensure_ascii=False)}\n\n"
            logger.info("技术方案生成成功（SSE流式）")

        except Exception as e:
            logger.error(f"技术方案生成失败（SSE流式）: {e}", exc_info=True)
            error_data = {
                'stage': 'error',
                'progress': 0,
                'message': f'生成失败: {str(e)}',
                'success': False,
                'error': str(e)
            }
            yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"

    return Response(
        stream_with_context(generate_events()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no'
        }
    )


@api_outline_bp.route('/downloads/<filename>', methods=['GET'])
def download_file(filename):
    """
    下载生成的文件

    Args:
        filename: 文件名

    Returns:
        文件内容
    """
    try:
        output_dir = config.get_path('output')
        file_path = output_dir / filename

        if not file_path.exists():
            return jsonify({
                'success': False,
                'error': '文件不存在'
            }), 404

        # 根据文件扩展名设置MIME类型
        ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''

        mime_types = {
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'txt': 'text/plain',
            'pdf': 'application/pdf'
        }

        mimetype = mime_types.get(ext, 'application/octet-stream')

        return send_file(
            str(file_path),
            as_attachment=True,
            download_name=filename,
            mimetype=mimetype
        )

    except Exception as e:
        logger.error(f"文件下载失败: {e}", exc_info=True)

        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_outline_bp.route('/generate-proposal-stream-v2', methods=['POST'])
def generate_proposal_stream_v2():
    """
    生成技术方案API（流式SSE版本 V2 - 支持实时内容推送）
    实时推送生成进度和章节内容

    请求参数（multipart/form-data）:
    - tender_file: 技术需求文档文件
    - outputPrefix: 输出文件名前缀
    - companyId: 公司ID
    - projectName: 项目名称
    - projectId: 项目ID（从HITL传递）
    - includeAnalysis: 是否包含需求分析
    - includeMapping: 是否生成匹配表
    - includeSummary: 是否生成总结报告
    - useStreamingContent: 是否使用流式内容生成（默认true）

    返回: text/event-stream
    """

    def generate_events():
        """生成SSE事件流"""
        try:
            # 初始化
            yield f"data: {json.dumps({'stage': 'init', 'progress': 0, 'message': '准备生成技术方案...'}, ensure_ascii=False)}\n\n"

            # 参数解析
            yield f"data: {json.dumps({'stage': 'init', 'progress': 5, 'message': '解析请求参数...'}, ensure_ascii=False)}\n\n"

            tender_file = request.files.get('tender_file')
            output_prefix = request.form.get('outputPrefix', '技术方案')
            company_id = request.form.get('companyId')
            project_name = request.form.get('projectName', '')
            project_id = request.form.get('projectId', '')
            use_streaming_content = request.form.get('useStreamingContent', 'true').lower() == 'true'

            # 生成选项
            options = {
                'include_analysis': request.form.get('includeAnalysis', 'false').lower() == 'true',
                'include_mapping': request.form.get('includeMapping', 'false').lower() == 'true',
                'include_summary': request.form.get('includeSummary', 'false').lower() == 'true'
            }

            # 获取技术需求文件路径
            if project_id:
                yield f"data: {json.dumps({'stage': 'init', 'progress': 10, 'message': f'从投标项目加载技术需求文件...'}, ensure_ascii=False)}\n\n"

                technical_files_base = config.get_path('upload') / 'technical_files'
                tender_path = None

                for year_dir in technical_files_base.glob('*'):
                    if not year_dir.is_dir():
                        continue
                    for month_dir in year_dir.glob('*'):
                        if not month_dir.is_dir():
                            continue
                        project_dir = month_dir / str(project_id)
                        if project_dir.exists():
                            technical_files = list(project_dir.glob('*.*'))
                            if technical_files:
                                tender_path = technical_files[0]
                                logger.info(f"找到HITL技术需求文件: {tender_path}")
                                break
                    if tender_path:
                        break

                if not tender_path:
                    raise ValueError(f'未找到项目的技术需求文件: project_id={project_id}')
            elif tender_file:
                yield f"data: {json.dumps({'stage': 'init', 'progress': 10, 'message': '保存上传的技术需求文件...'}, ensure_ascii=False)}\n\n"

                if not allowed_file(tender_file.filename):
                    raise ValueError('文件类型不支持')

                upload_dir = config.get_path('uploads') / 'tender_processing' / datetime.now().strftime('%Y/%m')
                upload_dir.mkdir(parents=True, exist_ok=True)

                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = secure_filename(f"{timestamp}_{tender_file.filename}")
                tender_path = upload_dir / filename
                tender_file.save(str(tender_path))
            else:
                raise ValueError('未提供技术需求文档文件')

            # 阶段1：需求分析
            yield f"data: {json.dumps({'stage': 'analysis', 'progress': 15, 'message': '🔍 正在分析技术需求文档...'}, ensure_ascii=False)}\n\n"

            analyzer = RequirementAnalyzer()
            analysis_result = analyzer.analyze_document(str(tender_path))

            yield f"data: {json.dumps({'stage': 'analysis', 'progress': 30, 'message': '✓ 需求分析完成'}, ensure_ascii=False)}\n\n"

            # 阶段2：大纲生成
            yield f"data: {json.dumps({'stage': 'outline', 'progress': 35, 'message': '📝 正在生成技术方案大纲...'}, ensure_ascii=False)}\n\n"

            outline_gen = OutlineGenerator()
            outline_data = outline_gen.generate_outline(analysis_result, project_name=output_prefix)

            yield f"data: {json.dumps({'stage': 'outline', 'progress': 55, 'message': '✓ 大纲生成完成'}, ensure_ascii=False)}\n\n"

            # 阶段3：产品文档匹配
            yield f"data: {json.dumps({'stage': 'matching', 'progress': 60, 'message': '🔗 正在匹配产品文档...'}, ensure_ascii=False)}\n\n"

            matcher = ProductMatcher()
            matched_docs = matcher.match_documents(
                analysis_result.get('requirement_categories', []),
                company_id=int(company_id) if company_id else None
            )

            matches_count = sum(len(v) for v in matched_docs.values())
            yield f"data: {json.dumps({'stage': 'matching', 'progress': 70, 'message': f'✓ 文档匹配完成（匹配到 {matches_count} 份文档）'}, ensure_ascii=False)}\n\n"

            # 阶段4：方案组装（流式）
            yield f"data: {json.dumps({'stage': 'assembly', 'progress': 75, 'message': '⚙️ 正在组装技术方案...'}, ensure_ascii=False)}\n\n"

            assembler = ProposalAssembler()

            # 选择流式或非流式组装
            if use_streaming_content:
                logger.info("使用流式内容生成模式")
                proposal = None

                for event in assembler.assemble_proposal_stream(outline_data, analysis_result, matched_docs, options):
                    event_type = event.get('type')

                    if event_type == 'chapter_start':
                        # 推送章节开始
                        chapter_start_data = {
                            'stage': 'content_generation',
                            'event': 'chapter_start',
                            'chapter_number': event.get('chapter_number', ''),
                            'chapter_title': event.get('chapter_title', ''),
                            'message': f"📄 开始生成 {event.get('chapter_number', '')} {event.get('chapter_title', '')}..."
                        }
                        yield f"data: {json.dumps(chapter_start_data, ensure_ascii=False)}\n\n"

                    elif event_type == 'content_chunk':
                        # 推送内容片段
                        content_chunk_data = {
                            'stage': 'content_generation',
                            'event': 'content_chunk',
                            'chapter_number': event.get('chapter_number', ''),
                            'content': event.get('chunk', '')
                        }
                        yield f"data: {json.dumps(content_chunk_data, ensure_ascii=False)}\n\n"

                    elif event_type == 'chapter_end':
                        # 推送章节完成
                        chapter_end_data = {
                            'stage': 'content_generation',
                            'event': 'chapter_end',
                            'chapter_number': event.get('chapter_number', ''),
                            'message': f"✓ {event.get('chapter_title', '')} 生成完成"
                        }
                        yield f"data: {json.dumps(chapter_end_data, ensure_ascii=False)}\n\n"

                    elif event_type == 'completed':
                        # 保存方案数据
                        proposal = event['proposal']

                    elif event_type == 'error':
                        raise Exception(event['error'])

                if not proposal:
                    raise ValueError("流式组装未返回完整方案")

                yield f"data: {json.dumps({'stage': 'assembly', 'progress': 85, 'message': '✓ 方案组装完成（流式）'}, ensure_ascii=False)}\n\n"
            else:
                # 使用非流式组装（原有逻辑）
                proposal = assembler.assemble_proposal(outline_data, analysis_result, matched_docs, options)
                yield f"data: {json.dumps({'stage': 'assembly', 'progress': 85, 'message': '✓ 方案组装完成'}, ensure_ascii=False)}\n\n"

            # 导出文件
            yield f"data: {json.dumps({'stage': 'export', 'progress': 90, 'message': '💾 正在导出文件...'}, ensure_ascii=False)}\n\n"

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_dir = config.get_path('output')
            output_dir.mkdir(parents=True, exist_ok=True)

            exporter = WordExporter()
            output_files = {}

            # 文件命名
            if project_name:
                proposal_filename = f"{project_name}_技术方案_{timestamp}.docx"
                analysis_filename = f"{project_name}_需求分析_{timestamp}.docx"
                mapping_filename = f"{project_name}_需求匹配表_{timestamp}.xlsx"
                summary_filename = f"{project_name}_生成报告_{timestamp}.txt"
            else:
                proposal_filename = f"{output_prefix}_{timestamp}.docx"
                analysis_filename = f"{output_prefix}_需求分析_{timestamp}.docx"
                mapping_filename = f"{output_prefix}_需求匹配表_{timestamp}.xlsx"
                summary_filename = f"{output_prefix}_生成报告_{timestamp}.txt"

            # 导出主方案
            proposal_path = output_dir / proposal_filename
            exporter.export_proposal(proposal, str(proposal_path))
            output_files['proposal'] = f"/api/downloads/{proposal_filename}"

            # 导出附件
            if options['include_analysis']:
                analysis_path = output_dir / analysis_filename
                exporter.export_analysis_report(analysis_result, str(analysis_path))
                output_files['analysis'] = f"/api/downloads/{analysis_filename}"

            if options['include_mapping']:
                mapping_path = output_dir / mapping_filename
                mapping_data = []
                for attachment in proposal.get('attachments', []):
                    if attachment['type'] == 'mapping':
                        mapping_data = attachment['data']
                        break
                exporter.export_mapping_table(mapping_data, str(mapping_path))
                output_files['mapping'] = f"/api/downloads/{mapping_filename}"

            if options['include_summary']:
                summary_path = output_dir / summary_filename
                summary_data = {}
                for attachment in proposal.get('attachments', []):
                    if attachment['type'] == 'summary':
                        summary_data = attachment['data']
                        break
                exporter.export_summary_report(summary_data, str(summary_path))
                output_files['summary'] = f"/api/downloads/{summary_filename}"

            # 统计信息
            requirements_count = analysis_result.get('document_summary', {}).get('total_requirements', 0)
            sections_count = len(outline_data.get('chapters', []))

            # 完成
            result = {
                'stage': 'completed',
                'progress': 100,
                'message': '✅ 技术方案生成成功！',
                'success': True,
                'requirements_count': requirements_count,
                'features_count': 0,
                'sections_count': sections_count,
                'matches_count': matches_count,
                'output_file': str(proposal_path),
                'output_files': output_files,
                'streaming_mode': use_streaming_content
            }

            yield f"data: {json.dumps(result, ensure_ascii=False)}\n\n"
            logger.info("技术方案生成成功（SSE流式V2）")

        except Exception as e:
            logger.error(f"技术方案生成失败（SSE流式V2）: {e}", exc_info=True)
            error_data = {
                'stage': 'error',
                'progress': 0,
                'message': f'生成失败: {str(e)}',
                'success': False,
                'error': str(e)
            }
            yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"

    return Response(
        stream_with_context(generate_events()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no'
        }
    )


# 导出蓝图
__all__ = ['api_outline_bp']
