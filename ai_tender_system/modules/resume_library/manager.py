#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简历库管理器
提供简历的增删改查、附件管理等核心功能
"""

import os
import json
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional, Any
from contextlib import contextmanager

from ai_tender_system.utils.storage_service import storage_service
from ai_tender_system.utils.db_utils import dict_factory, get_db_connection


class ResumeLibraryManager:
    """简历库管理器"""

    def __init__(self, db_path: str = None):
        """
        初始化管理器
        Args:
            db_path: 数据库路径，默认使用系统配置
        """
        self.db_path = db_path or 'ai_tender_system/data/knowledge_base.db'
        self._init_database()

    def _init_database(self):
        """初始化数据库表"""
        schema_file = 'ai_tender_system/database/resume_library_schema.sql'
        if os.path.exists(schema_file):
            with open(schema_file, 'r', encoding='utf-8') as f:
                schema_sql = f.read()

            with self._get_connection() as conn:
                cursor = conn.cursor()
                # 执行所有SQL语句
                cursor.executescript(schema_sql)
                conn.commit()

    @contextmanager
    def _get_connection(self):
        """获取数据库连接上下文管理器"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = dict_factory
        try:
            yield conn
        finally:
            conn.close()

    # ==================== 简历管理 ====================

    def create_resume(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建新简历
        Args:
            resume_data: 简历数据
        Returns:
            创建的简历信息
        """
        # 处理JSON字段
        json_fields = ['skills', 'certificates', 'languages', 'project_experience']
        for field in json_fields:
            if field in resume_data and resume_data[field]:
                if isinstance(resume_data[field], (list, dict)):
                    resume_data[field] = json.dumps(resume_data[field], ensure_ascii=False)

        # 准备SQL语句
        columns = []
        values = []
        placeholders = []

        for key, value in resume_data.items():
            if key not in ['resume_id', 'created_at', 'updated_at']:
                columns.append(key)
                values.append(value)
                placeholders.append('?')

        sql = f"""
            INSERT INTO resumes ({', '.join(columns)})
            VALUES ({', '.join(placeholders)})
        """

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, values)
                resume_id = cursor.lastrowid
                conn.commit()

                # 更新全文搜索索引
                self._update_fts_index(conn, resume_id)

                return self.get_resume_by_id(resume_id)

        except Exception as e:
            raise Exception(f"创建简历失败: {str(e)}")

    def update_resume(self, resume_id: int, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新简历信息
        Args:
            resume_id: 简历ID
            resume_data: 更新的数据
        Returns:
            更新后的简历信息
        """
        # 处理JSON字段
        json_fields = ['skills', 'certificates', 'languages', 'project_experience']
        for field in json_fields:
            if field in resume_data and resume_data[field]:
                if isinstance(resume_data[field], (list, dict)):
                    resume_data[field] = json.dumps(resume_data[field], ensure_ascii=False)

        # 准备SQL语句
        set_clauses = []
        values = []

        for key, value in resume_data.items():
            if key not in ['resume_id', 'created_at', 'updated_at']:
                set_clauses.append(f"{key} = ?")
                values.append(value)

        values.append(resume_id)

        sql = f"""
            UPDATE resumes
            SET {', '.join(set_clauses)}, updated_at = CURRENT_TIMESTAMP
            WHERE resume_id = ?
        """

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, values)
                conn.commit()

                # 更新全文搜索索引
                self._update_fts_index(conn, resume_id)

                return self.get_resume_by_id(resume_id)

        except Exception as e:
            raise Exception(f"更新简历失败: {str(e)}")

    def delete_resume(self, resume_id: int) -> bool:
        """
        删除简历（级联删除附件）
        Args:
            resume_id: 简历ID
        Returns:
            是否成功
        """
        try:
            # 先获取所有附件信息，以便删除文件
            attachments = self.get_attachments(resume_id)

            with self._get_connection() as conn:
                cursor = conn.cursor()

                # 删除简历（级联删除附件记录）
                cursor.execute("DELETE FROM resumes WHERE resume_id = ?", (resume_id,))

                # 删除全文搜索索引
                cursor.execute("DELETE FROM resumes_fts WHERE rowid = ?", (resume_id,))

                conn.commit()

            # 删除附件文件
            for attachment in attachments:
                if attachment['file_path'] and os.path.exists(attachment['file_path']):
                    try:
                        os.remove(attachment['file_path'])
                    except:
                        pass

            return True

        except Exception as e:
            raise Exception(f"删除简历失败: {str(e)}")

    def get_resume_by_id(self, resume_id: int) -> Optional[Dict[str, Any]]:
        """
        获取简历详情
        Args:
            resume_id: 简历ID
        Returns:
            简历信息
        """
        sql = "SELECT * FROM resumes WHERE resume_id = ?"

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (resume_id,))
            resume = cursor.fetchone()

            if resume:
                # 解析JSON字段
                json_fields = ['skills', 'certificates', 'languages', 'project_experience']
                for field in json_fields:
                    if resume.get(field):
                        try:
                            resume[field] = json.loads(resume[field])
                        except:
                            pass

                # 获取附件信息
                resume['attachments'] = self.get_attachments(resume_id)

            return resume

    def get_resumes(self,
                   company_id: Optional[int] = None,
                   status: Optional[str] = None,
                   search_keyword: Optional[str] = None,
                   education_level: Optional[str] = None,
                   position: Optional[str] = None,
                   tags: Optional[List[str]] = None,
                   page: int = 1,
                   page_size: int = 20,
                   order_by: str = 'created_at',
                   order_dir: str = 'DESC') -> Dict[str, Any]:
        """
        获取简历列表
        Args:
            company_id: 公司ID
            status: 状态
            search_keyword: 搜索关键词
            education_level: 学历
            position: 职位
            tags: 标签列表
            page: 页码
            page_size: 每页数量
            order_by: 排序字段
            order_dir: 排序方向
        Returns:
            简历列表和分页信息
        """
        conditions = []
        params = []

        # 构建查询条件
        if company_id:
            conditions.append("company_id = ?")
            params.append(company_id)

        if status:
            conditions.append("status = ?")
            params.append(status)

        if education_level:
            conditions.append("education_level = ?")
            params.append(education_level)

        if position:
            conditions.append("current_position LIKE ?")
            params.append(f"%{position}%")

        if tags:
            tag_conditions = []
            for tag in tags:
                tag_conditions.append("tags LIKE ?")
                params.append(f"%{tag}%")
            if tag_conditions:
                conditions.append(f"({' OR '.join(tag_conditions)})")

        # 全文搜索
        if search_keyword:
            # 使用全文搜索表
            fts_sql = """
                SELECT resume_id FROM resumes_fts
                WHERE resumes_fts MATCH ?
            """
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(fts_sql, (search_keyword,))
                resume_ids = [row['resume_id'] for row in cursor.fetchall()]

                if resume_ids:
                    conditions.append(f"resume_id IN ({','.join(['?'] * len(resume_ids))})")
                    params.extend(resume_ids)
                else:
                    # 如果没有匹配结果，返回空结果
                    return {
                        'resumes': [],
                        'total': 0,
                        'page': page,
                        'page_size': page_size,
                        'total_pages': 0
                    }

        # 构建查询SQL
        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        # 统计总数
        count_sql = f"SELECT COUNT(*) as total FROM resumes {where_clause}"

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(count_sql, params)
            total = cursor.fetchone()['total']

            # 分页查询
            offset = (page - 1) * page_size
            data_sql = f"""
                SELECT * FROM resumes
                {where_clause}
                ORDER BY {order_by} {order_dir}
                LIMIT ? OFFSET ?
            """

            cursor.execute(data_sql, params + [page_size, offset])
            resumes = cursor.fetchall()

            # 解析JSON字段
            for resume in resumes:
                json_fields = ['skills', 'certificates', 'languages', 'project_experience']
                for field in json_fields:
                    if resume.get(field):
                        try:
                            resume[field] = json.loads(resume[field])
                        except:
                            pass

                # 获取附件数量
                cursor.execute(
                    "SELECT COUNT(*) as count FROM resume_attachments WHERE resume_id = ?",
                    (resume['resume_id'],)
                )
                resume['attachment_count'] = cursor.fetchone()['count']

        return {
            'resumes': resumes,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        }

    # ==================== 附件管理 ====================

    def upload_attachment(self,
                         resume_id: int,
                         file_path: str,
                         original_filename: str,
                         attachment_category: str,
                         attachment_description: str = None,
                         uploaded_by: str = None) -> Dict[str, Any]:
        """
        上传简历附件
        Args:
            resume_id: 简历ID
            file_path: 文件路径
            original_filename: 原始文件名
            attachment_category: 附件类别
            attachment_description: 附件说明
            uploaded_by: 上传人
        Returns:
            附件信息
        """
        # 验证附件类别
        valid_categories = ['resume', 'id_card', 'education', 'degree',
                          'qualification', 'award', 'other']
        if attachment_category not in valid_categories:
            raise ValueError(f"无效的附件类别: {attachment_category}")

        # 获取文件信息
        file_size = os.path.getsize(file_path)
        file_type = os.path.splitext(original_filename)[1].lower()[1:]

        # 生成存储文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_name = f"resume_{resume_id}_{attachment_category}_{timestamp}.{file_type}"

        # 使用storage_service存储文件
        storage_info = storage_service.save_file(
            file_path,
            category='resume_attachments',
            metadata={
                'resume_id': resume_id,
                'attachment_category': attachment_category,
                'original_filename': original_filename
            }
        )

        # 保存到数据库
        sql = """
            INSERT INTO resume_attachments
            (resume_id, file_name, original_filename, file_path, file_type,
             file_size, attachment_category, attachment_description, uploaded_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (
                    resume_id,
                    storage_info['filename'],
                    original_filename,
                    storage_info['filepath'],
                    file_type,
                    file_size,
                    attachment_category,
                    attachment_description,
                    uploaded_by
                ))
                attachment_id = cursor.lastrowid
                conn.commit()

                return {
                    'attachment_id': attachment_id,
                    'resume_id': resume_id,
                    'file_name': storage_info['filename'],
                    'original_filename': original_filename,
                    'file_path': storage_info['filepath'],
                    'file_type': file_type,
                    'file_size': file_size,
                    'attachment_category': attachment_category,
                    'attachment_description': attachment_description,
                    'uploaded_by': uploaded_by,
                    'uploaded_at': datetime.now().isoformat()
                }

        except Exception as e:
            # 删除已上传的文件
            if os.path.exists(storage_info['filepath']):
                os.remove(storage_info['filepath'])
            raise Exception(f"保存附件信息失败: {str(e)}")

    def get_attachments(self,
                       resume_id: int,
                       category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        获取简历附件列表
        Args:
            resume_id: 简历ID
            category: 附件类别（可选）
        Returns:
            附件列表
        """
        sql = "SELECT * FROM resume_attachments WHERE resume_id = ?"
        params = [resume_id]

        if category:
            sql += " AND attachment_category = ?"
            params.append(category)

        sql += " ORDER BY uploaded_at DESC"

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            return cursor.fetchall()

    def delete_attachment(self, attachment_id: int) -> bool:
        """
        删除附件
        Args:
            attachment_id: 附件ID
        Returns:
            是否成功
        """
        try:
            # 先获取附件信息
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT file_path FROM resume_attachments WHERE attachment_id = ?",
                    (attachment_id,)
                )
                attachment = cursor.fetchone()

                if attachment:
                    # 删除文件
                    if attachment['file_path'] and os.path.exists(attachment['file_path']):
                        os.remove(attachment['file_path'])

                    # 删除数据库记录
                    cursor.execute(
                        "DELETE FROM resume_attachments WHERE attachment_id = ?",
                        (attachment_id,)
                    )
                    conn.commit()

                return True

        except Exception as e:
            raise Exception(f"删除附件失败: {str(e)}")

    # ==================== 辅助方法 ====================

    def _update_fts_index(self, conn: sqlite3.Connection, resume_id: int):
        """
        更新全文搜索索引
        Args:
            conn: 数据库连接
            resume_id: 简历ID
        """
        try:
            cursor = conn.cursor()

            # 获取简历信息
            cursor.execute(
                """SELECT name, current_position, skills, university,
                   major, introduction FROM resumes WHERE resume_id = ?""",
                (resume_id,)
            )
            resume = cursor.fetchone()

            if resume:
                # 删除旧索引
                cursor.execute("DELETE FROM resumes_fts WHERE rowid = ?", (resume_id,))

                # 插入新索引
                cursor.execute(
                    """INSERT INTO resumes_fts
                       (rowid, name, current_position, skills, university, major, introduction)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (resume_id, resume['name'], resume['current_position'],
                     resume['skills'], resume['university'], resume['major'],
                     resume['introduction'])
                )
        except:
            # 忽略FTS索引错误，不影响主要功能
            pass

    def search_resumes(self, keyword: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        快速搜索简历
        Args:
            keyword: 搜索关键词
            limit: 返回数量限制
        Returns:
            匹配的简历列表
        """
        sql = """
            SELECT r.* FROM resumes r
            JOIN resumes_fts fts ON r.resume_id = fts.rowid
            WHERE resumes_fts MATCH ?
            ORDER BY rank
            LIMIT ?
        """

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (keyword, limit))
            resumes = cursor.fetchall()

            # 解析JSON字段
            for resume in resumes:
                json_fields = ['skills', 'certificates', 'languages', 'project_experience']
                for field in json_fields:
                    if resume.get(field):
                        try:
                            resume[field] = json.loads(resume[field])
                        except:
                            pass

            return resumes

    def get_statistics(self, company_id: Optional[int] = None) -> Dict[str, Any]:
        """
        获取简历统计信息
        Args:
            company_id: 公司ID（可选）
        Returns:
            统计信息
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # 基础条件
            where_clause = "WHERE company_id = ?" if company_id else ""
            params = [company_id] if company_id else []

            # 总数
            cursor.execute(f"SELECT COUNT(*) as total FROM resumes {where_clause}", params)
            total = cursor.fetchone()['total']

            # 按学历统计
            cursor.execute(
                f"""SELECT education_level, COUNT(*) as count
                    FROM resumes {where_clause}
                    GROUP BY education_level""",
                params
            )
            education_stats = {row['education_level']: row['count'] for row in cursor.fetchall()}

            # 按状态统计
            cursor.execute(
                f"""SELECT status, COUNT(*) as count
                    FROM resumes {where_clause}
                    GROUP BY status""",
                params
            )
            status_stats = {row['status']: row['count'] for row in cursor.fetchall()}

            # 附件统计
            if company_id:
                cursor.execute(
                    """SELECT COUNT(*) as total_attachments
                       FROM resume_attachments ra
                       JOIN resumes r ON ra.resume_id = r.resume_id
                       WHERE r.company_id = ?""",
                    (company_id,)
                )
            else:
                cursor.execute("SELECT COUNT(*) as total_attachments FROM resume_attachments")

            total_attachments = cursor.fetchone()['total_attachments']

            return {
                'total_resumes': total,
                'education_stats': education_stats,
                'status_stats': status_stats,
                'total_attachments': total_attachments
            }