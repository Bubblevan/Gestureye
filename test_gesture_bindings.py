#!/usr/bin/env python3
"""
�������ư󶨸���
"""

from core.gesture_bindings import GestureBindings, GestureType
import json


def test_gesture_bindings():
    """�������ư�����"""
    print("=" * 60)
    print("�������ư����ø���")
    print("=" * 60)
    
    # �������ư󶨹�����
    bindings = GestureBindings()
    
    # ��ȡ���а�
    all_bindings = bindings.get_all_bindings()
    
    print(f"�ܹ������� {len(all_bindings)} ������:")
    print()
    
    # ��ʾ��̬����
    print("?? ��̬����:")
    static_gestures = bindings.get_static_gestures()
    for gesture_name, config in static_gestures.items():
        print(f"  - {gesture_name}: {config['description']}")
        print(f"    ��������: {config['action_type']}")
        print(f"    ����: {config['action']}")
        print(f"    ����״̬: {'?' if config['enabled'] else '?'}")
        print()
    
    # ��ʾ��̬����
    print("? ��̬����:")
    dynamic_gestures = bindings.get_dynamic_gestures()
    for gesture_name, config in dynamic_gestures.items():
        print(f"  - {gesture_name}: {config['description']}")
        print(f"    ��������: {config['action_type']}")
        print(f"    ����: {config['action']}")
        print(f"    ����״̬: {'?' if config['enabled'] else '?'}")
        print()
    
    # ������������ö��
    print("? ��������ö��:")
    for gesture_type in GestureType:
        print(f"  - {gesture_type.name}: {gesture_type.value}")
    
    print()
    print("=" * 60)
    print("�������!")
    print("=" * 60)


if __name__ == "__main__":
    test_gesture_bindings() 