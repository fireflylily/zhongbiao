    PROJECT_INFO_SCHEMA = {
        "name": "项目名称",
        "description": "项目描述",
        "budget": "项目预算",
        "duration": "项目周期",
        "location": "项目地址",
        "requirements": "项目要求"
    }
    
    QUALIFICATION_IMAGES_SCHEMA = {
        "business_license": {
            "path": "营业执照图片路径",
            "caption": "营业执照标题",
            "max_width": 500,
            "max_height": 400
        },
        "legal_person_id": {
            "path": "法人身份证图片路径", 
            "caption": "法人身份证标题",
            "max_width": 400,
            "max_height": 250
        },
        "iso9001": {
            "path": "ISO9001证书路径",
            "caption": "ISO9001认证证书",
            "max_width": 450,
            "max_height": 350
        },
        "iso14001": {
            "path": "ISO14001证书路径",
            "caption": "ISO14001认证证书", 
            "max_width": 450,
            "max_height": 350
        },
        "iso45001": {
            "path": "ISO45001证书路径",
            "caption": "ISO45001认证证书",
            # DOC/DOCX表格自动填充功能设计文档（更新版）

## 1. 系统架构设计

### 1.1 整体架构
基于现有AI标书平台的架构，采用模块化扩展设计：

```
现有AI标书平台架构
├── Web前端层 (已有)
│   ├── 用户界面
│   ├── AI标书生成界面
│   └── 表格处理界面 (新增)
├── 业务逻辑层 (扩展)
│   ├── 用户管理 (已有)
│   ├── AI文本生成 (已有)
│   ├── 表格处理引擎 (新增)
│   └── 配置管理 (已有)
├── 数据处理层 (扩展)
│   ├── 文档解析模块 (新增)
│   ├── 字段匹配引擎 (新增)
│   └── 内容填充引擎 (新增)
└── 数据存储层 (已有)
    ├── 用户数据
    ├── 配置文件
    └── 处理历史 (新增)
```

### 1.2 核心模块设计

#### 1.2.1 平台集成层 (Platform Integration Layer)
- **功能**：与现有AI标书平台无缝集成
- **职责**：
  - 复用现有用户认证和权限管理
  - 读取现有配置文件（公司信息、项目信息）
  - 集成现有文件管理系统
  - 保持界面风格一致性

#### 1.2.2 表格处理引擎 (Table Processing Engine)
- **功能**：核心业务逻辑处理
- **职责**：
  - 协调各子模块工作
  - 处理业务流程控制
  - 提供统一的API接口
  - 管理处理状态和进度

#### 1.2.3 文档解析模块 (Document Parser Module)
- **功能**：解析DOC/DOCX文档，提取表格结构
- **输入**：用户上传的DOC/DOCX文件
- **输出**：结构化的表格数据对象

#### 1.2.4 字段匹配引擎 (Field Matching Engine)
- **功能**：基于规则的智能字段匹配
- **输入**：表格结构数据、字段匹配规则库
- **输出**：字段匹配结果和置信度

#### 1.2.5 内容填充引擎 (Content Filling Engine)
- **功能**：将配置信息填入文档
- **输入**：原文档、匹配结果、配置数据
- **输出**：填写完成的文档

## 2. 详细模块设计

### 2.1 平台集成层设计

#### 2.1.1 配置读取适配器
```python
class ConfigurationAdapter:
    """适配现有平台的配置系统"""
    
    def __init__(self, existing_config_manager):
        self.config_manager = existing_config_manager
    
    def get_company_info(self, user_id):
        """读取公司信息配置"""
        return self.config_manager.load_company_profile(user_id)
    
    def get_project_info(self, project_id):
        """读取项目信息配置"""
        return self.config_manager.load_project_settings(project_id)
    
    def get_field_mapping_rules(self):
        """获取字段映射规则"""
        return self.config_manager.load_field_rules()
```

#### 2.1.2 用户认证集成
```python
class AuthenticationIntegrator:
    """集成现有用户认证系统"""
    
    def __init__(self, existing_auth_service):
        self.auth_service = existing_auth_service
    
    def verify_user_permission(self, user_id, action):
        """验证用户权限"""
        return self.auth_service.check_permission(user_id, action)
    
    def get_user_context(self, session):
        """获取用户上下文"""
        return self.auth_service.get_user_info(session)
```

### 2.2 文档解析模块设计

#### 2.2.1 核心解析类
```python
class DocumentParser:
    """文档解析主类"""
    
    def __init__(self):
        self.docx_parser = DOCXParser()
        self.doc_parser = DOCParser()  # 如需支持老格式
    
    def parse_document(self, file_path, file_type):
        """解析文档主入口"""
        if file_type == 'docx':
            return self.docx_parser.parse(file_path)
        elif file_type == 'doc':
            return self.doc_parser.parse(file_path)
        else:
            raise UnsupportedFormatError(f"不支持的文件格式: {file_type}")

class DOCXParser:
    """DOCX格式解析器"""
    
    def parse(self, file_path):
        """解析DOCX文档"""
        document = Document(file_path)
        tables = []
        
        for table in document.tables:
            table_data = self.extract_table_structure(table)
            tables.append(table_data)
        
        return DocumentStructure(
            tables=tables,
            metadata=self.extract_metadata(document)
        )
    
    def extract_table_structure(self, table):
        """提取表格结构"""
        rows = []
        for i, row in enumerate(table.rows):
            cells = []
            for j, cell in enumerate(row.cells):
                cell_data = TableCell(
                    content=cell.text.strip(),
                    row_index=i,
                    col_index=j,
                    is_empty=not cell.text.strip(),
                    format_info=self.extract_cell_format(cell)
                )
                cells.append(cell_data)
            rows.append(TableRow(cells=cells, row_index=i))
        
        return TableStructure(
            rows=rows,
            row_count=len(rows),
            col_count=len(rows[0].cells) if rows else 0
        )
```

#### 2.2.2 数据结构定义
```python
@dataclass
class DocumentStructure:
    """文档结构"""
    tables: List[TableStructure]
    metadata: Dict[str, Any]

@dataclass
class TableStructure:
    """表格结构"""
    rows: List[TableRow]
    row_count: int
    col_count: int
    table_id: str = None

@dataclass
class TableRow:
    """表格行"""
    cells: List[TableCell]
    row_index: int

@dataclass
class TableCell:
    """表格单元格"""
    content: str
    row_index: int
    col_index: int
    is_empty: bool
    format_info: Dict[str, Any]
    row_span: int = 1
    col_span: int = 1
```

### 2.3 字段匹配引擎设计

#### 2.3.1 基于规则的匹配策略
```python
class RuleBasedMatcher:
    """基于规则的字段匹配器"""
    
    def __init__(self):
        self.field_rules = self.load_field_mapping_rules()
        self.semantic_calculator = SemanticSimilarityCalculator()
    
    def match_fields(self, table_structure):
        """匹配表格中的字段"""
        matches = []
        
        for row in table_structure.rows:
            for cell in row.cells:
                if not cell.is_empty and self.is_potential_label(cell):
                    match_result = self.match_single_field(cell, table_structure)
                    if match_result:
                        matches.append(match_result)
        
        return matches
    
    def match_single_field(self, label_cell, table_structure):
        """匹配单个字段"""
        # 1. 精确匹配
        exact_match = self.exact_match(label_cell.content)
        if exact_match.confidence > 0.9:
            return exact_match
        
        # 2. 关键词匹配
        keyword_match = self.keyword_match(label_cell.content)
        if keyword_match.confidence > 0.7:
            return keyword_match
        
        # 3. 语义相似度匹配
        semantic_match = self.semantic_match(label_cell.content)
        if semantic_match.confidence > 0.6:
            return semantic_match
        
        return None
    
    def find_corresponding_input_cell(self, label_cell, table_structure):
        """找到对应的输入单元格"""
        # 水平布局：右侧单元格
        if label_cell.col_index < table_structure.col_count - 1:
            right_cell = table_structure.rows[label_cell.row_index].cells[label_cell.col_index + 1]
            if right_cell.is_empty or self.is_placeholder(right_cell.content):
                return right_cell
        
        # 垂直布局：下方单元格
        if label_cell.row_index < table_structure.row_count - 1:
            below_cell = table_structure.rows[label_cell.row_index + 1].cells[label_cell.col_index]
            if below_cell.is_empty or self.is_placeholder(below_cell.content):
                return below_cell
        
        return None
```

#### 2.3.2 字段映射规则库
```python
class FieldMappingRules:
    """字段映射规则库"""
    
    COMPANY_INFO_FIELDS = {
        "company_name": {
            "keywords": ["公司名称", "企业名称", "单位名称", "投标人名称", "投标单位"],
            "aliases": ["公司", "企业", "单位", "投标人"],
            "patterns": [r".*公司.*名称.*", r".*企业.*名称.*"],
            "priority": 1
        },
        "established_date": {
            "keywords": ["成立日期", "注册日期", "成立时间", "注册时间", "成立年月"],
            "aliases": ["成立", "注册", "创建"],
            "patterns": [r".*成立.*日期.*", r".*注册.*日期.*"],
            "priority": 2
        },
        "business_scope": {
            "keywords": ["经营范围", "业务范围", "主营业务", "营业范围"],
            "aliases": ["经营", "业务", "主营"],
            "patterns": [r".*经营.*范围.*", r".*业务.*范围.*"],
            "priority": 3
        },
        "registered_address": {
            "keywords": ["注册地址", "公司地址", "企业地址", "注册住所"],
            "aliases": ["地址", "住所", "所在地"],
            "patterns": [r".*注册.*地址.*", r".*公司.*地址.*"],
            "priority": 2
        }
        # ... 更多字段定义
    }
    
    PROJECT_INFO_FIELDS = {
        "project_name": {
            "keywords": ["项目名称", "工程名称", "标的名称", "采购项目"],
            "aliases": ["项目", "工程", "标的"],
            "patterns": [r".*项目.*名称.*", r".*工程.*名称.*"],
            "priority": 1
        }
        # ... 更多项目字段
    }
```

### 2.4 内容填充引擎设计

#### 2.4.1 填充策略管理器
```python
class ContentFillingEngine:
    """内容填充引擎"""
    
    def __init__(self, config_adapter):
        self.config_adapter = config_adapter
        self.formatters = {
            'text': TextFormatter(),
            'date': DateFormatter(),
            'currency': CurrencyFormatter(),
            'multiline': MultilineTextFormatter()
        }
    
    def fill_document(self, document_path, match_results, user_id, project_id=None):
        """填充文档内容"""
        # 1. 获取配置数据
        company_info = self.config_adapter.get_company_info(user_id)
        project_info = self.config_adapter.get_project_info(project_id) if project_id else {}
        
        # 2. 加载原文档
        document = Document(document_path)
        
        # 3. 执行填充
        for match in match_results:
            content = self.get_fill_content(match.field_type, company_info, project_info)
            formatted_content = self.format_content(content, match.format_type)
            self.fill_cell(document, match.target_cell, formatted_content)
        
        # 4. 保存结果
        output_path = self.generate_output_path(document_path, user_id)
        document.save(output_path)
        
        return output_path
    
    def get_fill_content(self, field_type, company_info, project_info):
        """根据字段类型获取填充内容"""
        field_mapping = {
            'company_name': company_info.get('name'),
            'established_date': company_info.get('established_date'),
            'business_scope': company_info.get('business_scope'),
            'registered_address': company_info.get('address'),
            'project_name': project_info.get('name'),
            # ... 更多字段映射
        }
        
        return field_mapping.get(field_type, '')
```

#### 2.4.2 格式化处理器
```python
class DateFormatter:
    """日期格式化器"""
    
    def format(self, date_value, target_format=None):
        """格式化日期"""
        if not date_value:
            return ""
        
        if isinstance(date_value, str):
            date_obj = self.parse_date_string(date_value)
        else:
            date_obj = date_value
        
        # 自动检测目标格式或使用默认格式
        if not target_format:
            target_format = "%Y年%m月%d日"
        
        return date_obj.strftime(target_format)

class MultilineTextFormatter:
    """多行文本格式化器"""
    
    def format(self, text, max_width=None):
        """格式化多行文本"""
        if not text:
            return ""
        
        # 处理换行和段落
        paragraphs = text.split('\n')
        formatted_paragraphs = []
        
        for paragraph in paragraphs:
            if max_width and len(paragraph) > max_width:
                wrapped = self.wrap_text(paragraph, max_width)
                formatted_paragraphs.extend(wrapped)
            else:
                formatted_paragraphs.append(paragraph)
        
        return '\n'.join(formatted_paragraphs)
```

### 2.5 Web界面集成设计

#### 2.5.1 前端组件设计
```javascript
// 表格处理主组件
class TableProcessingComponent {
    constructor() {
        this.fileUploader = new FileUploader();
        this.progressTracker = new ProgressTracker();
        this.resultViewer = new ResultViewer();
    }
    
    async processDocument(file) {
        // 1. 上传文档
        const uploadResult = await this.fileUploader.upload(file);
        
        // 2. 开始处理
        const taskId = await this.startProcessing(uploadResult.fileId);
        
        // 3. 跟踪进度
        this.progressTracker.track(taskId, (progress) => {
            this.updateUI(progress);
        });
        
        // 4. 显示结果
        const result = await this.waitForResult(taskId);
        this.resultViewer.display(result);
    }
}

// 结果预览组件
class ResultViewer {
    display(processingResult) {
        // 显示识别到的字段
        this.renderRecognizedFields(processingResult.matches);
        
        // 显示预览
        this.renderPreview(processingResult.preview);
        
        // 提供修正功能
        this.enableEditing(processingResult);
    }
    
    enableEditing(result) {
        // 允许用户修正识别结果
        result.matches.forEach(match => {
            this.createEditableField(match);
        });
    }
}
```

#### 2.5.2 API接口设计
```python
# Flask路由设计
@app.route('/api/table/upload', methods=['POST'])
@require_auth
def upload_document():
    """文档上传接口"""
    try:
        file = request.files['document']
        user_id = get_current_user_id()
        
        # 保存文件
        file_path = save_uploaded_file(file, user_id)
        
        # 创建处理任务
        task_id = table_processor.create_task(file_path, user_id)
        
        return jsonify({
            'success': True,
            'task_id': task_id,
            'message': '文档上传成功'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/table/process/<task_id>', methods=['POST'])
@require_auth
def start_processing(task_id):
    """开始处理文档"""
    try:
        user_id = get_current_user_id()
        project_id = request.json.get('project_id')
        
        # 异步处理
        result = table_processor.process_async(task_id, user_id, project_id)
        
        return jsonify({
            'success': True,
            'status': 'processing',
            'estimated_time': result.estimated_time
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/table/status/<task_id>')
@require_auth
def get_processing_status(task_id):
    """获取处理状态"""
    status = table_processor.get_task_status(task_id)
    return jsonify(status)

@app.route('/api/table/result/<task_id>')
@require_auth
def get_result(task_id):
    """获取处理结果"""
    result = table_processor.get_task_result(task_id)
    return jsonify(result)

@app.route('/api/table/download/<task_id>')
@require_auth
def download_result(task_id):
    """下载处理结果"""
    file_path = table_processor.get_result_file(task_id)
    return send_file(file_path, as_attachment=True)
```

## 3. 数据库设计

### 3.1 新增数据表

#### 3.1.1 字段映射规则表
```sql
CREATE TABLE field_mapping_rules (
    id INT PRIMARY KEY AUTO_INCREMENT,
    field_type VARCHAR(50) NOT NULL,
    field_name VARCHAR(100) NOT NULL,
    keywords TEXT,
    aliases TEXT,
    regex_patterns TEXT,
    priority INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

#### 3.1.2 处理任务表
```sql
CREATE TABLE processing_tasks (
    id VARCHAR(36) PRIMARY KEY,
    user_id INT NOT NULL,
    project_id INT,
    original_filename VARCHAR(255),
    file_path VARCHAR(500),
    status ENUM('pending', 'processing', 'completed', 'failed') DEFAULT 'pending',
    progress INT DEFAULT 0,
    result_data JSON,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

#### 3.1.3 字段匹配历史表
```sql
CREATE TABLE field_match_history (
    id INT PRIMARY KEY AUTO_INCREMENT,
    task_id VARCHAR(36) NOT NULL,
    field_text VARCHAR(200),
    matched_type VARCHAR(50),
    confidence DECIMAL(3,2),
    is_correct BOOLEAN,
    user_correction VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES processing_tasks(id)
);
```

### 3.2 配置数据结构

#### 3.2.1 现有配置读取适配
```python
class ConfigurationSchema:
    """配置数据结构定义"""
    
    COMPANY_INFO_SCHEMA = {
        "name": "公司名称",
        "established_date": "成立日期",
        "registered_address": "注册地址",
        "business_scope": "经营范围",
        "registered_capital": "注册资本",
        "contact_info": {
            "phone": "联系电话",
            "email": "邮箱地址",
            "fax": "传真号码",
            "contact_person": "联系人"
        },
        "qualifications": [
            {
                "name": "资质名称",
                "certificate_no": "证书编号",
                "validity_period": "有效期"
            }
        ]
    }
    
    PROJECT_INFO_SCHEMA = {
        "name": "项目名称",
        "description": "项目描述",
        "budget": "项目预算",
        "duration": "项目周期",
        "location": "项目地址",
        "requirements": "项目要求"
    }
```

## 4. 异常处理设计

### 4.1 异常分类和处理策略

#### 4.1.1 文档处理异常
```python
class DocumentProcessingExceptionHandler:
    """文档处理异常处理器"""
    
    def handle_document_exception(self, exception, file_path):
        """处理文档相关异常"""
        if isinstance(exception, CorruptedDocumentError):
            return ProcessingResult.error("文档已损坏，请检查文件完整性")
        
        elif isinstance(exception, UnsupportedFormatError):
            return ProcessingResult.error("不支持的文档格式")
        
        elif isinstance(exception, PasswordProtectedError):
            return ProcessingResult.error("文档受密码保护，请提供密码")
        
        elif isinstance(exception, EmptyDocumentError):
            return ProcessingResult.warning("文档中未发现表格内容")
        
        else:
            logger.error(f"未知文档处理错误: {str(exception)}")
            return ProcessingResult.error("文档处理失败，请联系技术支持")
```

#### 4.1.2 业务逻辑异常
```python
class BusinessLogicExceptionHandler:
    """业务逻辑异常处理器"""
    
    def handle_matching_exception(self, exception, context):
        """处理字段匹配异常"""
        if isinstance(exception, NoFieldsMatchedError):
            return {
                'status': 'warning',
                'message': '未识别到可填写的字段，请检查表格格式',
                'suggestions': ['确认表格包含标准字段名称', '尝试手动标注字段']
            }
        
        elif isinstance(exception, ConfigurationMissingError):
            return {
                'status': 'error',
                'message': '公司信息配置不完整',
                'required_fields': exception.missing_fields
            }
```

## 5. 性能优化设计

### 5.1 处理性能优化

#### 5.1.1 异步处理机制
```python
class AsyncTableProcessor:
    """异步表格处理器"""
    
    def __init__(self):
        self.task_queue = Queue()
        self.worker_pool = ThreadPoolExecutor(max_workers=4)
        self.cache = LRUCache(maxsize=100)
    
    async def process_document_async(self, task_id, file_path, user_config):
        """异步处理文档"""
        # 提交到工作线程池
        future = self.worker_pool.submit(
            self._process_document_sync, 
            task_id, file_path, user_config
        )
        
        # 更新任务状态
        self.update_task_status(task_id, 'processing')
        
        try:
            result = await asyncio.wrap_future(future, timeout=300)
            self.update_task_status(task_id, 'completed', result)
            return result
        except TimeoutError:
            self.update_task_status(task_id, 'failed', '处理超时')
            raise ProcessingTimeoutError("文档处理超时")
```

#### 5.1.2 缓存策略
```python
class IntelligentCache:
    """智能缓存管理器"""
    
    def __init__(self):
        self.field_rule_cache = TTLCache(maxsize=1000, ttl=3600)
        self.document_structure_cache = LRUCache(maxsize=50)
        self.user_config_cache = TTLCache(maxsize=500, ttl=1800)
    
    def get_field_rules(self):
        """获取字段规则（带缓存）"""
        cache_key = "field_mapping_rules"
        rules = self.field_rule_cache.get(cache_key)
        
        if rules is None:
            rules = self.load_rules_from_database()
            self.field_rule_cache[cache_key] = rules
        
        return rules
    
    def cache_document_structure(self, file_hash, structure):
        """缓存文档结构"""
        self.document_structure_cache[file_hash] = structure
```

## 6. 安全性设计

### 6.1 数据安全

#### 6.1.1 文件安全处理
```python
class SecureFileHandler:
    """安全文件处理器"""
    
    def __init__(self, encryption_key):
        self.encryption_key = encryption_key
        self.allowed_extensions = {'.docx', '.doc'}
        self.max_file_size = 50 * 1024 * 1024  # 50MB
    
    def validate_and_store_file(self, uploaded_file, user_id):
        """验证并安全存储文件"""
        # 1. 文件类型验证
        if not self.is_valid_file_type(uploaded_file.filename):
            raise InvalidFileTypeError("不支持的文件类型")
        
        # 2. 文件大小验证
        if uploaded_file.content_length > self.max_file_size:
            raise FileSizeExceededError("文件大小超出限制")
        
        # 3. 病毒扫描
        if not self.scan_for_malware(uploaded_file):
            raise MalwareDetectedError("检测到恶意文件")
        
        # 4. 加密存储
        secure_path = self.encrypt_and_store(uploaded_file, user_id)
        
        return secure_path
    
    def cleanup_temp_files(self, task_id):
        """清理临时文件"""
        temp_dir = os.path.join(TEMP_DIR, task_id)
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
```

#### 6.1.2 访问控制
```python
class AccessController:
    """访问控制器"""
    
    def __init__(self, auth_service):
        self.auth_service = auth_service
    
    def check_document_access(self, user_id, task_id):
        """检查用户对文档的访问权限"""
        task = self.get_task_by_id(task_id)
        
        if not task:
            raise TaskNotFoundError("任务不存在")
        
        if task.user_id != user_id:
            raise AccessDeniedError("无权访问此任务")
        
        return True
    
    def check_configuration_access(self, user_id, config_type):
        """检查配置访问权限"""
        return self.auth_service.has_permission(user_id, f"config:{config_type}")
```

## 7. 监控和日志设计

### 7.1 操作日志记录

#### 7.1.1 详细日志记录
```python
class DetailedLogger:
    """详细日志记录器"""
    
    def __init__(self):
        self.logger = logging.getLogger('table_processing')
        self.performance_logger = logging.getLogger('performance')
    
    def log_processing_start(self, task_id, user_id, file_info):
        """记录处理开始"""
        self.logger.info(
            f"开始处理任务 {task_id}",
            extra={
                'user_id': user_id,
                'filename': file_info['name'],
                'filesize': file_info['size'],
                'timestamp': datetime.now().isoformat()
            }
        )
    
    def log_field_matching(self, task_id, field_text, matched_type, confidence):
        """记录字段匹配结果"""
        self.logger.debug(
            f"字段匹配: '{field_text}' -> {matched_type} (置信度: {confidence})",
            extra={
                'task_id': task_id,
                'field_text': field_text,
                'matched_type': matched_type,
                'confidence': confidence
            }
        )
    
    def log_performance_metrics(self, task_id, metrics):
        """记录性能指标"""
        self.performance_logger.info(
            f"任务 {task_id} 性能指标",
            extra={
                'task_id': task_id,
                'processing_time': metrics['processing_time'],
                'document_size': metrics['document_size'],
                'tables_processed': metrics['tables_count'],
                'fields_matched': metrics['fields_matched']
            }
        )
```

### 7.2 性能监控

#### 7.2.1 实时监控指标
```python
class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.metrics_collector = MetricsCollector()
    
    def monitor_processing_task(self, func):
        """监控处理任务的装饰器"""
        def wrapper(*args, **kwargs):
            start_time = time.time()
            task_id = kwargs.get('task_id', 'unknown')
            
            try:
                result = func(*args, **kwargs)
                
                # 记录成功指标
                processing_time = time.time() - start_time
                self.metrics_collector.record_success(task_id, processing_time)
                
                return result
                
            except Exception as e:
                # 记录失败指标
                self.metrics_collector.record_failure(task_id, str(e))
                raise
        
        return wrapper
    
    def get_system_health(self):
        """获取系统健康状态"""
        return {
            'active_tasks': self.get_active_task_count(),
            'average_processing_time': self.get_average_processing_time(),
            'success_rate': self.get_success_rate(),
            'error_rate': self.get_error_rate(),
            'system_load': self.get_system_load()
        }
```

## 8. 测试策略设计

### 8.1 单元测试

#### 8.1.1 核心模块测试
```python
class TestDocumentParser(unittest.TestCase):
    """文档解析器测试"""
    
    def setUp(self):
        self.parser = DocumentParser()
        self.test_doc_path = "test_files/sample_table.docx"
    
    def test_parse_simple_table(self):
        """测试简单表格解析"""
        result = self.parser.parse_document(self.test_doc_path, 'docx')
        
        self.assertIsInstance(result, DocumentStructure)
        self.assertGreater(len(result.tables), 0)
        self.assertGreater(result.tables[0].row_count, 0)
    
    def test_parse_complex_table(self):
        """测试复杂表格解析"""
        complex_doc = "test_files/complex_table.docx"
        result = self.parser.parse_document(complex_doc, 'docx')
        
        # 验证合并单元格处理
        for table in result.tables:
            for row in table.rows:
                for cell in row.cells:
                    self.assertIsInstance(cell.row_span, int)
                    self.assertIsInstance(cell.col_span, int)

class TestFieldMatcher(unittest.TestCase):
    """字段匹配器测试"""
    
    def setUp(self):
        self.matcher = RuleBasedMatcher()
    
    def test_exact_match(self):
        """测试精确匹配"""
        result = self.matcher.match_single_field_text("公司名称")
        
        self.assertIsNotNone(result)
        self.assertEqual(result.field_type, "company_name")
        self.assertGreater(result.confidence, 0.9)
    
    def test_fuzzy_match(self):
        """测试模糊匹配"""
        result = self.matcher.match_single_field_text("企业名称")
        
        self.assertIsNotNone(result)
        self.assertEqual(result.field_type, "company_name")
        self.assertGreater(result.confidence, 0.7)
```

### 8.2 集成测试

#### 8.2.1 端到端测试
```python
class TestTableProcessingIntegration(unittest.TestCase):
    """表格处理集成测试"""
    
    def setUp(self):
        self.client = app.test_client()
        self.test_user_id = "test_user_123"
        self.test_file = "test_files/complete_table.docx"
    
    def test_complete_processing_workflow(self):
        """测试完整处理流程"""
        # 1. 上传文档
        with open(self.test_file, 'rb') as f:
            response = self.client.post('/api/table/upload', 
                data={'document': f},
                headers={'Authorization': f'Bearer {self.get_test_token()}'}
            )
        
        self.assertEqual(response.status_code, 200)
        task_id = response.json['task_id']
        
        # 2. 开始处理
        response = self.client.post(f'/api/table/process/{task_id}',
            json={'project_id': 'test_project'},
            headers={'Authorization': f'Bearer {self.get_test_token()}'}
        )
        
        self.assertEqual(response.status_code, 200)
        
        # 3. 等待完成
        max_wait = 60  # 最多等待60秒
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            response = self.client.get(f'/api/table/status/{task_id}',
                headers={'Authorization': f'Bearer {self.get_test_token()}'}
            )
            
            if response.json['status'] == 'completed':
                break
            
            time.sleep(2)
        
        self.assertEqual(response.json['status'], 'completed')
        
        # 4. 验证结果
        response = self.client.get(f'/api/table/result/{task_id}',
            headers={'Authorization': f'Bearer {self.get_test_token()}'}
        )
        
        result = response.json
        self.assertIn('matches', result)
        self.assertGreater(len(result['matches']), 0)
```

## 9. 部署和运维设计

### 9.1 部署策略

#### 9.1.1 容器化部署
```dockerfile
# Dockerfile for table processing service
FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    libreoffice \
    && rm -rf /var/lib/apt/lists/*

# 安装Python依赖
COPY requirements.txt .
RUN pip install -r requirements.txt

# 复制应用代码
COPY . .

# 设置环境变量
ENV PYTHONPATH=/app
ENV FLASK_ENV=production

# 暴露端口
EXPOSE 5000

# 启动命令
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
```

#### 9.1.2 配置管理
```yaml
# docker-compose.yml
version: '3.8'

services:
  table-processor:
    build: .
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - SECRET_KEY=${SECRET_KEY}
    volumes:
      - ./uploads:/app/uploads
      - ./temp:/app/temp
    depends_on:
      - redis
      - database
    
  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"
    
  database:
    image: mysql:8.0
    environment:
      - MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD}
      - MYSQL_DATABASE=${MYSQL_DATABASE}
    volumes:
      - mysql_data:/var/lib/mysql

volumes:
  mysql_data:
```

### 9.2 运维监控

#### 9.2.1 健康检查
```python
@app.route('/health')
def health_check():
    """健康检查接口"""
    try:
        # 检查数据库连接
        db.session.execute('SELECT 1')
        
        # 检查Redis连接
        redis_client.ping()
        
        # 检查磁盘空间
        disk_usage = shutil.disk_usage('/')
        free_space_gb = disk_usage.free / (1024**3)
        
        if free_space_gb < 1:  # 少于1GB空闲空间
            return jsonify({'status': 'warning', 'message': '磁盘空间不足'}), 200
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': app.config['VERSION']
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 503
```

这个更新后的设计文档完整地整合了我们讨论的所有要点，特别是与现有AI标书平台的集成、配置文件复用、基于规则的字段匹配方法，以及完整的技术实现方案。文档现在更适合作为实际开发的指导。