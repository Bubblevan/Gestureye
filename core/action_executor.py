"""
动作执行器 - 负责执行手势对应的快捷键和系统功能
跨平台兼容版本
"""

import time
import platform
from typing import Dict, Any, Optional
from pynput import keyboard, mouse
from pynput.keyboard import Key, Controller as KeyboardController
from pynput.mouse import Controller as MouseController, Button
import subprocess
import threading

# 根据操作系统导入不同的模块
CURRENT_OS = platform.system()

# 仅在Windows上导入pywin32
if CURRENT_OS == "Windows":
    try:
        import win32gui
        import win32con
        import win32api
        HAS_WIN32 = True
    except ImportError:
        HAS_WIN32 = False
        print("警告: 无法导入pywin32，某些Windows特有功能将不可用")
else:
    HAS_WIN32 = False

# Linux上导入X11支持
if CURRENT_OS == "Linux":
    try:
        from Xlib import display
        from Xlib.ext import xtest
        HAS_XLIB = True
    except ImportError:
        HAS_XLIB = False
        print("提示: 未安装python-xlib，某些Linux窗口管理功能将受限")
else:
    HAS_XLIB = False

class ActionExecutor:
    """跨平台动作执行器"""
    
    def __init__(self):
        self.keyboard_controller = KeyboardController()
        self.mouse_controller = MouseController()
        self.last_execution_time = {}  # 防止重复执行
        self.execution_cooldown = 1.0  # 执行冷却时间（秒）
        self.os = CURRENT_OS
        
    def execute_action(self, gesture: str, binding: Dict[str, Any]) -> Optional[bool]:
        """
        执行手势对应的动作
        Returns:
            True: 执行成功
            False: 执行失败
            None: 冷却时间内跳过执行
        """
        if not binding.get("enabled", True):
            return False
            
        # 检查冷却时间
        current_time = time.time()
        if gesture in self.last_execution_time:
            if current_time - self.last_execution_time[gesture] < self.execution_cooldown:
                # 在冷却时间内，返回None表示跳过执行
                return None
                
        action_type = binding.get("action_type")
        action = binding.get("action")
        
        try:
            if action_type == "keyboard_shortcut":
                success = self._execute_keyboard_shortcut(action)
            elif action_type == "system_function":
                success = self._execute_system_function(action)
            elif action_type == "custom_function":
                success = self._execute_custom_function(action)
            else:
                print(f"未知的动作类型: {action_type}")
                return False
                
            if success:
                self.last_execution_time[gesture] = current_time
                print(f"执行手势动作: {gesture} -> {action}")
            else:
                print(f"执行动作失败: {gesture} -> {action}")
                
            return success
            
        except Exception as e:
            print(f"执行动作失败: {gesture} -> {action}, 错误: {e}")
            return False
    
    def _execute_keyboard_shortcut(self, shortcut: str) -> bool:
        """执行键盘快捷键"""
        try:
            # 解析快捷键字符串
            keys = shortcut.lower().split('+')
            key_combination = []
            
            for key_str in keys:
                key_str = key_str.strip()
                if key_str == 'ctrl':
                    key_combination.append(Key.ctrl)
                elif key_str == 'alt':
                    key_combination.append(Key.alt)
                elif key_str == 'shift':
                    key_combination.append(Key.shift)
                elif key_str == 'win' or key_str == 'cmd':
                    if self.os == "Darwin":  # macOS
                        key_combination.append(Key.cmd)
                    else:  # Windows and Linux
                        key_combination.append(Key.cmd)
                elif len(key_str) == 1:
                    key_combination.append(key_str)
                else:
                    # 特殊键
                    special_keys = {
                        'enter': Key.enter,
                        'space': Key.space,
                        'tab': Key.tab,
                        'escape': Key.esc,
                        'backspace': Key.backspace,
                        'delete': Key.delete,
                        'home': Key.home,
                        'end': Key.end,
                        'pageup': Key.page_up,
                        'page_up': Key.page_up,
                        'pagedown': Key.page_down,
                        'page_down': Key.page_down,
                        'up': Key.up,
                        'down': Key.down,
                        'left': Key.left,
                        'right': Key.right,
                        'f1': Key.f1, 'f2': Key.f2, 'f3': Key.f3, 'f4': Key.f4,
                        'f5': Key.f5, 'f6': Key.f6, 'f7': Key.f7, 'f8': Key.f8,
                        'f9': Key.f9, 'f10': Key.f10, 'f11': Key.f11, 'f12': Key.f12,
                    }
                    if key_str in special_keys:
                        key_combination.append(special_keys[key_str])
                    else:
                        print(f"未知的键: {key_str}")
                        return False
            
            # 执行快捷键
            with self.keyboard_controller.pressed(*key_combination[:-1]):
                self.keyboard_controller.press(key_combination[-1])
                time.sleep(0.1)
                self.keyboard_controller.release(key_combination[-1])
                
            return True
            
        except Exception as e:
            print(f"执行键盘快捷键失败: {shortcut}, 错误: {e}")
            return False
    
    def _execute_system_function(self, function: str) -> bool:
        """执行系统功能"""
        try:
            if function == "window_maximize":
                return self._maximize_active_window()
            elif function == "window_minimize":
                return self._minimize_active_window()
            elif function == "window_restore":
                return self._restore_active_window()
            elif function == "window_close":
                return self._close_active_window()
            elif function == "volume_up":
                return self._volume_up()
            elif function == "volume_down":
                return self._volume_down()
            elif function == "volume_mute":
                return self._volume_mute()
            elif function == "play_pause":
                return self._play_pause()            
            elif function == "next_track":
                return self._next_track()
            elif function == "prev_track":
                return self._prev_track()
            elif function == "window_drag":
                return self._window_drag()
            elif function == "window_switch":
                return self._window_switch()
            elif function == "window_scroll_up":
                return self._window_scroll_up()
            elif function == "window_scroll_down":
                return self._window_scroll_down()
            else:
                print(f"未知的系统功能: {function}")
                return False
                
        except Exception as e:
            print(f"执行系统功能失败: {function}, 错误: {e}")
            return False
    
    def _execute_custom_function(self, function: str) -> bool:
        """执行自定义功能"""
        # 这里可以添加自定义的功能
        print(f"执行自定义功能: {function}")
        return True
    
    def _maximize_active_window(self) -> bool:
        """最大化当前活动窗口"""
        try:
            if self.os == "Windows" and HAS_WIN32:
                hwnd = win32gui.GetForegroundWindow()
                win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
                return True
            elif self.os == "Darwin":  # macOS
                # 使用AppleScript
                script = 'tell application "System Events" to set frontmost of first process whose frontmost is true to true'
                subprocess.run(['osascript', '-e', script], capture_output=True)
                return True
            elif self.os == "Linux":
                # 使用wmctrl或通过快捷键
                try:
                    subprocess.run(['wmctrl', '-r', ':ACTIVE:', '-b', 'add,maximized_vert,maximized_horz'], 
                                 capture_output=True, check=True)
                    return True
                except (subprocess.CalledProcessError, FileNotFoundError):
                    # 回退到快捷键方式
                    return self._execute_keyboard_shortcut("alt+f10")
            else:
                return self._execute_keyboard_shortcut("alt+f10")  # 通用快捷键
        except Exception as e:
            print(f"窗口最大化失败: {e}")
            return False
    
    def _minimize_active_window(self) -> bool:
        """最小化当前活动窗口"""
        try:
            if self.os == "Windows" and HAS_WIN32:
                hwnd = win32gui.GetForegroundWindow()
                win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
                return True
            elif self.os == "Darwin":  # macOS
                return self._execute_keyboard_shortcut("cmd+m")
            elif self.os == "Linux":
                try:
                    subprocess.run(['wmctrl', '-r', ':ACTIVE:', '-b', 'add,hidden'], 
                                 capture_output=True, check=True)
                    return True
                except (subprocess.CalledProcessError, FileNotFoundError):
                    return self._execute_keyboard_shortcut("alt+f9")
            else:
                return self._execute_keyboard_shortcut("alt+f9")
        except Exception as e:
            print(f"窗口最小化失败: {e}")
            return False
    
    def _restore_active_window(self) -> bool:
        """恢复当前活动窗口"""
        try:
            if self.os == "Windows" and HAS_WIN32:
                hwnd = win32gui.GetForegroundWindow()
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                return True
            elif self.os == "Darwin":  # macOS
                # macOS没有直接的恢复命令，使用系统快捷键
                return self._execute_keyboard_shortcut("cmd+shift+m")
            elif self.os == "Linux":
                try:
                    subprocess.run(['wmctrl', '-r', ':ACTIVE:', '-b', 'remove,maximized_vert,maximized_horz'], 
                                 capture_output=True, check=True)
                    return True
                except (subprocess.CalledProcessError, FileNotFoundError):
                    return self._execute_keyboard_shortcut("alt+f5")
            else:
                return self._execute_keyboard_shortcut("alt+f5")
        except Exception as e:
            print(f"窗口恢复失败: {e}")
            return False
    
    def _close_active_window(self) -> bool:
        """关闭当前活动窗口"""
        try:
            if self.os == "Windows":
                if HAS_WIN32:
                    hwnd = win32gui.GetForegroundWindow()
                    win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
                    return True
                else:
                    return self._execute_keyboard_shortcut("alt+f4")
            elif self.os == "Darwin":  # macOS
                return self._execute_keyboard_shortcut("cmd+w")
            else:  # Linux
                return self._execute_keyboard_shortcut("alt+f4")
        except Exception as e:
            print(f"窗口关闭失败: {e}")
            return False
    
    def _volume_up(self) -> bool:
        """音量增加"""
        try:
            if self.os == "Windows" and HAS_WIN32:
                win32api.keybd_event(win32con.VK_VOLUME_UP, 0, 0, 0)
                time.sleep(0.1)
                win32api.keybd_event(win32con.VK_VOLUME_UP, 0, win32con.KEYEVENTF_KEYUP, 0)
                return True
            elif self.os == "Darwin":  # macOS
                # 使用AppleScript
                script = 'set volume output volume (output volume of (get volume settings) + 10)'
                subprocess.run(['osascript', '-e', script], capture_output=True)
                return True
            elif self.os == "Linux":
                # 尝试多种Linux音量控制方式
                commands = [
                    ['amixer', 'sset', 'Master', '5%+'],
                    ['pactl', 'set-sink-volume', '@DEFAULT_SINK@', '+5%'],
                    ['pulseaudio-ctl', 'up']
                ]
                for cmd in commands:
                    try:
                        subprocess.run(cmd, capture_output=True, check=True)
                        return True
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        continue
                # 如果都失败，尝试媒体键
                return self._simulate_media_key("audio_vol_up")
            return False
        except Exception as e:
            print(f"音量增加失败: {e}")
            return False
    
    def _volume_down(self) -> bool:
        """音量减少"""
        try:
            if self.os == "Windows" and HAS_WIN32:
                win32api.keybd_event(win32con.VK_VOLUME_DOWN, 0, 0, 0)
                time.sleep(0.1)
                win32api.keybd_event(win32con.VK_VOLUME_DOWN, 0, win32con.KEYEVENTF_KEYUP, 0)
                return True
            elif self.os == "Darwin":  # macOS
                script = 'set volume output volume (output volume of (get volume settings) - 10)'
                subprocess.run(['osascript', '-e', script], capture_output=True)
                return True
            elif self.os == "Linux":
                commands = [
                    ['amixer', 'sset', 'Master', '5%-'],
                    ['pactl', 'set-sink-volume', '@DEFAULT_SINK@', '-5%'],
                    ['pulseaudio-ctl', 'down']
                ]
                for cmd in commands:
                    try:
                        subprocess.run(cmd, capture_output=True, check=True)
                        return True
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        continue
                return self._simulate_media_key("audio_vol_down")
            return False
        except Exception as e:
            print(f"音量减少失败: {e}")
            return False
    
    def _volume_mute(self) -> bool:
        """静音"""
        try:
            if self.os == "Windows" and HAS_WIN32:
                win32api.keybd_event(win32con.VK_VOLUME_MUTE, 0, 0, 0)
                time.sleep(0.1)
                win32api.keybd_event(win32con.VK_VOLUME_MUTE, 0, win32con.KEYEVENTF_KEYUP, 0)
                return True
            elif self.os == "Darwin":  # macOS
                script = 'set volume with output muted'
                subprocess.run(['osascript', '-e', script], capture_output=True)
                return True
            elif self.os == "Linux":
                commands = [
                    ['amixer', 'sset', 'Master', 'toggle'],
                    ['pactl', 'set-sink-mute', '@DEFAULT_SINK@', 'toggle'],
                    ['pulseaudio-ctl', 'mute']
                ]
                for cmd in commands:
                    try:
                        subprocess.run(cmd, capture_output=True, check=True)
                        return True
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        continue
                return self._simulate_media_key("audio_mute")
            return False
        except Exception as e:
            print(f"静音切换失败: {e}")
            return False
    
    def _play_pause(self) -> bool:
        """播放/暂停"""
        try:
            if self.os == "Windows" and HAS_WIN32:
                win32api.keybd_event(win32con.VK_MEDIA_PLAY_PAUSE, 0, 0, 0)
                time.sleep(0.1)
                win32api.keybd_event(win32con.VK_MEDIA_PLAY_PAUSE, 0, win32con.KEYEVENTF_KEYUP, 0)
                return True
            else:
                return self._simulate_media_key("audio_play")
        except Exception as e:
            print(f"播放/暂停失败: {e}")
            return False
    
    def _next_track(self) -> bool:
        """下一曲"""
        try:
            if self.os == "Windows" and HAS_WIN32:
                win32api.keybd_event(win32con.VK_MEDIA_NEXT_TRACK, 0, 0, 0)
                time.sleep(0.1)
                win32api.keybd_event(win32con.VK_MEDIA_NEXT_TRACK, 0, win32con.KEYEVENTF_KEYUP, 0)
                return True
            else:
                return self._simulate_media_key("audio_next")
        except Exception as e:
            print(f"下一曲失败: {e}")
            return False
    
    def _prev_track(self) -> bool:
        """上一曲"""
        try:
            if self.os == "Windows" and HAS_WIN32:
                win32api.keybd_event(win32con.VK_MEDIA_PREV_TRACK, 0, 0, 0)
                time.sleep(0.1)
                win32api.keybd_event(win32con.VK_MEDIA_PREV_TRACK, 0, win32con.KEYEVENTF_KEYUP, 0)
                return True
            else:
                return self._simulate_media_key("audio_prev")
        except Exception as e:
            print(f"上一曲失败: {e}")
            return False

    def _simulate_media_key(self, key_name: str) -> bool:
        """模拟媒体键（跨平台）"""
        try:
            # 使用pynput的媒体键支持
            media_keys = {
                "audio_play": Key.media_play_pause,
                "audio_next": Key.media_next,
                "audio_prev": Key.media_previous,
                "audio_vol_up": Key.media_volume_up,
                "audio_vol_down": Key.media_volume_down,
                "audio_mute": Key.media_volume_mute,
            }
            
            if key_name in media_keys:
                self.keyboard_controller.press(media_keys[key_name])
                time.sleep(0.1)
                self.keyboard_controller.release(media_keys[key_name])
                return True
            return False
        except Exception as e:
            print(f"媒体键模拟失败: {e}")
            return False

    def set_execution_cooldown(self, cooldown: float):
        """设置执行冷却时间"""
        self.execution_cooldown = cooldown

    def _window_drag(self) -> bool:
        """窗口拖拽模拟"""
        # TODO: 实现真正的窗口拖拽逻辑
        # 目前的实现与 window_switch 重复，暂时留空
        print("窗口拖拽功能尚未实现")
        return False

    def _window_switch(self) -> bool:
        """窗口切换"""
        try:
            if self.os == "Darwin":  # macOS
                return self._execute_keyboard_shortcut("cmd+tab")
            else:  # Windows and Linux
                return self._execute_keyboard_shortcut("alt+tab")
        except Exception as e:
            print(f"窗口切换失败: {e}")
            return False
    
    def _window_scroll_up(self) -> bool:
        """向上滚动"""
        try:
            if self.os == "Windows" and HAS_WIN32:
                # 使用Windows API
                for _ in range(3):
                    win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, 120, 0)
                    time.sleep(0.05)
                return True
            else:
                # 使用pynput进行跨平台滚轮控制
                for _ in range(3):
                    self.mouse_controller.scroll(0, 3)  # dx=0, dy=3 向上滚动
                    time.sleep(0.05)
                return True
        except Exception as e:
            print(f"向上滚动失败: {e}")
            return False
    
    def _window_scroll_down(self) -> bool:
        """向下滚动"""
        try:
            if self.os == "Windows" and HAS_WIN32:
                # 使用Windows API
                for _ in range(3):
                    win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, -120, 0)
                    time.sleep(0.05)
                return True
            else:
                # 使用pynput进行跨平台滚轮控制
                for _ in range(3):
                    self.mouse_controller.scroll(0, -3)  # dx=0, dy=-3 向下滚动
                    time.sleep(0.05)
                return True
        except Exception as e:
            print(f"向下滚动失败: {e}")
            return False