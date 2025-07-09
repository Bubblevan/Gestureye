#!/usr/bin/env python3
"""
UI转换工具 - 将.ui文件转换为Python代码
"""

import os
import sys
import subprocess
from pathlib import Path


def ui_to_py(ui_file, py_file=None, pyqt_version=6):
    """
    将.ui文件转换为Python代码

    Args:
        ui_file: .ui文件路径
        py_file: 输出的.py文件路径（可选）
        pyqt_version: PyQt版本（5或6）
    """
    ui_path = Path(ui_file)

    if not ui_path.exists():
        print(f"错误: UI文件不存在 - {ui_file}")
        return False

    if py_file is None:
        py_file = ui_path.with_suffix(".py")

    py_path = Path(py_file)

    # 选择正确的工具
    if pyqt_version == 6:
        tool = "pyuic6"
    else:
        tool = "pyuic5"

    try:
        # 运行pyuic工具
        cmd = [tool, "-x", str(ui_path), "-o", str(py_path)]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        print(f"? 成功转换: {ui_file} -> {py_file}")
        return True

    except subprocess.CalledProcessError as e:
        print(f"? 转换失败: {e}")
        print(f"错误信息: {e.stderr}")
        return False
    except FileNotFoundError:
        print(f"? 工具不存在: {tool}")
        print("请确保已安装PyQt6并且pyuic6在PATH中")
        return False


def watch_ui_file(ui_file, py_file=None, pyqt_version=6):
    """
    监控.ui文件变化并自动转换
    """
    import time

    ui_path = Path(ui_file)
    if not ui_path.exists():
        print(f"错误: UI文件不存在 - {ui_file}")
        return

    last_modified = ui_path.stat().st_mtime
    print(f"? 监控文件变化: {ui_file}")
    print("按Ctrl+C停止监控")

    try:
        while True:
            current_modified = ui_path.stat().st_mtime
            if current_modified > last_modified:
                print(f"? 检测到文件变化，正在转换...")
                if ui_to_py(ui_file, py_file, pyqt_version):
                    last_modified = current_modified
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n? 停止监控")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="UI文件转换工具")
    parser.add_argument("ui_file", help=".ui文件路径")
    parser.add_argument("-o", "--output", help="输出的.py文件路径")
    parser.add_argument(
        "-v",
        "--version",
        type=int,
        choices=[5, 6],
        default=6,
        help="PyQt版本 (5或6，默认6)",
    )
    parser.add_argument(
        "-w", "--watch", action="store_true", help="监控文件变化并自动转换"
    )

    args = parser.parse_args()

    if args.watch:
        watch_ui_file(args.ui_file, args.output, args.version)
    else:
        ui_to_py(args.ui_file, args.output, args.version)


if __name__ == "__main__":
    main()
