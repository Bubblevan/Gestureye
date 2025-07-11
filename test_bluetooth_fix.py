#!/usr/bin/env python3
"""
测试蓝牙MAC地址格式修复
"""

import socket
import re

def test_bluetooth_mac_format():
    """测试蓝牙MAC地址格式"""
    print("=" * 50)
    print("蓝牙MAC地址格式测试")
    print("=" * 50)
    
    # 测试不同的MAC地址格式
    test_macs = [
        "58:1C:F8:2E:5B:20",  # 大写格式（Windows返回的格式）
        "58:1c:f8:2e:5b:20",  # 小写格式（蓝牙socket期望的格式）
        "58-1C-F8-2E-5B-20",  # 带横线的格式
        "58:1c:f8:2e:5b:20",  # 标准小写格式
    ]
    
    for mac in test_macs:
        print(f"\n测试MAC地址: {mac}")
        
        # 转换为小写格式
        mac_lower = mac.replace('-', ':').lower()
        print(f"转换后: {mac_lower}")
        
        # 验证格式
        is_valid = re.match(r'^[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}$', mac_lower)
        print(f"格式有效: {is_valid is not None}")
        
        # 尝试创建蓝牙socket并绑定
        try:
            sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
            print(f"尝试绑定到: {mac_lower}:4")
            sock.bind((mac_lower, 4))
            print("✅ 绑定成功！")
            sock.close()
        except Exception as e:
            print(f"❌ 绑定失败: {e}")
    
    print("\n" + "=" * 50)
    print("测试完成")

def test_empty_binding():
    """测试空字符串绑定"""
    print("\n测试空字符串绑定（自动选择适配器）:")
    try:
        sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
        print("尝试绑定到: :4 (空字符串)")
        sock.bind(("", 4))
        print("✅ 空字符串绑定成功！")
        sock.close()
    except Exception as e:
        print(f"❌ 空字符串绑定失败: {e}")

if __name__ == "__main__":
    try:
        test_bluetooth_mac_format()
        test_empty_binding()
    except AttributeError:
        print("❌ 系统不支持蓝牙socket")
        print("请安装蓝牙库: pip install pybluez")
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}") 