# 招标信息读取页面重构设计文档

## 1. 系统架构设计

### 1.1 总体架构
```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│   前端展示层         │    │   业务逻辑层         │    │   数据存储层         │
│  (Web Interface)    │    │  (Business Logic)   │    │  (Data Storage)     │
├─────────────────────┤    ├─────────────────────┤    ├─────────────────────┤
│ • 多文件上传界面     │    │ • 文件解析服务       │    │ • 文件存储          │
│ • 三步骤信息展示     │    │ • 信息提取引擎       │    │ • 数据库            │
│ • 评分信息表格       │◄──►│ • 模板生成服务       │◄──►│ • 配置文件          │
│ • 应答模板管理       │    │ • 数据处理服务       │    │ • 缓存系统          │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
```

### 1.2 模块组件设计
```
TenderInfoSystem/
├── frontend/                    # 前端模块
│   ├── components/
│   │   ├── FileUpload/         # 文件上传组件
│   │   ├── StepIndicator/      # 步骤指示器
│   │   ├── BasicInfoForm/      # 基本信息表单
│   │   ├── RequirementsPanel/  # 投标要求面板
│   │   └── ScoringTable/       # 评分表格
│   ├── services/
│   │   ├── fileService.js      # 文件操作服务
│   │   ├── extractionService.js # 信息提取服务
│   │   └── templateService.js   # 模板服务
│   └── utils/
│       ├── fileValidator.js    # 文件验证工具
│       └── formatHelper.js     # 格式化工具
├── backend/                     # 后端模块
│   ├── parsers/                # 文档解析器
│   │   ├── pdf_parser.py       # PDF解析器
│   │   ├── word_parser.py      # Word解析器
│   │   ├── excel_parser.py     # Excel解析器
│   │   └── base_parser.py      # 基础解析器
│   ├── extractors/             # 信息提取器
│   │   ├── basic_info_extractor.py    # 基本信息提取
│   │   ├── requirements_extractor.py  # 要求信息提取
│   │   ├── scoring_extractor.py       # 评分信息提取
│   │   └── template_extractor.py      # 模板格式提取
│   ├── generators/             # 生成器
│   │   ├── template_generator.py      # 模板生成器
│   │   └── report_generator.py        # 报告生成器
│   └── services/
│       ├── file_service.py     # 文件服务
│       ├── extraction_service.py # 提取服务
│       └── integration_service.py # 集成服务
└── data/                       # 数据层
    ├── models/                 # 数据模型
    ├── storage/               # 存储管理
    └── cache/                 # 缓存管理
```

## 2. 数据模型设计

### 2.1 文件管理模型
```python
class UploadedFile:
    file_id: str              # 文件唯一标识
    original_name: str        # 原始文件名
    file_type: str           # 文件类型 (pdf/doc/docx/xls/xlsx)
    file_size: int           # 文件大小(字节)
    upload_time: datetime    # 上传时间
    storage_path: str        # 存储路径
    status: str             # 状态 (uploading/ready/processing/error)
    extraction_status: str   # 提取状态
    metadata: dict          # 文件元数据
```

### 2.2 项目信息模型
```python
class TenderProject:
    project_id: str          # 项目唯一标识
    basic_info: BasicInfo    # 基本信息
    requirements: Requirements # 投标要求
    scoring: ScoringInfo     # 评分信息
    response_template: ResponseTemplate # 应答模板
    created_time: datetime   # 创建时间
    updated_time: datetime   # 更新时间
    status: str             # 项目状态

class BasicInfo:
    tenderer: str           # 招标人
    agency: str             # 招标代理
    bidding_method: str     # 投标方式
    bidding_location: str   # 投标地点
    bidding_time: str       # 投标时间
    winner_count: str       # 中标人数量
    project_name: str       # 项目名称
    project_number: str     # 项目编号
    extraction_confidence: dict # 提取置信度

class Requirements:
    qualifications: List[QualificationRequirement] # 资质要求
    performance: List[PerformanceRequirement]     # 业绩要求
    other_requirements: List[OtherRequirement]    # 其他要求

class ScoringInfo:
    total_score: float      # 总分
    categories: List[ScoringCategory] # 评分类别
    has_scoring: bool       # 是否有评分标准
    
class ScoringCategory:
    category_name: str      # 类别名称 (技术分/商务分/报价分)
    weight: float          # 权重
    max_score: float       # 最高分
    items: List[ScoringItem] # 评分项目

class ScoringItem:
    item_name: str         # 评分项名称
    criteria: str          # 评分标准
    max_score: float       # 最高分值
    description: str       # 详细说明
```

### 2.3 应答模板模型
```python
class ResponseTemplate:
    template_id: str        # 模板ID
    template_name: str      # 模板名称
    content_sections: List[TemplateSection] # 内容章节
    format_requirements: str # 格式要求
    auto_generated: bool    # 是否自动生成
    file_path: str         # 模板文件路径

class TemplateSection:
    section_title: str      # 章节标题
    section_level: int      # 标题层级
    content_placeholder: str # 内容占位符
    required: bool         # 是否必需
    order: int            # 排序
```

## 3. 前端界面设计

### 3.1 主界面布局
```html
<div class="tender-info-container">
    <!-- 步骤指示器 -->
    <div class="step-indicator">
        <div class="step active" data-step="1">
            <div class="step-number">1</div>
            <div class="step-title">文件上传</div>
        </div>
        <div class="step" data-step="2">
            <div class="step-number">2</div>
            <div class="step-title">基本信息</div>
        </div>
        <div class="step" data-step="3">
            <div class="step-number">3</div>
            <div class="step-title">投标要求</div>
        </div>
        <div class="step" data-step="4">
            <div class="step-number">4</div>
            <div class="step-title">评分信息</div>
        </div>
    </div>

    <!-- 内容区域 -->
    <div class="content-area">
        <!-- 各步骤内容面板 -->
    </div>

    <!-- 操作按钮 -->
    <div class="action-buttons">
        <button class="btn-prev">上一步</button>
        <button class="btn-next">下一步</button>
        <button class="btn-save">保存</button>
        <button class="btn-complete">完成</button>
    </div>
</div>
```

### 3.2 多文件上传组件设计
```javascript
class MultiFileUpload {
    constructor(options) {
        this.maxFiles = options.maxFiles || 10;
        this.maxSize = options.maxSize || 50 * 1024 * 1024; // 50MB
        this.allowedTypes = options.allowedTypes || ['.pdf', '.doc', '.docx', '.xls', '.xlsx'];
        this.files = [];
    }

    // 拖拽上传处理
    handleDrop(event) {
        event.preventDefault();
        const files = Array.from(event.dataTransfer.files);
        this.addFiles(files);
    }

    // 文件选择处理
    handleFileSelect(event) {
        const files = Array.from(event.target.files);
        this.addFiles(files);
    }

    // 添加文件
    addFiles(files) {
        files.forEach(file => {
            if (this.validateFile(file)) {
                this.files.push({
                    file: file,
                    id: this.generateId(),
                    status: 'pending',
                    progress: 0
                });
            }
        });
        this.renderFileList();
    }

    // 文件验证
    validateFile(file) {
        // 检查文件类型
        const extension = '.' + file.name.split('.').pop().toLowerCase();
        if (!this.allowedTypes.includes(extension)) {
            this.showError(`不支持的文件类型: ${extension}`);
            return false;
        }

        // 检查文件大小
        if (file.size > this.maxSize) {
            this.showError(`文件过大: ${file.name}`);
            return false;
        }

        // 检查文件数量
        if (this.files.length >= this.maxFiles) {
            this.showError(`最多只能上传 ${this.maxFiles} 个文件`);
            return false;
        }

        return true;
    }

    // 上传文件
    async uploadFiles() {
        const uploadPromises = this.files.map(fileObj => {
            return this.uploadSingleFile(fileObj);
        });

        try {
            const results = await Promise.all(uploadPromises);
            return results;
        } catch (error) {
            console.error('文件上传失败:', error);
            throw error;
        }
    }

    // 上传单个文件
    async uploadSingleFile(fileObj) {
        const formData = new FormData();
        formData.append('file', fileObj.file);
        formData.append('fileId', fileObj.id);

        try {
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData,
                onUploadProgress: (progressEvent) => {
                    const progress = Math.round(
                        (progressEvent.loaded * 100) / progressEvent.total
                    );
                    this.updateProgress(fileObj.id, progress);
                }
            });

            if (response.ok) {
                const result = await response.json();
                fileObj.status = 'completed';
                fileObj.serverFileId = result.fileId;
                return result;
            } else {
                throw new Error('上传失败');
            }
        } catch (error) {
            fileObj.status = 'error';
            throw error;
        }
    }
}
```

### 3.3 信息提取结果展示组件
```javascript
class InfoExtractionDisplay {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.data = {};
    }

    // 显示基本信息
    renderBasicInfo(basicInfo) {
        const html = `
            <div class="basic-info-panel">
                <h3>基本信息</h3>
                <div class="info-grid">
                    ${this.renderInfoField('招标人', 'tenderer', basicInfo)}
                    ${this.renderInfoField('招标代理', 'agency', basicInfo)}
                    ${this.renderInfoField('投标方式', 'bidding_method', basicInfo)}
                    ${this.renderInfoField('投标地点', 'bidding_location', basicInfo)}
                    ${this.renderInfoField('投标时间', 'bidding_time', basicInfo)}
                    ${this.renderInfoField('中标人数量', 'winner_count', basicInfo)}
                    ${this.renderInfoField('项目名称', 'project_name', basicInfo)}
                    ${this.renderInfoField('项目编号', 'project_number', basicInfo)}
                </div>
            </div>
        `;
        this.container.innerHTML = html;
        this.bindEditEvents();
    }

    // 渲染信息字段
    renderInfoField(label, field, data) {
        const value = data[field] || '';
        const confidence = data.extraction_confidence?.[field] || 'medium';
        const confidenceClass = `confidence-${confidence}`;
        
        return `
            <div class="info-field ${confidenceClass}">
                <label class="field-label">${label}</label>
                <div class="field-content">
                    <input type="text" 
                           class="field-input" 
                           data-field="${field}"
                           value="${value}" 
                           placeholder="未提取到信息">
                    <div class="confidence-indicator" 
                         title="提取置信度: ${confidence}">
                        <i class="confidence-icon"></i>
                    </div>
                    <button class="edit-btn" data-field="${field}">
                        <i class="bi bi-pencil"></i>
                    </button>
                </div>
            </div>
        `;
    }

    // 显示评分信息
    renderScoringInfo(scoringInfo) {
        if (!scoringInfo.has_scoring) {
            return this.renderNoScoring();
        }

        const html = `
            <div class="scoring-info-panel">
                <h3>评分信息</h3>
                <div class="scoring-summary">
                    <div class="total-score">总分：${scoringInfo.total_score}分</div>
                </div>
                <div class="scoring-categories">
                    ${scoringInfo.categories.map(category => this.renderScoringCategory(category)).join('')}
                </div>
            </div>
        `;
        this.container.innerHTML = html;
    }

    // 渲染评分类别
    renderScoringCategory(category) {
        return `
            <div class="scoring-category">
                <div class="category-header">
                    <h4>${category.category_name}</h4>
                    <span class="category-score">${category.max_score}分 (${category.weight}%)</span>
                </div>
                <div class="scoring-items">
                    <table class="scoring-table">
                        <thead>
                            <tr>
                                <th>评分项</th>
                                <th>评分标准</th>
                                <th>分值</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${category.items.map(item => this.renderScoringItem(item)).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
    }

    // 渲染评分项
    renderScoringItem(item) {
        return `
            <tr class="scoring-item">
                <td class="item-name">${item.item_name}</td>
                <td class="item-criteria">${item.criteria}</td>
                <td class="item-score">${item.max_score}分</td>
            </tr>
        `;
    }

    // 无评分标准显示
    renderNoScoring() {
        return `
            <div class="no-scoring-panel">
                <div class="no-scoring-message">
                    <i class="bi bi-info-circle"></i>
                    <h4>该项目无评分标准</h4>
                    <p class="text-muted">招标文档中未找到具体的评分要求和标准</p>
                </div>
            </div>
        `;
    }
}
```

## 4. 后端API设计

### 4.1 文件上传API
```python
@app.route('/api/upload', methods=['POST'])
def upload_files():
    """
    多文件上传接口
    """
    try:
        files = request.files.getlist('files')
        project_id = request.form.get('project_id')
        
        uploaded_files = []
        for file in files:
            # 验证文件
            if not file_service.validate_file(file):
                continue
                
            # 保存文件
            file_info = file_service.save_file(file, project_id)
            uploaded_files.append(file_info)
        
        return jsonify({
            'success': True,
            'files': uploaded_files,
            'message': f'成功上传 {len(uploaded_files)} 个文件'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/extract', methods=['POST'])
def extract_information():
    """
    信息提取接口
    """
    try:
        project_id = request.json.get('project_id')
        file_ids = request.json.get('file_ids', [])
        
        # 获取上传的文件
        files = file_service.get_files(file_ids)
        
        # 提取信息
        extractor = TenderInfoExtractor()
        result = extractor.extract_from_files(files)
        
        # 保存结果
        project_service.save_extraction_result(project_id, result)
        
        return jsonify({
            'success': True,
            'data': result,
            'message': '信息提取完成'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/generate-template', methods=['POST'])
def generate_response_template():
    """
    应答模板生成接口
    """
    try:
        project_id = request.json.get('project_id')
        template_requirements = request.json.get('template_requirements')
        
        # 生成模板
        generator = ResponseTemplateGenerator()
        template = generator.generate_template(template_requirements)
        
        # 保存模板
        template_service.save_template(project_id, template)
        
        return jsonify({
            'success': True,
            'template': template,
            'message': '应答模板生成完成'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
```

### 4.2 信息提取服务设计
```python
class TenderInfoExtractor:
    def __init__(self):
        self.parsers = {
            'pdf': PDFParser(),
            'doc': WordParser(),
            'docx': WordParser(),
            'xls': ExcelParser(),
            'xlsx': ExcelParser()
        }
        self.extractors = {
            'basic_info': BasicInfoExtractor(),
            'requirements': RequirementsExtractor(),
            'scoring': ScoringExtractor(),
            'template': TemplateExtractor()
        }

    def extract_from_files(self, files):
        """
        从多个文件中提取信息
        """
        all_content = []
        
        # 解析所有文件
        for file_info in files:
            parser = self.parsers.get(file_info.file_type)
            if parser:
                content = parser.parse(file_info.storage_path)
                all_content.append({
                    'file_id': file_info.file_id,
                    'file_name': file_info.original_name,
                    'content': content
                })

        # 合并内容
        merged_content = self.merge_content(all_content)
        
        # 提取各类信息
        result = {}
        for extract_type, extractor in self.extractors.items():
            try:
                result[extract_type] = extractor.extract(merged_content)
            except Exception as e:
                logger.error(f"提取{extract_type}失败: {e}")
                result[extract_type] = None

        return result

    def merge_content(self, content_list):
        """
        合并多个文件的内容
        """
        merged = {
            'text_content': '',
            'tables': [],
            'images': [],
            'metadata': {}
        }
        
        for content in content_list:
            merged['text_content'] += content['content'].get('text', '') + '\n'
            merged['tables'].extend(content['content'].get('tables', []))
            merged['images'].extend(content['content'].get('images', []))
            
        return merged

class BasicInfoExtractor:
    def __init__(self):
        self.llm_client = LLMClient()
        self.regex_patterns = self.load_regex_patterns()

    def extract(self, content):
        """
        提取基本信息
        """
        # 首先使用正则表达式提取
        regex_result = self.extract_with_regex(content['text_content'])
        
        # 使用LLM补充和验证
        llm_result = self.extract_with_llm(content['text_content'])
        
        # 合并结果
        merged_result = self.merge_results(regex_result, llm_result)
        
        # 计算置信度
        confidence = self.calculate_confidence(regex_result, llm_result)
        
        return {
            **merged_result,
            'extraction_confidence': confidence
        }

    def extract_with_regex(self, text):
        """
        使用正则表达式提取
        """
        result = {}
        for field, patterns in self.regex_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    result[field] = match.group(1).strip()
                    break
        return result

    def extract_with_llm(self, text):
        """
        使用LLM提取
        """
        prompt = self.build_extraction_prompt(text)
        response = self.llm_client.call(prompt)
        return self.parse_llm_response(response)

    def calculate_confidence(self, regex_result, llm_result):
        """
        计算提取置信度
        """
        confidence = {}
        fields = ['tenderer', 'agency', 'bidding_method', 'bidding_location',
                 'bidding_time', 'winner_count', 'project_name', 'project_number']
        
        for field in fields:
            regex_value = regex_result.get(field)
            llm_value = llm_result.get(field)
            
            if regex_value and llm_value:
                # 如果两种方法结果一致，高置信度
                similarity = self.calculate_similarity(regex_value, llm_value)
                if similarity > 0.8:
                    confidence[field] = 'high'
                else:
                    confidence[field] = 'medium'
            elif regex_value or llm_value:
                # 只有一种方法有结果，中等置信度
                confidence[field] = 'medium'
            else:
                # 没有提取到，低置信度
                confidence[field] = 'low'
                
        return confidence

class ResponseTemplateGenerator:
    def __init__(self):
        self.template_patterns = self.load_template_patterns()
        self.word_generator = WordDocumentGenerator()

    def generate_template(self, template_requirements):
        """
        生成应答文件模板
        """
        # 解析模板要求
        sections = self.parse_template_requirements(template_requirements)
        
        # 生成模板结构
        template_structure = self.build_template_structure(sections)
        
        # 生成Word文档
        doc_path = self.word_generator.generate_document(template_structure)
        
        return {
            'template_id': self.generate_template_id(),
            'sections': template_structure,
            'file_path': doc_path,
            'auto_generated': True,
            'created_time': datetime.now()
        }

    def parse_template_requirements(self, requirements_text):
        """
        解析应答文件格式要求
        """
        sections = []
        
        # 使用正则表达式识别章节标题
        title_pattern = r'^(\d+[\.\)、]?\s*[^\n]+?)(?:\n|$)'
        matches = re.finditer(title_pattern, requirements_text, re.MULTILINE)
        
        for match in matches:
            title = match.group(1).strip()
            # 确定标题层级
            level = self.determine_title_level(title)
            
            sections.append({
                'title': self.clean_title(title),
                'level': level,
                'required': True,
                'placeholder': f'请在此处填写{self.clean_title(title)}相关内容'
            })
            
        return sections

    def build_template_structure(self, sections):
        """
        构建模板结构
        """
        template_structure = {
            'title': '投标文件',
            'sections': []
        }
        
        for i, section in enumerate(sections):
            template_structure['sections'].append({
                'order': i + 1,
                'title': section['title'],
                'level': section['level'],
                'content': section['placeholder'],
                'required': section['required']
            })
            
        return template_structure
```

## 5. 集成方案设计

### 5.1 与商务应答系统集成
```python
class BusinessResponseIntegration:
    def __init__(self):
        self.template_service = TemplateService()
        
    def auto_load_template(self, project_id):
        """
        自动加载生成的应答模板
        """
        try:
            # 获取项目的应答模板
            template = self.template_service.get_project_template(project_id)
            
            if template and template.auto_generated:
                # 检查模板文件是否存在
                if os.path.exists(template.file_path):
                    return {
                        'has_template': True,
                        'template_info': {
                            'template_id': template.template_id,
                            'file_path': template.file_path,
                            'file_name': os.path.basename(template.file_path),
                            'auto_generated': True
                        }
                    }
            
            return {'has_template': False}
            
        except Exception as e:
            logger.error(f"自动加载模板失败: {e}")
            return {'has_template': False}
    
    def handle_manual_upload(self, project_id, uploaded_file):
        """
        处理手动上传的模板文件
        """
        # 手动上传的文件优先级更高
        # 更新项目的模板引用
        self.template_service.update_project_template(
            project_id, 
            uploaded_file,
            auto_generated=False
        )
        
        return True
```

### 5.2 数据同步方案
```python
class DataSyncService:
    def __init__(self):
        self.config_manager = ConfigManager()
        
    def sync_to_config_file(self, project_info):
        """
        同步数据到配置文件（兼容现有系统）
        """
        config = configparser.ConfigParser()
        
        # 基本信息
        config.add_section('PROJECT_INFO')
        basic_info = project_info.basic_info
        config.set('PROJECT_INFO', 'tenderer', basic_info.tenderer)
        config.set('PROJECT_INFO', 'agency', basic_info.agency)
        config.set('PROJECT_INFO', 'bidding_method', basic_info.bidding_method)
        config.set('PROJECT_INFO', 'bidding_location', basic_info.bidding_location)
        config.set('PROJECT_INFO', 'bidding_time', basic_info.bidding_time)
        config.set('PROJECT_INFO', 'winner_count', basic_info.winner_count)
        config.set('PROJECT_INFO', 'project_name', basic_info.project_name)
        config.set('PROJECT_INFO', 'project_number', basic_info.project_number)
        
        # 资质要求
        config.add_section('QUALIFICATION_REQUIREMENTS')
        for req in project_info.requirements.qualifications:
            config.set('QUALIFICATION_REQUIREMENTS', 
                      f'{req.type}_required', str(req.required))
            config.set('QUALIFICATION_REQUIREMENTS', 
                      f'{req.type}_description', req.description)
        
        # 评分信息
        if project_info.scoring.has_scoring:
            config.add_section('SCORING_INFO')
            config.set('SCORING_INFO', 'total_score', str(project_info.scoring.total_score))
            config.set('SCORING_INFO', 'categories_count', str(len(project_info.scoring.categories)))
            
            for i, category in enumerate(project_info.scoring.categories):
                config.set('SCORING_INFO', f'category_{i}_name', category.category_name)
                config.set('SCORING_INFO', f'category_{i}_weight', str(category.weight))
                config.set('SCORING_INFO', f'category_{i}_score', str(category.max_score))
        
        # 保存配置文件
        config_path = f'projects/{project_info.project_id}/tender_config.ini'
        with open(config_path, 'w', encoding='utf-8') as f:
            config.write(f)
            
        return config_path
```

## 6. 性能优化设计

### 6.1 文件处理优化
```python
class FileProcessingOptimizer:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.cache = RedisCache()
        
    async def process_files_parallel(self, files):
        """
        并行处理文件
        """
        tasks = []
        for file_info in files:
            task = asyncio.create_task(
                self.process_single_file(file_info)
            )
            tasks.append(task)
            
        results = await asyncio.gather(*tasks)
        return results
    
    async def process_single_file(self, file_info):
        """
        处理单个文件（异步）
        """
        # 检查缓存
        cache_key = f"file_content_{file_info.file_id}"
        cached_result = self.cache.get(cache_key)
        
        if cached_result:
            return cached_result
            
        # 解析文件
        parser = self.get_parser(file_info.file_type)
        content = await parser.parse_async(file_info.storage_path)
        
        # 缓存结果
        self.cache.set(cache_key, content, ttl=3600)  # 1小时缓存
        
        return content
```

### 6.2 前端性能优化
```javascript
// 虚拟滚动优化大型表格
class VirtualScrollTable {
    constructor(container, data, rowHeight = 40) {
        this.container = container;
        this.data = data;
        this.rowHeight = rowHeight;
        this.viewportHeight = container.clientHeight;
        this.visibleCount = Math.ceil(this.viewportHeight / rowHeight) + 2;
        
        this.init();
    }
    
    init() {
        this.container.innerHTML = `
            <div class="table-viewport" style="height: ${this.viewportHeight}px; overflow-y: auto;">
                <div class="table-content" style="height: ${this.data.length * this.rowHeight}px; position: relative;">
                    <div class="visible-rows"></div>
                </div>
            </div>
        `;
        
        this.viewport = this.container.querySelector('.table-viewport');
        this.content = this.container.querySelector('.table-content');
        this.visibleRows = this.container.querySelector('.visible-rows');
        
        this.viewport.addEventListener('scroll', this.handleScroll.bind(this));
        this.render();
    }
    
    handleScroll() {
        this.render();
    }
    
    render() {
        const scrollTop = this.viewport.scrollTop;
        const startIndex = Math.floor(scrollTop / this.rowHeight);
        const endIndex = Math.min(startIndex + this.visibleCount, this.data.length);
        
        let html = '';
        for (let i = startIndex; i < endIndex; i++) {
            const item = this.data[i];
            html += `
                <div class="table-row" style="position: absolute; top: ${i * this.rowHeight}px; height: ${this.rowHeight}px;">
                    ${this.renderRow(item)}
                </div>
            `;
        }
        
        this.visibleRows.innerHTML = html;
    }
}

// 防抖优化搜索
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// 使用Web Workers处理大文件
class FileProcessor {
    constructor() {
        this.worker = new Worker('/js/file-processing-worker.js');
    }
    
    async processLargeFile(file) {
        return new Promise((resolve, reject) => {
            this.worker.postMessage({ file: file });
            
            this.worker.onmessage = (e) => {
                if (e.data.success) {
                    resolve(e.data.result);
                } else {
                    reject(new Error(e.data.error));
                }
            };
        });
    }
}
```

## 7. 安全设计

### 7.1 文件上传安全
```python
class FileSecurityValidator:
    def __init__(self):
        self.allowed_extensions = {'.pdf', '.doc', '.docx', '.xls', '.xlsx', '.txt'}
        self.max_file_size = 50 * 1024 * 1024  # 50MB
        self.virus_scanner = ClamAVScanner()
        
    def validate_file(self, file):
        """
        文件安全验证
        """
        # 检查文件扩展名
        if not self.check_extension(file.filename):
            raise SecurityError("不允许的文件类型")
            
        # 检查文件大小
        if file.content_length > self.max_file_size:
            raise SecurityError("文件太大")
            
        # 检查MIME类型
        if not self.check_mime_type(file):
            raise SecurityError("文件类型不匹配")
            
        # 病毒扫描
        if not self.virus_scanner.scan(file):
            raise SecurityError("文件包含恶意内容")
            
        # 检查文件头
        if not self.check_file_header(file):
            raise SecurityError("文件头验证失败")
            
        return True
    
    def check_extension(self, filename):
        return Path(filename).suffix.lower() in self.allowed_extensions
    
    def check_mime_type(self, file):
        mime_type = magic.from_buffer(file.read(1024), mime=True)
        file.seek(0)  # 重置文件指针
        
        allowed_mimes = {
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'text/plain'
        }
        
        return mime_type in allowed_mimes
    
    def check_file_header(self, file):
        """
        检查文件头魔数
        """
        file_headers = {
            b'%PDF': '.pdf',
            b'\xd0\xcf\x11\xe0': '.doc',
            b'PK\x03\x04': '.docx',  # 也可能是.xlsx
        }
        
        header = file.read(8)
        file.seek(0)
        
        for magic_bytes, extension in file_headers.items():
            if header.startswith(magic_bytes):
                return True
        
        return False

class AccessControl:
    def __init__(self):
        self.session_manager = SessionManager()
        
    def require_login(self, f):
        """
        登录验证装饰器
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not self.session_manager.is_logged_in():
                return jsonify({'error': '需要登录'}), 401
            return f(*args, **kwargs)
        return decorated_function
    
    def require_project_access(self, f):
        """
        项目访问权限验证装饰器
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            project_id = request.json.get('project_id') or request.args.get('project_id')
            user_id = self.session_manager.get_current_user_id()
            
            if not self.has_project_access(user_id, project_id):
                return jsonify({'error': '无访问权限'}), 403
                
            return f(*args, **kwargs)
        return decorated_function
```

## 8. 部署方案

### 8.1 容器化部署
```dockerfile
# Dockerfile
FROM python:3.9-slim

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    libmagic1 \
    clamav \
    clamav-daemon \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制项目文件
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# 暴露端口
EXPOSE 8080

# 启动命令
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "4", "app:app"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "8080:8080"
    volumes:
      - ./uploads:/app/uploads
      - ./data:/app/data
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=postgresql://user:pass@db:5432/tender_db
    depends_on:
      - db
      - redis

  db:
    image: postgres:13
    environment:
      POSTGRES_DB: tender_db
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

### 8.2 监控和日志
```python
# 监控配置
import logging
from prometheus_client import Counter, Histogram, generate_latest

# 指标定义
file_upload_counter = Counter('file_uploads_total', 'Total file uploads')
extraction_duration = Histogram('extraction_duration_seconds', 'Time spent on extraction')

class MonitoringMiddleware:
    def __init__(self, app):
        self.app = app
        
    def __call__(self, environ, start_response):
        start_time = time.time()
        
        def new_start_response(status, response_headers):
            # 记录响应时间
            duration = time.time() - start_time
            logging.info(f"Request completed in {duration:.2f}s")
            return start_response(status, response_headers)
            
        return self.app(environ, new_start_response)

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/tender-info.log'),
        logging.StreamHandler()
    ]
)
```

---

**文档版本**：1.0
**创建日期**：2025年9月9日
**最后更新**：2025年9月9日
**文档状态**：待审核