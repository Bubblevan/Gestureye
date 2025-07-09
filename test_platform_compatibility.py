#!/usr/bin/env python3
"""
�򵥵�ƽ̨�����Բ���
��֤��Ҫ����Ƿ�����ڵ�ǰƽ̨��������ͳ�ʼ��
"""

import sys
import platform

def test_imports():
    """���Թؼ�ģ�鵼��"""
    print(f"??  ��ǰƽ̨: {platform.system()} {platform.release()}")
    print(f"? Python�汾: {platform.python_version()}")
    print("-" * 50)
    
    try:
        print("? ���Ժ���ģ�鵼��...")
        
        # ����PyQt6
        from PyQt6.QtWidgets import QApplication
        print("? PyQt6 ����ɹ�")
        
        # ����pynput
        from pynput import keyboard, mouse
        print("? pynput ����ɹ�")
        
        # ����ActionExecutor
        from core.action_executor import ActionExecutor
        executor = ActionExecutor()
        print(f"? ActionExecutor ��ʼ���ɹ� (OS: {executor.os})")
        
        # ����Windows����ģ�飨����Windows�ϣ�
        if platform.system() == "Windows":
            try:
                import win32gui, win32con, win32api
                print("? pywin32 ģ�����")
            except ImportError:
                print("??  pywin32 �����ã���ʹ�ñ���ʵ��")
        
        # ����UI���
        from ui.main_window_ui import MainWindowUI
        print("? ������UI�������ɹ�")
        
        print("-" * 50)
        print("? ���к����������ɹ�����Ŀ֧�ֵ�ǰƽ̨��")
        return True
        
    except ImportError as e:
        print(f"? ����ʧ��: {e}")
        print("? �밲װȱʧ������: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"? ��ʼ��ʧ��: {e}")
        return False

def test_basic_functionality():
    """���Ի�������"""
    try:
        print("\n? ���Ի�������...")
        
        # ����ActionExecutor��������
        from core.action_executor import ActionExecutor
        executor = ActionExecutor()
        
        # ���Կ�ݼ���������ʵ��ִ�У�
        print("??  ���Կ�ݼ�����...")
        test_shortcuts = ["ctrl+c", "alt+tab", "f1"]
        for shortcut in test_shortcuts:
            # ֻ���Խ�������ʵ��ִ��
            keys = shortcut.lower().split('+')
            print(f"   {shortcut} -> ����Ϊ {len(keys)} ����")
        
        print("? �������ܲ���ͨ��")
        return True
        
    except Exception as e:
        print(f"? ���ܲ���ʧ��: {e}")
        return False

def main():
    """�����Ժ���"""
    print("? ���ƿ���ϵͳ - ƽ̨�����Բ���")
    print("=" * 50)
    
    # ���Ե���
    import_success = test_imports()
    
    if import_success:
        # ���Ի�������
        function_success = test_basic_functionality()
        
        if function_success:
            print("\n? ��ϲ����Ŀ��ȫ���ݵ�ǰƽ̨��")
            print("? �����ڿ�������: python app.py")
        else:
            print("\n??  ����ɹ������ܲ���ʧ�ܣ�������Ҫ�������á�")
    else:
        print("\n? ����ʧ�ܣ����Ȱ�װ��������ƽ̨�����ԡ�")

if __name__ == "__main__":
    main() 