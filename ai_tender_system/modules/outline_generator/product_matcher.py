#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
产品文档匹配器 - 阶段3
根据需求关键词从知识库匹配相关产品文档
"""

import json
import re
from typing import Dict, List, Any, Optional
from pathlib import Path

# 导入公共模块
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from common import get_module_logger, get_prompt_manager
from common.database import get_knowledge_base_db
from common.llm_client import create_llm_client


class ProductMatcher:
    """产品文档匹配器"""

    def __init__(self, model_name: str = "gpt-4o-mini", api_key: Optional[str] = None):
        """
        初始化产品文档匹配器

        Args:
            model_name: LLM模型名称
            api_key: API密钥（可选）
        """
        self.logger = get_module_logger("product_matcher")
        self.prompt_manager = get_prompt_manager()
        self.llm_client = create_llm_client(model_name, api_key)
        self.db = get_knowledge_base_db()

        self.logger.info("产品文档匹配器初始化完成")

    def match_documents(
        self,
        requirement_categories: List[Dict[str, Any]],
        company_id: Optional[int] = None
    ) -> Dict[str, List[Dict]]:
        """
        为需求类别匹配产品文档

        Args:
            requirement_categories: 需求类别列表
            company_id: 公司ID（可选，用于过滤公司文档）

        Returns:
            匹配结果字典 {category_code: [matched_docs]}
        """
        try:
            self.logger.info(f"开始匹配产品文档，需求类别数: {len(requirement_categories)}")

            matches = {}

            for category in requirement_categories:
                category_code = category.get('category_code', 'unknown')
                keywords = category.get('keywords', [])

                if not keywords:
                    continue

                # 从知识库搜索文档
                matched_docs = self._search_documents_by_keywords(
                    keywords,
                    company_id,
                    limit=5
                )

                if matched_docs:
                    matches[category_code] = matched_docs

            self.logger.info(f"匹配完成，共找到 {sum(len(v) for v in matches.values())} 份文档")
            return matches

        except Exception as e:
            self.logger.error(f"产品文档匹配失败: {e}", exc_info=True)
            return {}

    def _search_documents_by_keywords(
        self,
        keywords: List[str],
        company_id: Optional[int],
        limit: int = 5
    ) -> List[Dict]:
        """
        根据关键词搜索知识库文档

        Args:
            keywords: 关键词列表
            company_id: 公司ID
            limit: 返回文档数量限制

        Returns:
            匹配的文档列表
        """
        try:
            # 构建关键词查询
            keyword_query = ' '.join(keywords[:5])  # 最多使用5个关键词

            # 查询知识库
            with self.db.get_connection() as conn:
                # 构建SQL查询
                if company_id:
                    sql = """
                        SELECT
                            d.doc_id as document_id,
                            d.filename as title,
                            d.file_path,
                            d.file_type,
                            '' as summary,
                            0 as total_chunks
                        FROM documents d
                        INNER JOIN document_libraries dl ON d.library_id = dl.library_id
                        WHERE dl.owner_type = 'company'
                        AND dl.owner_id = ?
                        AND d.parse_status = 'completed'
                        AND (
                            d.filename LIKE ? OR
                            d.original_filename LIKE ? OR
                            d.tags LIKE ?
                        )
                        ORDER BY d.upload_time DESC
                        LIMIT ?
                    """
                    params = (
                        company_id,
                        f"%{keyword_query}%",
                        f"%{keyword_query}%",
                        f"%{keyword_query}%",
                        limit
                    )
                else:
                    # 不限制公司，搜索所有公开文档
                    sql = """
                        SELECT
                            d.doc_id as document_id,
                            d.filename as title,
                            d.file_path,
                            d.file_type,
                            '' as summary,
                            0 as total_chunks
                        FROM documents d
                        INNER JOIN document_libraries dl ON d.library_id = dl.library_id
                        WHERE dl.privacy_level = 1
                        AND d.parse_status = 'completed'
                        AND (
                            d.filename LIKE ? OR
                            d.original_filename LIKE ? OR
                            d.tags LIKE ?
                        )
                        ORDER BY d.upload_time DESC
                        LIMIT ?
                    """
                    params = (
                        f"%{keyword_query}%",
                        f"%{keyword_query}%",
                        f"%{keyword_query}%",
                        limit
                    )

                cursor = conn.execute(sql, params)
                rows = cursor.fetchall()

                # 转换为字典列表
                documents = []
                for row in rows:
                    doc = {
                        'doc_id': row[0],
                        'title': row[1],
                        'file_path': row[2],
                        'file_type': row[3],
                        'summary': row[4] or '',
                        'total_chunks': row[5] or 0
                    }
                    # 计算匹配度
                    doc['relevance_score'] = self._calculate_relevance(doc, keywords)
                    documents.append(doc)

                # 按相关度排序
                documents.sort(key=lambda x: x['relevance_score'], reverse=True)

                return documents

        except Exception as e:
            self.logger.error(f"知识库文档搜索失败: {e}")
            return []

    def _calculate_relevance(self, document: Dict, keywords: List[str]) -> float:
        """
        计算文档与关键词的相关度

        Args:
            document: 文档信息
            keywords: 关键词列表

        Returns:
            相关度分数 (0-100)
        """
        score = 0.0
        total_keywords = len(keywords)

        if total_keywords == 0:
            return 0.0

        title = document.get('title', '').lower()
        summary = document.get('summary', '').lower()

        for keyword in keywords:
            keyword_lower = keyword.lower()

            # 标题匹配（权重：5分）
            if keyword_lower in title:
                score += 5.0

            # 摘要匹配（权重：3分）
            if keyword_lower in summary:
                score += 3.0

        # 归一化到0-100
        max_score = total_keywords * 8.0  # 5 + 3
        if max_score > 0:
            score = min(100.0, (score / max_score) * 100)

        return round(score, 2)

    def get_document_content(self, document_id: int) -> Optional[str]:
        """
        获取文档内容

        Args:
            document_id: 文档ID

        Returns:
            文档内容文本，失败返回None
        """
        try:
            with self.db.get_connection() as conn:
                # 查询文档chunks
                sql = """
                    SELECT content
                    FROM document_chunks
                    WHERE doc_id = ?
                    ORDER BY chunk_index
                """
                cursor = conn.execute(sql, (document_id,))
                rows = cursor.fetchall()

                if not rows:
                    return None

                # 拼接所有chunks
                content = '\n\n'.join([row[0] for row in rows])
                return content

        except Exception as e:
            self.logger.error(f"获取文档内容失败: {e}")
            return None

    def recommend_documents_with_ai(
        self,
        requirement: str,
        keywords: List[str],
        category: str,
        available_docs: List[Dict]
    ) -> List[Dict]:
        """
        使用AI推荐最相关的文档

        Args:
            requirement: 需求描述
            keywords: 关键词
            category: 需求类别
            available_docs: 可用文档列表

        Returns:
            推荐的文档列表（按相关度排序）
        """
        try:
            if not available_docs:
                return []

            # 获取推荐提示词
            prompt_template = self.prompt_manager.get_prompt(
                'outline_generation',
                'recommend_product_docs'
            )

            if not prompt_template:
                # 如果没有提示词，直接返回前3个文档
                return available_docs[:3]

            # 构建文档列表字符串
            docs_str = json.dumps(available_docs, ensure_ascii=False, indent=2)

            # 生成提示词
            prompt = prompt_template.format(
                requirement=requirement,
                keywords=', '.join(keywords),
                category=category,
                available_docs=docs_str
            )

            # 调用LLM
            response = self.llm_client.call(
                prompt=prompt,
                temperature=0.7,
                max_retries=1,
                purpose="文档推荐"
            )

            # 解析响应
            recommended = self._parse_json_response(response)

            if recommended and isinstance(recommended, list):
                return recommended

            # 如果解析失败，返回原列表前3个
            return available_docs[:3]

        except Exception as e:
            self.logger.warning(f"AI文档推荐失败: {e}")
            return available_docs[:3]

    def _parse_json_response(self, response: str) -> Optional[Any]:
        """解析JSON响应"""
        if not response or not response.strip():
            return None

        # 移除markdown标记
        response = re.sub(r'^```json\s*', '', response.strip())
        response = re.sub(r'\s*```$', '', response.strip())

        # 尝试解析JSON数组或对象
        try:
            # 查找JSON数组
            if '[' in response:
                json_start = response.find('[')
                json_end = response.rfind(']') + 1
                if json_start != -1 and json_end > json_start:
                    return json.loads(response[json_start:json_end])

            # 查找JSON对象
            if '{' in response:
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                if json_start != -1 and json_end > json_start:
                    return json.loads(response[json_start:json_end])

        except json.JSONDecodeError:
            pass

        return None
