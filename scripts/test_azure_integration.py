#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Azure OpenAI 集成测试脚本

测试 Azure OpenAI 在标书系统中的集成情况
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_tender_system.common import create_llm_client, get_available_models


def test_azure_models_available():
    """测试 Azure 模型是否在可用模型列表中"""
    print("=" * 60)
    print("测试 1: 检查 Azure 模型配置")
    print("=" * 60)

    models = get_available_models()
    azure_models = [m for m in models if m['provider'] == 'Azure OpenAI']

    print(f"\n找到 {len(azure_models)} 个 Azure 模型:")
    for model in azure_models:
        print(f"  - {model['name']}: {model['display_name']}")
        print(f"    描述: {model['description']}")
        print(f"    配置状态: {'✓ 已配置' if model['has_api_key'] else '✗ 未配置'}")

    return len(azure_models) > 0


def test_azure_client_creation():
    """测试 Azure 客户端创建"""
    print("\n" + "=" * 60)
    print("测试 2: 创建 Azure LLM 客户端")
    print("=" * 60)

    try:
        # 尝试创建不同的 Azure 客户端
        models_to_test = ['azure-gpt4', 'azure-gpt4o', 'azure-gpt35-turbo']

        for model_name in models_to_test:
            print(f"\n创建客户端: {model_name}")
            client = create_llm_client(model_name)
            info = client.get_model_info()

            print(f"  模型名称: {info['model_name']}")
            print(f"  显示名称: {info['display_name']}")
            print(f"  提供商: {info['provider']}")
            print(f"  Max Tokens: {info['max_tokens']}")
            print(f"  Timeout: {info['timeout']}s")
            print(f"  API Key: {'✓ 已设置' if info['has_api_key'] else '✗ 未设置'}")

        return True
    except Exception as e:
        print(f"✗ 客户端创建失败: {e}")
        return False


def test_azure_api_call():
    """测试 Azure API 调用（需要有效的密钥）"""
    print("\n" + "=" * 60)
    print("测试 3: Azure API 调用测试")
    print("=" * 60)

    try:
        client = create_llm_client("azure-gpt35-turbo")

        # 检查是否配置了密钥
        info = client.get_model_info()
        if not info['has_api_key']:
            print("⚠️  跳过API调用测试：未配置 Azure OpenAI API 密钥")
            print("   请在 .env 文件中设置以下环境变量：")
            print("   - AZURE_OPENAI_API_KEY")
            print("   - AZURE_OPENAI_ENDPOINT")
            print("   - AZURE_OPENAI_DEPLOYMENT_35")
            return None

        print("\n发送测试请求...")
        response = client.call(
            prompt="请用一句话介绍你自己。",
            purpose="Azure集成测试",
            max_retries=1
        )

        print(f"✓ API 调用成功！")
        print(f"响应内容: {response[:200]}...")

        return True
    except Exception as e:
        print(f"✗ API 调用失败: {e}")
        print("\n可能的原因：")
        print("  1. Azure API 密钥未配置或无效")
        print("  2. Azure 端点地址不正确")
        print("  3. 部署名称不匹配")
        print("  4. 网络连接问题")
        return False


def test_azure_stream_call():
    """测试 Azure 流式调用（需要有效的密钥）"""
    print("\n" + "=" * 60)
    print("测试 4: Azure 流式调用测试")
    print("=" * 60)

    try:
        client = create_llm_client("azure-gpt35-turbo")

        # 检查是否配置了密钥
        info = client.get_model_info()
        if not info['has_api_key']:
            print("⚠️  跳过流式调用测试：未配置 Azure OpenAI API 密钥")
            return None

        print("\n发送流式测试请求...")
        print("响应内容: ", end='', flush=True)

        full_response = ""
        for chunk in client.call_stream(
            prompt="数到5，每个数字之间用逗号分隔。",
            purpose="Azure流式测试"
        ):
            print(chunk, end='', flush=True)
            full_response += chunk

        print("\n✓ 流式调用成功！")
        return True
    except Exception as e:
        print(f"\n✗ 流式调用失败: {e}")
        return False


def main():
    """运行所有测试"""
    print("\n🚀 Azure OpenAI 集成测试开始\n")

    results = {
        "模型配置": test_azure_models_available(),
        "客户端创建": test_azure_client_creation(),
        "API调用": test_azure_api_call(),
        "流式调用": test_azure_stream_call()
    }

    # 输出测试总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)

    for test_name, result in results.items():
        if result is True:
            status = "✓ 通过"
        elif result is False:
            status = "✗ 失败"
        else:
            status = "⊘ 跳过"
        print(f"  {test_name}: {status}")

    # 判断整体状态
    passed = sum(1 for r in results.values() if r is True)
    failed = sum(1 for r in results.values() if r is False)
    skipped = sum(1 for r in results.values() if r is None)

    print(f"\n总计: {passed} 通过, {failed} 失败, {skipped} 跳过")

    if failed == 0 and passed > 0:
        print("\n✅ Azure OpenAI 集成测试全部通过！")
        return 0
    elif skipped > 0 and failed == 0:
        print("\n⚠️  部分测试跳过（需要配置 Azure API 密钥）")
        return 0
    else:
        print("\n❌ 部分测试失败，请检查配置")
        return 1


if __name__ == "__main__":
    sys.exit(main())
