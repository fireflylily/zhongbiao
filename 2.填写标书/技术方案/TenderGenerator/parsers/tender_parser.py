"""
招标文件解析器
解析招标文件中的需求说明和评分标准
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple
try:
    from ..utils.file_utils import get_file_utils
    from ..config import (
        REQUIREMENT_KEYWORDS, SCORING_KEYWORDS, WEIGHT_KEYWORDS,
        MIN_PARAGRAPH_LENGTH
    )
except ImportError:
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent))
    from utils.file_utils import get_file_utils
    from config import (
        REQUIREMENT_KEYWORDS, SCORING_KEYWORDS, WEIGHT_KEYWORDS,
        MIN_PARAGRAPH_LENGTH
    )

class TenderParser:
    """招标文件解析器类"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.file_utils = get_file_utils()
    
    def parse_tender_document(self, file_path: str) -> Dict[str, Any]:
        """
        解析招标文件
        
        Args:
            file_path: 招标文件路径
            
        Returns:
            解析结果字典，包含需求和评分标准
        """
        self.logger.info(f"开始解析招标文件: {file_path}")
        
        # 读取文件
        file_data = self.file_utils.read_file(file_path)
        if 'error' in file_data:
            return {'error': file_data['error']}
        
        # 提取文本内容
        text_content = self.file_utils.extract_text_content(file_data)
        if not text_content:
            return {'error': '无法提取文档文本内容'}
        
        # 分割为章节
        sections = self.file_utils.split_into_sections(text_content)
        
        # 识别需求章节和评分章节
        requirements = self._extract_requirements(sections, text_content)
        scoring_criteria = self._extract_scoring_criteria(sections, text_content)
        
        # 解析评分标准详细信息
        scoring_details = self._parse_scoring_details(scoring_criteria)
        
        result = {
            'file_path': file_path,
            'file_type': file_data.get('type', 'unknown'),
            'total_sections': len(sections),
            'requirements': requirements,
            'scoring_criteria': scoring_criteria,
            'scoring_details': scoring_details,
            'sections': sections
        }
        
        self.logger.info(f"招标文件解析完成，发现 {len(requirements)} 个需求项，{len(scoring_details)} 个评分项")
        return result
    
    def _extract_requirements(self, sections: List[Dict[str, Any]], full_text: str) -> List[Dict[str, Any]]:
        """
        提取需求内容
        
        Args:
            sections: 章节列表
            full_text: 完整文本
            
        Returns:
            需求列表
        """
        requirements = []
        
        # 方法1：基于关键词查找需求章节
        requirement_sections = []
        for section in sections:
            title_lower = section['title'].lower()
            content_lower = section['content'].lower()
            
            # 检查标题是否包含需求关键词
            title_match = any(keyword in title_lower for keyword in REQUIREMENT_KEYWORDS)
            # 检查内容是否大量包含需求关键词
            content_match_count = sum(1 for keyword in REQUIREMENT_KEYWORDS if keyword in content_lower)
            
            if title_match or content_match_count >= 2:
                requirement_sections.append(section)
        
        # 方法2：如果没找到明确的需求章节，在全文中搜索
        if not requirement_sections:
            requirement_sections = self._find_requirement_paragraphs(full_text)
        
        # 处理需求内容
        for i, section in enumerate(requirement_sections):
            # 将章节内容分解为具体需求项
            requirement_items = self._parse_requirement_items(section['content'])
            
            for j, item in enumerate(requirement_items):
                requirements.append({
                    'id': f"REQ_{i+1}_{j+1}",
                    'title': item.get('title', f"需求项 {i+1}.{j+1}"),
                    'content': item.get('content', ''),
                    'category': item.get('category', '功能需求'),
                    'priority': item.get('priority', 'normal'),
                    'source_section': section['title']
                })
        
        return requirements
    
    def _extract_scoring_criteria(self, sections: List[Dict[str, Any]], full_text: str) -> List[Dict[str, Any]]:
        """
        提取评分标准
        
        Args:
            sections: 章节列表
            full_text: 完整文本
            
        Returns:
            评分标准列表
        """
        scoring_sections = []
        
        # 查找评分标准章节
        for section in sections:
            title_lower = section['title'].lower()
            content_lower = section['content'].lower()
            
            # 检查是否为评分相关章节
            title_match = any(keyword in title_lower for keyword in SCORING_KEYWORDS)
            content_match = any(keyword in content_lower for keyword in SCORING_KEYWORDS)
            weight_match = any(keyword in content_lower for keyword in WEIGHT_KEYWORDS)
            
            if title_match or (content_match and weight_match):
                scoring_sections.append(section)
        
        # 如果没找到评分章节，搜索包含分数的段落
        if not scoring_sections:
            scoring_sections = self._find_scoring_paragraphs(full_text)
        
        return scoring_sections
    
    def _parse_scoring_details(self, scoring_sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        解析评分标准详细信息
        
        Args:
            scoring_sections: 评分章节列表
            
        Returns:
            评分详细信息列表
        """
        scoring_details = []
        
        for section in scoring_sections:
            content = section.get('content', '')
            if isinstance(section, dict) and 'content' not in section:
                # 如果section是从_find_scoring_paragraphs返回的简单格式
                content = section.get('text', str(section))
            
            # 解析评分项目
            items = self._extract_scoring_items(content)
            
            for item in items:
                scoring_details.append({
                    'id': f"SCORE_{len(scoring_details)+1}",
                    'title': item['title'],
                    'description': item['description'],
                    'weight': item['weight'],
                    'max_score': item['max_score'],
                    'criteria': item.get('criteria', []),
                    'source_section': section.get('title', '评分标准')
                })
        
        return scoring_details
    
    def _extract_scoring_items(self, text: str) -> List[Dict[str, Any]]:
        """
        从文本中提取评分项目
        
        Args:
            text: 评分标准文本
            
        Returns:
            评分项目列表
        """
        items = []
        
        # 首先尝试解析表格形式的评分数据
        table_items = self._extract_scoring_from_tables(text)
        if table_items:
            items.extend(table_items)
        
        # 正则模式匹配评分项目
        patterns = [
            # 模式1：项目名(XX分)
            r'([^(（\\n]+)[（(](\d+)分[）)]',
            # 模式2：项目名：XX分
            r'([^：:\\n]+)[:：]\s*(\d+)分',
            # 模式3：序号+项目名+分数
            r'(\d+[、.]?\s*[^\\n]+?)\s+(\d+)分',
            # 模式4：表格形式：项目 | 分数
            r'([^|\\n]+)\s*\|\s*(\d+)',
            # 模式5：分值在单独列中
            r'([^\\t\\n]+)\\t+(\d+)\\s*$',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.MULTILINE)
            for match in matches:
                title = match.group(1).strip()
                try:
                    score = int(match.group(2))
                except ValueError:
                    continue
                
                # 跳过过短的标题
                if len(title) < 3:
                    continue
                
                # 避免重复添加相同项目
                if any(item['title'] == title for item in items):
                    continue
                
                # 查找该项目的详细描述
                description = self._find_item_description(text, title, match.start())
                
                items.append({
                    'title': title,
                    'description': description,
                    'weight': f"{score}分",
                    'max_score': score,
                    'criteria': self._extract_criteria_from_description(description)
                })
        
        # 如果没有找到明确的评分项目，尝试其他方法
        if not items:
            items = self._extract_scoring_items_fallback(text)
        
        return items
    
    def _extract_scoring_from_tables(self, text: str) -> List[Dict[str, Any]]:
        """
        从表格形式的文本中提取评分项目
        
        Args:
            text: 包含表格的文本
            
        Returns:
            评分项目列表
        """
        items = []
        
        # 查找表格标记
        table_pattern = r'\[表格 \d+\]\n(.*?)(?=\[表格|\Z)'
        table_matches = re.findall(table_pattern, text, re.DOTALL)
        
        for table_text in table_matches:
            lines = table_text.strip().split('\n')
            
            # 查找表头，确定列的位置
            header_found = False
            eval_content_col = -1  # 评审内容列
            eval_factor_col = -1   # 评分因素列
            score_col = -1         # 分值列
            criteria_col = -1      # 评分标准列
            
            for i, line in enumerate(lines):
                if not line.strip():
                    continue
                
                cols = [col.strip() for col in line.split('\t') if col.strip()]
                if len(cols) < 2:
                    continue
                
                # 检查是否为表头行
                if any(keyword in line for keyword in ['评审内容', '评分因素', '分值', '评分标准']):
                    header_found = True
                    for j, col in enumerate(cols):
                        if '评审内容' in col:
                            eval_content_col = j
                        elif '评分因素' in col:
                            eval_factor_col = j
                        elif '分值' in col:
                            score_col = j
                        elif '评分标准' in col:
                            criteria_col = j
                    continue
                
                # 如果已找到表头，处理数据行
                if header_found and len(cols) >= 2:
                    try:
                        # 提取评分项目标题 - 优先从评分因素列获取
                        title = ""
                        if eval_factor_col >= 0 and eval_factor_col < len(cols):
                            potential_title = cols[eval_factor_col].strip()
                            # 只有当该列内容不是数字且不为空时才作为标题
                            if potential_title and not potential_title.isdigit() and len(potential_title) > 1:
                                title = potential_title
                        
                        # 如果评分因素列没有有效标题，检查评审内容列
                        if not title and eval_content_col >= 0 and eval_content_col < len(cols):
                            content = cols[eval_content_col].strip()
                            if content and not content.endswith('分）') and '部分' not in content and not content.isdigit():
                                title = content
                        
                        # 如果标题仍为空，按顺序尝试其他列（跳过纯数字列）
                        if not title:
                            for j, col in enumerate(cols):
                                col = col.strip()
                                if (col and not col.isdigit() and 
                                    len(col) > 2 and 
                                    not re.match(r'^\d+$', col) and
                                    '分）' not in col and
                                    '部分' not in col and
                                    j != score_col):  # 不使用分值列作为标题
                                    title = col
                                    break
                        
                        # 提取分值
                        score = 0
                        if score_col >= 0 and score_col < len(cols):
                            score_text = cols[score_col]
                            score_match = re.search(r'(\d+)', score_text)
                            if score_match:
                                score = int(score_match.group(1))
                        else:
                            # 如果没有专门的分值列，在所有列中查找数字
                            for col in cols:
                                col_match = re.search(r'(\d+)', col)
                                if col_match:
                                    score = int(col_match.group(1))
                                    break
                        
                        # 提取评分标准
                        criteria_text = ""
                        if criteria_col >= 0 and criteria_col < len(cols):
                            criteria_text = cols[criteria_col]
                        elif len(cols) > 3:
                            # 如果没有明确的标准列，使用最后一列
                            criteria_text = cols[-1]
                        
                        if title and score > 0:
                            # 跳过表头和大分类行
                            skip_keywords = ['评审内容', '评分因素', '分值', '评分标准', '部分（满分', '部分(满分']
                            if any(keyword in title for keyword in skip_keywords):
                                continue
                                
                            items.append({
                                'title': title,
                                'description': criteria_text,
                                'weight': f"{score}分",
                                'max_score': score,
                                'criteria': [criteria_text] if criteria_text else []
                            })
                            
                    except (ValueError, IndexError) as e:
                        self.logger.debug(f"解析表格行失败: {line}, 错误: {e}")
                        continue
                
                # 如果没有找到表头，尝试通用方法解析
                elif not header_found:
                    # 查找包含分数的列
                    for j, col in enumerate(cols):
                        if re.search(r'\d+', col):
                            score_match = re.search(r'(\d+)', col)
                            if score_match:
                                score = int(score_match.group(1))
                                # 假设第一列是标题
                                if len(cols) > 1:
                                    title = cols[0].strip()
                                    description = cols[-1].strip() if len(cols) > 2 else ""
                                    
                                    if title and score > 0:
                                        items.append({
                                            'title': title,
                                            'description': description,
                                            'weight': f"{score}分",
                                            'max_score': score,
                                            'criteria': [description] if description else []
                                        })
                                break
        
        return items
    
    def _find_item_description(self, text: str, title: str, title_pos: int) -> str:
        """
        查找评分项目的详细描述
        
        Args:
            text: 完整文本
            title: 项目标题
            title_pos: 标题在文本中的位置
            
        Returns:
            项目描述
        """
        # 查找标题后的文本，直到下一个评分项目
        text_after_title = text[title_pos:]
        lines = text_after_title.split('\\n')
        
        description_lines = []
        for i, line in enumerate(lines[1:], 1):  # 跳过标题行
            line = line.strip()
            
            # 如果遇到新的评分项目，停止
            if any(pattern in line for pattern in ['分)', '分：', '分|']) and re.search(r'\\d+分', line):
                break
            
            # 如果遇到明显的章节标题，停止
            if re.match(r'^[一二三四五六七八九十]+[、.]', line) or re.match(r'^\\d+[、.]', line):
                break
            
            if line and len(line) > MIN_PARAGRAPH_LENGTH:
                description_lines.append(line)
            
            # 限制描述长度
            if len(description_lines) > 10:
                break
        
        return '\\n'.join(description_lines)
    
    def _extract_criteria_from_description(self, description: str) -> List[str]:
        """
        从描述中提取评分标准
        
        Args:
            description: 项目描述
            
        Returns:
            评分标准列表
        """
        criteria = []
        
        # 查找包含评分标准的句子
        sentences = re.split(r'[。；;]', description)
        for sentence in sentences:
            sentence = sentence.strip()
            if any(keyword in sentence for keyword in ['要求', '应当', '必须', '需要', '支持', '具备']):
                if len(sentence) > MIN_PARAGRAPH_LENGTH:
                    criteria.append(sentence)
        
        return criteria
    
    def _extract_scoring_items_fallback(self, text: str) -> List[Dict[str, Any]]:
        """
        备用方法：提取评分项目
        
        Args:
            text: 评分文本
            
        Returns:
            评分项目列表
        """
        items = []
        
        # 查找所有包含分数的行
        lines = text.split('\\n')
        for line in lines:
            if '分' in line and re.search(r'\\d+', line):
                # 提取分数
                score_matches = re.findall(r'(\\d+)分', line)
                if score_matches:
                    score = int(score_matches[0])
                    title = re.sub(r'\\(.*?\\)|（.*?）', '', line).strip()
                    title = re.sub(r'\\d+分.*', '', title).strip()
                    
                    if len(title) > 3:
                        items.append({
                            'title': title,
                            'description': '',
                            'weight': f"{score}分",
                            'max_score': score,
                            'criteria': []
                        })
        
        return items
    
    def _find_requirement_paragraphs(self, text: str) -> List[Dict[str, Any]]:
        """
        在全文中查找需求段落
        
        Args:
            text: 完整文本
            
        Returns:
            需求章节列表
        """
        sections = []
        paragraphs = text.split('\\n\\n')
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if len(paragraph) < MIN_PARAGRAPH_LENGTH:
                continue
            
            # 检查段落是否包含需求关键词
            keyword_count = sum(1 for keyword in REQUIREMENT_KEYWORDS if keyword in paragraph.lower())
            
            if keyword_count >= 2:
                sections.append({
                    'title': '需求说明',
                    'content': paragraph,
                    'level': 1
                })
        
        return sections
    
    def _find_scoring_paragraphs(self, text: str) -> List[Dict[str, Any]]:
        """
        在全文中查找评分段落
        
        Args:
            text: 完整文本
            
        Returns:
            评分章节列表
        """
        sections = []
        paragraphs = text.split('\\n\\n')
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if len(paragraph) < MIN_PARAGRAPH_LENGTH:
                continue
            
            # 检查段落是否包含评分相关内容
            has_scoring_keywords = any(keyword in paragraph.lower() for keyword in SCORING_KEYWORDS)
            has_weight_keywords = any(keyword in paragraph for keyword in WEIGHT_KEYWORDS)
            has_scores = re.search(r'\\d+分', paragraph)
            
            if (has_scoring_keywords and has_weight_keywords) or has_scores:
                sections.append({
                    'title': '评分标准',
                    'content': paragraph,
                    'level': 1
                })
        
        return sections
    
    def _parse_requirement_items(self, content: str) -> List[Dict[str, Any]]:
        """
        解析需求项目
        
        Args:
            content: 需求内容
            
        Returns:
            需求项目列表
        """
        items = []
        
        # 按段落分割
        paragraphs = [p.strip() for p in content.split('\\n') if p.strip()]
        
        for paragraph in paragraphs:
            if len(paragraph) < MIN_PARAGRAPH_LENGTH:
                continue
            
            # 尝试提取项目标题
            title = self._extract_requirement_title(paragraph)
            
            # 判断需求类型
            category = self._classify_requirement(paragraph)
            
            # 判断优先级
            priority = self._determine_priority(paragraph)
            
            items.append({
                'title': title,
                'content': paragraph,
                'category': category,
                'priority': priority
            })
        
        return items
    
    def _extract_requirement_title(self, text: str) -> str:
        """提取需求标题"""
        # 尝试找到第一个句子作为标题
        sentences = re.split(r'[。；;]', text)
        if sentences:
            title = sentences[0].strip()
            # 限制标题长度
            if len(title) > 50:
                title = title[:47] + "..."
            return title
        return text[:30] + "..." if len(text) > 30 else text
    
    def _classify_requirement(self, text: str) -> str:
        """分类需求"""
        text_lower = text.lower()
        
        if any(keyword in text_lower for keyword in ['性能', '响应时间', '并发', '吞吐量']):
            return '性能需求'
        elif any(keyword in text_lower for keyword in ['安全', '权限', '加密', '认证']):
            return '安全需求'
        elif any(keyword in text_lower for keyword in ['界面', 'ui', '用户体验', '操作']):
            return '界面需求'
        elif any(keyword in text_lower for keyword in ['数据', '存储', '备份', '恢复']):
            return '数据需求'
        else:
            return '功能需求'
    
    def _determine_priority(self, text: str) -> str:
        """判断需求优先级"""
        text_lower = text.lower()
        
        if any(keyword in text_lower for keyword in ['必须', '必需', '强制', '关键']):
            return 'high'
        elif any(keyword in text_lower for keyword in ['建议', '推荐', '可选']):
            return 'low'
        else:
            return 'normal'


# 全局解析器实例
_tender_parser = None

def get_tender_parser() -> TenderParser:
    """获取全局招标文件解析器实例"""
    global _tender_parser
    if _tender_parser is None:
        _tender_parser = TenderParser()
    return _tender_parser