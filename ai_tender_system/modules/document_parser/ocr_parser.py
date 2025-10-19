#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR解析器 - 使用PaddleOCR识别图片和扫描PDF中的文字
"""

import os
import fitz  # PyMuPDF
import asyncio
from pathlib import Path
from typing import List, Tuple, Dict, Optional
from PIL import Image
import io

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from common.logger import get_module_logger

logger = get_module_logger("document_parser.ocr")


class OCRParser:
    """OCR解析器 - 用于识别扫描PDF和图片中的文字"""

    def __init__(
        self,
        use_gpu: bool = False,
        lang: str = "ch",
        enable_ocr: bool = True
    ):
        """
        初始化OCR解析器

        Args:
            use_gpu: 是否使用GPU加速
            lang: 识别语言 ('ch'=中文, 'en'=英文)
            enable_ocr: 是否启用OCR
        """
        self.logger = logger
        self.enable_ocr = enable_ocr
        self.use_gpu = use_gpu
        self.lang = lang
        self._ocr_engine = None

        if self.enable_ocr:
            self._initialize_ocr()

    def _initialize_ocr(self):
        """初始化PaddleOCR引擎（延迟加载）"""
        try:
            from paddleocr import PaddleOCR

            self.logger.info(f"初始化PaddleOCR引擎 (GPU={self.use_gpu}, 语言={self.lang})")

            self._ocr_engine = PaddleOCR(
                use_angle_cls=True,  # 使用方向分类器
                lang=self.lang,      # 语言
                use_gpu=self.use_gpu  # GPU加速
            )

            self.logger.info("PaddleOCR引擎初始化完成")

        except ImportError:
            self.logger.error("PaddleOCR未安装，请运行: pip install paddleocr")
            self.enable_ocr = False
        except Exception as e:
            self.logger.error(f"PaddleOCR初始化失败: {e}")
            self.enable_ocr = False

    async def ocr_pdf_page(self, pdf_path: str, page_num: int) -> str:
        """
        对PDF的单个页面进行OCR识别

        Args:
            pdf_path: PDF文件路径
            page_num: 页码（从0开始）

        Returns:
            str: 识别出的文本
        """
        if not self.enable_ocr or not self._ocr_engine:
            return ""

        try:
            # 将PDF页面转换为图片
            doc = fitz.open(pdf_path)
            page = doc[page_num]

            # 渲染页面为图片 (放大2倍提高识别精度)
            mat = fitz.Matrix(2.0, 2.0)
            pix = page.get_pixmap(matrix=mat)

            # 转换为PIL Image
            img_data = pix.tobytes("png")
            image = Image.open(io.BytesIO(img_data))

            doc.close()

            # 在线程池中运行OCR（避免阻塞）
            loop = asyncio.get_event_loop()
            text = await loop.run_in_executor(None, self._ocr_image, image)

            return text

        except Exception as e:
            self.logger.error(f"OCR识别PDF第{page_num + 1}页失败: {e}")
            return ""

    def _ocr_image(self, image: Image.Image) -> str:
        """
        对PIL Image进行OCR识别

        Args:
            image: PIL Image对象

        Returns:
            str: 识别出的文本
        """
        try:
            # 转换为numpy数组
            import numpy as np
            img_array = np.array(image)

            # 进行OCR识别
            result = self._ocr_engine.ocr(img_array, cls=True)

            # 提取文本
            text_lines = []
            if result and result[0]:
                for line in result[0]:
                    if line and len(line) >= 2:
                        # line格式: [[[x1,y1],[x2,y2],[x3,y3],[x4,y4]], (text, confidence)]
                        text = line[1][0]
                        confidence = line[1][1]

                        # 只保留置信度高于0.5的结果
                        if confidence > 0.5:
                            text_lines.append(text)

            return '\n'.join(text_lines)

        except Exception as e:
            self.logger.error(f"OCR图片识别失败: {e}")
            return ""

    async def ocr_pdf(self, pdf_path: str, page_numbers: Optional[List[int]] = None) -> Dict[int, str]:
        """
        对PDF的多个页面进行OCR识别

        Args:
            pdf_path: PDF文件路径
            page_numbers: 要识别的页码列表（从0开始），None表示全部页面

        Returns:
            Dict[int, str]: {页码: 识别文本}
        """
        if not self.enable_ocr or not self._ocr_engine:
            self.logger.warning("OCR未启用")
            return {}

        try:
            # 获取总页数
            doc = fitz.open(pdf_path)
            total_pages = len(doc)
            doc.close()

            # 确定要识别的页面
            if page_numbers is None:
                page_numbers = list(range(total_pages))

            self.logger.info(f"开始OCR识别 {len(page_numbers)} 个页面")

            # 并发识别多个页面
            tasks = []
            for page_num in page_numbers:
                if 0 <= page_num < total_pages:
                    task = self.ocr_pdf_page(pdf_path, page_num)
                    tasks.append((page_num, task))

            # 等待所有任务完成
            results = {}
            for page_num, task in tasks:
                text = await task
                results[page_num] = text
                self.logger.debug(f"页面 {page_num + 1} OCR完成，提取 {len(text)} 字符")

            total_chars = sum(len(text) for text in results.values())
            self.logger.info(f"OCR识别完成，共提取 {total_chars} 字符")

            return results

        except Exception as e:
            self.logger.error(f"批量OCR识别失败: {e}")
            return {}

    async def detect_scanned_pages(self, pdf_path: str, min_chars_per_page: int = 50) -> List[int]:
        """
        检测PDF中哪些页面是扫描页（文字稀少）

        Args:
            pdf_path: PDF文件路径
            min_chars_per_page: 每页最少字符数阈值

        Returns:
            List[int]: 扫描页的页码列表（从0开始）
        """
        scanned_pages = []

        try:
            doc = fitz.open(pdf_path)

            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()

                # 如果文字数量少于阈值，判定为扫描页
                if len(text.strip()) < min_chars_per_page:
                    scanned_pages.append(page_num)
                    self.logger.debug(f"检测到扫描页: 第{page_num + 1}页 (仅{len(text)}字符)")

            doc.close()

            if scanned_pages:
                self.logger.info(f"检测到 {len(scanned_pages)} 个扫描页面: {[p+1 for p in scanned_pages]}")

        except Exception as e:
            self.logger.error(f"检测扫描页失败: {e}")

        return scanned_pages
