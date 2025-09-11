#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
始皇API配置文件
"""

# =========================== API配置 ===========================
# 请在此处配置您的始皇API密钥
SHIHUANG_API_KEY = """"

# API相关配置
API_CONFIG = {
    "base_url": "https://api.oaipro.com/v1/chat/completions",
    "model": "gpt-4o-mini",  # 使用GPT-4o-mini模型，成本效益更好
    "temperature": 0.3,      # 保持专业性和一致性
    "max_tokens": 300,       # 控制应答长度
    "timeout": 60            # 超时时间（秒）
}

# =========================== API密钥验证 ===========================
def is_valid_api_key(api_key: str) -> bool:
    """检查API密钥格式是否有效"""
    if not api_key or api_key == "sk-xxx":
        return False
    return api_key.startswith("sk-") and len(api_key) > 10

def get_api_key() -> str:
    """获取API密钥，优先从环境变量读取"""
    import os
    
    # 1. 从环境变量获取
    env_key = os.getenv("SHIHUANG_API_KEY")
    if env_key and is_valid_api_key(env_key):
        return env_key
    
    # 2. 从配置文件获取
    if is_valid_api_key(SHIHUANG_API_KEY):
        return SHIHUANG_API_KEY
    
    # 3. 返回默认值
    return "sk-xxx"

# =========================== 使用说明 ===========================
def print_api_setup_guide():
    """打印API配置指南"""
    print("=" * 60)
    print("🔑 始皇API配置指南")
    print("=" * 60)
    print()
    print("方法1: 修改配置文件")
    print("  编辑 api_config.py 第7行：")
    print('  SHIHUANG_API_KEY = "sk-your-actual-api-key"')
    print()
    print("方法2: 设置环境变量")
    print("  export SHIHUANG_API_KEY=sk-your-actual-api-key")
    print()
    print("方法3: 命令行参数")
    print("  python3 enhanced_inline_reply.py file.docx sk-your-api-key")
    print()
    print("📋 API密钥获取：")
    print("  访问 https://api.oaipro.com 申请API密钥")
    print("  当前使用 GPT-4o-mini 模型（成本效益佳）")
    print()
    print("=" * 60)

if __name__ == "__main__":
    print_api_setup_guide()
    
    # 测试当前配置
    current_key = get_api_key()
    if is_valid_api_key(current_key):
        print(f"✅ 当前API密钥格式正确: {current_key[:10]}...")
    else:
        print("❌ 未配置有效的API密钥，将使用备用模板")