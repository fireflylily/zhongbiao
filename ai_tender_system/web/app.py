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

    # 豁免登录API的CSRF检查
    csrf.exempt('web.blueprints.auth_bp.login')

    logger.info("CSRF保护已启用，登录API已豁免")

    # 提供CSRF token的API端点
    @app.route('/api/csrf-token', methods=['GET'])
    def get_csrf_token():
        """获取CSRF token（用于AJAX请求）"""
        from flask import make_response
        token = generate_csrf()
        response = make_response(jsonify({'csrf_token': token}))
        # 设置cookie，使前端能够读取（HttpOnly=False允许JavaScript读取）
        response.set_cookie(
            'csrf_token',
            value=token,
            max_age=3600,  # 1小时过期
            httponly=False,  # 允许JavaScript读取
            samesite='Lax',  # CSRF保护
            secure=False  # 开发环境使用HTTP，生产环境应改为True
        )
        return response

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
    """注册遗留路由（待迁移到Blueprint）"""

    # TODO: 将以下路由迁移到 blueprints/api_legacy_bp.py

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

    # 注册 HITL API 路由
    from web.api_tender_processing_hitl import register_hitl_routes
    register_hitl_routes(app)
    logger.info("HITL API 路由已注册")

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
                    h.step1_status,
                    h.step2_status,
                    h.step3_status,
                    h.step1_data,
                    t.overall_status as task_status,
                    t.total_requirements
                FROM tender_projects p
                LEFT JOIN tender_processing_tasks t ON p.project_id = t.project_id
                LEFT JOIN tender_hitl_tasks h ON h.project_id = p.project_id
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