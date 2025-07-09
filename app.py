#!/usr/bin/env python3
"""
手势检测应用程序入口
"""

import sys
import os
import platform

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, QSize
from ui.main_window_ui import MainWindowUI

# 平台特定的导入
CURRENT_OS = platform.system()

# Windows特定的导入
if CURRENT_OS == "Windows":
    try:
        import ctypes
        from ctypes import wintypes
        HAS_WINDOWS_API = True
    except ImportError:
        HAS_WINDOWS_API = False
else:
    HAS_WINDOWS_API = False

# macOS特定的导入
if CURRENT_OS == "Darwin":
    try:
        import subprocess
        HAS_MACOS_SUPPORT = True
    except ImportError:
        HAS_MACOS_SUPPORT = False
else:
    HAS_MACOS_SUPPORT = False

# Linux特定的导入
if CURRENT_OS == "Linux":
    try:
        import subprocess
        HAS_LINUX_SUPPORT = True
    except ImportError:
        HAS_LINUX_SUPPORT = False
else:
    HAS_LINUX_SUPPORT = False


def set_windows_app_user_model_id():
    """设置Windows应用程序用户模型ID"""
    if HAS_WINDOWS_API:
        try:
            # 设置应用程序用户模型ID，这有助于Windows正确显示任务栏图标
            app_id = "GestureDetection.MainApp.1.0"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
            print("Windows应用程序用户模型ID设置成功")
        except Exception as e:
            print(f"设置Windows应用程序用户模型ID失败: {e}")


def set_linux_desktop_properties():
    """设置Linux桌面属性（可选）"""
    if HAS_LINUX_SUPPORT:
        try:
            # 检查是否在支持的桌面环境中运行
            desktop_env = os.environ.get('XDG_CURRENT_DESKTOP', '').lower()
            if desktop_env:
                print(f"检测到桌面环境: {desktop_env}")
                # 在Linux上，图标主要通过Qt的setWindowIcon处理
                # 桌面文件(.desktop)可以进一步优化集成，但不是必需的
        except Exception as e:
            print(f"Linux桌面属性设置失败: {e}")


def set_macos_app_properties():
    """设置macOS应用程序属性（可选）"""
    if HAS_MACOS_SUPPORT:
        try:
            # 在macOS上，Qt的setWindowIcon通常足够
            # 对于更完整的集成，可以设置Info.plist，但对于开发阶段不是必需的
            print("macOS应用程序属性设置完成")
        except Exception as e:
            print(f"macOS应用程序属性设置失败: {e}")


def main():
    """主函数"""
    # 平台特定的设置
    if CURRENT_OS == "Windows":
        set_windows_app_user_model_id()
    elif CURRENT_OS == "Linux":
        set_linux_desktop_properties()
    elif CURRENT_OS == "Darwin":
        set_macos_app_properties()
    
    print(f"在 {CURRENT_OS} 平台上启动应用程序")
    
    app = QApplication(sys.argv)
    
    # 设置应用程序信息
    app.setApplicationName("手势检测控制中心")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("GestureDetection")
    app.setOrganizationDomain("gesturedetection.local")
    
    # 设置应用程序图标（跨平台）
    icon_path = os.path.join(project_root, "DDYN.png")
    if os.path.exists(icon_path):
        icon = QIcon(icon_path)
        
        # 平台特定的图标尺寸优化
        if CURRENT_OS == "Windows":
            # Windows偏好的图标尺寸
            icon_sizes = [16, 24, 32, 48, 64, 128, 256]
        elif CURRENT_OS == "Darwin":
            # macOS偏好的图标尺寸
            icon_sizes = [16, 32, 64, 128, 256, 512]
        elif CURRENT_OS == "Linux":
            # Linux桌面环境常用尺寸
            icon_sizes = [16, 22, 24, 32, 48, 64, 96, 128, 256]
        else:
            # 默认尺寸
            icon_sizes = [16, 24, 32, 48, 64, 128, 256]
        
        # 添加多种尺寸以确保在不同DPI下正确显示
        for size in icon_sizes:
            icon.addFile(icon_path, QSize(size, size), QIcon.Mode.Normal, QIcon.State.Off)
        
        app.setWindowIcon(icon)
        print(f"应用程序图标设置成功 ({CURRENT_OS}): {icon_path}")
        print(f"支持的图标尺寸: {icon_sizes}")
    else:
        print(f"警告: 图标文件不存在: {icon_path}")
    
    # 创建主窗口
    window = MainWindowUI()
    window.show()
    
    # 运行应用程序
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 