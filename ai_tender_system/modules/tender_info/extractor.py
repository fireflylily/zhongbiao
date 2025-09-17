#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
招标信息提取器 - 重构版本
从招标文档中提取项目信息、资质要求和技术评分标准

功能：从招标文档中提取项目信息、资质要求和技术评分标准

  🔧 核心功能模块

  1. 文档读取支持
    - PDF 文件 (使用 PyPDF2)
    - Word 文档 (使用 python-docx)
    - 纯文本文件 (支持 UTF-8 和 GBK 编码)
  2. LLM API 调用
    - 使用 Bearer Token 认证
    - 支持重试机制和指数退避
    - 超时控制和错误处理
  3. 信息提取功能
    - extract_basic_info(): 提取项目基本信息
    - extract_qualification_requirements(): 提取资质要求
    - extract_technical_scoring(): 提取技术评分标准
  4. 安全正则表达式
    - 带超时的正则表达式搜索，防止灾难性回溯
    - 支持大小写忽略模式

  📊 提取的数据类型

  基本信息：
  - 项目名称、编号
  - 招标人、代理机构
  - 采购方式、开标地点时间
  - 中标人数量

  资质要求：
  - 营业执照、纳税资格
  - 业绩要求、授权书
  - 信用查询、承诺书
  - 审计报告、社保劳动合同等

  技术评分：
  - 评分项目名称和分值
  - 评分标准描述
  - 来源位置信息

  🔒 错误处理

  - 自定义异常类型：TenderInfoExtractionError、APIError、FileProcessingError
  - 完整的日志记录系统
  - 配置文件保存功能

  这个模块为"读取信息"页面的后端处理提供了完整的文档分析和信息提取能力。
"""

import requests
import json
import re
import threading
import configparser
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, List, Any

# 导入公共模块
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from common import (
    get_config, get_module_logger, 
    TenderInfoExtractionError, APIError, FileProcessingError
)

class TenderInfoExtractor:
    """招标信息提取器"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.config = get_config()
        self.logger = get_module_logger("tender_info")
        
        # API配置
        api_config = self.config.get_api_config()
        self.api_key = api_key or api_config['api_key']
        self.api_endpoint = api_config['api_endpoint']
        self.model_name = api_config['model_name']
        self.max_tokens = api_config['max_tokens']
        self.timeout = api_config['timeout']
        
        self.logger.info("招标信息提取器初始化完成")
    
    def _timeout_regex_search(self, pattern: str, text: str, timeout: int = 5):
        """带超时的正则表达式搜索，防止灾难性回溯"""
        result = None
        exception = None
        
        def search_target():
            nonlocal result, exception
            try:
                result = re.search(pattern, text)
            except Exception as e:
                exception = e
        
        thread = threading.Thread(target=search_target)
        thread.daemon = True
        thread.start()
        thread.join(timeout)
        
        if thread.is_alive():
            self.logger.warning(f"正则表达式搜索超时，跳过模式: {pattern[:50]}...")
            return None
        
        if exception:
            self.logger.warning(f"正则表达式搜索出错: {str(exception)}")
            return None
            
        return result
    
    def _timeout_regex_search_ignore_case(self, pattern: str, text: str, timeout: int = 5):
        """带超时的正则表达式搜索（忽略大小写）"""
        result = None
        exception = None
        
        def search_target():
            nonlocal result, exception
            try:
                result = re.search(pattern, text, re.IGNORECASE)
            except Exception as e:
                exception = e
        
        thread = threading.Thread(target=search_target)
        thread.daemon = True
        thread.start()
        thread.join(timeout)
        
        if thread.is_alive():
            self.logger.warning(f"正则表达式搜索超时（忽略大小写）: {pattern[:50]}...")
            return None
        
        if exception:
            self.logger.warning(f"正则表达式搜索出错（忽略大小写）: {str(exception)}")
            return None
            
        return result
    
    def llm_callback(self, prompt: str, purpose: str = "应答", max_retries: int = 3) -> str:
        """调用LLM API"""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': self.model_name,
            'messages': [
                {'role': 'user', 'content': prompt}
            ],
            'max_completion_tokens': self.max_tokens,
            'temperature': 1
        }
        
        for attempt in range(max_retries):
            try:
                self.logger.info(f"LLM API调用 - {purpose} (尝试 {attempt + 1}/{max_retries})")
                
                response = requests.post(
                    self.api_endpoint, 
                    headers=headers, 
                    json=data, 
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if 'choices' in result and len(result['choices']) > 0:
                        content = result['choices'][0]['message']['content']
                        self.logger.info(f"LLM API调用成功 - {purpose}")
                        return content
                    else:
                        raise APIError(f"API响应格式异常: {result}")
                else:
                    error_msg = f"API调用失败: {response.status_code} - {response.text}"
                    self.logger.error(error_msg)
                    if attempt == max_retries - 1:
                        raise APIError(error_msg)
                        
            except requests.exceptions.Timeout:
                error_msg = f"API调用超时 - {purpose}"
                self.logger.error(error_msg)
                if attempt == max_retries - 1:
                    raise APIError(error_msg)
                    
            except requests.exceptions.RequestException as e:
                error_msg = f"API请求异常 - {purpose}: {str(e)}"
                self.logger.error(error_msg)
                if attempt == max_retries - 1:
                    raise APIError(error_msg)
            
            # 重试前等待
            if attempt < max_retries - 1:
                import time
                time.sleep(2 ** attempt)  # 指数退避
        
        raise APIError(f"LLM API调用失败 - {purpose} (已重试{max_retries}次)")
    
    def read_document(self, file_path: str) -> str:
        """读取文档内容"""
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                raise FileProcessingError(f"文件不存在: {file_path}")
            
            if file_path.suffix.lower() == '.pdf':
                return self._read_pdf(file_path)
            elif file_path.suffix.lower() in ['.doc', '.docx']:
                return self._read_word(file_path)
            elif file_path.suffix.lower() == '.txt':
                return self._read_text(file_path)
            else:
                raise FileProcessingError(f"不支持的文件格式: {file_path.suffix}")
                
        except Exception as e:
            if isinstance(e, FileProcessingError):
                raise
            else:
                raise FileProcessingError(f"读取文档失败: {str(e)}")
    
    def _read_pdf(self, file_path: Path) -> str:
        """读取PDF文件"""
        try:
            import PyPDF2
            
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                
                if not text.strip():
                    raise FileProcessingError("PDF文件内容为空或无法提取文本")
                
                self.logger.info(f"PDF文件读取成功，共{len(pdf_reader.pages)}页")
                return text
                
        except ImportError:
            raise FileProcessingError("缺少PyPDF2库，无法处理PDF文件")
        except Exception as e:
            raise FileProcessingError(f"PDF文件读取失败: {str(e)}")
    
    def _read_word(self, file_path: Path) -> str:
        """读取Word文件"""
        try:
            from docx import Document
            
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            # 读取表格内容
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        text += cell.text + "\t"
                    text += "\n"
            
            if not text.strip():
                raise FileProcessingError("Word文档内容为空")
            
            self.logger.info(f"Word文档读取成功，共{len(doc.paragraphs)}段落，{len(doc.tables)}表格")
            return text
            
        except ImportError:
            raise FileProcessingError("缺少python-docx库，无法处理Word文件")
        except Exception as e:
            raise FileProcessingError(f"Word文档读取失败: {str(e)}")
    
    def _read_text(self, file_path: Path) -> str:
        """读取文本文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
            
            if not text.strip():
                raise FileProcessingError("文本文件内容为空")
            
            self.logger.info(f"文本文件读取成功，长度: {len(text)}字符")
            return text
            
        except UnicodeDecodeError:
            # 尝试其他编码
            try:
                with open(file_path, 'r', encoding='gbk') as file:
                    text = file.read()
                self.logger.info(f"使用GBK编码读取文本文件成功")
                return text
            except:
                raise FileProcessingError("文本文件编码不支持")
        except Exception as e:
            raise FileProcessingError(f"文本文件读取失败: {str(e)}")
    
    def extract_basic_info(self, text: str) -> Dict[str, str]:
        """提取基本项目信息"""
        try:
            self.logger.info("开始提取基本项目信息")
            
            prompt = f"""
请从以下招标文档中提取基本信息，以JSON格式返回：

文档内容：
{text[:3000]}...

请提取以下信息：
1. project_name: 项目名称
2. project_number: 项目编号
3. tenderer: 招标人
4. agency: 招标代理机构
5. bidding_method: 采购方式
6. bidding_location: 开标地点
7. bidding_time: 开标时间
8. winner_count: 中标人数量

请严格按照JSON格式返回，例如：
{{
  "project_name": "项目名称",
  "project_number": "项目编号",
  "tenderer": "招标人",
  "agency": "代理机构",
  "bidding_method": "公开招标",
  "bidding_location": "开标地点",
  "bidding_time": "开标时间",
  "winner_count": "中标人数"
}}
"""
            
            response = self.llm_callback(prompt, "基本信息提取")
            
            # 解析JSON响应
            try:
                # 提取JSON部分
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                json_str = response[json_start:json_end]
                
                basic_info = json.loads(json_str)
                self.logger.info("基本信息提取成功")
                return basic_info
                
            except json.JSONDecodeError as e:
                self.logger.error(f"解析基本信息JSON失败: {e}")
                return {}
                
        except Exception as e:
            self.logger.error(f"提取基本信息失败: {e}")
            raise TenderInfoExtractionError(f"基本信息提取失败: {str(e)}")
    
    def extract_qualification_requirements(self, text: str) -> Dict[str, Any]:
        """基于关键字匹配的资质要求提取"""
        try:
            self.logger.info("开始提取资质要求（关键字匹配）")

            # 定义资质关键字词典
            qualification_keywords = {
                'business_license': [
                    '营业执照', '企业法人营业执照', '工商营业执照', '统一社会信用代码',
                    '营业执照副本', '企业营业执照', '法人营业执照'
                ],
                'taxpayer_qualification': [
                    '一般纳税人', '增值税纳税人', '纳税资格', '纳税人资格',
                    '增值税专用发票', '纳税人资格认定', '税务登记'
                ],
                'iso9001': [
                    'ISO9001', 'ISO 9001', '质量管理体系认证', '质量管理体系',
                    'ISO9001认证', '质量体系认证'
                ],
                'iso14001': [
                    'ISO14001', 'ISO 14001', '环境管理体系认证', '环境管理体系',
                    'ISO14001认证', '环境体系认证'
                ],
                'iso27001': [
                    'ISO27001', 'ISO 27001', '信息安全管理体系认证', '信息安全管理体系',
                    'ISO27001认证', '信息安全体系认证'
                ],
                'credit_china': [
                    '信用中国', '政府采购信用', '失信被执行人', '信用查询',
                    '黑名单', '信用记录', '诚信记录', '信用状况'
                ],
                'authorization_requirements': [
                    '法定代表人', '授权委托书', '授权书', '被授权人',
                    '授权代表', '委托代理人', '授权人'
                ],
                'audit_report': [
                    '审计报告', '财务审计', '年度审计', '审计证明',
                    '会计师事务所', '注册会计师审计'
                ],
                'social_security': [
                    '社会保险', '社保证明', '社保缴费', '社会保险登记证',
                    '社保登记', '社会保险费'
                ],
                'performance_requirements': [
                    '业绩要求', '类似项目', '成功案例', '项目经验',
                    '业绩证明', '合同业绩', '项目业绩'
                ],
                'commitment_letter': [
                    '承诺书', '承诺函', '声明函', '保证书',
                    '诚信承诺', '质量承诺'
                ],
                'labor_contract': [
                    '劳动合同', '用工合同', '聘用合同', '劳务合同',
                    '员工合同', '用工协议'
                ]
            }

            result = {}
            text_lower = text.lower()

            # 对每种资质类型进行关键字匹配
            for qual_type, keywords in qualification_keywords.items():
                matched = False
                matched_keyword = None
                context = ""

                # 检查是否匹配任一关键字
                for keyword in keywords:
                    if keyword.lower() in text_lower:
                        matched = True
                        matched_keyword = keyword
                        # 提取关键字周围的上下文
                        context = self._extract_context_for_qualification(text, keyword)
                        break

                result[f"{qual_type}_required"] = matched
                result[f"{qual_type}_description"] = context if matched else ""

                if matched:
                    self.logger.info(f"资质匹配成功: {qual_type} - 关键字: {matched_keyword}")

            self.logger.info(f"资质要求提取完成，匹配到 {sum(1 for k, v in result.items() if k.endswith('_required') and v)} 个资质要求")
            return result

        except Exception as e:
            self.logger.error(f"提取资质要求失败: {e}")
            return {}

    def _extract_context_for_qualification(self, text: str, keyword: str) -> str:
        """提取资质要求关键字的上下文描述"""
        try:
            keyword_pos = text.lower().find(keyword.lower())
            if keyword_pos == -1:
                return ""

            # 提取关键字前后的文本作为上下文
            start = max(0, keyword_pos - 100)
            end = min(len(text), keyword_pos + len(keyword) + 200)
            context = text[start:end].strip()

            # 尝试提取完整的句子
            sentences = re.split(r'[。；;]', context)
            for sentence in sentences:
                if keyword.lower() in sentence.lower():
                    return sentence.strip()

            return context[:150] + "..." if len(context) > 150 else context

        except Exception as e:
            self.logger.warning(f"提取上下文失败: {e}")
            return keyword
    
    def extract_technical_scoring(self, text: str) -> Dict[str, Any]:
        """提取技术评分标准"""
        try:
            self.logger.info("开始提取技术评分标准")
            
            prompt = f"""
请从以下招标文档中提取技术评分标准，以JSON格式返回：

文档内容：
{text[:4000]}...

请找出所有技术评分项目，并为每个项目提取以下信息：
1. 评分项目名称
2. 分值/权重
3. 评分标准/要求描述
4. 来源位置

请按以下JSON格式返回：
{{
  "total_score": "技术评分总分",
  "extraction_summary": "提取摘要",
  "items_count": "评分项目数量",
  "item_1_name": "第一个评分项名称",
  "item_1_weight": "第一个评分项分值",
  "item_1_criteria": "第一个评分项标准描述",
  "item_1_source": "第一个评分项来源",
  "item_2_name": "第二个评分项名称",
  "item_2_weight": "第二个评分项分值",
  ...
}}
"""
            
            response = self.llm_callback(prompt, "技术评分提取")
            
            try:
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                json_str = response[json_start:json_end]
                
                scoring_info = json.loads(json_str)
                self.logger.info("技术评分标准提取成功")
                return scoring_info
                
            except json.JSONDecodeError as e:
                self.logger.error(f"解析技术评分JSON失败: {e}")
                return {}
                
        except Exception as e:
            self.logger.error(f"提取技术评分标准失败: {e}")
            return {}
    
    def process_document(self, file_path: str) -> Dict[str, Any]:
        """处理完整文档提取"""
        try:
            self.logger.info(f"开始处理文档: {file_path}")
            
            # 读取文档
            text = self.read_document(file_path)
            
            # 提取各项信息
            basic_info = self.extract_basic_info(text)
            qualification_info = self.extract_qualification_requirements(text)
            # scoring_info = self.extract_technical_scoring(text)  # 暂时屏蔽

            # 合并结果 - 包含基本信息和资质要求
            result = {
                **basic_info,
                **qualification_info,
                'extraction_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'file_path': str(file_path)
            }
            
            # 保存到配置文件
            self.save_to_config(result)
            
            self.logger.info("文档处理完成")
            return result
            
        except Exception as e:
            self.logger.error(f"文档处理失败: {e}")
            raise TenderInfoExtractionError(f"文档处理失败: {str(e)}")
    
    def save_to_config(self, data: Dict[str, Any]) -> None:
        """保存数据到配置文件"""
        try:
            config_file = self.config.get_path('config') / 'tender_config.ini'
            
            config = configparser.ConfigParser()
            
            # 项目基本信息
            config['PROJECT_INFO'] = {}
            for key in ['project_name', 'project_number', 'extraction_time', 
                       'tenderer', 'agency', 'bidding_method', 'bidding_location', 
                       'bidding_time', 'winner_count']:
                if key in data:
                    config['PROJECT_INFO'][key] = str(data[key])
            
            # 资质要求
            config['QUALIFICATION_REQUIREMENTS'] = {}
            qual_keys = [k for k in data.keys() if k.endswith('_required') or k.endswith('_description')]
            for key in qual_keys:
                config['QUALIFICATION_REQUIREMENTS'][key] = str(data[key])
            
            # 技术评分
            config['TECHNICAL_SCORING'] = {}
            scoring_keys = [k for k in data.keys() if k.startswith('total_score') or 
                           k.startswith('extraction_summary') or k.startswith('items_count') or
                           k.startswith('item_')]
            for key in scoring_keys:
                config['TECHNICAL_SCORING'][key] = str(data[key])
            
            # 保存文件
            with open(config_file, 'w', encoding='utf-8') as f:
                config.write(f)
            
            self.logger.info(f"配置已保存到: {config_file}")
            
        except Exception as e:
            self.logger.error(f"保存配置失败: {e}")
            raise TenderInfoExtractionError(f"保存配置失败: {str(e)}")

if __name__ == "__main__":
    # 测试代码
    extractor = TenderInfoExtractor()
    print("招标信息提取器初始化完成")