# 测试Fixtures说明

本目录包含测试用的示例数据和文件。

## 📁 目录结构

```
tests/fixtures/
├── README.md                   # 本文件
├── company_data.json           # 测试用公司数据
├── sample_tender.docx          # 测试用招标文件（待添加）
├── sample_template.docx        # 测试用商务应答模板（待添加）
└── qualifications/             # 测试用资质文件（待添加）
    ├── business_license.jpg
    ├── iso9001.pdf
    ├── legal_id_front.jpg
    ├── legal_id_back.jpg
    ├── auth_id_front.jpg
    └── auth_id_back.jpg
```

## 📝 使用方法

### 在测试中使用fixtures

```python
import pytest
import json
from pathlib import Path

@pytest.fixture
def test_company_data():
    """加载测试用公司数据"""
    fixture_path = Path(__file__).parent.parent / 'fixtures' / 'company_data.json'
    with open(fixture_path, 'r', encoding='utf-8') as f:
        return json.load(f)['test_company_1']

def test_business_response(test_company_data):
    """使用fixture数据测试商务应答"""
    result = generate_business_response(test_company_data)
    assert result['success'] == True
```

## 🔧 添加新的测试文件

如果需要添加真实的Word文档用于测试：

1. 准备一个简单的招标文件：`sample_tender.docx`
2. 准备一个商务应答模板：`sample_template.docx`
3. 放在fixtures目录下
4. 在测试中使用

**注意**: 不要提交大文件到git，使用.gitignore排除大文件。

## 📊 当前可用的fixtures

- ✅ `company_data.json` - 2个测试公司数据
- ⚠️ Word文档 - 待添加
- ⚠️ 资质图片 - 待添加

## 🎯 优先级

**立即需要**:
- [ ] sample_template.docx - 用于测试商务应答生成
- [ ] 1-2个测试用资质图片

**可选**:
- [ ] sample_tender.docx - 用于测试文档解析
- [ ] 完整的资质文件集
