"""
手势历史记录显示组件
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QScrollArea, QFrame, QPushButton, QListWidget, 
                             QListWidgetItem, QGroupBox, QTextEdit, QSizePolicy)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QPalette
import json
from datetime import datetime
from typing import Dict, List, Any


class GestureHistoryItem(QFrame):
    """单个手势历史记录项目"""
    
    def __init__(self, gesture_data: Dict[str, Any]):
        super().__init__()
        self.gesture_data = gesture_data
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI"""
        self.setFrameShape(QFrame.Shape.Box)
        # 防止水平溢出，限制最小宽度
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,   # 水平扩展，但不超出容器
            QSizePolicy.Policy.Minimum      # 允许垂直扩展
        )
        self.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #e5e7eb;
                border-radius: 6px;
                padding: 8px;
                margin: 2px;
            }
            QFrame:hover {
                background: #f8fafc;
                border-color: #3b82f6;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(4)
        layout.setContentsMargins(8, 6, 8, 6)
        
        # 提取数据
        gesture_name = self.gesture_data.get('gesture', 'Unknown')
        hand_type = self.gesture_data.get('hand_type', 'unknown')
        confidence = self.gesture_data.get('confidence', 0)
        gesture_type = self.gesture_data.get('gesture_type', 'static')
        timestamp = self.gesture_data.get('timestamp', 0)
        details = self.gesture_data.get('details', {})
        
        # 时间显示
        time_str = datetime.fromtimestamp(timestamp).strftime('%H:%M:%S')
        
        # 第一行：手势名称（完整显示，支持换行）
        gesture_label = QLabel(f"🤚 {gesture_name}")
        gesture_label.setStyleSheet("font-weight: bold; color: #1f2937; font-size: 12px;")
        gesture_label.setWordWrap(True)  # 允许文本换行
        gesture_label.setSizePolicy(
            QSizePolicy.Policy.Expanding,  # 水平扩展
            QSizePolicy.Policy.Minimum     # 垂直最小
        )
        layout.addWidget(gesture_label)
        
        # 第二行：详细信息（水平紧凑布局）
        detail_layout = QHBoxLayout()
        
        # 手部类型（简化显示）
        hand_icon = "🫱" if hand_type.lower() == "right" else "🫲" if hand_type.lower() == "left" else "👋"
        hand_short = "右" if hand_type.lower() == "right" else "左" if hand_type.lower() == "left" else "?"
        hand_label = QLabel(f"{hand_icon}{hand_short}")
        hand_label.setStyleSheet("color: #4b5563; font-size: 10px;")
        detail_layout.addWidget(hand_label)
        
        # 手势类型（简化显示）
        type_icon = "📌" if gesture_type == "static" else "🔄"
        type_short = "静" if gesture_type == "static" else "动"
        type_label = QLabel(f"{type_icon}{type_short}")
        type_label.setStyleSheet("color: #4b5563; font-size: 10px;")
        detail_layout.addWidget(type_label)
        
        # 时间显示
        time_label = QLabel(time_str)
        time_label.setStyleSheet("color: #6b7280; font-size: 10px;")
        detail_layout.addWidget(time_label)
        
        detail_layout.addStretch()
        
        # 置信度（紧凑显示）
        confidence_color = "#10b981" if confidence >= 80 else "#f59e0b" if confidence >= 60 else "#ef4444"
        confidence_label = QLabel(f"{confidence:.0f}%")
        confidence_label.setStyleSheet(f"color: {confidence_color}; font-size: 10px; font-weight: 600;")
        detail_layout.addWidget(confidence_label)
        
        layout.addLayout(detail_layout)
        
        # 如果有额外详情，显示标签
        if details.get('tag'):
            tag = details['tag']
            tag_color = "#10b981" if tag == "start" else "#ef4444" if tag == "end" else "#6b7280"
            tag_label = QLabel(f"🏷️ {tag}")
            tag_label.setStyleSheet(f"color: {tag_color}; font-size: 10px; font-style: italic;")
            layout.addWidget(tag_label)


class GestureStatsWidget(QFrame):
    """手势统计显示组件"""
    
    def __init__(self):
        super().__init__()
        self.gesture_counts = {}
        self.total_gestures = 0
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI"""
        self.setFrameShape(QFrame.Shape.Box)
        # 防止水平溢出
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,  # 水平扩展，但不超出容器
            QSizePolicy.Policy.Minimum     # 垂直最小，允许内容完整显示
        )
        # 设置固定最大宽度，防止溢出
        self.setMaximumWidth(500)  # 小于控制面板宽度
        self.setStyleSheet("""
            QFrame {
                background: #f0f9ff;
                border: 1px solid #0ea5e9;
                border-radius: 8px;
                padding: 6px;
            }
        """)
        
        # 主布局采用垂直布局，避免水平溢出
        layout = QVBoxLayout(self)
        layout.setSpacing(6)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # 第一行：总计信息
        total_row = QHBoxLayout()
        title1 = QLabel("📊 总计")
        title1.setStyleSheet("font-weight: bold; color: #0369a1; font-size: 12px;")
        self.total_label = QLabel("0")
        self.total_label.setStyleSheet("color: #1e40af; font-size: 16px; font-weight: bold;")
        total_row.addWidget(title1)
        total_row.addStretch()
        total_row.addWidget(self.total_label)
        layout.addLayout(total_row)
        
        # 第二行：手势排行（垂直布局，防止溢出）
        gesture_container = QVBoxLayout()
        gesture_container.setSpacing(2)
        title2 = QLabel("🏆 手势排行")
        title2.setStyleSheet("font-weight: bold; color: #0369a1; font-size: 11px;")
        self.gesture_label = QLabel("暂无数据")
        self.gesture_label.setStyleSheet("color: #1e40af; font-size: 10px; line-height: 1.2;")
        self.gesture_label.setWordWrap(True)  # 允许换行
        self.gesture_label.setSizePolicy(
            QSizePolicy.Policy.Expanding,  # 水平扩展
            QSizePolicy.Policy.Minimum     # 垂直最小
        )
        gesture_container.addWidget(title2)
        gesture_container.addWidget(self.gesture_label)
        layout.addLayout(gesture_container)
        
        # 第三行：类型分布（垂直布局，防止溢出）
        type_container = QVBoxLayout()
        type_container.setSpacing(2)
        title3 = QLabel("📈 类型分布")
        title3.setStyleSheet("font-weight: bold; color: #0369a1; font-size: 11px;")
        self.type_label = QLabel("无分布")
        self.type_label.setStyleSheet("color: #1e40af; font-size: 10px; line-height: 1.2;")
        self.type_label.setWordWrap(True)  # 允许换行
        self.type_label.setSizePolicy(
            QSizePolicy.Policy.Expanding,  # 水平扩展
            QSizePolicy.Policy.Minimum     # 垂直最小
        )
        type_container.addWidget(title3)
        type_container.addWidget(self.type_label)
        layout.addLayout(type_container)
    
    def update_stats(self, gesture_history: List[Dict[str, Any]]):
        """更新统计信息"""
        if not gesture_history:
            self.total_label.setText("0")
            self.gesture_label.setText("暂无数据")
            self.type_label.setText("无分布")
            return
        
        # 统计手势类型
        gesture_counts = {}
        hand_counts = {"left": 0, "right": 0, "unknown": 0}
        type_counts = {"static": 0, "dynamic": 0}
        
        for gesture_data in gesture_history:
            gesture_name = gesture_data.get('gesture', 'Unknown')
            hand_type = gesture_data.get('hand_type', 'unknown').lower()
            gesture_type = gesture_data.get('gesture_type', 'static')
            
            # 只统计开始或完成的手势
            details = gesture_data.get('details', {})
            tag = details.get('tag', '')
            if tag == 'end' or (tag == 'start' and gesture_type == 'static'):
                gesture_counts[gesture_name] = gesture_counts.get(gesture_name, 0) + 1
                hand_counts[hand_type] = hand_counts.get(hand_type, 0) + 1
                type_counts[gesture_type] = type_counts.get(gesture_type, 0) + 1
        
        total = sum(gesture_counts.values())
        
        # 更新总计
        self.total_label.setText(str(total))
        
        # 更新手势排行（显示前5个，完整名称）
        if gesture_counts:
            gesture_text = ""
            sorted_gestures = sorted(gesture_counts.items(), key=lambda x: x[1], reverse=True)
            for i, (gesture, count) in enumerate(sorted_gestures[:5]):
                percentage = (count / total * 100) if total > 0 else 0
                # 显示完整手势名称和百分比
                gesture_text += f"{i+1}. {gesture}: {count}次 ({percentage:.0f}%)\n"
            self.gesture_label.setText(gesture_text.strip())
        else:
            self.gesture_label.setText("暂无数据")
            
        # 更新类型分布（紧凑显示）
        if type_counts:
            static_count = type_counts.get("static", 0)
            dynamic_count = type_counts.get("dynamic", 0)
            if static_count > 0 and dynamic_count > 0:
                self.type_label.setText(f"📌{static_count} 🔄{dynamic_count}")
            elif static_count > 0:
                self.type_label.setText(f"📌静态: {static_count}")
            elif dynamic_count > 0:
                self.type_label.setText(f"🔄动态: {dynamic_count}")
            else:
                self.type_label.setText("无分布")
        else:
            self.type_label.setText("无分布")


class GestureHistoryWidget(QWidget):
    """手势历史记录主组件"""
    
    clear_history_requested = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.gesture_history = []
        self.max_display_items = 50
        self.setup_ui()
        
        # 自动刷新定时器
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_display)
        self.refresh_timer.start(1000)  # 每秒刷新一次
    
    def setup_ui(self):
        """设置UI - 整个手势历史区域可滚动"""
        # 设置组件大小策略
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,   # 水平扩展
            QSizePolicy.Policy.Expanding    # 垂直扩展
        )
        
        # 主布局：只包含标题和滚动区域
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(4)
        main_layout.setContentsMargins(4, 4, 4, 4)
        
        # 标题和控制区域（固定在顶部，不滚动）
        header_layout = QHBoxLayout()
        
        title = QLabel("🕒 手势历史记录")
        title.setStyleSheet("font-size: 15px; font-weight: bold; color: #1f2937;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # 清空按钮
        self.clear_btn = QPushButton("🗑️ 清空")
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background: #fee2e2;
                border: 1px solid #fca5a5;
                color: #dc2626;
                padding: 3px 10px;
                border-radius: 4px;
                font-size: 11px;
            }
            QPushButton:hover {
                background: #fecaca;
            }
        """)
        self.clear_btn.clicked.connect(self.clear_history_requested.emit)
        header_layout.addWidget(self.clear_btn)
        
        main_layout.addLayout(header_layout)
        
        # 创建整体滚动区域（包含统计信息和记录列表）
        self.scroll_area = QScrollArea()
        # 设置固定最大宽度，防止溢出
        self.scroll_area.setMaximumWidth(590)  # 小于控制面板宽度
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)  # 禁用水平滚动
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)      # 需要时显示垂直滚动
        # 确保滚动区域不超出容器
        self.scroll_area.setSizePolicy(
            QSizePolicy.Policy.Expanding,   # 水平扩展但不超出
            QSizePolicy.Policy.Expanding    # 垂直扩展
        )
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #e5e7eb;
                border-radius: 4px;
                background: #f9fafb;
            }
            QScrollBar:vertical {
                border: none;
                background: #f1f5f9;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #cbd5e1;
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background: #94a3b8;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                height: 0px;
            }
        """)
        
        # 滚动内容容器（包含统计信息和记录列表）
        self.scroll_content = QWidget()
        # 设置固定最大宽度，防止溢出
        self.scroll_content.setMaximumWidth(580)  # 小于控制面板宽度
        # 确保滚动内容不会水平溢出
        self.scroll_content.setSizePolicy(
            QSizePolicy.Policy.Expanding,   # 水平扩展但适应容器
            QSizePolicy.Policy.Minimum      # 垂直最小，允许内容扩展
        )
        content_layout = QVBoxLayout(self.scroll_content)
        content_layout.setSpacing(8)
        content_layout.setContentsMargins(6, 6, 6, 6)
        
        # 统计信息区域（完整显示，不压缩）
        self.stats_widget = GestureStatsWidget()
        self.stats_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding,  # 水平扩展
            QSizePolicy.Policy.Minimum     # 垂直最小，允许完整显示
        )
        content_layout.addWidget(self.stats_widget)
        
        # 记录列表区域（直接添加，不再嵌套滚动）
        history_group = QGroupBox("📜 记录列表")
        # 设置固定最大宽度，防止溢出
        history_group.setMaximumWidth(580)  # 小于控制面板宽度
        history_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e5e7eb;
                border-radius: 6px;
                margin-top: 4px;
                padding-top: 4px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 4px 0 4px;
                color: #374151;
                font-size: 11px;
            }
        """)
        
        # 记录列表容器（不再需要内部滚动）
        history_layout = QVBoxLayout(history_group)
        history_layout.setSpacing(2)
        history_layout.setContentsMargins(8, 12, 8, 8)
        
        # 历史记录直接容器（所有记录项的容器）
        self.history_container = QWidget()
        # 确保历史记录容器不会水平溢出
        self.history_container.setSizePolicy(
            QSizePolicy.Policy.Expanding,    # 水平扩展但适应父容器
            QSizePolicy.Policy.Minimum       # 垂直适应内容
        )
        self.history_layout = QVBoxLayout(self.history_container)
        self.history_layout.setSpacing(6)
        self.history_layout.setContentsMargins(0, 0, 0, 0)
        
        history_layout.addWidget(self.history_container)
        content_layout.addWidget(history_group)
        
        # 设置滚动区域的内容
        self.scroll_area.setWidget(self.scroll_content)
        main_layout.addWidget(self.scroll_area)
        
        # 初始状态
        self.show_empty_state()
    
    def show_empty_state(self):
        """显示空状态"""
        empty_label = QLabel("🤷‍♂️ 暂无手势记录\n开始手势检测后，这里将显示识别到的手势历史")
        empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_label.setStyleSheet("""
            QLabel {
                color: #6b7280;
                font-size: 13px;
                line-height: 1.4;
                padding: 30px;
                background: white;
                border: 2px dashed #d1d5db;
                border-radius: 6px;
            }
        """)
        self.history_layout.insertWidget(0, empty_label)
    
    def add_gesture(self, gesture_data: Dict[str, Any]):
        """添加手势记录"""
        self.gesture_history.append(gesture_data)
        
        # 限制历史记录数量
        if len(self.gesture_history) > self.max_display_items * 2:
            self.gesture_history = self.gesture_history[-self.max_display_items:]
        
        # 刷新显示并自动滚动到新记录
        self.refresh_display()
    
    def refresh_display(self):
        """刷新显示"""
        # 清空现有显示
        for i in reversed(range(self.history_layout.count())):
            child = self.history_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        if not self.gesture_history:
            self.show_empty_state()
        else:
            # 显示最近的记录（倒序）
            recent_history = self.gesture_history[-self.max_display_items:]
            for gesture_data in reversed(recent_history):
                item = GestureHistoryItem(gesture_data)
                self.history_layout.addWidget(item)  # 直接添加到末尾，保持时间顺序
            
            # 优化滚动行为：滚动到底部显示最新记录
            # 使用QTimer延迟执行，确保布局完成后再滚动
            QTimer.singleShot(50, self._scroll_to_latest)
        
        # 更新统计
        self.stats_widget.update_stats(self.gesture_history)
    
    def clear_history(self):
        """清空历史记录"""
        self.gesture_history.clear()
        self.refresh_display()
    
    def get_history_count(self) -> int:
        """获取历史记录数量"""
        return len(self.gesture_history)
    
    def add_test_data(self):
        """添加测试数据（用于验证滚动效果）"""
        import time
        test_gestures = [
            {"gesture": "thumbs_up", "hand_type": "right", "confidence": 85, "gesture_type": "static", "timestamp": time.time(), "details": {"tag": "start"}},
            {"gesture": "peace_sign", "hand_type": "left", "confidence": 92, "gesture_type": "static", "timestamp": time.time() + 1, "details": {"tag": "end"}},
            {"gesture": "swipe_left", "hand_type": "right", "confidence": 78, "gesture_type": "dynamic", "timestamp": time.time() + 2, "details": {"tag": "start"}},
            {"gesture": "swipe_right", "hand_type": "left", "confidence": 88, "gesture_type": "dynamic", "timestamp": time.time() + 3, "details": {"tag": "end"}},
            {"gesture": "ok_gesture", "hand_type": "right", "confidence": 95, "gesture_type": "static", "timestamp": time.time() + 4, "details": {"tag": "start"}},
        ]
        
        for gesture_data in test_gestures:
            self.add_gesture(gesture_data)
    
    def _scroll_to_latest(self):
        """滚动到最新记录（底部）"""
        try:
            # 确保布局更新完成
            self.scroll_content.updateGeometry()
            self.scroll_area.updateGeometry()
            
            # 滚动到底部，显示最新添加的记录
            scrollbar = self.scroll_area.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
        except Exception as e:
            print(f"滚动到最新记录失败: {e}") 