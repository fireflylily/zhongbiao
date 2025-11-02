# 如何在Railway中打开Shell

## 📺 图文步骤

### 方法1: 通过Deployment页面（推荐）⭐

#### 步骤1: 登录Railway Dashboard
1. 访问 https://railway.app/dashboard
2. 使用您的账号登录（GitHub/Email）

#### 步骤2: 选择项目
1. 在Dashboard中找到您的项目（AI标书系统）
2. 点击项目卡片进入项目详情页

#### 步骤3: 进入Service
1. 在项目页面，您会看到服务列表（Services）
2. 点击您的Web服务（通常名为 `web` 或项目名称）

#### 步骤4: 打开Deployments
1. 在Service页面顶部，找到并点击 **"Deployments"** 标签
2. 您会看到部署历史列表

#### 步骤5: 选择最新部署
1. 找到状态为 **"Success"**（成功）的最新部署
2. 点击该部署记录

#### 步骤6: 打开Shell
1. 在部署详情页面右上角，找到 **三个点（⋮）** 或 **"Actions"** 按钮
2. 在下拉菜单中选择 **"Shell"** 或 **"Open Shell"**
3. 一个新的Shell窗口会在浏览器中打开

#### 步骤7: 验证Shell
Shell打开后，您应该看到类似这样的提示符：
```bash
/app #
```

或
```bash
root@railway-deployment-id:~#
```

现在可以输入命令了！

---

### 方法2: 通过Service页面的快捷方式

#### 步骤1-3: 同方法1

#### 步骤4: 使用快捷入口
1. 在Service页面右上角，直接点击 **"Shell"** 图标/按钮
2. 这会自动打开最新成功部署的Shell

---

### 方法3: 使用Railway CLI（本地命令行）

如果您已经安装了Railway CLI：

```bash
# 1. 确保已链接项目
railway link

# 2. 直接打开Shell
railway shell

# 或指定环境
railway shell -e production
```

---

## 🎯 Shell打开后的操作

### 1️⃣ 验证环境

```bash
# 检查当前目录
pwd
# 应该输出: /app

# 查看文件结构
ls -la
# 应该看到: ai_tender_system/ 等目录

# 检查Python版本
python3 --version
# 应该输出: Python 3.11.x 或 3.13.x
```

### 2️⃣ 导入数据库

假设您的GitHub Gist Raw URL是: `https://gist.githubusercontent.com/username/xxx/raw/knowledge_base.sql`

**完整命令**（复制粘贴整段）：

```bash
# 下载SQL文件
curl -o /tmp/knowledge_base.sql https://gist.githubusercontent.com/YOUR_USERNAME/GIST_ID/raw/knowledge_base_export_20251026_195125.sql

# 导入到数据库
cd /app
python3 << 'EOF'
import sqlite3
from pathlib import Path
import shutil

# 数据库路径
db_path = Path('ai_tender_system/data/knowledge_base.db')

# 确保目录存在
db_path.parent.mkdir(parents=True, exist_ok=True)

# 备份现有数据库（如果存在）
if db_path.exists():
    backup_path = db_path.with_suffix('.db.backup')
    shutil.copy(db_path, backup_path)
    print(f"✓ 已备份现有数据库到: {backup_path}")

# 读取SQL文件
print("正在读取SQL文件...")
with open('/tmp/knowledge_base.sql', 'r', encoding='utf-8') as f:
    sql_content = f.read()

# 导入数据
print("正在导入数据库...")
conn = sqlite3.connect(str(db_path))
conn.executescript(sql_content)
conn.close()

# 验证导入结果
print("\n验证导入结果:")
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
table_count = cursor.fetchone()[0]
print(f"  ✓ 表数量: {table_count}")

cursor.execute("SELECT COUNT(*) FROM companies")
company_count = cursor.fetchone()[0]
print(f"  ✓ 公司数量: {company_count}")

cursor.execute("SELECT COUNT(*) FROM tender_projects")
project_count = cursor.fetchone()[0]
print(f"  ✓ 项目数量: {project_count}")

cursor.execute("SELECT COUNT(*) FROM company_qualifications")
qual_count = cursor.fetchone()[0]
print(f"  ✓ 资质数量: {qual_count}")

conn.close()

print("\n✓ 数据库导入完成!")
EOF

# 清理临时文件
rm /tmp/knowledge_base.sql

echo "✓ 全部完成！"
```

### 3️⃣ 验证应用能否访问数据库

```bash
# 测试数据库连接
python3 << 'EOF'
import sys
sys.path.insert(0, '/app')

from ai_tender_system.common.database import Database

# 初始化数据库连接
db = Database()

# 查询公司列表
companies = db.execute_query("SELECT id, name FROM companies")
print(f"公司列表: {companies}")

# 查询项目列表
projects = db.execute_query("SELECT id, name FROM tender_projects")
print(f"项目列表: {projects}")

print("✓ 应用可以正常访问数据库!")
EOF
```

---

## 🔍 常见界面元素

### Railway页面结构：

```
┌────────────────────────────────────────────────┐
│ Railway Dashboard                               │
├────────────────────────────────────────────────┤
│                                                 │
│  Projects > Your Project Name                   │
│                                                 │
│  ┌──────────────────────────────────────────┐  │
│  │ Services                                  │  │
│  │ ┌─────────────┐  ┌─────────────┐        │  │
│  │ │ web         │  │ postgres    │        │  │
│  │ │ (active)    │  │ (optional)  │        │  │
│  │ └─────────────┘  └─────────────┘        │  │
│  └──────────────────────────────────────────┘  │
│                                                 │
│  点击 web 服务 →                                │
│                                                 │
│  ┌──────────────────────────────────────────┐  │
│  │ Web Service                               │  │
│  │                                           │  │
│  │ [Settings] [Variables] [Metrics]         │  │
│  │ [Deployments] [Logs]                     │  │
│  │            ↑                              │  │
│  │         点击这里                          │  │
│  └──────────────────────────────────────────┘  │
│                                                 │
│  Deployments 页面 →                             │
│                                                 │
│  ┌──────────────────────────────────────────┐  │
│  │ Recent Deployments                        │  │
│  │                                           │  │
│  │ ✓ #123 - 2 hours ago - Success  [⋮]     │  │
│  │                              ↑            │  │
│  │                          点击这里         │  │
│  │   下拉菜单出现:                           │  │
│  │   - View Logs                             │  │
│  │   - Open Shell  ← 选择这个               │  │
│  │   - Redeploy                              │  │
│  └──────────────────────────────────────────┘  │
└────────────────────────────────────────────────┘
```

---

## 📱 移动端访问

Railway Dashboard也支持移动浏览器，但Shell功能在桌面浏览器上体验更好。

---

## ⚠️ 注意事项

### 1. Shell超时
- Railway Shell会话通常在 **30分钟无操作** 后超时
- 如果命令执行时间较长，建议使用 `nohup` 或后台运行

### 2. Shell权限
- Shell默认以 `root` 或容器用户身份运行
- 有完整的文件系统访问权限

### 3. Shell持久性
- Shell中的更改（如上传的数据库）会保留在容器中
- 但如果容器重启，非Volume挂载的文件可能丢失
- **建议**: 使用Railway Volumes存储数据库

### 4. 文件上传限制
- Shell不直接支持文件拖放上传
- 需要通过URL下载（curl/wget）或粘贴内容

---

## 🆘 故障排除

### 问题1: 找不到Shell按钮

**原因**: 部署可能未成功或已停止

**解决**:
1. 确认部署状态为 "Success"（绿色勾号）
2. 如果部署失败，查看Logs找出原因
3. 确保服务正在运行（Dashboard显示 "Active"）

### 问题2: Shell打开后无响应

**解决**:
1. 刷新页面重试
2. 尝试不同浏览器（推荐Chrome/Edge）
3. 检查浏览器控制台是否有错误

### 问题3: Shell中命令无法执行

**解决**:
1. 确认当前目录：`pwd`
2. 切换到应用目录：`cd /app`
3. 检查Python是否可用：`which python3`

### 问题4: 权限被拒绝

**解决**:
```bash
# 检查文件权限
ls -la ai_tender_system/data/

# 修改权限
chmod -R 755 ai_tender_system/data/
```

---

## 📸 截图示意（文字版）

由于无法显示实际截图，这里是关键按钮的位置描述：

```
Railway Deployment 详情页:
┌─────────────────────────────────────────────────┐
│ ← Back to Service                               │
├─────────────────────────────────────────────────┤
│ Deployment #123                    [⋮] ← 点这里 │
│                                                  │
│ Status: Success ✓                                │
│ Duration: 2m 34s                                 │
│ Deployed: 2 hours ago                            │
│                                                  │
│ [View Logs] [View Build Logs]                   │
└─────────────────────────────────────────────────┘

点击 [⋮] 后的下拉菜单:
┌──────────────────┐
│ View Logs        │
│ Open Shell    ← │
│ Redeploy         │
│ Restart          │
└──────────────────┘
```

---

## ✅ 快速检查清单

打开Shell前确认：
- [ ] 已登录Railway账号
- [ ] 项目已部署成功
- [ ] 部署状态为 "Success"
- [ ] 使用桌面浏览器（非移动端）

打开Shell后确认：
- [ ] 看到命令提示符（如 `/app #`）
- [ ] 可以输入命令
- [ ] `pwd` 显示 `/app`
- [ ] `ls` 能看到项目文件

---

## 🎓 相关资源

- Railway官方文档: https://docs.railway.app/
- Railway Shell文档: https://docs.railway.app/guides/shell
- Railway支持: https://railway.app/support

---

**提示**: 如果您仍然无法找到Shell按钮，可以截图发送Railway Dashboard的页面，我可以帮您定位具体位置。

**创建时间**: 2025-10-26
