"""
数据统计分析API路由 - 使用数据库真实数据
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from ..core.database import get_db
from ..models.problem import LeetCodeProblem, ProblemSubmission, DailyProgress
from ..models.interview import InterviewQuestion, VoiceAnswer

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/overview")
async def get_overview_statistics(db: Session = Depends(get_db)):
    """获取概览统计数据（从数据库）"""
    try:
        # LeetCode统计
        total_problems = db.query(LeetCodeProblem).count()
        solved_problems = db.query(LeetCodeProblem).filter(
            LeetCodeProblem.submissions.any(ProblemSubmission.is_accepted == True)
        ).count()
        total_submissions = db.query(ProblemSubmission).count()
        
        # 面试统计
        total_questions = db.query(InterviewQuestion).count()
        total_answered = db.query(VoiceAnswer).count()
        avg_score_result = db.query(func.avg(VoiceAnswer.quality_score)).scalar()
        avg_score = round(float(avg_score_result), 1) if avg_score_result else 0
        
        # 连续刷题天数
        today = datetime.now().date()
        streak = 0
        current_date = today
        while True:
            progress = db.query(DailyProgress).filter(
                func.date(DailyProgress.date) == current_date
            ).first()
            if progress and progress.problems_solved > 0:
                streak += 1
                current_date -= timedelta(days=1)
            else:
                break
        
        # 本周统计
        week_start = today - timedelta(days=today.weekday())
        week_progress = db.query(DailyProgress).filter(
            func.date(DailyProgress.date) >= week_start
        ).all()
        problems_this_week = sum(p.problems_solved for p in week_progress)
        time_this_week = sum(p.study_time for p in week_progress)
        
        # 本月统计
        month_start = today.replace(day=1)
        month_progress = db.query(DailyProgress).filter(
            func.date(DailyProgress.date) >= month_start
        ).all()
        problems_this_month = sum(p.problems_solved for p in month_progress)
        time_this_month = sum(p.study_time for p in month_progress)
        
        overview = {
            "total_study_time": time_this_month * 60,
            "total_problems_solved": solved_problems,
            "total_submissions": total_submissions,
            "total_interview_questions": total_questions,
            "total_interview_answered": total_answered,
            "average_score": avg_score,
            "streak_days": streak,
            "weekly_progress": {
                "problems_this_week": problems_this_week,
                "time_this_week": time_this_week * 60,
            },
            "monthly_progress": {
                "problems_this_month": problems_this_month,
                "time_this_month": time_this_month * 60,
            }
        }
        
        return {"success": True, "overview": overview}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取概览统计失败: {str(e)}")


@router.get("/progress-trend")
async def get_progress_trend(
    days: int = Query(30, ge=7, le=365),
    db: Session = Depends(get_db)
):
    """获取进度趋势数据（从数据库）"""
    try:
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days - 1)
        
        progress_list = db.query(DailyProgress).filter(
            and_(
                func.date(DailyProgress.date) >= start_date,
                func.date(DailyProgress.date) <= end_date
            )
        ).order_by(DailyProgress.date).all()
        
        progress_dict = {}
        for p in progress_list:
            d = p.date.date() if isinstance(p.date, datetime) else p.date
            progress_dict[d] = p
        
        trend_data = []
        current_date = start_date
        while current_date <= end_date:
            progress = progress_dict.get(current_date)
            # 面试答题数
            interview_count = db.query(VoiceAnswer).filter(
                func.date(VoiceAnswer.created_at) == current_date
            ).count()
            
            trend_data.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "leetcode_problems": progress.problems_solved if progress else 0,
                "interview_questions": interview_count,
                "total_time": progress.study_time if progress else 0,
                "easy_solved": progress.easy_solved if progress else 0,
                "medium_solved": progress.medium_solved if progress else 0,
                "hard_solved": progress.hard_solved if progress else 0,
            })
            current_date += timedelta(days=1)
        
        return {
            "success": True,
            "trend_data": trend_data,
            "period": f"最近{days}天"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取进度趋势失败: {str(e)}")


@router.get("/category-distribution")
async def get_category_distribution(db: Session = Depends(get_db)):
    """获取分类分布数据（从数据库）"""
    try:
        # LeetCode分类分布
        leetcode_dist = {}
        categories = db.query(LeetCodeProblem.category).distinct().all()
        for (cat,) in categories:
            if not cat:
                continue
            total = db.query(LeetCodeProblem).filter(LeetCodeProblem.category == cat).count()
            completed = db.query(LeetCodeProblem).filter(
                and_(
                    LeetCodeProblem.category == cat,
                    LeetCodeProblem.submissions.any(ProblemSubmission.is_accepted == True)
                )
            ).count()
            leetcode_dist[cat] = {"total": total, "completed": completed}
        
        # 面试分类分布
        interview_dist = {}
        i_categories = db.query(InterviewQuestion.category).distinct().all()
        for (cat,) in i_categories:
            if not cat:
                continue
            questions = db.query(InterviewQuestion).filter(InterviewQuestion.category == cat).all()
            total = len(questions)
            q_ids = [q.id for q in questions]
            answered = db.query(VoiceAnswer).filter(VoiceAnswer.question_id.in_(q_ids)).count() if q_ids else 0
            avg = db.query(func.avg(VoiceAnswer.quality_score)).filter(
                VoiceAnswer.question_id.in_(q_ids)
            ).scalar() if q_ids else None
            interview_dist[cat] = {
                "total": total,
                "answered": answered,
                "avg_score": round(float(avg), 1) if avg else 0
            }
        
        return {
            "success": True,
            "distribution": {
                "leetcode": leetcode_dist,
                "interview": interview_dist
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取分类分布失败: {str(e)}")


@router.get("/score-analysis")
async def get_score_analysis(db: Session = Depends(get_db)):
    """获取分数分析数据（从数据库）"""
    try:
        # 面试分数分布
        answers = db.query(VoiceAnswer).filter(VoiceAnswer.quality_score.isnot(None)).all()
        
        score_dist = {"0-60": 0, "60-70": 0, "70-80": 0, "80-90": 0, "90-100": 0}
        for a in answers:
            s = a.quality_score
            if s < 60: score_dist["0-60"] += 1
            elif s < 70: score_dist["60-70"] += 1
            elif s < 80: score_dist["70-80"] += 1
            elif s < 90: score_dist["80-90"] += 1
            else: score_dist["90-100"] += 1
        
        # LeetCode按难度的提交统计
        difficulty_perf = {}
        for diff in ["Easy", "Medium", "Hard"]:
            problems = db.query(LeetCodeProblem).filter(LeetCodeProblem.difficulty == diff).all()
            p_ids = [p.id for p in problems]
            total_subs = db.query(ProblemSubmission).filter(
                ProblemSubmission.problem_id.in_(p_ids)
            ).count() if p_ids else 0
            accepted_subs = db.query(ProblemSubmission).filter(
                and_(
                    ProblemSubmission.problem_id.in_(p_ids),
                    ProblemSubmission.is_accepted == True
                )
            ).count() if p_ids else 0
            difficulty_perf[diff] = {
                "total_submissions": total_subs,
                "accepted": accepted_subs,
                "acceptance_rate": round(accepted_subs / total_subs * 100, 1) if total_subs > 0 else 0
            }
        
        analysis = {
            "score_distribution": score_dist,
            "difficulty_performance": difficulty_perf,
            "total_answers": len(answers),
        }
        
        return {"success": True, "analysis": analysis}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取分数分析失败: {str(e)}")


@router.get("/time-analysis")
async def get_time_analysis(db: Session = Depends(get_db)):
    """获取时间分析数据（从数据库）"""
    try:
        # 每日进度统计
        progress_list = db.query(DailyProgress).order_by(DailyProgress.date.desc()).limit(30).all()
        
        total_study_time = sum(p.study_time for p in progress_list)
        total_sessions = len(progress_list)
        avg_duration = round(total_study_time / total_sessions, 1) if total_sessions > 0 else 0
        max_duration = max((p.study_time for p in progress_list), default=0)
        min_duration = min((p.study_time for p in progress_list if p.study_time > 0), default=0)
        
        total_solved = sum(p.problems_solved for p in progress_list)
        total_hours = total_study_time / 60 if total_study_time > 0 else 1
        
        # 按星期统计
        weekly_pattern = {"周一": 0, "周二": 0, "周三": 0, "周四": 0, "周五": 0, "周六": 0, "周日": 0}
        day_names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        weekly_counts = {d: 0 for d in day_names}
        for p in progress_list:
            d = p.date.date() if isinstance(p.date, datetime) else p.date
            day_name = day_names[d.weekday()]
            weekly_pattern[day_name] += p.study_time
            weekly_counts[day_name] += 1
        
        # 取平均
        for d in day_names:
            if weekly_counts[d] > 0:
                weekly_pattern[d] = round(weekly_pattern[d] / weekly_counts[d], 1)
        
        analysis = {
            "daily_pattern": {
                "total_days_tracked": total_sessions,
                "total_study_time_minutes": total_study_time,
            },
            "weekly_pattern": {
                "days": day_names,
                "activity": [weekly_pattern[d] for d in day_names]
            },
            "session_duration": {
                "avg_duration": avg_duration,
                "max_duration": max_duration,
                "min_duration": min_duration,
                "total_sessions": total_sessions
            },
            "productivity_metrics": {
                "problems_per_hour": round(total_solved / total_hours, 1) if total_hours > 0 else 0,
                "total_problems_solved": total_solved,
                "total_study_hours": round(total_hours, 1),
            }
        }
        
        return {"success": True, "analysis": analysis}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取时间分析失败: {str(e)}")


@router.get("/learning-insights")
async def get_learning_insights(db: Session = Depends(get_db)):
    """获取学习洞察（从数据库）"""
    try:
        # 分析各分类表现
        strengths = []
        improvement_areas = []
        
        # LeetCode分类分析
        categories = db.query(LeetCodeProblem.category).distinct().all()
        cat_stats = []
        for (cat,) in categories:
            if not cat:
                continue
            total = db.query(LeetCodeProblem).filter(LeetCodeProblem.category == cat).count()
            completed = db.query(LeetCodeProblem).filter(
                and_(
                    LeetCodeProblem.category == cat,
                    LeetCodeProblem.submissions.any(ProblemSubmission.is_accepted == True)
                )
            ).count()
            rate = completed / total if total > 0 else 0
            cat_stats.append({"category": cat, "total": total, "completed": completed, "rate": rate})
        
        cat_stats.sort(key=lambda x: x["rate"], reverse=True)
        
        for cs in cat_stats[:3]:
            if cs["rate"] > 0.3:
                strengths.append({
                    "area": cs["category"],
                    "score": round(cs["rate"] * 100, 1),
                    "description": f"在{cs['category']}分类中完成了{cs['completed']}/{cs['total']}题"
                })
        
        for cs in cat_stats:
            if cs["rate"] < 0.5:
                improvement_areas.append({
                    "area": cs["category"],
                    "score": round(cs["rate"] * 100, 1),
                    "priority": "high" if cs["rate"] < 0.2 else "medium",
                    "suggestions": [
                        f"建议多练习{cs['category']}相关题目",
                        f"当前完成率{round(cs['rate'] * 100)}%，目标提升至50%以上"
                    ]
                })
        
        # 面试洞察
        i_categories = db.query(InterviewQuestion.category).distinct().all()
        for (cat,) in i_categories:
            if not cat:
                continue
            questions = db.query(InterviewQuestion).filter(InterviewQuestion.category == cat).all()
            q_ids = [q.id for q in questions]
            avg = db.query(func.avg(VoiceAnswer.quality_score)).filter(
                VoiceAnswer.question_id.in_(q_ids)
            ).scalar() if q_ids else None
            if avg and float(avg) >= 80:
                strengths.append({
                    "area": f"面试-{cat}",
                    "score": round(float(avg), 1),
                    "description": f"面试{cat}类题目平均得分{round(float(avg), 1)}"
                })
        
        # 学习建议
        recommendations = []
        if improvement_areas:
            top_weak = improvement_areas[0]
            recommendations.append({
                "type": "focus_area",
                "title": f"重点关注{top_weak['area']}",
                "description": f"建议每周至少练习3道{top_weak['area']}相关题目",
                "priority": "high"
            })
        
        total_problems = db.query(LeetCodeProblem).count()
        solved = db.query(LeetCodeProblem).filter(
            LeetCodeProblem.submissions.any(ProblemSubmission.is_accepted == True)
        ).count()
        
        recommendations.append({
            "type": "progress",
            "title": f"已完成 {solved}/{total_problems} 道题目",
            "description": "保持每日刷题习惯，稳步提升",
            "priority": "medium"
        })
        
        # 里程碑
        next_milestones = []
        if solved < total_problems:
            next_milestones.append({
                "title": f"完成所有{total_problems}道题目",
                "current": solved,
                "target": total_problems,
            })
        
        insights = {
            "strengths": strengths if strengths else [{"area": "起步阶段", "score": 0, "description": "开始刷题吧！"}],
            "improvement_areas": improvement_areas,
            "learning_recommendations": recommendations,
            "next_milestones": next_milestones
        }
        
        return {"success": True, "insights": insights}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取学习洞察失败: {str(e)}")


@router.get("/comparison")
async def get_comparison_data(
    period: str = Query("month"),
    db: Session = Depends(get_db)
):
    """获取对比数据（从数据库）"""
    try:
        today = datetime.now().date()
        
        if period == "week":
            current_start = today - timedelta(days=today.weekday())
            previous_start = current_start - timedelta(weeks=1)
            previous_end = current_start - timedelta(days=1)
            cur_label, prev_label = "本周", "上周"
        elif period == "quarter":
            month = today.month
            quarter_start_month = ((month - 1) // 3) * 3 + 1
            current_start = today.replace(month=quarter_start_month, day=1)
            if quarter_start_month > 3:
                previous_start = today.replace(month=quarter_start_month - 3, day=1)
            else:
                previous_start = today.replace(year=today.year - 1, month=10, day=1)
            previous_end = current_start - timedelta(days=1)
            cur_label, prev_label = "本季度", "上季度"
        else:  # month
            current_start = today.replace(day=1)
            if today.month > 1:
                previous_start = today.replace(month=today.month - 1, day=1)
            else:
                previous_start = today.replace(year=today.year - 1, month=12, day=1)
            previous_end = current_start - timedelta(days=1)
            cur_label, prev_label = "本月", "上月"
        
        # 当前周期数据
        cur_progress = db.query(DailyProgress).filter(
            func.date(DailyProgress.date) >= current_start
        ).all()
        cur_solved = sum(p.problems_solved for p in cur_progress)
        cur_time = sum(p.study_time for p in cur_progress)
        
        # 上个周期数据
        prev_progress = db.query(DailyProgress).filter(
            and_(
                func.date(DailyProgress.date) >= previous_start,
                func.date(DailyProgress.date) <= previous_end
            )
        ).all()
        prev_solved = sum(p.problems_solved for p in prev_progress)
        prev_time = sum(p.study_time for p in prev_progress)
        
        def calc_change(current, previous):
            if previous == 0:
                return "+100%" if current > 0 else "0%"
            change = round((current - previous) / previous * 100, 1)
            return f"+{change}%" if change >= 0 else f"{change}%"
        
        comparison = {
            "current_period": cur_label,
            "previous_period": prev_label,
            "metrics": {
                "problems_solved": {
                    "current": cur_solved,
                    "previous": prev_solved,
                    "change": calc_change(cur_solved, prev_solved)
                },
                "study_time": {
                    "current": cur_time,
                    "previous": prev_time,
                    "change": calc_change(cur_time, prev_time)
                },
            }
        }
        
        return {"success": True, "comparison": comparison}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取对比数据失败: {str(e)}")


@router.post("/export-report")
async def export_analytics_report(
    format: str = Query("pdf"),
    period: str = Query("month"),
    include_charts: bool = Query(True),
    db: Session = Depends(get_db)
):
    """导出分析报告"""
    try:
        total_problems = db.query(LeetCodeProblem).count()
        solved = db.query(LeetCodeProblem).filter(
            LeetCodeProblem.submissions.any(ProblemSubmission.is_accepted == True)
        ).count()
        total_submissions = db.query(ProblemSubmission).count()
        total_answered = db.query(VoiceAnswer).count()
        
        report_data = {
            "generated_at": datetime.utcnow().isoformat(),
            "period": period,
            "format": format,
            "summary": {
                "total_problems": total_problems,
                "solved_problems": solved,
                "total_submissions": total_submissions,
                "interview_answers": total_answered,
            }
        }
        
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
async def get_learning_goals(db: Session = Depends(get_db)):
    """获取学习目标（从数据库数据计算）"""
    try:
        total_problems = db.query(LeetCodeProblem).count()
        solved = db.query(LeetCodeProblem).filter(
            LeetCodeProblem.submissions.any(ProblemSubmission.is_accepted == True)
        ).count()
        total_answered = db.query(VoiceAnswer).count()
        total_questions = db.query(InterviewQuestion).count()
        
        # 连续天数
        today = datetime.now().date()
        streak = 0
        current_date = today
        while True:
            progress = db.query(DailyProgress).filter(
                func.date(DailyProgress.date) == current_date
            ).first()
            if progress and progress.problems_solved > 0:
                streak += 1
                current_date -= timedelta(days=1)
            else:
                break
        
        active_goals = [
            {
                "id": 1,
                "title": f"完成所有{total_problems}道LeetCode题目",
                "description": "提升算法解题能力",
                "target_value": total_problems,
                "current_value": solved,
                "progress": round(solved / total_problems * 100, 1) if total_problems > 0 else 0,
                "category": "leetcode"
            },
            {
                "id": 2,
                "title": f"练习全部{total_questions}道面试题",
                "description": "覆盖所有面试知识点",
                "target_value": total_questions,
                "current_value": total_answered,
                "progress": round(total_answered / total_questions * 100, 1) if total_questions > 0 else 0,
                "category": "interview"
            },
            {
                "id": 3,
                "title": "连续学习30天",
                "description": "养成良好学习习惯",
                "target_value": 30,
                "current_value": streak,
                "progress": round(streak / 30 * 100, 1),
                "category": "habit"
            }
        ]
        
        completed_goals = []
        for g in active_goals[:]:
            if g["current_value"] >= g["target_value"]:
                completed_goals.append(g)
                active_goals.remove(g)
        
        goals = {
            "active_goals": active_goals,
            "completed_goals": completed_goals,
            "suggested_goals": [
                {"title": "每周至少刷5道题", "description": "保持稳定的刷题节奏"},
                {"title": "每道题写解题笔记", "description": "加深理解和记忆"},
            ]
        }
        
        return {"success": True, "goals": goals}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取学习目标失败: {str(e)}")


@router.get("/achievements")
async def get_achievements(db: Session = Depends(get_db)):
    """获取成就系统（从数据库数据计算）"""
    try:
        solved = db.query(LeetCodeProblem).filter(
            LeetCodeProblem.submissions.any(ProblemSubmission.is_accepted == True)
        ).count()
        total_submissions = db.query(ProblemSubmission).count()
        total_answered = db.query(VoiceAnswer).count()
        
        # 连续天数
        today = datetime.now().date()
        streak = 0
        current_date = today
        while True:
            progress = db.query(DailyProgress).filter(
                func.date(DailyProgress.date) == current_date
            ).first()
            if progress and progress.problems_solved > 0:
                streak += 1
                current_date -= timedelta(days=1)
            else:
                break
        
        # 高分回答
        high_score_count = db.query(VoiceAnswer).filter(VoiceAnswer.quality_score >= 90).count()
        
        all_achievements = [
            {"id": "first_problem", "title": "初出茅庐", "description": "完成第一道LeetCode题目",
             "icon": "🎯", "condition": total_submissions >= 1, "progress": min(total_submissions, 1), "target": 1},
            {"id": "first_interview", "title": "面试新手", "description": "完成第一次面试练习",
             "icon": "💬", "condition": total_answered >= 1, "progress": min(total_answered, 1), "target": 1},
            {"id": "five_problems", "title": "小试牛刀", "description": "完成5道题目",
             "icon": "⭐", "condition": solved >= 5, "progress": min(solved, 5), "target": 5},
            {"id": "ten_problems", "title": "渐入佳境", "description": "完成10道题目",
             "icon": "🔥", "condition": solved >= 10, "progress": min(solved, 10), "target": 10},
            {"id": "week_streak", "title": "持之以恒", "description": "连续学习7天",
             "icon": "📅", "condition": streak >= 7, "progress": min(streak, 7), "target": 7},
            {"id": "month_streak", "title": "月度坚持", "description": "连续学习30天",
             "icon": "🏆", "condition": streak >= 30, "progress": min(streak, 30), "target": 30},
            {"id": "high_score", "title": "学霸模式", "description": "面试得分90分以上",
             "icon": "💯", "condition": high_score_count >= 1, "progress": min(high_score_count, 1), "target": 1},
            {"id": "twenty_problems", "title": "二十连斩", "description": "完成20道题目",
             "icon": "🎖️", "condition": solved >= 20, "progress": min(solved, 20), "target": 20},
        ]
        
        unlocked = []
        locked = []
        for a in all_achievements:
            if a["condition"]:
                unlocked.append({
                    "id": a["id"], "title": a["title"], "description": a["description"],
                    "icon": a["icon"], "unlocked_at": datetime.now().strftime("%Y-%m-%d")
                })
            else:
                locked.append({
                    "id": a["id"], "title": a["title"], "description": a["description"],
                    "icon": a["icon"], "progress": a["progress"], "target": a["target"]
                })
        
        achievements = {
            "unlocked": unlocked,
            "locked": locked,
            "statistics": {
                "total_achievements": len(all_achievements),
                "unlocked_count": len(unlocked),
                "completion_rate": round(len(unlocked) / len(all_achievements) * 100, 1)
            }
        }
        
        return {"success": True, "achievements": achievements}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取成就数据失败: {str(e)}")
