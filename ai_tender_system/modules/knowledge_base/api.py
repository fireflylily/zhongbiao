#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识库API接口
功能：提供REST API接口供前端调用
"""

from flask import Blueprint, request, jsonify, session
import os
import json
from typing import Dict, Any

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from .manager import KnowledgeBaseManager
from common.logger import get_module_logger

logger = get_module_logger("knowledge_base.api")


class KnowledgeBaseAPI:
    """知识库API类"""

    def __init__(self):
        self.manager = KnowledgeBaseManager()
        self.blueprint = Blueprint('knowledge_base', __name__, url_prefix='/api/knowledge_base')
        self._register_routes()

        logger.info("知识库API初始化完成")

    def _register_routes(self):
        """注册API路由"""

        # =========================
        # 公司管理API
        # =========================

        @self.blueprint.route('/companies', methods=['GET'])
        def get_companies():
            """获取公司列表"""
            try:
                companies = self.manager.get_companies()
                return jsonify({
                    'success': True,
                    'data': companies
                })
            except Exception as e:
                logger.error(f"获取公司列表失败: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        @self.blueprint.route('/companies', methods=['POST'])
        def create_company():
            """创建公司"""
            try:
                data = request.get_json()

                # 验证必需字段
                if not data or not data.get('company_name'):
                    return jsonify({
                        'success': False,
                        'error': '公司名称不能为空'
                    }), 400

                result = self.manager.create_company(
                    company_name=data['company_name'],
                    company_code=data.get('company_code'),
                    industry_type=data.get('industry_type'),
                    description=data.get('description')
                )

                if result['success']:
                    return jsonify(result), 201
                else:
                    return jsonify(result), 400

            except Exception as e:
                logger.error(f"创建公司失败: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        @self.blueprint.route('/companies/<int:company_id>', methods=['GET'])
        def get_company_detail(company_id):
            """获取公司详细信息"""
            try:
                company = self.manager.get_company_detail(company_id)
                if company:
                    return jsonify({
                        'success': True,
                        'data': company
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': '公司不存在'
                    }), 404

            except Exception as e:
                logger.error(f"获取公司详情失败: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        @self.blueprint.route('/companies/<int:company_id>', methods=['PUT'])
        def update_company(company_id):
            """更新公司信息"""
            try:
                data = request.get_json()

                # 验证必需字段
                if not data:
                    return jsonify({
                        'success': False,
                        'error': '请求数据不能为空'
                    }), 400

                # 调用管理器更新公司信息
                result = self.manager.update_company(company_id, data)

                if result['success']:
                    return jsonify(result)
                else:
                    return jsonify(result), 400

            except Exception as e:
                logger.error(f"更新公司信息失败: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        # =========================
        # 产品管理API
        # =========================

        @self.blueprint.route('/companies/<int:company_id>/products', methods=['GET'])
        def get_products(company_id):
            """获取公司的产品列表"""
            try:
                products = self.manager.get_products(company_id)
                return jsonify({
                    'success': True,
                    'data': products
                })
            except Exception as e:
                logger.error(f"获取产品列表失败: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        @self.blueprint.route('/companies/<int:company_id>/products', methods=['POST'])
        def create_product(company_id):
            """创建产品"""
            try:
                data = request.get_json()

                # 验证必需字段
                if not data or not data.get('product_name'):
                    return jsonify({
                        'success': False,
                        'error': '产品名称不能为空'
                    }), 400

                result = self.manager.create_product(
                    company_id=company_id,
                    product_name=data['product_name'],
                    product_code=data.get('product_code'),
                    product_category=data.get('product_category'),
                    description=data.get('description')
                )

                if result['success']:
                    return jsonify(result), 201
                else:
                    return jsonify(result), 400

            except Exception as e:
                logger.error(f"创建产品失败: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        @self.blueprint.route('/products/<int:product_id>', methods=['GET'])
        def get_product_detail(product_id):
            """获取产品详细信息"""
            try:
                product = self.manager.get_product_detail(product_id)
                if product:
                    return jsonify({
                        'success': True,
                        'data': product
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': '产品不存在'
                    }), 404

            except Exception as e:
                logger.error(f"获取产品详情失败: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        # =========================
        # 文档库管理API
        # =========================

        @self.blueprint.route('/libraries', methods=['POST'])
        def create_document_library():
            """创建文档库"""
            try:
                data = request.get_json()

                # 验证必需字段
                required_fields = ['owner_type', 'owner_id', 'library_name', 'library_type']
                for field in required_fields:
                    if not data or not data.get(field):
                        return jsonify({
                            'success': False,
                            'error': f'{field} 不能为空'
                        }), 400

                result = self.manager.create_document_library(
                    owner_type=data['owner_type'],
                    owner_id=data['owner_id'],
                    library_name=data['library_name'],
                    library_type=data['library_type'],
                    privacy_level=data.get('privacy_level', 1),
                    is_shared=data.get('is_shared', False),
                    share_scope=data.get('share_scope'),
                    share_products=data.get('share_products')
                )

                if result['success']:
                    return jsonify(result), 201
                else:
                    return jsonify(result), 400

            except Exception as e:
                logger.error(f"创建文档库失败: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        @self.blueprint.route('/<owner_type>/<int:owner_id>/libraries', methods=['GET'])
        def get_document_libraries(owner_type, owner_id):
            """获取文档库列表"""
            try:
                libraries = self.manager.get_document_libraries(owner_type, owner_id)
                return jsonify({
                    'success': True,
                    'data': libraries
                })
            except Exception as e:
                logger.error(f"获取文档库列表失败: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        @self.blueprint.route('/libraries/<int:library_id>', methods=['GET'])
        def get_library(library_id):
            """获取单个文档库详情"""
            try:
                library = self.manager.get_library_by_id(library_id)
                if library:
                    return jsonify({
                        'success': True,
                        'data': library
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': '文档库不存在'
                    }), 404
            except Exception as e:
                logger.error(f"获取文档库详情失败: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        # =========================
        # 文档管理API
        # =========================

        @self.blueprint.route('/libraries/<int:library_id>/documents', methods=['POST'])
        def upload_document(library_id):
            """上传文档到文档库 - 简化版（统一服务已处理验证）"""
            try:
                # 基本检查
                if 'file' not in request.files:
                    return jsonify({'success': False, 'error': '没有选择文件'}), 400

                file = request.files['file']
                if not file.filename:
                    return jsonify({'success': False, 'error': '文件名不能为空'}), 400

                # 获取参数
                privacy_classification = int(request.form.get('privacy_classification', 1))
                tags = json.loads(request.form.get('tags', '[]')) if request.form.get('tags') else []
                metadata = json.loads(request.form.get('metadata', '{}')) if request.form.get('metadata') else {}

                # 调用manager上传（已集成统一存储服务）
                result = self.manager.upload_document(
                    library_id=library_id,
                    file_obj=file,
                    original_filename=file.filename,  # 保留原始文件名
                    privacy_classification=privacy_classification,
                    tags=tags,
                    metadata=metadata
                )

                return jsonify(result), 201 if result['success'] else 400

            except Exception as e:
                logger.error(f"文档上传失败: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500

        @self.blueprint.route('/libraries/<int:library_id>/documents', methods=['GET'])
        def get_documents(library_id):
            """获取文档库的文档列表"""
            try:
                privacy_level = request.args.get('privacy_level', type=int)
                documents = self.manager.get_documents(library_id, privacy_level)

                return jsonify({
                    'success': True,
                    'data': documents
                })
            except Exception as e:
                logger.error(f"获取文档列表失败: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        @self.blueprint.route('/documents/<int:doc_id>/status', methods=['PUT'])
        def update_document_status(doc_id):
            """更新文档处理状态"""
            try:
                data = request.get_json()
                if not data:
                    return jsonify({
                        'success': False,
                        'error': '请求数据不能为空'
                    }), 400

                parse_status = data.get('parse_status')
                vector_status = data.get('vector_status')

                if not parse_status and not vector_status:
                    return jsonify({
                        'success': False,
                        'error': '至少需要提供一个状态字段'
                    }), 400

                result = self.manager.update_document_status(doc_id, parse_status, vector_status)

                if result:
                    return jsonify({
                        'success': True,
                        'message': '文档状态更新成功'
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': '更新文档状态失败'
                    }), 400

            except Exception as e:
                logger.error(f"更新文档状态失败: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        @self.blueprint.route('/documents/<int:doc_id>', methods=['GET'])
        def get_document(doc_id):
            """获取单个文档详细信息"""
            try:
                document = self.manager.get_document_by_id(doc_id)
                if document:
                    return jsonify({
                        'success': True,
                        'data': document
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': '文档不存在'
                    }), 404
            except Exception as e:
                logger.error(f"获取文档详情失败: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        @self.blueprint.route('/documents/<int:doc_id>/preview', methods=['GET'])
        def preview_document(doc_id):
            """预览文档内容（转换为HTML）"""
            try:
                from pathlib import Path
                import html

                # 获取文档信息
                document = self.manager.get_document_by_id(doc_id)
                if not document:
                    return jsonify({
                        'success': False,
                        'error': '文档不存在'
                    }), 404

                file_path = Path(document['file_path'])
                if not file_path.exists():
                    return jsonify({
                        'success': False,
                        'error': '文件不存在'
                    }), 404

                file_extension = file_path.suffix.lower()

                # Word文档预览
                if file_extension in ['.docx', '.doc']:
                    try:
                        from docx import Document
                        from docx.oxml.text.paragraph import CT_P
                        from docx.oxml.table import CT_Tbl
                        from docx.table import _Cell, Table
                        from docx.text.paragraph import Paragraph

                        doc = Document(file_path)
                        html_content = ['<div class="document-preview">']

                        # 按文档原始顺序遍历所有元素（段落和表格）
                        def is_heading(paragraph):
                            """判断段落是否为标题"""
                            if not paragraph.text.strip():
                                return None

                            style_name = paragraph.style.name if paragraph.style else ''

                            # 方法1: 通过样式名判断
                            if 'Heading 1' in style_name or 'heading 1' in style_name.lower() or '标题 1' in style_name:
                                return 1
                            elif 'Heading 2' in style_name or 'heading 2' in style_name.lower() or '标题 2' in style_name:
                                return 2
                            elif 'Heading 3' in style_name or 'heading 3' in style_name.lower() or '标题 3' in style_name:
                                return 3

                            # 方法2: 通过字体大小和加粗判断（适用于手动格式化的标题）
                            try:
                                runs = paragraph.runs
                                if runs:
                                    first_run = runs[0]
                                    if first_run.bold and first_run.font.size:
                                        size_pt = first_run.font.size.pt
                                        if size_pt >= 16:
                                            return 1
                                        elif size_pt >= 14:
                                            return 2
                                        elif size_pt >= 12:
                                            return 3
                            except:
                                pass

                            return None

                        # 遍历文档的body元素，保持原始顺序
                        for element in doc.element.body:
                            # 处理段落
                            if isinstance(element, CT_P):
                                paragraph = Paragraph(element, doc)
                                if paragraph.text.strip():
                                    heading_level = is_heading(paragraph)
                                    text = html.escape(paragraph.text)

                                    if heading_level == 1:
                                        html_content.append(f'<h1>{text}</h1>')
                                    elif heading_level == 2:
                                        html_content.append(f'<h2>{text}</h2>')
                                    elif heading_level == 3:
                                        html_content.append(f'<h3>{text}</h3>')
                                    else:
                                        html_content.append(f'<p>{text}</p>')

                            # 处理表格
                            elif isinstance(element, CT_Tbl):
                                table = Table(element, doc)
                                html_content.append('<table class="table table-bordered table-striped">')
                                for i, row in enumerate(table.rows):
                                    # 第一行作为表头
                                    tag = 'th' if i == 0 else 'td'
                                    html_content.append('<tr>')
                                    for cell in row.cells:
                                        cell_text = html.escape(cell.text)
                                        html_content.append(f'<{tag}>{cell_text}</{tag}>')
                                    html_content.append('</tr>')
                                html_content.append('</table>')

                        html_content.append('</div>')

                        # 添加CSS样式
                        css_styles = """
                        <style>
                            .document-preview {
                                font-family: 'Microsoft YaHei', 'Segoe UI', sans-serif;
                                line-height: 1.8;
                                padding: 20px;
                            }
                            .table {
                                margin: 20px 0;
                                width: 100%;
                                border-collapse: collapse;
                            }
                            .table th {
                                background-color: #f8f9fa;
                                font-weight: bold;
                                padding: 12px;
                                text-align: left;
                            }
                            .table td {
                                padding: 10px;
                            }
                            h1 {
                                color: #333;
                                font-size: 2rem;
                                margin: 30px 0 15px;
                                font-weight: bold;
                                border-bottom: 2px solid #007bff;
                                padding-bottom: 10px;
                            }
                            h2 {
                                color: #555;
                                font-size: 1.5rem;
                                margin: 25px 0 12px;
                                font-weight: bold;
                                border-bottom: 1px solid #ddd;
                                padding-bottom: 8px;
                            }
                            h3 {
                                color: #666;
                                font-size: 1.25rem;
                                margin: 20px 0 10px;
                                font-weight: bold;
                            }
                            p {
                                margin: 12px 0;
                                text-align: justify;
                                color: #333;
                            }
                        </style>
                        """

                        full_content = css_styles + ''.join(html_content)

                        return jsonify({
                            'success': True,
                            'content': full_content,
                            'filename': document['original_filename']
                        })

                    except Exception as e:
                        logger.error(f"Word文档预览失败: {e}")
                        return jsonify({
                            'success': False,
                            'error': f'Word文档预览失败: {str(e)}'
                        }), 500

                # PDF文档预览
                elif file_extension == '.pdf':
                    try:
                        import PyPDF2

                        with open(file_path, 'rb') as pdf_file:
                            pdf_reader = PyPDF2.PdfReader(pdf_file)
                            text_content = []
                            for page in pdf_reader.pages:
                                text_content.append(page.extract_text())

                        html_content = '<div class="document-preview"><pre style="white-space: pre-wrap; font-family: inherit;">'
                        html_content += html.escape('\n\n'.join(text_content))
                        html_content += '</pre></div>'

                        return jsonify({
                            'success': True,
                            'content': html_content,
                            'filename': document['original_filename']
                        })

                    except Exception as e:
                        logger.error(f"PDF文档预览失败: {e}")
                        return jsonify({
                            'success': False,
                            'error': f'PDF文档预览失败: {str(e)}'
                        }), 500

                # 文本文件预览
                elif file_extension in ['.txt', '.md', '.json', '.xml', '.csv']:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            text_content = f.read()

                        html_content = '<div class="document-preview"><pre style="white-space: pre-wrap; font-family: monospace;">'
                        html_content += html.escape(text_content)
                        html_content += '</pre></div>'

                        return jsonify({
                            'success': True,
                            'content': html_content,
                            'filename': document['original_filename']
                        })

                    except Exception as e:
                        logger.error(f"文本文件预览失败: {e}")
                        return jsonify({
                            'success': False,
                            'error': f'文本文件预览失败: {str(e)}'
                        }), 500

                else:
                    return jsonify({
                        'success': False,
                        'error': f'不支持预览此文件类型: {file_extension}'
                    }), 400

            except Exception as e:
                logger.error(f"文档预览失败: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        @self.blueprint.route('/documents/<int:doc_id>', methods=['DELETE'])
        def delete_document(doc_id):
            """删除文档"""
            try:
                result = self.manager.delete_document(doc_id)

                if result['success']:
                    return jsonify(result)
                else:
                    return jsonify(result), 400

            except Exception as e:
                logger.error(f"删除文档失败: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        # =========================
        # 统计和仪表板API
        # =========================

        @self.blueprint.route('/dashboard/stats', methods=['GET'])
        def get_dashboard_stats():
            """获取仪表板统计信息"""
            try:
                company_id = request.args.get('company_id', type=int)
                stats = self.manager.get_dashboard_stats(company_id)

                return jsonify({
                    'success': True,
                    'data': stats
                })
            except Exception as e:
                logger.error(f"获取统计信息失败: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        @self.blueprint.route('/statistics', methods=['GET'])
        def get_statistics():
            """获取知识库整体统计数据"""
            try:
                stats = self.manager.get_knowledge_base_statistics()
                return jsonify({
                    'success': True,
                    'data': stats
                })
            except Exception as e:
                logger.error(f"获取统计数据失败: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        @self.blueprint.route('/search', methods=['POST'])
        def search_documents():
            """智能文档搜索"""
            try:
                data = request.get_json()
                if not data or not data.get('query'):
                    return jsonify({
                        'success': False,
                        'error': '搜索查询不能为空'
                    }), 400

                query = data['query']
                category = data.get('category')
                privacy_level = data.get('privacy_level', 1)

                results = self.manager.search_documents(
                    query=query,
                    category=category,
                    privacy_level=int(privacy_level)
                )

                return jsonify({
                    'success': True,
                    'data': results
                })

            except Exception as e:
                logger.error(f"文档搜索失败: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        # =========================
        # 权限验证API
        # =========================

        @self.blueprint.route('/documents/<int:doc_id>/access', methods=['POST'])
        def check_document_access(doc_id):
            """检查文档访问权限并记录日志"""
            try:
                data = request.get_json()
                user_role = data.get('user_role', 'guest')
                doc_privacy_level = data.get('doc_privacy_level', 1)
                action_type = data.get('action_type', 'view')

                # 检查访问权限
                access_granted = self.manager.check_document_access(user_role, doc_privacy_level)

                # 记录访问日志
                log_id = self.manager.log_document_access(
                    user_id=data.get('user_id', 'anonymous'),
                    user_role=user_role,
                    action_type=action_type,
                    doc_id=doc_id,
                    privacy_level=doc_privacy_level,
                    access_granted=access_granted,
                    access_reason=data.get('access_reason'),
                    ip_address=request.remote_addr,
                    user_agent=request.headers.get('User-Agent'),
                    session_id=session.get('session_id')
                )

                return jsonify({
                    'success': True,
                    'access_granted': access_granted,
                    'log_id': log_id
                })

            except Exception as e:
                logger.error(f"检查文档访问权限失败: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

    def get_blueprint(self):
        """获取Flask蓝图"""
        return self.blueprint


# 创建全局API实例
knowledge_base_api = KnowledgeBaseAPI()