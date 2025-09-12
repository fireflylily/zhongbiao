#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试表格式布局字段处理修复效果
"""
import sys
import os
import json
import tempfile
from pathlib import Path
import shutil

# 添加项目路径
script_dir = Path(__file__).parent
project_root = script_dir / 'ai_tender_system'
sys.path.insert(0, str(project_root))

try:
    from docx import Document
    import importlib.util
    
    print("🧪 测试表格式布局字段处理修复")
    print("=" * 50)
    
    # 1. 准备测试文件
    template_file = "/Users/lvhe/Library/Mobile Documents/com~apple~CloudDocs/Work/智慧足迹2025/05投标项目/AI标书/项目/4-分段测试文件/采购人，项目名称，采购编号，（姓名，职务）（供应商名称，地址）传真，电子邮件，日期.docx"
    company_file = project_root / "data/configs/companies/945150ca-68e1-4141-921b-fd4c48e07ebd.json"
    
    # 创建临时输出文件
    output_file = tempfile.NamedTemporaryFile(suffix='.docx', delete=False).name
    
    print(f"📄 原始模板: {Path(template_file).name}")
    print(f"🏢 公司数据: {company_file.name}")
    print(f"📤 输出文件: {Path(output_file).name}")
    
    # 2. 检查文件存在性
    if not Path(template_file).exists():
        print(f"❌ 模板文件不存在")
        sys.exit(1)
    
    if not company_file.exists():
        print(f"❌ 公司数据文件不存在")
        sys.exit(1)
    
    # 3. 复制模板文件到输出位置
    shutil.copy2(template_file, output_file)
    
    # 4. 读取公司数据
    with open(company_file, 'r', encoding='utf-8') as f:
        company_data = json.load(f)
    
    print(f"\n📋 公司联系信息:")
    print(f"  固定电话: {company_data.get('fixedPhone', 'N/A')}")
    print(f"  电子邮件: {company_data.get('email', 'N/A')}")
    print(f"  传真: {company_data.get('fax', 'N/A')}")
    
    # 5. 动态加载MCP处理器
    processor_file = script_dir / "2.填写标书/点对点应答/mcp_bidder_name_processor_enhanced 2.py"
    
    print(f"\n🔧 加载MCP处理器: {processor_file.name}")
    
    spec = importlib.util.spec_from_file_location("mcp_processor", processor_file)
    mcp_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mcp_module)
    
    # 创建处理器实例
    processor_class = getattr(mcp_module, 'MCPBidderNameProcessor')
    processor = processor_class()
    
    # 6. 执行处理
    print(f"\n🚀 开始处理文档...")
    
    try:
        result = processor.process_business_response(
            input_file=template_file,
            output_file=output_file,
            company_info=company_data,
            project_name='测试项目',
            tender_no='TEST2025001',
            date_text='2025年9月12日'
        )
        
        print(f"✅ 处理完成: {result.get('message', '成功')}")
        
        if result.get('success'):
            # 7. 验证处理结果
            print(f"\n🔍 验证处理结果:")
            
            doc = Document(output_file)
            
            # 搜索联系信息相关段落
            contact_paragraphs = []
            for i, paragraph in enumerate(doc.paragraphs):
                text = paragraph.text.strip()
                if text and any(keyword in text for keyword in ['电话', '电子邮件', '传真']):
                    contact_paragraphs.append({
                        'index': i,
                        'text': text
                    })
            
            print(f"  找到 {len(contact_paragraphs)} 个联系信息相关段落:")
            
            for para_info in contact_paragraphs:
                text = para_info['text']
                print(f"\n  段落 #{para_info['index']}: '{text}'")
                
                # 检查字段是否被正确填充
                checks = []
                if '电话' in text:
                    has_phone_value = '010-63271000' in text or '电话：' in text
                    checks.append(f"    📞 电话字段: {'✅ 已填充' if has_phone_value else '❌ 未填充'}")
                
                if '电子邮件' in text or '电子邮箱' in text:
                    has_email_value = 'lvhe@smartsteps.com' in text or '电子邮件：' in text or '电子邮箱：' in text
                    checks.append(f"    📧 邮件字段: {'✅ 已填充' if has_email_value else '❌ 未填充'}")
                
                if '传真' in text:
                    has_fax_value = '010-63271000' in text or '传真：' in text
                    checks.append(f"    📠 传真字段: {'✅ 已填充' if has_fax_value else '❌ 未填充'}")
                
                for check in checks:
                    print(check)
            
            # 8. 统计处理结果
            stats = result.get('stats', {})
            print(f"\n📊 处理统计:")
            print(f"  总替换次数: {stats.get('total_replacements', 0)}")
            print(f"  字段处理数: {stats.get('info_fields_processed', 0)}")
            print(f"  模式匹配数: {len(stats.get('patterns_found', []))}")
            
            # 显示匹配的模式详情
            patterns = stats.get('patterns_found', [])
            if patterns:
                print(f"\n🎯 匹配的字段模式:")
                for i, pattern in enumerate(patterns[:5], 1):  # 只显示前5个
                    print(f"  {i}. {pattern.get('description', 'N/A')} (段落#{pattern.get('paragraph_index', 'N/A')})")
            
        else:
            print(f"❌ 处理失败: {result.get('error', '未知错误')}")
            
    except Exception as e:
        print(f"❌ 处理异常: {e}")
        import traceback
        traceback.print_exc()
    
    # 9. 清理临时文件
    try:
        os.unlink(output_file)
        print(f"\n🗑️  临时文件已清理")
    except Exception as e:
        print(f"⚠️  临时文件清理失败: {e}")
    
    print(f"\n✅ 测试完成")
    
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("请确保安装了 python-docx: pip install python-docx")
except Exception as e:
    print(f"❌ 执行错误: {e}")
    import traceback
    traceback.print_exc()