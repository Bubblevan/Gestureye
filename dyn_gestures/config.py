"""
配置文件 - 存储所有配置参数
"""

# 摄像头配置
CAMERA_INDEX = 0
CAMERA_FPS = 60  # 摄像头帧率设置
CAMERA_FRAME_WIDTH = 640  # 摄像头帧宽度
CAMERA_FRAME_HEIGHT = 360  # 摄像头帧高度

# 手势检测配置
HAND_DETECTION_CONFIG = {
    'static_mode': False,      # 是否使用静态模式
    'max_hands': 2,           # 最大检测手数
    'model_complexity': 1,    # 模型复杂度 (0-2)
    'detection_confidence': 0.5,        # 检测置信度
    'min_tracking_confidence': 0.5      # 最小跟踪置信度
}

# 手势识别参数
GESTURE_CONFIG = {
    # 握拳到张开手势
    'hand_open': {
        'history_length': 10,
        'variance_change_percent': 50,
        'distance_multiplier': 1.5
    },
    
    # V字手势
    'peace_sign': {
        'distance_threshold_percent': 0.6,  # 手指伸展阈值（相对于手掌基准长度）
        'required_frames': 15  # 需要连续检测的帧数
    },
    
    # 竖大拇指
    'thumbs_up': {
        'thumb_distance_threshold': 0.6,        # 大拇指指尖距离掌心阈值（百分比）
        'other_fingers_threshold': 0.45,        # 其他手指指尖距离掌心阈值（百分比）
        'thumb_angle_threshold': 45.0,          # 大拇指角度阈值（度）
        'thumb_isolation_threshold': 0.5,       # 大拇指与其他手指PIP最小距离阈值（百分比）
        'required_frames': 15                   # 需要连续检测的帧数
    },

    # 倒竖大拇指
    'thumbs_down': {
        'thumb_distance_threshold': 0.6,        # 大拇指指尖距离掌心阈值（百分比）
        'other_fingers_threshold': 0.45,        # 其他手指指尖距离掌心阈值（百分比）
        'thumb_angle_threshold': 45.0,          # 大拇指角度阈值（度）
        'thumb_isolation_threshold': 0.5,       # 大拇指与其他手指PIP最小距离阈值（百分比）
        'required_frames': 15                   # 需要连续检测的帧数
    },

    # OK手势
    'ok_sign': {
        'circle_threshold': 0.15,               # 圆圈检测阈值（相对于手掌基准长度）
        'other_fingers_threshold': 0.6,         # 其他手指伸展阈值
        'required_frames': 15                   # 需要连续检测的帧数
    },

    # 滑动手势
    'swipe': {
        'history_length': 10,                   # 历史记录长度
        'min_swipe_distance': 0.3,              # 最小滑动距离（相对于手掌基准长度）
        'min_swipe_speed': 0.1,                 # 最小滑动速度
        'required_frames': 5,                   # 需要连续检测的帧数
        'palm_angle_threshold': 45.0            # 手掌角度变化阈值（度）
    }
}

# 手势类型定义
GESTURE_TYPES = {
    'static_gestures': ['PeaceSign', 'ThumbsUp', 'ThumbsDown', 'OKSign'],  # 静态手势列表
    'dynamic_gestures': ['HandOpen', 'SwipeLeft', 'SwipeRight', 'SwipeUp', 'SwipeDown'],  # 动态手势列表
    'confidence_threshold_for_update': 5.0  # 静态手势置信度变化阈值
}

# 显示配置
DISPLAY_CONFIG = {
    'window_name': 'Hand Gesture Detection',
    'show_palm_center': True,
    'show_landmarks': True,
    'flip_image': True,                 # cvzone的flipType参数
    'show_camera_window': True,         # 是否显示摄像头识别画面
    'gesture_message_duration': 15,     # 帧数
    'show_fps': True,                   # 显示FPS
    'fps_update_interval': 10           # FPS更新间隔（帧数）
}

# 颜色配置 (BGR格式)
COLORS = {
    'palm_center': (0, 255, 255),      # 黄色
    'text_primary': (255, 0, 0),       # 蓝色
    'text_secondary': (0, 0, 255),     # 红色
    'gesture_message': (0, 255, 0),    # 绿色
    'palm_info': (0, 255, 255),        # 青色
    'fps_text': (255, 255, 255)        # 白色 - FPS文本颜色
}

# 蓝牙配置
BLUETOOTH_CONFIG = {
    'enabled': False,                    # 是否启用蓝牙接收模式
    'server_port': 1,                   # 蓝牙服务端口号 (RFCOMM channel)
    'server_uuid': '94f39d29-7d6d-437d-973b-fba39e49d4ee',  # 服务UUID
    'device_name': 'HandGestureReceiver',  # 设备名称
    'max_packet_size': 1024,            # 最大数据包大小（字节）
    'connection_timeout': 10.0,         # 连接超时时间（秒）
    'heartbeat_interval': 5.0,          # 心跳间隔（秒）
    'reconnect_attempts': 3,            # 重连尝试次数
    'protocol_version': '1.0',          # 协议版本
    'buffer_size': 4096,                # 接收缓冲区大小
    'data_validation': True,            # 是否启用数据校验
    'auto_gesture_detection': True      # 是否自动进行手势检测（从蓝牙数据）
}

# 蓝牙数据包类型定义
BLUETOOTH_PACKET_TYPES = {
    'HAND_LANDMARKS': 0x01,
    'GESTURE_RESULT': 0x02,
    'COMBINED_DATA': 0x03,
    'HEARTBEAT': 0x04,
    'CONFIG_REQUEST': 0x05,
    'STATUS_REPORT': 0x06
}

# 蓝牙协议常量
BLUETOOTH_PROTOCOL = {
    'PACKET_HEADER': 0xAA55,            # 包头
    'PACKET_FOOTER': 0x55AA,            # 包尾
    'MAX_RETRIES': 3,                   # 最大重试次数
    'TIMEOUT_MS': 1000,                 # 超时时间（毫秒）
    'HEARTBEAT_TIMEOUT_MS': 5000        # 心跳超时时间（毫秒）
}

# 日志路径
LOG_PATH = "logs/app.log"
