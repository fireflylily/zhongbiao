# Component Dependencies Analysis

## Python Module Dependencies

### Core Module Import Graph

```
ai_tender_system/
├── run.py
│   └── web.app import main
├── web/app.py (Central Hub)
│   ├── common import (get_config, setup_logging, get_module_logger, exceptions, utils)
│   ├── modules.tender_info.extractor import TenderInfoExtractor
│   ├── modules.point_to_point.processor import (PointToPointProcessor, DocumentProcessor, TableProcessor)
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

### Frontend Module Dependency Graph

```
web/static/js/
├── common.js (Base Layer - No Dependencies)
│   ├── Provides: API utilities, file handling, notifications, drag-drop
│   ├── Functions: apiRequest(), showNotification(), downloadFile(), setupDragDrop()
│   └── Global utilities used by all other modules
├── state-manager.js (State Management - No Dependencies)
│   ├── Provides: Client-side state persistence
│   ├── Functions: StateManager.get(), StateManager.set(), StateManager.remove()
│   └── Uses: localStorage for persistence
├── tender_info.js (Depends on: common.js, state-manager.js)
│   ├── Uses: onPageReady(), setupDragDrop(), showNotification(), StateManager
│   ├── Provides: Tender document processing UI
│   └── API Endpoints: /extract-tender-info, /extract-tender-info-step
├── company_selection.js (Depends on: common.js, state-manager.js)
│   ├── Uses: apiRequest(), showNotification(), StateManager
│   ├── Provides: Company profile management
│   └── API Endpoints: /api/companies, /api/companies/<id>
├── business_response.js (Depends on: common.js, state-manager.js)
│   ├── Uses: setupDragDrop(), showNotification(), StateManager
│   ├── Provides: Business response processing UI
│   └── API Endpoints: /process-business-response, /api/business-files
├── point_to_point.js (Depends on: common.js, state-manager.js)
│   ├── Uses: apiRequest(), setupDragDrop(), StateManager
│   ├── Provides: Point-to-point response UI
│   └── API Endpoints: /api/document/process, /api/table/analyze
├── tech_proposal.js (Depends on: common.js, state-manager.js)
│   ├── Uses: apiRequest(), showNotification(), StateManager
│   ├── Provides: Technical proposal generation UI
│   └── API Endpoints: /generate-proposal (placeholder)
└── word-editor.js (Depends on: common.js)
    ├── Uses: showNotification(), enablePasteImageUpload()
    ├── Provides: Word document editing capabilities
    └── Standalone utility for document editing
```

### JavaScript Loading Order (Critical)
```html
<!-- Base dependencies (must load first) -->
<script src="js/state-manager.js"></script>
<script src="js/common.js"></script>

<!-- Page-specific modules (can load in any order after base) -->
<script src="js/tender_info.js"></script>
<script src="js/company_selection.js"></script>
<script src="js/business_response.js"></script>
<script src="js/point_to_point.js"></script>
<script src="js/tech_proposal.js"></script>
<script src="js/word-editor.js"></script>
```

## HTML Template Relationships

### Template Hierarchy
```
web/templates/
├── Base Layout (Implicit - Bootstrap CDN)
│   ├── Bootstrap 5.1.3 CSS/JS
│   ├── Bootstrap Icons 1.7.2
│   └── Common CSS/JS includes
├── index.html (Main Dashboard)
│   ├── Includes: common.js, state-manager.js
│   ├── Navigation to all modules
│   ├── API key configuration
│   └── System status display
├── tender_info.html (Tender Information Page)
│   ├── Depends on: common.js, state-manager.js, tender_info.js
│   ├── File upload interface
│   ├── Progressive extraction display
│   └── Tabbed results view
├── company_selection.html (Company Management)
│   ├── Depends on: common.js, state-manager.js, company_selection.js
│   ├── Company profile CRUD interface
│   ├── Qualification file management
│   └── Form validation
├── business_response.html (Business Response)
│   ├── Depends on: common.js, state-manager.js, business_response.js
│   ├── Template upload interface
│   ├── Company data integration
│   └── Response generation
├── point_to_point.html (Point-to-Point Response)
│   ├── Depends on: common.js, state-manager.js, point_to_point.js
│   ├── Requirement analysis interface
│   ├── Document processing
│   └── Table analysis tools
├── tech_proposal.html (Technical Proposal)
│   ├── Depends on: common.js, state-manager.js, tech_proposal.js
│   ├── Proposal generation interface
│   ├── Word editing integration
│   └── Template management
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

### Must Load First (Bootstrap Dependencies)
1. **state-manager.js** - Required by all other JS modules
2. **common.js** - Required by all page-specific modules
3. **common/config.py** - Required by all Python modules

### Circular Dependency Prevention
- **common/** modules have no dependencies on **modules/** or **web/**
- **modules/** can import from **common/** but not from **web/**
- **web/** can import from both **common/** and **modules/**
- Frontend JS modules use explicit dependency loading order

### External Service Dependencies
- **LLM API Service** - Required for AI processing (configurable endpoint)
- **File System Access** - Required for document processing and storage
- **Network Access** - Required for API calls and external resources (Bootstrap CDN)