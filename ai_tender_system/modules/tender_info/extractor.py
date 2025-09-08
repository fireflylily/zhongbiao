# -*- coding: utf-8 -*-
"""
重构后的招标信息提取器
基于新的公共组件重构
"""

import json
import re
import configparser
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# 导入公共组件
from common.config import get_config
from common.llm_client import get_llm_client
from common.document_processor import get_document_processor
from common.logger import get_module_logger, log_performance
from common.exceptions import BusinessLogicError, ValidationError

# 导入本模块的数据模型
from .models import TenderInfo, QualificationRequirements, QualificationRequirement, TechnicalScoring, TechnicalScoringItem


class TenderInfoExtractor:
    """重构后的招标信息提取器"""
    
    def __init__(self, output_dir: Optional[str] = None):
        self.config = get_config()
        self.llm_client = get_llm_client()
        self.document_processor = get_document_processor()
        self.logger = get_module_logger("tender_info")
        
        # 配置输出目录
        self.output_dir = Path(output_dir) if output_dir else Path.cwd()
        self.config_file = self.output_dir / self.config.get('modules.tender_info.config_file', 'tender_config.ini')
    
    @log_performance("tender_info_extraction")
    def extract_from_file(self, file_path: str) -> TenderInfo:
        """从文件提取招标信息"""
        self.logger.info(f"开始提取招标信息: {file_path}")
        
        # 读取文档内容
        try:
            document_content = self.document_processor.process_document(file_path)
            self.logger.info(f"文档读取成功，内容长度: {len(document_content)}")
        except Exception as e:
            self.logger.error(f"文档读取失败: {e}")
            raise BusinessLogicError(f"无法读取文档: {e}")
        
        # 提取基本信息
        tender_info = self._extract_basic_info(document_content)
        tender_info.source_file = file_path
        
        # 提取资质要求
        tender_info.qualification_requirements = self._extract_qualification_requirements(document_content)
        
        # 提取技术评分
        tender_info.technical_scoring = self._extract_technical_scoring(document_content)
        
        # 验证结果
        if not tender_info.is_valid():
            self.logger.warning("提取到的信息可能不完整或无效")
        
        self.logger.info(f"信息提取完成: {tender_info.get_summary()}")
        return tender_info
    
    def _extract_basic_info(self, content: str) -> TenderInfo:
        """提取基本信息"""
        self.logger.info("开始提取基本信息...")
        
        # 第一阶段：正则表达式提取
        regex_result = self._regex_extraction(content)
        
        # 第二阶段：验证提取质量
        missing_fields = self._identify_missing_fields(regex_result)
        
        if missing_fields:
            self.logger.info(f"使用LLM补充缺失字段: {missing_fields}")
            llm_result = self._llm_extraction(content, missing_fields, regex_result)
            final_result = self._merge_results(regex_result, llm_result)
        else:
            final_result = regex_result
        
        return final_result
    
    def _regex_extraction(self, content: str) -> TenderInfo:
        """使用正则表达式提取基本信息"""
        self.logger.debug("执行正则表达式提取...")
        
        tender_info = TenderInfo()
        
        # 定义字段匹配模式
        field_patterns = {
            "project_name": [
                r'\*\*一、项目名称[：:]\*\*\s*([^\n\r*]+)',
                r'一、项目名称[：:]\s*([^\n\r，,*]+)',
                r'项目名称[：:]\s*([^\n\r，,*]+)',
                r'采购项目名称[：:]\s*([^\n\r，,*]+)',
                r'([^，,。\n\r]*(?:采购|项目|服务|招标)[^，,。\n\r]*?)(?:\s|$)',
            ],
            "project_number": [
                r'\*\*二、招标编号[：:]\*\*\s*\*\*([A-Z0-9\-_]+)\*\*',
                r'招标编号[：:]\s*([A-Z0-9\-_]{4,})',
                r'采购编号[：:]\s*([A-Z0-9\-_]{4,})',
                r'项目编号[：:]\s*([A-Z0-9\-_]{4,})',
                r'([A-Z]{2,}-\d{4}-[A-Z]{2,}-\d{4})',
            ],
            "tenderer": [
                r'受([^（）]*?)（招标人）委托',
                r'招标人[：:]\s*([^\n\r，,]+)',
                r'采购人[：:]\s*([^\n\r，,]+)',
                r'委托方[：:]\s*([^\n\r，,]+)',
            ],
            "agency": [
                r'([^（）\n\r]*?)（招标代理机构）',
                r'招标代理[公司机构]*[：:]\s*([^\n\r，,]+)',
                r'代理机构[：:]\s*([^\n\r，,]+)',
            ],
            "bidding_method": [
                r'进行([^。]*?招标)',
                r'投标方式[：:]\s*([^\n\r，,]+)',
                r'招标方式[：:]\s*([^\n\r，,]+)',
                r'采购方式[：:]\s*([^\n\r，,]+)',
            ],
            "bidding_location": [
                r'投标地点[：:]\s*([^\n\r，,。*]+)',
                r'递交地点[：:]\s*([^\n\r，,。]+)',
                r'开标地点[：:]\s*([^\n\r，,。]+)',
            ],
            "bidding_time": [
                r'投标截止时间[：:]\s*([^\n\r*]+)',
                r'递交截止时间[：:]?\s*([^\n\r，,。；]+)',
                r'应答文件递交截止时间[：:]\s*([^\n\r，,。；]+)',
                r'(\d{4}年\d{1,2}月\d{1,2}日[^\n\r，,。；地]*(?:上午|下午|早上|晚上)?\d{1,2}[：:]?\d{0,2}[点时前后]?)',
            ],
            "winner_count": [
                r'预计成交供应商数量[：:]\s*([^\n\r，,]+)',
                r'中标人数量[：:]\s*([^\n\r，,]+)',
                r'预计中标[：:]\s*([^\n\r，,]+)',
            ]
        }
        
        # 对每个字段尝试匹配
        for field, patterns in field_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, content)
                if match:
                    value = match.group(1).strip()
                    
                    # 字段特殊处理
                    if field == "project_number" and not self._is_valid_project_number(value):
                        continue
                    
                    setattr(tender_info, field, value)
                    self.logger.debug(f"正则提取 {field}: {value}")
                    break
        
        return tender_info
    
    def _is_valid_project_number(self, value: str) -> bool:
        """验证项目编号是否有效"""
        # 不能包含中文
        if any('\u4e00' <= char <= '\u9fff' for char in value):
            return False
        
        # 不能是纯年份
        if re.match(r'^(19|20)\d{2}$', value):
            return False
        
        # 必须符合编号格式
        if not re.match(r'^[A-Z0-9\-_]+$', value):
            return False
        
        # 长度检查
        if len(value) < 4 or len(value) > 30:
            return False
        
        return True
    
    def _identify_missing_fields(self, tender_info: TenderInfo) -> List[str]:
        """识别缺失的字段"""
        missing_fields = []
        
        required_fields = ['project_name', 'tenderer', 'bidding_time']
        optional_fields = ['project_number', 'agency', 'bidding_method', 'bidding_location', 'winner_count']
        
        # 检查必填字段
        for field in required_fields:
            if not getattr(tender_info, field, '').strip():
                missing_fields.append(field)
        
        # 检查可选字段（如果大部分都缺失，也需要LLM补充）
        missing_optional = sum(1 for field in optional_fields if not getattr(tender_info, field, '').strip())
        if missing_optional > len(optional_fields) * 0.6:  # 超过60%缺失
            missing_fields.extend([f for f in optional_fields if not getattr(tender_info, f, '').strip()])
        
        return missing_fields
    
    def _llm_extraction(self, content: str, missing_fields: List[str], existing_data: TenderInfo) -> Dict[str, str]:
        """使用LLM提取缺失字段"""
        self.logger.info(f"LLM补充提取字段: {missing_fields}")
        
        field_descriptions = {
            "tenderer": "招标人/采购人/采购单位（发起采购的主体）",
            "agency": "招标代理机构/采购代理机构（如果采购人自行组织则为'未提供'）",
            "bidding_method": "投标方式（如公开招标、竞争性磋商等）",
            "bidding_location": "投标地点/开标地点",
            "bidding_time": "投标截止时间/应答文件递交截止时间",
            "winner_count": "中标人数量/成交供应商数量",
            "project_name": "项目名称/采购项目名称",
            "project_number": "项目编号/招标编号/采购编号（如无明确编号则为'未提供'）"
        }
        
        # 构建针对性提示
        prompt = "请从以下文档中提取招标信息，只需要提取缺失的字段：\n\n"
        
        for field in missing_fields:
            prompt += f"- {field}: {field_descriptions.get(field, '')}\n"
        
        prompt += f"\n请返回JSON格式，只包含上述字段。\n\n文档内容：\n{content}"
        
        try:
            response = self.llm_client.simple_chat(prompt, 
                system_prompt="你是专业的文档信息提取专家，擅长从招标文件中准确提取关键信息。请严格按照JSON格式返回结果。")
            
            # 解析JSON响应
            if "```json" in response:
                json_text = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_text = response.split("```")[1].strip()
            else:
                json_text = response.strip()
            
            result = json.loads(json_text)
            self.logger.info("LLM提取成功")
            return result
            
        except Exception as e:
            self.logger.error(f"LLM提取失败: {e}")
            return {}
    
    def _merge_results(self, regex_result: TenderInfo, llm_result: Dict[str, str]) -> TenderInfo:
        """合并正则和LLM的提取结果"""
        for field, value in llm_result.items():
            if hasattr(regex_result, field) and value and value.strip():
                current_value = getattr(regex_result, field, '')
                if not current_value.strip():  # 只有当前值为空时才使用LLM结果
                    setattr(regex_result, field, value.strip())
                    self.logger.info(f"LLM补充 {field}: {value}")
        
        return regex_result
    
    def _extract_qualification_requirements(self, content: str) -> QualificationRequirements:
        """提取资质要求"""
        self.logger.info("开始提取资质要求...")
        
        qual_req = QualificationRequirements.create_default()
        
        # 资质匹配模式
        qualification_patterns = {
            "business_license": [
                r'营业执照[^\n\r]*?(必须|需要|要求|应当|应|须)',
                r'企业法人营业执照[^\n\r]*?(必须|需要|要求)',
                r'营业执照.*?(副本|原件|复印件)',
            ],
            "taxpayer_qualification": [
                r'纳税人[^\n\r]*?(资格|证明|登记)',
                r'增值税.*?纳税人[^\n\r]*?(资格|证明)',
                r'税务登记[^\n\r]*?证',
            ],
            "performance_requirements": [
                r'业绩[^\n\r]*?(要求|必须|需要)',
                r'类似项目[^\n\r]*?(经验|业绩)',
                r'同类项目[^\n\r]*?(经验|业绩)',
            ],
            "authorization_requirements": [
                r'授权[^\n\r]*?(书|函|委托)',
                r'法人授权[^\n\r]*?书',
                r'委托书[^\n\r]*?(必须|需要)',
            ],
            "credit_china": [
                r'信用中国[^\n\r]*?(查询|报告)',
                r'信用报告[^\n\r]*?(必须|需要)',
                r'信用查询[^\n\r]*?(必须|需要)',
            ],
            "audit_report": [
                r'审计报告[^\n\r]*?(必须|需要)',
                r'财务报告[^\n\r]*?(必须|需要)',
                r'财务状况[^\n\r]*?(报告|证明)',
            ],
            "social_security": [
                r'社保[^\n\r]*?(证明|缴费)',
                r'社会保险[^\n\r]*?(证明|缴费)',
                r'养老保险[^\n\r]*?(证明|缴费)',
            ],
            "labor_contract": [
                r'劳动合同[^\n\r]*?(必须|需要)',
                r'用工合同[^\n\r]*?(必须|需要)',
                r'聘用合同[^\n\r]*?(必须|需要)',
            ]
        }
        
        for qual_field, patterns in qualification_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    # 获取完整的要求描述
                    description = self._extract_requirement_context(content, match)
                    
                    # 更新资质要求
                    if hasattr(qual_req, qual_field):
                        setattr(qual_req, qual_field, 
                                QualificationRequirement(required=True, description=description))
                        self.logger.debug(f"发现资质要求 {qual_field}: {description}")
                    break
        
        return qual_req
    
    def _extract_requirement_context(self, content: str, match: re.Match) -> str:
        """提取资质要求的完整描述"""
        # 获取匹配位置周围的上下文
        start_pos = max(0, match.start() - 50)
        end_pos = min(len(content), match.end() + 100)
        context = content[start_pos:end_pos].strip()
        
        # 查找包含要求的句子
        sentences = re.split(r'[；;。\n]', context)
        for sentence in sentences:
            if match.group(0) in sentence:
                return sentence.strip()
        
        return match.group(0)
    
    @log_performance("technical_scoring_extraction")
    def _extract_technical_scoring(self, content: str) -> TechnicalScoring:
        """提取技术评分信息"""
        self.logger.info("开始提取技术评分信息...")
        
        prompt = """你是专业的招标文件分析师，请从文档中提取技术评分相关信息。

请提取以下内容：
1. 技术评分项目列表（名称、分值、评分标准、来源位置）
2. 技术部分总分
3. 提取情况说明

请返回JSON格式：
```json
{
    "technical_scoring_items": [
        {
            "name": "评分项名称",
            "weight": "权重/分值",
            "criteria": "评分标准",
            "source": "数据来源"
        }
    ],
    "total_technical_score": "技术部分总分",
    "extraction_summary": "提取情况说明"
}
```

文档内容：
""" + content
        
        try:
            response = self.llm_client.simple_chat(prompt, 
                system_prompt="你是专业的招标文件分析师，擅长提取技术评分信息。")
            
            # 解析JSON响应
            if "```json" in response:
                json_text = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_text = response.split("```")[1].strip()
            else:
                json_text = response.strip()
            
            try:
                data = json.loads(json_text)
                
                # 构建技术评分对象
                scoring_items = [
                    TechnicalScoringItem(
                        name=item.get('name', ''),
                        weight=item.get('weight', ''),
                        criteria=item.get('criteria', ''),
                        source=item.get('source', '')
                    ) for item in data.get('technical_scoring_items', [])
                ]
                
                technical_scoring = TechnicalScoring(
                    technical_scoring_items=scoring_items,
                    total_technical_score=data.get('total_technical_score', ''),
                    extraction_summary=data.get('extraction_summary', ''),
                    raw_response=response
                )
                
                self.logger.info(f"技术评分提取成功，包含{len(scoring_items)}个评分项")
                return technical_scoring
                
            except json.JSONDecodeError as e:
                self.logger.warning(f"技术评分JSON解析失败: {e}")
                return TechnicalScoring(
                    technical_scoring_items=[],
                    total_technical_score="解析失败",
                    extraction_summary=f"JSON解析失败: {e}",
                    raw_response=response
                )
        
        except Exception as e:
            self.logger.error(f"技术评分提取失败: {e}")
            return TechnicalScoring.create_empty()
    
    def save_to_config(self, tender_info: TenderInfo) -> str:
        """保存到配置文件"""
        self.logger.info(f"保存配置到: {self.config_file}")
        
        try:
            # 确保目录存在
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 创建配置解析器
            config = configparser.ConfigParser(interpolation=None)
            
            # 基本信息
            config.add_section('PROJECT_INFO')
            config.set('PROJECT_INFO', 'tenderer', tender_info.tenderer)
            config.set('PROJECT_INFO', 'agency', tender_info.agency)
            config.set('PROJECT_INFO', 'bidding_method', tender_info.bidding_method)
            config.set('PROJECT_INFO', 'bidding_location', tender_info.bidding_location)
            config.set('PROJECT_INFO', 'bidding_time', tender_info.bidding_time)
            config.set('PROJECT_INFO', 'winner_count', tender_info.winner_count)
            config.set('PROJECT_INFO', 'project_name', tender_info.project_name)
            config.set('PROJECT_INFO', 'project_number', tender_info.project_number)
            config.set('PROJECT_INFO', 'extraction_time', tender_info.extraction_time.strftime('%Y-%m-%d %H:%M:%S'))
            config.set('PROJECT_INFO', 'source_file', tender_info.source_file)
            
            # 资质要求
            if tender_info.qualification_requirements:
                config.add_section('QUALIFICATION_REQUIREMENTS')
                qual_dict = tender_info.qualification_requirements.to_dict()
                
                for qual_field, qual_info in qual_dict.items():
                    config.set('QUALIFICATION_REQUIREMENTS', f'{qual_field}_required', str(qual_info.get('required', False)))
                    config.set('QUALIFICATION_REQUIREMENTS', f'{qual_field}_description', qual_info.get('description', ''))
            
            # 技术评分
            if tender_info.technical_scoring and tender_info.technical_scoring.technical_scoring_items:
                config.add_section('TECHNICAL_SCORING')
                config.set('TECHNICAL_SCORING', 'total_score', tender_info.technical_scoring.total_technical_score)
                config.set('TECHNICAL_SCORING', 'extraction_summary', tender_info.technical_scoring.extraction_summary)
                config.set('TECHNICAL_SCORING', 'items_count', str(len(tender_info.technical_scoring.technical_scoring_items)))
                
                for i, item in enumerate(tender_info.technical_scoring.technical_scoring_items, 1):
                    config.set('TECHNICAL_SCORING', f'item_{i}_name', item.name)
                    config.set('TECHNICAL_SCORING', f'item_{i}_weight', item.weight)
                    config.set('TECHNICAL_SCORING', f'item_{i}_criteria', item.criteria)
                    config.set('TECHNICAL_SCORING', f'item_{i}_source', item.source)
            
            # 写入文件
            with open(self.config_file, 'w', encoding='utf-8') as f:
                config.write(f)
            
            self.logger.info("配置文件保存成功")
            return str(self.config_file)
            
        except Exception as e:
            self.logger.error(f"保存配置文件失败: {e}")
            raise BusinessLogicError(f"无法保存配置文件: {e}")
    
    def print_results(self, tender_info: TenderInfo):
        """打印提取结果"""
        print("=" * 70)
        print("招标信息提取完成!")
        print("=" * 70)
        print("【基本信息】")
        print(f"项目名称: {tender_info.project_name}")
        print(f"项目编号: {tender_info.project_number}")
        print(f"招标人: {tender_info.tenderer}")
        print(f"招标代理: {tender_info.agency}")
        print(f"投标方式: {tender_info.bidding_method}")
        print(f"投标地点: {tender_info.bidding_location}")
        print(f"投标时间: {tender_info.bidding_time}")
        print(f"中标人数量: {tender_info.winner_count}")
        
        print("-" * 70)
        print("【资质要求】")
        
        if tender_info.qualification_requirements:
            qualification_labels = {
                'business_license': '营业执照',
                'taxpayer_qualification': '纳税人资格',
                'performance_requirements': '业绩要求',
                'authorization_requirements': '授权要求',
                'credit_china': '信用中国',
                'commitment_letter': '承诺函',
                'audit_report': '审计报告',
                'social_security': '社保要求',
                'labor_contract': '劳动合同',
                'other_requirements': '其他要求'
            }
            
            qual_dict = tender_info.qualification_requirements.to_dict()
            for field, label in qualification_labels.items():
                if field in qual_dict:
                    qual_info = qual_dict[field]
                    required_text = "需要提供" if qual_info.get('required', False) else "不需要提供"
                    description = qual_info.get('description', '')
                    
                    if description:
                        print(f"{label}: {required_text} - {description}")
                    else:
                        print(f"{label}: {required_text}")
        
        print("-" * 70)
        print("【技术评分信息】")
        
        if tender_info.technical_scoring and tender_info.technical_scoring.technical_scoring_items:
            print(f"技术总分: {tender_info.technical_scoring.total_technical_score}")
            print(f"评分项数量: {len(tender_info.technical_scoring.technical_scoring_items)}个")
            
            for i, item in enumerate(tender_info.technical_scoring.technical_scoring_items, 1):
                print(f"")
                print(f"评分项 {i}:")
                print(f"  名称: {item.name}")
                print(f"  分值: {item.weight}")
                print(f"  标准: {item.criteria}")
                print(f"  来源: {item.source}")
        else:
            print("未找到技术评分信息")
        
        print("=" * 70)


def extract_tender_info(file_path: str, output_dir: Optional[str] = None) -> TenderInfo:
    """便捷函数：提取招标信息"""
    extractor = TenderInfoExtractor(output_dir)
    return extractor.extract_from_file(file_path)