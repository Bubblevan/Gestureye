"""
树莓派端蓝牙发送示例 - 发送手势数据到PC
"""

import time
import sys
import os
import cv2
from typing import List, Dict, Any

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bluetooth.sender import BluetoothSender, create_hand_data_from_landmarks, create_gesture_data_from_result
from bluetooth.protocol import HandData, GestureData
from gesture_manager import GestureManager
from hand_utils import HandUtils

# 导入CVZone手势检测
try:
    from cvzone.HandTrackingModule import HandDetector
    CVZONE_AVAILABLE = True
except ImportError:
    CVZONE_AVAILABLE = False
    print("警告: CVZone库未安装，无法进行手势检测")


class RaspberryPiGestureSender:
    """树莓派端手势发送器"""
    
    def __init__(self, pc_bluetooth_address: str, port: int = 1):
        self.pc_address = pc_bluetooth_address
        self.port = port
        self.sender = BluetoothSender(pc_bluetooth_address, port)
        self.gesture_manager = GestureManager()
        
        # 摄像头和检测器
        self.cap = None
        self.detector = None
        self.running = False
        
        if CVZONE_AVAILABLE:
            self.setup_camera_and_detector()
    
    def setup_camera_and_detector(self):
        """设置摄像头和手势检测器"""
        try:
            # 初始化摄像头
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                print("无法打开摄像头")
                return
            
            # 初始化手部检测器
            self.detector = HandDetector(
                staticMode=False,
                maxHands=2,
                modelComplexity=1,
                detectionCon=0.5,
                minTrackCon=0.5
            )
            
            print("摄像头和检测器初始化成功")
        
        except Exception as e:
            print(f"初始化失败: {e}")
    
    def connect_to_pc(self) -> bool:
        """连接到PC"""
        print(f"正在连接到PC: {self.pc_address}:{self.port}")
        return self.sender.connect()
    
    def disconnect(self):
        """断开连接"""
        self.sender.disconnect()
        if self.cap:
            self.cap.release()
    
    def start_gesture_detection_and_send(self):
        """开始手势检测并发送数据"""
        if not CVZONE_AVAILABLE:
            print("CVZone不可用，无法进行手势检测")
            return
        
        if not self.cap or not self.detector:
            print("摄像头或检测器未初始化")
            return
        
        if not self.sender.connected:
            print("未连接到PC，请先建立蓝牙连接")
            return
        
        print("开始手势检测和数据发送...")
        print("按 'q' 键退出")
        
        self.running = True
        frame_count = 0
        
        while self.running:
            try:
                success, img = self.cap.read()
                if not success:
                    print("无法读取摄像头画面")
                    break
                
                # 左右翻转画面
                img = cv2.flip(img, 1)
                
                # 检测手部
                hands, img = self.detector.findHands(img, draw=True)
                
                if hands:
                    for i, hand in enumerate(hands):
                        hand_id = f"hand_{i}"
                        landmarks = hand["lmList"]
                        hand_type = hand["type"]
                        
                        # 创建手部数据
                        hand_data = create_hand_data_from_landmarks(landmarks, hand_id, hand_type)
                        
                        # 检测手势
                        detected_gestures = self.gesture_manager.detect_gestures(
                            landmarks, hand_id, hand_type
                        )
                        
                        # 发送数据
                        if detected_gestures:
                            # 如果检测到手势，发送组合数据
                            for gesture in detected_gestures:
                                gesture_data = create_gesture_data_from_result(gesture)
                                self.sender.send_combined_data(hand_data, gesture_data)
                                print(f"发送手势: {hand_type}手 - {gesture['gesture']} "
                                      f"(置信度: {gesture.get('confidence', 0):.1f}%)")
                        else:
                            # 只发送手部关键点数据
                            if frame_count % 5 == 0:  # 每5帧发送一次以减少数据量
                                self.sender.send_hand_landmarks(hand_data)
                                # print(f"发送手部数据: {hand_type}手")
                
                # 显示画面（可选）
                cv2.imshow('Raspberry Pi Gesture Detection', img)
                
                # 检查退出键
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("用户请求退出")
                    break
                
                frame_count += 1
                
            except KeyboardInterrupt:
                print("程序被中断")
                break
            except Exception as e:
                print(f"处理帧失败: {e}")
                continue
        
        self.running = False
        cv2.destroyAllWindows()
        print("手势检测已停止")
    
    def send_test_data(self):
        """发送测试数据"""
        if not self.sender.connected:
            print("未连接到PC")
            return
        
        print("发送测试数据...")
        
        # 创建测试手部数据
        test_landmarks = []
        for i in range(21):
            # 生成模拟的21个关键点
            x = 100 + (i % 5) * 20
            y = 100 + (i // 5) * 25
            z = 0.0
            test_landmarks.append([x, y, z])
        
        hand_data = HandData(
            hand_id="test_hand",
            hand_type="Right",
            landmarks=test_landmarks,
            palm_center=(150.0, 150.0),
            palm_length=80.0,
            timestamp=time.time(),
            confidence=0.95
        )
        
        # 创建测试手势数据
        gesture_data = GestureData(
            gesture_name="TestGesture",
            hand_type="Right",
            confidence=90.0,
            timestamp=time.time(),
            details={"test": True}
        )
        
        # 发送测试数据
        self.sender.send_combined_data(hand_data, gesture_data)
        print("测试数据已发送")
    
    def discover_pc_devices(self) -> List[str]:
        """扫描附近的PC设备"""
        print("扫描附近的蓝牙设备...")
        return self.sender.auto_discover_devices()


def main():
    """主函数"""
    print("树莓派蓝牙手势发送器")
    print("=" * 40)
    
    # PC的蓝牙地址（需要替换为实际地址）
    pc_bluetooth_address = "XX:XX:XX:XX:XX:XX"  # 替换为PC的蓝牙地址
    
    if pc_bluetooth_address == "XX:XX:XX:XX:XX:XX":
        print("请先设置PC的蓝牙地址!")
        print("可以通过以下方式获取PC蓝牙地址:")
        print("Windows: 设置 -> 设备 -> 蓝牙和其他设备 -> 更多蓝牙选项 -> 硬件")
        print("Linux: bluetoothctl -> show")
        return
    
    # 创建发送器
    sender = RaspberryPiGestureSender(pc_bluetooth_address)
    
    try:
        # 连接到PC
        if sender.connect_to_pc():
            print("连接成功!")
            
            # 选择模式
            print("\n选择模式:")
            print("1. 实时手势检测和发送")
            print("2. 发送测试数据")
            print("3. 扫描设备")
            
            choice = input("请输入选择 (1-3): ").strip()
            
            if choice == "1":
                sender.start_gesture_detection_and_send()
            elif choice == "2":
                sender.send_test_data()
            elif choice == "3":
                devices = sender.discover_pc_devices()
                print(f"发现 {len(devices)} 个设备")
            else:
                print("无效选择")
        else:
            print("连接失败!")
    
    except KeyboardInterrupt:
        print("\n程序被中断")
    finally:
        sender.disconnect()
        print("程序结束")


if __name__ == "__main__":
    main() 