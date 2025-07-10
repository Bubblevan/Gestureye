# Windows API Easy

一个简化的Windows窗口操作模块，专为手势控制应用设计。提供简洁易用的API来控制Windows窗口的各种操作。

## 特性

- 🪟 **完整的窗口控制** - 移动、调整大小、最大化、最小化、关闭窗口
- 🎯 **智能窗口查找** - 根据标题、进程名、类名等多种方式查找窗口
- 🖱️ **拖拽操作** - 支持手势拖拽窗口
- 📐 **窗口贴靠** - 左右半屏、四分之一屏幕贴靠
- 🎮 **手势映射** - 预定义的手势到窗口操作的映射
- ⚡ **高性能** - 轻量级设计，响应迅速
- 🛡️ **错误处理** - 完善的异常处理和冷却机制

## 安装要求

```txt
pywin32>=227
psutil>=5.8.0
```

## 快速开始

### 基本窗口操作

```python
from windows_api_easy import window_controller

# 获取当前活动窗口信息
active_window = window_controller.get_active_window()
print(f"当前窗口: {active_window.title}")

# 移动窗口
window_controller.move_window(active_window.hwnd, 100, 100)

# 拖拽窗口（相对移动）
window_controller.drag_active_window(50, 30)

# 调整窗口大小
window_controller.resize_window(active_window.hwnd, 800, 600)

# 按比例缩放
window_controller.resize_active_window_by_scale(1.5)

# 窗口状态控制
window_controller.maximize_active_window()
window_controller.minimize_active_window()
window_controller.restore_active_window()
window_controller.center_active_window()

# 窗口贴靠
window_controller.snap_active_window_left()   # 左半屏
window_controller.snap_active_window_right()  # 右半屏
```

### 窗口查找

```python
from windows_api_easy import window_finder

# 查找所有可见窗口
visible_windows = window_finder.find_visible_windows()

# 根据标题查找窗口
chrome_windows = window_finder.find_by_title("Chrome")

# 根据进程名查找
notepad_windows = window_finder.find_by_process_name("notepad.exe")

# 使用正则表达式查找
regex_windows = window_finder.find_by_title_regex(r".*\.txt.*")

# 便捷方法
browser_windows = window_finder.find_browser_windows()
office_windows = window_finder.find_office_windows()
editor_windows = window_finder.find_code_editor_windows()

# 智能搜索
search_results = window_finder.search_windows("VS Code")
```

### 手势操作

```python
from windows_api_easy import gesture_operator

# 执行预定义的手势动作
gesture_operator.execute_gesture_action('maximize')
gesture_operator.execute_gesture_action('snap_left')
gesture_operator.execute_gesture_action('resize_larger')

# 手势拖拽（带敏感度调整）
gesture_operator.drag_window_by_gesture(dx=100, dy=50, sensitivity=1.5)

# 手势缩放
gesture_operator.resize_window_by_gesture(scale_delta=1.2)

# 窗口切换
gesture_operator.switch_to_window_by_gesture('next')

# 获取窗口状态
status = gesture_operator.get_window_status()
print(status)
```

## API 参考

### WindowController 类

主要的窗口控制类，提供所有窗口操作功能。

#### 窗口信息

- `get_active_window() -> Optional[WindowInfo]` - 获取当前活动窗口
- `get_window_info(hwnd: int) -> Optional[WindowInfo]` - 获取指定窗口信息
- `get_screen_size() -> Tuple[int, int]` - 获取屏幕尺寸

#### 窗口移动

- `move_window(hwnd, x, y, width=None, height=None) -> bool` - 移动窗口到指定位置
- `drag_window(hwnd, dx, dy) -> bool` - 按偏移量拖拽窗口
- `drag_active_window(dx, dy) -> bool` - 拖拽当前活动窗口
- `center_window(hwnd, width=None, height=None) -> bool` - 窗口居中
- `center_active_window() -> bool` - 当前窗口居中

#### 窗口大小调整

- `resize_window(hwnd, width, height) -> bool` - 调整窗口大小
- `resize_window_by_scale(hwnd, scale_factor) -> bool` - 按比例调整大小
- `resize_active_window_by_scale(scale_factor) -> bool` - 按比例调整当前窗口

#### 窗口状态控制

- `maximize_window(hwnd) -> bool` / `maximize_active_window() -> bool` - 最大化窗口
- `minimize_window(hwnd) -> bool` / `minimize_active_window() -> bool` - 最小化窗口
- `restore_window(hwnd) -> bool` / `restore_active_window() -> bool` - 还原窗口
- `close_window(hwnd) -> bool` / `close_active_window() -> bool` - 关闭窗口

#### 窗口贴靠

- `snap_window_left(hwnd) -> bool` / `snap_active_window_left() -> bool` - 左半屏贴靠
- `snap_window_right(hwnd) -> bool` / `snap_active_window_right() -> bool` - 右半屏贴靠
- `snap_window_top_left(hwnd) -> bool` - 左上角1/4屏幕贴靠
- `snap_window_top_right(hwnd) -> bool` - 右上角1/4屏幕贴靠
- `snap_window_bottom_left(hwnd) -> bool` - 左下角1/4屏幕贴靠
- `snap_window_bottom_right(hwnd) -> bool` - 右下角1/4屏幕贴靠

### WindowFinder 类

窗口查找和搜索功能。

#### 基本查找

- `find_all_windows(include_invisible=False) -> List[WindowInfo]` - 获取所有窗口
- `find_by_title(title, exact_match=False) -> List[WindowInfo]` - 根据标题查找
- `find_by_title_regex(pattern) -> List[WindowInfo]` - 正则表达式标题查找
- `find_by_class_name(class_name, exact_match=False) -> List[WindowInfo]` - 根据类名查找
- `find_by_process_name(process_name, exact_match=False) -> List[WindowInfo]` - 根据进程名查找
- `find_by_pid(pid) -> List[WindowInfo]` - 根据进程ID查找

#### 高级查找

- `find_by_custom_filter(filter_func) -> List[WindowInfo]` - 自定义过滤器查找
- `find_largest_window() -> Optional[WindowInfo]` - 查找最大窗口
- `find_windows_by_size_range(min_width, min_height, max_width, max_height) -> List[WindowInfo]` - 尺寸范围查找
- `find_windows_in_area(x, y, width, height) -> List[WindowInfo]` - 区域内窗口查找

#### 状态查找

- `find_visible_windows() -> List[WindowInfo]` - 可见窗口
- `find_minimized_windows() -> List[WindowInfo]` - 最小化窗口
- `find_maximized_windows() -> List[WindowInfo]` - 最大化窗口

#### 便捷查找

- `find_browser_windows() -> List[WindowInfo]` - 浏览器窗口
- `find_office_windows() -> List[WindowInfo]` - Office应用窗口
- `find_media_windows() -> List[WindowInfo]` - 媒体播放器窗口
- `find_code_editor_windows() -> List[WindowInfo]` - 代码编辑器窗口
- `get_window_under_cursor() -> Optional[WindowInfo]` - 光标下的窗口
- `search_windows(keyword) -> List[WindowInfo]` - 智能搜索

### GestureWindowOperator 类

手势操作的高级接口。

#### 预定义动作

支持的手势动作名称：
- `maximize`, `minimize`, `restore`, `close`, `center` - 窗口状态
- `snap_left`, `snap_right` - 半屏贴靠
- `snap_top_left`, `snap_top_right`, `snap_bottom_left`, `snap_bottom_right` - 四分之一屏贴靠
- `resize_larger`, `resize_smaller`, `resize_double`, `resize_half` - 大小调整

#### 主要方法

- `execute_gesture_action(action_name) -> bool` - 执行预定义手势动作
- `drag_window_by_gesture(dx, dy, sensitivity=1.0) -> bool` - 手势拖拽
- `resize_window_by_gesture(scale_delta, min_scale=0.1, max_scale=3.0) -> bool` - 手势缩放
- `switch_to_window_by_gesture(direction) -> bool` - 手势切换窗口
- `get_available_actions() -> list` - 获取可用动作列表
- `get_window_status() -> Dict[str, Any]` - 获取窗口状态

### WindowInfo 数据类

窗口信息数据结构：

```python
@dataclass
class WindowInfo:
    hwnd: int                    # 窗口句柄
    title: str                   # 窗口标题
    class_name: str             # 窗口类名
    pid: int                    # 进程ID
    process_name: str           # 进程名称
    x: int                      # 窗口X坐标
    y: int                      # 窗口Y坐标
    width: int                  # 窗口宽度
    height: int                 # 窗口高度
    is_visible: bool            # 是否可见
    is_minimized: bool          # 是否最小化
    is_maximized: bool          # 是否最大化
```

## 在手势控制中的集成

### 与主项目集成

在 `core/action_executor.py` 中集成：

```python
# 导入模块
from windows_api_easy import gesture_operator

class ActionExecutor:
    def __init__(self):
        self.gesture_operator = gesture_operator
    
    def _execute_system_function(self, action: str) -> bool:
        """执行系统功能"""
        # 窗口操作
        if action.startswith('window_'):
            window_action = action.replace('window_', '')
            return self.gesture_operator.execute_gesture_action(window_action)
        
        # 窗口拖拽（从手势数据中获取偏移量）
        elif action == 'drag_window':
            # 这里需要从手势数据中获取dx, dy
            return self.gesture_operator.drag_window_by_gesture(dx, dy)
        
        # 其他系统功能...
```

### 手势映射配置

在 `gesture_bindings.json` 中添加窗口操作：

```json
{
  "HandOpen": {
    "action_type": "system_function",
    "action": "window_maximize",
    "description": "最大化窗口",
    "enabled": true,
    "gesture_type": "dynamic"
  },
  "HandClose": {
    "action_type": "system_function", 
    "action": "window_minimize",
    "description": "最小化窗口",
    "enabled": true,
    "gesture_type": "dynamic"
  },
  "SwipeLeft": {
    "action_type": "system_function",
    "action": "window_snap_left", 
    "description": "窗口左贴靠",
    "enabled": true,
    "gesture_type": "dynamic"
  },
  "SwipeRight": {
    "action_type": "system_function",
    "action": "window_snap_right",
    "description": "窗口右贴靠", 
    "enabled": true,
    "gesture_type": "dynamic"
  }
}
```

## 性能特性

- **冷却机制**: 防止重复执行，默认0.5秒冷却时间
- **错误处理**: 完善的异常捕获和处理
- **内存优化**: 轻量级设计，最小化资源占用
- **线程安全**: 支持多线程环境使用

## 注意事项

1. **权限要求**: 某些操作可能需要管理员权限
2. **兼容性**: 仅支持Windows平台
3. **依赖项**: 需要安装pywin32和psutil
4. **冷却时间**: 相同操作有0.5秒冷却时间，防止重复执行

## 故障排除

### 常见问题

1. **导入错误**: 确保已安装pywin32
   ```bash
   pip install pywin32
   ```

2. **权限不足**: 以管理员身份运行程序

3. **窗口操作失败**: 检查目标窗口是否存在且可操作

4. **坐标超出屏幕**: 自动限制在屏幕范围内

## 示例代码

查看 `examples.py` 文件获取完整的使用示例和演示代码。

## 更新日志

### v1.0.0
- 初始版本
- 完整的窗口控制功能
- 智能窗口查找
- 手势操作映射
- 详细文档和示例
