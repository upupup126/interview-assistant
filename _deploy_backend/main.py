"""
面试助手后端服务入口
FastAPI应用程序主文件
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
from pathlib import Path

from app.core.config import Settings
settings = Settings()
from app.core.database import init_db
from app.api import resume, leetcode, interview, analytics

# 创建FastAPI应用实例
app = FastAPI(
    title="面试助手API",
    description="程序员面试助手后端服务API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发环境允许所有来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册API路由
app.include_router(resume.router, prefix="/api/v1/resume", tags=["简历管理"])
app.include_router(leetcode.router, prefix="/api/v1/leetcode", tags=["LeetCode刷题"])
app.include_router(interview.router, prefix="/api/v1/interview", tags=["面试练习"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["数据统计"])

# 静态文件服务
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.on_event("startup")
def startup_event():
    """应用启动时初始化数据库"""
    init_db()
    print("🚀 面试助手后端服务启动成功！")
    print(f"📖 API文档地址: http://localhost:{settings.PORT}/docs")

@app.get("/")
async def root():
    """根路径健康检查"""
    return {
        "message": "面试助手API服务运行中",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy", "service": "interview-assistant-api"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=False,
        log_level="info"
    )