"""
数据统计分析API路由
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import json

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/overview")
async def get_overview_statistics():
    """获取概览统计数据"""
    try:
        # 模拟综合统计数据
        overview = {
            "total_study_time": 2700,  # 秒
            "total_problems_solved": 128,
            "average_score": 82.5,
            "streak_days": 12,
            "weekly_progress": {
                "problems_this_week": 15,
                "time_this_week": 900,
                "score_improvement": 3.2
            },
            "monthly_progress": {
                "problems_this_month": 45,
                "time_this_month": 2700,
                "avg_score_this_month": 84.2
            }
        }
        
        return {
            "success": True,
            "overview": overview
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取概览统计失败: {str(e)}")


@router.get("/progress-trend")
async def get_progress_trend(
    days: int = Query(30, ge=7, le=365, description="天数范围")
):
    """获取进度趋势数据"""
    try:
        # 生成模拟趋势数据
        trend_data = []
        
        for i in range(days):
            date = datetime.now() - timedelta(days=days-1-i)
            
            # 模拟数据
            leetcode_count = max(0, 2 + (i % 7) + (i // 7) * 0.5)
            interview_count = max(0, 1 + (i % 5) + (i // 10) * 0.3)
            
            trend_data.append({
                "date": date.strftime("%Y-%m-%d"),
                "leetcode_problems": int(leetcode_count),
                "interview_questions": int(interview_count),
                "total_time": int((leetcode_count + interview_count) * 15),  # 分钟
                "average_score": round(75 + (i % 20), 1)
            })
        
        return {
            "success": True,
            "trend_data": trend_data,
            "period": f"最近{days}天"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取进度趋势失败: {str(e)}")


@router.get("/category-distribution")
async def get_category_distribution():
    """获取分类分布数据"""
    try:
        # 模拟分类分布数据
        distribution = {
            "leetcode": {
                "algorithms": {"total": 50, "completed": 35, "avg_score": 82.5},
                "database": {"total": 20, "completed": 12, "avg_score": 75.8},
                "shell": {"total": 5, "completed": 3, "avg_score": 88.0},
                "concurrency": {"total": 8, "completed": 5, "avg_score": 79.2}
            },
            "interview": {
                "algorithms": {"total": 25, "completed": 18, "avg_score": 85.2},
                "os": {"total": 20, "completed": 15, "avg_score": 78.5},
                "network": {"total": 18, "completed": 12, "avg_score": 83.1},
                "database": {"total": 15, "completed": 10, "avg_score": 80.7},
                "language": {"total": 22, "completed": 16, "avg_score": 86.3},
                "system_design": {"total": 12, "completed": 6, "avg_score": 72.5},
                "framework": {"total": 16, "completed": 9, "avg_score": 77.9},
                "project": {"total": 14, "completed": 11, "avg_score": 88.2}
            }
        }
        
        return {
            "success": True,
            "distribution": distribution
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取分类分布失败: {str(e)}")


@router.get("/score-analysis")
async def get_score_analysis():
    """获取分数分析数据"""
    try:
        # 模拟分数分析数据
        analysis = {
            "score_distribution": {
                "0-60": 2,
                "60-70": 8,
                "70-80": 15,
                "80-90": 25,
                "90-100": 12
            },
            "difficulty_performance": {
                "easy": {"avg_score": 88.5, "count": 45},
                "medium": {"avg_score": 78.2, "count": 38},
                "hard": {"avg_score": 65.8, "count": 15}
            },
            "improvement_trend": [
                {"month": "2024-01", "avg_score": 72.5},
                {"month": "2024-02", "avg_score": 75.8},
                {"month": "2024-03", "avg_score": 78.2},
                {"month": "2024-04", "avg_score": 81.5},
                {"month": "2024-05", "avg_score": 82.5}
            ],
            "weak_areas": [
                {"category": "system_design", "avg_score": 65.2, "priority": "high"},
                {"category": "concurrency", "avg_score": 71.8, "priority": "medium"},
                {"category": "database", "avg_score": 75.8, "priority": "low"}
            ]
        }
        
        return {
            "success": True,
            "analysis": analysis
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取分数分析失败: {str(e)}")


@router.get("/time-analysis")
async def get_time_analysis():
    """获取时间分析数据"""
    try:
        # 模拟时间分析数据
        analysis = {
            "daily_pattern": {
                "hours": list(range(24)),
                "activity": [0, 0, 0, 0, 0, 0, 1, 2, 3, 5, 7, 6, 4, 3, 5, 8, 9, 8, 6, 4, 3, 2, 1, 0]
            },
            "weekly_pattern": {
                "days": ["周一", "周二", "周三", "周四", "周五", "周六", "周日"],
                "activity": [8, 7, 6, 8, 9, 5, 4]
            },
            "session_duration": {
                "avg_duration": 25,  # 分钟
                "max_duration": 120,
                "min_duration": 5,
                "total_sessions": 156
            },
            "productivity_metrics": {
                "problems_per_hour": 2.3,
                "avg_thinking_time": 8.5,  # 分钟
                "success_rate": 0.78
            }
        }
        
        return {
            "success": True,
            "analysis": analysis
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取时间分析失败: {str(e)}")


@router.get("/learning-insights")
async def get_learning_insights():
    """获取学习洞察"""
    try:
        # 模拟学习洞察数据
        insights = {
            "strengths": [
                {
                    "area": "算法基础",
                    "score": 88.5,
                    "description": "在基础算法题目上表现优秀，理解深入"
                },
                {
                    "area": "编程语言",
                    "score": 86.3,
                    "description": "语言基础扎实，语法掌握熟练"
                },
                {
                    "area": "项目经验",
                    "score": 88.2,
                    "description": "项目经验丰富，能够很好地表达技术细节"
                }
            ],
            "improvement_areas": [
                {
                    "area": "系统设计",
                    "score": 65.2,
                    "priority": "high",
                    "suggestions": [
                        "多学习大型系统架构设计",
                        "练习系统容量估算",
                        "了解分布式系统常见问题"
                    ]
                },
                {
                    "area": "并发编程",
                    "score": 71.8,
                    "priority": "medium",
                    "suggestions": [
                        "深入理解锁机制",
                        "学习无锁编程",
                        "掌握线程池原理"
                    ]
                }
            ],
            "learning_recommendations": [
                {
                    "type": "focus_area",
                    "title": "重点关注系统设计",
                    "description": "建议每周至少练习2-3道系统设计题目",
                    "priority": "high"
                },
                {
                    "type": "study_plan",
                    "title": "制定并发编程学习计划",
                    "description": "系统学习多线程和并发相关知识",
                    "priority": "medium"
                },
                {
                    "type": "practice_habit",
                    "title": "保持每日练习习惯",
                    "description": "当前连续学习12天，建议继续保持",
                    "priority": "low"
                }
            ],
            "next_milestones": [
                {
                    "title": "完成100道LeetCode题目",
                    "current": 78,
                    "target": 100,
                    "estimated_days": 15
                },
                {
                    "title": "面试平均分达到85分",
                    "current": 82.5,
                    "target": 85.0,
                    "estimated_days": 20
                }
            ]
        }
        
        return {
            "success": True,
            "insights": insights
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取学习洞察失败: {str(e)}")


@router.get("/comparison")
async def get_comparison_data(
    period: str = Query("month", description="比较周期: week, month, quarter")
):
    """获取对比数据"""
    try:
        # 模拟对比数据
        if period == "week":
            comparison = {
                "current_period": "本周",
                "previous_period": "上周",
                "metrics": {
                    "problems_solved": {"current": 15, "previous": 12, "change": 25.0},
                    "study_time": {"current": 450, "previous": 380, "change": 18.4},
                    "average_score": {"current": 84.2, "previous": 81.0, "change": 3.9},
                    "new_topics": {"current": 3, "previous": 2, "change": 50.0}
                }
            }
        elif period == "month":
            comparison = {
                "current_period": "本月",
                "previous_period": "上月",
                "metrics": {
                    "problems_solved": {"current": 45, "previous": 38, "change": 18.4},
                    "study_time": {"current": 1800, "previous": 1520, "change": 18.4},
                    "average_score": {"current": 82.5, "previous": 78.8, "change": 4.7},
                    "new_topics": {"current": 8, "previous": 6, "change": 33.3}
                }
            }
        else:  # quarter
            comparison = {
                "current_period": "本季度",
                "previous_period": "上季度",
                "metrics": {
                    "problems_solved": {"current": 128, "previous": 95, "change": 34.7},
                    "study_time": {"current": 5400, "previous": 4200, "change": 28.6},
                    "average_score": {"current": 82.5, "previous": 76.2, "change": 8.3},
                    "new_topics": {"current": 15, "previous": 12, "change": 25.0}
                }
            }
        
        return {
            "success": True,
            "comparison": comparison
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取对比数据失败: {str(e)}")


@router.post("/export-report")
async def export_analytics_report(
    format: str = Query("pdf", description="导出格式: pdf, excel, json"),
    period: str = Query("month", description="统计周期: week, month, quarter, year"),
    include_charts: bool = Query(True, description="是否包含图表")
):
    """导出分析报告"""
    try:
        # 生成报告内容
        report_data = {
            "generated_at": datetime.utcnow().isoformat(),
            "period": period,
            "format": format,
            "include_charts": include_charts,
            "summary": {
                "total_problems": 128,
                "total_time": 2700,
                "average_score": 82.5,
                "improvement_rate": 15.2
            },
            "detailed_stats": {
                "category_performance": "详细分类表现数据...",
                "time_analysis": "时间分析数据...",
                "learning_insights": "学习洞察数据..."
            }
        }
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"analytics_report_{period}_{timestamp}.{format}"
        
        return {
            "success": True,
            "report_data": report_data,
            "download_url": f"/api/analytics/download/{filename}",
            "filename": filename
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出报告失败: {str(e)}")


@router.get("/goals")
async def get_learning_goals():
    """获取学习目标"""
    try:
        goals = {
            "active_goals": [
                {
                    "id": 1,
                    "title": "完成100道LeetCode算法题",
                    "description": "提升算法解题能力",
                    "target_value": 100,
                    "current_value": 78,
                    "deadline": "2024-06-30",
                    "priority": "high",
                    "category": "leetcode"
                },
                {
                    "id": 2,
                    "title": "面试平均分达到85分",
                    "description": "提高面试表现",
                    "target_value": 85.0,
                    "current_value": 82.5,
                    "deadline": "2024-07-15",
                    "priority": "medium",
                    "category": "interview"
                },
                {
                    "id": 3,
                    "title": "连续学习30天",
                    "description": "养成良好学习习惯",
                    "target_value": 30,
                    "current_value": 12,
                    "deadline": "2024-06-15",
                    "priority": "low",
                    "category": "habit"
                }
            ],
            "completed_goals": [
                {
                    "id": 4,
                    "title": "掌握基础数据结构",
                    "completed_at": "2024-04-20",
                    "achievement_rate": 100
                }
            ],
            "suggested_goals": [
                {
                    "title": "学习系统设计基础",
                    "description": "基于当前薄弱环节的建议目标",
                    "estimated_duration": "2个月",
                    "priority": "high"
                }
            ]
        }
        
        return {
            "success": True,
            "goals": goals
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取学习目标失败: {str(e)}")


@router.get("/achievements")
async def get_achievements():
    """获取成就系统"""
    try:
        achievements = {
            "unlocked": [
                {
                    "id": "first_problem",
                    "title": "初出茅庐",
                    "description": "完成第一道题目",
                    "icon": "🎯",
                    "unlocked_at": "2024-01-15"
                },
                {
                    "id": "week_streak",
                    "title": "持之以恒",
                    "description": "连续学习7天",
                    "icon": "🔥",
                    "unlocked_at": "2024-02-01"
                },
                {
                    "id": "high_score",
                    "title": "学霸模式",
                    "description": "单次面试得分90分以上",
                    "icon": "⭐",
                    "unlocked_at": "2024-02-15"
                }
            ],
            "locked": [
                {
                    "id": "hundred_problems",
                    "title": "百题斩",
                    "description": "完成100道题目",
                    "icon": "💯",
                    "progress": 78,
                    "target": 100
                },
                {
                    "id": "month_streak",
                    "title": "月度坚持",
                    "description": "连续学习30天",
                    "icon": "📅",
                    "progress": 12,
                    "target": 30
                }
            ],
            "statistics": {
                "total_achievements": 15,
                "unlocked_count": 8,
                "completion_rate": 53.3
            }
        }
        
        return {
            "success": True,
            "achievements": achievements
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取成就数据失败: {str(e)}")