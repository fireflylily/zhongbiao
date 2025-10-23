#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API响应帮助函数
提供统一的成功/错误响应格式
"""

from flask import jsonify
from typing import Any, Optional, Dict


def success_response(data: Any = None, message: str = "操作成功", code: int = 200) -> tuple:
    """
    返回成功响应
    Args:
        data: 响应数据
        message: 成功消息
        code: HTTP状态码
    Returns:
        Flask响应对象
    """
    response = {
        "success": True,
        "message": message,
        "data": data
    }
    return jsonify(response), code


def error_response(message: str = "操作失败", error: Optional[str] = None, code: int = 400) -> tuple:
    """
    返回错误响应
    Args:
        message: 错误消息
        error: 详细错误信息
        code: HTTP状态码
    Returns:
        Flask响应对象
    """
    response = {
        "success": False,
        "message": message
    }

    if error:
        response["error"] = error

    return jsonify(response), code


def paginated_response(items: list, total: int, page: int = 1, page_size: int = 20,
                       message: str = "查询成功") -> tuple:
    """
    返回分页响应
    Args:
        items: 数据项列表
        total: 总数
        page: 当前页码
        page_size: 每页大小
        message: 成功消息
    Returns:
        Flask响应对象
    """
    total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0

    data = {
        "items": items,
        "pagination": {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }
    }

    return success_response(data, message)


def validation_error(errors: Dict[str, Any]) -> tuple:
    """
    返回验证错误响应
    Args:
        errors: 验证错误字典
    Returns:
        Flask响应对象
    """
    response = {
        "success": False,
        "message": "验证失败",
        "errors": errors
    }
    return jsonify(response), 422