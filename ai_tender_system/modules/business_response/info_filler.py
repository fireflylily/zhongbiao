#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
信息填写模块 - 处理项目和公司信息的填写
实现六大规则：替换规则、填空规则、组合规则、变体处理、例外处理、后处理

⏺ 基于代码分析，这是一个AI标书系统的信息填写模块。以下是现有的
  字段映射、填写规则和替换规则的详细展示：

  🗺️ 字段映射 (field_mapping_rules)

  公司信息字段（直接映射）

  - companyName: 公司名称
  - email: 邮箱
  - fax: 传真
  - postalCode: 邮政编码
  - establishDate: 成立时间
  - businessScope: 经营范围
  - legalRepresentative: 法定代表人
  - authorizedPersonName: 被授权人姓名

  公司信息字段（多源映射 - 按优先级顺序）

  - address: ['address', 'registeredAddress', 'officeAddress']
  - phone: ['fixedPhone', 'phone']

  职位字段（智能映射 - 需上下文识别）

  - authorizedPersonPosition: 被授权人职务
  - legalRepresentativePosition: 法定代表人职位

  项目信息字段

  - projectName: 项目名称
  - projectNumber: 项目编号
  - date: 日期
  - purchaserName: 采购人名称

  🔄 替换规则

  1. 括号替换规则（6种类型）

  - 供应商名称类：（供应商名称）→（公司名）
    - 支持12种变体：供应商名称、供应商全称、投标人名称、公司名
  称、单位名称、应答人名称
    - 包含公章变体：如（供应商名称（盖章））
  - 采购人类：（采购人）→（项目采购人）
  - 项目信息类：（项目名称）→（具体项目名）、（项目编号）→（具
  体编号）
  - 其他字段类：电话、邮箱、地址、传真等

  2. 组合替换规则（2种）

  - （供应商名称、地址）→（公司名、地址）
  - （项目名称、项目编号）→（项目名、编号）
  - 🆕 职位、职称 → 智能职位信息组合
  - 🆕 姓名、职位 → 智能人员信息组合

  3. 致谓替换规则

  - 致：采购人 → 致：具体采购人名称

  ✏️ 填空规则

  支持的6种模式匹配

  1. 模式1: 字段名：___ - 多字段支持
  2. 模式2: 字段名： - 无下划线支持
  3. 模式3: 字段名：___ - 混合空格下划线
  4. 模式4: 字段名：___. - 以句号结束
  5. 模式5: 字段名  - 插入式填空（无下划线）
  6. 模式6: 字段名 ___ - 空格后跟下划线

  支持的4种替换策略

  1. 插入式替换：直接在字段名后插入内容
  2. 精确模式替换：
    - 多字段格式处理
    - 单字段格式处理
    - 无下划线格式处理
    - 备用简单模式
  3. 纯空格替换：处理只有空格无下划线的情况
  4. 公章格式替换：供应商名称：___（加盖公章）

  特殊处理

  - 年月日格式：支持文档末尾的年 月 日格式填充
  - 职位智能识别：根据上下文区分被授权人职务和法定代表人职位
  - 扩展模式匹配：支持带公章、盖章的复杂变体

  🎯 字段变体映射

  供应商名称变体（12种）

  ['供应商名称', '供应商全称', '投标人名称', '公司名称', 
  '单位名称', '应答人名称', '供应商名称（盖章）',
  '供应商名称（公章）', '公司名称（盖章）',
  '投标人名称（盖章）', '投标人名称（公章）',
  '单位名称（盖章）', '单位名称（公章）']

  其他字段变体

  - 邮箱: 8种变体（邮箱、邮件、电子邮件、电子邮箱、email等）
  - 电话: 5种变体（电话、联系电话、固定电话等）
  - 传真: 4种变体
  - 地址: 6种变体
  - 日期: 6种变体（日期、日 期、日  期等）

  ⚠️ 跳过规则

  跳过关键词

  - 招标人信息：['招标人', '甲方', '代理', '招标代理', 
  '采购代理', '业主', '发包人', '委托人']
  - 签字相关：['签字', '签名', '签章', '盖章处']

  例外处理

  - 保留"签字代表"等合法词汇
  - 区分采购人（需要填充）和招标人（需要跳过）

  这个系统实现了非常全面的文档信息填写功能，支持多种格式、多种
  规则，并具备智能识别和错误处理能力。
7.填空规则
7.1 电话、邮箱、地址、邮编、传真、成立时间、经营范围、采购人（不支持电子邮箱，电子邮件，因为与邮箱和邮件重复了），日期，日+空格+期
7.2 供应商名称、项目名称、项目编号
7.3 支持格式变化（冒号、空格、占位符、冒号+空格）
        模式匹配 (6种模式):
  - 模式1: {variant}\s*[:：]\s*_+ - 多字段支持：地址：___ 邮编：___
  - 模式2: {variant}\s*[:：]\s*$ - 无下划线支持：电子邮箱：
  - 模式3: {variant}\s*[:：]\s*[_\s]*$
  - 模式4: {variant}\s*[:：]\s*[_\s]+[。\.]
  - 模式5: {variant}(?=\s+(?!.*_)) - 插入式填空
  - 模式6: {variant}\s+[_\s]+$

  替换策略 (4种复杂策略):
  - 模式5: 插入式替换
  - 其他模式: 精确模式替换
    - multi_field_pattern: 多字段格式处理
    - single_field_pattern: 单字段格式处理
    - no_underscore_pattern: 无下划线格式处理
    - 备用简单模式  


8.采购人、项目名称、项目编号、日期信息从 项目信息配置文件中读取
    公司信息从公司的配置文件中读取。
    授权代表的姓名即 公司信息中的被授权人的姓名

"""

import re
from typing import Dict, Any
from docx import Document
from docx.text.paragraph import Paragraph
from docx.table import Table

# 导入公共模块
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
from common import get_module_logger

class InfoFiller:
    """信息填写处理器"""
    
    def __init__(self):
        self.logger = get_module_logger("info_filler")
        
        # 供应商名称的变体
        self.company_name_variants = [
            '供应商名称', '供应商全称', '投标人名称', '公司名称',
            '单位名称', '应答人名称', '供应商名称（盖章）',
            '供应商名称（公章）', '公司名称（盖章）', '投标人名称（盖章）',
            '投标人名称（公章）', '单位名称（盖章）', '单位名称（公章）'
        ]

        # 供应商名称的扩展匹配模式（支持带公章、盖章的变体）
        self.company_name_extended_patterns = [
            r'供应商名称(?:\s*[（(][^）)]*[公盖]章[^）)]*[）)])?',  # 供应商名称（加盖公章）
            r'供应商全称(?:\s*[（(][^）)]*[公盖]章[^）)]*[）)])?',
            r'投标人名称(?:\s*[（(][^）)]*[公盖]章[^）)]*[）)])?',  # 投标人名称（公章）
            r'公司名称(?:\s*[（(][^）)]*[公盖]章[^）)]*[）)])?',
            r'单位名称(?:\s*[（(][^）)]*[公盖]章[^）)]*[）)])?',
            r'应答人名称(?:\s*[（(][^）)]*[公盖]章[^）)]*[）)])?',
        ]
        
        # 其他字段的变体映射
        self.field_variants = {
            'email': ['邮箱', '邮件', '电子邮件', '电子邮箱', 'email', 'Email', 'E-mail', 'E-Mail'],
            'phone': ['电话', '联系电话', '固定电话', '电话号码', '联系方式'],
            'fax': ['传真', '传真号码', '传真号', 'fax', 'Fax'],
            'address': ['地址', '注册地址', '办公地址', '联系地址', '通讯地址', '供应商地址', '公司地址'],
            'postalCode': ['邮政编码', '邮编', '邮码'],
            'establishDate': ['成立时间', '成立日期', '注册时间', '注册日期'],
            'businessScope': ['经营范围', '业务范围', '经营项目'],
            'legalRepresentative': ['法定代表人', '法人代表', '法人'],
            'authorizedPersonName': ['供应商代表姓名', '授权代表姓名', '代表姓名', '授权代表'],
            'position': ['职务', '职位', '职称'],
            'projectName': ['项目名称', '采购项目名称', '招标项目名称'],
            'projectNumber': ['项目编号', '采购编号', '招标编号', '项目号'],
            'date': ['日期', '日 期', '日  期', '日   期', '日    期', '日     期']
        }
        
        # 需要跳过的关键词（招标人信息，但不包括采购人）
        self.skip_keywords = [
            '招标人', '甲方', '代理', '招标代理',
            '采购代理', '业主', '发包人', '委托人'
        ]
        
        # 采购人信息字段（使用项目信息填充）
        self.purchaser_variants = ['采购人', '采购人名称', '采购单位']
        
        # 需要跳过的签字相关词
        self.signature_keywords = ['签字', '签名', '签章', '盖章处']

        # 统一字段映射配置 - 定义字段名与数据源的映射关系
        self.field_mapping_rules = {
            # 公司信息字段 (直接映射)
            'companyName': ['companyName'],
            'email': ['email'],
            'fax': ['fax'],
            'postalCode': ['postalCode'],
            'establishDate': ['establishDate'],
            'businessScope': ['businessScope'],
            'legalRepresentative': ['legalRepresentative'],
            'authorizedPersonName': ['authorizedPersonName'],

            # 公司信息字段 (多源映射 - 按优先级顺序)
            'address': ['address', 'registeredAddress', 'officeAddress'],
            'phone': ['fixedPhone', 'phone'],

            # 职位字段 (智能映射 - 需要上下文识别)
            'authorizedPersonPosition': ['authorizedPersonPosition'],
            'legalRepresentativePosition': ['legalRepresentativePosition'],

            # 项目信息字段 (直接映射)
            'projectName': ['projectName'],
            'projectNumber': ['projectNumber'],
            'date': ['date'],

            # 项目信息字段 (多源映射)
            'purchaserName': ['purchaserName', 'projectOwner']
        }
        
    def fill_info(self, doc: Document, company_info: Dict[str, Any], 
                  project_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        填写信息主方法
        
        Args:
            doc: Word文档对象
            company_info: 公司信息字典
            project_info: 项目信息字典（包含项目名称、编号、日期等）
            
        Returns:
            处理统计信息
        """
        stats = {
            'total_replacements': 0,
            'replacement_rules': 0,
            'fill_rules': 0,
            'combination_rules': 0,
            'skipped_fields': 0,
            'none': 0  # 添加对未处理段落的统计
        }
        
        # 创建统一的字段映射（替代简单合并）
        all_info = self._create_unified_field_mapping(company_info, project_info)
        
        # 文档级别验证：记录处理前状态
        total_paragraphs = len([p for p in doc.paragraphs if p.text.strip()])
        total_tables = len(doc.tables)
        self.logger.info(f"📊 开始处理文档: {total_paragraphs} 个非空段落, {total_tables} 个表格")
        self.logger.debug(f"📊 可用信息键: {list(all_info.keys())}")
        
        # 处理所有段落
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                result = self._process_paragraph(paragraph, all_info)
                stats['total_replacements'] += result['count']
                
                # 安全地更新统计信息
                result_type = result['type']
                if result_type in stats:
                    if result_type == 'skipped':
                        stats[result_type] += 1
                    else:
                        stats[result_type] += result['count']
                else:
                    # 如果类型不存在，记录为'none'
                    stats['none'] += result['count']
        
        # 处理表格
        for table in doc.tables:
            result = self._process_table(table, all_info)
            stats['total_replacements'] += result['count']
            stats['fill_rules'] += result['count']
        
        # 后处理：清理多余的占位符
        self._post_process(doc)
        
        # 文档级别验证：处理完成后的验证
        self.logger.info(f"📊 文档处理完成统计: {stats}")
        
        # 详细验证处理结果
        if stats['total_replacements'] > 0:
            self.logger.info(f"✅ 成功处理了 {stats['total_replacements']} 个字段")
            if stats['replacement_rules'] > 0:
                self.logger.info(f"  - 替换规则: {stats['replacement_rules']} 个")
            if stats['fill_rules'] > 0:
                self.logger.info(f"  - 填空规则: {stats['fill_rules']} 个")
            if stats['combination_rules'] > 0:
                self.logger.info(f"  - 组合规则: {stats['combination_rules']} 个")
        else:
            self.logger.warning(f"⚠️  文档处理完成，但未处理任何字段！")
        
        if stats['skipped_fields'] > 0:
            self.logger.info(f"⏭️  跳过 {stats['skipped_fields']} 个字段")
        
        # 记录一些具体段落内容用于调试
        self.logger.debug(f"📄 文档处理后段落预览:")
        for i, paragraph in enumerate(doc.paragraphs[:5]):  # 只记录前5个段落
            if paragraph.text.strip():
                self.logger.debug(f"  段落{i+1}: '{paragraph.text[:100]}{'...' if len(paragraph.text) > 100 else ''}'")
        
        self.logger.info(f"信息填写完成: {stats}")
        return stats

    def _create_unified_field_mapping(self, company_info: Dict[str, Any],
                                    project_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建统一的字段映射表

        Args:
            company_info: 公司信息字典
            project_info: 项目信息字典

        Returns:
            统一的字段映射字典，所有字段都映射到标准化的值
        """
        # 合并原始数据
        raw_data = {**company_info, **project_info}
        unified_mapping = {}

        self.logger.debug(f"🔧 开始创建统一字段映射")
        self.logger.debug(f"🔧 原始数据键: {list(raw_data.keys())}")

        # 遍历所有映射规则
        for target_field, source_fields in self.field_mapping_rules.items():
            value = None

            # 按优先级顺序查找值 (第一个非空值)
            for source_field in source_fields:
                if source_field in raw_data:
                    candidate_value = raw_data[source_field]
                    if candidate_value and str(candidate_value).strip():  # 非空且非空白
                        value = candidate_value
                        self.logger.debug(f"🔧 字段映射: {target_field} ← {source_field} = '{value}'")
                        break

            # 存储映射结果 (即使是None也要存储，避免KeyError)
            unified_mapping[target_field] = value or ''

            if not value:
                self.logger.debug(f"⚠️ 字段映射: {target_field} ← 无有效数据源 (尝试了 {source_fields})")

        # 添加其他未配置映射规则的字段 (直接透传)
        for key, value in raw_data.items():
            if key not in unified_mapping:
                unified_mapping[key] = value
                self.logger.debug(f"🔧 直接映射: {key} = '{value}'")

        self.logger.info(f"🔧 统一字段映射完成: {len(unified_mapping)} 个字段")
        self.logger.debug(f"🔧 映射结果预览: {list(unified_mapping.keys())}")

        return unified_mapping

    def _process_paragraph(self, paragraph: Paragraph, info: Dict[str, Any]) -> Dict[str, Any]:
        """处理单个段落"""
        result = {'count': 0, 'type': 'none'}
        para_text = paragraph.text.strip()
        
        # 检查是否需要跳过
        if self._should_skip(para_text):
            self.logger.debug(f"跳过段落: {para_text[:50]}")
            return {'count': 0, 'type': 'skipped'}
        
        processed = False
        final_type = 'none'
        
        # 1. 尝试组合替换规则
        if self._try_combination_rule(paragraph, info):
            processed = True
            final_type = 'combination_rules'
        
        # 2. 尝试单字段替换规则（即使组合规则已处理，也要尝试）
        if self._try_replacement_rule(paragraph, info):
            processed = True
            # 如果已经有组合规则，保持组合规则类型，否则设为替换规则
            if final_type == 'none':
                final_type = 'replacement_rules'
        
        # 3. 尝试填空规则（仅在前两个都没有处理时才尝试）
        if not processed and self._try_fill_rule(paragraph, info):
            processed = True
            final_type = 'fill_rules'
        
        if processed:
            return {'count': 1, 'type': final_type}
        
        return result
    
    def _should_skip(self, text: str) -> bool:
        """检查是否应该跳过该文本"""
        # 检查是否包含采购人/招标人等关键词（使用更精确的匹配）
        for keyword in self.skip_keywords:
            # 避免误判：排除"签字代表"等合法词汇  
            if keyword in text and "签字代表" not in text:
                return True
        
        # 检查是否包含签字相关词（避免误判签字代表等合法词汇）
        for keyword in self.signature_keywords:
            if keyword in text:
                # 排除合法的描述性词汇
                if keyword == '签字' and ('签字代表' in text or '经正式授权' in text):
                    continue
                return True
        
        return False

    def _detect_position_context(self, paragraph_text: str) -> str:
        """
        检测段落中的职位上下文，区分被授权人职务和法定代表人职位

        Args:
            paragraph_text: 段落文本

        Returns:
            'authorized_person': 被授权人上下文
            'legal_representative': 法定代表人上下文（默认）
        """
        try:
            if not paragraph_text or not isinstance(paragraph_text, str):
                self.logger.warning(f"⚠️  职位上下文检测：无效的段落文本输入")
                return 'legal_representative'

            text = paragraph_text.strip()
            if not text:
                self.logger.warning(f"⚠️  职位上下文检测：段落文本为空")
                return 'legal_representative'

            # 被授权人上下文关键字模式 (增强版)
            authorized_person_patterns = [
                r'授权.*?代表.*?[职位务称]',          # "授权代表职务"
                r'为我方.*?授权.*?代表',             # "为我方授权代表"
                r'为我方代表.*?[职位务称]',           # "为我方代表职务"
                r'参加.*?代表.*?[职位务称]',          # "参加投标代表职务"
                r'授权.*?[（(].*?[）)].*?[职位务称]',   # "授权（张三）职务"
                r'被授权.*?[职位务称]',              # "被授权人职务"
                r'商务代表.*?[职位务称]',             # "商务代表职务"
                r'授权.*?[（(].*?姓名.*?职[位务称]',   # "授权（姓名、职位）"
                r'为我方.*?授权.*?[（(].*?职[位务称]', # "为我方授权（职位、职称）"
            ]

            # 法定代表人上下文关键字模式
            legal_representative_patterns = [
                r'法定代表人.*?职位',           # "法定代表人职位"
                r'法人.*?职位',                # "法人职位"
                r'系.*?法定代表人.*?职位',      # "系我公司法定代表人职位"
                r'公司.*?法定代表人.*?职位',    # "公司法定代表人职位"
            ]

            self.logger.debug(f"🔍 检测职位上下文: '{text[:100]}{'...' if len(text) > 100 else ''}'")

            # 检查被授权人上下文
            try:
                for pattern in authorized_person_patterns:
                    if re.search(pattern, text):
                        self.logger.info(f"✅ 识别为被授权人上下文: '{pattern}' 匹配")
                        return 'authorized_person'
            except re.error as e:
                self.logger.error(f"❌ 被授权人模式匹配正则表达式错误: {e}")

            # 检查法定代表人上下文
            try:
                for pattern in legal_representative_patterns:
                    if re.search(pattern, text):
                        self.logger.info(f"✅ 识别为法定代表人上下文: '{pattern}' 匹配")
                        return 'legal_representative'
            except re.error as e:
                self.logger.error(f"❌ 法定代表人模式匹配正则表达式错误: {e}")

            # 默认情况：如果没有明确上下文，使用法定代表人
            self.logger.debug(f"📝 未找到明确上下文，默认使用法定代表人职位")
            return 'legal_representative'

        except Exception as e:
            self.logger.error(f"❌ 职位上下文检测发生异常: {e}")
            self.logger.debug(f"📝 异常情况下默认使用法定代表人职位")
            return 'legal_representative'

    def _try_combination_rule(self, paragraph: Paragraph, info: Dict[str, Any]) -> bool:
        """
        尝试组合替换规则
        如：（供应商名称、地址）→（公司名、地址）
        """
        text = paragraph.text
        
        # 组合模式1：供应商名称、地址
        pattern1 = r'[（(]\s*供应商名称\s*[、，]\s*地址\s*[）)]'
        if re.search(pattern1, text):
            company_name = info.get('companyName', '')
            address = info.get('address', '')
            if company_name and address:
                replacement = f"（{company_name}、{address}）"
                new_text = re.sub(pattern1, replacement, text)
                self._update_paragraph_text(paragraph, new_text)
                self.logger.info(f"组合替换: 供应商名称、地址")
                return True
        
        # 组合模式2：项目名称、项目编号
        pattern2 = r'[（(]\s*项目名称\s*[、，]\s*项目编号\s*[）)]'
        if re.search(pattern2, text):
            project_name = info.get('projectName', '')
            project_number = info.get('projectNumber', '')
            if project_name and project_number:
                replacement = f"（{project_name}、{project_number}）"
                new_text = re.sub(pattern2, replacement, text)
                self._update_paragraph_text(paragraph, new_text)
                self.logger.info(f"组合替换: 项目名称、项目编号")
                return True

        # 组合模式3：（职位、职称）智能替换规则
        pattern3 = r'[（(]\s*职[位务称]\s*[、，]\s*职[位务称]\s*[）)]'
        if re.search(pattern3, text):
            self.logger.debug(f"🎯 检测到职位组合模式: '{text[:50]}...'")

            try:
                # 智能识别上下文
                context = self._detect_position_context(text)
                self.logger.debug(f"🧠 上下文识别结果: {context}")

                # 根据上下文选择数据源
                if context == 'authorized_person':
                    position = info.get('authorizedPersonPosition', '')
                    if position:
                        self.logger.debug(f"📝 选择被授权人职务: '{position}'")
                    else:
                        self.logger.warning(f"⚠️ 被授权人职务为空，尝试法定代表人职位")
                        position = info.get('legalRepresentativePosition', '')
                        if position:
                            self.logger.info(f"📝 回退使用法定代表人职位: '{position}'")
                else:  # legal_representative
                    position = info.get('legalRepresentativePosition', '')
                    if position:
                        self.logger.debug(f"📝 选择法定代表人职位: '{position}'")
                    else:
                        self.logger.warning(f"⚠️ 法定代表人职位为空，尝试被授权人职务")
                        position = info.get('authorizedPersonPosition', '')
                        if position:
                            self.logger.info(f"📝 回退使用被授权人职务: '{position}'")

                if position:
                    replacement = f"（{position}、{position}）"
                    new_text = re.sub(pattern3, replacement, text)
                    self._update_paragraph_text(paragraph, new_text)
                    self.logger.info(f"智能职位组合替换: （职位、职称） → （{position}、{position}）")
                    return True
                else:
                    self.logger.warning(f"⚠️ 所有职位数据源都为空，跳过处理")

            except Exception as e:
                self.logger.error(f"❌ 职位组合替换发生异常: {e}")
                # 异常情况下不影响其他规则处理

        # 组合模式4：（姓名、职位）智能替换规则
        pattern4 = r'[（(]\s*姓名\s*[、，]\s*职[位务称]\s*[）)]'
        if re.search(pattern4, text):
            self.logger.debug(f"🎯 检测到姓名职位组合模式: '{text[:50]}...'")

            try:
                # 智能识别上下文
                context = self._detect_position_context(text)
                self.logger.debug(f"🧠 上下文识别结果: {context}")

                # 根据上下文选择数据源
                if context == 'authorized_person':
                    name = info.get('authorizedPersonName', '')
                    position = info.get('authorizedPersonPosition', '')
                    self.logger.debug(f"📝 选择被授权人数据: 姓名='{name}', 职务='{position}'")

                    # 数据回退机制
                    if not name or not position:
                        self.logger.warning(f"⚠️ 被授权人数据不完整，尝试法定代表人数据")
                        name = info.get('legalRepresentative', '') if not name else name
                        position = info.get('legalRepresentativePosition', '') if not position else position
                        if name or position:
                            self.logger.info(f"📝 回退使用法定代表人数据: 姓名='{name}', 职位='{position}'")
                else:  # legal_representative
                    name = info.get('legalRepresentative', '')
                    position = info.get('legalRepresentativePosition', '')
                    self.logger.debug(f"📝 选择法定代表人数据: 姓名='{name}', 职位='{position}'")

                    # 数据回退机制
                    if not name or not position:
                        self.logger.warning(f"⚠️ 法定代表人数据不完整，尝试被授权人数据")
                        name = info.get('authorizedPersonName', '') if not name else name
                        position = info.get('authorizedPersonPosition', '') if not position else position
                        if name or position:
                            self.logger.info(f"📝 回退使用被授权人数据: 姓名='{name}', 职务='{position}'")

                if name and position:
                    replacement = f"（{name}、{position}）"
                    new_text = re.sub(pattern4, replacement, text)
                    self._update_paragraph_text(paragraph, new_text)
                    self.logger.info(f"智能姓名职位组合替换: （姓名、职位） → （{name}、{position}）")
                    return True
                else:
                    missing_fields = []
                    if not name:
                        missing_fields.append('姓名')
                    if not position:
                        missing_fields.append('职位')
                    self.logger.warning(f"⚠️ 缺少必要数据字段: {', '.join(missing_fields)}，跳过处理")

            except Exception as e:
                self.logger.error(f"❌ 姓名职位组合替换发生异常: {e}")
                # 异常情况下不影响其他规则处理

        return False
    
    def _try_replacement_rule(self, paragraph: Paragraph, info: Dict[str, Any]) -> bool:
        """
        尝试单字段替换规则
        如：（供应商名称）→（公司名）、（采购人）→（项目采购人）
        支持单段落中的多个字段替换
        """
        text = paragraph.text
        new_text = text
        replacement_count = 0
        
        # 处理供应商名称类
        for variant in self.company_name_variants:
            pattern = rf'[（(]\s*{re.escape(variant)}\s*[）)]'
            if re.search(pattern, new_text):
                company_name = info.get('companyName', '')
                if company_name:
                    replacement = f"（{company_name}）"
                    new_text = re.sub(pattern, replacement, new_text)
                    self.logger.info(f"替换规则: {variant} → {company_name}")
                    replacement_count += 1
        
        # 处理采购人信息
        for variant in self.purchaser_variants:
            pattern = rf'[（(]\s*{re.escape(variant)}\s*[）)]'
            if re.search(pattern, new_text):
                purchaser_name = info.get('purchaserName', '')
                if purchaser_name:
                    replacement = f"（{purchaser_name}）"
                    new_text = re.sub(pattern, replacement, new_text)
                    self.logger.info(f"替换规则: {variant} → {purchaser_name}")
                    replacement_count += 1
        
        # 处理项目信息（项目名称、项目编号）
        # 项目名称处理
        for variant in ['项目名称', '采购项目名称', '招标项目名称']:
            pattern = rf'[（(]\s*{re.escape(variant)}\s*[）)]'
            if re.search(pattern, new_text):
                self.logger.debug(f"🔎 检查项目名称变体: '{variant}'")
                # 获取项目名称（固定键名）
                project_name = info.get('projectName', '')
                if project_name:
                    replacement = f"（{project_name}）"
                    new_text = re.sub(pattern, replacement, new_text)
                    self.logger.info(f"替换规则: {variant} → {project_name}")
                    replacement_count += 1
                else:
                    self.logger.warning(f"⚠️ 项目名称数据为空，跳过字段 '{variant}'")
        
        # 项目编号处理  
        for variant in ['项目编号', '采购编号', '招标编号', '项目号']:
            pattern = rf'[（(]\s*{re.escape(variant)}\s*[）)]'
            if re.search(pattern, new_text):
                self.logger.debug(f"🔎 检查项目编号变体: '{variant}'")
                # 获取项目编号（固定键名）
                project_number = info.get('projectNumber', '')
                if project_number:
                    replacement = f"（{project_number}）"
                    new_text = re.sub(pattern, replacement, new_text)
                    self.logger.info(f"替换规则: {variant} → {project_number}")
                    replacement_count += 1
                else:
                    self.logger.warning(f"⚠️ 项目编号数据为空，跳过字段 '{variant}'")
        
        # 处理其他字段
        for field_key, variants in self.field_variants.items():
            for variant in variants:
                pattern = rf'[（(]\s*{re.escape(variant)}\s*[）)]'
                if re.search(pattern, new_text):
                    # 直接获取字段值（统一映射已处理多源映射）
                    value = info.get(field_key, '')
                    
                    if value:
                        replacement = f"（{value}）"
                        new_text = re.sub(pattern, replacement, new_text)
                        self.logger.info(f"替换规则: {variant} → {value}")
                        replacement_count += 1
        
        # 如果有替换，更新段落文本
        if replacement_count > 0:
            self._update_paragraph_text(paragraph, new_text)
            return True
        
        return False
    
    def _try_fill_rule(self, paragraph: Paragraph, info: Dict[str, Any]) -> bool:
        """
        尝试填空规则 - 改为累积处理模式，支持同一段落多字段
        如：地址：___ 邮编：___ → 地址：xxx 邮编：yyy
        """
        text = paragraph.text
        new_text = text
        fill_count = 0
        
        # 详细日志：记录段落处理开始
        self.logger.debug(f"🔍 开始处理段落: '{text[:100]}{'...' if len(text) > 100 else ''}'")
        self.logger.debug(f"📏 段落全文长度: {len(text)} 字符")
        
        # 处理供应商名称类的填空 - 使用扩展模式匹配
        self.logger.debug(f"🔍 开始扩展模式匹配:")
        matched_variant = None

        # 优先使用扩展模式进行匹配
        for pattern in self.company_name_extended_patterns:
            self.logger.debug(f"🔍 尝试扩展模式: {pattern}")
            match = re.search(pattern, new_text)
            if match:
                matched_variant = match.group()
                self.logger.debug(f"✅ 扩展模式匹配成功: '{matched_variant}'")
                break
            else:
                self.logger.debug(f"❌ 扩展模式不匹配")

        # 如果扩展模式匹配成功，使用匹配到的完整变体进行处理
        if matched_variant:
            variant = matched_variant
            self.logger.debug(f"🎯 使用扩展匹配的变体: '{variant}'")
            
            patterns = [
                rf'{re.escape(variant)}\s*[:：]\s*_+',  # 冒号后跟下划线
                rf'{re.escape(variant)}\s*[:：]\s*\s+$',  # 冒号后跟空格到行尾
                rf'{re.escape(variant)}\s*[:：]\s*[_\s]*$',  # 冒号后跟下划线或空格
                rf'{re.escape(variant)}\s*[:：]\s*[_\s]+[。\.]',  # 冒号后跟下划线，以句号结束
                rf'{re.escape(variant)}(?=\s+(?!.*_))',  # 字段名后跟空格（插入式填空，不含下划线）
                rf'{re.escape(variant)}\s+[_\s]+$',  # 空格后跟下划线
                rf'{re.escape(variant)}\s*[:：]\s*[_\s]+[（(][^）)]*章[^）)]*[）)]',  # 公章格式：供应商名称：___（加盖公章）
            ]
            
            for i, pattern in enumerate(patterns, 1):
                self.logger.debug(f"🔍 尝试模式{i}: {pattern}")
                match = re.search(pattern, new_text)
                if match:
                    self.logger.info(f"✅ 模式{i}匹配成功: '{match.group()}'")
                    company_name = info.get('companyName', '')
                    self.logger.debug(f"📝 准备填入公司名称: '{company_name}'")
                    
                    if company_name:
                        original_text = new_text
                        
                        # 根据匹配的模式选择不同的替换策略
                        if i == 2:  # 第2个模式：纯空格替换
                            self.logger.debug(f"🔄 使用纯空格替换策略")
                            # 替换冒号后的所有空格，保留冒号
                            space_pattern = rf'({re.escape(variant)}\s*[:：])\s*\s+$'
                            new_text = re.sub(space_pattern, rf'\1{company_name}', new_text)
                        elif i == 5:  # 第5个模式：插入式填空
                            self.logger.debug(f"🔄 使用插入式替换策略")
                            # 在字段名后直接插入内容，保持空格布局
                            insert_pattern = rf'{re.escape(variant)}(?=\s+)'
                            new_text = re.sub(insert_pattern, f'{variant}{company_name}', new_text)
                        elif i == 7:  # 第7个模式：公章格式
                            self.logger.debug(f"🔄 使用公章格式替换策略")
                            # 精确替换空格/下划线部分，保留公章括号
                            stamp_pattern = rf'(?P<prefix>{re.escape(variant)}\s*[:：]\s*)(?P<spaces>[_\s]+)(?P<stamp>[（(][^）)]*章[^）)]*[）)])'
                            new_text = re.sub(stamp_pattern, rf'\g<prefix>{company_name}\g<stamp>', new_text)
                        else:  # 其他模式：标准替换
                            self.logger.debug(f"🔄 使用标准替换策略")
                            # 使用与其他字段相同的精确替换逻辑（支持no_underscore_pattern）
                            # 模式1：多字段格式 "字段：___ 其他字段："
                            multi_field_pattern = rf'(?P<prefix>{re.escape(variant)}\s*[:：]\s*)(?P<underscores>_+)(?P<suffix>\s+[^\s_]+[:：])'
                            # 模式2：单字段格式 "字段：___" (到行尾或句号)
                            single_field_pattern = rf'(?P<prefix>{re.escape(variant)}\s*[:：]\s*)(?P<underscores>_+)(?P<suffix>$|[。\.])'
                            # 模式3：无下划线格式 "字段：" (直接在行尾)
                            no_underscore_pattern = rf'(?P<prefix>{re.escape(variant)}\s*[:：]\s*)(?P<suffix>$)'

                            if re.search(multi_field_pattern, new_text):
                                self.logger.debug(f"🔄 使用多字段模式替换")
                                new_text = re.sub(multi_field_pattern, rf'\g<prefix>{company_name}\g<suffix>', new_text)
                            elif re.search(single_field_pattern, new_text):
                                self.logger.debug(f"🔄 使用单字段模式替换")
                                new_text = re.sub(single_field_pattern, rf'\g<prefix>{company_name}\g<suffix>', new_text)
                            elif re.search(no_underscore_pattern, new_text):
                                self.logger.debug(f"🔄 使用无下划线模式替换")
                                new_text = re.sub(no_underscore_pattern, rf'\g<prefix>{company_name}', new_text)
                            else:
                                self.logger.debug(f"🔄 使用备用简单模式替换")
                                simple_pattern = rf'(?P<prefix>{re.escape(variant)}\s*[:：]\s*)(?P<underscores>_+)'
                                new_text = re.sub(simple_pattern, rf'\g<prefix>{company_name}', new_text)
                        
                        self.logger.info(f"🔄 替换前: '{original_text}'")
                        self.logger.info(f"🔄 替换后: '{new_text}'")
                        self.logger.info(f"填空规则: {variant} 填入 {company_name}")
                        fill_count += 1
                        break  # 找到一个模式就跳出内层循环
                    else:
                        self.logger.warning(f"⚠️  公司名称为空，跳过填写")
                else:
                    self.logger.debug(f"❌ 模式{i}不匹配")
        else:
            # 扩展模式匹配失败，使用传统的变体列表处理
            self.logger.debug(f"🔄 扩展模式匹配失败，尝试传统变体处理")

            for variant in self.company_name_variants:
                self.logger.debug(f"🔎 检查供应商名称变体: '{variant}'")

                # 检查字段是否存在于文本中
                if variant not in new_text:
                    self.logger.debug(f"❌ 字段 '{variant}' 不在段落文本中，跳过")
                    continue

                self.logger.debug(f"✅ 找到字段 '{variant}'，开始模式匹配")

                patterns = [
                    rf'{re.escape(variant)}\s*[:：]\s*_+',  # 冒号后跟下划线
                    rf'{re.escape(variant)}\s*[:：]\s+$',  # 冒号后跟空格到行尾（修复重复\s问题）
                    rf'{re.escape(variant)}\s*[:：]\s*[_\s]*$',  # 冒号后跟下划线或空格
                    rf'{re.escape(variant)}\s*[:：]\s*[_\s]+[。\.]',  # 冒号后跟下划线，以句号结束
                    rf'{re.escape(variant)}(?=\s+(?!.*_))',  # 字段名后跟空格（插入式填空，不含下划线）
                    rf'{re.escape(variant)}\s+[_\s]+$',  # 空格后跟下划线
                    rf'{re.escape(variant)}\s*[:：]\s*[_\s]+[（(][^）)]*章[^）)]*[）)]',  # 公章格式：供应商名称：___（加盖公章）
                ]

                for i, pattern in enumerate(patterns, 1):
                    self.logger.debug(f"🔍 尝试传统模式{i}: {pattern}")
                    match = re.search(pattern, new_text)
                    if match:
                        self.logger.info(f"✅ 传统模式{i}匹配成功: '{match.group()}'")
                        company_name = info.get('companyName', '')
                        self.logger.debug(f"📝 准备填入公司名称: '{company_name}'")

                        if company_name:
                            original_text = new_text

                            # 根据匹配的模式选择不同的替换策略
                            if i == 2:  # 第2个模式：纯空格替换
                                self.logger.debug(f"🔄 使用纯空格替换策略")
                                # 替换冒号后的所有空格，保留冒号
                                space_pattern = rf'({re.escape(variant)}\s*[:：])\s+$'
                                new_text = re.sub(space_pattern, rf'\1{company_name}', new_text)
                            elif i == 5:  # 第5个模式：插入式填空
                                self.logger.debug(f"🔄 使用插入式替换策略")
                                # 在字段名后直接插入内容，保持空格布局
                                insert_pattern = rf'{re.escape(variant)}(?=\s+)'
                                new_text = re.sub(insert_pattern, f'{variant}{company_name}', new_text)
                            elif i == 7:  # 第7个模式：公章格式
                                self.logger.debug(f"🔄 使用公章格式替换策略")
                                # 精确替换空格/下划线部分，保留公章括号
                                stamp_pattern = rf'(?P<prefix>{re.escape(variant)}\s*[:：]\s*)(?P<spaces>[_\s]+)(?P<stamp>[（(][^）)]*章[^）)]*[）)])'
                                new_text = re.sub(stamp_pattern, rf'\g<prefix>{company_name}\g<stamp>', new_text)
                            else:  # 其他模式：标准替换
                                self.logger.debug(f"🔄 使用标准替换策略")
                                # 多字段格式处理
                                multi_field_pattern = rf'(?P<prefix>{re.escape(variant)}\s*[:：]\s*)(?P<underscores>_+)(?P<suffix>\s+[^\s_]+[:：])'
                                # 单字段格式处理
                                single_field_pattern = rf'(?P<prefix>{re.escape(variant)}\s*[:：]\s*)(?P<underscores>_+)(?P<suffix>$|[。\.])'
                                # 无下划线格式处理
                                no_underscore_pattern = rf'(?P<prefix>{re.escape(variant)}\s*[:：]\s*)(?P<suffix>$)'

                                if re.search(multi_field_pattern, new_text):
                                    self.logger.debug(f"🔄 使用多字段模式替换")
                                    new_text = re.sub(multi_field_pattern, rf'\g<prefix>{company_name}\g<suffix>', new_text)
                                elif re.search(single_field_pattern, new_text):
                                    self.logger.debug(f"🔄 使用单字段模式替换")
                                    new_text = re.sub(single_field_pattern, rf'\g<prefix>{company_name}\g<suffix>', new_text)
                                elif re.search(no_underscore_pattern, new_text):
                                    self.logger.debug(f"🔄 使用无下划线模式替换")
                                    new_text = re.sub(no_underscore_pattern, rf'\g<prefix>{company_name}', new_text)
                                else:
                                    self.logger.debug(f"🔄 使用备用简单模式替换")
                                    simple_pattern = rf'(?P<prefix>{re.escape(variant)}\s*[:：]\s*)(?P<underscores>_+)'
                                    new_text = re.sub(simple_pattern, rf'\g<prefix>{company_name}', new_text)

                            self.logger.info(f"🔄 替换前: '{original_text}'")
                            self.logger.info(f"🔄 替换后: '{new_text}'")
                            self.logger.info(f"填空规则: {variant} 填入 {company_name}")
                            fill_count += 1
                            break  # 找到一个模式就跳出内层循环
                        else:
                            self.logger.warning(f"⚠️  公司名称为空，跳过填写")
                    else:
                        self.logger.debug(f"❌ 传统模式{i}不匹配")

                # 如果找到匹配的变体，跳出外层循环
                if fill_count > 0:
                    break

        # 处理采购人信息的填空
        for variant in self.purchaser_variants:
            # 检查字段是否存在于文本中
            if variant not in new_text:
                continue
                
            patterns = [
                rf'{re.escape(variant)}\s*[:：]\s*[_\s]*$',
                rf'{re.escape(variant)}\s*[:：]\s*[_\s]+[。\.]',
                rf'{re.escape(variant)}\s+[_\s]+$',
                rf'致\s*[:：]\s*{re.escape(variant)}\s*$',  # 支持"致：采购人"格式
            ]
            
            for pattern in patterns:
                if re.search(pattern, new_text):
                    purchaser_name = info.get('purchaserName', '')
                    if purchaser_name:
                        # 特殊处理"致：采购人"格式
                        if '致' in pattern:
                            replace_pattern = rf'(致\s*[:：]\s*){re.escape(variant)}\s*$'
                            new_text = re.sub(replace_pattern, rf'\1{purchaser_name}', new_text)
                        else:
                            # 检查是否是纯空格情况
                            if re.search(rf'{re.escape(variant)}\s*[:：]\s*\s+$', new_text):
                                # 纯空格替换策略
                                replace_pattern = rf'({re.escape(variant)}\s*[:：])\s+$'
                                new_text = re.sub(replace_pattern, rf'\g<1>{purchaser_name}', new_text)
                            else:
                                # 标准格式：只替换匹配字段后面的下划线
                                replace_pattern = rf'({re.escape(variant)}\s*[:：]\s*)(_+)'
                                new_text = re.sub(replace_pattern, rf'\g<1>{purchaser_name}', new_text)
                        self.logger.info(f"填空规则: {variant} 填入 {purchaser_name}")
                        fill_count += 1
                        break
        
        # 处理其他字段的填空（包括地址、邮编、电话、邮箱等）
        for field_key, variants in self.field_variants.items():
            self.logger.debug(f"🔎 处理字段类型: {field_key}")
            
            for variant in variants:
                self.logger.debug(f"🔍 检查字段变体: '{variant}' (类型: {field_key})")
                
                # 检查字段是否存在于文本中
                if variant not in new_text:
                    self.logger.debug(f"❌ 字段 '{variant}' 不在段落文本中，跳过")
                    continue
                    
                self.logger.debug(f"✅ 找到字段 '{variant}'，开始模式匹配")
                
                patterns = [
                    rf'{re.escape(variant)}\s*[:：]\s*_+',  # 多字段支持：地址：___ 邮编：___
                    rf'{re.escape(variant)}\s*[:：]\s*$',    # 无下划线支持：电子邮箱：
                    rf'{re.escape(variant)}\s*[:：]\s*[_\s]*$',
                    rf'{re.escape(variant)}\s*[:：]\s*[_\s]+[。\.]',
                    rf'{re.escape(variant)}(?=\s+(?!.*_))',  # 字段名后跟空格（插入式填空，不含下划线）
                    rf'{re.escape(variant)}\s+[_\s]+$',  # 空格后跟下划线
                    rf'{re.escape(variant)}\s*[:：]\s*[_\s]+[（(][^）)]*章[^）)]*[）)]',  # 公章格式：供应商名称：___（加盖公章）
                ]
                
                for i, pattern in enumerate(patterns, 1):
                    self.logger.debug(f"🔍 尝试模式{i}: {pattern}")
                    match = re.search(pattern, new_text)
                    if match:
                        self.logger.info(f"✅ 模式{i}匹配成功: '{match.group()}'")

                        # 职位字段的智能处理
                        if field_key == 'position':
                            try:
                                self.logger.info(f"🧠 检测到职位字段，启动智能上下文识别")
                                context_type = self._detect_position_context(text)

                                if context_type == 'authorized_person':
                                    value = info.get('authorizedPersonPosition', '')
                                    if value:
                                        self.logger.info(f"📝 选择被授权人职务: '{value}'")
                                    else:
                                        self.logger.warning(f"⚠️  被授权人职务数据为空，尝试使用法定代表人职位")
                                        value = info.get('legalRepresentativePosition', '')
                                        self.logger.info(f"📝 回退使用法定代表人职位: '{value}'")
                                else:  # legal_representative
                                    value = info.get('legalRepresentativePosition', '')
                                    if value:
                                        self.logger.info(f"📝 选择法定代表人职位: '{value}'")
                                    else:
                                        self.logger.warning(f"⚠️  法定代表人职位数据为空，尝试使用被授权人职务")
                                        value = info.get('authorizedPersonPosition', '')
                                        self.logger.info(f"📝 回退使用被授权人职务: '{value}'")

                            except Exception as e:
                                self.logger.error(f"❌ 智能职位处理发生异常: {e}")
                                # 异常情况下使用默认处理方式
                                value = info.get('legalRepresentativePosition', '') or info.get('authorizedPersonPosition', '')
                                self.logger.info(f"📝 异常处理：使用默认职位数据: '{value}'")
                        else:
                            # 其他字段的常规处理 - 直接获取字段值（统一映射已处理多源映射）
                            value = info.get(field_key, '')

                        self.logger.debug(f"📝 字段 {field_key} 值获取: {value}")
                        
                        if value:
                            original_text = new_text
                            self.logger.debug(f"🔄 开始执行精确替换，原文: '{original_text}'")
                            
                            # 根据匹配的模式选择不同的替换策略
                            if i == 2:  # 第2个模式：无下划线支持，包含纯空格处理
                                # 检查是否是纯空格情况
                                if re.search(rf'{re.escape(variant)}\s*[:：]\s*\s+$', new_text):
                                    self.logger.debug(f"🔄 使用纯空格替换策略")
                                    # 替换冒号后的所有空格，保留冒号和字段名
                                    space_pattern = rf'({re.escape(variant)}\s*[:：])\s+$'
                                    new_text = re.sub(space_pattern, rf'\g<1>{value}', new_text)
                                else:
                                    self.logger.debug(f"🔄 使用无下划线模式替换")
                                    # 处理直接结尾的情况：字段：
                                    no_underscore_pattern = rf'(?P<prefix>{re.escape(variant)}\s*[:：]\s*)(?P<suffix>$)'
                                    new_text = re.sub(no_underscore_pattern, rf'\g<prefix>{value}', new_text)
                            elif i == 5:  # 第5个模式：插入式填空
                                self.logger.debug(f"🔄 使用插入式替换策略")
                                # 在字段名后直接插入内容，保持空格布局
                                insert_pattern = rf'{re.escape(variant)}(?=\s+)'
                                new_text = re.sub(insert_pattern, f'{variant}{value}', new_text)
                            elif i == 7:  # 第7个模式：公章格式
                                self.logger.debug(f"🔄 使用公章格式替换策略")
                                # 精确替换空格/下划线部分，保留公章括号
                                stamp_pattern = rf'(?P<prefix>{re.escape(variant)}\s*[:：]\s*)(?P<spaces>[_\s]+)(?P<stamp>[（(][^）)]*章[^）)]*[）)])'
                                new_text = re.sub(stamp_pattern, rf'\g<prefix>{value}\g<stamp>', new_text)
                            else:  # 其他模式：标准替换
                                self.logger.debug(f"🔄 使用标准替换策略")
                                # 精确替换：分别处理多字段、单字段和无下划线情况
                                # 模式1：多字段格式 "字段：___ 其他字段："
                                multi_field_pattern = rf'(?P<prefix>{re.escape(variant)}\s*[:：]\s*)(?P<underscores>_+)(?P<suffix>\s+[^\s_]+[:：])'
                                # 模式2：单字段格式 "字段：___" (到行尾或句号)  
                                single_field_pattern = rf'(?P<prefix>{re.escape(variant)}\s*[:：]\s*)(?P<underscores>_+)(?P<suffix>$|[。\.])'
                                # 模式3：无下划线格式 "字段：" (直接在行尾)
                                no_underscore_pattern = rf'(?P<prefix>{re.escape(variant)}\s*[:：]\s*)(?P<suffix>$)'
                                
                                if re.search(multi_field_pattern, new_text):
                                    self.logger.debug(f"🔄 使用多字段模式替换")
                                    new_text = re.sub(multi_field_pattern, rf'\g<prefix>{value}\g<suffix>', new_text)
                                elif re.search(single_field_pattern, new_text):
                                    self.logger.debug(f"🔄 使用单字段模式替换")
                                    new_text = re.sub(single_field_pattern, rf'\g<prefix>{value}\g<suffix>', new_text)
                                elif re.search(no_underscore_pattern, new_text):
                                    self.logger.debug(f"🔄 使用无下划线模式替换")
                                    new_text = re.sub(no_underscore_pattern, rf'\g<prefix>{value}', new_text)
                                else:
                                    self.logger.debug(f"🔄 使用备用简单模式替换")
                                    simple_pattern = rf'(?P<prefix>{re.escape(variant)}\s*[:：]\s*)(?P<underscores>_+)'
                                    new_text = re.sub(simple_pattern, rf'\g<prefix>{value}', new_text)
                            
                            self.logger.info(f"🔄 替换前: '{original_text}'")
                            self.logger.info(f"🔄 替换后: '{new_text}'")
                            self.logger.info(f"填空规则: {variant} 填入 {value}")
                            fill_count += 1
                            break  # 找到一个模式就跳出内层循环
                        else:
                            self.logger.warning(f"⚠️  字段 '{variant}' 的值为空，跳过填写")
                    else:
                        self.logger.debug(f"❌ 模式{i}不匹配")
        
        # 处理文档末尾的"年月日"格式（独立规则）
        date_end_patterns = [
            r'(\s+)年(\s+)月(\s+)日(\s*)$',  # 末尾格式：空格+年+空格+月+空格+日
            r'(\n\s*)年(\s+)月(\s+)日(\s*)$', # 换行+空格+年月日格式
            r'(\s+)年(\s+)月(\s+)日',        # 通用格式：空格+年+空格+月+空格+日
        ]

        for i, pattern in enumerate(date_end_patterns, 1):
            self.logger.debug(f"🔍 尝试年月日模式{i}: {pattern}")
            match = re.search(pattern, new_text)
            if match:
                self.logger.info(f"✅ 年月日模式{i}匹配成功: '{match.group()}'")
                date_value = info.get('date', '')
                self.logger.debug(f"📝 准备填入日期: '{date_value}'")

                if date_value:
                    original_text = new_text
                    formatted_date = self._format_date(date_value)
                    self.logger.debug(f"📅 格式化后的日期: '{formatted_date}'")

                    # 根据模式类型进行不同的替换策略
                    if i == 2:  # 换行+空格+年月日格式
                        # 保留换行符，只替换年月日部分
                        new_text = re.sub(pattern, rf'\n{formatted_date}', new_text)
                    else:
                        # 标准替换：整个匹配的年月日模式为完整日期
                        new_text = re.sub(pattern, formatted_date, new_text)

                    self.logger.info(f"🔄 替换前: '{original_text}'")
                    self.logger.info(f"🔄 替换后: '{new_text}'")
                    self.logger.info(f"日期填空: {formatted_date}")
                    fill_count += 1
                    break
                else:
                    self.logger.warning(f"⚠️  日期值为空，跳过年月日格式填写")
            else:
                self.logger.debug(f"❌ 年月日模式{i}不匹配")

        # 如果有任何填充，更新段落文本
        if fill_count > 0:
            self.logger.info(f"📊 段落处理完成，共填充 {fill_count} 个字段")
            self.logger.debug(f"🔄 最终文本: '{new_text}'")
            self._update_paragraph_text(paragraph, new_text)
            return True
        else:
            self.logger.debug(f"📊 段落处理完成，未找到任何可填充字段")

        return False
    
    def _process_table(self, table: Table, info: Dict[str, Any]) -> Dict[str, Any]:
        """处理表格中的信息填写"""
        count = 0
        
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    if self._try_fill_rule(paragraph, info):
                        count += 1
                    elif self._try_replacement_rule(paragraph, info):
                        count += 1
        
        return {'count': count}
    
    def _format_date(self, date_str: str) -> str:
        """格式化日期字符串"""
        # 移除多余的空格
        date_str = re.sub(r'\s+', '', date_str)
        
        # 尝试匹配常见日期格式
        patterns = [
            (r'(\d{4})-(\d{1,2})-(\d{1,2})', r'\1年\2月\3日'),
            (r'(\d{4})/(\d{1,2})/(\d{1,2})', r'\1年\2月\3日'),
            (r'(\d{4})\.(\d{1,2})\.(\d{1,2})', r'\1年\2月\3日'),
        ]
        
        for pattern, replacement in patterns:
            if re.match(pattern, date_str):
                return re.sub(pattern, replacement, date_str)
        
        # 如果已经是中文格式，直接返回
        if '年' in date_str and '月' in date_str and '日' in date_str:
            return date_str
        
        # 默认返回原字符串
        return date_str
    
    def _update_paragraph_text(self, paragraph: Paragraph, new_text: str):
        """更新段落文本，保持格式"""
        # 记录更新前的状态
        original_text = paragraph.text
        self.logger.debug(f"📝 开始更新段落文本")
        self.logger.debug(f"📝 更新前文本: '{original_text}'")
        self.logger.debug(f"📝 目标文本: '{new_text}'")
        
        # 保存第一个run的格式
        if paragraph.runs:
            self.logger.debug(f"📝 段落有 {len(paragraph.runs)} 个runs，保持格式")
            first_run = paragraph.runs[0]
            # 保存格式属性
            font = first_run.font
            bold = font.bold
            italic = font.italic
            underline = font.underline
            font_size = font.size
            font_name = font.name
            
            self.logger.debug(f"📝 保存的格式: bold={bold}, italic={italic}, size={font_size}, name={font_name}")
            
            # 清空段落
            paragraph.clear()
            self.logger.debug(f"📝 段落已清空")
            
            # 添加新文本并恢复格式
            new_run = paragraph.add_run(new_text)
            if bold is not None:
                new_run.font.bold = bold
            if italic is not None:
                new_run.font.italic = italic
            if underline is not None:
                new_run.font.underline = underline
            if font_size:
                new_run.font.size = font_size
            if font_name:
                new_run.font.name = font_name
            
            self.logger.debug(f"📝 新文本已添加并恢复格式")
        else:
            # 如果没有runs，直接设置文本
            self.logger.debug(f"📝 段落无runs，直接设置文本")
            paragraph.text = new_text
        
        # 验证更新结果
        actual_new_text = paragraph.text
        if actual_new_text == new_text:
            self.logger.info(f"✅ 段落更新成功: '{original_text}' → '{actual_new_text}'")
        elif actual_new_text == original_text:
            self.logger.error(f"❌ 段落更新失败: 文本没有变化，仍为 '{original_text}'")
        else:
            self.logger.warning(f"⚠️  段落更新异常: 期望 '{new_text}'，实际为 '{actual_new_text}'")
    
    def _post_process(self, doc: Document):
        """后处理：清理多余的占位符和格式"""
        for paragraph in doc.paragraphs:
            text = paragraph.text
            
            # 清理多余的下划线
            text = re.sub(r'_{3,}', '', text)
            
            # 清理多余的空格（保留表格对齐所需的空格）
            if not re.search(r'\s{8,}', text):  # 不是表格式布局
                text = re.sub(r'\s{3,}', '  ', text)
            
            # 清理多余的冒号
            text = re.sub(r'[:：]{2,}', '：', text)
            
            # 标准化冒号
            text = re.sub(r':', '：', text)
            
            # 去除多余的年月日标识
            text = re.sub(r'(\d{4}年\d{1,2}月\d{1,2}日)\s*年\s*月\s*日', r'\1', text)
            
            if text != paragraph.text:
                self._update_paragraph_text(paragraph, text.strip())