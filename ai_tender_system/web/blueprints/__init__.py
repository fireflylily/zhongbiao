#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
蓝图注册模块
统一管理和注册所有应用蓝图
"""

from flask import Flask


def register_all_blueprints(app: Flask, config, logger):
    """
    注册所有内部蓝图

    Args:
        app: Flask应用实例
        config: 配置对象
        logger: 日志对象

    Notes:
        - 蓝图按功能域组织
        - 支持增量迁移：可以逐步启用/禁用蓝图
        - 每个蓝图独立，互不依赖
    """

    # 阶段1: 认证蓝图 (优先级最高)
    try:
        from .auth_bp import auth_bp
        app.register_blueprint(auth_bp)
        logger.info("认证蓝图注册成功")
    except ImportError as e:
        logger.warning(f"认证蓝图加载失败: {e}")

    # 静态文件蓝图
    try:
        from .static_files_bp import static_files_bp
        app.register_blueprint(static_files_bp)
        logger.info("静态文件蓝图注册成功")
    except ImportError as e:
        logger.warning(f"静态文件蓝图加载失败: {e}")

    # 阶段2: 核心API蓝图
    try:
        from .api_core_bp import api_core_bp
        app.register_blueprint(api_core_bp)
        logger.info("核心API蓝图注册成功")
    except ImportError as e:
        logger.warning(f"核心API蓝图加载失败: {e}")

    try:
        from .api_files_bp import api_files_bp
        app.register_blueprint(api_files_bp)
        logger.info("文件管理API蓝图注册成功")
    except ImportError as e:
        logger.warning(f"文件管理API蓝图加载失败: {e}")

    try:
        from .api_tender_bp import api_tender_bp
        app.register_blueprint(api_tender_bp)
        logger.info("招标信息API蓝图注册成功")
    except ImportError as e:
        logger.warning(f"招标信息API蓝图加载失败: {e}")

    # 阶段3: 业务API蓝图
    try:
        from .api_business_bp import api_business_bp
        app.register_blueprint(api_business_bp)
        logger.info("商务应答API蓝图注册成功")
    except ImportError as e:
        logger.warning(f"商务应答API蓝图加载失败: {e}")

    try:
        from .api_tech_bp import api_tech_bp
        app.register_blueprint(api_tech_bp)
        logger.info("技术需求API蓝图注册成功")
    except ImportError as e:
        logger.warning(f"技术需求API蓝图加载失败: {e}")

    try:
        from .api_companies_bp import api_companies_bp
        app.register_blueprint(api_companies_bp)
        logger.info("公司管理API蓝图注册成功")
    except ImportError as e:
        logger.warning(f"公司管理API蓝图加载失败: {e}")

    try:
        from .api_projects_bp import api_projects_bp
        app.register_blueprint(api_projects_bp)
        logger.info("招标项目管理API蓝图注册成功")
    except ImportError as e:
        logger.warning(f"招标项目管理API蓝图加载失败: {e}")

    try:
        from .api_editor_bp import api_editor_bp
        app.register_blueprint(api_editor_bp)
        logger.info("文档编辑器API蓝图注册成功")
    except ImportError as e:
        logger.warning(f"文档编辑器API蓝图加载失败: {e}")

    try:
        from .api_models_bp import api_models_bp
        app.register_blueprint(api_models_bp)
        logger.info("AI模型管理API蓝图注册成功")
    except ImportError as e:
        logger.warning(f"AI模型管理API蓝图加载失败: {e}")

    try:
        from .api_tender_management_bp import api_tender_management_bp
        app.register_blueprint(api_tender_management_bp)
        logger.info("标书管理API蓝图注册成功")
    except ImportError as e:
        logger.warning(f"标书管理API蓝图加载失败: {e}")

    try:
        from .api_tender_processing_bp import api_tender_processing_bp
        app.register_blueprint(api_tender_processing_bp)
        logger.info("标书智能处理API蓝图注册成功")
    except ImportError as e:
        logger.warning(f"标书智能处理API蓝图加载失败: {e}")

    try:
        from .document_merger_api import document_merger_api_bp
        app.register_blueprint(document_merger_api_bp)
        logger.info("文档融合API蓝图注册成功")
    except ImportError as e:
        logger.warning(f"文档融合API蓝图加载失败: {e}")

    # 解析方法对比调试工具
    try:
        from .api_parser_debug_bp import api_parser_debug_bp
        app.register_blueprint(api_parser_debug_bp)
        logger.info("解析方法对比调试API蓝图注册成功")
    except ImportError as e:
        logger.warning(f"解析方法对比调试API蓝图加载失败: {e}")

    # 阶段4: 知识库扩展模块
    try:
        from modules.resume_library.api import resume_library_bp
        app.register_blueprint(resume_library_bp)
        logger.info("简历库API蓝图注册成功")
    except ImportError as e:
        logger.warning(f"简历库API蓝图加载失败: {e}")

    # 阶段5: HITL任务处理蓝图
    # (待实现)

    # 阶段6: ABTest用户管理模块
    try:
        import sys
        from pathlib import Path
        # 添加项目根目录到Python路径
        project_root = Path(__file__).parent.parent.parent.parent
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))

        from abtest.blueprints.user_management_bp import user_management_bp
        app.register_blueprint(user_management_bp, url_prefix='/abtest')
        logger.info("ABTest用户管理蓝图注册成功")
    except ImportError as e:
        logger.warning(f"ABTest用户管理蓝图加载失败: {e}")

    # ============================================================
    # Vue前端应用蓝图 - 必须最后注册(作为catch-all路由)
    # ============================================================
    try:
        from .vue_app_bp import vue_app_bp
        app.register_blueprint(vue_app_bp)
        logger.info("✅ Vue前端应用蓝图注册成功 (主路径: / - 已切换到新前端)")
    except ImportError as e:
        logger.error(f"❌ Vue前端应用蓝图加载失败: {e}")
        logger.error("   系统将无法访问新Vue前端,请检查构建是否完成!")

    logger.info("所有蓝图注册完成")


__all__ = ['register_all_blueprints']
