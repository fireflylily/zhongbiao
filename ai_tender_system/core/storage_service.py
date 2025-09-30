"""
统一文件存储服务
统一所有上传功能的存储逻辑，为系统提供一致的文件管理接口

设计原则：
1. 存储与业务分离：文件存储作为基础设施，不依赖具体业务逻辑
2. 统一接口：所有上传功能使用相同的存储接口
3. 元数据管理：完整的文件生命周期管理
4. 向下兼容：逐步迁移现有功能，不破坏现有接口

架构层次：
- 业务层：各种上传功能（标书、商务应答、资质等）
- 服务层：FileStorageService（统一存储接口）
- 存储层：文件系统 + 数据库元数据

未来扩展：
- 云存储支持（OSS、S3等）
- 文件版本管理
- 自动备份和清理
- 访问权限控制
"""

import os
import uuid
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, BinaryIO
from dataclasses import dataclass

from ..common.config import get_config
from ..common.database import get_db_connection

# 初始化配置实例
config = get_config()


@dataclass
class FileMetadata:
    """文件元数据"""
    file_id: str
    original_name: str
    safe_name: str
    file_path: str
    file_size: int
    mime_type: str
    category: str
    business_type: str
    upload_time: datetime
    user_id: Optional[str] = None
    company_id: Optional[int] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    checksum: Optional[str] = None


class FileStorageService:
    """
    统一文件存储服务

    负责所有文件的存储、检索、管理和生命周期控制
    """

    def __init__(self):
        # 使用upload路径作为存储根目录
        self.storage_root = Path(config.get_path('upload'))
        self.ensure_storage_directories()

    def ensure_storage_directories(self):
        """确保存储目录结构存在"""
        categories = [
            'tender_documents',      # 招标文档
            'business_templates',    # 商务应答模板
            'point_to_point',       # 点对点应答文档
            'tech_proposals',       # 技术方案文档
            'qualifications',       # 资质文件
            'financial_docs',       # 财务文档
            'product_docs',         # 产品文档
            'personnel_docs',       # 人员档案
            'processed_results',    # 处理结果文件
            'temp'                  # 临时文件
        ]

        for category in categories:
            category_path = self.storage_root / category
            category_path.mkdir(parents=True, exist_ok=True)

    def store_file(self,
                   file_obj: BinaryIO,
                   original_name: str,
                   category: str,
                   business_type: str,
                   **metadata) -> FileMetadata:
        """
        存储文件并记录元数据

        Args:
            file_obj: 文件对象
            original_name: 原始文件名
            category: 文件分类
            business_type: 业务类型
            **metadata: 额外的元数据

        Returns:
            FileMetadata: 文件元数据对象
        """
        # 生成唯一文件ID
        file_id = str(uuid.uuid4())

        # 生成安全文件名
        safe_name = self._generate_safe_filename(original_name, file_id)

        # 构建存储路径
        file_path = self._build_file_path(category, safe_name)

        # 读取文件内容并计算校验和
        file_content = file_obj.read()
        file_size = len(file_content)
        checksum = hashlib.sha256(file_content).hexdigest()

        # 存储文件
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'wb') as f:
            f.write(file_content)

        # 检测MIME类型
        mime_type = self._detect_mime_type(original_name)

        # 创建文件元数据
        file_metadata = FileMetadata(
            file_id=file_id,
            original_name=original_name,
            safe_name=safe_name,
            file_path=str(file_path),
            file_size=file_size,
            mime_type=mime_type,
            category=category,
            business_type=business_type,
            upload_time=datetime.now(),
            checksum=checksum,
            **metadata
        )

        # 保存元数据到数据库
        self._save_metadata(file_metadata)

        return file_metadata

    def get_file_metadata(self, file_id: str) -> Optional[FileMetadata]:
        """根据文件ID获取元数据"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM file_storage
                WHERE file_id = ?
            """, (file_id,))

            row = cursor.fetchone()
            if row:
                return self._row_to_metadata(row)
            return None

    def get_file_path(self, file_id: str) -> Optional[Path]:
        """根据文件ID获取文件路径"""
        metadata = self.get_file_metadata(file_id)
        if metadata and os.path.exists(metadata.file_path):
            return Path(metadata.file_path)
        return None

    def get_files_by_category(self, category: str, limit: int = 100) -> List[FileMetadata]:
        """根据分类获取文件列表"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM file_storage
                WHERE category = ?
                ORDER BY upload_time DESC
                LIMIT ?
            """, (category, limit))

            return [self._row_to_metadata(row) for row in cursor.fetchall()]

    def get_files_by_business_type(self, business_type: str, limit: int = 100) -> List[FileMetadata]:
        """根据业务类型获取文件列表"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM file_storage
                WHERE business_type = ?
                ORDER BY upload_time DESC
                LIMIT ?
            """, (business_type, limit))

            return [self._row_to_metadata(row) for row in cursor.fetchall()]

    def delete_file(self, file_id: str) -> bool:
        """删除文件及其元数据"""
        metadata = self.get_file_metadata(file_id)
        if not metadata:
            return False

        try:
            # 删除物理文件
            if os.path.exists(metadata.file_path):
                os.remove(metadata.file_path)

            # 删除数据库记录
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM file_storage WHERE file_id = ?", (file_id,))
                conn.commit()

            return True
        except Exception as e:
            print(f"删除文件失败: {e}")
            return False

    def cleanup_temp_files(self, max_age_hours: int = 24):
        """清理临时文件"""
        temp_dir = self.storage_root / 'temp'
        if not temp_dir.exists():
            return

        cutoff_time = datetime.now().timestamp() - (max_age_hours * 3600)

        for file_path in temp_dir.iterdir():
            if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                try:
                    file_path.unlink()
                    print(f"已删除过期临时文件: {file_path}")
                except Exception as e:
                    print(f"删除临时文件失败 {file_path}: {e}")

    def _generate_safe_filename(self, original_name: str, file_id: str) -> str:
        """
        生成安全的文件名，保留中文字符

        格式：timestamp_原始名称_fileid.ext
        例如：20250930_160755_5G技术白皮书_a1b2c3d4.pdf
        """
        import re

        # 分离文件名和扩展名
        name_part, extension = os.path.splitext(original_name)

        # 只移除文件系统不允许的特殊字符，保留中文、字母、数字
        # Windows/Linux/Mac 不允许的字符: < > : " / \ | ? *
        safe_name_part = re.sub(r'[<>:"/\\|?*]', '_', name_part)

        # 限制长度，避免路径过长（一般文件系统限制255字符）
        if len(safe_name_part) > 100:
            safe_name_part = safe_name_part[:100]

        # 使用时间戳 + 原始名称 + UUID前8位 + 扩展名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = f"{timestamp}_{safe_name_part}_{file_id[:8]}{extension}"

        return safe_name

    def _build_file_path(self, category: str, filename: str) -> Path:
        """构建文件存储路径"""
        # 按年月分目录
        now = datetime.now()
        year_month = now.strftime("%Y/%m")

        return self.storage_root / category / year_month / filename

    def _detect_mime_type(self, filename: str) -> str:
        """检测文件MIME类型"""
        extension = filename.lower().split('.')[-1] if '.' in filename else ''

        mime_types = {
            'pdf': 'application/pdf',
            'doc': 'application/msword',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'txt': 'text/plain',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'xls': 'application/vnd.ms-excel',
            'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        }

        return mime_types.get(extension, 'application/octet-stream')

    def _save_metadata(self, metadata: FileMetadata):
        """保存文件元数据到数据库"""
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # 确保表存在
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS file_storage (
                    file_id TEXT PRIMARY KEY,
                    original_name TEXT NOT NULL,
                    safe_name TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    file_size INTEGER NOT NULL,
                    mime_type TEXT NOT NULL,
                    category TEXT NOT NULL,
                    business_type TEXT NOT NULL,
                    upload_time TIMESTAMP NOT NULL,
                    user_id TEXT,
                    company_id INTEGER,
                    description TEXT,
                    tags TEXT,
                    checksum TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 插入元数据
            cursor.execute("""
                INSERT INTO file_storage (
                    file_id, original_name, safe_name, file_path, file_size,
                    mime_type, category, business_type, upload_time, user_id,
                    company_id, description, tags, checksum
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                metadata.file_id,
                metadata.original_name,
                metadata.safe_name,
                metadata.file_path,
                metadata.file_size,
                metadata.mime_type,
                metadata.category,
                metadata.business_type,
                metadata.upload_time,
                metadata.user_id,
                metadata.company_id,
                metadata.description,
                ','.join(metadata.tags) if metadata.tags else None,
                metadata.checksum
            ))

            conn.commit()

    def _row_to_metadata(self, row) -> FileMetadata:
        """数据库行转换为FileMetadata对象"""
        return FileMetadata(
            file_id=row[0],
            original_name=row[1],
            safe_name=row[2],
            file_path=row[3],
            file_size=row[4],
            mime_type=row[5],
            category=row[6],
            business_type=row[7],
            upload_time=datetime.fromisoformat(row[8]) if isinstance(row[8], str) else row[8],
            user_id=row[9],
            company_id=row[10],
            description=row[11],
            tags=row[12].split(',') if row[12] else None,
            checksum=row[13]
        )


# 全局存储服务实例
storage_service = FileStorageService()