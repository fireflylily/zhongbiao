# 章节解析器A/B测试快速指南

## 🎯 功能概述

全新的**隔离式多解析器架构**,让你可以对比测试不同解析器的效果:

- ✅ **内置解析器** - 免费、快速,基于现有代码
- ✅ **Gemini AI** - 智能理解、支持复杂布局
- ✅ **清晰隔离** - 各解析器互不干扰,可独立测试
- ✅ **可视化对比** - Web界面直观对比效果

---

## 🚀 快速开始(5分钟)

### 步骤1: 安装依赖(可选)

如果要测试Gemini解析器:

```bash
pip install google-generativeai
```

### 步骤2: 配置API密钥(可选)

在`.env`文件添加(如果使用Gemini):

```ini
# Google Gemini API(免费额度足够测试)
GEMINI_API_KEY=your_api_key_here
```

**获取密钥**: 访问 https://ai.google.dev/

### 步骤3: 启动应用

```bash
python -m ai_tender_system.web.app
```

### 步骤4: 打开测试页面

浏览器访问:
```
http://localhost:5000/abtest/parser-test
```

### 步骤5: 上传文档测试

1. 点击"上传文档",选择招标文件(.docx或.doc)
2. 勾选要测试的解析器(如:内置解析器 + Gemini)
3. 点击"开始对比测试"
4. 查看对比结果

---

## 📊 对比结果说明

测试完成后,页面会显示:

### 1. 汇总指标

| 指标 | 说明 | 示例 |
|------|------|------|
| **最快** | 解析速度最快的解析器 | builtin (2.3秒) |
| **章节最多** | 识别章节数最多 | gemini (18个) |
| **置信度最高** | 结果最可靠 | gemini (95分) |
| **成本最低** | API调用成本最低 | builtin (免费) |

### 2. 详细对比

每个解析器显示:
- ⏱️ **耗时**: 解析所需时间
- 📋 **章节数**: 识别的章节数量
- ✓ **置信度**: 结果可靠性评分(0-100)
- 💰 **成本**: API调用成本(元)
- 🌳 **章节树**: 完整的层级结构

### 3. 章节标记

- 🟢 **绿色边框** - 自动选中(白名单匹配)
- 🔴 **红色边框** - 推荐跳过(黑名单匹配)

---

## 🔍 典型测试场景

### 场景1: 格式规范的标准招标文档

**推荐**: 使用内置解析器
- 免费、快速
- 准确率高(样式规范时)

### 场景2: 格式不规范的复杂文档

**推荐**: 使用Gemini
- 理解语义,不依赖样式
- 支持复杂布局、多语言

### 场景3: 不确定文档质量

**推荐**: 并行测试2-3个解析器
- 对比结果,选择最佳
- 找出最适合的解析器

---

## 🧪 测试建议

### 测试文档类型

建议准备以下类型的文档进行测试:

1. **标准格式** - 格式规范、样式清晰的文档
2. **非标格式** - 样式混乱、编号不规范
3. **复杂布局** - 多层级、表格嵌套
4. **PDF扫描件** - 图片型文档(仅Gemini支持)

### 评价标准

| 标准 | 权重 | 说明 |
|------|------|------|
| **准确性** | 40% | 是否正确识别所有章节 |
| **速度** | 30% | 解析耗时 |
| **成本** | 20% | API调用费用 |
| **易用性** | 10% | 配置难度 |

---

## 💡 常见问题

### Q1: Gemini解析器显示"不可用"?

**解决**:
1. 检查是否安装依赖: `pip list | grep google-generativeai`
2. 检查API密钥: `echo $GEMINI_API_KEY`
3. 如果密钥未设置,在`.env`文件添加

### Q2: 解析失败怎么办?

**调试步骤**:
1. 查看浏览器控制台(F12)的错误信息
2. 查看后端日志输出
3. 确认文档格式(.docx或.doc)
4. 尝试其他解析器

### Q3: Gemini成本高吗?

**答**: 非常低!
- 免费额度: 每分钟15次请求
- 10页文档: 约0.01-0.05元
- 100页文档: 约0.1-0.5元
- PDF原生文字提取免费(不计token)

### Q4: 内置解析器与Gemini哪个好?

**对比**:

| 解析器 | 优势 | 劣势 | 推荐场景 |
|--------|------|------|----------|
| 内置 | 免费、快速 | 依赖样式规范性 | 标准格式文档 |
| Gemini | 理解语义、支持复杂布局 | 需API密钥、有成本 | 非标格式、复杂文档 |

**建议**: 先测试内置解析器,效果不佳时再用Gemini

---

## 📁 文件说明

本次添加的文件:

```
ai_tender_system/modules/tender_processing/parsers/
├── __init__.py              # ⭐️ 解析器接口和工厂类
├── builtin_parser.py        # ⭐️ 内置解析器(包装现有代码)
├── gemini_parser.py         # ⭐️ Gemini AI解析器
└── README.md                # 开发文档

abtest/blueprints/
└── parser_abtest_bp.py      # ⭐️ A/B测试API

abtest/templates/
└── parser_test.html         # ⭐️ A/B测试页面

abtest/__init__.py           # 🔧 修改:注册新蓝图
PARSER_ABTEST_GUIDE.md      # 📖 本文档
```

**核心优势**:
- 🔒 **隔离性** - 各解析器独立,不会相互影响
- 🧪 **可测试** - 方便A/B对比
- 📈 **可扩展** - 未来可轻松添加新解析器(如PaddleOCR)

---

## 🔄 后续计划

### 短期(1周内)

1. ✅ 完成架构搭建
2. ✅ 实现内置+Gemini解析器
3. ⏳ 测试5-10个真实文档
4. ⏳ 收集效果数据

### 中期(1个月)

1. 根据测试结果优化Prompt
2. 可选:添加PaddleOCR解析器
3. 建立解析质量评分体系

### 长期(3个月)

1. 根据效果选择主力解析器
2. 集成到主流程(HITL1)
3. 建立文档类型-解析器映射规则

---

## 🛠️ 代码示例

### Python脚本使用

```python
from ai_tender_system.modules.tender_processing.parsers import ParserFactory

# 创建解析器
builtin = ParserFactory.create_parser('builtin')
gemini = ParserFactory.create_parser('gemini')

# 解析文档
doc_path = '/path/to/招标文档.docx'

result1 = builtin.parse_structure(doc_path)
result2 = gemini.parse_structure(doc_path)

# 对比结果
print(f"内置: {result1['metrics'].chapters_found}个章节, {result1['metrics'].parse_time:.2f}秒")
print(f"Gemini: {result2['metrics'].chapters_found}个章节, {result2['metrics'].parse_time:.2f}秒")
```

### 添加自定义解析器

```python
# 创建文件: parsers/my_parser.py
from . import BaseStructureParser, ParserMetrics

class MyParser(BaseStructureParser):
    def parse_structure(self, doc_path: str) -> Dict:
        # 你的解析逻辑
        ...

    def is_available(self) -> bool:
        return True

    def get_parser_info(self) -> Dict:
        return {
            "name": "my_parser",
            "display_name": "我的解析器",
            ...
        }

# 注册
from . import ParserFactory
ParserFactory.register_parser('my_parser', MyParser)
```

---

## 📞 支持

遇到问题?

1. 查看日志: 后端控制台输出
2. 查看README: `parsers/README.md`
3. 提Issue: GitHub Issues

---

## ✅ 总结

你现在拥有:

1. ✅ **清晰隔离的架构** - 各解析器互不干扰
2. ✅ **可视化测试平台** - 直观对比效果
3. ✅ **两种解析器** - 内置(免费) + Gemini(智能)
4. ✅ **可扩展设计** - 轻松添加新解析器

**建议行动**:
1. 立即测试5个真实招标文档
2. 记录各解析器的表现
3. 根据效果决定是否引入主流程

祝测试顺利! 🎉
