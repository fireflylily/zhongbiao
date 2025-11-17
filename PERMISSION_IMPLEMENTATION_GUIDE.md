# 🔐 权限控制实现指南

## 📚 概述

本指南展示如何在API中实现完整的权限控制,包括:
1. 用户认证
2. 角色权限检查
3. 数据隔离(只看自己创建的)
4. 隐私级别控制

---

## 1️⃣ 已创建的权限中间件

### 文件: `ai_tender_system/web/middleware/permission.py`

#### 核心函数

1. **`get_current_user()`** - 获取当前登录用户
   ```python
   user = get_current_user()
   # 返回: {
   #   'user_id': 1,
   #   'username': 'admin',
   #   'role_name': '高级管理',
   #   'role_id': 4,
   #   'privacy_level_access': 4,
   #   'can_upload': True,
   #   'can_delete': True,
   #   ...
   # }
   ```

2. **权限检查装饰器**
   - `@require_auth` - 要求已登录
   - `@require_permission('upload')` - 要求上传权限
   - `@require_permission('delete')` - 要求删除权限
   - `@require_role(['高级管理'])` - 要求特定角色
   - `@require_privacy_level(3)` - 要求最小隐私级别

3. **辅助函数**
   - `can_access_resource(user, privacy_level)` - 检查能否访问资源
   - `is_owner_or_admin(user, creator_id)` - 检查是否拥有者或管理员
   - `filter_by_permission(user)` - 生成SQL过滤条件

---

## 2️⃣ 如何在API中检查权限

### 场景1: 要求用户已登录

```python
from web.middleware.permission import require_auth, get_current_user

@api_companies_bp.route('/companies')
@require_auth  # ✅ 检查是否登录
def list_companies():
    user = get_current_user()  # 获取当前用户

    # 现在可以根据用户信息进行操作
    companies = get_companies_for_user(user)
    return jsonify({'success': True, 'data': companies})
```

### 场景2: 要求特定权限

```python
from web.middleware.permission import require_upload_permission

@api_companies_bp.route('/companies', methods=['POST'])
@require_upload_permission  # ✅ 检查上传权限
def create_company():
    # 只有有上传权限的用户才能创建公司
    data = request.get_json()
    # ... 创建逻辑
```

### 场景3: 要求特定角色

```python
from web.middleware.permission import require_admin

@api_companies_bp.route('/companies/<company_id>', methods=['DELETE'])
@require_admin  # ✅ 只有高级管理员能删除
def delete_company(company_id):
    # 删除逻辑
    pass
```

### 场景4: 数据隔离 - 只看自己创建的

```python
from web.middleware.permission import require_auth, get_current_user, filter_by_permission

@api_companies_bp.route('/companies')
@require_auth
def list_companies():
    user = get_current_user()

    # ✅ 生成权限过滤条件
    filter_info = filter_by_permission(user, include_created_by=True)

    # filter_info包含:
    # - where_clause: SQL WHERE子句
    # - params: SQL参数
    # - is_admin: 是否管理员

    if filter_info['is_admin']:
        # 管理员看到所有公司
        companies = db.execute_query("SELECT * FROM companies")
    else:
        # 普通用户只看自己创建的
        sql = f"SELECT * FROM companies WHERE {filter_info['where_clause']}"
        companies = db.execute_query(sql, filter_info['params'])

    return jsonify({'success': True, 'data': companies})
```

### 场景5: 检查隐私级别

```python
from web.middleware.permission import require_auth, get_current_user, can_access_resource

@api_companies_bp.route('/companies/<company_id>')
@require_auth
def get_company(company_id):
    user = get_current_user()

    # 获取公司信息
    company = db.get_company(company_id)

    # ✅ 检查用户能否访问该隐私级别的数据
    if not can_access_resource(user, company['security_level']):
        return jsonify({
            'success': False,
            'message': '您的权限不足,无法访问该公司信息'
        }), 403

    return jsonify({'success': True, 'data': company})
```

### 场景6: 检查是否拥有者或管理员

```python
from web.middleware.permission import require_auth, get_current_user, is_owner_or_admin

@api_companies_bp.route('/companies/<company_id>', methods=['PUT'])
@require_auth
def update_company(company_id):
    user = get_current_user()

    # 获取公司信息
    company = db.get_company(company_id)

    # ✅ 检查是否是创建者或管理员
    if not is_owner_or_admin(user, company['created_by_user_id']):
        return jsonify({
            'success': False,
            'message': '只有创建者或管理员才能修改公司信息'
        }), 403

    # 执行更新
    # ...
    return jsonify({'success': True, 'message': '更新成功'})
```

---

## 3️⃣ 完整示例: 改造公司API

### 改造前 (无权限控制)

```python
@api_companies_bp.route('/companies')
def list_companies():
    """获取所有公司"""
    companies = kb_manager.get_companies()  # ❌ 所有人都看到所有公司
    return jsonify({'success': True, 'data': companies})
```

### 改造后 (有权限控制)

```python
from web.middleware.permission import require_auth, get_current_user, filter_by_permission

@api_companies_bp.route('/companies')
@require_auth  # ✅ 第1步: 要求登录
def list_companies():
    user = get_current_user()  # ✅ 第2步: 获取用户信息

    # ✅ 第3步: 根据角色过滤数据
    filter_info = filter_by_permission(user, include_created_by=True)

    if filter_info['is_admin']:
        # 管理员/项目经理: 看所有公司
        logger.info(f"{user['role_name']} {user['username']} 查看所有公司")
        companies = kb_manager.get_companies()
    else:
        # 普通用户/内部员工: 只看自己创建的
        logger.info(f"{user['role_name']} {user['username']} 查看自己创建的公司")
        companies = kb_manager.get_companies(created_by_user_id=user['user_id'])

    return jsonify({'success': True, 'data': companies})
```

---

## 4️⃣ 多层权限控制示例

### 示例: 删除公司API

```python
from web.middleware.permission import (
    require_auth,           # 1. 要求登录
    require_delete_permission,  # 2. 要求删除权限
    get_current_user,
    is_owner_or_admin
)

@api_companies_bp.route('/companies/<company_id>', methods=['DELETE'])
@require_auth              # ✅ 层级1: 必须登录
@require_delete_permission # ✅ 层级2: 必须有删除权限
def delete_company(company_id):
    user = get_current_user()

    # 获取公司信息
    company = kb_manager.get_company_detail(int(company_id))
    if not company:
        return jsonify({'success': False, 'error': '公司不存在'}), 404

    # ✅ 层级3: 检查是否创建者或管理员
    if not is_owner_or_admin(user, company.get('created_by_user_id')):
        return jsonify({
            'success': False,
            'message': '只有创建者或管理员才能删除公司'
        }), 403

    # ✅ 层级4: 检查隐私级别
    # 如果公司是机密级别,需要相应权限
    if company.get('security_level', 1) > user['privacy_level_access']:
        return jsonify({
            'success': False,
            'message': '您的权限不足,无法删除该级别的公司'
        }), 403

    # 执行删除
    result = kb_manager.delete_company(int(company_id))
    return jsonify(result)
```

---

## 5️⃣ 登录系统改进

### 改进内容 (`auth_bp.py`)

#### 改进前
```python
# ❌ 硬编码验证
if username == 'admin' and password == 'admin123':
    session['logged_in'] = True
    session['username'] = username  # 只存用户名
```

#### 改进后
```python
# ✅ 查询数据库
cursor.execute("""
    SELECT u.*, r.*
    FROM users u
    LEFT JOIN user_roles r ON u.role_id = r.role_id
    WHERE u.username = ? AND u.is_active = 1
""", (username,))

user = cursor.fetchone()

# ✅ 存储完整信息
session['logged_in'] = True
session['user_id'] = user['user_id']          # ✅ 用户ID
session['username'] = user['username']
session['role_id'] = user['role_id']          # ✅ 角色ID
session['role_name'] = user['role_name']      # ✅ 角色名
session['privacy_level_access'] = user['privacy_level_access']  # ✅ 隐私级别
session['company_id'] = user['company_id']    # ✅ 关联公司
```

### 支持的账号

现在可以用数据库中的任何用户登录:
- `admin` / `admin123` - 高级管理
- `chenyy` / `chenyy123` - 内部员工
- `zhangsan` / `zhangsan123` - 内部员工
- `lvhe` / `lvhe123` - 内部员工
- `huangjf` / `huangjf123` - 内部员工

---

## 6️⃣ 数据库改造

### 需要添加创建者字段

**Companies表当前没有创建者字段**,需要添加:

```sql
-- 添加创建者字段
ALTER TABLE companies ADD COLUMN created_by_user_id INTEGER REFERENCES users(user_id);

-- 为现有数据设置默认值(可选)
UPDATE companies SET created_by_user_id = 4 WHERE created_by_user_id IS NULL;  -- 4是admin的user_id
```

其他表已有字段:
- ✅ `case_studies` 有 `created_by_user_id`
- ✅ `resumes` 有 `created_by_user_id`
- ✅ `tender_projects` 有 `created_by_user_id`

---

## 7️⃣ API改造清单

需要添加权限控制的API:

### 公司管理 (`api_companies_bp.py`)
- [ ] `GET /companies` - 添加数据过滤
- [ ] `POST /companies` - 添加上传权限检查
- [ ] `PUT /companies/<id>` - 添加拥有者检查
- [ ] `DELETE /companies/<id>` - 添加删除权限检查

### 案例管理
- [ ] `GET /cases` - 添加数据过滤
- [ ] `POST /cases` - 添加上传权限检查
- [ ] `PUT /cases/<id>` - 添加拥有者检查
- [ ] `DELETE /cases/<id>` - 添加删除权限检查

### 简历管理
- [ ] `GET /resumes` - 添加数据过滤
- [ ] `POST /resumes` - 添加上传权限检查
- [ ] `PUT /resumes/<id>` - 添加拥有者检查
- [ ] `DELETE /resumes/<id>` - 添加删除权限检查

### 项目管理
- [ ] `GET /projects` - 添加数据过滤
- [ ] `POST /projects` - 添加上传权限检查
- [ ] `PUT /projects/<id>` - 添加拥有者检查
- [ ] `DELETE /projects/<id>` - 添加删除权限检查

---

## 8️⃣ 实现步骤

### 第一步: 数据库迁移
1. 为companies表添加 `created_by_user_id`
2. 更新现有数据的创建者
3. 修改创建API,记录创建者

### 第二步: 修改登录系统 ✅
- ✅ 已完成: 登录时查询数据库
- ✅ 已完成: Session存储完整用户信息
- ✅ 已完成: 更新最后登录时间

### 第三步: 应用权限装饰器
在每个API函数上添加适当的装饰器

### 第四步: 添加数据过滤
在查询函数中根据用户角色过滤数据

### 第五步: 测试
测试不同角色用户的访问权限

---

## 9️⃣ 具体代码示例

### 示例1: 公司列表API (完整实现)

```python
from flask import Blueprint, request, jsonify
from web.middleware.permission import require_auth, get_current_user, filter_by_permission

@api_companies_bp.route('/companies')
@require_auth  # ✅ 第1步: 要求登录
def list_companies():
    """
    获取公司列表
    - 普通用户/内部员工: 只看自己创建的
    - 项目经理/高级管理: 看所有
    """
    user = get_current_user()  # ✅ 第2步: 获取用户

    # ✅ 第3步: 根据角色决定过滤策略
    filter_info = filter_by_permission(user, include_created_by=True)

    conn = get_db_connection()
    cursor = conn.cursor()

    # ✅ 第4步: 应用过滤条件
    sql = f"""
        SELECT * FROM companies
        WHERE {filter_info['where_clause']}
        ORDER BY updated_at DESC
    """

    cursor.execute(sql, filter_info['params'])
    companies = [dict(row) for row in cursor.fetchall()]
    conn.close()

    logger.info(f"用户 {user['username']}({user['role_name']}) 查看公司列表, 返回 {len(companies)} 条")

    return jsonify({
        'success': True,
        'data': companies,
        'user_role': user['role_name']  # 方便前端显示
    })
```

### 示例2: 创建公司API (记录创建者)

```python
from web.middleware.permission import require_auth, require_upload_permission, get_current_user

@api_companies_bp.route('/companies', methods=['POST'])
@require_auth              # ✅ 要求登录
@require_upload_permission # ✅ 要求上传权限
def create_company():
    """
    创建公司
    - 要求上传权限
    - 自动记录创建者
    """
    user = get_current_user()
    data = request.get_json()

    company_name = data.get('company_name')
    if not company_name:
        return jsonify({'success': False, 'error': '公司名称不能为空'}), 400

    # ✅ 记录创建者
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO companies (
            company_name,
            created_by_user_id,  -- ✅ 记录创建者
            created_at
        ) VALUES (?, ?, ?)
    """, (company_name, user['user_id'], datetime.now()))

    company_id = cursor.lastrowid
    conn.commit()
    conn.close()

    logger.info(f"用户 {user['username']} 创建公司: {company_name} (ID:{company_id})")

    return jsonify({
        'success': True,
        'company_id': company_id,
        'message': '公司创建成功'
    })
```

### 示例3: 更新公司API (检查拥有者)

```python
from web.middleware.permission import require_auth, get_current_user, is_owner_or_admin

@api_companies_bp.route('/companies/<int:company_id>', methods=['PUT'])
@require_auth
def update_company(company_id):
    """
    更新公司
    - 只有创建者或管理员可以修改
    """
    user = get_current_user()
    data = request.get_json()

    # 获取公司信息
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT company_id, company_name, created_by_user_id, security_level
        FROM companies
        WHERE company_id = ?
    """, (company_id,))

    company = cursor.fetchone()

    if not company:
        conn.close()
        return jsonify({'success': False, 'error': '公司不存在'}), 404

    company = dict(company)

    # ✅ 检查1: 是否拥有者或管理员
    if not is_owner_or_admin(user, company['created_by_user_id']):
        conn.close()
        return jsonify({
            'success': False,
            'message': '只有创建者或管理员才能修改公司信息'
        }), 403

    # ✅ 检查2: 隐私级别权限
    if company['security_level'] > user['privacy_level_access']:
        conn.close()
        return jsonify({
            'success': False,
            'message': f"您的权限不足,无法修改该级别的公司"
        }), 403

    # 执行更新
    cursor.execute("""
        UPDATE companies
        SET company_name = ?, updated_at = ?
        WHERE company_id = ?
    """, (data.get('company_name'), datetime.now(), company_id))

    conn.commit()
    conn.close()

    logger.info(f"用户 {user['username']} 更新公司 {company_id}")

    return jsonify({'success': True, 'message': '更新成功'})
```

### 示例4: 删除公司API (多重权限检查)

```python
from web.middleware.permission import (
    require_auth,
    require_delete_permission,  # 要求删除权限
    get_current_user,
    is_owner_or_admin
)

@api_companies_bp.route('/companies/<int:company_id>', methods=['DELETE'])
@require_auth               # ✅ 必须登录
@require_delete_permission  # ✅ 必须有删除权限
def delete_company(company_id):
    """
    删除公司
    - 要求删除权限(内部员工不能删除)
    - 只有创建者或管理员可以删除
    """
    user = get_current_user()

    # 获取公司信息
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT company_id, company_name, created_by_user_id
        FROM companies
        WHERE company_id = ?
    """, (company_id,))

    company = cursor.fetchone()

    if not company:
        conn.close()
        return jsonify({'success': False, 'error': '公司不存在'}), 404

    company = dict(company)

    # ✅ 检查是否拥有者或管理员
    if not is_owner_or_admin(user, company['created_by_user_id']):
        conn.close()
        return jsonify({
            'success': False,
            'message': '只有创建者或管理员才能删除公司'
        }), 403

    # 执行删除
    cursor.execute("DELETE FROM companies WHERE company_id = ?", (company_id,))
    conn.commit()
    conn.close()

    logger.info(f"用户 {user['username']} 删除公司 {company['company_name']} (ID:{company_id})")

    return jsonify({'success': True, 'message': '删除成功'})
```

---

## 🔟 装饰器参考表

| 装饰器 | 作用 | 使用场景 |
|--------|------|---------|
| `@require_auth` | 要求已登录 | 所有需要登录的API |
| `@require_upload_permission` | 要求上传权限 | 创建/上传操作 |
| `@require_delete_permission` | 要求删除权限 | 删除操作 |
| `@require_permission('modify_privacy')` | 要求修改隐私级别权限 | 修改隐私级别 |
| `@require_admin` | 要求高级管理员 | 敏感管理操作 |
| `@require_manager` | 要求项目经理或以上 | 管理功能 |
| `@require_role(['高级管理', '项目经理'])` | 要求特定角色 | 自定义角色限制 |
| `@require_privacy_level(3)` | 要求最小隐私级别 | 访问机密数据 |

---

## 1️⃣1️⃣ 权限逻辑总结

### 角色权限层级

```
高级管理 (role_id=4)
  ├─ 可访问: 所有数据 (隐私级别1-4)
  ├─ 可操作: 上传、删除、修改隐私、管理用户
  └─ 数据范围: 看所有人创建的数据

项目经理 (role_id=3)
  ├─ 可访问: 公开+内部+机密 (隐私级别1-3)
  ├─ 可操作: 上传、删除、修改隐私
  └─ 数据范围: 看所有人创建的数据

内部员工 (role_id=2)
  ├─ 可访问: 公开+内部 (隐私级别1-2)
  ├─ 可操作: 上传
  └─ 数据范围: ⚠️ 只看自己创建的数据

普通用户 (role_id=1)
  ├─ 可访问: 公开 (隐私级别1)
  ├─ 可操作: 无
  └─ 数据范围: ⚠️ 只看自己创建的数据
```

---

## 1️⃣2️⃣ 快速开始

### 1. 修复登录系统
✅ **已完成** - auth_bp.py 已更新

### 2. 在API中应用权限
```python
# 在文件顶部导入
from web.middleware.permission import require_auth, get_current_user

# 在API函数上添加装饰器
@require_auth
def your_api_function():
    user = get_current_user()
    # 使用user信息进行权限判断
```

### 3. 测试
```bash
# 以不同用户登录测试
curl -X POST http://localhost:8110/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"zhangsan","password":"zhangsan123"}'

# 测试权限控制是否生效
curl http://localhost:8110/api/companies
```

---

## 📝 总结

### ✅ 已完成
1. ✅ 创建权限中间件 (`permission.py`)
2. ✅ 修复登录系统查询数据库
3. ✅ Session存储完整用户信息
4. ✅ 提供完整的权限检查装饰器

### ⏳ 待完成
1. ⏳ 为companies表添加created_by_user_id字段
2. ⏳ 在各个API中应用权限装饰器
3. ⏳ 实现数据过滤逻辑
4. ⏳ 全面测试权限控制

### 💡 下一步
- 需要决定是否立即应用到所有API
- 需要为companies表添加创建者字段
- 需要处理现有数据的归属问题

---

**文档创建时间**: 2025-11-17
**状态**: 框架已完成,等待应用
