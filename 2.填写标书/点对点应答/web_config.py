#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统配置文件
"""

import os

# 默认API配置
DEFAULT_API_CONFIG = {
    # 默认API密钥 - 可以通过环境变量覆盖
    'api_key': os.getenv('DEFAULT_API_KEY', '""'),
    
    # API端点配置
    'api_endpoint': os.getenv('API_ENDPOINT', 'https://api.oaipro.com/v1/chat/completions'),
    
    # 模型配置
    'model_name': os.getenv('MODEL_NAME', 'gpt-5'),
    
    # 其他配置
    'max_tokens': int(os.getenv('MAX_TOKENS', '1000')),
    'timeout': int(os.getenv('API_TIMEOUT', '30'))
}

# Web界面配置
WEB_CONFIG = {
    'port': int(os.getenv('WEB_PORT', '8082')),
    'host': os.getenv('WEB_HOST', '0.0.0.0'),
    'debug': os.getenv('DEBUG', 'True').lower() == 'true'
}

# 文件上传配置
UPLOAD_CONFIG = {
    'max_file_size': 50 * 1024 * 1024,  # 50MB
    'allowed_extensions': {
        'point_to_point': {'docx', 'doc'},
        'tech_proposal': {'docx', 'doc', 'pdf'}, 
        'tender_info': {'docx', 'doc', 'txt', 'pdf'}
    }
}

def get_default_api_key():
    """获取默认API密钥"""
    return DEFAULT_API_CONFIG['api_key']

def get_api_config():
    """获取完整的API配置"""
    return DEFAULT_API_CONFIG.copy()

def get_web_config():
    """获取Web配置"""
    return WEB_CONFIG.copy()

if __name__ == "__main__":
    print("=== 系统配置信息 ===")
    print(f"默认API密钥: {get_default_api_key()[:10]}...")
    print(f"API端点: {DEFAULT_API_CONFIG['api_endpoint']}")
    print(f"模型: {DEFAULT_API_CONFIG['model_name']}")
    print(f"Web端口: {WEB_CONFIG['port']}")
    print(f"调试模式: {WEB_CONFIG['debug']}")