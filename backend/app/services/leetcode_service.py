"""
LeetCode服务层 - 处理题目管理、进度跟踪和学习计划
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from ..models.problem import (
    Problem, Submission, StudyPlan, DailyProgress,
    Difficulty, ProblemCategory, SubmissionStatus
)
from ..core.database import get_db


class LeetCodeService:
    """LeetCode服务类"""
    
    def __init__(self):
        self.db = next(get_db())
    
    # 题目管理
    def get_problems(
        self, 
        difficulty: Optional[Difficulty] = None,
        category: Optional[ProblemCategory] = None,
        is_completed: Optional[bool] = None,
        search_keyword: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """获取题目列表"""
        query = self.db.query(Problem)
        
        # 筛选条件
        if difficulty:
            query = query.filter(Problem.difficulty == difficulty)
        if category:
            query = query.filter(Problem.category == category)
        if search_keyword:
            query = query.filter(
                or_(
                    Problem.title.contains(search_keyword),
                    Problem.description.contains(search_keyword)
                )
            )
        
        # 完成状态筛选
        if is_completed is not None:
            if is_completed:
                query = query.filter(Problem.submissions.any(
                    Submission.status == SubmissionStatus.ACCEPTED
                ))
            else:
                query = query.filter(~Problem.submissions.any(
                    Submission.status == SubmissionStatus.ACCEPTED
                ))
        
        # 分页
        total = query.count()
        problems = query.offset((page - 1) * page_size).limit(page_size).all()
        
        return {
            "problems": problems,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
    
    def get_problem_by_id(self, problem_id: int) -> Optional[Problem]:
        """根据ID获取题目详情"""
        return self.db.query(Problem).filter(Problem.id == problem_id).first()
    
    def get_problem_by_leetcode_id(self, leetcode_id: int) -> Optional[Problem]:
        """根据LeetCode ID获取题目"""
        return self.db.query(Problem).filter(Problem.leetcode_id == leetcode_id).first()
    
    def create_or_update_problem(self, problem_data: Dict[str, Any]) -> Problem:
        """创建或更新题目"""
        existing = self.get_problem_by_leetcode_id(problem_data["leetcode_id"])
        
        if existing:
            # 更新现有题目
            for key, value in problem_data.items():
                if hasattr(existing, key):
                    setattr(existing, key, value)
            existing.updated_at = datetime.utcnow()
            problem = existing
        else:
            # 创建新题目
            problem = Problem(**problem_data)
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
                # 检查是否需要更新
                if (existing.title != problem_data.get("title") or 
                    existing.description != problem_data.get("description")):
                    self.create_or_update_problem(problem_data)
                    updated_count += 1
            else:
                self.create_or_update_problem(problem_data)
                created_count += 1
        
        return {"created": created_count, "updated": updated_count}
    
    # 提交记录管理
    def create_submission(self, submission_data: Dict[str, Any]) -> Submission:
        """创建提交记录"""
        submission = Submission(**submission_data)
        self.db.add(submission)
        self.db.commit()
        self.db.refresh(submission)
        
        # 更新每日进度
        self._update_daily_progress(submission.created_at.date())
        
        return submission
    
    def get_submissions(
        self, 
        problem_id: Optional[int] = None,
        status: Optional[SubmissionStatus] = None,
        limit: int = 50
    ) -> List[Submission]:
        """获取提交记录"""
        query = self.db.query(Submission)
        
        if problem_id:
            query = query.filter(Submission.problem_id == problem_id)
        if status:
            query = query.filter(Submission.status == status)
        
        return query.order_by(Submission.created_at.desc()).limit(limit).all()
    
    def get_user_statistics(self) -> Dict[str, Any]:
        """获取用户统计信息"""
        # 总题目数
        total_problems = self.db.query(Problem).count()
        
        # 已完成题目数
        completed_problems = self.db.query(Problem).filter(
            Problem.submissions.any(Submission.status == SubmissionStatus.ACCEPTED)
        ).count()
        
        # 按难度统计
        difficulty_stats = {}
        for difficulty in Difficulty:
            total = self.db.query(Problem).filter(Problem.difficulty == difficulty).count()
            completed = self.db.query(Problem).filter(
                and_(
                    Problem.difficulty == difficulty,
                    Problem.submissions.any(Submission.status == SubmissionStatus.ACCEPTED)
                )
            ).count()
            difficulty_stats[difficulty.value] = {
                "total": total,
                "completed": completed,
                "completion_rate": completed / total if total > 0 else 0
            }
        
        # 按分类统计
        category_stats = {}
        for category in ProblemCategory:
            total = self.db.query(Problem).filter(Problem.category == category).count()
            completed = self.db.query(Problem).filter(
                and_(
                    Problem.category == category,
                    Problem.submissions.any(Submission.status == SubmissionStatus.ACCEPTED)
                )
            ).count()
            category_stats[category.value] = {
                "total": total,
                "completed": completed,
                "completion_rate": completed / total if total > 0 else 0
            }
        
        # 连续刷题天数
        streak_days = self._calculate_streak()
        
        # 最近7天进度
        recent_progress = self._get_recent_progress(7)
        
        return {
            "total_problems": total_problems,
            "completed_problems": completed_problems,
            "completion_rate": completed_problems / total_problems if total_problems > 0 else 0,
            "difficulty_stats": difficulty_stats,
            "category_stats": category_stats,
            "streak_days": streak_days,
            "recent_progress": recent_progress
        }
    
    # 学习计划管理
    def create_study_plan(self, plan_data: Dict[str, Any]) -> StudyPlan:
        """创建学习计划"""
        plan = StudyPlan(**plan_data)
        self.db.add(plan)
        self.db.commit()
        self.db.refresh(plan)
        return plan
    
    def get_study_plans(self, is_active: Optional[bool] = None) -> List[StudyPlan]:
        """获取学习计划列表"""
        query = self.db.query(StudyPlan)
        
        if is_active is not None:
            query = query.filter(StudyPlan.is_active == is_active)
        
        return query.order_by(StudyPlan.created_at.desc()).all()
    
    def update_study_plan_progress(self, plan_id: int) -> StudyPlan:
        """更新学习计划进度"""
        plan = self.db.query(StudyPlan).filter(StudyPlan.id == plan_id).first()
        if not plan:
            return None
        
        # 计算完成的题目数
        completed_count = 0
        for problem_id in plan.problem_ids:
            problem = self.get_problem_by_id(problem_id)
            if problem and any(sub.status == SubmissionStatus.ACCEPTED for sub in problem.submissions):
                completed_count += 1
        
        plan.completed_count = completed_count
        plan.progress = completed_count / len(plan.problem_ids) if plan.problem_ids else 0
        
        # 检查是否完成
        if plan.progress >= 1.0:
            plan.is_active = False
            plan.completed_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(plan)
        return plan
    
    # 推荐系统
    def get_recommended_problems(self, count: int = 5) -> List[Problem]:
        """获取推荐题目"""
        # 获取用户薄弱的分类
        weak_categories = self._get_weak_categories()
        
        # 获取未完成的题目
        uncompleted_query = self.db.query(Problem).filter(
            ~Problem.submissions.any(Submission.status == SubmissionStatus.ACCEPTED)
        )
        
        recommended = []
        
        # 优先推荐薄弱分类的简单题目
        for category in weak_categories[:2]:
            problems = uncompleted_query.filter(
                and_(
                    Problem.category == category,
                    Problem.difficulty == Difficulty.EASY
                )
            ).limit(2).all()
            recommended.extend(problems)
        
        # 如果推荐数量不够，添加中等难度题目
        if len(recommended) < count:
            remaining = count - len(recommended)
            problems = uncompleted_query.filter(
                Problem.difficulty == Difficulty.MEDIUM
            ).limit(remaining).all()
            recommended.extend(problems)
        
        return recommended[:count]
    
    def get_daily_challenge(self) -> Optional[Problem]:
        """获取每日挑战题目"""
        # 简单的每日题目选择逻辑
        today = datetime.now().date()
        seed = int(today.strftime("%Y%m%d"))
        
        # 使用日期作为种子选择题目
        total_problems = self.db.query(Problem).count()
        if total_problems == 0:
            return None
        
        problem_index = seed % total_problems
        return self.db.query(Problem).offset(problem_index).first()
    
    # 私有方法
    def _update_daily_progress(self, date: datetime.date):
        """更新每日进度"""
        progress = self.db.query(DailyProgress).filter(DailyProgress.date == date).first()
        
        if not progress:
            progress = DailyProgress(date=date, problems_solved=0, time_spent=0)
            self.db.add(progress)
        
        # 计算当天解决的题目数
        solved_count = self.db.query(Submission).filter(
            and_(
                func.date(Submission.created_at) == date,
                Submission.status == SubmissionStatus.ACCEPTED
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
                DailyProgress.date == current_date
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
                DailyProgress.date >= start_date,
                DailyProgress.date <= end_date
            )
        ).order_by(DailyProgress.date).all()
        
        # 填充缺失的日期
        result = []
        current_date = start_date
        progress_dict = {p.date: p for p in progress_list}
        
        while current_date <= end_date:
            progress = progress_dict.get(current_date)
            result.append({
                "date": current_date.isoformat(),
                "problems_solved": progress.problems_solved if progress else 0,
                "time_spent": progress.time_spent if progress else 0
            })
            current_date += timedelta(days=1)
        
        return result
    
    def _get_weak_categories(self) -> List[ProblemCategory]:
        """获取用户薄弱的分类"""
        category_stats = []
        
        for category in ProblemCategory:
            total = self.db.query(Problem).filter(Problem.category == category).count()
            if total == 0:
                continue
                
            completed = self.db.query(Problem).filter(
                and_(
                    Problem.category == category,
                    Problem.submissions.any(Submission.status == SubmissionStatus.ACCEPTED)
                )
            ).count()
            
            completion_rate = completed / total
            category_stats.append((category, completion_rate))
        
        # 按完成率排序，返回完成率最低的分类
        category_stats.sort(key=lambda x: x[1])
        return [cat for cat, rate in category_stats if rate < 0.5]