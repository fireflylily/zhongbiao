#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识库管理器
功能：企业信息、产品、文档的业务逻辑处理
"""

import os
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from common.database import get_knowledge_base_db
from common.logger import get_module_logger
from common.config import get_config

logger = get_module_logger("knowledge_base.manager")


class KnowledgeBaseManager:
    """知识库管理器"""

    def __init__(self):
        self.db = get_knowledge_base_db()
        self.config = get_config()

        # 获取上传目录
        self.upload_dir = self.config.get_path('uploads')
        self.upload_dir.mkdir(exist_ok=True)

        logger.info("知识库管理器初始化完成")

    # =========================
    # 公司管理相关方法
    # =========================

    def create_company(self, company_name: str, company_code: str = None,
                      industry_type: str = None, description: str = None) -> Dict:
        """创建公司"""
        try:
            # 检查公司名称是否已存在
            existing_companies = self.db.get_companies()
            for company in existing_companies:
                if company['company_name'] == company_name:
                    raise ValueError(f"公司名称 '{company_name}' 已存在")
                if company_code and company['company_code'] == company_code:
                    raise ValueError(f"公司代码 '{company_code}' 已存在")

            company_id = self.db.create_company(
                company_name=company_name,
                company_code=company_code,
                industry_type=industry_type,
                description=description
            )

            # 自动创建默认的企业信息库分类
            default_profiles = [
                {'type': 'basic', 'name': '基础信息', 'desc': '公司基本信息和对外资料', 'privacy': 1},
                {'type': 'qualification', 'name': '资质证书', 'desc': '各类业务资质和认证证书', 'privacy': 2},
                {'type': 'personnel', 'name': '人员信息', 'desc': '员工信息和人力资源资料', 'privacy': 3},
                {'type': 'financial', 'name': '财务文档', 'desc': '财务报告和审计资料', 'privacy': 4}
            ]

            for profile in default_profiles:
                self.db.create_company_profile(
                    company_id=company_id,
                    profile_type=profile['type'],
                    profile_name=profile['name'],
                    description=profile['desc'],
                    privacy_level=profile['privacy']
                )

            logger.info(f"创建公司成功: {company_name} (ID: {company_id})")

            return {
                'success': True,
                'company_id': company_id,
                'message': f"公司 '{company_name}' 创建成功"
            }

        except Exception as e:
            logger.error(f"创建公司失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def update_company(self, company_id: int, data: Dict) -> Dict:
        """更新公司信息"""
        try:
            # DEBUG: 记录接收到的原始数据
            logger.info(f"[DEBUG] 更新公司 {company_id} - 接收到的原始数据: {data}")

            # 检查公司是否存在
            existing_company = self.db.get_company_by_id(company_id)
            if not existing_company:
                return {
                    'success': False,
                    'error': f'公司 ID {company_id} 不存在'
                }

            # 映射前端字段到数据库字段
            update_data = {}
            field_mapping = {
                'companyName': 'company_name',
                'establishDate': 'establish_date',
                'legalRepresentative': 'legal_representative',
                'legalRepresentativePosition': 'legal_representative_position',
                'socialCreditCode': 'social_credit_code',
                'registeredCapital': 'registered_capital',
                'companyType': 'company_type',
                'registeredAddress': 'registered_address',
                'businessScope': 'business_scope',
                'companyDescription': 'description',
                'fixedPhone': 'fixed_phone',
                'fax': 'fax',
                'postalCode': 'postal_code',
                'email': 'email',
                'officeAddress': 'office_address',
                'employeeCount': 'employee_count',
                'bankName': 'bank_name',
                'bankAccount': 'bank_account'
            }

            # DEBUG: 专门检查 registeredCapital 字段
            if 'registeredCapital' in data:
                logger.info(f"[DEBUG] registeredCapital 字段存在于输入数据中: {data['registeredCapital']!r}")
            else:
                logger.info(f"[DEBUG] registeredCapital 字段不存在于输入数据中")

            # 转换字段名并过滤None值，保留空字符串
            for frontend_key, db_key in field_mapping.items():
                if frontend_key in data and data[frontend_key] is not None:
                    update_data[db_key] = data[frontend_key]
                    # DEBUG: 专门追踪 registeredCapital 的映射过程
                    if frontend_key == 'registeredCapital':
                        logger.info(f"[DEBUG] registeredCapital 映射成功: {frontend_key} -> {db_key} = {data[frontend_key]!r}")
                elif frontend_key == 'registeredCapital':
                    if frontend_key not in data:
                        logger.info(f"[DEBUG] registeredCapital 不在输入数据中")
                    elif data[frontend_key] is None:
                        logger.info(f"[DEBUG] registeredCapital 值为 None，被过滤掉")

            # DEBUG: 记录最终的更新数据
            logger.info(f"[DEBUG] 字段映射完成，最终更新数据: {update_data}")
            if 'registered_capital' in update_data:
                logger.info(f"[DEBUG] registered_capital 包含在最终更新数据中: {update_data['registered_capital']!r}")
            else:
                logger.info(f"[DEBUG] registered_capital 不在最终更新数据中")

            if not update_data:
                return {
                    'success': False,
                    'error': '没有可更新的字段'
                }

            # 更新时间戳
            update_data['updated_at'] = datetime.now()

            # DEBUG: 记录发送给数据库的最终数据
            logger.info(f"[DEBUG] 发送给数据库的数据(包含时间戳): {update_data}")

            # 调用数据库更新方法
            result = self.db.update_company(company_id, update_data)

            if result:
                logger.info(f"更新公司信息成功: company_id={company_id}")
                return {
                    'success': True,
                    'message': '公司信息更新成功'
                }
            else:
                return {
                    'success': False,
                    'error': '更新公司信息失败'
                }

        except Exception as e:
            logger.error(f"更新公司信息失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_companies(self) -> List[Dict]:
        """获取公司列表"""
        try:
            companies = self.db.get_companies()

            # 为每个公司添加统计信息
            for company in companies:
                company_id = company['company_id']

                # 获取产品数量
                products = self.db.get_products(company_id)
                company['product_count'] = len(products)

                # 获取文档统计
                stats = self.db.get_knowledge_base_stats(company_id)
                company['document_count'] = stats.get('total_documents', 0)
                company['stats'] = stats

            return companies

        except Exception as e:
            logger.error(f"获取公司列表失败: {e}")
            return []

    def get_company_detail(self, company_id: int) -> Optional[Dict]:
        """获取公司详细信息"""
        try:
            company = self.db.get_company_by_id(company_id)
            if not company:
                return None

            # 获取企业信息库分类
            profiles = self.db.get_company_profiles(company_id)
            company['profiles'] = profiles

            # 获取产品列表
            products = self.db.get_products(company_id)
            company['products'] = products

            # 获取统计信息
            stats = self.db.get_knowledge_base_stats(company_id)
            company['stats'] = stats

            return company

        except Exception as e:
            logger.error(f"获取公司详情失败: {e}")
            return None

    def delete_company(self, company_id: int) -> Dict:
        """删除公司"""
        try:
            # 检查公司是否存在
            existing_company = self.db.get_company_by_id(company_id)
            if not existing_company:
                return {
                    'success': False,
                    'error': f'公司 ID {company_id} 不存在'
                }

            # 获取公司相关的产品
            products = self.db.get_products(company_id)

            # 删除所有产品相关的文档和文档库
            for product in products:
                product_id = product['product_id']

                # 获取产品的文档库
                libraries = self.db.get_document_libraries('product', product_id)
                for library in libraries:
                    library_id = library['library_id']

                    # 获取文档库中的所有文档
                    documents = self.db.get_documents(library_id)
                    for document in documents:
                        # 删除物理文件
                        file_path = Path(document['file_path'])
                        if file_path.exists():
                            file_path.unlink()

                        # 删除文档记录
                        self.db.delete_document(document['doc_id'])

                    # 删除文档库
                    self.db.delete_document_library(library_id)

                # 删除产品
                self.db.delete_product(product_id)

            # 获取公司信息库分类
            profiles = self.db.get_company_profiles(company_id)
            for profile in profiles:
                # 删除企业信息库分类
                self.db.delete_company_profile(profile['profile_id'])

            # 删除公司记录
            result = self.db.delete_company(company_id)

            if result:
                logger.info(f"删除公司成功: company_id={company_id}")
                return {
                    'success': True,
                    'message': '公司删除成功'
                }
            else:
                return {
                    'success': False,
                    'error': '删除公司失败'
                }

        except Exception as e:
            logger.error(f"删除公司失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    # =========================
    # 产品管理相关方法
    # =========================

    def create_product(self, company_id: int, product_name: str,
                      product_code: str = None, product_category: str = None,
                      description: str = None) -> Dict:
        """创建产品"""
        try:
            # 检查公司是否存在
            company = self.db.get_company_by_id(company_id)
            if not company:
                raise ValueError(f"公司ID {company_id} 不存在")

            # 检查产品代码是否重复
            if product_code:
                existing_products = self.db.get_products(company_id)
                for product in existing_products:
                    if product['product_code'] == product_code:
                        raise ValueError(f"产品代码 '{product_code}' 在该公司下已存在")

            product_id = self.db.create_product(
                company_id=company_id,
                product_name=product_name,
                product_code=product_code,
                product_category=product_category,
                description=description
            )

            # 自动创建默认的文档库分类
            default_libraries = [
                {'type': 'tech', 'name': '技术文档库'},
                {'type': 'impl', 'name': '实施文档库'},
                {'type': 'service', 'name': '售后服务文档库'}
            ]

            for lib in default_libraries:
                self.db.create_document_library(
                    owner_type='product',
                    owner_id=product_id,
                    library_name=lib['name'],
                    library_type=lib['type'],
                    privacy_level=1
                )

            logger.info(f"创建产品成功: {product_name} (ID: {product_id})")

            return {
                'success': True,
                'product_id': product_id,
                'message': f"产品 '{product_name}' 创建成功"
            }

        except Exception as e:
            logger.error(f"创建产品失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_products(self, company_id: int) -> List[Dict]:
        """获取公司的产品列表"""
        try:
            products = self.db.get_products(company_id)

            # 为每个产品添加文档库信息
            for product in products:
                product_id = product['product_id']
                libraries = self.db.get_document_libraries('product', product_id)
                product['libraries'] = libraries

                # 统计文档数量
                total_docs = 0
                for library in libraries:
                    docs = self.db.get_documents(library['library_id'])
                    total_docs += len(docs)
                product['document_count'] = total_docs

            return products

        except Exception as e:
            logger.error(f"获取产品列表失败: {e}")
            return []

    def get_product_detail(self, product_id: int) -> Optional[Dict]:
        """获取产品详细信息"""
        try:
            product = self.db.get_product_by_id(product_id)
            if not product:
                return None

            # 获取文档库列表
            libraries = self.db.get_document_libraries('product', product_id)

            # 为每个文档库添加文档列表
            for library in libraries:
                library_id = library['library_id']
                documents = self.db.get_documents(library_id)
                library['documents'] = documents

            product['libraries'] = libraries

            return product

        except Exception as e:
            logger.error(f"获取产品详情失败: {e}")
            return None

    # =========================
    # 文档库管理相关方法
    # =========================

    def create_document_library(self, owner_type: str, owner_id: int,
                               library_name: str, library_type: str,
                               privacy_level: int = 1, is_shared: bool = False,
                               share_scope: str = None, share_products: List[int] = None) -> Dict:
        """创建文档库"""
        try:
            library_id = self.db.create_document_library(
                owner_type=owner_type,
                owner_id=owner_id,
                library_name=library_name,
                library_type=library_type,
                privacy_level=privacy_level,
                is_shared=is_shared,
                share_scope=share_scope,
                share_products=share_products
            )

            logger.info(f"创建文档库成功: {library_name} (ID: {library_id})")

            return {
                'success': True,
                'library_id': library_id,
                'message': f"文档库 '{library_name}' 创建成功"
            }

        except Exception as e:
            logger.error(f"创建文档库失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_library_by_id(self, library_id: int) -> Optional[Dict]:
        """根据ID获取文档库详情"""
        try:
            return self.db.get_library(library_id)
        except Exception as e:
            logger.error(f"获取文档库详情失败: {e}")
            return None

    def get_document_libraries(self, owner_type: str, owner_id: int) -> List[Dict]:
        """获取文档库列表"""
        try:
            libraries = self.db.get_document_libraries(owner_type, owner_id)

            # 为每个文档库添加文档统计
            for library in libraries:
                library_id = library['library_id']
                documents = self.db.get_documents(library_id)
                library['document_count'] = len(documents)

                # 统计文档状态
                status_counts = {'uploaded': 0, 'parsing': 0, 'completed': 0, 'failed': 0}
                for doc in documents:
                    parse_status = doc.get('parse_status', 'pending')
                    if parse_status in status_counts:
                        status_counts[parse_status] += 1
                library['status_counts'] = status_counts

            return libraries

        except Exception as e:
            logger.error(f"获取文档库列表失败: {e}")
            return []

    # =========================
    # 文档管理相关方法
    # =========================

    def upload_document(self, library_id: int, file_obj, original_filename: str,
                       privacy_classification: int = 1,
                       tags: List[str] = None, metadata: Dict = None) -> Dict:
        """
        上传文档到文档库 - 使用统一文件存储服务
        """
        try:
            from core.storage_service import storage_service

            # 获取文档库信息以确定所属公司
            library = self.db.get_library(library_id)
            company_id = None
            product_id = None
            if library and library.get('owner_type') == 'product':
                # 如果是产品库，获取产品所属的公司ID
                product_id = library.get('owner_id')
                if product_id:
                    product = self.db.get_product(product_id)
                    if product:
                        company_id = product.get('company_id')

            # 使用统一存储服务保存文件
            file_metadata = storage_service.store_file(
                file_obj=file_obj,
                original_name=original_filename,
                category='product_docs',
                business_type='knowledge_base',
                company_id=company_id,
                tags=tags
            )

            # 创建文档记录（使用file_id关联）
            file_ext = Path(original_filename).suffix.lower()
            doc_id = self.db.create_document(
                library_id=library_id,
                filename=file_metadata.safe_name,  # 物理文件名
                original_filename=file_metadata.original_name,  # 原始文件名
                file_path=file_metadata.file_path,
                file_type=file_ext[1:],  # 去掉点号
                file_size=file_metadata.file_size,
                privacy_classification=privacy_classification,
                tags=tags,
                metadata={'file_id': file_metadata.file_id, 'checksum': file_metadata.checksum}
            )

            logger.info(f"文档上传成功: {original_filename} -> {file_metadata.safe_name} (ID: {doc_id}, file_id: {file_metadata.file_id})")

            return {
                'success': True,
                'doc_id': doc_id,
                'filename': file_metadata.safe_name,
                'original_filename': file_metadata.original_name,
                'file_id': file_metadata.file_id,
                'file_path': file_metadata.file_path,  # 向量化需要
                'file_type': file_ext[1:],  # 向量化需要
                'library_id': library_id,  # 向量化需要
                'company_id': company_id,  # 向量化需要
                'product_id': product_id,  # 向量化需要
                'message': f"文档 '{original_filename}' 上传成功"
            }

        except Exception as e:
            logger.error(f"文档上传失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_document_by_id(self, doc_id: int) -> Optional[Dict]:
        """根据ID获取文档详细信息"""
        try:
            query = """
            SELECT * FROM documents
            WHERE doc_id = ?
            """
            return self.db.execute_query(query, (doc_id,), fetch_one=True)
        except Exception as e:
            logger.error(f"获取文档详情失败: {e}")
            return None

    def get_documents(self, library_id: int = None, privacy_level: int = None) -> List[Dict]:
        """获取文档列表"""
        try:
            documents = self.db.get_documents(library_id, privacy_level)

            # 添加文件状态信息
            for doc in documents:
                file_path = Path(doc['file_path'])
                doc['file_exists'] = file_path.exists()
                doc['file_size_mb'] = round(doc['file_size'] / (1024 * 1024), 2) if doc['file_size'] else 0

                # 解析JSON字段
                if doc.get('tags'):
                    try:
                        doc['tags'] = json.loads(doc['tags'])
                    except (json.JSONDecodeError, TypeError):
                        doc['tags'] = []

                if doc.get('metadata'):
                    try:
                        doc['metadata'] = json.loads(doc['metadata'])
                    except (json.JSONDecodeError, TypeError):
                        doc['metadata'] = {}

            return documents

        except Exception as e:
            logger.error(f"获取文档列表失败: {e}")
            return []

    def update_document_status(self, doc_id: int, parse_status: str = None,
                              vector_status: str = None) -> bool:
        """更新文档处理状态"""
        try:
            result = self.db.update_document_status(doc_id, parse_status, vector_status)
            if result:
                logger.info(f"文档状态更新成功: doc_id={doc_id}, parse_status={parse_status}, vector_status={vector_status}")
            return result

        except Exception as e:
            logger.error(f"更新文档状态失败: {e}")
            return False

    def delete_document(self, doc_id: int) -> Dict:
        """删除文档"""
        try:
            # 先获取文档信息
            documents = self.db.get_documents()
            document = None
            for doc in documents:
                if doc['doc_id'] == doc_id:
                    document = doc
                    break

            if not document:
                return {
                    'success': False,
                    'error': f'文档 ID {doc_id} 不存在'
                }

            # 1. 删除向量数据（如果已建立索引）
            deleted_vector_count = 0
            try:
                from .rag_engine import get_rag_engine, LANGCHAIN_AVAILABLE
                if LANGCHAIN_AVAILABLE and document.get('vector_status') == 'completed':
                    engine = get_rag_engine()

                    # 尝试方式1: 通过document_id删除（RAG API格式）
                    delete_result = engine.delete_by_metadata({'document_id': doc_id})
                    deleted_vector_count = delete_result.get('deleted_count', 0)

                    # 尝试方式2: 如果方式1没有删除，通过source路径删除（Langchain格式）
                    if deleted_vector_count == 0:
                        file_path_str = str(document['file_path'])
                        delete_result2 = engine.delete_by_metadata({'source': file_path_str})
                        deleted_vector_count += delete_result2.get('deleted_count', 0)

                    # 尝试方式3: 如果前两种都失败，使用SQL直接删除（Vector Search API格式）
                    if deleted_vector_count == 0:
                        try:
                            import sqlite3
                            chroma_db = Path(__file__).parent.parent / 'data' / 'chroma_db' / 'chroma.sqlite3'
                            if chroma_db.exists():
                                conn = sqlite3.connect(str(chroma_db))
                                cursor = conn.cursor()
                                # 查找该document_id的所有向量ID
                                cursor.execute("""
                                    SELECT DISTINCT e.id FROM embeddings e
                                    JOIN embedding_metadata m ON e.id = m.id
                                    WHERE m.key = 'document_id' AND m.int_value = ?
                                """, (doc_id,))
                                vector_ids = [row[0] for row in cursor.fetchall()]

                                if vector_ids:
                                    # 删除向量及其元数据
                                    placeholders = ','.join(['?' for _ in vector_ids])
                                    cursor.execute(f"DELETE FROM embeddings WHERE id IN ({placeholders})", vector_ids)
                                    cursor.execute(f"DELETE FROM embedding_metadata WHERE id IN ({placeholders})", vector_ids)
                                    conn.commit()
                                    deleted_vector_count = len(vector_ids)
                                    logger.info(f"通过SQL直接删除了 {deleted_vector_count} 个向量（Vector Search格式）")
                                conn.close()
                        except Exception as ve:
                            logger.warning(f"SQL直接删除向量失败: {ve}")

                    if deleted_vector_count > 0:
                        logger.info(f"已删除文档 {doc_id} 的向量数据，删除数量: {deleted_vector_count}")
                    else:
                        logger.warning(f"未找到文档 {doc_id} 的向量数据")

            except Exception as e:
                logger.warning(f"删除向量数据时出错: {e}")

            # 2. 删除物理文件
            file_path = Path(document['file_path'])
            if file_path.exists():
                file_path.unlink()
                logger.info(f"已删除物理文件: {file_path}")

            # 3. 删除数据库记录
            result = self.db.delete_document(doc_id)
            if result:
                logger.info(f"文档删除成功: doc_id={doc_id}, filename={document['original_filename']}")
                return {
                    'success': True,
                    'message': f"文档 '{document['original_filename']}' 删除成功"
                }
            else:
                return {
                    'success': False,
                    'error': '删除数据库记录失败'
                }

        except Exception as e:
            logger.error(f"删除文档失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    # =========================
    # 隐私和权限管理方法
    # =========================

    def check_document_access(self, user_role: str, doc_privacy_level: int) -> bool:
        """检查文档访问权限"""
        # 权限级别定义：
        # 1: 公开 - 所有用户可访问
        # 2: 内部 - 内部用户可访问
        # 3: 机密 - 管理员及以上可访问
        # 4: 绝密 - 超级管理员可访问

        role_levels = {
            'guest': 1,
            'user': 2,
            'admin': 3,
            'super_admin': 4
        }

        user_level = role_levels.get(user_role, 0)
        return user_level >= doc_privacy_level

    def log_document_access(self, user_id: str, user_role: str, action_type: str,
                           doc_id: int, privacy_level: int = None, access_granted: bool = True,
                           access_reason: str = None, ip_address: str = None,
                           user_agent: str = None, session_id: str = None) -> int:
        """记录文档访问日志"""
        try:
            log_id = self.db.create_audit_log(
                user_id=user_id,
                user_role=user_role,
                action_type=action_type,
                resource_type='document',
                resource_id=doc_id,
                privacy_level=privacy_level,
                access_granted=access_granted,
                access_reason=access_reason,
                ip_address=ip_address,
                user_agent=user_agent,
                session_id=session_id
            )

            return log_id

        except Exception as e:
            logger.error(f"记录访问日志失败: {e}")
            return 0

    # =========================
    # 统计和分析方法
    # =========================

    def get_dashboard_stats(self, company_id: int = None) -> Dict:
        """获取仪表板统计信息"""
        try:
            stats = {}

            if company_id:
                # 单个公司的统计
                stats = self.db.get_knowledge_base_stats(company_id)
                company = self.db.get_company_by_id(company_id)
                stats['company_name'] = company['company_name'] if company else '未知公司'
            else:
                # 全系统统计
                companies = self.db.get_companies()
                stats['total_companies'] = len(companies)

                total_docs = 0
                total_products = 0

                for company in companies:
                    company_id = company['company_id']
                    products = self.db.get_products(company_id)
                    total_products += len(products)

                    company_stats = self.db.get_knowledge_base_stats(company_id)
                    total_docs += company_stats.get('total_documents', 0)

                stats['total_products'] = total_products
                stats['total_documents'] = total_docs

            return stats

        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return {}

    def get_knowledge_base_statistics(self) -> Dict:
        """获取知识库整体统计数据"""
        try:
            stats = {}

            # 获取企业总数
            companies = self.db.get_companies()
            stats['totalCompanies'] = len(companies)

            # 获取产品总数
            total_products = 0
            total_documents = 0
            confidential_docs = 0

            for company in companies:
                products = self.db.get_products(company['company_id'])
                total_products += len(products)

                # 统计文档数量
                for product in products:
                    libraries = self.db.get_document_libraries('product', product['product_id'])
                    for library in libraries:
                        documents = self.db.get_documents(library['library_id'])
                        total_documents += len(documents)

                        # 统计机密文档数量
                        for doc in documents:
                            if doc.get('privacy_classification', 1) >= 3:  # 机密及以上
                                confidential_docs += 1

            stats['totalProducts'] = total_products
            stats['totalDocuments'] = total_documents
            stats['confidentialDocs'] = confidential_docs

            # 按分类统计
            stats['byCategory'] = self._get_documents_by_category()
            stats['byPrivacyLevel'] = self._get_documents_by_privacy_level()

            return stats

        except Exception as e:
            logger.error(f"获取统计数据失败: {e}")
            return {
                'totalCompanies': 0,
                'totalProducts': 0,
                'totalDocuments': 0,
                'confidentialDocs': 0,
                'byCategory': {},
                'byPrivacyLevel': {}
            }

    def _get_documents_by_category(self) -> Dict:
        """按文档分类统计（通过library_type）"""
        try:
            query = """
            SELECT dl.library_type, COUNT(*) as count
            FROM documents d
            JOIN document_libraries dl ON d.library_id = dl.library_id
            GROUP BY dl.library_type
            """
            results = self.db.execute_query(query)
            return {item['library_type']: item['count'] for item in results}
        except Exception as e:
            self.logger.error(f"统计案例库类型失败: {e}")
            return {}

    def _get_documents_by_privacy_level(self) -> Dict:
        """按隐私级别统计"""
        try:
            query = """
            SELECT privacy_classification, COUNT(*) as count
            FROM documents
            GROUP BY privacy_classification
            """
            results = self.db.execute_query(query)
            return {str(item['privacy_classification']): item['count'] for item in results}
        except Exception as e:
            self.logger.error(f"统计隐私级别失败: {e}")
            return {}

    def search_documents(self, query: str, category: str = None, privacy_level: int = 1) -> List[Dict]:
        """搜索文档（基础版本，后续可增强为向量搜索）"""
        try:
            conditions = ["d.privacy_classification <= ?"]
            params = [privacy_level]

            # 添加分类过滤（通过library_type）
            if category:
                conditions.append("dl.library_type = ?")
                params.append(category)

            # 简单的文本搜索（在文件名中搜索）
            conditions.append("(d.original_filename LIKE ? OR d.tags LIKE ?)")
            search_term = f"%{query}%"
            params.extend([search_term, search_term])

            where_clause = " AND ".join(conditions)

            search_query = f"""
            SELECT d.*, dl.library_name, p.product_name
            FROM documents d
            JOIN document_libraries dl ON d.library_id = dl.library_id
            LEFT JOIN products p ON dl.owner_id = p.product_id AND dl.owner_type = 'product'
            WHERE {where_clause}
            ORDER BY d.upload_time DESC
            LIMIT 20
            """

            results = self.db.execute_query(search_query, tuple(params))

            # 为结果添加相关度评分（简单版本）
            for result in results:
                # 简单的相关度计算
                filename_score = 0.7 if query.lower() in result['original_filename'].lower() else 0.3
                result['relevance_score'] = filename_score
                result['category'] = result.get('library_type', 'tech')
                result['filename'] = result['original_filename']

            return results

        except Exception as e:
            logger.error(f"搜索文档失败: {e}")
            return []

    # =========================
    # 公司资质文件管理方法
    # =========================

    def upload_qualification(self, company_id: int, qualification_key: str,
                            file_obj, original_filename: str,
                            qualification_name: str = None, custom_name: str = None,
                            issue_date: str = None, expire_date: str = None) -> Dict:
        """上传公司资质文件 - 使用统一存储服务"""
        try:
            from core.storage_service import storage_service

            # 检查公司是否存在
            company = self.db.get_company_by_id(company_id)
            if not company:
                return {
                    'success': False,
                    'error': f'公司ID {company_id} 不存在'
                }

            # 使用统一存储服务保存文件
            file_metadata = storage_service.store_file(
                file_obj=file_obj,
                original_name=original_filename,
                category='qualifications',
                business_type=qualification_key,
                company_id=company_id,
                tags=[qualification_name or qualification_key, f'company_{company_id}']
            )

            # 获取文件类型
            file_ext = Path(original_filename).suffix.lower()
            file_type = file_ext[1:] if file_ext else ''

            # 创建或更新资质记录
            qualification_id = self.db.save_company_qualification(
                company_id=company_id,
                qualification_key=qualification_key,
                qualification_name=qualification_name or qualification_key,
                custom_name=custom_name,
                original_filename=file_metadata.original_name,
                safe_filename=file_metadata.safe_name,
                file_path=file_metadata.file_path,
                file_size=file_metadata.file_size,
                file_type=file_type,
                issue_date=issue_date,
                expire_date=expire_date
            )

            logger.info(f"公司 {company_id} 上传资质文件成功: {qualification_key} -> {file_metadata.safe_name} (file_id: {file_metadata.file_id})")

            return {
                'success': True,
                'qualification_id': qualification_id,
                'qualification_key': qualification_key,
                'filename': file_metadata.safe_name,
                'original_filename': file_metadata.original_name,
                'file_id': file_metadata.file_id,
                'message': f"资质文件 '{original_filename}' 上传成功"
            }

        except Exception as e:
            logger.error(f"上传资质文件失败: {e}")
            # 如果文件已保存但数据库操作失败，删除文件
            if 'file_path' in locals() and file_path.exists():
                file_path.unlink()
            return {
                'success': False,
                'error': str(e)
            }

    def get_company_qualifications(self, company_id: int) -> List[Dict]:
        """获取公司的所有资质文件"""
        try:
            qualifications = self.db.get_company_qualifications(company_id)

            # 检查文件是否存在
            for qual in qualifications:
                file_path = Path(qual['file_path'])
                qual['file_exists'] = file_path.exists()
                qual['file_size_kb'] = round(qual['file_size'] / 1024, 2) if qual['file_size'] else 0

                # 检查是否过期
                if qual.get('expire_date'):
                    expire_date = datetime.strptime(qual['expire_date'], '%Y-%m-%d').date()
                    qual['is_expired'] = expire_date < datetime.now().date()
                else:
                    qual['is_expired'] = False

            return qualifications

        except Exception as e:
            logger.error(f"获取公司资质文件失败: {e}")
            return []

    def delete_qualification(self, qualification_id: int) -> Dict:
        """删除资质文件"""
        try:
            # 获取资质信息
            qualification = self.db.get_qualification_by_id(qualification_id)
            if not qualification:
                return {
                    'success': False,
                    'error': f'资质文件 ID {qualification_id} 不存在'
                }

            # 删除物理文件
            file_path = Path(qualification['file_path'])
            if file_path.exists():
                file_path.unlink()
                logger.info(f"已删除资质文件: {file_path}")

            # 删除数据库记录
            result = self.db.delete_qualification(qualification_id)
            if result:
                logger.info(f"资质文件删除成功: qualification_id={qualification_id}")
                return {
                    'success': True,
                    'message': f"资质文件 '{qualification['original_filename']}' 删除成功"
                }
            else:
                return {
                    'success': False,
                    'error': '删除数据库记录失败'
                }

        except Exception as e:
            logger.error(f"删除资质文件失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def delete_qualification_by_key(self, company_id: int, qualification_key: str) -> Dict:
        """根据公司ID和资质key删除资质文件"""
        try:
            # 获取资质信息
            qualification = self.db.get_qualification_by_key(company_id, qualification_key)
            if not qualification:
                return {
                    'success': False,
                    'error': f'公司 {company_id} 的资质文件 {qualification_key} 不存在'
                }

            # 删除物理文件
            file_path = Path(qualification['file_path'])
            if file_path.exists():
                file_path.unlink()
                logger.info(f"已删除资质文件: {file_path}")

            # 删除数据库记录
            result = self.db.delete_qualification(qualification['qualification_id'])
            if result:
                logger.info(f"资质文件删除成功: company_id={company_id}, key={qualification_key}")
                return {
                    'success': True,
                    'message': f"资质文件 '{qualification['original_filename']}' 删除成功"
                }
            else:
                return {
                    'success': False,
                    'error': '删除数据库记录失败'
                }

        except Exception as e:
            logger.error(f"删除资质文件失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def verify_qualification(self, qualification_id: int, verify_status: str,
                           verify_by: str = None, verify_note: str = None) -> bool:
        """验证资质文件状态"""
        try:
            result = self.db.update_qualification_status(
                qualification_id=qualification_id,
                verify_status=verify_status,
                verify_by=verify_by,
                verify_note=verify_note
            )
            if result:
                logger.info(f"资质验证状态更新成功: qualification_id={qualification_id}, status={verify_status}")
            return result

        except Exception as e:
            logger.error(f"更新资质验证状态失败: {e}")
            return False

    def get_expired_qualifications(self, days_ahead: int = 30) -> List[Dict]:
        """获取即将过期的资质文件"""
        try:
            future_date = (datetime.now() + timedelta(days=days_ahead)).strftime('%Y-%m-%d')
            qualifications = self.db.get_expiring_qualifications(future_date)
            return qualifications

        except Exception as e:
            logger.error(f"获取过期资质文件失败: {e}")
            return []

    def get_qualification_types(self, include_inactive: bool = False) -> List[Dict]:
        """获取资质类型定义"""
        try:
            # 构建查询条件
            if include_inactive:
                query = """
                    SELECT type_key, type_name, category, is_required, description,
                           sort_order, is_active, created_at
                    FROM qualification_types
                    ORDER BY sort_order, type_name
                """
            else:
                query = """
                    SELECT type_key, type_name, category, is_required, description,
                           sort_order, is_active, created_at
                    FROM qualification_types
                    WHERE is_active = TRUE
                    ORDER BY sort_order, type_name
                """

            # 使用 execute_query 方法
            rows = self.db.execute_query(query)

            # 转换为字典格式
            qualifications = []
            if rows:
                for row in rows:
                    # row 已经是字典格式（execute_query 返回字典列表）
                    qualification = {
                        'qualification_key': row.get('type_key'),
                        'qualification_name': row.get('type_name'),
                        'category': row.get('category'),
                        'is_required': bool(row.get('is_required')),
                        'description': row.get('description'),
                        'sort_order': row.get('sort_order'),
                        'is_active': bool(row.get('is_active')),
                        'created_at': row.get('created_at')
                    }
                    qualifications.append(qualification)

            logger.info(f"获取资质类型定义成功，共 {len(qualifications)} 个类型")
            return qualifications

        except Exception as e:
            logger.error(f"获取资质类型定义失败: {e}", exc_info=True)
            return []

    def get_all_documents_with_filters(self, company_id=None, product_id=None,
                                       document_category=None, privacy_classification=None):
        """
        获取所有文档（带筛选）- 文档库视图专用

        Args:
            company_id: 公司ID
            product_id: 产品ID
            document_category: 文档类型（tech/impl/service等）
            privacy_classification: 隐私级别

        Returns:
            list: 文档列表，每个文档包含公司名称和产品名称
        """
        try:
            # 构建SQL查询
            # 支持两种类型的文档库：产品文档库(owner_type='product')和企业信息库(owner_type='companies'或'company_profile')
            query = """
                SELECT
                    d.doc_id,
                    d.library_id,
                    d.filename,
                    d.original_filename,
                    d.file_path,
                    d.file_type,
                    d.file_size,
                    d.privacy_classification,
                    d.tags,
                    d.document_category,
                    d.upload_status,
                    d.parse_status,
                    d.vector_status,
                    d.upload_time,
                    COALESCE(c1.company_id, c2.company_id) as company_id,
                    COALESCE(c1.company_name, c2.company_name) as company_name,
                    p.product_id,
                    p.product_name
                FROM documents d
                INNER JOIN document_libraries dl ON d.library_id = dl.library_id
                LEFT JOIN products p ON dl.owner_type = 'product' AND dl.owner_id = p.product_id
                LEFT JOIN companies c1 ON p.company_id = c1.company_id
                LEFT JOIN companies c2 ON (dl.owner_type = 'companies' OR dl.owner_type = 'company_profile') AND dl.owner_id = c2.company_id
                WHERE 1=1
            """

            params = []

            # 添加筛选条件
            if company_id:
                query += " AND (c1.company_id = ? OR c2.company_id = ?)"
                params.append(company_id)
                params.append(company_id)

            if product_id:
                query += " AND p.product_id = ?"
                params.append(product_id)

            if document_category:
                query += " AND d.document_category = ?"
                params.append(document_category)

            if privacy_classification:
                query += " AND d.privacy_classification = ?"
                params.append(privacy_classification)

            # 按上传时间降序排序
            query += " ORDER BY d.upload_time DESC"

            # 执行查询
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                rows = cursor.fetchall()

                documents = []
                for row in rows:
                    doc = {
                        'doc_id': row['doc_id'],
                        'library_id': row['library_id'],
                        'filename': row['filename'],
                        'original_filename': row['original_filename'],
                        'file_path': row['file_path'],
                        'file_type': row['file_type'],
                        'file_size': row['file_size'],
                        'privacy_classification': row['privacy_classification'],
                        'tags': row['tags'],
                        'document_category': row['document_category'],
                        'upload_status': row['upload_status'],
                        'parse_status': row['parse_status'],
                        'vector_status': row['vector_status'],
                        'upload_time': row['upload_time'],
                        'company_id': row['company_id'],
                        'company_name': row['company_name'],
                        'product_id': row['product_id'],
                        'product_name': row['product_name']
                    }
                    documents.append(doc)

                logger.info(f"获取文档列表成功，共 {len(documents)} 个文档")
                return documents

        except Exception as e:
            logger.error(f"获取文档列表失败: {e}", exc_info=True)
            return []