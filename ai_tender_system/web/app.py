#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI标书系统统一Web应用
整合招标信息提取、点对点应答、技术方案生成等所有功能
"""

import os
import sys
import tempfile
import hashlib
import time
import re
import urllib.parse
from datetime import datetime
from pathlib import Path
from functools import wraps
from flask import Flask, request, jsonify, render_template, send_file, send_from_directory, session, redirect, url_for
from flask_cors import CORS
from flask_compress import Compress
from flask_wtf.csrf import CSRFProtect, generate_csrf
from werkzeug.utils import secure_filename

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 导入公共组件
from common import (
    get_config, setup_logging, get_module_logger,
    AITenderSystemError, format_error_response, handle_api_error,
    safe_filename, allowed_file, ensure_dir
)
# 导入常量
from common.constants import (
    CACHE_MAX_AGE_STATIC, DEFAULT_PAGE_SIZE,
    PROGRESS_COMPLETE, PROGRESS_HALF_COMPLETE, PROGRESS_NOT_STARTED,
    TASK_START_MAX_RETRIES, TASK_START_RETRY_INTERVAL,
    STEP_EXECUTION_MAX_RETRIES, STEP_EXECUTION_RETRY_INTERVAL,
    STEP_3, HTTP_BAD_REQUEST, HTTP_NOT_FOUND, HTTP_INTERNAL_SERVER_ERROR
)

# 导入业务模块
try:
    from modules.tender_info.extractor import TenderInfoExtractor
    TENDER_INFO_AVAILABLE = True
except ImportError as e:
    print(f"招标信息提取模块加载失败: {e}")
    TENDER_INFO_AVAILABLE = False

# 商务应答模块（原点对点应答）
try:
    from modules.business_response.processor import BusinessResponseProcessor, PointToPointProcessor
    BUSINESS_RESPONSE_AVAILABLE = True
    POINT_TO_POINT_AVAILABLE = True  # 保持向后兼容
except ImportError as e:
    print(f"商务应答模块加载失败: {e}")
    BUSINESS_RESPONSE_AVAILABLE = False
    POINT_TO_POINT_AVAILABLE = False

# 技术需求回复模块
try:
    from modules.point_to_point.tech_responder import TechResponder
    TECH_RESPONDER_AVAILABLE = True
except ImportError as e:
    print(f"技术需求回复模块加载失败: {e}")
    TECH_RESPONDER_AVAILABLE = False

def create_app() -> Flask:
    """创建Flask应用"""
    # 初始化配置和日志
    config = get_config()
    setup_logging()
    logger = get_module_logger("web_app")
    
    # 创建Flask应用
    app = Flask(__name__, 
                template_folder=str(config.get_path('templates')),
                static_folder=str(config.get_path('static')))
    
    # 配置应用
    web_config = config.get_web_config()
    app.config.update({
        'SECRET_KEY': web_config['secret_key'],
        'MAX_CONTENT_LENGTH': config.get_upload_config()['max_file_size'],
        # CSRF豁免列表 - 登录页面不需要CSRF token
        'WTF_CSRF_EXEMPT_LIST': ['auth.login']
    })

    # 开发模式下禁用静态文件缓存
    if app.debug:
        app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
        logger.info("开发模式：已禁用静态文件缓存")

    # 启用CORS
    CORS(app, supports_credentials=True)

    # ⚡ 性能优化: 启用Gzip/Brotli压缩
    compress = Compress()
    compress.init_app(app)
    logger.info("已启用响应压缩(Gzip/Brotli)")

    # 启用CSRF保护
    csrf = CSRFProtect(app)
    logger.info("CSRF保护已启用，登录页面已豁免")

    # 提供CSRF token的API端点
    @app.route('/api/csrf-token', methods=['GET'])
    def get_csrf_token():
        """获取CSRF token（用于AJAX请求）"""
        token = generate_csrf()
        return jsonify({'csrf_token': token})

    # 注册知识库API蓝图
    try:
        from modules.knowledge_base.api import knowledge_base_api
        app.register_blueprint(knowledge_base_api.get_blueprint())
        logger.info("知识库API模块注册成功")
    except ImportError as e:
        logger.warning(f"知识库API模块加载失败: {e}")

    # 注册向量搜索API蓝图
    try:
        from modules.vector_search_api import vector_search_api
        app.register_blueprint(vector_search_api.get_blueprint())
        logger.info("向量搜索API模块注册成功")
    except ImportError as e:
        logger.warning(f"向量搜索API模块加载失败: {e}")

    # 注册RAG知识库API蓝图
    try:
        from modules.knowledge_base.rag_api import rag_api
        app.register_blueprint(rag_api, url_prefix='/api')
        logger.info("RAG知识库API模块注册成功")
    except ImportError as e:
        logger.warning(f"RAG知识库API模块加载失败: {e}")

    # 注册技术方案大纲生成API蓝图
    try:
        from web.api_outline_generator import api_outline_bp
        app.register_blueprint(api_outline_bp)
        logger.info("技术方案大纲生成API模块注册成功")
    except ImportError as e:
        logger.warning(f"技术方案大纲生成API模块加载失败: {e}")

    # 注册案例库API蓝图
    try:
        from modules.case_library.api import case_library_api
        app.register_blueprint(case_library_api.get_blueprint())
        logger.info("案例库API模块注册成功")
    except ImportError as e:
        logger.warning(f"案例库API模块加载失败: {e}")

    # 注册内部蓝图（新架构）
    from web.blueprints import register_all_blueprints
    register_all_blueprints(app, config, logger)

    # ⚡ 性能优化: 添加静态资源缓存头
    @app.after_request
    def add_performance_headers(response):
        """添加性能优化相关的HTTP头"""
        # 静态资源长期缓存 (1年)
        if request.path.startswith('/static/'):
            # 缓存静态资源1年
            response.cache_control.max_age = CACHE_MAX_AGE_STATIC
            response.cache_control.public = True
            response.cache_control.immutable = True

            # 添加ETag支持
            response.add_etag()

        # HTML页面短期缓存或无缓存
        elif request.path.endswith('.html') or request.path == '/':
            response.cache_control.no_cache = True
            response.cache_control.no_store = True
            response.cache_control.must_revalidate = True

        # API响应不缓存
        elif request.path.startswith('/api/'):
            response.cache_control.no_cache = True
            response.cache_control.private = True

        # 🔒 安全增强: 添加安全响应头
        # XSS 防护
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'

        # HSTS - 强制HTTPS (生产环境开启)
        if not app.debug:
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'

        # CSP - 内容安全策略 (根据实际需求调整)
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.tiny.cloud https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "font-src 'self' data:; "
            "img-src 'self' data: https:; "
            "connect-src 'self' https://maas-gz.ai-yuanjing.com https://maas.ai-yuanjing.com; "
            "frame-ancestors 'self';"
        )
        response.headers['Content-Security-Policy'] = csp

        # COOP - 跨源打开器策略
        response.headers['Cross-Origin-Opener-Policy'] = 'same-origin'

        # Referrer Policy
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'

        return response

    logger.info("已配置静态资源缓存策略")

    # 注册路由（旧架构 - 将逐步迁移）
    register_routes(app, config, logger)

    logger.info("AI标书系统Web应用初始化完成")
    return app

def register_routes(app: Flask, config, logger):
    """注册所有路由"""

    # 使用共享的知识库管理器单例
    from web.shared.instances import get_kb_manager
    kb_manager = get_kb_manager()

    # ===================
    # 辅助函数 - 已迁移的函数
    # login_required -> middleware/auth.py
    # enrich_qualification_with_company_status -> blueprints/api_tender_bp.py
    # ===================

    # ===================
    # 已迁移到蓝图的路由 (Phase 1 + Phase 2)
    # ===================
    # Phase 1: 认证和静态页面 -> blueprints/auth_bp.py, pages_bp.py, static_files_bp.py
    # Phase 2: 核心API -> blueprints/api_core_bp.py (/api/health, /api/config)
    # Phase 2: 文件管理 -> blueprints/api_files_bp.py (/upload, /download/<filename>)
    # Phase 2: 招标信息 -> blueprints/api_tender_bp.py (/extract-tender-info, /extract-tender-info-step)
    # ===================
    
    # ===================
    # 已迁移到蓝图的路由 (Phase 3: 业务API)
    # ===================
    # Phase 3a: 商务应答和点对点 -> blueprints/api_business_bp.py (9个路由)
    # Phase 3b: 技术需求 -> blueprints/api_tech_bp.py (1个路由)
    # Phase 3c: 公司管理 -> blueprints/api_companies_bp.py (10个路由)
    # Phase 3d: 招标项目管理 -> blueprints/api_projects_bp.py (4个路由)
    # Phase 3e: 文档编辑器和表格 -> blueprints/api_editor_bp.py (5个路由)
    #
    # 辅助函数:
    # - build_image_config_from_db() -> api_business_bp.py
    # - generate_output_filename() -> api_business_bp.py, api_tech_bp.py
    # ===================


    @app.route('/api/project-config')
    def get_project_config():
        """获取项目配置信息"""
        try:
            import configparser
            
            # 读取招标信息提取模块生成的配置文件
            config_file = config.get_path('config') / 'tender_config.ini'
            
            if not config_file.exists():
                return jsonify({'success': False, 'error': '项目配置文件不存在'})
                
            ini_config = configparser.ConfigParser(interpolation=None)
            ini_config.read(config_file, encoding='utf-8')
            
            # 提取项目信息
            project_info = {}
            if ini_config.has_section('PROJECT_INFO'):
                project_info = {
                    'projectName': ini_config.get('PROJECT_INFO', 'project_name', fallback=''),
                    'projectNumber': ini_config.get('PROJECT_INFO', 'project_number', fallback=''),
                    'tenderer': ini_config.get('PROJECT_INFO', 'tenderer', fallback=''),
                    'agency': ini_config.get('PROJECT_INFO', 'agency', fallback=''),
                    'biddingMethod': ini_config.get('PROJECT_INFO', 'bidding_method', fallback=''),
                    'biddingLocation': ini_config.get('PROJECT_INFO', 'bidding_location', fallback=''),
                    'biddingTime': ini_config.get('PROJECT_INFO', 'bidding_time', fallback=''),
                }
            
            return jsonify({'success': True, 'projectInfo': project_info})
            
        except Exception as e:
            logger.error(f"获取项目配置失败: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    # ===================
    # 模型管理API - 已迁移到 blueprints/api_models_bp.py
    # ===================

    # ===================
    # 标书智能处理API
    # ===================

    @app.route('/api/tender-processing/start', methods=['POST'])
    def start_tender_processing():
        """启动标书智能处理流程"""
        try:
            # 获取表单数据
            project_id = request.form.get('project_id')
            filter_model = request.form.get('filter_model', 'gpt-4o-mini')
            extract_model = request.form.get('extract_model', 'yuanjing-deepseek-v3')
            step = int(request.form.get('step', 1))  # 默认只执行第1步（分块）

            if not project_id:
                return jsonify({'success': False, 'error': '缺少project_id参数'}), 400

            # 检查文件上传
            if 'file' not in request.files:
                return jsonify({'success': False, 'error': '未上传文件'}), 400

            file = request.files['file']
            if not file.filename:
                return jsonify({'success': False, 'error': '文件名为空'}), 400

            # 保存文件到临时目录
            import os
            import tempfile
            from pathlib import Path

            temp_dir = Path(tempfile.gettempdir()) / 'tender_processing'
            temp_dir.mkdir(exist_ok=True)

            file_ext = Path(file.filename).suffix
            temp_file = temp_dir / f"tender_{project_id}{file_ext}"
            file.save(str(temp_file))

            logger.info(f"文件已保存: {temp_file}")

            # 使用ParserManager解析文档
            import asyncio
            from modules.document_parser.parser_manager import ParserManager

            async def parse_document():
                parser = ParserManager()
                result = await parser.parse_document(doc_id=int(project_id), file_path=str(temp_file))
                return result

            # 运行异步解析
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            parse_result = loop.run_until_complete(parse_document())
            loop.close()

            if parse_result.status.value != 'completed':
                return jsonify({
                    'success': False,
                    'error': f'文档解析失败: {parse_result.error_message}'
                }), 500

            document_text = parse_result.content
            logger.info(f"启动标书智能处理 - 项目ID: {project_id}, 文档长度: {len(document_text)}")

            # 导入处理流程
            from modules.tender_processing.processing_pipeline import TenderProcessingPipeline

            # 创建流程实例（异步处理需要在后台线程中运行）
            import threading

            result_holder = {'task_id': None, 'error': None}

            def run_pipeline():
                try:
                    from web.shared.instances import set_pipeline_instance

                    pipeline = TenderProcessingPipeline(
                        project_id=project_id,
                        document_text=document_text,
                        filter_model=filter_model,
                        extract_model=extract_model
                    )
                    result_holder['task_id'] = pipeline.task_id

                    # 保存pipeline实例到全局存储（线程安全）
                    set_pipeline_instance(pipeline.task_id, pipeline)

                    # 运行指定步骤
                    result = pipeline.run_step(step)
                    result_holder['result'] = result

                    logger.info(f"步骤 {step} 处理完成 - 任务ID: {pipeline.task_id}, 成功: {result['success']}")
                except Exception as e:
                    logger.error(f"处理流程执行失败: {e}")
                    result_holder['error'] = str(e)

            # 启动后台线程
            thread = threading.Thread(target=run_pipeline, daemon=True)
            thread.start()

            # 等待task_id生成
            import time
            for _ in range(TASK_START_MAX_RETRIES):
                if result_holder['task_id'] or result_holder['error']:
                    break
                time.sleep(TASK_START_RETRY_INTERVAL)

            if result_holder['error']:
                return jsonify({'success': False, 'error': result_holder['error']}), 500

            if not result_holder['task_id']:
                return jsonify({'success': False, 'error': '任务启动超时'}), 500

            return jsonify({
                'success': True,
                'task_id': result_holder['task_id'],
                'message': '处理任务已启动，请使用task_id查询进度'
            })

        except Exception as e:
            logger.error(f"启动标书处理失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/tender-processing/continue/<task_id>', methods=['POST'])
    def continue_tender_processing(task_id):
        """继续执行下一步骤"""
        try:
            from web.shared.instances import get_pipeline_instance, remove_pipeline_instance

            # 获取参数
            data = request.get_json()
            step = data.get('step', 2)  # 默认执行第2步

            # 从全局存储中获取pipeline实例（线程安全）
            pipeline = get_pipeline_instance(task_id)
            if pipeline is None:
                return jsonify({'success': False, 'error': f'找不到任务 {task_id} 的pipeline实例或已过期'}), 404

            # 在后台线程中执行步骤
            import threading

            result_holder = {'result': None, 'error': None}

            def run_step():
                try:
                    result = pipeline.run_step(step)
                    result_holder['result'] = result
                    logger.info(f"步骤 {step} 处理完成 - 任务ID: {task_id}, 成功: {result['success']}")
                except Exception as e:
                    logger.error(f"步骤 {step} 执行失败: {e}")
                    result_holder['error'] = str(e)

            # 启动后台线程
            thread = threading.Thread(target=run_step, daemon=True)
            thread.start()

            # 等待步骤完成
            import time
            for _ in range(STEP_EXECUTION_MAX_RETRIES):
                if result_holder['result'] or result_holder['error']:
                    break
                time.sleep(STEP_EXECUTION_RETRY_INTERVAL)

            if result_holder['error']:
                return jsonify({'success': False, 'error': result_holder['error']}), 500

            if not result_holder['result']:
                # 步骤仍在执行中，返回处理中状态
                return jsonify({
                    'success': True,
                    'task_id': task_id,
                    'message': f'步骤 {step} 正在处理中，请查询状态'
                })

            # 如果是最后一步，清理pipeline实例（线程安全）
            if step == STEP_3:
                remove_pipeline_instance(task_id)
                logger.info(f"任务 {task_id} 已完成，清理pipeline实例")

            return jsonify({
                'success': True,
                'task_id': task_id,
                'result': result_holder['result'],
                'message': f'步骤 {step} 处理完成'
            })

        except Exception as e:
            logger.error(f"继续处理失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/tender-processing/status/<task_id>', methods=['GET'])
    def get_processing_status(task_id):
        """查询处理进度"""
        try:
            from common.database import get_knowledge_base_db

            db = get_knowledge_base_db()

            # 获取任务信息
            task = db.get_processing_task(task_id)

            if not task:
                return jsonify({'success': False, 'error': '任务不存在'}), 404

            # 获取处理日志
            logs = db.get_processing_logs(task_id=task_id)

            # 获取统计信息
            stats = db.get_processing_statistics(task_id)

            return jsonify({
                'success': True,
                'task': dict(task),
                'logs': [dict(log) for log in logs],
                'statistics': dict(stats) if stats else None
            })

        except Exception as e:
            logger.error(f"查询处理状态失败: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/tender-processing/chunks/<int:project_id>', methods=['GET'])
    def get_tender_chunks(project_id):
        """获取文档分块列表"""
        try:
            from common.database import get_knowledge_base_db

            valuable_only = request.args.get('valuable_only', 'false').lower() == 'true'

            db = get_knowledge_base_db()
            chunks = db.get_tender_chunks(project_id, valuable_only=valuable_only)

            # 解析metadata JSON
            for chunk in chunks:
                if chunk.get('metadata'):
                    try:
                        chunk['metadata'] = json.loads(chunk['metadata'])
                    except (json.JSONDecodeError, TypeError) as e:
                        logger.warning(f"解析chunk metadata失败: {e}")
                        chunk['metadata'] = {}

            return jsonify({
                'success': True,
                'chunks': chunks,
                'total': len(chunks)
            })

        except Exception as e:
            logger.error(f"获取分块列表失败: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/tender-processing/requirements/<int:project_id>', methods=['GET'])
    def get_tender_requirements(project_id):
        """获取提取的要求列表"""
        try:
            from common.database import get_knowledge_base_db

            constraint_type = request.args.get('constraint_type')
            category = request.args.get('category')

            db = get_knowledge_base_db()
            requirements = db.get_tender_requirements(
                project_id=project_id,
                constraint_type=constraint_type,
                category=category
            )

            # 获取汇总统计
            summary = db.get_requirements_summary(project_id)

            return jsonify({
                'success': True,
                'requirements': requirements,
                'total': len(requirements),
                'summary': summary,
                'has_extracted': len(requirements) > 0
            })

        except Exception as e:
            logger.error(f"获取要求列表失败: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/tender-processing/analytics/<int:project_id>', methods=['GET'])
    def get_processing_analytics(project_id):
        """获取处理统计分析"""
        try:
            from common.database import get_knowledge_base_db

            db = get_knowledge_base_db()

            # 获取分块统计
            all_chunks = db.get_tender_chunks(project_id)
            valuable_chunks = db.get_tender_chunks(project_id, valuable_only=True)

            # 获取要求统计
            requirements = db.get_tender_requirements(project_id)
            summary = db.get_requirements_summary(project_id)

            # 计算分块类型分布
            chunk_type_dist = {}
            for chunk in all_chunks:
                chunk_type = chunk.get('chunk_type', 'unknown')
                chunk_type_dist[chunk_type] = chunk_type_dist.get(chunk_type, 0) + 1

            # 计算筛选效果
            filter_rate = (len(all_chunks) - len(valuable_chunks)) / len(all_chunks) * 100 if all_chunks else 0

            analytics = {
                'chunks': {
                    'total': len(all_chunks),
                    'valuable': len(valuable_chunks),
                    'filtered': len(all_chunks) - len(valuable_chunks),
                    'filter_rate': round(filter_rate, 2),
                    'type_distribution': chunk_type_dist
                },
                'requirements': {
                    'total': len(requirements),
                    'by_type': summary.get('by_type', {}),
                    'by_category': summary.get('by_category', {})
                }
            }

            return jsonify({
                'success': True,
                'analytics': analytics
            })

        except Exception as e:
            logger.error(f"获取处理统计失败: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/tender-processing/export/<int:project_id>', methods=['GET'])
    def export_requirements(project_id):
        """导出提取的要求为Excel"""
        try:
            from common.database import get_knowledge_base_db
            import pandas as pd
            from io import BytesIO

            db = get_knowledge_base_db()
            requirements = db.get_tender_requirements(project_id)

            if not requirements:
                return jsonify({'success': False, 'error': '没有可导出的数据'}), 404

            # 转换为DataFrame
            df = pd.DataFrame(requirements)

            # 选择需要的列
            columns = [
                'requirement_id', 'constraint_type', 'category', 'subcategory',
                'detail', 'source_location', 'priority', 'extraction_confidence',
                'is_verified', 'extracted_at'
            ]
            df = df[[col for col in columns if col in df.columns]]

            # 重命名列（中文）
            df.columns = [
                '要求ID', '类型', '分类', '子分类', '详情', '来源',
                '优先级', '置信度', '已验证', '提取时间'
            ][:len(df.columns)]

            # 生成Excel
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='投标要求', index=False)
            output.seek(0)

            return send_file(
                output,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name=f'项目{project_id}_投标要求.xlsx'
            )

        except ImportError:
            return jsonify({
                'success': False,
                'error': '缺少pandas或openpyxl库，请安装：pip install pandas openpyxl'
            }), 500
        except Exception as e:
            logger.error(f"导出要求失败: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    # ===================
    # 标书管理列表页API - 已迁移到 blueprints/api_tender_management_bp.py
    # ===================

    # @app.route('/api/tender-management/list', methods=['GET'])
    def get_tender_management_list():
        """获取标书管理列表"""
        try:
            from common.database import get_knowledge_base_db
            import json

            # 获取分页参数
            page = int(request.args.get('page', 1))
            page_size = int(request.args.get('page_size', DEFAULT_PAGE_SIZE))
            search_keyword = request.args.get('search', '')
            status_filter = request.args.get('status', '')  # all, in_progress, completed

            db = get_knowledge_base_db()

            # 构建查询条件
            where_conditions = []
            params = []

            # 搜索条件
            if search_keyword:
                where_conditions.append("""
                    (p.project_name LIKE ? OR c.company_name LIKE ?)
                """)
                params.extend([f'%{search_keyword}%', f'%{search_keyword}%'])

            # 状态筛选
            if status_filter == 'in_progress':
                where_conditions.append("t.overall_status IN ('pending', 'running')")
            elif status_filter == 'completed':
                where_conditions.append("t.overall_status = 'completed'")

            where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"

            # 查询总数
            count_query = f"""
                SELECT COUNT(DISTINCT p.project_id) as total
                FROM tender_projects p
                LEFT JOIN companies c ON p.company_id = c.company_id
                LEFT JOIN tender_processing_tasks t ON p.project_id = t.project_id
                LEFT JOIN tender_hitl_tasks h ON t.task_id = h.task_id
                WHERE {where_clause}
            """

            total_result = db.execute_query(count_query, params, fetch_one=True)
            total_count = total_result['total'] if total_result else 0

            # 计算分页
            total_pages = (total_count + page_size - 1) // page_size
            offset = (page - 1) * page_size

            # 查询列表数据
            list_query = f"""
                SELECT
                    p.project_id,
                    p.project_name,
                    p.project_number,
                    p.created_at as project_created_at,
                    p.updated_at as project_updated_at,
                    c.company_name,
                    c.legal_representative as authorized_person,

                    -- 处理任务信息
                    t.task_id,
                    t.overall_status as task_status,
                    t.current_step,
                    t.progress_percentage,
                    t.total_chunks,
                    t.valuable_chunks,
                    t.total_requirements,

                    -- HITL任务信息
                    h.hitl_task_id,
                    h.step1_status,
                    h.step1_data,
                    h.step2_status,
                    h.step3_status,
                    h.current_step as hitl_current_step,
                    h.overall_status as hitl_status

                FROM tender_projects p
                LEFT JOIN companies c ON p.company_id = c.company_id
                LEFT JOIN tender_processing_tasks t ON p.project_id = t.project_id
                LEFT JOIN tender_hitl_tasks h ON t.task_id = h.task_id
                WHERE {where_clause}
                ORDER BY p.updated_at DESC, p.created_at DESC
                LIMIT ? OFFSET ?
            """

            params.extend([page_size, offset])
            results = db.execute_query(list_query, params)

            # 处理结果，计算各阶段完成情况
            projects = []
            for row in results:
                # 解析step1_data来获取文件信息
                step1_data = {}
                if row['step1_data']:
                    try:
                        step1_data = json.loads(row['step1_data'])
                    except json.JSONDecodeError:
                        pass

                # 计算商务应答完成情况
                business_response_status = '未开始'
                business_response_progress = PROGRESS_NOT_STARTED
                if step1_data.get('business_response_file'):  # 检查商务应答文件
                    business_response_status = '已完成'
                    business_response_progress = PROGRESS_COMPLETE
                elif row['step1_status'] == 'in_progress':
                    business_response_status = '进行中'
                    business_response_progress = PROGRESS_HALF_COMPLETE

                # 计算技术点对点应答完成情况
                tech_response_status = '未开始'
                tech_response_progress = PROGRESS_NOT_STARTED
                if step1_data.get('technical_point_to_point_file'):  # 检查点对点应答文件
                    tech_response_status = '已完成'
                    tech_response_progress = PROGRESS_COMPLETE
                elif row['step2_status'] == 'in_progress':
                    tech_response_status = '进行中'
                    tech_response_progress = PROGRESS_HALF_COMPLETE

                # 计算技术方案情况
                tech_proposal_status = '未开始'
                tech_proposal_progress = PROGRESS_NOT_STARTED
                if step1_data.get('technical_proposal_file'):
                    tech_proposal_status = '已完成'
                    tech_proposal_progress = PROGRESS_COMPLETE
                elif row['hitl_current_step'] and row['hitl_current_step'] >= 2:
                    tech_proposal_status = '进行中'
                    tech_proposal_progress = PROGRESS_HALF_COMPLETE

                # 计算最后融合情况
                fusion_status = '未开始'
                fusion_progress = PROGRESS_NOT_STARTED
                all_completed = (business_response_progress == PROGRESS_COMPLETE and
                               tech_response_progress == PROGRESS_COMPLETE and
                               tech_proposal_progress == PROGRESS_COMPLETE)
                if all_completed:
                    fusion_status = '已完成'
                    fusion_progress = PROGRESS_COMPLETE
                elif any([business_response_progress > 0,
                         tech_response_progress > 0,
                         tech_proposal_progress > 0]):
                    fusion_status = '进行中'
                    fusion_progress = (business_response_progress +
                                     tech_response_progress +
                                     tech_proposal_progress) / 3

                projects.append({
                    'project_id': row['project_id'],
                    'project_name': row['project_name'] or '未命名项目',
                    'project_number': row['project_number'],
                    'company_name': row['company_name'] or '未设置',
                    'authorized_person': row['authorized_person'] or '未设置',
                    'business_response': {
                        'status': business_response_status,
                        'progress': business_response_progress
                    },
                    'tech_response': {
                        'status': tech_response_status,
                        'progress': tech_response_progress
                    },
                    'tech_proposal': {
                        'status': tech_proposal_status,
                        'progress': tech_proposal_progress
                    },
                    'fusion': {
                        'status': fusion_status,
                        'progress': round(fusion_progress, 1)
                    },
                    'created_at': row['project_created_at'],
                    'updated_at': row['project_updated_at']
                })

            return jsonify({
                'success': True,
                'data': {
                    'projects': projects,
                    'page': page,
                    'page_size': page_size,
                    'total': total_count,
                    'total_pages': total_pages
                }
            })

        except Exception as e:
            logger.error(f"获取标书管理列表失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/tender-management/stats/<int:project_id>', methods=['GET'])
    def get_tender_project_stats(project_id):
        """获取项目详细统计信息"""
        try:
            from common.database import get_knowledge_base_db

            db = get_knowledge_base_db()

            # 获取项目基本信息和处理统计
            stats_query = """
                SELECT
                    p.*,
                    c.company_name,
                    t.overall_status,
                    t.total_chunks,
                    t.valuable_chunks,
                    t.total_requirements,
                    h.step1_status,
                    h.step2_status,
                    h.step3_status,
                    h.step1_data
                FROM tender_projects p
                LEFT JOIN companies c ON p.company_id = c.company_id
                LEFT JOIN tender_processing_tasks t ON p.project_id = t.project_id
                LEFT JOIN tender_hitl_tasks h ON t.task_id = h.task_id
                WHERE p.project_id = ?
            """

            result = db.execute_query(stats_query, (project_id,), fetch_one=True)

            if not result:
                return jsonify({'success': False, 'error': '项目不存在'}), 404

            # 解析step1_data
            step1_data = {}
            if result['step1_data']:
                try:
                    import json
                    step1_data = json.loads(result['step1_data'])
                except json.JSONDecodeError:
                    pass

            stats = {
                'project_info': {
                    'project_id': result['project_id'],
                    'project_name': result['project_name'],
                    'company_name': result['company_name']
                },
                'processing_stats': {
                    'total_chunks': result['total_chunks'] or 0,
                    'valuable_chunks': result['valuable_chunks'] or 0,
                    'total_requirements': result['total_requirements'] or 0
                },
                'files': {
                    'business_response': step1_data.get('technical_point_to_point_file'),
                    'tech_proposal': step1_data.get('technical_proposal_file')
                },
                'status': {
                    'overall': result['overall_status'],
                    'step1': result['step1_status'],
                    'step2': result['step2_status'],
                    'step3': result['step3_status']
                }
            }

            return jsonify({
                'success': True,
                'stats': stats
            })

        except Exception as e:
            logger.error(f"获取项目统计信息失败: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/tender-management/project/<int:project_id>', methods=['DELETE'])
    def delete_tender_project(project_id):
        """删除项目及其关联数据"""
        try:
            from common.database import get_knowledge_base_db
            import json

            db = get_knowledge_base_db()

            # 1. 检查项目是否存在
            project_check = db.execute_query("""
                SELECT project_id, project_name, tender_document_path
                FROM tender_projects
                WHERE project_id = ?
            """, (project_id,), fetch_one=True)

            if not project_check:
                return jsonify({'success': False, 'error': '项目不存在'}), 404

            logger.info(f"开始删除项目: project_id={project_id}, project_name={project_check['project_name']}")

            # 2. 获取关联的任务ID (用于级联删除)
            task_info = db.execute_query("""
                SELECT task_id FROM tender_processing_tasks
                WHERE project_id = ?
            """, (project_id,), fetch_one=True)

            task_id = task_info['task_id'] if task_info else None

            # 3. 删除关联数据 (按外键依赖顺序)
            deleted_counts = {}

            # 3.1 删除HITL任务相关数据
            if task_id:
                # 删除HITL任务
                result = db.execute_query("""
                    DELETE FROM tender_hitl_tasks WHERE task_id = ?
                """, (task_id,))
                deleted_counts['hitl_tasks'] = result if result else 0

                # 删除处理日志
                result = db.execute_query("""
                    DELETE FROM tender_processing_logs WHERE task_id = ?
                """, (task_id,))
                deleted_counts['processing_logs'] = result if result else 0

                # 删除要求提取结果
                result = db.execute_query("""
                    DELETE FROM tender_requirements WHERE chunk_id IN (
                        SELECT chunk_id FROM tender_chunks WHERE project_id = ?
                    )
                """, (project_id,))
                deleted_counts['requirements'] = result if result else 0

                # 删除文档分块
                result = db.execute_query("""
                    DELETE FROM tender_chunks WHERE project_id = ?
                """, (project_id,))
                deleted_counts['chunks'] = result if result else 0

                # 删除处理任务
                result = db.execute_query("""
                    DELETE FROM tender_processing_tasks WHERE task_id = ?
                """, (task_id,))
                deleted_counts['processing_tasks'] = result if result else 0

            # 3.2 删除项目本身
            result = db.execute_query("""
                DELETE FROM tender_projects WHERE project_id = ?
            """, (project_id,))
            deleted_counts['projects'] = result if result else 0

            # 4. 可选: 删除关联文件 (暂时不删除物理文件，避免误删)
            # if project_check['tender_document_path']:
            #     try:
            #         os.remove(project_check['tender_document_path'])
            #         logger.info(f"已删除标书文件: {project_check['tender_document_path']}")
            #     except Exception as e:
            #         logger.warning(f"删除标书文件失败: {e}")

            logger.info(f"项目删除完成: project_id={project_id}, 删除统计={deleted_counts}")

            return jsonify({
                'success': True,
                'message': f"项目 '{project_check['project_name']}' 已成功删除",
                'deleted_counts': deleted_counts,
                'project_id': project_id
            })

        except Exception as e:
            logger.error(f"删除项目失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return jsonify({'success': False, 'error': f'删除失败: {str(e)}'}), 500

    # ===================
    # HITL（Human-in-the-Loop）API - 三步人工确认流程
    # ===================

    # 注册 HITL API 路由
    from web.api_tender_processing_hitl import register_hitl_routes
    register_hitl_routes(app)
    logger.info("HITL API 路由已注册")

    # ===================
    # 错误处理
    # ===================
    
    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({'error': 'Not Found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"内部服务器错误: {error}")
        return jsonify({'error': 'Internal Server Error'}), 500
    
    @app.errorhandler(413)
    def file_too_large(error):
        return jsonify({'error': '文件太大'}), 413

    @app.route('/api/tender-processing/sync-point-to-point/<task_id>', methods=['POST'])
    def sync_point_to_point_to_hitl(task_id):
        """
        同步点对点应答文件到HITL投标项目
        接收点对点应答生成的文件路径,复制到HITL任务目录,保存为"应答完成文件"
        """
        try:
            import json
            import shutil
            from common.database import get_knowledge_base_db

            data = request.get_json()
            source_file_path = data.get('file_path')

            if not source_file_path:
                return jsonify({
                    'success': False,
                    'error': '未提供文件路径'
                }), 400

            # 如果传入的是下载URL(以/api/downloads/或/downloads/开头),转换为实际文件路径
            if source_file_path.startswith('/api/downloads/') or source_file_path.startswith('/downloads/'):
                filename = source_file_path.replace('/api/downloads/', '').replace('/downloads/', '')
                # 使用URL解码处理中文文件名
                from urllib.parse import unquote
                filename = unquote(filename)
                project_root = Path(__file__).parent.parent
                source_file_path = os.path.join(project_root, 'data/outputs', filename)
                logger.info(f"从下载URL转换为文件路径: {source_file_path}")

            # 检查源文件是否存在
            if not os.path.exists(source_file_path):
                return jsonify({
                    'success': False,
                    'error': '源文件不存在'
                }), 404

            logger.info(f"同步点对点应答文件到HITL项目: task_id={task_id}, file_path={source_file_path}")

            # 获取数据库实例
            db = get_knowledge_base_db()

            # 查询任务信息
            task_data = db.execute_query("""
                SELECT step1_data FROM tender_hitl_tasks
                WHERE hitl_task_id = ?
            """, (task_id,), fetch_one=True)

            if not task_data:
                return jsonify({
                    'success': False,
                    'error': '任务不存在'
                }), 404

            step1_data = json.loads(task_data['step1_data'])

            # 创建存储目录
            now = datetime.now()
            project_root = Path(__file__).parent.parent
            save_dir = os.path.join(
                project_root,
                'data/uploads/completed_response_files',
                str(now.year),
                f"{now.month:02d}",
                task_id
            )
            os.makedirs(save_dir, exist_ok=True)

            # 生成文件名
            source_filename = os.path.basename(source_file_path)
            # 从源文件名提取,如果包含时间戳则保留,否则添加时间戳
            if '_' in source_filename:
                base_name = source_filename.rsplit('.', 1)[0]
                filename = f"{base_name}_应答完成.docx"
            else:
                filename = f"点对点应答_{now.strftime('%Y%m%d_%H%M%S')}_应答完成.docx"

            # 复制文件到目标位置
            target_path = os.path.join(save_dir, filename)
            shutil.copy2(source_file_path, target_path)

            # 计算文件大小
            file_size = os.path.getsize(target_path)

            # 更新任务的step1_data - 使用独立字段存储点对点应答文件
            point_to_point_file_info = {
                "file_path": target_path,
                "filename": filename,
                "file_size": file_size,
                "saved_at": now.isoformat(),
                "source_file": source_file_path
            }
            step1_data['technical_point_to_point_file'] = point_to_point_file_info

            db.execute_query("""
                UPDATE tender_hitl_tasks
                SET step1_data = ?
                WHERE hitl_task_id = ?
            """, (json.dumps(step1_data), task_id))

            logger.info(f"同步点对点应答文件到HITL任务: {task_id}, 文件: {filename} ({file_size} bytes)")

            return jsonify({
                'success': True,
                'message': '点对点应答文件已成功同步到投标项目',
                'file_path': target_path,
                'filename': filename,
                'file_size': file_size,
                'saved_at': point_to_point_file_info['saved_at']
            })

        except Exception as e:
            logger.error(f"同步点对点应答文件失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return jsonify({
                'success': False,
                'error': f'同步失败: {str(e)}'
            }), 500

    @app.route('/api/tender-processing/sync-tech-proposal/<task_id>', methods=['POST'])
    def sync_tech_proposal_to_hitl(task_id):
        """
        同步技术方案文件到HITL投标项目
        接收技术方案生成的文件路径,复制到HITL任务目录,保存为"应答完成文件"
        """
        try:
            import json
            import shutil
            from common.database import get_knowledge_base_db

            data = request.get_json()
            source_file_path = data.get('file_path')
            output_files = data.get('output_files', {})  # 可能包含多个输出文件

            if not source_file_path:
                return jsonify({
                    'success': False,
                    'error': '未提供文件路径'
                }), 400

            # 如果传入的是下载URL(以/api/downloads/开头),转换为实际文件路径
            if source_file_path.startswith('/api/downloads/'):
                filename = source_file_path.replace('/api/downloads/', '')
                # 使用URL解码处理中文文件名
                from urllib.parse import unquote
                filename = unquote(filename)
                project_root = Path(__file__).parent.parent
                source_file_path = os.path.join(project_root, 'data/outputs', filename)
                logger.info(f"从下载URL转换为文件路径: {source_file_path}")

            # 检查源文件是否存在
            if not os.path.exists(source_file_path):
                return jsonify({
                    'success': False,
                    'error': '源文件不存在'
                }), 404

            logger.info(f"同步技术方案文件到HITL项目: task_id={task_id}, file_path={source_file_path}")

            # 获取数据库实例
            db = get_knowledge_base_db()

            # 查询任务信息
            task_data = db.execute_query("""
                SELECT step1_data FROM tender_hitl_tasks
                WHERE hitl_task_id = ?
            """, (task_id,), fetch_one=True)

            if not task_data:
                return jsonify({
                    'success': False,
                    'error': '任务不存在'
                }), 404

            step1_data = json.loads(task_data['step1_data'])

            # 创建存储目录
            now = datetime.now()
            project_root = Path(__file__).parent.parent
            save_dir = os.path.join(
                project_root,
                'data/uploads/completed_response_files',
                str(now.year),
                f"{now.month:02d}",
                task_id
            )
            os.makedirs(save_dir, exist_ok=True)

            # 生成文件名
            source_filename = os.path.basename(source_file_path)
            # 从源文件名提取,如果包含时间戳则保留,否则添加时间戳
            if '_' in source_filename:
                base_name = source_filename.rsplit('.', 1)[0]
                filename = f"{base_name}_应答完成.docx"
            else:
                filename = f"技术方案_{now.strftime('%Y%m%d_%H%M%S')}_应答完成.docx"

            # 复制文件到目标位置
            target_path = os.path.join(save_dir, filename)
            shutil.copy2(source_file_path, target_path)

            # 计算文件大小
            file_size = os.path.getsize(target_path)

            # 更新任务的step1_data - 使用独立字段存储技术方案文件
            tech_proposal_file_info = {
                "file_path": target_path,
                "filename": filename,
                "file_size": file_size,
                "saved_at": now.isoformat(),
                "source_file": source_file_path,
                "output_files": output_files  # 保存所有输出文件信息
            }
            step1_data['technical_proposal_file'] = tech_proposal_file_info

            db.execute_query("""
                UPDATE tender_hitl_tasks
                SET step1_data = ?
                WHERE hitl_task_id = ?
            """, (json.dumps(step1_data), task_id))

            logger.info(f"同步技术方案文件到HITL任务: {task_id}, 文件: {filename} ({file_size} bytes)")

            return jsonify({
                'success': True,
                'message': '技术方案文件已成功同步到投标项目',
                'file_path': target_path,
                'filename': filename,
                'file_size': file_size,
                'saved_at': tech_proposal_file_info['saved_at']
            })

        except Exception as e:
            logger.error(f"同步技术方案文件失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return jsonify({
                'success': False,
                'error': f'同步失败: {str(e)}'
            }), 500

    # 调试API - 查看项目状态详情
    @app.route('/api/debug/project-status/<int:project_id>', methods=['GET'])
    def debug_project_status(project_id):
        """调试API：查看项目的完整状态信息"""
        try:
            from common.database import get_knowledge_base_db
            import json

            db = get_knowledge_base_db()

            query = """
                SELECT
                    p.project_id,
                    p.project_name,
                    h.hitl_task_id,
                    h.step1_status,
                    h.step2_status,
                    h.step3_status,
                    h.step1_data,
                    t.overall_status as task_status,
                    t.total_requirements
                FROM tender_projects p
                LEFT JOIN tender_processing_tasks t ON p.project_id = t.project_id
                LEFT JOIN tender_hitl_tasks h ON t.task_id = h.task_id
                WHERE p.project_id = ?
            """

            result = db.execute_query(query, (project_id,), fetch_one=True)

            if not result:
                return jsonify({'success': False, 'error': '项目不存在'})

            # 解析step1_data
            step1_data = {}
            file_fields = {}
            if result['step1_data']:
                try:
                    step1_data = json.loads(result['step1_data'])
                    # 提取所有文件相关字段
                    for key, value in step1_data.items():
                        if 'file' in key.lower():
                            file_fields[key] = value
                except json.JSONDecodeError as e:
                    file_fields['parse_error'] = str(e)

            debug_info = {
                'project_id': result['project_id'],
                'project_name': result['project_name'],
                'hitl_task_id': result['hitl_task_id'],
                'step1_status': result['step1_status'],
                'step2_status': result['step2_status'],
                'step3_status': result['step3_status'],
                'task_status': result['task_status'],
                'total_requirements': result['total_requirements'],
                'file_fields': file_fields,
                'has_business_response_file': 'business_response_file' in file_fields,
                'has_technical_point_to_point_file': 'technical_point_to_point_file' in file_fields,
                'has_technical_proposal_file': 'technical_proposal_file' in file_fields
            }

            return jsonify({'success': True, 'data': debug_info})

        except Exception as e:
            import traceback
            return jsonify({
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc()
            })

    return app

def main():
    """主函数"""
    app = create_app()
    config = get_config()
    web_config = config.get_web_config()

    print(f"启动AI标书系统Web应用...")
    print(f"访问地址: http://{web_config['host']}:{web_config['port']}")

    app.run(
        host=web_config['host'],
        port=web_config['port'],
        debug=web_config['debug']
    )

if __name__ == '__main__':
    main()