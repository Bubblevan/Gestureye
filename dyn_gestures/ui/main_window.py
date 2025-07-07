"""
主窗口 - 现代化的手势检测控制中心
"""

import sys
import cv2
import numpy as np
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QTextEdit, QTabWidget, 
                             QGroupBox, QSplitter, QFrame, QScrollArea,
                             QGridLayout, QSpacerItem, QSizePolicy, QMessageBox)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QPixmap, QImage, QFont, QPalette, QColor, QLinearGradient, QPainter

from .widgets.binding_config import GestureBindingDialog
from .threads.gesture_detection import GestureDetectionThread
from core.gesture_bindings import GestureBindings
from core.action_executor import ActionExecutor
from bluetooth.manager import BluetoothManager
import config


class ModernCard(QFrame):
    """现代化卡片组件"""
    
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.title = title
        self.setObjectName("modernCard")
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setLineWidth(0)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 创建渐变背景
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(255, 255, 255, 250))
        gradient.setColorAt(1, QColor(248, 250, 252, 250))
        
        # 绘制圆角矩形
        painter.setBrush(gradient)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), 12, 12)
        
        # 绘制阴影效果
        painter.setBrush(QColor(0, 0, 0, 20))
        painter.drawRoundedRect(self.rect().adjusted(2, 2, 2, 2), 12, 12)


class StatusIndicator(QLabel):
    """状态指示器组件"""
    
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setObjectName("statusIndicator")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumHeight(30)
        self.status = "idle"  # idle, running, error
        
    def set_status(self, status):
        """设置状态"""
        self.status = status
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 根据状态设置颜色
        if self.status == "running":
            color = QColor(34, 197, 94)  # 绿色
            text_color = QColor(255, 255, 255)
        elif self.status == "error":
            color = QColor(239, 68, 68)  # 红色
            text_color = QColor(255, 255, 255)
        else:
            color = QColor(156, 163, 175)  # 灰色
            text_color = QColor(75, 85, 99)
        
        # 绘制背景
        painter.setBrush(color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), 15, 15)
        
        # 绘制文本
        painter.setPen(text_color)
        font = QFont("Segoe UI", 10, QFont.Weight.Medium)
        painter.setFont(font)
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.text())


class ModernButton(QPushButton):
    """现代化按钮组件"""
    
    def __init__(self, text="", primary=False, parent=None):
        super().__init__(text, parent)
        self.primary = primary
        self.setObjectName("modernButton")
        self.setMinimumHeight(40)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 根据状态和类型设置颜色
        if self.primary:
            if self.isDown():
                color = QColor(30, 64, 175)  # 深蓝色
            elif self.underMouse():
                color = QColor(59, 130, 246)  # 蓝色
            else:
                color = QColor(37, 99, 235)  # 主蓝色
        else:
            if self.isDown():
                color = QColor(107, 114, 128)  # 深灰色
            elif self.underMouse():
                color = QColor(156, 163, 175)  # 灰色
            else:
                color = QColor(209, 213, 219)  # 浅灰色
        
        # 绘制背景
        painter.setBrush(color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), 8, 8)
        
        # 绘制文本
        if self.primary:
            text_color = QColor(255, 255, 255)
        else:
            text_color = QColor(55, 65, 81)
        
        painter.setPen(text_color)
        font = QFont("Segoe UI", 10, QFont.Weight.Medium)
        painter.setFont(font)
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.text())


class MainWindow(QMainWindow):
    """现代化手势检测控制中心"""
    
    def __init__(self):
        super().__init__()
        self.gesture_bindings = GestureBindings()
        self.action_executor = ActionExecutor()
        self.detection_thread = None
        self.bluetooth_manager = None
        
        self.init_ui()
        self.setup_detection()
        self.setup_bluetooth()
        self.apply_modern_style()
        
        # 设置定时器用于界面更新
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_interface)
        self.update_timer.start(100)  # 100ms更新一次
        
    def init_ui(self):
        """初始化现代化界面"""
        self.setWindowTitle("Gestureye - 智能手势检测控制中心")
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(1200, 800)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # 左侧：摄像头显示和控制面板
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel, 2)
        
        # 右侧：配置和监控面板
        right_panel = self.create_right_panel()
        main_layout.addWidget(right_panel, 1)
        
    def create_left_panel(self) -> QWidget:
        """创建左侧面板"""
        card = ModernCard("实时检测")
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # 标题
        title = QLabel("🎥 实时手势检测")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #1f2937; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # 摄像头显示区域
        camera_frame = QFrame()
        camera_frame.setObjectName("cameraFrame")
        camera_frame.setMinimumSize(640, 480)
        camera_frame.setMaximumSize(800, 600)
        camera_frame.setStyleSheet("""
            #cameraFrame {
                border: 3px solid #e5e7eb;
                border-radius: 16px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #f8fafc, stop:1 #e2e8f0);
            }
        """)
        
        camera_layout = QVBoxLayout(camera_frame)
        camera_layout.setContentsMargins(10, 10, 10, 10)
        
        self.camera_label = QLabel("等待启动摄像头...")
        self.camera_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.camera_label.setStyleSheet("""
            QLabel {
                color: #6b7280;
                font-size: 16px;
                font-weight: 500;
                background: transparent;
            }
        """)
        camera_layout.addWidget(self.camera_label)
        
        layout.addWidget(camera_frame, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # 控制按钮区域
        control_card = ModernCard("控制面板")
        control_layout = QVBoxLayout(control_card)
        control_layout.setContentsMargins(20, 20, 20, 20)
        control_layout.setSpacing(15)
        
        # 按钮行
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        self.start_btn = ModernButton("▶ 开始检测", primary=True)
        self.start_btn.clicked.connect(self.start_detection)
        self.start_btn.setMinimumHeight(50)
        
        self.stop_btn = ModernButton("⏹ 停止检测")
        self.stop_btn.clicked.connect(self.stop_detection)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setMinimumHeight(50)
        
        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.stop_btn)
        button_layout.addStretch()
        
        control_layout.addLayout(button_layout)
        
        # 状态指示器
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("系统状态:"))
        
        self.status_indicator = StatusIndicator("未启动")
        self.status_indicator.setMinimumWidth(120)
        status_layout.addWidget(self.status_indicator)
        status_layout.addStretch()
        
        control_layout.addLayout(status_layout)
        
        layout.addWidget(control_card)
        
        return card
    
    def create_right_panel(self) -> QWidget:
        """创建右侧面板"""
        card = ModernCard("配置与监控")
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # 标题
        title = QLabel("⚙️ 系统配置")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #1f2937; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # 创建标签页
        tab_widget = QTabWidget()
        tab_widget.setObjectName("modernTabWidget")
        
        # 绑定配置标签页
        binding_widget = GestureBindingDialog(self)
        tab_widget.addTab(binding_widget, "🎯 手势绑定")
        
        # 监控标签页
        monitor_widget = self.create_monitor_widget()
        tab_widget.addTab(monitor_widget, "📊 实时监控")
        
        layout.addWidget(tab_widget)
        
        return card
    
    def create_monitor_widget(self) -> QWidget:
        """创建监控面板"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        
        # 最近检测的手势卡片
        gesture_card = ModernCard("最近检测")
        gesture_layout = QVBoxLayout(gesture_card)
        gesture_layout.setContentsMargins(20, 20, 20, 20)
        gesture_layout.setSpacing(15)
        
        gesture_title = QLabel("🎯 最新手势")
        gesture_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        gesture_title.setStyleSheet("color: #1f2937;")
        gesture_layout.addWidget(gesture_title)
        
        self.recent_gesture_label = QLabel("等待检测...")
        self.recent_gesture_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: 600;
                color: #059669;
                padding: 15px;
                border: 2px solid #d1fae5;
                border-radius: 12px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #ecfdf5, stop:1 #d1fae5);
            }
        """)
        self.recent_gesture_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.recent_gesture_label.setMinimumHeight(80)
        gesture_layout.addWidget(self.recent_gesture_label)
        
        layout.addWidget(gesture_card)
        
        # 日志显示卡片
        log_card = ModernCard("运行日志")
        log_layout = QVBoxLayout(log_card)
        log_layout.setContentsMargins(20, 20, 20, 20)
        log_layout.setSpacing(15)
        
        log_header = QHBoxLayout()
        log_title = QLabel("📝 系统日志")
        log_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        log_title.setStyleSheet("color: #1f2937;")
        log_header.addWidget(log_title)
        log_header.addStretch()
        
        clear_log_btn = ModernButton("🗑 清空")
        clear_log_btn.clicked.connect(self.clear_log)
        clear_log_btn.setMaximumWidth(80)
        log_header.addWidget(clear_log_btn)
        
        log_layout.addLayout(log_header)
        
        # 日志显示区域
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(300)
        self.log_text.setObjectName("modernLogText")
        log_layout.addWidget(self.log_text)
        
        layout.addWidget(log_card)
        
        return widget
    
    def apply_modern_style(self):
        """应用现代化样式"""
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #f8fafc, stop:1 #e2e8f0);
            }
            
            #modernTabWidget::pane {
                border: none;
                background: transparent;
            }
            
            #modernTabWidget::tab-bar {
                alignment: left;
            }
            
            QTabBar::tab {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f1f5f9, stop:1 #e2e8f0);
                border: 1px solid #cbd5e1;
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                padding: 8px 16px;
                margin-right: 2px;
                font-weight: 500;
                color: #64748b;
            }
            
            QTabBar::tab:selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8fafc);
                color: #1e293b;
                border-bottom: 2px solid #3b82f6;
            }
            
            QTabBar::tab:hover:!selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8fafc, stop:1 #f1f5f9);
                color: #475569;
            }
            
            #modernLogText {
                background: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 10px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
                color: #374151;
            }
            
            QScrollBar:vertical {
                background: #f1f5f9;
                width: 12px;
                border-radius: 6px;
            }
            
            QScrollBar::handle:vertical {
                background: #cbd5e1;
                border-radius: 6px;
                min-height: 20px;
            }
            
            QScrollBar::handle:vertical:hover {
                background: #94a3b8;
            }
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
    
    def setup_detection(self):
        """设置检测线程"""
        self.detection_thread = GestureDetectionThread()
        self.detection_thread.gesture_detected.connect(self.on_gesture_detected)
        self.detection_thread.frame_processed.connect(self.on_frame_processed)
        self.detection_thread.status_updated.connect(self.on_status_updated)
    
    def setup_bluetooth(self):
        """设置蓝牙管理器"""
        if config.BLUETOOTH_CONFIG['enabled']:
            try:
                self.bluetooth_manager = BluetoothManager()
                
                # 连接蓝牙信号
                self.bluetooth_manager.bluetooth_gesture_detected.connect(
                    self.on_bluetooth_gesture_detected
                )
                self.bluetooth_manager.bluetooth_hand_data_received.connect(
                    self.on_bluetooth_hand_data_received
                )
                self.bluetooth_manager.bluetooth_status_changed.connect(
                    self.on_bluetooth_status_changed
                )
                self.bluetooth_manager.log_message.connect(
                    self.on_bluetooth_log_message
                )
                
                # 启动蓝牙服务器
                if self.bluetooth_manager.start_bluetooth_server():
                    self.add_log_message("🔵 蓝牙服务器启动成功")
                else:
                    self.add_log_message("❌ 蓝牙服务器启动失败")
                    
            except Exception as e:
                self.add_log_message(f"❌ 蓝牙初始化失败: {e}")
                self.bluetooth_manager = None
        else:
            self.add_log_message("蓝牙功能已禁用")
    
    def start_detection(self):
        """开始检测"""
        if self.detection_thread and not self.detection_thread.running:
            self.detection_thread.running = True
            self.detection_thread.start()
            
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.status_indicator.set_status("running")
            self.status_indicator.setText("运行中")
            self.add_log_message("🚀 手势检测已启动")
    
    def stop_detection(self):
        """停止检测"""
        if self.detection_thread and self.detection_thread.running:
            self.detection_thread.stop()
            
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.status_indicator.set_status("idle")
            self.status_indicator.setText("已停止")
            self.add_log_message("⏹ 手势检测已停止")
        
        # 也停止蓝牙服务器
        if self.bluetooth_manager:
            self.bluetooth_manager.stop_bluetooth_server()
    
    def on_gesture_detected(self, gesture_name: str, hand_type: str, confidence: float):
        """手势检测回调"""
        # 更新最近检测的手势显示
        gesture_text = f"{hand_type}手: {gesture_name}\n置信度: {confidence:.1f}%"
        self.recent_gesture_label.setText(gesture_text)
        
        # 记录日志
        self.add_log_message(f"🎯 检测到手势: {gesture_text}")
        
        # 执行对应的动作
        binding = self.gesture_bindings.get_binding(gesture_name)
        if binding and binding.get("enabled", True):
            result = self.action_executor.execute_action(gesture_name, binding)
            if result is True:
                self.add_log_message(f"✅ 执行动作: {binding.get('description', binding.get('action', ''))}")
            elif result is False:
                self.add_log_message(f"❌ 执行动作失败: {binding.get('action', '')}")
            # 如果result是None（冷却时间内），则不打印任何日志
    
    def on_frame_processed(self, frame):
        """帧处理回调"""
        # 将OpenCV图像转换为Qt图像
        height, width, channel = frame.shape
        bytes_per_line = 3 * width
        q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
        q_image = q_image.rgbSwapped()  # BGR to RGB
        
        # 缩放图像以适应显示区域
        pixmap = QPixmap.fromImage(q_image)
        scaled_pixmap = pixmap.scaled(
            self.camera_label.size(), 
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        
        self.camera_label.setPixmap(scaled_pixmap)
    
    def on_status_updated(self, status: str):
        """状态更新回调"""
        self.status_indicator.setText(f"状态: {status}")
        self.add_log_message(f"📊 {status}")
    
    def on_bluetooth_gesture_detected(self, gesture_name: str, hand_type: str, confidence: float):
        """蓝牙手势检测回调"""
        # 更新最近检测的手势显示
        gesture_text = f"{hand_type}手: {gesture_name} (蓝牙)\n置信度: {confidence:.1f}%"
        self.recent_gesture_label.setText(gesture_text)
        
        # 记录日志
        self.add_log_message(f"🔗 蓝牙手势: {gesture_text}")
    
    def on_bluetooth_hand_data_received(self, hand_data):
        """蓝牙手部数据接收回调"""
        # 这里可以添加手部数据的可视化或处理逻辑
        self.add_log_message(f"📥 接收到手部数据: {hand_data.hand_type}手")
    
    def on_bluetooth_status_changed(self, connected: bool):
        """蓝牙连接状态变化回调"""
        status = "蓝牙已连接" if connected else "蓝牙已断开"
        bluetooth_indicator_text = f" | {status}"
        
        # 更新状态指示器
        current_text = self.status_indicator.text()
        if " | 蓝牙" in current_text:
            # 替换现有的蓝牙状态
            current_text = current_text.split(" | 蓝牙")[0]
        
        self.status_indicator.setText(current_text + bluetooth_indicator_text)
    
    def on_bluetooth_log_message(self, message: str):
        """蓝牙日志消息回调"""
        self.add_log_message(message)
    
    def add_log_message(self, message: str):
        """添加日志消息到界面"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        
        self.log_text.append(log_entry)
        
        # 自动滚动到底部
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def clear_log(self):
        """清空日志"""
        self.log_text.clear()
        self.add_log_message("🗑 日志已清空")
    
    def update_interface(self):
        """定期更新界面"""
        # 可以在这里添加周期性的界面更新逻辑
        pass
    
    def closeEvent(self, event):
        """关闭事件"""
        if self.detection_thread and self.detection_thread.running:
            self.detection_thread.stop()
        event.accept()


def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 设置应用程序信息
    app.setApplicationName("手势检测控制中心")
    app.setApplicationVersion("1.0.0")
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    # 运行应用程序
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 