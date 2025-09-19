#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
技术需求回复模块 - 处理招标文件中的技术需求点对点回复
根据技术需求自动生成技术响应文档
"""

import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
import requests

# 导入公共模块
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from common import (
    get_config, get_module_logger,
    APIError, FileProcessingError,
    ensure_dir
)
from common.llm_client import create_llm_client

class TechResponder:
    """技术需求回复处理器"""
    
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gpt-4o-mini"):
        self.config = get_config()
        self.logger = get_module_logger("tech_responder")

        # 创建LLM客户端
        self.llm_client = create_llm_client(model_name, api_key)

        # 保持向后兼容性的配置
        api_config = self.config.get_api_config()
        self.api_key = api_key or api_config['api_key']
        self.api_endpoint = api_config.get('api_endpoint', 'https://api.openai.com/v1/chat/completions')
        self.model_name = model_name

        self.logger.info(f"技术需求回复处理器初始化完成，使用模型: {model_name}")
    
    def process_tech_requirements(self,
                                 requirements_file: str,
                                 output_file: str,
                                 company_info: Dict[str, Any],
                                 response_strategy: str = "comprehensive",
                                 response_frequency: str = "every_paragraph",
                                 response_mode: str = "simple",
                                 ai_model: str = "gpt-4o-mini") -> Dict[str, Any]:
        """
        处理技术需求并生成回复文档

        Args:
            requirements_file: 技术需求文档路径
            output_file: 输出文档路径
            company_info: 公司信息
            response_strategy: 回复策略 (comprehensive/concise/detailed)
            response_frequency: 应答频次 (every_paragraph/major_headings)
            response_mode: 应答方式 (simple/ai)
            ai_model: AI模型 (gpt-4o-mini/unicom-yuanjing)

        Returns:
            处理结果统计
        """
        try:
            self.logger.info(f"开始处理技术需求文档: {requirements_file}")
            self.logger.info(f"配置参数 - 应答频次: {response_frequency}, 应答方式: {response_mode}, AI模型: {ai_model}")

            # 第1步：提取技术需求
            requirements = self._extract_requirements(requirements_file, response_frequency)
            self.logger.info(f"提取到{len(requirements)}个技术需求")

            # 第2步：生成技术响应
            responses = self._generate_responses(requirements, company_info, response_strategy, response_mode, ai_model)
            
            # 第3步：创建响应文档
            self._create_response_document(responses, output_file, company_info)
            
            stats = {
                'success': True,
                'requirements_count': len(requirements),
                'responses_count': len(responses),
                'output_file': output_file,
                'message': f'成功处理{len(requirements)}个技术需求'
            }
            
            self.logger.info(f"技术需求处理完成: {stats['message']}")
            return stats
            
        except Exception as e:
            self.logger.error(f"技术需求处理失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': '处理失败'
            }
    
    def _extract_requirements(self, requirements_file: str, response_frequency: str = "every_paragraph") -> List[Dict[str, Any]]:
        """从文档中提取技术需求"""
        requirements = []
        
        try:
            doc = Document(requirements_file)
            current_section = ""
            requirement_id = 1
            
            for paragraph in doc.paragraphs:
                text = paragraph.text.strip()
                if not text:
                    continue
                
                # 识别章节标题
                if self._is_section_title(text):
                    current_section = text
                    continue
                
                # 识别技术需求点
                if self._is_requirement(text):
                    # 根据应答频次过滤
                    if response_frequency == "major_headings":
                        # 只对大标题条目应答，跳过段落级别的需求
                        if not self._is_major_heading(text):
                            continue

                    requirement = {
                        'id': requirement_id,
                        'section': current_section,
                        'content': text,
                        'type': self._classify_requirement(text)
                    }
                    requirements.append(requirement)
                    requirement_id += 1
                    self.logger.debug(f"提取需求#{requirement_id}: {text[:50]}...")
            
            # 也从表格中提取需求
            for table in doc.tables:
                table_requirements = self._extract_table_requirements(table)
                for req in table_requirements:
                    req['id'] = requirement_id
                    requirements.append(req)
                    requirement_id += 1
            
        except Exception as e:
            self.logger.error(f"提取需求失败: {e}")
            raise
        
        return requirements
    
    def _is_section_title(self, text: str) -> bool:
        """判断是否为章节标题"""
        patterns = [
            r'^\d+\.\s+',  # 1. 标题
            r'^第[一二三四五六七八九十]+[章节部分]',  # 第一章
            r'^[一二三四五六七八九十]+、',  # 一、标题
        ]
        
        for pattern in patterns:
            if re.match(pattern, text):
                return True
        
        # 检查是否包含关键词
        title_keywords = ['技术要求', '功能要求', '性能要求', '安全要求', '接口要求']
        return any(keyword in text for keyword in title_keywords)
    
    def _is_requirement(self, text: str) -> bool:
        """判断是否为技术需求"""
        # 需求通常包含的关键词
        requirement_keywords = [
            '应', '必须', '需要', '要求', '支持', '提供', '实现',
            '具备', '满足', '确保', '保证', '能够', '可以'
        ]
        
        return any(keyword in text for keyword in requirement_keywords)
    
    def _classify_requirement(self, text: str) -> str:
        """对需求进行分类"""
        if any(word in text for word in ['功能', '模块', '组件']):
            return 'functional'
        elif any(word in text for word in ['性能', '响应', '并发', '吞吐']):
            return 'performance'
        elif any(word in text for word in ['安全', '权限', '加密', '认证']):
            return 'security'
        elif any(word in text for word in ['接口', 'API', '集成', '对接']):
            return 'interface'
        elif any(word in text for word in ['数据', '存储', '备份', '恢复']):
            return 'data'
        else:
            return 'general'
    
    def _extract_table_requirements(self, table) -> List[Dict[str, Any]]:
        """从表格中提取需求"""
        requirements = []
        
        # 分析表格结构
        if len(table.rows) < 2:
            return requirements
        
        # 假设第一行是表头
        headers = [cell.text.strip() for cell in table.rows[0].cells]
        
        # 查找需求相关的列
        requirement_col_idx = -1
        for idx, header in enumerate(headers):
            if any(keyword in header for keyword in ['需求', '要求', '功能', '描述']):
                requirement_col_idx = idx
                break
        
        if requirement_col_idx >= 0:
            for row in table.rows[1:]:
                if requirement_col_idx < len(row.cells):
                    req_text = row.cells[requirement_col_idx].text.strip()
                    if req_text and self._is_requirement(req_text):
                        requirements.append({
                            'section': '表格需求',
                            'content': req_text,
                            'type': self._classify_requirement(req_text)
                        })
        
        return requirements
    
    def _generate_responses(self, requirements: List[Dict[str, Any]],
                          company_info: Dict[str, Any],
                          strategy: str,
                          response_mode: str = "simple",
                          ai_model: str = "gpt-4o-mini") -> List[Dict[str, Any]]:
        """生成技术响应"""
        responses = []
        
        for requirement in requirements:
            self.logger.info(f"生成响应 #{requirement['id']}: {requirement['content'][:50]}...")
            
            # 根据需求类型选择响应模板
            response_template = self._get_response_template(requirement['type'])
            
            # 生成具体响应
            if response_mode == "ai" and self.api_key:
                # 使用AI生成响应
                response_text = self._generate_ai_response(requirement, company_info, strategy, ai_model)
            else:
                # 使用模板生成响应
                response_text = self._generate_template_response(requirement, response_template, company_info)
            
            response = {
                'requirement_id': requirement['id'],
                'requirement': requirement['content'],
                'response': response_text,
                'type': requirement['type'],
                'section': requirement['section']
            }
            
            responses.append(response)
        
        return responses
    
    def _get_response_template(self, requirement_type: str) -> str:
        """获取响应模板"""
        templates = {
            'functional': """
我公司完全理解并响应该技术需求。我们的解决方案将：
1. 全面实现所要求的功能
2. 采用成熟稳定的技术架构
3. 确保系统的可扩展性和可维护性
具体实现方案：{details}
            """,
            'performance': """
我公司充分理解性能要求的重要性，承诺：
1. 系统响应时间满足要求
2. 支持并发用户数达到指定要求
3. 提供性能监控和优化方案
技术保障措施：{details}
            """,
            'security': """
我公司高度重视系统安全，将采取以下措施：
1. 实施多层次安全防护体系
2. 采用行业标准的加密算法
3. 建立完善的权限管理机制
安全保障方案：{details}
            """,
            'interface': """
针对接口集成需求，我公司方案包括：
1. 提供标准化的API接口
2. 支持多种数据交换格式
3. 确保接口的稳定性和兼容性
接口设计方案：{details}
            """,
            'data': """
关于数据管理需求，我公司将：
1. 建立完善的数据管理体系
2. 实施数据备份和恢复策略
3. 确保数据的安全性和完整性
数据管理方案：{details}
            """,
            'general': """
我公司完全响应该项技术需求：
1. 严格按照要求实施
2. 提供专业的技术支持
3. 确保达到预期效果
实施方案：{details}
            """
        }
        
        return templates.get(requirement_type, templates['general'])

    def _is_major_heading(self, text: str) -> bool:
        """判断文本是否为大标题条目"""
        # 大标题的特征：
        # 1. 以数字开头（如 1. 2. 3.）
        # 2. 以中文数字开头（如 一、二、三、）
        # 3. 长度相对较短
        # 4. 不包含详细描述性语言

        # 检查是否以数字或中文数字开头
        major_heading_patterns = [
            r'^\d+[\.\uff0e]',  # 1. 2. 3.
            r'^[一二三四五六七八九十]+[\u3001\uff0c]',  # 一、二、三、
            r'^\(\d+\)',  # (1) (2) (3)
            r'^\d+\)',  # 1) 2) 3)
            r'^第[一二三四五六七八九十\d]+[章节条款项]',  # 第一章 第二节
        ]

        for pattern in major_heading_patterns:
            if re.match(pattern, text):
                return True

        # 检查长度和内容特征
        if len(text) <= 50 and not any(keyword in text for keyword in ['应', '须', '必须', '要求', '不得', '应当']):
            return True

        return False

    def _get_model_config(self, ai_model: str) -> Dict[str, str]:
        """获取指定AI模型的配置"""
        # 使用配置系统获取模型配置
        model_config = self.config.get_model_config(ai_model)

        return {
            'endpoint': model_config.get('api_endpoint', self.api_endpoint),
            'api_key': model_config.get('api_key', self.api_key),
            'model_name': model_config.get('model_name', ai_model),
            'max_tokens': model_config.get('max_tokens', 500),
            'timeout': model_config.get('timeout', 30)
        }

    def _generate_ai_response(self, requirement: Dict[str, Any],
                            company_info: Dict[str, Any],
                            strategy: str,
                            ai_model: str = "gpt-4o-mini") -> str:
        """使用AI生成响应 - 使用统一的LLM客户端"""
        try:
            # 创建指定模型的LLM客户端
            llm_client = create_llm_client(ai_model)

            system_prompt = "你是一个专业的技术方案撰写专家，擅长为企业撰写技术响应文档。"

            prompt = f"""
作为{company_info.get('companyName', '投标方')}的技术专家，请针对以下技术需求生成专业的响应：

技术需求：{requirement['content']}
需求类型：{requirement['type']}
响应策略：{strategy}

要求：
1. 响应要专业、具体、可行
2. 突出公司的技术优势
3. 明确承诺满足需求
4. 提供具体的实现方案
5. 字数控制在200-300字

请生成响应：
            """

            response_content = llm_client.call(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.7,
                purpose=f"生成技术响应 - {requirement['type']}"
            )

            return response_content

        except Exception as e:
            self.logger.error(f"AI生成响应失败: {e}")
            # 回退到模板响应
            return self._generate_template_response(requirement,
                                                   self._get_response_template(requirement['type']),
                                                   company_info)
    
    def _generate_template_response(self, requirement: Dict[str, Any],
                                   template: str,
                                   company_info: Dict[str, Any]) -> str:
        """使用模板生成响应"""
        # 根据需求内容生成具体细节
        details = f"针对'{requirement['content'][:50]}...'的要求，我们将提供完整的解决方案，确保满足所有技术指标。"
        
        response = template.format(details=details)
        
        # 添加公司名称
        response = response.replace('我公司', company_info.get('companyName', '我公司'))
        
        return response.strip()
    
    def _create_response_document(self, responses: List[Dict[str, Any]],
                                 output_file: str,
                                 company_info: Dict[str, Any]):
        """创建响应文档"""
        doc = Document()
        
        # 添加标题
        title = doc.add_heading('技术需求响应文档', 0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # 添加公司信息
        doc.add_paragraph(f"投标单位：{company_info.get('companyName', '')}")
        doc.add_paragraph(f"联系电话：{company_info.get('phone', '')}")
        doc.add_paragraph(f"电子邮箱：{company_info.get('email', '')}")
        doc.add_paragraph()
        
        # 按章节组织响应
        current_section = ""
        for response in responses:
            # 如果进入新章节，添加章节标题
            if response['section'] != current_section:
                current_section = response['section']
                if current_section:
                    doc.add_heading(current_section, 1)
            
            # 添加需求
            req_para = doc.add_paragraph()
            req_para.add_run(f"需求{response['requirement_id']}：").bold = True
            req_para.add_run(response['requirement'])
            
            # 添加响应
            resp_para = doc.add_paragraph()
            resp_para.add_run("响应：").bold = True
            resp_para.add_run(response['response'])
            
            # 添加分隔
            doc.add_paragraph()
        
        # 保存文档
        doc.save(output_file)
        self.logger.info(f"响应文档已保存: {output_file}")