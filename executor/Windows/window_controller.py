"""
Windows 窗口控制器 - 核心窗口操作功能

简化的窗口操作接口，专为手势控制设计
"""

import time
import win32gui
import win32con
import win32api
import win32process
import psutil
from typing import Optional, Tuple, List, Dict, Any
from dataclasses import dataclass


@dataclass
class WindowInfo:
    """窗口信息数据类"""
    hwnd: int                    # 窗口句柄
    title: str                   # 窗口标题
    class_name: str             # 窗口类名
    pid: int                    # 进程ID
    process_name: str           # 进程名称
    x: int                      # 窗口X坐标
    y: int                      # 窗口Y坐标
    width: int                  # 窗口宽度
    height: int                 # 窗口高度
    is_visible: bool            # 是否可见
    is_minimized: bool          # 是否最小化
    is_maximized: bool          # 是否最大化


class WindowController:
    """Windows 窗口控制器"""
    
    def __init__(self):
        """初始化窗口控制器"""
        self.screen_width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
        self.screen_height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
        self._last_operation_time = {}
        self._operation_cooldown = 0.5  # 操作冷却时间
    
    def get_active_window(self) -> Optional[WindowInfo]:
        """获取当前活动窗口信息"""
        try:
            hwnd = win32gui.GetForegroundWindow()
            return self.get_window_info(hwnd)
        except Exception as e:
            print(f"获取活动窗口失败: {e}")
            return None
    
    def get_window_info(self, hwnd: int) -> Optional[WindowInfo]:
        """获取指定窗口的详细信息"""
        try:
            if not win32gui.IsWindow(hwnd):
                return None
            
            # 获取窗口基本信息
            title = win32gui.GetWindowText(hwnd)
            class_name = win32gui.GetClassName(hwnd)
            
            # 获取进程信息
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            try:
                process = psutil.Process(pid)
                process_name = process.name()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                process_name = "Unknown"
            
            # 获取窗口位置和大小
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            
            # 获取窗口状态
            is_visible = win32gui.IsWindowVisible(hwnd)
            is_minimized = win32gui.IsIconic(hwnd)
            
            # 检查是否最大化
            try:
                is_maximized = win32gui.IsZoomed(hwnd)
            except AttributeError:
                is_maximized = (left <= 0 and top <= 0 and 
                              right >= self.screen_width and bottom >= self.screen_height)
            
            return WindowInfo(
                hwnd=hwnd,
                title=title,
                class_name=class_name,
                pid=pid,
                process_name=process_name,
                x=left,
                y=top,
                width=right - left,
                height=bottom - top,
                is_visible=is_visible,
                is_minimized=is_minimized,
                is_maximized=is_maximized
            )
            
        except Exception as e:
            print(f"获取窗口信息失败: {e}")
            return None
    
    def _check_cooldown(self, operation: str) -> bool:
        """检查操作冷却时间"""
        current_time = time.time()
        if operation in self._last_operation_time:
            if current_time - self._last_operation_time[operation] < self._operation_cooldown:
                return False
        self._last_operation_time[operation] = current_time
        return True
    
    # ===== 窗口移动和拖拽功能 =====
    
    def move_window(self, hwnd: int, x: int, y: int, width: Optional[int] = None, height: Optional[int] = None) -> bool:
        """移动窗口到指定位置"""
        try:
            if not self._check_cooldown(f"move_{hwnd}"):
                return False
            
            if width is None or height is None:
                window_info = self.get_window_info(hwnd)
                if not window_info:
                    return False
                width = width or window_info.width
                height = height or window_info.height
            
            # 确保窗口不会移出屏幕
            x = max(0, min(x, self.screen_width - width))
            y = max(0, min(y, self.screen_height - height))
            
            # SetWindowPos 成功时返回None，失败时抛出异常
            win32gui.SetWindowPos(
                hwnd, 0, x, y, width, height,
                win32con.SWP_NOZORDER | win32con.SWP_NOACTIVATE
            )
            return True  # 没有异常就表示成功
        except Exception as e:
            print(f"移动窗口失败: {e}")
            return False
    
    def drag_window(self, hwnd: int, dx: int, dy: int) -> bool:
        """按偏移量拖拽窗口"""
        try:
            window_info = self.get_window_info(hwnd)
            if not window_info:
                return False
            
            new_x = window_info.x + dx
            new_y = window_info.y + dy
            
            return self.move_window(hwnd, new_x, new_y, window_info.width, window_info.height)
        except Exception as e:
            print(f"拖拽窗口失败: {e}")
            return False
    
    def drag_active_window(self, dx: int, dy: int) -> bool:
        """拖拽当前活动窗口"""
        try:
            window_info = self.get_active_window()
            if not window_info:
                return False
            
            return self.drag_window(window_info.hwnd, dx, dy)
        except Exception as e:
            print(f"拖拽活动窗口失败: {e}")
            return False
    
    # ===== 窗口大小调整功能 =====
    
    def resize_window(self, hwnd: int, width: int, height: int) -> bool:
        """调整窗口大小"""
        try:
            if not self._check_cooldown(f"resize_{hwnd}"):
                return False
            
            window_info = self.get_window_info(hwnd)
            if not window_info:
                return False
            
            # 限制最小尺寸
            width = max(200, width)
            height = max(150, height)
            
            # 限制最大尺寸
            width = min(self.screen_width, width)
            height = min(self.screen_height, height)
            
            # SetWindowPos 成功时返回None，失败时抛出异常
            win32gui.SetWindowPos(
                hwnd, 0, window_info.x, window_info.y, width, height,
                win32con.SWP_NOZORDER | win32con.SWP_NOACTIVATE
            )
            return True  # 没有异常就表示成功
        except Exception as e:
            print(f"调整窗口大小失败: {e}")
            return False
    
    def resize_window_by_scale(self, hwnd: int, scale_factor: float) -> bool:
        """按比例调整窗口大小"""
        try:
            window_info = self.get_window_info(hwnd)
            if not window_info:
                return False
            
            new_width = int(window_info.width * scale_factor)
            new_height = int(window_info.height * scale_factor)
            
            return self.resize_window(hwnd, new_width, new_height)
        except Exception as e:
            print(f"按比例调整窗口大小失败: {e}")
            return False
    
    # ===== 窗口状态控制功能 =====
    
    def maximize_window(self, hwnd: int) -> bool:
        """最大化窗口"""
        try:
            if not self._check_cooldown(f"maximize_{hwnd}"):
                return False
            
            # ShowWindow 成功时返回None，失败时抛出异常
            win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
            return True  # 没有异常就表示成功
        except Exception as e:
            print(f"最大化窗口失败: {e}")
            return False
    
    def minimize_window(self, hwnd: int) -> bool:
        """最小化窗口"""
        try:
            if not self._check_cooldown(f"minimize_{hwnd}"):
                return False
            
            # ShowWindow 成功时返回None，失败时抛出异常
            win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
            return True  # 没有异常就表示成功
        except Exception as e:
            print(f"最小化窗口失败: {e}")
            return False
    
    def restore_window(self, hwnd: int) -> bool:
        """还原窗口"""
        try:
            if not self._check_cooldown(f"restore_{hwnd}"):
                return False
            
            # ShowWindow 成功时返回None，失败时抛出异常
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            return True  # 没有异常就表示成功
        except Exception as e:
            print(f"还原窗口失败: {e}")
            return False
    
    def close_window(self, hwnd: int) -> bool:
        """关闭窗口"""
        try:
            # PostMessage 返回None表示成功
            win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
            return True  # 没有异常就表示成功
        except Exception as e:
            print(f"关闭窗口失败: {e}")
            return False
    
    # ===== 窗口贴靠功能 =====
    
    def snap_window_left(self, hwnd: int) -> bool:
        """将窗口贴靠到屏幕左半部"""
        try:
            # 先还原窗口
            self.restore_window(hwnd)
            time.sleep(0.1)
            
            width = self.screen_width // 2
            height = self.screen_height
            return self.move_window(hwnd, 0, 0, width, height)
        except Exception as e:
            print(f"窗口左贴靠失败: {e}")
            return False
    
    def snap_window_right(self, hwnd: int) -> bool:
        """将窗口贴靠到屏幕右半部"""
        try:
            # 先还原窗口
            self.restore_window(hwnd)
            time.sleep(0.1)
            
            width = self.screen_width // 2
            height = self.screen_height
            x = self.screen_width // 2
            return self.move_window(hwnd, x, 0, width, height)
        except Exception as e:
            print(f"窗口右贴靠失败: {e}")
            return False
    
    def snap_window_top_left(self, hwnd: int) -> bool:
        """将窗口贴靠到左上角1/4屏幕"""
        try:
            self.restore_window(hwnd)
            time.sleep(0.1)
            
            width = self.screen_width // 2
            height = self.screen_height // 2
            return self.move_window(hwnd, 0, 0, width, height)
        except Exception as e:
            print(f"窗口左上贴靠失败: {e}")
            return False
    
    def snap_window_top_right(self, hwnd: int) -> bool:
        """将窗口贴靠到右上角1/4屏幕"""
        try:
            self.restore_window(hwnd)
            time.sleep(0.1)
            
            width = self.screen_width // 2
            height = self.screen_height // 2
            x = self.screen_width // 2
            return self.move_window(hwnd, x, 0, width, height)
        except Exception as e:
            print(f"窗口右上贴靠失败: {e}")
            return False
    
    def snap_window_bottom_left(self, hwnd: int) -> bool:
        """将窗口贴靠到左下角1/4屏幕"""
        try:
            self.restore_window(hwnd)
            time.sleep(0.1)
            
            width = self.screen_width // 2
            height = self.screen_height // 2
            y = self.screen_height // 2
            return self.move_window(hwnd, 0, y, width, height)
        except Exception as e:
            print(f"窗口左下贴靠失败: {e}")
            return False
    
    def snap_window_bottom_right(self, hwnd: int) -> bool:
        """将窗口贴靠到右下角1/4屏幕"""
        try:
            self.restore_window(hwnd)
            time.sleep(0.1)
            
            width = self.screen_width // 2
            height = self.screen_height // 2
            x = self.screen_width // 2
            y = self.screen_height // 2
            return self.move_window(hwnd, x, y, width, height)
        except Exception as e:
            print(f"窗口右下贴靠失败: {e}")
            return False
    
    # ===== 便捷的活动窗口操作方法 =====
    
    def maximize_active_window(self) -> bool:
        """最大化当前活动窗口"""
        window_info = self.get_active_window()
        return self.maximize_window(window_info.hwnd) if window_info else False
    
    def minimize_active_window(self) -> bool:
        """最小化当前活动窗口"""
        window_info = self.get_active_window()
        return self.minimize_window(window_info.hwnd) if window_info else False
    
    def restore_active_window(self) -> bool:
        """还原当前活动窗口"""
        window_info = self.get_active_window()
        return self.restore_window(window_info.hwnd) if window_info else False
    
    def close_active_window(self) -> bool:
        """关闭当前活动窗口"""
        window_info = self.get_active_window()
        return self.close_window(window_info.hwnd) if window_info else False
    
    def snap_active_window_left(self) -> bool:
        """将当前活动窗口贴靠到左半屏"""
        window_info = self.get_active_window()
        return self.snap_window_left(window_info.hwnd) if window_info else False
    
    def snap_active_window_right(self) -> bool:
        """将当前活动窗口贴靠到右半屏"""
        window_info = self.get_active_window()
        return self.snap_window_right(window_info.hwnd) if window_info else False
    
    def resize_active_window_by_scale(self, scale_factor: float) -> bool:
        """按比例调整当前活动窗口大小"""
        window_info = self.get_active_window()
        return self.resize_window_by_scale(window_info.hwnd, scale_factor) if window_info else False
    
    # ===== 实用工具方法 =====
    
    def get_screen_size(self) -> Tuple[int, int]:
        """获取屏幕大小"""
        return self.screen_width, self.screen_height
    
    def center_window(self, hwnd: int, width: Optional[int] = None, height: Optional[int] = None) -> bool:
        """将窗口居中显示"""
        try:
            if width is None or height is None:
                window_info = self.get_window_info(hwnd)
                if not window_info:
                    return False
                width = width or window_info.width
                height = height or window_info.height
            
            x = (self.screen_width - width) // 2
            y = (self.screen_height - height) // 2
            
            return self.move_window(hwnd, x, y, width, height)
        except Exception as e:
            print(f"窗口居中失败: {e}")
            return False
    
    def center_active_window(self) -> bool:
        """将当前活动窗口居中"""
        window_info = self.get_active_window()
        return self.center_window(window_info.hwnd) if window_info else False
