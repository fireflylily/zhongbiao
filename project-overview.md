# AI Tender System Project Overview

## Project Description and Purpose

The AI Tender System (AI标书系统) is a comprehensive intelligent bidding system designed to streamline and automate the tender/bidding process. This system combines AI-powered document processing, automated information extraction, and intelligent response generation to assist companies in handling complex tender documents efficiently.

The system serves three primary functions:
1. **Information Extraction** - Automatically extract key information from tender documents
2. **Business Response Generation** - Generate standardized business responses and fill templates
3. **Technical Proposal Creation** - Create comprehensive technical proposals based on requirements

## Main Directory Structure

### Core System Architecture (`ai_tender_system/`)
```
ai_tender_system/
├── common/                    # Shared utilities and configurations
│   ├── config.py             # Unified configuration management
│   ├── exceptions.py         # Custom exception classes
│   ├── logger.py             # Logging system setup
│   └── utils.py              # Common utility functions
├── modules/                   # Core business modules
│   ├── tender_info/          # Tender information extraction
│   │   └── extractor.py      # Main extraction logic with AI integration
│   └── point_to_point/       # Point-to-point response processing
│       └── processor.py      # Business response processing
├── web/                      # Web application layer
│   ├── app.py               # Flask web application main file
│   ├── static/              # Static assets (CSS, JS, images)
│   │   ├── css/common.css   # Common styling
│   │   └── js/              # JavaScript modules
│   │       ├── common.js    # Shared JavaScript utilities
│   │       ├── tender_info.js      # Tender info extraction UI
│   │       ├── business_response.js # Business response UI
│   │       ├── point_to_point.js   # Point-to-point UI
│   │       ├── tech_proposal.js    # Technical proposal UI
│   │       └── state-manager.js    # Client-side state management
│   └── templates/           # HTML templates
│       ├── index.html       # Main dashboard
│       ├── tender_info.html # Tender information page
│       └── help.html        # Help and documentation
├── data/                    # Data storage
│   ├── configs/             # Configuration files
│   │   └── companies/       # Company profile storage
│   ├── uploads/             # Uploaded files
│   ├── outputs/             # Generated output files
│   └── logs/                # System logs
└── run.py                   # Application entry point
```

### Legacy Modules (Being Integrated)
```
1.读取信息/                    # Information reading module
├── read_info.py             # Document reading logic
├── test_extraction.py       # Extraction testing
└── web_info_app.py          # Web interface

2.填写标书/                    # Tender document filling modules
├── 商务应答/                  # Business response automation
│   ├── fill_bidder_name.py  # Bidder name filling
│   ├── fill_company_info.py # Company information filling
│   ├── insert_images.py     # Image insertion
│   └── insert_reply.py      # Response insertion
└── 技术方案/                  # Technical proposal generation
    ├── TenderGenerator/     # Core generation engine
    └── main.py              # Main generation script

4.需求文件/                    # Requirements and specifications
web页面/                       # Additional web pages
company_configs/              # Company configuration storage
qualifications/               # Qualification document storage
```

## Core Components and Their Roles

### 1. Web Application Layer (`web/app.py`)
- **Role**: Central Flask application serving as the main interface
- **Responsibilities**:
  - Route management for all system functions
  - API endpoint handling
  - File upload/download management
  - Company profile management
  - Integration with all business modules

### 2. Tender Information Extraction (`modules/tender_info/extractor.py`)
- **Role**: AI-powered document analysis and information extraction
- **Responsibilities**:
  - Parse PDF, DOCX, and text documents
  - Extract basic project information (project name, bidder info, dates)
  - Identify qualification requirements
  - Extract technical scoring criteria
  - Generate structured configuration files

### 3. Point-to-Point Processing (`modules/point_to_point/processor.py`)
- **Role**: Automated business response generation
- **Responsibilities**:
  - Process business response templates
  - Fill company information automatically
  - Handle document and table processing
  - Generate customized responses

### 4. Configuration Management (`common/config.py`)
- **Role**: Centralized configuration and settings management
- **Responsibilities**:
  - Environment variable handling
  - API configuration management
  - Path and directory management
  - Database connection settings

### 5. Common Utilities (`common/`)
- **Role**: Shared functionality across all modules
- **Components**:
  - **Logger**: Unified logging system with file rotation
  - **Exceptions**: Custom exception hierarchy for error handling
  - **Utils**: File handling, validation, and processing utilities

### 6. Frontend JavaScript Modules (`web/static/js/`)
- **Role**: Client-side functionality and user interaction
- **Components**:
  - **State Manager**: Client-side state management and data persistence
  - **Common**: Shared utilities (file upload, notifications, API calls)
  - **Module-specific JS**: UI logic for each major function

## Technology Stack

### Backend Technologies
- **Python 3.13** - Main programming language
- **Flask 2.x** - Web framework
- **Flask-CORS** - Cross-origin resource sharing
- **Requests** - HTTP client for API calls
- **PyPDF2** - PDF document processing
- **python-docx** - Microsoft Word document handling
- **ConfigParser** - Configuration file management

### Frontend Technologies
- **HTML5** - Markup language
- **Bootstrap 5.1.3** - CSS framework for responsive design
- **Bootstrap Icons 1.7.2** - Icon library
- **Vanilla JavaScript** - Client-side scripting
- **CSS3** - Styling and animations

### AI/ML Integration
- **OpenAI-compatible API** - Large Language Model integration
- **Custom Prompting System** - Structured AI prompts for information extraction
- **Multi-step Processing** - Staged AI processing for complex documents

### Storage and File Management
- **Local File System** - Document storage and processing
- **JSON Configuration** - Company profiles and settings
- **INI Configuration** - Project-specific settings
- **Log Files** - Comprehensive logging system

### Security Features
- **Secure File Upload** - Werkzeug secure filename handling
- **Input Validation** - Form and API input validation
- **Error Handling** - Comprehensive exception handling
- **API Key Encryption** - Client-side API key encryption

### Development and Deployment
- **Environment Variables** - Configuration through .env files
- **Logging System** - Multi-level logging with rotation
- **Error Tracking** - Detailed error reporting and handling
- **Development Server** - Built-in Flask development server

## System Integration Points

The system is designed with modular architecture where:

1. **Web Layer** acts as the orchestrator, routing requests to appropriate modules
2. **Business Modules** handle specific domain logic (extraction, processing, generation)
3. **Common Layer** provides shared services (logging, configuration, utilities)
4. **Frontend** provides interactive user interfaces with real-time feedback
5. **Storage Layer** manages documents, configurations, and outputs

This architecture enables easy extension, maintenance, and testing of individual components while maintaining system cohesion.