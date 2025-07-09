# Socket通信启动指南

## 概述

这个指南将帮助您启动两个项目之间的Socket通信：

- **project** - ? **Socket服务器**，只接收和处理手势数据，**不调用摄像头**
- **dyn_gestures** - ? **Socket客户端**，负责摄像头调用、手势识别和数据发送

## ?? 重要说明

**project应用不会调用摄像头！**

- `project/app.py` 只是Socket服务器，等待接收数据
- `dyn_gestures/main.py` 负责摄像头和手势识别
- 两个项目分工明确，互不干扰

### ?? 架构图

```
┌─────────────────────────────┐    ┌─────────────────────────────┐
│      dyn_gestures          │    │         project            │
│    (Socket客户端)           │    │    (Socket服务器)          │
├─────────────────────────────┤    ├─────────────────────────────┤
│ ? cv2.VideoCapture()      │    │ ? socket.bind()           │
│ ? 手势识别算法             │    │ ? 接收JSON数据             │
│ ? 发送JSON到服务器         │━━━?│ ?? 显示手势历史             │
│                            │    │ ? 执行对应动作             │
│ 真实摄像头调用              │    │ 无摄像头调用                │
└─────────────────────────────┘    └─────────────────────────────┘
```

## 网络配置

两个项目都配置为使用以下Socket地址：

- **IP地址**: `192.168.31.247`
- **IP地址**: `127.0.0.1` (本地回环地址)

- **端口**: `65432`

## 启动步骤

### 第一步：启动服务器端 (project)

1. 打开终端并进入project目录：

```bash
cd project
```

2. 确保依赖已安装：

```bash
pip install -r requirements.txt
```

3. 启动项目：

```bash
python app.py
```

4. 在GUI中点击"? 启动Socket服务器"按钮启动Socket服务器

### 第二步：启动客户端 (dyn_gestures)

1. 打开另一个终端并进入dyn_gestures目录：

```bash
cd dyn_gestures
```

2. 确保依赖已安装：

```bash
pip install -r requirements.txt
```

3. 启动手势识别：

```bash
python main.py
```

## 测试通信

### 1. 连接测试

- 启动`dyn_gestures`后，应该在`project`的GUI中看到客户端连接消息
- 状态栏会显示"客户端已连接: 127.0.0.1:xxxx"

### 2. 手势测试

在`dyn_gestures`的摄像头界面中执行以下手势：

#### 静态手势测试

- **数字1** - 竖起食指
- **数字2** - 竖起食指和中指
- **数字3** - 竖起食指、中指和无名指
- **竖大拇指** - 竖起大拇指，其他手指收拢
- **倒大拇指** - 大拇指向下，其他手指收拢

#### 动态手势测试

- **握拳** - 从张开的手变成握拳
- **张开手** - 从握拳变成张开的手
- **左右挥动** - 手掌左右快速移动
- **翻转手掌** - 手掌翻转

### 3. 观察结果

在`project`的GUI中您应该看到：

- **最近手势** 显示检测到的手势信息（图标化显示）
- **手势历史** 标签页实时显示所有手势记录和统计
- **日志窗口** 显示详细的通信和执行信息

#### 新增功能：手势历史记录 ?

- **实时记录** - 所有手势都会记录在"? 手势历史"标签页
- **详细信息** - 显示手势名称、手部类型、置信度、时间戳
- **统计分析** - 手势使用排行、手部使用分布、类型统计
- **可视化显示** - 彩色图标和状态指示器

## 故障排除

### 连接问题

1. **端口被占用**：
   - 确保端口65432没有被其他程序占用
   - 在Windows上可以使用: `netstat -an | findstr 65432`

2. **IP地址问题**：
   - 确保两个项目配置中的IP地址一致
   - 如果在同一台机器上运行，可以改为`127.0.0.1`或`localhost`

3. **防火墙**：
   - 确保防火墙允许端口65432的通信

### 修改IP地址（如果需要）

如果需要修改IP地址，请同时修改两个配置文件：

1. **project/config.py**:

```python
SOCKET_SERVER_HOST = "127.0.0.1"  # 改为新的IP
SOCKET_SERVER_PORT = 65432
```

2. **dyn_gestures/config.py**:

```python
SOCKET_HOST = '127.0.0.1'  # 改为新的IP
SOCKET_PORT = 65432
```

### 手势识别问题

1. **摄像头权限** - 确保dyn_gestures有摄像头访问权限
2. **光线条件** - 确保有足够的光线进行手势识别
3. **手的位置** - 将手放在摄像头可见范围内

## 高级配置

### 调试模式

如需查看详细的Socket通信日志，可以在代码中启用调试模式：

在 `project/core/socket_server.py` 中：

```python
self.debug_mode = True  # 启用调试输出
```

### 手势输出格式

在 `dyn_gestures/config.py` 中可以修改输出格式：

```python
DISPLAY_CONFIG = {
    'gesture_output': {
        'socket_format': 'json',  # 或 'simple'
    }
}
```

## 数据格式

`dyn_gestures`发送的JSON数据格式示例：

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

## ? 快速验证

### 验证project不调用摄像头

1. 只启动 `project/app.py`
2. 点击"? 启动Socket服务器"
3. 观察：**不会有摄像头指示灯亮起**
4. 任务管理器中也不会显示摄像头占用

### 验证Socket通信

```bash
# 可以先用测试脚本验证
python test_socket_communication.py
```

## 成功标志

通信成功建立的标志：

1. ? project GUI显示"Socket服务器已启动"
2. ? dyn_gestures启动时显示Socket连接成功信息  
3. ? dyn_gestures有摄像头窗口显示，project没有
4. ? 执行手势时project GUI实时显示手势信息
5. ? project日志显示"检测到手势"和"执行动作"信息
