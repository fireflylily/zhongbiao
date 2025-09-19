# 联通元景大模型集成使用指南

## 📋 配置说明

### 环境变量配置 (.env文件)

```bash
# 联通元景大模型配置
ACCESS_TOKEN=sk-40a84bd082404004b9741e3a18d5f881
UNICOM_BASE_URL=https://maas-api.ai-yuanjing.com/openapi/compatible-mode/v1
UNICOM_MODEL_NAME=deepseek-v3
UNICOM_MAX_TOKENS=1000
UNICOM_TIMEOUT=30
```

### 重要说明

- **ACCESS_TOKEN**: 联通元景API访问令牌（必须使用`ACCESS_TOKEN`而不是`UNICOM_API_KEY`）
- **模型名称**: 当前支持 `deepseek-v3` 模型
- **访问限制**: 试用账号每分钟最多调用5次

## 🚀 使用方法

### 1. 在代码中使用

```python
from common.llm_client import create_llm_client

# 创建联通元景客户端
client = create_llm_client('unicom-yuanjing')

# 调用API
response = client.call(
    prompt="你的问题",
    system_prompt="可选的系统提示",  # 可选
    purpose="调用目的"  # 用于日志记录
)

print(response)
```

### 2. 在Web界面使用

1. 启动Web服务: `python3 web/app.py`
2. 访问 http://localhost:8082
3. 在模型选择中选择"联通元景大模型"
4. 使用各项功能

## ⚠️ 访问频率限制

### 限制规则

- **试用账号限制**: 每分钟最多5次调用
- **自动控制**: 系统已实现自动频率控制
- **智能等待**: 超过限制时自动等待

### 频率控制机制

系统会自动：
1. 记录每次调用时间
2. 检查前60秒内的调用次数
3. 如果达到5次，自动等待至下一分钟
4. 遇到限流错误时，等待60秒后重试

## 🔧 故障排除

### 常见问题

#### 1. TOKEN错误 (错误代码: 1000)
- **原因**: ACCESS_TOKEN无效或配置错误
- **解决**: 检查.env文件中的ACCESS_TOKEN是否正确

#### 2. 限流错误 (错误代码: 5001)
- **原因**: 超过访问频率限制
- **解决**: 系统会自动处理，等待60秒后重试

#### 3. 服务不可用 (错误代码: 14)
- **原因**: 模型暂时不可用或服务问题
- **解决**: 稍后重试或使用其他模型

#### 4. 404错误
- **原因**: API端点配置错误
- **解决**: 确保UNICOM_BASE_URL配置正确

### 验证配置

运行以下命令测试配置：

```bash
# 快速测试
python3 quick_test.py

# 完整测试
python3 test_yuanjing_official.py

# 频率限制测试
python3 test_rate_limit.py
```

## 📊 API调用示例

### 基础对话

```python
response = client.call(
    prompt="请介绍一下Python语言",
    purpose="技术介绍"
)
```

### 带系统提示的对话

```python
response = client.call(
    prompt="分析这份招标文件的要点",
    system_prompt="你是专业的标书分析助手",
    purpose="招标分析"
)
```

### 控制生成长度

```python
client.max_tokens = 500  # 设置最大生成令牌数
response = client.call(
    prompt="写一个简短的故事",
    purpose="创意写作"
)
```

## 🎯 最佳实践

1. **合理规划调用频率**: 避免短时间内大量调用
2. **使用缓存**: 对相同问题的答案进行缓存
3. **批量处理**: 将多个小问题合并成一个请求
4. **错误处理**: 总是捕获APIError异常
5. **日志记录**: 使用purpose参数记录调用目的

## 📝 注意事项

- 试用账号有访问频率限制
- API密钥请妥善保管，不要提交到版本控制
- 生产环境建议申请正式账号以获得更高的访问限额
- 定期检查API使用量，避免超出配额

## 🔗 相关资源

- [联通元景官网](https://maas.ai-yuanjing.com)
- [API文档](https://maas.ai-yuanjing.com/doc/pages/216556732/)
- 技术支持: 联系联通元景客服

---

更新日期: 2025-09-19
版本: 1.0