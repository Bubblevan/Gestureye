#!/usr/bin/env python3
"""
蓝牙功能测试示例
这个脚本演示如何使用蓝牙功能进行手势数据传输
"""

import sys
import os
import time
import threading

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bluetooth.utils import (
    scan_bluetooth_devices, 
    find_gesture_receiver_devices,
    test_protocol_packing,
    benchmark_protocol_performance,
    calculate_bandwidth_usage,
    create_test_hand_data,
    verify_bluetooth_connection
)
from bluetooth.sender import BluetoothSender, create_hand_data_from_landmarks, create_gesture_data_from_result
from bluetooth.receiver import BluetoothReceiver
from bluetooth.protocol import HandData, GestureData
from PyQt6.QtCore import QCoreApplication


class BluetoothTestSuite:
    """蓝牙功能测试套件"""
    
    def __init__(self):
        self.app = None
        self.receiver = None
        self.sender = None
        
    def setup_qt_app(self):
        """设置Qt应用程序（接收器需要）"""
        if QCoreApplication.instance() is None:
            self.app = QCoreApplication(sys.argv)
        
    def test_protocol(self):
        """测试蓝牙协议"""
        print("🧪 测试蓝牙协议")
        print("-" * 40)
        test_protocol_packing()
        print()
    
    def test_performance(self):
        """测试性能"""
        print("⚡ 性能测试")
        print("-" * 40)
        results = benchmark_protocol_performance(500)
        print(f"协议性能测试完成")
        print(f"打包: {results['pack_operations_per_second']:.0f} ops/sec")
        print(f"解包: {results['unpack_operations_per_second']:.0f} ops/sec")
        print()
    
    def test_bandwidth_calculation(self):
        """测试带宽计算"""
        print("📊 带宽使用分析")
        print("-" * 40)
        
        # 不同场景的带宽计算
        scenarios = [
            ("低频率", 10.0, 0.5),    # 每秒10次关键点，0.5次手势
            ("标准频率", 30.0, 2.0),   # 每秒30次关键点，2次手势
            ("高频率", 60.0, 5.0),     # 每秒60次关键点，5次手势
        ]
        
        for name, landmarks_rate, gesture_rate in scenarios:
            bandwidth = calculate_bandwidth_usage(landmarks_rate, gesture_rate)
            print(f"{name}:")
            print(f"  关键点包: {bandwidth['packet_sizes']['hand_landmarks']} 字节")
            print(f"  手势包: {bandwidth['packet_sizes']['gesture_result']} 字节")
            print(f"  总带宽: {bandwidth['bandwidth_usage']['total_kbps']:.2f} KB/s")
            print()
    
    def test_device_discovery(self):
        """测试设备发现"""
        print("🔍 蓝牙设备发现")
        print("-" * 40)
        
        # 扫描附近设备
        print("扫描附近的蓝牙设备...")
        devices = scan_bluetooth_devices(duration=5, lookup_names=True)
        
        if devices:
            print(f"发现 {len(devices)} 个设备:")
            for addr, name in devices:
                print(f"  {name} ({addr})")
        else:
            print("未发现任何设备")
        print()
        
        # 查找手势接收器
        print("查找手势接收器设备...")
        receivers = find_gesture_receiver_devices()
        if receivers:
            print(f"发现 {len(receivers)} 个手势接收器:")
            for device in receivers:
                print(f"  {device['name']} ({device['host']}:{device['port']})")
        else:
            print("未发现手势接收器设备")
        print()
    
    def test_receiver_server(self, duration: int = 10):
        """测试接收器服务器"""
        print("📡 测试蓝牙接收器")
        print("-" * 40)
        
        self.setup_qt_app()
        
        self.receiver = BluetoothReceiver()
        
        # 连接信号
        self.receiver.hand_data_received.connect(self.on_hand_data_received)
        self.receiver.gesture_detected.connect(self.on_gesture_detected)
        self.receiver.connection_status_changed.connect(self.on_connection_changed)
        self.receiver.error_occurred.connect(self.on_error_occurred)
        
        # 启动服务器
        if self.receiver.start_server():
            print(f"蓝牙服务器已启动，等待连接 {duration} 秒...")
            
            # 运行Qt事件循环
            start_time = time.time()
            while time.time() - start_time < duration:
                if self.app:
                    self.app.processEvents()
                time.sleep(0.1)
            
            self.receiver.stop_server()
            print("接收器测试完成")
        else:
            print("❌ 启动蓝牙服务器失败")
        print()
    
    def test_sender_client(self, target_address: str):
        """测试发送器客户端"""
        print("📤 测试蓝牙发送器")
        print("-" * 40)
        
        self.sender = BluetoothSender(target_address)
        
        if self.sender.connect():
            print(f"✅ 连接成功: {target_address}")
            
            # 发送测试数据
            self.send_test_data()
            
            # 等待一段时间
            time.sleep(2)
            
            self.sender.disconnect()
            print("发送器测试完成")
        else:
            print(f"❌ 连接失败: {target_address}")
        print()
    
    def send_test_data(self):
        """发送各种测试数据"""
        if not self.sender or not self.sender.connected:
            return
        
        print("发送测试数据包...")
        
        # 创建测试手部数据
        hand_data = create_test_hand_data("Right")
        self.sender.send_hand_landmarks(hand_data)
        print("✅ 发送手部关键点数据")
        
        time.sleep(0.5)
        
        # 创建测试手势数据
        gesture_data = GestureData(
            gesture_name="TestGesture",
            hand_type="Right",
            confidence=95.0,
            timestamp=time.time(),
            details={"test_mode": True, "direction": "up"}
        )
        self.sender.send_gesture_result(gesture_data)
        print("✅ 发送手势识别结果")
        
        time.sleep(0.5)
        
        # 发送组合数据
        hand_data2 = create_test_hand_data("Left")
        gesture_data2 = GestureData(
            gesture_name="PeaceSign",
            hand_type="Left",
            confidence=88.0,
            timestamp=time.time(),
            details={"fingers_up": [0, 1, 1, 0, 0]}
        )
        self.sender.send_combined_data(hand_data2, gesture_data2)
        print("✅ 发送组合数据")
    
    def test_connection_verification(self, target_address: str):
        """测试连接验证"""
        print("🔗 测试连接验证")
        print("-" * 40)
        
        success = verify_bluetooth_connection(target_address)
        if success:
            print(f"✅ 连接验证成功: {target_address}")
        else:
            print(f"❌ 连接验证失败: {target_address}")
        print()
    
    def run_full_test_suite(self, target_address: Optional[str] = None):
        """运行完整测试套件"""
        print("🚀 蓝牙功能完整测试套件")
        print("=" * 50)
        print()
        
        # 基础测试
        self.test_protocol()
        self.test_performance()
        self.test_bandwidth_calculation()
        
        # 设备发现测试
        self.test_device_discovery()
        
        # 如果提供了目标地址，进行连接测试
        if target_address:
            self.test_connection_verification(target_address)
            # self.test_sender_client(target_address)
        
        # 接收器测试（短时间）
        # self.test_receiver_server(duration=5)
        
        print("🎉 所有测试完成！")
    
    # Qt信号处理函数
    def on_hand_data_received(self, hand_data: HandData):
        """处理接收到的手部数据"""
        print(f"📥 接收到手部数据: {hand_data.hand_type}手 (置信度: {hand_data.confidence:.2f})")
    
    def on_gesture_detected(self, gesture_data: GestureData):
        """处理接收到的手势数据"""
        print(f"🖐️ 检测到手势: {gesture_data.hand_type}手 - {gesture_data.gesture_name} (置信度: {gesture_data.confidence:.1f}%)")
    
    def on_connection_changed(self, connected: bool):
        """处理连接状态变化"""
        status = "已连接" if connected else "已断开"
        print(f"🔗 连接状态: {status}")
    
    def on_error_occurred(self, error_message: str):
        """处理错误"""
        print(f"❌ 错误: {error_message}")


def print_usage():
    """打印使用说明"""
    print("蓝牙功能测试程序")
    print("=" * 50)
    print("用法:")
    print("  python bluetooth_test.py [选项] [蓝牙地址]")
    print()
    print("选项:")
    print("  --protocol      只测试协议功能")
    print("  --performance   只测试性能")
    print("  --bandwidth     只测试带宽计算")
    print("  --discovery     只测试设备发现")
    print("  --receiver      只测试接收器")
    print("  --sender        只测试发送器（需要蓝牙地址）")
    print("  --verify        只测试连接验证（需要蓝牙地址）")
    print("  --help, -h      显示此帮助信息")
    print()
    print("示例:")
    print("  python bluetooth_test.py                    # 运行完整测试")
    print("  python bluetooth_test.py --protocol         # 只测试协议")
    print("  python bluetooth_test.py --sender 00:11:22:33:44:55  # 测试发送器")
    print()


def main():
    """主函数"""
    if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h']:
        print_usage()
        return
    
    test_suite = BluetoothTestSuite()
    
    if len(sys.argv) == 1:
        # 运行完整测试套件
        test_suite.run_full_test_suite()
    else:
        # 解析命令行参数
        option = sys.argv[1]
        target_address = sys.argv[2] if len(sys.argv) > 2 else None
        
        if option == '--protocol':
            test_suite.test_protocol()
        elif option == '--performance':
            test_suite.test_performance()
        elif option == '--bandwidth':
            test_suite.test_bandwidth_calculation()
        elif option == '--discovery':
            test_suite.test_device_discovery()
        elif option == '--receiver':
            test_suite.test_receiver_server(duration=30)
        elif option == '--sender':
            if target_address:
                test_suite.test_sender_client(target_address)
            else:
                print("❌ 发送器测试需要目标蓝牙地址")
        elif option == '--verify':
            if target_address:
                test_suite.test_connection_verification(target_address)
            else:
                print("❌ 连接验证需要目标蓝牙地址")
        else:
            print(f"❌ 未知选项: {option}")
            print_usage()


if __name__ == "__main__":
    main() 