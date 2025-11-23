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
- 智能筛选审计报告（年份、版本）
"""

import re
import json
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
    'legal_id_front',      # 法人身份证正面
    'legal_id_back',       # 法人身份证反面
    'auth_id_front',       # 被授权人身份证正面
    'auth_id_back',        # 被授权人身份证反面
    'id_card_front',       # 身份证正面（PersonnelTab使用）
    'id_card_back'         # 身份证反面（PersonnelTab使用）
}


# ==================== 审计报告智能筛选辅助函数 ====================

def _parse_years_requirement(requirement_text: str) -> int:
    """
    从项目要求中解析需要几年的审计报告

    Args:
        requirement_text: 项目要求描述文本

    Returns:
        需要的年份数（1-3），默认1

    Examples:
        "近三年审计报告" -> 3
        "近两年财务审计报告" -> 2
        "审计报告" -> 1
    """
    if not requirement_text:
        return 1

    # 定义年份模式（优先级从高到低）
    year_patterns = [
        (r'近[三3]年', 3),
        (r'近[二2两]年', 2),
        (r'近[一1]年', 1),
        (r'最近[三3]年', 3),
        (r'最近[二2两]年', 2),
        (r'最近[一1]年', 1),
        (r'[三3]年.*审计', 3),
        (r'[二2两]年.*审计', 2),
    ]

    for pattern, years in year_patterns:
        if re.search(pattern, requirement_text):
            logger.info(f"📅 识别年份要求: {years}年 (关键词: {pattern})")
            return years

    # 默认返回1年
    return 1


def _parse_fulltext_requirement(requirement_text: str) -> bool:
    """
    识别是否明确要求完整版审计报告

    Args:
        requirement_text: 项目要求描述文本

    Returns:
        True: 需要完整版  False: 默认关键页

    Examples:
        "完整的审计报告" -> True
        "审计报告全文" -> True
        "审计报告" -> False
    """
    if not requirement_text:
        return False

    # 完整版关键词
    fulltext_keywords = [
        '完整',
        '全文',
        '完整版',
        '完整的审计报告',
        '审计报告全文',
        '完整审计',
        '全本',
    ]

    for keyword in fulltext_keywords:
        if keyword in requirement_text:
            logger.info(f"📋 识别完整版要求: 关键词 '{keyword}'")
            return True

    return False


def _filter_audit_reports_by_year(
    all_audit_reports: List[Dict[str, Any]],
    required_years: int = 1,
    need_full_version: bool = False
) -> List[Dict[str, Any]]:
    """
    根据年份要求筛选审计报告

    Args:
        all_audit_reports: 所有审计报告列表
        required_years: 需要的年份数（1-3）
        need_full_version: 是否需要完整版

    Returns:
        筛选后的审计报告列表（按年份降序）
    """
    if not all_audit_reports:
        return []

    # 1. 按年份分组（使用 file_version 字段）
    year_groups = {}
    for audit in all_audit_reports:
        year = audit.get('file_version')
        if year:
            try:
                year = int(year)
                if year not in year_groups:
                    year_groups[year] = []
                year_groups[year].append(audit)
            except (ValueError, TypeError):
                logger.warning(f"无效的年份值: {year}, 文件: {audit.get('original_filename')}")
                continue

    if not year_groups:
        logger.warning("所有审计报告都缺少有效的 file_version 字段")
        # 降级策略：按上传时间排序取最新的
        sorted_audits = sorted(all_audit_reports,
                              key=lambda x: x.get('upload_time', ''),
                              reverse=True)
        return sorted_audits[:required_years]

    # 2. 按年份降序排序
    sorted_years = sorted(year_groups.keys(), reverse=True)

    logger.info(f"📊 审计报告年份分布: {dict((y, len(year_groups[y])) for y in sorted_years)}")

    # 3. 取最新的N年
    selected_years = sorted_years[:required_years]
    logger.info(f"✅ 选择年份: {selected_years} (共{required_years}年)")

    # 4. 为每个年份选择最佳版本
    selected_audits = []
    for year in selected_years:
        audits_this_year = year_groups[year]

        if len(audits_this_year) == 1:
            # 只有一个版本，直接使用
            selected_audits.append(audits_this_year[0])
            logger.info(f"  {year}年: 使用唯一版本 {audits_this_year[0]['original_filename']}")
        else:
            # 多个版本，选择最佳的
            best = _select_best_audit_version(audits_this_year, need_full_version)
            selected_audits.append(best)
            logger.info(f"  {year}年: 从{len(audits_this_year)}个版本中选择 {best['original_filename']}")

    return selected_audits


def _select_best_audit_version(
    audits_same_year: List[Dict[str, Any]],
    need_full_version: bool = False
) -> Dict[str, Any]:
    """
    为同一年份选择最佳审计报告版本

    选择策略：
    1. 如果需要完整版：完整版 > 关键页版
    2. 如果默认（关键页）：关键页版 > 完整版
    3. 同优先级：已转换PDF > 未转换PDF
    4. 同优先级：file_sequence 小的优先

    Args:
        audits_same_year: 同一年份的所有审计报告
        need_full_version: 是否需要完整版

    Returns:
        最佳版本的审计报告
    """
    if len(audits_same_year) == 1:
        return audits_same_year[0]

    # 为每个版本打分
    scored_audits = []

    for audit in audits_same_year:
        score = 0
        filename = audit.get('original_filename', '').lower()
        file_size = audit.get('file_size', 0)
        converted = audit.get('converted_images')
        sequence = audit.get('file_sequence', 999)

        # 1. 判断版本类型
        is_key_pages = any(kw in filename for kw in ['关键页', '摘要', '精简', 'key', 'summary'])
        is_full = any(kw in filename for kw in ['完整', '全文', 'full', 'complete'])

        # 如果文件名没有明确标注，通过文件大小推断
        if not is_key_pages and not is_full:
            if file_size < 5 * 1024 * 1024:  # < 5MB
                is_key_pages = True
            elif file_size > 10 * 1024 * 1024:  # > 10MB
                is_full = True

        # 2. 根据项目要求打分
        if need_full_version:
            # 需要完整版
            if is_full:
                score += 100
            elif is_key_pages:
                score += 50  # 关键页也可用，但完整版更好
        else:
            # 默认：关键页优先（节省空间）
            if is_key_pages:
                score += 100
            elif is_full:
                score += 50  # 完整版也可用，但关键页更好

        # 3. 已转换PDF加分（可以直接插入）
        if converted:
            score += 30

        # 4. file_sequence 小的加分（主文件）
        score -= sequence

        scored_audits.append((score, audit))
        logger.debug(f"    评分: {score} - {filename}")

    # 返回得分最高的
    best_score, best_audit = max(scored_audits, key=lambda x: x[0])
    logger.info(f"    最佳版本 (得分{best_score}): {best_audit['original_filename']}")

    return best_audit


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

    # 【新增】收集所有审计报告，稍后统一筛选
    audit_reports = []

    # 遍历所有资质，分类处理
    for qual in company_quals:
        qual_key = qual.get('qualification_key')
        file_path = qual.get('file_path')

        # 【新增】审计报告单独收集，稍后统一筛选
        if qual_key == 'audit_report':
            audit_reports.append(qual)
            continue  # 跳过正常处理流程

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

        # === 2. 法人身份证 ===
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

        # === 4. 被授权人身份证（支持多种字段名） ===
        elif qual_key in ['auth_id_front', 'id_card_front']:
            if 'auth_id' not in image_config:
                image_config['auth_id'] = {}
            image_config['auth_id']['front'] = file_path
            logger.info(f"  ✅ 被授权人身份证正面: {file_path}")

        elif qual_key in ['auth_id_back', 'id_card_back']:
            if 'auth_id' not in image_config:
                image_config['auth_id'] = {}
            image_config['auth_id']['back'] = file_path
            logger.info(f"  ✅ 被授权人身份证反面: {file_path}")

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

    # 【新增】统一处理审计报告（循环结束后）
    if audit_reports:
        logger.info(f"\n📊 开始处理审计报告，共收集到 {len(audit_reports)} 份")

        # 1. 解析项目要求
        audit_requirement = insert_hint_map.get('audit_report', '')
        required_years = _parse_years_requirement(audit_requirement)
        need_full_version = _parse_fulltext_requirement(audit_requirement)

        logger.info(f"📋 项目要求: {required_years}年审计报告, 完整版={'是' if need_full_version else '否'}")

        # 2. 筛选审计报告（按年份、版本）
        selected_audits = _filter_audit_reports_by_year(
            audit_reports,
            required_years=required_years,
            need_full_version=need_full_version
        )

        logger.info(f"✅ 筛选完成，最终选择 {len(selected_audits)} 份审计报告")

        # 3. 处理筛选后的审计报告（复用现有逻辑）
        for audit in selected_audits:
            year = audit.get('file_version', '未知')
            audit_file_path = audit.get('file_path')
            converted_images = audit.get('converted_images')

            # 处理PDF转换
            if converted_images:
                try:
                    images = json.loads(converted_images)
                    if images and len(images) > 0:
                        logger.info(f"  📄 {year}年审计报告: {len(images)}页已转换")

                        # 为每一页创建配置项
                        for img_data in images:
                            page_num = img_data.get('page_num', 1)
                            page_path = img_data.get('file_path')

                            qualification_paths.append(page_path)

                            qualification_detail = {
                                'qual_key': 'audit_report',
                                'file_path': page_path,
                                'original_filename': audit.get('original_filename', ''),
                                'insert_hint': insert_hint_map.get('audit_report', ''),
                                'page_num': page_num,
                                'is_multi_page': len(images) > 1,
                                'audit_year': year  # 【新增】标记年份
                            }
                            qualification_details.append(qualification_detail)

                        logger.info(f"  ✅ {year}年审计报告 ({audit['original_filename']}): {len(images)}页")
                except Exception as e:
                    logger.warning(f"  ⚠️ 解析{year}年审计报告converted_images失败: {e}")
            else:
                # 未转换的PDF，记录警告
                logger.warning(f"  ⚠️ {year}年审计报告未转换，无法插入: {audit['original_filename']}")

    # 添加资质证书列表到配置
    if qualification_paths:
        image_config['qualification_paths'] = qualification_paths
        image_config['qualification_details'] = qualification_details

    # 输出统计信息
    logger.info(f"📊 图片配置构建完成:")
    logger.info(f"  - 配置项数量: {len(image_config)} 个")
    logger.info(f"  - 资质证书数量: {len(qualification_paths)} 个")
    logger.info(f"  - 营业执照: {'✅' if 'license_path' in image_config else '❌'}")
    logger.info(f"  - 法人身份证: {'✅' if 'legal_id' in image_config else '❌'}")
    logger.info(f"  - 被授权人身份证: {'✅' if 'auth_id' in image_config else '❌'}")

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
