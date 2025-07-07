"""
蓝牙发送器 - 树莓派端发送手势数据到PC
"""

import time
import threading
import socket
from typing import Optional, List
from collections import deque

try:
    import bluetooth
    BLUETOOTH_AVAILABLE = True
except ImportError:
    BLUETOOTH_AVAILABLE = False
    print("警告: pybluez库未安装，蓝牙功能不可用")

from .protocol import BluetoothProtocol, PacketType, HandData, GestureData


class BluetoothSender:
    """蓝牙发送器 - 用于树莓派端"""
    
    def __init__(self, target_address: str, port: int = 1):
        self.protocol = BluetoothProtocol()
        self.target_address = target_address  # PC的蓝牙地址
        self.port = port
        self.socket = None
        self.connected = False
        self.running = False
        
        # 发送队列
        self.send_queue = deque(maxlen=100)
        self.send_thread = None
        self.heartbeat_thread = None
        
        # 检查蓝牙可用性
        if not BLUETOOTH_AVAILABLE:
            print("蓝牙功能不可用：请安装pybluez库")
    
    def connect(self) -> bool:
        """连接到PC端蓝牙服务器"""
        if not BLUETOOTH_AVAILABLE:
            print("蓝牙功能不可用")
            return False
        
        try:
            # 创建RFCOMM套接字
            self.socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            self.socket.connect((self.target_address, self.port))
            
            self.connected = True
            self.running = True
            
            # 启动发送线程
            self.send_thread = threading.Thread(target=self._send_worker, daemon=True)
            self.send_thread.start()
            
            # 启动心跳线程
            self.heartbeat_thread = threading.Thread(target=self._heartbeat_worker, daemon=True)
            self.heartbeat_thread.start()
            
            print(f"已连接到PC: {self.target_address}:{self.port}")
            return True
            
        except Exception as e:
            print(f"连接失败: {e}")
            self.disconnect()
            return False
    
    def disconnect(self):
        """断开连接"""
        self.running = False
        self.connected = False
        
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
        
        print("蓝牙连接已断开")
    
    def send_hand_landmarks(self, hand_data: HandData):
        """发送手部关键点数据"""
        if not self.connected:
            return
        
        packet = self.protocol.pack_hand_landmarks(hand_data)
        if packet:
            self._queue_packet(packet)
    
    def send_gesture_result(self, gesture_data: GestureData):
        """发送手势识别结果"""
        if not self.connected:
            return
        
        packet = self.protocol.pack_gesture_result(gesture_data)
        if packet:
            self._queue_packet(packet)
    
    def send_combined_data(self, hand_data: HandData, gesture_data: Optional[GestureData] = None):
        """发送组合数据"""
        if not self.connected:
            return
        
        packet = self.protocol.pack_combined_data(hand_data, gesture_data)
        if packet:
            self._queue_packet(packet)
    
    def _queue_packet(self, packet: bytes):
        """将数据包加入发送队列"""
        try:
            self.send_queue.append(packet)
        except Exception as e:
            print(f"加入发送队列失败: {e}")
    
    def _send_worker(self):
        """发送工作线程"""
        while self.running:
            try:
                if self.send_queue and self.socket:
                    packet = self.send_queue.popleft()
                    self.socket.send(packet)
                else:
                    time.sleep(0.01)  # 短暂等待
            except Exception as e:
                print(f"发送数据失败: {e}")
                if not self.running:
                    break
                time.sleep(0.1)
    
    def _heartbeat_worker(self):
        """心跳工作线程"""
        while self.running and self.connected:
            try:
                heartbeat_packet = self.protocol.pack_heartbeat()
                self._queue_packet(heartbeat_packet)
                time.sleep(5)  # 每5秒发送一次心跳
            except Exception as e:
                print(f"发送心跳失败: {e}")
                break
    
    def auto_discover_devices(self) -> List[str]:
        """自动发现附近的蓝牙设备"""
        if not BLUETOOTH_AVAILABLE:
            return []
        
        try:
            print("正在扫描蓝牙设备...")
            devices = bluetooth.discover_devices(duration=8, lookup_names=True)
            device_list = []
            
            for addr, name in devices:
                print(f"发现设备: {name} ({addr})")
                device_list.append(addr)
            
            return device_list
        except Exception as e:
            print(f"扫描蓝牙设备失败: {e}")
            return []
    
    def find_service_devices(self, service_uuid: str) -> List[str]:
        """查找提供特定服务的设备"""
        if not BLUETOOTH_AVAILABLE:
            return []
        
        try:
            services = bluetooth.find_service(uuid=service_uuid)
            device_addresses = [service['host'] for service in services]
            return device_addresses
        except Exception as e:
            print(f"查找服务设备失败: {e}")
            return []


# 用于树莓派端的便捷函数
def create_hand_data_from_landmarks(landmarks: List[List[int]], hand_id: str, hand_type: str) -> HandData:
    """从MediaPipe landmarks创建HandData对象"""
    from hand_utils import HandUtils
    
    # 转换为浮点数坐标
    float_landmarks = [[float(p[0]), float(p[1]), float(p[2]) if len(p) > 2 else 0.0] for p in landmarks]
    
    # 计算掌心和手掌长度
    palm_center = HandUtils.calculate_palm_center(landmarks)
    palm_length = HandUtils.calculate_palm_length(landmarks)
    
    return HandData(
        hand_id=hand_id,
        hand_type=hand_type,
        landmarks=float_landmarks,
        palm_center=(float(palm_center[0]), float(palm_center[1])),
        palm_length=float(palm_length),
        timestamp=time.time(),
        confidence=1.0  # 默认置信度
    )

def create_gesture_data_from_result(gesture_result: dict) -> GestureData:
    """从手势检测结果创建GestureData对象"""
    return GestureData(
        gesture_name=gesture_result['gesture'],
        hand_type=gesture_result['hand_type'],
        confidence=gesture_result.get('confidence', 0.0),
        timestamp=time.time(),
        details=gesture_result.get('details', {})
    ) 