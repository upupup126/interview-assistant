"""
应用配置管理
简化版配置，避免复杂依赖
"""

import os
from pathlib import Path
from typing import List

class Settings:
    """应用配置类"""
    
    def __init__(self):
        # 应用基本配置
        self.APP_NAME = "面试助手API"
        self.VERSION = "1.0.0"
        self.DEBUG = True
        
        # 服务器配置
        self.HOST = os.getenv("HOST", "127.0.0.1")
        self.PORT = int(os.getenv("PORT", "8000"))
        
        # 数据库配置
        self.DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/interview_assistant.db")
        
        # AI服务配置
        self.OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama2")
        
        # 文件存储配置
        self.UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./data/uploads")
        self.TEMPLATE_DIR = os.getenv("TEMPLATE_DIR", "./data/templates")
        self.USER_DATA_DIR = os.getenv("USER_DATA_DIR", "./data/user_data")
        
        # 安全配置
        self.SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
        self.ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
        
        # 爬虫配置
        self.LEETCODE_BASE_URL = os.getenv("LEETCODE_BASE_URL", "https://leetcode.com")
        self.CRAWLER_DELAY = float(os.getenv("CRAWLER_DELAY", "1.0"))
        
        # 语音处理配置
        self.AUDIO_SAMPLE_RATE = int(os.getenv("AUDIO_SAMPLE_RATE", "16000"))
        self.AUDIO_FORMAT = os.getenv("AUDIO_FORMAT", "wav")
        self.MAX_AUDIO_DURATION = int(os.getenv("MAX_AUDIO_DURATION", "300"))
        
        # 日志配置
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        self.LOG_FILE = os.getenv("LOG_FILE", "./logs/app.log")
        
        # 确保必要的目录存在
        self._ensure_directories()
    
    def _ensure_directories(self):
        """确保必要的目录存在"""
        directories = [
            Path(self.UPLOAD_DIR),
            Path(self.TEMPLATE_DIR),
            Path(self.USER_DATA_DIR),
            Path(self.LOG_FILE).parent,
            Path("./data")
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

# 创建全局配置实例
settings = Settings()