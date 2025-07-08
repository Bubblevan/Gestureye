"""
使用Qt Designer设计的主窗口 - 响应式布局版本
"""

import os
from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow, QApplication
from PyQt6.QtCore import pyqtSignal, QSettings, Qt, QTimer
from PyQt6.QtGui import QKeySequence, QShortcut
from .threads.gesture_detection import GestureDetectionThread
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
            
        # 初始化设置
        self.settings = QSettings('GestureDetection', 'MainWindow')
        self.debug_mode = False
        self.expanded_view = False
        self.is_detecting = False
        
        # 响应式布局设置
        self.compact_width_threshold = 500  # 紧凑模式的宽度阈值
        self.auto_layout = True  # 自动布局管理
        
        # 初始化业务逻辑
        self.gesture_bindings = GestureBindings()
        self.action_executor = ActionExecutor()
        self.detection_thread = None
        
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
        

    
    def setup_connections(self):
        """设置信号和槽连接"""
        # 连接按钮点击事件
        self.startBtn.clicked.connect(self.start_detection)
        self.stopBtn.clicked.connect(self.stop_detection)
        
        # 连接调试模式切换
        self.debugModeBtn.toggled.connect(self.toggle_debug_mode)
        self.actionToggleDebugMode.toggled.connect(self.toggle_debug_mode)
        
        # 连接展开视图切换
        self.actionToggleExpandedView.toggled.connect(self.toggle_expanded_view)
        
        # 连接配置菜单项
        self.actionCustomGestureBindings.triggered.connect(self.open_gesture_binding_config)
        self.actionResetBindings.triggered.connect(self.reset_gesture_bindings)
        
        # 同步按钮和菜单项状态
        self.debugModeBtn.toggled.connect(self.actionToggleDebugMode.setChecked)
        self.actionToggleDebugMode.toggled.connect(self.debugModeBtn.setChecked)
        
        # 设置检测线程
        self.detection_thread = GestureDetectionThread()
        self.detection_thread.gesture_detected.connect(self.on_gesture_detected)
        self.detection_thread.frame_processed.connect(self.on_frame_processed)
        self.detection_thread.status_updated.connect(self.on_status_updated)
    
    def setup_shortcuts(self):
        """设置快捷键"""
        # Ctrl+S 开始检测
        start_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        start_shortcut.activated.connect(self.start_detection)
        
        # Ctrl+T 停止检测
        stop_shortcut = QShortcut(QKeySequence("Ctrl+T"), self)
        stop_shortcut.activated.connect(self.stop_detection)
        
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
        self.stopBtn.setEnabled(False)
        self.statusLabel.setText("状态: 未启动")
        self.gestureLabel.setText("最近手势: 无")
        
        # 设置窗口属性
        self.setWindowTitle("Gestureyes")
        self.setMinimumSize(400, 600)
        
        # 强制初始状态：紧凑模式
        self.expanded_view = False
        self.contentPanel.setVisible(False)
        self.resize(450, 700)
        
        # 更新菜单项状态
        self.actionToggleExpandedView.setChecked(False)
        
        # 默认启用自动布局管理
        self.auto_layout = True
        
        # 更新手势帮助显示
        self.update_gesture_help_display()
    
    def toggle_debug_mode(self, checked):
        """切换调试模式"""
        self.debug_mode = checked
        
        # 更新按钮文本
        if checked:
            self.debugModeBtn.setText("退出开发者模式")
            self.log_message("开发者调试模式已启用")
            
            # 强制展开右边栏来显示摄像头预览
            if not self.expanded_view:
                self.log_message("开发者模式需要摄像头预览，自动展开右边栏")
                self.expanded_view = True
                self.contentPanel.setVisible(True)
                self.actionToggleExpandedView.setChecked(True)
                # 禁用自动布局，因为这是手动触发的
                self.auto_layout = False
                self.log_message("已禁用自动布局模式")
                # 调整窗口大小以适应展开视图
                self.resize(1000, 700)
            
            # 显示调试面板，隐藏欢迎面板
            self.welcomePanel.setVisible(False)
            self.debugPanel.setVisible(True)
            self.log_message("摄像头预览面板已显示")
            
        else:
            self.debugModeBtn.setText("开发者模式")
            self.log_message("开发者调试模式已关闭")
            
            # 如果当前是展开视图，隐藏调试面板，显示欢迎面板
            if self.expanded_view:
                self.debugPanel.setVisible(False)
                self.welcomePanel.setVisible(True)
                self.log_message("摄像头预览面板已隐藏")
        
        # 保存设置
        self.settings.setValue('debug_mode', checked)
    
    def toggle_expanded_view(self, checked=None):
        """切换展开/紧凑视图"""
        if checked is None:
            checked = not self.expanded_view
            
        self.expanded_view = checked
        self.auto_layout = False  # 手动切换时禁用自动布局
        
        if checked:
            # 展开视图：显示右侧面板
            self.contentPanel.setVisible(True)
            self.resize(1000, 700)
            self.log_message("已切换到展开视图模式")
            
            # 根据调试模式显示相应面板
            if self.debug_mode:
                self.welcomePanel.setVisible(False)
                self.debugPanel.setVisible(True)
            else:
                self.welcomePanel.setVisible(True)
                self.debugPanel.setVisible(False)
        else:
            # 紧凑视图：隐藏右侧面板
            self.contentPanel.setVisible(False)
            self.welcomePanel.setVisible(False)
            self.debugPanel.setVisible(False)
            self.resize(450, 700)
            self.log_message("已切换到紧凑视图模式，仅显示控制面板")
        
        # 更新菜单项状态
        self.actionToggleExpandedView.setChecked(checked)
        
        # 保存设置
        self.settings.setValue('expanded_view', checked)
        self.settings.setValue('auto_layout', self.auto_layout)
    
    def update_responsive_layout(self):
        """更新响应式布局"""
        if not self.auto_layout:
            return
            
        current_width = self.width()
        should_expand = current_width >= self.compact_width_threshold
        
        if should_expand != self.expanded_view:
            if should_expand:
                self.log_message("窗口宽度足够，自动切换到展开视图")
            else:
                self.log_message("窗口宽度较小，自动切换到紧凑视图")
            
            self.expanded_view = should_expand
            self.contentPanel.setVisible(should_expand)
            self.actionToggleExpandedView.setChecked(should_expand)
            
            # 在展开模式下根据调试状态显示相应面板
            if should_expand:
                if self.debug_mode:
                    self.welcomePanel.setVisible(False)
                    self.debugPanel.setVisible(True)
                else:
                    self.welcomePanel.setVisible(True)
                    self.debugPanel.setVisible(False)
    
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
        self.contentPanel.setVisible(False)
        self.welcomePanel.setVisible(False)
        self.debugPanel.setVisible(False)
        self.actionToggleExpandedView.setChecked(False)
        
        # 只在程序真正需要时才调整窗口大小
        # 如果当前窗口宽度小于阈值，才强制设置为紧凑模式大小
        if self.width() < self.compact_width_threshold:
            self.resize(450, 700)
        
        # 提示用户如何使用
        if not saved_auto_layout and saved_expanded_view:
            self.log_message("之前使用的是展开视图，可按F11切换回展开模式")
        
        if self.auto_layout:
            self.log_message("自动布局已启用，拖拽窗口边缘可自动调整布局")
            
        # 如果启用了自动布局，立即检查当前窗口大小并更新布局
        # 延迟执行，确保所有初始化完成
        if self.auto_layout:
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(100, self.update_responsive_layout)
    
    def start_detection(self):
        """开始检测"""
        if self.detection_thread and not self.detection_thread.running:
            self.detection_thread.running = True
            self.detection_thread.start()
            
            self.is_detecting = True
            self.startBtn.setEnabled(False)
            self.stopBtn.setEnabled(True)
            self.statusLabel.setText("状态: 运行中")
            self.log_message("手势检测已启动")
            
            # 更新状态样式
            self.statusLabel.setStyleSheet(self.statusLabel.styleSheet() + 
                "color: #047857; background: #d1fae5; border: 1px solid #a7f3d0;")
    
    def stop_detection(self):
        """停止检测"""
        if self.detection_thread and self.detection_thread.running:
            self.detection_thread.stop()
            
            self.is_detecting = False
            self.startBtn.setEnabled(True)
            self.stopBtn.setEnabled(False)
            self.statusLabel.setText("状态: 已停止")
            self.gestureLabel.setText("最近手势: 无")
            self.log_message("手势检测已停止")
            
            # 恢复状态样式
            self.statusLabel.setStyleSheet(self.statusLabel.styleSheet().replace(
                "color: #047857; background: #d1fae5; border: 1px solid #a7f3d0;", ""))
    
    def on_gesture_detected(self, gesture_name: str, hand_type: str, confidence: float):
        """手势检测回调"""
        # 更新手势显示
        gesture_text = f"最近手势: {hand_type}手-{gesture_name} ({confidence:.0f}%)"
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
    
    def on_frame_processed(self, frame):
        """帧处理回调"""
        # 只在调试模式且展开视图下更新摄像头预览
        if self.debug_mode and self.expanded_view and hasattr(self, 'cameraLabel'):
            try:
                # 将OpenCV图像转换为Qt图像并显示
                from PyQt6.QtGui import QImage, QPixmap
                
                height, width, channel = frame.shape
                bytes_per_line = 3 * width
                q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
                q_image = q_image.rgbSwapped()  # BGR to RGB
                
                # 缩放图像以适应显示区域
                pixmap = QPixmap.fromImage(q_image)
                scaled_pixmap = pixmap.scaled(
                    self.cameraLabel.size(), 
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                
                self.cameraLabel.setPixmap(scaled_pixmap)
                
                # 更新摄像头状态提示
                if self.cameraLabel.text() != "":
                    self.cameraLabel.setText("")
                    
            except Exception as e:
                if self.debug_mode:
                    self.log_message(f"摄像头预览更新失败: {e}")
    
    def on_status_updated(self, status: str):
        """状态更新回调"""
        self.statusLabel.setText(f"状态: {status}")
        if self.debug_mode:
            self.log_message(f"{status}")
    
    def log_message(self, message: str):
        """记录日志消息"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        
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
    
    def keyPressEvent(self, event):
        """键盘事件处理"""
        # F12快捷键切换调试模式
        if event.key() == Qt.Key.Key_F12:
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
        if self.detection_thread and self.detection_thread.running:
            self.log_message("正在停止检测线程...")
            self.detection_thread.stop()
        
        # 保存当前设置
        self.settings.setValue('debug_mode', self.debug_mode)
        self.settings.setValue('expanded_view', self.expanded_view)
        self.settings.setValue('auto_layout', self.auto_layout)
        
        self.log_message("感谢使用Gestureyes手视！")
        event.accept()


if __name__ == '__main__':
    app = QApplication([])
    window = MainWindowUI()
    window.show()
    app.exec() 