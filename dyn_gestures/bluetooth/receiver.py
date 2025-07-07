"""
蓝牙接收器 - PC端接收树莓派发送的手势数据
"""

import time
import threading
import socket
import struct
import json
from typing import Optional, Callable, Dict, Any
from PyQt6.QtCore import QObject, pyqtSignal

try:
    import bluetooth
    BLUETOOTH_AVAILABLE = True
except ImportError:
    BLUETOOTH_AVAILABLE = False
    print("警告: pybluez库未安装，蓝牙功能不可用")

from .protocol import BluetoothProtocol, PacketType, HandData, GestureData
import config


class BluetoothReceiver(QObject):
    """蓝牙接收器"""
    
    # Qt信号
    hand_data_received = pyqtSignal(object)  # HandData
    gesture_detected = pyqtSignal(object)   # GestureData 
    connection_status_changed = pyqtSignal(bool)  # 连接状态
    error_occurred = pyqtSignal(str)  # 错误信息
    
    def __init__(self):
        super().__init__()
        self.protocol = BluetoothProtocol()
        self.server_socket = None
        self.client_socket = None
        self.client_address = None
        self.running = False
        self.receive_thread = None
        self.heartbeat_thread = None
        self.last_heartbeat = 0
        self.buffer = b''
        self.connected = False
        
        # 从配置加载参数
        self.config = config.BLUETOOTH_CONFIG
        self.port = self.config['server_port']
        self.uuid = self.config['server_uuid']
        self.device_name = self.config['device_name']
        self.buffer_size = self.config['buffer_size']
        self.heartbeat_timeout = self.config['heartbeat_interval'] * 2
        
        # 检查蓝牙可用性
        if not BLUETOOTH_AVAILABLE:
            self.error_occurred.emit("蓝牙功能不可用：请安装pybluez库")
    
    def start_server(self) -> bool:
        """启动蓝牙服务器"""
        if not BLUETOOTH_AVAILABLE:
            self.error_occurred.emit("蓝牙功能不可用")
            return False
        
        try:
            # 创建RFCOMM套接字
            self.server_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            self.server_socket.bind(("", self.port))
            self.server_socket.listen(1)
            
            # 广告服务
            bluetooth.advertise_service(
                self.server_socket,
                self.device_name,
                service_id=self.uuid,
                service_classes=[self.uuid, bluetooth.SERIAL_PORT_CLASS],
                profiles=[bluetooth.SERIAL_PORT_PROFILE]
            )
            
            self.running = True
            
            # 启动接收线程
            self.receive_thread = threading.Thread(target=self._accept_connections, daemon=True)
            self.receive_thread.start()
            
            print(f"蓝牙服务器已启动，等待连接... (端口: {self.port})")
            return True
            
        except Exception as e:
            error_msg = f"启动蓝牙服务器失败: {e}"
            print(error_msg)
            self.error_occurred.emit(error_msg)
            return False
    
    def stop_server(self):
        """停止蓝牙服务器"""
        self.running = False
        
        if self.client_socket:
            try:
                self.client_socket.close()
            except:
                pass
            self.client_socket = None
        
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
            self.server_socket = None
        
        if self.connected:
            self.connected = False
            self.connection_status_changed.emit(False)
        
        print("蓝牙服务器已停止")
    
    def _accept_connections(self):
        """接受客户端连接"""
        while self.running:
            try:
                if not self.server_socket:
                    break
                
                print("等待蓝牙连接...")
                self.client_socket, self.client_address = self.server_socket.accept()
                
                print(f"客户端已连接: {self.client_address}")
                self.connected = True
                self.connection_status_changed.emit(True)
                self.last_heartbeat = time.time()
                
                # 启动心跳监控
                self.heartbeat_thread = threading.Thread(target=self._monitor_heartbeat, daemon=True)
                self.heartbeat_thread.start()
                
                # 处理客户端数据
                self._handle_client()
                
            except Exception as e:
                if self.running:
                    error_msg = f"接受连接失败: {e}"
                    print(error_msg)
                    self.error_occurred.emit(error_msg)
                    time.sleep(1)
    
    def _handle_client(self):
        """处理客户端数据"""
        self.buffer = b''
        
        while self.running and self.client_socket:
            try:
                # 接收数据
                data = self.client_socket.recv(self.buffer_size)
                if not data:
                    print("客户端断开连接")
                    break
                
                self.buffer += data
                
                # 处理缓冲区中的完整数据包
                self._process_buffer()
                
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    error_msg = f"接收数据失败: {e}"
                    print(error_msg)
                    self.error_occurred.emit(error_msg)
                break
        
        # 连接断开
        self._disconnect_client()
    
    def _process_buffer(self):
        """处理缓冲区中的数据包"""
        while len(self.buffer) >= 12:  # 最小包大小
            # 查找包头
            header_pos = -1
            for i in range(len(self.buffer) - 1):
                if struct.unpack('>H', self.buffer[i:i+2])[0] == self.protocol.HEADER:
                    header_pos = i
                    break
            
            if header_pos == -1:
                # 没有找到包头，清空缓冲区
                self.buffer = b''
                break
            
            # 移除包头前的数据
            if header_pos > 0:
                self.buffer = self.buffer[header_pos:]
            
            # 检查是否有足够的数据解析包头
            if len(self.buffer) < 8:
                break
            
            # 解析包头获取载荷长度
            try:
                header_data = struct.unpack('>HBBHH', self.buffer[:8])
                _, _, _, _, payload_length = header_data
            except struct.error:
                # 包头损坏，删除第一个字节继续查找
                self.buffer = self.buffer[1:]
                continue
            
            # 计算完整包大小
            full_packet_size = 8 + payload_length + 4  # 包头 + 载荷 + 校验和 + 包尾
            
            # 检查是否有完整的数据包
            if len(self.buffer) < full_packet_size:
                break
            
            # 提取完整数据包
            packet_data = self.buffer[:full_packet_size]
            self.buffer = self.buffer[full_packet_size:]
            
            # 解析数据包
            self._parse_packet(packet_data)
    
    def _parse_packet(self, packet_data: bytes):
        """解析数据包"""
        result = self.protocol.unpack_packet(packet_data)
        if not result:
            return
        
        packet_type, payload_data, sequence = result
        
        try:
            if packet_type == PacketType.HAND_LANDMARKS:
                hand_data = self.protocol.unpack_hand_data(payload_data)
                if hand_data:
                    self.hand_data_received.emit(hand_data)
            
            elif packet_type == PacketType.GESTURE_RESULT:
                gesture_data = self.protocol.unpack_gesture_data(payload_data)
                if gesture_data:
                    self.gesture_detected.emit(gesture_data)
            
            elif packet_type == PacketType.COMBINED_DATA:
                hand_data, gesture_data = self.protocol.unpack_combined_data(payload_data)
                if hand_data:
                    self.hand_data_received.emit(hand_data)
                if gesture_data:
                    self.gesture_detected.emit(gesture_data)
            
            elif packet_type == PacketType.HEARTBEAT:
                self.last_heartbeat = time.time()
                self._send_pong()
            
            elif packet_type == PacketType.PING:
                self._send_pong()
            
        except Exception as e:
            error_msg = f"处理数据包失败: {e}"
            print(error_msg)
            self.error_occurred.emit(error_msg)
    
    def _send_pong(self):
        """发送Pong回应"""
        if self.client_socket:
            try:
                pong_data = self.protocol.pack_pong()
                self.client_socket.send(pong_data)
            except Exception as e:
                print(f"发送Pong失败: {e}")
    
    def _monitor_heartbeat(self):
        """监控心跳"""
        while self.running and self.connected:
            current_time = time.time()
            if current_time - self.last_heartbeat > self.heartbeat_timeout:
                print("心跳超时，断开连接")
                self._disconnect_client()
                break
            time.sleep(1)
    
    def _disconnect_client(self):
        """断开客户端连接"""
        if self.client_socket:
            try:
                self.client_socket.close()
            except:
                pass
            self.client_socket = None
        
        if self.connected:
            self.connected = False
            self.connection_status_changed.emit(False)
            print("客户端连接已断开")
    
    def send_config_request(self):
        """发送配置请求"""
        if self.client_socket and self.connected:
            try:
                config_data = {
                    'request_type': 'get_config',
                    'timestamp': time.time()
                }
                packet = self.protocol._pack_packet(PacketType.CONFIG_REQUEST, 
                                                  json.dumps(config_data).encode('utf-8'))
                self.client_socket.send(packet)
            except Exception as e:
                error_msg = f"发送配置请求失败: {e}"
                print(error_msg)
                self.error_occurred.emit(error_msg)
    
    def is_connected(self) -> bool:
        """检查是否已连接"""
        return self.connected 