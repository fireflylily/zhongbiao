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

    # 阶段1: 认证和静态页面蓝图
    try:
        from .auth_bp import auth_bp
        app.register_blueprint(auth_bp)
        logger.info("认证蓝图注册成功")
    except ImportError as e:
        logger.warning(f"认证蓝图加载失败: {e}")

    try:
        from .pages_bp import pages_bp
        app.register_blueprint(pages_bp)
        logger.info("页面蓝图注册成功")
    except ImportError as e:
        logger.warning(f"页面蓝图加载失败: {e}")

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

    # 阶段4: HITL任务处理蓝图
    # (待实现)

    logger.info("所有蓝图注册完成")


__all__ = ['register_all_blueprints']
