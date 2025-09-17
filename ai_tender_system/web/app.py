#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI标书系统统一Web应用
整合招标信息提取、点对点应答、技术方案生成等所有功能
"""

import os
import sys
import tempfile
import hashlib
import time
from pathlib import Path
from flask import Flask, request, jsonify, render_template, send_file, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 导入公共组件
from common import (
    get_config, setup_logging, get_module_logger,
    AITenderSystemError, format_error_response, handle_api_error,
    safe_filename, allowed_file, ensure_dir
)

# 导入业务模块
try:
    from modules.tender_info.extractor import TenderInfoExtractor
    TENDER_INFO_AVAILABLE = True
except ImportError as e:
    print(f"招标信息提取模块加载失败: {e}")
    TENDER_INFO_AVAILABLE = False

# 商务应答模块（原点对点应答）
try:
    from modules.business_response.processor import BusinessResponseProcessor, PointToPointProcessor
    BUSINESS_RESPONSE_AVAILABLE = True
    POINT_TO_POINT_AVAILABLE = True  # 保持向后兼容
except ImportError as e:
    print(f"商务应答模块加载失败: {e}")
    BUSINESS_RESPONSE_AVAILABLE = False
    POINT_TO_POINT_AVAILABLE = False

# 技术需求回复模块
try:
    from modules.point_to_point.tech_responder import TechResponder
    TECH_RESPONDER_AVAILABLE = True
except ImportError as e:
    print(f"技术需求回复模块加载失败: {e}")
    TECH_RESPONDER_AVAILABLE = False

def create_app() -> Flask:
    """创建Flask应用"""
    # 初始化配置和日志
    config = get_config()
    setup_logging()
    logger = get_module_logger("web_app")
    
    # 创建Flask应用
    app = Flask(__name__, 
                template_folder=str(config.get_path('templates')),
                static_folder=str(config.get_path('static')))
    
    # 配置应用
    web_config = config.get_web_config()
    app.config.update({
        'SECRET_KEY': web_config['secret_key'],
        'MAX_CONTENT_LENGTH': config.get_upload_config()['max_file_size']
    })
    
    # 启用CORS
    CORS(app)
    
    # 注册路由
    register_routes(app, config, logger)
    
    logger.info("AI标书系统Web应用初始化完成")
    return app

def register_routes(app: Flask, config, logger):
    """注册所有路由"""
    
    # ===================
    # 静态页面路由
    # ===================
    
    @app.route('/')
    def index():
        """主页"""
        return render_template('index.html')
    
    
    @app.route('/help.html')
    def help():
        """帮助页面"""
        return render_template('help.html')
    
    @app.route('/system_status.html')
    def system_status():
        """系统状态页面"""
        return render_template('system_status.html')
    
    # ===================
    # 静态资源路由
    # ===================
    
    @app.route('/css/<path:filename>')
    def serve_css(filename):
        """提供CSS文件"""
        return send_from_directory(config.get_path('static') / 'css', filename)
    
    @app.route('/js/<path:filename>')
    def serve_js(filename):
        """提供JavaScript文件"""
        return send_from_directory(config.get_path('static') / 'js', filename)
    
    @app.route('/images/<path:filename>')
    def serve_images(filename):
        """提供图片文件"""
        return send_from_directory(config.get_path('static') / 'images', filename)
    
    # ===================
    # API路由
    # ===================
    
    @app.route('/api/health')
    def health_check():
        """健康检查"""
        from datetime import datetime
        return jsonify({
            'status': 'healthy',
            'version': '2.0.0',
            'timestamp': datetime.now().isoformat(),
            'tender_info_available': TENDER_INFO_AVAILABLE,
            'business_response_available': BUSINESS_RESPONSE_AVAILABLE,
            'point_to_point_available': POINT_TO_POINT_AVAILABLE,  # 向后兼容
            'tech_responder_available': TECH_RESPONDER_AVAILABLE
        })
    
    @app.route('/api/config')
    def get_api_config():
        """获取API配置"""
        try:
            api_config = config.get_api_config()
            # 隐藏敏感信息
            safe_config = {
                'api_endpoint': api_config['api_endpoint'],
                'model_name': api_config['model_name'],
                'max_completion_tokens': api_config['max_tokens'],
                'has_api_key': bool(api_config.get('api_key'))
            }
            return jsonify({'success': True, 'config': safe_config})
        except Exception as e:
            logger.error(f"获取API配置失败: {e}")
            return jsonify(format_error_response(e))
    
    @app.route('/api/get-default-api-key', methods=['GET'])
    def get_default_api_key():
        """获取默认API密钥（仅返回前10位）"""
        try:
            api_key = config.get_default_api_key()
            return jsonify({
                'success': True,
                'api_key': api_key[:10] + '...' if api_key else '',
                'has_key': bool(api_key)
            })
        except Exception as e:
            logger.error(f"获取默认API密钥失败: {e}")
            return jsonify(format_error_response(e))
    
    @app.route('/api/save-key', methods=['POST'])
    def save_api_key():
        """保存API密钥"""
        try:
            data = request.get_json()
            api_key = data.get('api_key', '').strip()
            
            if not api_key:
                raise ValueError("API密钥不能为空")
            
            config.set_api_key(api_key)
            logger.info("API密钥已更新")
            
            return jsonify({'success': True, 'message': 'API密钥保存成功'})
        except Exception as e:
            logger.error(f"保存API密钥失败: {e}")
            return jsonify(format_error_response(e))
    
    # ===================
    # 文件处理路由
    # ===================
    
    @app.route('/upload', methods=['POST'])
    def upload_file():
        """通用文件上传"""
        try:
            if 'file' not in request.files:
                raise ValueError("没有选择文件")
            
            file = request.files['file']
            if file.filename == '':
                raise ValueError("文件名为空")
            
            # 获取文件类型和允许的扩展名
            file_type = request.form.get('type', 'tender_info')
            upload_config = config.get_upload_config()
            allowed_extensions = upload_config['allowed_extensions'].get(file_type, set())
            
            if not allowed_file(file.filename, allowed_extensions):
                raise ValueError(f"不支持的文件类型，允许的类型: {', '.join(allowed_extensions)}")
            
            # 保存文件
            filename = safe_filename(file.filename)
            upload_dir = ensure_dir(config.get_path('upload'))
            file_path = upload_dir / filename
            file.save(str(file_path))
            
            logger.info(f"文件上传成功: {filename}")
            return jsonify({
                'success': True,
                'filename': filename,
                'file_path': str(file_path),
                'message': '文件上传成功'
            })
            
        except Exception as e:
            logger.error(f"文件上传失败: {e}")
            return jsonify(format_error_response(e))
    
    @app.route('/download/<filename>')
    def download_file(filename):
        """文件下载"""
        try:
            output_dir = config.get_path('output')
            file_path = output_dir / filename
            
            if not file_path.exists():
                raise FileNotFoundError(f"文件不存在: {filename}")
            
            logger.info(f"文件下载: {filename}")
            return send_file(str(file_path), as_attachment=True)
            
        except Exception as e:
            logger.error(f"文件下载失败: {e}")
            return jsonify(format_error_response(e))
    
    # ===================
    # 招标信息相关路由（暂时占位）
    # ===================
    
    @app.route('/extract-tender-info', methods=['POST'])
    def extract_tender_info():
        """招标信息提取"""
        if not TENDER_INFO_AVAILABLE:
            return jsonify({
                'success': False,
                'message': '招标信息提取模块不可用'
            })
        
        try:
            logger.info(f"一次性API调用 - Content-Type: {request.content_type}")
            logger.info(f"一次性API调用 - Form keys: {list(request.form.keys())}")
            logger.info(f"一次性API调用 - Files keys: {list(request.files.keys())}")

            # 获取上传的文件
            if 'file' not in request.files:
                raise ValueError("没有选择文件")

            file = request.files['file']
            if file.filename == '':
                raise ValueError("文件名为空")

            # 获取API密钥
            api_key = request.form.get('api_key') or config.get_default_api_key()
            if not api_key:
                raise ValueError("API密钥未配置。请在环境变量中设置DEFAULT_API_KEY或在页面中输入API密钥")

            # 保存上传文件
            filename = safe_filename(file.filename)
            upload_dir = ensure_dir(config.get_path('upload'))
            file_path = upload_dir / filename
            file.save(str(file_path))

            logger.info(f"一次性API - 开始提取招标信息: {filename}")
            
            # 执行信息提取
            extractor = TenderInfoExtractor(api_key=api_key)
            result = extractor.process_document(str(file_path))
            
            logger.info("招标信息提取完成")
            return jsonify({
                'success': True,
                'data': result,
                'message': '招标信息提取成功'
            })
            
        except Exception as e:
            logger.error(f"招标信息提取失败: {e}")
            return jsonify(format_error_response(e))
    
    @app.route('/extract-tender-info-step', methods=['POST'])
    def extract_tender_info_step():
        """分步招标信息提取"""
        if not TENDER_INFO_AVAILABLE:
            return jsonify({
                'success': False,
                'message': '招标信息提取模块不可用'
            })

        try:
            logger.info(f"分步API调用 - Content-Type: {request.content_type}")
            logger.info(f"分步API调用 - Form keys: {list(request.form.keys())}")
            logger.info(f"分步API调用 - Files keys: {list(request.files.keys())}")

            # 支持两种格式：JSON 和 FormData
            if request.content_type and 'application/json' in request.content_type:
                data = request.get_json()
                step = data.get('step', '1')
                file_path = data.get('file_path', '')
                api_key = data.get('api_key') or config.get_default_api_key()
                logger.info(f"分步API - JSON格式, step: {step}, file_path: {file_path}")
            else:
                # FormData 格式 - 支持文件上传
                step = request.form.get('step', '1')
                file_path = request.form.get('file_path', '')
                api_key = request.form.get('api_key') or config.get_default_api_key()
                logger.info(f"分步API - FormData格式, step: {step}, file_path: {file_path}")

                # 如果没有file_path但有文件上传，处理文件上传
                if not file_path and 'file' in request.files:
                    file = request.files['file']
                    if file.filename != '':
                        # 保存上传文件
                        filename = safe_filename(file.filename)
                        upload_dir = ensure_dir(config.get_path('upload'))
                        file_path = upload_dir / filename
                        file.save(str(file_path))
                        file_path = str(file_path)
                        logger.info(f"分步处理：文件已上传到 {file_path}")
                    else:
                        logger.warning("分步API - 文件名为空")
                else:
                    logger.info(f"分步API - 没有文件上传，使用现有file_path: {file_path}")

            if not file_path or not Path(file_path).exists():
                raise ValueError("文件路径无效或文件不存在")

            if not api_key:
                raise ValueError("API密钥未配置。请在环境变量中设置DEFAULT_API_KEY或在页面中输入API密钥")

            extractor = TenderInfoExtractor(api_key=api_key)
            
            if step == '1':
                # 第一步：提取基本信息
                text = extractor.read_document(file_path)
                basic_info = extractor.extract_basic_info(text)
                
                return jsonify({
                    'success': True,
                    'step': 1,
                    'data': basic_info,
                    'message': '基本信息提取成功'
                })
                
            elif step == '2':
                # 第二步：提取资质要求
                text = extractor.read_document(file_path)
                qualification_info = extractor.extract_qualification_requirements(text)
                
                return jsonify({
                    'success': True,
                    'step': 2,
                    'data': qualification_info,
                    'message': '资质要求提取成功'
                })
                
            elif step == '3':
                # 第三步：提取技术评分
                text = extractor.read_document(file_path)
                scoring_info = extractor.extract_technical_scoring(text)
                
                return jsonify({
                    'success': True,
                    'step': 3,
                    'data': scoring_info,
                    'message': '技术评分提取成功'
                })
                
            else:
                raise ValueError(f"无效的步骤: {step}")
                
        except Exception as e:
            logger.error(f"分步招标信息提取失败: {e}")
            return jsonify(format_error_response(e))
    
    # ===================
    # 商务应答相关路由（暂时占位）
    # ===================
    
    @app.route('/process-business-response', methods=['POST'])
    def process_business_response():
        """处理商务应答"""
        if not BUSINESS_RESPONSE_AVAILABLE:
            return jsonify({
                'success': False,
                'message': '商务应答模块不可用'
            })
        
        try:
            # 获取上传的文件
            if 'template_file' not in request.files:
                raise ValueError("没有选择模板文件")
            
            file = request.files['template_file']
            if file.filename == '':
                raise ValueError("文件名为空")
            
            # 获取表单数据
            data = request.form.to_dict()
            company_id = data.get('company_id', '')
            project_name = data.get('project_name', '')
            tender_no = data.get('tender_no', '')
            date_text = data.get('date_text', '')
            use_mcp = data.get('use_mcp', 'false').lower() == 'true'
            
            # 验证必填字段
            if not company_id:
                raise ValueError("请选择应答公司")
            
            # 获取公司信息
            import json
            company_configs_dir = config.get_path('config') / 'companies'
            company_file = company_configs_dir / f'{company_id}.json'
            
            if not company_file.exists():
                raise ValueError(f"未找到公司信息: {company_id}")
                
            with open(company_file, 'r', encoding='utf-8') as f:
                company_data = json.load(f)
            
            # 保存模板文件
            filename = safe_filename(file.filename)
            upload_dir = ensure_dir(config.get_path('upload'))
            template_path = upload_dir / filename
            file.save(str(template_path))
            
            logger.info(f"开始处理商务应答: {filename}")
            
            # 公共的输出文件路径设置（移到外面，两个分支都需要）
            output_dir = ensure_dir(config.get_path('output'))

            # 确保输出文件名格式正确，重新处理filename以确保有正确的扩展名
            # filename 可能已经被 safe_filename 处理过，但需要确保输出文件名格式正确
            base_name, ext = os.path.splitext(filename)
            if not ext or ext.lower() not in ['.docx', '.doc']:
                ext = '.docx'  # 确保有正确的扩展名

            output_filename = f"business_response_{company_id}_{base_name}{ext}"
            output_path = output_dir / output_filename

            logger.info(f"📁 输出文件路径: {output_path}")
            logger.info(f"📁 输出文件名: {output_filename}")
            
            logger.info(f"公司数据验证:")
            logger.info(f"  - 公司名称: {company_data.get('companyName', 'N/A')}")
            logger.info(f"  - 联系电话: {company_data.get('fixedPhone', 'N/A')}")
            logger.info(f"  - 电子邮件: {company_data.get('email', 'N/A')}")
            logger.info(f"  - 公司地址: {company_data.get('address', 'N/A')}")
            logger.info(f"  - 传真号码: {company_data.get('fax', 'N/A')}")
            logger.info(f"  - 项目名称: {project_name}")
            logger.info(f"  - 招标编号: {tender_no}")
            logger.info(f"  - 日期文本: {date_text}")
            
            # 使用MCP处理器处理商务应答
            if use_mcp:
                # 使用新架构的商务应答处理器
                processor = BusinessResponseProcessor()
                
                # 使用MCP处理器的完整商务应答处理方法，包含日期字段处理
                result_stats = processor.process_business_response(
                    str(template_path),
                    str(output_path), 
                    company_data,
                    project_name,
                    tender_no,
                    date_text
                )
                
                output_path = str(output_path)
                
                # 检查处理结果并构建响应
                if result_stats.get('success'):
                    logger.info(f"新架构处理器执行成功: {result_stats.get('message', '无消息')}")
                    logger.info(f"处理统计: {result_stats.get('stats', {})}")
                    
                    # 构建成功结果
                    result = {
                        'success': True,
                        'message': result_stats.get('message', '商务应答处理完成'),
                        'output_file': output_path,
                        'download_url': f'/download/{os.path.basename(output_path)}',
                        'stats': result_stats.get('stats', {})
                    }
                else:
                    logger.error(f"新架构处理器执行失败: {result_stats.get('error', '未知错误')}")
                    result = {
                        'success': False,
                        'error': result_stats.get('error', '处理失败'),
                        'message': result_stats.get('message', '商务应答处理失败')
                    }
            else:
                # 使用向后兼容的处理器（实际上还是新的BusinessResponseProcessor）
                processor = PointToPointProcessor()  # 这是BusinessResponseProcessor的别名
                result_stats = processor.process_business_response(
                    str(template_path),
                    str(output_path),
                    company_data,
                    project_name,
                    tender_no,
                    date_text
                )
                
                # 统一返回格式处理
                if result_stats.get('success'):
                    result = {
                        'success': True,
                        'message': result_stats.get('message', '商务应答处理完成'),
                        'output_file': str(output_path),
                        'download_url': f'/download/{os.path.basename(output_path)}',
                        'stats': result_stats.get('summary', {})
                    }
                else:
                    result = {
                        'success': False,
                        'error': result_stats.get('error', '处理失败'),
                        'message': result_stats.get('message', '商务应答处理失败')
                    }
            
            logger.info("商务应答处理完成")
            return jsonify(result)
            
        except Exception as e:
            logger.error(f"商务应答处理失败: {e}")
            return jsonify(format_error_response(e))
    
    @app.route('/api/document/process', methods=['POST'])
    def process_document():
        """处理文档 - 通用接口"""
        if not BUSINESS_RESPONSE_AVAILABLE:
            return jsonify({
                'success': False,
                'message': '文档处理模块不可用'
            })
        
        try:
            data = request.get_json()
            file_path = data.get('file_path', '')
            options = data.get('options', {})
            
            if not file_path:
                raise ValueError("文件路径不能为空")
            
            # 这是一个通用接口，根据选项决定使用哪个处理器
            doc_type = options.get('type', 'business_response')
            
            if doc_type == 'tech_requirements' and TECH_RESPONDER_AVAILABLE:
                result = {
                    'success': True,
                    'message': '技术需求处理功能可用，请使用 /process-tech-requirements 接口',
                    'redirect': '/process-tech-requirements'
                }
            else:
                result = {
                    'success': True,
                    'message': '商务应答处理功能可用，请使用 /process-business-response 接口',
                    'redirect': '/process-business-response'
                }
            
            return jsonify(result)
            
        except Exception as e:
            logger.error(f"文档处理失败: {e}")
            return jsonify(format_error_response(e))
    
    # ===================
    # 技术需求回复路由
    # ===================
    
    @app.route('/process-tech-requirements', methods=['POST'])
    def process_tech_requirements():
        """处理技术需求回复"""
        if not TECH_RESPONDER_AVAILABLE:
            return jsonify({
                'success': False,
                'message': '技术需求回复模块不可用'
            })
        
        try:
            # 获取上传的文件
            if 'requirements_file' not in request.files:
                raise ValueError("没有选择需求文件")
            
            file = request.files['requirements_file']
            if file.filename == '':
                raise ValueError("文件名为空")
            
            # 获取表单数据
            data = request.form.to_dict()
            company_id = data.get('company_id', '')
            response_strategy = data.get('response_strategy', 'comprehensive')
            
            # 验证必填字段
            if not company_id:
                raise ValueError("请选择应答公司")
            
            # 保存上传的文件
            filename = safe_filename(file.filename)
            upload_dir = ensure_dir(config.get_path('upload'))
            requirements_path = upload_dir / filename
            file.save(str(requirements_path))
            
            # 加载公司数据
            company_data = config.load_company_data(company_id)
            if not company_data:
                raise ValueError(f"未找到公司数据: {company_id}")
            
            logger.info(f"开始处理技术需求: {filename}")
            
            # 创建技术需求回复处理器
            responder = TechResponder()
            
            # 生成输出文件路径
            output_dir = ensure_dir(config.get_path('output'))
            output_filename = f"tech_response_{company_id}_{filename}"
            output_path = output_dir / output_filename
            
            # 处理技术需求
            result_stats = responder.process_tech_requirements(
                str(requirements_path),
                str(output_path),
                company_data,
                response_strategy
            )
            
            if result_stats.get('success'):
                logger.info(f"技术需求处理成功: {result_stats.get('message')}")
                result = {
                    'success': True,
                    'message': result_stats.get('message', '技术需求处理完成'),
                    'output_file': str(output_path),
                    'download_url': f'/download/{os.path.basename(output_path)}',
                    'stats': {
                        'requirements_count': result_stats.get('requirements_count', 0),
                        'responses_count': result_stats.get('responses_count', 0)
                    }
                }
            else:
                logger.error(f"技术需求处理失败: {result_stats.get('error')}")
                result = {
                    'success': False,
                    'error': result_stats.get('error', '处理失败'),
                    'message': result_stats.get('message', '技术需求处理失败')
                }
            
            return jsonify(result)
            
        except Exception as e:
            logger.error(f"技术需求处理异常: {e}")
            return jsonify(format_error_response(e))
    
    # 文档预览和编辑API
    @app.route('/api/document/preview/<filename>', methods=['GET'])
    def preview_document(filename):
        """预览文档内容（转换为HTML）"""
        try:
            from docx import Document
            import html
            
            # 直接查找文件，不对filename进行二次处理，避免破坏已有的文件名
            file_path = config.get_path('output') / filename

            if not file_path.exists():
                # 如果直接查找失败，尝试在输出目录中查找匹配的文件
                output_dir = config.get_path('output')
                matching_files = [f for f in output_dir.iterdir() if f.name.endswith(filename) or filename in f.name]

                if matching_files:
                    file_path = matching_files[0]  # 使用第一个匹配的文件
                    logger.info(f"找到匹配文件: {file_path}")
                else:
                    raise FileNotFoundError(f"文档不存在: {filename}")

            logger.info(f"预览文档: {file_path}")
            
            # 读取Word文档
            doc = Document(str(file_path))
            
            # 转换为HTML
            html_content = []
            html_content.append('<div class="document-preview">')
            
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    # 检查段落样式
                    style_name = paragraph.style.name if paragraph.style else ''
                    text = html.escape(paragraph.text)
                    
                    if 'Heading 1' in style_name:
                        html_content.append(f'<h1>{text}</h1>')
                    elif 'Heading 2' in style_name:
                        html_content.append(f'<h2>{text}</h2>')
                    elif 'Heading 3' in style_name:
                        html_content.append(f'<h3>{text}</h3>')
                    else:
                        html_content.append(f'<p>{text}</p>')
            
            # 处理表格
            for table in doc.tables:
                html_content.append('<table class="table table-bordered">')
                for row in table.rows:
                    html_content.append('<tr>')
                    for cell in row.cells:
                        cell_text = html.escape(cell.text)
                        html_content.append(f'<td>{cell_text}</td>')
                    html_content.append('</tr>')
                html_content.append('</table>')
            
            html_content.append('</div>')
            
            return jsonify({
                'success': True,
                'html_content': ''.join(html_content),
                'filename': filename
            })
            
        except Exception as e:
            logger.error(f"文档预览失败: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            })
    
    @app.route('/api/editor/load-document', methods=['POST'])
    def load_document_for_edit():
        """加载文档用于编辑"""
        try:
            from docx import Document
            from markupsafe import Markup
            
            if 'file' not in request.files:
                raise ValueError("没有选择文件")
            
            file = request.files['file']
            if file.filename == '':
                raise ValueError("文件名为空")
            
            # 读取Word文档
            doc = Document(file)
            
            # 转换为HTML格式用于编辑器
            html_content = []
            
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    style_name = paragraph.style.name if paragraph.style else ''
                    
                    if 'Heading 1' in style_name:
                        html_content.append(f'<h1>{paragraph.text}</h1>')
                    elif 'Heading 2' in style_name:
                        html_content.append(f'<h2>{paragraph.text}</h2>')
                    elif 'Heading 3' in style_name:
                        html_content.append(f'<h3>{paragraph.text}</h3>')
                    else:
                        html_content.append(f'<p>{paragraph.text}</p>')
            
            # 处理表格
            for table in doc.tables:
                html_content.append('<table>')
                for row in table.rows:
                    html_content.append('<tr>')
                    for cell in row.cells:
                        html_content.append(f'<td>{cell.text}</td>')
                    html_content.append('</tr>')
                html_content.append('</table>')
            
            return jsonify({
                'success': True,
                'html_content': ''.join(html_content),
                'original_filename': file.filename
            })
            
        except Exception as e:
            logger.error(f"文档加载失败: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            })
    
    @app.route('/api/editor/save-document', methods=['POST'])
    def save_edited_document():
        """保存编辑后的文档"""
        try:
            from docx import Document
            from bs4 import BeautifulSoup
            import re
            
            data = request.get_json()
            html_content = data.get('html_content', '')
            filename = data.get('filename', 'document')
            
            if not html_content:
                raise ValueError("文档内容为空")
            
            # 创建新文档
            doc = Document()
            
            # 解析HTML内容
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 处理各种HTML元素
            for element in soup.find_all(['h1', 'h2', 'h3', 'p', 'table']):
                if element.name == 'h1':
                    doc.add_heading(element.get_text(), level=1)
                elif element.name == 'h2':
                    doc.add_heading(element.get_text(), level=2)
                elif element.name == 'h3':
                    doc.add_heading(element.get_text(), level=3)
                elif element.name == 'p':
                    text = element.get_text()
                    if text.strip():
                        doc.add_paragraph(text)
                elif element.name == 'table':
                    # 计算表格行列数
                    rows = element.find_all('tr')
                    if rows:
                        cols = len(rows[0].find_all(['td', 'th']))
                        table = doc.add_table(rows=len(rows), cols=cols)
                        table.style = 'Table Grid'
                        
                        for i, row in enumerate(rows):
                            cells = row.find_all(['td', 'th'])
                            for j, cell in enumerate(cells):
                                if j < cols:
                                    table.cell(i, j).text = cell.get_text()
            
            # 保存文档
            output_dir = ensure_dir(config.get_path('output'))
            output_path = output_dir / f"{filename}.docx"
            doc.save(str(output_path))
            
            # 返回文件供下载
            return send_file(
                str(output_path),
                as_attachment=True,
                download_name=f"{filename}.docx",
                mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            )
            
        except Exception as e:
            logger.error(f"文档保存失败: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            })
    
    @app.route('/api/editor/upload-image', methods=['POST'])
    def upload_editor_image():
        """上传编辑器图片"""
        try:
            if 'image' not in request.files:
                raise ValueError("没有选择图片")
            
            file = request.files['image']
            if file.filename == '':
                raise ValueError("文件名为空")
            
            # 检查文件类型
            allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
            if not allowed_file(file.filename, allowed_extensions):
                raise ValueError(f"不支持的图片格式")
            
            # 保存图片
            filename = safe_filename(file.filename)
            upload_dir = ensure_dir(config.get_path('upload') / 'images')
            file_path = upload_dir / filename
            file.save(str(file_path))
            
            # 返回图片URL
            image_url = f'/static/uploads/images/{filename}'
            
            return jsonify({
                'success': True,
                'location': image_url
            })
            
        except Exception as e:
            logger.error(f"图片上传失败: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            })
    
    @app.route('/api/table/analyze', methods=['POST'])
    def analyze_table():
        """分析表格"""
        if not POINT_TO_POINT_AVAILABLE:
            return jsonify({
                'success': False,
                'message': '表格处理模块不可用'
            })
        
        try:
            data = request.get_json()
            table_data = data.get('table_data', {})
            
            processor = TableProcessor()
            result = processor.analyze_table(table_data)
            
            return jsonify(result)
            
        except Exception as e:
            logger.error(f"表格分析失败: {e}")
            return jsonify(format_error_response(e))
    
    @app.route('/api/table/process', methods=['POST'])
    def process_table():
        """处理表格"""
        if not POINT_TO_POINT_AVAILABLE:
            return jsonify({
                'success': False,
                'message': '表格处理模块不可用'
            })
        
        try:
            data = request.get_json()
            table_data = data.get('table_data', {})
            options = data.get('options', {})
            
            processor = TableProcessor()
            result = processor.process_table(table_data, options)
            
            return jsonify(result)
            
        except Exception as e:
            logger.error(f"表格处理失败: {e}")
            return jsonify(format_error_response(e))
    
    # ===================
    # 技术方案相关路由（暂时占位）
    # ===================
    
    @app.route('/generate-proposal', methods=['POST'])
    def generate_proposal():
        """生成技术方案"""
        # TODO: 实现技术方案生成功能
        return jsonify({
            'success': False,
            'message': '技术方案生成功能正在迁移中'
        })
    
    # ===================
    # 公司管理API
    # ===================
    
    @app.route('/api/companies')
    def list_companies():
        """获取所有公司配置"""
        try:
            import json
            
            companies = []
            company_configs_dir = config.get_path('config') / 'companies'
            
            if company_configs_dir.exists():
                for filename in os.listdir(company_configs_dir):
                    if filename.endswith('.json'):
                        file_path = company_configs_dir / filename
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
            import json
            
            company_configs_dir = config.get_path('config') / 'companies'
            company_file = company_configs_dir / f'{company_id}.json'
            
            if not company_file.exists():
                return jsonify({'success': False, 'error': '公司不存在'}), 404
                
            with open(company_file, 'r', encoding='utf-8') as f:
                company_data = json.load(f)
                
            return jsonify({'success': True, 'company': company_data})
            
        except Exception as e:
            logger.error(f"获取公司信息失败: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/companies', methods=['POST'])
    def create_company():
        """创建新公司"""
        try:
            import json
            from datetime import datetime
            
            data = request.get_json()
            if not data:
                return jsonify({'success': False, 'error': '请提供公司信息'}), 400
            
            company_name = data.get('companyName', '').strip()
            if not company_name:
                return jsonify({'success': False, 'error': '公司名称不能为空'}), 400
            
            # 生成公司ID
            company_id = hashlib.md5(company_name.encode('utf-8')).hexdigest()[:8]
            
            # 准备公司数据
            company_data = {
                'id': company_id,
                'companyName': company_name,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            # 添加其他字段
            for field in ['companyAddress', 'legalPerson', 'contactInfo', 'businessScope']:
                if field in data:
                    company_data[field] = data[field]
            
            # 确保目录存在
            company_configs_dir = config.get_path('config') / 'companies'
            company_configs_dir.mkdir(parents=True, exist_ok=True)
            
            # 保存公司信息
            company_file = company_configs_dir / f'{company_id}.json'
            with open(company_file, 'w', encoding='utf-8') as f:
                json.dump(company_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"创建公司成功: {company_name} (ID: {company_id})")
            return jsonify({'success': True, 'company': company_data})
            
        except Exception as e:
            logger.error(f"创建公司失败: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/companies/<company_id>', methods=['PUT'])
    def update_company(company_id):
        """更新公司信息"""
        try:
            import json
            from datetime import datetime
            
            data = request.get_json()
            if not data:
                return jsonify({'success': False, 'error': '请提供公司信息'}), 400
            
            # 检查公司是否存在
            company_configs_dir = config.get_path('config') / 'companies'
            company_file = company_configs_dir / f'{company_id}.json'
            
            if not company_file.exists():
                return jsonify({'success': False, 'error': '公司不存在'}), 404
            
            # 读取现有公司数据
            with open(company_file, 'r', encoding='utf-8') as f:
                existing_company = json.load(f)
            
            # 更新字段
            company_name = data.get('companyName', '').strip()
            if company_name:
                existing_company['companyName'] = company_name
            
            # 更新其他所有字段
            field_mapping = {
                'establishDate': 'establishDate',
                'legalRepresentative': 'legalRepresentative',
                'legalRepresentativePosition': 'legalRepresentativePosition',
                'socialCreditCode': 'socialCreditCode',
                'authorizedPersonName': 'authorizedPersonName',
                'authorizedPersonPosition': 'authorizedPersonPosition',
                'email': 'email',
                'registeredCapital': 'registeredCapital',
                'companyType': 'companyType',
                'fixedPhone': 'fixedPhone',
                'fax': 'fax',
                'postalCode': 'postalCode',
                'registeredAddress': 'registeredAddress',
                'officeAddress': 'officeAddress',
                'website': 'website',
                'employeeCount': 'employeeCount',
                'companyDescription': 'companyDescription',
                'businessScope': 'businessScope',
                'bankName': 'bankName',
                'bankAccount': 'bankAccount'
            }
            
            for field_name, data_key in field_mapping.items():
                if data_key in data:
                    existing_company[field_name] = data[data_key]
            
            # 更新时间戳
            existing_company['updated_at'] = datetime.now().isoformat()
            
            # 保存更新后的公司信息
            with open(company_file, 'w', encoding='utf-8') as f:
                json.dump(existing_company, f, ensure_ascii=False, indent=2)
            
            logger.info(f"更新公司成功: {company_name or existing_company.get('companyName', '')} (ID: {company_id})")
            return jsonify({'success': True, 'company': existing_company, 'message': '公司信息更新成功'})
            
        except Exception as e:
            logger.error(f"更新公司失败: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/companies/<company_id>', methods=['DELETE'])
    def delete_company(company_id):
        """删除公司"""
        try:
            company_configs_dir = config.get_path('config') / 'companies'
            company_file = company_configs_dir / f'{company_id}.json'
            
            if not company_file.exists():
                return jsonify({'success': False, 'error': '公司不存在'}), 404
            
            # 删除公司文件
            company_file.unlink()
            
            logger.info(f"删除公司成功: {company_id}")
            return jsonify({'success': True, 'message': '公司删除成功'})
            
        except Exception as e:
            logger.error(f"删除公司失败: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/companies/<company_id>/qualifications')
    def get_company_qualifications(company_id):
        """获取公司资质文件列表"""
        try:
            import json
            
            # 获取公司信息
            company_configs_dir = config.get_path('config') / 'companies'
            company_file = company_configs_dir / f'{company_id}.json'
            
            if not company_file.exists():
                logger.error(f"公司文件不存在: {company_file}")
                return jsonify({'success': False, 'error': '公司不存在'}), 404
                
            with open(company_file, 'r', encoding='utf-8') as f:
                company_data = json.load(f)
            
            # 获取资质文件信息
            qualifications = company_data.get('qualifications', {})
            
            logger.info(f"获取公司 {company_id} 的资质文件列表，共 {len(qualifications)} 个")
            return jsonify({
                'success': True, 
                'qualifications': qualifications
            })
            
        except Exception as e:
            logger.error(f"获取公司资质文件失败: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/companies/<company_id>/qualifications/upload', methods=['POST'])
    def upload_company_qualifications(company_id):
        """上传公司资质文件"""
        try:
            import json
            import shutil
            from werkzeug.utils import secure_filename
            
            # 获取公司信息
            company_configs_dir = config.get_path('config') / 'companies'
            company_file = company_configs_dir / f'{company_id}.json'
            
            if not company_file.exists():
                return jsonify({'success': False, 'error': '公司不存在'}), 404
                
            with open(company_file, 'r', encoding='utf-8') as f:
                company_data = json.load(f)
            
            # 创建资质文件目录
            qualifications_dir = company_configs_dir / 'qualifications' / company_id
            qualifications_dir.mkdir(parents=True, exist_ok=True)
            
            # 处理上传的文件
            uploaded_files = {}
            qualification_names = request.form.get('qualification_names', '{}')
            qualification_names = json.loads(qualification_names) if qualification_names else {}
            
            for key, file in request.files.items():
                if key.startswith('qualifications[') and file.filename:
                    # 提取资质键名
                    qual_key = key.replace('qualifications[', '').replace(']', '')
                    
                    # 安全的文件名
                    filename = secure_filename(file.filename)
                    timestamp = int(time.time())
                    safe_filename = f"{timestamp}_{filename}"
                    
                    # 保存文件
                    file_path = qualifications_dir / safe_filename
                    file.save(str(file_path))
                    
                    # 记录文件信息
                    file_info = {
                        'filename': filename,
                        'safe_filename': safe_filename,
                        'upload_time': timestamp,
                        'size': file_path.stat().st_size
                    }
                    
                    # 如果是自定义资质，添加名称
                    if qual_key in qualification_names:
                        file_info['custom_name'] = qualification_names[qual_key]
                    
                    uploaded_files[qual_key] = file_info
            
            # 更新公司信息中的资质文件记录
            if 'qualifications' not in company_data:
                company_data['qualifications'] = {}
            
            company_data['qualifications'].update(uploaded_files)
            
            # 保存公司信息
            with open(company_file, 'w', encoding='utf-8') as f:
                json.dump(company_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"公司 {company_id} 上传了 {len(uploaded_files)} 个资质文件")
            return jsonify({
                'success': True, 
                'message': f'成功上传 {len(uploaded_files)} 个资质文件',
                'uploaded_files': uploaded_files
            })
            
        except Exception as e:
            logger.error(f"上传公司资质文件失败: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/companies/<company_id>/qualifications/<qualification_key>/download')
    def download_qualification_file(company_id, qualification_key):
        """下载公司资质文件"""
        try:
            import json
            
            # 获取公司信息
            company_configs_dir = config.get_path('config') / 'companies'
            company_file = company_configs_dir / f'{company_id}.json'
            
            if not company_file.exists():
                return jsonify({'success': False, 'error': '公司不存在'}), 404
                
            with open(company_file, 'r', encoding='utf-8') as f:
                company_data = json.load(f)
            
            # 检查资质文件信息
            qualifications = company_data.get('qualifications', {})
            if qualification_key not in qualifications:
                return jsonify({'success': False, 'error': '资质文件不存在'}), 404
            
            qualification_info = qualifications[qualification_key]
            
            # 构建文件路径 - 检查多个可能的位置
            safe_filename = qualification_info.get('safe_filename', '')
            
            possible_paths = [
                # 新系统路径
                config.get_path('config') / 'companies' / 'qualifications' / company_id / safe_filename,
                # 项目根目录的qualifications路径  
                Path(__file__).parent.parent.parent / 'qualifications' / company_id / safe_filename
            ]
            
            file_path = None
            for path in possible_paths:
                if path.exists():
                    file_path = path
                    break
            
            if not file_path or not file_path.exists():
                return jsonify({'success': False, 'error': '资质文件不存在'}), 404
            
            # 返回文件
            original_filename = qualification_info.get('original_filename', qualification_info.get('safe_filename', 'qualification_file'))
            logger.info(f"下载资质文件: {original_filename}")
            return send_file(str(file_path), as_attachment=True, download_name=original_filename)
            
        except Exception as e:
            logger.error(f"下载资质文件失败: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    # ===================
    # 商务文件管理API
    # ===================
    
    @app.route('/api/business-files')
    def list_business_files():
        """获取商务应答文件列表"""
        try:
            import os
            from datetime import datetime
            
            files = []
            output_dir = config.get_path('output')
            
            if output_dir.exists():
                for filename in os.listdir(output_dir):
                    if filename.endswith(('.docx', '.doc', '.pdf')):
                        file_path = output_dir / filename
                        try:
                            stat = file_path.stat()
                            files.append({
                                'name': filename,
                                'size': stat.st_size,
                                'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                                'path': str(file_path)
                            })
                        except Exception as e:
                            logger.warning(f"读取文件信息失败 {filename}: {e}")
            
            files.sort(key=lambda x: x.get('modified', ''), reverse=True)
            return jsonify({'success': True, 'files': files})
            
        except Exception as e:
            logger.error(f"获取商务文件列表失败: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    # ===================
    # 项目配置API
    # ===================
    
    @app.route('/api/project-config')
    def get_project_config():
        """获取项目配置信息"""
        try:
            import configparser
            
            # 读取招标信息提取模块生成的配置文件
            config_file = config.get_path('config') / 'tender_config.ini'
            
            if not config_file.exists():
                return jsonify({'success': False, 'error': '项目配置文件不存在'})
                
            ini_config = configparser.ConfigParser(interpolation=None)
            ini_config.read(config_file, encoding='utf-8')
            
            # 提取项目信息
            project_info = {}
            if ini_config.has_section('PROJECT_INFO'):
                project_info = {
                    'projectName': ini_config.get('PROJECT_INFO', 'project_name', fallback=''),
                    'projectNumber': ini_config.get('PROJECT_INFO', 'project_number', fallback=''),
                    'tenderer': ini_config.get('PROJECT_INFO', 'tenderer', fallback=''),
                    'agency': ini_config.get('PROJECT_INFO', 'agency', fallback=''),
                    'biddingMethod': ini_config.get('PROJECT_INFO', 'bidding_method', fallback=''),
                    'biddingLocation': ini_config.get('PROJECT_INFO', 'bidding_location', fallback=''),
                    'biddingTime': ini_config.get('PROJECT_INFO', 'bidding_time', fallback=''),
                }
            
            return jsonify({'success': True, 'projectInfo': project_info})

        except Exception as e:
            logger.error(f"获取项目配置失败: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/tender-config')
    def get_tender_config():
        """获取完整的招标配置信息（包括基本信息、资质要求等）"""
        try:
            import configparser

            # 读取招标信息提取模块生成的配置文件
            config_file = config.get_path('config') / 'tender_config.ini'

            if not config_file.exists():
                return jsonify({'success': False, 'error': '招标配置文件不存在'})

            ini_config = configparser.ConfigParser(interpolation=None)
            ini_config.read(config_file, encoding='utf-8')

            result = {'success': True, 'config': {}}

            # 提取项目基本信息
            if ini_config.has_section('PROJECT_INFO'):
                project_info = {}
                for key, value in ini_config.items('PROJECT_INFO'):
                    project_info[key] = value
                result['config']['project_info'] = project_info

            # 提取资质要求信息
            if ini_config.has_section('QUALIFICATION_REQUIREMENTS'):
                qualification_requirements = {}
                for key, value in ini_config.items('QUALIFICATION_REQUIREMENTS'):
                    # 转换布尔值
                    if value.lower() in ('true', 'false'):
                        qualification_requirements[key] = value.lower() == 'true'
                    else:
                        qualification_requirements[key] = value
                result['config']['qualification_requirements'] = qualification_requirements

            # 提取技术评分信息
            if ini_config.has_section('TECHNICAL_SCORING'):
                technical_scoring = {}
                for key, value in ini_config.items('TECHNICAL_SCORING'):
                    technical_scoring[key] = value
                result['config']['technical_scoring'] = technical_scoring

            logger.info(f"成功读取招标配置文件，包含 {len(result['config'])} 个配置节")
            return jsonify(result)

        except Exception as e:
            logger.error(f"获取招标配置失败: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    # ===================
    # 错误处理
    # ===================
    
    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({'error': 'Not Found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"内部服务器错误: {error}")
        return jsonify({'error': 'Internal Server Error'}), 500
    
    @app.errorhandler(413)
    def file_too_large(error):
        return jsonify({'error': '文件太大'}), 413

def main():
    """主函数"""
    app = create_app()
    config = get_config()
    web_config = config.get_web_config()
    
    print(f"启动AI标书系统Web应用...")
    print(f"访问地址: http://{web_config['host']}:{web_config['port']}")
    
    app.run(
        host=web_config['host'],
        port=web_config['port'],
        debug=web_config['debug']
    )

if __name__ == '__main__':
    main()