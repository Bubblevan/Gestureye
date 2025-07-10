"""
Windows 窗口查找器 - 提供各种窗口查找功能

简化的窗口查找工具，专为手势控制设计
"""

import re
import win32gui
import win32process
import psutil
from typing import List, Optional, Callable
from .window_controller import WindowInfo, WindowController


class WindowFinder:
    """窗口查找工具类"""
    
    def __init__(self):
        self.window_controller = WindowController()
    
    def find_all_windows(self, include_invisible: bool = False) -> List[WindowInfo]:
        """获取所有窗口列表"""
        windows = []
        
        def enum_callback(hwnd, _):
            window_info = self.window_controller.get_window_info(hwnd)
            if window_info and (include_invisible or window_info.is_visible):
                # 过滤掉没有标题的系统窗口
                if window_info.title.strip():
                    windows.append(window_info)
            return True
        
        try:
            win32gui.EnumWindows(enum_callback, None)
        except Exception as e:
            print(f"枚举窗口失败: {e}")
        
        return windows
    
    def find_by_title(self, title: str, exact_match: bool = False) -> List[WindowInfo]:
        """根据窗口标题查找窗口"""
        windows = self.find_all_windows()
        if exact_match:
            return [w for w in windows if w.title == title]
        else:
            return [w for w in windows if title.lower() in w.title.lower()]
    
    def find_by_title_regex(self, pattern: str) -> List[WindowInfo]:
        """使用正则表达式根据标题查找窗口"""
        try:
            windows = self.find_all_windows()
            regex = re.compile(pattern, re.IGNORECASE)
            return [w for w in windows if regex.search(w.title)]
        except re.error as e:
            print(f"正则表达式错误: {e}")
            return []
    
    def find_by_class_name(self, class_name: str, exact_match: bool = False) -> List[WindowInfo]:
        """根据窗口类名查找窗口"""
        windows = self.find_all_windows()
        if exact_match:
            return [w for w in windows if w.class_name == class_name]
        else:
            return [w for w in windows if class_name.lower() in w.class_name.lower()]
    
    def find_by_process_name(self, process_name: str, exact_match: bool = False) -> List[WindowInfo]:
        """根据进程名查找窗口"""
        windows = self.find_all_windows()
        if exact_match:
            return [w for w in windows if w.process_name == process_name]
        else:
            return [w for w in windows if process_name.lower() in w.process_name.lower()]
    
    def find_by_pid(self, pid: int) -> List[WindowInfo]:
        """根据进程ID查找窗口"""
        windows = self.find_all_windows()
        return [w for w in windows if w.pid == pid]
    
    def find_by_custom_filter(self, filter_func: Callable[[WindowInfo], bool]) -> List[WindowInfo]:
        """使用自定义过滤函数查找窗口"""
        windows = self.find_all_windows()
        return [w for w in windows if filter_func(w)]
    
    def find_largest_window(self) -> Optional[WindowInfo]:
        """查找最大的窗口（按面积计算）"""
        windows = self.find_all_windows()
        if not windows:
            return None
        
        return max(windows, key=lambda w: w.width * w.height)
    
    def find_windows_by_size_range(self, min_width: int = 0, min_height: int = 0, 
                                  max_width: int = float('inf'), max_height: int = float('inf')) -> List[WindowInfo]:
        """根据尺寸范围查找窗口"""
        windows = self.find_all_windows()
        return [w for w in windows 
                if min_width <= w.width <= max_width and min_height <= w.height <= max_height]
    
    def find_windows_in_area(self, x: int, y: int, width: int, height: int) -> List[WindowInfo]:
        """查找在指定区域内的窗口"""
        windows = self.find_all_windows()
        return [w for w in windows 
                if (w.x >= x and w.y >= y and 
                    w.x + w.width <= x + width and 
                    w.y + w.height <= y + height)]
    
    def find_visible_windows(self) -> List[WindowInfo]:
        """查找所有可见窗口"""
        return [w for w in self.find_all_windows() if w.is_visible and not w.is_minimized]
    
    def find_minimized_windows(self) -> List[WindowInfo]:
        """查找所有最小化的窗口"""
        return [w for w in self.find_all_windows() if w.is_minimized]
    
    def find_maximized_windows(self) -> List[WindowInfo]:
        """查找所有最大化的窗口"""
        return [w for w in self.find_all_windows() if w.is_maximized]
    
    # ===== 便捷查找方法 =====
    
    def find_browser_windows(self) -> List[WindowInfo]:
        """查找浏览器窗口"""
        browser_processes = ['chrome.exe', 'firefox.exe', 'msedge.exe', 'opera.exe', 'brave.exe']
        windows = []
        for process in browser_processes:
            windows.extend(self.find_by_process_name(process, exact_match=True))
        return windows
    
    def find_office_windows(self) -> List[WindowInfo]:
        """查找Office应用窗口"""
        office_processes = ['winword.exe', 'excel.exe', 'powerpnt.exe', 'outlook.exe']
        windows = []
        for process in office_processes:
            windows.extend(self.find_by_process_name(process, exact_match=True))
        return windows
    
    def find_media_windows(self) -> List[WindowInfo]:
        """查找媒体播放器窗口"""
        media_processes = ['vlc.exe', 'wmplayer.exe', 'potplayer.exe', 'mpc-hc64.exe']
        windows = []
        for process in media_processes:
            windows.extend(self.find_by_process_name(process, exact_match=True))
        return windows
    
    def find_code_editor_windows(self) -> List[WindowInfo]:
        """查找代码编辑器窗口"""
        editor_processes = ['code.exe', 'notepad++.exe', 'sublime_text.exe', 'atom.exe', 'pycharm64.exe']
        windows = []
        for process in editor_processes:
            windows.extend(self.find_by_process_name(process, exact_match=True))
        return windows
    
    def get_window_under_cursor(self) -> Optional[WindowInfo]:
        """获取鼠标光标下的窗口"""
        try:
            import win32api
            x, y = win32api.GetCursorPos()
            hwnd = win32gui.WindowFromPoint((x, y))
            if hwnd:
                # 获取顶级窗口
                while True:
                    parent = win32gui.GetParent(hwnd)
                    if not parent:
                        break
                    hwnd = parent
                return self.window_controller.get_window_info(hwnd)
        except Exception as e:
            print(f"获取光标下窗口失败: {e}")
        return None
    
    def search_windows(self, keyword: str) -> List[WindowInfo]:
        """智能搜索窗口（标题和进程名）"""
        windows = self.find_all_windows()
        keyword_lower = keyword.lower()
        
        results = []
        for window in windows:
            if (keyword_lower in window.title.lower() or 
                keyword_lower in window.process_name.lower()):
                results.append(window)
        
        return results
