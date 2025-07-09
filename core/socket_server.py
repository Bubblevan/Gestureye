"""
Socket服务器模块 - 接收手势识别数据
"""

import socket
import threading
import json
import time
from typing import Optional, Callable, Dict, Any
from PyQt6.QtCore import QObject, pyqtSignal


class SocketServer(QObject):
    """Socket服务器类 - 接收手势识别数据并发送信号"""
    
    # PyQt6信号，用于将数据传递给主线程
    gesture_received = pyqtSignal(dict)  # 接收到手势数据
    client_connected = pyqtSignal(str)   # 客户端连接
    client_disconnected = pyqtSignal(str)  # 客户端断开连接
    server_status_changed = pyqtSignal(str)  # 服务器状态变化
    
    def __init__(self, host: str = "192.168.31.247", port: int = 65432):
        super().__init__()
        self.host = host
        self.port = port
        self.server_socket: Optional[socket.socket] = None
        self.is_running = False
        self.server_thread: Optional[threading.Thread] = None
        self.client_threads = []
        self.debug_mode = True
        
    def start_server(self) -> bool:
        """启动Socket服务器"""
        if self.is_running:
            self._emit_status("服务器已在运行")
            return True
            
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            
            self.is_running = True
            self.server_thread = threading.Thread(target=self._server_loop, daemon=True)
            self.server_thread.start()
            
            self._emit_status(f"Socket服务器已启动，监听 {self.host}:{self.port}")
            return True
            
        except Exception as e:
            self._emit_status(f"启动服务器失败: {e}")
            return False
    
    def stop_server(self):
        """停止Socket服务器"""
        if not self.is_running:
            return
            
        self.is_running = False
        
        # 关闭服务器套接字
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
            self.server_socket = None
            
        # 等待服务器线程结束
        if self.server_thread and self.server_thread.is_alive():
            self.server_thread.join(timeout=2)
            
        self._emit_status("Socket服务器已停止")
    
    def _server_loop(self):
        """服务器主循环"""
        while self.is_running and self.server_socket:
            try:
                # 设置短超时，以便能够响应停止信号
                self.server_socket.settimeout(1.0)
                client_socket, client_address = self.server_socket.accept()
                
                if self.is_running:
                    # 为每个客户端创建处理线程
                    client_thread = threading.Thread(
                        target=self._handle_client,
                        args=(client_socket, client_address),
                        daemon=True
                    )
                    client_thread.start()
                    self.client_threads.append(client_thread)
                    
                    self._emit_client_connected(f"{client_address[0]}:{client_address[1]}")
                    
            except socket.timeout:
                # 超时是正常的，继续循环
                continue
            except OSError:
                # 套接字被关闭，退出循环
                break
            except Exception as e:
                if self.is_running:
                    self._emit_status(f"服务器错误: {e}")
                break
    
    def _handle_client(self, client_socket: socket.socket, client_address):
        """处理客户端连接"""
        try:
            with client_socket:
                while self.is_running:
                    # 设置接收超时
                    client_socket.settimeout(1.0)
                    
                    try:
                        data = client_socket.recv(1024)
                        if not data:
                            break
                            
                        # 解码消息
                        message = data.decode('utf-8')
                        if self.debug_mode:
                            print(f"[SOCKET] 收到来自 {client_address} 的消息: {message}")
                        
                        # 尝试解析JSON数据
                        try:
                            gesture_data = json.loads(message)
                            # 发送信号到主线程
                            self.gesture_received.emit(gesture_data)
                        except json.JSONDecodeError:
                            # 如果不是JSON，作为普通文本处理
                            gesture_data = {
                                'type': 'text',
                                'message': message,
                                'timestamp': time.time(),
                                'client': f"{client_address[0]}:{client_address[1]}"
                            }
                            self.gesture_received.emit(gesture_data)
                        
                        # 发送确认响应
                        response = "数据已接收"
                        client_socket.sendall(response.encode('utf-8'))
                        
                    except socket.timeout:
                        # 接收超时，继续循环
                        continue
                    except ConnectionResetError:
                        # 客户端断开连接
                        break
                        
        except Exception as e:
            if self.debug_mode:
                print(f"[SOCKET] 处理客户端 {client_address} 时出错: {e}")
        finally:
            self._emit_client_disconnected(f"{client_address[0]}:{client_address[1]}")
    
    def _emit_status(self, message: str):
        """发送状态消息信号"""
        if self.debug_mode:
            print(f"[SOCKET] {message}")
        self.server_status_changed.emit(message)
    
    def _emit_client_connected(self, client_info: str):
        """发送客户端连接信号"""
        if self.debug_mode:
            print(f"[SOCKET] 客户端已连接: {client_info}")
        self.client_connected.emit(client_info)
    
    def _emit_client_disconnected(self, client_info: str):
        """发送客户端断开连接信号"""
        if self.debug_mode:
            print(f"[SOCKET] 客户端已断开: {client_info}")
        self.client_disconnected.emit(client_info)
    
    def get_status(self) -> Dict[str, Any]:
        """获取服务器状态"""
        return {
            'running': self.is_running,
            'host': self.host,
            'port': self.port,
            'active_threads': len([t for t in self.client_threads if t.is_alive()])
        }


class GestureHandler(QObject):
    """手势处理器 - 处理接收到的手势数据"""
    
    # 处理后的手势信号
    gesture_processed = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.gesture_history = []
        self.max_history = 100
        
    def handle_gesture_data(self, gesture_data: Dict[str, Any]):
        """处理手势数据"""
        try:
            # 添加处理时间戳
            processed_data = gesture_data.copy()
            processed_data['processed_timestamp'] = time.time()
            
            # 存储到历史记录
            self.gesture_history.append(processed_data)
            if len(self.gesture_history) > self.max_history:
                self.gesture_history.pop(0)
            
            # 判断数据类型 - 支持多种格式
            if 'gesture' in processed_data and 'gesture_type' in processed_data:
                # dyn_gestures项目的手势数据格式
                processed_data['type'] = 'gesture_detection'
                self._handle_gesture_detection(processed_data)
            elif processed_data.get('type') == 'gesture_detection':
                # 标准格式的手势数据
                self._handle_gesture_detection(processed_data)
            elif processed_data.get('type') == 'text':
                # 文本消息
                self._handle_text_message(processed_data)
            elif 'message' in processed_data:
                # 简单文本消息
                processed_data['type'] = 'text'
                self._handle_text_message(processed_data)
            else:
                # 未知格式
                self._handle_unknown_message(processed_data)
                
            # 发送处理后的数据
            self.gesture_processed.emit(processed_data)
            
        except Exception as e:
            print(f"[GESTURE_HANDLER] 处理手势数据时出错: {e}")
    
    def _handle_gesture_detection(self, data: Dict[str, Any]):
        """处理手势检测数据"""
        gesture_name = data.get('gesture', 'Unknown')
        hand_type = data.get('hand_type', 'Unknown')
        confidence = data.get('confidence', 0)
        
        print(f"[GESTURE] 检测到手势: {gesture_name} ({hand_type} 手, 置信度: {confidence})")
        
        # 这里可以添加具体的手势响应逻辑
        # 例如：执行对应的操作、更新UI等
        
    def _handle_text_message(self, data: Dict[str, Any]):
        """处理文本消息"""
        message = data.get('message', '')
        client = data.get('client', 'Unknown')
        
        print(f"[TEXT] 来自 {client} 的消息: {message}")
    
    def _handle_unknown_message(self, data: Dict[str, Any]):
        """处理未知类型消息"""
        print(f"[UNKNOWN] 收到未知类型数据: {data}")
    
    def get_gesture_history(self) -> list:
        """获取手势历史记录"""
        return self.gesture_history.copy()
    
    def clear_history(self):
        """清空历史记录"""
        self.gesture_history.clear() 