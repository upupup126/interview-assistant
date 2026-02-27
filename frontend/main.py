"""
面试助手桌面客户端入口
PyQt6应用程序主文件
"""

import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QStyleFactory
from PyQt6.QtCore import Qt, QDir
from PyQt6.QtGui import QFont, QPalette, QColor

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from gui.main_window import MainWindow
from services.api_client import APIClient
from utils.ui_helpers import setup_dark_theme

class InterviewAssistantApp:
    """面试助手应用程序类"""
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.setup_application()
        self.api_client = APIClient()
        self.main_window = None
    
    def setup_application(self):
        """设置应用程序基本配置"""
        # 设置应用程序信息
        self.app.setApplicationName("程序员面试助手")
        self.app.setApplicationVersion("1.0.0")
        self.app.setOrganizationName("Interview Assistant Team")
        
        # 设置应用程序图标
        # self.app.setWindowIcon(QIcon(":/icons/app_icon.png"))
        
        # 设置字体
        font = QFont("思源黑体", 10)
        if not font.exactMatch():
            # 如果思源黑体不可用，使用系统默认字体
            font = QFont("Arial", 10)
        self.app.setFont(font)
        
        # 应用深色主题
        setup_dark_theme(self.app)
        
        # 设置样式
        self.app.setStyle(QStyleFactory.create("Fusion"))
    
    def run(self):
        """运行应用程序"""
        try:
            # 创建主窗口
            self.main_window = MainWindow(self.api_client)
            self.main_window.show()
            
            print("🚀 面试助手桌面客户端启动成功！")
            
            # 启动事件循环
            return self.app.exec()
            
        except Exception as e:
            print(f"❌ 应用程序启动失败: {e}")
            return 1
    
    def cleanup(self):
        """清理资源"""
        if self.main_window:
            self.main_window.close()

def main():
    """主函数"""
    app = InterviewAssistantApp()
    
    try:
        exit_code = app.run()
    except KeyboardInterrupt:
        print("\n👋 用户中断，正在退出...")
        exit_code = 0
    finally:
        app.cleanup()
    
    return exit_code

if __name__ == "__main__":
    sys.exit(main())