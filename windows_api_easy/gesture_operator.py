"""
手势窗口操作器 - 专为手势控制设计的窗口操作接口

提供简单易用的手势到窗口操作的映射
"""

from typing import Dict, Any, Optional, Tuple
from .window_controller import WindowController
from .window_finder import WindowFinder


class GestureWindowOperator:
    """手势窗口操作器"""
    
    def __init__(self):
        self.controller = WindowController()
        self.finder = WindowFinder()
        
        # 预定义的手势操作映射
        self.gesture_actions = {
            # 窗口状态控制
            'maximize': self.controller.maximize_active_window,
            'minimize': self.controller.minimize_active_window,
            'restore': self.controller.restore_active_window,
            'close': self.controller.close_active_window,
            'center': self.controller.center_active_window,
            
            # 窗口贴靠
            'snap_left': self.controller.snap_active_window_left,
            'snap_right': self.controller.snap_active_window_right,
            'snap_top_left': lambda: self._snap_active_window_quarter('top_left'),
            'snap_top_right': lambda: self._snap_active_window_quarter('top_right'),
            'snap_bottom_left': lambda: self._snap_active_window_quarter('bottom_left'),
            'snap_bottom_right': lambda: self._snap_active_window_quarter('bottom_right'),
            
            # 窗口大小调整
            'resize_larger': lambda: self.controller.resize_active_window_by_scale(1.2),
            'resize_smaller': lambda: self.controller.resize_active_window_by_scale(0.8),
            'resize_double': lambda: self.controller.resize_active_window_by_scale(2.0),
            'resize_half': lambda: self.controller.resize_active_window_by_scale(0.5),
        }
    
    def _snap_active_window_quarter(self, position: str) -> bool:
        """将活动窗口贴靠到四分之一屏幕"""
        window_info = self.controller.get_active_window()
        if not window_info:
            return False
        
        if position == 'top_left':
            return self.controller.snap_window_top_left(window_info.hwnd)
        elif position == 'top_right':
            return self.controller.snap_window_top_right(window_info.hwnd)
        elif position == 'bottom_left':
            return self.controller.snap_window_bottom_left(window_info.hwnd)
        elif position == 'bottom_right':
            return self.controller.snap_window_bottom_right(window_info.hwnd)
        return False
    
    def execute_gesture_action(self, action_name: str) -> bool:
        """执行预定义的手势动作"""
        if action_name in self.gesture_actions:
            try:
                return self.gesture_actions[action_name]()
            except Exception as e:
                print(f"执行手势动作失败 {action_name}: {e}")
                return False
        else:
            print(f"未知的手势动作: {action_name}")
            return False
    
    def drag_window_by_gesture(self, dx: int, dy: int, sensitivity: float = 1.0) -> bool:
        """通过手势拖拽窗口"""
        # 应用敏感度调整
        adjusted_dx = int(dx * sensitivity)
        adjusted_dy = int(dy * sensitivity)
        
        return self.controller.drag_active_window(adjusted_dx, adjusted_dy)
    
    def resize_window_by_gesture(self, scale_delta: float, min_scale: float = 0.1, max_scale: float = 3.0) -> bool:
        """通过手势调整窗口大小"""
        # 限制缩放范围
        scale_delta = max(min_scale, min(scale_delta, max_scale))
        
        return self.controller.resize_active_window_by_scale(scale_delta)
    
    def switch_to_window_by_gesture(self, direction: str) -> bool:
        """通过手势切换到其他窗口"""
        visible_windows = self.finder.find_visible_windows()
        if len(visible_windows) <= 1:
            return False
        
        current_window = self.controller.get_active_window()
        if not current_window:
            return False
        
        # 找到当前窗口在列表中的索引
        current_index = -1
        for i, window in enumerate(visible_windows):
            if window.hwnd == current_window.hwnd:
                current_index = i
                break
        
        if current_index == -1:
            return False
        
        # 根据方向选择下一个窗口
        if direction == 'next':
            next_index = (current_index + 1) % len(visible_windows)
        elif direction == 'previous':
            next_index = (current_index - 1) % len(visible_windows)
        else:
            return False
        
        # 激活选中的窗口
        next_window = visible_windows[next_index]
        try:
            import win32gui
            win32gui.SetForegroundWindow(next_window.hwnd)
            return True
        except Exception as e:
            print(f"切换窗口失败: {e}")
            return False
    
    def get_available_actions(self) -> list:
        """获取所有可用的手势动作"""
        return list(self.gesture_actions.keys())
    
    def get_window_status(self) -> Dict[str, Any]:
        """获取当前窗口状态信息"""
        window_info = self.controller.get_active_window()
        if not window_info:
            return {'error': '无法获取活动窗口'}
        
        return {
            'title': window_info.title,
            'process': window_info.process_name,
            'position': (window_info.x, window_info.y),
            'size': (window_info.width, window_info.height),
            'is_maximized': window_info.is_maximized,
            'is_minimized': window_info.is_minimized,
            'is_visible': window_info.is_visible
        }


# 便捷的全局实例
gesture_operator = GestureWindowOperator()
