"""
Windows API Easy - 精简的Windows窗口操作模块

简化的Windows API封装，专为手势控制设计
提供常用的窗口操作功能，如移动、缩放、贴靠等

主要功能：
- 窗口查找和获取
- 窗口移动和拖拽
- 窗口大小调整
- 窗口状态控制（最大化/最小化/还原）
- 窗口贴靠操作
- 多显示器支持
"""

from .window_controller import WindowController, WindowInfo
from .window_finder import WindowFinder
from .gesture_operator import GestureWindowOperator, gesture_operator

__version__ = "1.0.0"
__author__ = "Gestureye Project"

# 便捷的全局实例
window_controller = WindowController()
window_finder = WindowFinder()

# 导出主要类和函数
__all__ = [
    'WindowController',
    'WindowFinder', 
    'GestureWindowOperator',
    'WindowInfo',
    'window_controller',
    'window_finder',
    'gesture_operator'
]
