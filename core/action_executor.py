#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MacOS 动作执行器 - 负责执行手势对应的快捷键和系统功能
专为 macOS 优化的版本
"""

import time
import subprocess
import sys
from typing import Dict, Any, Optional, Union, cast

# 导入必要的库
try:
    import applescript
except ImportError:
    print("Error: 'py-applescript' library not found.")
    print("Please install it using: pip install py-applescript")
    sys.exit(1)

try:
    import pyautogui
except ImportError:
    print("Error: 'pyautogui' library not found.")
    print("Please install it using: pip install pyautogui")
    sys.exit(1)

# 设置键盘/鼠标控制器常量
KEY_ALT = "alt"
KEY_CMD = "cmd"
KEY_CTRL = "ctrl"
KEY_SHIFT = "shift"
KEY_ENTER = "enter"
KEY_SPACE = "space"
KEY_TAB = "tab"
KEY_ESC = "esc"
KEY_BACKSPACE = "backspace"
KEY_DELETE = "delete"
KEY_HOME = "home"
KEY_END = "end"
KEY_PAGEUP = "page_up"
KEY_PAGEDOWN = "page_down"
KEY_UP = "up"
KEY_DOWN = "down"
KEY_LEFT = "left"
KEY_RIGHT = "right"
KEY_F1 = "f1"
KEY_F2 = "f2"
KEY_F3 = "f3"
KEY_F4 = "f4"
KEY_F5 = "f5"
KEY_F6 = "f6"
KEY_F7 = "f7"
KEY_F8 = "f8"
KEY_F9 = "f9"
KEY_F10 = "f10"
KEY_F11 = "f11"
KEY_F12 = "f12"

BUTTON_LEFT = "left"
BUTTON_RIGHT = "right"
BUTTON_MIDDLE = "middle"


# 定义自己的键枚举类
class Key:
    alt = KEY_ALT
    cmd = KEY_CMD
    ctrl = KEY_CTRL
    shift = KEY_SHIFT
    enter = KEY_ENTER
    space = KEY_SPACE
    tab = KEY_TAB
    esc = KEY_ESC
    backspace = KEY_BACKSPACE
    delete = KEY_DELETE
    home = KEY_HOME
    end = KEY_END
    page_up = KEY_PAGEUP
    page_down = KEY_PAGEDOWN
    up = KEY_UP
    down = KEY_DOWN
    left = KEY_LEFT
    right = KEY_RIGHT
    f1 = KEY_F1
    f2 = KEY_F2
    f3 = KEY_F3
    f4 = KEY_F4
    f5 = KEY_F5
    f6 = KEY_F6
    f7 = KEY_F7
    f8 = KEY_F8
    f9 = KEY_F9
    f10 = KEY_F10
    f11 = KEY_F11
    f12 = KEY_F12


# 定义自己的按钮类
class Button:
    left = BUTTON_LEFT
    right = BUTTON_RIGHT
    middle = BUTTON_MIDDLE


# 尝试导入pynput，如果可用则使用它，否则使用我们的实现
try:
    import pynput
    import pynput.keyboard
    import pynput.mouse
    HAS_PYNPUT = True
    # 注意：不直接导入类以避免名称冲突
except ImportError:
    print("Warning: 'pynput' library not found.")
    print("Some keyboard and mouse simulation features will be limited.")
    print("Consider installing it using: pip install pynput")
    HAS_PYNPUT = False


# 键盘控制器类
class KeyboardController:
    def __init__(self):
        if HAS_PYNPUT:
            self._controller = pynput.keyboard.Controller()
        else:
            self._controller = None

    def press(self, key):
        if HAS_PYNPUT:
            # 转换我们的键到pynput的键
            pynput_key = self._convert_to_pynput_key(key)
            self._controller.press(pynput_key)
        else:
            print(f"模拟按键: {key} [仅占位，没有实际效果]")

    def release(self, key):
        if HAS_PYNPUT:
            pynput_key = self._convert_to_pynput_key(key)
            self._controller.release(pynput_key)
        else:
            print(f"释放按键: {key} [仅占位，没有实际效果]")

    def _convert_to_pynput_key(self, key):
        """将我们的键转换为pynput的键"""
        if HAS_PYNPUT:
            if key == KEY_ALT:
                return pynput.keyboard.Key.alt
            elif key == KEY_CMD:
                return pynput.keyboard.Key.cmd
            elif key == KEY_CTRL:
                return pynput.keyboard.Key.ctrl
            elif key == KEY_SHIFT:
                return pynput.keyboard.Key.shift
            # ... 可以继续添加其他键的映射
            elif len(str(key)) == 1:  # 单个字符
                return key
            else:
                # 尝试查找对应的特殊键
                try:
                    return getattr(pynput.keyboard.Key, key)
                except AttributeError:
                    print(f"警告: 无法映射键 {key} 到pynput")
                    return key
        return key

    def pressed(self, *keys):
        if HAS_PYNPUT:
            # 转换所有键
            pynput_keys = [self._convert_to_pynput_key(k) for k in keys]
            return self._controller.pressed(*pynput_keys)
        else:

            class KeyContext:
                def __enter__(self):
                    for k in keys:
                        print(f"模拟按住: {k} [仅占位，没有实际效果]")
                    return self

                def __exit__(self, *args):
                    for k in keys:
                        print(f"释放按键: {k} [仅占位，没有实际效果]")

            return KeyContext()


# 鼠标控制器类
class MouseController:
    def __init__(self):
        if HAS_PYNPUT:
            self._controller = pynput.mouse.Controller()
        else:
            self._controller = None
            self.position = (0, 0)

    @property
    def position(self):
        if HAS_PYNPUT:
            return self._controller.position
        return (0, 0)

    @position.setter
    def position(self, pos):
        if HAS_PYNPUT:
            self._controller.position = pos

    def move(self, dx, dy):
        if HAS_PYNPUT:
            self._controller.move(dx, dy)
        else:
            print(f"移动鼠标: dx={dx}, dy={dy} [仅占位，没有实际效果]")

    def press(self, button):
        if HAS_PYNPUT:
            pynput_button = self._convert_to_pynput_button(button)
            self._controller.press(pynput_button)
        else:
            print(f"按下鼠标按钮: {button} [仅占位，没有实际效果]")

    def release(self, button):
        if HAS_PYNPUT:
            pynput_button = self._convert_to_pynput_button(button)
            self._controller.release(pynput_button)
        else:
            print(f"释放鼠标按钮: {button} [仅占位，没有实际效果]")

    def _convert_to_pynput_button(self, button):
        """将我们的按钮转换为pynput的按钮"""
        if HAS_PYNPUT:
            if button == BUTTON_LEFT:
                return pynput.mouse.Button.left
            elif button == BUTTON_RIGHT:
                return pynput.mouse.Button.right
            elif button == BUTTON_MIDDLE:
                return pynput.mouse.Button.middle
            else:
                # 尝试查找对应的按钮
                try:
                    return getattr(pynput.mouse.Button, button)
                except AttributeError:
                    print(f"警告: 无法映射按钮 {button} 到pynput")
                    return button
        return button


class MacActionExecutor:
    """macOS 特定的动作执行器"""

    def __init__(self):
        self.keyboard_controller = KeyboardController()
        self.mouse_controller = MouseController()
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
            if (
                current_time - self.last_execution_time[gesture]
                < self.execution_cooldown
            ):
                # 在冷却时间内，返回None表示跳过执行
                return None

        action_type = binding.get("action_type")
        action = binding.get("action")

        try:
            if action_type == "keyboard_shortcut" and action is not None:
                success = self._execute_keyboard_shortcut(str(action))
            elif action_type == "system_function" and action is not None:
                success = self._execute_system_function(str(action))
            elif action_type == "custom_function" and action is not None:
                success = self._execute_custom_function(str(action))
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
            keys = shortcut.lower().split("+")
            key_combination = []

            for key_str in keys:
                key_str = key_str.strip()
                if key_str == "ctrl":
                    key_combination.append(Key.ctrl)
                elif key_str == "alt" or key_str == "option":
                    key_combination.append(Key.alt)
                elif key_str == "shift":
                    key_combination.append(Key.shift)
                elif key_str == "cmd" or key_str == "command":
                    key_combination.append(Key.cmd)
                elif len(key_str) == 1:
                    key_combination.append(key_str)
                else:
                    # 特殊键
                    special_keys = {
                        "enter": Key.enter,
                        "return": Key.enter,
                        "space": Key.space,
                        "tab": Key.tab,
                        "escape": Key.esc,
                        "esc": Key.esc,
                        "backspace": Key.backspace,
                        "delete": Key.delete,
                        "home": Key.home,
                        "end": Key.end,
                        "pageup": Key.page_up,
                        "page_up": Key.page_up,
                        "pagedown": Key.page_down,
                        "page_down": Key.page_down,
                        "up": Key.up,
                        "down": Key.down,
                        "left": Key.left,
                        "right": Key.right,
                        "f1": Key.f1,
                        "f2": Key.f2,
                        "f3": Key.f3,
                        "f4": Key.f4,
                        "f5": Key.f5,
                        "f6": Key.f6,
                        "f7": Key.f7,
                        "f8": Key.f8,
                        "f9": Key.f9,
                        "f10": Key.f10,
                        "f11": Key.f11,
                        "f12": Key.f12,
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
            elif function == "window_fullscreen":
                return self._toggle_fullscreen()
            elif function == "window_restore":
                return self._restore_active_window()
            elif function == "window_close":
                return self._close_active_window()
            elif function == "window_move":
                return self._move_window_relative(50, 50)  # 默认移动值
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

    def _toggle_fullscreen(self) -> bool:
        """切换全屏状态"""
        print("切换全屏状态...")
        script = """
        tell application "System Events"
            key code 0 using {command down, control down}
        end tell
        """
        try:
            script_obj = applescript.AppleScript(script)
            result = script_obj.run()
            print(f"AppleScript 结果: {result}")
            return True
        except applescript.ScriptError as e:
            print(f"切换全屏状态失败: {e}")
            return False

    def _maximize_active_window(self) -> bool:
        """最大化当前活动窗口"""
        print("最大化当前窗口...")
        # macOS绿色按钮在默认情况下是全屏，而不是最大化
        # 使用AppleScript模拟点击缩放按钮
        script = """
        tell application "System Events"
            set frontApp to first application process whose frontmost is true
            tell frontApp
                tell window 1
                    set {xPosition, yPosition} to position
                    set {xSize, ySize} to size
                    -- 尝试使用"缩放"选项（模拟点击绿色按钮的选项菜单）
                    click button 3 of window 1
                end tell
            end tell
        end tell
        """

        try:
            # 或者使用快捷键 - 很多应用支持Cmd+Option+A作为最大化
            return self._execute_keyboard_shortcut("cmd+option+A")
        except Exception as e:
            print(f"最大化窗口失败: {e}")
            # 回退到标准全屏
            return self._toggle_fullscreen()

    def _minimize_active_window(self) -> bool:
        """最小化当前活动窗口"""
        print("最小化当前窗口...")
        script = """
        try
            tell application (path to frontmost application as text)
                if (count of windows) > 0 then
                    set miniaturized of window 1 to true
                end if
            end tell
        on error
            -- Fallback to hotkey if direct manipulation fails
            tell application "System Events" to key code 4 using {command down}
        end try
        """
        try:
            script_obj = applescript.AppleScript(script)
            result = script_obj.run()
            print(f"AppleScript 结果: {result}")
            return True
        except applescript.ScriptError as e:
            print(f"最小化窗口失败: {e}")
            # 回退到标准快捷键
            return self._execute_keyboard_shortcut("cmd+m")

    def _restore_active_window(self) -> bool:
        """恢复当前活动窗口"""
        print("恢复当前窗口...")
        # macOS没有直接的恢复命令，我们可以尝试最小化然后恢复
        # 或者使用特定的应用程序快捷键
        try:
            # 先尝试退出全屏
            self._toggle_fullscreen()
            time.sleep(0.5)
            # 然后尝试恢复最小化的窗口（macOS中通常是点击Dock上的图标）
            script = """
            tell application "System Events"
                set frontApp to first application process whose frontmost is true
                set frontAppName to name of frontApp
                tell application frontAppName
                    activate
                    try
                        set miniaturized of window 1 to false
                    end try
                end tell
            end tell
            """
            script_obj = applescript.AppleScript(script)
            result = script_obj.run()
            print(f"AppleScript 结果: {result}")
            return True
        except Exception as e:
            print(f"恢复窗口失败: {e}")
            # 这里没有一个通用的快捷键，我们只能通知用户
            print("无法自动恢复窗口，请手动点击Dock上的应用图标")
            return False

    def _close_active_window(self) -> bool:
        """关闭当前活动窗口"""
        print("关闭当前窗口...")
        # 使用macOS标准快捷键Cmd+W
        return self._execute_keyboard_shortcut("cmd+w")

    def _move_window_relative(self, dx, dy) -> bool:
        """相对移动当前窗口"""
        print(f"移动窗口 dx={dx}, dy={dy}...")

        # 首先获取当前应用程序信息
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
            print(f"当前前台应用: {app_name}")
        except applescript.ScriptError as e:
            print(f"获取前台应用失败: {e}")
            return False

        # 现在尝试移动窗口
        move_script = f"""
        try
            tell application "System Events"
                tell process "{app_name}"
                    if (count of windows) is 0 then 
                        return "在 {app_name} 中没有找到窗口"
                    end if
                    
                    tell first window
                        set windowPosition to position
                        set oldX to item 1 of windowPosition
                        set oldY to item 2 of windowPosition
                        set newX to oldX + {dx}
                        set newY to oldY + {dy}
                        set position to {{newX, newY}}
                        set finalPosition to position
                        return "窗口从: " & oldX & "," & oldY & " 移动到 " & (item 1 of finalPosition) & "," & (item 2 of finalPosition)
                    end tell
                end tell
            end tell
        on error errMsg
            return "移动窗口错误: " & errMsg
        end try
        """

        try:
            script_obj = applescript.AppleScript(move_script)
            result = script_obj.run()
            print(f"AppleScript 结果: {result}")
            return True
        except applescript.ScriptError as e:
            print(f"移动窗口失败: {e}")
            return False

    def _volume_up(self) -> bool:
        """增加音量"""
        print("增加音量...")
        # 使用AppleScript控制音量
        script = """
        set volume output volume ((output volume of (get volume settings)) + 10) --10%的音量增加
        """
        try:
            script_obj = applescript.AppleScript(script)
            script_obj.run()
            return True
        except applescript.ScriptError as e:
            print(f"增加音量失败: {e}")
            # 回退到媒体键
            return self._execute_keyboard_shortcut("fn+f12")

    def _volume_down(self) -> bool:
        """降低音量"""
        print("降低音量...")
        # 使用AppleScript控制音量
        script = """
        set volume output volume ((output volume of (get volume settings)) - 10) --10%的音量减少
        """
        try:
            script_obj = applescript.AppleScript(script)
            script_obj.run()
            return True
        except applescript.ScriptError as e:
            print(f"降低音量失败: {e}")
            # 回退到媒体键
            return self._execute_keyboard_shortcut("fn+f11")

    def _volume_mute(self) -> bool:
        """切换静音"""
        print("切换静音...")
        # 使用AppleScript控制静音
        script = """
        set volume with output muted (not output muted of (get volume settings))
        """
        try:
            script_obj = applescript.AppleScript(script)
            script_obj.run()
            return True
        except applescript.ScriptError as e:
            print(f"切换静音失败: {e}")
            # 回退到媒体键
            return self._execute_keyboard_shortcut("fn+f10")

    def _play_pause(self) -> bool:
        """播放/暂停"""
        print("播放/暂停...")
        # 使用AppleScript控制播放
        script = """
        tell application "System Events" to key code 16 using {command down, option down} -- P key
        """
        try:
            script_obj = applescript.AppleScript(script)
            script_obj.run()
            return True
        except applescript.ScriptError as e:
            print(f"播放/暂停失败: {e}")
            # 回退到媒体键
            return self._execute_keyboard_shortcut("fn+f8")

    def _next_track(self) -> bool:
        """下一曲"""
        print("下一曲...")
        # 使用AppleScript控制下一曲
        script = """
        tell application "System Events" to key code 17 using {command down, option down} -- ] key
        """
        try:
            script_obj = applescript.AppleScript(script)
            script_obj.run()
            return True
        except applescript.ScriptError as e:
            print(f"下一曲失败: {e}")
            # 回退到媒体键
            return self._execute_keyboard_shortcut("fn+f9")

    def _prev_track(self) -> bool:
        """上一曲"""
        print("上一曲...")
        # 使用AppleScript控制上一曲
        script = """
        tell application "System Events" to key code 18 using {command down, option down} -- [ key
        """
        try:
            script_obj = applescript.AppleScript(script)
            script_obj.run()
            return True
        except applescript.ScriptError as e:
            print(f"上一曲失败: {e}")
            # 回退到媒体键
            return self._execute_keyboard_shortcut("fn+f7")

    def _window_drag(self) -> bool:
        """窗口拖拽"""
        print("窗口拖拽...")
        # 这个功能在macOS中需要更复杂的实现
        # 这里提供一个简化版本，先点击窗口标题栏，然后拖动鼠标
        try:
            # 首先获取前台窗口信息
            app_info_script = """
            tell application "System Events"
                set frontApp to first application process whose frontmost is true
                set frontAppName to name of frontApp
                tell process frontAppName
                    if (count of windows) is 0 then
                        return "no_window"
                    end if
                    set winPos to position of window 1
                    set winSize to size of window 1
                    return (item 1 of winPos) & "," & (item 2 of winPos) & "," & (item 1 of winSize) & "," & (item 2 of winSize)
                end tell
            end tell
            """

            script_obj = applescript.AppleScript(app_info_script)
            result = script_obj.run()

            if result == "no_window":
                print("没有找到可拖拽的窗口")
                return False

            # 解析窗口位置和大小
            if isinstance(result, str):
                parts = result.split(",")
                if len(parts) != 4:
                    print("无法解析窗口位置和大小")
                    return False

                x, y, width, height = map(int, parts)
            else:
                print("无法获取窗口信息")
                return False

            # 计算标题栏中心位置 (假设标题栏高度为22像素)
            title_x = x + width // 2
            title_y = y + 11  # 标题栏中心

            # 使用pyautogui模拟拖拽
            # 首先将鼠标移动到标题栏
            current_pos = pyautogui.position()
            pyautogui.moveTo(title_x, title_y, duration=0.2)

            # 模拟鼠标按下、移动和释放
            pyautogui.mouseDown()
            pyautogui.moveTo(title_x + 100, title_y, duration=0.3)  # 向右移动100像素
            pyautogui.mouseUp()

            # 将鼠标移回原位
            pyautogui.moveTo(current_pos, duration=0.2)

            return True
        except Exception as e:
            print(f"窗口拖拽失败: {e}")
            return False

    def _window_switch(self) -> bool:
        """窗口切换"""
        print("窗口切换...")
        # 使用macOS的标准应用切换快捷键
        return self._execute_keyboard_shortcut("cmd+tab")

    def _window_scroll_up(self) -> bool:
        """向上滚动"""
        print("向上滚动...")
        # 使用pyautogui执行滚动
        pyautogui.scroll(10)  # 正数表示向上滚动
        return True

    def _window_scroll_down(self) -> bool:
        """向下滚动"""
        print("向下滚动...")
        # 使用pyautogui执行滚动
        pyautogui.scroll(-10)  # 负数表示向下滚动
        return True

    def set_execution_cooldown(self, cooldown: float):
        """设置执行冷却时间"""
        self.execution_cooldown = cooldown


# 为了兼容性，提供 ActionExecutor 别名
ActionExecutor = MacActionExecutor

# 导出所有公共类和函数
__all__ = [
    'ActionExecutor',
    'MacActionExecutor',
    'Key',
    'Button',
    'KeyboardController',
    'MouseController'
]


# 测试代码
if __name__ == "__main__":
    executor = MacActionExecutor()

    # 测试一些功能
    print("\n测试窗口移动:")
    executor._move_window_relative(100, 50)

    print("\n测试全屏切换:")
    executor._toggle_fullscreen()

    print("\n测试音量控制:")
    executor._volume_up()
