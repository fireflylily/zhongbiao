#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片配置构建器 - 统一的图片配置构建逻辑
从公司资质列表构建Word模板所需的图片配置

职责：
- 处理身份证（法人、授权人）的正反面
- 处理资质证书（ISO、CMMI、信用证明等）
- 处理营业执照、公章
- 支持多种命名规范（兼容性）
"""

from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

# 导入公共模块
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from common import get_module_logger

logger = get_module_logger("image_config_builder")


# 定义基础证件类型（需要特殊处理）
BASIC_CREDENTIALS = {
    'business_license',    # 营业执照
    'company_seal',        # 公章
    'legal_id_front',      # 法人身份证正面
    'legal_id_back',       # 法人身份证反面
    'auth_id_front',       # 授权人身份证正面
    'auth_id_back',        # 授权人身份证反面
    'id_card_front',       # 身份证正面（PersonnelTab使用）
    'id_card_back'         # 身份证反面（PersonnelTab使用）
}


def build_image_config(company_quals: List[Dict[str, Any]],
                      required_quals: Optional[List[Dict[str, Any]]] = None) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """
    从公司资质列表构建图片配置

    核心原则：
    1. 加载公司所有资质（不筛选）
    2. 由Word模板决定填充哪些（模板驱动）
    3. 可选：使用项目要求的insert_hint作为资质标题

    Args:
        company_quals: 公司所有资质列表（从数据库get_company_qualifications获取）
            每项包含：{
                'qualification_key': '资质键（如iso9001）',
                'file_path': '文件路径',
                'original_filename': '原始文件名'
            }
        required_quals: 项目资格要求列表（可选），用于提供insert_hint
            每项包含：{
                'qual_key': '资质键',
                'source_detail': '项目要求描述（用作insert_hint）'
            }

    Returns:
        (image_config, qualification_details) 元组:

        image_config: 图片配置字典
            {
                'license_path': '/path/to/营业执照.jpg',
                'seal_path': '/path/to/公章.png',
                'legal_id': {
                    'front': '/path/to/legal_front.jpg',
                    'back': '/path/to/legal_back.jpg'
                },
                'auth_id': {
                    'front': '/path/to/auth_front.jpg',
                    'back': '/path/to/auth_back.jpg'
                },
                'qualification_paths': ['/path/to/iso9001.jpg', ...],
                'qualification_details': [...]  # 见下方
            }

        qualification_details: 资质详细信息列表（用于精确插入和统计）
            [
                {
                    'qual_key': 'iso9001',
                    'file_path': '/path/to/iso9001.jpg',
                    'original_filename': 'ISO9001证书.jpg',
                    'insert_hint': 'ISO9001质量管理体系'  # 来自项目要求
                },
                ...
            ]
    """
    if not company_quals:
        logger.warning("公司没有上传任何资质文件")
        return ({}, [])

    logger.info(f"📋 开始构建图片配置，共 {len(company_quals)} 个资质")

    # 初始化配置
    image_config = {}
    qualification_paths = []
    qualification_details = []

    # 构建项目要求的insert_hint映射（qual_key -> insert_hint）
    insert_hint_map = {}
    if required_quals:
        for req_qual in required_quals:
            qual_key = req_qual.get('qual_key')
            insert_hint = req_qual.get('source_detail', '')
            if qual_key and insert_hint:
                insert_hint_map[qual_key] = insert_hint

    # 遍历所有资质，分类处理
    for qual in company_quals:
        qual_key = qual.get('qualification_key')
        file_path = qual.get('file_path')

        # 检查是否有PDF转换后的图片（优先使用转换后的图片）
        converted_images = qual.get('converted_images')
        pdf_pages = []  # 存储多页PDF的所有页面

        if converted_images:
            try:
                import json
                images = json.loads(converted_images)
                if images and len(images) > 0:
                    original_path = file_path

                    if len(images) > 1:
                        # 多页PDF：保存所有页面信息
                        pdf_pages = images
                        logger.info(f"  📄→🖼️ PDF已转换为{len(images)}页图片 (原PDF: {Path(original_path).name})")
                    else:
                        # 单页PDF：直接使用第一页
                        file_path = images[0]['file_path']
                        logger.info(f"  📄→🖼️ PDF已转换，使用图片: {Path(file_path).name}")
            except Exception as e:
                logger.warning(f"  ⚠️ 解析converted_images失败: {e}，使用原始文件")

        # 处理多页PDF的情况
        if pdf_pages:
            # 多页PDF：为每一页创建独立的配置项
            for img_data in pdf_pages:
                page_num = img_data.get('page_num', 1)
                page_path = img_data.get('file_path')

                # 只处理资质证书类型（不是身份证、营业执照等）
                if qual_key not in BASIC_CREDENTIALS:
                    qualification_paths.append(page_path)

                    qualification_detail = {
                        'qual_key': qual_key,
                        'file_path': page_path,
                        'original_filename': qual.get('original_filename', ''),
                        'insert_hint': insert_hint_map.get(qual_key, ''),
                        'page_num': page_num,  # 标记页码
                        'is_multi_page': True  # 标记为多页文档的一部分
                    }
                    qualification_details.append(qualification_detail)
                    logger.info(f"  ✅ 资质证书 ({qual_key}) 第{page_num}页: {Path(page_path).name}")

            # 多页PDF处理完成，跳过后续处理
            continue

        if not file_path:
            logger.warning(f"资质 {qual_key} 没有file_path，跳过")
            continue

        # === 1. 营业执照 ===
        if qual_key == 'business_license':
            image_config['license_path'] = file_path
            logger.info(f"  ✅ 营业执照: {file_path}")

        # === 2. 公章 ===
        elif qual_key == 'company_seal':
            image_config['seal_path'] = file_path
            logger.info(f"  ✅ 公章: {file_path}")

        # === 3. 法人身份证 ===
        elif qual_key == 'legal_id_front':
            if 'legal_id' not in image_config:
                image_config['legal_id'] = {}
            image_config['legal_id']['front'] = file_path
            logger.info(f"  ✅ 法人身份证正面: {file_path}")

        elif qual_key == 'legal_id_back':
            if 'legal_id' not in image_config:
                image_config['legal_id'] = {}
            image_config['legal_id']['back'] = file_path
            logger.info(f"  ✅ 法人身份证反面: {file_path}")

        # === 4. 授权代表身份证（支持多种字段名） ===
        elif qual_key in ['auth_id_front', 'id_card_front']:
            if 'auth_id' not in image_config:
                image_config['auth_id'] = {}
            image_config['auth_id']['front'] = file_path
            logger.info(f"  ✅ 授权代表身份证正面: {file_path}")

        elif qual_key in ['auth_id_back', 'id_card_back']:
            if 'auth_id' not in image_config:
                image_config['auth_id'] = {}
            image_config['auth_id']['back'] = file_path
            logger.info(f"  ✅ 授权代表身份证反面: {file_path}")

        # === 5. 所有其他资质（ISO、CMMI、信用证明、等保等） ===
        elif qual_key not in BASIC_CREDENTIALS:
            qualification_paths.append(file_path)

            # 构建详细信息（包含insert_hint）
            qualification_detail = {
                'qual_key': qual_key,
                'file_path': file_path,
                'original_filename': qual.get('original_filename', ''),
                'insert_hint': insert_hint_map.get(qual_key, '')  # 从项目要求获取
            }
            qualification_details.append(qualification_detail)

            logger.info(f"  ✅ 资质证书 ({qual_key}): {file_path}")

    # 添加资质证书列表到配置
    if qualification_paths:
        image_config['qualification_paths'] = qualification_paths
        image_config['qualification_details'] = qualification_details

    # 输出统计信息
    logger.info(f"📊 图片配置构建完成:")
    logger.info(f"  - 配置项数量: {len(image_config)} 个")
    logger.info(f"  - 资质证书数量: {len(qualification_paths)} 个")
    logger.info(f"  - 营业执照: {'✅' if 'license_path' in image_config else '❌'}")
    logger.info(f"  - 公章: {'✅' if 'seal_path' in image_config else '❌'}")
    logger.info(f"  - 法人身份证: {'✅' if 'legal_id' in image_config else '❌'}")
    logger.info(f"  - 授权人身份证: {'✅' if 'auth_id' in image_config else '❌'}")

    return (image_config, qualification_details)


def build_image_config_from_db(company_id: int,
                               project_name: Optional[str],
                               kb_manager) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """
    从数据库加载资质并构建图片配置（便捷函数）

    这是一个高级封装函数，整合了：
    1. 数据库查询（get_company_qualifications）
    2. 项目要求提取（extract_required_qualifications）
    3. 图片配置构建（build_image_config）

    Args:
        company_id: 公司ID
        project_name: 项目名称（可选）。用于获取项目资格要求
        kb_manager: 知识库管理器实例

    Returns:
        (image_config, required_quals) 元组:
        - image_config: 图片配置字典（包含所有资质）
        - required_quals: 项目资格要求列表（用于追加和统计），如果没有项目名称则为空列表
    """
    try:
        # 步骤1：获取公司的所有资质
        company_quals = kb_manager.db.get_company_qualifications(company_id)

        if not company_quals:
            logger.warning(f"公司 {company_id} 没有上传任何资质文件")
            return ({}, [])

        # 步骤2：获取项目资格要求（用于insert_hint和统计）
        required_quals = []
        if project_name:
            try:
                from .qualification_matcher import QualificationMatcher
                matcher = QualificationMatcher()

                # 从数据库查询项目资格要求
                query = """SELECT qualifications_data FROM tender_projects
                           WHERE company_id = ? AND project_name = ? LIMIT 1"""
                result = kb_manager.db.execute_query(query, [company_id, project_name])

                if result and len(result) > 0:
                    qualifications_data = result[0].get('qualifications_data')
                    if qualifications_data:
                        required_quals = matcher.extract_required_qualifications(qualifications_data)
                        logger.info(f"📊 项目资格要求: {len(required_quals)} 个")
            except Exception as e:
                logger.warning(f"获取项目资格要求失败（不影响处理）: {e}")

        # 步骤3：构建图片配置
        image_config, qualification_details = build_image_config(company_quals, required_quals)

        return (image_config, required_quals)

    except Exception as e:
        logger.error(f"从数据库构建图片配置失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return ({}, [])


__all__ = [
    'build_image_config',
    'build_image_config_from_db',
    'BASIC_CREDENTIALS'
]
