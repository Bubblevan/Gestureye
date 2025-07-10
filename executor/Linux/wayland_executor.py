"""
Linux Wayland平台执行器
使用Wayland协议工具和通用方法实现系统功能
"""

import time
import subprocess
from typing import Optional
from pynput import keyboard, mouse
from pynput.keyboard import Key, Controller as KeyboardController
from pynput.mouse import Controller as MouseController, Button
import pyautogui

from ..os_manager import PlatformExecutor


class WaylandExecutor(PlatformExecutor):
    """Linux Wayland平台特定执行器"""
    
    def __init__(self):
        super().__init__()
        self.keyboard_controller = KeyboardController()
        self.mouse_controller = MouseController()
        self.last_execution_time = {}
        self.execution_cooldown = 1.0
        self._check_dependencies()
    
    def _check_dependencies(self):
        """检查必要的依赖工具是否可用"""
        self.has_swaymsg = self._command_exists('swaymsg')
        self.has_wlr_randr = self._command_exists('wlr-randr')
        self.has_pactl = self._command_exists('pactl')
        self.has_playerctl = self._command_exists('playerctl')
        self.has_wtype = self._command_exists('wtype')
        
        if not self.has_pactl:
            print("警告: pactl未安装，音量控制可能不可用")
        if not self.has_playerctl:
            print("警告: playerctl未安装，媒体控制可能不可用")
        if not (self.has_swaymsg or self.has_wtype):
            print("警告: swaymsg和wtype都未安装，窗口控制功能受限")
    
    def _command_exists(self, command: str) -> bool:
        """检查命令是否存在"""
        try:
            subprocess.run(['which', command], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def _check_cooldown(self, operation: str) -> bool:
        """检查操作冷却时间"""
        current_time = time.time()
        if operation in self.last_execution_time:
            if current_time - self.last_execution_time[operation] < self.execution_cooldown:
                return False
        self.last_execution_time[operation] = current_time
        return True
    
    def _execute_sway_command(self, command: str) -> bool:
        """执行sway命令"""
        if not self.has_swaymsg:
            return False
        try:
            subprocess.call(['swaymsg', command])
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def _get_sink(self) -> Optional[str]:
        """获取默认音频输出设备"""
        if not self.has_pactl:
            return None
        try:
            sink = subprocess.check_output("pactl get-default-sink", shell=True).strip().decode('utf-8')
            return sink
        except subprocess.CalledProcessError:
            return None
    
    def _simulate_keyboard_shortcut(self, shortcut: str) -> bool:
        """模拟键盘快捷键"""
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
                elif key_str == 'super' or key_str == 'win':
                    key_combination.append(Key.cmd)
                elif len(key_str) == 1:
                    key_combination.append(key_str)
                else:
                    special_keys = {
                        'enter': Key.enter, 'space': Key.space, 'tab': Key.tab,
                        'escape': Key.esc, 'backspace': Key.backspace,
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
            if len(key_combination) > 1:
                with self.keyboard_controller.pressed(*key_combination[:-1]):
                    self.keyboard_controller.press(key_combination[-1])
                    time.sleep(0.1)
                    self.keyboard_controller.release(key_combination[-1])
            else:
                self.keyboard_controller.press(key_combination[0])
                time.sleep(0.1)
                self.keyboard_controller.release(key_combination[0])
                
            return True
        except Exception as e:
            print(f"键盘快捷键模拟失败: {e}")
            return False
    
    def maximize_window(self) -> bool:
        """最大化当前活动窗口"""
        if not self._check_cooldown("maximize"):
            return False
        
        # 优先使用sway命令
        if self.has_swaymsg:
            return self._execute_sway_command('fullscreen')
        
        # 回退到键盘快捷键
        return self._simulate_keyboard_shortcut('super+f')
    
    def minimize_window(self) -> bool:
        """最小化当前活动窗口"""
        if not self._check_cooldown("minimize"):
            return False
        
        # 使用键盘快捷键（Wayland中最通用的方法）
        return self._simulate_keyboard_shortcut('super+h')
    
    def restore_window(self) -> bool:
        """恢复当前活动窗口"""
        if not self._check_cooldown("restore"):
            return False
        
        # 在Wayland中，恢复通常通过窗口切换实现
        return self.window_switch()
    
    def close_window(self) -> bool:
        """关闭当前活动窗口"""
        if not self._check_cooldown("close"):
            return False
        
        # 优先使用sway命令
        if self.has_swaymsg:
            return self._execute_sway_command('kill')
        
        # 回退到Alt+F4
        return self._simulate_keyboard_shortcut('alt+f4')
    
    def drag_window(self, dx: int, dy: int) -> bool:
        """拖拽当前活动窗口"""
        # Wayland的窗口拖拽比较复杂，这里使用鼠标模拟
        try:
            # 先尝试激活拖拽模式（如果支持）
            if self.has_swaymsg:
                # 在sway中，可以使用move命令
                self._execute_sway_command(f'move position {dx} {dy}')
                return True
            
            # 回退到鼠标模拟（需要用户先点击标题栏）
            current_pos = self.mouse_controller.position
            self.mouse_controller.press(Button.left)
            time.sleep(0.05)
            
            new_pos = (current_pos[0] + dx, current_pos[1] + dy)
            self.mouse_controller.position = new_pos
            time.sleep(0.05)
            
            self.mouse_controller.release(Button.left)
            return True
            
        except Exception as e:
            print(f"窗口拖拽失败: {e}")
            return False
    
    def scroll_up(self) -> bool:
        """向上滚动"""
        try:
            pyautogui.scroll(3)
            return True
        except Exception as e:
            print(f"向上滚动失败: {e}")
            # 回退到鼠标控制器
            try:
                for _ in range(3):
                    self.mouse_controller.scroll(0, 3)
                    time.sleep(0.05)
                return True
            except Exception as e2:
                print(f"鼠标滚动失败: {e2}")
                return False
    
    def scroll_down(self) -> bool:
        """向下滚动"""
        try:
            pyautogui.scroll(-3)
            return True
        except Exception as e:
            print(f"向下滚动失败: {e}")
            # 回退到鼠标控制器
            try:
                for _ in range(3):
                    self.mouse_controller.scroll(0, -3)
                    time.sleep(0.05)
                return True
            except Exception as e2:
                print(f"鼠标滚动失败: {e2}")
                return False
    
    def volume_up(self) -> bool:
        """音量增加"""
        sink = self._get_sink()
        if sink:
            try:
                subprocess.call(['pactl', 'set-sink-volume', sink, '+10%'])
                return True
            except (subprocess.CalledProcessError, FileNotFoundError):
                pass
        
        # 回退到媒体键
        return self._simulate_media_key('audio_vol_up')
    
    def volume_down(self) -> bool:
        """音量减少"""
        sink = self._get_sink()
        if sink:
            try:
                subprocess.call(['pactl', 'set-sink-volume', sink, '-10%'])
                return True
            except (subprocess.CalledProcessError, FileNotFoundError):
                pass
        
        # 回退到媒体键
        return self._simulate_media_key('audio_vol_down')
    
    def volume_mute(self) -> bool:
        """静音切换"""
        sink = self._get_sink()
        if sink:
            try:
                subprocess.call(['pactl', 'set-sink-mute', sink, 'toggle'])
                return True
            except (subprocess.CalledProcessError, FileNotFoundError):
                pass
        
        # 回退到媒体键
        return self._simulate_media_key('audio_mute')
    
    def media_play_pause(self) -> bool:
        """播放/暂停"""
        if self.has_playerctl:
            try:
                subprocess.call(["playerctl", "play-pause"])
                return True
            except (subprocess.CalledProcessError, FileNotFoundError):
                pass
        
        # 回退到媒体键
        return self._simulate_media_key('audio_play')
    
    def media_next(self) -> bool:
        """下一曲"""
        if self.has_playerctl:
            try:
                subprocess.call(["playerctl", "next"])
                return True
            except (subprocess.CalledProcessError, FileNotFoundError):
                pass
        
        # 回退到媒体键
        return self._simulate_media_key('audio_next')
    
    def media_previous(self) -> bool:
        """上一曲"""
        if self.has_playerctl:
            try:
                subprocess.call(["playerctl", "previous"])
                return True
            except (subprocess.CalledProcessError, FileNotFoundError):
                pass
        
        # 回退到媒体键
        return self._simulate_media_key('audio_prev')
    
    def window_switch(self) -> bool:
        """窗口切换"""
        # 使用Alt+Tab进行窗口切换
        return self._simulate_keyboard_shortcut('alt+tab')
    
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