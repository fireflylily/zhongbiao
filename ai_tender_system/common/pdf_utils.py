#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用PDF处理工具
支持多种场景下的PDF文件处理
- PDF检测
- PDF转图片
- PDF文本提取
"""

import os
import hashlib
import json
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass
from enum import Enum

# 导入日志模块
from . import get_module_logger

logger = get_module_logger("pdf_utils")


@dataclass
class PDFConversionConfig:
    """PDF转换配置"""
    output_format: str = 'JPEG'  # 输出格式: PNG, JPEG, JPG（优化：改用JPEG减小体积）
    dpi: int = 150  # 分辨率（优化：从200降到150，标书足够）
    max_width: int = 1200  # 最大宽度(像素)（优化：从1600降到1200）
    quality: int = 75  # JPEG质量(1-100)（优化：从95降到75，平衡质量和大小）
    page_prefix: str = 'page'  # 页面文件名前缀
    first_page_only: bool = False  # 是否只转换第一页


class ConversionMode(Enum):
    """转换模式"""
    IMAGE = "image"  # 转为图片
    TEXT = "text"    # 提取文本
    BOTH = "both"    # 同时转换


class PDFConverter:
    """通用PDF转换器"""

    def __init__(self, config: Optional[PDFConversionConfig] = None):
        """
        初始化PDF转换器

        Args:
            config: 转换配置，如果不提供则使用默认配置
        """
        self.config = config or PDFConversionConfig()
        self._cache = {}  # 缓存转换结果
        self.logger = get_module_logger("pdf_converter")

    def convert_to_images(self,
                         pdf_path: str,
                         output_dir: Optional[str] = None,
                         custom_prefix: Optional[str] = None,
                         page_list: Optional[List[int]] = None) -> Dict[str, Any]:
        """
        将PDF转换为图片

        Args:
            pdf_path: PDF文件路径
            output_dir: 输出目录，如果不提供则创建临时目录
            custom_prefix: 自定义文件名前缀
            page_list: 要转换的页码列表（从1开始），如 [1,2,5,6]
                      如果为None，则转换全部页面

        Returns:
            转换结果字典：
            {
                'success': bool,
                'original_pdf': str,  # 原始PDF路径
                'images': [            # 转换后的图片列表
                    {
                        'page_num': 1,
                        'file_path': '/path/to/image1.png',
                        'width': 1600,
                        'height': 2000
                    },
                    ...
                ],
                'total_pages': int,    # 转换的页数
                'source_total_pages': int,  # 原PDF总页数
                'is_partial': bool,    # 是否为部分转换
                'output_dir': str,     # 输出目录
                'error': str          # 错误信息(如果有)
            }
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(pdf_path):
                self.logger.error(f"PDF文件不存在: {pdf_path}")
                return {
                    'success': False,
                    'error': f'PDF文件不存在: {pdf_path}'
                }

            # 计算文件哈希，用于缓存
            file_hash = self._calculate_file_hash(pdf_path)

            # 检查缓存
            if file_hash in self._cache:
                self.logger.info(f"使用缓存的转换结果: {pdf_path}")
                return self._cache[file_hash]

            # 创建输出目录
            if not output_dir:
                pdf_dir = Path(pdf_path).parent
                pdf_name = Path(pdf_path).stem
                output_dir = pdf_dir / f'{pdf_name}_images'

            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)

            self.logger.info(f"开始转换PDF: {pdf_path}")
            self.logger.info(f"输出目录: {output_dir}")

            # 尝试方法1：使用pdf2image（需要poppler）
            images = None
            conversion_method = None

            try:
                from pdf2image import convert_from_path
                from PIL import Image

                self.logger.info("尝试使用pdf2image转换...")
                if self.config.first_page_only:
                    images = convert_from_path(
                        pdf_path,
                        dpi=self.config.dpi,
                        first_page=1,
                        last_page=1
                    )
                else:
                    images = convert_from_path(
                        pdf_path,
                        dpi=self.config.dpi
                    )
                conversion_method = 'pdf2image'
                self.logger.info(f"✅ pdf2image转换成功，共{len(images)}页")

            except Exception as pdf2image_error:
                self.logger.warning(f"pdf2image转换失败: {pdf2image_error}")

                # 尝试方法2：使用PyMuPDF（不需要poppler）
                try:
                    import fitz  # PyMuPDF
                    from PIL import Image

                    self.logger.info("尝试使用PyMuPDF转换...")
                    doc = fitz.open(pdf_path)
                    source_total_pages = len(doc)

                    # 转换为PIL Image对象列表
                    images = []

                    # 确定要转换的页面范围
                    if self.config.first_page_only:
                        page_range = [0]
                    elif page_list:
                        # 【新增】使用指定的页码列表（转换为0-based索引）
                        page_range = [p - 1 for p in page_list if 1 <= p <= source_total_pages]
                        self.logger.info(f"转换指定页码: {page_list} (共{len(page_range)}页)")
                    else:
                        # 转换全部页面
                        page_range = range(len(doc))

                    for page_index in page_range:
                        page = doc[page_index]
                        # 使用指定的DPI渲染
                        mat = fitz.Matrix(self.config.dpi / 72, self.config.dpi / 72)
                        pix = page.get_pixmap(matrix=mat)

                        # 转换为PIL Image
                        img_data = pix.tobytes("png")
                        from io import BytesIO
                        pil_image = Image.open(BytesIO(img_data))
                        images.append((page_index + 1, pil_image))  # 保存原始页码

                    doc.close()
                    conversion_method = 'pymupdf'
                    is_partial = bool(page_list)  # 是否为部分转换
                    self.logger.info(f"✅ PyMuPDF转换成功，共{len(images)}页 (原PDF {source_total_pages}页)")
                    if is_partial:
                        self.logger.info(f"   部分转换：从{source_total_pages}页中选择了{len(images)}个关键页")

                except ImportError as import_error:
                    self.logger.error(f"缺少必要的库: {import_error}")
                    return {
                        'success': False,
                        'error': '缺少PDF处理库。请安装: pip install pdf2image pillow 或 pip install PyMuPDF'
                    }
                except Exception as pymupdf_error:
                    self.logger.error(f"PyMuPDF转换也失败: {pymupdf_error}")
                    return {
                        'success': False,
                        'error': f'PDF转换失败（尝试了pdf2image和PyMuPDF）: {str(pymupdf_error)}'
                    }

            if not images:
                return {
                    'success': False,
                    'error': 'PDF转换失败：无法使用任何可用方法转换'
                }

            # 处理每一页
            result_images = []
            prefix = custom_prefix or self.config.page_prefix

            # 检查images是否包含页码信息（PyMuPDF返回元组）
            has_page_nums = images and isinstance(images[0], tuple)

            for i, img_data in enumerate(images, 1):
                # 提取图片对象和原始页码
                if has_page_nums:
                    original_page_num, image = img_data
                else:
                    original_page_num = i
                    image = img_data

                self.logger.debug(f"处理第{i}页（原始页码{original_page_num}），原始尺寸: {image.width}x{image.height}")

                # 优化图片尺寸
                optimized_image = self._optimize_image(image)
                self.logger.debug(f"优化后尺寸: {optimized_image.width}x{optimized_image.height}")

                # 生成文件名
                ext = self.config.output_format.lower()
                filename = f'{prefix}_{i:03d}.{ext}'
                image_path = output_dir / filename

                # 保存图片
                if self.config.output_format.upper() in ['JPEG', 'JPG']:
                    optimized_image.save(
                        str(image_path),
                        'JPEG',
                        quality=self.config.quality,
                        optimize=True
                    )
                else:
                    optimized_image.save(str(image_path), self.config.output_format.upper())

                self.logger.info(f"保存图片: {image_path}")

                # 记录图片信息
                result_images.append({
                    'page_num': original_page_num,  # 使用原始页码
                    'file_path': str(image_path),
                    'width': optimized_image.width,
                    'height': optimized_image.height
                })

            # 获取源PDF总页数
            try:
                import fitz
                doc = fitz.open(pdf_path)
                source_total_pages = len(doc)
                doc.close()
            except:
                source_total_pages = len(result_images)

            # 构建结果
            result = {
                'success': True,
                'original_pdf': pdf_path,
                'images': result_images,
                'total_pages': len(result_images),
                'source_total_pages': source_total_pages,  # 【新增】原PDF总页数
                'is_partial': bool(page_list),  # 【新增】是否为部分转换
                'output_dir': str(output_dir),
                'conversion_method': conversion_method  # 记录使用的转换方法
            }

            # 缓存结果
            self._cache[file_hash] = result

            self.logger.info(f"PDF转换完成（使用{conversion_method}），共生成{len(result_images)}张图片")
            return result

        except Exception as e:
            self.logger.error(f"转换过程出错: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return {
                'success': False,
                'error': f'转换过程出错: {str(e)}'
            }

    def _optimize_image(self, image) -> Any:
        """
        优化图片尺寸

        Args:
            image: PIL Image对象

        Returns:
            优化后的图片
        """
        from PIL import Image

        # 如果图片宽度超过最大宽度，按比例缩放
        if image.width > self.config.max_width:
            ratio = self.config.max_width / image.width
            new_size = (
                self.config.max_width,
                int(image.height * ratio)
            )
            return image.resize(new_size, Image.Resampling.LANCZOS)

        return image

    def _calculate_file_hash(self, file_path: str) -> str:
        """计算文件哈希值"""
        hasher = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hasher.update(chunk)
        return hasher.hexdigest()

    def extract_text(self, pdf_path: str) -> Dict[str, Any]:
        """
        从PDF提取文本

        Args:
            pdf_path: PDF文件路径

        Returns:
            提取结果
        """
        try:
            import PyPDF2

            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                pages_text = []

                for page_num, page in enumerate(pdf_reader.pages, 1):
                    page_text = page.extract_text()
                    text += page_text + "\n"
                    pages_text.append({
                        'page_num': page_num,
                        'text': page_text
                    })

                return {
                    'success': True,
                    'text': text,
                    'pages_text': pages_text,
                    'total_pages': len(pdf_reader.pages)
                }

        except ImportError:
            return {
                'success': False,
                'error': '缺少PyPDF2库，请安装: pip install PyPDF2'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'文本提取失败: {str(e)}'
            }

    def clear_cache(self):
        """清空缓存"""
        self._cache.clear()
        self.logger.info("缓存已清空")


class PDFDetector:
    """PDF文件检测器"""

    @staticmethod
    def is_pdf(file_path: str) -> bool:
        """
        检测文件是否为PDF

        Args:
            file_path: 文件路径

        Returns:
            是否为PDF文件
        """
        # 先检查扩展名
        if not str(file_path).lower().endswith('.pdf'):
            return False

        # 检查文件头（PDF文件以 %PDF 开头）
        try:
            with open(file_path, 'rb') as f:
                header = f.read(4)
                return header == b'%PDF'
        except:
            return False

    @staticmethod
    def get_pdf_info(file_path: str) -> Optional[Dict[str, Any]]:
        """
        获取PDF文件信息

        Args:
            file_path: PDF文件路径

        Returns:
            PDF信息字典或None
        """
        try:
            import PyPDF2

            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)

                # 获取文档信息
                info = pdf_reader.metadata if hasattr(pdf_reader, 'metadata') else {}

                return {
                    'page_count': len(pdf_reader.pages),
                    'title': info.get('/Title', '') if info else '',
                    'author': info.get('/Author', '') if info else '',
                    'subject': info.get('/Subject', '') if info else '',
                    'creator': info.get('/Creator', '') if info else '',
                    'file_size': os.path.getsize(file_path),
                    'is_encrypted': pdf_reader.is_encrypted if hasattr(pdf_reader, 'is_encrypted') else False
                }
        except Exception as e:
            logger.error(f"获取PDF信息失败: {e}")
            return None


def get_pdf_converter(qual_key: str = None) -> PDFConverter:
    """
    根据资质类型获取配置好的PDF转换器

    Args:
        qual_key: 资质键，如 'audit_report', 'value_added_license' 等

    Returns:
        配置好的PDFConverter实例
    """
    # 高质量资质列表（需要更高的DPI）
    high_quality_quals = [
        'audit_report',           # 审计报告
        'value_added_license',    # 增值业务许可证
        'business_license',       # 营业执照
        'iso9001',               # ISO证书
        'cmmi',                  # CMMI证书
    ]

    # 根据资质类型配置参数
    if qual_key in high_quality_quals:
        config = PDFConversionConfig(
            output_format='JPEG',  # 优化：改用JPEG
            dpi=180,  # 优化：从200降到180（仍然高质量）
            max_width=1400,  # 优化：从1600降到1400
            quality=80  # 优化：从95降到80（高质量但体积小）
        )
    else:
        config = PDFConversionConfig(
            output_format='JPEG',  # 优化：改用JPEG
            dpi=150,  # 标准DPI（保持）
            max_width=1200,  # 优化：从1400降到1200
            quality=75  # 优化：从90降到75（标准质量）
        )

    return PDFConverter(config)


# 导出主要类和函数
__all__ = [
    'PDFConverter',
    'PDFDetector',
    'PDFConversionConfig',
    'ConversionMode',
    'get_pdf_converter'
]