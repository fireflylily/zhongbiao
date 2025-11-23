#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
浏览器自动化API蓝图
提供信用中国网站自动截图等浏览器自动化功能
"""

import sys
import os
import time
from pathlib import Path
from flask import Blueprint, request, jsonify

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from common import get_module_logger, format_error_response
from services.browser_automation import screenshot_service, CreditChinaScreenshotService

# 创建蓝图
api_browser_automation_bp = Blueprint('api_browser_automation', __name__, url_prefix='/api/browser')

# 日志记录器
logger = get_module_logger("web.api_browser_automation")


def _execute_playwright_screenshot(company_name: str, query_type: str, config: dict) -> tuple:
    """
    执行Playwright截图的核心逻辑(可复用)

    Args:
        company_name: 公司名称
        query_type: 查询类型
        config: 截图配置信息

    Returns:
        (screenshot_success: bool, screenshot_method: str, screenshot_path: str)
    """
    url = config['url']
    search_selector = config['search_selector']
    search_button = config['search_button']
    result_selector = config['result_selector']
    screenshot_path = config['file_path']

    logger.info(f"📋 准备截图: {company_name} - {config['query_name']}")

    screenshot_success = False
    screenshot_method = 'config_only'

    # 尝试通过Python Playwright库执行
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            # 启动浏览器
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # 导航到目标页面
            logger.info(f"🌐 导航到: {url}")
            page.goto(url, timeout=30000)

            # 等待页面加载
            page.wait_for_load_state('networkidle', timeout=15000)

            # 填写搜索框
            logger.info(f"📝 填写公司名称: {company_name}")
            page.fill(search_selector, company_name)

            # 点击搜索按钮
            logger.info("🔍 点击查询按钮")
            page.click(search_button)

            # 等待结果显示
            logger.info("⏳ 等待查询结果...")
            page.wait_for_selector(result_selector, timeout=10000)

            # 等待额外时间确保页面完全加载
            page.wait_for_timeout(2000)

            # 截图
            logger.info(f"📸 截图保存到: {screenshot_path}")
            os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
            page.screenshot(path=screenshot_path, full_page=True)

            browser.close()

            screenshot_success = True
            screenshot_method = 'playwright_python'
            logger.info("✅ 截图成功 (Playwright Python)")

    except ImportError:
        logger.warning("⚠️  Playwright未安装,无法执行浏览器自动化")
        logger.info("💡 提示: 运行 'pip install playwright && playwright install chromium' 来安装")
    except Exception as playwright_error:
        logger.error(f"❌ Playwright操作失败: {playwright_error}")
        import traceback
        logger.error(traceback.format_exc())

    return screenshot_success, screenshot_method, screenshot_path


@api_browser_automation_bp.route('/creditchina/query-types', methods=['GET'])
def get_query_types():
    """
    获取可用的信用中国查询类型列表

    Returns:
        {
            "success": true,
            "data": [
                {
                    "key": "dishonest_executor",
                    "name": "失信被执行人",
                    "url": "https://..."
                }
            ]
        }
    """
    try:
        query_types = CreditChinaScreenshotService.get_available_query_types()
        return jsonify({
            'success': True,
            'data': query_types
        })
    except Exception as e:
        logger.error(f"获取查询类型失败: {e}")
        return jsonify(format_error_response(e))


@api_browser_automation_bp.route('/creditchina/screenshot', methods=['POST'])
def capture_screenshot():
    """
    截取信用中国网站截图

    POST参数:
    {
        "company_name": "公司名称",
        "query_type": "查询类型",
        "company_id": 公司ID (可选,用于自动关联资质)
    }

    Returns:
        {
            "success": true,
            "data": {
                "file_path": "截图文件路径",
                "filename": "文件名",
                "query_type": "查询类型",
                "query_name": "查询名称",
                "company_name": "公司名称",
                "screenshot_url": "截图预览URL"
            }
        }
    """
    try:
        data = request.get_json()
        if not data:
            raise ValueError("请求数据为空")

        company_name = data.get('company_name')
        query_type = data.get('query_type')
        company_id = data.get('company_id')

        if not company_name:
            raise ValueError("公司名称不能为空")
        if not query_type:
            raise ValueError("查询类型不能为空")

        logger.info(f"收到截图请求: 公司={company_name}, 类型={query_type}")

        # 获取截图配置信息
        config = screenshot_service.capture_screenshot(company_name, query_type)

        if not config['success']:
            raise Exception(config.get('error', '生成截图配置失败'))

        # 执行Playwright截图
        screenshot_success, screenshot_method, screenshot_path = _execute_playwright_screenshot(
            company_name, query_type, config
        )

        # 生成预览URL
        filename_only = os.path.basename(screenshot_path)
        screenshot_url = f"/api/files/serve/uploads/{filename_only}"

        # 如果提供了company_id且截图成功,自动关联到公司资质
        qualification_id = None
        if company_id and screenshot_success:
            try:
                from common.database import get_knowledge_base_db
                db = get_knowledge_base_db()

                # 插入资质记录
                insert_query = """
                INSERT INTO company_qualifications
                (company_id, qualification_key, file_path, original_filename, file_size, upload_date)
                VALUES (?, ?, ?, ?, ?, datetime('now'))
                """

                file_size = os.path.getsize(screenshot_path) if os.path.exists(screenshot_path) else 0

                db.execute_update(insert_query, [
                    company_id,
                    query_type,
                    screenshot_path,
                    filename_only,
                    file_size
                ])

                # 获取插入的ID
                result = db.execute_query(
                    "SELECT qualification_id FROM company_qualifications WHERE company_id = ? AND qualification_key = ? ORDER BY qualification_id DESC LIMIT 1",
                    [company_id, query_type],
                    fetch_one=True
                )
                if result:
                    qualification_id = result['qualification_id']
                    logger.info(f"✅ 已关联到资质库: 公司{company_id}, 资质ID={qualification_id}")

            except Exception as db_error:
                logger.error(f"❌ 关联资质库失败: {db_error}")

        return jsonify({
            'success': screenshot_success,
            'data': {
                'file_path': screenshot_path,
                'filename': filename_only,
                'query_type': config['query_type'],
                'query_name': config['query_name'],
                'company_name': company_name,
                'screenshot_url': screenshot_url,
                'screenshot_exists': os.path.exists(screenshot_path) if screenshot_success else False,
                'screenshot_method': screenshot_method,
                'qualification_id': qualification_id,
                'config': config if not screenshot_success else None  # 只在失败时返回配置供调试
            },
            'message': '截图成功并已关联到资质库' if qualification_id else ('截图成功' if screenshot_success else '截图配置已生成,等待浏览器执行')
        })

    except Exception as e:
        logger.error(f"截图请求处理失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify(format_error_response(e))


@api_browser_automation_bp.route('/creditchina/screenshot/batch', methods=['POST'])
def capture_batch_screenshots():
    """
    批量截取信用中国网站截图

    POST参数:
    {
        "company_name": "公司名称",
        "query_types": ["dishonest_executor", "tax_violation_check", "gov_procurement_creditchina"],
        "company_id": 公司ID (可选)
    }

    Returns:
        {
            "success": true,
            "data": {
                "results": [截图结果列表],
                "stats": {
                    "total": 总数,
                    "succeeded": 成功数,
                    "failed": 失败数
                }
            }
        }
    """
    try:
        data = request.get_json()
        if not data:
            raise ValueError("请求数据为空")

        company_name = data.get('company_name')
        query_types = data.get('query_types', [])
        company_id = data.get('company_id')

        if not company_name:
            raise ValueError("公司名称不能为空")
        if not query_types:
            raise ValueError("查询类型列表不能为空")

        logger.info(f"收到批量截图请求: 公司={company_name}, 类型数={len(query_types)}")

        # 批量执行截图
        results = []
        stats = {'total': len(query_types), 'succeeded': 0, 'failed': 0}

        for query_type in query_types:
            try:
                # 获取配置
                config = screenshot_service.capture_screenshot(company_name, query_type)
                if not config['success']:
                    results.append({
                        'success': False,
                        'error': config.get('error', '配置生成失败'),
                        'query_type': query_type,
                        'company_name': company_name
                    })
                    stats['failed'] += 1
                    continue

                # 执行截图
                screenshot_success, screenshot_method, screenshot_path = _execute_playwright_screenshot(
                    company_name, query_type, config
                )

                filename_only = os.path.basename(screenshot_path)
                screenshot_url = f"/api/files/serve/uploads/{filename_only}"

                # 如果成功且有company_id,关联到资质库
                qualification_id = None
                if company_id and screenshot_success:
                    try:
                        from common.database import get_knowledge_base_db
                        db = get_knowledge_base_db()

                        insert_query = """
                        INSERT INTO company_qualifications
                        (company_id, qualification_key, file_path, original_filename, file_size, upload_date)
                        VALUES (?, ?, ?, ?, ?, datetime('now'))
                        """

                        file_size = os.path.getsize(screenshot_path) if os.path.exists(screenshot_path) else 0

                        db.execute_update(insert_query, [
                            company_id, query_type, screenshot_path,
                            filename_only, file_size
                        ])

                        result = db.execute_query(
                            "SELECT qualification_id FROM company_qualifications WHERE company_id = ? AND qualification_key = ? ORDER BY qualification_id DESC LIMIT 1",
                            [company_id, query_type],
                            fetch_one=True
                        )
                        if result:
                            qualification_id = result['qualification_id']
                            logger.info(f"✅ 已关联到资质库: 资质ID={qualification_id}")

                    except Exception as db_error:
                        logger.error(f"❌ 关联资质库失败: {db_error}")

                # 记录结果
                results.append({
                    'success': screenshot_success,
                    'file_path': screenshot_path,
                    'filename': filename_only,
                    'query_type': query_type,
                    'query_name': config['query_name'],
                    'company_name': company_name,
                    'screenshot_url': screenshot_url,
                    'screenshot_method': screenshot_method,
                    'qualification_id': qualification_id
                })

                if screenshot_success:
                    stats['succeeded'] += 1
                else:
                    stats['failed'] += 1

            except Exception as e:
                logger.error(f"截图失败 {query_type}: {e}")
                results.append({
                    'success': False,
                    'error': str(e),
                    'query_type': query_type,
                    'company_name': company_name
                })
                stats['failed'] += 1

        return jsonify({
            'success': stats['failed'] == 0,
            'data': {
                'results': results,
                'stats': stats,
                'company_name': company_name
            }
        })

    except Exception as e:
        logger.error(f"批量截图请求处理失败: {e}")
        return jsonify(format_error_response(e))


@api_browser_automation_bp.route('/creditchina/screenshot/all', methods=['POST'])
def capture_all_screenshots():
    """
    截取公司的所有信用查询截图

    POST参数:
    {
        "company_name": "公司名称",
        "company_id": 公司ID (可选)
    }

    Returns:
        批量截图结果
    """
    try:
        data = request.get_json()
        if not data:
            raise ValueError("请求数据为空")

        company_name = data.get('company_name')
        company_id = data.get('company_id')

        if not company_name:
            raise ValueError("公司名称不能为空")

        logger.info(f"收到全量截图请求: 公司={company_name}")

        # 获取所有查询类型
        all_types = list(CreditChinaScreenshotService.QUERY_TYPES.keys())

        # 批量执行截图
        results = []
        stats = {'total': len(all_types), 'succeeded': 0, 'failed': 0}

        for query_type in all_types:
            try:
                # 获取配置
                config = screenshot_service.capture_screenshot(company_name, query_type)
                if not config['success']:
                    results.append({
                        'success': False,
                        'error': config.get('error', '配置生成失败'),
                        'query_type': query_type,
                        'company_name': company_name
                    })
                    stats['failed'] += 1
                    continue

                # 执行截图
                screenshot_success, screenshot_method, screenshot_path = _execute_playwright_screenshot(
                    company_name, query_type, config
                )

                filename_only = os.path.basename(screenshot_path)
                screenshot_url = f"/api/files/serve/uploads/{filename_only}"

                # 如果成功且有company_id,关联到资质库
                qualification_id = None
                if company_id and screenshot_success:
                    try:
                        from common.database import get_knowledge_base_db
                        db = get_knowledge_base_db()

                        insert_query = """
                        INSERT INTO company_qualifications
                        (company_id, qualification_key, file_path, original_filename, file_size, upload_date)
                        VALUES (?, ?, ?, ?, ?, datetime('now'))
                        """

                        file_size = os.path.getsize(screenshot_path) if os.path.exists(screenshot_path) else 0

                        db.execute_update(insert_query, [
                            company_id, query_type, screenshot_path,
                            filename_only, file_size
                        ])

                        result = db.execute_query(
                            "SELECT qualification_id FROM company_qualifications WHERE company_id = ? AND qualification_key = ? ORDER BY qualification_id DESC LIMIT 1",
                            [company_id, query_type],
                            fetch_one=True
                        )
                        if result:
                            qualification_id = result['qualification_id']
                            logger.info(f"✅ 已关联到资质库: {query_type}, 资质ID={qualification_id}")

                    except Exception as db_error:
                        logger.error(f"❌ 关联资质库失败: {db_error}")

                # 记录结果
                results.append({
                    'success': screenshot_success,
                    'file_path': screenshot_path,
                    'filename': filename_only,
                    'query_type': query_type,
                    'query_name': config['query_name'],
                    'company_name': company_name,
                    'screenshot_url': screenshot_url,
                    'screenshot_method': screenshot_method,
                    'qualification_id': qualification_id
                })

                if screenshot_success:
                    stats['succeeded'] += 1
                else:
                    stats['failed'] += 1

            except Exception as e:
                logger.error(f"截图失败 {query_type}: {e}")
                results.append({
                    'success': False,
                    'error': str(e),
                    'query_type': query_type,
                    'company_name': company_name
                })
                stats['failed'] += 1

        return jsonify({
            'success': stats['failed'] == 0,
            'data': {
                'results': results,
                'stats': stats,
                'company_name': company_name
            }
        })

    except Exception as e:
        logger.error(f"全量截图请求处理失败: {e}")
        return jsonify(format_error_response(e))


__all__ = ['api_browser_automation_bp']
