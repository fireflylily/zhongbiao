#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
公司管理API蓝图
处理公司信息和资质证书的CRUD操作
"""

import json
import base64
import shutil
from pathlib import Path
from datetime import datetime
from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename

# 导入公共组件
import sys
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from common import get_module_logger, get_config, format_error_response
from web.shared.instances import get_kb_manager

# 创建logger
logger = get_module_logger('api_companies')

# 创建蓝图
api_companies_bp = Blueprint('api_companies', __name__, url_prefix='/api')

# 获取知识库管理器实例
kb_manager = get_kb_manager()


# ===================
# 公司管理API
# ===================

@api_companies_bp.route('/companies')
def list_companies():
    """获取所有公司配置"""
    try:
        companies = kb_manager.get_companies()

        # 转换字段格式以保持前端兼容性，过滤无效公司ID
        result_companies = []
        for company in companies:
            company_id = company.get('company_id')
            # 跳过没有有效 company_id 的记录
            if company_id is None:
                logger.warning(f"跳过无效的公司记录，company_id为None: {company.get('company_name', '未知')}")
                continue

            company_name = company.get('company_name', '未命名公司')
            result_companies.append({
                'company_id': company_id,
                'name': company_name,  # 前端 el-select 需要的字段
                'company_name': company_name,  # 保持向后兼容
                'social_credit_code': company.get('social_credit_code', ''),
                'legal_representative': company.get('legal_representative', ''),
                'registered_capital': company.get('registered_capital', ''),
                'employee_count': company.get('employee_count', ''),
                'created_at': company.get('created_at', ''),
                'updated_at': company.get('updated_at', ''),
                'product_count': company.get('product_count', 0),
                'document_count': company.get('document_count', 0),
                # 被授权人信息 - 用于项目自动填充
                'authorized_person_name': company.get('authorized_person_name', ''),
                'authorized_person_id': company.get('authorized_person_id', '')
            })

        # 安全排序，处理可能的 None 值
        result_companies.sort(key=lambda x: x.get('updated_at') or '', reverse=True)
        return jsonify({'success': True, 'data': result_companies})

    except Exception as e:
        logger.error(f"获取公司列表失败: {e}")
        return jsonify({'error': str(e)}), 500


@api_companies_bp.route('/companies/<company_id>')
def get_company(company_id):
    """获取指定公司的详细信息"""
    try:
        # 转换字符串ID为整数ID
        company_id_int = int(company_id)

        company_data = kb_manager.get_company_detail(company_id_int)

        # DEBUG: 记录从数据库获取的原始数据
        logger.info(f"[DEBUG GET] 公司 {company_id} - 数据库返回的原始数据: {company_data}")
        if company_data and 'registered_capital' in company_data:
            logger.info(f"[DEBUG GET] registered_capital 字段存在: {company_data['registered_capital']!r}")
        elif company_data:
            logger.info(f"[DEBUG GET] registered_capital 字段不在返回数据中，可用字段: {list(company_data.keys())}")

        if not company_data:
            return jsonify({'success': False, 'error': '公司不存在'}), 404

        # 转换字段格式以保持前端兼容性 - 保持原有格式
        result_company = company_data

        return jsonify({'success': True, 'data': result_company})

    except ValueError:
        return jsonify({'success': False, 'error': '无效的公司ID'}), 400
    except Exception as e:
        logger.error(f"获取公司信息失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_companies_bp.route('/companies', methods=['POST'])
def create_company():
    """创建新公司"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': '请提供公司信息'}), 400

        company_name = data.get('companyName', '').strip()
        if not company_name:
            return jsonify({'success': False, 'error': '公司名称不能为空'}), 400

        # 使用知识库管理器创建公司
        result = kb_manager.create_company(
            company_name=company_name,
            company_code=data.get('companyCode', None),
            industry_type=data.get('industryType', None),
            description=data.get('companyDescription', None)
        )

        if result['success']:
            # 返回格式与前端兼容
            company_data = {
                'id': str(result['company_id']),
                'companyName': company_name,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }

            logger.info(f"创建公司成功: {company_name} (ID: {result['company_id']})")
            return jsonify({'success': True, 'company': company_data})
        else:
            return jsonify({'success': False, 'error': result['error']}), 400

    except Exception as e:
        logger.error(f"创建公司失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_companies_bp.route('/companies/<company_id>', methods=['PUT'])
def update_company(company_id):
    """更新公司信息"""
    try:
        # 转换字符串ID为整数ID
        company_id_int = int(company_id)

        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': '请提供公司信息'}), 400

        # 🆕 自动提取控股股东和实际控制人信息
        if 'shareholders_info' in data:
            try:
                # 解析股东信息JSON
                shareholders = data['shareholders_info']
                if isinstance(shareholders, str):
                    shareholders = json.loads(shareholders)

                # 查找标记为控股股东的股东
                controlling = next((s for s in shareholders if s.get('is_controlling')), None)
                if controlling:
                    # 格式：股东名称，出资比例
                    data['controlling_shareholder'] = f"{controlling['name']}，{controlling['ratio']}"
                    logger.info(f"自动提取控股股东: {data['controlling_shareholder']}")
                else:
                    # 如果没有标记，保持原值或设为空
                    if 'controlling_shareholder' not in data:
                        data['controlling_shareholder'] = ''

                # 查找标记为实际控制人的股东
                actual_controller = next((s for s in shareholders if s.get('is_actual_controller')), None)
                if actual_controller:
                    # 格式：只保存名称
                    data['actual_controller'] = actual_controller['name']
                    logger.info(f"自动提取实际控制人: {data['actual_controller']}")
                else:
                    # 如果没有标记，保持原值或设为空
                    if 'actual_controller' not in data:
                        data['actual_controller'] = ''

            except json.JSONDecodeError as e:
                logger.warning(f"解析股东信息JSON失败: {e}")
            except Exception as e:
                logger.error(f"提取控股股东/实际控制人信息失败: {e}")

        # 使用知识库管理器更新公司信息
        result = kb_manager.update_company(company_id_int, data)

        if result['success']:
            # 获取更新后的公司详情
            updated_company = kb_manager.get_company_detail(company_id_int)

            if updated_company:
                # 转换格式与前端兼容
                result_company = {
                    'id': str(updated_company.get('company_id', '')),
                    'companyName': updated_company.get('company_name', ''),
                    'establishDate': updated_company.get('establish_date', ''),
                    'legalRepresentative': updated_company.get('legal_representative', ''),
                    'legalRepresentativePosition': updated_company.get('legal_representative_position', ''),
                    'legalRepresentativeGender': updated_company.get('legal_representative_gender', ''),
                    'legalRepresentativeAge': updated_company.get('legal_representative_age', ''),
                    'socialCreditCode': updated_company.get('social_credit_code', ''),
                    'registeredCapital': updated_company.get('registered_capital', ''),
                    'companyType': updated_company.get('company_type', ''),
                    'registeredAddress': updated_company.get('registered_address', ''),
                    'businessScope': updated_company.get('business_scope', ''),
                    'companyDescription': updated_company.get('description', ''),
                    'fixedPhone': updated_company.get('fixed_phone', ''),
                    'fax': updated_company.get('fax', ''),
                    'postalCode': updated_company.get('postal_code', ''),
                    'email': updated_company.get('email', ''),
                    'officeAddress': updated_company.get('office_address', ''),
                    'employeeCount': updated_company.get('employee_count', ''),
                    # 财务信息
                    'bank_name': updated_company.get('bank_name', ''),
                    'bank_account': updated_company.get('bank_account', ''),
                    # 股权结构信息
                    'actual_controller': updated_company.get('actual_controller', ''),
                    'controlling_shareholder': updated_company.get('controlling_shareholder', ''),
                    'shareholders_info': updated_company.get('shareholders_info', '[]'),
                    # 管理关系信息
                    'managing_unit_name': updated_company.get('managing_unit_name', ''),
                    'managed_unit_name': updated_company.get('managed_unit_name', ''),
                    # 被授权人信息
                    'authorized_person_name': updated_company.get('authorized_person_name', ''),
                    'authorized_person_id': updated_company.get('authorized_person_id', ''),
                    'authorized_person_gender': updated_company.get('authorized_person_gender', ''),
                    'authorized_person_position': updated_company.get('authorized_person_position', ''),
                    'authorized_person_title': updated_company.get('authorized_person_title', ''),
                    'authorized_person_age': updated_company.get('authorized_person_age', ''),
                    'created_at': updated_company.get('created_at', ''),
                    'updated_at': updated_company.get('updated_at', '')
                }

                logger.info(f"更新公司成功: {updated_company.get('company_name', '')} (ID: {company_id})")
                return jsonify({'success': True, 'company': result_company, 'message': '公司信息更新成功'})
            else:
                return jsonify({'success': False, 'error': '获取更新后的公司信息失败'}), 500
        else:
            return jsonify({'success': False, 'error': result['error']}), 400

    except ValueError:
        return jsonify({'success': False, 'error': '无效的公司ID'}), 400
    except Exception as e:
        logger.error(f"更新公司失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_companies_bp.route('/companies/<company_id>', methods=['DELETE'])
def delete_company(company_id):
    """删除公司"""
    try:
        # 转换字符串ID为整数ID
        company_id_int = int(company_id)

        # 使用知识库管理器删除公司
        result = kb_manager.delete_company(company_id_int)

        if result['success']:
            logger.info(f"删除公司成功: {company_id}")
            return jsonify({'success': True, 'message': '公司删除成功'})
        else:
            if '不存在' in result['error']:
                return jsonify({'success': False, 'error': result['error']}), 404
            else:
                return jsonify({'success': False, 'error': result['error']}), 500

    except ValueError:
        return jsonify({'success': False, 'error': '无效的公司ID'}), 400
    except Exception as e:
        logger.error(f"删除公司失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_companies_bp.route('/companies/<company_id>/qualifications')
def get_company_qualifications(company_id):
    """获取公司资质文件列表（支持多文件）"""
    try:
        # 验证公司ID并获取资质列表
        try:
            company_id_int = int(company_id)
            # 使用数据库方法获取资质列表
            qualifications = kb_manager.get_company_qualifications(company_id_int)

            # 转换为前端期望的格式 - 支持多文件
            qualifications_dict = {}
            for qual in qualifications:
                qual_key = qual['qualification_key']
                allow_multiple = qual.get('allow_multiple_files', False)

                file_info = {
                    'qualification_id': qual['qualification_id'],
                    'original_filename': qual['original_filename'],
                    'safe_filename': qual['safe_filename'],
                    'file_size': qual['file_size'],
                    'upload_time': qual['upload_time'],
                    'custom_name': qual.get('custom_name'),
                    'expire_date': qual.get('expire_date'),
                    'verify_status': qual.get('verify_status', 'pending'),
                    'file_version': qual.get('file_version'),
                    'file_sequence': qual.get('file_sequence', 1),
                    'is_primary': qual.get('is_primary', True)
                }

                if allow_multiple:
                    # 多文件资质：返回文件数组
                    if qual_key not in qualifications_dict:
                        qualifications_dict[qual_key] = {
                            'allow_multiple_files': True,
                            'version_label': qual.get('version_label', '版本'),
                            'files': []
                        }
                    qualifications_dict[qual_key]['files'].append(file_info)
                else:
                    # 单文件资质：返回单个对象（保持向后兼容）
                    qualifications_dict[qual_key] = {
                        'allow_multiple_files': False,
                        **file_info
                    }

            logger.info(f"获取公司 {company_id} 的资质文件列表，共 {len(qualifications_dict)} 个资质类型")
            return jsonify({
                'success': True,
                'data': qualifications_dict
            })

        except ValueError:
            return jsonify({'success': False, 'error': '无效的公司ID'}), 400

    except Exception as e:
        logger.error(f"获取公司资质文件失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_companies_bp.route('/companies/<company_id>/qualifications/upload', methods=['POST'])
def upload_company_qualifications(company_id):
    """上传公司资质文件（支持多文件版本和PDF自动转换）"""
    try:
        # 导入PDF处理工具
        from common.pdf_utils import PDFDetector, get_pdf_converter
        from datetime import datetime

        # 首先检查数据库中是否存在该公司
        try:
            company_id_int = int(company_id)
            company_data = kb_manager.get_company_detail(company_id_int)
            if not company_data:
                return jsonify({'success': False, 'error': '公司不存在'}), 404
        except ValueError:
            return jsonify({'success': False, 'error': '无效的公司ID'}), 400

        # 处理上传的文件
        uploaded_files = {}
        pdf_conversions = {}  # 记录PDF转换信息
        qualification_names = request.form.get('qualification_names', '{}')
        qualification_names = json.loads(qualification_names) if qualification_names else {}

        # 获取文件版本信息（可选）
        file_versions = request.form.get('file_versions', '{}')
        file_versions = json.loads(file_versions) if file_versions else {}

        for key, file in request.files.items():
            if key.startswith('qualifications[') and file.filename:
                # 提取资质键名
                qual_key = key.replace('qualifications[', '').replace(']', '')

                # 获取文件版本（如果有）
                file_version = file_versions.get(qual_key)

                # 使用数据库方法上传资质文件
                result = kb_manager.upload_qualification(
                    company_id=company_id_int,
                    qualification_key=qual_key,
                    file_obj=file,
                    original_filename=file.filename,
                    qualification_name=qualification_names.get(qual_key, qual_key),
                    custom_name=qualification_names.get(qual_key) if qual_key.startswith('custom') else None,
                    file_version=file_version  # 新增：文件版本参数
                )

                if result['success']:
                    uploaded_files[qual_key] = {
                        'filename': file.filename,
                        'qualification_id': result['qualification_id'],
                        'message': result['message'],
                        'file_version': file_version
                    }

                    # 检测并转换PDF文件
                    if result.get('file_path'):
                        saved_path = result['file_path']

                        # 检测是否为PDF
                        if PDFDetector.is_pdf(saved_path):
                            logger.info(f"检测到PDF文件: {file.filename}，准备转换为图片")

                            # 获取配置好的PDF转换器
                            converter = get_pdf_converter(qual_key)

                            # 转换PDF为图片
                            conversion_result = converter.convert_to_images(
                                saved_path,
                                custom_prefix=qual_key
                            )

                            if conversion_result['success']:
                                pdf_conversions[qual_key] = conversion_result

                                # 更新数据库记录，保存转换信息
                                try:
                                    kb_manager.db.execute_query("""
                                        UPDATE company_qualifications
                                        SET
                                            original_file_type = 'PDF',
                                            converted_images = ?,
                                            conversion_info = ?,
                                            conversion_date = ?
                                        WHERE qualification_id = ?
                                    """, [
                                        json.dumps(conversion_result['images']),
                                        json.dumps({
                                            'total_pages': conversion_result['total_pages'],
                                            'output_dir': conversion_result['output_dir'],
                                            'dpi': converter.config.dpi,
                                            'format': converter.config.output_format
                                        }),
                                        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                        result['qualification_id']
                                    ])

                                    logger.info(f"PDF转换成功: {qual_key}, 共{conversion_result['total_pages']}页")
                                    uploaded_files[qual_key]['pdf_conversion'] = {
                                        'total_pages': conversion_result['total_pages'],
                                        'output_dir': conversion_result['output_dir']
                                    }
                                except Exception as e:
                                    logger.error(f"保存PDF转换信息失败: {e}")
                            else:
                                logger.warning(f"PDF转换失败: {conversion_result.get('error')}")

        logger.info(f"公司 {company_id} 上传了 {len(uploaded_files)} 个资质文件")
        if pdf_conversions:
            logger.info(f"其中 {len(pdf_conversions)} 个PDF文件已自动转换为图片")

        return jsonify({
            'success': True,
            'message': f'成功上传 {len(uploaded_files)} 个资质文件',
            'uploaded_files': uploaded_files,
            'pdf_conversions': len(pdf_conversions)  # 返回PDF转换数量
        })

    except Exception as e:
        logger.error(f"上传公司资质文件失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_companies_bp.route('/companies/<company_id>/qualifications/<qualification_key>/download')
def download_qualification_file(company_id, qualification_key):
    """下载公司资质文件"""
    try:
        # 验证公司ID
        try:
            company_id_int = int(company_id)
            company_data = kb_manager.get_company_detail(company_id_int)
            if not company_data:
                return jsonify({'success': False, 'error': '公司不存在'}), 404
        except ValueError:
            return jsonify({'success': False, 'error': '无效的公司ID'}), 400

        # 从数据库获取资质文件信息
        qualification = kb_manager.db.get_qualification_by_key(company_id_int, qualification_key)
        if not qualification:
            return jsonify({'success': False, 'error': '资质文件不存在'}), 404

        # 检查文件是否存在
        file_path = Path(qualification['file_path'])
        if not file_path.exists():
            return jsonify({'success': False, 'error': '文件不存在'}), 404

        # 返回文件
        original_filename = qualification['original_filename']
        logger.info(f"下载资质文件: {original_filename}")
        return send_file(str(file_path), as_attachment=True, download_name=original_filename)

    except Exception as e:
        logger.error(f"下载资质文件失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_companies_bp.route('/companies/<company_id>/qualifications/<qualification_key>/preview')
def preview_qualification_file(company_id, qualification_key):
    """预览资质文件 - 返回JSON格式（符合全站架构）"""
    try:
        # 验证公司ID
        try:
            company_id_int = int(company_id)
            company_data = kb_manager.get_company_detail(company_id_int)
            if not company_data:
                return jsonify({'success': False, 'error': '公司不存在'}), 404
        except ValueError:
            return jsonify({'success': False, 'error': '无效的公司ID'}), 400

        # 从数据库获取资质文件信息
        qualification = kb_manager.db.get_qualification_by_key(company_id_int, qualification_key)
        if not qualification:
            return jsonify({'success': False, 'error': '资质文件不存在'}), 404

        # 检查文件是否存在
        file_path = Path(qualification['file_path'])
        if not file_path.exists():
            return jsonify({'success': False, 'error': '文件不存在'}), 404

        file_type = qualification['file_type'].lower() if qualification['file_type'] else ''
        filename = qualification['original_filename']

        # 根据文件类型生成HTML内容
        if file_type in ['png', 'jpg', 'jpeg', 'gif', 'bmp']:
            # 图片：base64编码嵌入
            with open(file_path, 'rb') as f:
                img_data = base64.b64encode(f.read()).decode()
            html_content = f'''
                <div class="text-center p-4">
                    <img src="data:image/{file_type};base64,{img_data}"
                         class="img-fluid"
                         style="max-width: 100%; height: auto; box-shadow: 0 2px 8px rgba(0,0,0,0.1);" />
                </div>
            '''
        elif file_type == 'pdf':
            # PDF：提示下载
            html_content = f'''
                <div class="alert alert-info m-4">
                    <h5><i class="bi bi-file-pdf"></i> PDF文档预览</h5>
                    <p class="mb-0">文件名: {filename}</p>
                    <p class="text-muted">PDF预览功能正在开发中，请使用下载功能查看完整内容。</p>
                </div>
            '''
        else:
            return jsonify({'success': False, 'error': f'不支持的文件格式: {file_type}'}), 400

        logger.info(f"预览资质文件: {filename}")
        return jsonify({
            'success': True,
            'content': html_content,
            'filename': filename
        })

    except Exception as e:
        logger.error(f"预览资质文件失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_companies_bp.route('/companies/<company_id>/qualifications/<qualification_key>', methods=['DELETE'])
def delete_qualification_file(company_id, qualification_key):
    """删除公司资质文件"""
    try:
        # 验证公司ID
        try:
            company_id_int = int(company_id)
            company_data = kb_manager.get_company_detail(company_id_int)
            if not company_data:
                return jsonify({'success': False, 'error': '公司不存在'}), 404
        except ValueError:
            return jsonify({'success': False, 'error': '无效的公司ID'}), 400

        # 使用新的数据库方法删除资质文件
        result = kb_manager.delete_qualification_by_key(company_id_int, qualification_key)

        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400

    except Exception as e:
        logger.error(f"删除资质文件失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_companies_bp.route('/qualifications/<int:qualification_id>/download')
def download_qualification_by_id(qualification_id):
    """通过资质ID下载文件（用于多文件资质）"""
    try:
        # 从数据库获取资质文件信息
        qualification = kb_manager.db.get_qualification_by_id(qualification_id)
        if not qualification:
            return jsonify({'success': False, 'error': '资质文件不存在'}), 404

        # 检查文件是否存在
        file_path = Path(qualification['file_path'])
        if not file_path.exists():
            return jsonify({'success': False, 'error': '文件不存在'}), 404

        # 返回文件
        original_filename = qualification['original_filename']
        logger.info(f"下载资质文件 (ID={qualification_id}): {original_filename}")
        return send_file(str(file_path), as_attachment=True, download_name=original_filename)

    except Exception as e:
        logger.error(f"下载资质文件失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_companies_bp.route('/qualifications/<int:qualification_id>', methods=['DELETE'])
def delete_qualification_by_id(qualification_id):
    """通过资质ID删除文件（用于多文件资质）"""
    try:
        # 从数据库获取资质文件信息
        qualification = kb_manager.db.get_qualification_by_id(qualification_id)
        if not qualification:
            return jsonify({'success': False, 'error': '资质文件不存在'}), 404

        # 删除物理文件
        file_path = Path(qualification['file_path'])
        if file_path.exists():
            file_path.unlink()
            logger.info(f"删除物理文件: {file_path}")

        # 删除数据库记录
        result = kb_manager.db.delete_qualification(qualification_id)
        if result:
            logger.info(f"删除资质文件成功 (ID={qualification_id})")
            return jsonify({'success': True, 'message': '资质文件删除成功'})
        else:
            return jsonify({'success': False, 'error': '删除数据库记录失败'}), 500

    except Exception as e:
        logger.error(f"删除资质文件失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# 导出蓝图
__all__ = ['api_companies_bp']
