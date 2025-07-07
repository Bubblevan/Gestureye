"""
蓝牙管理器 - 集成蓝牙通信到手势检测系统
"""

from typing import Optional, Dict, Any, List
from PyQt6.QtCore import QObject, pyqtSignal

from .receiver import BluetoothReceiver
from .protocol import HandData, GestureData
from gesture_manager import GestureManager
from hand_utils import HandUtils
from core.action_executor import ActionExecutor
from core.gesture_bindings import GestureBindings
import config


class BluetoothManager(QObject):
    """蓝牙管理器 - 处理蓝牙接收的数据并执行相应动作"""
    
    # Qt信号
    bluetooth_gesture_detected = pyqtSignal(str, str, float)  # gesture_name, hand_type, confidence
    bluetooth_hand_data_received = pyqtSignal(object)  # HandData
    bluetooth_status_changed = pyqtSignal(bool)  # 蓝牙连接状态
    log_message = pyqtSignal(str)  # 日志消息
    
    def __init__(self):
        super().__init__()
        self.receiver = None
        self.gesture_manager = None
        self.action_executor = None
        self.gesture_bindings = None
        self.enabled = config.BLUETOOTH_CONFIG['enabled']
        self.auto_gesture_detection = config.BLUETOOTH_CONFIG['auto_gesture_detection']
        
        if self.enabled:
            self.setup_bluetooth()
            self.setup_gesture_system()
    
    def setup_bluetooth(self):
        """设置蓝牙接收器"""
        try:
            self.receiver = BluetoothReceiver()
            
            # 连接信号
            self.receiver.hand_data_received.connect(self.on_hand_data_received)
            self.receiver.gesture_detected.connect(self.on_gesture_detected)
            self.receiver.connection_status_changed.connect(self.on_connection_status_changed)
            self.receiver.error_occurred.connect(self.on_error_occurred)
            
            self.log_message.emit("蓝牙管理器已初始化")
        except Exception as e:
            self.log_message.emit(f"蓝牙初始化失败: {e}")
    
    def setup_gesture_system(self):
        """设置手势识别系统"""
        if self.auto_gesture_detection:
            self.gesture_manager = GestureManager()
            
        self.action_executor = ActionExecutor()
        self.gesture_bindings = GestureBindings()
    
    def start_bluetooth_server(self) -> bool:
        """启动蓝牙服务器"""
        if not self.enabled or not self.receiver:
            self.log_message.emit("蓝牙功能未启用或未初始化")
            return False
        
        success = self.receiver.start_server()
        if success:
            self.log_message.emit("蓝牙服务器启动成功")
        else:
            self.log_message.emit("蓝牙服务器启动失败")
        
        return success
    
    def stop_bluetooth_server(self):
        """停止蓝牙服务器"""
        if self.receiver:
            self.receiver.stop_server()
            self.log_message.emit("蓝牙服务器已停止")
    
    def on_hand_data_received(self, hand_data: HandData):
        """处理接收到的手部数据"""
        try:
            self.bluetooth_hand_data_received.emit(hand_data)
            self.log_message.emit(f"接收到手部数据: {hand_data.hand_type}手 (置信度: {hand_data.confidence:.2f})")
            
            # 如果启用自动手势检测，使用本地手势管理器处理
            if self.auto_gesture_detection and self.gesture_manager:
                # 转换手部数据为int格式的landmarks
                int_landmarks = [[int(p[0]), int(p[1]), int(p[2])] for p in hand_data.landmarks]
                
                # 检测手势
                detected_gestures = self.gesture_manager.detect_gestures(
                    int_landmarks, hand_data.hand_id, hand_data.hand_type
                )
                
                # 处理检测到的手势
                for gesture in detected_gestures:
                    self._execute_gesture_action(gesture)
        
        except Exception as e:
            self.log_message.emit(f"处理手部数据失败: {e}")
    
    def on_gesture_detected(self, gesture_data: GestureData):
        """处理接收到的手势数据"""
        try:
            self.bluetooth_gesture_detected.emit(
                gesture_data.gesture_name, 
                gesture_data.hand_type, 
                gesture_data.confidence
            )
            
            self.log_message.emit(
                f"接收到手势: {gesture_data.hand_type}手 - {gesture_data.gesture_name} "
                f"(置信度: {gesture_data.confidence:.1f}%)"
            )
            
            # 执行手势对应的动作
            gesture_result = {
                'gesture': gesture_data.gesture_name,
                'hand_type': gesture_data.hand_type,
                'confidence': gesture_data.confidence,
                'details': gesture_data.details
            }
            
            self._execute_gesture_action(gesture_result)
        
        except Exception as e:
            self.log_message.emit(f"处理手势数据失败: {e}")
    
    def _execute_gesture_action(self, gesture_result: Dict[str, Any]):
        """执行手势对应的动作"""
        if not self.action_executor or not self.gesture_bindings:
            return
        
        gesture_name = gesture_result['gesture']
        
        # 获取手势绑定
        binding = self.gesture_bindings.get_binding(gesture_name)
        if not binding or not binding.get("enabled", True):
            return
        
        # 执行动作
        result = self.action_executor.execute_action(gesture_name, binding)
        if result is True:
            action_desc = binding.get('description', binding.get('action', ''))
            self.log_message.emit(f"✅ 执行蓝牙手势动作: {action_desc}")
        elif result is False:
            self.log_message.emit(f"❌ 蓝牙手势动作执行失败: {binding.get('action', '')}")
    
    def on_connection_status_changed(self, connected: bool):
        """处理连接状态变化"""
        self.bluetooth_status_changed.emit(connected)
        status = "已连接" if connected else "已断开"
        self.log_message.emit(f"🔗 蓝牙连接状态: {status}")
    
    def on_error_occurred(self, error_message: str):
        """处理错误"""
        self.log_message.emit(f"❌ 蓝牙错误: {error_message}")
    
    def is_bluetooth_enabled(self) -> bool:
        """检查蓝牙是否启用"""
        return self.enabled
    
    def is_connected(self) -> bool:
        """检查是否有蓝牙连接"""
        return self.receiver and self.receiver.is_connected()
    
    def enable_bluetooth(self, enabled: bool):
        """启用/禁用蓝牙功能"""
        self.enabled = enabled
        if enabled and not self.receiver:
            self.setup_bluetooth()
        elif not enabled and self.receiver:
            self.stop_bluetooth_server()
            self.receiver = None
    
    def set_auto_gesture_detection(self, enabled: bool):
        """设置是否启用自动手势检测"""
        self.auto_gesture_detection = enabled
        if enabled and not self.gesture_manager:
            self.gesture_manager = GestureManager()
        elif not enabled:
            self.gesture_manager = None
    
    def get_connection_info(self) -> Dict[str, Any]:
        """获取连接信息"""
        if not self.receiver:
            return {"enabled": False, "connected": False}
        
        return {
            "enabled": self.enabled,
            "connected": self.receiver.is_connected(),
            "client_address": getattr(self.receiver, 'client_address', None),
            "port": self.receiver.port,
            "device_name": self.receiver.device_name
        } 