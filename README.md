# 🚀 AI 智能标书生成平台

> 基于人工智能的标书自动化处理与生成系统

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Flask Version](https://img.shields.io/badge/flask-2.3.3-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![CSRF Protection](https://img.shields.io/badge/CSRF-Protected-success.svg)](CSRF_PROTECTION_GUIDE.md)

---

## 📖 目录

- [系统简介](#-系统简介)
- [核心功能](#-核心功能)
- [技术架构](#-技术架构)
- [快速开始](#-快速开始)
- [功能模块](#-功能模块)
- [项目结构](#-项目结构)
- [文档导航](#-文档导航)
- [开发指南](#-开发指南)
- [部署说明](#-部署说明)
- [常见问题](#-常见问题)
- [贡献指南](#-贡献指南)
- [许可证](#-许可证)

---

## 🎯 系统简介

**AI 智能标书生成平台**是一套完整的投标文件自动化处理解决方案，通过 AI 技术实现招标文档智能解析、知识库管理、商务应答生成、技术方案编写等核心功能，大幅提升投标效率。

### 🌟 核心优势

- **🤖 智能化处理** - AI 驱动的文档解析与内容生成
- **📚 知识沉淀** - 企业知识库统一管理，历史案例快速复用
- **⚡ 高效协作** - HITL（Human-in-the-Loop）人机协作流程
- **🔍 精准检索** - 向量搜索引擎，语义级内容匹配
- **🛡️ 安全可靠** - CSRF 保护、输入验证、安全日志

---

## ✨ 核心功能

### 1. 📄 招标文档智能解析

- **多格式支持** - PDF、Word、Excel 自动识别与提取
- **结构化提取** - 投标要求、评分标准、资质要求智能识别
- **表格识别** - 复杂表格内容精准提取
- **目录解析** - 自动识别文档层级结构

### 2. 🤖 商务应答智能生成

- **点对点应答** - 招标要求与企业能力自动匹配
- **内容推荐** - 基于历史案例的智能推荐
- **模板管理** - 可定制的应答模板库
- **批量处理** - 多个问题批量生成应答

### 3. 📚 企业知识库管理

- **多维分类** - 产品/服务/行业多维度组织
- **版本控制** - 文档版本历史追踪
- **权限管理** - 隐私分级与访问控制
- **智能搜索** - 关键词 + 语义双重检索

### 4. 🔍 向量搜索引擎

- **语义检索** - 基于 FAISS + Sentence-Transformers
- **混合搜索** - 关键词 + 向量组合检索
- **相似度排序** - 智能推荐最相关内容
- **实时索引** - 文档上传即可搜索

### 5. 📝 技术方案大纲生成

- **智能分析** - 技术要求自动解析
- **大纲生成** - 多级目录结构自动创建
- **内容填充** - 基于知识库的内容推荐

### 6. 📊 案例库管理

- **案例沉淀** - 历史投标案例统一管理
- **快速复用** - 相似项目快速检索
- **经验积累** - 成功案例知识提取

---

## 🏗️ 技术架构

### 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| **前端** | HTML5 + Bootstrap 5 + JavaScript | 响应式 UI，现代化交互 |
| **后端** | Flask 2.3.3 + Python 3.11+ | RESTful API，模块化设计 |
| **数据库** | SQLite 3 | 轻量级关系型数据库 |
| **向量引擎** | FAISS + Sentence-Transformers | 语义搜索与相似度匹配 |
| **AI 模型** | 通义千问 / GPT / DeepSeek | 多模型支持，可配置切换 |
| **文档解析** | PyMuPDF + python-docx + pdfplumber | 多格式文档处理 |
| **文本处理** | LangChain + tiktoken + jieba | 智能分块与中文分词 |
| **安全防护** | Flask-WTF (CSRF) + CORS | 跨站攻击防护 |

### 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                         用户界面层                            │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────┐  │
│  │ 文档管理 │ 知识库   │ 商务应答 │ 技术方案 │ 案例库   │  │
│  └──────────┴──────────┴──────────┴──────────┴──────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↕ RESTful API
┌─────────────────────────────────────────────────────────────┐
│                         业务逻辑层                            │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  文档解析引擎 │ AI 处理引擎 │ 向量搜索引擎 │ 知识管理  │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│                         数据存储层                            │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────┐  │
│  │ SQLite   │ 文件存储 │ FAISS    │ 向量索引 │ 配置管理 │  │
│  └──────────┴──────────┴──────────┴──────────┴──────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 快速开始

### 环境要求

- **Python**: 3.11 或更高版本
- **操作系统**: Windows / macOS / Linux
- **内存**: 建议 8GB+
- **磁盘空间**: 2GB+（包含模型文件）

### 安装步骤

#### 1. 克隆项目

```bash
git clone <repository-url>
cd zhongbiao
```

#### 2. 安装依赖

```bash
pip install -r requirements.txt
```

#### 3. 配置环境变量

复制示例配置文件：
```bash
cp ai_tender_system/.env.example ai_tender_system/.env
```

编辑 `.env` 文件，配置 API 密钥：
```ini
# AI 模型配置
QWEN_API_KEY=your_qwen_api_key_here
OPENAI_API_KEY=your_openai_api_key_here  # 可选
DEEPSEEK_API_KEY=your_deepseek_api_key_here  # 可选

# 应用配置
SECRET_KEY=your_secret_key_for_csrf_protection
DEBUG=False
```

#### 4. 初始化数据库

```bash
python -m ai_tender_system.database.init_db
```

#### 5. 启动应用

```bash
python -m ai_tender_system.web.app
```

#### 6. 访问系统

打开浏览器访问：[http://localhost:5000](http://localhost:5000)

**默认登录信息**（请立即修改）：
- 用户名：`admin`
- 密码：`admin123`

⚠️ **安全提示**：首次登录后请立即修改默认密码！

---

## 📦 功能模块

### 模块架构

```
ai_tender_system/
├── modules/                    # 核心业务模块
│   ├── business_response/      # 商务应答处理
│   ├── case_library/           # 案例库管理
│   ├── document_parser/        # 文档解析引擎
│   ├── knowledge_base/         # 知识库管理
│   ├── outline_generator/      # 技术方案大纲生成
│   ├── tender_info/            # 招标信息提取
│   ├── tender_processing/      # 标书处理流程
│   └── vector_engine/          # 向量搜索引擎
├── web/                        # Web 应用
│   ├── app.py                  # Flask 应用入口
│   ├── templates/              # HTML 模板
│   └── static/                 # 静态资源
├── common/                     # 公共工具
│   ├── config.py               # 配置管理
│   ├── database.py             # 数据库操作
│   └── llm_client.py           # AI 模型客户端
└── database/                   # 数据库相关
    └── *.sql                   # 数据库架构
```

### 主要 API 端点

| 端点 | 方法 | 功能 | CSRF 保护 |
|------|------|------|-----------|
| `/api/upload` | POST | 文件上传 | ✅ |
| `/api/extract-tender-info` | POST | 招标信息提取 | ✅ |
| `/api/process-business-response` | POST | 商务应答生成 | ✅ |
| `/api/knowledge-base/documents` | GET | 获取文档列表 | - |
| `/api/knowledge-base/documents` | POST | 上传文档 | ✅ |
| `/api/vector-search` | POST | 向量搜索 | ✅ |
| `/api/case-library/cases` | GET | 获取案例列表 | - |
| `/api/outline/generate` | POST | 生成技术方案大纲 | ✅ |

完整 API 文档：[docs/api.md](ai_tender_system/docs/architecture/api-interfaces.md)

---

## 📁 项目结构

```
zhongbiao/
├── ai_tender_system/              # 主应用目录
│   ├── modules/                   # 业务模块
│   │   ├── business_response/     # 商务应答
│   │   ├── case_library/          # 案例库
│   │   ├── document_parser/       # 文档解析
│   │   ├── knowledge_base/        # 知识库
│   │   ├── outline_generator/     # 大纲生成
│   │   ├── point_to_point/        # 点对点应答
│   │   ├── tender_info/           # 招标信息
│   │   ├── tender_processing/     # 标书处理
│   │   └── vector_engine/         # 向量引擎
│   ├── web/                       # Web 应用
│   │   ├── app.py                 # Flask 入口（3,248行）
│   │   ├── templates/             # 前端模板（7个）
│   │   └── static/                # 静态资源
│   │       ├── css/               # 样式文件
│   │       ├── js/                # JavaScript
│   │       └── vendor/            # 第三方库
│   ├── common/                    # 公共模块
│   │   ├── config.py              # 配置管理
│   │   ├── database.py            # 数据库操作
│   │   ├── llm_client.py          # AI 客户端
│   │   └── logger.py              # 日志系统
│   ├── database/                  # 数据库
│   │   ├── *.sql                  # SQL 架构文件
│   │   └── *.db                   # SQLite 数据库
│   ├── data/                      # 数据目录
│   │   ├── uploads/               # 上传文件
│   │   ├── output/                # 输出文件
│   │   └── logs/                  # 日志文件
│   ├── docs/                      # 文档中心
│   │   ├── README.md              # 文档导航
│   │   ├── architecture/          # 架构设计
│   │   └── implementation/        # 实施指南
│   └── .env.example               # 环境变量示例
├── requirements.txt               # Python 依赖
├── requirements_rag.txt           # RAG 相关依赖
├── README.md                      # 本文件
├── CSRF_PROTECTION_GUIDE.md       # CSRF 安全指南
└── *.md                           # 其他文档
```

---

## 📚 文档导航

### 📘 核心文档

- [系统架构设计](ai_tender_system/docs/README.md)
- [数据库架构](ai_tender_system/docs/architecture/database-schema.md)
- [API 接口文档](ai_tender_system/docs/architecture/api-interfaces.md)
- [向量搜索设计](ai_tender_system/docs/architecture/vector-search-design.md)

### 🔒 安全文档

- [CSRF 保护指南](CSRF_PROTECTION_GUIDE.md)
- [安全配置说明](ai_tender_system/docs/security/security-config.md)

### 📖 用户指南

- [快速入门指南](ai_tender_system/docs/user-guide/quick-start.md)
- [功能使用说明](ai_tender_system/docs/user-guide/features.md)
- [常见问题解答](ai_tender_system/docs/user-guide/faq.md)

### 🛠️ 开发文档

- [开发环境配置](ai_tender_system/docs/implementation/development-guide.md) 🚧
- [编码规范](ai_tender_system/docs/implementation/coding-standards.md) 🚧
- [测试策略](ai_tender_system/docs/implementation/testing-strategy.md) 🚧

### 📦 部署文档

- [部署指南](ai_tender_system/docs/implementation/deployment-guide.md) 🚧
- [Docker 部署](ai_tender_system/docs/deployment/docker.md) 🚧
- [生产环境配置](ai_tender_system/docs/deployment/production.md) 🚧

---

## 🛠️ 开发指南

### 开发环境设置

1. **安装开发依赖**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # 测试、格式化工具
   ```

2. **配置开发环境**
   ```bash
   export FLASK_ENV=development
   export DEBUG=True
   ```

3. **运行开发服务器**
   ```bash
   python -m ai_tender_system.web.app
   ```

### 代码风格

- **Python**: 遵循 [PEP 8](https://peps.python.org/pep-0008/)
- **格式化工具**: Black (line-length=120)
- **代码检查**: Flake8, Pylint
- **类型提示**: 使用 Type Hints（Python 3.11+）

### 提交规范

```bash
git commit -m "类型(范围): 简短描述

详细说明（可选）

BREAKING CHANGE: 破坏性更改说明（如有）
"
```

**类型**:
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建/工具链

### 分支策略

- `master`: 生产环境代码
- `develop`: 开发分支
- `feature/*`: 功能开发
- `bugfix/*`: Bug 修复
- `hotfix/*`: 紧急修复

---

## 🚢 部署说明

### 生产环境部署

#### 1. 使用 Docker（推荐）

```bash
# 构建镜像
docker build -t ai-tender-system .

# 运行容器
docker run -d \
  -p 5000:5000 \
  -v $(pwd)/data:/app/data \
  -e SECRET_KEY=your_secret_key \
  ai-tender-system
```

#### 2. 使用 docker-compose

```bash
docker-compose up -d
```

#### 3. 传统部署

```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境变量
export FLASK_ENV=production
export DEBUG=False
export SECRET_KEY=your_production_secret_key

# 使用 Gunicorn 运行
gunicorn -w 4 -b 0.0.0.0:5000 ai_tender_system.web.app:app
```

### 性能优化建议

- ✅ 使用 **Nginx** 作为反向代理
- ✅ 启用 **Redis** 缓存（可选）
- ✅ 配置 **CDN** 加速静态资源
- ✅ 数据库定期备份
- ✅ 监控与日志收集

---

## ❓ 常见问题

### Q1: 如何更换 AI 模型？

编辑 `ai_tender_system/common/config.py`，修改 `default_model` 配置：

```python
'default_model': 'qwen-max'  # 或 'gpt-4', 'deepseek-chat'
```

### Q2: 如何添加新的文档类型支持？

在 `ai_tender_system/modules/document_parser/` 中添加新的解析器：

```python
class NewFormatParser:
    def parse(self, file_path):
        # 解析逻辑
        return content
```

### Q3: 向量搜索速度慢怎么办？

1. 检查向量索引是否已创建
2. 优化分块大小（默认 500 tokens）
3. 考虑使用 GPU 加速（FAISS-GPU）

### Q4: 如何备份数据？

```bash
# 备份数据库
cp ai_tender_system/database/*.db /backup/

# 备份上传文件
cp -r ai_tender_system/data/uploads /backup/

# 备份向量索引
cp -r ai_tender_system/modules/data/chroma_db /backup/
```

### Q5: CSRF Token 错误怎么办？

查看 [CSRF_PROTECTION_GUIDE.md](CSRF_PROTECTION_GUIDE.md) 故障排除部分。

---

## 🤝 贡献指南

我们欢迎所有形式的贡献！

### 如何贡献

1. **Fork** 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'feat: Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 **Pull Request**

### 贡献类型

- 🐛 报告 Bug
- 💡 提出新功能建议
- 📝 改进文档
- 🔧 提交代码
- ✅ 编写测试
- 🌍 翻译

### 行为准则

- 尊重所有贡献者
- 建设性的讨论
- 遵循项目编码规范
- 详细描述 PR 内容

---

## 📊 项目统计

| 指标 | 数值 |
|------|------|
| **代码行数** | 50,000+ |
| **Python 模块** | 90+ |
| **API 端点** | 30+ |
| **前端页面** | 7 |
| **数据库表** | 15+ |
| **测试覆盖率** | 目标 80%+ 🚧 |

---

## 🗺️ 开发路线图

### ✅ 已完成

- [x] 招标文档智能解析
- [x] 企业知识库管理
- [x] 向量搜索引擎
- [x] 商务应答生成
- [x] 技术方案大纲生成
- [x] 案例库管理
- [x] CSRF 安全保护
- [x] 文档中心建设

### 🚧 进行中

- [ ] 完整的测试框架（pytest + coverage）
- [ ] 单元测试编写（目标 80%+ 覆盖率）
- [ ] 代码重构（app.py 模块化）
- [ ] Docker 容器化

### 📋 计划中

- [ ] JWT 身份认证
- [ ] API 限流保护
- [ ] 多租户支持
- [ ] 实时协作编辑
- [ ] 移动端适配
- [ ] 数据分析仪表板

---

## 📄 许可证

本项目采用 **MIT License** 许可证。

详见 [LICENSE](LICENSE) 文件。

---

## 📞 联系方式

- **项目维护者**: AI标书系统开发团队
- **问题反馈**: [GitHub Issues](https://github.com/your-org/ai-tender-system/issues)
- **功能建议**: [GitHub Discussions](https://github.com/your-org/ai-tender-system/discussions)

---

## 🙏 致谢

感谢以下开源项目：

- [Flask](https://flask.palletsprojects.com/) - Web 框架
- [FAISS](https://github.com/facebookresearch/faiss) - 向量搜索
- [Sentence-Transformers](https://www.sbert.net/) - 语义编码
- [LangChain](https://www.langchain.com/) - LLM 应用框架
- [Bootstrap](https://getbootstrap.com/) - UI 框架
- [PyMuPDF](https://pymupdf.readthedocs.io/) - PDF 处理

---

<div align="center">

**⭐ 如果这个项目对您有帮助，请给我们一个 Star！**

Made with ❤️ by AI Tender System Team

</div>
