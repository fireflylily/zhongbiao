#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识库管理器
功能：企业信息、产品、文档的业务逻辑处理
"""

import os
import json
import hashlib
from datetime import datetime
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
                       privacy_classification: int = 1, document_category: str = 'tech',
                       tags: List[str] = None, metadata: Dict = None) -> Dict:
        """上传文档到文档库"""
        try:
            # 生成文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_ext = Path(original_filename).suffix.lower()
            filename = f"{timestamp}_{hashlib.md5(original_filename.encode()).hexdigest()[:8]}{file_ext}"

            # 保存文件
            file_path = self.upload_dir / filename
            file_obj.save(str(file_path))

            # 获取文件信息
            file_size = file_path.stat().st_size
            file_type = file_ext[1:]  # 去掉点号

            # 创建文档记录
            doc_id = self.db.create_document(
                library_id=library_id,
                filename=filename,
                original_filename=original_filename,
                file_path=str(file_path),
                file_type=file_type,
                file_size=file_size,
                privacy_classification=privacy_classification,
                document_category=document_category,
                tags=tags,
                metadata=metadata
            )

            logger.info(f"文档上传成功: {original_filename} -> {filename} (ID: {doc_id})")

            return {
                'success': True,
                'doc_id': doc_id,
                'filename': filename,
                'message': f"文档 '{original_filename}' 上传成功"
            }

        except Exception as e:
            logger.error(f"文档上传失败: {e}")
            # 如果数据库操作失败，删除已上传的文件
            if 'file_path' in locals() and file_path.exists():
                file_path.unlink()

            return {
                'success': False,
                'error': str(e)
            }

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
                    except:
                        doc['tags'] = []

                if doc.get('metadata'):
                    try:
                        doc['metadata'] = json.loads(doc['metadata'])
                    except:
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

            # 删除物理文件
            file_path = Path(document['file_path'])
            if file_path.exists():
                file_path.unlink()
                logger.info(f"已删除物理文件: {file_path}")

            # 删除数据库记录
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
        """按文档分类统计"""
        try:
            query = """
            SELECT document_category, COUNT(*) as count
            FROM documents
            GROUP BY document_category
            """
            results = self.db.execute_query(query)
            return {item['document_category']: item['count'] for item in results}
        except:
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
        except:
            return {}

    def search_documents(self, query: str, category: str = None, privacy_level: int = 1) -> List[Dict]:
        """搜索文档（基础版本，后续可增强为向量搜索）"""
        try:
            conditions = ["d.privacy_classification <= ?"]
            params = [privacy_level]

            # 添加分类过滤
            if category:
                conditions.append("d.document_category = ?")
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
                result['category'] = result.get('document_category', 'tech')
                result['filename'] = result['original_filename']

            return results

        except Exception as e:
            logger.error(f"搜索文档失败: {e}")
            return []