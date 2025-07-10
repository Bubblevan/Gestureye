"""
Windows API Easy 使用示例

演示如何使用简化的Windows API进行窗口操作
"""

import time
from windows_api_easy import window_controller, window_finder, gesture_operator


def demo_basic_operations():
    """演示基本窗口操作"""
    print("=== 基本窗口操作演示 ===")
    
    # 获取当前活动窗口
    active_window = window_controller.get_active_window()
    if active_window:
        print(f"当前活动窗口: {active_window.title}")
        print(f"进程名: {active_window.process_name}")
        print(f"位置: ({active_window.x}, {active_window.y})")
        print(f"大小: {active_window.width} x {active_window.height}")
    
    # 等待用户确认
    input("按回车键继续演示窗口操作...")
    
    # 演示窗口移动
    print("移动窗口...")
    window_controller.drag_active_window(100, 50)
    time.sleep(1)
    
    # 演示窗口缩放
    print("放大窗口...")
    window_controller.resize_active_window_by_scale(1.2)
    time.sleep(1)
    
    # 演示窗口居中
    print("窗口居中...")
    window_controller.center_active_window()
    time.sleep(1)
    
    print("基本操作演示完成!")


def demo_window_snapping():
    """演示窗口贴靠功能"""
    print("\n=== 窗口贴靠演示 ===")
    
    input("按回车键开始窗口贴靠演示...")
    
    # 左半屏
    print("贴靠到左半屏...")
    window_controller.snap_active_window_left()
    time.sleep(2)
    
    # 右半屏
    print("贴靠到右半屏...")
    window_controller.snap_active_window_right()
    time.sleep(2)
    
    # 还原窗口
    print("还原窗口...")
    window_controller.restore_active_window()
    time.sleep(1)
    
    print("窗口贴靠演示完成!")


def demo_window_finding():
    """演示窗口查找功能"""
    print("\n=== 窗口查找演示 ===")
    
    # 查找所有可见窗口
    visible_windows = window_finder.find_visible_windows()
    print(f"找到 {len(visible_windows)} 个可见窗口:")
    for i, window in enumerate(visible_windows[:5]):  # 只显示前5个
        print(f"  {i+1}. {window.title} ({window.process_name})")
    
    # 查找浏览器窗口
    browser_windows = window_finder.find_browser_windows()
    print(f"\n找到 {len(browser_windows)} 个浏览器窗口:")
    for window in browser_windows:
        print(f"  - {window.title}")
    
    # 查找代码编辑器窗口
    editor_windows = window_finder.find_code_editor_windows()
    print(f"\n找到 {len(editor_windows)} 个代码编辑器窗口:")
    for window in editor_windows:
        print(f"  - {window.title}")


def demo_gesture_operations():
    """演示手势操作"""
    print("\n=== 手势操作演示 ===")
    
    # 显示可用的手势动作
    actions = gesture_operator.get_available_actions()
    print("可用的手势动作:")
    for action in actions:
        print(f"  - {action}")
    
    # 获取当前窗口状态
    status = gesture_operator.get_window_status()
    print(f"\n当前窗口状态: {status}")
    
    input("\n按回车键开始手势操作演示...")
    
    # 演示不同的手势操作
    gestures_to_demo = ['resize_larger', 'center', 'resize_smaller', 'restore']
    
    for gesture in gestures_to_demo:
        print(f"执行手势动作: {gesture}")
        success = gesture_operator.execute_gesture_action(gesture)
        print(f"执行结果: {'成功' if success else '失败'}")
        time.sleep(1.5)


def demo_drag_simulation():
    """演示拖拽模拟"""
    print("\n=== 拖拽模拟演示 ===")
    
    input("按回车键开始拖拽模拟...")
    
    # 模拟手势拖拽
    drag_sequences = [
        (50, 0, "向右拖拽"),
        (0, 50, "向下拖拽"),
        (-50, 0, "向左拖拽"),
        (0, -50, "向上拖拽")
    ]
    
    for dx, dy, description in drag_sequences:
        print(f"{description}...")
        gesture_operator.drag_window_by_gesture(dx, dy, sensitivity=2.0)
        time.sleep(1)
    
    print("拖拽模拟演示完成!")


def main():
    """主演示函数"""
    print("Windows API Easy 功能演示")
    print("请确保有一个窗口处于活动状态")
    print("=" * 50)
    
    try:
        # 检查是否有活动窗口
        active_window = window_controller.get_active_window()
        if not active_window:
            print("错误: 没有检测到活动窗口!")
            return
        
        # 运行各种演示
        demo_basic_operations()
        demo_window_snapping()
        demo_window_finding()
        demo_gesture_operations()
        demo_drag_simulation()
        
        print("\n所有演示完成!")
        
    except Exception as e:
        print(f"演示过程中出现错误: {e}")
    
    input("\n按回车键退出...")


if __name__ == "__main__":
    main()
