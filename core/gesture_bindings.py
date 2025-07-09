"""
手势绑定配置 - 定义手势与快捷键/系统功能的映射关系
"""

from enum import Enum
from typing import Dict, Any, Callable, Optional
import json
import os

class GestureType(Enum):
    """手势类型枚举"""
    FINGER_COUNT_ONE = "FingerCountOne"
    FINGER_COUNT_TWO = "FingerCountTwo"
    FINGER_COUNT_THREE = "FingerCountThree"
    HAND_OPEN = "HandOpen"
    TWO_FINGER_SWIPE = "TwoFingerSwipe"
    HAND_CLOSE = "HandClose"
    HAND_SWIPE = "HandSwipe"
    HAND_FLIP = "HandFlip"
    THUMBS_UP = "ThumbsUp"
    THUMBS_DOWN = "ThumbsDown"

class ActionType(Enum):
    """动作类型枚举"""
    KEYBOARD_SHORTCUT = "keyboard_shortcut"
    SYSTEM_FUNCTION = "system_function"
    CUSTOM_FUNCTION = "custom_function"

class GestureBindings:
    """手势绑定管理器"""
    
    def __init__(self, config_file: str = "gesture_bindings.json"):
        self.config_file = config_file
        self.bindings = self.load_bindings()
        
    def load_bindings(self) -> Dict[str, Dict[str, Any]]:
        """加载手势绑定配置"""        
        default_bindings = {
            # 静态手势
            "FingerCountOne": {
                "action_type": ActionType.SYSTEM_FUNCTION.value,
                "action": "volume_up",
                "description": "音量增加",
                "enabled": True,
                "gesture_type": "static"
            },
            "FingerCountTwo": {
                "action_type": ActionType.SYSTEM_FUNCTION.value,
                "action": "volume_down",
                "description": "音量减少",
                "enabled": True,
                "gesture_type": "static"
            },
            "FingerCountThree": {
                "action_type": ActionType.SYSTEM_FUNCTION.value,
                "action": "play_pause",
                "description": "播放/暂停",
                "enabled": True,
                "gesture_type": "static"
            },
            "ThumbsUp": {
                "action_type": ActionType.SYSTEM_FUNCTION.value,
                "action": "volume_mute",
                "description": "静音",
                "enabled": True,
                "gesture_type": "static"
            },
            "ThumbsDown": {
                "action_type": ActionType.SYSTEM_FUNCTION.value,
                "action": "brightness_down",
                "description": "亮度减少",
                "enabled": True,
                "gesture_type": "static"
            },
            # 动态手势
            "HandOpen": {
                "action_type": ActionType.SYSTEM_FUNCTION.value,
                "action": "window_maximize",
                "description": "最大化窗口",
                "enabled": True,
                "gesture_type": "dynamic"
            },
            "HandClose": {
                "action_type": ActionType.SYSTEM_FUNCTION.value,
                "action": "window_minimize",
                "description": "最小化窗口",
                "enabled": True,
                "gesture_type": "dynamic"
            },
            "HandSwipe": {
                "action_type": ActionType.KEYBOARD_SHORTCUT.value,
                "action": "alt+tab",
                "description": "应用切换",
                "enabled": True,
                "gesture_type": "dynamic"
            },
            "HandFlip": {
                "action_type": ActionType.KEYBOARD_SHORTCUT.value,
                "action": "alt+f4",
                "description": "关闭窗口",
                "enabled": True,
                "gesture_type": "dynamic"
            },
            "TwoFingerSwipe": {
                "action_type": ActionType.KEYBOARD_SHORTCUT.value,
                "action": "win+tab",
                "description": "任务视图",
                "enabled": True,
                "gesture_type": "dynamic"
            }
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    saved_bindings = json.load(f)
                    # 合并默认配置和保存的配置
                    for gesture, config in default_bindings.items():
                        if gesture not in saved_bindings:
                            saved_bindings[gesture] = config
                    return saved_bindings
            except Exception as e:
                print(f"加载手势绑定配置失败: {e}")
                return default_bindings
        else:
            # 保存默认配置
            self.save_bindings(default_bindings)
            return default_bindings
    
    def save_bindings(self, bindings: Optional[Dict[str, Dict[str, Any]]] = None):
        """保存手势绑定配置"""
        if bindings is None:
            bindings = self.bindings
            
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(bindings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存手势绑定配置失败: {e}")
    
    def get_binding(self, gesture: str) -> Dict[str, Any]:
        """获取指定手势的绑定配置"""
        return self.bindings.get(gesture, {})
    
    def set_binding(self, gesture: str, action_type: str, action: str, 
                   description: str = "", enabled: bool = True):
        """设置手势绑定"""
        self.bindings[gesture] = {
            "action_type": action_type,
            "action": action,
            "description": description,
            "enabled": enabled
        }
        self.save_bindings()
    
    def enable_binding(self, gesture: str, enabled: bool = True):
        """启用/禁用手势绑定"""
        if gesture in self.bindings:
            self.bindings[gesture]["enabled"] = enabled
            self.save_bindings()
    
    def get_all_bindings(self) -> Dict[str, Dict[str, Any]]:
        """获取所有手势绑定"""
        return self.bindings.copy()
    
    def reset_to_defaults(self):
        """重置为默认配置"""
        # 删除现有配置文件
        if os.path.exists(self.config_file):
            os.remove(self.config_file)
        # 重新加载默认配置
        self.bindings = self.load_bindings()
        self.save_bindings()
    
    def update_bindings(self, bindings: Dict[str, Dict[str, Any]]):
        """更新手势绑定配置"""
        self.bindings.update(bindings)
        self.save_bindings()

    def get_gesture_type(self, gesture: str) -> str:
        """获取手势类型 (static/dynamic)"""
        binding = self.get_binding(gesture)
        return binding.get("gesture_type", "static")
    
    def get_static_gestures(self) -> Dict[str, Dict[str, Any]]:
        """获取所有静态手势绑定"""
        return {k: v for k, v in self.bindings.items() 
                if v.get("gesture_type", "static") == "static"}
    
    def get_dynamic_gestures(self) -> Dict[str, Dict[str, Any]]:
        """获取所有动态手势绑定"""
        return {k: v for k, v in self.bindings.items() 
                if v.get("gesture_type", "static") == "dynamic"}
    
    def is_gesture_enabled(self, gesture: str) -> bool:
        """检查手势是否启用"""
        binding = self.get_binding(gesture)
        return binding.get("enabled", False) if binding else False