# 蓝牙RFCOMM通信功能设置指南

## 概述

`project`现在支持通过蓝牙RFCOMM协议接收来自`dyn_gestures`的手势数据。这个功能允许您在Socket和Bluetooth通信方式之间无缝切换。

## 功能特性

? **完整的蓝牙RFCOMM服务器实现**
? **与dyn_gestures完全兼容**  
? **UI中动态切换通信方式**
? **详细的状态显示和错误处理**
? **跨平台支持**

## 系统要求

### Linux系统
```bash
# 安装蓝牙开发库
sudo apt-get install bluetooth libbluetooth-dev

# 安装Python蓝牙库
pip install pybluez
```

### Windows系统
```bash
# Windows通常内置蓝牙支持，但可能需要额外的库
pip install pybluez
# 或者使用Windows特定的蓝牙库
```

### macOS系统
```bash
# macOS可能需要特定的蓝牙库
pip install pybluez
# 或者使用macOS特定的蓝牙库
```

## 配置步骤

### 1. 配置dyn_gestures

在`dyn_gestures/config.py`中设置：
```python
CONNECTION_TYPE = 'serial'  # 启用蓝牙模式
BLUETOOTH_MAC = 'XX:XX:XX:XX:XX:XX'  # 可选：指定MAC地址
BLUETOOTH_PORT = 4  # RFCOMM端口号
```

### 2. 配置project UI

1. 启动project应用：`python app.py`
2. 点击菜单栏的"通信"
3. 选择"切换通信方式"
4. 确认切换到Bluetooth模式
5. 重启手势检测

### 3. 验证配置

使用提供的测试脚本验证蓝牙功能：
```bash
cd project
python test_bluetooth.py
```

## 使用流程

### 启动蓝牙接收模式

1. **启动project应用**
   ```bash
   cd project
   python app.py
   ```

2. **切换到蓝牙模式** (如果尚未配置)
   - 菜单栏 → 通信 → 切换通信方式
   - 选择"是"确认切换到Bluetooth

3. **启动手势检测**
   - 点击"启动Socket服务器" (现在会启动蓝牙服务器)
   - 查看状态显示"蓝牙RFCOMM服务器启动成功"

4. **启动dyn_gestures**
   ```bash
   cd dyn_gestures
   python main.py
   ```

5. **验证连接**
   - project UI应显示"客户端已连接"
   - 开始检测手势，应该能看到数据传输

## 状态监控

### 通信状态查看
- 菜单栏 → 通信 → 显示通信状态
- 快捷键：`Ctrl+S`

### 状态信息包括：
- 当前通信方式：Bluetooth (RFCOMM)
- 检测状态：运行中/已停止
- 蓝牙端口：RFCOMM端口4
- 活动连接数：X个连接
- 蓝牙支持：已启用/未安装
- 协议：蓝牙RFCOMM通信
- MAC地址：自动检测本地适配器

## 故障排除

### 常见问题

#### 1. "系统不支持蓝牙RFCOMM协议"
**解决方案：**
```bash
# Linux
sudo apt-get install bluetooth libbluetooth-dev
pip install pybluez

# Windows/macOS
pip install pybluez
```

#### 2. "蓝牙服务器启动失败"
**可能原因：**
- 蓝牙硬件未启用
- 端口被占用
- 权限不足

**解决方案：**
```bash
# 检查蓝牙状态
sudo systemctl status bluetooth  # Linux

# 启用蓝牙
sudo systemctl start bluetooth   # Linux

# 检查端口占用
sudo netstat -tlnp | grep :4     # Linux
```

#### 3. "dyn_gestures连接失败"
**检查清单：**
- [ ] dyn_gestures配置为`CONNECTION_TYPE = 'serial'`
- [ ] project切换到Bluetooth模式
- [ ] 蓝牙服务器已启动
- [ ] 防火墙未阻止连接
- [ ] 蓝牙设备在范围内

### 调试模式

启用调试输出来查看详细信息：
```python
# 在core/socket_server.py中设置
self.debug_mode = True  # BluetoothServer类
```

### 测试连接

使用内置测试脚本：
```bash
cd project
python test_bluetooth.py
```

## 技术细节

### 协议规格
- **协议族**: `AF_BLUETOOTH`
- **socket类型**: `SOCK_STREAM`
- **协议**: `BTPROTO_RFCOMM`
- **默认端口**: 4
- **编码**: UTF-8
- **数据格式**: JSON

### 数据流
```
dyn_gestures (Bluetooth Client)
    ↓ JSON hand gesture data
    ↓ RFCOMM protocol
    ↓ 
project (Bluetooth Server)
    ↓ Parse & process
    ↓
UI Display & Action Execution
```

### 兼容性
- ? 与现有Socket通信完全兼容
- ? 无缝切换，无需重启应用
- ? 相同的手势数据格式
- ? 相同的UI和功能

## 高级配置

### 自定义端口
修改`BluetoothServer`初始化参数：
```python
# 在ui/threads/socket_gesture_receiver.py中
self.server = BluetoothServer(host="", port=6)  # 使用端口6
```

### 指定MAC地址
```python
# 绑定到特定蓝牙适配器
self.server = BluetoothServer(host="00:11:22:33:44:55", port=4)
```

### 性能优化
```python
# 增加连接队列
self.server_socket.listen(10)  # 默认为5

# 调整接收缓冲区
data = client_socket.recv(2048)  # 默认为1024
```

## 支持与反馈

如果遇到问题或需要技术支持，请：
1. 检查系统蓝牙状态
2. 运行测试脚本确认功能
3. 查看调试输出信息
4. 提供详细的错误信息和系统环境

---

**注意**: 蓝牙功能需要系统蓝牙硬件支持和相应的驱动程序。某些虚拟机环境可能不支持蓝牙功能。 