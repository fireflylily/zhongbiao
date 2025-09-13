#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
商务应答处理器 - 主协调器
协调信息填写、表格处理、图片插入三个子模块
 采购人、项目名称、项目编号信息从 项目信息配置文件中读取
    公司信息从公司的配置文件中读取。
   商务应答模块重构实施方案                │
     │                                         │
     │ 第一步：目录结构调整                    │
     │                                         │
     │ ai_tender_system/modules/               │
     │ ├── business_response/        #         │
     │ 商务应答（原point_to_point改名）        │
     │ │   ├── __init__.py                     │
     │ │   ├── processor.py          #         │
     │ 主处理器，协调三个子模块                │
     │ │   ├── info_filler.py        #         │
     │ 信息填写模块                            │
     │ │   ├── table_processor.py    #         │
     │ 表格处理模块                            │
     │ │   ├── image_handler.py      #         │
     │ 图片插入模块                            │
     │ │   └── utils.py              #         │
     │ 共享工具函数                            │
     │ └── point_to_point/           #         │
     │ 新建：技术需求点对点回复                │
     │     ├── __init__.py                     │
     │     └── tech_responder.py     #         │
     │ 技术需求回复处理器                      │
     │                                         │
     │ 第二步：信息填写模块(info_filler.py)实  │
     │ 现                                      │
     │                                         │
     │ 2.1 核心字段处理规则                    │
     │                                         │
     │ 供应商名称类（支持多种规则）：          │
     │ - 替换规则：（供应商名称） →       （智慧足迹数据科技有限公司）            │
     │ - 填空规则：供应商名称：____ →      供应商名称：智慧足迹数据科技有限公司    │
     │ - 组合规则：（供应商名称、地址） → （智慧足迹数据科技有限公司、北京市东城区）  │
     │ - 变体处理：公司名称、应答人名称、供应商名称（盖章）等                        │
     │                                         │
     │ 其他信息字段（仅填空）：                │
     │ - 电话、邮箱、地址、邮编、传真等        │
     │ - 支持标签变体（如：邮箱/电子邮件）     │
     │ - 支持格式变化（冒号、空格、占位符）    │
     │                                         │
     │ 2.2 例外处理                            │
     │                                         │
     │ - 跳过"签字"相关字段（法定代表人签字、授权代表人签字）                        │
     │ - 智能日期处理（处理空格、去除多余的年月日）                                  │
     │ - 识别并跳过采购人/招标人信息           │
     │                                         │
     │ 第三步：表格处理模块(table_processor.py │
     │ )                                       │
     │                                         │
     │ - 识别表格中的待填字段                  │
     │ - 保持表格格式不变                      │
     │ - 处理合并单元格                        │
     │ - 支持表格内的字段组合                  │
     │                                         │
     │ 第四步：图片插入模块(image_handler.py)  │
     │                                         │
     │ - 公司公章图片插入                      │
     │ - 资质证明图片插入                      │
     │ - 保持文档布局                          │
     │ - 图片尺寸自适应                        │
     │                                         │
     │ 第五步：技术需求回复模块(tech_responder │
     │ .py)                                    │
     │                                         │
     │ - 恢复原有的技术需求点对点回复功能      │
     │ - 基于需求自动生成技术响应              │
     │ - 支持技术参数匹配                      │
     │ - 技术方案模板填充                      │
     │                                         │
     │ 实施步骤：                              │
     │                                         │
     │ 1. 备份现有代码（5分钟）                │
     │   - 备份当前processor.py                │
     │   - 保存测试用例                        │
     │ 2. 创建新目录结构（10分钟）             │
     │   -                                     │
     │ 重命名point_to_point为business_response │
     │   - 创建新的point_to_point目录          │
     │ 3. 拆分info_filler.py（2小时）          │
     │   - 提取信息填写相关代码                │
     │   - 实现六大规则类型                    │
     │   - 添加例外处理逻辑                    │
     │ 4. 实现table_processor.py（1小时）      │
     │   - 提取表格处理逻辑                    │
     │   - 优化表格识别算法                    │
     │ 5. 实现image_handler.py（1小时）        │
     │   - 实现图片插入功能                    │
     │   - 处理图片定位和缩放                  │
     │ 6. 恢复tech_responder.py（2小时）       │
     │   - 查找原有技术回复代码                │
     │   - 重新实现技术需求响应                │
     │ 7. 集成测试（1小时）                    │
     │   - 测试商务应答三大功能                │
     │   - 验证技术需求回复                    │
     │   - 确保格式保持完整                    │
     │                                         │
     │ 预期效果：                              │
     │                                         │
     │ - 代码结构清晰，每个模块200行以内       │
     │ - 功能独立，便于维护和测试              │
     │ - 恢复丢失的技术需求回复功能            │
     │ - 保持原有的格式处理能力                │
     │ - 提高字段识别准确率到95%+  
"""

import configparser
import json
import re
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List
from docx import Document

# 导入子模块
from .info_filler import InfoFiller
from .table_processor import TableProcessor
from .image_handler import ImageHandler

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
    
    def __init__(self, api_key: Optional[str] = None):
        self.config = get_config()
        self.logger = get_module_logger("business_response")
        
        # API配置
        api_config = self.config.get_api_config()
        self.api_key = api_key or api_config['api_key']
        
        # 初始化子模块
        self.info_filler = InfoFiller()
        self.table_processor = TableProcessor()
        self.image_handler = ImageHandler()
        
        self.logger.info("商务应答处理器初始化完成")
    
    def process_business_response(self, 
                                 input_file: str, 
                                 output_file: str,
                                 company_info: Dict[str, Any],
                                 project_name: str = "",
                                 tender_no: str = "", 
                                 date_text: str = "",
                                 purchaser_name: str = "",
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
            purchaser_name: 采购人名称
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
            # 从项目配置文件读取项目信息
            project_config = self._load_project_config()
            
            # 如果配置文件有信息，优先使用配置文件中的信息
            if project_config:
                project_name = project_config.get('project_name', project_name)
                tender_no = project_config.get('project_number', tender_no) 
                purchaser_name = project_config.get('tenderer', purchaser_name)
                self.logger.info(f"从项目配置文件读取信息:")
                self.logger.info(f"  - 项目名称: {project_name}")
                self.logger.info(f"  - 项目编号: {tender_no}")
                self.logger.info(f"  - 采购人: {purchaser_name}")
            else:
                # 如果没有配置文件且没有传入采购人名称，尝试从项目名称中提取
                if not purchaser_name and project_name:
                    purchaser_name = self._extract_purchaser_from_project_name(project_name)
                    self.logger.info(f"从项目名称提取采购人: {purchaser_name}")
            
            self.logger.info(f"最终使用的采购人名称: {purchaser_name}")
            
            # 复制输入文件到输出文件
            shutil.copy2(input_file, output_file)
            
            # 打开文档
            doc = Document(output_file)
            
            # 准备项目信息
            project_info = {
                'projectName': project_name,
                'projectNumber': tender_no,
                'date': date_text,
                'purchaserName': purchaser_name,
                'projectOwner': purchaser_name  # 作为fallback
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
    
    def _load_project_config(self) -> Dict[str, str]:
        """从项目配置文件中加载项目信息"""
        try:
            # 项目配置文件路径  
            from common.config import Config
            config_manager = Config()
            config_path = config_manager.get_path('config') / 'tender_config.ini'
            
            if not config_path.exists():
                self.logger.warning(f"项目配置文件不存在: {config_path}")
                return {}
            
            # 读取配置文件
            config = configparser.ConfigParser()
            config.read(config_path, encoding='utf-8')
            
            if 'PROJECT_INFO' not in config:
                self.logger.warning("配置文件中没有找到 PROJECT_INFO 部分")
                return {}
            
            project_info = {}
            project_section = config['PROJECT_INFO']
            
            # 提取相关信息
            if 'project_name' in project_section:
                project_info['project_name'] = project_section['project_name']
            if 'project_number' in project_section:
                project_info['project_number'] = project_section['project_number']
            if 'tenderer' in project_section:
                project_info['tenderer'] = project_section['tenderer']  # 采购人
            if 'bidding_time' in project_section:
                project_info['bidding_time'] = project_section['bidding_time']
            
            self.logger.info(f"成功从配置文件加载项目信息: {list(project_info.keys())}")
            return project_info
            
        except Exception as e:
            self.logger.error(f"加载项目配置文件失败: {e}")
            return {}
    
    def _extract_purchaser_from_project_name(self, project_name: str) -> str:
        """从项目名称中提取采购人名称"""
        try:
            # 常见的采购人名称模式
            patterns = [
                # 哈银消金2025年-2027年运营商数据采购项目 -> 哈银消金
                r'^([^0-9]+?)(?:20\d{2}年?|采购|招标)',
                # 北京市教委2025年设备采购项目 -> 北京市教委  
                r'^([^采购招标]+?)(?:采购|招标)',
                # 中国移动浙江分公司数据中心建设项目 -> 中国移动浙江分公司
                r'^([^建设项目]+?)(?:建设|项目)',
                # 通用模式：提取前面的组织名称
                r'^([^0-9]{2,}?)(?:20\d{2}|年|项目|采购|招标|建设)'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, project_name)
                if match:
                    purchaser = match.group(1).strip()
                    # 移除常见的后缀词
                    purchaser = re.sub(r'(有限公司|股份公司|集团|公司)$', '', purchaser)
                    if len(purchaser) >= 2:  # 确保提取的名称合理
                        self.logger.info(f"使用模式 '{pattern}' 提取采购人: '{purchaser}'")
                        return purchaser
            
            # 如果所有模式都没有匹配，返回空字符串
            self.logger.warning(f"无法从项目名称提取采购人: {project_name}")
            return ""
            
        except Exception as e:
            self.logger.error(f"提取采购人名称时出错: {e}")
            return ""
    
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