#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API测试脚本
用于验证API配置是否正确，测试LLM调用功能

功能：
1. 加载环境变量
2. 测试API连接性
3. 测试认证
4. 测试模型响应
5. 显示详细诊断信息
"""

import os
import sys
import json
import time
import requests
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime

# 添加父目录到路径，以便导入common模块
sys.path.append(str(Path(__file__).parent.parent))

def load_env():
    """加载环境变量"""
    # 查找.env文件
    env_paths = [
        Path(__file__).parent.parent / '.env',  # 项目根目录
        Path(__file__).parent / '.env',         # 当前目录
    ]

    env_file = None
    for path in env_paths:
        if path.exists():
            env_file = path
            break

    if env_file:
        load_dotenv(env_file)
        print(f"✅ 从文件加载环境变量: {env_file}")
    else:
        print("⚠️  未找到.env文件，使用系统环境变量")

    # 返回默认配置和所有模型配置
    configs = {
        'default': {
            'api_key': os.getenv('DEFAULT_API_KEY', ''),
            'api_endpoint': os.getenv('API_ENDPOINT', 'https://api.oaipro.com/v1/chat/completions'),
            'model_name': os.getenv('MODEL_NAME', 'gpt-5'),
            'max_tokens': int(os.getenv('MAX_TOKENS', '1000')),
            'timeout': int(os.getenv('API_TIMEOUT', '30'))
        },
        'gpt-4o-mini': {
            'api_key': os.getenv('OPENAI_API_KEY', os.getenv('DEFAULT_API_KEY', '')),
            'api_endpoint': os.getenv('OPENAI_API_ENDPOINT', 'https://api.oaipro.com/v1/chat/completions'),
            'model_name': 'gpt-4o-mini',
            'max_tokens': int(os.getenv('OPENAI_MAX_TOKENS', '1000')),
            'timeout': int(os.getenv('OPENAI_TIMEOUT', '30'))
        },
        'unicom-yuanjing': {
            'api_key': os.getenv('UNICOM_API_KEY', os.getenv('DEFAULT_API_KEY', '')),
            'client_secret': os.getenv('UNICOM_CLIENT_SECRET', ''),
            'api_endpoint': os.getenv('UNICOM_API_ENDPOINT', 'https://maas.ai-yuanjing.com/v1/chat/completions'),
            'token_endpoint': os.getenv('UNICOM_TOKEN_ENDPOINT', 'https://maas.ai-yuanjing.com/oauth/token'),
            'model_name': os.getenv('UNICOM_MODEL_NAME', 'yuanjing-pro'),
            'max_tokens': int(os.getenv('UNICOM_MAX_TOKENS', '1000')),
            'timeout': int(os.getenv('UNICOM_TIMEOUT', '30'))
        }
    }

    return configs

def test_api_connection(config):
    """测试API连接和认证"""
    print("\n" + "="*60)
    print("🔍 开始API测试")
    print("="*60)

    # 显示配置信息
    print("\n📋 当前配置:")
    print(f"  API端点: {config['api_endpoint']}")
    print(f"  模型名称: {config['model_name']}")
    print(f"  API密钥: {config['api_key'][:15]}...{config['api_key'][-5:] if len(config['api_key']) > 20 else ''}")
    print(f"  最大令牌: {config['max_tokens']}")
    print(f"  超时时间: {config['timeout']}秒")

    if not config['api_key']:
        print("\n❌ 错误: API密钥未设置!")
        print("解决方案: 请在.env文件或环境变量中设置DEFAULT_API_KEY")
        return False

    # 准备测试请求
    headers = {
        'Authorization': f'Bearer {config["api_key"]}',
        'Content-Type': 'application/json'
    }

    test_data = {
        'model': config['model_name'],
        'messages': [
            {
                'role': 'user',
                'content': '请回复"测试成功"这四个字'
            }
        ],
        'max_completion_tokens': 50,
        'temperature': 1
    }

    print("\n🚀 发送测试请求...")
    print(f"  测试消息: {test_data['messages'][0]['content']}")

    try:
        start_time = time.time()
        response = requests.post(
            config['api_endpoint'],
            headers=headers,
            json=test_data,
            timeout=config['timeout']
        )
        elapsed_time = time.time() - start_time

        print(f"\n📡 收到响应 (耗时: {elapsed_time:.2f}秒)")
        print(f"  状态码: {response.status_code}")

        if response.status_code == 200:
            result = response.json()

            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0]['message']['content']
                print(f"\n✅ API测试成功!")
                print(f"  模型回复: {content}")

                # 显示使用统计
                if 'usage' in result:
                    usage = result['usage']
                    print(f"\n📊 使用统计:")
                    print(f"  输入令牌: {usage.get('prompt_tokens', 'N/A')}")
                    print(f"  输出令牌: {usage.get('completion_tokens', 'N/A')}")
                    print(f"  总计令牌: {usage.get('total_tokens', 'N/A')}")

                return True
            else:
                print("\n❌ API响应格式异常")
                print(f"响应内容: {json.dumps(result, indent=2, ensure_ascii=False)}")
                return False

        elif response.status_code == 401:
            print("\n❌ 认证失败 (401)")
            print("原因: API密钥无效或已过期")
            print("解决方案:")
            print("  1. 检查API密钥是否正确")
            print("  2. 确认密钥未过期")
            print("  3. 验证密钥格式（应以'sk-'开头）")
            error_detail = response.json() if response.text else {}
            if error_detail:
                print(f"\n错误详情: {json.dumps(error_detail, indent=2, ensure_ascii=False)}")
            return False

        elif response.status_code == 429:
            print("\n⚠️  请求频率限制 (429)")
            print("原因: 请求太频繁或配额用尽")
            print("解决方案: 稍后重试或检查账户配额")
            return False

        elif response.status_code == 404:
            print("\n❌ 端点不存在 (404)")
            print(f"原因: API端点 {config['api_endpoint']} 不存在")
            print("解决方案: 检查API_ENDPOINT配置是否正确")
            return False

        else:
            print(f"\n❌ 未预期的状态码: {response.status_code}")
            print(f"响应内容: {response.text[:500]}")
            return False

    except requests.exceptions.Timeout:
        print(f"\n❌ 请求超时 (>{config['timeout']}秒)")
        print("解决方案:")
        print("  1. 检查网络连接")
        print("  2. 增加API_TIMEOUT配置")
        print("  3. 验证API端点是否可访问")
        return False

    except requests.exceptions.ConnectionError as e:
        print(f"\n❌ 连接错误")
        print(f"错误: {str(e)}")
        print("解决方案:")
        print("  1. 检查网络连接")
        print("  2. 验证API端点地址")
        print("  3. 检查防火墙设置")
        return False

    except Exception as e:
        print(f"\n❌ 未预期的错误")
        print(f"错误类型: {type(e).__name__}")
        print(f"错误信息: {str(e)}")
        import traceback
        print("\n堆栈跟踪:")
        print(traceback.format_exc())
        return False

def test_complex_query(config):
    """测试复杂查询功能"""
    print("\n" + "="*60)
    print("🔬 测试复杂查询功能")
    print("="*60)

    headers = {
        'Authorization': f'Bearer {config["api_key"]}',
        'Content-Type': 'application/json'
    }

    # 测试JSON提取功能
    test_prompt = """
请从以下文本中提取信息，以JSON格式返回：

文本：张三是项目经理，负责ABC项目，项目编号是P2025001。

请提取：
1. name: 姓名
2. role: 职位
3. project: 项目名称
4. project_id: 项目编号

严格按JSON格式返回。
"""

    test_data = {
        'model': config['model_name'],
        'messages': [
            {'role': 'user', 'content': test_prompt}
        ],
        'max_completion_tokens': 200,
        'temperature': 1
    }

    print("📝 测试JSON提取功能...")

    try:
        response = requests.post(
            config['api_endpoint'],
            headers=headers,
            json=test_data,
            timeout=config['timeout']
        )

        if response.status_code == 200:
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0]['message']['content']
                print(f"\n模型响应:\n{content}")

                # 尝试解析JSON
                try:
                    json_start = content.find('{')
                    json_end = content.rfind('}') + 1
                    if json_start >= 0 and json_end > json_start:
                        json_str = content[json_start:json_end]
                        parsed = json.loads(json_str)
                        print(f"\n✅ JSON解析成功:")
                        print(json.dumps(parsed, indent=2, ensure_ascii=False))
                        return True
                    else:
                        print("\n⚠️  响应中未找到JSON格式")
                        return False
                except json.JSONDecodeError as e:
                    print(f"\n⚠️  JSON解析失败: {e}")
                    return False
            else:
                print("\n❌ 无有效响应")
                return False
        else:
            print(f"\n❌ 请求失败: {response.status_code}")
            return False

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        return False

def test_llm_client(model_name, model_config):
    """测试统一LLM客户端"""
    print("\n" + "="*60)
    print(f"🔬 测试统一LLM客户端 - {model_name}")
    print("="*60)

    try:
        # 导入LLM客户端
        from common.llm_client import create_llm_client

        # 创建客户端
        client = create_llm_client(model_name, model_config.get('api_key'))

        # 显示模型信息
        model_info = client.get_model_info()
        print("\n📋 模型信息:")
        for key, value in model_info.items():
            if key == 'has_api_key':
                print(f"  {key}: {'是' if value else '否'}")
            else:
                print(f"  {key}: {value}")

        if not model_info['has_api_key']:
            print(f"\n❌ 模型 {model_name} 未配置API密钥，跳过测试")
            return False

        # 验证配置
        print(f"\n🚀 验证模型配置...")
        validation_result = client.validate_config()

        if validation_result['valid']:
            print(f"✅ 配置验证成功！")
            print(f"  测试响应: {validation_result.get('test_response', 'N/A')}")
            return True
        else:
            print(f"❌ 配置验证失败: {validation_result.get('error', '未知错误')}")
            return False

    except ImportError as e:
        print(f"❌ 导入LLM客户端失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 测试LLM客户端失败: {e}")
        import traceback
        print(f"错误详情: {traceback.format_exc()}")
        return False

def test_all_models(configs):
    """测试所有配置的模型"""
    print("\n" + "="*60)
    print("🔍 多模型测试")
    print("="*60)

    results = {}

    # 测试每个模型（除了default）
    for model_name, config in configs.items():
        if model_name == 'default':
            continue

        print(f"\n--- 测试 {model_name} ---")

        if not config.get('api_key'):
            print(f"⚠️  模型 {model_name} 未配置API密钥，跳过测试")
            results[model_name] = False
            continue

        try:
            # 先尝试传统方式测试
            legacy_result = test_api_connection(config)

            # 然后测试统一客户端
            client_result = test_llm_client(model_name, config)

            results[model_name] = legacy_result and client_result

        except Exception as e:
            print(f"❌ 测试模型 {model_name} 时发生错误: {e}")
            results[model_name] = False

    return results

def main():
    """主测试函数"""
    print("\n" + "🤖 AI标书系统 - 多模型API测试工具 🤖".center(60))
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 加载配置
    configs = load_env()

    # 显示可用模型
    print(f"\n📋 检测到 {len(configs)} 个配置:")
    for model_name, config in configs.items():
        api_key = config.get('api_key', '')
        status = "✅ 已配置" if api_key else "❌ 未配置"
        print(f"  {model_name}: {status}")

    # 测试默认配置（向后兼容）
    print(f"\n{'='*60}")
    print("🔧 传统API测试 (向后兼容)")
    print("="*60)

    default_config = configs['default']
    basic_test = test_api_connection(default_config)

    if basic_test:
        complex_test = test_complex_query(default_config)
    else:
        complex_test = False

    # 测试所有模型
    model_results = test_all_models(configs)

    # 显示测试总结
    print("\n" + "="*60)
    print("📊 测试总结")
    print("="*60)

    print("传统API测试:")
    print(f"  ✅ 基础连接测试: {'通过' if basic_test else '失败'}")
    print(f"  {'✅' if complex_test else '❌'} JSON提取测试: {'通过' if complex_test else '失败'}")

    print("\n多模型测试:")
    for model_name, success in model_results.items():
        status = "✅ 通过" if success else "❌ 失败"
        print(f"  {model_name}: {status}")

    # 总体结论
    all_passed = basic_test and complex_test and all(model_results.values())
    some_passed = basic_test or any(model_results.values())

    print(f"\n{'='*60}")
    if all_passed:
        print("🎉 所有测试通过！多模型配置正确，可以正常使用。")
    elif some_passed:
        print("⚠️  部分测试通过，建议检查失败的配置。")
    else:
        print("❌ 所有测试失败，请检查网络连接和API配置。")

    print("="*60)

if __name__ == "__main__":
    main()