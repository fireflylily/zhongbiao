"""
ABTest 模块
提供用户管理和解析器测试功能
"""

from flask import Flask


def init_app(app: Flask):
    """初始化 ABTest 模块"""
    from .blueprints.user_management_bp import user_management_bp
    from .blueprints.parser_abtest_bp import parser_abtest_bp

    # 注册蓝图
    app.register_blueprint(user_management_bp, url_prefix='/abtest')
    app.register_blueprint(parser_abtest_bp, url_prefix='/abtest')

    print("ABTest 模块已初始化(用户管理 + 解析器测试)")
