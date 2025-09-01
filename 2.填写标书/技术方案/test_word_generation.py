#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试Word文档生成功能
"""

import sys
import os
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from TenderGenerator.generators.word_generator import get_word_generator

def test_word_generation():
    """测试Word文档生成功能"""
    
    print("=" * 60)
    print("测试Word文档生成功能")
    print("=" * 60)
    
    # 创建测试数据
    test_proposal_data = {
        'title': '中邮保险手机号实名认证服务技术方案',
        'project_name': '中邮保险手机号实名认证服务项目',
        'company': '智慧足迹数据科技有限公司',
        'contact': 'contact@example.com',
        'version': 'V1.0',
        'sections': [
            {
                'title': '1. 项目背景与需求分析',
                'content': '''本项目旨在为中邮保险提供手机号实名认证服务，满足监管合规要求。

项目背景：
随着金融科技的快速发展和监管政策的日趋严格，保险行业对客户身份验证的要求愈发严谨。

需求分析：
1. 业务需求：支持新客户注册认证、既有客户信息更新验证等场景
2. 功能需求：多维度验证引擎、智能风险评估系统
3. 非功能性需求：高可用性、高性能、数据安全''',
                'subsections': [
                    {
                        'title': '1.1 项目背景',
                        'content': '详细的项目背景描述...'
                    },
                    {
                        'title': '1.2 需求分析', 
                        'content': '详细的需求分析内容...'
                    }
                ]
            },
            {
                'title': '2. 技术方案设计',
                'content': '''本章节描述详细的技术方案设计。

系统架构采用微服务设计，具备以下特点：
• 高可扩展性
• 高可用性
• 安全可靠

技术选型：
- 开发语言：Java 17
- 框架：Spring Boot + Spring Cloud
- 数据库：MySQL + Redis
- 消息队列：Apache Kafka''',
                'subsections': [
                    {
                        'title': '2.1 系统架构',
                        'content': '系统采用分层架构设计...'
                    },
                    {
                        'title': '2.2 技术选型',
                        'content': '技术选型的详细说明...'
                    }
                ]
            },
            {
                'title': '3. 实施计划',
                'content': '''项目实施分为5个阶段：

**第一阶段**：需求调研与系统设计（4周）
- 深入调研业务需求
- 完成系统架构设计
- 制定开发计划

**第二阶段**：核心功能开发（8周）
- 实现认证核心引擎
- 开发API接口
- 集成第三方服务

**第三阶段**：系统测试（4周）
- 功能测试
- 性能测试
- 安全测试

**第四阶段**：试运行（2周）
- 生产环境部署
- 试运行验证

**第五阶段**：正式上线（持续）
- 系统正式投产
- 运维支持'''
            }
        ]
    }
    
    test_outline_data = {
        'title': '技术方案大纲',
        'sections': [
            {'title': '项目背景与需求分析', 'level': 1},
            {'title': '技术方案设计', 'level': 1}, 
            {'title': '实施计划', 'level': 1}
        ]
    }
    
    # 获取Word生成器
    word_generator = get_word_generator()
    
    # 生成Word文档
    output_file = "test_proposal.docx"
    
    print(f"开始生成Word文档: {output_file}")
    success = word_generator.export_proposal_to_word(
        test_proposal_data,
        test_outline_data,
        output_file
    )
    
    if success:
        print(f"✅ Word文档生成成功: {output_file}")
        
        # 检查文件是否存在
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            print(f"📄 文件大小: {file_size} 字节")
        else:
            print("❌ 文件不存在")
            
    else:
        print("❌ Word文档生成失败")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    test_word_generation()