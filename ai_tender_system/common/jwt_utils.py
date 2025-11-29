#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JWT Token 工具模块
提供 JWT token 的生成和验证功能
"""

import jwt
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class JWTError(Exception):
    """JWT相关异常"""
    pass


class TokenExpiredError(JWTError):
    """Token过期异常"""
    pass


class TokenInvalidError(JWTError):
    """Token无效异常"""
    pass


def generate_jwt_token(
    payload: Dict[str, Any],
    secret_key: str,
    expires_in: int = 86400,  # 默认24小时
    algorithm: str = 'HS256'
) -> str:
    """
    生成 JWT token

    Args:
        payload: Token载荷数据（用户信息）
        secret_key: 签名密钥
        expires_in: 过期时间（秒），默认24小时
        algorithm: 加密算法，默认HS256

    Returns:
        str: JWT token字符串

    Raises:
        JWTError: Token生成失败

    Example:
        >>> payload = {'user_id': 1, 'username': 'admin'}
        >>> token = generate_jwt_token(payload, 'secret-key', expires_in=3600)
    """
    try:
        # 创建完整的payload
        now = datetime.now(timezone.utc)
        token_payload = {
            **payload,  # 用户数据
            'iat': now,  # 签发时间 (issued at)
            'exp': now + timedelta(seconds=expires_in),  # 过期时间 (expiration)
            'nbf': now  # 生效时间 (not before)
        }

        # 生成token
        token = jwt.encode(
            token_payload,
            secret_key,
            algorithm=algorithm
        )

        logger.debug(f"生成JWT token成功，过期时间: {expires_in}秒")
        return token

    except Exception as e:
        logger.error(f"生成JWT token失败: {e}")
        raise JWTError(f"生成token失败: {str(e)}")


def verify_jwt_token(
    token: str,
    secret_key: str,
    algorithm: str = 'HS256'
) -> Dict[str, Any]:
    """
    验证 JWT token

    Args:
        token: JWT token字符串
        secret_key: 签名密钥
        algorithm: 加密算法，默认HS256

    Returns:
        Dict[str, Any]: Token载荷数据（用户信息）

    Raises:
        TokenExpiredError: Token已过期
        TokenInvalidError: Token无效

    Example:
        >>> token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        >>> payload = verify_jwt_token(token, 'secret-key')
        >>> print(payload['user_id'])
        1
    """
    try:
        # 验证并解码token
        payload = jwt.decode(
            token,
            secret_key,
            algorithms=[algorithm]
        )

        logger.debug(f"JWT token验证成功，用户: {payload.get('username', 'unknown')}")
        return payload

    except jwt.ExpiredSignatureError:
        logger.warning("JWT token已过期")
        raise TokenExpiredError("Token已过期，请重新登录")

    except jwt.InvalidTokenError as e:
        logger.warning(f"JWT token无效: {e}")
        raise TokenInvalidError(f"Token无效: {str(e)}")

    except Exception as e:
        logger.error(f"验证JWT token失败: {e}")
        raise JWTError(f"验证token失败: {str(e)}")


def decode_jwt_token_without_verification(token: str) -> Optional[Dict[str, Any]]:
    """
    解码 JWT token（不验证签名和过期时间）

    用于调试或获取token信息，不应用于生产环境的认证

    Args:
        token: JWT token字符串

    Returns:
        Optional[Dict[str, Any]]: Token载荷数据，解码失败返回None

    Example:
        >>> token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        >>> payload = decode_jwt_token_without_verification(token)
        >>> print(payload)
        {'user_id': 1, 'username': 'admin', 'exp': 1234567890}
    """
    try:
        # 不验证签名和过期时间，仅解码
        payload = jwt.decode(
            token,
            options={"verify_signature": False, "verify_exp": False}
        )
        return payload

    except Exception as e:
        logger.error(f"解码JWT token失败: {e}")
        return None


def get_token_expiration_time(token: str) -> Optional[datetime]:
    """
    获取 JWT token 的过期时间

    Args:
        token: JWT token字符串

    Returns:
        Optional[datetime]: 过期时间，解码失败返回None

    Example:
        >>> token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        >>> exp_time = get_token_expiration_time(token)
        >>> print(exp_time)
        2024-12-31 23:59:59+00:00
    """
    payload = decode_jwt_token_without_verification(token)
    if payload and 'exp' in payload:
        return datetime.fromtimestamp(payload['exp'], tz=timezone.utc)
    return None


def is_token_expired(token: str) -> bool:
    """
    检查 JWT token 是否已过期

    Args:
        token: JWT token字符串

    Returns:
        bool: True表示已过期，False表示未过期

    Example:
        >>> token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        >>> if is_token_expired(token):
        ...     print("Token已过期")
    """
    exp_time = get_token_expiration_time(token)
    if exp_time:
        return datetime.now(timezone.utc) > exp_time
    return True  # 无法获取过期时间，视为已过期


__all__ = [
    'generate_jwt_token',
    'verify_jwt_token',
    'decode_jwt_token_without_verification',
    'get_token_expiration_time',
    'is_token_expired',
    'JWTError',
    'TokenExpiredError',
    'TokenInvalidError'
]
