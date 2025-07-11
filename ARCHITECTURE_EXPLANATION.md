# 手势检测系统架构说明

## 系统架构概述

本系统采用**客户端-服务器**架构，但与传统架构相反：

- **dyn_gestures**: 服务端，负责手势检测和数据发送
- **project**: 客户端，负责数据接收和动作执行

## 通信模式

### 1. Socket模式 (TCP/IP)
```
dyn_gestures (服务端) --TCP/IP--> project (客户端)
```

**配置**:
- `dyn_gestures/config.py`: `CONNECTION_TYPE = 'socket'`
- `project/config.py`: `CONNECTION_TYPE = 'socket'`

### 2. 蓝牙模式 (RFCOMM)
```
dyn_gestures (服务端) --蓝牙RFCOMM--> project (客户端)
```

**配置**:
- `dyn_gestures/config.py`: `CONNECTION_TYPE = 'serial'`
- `project/config.py`: `CONNECTION_TYPE = 'serial'`

## 数据流向

### dyn_gestures (服务端)
1. **手势检测**: 使用摄像头检测手势
2. **数据处理**: 识别手势类型和置信度
3. **数据发送**: 通过socket发送到project
   - Socket模式: 使用TCP/IP发送到指定IP和端口
   - 蓝牙模式: 使用RFCOMM发送到指定MAC地址和端口

### project (客户端)
1. **数据接收**: 通过socket接收来自dyn_gestures的数据
   - Socket模式: 监听TCP/IP端口
   - 蓝牙模式: 监听RFCOMM端口
2. **数据处理**: 解析手势数据
3. **动作执行**: 根据手势绑定执行相应动作

## 配置一致性要求

### 重要：两个项目的配置必须一致！

| 项目 | CONNECTION_TYPE | 说明 |
|------|----------------|------|
| dyn_gestures | `'socket'` | 使用TCP/IP发送数据 |
| project | `'socket'` | 使用TCP/IP接收数据 |
| dyn_gestures | `'serial'` | 使用蓝牙RFCOMM发送数据 |
| project | `'serial'` | 使用蓝牙RFCOMM接收数据 |

### 蓝牙配置
当使用蓝牙模式时，还需要配置：

**dyn_gestures/config.py**:
```python
CONNECTION_TYPE = 'serial'
BLUETOOTH_MAC = 'project的蓝牙MAC地址'  # project应用的蓝牙MAC地址
BLUETOOTH_PORT = 4
```

**project/config.py**:
```python
CONNECTION_TYPE = 'serial'
BLUETOOTH_MAC = 'XX:XX:XX:XX:XX:XX'  # 自动检测或手动配置
BLUETOOTH_PORT = 4
```

## 常见问题

### 1. 为什么切换通信方式需要点击两次？
**原因**: 配置不一致导致客户端初始化失败
**解决**: 确保两个项目的`CONNECTION_TYPE`设置一致

### 2. 为什么显示"socket服务器已启动"而不是蓝牙服务器？
**原因**: 蓝牙服务器初始化失败，自动降级到socket模式
**解决**: 
- 检查是否安装了`pybluez`
- 检查蓝牙服务是否运行
- 检查MAC地址配置是否正确

### 3. 为什么无法接收到手势数据？
**检查清单**:
- [ ] 两个项目的`CONNECTION_TYPE`一致
- [ ] 蓝牙模式下MAC地址配置正确
- [ ] 网络/蓝牙连接正常
- [ ] 防火墙未阻止连接

## 调试方法

### 1. 检查配置
```bash
# 检查dyn_gestures配置
cat dyn_gestures/config.py | grep CONNECTION_TYPE

# 检查project配置  
cat project/config.py | grep CONNECTION_TYPE
```

### 2. 测试连接
```bash
# 测试Socket连接
cd project
python -c "import socket; s=socket.socket(); s.connect(('127.0.0.1', 65432)); print('Socket连接成功')"

# 测试蓝牙连接
cd project
python get_linux_bluetooth_mac.py
```

### 3. 查看日志
- dyn_gestures: 查看控制台输出的连接信息
- project: 查看UI日志面板的服务器状态

## 切换通信方式步骤

### 从Socket切换到蓝牙
1. **停止两个应用**
2. **修改dyn_gestures配置**:
   ```python
   CONNECTION_TYPE = 'serial'
   BLUETOOTH_MAC = 'project的蓝牙MAC地址'
   ```
3. **修改project配置**:
   ```python
   CONNECTION_TYPE = 'serial'
   ```
4. **启动project应用**，在UI中切换到蓝牙模式
5. **启动dyn_gestures应用**

### 从蓝牙切换到Socket
1. **停止两个应用**
2. **修改dyn_gestures配置**:
   ```python
   CONNECTION_TYPE = 'socket'
   SOCKET_HOST = 'project的IP地址'
   ```
3. **修改project配置**:
   ```python
   CONNECTION_TYPE = 'socket'
   ```
4. **启动两个应用**

## 技术细节

### Socket通信
- **协议**: TCP/IP
- **端口**: 65432 (默认)
- **数据格式**: JSON
- **编码**: UTF-8

### 蓝牙通信
- **协议**: RFCOMM
- **端口**: 4 (默认)
- **数据格式**: JSON
- **编码**: UTF-8

### 数据格式示例
```json
{
    "type": "gesture_detection",
    "gesture": "HandOpen",
    "hand_type": "Right",
    "confidence": 95.5,
    "gesture_type": "dynamic",
    "timestamp": 1234567890.123,
    "details": {
        "tag": "end"
    }
}
``` 