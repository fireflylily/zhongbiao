#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小程序专用API蓝图
提供微信小程序的所有接口，使用 /api/mp 前缀与 Web 端接口区分

接口列表：
- /api/mp/auth/login                    微信登录
- /api/mp/auth/profile                  更新用户资料
- /api/mp/risk/upload                   上传文件并分析
- /api/mp/risk/status/<id>              查询任务状态
- /api/mp/risk/result/<id>              获取分析结果
- /api/mp/risk/history                  历史任务列表
- /api/mp/risk/delete/<id>              删除任务

V5.0 新增接口：
- /api/mp/risk/upload-response/<id>     上传应答文件 (POST)
- /api/mp/risk/reconcile/<id>           启动双向对账 (POST) / 获取对账结果 (GET)
- /api/mp/risk/export/<id>              导出 Excel 报告 (GET)
"""

import sys
import requests
from pathlib import Path
from functools import wraps
from flask import Blueprint, request, jsonify, g

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from common import get_module_logger, get_config
from common.jwt_utils import generate_jwt_token, verify_jwt_token, TokenExpiredError, TokenInvalidError
from common.database import get_db_connection
from core.storage_service import FileStorageService

# 创建蓝图
api_miniprogram_bp = Blueprint('api_miniprogram', __name__, url_prefix='/api/mp')

# 日志记录器
logger = get_module_logger("web.api_miniprogram")

# 配置
config = get_config()

# 文件存储服务
storage_service = FileStorageService()


# ============================================================
# 鉴权装饰器
# ============================================================

def require_mp_auth(f):
    """
    小程序鉴权装饰器
    从 Authorization header 中提取 JWT token，验证并获取 openid
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')

        if not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': '未提供认证信息'}), 401

        token = auth_header[7:]  # 去掉 "Bearer " 前缀

        try:
            web_config = config.get_web_config()
            secret_key = web_config.get('secret_key', 'default-secret-key')

            payload = verify_jwt_token(token, secret_key)
            g.openid = payload.get('openid')
            g.user_id = payload.get('user_id')

            if not g.openid:
                return jsonify({'success': False, 'message': 'Token 无效'}), 401

        except TokenExpiredError:
            return jsonify({'success': False, 'message': 'Token 已过期，请重新登录'}), 401
        except TokenInvalidError:
            return jsonify({'success': False, 'message': 'Token 无效'}), 401
        except Exception as e:
            logger.error(f"Token 验证失败: {e}")
            return jsonify({'success': False, 'message': '认证失败'}), 401

        return f(*args, **kwargs)

    return decorated


def optional_mp_auth(f):
    """
    可选的小程序鉴权装饰器
    如果提供了 Token 则验证，否则 g.openid 为 None
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        g.openid = None
        g.user_id = None

        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
            try:
                web_config = config.get_web_config()
                secret_key = web_config.get('secret_key', 'default-secret-key')
                payload = verify_jwt_token(token, secret_key)
                g.openid = payload.get('openid')
                g.user_id = payload.get('user_id')
            except Exception:
                pass  # 忽略验证失败

        return f(*args, **kwargs)

    return decorated


# ============================================================
# 认证相关接口
# ============================================================

@api_miniprogram_bp.route('/auth/login', methods=['POST'])
def wechat_login():
    """
    微信登录

    POST: { "code": "wx.login获取的code" }

    Returns:
        {
            "success": true,
            "data": {
                "token": "jwt_token",
                "openid": "xxx",
                "is_new_user": false
            }
        }
    """
    try:
        data = request.get_json()
        code = data.get('code')

        if not code:
            return jsonify({'success': False, 'message': '缺少 code 参数'}), 400

        # 获取微信配置
        wechat_config = config.get_wechat_config() if hasattr(config, 'get_wechat_config') else {}
        appid = wechat_config.get('appid', '')
        secret = wechat_config.get('secret', '')

        if not appid or not secret:
            # 开发模式：使用 mock openid
            logger.warning("微信配置未设置，使用开发模式")
            openid = f"dev_{code[:16]}"
            session_key = "dev_session_key"
        else:
            # 生产模式：调用微信 API
            wx_res = requests.get(
                'https://api.weixin.qq.com/sns/jscode2session',
                params={
                    'appid': appid,
                    'secret': secret,
                    'js_code': code,
                    'grant_type': 'authorization_code'
                },
                timeout=10
            )

            wx_data = wx_res.json()

            if 'errcode' in wx_data and wx_data['errcode'] != 0:
                logger.error(f"微信登录失败: {wx_data}")
                return jsonify({
                    'success': False,
                    'message': f"微信登录失败: {wx_data.get('errmsg', '未知错误')}"
                }), 400

            openid = wx_data.get('openid')
            session_key = wx_data.get('session_key')

            if not openid:
                return jsonify({'success': False, 'message': '获取 openid 失败'}), 400

        # 查找或创建用户
        user, is_new_user = _find_or_create_wechat_user(openid, session_key)

        # 生成 JWT token
        web_config = config.get_web_config()
        secret_key = web_config.get('secret_key', 'default-secret-key')

        token = generate_jwt_token({
            'user_id': user.get('user_id'),
            'openid': openid,
            'source': 'miniprogram'
        }, secret_key, expires_in=86400 * 7)  # 7天有效

        logger.info(f"微信用户登录成功: openid={openid[:8]}...")

        return jsonify({
            'success': True,
            'data': {
                'token': token,
                'openid': openid,
                'user_id': user.get('user_id'),
                'nickname': user.get('nickname', ''),
                'is_new_user': is_new_user
            }
        })

    except Exception as e:
        logger.error(f"微信登录异常: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@api_miniprogram_bp.route('/auth/profile', methods=['POST'])
@require_mp_auth
def update_profile():
    """
    更新用户资料

    POST: {
        "nickname": "用户昵称",
        "avatar_url": "头像URL"
    }
    """
    try:
        data = request.get_json()
        nickname = data.get('nickname', '')
        avatar_url = data.get('avatar_url', '')

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users
                SET nickname = ?, avatar_url = ?, updated_at = CURRENT_TIMESTAMP
                WHERE openid = ?
            """, (nickname, avatar_url, g.openid))
            conn.commit()

        return jsonify({'success': True, 'message': '更新成功'})

    except Exception as e:
        logger.error(f"更新用户资料失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


# ============================================================
# 风险分析相关接口
# ============================================================

@api_miniprogram_bp.route('/risk/upload', methods=['POST'])
@require_mp_auth
def upload_and_analyze():
    """
    上传文件并创建分析任务

    POST: multipart/form-data
    - file: 招标文档文件 (PDF/Word)
    - model: AI模型名称 (可选，默认 deepseek-v3)

    Returns:
        {
            "success": true,
            "data": {
                "task_id": "uuid-xxx",
                "status": "pending",
                "message": "任务已创建"
            }
        }
    """
    try:
        # 验证文件
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': '未上传文件'}), 400

        file = request.files['file']

        # 获取原始文件名：优先从 formData 获取，否则用 file.filename
        # 微信小程序 wx.uploadFile 的 filePath 是临时路径，file.filename 可能是 UUID
        original_filename = request.form.get('filename') or file.filename
        if not original_filename:
            return jsonify({'success': False, 'message': '文件名为空'}), 400

        # 检查文件类型
        allowed_extensions = {'pdf', 'doc', 'docx'}
        ext = original_filename.rsplit('.', 1)[-1].lower() if '.' in original_filename else ''
        if ext not in allowed_extensions:
            return jsonify({'success': False, 'message': f'不支持的文件格式: {ext}'}), 400

        # 检查文件大小（限制 20MB）
        file.seek(0, 2)  # 移到文件末尾
        file_size = file.tell()
        file.seek(0)  # 移回开头

        if file_size > 20 * 1024 * 1024:
            return jsonify({'success': False, 'message': '文件大小不能超过 20MB'}), 400

        # 存储文件
        file_metadata = storage_service.store_file(
            file_obj=file,
            original_name=original_filename,
            category='risk_analysis',
            business_type='bid_risk_check'
        )

        # 获取模型配置
        model_name = request.form.get('model', 'deepseek-v3')

        # 创建任务
        from modules.risk_analyzer import RiskTaskManager
        task_manager = RiskTaskManager()

        task_id = task_manager.create_task(
            file_id=file_metadata.file_id,
            file_path=file_metadata.file_path,
            original_filename=file_metadata.original_name,
            openid=g.openid,
            user_id=g.user_id,
            file_size=file_metadata.file_size,
            model_name=model_name
        )

        # 异步启动分析
        task_manager.start_analysis(task_id)

        logger.info(f"风险分析任务已创建: {task_id}, 文件: {original_filename}")

        return jsonify({
            'success': True,
            'data': {
                'task_id': task_id,
                'status': 'pending',
                'message': '任务已创建，正在分析中'
            }
        })

    except Exception as e:
        logger.error(f"创建风险分析任务失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@api_miniprogram_bp.route('/risk/status/<task_id>', methods=['GET'])
@require_mp_auth
def get_task_status(task_id: str):
    """
    查询任务状态（支持边分析边显示）

    Returns:
        {
            "success": true,
            "data": {
                "task_id": "xxx",
                "status": "analyzing",
                "progress": 45,
                "current_step": "正在分析第3/5块...",
                "risk_items": [...],  // 分析中也返回已发现的风险项
                "found_count": 5      // 已发现的风险项数量
            }
        }
    """
    try:
        from modules.risk_analyzer import RiskTaskManager
        import json

        task_manager = RiskTaskManager()

        task = task_manager.get_task_by_openid(task_id, g.openid)
        if not task:
            return jsonify({'success': False, 'message': '任务不存在或无权访问'}), 404

        # 解析已发现的风险项（即使还在分析中）
        risk_items = []
        if task.get('risk_items'):
            try:
                risk_items = json.loads(task['risk_items'])
            except json.JSONDecodeError:
                risk_items = []

        return jsonify({
            'success': True,
            'data': {
                'task_id': task_id,
                'status': task['status'],
                'progress': task['progress'],
                'current_step': task.get('current_step', ''),
                'error_message': task.get('error_message', ''),
                'risk_items': risk_items,
                'found_count': len(risk_items)
            }
        })

    except Exception as e:
        logger.error(f"查询任务状态失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@api_miniprogram_bp.route('/risk/result/<task_id>', methods=['GET'])
@require_mp_auth
def get_task_result(task_id: str):
    """
    获取分析结果

    Returns:
        {
            "success": true,
            "data": {
                "task_id": "xxx",
                "risk_items": [...],
                "summary": "...",
                "risk_score": 75,
                "statistics": {...}
            }
        }
    """
    try:
        from modules.risk_analyzer import RiskTaskManager
        task_manager = RiskTaskManager()

        task = task_manager.get_task_by_openid(task_id, g.openid)
        if not task:
            return jsonify({'success': False, 'message': '任务不存在或无权访问'}), 404

        if task['status'] != 'completed':
            return jsonify({
                'success': False,
                'message': f'任务尚未完成，当前状态: {task["status"]}'
            }), 400

        # 获取完整结果（包含解析后的 risk_items）
        result = task_manager.get_task_result(task_id)

        # 计算统计信息
        risk_items = result.get('risk_items', [])
        statistics = {
            'total_items': len(risk_items),
            'high_risk_count': sum(1 for item in risk_items if item.get('risk_level') == 'high'),
            'medium_risk_count': sum(1 for item in risk_items if item.get('risk_level') == 'medium'),
            'low_risk_count': sum(1 for item in risk_items if item.get('risk_level') == 'low')
        }

        return jsonify({
            'success': True,
            'data': {
                'task_id': task_id,
                'filename': result.get('original_filename', ''),
                'risk_items': risk_items,
                'summary': result.get('summary', ''),
                'risk_score': result.get('risk_score', 0),
                'statistics': statistics,
                'model_name': result.get('model_name', ''),
                'analysis_time': result.get('analysis_time', 0),
                'completed_at': result.get('completed_at', '')
            }
        })

    except Exception as e:
        logger.error(f"获取分析结果失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@api_miniprogram_bp.route('/risk/history', methods=['GET'])
@require_mp_auth
def list_tasks():
    """
    列表查询任务（按 openid 筛选）

    Query params:
    - page: 页码 (默认 1)
    - page_size: 每页数量 (默认 10)
    - status: 状态筛选 (可选)
    """
    try:
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 10, type=int)
        status = request.args.get('status')

        # 限制 page_size
        page_size = min(page_size, 50)

        from modules.risk_analyzer import RiskTaskManager
        task_manager = RiskTaskManager()

        result = task_manager.list_tasks(
            openid=g.openid,
            status=status,
            page=page,
            page_size=page_size
        )

        return jsonify({
            'success': True,
            'data': result
        })

    except Exception as e:
        logger.error(f"列表查询任务失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@api_miniprogram_bp.route('/risk/delete/<task_id>', methods=['DELETE'])
@require_mp_auth
def delete_task(task_id: str):
    """删除任务"""
    try:
        from modules.risk_analyzer import RiskTaskManager
        task_manager = RiskTaskManager()

        success = task_manager.delete_task(task_id, openid=g.openid)

        if success:
            return jsonify({'success': True, 'message': '删除成功'})
        else:
            return jsonify({'success': False, 'message': '任务不存在或无权删除'}), 404

    except Exception as e:
        logger.error(f"删除任务失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


# ============================================================
# 应答文件上传与双向对账接口 (5.0 新增)
# ============================================================

@api_miniprogram_bp.route('/risk/upload-response/<task_id>', methods=['POST'])
@require_mp_auth
def upload_response_file(task_id: str):
    """
    上传应答文件（用于双向对账）

    POST: multipart/form-data
    - file: 应答文档文件 (PDF/Word)

    Returns:
        {
            "success": true,
            "data": {
                "task_id": "uuid-xxx",
                "response_file_path": "...",
                "message": "应答文件上传成功，可启动对账"
            }
        }
    """
    try:
        from modules.risk_analyzer import RiskTaskManager
        task_manager = RiskTaskManager()

        # 验证任务存在且属于当前用户
        task = task_manager.get_task_by_openid(task_id, g.openid)
        if not task:
            return jsonify({'success': False, 'message': '任务不存在或无权访问'}), 404

        # 验证任务已完成分析
        if task['status'] != 'completed':
            return jsonify({
                'success': False,
                'message': f'请先完成招标文件分析，当前状态: {task["status"]}'
            }), 400

        # 验证文件
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': '未上传文件'}), 400

        file = request.files['file']
        original_filename = request.form.get('filename') or file.filename

        if not original_filename:
            return jsonify({'success': False, 'message': '文件名为空'}), 400

        # 检查文件类型
        allowed_extensions = {'pdf', 'doc', 'docx'}
        ext = original_filename.rsplit('.', 1)[-1].lower() if '.' in original_filename else ''
        if ext not in allowed_extensions:
            return jsonify({'success': False, 'message': f'不支持的文件格式: {ext}'}), 400

        # 检查文件大小（限制 20MB）
        file.seek(0, 2)
        file_size = file.tell()
        file.seek(0)

        if file_size > 20 * 1024 * 1024:
            return jsonify({'success': False, 'message': '文件大小不能超过 20MB'}), 400

        # 存储文件
        file_metadata = storage_service.store_file(
            file_obj=file,
            original_name=original_filename,
            category='risk_analysis',
            business_type='response_file'
        )

        # 更新任务，保存应答文件信息
        task_manager.update_task(
            task_id,
            response_file_path=file_metadata.file_path,
            response_file_name=file_metadata.original_name,
            analysis_mode='bid_response_reconcile'
        )

        logger.info(f"应答文件上传成功: task_id={task_id}, 文件: {original_filename}")

        return jsonify({
            'success': True,
            'data': {
                'task_id': task_id,
                'response_file_path': file_metadata.file_path,
                'response_file_name': original_filename,
                'message': '应答文件上传成功，可启动对账'
            }
        })

    except Exception as e:
        logger.error(f"上传应答文件失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@api_miniprogram_bp.route('/risk/reconcile/<task_id>', methods=['POST'])
@require_mp_auth
def start_reconcile(task_id: str):
    """
    启动双向对账

    POST: {}  （无需参数，使用已上传的应答文件）

    Returns:
        {
            "success": true,
            "data": {
                "task_id": "xxx",
                "status": "reconciling",
                "message": "对账任务已启动"
            }
        }
    """
    try:
        from modules.risk_analyzer import RiskTaskManager
        task_manager = RiskTaskManager()

        # 验证任务
        task = task_manager.get_task_by_openid(task_id, g.openid)
        if not task:
            return jsonify({'success': False, 'message': '任务不存在或无权访问'}), 404

        # 验证分析已完成
        if task['status'] not in ['completed', 'reconcile_completed']:
            return jsonify({
                'success': False,
                'message': f'请先完成招标文件分析，当前状态: {task["status"]}'
            }), 400

        # 验证应答文件已上传
        if not task.get('response_file_path'):
            return jsonify({
                'success': False,
                'message': '请先上传应答文件'
            }), 400

        # 启动对账任务
        success = task_manager.start_reconcile(task_id)

        if success:
            return jsonify({
                'success': True,
                'data': {
                    'task_id': task_id,
                    'status': 'reconciling',
                    'message': '对账任务已启动'
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': '启动对账失败'
            }), 500

    except Exception as e:
        logger.error(f"启动对账失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@api_miniprogram_bp.route('/risk/reconcile/<task_id>', methods=['GET'])
@require_mp_auth
def get_reconcile_result(task_id: str):
    """
    获取对账结果

    Returns:
        {
            "success": true,
            "data": {
                "task_id": "xxx",
                "status": "reconcile_completed",
                "reconcile_summary": {
                    "total": 10,
                    "compliant": 6,
                    "non_compliant": 2,
                    "partial": 2
                },
                "risk_items": [...],  // 包含合规状态的风险项
                "reconcile_results": [...] // 详细对账结果
            }
        }
    """
    try:
        from modules.risk_analyzer import RiskTaskManager
        import json

        task_manager = RiskTaskManager()

        task = task_manager.get_task_by_openid(task_id, g.openid)
        if not task:
            return jsonify({'success': False, 'message': '任务不存在或无权访问'}), 404

        # 获取完整结果
        result = task_manager.get_task_result(task_id)

        # 解析对账结果
        reconcile_results = []
        if result.get('reconcile_results'):
            try:
                reconcile_results = json.loads(result['reconcile_results'])
            except json.JSONDecodeError:
                reconcile_results = []

        # 计算对账汇总
        reconcile_summary = {
            'total': len(reconcile_results),
            'compliant': sum(1 for r in reconcile_results if r.get('compliance_status') == 'compliant'),
            'non_compliant': sum(1 for r in reconcile_results if r.get('compliance_status') == 'non_compliant'),
            'partial': sum(1 for r in reconcile_results if r.get('compliance_status') == 'partial'),
            'unknown': sum(1 for r in reconcile_results if r.get('compliance_status') == 'unknown')
        }

        return jsonify({
            'success': True,
            'data': {
                'task_id': task_id,
                'status': result.get('status', 'unknown'),
                'reconcile_progress': result.get('reconcile_progress', 0),
                'reconcile_step': result.get('reconcile_step', ''),
                'reconcile_summary': reconcile_summary,
                'risk_items': result.get('risk_items', []),
                'reconcile_results': reconcile_results,
                'response_file_name': result.get('response_file_name', '')
            }
        })

    except Exception as e:
        logger.error(f"获取对账结果失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@api_miniprogram_bp.route('/risk/export/<task_id>', methods=['GET'])
@require_mp_auth
def export_excel(task_id: str):
    """
    导出分析结果为 Excel 文件

    Query params:
    - include_reconcile: 是否包含对账结果 (默认 true)

    Returns:
        Excel 文件下载
    """
    try:
        from flask import send_file
        from modules.risk_analyzer import RiskTaskManager
        from modules.risk_analyzer.excel_exporter import ExcelExporterV5
        import json
        import tempfile
        import os

        task_manager = RiskTaskManager()

        # 验证任务
        task = task_manager.get_task_by_openid(task_id, g.openid)
        if not task:
            return jsonify({'success': False, 'message': '任务不存在或无权访问'}), 404

        if task['status'] not in ['completed', 'reconcile_completed']:
            return jsonify({
                'success': False,
                'message': f'任务尚未完成，当前状态: {task["status"]}'
            }), 400

        # 获取完整结果
        result = task_manager.get_task_result(task_id)

        # 解析风险项
        risk_items = result.get('risk_items', [])

        # 解析对账结果
        reconcile_results = []
        if result.get('reconcile_results'):
            try:
                reconcile_results = json.loads(result['reconcile_results'])
            except json.JSONDecodeError:
                pass

        include_reconcile = request.args.get('include_reconcile', 'true').lower() == 'true'

        # 生成 Excel
        exporter = ExcelExporterV5()

        # 创建临时文件
        fd, temp_path = tempfile.mkstemp(suffix='.xlsx')
        os.close(fd)

        try:
            exporter.export(
                risk_items=risk_items,
                output_path=temp_path,
                project_name=result.get('original_filename', '招标分析报告'),
                summary=result.get('summary', ''),
                reconcile_results=reconcile_results if include_reconcile else None
            )

            # 设置下载文件名
            safe_filename = result.get('original_filename', '分析报告')
            safe_filename = safe_filename.rsplit('.', 1)[0] if '.' in safe_filename else safe_filename
            download_name = f"{safe_filename}_风险分析报告.xlsx"

            return send_file(
                temp_path,
                as_attachment=True,
                download_name=download_name,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

        finally:
            # 延迟删除临时文件（send_file 完成后）
            # 注意：Flask send_file 在发送后会自动处理
            pass

    except Exception as e:
        logger.error(f"导出 Excel 失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


# ============================================================
# 辅助函数
# ============================================================

def _find_or_create_wechat_user(openid: str, session_key: str = None):
    """
    查找或创建微信用户

    Returns:
        (user_dict, is_new_user)
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # 查找现有用户
        cursor.execute("""
            SELECT user_id, username, openid, nickname, avatar_url
            FROM users
            WHERE openid = ?
        """, (openid,))

        row = cursor.fetchone()

        if row:
            # 更新 session_key
            if session_key:
                cursor.execute("""
                    UPDATE users
                    SET wechat_session_key = ?, last_login = CURRENT_TIMESTAMP
                    WHERE openid = ?
                """, (session_key, openid))
                conn.commit()

            return dict(row), False

        # 创建新用户
        cursor.execute("""
            INSERT INTO users (
                username, openid, wechat_session_key,
                role_id, is_active, created_at
            ) VALUES (?, ?, ?, 1, 1, CURRENT_TIMESTAMP)
        """, (
            f"wx_{openid[:8]}",  # 临时用户名
            openid,
            session_key
        ))
        conn.commit()

        user_id = cursor.lastrowid

        return {
            'user_id': user_id,
            'openid': openid,
            'nickname': ''
        }, True


__all__ = ['api_miniprogram_bp']
