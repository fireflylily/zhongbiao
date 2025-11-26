#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户密码迁移脚本
将现有的硬编码密码逻辑迁移到数据库
"""

import sys
import sqlite3
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 安装bcrypt（如果未安装）
try:
    import bcrypt
except ImportError:
    print("正在安装bcrypt...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "bcrypt"])
    import bcrypt

# 数据库路径
DB_PATH = project_root / 'ai_tender_system' / 'data' / 'knowledge_base.db'


def hash_password(password: str) -> str:
    """使用bcrypt加密密码"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def migrate_passwords():
    """迁移现有用户的密码"""
    print(f"连接数据库: {DB_PATH}")

    # 检查数据库是否存在
    if not DB_PATH.exists():
        print(f"错误：数据库不存在: {DB_PATH}")
        return False

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        # 1. 检查password字段是否已存在
        cursor.execute("PRAGMA table_info(users)")
        columns = [row[1] for row in cursor.fetchall()]

        if 'password' not in columns:
            print("添加password字段...")
            cursor.execute("ALTER TABLE users ADD COLUMN password VARCHAR(255)")
            conn.commit()

        # 2. 查询所有用户
        cursor.execute("SELECT user_id, username FROM users")
        users = cursor.fetchall()

        print(f"找到 {len(users)} 个用户，开始迁移密码...")

        # 3. 为每个用户设置默认密码
        for user in users:
            user_id = user['user_id']
            username = user['username']

            # 根据旧的密码规则设置默认密码
            if username == 'admin':
                plain_password = 'admin123'
            else:
                plain_password = f'{username}123'

            # 加密密码
            hashed_password = hash_password(plain_password)

            # 更新数据库
            cursor.execute(
                "UPDATE users SET password = ? WHERE user_id = ?",
                (hashed_password, user_id)
            )

            print(f"  ✓ 已设置用户 {username} 的密码")

        # 提交更改
        conn.commit()
        print("\n✅ 密码迁移完成！")
        print("\n默认密码规则：")
        print("  - admin用户: admin123")
        print("  - 其他用户: {用户名}123")
        print("\n建议用户登录后立即修改密码。")

        return True

    except Exception as e:
        print(f"❌ 迁移失败: {e}")
        conn.rollback()
        return False

    finally:
        conn.close()


if __name__ == '__main__':
    success = migrate_passwords()
    sys.exit(0 if success else 1)
