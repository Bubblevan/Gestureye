#!/usr/bin/env python3
"""
简单的蓝牙RFCOMM服务器测试脚本
使用普通socket而不是pybluez库
参考dyn_gestures/connect/test_bluetooth_server.py的实现
"""

import socket
import threading
import json
import time

def start_bluetooth_server():
    """启动蓝牙RFCOMM服务器"""
    try:
        # 创建蓝牙RFCOMM socket
        server_sock = socket.socket(
            socket.AF_BLUETOOTH, 
            socket.SOCK_STREAM, 
            socket.BTPROTO_RFCOMM
        )
        
        # 绑定到本地任意可用的蓝牙适配器和RFCOMM端口4
        # 使用空字符串作为地址，系统会自动选择第一个可用的蓝牙设备
        host = ""  # 空字符串表示自动选择
        port = 4
        server_sock.bind((host, port))
        
        # 开始监听，1表示允许的最大挂起连接数为1
        server_sock.listen(1)
        
        print(f"[*] 蓝牙RFCOMM服务器已启动，监听端口 {port}...")
        print(f"[*] 等待客户端连接...")
        
        try:
            # 接受客户端连接
            # accept()会阻塞程序，直到有客户端连接进来
            client_sock, client_info = server_sock.accept()
            print(f"[+] 接受来自 {client_info[0]} 的连接")
            
            while True:
                # 从客户端接收数据，缓冲区大小为1024字节
                data = client_sock.recv(1024)
                if not data:
                    break
                
                # 将收到的字节解码为字符串并打印
                received_message = data.decode('utf-8')
                print(f"[*] 收到消息: {received_message}")
                
                # 尝试解析JSON数据
                try:
                    gesture_data = json.loads(received_message)
                    print(f"[*] 解析为JSON数据: {json.dumps(gesture_data, indent=2, ensure_ascii=False)}")
                except json.JSONDecodeError:
                    print(f"[*] 非JSON格式数据")
                
                # 构造回复消息并发送给客户端
                response = "服务器已收到你的消息"
                client_sock.sendall(response.encode('utf-8'))
                
        except KeyboardInterrupt:
            print("\n[!] 服务器被手动停止")
        except Exception as e:
            print(f"[!] 处理客户端连接时发生错误: {e}")
        finally:
            print("[-] 关闭套接字")
            if 'client_sock' in locals():
                client_sock.close()
            server_sock.close()
            
    except AttributeError:
        print("[!] 错误：系统不支持蓝牙socket连接")
        print("[!] 请安装蓝牙库，例如：pip install pybluez")
        print("[!] 或者检查socket模块是否支持AF_BLUETOOTH和BTPROTO_RFCOMM")
    except Exception as e:
        print(f"[!] 启动蓝牙服务器失败: {e}")

def test_bluetooth_client():
    """测试蓝牙客户端连接"""
    try:
        # 创建蓝牙客户端socket
        client_sock = socket.socket(
            socket.AF_BLUETOOTH, 
            socket.SOCK_STREAM, 
            socket.BTPROTO_RFCOMM
        )
        
        # 连接到服务器（需要替换为实际的MAC地址）
        server_mac = "XX:XX:XX:XX:XX:XX"  # 需要替换为实际的MAC地址
        port = 4
        
        print(f"[*] 尝试连接到蓝牙设备 {server_mac}:{port}...")
        client_sock.connect((server_mac, port))
        print(f"[+] 连接成功！")
        
        # 发送测试消息
        test_message = json.dumps({
            "gesture": "HandOpen",
            "hand_type": "right",
            "confidence": 85.5,
            "timestamp": time.time()
        })
        
        print(f"[*] 发送测试消息: {test_message}")
        client_sock.sendall(test_message.encode('utf-8'))
        
        # 接收响应
        data = client_sock.recv(1024)
        response = data.decode('utf-8')
        print(f"[*] 收到服务器响应: {response}")
        
        client_sock.close()
        
    except AttributeError:
        print("[!] 错误：系统不支持蓝牙socket连接")
    except Exception as e:
        print(f"[!] 蓝牙客户端测试失败: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "client":
        print("运行蓝牙客户端测试...")
        test_bluetooth_client()
    else:
        print("运行蓝牙服务器测试...")
        start_bluetooth_server() 