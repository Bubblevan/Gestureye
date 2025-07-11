"""
配置文件 - 存储所有配置参数
"""

# 日志路径
LOG_PATH = "logs/app.log"

# Socket服务器配置
SOCKET_SERVER_HOST = "127.0.0.1"  # 本地回环地址
SOCKET_SERVER_PORT = 65432

# 通信方式配置
CONNECTION_TYPE = 'serial'  # 通信模式：'socket' 或 'serial' (蓝牙)

# 蓝牙配置
BLUETOOTH_MAC = "XX:XX:XX:XX:XX:XX"  # 蓝牙MAC地址（自动检测，Linux用户请手动配置）
BLUETOOTH_PORT = 4  # 蓝牙RFCOMM端口
BLUETOOTH_ENABLED = True  # 是否启用蓝牙功能

# Linux用户获取蓝牙MAC地址的方法：
# 1. 命令行: hciconfig 或 bluetoothctl show
# 2. 系统文件: cat /sys/class/bluetooth/hci0/address
# 3. 将获取到的MAC地址填入上面的BLUETOOTH_MAC字段
