"""
测试common/config.py配置管理
"""

import pytest
import os
from pathlib import Path
from unittest.mock import patch, MagicMock


@pytest.mark.unit
class TestConfig:
    """测试配置类"""

    def test_config_singleton(self, mock_env):
        """测试配置单例模式"""
        from ai_tender_system.common.config import get_config
        config1 = get_config()
        config2 = get_config()
        assert config1 is config2

    def test_get_path(self, mock_env):
        """测试路径获取"""
        from ai_tender_system.common.config import get_config
        config = get_config()
        
        base_path = config.get_path('base')
        assert isinstance(base_path, Path)
        
        data_path = config.get_path('data')
        assert data_path.name == 'data'

    def test_get_model_config(self, mock_env):
        """测试获取模型配置"""
        from ai_tender_system.common.config import get_config
        config = get_config()
        
        model_config = config.get_model_config('yuanjing-deepseek-v3')
        assert 'access_token' in model_config
        assert 'base_url' in model_config
        assert 'model_name' in model_config

    def test_get_all_model_configs(self, mock_env):
        """测试获取所有模型配置"""
        from ai_tender_system.common.config import get_config
        config = get_config()
        
        all_configs = config.get_all_model_configs()
        assert isinstance(all_configs, dict)
        assert 'yuanjing-deepseek-v3' in all_configs
        assert 'gpt-4o-mini' in all_configs

    def test_web_config(self, mock_env):
        """测试Web配置"""
        from ai_tender_system.common.config import get_config
        config = get_config()
        
        web_config = config.get_web_config()
        assert 'host' in web_config
        assert 'port' in web_config
        assert 'debug' in web_config
        assert 'secret_key' in web_config

    def test_upload_config(self, mock_env):
        """测试上传配置"""
        from ai_tender_system.common.config import get_config
        config = get_config()
        
        upload_config = config.get_upload_config()
        assert 'max_file_size' in upload_config
        assert 'allowed_extensions' in upload_config
        assert upload_config['max_file_size'] == 100 * 1024 * 1024
