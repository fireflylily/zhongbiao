# 部署指南：修复小程序对账进度卡在 0% 的问题

## 问题现象

用户在小程序中上传招标文件和应答文件后，对账进度始终显示：
```
正在进行双向对账... 0%
```

## 问题根因

1. **API 响应缺失字段**：`/api/mp/risk/status/<task_id>` 接口未返回对账相关字段
2. **数据库表不存在**：生产环境 `knowledge_base.db` 缺少 `risk_analysis_tasks` 表

## 修复内容

### 代码修改
- ✅ [web/blueprints/api_miniprogram_bp.py](../web/blueprints/api_miniprogram_bp.py#L380-L420) - 添加对账字段
- ✅ [scripts/init_production_db.py](../scripts/init_production_db.py) - 数据库初始化脚本

### Git 提交
- Commit: `dad8477d`
- 已推送到 `origin/master`

---

## 🚀 生产环境部署步骤

### 准备工作
```bash
# 1. SSH 登录生产服务器
ssh user@toubiao.succtech.com

# 2. 切换到项目目录
cd /path/to/ai_tender_system
```

### Step 1: 拉取最新代码
```bash
# 拉取修复代码
git pull origin master

# 验证提交
git log -1 --oneline
# 应显示: dad8477d fix: 修复小程序对账进度卡在0%的问题
```

### Step 2: 初始化数据库

**重要提示**：如果服务器 Python 版本 < 3.7，使用简化版脚本：

```bash
# 检查 Python 版本
python3 --version

# 如果 Python < 3.7，使用简化版脚本（推荐）
python3 scripts/init_db_simple.py

# 如果 Python >= 3.7，可使用标准脚本
python3 scripts/init_production_db.py
```

**预期输出：**
```
[INFO] 开始初始化生产环境数据库...
[INFO] ✅ risk_analysis_tasks 表已创建
[INFO] ✅ 表 risk_analysis_tasks 已存在
[INFO] ✅ 所有必需字段已存在: 10 个
[INFO] ✅ 已添加 task_mode 字段
[INFO] 🎉 数据库初始化完成！
```

### Step 3: 验证数据库表结构
```bash
# 连接数据库
sqlite3 data/knowledge_base.db

# 查看表结构
.schema risk_analysis_tasks

# 验证关键字段
PRAGMA table_info(risk_analysis_tasks);

# 应包含以下字段：
# - response_file_path
# - response_file_name
# - reconcile_results
# - reconcile_progress
# - reconcile_step
# - task_mode

# 退出
.quit
```

### Step 4: 重启后端服务

**如果使用 systemd：**
```bash
sudo systemctl restart ai_tender_system
sudo systemctl status ai_tender_system
```

**如果使用 supervisor：**
```bash
supervisorctl restart ai_tender_system
supervisorctl status ai_tender_system
```

**如果手动运行：**
```bash
# 查找进程
ps aux | grep "python.*run.py"

# 杀掉旧进程
kill <PID>

# 启动新进程
nohup python3 run.py > logs/app.log 2>&1 &
```

### Step 5: 验证服务运行
```bash
# 检查服务监听端口
netstat -tuln | grep 8110

# 测试健康检查接口
curl http://localhost:8110/api/mp/health

# 查看日志
tail -f logs/app.log
```

---

## 🧪 功能测试

### 测试场景 1：仅上传招标文件
1. 打开小程序
2. 上传招标文件（PDF/Word）
3. 等待分析完成
4. **预期**：显示风险项列表，无对账相关内容

### 测试场景 2：上传招标文件 + 应答文件
1. 上传招标文件
2. 等待分析完成后，点击「上传应答文件」
3. 上传应答文件
4. **预期**：
   - 显示「正在进行双向对账... X%」，进度从 0% 增长到 100%
   - 显示当前步骤：「正在提取对账内容...」→「正在进行合规检查...」
   - 完成后显示对账汇总：
     ```
     对账完成
     匹配度: 87分
     🟢 通过: 12项
     🔴 不通过: 2项
     🟡 部分符合: 3项
     ```

### 测试场景 3：历史任务查询
1. 点击「查看历史记录」
2. 选择一个包含对账的任务
3. **预期**：
   - 显示应答文件名
   - 显示对账汇总卡片
   - 可点击查看详细对账结果

---

## 🔍 故障排查

### 问题 1: 数据库初始化失败
**症状**：`init_production_db.py` 报错
```python
sqlite3.OperationalError: unable to open database file
```

**解决方案**：
```bash
# 检查数据目录权限
ls -la data/

# 创建数据目录（如不存在）
mkdir -p data

# 修改权限
chmod 755 data/
```

### 问题 2: 进度仍然卡在 0%
**检查清单**：
1. ✅ 确认代码已拉取（git log 看到 dad8477d）
2. ✅ 确认数据库表已创建（sqlite3 查询）
3. ✅ 确认服务已重启（ps aux 看到新进程）
4. ✅ 小程序缓存已清除（微信开发者工具 → 清除缓存）

**查看日志**：
```bash
# 后端日志
tail -100 logs/app.log | grep -E "reconcile|status"

# 查找报错
grep "ERROR" logs/app.log | tail -20
```

### 问题 3: API 返回 500 错误
**症状**：小程序显示「系统错误」

**检查步骤**：
```bash
# 查看详细错误
tail -50 logs/app.log

# 检查数据库连接
python3 -c "
from modules.risk_analyzer import RiskTaskManager
tm = RiskTaskManager()
print('✅ 数据库连接正常')
"

# 检查 API 路由
curl -X GET http://localhost:8110/api/mp/risk/status/test_task_id \
  -H "Authorization: Bearer <token>"
```

---

## 📋 回滚方案

如果部署后出现严重问题，可以回滚：

```bash
# 1. 回退代码到上一版本
git reset --hard 54562dfa
git push origin master --force

# 2. 重启服务
supervisorctl restart ai_tender_system

# 3. 通知用户暂时不要使用对账功能
```

---

## 📊 监控指标

部署后持续监控以下指标：

- **任务创建成功率**：`SELECT COUNT(*) FROM risk_analysis_tasks WHERE created_at > datetime('now', '-1 hour')`
- **对账任务完成率**：`SELECT COUNT(*) FROM risk_analysis_tasks WHERE reconcile_progress = 100`
- **API 响应时间**：查看日志中 `/api/mp/risk/status` 的耗时
- **错误率**：`grep "ERROR" logs/app.log | wc -l`

---

## 📞 联系方式

如有问题，请联系：
- 开发者：lvhe@succtech.com
- GitHub Issue: https://github.com/fireflylily/zhongbiao/issues

---

## ✅ 部署检查清单

完成以下步骤后打勾：

- [ ] SSH 登录生产服务器
- [ ] `git pull origin master` 拉取代码
- [ ] 验证提交 `dad8477d` 已拉取
- [ ] 运行 `python3 scripts/init_production_db.py`
- [ ] 验证数据库表结构包含所有字段
- [ ] 重启后端服务
- [ ] 验证服务监听端口 8110
- [ ] 测试场景 1：仅招标文件
- [ ] 测试场景 2：招标 + 应答对账
- [ ] 测试场景 3：历史任务查询
- [ ] 监控日志无异常
- [ ] 通知团队部署完成

---

**部署完成时间**: __________
**部署人员**: __________
**验证人员**: __________
