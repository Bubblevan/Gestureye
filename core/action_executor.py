"""
动作执行器 - 负责执行手势对应的快捷键和系统功能
"""

import time
from typing import Dict, Any, Optional
from pynput import keyboard
from pynput.keyboard import Key, Controller
import win32gui
import win32con
import win32api
import threading

class ActionExecutor:
    """动作执行器"""
    
    def __init__(self):
        self.keyboard_controller = Controller()
        self.last_execution_time = {}  # 防止重复执行
        self.execution_cooldown = 1.0  # 执行冷却时间（秒）
        
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
                elif key_str == 'win':
                    key_combination.append(Key.cmd)  # Windows键
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
                        'page_up': Key.page_up,  # 添加下划线版本
                        'pagedown': Key.page_down,
                        'page_down': Key.page_down,  # 添加下划线版本
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
            hwnd = win32gui.GetForegroundWindow()
            win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
            return True
        except:
            return False
    
    def _minimize_active_window(self) -> bool:
        """最小化当前活动窗口"""
        try:
            hwnd = win32gui.GetForegroundWindow()
            win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
            return True
        except:
            return False
    
    def _restore_active_window(self) -> bool:
        """恢复当前活动窗口"""
        try:
            hwnd = win32gui.GetForegroundWindow()
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            return True
        except:
            return False
    
    def _close_active_window(self) -> bool:
        """关闭当前活动窗口"""
        try:
            hwnd = win32gui.GetForegroundWindow()
            win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
            return True
        except:
            return False
    
    def _volume_up(self) -> bool:
        """音量增加"""
        try:
            win32api.keybd_event(win32con.VK_VOLUME_UP, 0, 0, 0)
            time.sleep(0.1)
            win32api.keybd_event(win32con.VK_VOLUME_UP, 0, win32con.KEYEVENTF_KEYUP, 0)
            return True
        except Exception as e:
            print(f"音量增加失败: {e}")
            return False
    
    def _volume_down(self) -> bool:
        """音量减少"""
        try:
            win32api.keybd_event(win32con.VK_VOLUME_DOWN, 0, 0, 0)
            time.sleep(0.1)
            win32api.keybd_event(win32con.VK_VOLUME_DOWN, 0, win32con.KEYEVENTF_KEYUP, 0)
            return True
        except Exception as e:
            print(f"音量减少失败: {e}")
            return False
    
    def _volume_mute(self) -> bool:
        """静音"""
        try:
            win32api.keybd_event(win32con.VK_VOLUME_MUTE, 0, 0, 0)
            time.sleep(0.1)
            win32api.keybd_event(win32con.VK_VOLUME_MUTE, 0, win32con.KEYEVENTF_KEYUP, 0)
            return True
        except Exception as e:
            print(f"静音切换失败: {e}")
            return False
    
    def _play_pause(self) -> bool:
        """播放/暂停"""
        try:
            win32api.keybd_event(win32con.VK_MEDIA_PLAY_PAUSE, 0, 0, 0)
            time.sleep(0.1)
            win32api.keybd_event(win32con.VK_MEDIA_PLAY_PAUSE, 0, win32con.KEYEVENTF_KEYUP, 0)
            return True
        except Exception as e:
            print(f"播放/暂停失败: {e}")
            return False
    
    def _next_track(self) -> bool:
        """下一曲"""
        try:
            win32api.keybd_event(win32con.VK_MEDIA_NEXT_TRACK, 0, 0, 0)
            time.sleep(0.1)
            win32api.keybd_event(win32con.VK_MEDIA_NEXT_TRACK, 0, win32con.KEYEVENTF_KEYUP, 0)
            return True
        except Exception as e:
            print(f"下一曲失败: {e}")
            return False
    
    def _prev_track(self) -> bool:
        """上一曲"""
        try:
            win32api.keybd_event(win32con.VK_MEDIA_PREV_TRACK, 0, 0, 0)
            time.sleep(0.1)
            win32api.keybd_event(win32con.VK_MEDIA_PREV_TRACK, 0, win32con.KEYEVENTF_KEYUP, 0)
            return True
        except Exception as e:
            print(f"上一曲失败: {e}")
            return False
    
    def set_execution_cooldown(self, cooldown: float):
        """设置执行冷却时间"""
        self.execution_cooldown = cooldown 