#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信工具类
包含 access_token 管理和订阅消息发送功能
"""

import requests
import time
from typing import Dict, Optional
from datetime import datetime

from .logger import get_module_logger
from .config import get_config

logger = get_module_logger("wechat_utils")
config = get_config()


class WeChatNotifier:
    """微信通知发送器"""

    # access_token 缓存
    _access_token: Optional[str] = None
    _token_expires_at: float = 0

    def __init__(self):
        wechat_config = config.get_wechat_config() if hasattr(config, 'get_wechat_config') else {}
        self.appid = wechat_config.get('appid', '')
        self.secret = wechat_config.get('secret', '')
        self.template_risk_complete = wechat_config.get('template_risk_complete', '')

    def get_access_token(self) -> str:
        """
        获取 access_token（带缓存）

        Returns:
            access_token 字符串

        Raises:
            Exception: 获取失败时抛出异常
        """
        now = time.time()

        # 检查缓存是否有效（提前5分钟刷新）
        if self._access_token and self._token_expires_at > now + 300:
            return self._access_token

        if not self.appid or not self.secret:
            raise Exception("微信配置未设置 (appid/secret)")

        # 重新获取
        try:
            res = requests.get(
                'https://api.weixin.qq.com/cgi-bin/token',
                params={
                    'grant_type': 'client_credential',
                    'appid': self.appid,
                    'secret': self.secret
                },
                timeout=10
            )

            data = res.json()

            if 'access_token' in data:
                self._access_token = data['access_token']
                self._token_expires_at = now + data.get('expires_in', 7200)
                logger.info("access_token 获取成功")
                return self._access_token
            else:
                error_msg = data.get('errmsg', '未知错误')
                logger.error(f"获取 access_token 失败: {data}")
                raise Exception(f"获取 access_token 失败: {error_msg}")

        except requests.RequestException as e:
            logger.error(f"获取 access_token 网络异常: {e}")
            raise

    def send_subscribe_message(self,
                               openid: str,
                               template_id: str,
                               data: Dict,
                               page: str = None,
                               miniprogram_state: str = 'formal') -> Dict:
        """
        发送订阅消息

        Args:
            openid: 用户 openid
            template_id: 消息模板 ID
            data: 消息数据，格式如 {"thing1": {"value": "xxx"}}
            page: 点击消息跳转的页面路径
            miniprogram_state: 小程序状态 (formal/developer/trial)

        Returns:
            微信 API 响应

        Raises:
            Exception: 发送失败时抛出异常
        """
        try:
            access_token = self.get_access_token()

            payload = {
                'touser': openid,
                'template_id': template_id,
                'data': data,
                'miniprogram_state': miniprogram_state
            }

            if page:
                payload['page'] = page

            res = requests.post(
                f'https://api.weixin.qq.com/cgi-bin/message/subscribe/send?access_token={access_token}',
                json=payload,
                timeout=10
            )

            result = res.json()

            if result.get('errcode') == 0:
                logger.info(f"订阅消息发送成功: openid={openid[:8]}...")
            else:
                logger.warning(f"订阅消息发送失败: {result}")

            return result

        except Exception as e:
            logger.error(f"发送订阅消息异常: {e}")
            raise

    def send_risk_analysis_complete(self,
                                    openid: str,
                                    task_id: str,
                                    filename: str,
                                    risk_count: int) -> Optional[Dict]:
        """
        发送风险分析完成通知

        需要在微信公众平台配置对应的订阅消息模板:
        - thing1: 文件名
        - number2: 风险项数量
        - time3: 完成时间

        Args:
            openid: 用户 openid
            task_id: 任务 ID
            filename: 文件名
            risk_count: 风险项数量

        Returns:
            微信 API 响应，如果模板未配置则返回 None
        """
        if not self.template_risk_complete:
            logger.debug("未配置风险分析完成通知模板，跳过发送")
            return None

        try:
            # 截断文件名（模板限制20字符）
            display_filename = filename[:17] + "..." if len(filename) > 20 else filename

            return self.send_subscribe_message(
                openid=openid,
                template_id=self.template_risk_complete,
                data={
                    'thing1': {'value': display_filename},
                    'number2': {'value': risk_count},
                    'time3': {'value': datetime.now().strftime('%Y-%m-%d %H:%M')}
                },
                page=f'/pages/index/check/check?taskId={task_id}'
            )

        except Exception as e:
            logger.error(f"发送风险分析完成通知失败: {e}")
            return None


# 全局单例
_wechat_notifier: Optional[WeChatNotifier] = None


def get_wechat_notifier() -> WeChatNotifier:
    """获取微信通知器单例"""
    global _wechat_notifier
    if _wechat_notifier is None:
        _wechat_notifier = WeChatNotifier()
    return _wechat_notifier
