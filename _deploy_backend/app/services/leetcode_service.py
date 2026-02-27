"""
LeetCode服务层 - 处理题目管理、进度跟踪和学习计划
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from ..models.problem import (
    LeetCodeProblem, ProblemSubmission, StudyPlan, DailyProgress,
    DifficultyEnum
)
from ..core.database import get_db


class LeetCodeService:
    """LeetCode服务类"""
    
    def __init__(self):
        self.db = next(get_db())
    
    # 题目管理
    def get_problems(
        self, 
        difficulty: Optional[str] = None,
        category: Optional[str] = None,
        is_completed: Optional[bool] = None,
        search_keyword: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """获取题目列表"""
        query = self.db.query(LeetCodeProblem)
        
        if difficulty:
            query = query.filter(LeetCodeProblem.difficulty == difficulty)
        if category:
            query = query.filter(LeetCodeProblem.category == category)
        if search_keyword:
            query = query.filter(
                or_(
                    LeetCodeProblem.title.contains(search_keyword),
                    LeetCodeProblem.content.contains(search_keyword)
                )
            )
        
        if is_completed is not None:
            if is_completed:
                query = query.filter(LeetCodeProblem.submissions.any(
                    ProblemSubmission.is_accepted == True
                ))
            else:
                query = query.filter(~LeetCodeProblem.submissions.any(
                    ProblemSubmission.is_accepted == True
                ))
        
        total = query.count()
        problems = query.offset((page - 1) * page_size).limit(page_size).all()
        
        # 序列化
        problems_list = []
        for p in problems:
            problems_list.append({
                "id": p.id,
                "leetcode_id": p.leetcode_id,
                "title": p.title,
                "title_slug": p.title_slug,
                "difficulty": p.difficulty,
                "category": p.category,
                "tags": p.tags if isinstance(p.tags, list) else (eval(p.tags) if p.tags else []),
                "acceptance_rate": p.acceptance_rate,
                "frequency": p.frequency,
                "is_premium": p.is_premium,
                "is_completed": any(s.is_accepted for s in p.submissions) if p.submissions else False
            })
        
        return {
            "problems": problems_list,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
    
    def get_problem_by_id(self, problem_id: int) -> Optional[Dict]:
        """根据ID获取题目详情"""
        p = self.db.query(LeetCodeProblem).filter(LeetCodeProblem.id == problem_id).first()
        if not p:
            return None
        return {
            "id": p.id,
            "leetcode_id": p.leetcode_id,
            "title": p.title,
            "title_slug": p.title_slug,
            "difficulty": p.difficulty,
            "category": p.category,
            "tags": p.tags if isinstance(p.tags, list) else (eval(p.tags) if p.tags else []),
            "content": p.content,
            "hints": p.hints if isinstance(p.hints, list) else (eval(p.hints) if p.hints else []),
            "acceptance_rate": p.acceptance_rate,
            "frequency": p.frequency,
            "is_premium": p.is_premium,
            "submissions_count": len(p.submissions) if p.submissions else 0,
            "is_completed": any(s.is_accepted for s in p.submissions) if p.submissions else False
        }
    
    def get_problem_by_leetcode_id(self, leetcode_id: int):
        """根据LeetCode ID获取题目"""
        return self.db.query(LeetCodeProblem).filter(LeetCodeProblem.leetcode_id == leetcode_id).first()
    
    def create_or_update_problem(self, problem_data: Dict[str, Any]):
        """创建或更新题目"""
        existing = self.get_problem_by_leetcode_id(problem_data["leetcode_id"])
        
        if existing:
            for key, value in problem_data.items():
                if hasattr(existing, key):
                    setattr(existing, key, value)
            existing.updated_at = datetime.utcnow()
            problem = existing
        else:
            problem = LeetCodeProblem(**problem_data)
            self.db.add(problem)
        
        self.db.commit()
        self.db.refresh(problem)
        return problem
    
    def sync_problems_from_crawler(self, problems_data: List[Dict[str, Any]]) -> Dict[str, int]:
        """从爬虫数据同步题目"""
        created_count = 0
        updated_count = 0
        
        for problem_data in problems_data:
            existing = self.get_problem_by_leetcode_id(problem_data["leetcode_id"])
            
            if existing:
                if existing.title != problem_data.get("title"):
                    self.create_or_update_problem(problem_data)
                    updated_count += 1
            else:
                self.create_or_update_problem(problem_data)
                created_count += 1
        
        return {"created": created_count, "updated": updated_count}
    
    # 提交记录管理
    def create_submission(self, submission_data: Dict[str, Any]) -> Dict:
        """创建提交记录"""
        submission = ProblemSubmission(
            problem_id=submission_data.get("problem_id"),
            language=submission_data.get("language", "python"),
            code=submission_data.get("code", ""),
            status=submission_data.get("status", "Accepted"),
            runtime=submission_data.get("runtime"),
            memory=submission_data.get("memory"),
            notes=submission_data.get("notes"),
            approach=submission_data.get("approach"),
            time_complexity=submission_data.get("time_complexity"),
            space_complexity=submission_data.get("space_complexity"),
            is_accepted=submission_data.get("is_accepted", False),
            attempt_count=submission_data.get("attempt_count", 1),
        )
        self.db.add(submission)
        self.db.commit()
        self.db.refresh(submission)
        
        # 更新每日进度
        if submission.is_accepted:
            self._update_daily_progress(datetime.now().date())
        
        return {
            "id": submission.id,
            "problem_id": submission.problem_id,
            "language": submission.language,
            "code": submission.code,
            "status": submission.status,
            "runtime": submission.runtime,
            "memory": submission.memory,
            "is_accepted": submission.is_accepted,
            "created_at": submission.created_at.isoformat() if submission.created_at else None
        }
    
    def get_submissions(
        self, 
        problem_id: Optional[int] = None,
        status: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict]:
        """获取提交记录"""
        query = self.db.query(ProblemSubmission)
        
        if problem_id:
            query = query.filter(ProblemSubmission.problem_id == problem_id)
        if status:
            query = query.filter(ProblemSubmission.status == status)
        
        submissions = query.order_by(ProblemSubmission.created_at.desc()).limit(limit).all()
        
        result = []
        for s in submissions:
            result.append({
                "id": s.id,
                "problem_id": s.problem_id,
                "language": s.language,
                "code": s.code,
                "status": s.status,
                "runtime": s.runtime,
                "memory": s.memory,
                "is_accepted": s.is_accepted,
                "notes": s.notes,
                "approach": s.approach,
                "time_complexity": s.time_complexity,
                "space_complexity": s.space_complexity,
                "created_at": s.created_at.isoformat() if s.created_at else None
            })
        return result
    
    def get_user_statistics(self) -> Dict[str, Any]:
        """获取用户统计信息"""
        total_problems = self.db.query(LeetCodeProblem).count()
        
        completed_problems = self.db.query(LeetCodeProblem).filter(
            LeetCodeProblem.submissions.any(ProblemSubmission.is_accepted == True)
        ).count()
        
        # 按难度统计
        difficulty_stats = {}
        for diff in [DifficultyEnum.EASY, DifficultyEnum.MEDIUM, DifficultyEnum.HARD]:
            total = self.db.query(LeetCodeProblem).filter(LeetCodeProblem.difficulty == diff.value).count()
            completed = self.db.query(LeetCodeProblem).filter(
                and_(
                    LeetCodeProblem.difficulty == diff.value,
                    LeetCodeProblem.submissions.any(ProblemSubmission.is_accepted == True)
                )
            ).count()
            difficulty_stats[diff.value] = {
                "total": total,
                "completed": completed,
                "completion_rate": round(completed / total, 2) if total > 0 else 0
            }
        
        # 按分类统计（动态获取分类）
        categories = self.db.query(LeetCodeProblem.category).distinct().all()
        category_stats = {}
        for (cat,) in categories:
            if not cat:
                continue
            total = self.db.query(LeetCodeProblem).filter(LeetCodeProblem.category == cat).count()
            completed = self.db.query(LeetCodeProblem).filter(
                and_(
                    LeetCodeProblem.category == cat,
                    LeetCodeProblem.submissions.any(ProblemSubmission.is_accepted == True)
                )
            ).count()
            category_stats[cat] = {
                "total": total,
                "completed": completed,
                "completion_rate": round(completed / total, 2) if total > 0 else 0
            }
        
        streak_days = self._calculate_streak()
        recent_progress = self._get_recent_progress(7)
        
        return {
            "total_problems": total_problems,
            "completed_problems": completed_problems,
            "completion_rate": round(completed_problems / total_problems, 2) if total_problems > 0 else 0,
            "difficulty_stats": difficulty_stats,
            "category_stats": category_stats,
            "streak_days": streak_days,
            "recent_progress": recent_progress
        }
    
    # 推荐系统
    def get_recommended_problems(self, count: int = 5) -> List[Dict]:
        """获取推荐题目"""
        # 获取未完成的题目
        uncompleted = self.db.query(LeetCodeProblem).filter(
            ~LeetCodeProblem.submissions.any(ProblemSubmission.is_accepted == True)
        ).limit(count).all()
        
        # 如果未完成题目不够，补充所有题目
        if len(uncompleted) < count:
            remaining = count - len(uncompleted)
            existing_ids = [p.id for p in uncompleted]
            more = self.db.query(LeetCodeProblem).filter(
                ~LeetCodeProblem.id.in_(existing_ids) if existing_ids else True
            ).limit(remaining).all()
            uncompleted.extend(more)
        
        result = []
        for p in uncompleted[:count]:
            result.append({
                "id": p.id,
                "leetcode_id": p.leetcode_id,
                "title": p.title,
                "title_slug": p.title_slug,
                "difficulty": p.difficulty,
                "category": p.category,
                "tags": p.tags if isinstance(p.tags, list) else (eval(p.tags) if p.tags else []),
                "acceptance_rate": p.acceptance_rate,
            })
        return result
    
    def get_daily_challenge(self):
        """获取每日挑战题目"""
        today = datetime.now().date()
        seed = int(today.strftime("%Y%m%d"))
        
        total_problems = self.db.query(LeetCodeProblem).count()
        if total_problems == 0:
            return None
        
        problem_index = seed % total_problems
        p = self.db.query(LeetCodeProblem).offset(problem_index).first()
        if not p:
            return None
        return {
            "date": str(today),
            "leetcode_id": p.leetcode_id,
            "title": p.title,
            "title_slug": p.title_slug,
            "difficulty": p.difficulty,
            "is_premium": p.is_premium,
            "tags": p.tags if isinstance(p.tags, list) else (eval(p.tags) if p.tags else []),
            "category": p.category,
        }
    
    # 私有方法
    def _update_daily_progress(self, date):
        """更新每日进度"""
        from datetime import datetime as dt
        if not isinstance(date, datetime):
            date_dt = datetime.combine(date, datetime.min.time())
        else:
            date_dt = date
            
        progress = self.db.query(DailyProgress).filter(
            func.date(DailyProgress.date) == date
        ).first()
        
        if not progress:
            progress = DailyProgress(
                date=date_dt,
                problems_solved=0,
                problems_attempted=0,
                study_time=0,
                easy_solved=0,
                medium_solved=0,
                hard_solved=0
            )
            self.db.add(progress)
        
        # 计算当天解决的题目数
        solved_count = self.db.query(ProblemSubmission).filter(
            and_(
                func.date(ProblemSubmission.created_at) == date,
                ProblemSubmission.is_accepted == True
            )
        ).count()
        
        progress.problems_solved = solved_count
        self.db.commit()
    
    def _calculate_streak(self) -> int:
        """计算连续刷题天数"""
        today = datetime.now().date()
        streak = 0
        current_date = today
        
        while True:
            progress = self.db.query(DailyProgress).filter(
                func.date(DailyProgress.date) == current_date
            ).first()
            
            if progress and progress.problems_solved > 0:
                streak += 1
                current_date -= timedelta(days=1)
            else:
                break
        
        return streak
    
    def _get_recent_progress(self, days: int) -> List[Dict[str, Any]]:
        """获取最近几天的进度"""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days-1)
        
        progress_list = self.db.query(DailyProgress).filter(
            and_(
                func.date(DailyProgress.date) >= start_date,
                func.date(DailyProgress.date) <= end_date
            )
        ).order_by(DailyProgress.date).all()
        
        result = []
        current_date = start_date
        progress_dict = {}
        for p in progress_list:
            d = p.date.date() if isinstance(p.date, datetime) else p.date
            progress_dict[d] = p
        
        while current_date <= end_date:
            progress = progress_dict.get(current_date)
            result.append({
                "date": current_date.isoformat(),
                "problems_solved": progress.problems_solved if progress else 0,
                "study_time": progress.study_time if progress else 0
            })
            current_date += timedelta(days=1)
        
        return result
