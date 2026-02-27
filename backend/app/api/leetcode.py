"""
LeetCode相关API路由
"""
from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from typing import Optional, List
import asyncio

from ..services.crawler_service import CrawlerService
from ..services.leetcode_service import LeetCodeService
from ..models.problem import Difficulty, ProblemCategory, SubmissionStatus

router = APIRouter(prefix="/leetcode", tags=["leetcode"])

# 服务实例
leetcode_service = LeetCodeService()


@router.get("/problems")
async def get_problems(
    difficulty: Optional[Difficulty] = None,
    category: Optional[ProblemCategory] = None,
    is_completed: Optional[bool] = None,
    search_keyword: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    """获取题目列表"""
    try:
        result = leetcode_service.get_problems(
            difficulty=difficulty,
            category=category,
            is_completed=is_completed,
            search_keyword=search_keyword,
            page=page,
            page_size=page_size
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取题目列表失败: {str(e)}")


@router.get("/problems/{problem_id}")
async def get_problem_detail(problem_id: int):
    """获取题目详情"""
    try:
        problem = leetcode_service.get_problem_by_id(problem_id)
        if not problem:
            raise HTTPException(status_code=404, detail="题目不存在")
        return problem
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取题目详情失败: {str(e)}")


@router.post("/sync")
async def sync_problems_from_leetcode(
    background_tasks: BackgroundTasks,
    max_problems: Optional[int] = Query(None, description="最大同步题目数量"),
    batch_size: int = Query(50, ge=1, le=100, description="批次大小")
):
    """从LeetCode同步题目数据"""
    try:
        # 在后台任务中执行同步
        background_tasks.add_task(
            _sync_problems_task, 
            max_problems=max_problems, 
            batch_size=batch_size
        )
        
        return {
            "success": True,
            "message": "题目同步任务已启动，请稍后查看同步结果"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"启动同步任务失败: {str(e)}")


async def _sync_problems_task(max_problems: Optional[int] = None, batch_size: int = 50):
    """后台同步任务"""
    try:
        async with CrawlerService() as crawler:
            # 批量获取题目
            result = await crawler.batch_fetch_problems(
                batch_size=batch_size,
                max_problems=max_problems
            )
            
            if result["success"]:
                # 同步到数据库
                sync_result = leetcode_service.sync_problems_from_crawler(result["problems"])
                print(f"同步完成: 创建 {sync_result['created']} 题，更新 {sync_result['updated']} 题")
            else:
                print(f"同步失败: {result['error']}")
                
    except Exception as e:
        print(f"同步任务异常: {str(e)}")


@router.get("/statistics")
async def get_user_statistics():
    """获取用户统计信息"""
    try:
        stats = leetcode_service.get_user_statistics()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")


@router.get("/daily-challenge")
async def get_daily_challenge():
    """获取每日挑战题目"""
    try:
        # 先尝试从爬虫获取
        async with CrawlerService() as crawler:
            result = await crawler.get_daily_challenge()
            
            if result["success"]:
                daily_problem = result["daily_challenge"]
                
                # 检查数据库中是否已存在该题目
                existing = leetcode_service.get_problem_by_leetcode_id(daily_problem["leetcode_id"])
                if not existing:
                    # 获取详细信息并保存
                    detail_result = await crawler.get_problem_detail(daily_problem["title_slug"])
                    if detail_result["success"]:
                        leetcode_service.create_or_update_problem(detail_result["problem"])
                
                return daily_problem
            else:
                # 如果爬虫失败，从本地数据库获取
                local_challenge = leetcode_service.get_daily_challenge()
                if local_challenge:
                    return {
                        "success": True,
                        "daily_challenge": {
                            "date": "local",
                            "leetcode_id": local_challenge.leetcode_id,
                            "title": local_challenge.title,
                            "title_slug": local_challenge.title_slug,
                            "difficulty": local_challenge.difficulty.value,
                            "is_premium": local_challenge.is_premium,
                            "tags": local_challenge.tags
                        }
                    }
                else:
                    raise HTTPException(status_code=404, detail="暂无每日挑战题目")
                    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取每日挑战失败: {str(e)}")


@router.get("/recommendations")
async def get_recommended_problems(count: int = Query(5, ge=1, le=20)):
    """获取推荐题目"""
    try:
        problems = leetcode_service.get_recommended_problems(count)
        return {"problems": problems}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取推荐题目失败: {str(e)}")


@router.post("/submissions")
async def create_submission(submission_data: dict):
    """创建提交记录"""
    try:
        submission = leetcode_service.create_submission(submission_data)
        return submission
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建提交记录失败: {str(e)}")


@router.get("/submissions")
async def get_submissions(
    problem_id: Optional[int] = None,
    status: Optional[SubmissionStatus] = None,
    limit: int = Query(50, ge=1, le=100)
):
    """获取提交记录"""
    try:
        submissions = leetcode_service.get_submissions(
            problem_id=problem_id,
            status=status,
            limit=limit
        )
        return {"submissions": submissions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取提交记录失败: {str(e)}")


@router.get("/search")
async def search_problems(
    keyword: str = Query(..., description="搜索关键词"),
    limit: int = Query(20, ge=1, le=100)
):
    """搜索题目"""
    try:
        async with CrawlerService() as crawler:
            result = await crawler.search_problems(keyword, limit)
            
            if result["success"]:
                return result
            else:
                raise HTTPException(status_code=500, detail=result["error"])
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索题目失败: {str(e)}")


@router.get("/crawler/health")
async def crawler_health_check():
    """爬虫健康检查"""
    try:
        async with CrawlerService() as crawler:
            result = await crawler.health_check()
            return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"健康检查失败: {str(e)}")


@router.get("/crawler/stats")
async def get_crawler_statistics():
    """获取爬虫统计信息"""
    try:
        crawler = CrawlerService()
        stats = crawler.get_crawler_statistics()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取爬虫统计失败: {str(e)}")