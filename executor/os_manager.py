"""
跨平台操作系统管理器
自动检测操作系统和显示服务器，提供统一的平台特定功能接口
"""

import platform
import os
import subprocess
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Type
from enum import Enum


class OSType(Enum):
    """操作系统类型枚举"""
    WINDOWS = "Windows"
    MACOS = "Darwin"
    LINUX = "Linux"
    UNKNOWN = "Unknown"


class DisplayServer(Enum):
    """Linux显示服务器类型枚举"""
    X11 = "x11"
    WAYLAND = "wayland"
    UNKNOWN = "unknown"


class PlatformExecutor(ABC):
    """平台特定执行器抽象基类"""
    
    def __init__(self):
        self.os_type = self._detect_os()
        self.display_server = self._detect_display_server() if self.os_type == OSType.LINUX else None
    
    @abstractmethod
    def maximize_window(self) -> bool:
        """最大化当前活动窗口"""
        pass
    
    @abstractmethod
    def minimize_window(self) -> bool:
        """最小化当前活动窗口"""
        pass
    
    @abstractmethod
    def restore_window(self) -> bool:
        """恢复当前活动窗口"""
        pass
    
    @abstractmethod
    def close_window(self) -> bool:
        """关闭当前活动窗口"""
        pass
    
    @abstractmethod
    def drag_window(self, dx: int, dy: int) -> bool:
        """拖拽当前活动窗口"""
        pass
    
    @abstractmethod
    def scroll_up(self) -> bool:
        """向上滚动"""
        pass
    
    @abstractmethod
    def scroll_down(self) -> bool:
        """向下滚动"""
        pass
    
    @abstractmethod
    def volume_up(self) -> bool:
        """音量增加"""
        pass
    
    @abstractmethod
    def volume_down(self) -> bool:
        """音量减少"""
        pass
    
    @abstractmethod
    def volume_mute(self) -> bool:
        """静音切换"""
        pass
    
    @abstractmethod
    def media_play_pause(self) -> bool:
        """播放/暂停"""
        pass
    
    @abstractmethod
    def media_next(self) -> bool:
        """下一曲"""
        pass
    
    @abstractmethod
    def media_previous(self) -> bool:
        """上一曲"""
        pass
    
    @abstractmethod
    def window_switch(self) -> bool:
        """窗口切换"""
        pass
    
    def _detect_os(self) -> OSType:
        """检测操作系统类型"""
        system = platform.system()
        if system == "Windows":
            return OSType.WINDOWS
        elif system == "Darwin":
            return OSType.MACOS
        elif system == "Linux":
            return OSType.LINUX
        else:
            return OSType.UNKNOWN
    
    def _detect_display_server(self) -> DisplayServer:
        """检测Linux显示服务器类型"""
        if self.os_type != OSType.LINUX:
            return DisplayServer.UNKNOWN
        
        # 检查环境变量
        wayland_display = os.environ.get('WAYLAND_DISPLAY')
        x11_display = os.environ.get('DISPLAY')
        xdg_session_type = os.environ.get('XDG_SESSION_TYPE', '').lower()
        
        # 优先检查XDG_SESSION_TYPE
        if xdg_session_type == 'wayland':
            return DisplayServer.WAYLAND
        elif xdg_session_type == 'x11':
            return DisplayServer.X11
        
        # 检查显示服务器环境变量
        if wayland_display and not x11_display:
            return DisplayServer.WAYLAND
        elif x11_display and not wayland_display:
            return DisplayServer.X11
        elif wayland_display and x11_display:
            # 两个都有，优先Wayland（新的默认）
            return DisplayServer.WAYLAND
        
        # 尝试检测运行中的显示服务器
        try:
            # 检查是否有Wayland compositor在运行
            result = subprocess.run(['pgrep', '-f', 'wayland|weston|sway|gnome-shell'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return DisplayServer.WAYLAND
            
            # 检查是否有X11服务器在运行
            result = subprocess.run(['pgrep', '-f', 'Xorg|X'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return DisplayServer.X11
        except FileNotFoundError:
            pass
        
        return DisplayServer.UNKNOWN


class OSManager:
    """操作系统管理器 - 统一接口"""
    
    def __init__(self):
        self.os_type = self._detect_os()
        self.display_server = self._detect_display_server() if self.os_type == OSType.LINUX else None
        self.executor: Optional[PlatformExecutor] = None
        self._initialize_executor()
    
    def _detect_os(self) -> OSType:
        """检测操作系统类型"""
        system = platform.system()
        if system == "Windows":
            return OSType.WINDOWS
        elif system == "Darwin":
            return OSType.MACOS
        elif system == "Linux":
            return OSType.LINUX
        else:
            return OSType.UNKNOWN
    
    def _detect_display_server(self) -> DisplayServer:
        """检测Linux显示服务器类型"""
        if self.os_type != OSType.LINUX:
            return DisplayServer.UNKNOWN
        
        # 检查环境变量
        wayland_display = os.environ.get('WAYLAND_DISPLAY')
        x11_display = os.environ.get('DISPLAY')
        xdg_session_type = os.environ.get('XDG_SESSION_TYPE', '').lower()
        
        print(f"检测显示服务器 - XDG_SESSION_TYPE: {xdg_session_type}, "
              f"WAYLAND_DISPLAY: {wayland_display}, DISPLAY: {x11_display}")
        
        # 优先检查XDG_SESSION_TYPE
        if xdg_session_type == 'wayland':
            return DisplayServer.WAYLAND
        elif xdg_session_type == 'x11':
            return DisplayServer.X11
        
        # 检查显示服务器环境变量
        if wayland_display and not x11_display:
            return DisplayServer.WAYLAND
        elif x11_display and not wayland_display:
            return DisplayServer.X11
        elif wayland_display and x11_display:
            # 两个都有，优先Wayland（新的默认）
            return DisplayServer.WAYLAND
        
        # 尝试检测运行中的显示服务器
        try:
            # 检查是否有Wayland compositor在运行
            result = subprocess.run(['pgrep', '-f', 'wayland|weston|sway|gnome-shell'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return DisplayServer.WAYLAND
            
            # 检查是否有X11服务器在运行
            result = subprocess.run(['pgrep', '-f', 'Xorg|X'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return DisplayServer.X11
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        
        return DisplayServer.UNKNOWN
    
    def _initialize_executor(self):
        """初始化平台特定的执行器"""
        try:
            if self.os_type == OSType.WINDOWS:
                from .Windows.windows_executor import WindowsExecutor
                self.executor = WindowsExecutor()
            elif self.os_type == OSType.MACOS:
                from .Darwin.macos_executor import MacOSExecutor
                self.executor = MacOSExecutor()
            elif self.os_type == OSType.LINUX:
                if self.display_server == DisplayServer.WAYLAND:
                    from .Linux.wayland_executor import WaylandExecutor
                    self.executor = WaylandExecutor()
                else:  # X11 或 Unknown 默认使用 X11
                    from .Linux.x11_executor import X11Executor
                    self.executor = X11Executor()
            else:
                print(f"不支持的操作系统: {self.os_type}")
                # 使用通用fallback实现
                from .generic_executor import GenericExecutor
                self.executor = GenericExecutor()
        except ImportError as e:
            print(f"无法导入平台特定执行器: {e}")
            print("使用通用fallback实现")
            from .generic_executor import GenericExecutor
            self.executor = GenericExecutor()
    
    def get_system_info(self) -> Dict[str, Any]:
        """获取系统信息"""
        info = {
            "os_type": self.os_type.value,
            "platform": platform.platform(),
            "architecture": platform.architecture(),
            "python_version": platform.python_version(),
        }
        
        if self.os_type == OSType.LINUX:
            info["display_server"] = self.display_server.value if self.display_server else "unknown"
            info["desktop_environment"] = os.environ.get('XDG_CURRENT_DESKTOP', 'unknown')
        
        return info
    
    def is_available(self) -> bool:
        """检查当前平台是否可用"""
        return self.executor is not None
    
    # 委托方法到平台特定执行器
    def maximize_window(self) -> bool:
        """最大化当前活动窗口"""
        return self.executor.maximize_window() if self.executor else False
    
    def minimize_window(self) -> bool:
        """最小化当前活动窗口"""
        return self.executor.minimize_window() if self.executor else False
    
    def restore_window(self) -> bool:
        """恢复当前活动窗口"""
        return self.executor.restore_window() if self.executor else False
    
    def close_window(self) -> bool:
        """关闭当前活动窗口"""
        return self.executor.close_window() if self.executor else False
    
    def drag_window(self, dx: int, dy: int) -> bool:
        """拖拽当前活动窗口"""
        return self.executor.drag_window(dx, dy) if self.executor else False
    
    def scroll_up(self) -> bool:
        """向上滚动"""
        return self.executor.scroll_up() if self.executor else False
    
    def scroll_down(self) -> bool:
        """向下滚动"""
        return self.executor.scroll_down() if self.executor else False
    
    def volume_up(self) -> bool:
        """音量增加"""
        return self.executor.volume_up() if self.executor else False
    
    def volume_down(self) -> bool:
        """音量减少"""
        return self.executor.volume_down() if self.executor else False
    
    def volume_mute(self) -> bool:
        """静音切换"""
        return self.executor.volume_mute() if self.executor else False
    
    def media_play_pause(self) -> bool:
        """播放/暂停"""
        return self.executor.media_play_pause() if self.executor else False
    
    def media_next(self) -> bool:
        """下一曲"""
        return self.executor.media_next() if self.executor else False
    
    def media_previous(self) -> bool:
        """上一曲"""
        return self.executor.media_previous() if self.executor else False
    
    def window_switch(self) -> bool:
        """窗口切换"""
        return self.executor.window_switch() if self.executor else False
