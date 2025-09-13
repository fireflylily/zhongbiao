# -*- coding: utf-8 -*-
"""
统一配置管理模块
解决硬编码API密钥和分散配置的问题
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class LLMConfig:
    """LLM配置"""
    api_key: str
    base_url: str = "https://api.oaipro.com/v1/chat/completions"
    model: str = "gpt-4o-mini"
    max_tokens: int = 2000
    timeout: int = 90
    max_retries: int = 3


@dataclass
class AppConfig:
    """应用配置"""
    log_level: str = "INFO"
    log_dir: str = "logs"
    max_file_size: str = "50MB"
    upload_dir: str = "uploads"
    output_dir: str = "outputs"


class ConfigManager:
    """统一配置管理器"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or self._get_default_config_file()
        self._config_data = {}
        self._load_config()
    
    def _get_default_config_file(self) -> str:
        """获取默认配置文件路径"""
        project_root = Path(__file__).parent.parent
        return str(project_root / "configs" / "app_config.yaml")
    
    def _load_config(self):
        """加载配置文件"""
        # 首先尝试从环境变量加载
        self._load_from_env()
        
        # 然后尝试从配置文件加载（如果存在）
        if os.path.exists(self.config_file):
            self._load_from_file()
        else:
            # 如果配置文件不存在，创建默认配置
            self._create_default_config()
    
    def _load_from_env(self):
        """从环境变量加载配置"""
        # LLM配置
        api_key = os.getenv('SHIHUANG_API_KEY')
        if not api_key:
            # 如果环境变量中没有，尝试从其他常见的环境变量名
            api_key = os.getenv('OPENAI_API_KEY') or os.getenv('API_KEY')
        
        if not api_key:
            raise ValueError(
                "API密钥未找到！请设置环境变量：\n"
                "export SHIHUANG_API_KEY='your-api-key-here'\n"
                "或在配置文件中设置"
            )
        
        self._config_data.update({
            'llm': {
                'api_key': api_key,
                'base_url': os.getenv('LLM_BASE_URL', 'https://api.oaipro.com/v1/chat/completions'),
                'model': os.getenv('LLM_MODEL', 'gpt-4o-mini'),
                'max_tokens': int(os.getenv('LLM_MAX_TOKENS', '2000')),
                'timeout': int(os.getenv('LLM_TIMEOUT', '90')),
                'max_retries': int(os.getenv('LLM_MAX_RETRIES', '3'))
            },
            'app': {
                'log_level': os.getenv('LOG_LEVEL', 'INFO'),
                'log_dir': os.getenv('LOG_DIR', 'logs'),
                'max_file_size': os.getenv('MAX_FILE_SIZE', '50MB'),
                'upload_dir': os.getenv('UPLOAD_DIR', 'uploads'),
                'output_dir': os.getenv('OUTPUT_DIR', 'outputs')
            }
        })
    
    def _load_from_file(self):
        """从配置文件加载配置"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                file_config = yaml.safe_load(f)
            
            # 合并文件配置（环境变量优先级更高）
            self._merge_config(file_config)
            
        except Exception as e:
            print(f"警告：无法加载配置文件 {self.config_file}: {e}")
    
    def _merge_config(self, file_config: Dict[str, Any]):
        """合并配置，环境变量优先级更高"""
        for section, values in file_config.items():
            if section in self._config_data:
                # 只有当环境变量中没有设置时，才使用文件中的值
                for key, value in values.items():
                    if key not in self._config_data[section] or self._config_data[section][key] is None:
                        self._config_data[section][key] = value
            else:
                self._config_data[section] = values
    
    def _create_default_config(self):
        """创建默认配置文件"""
        default_config = {
            'llm': {
                'base_url': 'https://api.oaipro.com/v1/chat/completions',
                'model': 'gpt-4o-mini',
                'max_tokens': 2000,
                'timeout': 90,
                'max_retries': 3
            },
            'app': {
                'log_level': 'INFO',
                'log_dir': 'logs',
                'max_file_size': '50MB',
                'upload_dir': 'uploads',
                'output_dir': 'outputs'
            }
        }
        
        # 确保配置目录存在
        config_dir = Path(self.config_file).parent
        config_dir.mkdir(parents=True, exist_ok=True)
        
        # 写入默认配置文件
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(default_config, f, default_flow_style=False, 
                         allow_unicode=True, indent=2)
            print(f"已创建默认配置文件: {self.config_file}")
        except Exception as e:
            print(f"警告：无法创建配置文件: {e}")
    
    @property
    def llm(self) -> LLMConfig:
        """获取LLM配置"""
        llm_data = self._config_data.get('llm', {})
        return LLMConfig(
            api_key=llm_data.get('api_key', ''),
            base_url=llm_data.get('base_url', 'https://api.oaipro.com/v1/chat/completions'),
            model=llm_data.get('model', 'gpt-4o-mini'),
            max_tokens=llm_data.get('max_tokens', 2000),
            timeout=llm_data.get('timeout', 90),
            max_retries=llm_data.get('max_retries', 3)
        )
    
    @property
    def app(self) -> AppConfig:
        """获取应用配置"""
        app_data = self._config_data.get('app', {})
        return AppConfig(
            log_level=app_data.get('log_level', 'INFO'),
            log_dir=app_data.get('log_dir', 'logs'),
            max_file_size=app_data.get('max_file_size', '50MB'),
            upload_dir=app_data.get('upload_dir', 'uploads'),
            output_dir=app_data.get('output_dir', 'outputs')
        )
    
    def get(self, key: str, default=None) -> Any:
        """获取配置值，支持点号分隔的嵌套key"""
        keys = key.split('.')
        value = self._config_data
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def validate(self) -> bool:
        """验证配置是否有效"""
        errors = []
        
        # 验证API密钥
        if not self.llm.api_key:
            errors.append("API密钥未设置")
        
        # 验证日志级别
        valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if self.app.log_level not in valid_log_levels:
            errors.append(f"日志级别无效: {self.app.log_level}")
        
        if errors:
            print("配置验证失败:")
            for error in errors:
                print(f"  - {error}")
            return False
        
        return True


# 全局配置实例
_config_manager = None


def get_config() -> ConfigManager:
    """获取全局配置管理器实例"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def reload_config(config_file: Optional[str] = None) -> ConfigManager:
    """重新加载配置"""
    global _config_manager
    _config_manager = ConfigManager(config_file)
    return _config_manager


if __name__ == "__main__":
    # 测试配置管理器
    try:
        config = get_config()
        
        print("配置加载测试:")
        print(f"LLM模型: {config.llm.model}")
        print(f"日志级别: {config.app.log_level}")
        print(f"API密钥长度: {len(config.llm.api_key) if config.llm.api_key else 0}")
        
        if config.validate():
            print("✅ 配置验证通过")
        else:
            print("❌ 配置验证失败")
            
    except Exception as e:
        print(f"❌ 配置测试失败: {e}")