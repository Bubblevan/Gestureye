"""
Socket 线程 - 负责在后台接收手势检测信息
"""

import socket
import threading
import json
from PyQt6.QtCore import QThread, pyqtSignal

import config


class SocketGestureReceiverThread(QThread):
    """Socket 手势接收线程"""
    gesture_detected = pyqtSignal(str, str, float)  # gesture_name, hand_type, confidence
    gesture_detail_detected = pyqtSignal(dict)  # 完整的手势数据字典
    client_connected = pyqtSignal(str)  # client address
    client_disconnected = pyqtSignal(str)  # client address
    status_updated = pyqtSignal(str)  # status message
    error_occurred = pyqtSignal(str)  # error message
    
    def __init__(self, host='192.168.31.247', port=65432):
        super().__init__()
        self.host = host
        self.port = port
        self.running = False
        self.server_socket = None
        self.client_connections = []
        
    def run(self):
        """运行 Socket 服务器"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            
            self.running = True
            self.status_updated.emit(f"Socket 服务器已在 {self.host}:{self.port} 启动")
            
            while self.running:
                try:
                    # 设置超时以便能够检查 running 状态
                    self.server_socket.settimeout(1.0)
                    conn, addr = self.server_socket.accept()
                    
                    if self.running:
                        # 为每个客户端创建处理线程
                        client_thread = threading.Thread(
                            target=self.handle_client_connection, 
                            args=(conn, addr)
                        )
                        client_thread.daemon = True
                        client_thread.start()
                        
                        self.client_connections.append(conn)
                        self.client_connected.emit(f"{addr[0]}:{addr[1]}")
                        
                except socket.timeout:
                    # 超时是正常的，继续循环
                    continue
                except Exception as e:
                    if self.running:
                        self.error_occurred.emit(f"接受连接时出错: {e}")
                        
        except Exception as e:
            self.error_occurred.emit(f"启动服务器失败: {e}")
        finally:
            self.cleanup()
    
    def handle_client_connection(self, conn, addr):
        """处理单个客户端连接"""
        addr_str = f"{addr[0]}:{addr[1]}"
        
        try:
            with conn:
                while self.running:
                    try:
                        # 设置接收超时
                        conn.settimeout(1.0)
                        data = conn.recv(1024)
                        
                        if not data:
                            break
                        
                        # 解析接收到的数据
                        self.parse_gesture_data(data.decode('utf-8'), addr_str)
                        
                        # 发送确认响应
                        response = "OK"
                        conn.sendall(response.encode('utf-8'))
                        
                    except socket.timeout:
                        # 超时是正常的，继续循环
                        continue
                    except Exception as e:
                        if self.running:
                            self.error_occurred.emit(f"处理客户端 {addr_str} 数据时出错: {e}")
                        break
                        
        except Exception as e:
            if self.running:
                self.error_occurred.emit(f"客户端 {addr_str} 连接处理出错: {e}")
        finally:
            self.client_disconnected.emit(addr_str)
            if conn in self.client_connections:
                self.client_connections.remove(conn)
    
    def parse_gesture_data(self, data_str, client_addr):
        """解析手势数据"""
        try:
            # 尝试解析 JSON 格式的数据
            try:
                data = json.loads(data_str)
                gesture_name = data.get('gesture', 'unknown')
                hand_type = data.get('hand_type', 'unknown')
                confidence = data.get('confidence', 0.0)
                gesture_type = data.get('gesture_type', 'static')  # 默认为静态手势
                details = data.get('details', {})
                timestamp = data.get('timestamp', 0)
                
                # 发送完整的手势数据
                self.gesture_detail_detected.emit(data)
                
                # 根据手势类型进行不同的处理
                if gesture_type == 'static':
                    # 静态手势处理
                    tag = details.get('tag', 'start')
                    if tag == 'start':
                        # 静态手势开始，发送手势检测信号
                        self.gesture_detected.emit(gesture_name, hand_type, confidence)
                        self.status_updated.emit(f"收到来自 {client_addr} 的静态手势: {gesture_name} (开始, 置信度: {confidence:.1f}%)")
                    elif tag == 'end':
                        # 静态手势结束，可以在这里处理手势结束逻辑
                        self.status_updated.emit(f"收到来自 {client_addr} 的静态手势: {gesture_name} (结束)")
                        
                elif gesture_type == 'dynamic':
                    # 动态手势处理
                    if 'tag' in details:
                        # 带轨迹追踪的动态手势
                        tag = details.get('tag', 'end')
                        dx = details.get('dx', 0)
                        dy = details.get('dy', 0)
                        
                        if tag == 'start':
                            self.status_updated.emit(f"收到来自 {client_addr} 的动态手势: {gesture_name} (开始)")
                        elif tag == 'end':
                            # 动态手势结束，发送手势检测信号
                            self.gesture_detected.emit(gesture_name, hand_type, confidence)
                            self.status_updated.emit(f"收到来自 {client_addr} 的动态手势: {gesture_name} (结束, dx:{dx}, dy:{dy}, 置信度: {confidence:.1f}%)")
                    else:
                        # 无轨迹追踪的动态手势，直接发送
                        self.gesture_detected.emit(gesture_name, hand_type, confidence)
                        self.status_updated.emit(f"收到来自 {client_addr} 的动态手势: {gesture_name} (置信度: {confidence:.1f}%)")
                        
            except json.JSONDecodeError:
                # 如果不是 JSON 格式，尝试解析简单的文本格式
                # 格式: "gesture_name,hand_type,confidence"
                parts = data_str.strip().split(',')
                if len(parts) >= 3:
                    gesture_name = parts[0]
                    hand_type = parts[1]
                    confidence = float(parts[2])
                else:
                    gesture_name = data_str.strip()
                    hand_type = 'unknown'
                    confidence = 0.0
                
                # 对于文本格式，直接发送手势检测信号
                self.gesture_detected.emit(gesture_name, hand_type, confidence)
                self.status_updated.emit(f"收到来自 {client_addr} 的手势: {gesture_name}")
            
        except Exception as e:
            self.error_occurred.emit(f"解析手势数据失败: {e}")
    
    def stop(self):
        """停止 Socket 服务器"""
        self.running = False
        
        # 关闭所有客户端连接
        for conn in self.client_connections.copy():
            try:
                conn.close()
            except:
                pass
        self.client_connections.clear()
        
        # 关闭服务器 socket
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        
        self.wait()
    
    def cleanup(self):
        """清理资源"""
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        self.status_updated.emit("Socket 服务器已关闭")
    
    def get_client_count(self):
        """获取连接的客户端数量"""
        return len(self.client_connections)
    
    def send_message_to_all_clients(self, message):
        """向所有客户端发送消息"""
        for conn in self.client_connections.copy():
            try:
                conn.sendall(message.encode('utf-8'))
            except:
                # 如果发送失败，移除这个连接
                if conn in self.client_connections:
                    self.client_connections.remove(conn)