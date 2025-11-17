# Azure Form Recognizer 配置指南

## 前提条件

1. Azure订阅账号
2. Azure Form Recognizer资源

## 配置步骤

### 1. 创建Azure Form Recognizer资源

1. 登录 [Azure Portal](https://portal.azure.com/)
2. 创建新资源 → 选择 "Azure AI services"  → "Form Recognizer"
3. 配置资源:
   - **订阅**: 选择你的Azure订阅
   - **资源组**: 创建新的或选择现有的资源组
   - **区域**: 选择靠近你的区域(如East Asia、Southeast Asia)
   - **名称**: 输入资源名称(如`tender-doc-parser`)
   - **定价层**: 选择Free F0(每月1,000页免费)或Standard S0

4. 点击"创建"并等待部署完成

### 2. 获取API密钥和端点

部署完成后:
1. 进入资源页面
2. 在左侧菜单选择 "Keys and Endpoint"
3. 复制以下信息:
   - **Endpoint**: 形如 `https://your-resource-name.cognitiveservices.azure.com/`
   - **KEY 1** 或 **KEY 2**: 选择其中一个

### 3. 配置环境变量

#### macOS/Linux:
```bash
export AZURE_FORM_RECOGNIZER_ENDPOINT="https://your-resource-name.cognitiveservices.azure.com/"
export AZURE_FORM_RECOGNIZER_KEY="your-api-key-here"
```

将这些命令添加到 `~/.zshrc` 或 `~/.bashrc` 以持久化:
```bash
echo 'export AZURE_FORM_RECOGNIZER_ENDPOINT="https://your-resource-name.cognitiveservices.azure.com/"' >> ~/.zshrc
echo 'export AZURE_FORM_RECOGNIZER_KEY="your-api-key-here"' >> ~/.zshrc
source ~/.zshrc
```

#### Windows (PowerShell):
```powershell
$env:AZURE_FORM_RECOGNIZER_ENDPOINT = "https://your-resource-name.cognitiveservices.azure.com/"
$env:AZURE_FORM_RECOGNIZER_KEY = "your-api-key-here"
```

持久化(系统环境变量):
1. 右键"此电脑" → 属性 → 高级系统设置 → 环境变量
2. 在"用户变量"中添加:
   - 变量名: `AZURE_FORM_RECOGNIZER_ENDPOINT`
   - 变量值: 你的endpoint
   - 变量名: `AZURE_FORM_RECOGNIZER_KEY`
   - 变量值: 你的API key

### 4. 安装Python依赖

```bash
pip install azure-ai-formrecognizer
```

#### 可选:Word转PDF工具(三选一)

**方案A: docx2pdf (推荐,Windows/Mac)**
```bash
pip install docx2pdf
```

**方案B: LibreOffice (跨平台)**
- macOS: `brew install libreoffice`
- Ubuntu/Debian: `sudo apt-get install libreoffice`
- Windows: 下载安装 [LibreOffice](https://www.libreoffice.org/download/download/)

**方案C: unoconv**
```bash
pip install unoconv
```

### 5. 验证配置

运行测试脚本:
```bash
python -c "from ai_tender_system.modules.tender_processing.azure_parser import is_azure_available; print('Azure可用' if is_azure_available() else 'Azure未配置')"
```

或使用内置测试:
```bash
cd ai_tender_system/modules/tender_processing
python azure_parser.py
```

输出应显示: `Azure Form Recognizer 配置已就绪`

### 6. 在应用中使用

配置完成后,目录解析对比工具会自动启用Azure方法。上传Word文档后,系统会:
1. 自动将Word转换为PDF
2. 调用Azure Form Recognizer API分析文档
3. 提取章节结构并与其他方法对比

## 费用说明

- **Free F0层**: 每月1,000页免费
- **Standard S0层**:
  - 前1,000页: $1.50/页
  - 后续页面: 逐渐降低

## 故障排查

### 问题1: 提示"Azure Form Recognizer 未配置"
- 检查环境变量是否正确设置: `echo $AZURE_FORM_RECOGNIZER_ENDPOINT`
- 重启终端或IDE

### 问题2: Word转PDF失败
- 确保已安装docx2pdf或LibreOffice
- Windows用户: 确保LibreOffice在PATH中

### 问题3: API调用失败
- 检查endpoint格式(需要以`/`结尾)
- 检查API key是否正确
- 确认Azure订阅处于活跃状态
- 检查配额是否用完

## 参考资料

- [Azure Form Recognizer 文档](https://learn.microsoft.com/zh-cn/azure/ai-services/document-intelligence/)
- [Python SDK文档](https://learn.microsoft.com/zh-cn/python/api/overview/azure/ai-formrecognizer-readme)
