#!/usr/bin/env python3
"""
Silent Binary Hardening Issues Extractor - 程序入口点
这个文件仅作为程序的入口点，实际的main函数在src/main.py中
"""

import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

def main():
    """程序入口点"""
    try:
        from main import main as src_main
        src_main()
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请确保项目结构正确，src/main.py文件存在")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 程序运行错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
