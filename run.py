#!/usr/bin/env python3
"""
MiniChat 启动脚本
"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

from src.main import main

if __name__ == "__main__":
    sys.exit(main())
