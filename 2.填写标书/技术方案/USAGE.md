# 标书生成系统使用说明

## 功能更新

✅ **Word文档输出**：技术方案现在输出为Word文档格式（.docx）而非文本文件  
✅ **招标文件格式参考**：Word文档格式参考招标文件样式，包含标题页、章节结构等  
✅ **评分表格解析修复**：完美解决招标文件评分表格读取问题

## 基本用法

### 命令语法
```bash
python3 main.py --tender <招标文件路径> --product <产品文档路径> --output <输出前缀>
```

### 参数说明
- `--tender, -t`：招标文件路径（必需）
- `--product, -p`：产品文档路径（必需）  
- `--output, -o`：输出文件前缀（可选，默认为"proposal"）
- `--test-api`：测试API连接（可选）
- `--analyze-only`：仅分析文件不生成方案（可选）

## 使用示例

### 示例1：完整生成技术方案
```bash
python3 main.py \
  --tender "/Users/lvhe/Library/Mobile Documents/com~apple~CloudDocs/Work/智慧足迹2025/05投标项目/AI标书/项目/中邮保险/中邮保险手机号实名认证服务采购项目竞争性磋商采购文件(1).docx" \
  --product "/Users/lvhe/Library/Mobile Documents/com~apple~CloudDocs/Work/智慧足迹2022/售前项目/2.投标项目/资料收集/产品技术方案/服务方案.docx" \
  --output "中邮技术方案"
```

### 示例2：仅分析文件
```bash
python3 main.py \
  --tender "招标文件.docx" \
  --product "产品方案.docx" \
  --analyze-only
```

### 示例3：测试API连接
```bash
python3 main.py \
  --tender "招标文件.docx" \
  --product "产品方案.docx" \
  --test-api
```

## 输出文件

系统会在项目目录下生成以下文件：

### 1. 技术方案文档（Word格式）
- **文件名**：`{output}_proposal.docx`
- **内容**：完整的技术方案Word文档
- **格式**：参考招标文件样式，包含：
  - 标题页（项目信息表格）
  - 各章节内容（按大纲生成）
  - 标准化格式（宋体正文，黑体标题）

### 2. 方案大纲（JSON格式）
- **文件名**：`{output}_outline.json`
- **内容**：技术方案章节大纲结构

### 3. 匹配分析报告（JSON格式）
- **文件名**：`{output}_match_report.json`
- **内容**：需求与产品功能匹配度分析

### 4. 完整数据（JSON格式）
- **文件名**：`{output}_full_data.json`
- **内容**：包含所有解析和生成数据

## 输出示例

使用上述示例命令后，会生成：
```
📁 输出文件:
  - outline: /path/to/output/中邮技术方案_outline.json
  - proposal: /path/to/output/中邮技术方案_proposal.docx  ← Word文档
  - match_report: /path/to/output/中邮技术方案_match_report.json
  - full_data: /path/to/output/中邮技术方案_full_data.json
```

## 技术方案Word文档特点

### 文档结构
1. **标题页**
   - 项目标题居中
   - 项目信息表格（项目名称、方案类型、编制日期等）

2. **章节内容**
   - 层次化标题（1级~4级）
   - 格式化段落（列表、加粗等）
   - 标准字体和间距

3. **样式规范**
   - 正文：宋体12pt
   - 标题：黑体，1级18pt，2级16pt，3级14pt，4级12pt
   - 行间距：1.15倍
   - 段后间距：6pt

### Word文档优势
- ✅ 专业格式，符合投标要求
- ✅ 易于编辑和二次修改
- ✅ 支持复杂格式（表格、图片等）
- ✅ 兼容Office和WPS等办公软件
- ✅ 可直接用于投标文件提交

## 错误处理

### 如果Word生成失败
系统会自动fallback到文本格式：
- 生成 `{output}_proposal.txt` 文件
- 保留所有内容，仅格式不同
- 日志中会显示具体错误信息

### 常见问题
1. **python-docx未安装**：运行 `pip install python-docx`
2. **文件路径错误**：确保文件路径正确且文件存在
3. **权限问题**：确保对输出目录有写权限

## 系统要求

### 必需依赖
- Python 3.8+
- python-docx
- PyPDF2（用于PDF文件）
- openpyxl（用于Excel文件）

### 安装依赖
```bash
pip install python-docx PyPDF2 openpyxl
```

## 更新日志

### v2.0 (当前版本)
- ✅ 新增Word文档输出功能
- ✅ 修复评分表格解析问题
- ✅ 优化文档格式和样式
- ✅ 增强错误处理和fallback机制

### v1.0
- 基础文本格式输出
- 需求匹配和方案生成
- JSON格式数据输出

---

**提示**：系统现在完全支持Word文档输出，生成的技术方案可直接用于投标文件！