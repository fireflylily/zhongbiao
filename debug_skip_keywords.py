#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试跳过关键词匹配问题
"""

import sys
from pathlib import Path

# 添加项目根目录到系统路径
sys.path.append(str(Path(__file__).parent))

from ai_tender_system.modules.business_response.info_filler import InfoFiller

def debug_skip_keywords():
    """调试跳过关键词匹配"""
    print("=" * 80)
    print("调试跳过关键词匹配问题")
    print("=" * 80)
    
    # 创建InfoFiller实例
    filler = InfoFiller()
    
    # 测试段落
    text = "根据贵方为（项目名称）项目采购采购货物及服务的竞争性磋商公告（采购编号），签字代表（姓名、职务）经正式授权并代表供应商（供应商名称、地址）提交下述文件正本一份及副本份："
    
    print(f"测试文本: '{text}'")
    print(f"文本长度: {len(text)}")
    
    print(f"\n🔍 跳过关键词检查:")
    print(f"skip_keywords: {filler.skip_keywords}")
    print(f"signature_keywords: {filler.signature_keywords}")
    
    # 逐个检查跳过关键词
    print(f"\n📝 逐个检查skip_keywords:")
    for keyword in filler.skip_keywords:
        if keyword in text:
            print(f"❌ 匹配到关键词: '{keyword}'")
            # 找出匹配位置
            start = text.find(keyword)
            end = start + len(keyword)
            context = text[max(0, start-10):end+10]
            print(f"   匹配位置: {start}-{end}")
            print(f"   上下文: '...{context}...'")
        else:
            print(f"✅ 未匹配: '{keyword}'")
    
    print(f"\n📝 逐个检查signature_keywords:")
    for keyword in filler.signature_keywords:
        if keyword in text:
            print(f"❌ 匹配到关键词: '{keyword}'")
            # 找出匹配位置
            start = text.find(keyword)
            end = start + len(keyword)
            context = text[max(0, start-10):end+10]
            print(f"   匹配位置: {start}-{end}")
            print(f"   上下文: '...{context}...'")
        else:
            print(f"✅ 未匹配: '{keyword}'")
    
    # 测试_should_skip方法
    print(f"\n🎯 _should_skip方法结果: {filler._should_skip(text)}")

if __name__ == "__main__":
    debug_skip_keywords()