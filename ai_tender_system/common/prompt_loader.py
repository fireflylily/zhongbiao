#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多产品提示词加载器
支持根据产品类型和行业动态加载和渲染提示词模板
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from common import get_module_logger

logger = get_module_logger("prompt_loader")


class MultiProductPromptLoader:
    """
    多产品提示词加载器

    功能：
    1. 加载多产品提示词配置
    2. 根据产品类型动态渲染提示词
    3. 提供产品特定的关键词、证据清单、章节模板
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        初始化加载器

        Args:
            config_path: 配置文件路径，默认使用 outline_generation_multi_product.json
        """
        if config_path is None:
            prompts_dir = Path(__file__).parent.parent / "prompts"
            config_path = prompts_dir / "outline_generation_multi_product.json"

        self.config_path = Path(config_path)
        self.config = self._load_config()

        logger.info(f"多产品提示词配置已加载，支持产品: {self.config['metadata']['supported_products']}")

    def _load_config(self) -> Dict:
        """加载配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            raise

    def get_supported_products(self) -> List[str]:
        """获取支持的产品列表"""
        return self.config['metadata']['supported_products']

    def get_supported_industries(self) -> List[str]:
        """获取支持的行业列表"""
        return self.config['metadata']['supported_industries']

    def get_product_profile(self, product_type: str) -> Dict[str, Any]:
        """
        获取产品档案

        Args:
            product_type: 产品类型（如 telecom_data_service）

        Returns:
            产品档案字典，包含名称、描述、典型需求、关键技术等
        """
        profile = self.config['product_profiles'].get(product_type)
        if not profile:
            logger.warning(f"产品类型 '{product_type}' 不存在，使用通用配置")
            return {}
        return profile

    def get_industry_keywords(self, industry: str) -> Dict[str, List[str]]:
        """
        获取行业关键词

        Args:
            industry: 行业类型（如 telecom, government）

        Returns:
            包含 domain_terms, technical_terms, compliance_terms 的字典
        """
        keywords = self.config['industry_keywords'].get(industry)
        if not keywords:
            logger.warning(f"行业 '{industry}' 不存在，返回空关键词")
            return {"domain_terms": [], "technical_terms": [], "compliance_terms": []}
        return keywords

    def render_prompt(
        self,
        prompt_name: str,
        product_type: str,
        variables: Optional[Dict[str, str]] = None
    ) -> str:
        """
        渲染提示词模板

        Args:
            prompt_name: 提示词名称（如 analyze_requirements）
            product_type: 产品类型（如 telecom_data_service）
            variables: 额外的变量字典（如 {text: "招标文档内容"}）

        Returns:
            渲染后的提示词字符串
        """
        # 获取基础模板
        base_template = self.config['prompt_templates']['base'].get(prompt_name)
        if not base_template:
            raise ValueError(f"提示词 '{prompt_name}' 不存在")

        # 获取产品特定配置
        product_template = self.config['prompt_templates'].get(product_type, {})

        # 获取产品档案
        profile = self.get_product_profile(product_type)

        # 推断行业
        industry = self._infer_industry(product_type)
        keywords = self.get_industry_keywords(industry)

        # 构建替换变量
        template_vars = {
            'product_type': product_type,
            'product_name': profile.get('name', '通用产品'),
            'industry': industry,
            'product_context': product_template.get('product_context', ''),
            'industry_specific_categories': product_template.get('industry_specific_categories', ''),
            'product_priority_rules': product_template.get('product_priority_rules', ''),
            'product_evidence_rules': product_template.get('product_evidence_rules', ''),
            'domain_keywords': ', '.join(keywords.get('domain_terms', [])),
            'evidence_list': product_template.get('evidence_list', '[]'),
            'product_analysis_tips': product_template.get('product_analysis_tips', '')
        }

        # 合并用户提供的变量
        if variables:
            template_vars.update(variables)

        # 渲染模板
        try:
            rendered = base_template.format(**template_vars)
            return rendered
        except KeyError as e:
            logger.error(f"模板渲染失败，缺少变量: {e}")
            raise

    def _infer_industry(self, product_type: str) -> str:
        """根据产品类型推断行业"""
        industry_mapping = {
            'telecom_data_service': 'telecom',
            'government_platform': 'government',
            'smart_city': 'government',
            'financial_system': 'finance',
            'education_platform': 'education',
            'healthcare_system': 'healthcare'
        }
        return industry_mapping.get(product_type, 'general')

    def get_chapter_template(self, product_type: str) -> List[Dict]:
        """
        获取产品特定的章节模板

        Args:
            product_type: 产品类型

        Returns:
            章节模板列表
        """
        templates = self.config['chapter_templates'].get(product_type)
        if not templates:
            logger.warning(f"产品 '{product_type}' 没有预定义章节模板")
            return []
        return templates.get('typical_chapters', [])

    def get_evidence_checklist(self, product_type: str) -> List[str]:
        """
        获取产品所需的证明材料清单

        Args:
            product_type: 产品类型

        Returns:
            证明材料列表
        """
        profile = self.get_product_profile(product_type)
        return profile.get('common_evidence', [])

    def get_scoring_focus(self, product_type: str) -> List[str]:
        """
        获取产品的评分重点

        Args:
            product_type: 产品类型

        Returns:
            评分重点列表
        """
        profile = self.get_product_profile(product_type)
        return profile.get('scoring_focus', [])

    def auto_detect_product_type(self, requirement_text: str) -> str:
        """
        根据需求文本自动检测产品类型

        Args:
            requirement_text: 需求文本

        Returns:
            推测的产品类型
        """
        # 统计每个产品的关键词出现次数
        scores = {}

        for product_type in self.get_supported_products():
            profile = self.get_product_profile(product_type)
            score = 0

            # 检查典型需求关键词
            for req in profile.get('typical_requirements', []):
                if req in requirement_text:
                    score += 10

            # 检查关键技术术语
            for tech in profile.get('key_technologies', []):
                if tech in requirement_text:
                    score += 5

            scores[product_type] = score

        # 返回得分最高的产品类型
        if not scores or max(scores.values()) == 0:
            logger.warning("无法自动检测产品类型，使用默认产品")
            return 'telecom_data_service'  # 默认产品

        best_match = max(scores.items(), key=lambda x: x[1])
        logger.info(f"自动检测到产品类型: {best_match[0]} (得分: {best_match[1]})")
        return best_match[0]


# 示例用法
if __name__ == "__main__":
    # 初始化加载器
    loader = MultiProductPromptLoader()

    # 查看支持的产品
    print("支持的产品:", loader.get_supported_products())
    print()

    # 获取产品档案
    profile = loader.get_product_profile('telecom_data_service')
    print("通信运营商数据服务产品档案:")
    print(f"  名称: {profile['name']}")
    print(f"  典型需求: {profile['typical_requirements'][:3]}")
    print()

    # 获取行业关键词
    keywords = loader.get_industry_keywords('telecom')
    print("通信行业关键词:")
    print(f"  领域术语: {keywords['domain_terms'][:5]}")
    print()

    # 渲染提示词
    prompt = loader.render_prompt(
        prompt_name='analyze_requirements',
        product_type='telecom_data_service',
        variables={'text': '需要实现运营商三要素验证功能...'}
    )
    print("渲染后的提示词（前500字符）:")
    print(prompt[:500])
    print()

    # 获取证明材料清单
    evidence = loader.get_evidence_checklist('telecom_data_service')
    print("所需证明材料:")
    for item in evidence:
        print(f"  - {item}")
    print()

    # 自动检测产品类型
    test_text = "需要实现运营商三要素验证、在网状态查询、号码归属地查询功能"
    detected = loader.auto_detect_product_type(test_text)
    print(f"自动检测到产品类型: {detected}")
