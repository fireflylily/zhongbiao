#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用工具函数模块
"""

import os
import hashlib
import tempfile
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional, Union, List, Dict, Any
from werkzeug.utils import secure_filename

def generate_timestamp() -> str:
    """生成时间戳字符串"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def generate_file_hash(file_path: Union[str, Path]) -> str:
    """生成文件MD5哈希值"""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def safe_filename(filename: str, timestamp: bool = True) -> str:
    """生成安全的文件名"""
    # 先提取原始文件的扩展名
    original_name, original_ext = os.path.splitext(filename)

    # 使用werkzeug的secure_filename确保安全，但只处理文件名部分
    safe_name_part = secure_filename(original_name)

    # 如果secure_filename处理后为空（比如纯中文文件名），使用默认名称
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
    
    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
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

def extract_text_preview(text: str, max_length: int = 200) -> str:
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

if __name__ == "__main__":
    # 测试工具函数
    print(f"时间戳: {generate_timestamp()}")
    print(f"安全文件名: {safe_filename('测试文件.docx')}")
    print(f"文件大小: {format_file_size(1024*1024*5)}")
    print("工具函数测试完成")