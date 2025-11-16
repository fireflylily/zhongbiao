#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
添加用户到知识库系统
为智慧足迹数据科技有限公司添加 huangjf 和 lvhe 两个用户
"""

import os
import sqlite3
import logging
from pathlib import Path

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def add_users_to_company():
    """
    为智慧足迹公司添加两个新用户: huangjf 和 lvhe
    """
    # 数据库路径
    db_path = Path(__file__).parent.parent / 'data' / 'knowledge_base.db'

    if not db_path.exists():
        logger.error(f"数据库文件不存在: {db_path}")
        return False

    logger.info(f"连接到数据库: {db_path}")

    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # 验证智慧足迹公司是否存在
        cursor.execute("SELECT company_id, company_name FROM companies WHERE company_id = 2")
        company = cursor.fetchone()

        if not company:
            logger.error("未找到智慧足迹公司 (company_id=2)")
            return False

        logger.info(f"找到公司: {company[1]} (ID: {company[0]})")

        # 验证内部员工角色是否存在
        cursor.execute("SELECT role_id, role_name FROM user_roles WHERE role_id = 2")
        role = cursor.fetchone()

        if not role:
            logger.error("未找到内部员工角色 (role_id=2)")
            return False

        logger.info(f"找到角色: {role[1]} (ID: {role[0]})")

        # 要添加的用户列表
        users_to_add = [
            {
                'username': 'huangjf',
                'email': 'huangjf@zhihuizuji.com',
                'role_id': 2,  # 内部员工
                'company_id': 2,  # 智慧足迹
                'is_active': True
            },
            {
                'username': 'lvhe',
                'email': 'lvhe@zhihuizuji.com',
                'role_id': 2,  # 内部员工
                'company_id': 2,  # 智慧足迹
                'is_active': True
            }
        ]

        # 插入用户
        success_count = 0
        for user in users_to_add:
            try:
                # 检查用户是否已存在
                cursor.execute("SELECT user_id FROM users WHERE username = ?", (user['username'],))
                existing = cursor.fetchone()

                if existing:
                    logger.warning(f"用户 {user['username']} 已存在 (user_id={existing[0]}), 跳过")
                    continue

                # 插入新用户
                cursor.execute("""
                    INSERT INTO users (username, email, role_id, company_id, is_active)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    user['username'],
                    user['email'],
                    user['role_id'],
                    user['company_id'],
                    user['is_active']
                ))

                user_id = cursor.lastrowid
                success_count += 1
                logger.info(f"✓ 成功添加用户: {user['username']} (user_id={user_id}, email={user['email']})")

            except sqlite3.IntegrityError as e:
                logger.error(f"✗ 添加用户 {user['username']} 失败: {e}")
                continue

        # 提交事务
        conn.commit()
        logger.info(f"\n总共成功添加 {success_count} 个用户")

        # 显示所有智慧足迹公司的用户
        logger.info("\n=== 智慧足迹公司的所有用户 ===")
        cursor.execute("""
            SELECT u.user_id, u.username, u.email, r.role_name, u.is_active
            FROM users u
            JOIN user_roles r ON u.role_id = r.role_id
            WHERE u.company_id = 2
            ORDER BY u.user_id
        """)

        users = cursor.fetchall()
        for user in users:
            status = "✓ 激活" if user[4] else "✗ 停用"
            logger.info(f"  ID:{user[0]:3d} | {user[1]:15s} | {user[2]:30s} | {user[3]:10s} | {status}")

        return True

    except sqlite3.Error as e:
        logger.error(f"数据库操作失败: {e}")
        return False

    finally:
        if 'conn' in locals():
            conn.close()
            logger.info("\n数据库连接已关闭")


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("开始添加用户到智慧足迹公司")
    logger.info("=" * 60)

    success = add_users_to_company()

    if success:
        logger.info("\n✓ 用户添加完成!")
    else:
        logger.error("\n✗ 用户添加失败!")
        exit(1)
