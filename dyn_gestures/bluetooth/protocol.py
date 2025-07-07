"""
蓝牙通信协议定义
"""

import struct
import json
import time
import hashlib
from enum import IntEnum
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass


class PacketType(IntEnum):
    """数据包类型"""
    HAND_LANDMARKS = 0x01      # 手部关键点数据
    GESTURE_RESULT = 0x02      # 手势识别结果
    COMBINED_DATA = 0x03       # 组合数据（关键点+手势）
    HEARTBEAT = 0x04           # 心跳包
    CONFIG_REQUEST = 0x05      # 配置请求
    STATUS_REPORT = 0x06       # 状态报告
    PING = 0x07               # Ping包
    PONG = 0x08               # Pong回应


@dataclass
class HandData:
    """手部数据结构"""
    hand_id: str                    # 手部ID
    hand_type: str                  # "Left" 或 "Right"
    landmarks: List[List[float]]    # 21个关键点坐标 [x, y, z]
    palm_center: Tuple[float, float]  # 掌心坐标 (x, y)
    palm_length: float              # 手掌基准长度
    timestamp: float                # 时间戳
    confidence: float               # 检测置信度


@dataclass 
class GestureData:
    """手势数据结构"""
    gesture_name: str               # 手势名称
    hand_type: str                  # "Left" 或 "Right"
    confidence: float               # 置信度
    timestamp: float                # 时间戳
    details: Dict[str, Any]         # 详细信息


class BluetoothProtocol:
    """蓝牙通信协议处理器"""
    
    # 协议常量
    HEADER = 0xAA55
    FOOTER = 0x55AA
    PROTOCOL_VERSION = 0x01
    MAX_PACKET_SIZE = 4096
    
    def __init__(self):
        self.sequence_number = 0
    
    def _next_sequence(self) -> int:
        """获取下一个序列号"""
        self.sequence_number = (self.sequence_number + 1) % 0xFFFF
        return self.sequence_number
    
    def _calculate_checksum(self, data: bytes) -> int:
        """计算校验和"""
        return sum(data) & 0xFFFF
    
    def pack_hand_landmarks(self, hand_data: HandData) -> bytes:
        """打包手部关键点数据"""
        try:
            # 构建数据负载
            payload_data = {
                'hand_id': hand_data.hand_id,
                'hand_type': hand_data.hand_type,
                'landmarks': hand_data.landmarks,
                'palm_center': hand_data.palm_center,
                'palm_length': hand_data.palm_length,
                'timestamp': hand_data.timestamp,
                'confidence': hand_data.confidence
            }
            
            payload_json = json.dumps(payload_data, separators=(',', ':'))
            payload_bytes = payload_json.encode('utf-8')
            
            return self._pack_packet(PacketType.HAND_LANDMARKS, payload_bytes)
        
        except Exception as e:
            print(f"打包手部关键点数据失败: {e}")
            return b''
    
    def pack_gesture_result(self, gesture_data: GestureData) -> bytes:
        """打包手势识别结果"""
        try:
            payload_data = {
                'gesture_name': gesture_data.gesture_name,
                'hand_type': gesture_data.hand_type,
                'confidence': gesture_data.confidence,
                'timestamp': gesture_data.timestamp,
                'details': gesture_data.details
            }
            
            payload_json = json.dumps(payload_data, separators=(',', ':'))
            payload_bytes = payload_json.encode('utf-8')
            
            return self._pack_packet(PacketType.GESTURE_RESULT, payload_bytes)
        
        except Exception as e:
            print(f"打包手势结果失败: {e}")
            return b''
    
    def pack_combined_data(self, hand_data: HandData, gesture_data: Optional[GestureData] = None) -> bytes:
        """打包组合数据（手部关键点+手势结果）"""
        try:
            payload_data = {
                'hand_data': {
                    'hand_id': hand_data.hand_id,
                    'hand_type': hand_data.hand_type,
                    'landmarks': hand_data.landmarks,
                    'palm_center': hand_data.palm_center,
                    'palm_length': hand_data.palm_length,
                    'timestamp': hand_data.timestamp,
                    'confidence': hand_data.confidence
                },
                'gesture_data': None
            }
            
            if gesture_data:
                payload_data['gesture_data'] = {
                    'gesture_name': gesture_data.gesture_name,
                    'hand_type': gesture_data.hand_type,
                    'confidence': gesture_data.confidence,
                    'timestamp': gesture_data.timestamp,
                    'details': gesture_data.details
                }
            
            payload_json = json.dumps(payload_data, separators=(',', ':'))
            payload_bytes = payload_json.encode('utf-8')
            
            return self._pack_packet(PacketType.COMBINED_DATA, payload_bytes)
        
        except Exception as e:
            print(f"打包组合数据失败: {e}")
            return b''
    
    def pack_heartbeat(self) -> bytes:
        """打包心跳包"""
        payload_data = {
            'timestamp': time.time(),
            'status': 'alive'
        }
        payload_json = json.dumps(payload_data, separators=(',', ':'))
        payload_bytes = payload_json.encode('utf-8')
        
        return self._pack_packet(PacketType.HEARTBEAT, payload_bytes)
    
    def pack_ping(self) -> bytes:
        """打包Ping包"""
        payload_data = {
            'timestamp': time.time(),
            'message': 'ping'
        }
        payload_json = json.dumps(payload_data, separators=(',', ':'))
        payload_bytes = payload_json.encode('utf-8')
        
        return self._pack_packet(PacketType.PING, payload_bytes)
    
    def pack_pong(self) -> bytes:
        """打包Pong包"""
        payload_data = {
            'timestamp': time.time(),
            'message': 'pong'
        }
        payload_json = json.dumps(payload_data, separators=(',', ':'))
        payload_bytes = payload_json.encode('utf-8')
        
        return self._pack_packet(PacketType.PONG, payload_bytes)
    
    def _pack_packet(self, packet_type: PacketType, payload: bytes) -> bytes:
        """打包数据包"""
        try:
            # 包头：HEADER(2) + VERSION(1) + TYPE(1) + SEQUENCE(2) + LENGTH(2) = 8字节
            sequence = self._next_sequence()
            payload_length = len(payload)
            
            if payload_length > self.MAX_PACKET_SIZE - 12:  # 8字节包头 + 2字节校验和 + 2字节包尾
                raise ValueError(f"数据包过大: {payload_length}")
            
            # 构建包头
            header = struct.pack('>HBBHH', 
                self.HEADER,
                self.PROTOCOL_VERSION,
                packet_type,
                sequence,
                payload_length
            )
            
            # 计算校验和（包含包头和载荷）
            packet_data = header + payload
            checksum = self._calculate_checksum(packet_data)
            
            # 添加校验和和包尾
            footer = struct.pack('>HH', checksum, self.FOOTER)
            
            return packet_data + footer
        
        except Exception as e:
            print(f"打包数据包失败: {e}")
            return b''
    
    def unpack_packet(self, data: bytes) -> Optional[Tuple[PacketType, Dict[str, Any], int]]:
        """解包数据包
        
        Returns:
            (packet_type, payload_data, sequence) 或 None
        """
        try:
            if len(data) < 12:  # 最小包大小
                return None
            
            # 解析包头
            header_data = struct.unpack('>HBBHH', data[:8])
            header, version, packet_type, sequence, payload_length = header_data
            
            # 验证包头
            if header != self.HEADER or version != self.PROTOCOL_VERSION:
                print(f"无效的包头或版本: {header:04X}, {version}")
                return None
            
            # 检查数据包长度
            expected_total_length = 8 + payload_length + 4  # 包头 + 载荷 + 校验和 + 包尾
            if len(data) < expected_total_length:
                print(f"数据包长度不足: {len(data)} < {expected_total_length}")
                return None
            
            # 提取载荷
            payload = data[8:8+payload_length]
            
            # 提取校验和和包尾
            footer_data = struct.unpack('>HH', data[8+payload_length:8+payload_length+4])
            received_checksum, footer = footer_data
            
            # 验证包尾
            if footer != self.FOOTER:
                print(f"无效的包尾: {footer:04X}")
                return None
            
            # 验证校验和
            packet_for_checksum = data[:8+payload_length]
            calculated_checksum = self._calculate_checksum(packet_for_checksum)
            if received_checksum != calculated_checksum:
                print(f"校验和错误: {received_checksum:04X} != {calculated_checksum:04X}")
                return None
            
            # 解析载荷
            try:
                payload_str = payload.decode('utf-8')
                payload_data = json.loads(payload_str)
            except (UnicodeDecodeError, json.JSONDecodeError) as e:
                print(f"载荷解析失败: {e}")
                return None
            
            return (PacketType(packet_type), payload_data, sequence)
        
        except Exception as e:
            print(f"解包数据包失败: {e}")
            return None
    
    def unpack_hand_data(self, payload_data: Dict[str, Any]) -> Optional[HandData]:
        """从载荷数据解包手部数据"""
        try:
            return HandData(
                hand_id=payload_data['hand_id'],
                hand_type=payload_data['hand_type'],
                landmarks=payload_data['landmarks'],
                palm_center=tuple(payload_data['palm_center']),
                palm_length=payload_data['palm_length'],
                timestamp=payload_data['timestamp'],
                confidence=payload_data['confidence']
            )
        except (KeyError, ValueError) as e:
            print(f"解包手部数据失败: {e}")
            return None
    
    def unpack_gesture_data(self, payload_data: Dict[str, Any]) -> Optional[GestureData]:
        """从载荷数据解包手势数据"""
        try:
            return GestureData(
                gesture_name=payload_data['gesture_name'],
                hand_type=payload_data['hand_type'],
                confidence=payload_data['confidence'],
                timestamp=payload_data['timestamp'],
                details=payload_data.get('details', {})
            )
        except (KeyError, ValueError) as e:
            print(f"解包手势数据失败: {e}")
            return None
    
    def unpack_combined_data(self, payload_data: Dict[str, Any]) -> Tuple[Optional[HandData], Optional[GestureData]]:
        """从载荷数据解包组合数据"""
        hand_data = None
        gesture_data = None
        
        if 'hand_data' in payload_data and payload_data['hand_data']:
            hand_data = self.unpack_hand_data(payload_data['hand_data'])
        
        if 'gesture_data' in payload_data and payload_data['gesture_data']:
            gesture_data = self.unpack_gesture_data(payload_data['gesture_data'])
        
        return hand_data, gesture_data 