#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
认证中间件
提供登录验证装饰器和相关功能
"""

from functools import wraps
from flask import session, redirect, url_for


def login_required(f):
    """
    登录验证装饰器

    用于保护需要登录才能访问的路由
    如果用户未登录，自动重定向到登录页面

    Args:
        f: 被装饰的视图函数

    Returns:
        装饰后的函数

    Example:
        @app.route('/dashboard')
        @login_required
        def dashboard():
            return render_template('dashboard.html')
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('auth.auth_login'))
        return f(*args, **kwargs)
    return decorated_function
