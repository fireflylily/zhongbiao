#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TXT文档解析器
处理纯文本文档的解析和编码检测
"""

import asyncio
import chardet
from pathlib import Path
from typing import Dict, Tuple
from datetime import datetime

import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from common.logger import get_module_logger

logger = get_module_logger("document_parser.txt")


class TXTParser:
    """TXT文档解析器"""

    def __init__(self):
        self.logger = logger
        self.max_file_size = 50 * 1024 * 1024  # 50MB限制

    async def parse(self, file_path: str) -> Tuple[str, Dict]:
        """
        解析TXT文档

        Args:
            file_path: TXT文件路径

        Returns:
            Tuple[str, Dict]: (提取的文本内容, 元数据)
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"TXT文件不存在: {file_path}")

        # 检查文件大小
        file_size = file_path.stat().st_size
        if file_size > self.max_file_size:
            raise ValueError(f"文件过大: {file_size / (1024*1024):.1f}MB > {self.max_file_size / (1024*1024)}MB")

        self.logger.info(f"开始解析TXT文档: {file_path}")

        try:
            # 在线程池中运行解析
            loop = asyncio.get_event_loop()
            content, metadata = await loop.run_in_executor(None, self._parse_text_file, str(file_path))

            # 增强元数据
            metadata.update({
                'file_size_mb': round(file_size / (1024 * 1024), 2),
                'extraction_time': datetime.now().isoformat(),
                'parser_version': 'txt-parser-1.0'
            })

            self.logger.info(f"TXT解析完成: lines={metadata.get('line_count', 0)}")

            return content, metadata

        except Exception as e:
            self.logger.error(f"TXT解析失败: {file_path}, error={e}")
            raise

    def _parse_text_file(self, file_path: str) -> Tuple[str, Dict]:
        """解析文本文件的核心方法"""
        # 检测文件编码
        encoding = self._detect_encoding(file_path)

        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
        except UnicodeDecodeError:
            # 如果检测的编码失败，尝试其他常见编码
            for fallback_encoding in ['utf-8', 'gbk', 'gb2312', 'latin-1']:
                try:
                    with open(file_path, 'r', encoding=fallback_encoding) as f:
                        content = f.read()
                    encoding = fallback_encoding
                    self.logger.info(f"使用后备编码成功读取文件: {fallback_encoding}")
                    break
                except UnicodeDecodeError:
                    continue
            else:
                raise ValueError(f"无法使用任何编码读取文件: {file_path}")

        # 分析文本内容
        lines = content.split('\n')
        metadata = {
            'encoding': encoding,
            'line_count': len(lines),
            'char_count': len(content),
            'non_empty_lines': len([line for line in lines if line.strip()]),
            'avg_line_length': sum(len(line) for line in lines) / len(lines) if lines else 0,
            'max_line_length': max(len(line) for line in lines) if lines else 0
        }

        return content, metadata

    def _detect_encoding(self, file_path: str) -> str:
        """检测文件编码"""
        try:
            with open(file_path, 'rb') as f:
                # 读取文件的前几KB来检测编码
                raw_data = f.read(10240)  # 读取10KB

            detected = chardet.detect(raw_data)
            encoding = detected['encoding']
            confidence = detected['confidence']

            self.logger.info(f"检测到编码: {encoding} (置信度: {confidence:.2f})")

            # 如果置信度太低，使用默认编码
            if confidence < 0.7:
                encoding = 'utf-8'
                self.logger.warning(f"编码检测置信度过低，使用默认编码: {encoding}")

            return encoding or 'utf-8'

        except Exception as e:
            self.logger.warning(f"编码检测失败，使用UTF-8: {e}")
            return 'utf-8'