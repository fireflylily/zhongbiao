#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
可视化内容生成器

负责生成表格和流程图，增强技术方案的可视化表达
"""

import re
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from ...common.logger import get_module_logger
from ...common import get_prompt_manager, create_llm_client

logger = get_module_logger("visual_generator")


@dataclass
class TableData:
    """表格数据"""
    markdown: str  # Markdown 格式的表格
    caption: str   # 表格标题
    table_type: str  # 表格类型: comparison/features/timeline


@dataclass
class FlowchartData:
    """流程图数据"""
    mermaid_code: str  # Mermaid 语法代码
    caption: str       # 图片标题
    flowchart_type: str  # 流程图类型: workflow/architecture


class VisualGenerator:
    """
    可视化内容生成器

    根据章节内容智能分析并生成:
    - 表格: 对比表、功能表、时间表
    - 流程图: 工作流程图、架构图 (Mermaid 语法)
    """

    # 表格类型定义
    TABLE_TYPES = {
        'comparison': '对比表 - 用于功能对比、方案比较',
        'features': '功能表 - 用于功能清单、需求列表',
        'timeline': '时间表 - 用于项目计划、实施阶段'
    }

    # 流程图类型定义
    FLOWCHART_TYPES = {
        'workflow': '工作流程 - 业务流程、操作步骤',
        'architecture': '架构图 - 系统架构、组件关系'
    }

    # 关键词映射: 用于判断章节是否需要表格或流程图
    TABLE_KEYWORDS = {
        'comparison': ['对比', '比较', 'vs', '与', '相比', '优势', '劣势', '方案一', '方案二'],
        'features': ['功能', '特性', '特点', '能力', '支持', '清单', '列表', '需求'],
        'timeline': ['计划', '阶段', '时间', '周期', '里程碑', '进度', '排期', '实施']
    }

    FLOWCHART_KEYWORDS = {
        'workflow': ['流程', '步骤', '操作', '执行', '处理', '工作流', '业务流程', '过程'],
        'architecture': ['架构', '结构', '组成', '模块', '组件', '系统', '层次', '拓扑']
    }

    # content_style 配置到数量的映射
    QUANTITY_MAP = {
        '无': 0,
        '少量': 2,  # 1-2个
        '适量': 4,  # 3-5个
        '大量': 8   # 6+个
    }

    def __init__(self, model_name: str = "deepseek-v3"):
        """
        初始化可视化生成器

        Args:
            model_name: LLM 模型名称
        """
        self.model_name = model_name
        self.prompt_manager = get_prompt_manager()
        self.llm_client = create_llm_client(model_name)
        self.logger = logger

    def analyze_content_for_visuals(
        self,
        title: str,
        content: str,
        content_style: Dict
    ) -> Dict[str, List[Dict]]:
        """
        分析内容，确定需要生成的可视化元素

        Args:
            title: 章节标题
            content: 章节内容
            content_style: 内容风格配置
                - tables: '无'/'少量'/'适量'/'大量'
                - flowcharts: '无'/'少量'/'适量'

        Returns:
            {
                'tables': [{'type': 'comparison', 'topic': '...'}],
                'flowcharts': [{'type': 'workflow', 'topic': '...'}]
            }
        """
        result = {'tables': [], 'flowcharts': []}

        # 获取配置的表格和流程图数量
        table_config = content_style.get('tables', '适量')
        flowchart_config = content_style.get('flowcharts', '适量')

        max_tables = self.QUANTITY_MAP.get(table_config, 4)
        max_flowcharts = self.QUANTITY_MAP.get(flowchart_config, 4)

        if max_tables == 0 and max_flowcharts == 0:
            return result

        # 组合标题和内容进行分析
        text = f"{title}\n{content}"

        # 分析需要的表格类型
        if max_tables > 0:
            for table_type, keywords in self.TABLE_KEYWORDS.items():
                if any(kw in text for kw in keywords):
                    # 提取具体主题
                    topic = self._extract_topic(text, keywords)
                    result['tables'].append({
                        'type': table_type,
                        'topic': topic or title
                    })
                    if len(result['tables']) >= max_tables:
                        break

        # 分析需要的流程图类型
        if max_flowcharts > 0:
            for flowchart_type, keywords in self.FLOWCHART_KEYWORDS.items():
                if any(kw in text for kw in keywords):
                    topic = self._extract_topic(text, keywords)
                    result['flowcharts'].append({
                        'type': flowchart_type,
                        'topic': topic or title
                    })
                    if len(result['flowcharts']) >= max_flowcharts:
                        break

        self.logger.info(
            f"可视化分析: 章节'{title[:20]}...' -> "
            f"表格{len(result['tables'])}个, 流程图{len(result['flowcharts'])}个"
        )

        return result

    def _extract_topic(self, text: str, keywords: List[str]) -> Optional[str]:
        """从文本中提取与关键词相关的主题"""
        for keyword in keywords:
            if keyword in text:
                # 找到关键词附近的句子作为主题
                pattern = f"[^。！？\n]*{keyword}[^。！？\n]*"
                match = re.search(pattern, text)
                if match:
                    topic = match.group(0).strip()
                    if len(topic) > 50:
                        topic = topic[:50] + "..."
                    return topic
        return None

    def generate_table(
        self,
        table_type: str,
        content: str,
        topic: str
    ) -> Optional[TableData]:
        """
        使用 LLM 生成 Markdown 表格

        Args:
            table_type: 表格类型 (comparison/features/timeline)
            content: 章节内容
            topic: 表格主题

        Returns:
            TableData 或 None
        """
        try:
            prompt = self._get_table_prompt(table_type, content, topic)
            response = self.llm_client.call(
                prompt=prompt,
                purpose=f"生成{table_type}类型表格"
            )

            # 解析响应
            result = self._parse_json_response(response)
            if not result:
                return None

            markdown = result.get('table', '')
            caption = result.get('caption', topic)

            if not markdown or '|' not in markdown:
                self.logger.warning(f"表格生成失败: 无有效的 Markdown 表格")
                return None

            return TableData(
                markdown=markdown,
                caption=caption,
                table_type=table_type
            )

        except Exception as e:
            self.logger.error(f"生成表格失败: {e}")
            return None

    def generate_flowchart(
        self,
        flowchart_type: str,
        content: str,
        topic: str
    ) -> Optional[FlowchartData]:
        """
        使用 LLM 生成 Mermaid 流程图代码

        Args:
            flowchart_type: 流程图类型 (workflow/architecture)
            content: 章节内容
            topic: 流程图主题

        Returns:
            FlowchartData 或 None
        """
        try:
            prompt = self._get_flowchart_prompt(flowchart_type, content, topic)
            response = self.llm_client.call(
                prompt=prompt,
                purpose=f"生成{flowchart_type}类型流程图"
            )

            # 解析响应
            result = self._parse_json_response(response)
            if not result:
                return None

            mermaid_code = result.get('mermaid_code', '')
            caption = result.get('caption', topic)

            if not mermaid_code:
                self.logger.warning(f"流程图生成失败: 无 Mermaid 代码")
                return None

            # 清洗 Mermaid 代码
            mermaid_code = self._sanitize_mermaid_code(mermaid_code)

            return FlowchartData(
                mermaid_code=mermaid_code,
                caption=caption,
                flowchart_type=flowchart_type
            )

        except Exception as e:
            self.logger.error(f"生成流程图失败: {e}")
            return None

    def _get_table_prompt(self, table_type: str, content: str, topic: str) -> str:
        """获取表格生成提示词"""
        type_descriptions = {
            'comparison': "创建一个对比表，展示不同方案/产品的特点对比",
            'features': "创建一个功能清单表，列出系统/产品的功能特性",
            'timeline': "创建一个时间表/计划表，展示项目阶段和里程碑"
        }

        prompt = f"""你是一个专业的技术文档编写专家。请根据以下内容生成一个 {type_descriptions.get(table_type, '数据')} 表格。

## 主题
{topic}

## 参考内容
{content[:2000]}

## 要求
1. 表格使用标准 Markdown 格式
2. 表头清晰明确
3. 内容专业、具体
4. 行数控制在 3-8 行
5. 列数控制在 3-5 列
6. 表格标题简洁明了

请严格按照以下 JSON 格式返回:
```json
{{
    "table": "| 列1 | 列2 | 列3 |\\n|---|---|---|\\n| 数据1 | 数据2 | 数据3 |",
    "caption": "表格标题"
}}
```

注意: table 字段中的换行使用 \\n 表示。"""

        return prompt

    def _get_flowchart_prompt(self, flowchart_type: str, content: str, topic: str) -> str:
        """获取流程图生成提示词"""
        type_descriptions = {
            'workflow': "创建一个工作流程图，展示业务流程或操作步骤",
            'architecture': "创建一个架构图，展示系统组件和它们之间的关系"
        }

        diagram_type = "flowchart TD" if flowchart_type == 'workflow' else "flowchart LR"

        prompt = f"""你是一个专业的技术文档编写专家。请根据以下内容生成一个 {type_descriptions.get(flowchart_type, '流程')} 图的 Mermaid 代码。

## 主题
{topic}

## 参考内容
{content[:2000]}

## Mermaid 语法示例
```mermaid
{diagram_type}
    A[开始] --> B{{判断条件}}
    B -->|是| C[处理步骤1]
    B -->|否| D[处理步骤2]
    C --> E[结束]
    D --> E
```

## 要求
1. 使用 Mermaid flowchart 语法
2. 节点数量控制在 5-10 个
3. 节点标签使用中文，简洁明了
4. 使用合适的形状:
   - [] 普通节点
   - {{}} 判断节点
   - () 圆角节点
   - (()) 圆形节点
5. 确保语法正确，可直接渲染

请严格按照以下 JSON 格式返回:
```json
{{
    "mermaid_code": "{diagram_type}\\n    A[开始] --> B[步骤1]\\n    B --> C[结束]",
    "caption": "流程图标题"
}}
```

注意: mermaid_code 字段中的换行使用 \\n 表示。"""

        return prompt

    def _sanitize_mermaid_code(self, code: str) -> str:
        """
        清洗 Mermaid 代码，确保语法正确

        处理:
        1. 移除 Markdown 代码块标记
        2. 确保有正确的起始关键字
        3. 修复常见语法问题
        """
        # 1. 移除 Markdown 代码块标记
        code = re.sub(r'^```mermaid\s*\n?', '', code.strip())
        code = re.sub(r'^```\s*\n?', '', code.strip())
        code = re.sub(r'\n?```$', '', code.strip())

        # 2. 确保有正确的起始关键字
        valid_starts = ['graph', 'flowchart', 'sequenceDiagram', 'classDiagram',
                        'stateDiagram', 'erDiagram', 'gantt', 'pie']
        if not any(code.strip().startswith(s) for s in valid_starts):
            # 默认添加 flowchart TD
            code = f"flowchart TD\n{code}"

        # 3. 修复常见语法问题
        # 中文引号转英文引号
        code = code.replace('"', '"').replace('"', '"')
        code = code.replace(''', "'").replace(''', "'")

        # 处理转义的换行符
        code = code.replace('\\n', '\n')

        return code

    def _parse_json_response(self, response: str) -> Optional[Dict[str, Any]]:
        """解析 LLM 返回的 JSON 响应"""
        try:
            # 移除可能的 markdown 代码块标记
            cleaned = response.strip()
            if cleaned.startswith('```json'):
                cleaned = cleaned[7:]
            if cleaned.startswith('```'):
                cleaned = cleaned[3:]
            if cleaned.endswith('```'):
                cleaned = cleaned[:-3]

            cleaned = cleaned.strip()

            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON 解析失败: {e}\n响应内容: {response[:200]}...")
            return None

    def generate_chapter_visuals(
        self,
        title: str,
        content: str,
        content_style: Dict
    ) -> Dict[str, List]:
        """
        为章节生成所有可视化元素

        这是主入口方法，由 ContentWriterAgent 调用

        Args:
            title: 章节标题
            content: 章节内容
            content_style: 内容风格配置

        Returns:
            {
                'tables': [TableData, ...],
                'flowcharts': [FlowchartData, ...]
            }
        """
        result = {'tables': [], 'flowcharts': []}

        # 分析需要什么可视化元素
        analysis = self.analyze_content_for_visuals(title, content, content_style)

        # 生成表格
        for table_spec in analysis.get('tables', []):
            table = self.generate_table(
                table_spec['type'],
                content,
                table_spec['topic']
            )
            if table:
                result['tables'].append({
                    'markdown': table.markdown,
                    'caption': table.caption,
                    'type': table.table_type
                })

        # 生成流程图
        for flowchart_spec in analysis.get('flowcharts', []):
            flowchart = self.generate_flowchart(
                flowchart_spec['type'],
                content,
                flowchart_spec['topic']
            )
            if flowchart:
                result['flowcharts'].append({
                    'mermaid_code': flowchart.mermaid_code,
                    'caption': flowchart.caption,
                    'type': flowchart.flowchart_type
                })

        self.logger.info(
            f"章节 '{title[:20]}...' 生成可视化: "
            f"表格 {len(result['tables'])} 个, 流程图 {len(result['flowcharts'])} 个"
        )

        return result
