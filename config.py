"""
配置文件 - 存储所有配置参数
"""

# 日志路径
LOG_PATH = "logs/app.log"

# Socket服务器配置
SOCKET_SERVER_HOST = "10.162.34.40"  # 本地回环地址
SOCKET_SERVER_PORT = 65432

# 通信方式配置
CONNECTION_TYPE = 'socket'  # 通信模式：'socket' 或 'serial' (蓝牙)

# 蓝牙配置
BLUETOOTH_MAC = "XX:XX:XX:XX:XX:XX"  # 蓝牙MAC地址（自动检测）
BLUETOOTH_PORT = 4  # 蓝牙RFCOMM端口
BLUETOOTH_ENABLED = True  # 是否启用蓝牙功能
