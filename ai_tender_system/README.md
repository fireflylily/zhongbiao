# AI标书系统 v2.0

## 🎯 系统概述

AI标书系统v2.0是一个重构后的统一Web应用，整合了招标信息提取、点对点应答、技术方案生成等所有功能。

### 主要改进

- ✅ **统一架构**: 合并原有的双服务为单一Web服务
- ✅ **模块化设计**: 清晰的模块边界和职责分离  
- ✅ **配置统一**: 统一的配置管理和API密钥处理
- ✅ **日志优化**: 统一的日志系统和错误处理
- ✅ **代码复用**: 消除重复代码，建立共享组件库
- ✅ **增强验证**: 完整的错误处理和状态验证机制

## 📁 目录结构

```
ai_tender_system/
├── web/                   # Web应用
│   ├── app.py            # 主应用文件
│   ├── templates/        # HTML模板
│   └── static/           # 静态资源
├── modules/              # 业务模块
│   ├── tender_info/      # 招标信息提取
│   ├── point_to_point/   # 点对点应答
│   └── tech_proposal/    # 技术方案生成
├── common/               # 共享组件
│   ├── config.py         # 统一配置
│   ├── logger.py         # 日志管理
│   ├── exceptions.py     # 异常处理
│   └── utils.py          # 工具函数
├── data/                 # 数据目录
│   ├── uploads/          # 上传文件
│   ├── outputs/          # 输出文件
│   ├── configs/          # 配置文件
│   └── logs/             # 日志文件
├── run.py               # 启动脚本
└── README.md            # 说明文档
```

## 🚀 快速启动

### 1. 环境要求

- Python 3.8+
- 必要的Python包:
  ```bash
  pip install flask flask-cors requests PyPDF2 python-docx configparser
  ```

### 2. 启动系统

```bash
cd ai_tender_system
python3 run.py
```

### 3. 访问系统

- 主页: http://localhost:8082
- 系统状态: http://localhost:8082/system_status.html
- API健康检查: http://localhost:8082/api/health

## 🔧 配置说明

### API配置

系统使用统一的API配置，支持环境变量覆盖：

```python
# 环境变量配置
export DEFAULT_API_KEY="your-api-key"
export API_ENDPOINT="https://api.oaipro.com/v1/chat/completions"
export MODEL_NAME="gpt-5"
export WEB_PORT="8082"
```

### 文件路径配置

- 上传目录: `data/uploads/`
- 输出目录: `data/outputs/`
- 配置目录: `data/configs/`
- 日志目录: `data/logs/`

## 📋 功能特性

### 招标信息提取
- 支持PDF、Word、文本文件
- 提取项目基本信息
- 识别资质要求
- 分析技术评分标准
- 分步处理和一键处理

### 点对点应答
- 商务应答模板填充
- 智能公司信息匹配
- 文档处理和格式化
- 表格分析和处理

### 技术方案生成
- 基于招标要求生成方案
- 智能内容匹配
- 多格式输出支持

## 🔍 API文档

### 核心API端点

- `GET /api/health` - 系统健康检查
- `GET /api/config` - 获取API配置
- `POST /extract-tender-info` - 招标信息提取
- `POST /process-business-response` - 商务应答处理
- `POST /generate-proposal` - 技术方案生成

### 招标信息提取API

```bash
# 完整提取
curl -X POST http://localhost:8082/extract-tender-info \
  -F "file=@tender.pdf" \
  -F "api_key=your-api-key"

# 分步提取
curl -X POST http://localhost:8082/extract-tender-info-step \
  -H "Content-Type: application/json" \
  -d '{"step": "1", "file_path": "path/to/file", "api_key": "your-key"}'
```

## 🧪 测试验证

### 1. 模块测试

```bash
cd ai_tender_system

# 测试配置系统
python3 -c "from common.config import get_config; print('配置正常')"

# 测试日志系统  
python3 -c "from common.logger import get_module_logger; print('日志正常')"

# 测试招标信息提取
python3 -c "from modules.tender_info.extractor import TenderInfoExtractor; print('招标模块正常')"

# 测试点对点应答
python3 -c "from modules.point_to_point.processor import PointToPointProcessor; print('应答模块正常')"
```

### 2. Web应用测试

```bash
# 测试Web应用创建
python3 -c "from web.app import create_app; app = create_app(); print('Web应用正常')"

# 测试API健康检查
curl http://localhost:8082/api/health
```

## 🔒 安全考虑

- API密钥通过环境变量或配置文件管理
- 文件上传类型验证
- 路径遍历防护
- 错误信息过滤

## 📊 监控和日志

### 日志文件位置
- 主日志: `data/logs/ai_tender_system.log`
- 模块日志: `data/logs/{module_name}.log`
- 错误日志: `data/logs/errors.log`

### 系统监控
- 访问 `/system_status.html` 查看系统状态
- 使用 `/api/health` 进行健康检查
- 日志轮转自动管理

## 🆘 故障排除

### 常见问题

1. **模块导入失败**
   - 检查Python路径设置
   - 确认依赖包安装完整

2. **API调用失败**
   - 验证API密钥配置
   - 检查网络连接
   - 查看日志文件

3. **文件处理错误**
   - 确认文件格式支持
   - 检查文件完整性
   - 验证文件权限

### 日志分析

```bash
# 查看最新日志
tail -f data/logs/ai_tender_system.log

# 搜索错误
grep -i error data/logs/*.log

# 查看特定模块日志
tail -f data/logs/tender_info.log
```

## 🔄 维护和更新

### 日常维护
- 定期清理临时文件
- 监控日志文件大小
- 检查系统性能

### 备份建议
- 定期备份配置文件
- 保存重要的输出结果
- 备份公司信息数据

## 📞 技术支持

如有问题，请按以下顺序排查：

1. 查看系统状态页面
2. 检查日志文件
3. 验证配置设置
4. 测试API连接

---

**AI标书系统 v2.0** - 重构完成于 2025年9月10日