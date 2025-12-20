#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
章节解析器A/B测试API

提供多种解析器的并行测试和对比功能
"""

import os
import sys
import json
import tempfile
from pathlib import Path
from flask import Blueprint, request, jsonify, render_template
from werkzeug.utils import secure_filename

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from common import get_module_logger
from ai_tender_system.modules.tender_processing.parsers import ParserFactory

# 创建蓝图
parser_abtest_bp = Blueprint('parser_abtest', __name__)
logger = get_module_logger("abtest.parser")


@parser_abtest_bp.route('/parser-test')
def parser_test_page():
    """章节解析器测试页面"""
    return render_template('parser_test.html')


@parser_abtest_bp.route('/api/parsers', methods=['GET'])
def get_available_parsers():
    """获取所有可用的解析器列表

    Returns:
        {
            "success": true,
            "parsers": [
                {
                    "name": "builtin",
                    "display_name": "内置解析器",
                    "description": "...",
                    "available": true,
                    "requires_api": false,
                    "cost_per_page": 0.0
                },
                ...
            ]
        }
    """
    try:
        parsers = ParserFactory.get_available_parsers()

        return jsonify({
            "success": True,
            "parsers": parsers
        })

    except Exception as e:
        logger.error(f"获取解析器列表失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@parser_abtest_bp.route('/api/parse-single', methods=['POST'])
def parse_single():
    """使用单个解析器解析文档

    Form Data:
        file: 上传的文档文件
        parser: 解析器名称 (builtin/gemini)

    Returns:
        {
            "success": true,
            "parser": "gemini",
            "result": {
                "success": true,
                "chapters": [...],
                "statistics": {...},
                "metrics": {...}
            }
        }
    """
    try:
        # 获取参数
        if 'file' not in request.files:
            return jsonify({"success": False, "error": "未上传文件"}), 400

        file = request.files['file']
        parser_name = request.form.get('parser', 'builtin')

        if file.filename == '':
            return jsonify({"success": False, "error": "文件名为空"}), 400

        # 保存上传的文件
        filename = secure_filename(file.filename)
        temp_dir = Path(tempfile.gettempdir()) / 'parser_abtest'
        temp_dir.mkdir(exist_ok=True)

        file_path = temp_dir / filename
        file.save(str(file_path))

        logger.info(f"使用解析器'{parser_name}'解析文件: {filename}")

        # 创建解析器
        parser = ParserFactory.create_parser(parser_name)

        # 执行解析
        result = parser.parse_structure(str(file_path))

        # 清理临时文件
        file_path.unlink(missing_ok=True)

        return jsonify({
            "success": True,
            "parser": parser_name,
            "result": result
        })

    except ValueError as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400

    except Exception as e:
        logger.error(f"解析失败: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": f"解析失败: {str(e)}"
        }), 500


@parser_abtest_bp.route('/api/parse-compare', methods=['POST'])
def parse_compare():
    """并行对比多个解析器

    Form Data:
        file: 上传的文档文件
        parsers: 解析器列表,逗号分隔 (如: "builtin,gemini")

    Returns:
        {
            "success": true,
            "results": {
                "builtin": {...},
                "gemini": {...}
            },
            "comparison": {
                "fastest": "builtin",
                "most_chapters": "gemini",
                "highest_confidence": "gemini"
            }
        }
    """
    try:
        # 获取参数
        if 'file' not in request.files:
            return jsonify({"success": False, "error": "未上传文件"}), 400

        file = request.files['file']
        parsers_str = request.form.get('parsers', 'builtin,gemini')
        parser_names = [p.strip() for p in parsers_str.split(',')]

        if file.filename == '':
            return jsonify({"success": False, "error": "文件名为空"}), 400

        # 保存上传的文件
        filename = secure_filename(file.filename)
        temp_dir = Path(tempfile.gettempdir()) / 'parser_abtest'
        temp_dir.mkdir(exist_ok=True)

        file_path = temp_dir / filename
        file.save(str(file_path))

        logger.info(f"对比解析器: {parser_names}, 文件: {filename}")

        # 并行执行所有解析器
        results = {}
        for parser_name in parser_names:
            try:
                parser = ParserFactory.create_parser(parser_name)

                # 检查解析器是否可用
                if not parser.is_available():
                    results[parser_name] = {
                        "success": False,
                        "error": f"{parser_name}解析器不可用,请检查配置"
                    }
                    continue

                result = parser.parse_structure(str(file_path))
                results[parser_name] = result

            except Exception as e:
                logger.error(f"解析器'{parser_name}'执行失败: {e}")
                results[parser_name] = {
                    "success": False,
                    "error": str(e)
                }

        # 清理临时文件
        file_path.unlink(missing_ok=True)

        # 对比分析
        comparison = _analyze_results(results)

        return jsonify({
            "success": True,
            "results": results,
            "comparison": comparison
        })

    except Exception as e:
        logger.error(f"对比解析失败: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": f"对比解析失败: {str(e)}"
        }), 500


def _analyze_results(results: dict) -> dict:
    """分析对比结果

    Args:
        results: {parser_name: result_dict}

    Returns:
        对比分析结果
    """
    # 过滤出成功的结果
    successful_results = {
        name: res for name, res in results.items()
        if res.get('success', False)
    }

    if not successful_results:
        return {
            "fastest": None,
            "most_chapters": None,
            "highest_confidence": None,
            "lowest_cost": None
        }

    # 找出最快的
    fastest = min(
        successful_results.items(),
        key=lambda x: x[1].get('metrics', {}).parse_time
            if hasattr(x[1].get('metrics', {}), 'parse_time')
            else x[1].get('metrics', {}).get('parse_time', 999)
    )[0]

    # 找出章节最多的
    most_chapters = max(
        successful_results.items(),
        key=lambda x: x[1].get('metrics', {}).chapters_found
            if hasattr(x[1].get('metrics', {}), 'chapters_found')
            else x[1].get('metrics', {}).get('chapters_found', 0)
    )[0]

    # 找出置信度最高的
    highest_confidence = max(
        successful_results.items(),
        key=lambda x: x[1].get('metrics', {}).confidence_score
            if hasattr(x[1].get('metrics', {}), 'confidence_score')
            else x[1].get('metrics', {}).get('confidence_score', 0)
    )[0]

    # 找出成本最低的
    lowest_cost = min(
        successful_results.items(),
        key=lambda x: x[1].get('metrics', {}).api_cost
            if hasattr(x[1].get('metrics', {}), 'api_cost')
            else x[1].get('metrics', {}).get('api_cost', 0)
    )[0]

    return {
        "fastest": fastest,
        "most_chapters": most_chapters,
        "highest_confidence": highest_confidence,
        "lowest_cost": lowest_cost,
        "summary": _generate_summary(successful_results)
    }


def _generate_summary(results: dict) -> dict:
    """生成汇总统计

    Returns:
        {
            "total_parsers_tested": 2,
            "successful_parsers": 2,
            "average_parse_time": 3.5,
            "average_chapters_found": 15.5,
            ...
        }
    """
    total = len(results)

    if total == 0:
        return {}

    # 计算平均值
    avg_time = sum(
        res.get('metrics', {}).parse_time
        if hasattr(res.get('metrics', {}), 'parse_time')
        else res.get('metrics', {}).get('parse_time', 0)
        for res in results.values()
    ) / total

    avg_chapters = sum(
        res.get('metrics', {}).chapters_found
        if hasattr(res.get('metrics', {}), 'chapters_found')
        else res.get('metrics', {}).get('chapters_found', 0)
        for res in results.values()
    ) / total

    avg_confidence = sum(
        res.get('metrics', {}).confidence_score
        if hasattr(res.get('metrics', {}), 'confidence_score')
        else res.get('metrics', {}).get('confidence_score', 0)
        for res in results.values()
    ) / total

    total_cost = sum(
        res.get('metrics', {}).api_cost
        if hasattr(res.get('metrics', {}), 'api_cost')
        else res.get('metrics', {}).get('api_cost', 0)
        for res in results.values()
    )

    return {
        "total_parsers_tested": total,
        "successful_parsers": total,
        "average_parse_time": round(avg_time, 2),
        "average_chapters_found": round(avg_chapters, 1),
        "average_confidence": round(avg_confidence, 1),
        "total_cost": round(total_cost, 4)
    }


# 导出蓝图
__all__ = ['parser_abtest_bp']
