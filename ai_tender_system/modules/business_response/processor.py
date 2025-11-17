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
from .smart_filler import SmartDocumentFiller  # 新：智能文档填写器
from .table_processor import TableProcessor
from .image_handler import ImageHandler
from .inline_processor import InlineReplyProcessor
from .qualification_matcher import QUALIFICATION_MAPPING

# 保持向后兼容：导入旧的 InfoFiller（如果需要的话）
try:
    from .info_filler import InfoFiller
    LEGACY_INFO_FILLER_AVAILABLE = True
except ImportError:
    LEGACY_INFO_FILLER_AVAILABLE = False

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
        self.smart_filler = SmartDocumentFiller()  # 新：使用智能填写器
        self.table_processor = TableProcessor()
        self.image_handler = ImageHandler()

        # 初始化内联回复处理器（使用指定的模型或默认始皇API）
        self.model_name = model_name or "shihuang-gpt4o-mini"
        self.inline_processor = InlineReplyProcessor(model_name=self.model_name)

        # 初始化案例库和简历库填充器
        try:
            from ..case_library.manager import CaseLibraryManager
            from ..resume_library.manager import ResumeLibraryManager
            from .case_table_filler import CaseTableFiller
            from .resume_table_filler import ResumeTableFiller

            self.case_manager = CaseLibraryManager()
            self.resume_manager = ResumeLibraryManager()
            self.case_filler = CaseTableFiller(self.case_manager, self.image_handler)  # 传入image_handler
            self.resume_filler = ResumeTableFiller(self.resume_manager, self.image_handler)  # 传入image_handler
            self.case_resume_available = True
            self.logger.info("案例库和简历库填充器初始化完成")
        except Exception as e:
            self.logger.warning(f"案例库/简历库填充器初始化失败: {e}")
            self.case_resume_available = False

        self.logger.info(f"商务应答处理器初始化完成，内联回复模型: {self.model_name}")

    def _format_date_for_document(self, date_text: str) -> str:
        """
        格式化日期用于文档填充（去掉时间部分）

        区分场景：
        - 项目管理：保留完整时间（用于提醒用户截止时间）
        - 文档填充：仅保留日期部分（签字日期不需要时间）

        支持格式：
        - 2025年08月27日下午14:30整（北京时间） → 2025年08月27日
        - 2025-08-27 14:30:00 → 2025年08月27日
        - 2025/08/27 → 2025年08月27日
        - 2025.08.27 → 2025年08月27日
        - 2025年08月27日 → 2025年08月27日（已格式化，保持不变）

        Args:
            date_text: 原始日期文本

        Returns:
            格式化后的日期（仅包含年月日）
        """
        if not date_text or date_text.strip() == '':
            return date_text

        import re

        # 移除空格
        date_text_cleaned = re.sub(r'\s+', '', date_text)

        # 1. 匹配常见格式并转换为中文格式
        patterns = [
            (r'(\d{4})-(\d{1,2})-(\d{1,2})', r'\1年\2月\3日'),
            (r'(\d{4})/(\d{1,2})/(\d{1,2})', r'\1年\2月\3日'),
            (r'(\d{4})\.(\d{1,2})\.(\d{1,2})', r'\1年\2月\3日'),
        ]

        for pattern, replacement in patterns:
            if re.match(pattern, date_text_cleaned):
                formatted = re.sub(pattern, replacement, date_text_cleaned)
                self.logger.debug(f"日期格式化: {date_text} → {formatted}")
                return formatted

        # 2. 已经是中文格式，提取"年月日"部分（去掉时间后缀）
        if '年' in date_text_cleaned and '月' in date_text_cleaned:
            # 匹配格式：2025年08月27日下午14:30整（北京时间） → 2025年08月27日
            date_match = re.match(r'(\d{4}年\d{1,2}月\d{1,2}日)', date_text_cleaned)
            if date_match:
                formatted = date_match.group(1)
                if formatted != date_text_cleaned:
                    self.logger.info(f"日期格式化（去除时间后缀）: {date_text} → {formatted}")
                return formatted
            # 已经是纯日期格式，保持不变
            return date_text_cleaned

        # 3. 无法识别的格式，保持原样
        self.logger.warning(f"日期格式无法识别，保持原样: {date_text}")
        return date_text

    def process_business_response(self,
                                 input_file: str,
                                 output_file: str,
                                 company_info: Dict[str, Any],
                                 project_name: str = "",
                                 tender_no: str = "",
                                 date_text: str = "",
                                 image_config: Optional[Dict[str, Any]] = None,
                                 required_quals: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        处理商务应答文档 - 主处理方法（模板驱动）

        Args:
            input_file: 输入文档路径
            output_file: 输出文档路径
            company_info: 完整的公司信息字典
            project_name: 项目名称
            tender_no: 招标编号
            date_text: 日期文本
            image_config: 图片配置（包含所有资质）
            required_quals: 项目资格要求列表（用于追加和统计）

        Returns:
            dict: 处理结果，包含详细统计信息
        """
        try:
            self.logger.info(f"开始处理商务应答文档")
            self.logger.info(f"输入文件: {input_file}")
            self.logger.info(f"输出文件: {output_file}")
            self.logger.info(f"公司名称: {company_info.get('companyName', 'N/A')}")
            self.logger.info(f"项目名称: {project_name}")
            self.logger.info(f"招标编号: {tender_no}")
            self.logger.info(f"日期文本: {date_text}")

            # 直接打开输入文件(避免对output_file的引用问题)
            doc = Document(input_file)

            # 格式化日期用于文档填充（去掉时间部分）
            # 项目管理中保留完整时间，文档填充只需要日期
            formatted_date = self._format_date_for_document(date_text)

            # 准备所有数据（合并公司信息和项目信息）
            all_data = {
                **company_info,  # 公司信息
                'projectName': project_name,
                'projectNumber': tender_no,
                'date': formatted_date  # 使用格式化后的日期
            }

            # ✅ 数据传递确认：检查purchaserName是否包含在all_data中
            if 'purchaserName' in all_data:
                self.logger.info(f"✅ purchaserName已包含在all_data中: {all_data['purchaserName']}")
            else:
                self.logger.warning("⚠️  purchaserName未包含在all_data中")
                self.logger.info(f"📋 all_data可用字段: {list(all_data.keys())}")

            # 第1步：信息填写（使用新的智能填写器）
            self.logger.info("第1步：执行智能信息填写")
            smart_stats = self.smart_filler.fill_document(doc, all_data)

            # 转换统计格式以保持兼容（使用过滤后的未填充字段）
            info_stats = {
                'total_replacements': smart_stats.get('total_filled', 0),
                'total_filled': smart_stats.get('total_filled', 0),  # 添加total_filled
                'pattern_counts': smart_stats.get('pattern_counts', {}),
                'unfilled_fields': smart_stats.get('filtered_unfilled_fields', []),  # 使用过滤后的字段
                'original_unfilled_count': smart_stats.get('original_unfilled_count', 0)  # 原始未填充数量（调试用）
            }
            
            # 第2步：表格处理
            self.logger.info("第2步：执行表格处理")
            # 准备项目信息（使用与all_data一致的键名）
            project_info = {
                'projectName': project_name,
                'projectNumber': tender_no,
                'date': formatted_date  # 使用格式化后的日期，保持一致
            }
            table_stats = self.table_processor.process_tables(doc, company_info, project_info)
            
            # 第3步：图片插入（如果有配置）
            image_stats = {}
            if image_config and any(image_config.values()):
                self.logger.info("第3步：执行图片插入")
                image_stats = self.image_handler.insert_images(doc, image_config, required_quals)

            # 第4步：案例表格填充（如果可用）
            case_stats = {}
            if self.case_resume_available:
                self.logger.info("第4步：执行案例表格填充")
                company_id = company_info.get('company_id')
                if company_id:
                    case_stats = self.case_filler.fill_case_tables(doc, company_id)
                else:
                    self.logger.warning("  ⚠️  缺少company_id,跳过案例表格填充")

            # 第5步：简历表格填充（如果可用）
            resume_stats = {}
            if self.case_resume_available:
                self.logger.info("第5步：执行简历表格填充")
                company_id = company_info.get('company_id')
                if company_id:
                    resume_stats = self.resume_filler.fill_resume_tables(doc, company_id)
                else:
                    self.logger.warning("  ⚠️  缺少company_id,跳过简历表格填充")

            # 保存文档
            doc.save(output_file)
            
            # 合并统计结果
            total_stats = {
                'success': True,
                'output_file': output_file,
                'info_filling': info_stats,
                'table_processing': table_stats,
                'image_insertion': image_stats,
                'case_filling': case_stats,
                'resume_filling': resume_stats,
                'summary': {
                    'total_replacements': info_stats.get('total_replacements', 0),
                    'tables_processed': table_stats.get('tables_processed', 0),
                    'cells_filled': table_stats.get('cells_filled', 0),
                    'images_inserted': image_stats.get('images_inserted', 0) if image_stats else 0,
                    'case_tables_filled': case_stats.get('tables_filled', 0) if case_stats else 0,
                    'case_rows_filled': case_stats.get('rows_filled', 0) if case_stats else 0,
                    'resume_tables_filled': resume_stats.get('tables_filled', 0) if resume_stats else 0,
                    'resume_rows_filled': resume_stats.get('rows_filled', 0) if resume_stats else 0
                },
                'message': self._generate_summary_message(info_stats, table_stats, image_stats, required_quals, case_stats, resume_stats)
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
    
    def process_inline_reply(self, input_file: str, output_file: Optional[str] = None, use_ai: bool = True) -> Dict[str, Any]:
        """
        处理内联回复（原地插入应答）

        特性：
        1. 在原文档每个需求后直接插入应答
        2. 应答内容添加浅灰色底纹标记
        3. 保持原文档格式不变

        Args:
            input_file: 输入文档路径
            output_file: 输出文档路径（可选）
            use_ai: 是否使用AI生成应答（False则使用简单模板）

        Returns:
            dict: 处理结果
        """
        try:
            self.logger.info(f"开始处理内联回复文档")
            self.logger.info(f"输入文件: {input_file}")
            self.logger.info(f"使用模型: {self.model_name}")
            self.logger.info(f"应答模式: {'AI智能应答' if use_ai else '简单模板应答'}")

            # 调用内联处理器，传递use_ai参数
            result = self.inline_processor.process_document(input_file, output_file, use_ai)

            return {
                'success': True,
                'output_file': result['output_file'],
                'model_used': self.model_name,
                'requirements_count': result.get('requirements_count', 0),
                'responses_count': result.get('responses_count', 0),
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

    def _generate_summary_message(self, info_stats: Dict, table_stats: Dict, image_stats: Dict, required_quals: Optional[List[Dict]] = None, case_stats: Optional[Dict] = None, resume_stats: Optional[Dict] = None) -> str:
        """
        生成处理摘要消息（模板驱动，包含详细统计信息）

        Args:
            info_stats: 信息填充统计
            table_stats: 表格处理统计
            image_stats: 图片插入统计（包含filled/missing/appended三类统计）
            required_quals: 项目资格要求列表（用于显示）
            case_stats: 案例表格填充统计（可选）
            resume_stats: 简历表格填充统计（可选）

        Returns:
            完整的处理摘要消息
        """
        messages = []

        # 1. 文字信息处理统计（修正版：只统计真正的数据字段）
        total_fields_filled = info_stats.get('total_filled', 0)
        unfilled_count = len(info_stats.get('unfilled_fields', []))  # 使用过滤后的未填充数量

        if total_fields_filled > 0:
            if unfilled_count > 0:
                # 有未填充字段（真正因数据库无记录）
                messages.append(
                    f"填充了{total_fields_filled}个信息字段"
                    f"（{unfilled_count}个因数据库无记录未填充）"
                )
            else:
                # 所有识别的字段都已填充
                messages.append(f"填充了{total_fields_filled}个信息字段")

        # 2. 表格处理统计
        if table_stats.get('tables_processed', 0) > 0:
            messages.append(f"，处理了{table_stats['tables_processed']}个表格")
        if table_stats.get('cells_filled', 0) > 0:
            messages.append(f"，填充了{table_stats['cells_filled']}个单元格")

        # 3. 图片插入统计（模板驱动三分类统计）
        if image_stats and image_stats.get('images_inserted', 0) > 0:
            total_images_inserted = image_stats.get('images_inserted', 0)
            filled_count = len(image_stats.get('filled_qualifications', []))
            missing_count = len(image_stats.get('missing_qualifications', []))
            appended_count = len(image_stats.get('appended_qualifications', []))

            # 基础统计：插入的总图片数
            if filled_count > 0:
                messages.append(f"。成功填充{filled_count}个资质（{total_images_inserted}张图片）")
            else:
                messages.append(f"。插入了{total_images_inserted}张图片")

            # 追加资质统计
            if appended_count > 0:
                messages.append(f"，追加了{appended_count}个项目要求的资质")

            # 缺失资质统计
            if missing_count > 0:
                messages.append(f"，{missing_count}个模板资质因无文件未填充")

        # 4. 缺失资质详细提示
        if image_stats and image_stats.get('missing_qualifications'):
            missing_quals = image_stats['missing_qualifications']
            if missing_quals:
                # 提取资质名称
                missing_qual_names = [q.get('qual_name', q.get('qual_key', '未知资质')) for q in missing_quals]

                # 添加提示信息
                missing_list = "、".join(missing_qual_names)
                messages.append(
                    f"\n\n⚠️  以下资质模板有占位符但未上传文件：{missing_list}。"
                    f"请在企业信息库中上传相应资质文件。"
                )

        # 5. 案例表格填充统计
        if case_stats and case_stats.get('tables_filled', 0) > 0:
            tables_filled = case_stats.get('tables_filled', 0)
            rows_filled = case_stats.get('rows_filled', 0)
            cases_used = case_stats.get('cases_used', 0)
            images_inserted = case_stats.get('images_inserted', 0)

            # 基础统计
            msg = f"\n填充了{tables_filled}个案例表格，共{rows_filled}行数据（使用{cases_used}个案例）"

            # 图片统计
            if images_inserted > 0:
                msg += f"，插入了{images_inserted}张案例附件图片"

            messages.append(msg)

        # 6. 简历表格填充统计
        if resume_stats and resume_stats.get('tables_filled', 0) > 0:
            tables_filled = resume_stats.get('tables_filled', 0)
            rows_filled = resume_stats.get('rows_filled', 0)
            resumes_used = resume_stats.get('resumes_used', 0)
            images_inserted = resume_stats.get('images_inserted', 0)

            # 基础统计
            msg = f"\n填充了{tables_filled}个简历表格，共{rows_filled}行数据（使用{resumes_used}份简历）"

            # 图片统计
            if images_inserted > 0:
                msg += f"，插入了{images_inserted}张简历附件图片"

            messages.append(msg)

        if not messages:
            return "文档处理完成（未发现需要处理的内容）"

        return "".join(messages)
    
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