"""
现代化UI组件库
"""
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from typing import Optional, Callable, List, Dict

class ModernCard(QFrame):
    """现代化卡片组件"""
    
    clicked = pyqtSignal()
    
    def __init__(self, parent=None, elevation: int = 2, clickable: bool = False):
        super().__init__(parent)
        self.elevation = elevation
        self.clickable = clickable
        self.setup_ui()
        
    def setup_ui(self):
        """设置UI"""
        self.setFrameStyle(QFrame.Shape.NoFrame)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self.update_style()
        
        if self.clickable:
            self.setCursor(Qt.CursorShape.PointingHandCursor)
    
    def update_style(self):
        """更新样式"""
        self.setStyleSheet(f"""
            ModernCard {{
                background-color: white;
                border-radius: 12px;
                border: 1px solid rgba(0, 0, 0, 0.08);
                padding: 16px;
            }}
            ModernCard:hover {{
                border: 1px solid #1976D2;
                background-color: #fafafa;
            }}
        """)
        
        # 添加阴影效果
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(self.elevation * 2)
        shadow.setOffset(0, self.elevation)
        shadow.setColor(QColor(0, 0, 0, 30))
        self.setGraphicsEffect(shadow)
    
    def mousePressEvent(self, event):
        """鼠标点击事件"""
        if self.clickable and event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)

class ModernButton(QPushButton):
    """现代化按钮组件"""
    
    def __init__(self, text: str = "", button_type: str = "primary", parent=None):
        super().__init__(text, parent)
        self.button_type = button_type
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI"""
        self.setMinimumHeight(40)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        styles = {
            "primary": {
                "bg": "#1976D2",
                "hover": "#1565C0",
                "pressed": "#0D47A1",
                "text": "white"
            },
            "secondary": {
                "bg": "transparent",
                "hover": "rgba(25, 118, 210, 0.08)",
                "pressed": "rgba(25, 118, 210, 0.16)",
                "text": "#1976D2"
            },
            "success": {
                "bg": "#4CAF50",
                "hover": "#45a049",
                "pressed": "#3d8b40",
                "text": "white"
            },
            "danger": {
                "bg": "#F44336",
                "hover": "#D32F2F",
                "pressed": "#B71C1C",
                "text": "white"
            }
        }
        
        style = styles.get(self.button_type, styles["primary"])
        
        self.setStyleSheet(f"""
            ModernButton {{
                background-color: {style["bg"]};
                color: {style["text"]};
                border: 1px solid {style["bg"] if style["bg"] != "transparent" else "#1976D2"};
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: 500;
                font-size: 14px;
            }}
            ModernButton:hover {{
                background-color: {style["hover"]};
            }}
            ModernButton:pressed {{
                background-color: {style["pressed"]};
            }}
            ModernButton:disabled {{
                background-color: #E0E0E0;
                color: #9E9E9E;
                border-color: #E0E0E0;
            }}
        """)

class ModernInput(QLineEdit):
    """现代化输入框组件"""
    
    def __init__(self, placeholder: str = "", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI"""
        self.setMinimumHeight(44)
        self.setStyleSheet("""
            ModernInput {
                border: 2px solid #E0E0E0;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 14px;
                background-color: white;
            }
            ModernInput:focus {
                border-color: #1976D2;
                outline: none;
            }
            ModernInput:hover {
                border-color: #BDBDBD;
            }
        """)

class LoadingSpinner(QWidget):
    """加载动画组件"""
    
    def __init__(self, size: int = 32, parent=None):
        super().__init__(parent)
        self.size = size
        self.angle = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.rotate)
        self.setFixedSize(size, size)
    
    def start(self):
        """开始动画"""
        self.timer.start(50)  # 20 FPS
        self.show()
    
    def stop(self):
        """停止动画"""
        self.timer.stop()
        self.hide()
    
    def rotate(self):
        """旋转动画"""
        self.angle = (self.angle + 10) % 360
        self.update()
    
    def paintEvent(self, event):
        """绘制事件"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 绘制圆环
        rect = QRect(2, 2, self.size - 4, self.size - 4)
        pen = QPen(QColor("#1976D2"), 3)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        
        # 旋转画布
        painter.translate(self.size // 2, self.size // 2)
        painter.rotate(self.angle)
        painter.translate(-self.size // 2, -self.size // 2)
        
        # 绘制弧形
        painter.drawArc(rect, 0, 270 * 16)  # 270度弧形

class ModernSidebar(QFrame):
    """现代化侧边栏"""
    
    page_requested = pyqtSignal(str)  # 页面请求信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.nav_buttons = {}
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI"""
        self.setFixedWidth(280)
        self.setStyleSheet("""
            ModernSidebar {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1976D2, stop:1 #1565C0);
                border: none;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 30, 20, 30)
        layout.setSpacing(20)
        
        # 应用标题
        title_label = QLabel("面试助手")
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 24px;
                font-weight: bold;
                padding: 10px 0;
            }
        """)
        layout.addWidget(title_label)
        
        # 导航菜单
        nav_items = [
            ("resume", "📝 简历管理", "管理和优化您的简历"),
            ("leetcode", "💻 LeetCode", "刷题练习和进度跟踪"),
            ("interview", "🎯 面试练习", "八股文练习和语音分析"),
            ("summary", "📊 面试总结", "面试记录和改进建议"),
            ("analytics", "📈 数据统计", "学习进度和成长分析")
        ]
        
        for key, title, description in nav_items:
            btn = self.create_nav_button(title, description, key)
            self.nav_buttons[key] = btn
            layout.addWidget(btn)
        
        # 添加弹性空间
        layout.addStretch()
        
        # 设置按钮
        settings_btn = self.create_nav_button("⚙️ 设置", "应用程序设置", "settings")
        layout.addWidget(settings_btn)
    
    def create_nav_button(self, title: str, description: str, key: str):
        """创建导航按钮"""
        button = QPushButton()
        button.setFixedHeight(80)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # 创建按钮内容
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(15, 10, 15, 10)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        
        desc_label = QLabel(description)
        desc_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.8);
                font-size: 12px;
            }
        """)
        desc_label.setWordWrap(True)
        
        layout.addWidget(title_label)
        layout.addWidget(desc_label)
        
        # 设置按钮样式
        button.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 10px;
                text-align: left;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.3);
            }
            QPushButton:pressed {
                background: rgba(255, 255, 255, 0.3);
            }
        """)
        
        # 将widget设置为按钮的布局
        button_layout = QVBoxLayout(button)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.addWidget(widget)
        
        # 连接点击事件
        button.clicked.connect(lambda: self.page_requested.emit(key))
        
        return button

class ModernContentArea(QWidget):
    """现代化内容区域"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI"""
        self.setStyleSheet("""
            ModernContentArea {
                background-color: #f5f5f5;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建堆叠窗口部件
        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget)
        
        # 添加默认欢迎页面
        welcome_page = self.create_welcome_page()
        self.stacked_widget.addWidget(welcome_page)
    
    def create_welcome_page(self):
        """创建欢迎页面"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(50, 50, 50, 50)
        
        # 欢迎标题
        welcome_label = QLabel("欢迎使用程序员面试助手")
        welcome_label.setStyleSheet("""
            QLabel {
                font-size: 32px;
                font-weight: bold;
                color: #1976D2;
                margin-bottom: 20px;
            }
        """)
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(welcome_label)
        
        # 描述文本
        desc_label = QLabel("全方位提升您的面试竞争力")
        desc_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                color: #666;
                margin-bottom: 40px;
            }
        """)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc_label)
        
        # 功能卡片网格
        cards_widget = self.create_feature_cards()
        layout.addWidget(cards_widget)
        
        return page
    
    def create_feature_cards(self):
        """创建功能卡片"""
        widget = QWidget()
        layout = QGridLayout(widget)
        layout.setSpacing(20)
        
        # 功能卡片数据
        features = [
            ("📝", "简历管理", "AI优化建议，多版本管理"),
            ("💻", "LeetCode刷题", "智能推荐，进度跟踪"),
            ("🎯", "面试练习", "语音分析，AI点评"),
            ("📈", "数据统计", "可视化分析，成长曲线")
        ]
        
        for i, (icon, title, description) in enumerate(features):
            card = self.create_feature_card(icon, title, description)
            row = i // 2
            col = i % 2
            layout.addWidget(card, row, col)
        
        return widget
    
    def create_feature_card(self, icon: str, title: str, description: str):
        """创建功能卡片"""
        card = ModernCard(clickable=True)
        card.setFixedSize(300, 200)
        
        layout = QVBoxLayout(card)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(15)
        
        # 图标
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("""
            QLabel {
                font-size: 48px;
            }
        """)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)
        
        # 标题
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #1976D2;
            }
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # 描述
        desc_label = QLabel(description)
        desc_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #666;
            }
        """)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        return card