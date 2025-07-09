#!/usr/bin/env python3
"""
测试手势绑定更新
"""

from core.gesture_bindings import GestureBindings, GestureType
import json


def test_gesture_bindings():
    """测试手势绑定配置"""
    print("=" * 60)
    print("测试手势绑定配置更新")
    print("=" * 60)
    
    # 创建手势绑定管理器
    bindings = GestureBindings()
    
    # 获取所有绑定
    all_bindings = bindings.get_all_bindings()
    
    print(f"总共配置了 {len(all_bindings)} 个手势:")
    print()
    
    # 显示静态手势
    print("?? 静态手势:")
    static_gestures = bindings.get_static_gestures()
    for gesture_name, config in static_gestures.items():
        print(f"  - {gesture_name}: {config['description']}")
        print(f"    动作类型: {config['action_type']}")
        print(f"    动作: {config['action']}")
        print(f"    启用状态: {'?' if config['enabled'] else '?'}")
        print()
    
    # 显示动态手势
    print("? 动态手势:")
    dynamic_gestures = bindings.get_dynamic_gestures()
    for gesture_name, config in dynamic_gestures.items():
        print(f"  - {gesture_name}: {config['description']}")
        print(f"    动作类型: {config['action_type']}")
        print(f"    动作: {config['action']}")
        print(f"    启用状态: {'?' if config['enabled'] else '?'}")
        print()
    
    # 测试手势类型枚举
    print("? 手势类型枚举:")
    for gesture_type in GestureType:
        print(f"  - {gesture_type.name}: {gesture_type.value}")
    
    print()
    print("=" * 60)
    print("测试完成!")
    print("=" * 60)


if __name__ == "__main__":
    test_gesture_bindings() 