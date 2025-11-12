#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简历解析器
从上传的简历文件（PDF/Word）中智能提取人员信息
"""

import os
import re
import json
from typing import Dict, Any, Optional
from datetime import datetime

from modules.document_parser.parser_manager import ParserManager
from common.llm_client import LLMClient


class ResumeParser:
    """简历解析器"""

    def __init__(self):
        """初始化解析器"""
        self.parser_manager = ParserManager()
        self._llm_client = None  # 懒加载：首次使用时才初始化

    @property
    def llm_client(self):
        """懒加载LLM客户端"""
        if self._llm_client is None:
            try:
                self._llm_client = LLMClient()
            except Exception as e:
                raise Exception(f"初始化AI模型失败: {str(e)}。请检查模型配置(API密钥、网络连接等)")
        return self._llm_client

    def parse_resume(self, file_path: str) -> Dict[str, Any]:
        """
        解析简历文件，提取结构化信息
        Args:
            file_path: 简历文件路径
        Returns:
            解析后的结构化数据
        """
        try:
            # 1. 读取文档内容
            content = self._read_document(file_path)
            if not content:
                raise ValueError("无法读取文件内容")

            # 2. 使用关键词提取基础信息
            basic_info = self._extract_basic_info_by_keywords(content)

            # 3. 使用AI提取详细信息
            ai_extracted = self._extract_info_by_ai(content)

            # 4. 合并和验证数据
            merged_data = self._merge_and_validate(basic_info, ai_extracted)

            # 5. 格式化最终结果
            return self._format_result(merged_data)

        except Exception as e:
            raise Exception(f"解析简历失败: {str(e)}")

    def _read_document(self, file_path: str) -> str:
        """
        读取文档内容
        Args:
            file_path: 文件路径
        Returns:
            文档文本内容
        """
        try:
            # 使用ParserManager的简化版本读取文档
            text = self.parser_manager.parse_document_simple(file_path)
            if text:
                return text

            # 备用方案：直接读取
            file_ext = os.path.splitext(file_path)[1].lower()
            if file_ext == '.txt':
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()

            return ""

        except Exception as e:
            raise Exception(f"读取文档失败: {str(e)}")

    def _extract_basic_info_by_keywords(self, content: str) -> Dict[str, Any]:
        """
        通过关键词提取基础信息
        Args:
            content: 文档内容
        Returns:
            提取的基础信息
        """
        info = {}

        # 提取姓名
        name_patterns = [
            r'姓[\s　]*名[：:]\s*([^\s\n]{2,4})',
            r'姓名[：:]\s*([^\s\n]{2,4})',
            r'Name[：:]\s*([^\n]+)',
            r'^([^\s\n]{2,4})\s*(?:先生|女士|小姐)?$'
        ]
        for pattern in name_patterns:
            match = re.search(pattern, content, re.MULTILINE)
            if match:
                info['name'] = match.group(1).strip()
                break

        # 提取手机号
        phone_pattern = r'(?:手机|电话|Tel|Phone|Mobile)[：:]*\s*(1[3-9]\d{9})'
        match = re.search(phone_pattern, content)
        if match:
            info['phone'] = match.group(1)
        else:
            # 直接查找手机号格式
            match = re.search(r'1[3-9]\d{9}', content)
            if match:
                info['phone'] = match.group(0)

        # 提取邮箱
        email_pattern = r'(?:邮箱|Email|E-mail)[：:]*\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
        match = re.search(email_pattern, content, re.IGNORECASE)
        if match:
            info['email'] = match.group(1).lower()
        else:
            # 直接查找邮箱格式
            match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', content)
            if match:
                info['email'] = match.group(0).lower()

        # 提取身份证号
        id_pattern = r'(?:身份证|ID|身份证号)[：:]*\s*(\d{15}|\d{17}[\dXx])'
        match = re.search(id_pattern, content)
        if match:
            info['id_number'] = match.group(1).upper()

        # 提取学历
        education_keywords = {
            '博士': '博士',
            '硕士': '硕士',
            '研究生': '硕士',
            '本科': '本科',
            '学士': '本科',
            '大专': '大专',
            '专科': '大专',
            '高中': '高中',
            '中专': '中专'
        }
        for keyword, level in education_keywords.items():
            if keyword in content:
                info['education_level'] = level
                break

        # 提取性别
        if '男' in content and '女' not in content:
            info['gender'] = '男'
        elif '女' in content and '男' not in content:
            info['gender'] = '女'
        else:
            # 尝试从关键词后提取
            gender_pattern = r'(?:性别|Gender)[：:]\s*([男女])'
            match = re.search(gender_pattern, content)
            if match:
                info['gender'] = match.group(1)

        # 提取出生日期
        date_patterns = [
            r'(?:出生日期|生日|Birthday)[：:]\s*(\d{4}[-年/]\d{1,2}[-月/]\d{1,2})',
            r'(\d{4}[-年/]\d{1,2}[-月/]\d{1,2})(?:日)?(?:出生)',
            r'(?:Age|年龄)[：:]\s*(\d+)'  # 如果只有年龄，计算出生年份
        ]
        for pattern in date_patterns:
            match = re.search(pattern, content)
            if match:
                if '年龄' in pattern or 'Age' in pattern:
                    # 从年龄推算出生年份
                    age = int(match.group(1))
                    birth_year = datetime.now().year - age
                    info['birth_date'] = f"{birth_year}-01-01"
                else:
                    # 格式化日期
                    date_str = match.group(1)
                    date_str = re.sub(r'[年月/]', '-', date_str)
                    info['birth_date'] = date_str
                break

        # 提取毕业院校
        university_pattern = r'(?:毕业院校|学校|大学|学院|University|College)[：:]*\s*([^\s\n]+(?:大学|学院|学校))'
        match = re.search(university_pattern, content)
        if match:
            info['university'] = match.group(1)

        # 提取专业
        major_pattern = r'(?:专业|Major)[：:]\s*([^\s\n]+)'
        match = re.search(major_pattern, content)
        if match:
            info['major'] = match.group(1)

        # 提取工作单位
        company_pattern = r'(?:工作单位|公司|企业|Company|Employer)[：:]\s*([^\s\n]+(?:公司|集团|企业|院|所|中心))'
        match = re.search(company_pattern, content)
        if match:
            info['current_company'] = match.group(1)

        # 提取职位/职称
        position_patterns = [
            r'(?:职位|职务|岗位|Position|Title)[：:]\s*([^\s\n]+)',
            r'(?:职称|Professional Title)[：:]\s*([^\s\n]+)'
        ]
        for pattern in position_patterns:
            match = re.search(pattern, content)
            if match:
                if '职称' in pattern:
                    info['professional_title'] = match.group(1)
                else:
                    info['current_position'] = match.group(1)

        return info

    def _extract_info_by_ai(self, content: str) -> Dict[str, Any]:
        """
        使用AI提取详细信息
        Args:
            content: 文档内容
        Returns:
            AI提取的信息
        """
        # 限制内容长度，避免超过token限制
        max_length = 4000
        if len(content) > max_length:
            content = content[:max_length] + "..."

        prompt = f"""请从以下简历内容中提取人员信息，返回JSON格式数据。

简历内容：
{content}

请提取以下信息（如果存在的话）：
1. 基本信息：姓名、性别、出生日期、民族、籍贯、政治面貌、身份证号
2. 教育信息：学历、学位、毕业院校、专业、毕业时间
3. 工作信息：当前职位、职称、工作年限、当前工作单位、所在部门
4. 技能信息：
   - skills: 技能特长列表
   - certificates: 证书列表（包含证书名称和获得时间）
   - languages: 语言能力（包含语言和水平）
   - project_experience: 项目经历列表（包含项目名称、角色、时间、描述）
   - work_experience: 工作经历列表（包含公司名称、职位、工作时间、工作描述）
5. 联系方式：手机号码、邮箱、联系地址
6. 其他信息：期望薪资、工作地点、个人简介、获奖情况

返回JSON格式，示例：
{{
    "name": "张三",
    "gender": "男",
    "birth_date": "1990-01-01",
    "nationality": "汉族",
    "native_place": "北京",
    "political_status": "中共党员",
    "id_number": "110101199001011234",
    "education_level": "硕士",
    "degree": "工学硕士",
    "university": "清华大学",
    "major": "计算机科学与技术",
    "graduation_date": "2015-07-01",
    "current_position": "高级工程师",
    "professional_title": "高级工程师",
    "work_years": 8,
    "current_company": "某科技有限公司",
    "department": "技术部",
    "skills": ["Python", "Java", "机器学习"],
    "certificates": [
        {{"name": "PMP证书", "date": "2020-03"}}
    ],
    "languages": [
        {{"language": "英语", "level": "CET-6"}}
    ],
    "project_experience": [
        {{
            "name": "智能投标系统",
            "role": "技术负责人",
            "period": "2023-01至2023-12",
            "description": "负责系统架构设计和核心功能开发"
        }}
    ],
    "work_experience": [
        {{
            "company": "某科技有限公司",
            "position": "高级工程师",
            "period": "2020-01至2023-12",
            "description": "负责核心业务系统的设计和开发"
        }}
    ],
    "phone": "13800138000",
    "email": "zhangsan@example.com",
    "address": "北京市朝阳区",
    "salary_expectation": "20-30万/年",
    "work_location": "北京",
    "introduction": "具有丰富的软件开发经验...",
    "awards": "2022年度优秀员工"
}}

只返回JSON，不要其他说明。如果某个字段无法提取，可以省略或设为null。"""

        try:
            # 调用AI模型
            response = self.llm_client.call(
                prompt=prompt,
                temperature=0.1,
                max_tokens=2000,
                purpose="简历信息提取"
            )

            # 解析JSON响应
            return self._safe_json_parse(response)

        except Exception as e:
            print(f"AI提取失败: {str(e)}")
            return {}

    def _safe_json_parse(self, text: str) -> Dict[str, Any]:
        """
        安全地解析JSON字符串
        Args:
            text: 待解析的文本
        Returns:
            解析后的字典
        """
        if not text:
            return {}

        # 清理文本
        text = text.strip()

        # 尝试提取JSON块
        json_patterns = [
            r'```json\s*(.*?)\s*```',
            r'```\s*(.*?)\s*```',
            r'\{.*\}'
        ]

        json_str = text
        for pattern in json_patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                json_str = match.group(1) if '```' in pattern else match.group(0)
                break

        try:
            # 尝试解析JSON
            return json.loads(json_str)
        except json.JSONDecodeError:
            # 尝试修复常见的JSON错误
            json_str = re.sub(r',\s*}', '}', json_str)  # 移除尾随逗号
            json_str = re.sub(r',\s*]', ']', json_str)  # 移除数组尾随逗号
            json_str = re.sub(r'(\w+):', r'"\1":', json_str)  # 给键加引号

            try:
                return json.loads(json_str)
            except:
                return {}

    def _merge_and_validate(self,
                           keyword_data: Dict[str, Any],
                           ai_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        合并关键词提取和AI提取的数据，优先使用关键词提取的准确数据
        Args:
            keyword_data: 关键词提取的数据
            ai_data: AI提取的数据
        Returns:
            合并后的数据
        """
        merged = {}

        # 定义字段优先级（关键词提取通常更准确的字段）
        keyword_priority_fields = ['name', 'phone', 'email', 'id_number']

        # 合并数据
        for field in keyword_priority_fields:
            if keyword_data.get(field):
                merged[field] = keyword_data[field]
            elif ai_data.get(field):
                merged[field] = ai_data[field]

        # 其他字段优先使用AI提取的数据（通常更完整）
        for field, value in ai_data.items():
            if field not in merged and value:
                merged[field] = value

        # 补充关键词提取中独有的数据
        for field, value in keyword_data.items():
            if field not in merged and value:
                merged[field] = value

        # 数据验证和清理
        merged = self._validate_and_clean(merged)

        return merged

    def _validate_and_clean(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证和清理数据
        Args:
            data: 待验证的数据
        Returns:
            清理后的数据
        """
        # 验证手机号
        if 'phone' in data:
            phone = re.sub(r'\D', '', str(data['phone']))
            if len(phone) == 11 and phone.startswith('1'):
                data['phone'] = phone
            else:
                del data['phone']

        # 验证邮箱
        if 'email' in data:
            email = str(data['email']).lower().strip()
            if '@' in email and '.' in email:
                data['email'] = email
            else:
                del data['email']

        # 验证身份证号
        if 'id_number' in data:
            id_number = str(data['id_number']).upper().strip()
            if len(id_number) in [15, 18]:
                data['id_number'] = id_number
            else:
                del data['id_number']

        # 格式化日期字段
        date_fields = ['birth_date', 'graduation_date']
        for field in date_fields:
            if field in data and data[field]:
                try:
                    # 尝试解析和格式化日期
                    date_str = str(data[field])
                    date_str = re.sub(r'[年月/]', '-', date_str)
                    date_str = re.sub(r'日', '', date_str)
                    # 简单验证日期格式
                    if re.match(r'\d{4}-\d{1,2}-\d{1,2}', date_str):
                        data[field] = date_str
                    else:
                        del data[field]
                except:
                    del data[field]

        # 确保数值字段是整数
        if 'work_years' in data:
            try:
                data['work_years'] = int(data['work_years'])
            except:
                del data['work_years']

        # 清理字符串字段
        string_fields = ['name', 'gender', 'nationality', 'native_place',
                        'political_status', 'education_level', 'degree',
                        'university', 'major', 'current_position',
                        'professional_title', 'current_company', 'department',
                        'salary_expectation', 'work_location', 'address',
                        'introduction', 'awards']

        for field in string_fields:
            if field in data and data[field]:
                data[field] = str(data[field]).strip()
                if len(data[field]) == 0:
                    del data[field]

        return data

    def _format_result(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        格式化最终结果，确保符合数据库结构
        Args:
            data: 原始数据
        Returns:
            格式化后的数据
        """
        # 确保JSON字段是正确的格式
        json_fields = ['skills', 'certificates', 'languages', 'project_experience', 'work_experience']

        for field in json_fields:
            if field in data:
                if isinstance(data[field], str):
                    # 如果是字符串，尝试解析为列表
                    try:
                        data[field] = json.loads(data[field])
                    except:
                        # 如果解析失败，转为列表
                        data[field] = [data[field]] if data[field] else []
                elif not isinstance(data[field], (list, dict)):
                    data[field] = []

        # 添加默认值
        data.setdefault('status', 'active')

        # 移除空值
        data = {k: v for k, v in data.items() if v is not None and v != ''}

        return data

    def extract_from_text(self, text: str) -> Dict[str, Any]:
        """
        从文本内容中提取简历信息（不读取文件）
        Args:
            text: 简历文本内容
        Returns:
            解析后的结构化数据
        """
        try:
            # 使用关键词提取基础信息
            basic_info = self._extract_basic_info_by_keywords(text)

            # 使用AI提取详细信息
            ai_extracted = self._extract_info_by_ai(text)

            # 合并和验证数据
            merged_data = self._merge_and_validate(basic_info, ai_extracted)

            # 格式化最终结果
            return self._format_result(merged_data)

        except Exception as e:
            raise Exception(f"解析简历文本失败: {str(e)}")