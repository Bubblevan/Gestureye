"""
手势历史记录显示组件
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QScrollArea, QFrame, QPushButton, QListWidget, 
                             QListWidgetItem, QGroupBox, QTextEdit)
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
        self.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #e5e7eb;
                border-radius: 6px;
                padding: 6px;
                margin: 1px;
            }
            QFrame:hover {
                background: #f8fafc;
                border-color: #3b82f6;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(3)
        layout.setContentsMargins(6, 4, 6, 4)
        
        # 提取数据
        gesture_name = self.gesture_data.get('gesture', 'Unknown')
        hand_type = self.gesture_data.get('hand_type', 'unknown')
        confidence = self.gesture_data.get('confidence', 0)
        gesture_type = self.gesture_data.get('gesture_type', 'static')
        timestamp = self.gesture_data.get('timestamp', 0)
        details = self.gesture_data.get('details', {})
        
        # 时间显示
        time_str = datetime.fromtimestamp(timestamp).strftime('%H:%M:%S')
        
        # 主要信息行
        main_layout = QHBoxLayout()
        
        # 手势名称和类型
        gesture_label = QLabel(f"🤚 {gesture_name}")
        gesture_label.setStyleSheet("font-weight: bold; color: #1f2937; font-size: 13px;")
        main_layout.addWidget(gesture_label)
        
        main_layout.addStretch()
        
        # 时间
        time_label = QLabel(time_str)
        time_label.setStyleSheet("color: #6b7280; font-size: 11px;")
        main_layout.addWidget(time_label)
        
        layout.addLayout(main_layout)
        
        # 详细信息行
        detail_layout = QHBoxLayout()
        
        # 手部类型
        hand_icon = "🫱" if hand_type.lower() == "right" else "🫲" if hand_type.lower() == "left" else "👋"
        hand_label = QLabel(f"{hand_icon} {hand_type.title()}")
        hand_label.setStyleSheet("color: #4b5563; font-size: 11px;")
        detail_layout.addWidget(hand_label)
        
        # 手势类型
        type_icon = "📌" if gesture_type == "static" else "🔄"
        type_label = QLabel(f"{type_icon} {gesture_type.title()}")
        type_label.setStyleSheet("color: #4b5563; font-size: 11px;")
        detail_layout.addWidget(type_label)
        
        detail_layout.addStretch()
        
        # 置信度
        confidence_color = "#10b981" if confidence >= 80 else "#f59e0b" if confidence >= 60 else "#ef4444"
        confidence_label = QLabel(f"📊 {confidence:.0f}%")
        confidence_label.setStyleSheet(f"color: {confidence_color}; font-size: 11px; font-weight: 600;")
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
        self.setStyleSheet("""
            QFrame {
                background: #f0f9ff;
                border: 1px solid #0ea5e9;
                border-radius: 8px;
                padding: 6px;
            }
        """)
        
        layout = QHBoxLayout(self)  # 改为水平布局
        layout.setSpacing(8)
        
        # 左侧：总计信息
        total_container = QVBoxLayout()
        title1 = QLabel("📊 总计")
        title1.setStyleSheet("font-weight: bold; color: #0369a1; font-size: 12px; margin-bottom: 2px;")
        self.total_label = QLabel("0")
        self.total_label.setStyleSheet("color: #1e40af; font-size: 16px; font-weight: bold;")
        total_container.addWidget(title1)
        total_container.addWidget(self.total_label)
        total_container.addStretch()
        layout.addLayout(total_container)
        
        # 中间：手势排行
        gesture_container = QVBoxLayout()
        title2 = QLabel("🏆 手势排行")
        title2.setStyleSheet("font-weight: bold; color: #0369a1; font-size: 12px; margin-bottom: 2px;")
        self.gesture_label = QLabel("暂无数据")
        self.gesture_label.setStyleSheet("color: #1e40af; font-size: 10px; line-height: 1.2;")
        self.gesture_label.setWordWrap(True)
        gesture_container.addWidget(title2)
        gesture_container.addWidget(self.gesture_label)
        gesture_container.addStretch()
        layout.addLayout(gesture_container, 1)
        
        # 右侧：类型分布
        type_container = QVBoxLayout()
        title3 = QLabel("📈 类型分布")
        title3.setStyleSheet("font-weight: bold; color: #0369a1; font-size: 12px; margin-bottom: 2px;")
        self.type_label = QLabel("无分布")
        self.type_label.setStyleSheet("color: #1e40af; font-size: 10px; line-height: 1.2;")
        self.type_label.setWordWrap(True)
        type_container.addWidget(title3)
        type_container.addWidget(self.type_label)
        type_container.addStretch()
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
        
        # 更新手势排行（只显示前3个）
        if gesture_counts:
            gesture_text = ""
            sorted_gestures = sorted(gesture_counts.items(), key=lambda x: x[1], reverse=True)
            for i, (gesture, count) in enumerate(sorted_gestures[:3]):
                percentage = (count / total * 100) if total > 0 else 0
                gesture_text += f"{i+1}. {gesture}: {count}({percentage:.0f}%)\n"
            self.gesture_label.setText(gesture_text.strip())
        else:
            self.gesture_label.setText("暂无数据")
            
        # 更新类型分布
        if type_counts:
            type_text = ""
            for gtype, count in type_counts.items():
                if count > 0:
                    percentage = (count / total * 100) if total > 0 else 0
                    icon = "📌" if gtype == "static" else "🔄"
                    type_text += f"{icon} {gtype}: {count}({percentage:.0f}%)\n"
            self.type_label.setText(type_text.strip())
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
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(6)
        layout.setContentsMargins(4, 4, 4, 4)
        
        # 标题和控制区域
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
        
        layout.addLayout(header_layout)
        
        # 主内容区域 - 改为上下布局
        content_layout = QVBoxLayout()
        
        # 上方：统计信息（紧凑显示）
        self.stats_widget = GestureStatsWidget()
        self.stats_widget.setMaximumHeight(120)  # 限制高度
        content_layout.addWidget(self.stats_widget)
        
        # 下方：历史记录列表
        history_group = QGroupBox("📜 记录列表")
        history_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e5e7eb;
                border-radius: 6px;
                margin-top: 8px;
                padding-top: 6px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 6px 0 6px;
                color: #374151;
            }
        """)
        
        history_layout = QVBoxLayout(history_group)
        history_layout.setSpacing(4)
        
        # 滚动区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: #f9fafb;
            }
        """)
        
        # 历史记录容器
        self.history_container = QWidget()
        self.history_layout = QVBoxLayout(self.history_container)
        self.history_layout.setSpacing(3)
        self.history_layout.addStretch()
        
        self.scroll_area.setWidget(self.history_container)
        history_layout.addWidget(self.scroll_area)
        
        content_layout.addWidget(history_group)
        
        layout.addLayout(content_layout)
        
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
                self.history_layout.insertWidget(0, item)
            
            # 添加弹性空间
            self.history_layout.addStretch()
            
            # 自动滚动到顶部（最新记录）
            self.scroll_area.verticalScrollBar().setValue(0)
        
        # 更新统计
        self.stats_widget.update_stats(self.gesture_history)
    
    def clear_history(self):
        """清空历史记录"""
        self.gesture_history.clear()
        self.refresh_display()
    
    def get_history_count(self) -> int:
        """获取历史记录数量"""
        return len(self.gesture_history) 