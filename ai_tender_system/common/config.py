#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理模块
处理系统配置、环境变量和路径管理
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# 加载环境变量
env_file = BASE_DIR / '.env'
if env_file.exists():
    load_dotenv(env_file)
    print(f"加载环境变量文件: {env_file}")
else:
    print(f"警告: 环境变量文件不存在: {env_file}")


class Config:
    """配置管理类"""

    def __init__(self):
        """初始化配置"""
        self.base_dir = BASE_DIR
        self.ai_tender_system_dir = BASE_DIR / 'ai_tender_system'
        self.data_dir = self.ai_tender_system_dir / 'data'

        # 确保必要的目录存在
        self._ensure_directories()

        # 加载配置
        self._load_config()

    def _ensure_directories(self):
        """确保必要的目录存在"""
        dirs = [
            self.data_dir,
            self.data_dir / 'uploads',
            self.data_dir / 'output',
            self.data_dir / 'logs',
            self.data_dir / 'configs',
            self.data_dir / 'configs' / 'companies',
            self.data_dir / 'templates',
            self.data_dir / 'knowledge_base'
        ]
        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)

    def _load_config(self):
        """加载配置项"""
        # API配置
        self.api_config = {
            'default': {
                'api_key': os.getenv('DEFAULT_API_KEY', 'sk-40a84bd082404004b9741e3a18d5f881'),
                'api_endpoint': os.getenv('API_ENDPOINT', 'https://api.openai.com/v1/chat/completions'),
                'model_name': os.getenv('MODEL_NAME', 'gpt-4o-mini'),
                'max_tokens': int(os.getenv('MAX_TOKENS', '1000')),
                'timeout': int(os.getenv('API_TIMEOUT', '30'))
            },
            'openai': {
                'api_key': os.getenv('OPENAI_API_KEY', 'sk-40a84bd082404004b9741e3a18d5f881'),
                'api_endpoint': os.getenv('OPENAI_API_ENDPOINT', 'https://api.openai.com/v1/chat/completions'),
                'model_name': 'gpt-4o-mini',
                'max_tokens': int(os.getenv('OPENAI_MAX_TOKENS', '1000')),
                'timeout': int(os.getenv('OPENAI_TIMEOUT', '30'))
            },
            'unicom-yuanjing': {
                'api_key': os.getenv('ACCESS_TOKEN', 'sk-40a84bd082404004b9741e3a18d5f881'),
                'base_url': os.getenv('UNICOM_BASE_URL', 'https://maas-api.ai-yuanjing.com/openapi/compatible-mode/v1'),
                'model_name': os.getenv('UNICOM_MODEL_NAME', 'deepseek-v3'),
                'max_tokens': int(os.getenv('UNICOM_MAX_TOKENS', '1000')),
                'timeout': int(os.getenv('UNICOM_TIMEOUT', '30'))
            }
        }

        # Web服务配置
        self.web_config = {
            'host': os.getenv('WEB_HOST', '0.0.0.0'),
            'port': int(os.getenv('WEB_PORT', '8082')),
            'debug': os.getenv('DEBUG', 'True').lower() == 'true',
            'secret_key': os.getenv('SECRET_KEY', 'ai-tender-system-2025')
        }

        # 文件上传配置
        self.upload_config = {
            'max_size': int(os.getenv('MAX_UPLOAD_SIZE', '50')) * 1024 * 1024,  # MB转字节
            'max_file_size': int(os.getenv('MAX_UPLOAD_SIZE', '50')) * 1024 * 1024,  # 兼容旧名称
            'allowed_extensions': {
                'tender_info': {'.pdf', '.doc', '.docx', '.txt'},
                'business_response': {'.docx', '.doc'},
                'point_to_point': {'.docx', '.doc'},
                'default': {'.pdf', '.doc', '.docx', '.txt'}
            }
        }

    def get_api_config(self, model_name: str = 'default') -> Dict[str, Any]:
        """获取API配置"""
        return self.api_config.get(model_name, self.api_config['default'])

    def get_web_config(self) -> Dict[str, Any]:
        """获取Web服务配置"""
        return self.web_config

    def get_upload_config(self) -> Dict[str, Any]:
        """获取上传配置"""
        return self.upload_config

    def get_path(self, path_type: str) -> Path:
        """获取路径"""
        paths = {
            'base': self.base_dir,
            'data': self.data_dir,
            'upload': self.data_dir / 'uploads',
            'output': self.data_dir / 'output',
            'logs': self.data_dir / 'logs',
            'configs': self.data_dir / 'configs',
            'companies': self.data_dir / 'configs' / 'companies',
            'templates': self.data_dir / 'templates',
            'knowledge_base': self.data_dir / 'knowledge_base'
        }
        return paths.get(path_type, self.data_dir)

    def get_logging_config(self) -> Dict[str, Any]:
        """获取日志配置"""
        return {
            'log_dir': str(self.get_path('logs')),
            'level': os.getenv('LOG_LEVEL', 'INFO'),
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'log_file': 'ai_tender_system.log',
            'max_bytes': 10 * 1024 * 1024,  # 10MB
            'backup_count': 5
        }


# 全局配置实例
_config_instance = None


def get_config() -> Config:
    """获取配置实例（单例模式）"""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance


# 导出
__all__ = ['Config', 'get_config']