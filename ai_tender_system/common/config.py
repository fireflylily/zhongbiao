#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一配置管理模块
整合所有系统配置到单一入口
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# 配置基础日志(在logger模块加载前使用)
_basic_logger = logging.getLogger("config")
_basic_logger.setLevel(logging.INFO)
if not _basic_logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    _basic_logger.addHandler(_handler)

# 工具函数：清理环境变量值
def clean_env_value(value: str) -> str:
    """
    清理环境变量值，移除不可见字符

    Args:
        value: 原始环境变量值

    Returns:
        清理后的值
    """
    if not value:
        return value

    # 移除前后空格、换行符、制表符等
    cleaned = value.strip()

    # 检测并警告包含不可见字符的情况
    if cleaned != value:
        _basic_logger.warning(
            f"环境变量包含不可见字符 (长度: {len(value)} → {len(cleaned)}): "
            f"{repr(value)[:50]}..."
        )

    return cleaned

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
            _basic_logger.info(f"加载环境变量文件: {env_file}")
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = clean_env_value(value.strip())  # 使用清理函数
                        # 设置环境变量（覆盖现有值）
                        os.environ[key] = value
            return

    _basic_logger.warning("警告: 未找到.env文件")

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
            'api_key': clean_env_value(os.getenv('DEFAULT_API_KEY', '')),
            'api_endpoint': clean_env_value(os.getenv('API_ENDPOINT', 'https://api.oaipro.com/v1/chat/completions')),
            'model_name': clean_env_value(os.getenv('MODEL_NAME', 'gpt-5')),
            'max_tokens': int(os.getenv('MAX_TOKENS', '1000')),
            'timeout': int(os.getenv('API_TIMEOUT', '30'))
        }

        # 多模型配置
        self.multi_model_config = {
            # 联通元景系列模型
            'yuanjing-deepseek-v3': {
                'access_token': clean_env_value(os.getenv('ACCESS_TOKEN', '')),
                'base_url': clean_env_value(os.getenv('UNICOM_BASE_URL', 'https://maas-api.ai-yuanjing.com/openapi/compatible-mode/v1')),
                'model_name': 'deepseek-v3',
                'max_tokens': int(os.getenv('UNICOM_MAX_TOKENS', '1000')),
                'timeout': int(os.getenv('UNICOM_TIMEOUT', '30')),
                'provider': 'China Unicom',
                'display_name': '元景-DeepSeek-V3',
                'description': '通用对话模型，平衡性能与速度，适合日常标书内容生成'
            },
            'yuanjing-qwen3-235b': {
                'access_token': clean_env_value(os.getenv('ACCESS_TOKEN', '')),
                'base_url': clean_env_value(os.getenv('UNICOM_BASE_URL', 'https://maas-api.ai-yuanjing.com/openapi/compatible-mode/v1')),
                'model_name': 'qwen3-235b-a22b',
                'max_tokens': int(os.getenv('UNICOM_MAX_TOKENS', '1000')),
                'timeout': int(os.getenv('UNICOM_TIMEOUT', '30')),
                'provider': 'China Unicom',
                'display_name': '元景-通义千问3-235B',
                'description': '最大参数模型，文本生成质量最高，适合复杂商务文档和标书写作'
            },
            'yuanjing-glm-rumination': {
                'access_token': clean_env_value(os.getenv('ACCESS_TOKEN', '')),
                'base_url': clean_env_value(os.getenv('UNICOM_BASE_URL', 'https://maas-api.ai-yuanjing.com/openapi/compatible-mode/v1')),
                'model_name': 'glm-z1-rumination-32b-0414',
                'max_tokens': int(os.getenv('UNICOM_MAX_TOKENS', '1000')),
                'timeout': int(os.getenv('UNICOM_TIMEOUT', '30')),
                'provider': 'China Unicom',
                'display_name': '元景-智谱GLM思考版',
                'description': '深度思考推理模型，逻辑严密，适合技术方案和解决方案论述'
            },
            'yuanjing-70b-chat': {
                'access_token': clean_env_value(os.getenv('ACCESS_TOKEN', '')),
                'base_url': clean_env_value(os.getenv('UNICOM_BASE_URL', 'https://maas-api.ai-yuanjing.com/openapi/compatible-mode/v1')),
                'model_name': 'yuanjing-70b-chat',
                'max_tokens': int(os.getenv('UNICOM_MAX_TOKENS', '1000')),
                'timeout': int(os.getenv('UNICOM_TIMEOUT', '30')),
                'provider': 'China Unicom',
                'display_name': '元景-70B对话版',
                'description': '联通自研70B模型，可能针对政企场景优化，适合政府采购项目'
            },
            'yuanjing-ernie-300b': {
                'access_token': clean_env_value(os.getenv('ACCESS_TOKEN', '')),
                'base_url': clean_env_value(os.getenv('UNICOM_BASE_URL', 'https://maas-api.ai-yuanjing.com/openapi/compatible-mode/v1')),
                'model_name': 'ernie-4.5-300b-a47b',
                'max_tokens': int(os.getenv('UNICOM_MAX_TOKENS', '1000')),
                'timeout': int(os.getenv('UNICOM_TIMEOUT', '30')),
                'provider': 'China Unicom',
                'display_name': '元景-文心大模型4.5',
                'description': '百度文心300B大模型，中文商务写作专长，政府采购语言风格优秀'
            },
            'yuanjing-deepseek-function': {
                'access_token': clean_env_value(os.getenv('ACCESS_TOKEN', '')),
                'base_url': clean_env_value(os.getenv('UNICOM_BASE_URL', 'https://maas-api.ai-yuanjing.com/openapi/compatible-mode/v1')),
                'model_name': 'deepseek-v3-functioncall',
                'max_tokens': int(os.getenv('UNICOM_MAX_TOKENS', '1000')),
                'timeout': int(os.getenv('UNICOM_TIMEOUT', '30')),
                'provider': 'China Unicom',
                'display_name': '元景-DeepSeek函数调用版',
                'description': '结构化输出能力强，适合生成规范格式的标书内容和表格'
            },
            # 始皇API配置 - 所有模型共享同一个API Key和Endpoint
            'shihuang-gpt5': {
                'api_key': clean_env_value(os.getenv('SHIHUANG_API_KEY', '')),
                'api_endpoint': clean_env_value(os.getenv('SHIHUANG_API_ENDPOINT', 'https://api.oaipro.com/v1/chat/completions')),
                'model_name': 'gpt-5',
                'max_tokens': int(os.getenv('SHIHUANG_MAX_TOKENS', '2000')),
                'temperature': float(os.getenv('SHIHUANG_TEMPERATURE', '0.3')),
                'timeout': int(os.getenv('SHIHUANG_TIMEOUT', '60')),
                'provider': 'Shihuang',
                'display_name': '始皇-GPT5',
                'description': 'OpenAI最新GPT-5模型，最强推理能力，适合复杂技术方案'
            },
            'shihuang-claude-sonnet-45': {
                'api_key': clean_env_value(os.getenv('SHIHUANG_API_KEY', '')),
                'api_endpoint': clean_env_value(os.getenv('SHIHUANG_API_ENDPOINT', 'https://api.oaipro.com/v1/chat/completions')),
                'model_name': 'claude-sonnet-4-20250514',
                'max_tokens': int(os.getenv('SHIHUANG_MAX_TOKENS', '2000')),
                'temperature': 1.0,  # Claude Sonnet 4.5 只支持默认温度1.0
                'supports_temperature': False,  # ✅ Claude Sonnet 4.5 不支持自定义temperature参数
                'timeout': int(os.getenv('SHIHUANG_TIMEOUT', '60')),
                'provider': 'Shihuang',
                'display_name': '始皇-Claude Sonnet 4.5',
                'description': 'Anthropic Claude Sonnet 4.5，卓越的标书写作和文档生成能力（注：仅支持默认温度1.0）'
            },
            'shihuang-gpt4o-mini': {
                'api_key': clean_env_value(os.getenv('SHIHUANG_API_KEY', '')),
                'api_endpoint': clean_env_value(os.getenv('SHIHUANG_API_ENDPOINT', 'https://api.oaipro.com/v1/chat/completions')),
                'model_name': 'gpt-4o-mini',
                'max_tokens': int(os.getenv('SHIHUANG_MAX_TOKENS', '1000')),
                'temperature': 1.0,  # GPT-4o-mini 只支持默认温度1.0
                'supports_temperature': False,  # ✅ GPT-4o-mini 不支持自定义temperature参数
                'timeout': int(os.getenv('SHIHUANG_TIMEOUT', '60')),
                'provider': 'Shihuang',
                'display_name': '始皇-GPT4o Mini',
                'description': '高效快速的AI模型，适合日常应答和点对点回复（注：仅支持默认温度1.0）'
            },
            # 向后兼容性配置 - 保持原有模型名称可用
            'unicom-yuanjing': {
                'access_token': clean_env_value(os.getenv('ACCESS_TOKEN', '')),
                'base_url': clean_env_value(os.getenv('UNICOM_BASE_URL', 'https://maas-api.ai-yuanjing.com/openapi/compatible-mode/v1')),
                'model_name': clean_env_value(os.getenv('UNICOM_MODEL_NAME', 'deepseek-v3')),
                'max_tokens': int(os.getenv('UNICOM_MAX_TOKENS', '1000')),
                'timeout': int(os.getenv('UNICOM_TIMEOUT', '30')),
                'provider': 'China Unicom',
                'display_name': '联通元景大模型 (兼容)',
                'description': '通用对话模型'
            },
            # Azure OpenAI配置
            'azure-gpt4': {
                'api_key': clean_env_value(os.getenv('AZURE_OPENAI_API_KEY', '')),
                'azure_endpoint': clean_env_value(os.getenv('AZURE_OPENAI_ENDPOINT', '')),
                'azure_deployment': clean_env_value(os.getenv('AZURE_OPENAI_DEPLOYMENT', 'gpt-4')),
                'api_version': clean_env_value(os.getenv('AZURE_OPENAI_API_VERSION', '2024-02-15-preview')),
                'max_tokens': int(os.getenv('AZURE_MAX_TOKENS', '2000')),
                'timeout': int(os.getenv('AZURE_TIMEOUT', '60')),
                'provider': 'Azure OpenAI',
                'display_name': 'Azure GPT-4',
                'description': 'Microsoft Azure部署的GPT-4模型，企业级稳定性和安全性'
            },
            'azure-gpt4o': {
                'api_key': clean_env_value(os.getenv('AZURE_OPENAI_API_KEY', '')),
                'azure_endpoint': clean_env_value(os.getenv('AZURE_OPENAI_ENDPOINT', '')),
                'azure_deployment': clean_env_value(os.getenv('AZURE_OPENAI_DEPLOYMENT_4O', 'gpt-4o')),
                'api_version': clean_env_value(os.getenv('AZURE_OPENAI_API_VERSION', '2024-02-15-preview')),
                'max_tokens': int(os.getenv('AZURE_MAX_TOKENS', '2000')),
                'timeout': int(os.getenv('AZURE_TIMEOUT', '60')),
                'provider': 'Azure OpenAI',
                'display_name': 'Azure GPT-4o',
                'description': 'Azure部署的GPT-4o模型，多模态能力，适合复杂标书处理'
            },
            'azure-gpt35-turbo': {
                'api_key': clean_env_value(os.getenv('AZURE_OPENAI_API_KEY', '')),
                'azure_endpoint': clean_env_value(os.getenv('AZURE_OPENAI_ENDPOINT', '')),
                'azure_deployment': clean_env_value(os.getenv('AZURE_OPENAI_DEPLOYMENT_35', 'gpt-35-turbo')),
                'api_version': clean_env_value(os.getenv('AZURE_OPENAI_API_VERSION', '2024-02-15-preview')),
                'max_tokens': int(os.getenv('AZURE_MAX_TOKENS', '2000')),
                'timeout': int(os.getenv('AZURE_TIMEOUT', '60')),
                'provider': 'Azure OpenAI',
                'display_name': 'Azure GPT-3.5 Turbo',
                'description': 'Azure部署的GPT-3.5模型，快速且经济的AI助手'
            }
        }
        
        # Web配置
        # 标准端口：8110（与Nginx、Docker配置统一）
        self.web_config = {
            'host': os.getenv('WEB_HOST', '0.0.0.0'),
            'port': int(os.getenv('WEB_PORT', '8110')),  # ✅ 统一为8110
            'debug': os.getenv('DEBUG', 'True').lower() == 'true',
            'secret_key': os.getenv('SECRET_KEY', 'ai-tender-system-2025')
        }
        
        # 企业征信API配置
        self.enterprise_credit_config = {
            'ENTERPRISE_CREDIT_BASE_URL': clean_env_value(os.getenv('ENTERPRISE_CREDIT_BASE_URL', '')),
            'ENTERPRISE_CREDIT_CUST_USER_ID': clean_env_value(os.getenv('ENTERPRISE_CREDIT_CUST_USER_ID', '')),
            'ENTERPRISE_CREDIT_API_KEY': clean_env_value(os.getenv('ENTERPRISE_CREDIT_API_KEY', '')),
            'ENTERPRISE_CREDIT_ENCRYPT_KEY': clean_env_value(os.getenv('ENTERPRISE_CREDIT_ENCRYPT_KEY', '')),
            'ENTERPRISE_CREDIT_ENCRYPT_IV': clean_env_value(os.getenv('ENTERPRISE_CREDIT_ENCRYPT_IV', '')),
            'ENTERPRISE_CREDIT_ENCRYPT_METHOD': clean_env_value(os.getenv('ENTERPRISE_CREDIT_ENCRYPT_METHOD', 'aes'))
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

    def get_enterprise_credit_config(self) -> Dict[str, Any]:
        """获取企业征信API配置"""
        return self.enterprise_credit_config.copy()

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项（支持字典式访问）"""
        if hasattr(self, key):
            return getattr(self, key)
        # 尝试从enterprise_credit_config中获取
        if key in self.enterprise_credit_config:
            return self.enterprise_credit_config[key]
        return default

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
                _basic_logger.error(f"加载招标配置失败: {e}")
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
            _basic_logger.error(f"保存配置失败: {e}")
            return False
    
    def load_config(self, config_name: str) -> Dict[str, Any]:
        """从文件加载配置"""
        try:
            config_file = self.config_dir / f"{config_name}.json"
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            _basic_logger.error(f"加载配置失败: {e}")
        return {}

# 全局配置实例
config = Config()

def get_config() -> Config:
    """获取配置实例"""
    return config

if __name__ == "__main__":
    _basic_logger.info("=== AI标书系统配置信息 ===")
    cfg = get_config()
    _basic_logger.info(f"基础目录: {cfg.base_dir}")
    _basic_logger.info(f"数据目录: {cfg.data_dir}")
    _basic_logger.info(f"API密钥: {cfg.get_default_api_key()[:10]}...")
    _basic_logger.info(f"Web端口: {cfg.web_config['port']}")
    _basic_logger.info(f"调试模式: {cfg.web_config['debug']}")