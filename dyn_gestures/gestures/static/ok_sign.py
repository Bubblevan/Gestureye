"""
OK手势检测器 - 检测拇指和食指形成圆圈的手势
"""

from typing import List, Dict, Any, Optional
import math
from ..base import StaticGestureDetector
from hand_utils import HandUtils


class OKSignDetector(StaticGestureDetector):
    """OK手势检测器"""
    
    def __init__(self, circle_threshold: float = 0.15, other_fingers_threshold: float = 0.6, required_frames: int = 15):
        super().__init__("OKSign", required_frames)
        self.circle_threshold = circle_threshold  # 圆圈检测阈值（相对于手掌基准长度）
        self.other_fingers_threshold = other_fingers_threshold  # 其他手指伸展阈值
    
    def detect(self, landmarks: List[List[int]], hand_id: str, hand_type: str) -> Optional[Dict[str, Any]]:
        """
        检测OK手势
        Args:
            landmarks: 手部关键点列表
            hand_id: 手部ID
            hand_type: 手部类型
        Returns:
            检测结果字典或None
        """
        if len(landmarks) < 21:
            return None
        
        # 计算手掌基准长度（手腕到中指根部）
        palm_length = HandUtils.calculate_palm_length(landmarks)
        
        # 检查拇指和食指是否形成圆圈
        thumb_tip = landmarks[4]  # 拇指尖
        index_tip = landmarks[8]  # 食指尖
        thumb_ip = landmarks[3]   # 拇指IP关节
        index_pip = landmarks[6]  # 食指PIP关节
        
        # 计算拇指和食指指尖的距离
        thumb_index_distance = HandUtils.calculate_distance(thumb_tip, index_tip)
        
        # 计算拇指IP到食指PIP的距离（作为圆圈参考）
        thumb_ip_to_index_pip = HandUtils.calculate_distance(thumb_ip, index_pip)
        
        # 检查是否形成圆圈（指尖距离小于阈值）
        circle_formed = thumb_index_distance < (palm_length * self.circle_threshold)
        
        # 检查其他手指是否伸直
        other_fingers_extended = self._check_other_fingers_extended(landmarks, palm_length)
        
        # 计算置信度
        confidence = self._calculate_confidence(thumb_index_distance, palm_length, other_fingers_extended)
        
        # 检查是否满足连续检测条件
        if circle_formed and other_fingers_extended:
            if self.check_continuous_detection(hand_id, "OKSign", confidence):
                return {
                    'gesture': 'OKSign',
                    'hand_type': hand_type,
                    'confidence': confidence,
                    'details': {
                        'thumb_index_distance': thumb_index_distance,
                        'palm_length': palm_length,
                        'circle_ratio': thumb_index_distance / palm_length
                    }
                }
        
        return None
    
    def _check_other_fingers_extended(self, landmarks: List[List[int]], palm_length: float) -> bool:
        """检查其他手指是否伸直"""
        # 检查中指、无名指、小指是否伸直
        middle_tip = landmarks[12]  # 中指尖
        ring_tip = landmarks[16]    # 无名指尖
        pinky_tip = landmarks[20]   # 小指尖
        
        middle_pip = landmarks[10]  # 中指PIP
        ring_pip = landmarks[14]    # 无名指PIP
        pinky_pip = landmarks[18]   # 小指PIP
        
        # 计算各手指的伸展距离
        middle_extension = HandUtils.calculate_distance(middle_tip, middle_pip)
        ring_extension = HandUtils.calculate_distance(ring_tip, ring_pip)
        pinky_extension = HandUtils.calculate_distance(pinky_tip, pinky_pip)
        
        # 检查是否超过阈值
        middle_extended = middle_extension > (palm_length * self.other_fingers_threshold)
        ring_extended = ring_extension > (palm_length * self.other_fingers_threshold)
        pinky_extended = pinky_extension > (palm_length * self.other_fingers_threshold)
        
        return middle_extended and ring_extended and pinky_extended
    
    def _calculate_confidence(self, thumb_index_distance: float, palm_length: float, other_fingers_extended: bool) -> float:
        """计算检测置信度"""
        # 基础置信度基于圆圈形成的程度
        circle_ratio = thumb_index_distance / palm_length
        base_confidence = max(0, 100 - (circle_ratio * 200))  # 距离越小，置信度越高
        
        # 其他手指伸直加分
        if other_fingers_extended:
            base_confidence += 20
        
        return min(100, base_confidence)
    
    def reset(self, hand_id: Optional[str] = None):
        """重置检测器状态"""
        super().reset(hand_id)
        self.reset_detection_history(hand_id)
    
    def get_display_message(self, gesture_result: Dict[str, Any]) -> str:
        """获取OK手势的显示消息"""
        hand_type = gesture_result['hand_type']
        confidence = gesture_result.get('confidence', 0)
        return f"{hand_type} Hand: OK Sign (Confidence: {confidence:.1f}%)" 