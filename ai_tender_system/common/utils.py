#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用工具函数模块
"""

import os
import re
import hashlib
import tempfile
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional, Union, List, Dict, Any
from werkzeug.utils import secure_filename
from .constants import BYTES_PER_KB, DEFAULT_CHUNK_READ_SIZE, DEFAULT_TEXT_PREVIEW_LENGTH

def generate_timestamp() -> str:
    """生成时间戳字符串"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def generate_file_hash(file_path: Union[str, Path]) -> str:
    """生成文件MD5哈希值"""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(DEFAULT_CHUNK_READ_SIZE), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def safe_filename(filename: str, timestamp: bool = True) -> str:
    """
    生成安全的文件名，支持中文

    Args:
        filename: 原始文件名
        timestamp: 是否添加时间戳前缀

    Returns:
        安全的文件名，保留中文但移除文件系统危险字符
    """
    # 先提取原始文件的扩展名
    original_name, original_ext = os.path.splitext(filename)

    # 移除文件系统危险字符：/ \ : * ? " < > |
    # 但保留中文、字母、数字、空格、下划线、连字符、圆括号
    safe_name_part = re.sub(r'[/\\:*?"<>|]', '', original_name)
    safe_name_part = safe_name_part.strip()

    # 如果处理后为空，使用默认名称
    if not safe_name_part:
        safe_name_part = "document"

    if timestamp:
        # 添加时间戳避免冲突，保留原始扩展名
        safe_name = f"{generate_timestamp()}_{safe_name_part}{original_ext}"
    else:
        safe_name = f"{safe_name_part}{original_ext}"

    return safe_name

def allowed_file(filename: str, allowed_extensions: set) -> bool:
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def ensure_dir(directory: Union[str, Path]) -> Path:
    """确保目录存在"""
    dir_path = Path(directory)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path

def cleanup_temp_files(temp_dir: Union[str, Path], max_age_hours: int = 24) -> int:
    """清理临时文件"""
    temp_path = Path(temp_dir)
    if not temp_path.exists():
        return 0
    
    cleaned_count = 0
    cutoff_time = datetime.now().timestamp() - (max_age_hours * 3600)
    
    for file_path in temp_path.iterdir():
        if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
            try:
                file_path.unlink()
                cleaned_count += 1
            except Exception:
                pass  # 忽略删除失败的文件
    
    return cleaned_count

def create_temp_copy(source_file: Union[str, Path], temp_dir: Optional[Union[str, Path]] = None) -> Path:
    """创建文件的临时副本"""
    source_path = Path(source_file)
    
    if temp_dir:
        temp_path = ensure_dir(temp_dir)
    else:
        temp_path = Path(tempfile.gettempdir())
    
    temp_file = temp_path / f"temp_{generate_timestamp()}_{source_path.name}"
    shutil.copy2(source_path, temp_file)
    
    return temp_file

def format_file_size(size_bytes: int) -> str:
    """格式化文件大小"""
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(size_bytes)

    while size >= BYTES_PER_KB and i < len(size_names) - 1:
        size /= BYTES_PER_KB
        i += 1

    return f"{size:.2f} {size_names[i]}"

def validate_file_type(file_path: Union[str, Path], expected_types: List[str]) -> bool:
    """验证文件类型（基于内容而非扩展名）"""
    try:
        import magic
        file_type = magic.from_file(str(file_path), mime=True)
        return any(expected_type in file_type for expected_type in expected_types)
    except ImportError:
        # 如果没有python-magic库，回退到扩展名检查
        file_path = Path(file_path)
        extension = file_path.suffix.lower().lstrip('.')
        extension_to_mime = {
            'pdf': 'application/pdf',
            'doc': 'application/msword',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'txt': 'text/plain',
            'png': 'image/png',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'gif': 'image/gif'
        }
        file_mime = extension_to_mime.get(extension, '')
        return any(expected_type in file_mime for expected_type in expected_types)

def extract_text_preview(text: str, max_length: int = DEFAULT_TEXT_PREVIEW_LENGTH) -> str:
    """提取文本预览"""
    if len(text) <= max_length:
        return text
    
    # 尽量在句号处截断
    preview = text[:max_length]
    last_period = preview.rfind('。')
    if last_period > max_length * 0.5:  # 如果句号位置合理
        preview = preview[:last_period + 1]
    else:
        preview = preview + "..."
    
    return preview

def merge_configs(*configs: Dict[str, Any]) -> Dict[str, Any]:
    """合并多个配置字典"""
    merged = {}
    for config in configs:
        if config:
            merged.update(config)
    return merged

def sanitize_json_value(value: Any) -> Any:
    """清理JSON值，确保可序列化"""
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    elif isinstance(value, (list, tuple)):
        return [sanitize_json_value(item) for item in value]
    elif isinstance(value, dict):
        return {k: sanitize_json_value(v) for k, v in value.items()}
    else:
        return str(value)

def batch_process_files(file_list: List[Path], processor_func, max_workers: int = 4):
    """批量处理文件（并发）"""
    from concurrent.futures import ThreadPoolExecutor, as_completed

    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_file = {executor.submit(processor_func, file_path): file_path
                         for file_path in file_list}

        for future in as_completed(future_to_file):
            file_path = future_to_file[future]
            try:
                result = future.result()
                results.append({'file': file_path, 'result': result, 'success': True})
            except Exception as e:
                results.append({'file': file_path, 'error': str(e), 'success': False})

    return results

# ========================================
# 路径处理工具方法
# ========================================

def get_project_root() -> Path:
    """
    获取项目根目录

    Returns:
        项目根目录的Path对象
        例如: /Users/lvhe/Downloads/zhongbiao/zhongbiao
    """
    # 从当前文件(common/utils.py)向上2级到达项目根
    return Path(__file__).parent.parent

def to_relative_path(absolute_path: Union[str, Path], base_path: Optional[Path] = None) -> str:
    """
    将绝对路径转换为相对于项目根目录（或指定base_path）的路径

    Args:
        absolute_path: 绝对路径
        base_path: 基准路径（可选，默认为项目根目录）

    Returns:
        相对路径字符串

    Examples:
        输入: /Users/lvhe/.../zhongbiao/ai_tender_system/data/uploads/xxx.docx
        输出: ai_tender_system/data/uploads/xxx.docx
    """
    abs_path = Path(absolute_path)
    base = base_path or get_project_root()

    try:
        # 计算相对路径
        relative = abs_path.relative_to(base)
        return str(relative)
    except ValueError:
        # 如果路径不在base_path下，返回绝对路径（兼容处理）
        return str(abs_path)

def to_absolute_path(relative_path: Union[str, Path], base_path: Optional[Path] = None) -> Path:
    """
    将相对路径转换为绝对路径

    Args:
        relative_path: 相对路径
        base_path: 基准路径（可选，默认为项目根目录）

    Returns:
        绝对路径的Path对象

    Examples:
        输入: ai_tender_system/data/uploads/xxx.docx
        输出: /Users/lvhe/.../zhongbiao/ai_tender_system/data/uploads/xxx.docx
    """
    base = base_path or get_project_root()
    return base / relative_path

def resolve_file_path(file_path: Union[str, Path], logger=None) -> Optional[Path]:
    """
    智能解析文件路径（自动处理相对路径和绝对路径）

    功能:
    1. 如果是绝对路径且存在，直接返回
    2. 如果是相对路径，尝试从项目根目录解析
    3. 支持多种相对路径格式（data/..., ai_tender_system/data/...）

    Args:
        file_path: 原始文件路径（可能是相对路径或绝对路径）
        logger: 可选的日志记录器，用于输出详细诊断信息

    Returns:
        解析后的绝对路径Path对象，如果无法解析返回None

    Examples:
        输入: data/uploads/xxx.jpg (相对路径)
        输出: /Users/.../zhongbiao/ai_tender_system/data/uploads/xxx.jpg

        输入: /Users/.../xxx.jpg (绝对路径)
        输出: /Users/.../xxx.jpg
    """
    try:
        if not file_path:
            if logger:
                logger.warning("resolve_file_path: 输入路径为空")
            return None

        path_obj = Path(file_path)
        project_root = get_project_root()

        if logger:
            logger.info(f"resolve_file_path: 输入路径={file_path}, 项目根={project_root}")

        # 情况1: 已经是绝对路径且存在
        if path_obj.is_absolute():
            exists = path_obj.exists()
            if logger:
                logger.info(f"resolve_file_path: 绝对路径检测 - 存在={exists}, 路径={path_obj}")
            return path_obj if exists else None

        # 情况2: 相对路径，尝试多种解析方式
        # 2.1 直接从项目根解析: ai_tender_system/data/...
        resolved = project_root / file_path
        if logger:
            logger.debug(f"resolve_file_path: 尝试路径1={resolved}, 存在={resolved.exists()}")
        if resolved.exists():
            if logger:
                logger.info(f"resolve_file_path: ✅ 成功解析(方式1)={resolved}")
            return resolved

        # 2.2 添加 ai_tender_system 前缀: data/... -> ai_tender_system/data/...
        if not str(file_path).startswith('ai_tender_system/'):
            resolved = project_root / 'ai_tender_system' / file_path
            if logger:
                logger.debug(f"resolve_file_path: 尝试路径2={resolved}, 存在={resolved.exists()}")
            if resolved.exists():
                if logger:
                    logger.info(f"resolve_file_path: ✅ 成功解析(方式2)={resolved}")
                return resolved

        # 2.3 去除 ai_tender_system 前缀（如果有）
        file_path_str = str(file_path)
        if file_path_str.startswith('ai_tender_system/'):
            resolved = project_root / file_path_str[len('ai_tender_system/'):]
            if logger:
                logger.debug(f"resolve_file_path: 尝试路径3={resolved}, 存在={resolved.exists()}")
            if resolved.exists():
                if logger:
                    logger.info(f"resolve_file_path: ✅ 成功解析(方式3)={resolved}")
                return resolved

        # 无法解析
        if logger:
            logger.error(f"resolve_file_path: ❌ 所有解析方式均失败 - 输入={file_path}, 项目根={project_root}")
        return None

    except Exception as e:
        if logger:
            logger.exception(f"resolve_file_path: 发生异常 - 输入={file_path}, 错误={e}")
        return None

if __name__ == "__main__":
    # 测试工具函数
    print(f"时间戳: {generate_timestamp()}")
    print(f"安全文件名: {safe_filename('测试文件.docx')}")
    print(f"文件大小: {format_file_size(1024*1024*5)}")
    print("工具函数测试完成")