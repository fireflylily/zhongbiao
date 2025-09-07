#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI标书点对点应答系统 - Web界面
"""

import os
import logging
import json
import hashlib
import base64
from datetime import datetime
from flask import Flask, render_template, request, send_file, flash, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
from enhanced_inline_reply import EnhancedInlineReplyProcessor
import tempfile
import shutil
import sys
from pathlib import Path
from web_config import get_default_api_key, get_api_config, get_web_config

# 添加招标信息提取模块路径
tender_info_path = str(Path(__file__).parent.parent.parent / "1.读取信息")
sys.path.insert(0, tender_info_path)

try:
    from read_info import TenderInfoExtractor
    TENDER_INFO_AVAILABLE = True
except ImportError as e:
    print(f"警告：招标信息提取模块未能加载: {e}")
    TENDER_INFO_AVAILABLE = False

# 添加技术方案模块路径
tech_proposal_path = str(Path(__file__).parent.parent / "技术方案" / "TenderGenerator")
sys.path.insert(0, tech_proposal_path)

try:
    from main import TenderGenerator
    TECH_PROPOSAL_AVAILABLE = True
except ImportError as e:
    print(f"警告：技术方案模块未能加载: {e}")
    TECH_PROPOSAL_AVAILABLE = False

app = Flask(__name__)
app.secret_key = 'ai_tender_response_system_2025'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# 全局进度追踪
processing_status = {}

# 配置上传文件夹
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
TECH_OUTPUT_FOLDER = 'tech_outputs'
ALLOWED_EXTENSIONS = {'docx', 'doc'}
TECH_ALLOWED_EXTENSIONS = {'docx', 'doc', 'pdf'}
TENDER_INFO_ALLOWED_EXTENSIONS = {'docx', 'doc', 'txt', 'pdf'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(TECH_OUTPUT_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['TECH_OUTPUT_FOLDER'] = TECH_OUTPUT_FOLDER

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def allowed_file(filename):
    """检查文件类型是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_tech_file(filename):
    """检查技术方案文件类型是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in TECH_ALLOWED_EXTENSIONS

def allowed_tender_info_file(filename):
    """检查招标信息提取文件类型是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in TENDER_INFO_ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """主页"""
    default_api_key = get_default_api_key()
    return render_template('index.html', default_api_key=default_api_key)

@app.route('/debug')
def debug_upload():
    """调试上传页面"""
    return send_file('test_upload_debug.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """处理文件上传"""
    upload_path = None
    try:
        logger.info("开始处理文件上传请求")
        
        if 'file' not in request.files:
            logger.warning("请求中未包含文件")
            return jsonify({'error': '没有选择文件'}), 400
        
        file = request.files['file']
        api_key = request.form.get('api_key', '').strip()
        
        if file.filename == '':
            logger.warning("文件名为空")
            return jsonify({'error': '没有选择文件'}), 400
        
        if not allowed_file(file.filename):
            logger.warning(f"不支持的文件类型: {file.filename}")
            return jsonify({'error': '不支持的文件类型，请上传.docx或.doc文件'}), 400
            
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_filename = f"{timestamp}_{filename}"
        
        # 保存上传的文件
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        logger.info(f"保存文件到: {upload_path}")
        file.save(upload_path)
        
        # 检查文件大小
        file_size = os.path.getsize(upload_path)
        logger.info(f"文件大小: {file_size / 1024 / 1024:.2f} MB")
        
        if file_size > 50 * 1024 * 1024:  # 50MB
            os.remove(upload_path)
            return jsonify({'error': '文件过大，请上传小于50MB的文件'}), 400
        
        # 处理文档
        logger.info("开始初始化文档处理器")
        processor = EnhancedInlineReplyProcessor(api_key=api_key)
        
        # 生成输出文件名
        base_name = os.path.splitext(filename)[0]
        output_filename = f"{base_name}-AI应答-{timestamp}.docx"
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        
        logger.info(f"开始处理文档: {filename}")
        
        # 执行处理
        result_file = processor.process_document_enhanced(upload_path, output_path)
        
        logger.info(f"文档处理完成: {result_file}")
        
        # 清理上传的临时文件
        if upload_path and os.path.exists(upload_path):
            os.remove(upload_path)
            logger.info("临时文件已清理")
        
        return jsonify({
            'success': True,
            'message': '文档处理完成',
            'filename': output_filename,
            'download_url': url_for('download_file', filename=output_filename)
        })
            
    except Exception as e:
        logger.error(f"文件处理失败: {e}", exc_info=True)
        
        # 清理临时文件
        if upload_path and os.path.exists(upload_path):
            try:
                os.remove(upload_path)
                logger.info("清理临时文件成功")
            except Exception as cleanup_error:
                logger.error(f"清理临时文件失败: {cleanup_error}")
        
        # 返回详细错误信息
        error_message = str(e)
        if "python-docx" in error_message:
            error_message = "文档格式错误，请确保上传的是有效的Word文档"
        elif "Memory" in error_message or "内存" in error_message:
            error_message = "文档过大导致内存不足，请尝试上传更小的文件"
        elif "API" in error_message:
            error_message = f"AI服务调用失败: {error_message}"
        
        return jsonify({'error': f'处理失败: {error_message}'}), 500

@app.route('/status/<task_id>')
def get_status(task_id):
    """获取处理状态"""
    status = processing_status.get(task_id, {
        'status': 'unknown',
        'message': '未知任务',
        'progress': 0
    })
    return jsonify(status)

@app.route('/download/<filename>')
def download_file(filename):
    """下载处理后的文件"""
    try:
        # 安全性检查：防止路径遍历攻击
        if '..' in filename or '/' in filename or '\\' in filename:
            logger.warning(f"不安全的文件名: {filename}")
            return "无效的文件名", 400
            
        file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        logger.info(f"尝试下载文件: {file_path}")
        
        if not os.path.exists(file_path):
            logger.error(f"文件不存在: {file_path}")
            return "文件不存在", 404
            
        # 检查文件大小
        file_size = os.path.getsize(file_path)
        logger.info(f"下载文件大小: {file_size / 1024 / 1024:.2f} MB")
        
        # 使用绝对路径和正确的mimetype
        return send_file(
            os.path.abspath(file_path), 
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        
    except Exception as e:
        logger.error(f"文件下载失败: {e}", exc_info=True)
        return jsonify({'error': f'下载失败: {str(e)}'}), 500

@app.route('/api/files')
def list_files():
    """列出可下载的文件"""
    try:
        output_dir = app.config['OUTPUT_FOLDER']
        if not os.path.exists(output_dir):
            return jsonify({'files': []})
            
        files = []
        for filename in os.listdir(output_dir):
            if filename.endswith('.docx'):
                file_path = os.path.join(output_dir, filename)
                stat = os.stat(file_path)
                files.append({
                    'name': filename,
                    'size': stat.st_size,
                    'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    'download_url': url_for('download_file', filename=filename)
                })
        
        files.sort(key=lambda x: x['created'], reverse=True)
        return jsonify({'files': files})
        
    except Exception as e:
        logger.error(f"列出文件失败: {e}")
        return jsonify({'error': f'获取文件列表失败: {str(e)}'}), 500

@app.route('/api/test', methods=['POST'])
def test_api():
    """测试API连接"""
    try:
        api_key = request.json.get('api_key', '').strip()
        if not api_key:
            return jsonify({'error': 'API密钥不能为空'}), 400
            
        processor = EnhancedInlineReplyProcessor(api_key=api_key)
        
        if processor.test_api_connection():
            return jsonify({
                'success': True,
                'message': 'API连接测试成功！',
                'model': processor.model_config['model']
            })
        else:
            return jsonify({
                'success': False,
                'message': 'API连接测试失败，请检查密钥是否正确'
            })
            
    except Exception as e:
        logger.error(f"API测试失败: {e}")
        return jsonify({
            'success': False,
            'message': f'测试失败: {str(e)}'
        }), 500

@app.route('/api/save-key', methods=['POST'])
def save_api_key():
    """安全保存API密钥到服务器端"""
    try:
        api_key = request.json.get('api_key', '').strip()
        if not api_key:
            return jsonify({'error': 'API密钥不能为空'}), 400
        
        # 创建配置目录
        config_dir = 'config'
        os.makedirs(config_dir, exist_ok=True)
        
        # 使用简单加密存储（仅用于本地备份）
        key_hash = hashlib.md5(api_key.encode()).hexdigest()[:8]
        encrypted_key = base64.b64encode(api_key.encode()).decode()
        
        config_file = os.path.join(config_dir, f'api_backup_{key_hash}.json')
        
        backup_data = {
            'encrypted_key': encrypted_key,
            'created_at': datetime.now().isoformat(),
            'key_prefix': api_key[:10] + '...',
            'description': '始皇API密钥备份'
        }
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2)
        
        return jsonify({
            'success': True,
            'message': f'API密钥已安全备份 ({key_hash})',
            'backup_id': key_hash
        })
        
    except Exception as e:
        logger.error(f"API密钥保存失败: {e}")
        return jsonify({'error': f'保存失败: {str(e)}'}), 500

@app.route('/api/load-backups', methods=['GET'])
def load_api_backups():
    """加载API密钥备份列表"""
    try:
        config_dir = 'config'
        if not os.path.exists(config_dir):
            return jsonify({'backups': []})
        
        backups = []
        for filename in os.listdir(config_dir):
            if filename.startswith('api_backup_') and filename.endswith('.json'):
                try:
                    with open(os.path.join(config_dir, filename), 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        backups.append({
                            'id': filename.replace('api_backup_', '').replace('.json', ''),
                            'prefix': data.get('key_prefix', ''),
                            'created_at': data.get('created_at', ''),
                            'description': data.get('description', '')
                        })
                except Exception as e:
                    logger.warning(f"读取备份文件失败 {filename}: {e}")
        
        backups.sort(key=lambda x: x['created_at'], reverse=True)
        return jsonify({'backups': backups})
        
    except Exception as e:
        logger.error(f"加载备份列表失败: {e}")
        return jsonify({'error': f'加载失败: {str(e)}'}), 500

@app.route('/api/restore-key/<backup_id>', methods=['POST'])
def restore_api_key(backup_id):
    """恢复API密钥"""
    try:
        config_file = os.path.join('config', f'api_backup_{backup_id}.json')
        if not os.path.exists(config_file):
            return jsonify({'error': '备份文件不存在'}), 404
        
        with open(config_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        encrypted_key = data.get('encrypted_key', '')
        if not encrypted_key:
            return jsonify({'error': '备份数据无效'}), 400
        
        # 解密API密钥
        api_key = base64.b64decode(encrypted_key).decode()
        
        return jsonify({
            'success': True,
            'api_key': api_key,
            'message': 'API密钥恢复成功'
        })
        
    except Exception as e:
        logger.error(f"API密钥恢复失败: {e}")
        return jsonify({'error': f'恢复失败: {str(e)}'}), 500

@app.route('/extract-tender-info', methods=['POST'])
def extract_tender_info():
    """提取招标信息"""
    upload_path = None
    
    try:
        logger.info("开始处理招标信息提取请求")
        logger.info(f"请求方法: {request.method}")
        logger.info(f"请求文件: {list(request.files.keys())}")
        logger.info(f"请求表单: {list(request.form.keys())}")
        
        if not TENDER_INFO_AVAILABLE:
            logger.error("招标信息提取模块未加载")
            return jsonify({'error': '招标信息提取模块未加载，请检查系统配置'}), 500
        
        # 检查文件
        if 'file' not in request.files:
            logger.error("请求中未包含文件")
            return jsonify({'error': '需要上传招标文档'}), 400
        
        file = request.files['file']
        api_key = request.form.get('api_key', '').strip()
        
        logger.info(f"上传文件名: {file.filename}")
        logger.info(f"API密钥长度: {len(api_key) if api_key else 0}")
        
        if file.filename == '':
            return jsonify({'error': '请选择招标文档'}), 400
        
        if not allowed_tender_info_file(file.filename):
            return jsonify({'error': '不支持的文件类型，请上传.docx、.doc、.txt或.pdf文件'}), 400
        
        # 保存上传的文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = secure_filename(file.filename)
        unique_filename = f"{timestamp}_tender_{filename}"
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(upload_path)
        
        logger.info(f"招标文档上传完成: {upload_path}")
        
        # 初始化招标信息提取器
        logger.info("初始化招标信息提取器")
        extractor = TenderInfoExtractor(api_key=api_key)
        
        # 提取招标信息
        logger.info("开始提取招标信息")
        tender_info = extractor.process_document(upload_path)
        
        # 读取配置文件获取技术评分信息
        config_file_path = os.path.join(tender_info_path, 'tender_config.ini')
        technical_scoring = None
        if os.path.exists(config_file_path):
            try:
                import configparser
                config = configparser.ConfigParser(interpolation=None)
                config.read(config_file_path, encoding='utf-8')
                
                if 'TECHNICAL_SCORING' in config:
                    technical_scoring = {
                        'total_score': config.get('TECHNICAL_SCORING', 'total_score', fallback=''),
                        'extraction_summary': config.get('TECHNICAL_SCORING', 'extraction_summary', fallback=''),
                        'items_count': int(config.get('TECHNICAL_SCORING', 'items_count', fallback='0')),
                        'items': []
                    }
                    
                    # 读取技术评分项
                    for i in range(1, technical_scoring['items_count'] + 1):
                        item = {
                            'name': config.get('TECHNICAL_SCORING', f'item_{i}_name', fallback=''),
                            'weight': config.get('TECHNICAL_SCORING', f'item_{i}_weight', fallback=''),
                            'criteria': config.get('TECHNICAL_SCORING', f'item_{i}_criteria', fallback=''),
                            'source': config.get('TECHNICAL_SCORING', f'item_{i}_source', fallback='')
                        }
                        if item['name']:  # 只添加有名称的项目
                            technical_scoring['items'].append(item)
                    
                    logger.info(f"成功读取技术评分信息: {len(technical_scoring['items'])} 个评分项")
            except Exception as e:
                logger.error(f"读取技术评分配置失败: {e}")
                technical_scoring = None
        
        # 将技术评分信息添加到返回结果中
        if technical_scoring:
            tender_info['technical_scoring'] = technical_scoring
        
        logger.info(f"招标信息提取成功: {tender_info}")
        
        return jsonify({
            'success': True,
            'message': '招标信息提取完成',
            'tender_info': tender_info
        })
        
    except Exception as e:
        logger.error(f"招标信息提取失败: {e}", exc_info=True)
        
        error_message = str(e)
        if "API" in error_message or "OpenAI" in error_message:
            error_message = f"AI服务调用失败: {error_message}"
        elif "Memory" in error_message or "内存" in error_message:
            error_message = "文档过大导致内存不足，请尝试上传更小的文件"
        elif "No such file" in error_message:
            error_message = "文件读取失败，请确保上传的是有效的文档文件"
        
        return jsonify({'error': f'提取失败: {error_message}'}), 500
    
    finally:
        # 清理临时文件
        if upload_path and os.path.exists(upload_path):
            try:
                os.remove(upload_path)
                logger.info(f"清理临时文件: {upload_path}")
            except Exception as cleanup_error:
                logger.error(f"清理临时文件失败: {cleanup_error}")

@app.route('/health')
def health_check():
    """健康检查"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'AI标书智能生成系统',
        'tech_proposal_available': TECH_PROPOSAL_AVAILABLE,
        'tender_info_available': TENDER_INFO_AVAILABLE
    })

@app.route('/generate-proposal', methods=['POST'])
def generate_proposal():
    """生成技术方案"""
    tender_upload_path = None
    product_upload_path = None
    
    try:
        logger.info("开始处理技术方案生成请求")
        
        if not TECH_PROPOSAL_AVAILABLE:
            return jsonify({'error': '技术方案模块未加载，请检查系统配置'}), 500
        
        # 检查文件
        if 'tender_file' not in request.files or 'product_file' not in request.files:
            return jsonify({'error': '需要上传招标文件和产品文档'}), 400
        
        tender_file = request.files['tender_file']
        product_file = request.files['product_file']
        api_key = request.form.get('api_key', '').strip()
        output_prefix = request.form.get('output_prefix', '技术方案').strip()
        
        if tender_file.filename == '' or product_file.filename == '':
            return jsonify({'error': '请选择招标文件和产品文档'}), 400
        
        if not (allowed_tech_file(tender_file.filename) and allowed_tech_file(product_file.filename)):
            return jsonify({'error': '不支持的文件类型，请上传.docx、.doc或.pdf文件'}), 400
        
        # 保存上传的文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        tender_filename = secure_filename(tender_file.filename)
        tender_unique_filename = f"{timestamp}_tender_{tender_filename}"
        tender_upload_path = os.path.join(app.config['UPLOAD_FOLDER'], tender_unique_filename)
        tender_file.save(tender_upload_path)
        
        product_filename = secure_filename(product_file.filename)
        product_unique_filename = f"{timestamp}_product_{product_filename}"
        product_upload_path = os.path.join(app.config['UPLOAD_FOLDER'], product_unique_filename)
        product_file.save(product_upload_path)
        
        logger.info(f"文件上传完成: 招标文件={tender_upload_path}, 产品文档={product_upload_path}")
        
        # 初始化技术方案生成器
        logger.info("初始化技术方案生成器")
        
        # 临时修改环境变量以传递API密钥
        old_api_key = os.environ.get('OPENAI_API_KEY')
        if api_key:
            os.environ['OPENAI_API_KEY'] = api_key
        
        try:
            generator = TenderGenerator()
            
            # 生成输出文件前缀
            safe_prefix = f"{output_prefix}_{timestamp}"
            
            logger.info(f"开始生成技术方案: {safe_prefix}")
            
            # 生成技术方案
            result = generator.generate_proposal(
                tender_file=tender_upload_path,
                product_file=product_upload_path,
                output_prefix=safe_prefix
            )
            
            if result['success']:
                # 移动输出文件到技术方案输出目录
                moved_files = {}
                for file_type, file_path in result['output_files'].items():
                    if os.path.exists(file_path):
                        filename = os.path.basename(file_path)
                        new_path = os.path.join(app.config['TECH_OUTPUT_FOLDER'], filename)
                        shutil.move(file_path, new_path)
                        moved_files[file_type] = new_path
                        logger.info(f"移动文件: {file_path} -> {new_path}")
                
                result['output_files'] = moved_files
                logger.info(f"技术方案生成成功: {result}")
                
                return jsonify(result)
            else:
                logger.error(f"技术方案生成失败: {result['error']}")
                return jsonify(result), 500
                
        finally:
            # 恢复环境变量
            if old_api_key:
                os.environ['OPENAI_API_KEY'] = old_api_key
            elif 'OPENAI_API_KEY' in os.environ:
                del os.environ['OPENAI_API_KEY']
        
    except Exception as e:
        logger.error(f"技术方案生成失败: {e}", exc_info=True)
        
        error_message = str(e)
        if "API" in error_message or "OpenAI" in error_message:
            error_message = f"AI服务调用失败: {error_message}"
        elif "Memory" in error_message or "内存" in error_message:
            error_message = "文档过大导致内存不足，请尝试上传更小的文件"
        elif "No such file" in error_message:
            error_message = "文件读取失败，请确保上传的是有效的文档文件"
        
        return jsonify({'error': f'生成失败: {error_message}'}), 500
    
    finally:
        # 清理临时文件
        for path in [tender_upload_path, product_upload_path]:
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                    logger.info(f"清理临时文件: {path}")
                except Exception as cleanup_error:
                    logger.error(f"清理临时文件失败: {cleanup_error}")

@app.route('/download-tech/<filename>')
def download_tech_file(filename):
    """下载技术方案文件"""
    try:
        # 安全性检查：防止路径遍历攻击
        if '..' in filename or '/' in filename or '\\' in filename:
            logger.warning(f"不安全的文件名: {filename}")
            return "无效的文件名", 400
            
        file_path = os.path.join(app.config['TECH_OUTPUT_FOLDER'], filename)
        logger.info(f"尝试下载技术方案文件: {file_path}")
        
        if not os.path.exists(file_path):
            logger.error(f"文件不存在: {file_path}")
            return "文件不存在", 404
            
        # 根据文件扩展名设置正确的mimetype
        file_ext = filename.lower().split('.')[-1]
        if file_ext == 'docx':
            mimetype = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        elif file_ext == 'json':
            mimetype = 'application/json'
        elif file_ext == 'txt':
            mimetype = 'text/plain'
        else:
            mimetype = 'application/octet-stream'
        
        return send_file(
            os.path.abspath(file_path), 
            as_attachment=True,
            download_name=filename,
            mimetype=mimetype
        )
        
    except Exception as e:
        logger.error(f"技术方案文件下载失败: {e}", exc_info=True)
        return jsonify({'error': f'下载失败: {str(e)}'}), 500

@app.route('/api/tech-files')
def list_tech_files():
    """列出可下载的技术方案文件"""
    try:
        output_dir = app.config['TECH_OUTPUT_FOLDER']
        if not os.path.exists(output_dir):
            return jsonify({'files': []})
            
        files = []
        for filename in os.listdir(output_dir):
            if filename.endswith(('.docx', '.json', '.txt')):
                file_path = os.path.join(output_dir, filename)
                stat = os.stat(file_path)
                files.append({
                    'name': filename,
                    'size': stat.st_size,
                    'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    'download_url': url_for('download_tech_file', filename=filename)
                })
        
        files.sort(key=lambda x: x['created'], reverse=True)
        return jsonify({'files': files})
        
    except Exception as e:
        logger.error(f"列出技术方案文件失败: {e}")
        return jsonify({'error': f'获取文件列表失败: {str(e)}'}), 500

@app.route('/api/companies')
def list_companies():
    """获取所有公司配置"""
    try:
        companies = []
        company_configs_dir = 'company_configs'
        
        if os.path.exists(company_configs_dir):
            for filename in os.listdir(company_configs_dir):
                if filename.endswith('.json'):
                    file_path = os.path.join(company_configs_dir, filename)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            company_data = json.load(f)
                            companies.append({
                                'id': company_data.get('id', filename.replace('.json', '')),
                                'companyName': company_data.get('companyName', '未命名公司'),
                                'created_at': company_data.get('created_at', ''),
                                'updated_at': company_data.get('updated_at', '')
                            })
                    except Exception as e:
                        logger.warning(f"读取公司配置文件失败 {filename}: {e}")
        
        companies.sort(key=lambda x: x.get('updated_at', ''), reverse=True)
        return jsonify({'success': True, 'companies': companies})
        
    except Exception as e:
        logger.error(f"获取公司列表失败: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/companies/<company_id>')
def get_company(company_id):
    """获取指定公司的详细信息"""
    try:
        company_file = os.path.join('company_configs', f'{company_id}.json')
        
        if not os.path.exists(company_file):
            return jsonify({'error': '公司不存在'}), 404
            
        with open(company_file, 'r', encoding='utf-8') as f:
            company_data = json.load(f)
            
        return jsonify(company_data)
        
    except Exception as e:
        logger.error(f"获取公司信息失败: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/project-config')
def get_project_config():
    """获取项目配置信息"""
    try:
        import configparser
        
        config_file = 'tender_config.ini'
        if not os.path.exists(config_file):
            return jsonify({'success': False, 'error': '项目配置文件不存在'})
            
        config = configparser.ConfigParser()
        config.read(config_file, encoding='utf-8')
        
        # 提取项目信息
        project_info = {}
        if config.has_section('PROJECT_INFO'):
            project_info = {
                'projectName': config.get('PROJECT_INFO', 'project_name', fallback=''),
                'projectNumber': config.get('PROJECT_INFO', 'project_number', fallback=''),
                'tenderer': config.get('PROJECT_INFO', 'tenderer', fallback=''),
                'biddingMethod': config.get('PROJECT_INFO', 'bidding_method', fallback=''),
                'extractionTime': config.get('PROJECT_INFO', 'extraction_time', fallback='')
            }
        
        # 生成当前日期
        current_date = datetime.now().strftime('%Y年 %m月 %d日')
        project_info['currentDate'] = current_date
        
        return jsonify({
            'success': True, 
            'project_info': project_info
        })
        
    except Exception as e:
        logger.error(f"获取项目配置失败: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/process-business-response', methods=['POST'])
def process_business_response():
    """处理商务应答请求"""
    try:
        logger.info("开始处理商务应答请求")
        
        # 检查上传的文件
        if 'template_file' not in request.files:
            return jsonify({'error': '未上传模板文件'}), 400
            
        file = request.files['template_file']
        if file.filename == '':
            return jsonify({'error': '未选择文件'}), 400
            
        # 获取表单数据
        company_id = request.form.get('company_id')
        project_name = request.form.get('project_name', '')
        tender_no = request.form.get('tender_no', '')
        date_text = request.form.get('date_text', '')
        use_mcp = request.form.get('use_mcp', 'false').lower() == 'true'
        
        if not company_id:
            return jsonify({'error': '请选择公司'}), 400
            
        # 加载公司信息
        company_file = os.path.join('company_configs', f'{company_id}.json')
        if not os.path.exists(company_file):
            return jsonify({'error': '公司配置不存在'}), 404
            
        with open(company_file, 'r', encoding='utf-8') as f:
            company_info = json.load(f)
            
        # 保存上传的文件
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = secure_filename(file.filename)
        upload_filename = f"{timestamp}_business_template_{filename}"
        upload_path = os.path.join('uploads', upload_filename)
        
        os.makedirs('uploads', exist_ok=True)
        file.save(upload_path)
        logger.info(f"商务应答模板上传完成: {upload_path}")
        
        # 准备输出文件名
        base_name = filename.rsplit('.', 1)[0]
        output_filename = f"{base_name}-商务应答-{timestamp}.docx"
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
        
        # 根据用户选择初始化处理器
        if use_mcp:
            # 使用MCP模式：只处理投标人名称，不处理其他内容
            try:
                # 首先尝试使用增强版处理器（带占位符清理修复）
                try:
                    from mcp_bidder_name_processor_enhanced import MCPBidderNameProcessor
                    processor = MCPBidderNameProcessor()
                    logger.info("初始化增强版MCP投标人名称处理器（含占位符清理修复）")
                    
                    # 只处理投标人名称填写
                    result = processor.process_bidder_name(
                        input_file=upload_path,
                        output_file=output_path,
                        company_name=company_info.get('companyName', '')
                    )
                except ImportError:
                    # 如果增强版不可用，回退到原版
                    from mcp_bidder_name_processor import MCPBidderNameProcessor
                    processor = MCPBidderNameProcessor()
                    logger.info("初始化原版MCP投标人名称处理器")
                    
                    # 只处理投标人名称填写
                    result = processor.process_bidder_name(
                        input_file=upload_path,
                        output_file=output_path,
                        company_name=company_info.get('companyName', '')
                    )
                
            except ImportError as e:
                logger.error(f"MCP处理器加载失败: {e}")
                return jsonify({'error': 'MCP处理器不可用'}), 500
        else:
            # 使用传统模式：处理所有内容
            try:
                from business_response_processor import BusinessResponseProcessor
                processor = BusinessResponseProcessor()
                logger.info("初始化商务应答处理器 (传统模式)")
                
                # 处理完整的商务应答
                result = processor.process_business_response(
                    input_file=upload_path,
                    output_file=output_path,
                    company_info=company_info,
                    project_info={
                        'projectName': project_name,
                        'tenderNo': tender_no,
                        'date': date_text
                    }
                )
            except ImportError as e:
                logger.error(f"传统处理器加载失败: {e}")
                return jsonify({'error': '传统处理器不可用'}), 500
        
        # 清理临时文件
        try:
            os.remove(upload_path)
            logger.info(f"清理临时文件: {upload_path}")
        except:
            pass
        
        if result.get('success'):
            return jsonify({
                'success': True,
                'output_file': output_filename,
                'download_url': f'/download/{output_filename}',
                'stats': result.get('stats', {}),
                'message': '商务应答文档处理完成'
            })
        else:
            return jsonify({'error': result.get('error', '处理失败')}), 500
            
    except Exception as e:
        logger.error(f"商务应答处理失败: {e}", exc_info=True)
        return jsonify({'error': f'处理失败: {str(e)}'}), 500

def find_available_port(start_port=8080):
    """找到可用端口"""
    import socket
    for port in range(start_port, start_port + 100):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue
    return None

if __name__ == '__main__':
    port = find_available_port()
    if port:
        print("🚀 启动AI标书智能生成系统...")
        print(f"📱 Web界面地址: http://localhost:{port}")
        print("📋 点对点应答: 支持 .docx, .doc")
        print("📊 技术方案: 支持 .docx, .doc, .pdf") 
        print("📄 招标信息提取: 支持 .docx, .doc, .txt, .pdf")
        print("🤖 使用始皇API生成专业内容")
        if TECH_PROPOSAL_AVAILABLE:
            print("✅ 技术方案生成功能已加载")
        else:
            print("⚠️ 技术方案生成功能未加载")
        if TENDER_INFO_AVAILABLE:
            print("✅ 招标信息提取功能已加载")
        else:
            print("⚠️ 招标信息提取功能未加载")
        app.run(debug=True, host='0.0.0.0', port=port)
    else:
        print("❌ 无法找到可用端口，请手动指定端口运行")