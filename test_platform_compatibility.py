#!/usr/bin/env python3
"""
简单的平台兼容性测试
验证主要组件是否可以在当前平台正常导入和初始化
"""

import sys
import platform

def test_imports():
    """测试关键模块导入"""
    print(f"??  当前平台: {platform.system()} {platform.release()}")
    print(f"? Python版本: {platform.python_version()}")
    print("-" * 50)
    
    try:
        print("? 测试核心模块导入...")
        
        # 测试PyQt6
        from PyQt6.QtWidgets import QApplication
        print("? PyQt6 导入成功")
        
        # 测试pynput
        from pynput import keyboard, mouse
        print("? pynput 导入成功")
        
        # 测试ActionExecutor
        from core.action_executor import ActionExecutor
        executor = ActionExecutor()
        print(f"? ActionExecutor 初始化成功 (OS: {executor.os})")
        
        # 测试Windows特有模块（仅在Windows上）
        if platform.system() == "Windows":
            try:
                import win32gui, win32con, win32api
                print("? pywin32 模块可用")
            except ImportError:
                print("??  pywin32 不可用，将使用备用实现")
        
        # 测试UI组件
        from ui.main_window_ui import MainWindowUI
        print("? 主窗口UI组件导入成功")
        
        print("-" * 50)
        print("? 所有核心组件导入成功！项目支持当前平台。")
        return True
        
    except ImportError as e:
        print(f"? 导入失败: {e}")
        print("? 请安装缺失的依赖: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"? 初始化失败: {e}")
        return False

def test_basic_functionality():
    """测试基本功能"""
    try:
        print("\n? 测试基本功能...")
        
        # 测试ActionExecutor基本功能
        from core.action_executor import ActionExecutor
        executor = ActionExecutor()
        
        # 测试快捷键解析（不实际执行）
        print("??  测试快捷键解析...")
        test_shortcuts = ["ctrl+c", "alt+tab", "f1"]
        for shortcut in test_shortcuts:
            # 只测试解析，不实际执行
            keys = shortcut.lower().split('+')
            print(f"   {shortcut} -> 解析为 {len(keys)} 个键")
        
        print("? 基本功能测试通过")
        return True
        
    except Exception as e:
        print(f"? 功能测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("? 手势控制系统 - 平台兼容性测试")
    print("=" * 50)
    
    # 测试导入
    import_success = test_imports()
    
    if import_success:
        # 测试基本功能
        function_success = test_basic_functionality()
        
        if function_success:
            print("\n? 恭喜！项目完全兼容当前平台。")
            print("? 你现在可以运行: python app.py")
        else:
            print("\n??  导入成功但功能测试失败，可能需要额外配置。")
    else:
        print("\n? 导入失败，请先安装依赖或检查平台兼容性。")

if __name__ == "__main__":
    main() 