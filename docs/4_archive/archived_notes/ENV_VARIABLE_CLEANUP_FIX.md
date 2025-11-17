# 环境变量自动清理修复文档

## 问题描述

**错误信息**：
```
Invalid non-printable ASCII character in URL, '\n' at position 52
```

**根本原因**：
Railway环境变量中的URL包含了**不可见的换行符（\n）**或其他不可打印字符。这通常发生在：
1. 从文本编辑器复制粘贴URL到Railway Dashboard时
2. 环境变量值末尾意外包含换行符
3. 多行字符串被错误地设置为环境变量

## 影响范围

所有从环境变量读取的URL和Token，包括：
- `OPENAI_API_ENDPOINT`
- `UNICOM_BASE_URL`
- `EMBEDDING_API_ENDPOINT`
- `ACCESS_TOKEN`
- `OPENAI_API_KEY`
- `SHIHUANG_API_KEY`

## 解决方案

### 代码层面自动清理（已实现）

#### 1. 新增清理函数 (`ai_tender_system/common/config.py`)

```python
def clean_env_value(value: str) -> str:
    """
    清理环境变量值，移除不可见字符

    - 自动移除前后空格、换行符、制表符等
    - 检测并警告包含不可见字符的情况
    - 返回清理后的值
    """
    if not value:
        return value

    cleaned = value.strip()

    # 检测并警告
    if cleaned != value:
        logger.warning(
            f"环境变量包含不可见字符 (长度: {len(value)} → {len(cleaned)}): "
            f"{repr(value)[:50]}..."
        )

    return cleaned
```

#### 2. 应用清理函数到所有环境变量读取

**修改文件**：
- `ai_tender_system/common/config.py` - 所有模型配置
- `ai_tender_system/modules/vector_engine/embedding_service.py` - 嵌入服务

**示例**：
```python
# ❌ 旧代码
'base_url': os.getenv('UNICOM_BASE_URL', 'https://...')

# ✅ 新代码
'base_url': clean_env_value(os.getenv('UNICOM_BASE_URL', 'https://...'))
```

#### 3. 自动警告日志

当环境变量包含不可见字符时，系统会在启动时输出警告：
```
2025-10-27 10:30:15 - config - WARNING - 环境变量包含不可见字符 (长度: 53 → 52): 'https://api.oaipro.com/v1\n'...
```

## 使用诊断工具

我们提供了一个诊断脚本来检查环境变量：

```bash
python scripts/diagnose_env.py
```

**输出示例**：
```
============================================================
检查环境变量: OPENAI_API_ENDPOINT
============================================================
原始值长度: 53
原始值 (repr): 'https://api.oaipro.com/v1\n'

⚠️ 发现问题:
  - 包含换行符 (\n)

✅ 清理后的值: https://api.oaipro.com/v1
✅ 清理后长度: 52
```

## Railway环境配置建议

### 正确设置方式

1. **手动输入**（推荐）：
   - 在Railway Dashboard中直接手动输入URL
   - 不要从文本编辑器复制粘贴

2. **使用Railway CLI**：
   ```bash
   railway variables set OPENAI_API_ENDPOINT=https://api.oaipro.com/v1
   ```

3. **从.env文件导入**：
   ```bash
   railway variables set -f .env
   ```

### 错误设置示例

❌ **不要这样做**：
- 从Word/Notes复制粘贴URL
- 从多行文本中复制URL（可能包含隐藏换行符）
- 在环境变量值后按Enter键

## 验证修复

### 本地验证

1. 启动服务：
   ```bash
   FLASK_RUN_PORT=8110 python3 -m ai_tender_system.web.app
   ```

2. 查看启动日志，确认无警告：
   ```
   2025-10-27 10:30:15 - config - INFO - 加载环境变量文件: /path/to/.env
   ```

3. 测试API调用（如商务应答生成）

### Railway验证

1. 部署新代码到Railway
2. 查看部署日志，确认无环境变量警告
3. 测试系统功能

## 技术细节

### 为什么会出现换行符？

1. **文本编辑器换行**：
   - macOS/Linux: `\n` (LF)
   - Windows: `\r\n` (CRLF)

2. **复制粘贴行为**：
   - 某些编辑器在复制时会包含结尾换行符
   - Railway Dashboard解析环境变量时不会自动trim

3. **Python URL验证**：
   - `requests` 库严格验证URL格式
   - 不允许URL中包含换行符等控制字符

### 清理函数的安全性

`clean_env_value()` 只清理：
- 前后空格 (leading/trailing spaces)
- 换行符 `\n`
- 回车符 `\r`
- 制表符 `\t`

**不会影响**：
- URL中的有效字符（`://`, `/`, `?`, `&`等）
- Token/API Key的有效字符

## 相关资源

- **Python requests文档**: https://requests.readthedocs.io/
- **Railway环境变量文档**: https://docs.railway.app/develop/variables
- **项目诊断脚本**: `scripts/diagnose_env.py`

## 后续改进建议

1. **添加环境变量验证中间件**：
   - 启动时检查所有关键环境变量
   - 提供友好的错误提示

2. **创建环境变量模板**：
   - 为Railway提供标准的 `railway.json`
   - 包含所有必需的环境变量和默认值

3. **自动化测试**：
   - 添加环境变量格式验证的单元测试
   - CI/CD中检查环境变量配置

## 修复历史

- **2025-10-27**: 初次修复，添加 `clean_env_value()` 函数和自动清理逻辑
- **影响模块**: config.py, embedding_service.py
- **向后兼容**: 是（对正常环境变量无影响）
