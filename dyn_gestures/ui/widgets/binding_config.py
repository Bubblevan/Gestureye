"""
手势绑定配置对话框
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QPushButton, QComboBox, QLineEdit, QCheckBox, QGroupBox, QGridLayout,
    QMessageBox, QWidget, QSplitter, QTextEdit, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
import json
import os

class GestureBindingDialog(QDialog):
    """手势绑定配置对话框"""
    
    gesture_bindings_updated = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("手势绑定配置")
        self.setModal(True)
        self.resize(600, 500)
        
        # 加载当前绑定配置
        self.current_bindings = {}
        self.load_current_bindings()
        
        # 设置UI
        self.setup_ui()
        self.load_bindings_to_ui()
        
        # 连接信号
        self.setup_connections()
    
    def setup_ui(self):
        """设置UI界面"""
        layout = QVBoxLayout()
        
        # 标题
        title_label = QLabel("手势绑定配置")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #1f2937;
                padding: 12px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8fafc, stop:1 #e2e8f0);
                border: 1px solid #cbd5e1;
                border-radius: 8px;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(title_label)
        
        # 创建分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 左侧 - 手势列表
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        gesture_group = QGroupBox("手势列表")
        gesture_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #374151;
                border: 2px solid #cbd5e1;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
            }
        """)
        gesture_layout = QVBoxLayout()
        
        self.gesture_list = QListWidget()
        self.gesture_list.setStyleSheet("""
            QListWidget {
                background: white;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                selection-background-color: #2563eb;
                font-size: 13px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #e5e7eb;
            }
            QListWidget::item:selected {
                background: #2563eb;
                color: white;
            }
            QListWidget::item:hover {
                background: #f1f5f9;
            }
        """)
        gesture_layout.addWidget(self.gesture_list)
        
        gesture_group.setLayout(gesture_layout)
        left_layout.addWidget(gesture_group)
        
        # 右侧 - 配置区域
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        config_group = QGroupBox("配置设置")
        config_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #374151;
                border: 2px solid #cbd5e1;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
            }
        """)
        config_layout = QGridLayout()
        
        # 启用/禁用
        config_layout.addWidget(QLabel("启用状态:"), 0, 0)
        self.enabled_checkbox = QCheckBox("启用此手势")
        self.enabled_checkbox.setStyleSheet("""
            QCheckBox {
                font-size: 13px;
                color: #374151;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
            }
            QCheckBox::indicator:checked {
                background: #059669;
                border: 1px solid #047857;
            }
        """)
        config_layout.addWidget(self.enabled_checkbox, 0, 1)
        
        # 动作类型
        config_layout.addWidget(QLabel("动作类型:"), 1, 0)
        self.action_type_combo = QComboBox()
        self.action_type_combo.addItems([
            "系统功能",
            "键盘快捷键",
            "自定义功能"
        ])
        self.action_type_combo.setStyleSheet("""
            QComboBox {
                background: white;
                border: 1px solid #cbd5e1;
                border-radius: 4px;
                padding: 6px;
                font-size: 13px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                width: 12px;
                height: 12px;
            }
        """)
        config_layout.addWidget(self.action_type_combo, 1, 1)
        
        # 动作设置
        config_layout.addWidget(QLabel("动作设置:"), 2, 0)
        self.action_combo = QComboBox()
        self.action_combo.setEditable(False)  # 改为纯选择模式
        self.action_combo.setStyleSheet("""
            QComboBox {
                background: white;
                border: 1px solid #cbd5e1;
                border-radius: 4px;
                padding: 6px;
                font-size: 13px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                width: 12px;
                height: 12px;
            }
        """)
        config_layout.addWidget(self.action_combo, 2, 1)
        
        # 描述
        config_layout.addWidget(QLabel("描述:"), 3, 0)
        self.description_edit = QLineEdit()
        self.description_edit.setStyleSheet("""
            QLineEdit {
                background: white;
                border: 1px solid #cbd5e1;
                border-radius: 4px;
                padding: 6px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 2px solid #2563eb;
            }
        """)
        config_layout.addWidget(self.description_edit, 3, 1)
        
        config_group.setLayout(config_layout)
        right_layout.addWidget(config_group)
        
        # 说明区域
        help_group = QGroupBox("使用说明")
        help_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #374151;
                border: 2px solid #cbd5e1;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
            }
        """)
        help_layout = QVBoxLayout()
        
        self.help_text = QTextEdit()
        self.help_text.setReadOnly(True)
        self.help_text.setMaximumHeight(120)
        self.help_text.setStyleSheet("""
            QTextEdit {
                background: #f8fafc;
                border: 1px solid #e5e7eb;
                border-radius: 4px;
                padding: 8px;
                font-size: 12px;
                color: #4b5563;
            }
        """)
        self.help_text.setPlainText("""动作类型说明:
• 系统功能: 音量控制、媒体控制、亮度控制等
• 键盘快捷键: 常用的组合键和单独按键
• 自定义功能: 用户自定义的特殊功能

选择合适的动作类型后，从下拉菜单中选择具体的动作
修改后点击"保存"生效，"重置"恢复默认设置""")
        help_layout.addWidget(self.help_text)
        
        help_group.setLayout(help_layout)
        right_layout.addWidget(help_group)
        
        # 添加到分割器
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([250, 350])
        
        layout.addWidget(splitter)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("保存配置")
        self.save_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #059669, stop:1 #047857);
                border: none;
                color: white;
                font-size: 14px;
                font-weight: 600;
                padding: 8px 16px;
                border-radius: 6px;
                min-width: 100px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #10b981, stop:1 #059669);
            }
        """)
        
        self.reset_btn = QPushButton("重置")
        self.reset_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #d97706, stop:1 #b45309);
                border: none;
                color: white;
                font-size: 14px;
                font-weight: 600;
                padding: 8px 16px;
                border-radius: 6px;
                min-width: 100px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f59e0b, stop:1 #d97706);
            }
        """)
        
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #6b7280, stop:1 #4b5563);
                border: none;
                color: white;
                font-size: 14px;
                font-weight: 600;
                padding: 8px 16px;
                border-radius: 6px;
                min-width: 100px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #9ca3af, stop:1 #6b7280);
            }
        """)
        
        button_layout.addStretch()
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.reset_btn)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def setup_connections(self):
        """设置信号连接"""
        self.gesture_list.currentRowChanged.connect(self.on_gesture_selected)
        self.action_type_combo.currentTextChanged.connect(self.on_action_type_changed)
        self.enabled_checkbox.toggled.connect(self.on_config_changed)
        self.action_combo.currentTextChanged.connect(self.on_config_changed)
        self.description_edit.textChanged.connect(self.on_config_changed)
        
        self.save_btn.clicked.connect(self.save_configuration)
        self.reset_btn.clicked.connect(self.reset_current_gesture)
        self.cancel_btn.clicked.connect(self.reject)
    
    def load_current_bindings(self):
        """加载当前绑定配置"""
        try:
            config_file = "gesture_bindings.json"
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    self.current_bindings = json.load(f)
            else:
                # 使用默认配置
                self.current_bindings = {
                    "thumbs_up": {"action_type": "system_function", "action": "volume_up", "description": "音量增加", "enabled": True},
                    "thumbs_down": {"action_type": "system_function", "action": "volume_down", "description": "音量减少", "enabled": True},
                    "peace": {"action_type": "system_function", "action": "play_pause", "description": "播放/暂停", "enabled": True},
                    "ok": {"action_type": "system_function", "action": "volume_mute", "description": "静音", "enabled": True},
                    "pinch": {"action_type": "system_function", "action": "previous_track", "description": "上一首", "enabled": True},
                    "wave": {"action_type": "system_function", "action": "next_track", "description": "下一首", "enabled": True},
                    "swipe_left": {"action_type": "keyboard_shortcut", "action": "alt+left", "description": "后退", "enabled": True},
                    "swipe_right": {"action_type": "keyboard_shortcut", "action": "alt+right", "description": "前进", "enabled": True},
                    "swipe_up": {"action_type": "keyboard_shortcut", "action": "page_up", "description": "向上滚动", "enabled": True},
                    "swipe_down": {"action_type": "keyboard_shortcut", "action": "page_down", "description": "向下滚动", "enabled": True}
                }
        except Exception as e:
            print(f"加载配置失败: {e}")
            self.current_bindings = {}
    
    def load_bindings_to_ui(self):
        """加载绑定到UI"""
        # 清空列表
        self.gesture_list.clear()
        
        # 手势名称映射
        gesture_names = {
            "thumbs_up": "拇指向上",
            "thumbs_down": "拇指向下", 
            "peace": "V字手势",
            "ok": "OK手势",
            "pinch": "捏合手势",
            "wave": "挥手手势",
            "swipe_left": "向左滑动",
            "swipe_right": "向右滑动",
            "swipe_up": "向上滑动",
            "swipe_down": "向下滑动"
        }
        
        # 添加手势到列表
        for gesture_key, gesture_name in gesture_names.items():
            item = QListWidgetItem(gesture_name)
            item.setData(Qt.ItemDataRole.UserRole, gesture_key)
            
            # 设置样式根据启用状态
            if gesture_key in self.current_bindings:
                enabled = self.current_bindings[gesture_key].get("enabled", True)
                if not enabled:
                    item.setText(f"{gesture_name} (已禁用)")
                    item.setData(Qt.ItemDataRole.ForegroundRole, "#9ca3af")
            
            self.gesture_list.addItem(item)
        
        # 选中第一个项目
        if self.gesture_list.count() > 0:
            self.gesture_list.setCurrentRow(0)
    
    def on_gesture_selected(self, row):
        """手势选择事件"""
        if row < 0:
            return
            
        item = self.gesture_list.item(row)
        if not item:
            return
            
        gesture_key = item.data(Qt.ItemDataRole.UserRole)
        if gesture_key not in self.current_bindings:
            return
            
        config = self.current_bindings[gesture_key]
        
        # 更新UI
        self.enabled_checkbox.setChecked(config.get("enabled", True))
        
        # 设置动作类型
        action_type = config.get("action_type", "system_function")
        if action_type == "system_function":
            self.action_type_combo.setCurrentText("系统功能")
        elif action_type == "keyboard_shortcut":
            self.action_type_combo.setCurrentText("键盘快捷键")
        else:
            self.action_type_combo.setCurrentText("自定义功能")
        
        # 更新动作选项
        self.on_action_type_changed(self.action_type_combo.currentText())
        
        # 根据内部值设置选中项
        current_action = config.get("action", "")
        self.set_action_combo_by_value(current_action)
        
        # 设置描述
        self.description_edit.setText(config.get("description", ""))
    
    def set_action_combo_by_value(self, value):
        """根据内部值设置下拉框选中项"""
        for i in range(self.action_combo.count()):
            item_data = self.action_combo.itemData(i)
            if item_data == value:
                self.action_combo.setCurrentIndex(i)
                break
    
    def on_action_type_changed(self, action_type):
        """动作类型改变事件"""
        self.action_combo.clear()
        
        if action_type == "系统功能":
            # 系统功能选项：显示名称 + 内部值
            actions = [
                ("音量增加", "volume_up"),
                ("音量减少", "volume_down"),
                ("静音切换", "volume_mute"),
                ("播放/暂停", "play_pause"),
                ("下一首", "next_track"),
                ("上一首", "previous_track"),
                ("亮度增加", "brightness_up"),
                ("亮度减少", "brightness_down"),
                ("锁定屏幕", "lock_screen"),
                ("睡眠模式", "sleep_mode"),
                ("唤醒屏幕", "wake_screen"),
                ("显示桌面", "show_desktop"),
                ("任务管理器", "task_manager"),
                ("文件管理器", "file_manager"),
                ("关机", "shutdown"),
                ("重启", "restart")
            ]
            
            for display_name, internal_value in actions:
                self.action_combo.addItem(display_name, internal_value)
                
        elif action_type == "键盘快捷键":
            # 键盘快捷键选项：显示名称 + 内部值
            actions = [
                ("复制 (Ctrl+C)", "ctrl+c"),
                ("粘贴 (Ctrl+V)", "ctrl+v"),
                ("剪切 (Ctrl+X)", "ctrl+x"),
                ("撤销 (Ctrl+Z)", "ctrl+z"),
                ("重做 (Ctrl+Y)", "ctrl+y"),
                ("全选 (Ctrl+A)", "ctrl+a"),
                ("保存 (Ctrl+S)", "ctrl+s"),
                ("打开 (Ctrl+O)", "ctrl+o"),
                ("新建 (Ctrl+N)", "ctrl+n"),
                ("查找 (Ctrl+F)", "ctrl+f"),
                ("应用切换 (Alt+Tab)", "alt+tab"),
                ("后退 (Alt+Left)", "alt+left"),
                ("前进 (Alt+Right)", "alt+right"),
                ("向上滚动 (Page Up)", "page_up"),
                ("向下滚动 (Page Down)", "page_down"),
                ("文档开头 (Home)", "home"),
                ("文档末尾 (End)", "end"),
                ("删除 (Delete)", "delete"),
                ("回车键 (Enter)", "enter"),
                ("退格键 (Backspace)", "backspace"),
                ("空格键 (Space)", "space"),
                ("Tab键", "tab"),
                ("ESC键", "escape"),
                ("F1功能键", "f1"),
                ("F2功能键", "f2"),
                ("F3功能键", "f3"),
                ("F4功能键", "f4"),
                ("F5功能键", "f5"),
                ("F6功能键", "f6"),
                ("F7功能键", "f7"),
                ("F8功能键", "f8"),
                ("F9功能键", "f9"),
                ("F10功能键", "f10"),
                ("F11功能键", "f11"),
                ("F12功能键", "f12"),
                ("Win+D (显示桌面)", "win+d"),
                ("Win+E (文件管理器)", "win+e"),
                ("Win+L (锁定屏幕)", "win+l"),
                ("Win+R (运行)", "win+r"),
                ("Win+S (搜索)", "win+s"),
                ("Win+Tab (任务视图)", "win+tab"),
                ("截图 (Win+Shift+S)", "win+shift+s"),
                ("关闭窗口 (Alt+F4)", "alt+f4"),
                ("最小化 (Win+M)", "win+m"),
                ("最大化 (Win+Up)", "win+up"),
                ("还原 (Win+Down)", "win+down"),
                ("左半屏 (Win+Left)", "win+left"),
                ("右半屏 (Win+Right)", "win+right")
            ]
            
            for display_name, internal_value in actions:
                self.action_combo.addItem(display_name, internal_value)
                
        else:
            # 自定义功能选项
            actions = [
                ("自定义功能1", "custom_function_1"),
                ("自定义功能2", "custom_function_2"),
                ("自定义功能3", "custom_function_3"),
                ("自定义功能4", "custom_function_4"),
                ("自定义功能5", "custom_function_5"),
                ("打开计算器", "open_calculator"),
                ("打开记事本", "open_notepad"),
                ("打开浏览器", "open_browser"),
                ("打开邮件客户端", "open_mail"),
                ("打开音乐播放器", "open_music_player"),
                ("打开视频播放器", "open_video_player"),
                ("打开画图工具", "open_paint"),
                ("打开摄像头", "open_camera"),
                ("打开控制面板", "open_control_panel"),
                ("打开设置", "open_settings")
            ]
            
            for display_name, internal_value in actions:
                self.action_combo.addItem(display_name, internal_value)
    
    def on_config_changed(self):
        """配置改变事件"""
        # 获取当前选中的手势
        current_row = self.gesture_list.currentRow()
        if current_row < 0:
            return
            
        item = self.gesture_list.item(current_row)
        if not item:
            return
            
        gesture_key = item.data(Qt.ItemDataRole.UserRole)
        if gesture_key not in self.current_bindings:
            return
        
        # 更新配置
        config = self.current_bindings[gesture_key]
        config["enabled"] = self.enabled_checkbox.isChecked()
        
        # 转换动作类型
        action_type_text = self.action_type_combo.currentText()
        if action_type_text == "系统功能":
            config["action_type"] = "system_function"
        elif action_type_text == "键盘快捷键":
            config["action_type"] = "keyboard_shortcut"
        else:
            config["action_type"] = "custom_function"
        
        # 获取选中的动作的内部值
        current_index = self.action_combo.currentIndex()
        if current_index >= 0:
            config["action"] = self.action_combo.itemData(current_index)
        
        config["description"] = self.description_edit.text()
        
        # 更新列表显示
        gesture_names = {
            "thumbs_up": "拇指向上",
            "thumbs_down": "拇指向下", 
            "peace": "V字手势",
            "ok": "OK手势",
            "pinch": "捏合手势",
            "wave": "挥手手势",
            "swipe_left": "向左滑动",
            "swipe_right": "向右滑动",
            "swipe_up": "向上滑动",
            "swipe_down": "向下滑动"
        }
        
        gesture_name = gesture_names.get(gesture_key, gesture_key)
        if config["enabled"]:
            item.setText(gesture_name)
            item.setData(Qt.ItemDataRole.ForegroundRole, "#000000")
        else:
            item.setText(f"{gesture_name} (已禁用)")
            item.setData(Qt.ItemDataRole.ForegroundRole, "#9ca3af")
    
    def reset_current_gesture(self):
        """重置当前手势"""
        current_row = self.gesture_list.currentRow()
        if current_row < 0:
            return
            
        item = self.gesture_list.item(current_row)
        if not item:
            return
            
        gesture_key = item.data(Qt.ItemDataRole.UserRole)
        
        # 默认配置
        default_configs = {
            "thumbs_up": {"action_type": "system_function", "action": "volume_up", "description": "音量增加", "enabled": True},
            "thumbs_down": {"action_type": "system_function", "action": "volume_down", "description": "音量减少", "enabled": True},
            "peace": {"action_type": "system_function", "action": "play_pause", "description": "播放/暂停", "enabled": True},
            "ok": {"action_type": "system_function", "action": "volume_mute", "description": "静音", "enabled": True},
            "pinch": {"action_type": "system_function", "action": "previous_track", "description": "上一首", "enabled": True},
            "wave": {"action_type": "system_function", "action": "next_track", "description": "下一首", "enabled": True},
            "swipe_left": {"action_type": "keyboard_shortcut", "action": "alt+left", "description": "后退", "enabled": True},
            "swipe_right": {"action_type": "keyboard_shortcut", "action": "alt+right", "description": "前进", "enabled": True},
            "swipe_up": {"action_type": "keyboard_shortcut", "action": "page_up", "description": "向上滚动", "enabled": True},
            "swipe_down": {"action_type": "keyboard_shortcut", "action": "page_down", "description": "向下滚动", "enabled": True}
        }
        
        if gesture_key in default_configs:
            self.current_bindings[gesture_key] = default_configs[gesture_key].copy()
            self.on_gesture_selected(current_row)  # 刷新UI
    
    def save_configuration(self):
        """保存配置"""
        try:
            # 保存到文件
            with open("gesture_bindings.json", 'w', encoding='utf-8') as f:
                json.dump(self.current_bindings, f, ensure_ascii=False, indent=2)
            
            # 发送信号
            self.gesture_bindings_updated.emit(self.current_bindings)
            
            # 关闭对话框
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存配置失败: {e}") 