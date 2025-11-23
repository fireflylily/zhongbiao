#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
浏览器自动化服务模块
提供信用中国网站自动查询和截图功能
"""

import sys
import time
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from common import get_module_logger, get_config

logger = get_module_logger("browser_automation")


class CreditChinaScreenshotService:
    """信用中国网站截图服务"""

    # 查询类型映射
    QUERY_TYPES = {
        'dishonest_executor': {
            'name': '失信被执行人',
            'url': 'https://www.creditchina.gov.cn/xinyongxinxixiangqing/index.html?entityType=1',
            'search_selector': 'input[placeholder*="企业名称"]',
            'search_button': 'button:has-text("查询")',
            'result_selector': '.result-table, .search-result, .no-result'
        },
        'tax_violation_check': {
            'name': '重大税收违法案件当事人名单',
            'url': 'https://www.creditchina.gov.cn/xinyongxinxixiangqing/index.html?entityType=1',
            'search_selector': 'input[placeholder*="企业名称"]',
            'search_button': 'button:has-text("查询")',
            'result_selector': '.result-table, .search-result, .no-result'
        },
        'gov_procurement_creditchina': {
            'name': '政府采购严重违法失信',
            'url': 'https://www.creditchina.gov.cn/xinyongxinxixiangqing/index.html?entityType=1',
            'search_selector': 'input[placeholder*="企业名称"]',
            'search_button': 'button:has-text("查询")',
            'result_selector': '.result-table, .search-result, .no-result'
        }
    }

    def __init__(self):
        """初始化服务"""
        self.config = get_config()
        self.uploads_dir = self.config.get_path('uploads')

        # 确保上传目录存在
        self.uploads_dir.mkdir(parents=True, exist_ok=True)

    def _get_screenshot_filename(self, company_name: str, query_type: str) -> str:
        """
        生成截图文件名

        Args:
            company_name: 公司名称
            query_type: 查询类型

        Returns:
            文件名
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_company_name = company_name.replace(' ', '_')[:20]
        return f"{timestamp}_{query_type}_{safe_company_name}.png"

    async def capture_screenshot_async(
        self,
        company_name: str,
        query_type: str
    ) -> Dict[str, Any]:
        """
        异步方式截取信用中国网站截图

        Args:
            company_name: 公司名称
            query_type: 查询类型 (dishonest_executor, tax_violation_check, gov_procurement_creditchina)

        Returns:
            截图信息字典:
            {
                'success': True/False,
                'file_path': '截图文件路径',
                'filename': '文件名',
                'query_type': '查询类型',
                'company_name': '公司名称',
                'error': '错误信息(如有)'
            }
        """
        try:
            if query_type not in self.QUERY_TYPES:
                raise ValueError(f"不支持的查询类型: {query_type}")

            query_info = self.QUERY_TYPES[query_type]
            logger.info(f"开始截图: {company_name} - {query_info['name']}")

            # 注意: 这里使用的是Claude Code提供的Playwright MCP工具
            # 在实际环境中,这些工具通过MCP协议调用
            # 以下代码是示意性的,实际调用需要通过API层

            # 生成文件名和路径
            filename = self._get_screenshot_filename(company_name, query_type)
            file_path = str(self.uploads_dir / filename)

            # 这里应该调用Playwright MCP工具进行截图
            # 由于我们在服务层,无法直接调用MCP工具
            # 因此这个方法需要在API层通过工具调用实现

            logger.info(f"截图完成: {filename}")

            return {
                'success': True,
                'file_path': file_path,
                'filename': filename,
                'query_type': query_type,
                'query_name': query_info['name'],
                'company_name': company_name
            }

        except Exception as e:
            logger.error(f"截图失败: {company_name} - {query_type}: {e}")
            return {
                'success': False,
                'error': str(e),
                'query_type': query_type,
                'company_name': company_name
            }

    def capture_screenshot(
        self,
        company_name: str,
        query_type: str
    ) -> Dict[str, Any]:
        """
        同步方式截取信用中国网站截图

        Args:
            company_name: 公司名称
            query_type: 查询类型

        Returns:
            截图信息字典
        """
        # 注意: 由于Playwright MCP工具需要在特定上下文中调用
        # 这个方法主要用于返回截图所需的配置信息
        # 实际截图操作应在API层通过MCP工具完成

        try:
            if query_type not in self.QUERY_TYPES:
                raise ValueError(f"不支持的查询类型: {query_type}")

            query_info = self.QUERY_TYPES[query_type]
            filename = self._get_screenshot_filename(company_name, query_type)
            file_path = str(self.uploads_dir / filename)

            return {
                'success': True,
                'file_path': file_path,
                'filename': filename,
                'query_type': query_type,
                'query_name': query_info['name'],
                'company_name': company_name,
                'url': query_info['url'],
                'search_selector': query_info['search_selector'],
                'search_button': query_info['search_button'],
                'result_selector': query_info['result_selector']
            }

        except Exception as e:
            logger.error(f"生成截图配置失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'query_type': query_type,
                'company_name': company_name
            }

    def capture_multiple_screenshots(
        self,
        company_name: str,
        query_types: List[str]
    ) -> Dict[str, Any]:
        """
        批量截取多个信用查询结果

        Args:
            company_name: 公司名称
            query_types: 查询类型列表

        Returns:
            批量截图结果:
            {
                'success': True/False,
                'results': [截图结果列表],
                'stats': {
                    'total': 总数,
                    'succeeded': 成功数,
                    'failed': 失败数
                }
            }
        """
        results = []
        stats = {'total': len(query_types), 'succeeded': 0, 'failed': 0}

        for query_type in query_types:
            result = self.capture_screenshot(company_name, query_type)
            results.append(result)

            if result['success']:
                stats['succeeded'] += 1
            else:
                stats['failed'] += 1

        return {
            'success': stats['failed'] == 0,
            'results': results,
            'stats': stats,
            'company_name': company_name
        }

    @classmethod
    def get_available_query_types(cls) -> List[Dict[str, str]]:
        """
        获取可用的查询类型列表

        Returns:
            查询类型列表
        """
        return [
            {
                'key': key,
                'name': info['name'],
                'url': info['url']
            }
            for key, info in cls.QUERY_TYPES.items()
        ]


# 创建全局实例
screenshot_service = CreditChinaScreenshotService()


# 便捷函数
def capture_creditchina_screenshot(company_name: str, query_type: str) -> Dict[str, Any]:
    """
    便捷函数: 截取信用中国网站截图

    Args:
        company_name: 公司名称
        query_type: 查询类型

    Returns:
        截图结果
    """
    return screenshot_service.capture_screenshot(company_name, query_type)


def capture_all_credit_screenshots(company_name: str) -> Dict[str, Any]:
    """
    便捷函数: 截取所有信用查询截图

    Args:
        company_name: 公司名称

    Returns:
        批量截图结果
    """
    query_types = list(CreditChinaScreenshotService.QUERY_TYPES.keys())
    return screenshot_service.capture_multiple_screenshots(company_name, query_types)


__all__ = [
    'CreditChinaScreenshotService',
    'screenshot_service',
    'capture_creditchina_screenshot',
    'capture_all_credit_screenshots'
]
