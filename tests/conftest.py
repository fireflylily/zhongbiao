"""
Pytest 配置和全局 Fixtures

这个文件定义了所有测试都可以使用的共享 fixtures
"""

import os
import sys
import tempfile
from pathlib import Path
from typing import Generator

import pytest
from flask import Flask
from flask.testing import FlaskClient

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


# ============================================================================
# 应用级别 Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def app() -> Generator[Flask, None, None]:
    """
    创建 Flask 测试应用
    scope="session" 表示整个测试会话只创建一次
    """
    from ai_tender_system.web.app import create_app

    # 创建测试应用
    test_app = create_app()

    # 配置测试模式
    test_app.config.update({
        "TESTING": True,
        "DEBUG": False,
        "WTF_CSRF_ENABLED": False,  # 测试时禁用 CSRF
        "SECRET_KEY": "test-secret-key-for-testing-only",
    })

    yield test_app

    # 清理（如果需要）


@pytest.fixture(scope="function")
def client(app: Flask) -> FlaskClient:
    """
    创建 Flask 测试客户端
    scope="function" 表示每个测试函数都会创建新的客户端
    """
    return app.test_client()


@pytest.fixture(scope="function")
def runner(app: Flask):
    """
    创建 Flask CLI 测试运行器
    """
    return app.test_cli_runner()


# ============================================================================
# 数据库 Fixtures
# ============================================================================

@pytest.fixture(scope="function")
def temp_db() -> Generator[Path, None, None]:
    """
    创建临时测试数据库
    测试结束后自动删除
    """
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)

    yield db_path

    # 清理：删除临时数据库
    if db_path.exists():
        db_path.unlink()


@pytest.fixture(scope="function")
def init_db(temp_db: Path):
    """
    初始化测试数据库（创建表结构）
    """
    from ai_tender_system.common.database import Database

    db = Database(str(temp_db))

    # 读取并执行所有 schema 文件
    schema_dir = project_root / "ai_tender_system" / "database"
    schema_files = [
        "knowledge_base_schema.sql",
        "case_library_schema.sql",
        "tender_processing_schema.sql",
        "company_qualifications_schema.sql",
    ]

    for schema_file in schema_files:
        schema_path = schema_dir / schema_file
        if schema_path.exists():
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
                db.execute_script(schema_sql)

    return db


# ============================================================================
# 文件系统 Fixtures
# ============================================================================

@pytest.fixture(scope="function")
def temp_dir() -> Generator[Path, None, None]:
    """
    创建临时测试目录
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture(scope="function")
def sample_pdf_file(temp_dir: Path) -> Path:
    """
    创建示例 PDF 文件（用于测试）
    """
    pdf_path = temp_dir / "sample.pdf"
    # 这里可以创建一个简单的 PDF 文件
    pdf_path.write_text("Sample PDF content for testing")
    return pdf_path


@pytest.fixture(scope="function")
def sample_word_file(temp_dir: Path) -> Path:
    """
    创建示例 Word 文件（用于测试）
    """
    word_path = temp_dir / "sample.docx"
    word_path.write_text("Sample Word content for testing")
    return word_path


# ============================================================================
# Mock Fixtures
# ============================================================================

@pytest.fixture
def mock_llm_response(mocker):
    """
    Mock AI 模型响应（避免实际调用 API）
    """
    mock_response = {
        "choices": [{
            "message": {
                "content": "这是一个模拟的AI响应，用于测试。"
            }
        }]
    }

    # Mock LLM 客户端
    mocker.patch(
        'ai_tender_system.common.llm_client.LLMClient.chat',
        return_value=mock_response
    )

    return mock_response


@pytest.fixture
def mock_vector_search(mocker):
    """
    Mock 向量搜索（避免实际的向量计算）
    """
    mock_results = [
        {"content": "相关文档1", "score": 0.95},
        {"content": "相关文档2", "score": 0.88},
    ]

    mocker.patch(
        'ai_tender_system.modules.vector_engine.engine_manager.VectorEngineManager.search',
        return_value=mock_results
    )

    return mock_results


# ============================================================================
# 测试数据 Fixtures
# ============================================================================

@pytest.fixture
def sample_tender_text() -> str:
    """
    示例招标文本
    """
    return """
    项目名称：智慧城市建设项目
    投标截止时间：2025年12月31日17:00
    项目预算：500万元

    技术要求：
    1. 提供完整的系统架构设计
    2. 支持至少1000个并发用户
    3. 数据安全符合国家标准

    资质要求：
    1. 具有软件企业认证
    2. ISO9001质量管理体系认证
    3. 3年以上相关项目经验
    """


@pytest.fixture
def sample_company_info() -> dict:
    """
    示例公司信息
    """
    return {
        "company_id": 1,
        "company_name": "测试科技有限公司",
        "industry": "软件开发",
        "established_year": 2018,
        "certifications": ["ISO9001", "CMMI3"],
        "employee_count": 150,
    }


@pytest.fixture
def sample_document_metadata() -> dict:
    """
    示例文档元数据
    """
    return {
        "document_id": "doc_001",
        "title": "测试文档",
        "category": "技术方案",
        "tags": ["AI", "大数据", "云计算"],
        "upload_date": "2025-01-01",
        "file_type": "pdf",
    }


# ============================================================================
# Session Fixtures（会话级别配置）
# ============================================================================

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """
    设置测试环境（自动执行）
    autouse=True 表示自动应用到所有测试
    """
    # 设置测试环境变量
    os.environ["TESTING"] = "1"
    os.environ["DEBUG"] = "0"

    yield

    # 清理环境变量
    os.environ.pop("TESTING", None)
    os.environ.pop("DEBUG", None)


@pytest.fixture(scope="session")
def test_config():
    """
    测试配置字典
    """
    return {
        "max_file_size": 10 * 1024 * 1024,  # 10MB
        "allowed_extensions": [".pdf", ".docx", ".xlsx"],
        "chunk_size": 500,
        "overlap": 50,
    }


# ============================================================================
# Pytest Hooks（钩子函数）
# ============================================================================

def pytest_configure(config):
    """
    Pytest 配置钩子
    在测试开始前执行
    """
    # 注册自定义标记
    config.addinivalue_line(
        "markers", "unit: 标记单元测试"
    )
    config.addinivalue_line(
        "markers", "integration: 标记集成测试"
    )
    config.addinivalue_line(
        "markers", "slow: 标记慢速测试"
    )


def pytest_collection_modifyitems(config, items):
    """
    修改测试收集项
    可以为测试自动添加标记
    """
    for item in items:
        # 为在 tests/unit/ 下的测试自动添加 @pytest.mark.unit
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        # 为在 tests/integration/ 下的测试自动添加 @pytest.mark.integration
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        # 为在 tests/e2e/ 下的测试自动添加 @pytest.mark.e2e
        elif "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)
