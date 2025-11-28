#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动化测试运行器 API
提供Web界面运行pytest测试的功能
"""

import os
import sys
import json
import subprocess
import threading
import time
from datetime import datetime
from pathlib import Path
from flask import Blueprint, request, jsonify
from typing import Dict, List, Optional

# 创建蓝图
api_test_runner_bp = Blueprint('api_test_runner', __name__, url_prefix='/api/test')

# 全局测试任务状态
_test_tasks: Dict[str, dict] = {}
_test_task_lock = threading.Lock()

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent


def run_pytest_async(task_id: str, test_type: str, args: List[str]):
    """
    异步运行pytest测试

    Args:
        task_id: 任务ID
        test_type: 测试类型 (unit/integration/all)
        args: pytest参数列表
    """
    try:
        # 更新任务状态
        with _test_task_lock:
            _test_tasks[task_id]['status'] = 'running'
            _test_tasks[task_id]['start_time'] = datetime.now().isoformat()

        # 构建pytest命令
        cmd = [sys.executable, '-m', 'pytest'] + args

        # 运行pytest
        process = subprocess.Popen(
            cmd,
            cwd=str(PROJECT_ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

        # 收集输出
        output_lines = []
        for line in iter(process.stdout.readline, ''):
            if line:
                output_lines.append(line.rstrip())
                # 实时更新日志
                with _test_task_lock:
                    _test_tasks[task_id]['logs'] = output_lines[-100:]  # 只保留最后100行

        process.wait()

        # 解析测试结果
        result = {
            'return_code': process.returncode,
            'passed': process.returncode == 0,
            'output': '\n'.join(output_lines)
        }

        # 解析测试统计
        stats = parse_test_output('\n'.join(output_lines))
        result.update(stats)

        # 更新任务状态
        with _test_task_lock:
            _test_tasks[task_id].update({
                'status': 'completed',
                'end_time': datetime.now().isoformat(),
                'result': result,
                'logs': output_lines
            })

    except Exception as e:
        with _test_task_lock:
            _test_tasks[task_id].update({
                'status': 'failed',
                'end_time': datetime.now().isoformat(),
                'error': str(e)
            })


def parse_test_output(output: str) -> dict:
    """
    解析pytest输出，提取测试统计信息

    Args:
        output: pytest输出文本

    Returns:
        dict: 包含测试统计的字典
    """
    stats = {
        'total': 0,
        'passed': 0,
        'failed': 0,
        'skipped': 0,
        'errors': 0,
        'duration': 0.0
    }

    # 解析最后一行的统计信息
    # 例如: "15 failed, 4 passed, 2 skipped in 1.00s"
    lines = output.split('\n')
    for line in reversed(lines):
        if ' passed' in line or ' failed' in line:
            # 提取各种状态的数量
            import re

            passed_match = re.search(r'(\d+)\s+passed', line)
            if passed_match:
                stats['passed'] = int(passed_match.group(1))

            failed_match = re.search(r'(\d+)\s+failed', line)
            if failed_match:
                stats['failed'] = int(failed_match.group(1))

            skipped_match = re.search(r'(\d+)\s+skipped', line)
            if skipped_match:
                stats['skipped'] = int(skipped_match.group(1))

            error_match = re.search(r'(\d+)\s+error', line)
            if error_match:
                stats['errors'] = int(error_match.group(1))

            # 提取耗时
            time_match = re.search(r'in\s+([\d.]+)s', line)
            if time_match:
                stats['duration'] = float(time_match.group(1))

            break

    stats['total'] = stats['passed'] + stats['failed'] + stats['skipped'] + stats['errors']

    return stats


@api_test_runner_bp.route('/run', methods=['POST'])
def run_tests():
    """
    运行测试

    Request JSON:
        {
            "test_type": "unit|integration|all",
            "coverage": true,
            "verbose": true
        }

    Returns:
        {
            "success": true,
            "task_id": "test_xxx",
            "message": "测试已开始"
        }
    """
    try:
        data = request.get_json() or {}
        test_type = data.get('test_type', 'unit')
        coverage = data.get('coverage', True)
        verbose = data.get('verbose', True)

        # 生成任务ID
        task_id = f"test_{int(time.time() * 1000)}"

        # 构建pytest参数
        args = []

        # 选择测试路径
        if test_type == 'unit':
            args.append('tests/unit/')
        elif test_type == 'integration':
            args.extend(['tests/', '-m', 'integration'])
        elif test_type == 'all':
            args.append('tests/')
        else:
            return jsonify({
                'success': False,
                'error': f'不支持的测试类型: {test_type}'
            }), 400

        # 添加其他参数
        if verbose:
            args.append('-v')

        args.extend(['--tb=short', '--maxfail=50'])

        # 跳过慢速测试
        args.extend(['-m', 'not slow'])

        if coverage:
            args.extend([
                '--cov=ai_tender_system',
                '--cov-report=html',
                '--cov-report=json',
                '--cov-report=term'
            ])

        # 初始化任务
        with _test_task_lock:
            _test_tasks[task_id] = {
                'task_id': task_id,
                'test_type': test_type,
                'coverage': coverage,
                'status': 'pending',
                'created_time': datetime.now().isoformat(),
                'start_time': None,
                'end_time': None,
                'result': None,
                'logs': [],
                'error': None
            }

        # 在后台线程运行测试
        thread = threading.Thread(
            target=run_pytest_async,
            args=(task_id, test_type, args),
            daemon=True
        )
        thread.start()

        return jsonify({
            'success': True,
            'task_id': task_id,
            'message': '测试已开始运行'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_test_runner_bp.route('/status/<task_id>', methods=['GET'])
def get_test_status(task_id: str):
    """
    获取测试任务状态

    Returns:
        {
            "success": true,
            "task": {
                "task_id": "test_xxx",
                "status": "running|completed|failed",
                "result": {...},
                "logs": [...]
            }
        }
    """
    try:
        with _test_task_lock:
            task = _test_tasks.get(task_id)

        if not task:
            return jsonify({
                'success': False,
                'error': '任务不存在'
            }), 404

        return jsonify({
            'success': True,
            'task': task
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_test_runner_bp.route('/coverage', methods=['GET'])
def get_coverage_data():
    """
    获取最新的测试覆盖率数据

    Returns:
        {
            "success": true,
            "coverage": {
                "total_statements": 5830,
                "covered_statements": 799,
                "coverage_percent": 10.56,
                "files": [...]
            }
        }
    """
    try:
        coverage_file = PROJECT_ROOT / 'coverage.json'

        if not coverage_file.exists():
            return jsonify({
                'success': False,
                'error': '覆盖率数据不存在，请先运行测试'
            }), 404

        # 读取覆盖率JSON数据
        with open(coverage_file, 'r', encoding='utf-8') as f:
            coverage_data = json.load(f)

        # 提取关键信息
        totals = coverage_data.get('totals', {})
        files_data = coverage_data.get('files', {})

        # 构建文件列表
        files = []
        for file_path, file_data in files_data.items():
            summary = file_data.get('summary', {})
            files.append({
                'file': file_path.replace(str(PROJECT_ROOT) + '/', ''),
                'statements': summary.get('num_statements', 0),
                'missing': summary.get('missing_lines', 0),
                'covered': summary.get('covered_lines', 0),
                'coverage': summary.get('percent_covered', 0)
            })

        # 按覆盖率排序
        files.sort(key=lambda x: x['coverage'])

        return jsonify({
            'success': True,
            'coverage': {
                'total_statements': totals.get('num_statements', 0),
                'covered_statements': totals.get('covered_lines', 0),
                'missing_statements': totals.get('missing_lines', 0),
                'coverage_percent': round(totals.get('percent_covered', 0), 2),
                'files': files,
                'generated_at': datetime.now().isoformat()
            }
        })

    except FileNotFoundError:
        return jsonify({
            'success': False,
            'error': '覆盖率数据文件不存在'
        }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_test_runner_bp.route('/history', methods=['GET'])
def get_test_history():
    """
    获取测试历史记录

    Returns:
        {
            "success": true,
            "history": [...]
        }
    """
    try:
        limit = request.args.get('limit', 20, type=int)

        # 获取所有已完成的任务
        with _test_task_lock:
            tasks = list(_test_tasks.values())

        # 按创建时间倒序排序
        tasks.sort(key=lambda x: x['created_time'], reverse=True)

        # 限制数量
        tasks = tasks[:limit]

        return jsonify({
            'success': True,
            'history': tasks,
            'total': len(_test_tasks)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_test_runner_bp.route('/clear-history', methods=['POST'])
def clear_test_history():
    """
    清除测试历史记录

    Returns:
        {
            "success": true,
            "message": "历史记录已清除"
        }
    """
    try:
        with _test_task_lock:
            _test_tasks.clear()

        return jsonify({
            'success': True,
            'message': '历史记录已清除'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_test_runner_bp.route('/quick-info', methods=['GET'])
def get_quick_info():
    """
    获取快速测试信息

    Returns:
        {
            "success": true,
            "info": {
                "total_tests": 252,
                "test_files": 20,
                "coverage_percent": 10.56,
                "last_run": "2025-11-28 09:11"
            }
        }
    """
    try:
        # 统计测试文件
        test_dir = PROJECT_ROOT / 'tests'
        test_files = list(test_dir.rglob('test_*.py'))

        # 读取覆盖率
        coverage_file = PROJECT_ROOT / 'coverage.json'
        coverage_percent = 0.0
        if coverage_file.exists():
            with open(coverage_file, 'r') as f:
                coverage_data = json.load(f)
                coverage_percent = coverage_data.get('totals', {}).get('percent_covered', 0)

        # 获取最后一次运行时间
        coverage_html = PROJECT_ROOT / 'htmlcov' / 'index.html'
        last_run = None
        if coverage_html.exists():
            import re
            with open(coverage_html, 'r', encoding='utf-8') as f:
                content = f.read()
                match = re.search(r'created at ([\d-]+ [\d:]+)', content)
                if match:
                    last_run = match.group(1)

        return jsonify({
            'success': True,
            'info': {
                'total_tests': 252,  # 从之前的统计
                'test_files': len(test_files),
                'coverage_percent': round(coverage_percent, 2),
                'last_run': last_run,
                'test_dir': str(test_dir)
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


__all__ = ['api_test_runner_bp']
