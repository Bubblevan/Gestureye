"""
使用Qt Designer设计的主窗口 - 响应式布局版本
"""

import os
import platform
from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow, QApplication
from PyQt6.QtCore import pyqtSignal, QSettings, Qt, QTimer, QSize
from PyQt6.QtGui import QKeySequence, QShortcut, QIcon
from .threads.socket_gesture_receiver import SocketGestureReceiverThread
from .widgets.gesture_history_widget import GestureHistoryWidget
from core.gesture_bindings import GestureBindings
from core.action_executor import ActionExecutor

# 获取.ui文件的绝对路径
UI_FILE = os.path.join(os.path.dirname(__file__), 'main_window.ui')

class MainWindowUI(QMainWindow):
    """基于.ui文件的主窗口类 - 响应式布局版本"""
    
    def __init__(self):
        super().__init__()
        
        # 加载.ui文件
        if os.path.exists(UI_FILE):
            uic.loadUi(UI_FILE, self)
        else:
            raise FileNotFoundError(f"UI文件不存在: {UI_FILE}")
            
        # 设置窗口图标
        self.setup_window_icon()
            
        # 初始化设置
        self.settings = QSettings('GestureDetection', 'MainWindow')
        self.debug_mode = False
        self.expanded_view = False
        self.is_detecting = False
        
        # 拖拽状态管理
        self.is_dragging = False
        self.last_gesture = None
        self.drag_gesture_timeout = 3.0  # 拖拽模式超时时间（秒）
        self.last_gesture_time = 0
        
        # 响应式布局设置 - 重构为以水平宽度为主的布局管理
        self.compact_width_threshold = 800  # 调整紧凑模式的宽度阈值，考虑手势历史组件的宽度需求
        self.auto_layout = True  # 自动布局管理
        self.min_content_width = 600  # 内容区域最小宽度，确保手势历史组件不会溢出
        
        # 初始化业务逻辑
        self.gesture_bindings = GestureBindings()
        self.action_executor = ActionExecutor()
        self.detection_thread = None
        
        # 初始化通信配置
        self.current_connection_type = self.read_connection_type()
        
        # 初始化手势历史记录组件
        self.gesture_history_widget = GestureHistoryWidget()
        self.gesture_history_widget.clear_history_requested.connect(self.clear_gesture_history)
        
        # 连接信号和槽
        self.setup_connections()
        
        # 设置快捷键
        self.setup_shortcuts()
        
        # 初始化UI状态
        self.init_ui_state()
        
        # 恢复设置
        self.restore_settings()
        
        # 设置响应式布局定时器
        self.layout_timer = QTimer()
        self.layout_timer.timeout.connect(self.update_responsive_layout)
        self.layout_timer.setSingleShot(True)
        
        # 手势历史组件将在展开视图中显示，不再作为标签页
        # 延迟设置手势历史组件到右边栏，确保UI完全初始化后再添加
        QTimer.singleShot(100, self.setup_gesture_history_sidebar)
    
    def setup_window_icon(self):
        """设置窗口图标（跨平台优化）"""
        try:
            # 获取当前操作系统
            current_os = platform.system()
            
            # 获取项目根目录（相对于当前文件位置）
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)  # 回到project目录
            icon_path = os.path.join(project_root, "DDYN.png")
            
            if os.path.exists(icon_path):
                icon = QIcon(icon_path)
                
                # 平台特定的图标尺寸优化
                if current_os == "Windows":
                    icon_sizes = [16, 24, 32, 48, 64, 128, 256]
                elif current_os == "Darwin":  # macOS
                    icon_sizes = [16, 32, 64, 128, 256, 512]
                elif current_os == "Linux":
                    icon_sizes = [16, 22, 24, 32, 48, 64, 96, 128, 256]
                else:
                    icon_sizes = [16, 24, 32, 48, 64, 128, 256]
                
                # 添加多种尺寸的图标以确保在不同场景下正确显示
                for size in icon_sizes:
                    icon.addFile(icon_path, QSize(size, size), QIcon.Mode.Normal, QIcon.State.Off)
                
                # 设置窗口图标
                self.setWindowIcon(icon)
                
                # 同时设置应用程序图标（如果当前窗口是主窗口）
                app = QApplication.instance()
                if app:
                    app.setWindowIcon(icon)
                
                # 强制刷新窗口以确保图标更新
                self.update()
                
                print(f"窗口图标设置成功 ({current_os}): {icon_path}")
                print(f"窗口图标尺寸: {icon_sizes}")
            else:
                print(f"警告: 图标文件不存在: {icon_path}")
                # 尝试查找可能的图标路径
                possible_paths = [
                    os.path.join(project_root, "assets", "DDYN.png"),
                    os.path.join(project_root, "images", "DDYN.png"),
                    os.path.join(project_root, "resources", "DDYN.png"),
                ]
                
                # 获取平台特定的图标尺寸
                if current_os == "Windows":
                    icon_sizes = [16, 24, 32, 48, 64, 128, 256]
                elif current_os == "Darwin":
                    icon_sizes = [16, 32, 64, 128, 256, 512]
                elif current_os == "Linux":
                    icon_sizes = [16, 22, 24, 32, 48, 64, 96, 128, 256]
                else:
                    icon_sizes = [16, 24, 32, 48, 64, 128, 256]
                
                for path in possible_paths:
                    if os.path.exists(path):
                        icon = QIcon(path)
                        # 添加多种尺寸
                        for size in icon_sizes:
                            icon.addFile(path, QSize(size, size), QIcon.Mode.Normal, QIcon.State.Off)
                        self.setWindowIcon(icon)
                        app = QApplication.instance()
                        if app:
                            app.setWindowIcon(icon)
                        print(f"在备用位置找到图标 ({current_os}): {path}")
                        break
                
        except Exception as e:
            print(f"设置窗口图标失败: {e}")
    
    def setup_gesture_history_sidebar(self):
        """在展开视图的右边栏中设置手势历史组件"""
        try:
            print("开始设置手势历史右边栏...")
            
            # 检查各个组件是否存在
            if hasattr(self, 'rightSidebar'):
                print("找到rightSidebar组件")
            else:
                print("未找到rightSidebar组件")
                
            if hasattr(self, 'rightSidebarLayout'):
                print("找到rightSidebarLayout布局")
            else:
                print("未找到rightSidebarLayout布局")
                
            if hasattr(self, 'gesture_history_widget'):
                print("找到gesture_history_widget组件")
            else:
                print("未找到gesture_history_widget组件")
            
            # 获取右边栏布局
            if hasattr(self, 'rightSidebarLayout') and hasattr(self, 'gesture_history_widget'):
                # 确保手势历史组件没有其他父对象
                if self.gesture_history_widget.parent():
                    print(f"手势历史组件当前父对象: {self.gesture_history_widget.parent()}")
                    self.gesture_history_widget.setParent(None)
                
                # 将手势历史组件添加到右边栏
                self.rightSidebarLayout.addWidget(self.gesture_history_widget)
                
                # 设置手势历史组件的大小策略
                self.gesture_history_widget.setMaximumWidth(620)
                
                # 强制显示手势历史组件
                self.gesture_history_widget.setVisible(True)
                self.gesture_history_widget.show()
                
                # 强制刷新布局
                self.gesture_history_widget.updateGeometry()
                self.rightSidebar.updateGeometry()
                
                print("手势历史组件已成功添加到右边栏")
                self.log_message("手势历史组件已添加到展开视图右边栏")
            else:
                error_msg = "右边栏布局或手势历史组件未找到，无法添加手势历史组件"
                print(error_msg)
                self.log_message(error_msg)
                
        except Exception as e:
            error_msg = f"设置手势历史右边栏失败: {e}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            self.log_message(error_msg)
    
    def clear_gesture_history(self):
        """清空手势历史记录"""
        try:
            from PyQt6.QtWidgets import QMessageBox
            
            reply = QMessageBox.question(
                self,
                "清空手势历史",
                "确定要清空所有手势历史记录吗？\n\n此操作不可撤销！",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.gesture_history_widget.clear_history()
                self.log_message("手势历史记录已清空")
            else:
                self.log_message("清空手势历史记录已取消")
                
        except Exception as e:
            self.log_message(f"清空手势历史记录失败: {e}")

    
    def setup_connections(self):
        """设置信号连接"""
        # 主要控制按钮
        self.startBtn.clicked.connect(self.toggle_detection)  # 改为切换功能
        # self.stopBtn.clicked.connect(self.stop_detection)  # 移除停止按钮连接
        
        # 调试和视图控制
        self.debugModeBtn.clicked.connect(self.toggle_debug_mode)
        self.actionToggleDebugMode.triggered.connect(self.toggle_debug_mode)
        self.actionToggleExpandedView.triggered.connect(self.toggle_expanded_view)
        
        # 配置相关
        self.actionCustomGestureBindings.triggered.connect(self.open_gesture_binding_config)
        self.actionResetBindings.triggered.connect(self.reset_gesture_bindings)
        
        # 通信相关
        self.actionToggleConnectionType.triggered.connect(self.toggle_connection_type)
        self.actionShowConnectionStatus.triggered.connect(self.show_connection_status)
        
        # 手势历史清理
        self.gesture_history_widget.clear_history_requested.connect(self.clear_gesture_history)
        
        # 设置Socket手势接收线程
        self.detection_thread = SocketGestureReceiverThread()
        self.detection_thread.gesture_detected.connect(self.on_gesture_detected)
        self.detection_thread.gesture_detail_detected.connect(self.on_gesture_detail_detected)
        self.detection_thread.trail_change_detected.connect(self.on_trail_change_detected)
        self.detection_thread.status_updated.connect(self.on_status_updated)
        self.detection_thread.error_occurred.connect(self.on_error_occurred)
    
    def setup_shortcuts(self):
        """设置快捷键"""
        # Ctrl+S 切换检测（启动/停止）
        toggle_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        toggle_shortcut.activated.connect(self.toggle_detection)
        
        # F11 切换展开/紧凑视图
        expand_shortcut = QShortcut(QKeySequence("F11"), self)
        expand_shortcut.activated.connect(self.toggle_expanded_view)
        
        # Ctrl+G 打开手势绑定配置
        gesture_config_shortcut = QShortcut(QKeySequence("Ctrl+G"), self)
        gesture_config_shortcut.activated.connect(self.open_gesture_binding_config)
        
        # Ctrl+R 重置手势绑定
        reset_bindings_shortcut = QShortcut(QKeySequence("Ctrl+R"), self)
        reset_bindings_shortcut.activated.connect(self.reset_gesture_bindings)
    
    def init_ui_state(self):
        """初始化UI状态"""
        # 初始状态：停止状态
        self.is_detecting = False
        
        # 合并为单个切换按钮
        self.startBtn.setText("启动服务器")
        self.startBtn.setToolTip("启动Socket/Bluetooth服务器，等待手势检测客户端连接")
        
        # 设置按钮初始样式 - 启动状态（蓝色）
        self.startBtn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2563eb, stop:1 #1d4ed8);
                border: none;
                color: white;
                font-size: 14px;
                font-weight: 600;
                padding: 8px 16px;
                border-radius: 6px;
                min-height: 18px;
                max-height: 35px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3b82f6, stop:1 #2563eb);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1d4ed8, stop:1 #1e40af);
            }
        """)
        
        # 设置状态标签
        self.statusLabel.setText("状态: 未启动")
        self.gestureLabel.setText("最近手势: 无")
        
        # 设置调试模式按钮
        self.debugModeBtn.setText("开发者模式")
        
        # 设置展开视图按钮
        self.actionToggleExpandedView.setText("展开视图")
        
        # 读取当前通信配置
        self.current_connection_type = self.read_connection_type()
        
        # 设置窗口属性和按钮文本
        self.setWindowTitle("手势检测控制中心")
        self.setMinimumSize(620, 600)  # 增加最小宽度以确保手势历史组件不会溢出
        
        # 强制初始状态：紧凑模式，但给予更合理的初始尺寸
        self.expanded_view = False
        self.contentPanel.setVisible(False)
        self.resize(630, 700)  # 增加初始宽度以容纳手势历史组件
        
        # 更新菜单项状态
        self.actionToggleExpandedView.setChecked(False)
        
        # 默认启用自动布局管理
        self.auto_layout = True
        
        # 更新手势帮助显示
        self.update_gesture_help_display()
    
    def toggle_detection(self):
        """切换检测状态（启动/停止）"""
        if self.is_detecting:
            self.stop_detection()
        else:
            self.start_detection()
    
    def start_detection(self):
        """开始检测"""
        if self.detection_thread and not self.detection_thread.isRunning():
            self.detection_thread.start()
            
            self.is_detecting = True
            self.startBtn.setText("停止服务器")
            self.startBtn.setToolTip("停止Socket/Bluetooth服务器，断开客户端连接")
            self.statusLabel.setText("状态: 服务器运行中")
            self.log_message("服务器已启动，等待客户端连接...")
            
            # 更新按钮样式 - 停止状态（红色）
            self.startBtn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #dc2626, stop:1 #b91c1c);
                    border: none;
                    color: white;
                    font-size: 14px;
                    font-weight: 600;
                    padding: 8px 16px;
                    border-radius: 6px;
                    min-height: 18px;
                    max-height: 35px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #ef4444, stop:1 #dc2626);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #b91c1c, stop:1 #991b1b);
                }
            """)
            
            # 更新状态样式
            self.statusLabel.setStyleSheet(self.statusLabel.styleSheet() + 
                "color: #047857; background: #d1fae5; border: 1px solid #a7f3d0;")
    
    def stop_detection(self):
        """停止检测"""
        if self.detection_thread and self.detection_thread.isRunning():
            self.detection_thread.stop()
            
            self.is_detecting = False
            self.startBtn.setText("启动服务器")
            self.startBtn.setToolTip("启动Socket/Bluetooth服务器，等待手势检测客户端连接")
            
            # 更新按钮样式 - 启动状态（蓝色）
            self.startBtn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #2563eb, stop:1 #1d4ed8);
                    border: none;
                    color: white;
                    font-size: 14px;
                    font-weight: 600;
                    padding: 8px 16px;
                    border-radius: 6px;
                    min-height: 18px;
                    max-height: 35px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #3b82f6, stop:1 #2563eb);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #1d4ed8, stop:1 #1e40af);
                }
            """)
            
            # 显示统计信息
            history_count = self.gesture_history_widget.get_history_count()
            self.statusLabel.setText(f"状态: 已停止 (共识别 {history_count} 个手势)")
            self.gestureLabel.setText("最近手势: 无")
            self.log_message(f"手势检测服务器已停止，本次会话共识别 {history_count} 个手势")
            
            # 恢复状态样式
            self.statusLabel.setStyleSheet(self.statusLabel.styleSheet().replace(
                "color: #047857; background: #d1fae5; border: 1px solid #a7f3d0;", ""))
            self.gestureLabel.setStyleSheet(self.gestureLabel.styleSheet().replace(
                "color: #047857; background: #d1fae5; border: 1px solid #a7f3d0;", ""))
    
    def on_gesture_detected(self, gesture_name: str, hand_type: str, confidence: float):
        """手势检测回调"""
        # 更新手势显示 - 添加更多信息
        hand_icon = "右" if hand_type.lower() == "right" else "左" if hand_type.lower() == "left" else "未知"
        confidence_icon = "高" if confidence >= 80 else "中" if confidence >= 60 else "低"
        
        gesture_text = f"{gesture_name} | {hand_type.title()} | {confidence:.0f}%"
        self.gestureLabel.setText(gesture_text)
        
        # 高亮显示手势标签
        self.gestureLabel.setStyleSheet(self.gestureLabel.styleSheet() + 
            "color: #047857; background: #d1fae5; border: 1px solid #a7f3d0;")
        
        # 记录日志
        self.log_message(f"检测到手势: {hand_type}手 - {gesture_name} ({confidence:.0f}%)")
        
        # 执行对应的动作
        binding = self.gesture_bindings.get_binding(gesture_name)
        if binding and binding.get("enabled", True):
            result = self.action_executor.execute_action(gesture_name, binding)
            if result is True:
                action_desc = binding.get('description', binding.get('action', ''))
                self.log_message(f"执行动作: {action_desc}")
            elif result is False:
                self.log_message(f"执行动作失败: {binding.get('action', '')}")
    
    def on_error_occurred(self, error_message: str):
        """错误处理回调"""
        self.log_message(f"错误: {error_message}")
        self.statusLabel.setText(f"状态: 错误 - {error_message}")
        
        # 如果是连接错误，自动停止检测
        if "连接" in error_message or "网络" in error_message:
            self.stop_detection()
    
    def on_status_updated(self, status: str):
        """状态更新回调"""
        self.statusLabel.setText(f"状态: {status}")
        if self.debug_mode:
            self.log_message(f"{status}")
    
    def toggle_debug_mode(self, checked):
        """切换调试模式"""
        self.debug_mode = checked
        
        # 更新按钮文本
        if checked:
            self.debugModeBtn.setText("退出开发者模式")
            self.log_message("开发者调试模式已启用 - 详细日志将显示在控制台")
            
            # 如果当前是紧凑视图，自动展开以显示手势历史
            if not self.expanded_view:
                self.log_message("开发者模式已启用，展开手势历史查看详细信息")
                self.toggle_expanded_view(True)
                self.auto_layout = False
                self.log_message("已禁用自动布局模式")
            
        else:
            self.debugModeBtn.setText("开发者模式")
            self.log_message("开发者调试模式已关闭")
        
        # 保存设置
        self.settings.setValue('debug_mode', checked)
    
    def toggle_expanded_view(self, checked=None):
        """切换展开/紧凑视图"""
        if checked is None:
            checked = not self.expanded_view
            
        self.expanded_view = checked
        self.auto_layout = False  # 手动切换时禁用自动布局
        
        if checked:
            # 展开视图：显示内容面板和手势历史边栏
            self.contentPanel.setVisible(True)
            if hasattr(self, 'rightSidebar'):
                self.rightSidebar.setVisible(True)
            self.resize(1300, 700)  # 宽度：控制面板630px + 手势历史630px + 边距
            self.log_message("已切换到展开视图模式（显示手势历史）")
        else:
            # 紧凑视图：隐藏内容面板
            self.contentPanel.setVisible(False)
            self.resize(650, 700)  # 仅显示控制面板的宽度
            self.log_message("已切换到紧凑视图模式，仅显示控制面板")
        
        # 更新菜单项状态
        self.actionToggleExpandedView.setChecked(checked)
        
        # 保存设置
        self.settings.setValue('expanded_view', checked)
        self.settings.setValue('auto_layout', self.auto_layout)
    
    def update_responsive_layout(self):
        """更新响应式布局 - 重构为水平宽度优先的管理"""
        if not self.auto_layout:
            return
            
        current_width = self.width()
        current_height = self.height()
        
        # 计算控制面板占用的宽度（包括边距）
        control_panel_width = self.controlPanel.width() + 20  # 考虑边距
        # 计算右边栏宽度（手势历史）
        sidebar_width = 630 + 20 if hasattr(self, 'rightSidebar') else 0
        
        # 基于水平空间决定是否展开手势历史边栏
        min_required_width = control_panel_width + sidebar_width
        should_expand = current_width >= min_required_width
        
        if should_expand != self.expanded_view:
            if should_expand:
                self.log_message(f"水平空间足够 ({current_width}px)，自动展开手势历史边栏")
            else:
                self.log_message(f"水平空间不足 ({current_width}px)，切换到紧凑视图")
            
            self.expanded_view = should_expand
            # 控制内容面板和右边栏的显示
            self.contentPanel.setVisible(should_expand)
            if hasattr(self, 'rightSidebar'):
                self.rightSidebar.setVisible(should_expand)
            self.actionToggleExpandedView.setChecked(should_expand)
        
        # 确保窗口有足够的高度来显示内容（移除水平滚动的需要）
        min_required_height = 500  # 基础最小高度
        if current_height < min_required_height:
            self.resize(current_width, min_required_height)
    
    def restore_settings(self):
        """恢复设置"""
        # 恢复调试模式
        saved_debug_mode = self.settings.value('debug_mode', False, type=bool)
        self.debugModeBtn.setChecked(saved_debug_mode)
        self.actionToggleDebugMode.setChecked(saved_debug_mode)
        
        # 恢复展开视图设置
        saved_expanded_view = self.settings.value('expanded_view', False, type=bool)
        saved_auto_layout = self.settings.value('auto_layout', True, type=bool)
        
        # 恢复自动布局状态
        self.auto_layout = saved_auto_layout
        
        # 强制初始为紧凑模式，不管之前的设置
        # 这确保程序启动时总是显示紧凑视图
        self.expanded_view = False
        # 初始状态下隐藏内容面板（包含手势历史）
        self.contentPanel.setVisible(False)
        self.actionToggleExpandedView.setChecked(False)
        
        # 只在程序真正需要时才调整窗口大小
        # 确保窗口有足够的宽度来容纳内容而不溢出
        min_required_width = 620  # 最小宽度以确保手势历史组件不会水平溢出
        if self.width() < min_required_width:
            self.resize(min_required_width, max(700, self.height()))
        
        # 提示用户如何使用
        if not saved_auto_layout and saved_expanded_view:
            self.log_message("之前使用的是展开视图，可按F11切换回展开模式")
        
        if self.auto_layout:
            self.log_message("自动布局已启用，拖拽窗口边缘可自动调整布局")
            
        # 如果启用了自动布局，立即检查当前窗口大小并更新布局
        # 延迟执行，确保所有初始化完成
        if self.auto_layout:
            QTimer.singleShot(100, self.update_responsive_layout)
    
    def log_message(self, message: str):
        """记录日志消息"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        
        # 安全检查：只有在logTextEdit存在时才记录日志
        if hasattr(self, 'logTextEdit') and self.logTextEdit is not None:
            self.logTextEdit.append(log_entry)
            
            # 自动滚动到底部
            scrollbar = self.logTextEdit.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
            
            # 限制日志条数，避免占用过多内存
            if self.logTextEdit.document().blockCount() > 300:
                cursor = self.logTextEdit.textCursor()
                cursor.movePosition(cursor.MoveOperation.Start)
                cursor.movePosition(cursor.MoveOperation.Down, cursor.MoveMode.KeepAnchor, 50)
                cursor.removeSelectedText()
        else:
            # 如果logTextEdit不可用，可以将日志输出到控制台
            print(log_entry)
    
    def keyPressEvent(self, event):
        """键盘事件处理"""
        # Ctrl+S 快捷键切换检测状态
        if event.key() == Qt.Key.Key_S and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.toggle_detection()
        # F12快捷键切换调试模式
        elif event.key() == Qt.Key.Key_F12:
            self.debugModeBtn.toggle()
        # F11快捷键切换展开视图
        elif event.key() == Qt.Key.Key_F11:
            self.toggle_expanded_view()
        else:
            super().keyPressEvent(event)
    
    def resizeEvent(self, event):
        """窗口大小改变事件"""
        super().resizeEvent(event)
        
        # 延迟更新响应式布局，避免频繁触发
        self.layout_timer.start(100)
    
    def open_gesture_binding_config(self):
        """打开手势绑定配置界面"""
        try:
            from .widgets.binding_config import GestureBindingDialog
            dialog = GestureBindingDialog(self)
            dialog.gesture_bindings_updated.connect(self.on_gesture_bindings_updated)
            
            # 设置对话框位置
            dialog.setGeometry(
                self.x() + 50,
                self.y() + 50,
                500,
                600
            )
            
            # 显示对话框
            if dialog.exec() == dialog.DialogCode.Accepted:
                self.log_message("手势绑定配置已保存")
            else:
                self.log_message("手势绑定配置已取消")
                
        except ImportError:
            self.log_message("手势绑定配置界面模块未找到")
        except Exception as e:
            self.log_message(f"打开手势绑定配置界面失败: {e}")
    
    def reset_gesture_bindings(self):
        """重置手势绑定"""
        try:
            from PyQt6.QtWidgets import QMessageBox
            
            # 显示确认对话框
            reply = QMessageBox.question(
                self,
                "重置手势绑定",
                "确定要将所有手势绑定重置为默认设置吗？\n\n这将删除所有自定义配置！",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # 重置绑定
                self.gesture_bindings.reset_to_defaults()
                self.log_message("手势绑定已重置为默认设置")
                
                # 更新手势绑定标签页的显示
                self.update_gesture_help_display()
                
            else:
                self.log_message("重置手势绑定已取消")
                
        except Exception as e:
            self.log_message(f"重置手势绑定失败: {e}")
    
    def on_gesture_bindings_updated(self, bindings):
        """手势绑定更新回调"""
        try:
            # 更新手势绑定对象
            self.gesture_bindings.update_bindings(bindings)
            
            # 更新显示
            self.update_gesture_help_display()
            
            self.log_message("手势绑定已更新")
            
        except Exception as e:
            self.log_message(f"更新手势绑定失败: {e}")
    
    def update_gesture_help_display(self):
        """更新手势帮助显示"""
        try:
            # 获取当前绑定
            bindings = self.gesture_bindings.get_all_bindings()
            
            # 构建显示文本
            help_text = "当前手势绑定：\n\n"
            
            static_gestures = []
            dynamic_gestures = []
            
            for gesture, config in bindings.items():
                if config.get('enabled', True):
                    description = config.get('description', config.get('action', ''))
                    
                    if gesture in ['swipe_left', 'swipe_right', 'swipe_up', 'swipe_down']:
                        dynamic_gestures.append(f"• {gesture} - {description}")
                    else:
                        static_gestures.append(f"• {gesture} - {description}")
            
            # 添加静态手势
            if static_gestures:
                help_text += "静态手势：\n"
                for gesture in static_gestures:
                    help_text += f"  {gesture}\n"
                help_text += "\n"
            
            # 添加动态手势
            if dynamic_gestures:
                help_text += "动态手势：\n"
                for gesture in dynamic_gestures:
                    help_text += f"  {gesture}\n"
                help_text += "\n"
            
            # 添加使用说明
            help_text += """使用技巧：
• 确保手势在摄像头范围内
• 保持手势1-2秒以确保识别
• 良好的光线条件有助于识别
• 避免快速移动以免误识别

调试模式：
• 启用后可查看实时摄像头画面
• 查看手势识别的详细信息
• 调整手势动作以获得最佳效果

注意事项：
• 首次使用请允许摄像头权限
• 建议在稳定的环境中使用
• 如遇识别问题可重启检测

启动检测后即可使用所有手势功能"""
            
            # 更新标签文本
            self.gestureHelpLabel.setText(help_text)
            
        except Exception as e:
            self.log_message(f"更新手势帮助显示失败: {e}")
    
    def closeEvent(self, event):
        """关闭事件"""
        if self.detection_thread and self.detection_thread.isRunning():
            self.log_message("正在停止服务器线程...")
            self.detection_thread.stop()
            # 等待线程完全停止
            self.detection_thread.wait(3000)  # 等待最多3秒
        
        # 保存当前设置
        try:
            self.settings.setValue('debug_mode', self.debug_mode)
            self.settings.setValue('expanded_view', self.expanded_view)
            self.settings.setValue('auto_layout', self.auto_layout)
        except:
            pass  # 忽略设置保存错误
        
        # 在关闭前记录，但如果失败就忽略
        try:
            self.log_message("感谢使用手势检测控制中心！")
        except:
            print("感谢使用手势检测控制中心！")  # 备用输出
            
        event.accept()
    
    def on_gesture_detail_detected(self, gesture_data: dict):
        """处理详细的手势数据"""
        try:
            gesture_name = gesture_data.get('gesture', 'unknown')
            hand_type = gesture_data.get('hand_type', 'unknown')
            confidence = gesture_data.get('confidence', 0.0)
            gesture_type = gesture_data.get('gesture_type', 'static')
            details = gesture_data.get('details', {})
            timestamp = gesture_data.get('timestamp', 0)
            
            # 更新拖拽状态
            self._update_drag_state(gesture_name, hand_type)
            
            # 添加到手势历史记录
            self.gesture_history_widget.add_gesture(gesture_data)
            
            # 记录详细的手势信息到日志
            if self.debug_mode:
                log_msg = f"详细手势数据 - 类型: {gesture_type}, 手势: {gesture_name}, 手部: {hand_type}, 置信度: {confidence:.1f}%"
                
                if gesture_type == 'static':
                    tag = details.get('tag', '')
                    if tag:
                        log_msg += f", 标签: {tag}"
                        
                elif gesture_type == 'dynamic':
                    if 'tag' in details:
                        tag = details.get('tag', '')
                        dx = details.get('dx', 0)
                        dy = details.get('dy', 0)
                        log_msg += f", 标签: {tag}, 位移: dx={dx}, dy={dy}"
                    else:
                        log_msg += ", 无轨迹追踪"
                
                self.log_message(log_msg)
            
            # 将详细的手势数据传递给动作执行器
            if gesture_type == 'static' and details.get('tag') == 'start':
                # 静态手势开始时执行动作
                self._execute_gesture_action(gesture_name, hand_type, confidence)
            elif gesture_type == 'dynamic':
                if 'tag' not in details or details.get('tag') == 'end':
                    # 动态手势完成时执行动作
                    self._execute_gesture_action(gesture_name, hand_type, confidence)
                    
        except Exception as e:
            self.log_message(f"处理详细手势数据失败: {e}")
    
    def _execute_gesture_action(self, gesture_name: str, hand_type: str, confidence: float):
        """执行手势对应的动作（内部方法）"""
        binding = self.gesture_bindings.get_binding(gesture_name)
        if binding and binding.get("enabled", True):
            result = self.action_executor.execute_action(gesture_name, binding)
            if result is True:
                action_desc = binding.get('description', binding.get('action', ''))
                self.log_message(f"执行动作: {action_desc}")
            elif result is False:
                self.log_message(f"执行动作失败: {binding.get('action', '')}")
            # result为None时表示在冷却期内，不记录日志
    
    def on_trail_change_detected(self, trail_data: dict):
        """处理轨迹变化数据"""
        try:
            # 获取轨迹变化信息
            details = trail_data.get('details', {})
            dx = details.get('dx', 0)
            dy = details.get('dy', 0)
            hand_type = trail_data.get('hand_type', 'unknown')
            
            if self.debug_mode:
                distance = details.get('distance', 0)
                drag_status = "拖拽中" if self.is_dragging else "非拖拽"
                self.log_message(f"轨迹变化: {hand_type}手 移动({dx:+d},{dy:+d}) 距离={distance:.1f} [{drag_status}]")
            
            # 只有在拖拽模式下才执行窗口拖拽
            if self.is_dragging:
                success = self.action_executor.execute_window_drag_with_trail(dx, dy)
                if self.debug_mode:
                    self.log_message(f"窗口拖拽执行: {'成功' if success else '失败'}")
            else:
                if self.debug_mode:
                    self.log_message("忽略轨迹变化（未处于拖拽模式）")
                    
        except Exception as e:
            self.log_message(f"处理轨迹变化失败: {e}")
    
    def _update_drag_state(self, gesture_name: str, hand_type: str):
        """更新拖拽状态"""
        import time
        
        current_time = time.time()
        self.last_gesture = gesture_name
        self.last_gesture_time = current_time
        
        # 如果检测到HandClose手势，激活拖拽模式
        if gesture_name == "HandClose":
            if not self.is_dragging:
                self.is_dragging = True
                self.log_message(f"激活拖拽模式: {hand_type}手")
        
        # 如果检测到HandOpen手势，取消拖拽模式
        elif gesture_name == "HandOpen":
            if self.is_dragging:
                self.is_dragging = False
                self.log_message(f"✋ 取消拖拽模式: {hand_type}手")
        
        # 设置定时器，在一定时间后自动取消拖拽模式
        if self.is_dragging:
            QTimer.singleShot(int(self.drag_gesture_timeout * 1000), self._check_drag_timeout)
    
    def _check_drag_timeout(self):
        """检查拖拽超时"""
        import time
        
        current_time = time.time()
        if self.is_dragging and (current_time - self.last_gesture_time) >= self.drag_gesture_timeout:
            self.is_dragging = False
            self.log_message("拖拽模式超时自动取消")

    def read_connection_type(self) -> str:
        """读取当前通信配置类型"""
        try:
            # 读取project/config.py文件
            config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.py")
            
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 查找CONNECTION_TYPE配置行
            for line in content.split('\n'):
                if line.strip().startswith('CONNECTION_TYPE') and '=' in line:
                    # 提取配置值
                    value = line.split('=')[1].strip().strip("'\"")
                    return value
                    
            return 'socket'  # 默认值
            
        except Exception as e:
            print(f"读取通信配置失败: {e}")
            return 'socket'  # 默认值
    
    def write_connection_type(self, connection_type: str) -> bool:
        """写入通信配置类型"""
        try:
            # 读取project/config.py文件
            config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.py")
            
            with open(config_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 修改CONNECTION_TYPE配置行
            for i, line in enumerate(lines):
                if line.strip().startswith('CONNECTION_TYPE') and '=' in line:
                    # 保持原有的注释
                    if '#' in line:
                        comment = line.split('#', 1)[1]
                        lines[i] = f"CONNECTION_TYPE = '{connection_type}'  #{comment}"
                    else:
                        lines[i] = f"CONNECTION_TYPE = '{connection_type}'  # 通信模式：'socket' 或 'serial' (蓝牙)\n"
                    break
            
            # 写入文件
            with open(config_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
                
            return True
            
        except Exception as e:
            print(f"写入通信配置失败: {e}")
            return False
    
    def toggle_connection_type(self):
        """切换通信方式"""
        try:
            from PyQt6.QtWidgets import QMessageBox
            
            # 确定新的通信类型
            new_type = 'serial' if self.current_connection_type == 'socket' else 'socket'
            
            # 获取用户友好的显示名称
            current_display = 'Socket' if self.current_connection_type == 'socket' else 'Bluetooth'
            new_display = 'Bluetooth' if new_type == 'serial' else 'Socket'
            
            # 提示用户
            reply = QMessageBox.question(
                self, 
                '切换通信方式', 
                f'确定要将通信方式从 {current_display} 切换到 {new_display} 吗？\n\n'
                f'说明：\n'
                f'• Socket: 使用TCP/IP网络通信\n'
                f'• Bluetooth: 使用蓝牙RFCOMM协议通信\n\n'
                f'这将修改当前应用的配置文件。',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # 如果当前服务器正在运行，先停止
                was_running = self.is_detecting
                if was_running:
                    self.stop_detection()
                
                # 写入新配置
                if self.write_connection_type(new_type):
                    # 更新当前状态
                    self.current_connection_type = new_type
                    
                    # 重新创建通信线程以使用新配置
                    if hasattr(self, 'detection_thread') and self.detection_thread:
                        self.detection_thread.stop()
                        self.detection_thread.wait()
                    
                    # 创建新的通信线程（会重新读取配置文件）
                    from ui.threads.socket_gesture_receiver import SocketGestureReceiverThread
                    self.detection_thread = SocketGestureReceiverThread()
                    self.detection_thread.gesture_detected.connect(self.on_gesture_detected)
                    self.detection_thread.gesture_detail_detected.connect(self.on_gesture_detail_detected)
                    self.detection_thread.trail_change_detected.connect(self.on_trail_change_detected)
                    self.detection_thread.status_updated.connect(self.on_status_updated)
                    self.detection_thread.error_occurred.connect(self.on_error_occurred)
                    
                    # 验证线程是否正确读取了新配置
                    thread_connection_type = self.detection_thread.connection_type
                    self.log_message(f"线程配置验证: 期望 {new_type}，实际 {thread_connection_type}")
                    
                    if thread_connection_type != new_type:
                        self.log_message(f"警告：线程配置不匹配，强制重新初始化")
                        # 强制重新初始化线程
                        self.detection_thread.stop()
                        self.detection_thread.wait()
                        self.detection_thread = SocketGestureReceiverThread()
                        self.detection_thread.gesture_detected.connect(self.on_gesture_detected)
                        self.detection_thread.gesture_detail_detected.connect(self.on_gesture_detail_detected)
                        self.detection_thread.trail_change_detected.connect(self.on_trail_change_detected)
                        self.detection_thread.status_updated.connect(self.on_status_updated)
                        self.detection_thread.error_occurred.connect(self.on_error_occurred)
                        
                        # 再次验证
                        final_connection_type = self.detection_thread.connection_type
                        self.log_message(f"重新初始化后配置: {final_connection_type}")
                    else:
                        self.log_message(f"线程配置验证通过")
                    
                    self.log_message(f"通信方式已切换到: {new_display}")
                    
                    # 如果切换到蓝牙模式，立即获取并打印MAC地址
                    if new_type == 'serial':
                        self._print_bluetooth_mac_address()
                    
                    # 显示成功消息
                    QMessageBox.information(
                        self, 
                        '切换成功', 
                        f'通信方式已成功切换到 {new_display}！\n\n'
                        f'新配置已保存，可以立即使用。'
                    )
                    
                    # 如果之前在运行，询问是否重启
                    if was_running:
                        restart_reply = QMessageBox.question(
                            self,
                            '重启检测',
                            '是否重新启动手势检测？',
                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                            QMessageBox.StandardButton.Yes
                        )
                        if restart_reply == QMessageBox.StandardButton.Yes:
                            self.start_detection()
                    
                else:
                    QMessageBox.critical(
                        self,
                        '切换失败',
                        '无法写入配置文件，请检查文件权限。'
                    )
                    
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(
                self,
                '切换失败',
                f'切换通信方式时发生错误：\n{str(e)}'
            )
    
    def show_connection_status(self):
        """显示通信状态"""
        try:
            from PyQt6.QtWidgets import QMessageBox
            
            # 刷新当前配置
            current_type = self.read_connection_type()
            self.current_connection_type = current_type
            
            # 获取用户友好的显示名称
            display_name = 'Socket' if current_type == 'socket' else 'Bluetooth'
            
            # 获取详细的服务器状态信息
            server_info = {}
            if hasattr(self, 'detection_thread') and self.detection_thread:
                server_info = self.detection_thread.get_server_info()
            
            # 获取状态信息
            if current_type == 'socket':
                status_text = f"当前通信方式: Socket (TCP/IP)\n"
                status_text += f"检测状态: {'运行中' if self.is_detecting else '已停止'}\n"
                
                if server_info.get('running', False):
                    status_text += f"Socket地址: {server_info.get('host', '127.0.0.1')}:{server_info.get('port', 65432)}\n"
                    status_text += f"活动连接数: {server_info.get('active_threads', 0)}\n"
                else:
                    status_text += f"Socket地址: 127.0.0.1:65432 (未启动)\n"
                    
                status_text += f"协议: TCP/IP网络通信"
                
            elif current_type == 'serial':
                status_text = f"当前通信方式: Bluetooth (RFCOMM)\n"
                status_text += f"检测状态: {'运行中' if self.is_detecting else '已停止'}\n"
                
                if server_info.get('running', False):
                    status_text += f"蓝牙端口: RFCOMM端口{server_info.get('port', 4)}\n"
                    status_text += f"活动连接数: {server_info.get('active_threads', 0)}\n"
                    
                    # 显示本机MAC地址
                    local_mac = server_info.get('local_mac_address')
                    if local_mac:
                        status_text += f"本机MAC地址: {local_mac}\n"
                        status_text += f"当前配置:\n"
                        status_text += f"  BLUETOOTH_MAC = '{local_mac}'\n"
                        status_text += f"  CONNECTION_TYPE = 'serial'\n"
                    else:
                        status_text += "本机MAC地址: 无法获取\n"
                    
                    # 显示蓝牙支持状态
                    if server_info.get('bluetooth_available', False):
                        status_text += "蓝牙支持: 已启用\n"
                    else:
                        status_text += "蓝牙支持: 未安装 (需要: pip install pybluez)\n"
                else:
                    status_text += "蓝牙端口: RFCOMM端口4 (未启动)\n"
                    
                status_text += "协议: 蓝牙RFCOMM通信"
            else:
                status_text = f"当前通信方式: {current_type}\n"
                status_text += "状态: 未知配置"
            
            QMessageBox.information(
                self,
                '通信状态',
                status_text
            )
            
            self.log_message(f"通信状态: {display_name}")
            
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(
                self,
                '状态查询失败',
                f'查询通信状态时发生错误：\n{str(e)}'
            )
    
    def _print_bluetooth_mac_address(self):
        """切换到蓝牙模式时立即获取并打印MAC地址"""
        try:
            from core.socket_server import BluetoothServer
            
            # 创建临时的蓝牙服务器实例来获取MAC地址
            temp_bluetooth = BluetoothServer(host="", port=4)
            
            # 获取本机蓝牙MAC地址
            mac_address = temp_bluetooth._get_local_bluetooth_mac()
            
            if mac_address:
                print(f"\n蓝牙通信模式已启用")
                print(f"   本机蓝牙MAC地址: {mac_address}")
                print(f"   RFCOMM端口: 4")
                print(f"   蓝牙配置已自动更新:")
                print(f"      BLUETOOTH_MAC = '{mac_address}'")
                print(f"      BLUETOOTH_PORT = 4")
                print(f"      CONNECTION_TYPE = 'serial'\n")
                
                # 同时记录到UI日志
                self.log_message(f"本机蓝牙MAC地址: {mac_address}")
                self.log_message(f"RFCOMM端口: 4")
                self.log_message(f"蓝牙配置已自动更新")
                
            else:
                print(f"\n蓝牙通信模式已启用")
                print(f"   无法获取本机蓝牙MAC地址")
                print(f"   RFCOMM端口: 4")
                print(f"   手动获取Windows蓝牙MAC地址:")
                print(f"      1. 打开 设置 -> 蓝牙和设备")
                print(f"      2. 点击 更多蓝牙设置")
                print(f"      3. 在硬件选项卡中查看蓝牙适配器属性")
                print(f"      4. 或者在设备管理器中查看蓝牙适配器详情")
                print(f"   或者尝试安装依赖: pip install psutil wmi")
                print(f"   请手动配置蓝牙MAC地址\n")
                
                # 记录到UI日志  
                self.log_message("无法自动获取蓝牙MAC地址")
                self.log_message("请手动查看Windows蓝牙设置获取MAC地址")
                self.log_message("参考: 设置->蓝牙和设备->更多蓝牙设置")
                
        except Exception as e:
            print(f"\n蓝牙通信模式已启用")
            print(f"   获取蓝牙MAC地址时出错: {e}")
            print(f"   请手动配置蓝牙MAC地址")
            print(f"   或安装所需依赖: pip install pybluez psutil\n")
            
            # 记录到UI日志
            self.log_message(f"获取蓝牙MAC地址失败: {e}")
            self.log_message("请检查蓝牙依赖库安装情况")