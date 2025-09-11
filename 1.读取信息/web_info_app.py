#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
招标信息提取系统 - 独立Web应用
专注于从招标文档中提取项目信息、资质要求和技术评分标准
"""

import os
import logging
import json
import tempfile
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from read_info import TenderInfoExtractor

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tender_info_extraction.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Flask应用初始化
app = Flask(__name__)
app.config['SECRET_KEY'] = 'tender-info-extraction-system'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB最大文件大小
app.config['UPLOAD_FOLDER'] = 'uploads'

# 确保上传文件夹存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 支持的文件格式
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx'}

def allowed_file(filename):
    """检查文件类型是否支持"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_default_api_key():
    """获取默认API密钥"""
    try:
        # 从环境变量或配置文件获取
        return os.getenv('DEFAULT_API_KEY', '""')
    except Exception as e:
        logger.error(f"获取默认API密钥失败: {e}")
        return None

@app.route('/')
def index():
    """主页"""
    return render_template('tender_info.html')

@app.route('/api/get-default-api-key', methods=['GET'])
def get_api_key():
    """获取默认API密钥"""
    try:
        default_api_key = get_default_api_key()
        if default_api_key:
            return jsonify({'api_key': default_api_key})
        else:
            return jsonify({'error': '未配置默认API密钥'}), 404
    except Exception as e:
        logger.error(f"获取默认API密钥失败: {e}")
        return jsonify({'error': f'获取API密钥失败: {str(e)}'}), 500

@app.route('/extract-tender-info', methods=['POST'])
def extract_tender_info():
    """一次性提取招标信息"""
    upload_path = None
    
    try:
        # 检查文件
        if 'file' not in request.files:
            return jsonify({'error': '未提供文件'}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '未选择文件'}), 400
            
        if not allowed_file(file.filename):
            return jsonify({'error': '不支持的文件格式，请上传 .docx, .doc, .txt 或 .pdf 文件'}), 400
        
        # API密钥
        api_key = request.form.get('api_key', '').strip()
        if not api_key:
            api_key = get_default_api_key()
            logger.info("使用默认API密钥")
        
        if not api_key:
            return jsonify({'error': '请提供API密钥'}), 400
        
        # 保存文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = secure_filename(file.filename)
        unique_filename = f"{timestamp}_tender_{filename}"
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(upload_path)
        
        logger.info(f"招标文档上传完成: {upload_path}")
        
        # 初始化提取器
        extractor = TenderInfoExtractor(api_key=api_key)
        
        # 提取信息
        logger.info("开始提取招标信息")
        tender_info = extractor.process_document(upload_path)
        
        # 返回结果
        return jsonify({
            'success': True,
            'data': tender_info,
            'message': '招标信息提取完成'
        })
        
    except Exception as e:
        logger.error(f"提取招标信息失败: {e}", exc_info=True)
        return jsonify({'error': f'提取失败: {str(e)}'}), 500
        
    finally:
        # 清理临时文件
        if upload_path and os.path.exists(upload_path):
            try:
                os.remove(upload_path)
                logger.info(f"清理临时文件: {upload_path}")
            except Exception as cleanup_error:
                logger.error(f"清理临时文件失败: {cleanup_error}")

@app.route('/extract-tender-info-step', methods=['POST'])
def extract_tender_info_step():
    """分步提取招标信息"""
    upload_path = None
    
    try:
        step = request.form.get('step', '1')
        api_key = request.form.get('api_key', '').strip()
        
        logger.info(f"分步提取招标信息 - 步骤: {step}")
        
        # 如果没有提供API密钥，使用默认密钥
        if not api_key:
            api_key = get_default_api_key()
            logger.info("使用默认API密钥")
        
        if step == '1':
            # 第一步：处理文件上传并提取基本信息
            if 'file' not in request.files:
                return jsonify({'error': '需要上传招标文档'}), 400
                
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': '请选择招标文档'}), 400
                
            if not allowed_file(file.filename):
                return jsonify({'error': '不支持的文件格式，请上传 .docx, .doc, .txt 或 .pdf 文件'}), 400
            
            # 保存文件
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
            
            # 从提取结果中获取基本信息
            basic_info = {
                'tenderer': tender_info.get('tenderer', ''),
                'agency': tender_info.get('agency', ''),  
                'bidding_method': tender_info.get('bidding_method', ''),
                'bidding_location': tender_info.get('bidding_location', ''),
                'bidding_time': tender_info.get('bidding_time', ''),
                'winner_count': tender_info.get('winner_count', ''),
                'project_name': tender_info.get('project_name', ''),
                'project_number': tender_info.get('project_number', '')
            }
            
            # 保存提取结果到临时文件供后续步骤使用
            temp_result_file = upload_path + '.result.json'
            with open(temp_result_file, 'w', encoding='utf-8') as f:
                json.dump(tender_info, f, ensure_ascii=False, indent=2)
            
            return jsonify({
                'success': True,
                'basic_info': basic_info,
                'file_path': upload_path,
                'result_file': temp_result_file
            })
            
        elif step == '2':
            # 第二步：提取资质要求
            file_path = request.form.get('file_path')
            result_file = request.form.get('result_file')
            
            if not file_path or not os.path.exists(file_path):
                return jsonify({'error': '文件路径无效'}), 400
                
            # 尝试从临时结果文件读取
            tender_info = {}
            if result_file and os.path.exists(result_file):
                try:
                    with open(result_file, 'r', encoding='utf-8') as f:
                        tender_info = json.load(f)
                except:
                    pass
                    
            # 如果没有临时结果，重新提取
            if not tender_info:
                logger.info("重新提取招标信息")
                extractor = TenderInfoExtractor(api_key=api_key)
                tender_info = extractor.process_document(file_path)
                
            # 从提取结果中获取资质要求
            qualification_requirements = tender_info.get('qualification_requirements', {})
            
            # 如果没有资质要求数据，提供默认结构
            if not qualification_requirements:
                qualification_requirements = {
                    'business_license': {'required': False, 'description': '未检测到相关要求'},
                    'taxpayer_qualification': {'required': False, 'description': '未检测到相关要求'},
                    'performance_requirements': {'required': False, 'description': '未检测到相关要求'},
                    'authorization_requirements': {'required': False, 'description': '未检测到相关要求'},
                    'credit_china': {'required': False, 'description': '未检测到相关要求'},
                    'commitment_letter': {'required': False, 'description': '未检测到相关要求'},
                    'audit_report': {'required': False, 'description': '未检测到相关要求'},
                    'social_security': {'required': False, 'description': '未检测到相关要求'},
                    'labor_contract': {'required': False, 'description': '未检测到相关要求'},
                    'other_requirements': {'required': False, 'description': '未检测到相关要求'}
                }
            
            return jsonify({
                'success': True,
                'qualification_requirements': qualification_requirements
            })
            
        elif step == '3':
            # 第三步：提取技术评分
            file_path = request.form.get('file_path')
            result_file = request.form.get('result_file')
            
            if not file_path or not os.path.exists(file_path):
                return jsonify({'error': '文件路径无效'}), 400
                
            # 尝试从临时结果文件读取技术评分
            technical_scoring = {}
            if result_file and os.path.exists(result_file):
                try:
                    with open(result_file, 'r', encoding='utf-8') as f:
                        tender_info = json.load(f)
                        technical_scoring = tender_info.get('technical_scoring', {})
                except Exception as e:
                    logger.error(f"读取临时结果文件失败: {e}")
                    
            # 如果没有技术评分数据，重新提取
            if not technical_scoring:
                logger.info("重新提取技术评分信息")
                extractor = TenderInfoExtractor(api_key=api_key)
                tender_info = extractor.process_document(file_path)
                technical_scoring = tender_info.get('technical_scoring', {})
            
            # 如果仍然没有技术评分数据，提供默认信息
            if not technical_scoring:
                technical_scoring = {
                    '未检测到评分项目': {
                        'score': '未提取到分值',
                        'criteria': ['未检测到具体评分标准，请检查文档中是否包含评分表格']
                    }
                }
            
            return jsonify({
                'success': True,
                'technical_scoring': technical_scoring
            })
            
        else:
            return jsonify({'error': f'无效的步骤: {step}'}), 400
            
    except Exception as e:
        logger.error(f"分步提取失败: {e}", exc_info=True)
        return jsonify({'error': f'提取失败: {str(e)}'}), 500
        
    finally:
        # 清理临时文件（仅在步骤3之后）
        if step == '3' and upload_path and os.path.exists(upload_path):
            try:
                os.remove(upload_path)
                logger.info(f"清理临时文件: {upload_path}")
                # 同时清理结果文件
                result_file = upload_path + '.result.json'
                if os.path.exists(result_file):
                    os.remove(result_file)
            except Exception as cleanup_error:
                logger.error(f"清理临时文件失败: {cleanup_error}")

@app.route('/static/<path:filename>')
def serve_static(filename):
    """服务静态文件，强制缓存刷新"""
    response = send_from_directory('static', filename)
    # 对JavaScript文件强制禁用缓存
    if filename.endswith('.js'):
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    return response

@app.route('/health')
def health_check():
    """健康检查"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': '招标信息提取系统',
        'version': '1.0.0'
    })

if __name__ == '__main__':
    # 检查依赖
    try:
        from read_info import TenderInfoExtractor
        logger.info("招标信息提取模块加载成功")
    except ImportError as e:
        logger.error(f"招标信息提取模块加载失败: {e}")
        exit(1)
    
    # 启动应用
    logger.info("启动招标信息提取Web服务")
    app.run(host='0.0.0.0', port=5001, debug=True)