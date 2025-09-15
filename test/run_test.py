#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于Run级别的精确Word文档填充工具
采用逐个Run处理策略，保持原有格式不被破坏
1.清理日志，重复日志太多。
2.年 月  日格式没有处理
3.（职务，职称）没有处理
4.（请填写供应商名称）没有处理。
（已处理）1. 报错，统一替换失败
2. 上传文件夹和下载文件夹有两处。
（已处理）3.  re.sub()、new_text是否可以清理？
4. 是把整个文档做为一个文件处理的吗？建议分段处理。因为文档很长。
5. 是每个字段都调用一下精确处理方法吗？可以统一架构的调用吗？
（已处理）6. 电子邮箱也被处理了两次。
（已处理）6. 从日志上来看，日期被处理了多次。

"""

from docx import Document
import re
import os

class PreciseWordFiller:
    def __init__(self):
        self.debug = True
    
    def log(self, message):
        """调试输出"""
        if self.debug:
            print(message)
    
    def build_paragraph_text_map(self, paragraph):
        """
        构建段落的文本到Run映射
        返回：文本内容、Run列表、每个字符对应的Run索引
        """
        full_text = ""
        runs = []
        char_to_run_map = []
        
        for run_idx, run in enumerate(paragraph.runs):
            run_text = run.text
            runs.append(run)
            
            # 记录每个字符属于哪个run
            for _ in range(len(run_text)):
                char_to_run_map.append(run_idx)
            
            full_text += run_text
        
        return full_text, runs, char_to_run_map
    
    def find_cross_run_matches(self, full_text, pattern):
        """
        在完整文本中查找匹配，可能跨越多个Run
        """
        matches = []
        for match in re.finditer(pattern, full_text):
            matches.append({
                'start': match.start(),
                'end': match.end(),
                'text': match.group(),
                'pattern': pattern
            })
        return matches
    
    def apply_replacement_to_runs(self, runs, char_to_run_map, match, replacement_text):
        """
        将替换应用到涉及的Run中，保持格式
        """
        start_pos = match['start']
        end_pos = match['end']
        
        # 找出涉及的Run范围
        if start_pos >= len(char_to_run_map) or end_pos > len(char_to_run_map):
            self.log(f"警告：匹配位置超出范围，跳过 {match['text']}")
            return False
        
        start_run_idx = char_to_run_map[start_pos]
        end_run_idx = char_to_run_map[end_pos - 1] if end_pos > 0 else start_run_idx
        
        self.log(f"  匹配范围：Run {start_run_idx} 到 Run {end_run_idx}")
        
        # 计算在每个Run中的相对位置
        run_modifications = {}
        
        # 构建每个Run的字符偏移映射
        run_char_offsets = {}
        current_offset = 0
        for i, run in enumerate(runs):
            run_char_offsets[i] = current_offset
            current_offset += len(run.text)
        
        # 计算需要修改的Run及其新内容
        for run_idx in range(start_run_idx, end_run_idx + 1):
            if run_idx >= len(runs):
                continue
                
            run = runs[run_idx]
            run_start_in_full = run_char_offsets[run_idx]
            run_end_in_full = run_start_in_full + len(run.text)
            
            # 计算这个Run中需要替换的部分
            replace_start_in_run = max(0, start_pos - run_start_in_full)
            replace_end_in_run = min(len(run.text), end_pos - run_start_in_full)
            
            old_run_text = run.text
            
            if run_idx == start_run_idx and run_idx == end_run_idx:
                # 替换完全在一个Run内
                new_run_text = (old_run_text[:replace_start_in_run] + 
                              replacement_text + 
                              old_run_text[replace_end_in_run:])
            elif run_idx == start_run_idx:
                # 开始Run：保留前缀，加上替换文本
                new_run_text = old_run_text[:replace_start_in_run] + replacement_text
            elif run_idx == end_run_idx:
                # 结束Run：只保留后缀
                new_run_text = old_run_text[replace_end_in_run:]
            else:
                # 中间Run：完全清空
                new_run_text = ""
            
            run_modifications[run_idx] = new_run_text
            self.log(f"    Run {run_idx}: '{old_run_text}' -> '{new_run_text}'")
        
        # 应用修改
        for run_idx, new_text in run_modifications.items():
            runs[run_idx].text = new_text
        
        return True
    
    def process_paragraph(self, paragraph, replacements):
        """
        处理单个段落的字段替换
        """
        if not paragraph.text.strip():
            return 0

        self.log(f"\n--- 处理段落 ---")
        self.log(f"原文: {paragraph.text}")

        # 优先检测和处理组合模式
        combination_result = self.detect_combination_patterns(paragraph, replacements)
        if combination_result > 0:
            self.log(f"组合规则处理完成，替换了 {combination_result} 个组合模式")

        # 构建文本映射
        full_text, runs, char_to_run_map = self.build_paragraph_text_map(paragraph)
        
        if len(runs) == 0:
            return 0
        
        self.log(f"Run结构: {len(runs)} 个runs，总长度 {len(full_text)} 字符")
        for i, run in enumerate(runs):
            self.log(f"  Run {i}: '{run.text}' (长度: {len(run.text)})")
        
        replacement_count = 0
        
        # 按优先级处理不同的替换模式
        all_matches = []
        
        for field_name, replacement_value in replacements.items():
            if not replacement_value:
                continue
            
            # 定义各种匹配模式
            patterns = [
                # 方括号格式（优先级最高）
                (rf'\[\（{re.escape(field_name)}\）\]', replacement_value, "方括号中文"),
                (rf'\[\({re.escape(field_name)}\)\]', replacement_value, "方括号英文"),
                (rf'\[\（{re.escape(field_name)}.*?\）\]', replacement_value, "方括号中文变体"),
                (rf'\[\({re.escape(field_name)}.*?\)\]', replacement_value, "方括号英文变体"),
                
                # 下划线格式
                (rf'{re.escape(field_name)}\s*[：:]\s*_{3,}', f'{field_name}：{replacement_value}', "下划线"),
                
                # 括号格式
                (rf'\（{re.escape(field_name)}\）', f'（{replacement_value}）', "括号中文"),
                (rf'\({re.escape(field_name)}\)', f'（{replacement_value}）', "括号英文"),
                
                # 空格格式
                (rf'{re.escape(field_name)}\s*[：:]\s*\s+$', f'{field_name}：{replacement_value}', "尾部空格"),
            ]
            
            # 收集所有匹配
            for pattern, replacement, pattern_type in patterns:
                matches = self.find_cross_run_matches(full_text, pattern)
                # 只在找到匹配时输出日志
                if matches:
                    self.log(f"    模式 '{pattern_type}': 找到 {len(matches)} 个匹配")
                for match in matches:
                    match['replacement'] = replacement
                    match['field_name'] = field_name
                    match['pattern_type'] = pattern_type
                    all_matches.append(match)
                    self.log(f"      匹配: '{match['text']}' at {match['start']}-{match['end']}")
        
        # 按位置排序（从后往前处理，避免位置偏移问题）
        all_matches.sort(key=lambda x: x['start'], reverse=True)
        
        # 执行替换
        for match in all_matches:
            self.log(f"  ✅ 替换: {match['field_name']} → {match['replacement']}")
            
            if self.apply_replacement_to_runs(runs, char_to_run_map, match, match['replacement']):
                replacement_count += 1
                # 重新构建映射，因为文本已经改变
                full_text, runs, char_to_run_map = self.build_paragraph_text_map(paragraph)
            else:
                self.log(f"  替换失败: {match['text']}")
        
        if replacement_count > 0:
            self.log(f"  最终结果: {paragraph.text}")
        
        return replacement_count

    def detect_combination_patterns(self, paragraph, replacements):
        """
        检测和处理各种组合模式
        """
        text = paragraph.text
        total_replacements = 0

        self.log(f"检测组合模式: '{text[:80]}{'...' if len(text) > 80 else ''}'")

        # 检测（职务、职称）组合
        if re.search(r'[（(]\s*职[务位]\s*[、，]\s*职[称位]\s*[）)]', text):
            self.log(f"发现职务职称组合模式")
            result = self.handle_position_combination(paragraph, replacements)
            if result:
                total_replacements += 1
                self.log(f"✅ 职务职称组合替换成功")

        # 检测（供应商名称、地址）组合
        if re.search(r'[（(]\s*供应商名称\s*[、，]\s*地址\s*[）)]', text):
            self.log(f"发现供应商名称地址组合模式")
            result = self.handle_company_address_combination(paragraph, replacements)
            if result:
                total_replacements += 1
                self.log(f"✅ 供应商名称地址组合替换成功")

        # 检测（项目名称、项目编号）组合
        if re.search(r'[（(]\s*项目名称\s*[、，]\s*项目编号\s*[）)]', text):
            self.log(f"发现项目名称编号组合模式")
            result = self.handle_project_combination(paragraph, replacements)
            if result:
                total_replacements += 1
                self.log(f"✅ 项目名称编号组合替换成功")

        return total_replacements

    def handle_position_combination(self, paragraph, replacements):
        """
        处理（职务、职称）组合 - 从简单字典获取数据
        """
        # 尝试获取职务数据
        position = replacements.get('职务', replacements.get('职位', ''))
        if position:
            pattern = r'[（(]\s*职[务位]\s*[、，]\s*职[称位]\s*[）)]'
            replacement = f"（{position}、{position}）"
            return self.apply_pattern_replacement(paragraph, pattern, replacement)
        else:
            self.log(f"⚠️ 未找到职务/职位数据，跳过处理")
            return False

    def handle_company_address_combination(self, paragraph, replacements):
        """
        处理（供应商名称、地址）组合
        """
        company_name = replacements.get('供应商名称', '')
        address = replacements.get('地址', '')

        if company_name and address:
            pattern = r'[（(]\s*供应商名称\s*[、，]\s*地址\s*[）)]'
            replacement = f"（{company_name}、{address}）"
            return self.apply_pattern_replacement(paragraph, pattern, replacement)
        else:
            self.log(f"⚠️ 未找到供应商名称或地址数据，跳过处理")
            return False

    def handle_project_combination(self, paragraph, replacements):
        """
        处理（项目名称、项目编号）组合
        """
        project_name = replacements.get('项目名称', '')
        project_number = replacements.get('项目编号', '')

        if project_name and project_number:
            pattern = r'[（(]\s*项目名称\s*[、，]\s*项目编号\s*[）)]'
            replacement = f"（{project_name}、{project_number}）"
            return self.apply_pattern_replacement(paragraph, pattern, replacement)
        else:
            self.log(f"⚠️ 未找到项目名称或项目编号数据，跳过处理")
            return False

    def apply_pattern_replacement(self, paragraph, pattern, replacement):
        """
        应用模式替换 - 使用现有的精确格式处理引擎
        """
        # 构建文本映射
        full_text, runs, char_to_run_map = self.build_paragraph_text_map(paragraph)

        if not full_text:
            return False

        # 查找匹配
        matches = self.find_cross_run_matches(full_text, pattern)

        if not matches:
            return False

        self.log(f"  ✅ 找到 {len(matches)} 个匹配项")

        # 按位置排序（从后往前处理）
        matches.sort(key=lambda x: x['start'], reverse=True)

        # 执行替换
        for match in matches:
            self.log(f"  执行替换: '{match['text']}' -> '{replacement}'")

            if self.apply_replacement_to_runs(runs, char_to_run_map, match, replacement):
                # 重新构建映射，因为文本已经改变
                full_text, runs, char_to_run_map = self.build_paragraph_text_map(paragraph)
                return True
            else:
                self.log(f"  替换失败: {match['text']}")

        return False

    def fill_document(self, doc_path, replacements, output_path=None):
        """
        填充整个文档
        """
        self.log(f"开始处理文档: {doc_path}")
        self.log(f"替换配置: {replacements}")
        
        # 检查文件
        if not os.path.exists(doc_path):
            self.log(f"错误：文件不存在 - {doc_path}")
            return 0
        
        try:
            # 打开文档
            doc = Document(doc_path)
            total_replacements = 0
            
            # 处理所有段落
            for para_idx, paragraph in enumerate(doc.paragraphs):
                para_replacements = self.process_paragraph(paragraph, replacements)
                total_replacements += para_replacements
                
                if para_replacements > 0:
                    self.log(f"段落 {para_idx + 1}: 完成 {para_replacements} 个替换")
            
            # 保存文档
            output_file = output_path if output_path else doc_path
            doc.save(output_file)
            
            self.log(f"\n处理完成!")
            self.log(f"总替换数: {total_replacements}")
            self.log(f"输出文件: {output_file}")
            
            return total_replacements
            
        except Exception as e:
            self.log(f"处理出错: {str(e)}")
            import traceback
            traceback.print_exc()
            return 0

def main():
    """主函数"""
    print("=== 精确Word文档字段填充工具 ===\n")
    
    # 配置替换内容
    replacements = {
        '采购人': '北京市教育委员会',
        '供应商名称': '北京智慧足迹科技有限公司',
        '供应商全称': '北京智慧足迹科技有限公司',
        '供应商代表姓名': '李华',
        '项目名称': '智慧校园建设项目',
        '项目编号': 'BJJW-2024-001',
        '职务': '项目经理',
        '职称': '高级工程师',
        '地址': '北京市海淀区中关村大街1号',
        '邮编': '100080',
        '电话': '010-82345678',
        '电子邮箱': 'contact@smartsteps.com'
    }
    
    # 文件路径
    input_file = "/Users/lvhe/Library/Mobile Documents/com~apple~CloudDocs/Work/智慧足迹2025/05投标项目/AI标书/项目/4-分段测试文件/采购人-供应商全称、供应商代表姓名、项目名称编号、地址、邮编、电话、邮箱、供应商名称、公章、日期.docx"
    
    output_file = "/Users/lvhe/Library/Mobile Documents/com~apple~CloudDocs/Work/智慧足迹2025/05投标项目/AI标书/项目/4-分段测试文件/test-精确输出.docx"
    
    # 创建处理器并执行
    filler = PreciseWordFiller()
    result = filler.fill_document(input_file, replacements, output_file)
    
    if result > 0:
        print(f"\n成功完成 {result} 个字段替换")
    else:
        print(f"\n未找到可替换的字段")

if __name__ == "__main__":
    main()