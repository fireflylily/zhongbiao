#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
设置测试数据：创建文档并向量化
用于测试AI智能搜索功能
"""

import asyncio
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent / "ai_tender_system"
sys.path.insert(0, str(project_root))

from modules.vector_engine.chroma_adapter import ChromaVectorStore
from modules.vector_engine.simple_embedding import SimpleEmbeddingService


async def setup_test_documents():
    """创建测试文档并向量化"""
    print("=" * 70)
    print(" " * 20 + "设置AI搜索测试数据")
    print("=" * 70)

    # 1. 初始化组件
    print("\n【步骤1】初始化向量引擎...")
    vector_store = ChromaVectorStore(dimension=100)
    await vector_store.initialize()

    embedding_service = SimpleEmbeddingService(dimension=100)
    await embedding_service.initialize()
    print("✅ 初始化完成")

    # 2. 准备测试文档（模拟真实业务场景）
    print("\n【步骤2】准备测试文档...")
    test_docs = [
        {
            "id": "doc_unicom_5g_core",
            "content": """中国联通5G核心网产品介绍

产品概述：
中国联通5G核心网产品采用云原生架构设计，基于NFV（网络功能虚拟化）和SDN（软件定义网络）技术，
实现网络功能的灵活部署和动态编排。支持eMBB、uRLLC、mMTC三大5G应用场景。

技术特点：
1. 服务化架构（SBA）：采用微服务架构，各网元间通过HTTP/2协议通信
2. 网络切片：支持多租户隔离和差异化服务质量保证
3. 边缘计算：MEC（移动边缘计算）能力，降低时延至10ms以内
4. 高可靠性：99.999%可用性，支持双活/多活部署

关键性能指标：
- 用户容量：单套系统支持5000万用户
- 会话容量：每秒处理10万次会话建立
- 时延：端到端时延<20ms
- 吞吐量：单节点吞吐量达100Gbps

应用场景：
智慧城市、工业互联网、车联网、远程医疗、高清视频传输等。""",
            "metadata": {
                "company_id": 1,
                "product_id": 1,
                "doc_id": 100,
                "document_type": "产品介绍",
                "document_name": "5G核心网产品手册",
                "product_name": "5G核心网产品"
            }
        },
        {
            "id": "doc_unicom_cloud_platform",
            "content": """中国联通云计算平台技术架构

平台简介：
联通云计算平台是面向政企客户的公有云服务平台，提供IaaS、PaaS、SaaS全栈云服务。
平台采用OpenStack+Kubernetes混合架构，支持虚拟机和容器两种资源交付模式。

核心组件：
1. 计算资源池：采用KVM虚拟化技术，支持x86和ARM架构
2. 存储资源池：分布式块存储（Ceph）+ 对象存储（S3兼容）
3. 网络资源池：SDN网络，支持VPC、专线、VPN多种接入方式
4. 数据库服务：MySQL、PostgreSQL、Redis、MongoDB等

安全保障：
- 物理隔离：租户间网络物理隔离
- 数据加密：静态加密和传输加密
- 等保合规：通过等保三级认证
- 安全防护：DDoS防护、Web应用防火墙、入侵检测系统

资源规模：
全国31个省市部署，总计算能力100万核vCPU，存储容量50PB。""",
            "metadata": {
                "company_id": 1,
                "product_id": 2,
                "doc_id": 101,
                "document_type": "技术文档",
                "document_name": "云计算平台技术白皮书",
                "product_name": "云计算平台"
            }
        },
        {
            "id": "doc_zhzj_riskcontrol",
            "content": """智慧足迹极盾风控平台产品说明

产品定位：
极盾风控平台是一款基于大数据和人工智能技术的智能风险控制系统，
专注于金融、电商、社交等领域的欺诈检测和风险防控。

核心算法：
1. 深度学习神经网络：LSTM/GRU用于序列行为分析
2. 随机森林算法：多维特征融合决策
3. XGBoost梯度提升：高精度风险评分
4. 图神经网络：社交网络关系挖掘
5. 异常检测算法：Isolation Forest、LOF

实时监控能力：
- 并发处理：支持100万TPS高并发
- 响应时间：平均30ms，P99<50ms
- 准确率：欺诈识别准确率>99.5%
- 误报率：<0.1%

应用场景：
1. 金融反欺诈：信用卡盗刷、贷款欺诈、洗钱监测
2. 电商风控：刷单检测、恶意退货、账号盗用
3. 内容安全：垃圾信息过滤、恶意账号识别

客户案例：
已为120+金融机构和电商平台提供服务，累计处理交易量超100亿笔，
识别欺诈交易1000万+笔，挽回客户损失超50亿元。""",
            "metadata": {
                "company_id": 8,
                "product_id": 22,
                "doc_id": 102,
                "document_type": "产品手册",
                "document_name": "极盾风控平台产品手册",
                "product_name": "极盾风控平台"
            }
        },
        {
            "id": "doc_unicom_qualification",
            "content": """中国联通企业资质证明文件

企业基本信息：
企业名称：中国联合网络通信集团有限公司
统一社会信用代码：91110000710939135P
注册资本：22539208.432769万元人民币
法定代表人：陈忠岳
成立日期：2000年4月21日
注册地址：北京市西城区金融大街21号

资质证书：
1. 营业执照：统一社会信用代码证
2. 电信业务经营许可证：A2.B1.B2全业务牌照
3. ISO9001质量管理体系认证
4. ISO27001信息安全管理体系认证
5. ISO20000 IT服务管理体系认证
6. CMMI5级软件能力成熟度认证
7. 信息系统集成及服务资质（一级）
8. 高新技术企业证书
9. AAA级信用企业

知识产权：
累计申请专利8000+项，其中发明专利6000+项
软件著作权2000+项
参与制定国际标准100+项，国家标准200+项""",
            "metadata": {
                "company_id": 1,
                "product_id": None,
                "doc_id": 103,
                "document_type": "企业资质",
                "document_name": "企业资质证明",
                "company_name": "中国联通"
            }
        },
        {
            "id": "doc_zhzj_case_bank",
            "content": """极盾风控平台银行业应用案例

客户背景：
某国有大型商业银行，信用卡用户2000万+，日交易量500万笔，
面临信用卡盗刷、套现、养卡等多种欺诈风险。

解决方案：
1. 实时风险监控：
   - 部署实时规则引擎，毫秒级交易决策
   - 接入银联、网联等支付清算系统
   - 7x24小时不间断监控

2. 智能风险模型：
   - 构建20+维度特征体系（用户画像、设备指纹、行为序列）
   - 训练深度学习模型，识别隐蔽欺诈模式
   - 每日模型更新，快速响应新型欺诈手段

3. 多层防御体系：
   - 事前：风险评估，高风险用户限额控制
   - 事中：实时拦截，可疑交易短信验证
   - 事后：案件调查，黑名单管理

实施效果：
- 欺诈交易拦截率提升40%
- 误报率下降60%
- 挽回损失超5000万元/年
- 客户投诉率下降30%
- 风控审核效率提升3倍""",
            "metadata": {
                "company_id": 8,
                "product_id": 22,
                "doc_id": 104,
                "document_type": "客户案例",
                "document_name": "银行业应用案例",
                "product_name": "极盾风控平台"
            }
        }
    ]

    print(f"✅ 准备了 {len(test_docs)} 个业务文档")
    for i, doc in enumerate(test_docs, 1):
        print(f"   {i}. {doc['metadata']['document_name']}")

    # 3. 向量化并存储
    print("\n【步骤3】向量化并存储到Chroma...")
    for i, doc in enumerate(test_docs, 1):
        # 生成向量
        result = await embedding_service.embed_texts([doc["content"]])
        vector = result.vectors[0]

        # 存储到Chroma
        await vector_store.add_document(
            doc_id=doc["id"],
            content=doc["content"],
            vector=vector,
            metadata=doc["metadata"]
        )
        print(f"  ✓ [{i}/{len(test_docs)}] {doc['id']} 向量化完成")

    # 4. 验证
    stats = vector_store.get_stats()
    print(f"\n✅ 测试数据设置完成!")
    print(f"   - 总文档数: {stats['total_documents']}")
    print(f"   - 持久化目录: {stats['persist_directory']}")

    print("\n" + "=" * 70)
    print("✨ 测试数据已就绪，可以开始测试AI搜索功能了！")
    print("=" * 70)
    print("\n💡 测试建议：")
    print("   1. 访问: http://localhost:8110/knowledge_base")
    print("   2. 点击工具栏的 AI搜索 按钮 (⭐图标)")
    print("   3. 尝试搜索：")
    print("      - '5G核心网的性能指标'")
    print("      - '云计算平台的安全保障'")
    print("      - '风控系统的算法有哪些'")
    print("      - '中国联通有哪些资质证书'")
    print("      - '银行风控案例效果'")


if __name__ == "__main__":
    try:
        asyncio.run(setup_test_documents())
    except KeyboardInterrupt:
        print("\n\n⚠️  操作被用户中断")
    except Exception as e:
        print(f"\n\n❌ 设置失败: {e}")
        import traceback
        traceback.print_exc()