# 环境变量文件说明

## 📁 项目环境变量文件清单

### 1. `ai_tender_system/.env` ✅ **主配置文件**

**位置**: `/ai_tender_system/.env`
**用途**: 应用运行时实际使用的环境变量配置
**状态**: ✅ 已配置，包含所有API密钥
**Git状态**: ✅ 已忽略（不会提交到版本控制）

**包含的配置**:
```ini
# API配置
- DEFAULT_API_KEY              # 默认API密钥
- API_ENDPOINT                 # API端点
- MODEL_NAME                   # 模型名称

# 多模型API配置
- OPENAI_API_KEY              # OpenAI API密钥
- ACCESS_TOKEN                # 联通元景访问令牌
- SHIHUANG_API_KEY            # 始皇API密钥

# Azure服务配置
- AZURE_FORM_RECOGNIZER_KEY   # Azure文档智能密钥
- AZURE_FORM_RECOGNIZER_ENDPOINT

# Google Gemini配置 (新增)
- GEMINI_API_KEY              # ✅ Gemini AI解析器密钥

# Web服务配置
- WEB_HOST                    # 服务绑定地址
- WEB_PORT                    # 服务端口 (8110)
- DEBUG                       # 调试模式

# 安全配置
- SECRET_KEY                  # Flask会话密钥
- MAX_UPLOAD_SIZE            # 最大上传文件大小

# OCR配置
- ENABLE_OCR                 # 是否启用OCR
- OCR_USE_GPU                # 是否使用GPU加速

# 企业征信API配置
- ENTERPRISE_CREDIT_BASE_URL
- ENTERPRISE_CREDIT_API_KEY
```

---

### 2. `.env.production.example` ℹ️ **生产环境模板**

**位置**: `/.env.production.example`
**用途**: 生产环境配置模板（示例文件）
**状态**: 📖 仅作参考，未实际使用
**Git状态**: ✅ 已提交（作为配置模板）

**用途说明**:
- 提供生产环境部署时的配置参考
- 包含完整的配置项说明和安全建议
- 部署时可复制为 `.env` 并填写实际值

**使用方法**:
```bash
# 生产环境部署时
cp .env.production.example .env
# 然后编辑 .env 填写实际配置值
```

---

### 3. `frontend/node_modules/plyr/.env` 🔧 **第三方包文件**

**位置**: `/frontend/node_modules/plyr/.env`
**用途**: npm包 `plyr` 自带的配置文件
**状态**: 🔧 第三方包内部文件
**Git状态**: ✅ 已忽略（node_modules整个目录被忽略）

**说明**:
- 这是npm包内部的配置文件
- 不需要修改或关注
- `node_modules` 目录通过 `.gitignore` 自动忽略

---

## 🎯 环境变量文件结构总结

```
项目根目录/
│
├── .env.production.example      # 📖 生产环境配置模板（参考用）
│                                # Git: 已提交 ✅
│
├── ai_tender_system/
│   └── .env                     # ✅ 实际使用的配置文件
│                                # Git: 已忽略 ✅
│                                # 包含所有API密钥（含Gemini）
│
└── frontend/
    └── node_modules/
        └── plyr/
            └── .env             # 🔧 第三方包文件（忽略）
                                 # Git: 已忽略 ✅
```

---

## ✅ Git忽略配置

`.gitignore` 文件已正确配置，确保敏感配置不会提交：

```gitignore
# Ignore environment files with sensitive data
.env
.env.local
ai_tender_system/.env
*/.env
```

**验证方法**:
```bash
# 检查.env文件是否被忽略
git status

# 应该看不到 ai_tender_system/.env 文件
# 如果看到了，说明忽略配置有问题
```

---

## 📝 环境变量管理最佳实践

### ✅ 正确做法

1. **开发环境**: 使用 `ai_tender_system/.env`（已配置）
2. **生产环境**: 复制 `.env.production.example` 并修改
3. **API密钥**: 只在 `.env` 文件中配置，不要硬编码
4. **版本控制**: `.env` 文件永远不提交到Git

### ❌ 避免的错误

1. ❌ 不要在代码中硬编码API密钥
2. ❌ 不要将 `.env` 文件提交到Git
3. ❌ 不要在多个位置维护重复的配置
4. ❌ 不要在公开场合分享 `.env` 文件内容

---

## 🔐 安全建议

### 1. 定期更换API密钥
```bash
# 如果怀疑密钥泄露，立即：
# 1. 在API提供商后台撤销旧密钥
# 2. 生成新密钥
# 3. 更新 .env 文件
# 4. 重启应用
```

### 2. 使用不同的密钥环境
```bash
# 开发环境: ai_tender_system/.env
GEMINI_API_KEY=开发环境密钥

# 生产环境: 服务器上的.env
GEMINI_API_KEY=生产环境密钥
```

### 3. 备份配置（安全存储）
```bash
# 将配置文件加密备份到安全位置
# 不要存储在公共云盘或版本控制系统
```

---

## 🚀 快速检查清单

在提交代码前，请确认：

- [ ] `ai_tender_system/.env` 文件存在且包含所需配置
- [ ] `.gitignore` 正确配置，`.env` 文件被忽略
- [ ] 运行 `git status` 确认没有 `.env` 文件待提交
- [ ] 代码中没有硬编码的API密钥
- [ ] 所有API密钥都已正确配置且可用

---

## 📞 常见问题

### Q1: 为什么 `.env` 在 `ai_tender_system` 目录而不是根目录？

**A**: 这是合理的设计：
- ✅ 与应用代码在同一目录，便于管理
- ✅ 符合Python项目的常见做法
- ✅ 前后端配置分离（前端有自己的配置）

### Q2: `.env.production.example` 要不要删除？

**A**: 不要删除！
- ✅ 作为生产环境部署的配置参考
- ✅ 团队成员可以参考快速配置
- ✅ 提交到Git作为文档

### Q3: 如何添加新的环境变量？

**A**: 在 `ai_tender_system/.env` 中添加即可：
```bash
# 1. 编辑文件
vim ai_tender_system/.env

# 2. 添加新配置
NEW_CONFIG=value

# 3. 重启应用使配置生效
python -m ai_tender_system.web.app
```

### Q4: 团队协作时如何同步配置？

**A**:
1. ❌ 不要直接分享 `.env` 文件（包含敏感信息）
2. ✅ 更新 `.env.production.example` 添加新配置项说明
3. ✅ 通过安全渠道（如加密邮件）分享API密钥
4. ✅ 在文档中说明必需的配置项

---

## ✅ 总结

当前项目的环境变量配置**已经很规范**：

1. ✅ 主配置文件 `ai_tender_system/.env` 位置合理
2. ✅ 生产环境模板 `.env.production.example` 提供参考
3. ✅ `.gitignore` 正确配置，敏感配置不会泄露
4. ✅ Gemini API密钥已正确添加

**无需进一步整理，当前结构最佳！** 🎉
