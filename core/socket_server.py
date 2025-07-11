"""
Socket服务器模块 - 接收手势识别数据
"""

import socket
import threading
import json
import time
from typing import Optional, Callable, Dict, Any
from PyQt6.QtCore import QObject, pyqtSignal


class SocketServer(QObject):
    """Socket服务器类 - 接收手势识别数据并发送信号"""
    
    # PyQt6信号，用于将数据传递给主线程
    gesture_received = pyqtSignal(dict)  # 接收到手势数据
    client_connected = pyqtSignal(str)   # 客户端连接
    client_disconnected = pyqtSignal(str)  # 客户端断开连接
    server_status_changed = pyqtSignal(str)  # 服务器状态变化
    
    def __init__(self, host: str = "192.168.31.247", port: int = 65432):
        super().__init__()
        self.host = host
        self.port = port
        self.server_socket: Optional[socket.socket] = None
        self.is_running = False
        self.server_thread: Optional[threading.Thread] = None
        self.client_threads = []
        self.debug_mode = True
        
    def start_server(self) -> bool:
        """启动Socket服务器"""
        if self.is_running:
            self._emit_status("服务器已在运行")
            return True
            
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            
            self.is_running = True
            self.server_thread = threading.Thread(target=self._server_loop, daemon=True)
            self.server_thread.start()
            
            self._emit_status(f"Socket服务器已启动，监听 {self.host}:{self.port}")
            return True
            
        except Exception as e:
            self._emit_status(f"启动服务器失败: {e}")
            return False
    
    def stop_server(self):
        """停止Socket服务器"""
        if not self.is_running:
            return
            
        self.is_running = False
        
        # 关闭服务器套接字
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
            self.server_socket = None
            
        # 等待服务器线程结束
        if self.server_thread and self.server_thread.is_alive():
            self.server_thread.join(timeout=2)
            
        self._emit_status("Socket服务器已停止")
    
    def _server_loop(self):
        """服务器主循环"""
        while self.is_running and self.server_socket:
            try:
                # 设置短超时，以便能够响应停止信号
                self.server_socket.settimeout(1.0)
                client_socket, client_address = self.server_socket.accept()
                
                if self.is_running:
                    # 为每个客户端创建处理线程
                    client_thread = threading.Thread(
                        target=self._handle_client,
                        args=(client_socket, client_address),
                        daemon=True
                    )
                    client_thread.start()
                    self.client_threads.append(client_thread)
                    
                    self._emit_client_connected(f"{client_address[0]}:{client_address[1]}")
                    
            except socket.timeout:
                # 超时是正常的，继续循环
                continue
            except OSError:
                # 套接字被关闭，退出循环
                break
            except Exception as e:
                if self.is_running:
                    self._emit_status(f"服务器错误: {e}")
                break
    
    def _handle_client(self, client_socket: socket.socket, client_address):
        """处理客户端连接"""
        try:
            with client_socket:
                while self.is_running:
                    # 设置接收超时
                    client_socket.settimeout(1.0)
                    
                    try:
                        data = client_socket.recv(1024)
                        if not data:
                            break
                            
                        # 解码消息
                        message = data.decode('utf-8')
                        if self.debug_mode:
                            print(f"[SOCKET] 收到来自 {client_address} 的消息: {message}")
                        
                        # 尝试解析JSON数据
                        try:
                            gesture_data = json.loads(message)
                            # 发送信号到主线程
                            self.gesture_received.emit(gesture_data)
                        except json.JSONDecodeError:
                            # 如果不是JSON，作为普通文本处理
                            gesture_data = {
                                'type': 'text',
                                'message': message,
                                'timestamp': time.time(),
                                'client': f"{client_address[0]}:{client_address[1]}"
                            }
                            self.gesture_received.emit(gesture_data)
                        
                        # 发送确认响应
                        response = "数据已接收"
                        client_socket.sendall(response.encode('utf-8'))
                        
                    except socket.timeout:
                        # 接收超时，继续循环
                        continue
                    except ConnectionResetError:
                        # 客户端断开连接
                        break
                        
        except Exception as e:
            if self.debug_mode:
                print(f"[SOCKET] 处理客户端 {client_address} 时出错: {e}")
        finally:
            self._emit_client_disconnected(f"{client_address[0]}:{client_address[1]}")
    
    def _emit_status(self, message: str):
        """发送状态消息信号"""
        if self.debug_mode:
            print(f"[SOCKET] {message}")
        self.server_status_changed.emit(message)
    
    def _emit_client_connected(self, client_info: str):
        """发送客户端连接信号"""
        if self.debug_mode:
            print(f"[SOCKET] 客户端已连接: {client_info}")
        self.client_connected.emit(client_info)
    
    def _emit_client_disconnected(self, client_info: str):
        """发送客户端断开连接信号"""
        if self.debug_mode:
            print(f"[SOCKET] 客户端已断开: {client_info}")
        self.client_disconnected.emit(client_info)
    
    def get_status(self) -> Dict[str, Any]:
        """获取服务器状态"""
        return {
            'running': self.is_running,
            'host': self.host,
            'port': self.port,
            'active_threads': len([t for t in self.client_threads if t.is_alive()])
        }


class BluetoothServer(QObject):
    """蓝牙RFCOMM服务器类 - 使用普通socket接收手势识别数据并发送信号"""
    
    # PyQt6信号，用于将数据传递给主线程
    gesture_received = pyqtSignal(dict)  # 接收到手势数据
    client_connected = pyqtSignal(str)   # 客户端连接
    client_disconnected = pyqtSignal(str)  # 客户端断开连接
    server_status_changed = pyqtSignal(str)  # 服务器状态变化
    
    def __init__(self, host: str = "", port: int = 4):
        super().__init__()
        self.host = host  # 蓝牙MAC地址，空字符串表示自动选择
        self.port = port  # RFCOMM端口
        self.server_socket: Optional[socket.socket] = None
        self.is_running = False
        self.server_thread: Optional[threading.Thread] = None
        self.client_threads = []
        self.debug_mode = True
        self.bluetooth_available = self._check_bluetooth_support()
        self.local_mac_address = None  # 存储本机MAC地址
        
    def _check_bluetooth_support(self) -> bool:
        """检查系统是否支持蓝牙socket"""
        try:
            # 尝试访问蓝牙相关的socket常量
            socket.AF_BLUETOOTH
            socket.BTPROTO_RFCOMM
            return True
        except AttributeError:
            return False
    
    def _get_local_bluetooth_mac(self) -> Optional[str]:
        """获取本机蓝牙MAC地址"""
        try:
            import platform
            import re
            
            system = platform.system()
            
            # 首先检查配置文件中的手动配置
            try:
                import config
                if hasattr(config, 'BLUETOOTH_MAC') and config.BLUETOOTH_MAC != "XX:XX:XX:XX:XX:XX":
                    manual_mac = config.BLUETOOTH_MAC.strip()
                    if re.match(r'^[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}$', manual_mac):
                        print(f"[BLUETOOTH] 使用手动配置的MAC地址: {manual_mac}")
                        return manual_mac.lower()  # 确保小写格式
            except Exception as e:
                print(f"[BLUETOOTH] 读取手动配置失败: {e}")
            
            # 方法1: 使用socket直接获取蓝牙地址
            if self.bluetooth_available:
                try:
                    # 创建临时蓝牙socket并获取本地地址
                    temp_socket = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
                    temp_socket.bind(("", 0))  # 绑定到任意可用端口
                    local_addr = temp_socket.getsockname()
                    temp_socket.close()
                    if local_addr and local_addr[0] and local_addr[0] != "00:00:00:00:00:00":
                        return local_addr[0].upper()
                except Exception:
                    pass
            
            # 方法2: 根据平台使用不同的Python库
            if system == "Linux":
                try:
                    # Linux: 读取系统文件
                    import glob
                    import os
                    bluetooth_dirs = glob.glob('/sys/class/bluetooth/hci*')
                    for bt_dir in bluetooth_dirs:
                        address_file = os.path.join(bt_dir, 'address')
                        if os.path.exists(address_file):
                            with open(address_file, 'r') as f:
                                mac = f.read().strip().upper()
                                if re.match(r'^[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}$', mac):
                                    return mac
                except Exception:
                    pass
                    
            elif system == "Windows":
                # Windows: 使用多种方法获取本机蓝牙适配器MAC地址
                
                # 方法1: 使用WMI查询网络适配器（最准确）
                try:
                    import wmi
                    c = wmi.WMI()
                    
                    # 查询网络适配器，寻找蓝牙网络连接
                    for adapter in c.Win32_NetworkAdapter():
                        if adapter.MACAddress and adapter.NetConnectionID:
                            # 检查是否是蓝牙网络连接
                            if ('蓝牙' in adapter.NetConnectionID or 
                                'bluetooth' in adapter.NetConnectionID.lower() or
                                'Bluetooth' in adapter.NetConnectionID):
                                mac = adapter.MACAddress.replace('-', ':').lower()  # 转换为小写
                                print(f"[BLUETOOTH] 找到蓝牙网络适配器: {adapter.NetConnectionID} -> {mac}")
                                if re.match(r'^[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}$', mac):
                                    return mac
                    
                    # 如果没找到中文"蓝牙"，尝试查找描述中包含蓝牙的适配器
                    for adapter in c.Win32_NetworkAdapter():
                        if adapter.MACAddress and adapter.Description:
                            if ('bluetooth' in adapter.Description.lower() and 
                                'network' in adapter.Description.lower()):
                                mac = adapter.MACAddress.replace('-', ':').lower()  # 转换为小写
                                print(f"[BLUETOOTH] 找到蓝牙适配器: {adapter.Description} -> {mac}")
                                if re.match(r'^[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}$', mac):
                                    return mac
                                    
                except ImportError:
                    print("[BLUETOOTH] 请安装wmi库: pip install wmi")
                except Exception as e:
                    print(f"[BLUETOOTH] WMI查询失败: {e}")
                
                # 方法2: 使用psutil查询网络接口
                try:
                    import psutil
                    net_if_addrs = psutil.net_if_addrs()
                    net_if_stats = psutil.net_if_stats()
                    
                    for interface_name, interface_addresses in net_if_addrs.items():
                        # 查找蓝牙相关的网络接口
                        if ('蓝牙' in interface_name or 
                            'bluetooth' in interface_name.lower() or 
                            'bt' in interface_name.lower()):
                            
                            for address in interface_addresses:
                                if hasattr(psutil, 'AF_LINK') and address.family == psutil.AF_LINK:
                                    mac = address.address.replace('-', ':').lower()  # 转换为小写
                                    print(f"[BLUETOOTH] psutil找到蓝牙接口: {interface_name} -> {mac}")
                                    if re.match(r'^[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}$', mac):
                                        return mac
                                        
                except ImportError:
                    print("[BLUETOOTH] 请安装psutil库: pip install psutil")
                except Exception as e:
                    print(f"[BLUETOOTH] psutil查询失败: {e}")
                
                # 方法3: 使用Windows注册表（查找本机适配器，不是已配对设备）
                try:
                    import winreg
                    
                    # 查询本机蓝牙适配器的注册表项
                    adapter_keys = [
                        r"SYSTEM\CurrentControlSet\Services\BTHPORT\Parameters",
                        r"SYSTEM\CurrentControlSet\Control\Class\{e0cbf06c-cd8b-4647-bb8a-263b43f0f974}"  # 蓝牙适配器类
                    ]
                    
                    for adapter_key in adapter_keys:
                        try:
                            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, adapter_key) as key:
                                try:
                                    # 尝试读取LocalRadioAddress
                                    local_mac, _ = winreg.QueryValueEx(key, "LocalRadioAddress")
                                    if local_mac and isinstance(local_mac, bytes) and len(local_mac) >= 6:
                                        mac = ':'.join(f'{b:02x}' for b in local_mac[:6])  # 转换为小写
                                        print(f"[BLUETOOTH] 注册表找到本机适配器: {mac}")
                                        return mac
                                except FileNotFoundError:
                                    pass
                        except FileNotFoundError:
                            continue
                            
                except ImportError:
                    print("[BLUETOOTH] Windows注册表访问失败")
                except Exception as e:
                    print(f"[BLUETOOTH] 注册表查询失败: {e}")
                
                # 如果所有方法都失败，提示用户手动获取
                print("[BLUETOOTH] 自动获取失败，建议使用命令: getmac /v")
                    
            elif system == "Darwin":  # macOS
                try:
                    # macOS: 使用psutil
                    import psutil
                    net_if_addrs = psutil.net_if_addrs()
                    for interface_name, interface_addresses in net_if_addrs.items():
                        if 'bluetooth' in interface_name.lower() or 'bt' in interface_name.lower():
                            for address in interface_addresses:
                                if hasattr(psutil, 'AF_LINK') and address.family == psutil.AF_LINK:
                                    mac = address.address.upper()
                                    if re.match(r'^[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}$', mac):
                                        return mac
                except ImportError:
                    print("[BLUETOOTH] 请安装psutil库: pip install psutil")
                except Exception as e:
                    print(f"[BLUETOOTH] macOS psutil查询失败: {e}")
            
            # 注意：不使用uuid.getnode()，因为它返回的是网络接口MAC，不是蓝牙MAC
            # 这会误导用户
                    
        except Exception as e:
            print(f"[BLUETOOTH] 获取本机MAC地址时出错: {e}")
            
        return None
        
    def start_server(self) -> bool:
        """启动蓝牙RFCOMM服务器 - 使用普通socket"""
        if not self.bluetooth_available:
            self._emit_status("系统不支持蓝牙RFCOMM协议，请安装 pybluez: pip install pybluez")
            return False
            
        if self.is_running:
            self._emit_status("蓝牙服务器已在运行")
            return True
            
        try:
            # 获取本机蓝牙MAC地址
            self.local_mac_address = self._get_local_bluetooth_mac()
            
            # 创建蓝牙RFCOMM socket - 使用普通socket而不是pybluez
            self.server_socket = socket.socket(
                socket.AF_BLUETOOTH, 
                socket.SOCK_STREAM, 
                socket.BTPROTO_RFCOMM
            )
            
            # 绑定到本地蓝牙适配器和RFCOMM端口
            # 对于蓝牙服务器，通常使用空字符串让系统自动选择适配器
            # 或者使用获取到的MAC地址
            if self.local_mac_address:
                bind_host = self.local_mac_address
            else:
                bind_host = ""  # 空字符串让系统自动选择
                
            print(f"[BLUETOOTH] 尝试绑定到: {bind_host}:{self.port}")
            self.server_socket.bind((bind_host, self.port))
            
            # 开始监听，1表示允许的最大挂起连接数为1
            self.server_socket.listen(1)
            
            self.is_running = True
            self.server_thread = threading.Thread(target=self._server_loop, daemon=True)
            self.server_thread.start()
            
            # 显示启动信息
            if self.local_mac_address:
                self._emit_status(f"蓝牙RFCOMM服务器已启动，监听 {self.local_mac_address}:{self.port}")
            else:
                self._emit_status(f"蓝牙RFCOMM服务器已启动，监听端口 {self.port}")
            
            return True
            
        except Exception as e:
            self._emit_status(f"启动蓝牙服务器失败: {e}")
            return False
    
    def stop_server(self):
        """停止蓝牙RFCOMM服务器"""
        if not self.is_running:
            return
            
        self.is_running = False
        
        # 关闭服务器套接字
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
            self.server_socket = None
            
        # 等待服务器线程结束
        if self.server_thread and self.server_thread.is_alive():
            self.server_thread.join(timeout=2)
            
        self._emit_status("蓝牙RFCOMM服务器已停止")
    
    def _server_loop(self):
        """蓝牙服务器主循环"""
        while self.is_running and self.server_socket:
            try:
                # 设置短超时，以便能够响应停止信号
                self.server_socket.settimeout(1.0)
                client_socket, client_info = self.server_socket.accept()
                
                if self.is_running:
                    # 为每个客户端创建处理线程
                    client_thread = threading.Thread(
                        target=self._handle_client,
                        args=(client_socket, client_info),
                        daemon=True
                    )
                    client_thread.start()
                    self.client_threads.append(client_thread)
                    
                    self._emit_client_connected(f"{client_info[0]}")
                    
            except socket.timeout:
                # 超时是正常的，继续循环
                continue
            except OSError:
                # 套接字被关闭，退出循环
                break
            except Exception as e:
                if self.is_running:
                    self._emit_status(f"蓝牙服务器错误: {e}")
                break
    
    def _handle_client(self, client_socket: socket.socket, client_info):
        """处理蓝牙客户端连接"""
        try:
            with client_socket:
                while self.is_running:
                    # 设置接收超时
                    client_socket.settimeout(1.0)
                    
                    try:
                        # 从客户端接收数据，缓冲区大小为1024字节
                        data = client_socket.recv(1024)
                        if not data:
                            break
                            
                        # 将收到的字节解码为字符串
                        message = data.decode('utf-8')
                        if self.debug_mode:
                            print(f"[BLUETOOTH] 收到来自 {client_info[0]} 的消息: {message}")
                        
                        # 尝试解析JSON数据
                        try:
                            gesture_data = json.loads(message)
                            # 发送信号到主线程
                            self.gesture_received.emit(gesture_data)
                        except json.JSONDecodeError:
                            # 如果不是JSON，作为普通文本处理
                            gesture_data = {
                                'type': 'text',
                                'message': message,
                                'timestamp': time.time(),
                                'client': client_info[0]
                            }
                            self.gesture_received.emit(gesture_data)
                        
                        # 构造回复消息并发送给客户端
                        response = "服务器已收到你的消息"
                        client_socket.sendall(response.encode('utf-8'))
                        
                    except socket.timeout:
                        # 接收超时，继续循环
                        continue
                    except ConnectionResetError:
                        # 客户端断开连接
                        break
                        
        except Exception as e:
            if self.debug_mode:
                print(f"[BLUETOOTH] 处理客户端 {client_info[0]} 时出错: {e}")
        finally:
            self._emit_client_disconnected(f"{client_info[0]}")
    
    def _emit_status(self, message: str):
        """发送状态消息信号"""
        if self.debug_mode:
            print(f"[BLUETOOTH] {message}")
        self.server_status_changed.emit(message)
    
    def _emit_client_connected(self, client_info: str):
        """发送客户端连接信号"""
        if self.debug_mode:
            print(f"[BLUETOOTH] 客户端已连接: {client_info}")
        self.client_connected.emit(client_info)
    
    def _emit_client_disconnected(self, client_info: str):
        """发送客户端断开连接信号"""
        if self.debug_mode:
            print(f"[BLUETOOTH] 客户端已断开: {client_info}")
        self.client_disconnected.emit(client_info)
    
    def get_status(self) -> Dict[str, Any]:
        """获取蓝牙服务器状态"""
        return {
            'running': self.is_running,
            'host': self.local_mac_address or self.host,
            'port': self.port,
            'active_threads': len([t for t in self.client_threads if t.is_alive()]),
            'bluetooth_available': self.bluetooth_available,
            'local_mac_address': self.local_mac_address
        }


class GestureHandler(QObject):
    """手势处理器 - 处理接收到的手势数据"""
    
    # 处理后的手势信号
    gesture_processed = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.gesture_history = []
        self.max_history = 100
        
    def handle_gesture_data(self, gesture_data: Dict[str, Any]):
        """处理手势数据"""
        try:
            # 添加处理时间戳
            processed_data = gesture_data.copy()
            processed_data['processed_timestamp'] = time.time()
            
            # 存储到历史记录
            self.gesture_history.append(processed_data)
            if len(self.gesture_history) > self.max_history:
                self.gesture_history.pop(0)
            
            # 判断数据类型 - 支持多种格式
            if 'gesture' in processed_data and 'gesture_type' in processed_data:
                # dyn_gestures项目的手势数据格式
                processed_data['type'] = 'gesture_detection'
                self._handle_gesture_detection(processed_data)
            elif processed_data.get('type') == 'gesture_detection':
                # 标准格式的手势数据
                self._handle_gesture_detection(processed_data)
            elif processed_data.get('type') == 'trail_change':
                # 轨迹变化数据
                self._handle_trail_change(processed_data)
            elif processed_data.get('type') == 'text':
                # 文本消息
                self._handle_text_message(processed_data)
            elif 'message' in processed_data:
                # 简单文本消息
                processed_data['type'] = 'text'
                self._handle_text_message(processed_data)
            else:
                # 未知格式
                self._handle_unknown_message(processed_data)
                
            # 发送处理后的数据
            self.gesture_processed.emit(processed_data)
            
        except Exception as e:
            print(f"[GESTURE_HANDLER] 处理手势数据时出错: {e}")
    
    def _handle_gesture_detection(self, data: Dict[str, Any]):
        """处理手势检测数据"""
        gesture_name = data.get('gesture', 'Unknown')
        hand_type = data.get('hand_type', 'Unknown')
        confidence = data.get('confidence', 0)
        
        print(f"[GESTURE] 检测到手势: {gesture_name} ({hand_type} 手, 置信度: {confidence})")
        
        # 这里可以添加具体的手势响应逻辑
        # 例如：执行对应的操作、更新UI等
        
    def _handle_trail_change(self, data: Dict[str, Any]):
        """处理轨迹变化数据"""
        details = data.get('details', {})
        dx = details.get('dx', 0)
        dy = details.get('dy', 0)
        distance = details.get('distance', 0)
        hand_type = data.get('hand_type', 'Unknown')
        
        print(f"[TRAIL] 轨迹变化: {hand_type}手 dx={dx}, dy={dy}, distance={distance:.1f}")
    
    def _handle_text_message(self, data: Dict[str, Any]):
        """处理文本消息"""
        message = data.get('message', '')
        client = data.get('client', 'Unknown')
        
        print(f"[TEXT] 来自 {client} 的消息: {message}")
    
    def _handle_unknown_message(self, data: Dict[str, Any]):
        """处理未知类型消息"""
        print(f"[UNKNOWN] 收到未知类型数据: {data}")
    
    def get_gesture_history(self) -> list:
        """获取手势历史记录"""
        return self.gesture_history.copy()
    
    def clear_history(self):
        """清空历史记录"""
        self.gesture_history.clear() 