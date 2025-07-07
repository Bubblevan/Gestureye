# 蓝牙手势传输功能使用指南

## 概述

本项目实现了完整的蓝牙手势传输系统，支持从树莓派到PC的实时手势数据传输。系统包含21个手部关键点坐标和手势识别结果的传输。

## ?? 系统架构

```
树莓派端 (发送器)          PC端 (接收器)
┌─────────────────┐       ┌─────────────────┐
│   手势检测      │       │   蓝牙接收器    │
│   ↓             │       │   ↓             │
│   数据打包      │ ====> │   数据解包      │
│   ↓             │  蓝牙  │   ↓             │
│   蓝牙发送      │       │   动作执行      │
└─────────────────┘       └─────────────────┘
```

## ? 核心组件

### 1. 蓝牙协议 (`bluetooth/protocol.py`)
- **数据包类型**：手部关键点、手势结果、组合数据、心跳包
- **数据格式**：二进制头部 + JSON载荷 + 校验和
- **数据结构**：`HandData`和`GestureData`

### 2. 蓝牙发送器 (`bluetooth/sender.py`)
- **用途**：树莓派端发送数据
- **特性**：自动重连、发送队列、心跳机制

### 3. 蓝牙接收器 (`bluetooth/receiver.py`)
- **用途**：PC端接收数据
- **特性**：服务器模式、Qt信号集成、连接管理

### 4. 蓝牙管理器 (`bluetooth/manager.py`)
- **用途**：系统集成和动作执行
- **特性**：自动手势检测、动作绑定

## ? 快速开始

### 环境要求

**PC端：**
```bash
pip install PyQt6 opencv-python cvzone mediapipe numpy pynput pywin32 pybluez
```

**树莓派端：**
```bash
pip install opencv-python cvzone mediapipe numpy pybluez
```

### 基本使用流程

#### 1. PC端（接收器）

```python
from bluetooth.manager import BluetoothManager

# 创建蓝牙管理器
bt_manager = BluetoothManager()

# 启动蓝牙服务器
bt_manager.start_bluetooth_server()

# 连接信号处理
bt_manager.bluetooth_gesture_detected.connect(lambda name, hand, conf: 
    print(f"检测到手势: {name} ({hand}手, {conf:.1f}%)"))
```

#### 2. 树莓派端（发送器）

```python
from bluetooth.raspberry_pi_sender import RaspberryPiGestureSender

# 创建发送器（替换为PC的蓝牙地址）
sender = RaspberryPiGestureSender("PC_BLUETOOTH_ADDRESS")

# 连接到PC
if sender.connect_to_pc():
    # 开始手势检测和发送
    sender.start_gesture_detection_and_send()
```

## ? 协议详解

### 数据包格式

```
+--------+--------+------+------+----------+--------+----------+----------+--------+
| Header | Version| Type | Seq  | Length   | Payload (JSON)    | Checksum | Footer |
| 2B     | 1B     | 1B   | 2B   | 2B       | Variable          | 2B       | 2B     |
+--------+--------+------+------+----------+-------------------+----------+--------+
```

### 数据包类型

| 类型 | 代码 | 说明 |
|------|------|------|
| HAND_LANDMARKS | 0x01 | 手部关键点数据 |
| GESTURE_RESULT | 0x02 | 手势识别结果 |
| COMBINED_DATA | 0x03 | 组合数据 |
| HEARTBEAT | 0x04 | 心跳包 |

### HandData 结构

```python
@dataclass
class HandData:
    hand_id: str                    # 手部ID
    hand_type: str                  # "Left" 或 "Right"
    landmarks: List[List[float]]    # 21个关键点坐标 [x, y, z]
    palm_center: Tuple[float, float]  # 掌心坐标
    palm_length: float              # 手掌基准长度
    timestamp: float                # 时间戳
    confidence: float               # 检测置信度
```

### GestureData 结构

```python
@dataclass
class GestureData:
    gesture_name: str               # 手势名称
    hand_type: str                  # "Left" 或 "Right"
    confidence: float               # 置信度
    timestamp: float                # 时间戳
    details: Dict[str, Any]         # 详细信息
```

## ?? 配置说明

### `config.py` 蓝牙配置

```python
BLUETOOTH_CONFIG = {
    'enabled': True,                     # 启用蓝牙功能
    'server_port': 1,                   # RFCOMM端口
    'server_uuid': '94f39d29-7d6d-437d-973b-fba39e49d4ee',
    'device_name': 'HandGestureReceiver',
    'heartbeat_interval': 5.0,          # 心跳间隔（秒）
    'auto_gesture_detection': True      # 自动手势检测
}
```

## ? 工具和测试

### 1. 协议测试

```bash
# 测试协议打包/解包
python -m bluetooth.utils

# 或者使用测试脚本
python examples/bluetooth_test.py --protocol
```

### 2. 设备发现

```bash
# 扫描蓝牙设备
python examples/bluetooth_test.py --discovery

# 查找手势接收器
python -c "from bluetooth.utils import find_gesture_receiver_devices; print(find_gesture_receiver_devices())"
```

### 3. 性能测试

```bash
# 运行性能基准测试
python examples/bluetooth_test.py --performance
```

### 4. 连接测试

```bash
# 测试与指定设备的连接
python examples/bluetooth_test.py --verify YOUR_BLUETOOTH_ADDRESS
```

## ? 性能和带宽

### 典型带宽使用

| 场景 | 关键点频率 | 手势频率 | 总带宽 |
|------|------------|----------|--------|
| 低频 | 10 FPS | 0.5 FPS | ~2.5 KB/s |
| 标准 | 30 FPS | 2 FPS | ~7.8 KB/s |
| 高频 | 60 FPS | 5 FPS | ~16.2 KB/s |

### 数据包大小

- 手部关键点包: ~600-800 字节
- 手势结果包: ~200-300 字节
- 心跳包: ~50-80 字节

## ?? 集成到现有项目

### 1. 启用PC端接收

```python
# 在 ui/main_window.py 中
from bluetooth.manager import BluetoothManager

class MainWindowUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.bluetooth_manager = BluetoothManager()
        self.setup_bluetooth()
    
    def setup_bluetooth(self):
        if self.bluetooth_manager.is_bluetooth_enabled():
            self.bluetooth_manager.start_bluetooth_server()
            
            # 连接信号
            self.bluetooth_manager.bluetooth_gesture_detected.connect(
                self.on_bluetooth_gesture
            )
    
    def on_bluetooth_gesture(self, gesture_name, hand_type, confidence):
        print(f"蓝牙手势: {gesture_name}")
```

### 2. 修改配置启用蓝牙

```python
# 在 config.py 中修改
BLUETOOTH_CONFIG = {
    'enabled': True,  # 改为 True
    # ... 其他配置
}
```

## ? 故障排除

### 常见问题

1. **"pybluez库未安装"**
   ```bash
   pip install pybluez
   ```

2. **"无法打开蓝牙适配器"**
   - 确保蓝牙适配器已启用
   - 检查驱动程序安装

3. **"连接失败"**
   - 确认设备地址正确
   - 检查防火墙设置
   - 确保设备在配对范围内

4. **"数据传输中断"**
   - 检查蓝牙信号强度
   - 查看心跳包是否正常

### 调试方法

```python
# 启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 使用工具函数测试
from bluetooth.utils import verify_bluetooth_connection
result = verify_bluetooth_connection("TARGET_ADDRESS")
```

## ? 开发指南

### 添加新的数据包类型

1. 在 `PacketType` 枚举中添加新类型
2. 实现对应的打包/解包方法
3. 更新协议版本号

### 自定义手势处理

```python
# 在蓝牙管理器中添加自定义处理
def custom_gesture_handler(self, gesture_data):
    if gesture_data.gesture_name == "CustomGesture":
        # 执行自定义动作
        print("执行自定义手势动作")
```

## ? API 参考

### BluetoothSender 主要方法

- `connect()`: 连接到PC
- `send_hand_landmarks(hand_data)`: 发送手部数据
- `send_gesture_result(gesture_data)`: 发送手势结果
- `send_combined_data(hand_data, gesture_data)`: 发送组合数据
- `disconnect()`: 断开连接

### BluetoothReceiver 主要信号

- `hand_data_received(HandData)`: 接收到手部数据
- `gesture_detected(GestureData)`: 检测到手势
- `connection_status_changed(bool)`: 连接状态变化
- `error_occurred(str)`: 发生错误

### BluetoothManager 主要方法

- `start_bluetooth_server()`: 启动服务器
- `stop_bluetooth_server()`: 停止服务器
- `is_connected()`: 检查连接状态
- `enable_bluetooth(enabled)`: 启用/禁用蓝牙

## ? 安全考虑

1. **数据加密**: 考虑在敏感环境中添加数据加密
2. **设备认证**: 实现设备配对验证机制
3. **访问控制**: 限制连接的设备白名单

## ? 性能优化建议

1. **降低发送频率**: 根据应用需求调整数据发送频率
2. **数据压缩**: 对大量数据考虑压缩传输
3. **缓存管理**: 合理设置发送队列大小
4. **连接复用**: 避免频繁建立/断开连接

## ? 贡献

欢迎提交问题和改进建议！请确保：

1. 代码符合项目风格
2. 添加适当的测试
3. 更新相关文档
4. 测试在不同环境下的兼容性

## ? 许可证

本项目遵循 MIT 许可证。详见 LICENSE 文件。 