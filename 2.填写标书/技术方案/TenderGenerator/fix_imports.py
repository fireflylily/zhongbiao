#!/usr/bin/env python3
"""
修复导入问题的脚本
"""

import os
import re
from pathlib import Path

def fix_relative_imports(file_path):
    """修复文件中的相对导入"""
    print(f"处理文件: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找相对导入
    relative_import_pattern = r'from \.\.[a-zA-Z_.]+ import'
    
    if re.search(relative_import_pattern, content):
        print(f"  发现相对导入，需要修复")
        
        # 为每个相对导入添加try-except包装
        lines = content.split('\n')
        new_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # 检查是否是相对导入
            if re.match(r'from \.\.[a-zA-Z_.]+ import', line.strip()):
                # 找到连续的相对导入行
                import_lines = []
                while i < len(lines) and re.match(r'from \.\.[a-zA-Z_.]+ import', lines[i].strip()):
                    import_lines.append(lines[i])
                    i += 1
                
                # 生成修复后的导入代码
                try_block = ['try:']
                try_block.extend(['    ' + imp_line for imp_line in import_lines])
                try_block.append('except ImportError:')
                try_block.append('    import sys')
                try_block.append('    from pathlib import Path')
                try_block.append('    sys.path.append(str(Path(__file__).parent.parent))')
                
                # 生成对应的绝对导入
                for imp_line in import_lines:
                    # 将 from ..utils.xxx import 转换为 from utils.xxx import
                    abs_import = imp_line.replace('from ..', 'from ')
                    try_block.append('    ' + abs_import)
                
                new_lines.extend(try_block)
                i -= 1  # 因为while循环会多加1
                
            else:
                new_lines.append(line)
            
            i += 1
        
        # 写回文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_lines))
        
        print(f"  ✅ 修复完成")
    else:
        print(f"  无需修复")

def main():
    """主函数"""
    print("=== 修复相对导入问题 ===\n")
    
    # 需要检查的目录和文件
    dirs_to_check = ['parsers', 'matchers', 'generators', 'utils']
    
    for dir_name in dirs_to_check:
        if os.path.isdir(dir_name):
            print(f"\n检查目录: {dir_name}/")
            
            for file_name in os.listdir(dir_name):
                if file_name.endswith('.py') and file_name != '__init__.py':
                    file_path = os.path.join(dir_name, file_name)
                    fix_relative_imports(file_path)
    
    print("\n=== 修复完成 ===")

if __name__ == "__main__":
    main()