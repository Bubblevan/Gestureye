#!/usr/bin/env python3
"""
手势检测应用程序入口
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from PyQt6.QtWidgets import QApplication
from ui.main_window_ui import MainWindowUI


def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 设置应用程序信息
    app.setApplicationName("手势检测控制中心")
    app.setApplicationVersion("1.0.0")
    
    # 创建主窗口
    window = MainWindowUI()
    window.show()
    
    # 运行应用程序
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 