#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
风险分析任务管理器
处理异步任务、数据库操作、进度跟踪
"""

import uuid
import json
import threading
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

import sys
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from common.logger import get_module_logger
from common.database import get_knowledge_base_db

from .schemas import RiskTask, RiskAnalysisResult, RiskItem, ReconcileResult
from .analyzer import RiskAnalyzer

# V5 新增模块
try:
    from .analyzer_v5 import RiskAnalyzerV5
    from .reconciler import Reconciler
    HAS_V5 = True
except ImportError:
    HAS_V5 = False

logger = get_module_logger("risk_analyzer.task_manager")


class RiskTaskManager:
    """风险分析任务管理器"""

    # 任务实例缓存（用于异步任务）
    _running_tasks: Dict[str, Dict] = {}
    _lock = threading.Lock()

    def __init__(self):
        self.db = get_knowledge_base_db()
        self._ensure_table_exists()
        logger.info("风险分析任务管理器初始化完成")

    def _ensure_table_exists(self):
        """确保数据库表存在"""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS risk_analysis_tasks (
            task_id TEXT PRIMARY KEY,
            openid TEXT,
            user_id INTEGER,
            file_id TEXT NOT NULL,
            file_path TEXT,
            original_filename TEXT NOT NULL,
            file_size INTEGER DEFAULT 0,

            status TEXT DEFAULT 'pending',
            progress INTEGER DEFAULT 0,
            current_step TEXT DEFAULT '',
            error_message TEXT DEFAULT '',

            total_text_length INTEGER DEFAULT 0,
            chunk_count INTEGER DEFAULT 0,

            risk_items TEXT,
            summary TEXT,
            risk_score INTEGER DEFAULT 0,

            model_name TEXT DEFAULT 'deepseek-v3',
            total_tokens INTEGER DEFAULT 0,
            analysis_time REAL DEFAULT 0,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            started_at TIMESTAMP,
            completed_at TIMESTAMP
        );
        """
        create_index_sql = """
        CREATE INDEX IF NOT EXISTS idx_risk_tasks_openid ON risk_analysis_tasks(openid);
        CREATE INDEX IF NOT EXISTS idx_risk_tasks_status ON risk_analysis_tasks(status);
        CREATE INDEX IF NOT EXISTS idx_risk_tasks_created ON risk_analysis_tasks(created_at DESC);
        """

        # V5 新增字段
        v5_columns = [
            ("response_file_path", "TEXT DEFAULT ''"),
            ("response_file_name", "TEXT DEFAULT ''"),
            ("has_toc", "INTEGER DEFAULT 0"),
            ("analysis_mode", "TEXT DEFAULT 'bid_only'"),
            ("reconcile_results", "TEXT DEFAULT ''"),
            ("reconcile_progress", "INTEGER DEFAULT 0"),
            ("reconcile_step", "TEXT DEFAULT ''"),
            ("exclude_chapters", "TEXT DEFAULT ''"),
        ]

        try:
            self.db.execute_query(create_table_sql)
            for sql in create_index_sql.strip().split(';'):
                if sql.strip():
                    self.db.execute_query(sql)

            # 尝试添加 V5 新增字段（如果不存在）
            for col_name, col_def in v5_columns:
                try:
                    self.db.execute_query(
                        f"ALTER TABLE risk_analysis_tasks ADD COLUMN {col_name} {col_def}"
                    )
                    logger.debug(f"添加字段: {col_name}")
                except Exception:
                    pass  # 字段已存在，忽略

            logger.debug("数据库表检查完成")
        except Exception as e:
            logger.error(f"创建数据库表失败: {e}")

    def create_task(self,
                    file_id: str,
                    file_path: str,
                    original_filename: str,
                    openid: str = '',
                    user_id: Optional[int] = None,
                    file_size: int = 0,
                    model_name: str = 'deepseek-v3') -> str:
        """
        创建分析任务

        Returns:
            task_id: 任务ID
        """
        task_id = str(uuid.uuid4())

        insert_sql = """
        INSERT INTO risk_analysis_tasks (
            task_id, openid, user_id, file_id, file_path,
            original_filename, file_size, status, model_name, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, 'pending', ?, ?)
        """

        try:
            self.db.execute_query(insert_sql, (
                task_id, openid, user_id, file_id, file_path,
                original_filename, file_size, model_name,
                datetime.now().isoformat()
            ))
            logger.info(f"创建任务成功: {task_id}, 文件: {original_filename}")
            return task_id
        except Exception as e:
            logger.error(f"创建任务失败: {e}")
            raise

    def start_analysis(self, task_id: str) -> bool:
        """
        异步启动分析任务

        Args:
            task_id: 任务ID

        Returns:
            是否成功启动
        """
        task = self.get_task(task_id)
        if not task:
            logger.error(f"任务不存在: {task_id}")
            return False

        if task['status'] not in ['pending', 'failed']:
            logger.warning(f"任务状态不允许启动: {task_id}, status={task['status']}")
            return False

        # 更新状态为处理中
        self.update_task(task_id, status='parsing', progress=0, current_step='准备开始分析...')

        # 启动后台线程
        thread = threading.Thread(
            target=self._run_analysis,
            args=(task_id,),
            daemon=True
        )
        thread.start()

        logger.info(f"任务已启动: {task_id}")
        return True

    def _run_analysis(self, task_id: str):
        """在后台线程中运行分析"""
        try:
            task = self.get_task(task_id)
            if not task:
                return

            file_path = task['file_path']
            model_name = task.get('model_name', 'deepseek-v3')

            # 更新开始时间
            self.db.execute_query(
                "UPDATE risk_analysis_tasks SET started_at = ? WHERE task_id = ?",
                (datetime.now().isoformat(), task_id)
            )

            # 定义进度回调
            def progress_callback(progress: int, message: str):
                status = 'analyzing' if progress < 100 else 'completed'
                if progress <= 10:
                    status = 'parsing'
                self.update_task(task_id, status=status, progress=progress, current_step=message)

            # 定义增量结果回调 - 每分析完一个 chunk 就保存
            def item_callback(items: List[RiskItem]):
                if items:
                    self.append_risk_items(task_id, items)

            # 优先使用 V5 分析器
            if HAS_V5:
                logger.info(f"使用 V5 分析器: {task_id}")
                analyzer = RiskAnalyzerV5(model_name=model_name)
                result = analyzer.analyze(file_path, progress_callback, item_callback)

                # 保存 V5 特有字段
                self._save_v5_result(task_id, result)
            else:
                # 回退到旧版分析器
                logger.info(f"使用旧版分析器: {task_id}")
                analyzer = RiskAnalyzer(model_name=model_name)
                result = analyzer.analyze(file_path, progress_callback, item_callback)
                self._save_final_result(task_id, result)

            logger.info(f"任务完成: {task_id}, 发现 {len(result.risk_items)} 个风险项")

        except Exception as e:
            logger.error(f"任务执行失败: {task_id}, 错误: {e}")
            self.update_task(
                task_id,
                status='failed',
                error_message=str(e)
            )

    def _save_v5_result(self, task_id: str, result: RiskAnalysisResult):
        """保存 V5 分析结果"""
        update_sql = """
        UPDATE risk_analysis_tasks SET
            status = 'completed',
            progress = 100,
            current_step = '分析完成',
            summary = ?,
            risk_score = ?,
            chunk_count = ?,
            total_tokens = ?,
            analysis_time = ?,
            has_toc = ?,
            exclude_chapters = ?,
            completed_at = ?
        WHERE task_id = ?
        """

        exclude_chapters_json = json.dumps(result.exclude_chapters, ensure_ascii=False)

        self.db.execute_query(update_sql, (
            result.summary,
            result.risk_score,
            result.total_chunks,
            result.total_tokens,
            result.analysis_time,
            1 if result.has_toc else 0,
            exclude_chapters_json,
            datetime.now().isoformat(),
            task_id
        ))

    def append_risk_items(self, task_id: str, new_items: List[RiskItem]):
        """增量追加风险项到数据库"""
        if not new_items:
            return

        try:
            # 获取现有的 risk_items
            task = self.get_task(task_id)
            if not task:
                return

            existing_items = []
            if task.get('risk_items'):
                try:
                    existing_items = json.loads(task['risk_items'])
                except json.JSONDecodeError:
                    existing_items = []

            # 追加新项
            for item in new_items:
                existing_items.append(item.to_dict())

            # 更新数据库
            risk_items_json = json.dumps(existing_items, ensure_ascii=False)
            self.db.execute_query(
                "UPDATE risk_analysis_tasks SET risk_items = ? WHERE task_id = ?",
                (risk_items_json, task_id)
            )

            logger.debug(f"任务 {task_id} 追加 {len(new_items)} 个风险项，当前共 {len(existing_items)} 个")

        except Exception as e:
            logger.error(f"追加风险项失败: {e}")

    def _save_final_result(self, task_id: str, result: RiskAnalysisResult):
        """保存最终分析结果（summary、score等，不覆盖已有的 risk_items）"""
        update_sql = """
        UPDATE risk_analysis_tasks SET
            status = 'completed',
            progress = 100,
            current_step = '分析完成',
            summary = ?,
            risk_score = ?,
            chunk_count = ?,
            total_tokens = ?,
            analysis_time = ?,
            completed_at = ?
        WHERE task_id = ?
        """

        self.db.execute_query(update_sql, (
            result.summary,
            result.risk_score,
            result.total_chunks,
            result.total_tokens,
            result.analysis_time,
            datetime.now().isoformat(),
            task_id
        ))

    def _save_result(self, task_id: str, result: RiskAnalysisResult):
        """保存分析结果到数据库"""
        risk_items_json = json.dumps(
            [item.to_dict() for item in result.risk_items],
            ensure_ascii=False
        )

        update_sql = """
        UPDATE risk_analysis_tasks SET
            status = 'completed',
            progress = 100,
            current_step = '分析完成',
            risk_items = ?,
            summary = ?,
            risk_score = ?,
            chunk_count = ?,
            total_tokens = ?,
            analysis_time = ?,
            completed_at = ?
        WHERE task_id = ?
        """

        self.db.execute_query(update_sql, (
            risk_items_json,
            result.summary,
            result.risk_score,
            result.total_chunks,
            result.total_tokens,
            result.analysis_time,
            datetime.now().isoformat(),
            task_id
        ))

    def get_task(self, task_id: str) -> Optional[Dict]:
        """获取任务信息"""
        query_sql = "SELECT * FROM risk_analysis_tasks WHERE task_id = ?"
        result = self.db.execute_query(query_sql, (task_id,), fetch_one=True)
        return dict(result) if result else None

    def get_task_by_openid(self, task_id: str, openid: str) -> Optional[Dict]:
        """根据 task_id 和 openid 获取任务（权限校验）"""
        query_sql = "SELECT * FROM risk_analysis_tasks WHERE task_id = ? AND openid = ?"
        result = self.db.execute_query(query_sql, (task_id, openid), fetch_one=True)
        return dict(result) if result else None

    def get_task_result(self, task_id: str) -> Optional[Dict]:
        """获取任务结果（包含解析后的 risk_items）"""
        task = self.get_task(task_id)
        if not task:
            return None

        # 解析 risk_items JSON
        if task.get('risk_items'):
            try:
                task['risk_items'] = json.loads(task['risk_items'])
            except json.JSONDecodeError:
                task['risk_items'] = []
        else:
            task['risk_items'] = []

        return task

    def update_task(self, task_id: str, **kwargs):
        """更新任务状态"""
        if not kwargs:
            return

        set_clauses = []
        values = []

        for key, value in kwargs.items():
            set_clauses.append(f"{key} = ?")
            values.append(value)

        values.append(task_id)

        update_sql = f"UPDATE risk_analysis_tasks SET {', '.join(set_clauses)} WHERE task_id = ?"

        try:
            self.db.execute_query(update_sql, tuple(values))
        except Exception as e:
            logger.error(f"更新任务失败: {e}")

    def list_tasks(self,
                   openid: Optional[str] = None,
                   user_id: Optional[int] = None,
                   status: Optional[str] = None,
                   page: int = 1,
                   page_size: int = 20) -> Dict:
        """
        列表查询任务

        Returns:
            {
                'items': [...],
                'total': int,
                'page': int,
                'page_size': int
            }
        """
        where_clauses = []
        params = []

        if openid:
            where_clauses.append("openid = ?")
            params.append(openid)

        if user_id:
            where_clauses.append("user_id = ?")
            params.append(user_id)

        if status:
            where_clauses.append("status = ?")
            params.append(status)

        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"

        # 查询总数
        count_sql = f"SELECT COUNT(*) as total FROM risk_analysis_tasks WHERE {where_sql}"
        count_result = self.db.execute_query(count_sql, tuple(params), fetch_one=True)
        total = count_result['total'] if count_result else 0

        # 查询列表
        offset = (page - 1) * page_size
        query_sql = f"""
        SELECT task_id, openid, original_filename, file_size, status, progress,
               current_step, risk_score, summary, created_at, completed_at, model_name
        FROM risk_analysis_tasks
        WHERE {where_sql}
        ORDER BY created_at DESC
        LIMIT ? OFFSET ?
        """

        params.extend([page_size, offset])
        results = self.db.execute_query(query_sql, tuple(params))

        items = [dict(row) for row in results] if results else []

        return {
            'items': items,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        }

    def delete_task(self, task_id: str, openid: Optional[str] = None) -> bool:
        """
        删除任务

        Args:
            task_id: 任务ID
            openid: 如果提供，则验证权限

        Returns:
            是否删除成功
        """
        if openid:
            # 验证权限
            task = self.get_task_by_openid(task_id, openid)
            if not task:
                return False

        delete_sql = "DELETE FROM risk_analysis_tasks WHERE task_id = ?"
        try:
            self.db.execute_query(delete_sql, (task_id,))
            logger.info(f"删除任务成功: {task_id}")
            return True
        except Exception as e:
            logger.error(f"删除任务失败: {e}")
            return False

    # ============================================================
    # V5 双向对账功能
    # ============================================================

    def start_reconcile(self, task_id: str) -> bool:
        """
        启动双向对账任务

        Args:
            task_id: 任务ID

        Returns:
            是否成功启动
        """
        if not HAS_V5:
            logger.error("V5 模块未加载，无法执行对账")
            return False

        task = self.get_task(task_id)
        if not task:
            logger.error(f"任务不存在: {task_id}")
            return False

        if not task.get('response_file_path'):
            logger.error(f"未上传应答文件: {task_id}")
            return False

        # 更新状态为对账中
        self.update_task(
            task_id,
            status='reconciling',
            reconcile_progress=0,
            reconcile_step='准备开始对账...'
        )

        # 启动后台线程
        thread = threading.Thread(
            target=self._run_reconcile,
            args=(task_id,),
            daemon=True
        )
        thread.start()

        logger.info(f"对账任务已启动: {task_id}")
        return True

    def _run_reconcile(self, task_id: str):
        """在后台线程中运行对账"""
        try:
            task = self.get_task(task_id)
            if not task:
                return

            response_file_path = task['response_file_path']
            model_name = task.get('model_name', 'deepseek-v3')

            # 获取已分析的风险项
            risk_items_data = []
            if task.get('risk_items'):
                try:
                    risk_items_data = json.loads(task['risk_items'])
                except json.JSONDecodeError:
                    risk_items_data = []

            if not risk_items_data:
                logger.warning(f"没有风险项需要对账: {task_id}")
                self.update_task(
                    task_id,
                    status='reconcile_completed',
                    reconcile_progress=100,
                    reconcile_step='没有风险项需要对账'
                )
                return

            # 转换为 RiskItem 对象
            risk_items = [RiskItem(**item) for item in risk_items_data]

            # 定义进度回调
            def progress_callback(progress: int, message: str):
                self.update_task(
                    task_id,
                    reconcile_progress=progress,
                    reconcile_step=message
                )

            # 创建对账引擎并执行
            reconciler = Reconciler(model_name=model_name)
            reconcile_results = reconciler.reconcile(
                risk_items=risk_items,
                response_file_path=response_file_path,
                progress_callback=progress_callback
            )

            # 保存对账结果
            self._save_reconcile_results(task_id, risk_items, reconcile_results)

            logger.info(f"对账完成: {task_id}, 共 {len(reconcile_results)} 项")

        except Exception as e:
            logger.error(f"对账执行失败: {task_id}, 错误: {e}")
            self.update_task(
                task_id,
                status='reconcile_failed',
                reconcile_step=f"对账失败: {str(e)}"
            )

    def _save_reconcile_results(self,
                                 task_id: str,
                                 risk_items: List[RiskItem],
                                 reconcile_results: List[ReconcileResult]):
        """保存对账结果"""
        # 更新风险项的合规状态
        updated_items = []
        for item in risk_items:
            item_dict = item.to_dict()

            # 查找对应的对账结果
            for result in reconcile_results:
                if result.risk_item_id == risk_items.index(item):
                    item_dict['compliance_status'] = result.compliance_status
                    item_dict['compliance_note'] = result.overall_assessment
                    item_dict['match_score'] = result.match_score
                    item_dict['response_text'] = result.response_content[:500]
                    break

            updated_items.append(item_dict)

        # 对账结果序列化
        reconcile_results_json = json.dumps(
            [r.to_dict() for r in reconcile_results],
            ensure_ascii=False
        )

        # 更新数据库
        update_sql = """
        UPDATE risk_analysis_tasks SET
            status = 'reconcile_completed',
            reconcile_progress = 100,
            reconcile_step = '对账完成',
            risk_items = ?,
            reconcile_results = ?
        WHERE task_id = ?
        """

        risk_items_json = json.dumps(updated_items, ensure_ascii=False)

        self.db.execute_query(update_sql, (
            risk_items_json,
            reconcile_results_json,
            task_id
        ))


# 全局单例
_task_manager: Optional[RiskTaskManager] = None


def get_task_manager() -> RiskTaskManager:
    """获取任务管理器单例"""
    global _task_manager
    if _task_manager is None:
        _task_manager = RiskTaskManager()
    return _task_manager
