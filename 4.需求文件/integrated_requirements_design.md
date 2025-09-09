# AI标书平台表格自动填充功能 - 集成需求与设计文档

## 目录
1. [项目概述](#1-项目概述)
2. [需求分析](#2-需求分析)
3. [系统设计](#3-系统设计)
4. [实施计划](#4-实施计划)
5. [风险管理](#5-风险管理)
6. [验收标准](#6-验收标准)

---

## 1. 项目概述

### 1.1 项目背景
在现有AI标书智能生成平台基础上，新增DOC/DOCX表格自动填充功能，实现招标文档中表格的智能识别、字段匹配和自动填充，形成"AI文本生成 + 表格自动填充"的完整解决方案。

### 1.2 现有系统架构
```
AI标书平台 (当前版本)
├── Web前端 (Bootstrap 5 + JavaScript)
│   ├── 点对点应答
│   ├── 商务应答
│   ├── 技术方案
│   └── 公司管理
├── Flask后端 (Python 3.x)
│   ├── 文档处理引擎 (python-docx)
│   ├── AI生成模块 (OpenAI API)
│   └── 配置管理 (JSON/INI)
└── 数据存储
    ├── 公司配置 (JSON)
    ├── 项目配置 (INI)
    └── 模板库 (JSON)
```

### 1.3 项目目标
- **主要目标**：实现招标文档表格的自动识别和填充
- **集成目标**：与现有系统无缝集成，复用配置和用户体系
- **性能目标**：单文档处理时间<30秒，支持批量处理
- **质量目标**：字段识别准确率>85%，格式保持100%

---

## 2. 需求分析

### 2.1 功能需求

#### 2.1.1 核心功能需求

| 需求编号 | 需求描述 | 优先级 | 实现状态 |
|---------|---------|--------|----------|
| FR-001 | 支持DOC/DOCX文档上传和解析 | P0 | 待开发 |
| FR-002 | 识别表格中的标签字段和填写区域 | P0 | 待开发 |
| FR-003 | 基于规则的字段智能匹配 | P0 | 待开发 |
| FR-004 | 自动填充公司信息到表格对应字段 | P0 | 待开发 |
| FR-005 | 保持原文档格式和样式 | P0 | 待开发 |
| FR-006 | 提供Web界面预览和修正 | P0 | 待开发 |
| FR-007 | 支持文档级资质图片智能插入（方案4） | P0 | 待开发 |
| FR-008 | 批量文档处理 | P1 | 待开发 |
| FR-009 | 字段匹配规则配置 | P1 | 待开发 |
| FR-010 | 处理历史记录和统计 | P2 | 待开发 |

#### 2.1.2 图片插入功能需求（方案4）

| 需求编号 | 需求描述 | 优先级 | 实现方式 |
|---------|---------|--------|----------|
| IMG-001 | 支持文本标记识别和替换 | P0 | 识别[营业执照]等标记 |
| IMG-002 | 支持段落占位符识别 | P0 | 识别独立占位符段落 |
| IMG-003 | 支持基于文档结构的智能插入 | P0 | 在特定章节后插入 |
| IMG-004 | 智能回退机制 | P0 | 多策略组合，确保插入成功 |
| IMG-005 | 上下文感知插入 | P1 | 根据上下文决定插入方式 |
| IMG-006 | 动态配置支持 | P1 | JSON配置文件控制行为 |
| IMG-007 | 插件式扩展机制 | P2 | 支持自定义插入策略 |

#### 2.1.3 集成需求

| 需求编号 | 需求描述 | 实现方式 |
|---------|---------|----------|
| IR-001 | 复用现有用户认证系统 | 使用现有Flask session |
| IR-002 | 读取现有公司配置 | 调用company_configs/*.json |
| IR-003 | 集成到现有Web界面 | 新增菜单项和页面 |
| IR-004 | 使用现有文件管理 | 复用uploads/outputs目录 |

### 2.2 非功能需求

#### 2.2.1 性能需求
- 单文档（<20页）处理时间：<30秒
- 并发处理能力：5个文档
- Web响应时间：<3秒
- 内存占用：<500MB/文档

#### 2.2.2 可靠性需求
- 字段识别准确率：>85%
- 系统可用性：>99%
- 异常恢复：自动重试机制
- 数据备份：处理结果自动备份

#### 2.2.3 安全性需求
- 文件上传校验（类型、大小）
- 临时文件自动清理
- 操作日志记录
- 用户权限控制

### 2.3 用户场景

#### 场景1：单个文档完整处理（表格+图片）
```
1. 用户上传包含表格和图片占位符的招标文档
2. 系统识别表格中的字段
3. 自动匹配并填充公司信息到表格
4. 系统识别文档中的图片插入位置（方案4智能识别）
5. 自动插入对应的资质图片（营业执照、证书等）
6. 用户预览表格填充和图片插入结果
7. 用户修正需要调整的内容
8. 下载完整的填写文档
```

#### 场景2：批量文档处理
```
1. 用户批量上传多个文档
2. 系统队列处理每个文档（表格+图片）
3. 显示处理进度和状态
4. 提供处理结果预览
5. 批量下载所有文档
```

#### 场景3：图片插入失败的智能处理
```
1. 系统尝试文本标记识别
2. 如失败，尝试段落占位符识别
3. 如失败，尝试基于文档结构插入
4. 如仍失败，在文档末尾附件区域插入
5. 记录插入位置供用户确认
```

---

## 3. 系统设计

### 3.1 架构设计

#### 3.1.1 模块架构
```
文档处理模块
├── 表格处理层
│   ├── TableExtractor (表格提取)
│   ├── CellAnalyzer (单元格分析)
│   └── LayoutDetector (布局检测)
├── 字段匹配层
│   ├── RuleMatcher (规则匹配)
│   ├── PatternMatcher (模式匹配)
│   └── ConfidenceCalculator (置信度计算)
├── 内容填充层
│   ├── TextFiller (表格文本填充)
│   ├── DateFormatter (日期格式化)
│   └── CurrencyFormatter (货币格式化)
├── 图片插入层（方案4）
│   ├── TextMarkerStrategy (文本标记策略)
│   ├── ParagraphStrategy (段落占位符策略)
│   ├── StructureStrategy (文档结构策略)
│   ├── FallbackStrategy (智能回退策略)
│   └── PluginManager (插件管理器)
└── 接口层
    ├── Web API (REST接口)
    └── UI Components (前端组件)
```

#### 3.1.2 数据流设计
```
用户上传 → 文档解析 → 并行处理 → 结果合并 → 输出文档
         ↓           ↓           ↓           ↓
      验证校验    结构提取   ┌─表格处理    合并结果
                             └─图片插入

表格处理流：表格识别 → 字段匹配 → 文本填充
图片插入流：位置识别 → 策略选择 → 图片插入
```

### 3.2 核心模块设计

#### 3.2.1 表格识别模块

```python
class TableProcessor:
    """表格处理核心类"""
    
    def __init__(self):
        self.extractor = TableExtractor()
        self.matcher = FieldMatcher()
        self.filler = ContentFiller()
    
    def process_document(self, doc_path, company_id):
        """处理文档主流程"""
        # 1. 提取表格
        tables = self.extractor.extract_tables(doc_path)
        
        # 2. 识别字段
        fields = self.matcher.match_fields(tables)
        
        # 3. 填充内容
        company_info = self.load_company_info(company_id)
        result = self.filler.fill_content(doc_path, fields, company_info)
        
        return result

class TableExtractor:
    """表格提取器"""
    
    def extract_tables(self, doc_path):
        """提取文档中的所有表格"""
        document = Document(doc_path)
        tables = []
        
        for table in document.tables:
            table_data = {
                'rows': [],
                'layout': self.detect_layout(table)
            }
            
            for row in table.rows:
                row_data = []
                for cell in row.cells:
                    row_data.append({
                        'text': cell.text.strip(),
                        'is_empty': not cell.text.strip(),
                        'has_underline': self.has_underline(cell),
                        'is_placeholder': self.is_placeholder(cell.text)
                    })
                table_data['rows'].append(row_data)
            
            tables.append(table_data)
        
        return tables
    
    def detect_layout(self, table):
        """检测表格布局类型"""
        # 分析表格结构，判断是水平、垂直还是混合布局
        pass
```

#### 3.2.2 字段匹配引擎

```python
class FieldMatcher:
    """字段匹配器"""
    
    def __init__(self):
        self.rules = self.load_matching_rules()
    
    def load_matching_rules(self):
        """加载字段匹配规则"""
        return {
            'company_name': {
                'keywords': ['公司名称', '企业名称', '单位名称', '投标人', '供应商'],
                'patterns': [r'.*公司.*名称', r'.*企业.*名称'],
                'priority': 1
            },
            'established_date': {
                'keywords': ['成立日期', '注册日期', '成立时间'],
                'patterns': [r'.*成立.*日期', r'.*注册.*时间'],
                'priority': 2
            },
            'business_scope': {
                'keywords': ['经营范围', '业务范围', '主营业务'],
                'patterns': [r'.*经营.*范围', r'.*业务.*范围'],
                'priority': 3
            },
            'registered_capital': {
                'keywords': ['注册资本', '注册资金', '资本金'],
                'patterns': [r'.*注册.*资本', r'.*注册.*资金'],
                'priority': 2
            },
            'legal_representative': {
                'keywords': ['法定代表人', '法人代表', '法人'],
                'patterns': [r'.*法.*代表人', r'.*法人.*'],
                'priority': 1
            },
            'contact_phone': {
                'keywords': ['联系电话', '电话', '联系方式', '手机'],
                'patterns': [r'.*联系.*电话', r'.*电话.*'],
                'priority': 2
            },
            'company_address': {
                'keywords': ['公司地址', '企业地址', '注册地址', '地址'],
                'patterns': [r'.*公司.*地址', r'.*注册.*地址'],
                'priority': 2
            },
            'business_license': {
                'keywords': ['营业执照', '营业执照号', '统一社会信用代码'],
                'patterns': [r'.*营业执照.*', r'.*信用代码.*'],
                'priority': 1,
                'type': 'image'  # 标记为图片类型
            }
        }
    
    def match_fields(self, tables):
        """匹配表格中的字段"""
        matched_fields = []
        
        for table in tables:
            for i, row in enumerate(table['rows']):
                for j, cell in enumerate(row):
                    if not cell['is_empty']:
                        # 尝试匹配字段
                        field_type = self.match_single_field(cell['text'])
                        if field_type:
                            # 找到对应的填写位置
                            target = self.find_target_cell(table, i, j)
                            if target:
                                matched_fields.append({
                                    'field_type': field_type,
                                    'label_position': (i, j),
                                    'target_position': target,
                                    'confidence': self.calculate_confidence(cell['text'], field_type)
                                })
        
        return matched_fields
    
    def match_single_field(self, text):
        """匹配单个字段"""
        text = text.strip().lower()
        
        for field_type, rule in self.rules.items():
            # 关键词匹配
            for keyword in rule['keywords']:
                if keyword.lower() in text:
                    return field_type
            
            # 模式匹配
            for pattern in rule['patterns']:
                if re.search(pattern, text, re.IGNORECASE):
                    return field_type
        
        return None
    
    def find_target_cell(self, table, row_idx, col_idx):
        """找到字段对应的填写单元格"""
        row = table['rows'][row_idx]
        
        # 检查右侧单元格（水平布局）
        if col_idx + 1 < len(row):
            right_cell = row[col_idx + 1]
            if right_cell['is_empty'] or right_cell['has_underline'] or right_cell['is_placeholder']:
                return (row_idx, col_idx + 1)
        
        # 检查下方单元格（垂直布局）
        if row_idx + 1 < len(table['rows']):
            below_cell = table['rows'][row_idx + 1][col_idx]
            if below_cell['is_empty'] or below_cell['has_underline'] or below_cell['is_placeholder']:
                return (row_idx + 1, col_idx)
        
        return None
```

#### 3.2.3 表格内容填充模块

```python
class ContentFiller:
    """内容填充器"""
    
    def fill_content(self, doc_path, matched_fields, company_info):
        """填充文档内容"""
        document = Document(doc_path)
        
        for field in matched_fields:
            content = self.get_content_for_field(field['field_type'], company_info)
            if content:
                self.fill_table_cell(
                    document,
                    field['target_position'],
                    content,
                    field['field_type']
                )
        
        # 保存结果
        output_path = self.generate_output_path(doc_path)
        document.save(output_path)
        
        return output_path
    
    def get_content_for_field(self, field_type, company_info):
        """根据字段类型获取填充内容"""
        field_mapping = {
            'company_name': company_info.get('companyName'),
            'established_date': self.format_date(company_info.get('establishDate')),
            'business_scope': company_info.get('businessScope'),
            'registered_capital': company_info.get('registeredCapital'),
            'legal_representative': company_info.get('legalRepresentative'),
            'contact_phone': company_info.get('contactPhone'),
            'company_address': company_info.get('companyAddress'),
            'business_license': company_info.get('qualifications', {}).get('business_license')
        }
        
        return field_mapping.get(field_type)
    
    def fill_table_cell(self, document, position, content, field_type):
        """填充表格单元格"""
        table_idx, row_idx, col_idx = position
        cell = document.tables[table_idx].rows[row_idx].cells[col_idx]
        
        if field_type in ['business_license', 'qualification_cert']:
            # 处理图片插入
            if content and os.path.exists(content):
                self.insert_image_to_cell(cell, content)
        else:
            # 处理文本填充
            cell.text = str(content) if content else ''
            # 保持原有格式
            if cell.paragraphs:
                self.preserve_formatting(cell.paragraphs[0])
```

#### 3.2.4 文档级图片插入模块（方案4）

```python
class SmartImageInserter:
    """智能图片插入器 - 方案4实现"""
    
    def __init__(self):
        # 三种策略组合
        self.strategies = [
            TextMarkerStrategy(),      # 策略1：文本标记
            ParagraphPlaceholderStrategy(),  # 策略2：段落占位符
            DocumentStructureStrategy()   # 策略3：文档结构
        ]
        
        # 策略优先级配置
        self.strategy_priority = {
            'text_marker': 1,        # 最高优先级
            'paragraph_placeholder': 2,
            'document_structure': 3   # 最低优先级
        }
        
        # 加载配置
        self.config = self.load_config()
    
    def insert_all_images(self, document, company_info):
        """灵活的图片插入主逻辑"""
        inserted_images = {}
        
        # 1. 按优先级尝试每种策略
        for strategy in self.get_ordered_strategies():
            if strategy.is_enabled():
                results = strategy.find_insertion_points(document)
                
                for result in results:
                    if not self.is_already_inserted(result.image_type, inserted_images):
                        success = strategy.insert_image(
                            document, 
                            result, 
                            company_info
                        )
                        if success:
                            inserted_images[result.image_type] = result
        
        # 2. 智能补充机制 - 确保必要图片都被插入
        self.smart_supplement(document, inserted_images, company_info)
        
        return document, inserted_images
    
    def smart_supplement(self, document, inserted_images, company_info):
        """智能补充未插入的必要图片"""
        required_images = self.config.get('required_images', ['business_license'])
        missing_images = set(required_images) - set(inserted_images.keys())
        
        if missing_images:
            # 在文档末尾添加附件区域
            self.append_missing_images(document, missing_images, company_info)

class TextMarkerStrategy:
    """文本标记策略 - 灵活的标记配置"""
    
    def find_insertion_points(self, document):
        """查找文本标记位置"""
        insertion_points = []
        
        # 支持多种标记格式
        markers = {
            'business_license': ['[营业执照]', '【营业执照】', '{营业执照}'],
            'qualification_cert': ['[资质证书]', '【资质证书】'],
            'legal_person_id': ['[法人身份证]', '【法人身份证】']
        }
        
        for paragraph in document.paragraphs:
            for image_type, marker_list in markers.items():
                for marker in marker_list:
                    if marker in paragraph.text:
                        insertion_points.append({
                            'paragraph': paragraph,
                            'image_type': image_type,
                            'marker': marker,
                            'strategy': 'text_marker'
                        })
        
        return insertion_points

class SmartFallbackHandler:
    """智能回退处理器"""
    
    def insert_with_fallback(self, document, image_type, company_info):
        """带回退的插入逻辑"""
        
        # 定义回退链
        fallback_chain = [
            self.try_exact_marker,      # 1. 尝试精确标记
            self.try_fuzzy_marker,       # 2. 尝试模糊匹配
            self.try_structure_based,    # 3. 尝试基于结构
            self.try_append_to_end       # 4. 最后添加到末尾
        ]
        
        for method in fallback_chain:
            try:
                result = method(document, image_type, company_info)
                if result:
                    return result
            except Exception as e:
                continue
        
        return None
```

### 3.3 Web接口设计

#### 3.3.1 API接口

```python
# 在web_app.py中添加新路由

@app.route('/table-fill')
def table_fill_page():
    """表格填充页面"""
    companies = load_all_companies()
    return render_template('table_fill.html', companies=companies)

@app.route('/api/table/upload', methods=['POST'])
def upload_table_document():
    """上传表格文档"""
    try:
        file = request.files['document']
        company_id = request.form.get('company_id')
        
        # 验证文件
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': '不支持的文件格式'})
        
        # 保存文件
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # 创建处理任务
        task_id = str(uuid.uuid4())
        
        # 异步处理
        thread = Thread(target=process_table_async, args=(task_id, filepath, company_id))
        thread.start()
        
        return jsonify({
            'success': True,
            'task_id': task_id,
            'message': '文档上传成功，正在处理...'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/table/status/<task_id>')
def get_table_status(task_id):
    """获取处理状态"""
    status = get_task_status(task_id)
    return jsonify(status)

@app.route('/api/table/preview/<task_id>')
def preview_table_result(task_id):
    """预览处理结果"""
    result = get_task_result(task_id)
    return jsonify(result)

@app.route('/api/table/download/<task_id>')
def download_table_result(task_id):
    """下载处理结果"""
    filepath = get_result_filepath(task_id)
    if filepath and os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    return jsonify({'error': '文件不存在'}), 404

def process_table_async(task_id, filepath, company_id):
    """异步处理表格"""
    try:
        # 更新状态
        update_task_status(task_id, 'processing', progress=10)
        
        # 处理文档
        processor = TableProcessor()
        result = processor.process_document(filepath, company_id)
        
        # 更新完成状态
        update_task_status(task_id, 'completed', progress=100, result=result)
        
    except Exception as e:
        update_task_status(task_id, 'failed', error=str(e))
```

#### 3.3.2 前端界面

```html
<!-- table_fill.html -->
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>表格自动填充 - AI标书平台</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-5">
        <h2>表格自动填充</h2>
        
        <!-- 公司选择 -->
        <div class="mb-3">
            <label for="companySelect" class="form-label">选择公司</label>
            <select class="form-select" id="companySelect">
                <option value="">请选择公司...</option>
                {% for company in companies %}
                <option value="{{ company.id }}">{{ company.name }}</option>
                {% endfor %}
            </select>
        </div>
        
        <!-- 文件上传 -->
        <div class="mb-3">
            <label for="fileUpload" class="form-label">上传文档</label>
            <div class="border rounded p-4 text-center" id="dropZone">
                <i class="bi bi-cloud-upload" style="font-size: 48px;"></i>
                <p>拖拽文件到此处或点击选择</p>
                <input type="file" id="fileUpload" class="d-none" accept=".doc,.docx">
            </div>
        </div>
        
        <!-- 处理进度 -->
        <div class="mb-3 d-none" id="progressSection">
            <div class="progress">
                <div class="progress-bar progress-bar-striped progress-bar-animated" 
                     role="progressbar" style="width: 0%"></div>
            </div>
            <p class="text-center mt-2" id="statusText">准备处理...</p>
        </div>
        
        <!-- 结果预览 -->
        <div class="mb-3 d-none" id="resultSection">
            <h4>处理结果</h4>
            <div class="table-responsive">
                <table class="table table-bordered" id="resultTable">
                    <thead>
                        <tr>
                            <th>字段名称</th>
                            <th>识别结果</th>
                            <th>填充内容</th>
                            <th>置信度</th>
                        </tr>
                    </thead>
                    <tbody></tbody>
                </table>
            </div>
            <div class="mt-3">
                <button class="btn btn-primary" id="downloadBtn">下载结果</button>
                <button class="btn btn-secondary" id="resetBtn">处理新文档</button>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="/static/js/table_fill.js"></script>
</body>
</html>
```

```javascript
// table_fill.js
class TableFillManager {
    constructor() {
        this.taskId = null;
        this.initEventListeners();
    }
    
    initEventListeners() {
        // 文件拖拽
        const dropZone = document.getElementById('dropZone');
        const fileInput = document.getElementById('fileUpload');
        
        dropZone.addEventListener('click', () => fileInput.click());
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('border-primary');
        });
        dropZone.addEventListener('dragleave', () => {
            dropZone.classList.remove('border-primary');
        });
        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('border-primary');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.handleFileUpload(files[0]);
            }
        });
        
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.handleFileUpload(e.target.files[0]);
            }
        });
        
        // 下载按钮
        document.getElementById('downloadBtn')?.addEventListener('click', () => {
            this.downloadResult();
        });
        
        // 重置按钮
        document.getElementById('resetBtn')?.addEventListener('click', () => {
            this.reset();
        });
    }
    
    async handleFileUpload(file) {
        const companyId = document.getElementById('companySelect').value;
        if (!companyId) {
            alert('请先选择公司');
            return;
        }
        
        const formData = new FormData();
        formData.append('document', file);
        formData.append('company_id', companyId);
        
        try {
            // 显示进度条
            this.showProgress();
            
            // 上传文件
            const response = await fetch('/api/table/upload', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            if (result.success) {
                this.taskId = result.task_id;
                this.checkStatus();
            } else {
                alert('上传失败：' + result.error);
                this.hideProgress();
            }
        } catch (error) {
            alert('上传错误：' + error.message);
            this.hideProgress();
        }
    }
    
    async checkStatus() {
        if (!this.taskId) return;
        
        try {
            const response = await fetch(`/api/table/status/${this.taskId}`);
            const status = await response.json();
            
            // 更新进度
            this.updateProgress(status.progress || 0);
            this.updateStatusText(status.message || '处理中...');
            
            if (status.status === 'completed') {
                // 显示结果
                this.showResult(status.result);
            } else if (status.status === 'failed') {
                alert('处理失败：' + status.error);
                this.hideProgress();
            } else {
                // 继续检查
                setTimeout(() => this.checkStatus(), 1000);
            }
        } catch (error) {
            console.error('状态检查错误：', error);
        }
    }
    
    showProgress() {
        document.getElementById('progressSection').classList.remove('d-none');
        document.getElementById('resultSection').classList.add('d-none');
    }
    
    hideProgress() {
        document.getElementById('progressSection').classList.add('d-none');
    }
    
    updateProgress(percent) {
        const progressBar = document.querySelector('.progress-bar');
        progressBar.style.width = percent + '%';
    }
    
    updateStatusText(text) {
        document.getElementById('statusText').textContent = text;
    }
    
    showResult(result) {
        this.hideProgress();
        
        const resultSection = document.getElementById('resultSection');
        const tbody = document.querySelector('#resultTable tbody');
        
        // 清空表格
        tbody.innerHTML = '';
        
        // 填充结果
        result.matched_fields?.forEach(field => {
            const row = tbody.insertRow();
            row.innerHTML = `
                <td>${field.field_name}</td>
                <td>${field.recognized_text}</td>
                <td>${field.filled_content}</td>
                <td>${(field.confidence * 100).toFixed(0)}%</td>
            `;
        });
        
        resultSection.classList.remove('d-none');
    }
    
    async downloadResult() {
        if (!this.taskId) return;
        
        window.location.href = `/api/table/download/${this.taskId}`;
    }
    
    reset() {
        this.taskId = null;
        document.getElementById('fileUpload').value = '';
        document.getElementById('companySelect').value = '';
        document.getElementById('resultSection').classList.add('d-none');
    }
}

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    new TableFillManager();
});
```

### 3.4 数据存储设计（JSON文件存储方案）

#### 3.4.1 配置文件结构

```json
// document_processing_config.json
{
    "table_processing": {
        "field_mappings": {
            "standard_fields": {
                "company_name": {
                    "keywords": ["公司名称", "企业名称", "单位名称"],
                    "patterns": [".*公司.*名称", ".*企业.*名称"],
                    "priority": 1
                }
            },
            "custom_fields": {},
            "industry_specific": {}
        },
        "processing_rules": {
            "date_formats": ["YYYY-MM-DD", "YYYY年MM月DD日"],
            "currency_formats": ["￥#,###.##", "人民币#,###.##元"]
        }
    },
    "image_insertion": {
        "methods": {
            "text_markers": {
                "enabled": true,
                "priority": 1,
                "markers": {
                    "营业执照": ["[营业执照]", "【营业执照】", "{营业执照}"],
                    "资质证书": ["[资质证书]", "【资质证书】"],
                    "法人身份证": ["[法人身份证]", "【法人身份证】"]
                }
            },
            "paragraph_placeholders": {
                "enabled": true,
                "priority": 2,
                "placeholders": ["营业执照附件", "资质证书附件", "此处插入营业执照"]
            },
            "structure_based": {
                "enabled": true,
                "priority": 3,
                "after_sections": {
                    "公司资质": ["business_license", "qualification_cert"],
                    "附件": ["business_license", "qualification_cert", "legal_person_id"]
                }
            }
        },
        "fallback_strategy": {
            "enabled": true,
            "append_to_end": true,
            "create_appendix_section": true
        },
        "image_settings": {
            "default_width_inches": 4,
            "max_width_inches": 5,
            "quality": 85,
            "formats": ["jpg", "jpeg", "png", "gif"],
            "center_align": true,
            "add_captions": true
        },
        "required_images": ["business_license"],
        "optional_images": ["qualification_cert", "legal_person_id"]
    }
}
```

#### 3.4.2 处理历史存储

```json
// processing_history.json
{
    "tasks": [
        {
            "task_id": "uuid",
            "user_id": "user_id",
            "company_id": "company_id",
            "filename": "tender_form.docx",
            "status": "completed",
            "created_at": "2024-01-01T10:00:00",
            "completed_at": "2024-01-01T10:00:30",
            "statistics": {
                "tables_found": 3,
                "fields_matched": 15,
                "fields_filled": 14,
                "accuracy": 0.93
            }
        }
    ]
}
```

### 3.5 错误处理与日志

#### 3.5.1 异常处理策略

```python
class TableProcessingError(Exception):
    """表格处理基础异常"""
    pass

class DocumentParsingError(TableProcessingError):
    """文档解析异常"""
    pass

class FieldMatchingError(TableProcessingError):
    """字段匹配异常"""
    pass

class ContentFillingError(TableProcessingError):
    """内容填充异常"""
    pass

def handle_processing_error(func):
    """错误处理装饰器"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except DocumentParsingError as e:
            logger.error(f"文档解析错误: {e}")
            return {'success': False, 'error': '文档格式不正确或已损坏'}
        except FieldMatchingError as e:
            logger.error(f"字段匹配错误: {e}")
            return {'success': False, 'error': '无法识别表格字段'}
        except ContentFillingError as e:
            logger.error(f"内容填充错误: {e}")
            return {'success': False, 'error': '填充内容时发生错误'}
        except Exception as e:
            logger.exception(f"未知错误: {e}")
            return {'success': False, 'error': '处理失败，请联系技术支持'}
    return wrapper
```

#### 3.5.2 日志记录

```python
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('table_processing.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('TableProcessor')

class ProcessingLogger:
    """处理日志记录器"""
    
    @staticmethod
    def log_task_start(task_id, filename, company_id):
        logger.info(f"开始处理任务 {task_id}: 文件={filename}, 公司={company_id}")
    
    @staticmethod
    def log_field_matched(task_id, field_type, confidence):
        logger.debug(f"任务 {task_id}: 匹配字段 {field_type}, 置信度={confidence:.2f}")
    
    @staticmethod
    def log_task_complete(task_id, duration, stats):
        logger.info(f"任务 {task_id} 完成: 耗时={duration}s, 统计={stats}")
    
    @staticmethod
    def log_task_error(task_id, error):
        logger.error(f"任务 {task_id} 失败: {error}")
```

---

## 4. 实施计划

### 4.1 分阶段迭代开发计划

#### 第一阶段：表格处理基础（2周）
- [ ] 文档解析模块开发
- [ ] 表格识别算法实现
- [ ] 基于规则的字段匹配
- [ ] 表格文本填充功能
- [ ] JSON配置文件结构设计

#### 第二阶段：图片插入方案4实现（2周）
- [ ] 文本标记策略实现
- [ ] 段落占位符策略实现
- [ ] 文档结构策略实现
- [ ] 智能回退机制开发
- [ ] 动态配置系统集成

#### 第三阶段：功能完善与集成（1周）
- [ ] Web界面集成
- [ ] 批量处理支持
- [ ] 用户修正界面
- [ ] 处理结果预览
- [ ] 上下文感知优化

#### 第四阶段：测试与优化（1周）
- [ ] 单元测试编写
- [ ] 集成测试执行
- [ ] 性能优化
- [ ] 文档编写
- [ ] 部署上线

### 4.2 测试计划

#### 4.2.1 单元测试
```python
# test_table_processor.py
import unittest
from table_processor import TableProcessor, FieldMatcher

class TestTableProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = TableProcessor()
        
    def test_extract_tables(self):
        """测试表格提取"""
        tables = self.processor.extractor.extract_tables('test_doc.docx')
        self.assertGreater(len(tables), 0)
    
    def test_field_matching(self):
        """测试字段匹配"""
        matcher = FieldMatcher()
        result = matcher.match_single_field('公司名称')
        self.assertEqual(result, 'company_name')
    
    def test_content_filling(self):
        """测试内容填充"""
        # ... 测试代码
        pass

if __name__ == '__main__':
    unittest.main()
```

#### 4.2.2 集成测试
- 端到端流程测试
- 不同文档格式测试
- 批量处理测试
- 异常情况测试

#### 4.2.3 性能测试
- 单文档处理时间测试
- 并发处理能力测试
- 内存占用测试
- 大文件处理测试

### 4.3 部署计划

#### 4.3.1 部署准备
```bash
# 安装依赖
pip install python-docx
pip install pillow
pip install python-magic

# 创建必要目录
mkdir -p uploads/tables
mkdir -p outputs/tables
mkdir -p logs
```

#### 4.3.2 配置更新
```python
# 在config.py中添加
TABLE_FILL_CONFIG = {
    'MAX_FILE_SIZE': 20 * 1024 * 1024,  # 20MB
    'ALLOWED_EXTENSIONS': ['.doc', '.docx'],
    'PROCESSING_TIMEOUT': 60,  # 秒
    'MAX_CONCURRENT_TASKS': 5
}
```

---

## 5. 风险管理

### 5.1 技术风险

| 风险项 | 概率 | 影响 | 缓解措施 |
|--------|------|------|----------|
| 复杂表格识别失败 | 中 | 高 | 提供手动标注功能 |
| 字段匹配准确率低 | 中 | 中 | 持续优化规则库 |
| 图片插入位置识别失败 | 中 | 中 | 方案4多策略回退机制 |
| 图片格式兼容性 | 低 | 中 | 多版本Word测试 |
| 性能瓶颈 | 低 | 低 | 使用任务队列 |

### 5.2 业务风险

| 风险项 | 概率 | 影响 | 缓解措施 |
|--------|------|------|----------|
| 用户接受度低 | 低 | 中 | 用户培训和引导 |
| 数据安全问题 | 低 | 高 | 加密存储和传输 |
| 法律合规风险 | 低 | 高 | 审查合规要求 |

---

## 6. 验收标准

### 6.1 功能验收

- ✅ 成功识别90%以上的标准表格布局
- ✅ 字段匹配准确率达到85%以上
- ✅ 保持原文档格式100%不变
- ✅ 支持批量处理至少5个文档
- ✅ 图片插入成功率95%以上（方案4多策略保障）
- ✅ 智能回退机制100%确保图片插入

### 6.2 性能验收

- ✅ 单文档处理时间<30秒（20页以内）
- ✅ Web响应时间<3秒
- ✅ 内存占用<500MB/文档
- ✅ 系统稳定运行72小时无故障

### 6.3 用户体验验收

- ✅ 界面风格与现有系统一致
- ✅ 操作流程简洁直观
- ✅ 错误提示清晰明确
- ✅ 提供完整的使用文档

### 6.4 集成验收

- ✅ 与现有系统无缝集成
- ✅ 正确读取公司配置信息（JSON文件）
- ✅ 用户权限控制有效
- ✅ 不影响现有功能性能
- ✅ 配置文件热更新支持

---

## 附录

### A. 字段映射规则表

| 字段类型 | 中文名称 | 关键词列表 | 优先级 |
|----------|----------|------------|--------|
| company_name | 公司名称 | 公司名称、企业名称、单位名称、投标人 | 1 |
| established_date | 成立日期 | 成立日期、注册日期、成立时间 | 2 |
| business_scope | 经营范围 | 经营范围、业务范围、主营业务 | 3 |
| registered_capital | 注册资本 | 注册资本、注册资金、资本金 | 2 |
| legal_representative | 法定代表人 | 法定代表人、法人代表、法人 | 1 |
| contact_phone | 联系电话 | 联系电话、电话、手机、联系方式 | 2 |
| company_address | 公司地址 | 公司地址、注册地址、地址 | 2 |
| business_license | 营业执照 | 营业执照、执照、统一社会信用代码 | 1 |

### B. 常见表格布局模式

1. **水平布局**
   ```
   | 公司名称 | _________ | 成立日期 | _________ |
   | 注册资本 | _________ | 法人代表 | _________ |
   ```

2. **垂直布局**
   ```
   | 公司名称 |
   | _________ |
   | 成立日期 |
   | _________ |
   ```

3. **混合布局**
   ```
   | 基本信息 |          |          |
   | 公司名称 | ________ | 成立日期 | ________ |
   | 经营范围 |          |
   | ________ |          |
   ```

### C. 错误代码对照表

| 错误代码 | 错误描述 | 解决方案 |
|----------|----------|----------|
| E001 | 文档格式不支持 | 使用DOC/DOCX格式 |
| E002 | 文档已损坏 | 重新保存文档 |
| E003 | 未找到表格 | 检查文档内容 |
| E004 | 字段匹配失败 | 手动指定字段 |
| E005 | 公司信息不完整 | 补充公司配置 |
| E006 | 图片格式不支持 | 使用JPG/PNG格式 |
| E007 | 处理超时 | 减小文档大小 |
| E008 | 图片插入位置未找到 | 方案4自动回退到附件区 |
| E009 | 配置文件读取失败 | 检查JSON文件格式 |

---

### D. 图片插入策略优先级（方案4）

| 优先级 | 策略名称 | 识别方式 | 适用场景 |
|---------|----------|----------|----------|
| 1 | 文本标记策略 | 识别[营业执照]等标记 | 明确标记的文档 |
| 2 | 段落占位符策略 | 识别独立占位符段落 | 专门留空的位置 |
| 3 | 文档结构策略 | 在特定章节后插入 | 标准格式文档 |
| 4 | 智能回退 | 自动附加到文末 | 保底策略 |

### E. 配置文件说明

| 配置文件 | 用途 | 格式 |
|---------|------|------|
| document_processing_config.json | 主配置文件 | JSON |
| company_configs/*.json | 公司信息配置 | JSON |
| processing_history.json | 处理历史记录 | JSON |
| field_mapping_rules.json | 字段映射规则 | JSON |

---

**文档版本**: 2.0
**创建日期**: 2024-12-09
**最后更新**: 2024-12-09
**更新内容**: 
- 添加文档级图片插入方案4
- 更新为JSON文件存储方案
- 优化分阶段迭代开发计划
**作者**: AI标书平台开发团队