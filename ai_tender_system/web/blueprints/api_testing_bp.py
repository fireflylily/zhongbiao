#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试状态管理API - 提供测试报告、覆盖率、历史记录等接口

功能：
1. 获取最新测试报告
2. 查看代码覆盖率
3. 运行测试用例
4. 查看测试历史记录
5. 下载测试报告

作者：AI Tender System
日期：2025-11-28
"""

from flask import Blueprint, jsonify, request, send_file, current_app
import subprocess
import json
import os
from pathlib import Path
from datetime import datetime
import sqlite3

api_testing_bp = Blueprint('api_testing', __name__, url_prefix='/api/testing')


# ============================================================================
# 辅助函数
# ============================================================================

def get_test_history_db():
    """获取测试历史数据库连接"""
    db_path = Path(__file__).parent.parent.parent / 'data' / 'test_history.db'
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row

    # 初始化表
    conn.execute('''
        CREATE TABLE IF NOT EXISTS test_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total_tests INTEGER,
            passed_tests INTEGER,
            failed_tests INTEGER,
            skipped_tests INTEGER,
            duration REAL,
            coverage_percent REAL,
            status TEXT,
            error_message TEXT
        )
    ''')
    conn.commit()

    return conn


def parse_coverage_report():
    """解析覆盖率报告"""
    htmlcov_path = Path(__file__).parent.parent.parent.parent / 'htmlcov'

    if not htmlcov_path.exists():
        return None

    # 读取coverage的status.json
    status_file = htmlcov_path / 'status.json'
    if status_file.exists():
        with open(status_file, 'r') as f:
            coverage_data = json.load(f)
            return {
                'total_statements': coverage_data.get('totals', {}).get('num_statements', 0),
                'covered_statements': coverage_data.get('totals', {}).get('covered_statements', 0),
                'coverage_percent': coverage_data.get('totals', {}).get('percent_covered', 0),
                'files': coverage_data.get('files', {})
            }

    return None


def run_backend_tests(project_root, test_path):
    """运行后端Python测试"""
    # 构建测试命令
    cmd = [
        'pytest',
        test_path,
        '-v',
        '--tb=short',
        '--html=test-report.html',
        '--self-contained-html',
        '--cov=ai_tender_system',
        '--cov-report=html',
        '--cov-report=json'
    ]

    # 运行测试
    result = subprocess.run(
        cmd,
        cwd=str(project_root),
        capture_output=True,
        text=True,
        timeout=300
    )

    return parse_test_result(result, project_root, 'backend')


def run_frontend_tests(project_root, data):
    """运行前端Vitest测试"""
    test_module = data.get('test_module', '')  # 可选：指定模块

    frontend_dir = project_root / 'frontend'

    # 构建测试命令
    cmd = ['npm', 'run', 'test:run']

    # 如果指定了模块，添加过滤参数
    if test_module:
        cmd.extend(['--', test_module])

    # 运行前端测试
    result = subprocess.run(
        cmd,
        cwd=str(frontend_dir),
        capture_output=True,
        text=True,
        timeout=120
    )

    return parse_test_result(result, project_root, 'frontend')


def parse_test_result(result, project_root, test_type):
    """解析测试结果（统一处理后端和前端）"""
    output = result.stdout + result.stderr

    if test_type == 'frontend':
        # 解析Vitest输出
        # "Test Files  2 passed (2)"
        # "Tests  11 passed (11)"
        import re

        # 去除ANSI颜色代码
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        clean_output = ansi_escape.sub('', output)

        passed = 0
        failed = 0
        skipped = 0
        total = 0

        # 解析测试数量（Vitest格式：Tests  11 passed (11)）
        test_match = re.search(r'Tests\s+(\d+)\s+passed\s+\((\d+)\)', clean_output)
        if test_match:
            passed = int(test_match.group(1))
            total = int(test_match.group(2))

        failed_match = re.search(r'(\d+)\s+failed', clean_output)
        if failed_match:
            failed = int(failed_match.group(1))
            total += failed

        # 如果没有匹配到，尝试简化的匹配
        if total == 0:
            simple_match = re.search(r'(\d+)\s+passed', clean_output)
            if simple_match:
                passed = int(simple_match.group(1))
                total = passed

        # 前端测试结果
        return jsonify({
            'success': result.returncode == 0,
            'test_type': 'frontend',
            'total_tests': total,
            'passed': passed,
            'failed': failed,
            'skipped': 0,
            'output': output,
            'return_code': result.returncode
        })

    else:
        # 解析pytest输出（原有逻辑）
        passed = output.count(' PASSED')
        failed = output.count(' FAILED')
        skipped = output.count(' SKIPPED')
        total = passed + failed + skipped

        # 解析coverage.json获取覆盖率
        coverage_json_path = project_root / 'coverage.json'
        coverage_percent = 0.0
        if coverage_json_path.exists():
            with open(coverage_json_path, 'r') as f:
                coverage_data = json.load(f)
                coverage_percent = coverage_data.get('totals', {}).get('percent_covered', 0.0)

        # 记录到历史数据库
        conn = get_test_history_db()
        conn.execute('''
            INSERT INTO test_runs
            (total_tests, passed_tests, failed_tests, skipped_tests,
             coverage_percent, status, duration)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            total,
            passed,
            failed,
            skipped,
            coverage_percent,
            'success' if result.returncode == 0 else 'failed',
            0.0
        ))
        conn.commit()
        conn.close()

        return jsonify({
            'success': result.returncode == 0,
            'test_type': 'backend',
            'total_tests': total,
            'passed': passed,
            'failed': failed,
            'skipped': skipped,
            'coverage_percent': coverage_percent,
            'output': output,
            'return_code': result.returncode
        })


def parse_test_report():
    """解析测试报告HTML文件获取测试结果"""
    report_path = Path(__file__).parent.parent.parent.parent / 'test-report.html'

    if not report_path.exists():
        return None

    # 简单解析HTML获取测试统计（实际生产中可以用BeautifulSoup）
    # 这里返回基本信息
    return {
        'report_exists': True,
        'report_path': str(report_path),
        'file_size': report_path.stat().st_size,
        'last_modified': datetime.fromtimestamp(report_path.stat().st_mtime).isoformat()
    }


# ============================================================================
# API端点
# ============================================================================

@api_testing_bp.route('/status', methods=['GET'])
def get_test_status():
    """获取测试状态概览"""
    try:
        # 获取最新测试运行记录
        conn = get_test_history_db()
        cursor = conn.execute(
            'SELECT * FROM test_runs ORDER BY run_time DESC LIMIT 1'
        )
        latest_run = cursor.fetchone()
        conn.close()

        # 获取覆盖率数据
        coverage = parse_coverage_report()

        # 获取测试报告信息
        test_report = parse_test_report()

        return jsonify({
            'success': True,
            'latest_run': dict(latest_run) if latest_run else None,
            'coverage': coverage,
            'test_report': test_report,
            'reports_available': {
                'html_report': test_report is not None,
                'coverage_report': coverage is not None
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_testing_bp.route('/coverage', methods=['GET'])
def get_coverage_details():
    """获取代码覆盖率详情"""
    try:
        coverage = parse_coverage_report()

        if not coverage:
            return jsonify({
                'success': False,
                'message': '覆盖率报告不存在，请先运行测试'
            }), 404

        # 提取关键模块的覆盖率
        modules = {}
        for file_path, file_data in coverage.get('files', {}).items():
            # 只显示ai_tender_system下的文件
            if 'ai_tender_system' in file_path:
                module_name = file_path.split('ai_tender_system/')[-1]
                modules[module_name] = {
                    'statements': file_data.get('summary', {}).get('num_statements', 0),
                    'covered': file_data.get('summary', {}).get('covered_lines', 0),
                    'percent': file_data.get('summary', {}).get('percent_covered', 0)
                }

        return jsonify({
            'success': True,
            'total_coverage': coverage['coverage_percent'],
            'total_statements': coverage['total_statements'],
            'covered_statements': coverage['covered_statements'],
            'modules': modules
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_testing_bp.route('/history', methods=['GET'])
def get_test_history():
    """获取测试历史记录"""
    try:
        limit = request.args.get('limit', 30, type=int)

        conn = get_test_history_db()
        cursor = conn.execute(
            'SELECT * FROM test_runs ORDER BY run_time DESC LIMIT ?',
            (limit,)
        )

        history = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return jsonify({
            'success': True,
            'history': history,
            'count': len(history)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_testing_bp.route('/run', methods=['POST'])
def run_tests():
    """运行测试用例（后端或前端）"""
    try:
        data = request.get_json()
        test_type = data.get('test_type', 'backend')  # backend 或 frontend
        test_path = data.get('test_path', 'tests/unit/')

        # 项目根目录
        project_root = Path(__file__).parent.parent.parent.parent

        # 根据测试类型选择命令
        if test_type == 'frontend':
            return run_frontend_tests(project_root, data)
        else:
            return run_backend_tests(project_root, test_path)

        # 构建测试命令
        cmd = [
            'pytest',
            test_path,
            '-v',
            '--tb=short',
            '--html=test-report.html',
            '--self-contained-html',
            '--cov=ai_tender_system',
            '--cov-report=html',
            '--cov-report=json'
        ]

        # 运行测试
        result = subprocess.run(
            cmd,
            cwd=str(project_root),
            capture_output=True,
            text=True,
            timeout=300  # 5分钟超时
        )

        # 解析coverage.json获取覆盖率
        coverage_json_path = project_root / 'coverage.json'
        coverage_percent = 0.0
        if coverage_json_path.exists():
            with open(coverage_json_path, 'r') as f:
                coverage_data = json.load(f)
                coverage_percent = coverage_data.get('totals', {}).get('percent_covered', 0.0)

        # 解析测试结果（简单解析）
        output = result.stdout + result.stderr
        passed = output.count(' PASSED')
        failed = output.count(' FAILED')
        skipped = output.count(' SKIPPED')
        total = passed + failed + skipped

        # 记录到历史数据库
        conn = get_test_history_db()
        conn.execute('''
            INSERT INTO test_runs
            (total_tests, passed_tests, failed_tests, skipped_tests,
             coverage_percent, status, duration)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            total,
            passed,
            failed,
            skipped,
            coverage_percent,
            'success' if result.returncode == 0 else 'failed',
            0.0  # 可以从输出中解析实际时间
        ))
        conn.commit()
        conn.close()

        return jsonify({
            'success': result.returncode == 0,
            'total_tests': total,
            'passed': passed,
            'failed': failed,
            'skipped': skipped,
            'coverage_percent': coverage_percent,
            'output': output,
            'return_code': result.returncode
        })

    except subprocess.TimeoutExpired:
        return jsonify({
            'success': False,
            'error': '测试运行超时（超过5分钟）'
        }), 500

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_testing_bp.route('/download/report', methods=['GET'])
def download_test_report():
    """下载HTML测试报告"""
    try:
        report_path = Path(__file__).parent.parent.parent.parent / 'test-report.html'

        if not report_path.exists():
            return jsonify({
                'success': False,
                'message': '测试报告不存在'
            }), 404

        return send_file(
            report_path,
            as_attachment=True,
            download_name=f'test-report-{datetime.now().strftime("%Y%m%d-%H%M%S")}.html'
        )

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_testing_bp.route('/download/coverage', methods=['GET'])
def download_coverage_report():
    """下载覆盖率报告（ZIP）"""
    try:
        import zipfile
        import io

        htmlcov_path = Path(__file__).parent.parent.parent.parent / 'htmlcov'

        if not htmlcov_path.exists():
            return jsonify({
                'success': False,
                'message': '覆盖率报告不存在'
            }), 404

        # 创建内存中的ZIP文件
        memory_file = io.BytesIO()
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file_path in htmlcov_path.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(htmlcov_path.parent)
                    zf.write(file_path, arcname)

        memory_file.seek(0)

        return send_file(
            memory_file,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f'coverage-report-{datetime.now().strftime("%Y%m%d-%H%M%S")}.zip'
        )

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_testing_bp.route('/view/report', methods=['GET'])
def view_test_report():
    """查看测试报告（iframe嵌入）"""
    try:
        report_path = Path(__file__).parent.parent.parent.parent / 'test-report.html'

        if not report_path.exists():
            return jsonify({
                'success': False,
                'message': '测试报告不存在'
            }), 404

        return send_file(report_path)

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_testing_bp.route('/view/coverage', methods=['GET'])
def view_coverage_report():
    """查看覆盖率报告（iframe嵌入）"""
    try:
        coverage_path = Path(__file__).parent.parent.parent.parent / 'htmlcov' / 'index.html'

        if not coverage_path.exists():
            return jsonify({
                'success': False,
                'message': '覆盖率报告不存在'
            }), 404

        return send_file(coverage_path)

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# 健康检查
# ============================================================================

@api_testing_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        'success': True,
        'message': '测试管理API运行正常',
        'timestamp': datetime.now().isoformat()
    })
