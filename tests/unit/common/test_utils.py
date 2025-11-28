"""
测试common/utils.py中的工具函数
"""

import pytest
from pathlib import Path
from ai_tender_system.common.utils import (
    safe_filename,
    ensure_dir,
    format_file_size,
    extract_text_preview,
    allowed_file,
    generate_timestamp
)


@pytest.mark.unit
class TestSafeFilename:
    """测试安全文件名生成"""

    def test_basic_filename(self):
        """测试基本文件名"""
        result = safe_filename("test.txt", timestamp=False)
        assert "test.txt" in result

    def test_with_timestamp(self):
        """测试带时间戳的文件名"""
        result = safe_filename("test.txt", timestamp=True)
        assert "test.txt" in result
        # 时间戳格式: YYYYMMDD_HHMMSS
        assert len(result) > len("test.txt")

    def test_preserve_chinese(self):
        """测试保留中文字符"""
        result = safe_filename("测试文件.txt", timestamp=False)
        assert "测试文件" in result


@pytest.mark.unit
class TestEnsureDir:
    """测试目录创建函数"""

    def test_create_new_directory(self, temp_dir):
        """测试创建新目录"""
        new_dir = temp_dir / "test_folder"
        result = ensure_dir(new_dir)
        assert result.exists()
        assert result.is_dir()

    def test_existing_directory(self, temp_dir):
        """测试已存在的目录"""
        new_dir = temp_dir / "existing"
        new_dir.mkdir()
        result = ensure_dir(new_dir)  # 不应抛出异常
        assert result.exists()

    def test_nested_directories(self, temp_dir):
        """测试嵌套目录创建"""
        nested_dir = temp_dir / "level1" / "level2" / "level3"
        result = ensure_dir(nested_dir)
        assert result.exists()


@pytest.mark.unit
class TestFormatFileSize:
    """测试文件大小格式化"""

    def test_bytes(self):
        """测试字节"""
        assert format_file_size(100) == "100.00 B"

    def test_kilobytes(self):
        """测试KB"""
        assert format_file_size(1024) == "1.00 KB"
        assert format_file_size(1536) == "1.50 KB"

    def test_megabytes(self):
        """测试MB"""
        assert format_file_size(1024 * 1024) == "1.00 MB"

    def test_gigabytes(self):
        """测试GB"""
        assert format_file_size(1024 * 1024 * 1024) == "1.00 GB"

    def test_zero_size(self):
        """测试零大小"""
        assert format_file_size(0) == "0 B"


@pytest.mark.unit
class TestExtractTextPreview:
    """测试文本预览提取"""

    def test_short_text(self):
        """测试短文本不截断"""
        text = "短文本"
        result = extract_text_preview(text, max_length=100)
        assert result == text

    def test_long_text(self):
        """测试长文本截断"""
        text = "这是一段很长的文本" * 20
        result = extract_text_preview(text, max_length=50)
        assert len(result) <= 53  # 50 + "..."
        assert result.endswith("...")


@pytest.mark.unit
class TestAllowedFile:
    """测试文件类型验证"""

    def test_allowed_extension(self):
        """测试允许的扩展名"""
        assert allowed_file("test.pdf", {'pdf', 'docx'}) == True

    def test_disallowed_extension(self):
        """测试不允许的扩展名"""
        assert allowed_file("test.exe", {'pdf', 'docx'}) == False

    def test_case_insensitive(self):
        """测试扩展名大小写不敏感"""
        assert allowed_file("test.PDF", {'pdf'}) == True


@pytest.mark.unit
class TestGenerateTimestamp:
    """测试时间戳生成"""

    def test_timestamp_format(self):
        """测试时间戳格式"""
        result = generate_timestamp()
        assert len(result) == 15  # YYYYMMDD_HHMMSS
        assert "_" in result
