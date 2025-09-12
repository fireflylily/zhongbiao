# Component Dependencies Analysis

## Python Module Dependencies

### Core Module Import Graph

```
ai_tender_system/
├── run.py
│   └── web.app import main
├── web/app.py (Central Hub) ⚡ **UPDATED 2025-09-12**
│   ├── common import (get_config, setup_logging, get_module_logger, exceptions, utils)
│   ├── modules.tender_info.extractor import TenderInfoExtractor
│   ├── modules.point_to_point.processor import (PointToPointProcessor, DocumentProcessor, TableProcessor)
│   ├── ✅ 2.填写标书.点对点应答.mcp_bidder_name_processor_enhanced import MCPBidderNameProcessor (Dynamic import)
│   ├── flask import (Flask, request, jsonify, render_template, send_file, send_from_directory)
│   ├── flask_cors import CORS
│   └── werkzeug.utils import secure_filename
├── common/ (Shared Layer)
│   ├── config.py
│   │   ├── os, json, pathlib.Path
│   │   └── typing import (Dict, Any, Optional)
│   ├── exceptions.py (Custom Exception Hierarchy)
│   │   └── No external dependencies
│   ├── logger.py
│   │   ├── logging, logging.handlers
│   │   ├── pathlib.Path
│   │   └── .config import get_config
│   ├── utils.py
│   │   ├── os, hashlib, tempfile, shutil
│   │   ├── datetime, pathlib.Path
│   │   ├── typing import (Optional, Union, List, Dict, Any)
│   │   ├── werkzeug.utils import secure_filename
│   │   └── concurrent.futures import (ThreadPoolExecutor, as_completed)
│   └── __init__.py
│       ├── .config import (get_config, Config)
│       ├── .logger import (setup_logging, get_module_logger)
│       ├── .exceptions import (all exception classes)
│       └── .utils import (all utility functions)
└── modules/
    ├── tender_info/
    │   ├── __init__.py
    │   │   └── .extractor import TenderInfoExtractor
    │   └── extractor.py
    │       ├── requests, json, re, threading, configparser
    │       ├── datetime, pathlib.Path
    │       ├── typing import (Dict, Optional, List, Any)
    │       ├── sys (for path manipulation)
    │       ├── common import (get_config, get_module_logger, exceptions)
    │       ├── PyPDF2 (conditional import)
    │       └── docx import Document (conditional import)
    └── point_to_point/
        ├── __init__.py
        │   └── .processor import (PointToPointProcessor, DocumentProcessor, TableProcessor)
        └── processor.py
            ├── json, pathlib.Path
            ├── typing import (Dict, Any, Optional, List)
            ├── sys (for path manipulation)
            └── common import (get_config, get_module_logger, exceptions, utils)
```

### External Library Dependencies

#### Core System Dependencies
```python
# Web Framework
Flask==2.x
Flask-CORS
Werkzeug

# Document Processing
PyPDF2              # PDF reading
python-docx         # Word document processing
beautifulsoup4      # HTML parsing for preview/edit functionality ⚡ NEW
configparser        # INI file handling (built-in)

# HTTP and API
requests            # API calls to LLM services

# System and Utilities
pathlib            # Path handling (built-in)
hashlib            # File hashing (built-in)
tempfile           # Temporary file handling (built-in)
shutil             # File operations (built-in)
datetime           # Time handling (built-in)
threading          # Concurrent processing (built-in)
concurrent.futures # Async processing (built-in)
```

#### Optional Dependencies
```python
# File Type Detection
python-magic       # MIME type detection (fallback: extension-based)

# Additional Document Formats (Future)
openpyxl          # Excel processing
Pillow            # Image processing
```

## JavaScript Module Relationships

### Frontend Module Dependency Graph (Updated 2025-09-12)

```
web/static/js/
├── common.js (Base Layer - No Dependencies)
│   ├── Provides: API utilities, file handling, notifications, drag-drop
│   ├── Functions: apiRequest(), showNotification(), downloadFile(), setupDragDrop()
│   └── Global utilities used by all other modules
├── state-manager.js (State Management - No Dependencies) [ENHANCED]
│   ├── Provides: Client-side state persistence, cross-page messaging
│   ├── Functions: StateManager.get(), StateManager.set(), StateManager.remove()
│   ├── Enhanced: validateCompanyState(), syncAllPages(), broadcastStateChange()
│   ├── Cross-page communication via storage events
│   └── Uses: localStorage for persistence
└── word-editor.js (Depends on: common.js)
    ├── Uses: showNotification(), enablePasteImageUpload()
    ├── Provides: Word document editing capabilities
    └── Standalone utility for document editing

REMOVED MODULES (Integrated into index.html):
├── [DELETED] tender_info.js - Functionality moved to index.html
├── [DELETED] company_selection.js - Functionality moved to index.html  
├── [DELETED] business_response.js - Functionality moved to index.html
├── [DELETED] point_to_point.js - Functionality moved to index.html
└── [DELETED] tech_proposal.js - Functionality moved to index.html
```

### JavaScript Loading Order (Updated 2025-09-12)
```html
<!-- Single Page Application - All in index.html -->
<script src="js/state-manager.js"></script>
<script src="js/common.js"></script>

<!-- Inline JavaScript within index.html:
- GlobalCompanyManager (Company state synchronization)
- All feature functionality (tender info, business response, etc.)
- Unified company selection management
- Cross-tab state synchronization
-->

<!-- Optional standalone utilities -->
<script src="js/word-editor.js"></script> <!-- Only when needed -->
```

## Critical Component Dependencies ⚡ **UPDATED 2025-09-12**

### Business Response Processing Chain

#### Frontend Dependencies
```
businessResponseForm (index.html)
├── FormData() - 表单数据收集
├── template_file - 模板文件上传
├── company_id - 公司ID (从GlobalCompanyManager获取)
├── project_name, tender_no, date_text - 项目信息
└── fetch('/process-business-response') - API调用
```

#### Backend Dependencies
```
process_business_response() (app.py:364-451)
├── config.get_path('config') - 配置路径获取
├── company_configs_dir / f'{company_id}.json' - 公司配置文件
├── config.get_path('root') / '2.填写标书' / '点对点应答' - MCP处理器路径
├── mcp_bidder_name_processor_enhanced.MCPBidderNameProcessor - 动态导入
└── processor.process_document(template_path) - 文档处理
```

#### Critical File Dependencies
```
Key Files Modified/Referenced:
├── ai_tender_system/web/app.py:375 - 文件字段名检查
├── ai_tender_system/web/app.py:395-403 - 公司数据加载
├── ai_tender_system/web/app.py:425 - 公司名称字段映射
├── data/configs/companies/*.json - 公司配置文件结构
└── 2.填写标书/点对点应答/mcp_bidder_name_processor_enhanced.py - MCP处理器
```

#### Data Flow
```
Frontend Form → FormData → POST /process-business-response → 
Company JSON Load → MCP Processor → Document Processing → 
Result Response → Frontend Display
```

## HTML Template Relationships

### Template Hierarchy (Updated 2025-09-12 - Single Page Architecture)
```
web/templates/
├── Base Layout (Implicit - Bootstrap CDN)
│   ├── Bootstrap 5.1.3 CSS/JS
│   ├── Bootstrap Icons 1.7.2
│   └── Common CSS/JS includes
├── index.html (Single Page Application Hub) [ENHANCED]
│   ├── Includes: state-manager.js, common.js
│   ├── Integrated Features:
│   │   ├── Tender Information Extraction (Tab-based)
│   │   ├── Company Management (Tab-based)
│   │   ├── Business Response Processing (Tab-based)
│   │   ├── Point-to-Point Response (Tab-based)
│   │   └── Technical Proposal Generation (Tab-based)
│   ├── GlobalCompanyManager (Unified company state)
│   ├── Cross-tab state synchronization
│   ├── API key configuration
│   └── System status display
├── help.html (Help and Documentation)
│   ├── Depends on: common.js
│   ├── System usage guide
│   ├── API configuration help
│   └── Troubleshooting information
└── system_status.html (System Status)
    ├── Depends on: common.js, state-manager.js
    ├── Module availability status
    ├── Configuration validation
    └── System health checks

REMOVED TEMPLATES (Functionality integrated into index.html):
├── [DELETED] tender_info.html - Now a tab in index.html
├── [DELETED] company_selection.html - Now a tab in index.html
├── [DELETED] business_response.html - Now a tab in index.html
├── [DELETED] point_to_point.html - Now a tab in index.html
└── [DELETED] tech_proposal.html - Now a tab in index.html
```

## CSS Dependencies

### Styling Hierarchy
```
web/static/css/
└── common.css (Main Stylesheet)
    ├── Base: Bootstrap 5.1.3 (CDN)
    ├── Icons: Bootstrap Icons 1.7.2 (CDN)
    ├── Custom Components:
    │   ├── .upload-area (File upload styling)
    │   ├── .feature-card (Module cards)
    │   ├── .api-status (Status indicators)
    │   ├── .unsaved-indicator (Form state)
    │   └── .modal-backdrop (Modal improvements)
    ├── Animations:
    │   ├── @keyframes pulse-indicator
    │   ├── .feature-card:hover transitions
    │   └── .upload-area:hover effects
    └── Responsive Design:
        ├── Mobile-first approach
        ├── Bootstrap grid integration
        └── Custom breakpoints
```

## Data Flow Dependencies

### Configuration Flow
```
Environment Variables (.env)
    ↓
common/config.py (Config class)
    ↓
All modules import get_config()
    ↓
Runtime configuration access
```

### State Management Flow (Updated 2025-09-12 - Unified Architecture with Fixes)
```
StateManager (Enhanced Global State)
    ├── validateCompanyState() - State consistency validation
    ├── broadcastStateChange() - Cross-component messaging  
    ├── syncAllPages() - Force state synchronization
    └── onStateChangeByKey() - Targeted event listeners
    ↓
GlobalCompanyManager (Enhanced Unified Layer)
    ├── syncCompanySelectors() - Sync all company dropdowns
    ├── displaySelectedCompany() - Show current selection status [NEW]
    ├── loadSelectedCompanyData() - Auto-load company information [NEW]  
    ├── updateCompanyStatusUI() - Update UI state indicators
    ├── bindCompanySelectors() - Bind all selector events
    ├── getCurrentCompanyInfo() - Fixed API response parsing [FIXED]
    └── init() - Initialize with duplicate prevention [ENHANCED]
    ↓
All Feature Components (Within index.html)
    ├── Business Response Processing - Shows "当前选中：公司名称" [ENHANCED]
    ├── Company Management - Auto-fills form and qualifications [ENHANCED]
    ├── Point-to-Point Response
    ├── Technical Proposal Generation
    └── Tender Information Extraction
    ↓
Unified Company Information Access
    ├── getSelectedCompanyInfo() - Single API for all features
    ├── loadCompanyToPage() - Correct form filling function [FIXED]
    └── fillCompanyForm() - Enhanced with debugging [ENHANCED]
```

### Logging Flow
```
common/logger.py (setup_logging)
    ↓
common/__init__.py exports
    ↓
All modules import get_module_logger()
    ↓
Centralized log file writing
```

### Error Handling Flow
```
common/exceptions.py (Exception classes)
    ↓
All modules import custom exceptions
    ↓
web/app.py error handlers
    ↓
JSON error responses to frontend
```

### File Processing Flow
```
File Upload (Frontend)
    ↓
web/app.py (Route handling)
    ↓
common/utils.py (File validation/processing)
    ↓
Module-specific processing
    ↓
common/utils.py (Output file generation)
    ↓
Response to frontend
```

## Critical Dependencies

### Must Load First (Bootstrap Dependencies - Updated 2025-09-12)
1. **state-manager.js** - Enhanced with cross-page messaging, required by index.html
2. **common.js** - Required by all functionality within index.html  
3. **common/config.py** - Required by all Python modules

### Circular Dependency Prevention (Simplified Architecture)
- **common/** modules have no dependencies on **modules/** or **web/**
- **modules/** can import from **common/** but not from **web/**
- **web/** can import from both **common/** and **modules/**
- **Single Page Architecture**: All frontend functionality consolidated in index.html
- **No Cross-Template Dependencies**: Each template is self-contained

### External Service Dependencies ⚡ **UPDATED 2025-09-12**
- **LLM API Service** - Required for AI processing (configurable endpoint)
- **File System Access** - Required for document processing and storage
- **Network Access** - Required for API calls and external resources (Bootstrap CDN)
- **🆕 TinyMCE CDN** - Required for document editing functionality (cloud.tinymce.com)

## 🆕 **新增组件依赖分析** ⚡ **NEW 2025-09-12**

### 文档预览与编辑系统依赖关系

#### Frontend Dependencies
```
Document Preview & Edit System
├── TinyMCE 6.x (CDN) - Rich text editor core
│   ├── cloud.tinymce.com/6/tinymce.min.js
│   ├── Plugins: advlist, autolink, lists, link, image, table, help, wordcount
│   └── Toolbar: formatting, alignment, lists, tables, media
├── Bootstrap 5 Modal - UI container
│   ├── Modal backdrop and dialog structure
│   ├── Responsive layout and mobile optimization
│   └── Event handling for show/hide
├── JavaScript Integration
│   ├── WordEditor class (word-editor.js)
│   ├── Modal management functions (inline in index.html)
│   ├── Dual loading mechanism (API + file upload)
│   └── Error handling and fallback mechanisms
└── CSS Styling
    ├── Bootstrap modal styles
    ├── TinyMCE editor container
    ├── Custom loading animations
    └── Responsive preview layout
```

#### Backend Dependencies
```
Document Processing APIs
├── Flask Routes (/api/document/preview, /api/editor/*)
│   ├── Route registration in app.py
│   ├── Request validation and error handling
│   └── Response formatting (JSON/Binary)
├── python-docx Integration
│   ├── Document parsing and structure extraction
│   ├── Paragraph, table, and list processing
│   ├── Image and media handling
│   └── Word document generation from HTML
├── BeautifulSoup4 Integration
│   ├── HTML parsing and cleanup
│   ├── Tag structure validation
│   ├── Content sanitization
│   └── Format conversion utilities
└── File System Operations
    ├── Temporary file management
    ├── Document caching mechanisms
    ├── Safe filename handling
    └── Path validation and security
```

#### Data Flow Dependencies
```
Preview/Edit Workflow
User Action → Modal Trigger → TinyMCE Load → Document API → 
python-docx Parse → BeautifulSoup Process → HTML Display → 
User Edit → Content Validate → Document Generate → File Download

Error Handling Chain:
TinyMCE Fail → Pure HTML Preview → API Fail → File Download → 
Complete Fail → Hide Feature
```

#### Critical Integration Points
```
Key Dependency Intersections:
├── TinyMCE.init() ↔ WordEditor.constructor - Editor initialization
├── Modal.show() ↔ Document.preview() - UI/API coordination  
├── FormData ↔ /api/editor/load-document - File upload handling
├── HTML Content ↔ python-docx.Document - Format conversion
├── BeautifulSoup ↔ TinyMCE.getContent() - Content processing
└── Error States ↔ Fallback Mechanisms - Graceful degradation
```

### 性能与可靠性考虑

#### CDN依赖风险
- **TinyMCE CDN失败**: 自动降级为纯HTML预览
- **Bootstrap CDN失败**: 基础功能仍可用，UI样式降级
- **网络连接问题**: 本地缓存机制和离线提示

#### 内存与处理性能
- **大文档处理**: 分块处理和进度指示
- **编辑器实例管理**: 按需创建和销毁
- **HTML内容缓存**: 避免重复转换

#### 兼容性保证
- **浏览器兼容**: 支持主流现代浏览器
- **MIME类型检测**: 多层验证机制
- **文档格式支持**: .docx优先，.doc备用