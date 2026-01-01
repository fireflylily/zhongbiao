#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mermaid 流程图渲染器

将 Mermaid 代码渲染为 PNG 图片
支持本地渲染 (mermaid-cli) 和在线渲染 (kroki.io) 两种方式
"""

import os
import re
import base64
import tempfile
import subprocess
import hashlib
from pathlib import Path
from typing import Optional

import requests

from ...common.logger import get_module_logger
from ...common.config import get_config

logger = get_module_logger("mermaid_renderer")


class MermaidRenderer:
    """
    Mermaid 流程图渲染器

    渲染策略:
    1. 优先使用本地 mermaid-cli (mmdc)
    2. 本地不可用时，使用 kroki.io 在线 API
    """

    # kroki.io API 端点
    KROKI_API = "https://kroki.io/mermaid/png"

    # 备用 kroki 端点
    KROKI_BACKUP_API = "https://kroki.yuzutech.fr/mermaid/png"

    # 图片默认宽度
    DEFAULT_WIDTH = 800

    # 图片默认高度
    DEFAULT_HEIGHT = 600

    def __init__(self, output_dir: Optional[str] = None):
        """
        初始化渲染器

        Args:
            output_dir: 图片输出目录，默认使用临时目录
        """
        config = get_config()
        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            # 使用项目的临时目录
            self.output_dir = config.get_path('data') / 'temp' / 'mermaid'

        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logger

        # 检测本地 mermaid-cli 是否可用
        self.use_local = self._check_mermaid_cli()
        if self.use_local:
            self.logger.info("Mermaid 渲染器: 使用本地 mermaid-cli")
        else:
            self.logger.info("Mermaid 渲染器: 使用 kroki.io 在线 API")

    def _check_mermaid_cli(self) -> bool:
        """检查本地 mermaid-cli 是否可用"""
        try:
            result = subprocess.run(
                ['mmdc', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def render_to_png(
        self,
        mermaid_code: str,
        filename: Optional[str] = None,
        width: int = DEFAULT_WIDTH,
        height: int = DEFAULT_HEIGHT
    ) -> Optional[str]:
        """
        将 Mermaid 代码渲染为 PNG 图片

        Args:
            mermaid_code: Mermaid 语法代码
            filename: 输出文件名 (不含扩展名)，默认使用代码哈希
            width: 图片宽度
            height: 图片高度

        Returns:
            生成的 PNG 文件路径，失败返回 None
        """
        # 清洗代码
        clean_code = self._sanitize_mermaid_code(mermaid_code)

        # 生成文件名
        if not filename:
            code_hash = hashlib.md5(clean_code.encode()).hexdigest()[:12]
            filename = f"flowchart_{code_hash}"

        output_path = self.output_dir / f"{filename}.png"

        # 如果文件已存在且有效，直接返回
        if output_path.exists() and output_path.stat().st_size > 0:
            self.logger.info(f"使用已缓存的图片: {output_path}")
            return str(output_path)

        # 选择渲染方式
        if self.use_local:
            result = self._render_local(clean_code, output_path, width, height)
        else:
            result = self._render_online(clean_code, output_path)

        if result:
            self.logger.info(f"Mermaid 渲染成功: {output_path}")
        else:
            self.logger.error(f"Mermaid 渲染失败")

        return result

    def _render_local(
        self,
        code: str,
        output_path: Path,
        width: int,
        height: int
    ) -> Optional[str]:
        """
        使用本地 mermaid-cli (mmdc) 渲染

        Args:
            code: Mermaid 代码
            output_path: 输出路径
            width: 图片宽度
            height: 图片高度

        Returns:
            成功返回文件路径，失败返回 None
        """
        try:
            # 创建临时输入文件
            with tempfile.NamedTemporaryFile(
                mode='w',
                suffix='.mmd',
                delete=False,
                encoding='utf-8'
            ) as f:
                f.write(code)
                input_path = f.name

            try:
                # 调用 mmdc 命令
                result = subprocess.run(
                    [
                        'mmdc',
                        '-i', input_path,
                        '-o', str(output_path),
                        '-w', str(width),
                        '-H', str(height),
                        '-b', 'transparent'  # 透明背景
                    ],
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if result.returncode == 0 and output_path.exists():
                    return str(output_path)
                else:
                    self.logger.error(f"mmdc 渲染失败: {result.stderr}")
                    return None

            finally:
                # 清理临时文件
                if os.path.exists(input_path):
                    os.unlink(input_path)

        except subprocess.TimeoutExpired:
            self.logger.error("mmdc 渲染超时")
            return None
        except Exception as e:
            self.logger.error(f"本地渲染失败: {e}")
            return None

    def _render_online(self, code: str, output_path: Path) -> Optional[str]:
        """
        使用 kroki.io API 在线渲染

        Args:
            code: Mermaid 代码
            output_path: 输出路径

        Returns:
            成功返回文件路径，失败返回 None
        """
        # 尝试主 API
        result = self._try_kroki_api(self.KROKI_API, code, output_path)
        if result:
            return result

        # 尝试备用 API
        self.logger.info("主 API 失败，尝试备用 API")
        return self._try_kroki_api(self.KROKI_BACKUP_API, code, output_path)

    def _try_kroki_api(
        self,
        api_url: str,
        code: str,
        output_path: Path
    ) -> Optional[str]:
        """尝试调用 kroki API"""
        try:
            # 将代码编码为 base64
            encoded = base64.urlsafe_b64encode(code.encode('utf-8')).decode('utf-8')

            # 发送请求
            response = requests.get(
                f"{api_url}/{encoded}",
                timeout=30,
                headers={'Accept': 'image/png'}
            )

            if response.status_code == 200:
                # 保存图片
                with open(output_path, 'wb') as f:
                    f.write(response.content)

                if output_path.exists() and output_path.stat().st_size > 0:
                    return str(output_path)

            self.logger.warning(
                f"kroki API 请求失败: {response.status_code} - {response.text[:100]}"
            )
            return None

        except requests.Timeout:
            self.logger.error(f"kroki API 超时: {api_url}")
            return None
        except requests.RequestException as e:
            self.logger.error(f"kroki API 请求异常: {e}")
            return None

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
                        'stateDiagram', 'erDiagram', 'gantt', 'pie', 'mindmap']
        if not any(code.strip().startswith(s) for s in valid_starts):
            # 默认添加 flowchart TD
            code = f"flowchart TD\n{code}"

        # 3. 修复常见语法问题
        # 中文引号转英文引号
        code = code.replace('"', '"').replace('"', '"')
        code = code.replace(''', "'").replace(''', "'")

        # 处理转义的换行符
        code = code.replace('\\n', '\n')

        # 移除空行
        lines = [line for line in code.split('\n') if line.strip()]
        code = '\n'.join(lines)

        return code

    def cleanup(self, max_age_hours: int = 24):
        """
        清理过期的临时文件

        Args:
            max_age_hours: 最大保留时间(小时)
        """
        import time

        now = time.time()
        max_age_seconds = max_age_hours * 3600

        try:
            for file_path in self.output_dir.glob('*.png'):
                if now - file_path.stat().st_mtime > max_age_seconds:
                    file_path.unlink()
                    self.logger.info(f"清理过期文件: {file_path}")
        except Exception as e:
            self.logger.error(f"清理文件失败: {e}")

    def cleanup_all(self):
        """清理所有临时文件"""
        try:
            for file_path in self.output_dir.glob('*.png'):
                file_path.unlink()
            self.logger.info(f"已清理所有 Mermaid 临时文件")
        except Exception as e:
            self.logger.error(f"清理文件失败: {e}")


# 全局实例
_renderer_instance = None


def get_mermaid_renderer() -> MermaidRenderer:
    """获取全局 Mermaid 渲染器实例"""
    global _renderer_instance
    if _renderer_instance is None:
        _renderer_instance = MermaidRenderer()
    return _renderer_instance
