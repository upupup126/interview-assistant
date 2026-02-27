"""
现代化主窗口界面 - 基于MVC架构重构
"""

from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QStackedWidget
from PyQt6.QtCore import Qt, pyqtSlot, QTimer
from PyQt6.QtGui import QFont

from ..services.api_client import APIClient
from ..core.app_controller import AppController
from ..components.modern_widgets import ModernSidebar, ModernContentArea, LoadingSpinner
from ..models.app_state import AppState
from .leetcode_page import LeetCodePage
from .interview_page import InterviewPage
from .analytics_page import AnalyticsPage

class MainWindow(QMainWindow):
    """现代化主窗口类"""
    
    def __init__(self, api_client: APIClient):
        super().__init__()
        self.api_client = api_client
        
        # 初始化控制器和状态管理
        self.app_controller = AppController(api_client)
        self.app_state = self.app_controller.app_state
        
        # UI组件
        self.sidebar = None
        self.content_area = None
        self.loading_spinner = None
        self.status_label = None
        
        self.init_ui()
        self.setup_connections()
        self.check_backend_status()
    
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("程序员面试助手 v1.0")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        
        # 应用用户偏好
        preferences = self.app_state.get_preferences()
        if preferences.window_geometry:
            self.restoreGeometry(preferences.window_geometry.get('geometry', b''))
        
        # 创建中央窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 创建侧边栏
        self.sidebar = ModernSidebar()
        main_layout.addWidget(self.sidebar)
        
        # 创建内容区域 - 使用堆叠窗口管理多个页面
        self.content_stack = QStackedWidget()
        
        # 初始化各个页面
        self.init_pages()
        
        main_layout.addWidget(self.content_stack)
        
        # 创建状态栏
        self.setup_status_bar()
        
        # 设置布局比例
        main_layout.setStretch(0, 0)  # 侧边栏固定宽度
        main_layout.setStretch(1, 1)  # 内容区域自适应
    
    def init_pages(self):
        """初始化所有页面"""
        # 页面字典
        self.pages = {}
        
        # 简历管理页面（占位符）
        resume_page = QWidget()
        resume_layout = QVBoxLayout(resume_page)
        resume_label = QLabel("简历管理页面")
        resume_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        resume_label.setFont(QFont("Microsoft YaHei", 24))
        resume_label.setStyleSheet("color: #666; padding: 50px;")
        resume_layout.addWidget(resume_label)
        
        self.pages["resume"] = resume_page
        self.content_stack.addWidget(resume_page)
        
        # LeetCode刷题页面
        self.leetcode_page = LeetCodePage()
        self.pages["leetcode"] = self.leetcode_page
        self.content_stack.addWidget(self.leetcode_page)
        
        # 面试练习页面
        self.interview_page = InterviewPage()
        self.pages["interview"] = self.interview_page
        self.content_stack.addWidget(self.interview_page)
        
        # 面试总结页面（占位符）
        summary_page = QWidget()
        summary_layout = QVBoxLayout(summary_page)
        summary_label = QLabel("面试总结页面")
        summary_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        summary_label.setFont(QFont("Microsoft YaHei", 24))
        summary_label.setStyleSheet("color: #666; padding: 50px;")
        summary_layout.addWidget(summary_label)
        
        self.pages["summary"] = summary_page
        self.content_stack.addWidget(summary_page)
        
        # 数据统计页面
        self.analytics_page = AnalyticsPage()
        self.pages["analytics"] = self.analytics_page
        self.content_stack.addWidget(self.analytics_page)
        
        # 设置页面（占位符）
        settings_page = QWidget()
        settings_layout = QVBoxLayout(settings_page)
        settings_label = QLabel("设置页面")
        settings_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        settings_label.setFont(QFont("Microsoft YaHei", 24))
        settings_label.setStyleSheet("color: #666; padding: 50px;")
        settings_layout.addWidget(settings_label)
        
        self.pages["settings"] = settings_page
        self.content_stack.addWidget(settings_page)
        
        # 默认显示简历页面
        self.content_stack.setCurrentWidget(self.pages["resume"])
    
    def setup_status_bar(self):
        """设置状态栏"""
        status_bar = self.statusBar()
        
        # 状态标签
        self.status_label = QLabel("就绪")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #666;
                padding: 4px 8px;
            }
        """)
        status_bar.addWidget(self.status_label)
        
        # 加载动画
        self.loading_spinner = LoadingSpinner(size=16)
        status_bar.addPermanentWidget(self.loading_spinner)
        
        # 后端连接状态
        self.connection_label = QLabel("🔴 后端未连接")
        self.connection_label.setStyleSheet("""
            QLabel {
                color: #F44336;
                padding: 4px 8px;
                font-weight: bold;
            }
        """)
        status_bar.addPermanentWidget(self.connection_label)
    
    def setup_connections(self):
        """设置信号连接"""
        # 侧边栏导航
        self.sidebar.page_requested.connect(self.switch_page)
        
        # 应用控制器信号
        self.app_controller.page_changed.connect(self.on_page_changed)
        self.app_controller.error_occurred.connect(self.show_error)
        self.app_controller.loading_started.connect(self.show_loading)
        self.app_controller.loading_finished.connect(self.hide_loading)
        
        # 应用状态信号
        self.app_state.user_preferences_changed.connect(self.on_preferences_changed)
    
    def check_backend_status(self):
        """检查后端服务状态"""
        if self.app_controller.check_backend_connection():
            self.connection_label.setText("🟢 后端已连接")
            self.connection_label.setStyleSheet("""
                QLabel {
                    color: #4CAF50;
                    padding: 4px 8px;
                    font-weight: bold;
                }
            """)
        else:
            # 设置定时器重试连接
            QTimer.singleShot(5000, self.check_backend_status)
    
    @pyqtSlot(str)
    def switch_page(self, page_key: str):
        """切换页面"""
        self.app_controller.switch_page(page_key)
    
    @pyqtSlot(str)
    def on_page_changed(self, page_key: str):
        """页面切换处理"""
        self.status_label.setText(f"当前页面: {self.get_page_display_name(page_key)}")
        
        # 切换到对应页面
        if page_key in self.pages:
            self.content_stack.setCurrentWidget(self.pages[page_key])
            
            # 根据页面类型刷新数据
            if page_key == "leetcode" and hasattr(self, 'leetcode_page'):
                self.leetcode_page.refresh_data()
            elif page_key == "interview" and hasattr(self, 'interview_page'):
                self.interview_page.refresh_data()
            elif page_key == "analytics" and hasattr(self, 'analytics_page'):
                self.analytics_page.refresh_data()
        else:
            print(f"未找到页面: {page_key}")
    
    def get_page_display_name(self, page_key: str) -> str:
        """获取页面显示名称"""
        page_names = {
            "resume": "简历管理",
            "leetcode": "LeetCode刷题", 
            "interview": "面试练习",
            "summary": "面试总结",
            "analytics": "数据统计",
            "settings": "设置"
        }
        return page_names.get(page_key, page_key)
    
    @pyqtSlot(str)
    def show_error(self, message: str):
        """显示错误信息"""
        self.status_label.setText(f"错误: {message}")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #F44336;
                padding: 4px 8px;
                font-weight: bold;
            }
        """)
        
        # 3秒后恢复正常状态
        QTimer.singleShot(3000, self.reset_status)
    
    @pyqtSlot(str)
    def show_loading(self, message: str):
        """显示加载状态"""
        self.status_label.setText(message)
        self.loading_spinner.start()
    
    @pyqtSlot(str)
    def hide_loading(self, message: str = ""):
        """隐藏加载状态"""
        self.loading_spinner.stop()
        if message:
            self.status_label.setText(message)
        else:
            self.reset_status()
    
    def reset_status(self):
        """重置状态"""
        self.status_label.setText("就绪")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #666;
                padding: 4px 8px;
            }
        """)
    
    @pyqtSlot(object)
    def on_preferences_changed(self, preferences):
        """用户偏好变更处理"""
        # 应用字体大小变更
        font = self.font()
        font.setPointSize(preferences.font_size)
        self.setFont(font)
        
        # 这里可以添加主题切换等其他偏好应用
        print(f"偏好已更新: 主题={preferences.theme}, 字体大小={preferences.font_size}")
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        # 保存窗口几何信息
        geometry_data = {
            'geometry': self.saveGeometry(),
            'state': self.saveState()
        }
        self.app_state.update_preferences(window_geometry=geometry_data)
        
        # 清理资源
        if hasattr(self, 'loading_spinner'):
            self.loading_spinner.stop()
        
        event.accept()