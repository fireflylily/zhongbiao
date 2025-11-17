#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
案例库管理器
功能：案例信息、合同信息、附件的业务逻辑处理
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from common.database import get_knowledge_base_db
from common.logger import get_module_logger
from common.config import get_config

logger = get_module_logger("case_library.manager")


class CaseLibraryManager:
    """案例库管理器"""

    def __init__(self):
        self.db = get_knowledge_base_db()
        self.config = get_config()

        # 获取上传目录
        self.upload_dir = self.config.get_path('uploads')
        self.upload_dir.mkdir(exist_ok=True)

        # 案例附件子目录
        self.case_attachments_dir = self.upload_dir / 'case_attachments'
        self.case_attachments_dir.mkdir(exist_ok=True)

        logger.info("案例库管理器初始化完成")

    # =========================
    # 案例管理相关方法
    # =========================

    def create_case(self, company_id: int, data: Dict) -> Dict:
        """创建案例"""
        try:
            logger.info(f"开始创建案例，company_id: {company_id}")

            # 验证必填字段
            required_fields = ['case_title', 'customer_name', 'contract_type']
            for field in required_fields:
                if not data.get(field):
                    error_msg = f'字段 {field} 不能为空'
                    logger.warning(f"必填字段验证失败: {error_msg}, 当前值: {data.get(field)}")
                    return {
                        'success': False,
                        'error': error_msg
                    }

            # 构建插入数据
            insert_data = {
                'company_id': company_id,
                'product_id': data.get('product_id'),
                'product_category': data.get('product_category'),
                'case_title': data['case_title'],
                'case_number': data.get('case_number'),
                'customer_name': data['customer_name'],
                'industry': data.get('industry'),
                'contract_name': data.get('contract_name'),
                'contract_type': data['contract_type'],
                'final_customer_name': data.get('final_customer_name'),
                'contract_amount': data.get('contract_amount'),
                'contract_start_date': data.get('contract_start_date'),
                'contract_end_date': data.get('contract_end_date'),
                'party_a_customer_name': data.get('party_a_customer_name'),
                'party_b_company_name': data.get('party_b_company_name'),
                'party_a_name': data.get('party_a_name'),
                'party_a_address': data.get('party_a_address'),
                'party_a_contact_name': data.get('party_a_contact_name'),
                'party_a_contact_phone': data.get('party_a_contact_phone'),
                'party_a_contact_email': data.get('party_a_contact_email'),
                'party_b_name': data.get('party_b_name'),
                'party_b_address': data.get('party_b_address'),
                'party_b_contact_name': data.get('party_b_contact_name'),
                'party_b_contact_phone': data.get('party_b_contact_phone'),
                'party_b_contact_email': data.get('party_b_contact_email'),
                'case_status': data.get('case_status', 'success'),
                'created_by': data.get('created_by', 'system'),
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            }

            # 执行插入
            case_id = self._insert_case(insert_data)

            if case_id:
                logger.info(f"创建案例成功: {data['case_title']} (ID: {case_id})")
                # 获取完整的案例信息返回
                case_data = self.get_case_by_id(case_id)
                return {
                    'success': True,
                    'data': case_data,
                    'message': f"案例 '{data['case_title']}' 创建成功"
                }
            else:
                return {
                    'success': False,
                    'error': '创建案例失败'
                }

        except Exception as e:
            logger.error(f"创建案例失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _insert_case(self, data: Dict) -> Optional[int]:
        """插入案例记录"""
        try:
            fields = ', '.join(data.keys())
            placeholders = ', '.join(['?' for _ in data])
            query = f"INSERT INTO case_studies ({fields}) VALUES ({placeholders})"

            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, tuple(data.values()))
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"插入案例记录失败: {e}")
            return None

    def update_case(self, case_id: int, data: Dict) -> Dict:
        """更新案例信息"""
        try:
            # 检查案例是否存在
            existing_case = self.get_case_by_id(case_id)
            if not existing_case:
                return {
                    'success': False,
                    'error': f'案例 ID {case_id} 不存在'
                }

            # 构建更新数据
            update_data = {}
            allowed_fields = [
                'company_id',  # 允许修改所属公司
                'product_id', 'product_category', 'case_title', 'case_number', 'customer_name', 'industry',
                'contract_name', 'contract_type', 'final_customer_name', 'contract_amount',
                'contract_start_date', 'contract_end_date', 'party_a_customer_name', 'party_b_company_name',
                'party_a_name', 'party_a_address', 'party_a_contact_name', 'party_a_contact_phone', 'party_a_contact_email',
                'party_b_name', 'party_b_address', 'party_b_contact_name', 'party_b_contact_phone', 'party_b_contact_email',
                'case_status'
            ]

            for field in allowed_fields:
                if field in data:
                    update_data[field] = data[field]

            if not update_data:
                return {
                    'success': False,
                    'error': '没有可更新的字段'
                }

            # 添加更新时间
            update_data['updated_at'] = datetime.now()

            # 执行更新
            result = self._update_case(case_id, update_data)

            if result:
                logger.info(f"更新案例成功: case_id={case_id}")
                return {
                    'success': True,
                    'message': '案例信息更新成功'
                }
            else:
                return {
                    'success': False,
                    'error': '更新案例失败'
                }

        except Exception as e:
            logger.error(f"更新案例失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _update_case(self, case_id: int, data: Dict) -> bool:
        """更新案例记录"""
        try:
            set_clause = ', '.join([f"{k} = ?" for k in data.keys()])
            query = f"UPDATE case_studies SET {set_clause} WHERE case_id = ?"

            values = list(data.values()) + [case_id]

            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, values)
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"更新案例记录失败: {e}")
            return False

    def get_cases(self, company_id: int = None, filters: Dict = None) -> List[Dict]:
        """
        获取案例列表

        权限规则:
        - 如果提供了company_id,返回: 该公司的案例 + 所有公开案例
        - 如果没有提供company_id,返回: 所有公开案例
        """
        try:
            conditions = []
            params = []

            # 权限筛选
            if company_id:
                # 当前公司的案例 OR 公开案例
                conditions.append("(company_id = ? OR visibility = 'public')")
                params.append(company_id)
            else:
                # 只返回公开案例
                conditions.append("visibility = 'public'")

            # 其他筛选条件
            if filters:
                if filters.get('product_id'):
                    conditions.append("product_id = ?")
                    params.append(filters['product_id'])

                if filters.get('industry'):
                    conditions.append("industry = ?")
                    params.append(filters['industry'])

                if filters.get('contract_type'):
                    conditions.append("contract_type = ?")
                    params.append(filters['contract_type'])

                if filters.get('case_status'):
                    conditions.append("case_status = ?")
                    params.append(filters['case_status'])

            where_clause = " AND ".join(conditions) if conditions else "1=1"

            query = f"""
                SELECT * FROM case_studies
                WHERE {where_clause}
                ORDER BY created_at DESC
            """

            cases = self.db.execute_query(query, tuple(params))

            # 为每个案例添加附件统计
            for case in cases:
                attachments = self.get_attachments(case['case_id'])
                case['attachment_count'] = len(attachments)

            return cases

        except Exception as e:
            logger.error(f"获取案例列表失败: {e}")
            return []

    def get_case_by_id(self, case_id: int) -> Optional[Dict]:
        """根据ID获取案例详情"""
        try:
            query = "SELECT * FROM case_studies WHERE case_id = ?"
            return self.db.execute_query(query, (case_id,), fetch_one=True)
        except Exception as e:
            logger.error(f"获取案例详情失败: {e}")
            return None

    def get_case_detail(self, case_id: int) -> Optional[Dict]:
        """获取案例详细信息（包含附件）"""
        try:
            case = self.get_case_by_id(case_id)
            if not case:
                return None

            # 获取附件列表
            attachments = self.get_attachments(case_id)
            case['attachments'] = attachments

            return case

        except Exception as e:
            logger.error(f"获取案例详情失败: {e}")
            return None

    def delete_case(self, case_id: int) -> Dict:
        """删除案例"""
        try:
            # 检查案例是否存在
            case = self.get_case_by_id(case_id)
            if not case:
                return {
                    'success': False,
                    'error': f'案例 ID {case_id} 不存在'
                }

            # 获取并删除所有附件
            attachments = self.get_attachments(case_id)
            for attachment in attachments:
                # 删除物理文件
                file_path = Path(attachment['file_path'])
                if file_path.exists():
                    file_path.unlink()
                    logger.info(f"已删除附件文件: {file_path}")

            # 删除案例记录（附件记录会通过ON DELETE CASCADE自动删除）
            query = "DELETE FROM case_studies WHERE case_id = ?"

            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (case_id,))
                conn.commit()
                row_count = cursor.rowcount

            if row_count > 0:
                logger.info(f"删除案例成功: case_id={case_id}")
                return {
                    'success': True,
                    'message': f"案例 '{case['case_title']}' 删除成功"
                }
            else:
                return {
                    'success': False,
                    'error': '删除案例失败'
                }

        except Exception as e:
            logger.error(f"删除案例失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def search_cases(self, query: str, company_id: int = None) -> List[Dict]:
        """
        搜索案例

        权限规则:
        - 如果提供了company_id,搜索: 该公司的案例 + 所有公开案例
        - 如果没有提供company_id,搜索: 所有公开案例
        """
        try:
            conditions = []
            params = []

            # 权限筛选
            if company_id:
                # 当前公司的案例 OR 公开案例
                conditions.append("(company_id = ? OR visibility = 'public')")
                params.append(company_id)
            else:
                # 只搜索公开案例
                conditions.append("visibility = 'public'")

            # 搜索条件
            search_condition = """
                (case_title LIKE ? OR
                 customer_name LIKE ? OR
                 contract_name LIKE ? OR
                 party_a_customer_name LIKE ? OR
                 party_b_company_name LIKE ?)
            """
            conditions.append(search_condition)

            search_term = f"%{query}%"
            params.extend([search_term] * 5)

            where_clause = " AND ".join(conditions)

            sql = f"""
                SELECT * FROM case_studies
                WHERE {where_clause}
                ORDER BY created_at DESC
                LIMIT 50
            """

            results = self.db.execute_query(sql, tuple(params))

            # 添加附件统计
            for case in results:
                attachments = self.get_attachments(case['case_id'])
                case['attachment_count'] = len(attachments)

            return results

        except Exception as e:
            logger.error(f"搜索案例失败: {e}")
            return []

    def get_statistics(self, company_id: int = None) -> Dict:
        """获取案例统计信息"""
        try:
            stats = {
                'total_cases': 0,
                'total_amount': 0,
                'by_status': {},
                'by_contract_type': {},
                'by_industry': {}
            }

            # 总数和总金额
            where_clause = f"WHERE company_id = {company_id}" if company_id else ""

            query = f"SELECT COUNT(*) as total, SUM(contract_amount) as total_amount FROM case_studies {where_clause}"
            result = self.db.execute_query(query, fetch_one=True)
            if result:
                stats['total_cases'] = result['total'] or 0
                stats['total_amount'] = float(result['total_amount'] or 0)

            # 按状态统计
            query = f"SELECT case_status, COUNT(*) as count FROM case_studies {where_clause} GROUP BY case_status"
            results = self.db.execute_query(query)
            stats['by_status'] = {row['case_status']: row['count'] for row in results}

            # 按合同类型统计
            query = f"SELECT contract_type, COUNT(*) as count FROM case_studies {where_clause} GROUP BY contract_type"
            results = self.db.execute_query(query)
            stats['by_contract_type'] = {row['contract_type']: row['count'] for row in results}

            # 按行业统计
            query = f"SELECT industry, COUNT(*) as count FROM case_studies {where_clause} WHERE industry IS NOT NULL GROUP BY industry"
            results = self.db.execute_query(query)
            stats['by_industry'] = {row['industry']: row['count'] for row in results}

            return stats

        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return {}

    # =========================
    # 附件管理相关方法
    # =========================

    def upload_attachment(self, case_id: int, file_obj, original_filename: str,
                         attachment_type: str = 'contract_order', description: str = None) -> Dict:
        """
        上传案例附件（支持PDF和Word自动转换为图片）

        转换规则：
        - PDF文件：自动转换每一页为图片
        - Word文档：自动提取文档中的所有图片
        - 图片文件：直接使用，无需转换
        """
        try:
            from core.storage_service import storage_service

            # 检查案例是否存在
            case = self.get_case_by_id(case_id)
            if not case:
                return {
                    'success': False,
                    'error': f'案例 ID {case_id} 不存在'
                }

            # 使用统一存储服务保存文件
            file_metadata = storage_service.store_file(
                file_obj=file_obj,
                original_name=original_filename,
                category='case_attachments',
                business_type=attachment_type,
                company_id=case['company_id'],
                tags=[f'case_{case_id}', attachment_type]
            )

            # 创建附件记录（基础信息）
            file_ext = Path(original_filename).suffix.lower()
            original_file_type = file_ext[1:].upper() if file_ext else ''

            attachment_data = {
                'case_id': case_id,
                'file_name': file_metadata.safe_name,
                'original_filename': file_metadata.original_name,
                'file_path': file_metadata.file_path,
                'file_type': file_ext[1:] if file_ext else '',
                'file_size': file_metadata.file_size,
                'attachment_type': attachment_type,
                'attachment_description': description,
                'original_file_type': original_file_type,  # 新增：记录原始文件类型
                'uploaded_by': 'system',
                'uploaded_at': datetime.now()
            }

            # 🆕 步骤：如果是PDF或Word，自动转换/提取图片
            converted_images = None
            conversion_info = None

            if file_ext in ['.pdf', '.docx', '.doc']:
                try:
                    from common.document_image_extractor import extract_images_from_document

                    logger.info(f"检测到文档类型 {original_file_type}，开始自动转换/提取图片...")

                    result = extract_images_from_document(
                        file_path=file_metadata.file_path,
                        base_name=f"case_{case_id}_{file_metadata.safe_name}",
                        dpi=200
                    )

                    if result['success']:
                        converted_images = result['images']
                        conversion_info = result['conversion_info']

                        # 保存到附件记录
                        attachment_data['converted_images'] = json.dumps(converted_images, ensure_ascii=False)
                        attachment_data['conversion_info'] = json.dumps(conversion_info, ensure_ascii=False)
                        attachment_data['conversion_date'] = datetime.now()

                        logger.info(f"✅ 文档转换成功: 提取/转换了 {len(converted_images)} 张图片")
                    else:
                        logger.warning(f"⚠️  文档转换失败: {result.get('error', '未知错误')}，将只保存原文件")

                except Exception as e:
                    logger.warning(f"⚠️  文档转换异常: {e}，将只保存原文件")

            # 插入附件记录
            attachment_id = self._insert_attachment(attachment_data)

            if attachment_id:
                logger.info(f"案例附件上传成功: {original_filename} (ID: {attachment_id})")

                # 构建返回结果
                result = {
                    'success': True,
                    'attachment_id': attachment_id,
                    'file_name': file_metadata.safe_name,
                    'message': f"附件 '{original_filename}' 上传成功"
                }

                # 如果有转换结果，添加到返回信息中
                if converted_images:
                    result['converted_images'] = converted_images
                    result['conversion_info'] = conversion_info
                    result['message'] += f"，已自动提取/转换 {len(converted_images)} 张图片"

                return result
            else:
                return {
                    'success': False,
                    'error': '附件记录创建失败'
                }

        except Exception as e:
            logger.error(f"上传附件失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _insert_attachment(self, data: Dict) -> Optional[int]:
        """插入附件记录"""
        try:
            fields = ', '.join(data.keys())
            placeholders = ', '.join(['?' for _ in data])
            query = f"INSERT INTO case_attachments ({fields}) VALUES ({placeholders})"

            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, tuple(data.values()))
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"插入附件记录失败: {e}")
            return None

    def get_attachments(self, case_id: int) -> List[Dict]:
        """获取案例的附件列表"""
        try:
            query = """
                SELECT * FROM case_attachments
                WHERE case_id = ?
                ORDER BY uploaded_at DESC
            """
            attachments = self.db.execute_query(query, (case_id,))

            # 检查文件是否存在
            for attachment in attachments:
                file_path = Path(attachment['file_path'])
                attachment['file_exists'] = file_path.exists()
                attachment['file_size_mb'] = round(attachment['file_size'] / (1024 * 1024), 2) if attachment['file_size'] else 0

            return attachments

        except Exception as e:
            logger.error(f"获取附件列表失败: {e}")
            return []

    def delete_attachment(self, attachment_id: int) -> Dict:
        """删除附件"""
        try:
            # 获取附件信息
            query = "SELECT * FROM case_attachments WHERE attachment_id = ?"
            attachment = self.db.execute_query(query, (attachment_id,), fetch_one=True)

            if not attachment:
                return {
                    'success': False,
                    'error': f'附件 ID {attachment_id} 不存在'
                }

            # 删除物理文件
            file_path = Path(attachment['file_path'])
            if file_path.exists():
                file_path.unlink()
                logger.info(f"已删除附件文件: {file_path}")

            # 删除数据库记录
            delete_query = "DELETE FROM case_attachments WHERE attachment_id = ?"

            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(delete_query, (attachment_id,))
                conn.commit()
                row_count = cursor.rowcount

            if row_count > 0:
                logger.info(f"删除附件成功: attachment_id={attachment_id}")
                return {
                    'success': True,
                    'message': f"附件 '{attachment['original_filename']}' 删除成功"
                }
            else:
                return {
                    'success': False,
                    'error': '删除附件失败'
                }

        except Exception as e:
            logger.error(f"删除附件失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
