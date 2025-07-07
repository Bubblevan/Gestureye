"""
手势绑定配置 - 定义手势与快捷键/系统功能的映射关系
"""

from enum import Enum
from typing import Dict, Any, Callable
import json
import os

class GestureType(Enum):
    """手势类型枚举"""
    PEACE_SIGN = "PeaceSign"
    THUMBS_UP = "ThumbsUp"
    THUMBS_DOWN = "ThumbsDown"
    HAND_OPEN = "HandOpen"
    OK_SIGN = "OKSign"
    SWIPE_LEFT = "SwipeLeft"
    SWIPE_RIGHT = "SwipeRight"
    SWIPE_UP = "SwipeUp"
    SWIPE_DOWN = "SwipeDown"

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
            "thumbs_up": {
                "action_type": ActionType.SYSTEM_FUNCTION.value,
                "action": "volume_up",
                "description": "音量增加",
                "enabled": True
            },
            "thumbs_down": {
                "action_type": ActionType.SYSTEM_FUNCTION.value,
                "action": "volume_down",
                "description": "音量减少",
                "enabled": True
            },
            "peace": {
                "action_type": ActionType.SYSTEM_FUNCTION.value,
                "action": "play_pause",
                "description": "播放/暂停",
                "enabled": True
            },
            "ok": {
                "action_type": ActionType.SYSTEM_FUNCTION.value,
                "action": "volume_mute",
                "description": "静音",
                "enabled": True
            },
            "pinch": {
                "action_type": ActionType.SYSTEM_FUNCTION.value,
                "action": "previous_track",
                "description": "上一首",
                "enabled": True
            },
            "wave": {
                "action_type": ActionType.SYSTEM_FUNCTION.value,
                "action": "next_track",
                "description": "下一首",
                "enabled": True
            },
            "swipe_left": {
                "action_type": ActionType.KEYBOARD_SHORTCUT.value,
                "action": "alt+left",
                "description": "后退",
                "enabled": True
            },
            "swipe_right": {
                "action_type": ActionType.KEYBOARD_SHORTCUT.value,
                "action": "alt+right",
                "description": "前进",
                "enabled": True
            },
            "swipe_up": {
                "action_type": ActionType.KEYBOARD_SHORTCUT.value,
                "action": "page_up",
                "description": "向上滚动",
                "enabled": True
            },
            "swipe_down": {
                "action_type": ActionType.KEYBOARD_SHORTCUT.value,
                "action": "page_down",
                "description": "向下滚动",
                "enabled": True
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
    
    def save_bindings(self, bindings: Dict[str, Dict[str, Any]] = None):
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