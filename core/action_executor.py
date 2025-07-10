"""
动作执行器 - 负责执行手势对应的快捷键和系统功能
重构版本，使用跨平台管理器
"""

import time
from typing import Dict, Any, Optional
from pynput import keyboard, mouse
from pynput.keyboard import Key, Controller as KeyboardController
from pynput.mouse import Controller as MouseController, Button

# 导入跨平台管理器
from executor.os_manager import OSManager

class ActionExecutor:
    """跨平台动作执行器"""
    
    def __init__(self):
        self.keyboard_controller = KeyboardController()
        self.mouse_controller = MouseController()
        self.last_execution_time = {}  # 防止重复执行
        self.execution_cooldown = 1.0  # 执行冷却时间（秒）
        
        # 初始化跨平台管理器
        self.os_manager = OSManager()
        print(f"初始化ActionExecutor - 系统信息: {self.os_manager.get_system_info()}")
        
        if not self.os_manager.is_available():
            print("警告: 平台特定功能不可用，将使用通用fallback实现")
        
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
                return self.os_manager.maximize_window()
            elif function == "window_minimize":
                return self.os_manager.minimize_window()
            elif function == "window_restore":
                return self.os_manager.restore_window()
            elif function == "window_close":
                return self.os_manager.close_window()
            elif function == "volume_up":
                return self.os_manager.volume_up()
            elif function == "volume_down":
                return self.os_manager.volume_down()
            elif function == "volume_mute":
                return self.os_manager.volume_mute()
            elif function == "play_pause":
                return self.os_manager.media_play_pause()            
            elif function == "next_track":
                return self.os_manager.media_next()
            elif function == "prev_track":
                return self.os_manager.media_previous()
            elif function == "window_drag":
                return self._window_drag()  # 这个需要特殊处理
            elif function == "window_switch":
                return self.os_manager.window_switch()
            elif function == "window_scroll_up":
                return self.os_manager.scroll_up()
            elif function == "window_scroll_down":
                return self.os_manager.scroll_down()
            else:
                print(f"未知的系统功能: {function}")
                return False
                
        except Exception as e:
            print(f"执行系统功能失败: {function}, 错误: {e}")
            return False
    
    def _execute_custom_function(self, function: str) -> bool:
        """执行自定义功能"""
        try:
            if function == "custom_action_1":
                # 数字1手势 - 复制
                return self._execute_keyboard_shortcut("ctrl+c")
            elif function == "custom_action_2":
                # 数字2手势 - 粘贴
                return self._execute_keyboard_shortcut("ctrl+v")
            elif function == "custom_action_3":
                # 数字3手势 - 撤销
                return self._execute_keyboard_shortcut("ctrl+z")
            else:
                print(f"执行自定义功能: {function}")
                return True
        except Exception as e:
            print(f"执行自定义功能失败: {function}, 错误: {e}")
            return False

    def set_execution_cooldown(self, cooldown: float):
        """设置执行冷却时间"""
        self.execution_cooldown = cooldown

    def _window_drag(self) -> bool:
        """窗口拖拽初始化 - 触发手势时调用一次"""
        print("HandClose手势触发，开始窗口拖拽模式")
        # 这里可以进行一些初始化工作，如获取当前活动窗口信息
        return True
    
    def execute_window_drag_with_trail(self, dx: int, dy: int) -> bool:
        """根据轨迹数据执行窗口拖拽"""
        try:
            return self.os_manager.drag_window(dx, dy)
        except Exception as e:
            print(f"窗口拖拽失败: {e}")
            return False

    def _windows_drag_with_trail(self, dx: int, dy: int) -> bool:
        """Windows窗口拖拽实现"""
        if not HAS_WIN32:
            print("Windows API不可用，使用鼠标模拟")
            return self._simulate_mouse_drag(dx, dy)
            
        try:
            # 获取前台窗口
            hwnd = win32gui.GetForegroundWindow()
            if not hwnd:
                return False
            
            # 获取窗口当前位置
            rect = win32gui.GetWindowRect(hwnd)
            left, top, right, bottom = rect
            
            # 计算新位置
            new_left = left + dx
            new_top = top + dy
            width = right - left
            height = bottom - top
            
            # 移动窗口
            win32gui.SetWindowPos(
                hwnd, 0, new_left, new_top, width, height,
                win32con.SWP_NOZORDER | win32con.SWP_NOACTIVATE
            )
            return True
            
        except Exception as e:
            print(f"Windows窗口拖拽失败: {e}")
            return self._simulate_mouse_drag(dx, dy)
    
    def _macos_drag_with_trail(self, dx: int, dy: int) -> bool:
        """macOS窗口拖拽实现"""
        try:
            # 使用AppleScript移动窗口
            script = f'''
            tell application "System Events"
                set frontApp to first application process whose frontmost is true
                tell frontApp
                    set windowPosition to position of front window
                    set newX to (item 1 of windowPosition) + {dx}
                    set newY to (item 2 of windowPosition) + {dy}
                    set position of front window to {{newX, newY}}
                end tell
            end tell
            '''
            subprocess.run(['osascript', '-e', script], capture_output=True, check=True)
            return True
        except Exception as e:
            print(f"macOS窗口拖拽失败: {e}")
            return self._simulate_mouse_drag(dx, dy)
    
    def _linux_drag_with_trail(self, dx: int, dy: int) -> bool:
        """Linux窗口拖拽实现"""
        try:
            # 尝试使用wmctrl
            result = subprocess.run(['wmctrl', '-r', ':ACTIVE:', '-e', f'0,-1,-1,-1,-1'], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                raise subprocess.CalledProcessError(result.returncode, 'wmctrl')
            
            # 获取当前活动窗口信息
            result = subprocess.run(['wmctrl', '-lG'], capture_output=True, text=True, check=True)
            lines = result.stdout.strip().split('\n')
            
            # 找到活动窗口
            active_result = subprocess.run(['xprop', '-root', '_NET_ACTIVE_WINDOW'], 
                                         capture_output=True, text=True, check=True)
            active_id = active_result.stdout.split()[-1]
            
            for line in lines:
                if active_id in line:
                    parts = line.split()
                    if len(parts) >= 5:
                        current_x, current_y = int(parts[2]), int(parts[3])
                        new_x, new_y = current_x + dx, current_y + dy
                        
                        # 移动窗口
                        subprocess.run(['wmctrl', '-r', ':ACTIVE:', '-e', f'0,{new_x},{new_y},-1,-1'], 
                                     check=True)
                        return True
            
            return False
            
        except (subprocess.CalledProcessError, FileNotFoundError):
            # wmctrl不可用，尝试使用X11
            if HAS_XLIB:
                return self._x11_drag_with_trail(dx, dy)
            else:
                return self._simulate_mouse_drag(dx, dy)
    
    def _x11_drag_with_trail(self, dx: int, dy: int) -> bool:
        """使用X11直接操作窗口"""
        try:
            d = display.Display()
            root = d.screen().root
            
            # 获取活动窗口
            active_window = root.get_full_property(
                d.intern_atom('_NET_ACTIVE_WINDOW'), 0
            ).value[0]
            
            window = d.create_resource_object('window', active_window)
            geom = window.get_geometry()
            
            # 计算新位置
            new_x = geom.x + dx
            new_y = geom.y + dy
            
            # 移动窗口
            window.configure(x=new_x, y=new_y)
            d.sync()
            return True
            
        except Exception as e:
            print(f"X11窗口拖拽失败: {e}")
            return self._simulate_mouse_drag(dx, dy)
    
    def _simulate_mouse_drag(self, dx: int, dy: int) -> bool:
        """使用鼠标模拟拖拽（备用方案）"""
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