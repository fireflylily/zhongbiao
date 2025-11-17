"""
ABTest 用户管理模块
提供用户和角色管理功能
"""

from flask import Flask


def init_app(app: Flask):
    """初始化 ABTest 模块"""
    from .blueprints.user_management_bp import user_management_bp

    # 注册蓝图
    app.register_blueprint(user_management_bp, url_prefix='/abtest')

    print("ABTest 用户管理模块已初始化")
