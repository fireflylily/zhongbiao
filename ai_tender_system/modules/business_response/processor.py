#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
商务应答处理器 - 主协调器
协调信息填写、表格处理、图片插入三个子模块
新增内联回复功能（原地插入应答）
"""

import json
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List
from docx import Document

# 导入子模块
from .info_filler import InfoFiller
from .table_processor import TableProcessor
from .image_handler import ImageHandler
from .inline_processor import InlineReplyProcessor

# 导入公共模块
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from common import (
    get_config, get_module_logger,
    BusinessResponseError, APIError, FileProcessingError,
    safe_filename, ensure_dir
)

class BusinessResponseProcessor:
    """商务应答处理器 - 主协调器"""

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        self.config = get_config()
        self.logger = get_module_logger("business_response")

        # API配置
        api_config = self.config.get_api_config()
        self.api_key = api_key or api_config['api_key']

        # 初始化子模块
        self.info_filler = InfoFiller()
        self.table_processor = TableProcessor()
        self.image_handler = ImageHandler()

        # 初始化内联回复处理器（使用指定的模型或默认始皇API）
        self.model_name = model_name or "shihuang-gpt4o-mini"
        self.inline_processor = InlineReplyProcessor(model_name=self.model_name)

        self.logger.info(f"商务应答处理器初始化完成，内联回复模型: {self.model_name}")
    
    def process_business_response(self, 
                                 input_file: str, 
                                 output_file: str,
                                 company_info: Dict[str, Any],
                                 project_name: str = "",
                                 tender_no: str = "", 
                                 date_text: str = "",
                                 image_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        处理商务应答文档 - 主处理方法
        
        Args:
            input_file: 输入文档路径
            output_file: 输出文档路径
            company_info: 完整的公司信息字典
            project_name: 项目名称
            tender_no: 招标编号
            date_text: 日期文本
            image_config: 图片配置（可选）
            
        Returns:
            dict: 处理结果
        """
        try:
            self.logger.info(f"开始处理商务应答文档")
            self.logger.info(f"输入文件: {input_file}")
            self.logger.info(f"输出文件: {output_file}")
            self.logger.info(f"公司名称: {company_info.get('companyName', 'N/A')}")
            self.logger.info(f"项目名称: {project_name}")
            self.logger.info(f"招标编号: {tender_no}")
            self.logger.info(f"日期文本: {date_text}")
            
            # 复制输入文件到输出文件
            shutil.copy2(input_file, output_file)
            
            # 打开文档
            doc = Document(output_file)
            
            # 准备项目信息
            project_info = {
                'projectName': project_name,
                'projectNumber': tender_no,
                'date': date_text
            }
            
            # 第1步：信息填写（核心功能）
            self.logger.info("第1步：执行信息填写")
            info_stats = self.info_filler.fill_info(doc, company_info, project_info)
            
            # 第2步：表格处理
            self.logger.info("第2步：执行表格处理")
            table_stats = self.table_processor.process_tables(doc, company_info, project_info)
            
            # 第3步：图片插入（如果有配置）
            image_stats = {}
            if image_config and any(image_config.values()):
                self.logger.info("第3步：执行图片插入")
                image_stats = self.image_handler.insert_images(doc, image_config)
            
            # 保存文档
            doc.save(output_file)
            
            # 合并统计结果
            total_stats = {
                'success': True,
                'output_file': output_file,
                'info_filling': info_stats,
                'table_processing': table_stats,
                'image_insertion': image_stats,
                'summary': {
                    'total_replacements': info_stats.get('total_replacements', 0),
                    'tables_processed': table_stats.get('tables_processed', 0),
                    'cells_filled': table_stats.get('cells_filled', 0),
                    'images_inserted': image_stats.get('images_inserted', 0) if image_stats else 0
                },
                'message': self._generate_summary_message(info_stats, table_stats, image_stats)
            }
            
            self.logger.info(f"商务应答文档处理完成: {total_stats['message']}")
            
            return total_stats
            
        except Exception as e:
            self.logger.error(f"商务应答文档处理失败: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return {
                'success': False,
                'error': f'处理失败: {str(e)}',
                'message': '处理失败'
            }
    
    def process_inline_reply(self, input_file: str, output_file: Optional[str] = None) -> Dict[str, Any]:
        """
        处理内联回复（原地插入应答）

        特性：
        1. 在原文档每个需求后直接插入应答
        2. 应答内容添加浅灰色底纹标记
        3. 保持原文档格式不变

        Args:
            input_file: 输入文档路径
            output_file: 输出文档路径（可选）

        Returns:
            dict: 处理结果
        """
        try:
            self.logger.info(f"开始处理内联回复文档")
            self.logger.info(f"输入文件: {input_file}")
            self.logger.info(f"使用模型: {self.model_name}")

            # 调用内联处理器
            result_file = self.inline_processor.process_document(input_file, output_file)

            return {
                'success': True,
                'output_file': result_file,
                'model_used': self.model_name,
                'features': {
                    'inline_reply': True,
                    'gray_shading': True,
                    'format_preserved': True
                },
                'message': f'内联回复处理完成，已在原文档中插入应答'
            }

        except Exception as e:
            self.logger.error(f"内联回复处理失败: {e}")
            return {
                'success': False,
                'error': f'处理失败: {str(e)}',
                'message': '内联回复处理失败'
            }

    def _generate_summary_message(self, info_stats: Dict, table_stats: Dict, image_stats: Dict) -> str:
        """生成处理摘要消息"""
        messages = []

        if info_stats.get('total_replacements', 0) > 0:
            messages.append(f"填充了{info_stats['total_replacements']}个信息字段")

        if table_stats.get('tables_processed', 0) > 0:
            messages.append(f"处理了{table_stats['tables_processed']}个表格")

        if table_stats.get('cells_filled', 0) > 0:
            messages.append(f"填充了{table_stats['cells_filled']}个单元格")

        if image_stats and image_stats.get('images_inserted', 0) > 0:
            messages.append(f"插入了{image_stats['images_inserted']}张图片")

        if not messages:
            return "文档处理完成（未发现需要处理的内容）"

        return "，".join(messages)
    
    def validate_input(self, input_file: str, company_info: Dict[str, Any]) -> Dict[str, Any]:
        """验证输入参数"""
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # 验证输入文件
        if not Path(input_file).exists():
            validation_result['valid'] = False
            validation_result['errors'].append(f"输入文件不存在: {input_file}")
        elif not input_file.endswith(('.docx', '.doc')):
            validation_result['valid'] = False
            validation_result['errors'].append("输入文件必须是Word文档")
        
        # 验证公司信息
        required_fields = ['companyName']
        for field in required_fields:
            if not company_info.get(field):
                validation_result['warnings'].append(f"缺少必填字段: {field}")
        
        # 验证推荐字段
        recommended_fields = ['address', 'phone', 'email', 'legalRepresentative']
        missing_recommended = []
        for field in recommended_fields:
            if not company_info.get(field):
                missing_recommended.append(field)
        
        if missing_recommended:
            validation_result['warnings'].append(f"缺少推荐字段: {', '.join(missing_recommended)}")
        
        return validation_result
    
    def get_supported_fields(self) -> Dict[str, List[str]]:
        """获取支持的字段列表"""
        return {
            'company_fields': [
                'companyName', 'address', 'registeredAddress', 'officeAddress',
                'phone', 'fixedPhone', 'email', 'fax', 'postalCode',
                'legalRepresentative', 'socialCreditCode', 'registeredCapital',
                'establishDate', 'bankName', 'bankAccount', 'taxNumber'
            ],
            'project_fields': [
                'projectName', 'projectNumber', 'date', 'bidPrice',
                'deliveryTime', 'warrantyPeriod'
            ],
            'image_fields': [
                'seal_path', 'license_path', 'qualification_paths'
            ]
        }


# 保持向后兼容性
class PointToPointProcessor(BusinessResponseProcessor):
    """向后兼容的别名"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger.warning("PointToPointProcessor已更名为BusinessResponseProcessor，请更新代码")