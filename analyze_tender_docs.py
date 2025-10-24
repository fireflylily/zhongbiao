#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
招标文档结构分析脚本
分析多个招标文档的结构模式，找出通用的解析方案
"""

import os
import sys
from pathlib import Path
from docx import Document
from docx.oxml.text.paragraph import CT_P
from docx.oxml.table import CT_Tbl
from docx.table import Table, _Cell
import re

def analyze_document(doc_path):
    """分析单个文档的结构"""
    try:
        doc = Document(doc_path)
    except Exception as e:
        return {
            'error': str(e),
            'path': doc_path
        }

    result = {
        'name': os.path.basename(doc_path),
        'path': doc_path,
        'total_paragraphs': 0,
        'has_toc': False,
        'toc_range': None,
        'main_sections': [],
        'structure_pattern': None,
        'key_sections': {},
        'challenges': [],
        'heading_styles': {},
        'document_composition': None
    }

    paragraphs = []

    # 直接遍历所有段落
    for para_index, para in enumerate(doc.paragraphs):
        paragraphs.append({
            'index': para_index,
            'text': para.text.strip(),
            'style': para.style.name if para.style else 'Normal',
            'is_heading': para.style.name.startswith('Heading') if para.style else False,
            'level': int(para.style.name[-1]) if para.style and para.style.name.startswith('Heading') and para.style.name[-1].isdigit() else 0
        })

    result['total_paragraphs'] = len(paragraphs)

    # 检测目录
    toc_start = None
    toc_end = None
    for i, para in enumerate(paragraphs):
        text = para['text']
        if re.search(r'(目\s*录|Contents|TABLE OF CONTENTS)', text, re.IGNORECASE):
            toc_start = i
        # 检测目录结束（通常是第一个非空白、非目录项的段落）
        if toc_start is not None and toc_end is None:
            if i > toc_start + 1:
                # 如果连续3个段落不像目录项，认为目录结束
                if not re.search(r'(第.*[部分章节]|[一二三四五六七八九十]、|\d+\.|附件|\s+\d+)', text):
                    if i - toc_start > 10:  # 至少有10行才算有效目录
                        toc_end = i

    if toc_start is not None and toc_end is not None:
        result['has_toc'] = True
        result['toc_range'] = (toc_start, toc_end)

    # 分析章节编号模式
    patterns = {
        '第X部分': [],
        '一、': [],
        '1.': [],
        '1.1': [],
        '混合': []
    }

    for i, para in enumerate(paragraphs):
        text = para['text']
        if not text:
            continue

        # 跳过目录范围
        if result['has_toc'] and toc_start <= i < toc_end:
            continue

        # 检测各种编号模式
        if re.match(r'^第[一二三四五六七八九十\d]+[部分章节]', text):
            patterns['第X部分'].append({'index': i, 'text': text})
        elif re.match(r'^[一二三四五六七八九十]+、', text):
            patterns['一、'].append({'index': i, 'text': text})
        elif re.match(r'^\d+\.\s+[^\d]', text):
            patterns['1.'].append({'index': i, 'text': text})
        elif re.match(r'^\d+\.\d+', text):
            patterns['1.1'].append({'index': i, 'text': text})

        # 检测"文档构成"
        if re.search(r'(文件构成|招标文件构成|文档构成|采购文件构成)', text):
            result['document_composition'] = {'index': i, 'text': text}

    # 确定主要结构模式
    max_pattern = max(patterns.items(), key=lambda x: len(x[1]))
    if len(max_pattern[1]) > 0:
        result['structure_pattern'] = max_pattern[0]
        result['main_sections'] = max_pattern[1][:10]  # 只保存前10个

    # 统计Heading样式
    for para in paragraphs:
        if para['is_heading']:
            style = para['style']
            if style not in result['heading_styles']:
                result['heading_styles'][style] = 0
            result['heading_styles'][style] += 1

    # 查找关键章节
    key_section_patterns = {
        '投标须知': r'(投标[人供应商]*须知|供应商须知|投标人须知|响应人须知)',
        '技术需求': r'(技术[需求规格参数标准]|技术要求|服务要求|项目要求|采购需求)',
        '商务要求': r'(商务[要求条款]|合同条款|价格条款)',
        '评分标准': r'(评[分审]标准|评[分审]办法|综合评[分审]|评价方法)'
    }

    for key, pattern in key_section_patterns.items():
        for i, para in enumerate(paragraphs):
            if re.search(pattern, para['text'], re.IGNORECASE):
                if key not in result['key_sections']:
                    result['key_sections'][key] = []
                result['key_sections'][key].append({'index': i, 'text': para['text'][:50]})

    # 识别解析挑战
    if not result['has_toc']:
        result['challenges'].append('无目录，需要通过章节编号识别结构')

    if result['document_composition']:
        result['challenges'].append(f"存在文档构成章节(段落{result['document_composition']['index']})，可能干扰章节提取")

    if len(result['heading_styles']) == 0:
        result['challenges'].append('无Heading样式，需要依赖文本模式识别章节')

    if result['has_toc']:
        # 检查目录后是否有大量非内容段落
        if toc_end and toc_end < len(paragraphs):
            non_content_count = 0
            for i in range(toc_end, min(toc_end + 50, len(paragraphs))):
                text = paragraphs[i]['text']
                if len(text) < 50 and not re.search(r'第.*[部分章节]|[一二三四五六七八九十]、|\d+\.', text):
                    non_content_count += 1
            if non_content_count > 20:
                result['challenges'].append(f'目录后有大量非内容段落(约{non_content_count}个)')

    return result

def format_report(results):
    """格式化分析报告"""
    report = []

    for i, result in enumerate(results, 1):
        if 'error' in result:
            name = result.get('name', os.path.basename(result.get('path', '未知文档')))
            report.append(f"\n## 文档{i}: {name}")
            report.append(f"**错误**: {result['error']}\n")
            continue

        report.append(f"\n## 文档{i}: {result['name']}")
        report.append(f"\n### 基本信息")
        report.append(f"- 总段落数: {result['total_paragraphs']}")
        report.append(f"- 是否有TOC: {'是' if result['has_toc'] else '否'}")
        if result['toc_range']:
            report.append(f"- TOC位置: 段落 {result['toc_range'][0]}-{result['toc_range'][1]}")

        report.append(f"\n### 结构特征")
        report.append(f"- 主章节编号格式: {result['structure_pattern'] or '未识别'}")
        report.append(f"- 第一层章节数: {len(result['main_sections'])}个")
        if result['document_composition']:
            report.append(f"- 是否有\"文档构成\"章节: 是 (位置: 段落{result['document_composition']['index']})")
        else:
            report.append(f"- 是否有\"文档构成\"章节: 否")

        if result['heading_styles']:
            report.append(f"- Heading样式统计: {dict(result['heading_styles'])}")
        else:
            report.append(f"- Heading样式统计: 无")

        report.append(f"\n### 关键章节位置")
        for key, sections in result['key_sections'].items():
            if sections:
                first = sections[0]
                report.append(f"- {key}: 段落 {first['index']} ({first['text']})")

        if not result['key_sections']:
            report.append("- 未识别到关键章节")

        report.append(f"\n### 解析挑战")
        if result['challenges']:
            for challenge in result['challenges']:
                report.append(f"- {challenge}")
        else:
            report.append("- 无明显挑战")

        report.append(f"\n### 示例章节标题（前5个主章节）")
        for j, section in enumerate(result['main_sections'][:5], 1):
            report.append(f"{j}. {section['text']}")

        if not result['main_sections']:
            report.append("（未识别到主章节）")

    # 总结共性和差异
    report.append(f"\n\n# 总结：共性特征与差异点\n")

    # 统计有目录的文档
    has_toc_count = sum(1 for r in results if not 'error' in r and r['has_toc'])
    report.append(f"## 共性特征\n")
    report.append(f"1. **目录情况**: {has_toc_count}/{len([r for r in results if 'error' not in r])} 个文档有目录")

    # 统计编号模式
    pattern_stats = {}
    for r in results:
        if 'error' not in r and r['structure_pattern']:
            pattern = r['structure_pattern']
            pattern_stats[pattern] = pattern_stats.get(pattern, 0) + 1

    report.append(f"2. **编号模式分布**:")
    for pattern, count in sorted(pattern_stats.items(), key=lambda x: -x[1]):
        report.append(f"   - {pattern}: {count}个文档")

    # 统计文档构成
    has_composition = sum(1 for r in results if not 'error' in r and r['document_composition'])
    report.append(f"3. **文档构成章节**: {has_composition}/{len([r for r in results if 'error' not in r])} 个文档包含此章节")

    report.append(f"\n## 差异点\n")
    report.append(f"1. **章节编号**: 存在\"第X部分\"、\"一、\"、\"1.\"等多种格式，需要灵活识别")
    report.append(f"2. **目录格式**: 有/无目录，目录格式不统一")
    report.append(f"3. **Heading样式**: 部分文档使用Heading样式，部分完全不使用")

    report.append(f"\n## 通用解析策略\n")
    report.append(f"""
1. **多模式章节识别**
   - 优先检测Heading样式（如果存在）
   - 使用正则表达式识别多种编号格式：
     * `第[X]部分/章节`
     * `一、二、三...`
     * `1. 2. 3...`
     * `1.1 1.2 2.1...`
   - 结合缩进和字体大小辅助判断

2. **目录处理**
   - 先检测是否有目录（关键词："目录"）
   - 如果有目录：
     * 提取目录范围（通过连续性判断）
     * 解析目录项获取章节结构
     * 跳过目录范围，避免重复提取
   - 如果无目录：
     * 直接从正文识别章节

3. **文档构成过滤**
   - 检测"文件构成/招标文件构成"等元数据章节
   - 将其标记为元数据，不作为正文章节
   - 在章节提取时跳过此类内容

4. **关键章节定位**
   - 使用关键词模式匹配：
     * 投标须知：`投标.*须知|供应商须知`
     * 技术需求：`技术.*[需求|规格|要求]|采购需求`
     * 商务要求：`商务.*要求|合同条款`
     * 评分标准：`评.*标准|评.*办法`
   - 记录首次出现位置和所属章节

5. **鲁棒性设计**
   - 多种识别方法并行，投票决定
   - 对无Heading样式的文档，依赖文本模式
   - 处理目录后的封面、说明等干扰段落
   - 建立章节编号的优先级（第X部分 > 一、 > 1.）

6. **结构验证**
   - 检查识别的章节是否合理（数量、层级）
   - 验证关键章节是否都已识别
   - 对异常情况（如只识别到1-2个章节）给出警告
""")

    return '\n'.join(report)

def main():
    # 文档路径
    base_path = Path("/Users/lvhe/Library/Mobile Documents/com~apple~CloudDocs/Work/智慧足迹2025/05投标项目/AI标书/项目/7-标书读取/")

    doc_files = [
        "采购文件-2025-IT-0032所属运营商数据.doc",
        "招标文件-哈银消金.docx",
        "正式版（2025-066期）2025年信息公司上市公司股东会网络投票一键通项目磋商文件.docx",
        "单一谈判文件-中国联通手机信息核验类外部数据服务采购项目-9-22(1).docx",
        "数字人民币运营管理中心有限公司2025年二次放号查询服务采购项目采购需求文件-无目录.docx",
        "中邮保险手机号实名认证服务采购项目竞争性磋商采购文件.docx",
        "采购谈判邀请函（采购项目：中国联通运营商个人数据服务）.doc",
        "中国建设银行股份有限公司运营商失联修复外呼服务采购项目谈判文件(1).docx"
    ]

    results = []
    for doc_file in doc_files:
        doc_path = base_path / doc_file
        print(f"正在分析: {doc_file}...")
        result = analyze_document(str(doc_path))
        results.append(result)

    # 生成报告
    report = format_report(results)

    # 保存报告
    output_path = Path("/Users/lvhe/Downloads/zhongbiao/zhongbiao/tender_structure_analysis_report.md")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\n分析完成！报告已保存至: {output_path}")
    print(report)

if __name__ == "__main__":
    main()
