#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
资质匹配模块
功能:
- 从项目资格要求中提取需要的资质类型
- 智能匹配公司拥有的资质
- 支持模糊匹配和别名映射
"""

import json
import re
from typing import List, Dict, Any, Set
from pathlib import Path

# 导入公共模块
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from common import get_module_logger

logger = get_module_logger("qualification_matcher")


# 资质类型关键词映射表
QUALIFICATION_MAPPING = {
    'iso9001': {
        'keywords': ['ISO9001', 'ISO 9001', 'iso9001', '质量管理体系', '质量体系认证', 'GB/T19001'],
        'priority': 'high',
        'category': '质量管理'
    },
    'iso20000': {
        'keywords': ['ISO20000', 'ISO 20000', 'iso20000', 'IT服务管理体系', 'ITSM', 'GB/T20000'],
        'priority': 'medium',
        'category': 'IT服务'
    },
    'iso27001': {
        'keywords': ['ISO27001', 'ISO 27001', 'iso27001', '信息安全管理体系', 'ISMS', 'GB/T22080'],
        'priority': 'high',
        'category': '信息安全'
    },
    'cmmi': {
        'keywords': ['CMMI', 'cmmi', '软件能力成熟度', '软件成熟度', '能力成熟度模型'],
        'priority': 'high',
        'category': '软件能力'
    },
    'itss': {
        'keywords': ['ITSS', 'itss', 'IT运维服务能力成熟度', '信息技术服务标准'],
        'priority': 'medium',
        'category': 'IT运维'
    },
    'safety_production': {
        'keywords': ['安全生产许可证', '安全生产标准化', '安全生产'],
        'priority': 'medium',
        'category': '安全生产'
    },
    'software_copyright': {
        'keywords': ['软件著作权', '计算机软件著作权', '软著'],
        'priority': 'low',
        'category': '知识产权'
    },
    'patent_certificate': {
        'keywords': ['专利证书', '发明专利', '实用新型专利', '外观设计专利'],
        'priority': 'low',
        'category': '知识产权'
    },
    'business_license': {
        'keywords': ['营业执照', '营业执照副本', '工商营业执照'],
        'priority': 'high',
        'category': '基本资质'
    },
    'company_seal': {
        'keywords': ['公章', '企业公章', '印章'],
        'priority': 'medium',
        'category': '基本资质'
    },
    'basic_telecom_permit': {
        'keywords': ['基础电信业务许可证', '基础电信业务经营许可证', '电信业务经营许可证'],
        'priority': 'high',
        'category': '电信资质'
    },
    'value_added_telecom_permit': {
        'keywords': ['增值电信业务许可证', '增值电信业务经营许可证', 'ICP许可证', 'ISP许可证', 'IDC许可证'],
        'priority': 'high',
        'category': '电信资质'
    },
    'credit_china_check': {
        'keywords': ['信用中国', 'www.creditchina.gov.cn', '失信被执行人', '信用查询', '信用承诺书', '信用记录'],
        'priority': 'high',
        'category': '信用证明'
    },
    'tax_violation_check': {
        'keywords': ['重大税收违法', '税收违法案件', '税务违法', '税收黑名单'],
        'priority': 'high',
        'category': '信用证明'
    },
    'gov_procurement_check': {
        'keywords': ['政府采购', '严重违法失信', '政府采购黑名单', '政府采购违法'],
        'priority': 'high',
        'category': '信用证明'
    }
}


class QualificationMatcher:
    """资质匹配器"""

    def __init__(self):
        self.logger = get_module_logger("qualification_matcher")

    def extract_required_qualifications(self, qualifications_data: str | dict) -> List[Dict[str, Any]]:
        """
        从项目资格要求数据中提取需要的资质

        Args:
            qualifications_data: JSON字符串或字典,包含资格要求列表

        Returns:
            资质需求列表,每项包含:
            {
                'qual_key': '资质key (如iso9001)',
                'qual_name': '资质名称',
                'matched_keywords': ['匹配的关键词列表'],
                'source_detail': '原始要求描述',
                'priority': 'high/medium/low'
            }
        """
        try:
            # 解析JSON数据
            if isinstance(qualifications_data, str):
                data = json.loads(qualifications_data)
            else:
                data = qualifications_data

            # 如果数据是字典且有requirements键,提取requirements
            if isinstance(data, dict) and 'requirements' in data:
                requirements = data['requirements']
            elif isinstance(data, list):
                requirements = data
            else:
                self.logger.warning(f"无法识别的qualifications_data格式: {type(data)}")
                return []

            required_quals = []
            matched_qual_keys = set()  # 避免重复

            # 遍历所有要求
            for req in requirements:
                if not isinstance(req, dict):
                    continue

                # 只处理资质类别的要求
                category = req.get('category', '')
                if category != 'qualification':
                    continue

                detail = req.get('detail', '')
                subcategory = req.get('subcategory', '')

                # 合并detail和subcategory作为匹配文本
                match_text = f"{detail} {subcategory}"

                # 尝试匹配每个资质类型
                for qual_key, qual_info in QUALIFICATION_MAPPING.items():
                    # 跳过已匹配的资质
                    if qual_key in matched_qual_keys:
                        continue

                    # 检查是否包含关键词
                    matched_keywords = []
                    for keyword in qual_info['keywords']:
                        if keyword in match_text:
                            matched_keywords.append(keyword)

                    # 如果匹配到关键词,添加到结果
                    if matched_keywords:
                        required_quals.append({
                            'qual_key': qual_key,
                            'qual_name': qual_info['category'],
                            'matched_keywords': matched_keywords,
                            'source_detail': detail,
                            'priority': qual_info['priority'],
                            'constraint_type': req.get('constraint_type', 'optional')
                        })
                        matched_qual_keys.add(qual_key)
                        self.logger.info(f"✅ 匹配资质: {qual_key} - 关键词: {matched_keywords}")

            self.logger.info(f"📊 从资格要求中提取到 {len(required_quals)} 个资质需求")
            return required_quals

        except json.JSONDecodeError as e:
            self.logger.error(f"解析qualifications_data失败: {e}")
            return []
        except Exception as e:
            self.logger.error(f"提取资质需求失败: {e}")
            return []

    def match_company_qualifications(self,
                                     company_quals: List[Dict[str, Any]],
                                     required_quals: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        匹配公司资质和项目要求

        Args:
            company_quals: 公司拥有的资质列表 (来自数据库)
            required_quals: 项目要求的资质列表 (从extract_required_qualifications获取)

        Returns:
            匹配结果字典:
            {
                'matched': [
                    {
                        'qual_key': 'iso9001',
                        'file_path': '/path/to/iso9001.jpg',
                        'original_filename': 'ISO9001证书.jpg',
                        'insert_hint': 'ISO9001质量管理体系'
                    }
                ],
                'missing': ['iso14001', 'cmmi'],  # 项目要求但公司没有的
                'extra': ['iso20000'],  # 公司有但项目不要求的
                'stats': {
                    'total_required': 3,
                    'total_matched': 2,
                    'match_rate': 0.67
                }
            }
        """
        matched = []
        missing = []
        extra_qual_keys = set()

        # 构建公司资质字典 {qual_key: qual_data}
        company_quals_dict = {}
        for qual in company_quals:
            qual_key = qual.get('qualification_key')
            if qual_key:
                company_quals_dict[qual_key] = qual
                extra_qual_keys.add(qual_key)

        # 如果没有项目要求,返回空匹配
        if not required_quals:
            self.logger.info("📋 项目无资质要求,不插入资质证书")
            return {
                'matched': [],
                'missing': [],
                'extra': list(extra_qual_keys),
                'stats': {
                    'total_required': 0,
                    'total_matched': 0,
                    'match_rate': 0
                }
            }

        # 遍历项目要求,查找匹配的公司资质
        for req_qual in required_quals:
            qual_key = req_qual['qual_key']

            if qual_key in company_quals_dict:
                # 找到匹配
                company_qual = company_quals_dict[qual_key]
                matched.append({
                    'qual_key': qual_key,
                    'file_path': company_qual.get('file_path'),
                    'original_filename': company_qual.get('original_filename'),
                    'insert_hint': req_qual.get('source_detail', ''),
                    'matched_keywords': req_qual.get('matched_keywords', []),
                    'priority': req_qual.get('priority', 'medium'),
                    'constraint_type': req_qual.get('constraint_type', 'optional')
                })
                extra_qual_keys.discard(qual_key)  # 从额外资质中移除
                self.logger.info(f"✅ 匹配成功: {qual_key} - {company_qual.get('original_filename')}")
            else:
                # 缺失
                missing.append(qual_key)
                self.logger.warning(f"⚠️  缺失资质: {qual_key} (项目要求但公司未上传)")

        # 计算统计信息
        total_required = len(required_quals)
        total_matched = len(matched)
        match_rate = total_matched / total_required if total_required > 0 else 0

        result = {
            'matched': matched,
            'missing': missing,
            'extra': list(extra_qual_keys),
            'stats': {
                'total_required': total_required,
                'total_matched': total_matched,
                'match_rate': match_rate
            }
        }

        self.logger.info(f"📊 资质匹配完成:")
        self.logger.info(f"  - 要求数量: {total_required}")
        self.logger.info(f"  - 匹配数量: {total_matched}")
        self.logger.info(f"  - 匹配率: {match_rate*100:.1f}%")
        self.logger.info(f"  - 缺失资质: {missing if missing else '无'}")

        return result

    def build_image_config_from_match(self, match_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        根据匹配结果构建图片配置

        Args:
            match_result: 匹配结果 (从match_company_qualifications获取)

        Returns:
            图片配置字典:
            {
                'license_path': '/path/to/营业执照.jpg',
                'seal_path': '/path/to/公章.png',
                'qualification_paths': ['/path/to/iso9001.jpg', '/path/to/cmmi.jpg'],
                'qualification_details': [
                    {
                        'qual_key': 'iso9001',
                        'file_path': '/path/to/iso9001.jpg',
                        'insert_hint': 'ISO9001质量管理体系'
                    }
                ]
            }
        """
        image_config = {}
        qualification_paths = []
        qualification_details = []

        for matched_qual in match_result.get('matched', []):
            qual_key = matched_qual['qual_key']
            file_path = matched_qual.get('file_path')

            if not file_path:
                continue

            # 营业执照
            if qual_key == 'business_license':
                image_config['license_path'] = file_path
                self.logger.info(f"  - 营业执照: {file_path}")

            # 公章
            elif qual_key == 'company_seal':
                image_config['seal_path'] = file_path
                self.logger.info(f"  - 公章: {file_path}")

            # 资质证书
            elif qual_key in ['iso9001', 'iso20000', 'iso27001',
                             'cmmi', 'itss', 'safety_production',
                             'software_copyright', 'patent_certificate',
                             'basic_telecom_permit', 'value_added_telecom_permit',
                             'credit_china_check', 'tax_violation_check', 'gov_procurement_check']:
                qualification_paths.append(file_path)
                qualification_details.append(matched_qual)
                self.logger.info(f"  - 资质证书 ({qual_key}): {file_path}")

        # 添加资质证书列表
        if qualification_paths:
            image_config['qualification_paths'] = qualification_paths
            image_config['qualification_details'] = qualification_details

        self.logger.info(f"📋 构建图片配置完成: {len(image_config)} 个类型, {len(qualification_paths)} 个资质证书")

        return image_config


# 便捷函数
def match_qualifications_for_project(company_id: int, project_name: str, kb_manager) -> Dict[str, Any]:
    """
    为指定项目匹配资质的便捷函数

    Args:
        company_id: 公司ID
        project_name: 项目名称
        kb_manager: 知识库管理器实例

    Returns:
        图片配置字典
    """
    matcher = QualificationMatcher()

    # 1. 获取公司所有资质
    company_quals = kb_manager.db.get_company_qualifications(company_id)

    # 2. 获取项目资格要求
    required_quals = []
    if project_name:
        # 从数据库查询项目
        query = """SELECT qualifications_data FROM tender_projects
                   WHERE company_id = ? AND project_name = ? LIMIT 1"""
        result = kb_manager.db.execute_query(query, [company_id, project_name])

        if result and len(result) > 0:
            qualifications_data = result[0].get('qualifications_data')
            if qualifications_data:
                required_quals = matcher.extract_required_qualifications(qualifications_data)

    # 3. 匹配资质
    match_result = matcher.match_company_qualifications(company_quals, required_quals)

    # 4. 构建图片配置
    image_config = matcher.build_image_config_from_match(match_result)

    return image_config
