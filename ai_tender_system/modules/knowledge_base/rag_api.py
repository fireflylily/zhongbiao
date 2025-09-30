"""
RAG知识库API接口
提供文档向量化、智能检索等功能的REST API
"""
import logging
from flask import Blueprint, request, jsonify
from .rag_engine import get_rag_engine, LANGCHAIN_AVAILABLE

logger = logging.getLogger(__name__)

# 创建Blueprint
rag_api = Blueprint('rag_api', __name__)


@rag_api.route('/rag/status', methods=['GET'])
def get_rag_status():
    """获取RAG服务状态"""
    try:
        if not LANGCHAIN_AVAILABLE:
            return jsonify({
                'success': False,
                'available': False,
                'message': 'LangChain依赖未安装，RAG功能不可用'
            })

        engine = get_rag_engine()
        stats = engine.get_stats()

        return jsonify({
            'success': True,
            'available': True,
            'stats': stats
        })

    except Exception as e:
        logger.error(f"获取RAG状态失败: {e}")
        return jsonify({
            'success': False,
            'available': False,
            'error': str(e)
        }), 500


@rag_api.route('/rag/vectorize_document', methods=['POST'])
def vectorize_document():
    """
    向量化文档

    Request JSON:
    {
        "file_path": "/path/to/document.pdf",
        "metadata": {
            "company_id": 8,
            "product_id": 1,
            "document_id": 123,
            "document_type": "tech_doc",
            "document_name": "产品技术文档.pdf"
        }
    }
    """
    try:
        if not LANGCHAIN_AVAILABLE:
            return jsonify({
                'success': False,
                'error': 'RAG功能不可用，请安装依赖: pip install -r requirements_rag.txt'
            }), 503

        data = request.json
        file_path = data.get('file_path')
        metadata = data.get('metadata', {})

        if not file_path:
            return jsonify({
                'success': False,
                'error': '缺少file_path参数'
            }), 400

        # 执行向量化
        engine = get_rag_engine()
        result = engine.add_document(file_path, metadata)

        if result['success']:
            logger.info(f"文档向量化成功: {file_path}")
            return jsonify(result)
        else:
            logger.error(f"文档向量化失败: {result.get('error')}")
            return jsonify(result), 500

    except Exception as e:
        logger.error(f"向量化文档异常: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@rag_api.route('/rag/search', methods=['POST'])
def search_knowledge():
    """
    智能检索

    Request JSON:
    {
        "query": "公司有哪些ISO认证？",
        "company_id": 8,  // 可选，限定公司范围
        "product_id": 1,  // 可选，限定产品范围
        "k": 5            // 可选，返回结果数量，默认5
    }
    """
    try:
        if not LANGCHAIN_AVAILABLE:
            return jsonify({
                'success': False,
                'error': 'RAG功能不可用'
            }), 503

        data = request.json
        query = data.get('query')
        company_id = data.get('company_id')
        product_id = data.get('product_id')
        k = data.get('k', 5)

        if not query:
            return jsonify({
                'success': False,
                'error': '缺少query参数'
            }), 400

        # 构建过滤条件
        filter_dict = {}
        if company_id:
            filter_dict['company_id'] = company_id
        if product_id:
            filter_dict['product_id'] = product_id

        # 执行检索
        engine = get_rag_engine()
        results = engine.search(
            query=query,
            k=k,
            filter_dict=filter_dict if filter_dict else None
        )

        return jsonify({
            'success': True,
            'query': query,
            'results': results,
            'count': len(results)
        })

    except Exception as e:
        logger.error(f"智能检索异常: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@rag_api.route('/rag/delete_document', methods=['DELETE'])
def delete_document_vectors():
    """
    删除文档的向量数据

    Request JSON:
    {
        "document_id": 123,
        "company_id": 8
    }
    """
    try:
        if not LANGCHAIN_AVAILABLE:
            return jsonify({
                'success': False,
                'error': 'RAG功能不可用'
            }), 503

        data = request.json
        filter_dict = {}

        # 构建删除条件
        if data.get('document_id'):
            filter_dict['document_id'] = data['document_id']
        if data.get('company_id'):
            filter_dict['company_id'] = data['company_id']

        if not filter_dict:
            return jsonify({
                'success': False,
                'error': '至少需要提供一个过滤条件'
            }), 400

        # 执行删除
        engine = get_rag_engine()
        result = engine.delete_by_metadata(filter_dict)

        return jsonify(result)

    except Exception as e:
        logger.error(f"删除向量数据异常: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


logger.info("RAG API模块加载完成")