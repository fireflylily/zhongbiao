#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gemini AI解析器 - 使用Google Gemini多模态模型解析文档结构

优势:
- 直接理解PDF/Word文档,无需格式转换
- 支持结构化JSON输出
- 理解语义,不只是识别样式
- 支持多语言和复杂布局
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Optional

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from common import get_module_logger
from . import BaseStructureParser, ParserMetrics


class GeminiParser(BaseStructureParser):
    """Gemini AI文档结构解析器"""

    def __init__(self):
        super().__init__()
        self.logger = get_module_logger("parsers.gemini")
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

        # 价格配置(元/百万token)
        self.pricing = {
            "gemini-2.0-flash": {"input": 0.015, "output": 0.06},      # 性价比最高
            "gemini-2.5-pro": {"input": 0.25, "output": 1.0},          # 功能最强
        }

    def parse_structure(self, doc_path: str) -> Dict:
        """使用Gemini解析文档结构"""
        start_time = time.time()

        try:
            self.logger.info(f"[Gemini解析器] 开始解析: {doc_path}")

            # 检查依赖
            if not self.is_available():
                raise ValueError(
                    "Gemini API未配置\n"
                    "请在.env文件添加: GEMINI_API_KEY=your_key\n"
                    "获取密钥: https://ai.google.dev/"
                )

            # 导入Gemini SDK
            import google.generativeai as genai

            # 配置API
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(self.model_name)

            # 上传文档
            self.logger.info(f"[Gemini] 上传文档到Gemini...")
            uploaded_file = genai.upload_file(doc_path)
            self.logger.info(f"[Gemini] 文档已上传,URI: {uploaded_file.uri}")

            # 构造Prompt
            prompt = self._build_prompt()

            # 调用Gemini
            self.logger.info(f"[Gemini] 调用模型: {self.model_name}")
            response = model.generate_content(
                [uploaded_file, prompt],
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json",  # 强制JSON输出
                    temperature=0.1  # 降低随机性,提高一致性
                )
            )

            # 解析响应
            gemini_result = json.loads(response.text)
            self.logger.debug(f"[Gemini] 原始响应: {json.dumps(gemini_result, ensure_ascii=False, indent=2)}")

            # 转换为系统格式
            chapters = self._convert_gemini_to_chapters(gemini_result)

            # 计算统计信息
            statistics = self._calculate_statistics(chapters)

            # 计算成本
            token_count = response.usage_metadata.total_token_count if hasattr(response, 'usage_metadata') else 1000
            api_cost = self._calculate_cost(token_count)

            # 计算性能指标
            parse_time = time.time() - start_time
            metrics = ParserMetrics(
                parser_name="gemini",
                parse_time=parse_time,
                chapters_found=len(chapters),
                success=True,
                confidence_score=95.0,  # Gemini通常有很高的置信度
                api_cost=api_cost
            )

            self.logger.info(
                f"[Gemini解析器] 完成: 找到{len(chapters)}个章节, "
                f"耗时{parse_time:.2f}秒, 成本≈{api_cost:.4f}元"
            )

            return {
                "success": True,
                "chapters": [ch.to_dict() if hasattr(ch, 'to_dict') else ch for ch in chapters],
                "statistics": statistics,
                "metrics": metrics,
                "gemini_metadata": {
                    "model": self.model_name,
                    "token_count": token_count,
                    "file_uri": uploaded_file.uri
                }
            }

        except Exception as e:
            parse_time = time.time() - start_time
            error_msg = str(e)
            self.logger.error(f"[Gemini解析器] 失败: {error_msg}")

            return {
                "success": False,
                "chapters": [],
                "statistics": {},
                "error": error_msg,
                "metrics": ParserMetrics(
                    parser_name="gemini",
                    parse_time=parse_time,
                    chapters_found=0,
                    success=False,
                    error_message=error_msg
                )
            }

    def _build_prompt(self) -> str:
        """构造Gemini Prompt"""
        return """
你是一个专业的招标文档分析专家。请仔细分析这份招标文档,提取其完整的章节结构。

任务要求:
1. 识别所有一级、二级、三级标题(章、节、条)
2. 判断每个章节是否属于"重要章节"(投标须知、技术要求、商务要求、评分标准等)
3. 标记应该跳过的章节(合同条款、附件清单、目录、封面等)
4. 记录每个章节的起始页码(如果可识别)

重要章节关键词(应标记auto_selected=true):
- 投标须知、供应商须知、响应人须知
- 技术要求、技术需求、需求书、技术规格、性能指标
- 商务要求、商务条款、付款方式、交付要求
- 评分标准、评标办法、评分细则、打分标准

应跳过的章节关键词(应标记skip_recommended=true):
- 合同条款、合同文本、合同范本、合同格式
- 目录、索引、附件清单、附表
- 封面、声明、授权书、承诺书

返回JSON格式:
{
  "chapters": [
    {
      "level": 1,
      "title": "第一章 投标须知",
      "auto_selected": true,
      "skip_recommended": false,
      "page_start": 5,
      "children": [
        {
          "level": 2,
          "title": "1.1 项目概况",
          "auto_selected": false,
          "skip_recommended": false,
          "page_start": 5,
          "children": []
        }
      ]
    }
  ]
}

注意事项:
1. 保持完整的层级结构(parent-children关系)
2. level: 1=一级标题, 2=二级标题, 3=三级标题
3. 如果无法确定页码,page_start设为0
4. children是数组,即使为空也要包含[]
5. 只返回JSON,不要有任何其他解释文字
"""

    def _convert_gemini_to_chapters(self, gemini_result: Dict) -> List:
        """将Gemini返回的JSON转换为ChapterNode对象"""
        from ..structure_parser import ChapterNode

        def convert_chapter(ch_data: Dict, parent_id: str = "", idx: int = 0) -> ChapterNode:
            """递归转换章节"""
            # 生成章节ID
            if parent_id:
                chapter_id = f"{parent_id}_{idx}"
            else:
                chapter_id = f"ch_{idx}"

            # 创建ChapterNode
            chapter = ChapterNode(
                id=chapter_id,
                level=ch_data.get('level', 1),
                title=ch_data.get('title', '未命名章节'),
                para_start_idx=ch_data.get('page_start', 0),  # 使用页码作为索引
                para_end_idx=None,  # Gemini无法提供
                word_count=0,  # 需要后续计算
                preview_text="",  # 需要后续提取
                auto_selected=ch_data.get('auto_selected', False),
                skip_recommended=ch_data.get('skip_recommended', False),
                children=[]
            )

            # 递归处理子章节
            children_data = ch_data.get('children', [])
            for child_idx, child_data in enumerate(children_data):
                child = convert_chapter(child_data, chapter_id, child_idx)
                chapter.children.append(child)

            return chapter

        # 转换所有顶层章节
        chapters = []
        for idx, ch_data in enumerate(gemini_result.get('chapters', [])):
            chapter = convert_chapter(ch_data, "", idx)
            chapters.append(chapter)

        return chapters

    def _calculate_statistics(self, chapters: List) -> Dict:
        """计算章节统计信息"""
        def count_chapters(chs):
            total = len(chs)
            auto_selected = sum(1 for ch in chs if ch.auto_selected)
            skip_recommended = sum(1 for ch in chs if ch.skip_recommended)

            # 递归统计子章节
            for ch in chs:
                if ch.children:
                    child_stats = count_chapters(ch.children)
                    total += child_stats['total_chapters']
                    auto_selected += child_stats['auto_selected']
                    skip_recommended += child_stats['skip_recommended']

            return {
                'total_chapters': total,
                'auto_selected': auto_selected,
                'skip_recommended': skip_recommended
            }

        stats = count_chapters(chapters)
        stats['total_words'] = 0  # Gemini无法直接提供

        return stats

    def _calculate_cost(self, token_count: int) -> float:
        """计算API调用成本

        Args:
            token_count: 总token数

        Returns:
            成本(元)
        """
        model_pricing = self.pricing.get(
            self.model_name,
            self.pricing["gemini-2.0-flash"]  # 默认使用Flash定价
        )

        # 假设输入输出各占一半
        input_tokens = token_count * 0.7
        output_tokens = token_count * 0.3

        cost = (
            (input_tokens / 1_000_000) * model_pricing["input"] +
            (output_tokens / 1_000_000) * model_pricing["output"]
        )

        return round(cost, 4)

    def is_available(self) -> bool:
        """检查Gemini API是否可用"""
        if not self.api_key:
            return False

        try:
            import google.generativeai
            return True
        except ImportError:
            self.logger.warning("[Gemini] google-generativeai未安装,运行: pip install google-generativeai")
            return False

    def get_parser_info(self) -> Dict:
        """获取解析器信息"""
        return {
            "name": "gemini",
            "display_name": "Gemini AI",
            "description": (
                "基于Google Gemini多模态大模型的智能文档解析\n"
                f"• 模型: {self.model_name}\n"
                "• 优势: 理解语义、支持复杂布局、多语言、结构化输出\n"
                "• 劣势: 需要API密钥、有一定成本\n"
                "• 适用: 格式不规范、复杂布局的文档"
            ),
            "requires_api": True,
            "cost_per_page": 0.01,  # 估算
            "available": self.is_available(),
            "model": self.model_name,
            "capabilities": [
                "直接理解PDF/Word",
                "语义理解",
                "结构化输出",
                "多语言支持",
                "复杂布局识别"
            ]
        }


# 注册解析器
from . import ParserFactory
ParserFactory.register_parser('gemini', GeminiParser)
