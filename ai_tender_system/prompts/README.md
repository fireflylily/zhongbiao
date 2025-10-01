# 统一提示词管理系统实施文档

## 概述

本文档记录了统一提示词管理系统的设计、实施和使用说明。

**实施日期**: 2025-10-01
**版本**: 1.0.0

## 一、项目背景

### 问题分析

在重构前，提示词管理存在以下问题：

1. **分散管理**: 提示词散落在多个 Python 文件中
2. **硬编码**: 提示词以模块常量或方法返回值形式硬编码
3. **维护困难**: 修改提示词需要改代码，容易出错
4. **重复定义**: 相似的提示词在不同文件中重复定义
5. **版本控制困难**: 提示词变更混在代码变更中

### 受影响的文件

原有硬编码提示词位置：
- `modules/point_to_point/tech_responder.py` (28-33行)
- `modules/business_response/inline_processor.py` (41-67行)
- `modules/point_to_point/enhanced_inline_reply.py` (244-287行)

## 二、解决方案设计

### 架构设计

```
ai_tender_system/
├── prompts/                    # 提示词目录
│   ├── README.md              # 本文档
│   ├── point_to_point.json    # 点对点应答提示词
│   ├── business_response.json # 商务响应提示词
│   └── common.json            # 通用提示词
├── common/
│   ├── prompt_manager.py      # 提示词管理器
│   └── __init__.py            # 导出 PromptManager
└── modules/
    ├── point_to_point/
    │   ├── tech_responder.py           # 已重构
    │   └── enhanced_inline_reply.py    # 已重构
    └── business_response/
        └── inline_processor.py         # 已重构
```

### 核心组件

#### 1. PromptManager (提示词管理器)

**位置**: `common/prompt_manager.py`

**功能**:
- 单例模式，全局共享
- 从 JSON 文件加载提示词
- 提供缓存机制，提高性能
- 支持默认值和回退机制
- 支持热更新（重新加载）

**主要方法**:
```python
# 获取提示词
get_prompt(module_name, prompt_key, default=None) -> str

# 获取所有提示词
get_all_prompts(module_name) -> Dict

# 重新加载
reload_prompts(module_name=None)

# 列出模块
list_modules() -> List

# 获取模块信息
get_module_info(module_name) -> Dict
```

#### 2. JSON 提示词文件

**格式规范**:
```json
{
  "module": "模块名称",
  "description": "模块描述",
  "version": "版本号",
  "updated_at": "更新时间",
  "prompts": {
    "key1": "提示词内容1",
    "key2": "提示词内容2"
  }
}
```

## 三、实施步骤

### 步骤1: 创建提示词文件结构 ✅

创建了以下文件：
- `prompts/point_to_point.json`
- `prompts/business_response.json`
- `prompts/common.json`

### 步骤2: 创建提示词管理器 ✅

实现了 `common/prompt_manager.py`，包含：
- `PromptManager` 类（单例模式）
- 便捷函数：`get_prompt()`, `reload_prompts()`
- 完整的错误处理和日志记录

### 步骤3: 重构现有代码 ✅

已重构的文件：
1. **tech_responder.py**
   - 删除了硬编码的 `PROMPT_ANSWER`, `PROMPT_CONTENT`, `PROMPT_TITLE`
   - 在 `__init__` 中初始化 `prompt_manager`
   - 修改 `get_inline_system_prompt()` 使用 PromptManager
   - 修改 `generate_inline_response()` 使用 PromptManager

2. **inline_processor.py**
   - 删除了 `PROMPT_TEMPLATES` 类属性字典
   - 在 `__init__` 中初始化 `prompt_manager`
   - 修改 `generate_professional_response()` 使用 PromptManager

3. **enhanced_inline_reply.py**
   - 将全局常量改为 None（保留向后兼容）
   - 在 `__init__` 中初始化 `prompt_manager`
   - 修改 `get_system_prompt()` 使用 PromptManager
   - 修改 `_get_fallback_response()` 使用 PromptManager

### 步骤4: 导出到公共模块 ✅

修改 `common/__init__.py`，导出：
- `get_prompt_manager`
- `PromptManager`
- `get_prompt`
- `reload_prompts`

## 四、使用说明

### 基本用法

```python
from common import get_prompt_manager

# 获取管理器实例
pm = get_prompt_manager()

# 获取提示词
prompt = pm.get_prompt('point_to_point', 'answer')

# 获取所有提示词
all_prompts = pm.get_all_prompts('point_to_point')

# 重新加载提示词
pm.reload_prompts('point_to_point')
```

### 便捷用法

```python
from common import get_prompt

# 直接获取提示词
prompt = get_prompt('point_to_point', 'answer', default='默认值')
```

### 在模块中使用

```python
class MyProcessor:
    def __init__(self):
        self.prompt_manager = get_prompt_manager()

    def process(self, text):
        # 获取提示词
        prompt_template = self.prompt_manager.get_prompt(
            'business_response',
            'point_to_point',
            default="默认提示词"
        )

        # 使用提示词
        prompt = f"{prompt_template}'{text}'"
        # ... 继续处理
```

## 五、提示词配置

### point_to_point.json

**包含提示词**:
- `answer`: 点对点应答格式提示词
- `content`: 内容生成提示词
- `title`: 标题简化提示词
- `system_prompt`: 系统级提示词

### business_response.json

**包含提示词**:
- `point_to_point`: 点对点应答
- `content_generation`: 内容生成
- `title_simplification`: 标题简化
- `system_default`: 默认系统提示词

### common.json

**包含提示词**:
- `default`: 通用默认提示词
- `fallback`: 备用应答

## 六、优势总结

1. **集中管理**: 所有提示词在一个目录下，易于查找和管理
2. **易于修改**: 无需改代码，直接编辑 JSON 文件
3. **版本控制**: 可以跟踪提示词的历史变更
4. **多环境支持**: 可为开发/测试/生产配置不同提示词
5. **可视化管理**: 未来可添加 Web UI 管理界面
6. **性能优化**: 缓存机制提高加载速度
7. **向后兼容**: 保留默认值，不影响现有功能

## 七、维护指南

### 修改提示词

1. 打开对应的 JSON 文件
2. 找到要修改的提示词键
3. 修改提示词内容
4. 更新 `updated_at` 字段
5. 保存文件

### 添加新提示词

1. 打开对应的 JSON 文件
2. 在 `prompts` 对象中添加新键值对
3. 更新 `version` 和 `updated_at`
4. 保存文件

### 创建新模块

1. 在 `prompts/` 目录创建新的 JSON 文件
2. 按照格式规范编写内容
3. 在代码中使用 `get_prompt('新模块名', 'key')`

### 热更新提示词

```python
from common import reload_prompts

# 重新加载特定模块
reload_prompts('point_to_point')

# 重新加载所有模块
reload_prompts()
```

## 八、注意事项

1. **JSON 格式**: 确保 JSON 格式正确，避免解析错误
2. **文件编码**: 使用 UTF-8 编码保存文件
3. **提示词长度**: 注意提示词长度，避免超过 API 限制
4. **测试验证**: 修改提示词后务必测试功能是否正常
5. **备份**: 修改前建议备份原有文件
6. **部署**: 提示词文件需要包含在部署包中

## 九、未来规划

1. **Web 管理界面**: 开发可视化的提示词管理界面
2. **A/B 测试**: 支持多版本提示词对比测试
3. **统计分析**: 记录提示词使用情况和效果
4. **智能推荐**: 根据场景智能推荐合适的提示词
5. **多语言支持**: 支持多语言提示词配置

## 十、问题反馈

如遇到问题，请检查：
1. JSON 文件格式是否正确
2. 提示词键名是否匹配
3. 默认值是否设置
4. 日志中的错误信息

## 附录

### A. 提示词键名映射表

| 原代码位置 | 新位置 | 提示词键 |
|-----------|--------|---------|
| tech_responder.PROMPT_ANSWER | point_to_point.json | answer |
| tech_responder.PROMPT_CONTENT | point_to_point.json | content |
| tech_responder.PROMPT_TITLE | point_to_point.json | title |
| inline_processor.PROMPT_TEMPLATES['point_to_point'] | business_response.json | point_to_point |
| inline_processor.PROMPT_TEMPLATES['system_default'] | business_response.json | system_default |
| enhanced_inline_reply.get_system_prompt('point_to_point') | point_to_point.json | system_prompt |
| enhanced_inline_reply._get_fallback_response() | common.json | fallback |

### B. 参考资料

- PromptManager 源码: `common/prompt_manager.py`
- 提示词文件: `prompts/*.json`
- 测试代码: `python -m common.prompt_manager`

---

**文档维护**: AI 标书系统开发团队
**最后更新**: 2025-10-01
