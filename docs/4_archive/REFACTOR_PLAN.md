# 移除 task_id 重构计划

## 重构目标
将系统从使用 `task_id` 和 `hitl_task_id` 作为标识符改为直接使用 `project_id`，简化数据库结构和API设计。

## 重构原则
- **一个项目一个任务**：每个 `project_id` 对应一个处理任务和一个 HITL 任务
- **project_id 作为主键**：`tender_processing_tasks` 和 `tender_hitl_tasks` 表使用 `project_id` 作为主键
- **简化API路由**：所有 `/api/xxx/<task_id>` 改为 `/api/xxx/<int:project_id>`
- **向后兼容性**：暂时保留旧数据，通过迁移脚本转换

---

## 第一阶段：数据库层修改

### 1.1 database.py 方法修改清单

#### 需要修改的方法（7个）：

**1. `create_processing_task`** (第1287行)
```python
# 修改前
def create_processing_task(self, project_id: int, task_id: str,
                          pipeline_config: Dict = None, options: Dict = None) -> bool:
    query = """
    INSERT INTO tender_processing_tasks
    (task_id, project_id, pipeline_config, options)
    VALUES (?, ?, ?, ?)
    """
    return self.execute_query(query, (task_id, project_id, config_json, options_json))

# 修改后
def create_processing_task(self, project_id: int,
                          pipeline_config: Dict = None, options: Dict = None) -> bool:
    query = """
    INSERT INTO tender_processing_tasks
    (project_id, pipeline_config, options)
    VALUES (?, ?, ?)
    """
    return self.execute_query(query, (project_id, config_json, options_json))
```

**2. `get_processing_task`** (第1301行)
```python
# 修改前
def get_processing_task(self, task_id: str) -> Optional[Dict]:
    query = "SELECT * FROM tender_processing_tasks WHERE task_id = ?"
    return self.execute_query(query, (task_id,), fetch_one=True)

# 修改后
def get_processing_task(self, project_id: int) -> Optional[Dict]:
    query = "SELECT * FROM tender_processing_tasks WHERE project_id = ?"
    return self.execute_query(query, (project_id,), fetch_one=True)
```

**3. `update_processing_task`** (第1306行)
```python
# 修改前
def update_processing_task(self, task_id: str, overall_status: str = None, ...):
    # ...
    params.append(task_id)
    query = f"UPDATE tender_processing_tasks SET {', '.join(updates)} WHERE task_id = ?"

# 修改后
def update_processing_task(self, project_id: int, overall_status: str = None, ...):
    # ...
    params.append(project_id)
    query = f"UPDATE tender_processing_tasks SET {', '.join(updates)} WHERE project_id = ?"
```

**4. `create_processing_log`** (第1351行)
```python
# 修改前
def create_processing_log(self, project_id: int, task_id: str, step: str) -> int:
    query = """
    INSERT INTO tender_processing_logs
    (project_id, task_id, step, status, started_at)
    VALUES (?, ?, ?, 'pending', CURRENT_TIMESTAMP)
    """
    return self.execute_query(query, (project_id, task_id, step))

# 修改后
def create_processing_log(self, project_id: int, step: str) -> int:
    query = """
    INSERT INTO tender_processing_logs
    (project_id, step, status, started_at)
    VALUES (?, ?, 'pending', CURRENT_TIMESTAMP)
    """
    return self.execute_query(query, (project_id, step))
```

**5. `get_processing_logs`** (第1411行)
```python
# 修改前
def get_processing_logs(self, task_id: str = None, project_id: int = None) -> List[Dict]:
    conditions = []
    params = []

    if task_id:
        conditions.append("task_id = ?")
        params.append(task_id)

    if project_id:
        conditions.append("project_id = ?")
        params.append(project_id)
    # ...

# 修改后
def get_processing_logs(self, project_id: int) -> List[Dict]:
    query = """
    SELECT * FROM tender_processing_logs
    WHERE project_id = ?
    ORDER BY created_at DESC
    """
    return self.execute_query(query, (project_id,))
```

**6. `get_processing_statistics`** (第1433行)
```python
# 修改前
def get_processing_statistics(self, task_id: str) -> Optional[Dict]:
    query = "SELECT * FROM v_processing_statistics WHERE task_id = ?"
    return self.execute_query(query, (task_id,), fetch_one=True)

# 修改后
def get_processing_statistics(self, project_id: int) -> Optional[Dict]:
    query = "SELECT * FROM v_processing_statistics WHERE project_id = ?"
    return self.execute_query(query, (project_id,), fetch_one=True)
```

**7. `create_tender_requirement` & `batch_create_tender_requirements`**
```python
# 移除 hitl_task_id 参数
# 第1181-1197行 和 第1239-1262行
```

---

## 第二阶段：业务逻辑层修改

### 2.1 processing_pipeline.py 修改

**修改要点：**
1. 移除 `self.task_id` 的生成（第79行）
2. 所有 `db.update_processing_task(task_id=self.task_id, ...)` 改为 `(project_id=self.project_id, ...)`
3. 所有 `db.create_processing_task(task_id=self.task_id, ...)` 改为不传 task_id
4. 返回结果中的 `task_id` 改为 `project_id`

**具体位置：**
- 第140行: `update_processing_task` 调用
- 第247行: `update_processing_task` 调用
- 第298行: `update_processing_task` 调用
- 第363行: `update_processing_task` 调用
- 第402-404行: `create_processing_task` 调用
- 第435行: `update_processing_task` 调用
- 第443行: 返回结果中的 `task_id`
- 第502-504行: `create_processing_task` 调用
- 第533行: 返回结果中的 `task_id`

---

## 第三阶段：API层修改

### 3.1 api_tender_processing_bp.py 修改

**需要修改的路由（6个）：**

1. `/start` - 返回值改为 `project_id`
2. `/continue/<task_id>` → `/continue/<int:project_id>`
3. `/status/<task_id>` → `/status/<int:project_id>`
4. `/sync-point-to-point/<task_id>` → `/sync-point-to-point/<int:project_id>`
5. `/sync-tech-proposal/<task_id>` → `/sync-tech-proposal/<int:project_id>`

**修改示例：**
```python
# 修改前
@api_tender_processing_bp.route('/continue/<task_id>', methods=['POST'])
def continue_tender_processing(task_id):
    pipeline = get_pipeline_instance(task_id)
    # ...

# 修改后
@api_tender_processing_bp.route('/continue/<int:project_id>', methods=['POST'])
def continue_tender_processing(project_id):
    pipeline = get_pipeline_instance(project_id)
    # ...
```

### 3.2 api_tender_processing_hitl.py 修改

**大量路由需要修改（约20个）：**

主要模式：`/<task_id>` → `/<int:project_id>`

关键路由列表：
1. `/start-hitl` - 修改返回值和数据库操作
2. `/select-chapters` - 参数从 `task_id` 改为 `project_id`
3. `/export-chapter/<task_id>/<chapter_id>` → `/export-chapter/<int:project_id>/<chapter_id>`
4. `/export-chapters/<task_id>` → `/export-chapters/<int:project_id>`
5. `/save-response-file/<task_id>` → `/save-response-file/<int:project_id>`
6. `/download-response-file/<task_id>` → `/download-response-file/<int:project_id>`
7. `/preview-response-file/<task_id>` → `/preview-response-file/<int:project_id>`
8. `/response-file-info/<task_id>` → `/response-file-info/<int:project_id>`
9. `/save-technical-chapters/<task_id>` → `/save-technical-chapters/<int:project_id>`
10. `/technical-file-info/<task_id>` → `/technical-file-info/<int:project_id>`
11. `/download-technical-file/<task_id>` → `/download-technical-file/<int:project_id>`
12. `/preview-technical-file/<task_id>` → `/preview-technical-file/<int:project_id>`
13. `/chapters/<task_id>` → `/chapters/<int:project_id>`
14. `/chapter-content/<task_id>/<chapter_id>` → `/chapter-content/<int:project_id>/<chapter_id>`
15. `/chapter-requirements/<task_id>` → `/chapter-requirements/<int:project_id>`
16. `/filtered-blocks/<task_id>` → `/filtered-blocks/<int:project_id>`

**关键修改：**
- HITL 任务创建时不再生成 `hitl_task_id`，直接使用 `project_id`
- 所有数据库查询从 `WHERE hitl_task_id = ?` 改为 `WHERE project_id = ?`
- 所有数据库插入移除 `hitl_task_id` 字段

### 3.3 api_projects_bp.py 修改

已经部分修改，需要检查：
- 第294行：查询章节的 `WHERE project_id = ? AND task_id = ?` 应该改为只用 `project_id`
- 移除对 `task_id` 的引用

---

## 第四阶段：前端修改

### 4.1 TypeScript 类型定义修改

**文件：frontend/src/types/api.ts 和 types/models.ts**

```typescript
// 修改前
export interface TenderHITLTask {
  task_id: string
  project_id: number
  // ...
}

// 修改后
export interface TenderHITLTask {
  project_id: number  // 移除 task_id
  // ...
}
```

### 4.2 API端点修改

**文件：frontend/src/api/endpoints/tender.ts**

```typescript
// 修改前
export const tenderApi = {
  getChapters: (taskId: string) => api.get(`/api/tender-processing/chapters/${taskId}`),
  // ...
}

// 修改后
export const tenderApi = {
  getChapters: (projectId: number) => api.get(`/api/tender-processing/chapters/${projectId}`),
  // ...
}
```

### 4.3 Vue组件修改

**需要修改的组件：**
1. `frontend/src/views/Tender/ManagementDetail.vue`
2. `frontend/src/components/TenderDocumentProcessor.vue`
3. `frontend/src/views/Business/Response.vue`

**修改模式：**
```typescript
// 修改前
const taskId = ref<string>('')
const loadData = async () => {
  const res = await api.getChapters(taskId.value)
}

// 修改后
const projectId = ref<number>(0)
const loadData = async () => {
  const res = await api.getChapters(projectId.value)
}
```

---

## 第五阶段：数据迁移

### 5.1 运行迁移脚本

**文件：ai_tender_system/database/migrate_to_new_structure.sql**

该脚本已准备好，执行步骤：
1. 备份旧数据：`migrate_backup_old_structure.sql`
2. 迁移到新结构：`migrate_to_new_structure.sql`

**注意事项：**
- 迁移策略：每个 `project_id` 只保留最新的一条记录
- 关联数据通过 `hitl_task_id` 匹配后迁移
- 保留备份表以便回滚

---

## 第六阶段：测试计划

### 6.1 后端测试
1. 测试项目创建流程
2. 测试文档上传和处理
3. 测试 HITL 流程（章节选择、应答文件生成等）
4. 测试商务应答生成
5. 测试技术方案生成

### 6.2 前端测试
1. 项目管理页面加载
2. 文档上传功能
3. 章节选择功能
4. 文件预览和下载
5. 商务应答生成界面

### 6.3 集成测试
1. 完整流程：创建项目 → 上传文档 → 处理 → HITL → 生成应答
2. 多项目并发处理
3. 错误恢复机制

---

## 执行顺序

建议按以下顺序执行：

### 第1步：数据库层（database.py）
- ✅ 低风险，基础修改
- 修改7个方法
- 预计耗时：15分钟

### 第2步：业务逻辑层（processing_pipeline.py）
- ✅ 中等风险，依赖数据库层
- 修改task_id相关逻辑
- 预计耗时：10分钟

### 第3步：API层（后端路由）
- ⚠️ 高风险，影响前后端接口
- 修改 api_tender_processing_bp.py（6个路由）
- 修改 api_tender_processing_hitl.py（20个路由）
- 修改 api_projects_bp.py（检查完整性）
- 预计耗时：30分钟

### 第4步：前端层
- ⚠️ 高风险，需要重新构建
- 修改 TypeScript 类型（5分钟）
- 修改 API 调用（10分钟）
- 修改 Vue 组件（20分钟）
- 运行构建（5分钟）
- 预计耗时：40分钟

### 第5步：测试
- 🔴 关键步骤
- 后端API测试（15分钟）
- 前端功能测试（15分钟）
- 预计耗时：30分钟

### 第6步：数据迁移（生产环境）
- 🔴 最后一步
- 运行迁移脚本
- 验证数据完整性

---

## 风险评估

### 高风险点
1. **API路由变更**：前后端不匹配会导致404错误
2. **数据迁移**：可能丢失数据或产生不一致
3. **前端构建**：可能引入TypeScript类型错误

### 缓解措施
1. 分阶段提交，每个阶段独立测试
2. 保留数据库备份，支持快速回滚
3. 使用TypeScript严格模式，构建前检查类型错误

---

## 预计总耗时
- **开发修改**：约2小时
- **测试验证**：约30分钟
- **数据迁移**：约15分钟
- **总计**：约2.75小时

---

## 回滚计划

如果重构失败，回滚步骤：
1. 恢复 git 提交到重构前版本
2. 从备份表恢复数据库：`restore_from_backup.sql`
3. 重启后端和前端服务

---

## 检查清单

完成后请检查：
- [ ] 所有数据库方法已更新
- [ ] 所有API路由已更新
- [ ] 前端类型定义已更新
- [ ] 前端API调用已更新
- [ ] 前端组件已更新
- [ ] 前端构建成功
- [ ] 后端API测试通过
- [ ] 前端功能测试通过
- [ ] 数据迁移脚本已准备
- [ ] 回滚方案已确认

---

*重构计划生成时间：2025-11-07*
*预计完成时间：2025-11-07*
