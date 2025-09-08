# 自动标书生成系统

这是一个智能化的标书生成系统，能够自动解析招标文件和产品技术文档，通过智能匹配和AI内容生成，自动创建完整的技术方案标书。

## 功能特点

### 核心功能
- **招标文件解析**: 自动提取需求说明和评分标准
- **产品文档解析**: 解析技术说明书，提取功能特性
- **智能匹配**: 精确匹配和语义匹配相结合
- **大纲生成**: 根据评分标准自动生成技术方案大纲
- **内容生成**: 基于匹配度智能选择内容生成策略

### 技术特色
- **多级匹配策略**: 
  - 精确匹配(>0.8): 直接复用产品文档内容
  - 高匹配(0.5-0.8): LLM改写适配需求
  - 低匹配(<0.5): AI生成全新内容
- **文档格式支持**: PDF、Word、Excel、文本文件
- **AI集成**: 支持OpenAI兼容API接口
- **模块化设计**: 各模块独立，便于扩展和维护

## 系统架构

```
TenderGenerator/
├── main.py                    # 主程序入口
├── config.py                 # 配置文件
├── parsers/                  # 文档解析模块
│   ├── tender_parser.py      # 招标文件解析器
│   └── product_parser.py     # 产品文档解析器
├── matchers/                 # 匹配引擎模块
│   ├── exact_matcher.py      # 精确匹配引擎
│   └── semantic_matcher.py   # 语义匹配引擎
├── generators/               # 生成器模块
│   ├── outline_generator.py  # 大纲生成器
│   └── content_generator.py  # 内容生成器
└── utils/                    # 工具模块
    ├── file_utils.py         # 文件处理工具
    └── llm_client.py         # LLM客户端封装
```

## 安装配置

### 1. 环境要求
- Python 3.8+
- 依赖包安装：
```bash
pip install -r requirements.txt
```

### 2. API配置
修改 `config.py` 中的API配置：
```python
SHIHUANG_API_KEY = "your-api-key-here"
SHIHUANG_BASE_URL = "https://api.oaipro.com/v1"
SHIHUANG_MODEL = "gpt-4o-mini"
```

### 3. 参数调整
根据需要调整匹配阈值：
```python
EXACT_MATCH_THRESHOLD = 0.8    # 直接复制阈值
REWRITE_THRESHOLD = 0.5        # 改写阈值
GENERATE_THRESHOLD = 0.3       # 原创生成阈值
```

## 使用方法

### 命令行使用

#### 1. 生成完整技术方案
```bash
python main.py --tender 招标文件.pdf --product 产品说明书.docx --output 项目名称
```

#### 2. 仅分析文件（不生成方案）
```bash
python main.py --tender 招标文件.pdf --product 产品说明书.docx --analyze-only
```

#### 3. 测试API连接
```bash
python main.py --tender 招标文件.pdf --product 产品说明书.docx --test-api
```

### Python代码使用

```python
from TenderGenerator import TenderGenerator

# 创建生成器实例
generator = TenderGenerator()

# 生成技术方案
result = generator.generate_proposal(
    tender_file="path/to/tender.pdf",
    product_file="path/to/product.docx",
    output_prefix="my_project"
)

if result['success']:
    print(f"生成成功！输出文件：{result['output_files']}")
else:
    print(f"生成失败：{result['error']}")
```

## 输出文件

系统会在 `output/` 目录下生成以下文件：

- `{prefix}_outline.json` - 技术方案大纲（JSON格式）
- `{prefix}_proposal.txt` - 技术方案内容（文本格式）
- `{prefix}_match_report.json` - 匹配度报告（JSON格式）
- `{prefix}_full_data.json` - 完整数据（包含所有分析结果）

## 工作流程

### 1. 文档解析阶段
- 解析招标文件，提取需求说明和评分标准
- 解析产品文档，提取功能特性和技术规格
- 对文档内容进行结构化处理

### 2. 智能匹配阶段  
- **精确匹配**: 基于关键词和文本相似度
- **语义匹配**: 基于TF-IDF和语义词典
- 为每个需求找到最匹配的产品功能

### 3. 大纲生成阶段
- 根据评分标准生成章节结构
- 按权重和重要性排序章节
- 生成子章节和要点列表

### 4. 内容生成阶段
- 根据匹配度选择生成策略：
  - 高匹配度：直接复用产品文档内容
  - 中匹配度：LLM改写产品内容适配需求
  - 低匹配度：AI生成全新技术方案内容

## 核心算法

### 匹配算法
1. **文本预处理**: 清理、分词、去停用词
2. **特征提取**: TF-IDF向量化
3. **相似度计算**: 余弦相似度 + 语义相似度
4. **综合评分**: 加权平均多个相似度指标

### 内容生成策略
```python
if match_score >= 0.8:
    strategy = "直接复用"  # 精确匹配
elif match_score >= 0.5:
    strategy = "改写适配"  # 高度匹配  
elif match_score >= 0.3:
    strategy = "AI生成"   # 中等匹配
else:
    strategy = "模板生成" # 低匹配度
```

## 扩展开发

### 添加新的文档格式支持
在 `utils/file_utils.py` 中添加新的解析方法：

```python
def read_new_format(self, file_path: str) -> Dict[str, Any]:
    # 实现新格式的解析逻辑
    pass
```

### 集成新的匹配算法
在 `matchers/` 目录下创建新的匹配器：

```python
class NewMatcher:
    def match_requirements_with_features(self, requirements, features):
        # 实现新的匹配算法
        pass
```

### 自定义内容生成模板
修改 `generators/content_generator.py` 中的模板：

```python
def _generate_fallback_content(self, subsection_title: str, parent_title: str) -> str:
    # 自定义内容生成模板
    pass
```

## 性能优化

### 1. 缓存机制
- 文档解析结果缓存
- API调用结果缓存
- 匹配计算结果缓存

### 2. 批处理
- 批量API调用减少延迟
- 并行处理多个匹配任务

### 3. 配置调优
- 调整匹配阈值优化准确性
- 优化提示词提升生成质量
- 限制处理文档大小避免超时

## 故障排除

### 常见问题

1. **API调用失败**
   - 检查API密钥和网络连接
   - 确认API接口地址正确
   - 查看日志文件了解详细错误

2. **文档解析失败**  
   - 确认文档格式支持
   - 检查文件是否损坏
   - 查看文档是否有密码保护

3. **内容生成质量差**
   - 调整匹配阈值参数
   - 优化提示词模板
   - 检查产品文档质量

4. **匹配度过低**
   - 检查关键词配置
   - 扩展语义词典
   - 优化文本预处理逻辑

### 调试模式
启用详细日志：
```python
LOG_LEVEL = "DEBUG"
```

查看中间结果：
```bash
python main.py --analyze-only --tender file.pdf --product doc.docx
```

## 版本历史

- **v1.0.0** - 初始版本
  - 基础文档解析功能
  - 精确匹配和语义匹配
  - AI内容生成集成
  - 完整的标书生成流程

## 技术支持

如需技术支持或功能扩展，请联系开发团队。

## 许可证

本项目采用 MIT 许可证。