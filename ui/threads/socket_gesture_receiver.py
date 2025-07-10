"""
Socket 线程 - 负责在后台接收手势检测信息
"""

import socket
import threading
import json
from PyQt6.QtCore import QThread, pyqtSignal

import config
from core.socket_server import SocketServer, GestureHandler


class SocketGestureReceiverThread(QThread):
    """Socket 手势接收线程"""
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
        
        # 使用新的Socket服务器和手势处理器
        self.socket_server = SocketServer(host, port)
        self.gesture_handler = GestureHandler()
        
        # 连接信号
        self.socket_server.gesture_received.connect(self.on_gesture_received)
        self.socket_server.client_connected.connect(self.client_connected.emit)
        self.socket_server.client_disconnected.connect(self.client_disconnected.emit)
        self.socket_server.server_status_changed.connect(self.status_updated.emit)
        
        self.gesture_handler.gesture_processed.connect(self.on_gesture_processed)
        
    def run(self):
        """运行 Socket 服务器"""
        try:
            self.running = True
            
            # 启动Socket服务器
            if self.socket_server.start_server():
                # 保持线程运行，直到停止
                while self.running:
                    self.msleep(100)  # 睡眠100毫秒
            else:
                self.error_occurred.emit("启动Socket服务器失败")
                        
        except Exception as e:
            self.error_occurred.emit(f"运行Socket服务器时出错: {e}")
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
    # 现在使用 SocketServer 和 GestureHandler 类来处理这些功能
    
    def stop(self):
        """停止 Socket 服务器"""
        self.running = False
        
        # 停止Socket服务器
        if self.socket_server:
            self.socket_server.stop_server()
        
        self.wait()
    
    def cleanup(self):
        """清理资源"""
        if self.socket_server:
            self.socket_server.stop_server()
        self.status_updated.emit("Socket 服务器已关闭")
    
    def get_client_count(self):
        """获取连接的客户端数量"""
        if self.socket_server:
            status = self.socket_server.get_status()
            return status.get('active_threads', 0)
        return 0
    
    def send_message_to_all_clients(self, message):
        """向所有客户端发送消息"""
        # 注意：新的Socket服务器实现目前不支持向客户端发送消息
        # 这是因为我们的协议是客户端向服务器发送数据，服务器只返回确认
        # 如果需要此功能，可以扩展SocketServer类
        self.status_updated.emit(f"发送消息功能暂不支持: {message}")