"""
通用平台执行器（Fallback实现）
使用pynput提供基本的跨平台功能
"""

import time
from typing import Optional
from pynput import keyboard, mouse
from pynput.keyboard import Key, Controller as KeyboardController
from pynput.mouse import Controller as MouseController, Button

from .os_manager import PlatformExecutor


class GenericExecutor(PlatformExecutor):
    """通用平台执行器（fallback实现）"""
    
    def __init__(self):
        super().__init__()
        self.keyboard_controller = KeyboardController()
        self.mouse_controller = MouseController()
        self.last_execution_time = {}
        self.execution_cooldown = 1.0
    
    def _check_cooldown(self, operation: str) -> bool:
        """检查操作冷却时间"""
        current_time = time.time()
        if operation in self.last_execution_time:
            if current_time - self.last_execution_time[operation] < self.execution_cooldown:
                return False
        self.last_execution_time[operation] = current_time
        return True
    
    def maximize_window(self) -> bool:
        """最大化当前活动窗口（使用快捷键）"""
        if not self._check_cooldown("maximize"):
            return False
        return self._execute_keyboard_shortcut("alt+f10")
    
    def minimize_window(self) -> bool:
        """最小化当前活动窗口（使用快捷键）"""
        if not self._check_cooldown("minimize"):
            return False
        return self._execute_keyboard_shortcut("alt+f9")
    
    def restore_window(self) -> bool:
        """恢复当前活动窗口（使用快捷键）"""
        if not self._check_cooldown("restore"):
            return False
        return self._execute_keyboard_shortcut("alt+f5")
    
    def close_window(self) -> bool:
        """关闭当前活动窗口（使用快捷键）"""
        if not self._check_cooldown("close"):
            return False
        return self._execute_keyboard_shortcut("alt+f4")
    
    def drag_window(self, dx: int, dy: int) -> bool:
        """拖拽当前活动窗口（使用鼠标模拟）"""
        try:
            # 获取当前鼠标位置
            current_pos = self.mouse_controller.position
            
            # 模拟拖拽：按下左键，移动，释放
            self.mouse_controller.press(Button.left)
            time.sleep(0.05)
            
            # 移动鼠标
            new_pos = (current_pos[0] + dx, current_pos[1] + dy)
            self.mouse_controller.position = new_pos
            time.sleep(0.05)
            
            self.mouse_controller.release(Button.left)
            return True
            
        except Exception as e:
            print(f"鼠标拖拽模拟失败: {e}")
            return False
    
    def scroll_up(self) -> bool:
        """向上滚动"""
        try:
            for _ in range(3):
                self.mouse_controller.scroll(0, 3)
                time.sleep(0.05)
            return True
        except Exception as e:
            print(f"向上滚动失败: {e}")
            return False
    
    def scroll_down(self) -> bool:
        """向下滚动"""
        try:
            for _ in range(3):
                self.mouse_controller.scroll(0, -3)
                time.sleep(0.05)
            return True
        except Exception as e:
            print(f"向下滚动失败: {e}")
            return False
    
    def volume_up(self) -> bool:
        """音量增加（使用媒体键）"""
        return self._simulate_media_key("audio_vol_up")
    
    def volume_down(self) -> bool:
        """音量减少（使用媒体键）"""
        return self._simulate_media_key("audio_vol_down")
    
    def volume_mute(self) -> bool:
        """静音切换（使用媒体键）"""
        return self._simulate_media_key("audio_mute")
    
    def media_play_pause(self) -> bool:
        """播放/暂停（使用媒体键）"""
        return self._simulate_media_key("audio_play")
    
    def media_next(self) -> bool:
        """下一曲（使用媒体键）"""
        return self._simulate_media_key("audio_next")
    
    def media_previous(self) -> bool:
        """上一曲（使用媒体键）"""
        return self._simulate_media_key("audio_prev")
    
    def window_switch(self) -> bool:
        """窗口切换（使用Alt+Tab）"""
        return self._execute_keyboard_shortcut("alt+tab")
    
    def _simulate_media_key(self, key_name: str) -> bool:
        """模拟媒体键"""
        try:
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
    
    def _execute_keyboard_shortcut(self, shortcut: str) -> bool:
        """执行键盘快捷键"""
        try:
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
                    key_combination.append(Key.cmd)
                elif len(key_str) == 1:
                    key_combination.append(key_str)
                else:
                    special_keys = {
                        'enter': Key.enter,
                        'space': Key.space,
                        'tab': Key.tab,
                        'escape': Key.esc,
                        'backspace': Key.backspace,
                        'delete': Key.delete,
                        'home': Key.home,
                        'end': Key.end,
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