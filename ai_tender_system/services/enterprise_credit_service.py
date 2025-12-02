"""
企业征信服务

集成第三方企业征信API,提供企业信息查询功能
"""

import time
import requests
import urllib.parse
from typing import Dict, List, Optional, Any
from ai_tender_system.utils.crypto_utils import CryptoUtils


class EnterpriseCreditService:
    """企业征信服务类"""

    def __init__(
        self,
        base_url: str,
        cust_user_id: str,
        api_key: str,
        encrypt_key: str,
        encrypt_iv: str,
        encrypt_method: str = 'aes'
    ):
        """
        初始化企业征信服务

        Args:
            base_url: API基础URL
            cust_user_id: 客户用户ID
            api_key: API密钥
            encrypt_key: 加密密钥(Base64)
            encrypt_iv: 加密向量
            encrypt_method: 加密方式('aes'或'3des')
        """
        self.base_url = base_url.rstrip('/')
        self.cust_user_id = cust_user_id
        self.api_key = api_key
        self.encrypt_key = encrypt_key
        self.encrypt_iv = encrypt_iv
        self.encrypt_method = encrypt_method.lower()

        # 加密方式映射
        self.encrypt_type_map = {
            'none': '0',
            'des': '1',
            '3des': '2',
            'aes': '3',
            'rsa': '4',
            'sm4': '5'
        }

    def _encrypt_params(self, params: Dict[str, str]) -> str:
        """
        加密业务参数

        Args:
            params: 业务参数字典

        Returns:
            加密后的参数字符串(Base64)
        """
        # 构造参数字符串: key1=value1&key2=value2
        param_str = '&'.join([f"{k}={v}" for k, v in params.items()])

        # 根据加密方式进行加密
        if self.encrypt_method == 'aes':
            return CryptoUtils.aes_encrypt(self.encrypt_key, self.encrypt_iv, param_str)
        elif self.encrypt_method == '3des':
            return CryptoUtils.des3_encrypt(self.encrypt_key, self.encrypt_iv, param_str)
        elif self.encrypt_method == 'des':
            return CryptoUtils.des_encrypt(self.encrypt_key, self.encrypt_iv, param_str)
        else:
            # 不加密,直接返回
            return param_str

    def _generate_order_id(self) -> str:
        """
        生成客户订单ID

        Returns:
            16-32位订单ID
        """
        timestamp = str(int(time.time() * 1000))
        # 使用时间戳后16位作为订单ID
        return timestamp[-16:]

    def _build_request_data(self, business_params: Dict[str, str]) -> Dict[str, str]:
        """
        构建请求数据

        Args:
            business_params: 业务参数

        Returns:
            完整的请求参数
        """
        # 加密业务参数
        encrypted_params = self._encrypt_params(business_params)

        # 构建请求数据
        return {
            'custUserId': self.cust_user_id,
            'custOrderId': self._generate_order_id(),
            'apiKey': self.api_key,
            'reqTime': str(int(time.time() * 1000)),
            'auxiliaryParameter': self.encrypt_type_map.get(self.encrypt_method, '0'),
            'primaryParameter': encrypted_params
        }

    def _make_request(self, business_params: Dict[str, str]) -> Dict[str, Any]:
        """
        发送请求到第三方API

        Args:
            business_params: 业务参数

        Returns:
            响应数据

        Raises:
            requests.RequestException: 请求失败
            ValueError: 响应数据异常
        """
        # 构建请求数据
        request_data = self._build_request_data(business_params)

        # 发送POST请求
        url = f"{self.base_url}/api/main/v2"
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cache-Control': 'no-cache'
        }

        try:
            response = requests.post(
                url,
                data=request_data,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()

            # 解析JSON响应
            result = response.json()

            # 检查响应状态
            if result.get('code') != '200':
                error_msg = result.get('msg', '未知错误')
                raise ValueError(f"API返回错误: {result.get('code')} - {error_msg}")

            return result

        except requests.RequestException as e:
            raise requests.RequestException(f"请求第三方API失败: {str(e)}")
        except ValueError as e:
            raise ValueError(f"解析API响应失败: {str(e)}")

    def search_enterprises(self, keyword: str) -> List[Dict[str, Any]]:
        """
        搜索企业列表 (API 100102)

        Args:
            keyword: 企业名称或统一社会信用代码

        Returns:
            企业列表
        """
        # 业务参数
        business_params = {
            'word': keyword
        }

        try:
            result = self._make_request(business_params)

            # 获取data字段
            data = result.get('data', '')

            # 如果data是加密的,需要解密
            if isinstance(data, str) and self.encrypt_method != 'none':
                if self.encrypt_method == 'aes':
                    decrypted_data = CryptoUtils.aes_decrypt(
                        self.encrypt_key,
                        self.encrypt_iv,
                        data
                    )
                elif self.encrypt_method == '3des':
                    decrypted_data = CryptoUtils.des3_decrypt(
                        self.encrypt_key,
                        self.encrypt_iv,
                        data
                    )
                elif self.encrypt_method == 'des':
                    decrypted_data = CryptoUtils.des_decrypt(
                        self.encrypt_key,
                        self.encrypt_iv,
                        data
                    )
                else:
                    decrypted_data = data

                # 尝试解析为JSON
                import json
                try:
                    data = json.loads(decrypted_data)
                except json.JSONDecodeError:
                    data = decrypted_data

            # 返回企业列表
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                return [data]
            else:
                return []

        except Exception as e:
            raise Exception(f"搜索企业失败: {str(e)}")

    def get_enterprise_detail(self, company_ss_id: str) -> Optional[Dict[str, Any]]:
        """
        获取企业详情 (API 100103)

        Args:
            company_ss_id: 企业ID

        Returns:
            企业详情数据
        """
        # 业务参数
        business_params = {
            'company_ss_id': company_ss_id
        }

        try:
            result = self._make_request(business_params)

            # 获取data字段
            data = result.get('data', '')

            # 如果data是加密的,需要解密
            if isinstance(data, str) and self.encrypt_method != 'none':
                if self.encrypt_method == 'aes':
                    decrypted_data = CryptoUtils.aes_decrypt(
                        self.encrypt_key,
                        self.encrypt_iv,
                        data
                    )
                elif self.encrypt_method == '3des':
                    decrypted_data = CryptoUtils.des3_decrypt(
                        self.encrypt_key,
                        self.encrypt_iv,
                        data
                    )
                elif self.encrypt_method == 'des':
                    decrypted_data = CryptoUtils.des_decrypt(
                        self.encrypt_key,
                        self.encrypt_iv,
                        data
                    )
                else:
                    decrypted_data = data

                # 尝试解析为JSON
                import json
                try:
                    data = json.loads(decrypted_data)
                except json.JSONDecodeError:
                    data = {'raw': decrypted_data}

            return data if isinstance(data, dict) else None

        except Exception as e:
            raise Exception(f"获取企业详情失败: {str(e)}")


def create_enterprise_credit_service(config: Dict[str, str]) -> EnterpriseCreditService:
    """
    创建企业征信服务实例的工厂函数

    Args:
        config: 配置字典

    Returns:
        EnterpriseCreditService实例
    """
    return EnterpriseCreditService(
        base_url=config.get('ENTERPRISE_CREDIT_BASE_URL', ''),
        cust_user_id=config.get('ENTERPRISE_CREDIT_CUST_USER_ID', ''),
        api_key=config.get('ENTERPRISE_CREDIT_API_KEY', ''),
        encrypt_key=config.get('ENTERPRISE_CREDIT_ENCRYPT_KEY', ''),
        encrypt_iv=config.get('ENTERPRISE_CREDIT_ENCRYPT_IV', ''),
        encrypt_method=config.get('ENTERPRISE_CREDIT_ENCRYPT_METHOD', 'aes')
    )
