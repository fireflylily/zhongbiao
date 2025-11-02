import json
import time
import uuid
import threading
from flask import Blueprint, request, jsonify, current_app, Response
from ai_tender_system.common.database import get_knowledge_base_db
from ai_tender_system.common.logger import get_module_logger

document_merger_api_bp = Blueprint('document_merger_api', __name__)
logger = get_module_logger("document_merger_api")

def run_merge_task(task_id, project_id, business_doc_path, p2p_doc_path, tech_doc_path):
    """
    A background task that 'merges' documents.
    This is a placeholder and does not perform a real merge.
    """
    db = get_knowledge_base_db()
    logger.info(f"Starting merge task {task_id} for project {project_id}")

    try:
        # 1. Update task status to 'running'
        db.update_task_status(task_id, 'running', 'Merging documents')

        # FAKE MERGE LOGIC: Simulate merging by waiting for a few seconds
        time.sleep(5)

        # In a real implementation, you would merge the documents here
        # and get the path to the merged document.
        merged_document_path = f"/path/to/merged_document_{task_id}.docx"
        index_file_path = f"/path/to/index_file_{task_id}.json"

        # 2. Update task status to 'completed'
        options = {
            "merged_document_path": merged_document_path,
            "index_file_path": index_file_path
        }
        db.update_task_status(task_id, 'completed', 'Merge complete', options=options)
        logger.info(f"Merge task {task_id} completed successfully.")

    except Exception as e:
        logger.error(f"Merge task {task_id} failed: {e}", exc_info=True)
        db.update_task_status(task_id, 'failed', str(e))

def start_merge_task(project_id, business_doc_path, p2p_doc_path, tech_doc_path):
    """
    Starts the background merge task.
    """
    db = get_knowledge_base_db()
    task_id = str(uuid.uuid4())
    
    options = {
        'business_doc_path': business_doc_path,
        'p2p_doc_path': p2p_doc_path,
        'tech_doc_path': tech_doc_path
    }

    db.create_processing_task(
        task_id,
        project_id,
        'document_merge',
        'pending',
        'Waiting to start',
        options=options
    )

    thread = threading.Thread(
        target=run_merge_task,
        args=(task_id, project_id, business_doc_path, p2p_doc_path, tech_doc_path)
    )
    thread.daemon = True
    thread.start()
    
    return task_id

@document_merger_api_bp.route('/api/projects/<int:project_id>/merge-documents', methods=['POST'])
def merge_project_documents(project_id):
    """
    Starts a background task to merge project documents.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON payload"}), 400

    business_doc_path = data.get('business_doc_path')
    p2p_doc_path = data.get('p2p_doc_path')
    tech_doc_path = data.get('tech_doc_path')

    if not all([business_doc_path, p2p_doc_path, tech_doc_path]):
        return jsonify({"error": "Missing one or more document paths"}), 400

    try:
        task_id = start_merge_task(project_id, business_doc_path, p2p_doc_path, tech_doc_path)
        return jsonify({"message": "Merge task started", "task_id": task_id}), 202
    except Exception as e:
        current_app.logger.error(f"Failed to start merge task for project {project_id}: {e}", exc_info=True)
        return jsonify({"error": "Failed to start merge task"}), 500

@document_merger_api_bp.route('/api/projects/<int:project_id>/source-documents', methods=['GET'])
def get_project_source_documents(project_id):
    db = get_knowledge_base_db()
    try:
        # Get project name and company name
        project_data = db.execute_query(
            "SELECT tp.project_name, c.company_name FROM tender_projects tp JOIN companies c ON tp.company_id = c.company_id WHERE tp.project_id = ?",
            (project_id,),
            fetch_one=True
        )
        if not project_data:
            return jsonify({"success": False, "error": f"Project with ID {project_id} not found."} ), 404
        
        project_name = project_data.get('project_name')
        company_name = project_data.get('company_name')

        # Get document paths from the latest tender_processing_tasks for this project
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
        current_app.logger.error(f"Database error retrieving project source documents for {project_id}: {e}", exc_info=True)
        return jsonify({"success": False, "error": "Failed to retrieve project source documents from database."} ), 500


# SSE endpoint to get task status/progress
@document_merger_api_bp.route('/api/merge-status/<task_id>')
def get_merge_status(task_id):
    db = get_knowledge_base_db()

    def generate():
        last_status = {}
        while True:
            task = db.get_processing_task(task_id)
            if task:
                current_status = {
                    "task_id": task['task_id'],
                    "overall_status": task['overall_status'],
                    "current_step": task['current_step'],
                    "progress_percentage": task['progress_percentage'],
                    "merged_document_path": None, # Placeholder for final path
                    "index_file_path": None # Placeholder for final path
                }
                
                # If task is completed, extract final document paths from options
                if task['overall_status'] == 'completed' and task.get('options'):
                    task_options = json.loads(task['options'])
                    current_status['merged_document_path'] = task_options.get('merged_document_path')
                    current_status['index_file_path'] = task_options.get('index_file_path')

                if current_status != last_status:
                    yield f"data: {json.dumps(current_status)}\n\n"
                    last_status = current_status

                if task['overall_status'] in ['completed', 'failed', 'cancelled']:
                    break
            else:
                # Task not found, send a failed status and break
                yield f"data: {json.dumps({'task_id': task_id, 'overall_status': 'failed', 'current_step': '任务不存在', 'progress_percentage': 0})}\\n\n"
                break
            time.sleep(1) # Poll every 1 second

    return Response(generate(), mimetype='text/event-stream')