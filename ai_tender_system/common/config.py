#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一配置管理模块
整合所有系统配置到单一入口
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional

# 加载 .env 文件（如果存在）
def load_env_file():
    """加载 .env 文件中的环境变量"""
    # 尝试多个可能的.env文件位置
    possible_paths = [
        Path(__file__).parent.parent / '.env',  # ai_tender_system/.env
        Path(__file__).parent.parent.parent / '.env',  # 项目根目录/.env
    ]

    for env_file in possible_paths:
        if env_file.exists():
            print(f"加载环境变量文件: {env_file}")
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        # 设置环境变量（覆盖现有值）
                        os.environ[key] = value
            return

    print("警告: 未找到.env文件")

# 在模块加载时执行
load_env_file()

class Config:
    """统一配置管理类"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.data_dir = self.base_dir / "data"
        self.config_dir = self.data_dir / "configs"
        self.upload_dir = self.data_dir / "uploads"
        self.output_dir = self.data_dir / "outputs"
        
        # 确保目录存在
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 加载配置
        self._load_config()
    
    def _load_config(self):
        """加载配置"""
        # API配置
        self.api_config = {
            'api_key': os.getenv('DEFAULT_API_KEY', ''),
            'api_endpoint': os.getenv('API_ENDPOINT', 'https://api.oaipro.com/v1/chat/completions'),
            'model_name': os.getenv('MODEL_NAME', 'gpt-5'),
            'max_tokens': int(os.getenv('MAX_TOKENS', '1000')),
            'timeout': int(os.getenv('API_TIMEOUT', '30'))
        }

        # 多模型配置
        self.multi_model_config = {
            'gpt-4o-mini': {
                'api_key': os.getenv('OPENAI_API_KEY', os.getenv('DEFAULT_API_KEY', '')),
                'api_endpoint': os.getenv('OPENAI_API_ENDPOINT', 'https://api.oaipro.com/v1/chat/completions'),
                'model_name': 'gpt-4o-mini',
                'max_tokens': int(os.getenv('OPENAI_MAX_TOKENS', '1000')),
                'timeout': int(os.getenv('OPENAI_TIMEOUT', '30')),
                'provider': 'OpenAI',
                'display_name': 'GPT-4o Mini',
                'description': 'OpenAI GPT-4o Mini模型，快速且经济的AI助手'
            },
            'unicom-yuanjing': {
                'access_token': os.getenv('ACCESS_TOKEN', ''),
                'base_url': os.getenv('UNICOM_BASE_URL', 'https://maas-api.ai-yuanjing.com/openapi/compatible-mode/v1'),
                'model_name': os.getenv('UNICOM_MODEL_NAME', 'deepseek-v3'),
                'max_tokens': int(os.getenv('UNICOM_MAX_TOKENS', '1000')),
                'timeout': int(os.getenv('UNICOM_TIMEOUT', '30')),
                'provider': 'China Unicom',
                'display_name': '联通元景大模型',
                'description': '中国联通元景大模型，基于官方OpenAI兼容接口，支持deepseek-v3等模型'
            }
        }
        
        # Web配置
        self.web_config = {
            'host': os.getenv('WEB_HOST', '0.0.0.0'),
            'port': int(os.getenv('WEB_PORT', '8082')),
            'debug': os.getenv('DEBUG', 'True').lower() == 'true',
            'secret_key': os.getenv('SECRET_KEY', 'ai-tender-system-2025')
        }
        
        # 文件上传配置
        self.upload_config = {
            'max_file_size': 100 * 1024 * 1024,  # 100MB
            'allowed_extensions': {
                'tender_info': {'txt', 'pdf', 'doc', 'docx'},
                'point_to_point': {'docx', 'doc'},
                'tech_proposal': {'docx', 'doc', 'pdf'},
                'business_response': {'docx', 'doc'},
                'images': {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
            }
        }
        
        # 日志配置
        self.logging_config = {
            'level': os.getenv('LOG_LEVEL', 'INFO'),
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'max_bytes': 10 * 1024 * 1024,  # 10MB
            'backup_count': 5
        }
    
    def get_api_config(self) -> Dict[str, Any]:
        """获取API配置"""
        return self.api_config.copy()
    
    def get_web_config(self) -> Dict[str, Any]:
        """获取Web配置"""
        return self.web_config.copy()
    
    def get_upload_config(self) -> Dict[str, Any]:
        """获取上传配置"""
        return self.upload_config.copy()
    
    def get_logging_config(self) -> Dict[str, Any]:
        """获取日志配置"""
        return self.logging_config.copy()

    def get_model_config(self, model_name: str) -> Dict[str, Any]:
        """获取指定模型的配置"""
        if model_name in self.multi_model_config:
            return self.multi_model_config[model_name].copy()
        else:
            # 如果没有找到指定模型，返回默认配置
            return self.api_config.copy()

    def get_all_model_configs(self) -> Dict[str, Dict[str, Any]]:
        """获取所有模型配置"""
        return self.multi_model_config.copy()

    def get_default_api_key(self) -> str:
        """获取默认API密钥"""
        return self.api_config['api_key']
    
    def set_api_key(self, api_key: str) -> None:
        """设置API密钥"""
        self.api_config['api_key'] = api_key
        # 可以选择保存到环境变量或配置文件
    
    def get_path(self, path_type: str) -> Path:
        """获取路径"""
        paths = {
            'base': self.base_dir,
            'data': self.data_dir,
            'config': self.config_dir,
            'upload': self.upload_dir,
            'output': self.output_dir,
            'web': self.base_dir / "web",
            'templates': self.base_dir / "web" / "templates",
            'static': self.base_dir / "web" / "static"
        }
        return paths.get(path_type, self.base_dir)
    
    def load_tender_config(self, config_file: Optional[str] = None) -> Dict[str, Any]:
        """加载招标项目配置"""
        if config_file is None:
            # 查找现有的配置文件
            possible_configs = [
                self.config_dir / "tender_config.ini"
            ]
            for config_path in possible_configs:
                if config_path.exists():
                    config_file = str(config_path)
                    break
        
        if config_file and os.path.exists(config_file):
            try:
                import configparser
                config = configparser.ConfigParser()
                config.read(config_file, encoding='utf-8')
                
                result = {}
                for section in config.sections():
                    result[section] = dict(config.items(section))
                
                return result
            except Exception as e:
                print(f"加载招标配置失败: {e}")
                return {}
        
        return {}
    
    def save_config(self, config_name: str, config_data: Dict[str, Any]) -> bool:
        """保存配置到文件"""
        try:
            config_file = self.config_dir / f"{config_name}.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False
    
    def load_config(self, config_name: str) -> Dict[str, Any]:
        """从文件加载配置"""
        try:
            config_file = self.config_dir / f"{config_name}.json"
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"加载配置失败: {e}")
        return {}

# 全局配置实例
config = Config()

def get_config() -> Config:
    """获取配置实例"""
    return config

if __name__ == "__main__":
    print("=== AI标书系统配置信息 ===")
    cfg = get_config()
    print(f"基础目录: {cfg.base_dir}")
    print(f"数据目录: {cfg.data_dir}")
    print(f"API密钥: {cfg.get_default_api_key()[:10]}...")
    print(f"Web端口: {cfg.web_config['port']}")
    print(f"调试模式: {cfg.web_config['debug']}")