# Linux系统蓝牙通信配置指南

## 问题描述

当您在Linux系统上运行project应用并切换到蓝牙通信模式时，可能会遇到以下问题：
1. 无法自动获取蓝牙MAC地址
2. 启动服务器时显示"socket服务器已启动"而不是蓝牙服务器
3. 无法接收到dyn_gestures客户端发送的手势信息

## 解决方案

### 1. 获取Linux系统蓝牙MAC地址

#### 方法1: 使用提供的脚本
```bash
cd project
python get_linux_bluetooth_mac.py
```

#### 方法2: 手动获取
```bash
# 方法1: 使用hciconfig
sudo hciconfig

# 方法2: 使用bluetoothctl
bluetoothctl show

# 方法3: 读取系统文件
cat /sys/class/bluetooth/hci0/address

# 方法4: 查看网络接口
ip link show | grep -i bluetooth
```

### 2. 配置project应用

编辑 `project/config.py` 文件：
```python
# 通信方式配置
CONNECTION_TYPE = 'serial'  # 通信模式：'socket' 或 'serial' (蓝牙)

# 蓝牙配置
BLUETOOTH_MAC = "你的蓝牙MAC地址"  # 例如: "00:11:22:33:44:55"
BLUETOOTH_PORT = 4  # 蓝牙RFCOMM端口
BLUETOOTH_ENABLED = True  # 是否启用蓝牙功能
```

### 3. 配置dyn_gestures客户端

编辑 `dyn_gestures/config.py` 文件：
```python
CONNECTION_TYPE = 'serial'      # 连接模式：'socket' 或 'serial'
BLUETOOTH_MAC = 'project应用的蓝牙MAC地址'  # 与project/config.py中的BLUETOOTH_MAC一致
BLUETOOTH_PORT = 4              # 蓝牙RFCOMM端口
```

### 4. 安装必要的依赖

```bash
# 安装蓝牙支持库
pip install pybluez

# 如果遇到编译错误，可能需要安装系统依赖
sudo apt-get install libbluetooth-dev
sudo apt-get install python3-dev

# 对于某些Linux发行版，可能还需要
sudo apt-get install bluetooth libbluetooth-dev
```

### 5. 启动蓝牙服务

```bash
# 启动蓝牙服务
sudo systemctl start bluetooth
sudo systemctl enable bluetooth

# 检查蓝牙服务状态
sudo systemctl status bluetooth

# 确保蓝牙适配器已启用
sudo hciconfig hci0 up
```

### 6. 测试蓝牙连接

#### 启动project服务器
```bash
cd project
python app.py
```

在UI中：
1. 点击"通信" -> "切换通信方式" -> 选择"Bluetooth"
2. 点击"启动服务器"
3. 查看日志，应该显示"蓝牙RFCOMM服务器启动成功"

#### 启动dyn_gestures客户端
```bash
cd dyn_gestures
python main.py
```

### 7. 故障排除

#### 问题1: 仍然显示"socket服务器已启动"
**原因**: 蓝牙服务器初始化失败，自动降级到socket模式
**解决**: 
1. 检查是否安装了pybluez: `pip install pybluez`
2. 检查蓝牙服务是否运行: `sudo systemctl status bluetooth`
3. 检查蓝牙适配器是否启用: `sudo hciconfig`

#### 问题2: 无法获取蓝牙MAC地址
**解决**: 手动配置MAC地址
1. 运行 `python get_linux_bluetooth_mac.py` 获取MAC地址
2. 将获取到的MAC地址填入 `project/config.py` 的 `BLUETOOTH_MAC` 字段

#### 问题3: 连接被拒绝
**原因**: 防火墙或权限问题
**解决**:
```bash
# 检查RFCOMM端口是否被占用
sudo lsof -i :4

# 重启蓝牙服务
sudo systemctl restart bluetooth

# 检查蓝牙权限
sudo usermod -a -G bluetooth $USER
```

#### 问题4: 客户端无法连接
**检查清单**:
- [ ] project和dyn_gestures的CONNECTION_TYPE都设置为'serial'
- [ ] BLUETOOTH_MAC地址配置正确
- [ ] BLUETOOTH_PORT端口一致（默认4）
- [ ] 蓝牙服务正在运行
- [ ] 两个设备在蓝牙范围内

### 8. 调试模式

启用详细日志输出：
```python
# 在project/core/socket_server.py中
self.debug_mode = True  # BluetoothServer类
```

### 9. 验证配置

使用提供的测试脚本验证：
```bash
cd project
python get_linux_bluetooth_mac.py
```

成功配置后，您应该看到：
- project应用显示"蓝牙RFCOMM服务器启动成功"
- 显示本机蓝牙MAC地址
- dyn_gestures客户端能够连接并发送手势数据

## 常见错误信息及解决方案

| 错误信息 | 原因 | 解决方案 |
|---------|------|----------|
| "系统不支持蓝牙RFCOMM协议" | 未安装pybluez | `pip install pybluez` |
| "蓝牙服务器初始化失败" | 蓝牙服务未启动 | `sudo systemctl start bluetooth` |
| "无法获取本机蓝牙MAC地址" | 自动检测失败 | 手动配置MAC地址 |
| "连接被拒绝" | 端口被占用或权限不足 | 重启蓝牙服务，检查权限 |

## 技术支持

如果仍然遇到问题，请提供以下信息：
1. Linux发行版和版本
2. 蓝牙适配器型号
3. 完整的错误日志
4. `python get_linux_bluetooth_mac.py` 的输出结果 