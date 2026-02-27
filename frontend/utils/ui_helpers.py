"""
UI辅助工具
提供通用的UI组件和样式设置
"""

from PyQt6.QtWidgets import (
    QWidget, QFrame, QPushButton, QLabel, QVBoxLayout, QHBoxLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QColor, QFont

def setup_dark_theme(app):
    """设置深色主题"""
    palette = QPalette()
    
    # 窗口颜色
    palette.setColor(QPalette.ColorRole.Window, QColor(45, 45, 45))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
    
    # 基础颜色
    palette.setColor(QPalette.ColorRole.Base, QColor(30, 30, 30))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(60, 60, 60))
    
    # 文本颜色
    palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
    
    # 按钮颜色
    palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
    
    # 高亮颜色
    palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(0, 0, 0))
    
    app.setPalette(palette)

def create_card_widget(parent=None):
    """创建卡片样式的widget"""
    card = QFrame(parent)
    card.setFrameStyle(QFrame.Shape.Box)
    card.setStyleSheet("""
        QFrame {
            background-color: white;
            border: 1px solid #e0e0e0;
            border-radius: 12px;
            padding: 20px;
        }
        QFrame:hover {
            border: 1px solid #1976D2;
            box-shadow: 0 4px 12px rgba(25, 118, 210, 0.15);
        }
    """)
    return card

def create_gradient_button(text: str, primary_color: str = "#1976D2", parent=None):
    """创建渐变按钮"""
    button = QPushButton(text, parent)
    button.setStyleSheet(f"""
        QPushButton {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {primary_color}, stop:1 #1565C0);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 12px 24px;
            font-weight: bold;
            font-size: 14px;
        }}
        QPushButton:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #2196F3, stop:1 {primary_color});
        }}
        QPushButton:pressed {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #1565C0, stop:1 #0D47A1);
        }}
    """)
    button.setCursor(Qt.CursorShape.PointingHandCursor)
    return button

def create_icon_button(icon_text: str, tooltip: str = "", parent=None):
    """创建图标按钮"""
    button = QPushButton(icon_text, parent)
    button.setFixedSize(40, 40)
    button.setToolTip(tooltip)
    button.setStyleSheet("""
        QPushButton {
            background-color: rgba(25, 118, 210, 0.1);
            border: 1px solid rgba(25, 118, 210, 0.3);
            border-radius: 20px;
            font-size: 16px;
            color: #1976D2;
        }
        QPushButton:hover {
            background-color: rgba(25, 118, 210, 0.2);
            border: 1px solid rgba(25, 118, 210, 0.5);
        }
        QPushButton:pressed {
            background-color: rgba(25, 118, 210, 0.3);
        }
    """)
    button.setCursor(Qt.CursorShape.PointingHandCursor)
    return button

def create_section_title(text: str, parent=None):
    """创建章节标题"""
    label = QLabel(text, parent)
    label.setStyleSheet("""
        QLabel {
            font-size: 20px;
            font-weight: bold;
            color: #1976D2;
            padding: 10px 0;
            border-bottom: 2px solid #1976D2;
            margin-bottom: 15px;
        }
    """)
    return label

def create_info_card(title: str, value: str, description: str = "", parent=None):
    """创建信息卡片"""
    card = create_card_widget(parent)
    card.setFixedHeight(120)
    
    layout = QVBoxLayout(card)
    layout.setSpacing(5)
    
    # 标题
    title_label = QLabel(title)
    title_label.setStyleSheet("""
        QLabel {
            font-size: 14px;
            color: #666;
            font-weight: 500;
        }
    """)
    layout.addWidget(title_label)
    
    # 数值
    value_label = QLabel(value)
    value_label.setStyleSheet("""
        QLabel {
            font-size: 28px;
            font-weight: bold;
            color: #1976D2;
        }
    """)
    layout.addWidget(value_label)
    
    # 描述
    if description:
        desc_label = QLabel(description)
        desc_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #999;
            }
        """)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
    
    layout.addStretch()
    return card

def apply_card_hover_effect(widget: QWidget):
    """为widget添加卡片悬停效果"""
    widget.setStyleSheet(widget.styleSheet() + """
        QWidget:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        }
    """)

def create_status_badge(text: str, status_type: str = "default", parent=None):
    """创建状态徽章"""
    badge = QLabel(text, parent)
    
    colors = {
        "success": "#4CAF50",
        "warning": "#FF9800", 
        "error": "#F44336",
        "info": "#2196F3",
        "default": "#9E9E9E"
    }
    
    color = colors.get(status_type, colors["default"])
    
    badge.setStyleSheet(f"""
        QLabel {{
            background-color: {color};
            color: white;
            border-radius: 10px;
            padding: 4px 12px;
            font-size: 12px;
            font-weight: bold;
        }}
    """)
    badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
    return badge