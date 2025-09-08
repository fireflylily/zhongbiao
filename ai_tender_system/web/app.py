# -*- coding: utf-8 -*-
"""
重构后的统一Web应用
整合所有模块的Web接口
"""

import os
import tempfile
from pathlib import Path
from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename

# 导入公共组件
from common.config import get_config
from common.logger import get_module_logger, setup_logging
from common.exceptions import AITenderSystemError

# 导入业务模块
from modules.tender_info.extractor import TenderInfoExtractor


def create_app() -> Flask:
    """创建Flask应用"""
    # 初始化日志系统
    setup_logging()
    
    app = Flask(__name__)
    CORS(app)
    
    # 加载配置
    config = get_config()
    logger = get_module_logger("web")
    
    # 应用配置
    app.config['MAX_CONTENT_LENGTH'] = config.get('web.max_content_length', 50 * 1024 * 1024)  # 50MB
    app.config['UPLOAD_FOLDER'] = config.app.upload_dir
    app.config['OUTPUT_FOLDER'] = config.app.output_dir
    
    # 确保必要目录存在
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
    
    def allowed_file(filename: str) -> bool:
        """检查文件格式是否允许"""
        allowed_extensions = config.get('web.allowed_extensions', ['.docx', '.doc', '.txt', '.pdf'])
        return any(filename.lower().endswith(ext) for ext in allowed_extensions)
    
    @app.errorhandler(AITenderSystemError)
    def handle_system_error(error):
        """处理系统异常"""
        logger.error(f"系统异常: {error}")
        return jsonify({'error': str(error), 'type': 'system_error'}), 500
    
    @app.errorhandler(413)
    def handle_large_file(error):
        """处理文件过大"""
        return jsonify({'error': '文件过大，请确保文件小于50MB'}), 413
    
    @app.route('/')
    def index():
        """主页"""
        return render_template('index.html')
    
    @app.route('/health')
    def health_check():
        """健康检查"""
        try:
            # 检查各模块状态
            status = {
                'status': 'healthy',
                'modules': {
                    'config': config.validate(),
                    'tender_info': True,  # 招标信息提取模块
                    'inline_reply': False,  # TODO: 实现后更新
                    'tech_proposal': False,  # TODO: 实现后更新
                },
                'version': '2.0.0'
            }
            
            return jsonify(status)
        except Exception as e:
            logger.error(f"健康检查失败: {e}")
            return jsonify({'status': 'unhealthy', 'error': str(e)}), 500
    
    @app.route('/api/extract-tender-info', methods=['POST'])
    def extract_tender_info():
        """招标信息提取API"""
        logger.info("收到招标信息提取请求")
        
        try:
            # 检查文件
            if 'file' not in request.files:
                return jsonify({'error': '未提供文件'}), 400
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': '文件名为空'}), 400
            
            if not allowed_file(file.filename):
                return jsonify({'error': '不支持的文件格式'}), 400
            
            # 保存临时文件
            filename = secure_filename(file.filename)
            temp_dir = tempfile.mkdtemp()
            temp_file_path = os.path.join(temp_dir, filename)
            file.save(temp_file_path)
            
            try:
                # 提取信息
                extractor = TenderInfoExtractor(output_dir=app.config['OUTPUT_FOLDER'])
                tender_info = extractor.extract_from_file(temp_file_path)
                
                # 保存配置文件
                config_file_path = extractor.save_to_config(tender_info)
                
                # 准备响应
                result = {
                    'success': True,
                    'data': tender_info.to_dict(),
                    'config_file': config_file_path,
                    'summary': tender_info.get_summary()
                }
                
                logger.info(f"招标信息提取成功: {tender_info.get_summary()}")
                return jsonify(result)
                
            finally:
                # 清理临时文件
                try:
                    os.remove(temp_file_path)
                    os.rmdir(temp_dir)
                except:
                    pass
        
        except AITenderSystemError as e:
            logger.error(f"业务异常: {e}")
            return jsonify({'error': str(e), 'type': 'business_error'}), 400
        
        except Exception as e:
            logger.error(f"未知异常: {e}")
            return jsonify({'error': '内部服务器错误', 'type': 'unknown_error'}), 500
    
    @app.route('/api/config/<filename>')
    def download_config(filename):
        """下载配置文件"""
        try:
            config_path = Path(app.config['OUTPUT_FOLDER']) / filename
            if config_path.exists() and config_path.suffix == '.ini':
                return send_file(config_path, as_attachment=True)
            else:
                return jsonify({'error': '配置文件不存在'}), 404
        except Exception as e:
            logger.error(f"下载配置文件失败: {e}")
            return jsonify({'error': '下载失败'}), 500
    
    @app.route('/api/modules')
    def list_modules():
        """列出所有可用模块"""
        modules = {
            'tender_info': {
                'name': '招标信息提取',
                'description': '从招标文档中提取项目基本信息、资质要求和技术评分',
                'endpoint': '/api/extract-tender-info',
                'supported_formats': ['.docx', '.doc', '.txt', '.pdf']
            },
            'inline_reply': {
                'name': '点对点应答',
                'description': '针对招标文件问题进行智能应答',
                'endpoint': '/api/inline-reply',
                'supported_formats': ['.docx', '.doc', '.txt', '.pdf'],
                'status': 'todo'  # TODO: 实现后更新
            },
            'tech_proposal': {
                'name': '技术方案生成',
                'description': '根据招标要求生成技术方案文档',
                'endpoint': '/api/generate-proposal',
                'supported_formats': ['.docx', '.doc', '.txt', '.pdf'],
                'status': 'todo'  # TODO: 实现后更新
            }
        }
        
        return jsonify(modules)
    
    logger.info("Web应用初始化完成")
    return app


if __name__ == '__main__':
    app = create_app()
    config = get_config()
    
    host = config.get('web.host', '0.0.0.0')
    port = config.get('web.port', 5000)
    debug = config.get('web.debug', False)
    
    print(f"启动Web服务: http://{host}:{port}")
    app.run(host=host, port=port, debug=debug)