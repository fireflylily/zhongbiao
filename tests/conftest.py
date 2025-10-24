"""
Pytest配置和全局fixtures
"""

import pytest
import tempfile
import sqlite3
from pathlib import Path
import sys

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture(scope="session")
def temp_dir():
    """创建临时目录用于测试"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture(scope="function")
def temp_db(temp_dir):
    """创建临时SQLite数据库"""
    db_path = temp_dir / "test.db"
    conn = sqlite3.connect(str(db_path))
    yield conn
    conn.close()


@pytest.fixture
def mock_env(monkeypatch):
    """模拟环境变量"""
    test_env = {
        'ACCESS_TOKEN': 'test_token_123',
        'OPENAI_API_KEY': 'test_openai_key',
        'SECRET_KEY': 'test_secret_key',
        'DEBUG': 'True'
    }
    for key, value in test_env.items():
        monkeypatch.setenv(key, value)
    return test_env


@pytest.fixture
def mock_config():
    """模拟配置对象"""
    from unittest.mock import MagicMock
    config = MagicMock()
    config.base_dir = Path("/tmp/test_ai_tender")
    config.data_dir = config.base_dir / "data"
    config.upload_dir = config.data_dir / "uploads"
    config.output_dir = config.data_dir / "outputs"

    config.get_path.side_effect = lambda path_type: {
        'base': config.base_dir,
        'data': config.data_dir,
        'upload': config.upload_dir,
        'output': config.output_dir
    }.get(path_type, config.base_dir)

    return config


@pytest.fixture
def sample_tender_text():
    """示例招标文档文本"""
    return """
    招标项目名称:某市政府信息化建设项目
    招标编号:2025-001

    一、项目概况
    本项目旨在建设某市政府信息化平台。

    二、资质要求
    1. 投标人须具有有效的营业执照
    2. 具有信息系统集成及服务资质证书(三级及以上)
    3. 具有ISO9001质量管理体系认证

    三、技术要求
    1. 系统应支持至少1000个并发用户
    """


@pytest.fixture
def sample_company_data():
    """示例公司数据"""
    return {
        'company_id': 1,
        'company_name': '测试科技有限公司',
        'social_credit_code': '91110000123456789X',
        'registered_capital': '5000万元',
        'legal_representative': '张三'
    }
