#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
案例库API接口
功能：提供REST API接口供前端调用
"""

from flask import Blueprint, request, jsonify, send_file
import json
import os
import asyncio
from typing import Dict, Any
from werkzeug.utils import secure_filename
from datetime import datetime

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from .manager import CaseLibraryManager
from .document_extractor import CaseDocumentExtractor
from common.logger import get_module_logger
from common.config import get_config

logger = get_module_logger("case_library.api")
config = get_config()


class CaseLibraryAPI:
    """案例库API类"""

    def __init__(self):
        self.manager = CaseLibraryManager()
        self.blueprint = Blueprint('case_library', __name__, url_prefix='/api/case_library')
        self._register_routes()

        logger.info("案例库API初始化完成")

    def _register_routes(self):
        """注册API路由"""

        # =========================
        # 案例管理API
        # =========================

        @self.blueprint.route('/cases', methods=['GET'])
        def get_cases():
            """获取案例列表"""
            try:
                company_id = request.args.get('company_id', type=int)

                # 构建筛选条件
                filters = {}
                if request.args.get('product_id'):
                    filters['product_id'] = int(request.args.get('product_id'))
                if request.args.get('industry'):
                    filters['industry'] = request.args.get('industry')
                if request.args.get('contract_type'):
                    filters['contract_type'] = request.args.get('contract_type')
                if request.args.get('case_status'):
                    filters['case_status'] = request.args.get('case_status')

                cases = self.manager.get_cases(company_id, filters)

                return jsonify({
                    'success': True,
                    'data': cases
                })
            except Exception as e:
                logger.error(f"获取案例列表失败: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        @self.blueprint.route('/cases', methods=['POST'])
        def create_case():
            """创建案例"""
            try:
                data = request.get_json()
                logger.info(f"收到创建案例请求，数据: {data}")

                # 验证必需字段
                if not data or not data.get('company_id'):
                    error_msg = '公司ID不能为空'
                    logger.warning(f"创建案例失败: {error_msg}")
                    return jsonify({
                        'success': False,
                        'error': error_msg
                    }), 400

                company_id = data['company_id']
                result = self.manager.create_case(company_id, data)

                if result['success']:
                    logger.info(f"案例创建成功: {result.get('case_id')}")
                    return jsonify(result), 201
                else:
                    logger.warning(f"案例创建失败: {result.get('error')}")
                    return jsonify(result), 400

            except Exception as e:
                logger.error(f"创建案例失败: {e}", exc_info=True)
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        @self.blueprint.route('/cases/<int:case_id>', methods=['GET'])
        def get_case_detail(case_id):
            """获取案例详细信息"""
            try:
                case = self.manager.get_case_detail(case_id)
                if case:
                    return jsonify({
                        'success': True,
                        'data': case
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': '案例不存在'
                    }), 404

            except Exception as e:
                logger.error(f"获取案例详情失败: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        @self.blueprint.route('/cases/<int:case_id>', methods=['PUT'])
        def update_case(case_id):
            """更新案例信息"""
            try:
                data = request.get_json()

                if not data:
                    return jsonify({
                        'success': False,
                        'error': '请求数据不能为空'
                    }), 400

                result = self.manager.update_case(case_id, data)

                if result['success']:
                    return jsonify(result)
                else:
                    return jsonify(result), 400

            except Exception as e:
                logger.error(f"更新案例失败: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        @self.blueprint.route('/cases/<int:case_id>', methods=['DELETE'])
        def delete_case(case_id):
            """删除案例"""
            try:
                result = self.manager.delete_case(case_id)

                if result['success']:
                    return jsonify(result)
                else:
                    return jsonify(result), 400

            except Exception as e:
                logger.error(f"删除案例失败: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        @self.blueprint.route('/search', methods=['GET'])
        def search_cases():
            """搜索案例"""
            try:
                query = request.args.get('q', '')
                company_id = request.args.get('company_id', type=int)

                if not query:
                    return jsonify({
                        'success': False,
                        'error': '搜索关键词不能为空'
                    }), 400

                results = self.manager.search_cases(query, company_id)

                return jsonify({
                    'success': True,
                    'data': results
                })

            except Exception as e:
                logger.error(f"搜索案例失败: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        @self.blueprint.route('/statistics', methods=['GET'])
        def get_statistics():
            """获取统计信息"""
            try:
                company_id = request.args.get('company_id', type=int)
                stats = self.manager.get_statistics(company_id)

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

        # =========================
        # 附件管理API
        # =========================

        @self.blueprint.route('/cases/<int:case_id>/attachments', methods=['POST'])
        def upload_attachment(case_id):
            """上传案例附件"""
            try:
                if 'file' not in request.files:
                    return jsonify({
                        'success': False,
                        'error': '没有选择文件'
                    }), 400

                file = request.files['file']
                if not file.filename:
                    return jsonify({
                        'success': False,
                        'error': '文件名不能为空'
                    }), 400

                attachment_type = request.form.get('attachment_type', 'other')
                description = request.form.get('description', '')

                result = self.manager.upload_attachment(
                    case_id=case_id,
                    file_obj=file,
                    original_filename=file.filename,
                    attachment_type=attachment_type,
                    description=description
                )

                if result['success']:
                    return jsonify(result), 201
                else:
                    return jsonify(result), 400

            except Exception as e:
                logger.error(f"上传附件失败: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        @self.blueprint.route('/cases/<int:case_id>/attachments', methods=['GET'])
        def get_attachments(case_id):
            """获取案例的附件列表"""
            try:
                attachments = self.manager.get_attachments(case_id)

                return jsonify({
                    'success': True,
                    'data': attachments
                })

            except Exception as e:
                logger.error(f"获取附件列表失败: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        @self.blueprint.route('/attachments/<int:attachment_id>', methods=['DELETE'])
        def delete_attachment(attachment_id):
            """删除附件"""
            try:
                result = self.manager.delete_attachment(attachment_id)

                if result['success']:
                    return jsonify(result)
                else:
                    return jsonify(result), 400

            except Exception as e:
                logger.error(f"删除附件失败: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        @self.blueprint.route('/attachments/<int:attachment_id>/download', methods=['GET'])
        def download_attachment(attachment_id):
            """下载附件"""
            try:
                # 获取附件信息
                query = "SELECT * FROM case_attachments WHERE attachment_id = ?"
                attachment = self.manager.db.execute_query(query, (attachment_id,), fetch_one=True)

                if not attachment:
                    return jsonify({
                        'success': False,
                        'error': f'附件 ID {attachment_id} 不存在'
                    }), 404

                # 返回文件
                file_path = attachment['file_path']
                if os.path.exists(file_path):
                    return send_file(
                        file_path,
                        as_attachment=True,
                        download_name=attachment['original_filename']
                    )
                else:
                    return jsonify({
                        'success': False,
                        'error': '文件不存在'
                    }), 404

            except Exception as e:
                logger.error(f"下载附件失败: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        # =========================
        # 文档智能提取API
        # =========================

        @self.blueprint.route('/upload-case-document', methods=['POST'])
        def upload_case_document():
            """上传案例文档"""
            try:
                logger.info("收到案例文档上传请求")

                # 检查文件
                if 'file' not in request.files:
                    return jsonify({
                        'success': False,
                        'error': '没有文件'
                    }), 400

                file = request.files['file']

                if file.filename == '':
                    return jsonify({
                        'success': False,
                        'error': '文件名为空'
                    }), 400

                # 检查文件类型
                allowed_extensions = {'.doc', '.docx', '.pdf'}
                file_ext = os.path.splitext(file.filename)[1].lower()

                if file_ext not in allowed_extensions:
                    return jsonify({
                        'success': False,
                        'error': f'不支持的文件类型: {file_ext}，仅支持 DOC、DOCX、PDF'
                    }), 400

                # 生成安全的文件名
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                safe_filename = secure_filename(file.filename)
                filename = f"case_{timestamp}_{safe_filename}"

                # 确保上传目录存在
                upload_dir = os.path.join(project_root, 'data', 'uploads', 'case_documents')
                os.makedirs(upload_dir, exist_ok=True)

                # 保存文件
                file_path = os.path.join(upload_dir, filename)
                file.save(file_path)

                logger.info(f"文档上传成功: {file_path}")

                return jsonify({
                    'success': True,
                    'message': '文档上传成功',
                    'file_path': file_path,
                    'filename': filename
                })

            except Exception as e:
                logger.error(f"文档上传失败: {e}", exc_info=True)
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        @self.blueprint.route('/extract-from-document', methods=['POST'])
        def extract_from_document():
            """从文档提取案例信息"""
            try:
                logger.info("收到案例信息提取请求")

                data = request.get_json()
                file_path = data.get('file_path')

                if not file_path:
                    return jsonify({
                        'success': False,
                        'error': '缺少文件路径'
                    }), 400

                if not os.path.exists(file_path):
                    return jsonify({
                        'success': False,
                        'error': '文件不存在'
                    }), 404

                # 创建提取器
                extractor = CaseDocumentExtractor()

                # 使用asyncio运行异步提取
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    case_info = loop.run_until_complete(extractor.extract_from_file(file_path))
                finally:
                    loop.close()

                logger.info(f"案例信息提取成功: {case_info.get('case_title', 'Unknown')}")

                return jsonify({
                    'success': True,
                    'message': '案例信息提取成功',
                    'data': case_info
                })

            except ValueError as e:
                logger.warning(f"提取失败(数据问题): {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 400

            except Exception as e:
                logger.error(f"提取案例信息失败: {e}", exc_info=True)
                return jsonify({
                    'success': False,
                    'error': f'提取失败: {str(e)}'
                }), 500

    def get_blueprint(self):
        """获取Flask蓝图"""
        return self.blueprint


# 创建全局API实例
case_library_api = CaseLibraryAPI()
