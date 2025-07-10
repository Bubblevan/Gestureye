"""
拖拽功能测试脚本

模拟发送拖拽手势数据到 Gestureye 应用，测试窗口拖拽功能
"""

import socket
import json
import time
import sys


def send_gesture_data(host='192.168.31.247', port=65432, data=None):
    """发送手势数据到 Gestureye 应用"""
    try:
        # 创建 socket 连接
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))
        
        # 发送数据
        message = json.dumps(data)
        client_socket.sendall(message.encode('utf-8'))
        
        # 接收确认
        response = client_socket.recv(1024).decode('utf-8')
        print(f"服务器响应: {response}")
        
        client_socket.close()
        return True
        
    except Exception as e:
        print(f"发送数据失败: {e}")
        return False


def test_window_drag():
    """测试窗口拖拽功能"""
    print("=== 窗口拖拽功能测试 ===")
    
    # 测试数据序列
    test_gestures = [
        {
            "description": "向右拖拽窗口 100px",
            "data": {
                "type": "gesture_detection",
                "gesture": "DragGesture",
                "hand_type": "Right",
                "confidence": 95.0,
                "gesture_type": "dynamic",
                "timestamp": time.time(),
                "details": {
                    "tag": "end",
                    "dx": 100,
                    "dy": 0
                }
            }
        },
        {
            "description": "向下拖拽窗口 80px",
            "data": {
                "type": "gesture_detection",
                "gesture": "DragGesture", 
                "hand_type": "Right",
                "confidence": 92.0,
                "gesture_type": "dynamic",
                "timestamp": time.time(),
                "details": {
                    "tag": "end",
                    "dx": 0,
                    "dy": 80
                }
            }
        },
        {
            "description": "对角线拖拽窗口",
            "data": {
                "type": "gesture_detection",
                "gesture": "HandMove",
                "hand_type": "Right", 
                "confidence": 88.0,
                "gesture_type": "dynamic",
                "timestamp": time.time(),
                "details": {
                    "tag": "end",
                    "dx": -50,
                    "dy": -40
                }
            }
        }
    ]
    
    for i, gesture in enumerate(test_gestures, 1):
        print(f"\n测试 {i}: {gesture['description']}")
        success = send_gesture_data(data=gesture['data'])
        
        if success:
            print("✓ 数据发送成功")
        else:
            print("✗ 数据发送失败")
        
        # 等待操作完成
        time.sleep(2)


def test_window_operations():
    """测试其他窗口操作"""
    print("\n=== 其他窗口操作测试 ===")
    
    operations = [
        {
            "description": "最大化窗口",
            "gesture": "HandOpen"
        },
        {
            "description": "窗口居中", 
            "gesture": "DoubleTap"
        },
        {
            "description": "窗口左贴靠",
            "gesture": "SwipeLeft"
        },
        {
            "description": "最小化窗口",
            "gesture": "HandClose"
        }
    ]
    
    for operation in operations:
        print(f"\n测试: {operation['description']}")
        
        data = {
            "type": "gesture_detection",
            "gesture": operation['gesture'],
            "hand_type": "Right",
            "confidence": 95.0,
            "gesture_type": "dynamic",
            "timestamp": time.time(),
            "details": {
                "tag": "end"
            }
        }
        
        success = send_gesture_data(data=data)
        
        if success:
            print("✓ 操作发送成功")
        else:
            print("✗ 操作发送失败")
        
        time.sleep(2)


def test_continuous_drag():
    """测试连续拖拽"""
    print("\n=== 连续拖拽测试 ===")
    
    # 模拟连续的小幅拖拽
    drag_sequence = [
        (10, 0, "小步向右"),
        (0, 10, "小步向下"), 
        (-10, 0, "小步向左"),
        (0, -10, "小步向上"),
        (20, 20, "对角线移动")
    ]
    
    for dx, dy, desc in drag_sequence:
        print(f"执行: {desc} (dx={dx}, dy={dy})")
        
        data = {
            "type": "gesture_detection",
            "gesture": "HandMove",
            "hand_type": "Right",
            "confidence": 90.0,
            "gesture_type": "dynamic", 
            "timestamp": time.time(),
            "details": {
                "tag": "end",
                "dx": dx,
                "dy": dy
            }
        }
        
        send_gesture_data(data=data)
        time.sleep(1)


def main():
    """主测试函数"""
    print("Gestureye 拖拽功能测试工具")
    print("=" * 50)
    print("确保 Gestureye 应用正在运行并监听 Socket 连接")
    print("测试将发送各种手势数据来验证拖拽功能")
    
    # 检查连接
    print("\n检查连接...")
    test_data = {
        "type": "text",
        "message": "测试连接",
        "timestamp": time.time()
    }
    
    if not send_gesture_data(data=test_data):
        print("无法连接到 Gestureye 应用，请检查:")
        print("1. 应用是否正在运行")
        print("2. Socket 服务器是否已启动")
        print("3. IP 地址和端口是否正确")
        return
    
    print("✓ 连接成功!")
    
    # 等待用户确认
    input("\n请确保有一个窗口处于活动状态，然后按回车键开始测试...")
    
    try:
        # 运行测试
        test_window_drag()
        test_window_operations()
        test_continuous_drag()
        
        print("\n" + "=" * 50)
        print("所有测试完成!")
        print("如果窗口成功移动，说明拖拽功能工作正常")
        
    except KeyboardInterrupt:
        print("\n测试被用户中断")
    except Exception as e:
        print(f"\n测试过程中出现错误: {e}")
    
    input("\n按回车键退出...")


if __name__ == "__main__":
    main()
