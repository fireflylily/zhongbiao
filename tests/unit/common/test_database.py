"""
测试数据库模块

测试 ai_tender_system/common/database.py
"""

import pytest
import sqlite3
import tempfile
from pathlib import Path


class TestKnowledgeBaseDB:
    """测试 KnowledgeBaseDB 类"""

    def test_init_with_custom_path(self, temp_dir):
        """测试使用自定义路径初始化数据库"""
        from ai_tender_system.common.database import KnowledgeBaseDB

        db_path = temp_dir / "test.db"
        db = KnowledgeBaseDB(str(db_path))

        assert db.db_path == str(db_path)
        assert Path(db.db_path).exists()

    def test_init_creates_directory_if_not_exists(self, temp_dir):
        """测试数据库初始化时自动创建目录"""
        from ai_tender_system.common.database import KnowledgeBaseDB

        # 创建不存在的子目录路径
        db_path = temp_dir / "subdir" / "test.db"
        db = KnowledgeBaseDB(str(db_path))

        assert Path(db.db_path).parent.exists()
        assert Path(db.db_path).exists()

    def test_database_file_created(self, temp_dir):
        """测试数据库文件被创建"""
        from ai_tender_system.common.database import KnowledgeBaseDB

        db_path = temp_dir / "test.db"
        KnowledgeBaseDB(str(db_path))

        assert db_path.exists()
        assert db_path.is_file()

    def test_database_connection_works(self, temp_dir):
        """测试数据库连接可用"""
        from ai_tender_system.common.database import KnowledgeBaseDB

        db_path = temp_dir / "test.db"
        db = KnowledgeBaseDB(str(db_path))

        # 尝试执行简单查询
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        conn.close()

        assert result[0] == 1


class TestKnowledgeBaseDBMethods:
    """测试 KnowledgeBaseDB 的基本数据库操作"""

    def test_execute_query_select(self, temp_db):
        """测试执行 SELECT 查询"""
        from ai_tender_system.common.database import KnowledgeBaseDB

        db = KnowledgeBaseDB(str(temp_db))

        # 使用 get_connection 创建测试表
        with db.get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS test_table (
                    id INTEGER PRIMARY KEY,
                    name TEXT
                )
            """)
            conn.execute("INSERT INTO test_table (name) VALUES ('test1')")
            conn.execute("INSERT INTO test_table (name) VALUES ('test2')")
            conn.commit()

        # 查询数据
        results = db.execute_query("SELECT * FROM test_table")

        assert len(results) == 2
        assert results[0]['name'] == 'test1'
        assert results[1]['name'] == 'test2'

    def test_execute_query_with_params(self, temp_db):
        """测试带参数的查询"""
        from ai_tender_system.common.database import KnowledgeBaseDB

        db = KnowledgeBaseDB(str(temp_db))

        # 创建测试表并插入数据（使用不冲突的表名）
        with db.get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS test_persons (
                    id INTEGER PRIMARY KEY,
                    person_name TEXT,
                    age INTEGER
                )
            """)
            conn.execute("INSERT INTO test_persons (person_name, age) VALUES (?, ?)", ('Alice', 30))
            conn.execute("INSERT INTO test_persons (person_name, age) VALUES (?, ?)", ('Bob', 25))
            conn.commit()

        # 参数化查询
        results = db.execute_query(
            "SELECT * FROM test_persons WHERE age > ?",
            (26,)
        )

        assert len(results) == 1
        assert results[0]['person_name'] == 'Alice'

    def test_execute_query_insert(self, temp_db):
        """测试 INSERT 操作"""
        from ai_tender_system.common.database import KnowledgeBaseDB

        db = KnowledgeBaseDB(str(temp_db))

        with db.get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS items (
                    id INTEGER PRIMARY KEY,
                    title TEXT
                )
            """)
            conn.commit()

        # 使用 execute_query 执行插入
        db.execute_query("INSERT INTO items (title) VALUES ('Item 1')")

        # 验证插入
        results = db.execute_query("SELECT * FROM items")
        assert len(results) == 1
        assert results[0]['title'] == 'Item 1'

    def test_execute_query_update(self, temp_db):
        """测试 UPDATE 操作"""
        from ai_tender_system.common.database import KnowledgeBaseDB

        db = KnowledgeBaseDB(str(temp_db))

        with db.get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS test_inventory (
                    id INTEGER PRIMARY KEY,
                    item_name TEXT,
                    price REAL
                )
            """)
            conn.execute("INSERT INTO test_inventory (item_name, price) VALUES ('Product A', 10.0)")
            conn.commit()

        # 更新数据
        db.execute_query("UPDATE test_inventory SET price = ? WHERE item_name = ?", (15.0, 'Product A'))

        # 验证更新
        results = db.execute_query("SELECT * FROM test_inventory WHERE item_name = ?", ('Product A',))
        assert results[0]['price'] == 15.0

    def test_execute_query_delete(self, temp_db):
        """测试 DELETE 操作"""
        from ai_tender_system.common.database import KnowledgeBaseDB

        db = KnowledgeBaseDB(str(temp_db))

        with db.get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY,
                    task_name TEXT
                )
            """)
            conn.execute("INSERT INTO tasks (task_name) VALUES ('Task 1')")
            conn.execute("INSERT INTO tasks (task_name) VALUES ('Task 2')")
            conn.commit()

        # 删除数据
        db.execute_query("DELETE FROM tasks WHERE task_name = ?", ('Task 1',))

        # 验证删除
        results = db.execute_query("SELECT * FROM tasks")
        assert len(results) == 1
        assert results[0]['task_name'] == 'Task 2'

    def test_execute_query_returns_dict(self, temp_db):
        """测试查询结果返回字典格式"""
        from ai_tender_system.common.database import KnowledgeBaseDB

        db = KnowledgeBaseDB(str(temp_db))

        with db.get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS books (
                    id INTEGER PRIMARY KEY,
                    title TEXT,
                    author TEXT
                )
            """)
            conn.execute("INSERT INTO books (title, author) VALUES ('Book 1', 'Author 1')")
            conn.commit()

        results = db.execute_query("SELECT * FROM books")

        # 验证返回的是字典
        assert isinstance(results[0], dict)
        assert 'id' in results[0]
        assert 'title' in results[0]
        assert 'author' in results[0]

    def test_fetch_one_parameter(self, temp_db):
        """测试 fetch_one 参数"""
        from ai_tender_system.common.database import KnowledgeBaseDB

        db = KnowledgeBaseDB(str(temp_db))

        with db.get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS test_single (
                    id INTEGER PRIMARY KEY,
                    value TEXT
                )
            """)
            conn.execute("INSERT INTO test_single (value) VALUES ('single')")
            conn.commit()

        # 测试 fetch_one=True
        result = db.execute_query("SELECT * FROM test_single", fetch_one=True)
        assert isinstance(result, dict)
        assert result['value'] == 'single'

        # 测试 fetch_one=False（默认）
        results = db.execute_query("SELECT * FROM test_single")
        assert isinstance(results, list)
        assert len(results) == 1

    def test_empty_query_result(self, temp_db):
        """测试空查询结果"""
        from ai_tender_system.common.database import KnowledgeBaseDB

        db = KnowledgeBaseDB(str(temp_db))

        with db.get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS empty_table (
                    id INTEGER PRIMARY KEY,
                    data TEXT
                )
            """)
            conn.commit()

        results = db.execute_query("SELECT * FROM empty_table")
        assert results == []
        assert isinstance(results, list)

    def test_get_connection_context_manager(self, temp_db):
        """测试 get_connection 上下文管理器"""
        from ai_tender_system.common.database import KnowledgeBaseDB

        db = KnowledgeBaseDB(str(temp_db))

        # 测试上下文管理器正常工作
        with db.get_connection() as conn:
            cursor = conn.execute("SELECT 1")
            result = cursor.fetchone()
            assert result[0] == 1


class TestDatabaseHelpers:
    """测试数据库辅助方法"""

    def test_table_exists(self, temp_db):
        """测试检查表是否存在"""
        from ai_tender_system.common.database import KnowledgeBaseDB

        db = KnowledgeBaseDB(str(temp_db))

        # 创建表
        with db.get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS test_exists (
                    id INTEGER PRIMARY KEY
                )
            """)
            conn.commit()

        # 检查表是否存在
        conn = sqlite3.connect(str(temp_db))
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='test_exists'
        """)
        result = cursor.fetchone()
        conn.close()

        assert result is not None
        assert result[0] == 'test_exists'

    def test_get_table_info(self, temp_db):
        """测试获取表信息"""
        from ai_tender_system.common.database import KnowledgeBaseDB

        db = KnowledgeBaseDB(str(temp_db))

        with db.get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_info (
                    id INTEGER PRIMARY KEY,
                    username TEXT NOT NULL,
                    email TEXT UNIQUE
                )
            """)
            conn.commit()

        # 获取表信息
        conn = sqlite3.connect(str(temp_db))
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(user_info)")
        columns = cursor.fetchall()
        conn.close()

        assert len(columns) == 3
        column_names = [col[1] for col in columns]
        assert 'id' in column_names
        assert 'username' in column_names
        assert 'email' in column_names


class TestDatabaseEdgeCases:
    """测试边界情况和异常处理"""

    def test_invalid_sql_syntax(self, temp_db):
        """测试无效的 SQL 语法"""
        from ai_tender_system.common.database import KnowledgeBaseDB

        db = KnowledgeBaseDB(str(temp_db))

        with pytest.raises(sqlite3.Error):
            with db.get_connection() as conn:
                conn.execute("INVALID SQL SYNTAX")

    def test_missing_table(self, temp_db):
        """测试查询不存在的表"""
        from ai_tender_system.common.database import KnowledgeBaseDB

        db = KnowledgeBaseDB(str(temp_db))

        with pytest.raises(sqlite3.Error):
            db.execute_query("SELECT * FROM non_existent_table")

    def test_sql_injection_prevention(self, temp_db):
        """测试 SQL 注入防护（使用参数化查询）"""
        from ai_tender_system.common.database import KnowledgeBaseDB

        db = KnowledgeBaseDB(str(temp_db))

        with db.get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS secure_table (
                    id INTEGER PRIMARY KEY,
                    value TEXT
                )
            """)
            conn.execute("INSERT INTO secure_table (value) VALUES ('safe')")
            conn.commit()

        # 尝试 SQL 注入（应该失败）
        malicious_input = "'; DROP TABLE secure_table; --"
        results = db.execute_query(
            "SELECT * FROM secure_table WHERE value = ?",
            (malicious_input,)
        )

        # 表应该仍然存在
        assert results == []
        all_results = db.execute_query("SELECT * FROM secure_table")
        assert len(all_results) == 1


class TestDatabaseConcurrency:
    """测试并发访问"""

    def test_multiple_connections(self, temp_db):
        """测试多个连接同时访问"""
        from ai_tender_system.common.database import KnowledgeBaseDB

        db1 = KnowledgeBaseDB(str(temp_db))
        db2 = KnowledgeBaseDB(str(temp_db))

        # 第一个连接创建表并插入数据
        with db1.get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS shared_table (
                    id INTEGER PRIMARY KEY,
                    data TEXT
                )
            """)
            conn.execute("INSERT INTO shared_table (data) VALUES ('data1')")
            conn.commit()

        # 第二个连接应该能看到数据
        results = db2.execute_query("SELECT * FROM shared_table")
        assert len(results) == 1
        assert results[0]['data'] == 'data1'
