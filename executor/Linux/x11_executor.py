"""
Linux X11平台执行器
使用xdotool、kdotool和其他X11工具实现系统功能
"""

import time
import subprocess
from typing import Optional, Tuple
import pyautogui

from ..os_manager import PlatformExecutor


class X11Executor(PlatformExecutor):
    """Linux X11平台特定执行器"""
    
    def __init__(self):
        super().__init__()
        self.last_execution_time = {}
        self.execution_cooldown = 1.0
        self._check_dependencies()
    
    def _check_dependencies(self):
        """检查必要的依赖工具是否可用"""
        self.has_xdotool = self._command_exists('xdotool')
        self.has_kdotool = self._command_exists('kdotool')
        self.has_pactl = self._command_exists('pactl')
        self.has_playerctl = self._command_exists('playerctl')
        
        if not self.has_xdotool:
            print("警告: xdotool未安装，某些功能可能不可用")
        if not self.has_pactl:
            print("警告: pactl未安装，音量控制可能不可用")
        if not self.has_playerctl:
            print("警告: playerctl未安装，媒体控制可能不可用")
    
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
    
    def _execute_kdotool_command(self, command: str, *args) -> Tuple[bool, str]:
        """执行kdotool命令"""
        if not self.has_kdotool:
            print("Failed: kdotool not found")
            return False, "Failed: kdotool not found"
        try:
            result = subprocess.run(['kdotool', 'getactivewindow', command] + list(args), capture_output=True, text=True)
            return True, result.stdout.strip()

        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            return False, f"Failed: {e}"
    
    def _execute_xdotool_command(self, command: str, *args) -> bool:
        """执行xdotool命令"""
        if not self.has_xdotool:
            return False
        try:
            subprocess.call(['xdotool', command] + list(args))
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def _execute_xdotool_key_command(self, command: str, *args) -> bool:
        """执行xdotool键盘命令"""
        if not self.has_xdotool:
            return False
        try:
            subprocess.call(['xdotool', command] + list(args))
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
    
    def maximize_window(self) -> bool:
        """最大化当前活动窗口（使用全屏切换）"""
        if not self._check_cooldown("maximize"):
            return False
        # 使用Super+Page_Up切换全屏
        return self._execute_xdotool_key_command('key', 'Super_L+Page_Up')
    
    def minimize_window(self) -> bool:
        """最小化当前活动窗口"""
        if not self._check_cooldown("minimize"):
            return False
        return self._execute_kdotool_command('windowminimize')[0]
    
    def restore_window(self) -> bool:
        """恢复当前活动窗口"""
        if not self._check_cooldown("restore"):
            return False
        # 在Linux中，恢复通常通过窗口切换实现
        return self.window_switch()
    
    def close_window(self) -> bool:
        """关闭当前活动窗口"""
        if not self._check_cooldown("close"):
            return False
        return self._execute_kdotool_command('windowclose')[0]
    
    def drag_window(self, dx: int, dy: int) -> bool:
        """拖拽当前活动窗口"""
        if self.has_kdotool:
            result = self._execute_kdotool_command('getwindowgeometry')
            cur_x, cur_y = map(float, result[1].splitlines()[1].strip().split()[1].split(','))
            return self._execute_kdotool_command('windowmove', str(int(round(cur_x) + dx)), str(int(round(cur_y) + dy)))[0]
        return False
    
    def scroll_up(self) -> bool:
        """向上滚动"""
        try:
            pyautogui.scroll(3)
            return True
        except Exception as e:
            print(f"向上滚动失败: {e}")
            return False
    
    def scroll_down(self) -> bool:
        """向下滚动"""
        try:
            pyautogui.scroll(-3)
            return True
        except Exception as e:
            print(f"向下滚动失败: {e}")
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
        return False
    
    def volume_down(self) -> bool:
        """音量减少"""
        sink = self._get_sink()
        if sink:
            try:
                subprocess.call(['pactl', 'set-sink-volume', sink, '-10%'])
                return True
            except (subprocess.CalledProcessError, FileNotFoundError):
                pass
        return False
    
    def volume_mute(self) -> bool:
        """静音切换"""
        sink = self._get_sink()
        if sink:
            try:
                subprocess.call(['pactl', 'set-sink-mute', sink, 'toggle'])
                return True
            except (subprocess.CalledProcessError, FileNotFoundError):
                pass
        return False
    
    def media_play_pause(self) -> bool:
        """播放/暂停"""
        if not self.has_playerctl:
            return False
        try:
            subprocess.call(["playerctl", "play-pause"])
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def media_next(self) -> bool:
        """下一曲"""
        if not self.has_playerctl:
            return False
        try:
            subprocess.call(["playerctl", "next"])
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def media_previous(self) -> bool:
        """上一曲"""
        if not self.has_playerctl:
            return False
        try:
            subprocess.call(["playerctl", "previous"])
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def window_switch(self) -> bool:
        """窗口切换"""
        if not self.has_xdotool:
            return False
        try:
            # 使用Alt+Tab进行窗口切换
            self._execute_xdotool_key_command('keydown', 'Alt_L')
            time.sleep(0.1)
            self._execute_xdotool_key_command('key', 'Tab')
            time.sleep(0.1)
            self._execute_xdotool_key_command('keyup', 'Alt_L')
            return True
        except Exception as e:
            print(f"窗口切换失败: {e}")
            return False
    
    def get_active_window_title(self) -> Optional[str]:
        """获取当前活动窗口标题（额外功能）"""
        if self.has_kdotool:
            try:
                result = subprocess.check_output(['kdotool', 'getactivewindowtitle']).strip().decode()
                return result
            except (subprocess.CalledProcessError, FileNotFoundError):
                pass
        
        if self.has_xdotool:
            try:
                window_id = subprocess.check_output(['xdotool', 'getactivewindow']).strip().decode()
                title = subprocess.check_output(['xdotool', 'getwindowname', window_id]).strip().decode()
                return title
            except (subprocess.CalledProcessError, FileNotFoundError):
                pass
        
        return None 