# 文档结构解析器架构说明

## 📁 目录结构

```
parsers/
├── __init__.py              # 解析器接口和工厂类
├── builtin_parser.py        # 内置解析器(包装现有structure_parser)
├── gemini_parser.py         # Gemini AI解析器
└── README.md               # 本文档
```

## 🎯 设计理念

### 1. **策略模式** - 灵活切换解析器
每个解析器都实现`BaseStructureParser`接口,可以随时切换使用

### 2. **隔离性** - 各解析器互不干扰
- `builtin_parser.py` - 只调用现有代码,不修改
- `gemini_parser.py` - 完全独立实现
- 未来可添加更多解析器(如PaddleOCR、DeepSeek等)

### 3. **可测试性** - 便于A/B测试
通过`ParserFactory`统一创建和管理,方便对比测试

## 🔧 使用方法

### 基础用法

```python
from ai_tender_system.modules.tender_processing.parsers import ParserFactory

# 方式1: 使用内置解析器
parser = ParserFactory.create_parser('builtin')
result = parser.parse_structure('/path/to/document.docx')

# 方式2: 使用Gemini解析器(需配置GEMINI_API_KEY)
parser = ParserFactory.create_parser('gemini')
result = parser.parse_structure('/path/to/document.docx')

# 方式3: 获取所有可用解析器
parsers = ParserFactory.get_available_parsers()
for parser_info in parsers:
    print(f"{parser_info['display_name']}: {'可用' if parser_info['available'] else '不可用'}")
```

### A/B测试(推荐)

使用Web界面进行可视化对比测试:

1. 启动应用:
   ```bash
   python -m ai_tender_system.web.app
   ```

2. 访问测试页面:
   ```
   http://localhost:5000/abtest/parser-test
   ```

3. 上传文档,选择解析器,点击"开始对比测试"

## 📊 解析器对比

| 解析器 | 优势 | 劣势 | 适用场景 |
|--------|------|------|----------|
| **builtin** | 免费、快速、无需配置 | 依赖文档样式规范性 | 格式规范的标准招标文档 |
| **gemini** | 理解语义、支持复杂布局 | 需要API密钥、有成本 | 格式不规范、复杂布局的文档 |

## 🆕 添加新解析器

### 步骤1: 创建解析器类

```python
# parsers/my_parser.py
from . import BaseStructureParser, ParserMetrics

class MyParser(BaseStructureParser):
    def parse_structure(self, doc_path: str) -> Dict:
        # 实现你的解析逻辑
        ...

    def is_available(self) -> bool:
        # 检查依赖和配置
        ...

    def get_parser_info(self) -> Dict:
        return {
            "name": "my_parser",
            "display_name": "我的解析器",
            "description": "...",
            "requires_api": False,
            "cost_per_page": 0.0,
            "available": self.is_available()
        }

# 注册解析器
from . import ParserFactory
ParserFactory.register_parser('my_parser', MyParser)
```

### 步骤2: 在`__init__.py`中导入

```python
# parsers/__init__.py
from .my_parser import MyParser
```

## 🔍 返回结果格式

所有解析器都返回统一格式:

```python
{
    "success": True/False,
    "chapters": [
        {
            "id": "ch_0",
            "level": 1,
            "title": "第一章 投标须知",
            "para_start_idx": 5,
            "para_end_idx": 50,
            "word_count": 1000,
            "preview_text": "...",
            "auto_selected": True,  # 是否自动选中
            "skip_recommended": False,  # 是否推荐跳过
            "children": [...]
        }
    ],
    "statistics": {
        "total_chapters": 10,
        "auto_selected": 5,
        "skip_recommended": 2,
        "total_words": 15000
    },
    "metrics": ParserMetrics(
        parser_name="gemini",
        parse_time=3.5,  # 秒
        chapters_found=10,
        success=True,
        confidence_score=95.0,  # 0-100
        api_cost=0.02  # 元
    ),
    "error": "错误信息(如果失败)"
}
```

## ⚙️ 配置说明

### Gemini解析器配置

在`.env`文件添加:

```ini
# Google Gemini API
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.0-flash  # 可选,默认为gemini-2.0-flash
```

获取API密钥:
- 访问: https://ai.google.dev/
- 免费额度: 每分钟15个请求
- 成本: 极低(约0.01元/页)

## 📈 性能监控

每次解析都会记录性能指标:

```python
metrics = result['metrics']

print(f"解析器: {metrics.parser_name}")
print(f"耗时: {metrics.parse_time}秒")
print(f"识别章节: {metrics.chapters_found}个")
print(f"置信度: {metrics.confidence_score}分")
print(f"成本: {metrics.api_cost}元")
```

## 🐛 故障排查

### Gemini解析器不可用

1. 检查环境变量:
   ```bash
   echo $GEMINI_API_KEY
   ```

2. 检查依赖安装:
   ```bash
   pip install google-generativeai
   ```

3. 测试API连接:
   ```python
   import google.generativeai as genai
   genai.configure(api_key="your_key")
   print("API连接成功")
   ```

### 解析失败

查看日志获取详细错误信息:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# 然后运行解析
```

## 📚 相关文档

- [Gemini文档处理指南](https://ai.google.dev/gemini-api/docs/document-processing)
- [结构解析器原理](/docs/4_archive/ParseDocumentStructure.md)
- [ABTest使用指南](/abtest/README.md)
