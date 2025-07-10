"""
macOS平台执行器
整合AppleScript和系统功能，合并原有macos_automator.py的优秀实现
"""

import time
import subprocess
from typing import Optional
from pynput import keyboard, mouse
from pynput.keyboard import Key, Controller as KeyboardController
from pynput.mouse import Controller as MouseController, Button

from ..os_manager import PlatformExecutor


class MacOSExecutor(PlatformExecutor):
    """macOS平台特定执行器"""
    
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
    
    def _execute_applescript(self, script: str) -> bool:
        """执行AppleScript，改进错误处理"""
        try:
            result = subprocess.run(['osascript', '-e', script], 
                                  capture_output=True, text=True, check=True, timeout=10)
            # 检查是否有返回值表示错误
            if result.stdout and "Error" in result.stdout:
                print(f"AppleScript警告: {result.stdout.strip()}")
                return False
            return True
        except subprocess.CalledProcessError as e:
            print(f"AppleScript执行失败: {e}")
            if e.stderr:
                print(f"错误详情: {e.stderr}")
            return False
        except subprocess.TimeoutExpired:
            print("AppleScript执行超时")
            return False
    
    def maximize_window(self) -> bool:
        """最大化当前活动窗口（全屏）"""
        if not self._check_cooldown("maximize"):
            return False
        # 使用Control+Command+F进入全屏
        script = """
        tell application "System Events"
            key code 3 using {command down, control down}
        end tell
        """
        return self._execute_applescript(script)
    
    def minimize_window(self) -> bool:
        """最小化当前活动窗口"""
        if not self._check_cooldown("minimize"):
            return False
        # 使用Command+M最小化
        script = """
        tell application "System Events"
            key code 46 using {command down}
        end tell
        """
        return self._execute_applescript(script)
    
    def restore_window(self) -> bool:
        """恢复当前活动窗口"""
        if not self._check_cooldown("restore"):
            return False
        # macOS中从最小化恢复通常是点击Dock图标或使用Exposé
        # 这里使用Command+Tab切换来尝试恢复
        return self._execute_keyboard_shortcut("cmd+tab")
    
    def close_window(self) -> bool:
        """关闭当前活动窗口"""
        if not self._check_cooldown("close"):
            return False
        # 使用Command+W关闭窗口
        script = """
        tell application "System Events"
            key code 13 using {command down}
        end tell
        """
        return self._execute_applescript(script)
    
    def drag_window(self, dx: int, dy: int) -> bool:
        """拖拽当前活动窗口 - 改进版本整合macos_automator.py的实现"""
        # 增强的AppleScript，包含更好的错误处理
        script = f'''
        try
            tell application "System Events"
                set frontApp to first application process whose frontmost is true
                set frontAppName to name of frontApp
                tell process frontAppName
                    if (count of windows) is 0 then 
                        return "Error: No windows found in " & frontAppName
                    end if
                    
                    tell first window
                        set windowPosition to position
                        set oldX to item 1 of windowPosition
                        set oldY to item 2 of windowPosition
                        set newX to oldX + {dx}
                        set newY to oldY + {dy}
                        
                        -- 确保窗口不会移到屏幕外
                        if newX < 0 then set newX to 0
                        if newY < 0 then set newY to 0
                        
                        set position to {{newX, newY}}
                        set finalPosition to position
                        return "Success: Window moved from " & oldX & "," & oldY & " to " & (item 1 of finalPosition) & "," & (item 2 of finalPosition)
                    end tell
                end tell
            end tell
        on error errMsg
            return "Error: " & errMsg
        end try
        '''
        
        try:
            result = subprocess.run(['osascript', '-e', script], 
                                  capture_output=True, text=True, check=True, timeout=10)
            
            # 检查AppleScript的返回结果
            if result.stdout:
                output = result.stdout.strip()
                if output.startswith("Success:"):
                    print(f"窗口拖拽成功: {output}")
                    return True
                elif output.startswith("Error:"):
                    print(f"窗口拖拽失败: {output}")
                    return False
            
            return True  # 没有输出但也没有异常，认为成功
            
        except subprocess.CalledProcessError as e:
            print(f"窗口拖拽AppleScript失败: {e}")
            return False
        except subprocess.TimeoutExpired:
            print("窗口拖拽超时")
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
        """音量增加 - 改进版本"""
        script = '''
        try
            set currentVolume to output volume of (get volume settings)
            set newVolume to currentVolume + 10
            if newVolume > 100 then set newVolume to 100
            set volume output volume newVolume
            return "Volume set to " & newVolume
        on error errMsg
            return "Error: " & errMsg
        end try
        '''
        return self._execute_applescript(script)
    
    def volume_down(self) -> bool:
        """音量减少 - 改进版本"""
        script = '''
        try
            set currentVolume to output volume of (get volume settings)
            set newVolume to currentVolume - 10
            if newVolume < 0 then set newVolume to 0
            set volume output volume newVolume
            return "Volume set to " & newVolume
        on error errMsg
            return "Error: " & errMsg
        end try
        '''
        return self._execute_applescript(script)
    
    def volume_mute(self) -> bool:
        """静音切换 - 改进版本"""
        script = '''
        try
            set currentMute to output muted of (get volume settings)
            if currentMute then
                set volume with output unmuted
                return "Volume unmuted"
            else
                set volume with output muted
                return "Volume muted"
            end if
        on error errMsg
            return "Error: " & errMsg
        end try
        '''
        return self._execute_applescript(script)
    
    def media_play_pause(self) -> bool:
        """播放/暂停 - 改进版本，支持多个音乐应用"""
        # 尝试多个常见的音乐应用
        apps_to_try = ["Music", "Spotify", "iTunes"]
        
        for app in apps_to_try:
            script = f'''
            try
                tell application "{app}"
                    if it is running then
                        playpause
                        return "Success with {app}"
                    end if
                end tell
            on error
                return "Failed with {app}"
            end try
            '''
            
            try:
                result = subprocess.run(['osascript', '-e', script], 
                                      capture_output=True, text=True, timeout=5)
                if result.stdout and "Success" in result.stdout:
                    return True
            except:
                continue
        
        # 如果所有应用都失败，尝试媒体键
        return self._simulate_media_key("audio_play")
    
    def media_next(self) -> bool:
        """下一曲"""
        return self._simulate_media_key("audio_next")
    
    def media_previous(self) -> bool:
        """上一曲"""
        return self._simulate_media_key("audio_prev")
    
    def window_switch(self) -> bool:
        """窗口切换"""
        return self._execute_keyboard_shortcut("cmd+tab")
    
    def _simulate_media_key(self, key_name: str) -> bool:
        """模拟媒体键（使用pynput）"""
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