"""
应用程序控制器 - 实现MVC模式的Controller层
"""
from PyQt6.QtCore import QObject, pyqtSignal
from typing import Dict, Any, Optional
from services.api_client import APIClient
from models.app_state import AppState

class AppController(QObject):
    """应用程序主控制器"""
    
    # 信号定义
    page_changed = pyqtSignal(str)  # 页面切换信号
    data_updated = pyqtSignal(str, dict)  # 数据更新信号
    error_occurred = pyqtSignal(str)  # 错误信号
    loading_started = pyqtSignal(str)  # 加载开始信号
    loading_finished = pyqtSignal(str)  # 加载完成信号
    
    def __init__(self, api_client: APIClient):
        super().__init__()
        self.api_client = api_client
        self.app_state = AppState()
        self.page_controllers = {}
        self._setup_connections()
    
    def _setup_connections(self):
        """设置信号连接"""
        # 连接应用状态信号
        self.app_state.state_changed.connect(self._on_state_changed)
        
        # 连接API客户端（如果有错误处理）
        # self.api_client.error_occurred.connect(self.error_occurred)
    
    def _on_state_changed(self, key: str, value: Any):
        """状态变更处理"""
        if key == "current_page":
            self.page_changed.emit(value)
        
        # 发送数据更新信号
        self.data_updated.emit(key, {"value": value})
    
    def switch_page(self, page_key: str, data: Optional[Dict] = None):
        """切换页面"""
        if page_key != self.app_state.current_page:
            self.loading_started.emit(f"正在加载{page_key}页面...")
            
            # 保存页面数据
            if data:
                self.app_state.set_user_data(f"page_data_{page_key}", data)
            
            # 更新当前页面
            self.app_state.current_page = page_key
            
            self.loading_finished.emit("页面加载完成")
    
    def get_page_data(self, page_key: str) -> Optional[Dict]:
        """获取页面数据"""
        return self.app_state.get_user_data(f"page_data_{page_key}")
    
    def handle_api_error(self, error_message: str):
        """处理API错误"""
        self.error_occurred.emit(f"API错误: {error_message}")
    
    def check_backend_connection(self):
        """检查后端连接状态"""
        try:
            result = self.api_client.health_check()
            if "error" in result:
                self.error_occurred.emit("无法连接到后端服务，请确保后端服务已启动")
                return False
            return True
        except Exception as e:
            self.error_occurred.emit(f"连接检查失败: {str(e)}")
            return False