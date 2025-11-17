# ABTest 用户管理模块

这是一个完整的用户和角色管理系统，提供了用户增删改查、角色管理和权限控制功能。

## 功能特性

### 用户管理
- ✅ 创建新用户
- ✅ 查看用户列表（支持分页和搜索）
- ✅ 编辑用户信息
- ✅ 删除用户
- ✅ 激活/禁用用户
- ✅ 关联用户到公司
- ✅ 分配角色权限

### 角色管理
- ✅ 创建新角色
- ✅ 查看角色列表
- ✅ 编辑角色信息
- ✅ 删除角色（检查是否有用户使用）
- ✅ 配置角色权限：
  - 隐私级别访问（1-4级）
  - 上传权限
  - 删除权限
  - 修改隐私级别权限
  - 管理用户权限

### 统计信息
- ✅ 总用户数统计
- ✅ 活跃/禁用用户统计
- ✅ 角色分布统计
- ✅ 最近登录记录

## 访问方式

### 前端页面
访问地址：`http://localhost:5000/abtest/` 或 `http://localhost:5000/abtest/management`

### API 接口

#### 用户 API

1. **获取用户列表**
   ```
   GET /abtest/users?page=1&page_size=10&search=关键词&role_id=1&is_active=true
   ```

2. **获取单个用户**
   ```
   GET /abtest/users/{user_id}
   ```

3. **创建用户**
   ```
   POST /abtest/users
   Content-Type: application/json

   {
     "username": "testuser",
     "email": "test@example.com",
     "role_id": 1,
     "company_id": 1,
     "is_active": true
   }
   ```

4. **更新用户**
   ```
   PUT /abtest/users/{user_id}
   Content-Type: application/json

   {
     "username": "newname",
     "email": "new@example.com",
     "is_active": false
   }
   ```

5. **删除用户**
   ```
   DELETE /abtest/users/{user_id}
   ```

#### 角色 API

1. **获取角色列表**
   ```
   GET /abtest/roles
   ```

2. **获取单个角色**
   ```
   GET /abtest/roles/{role_id}
   ```

3. **创建角色**
   ```
   POST /abtest/roles
   Content-Type: application/json

   {
     "role_name": "编辑",
     "role_description": "内容编辑人员",
     "privacy_level_access": 2,
     "can_upload": true,
     "can_delete": false,
     "can_modify_privacy": false,
     "can_manage_users": false
   }
   ```

4. **更新角色**
   ```
   PUT /abtest/roles/{role_id}
   Content-Type: application/json

   {
     "role_name": "高级编辑",
     "privacy_level_access": 3,
     "can_delete": true
   }
   ```

5. **删除角色**
   ```
   DELETE /abtest/roles/{role_id}
   ```

#### 统计 API

```
GET /abtest/stats
```

## API 响应格式

所有 API 都返回统一的 JSON 格式：

**成功响应：**
```json
{
  "code": 0,
  "message": "操作成功",
  "data": { ... }
}
```

**错误响应：**
```json
{
  "code": -1,
  "message": "错误信息"
}
```

## 数据库表结构

该模块使用了以下数据库表（已在 `knowledge_base_schema.sql` 中定义）：

- `users` - 用户表
- `user_roles` - 角色表
- `companies` - 公司表（关联）

## 快速开始

1. 启动应用：
   ```bash
   python -m ai_tender_system.web.app
   ```

2. 访问用户管理页面：
   ```
   http://localhost:5000/abtest/
   ```

3. 或者直接使用 API：
   ```bash
   # 获取用户列表
   curl http://localhost:5000/abtest/users

   # 创建新用户
   curl -X POST http://localhost:5000/abtest/users \
     -H "Content-Type: application/json" \
     -d '{"username":"test","role_id":1}'
   ```

## 目录结构

```
abtest/
├── __init__.py                      # 模块初始化
├── README.md                        # 本文档
├── blueprints/                      # Flask蓝图
│   ├── __init__.py
│   └── user_management_bp.py        # 用户管理API
└── templates/                       # HTML模板
    └── user_management.html         # 用户管理前端页面
```

## 权限说明

### 隐私级别
- **级别 1**: 公开 - 所有人可见
- **级别 2**: 内部 - 内部员工可见
- **级别 3**: 机密 - 仅授权人员可见
- **级别 4**: 绝密 - 最高权限人员可见

### 角色权限
- `can_upload`: 允许上传文档
- `can_delete`: 允许删除文档
- `can_modify_privacy`: 允许修改文档隐私级别
- `can_manage_users`: 允许管理用户和角色

## 注意事项

1. 删除角色前会检查是否有用户正在使用该角色
2. 用户名必须唯一
3. 角色名必须唯一
4. 创建用户时必须指定角色ID
5. 数据库文件路径：`ai_tender_system/data/knowledge_base.db`

## 扩展开发

如需添加新功能，可以在以下位置扩展：

1. **添加新 API**: 在 `blueprints/user_management_bp.py` 中添加新路由
2. **修改前端**: 编辑 `templates/user_management.html`
3. **添加数据库表**: 在 `knowledge_base_schema.sql` 中添加新表定义

## 问题排查

如果遇到问题：

1. 检查数据库文件是否存在
2. 检查日志输出中的错误信息
3. 确认蓝图是否成功注册（启动日志中会显示）
4. 验证数据库表结构是否正确创建

## 测试

可以使用以下方式测试功能：

```bash
# 测试获取用户列表
curl http://localhost:5000/abtest/users

# 测试获取角色列表
curl http://localhost:5000/abtest/roles

# 测试获取统计信息
curl http://localhost:5000/abtest/stats
```
