#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试表格解析功能
验证修复后的评分表格读取效果
"""

import sys
import os
from pathlib import Path

# 添加项目路径到系统路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from TenderGenerator.parsers.tender_parser import get_tender_parser
from TenderGenerator.utils.file_utils import get_file_utils
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_table_parsing():
    """测试表格解析功能"""
    
    print("=" * 60)
    print("开始测试表格解析功能")
    print("=" * 60)
    
    # 创建测试用的表格文本
    test_table_text = """
    23、磋商的评价

    23.1 经初审合格的响应文件，磋商小组将严格按照竞争性磋商采购文件确定的评标标准和方法进行评审。

    23.2 本项目将采用综合评分法，按商务、技术（服务）、价格三部分评分，总分设置 100 分，其中商务部分 30 分、技术（服务）部分 30 分、价格部分 40 分：

    [表格 1]
    评审内容	评分因素	分值	评分标准
    商务部分（满分30分）	企业认证	6	信息安全管理体系认证（ISO27001）、信息技术服务管理体系认证（ISO20000）、高新技术企业证书等，每提供一个认证证书得2分，最多得6分。
    	成立时间	1	供应商成立5年及以上的得1分，不满足不得分。
    	处理能力	6	供应商数据可覆盖移动、联通、电信、广电等运营商在网数据，全部覆盖得6分；覆盖移动、联通、电信三大运营商得3分；未覆盖移动、联通、电信三大运营商其中一家的不得分。
    """
    
    # 测试文件工具
    print("\n1. 测试文件工具类")
    file_utils = get_file_utils()
    
    # 模拟文档数据结构
    mock_file_data = {
        'type': 'word',
        'paragraphs': [
            {'text': '23、磋商的评价'},
            {'text': '23.1 经初审合格的响应文件，磋商小组将严格按照竞争性磋商采购文件确定的评标标准和方法进行评审。'},
            {'text': '23.2 本项目将采用综合评分法，按商务、技术（服务）、价格三部分评分，总分设置 100 分，其中商务部分 30 分、技术（服务）部分 30 分、价格部分 40 分：'}
        ],
        'tables': [
            {
                'data': [
                    ['评审内容', '评分因素', '分值', '评分标准'],
                    ['商务部分（满分30分）', '企业认证', '6', '信息安全管理体系认证（ISO27001）、信息技术服务管理体系认证（ISO20000）、高新技术企业证书等，每提供一个认证证书得2分，最多得6分。'],
                    ['', '成立时间', '1', '供应商成立5年及以上的得1分，不满足不得分。'],
                    ['', '处理能力', '6', '供应商数据可覆盖移动、联通、电信、广电等运营商在网数据，全部覆盖得6分；覆盖移动、联通、电信三大运营商得3分；未覆盖移动、联通、电信三大运营商其中一家的不得分。']
                ]
            }
        ]
    }
    
    # 提取文本内容
    extracted_text = file_utils.extract_text_content(mock_file_data)
    print(f"提取的文本内容长度: {len(extracted_text)}")
    print("提取的文本内容预览:")
    print("-" * 40)
    print(extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text)
    print("-" * 40)
    
    # 测试招标文件解析器
    print("\n2. 测试招标文件解析器")
    parser = get_tender_parser()
    
    # 分割章节
    sections = file_utils.split_into_sections(extracted_text)
    print(f"发现章节数: {len(sections)}")
    for i, section in enumerate(sections):
        print(f"  章节 {i+1}: {section['title'][:50]}... (级别: {section['level']})")
    
    # 提取评分标准
    print("\n3. 提取评分标准")
    scoring_criteria = parser._extract_scoring_criteria(sections, extracted_text)
    print(f"发现评分标准章节数: {len(scoring_criteria)}")
    
    for i, section in enumerate(scoring_criteria):
        print(f"  评分章节 {i+1}: {section.get('title', 'Unknown')}")
        print(f"    内容长度: {len(section.get('content', ''))}")
    
    # 解析评分详细信息
    print("\n4. 解析评分详细信息")
    scoring_details = parser._parse_scoring_details(scoring_criteria)
    print(f"发现评分项目数: {len(scoring_details)}")
    
    for i, detail in enumerate(scoring_details):
        print(f"\n  评分项目 {i+1}:")
        print(f"    ID: {detail['id']}")
        print(f"    标题: {detail['title']}")
        print(f"    权重: {detail['weight']}")
        print(f"    最大分值: {detail['max_score']}")
        print(f"    描述: {detail['description'][:100]}..." if len(detail['description']) > 100 else f"    描述: {detail['description']}")
        print(f"    评分标准数量: {len(detail.get('criteria', []))}")
    
    # 测试直接从文本提取评分项目
    print("\n5. 直接从文本提取评分项目")
    items = parser._extract_scoring_items(extracted_text)
    print(f"直接提取的评分项目数: {len(items)}")
    
    for i, item in enumerate(items):
        print(f"\n  项目 {i+1}:")
        print(f"    标题: {item['title']}")
        print(f"    权重: {item['weight']}")
        print(f"    最大分值: {item['max_score']}")
        if item['description']:
            print(f"    描述: {item['description'][:100]}..." if len(item['description']) > 100 else f"    描述: {item['description']}")
    
    print("\n" + "=" * 60)
    print("表格解析功能测试完成")
    print("=" * 60)
    
    return len(scoring_details) > 0 or len(items) > 0

def test_with_real_file():
    """测试真实文件（如果存在）"""
    print("\n" + "=" * 60)
    print("测试真实招标文件")
    print("=" * 60)
    
    # 查找可能的招标文件
    possible_files = [
        "招标文件.docx",
        "招标文件.doc",
        "磋商文件.docx",
        "采购文件.docx"
    ]
    
    current_dir = Path(__file__).parent
    test_file = None
    
    for filename in possible_files:
        file_path = current_dir / filename
        if file_path.exists():
            test_file = str(file_path)
            break
    
    if not test_file:
        print("未找到真实的招标文件，跳过真实文件测试")
        return False
    
    print(f"找到测试文件: {test_file}")
    
    try:
        parser = get_tender_parser()
        result = parser.parse_tender_document(test_file)
        
        if 'error' in result:
            print(f"解析文件失败: {result['error']}")
            return False
        
        print(f"\n文件解析结果:")
        print(f"  文件类型: {result['file_type']}")
        print(f"  总章节数: {result['total_sections']}")
        print(f"  需求项目数: {len(result['requirements'])}")
        print(f"  评分项目数: {len(result['scoring_details'])}")
        
        # 显示评分详情
        if result['scoring_details']:
            print(f"\n评分项目详情:")
            for i, item in enumerate(result['scoring_details'][:5]):  # 只显示前5个
                print(f"  {i+1}. {item['title']} - {item['weight']}")
                if item['description']:
                    print(f"     {item['description'][:80]}..." if len(item['description']) > 80 else f"     {item['description']}")
        
        return len(result['scoring_details']) > 0
        
    except Exception as e:
        print(f"测试真实文件时出错: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success_mock = test_table_parsing()
    success_real = test_with_real_file()
    
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"模拟数据测试: {'成功' if success_mock else '失败'}")
    print(f"真实文件测试: {'成功' if success_real else '跳过/失败'}")
    
    if success_mock or success_real:
        print("\n✅ 表格解析功能修复成功！")
    else:
        print("\n❌ 表格解析功能需要进一步修复")