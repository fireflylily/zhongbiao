#!/usr/bin/env python3
"""
CSS压缩工具
使用rcssmin库压缩CSS文件,减少文件大小,提升加载性能
"""

import os
import rcssmin
from pathlib import Path

def minify_css_file(source_path, target_path=None):
    """
    压缩单个CSS文件

    Args:
        source_path: 源CSS文件路径
        target_path: 目标压缩文件路径,默认为源文件名.min.css
    """
    source_path = Path(source_path)

    if not source_path.exists():
        print(f"❌ 文件不存在: {source_path}")
        return False

    # 读取源文件
    with open(source_path, 'r', encoding='utf-8') as f:
        css_content = f.read()

    # 压缩CSS
    minified_css = rcssmin.cssmin(css_content)

    # 确定目标路径
    if target_path is None:
        target_path = source_path.parent / f"{source_path.stem}.min.css"
    else:
        target_path = Path(target_path)

    # 写入压缩后的文件
    with open(target_path, 'w', encoding='utf-8') as f:
        f.write(minified_css)

    # 计算压缩比
    original_size = len(css_content)
    minified_size = len(minified_css)
    compression_ratio = (1 - minified_size / original_size) * 100

    print(f"✅ {source_path.name}")
    print(f"   原始大小: {original_size:,} bytes")
    print(f"   压缩后: {minified_size:,} bytes")
    print(f"   压缩率: {compression_ratio:.1f}%")
    print()

    return True

def minify_all_css(directory):
    """
    压缩目录下所有CSS文件(递归)

    Args:
        directory: CSS文件目录
    """
    directory = Path(directory)

    if not directory.exists():
        print(f"❌ 目录不存在: {directory}")
        return

    # 查找所有CSS文件(排除已压缩的.min.css文件)
    css_files = [
        f for f in directory.rglob('*.css')
        if not f.name.endswith('.min.css') and f.name != 'minify_css.py'
    ]

    if not css_files:
        print(f"⚠️  目录中没有找到CSS文件: {directory}")
        return

    print(f"📦 开始压缩 {len(css_files)} 个CSS文件...\n")

    total_original = 0
    total_minified = 0
    success_count = 0

    for css_file in css_files:
        # 读取原始大小
        with open(css_file, 'r', encoding='utf-8') as f:
            original_content = f.read()

        # 压缩
        if minify_css_file(css_file):
            success_count += 1
            # 读取压缩后的大小
            minified_path = css_file.parent / f"{css_file.stem}.min.css"
            with open(minified_path, 'r', encoding='utf-8') as f:
                minified_content = f.read()

            total_original += len(original_content)
            total_minified += len(minified_content)

    # 打印总结
    print("=" * 60)
    print(f"✨ 压缩完成! 成功压缩 {success_count}/{len(css_files)} 个文件")
    print(f"📊 总原始大小: {total_original:,} bytes ({total_original/1024:.1f} KB)")
    print(f"📉 总压缩后: {total_minified:,} bytes ({total_minified/1024:.1f} KB)")
    print(f"💾 节省空间: {total_original - total_minified:,} bytes ({(total_original - total_minified)/1024:.1f} KB)")
    print(f"📈 总压缩率: {(1 - total_minified/total_original)*100:.1f}%")
    print("=" * 60)

if __name__ == '__main__':
    # 获取当前脚本所在目录(css目录)
    css_dir = Path(__file__).parent

    print("🚀 CSS压缩工具")
    print(f"📂 目标目录: {css_dir}")
    print()

    minify_all_css(css_dir)
