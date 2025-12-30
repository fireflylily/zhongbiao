"""
技术方案生成任务管理器
负责任务的创建、状态更新、持久化和恢复
"""

import json
import uuid
import sqlite3
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from pathlib import Path
from dataclasses import dataclass, asdict
from contextlib import contextmanager

from ...common.logger import get_module_logger
from ...common.config import get_config

logger = get_module_logger("task_manager")


# 阶段顺序定义
PHASE_ORDER = [
    "scoring_extraction",
    "product_matching",
    "strategy_planning",
    "material_retrieval",
    "outline_generation",
    "content_writing",
    "expert_review",
    "iteration"
]

# 阶段进度权重
PHASE_WEIGHTS = {
    "scoring_extraction": 10,
    "product_matching": 10,
    "strategy_planning": 10,
    "material_retrieval": 10,
    "outline_generation": 15,
    "content_writing": 30,
    "expert_review": 10,
    "iteration": 5
}


@dataclass
class TaskConfig:
    """任务配置"""
    generation_mode: str = "quality_first"
    ai_model: str = "deepseek-v3"
    page_count: int = 200
    crew_config: Dict = None
    tender_file_path: str = None


class TechProposalTaskManager:
    """
    技术方案生成任务管理器

    功能:
    - 创建和管理任务
    - 持久化任务状态到数据库
    - 支持断点恢复
    - 记录智能体执行日志
    """

    # 默认恢复时效(小时)
    DEFAULT_RESUME_HOURS = 24

    def __init__(self, db_path: Optional[str] = None):
        config = get_config()
        self.db_path = db_path or str(config.get_path('data') / 'knowledge_base.db')
        self.logger = logger

        # 确保表结构存在
        self._ensure_tables()

    @contextmanager
    def _get_connection(self):
        """获取数据库连接"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            self.logger.error(f"数据库操作失败: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def _ensure_tables(self):
        """确保任务相关表存在"""
        schema_file = Path(__file__).parent.parent.parent / 'database' / 'tech_proposal_task_schema.sql'

        if not schema_file.exists():
            self.logger.warning(f"Schema文件不存在: {schema_file}")
            return

        try:
            with self._get_connection() as conn:
                with open(schema_file, 'r', encoding='utf-8') as f:
                    schema_sql = f.read()
                conn.executescript(schema_sql)
                conn.commit()
                self.logger.info("技术方案任务表结构已初始化")
        except Exception as e:
            self.logger.error(f"初始化任务表结构失败: {e}")

    def generate_task_id(self) -> str:
        """生成任务ID"""
        return str(uuid.uuid4())[:8]

    def create_task(
        self,
        project_id: int,
        company_id: int = None,
        generation_mode: str = "quality_first",
        ai_model: str = "deepseek-v3",
        crew_config: Dict = None,
        tender_file_path: str = None,
        page_count: int = 200
    ) -> str:
        """
        创建新任务

        Args:
            project_id: 项目ID
            company_id: 公司ID
            generation_mode: 生成模式
            ai_model: AI模型
            crew_config: Crew配置
            tender_file_path: 招标文件路径
            page_count: 目标页数

        Returns:
            任务ID
        """
        task_id = self.generate_task_id()
        now = datetime.now()
        expires_at = now + timedelta(hours=self.DEFAULT_RESUME_HOURS)

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO tech_proposal_tasks (
                        task_id, project_id, company_id,
                        generation_mode, ai_model, crew_config,
                        tender_file_path, page_count,
                        overall_status, current_phase, progress_percentage,
                        phases_completed, phase_results,
                        can_resume, created_at, expires_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    task_id, project_id, company_id,
                    generation_mode, ai_model,
                    json.dumps(crew_config or {}, ensure_ascii=False),
                    tender_file_path, page_count,
                    "pending", None, 0.0,
                    json.dumps([]), json.dumps({}),
                    True, now.isoformat(), expires_at.isoformat()
                ))
                conn.commit()

            self.logger.info(f"创建任务成功: {task_id} (项目ID: {project_id})")
            return task_id

        except Exception as e:
            self.logger.error(f"创建任务失败: {e}")
            raise

    def get_task(self, task_id: str) -> Optional[Dict]:
        """获取任务信息"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM tech_proposal_tasks WHERE task_id = ?
                """, (task_id,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            self.logger.error(f"获取任务失败: {e}")
            return None

    def get_tasks_by_project(self, project_id: int, limit: int = 10) -> List[Dict]:
        """获取项目的任务列表"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM tech_proposal_tasks
                    WHERE project_id = ?
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (project_id, limit))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            self.logger.error(f"获取项目任务列表失败: {e}")
            return []

    def get_resumable_tasks(self, project_id: int = None) -> List[Dict]:
        """
        获取可恢复的任务列表

        Args:
            project_id: 可选，按项目过滤

        Returns:
            可恢复任务列表
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                if project_id:
                    cursor.execute("""
                        SELECT * FROM v_resumable_tasks
                        WHERE project_id = ?
                    """, (project_id,))
                else:
                    cursor.execute("SELECT * FROM v_resumable_tasks")

                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            self.logger.error(f"获取可恢复任务失败: {e}")
            return []

    def start_task(self, task_id: str) -> bool:
        """开始执行任务"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE tech_proposal_tasks
                    SET overall_status = 'running',
                        started_at = ?
                    WHERE task_id = ? AND overall_status IN ('pending', 'failed')
                """, (datetime.now().isoformat(), task_id))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            self.logger.error(f"启动任务失败: {e}")
            return False

    def update_phase(
        self,
        task_id: str,
        phase_name: str,
        status: str,
        result: Dict = None,
        error: str = None
    ) -> bool:
        """
        更新阶段执行状态

        Args:
            task_id: 任务ID
            phase_name: 阶段名称
            status: 状态 (success/failed/skipped)
            result: 阶段结果摘要
            error: 错误信息
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                # 获取当前任务信息
                cursor.execute("""
                    SELECT phases_completed, phase_results, progress_percentage
                    FROM tech_proposal_tasks WHERE task_id = ?
                """, (task_id,))
                row = cursor.fetchone()
                if not row:
                    return False

                phases_completed = json.loads(row['phases_completed'] or '[]')
                phase_results = json.loads(row['phase_results'] or '{}')

                # 更新阶段结果
                phase_results[phase_name] = {
                    "status": status,
                    "end_time": datetime.now().isoformat(),
                    "error": error
                }

                # 如果成功，添加到已完成列表
                if status == "success" and phase_name not in phases_completed:
                    phases_completed.append(phase_name)

                # 计算进度
                progress = self._calculate_progress(phases_completed)

                # 确定整体状态
                overall_status = "running"
                if status == "failed":
                    overall_status = "failed"
                elif phase_name == PHASE_ORDER[-1] and status == "success":
                    overall_status = "completed"

                # 更新数据库
                cursor.execute("""
                    UPDATE tech_proposal_tasks
                    SET current_phase = ?,
                        phases_completed = ?,
                        phase_results = ?,
                        progress_percentage = ?,
                        overall_status = ?,
                        last_error = ?,
                        last_error_time = ?
                    WHERE task_id = ?
                """, (
                    phase_name,
                    json.dumps(phases_completed),
                    json.dumps(phase_results, ensure_ascii=False),
                    progress,
                    overall_status,
                    error if status == "failed" else None,
                    datetime.now().isoformat() if status == "failed" else None,
                    task_id
                ))
                conn.commit()

                self.logger.info(f"任务 {task_id} 阶段 {phase_name} 状态更新为 {status}")
                return True

        except Exception as e:
            self.logger.error(f"更新阶段状态失败: {e}")
            return False

    def _calculate_progress(self, phases_completed: List[str]) -> float:
        """计算任务进度百分比"""
        total_weight = sum(PHASE_WEIGHTS.values())
        completed_weight = sum(
            PHASE_WEIGHTS.get(phase, 0)
            for phase in phases_completed
        )
        return round(completed_weight / total_weight * 100, 1)

    def save_state(self, task_id: str, state_data: Dict) -> bool:
        """
        保存任务中间状态(用于恢复)

        Args:
            task_id: 任务ID
            state_data: 状态数据(CrewState序列化)
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE tech_proposal_tasks
                    SET saved_state = ?
                    WHERE task_id = ?
                """, (json.dumps(state_data, ensure_ascii=False), task_id))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            self.logger.error(f"保存任务状态失败: {e}")
            return False

    def load_state(self, task_id: str) -> Optional[Dict]:
        """加载任务中间状态"""
        task = self.get_task(task_id)
        if task and task.get('saved_state'):
            try:
                return json.loads(task['saved_state'])
            except json.JSONDecodeError:
                return None
        return None

    def get_completed_phases(self, task_id: str) -> List[str]:
        """获取已完成的阶段列表"""
        task = self.get_task(task_id)
        if task and task.get('phases_completed'):
            try:
                return json.loads(task['phases_completed'])
            except json.JSONDecodeError:
                return []
        return []

    def get_next_phase(self, task_id: str) -> Optional[str]:
        """获取下一个待执行的阶段"""
        completed = set(self.get_completed_phases(task_id))
        for phase in PHASE_ORDER:
            if phase not in completed:
                return phase
        return None

    def can_resume(self, task_id: str) -> bool:
        """检查任务是否可恢复"""
        task = self.get_task(task_id)
        if not task:
            return False

        # 检查状态
        if task['overall_status'] not in ('failed', 'pending'):
            return False

        # 检查是否已过期
        if task.get('expires_at'):
            try:
                expires = datetime.fromisoformat(task['expires_at'])
                if datetime.now() > expires:
                    return False
            except ValueError:
                pass

        return task.get('can_resume', False)

    def complete_task(self, task_id: str, output_files: List[str] = None, final_score: float = None) -> bool:
        """标记任务完成"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE tech_proposal_tasks
                    SET overall_status = 'completed',
                        completed_at = ?,
                        output_files = ?,
                        final_score = ?,
                        can_resume = FALSE,
                        progress_percentage = 100.0
                    WHERE task_id = ?
                """, (
                    datetime.now().isoformat(),
                    json.dumps(output_files or []),
                    final_score,
                    task_id
                ))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            self.logger.error(f"完成任务失败: {e}")
            return False

    def fail_task(self, task_id: str, error: str) -> bool:
        """标记任务失败"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE tech_proposal_tasks
                    SET overall_status = 'failed',
                        last_error = ?,
                        last_error_time = ?
                    WHERE task_id = ?
                """, (error, datetime.now().isoformat(), task_id))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            self.logger.error(f"标记任务失败失败: {e}")
            return False

    def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE tech_proposal_tasks
                    SET overall_status = 'cancelled',
                        completed_at = ?,
                        can_resume = FALSE
                    WHERE task_id = ? AND overall_status IN ('pending', 'running', 'failed')
                """, (datetime.now().isoformat(), task_id))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            self.logger.error(f"取消任务失败: {e}")
            return False

    # =========================
    # 执行日志管理
    # =========================

    def log_agent_execution(
        self,
        task_id: str,
        agent_name: str,
        phase_name: str,
        status: str,
        attempt_number: int = 1,
        start_time: datetime = None,
        end_time: datetime = None,
        duration_ms: int = None,
        input_summary: str = None,
        output_summary: str = None,
        error_message: str = None,
        error_traceback: str = None,
        retry_delay_ms: int = None
    ) -> int:
        """
        记录智能体执行日志

        Returns:
            日志ID
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO agent_execution_logs (
                        task_id, agent_name, phase_name, status, attempt_number,
                        start_time, end_time, duration_ms,
                        input_summary, output_summary,
                        error_message, error_traceback, retry_delay_ms
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    task_id, agent_name, phase_name, status, attempt_number,
                    start_time.isoformat() if start_time else None,
                    end_time.isoformat() if end_time else None,
                    duration_ms,
                    input_summary, output_summary,
                    error_message, error_traceback, retry_delay_ms
                ))
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            self.logger.error(f"记录执行日志失败: {e}")
            return 0

    def get_execution_logs(self, task_id: str) -> List[Dict]:
        """获取任务的执行日志"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM agent_execution_logs
                    WHERE task_id = ?
                    ORDER BY created_at ASC
                """, (task_id,))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            self.logger.error(f"获取执行日志失败: {e}")
            return []

    def get_task_stats(self, task_id: str) -> Optional[Dict]:
        """获取任务执行统计"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM v_task_execution_stats WHERE task_id = ?
                """, (task_id,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            self.logger.error(f"获取任务统计失败: {e}")
            return None

    # =========================
    # 清理过期任务
    # =========================

    def cleanup_expired_tasks(self, days: int = 7) -> int:
        """
        清理过期任务

        Args:
            days: 保留天数

        Returns:
            删除的任务数
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                # 删除过期的已完成/已取消任务
                cursor.execute("""
                    DELETE FROM tech_proposal_tasks
                    WHERE overall_status IN ('completed', 'cancelled')
                      AND created_at < datetime('now', '-' || ? || ' days')
                """, (days,))

                deleted = cursor.rowcount
                conn.commit()

                if deleted > 0:
                    self.logger.info(f"清理了 {deleted} 个过期任务")

                return deleted
        except Exception as e:
            self.logger.error(f"清理过期任务失败: {e}")
            return 0


# 全局实例
_task_manager_instance = None


def get_task_manager() -> TechProposalTaskManager:
    """获取任务管理器实例"""
    global _task_manager_instance
    if _task_manager_instance is None:
        _task_manager_instance = TechProposalTaskManager()
    return _task_manager_instance
