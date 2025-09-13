#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一字段映射功能测试
测试新实现的字段映射逻辑是否正确工作
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent))

from modules.business_response.info_filler import InfoFiller

def test_unified_field_mapping():
    """测试统一字段映射功能"""
    print("=" * 60)
    print("🧪 统一字段映射功能测试")
    print("=" * 60)

    # 创建InfoFiller实例
    filler = InfoFiller()

    # 模拟输入数据
    company_info = {
        'companyName': '智慧足迹数据科技有限公司',
        'address': '',  # 主地址为空
        'registeredAddress': '北京市朝阳区xxx路xxx号',  # 注册地址有值
        'officeAddress': '北京市海淀区yyy路yyy号',  # 办公地址有值
        'phone': '',  # phone为空
        'fixedPhone': '010-12345678',  # fixedPhone有值
        'email': 'contact@smartsteps.com',
        'fax': '010-87654321',
        'legalRepresentative': '张三',
        'establishDate': '2020年1月1日'
    }

    project_info = {
        'projectName': 'AI标书生成系统项目',
        'projectNumber': 'AI-2025-001',
        'purchaserName': '',  # 采购人名称为空
        'projectOwner': '某市政府采购中心',  # 项目业主有值
        'date': '2025年1月15日'
    }

    print("\n📋 输入数据:")
    print("公司信息:")
    for key, value in company_info.items():
        status = "✅" if value else "❌"
        print(f"  {status} {key}: '{value}'")

    print("\n项目信息:")
    for key, value in project_info.items():
        status = "✅" if value else "❌"
        print(f"  {status} {key}: '{value}'")

    # 测试统一字段映射
    print("\n🔧 执行统一字段映射...")
    unified_mapping = filler._create_unified_field_mapping(company_info, project_info)

    print("\n📊 映射结果验证:")

    # 测试关键映射逻辑
    test_cases = [
        {
            'field': 'companyName',
            'expected': '智慧足迹数据科技有限公司',
            'description': '公司名称直接映射'
        },
        {
            'field': 'address',
            'expected': '北京市朝阳区xxx路xxx号',  # 应该取registeredAddress
            'description': '地址多源映射: address(空) → registeredAddress'
        },
        {
            'field': 'phone',
            'expected': '010-12345678',  # 应该取fixedPhone
            'description': '电话多源映射: phone(空) → fixedPhone'
        },
        {
            'field': 'purchaserName',
            'expected': '某市政府采购中心',  # 应该取projectOwner
            'description': '采购人多源映射: purchaserName(空) → projectOwner'
        },
        {
            'field': 'projectName',
            'expected': 'AI标书生成系统项目',
            'description': '项目名称直接映射'
        }
    ]

    all_passed = True

    for test_case in test_cases:
        field = test_case['field']
        expected = test_case['expected']
        description = test_case['description']

        actual = unified_mapping.get(field, '')

        if actual == expected:
            print(f"  ✅ {description}: '{actual}'")
        else:
            print(f"  ❌ {description}: 期望 '{expected}', 实际 '{actual}'")
            all_passed = False

    # 输出完整映射结果
    print(f"\n📋 完整映射结果 (共{len(unified_mapping)}个字段):")
    for key, value in sorted(unified_mapping.items()):
        print(f"  {key}: '{value}'")

    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 测试通过! 统一字段映射功能正常工作")
    else:
        print("❌ 测试失败! 发现映射逻辑问题")
    print("=" * 60)

    return all_passed

def test_mapping_priority():
    """测试映射优先级逻辑"""
    print("\n🧪 映射优先级测试")
    print("-" * 40)

    filler = InfoFiller()

    # 测试地址优先级: address > registeredAddress > officeAddress
    test_data = {
        'address': '主地址',
        'registeredAddress': '注册地址',
        'officeAddress': '办公地址'
    }

    result = filler._create_unified_field_mapping(test_data, {})
    expected = '主地址'  # 应该取第一优先级
    actual = result.get('address', '')

    if actual == expected:
        print(f"✅ 地址优先级测试通过: '{actual}'")
    else:
        print(f"❌ 地址优先级测试失败: 期望 '{expected}', 实际 '{actual}'")

    # 测试空值回退逻辑
    test_data2 = {
        'address': '',  # 主地址为空
        'registeredAddress': '注册地址',
        'officeAddress': '办公地址'
    }

    result2 = filler._create_unified_field_mapping(test_data2, {})
    expected2 = '注册地址'  # 应该回退到第二优先级
    actual2 = result2.get('address', '')

    if actual2 == expected2:
        print(f"✅ 空值回退测试通过: '{actual2}'")
        return True
    else:
        print(f"❌ 空值回退测试失败: 期望 '{expected2}', 实际 '{actual2}'")
        return False

if __name__ == "__main__":
    success1 = test_unified_field_mapping()
    success2 = test_mapping_priority()

    if success1 and success2:
        print("\n🎊 所有测试通过! 统一字段映射功能实现正确")
        exit(0)
    else:
        print("\n💥 测试失败! 需要修复映射逻辑问题")
        exit(1)