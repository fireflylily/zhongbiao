#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档处理统一入口 - 整合所有文档处理功能
Author: AI标书平台开发团队
Date: 2024-12-09
"""

import os
import json
import logging
from typing import Dict, Optional, List, Tuple
from dataclasses import dataclass
import datetime

# 导入各个处理模块
try:
    from mcp_bidder_name_processor_enhanced import MCPBidderNameProcessorEnhanced
except ImportError:
    MCPBidderNameProcessorEnhanced = None
    
from table_processor import TableProcessor
from image_inserter import SmartImageInserter

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ProcessingOptions:
    """处理选项"""
    process_names: bool = True  # 处理投标人名称
    process_tables: bool = True  # 处理表格
    insert_images: bool = True  # 插入图片
    keep_intermediate: bool = False  # 保留中间文件
    output_dir: Optional[str] = None  # 输出目录


@dataclass
class ProcessingResult:
    """处理结果"""
    success: bool
    input_path: str
    output_path: str
    processing_time: float
    statistics: Dict
    errors: List[str]


class DocumentProcessor:
    """文档处理统一入口类"""
    
    def __init__(self, config_dir: str = None):
        """
        初始化文档处理器
        
        Args:
            config_dir: 配置文件目录
        """
        self.config_dir = config_dir or os.path.join(
            os.path.dirname(__file__), 'config'
        )
        
        # 加载配置
        self.config = self._load_main_config()
        
        # 初始化各个处理模块
        self._init_processors()
        
    def _load_main_config(self) -> Dict:
        """加载主配置文件"""
        config_path = os.path.join(self.config_dir, 'document_processing_config.json')
        
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # 默认配置
        return {
            "enabled_modules": {
                "name_processor": True,
                "table_processor": True,
                "image_inserter": True
            },
            "processing_order": [
                "name_processor",
                "table_processor",
                "image_inserter"
            ],
            "output_settings": {
                "create_backup": True,
                "use_timestamp": True,
                "output_dir": "outputs/complete"
            }
        }
    
    def _init_processors(self):
        """初始化各个处理器"""
        # 名称处理器（如果可用）
        if MCPBidderNameProcessorEnhanced and self.config['enabled_modules'].get('name_processor'):
            try:
                self.name_processor = MCPBidderNameProcessorEnhanced()
                logger.info("名称处理器已初始化")
            except Exception as e:
                logger.warning(f"名称处理器初始化失败: {str(e)}")
                self.name_processor = None
        else:
            self.name_processor = None
        
        # 表格处理器
        if self.config['enabled_modules'].get('table_processor'):
            try:
                table_config_path = os.path.join(self.config_dir, 'table_config.json')
                self.table_processor = TableProcessor(table_config_path)
                logger.info("表格处理器已初始化")
            except Exception as e:
                logger.error(f"表格处理器初始化失败: {str(e)}")
                self.table_processor = None
        else:
            self.table_processor = None
        
        # 图片插入器
        if self.config['enabled_modules'].get('image_inserter'):
            try:
                image_config_path = os.path.join(self.config_dir, 'image_config.json')
                self.image_inserter = SmartImageInserter(image_config_path)
                logger.info("图片插入器已初始化")
            except Exception as e:
                logger.error(f"图片插入器初始化失败: {str(e)}")
                self.image_inserter = None
        else:
            self.image_inserter = None
    
    def process_document(self, doc_path: str, company_info: Dict, 
                        options: ProcessingOptions = None) -> ProcessingResult:
        """
        处理文档的统一入口方法
        
        Args:
            doc_path: 文档路径
            company_info: 公司信息
            options: 处理选项
            
        Returns:
            处理结果
        """
        start_time = datetime.datetime.now()
        options = options or ProcessingOptions()
        
        # 验证输入
        if not os.path.exists(doc_path):
            return ProcessingResult(
                success=False,
                input_path=doc_path,
                output_path="",
                processing_time=0,
                statistics={},
                errors=[f"文档不存在: {doc_path}"]
            )
        
        # 准备统计信息
        statistics = {
            'name_replacements': 0,
            'tables_processed': 0,
            'fields_filled': 0,
            'images_inserted': 0
        }
        errors = []
        
        try:
            current_path = doc_path
            
            # 1. 处理投标人名称（如果启用）
            if options.process_names and self.name_processor:
                try:
                    logger.info("开始处理投标人名称...")
                    result = self.name_processor.process_document(
                        current_path, 
                        company_info.get('companyName', '')
                    )
                    
                    if result['success']:
                        current_path = result['output_file']
                        statistics['name_replacements'] = result.get('replacement_count', 0)
                        logger.info(f"名称处理完成，替换 {statistics['name_replacements']} 处")
                    else:
                        errors.append("名称处理失败")
                        
                except Exception as e:
                    logger.error(f"名称处理异常: {str(e)}")
                    errors.append(f"名称处理异常: {str(e)}")
            
            # 2. 处理表格（如果启用）
            if options.process_tables and self.table_processor:
                try:
                    logger.info("开始处理表格...")
                    current_path = self.table_processor.process_document(
                        current_path,
                        company_info
                    )
                    
                    # 获取表格处理统计
                    analysis = self.table_processor.analyze_tables(doc_path)
                    statistics['tables_processed'] = analysis['total_tables']
                    statistics['fields_filled'] = sum(
                        len(t['matched_fields']) for t in analysis['tables']
                    )
                    logger.info(f"表格处理完成，处理 {statistics['tables_processed']} 个表格")
                    
                except Exception as e:
                    logger.error(f"表格处理异常: {str(e)}")
                    errors.append(f"表格处理异常: {str(e)}")
            
            # 3. 插入图片（如果启用）
            if options.insert_images and self.image_inserter:
                try:
                    logger.info("开始插入图片...")
                    current_path, insertion_results = self.image_inserter.process_document(
                        current_path,
                        company_info
                    )
                    
                    statistics['images_inserted'] = sum(
                        1 for r in insertion_results if r.success
                    )
                    logger.info(f"图片插入完成，插入 {statistics['images_inserted']} 张图片")
                    
                except Exception as e:
                    logger.error(f"图片插入异常: {str(e)}")
                    errors.append(f"图片插入异常: {str(e)}")
            
            # 4. 最终输出处理
            final_path = self._finalize_output(
                current_path, 
                doc_path, 
                options
            )
            
            # 计算处理时间
            processing_time = (datetime.datetime.now() - start_time).total_seconds()
            
            # 返回结果
            return ProcessingResult(
                success=len(errors) == 0,
                input_path=doc_path,
                output_path=final_path,
                processing_time=processing_time,
                statistics=statistics,
                errors=errors
            )
            
        except Exception as e:
            logger.error(f"文档处理失败: {str(e)}")
            return ProcessingResult(
                success=False,
                input_path=doc_path,
                output_path="",
                processing_time=(datetime.datetime.now() - start_time).total_seconds(),
                statistics=statistics,
                errors=[f"处理失败: {str(e)}"]
            )
    
    def _finalize_output(self, current_path: str, original_path: str, 
                        options: ProcessingOptions) -> str:
        """最终输出处理"""
        # 确定输出目录
        if options.output_dir:
            output_dir = options.output_dir
        else:
            output_dir = self.config['output_settings'].get('output_dir', 'outputs/complete')
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成最终文件名
        base_name = os.path.basename(original_path)
        name, ext = os.path.splitext(base_name)
        
        if self.config['output_settings'].get('use_timestamp', True):
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            final_name = f"{name}_完整处理_{timestamp}{ext}"
        else:
            final_name = f"{name}_完整处理{ext}"
        
        final_path = os.path.join(output_dir, final_name)
        
        # 如果需要，移动文件到最终位置
        if current_path != final_path:
            import shutil
            shutil.copy2(current_path, final_path)
            
            # 删除中间文件（如果不保留）
            if not options.keep_intermediate and current_path != original_path:
                try:
                    os.remove(current_path)
                except:
                    pass
        
        logger.info(f"最终文档已保存: {final_path}")
        return final_path
    
    def batch_process(self, doc_paths: List[str], company_info: Dict,
                     options: ProcessingOptions = None) -> List[ProcessingResult]:
        """
        批量处理文档
        
        Args:
            doc_paths: 文档路径列表
            company_info: 公司信息
            options: 处理选项
            
        Returns:
            处理结果列表
        """
        results = []
        total = len(doc_paths)
        
        for idx, doc_path in enumerate(doc_paths, 1):
            logger.info(f"处理进度: {idx}/{total} - {os.path.basename(doc_path)}")
            
            result = self.process_document(doc_path, company_info, options)
            results.append(result)
            
            # 记录结果
            if result.success:
                logger.info(f"✓ 成功: {os.path.basename(doc_path)}")
            else:
                logger.error(f"✗ 失败: {os.path.basename(doc_path)} - {result.errors}")
        
        # 汇总统计
        success_count = sum(1 for r in results if r.success)
        logger.info(f"批量处理完成: {success_count}/{total} 成功")
        
        return results
    
    def load_company_info(self, company_id: str) -> Dict:
        """
        加载公司信息
        
        Args:
            company_id: 公司ID
            
        Returns:
            公司信息字典
        """
        # 从配置目录加载公司信息
        company_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'company_configs'
        )
        
        company_file = os.path.join(company_dir, f"{company_id}.json")
        
        if os.path.exists(company_file):
            with open(company_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        logger.warning(f"公司配置文件不存在: {company_file}")
        return {}


# 便捷函数
def process_single_document(doc_path: str, company_id: str, **kwargs) -> ProcessingResult:
    """
    便捷函数：处理单个文档
    
    Args:
        doc_path: 文档路径
        company_id: 公司ID
        **kwargs: 其他选项
        
    Returns:
        处理结果
    """
    processor = DocumentProcessor()
    company_info = processor.load_company_info(company_id)
    
    options = ProcessingOptions(
        process_names=kwargs.get('process_names', True),
        process_tables=kwargs.get('process_tables', True),
        insert_images=kwargs.get('insert_images', True),
        keep_intermediate=kwargs.get('keep_intermediate', False),
        output_dir=kwargs.get('output_dir')
    )
    
    return processor.process_document(doc_path, company_info, options)


# 测试代码
if __name__ == "__main__":
    # 示例公司信息
    test_company_info = {
        "companyName": "智慧科技有限公司",
        "establishDate": "2015-12-18",
        "legalRepresentative": "张三",
        "registeredCapital": "10000000",
        "businessScope": "软件开发、技术服务、技术咨询",
        "companyAddress": "北京市海淀区中关村大街1号",
        "contactPhone": "010-12345678",
        "email": "contact@example.com",
        "socialCreditCode": "91110108MA00XXXX00",
        "bankName": "中国工商银行北京分行",
        "bankAccount": "1234567890123456789",
        "qualifications": {
            "business_license_path": "/path/to/business_license.jpg",
            "qualification_cert_path": "/path/to/qualification.jpg",
            "legal_person_id_path": "/path/to/id.jpg"
        }
    }
    
    # 创建处理器
    processor = DocumentProcessor()
    
    # 测试单个文档处理
    test_doc = "test_complete.docx"
    if os.path.exists(test_doc):
        options = ProcessingOptions(
            process_names=True,
            process_tables=True,
            insert_images=True
        )
        
        result = processor.process_document(test_doc, test_company_info, options)
        
        print(f"处理结果:")
        print(f"  成功: {result.success}")
        print(f"  输出文件: {result.output_path}")
        print(f"  处理时间: {result.processing_time:.2f}秒")
        print(f"  统计信息: {result.statistics}")
        if result.errors:
            print(f"  错误: {result.errors}")
    
    # 测试批量处理
    test_docs = ["test1.docx", "test2.docx", "test3.docx"]
    existing_docs = [doc for doc in test_docs if os.path.exists(doc)]
    
    if existing_docs:
        results = processor.batch_process(existing_docs, test_company_info)
        
        print(f"\n批量处理结果:")
        for i, result in enumerate(results, 1):
            print(f"  文档{i}: {'成功' if result.success else '失败'}")