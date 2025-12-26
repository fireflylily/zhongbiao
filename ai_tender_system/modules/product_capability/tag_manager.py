#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
核心能力标签管理器

用于管理产品能力标签（人工定义的能力大类），如：
- 风控产品
- 实修
- 免密
- 位置服务

每个企业独立维护自己的标签体系。
"""

import json
import logging
import sqlite3
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path


class TagManager:
    """核心能力标签管理器"""

    def __init__(self, db_path: str = None):
        """
        初始化标签管理器

        Args:
            db_path: 数据库路径，默认使用系统数据库
        """
        if db_path is None:
            db_path = str(Path(__file__).parent.parent.parent / "data" / "knowledge_base.db")
        self.db_path = db_path
        self.logger = logging.getLogger(self.__class__.__name__)

    def _get_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    # =========================================================================
    # 标签 CRUD 操作
    # =========================================================================

    def create_tag(
        self,
        company_id: int,
        tag_name: str,
        tag_code: str,
        parent_tag_id: int = None,
        description: str = None,
        example_keywords: List[str] = None,
        tag_order: int = 999
    ) -> int:
        """
        创建能力标签

        Args:
            company_id: 企业ID
            tag_name: 标签名称，如"风控产品"
            tag_code: 标签代码，如"risk_control"
            parent_tag_id: 父标签ID（可选）
            description: 标签描述
            example_keywords: 示例关键词列表
            tag_order: 显示顺序

        Returns:
            新创建的标签ID
        """
        conn = self._get_connection()
        try:
            # 计算层级
            tag_level = 1
            if parent_tag_id:
                cursor = conn.execute(
                    "SELECT tag_level FROM product_capability_tags WHERE tag_id = ?",
                    (parent_tag_id,)
                )
                parent = cursor.fetchone()
                if parent:
                    tag_level = parent['tag_level'] + 1

            cursor = conn.execute(
                """
                INSERT INTO product_capability_tags
                (company_id, tag_name, tag_code, parent_tag_id, description,
                 example_keywords, tag_order, tag_level)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    company_id,
                    tag_name,
                    tag_code,
                    parent_tag_id,
                    description,
                    json.dumps(example_keywords, ensure_ascii=False) if example_keywords else None,
                    tag_order,
                    tag_level
                )
            )
            conn.commit()
            tag_id = cursor.lastrowid
            self.logger.info(f"创建标签成功: {tag_name} (ID: {tag_id})")
            return tag_id
        except sqlite3.IntegrityError as e:
            self.logger.error(f"创建标签失败（重复）: {tag_code} - {e}")
            raise ValueError(f"标签代码已存在: {tag_code}")
        finally:
            conn.close()

    def get_tag(self, tag_id: int) -> Optional[Dict[str, Any]]:
        """获取单个标签"""
        conn = self._get_connection()
        try:
            cursor = conn.execute(
                "SELECT * FROM product_capability_tags WHERE tag_id = ?",
                (tag_id,)
            )
            row = cursor.fetchone()
            if row:
                return self._row_to_dict(row)
            return None
        finally:
            conn.close()

    def get_tags_by_company(
        self,
        company_id: int,
        include_inactive: bool = False
    ) -> List[Dict[str, Any]]:
        """
        获取企业的所有标签

        Args:
            company_id: 企业ID
            include_inactive: 是否包含已禁用的标签

        Returns:
            标签列表
        """
        conn = self._get_connection()
        try:
            sql = """
                SELECT * FROM product_capability_tags
                WHERE company_id = ?
            """
            if not include_inactive:
                sql += " AND is_active = 1"
            sql += " ORDER BY tag_level, tag_order, tag_name"

            cursor = conn.execute(sql, (company_id,))
            return [self._row_to_dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def get_tags_tree(self, company_id: int) -> List[Dict[str, Any]]:
        """
        获取企业的标签树结构

        Args:
            company_id: 企业ID

        Returns:
            树形结构的标签列表
        """
        tags = self.get_tags_by_company(company_id)

        # 构建树
        tag_map = {tag['tag_id']: tag for tag in tags}
        root_tags = []

        for tag in tags:
            tag['children'] = []
            parent_id = tag.get('parent_tag_id')
            if parent_id and parent_id in tag_map:
                tag_map[parent_id]['children'].append(tag)
            else:
                root_tags.append(tag)

        return root_tags

    def update_tag(
        self,
        tag_id: int,
        tag_name: str = None,
        description: str = None,
        example_keywords: List[str] = None,
        tag_order: int = None,
        is_active: bool = None
    ) -> bool:
        """更新标签信息"""
        conn = self._get_connection()
        try:
            updates = []
            params = []

            if tag_name is not None:
                updates.append("tag_name = ?")
                params.append(tag_name)
            if description is not None:
                updates.append("description = ?")
                params.append(description)
            if example_keywords is not None:
                updates.append("example_keywords = ?")
                params.append(json.dumps(example_keywords, ensure_ascii=False))
            if tag_order is not None:
                updates.append("tag_order = ?")
                params.append(tag_order)
            if is_active is not None:
                updates.append("is_active = ?")
                params.append(is_active)

            if not updates:
                return False

            updates.append("updated_at = ?")
            params.append(datetime.now().isoformat())
            params.append(tag_id)

            conn.execute(
                f"UPDATE product_capability_tags SET {', '.join(updates)} WHERE tag_id = ?",
                params
            )
            conn.commit()
            return True
        finally:
            conn.close()

    def delete_tag(self, tag_id: int, force: bool = False) -> bool:
        """
        删除标签

        Args:
            tag_id: 标签ID
            force: 是否强制删除（包括子标签和关联能力）

        Returns:
            是否删除成功
        """
        conn = self._get_connection()
        try:
            # 检查是否有子标签
            cursor = conn.execute(
                "SELECT COUNT(*) as cnt FROM product_capability_tags WHERE parent_tag_id = ?",
                (tag_id,)
            )
            if cursor.fetchone()['cnt'] > 0 and not force:
                raise ValueError("标签下有子标签，无法删除。请先删除子标签或使用强制删除。")

            # 检查是否有关联能力
            cursor = conn.execute(
                "SELECT COUNT(*) as cnt FROM product_capabilities_index WHERE tag_id = ?",
                (tag_id,)
            )
            if cursor.fetchone()['cnt'] > 0 and not force:
                raise ValueError("标签下有关联能力，无法删除。请先解除关联或使用强制删除。")

            if force:
                # 递归删除子标签
                conn.execute(
                    "DELETE FROM product_capability_tags WHERE parent_tag_id = ?",
                    (tag_id,)
                )
                # 解除能力关联
                conn.execute(
                    "UPDATE product_capabilities_index SET tag_id = NULL WHERE tag_id = ?",
                    (tag_id,)
                )

            conn.execute(
                "DELETE FROM product_capability_tags WHERE tag_id = ?",
                (tag_id,)
            )
            conn.commit()
            return True
        finally:
            conn.close()

    # =========================================================================
    # 批量操作
    # =========================================================================

    def init_default_tags(self, company_id: int) -> List[int]:
        """
        为企业初始化默认标签体系

        基于案例库中已有的分类（风控产品、实修、免密、风控位置）

        Args:
            company_id: 企业ID

        Returns:
            创建的标签ID列表
        """
        default_tags = [
            {
                "tag_name": "风控产品",
                "tag_code": "risk_control",
                "description": "风控相关产品和服务",
                "example_keywords": ["风控", "反欺诈", "信用评估", "风险监控", "实时决策"],
                "tag_order": 1
            },
            {
                "tag_name": "实修",
                "tag_code": "repair_service",
                "description": "实修服务",
                "example_keywords": ["实修", "维修", "售后", "上门服务"],
                "tag_order": 2
            },
            {
                "tag_name": "免密",
                "tag_code": "passwordless",
                "description": "免密支付/认证服务",
                "example_keywords": ["免密", "免密支付", "快捷支付", "无感支付"],
                "tag_order": 3
            },
            {
                "tag_name": "风控位置",
                "tag_code": "location_risk",
                "description": "位置风控服务",
                "example_keywords": ["位置", "定位", "轨迹", "位置核验", "地理围栏"],
                "tag_order": 4
            },
            {
                "tag_name": "大数据",
                "tag_code": "big_data",
                "description": "大数据分析和处理",
                "example_keywords": ["大数据", "数据分析", "数据挖掘", "数据治理"],
                "tag_order": 5
            },
            {
                "tag_name": "云服务",
                "tag_code": "cloud_service",
                "description": "云计算和云服务",
                "example_keywords": ["云计算", "云平台", "云服务", "私有云", "混合云"],
                "tag_order": 6
            }
        ]

        created_ids = []
        for tag_info in default_tags:
            try:
                tag_id = self.create_tag(
                    company_id=company_id,
                    **tag_info
                )
                created_ids.append(tag_id)
            except ValueError as e:
                self.logger.warning(f"标签已存在，跳过: {tag_info['tag_code']} - {e}")

        return created_ids

    def import_tags(
        self,
        company_id: int,
        tags_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        批量导入标签

        Args:
            company_id: 企业ID
            tags_data: 标签数据列表

        Returns:
            导入结果统计
        """
        result = {
            "success": 0,
            "failed": 0,
            "errors": []
        }

        for tag_data in tags_data:
            try:
                self.create_tag(
                    company_id=company_id,
                    tag_name=tag_data['tag_name'],
                    tag_code=tag_data['tag_code'],
                    parent_tag_id=tag_data.get('parent_tag_id'),
                    description=tag_data.get('description'),
                    example_keywords=tag_data.get('example_keywords'),
                    tag_order=tag_data.get('tag_order', 999)
                )
                result['success'] += 1
            except Exception as e:
                result['failed'] += 1
                result['errors'].append({
                    "tag_code": tag_data.get('tag_code'),
                    "error": str(e)
                })

        return result

    def export_tags(self, company_id: int) -> List[Dict[str, Any]]:
        """导出企业的所有标签"""
        return self.get_tags_by_company(company_id, include_inactive=True)

    # =========================================================================
    # 辅助方法
    # =========================================================================

    def _row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        """将数据库行转换为字典"""
        d = dict(row)
        # 解析JSON字段
        if d.get('example_keywords'):
            try:
                d['example_keywords'] = json.loads(d['example_keywords'])
            except:
                d['example_keywords'] = []
        return d

    def get_tag_by_code(self, company_id: int, tag_code: str) -> Optional[Dict[str, Any]]:
        """根据代码获取标签"""
        conn = self._get_connection()
        try:
            cursor = conn.execute(
                "SELECT * FROM product_capability_tags WHERE company_id = ? AND tag_code = ?",
                (company_id, tag_code)
            )
            row = cursor.fetchone()
            if row:
                return self._row_to_dict(row)
            return None
        finally:
            conn.close()

    def search_tags(
        self,
        company_id: int,
        keyword: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        搜索标签

        Args:
            company_id: 企业ID
            keyword: 搜索关键词
            limit: 返回数量限制

        Returns:
            匹配的标签列表
        """
        conn = self._get_connection()
        try:
            cursor = conn.execute(
                """
                SELECT * FROM product_capability_tags
                WHERE company_id = ? AND is_active = 1
                  AND (tag_name LIKE ? OR tag_code LIKE ? OR description LIKE ?)
                ORDER BY tag_order
                LIMIT ?
                """,
                (company_id, f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", limit)
            )
            return [self._row_to_dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
