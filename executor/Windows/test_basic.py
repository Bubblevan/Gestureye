"""
Windows API Easy 简单测试脚本

测试基本功能是否正常工作
"""

import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def test_imports():
    """测试模块导入"""
    print("=== 测试模块导入 ===")
    try:
        from windows_api_easy import window_controller, window_finder, gesture_operator
        print("✓ 成功导入所有模块")
        return True
    except Exception as e:
        print(f"✗ 导入失败: {e}")
        return False

def test_window_info():
    """测试窗口信息获取"""
    print("\n=== 测试窗口信息获取 ===")
    try:
        from windows_api_easy import window_controller
        
        # 获取活动窗口
        active_window = window_controller.get_active_window()
        if active_window:
            print(f"✓ 当前活动窗口: {active_window.title}")
            print(f"  进程: {active_window.process_name}")
            print(f"  位置: ({active_window.x}, {active_window.y})")
            print(f"  大小: {active_window.width} x {active_window.height}")
            print(f"  状态: 可见={active_window.is_visible}, 最小化={active_window.is_minimized}")
            return True
        else:
            print("✗ 无法获取活动窗口")
            return False
    except Exception as e:
        print(f"✗ 获取窗口信息失败: {e}")
        return False

def test_window_finding():
    """测试窗口查找功能"""
    print("\n=== 测试窗口查找功能 ===")
    try:
        from windows_api_easy import window_finder
        
        # 查找可见窗口
        visible_windows = window_finder.find_visible_windows()
        print(f"✓ 找到 {len(visible_windows)} 个可见窗口")
        
        # 显示前3个窗口
        for i, window in enumerate(visible_windows[:3]):
            print(f"  {i+1}. {window.title} ({window.process_name})")
        
        # 查找浏览器窗口
        browser_windows = window_finder.find_browser_windows()
        print(f"✓ 找到 {len(browser_windows)} 个浏览器窗口")
        
        return True
    except Exception as e:
        print(f"✗ 窗口查找失败: {e}")
        return False

def test_gesture_actions():
    """测试手势动作"""
    print("\n=== 测试手势动作 ===")
    try:
        from windows_api_easy import gesture_operator
        
        # 获取可用动作
        actions = gesture_operator.get_available_actions()
        print(f"✓ 可用的手势动作 ({len(actions)} 个):")
        for action in actions[:5]:  # 只显示前5个
            print(f"  - {action}")
        
        # 获取窗口状态
        status = gesture_operator.get_window_status()
        if 'error' not in status:
            print(f"✓ 当前窗口状态: {status['title']}")
            return True
        else:
            print(f"✗ 获取窗口状态失败: {status['error']}")
            return False
    except Exception as e:
        print(f"✗ 手势动作测试失败: {e}")
        return False

def test_basic_operations():
    """测试基本操作（非破坏性）"""
    print("\n=== 测试基本操作 ===")
    try:
        from windows_api_easy import window_controller
        
        # 获取屏幕大小
        screen_width, screen_height = window_controller.get_screen_size()
        print(f"✓ 屏幕大小: {screen_width} x {screen_height}")
        
        # 获取当前窗口位置（不修改）
        active_window = window_controller.get_active_window()
        if active_window:
            print(f"✓ 当前窗口位置: ({active_window.x}, {active_window.y})")
            print(f"✓ 当前窗口大小: {active_window.width} x {active_window.height}")
            return True
        else:
            print("✗ 无法获取活动窗口")
            return False
    except Exception as e:
        print(f"✗ 基本操作测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("Windows API Easy 功能测试")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_window_info,
        test_window_finding,
        test_gesture_actions,
        test_basic_operations
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"测试异常: {e}")
    
    print(f"\n测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("✓ 所有测试通过！windows_api_easy 模块工作正常")
    else:
        print("✗ 部分测试失败，请检查依赖项和配置")
    
    input("\n按回车键退出...")

if __name__ == "__main__":
    main()
