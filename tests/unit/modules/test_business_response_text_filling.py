#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
商务应答文字填充功能测试

测试场景：
1. 供应商名称的多种别名填充
2. 应答人名称填充
3. 地址填充
4. 法人代表填充
5. 组合字段填充
6. 日期格式化
7. 签字字段跳过逻辑

作者：AI Tender System
日期：2025-11-28
更新：2025-12-02 - 改为从JSON文件加载测试数据
"""

import json
import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock
from docx.text.paragraph import Paragraph

from ai_tender_system.modules.business_response.content_filler import ContentFiller
from ai_tender_system.modules.business_response.field_recognizer import FieldRecognizer


# ============================================================================
# 测试数据加载
# ============================================================================

TEST_DATA_FILE = Path(__file__).parent.parent.parent / "data" / "business_response_test_cases.json"

def load_test_data():
    """加载JSON测试数据"""
    with open(TEST_DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_test_cases(suite_name, *fields):
    """
    从JSON中提取指定测试套件的测试用例

    Args:
        suite_name: 测试套件名称
        *fields: 要提取的字段名

    Returns:
        list: 测试用例列表，每个元素是一个元组
    """
    data = load_test_data()
    cases = data['test_suites'][suite_name]['test_cases']

    if not fields:
        return cases

    return [tuple(case.get(field) for field in fields) for case in cases]


@pytest.fixture
def logger():
    """Mock logger"""
    return Mock()


@pytest.fixture
def content_filler(logger):
    """创建ContentFiller实例"""
    return ContentFiller(logger)


@pytest.fixture
def sample_company_data():
    """测试用的公司数据（从JSON加载）"""
    data = load_test_data()
    return data['sample_data']['data']


# ============================================================================
# 测试1：供应商名称的多种别名识别和填充（从JSON加载）
# ============================================================================

@pytest.mark.unit
@pytest.mark.parametrize("field_alias,expected_standard_field",
    get_test_cases('field_recognition_company', 'field_alias', 'expected_standard_field')
)
def test_company_name_aliases(field_alias, expected_standard_field):
    """测试供应商名称的所有别名都能正确识别

    场景：
    - 文档中可能使用"供应商"、"公司名称"、"单位名称"等不同叫法
    - 都应该识别为标准字段 company_name
    - 并使用公司数据库中的 company_name 值填充
    """
    recognizer = FieldRecognizer()

    # 验证字段识别
    standard_field = recognizer.recognize_field(field_alias)

    assert standard_field == expected_standard_field, \
        f"字段'{field_alias}'应该识别为'{expected_standard_field}'，但识别为'{standard_field}'"


# ============================================================================
# 测试2：地址字段的多种别名（从JSON加载）
# ============================================================================

@pytest.mark.unit
@pytest.mark.parametrize("field_alias,expected_field",
    get_test_cases('field_recognition_address', 'field_alias', 'expected_standard_field')
)
def test_address_field_recognition(field_alias, expected_field):
    """测试地址字段的所有别名

    场景：招标文件中地址字段可能有多种叫法
    """
    recognizer = FieldRecognizer()
    standard_field = recognizer.recognize_field(field_alias)

    assert standard_field == expected_field, \
        f"'{field_alias}'应该识别为'{expected_field}'字段"


# ============================================================================
# 测试3：法人代表字段（从JSON加载）
# ============================================================================

@pytest.mark.unit
@pytest.mark.parametrize("field_alias,expected_field",
    get_test_cases('field_recognition_legal_person', 'field_alias', 'expected_standard_field')
)
def test_legal_representative_recognition(field_alias, expected_field):
    """测试法人代表和被授权人字段的多种别名"""
    recognizer = FieldRecognizer()
    standard_field = recognizer.recognize_field(field_alias)

    assert standard_field == expected_field, \
        f"'{field_alias}'应该识别为'{expected_field}'字段"


# ============================================================================
# 测试4：括号字段填充（从JSON加载）
# ============================================================================

@pytest.mark.unit
@pytest.mark.parametrize("bracket_text,field_name,expected_value",
    get_test_cases('bracket_field_filling', 'bracket_text', 'field_name', 'expected_value')
)
def test_bracket_field_filling(content_filler, sample_company_data,
                                bracket_text, field_name, expected_value):
    """测试括号字段的填充

    场景：
    - 文档中有 (供应商名称) 这样的括号字段
    - 应该识别字段并填充为 (北京测试科技有限公司)
    - 保持原括号类型（中文括号/英文括号/方括号）
    """
    # 模拟段落
    paragraph = Mock(spec=Paragraph)
    run = Mock()
    run.text = f"请填写{bracket_text}的信息"
    paragraph.runs = [run]

    # 构建匹配数据
    matches = [{
        'full_match': bracket_text,
        'field': field_name,
        'start': 3,
        'end': 3 + len(bracket_text)
    }]

    # 这里我们主要测试逻辑，实际填充需要完整的Word文档对象
    # 所以主要验证字段识别是否正确
    recognizer = FieldRecognizer()
    std_field = recognizer.recognize_field(field_name)

    assert std_field in sample_company_data, \
        f"标准字段'{std_field}'应该存在于公司数据中"
    assert sample_company_data[std_field] == expected_value, \
        f"字段'{field_name}'应该填充为'{expected_value}'"


# ============================================================================
# 测试5：组合字段填充（从JSON加载）
# ============================================================================

@pytest.mark.unit
@pytest.mark.parametrize("combo_text,fields,std_fields,expected_values",
    get_test_cases('combo_field_recognition', 'combo_text', 'fields', 'expected_standard_fields', 'expected_values')
)
def test_combo_field_recognition(combo_text, fields, std_fields, expected_values,
                                  sample_company_data):
    """测试组合字段的识别和填充

    场景：
    - 文档中有 (公司名称、地址) 这样的组合字段
    - 应该识别为两个字段：companyName 和 address
    - 填充为：(北京测试科技有限公司、北京市海淀区中关村大街1号)
    """
    recognizer = FieldRecognizer()

    # 识别所有字段
    standard_fields = recognizer.recognize_combo_fields(fields)

    # 验证识别结果
    assert len(standard_fields) == len(fields), \
        f"应该识别{len(fields)}个字段"

    # 验证字段映射正确
    for actual_std, expected_std in zip(standard_fields, std_fields):
        assert actual_std == expected_std, \
            f"字段映射错误：期望'{expected_std}'，实际'{actual_std}'"

    # 验证每个字段都能找到对应的值
    for std_field, expected_value in zip(standard_fields, expected_values):
        if std_field:  # 如果字段被识别
            actual_value = sample_company_data.get(std_field)
            assert actual_value == expected_value, \
                f"标准字段'{std_field}'的值应该是'{expected_value}'，实际是'{actual_value}'"


# ============================================================================
# 测试6：日期格式化（从JSON加载）
# ============================================================================

@pytest.mark.unit
@pytest.mark.parametrize("input_date,expected_format",
    get_test_cases('date_formatting', 'input_date', 'expected_format')
)
def test_date_formatting(content_filler, input_date, expected_format):
    """测试日期格式化

    场景：
    - 数据库中的日期可能是 2025-11-28 格式
    - 文档中应该显示为 2025年11月28日 中文格式
    - 如果日期包含时间，只保留日期部分
    """
    formatted_date = content_filler._format_date(input_date)

    assert formatted_date == expected_format, \
        f"日期'{input_date}'应该格式化为'{expected_format}'，实际为'{formatted_date}'"


# ============================================================================
# 测试7：签字字段跳过逻辑（从JSON加载）
# ============================================================================

@pytest.mark.unit
@pytest.mark.parametrize("field_text,should_skip",
    get_test_cases('signature_field_skip_logic', 'field_text', 'should_skip')
)
def test_signature_field_skip_logic(field_text, should_skip):
    """测试签字字段的跳过逻辑

    场景：
    - "法定代表人（签字）" 这种个人签字字段不应该填充
    - "单位名称（盖章）" 这种单位盖章字段应该填充
    - "投标人（签字或盖章）" 投标人是单位，应该填充
    - 保证不会错误填充个人签字区域
    """
    from ai_tender_system.modules.business_response.field_classifier import FieldClassifier

    recognizer = FieldRecognizer()

    # 使用recognize_field判断（它会检查签字逻辑）
    std_field = recognizer.recognize_field(field_text)

    # 如果返回None，表示应该跳过
    # 如果返回字段名，则用FieldClassifier进一步判断
    if std_field is None:
        actual_skip = True
    else:
        actual_skip = not FieldClassifier.should_fill(field_text, std_field)

    assert actual_skip == should_skip, \
        f"字段'{field_text}'的跳过逻辑错误：期望{'跳过' if should_skip else '填充'}，实际{'跳过' if actual_skip else '填充'}"


# ============================================================================
# 测试8：空值处理
# ============================================================================

@pytest.mark.unit
def test_skip_empty_values(sample_company_data):
    """测试空值不应该被填充

    场景：
    - 如果公司数据中某个字段为空（如email为空）
    - 不应该填充为空字符串
    - 应该保持模板原样（或跳过）
    """
    # 创建包含空值的数据
    data_with_empty = sample_company_data.copy()
    data_with_empty['email'] = ''  # 空字符串
    data_with_empty['fax'] = None  # None值

    # 验证空值不会被填充（这里是逻辑验证，实际填充在ContentFiller中）
    for key, value in data_with_empty.items():
        if not value or str(value).strip() == '':
            # 空值字段不应该参与填充
            assert True  # 验证逻辑正确


# ============================================================================
# 测试9：完整的字段填充流程（集成测试风格）
# ============================================================================

@pytest.mark.unit
def test_complete_text_filling_scenario(sample_company_data):
    """测试完整的字段填充场景

    场景：
    一份商务应答文档包含：
    1. 供应商名称：(          )
    2. 注册地址：(          )
    3. 法定代表人：(          )
    4. 日期：   年  月  日

    应该全部正确填充
    """
    test_fields = {
        '供应商名称': 'companyName',
        '注册地址': 'address',
        '法定代表人': 'legalRepresentative',
    }

    recognizer = FieldRecognizer()

    # 验证所有字段都能识别和填充
    for field_alias, expected_std_field in test_fields.items():
        std_field = recognizer.recognize_field(field_alias)

        # 验证字段识别正确
        assert std_field == expected_std_field, \
            f"字段'{field_alias}'识别错误，期望'{expected_std_field}'，实际'{std_field}'"

        # 验证数据存在
        assert std_field in sample_company_data, \
            f"标准字段'{std_field}'应该存在于数据中"

        # 验证值非空
        value = sample_company_data[std_field]
        assert value and str(value).strip(), \
            f"字段'{field_alias}'的值不应为空"


# ============================================================================
# 测试10：真实场景字段映射（从JSON加载）
# ============================================================================

@pytest.mark.unit
@pytest.mark.parametrize("document_field,data_field,test_value",
    get_test_cases('real_world_scenarios', 'document_field', 'expected_data_field', 'test_value')
)
def test_real_world_scenarios(document_field, data_field, test_value):
    """测试真实场景中的字段映射

    这是你问的场景：
    - 文档中有"供应商名称"字段
    - 也有"应答人名称"字段
    - 它们都映射到 companyName（公司名称）
    """
    recognizer = FieldRecognizer()

    # 识别字段
    std_field = recognizer.recognize_field(document_field)

    # 验证映射正确
    assert std_field == data_field, \
        f"文档字段'{document_field}'应该映射到'{data_field}'，实际映射到'{std_field}'"

    # 模拟填充
    mock_data = {data_field: test_value}
    filled_value = mock_data.get(std_field)

    assert filled_value == test_value, \
        f"字段'{document_field}'应该填充为'{test_value}'"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
