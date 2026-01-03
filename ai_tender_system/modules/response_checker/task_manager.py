#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
应答文件自检任务管理器

负责任务的创建、执行、状态管理和持久化
"""

import uuid
import json
import sqlite3
import threading
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging

from .schemas import ResponseCheckTask, ResponseCheckResult, CheckCategory
from .checker import ResponseChecker

logger = logging.getLogger(__name__)


class ResponseCheckTaskManager:
    """
    应答文件自检任务管理器
    """

    # 内存中的运行任务缓存
    _running_tasks: Dict[str, ResponseCheckTask] = {}
    _lock = threading.Lock()

    def __init__(self, db_path: str = None):
        """
        初始化任务管理器

        Args:
            db_path: 数据库路径
        """
        if db_path is None:
            # 使用默认数据库路径
            base_dir = Path(__file__).parent.parent.parent
            db_path = str(base_dir / 'data' / 'knowledge_base.db')

        self.db_path = db_path
        self._ensure_table()

    def _ensure_table(self):
        """确保数据库表存在"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS response_check_tasks (
                    task_id TEXT PRIMARY KEY,
                    openid TEXT,
                    user_id INTEGER,
                    file_id TEXT NOT NULL,
                    file_path TEXT,
                    original_filename TEXT NOT NULL,
                    file_size INTEGER DEFAULT 0,
                    total_pages INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'pending',
                    progress INTEGER DEFAULT 0,
                    current_step TEXT DEFAULT '',
                    current_category TEXT DEFAULT '',
                    error_message TEXT DEFAULT '',
                    extracted_info TEXT DEFAULT '{}',
                    check_categories TEXT DEFAULT '[]',
                    total_items INTEGER DEFAULT 0,
                    pass_count INTEGER DEFAULT 0,
                    fail_count INTEGER DEFAULT 0,
                    unknown_count INTEGER DEFAULT 0,
                    model_name TEXT DEFAULT 'deepseek-v3',
                    analysis_time REAL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP
                )
            ''')

            # 创建索引
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_response_check_openid ON response_check_tasks(openid)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_response_check_user_id ON response_check_tasks(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_response_check_status ON response_check_tasks(status)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_response_check_created ON response_check_tasks(created_at DESC)')

            conn.commit()
            conn.close()
            logger.info("数据库表初始化完成")

        except Exception as e:
            logger.error(f"数据库表初始化失败: {e}")

    def create_task(self,
                    file_id: str,
                    file_path: str,
                    original_filename: str,
                    user_id: int = None,
                    openid: str = '',
                    file_size: int = 0,
                    model_name: str = 'deepseek-v3') -> str:
        """
        创建检查任务

        Args:
            file_id: 文件ID
            file_path: 文件路径
            original_filename: 原始文件名
            user_id: 用户ID
            openid: 小程序openid
            file_size: 文件大小
            model_name: AI模型名称

        Returns:
            任务ID
        """
        task_id = str(uuid.uuid4())

        task = ResponseCheckTask(
            task_id=task_id,
            openid=openid,
            user_id=user_id,
            file_id=file_id,
            file_path=file_path,
            original_filename=original_filename,
            file_size=file_size,
            status='pending',
            progress=0,
            model_name=model_name,
            created_at=datetime.now()
        )

        # 保存到数据库
        self._save_task(task)

        # 缓存到内存
        with self._lock:
            self._running_tasks[task_id] = task

        logger.info(f"创建检查任务: {task_id}")
        return task_id

    def start_check(self, task_id: str):
        """
        启动检查任务（异步）

        Args:
            task_id: 任务ID
        """
        # 在新线程中执行检查
        thread = threading.Thread(target=self._run_check, args=(task_id,))
        thread.daemon = True
        thread.start()

        logger.info(f"检查任务已启动: {task_id}")

    def _run_check(self, task_id: str):
        """
        执行检查任务

        Args:
            task_id: 任务ID
        """
        task = self.get_task(task_id)
        if not task:
            logger.error(f"任务不存在: {task_id}")
            return

        try:
            # 更新状态为解析中
            self._update_task_status(task_id, 'parsing', 5, '正在解析文档...')

            # 获取任务信息
            file_path = task.get('file_path', '')
            model_name = task.get('model_name', 'deepseek-v3')

            # 创建检查器并执行检查
            checker = ResponseChecker(model_name=model_name)

            # 定义进度回调
            def progress_callback(progress: int, message: str):
                self._update_task_status(task_id, 'checking', progress, message)

            # 定义类别完成回调
            categories_completed = []

            def category_callback(category: CheckCategory):
                categories_completed.append(category)
                self._update_task_categories(task_id, categories_completed)

            # 执行检查
            result = checker.check(
                file_path=file_path,
                progress_callback=progress_callback,
                category_callback=category_callback
            )

            # 保存结果
            self._save_result(task_id, result)

            logger.info(f"检查任务完成: {task_id}")

        except Exception as e:
            logger.error(f"检查任务失败: {task_id}, 错误: {e}")
            self._update_task_status(task_id, 'failed', 0, '', str(e))

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        获取任务信息

        Args:
            task_id: 任务ID

        Returns:
            任务信息字典
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM response_check_tasks WHERE task_id = ?', (task_id,))
            row = cursor.fetchone()
            conn.close()

            if row:
                return dict(row)
            return None

        except Exception as e:
            logger.error(f"获取任务失败: {e}")
            return None

    def get_task_result(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        获取任务完整结果

        Args:
            task_id: 任务ID

        Returns:
            完整结果字典
        """
        task = self.get_task(task_id)
        if not task:
            return None

        if task['status'] != 'completed':
            return None

        # 解析存储的JSON数据
        try:
            categories = json.loads(task.get('check_categories', '[]'))
            extracted_info = json.loads(task.get('extracted_info', '{}'))

            return {
                'task_id': task['task_id'],
                'file_name': task['original_filename'],
                'check_time': task['completed_at'],
                'categories': categories,
                'extracted_info': extracted_info,
                'statistics': {
                    'total_items': task['total_items'],
                    'pass_count': task['pass_count'],
                    'fail_count': task['fail_count'],
                    'unknown_count': task['unknown_count']
                },
                'total_pages': task['total_pages'],
                'analysis_time': task['analysis_time'],
                'model_name': task['model_name']
            }

        except Exception as e:
            logger.error(f"解析任务结果失败: {e}")
            return None

    def list_tasks(self,
                   user_id: int = None,
                   openid: str = None,
                   page: int = 1,
                   page_size: int = 10) -> Dict[str, Any]:
        """
        获取任务列表

        Args:
            user_id: 用户ID
            openid: 小程序openid
            page: 页码
            page_size: 每页数量

        Returns:
            任务列表和分页信息
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # 构建查询条件
            conditions = []
            params = []

            if user_id:
                conditions.append('user_id = ?')
                params.append(user_id)
            if openid:
                conditions.append('openid = ?')
                params.append(openid)

            where_clause = ' AND '.join(conditions) if conditions else '1=1'

            # 查询总数
            cursor.execute(f'SELECT COUNT(*) FROM response_check_tasks WHERE {where_clause}', params)
            total = cursor.fetchone()[0]

            # 查询列表
            offset = (page - 1) * page_size
            cursor.execute(f'''
                SELECT task_id, original_filename, status, progress, current_step,
                       total_items, pass_count, fail_count, unknown_count,
                       created_at, completed_at, error_message
                FROM response_check_tasks
                WHERE {where_clause}
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            ''', params + [page_size, offset])

            rows = cursor.fetchall()
            conn.close()

            tasks = [dict(row) for row in rows]

            return {
                'tasks': tasks,
                'total': total,
                'page': page,
                'page_size': page_size,
                'total_pages': (total + page_size - 1) // page_size
            }

        except Exception as e:
            logger.error(f"获取任务列表失败: {e}")
            return {'tasks': [], 'total': 0, 'page': page, 'page_size': page_size, 'total_pages': 0}

    def delete_task(self, task_id: str, user_id: int = None) -> bool:
        """
        删除任务

        Args:
            task_id: 任务ID
            user_id: 用户ID（用于权限校验）

        Returns:
            是否删除成功
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            if user_id:
                cursor.execute(
                    'DELETE FROM response_check_tasks WHERE task_id = ? AND user_id = ?',
                    (task_id, user_id)
                )
            else:
                cursor.execute(
                    'DELETE FROM response_check_tasks WHERE task_id = ?',
                    (task_id,)
                )

            affected = cursor.rowcount
            conn.commit()
            conn.close()

            # 从内存缓存中移除
            with self._lock:
                if task_id in self._running_tasks:
                    del self._running_tasks[task_id]

            return affected > 0

        except Exception as e:
            logger.error(f"删除任务失败: {e}")
            return False

    # ========== 内部方法 ==========

    def _save_task(self, task: ResponseCheckTask):
        """保存任务到数据库"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT OR REPLACE INTO response_check_tasks
                (task_id, openid, user_id, file_id, file_path, original_filename,
                 file_size, status, progress, current_step, model_name, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                task.task_id, task.openid, task.user_id, task.file_id,
                task.file_path, task.original_filename, task.file_size,
                task.status, task.progress, task.current_step,
                task.model_name, task.created_at
            ))

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"保存任务失败: {e}")

    def _update_task_status(self, task_id: str, status: str, progress: int,
                            current_step: str, error_message: str = ''):
        """更新任务状态"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            if status == 'parsing':
                cursor.execute('''
                    UPDATE response_check_tasks
                    SET status = ?, progress = ?, current_step = ?, started_at = ?
                    WHERE task_id = ?
                ''', (status, progress, current_step, datetime.now(), task_id))
            elif status == 'failed':
                cursor.execute('''
                    UPDATE response_check_tasks
                    SET status = ?, progress = ?, current_step = ?, error_message = ?,
                        completed_at = ?
                    WHERE task_id = ?
                ''', (status, progress, current_step, error_message, datetime.now(), task_id))
            else:
                cursor.execute('''
                    UPDATE response_check_tasks
                    SET status = ?, progress = ?, current_step = ?
                    WHERE task_id = ?
                ''', (status, progress, current_step, task_id))

            conn.commit()
            conn.close()

            # 更新内存缓存
            with self._lock:
                if task_id in self._running_tasks:
                    self._running_tasks[task_id].status = status
                    self._running_tasks[task_id].progress = progress
                    self._running_tasks[task_id].current_step = current_step

        except Exception as e:
            logger.error(f"更新任务状态失败: {e}")

    def _update_task_categories(self, task_id: str, categories: List[CheckCategory]):
        """更新任务检查类别（增量更新）"""
        try:
            categories_data = [cat.to_dict() for cat in categories]

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                UPDATE response_check_tasks
                SET check_categories = ?, current_category = ?
                WHERE task_id = ?
            ''', (
                json.dumps(categories_data, ensure_ascii=False),
                categories[-1].category_name if categories else '',
                task_id
            ))

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"更新任务类别失败: {e}")

    def _save_result(self, task_id: str, result: ResponseCheckResult):
        """保存检查结果"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            categories_data = [cat.to_dict() for cat in result.categories]
            extracted_info_data = result.extracted_info.to_dict()

            cursor.execute('''
                UPDATE response_check_tasks
                SET status = 'completed',
                    progress = 100,
                    current_step = '检查完成',
                    extracted_info = ?,
                    check_categories = ?,
                    total_items = ?,
                    pass_count = ?,
                    fail_count = ?,
                    unknown_count = ?,
                    total_pages = ?,
                    analysis_time = ?,
                    completed_at = ?
                WHERE task_id = ?
            ''', (
                json.dumps(extracted_info_data, ensure_ascii=False),
                json.dumps(categories_data, ensure_ascii=False),
                result.total_items,
                result.pass_count,
                result.fail_count,
                result.unknown_count,
                result.total_pages,
                result.analysis_time,
                datetime.now(),
                task_id
            ))

            conn.commit()
            conn.close()

            # 从内存缓存中移除
            with self._lock:
                if task_id in self._running_tasks:
                    del self._running_tasks[task_id]

        except Exception as e:
            logger.error(f"保存检查结果失败: {e}")
