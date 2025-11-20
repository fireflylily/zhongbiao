import json
import time
import threading
import os
from flask import Blueprint, request, jsonify, current_app, Response
from ai_tender_system.common.database import get_knowledge_base_db
from ai_tender_system.common.logger import get_module_logger
from ai_tender_system.modules.document_merger.merger_service import DocumentMergerService
from ai_tender_system.common.config import Config

document_merger_api_bp = Blueprint('document_merger_api', __name__)
logger = get_module_logger("document_merger_api")


def run_merge_task(project_id, file_paths, config):
    """
    后台任务：执行文档整合
    """
    db = get_knowledge_base_db()
    logger.info(f"Starting merge task for project {project_id}")

    try:
        # 1. 更新任务状态为running
        db.update_processing_task(project_id, overall_status='running',
                                 current_step='开始文档整合', progress_percentage=0)

        # 2. 创建整合服务
        merger_service = DocumentMergerService()

        # 3. 设置输出目录
        config_obj = Config()
        output_dir = str(config_obj.output_dir)
        os.makedirs(output_dir, exist_ok=True)

        logger.info(f"输出目录: {output_dir}")

        # 4. 进度回调函数
        def progress_callback(percent, message):
            db.update_processing_task(project_id, overall_status='running',
                                     current_step=message, progress_percentage=percent)

        # 5. 执行整合
        result = merger_service.merge_documents_v2(
            project_id=project_id,
            file_paths=file_paths,
            config=config,
            output_dir=output_dir,
            progress_callback=progress_callback
        )

        # 6. 更新任务状态为completed
        # 获取文件大小
        file_size = 0
        try:
            if os.path.exists(result["docx_path"]):
                file_size = os.path.getsize(result["docx_path"])
        except:
            pass

        # 将结果存储到options字段
        options = {
            "merged_document_path": result["docx_path"],
            "file_size": file_size,
            "stats": result["stats"]
        }

        # 需要创建或更新tender_processing_tasks表的options字段
        # 先检查任务是否存在
        existing_task = db.get_processing_task(project_id)

        if existing_task:
            # 更新现有任务
            db.update_processing_task(
                project_id,
                overall_status='completed',
                current_step='Merge complete',
                progress_percentage=100
            )

            # 单独更新options字段（因为update_processing_task不支持options参数）
            db.execute_query(
                "UPDATE tender_processing_tasks SET options = ? WHERE project_id = ?",
                (json.dumps(options, ensure_ascii=False), project_id)
            )
        else:
            # 创建新任务
            db.create_processing_task(project_id, pipeline_config=None, options=options)
            db.update_processing_task(project_id, overall_status='completed',
                                     current_step='Merge complete', progress_percentage=100)

        logger.info(f"Merge task for project {project_id} completed successfully.")

    except Exception as e:
        logger.error(f"Merge task for project {project_id} failed: {e}", exc_info=True)
        db.update_processing_task(project_id, overall_status='failed',
                                 current_step=str(e), progress_percentage=0)


def start_merge_task(project_id, file_paths, config):
    """
    启动后台整合任务
    """
    db = get_knowledge_base_db()

    # 检查任务是否存在，不存在则创建
    existing_task = db.get_processing_task(project_id)

    if not existing_task:
        # 创建新任务
        db.create_processing_task(
            project_id,
            pipeline_config=None,
            options={'file_paths': file_paths, 'config': config}
        )
    else:
        # 更新现有任务为pending状态
        db.update_processing_task(
            project_id,
            overall_status='pending',
            current_step='Waiting to start',
            progress_percentage=0
        )

    # 启动后台线程
    thread = threading.Thread(
        target=run_merge_task,
        args=(project_id, file_paths, config)
    )
    thread.daemon = True
    thread.start()

    return project_id  # 返回project_id作为任务标识


@document_merger_api_bp.route('/api/projects/<int:project_id>/merge-config', methods=['GET'])
def get_merge_config(project_id):
    """
    获取项目的整合配置和文件状态
    """
    db = get_knowledge_base_db()
    try:
        # 获取项目信息
        project_data = db.execute_query(
            "SELECT project_name, step1_data, index_requirement FROM tender_projects WHERE project_id = ?",
            (project_id,),
            fetch_one=True
        )

        if not project_data:
            return jsonify({"success": False, "error": "Project not found"}), 404

        step1_data = {}
        if project_data.get('step1_data'):
            try:
                step1_data = json.loads(project_data['step1_data'])
            except:
                pass

        # 解析索引要求
        index_requirement = {"required": False, "type": "none"}
        if project_data.get('index_requirement'):
            try:
                index_requirement = json.loads(project_data['index_requirement'])
            except:
                pass

        # 构建文件信息
        files = {}

        # 商务应答文件
        if step1_data.get('business_response_file'):
            br_file = step1_data['business_response_file']
            files['business'] = {
                "status": "ready",
                "file_path": br_file.get('file_path'),
                "file_name": br_file.get('file_name'),
                "file_size": br_file.get('file_size', 0)
            }

        # 点对点应答文件
        if step1_data.get('technical_point_to_point_file'):
            p2p_file = step1_data['technical_point_to_point_file']
            files['p2p'] = {
                "status": "ready",
                "file_path": p2p_file.get('file_path'),
                "file_name": p2p_file.get('file_name'),
                "file_size": p2p_file.get('file_size', 0)
            }

        # 技术方案文件
        if step1_data.get('technical_proposal_file'):
            tech_file = step1_data['technical_proposal_file']
            files['tech'] = {
                "status": "ready",
                "file_path": tech_file.get('file_path'),
                "file_name": tech_file.get('file_name'),
                "file_size": tech_file.get('file_size', 0)
            }

        # 默认配置
        default_config = {
            "include_p2p": 'p2p' in files,
            "doc_order": ["business", "p2p", "tech"] if 'p2p' in files else ["business", "tech"],
            "generate_toc": True,
            "remove_blanks": True,
            "unify_styles": True,
            "add_section_breaks": True,
            "index_config": index_requirement,
            "output_filename": f"{project_data.get('project_name', '项目')}_最终标书"
        }

        return jsonify({
            "success": True,
            "data": {
                "files": files,
                "default_config": default_config,
                "index_requirement": index_requirement
            }
        })

    except Exception as e:
        logger.error(f"Failed to get merge config for project {project_id}: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@document_merger_api_bp.route('/api/projects/<int:project_id>/merge-documents', methods=['POST'])
def merge_project_documents(project_id):
    """
    启动文档整合任务
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON payload"}), 400

    file_paths = data.get('file_paths', {})
    config = data.get('config', {})

    logger.info(f"收到整合请求 - project_id: {project_id}, file_paths: {file_paths.keys()}, config: {config.keys()}")

    # 验证必需的文件
    if not file_paths.get('business'):
        return jsonify({"error": "Business response file is required"}), 400

    if not file_paths.get('tech'):
        return jsonify({"error": "Technical proposal file is required"}), 400

    try:
        task_id = start_merge_task(project_id, file_paths, config)
        return jsonify({
            "success": True,
            "message": "Merge task started",
            "task_id": task_id  # 实际上是project_id
        }), 202
    except Exception as e:
        logger.error(f"Failed to start merge task for project {project_id}: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@document_merger_api_bp.route('/api/projects/<int:project_id>/source-documents', methods=['GET'])
def get_project_source_documents(project_id):
    """获取项目的源文档列表"""
    db = get_knowledge_base_db()
    try:
        # 获取项目名称和公司名称
        project_data = db.execute_query(
            "SELECT tp.project_name, c.company_name FROM tender_projects tp JOIN companies c ON tp.company_id = c.company_id WHERE tp.project_id = ?",
            (project_id,),
            fetch_one=True
        )
        if not project_data:
            return jsonify({"success": False, "error": f"Project with ID {project_id} not found."}), 404

        project_name = project_data.get('project_name')
        company_name = project_data.get('company_name')

        # 获取文档路径from tender_processing_tasks
        task_data = db.execute_query(
            "SELECT options FROM tender_processing_tasks WHERE project_id = ? ORDER BY created_at DESC LIMIT 1",
            (project_id,),
            fetch_one=True
        )

        business_doc_path = None
        p2p_doc_path = None
        tech_doc_path = None

        if task_data and task_data.get('options'):
            task_options = json.loads(task_data['options'])
            business_doc_path = task_options.get('business_response_path')
            p2p_doc_path = task_options.get('p2p_response_path')
            tech_doc_path = task_options.get('tech_solution_path')

        return jsonify({
            "success": True,
            "data": {
                "project_name": project_name,
                "company_name": company_name,
                "business_doc_path": business_doc_path,
                "p2p_doc_path": p2p_doc_path,
                "tech_doc_path": tech_doc_path
            }
        }), 200

    except Exception as e:
        logger.error(f"Database error retrieving project source documents for {project_id}: {e}", exc_info=True)
        return jsonify({"success": False, "error": "Failed to retrieve project source documents from database."}), 500


# SSE endpoint to get task status/progress
@document_merger_api_bp.route('/api/merge-status/<int:project_id>')
def get_merge_status(project_id):
    """
    获取整合任务的实时进度（SSE流）
    使用project_id而不是task_id
    """
    db = get_knowledge_base_db()

    def generate():
        last_status = {}
        max_iterations = 300  # 最多5分钟
        iterations = 0

        while iterations < max_iterations:
            iterations += 1

            task = db.get_processing_task(project_id)
            if task:
                current_status = {
                    "project_id": project_id,
                    "overall_status": task.get('overall_status', 'pending'),
                    "current_step": task.get('current_step', ''),
                    "progress_percentage": task.get('progress_percentage', 0),
                    "merged_document_path": None,
                    "stats": None
                }

                # 如果任务完成，提取最终文档路径和统计信息
                if task.get('overall_status') == 'completed' and task.get('options'):
                    try:
                        task_options = json.loads(task['options'])
                        current_status['merged_document_path'] = task_options.get('merged_document_path')
                        current_status['stats'] = task_options.get('stats')
                        current_status['options'] = task_options  # 完整的options
                    except:
                        pass

                # 只在状态变化时发送
                if current_status != last_status:
                    yield f"data: {json.dumps(current_status, ensure_ascii=False)}\n\n"
                    last_status = current_status

                # 如果任务完成或失败，停止监听
                if task.get('overall_status') in ['completed', 'failed', 'cancelled']:
                    break
            else:
                # 任务不存在，发送失败状态
                yield f"data: {json.dumps({'project_id': project_id, 'overall_status': 'failed', 'current_step': '任务不存在', 'progress_percentage': 0}, ensure_ascii=False)}\n\n"
                break

            time.sleep(1)  # 每秒轮询一次

    return Response(generate(), mimetype='text/event-stream')
