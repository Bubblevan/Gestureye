"""
蓝牙工具函数 - 用于测试、调试和管理蓝牙功能
"""

import time
import json
import struct
import platform
from typing import List, Dict, Any, Optional, Tuple
from .protocol import BluetoothProtocol, PacketType, HandData, GestureData

try:
    import bluetooth
    BLUETOOTH_AVAILABLE = True
    
    # 检查Windows兼容性
    WINDOWS_COMPATIBILITY_ISSUE = platform.system() == "Windows"
    
    # 测试关键API是否可用
    if WINDOWS_COMPATIBILITY_ISSUE:
        try:
            # 测试是否有这些方法
            hasattr(bluetooth, 'discover_devices')
            hasattr(bluetooth, 'read_local_bdaddr')
            BLUETOOTH_DISCOVERY_AVAILABLE = True
        except:
            BLUETOOTH_DISCOVERY_AVAILABLE = False
    else:
        BLUETOOTH_DISCOVERY_AVAILABLE = True
        
except ImportError:
    BLUETOOTH_AVAILABLE = False
    BLUETOOTH_DISCOVERY_AVAILABLE = False


def check_bluetooth_compatibility() -> Dict[str, Any]:
    """检查蓝牙兼容性"""
    status = {
        'bluetooth_available': BLUETOOTH_AVAILABLE,
        'discovery_available': BLUETOOTH_DISCOVERY_AVAILABLE,
        'platform': platform.system(),
        'issues': [],
        'recommendations': []
    }
    
    if not BLUETOOTH_AVAILABLE:
        status['issues'].append("pybluez库未安装")
        status['recommendations'].append("运行: pip install pybluez")
    
    if BLUETOOTH_AVAILABLE and not BLUETOOTH_DISCOVERY_AVAILABLE:
        status['issues'].append("Windows平台蓝牙API兼容性问题")
        status['recommendations'].extend([
            "这是Windows下pybluez的已知问题",
            "协议功能正常，但设备发现功能受限",
            "建议在Linux/树莓派上运行发送端",
            "或考虑使用bleak库作为替代方案"
        ])
    
    return status


def print_compatibility_report():
    """打印兼容性报告"""
    report = check_bluetooth_compatibility()
    
    print("🔍 蓝牙兼容性检查报告")
    print("=" * 50)
    print(f"平台: {report['platform']}")
    print(f"蓝牙库可用: {'✅' if report['bluetooth_available'] else '❌'}")
    print(f"设备发现可用: {'✅' if report['discovery_available'] else '❌'}")
    
    if report['issues']:
        print("\n⚠️ 发现问题:")
        for issue in report['issues']:
            print(f"  • {issue}")
    
    if report['recommendations']:
        print("\n💡 建议:")
        for rec in report['recommendations']:
            print(f"  • {rec}")
    
    print()


def scan_bluetooth_devices(duration: int = 8, lookup_names: bool = True) -> List[Tuple[str, str]]:
    """
    扫描附近的蓝牙设备
    Args:
        duration: 扫描时间（秒）
        lookup_names: 是否查找设备名称
    Returns:
        设备列表 [(地址, 名称), ...]
    """
    if not BLUETOOTH_AVAILABLE:
        print("蓝牙功能不可用，请安装pybluez")
        return []
    
    if not BLUETOOTH_DISCOVERY_AVAILABLE:
        print("⚠️ 设备发现功能在当前平台不可用")
        print("这是Windows下pybluez的已知兼容性问题")
        print("建议在Linux系统或树莓派上使用此功能")
        return []
    
    try:
        print(f"正在扫描蓝牙设备（{duration}秒）...")
        devices = bluetooth.discover_devices(duration=duration, lookup_names=lookup_names)
        
        if lookup_names:
            for addr, name in devices:
                print(f"发现设备: {name} ({addr})")
        else:
            for addr in devices:
                print(f"发现设备: {addr}")
        
        return devices if lookup_names else [(addr, "") for addr in devices]
        
    except Exception as e:
        print(f"扫描蓝牙设备失败: {e}")
        return []


def find_gesture_receiver_devices(service_uuid: str = "94f39d29-7d6d-437d-973b-fba39e49d4ee") -> List[Dict[str, str]]:
    """
    查找手势接收器设备
    Args:
        service_uuid: 服务UUID
    Returns:
        设备列表
    """
    if not BLUETOOTH_AVAILABLE:
        print("蓝牙功能不可用，请安装pybluez")
        return []
    
    if not BLUETOOTH_DISCOVERY_AVAILABLE:
        print("⚠️ 服务发现功能在当前平台不可用")
        return []
    
    try:
        print("正在查找手势接收器设备...")
        services = bluetooth.find_service(uuid=service_uuid)
        
        devices = []
        for service in services:
            device_info = {
                'name': service.get('name', '未知设备'),
                'host': service['host'],
                'port': service['port'],
                'description': service.get('description', ''),
                'provider': service.get('provider', ''),
                'service_id': service.get('service-id', '')
            }
            devices.append(device_info)
            print(f"找到手势接收器: {device_info['name']} ({device_info['host']}:{device_info['port']})")
        
        if not devices:
            print("未找到手势接收器设备")
        
        return devices
        
    except Exception as e:
        print(f"查找手势接收器失败: {e}")
        return []


def test_protocol_packing():
    """测试协议打包和解包功能"""
    print("测试蓝牙协议打包和解包...")
    
    protocol = BluetoothProtocol()
    
    # 测试手部数据
    test_landmarks = []
    for i in range(21):
        x = 100.0 + (i % 5) * 20.0
        y = 100.0 + (i // 5) * 25.0
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
    
    # 测试手势数据
    gesture_data = GestureData(
        gesture_name="TestGesture",
        hand_type="Right",
        confidence=90.0,
        timestamp=time.time(),
        details={"test": True, "direction": "up"}
    )
    
    # 测试打包
    print("测试数据打包...")
    hand_packet = protocol.pack_hand_landmarks(hand_data)
    gesture_packet = protocol.pack_gesture_result(gesture_data)
    combined_packet = protocol.pack_combined_data(hand_data, gesture_data)
    heartbeat_packet = protocol.pack_heartbeat()
    
    packets = [
        ("手部关键点数据", hand_packet),
        ("手势结果", gesture_packet),
        ("组合数据", combined_packet),
        ("心跳包", heartbeat_packet)
    ]
    
    for name, packet in packets:
        if packet:
            print(f"✅ {name}打包成功，大小: {len(packet)} 字节")
            
            # 测试解包
            result = protocol.unpack_packet(packet)
            if result:
                packet_type, payload_data, sequence = result
                print(f"✅ {name}解包成功，类型: {packet_type.name}, 序列号: {sequence}")
            else:
                print(f"❌ {name}解包失败")
        else:
            print(f"❌ {name}打包失败")
    
    print("协议测试完成")


def calculate_bandwidth_usage(landmarks_per_second: float = 30.0, gestures_per_second: float = 2.0) -> Dict[str, Any]:
    """
    计算带宽使用情况
    Args:
        landmarks_per_second: 每秒手部关键点数据包数量
        gestures_per_second: 每秒手势数据包数量
    Returns:
        带宽使用信息
    """
    protocol = BluetoothProtocol()
    
    # 创建示例数据
    test_landmarks = [[100.0 + i, 100.0 + i, 0.0] for i in range(21)]
    hand_data = HandData(
        hand_id="test",
        hand_type="Right", 
        landmarks=test_landmarks,
        palm_center=(150.0, 150.0),
        palm_length=80.0,
        timestamp=time.time(),
        confidence=0.95
    )
    
    gesture_data = GestureData(
        gesture_name="TestGesture",
        hand_type="Right",
        confidence=90.0,
        timestamp=time.time(),
        details={"test": True}
    )
    
    # 计算数据包大小
    hand_packet_size = len(protocol.pack_hand_landmarks(hand_data))
    gesture_packet_size = len(protocol.pack_gesture_result(gesture_data))
    combined_packet_size = len(protocol.pack_combined_data(hand_data, gesture_data))
    heartbeat_packet_size = len(protocol.pack_heartbeat())
    
    # 计算每秒字节数
    landmarks_bytes_per_sec = hand_packet_size * landmarks_per_second
    gestures_bytes_per_sec = gesture_packet_size * gestures_per_second
    heartbeat_bytes_per_sec = heartbeat_packet_size * (1/5)  # 每5秒一次心跳
    
    total_bytes_per_sec = landmarks_bytes_per_sec + gestures_bytes_per_sec + heartbeat_bytes_per_sec
    
    return {
        "packet_sizes": {
            "hand_landmarks": hand_packet_size,
            "gesture_result": gesture_packet_size,
            "combined_data": combined_packet_size,
            "heartbeat": heartbeat_packet_size
        },
        "bandwidth_usage": {
            "landmarks_bps": landmarks_bytes_per_sec,
            "gestures_bps": gestures_bytes_per_sec,
            "heartbeat_bps": heartbeat_bytes_per_sec,
            "total_bps": total_bytes_per_sec,
            "total_kbps": total_bytes_per_sec / 1024,
            "total_mbps": total_bytes_per_sec / (1024 * 1024)
        },
        "estimated_rates": {
            "landmarks_per_second": landmarks_per_second,
            "gestures_per_second": gestures_per_second,
            "heartbeat_per_second": 0.2
        }
    }


def benchmark_protocol_performance(iterations: int = 1000) -> Dict[str, float]:
    """
    性能基准测试
    Args:
        iterations: 测试迭代次数
    Returns:
        性能测试结果
    """
    print(f"开始协议性能测试（{iterations}次迭代）...")
    
    protocol = BluetoothProtocol()
    
    # 准备测试数据
    test_landmarks = [[100.0 + i, 100.0 + i, 0.0] for i in range(21)]
    hand_data = HandData(
        hand_id="perf_test",
        hand_type="Right",
        landmarks=test_landmarks,
        palm_center=(150.0, 150.0),
        palm_length=80.0,
        timestamp=time.time(),
        confidence=0.95
    )
    
    # 测试打包性能
    start_time = time.time()
    for _ in range(iterations):
        packet = protocol.pack_hand_landmarks(hand_data)
    pack_time = time.time() - start_time
    
    # 测试解包性能
    test_packet = protocol.pack_hand_landmarks(hand_data)
    start_time = time.time()
    for _ in range(iterations):
        result = protocol.unpack_packet(test_packet)
    unpack_time = time.time() - start_time
    
    results = {
        "pack_time_total": pack_time,
        "pack_time_per_operation": pack_time / iterations,
        "pack_operations_per_second": iterations / pack_time,
        "unpack_time_total": unpack_time,
        "unpack_time_per_operation": unpack_time / iterations,
        "unpack_operations_per_second": iterations / unpack_time
    }
    
    print(f"打包性能: {results['pack_operations_per_second']:.1f} 操作/秒")
    print(f"解包性能: {results['unpack_operations_per_second']:.1f} 操作/秒")
    
    return results


def create_test_hand_data(hand_type: str = "Right") -> HandData:
    """创建测试用手部数据"""
    # 模拟真实的手部关键点位置
    test_landmarks = []
    for i in range(21):
        # 模拟手掌形状
        if i == 0:  # 手腕
            x, y = 300, 400
        elif i <= 4:  # 拇指
            x = 250 + i * 15
            y = 350 - i * 10
        elif i <= 8:  # 食指
            x = 280 + (i-4) * 10
            y = 300 - (i-4) * 20
        elif i <= 12:  # 中指
            x = 300 + (i-8) * 10
            y = 280 - (i-8) * 25
        elif i <= 16:  # 无名指
            x = 320 + (i-12) * 10
            y = 300 - (i-12) * 20
        else:  # 小指
            x = 340 + (i-16) * 8
            y = 320 - (i-16) * 15
        
        test_landmarks.append([float(x), float(y), 0.0])
    
    return HandData(
        hand_id="test_hand",
        hand_type=hand_type,
        landmarks=test_landmarks,
        palm_center=(300.0, 350.0),
        palm_length=80.0,
        timestamp=time.time(),
        confidence=0.95
    )


def verify_bluetooth_connection(target_address: str, port: int = 1) -> bool:
    """
    验证蓝牙连接
    Args:
        target_address: 目标蓝牙地址
        port: 端口号
    Returns:
        连接是否成功
    """
    if not BLUETOOTH_AVAILABLE:
        print("蓝牙功能不可用")
        return False
    
    try:
        print(f"测试连接到 {target_address}:{port}...")
        sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        sock.settimeout(5.0)  # 5秒超时
        sock.connect((target_address, port))
        
        # 发送测试数据
        protocol = BluetoothProtocol()
        ping_packet = protocol.pack_ping()
        sock.send(ping_packet)
        
        # 等待回应
        data = sock.recv(1024)
        if data:
            result = protocol.unpack_packet(data)
            if result and result[0] == PacketType.PONG:
                print("✅ 连接测试成功")
                sock.close()
                return True
        
        sock.close()
        print("❌ 连接测试失败：未收到有效回应")
        return False
        
    except Exception as e:
        print(f"❌ 连接测试失败: {e}")
        return False


if __name__ == "__main__":
    """测试工具函数"""
    print("蓝牙工具测试")
    print("=" * 50)
    
    # 测试协议
    test_protocol_packing()
    print()
    
    # 性能测试
    benchmark_protocol_performance(100)
    print()
    
    # 带宽计算
    bandwidth_info = calculate_bandwidth_usage()
    print("带宽使用情况:")
    print(f"总带宽: {bandwidth_info['bandwidth_usage']['total_kbps']:.2f} KB/s")
    print()
    
    # 扫描设备
    scan_bluetooth_devices(3) 