"""
通信接收线程 - 负责在后台接收手势检测信息 (支持Socket和Bluetooth)
"""

import socket
import threading
import json
import os
from PyQt6.QtCore import QThread, pyqtSignal

import config
from core.socket_server import SocketServer, BluetoothServer, GestureHandler


class SocketGestureReceiverThread(QThread):
    """通信接收线程 - 支持Socket和Bluetooth"""
    gesture_detected = pyqtSignal(str, str, float)  # gesture_name, hand_type, confidence
    gesture_detail_detected = pyqtSignal(dict)  # 完整的手势数据字典
    trail_change_detected = pyqtSignal(dict)  # 轨迹变化数据，包含dx, dy等信息
    client_connected = pyqtSignal(str)  # client address
    client_disconnected = pyqtSignal(str)  # client address
    status_updated = pyqtSignal(str)  # status message
    error_occurred = pyqtSignal(str)  # error message

    def __init__(self, host=config.SOCKET_SERVER_HOST, port=config.SOCKET_SERVER_PORT):
        super().__init__()
        self.host = host
        self.port = port
        self.running = False
        
        # 读取当前通信配置
        self.connection_type = self._read_connection_type()
        
        # 根据配置选择服务器类型
        self.server = None
        self.gesture_handler = GestureHandler()
        
        # 初始化服务器
        self._initialize_server()
        
        # 连接手势处理器信号
        self.gesture_handler.gesture_processed.connect(self.on_gesture_processed)
    
    def _read_connection_type(self) -> str:
        """读取project配置文件中的通信方式"""
        try:
            # 读取project/config.py文件
            config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config.py")
            
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 查找CONNECTION_TYPE配置行
            for line in content.split('\n'):
                if line.strip().startswith('CONNECTION_TYPE') and '=' in line:
                    # 提取配置值
                    value = line.split('=')[1].strip().strip("'\"")
                    return value
                    
            return 'socket'  # 默认值
            
        except Exception as e:
            print(f"读取通信配置失败: {e}")
            return 'socket'  # 默认值
    
    def _initialize_server(self):
        """根据配置初始化对应的服务器"""
        try:
            if self.connection_type == 'serial':  # serial对应蓝牙
                # 创建蓝牙服务器
                self.server = BluetoothServer(host="", port=4)  # 使用默认RFCOMM端口4
                self.status_updated.emit("初始化蓝牙RFCOMM服务器")
            else:
                # 创建Socket服务器 
                self.server = SocketServer(self.host, self.port)
                self.status_updated.emit("初始化TCP/IP Socket服务器")
            
            # 连接服务器信号
            if self.server:
                self.server.gesture_received.connect(self.on_gesture_received)
                self.server.client_connected.connect(self.client_connected.emit)
                self.server.client_disconnected.connect(self.client_disconnected.emit)
                self.server.server_status_changed.connect(self.status_updated.emit)
                
        except Exception as e:
            self.error_occurred.emit(f"初始化服务器失败: {e}")
            # 降级到Socket服务器
            self.server = SocketServer(self.host, self.port)
            self.server.gesture_received.connect(self.on_gesture_received)
            self.server.client_connected.connect(self.client_connected.emit)
            self.server.client_disconnected.connect(self.client_disconnected.emit)
            self.server.server_status_changed.connect(self.status_updated.emit)
        
    def run(self):
        """运行通信服务器 (Socket或Bluetooth)"""
        try:
            self.running = True
            
            # 启动对应的服务器
            if self.server and self.server.start_server():
                server_type = "蓝牙RFCOMM" if self.connection_type == 'serial' else "TCP/IP Socket"
                self.status_updated.emit(f"{server_type}服务器启动成功")
                
                # 保持线程运行，直到停止
                while self.running:
                    self.msleep(100)  # 睡眠100毫秒
            else:
                server_type = "蓝牙" if self.connection_type == 'serial' else "Socket"
                self.error_occurred.emit(f"启动{server_type}服务器失败")
                        
        except Exception as e:
            server_type = "蓝牙" if self.connection_type == 'serial' else "Socket"
            self.error_occurred.emit(f"运行{server_type}服务器时出错: {e}")
        finally:
            self.cleanup()
    
    def on_gesture_received(self, gesture_data):
        """处理收到的手势数据"""
        # 使用手势处理器处理数据
        self.gesture_handler.handle_gesture_data(gesture_data)
    
    def on_gesture_processed(self, processed_data):
        """处理已处理的手势数据"""
        try:
            gesture_type = processed_data.get('type', 'unknown')
            
            if gesture_type == 'gesture_detection':
                # 手势检测数据
                gesture_name = processed_data.get('gesture', 'unknown')
                hand_type = processed_data.get('hand_type', 'unknown')
                confidence = processed_data.get('confidence', 0.0)
                
                # 发送信号
                self.gesture_detected.emit(gesture_name, hand_type, confidence)
                self.gesture_detail_detected.emit(processed_data)
                
            elif gesture_type == 'trail_change':
                # 轨迹变化数据 - 新增处理
                self.trail_change_detected.emit(processed_data)
                
            elif gesture_type == 'text':
                # 文本消息
                self.status_updated.emit(f"收到文本消息: {processed_data.get('message', '')}")
            
        except Exception as e:
            self.error_occurred.emit(f"处理手势数据时出错: {e}")
    
# 注意：handle_client_connection 和 parse_gesture_data 方法已被移除
    # 现在使用 SocketServer/BluetoothServer 和 GestureHandler 类来处理这些功能
    
    def stop(self):
        """停止通信服务器"""
        self.running = False
        
        # 停止对应的服务器
        if self.server:
            self.server.stop_server()
        
        self.wait()
    
    def cleanup(self):
        """清理资源"""
        if self.server:
            self.server.stop_server()
        
        server_type = "蓝牙RFCOMM" if self.connection_type == 'serial' else "TCP/IP Socket"
        self.status_updated.emit(f"{server_type}服务器已关闭")
    
    def get_client_count(self):
        """获取连接的客户端数量"""
        if self.server:
            status = self.server.get_status()
            return status.get('active_threads', 0)
        return 0
    
    def send_message_to_all_clients(self, message):
        """向所有客户端发送消息"""
        # 注意：新的服务器实现目前不支持向客户端发送消息
        # 这是因为我们的协议是客户端向服务器发送数据，服务器只返回确认
        # 如果需要此功能，可以扩展服务器类
        self.status_updated.emit(f"发送消息功能暂不支持: {message}")
    
    def get_server_info(self) -> dict:
        """获取服务器信息"""
        if self.server:
            status = self.server.get_status()
            status['connection_type'] = self.connection_type
            status['display_name'] = 'Bluetooth (RFCOMM)' if self.connection_type == 'serial' else 'Socket (TCP/IP)'
            return status
        return {
            'running': False,
            'connection_type': self.connection_type,
            'display_name': 'Bluetooth (RFCOMM)' if self.connection_type == 'serial' else 'Socket (TCP/IP)'
        }