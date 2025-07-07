"""
手势检测线程 - 负责在后台进行手势检测
"""

import cv2
import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal

from gesture_manager import GestureManager
from hand_utils import HandUtils
import config


class GestureDetectionThread(QThread):
    """手势检测线程"""
    gesture_detected = pyqtSignal(str, str, float)  # gesture_name, hand_type, confidence
    frame_processed = pyqtSignal(np.ndarray)  # processed frame
    status_updated = pyqtSignal(str)  # status message
    
    def __init__(self):
        super().__init__()
        self.running = False
        self.cap = None
        self.detector = None
        self.gesture_manager = None
        
    def run(self):
        """运行检测线程"""
        try:
            # 初始化摄像头
            self.cap = cv2.VideoCapture(config.CAMERA_INDEX)
            if not self.cap.isOpened():
                self.status_updated.emit("无法打开摄像头")
                return
                
            # 初始化手部检测器
            from cvzone.HandTrackingModule import HandDetector
            self.detector = HandDetector(
                staticMode=config.HAND_DETECTION_CONFIG['static_mode'],
                maxHands=config.HAND_DETECTION_CONFIG['max_hands'],
                modelComplexity=config.HAND_DETECTION_CONFIG['model_complexity'],
                detectionCon=config.HAND_DETECTION_CONFIG['detection_confidence'],
                minTrackCon=config.HAND_DETECTION_CONFIG['min_tracking_confidence']
            )
            
            # 初始化手势管理器
            self.gesture_manager = GestureManager()
            
            self.status_updated.emit("手势检测已启动")
            
            while self.running:
                success, img = self.cap.read()
                if not success:
                    continue
                
                # 处理帧
                img = self.process_frame(img)
                
                # 发送处理后的帧
                self.frame_processed.emit(img)
                
        except Exception as e:
            self.status_updated.emit(f"检测线程错误: {e}")
        finally:
            if self.cap:
                self.cap.release()
    
    def process_frame(self, img):
        """处理单帧图像"""
        # 左右翻转摄像头画面
        if config.DISPLAY_CONFIG['flip_image']:
            img = cv2.flip(img, 1)
        
        # 检测手部
        hands, img = self.detector.findHands(
            img, 
            draw=config.DISPLAY_CONFIG['show_landmarks'], 
            flipType=not config.DISPLAY_CONFIG['flip_image']
        )
        
        if hands:
            for i, hand in enumerate(hands):
                hand_id = f"hand_{i}"
                landmarks = hand["lmList"]
                hand_type = hand["type"]
                
                # 使用手势管理器检测手势
                detected_gestures = self.gesture_manager.detect_gestures(
                    landmarks, hand_id, hand_type
                )

                if detected_gestures:
                    # 发送检测到的手势
                    for gesture in detected_gestures:
                        self.gesture_detected.emit(
                            gesture['gesture'],
                            gesture['hand_type'],
                            gesture.get('confidence', 0)
                        )
                
                # 绘制手部信息
                self.draw_hand_info(img, hand, i)
        else:
            # 没有检测到手时，重置检测历史
            self.gesture_manager.on_all_hands_lost()
        
        return img
    
    def draw_hand_info(self, img, hand, hand_index):
        """绘制手部信息"""
        landmarks = hand["lmList"]
        hand_type = hand["type"]
        
        # 计算并绘制手掌中心
        palm_center = HandUtils.calculate_palm_center(landmarks)
        if config.DISPLAY_CONFIG['show_palm_center']:
            HandUtils.draw_palm_center(img, palm_center, config.COLORS['palm_center'])
        
        # 计算手指数量
        fingers = self.detector.fingersUp(hand)
        finger_count = fingers.count(1)
        
        # 准备显示信息
        info_dict = {
            'Fingers': finger_count,
            'Palm': f'({palm_center[0]}, {palm_center[1]})'
        }
        
        # 绘制信息
        HandUtils.draw_text_info(
            img, hand_type, info_dict, 
            position_offset=hand_index * 120
        )
    
    def stop(self):
        """停止检测线程"""
        self.running = False
        self.wait() 