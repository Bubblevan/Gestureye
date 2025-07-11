#!/usr/bin/env python3
"""
Linux系统蓝牙MAC地址获取工具
"""

import os
import subprocess
import re
import glob

def get_bluetooth_mac_linux():
    """在Linux系统上获取蓝牙MAC地址"""
    print("=== Linux蓝牙MAC地址获取工具 ===\n")
    
    methods = [
        ("方法1: 使用hciconfig命令", get_mac_via_hciconfig),
        ("方法2: 使用bluetoothctl命令", get_mac_via_bluetoothctl),
        ("方法3: 读取系统文件", get_mac_via_sysfs),
        ("方法4: 使用dmesg命令", get_mac_via_dmesg),
    ]
    
    found_macs = []
    
    for method_name, method_func in methods:
        print(f"尝试 {method_name}...")
        try:
            mac = method_func()
            if mac:
                print(f"✅ 成功: {mac}")
                found_macs.append(mac)
            else:
                print("❌ 失败: 未找到MAC地址")
        except Exception as e:
            print(f"❌ 错误: {e}")
        print()
    
    if found_macs:
        print("=== 找到的蓝牙MAC地址 ===")
        for i, mac in enumerate(found_macs, 1):
            print(f"{i}. {mac}")
        
        # 去重并选择第一个
        unique_macs = list(dict.fromkeys(found_macs))
        if unique_macs:
            recommended_mac = unique_macs[0]
            print(f"\n推荐使用: {recommended_mac}")
            print(f"\n请在 project/config.py 中设置:")
            print(f"BLUETOOTH_MAC = '{recommended_mac}'")
        else:
            print("\n未找到有效的蓝牙MAC地址")
    else:
        print("❌ 所有方法都失败了")
        print("\n请尝试手动获取:")
        print("1. 运行: sudo hciconfig")
        print("2. 运行: bluetoothctl show")
        print("3. 查看: cat /sys/class/bluetooth/hci0/address")

def get_mac_via_hciconfig():
    """使用hciconfig命令获取MAC地址"""
    try:
        result = subprocess.run(['hciconfig'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            # 查找MAC地址模式
            mac_pattern = r'BD Address: ([0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2})'
            match = re.search(mac_pattern, result.stdout)
            if match:
                return match.group(1).upper()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return None

def get_mac_via_bluetoothctl():
    """使用bluetoothctl命令获取MAC地址"""
    try:
        result = subprocess.run(['bluetoothctl', 'show'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            # 查找MAC地址模式
            mac_pattern = r'([0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2})'
            match = re.search(mac_pattern, result.stdout)
            if match:
                return match.group(1).upper()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return None

def get_mac_via_sysfs():
    """通过sysfs文件系统获取MAC地址"""
    try:
        # 查找所有蓝牙适配器
        bluetooth_dirs = glob.glob('/sys/class/bluetooth/hci*')
        for bt_dir in bluetooth_dirs:
            address_file = os.path.join(bt_dir, 'address')
            if os.path.exists(address_file):
                with open(address_file, 'r') as f:
                    mac = f.read().strip().upper()
                    if re.match(r'^[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}$', mac):
                        return mac
    except Exception:
        pass
    return None

def get_mac_via_dmesg():
    """使用dmesg命令获取MAC地址"""
    try:
        result = subprocess.run(['dmesg'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            # 查找蓝牙相关的MAC地址
            mac_pattern = r'([0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2})'
            matches = re.findall(mac_pattern, result.stdout)
            for mac in matches:
                mac_upper = mac.upper()
                # 过滤掉一些常见的无效MAC地址
                if mac_upper not in ['00:00:00:00:00:00', 'FF:FF:FF:FF:FF:FF']:
                    return mac_upper
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return None

if __name__ == "__main__":
    get_bluetooth_mac_linux() 