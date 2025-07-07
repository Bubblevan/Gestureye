#!/usr/bin/env python3
"""
UIת������ - ��.ui�ļ�ת��ΪPython����
"""

import os
import sys
import subprocess
from pathlib import Path

def ui_to_py(ui_file, py_file=None, pyqt_version=6):
    """
    ��.ui�ļ�ת��ΪPython����
    
    Args:
        ui_file: .ui�ļ�·��
        py_file: �����.py�ļ�·������ѡ��
        pyqt_version: PyQt�汾��5��6��
    """
    ui_path = Path(ui_file)
    
    if not ui_path.exists():
        print(f"����: UI�ļ������� - {ui_file}")
        return False
    
    if py_file is None:
        py_file = ui_path.with_suffix('.py')
    
    py_path = Path(py_file)
    
    # ѡ����ȷ�Ĺ���
    if pyqt_version == 6:
        tool = 'pyuic6'
    else:
        tool = 'pyuic5'
    
    try:
        # ����pyuic����
        cmd = [tool, '-x', str(ui_path), '-o', str(py_path)]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        print(f"? �ɹ�ת��: {ui_file} -> {py_file}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"? ת��ʧ��: {e}")
        print(f"������Ϣ: {e.stderr}")
        return False
    except FileNotFoundError:
        print(f"? ���߲�����: {tool}")
        print("��ȷ���Ѱ�װPyQt6����pyuic6��PATH��")
        return False

def watch_ui_file(ui_file, py_file=None, pyqt_version=6):
    """
    ���.ui�ļ��仯���Զ�ת��
    """
    import time
    
    ui_path = Path(ui_file)
    if not ui_path.exists():
        print(f"����: UI�ļ������� - {ui_file}")
        return
    
    last_modified = ui_path.stat().st_mtime
    print(f"? ����ļ��仯: {ui_file}")
    print("��Ctrl+Cֹͣ���")
    
    try:
        while True:
            current_modified = ui_path.stat().st_mtime
            if current_modified > last_modified:
                print(f"? ��⵽�ļ��仯������ת��...")
                if ui_to_py(ui_file, py_file, pyqt_version):
                    last_modified = current_modified
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n? ֹͣ���")

def main():
    """������"""
    import argparse
    
    parser = argparse.ArgumentParser(description="UI�ļ�ת������")
    parser.add_argument("ui_file", help=".ui�ļ�·��")
    parser.add_argument("-o", "--output", help="�����.py�ļ�·��")
    parser.add_argument("-v", "--version", type=int, choices=[5, 6], default=6, 
                       help="PyQt�汾 (5��6��Ĭ��6)")
    parser.add_argument("-w", "--watch", action="store_true", 
                       help="����ļ��仯���Զ�ת��")
    
    args = parser.parse_args()
    
    if args.watch:
        watch_ui_file(args.ui_file, args.output, args.version)
    else:
        ui_to_py(args.ui_file, args.output, args.version)

if __name__ == "__main__":
    main() 