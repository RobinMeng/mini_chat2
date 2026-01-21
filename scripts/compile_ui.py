#!/usr/bin/env python3
"""
UI 文件编译脚本
将 .ui 文件编译为 Python 代码
"""
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
UI_DIR = BASE_DIR / "ui"
OUTPUT_DIR = BASE_DIR / "src" / "ui" / "generated"

def compile_ui_files():
    """编译所有 .ui 文件"""
    # 确保输出目录存在
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # 创建 __init__.py
    init_file = OUTPUT_DIR / "__init__.py"
    init_file.write_text('"""自动生成的 UI 文件"""\n')
    
    # 查找所有 .ui 文件
    ui_files = list(UI_DIR.glob("*.ui"))
    
    if not ui_files:
        print("未找到 .ui 文件")
        return
    
    print(f"找到 {len(ui_files)} 个 .ui 文件")
    
    for ui_file in ui_files:
        # 生成输出文件名
        output_name = f"ui_{ui_file.stem}.py"
        output_file = OUTPUT_DIR / output_name
        
        # 执行编译
        cmd = f'pyuic5 "{ui_file}" -o "{output_file}"'
        print(f"编译: {ui_file.name} -> {output_name}")
        
        ret = os.system(cmd)
        
        if ret == 0:
            print(f"  ✓ 成功")
        else:
            print(f"  ✗ 失败 (返回码: {ret})")
    
    print("\n编译完成！")
    print(f"生成的文件位于: {OUTPUT_DIR}")

if __name__ == "__main__":
    try:
        compile_ui_files()
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)
