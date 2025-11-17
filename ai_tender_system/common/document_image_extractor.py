#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档图片提取器 - 从Word和PDF文档中提取图片
支持：
1. Word文档(.docx/.doc) - 提取文档中的所有图片
2. PDF文档 - 转换每一页为图片
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime

# 导入公共模块
import sys
sys.path.append(str(Path(__file__).parent.parent))
from common import get_module_logger, ensure_dir

logger = get_module_logger("document_image_extractor")


class DocumentImageExtractor:
    """文档图片提取器"""

    def __init__(self, output_dir: Optional[Path] = None):
        """
        初始化图片提取器

        Args:
            output_dir: 输出目录（默认为data/converted_images/）
        """
        self.logger = logger

        # 默认输出目录
        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            self.output_dir = Path(__file__).parent.parent / 'data' / 'converted_images'

        # 确保输出目录存在
        ensure_dir(self.output_dir)

        self.logger.info(f"文档图片提取器初始化完成，输出目录: {self.output_dir}")

    def extract_from_word(self, word_path: str, base_name: str = None) -> Tuple[List[Dict], Dict]:
        """
        从Word文档中提取所有图片

        Args:
            word_path: Word文档路径
            base_name: 基础文件名（用于生成输出文件名），如果不提供则使用原文件名

        Returns:
            (images_list, conversion_info) 元组：
            - images_list: 图片信息列表 [{"page_num": 1, "file_path": "/path/to/img_001.png", ...}, ...]
            - conversion_info: 转换元信息 {"total_images": 5, "output_dir": "/path", ...}
        """
        try:
            from docx import Document
            from PIL import Image
            import io

            word_path = Path(word_path)

            if not word_path.exists():
                raise FileNotFoundError(f"Word文档不存在: {word_path}")

            self.logger.info(f"开始从Word文档提取图片: {word_path}")

            # 打开Word文档
            doc = Document(word_path)

            # 准备输出目录
            if not base_name:
                base_name = word_path.stem

            # 创建子目录（使用时间戳避免冲突）
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_subdir = self.output_dir / f"{base_name}_{timestamp}"
            ensure_dir(output_subdir)

            # 提取图片
            images_list = []
            image_count = 0

            # 方法1：通过文档关系提取（推荐）
            for rel_id, rel in doc.part.rels.items():
                if "image" in rel.target_ref.lower():
                    try:
                        # 获取图片数据
                        image_part = rel.target_part
                        image_data = image_part.blob

                        # 确定图片格式
                        content_type = image_part.content_type
                        if 'png' in content_type:
                            ext = 'png'
                        elif 'jpeg' in content_type or 'jpg' in content_type:
                            ext = 'jpg'
                        elif 'gif' in content_type:
                            ext = 'gif'
                        elif 'bmp' in content_type:
                            ext = 'bmp'
                        else:
                            ext = 'png'  # 默认使用PNG

                        # 保存图片
                        image_count += 1
                        image_filename = f"image_{image_count:03d}.{ext}"
                        image_path = output_subdir / image_filename

                        with open(image_path, 'wb') as f:
                            f.write(image_data)

                        # 获取图片尺寸
                        try:
                            img = Image.open(io.BytesIO(image_data))
                            width, height = img.size
                        except:
                            width, height = 0, 0

                        images_list.append({
                            'page_num': image_count,  # Word没有页码概念，用序号代替
                            'file_path': str(image_path),
                            'width': width,
                            'height': height,
                            'format': ext.upper()
                        })

                        self.logger.debug(f"  提取图片 #{image_count}: {image_filename} ({width}x{height})")

                    except Exception as e:
                        self.logger.warning(f"  提取图片失败 (rel_id={rel_id}): {e}")

            # 转换元信息
            conversion_info = {
                'total_images': len(images_list),
                'output_dir': str(output_subdir),
                'source_file': str(word_path),
                'extraction_method': 'docx_relations',
                'timestamp': timestamp
            }

            self.logger.info(f"✅ Word图片提取完成: 提取了 {len(images_list)} 张图片")

            return images_list, conversion_info

        except ImportError as e:
            self.logger.error(f"缺少必要的库: {e}. 请安装: pip install python-docx Pillow")
            raise
        except Exception as e:
            self.logger.error(f"Word图片提取失败: {e}")
            raise

    def extract_from_pdf(self, pdf_path: str, base_name: str = None, dpi: int = 200) -> Tuple[List[Dict], Dict]:
        """
        从PDF文档转换每一页为图片

        Args:
            pdf_path: PDF文档路径
            base_name: 基础文件名（用于生成输出文件名），如果不提供则使用原文件名
            dpi: 图片DPI（默认200，值越大图片越清晰但文件越大）

        Returns:
            (images_list, conversion_info) 元组：
            - images_list: 图片信息列表 [{"page_num": 1, "file_path": "/path/to/page_001.png", ...}, ...]
            - conversion_info: 转换元信息 {"total_pages": 3, "output_dir": "/path", ...}
        """
        try:
            from pdf2image import convert_from_path
            from PIL import Image

            pdf_path = Path(pdf_path)

            if not pdf_path.exists():
                raise FileNotFoundError(f"PDF文档不存在: {pdf_path}")

            self.logger.info(f"开始转换PDF为图片: {pdf_path}, DPI={dpi}")

            # 准备输出目录
            if not base_name:
                base_name = pdf_path.stem

            # 创建子目录（使用时间戳避免冲突）
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_subdir = self.output_dir / f"{base_name}_{timestamp}"
            ensure_dir(output_subdir)

            # 转换PDF为图片列表
            images = convert_from_path(str(pdf_path), dpi=dpi)

            images_list = []

            for page_num, image in enumerate(images, start=1):
                # 保存图片
                image_filename = f"page_{page_num:03d}.png"
                image_path = output_subdir / image_filename
                image.save(image_path, 'PNG')

                images_list.append({
                    'page_num': page_num,
                    'file_path': str(image_path),
                    'width': image.width,
                    'height': image.height,
                    'format': 'PNG'
                })

                self.logger.debug(f"  转换页 {page_num}/{len(images)}: {image_filename} ({image.width}x{image.height})")

            # 转换元信息
            conversion_info = {
                'total_pages': len(images_list),
                'output_dir': str(output_subdir),
                'source_file': str(pdf_path),
                'dpi': dpi,
                'format': 'PNG',
                'timestamp': timestamp
            }

            self.logger.info(f"✅ PDF转换完成: {len(images_list)} 页转换为图片")

            return images_list, conversion_info

        except ImportError as e:
            self.logger.error(f"缺少必要的库: {e}. 请安装: pip install pdf2image Pillow poppler-utils")
            raise
        except Exception as e:
            self.logger.error(f"PDF转换失败: {e}")
            raise

    def extract_from_document(self, file_path: str, base_name: str = None,
                            dpi: int = 200) -> Tuple[List[Dict], Dict, str]:
        """
        自动识别文档类型并提取图片（统一入口）

        Args:
            file_path: 文档路径
            base_name: 基础文件名
            dpi: PDF转换DPI

        Returns:
            (images_list, conversion_info, original_file_type) 元组：
            - images_list: 图片信息列表
            - conversion_info: 转换元信息
            - original_file_type: 原始文件类型（PDF/DOCX/DOC/JPG/PNG等）
        """
        file_path = Path(file_path)
        file_ext = file_path.suffix.lower()

        # 记录原始文件类型
        original_file_type = file_ext[1:].upper() if file_ext else 'UNKNOWN'

        # 根据文件类型调用对应的提取方法
        if file_ext == '.pdf':
            images_list, conversion_info = self.extract_from_pdf(str(file_path), base_name, dpi)
        elif file_ext in ['.docx', '.doc']:
            images_list, conversion_info = self.extract_from_word(str(file_path), base_name)
        elif file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
            # 已经是图片，无需转换
            images_list = [{
                'page_num': 1,
                'file_path': str(file_path),
                'width': 0,
                'height': 0,
                'format': original_file_type
            }]
            conversion_info = {
                'total_images': 1,
                'source_file': str(file_path),
                'no_conversion_needed': True
            }
            self.logger.info(f"文件已是图片格式，无需转换: {file_path}")
        else:
            raise ValueError(f"不支持的文件类型: {file_ext}")

        return images_list, conversion_info, original_file_type


# 便捷函数
def extract_images_from_document(file_path: str, output_dir: Optional[Path] = None,
                                 base_name: str = None, dpi: int = 200) -> Dict:
    """
    从文档中提取图片的便捷函数

    Args:
        file_path: 文档路径
        output_dir: 输出目录
        base_name: 基础文件名
        dpi: PDF转换DPI

    Returns:
        结果字典:
        {
            'success': True,
            'images': [...],  # 图片列表
            'conversion_info': {...},  # 转换信息
            'original_file_type': 'PDF'  # 原始文件类型
        }
    """
    try:
        extractor = DocumentImageExtractor(output_dir)
        images_list, conversion_info, original_file_type = extractor.extract_from_document(
            file_path, base_name, dpi
        )

        return {
            'success': True,
            'images': images_list,
            'conversion_info': conversion_info,
            'original_file_type': original_file_type
        }

    except Exception as e:
        logger.error(f"文档图片提取失败: {e}")
        return {
            'success': False,
            'error': str(e),
            'images': [],
            'conversion_info': {},
            'original_file_type': 'UNKNOWN'
        }


__all__ = [
    'DocumentImageExtractor',
    'extract_images_from_document'
]
