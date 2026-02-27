"""
数据库连接和会话管理
简化版，使用同步SQLite
"""

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session
from .config import Settings

# 创建配置实例
settings = Settings()

# 使用同步SQLite引擎
DATABASE_URL = settings.DATABASE_URL.replace("sqlite+aiosqlite://", "sqlite://")
engine = create_engine(
    DATABASE_URL,
    echo=settings.DEBUG,
    connect_args={"check_same_thread": False}  # SQLite特定配置
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 数据库模型基类
class Base(DeclarativeBase):
    """数据库模型基类"""
    metadata = MetaData()

def init_db():
    """初始化数据库，创建所有表"""
    # 导入所有模型以确保表被创建
    from app.models import resume, problem, interview
    Base.metadata.create_all(bind=engine)

def get_db() -> Session:
    """获取数据库会话的依赖注入函数"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def close_db():
    """关闭数据库连接"""
    engine.dispose()