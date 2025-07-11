"""
macOS平台执行器
整合AppleScript和系统功能，合并原有macos_automator.py的优秀实现
"""

import time
import sys
import applescript
import pyautogui

from executor.Darwin.macos_automator import execute_applescript
from ..os_manager import PlatformExecutor


class MacOSExecutor(PlatformExecutor):
    """macOS平台特定执行器"""

    def __init__(self):
        super().__init__()
        self.last_execution_time = {}
        self.execution_cooldown = 1.0

    def _check_cooldown(self, operation: str) -> bool:
        """检查操作冷却时间"""
        current_time = time.time()
        if operation in self.last_execution_time:
            if (
                current_time - self.last_execution_time[operation]
                < self.execution_cooldown
            ):
                return False
        self.last_execution_time[operation] = current_time
        return True

    def _execute_applescript(self, script: str) -> bool:
        """Executes an AppleScript command."""
        try:
            script_obj = applescript.AppleScript(script)
            result = script_obj.run()
            print(f"AppleScript result: {result}")
            return True
        except applescript.ScriptError as e:
            print(f"Error executing AppleScript: {e}", file=sys.stderr)
            return False

    def maximize_window(self) -> bool:
        """最大化当前活动窗口（全屏）"""
        if not self._check_cooldown("maximize"):
            return False
        script = """
        tell application "System Events"
            key code 0 using {command down, control down}
        end tell
        """
        return self._execute_applescript(script)

    def minimize_window(self) -> bool:
        """最小化当前活动窗口"""
        if not self._check_cooldown("minimize"):
            return False
        script = """
        tell application "System Events" to key code 46 using {command down}
        """
        return self._execute_applescript(script)

    def restore_window(self) -> bool:
        return self.window_switch()

    def window_switch(self) -> bool:
        if not self._check_cooldown("restore"):
            return False
        script = """
        tell application "System Events"
            key code 48 using {command down}
        end tell
        """
        return self._execute_applescript(script)
    
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
        # First, get information about the frontmost application
        app_info_script = """
        tell application "System Events"
            set frontApp to first application process whose frontmost is true
            set frontAppName to name of frontApp
            return frontAppName
        end tell
        """

        try:
            script_obj = applescript.AppleScript(app_info_script)
            app_name = script_obj.run()
            print(f"Current frontmost application: {app_name}")
        except applescript.ScriptError as e:
            print(f"Error getting frontmost application: {e}", file=sys.stderr)
            return False

        # Now try to move the window
        move_script = f"""
        try
            tell application "System Events"
                tell process "{app_name}"
                    if (count of windows) is 0 then 
                        return "No windows found in {app_name}"
                    end if
                    
                    tell first window
                        set windowPosition to position
                        set oldX to item 1 of windowPosition
                        set oldY to item 2 of windowPosition
                        set newX to oldX + {dx}
                        set newY to oldY + {dy}
                        set position to {{newX, newY}}
                        set finalPosition to position
                        return "Window moved from: " & oldX & "," & oldY & " to " & (item 1 of finalPosition) & "," & (item 2 of finalPosition)
                    end tell
                end tell
            end tell
        on error errMsg
            return "Error moving window: " & errMsg
        end try
        """
        return self._execute_applescript(move_script)

    def scroll_up(self) -> bool:
        """向上滚动"""
        try:
            pyautogui.scroll(20)
            return True
        except Exception as e:
            print(f"向上滚动失败: {e}")
            return False

    def scroll_down(self) -> bool:
        """向下滚动"""
        try:
            pyautogui.scroll(-20)
            return True
        except Exception as e:
            print(f"向下滚动失败: {e}")
            return False

    def volume_up(self) -> bool:
        script = """set volume output volume (output volume of (get volume settings) + 10)
        """
        return self._execute_applescript(script)

    def volume_down(self) -> bool:
        script = """set volume output volume (output volume of (get volume settings) - 10)
        """
        return self._execute_applescript(script)

    def volume_mute(self) -> bool:
        script = "set volume with output muted"
        return self._execute_applescript(script)

    def media_play_pause(self) -> bool:
        script = """
        tell application "Music"
            playpause
        end tell
        """
        return self._execute_applescript(script)

    def media_next(self) -> bool:
        script = """
        tell application "Music"
            next track
        end tell
        """
        return self._execute_applescript(script)

    def media_previous(self) -> bool:
        script = """
        tell application "Music"
            previous track
        end tell
        """
        return self._execute_applescript(script)
