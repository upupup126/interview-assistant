"""
面试助手后端服务入口
FastAPI应用程序主文件
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
import os
from pathlib import Path

from app.core.config import Settings
settings = Settings()
from app.core.database import init_db, SessionLocal
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
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册API路由
app.include_router(resume.router, prefix="/api/v1", tags=["简历管理"])
app.include_router(leetcode.router, prefix="/api/v1", tags=["LeetCode刷题"])
app.include_router(interview.router, prefix="/api/v1", tags=["面试练习"])
app.include_router(analytics.router, prefix="/api/v1", tags=["数据统计"])

# Web前端静态文件目录
WEB_DIR = Path(__file__).parent.parent / "web"
STATIC_DIR = Path(__file__).parent / "static"

@app.on_event("startup")
def startup_event():
    """应用启动时初始化数据库并填充种子数据"""
    init_db()
    _seed_data_if_empty()
    print("🚀 面试助手后端服务启动成功！")
    print(f"📖 API文档地址: http://localhost:{settings.PORT}/docs")
    print(f"🌐 前端地址: http://localhost:{settings.PORT}/")

def _seed_data_if_empty():
    """如果数据库为空则自动填充种子数据"""
    try:
        from app.models.problem import LeetCodeProblem, DailyProgress
        from app.models.interview import InterviewQuestion
        db = SessionLocal()
        try:
            if db.query(LeetCodeProblem).count() == 0 or db.query(InterviewQuestion).count() == 0:
                print("📦 数据库为空，正在填充种子数据...")
                from seed_data import seed_leetcode_problems, seed_interview_questions, seed_daily_progress
                seed_leetcode_problems(db)
                seed_interview_questions(db)
                seed_daily_progress(db)
                print("✅ 种子数据填充完成")
            else:
                print("✅ 数据库已有数据，跳过种子填充")
        finally:
            db.close()
    except Exception as e:
        print(f"⚠️ 种子数据填充失败（不影响服务启动）: {e}")

@app.get("/")
async def root():
    """返回前端页面"""
    index_file = WEB_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file), media_type="text/html")
    return {"message": "面试助手API服务运行中", "version": "1.0.0", "docs": "/docs"}

@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy", "service": "interview-assistant-api"}

@app.get("/style.css")
async def serve_css():
    """提供前端CSS文件"""
    css_file = WEB_DIR / "style.css"
    if css_file.exists():
        return FileResponse(str(css_file), media_type="text/css")

@app.get("/app.js")
async def serve_js():
    """提供前端JS文件"""
    js_file = WEB_DIR / "app.js"
    if js_file.exists():
        return FileResponse(str(js_file), media_type="application/javascript")

# 挂载静态文件目录（必须在路由之后）
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
if WEB_DIR.exists():
    app.mount("/web", StaticFiles(directory=str(WEB_DIR)), name="web")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=False,
        log_level="info"
    )