# API 参考文档

## 模块概览

Windows API Easy 提供三个主要类：

- `WindowController` - 核心窗口操作功能
- `WindowFinder` - 窗口查找和搜索
- `GestureWindowOperator` - 手势操作的高级接口

## WindowController

### 构造函数

```python
WindowController()
```

初始化窗口控制器，自动获取屏幕尺寸。

### 属性

- `screen_width: int` - 屏幕宽度
- `screen_height: int` - 屏幕高度

### 窗口信息获取

#### get_active_window()

```python
def get_active_window() -> Optional[WindowInfo]
```

获取当前活动窗口的信息。

**返回值**: WindowInfo对象或None

**示例**:
```python
window = controller.get_active_window()
if window:
    print(f"活动窗口: {window.title}")
```

#### get_window_info(hwnd)

```python
def get_window_info(hwnd: int) -> Optional[WindowInfo]
```

获取指定窗口句柄的详细信息。

**参数**:
- `hwnd` (int): 窗口句柄

**返回值**: WindowInfo对象或None

#### get_screen_size()

```python
def get_screen_size() -> Tuple[int, int]
```

获取屏幕尺寸。

**返回值**: (width, height) 元组

### 窗口移动操作

#### move_window(hwnd, x, y, width, height)

```python
def move_window(hwnd: int, x: int, y: int, 
                width: Optional[int] = None, 
                height: Optional[int] = None) -> bool
```

移动窗口到指定位置和大小。

**参数**:
- `hwnd` (int): 窗口句柄
- `x` (int): 新的X坐标
- `y` (int): 新的Y坐标  
- `width` (int, 可选): 新的宽度，None则保持原宽度
- `height` (int, 可选): 新的高度，None则保持原高度

**返回值**: 操作是否成功

**特性**:
- 自动限制窗口在屏幕范围内
- 包含操作冷却机制

#### drag_window(hwnd, dx, dy)

```python
def drag_window(hwnd: int, dx: int, dy: int) -> bool
```

按偏移量拖拽窗口。

**参数**:
- `hwnd` (int): 窗口句柄
- `dx` (int): X轴偏移量
- `dy` (int): Y轴偏移量

**返回值**: 操作是否成功

#### drag_active_window(dx, dy)

```python
def drag_active_window(dx: int, dy: int) -> bool
```

拖拽当前活动窗口。

**参数**:
- `dx` (int): X轴偏移量
- `dy` (int): Y轴偏移量

**返回值**: 操作是否成功

### 窗口大小调整

#### resize_window(hwnd, width, height)

```python
def resize_window(hwnd: int, width: int, height: int) -> bool
```

调整窗口大小。

**参数**:
- `hwnd` (int): 窗口句柄
- `width` (int): 新宽度
- `height` (int): 新高度

**返回值**: 操作是否成功

**特性**:
- 自动限制最小尺寸 (200x150)
- 自动限制最大尺寸为屏幕大小

#### resize_window_by_scale(hwnd, scale_factor)

```python
def resize_window_by_scale(hwnd: int, scale_factor: float) -> bool
```

按比例调整窗口大小。

**参数**:
- `hwnd` (int): 窗口句柄  
- `scale_factor` (float): 缩放比例 (1.0 = 原始大小)

**返回值**: 操作是否成功

#### resize_active_window_by_scale(scale_factor)

```python
def resize_active_window_by_scale(scale_factor: float) -> bool
```

按比例调整当前活动窗口大小。

**参数**:
- `scale_factor` (float): 缩放比例

**返回值**: 操作是否成功

### 窗口状态控制

#### maximize_window(hwnd) / maximize_active_window()

```python
def maximize_window(hwnd: int) -> bool
def maximize_active_window() -> bool
```

最大化窗口。

#### minimize_window(hwnd) / minimize_active_window()

```python
def minimize_window(hwnd: int) -> bool  
def minimize_active_window() -> bool
```

最小化窗口。

#### restore_window(hwnd) / restore_active_window()

```python
def restore_window(hwnd: int) -> bool
def restore_active_window() -> bool
```

还原窗口到正常状态。

#### close_window(hwnd) / close_active_window()

```python
def close_window(hwnd: int) -> bool
def close_active_window() -> bool
```

关闭窗口。

### 窗口贴靠操作

#### snap_window_left(hwnd) / snap_active_window_left()

```python
def snap_window_left(hwnd: int) -> bool
def snap_active_window_left() -> bool
```

将窗口贴靠到屏幕左半部。

#### snap_window_right(hwnd) / snap_active_window_right()

```python
def snap_window_right(hwnd: int) -> bool
def snap_active_window_right() -> bool
```

将窗口贴靠到屏幕右半部。

#### 四分之一屏幕贴靠

```python
def snap_window_top_left(hwnd: int) -> bool
def snap_window_top_right(hwnd: int) -> bool  
def snap_window_bottom_left(hwnd: int) -> bool
def snap_window_bottom_right(hwnd: int) -> bool
```

将窗口贴靠到屏幕的四个角落，各占1/4屏幕。

### 实用工具

#### center_window(hwnd, width, height)

```python
def center_window(hwnd: int, 
                  width: Optional[int] = None, 
                  height: Optional[int] = None) -> bool
```

将窗口居中显示。

**参数**:
- `hwnd` (int): 窗口句柄
- `width` (int, 可选): 窗口宽度，None则保持原宽度
- `height` (int, 可选): 窗口高度，None则保持原高度

#### center_active_window()

```python
def center_active_window() -> bool
```

将当前活动窗口居中。

## WindowFinder

### 构造函数

```python
WindowFinder()
```

### 基本查找方法

#### find_all_windows(include_invisible)

```python
def find_all_windows(include_invisible: bool = False) -> List[WindowInfo]
```

获取所有窗口列表。

**参数**:
- `include_invisible` (bool): 是否包含不可见窗口

**返回值**: WindowInfo对象列表

#### find_by_title(title, exact_match)

```python
def find_by_title(title: str, exact_match: bool = False) -> List[WindowInfo]
```

根据窗口标题查找窗口。

**参数**:
- `title` (str): 要搜索的标题
- `exact_match` (bool): 是否精确匹配

**返回值**: 匹配的WindowInfo对象列表

#### find_by_title_regex(pattern)

```python
def find_by_title_regex(pattern: str) -> List[WindowInfo]
```

使用正则表达式搜索窗口标题。

**参数**:
- `pattern` (str): 正则表达式模式

**返回值**: 匹配的WindowInfo对象列表

#### find_by_process_name(process_name, exact_match)

```python
def find_by_process_name(process_name: str, 
                        exact_match: bool = False) -> List[WindowInfo]
```

根据进程名查找窗口。

**参数**:
- `process_name` (str): 进程名称
- `exact_match` (bool): 是否精确匹配

### 高级查找方法

#### find_by_custom_filter(filter_func)

```python
def find_by_custom_filter(filter_func: Callable[[WindowInfo], bool]) -> List[WindowInfo]
```

使用自定义过滤函数查找窗口。

**参数**:
- `filter_func`: 接受WindowInfo对象，返回bool的函数

**示例**:
```python
# 查找宽度大于800的窗口
wide_windows = finder.find_by_custom_filter(lambda w: w.width > 800)
```

#### find_windows_by_size_range(min_width, min_height, max_width, max_height)

```python
def find_windows_by_size_range(min_width: int = 0, 
                              min_height: int = 0,
                              max_width: int = float('inf'), 
                              max_height: int = float('inf')) -> List[WindowInfo]
```

根据尺寸范围查找窗口。

#### find_windows_in_area(x, y, width, height)

```python
def find_windows_in_area(x: int, y: int, 
                        width: int, height: int) -> List[WindowInfo]
```

查找在指定区域内的窗口。

### 状态查找方法

#### find_visible_windows()

```python
def find_visible_windows() -> List[WindowInfo]
```

查找所有可见且未最小化的窗口。

#### find_minimized_windows()

```python
def find_minimized_windows() -> List[WindowInfo]
```

查找所有最小化的窗口。

#### find_maximized_windows()

```python
def find_maximized_windows() -> List[WindowInfo]
```

查找所有最大化的窗口。

### 便捷查找方法

#### 应用程序特定查找

```python
def find_browser_windows() -> List[WindowInfo]
def find_office_windows() -> List[WindowInfo]  
def find_media_windows() -> List[WindowInfo]
def find_code_editor_windows() -> List[WindowInfo]
```

查找特定类型的应用程序窗口。

#### 实用查找

```python
def get_window_under_cursor() -> Optional[WindowInfo]
```

获取鼠标光标下的窗口。

```python
def search_windows(keyword: str) -> List[WindowInfo]
```

智能搜索窗口（同时搜索标题和进程名）。

## GestureWindowOperator

### 构造函数

```python
GestureWindowOperator()
```

### 预定义手势动作

支持的动作名称：

**窗口状态控制**:
- `maximize` - 最大化窗口
- `minimize` - 最小化窗口  
- `restore` - 还原窗口
- `close` - 关闭窗口
- `center` - 窗口居中

**窗口贴靠**:
- `snap_left` - 左半屏贴靠
- `snap_right` - 右半屏贴靠
- `snap_top_left` - 左上角1/4屏贴靠
- `snap_top_right` - 右上角1/4屏贴靠
- `snap_bottom_left` - 左下角1/4屏贴靠
- `snap_bottom_right` - 右下角1/4屏贴靠

**大小调整**:
- `resize_larger` - 放大20%
- `resize_smaller` - 缩小20%
- `resize_double` - 放大100%
- `resize_half` - 缩小50%

### 主要方法

#### execute_gesture_action(action_name)

```python
def execute_gesture_action(action_name: str) -> bool
```

执行预定义的手势动作。

**参数**:
- `action_name` (str): 动作名称

**返回值**: 执行是否成功

#### drag_window_by_gesture(dx, dy, sensitivity)

```python
def drag_window_by_gesture(dx: int, dy: int, 
                          sensitivity: float = 1.0) -> bool
```

通过手势拖拽窗口。

**参数**:
- `dx` (int): X轴偏移量
- `dy` (int): Y轴偏移量
- `sensitivity` (float): 敏感度调整

#### resize_window_by_gesture(scale_delta, min_scale, max_scale)

```python
def resize_window_by_gesture(scale_delta: float, 
                            min_scale: float = 0.1, 
                            max_scale: float = 3.0) -> bool
```

通过手势调整窗口大小。

**参数**:
- `scale_delta` (float): 缩放变化量
- `min_scale` (float): 最小缩放比例
- `max_scale` (float): 最大缩放比例

#### switch_to_window_by_gesture(direction)

```python
def switch_to_window_by_gesture(direction: str) -> bool
```

通过手势切换窗口。

**参数**:
- `direction` (str): 'next' 或 'previous'

#### get_available_actions()

```python
def get_available_actions() -> list
```

获取所有可用的手势动作名称。

#### get_window_status()

```python
def get_window_status() -> Dict[str, Any]
```

获取当前窗口的状态信息。

**返回值**: 包含窗口信息的字典

## WindowInfo 数据类

### 属性

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

### 使用示例

```python
window = controller.get_active_window()
if window:
    print(f"标题: {window.title}")
    print(f"进程: {window.process_name}")
    print(f"位置: ({window.x}, {window.y})")
    print(f"大小: {window.width}x{window.height}")
    print(f"状态: 可见={window.is_visible}, 最小化={window.is_minimized}")
```

## 错误处理

所有方法都包含完善的错误处理机制：

- 返回值为bool的方法：成功返回True，失败返回False
- 返回值为对象的方法：失败时返回None
- 错误信息会打印到控制台

## 性能考虑

- **冷却机制**: 防止重复操作，默认0.5秒
- **参数验证**: 自动验证和修正参数
- **内存管理**: 合理的对象生命周期管理
