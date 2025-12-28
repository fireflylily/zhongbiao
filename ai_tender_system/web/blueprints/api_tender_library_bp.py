#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
标书素材库API蓝图

提供历史标书和片段的管理功能：
1. 标书文档上传和管理
2. 片段/章节的CRUD和搜索
3. 素材检索
"""

import os
import uuid
from datetime import datetime
from pathlib import Path
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename

# 导入公共组件
import sys
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from common import get_module_logger
from web.middleware.permission import require_auth

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {'docx', 'doc', 'pdf'}

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 创建logger
logger = get_module_logger('api_tender_library')

# 创建蓝图
api_tender_library_bp = Blueprint('api_tender_library', __name__, url_prefix='/api/tender-library')


def get_document_manager():
    """获取标书文档管理器"""
    from modules.tender_library import TenderDocumentManager
    return TenderDocumentManager()


def get_excerpt_manager():
    """获取片段管理器"""
    from modules.tender_library import ExcerptManager
    return ExcerptManager()


# ===================
# 标书文档管理 API
# ===================

@api_tender_library_bp.route('/documents', methods=['GET'])
def list_tender_documents():
    """
    获取企业的标书文档列表

    Query params:
        company_id: 企业ID（必填）
        bid_result: 筛选投标结果 won/lost/unknown
        industry: 筛选行业
        page: 页码（默认1）
        page_size: 每页数量（默认20）
    """
    try:
        company_id = request.args.get('company_id', type=int)
        if not company_id:
            return jsonify({'success': False, 'error': '请提供企业ID'}), 400

        bid_result_cn = request.args.get('bid_result')
        industry = request.args.get('industry')
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)

        # 转换中文投标结果查询条件为数据库格式
        bid_result_map = {'中标': 'won', '未中标': 'lost', '待定': 'unknown'}
        bid_result = bid_result_map.get(bid_result_cn) if bid_result_cn else None

        manager = get_document_manager()
        documents = manager.list_documents(
            company_id=company_id,
            bid_result=bid_result,
            industry=industry,
            limit=page_size,
            offset=(page - 1) * page_size
        )

        # 转换数据库中的投标结果为中文显示
        bid_result_display = {'won': '中标', 'lost': '未中标', 'unknown': '待定'}
        for doc in documents:
            if doc.get('bid_result'):
                doc['bid_result'] = bid_result_display.get(doc['bid_result'], doc['bid_result'])

        return jsonify({
            'success': True,
            'data': documents,
            'total': len(documents),
            'page': page,
            'page_size': page_size
        })

    except Exception as e:
        logger.error(f"获取标书文档列表失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_tender_library_bp.route('/documents/<int:tender_doc_id>', methods=['GET'])
def get_tender_document(tender_doc_id):
    """获取标书文档详情"""
    try:
        manager = get_document_manager()
        document = manager.get_document(tender_doc_id)

        if not document:
            return jsonify({'success': False, 'error': '文档不存在'}), 404

        return jsonify({'success': True, 'data': document})

    except Exception as e:
        logger.error(f"获取标书文档详情失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_tender_library_bp.route('/documents', methods=['POST'])
@require_auth
def create_tender_document():
    """
    创建标书文档记录

    Body:
        company_id: 企业ID
        doc_name: 标书名称
        file_path: 文件路径
        file_name: 文件名
        file_type: 文件类型
        file_size: 文件大小
        ... 其他可选字段
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': '请提供文档信息'}), 400

        required = ['company_id', 'doc_name', 'file_path', 'file_name', 'file_type', 'file_size']
        for field in required:
            if field not in data:
                return jsonify({'success': False, 'error': f'缺少必填字段: {field}'}), 400

        manager = get_document_manager()
        doc_id = manager.create_document(**data)

        logger.info(f"创建标书文档成功: ID={doc_id}")
        return jsonify({
            'success': True,
            'data': {'tender_doc_id': doc_id},
            'message': '文档创建成功'
        })

    except Exception as e:
        logger.error(f"创建标书文档失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_tender_library_bp.route('/documents/upload', methods=['POST'])
@require_auth
def upload_tender_document():
    """
    上传标书文档

    Form data:
        file: 文件
        company_id: 企业ID
        project_name: 项目名称
        bid_result: 投标结果（中标/未中标/待定）
        bid_date: 投标日期（可选）
        notes: 备注（可选）
        related_products: 关联产品分类（JSON数组，可选）
    """
    try:
        # 检查文件
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': '请选择文件'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': '请选择文件'}), 400

        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': '不支持的文件格式，请上传 .docx, .doc 或 .pdf 文件'}), 400

        # 获取表单数据
        company_id = request.form.get('company_id', type=int)
        if not company_id:
            return jsonify({'success': False, 'error': '请提供企业ID'}), 400

        project_name = request.form.get('project_name', '').strip()
        bid_result_cn = request.form.get('bid_result', '待定')
        bid_date = request.form.get('bid_date')
        notes = request.form.get('notes', '')
        related_products = request.form.get('related_products', '')

        # 转换中文投标结果为数据库格式
        bid_result_map = {'中标': 'won', '未中标': 'lost', '待定': 'unknown'}
        bid_result = bid_result_map.get(bid_result_cn, 'unknown')

        # 生成安全的文件名
        original_filename = secure_filename(file.filename)
        file_ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else ''
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        safe_filename = f"{timestamp}_{unique_id}.{file_ext}"

        # 确定上传目录
        upload_dir = Path(project_root) / "data" / "tender_library" / str(company_id)
        upload_dir.mkdir(parents=True, exist_ok=True)

        # 保存文件
        file_path = upload_dir / safe_filename
        file.save(str(file_path))

        # 获取文件大小
        file_size = os.path.getsize(str(file_path))

        # 创建数据库记录
        manager = get_document_manager()
        doc_id = manager.create_document(
            company_id=company_id,
            doc_name=project_name or original_filename,
            project_name=project_name,
            file_path=str(file_path),
            file_name=original_filename,
            file_type=file_ext,
            file_size=file_size,
            bid_result=bid_result,
            bid_date=bid_date,
            notes=notes,
            related_products=related_products if related_products else None
        )

        logger.info(f"上传标书文档成功: ID={doc_id}, 文件={original_filename}, 关联产品={related_products}")
        return jsonify({
            'success': True,
            'data': {'tender_doc_id': doc_id},
            'message': '文档上传成功'
        })

    except Exception as e:
        logger.error(f"上传标书文档失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_tender_library_bp.route('/documents/<int:tender_doc_id>', methods=['PUT'])
@require_auth
def update_tender_document(tender_doc_id):
    """更新标书文档"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': '请提供更新信息'}), 400

        manager = get_document_manager()

        # 检查文档是否存在
        existing = manager.get_document(tender_doc_id)
        if not existing:
            return jsonify({'success': False, 'error': '文档不存在'}), 404

        success = manager.update_document(tender_doc_id, **data)

        if success:
            logger.info(f"更新标书文档成功: ID={tender_doc_id}")
            return jsonify({'success': True, 'message': '文档更新成功'})
        else:
            return jsonify({'success': False, 'error': '更新失败'}), 500

    except Exception as e:
        logger.error(f"更新标书文档失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_tender_library_bp.route('/documents/<int:tender_doc_id>', methods=['DELETE'])
@require_auth
def delete_tender_document(tender_doc_id):
    """删除标书文档"""
    try:
        manager = get_document_manager()

        # 检查文档是否存在
        existing = manager.get_document(tender_doc_id)
        if not existing:
            return jsonify({'success': False, 'error': '文档不存在'}), 404

        success = manager.delete_document(tender_doc_id)

        if success:
            logger.info(f"删除标书文档成功: ID={tender_doc_id}")
            return jsonify({'success': True, 'message': '文档删除成功'})
        else:
            return jsonify({'success': False, 'error': '删除失败'}), 500

    except Exception as e:
        logger.error(f"删除标书文档失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_tender_library_bp.route('/documents/<int:tender_doc_id>/extract', methods=['POST'])
@require_auth
def extract_excerpts(tender_doc_id):
    """
    从标书文档中提取片段

    使用 structure_parser 解析文档章节结构，提取结构化的素材片段。
    """
    try:
        doc_manager = get_document_manager()
        excerpt_manager = get_excerpt_manager()

        # 检查文档是否存在
        document = doc_manager.get_document(tender_doc_id)
        if not document:
            return jsonify({'success': False, 'error': '文档不存在'}), 404

        file_path = document.get('file_path')
        if not file_path or not os.path.exists(file_path):
            return jsonify({'success': False, 'error': '文档文件不存在'}), 404

        company_id = document.get('company_id')

        # 检查文件类型
        file_ext = file_path.rsplit('.', 1)[-1].lower() if '.' in file_path else ''
        if file_ext not in ['docx', 'doc']:
            # 对于非 Word 文件，使用旧的解析方式
            return _extract_excerpts_legacy(tender_doc_id, document, doc_manager, excerpt_manager)

        # 使用 structure_parser 解析章节结构
        from modules.tender_processing.structure_parser import DocumentStructureParser

        parser = DocumentStructureParser()
        try:
            result = parser.parse_document_structure(file_path)
        except Exception as parse_error:
            logger.error(f"解析文档结构失败: {parse_error}")
            # 降级到旧的解析方式
            return _extract_excerpts_legacy(tender_doc_id, document, doc_manager, excerpt_manager)

        if not result.get('success') or not result.get('chapters'):
            logger.warning(f"structure_parser 解析失败或无章节，降级到旧方式")
            return _extract_excerpts_legacy(tender_doc_id, document, doc_manager, excerpt_manager)

        chapters = result['chapters']

        # 打开 Word 文档提取内容
        from docx import Document as DocxDocument
        try:
            word_doc = DocxDocument(file_path)
        except Exception as e:
            logger.error(f"打开Word文档失败: {e}")
            return _extract_excerpts_legacy(tender_doc_id, document, doc_manager, excerpt_manager)

        # 清空旧的片段
        _delete_old_excerpts(tender_doc_id)

        # 递归保存章节为素材
        extracted_count = _save_chapters_as_excerpts(
            chapters=chapters,
            tender_doc_id=tender_doc_id,
            company_id=company_id,
            word_doc=word_doc,
            excerpt_manager=excerpt_manager
        )

        # 更新文档解析状态
        doc_manager.update_document(
            tender_doc_id,
            parse_status='completed',
            total_chapters=extracted_count
        )

        statistics = result.get('statistics', {})
        logger.info(f"提取片段完成: 文档ID={tender_doc_id}, 提取数量={extracted_count}")
        return jsonify({
            'success': True,
            'message': f'成功提取 {extracted_count} 个章节素材',
            'data': {
                'excerpt_count': extracted_count,
                'statistics': statistics
            }
        })

    except Exception as e:
        logger.error(f"提取片段失败: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


def _extract_excerpts_legacy(tender_doc_id, document, doc_manager, excerpt_manager):
    """
    旧版提取方式（降级方案）

    用于非 Word 文件或 structure_parser 解析失败时。
    """
    file_path = document.get('file_path')
    company_id = document.get('company_id')

    # 使用文档解析器解析文档
    from modules.document_parser.parser_manager import ParserManager
    parser = ParserManager()

    try:
        content = parser.parse_document_simple(file_path)
    except Exception as parse_error:
        logger.error(f"解析文档失败: {parse_error}")
        return jsonify({'success': False, 'error': f'解析文档失败: {str(parse_error)}'}), 500

    if not content or not content.strip():
        return jsonify({'success': False, 'error': '文档内容为空'}), 400

    # 清空旧的片段
    _delete_old_excerpts(tender_doc_id)

    # 按章节/段落拆分内容
    excerpts = _split_content_to_excerpts(content, document)
    extracted_count = 0

    for excerpt_data in excerpts:
        try:
            excerpt_manager.create_excerpt(
                tender_doc_id=tender_doc_id,
                company_id=company_id,
                content=excerpt_data['content'],
                chapter_number=excerpt_data.get('chapter_number'),
                chapter_title=excerpt_data.get('chapter_title'),
                chapter_level=excerpt_data.get('chapter_level', 1),
                category=excerpt_data.get('category'),
                quality_score=excerpt_data.get('quality_score', 0)
            )
            extracted_count += 1
        except Exception as e:
            logger.warning(f"创建片段失败: {e}")
            continue

    # 更新文档解析状态
    doc_manager.update_document(tender_doc_id, parse_status='completed', total_chapters=extracted_count)

    logger.info(f"提取片段完成(旧方式): 文档ID={tender_doc_id}, 提取数量={extracted_count}")
    return jsonify({
        'success': True,
        'message': f'成功提取 {extracted_count} 个片段',
        'data': {
            'excerpt_count': extracted_count
        }
    })


def _delete_old_excerpts(tender_doc_id: int):
    """删除文档的旧片段"""
    import sqlite3
    from pathlib import Path

    db_path = Path(__file__).parent.parent.parent / "data" / "knowledge_base.db"
    try:
        conn = sqlite3.connect(str(db_path))
        conn.execute("DELETE FROM tender_excerpts WHERE tender_doc_id = ?", (tender_doc_id,))
        conn.commit()
        conn.close()
        logger.info(f"已删除文档 {tender_doc_id} 的旧片段")
    except Exception as e:
        logger.warning(f"删除旧片段失败: {e}")


def _save_chapters_as_excerpts(
    chapters: list,
    tender_doc_id: int,
    company_id: int,
    word_doc,
    excerpt_manager,
    parent_excerpt_id: int = None
) -> int:
    """
    递归保存章节树为素材

    Args:
        chapters: 章节列表
        tender_doc_id: 标书文档ID
        company_id: 企业ID
        word_doc: python-docx Document 对象
        excerpt_manager: 片段管理器
        parent_excerpt_id: 父章节ID

    Returns:
        提取的片段数量
    """
    count = 0

    for chapter in chapters:
        # 提取章节内容
        content = _extract_chapter_content(
            word_doc,
            chapter.get('para_start_idx', 0),
            chapter.get('para_end_idx')
        )

        # 跳过空内容或过短内容
        if not content or len(content.strip()) < 50:
            # 仍然递归处理子章节
            if chapter.get('children'):
                count += _save_chapters_as_excerpts(
                    chapter['children'],
                    tender_doc_id, company_id, word_doc,
                    excerpt_manager, parent_excerpt_id
                )
            continue

        # 简单规则分类（基于标题关键词）
        category = _guess_category_by_title(chapter.get('title', ''))

        # 质量评分
        quality_score = _calculate_quality_score(content)

        # 存入数据库
        try:
            excerpt_id = excerpt_manager.create_excerpt(
                tender_doc_id=tender_doc_id,
                company_id=company_id,
                content=content,
                chapter_number=chapter.get('id', ''),
                chapter_title=chapter.get('title', ''),
                chapter_level=chapter.get('level', 1),
                parent_excerpt_id=parent_excerpt_id,
                category=category,
                quality_score=quality_score
            )
            count += 1

            # 递归处理子章节
            if chapter.get('children'):
                count += _save_chapters_as_excerpts(
                    chapter['children'],
                    tender_doc_id, company_id, word_doc,
                    excerpt_manager, excerpt_id
                )
        except Exception as e:
            logger.warning(f"创建片段失败: {e}, 章节={chapter.get('title', '')}")
            # 仍然递归处理子章节
            if chapter.get('children'):
                count += _save_chapters_as_excerpts(
                    chapter['children'],
                    tender_doc_id, company_id, word_doc,
                    excerpt_manager, parent_excerpt_id
                )

    return count


def _extract_chapter_content(word_doc, para_start_idx: int, para_end_idx: int) -> str:
    """
    从 Word 文档提取章节内容

    Args:
        word_doc: python-docx Document 对象
        para_start_idx: 起始段落索引
        para_end_idx: 结束段落索引

    Returns:
        章节文本内容
    """
    paragraphs = word_doc.paragraphs

    if para_end_idx is None:
        para_end_idx = len(paragraphs)

    content_parts = []
    for i in range(para_start_idx, min(para_end_idx, len(paragraphs))):
        text = paragraphs[i].text.strip()
        if text:
            content_parts.append(text)

    return '\n'.join(content_parts)


def _guess_category_by_title(title: str) -> str:
    """
    根据标题关键词猜测分类

    Args:
        title: 章节标题

    Returns:
        分类名称（中文，与前端一致）
    """
    if not title:
        return '其他'

    # 优先匹配规则（更精确的匹配放前面）
    # 规则：(关键词, 分类, 排除词列表)
    priority_rules = [
        # 售后服务 - 精确匹配
        ('维保', '售后服务', []),
        ('运维', '售后服务', []),
        ('售后', '售后服务', []),
        ('培训服务', '售后服务', []),
        ('培训方案', '售后服务', []),
        ('交付文档', '售后服务', []),
        ('验收', '售后服务', []),
        ('知识转移', '售后服务', []),

        # 技术方案 - 精确匹配
        ('技术方案', '技术方案', []),
        ('系统设计', '技术方案', []),
        ('总体设计', '技术方案', []),
        ('详细设计', '技术方案', []),
        ('架构设计', '技术方案', []),
        ('功能设计', '技术方案', []),
        ('接口方案', '技术方案', []),
        ('对接方案', '技术方案', []),
        ('具体接口', '技术方案', []),
        ('项目理解', '技术方案', []),
        ('项目背景', '技术方案', []),
        ('项目目标', '技术方案', []),
        ('需求分析', '技术方案', []),
        ('需求理解', '技术方案', []),
        ('解决方案', '技术方案', []),
        ('实施方案', '技术方案', []),
        ('部署方案', '技术方案', []),
        ('安全方案', '技术方案', []),
        ('安全保障', '技术方案', []),

        # 项目管理
        ('项目管理', '项目管理', []),
        ('进度计划', '项目管理', []),
        ('实施时间', '项目管理', []),
        ('实施计划', '项目管理', []),
        ('质量管理', '项目管理', []),
        ('风险管理', '项目管理', []),
        ('项目组织', '项目管理', []),
        ('组织架构', '项目管理', []),

        # 企业资质
        ('公司简介', '企业资质', []),
        ('公司介绍', '企业资质', []),
        ('企业介绍', '企业资质', []),
        ('公司基本情况', '企业资质', []),
        ('资质证书', '企业资质', []),
        ('业绩一览', '企业资质', []),
        ('项目经验', '企业资质', []),
        ('成功案例', '企业资质', []),
        ('合作案例', '企业资质', []),

        # 团队介绍
        ('团队成员', '团队介绍', []),
        ('项目团队', '团队介绍', []),
        ('人员配置', '团队介绍', []),
        ('人员情况', '团队介绍', []),
        ('服务团队', '团队介绍', []),
        ('人员简历', '团队介绍', []),
    ]

    # 先尝试精确匹配
    for keyword, category, excludes in priority_rules:
        if keyword in title:
            # 检查排除词
            excluded = False
            for ex in excludes:
                if ex in title:
                    excluded = True
                    break
            if not excluded:
                return category

    # 次级匹配（更宽泛的关键词）
    secondary_keywords = {
        '技术方案': ['架构', '设计', '方案', '接口', '开发', '集成', '对接'],
        '项目管理': ['进度', '计划', '管理', '组织'],
        '企业资质': ['公司', '企业', '资质', '业绩', '案例', '经验', '荣誉'],
        '团队介绍': ['团队', '人员', '简历'],
    }

    for category, keywords in secondary_keywords.items():
        for kw in keywords:
            if kw in title:
                # 避免把"服务方案"分到技术方案
                if kw == '方案' and '服务' in title:
                    continue
                # 避免把"开发服务"分到技术方案
                if kw == '开发' and '服务' in title:
                    continue
                return category

    return '其他'


def _split_content_to_excerpts(content: str, document: dict) -> list:
    """
    将文档内容拆分为片段

    Args:
        content: 文档文本内容
        document: 文档信息

    Returns:
        片段列表
    """
    import re

    excerpts = []

    # 按章节标题拆分（常见的章节标题模式）
    chapter_patterns = [
        # 一、二、三 等中文数字章节
        r'^(第[一二三四五六七八九十百]+[章节篇])\s*[、：:.]?\s*(.+?)$',
        # 1. 2. 3. 等阿拉伯数字章节
        r'^(\d+)\s*[、.:：]\s*(.+?)$',
        # 1.1 1.2 等多级编号
        r'^(\d+(?:\.\d+)+)\s*[、.:：]?\s*(.+?)$',
        # （一）（二）等带括号的中文数字
        r'^[（(]([一二三四五六七八九十]+)[）)]\s*(.+?)$',
    ]

    lines = content.split('\n')
    current_chapter = None
    current_content = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # 检查是否是章节标题
        is_chapter = False
        for pattern in chapter_patterns:
            match = re.match(pattern, line, re.MULTILINE)
            if match:
                # 保存上一个章节的内容
                if current_chapter and current_content:
                    content_text = '\n'.join(current_content).strip()
                    # 验证内容有效性
                    is_valid, reason = _is_valid_excerpt(content_text)
                    if is_valid and len(content_text) > 50:  # 有效且不过短
                        excerpts.append({
                            'chapter_number': current_chapter.get('number'),
                            'chapter_title': current_chapter.get('title'),
                            'chapter_level': current_chapter.get('level', 1),
                            'content': content_text,
                            'category': _guess_category(current_chapter.get('title', '')),
                            'quality_score': _calculate_quality_score(content_text)
                        })
                    else:
                        logger.debug(f"跳过无效片段: {reason}, 章节={current_chapter.get('title', '')}")

                # 开始新章节
                current_chapter = {
                    'number': match.group(1),
                    'title': match.group(2) if len(match.groups()) > 1 else line,
                    'level': _determine_chapter_level(match.group(1))
                }
                current_content = []
                is_chapter = True
                break

        if not is_chapter:
            current_content.append(line)

    # 处理最后一个章节
    if current_chapter and current_content:
        content_text = '\n'.join(current_content).strip()
        is_valid, reason = _is_valid_excerpt(content_text)
        if is_valid and len(content_text) > 50:
            excerpts.append({
                'chapter_number': current_chapter.get('number'),
                'chapter_title': current_chapter.get('title'),
                'chapter_level': current_chapter.get('level', 1),
                'content': content_text,
                'category': _guess_category(current_chapter.get('title', '')),
                'quality_score': _calculate_quality_score(content_text)
            })
        else:
            logger.debug(f"跳过无效片段: {reason}, 章节={current_chapter.get('title', '')}")

    # 如果没有识别到章节，按段落拆分
    if not excerpts:
        paragraphs = content.split('\n\n')
        valid_para_index = 0
        for para in paragraphs:
            para = para.strip()
            # 验证内容有效性
            is_valid, reason = _is_valid_excerpt(para)
            if is_valid and len(para) > 100:  # 有效且不过短
                valid_para_index += 1
                excerpts.append({
                    'chapter_number': str(valid_para_index),
                    'chapter_title': f'段落{valid_para_index}',
                    'chapter_level': 1,
                    'content': para,
                    'category': _guess_category(para[:50]),
                    'quality_score': _calculate_quality_score(para)
                })
            elif len(para) > 100:
                logger.debug(f"跳过无效段落: {reason}")

    return excerpts


def _determine_chapter_level(chapter_number: str) -> int:
    """根据章节编号确定级别"""
    if not chapter_number:
        return 1

    # 中文章节标题通常是一级
    if any(c in chapter_number for c in '第章节篇'):
        return 1

    # 计算数字层级 (1.1.1 = 3级)
    if '.' in chapter_number:
        return chapter_number.count('.') + 1

    return 1


def _guess_category(title: str) -> str:
    """根据标题猜测分类"""
    if not title:
        return '其他'

    category_keywords = {
        '公司介绍': ['公司', '企业', '简介', '关于我们', '概述'],
        '技术方案': ['技术', '方案', '架构', '设计', '实现'],
        '项目经验': ['项目', '案例', '经验', '业绩'],
        '团队介绍': ['团队', '人员', '资质', '专家'],
        '售后服务': ['售后', '服务', '保障', '支持', '运维'],
        '商务条款': ['商务', '报价', '价格', '付款', '合同'],
        '资质证书': ['资质', '证书', '认证', '荣誉'],
        '实施计划': ['实施', '进度', '计划', '里程碑', '工期'],
    }

    for category, keywords in category_keywords.items():
        for keyword in keywords:
            if keyword in title:
                return category

    return '其他'


def _is_valid_excerpt(content: str) -> tuple[bool, str]:
    """
    验证内容是否为有效的标书素材

    Args:
        content: 待验证的文本内容

    Returns:
        (是否有效, 原因)
    """
    import re

    if not content or not content.strip():
        return False, "内容为空"

    content = content.strip()

    # 1. 检测URL/API字符串（如 http://, https://, apiKey=, endpoint=）
    url_patterns = [
        r'https?://[^\s]+',  # HTTP/HTTPS URL
        r'apiKey\s*[=:]\s*[^\s]+',  # API密钥
        r'endpoint\s*[=:]\s*[^\s]+',  # 端点配置
        r'api\.[a-z]+\.[a-z]+',  # API域名模式
        r'Bearer\s+[A-Za-z0-9\-._~+/]+=*',  # Bearer Token
    ]
    for pattern in url_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        # 如果URL占比过高（超过20%），认为是技术配置内容
        url_length = sum(len(m) for m in matches)
        if url_length > len(content) * 0.2:
            return False, "包含过多URL/API配置"

    # 2. 检测敏感信息（手机号、身份证号）
    sensitive_patterns = [
        r'1[3-9]\d{9}',  # 手机号
        r'\d{6}(19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dXx]',  # 身份证号
        r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}',  # 邮箱地址（可能是测试数据）
    ]
    sensitive_count = 0
    for pattern in sensitive_patterns:
        matches = re.findall(pattern, content)
        sensitive_count += len(matches)
    if sensitive_count > 3:  # 如果包含超过3个敏感信息，可能是测试数据
        return False, "包含过多敏感信息（可能是测试数据）"

    # 3. 检测代码/JSON片段
    code_indicators = [
        r'\{[^{}]*"[^"]+"\s*:\s*[^{}]+\}',  # JSON对象
        r'\[[^\[\]]*\{[^{}]+\}[^\[\]]*\]',  # JSON数组
        r'function\s*\([^)]*\)\s*\{',  # JavaScript函数
        r'def\s+\w+\s*\([^)]*\)\s*:',  # Python函数
        r'import\s+[a-zA-Z_][a-zA-Z0-9_]*',  # import语句
        r'<[a-zA-Z][^>]*>[^<]*</[a-zA-Z]+>',  # HTML/XML标签
        r'SELECT\s+.*\s+FROM\s+',  # SQL语句
    ]
    code_match_count = 0
    for pattern in code_indicators:
        if re.search(pattern, content, re.IGNORECASE):
            code_match_count += 1
    if code_match_count >= 2:  # 如果多个代码特征匹配
        return False, "包含代码/技术配置内容"

    # 4. 检测中文内容比例（标书应该主要是中文）
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', content))
    total_chars = len(re.findall(r'[a-zA-Z\u4e00-\u9fff]', content))
    if total_chars > 0:
        chinese_ratio = chinese_chars / total_chars
        if chinese_ratio < 0.3:  # 中文占比低于30%
            return False, "中文内容比例过低"

    # 5. 检测纯数字/符号内容
    meaningful_chars = len(re.findall(r'[\u4e00-\u9fffa-zA-Z]', content))
    if meaningful_chars < 20:  # 有意义的字符太少
        return False, "有效内容过少"

    # 6. 检测重复字符（如 "=====" 或 "-----"）
    if re.search(r'(.)\1{10,}', content):  # 连续重复10次以上
        return False, "包含重复填充字符"

    return True, "有效"


def _calculate_quality_score(content: str) -> int:
    """计算内容质量评分（0-100）"""
    import re

    if not content:
        return 0

    # 先验证内容有效性
    is_valid, reason = _is_valid_excerpt(content)
    if not is_valid:
        return 0  # 无效内容直接返回0分

    score = 50  # 基础分

    # 内容长度加分
    length = len(content)
    if length > 500:
        score += 10
    if length > 1000:
        score += 10
    if length > 2000:
        score += 10

    # 格式规范加分（有段落）
    if '\n' in content:
        score += 5

    # 有数据支撑加分
    if re.search(r'\d+%|\d+万|\d+亿', content):
        score += 10

    # 专业术语加分
    professional_terms = [
        '技术方案', '实施方案', '项目管理', '质量保证', '售后服务',
        '系统架构', '安全保障', '风险控制', '应急预案', '培训方案',
        '验收标准', '进度计划', '资质证书', '业绩案例', '团队配置'
    ]
    term_count = sum(1 for term in professional_terms if term in content)
    if term_count > 0:
        score += min(term_count * 3, 15)  # 最多加15分

    # 结构化内容加分（有编号列表）
    if re.search(r'^\s*[（(]?[一二三四五六七八九十\d]+[）)、.:：]', content, re.MULTILINE):
        score += 5

    # 控制分数范围
    return min(100, max(0, score))


@api_tender_library_bp.route('/documents/stats', methods=['GET'])
def get_document_stats():
    """
    获取标书库统计信息

    Query params:
        company_id: 企业ID（必填）
    """
    try:
        company_id = request.args.get('company_id', type=int)
        if not company_id:
            return jsonify({'success': False, 'error': '请提供企业ID'}), 400

        manager = get_document_manager()
        stats = manager.get_stats(company_id)

        return jsonify({'success': True, 'data': stats})

    except Exception as e:
        logger.error(f"获取统计信息失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_tender_library_bp.route('/documents/industries', methods=['GET'])
def get_industries():
    """获取企业标书涉及的所有行业"""
    try:
        company_id = request.args.get('company_id', type=int)
        if not company_id:
            return jsonify({'success': False, 'error': '请提供企业ID'}), 400

        manager = get_document_manager()
        industries = manager.get_industries(company_id)

        return jsonify({'success': True, 'data': industries})

    except Exception as e:
        logger.error(f"获取行业列表失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ===================
# 标书片段管理 API
# ===================

@api_tender_library_bp.route('/excerpts', methods=['GET'])
def list_excerpts():
    """
    获取片段列表

    Query params:
        company_id: 企业ID（必填）
        tender_doc_id: 筛选特定标书
        category: 筛选分类
        is_highlighted: 筛选精选 true/false
        min_quality: 最低质量分
        page: 页码
        page_size: 每页数量
    """
    try:
        company_id = request.args.get('company_id', type=int)
        if not company_id:
            return jsonify({'success': False, 'error': '请提供企业ID'}), 400

        tender_doc_id = request.args.get('tender_doc_id', type=int)
        category = request.args.get('category')
        is_highlighted = request.args.get('is_highlighted')
        min_quality = request.args.get('min_quality', type=int)
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)

        # 转换布尔值
        if is_highlighted is not None:
            is_highlighted = is_highlighted.lower() == 'true'

        manager = get_excerpt_manager()

        # 获取总数
        total = manager.count_excerpts(
            company_id=company_id,
            tender_doc_id=tender_doc_id,
            category=category,
            is_highlighted=is_highlighted,
            min_quality=min_quality
        )

        # 获取分页数据
        excerpts = manager.list_excerpts(
            company_id=company_id,
            tender_doc_id=tender_doc_id,
            category=category,
            is_highlighted=is_highlighted,
            min_quality=min_quality,
            limit=page_size,
            offset=(page - 1) * page_size
        )

        return jsonify({
            'success': True,
            'data': excerpts,
            'total': total,
            'page': page,
            'page_size': page_size
        })

    except Exception as e:
        logger.error(f"获取片段列表失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_tender_library_bp.route('/excerpts/<int:excerpt_id>', methods=['GET'])
def get_excerpt(excerpt_id):
    """获取片段详情"""
    try:
        manager = get_excerpt_manager()
        excerpt = manager.get_excerpt(excerpt_id)

        if not excerpt:
            return jsonify({'success': False, 'error': '片段不存在'}), 404

        return jsonify({'success': True, 'data': excerpt})

    except Exception as e:
        logger.error(f"获取片段详情失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_tender_library_bp.route('/excerpts', methods=['POST'])
@require_auth
def create_excerpt():
    """
    创建片段

    Body:
        tender_doc_id: 标书文档ID
        company_id: 企业ID
        content: 片段内容
        ... 其他可选字段
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': '请提供片段信息'}), 400

        required = ['tender_doc_id', 'company_id', 'content']
        for field in required:
            if field not in data:
                return jsonify({'success': False, 'error': f'缺少必填字段: {field}'}), 400

        manager = get_excerpt_manager()
        excerpt_id = manager.create_excerpt(**data)

        logger.info(f"创建片段成功: ID={excerpt_id}")
        return jsonify({
            'success': True,
            'data': {'excerpt_id': excerpt_id},
            'message': '片段创建成功'
        })

    except Exception as e:
        logger.error(f"创建片段失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_tender_library_bp.route('/excerpts/<int:excerpt_id>', methods=['PUT'])
@require_auth
def update_excerpt(excerpt_id):
    """更新片段"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': '请提供更新信息'}), 400

        manager = get_excerpt_manager()

        # 检查片段是否存在
        existing = manager.get_excerpt(excerpt_id)
        if not existing:
            return jsonify({'success': False, 'error': '片段不存在'}), 404

        success = manager.update_excerpt(excerpt_id, **data)

        if success:
            logger.info(f"更新片段成功: ID={excerpt_id}")
            return jsonify({'success': True, 'message': '片段更新成功'})
        else:
            return jsonify({'success': False, 'error': '更新失败'}), 500

    except Exception as e:
        logger.error(f"更新片段失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_tender_library_bp.route('/excerpts/<int:excerpt_id>', methods=['DELETE'])
@require_auth
def delete_excerpt(excerpt_id):
    """删除片段"""
    try:
        manager = get_excerpt_manager()

        # 检查片段是否存在
        existing = manager.get_excerpt(excerpt_id)
        if not existing:
            return jsonify({'success': False, 'error': '片段不存在'}), 404

        success = manager.delete_excerpt(excerpt_id)

        if success:
            logger.info(f"删除片段成功: ID={excerpt_id}")
            return jsonify({'success': True, 'message': '片段删除成功'})
        else:
            return jsonify({'success': False, 'error': '删除失败'}), 500

    except Exception as e:
        logger.error(f"删除片段失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_tender_library_bp.route('/excerpts/<int:excerpt_id>/highlight', methods=['POST'])
@require_auth
def toggle_highlight(excerpt_id):
    """切换精选状态"""
    try:
        data = request.get_json() or {}
        is_highlighted = data.get('is_highlighted', True)

        manager = get_excerpt_manager()

        # 检查片段是否存在
        existing = manager.get_excerpt(excerpt_id)
        if not existing:
            return jsonify({'success': False, 'error': '片段不存在'}), 404

        success = manager.update_excerpt(excerpt_id, is_highlighted=is_highlighted)

        if success:
            status = "设为精选" if is_highlighted else "取消精选"
            logger.info(f"片段{status}成功: ID={excerpt_id}")
            return jsonify({'success': True, 'message': f'{status}成功'})
        else:
            return jsonify({'success': False, 'error': '操作失败'}), 500

    except Exception as e:
        logger.error(f"切换精选状态失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ===================
# 素材搜索 API
# ===================

@api_tender_library_bp.route('/search/category', methods=['GET'])
def search_by_category():
    """
    按分类搜索片段

    Query params:
        company_id: 企业ID
        category: 分类
        subcategory: 子分类（可选）
        won_only: 只返回中标的（默认true）
        limit: 返回数量（默认10）
    """
    try:
        company_id = request.args.get('company_id', type=int)
        category = request.args.get('category')

        if not company_id or not category:
            return jsonify({'success': False, 'error': '请提供企业ID和分类'}), 400

        subcategory = request.args.get('subcategory')
        won_only = request.args.get('won_only', 'true').lower() == 'true'
        limit = request.args.get('limit', 10, type=int)

        manager = get_excerpt_manager()
        excerpts = manager.search_by_category(
            company_id=company_id,
            category=category,
            subcategory=subcategory,
            won_only=won_only,
            limit=limit
        )

        return jsonify({
            'success': True,
            'data': excerpts,
            'total': len(excerpts)
        })

    except Exception as e:
        logger.error(f"按分类搜索失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_tender_library_bp.route('/search/scoring-point', methods=['GET'])
def search_by_scoring_point():
    """
    按评分点搜索片段

    Query params:
        company_id: 企业ID
        scoring_point: 评分点关键词
        won_only: 只返回中标的（默认true）
        limit: 返回数量（默认10）
    """
    try:
        company_id = request.args.get('company_id', type=int)
        scoring_point = request.args.get('scoring_point')

        if not company_id or not scoring_point:
            return jsonify({'success': False, 'error': '请提供企业ID和评分点'}), 400

        won_only = request.args.get('won_only', 'true').lower() == 'true'
        limit = request.args.get('limit', 10, type=int)

        manager = get_excerpt_manager()
        excerpts = manager.search_by_scoring_point(
            company_id=company_id,
            scoring_point=scoring_point,
            won_only=won_only,
            limit=limit
        )

        return jsonify({
            'success': True,
            'data': excerpts,
            'total': len(excerpts)
        })

    except Exception as e:
        logger.error(f"按评分点搜索失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_tender_library_bp.route('/search/keyword', methods=['GET'])
def search_by_keyword():
    """
    按关键词搜索片段

    Query params:
        company_id: 企业ID
        keyword: 搜索关键词
        won_only: 只返回中标的（默认true）
        limit: 返回数量（默认10）
    """
    try:
        company_id = request.args.get('company_id', type=int)
        keyword = request.args.get('keyword')

        if not company_id or not keyword:
            return jsonify({'success': False, 'error': '请提供企业ID和关键词'}), 400

        won_only = request.args.get('won_only', 'true').lower() == 'true'
        limit = request.args.get('limit', 10, type=int)

        manager = get_excerpt_manager()
        excerpts = manager.search_by_keyword(
            company_id=company_id,
            keyword=keyword,
            won_only=won_only,
            limit=limit
        )

        return jsonify({
            'success': True,
            'data': excerpts,
            'total': len(excerpts)
        })

    except Exception as e:
        logger.error(f"按关键词搜索失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ===================
# 分类管理 API
# ===================

@api_tender_library_bp.route('/categories', methods=['GET'])
def get_categories():
    """获取所有分类"""
    try:
        company_id = request.args.get('company_id', type=int)

        manager = get_excerpt_manager()
        categories = manager.get_categories(company_id)

        return jsonify({
            'success': True,
            'data': categories
        })

    except Exception as e:
        logger.error(f"获取分类失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_tender_library_bp.route('/categories/stats', methods=['GET'])
def get_category_stats():
    """获取分类统计"""
    try:
        company_id = request.args.get('company_id', type=int)
        if not company_id:
            return jsonify({'success': False, 'error': '请提供企业ID'}), 400

        manager = get_excerpt_manager()
        stats = manager.get_category_stats(company_id)

        return jsonify({
            'success': True,
            'data': stats
        })

    except Exception as e:
        logger.error(f"获取分类统计失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_tender_library_bp.route('/most-used', methods=['GET'])
def get_most_used():
    """获取使用最多的片段"""
    try:
        company_id = request.args.get('company_id', type=int)
        if not company_id:
            return jsonify({'success': False, 'error': '请提供企业ID'}), 400

        category = request.args.get('category')
        limit = request.args.get('limit', 10, type=int)

        manager = get_excerpt_manager()
        excerpts = manager.get_most_used(
            company_id=company_id,
            category=category,
            limit=limit
        )

        return jsonify({
            'success': True,
            'data': excerpts
        })

    except Exception as e:
        logger.error(f"获取常用片段失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# 导出蓝图
__all__ = ['api_tender_library_bp']
