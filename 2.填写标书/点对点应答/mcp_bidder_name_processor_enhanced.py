#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP投标人名称处理器
专门处理文档中投标人名称的填写
支持两种填写方式：
1. 替换内容（如将"（公司全称）"替换为公司名称）
2. 在空格处填写（将空格替换为公司名称，格式与标签保持一致）
"""

import os
import re
import logging
from datetime import datetime
from typing import Dict, List, Optional

try:
    from docx import Document
    from docx.shared import Inches, Mm
    from docx.enum.text import WD_PARAGRAPH_ALIGNMENT, WD_UNDERLINE
    from docx.text.paragraph import Paragraph
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

# 配置日志
logger = logging.getLogger(__name__)


class MCPBidderNameProcessor:
    """MCP投标人名称处理器 - 专门处理投标人名称填写"""
    
    def __init__(self):
        if not DOCX_AVAILABLE:
            raise ImportError("请安装python-docx库：pip install python-docx")
        
        # 投标人名称匹配规则 - 按优先级排序
        self.bidder_patterns = [
            # === 第一种方式：替换内容 ===
            # 格式11: "（请填写供应商名称）" - 提示性括号内容替换
            {
                'pattern': re.compile(r'(?P<prefix>[\(（])\s*(?P<content>请填写\s*供应商名称)\s*(?P<suffix>[\)）])'),
                'type': 'replace_content',
                'description': '提示性括号内容替换 - 供应商名称'
            },
            
            # 格式12: "（请填写投标人名称）" - 提示性括号内容替换
            {
                'pattern': re.compile(r'(?P<prefix>[\(（])\s*(?P<content>请填写\s*投标人名称)\s*(?P<suffix>[\)）])'),
                'type': 'replace_content',
                'description': '提示性括号内容替换 - 投标人名称'
            },
            
            # 格式13: "（请填写公司名称）" - 提示性括号内容替换
            {
                'pattern': re.compile(r'(?P<prefix>[\(（])\s*(?P<content>请填写\s*公司名称)\s*(?P<suffix>[\)）])'),
                'type': 'replace_content',
                'description': '提示性括号内容替换 - 公司名称'
            },
            
            # 格式1: " (供应商全称)  " - 括号内容替换，保持字体和大小
            {
                'pattern': re.compile(r'(?P<prefix>[\(（])\s*(?P<content>供应商全称)\s*(?P<suffix>[\)）])'),
                'type': 'replace_content',
                'description': '括号内容替换 - 供应商全称'
            },
            
            # 格式10: "（供应商名称）" - 括号内容替换，保持字体和大小
            {
                'pattern': re.compile(r'(?P<prefix>[\(（])\s*(?P<content>供应商名称)\s*(?P<suffix>[\)）])'),
                'type': 'replace_content',
                'description': '括号内容替换 - 供应商名称'
            },
            
            # === 第二种方式：在空格处填写 ===
            # 格式6: "公司名称（全称、盖章）：________________" - 横线上填写（允许前面有空格）
            {
                'pattern': re.compile(r'^\s*(?P<label>公司名称（全称、盖章）)\s*(?P<sep>[:：])\s*(?P<placeholder>_{3,})\s*$'),
                'type': 'fill_space',
                'description': '横线上填写 - 公司名称（全称、盖章）'
            },
            
            # 格式6-2: "公司名称（全称、盖章）：" - 冒号后填写（无占位符，允许前面有空格）
            {
                'pattern': re.compile(r'^\s*(?P<label>公司名称（全称、盖章）)\s*(?P<sep>[:：])\s*(?P<placeholder>)\s*$'),
                'type': 'fill_space',
                'description': '冒号后填写 - 公司名称（全称、盖章）'
            },
            
            # 格式7: "公司名称（盖章）：" - 冒号后填写
            {
                'pattern': re.compile(r'^(?P<label>公司名称（盖章）)\s*(?P<sep>[:：])\s*(?P<placeholder>)\s*$'),
                'type': 'fill_space',
                'description': '冒号后填写 - 公司名称（盖章）'
            },
            
            # 格式5: "供应商全称及公章：  " - 冒号后填写（最少有空格）
            {
                'pattern': re.compile(r'^(?P<label>供应商全称及公章)\s*(?P<sep>[:：])\s*(?P<placeholder>\s+)\s*$'),
                'type': 'fill_space',
                'description': '冒号后填写 - 供应商全称及公章'
            },
            
            # 格式9: "供应商名称：________________（公章）" - 下划线处填写，带公章后缀
            {
                'pattern': re.compile(r'^(?P<label>供应商名称)\s*(?P<sep>[:：])\s*(?P<placeholder>_{3,})\s*(?P<suffix>（[^）]*公章[^）]*）|\([^)]*公章[^)]*\))\s*$'),
                'type': 'fill_space',
                'description': '下划线处填写 - 供应商名称（公章）'
            },
            
            # 格式9-2: "供应商名称：                                （加盖公章）" - 中间空格处填写，带公章后缀
            {
                'pattern': re.compile(r'^(?P<label>供应商名称)\s*(?P<sep>[:：])\s*(?P<placeholder>\s{10,})\s*(?P<suffix>（[^）]*公章[^）]*）|\([^)]*公章[^)]*\))\s*$'),
                'type': 'fill_space',
                'description': '中间空格处填写 - 供应商名称（公章）'
            },
            
            # 格式3: "供应商名称：                                        " - 空格处填写（长空格）
            {
                'pattern': re.compile(r'^(?P<label>供应商名称)\s*(?P<sep>[:：])\s*(?P<placeholder>\s{20,})\s*$'),
                'type': 'fill_space',
                'description': '空格处填写 - 供应商名称（长空格）'
            },
            
            # 格式4: "供应商名称：               " - 中等长度空格
            {
                'pattern': re.compile(r'^(?P<label>供应商名称)\s*(?P<sep>[:：])\s*(?P<placeholder>\s{10,19})\s*$'),
                'type': 'fill_space',
                'description': '空格处填写 - 供应商名称（中等空格）'
            },
            
            # 格式2: "供应商名称：___________________" - 横线上填写
            {
                'pattern': re.compile(r'^(?P<label>供应商名称)\s*(?P<sep>[:：])\s*(?P<placeholder>_{3,})\s*$'),
                'type': 'fill_space',
                'description': '横线上填写 - 供应商名称'
            },
            
            # 格式8: "供应商名称：" - 冒号后填写（最通用，允许前面有空格，放在最后）
            {
                'pattern': re.compile(r'^\s*(?P<label>供应商名称)\s*(?P<sep>[:：])\s*(?P<placeholder>)\s*$'),
                'type': 'fill_space',
                'description': '冒号后填写 - 供应商名称（通用）'
            },
            
            # 投标人名称相关
            {
                'pattern': re.compile(r'^(?P<label>投标人名称(?:（公章）|\(公章\))?)\s*(?P<sep>[:：]?)\s*(?P<placeholder>[_\-\u2014\s\u3000]*|＿*|——*)\s*$'),
                'type': 'fill_space',
                'description': '投标人名称相关填写'
            },
        ]
        
    def process_bidder_name(self, input_file: str, output_file: str, company_name: str) -> Dict:
        """
        处理投标人名称填写
        
        Args:
            input_file: 输入文件路径
            output_file: 输出文件路径  
            company_name: 公司名称
            
        Returns:
            处理结果字典
        """
        logger.info(f"开始MCP投标人名称处理: {input_file}")
        logger.info(f"使用公司名称: {company_name}")
        
        try:
            # 打开Word文档
            doc = Document(input_file)
            
            # 统计信息
            stats = {
                'total_replacements': 0,
                'replace_content_count': 0,
                'fill_space_count': 0,
                'patterns_found': []
            }
            
            # 遍历所有段落
            for para_idx, paragraph in enumerate(doc.paragraphs):
                if not paragraph.text.strip():
                    continue
                
                # 记录段落处理前的文本
                original_para_text = paragraph.text
                logger.info(f"处理段落 #{para_idx}: '{original_para_text}'")
                    
                # 尝试匹配每个规则
                paragraph_processed = False  # 添加标志，确保每个段落只处理一次
                for rule_idx, rule in enumerate(self.bidder_patterns):
                    if paragraph_processed:
                        break  # 如果段落已处理，跳出规则循环
                        
                    pattern = rule['pattern']
                    match = pattern.search(original_para_text)  # 使用原始文本匹配
                    
                    if match:
                        logger.info(f"匹配到规则 #{rule_idx+1}: {rule['description']}")
                        logger.info(f"匹配文本: '{match.group(0)}'")
                        
                        success = False
                        # 根据类型选择处理方式
                        if rule['type'] == 'replace_content':
                            success = self._replace_content_method(paragraph, match, company_name, rule)
                            if success:
                                stats['replace_content_count'] += 1
                        elif rule['type'] == 'fill_space':
                            success = self._fill_space_method(paragraph, match, company_name, rule)  
                            if success:
                                stats['fill_space_count'] += 1
                                
                        if success:
                            stats['total_replacements'] += 1
                            stats['patterns_found'].append({
                                'rule_index': rule_idx + 1,
                                'description': rule['description'],
                                'type': rule['type'],
                                'original_text': match.group(0),
                                'paragraph_index': para_idx
                            })
                            logger.info(f"处理后: '{paragraph.text}'")
                            paragraph_processed = True  # 标记段落已处理
                            # 不再需要break，因为我们用flag控制了循环
            
            # 保存文档
            doc.save(output_file)
            logger.info(f"MCP投标人名称处理完成，保存到: {output_file}")
            logger.info(f"处理统计: 总计{stats['total_replacements']}次, 替换内容{stats['replace_content_count']}次, 空格填写{stats['fill_space_count']}次")
            
            return {
                'success': True,
                'stats': stats,
                'message': f'成功处理{stats["total_replacements"]}个投标人名称字段'
            }
            
        except Exception as e:
            logger.error(f"MCP投标人名称处理失败: {e}", exc_info=True)
            return {
                'success': False,
                'error': f'处理失败: {str(e)}'
            }
    
    def _replace_content_method(self, paragraph: Paragraph, match, company_name: str, rule: dict) -> bool:
        """
        第一种填写方式：替换内容
        如将"（公司全称）"替换为"（智慧足迹数据科技有限公司）"，格式保持不变
        """
        try:
            # 获取匹配的组
            groups = match.groupdict()
            prefix = groups.get('prefix', '')
            content = groups.get('content', '')  
            suffix = groups.get('suffix', '')
            
            if not content:
                return False
            
            # 找到包含内容的run并替换
            for run in paragraph.runs:
                if content in run.text:
                    # 保存原始格式
                    original_font = run.font
                    
                    # 替换内容，保持括号
                    new_text = run.text.replace(f"{prefix}{content}{suffix}", f"{prefix}{company_name}{suffix}")
                    run.text = new_text
                    
                    logger.info(f"替换内容方式: {content} -> {company_name}")
                    
                    return True
                    
            return False
            
        except Exception as e:
            logger.error(f"替换内容方式处理失败: {e}")
            return False
    
    def _fill_space_method(self, paragraph: Paragraph, match, company_name: str, rule: dict) -> bool:
        """
        第二种填写方式：在空格处填写
        增强版：支持跨run拆分处理
        """
        try:
            # 获取匹配的组
            groups = match.groupdict()
            label = groups.get('label', '')
            sep = groups.get('sep', '')
            placeholder = groups.get('placeholder', '')
            suffix = groups.get('suffix', '')
            
            if not label:
                return False
            
            # 特殊处理：检查是否是跨run拆分的情况（如"供应商名称："被拆分）
            # 注意：只有当文本恰好是标签+分隔符（无前导空格）时才认为是跨run拆分
            full_text = ''.join(run.text for run in paragraph.runs)
            if full_text == f"{label}{sep}" and not placeholder:
                logger.info(f"检测到跨run拆分情况: '{full_text}'")
                return self._enhanced_cross_run_fill(paragraph, label, sep, company_name)
            
            # 构建要查找和替换的模式
            if suffix:  # 有后缀的情况，如（加盖公章）
                search_pattern = f"{label}{sep}{placeholder}{suffix}"
                replacement = f"{label}{sep}{company_name} {suffix}"
            else:  # 无后缀的情况
                if placeholder:  # 有占位符（空格或下划线）
                    search_pattern = f"{label}{sep}{placeholder}"
                    replacement = f"{label}{sep}{company_name}"
                else:  # 无占位符，直接在冒号后添加
                    search_pattern = f"{label}{sep}"
                    replacement = f"{label}{sep}{company_name}"
            
            logger.info(f"查找模式: '{search_pattern}' -> 替换为: '{replacement}'")
            
            # 寻找包含整个匹配文本的run并替换
            found_and_replaced = False
            for run in paragraph.runs:
                if search_pattern in run.text:
                    font_name = run.font.name if run.font.name else "默认"
                    logger.info(f"找到匹配run: '{run.text}'，字体={font_name}")
                    # 直接在run中替换内容，保持原有格式
                    run.text = run.text.replace(search_pattern, replacement)
                    logger.info(f"替换后: '{run.text}'，字体={font_name}")
                    found_and_replaced = True
                    break
            
            # 如果没找到完整匹配，尝试分别查找标签和占位符
            if not found_and_replaced:
                logger.info("未找到完整匹配，尝试分别处理")
                for run in paragraph.runs:
                    # 查找包含占位符的部分
                    if placeholder and placeholder in run.text:
                        logger.info(f"找到包含占位符的run: '{run.text}'")
                        # 只替换第一个匹配的占位符，避免重复替换
                        run.text = run.text.replace(placeholder, company_name, 1)
                        logger.info(f"替换占位符后: '{run.text}'")
                        found_and_replaced = True
                        break
            
            if found_and_replaced:
                logger.info(f"空格填写方式成功: 填写'{company_name}'，保持原有格式")
                
                # 清理可能的尾部空格和下划线
                self._clean_trailing_spaces(paragraph)
                
                # 清理公司名称后面的多余占位符空格
                self._cleanup_trailing_placeholders_after_company(paragraph, company_name)
                
                return True
            else:
                logger.info("尝试跨run处理分散的文本")
                return self._handle_cross_run_text(paragraph, match, company_name, rule)
                
        except Exception as e:
            logger.error(f"填空方式处理失败: {e}")
            return False
    
    def _enhanced_cross_run_fill(self, paragraph: Paragraph, label: str, sep: str, company_name: str) -> bool:
        """
        增强的跨run填写方法
        专门处理像"供应商名称："这样被拆分成两个run的情况
        保留原有格式，只在适当位置添加公司名称
        """
        try:
            logger.info(f"使用增强跨run填写: 标签='{label}', 分隔符='{sep}'")
            
            # 寻找包含分隔符的run，在其后添加公司名称
            for i, run in enumerate(paragraph.runs):
                if sep in run.text:
                    # 在包含分隔符的run后面添加公司名称和空格
                    if run.text.endswith(sep):
                        # 如果run以分隔符结尾，直接添加
                        run.text = run.text + " " + company_name
                    else:
                        # 如果分隔符在中间，在分隔符后面插入
                        run.text = run.text.replace(sep, sep + " " + company_name, 1)
                    
                    # 给公司名称添加下划线（如果需要）
                    run.underline = True
                    
                    logger.info(f"增强跨run填写成功: '{label}{sep}' + '{company_name}'（带下划线）")
                    return True
            
            # 如果没找到分隔符，尝试在最后一个run添加
            if paragraph.runs:
                last_run = paragraph.runs[-1]
                # 添加公司名称到最后一个run
                if not last_run.text.strip():
                    # 如果最后一个run是空的或只有空格，替换为公司名称
                    last_run.text = company_name
                else:
                    # 否则添加到末尾
                    last_run.text = last_run.text + company_name
                
                last_run.underline = True
                logger.info(f"增强跨run填写成功: 在最后run添加'{company_name}'（带下划线）")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"增强跨run填写失败: {e}")
            return False
    
    def _handle_cross_run_text(self, paragraph: Paragraph, match, company_name: str, rule: dict) -> bool:
        """
        处理跨run分散的文本情况
        当标签和占位符分布在不同run中时使用
        """
        try:
            groups = match.groupdict()
            label = groups.get('label', '')
            sep = groups.get('sep', '')
            
            # 查找包含标签的run
            label_run = None
            for run in paragraph.runs:
                if label in run.text:
                    label_run = run
                    break
            
            if not label_run:
                logger.warning(f"未能找到包含标签'{label}'的run")
                return False
            
            # 智能地在适当位置添加公司名称
            # 如果标签run已经包含分隔符，直接添加公司名称
            if sep in label_run.text:
                # 在现有内容基础上添加，避免重复分隔符
                if label_run.text.endswith(sep):
                    label_run.text = label_run.text + " " + company_name
                else:
                    # 分隔符在中间，在分隔符后插入
                    label_run.text = label_run.text.replace(sep, f"{sep} {company_name}", 1)
            else:
                # 如果标签run不包含分隔符，添加分隔符和公司名称
                label_run.text = label_run.text + f"{sep} {company_name}"
            
            # 清空后续run中的空格、占位符或分隔符
            for run in paragraph.runs:
                if run != label_run:
                    # 清空包含分隔符、空格或下划线的run
                    if (run.text.strip() == '' or '_' in run.text or 
                        run.text.strip() == sep or run.text.isspace()):
                        run.text = ""
            
            logger.info(f"跨run处理成功: '{label}{sep} {company_name}'")
            
            # 清理公司名称后面的多余占位符空格
            self._cleanup_trailing_placeholders_after_company(paragraph, company_name)
            
            return True
            
        except Exception as e:
            logger.error(f"跨run处理失败: {e}")
            return False
    
    def _clean_trailing_spaces(self, paragraph: Paragraph) -> None:
        """
        清理段落末尾的多余空格和下划线
        """
        try:
            # 从后往前检查run
            for run in reversed(paragraph.runs):
                original_text = run.text
                # 移除尾部的空格和下划线
                cleaned_text = re.sub(r'[_\s　]+$', '', run.text)
                if cleaned_text != original_text:
                    run.text = cleaned_text
                    removed_count = len(original_text) - len(cleaned_text)
                    if removed_count > 0:
                        logger.info(f"删除末尾空格下划线: '{original_text}' -> '{cleaned_text}'")
                        logger.info(f"尾部清理完成: 删除了{removed_count}个字符")
                    break  # 只清理最后一个有内容的run
        except Exception as e:
            logger.warning(f"清理尾部字符失败: {e}")
    def _copy_font_format(self, source_run, target_run):
        """复制字体格式"""
        try:
            if hasattr(source_run, 'font') and hasattr(target_run, 'font'):
                source_font = source_run.font
                target_font = target_run.font
                
                # 记录原始字体信息
                logger.info(f"源字体信息: 名称={source_font.name}, 大小={source_font.size}, 粗体={source_font.bold}")
                
                # 复制字体名称 - 尝试多种方式
                if source_font.name:
                    target_font.name = source_font.name
                    logger.info(f"设置目标字体名称为: {source_font.name}")
                else:
                    # 如果字体名称为空，尝试从段落样式获取
                    para_style = source_run._parent.style if hasattr(source_run, '_parent') else None
                    if para_style and hasattr(para_style.font, 'name') and para_style.font.name:
                        target_font.name = para_style.font.name
                        logger.info(f"从段落样式设置字体名称为: {para_style.font.name}")
                
                # 复制字体大小
                if source_font.size:
                    target_font.size = source_font.size
                elif hasattr(source_run, '_parent'):
                    # 尝试从段落样式获取
                    para_style = source_run._parent.style
                    if para_style and hasattr(para_style.font, 'size') and para_style.font.size:
                        target_font.size = para_style.font.size
                
                # 复制其他格式属性
                if source_font.bold is not None:
                    target_font.bold = source_font.bold
                if source_font.italic is not None:
                    target_font.italic = source_font.italic
                    
                # 复制字体颜色
                if source_font.color and hasattr(source_font.color, 'rgb'):
                    if source_font.color.rgb:
                        target_font.color.rgb = source_font.color.rgb
                
                # 验证复制结果
                logger.info(f"目标字体设置后: 名称={target_font.name}, 大小={target_font.size}, 粗体={target_font.bold}")
                        
        except Exception as e:
            logger.error(f"复制字体格式失败: {e}", exc_info=True)
    
    def _apply_saved_format(self, target_run, font_name, font_size, font_bold, font_italic, font_color):
        """应用保存的格式信息到目标run"""
        try:
            if hasattr(target_run, 'font'):
                target_font = target_run.font
                
                # 应用字体名称
                if font_name:
                    target_font.name = font_name
                    logger.info(f"应用字体名称: {font_name}")
                
                # 应用字体大小
                if font_size:
                    target_font.size = font_size
                    logger.info(f"应用字体大小: {font_size}")
                
                # 应用粗体
                if font_bold is not None:
                    target_font.bold = font_bold
                
                # 应用斜体
                if font_italic is not None:
                    target_font.italic = font_italic
                
                # 应用颜色
                if font_color:
                    target_font.color.rgb = font_color
                    
                logger.info(f"格式应用完成: 名称={target_font.name}, 大小={target_font.size}")
                        
        except Exception as e:
            logger.error(f"应用格式失败: {e}", exc_info=True)
    
    def _cleanup_trailing_spaces(self, paragraph: Paragraph, company_name: str):
        """
        清理段落中公司名称后面的多余空格和下划线
        仅删除末尾的纯空格和下划线，保留有汉字的后缀
        """
        try:
            original_text = paragraph.text
            
            # 查找公司名称在文本中的位置
            company_pos = original_text.find(company_name)
            if company_pos == -1:
                logger.debug("未找到公司名称，跳过尾部清理")
                return
            
            # 获取公司名称后面的内容
            after_company = original_text[company_pos + len(company_name):]
            
            # 检查后缀是否只包含空格、下划线等非汉字字符
            # 使用正则匹配末尾的空格和下划线
            trailing_pattern = re.compile(r'^([\s_]+)(.*)$')
            match = trailing_pattern.match(after_company)
            
            if match:
                trailing_chars = match.group(1)  # 空格和下划线
                remaining_text = match.group(2)  # 剩余文本
                
                # 如果剩余文本包含汉字，则保留（如"（加盖公章）"）
                if re.search(r'[\u4e00-\u9fa5]', remaining_text):
                    # 有汉字，只删除公司名称和汉字内容之间的空格下划线
                    cleaned_after = remaining_text
                    logger.info(f"保留汉字后缀，删除中间空格: '{trailing_chars}' -> ''")
                else:
                    # 没有汉字，可以删除所有尾部字符
                    cleaned_after = remaining_text
                    logger.info(f"删除末尾空格下划线: '{trailing_chars}' -> ''")
                
                # 构建新的文本
                before_company = original_text[:company_pos + len(company_name)]
                new_text = before_company + cleaned_after
                
                if new_text != original_text:
                    # 更新段落中的run
                    self._update_paragraph_text(paragraph, original_text, new_text)
                    logger.info(f"尾部清理完成: 删除了{len(original_text) - len(new_text)}个字符")
                else:
                    logger.debug("无需清理尾部空格")
            else:
                logger.debug("公司名称后面无需清理的内容")
                
        except Exception as e:
            logger.error(f"尾部清理失败: {e}", exc_info=True)
    
    def _update_paragraph_text(self, paragraph: Paragraph, old_text: str, new_text: str):
        """更新段落文本，保持格式"""
        try:
            # 查找包含完整旧文本的run并替换
            for run in paragraph.runs:
                if old_text in run.text:
                    run.text = run.text.replace(old_text, new_text)
                    logger.debug(f"更新run文本: '{old_text}' -> '{new_text}'")
                    return True
            
            # 如果没找到包含完整文本的run，尝试更新整个段落
            if paragraph.text == old_text:
                # 清除所有run并重新创建
                for run in paragraph.runs:
                    run.clear()
                if paragraph.runs:
                    paragraph.runs[0].text = new_text
                    logger.debug(f"重建段落文本: '{new_text}'")
                return True
            
            logger.warning("无法更新段落文本")
            return False
            
        except Exception as e:
            logger.error(f"更新段落文本失败: {e}", exc_info=True)
            return False
    
    def _cleanup_extra_placeholders(self, paragraph, company_name: str):
        """清理多余的占位符（主要是长空格），但保留前导空格格式"""
        try:
            import re
            
            full_text = paragraph.text
            if not full_text or company_name not in full_text:
                return
                
            logger.info(f"开始清理占位符: '{full_text}'")
            
            # 查找公司名称在完整文本中的位置，以确定哪些空格需要清理
            company_pos = full_text.find(company_name)
            
            # 清理每个run中的多余占位符
            current_pos = 0
            for run_idx, run in enumerate(paragraph.runs):
                run_text = run.text
                if not run_text:
                    continue
                    
                logger.info(f"  检查run #{run_idx}: '{run_text}'")
                
                # 计算当前run在完整文本中的位置
                run_start_pos = current_pos
                run_end_pos = current_pos + len(run_text)
                current_pos = run_end_pos
                
                # 清理长空格（超过5个连续空格）
                long_spaces = re.findall(r'\s{10,}', run_text)  # 只处理10个以上的长空格
                if long_spaces:
                    cleaned_text = run_text
                    for spaces in long_spaces:
                        space_pos_in_run = cleaned_text.find(spaces)
                        space_pos_in_full_text = run_start_pos + space_pos_in_run
                        
                        # 只清理在公司名称之后的占位符空格
                        if company_pos >= 0 and space_pos_in_full_text > company_pos:
                            # 检查空格前后的内容，决定清理策略
                            before_space = cleaned_text[:space_pos_in_run]
                            after_space = cleaned_text[space_pos_in_run + len(spaces):]
                            
                            # 如果后面是括号或特殊内容，保留适当空格；否则删除
                            if (after_space.startswith('（') or after_space.startswith('(') or 
                                after_space.startswith('为') or after_space.startswith('，') or
                                after_space.startswith('的')):
                                # 保留2个空格用于格式对齐
                                cleaned_text = cleaned_text.replace(spaces, '  ', 1)
                                logger.info(f"    清理长空格（保留2个）: {len(spaces)} -> 2个空格")
                            else:
                                # 完全删除多余空格
                                cleaned_text = cleaned_text.replace(spaces, '', 1)
                                logger.info(f"    清理长空格（删除）: {len(spaces)} -> 0个空格")
                        else:
                            # 在公司名称之前的空格，很可能是前导空格，不要清理
                            logger.info(f"    保留前导空格: {len(spaces)}个空格")
                    
                    if cleaned_text != run_text:
                        run.text = cleaned_text
                        logger.info(f"    清理完成: '{cleaned_text}'")
            
            logger.info(f"占位符清理完成: '{paragraph.text}'")
            
        except Exception as e:
            logger.error(f"清理占位符失败: {e}")

    def _cleanup_trailing_placeholders_after_company(self, paragraph, company_name: str):
        """清理公司名称后面的多余占位符空格，但保留前导空格"""
        try:
            import re
            
            full_text = paragraph.text
            if not full_text or company_name not in full_text:
                return
                
            logger.info(f"开始清理公司名称后的占位符: '{full_text}'")
            
            # 找到公司名称在完整文本中的位置
            company_pos = full_text.find(company_name)
            if company_pos == -1:
                return
                
            company_end_pos = company_pos + len(company_name)
            
            # 清理每个run中的多余占位符
            current_pos = 0
            for run_idx, run in enumerate(paragraph.runs):
                run_text = run.text
                if not run_text:
                    continue
                    
                # 计算当前run在完整文本中的位置
                run_start_pos = current_pos
                run_end_pos = current_pos + len(run_text)
                current_pos = run_end_pos
                
                # 只清理在公司名称之后的run中的占位符空格
                if run_start_pos >= company_end_pos:
                    # 检查是否有长空格占位符
                    long_spaces = re.findall(r'\s{10,}', run_text)
                    if long_spaces:
                        cleaned_text = run_text
                        for spaces in long_spaces:
                            # 清理长空格占位符，但保留2-3个空格用于格式
                            if len(spaces) >= 10:
                                # 如果后面还有其他内容，保留少量空格；否则删除
                                space_pos = cleaned_text.find(spaces)
                                after_space = cleaned_text[space_pos + len(spaces):]
                                
                                if after_space.strip():
                                    # 后面还有内容，保留2个空格
                                    cleaned_text = cleaned_text.replace(spaces, '  ', 1)
                                    logger.info(f"    清理公司名后占位符（保留2个）: {len(spaces)} -> 2个空格")
                                else:
                                    # 后面没有内容，删除多余空格
                                    cleaned_text = cleaned_text.replace(spaces, '', 1)
                                    logger.info(f"    清理公司名后占位符（删除）: {len(spaces)} -> 0个空格")
                        
                        if cleaned_text != run_text:
                            run.text = cleaned_text
                            logger.info(f"    run #{run_idx} 清理完成: '{cleaned_text}'")
            
            logger.info(f"公司名称后占位符清理完成: '{paragraph.text}'")
            
        except Exception as e:
            logger.error(f"清理公司名称后占位符失败: {e}")


def test_mcp_bidder_processor():
    """测试MCP投标人名称处理器"""
    # 这里可以添加测试代码
    pass


if __name__ == "__main__":
    test_mcp_bidder_processor()