"""
滑动手势检测器 - 检测手背到手心的翻转滑动动作
"""

from typing import List, Dict, Any, Optional
import numpy as np
from ..base import DynamicGestureDetector
from hand_utils import HandUtils


class SwipeDetector(DynamicGestureDetector):
    """滑动手势检测器 - 基于手背到手心的翻转动作"""
    
    def __init__(self, history_length: int = 10, min_swipe_distance: float = 0.3, 
                 min_swipe_speed: float = 0.1, required_frames: int = 5,
                 palm_angle_threshold: float = 45.0):
        super().__init__("Swipe", history_length)
        self.min_swipe_distance = min_swipe_distance  # 最小滑动距离（相对于手掌基准长度）
        self.min_swipe_speed = min_swipe_speed  # 最小滑动速度
        self.required_frames = required_frames  # 需要连续检测的帧数
        self.palm_angle_threshold = palm_angle_threshold  # 手掌角度变化阈值（度）
        self.detection_history = {}  # 存储检测历史
    
    def detect(self, landmarks: List[List[int]], hand_id: str, hand_type: str) -> Optional[Dict[str, Any]]:
        """
        检测滑动手势 - 基于手背到手心的翻转动作
        Args:
            landmarks: 手部关键点列表
            hand_id: 手部ID
            hand_type: 手部类型
        Returns:
            检测结果字典或None
        """
        if len(landmarks) < 21:
            return None
        
        # 计算手掌中心位置和手掌角度
        palm_center = HandUtils.calculate_palm_center(landmarks)
        palm_angle = self._calculate_palm_angle(landmarks)
        
        # 初始化手部历史记录
        if hand_id not in self.history:
            self.history[hand_id] = {
                'positions': [], 
                'timestamps': [], 
                'angles': [],
                'palm_orientations': [],  # 记录手掌朝向（手心/手背）
                'landmarks': []  # 保存landmarks用于计算palm_length
            }
        
        # 添加当前位置、时间戳、角度和手掌朝向
        import time
        current_time = time.time()
        palm_orientation = self._detect_palm_orientation(landmarks)
        
        self.history[hand_id]['positions'].append(palm_center)
        self.history[hand_id]['timestamps'].append(current_time)
        self.history[hand_id]['angles'].append(palm_angle)
        self.history[hand_id]['palm_orientations'].append(palm_orientation)
        self.history[hand_id]['landmarks'].append(landmarks)
        
        # 保持历史记录长度
        if len(self.history[hand_id]['positions']) > self.history_length:
            self.history[hand_id]['positions'].pop(0)
            self.history[hand_id]['timestamps'].pop(0)
            self.history[hand_id]['angles'].pop(0)
            self.history[hand_id]['palm_orientations'].pop(0)
            self.history[hand_id]['landmarks'].pop(0)
        
        # 检查是否有足够的历史数据
        if len(self.history[hand_id]['positions']) < self.required_frames:
            return None
        
        # 分析翻转滑动动作
        swipe_result = self._analyze_flip_swipe(hand_id)
        
        if swipe_result:
            # 清空历史记录避免重复检测
            self.reset(hand_id)
            return {
                'gesture': f'Swipe{swipe_result["direction"]}',
                'hand_type': hand_type,
                'confidence': swipe_result['confidence'],
                'details': {
                    'direction': swipe_result['direction'],
                    'distance': swipe_result['distance'],
                    'speed': swipe_result['speed'],
                    'angle_change': swipe_result['angle_change'],
                    'flip_detected': swipe_result['flip_detected'],
                    'start_pos': swipe_result['start_pos'],
                    'end_pos': swipe_result['end_pos']
                }
            }
        
        return None
    
    def _analyze_flip_swipe(self, hand_id: str) -> Optional[Dict[str, Any]]:
        """分析翻转滑动动作"""
        positions = self.history[hand_id]['positions']
        timestamps = self.history[hand_id]['timestamps']
        angles = self.history[hand_id]['angles']
        orientations = self.history[hand_id]['palm_orientations']
        landmarks_history = self.history[hand_id]['landmarks']
        
        if len(positions) < 2 or len(landmarks_history) < 1:
            return None
        
        # 计算手掌基准长度（用于距离标准化）
        # 使用最新的landmarks来计算palm_length
        try:
            palm_length = HandUtils.calculate_palm_length(landmarks_history[-1])
        except (IndexError, TypeError) as e:
            # 如果计算失败，使用固定值作为fallback
            palm_length = 100.0
        
        # 计算总位移
        start_pos = positions[0]
        end_pos = positions[-1]
        
        dx = end_pos[0] - start_pos[0]  # X方向位移
        dy = end_pos[1] - start_pos[1]  # Y方向位移
        
        # 计算总距离
        total_distance = np.sqrt(dx**2 + dy**2)
        normalized_distance = total_distance / palm_length
        
        # 计算滑动时间
        swipe_time = timestamps[-1] - timestamps[0]
        if swipe_time <= 0:
            return None
        
        # 计算滑动速度
        swipe_speed = normalized_distance / swipe_time
        
        # 检查角度变化（翻转检测）
        angle_change = abs(angles[-1] - angles[0])
        flip_detected = angle_change > self.palm_angle_threshold
        
        # 检查手掌朝向变化
        orientation_change = self._check_orientation_change(orientations)
        
        # 检查是否满足翻转滑动条件
        if (normalized_distance < self.min_swipe_distance or 
            swipe_speed < self.min_swipe_speed or 
            not flip_detected or 
            not orientation_change):
            return None
        
        # 确定滑动方向
        direction = self._determine_direction(dx, dy)
        
        # 计算置信度
        confidence = self._calculate_confidence(normalized_distance, swipe_speed, angle_change)
        
        return {
            'direction': direction,
            'distance': normalized_distance,
            'speed': swipe_speed,
            'angle_change': angle_change,
            'flip_detected': flip_detected,
            'confidence': confidence,
            'start_pos': start_pos,
            'end_pos': end_pos
        }
    
    def _determine_direction(self, dx: float, dy: float) -> str:
        """确定滑动方向"""
        abs_dx = abs(dx)
        abs_dy = abs(dy)
        
        # 判断主要方向
        if abs_dx > abs_dy:
            # 水平滑动
            if dx > 0:
                return "Right"
            else:
                return "Left"
        else:
            # 垂直滑动
            if dy > 0:
                return "Down"
            else:
                return "Up"
    
    def _calculate_palm_angle(self, landmarks: List[List[int]]) -> float:
        """计算手掌角度（相对于水平方向）"""
        # 使用手腕和中指根部计算手掌方向
        wrist = landmarks[0]  # 手腕
        middle_mcp = landmarks[9]  # 中指根部
        
        # 计算手掌方向向量
        dx = middle_mcp[0] - wrist[0]
        dy = middle_mcp[1] - wrist[1]
        
        # 计算角度（弧度转度）
        angle = np.arctan2(dy, dx) * 180 / np.pi
        
        # 标准化到0-360度
        if angle < 0:
            angle += 360
            
        return angle
    
    def _detect_palm_orientation(self, landmarks: List[List[int]]) -> str:
        """检测手掌朝向（手心/手背）"""
        # 使用拇指和食指的位置关系判断手掌朝向
        thumb_tip = landmarks[4]  # 拇指尖
        index_tip = landmarks[8]  # 食指尖
        wrist = landmarks[0]      # 手腕
        
        # 计算拇指和食指相对于手腕的位置
        thumb_relative_x = thumb_tip[0] - wrist[0]
        index_relative_x = index_tip[0] - wrist[0]
        
        # 根据手部类型判断朝向
        # 对于右手：拇指在食指左侧为手心朝前，右侧为手背朝前
        # 对于左手：拇指在食指右侧为手心朝前，左侧为手背朝前
        
        # 这里简化处理，根据拇指和食指的相对位置判断
        if thumb_relative_x < index_relative_x:
            return "palm_up"  # 手心朝上
        else:
            return "palm_down"  # 手背朝上
    
    def _check_orientation_change(self, orientations: List[str]) -> bool:
        """检查手掌朝向是否发生变化"""
        if len(orientations) < 2:
            return False
        
        # 检查是否有朝向变化
        for i in range(1, len(orientations)):
            if orientations[i] != orientations[i-1]:
                return True
        
        return False
    
    def _calculate_confidence(self, distance: float, speed: float, angle_change: float) -> float:
        """计算滑动置信度"""
        # 基于距离、速度和角度变化计算置信度
        distance_score = min(100, (distance / self.min_swipe_distance) * 30)
        speed_score = min(100, (speed / self.min_swipe_speed) * 30)
        angle_score = min(100, (angle_change / self.palm_angle_threshold) * 40)
        
        return min(100, (distance_score + speed_score + angle_score) / 3)
    
    def reset(self, hand_id: Optional[str] = None):
        """重置检测器状态"""
        if hand_id is None:
            self.history.clear()
        elif hand_id in self.history:
            self.history[hand_id]['positions'].clear()
            self.history[hand_id]['timestamps'].clear()
            self.history[hand_id]['angles'].clear()
            self.history[hand_id]['palm_orientations'].clear()
            self.history[hand_id]['landmarks'].clear()
    
    def get_display_message(self, gesture_result: Dict[str, Any]) -> str:
        """获取翻转滑动手势的显示消息"""
        hand_type = gesture_result['hand_type']
        details = gesture_result.get('details', {})
        direction = details.get('direction', 'Unknown')
        confidence = gesture_result.get('confidence', 0)
        angle_change = details.get('angle_change', 0)
        return f"{hand_type} Hand: Flip Swipe {direction} (Angle: {angle_change:.1f}°, Conf: {confidence:.1f}%)" 