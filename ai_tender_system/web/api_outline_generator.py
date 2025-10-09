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
from flask import Blueprint, request, jsonify, send_file
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

        # 1. 验证请求
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

        # 2. 获取参数
        company_id = request.form.get('companyId')
        output_prefix = request.form.get('output_prefix', '技术方案')

        options = {
            'include_analysis': request.form.get('includeAnalysis', 'false').lower() == 'true',
            'include_mapping': request.form.get('includeMapping', 'false').lower() == 'true',
            'include_summary': request.form.get('includeSummary', 'false').lower() == 'true'
        }

        logger.info(f"生成选项: {options}")

        # 3. 保存上传的文件
        upload_dir = config.get_path('uploads')
        upload_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        tender_filename = secure_filename(f"{timestamp}_{tender_file.filename}")
        tender_path = upload_dir / tender_filename

        tender_file.save(str(tender_path))
        logger.info(f"需求文档已保存: {tender_path}")

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

        # 导出主方案
        proposal_filename = f"{output_prefix}_{timestamp}.docx"
        proposal_path = output_dir / proposal_filename
        exporter.export_proposal(proposal, str(proposal_path))
        output_files['proposal'] = f"/downloads/{proposal_filename}"

        logger.info(f"主方案已导出: {proposal_path}")

        # 导出附件
        if options['include_analysis']:
            analysis_filename = f"{output_prefix}_需求分析_{timestamp}.docx"
            analysis_path = output_dir / analysis_filename
            exporter.export_analysis_report(analysis_result, str(analysis_path))
            output_files['analysis'] = f"/downloads/{analysis_filename}"

            logger.info(f"需求分析报告已导出: {analysis_path}")

        if options['include_mapping']:
            mapping_filename = f"{output_prefix}_需求匹配表_{timestamp}.xlsx"
            mapping_path = output_dir / mapping_filename

            mapping_data = []
            for attachment in proposal.get('attachments', []):
                if attachment['type'] == 'mapping':
                    mapping_data = attachment['data']
                    break

            exporter.export_mapping_table(mapping_data, str(mapping_path))
            output_files['mapping'] = f"/downloads/{mapping_filename}"

            logger.info(f"需求匹配表已导出: {mapping_path}")

        if options['include_summary']:
            summary_filename = f"{output_prefix}_生成报告_{timestamp}.txt"
            summary_path = output_dir / summary_filename

            summary_data = {}
            for attachment in proposal.get('attachments', []):
                if attachment['type'] == 'summary':
                    summary_data = attachment['data']
                    break

            exporter.export_summary_report(summary_data, str(summary_path))
            output_files['summary'] = f"/downloads/{summary_filename}"

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


# 导出蓝图
__all__ = ['api_outline_bp']
