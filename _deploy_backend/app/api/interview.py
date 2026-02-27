"""
面试练习API路由 - 使用数据库真实数据
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..models.interview import InterviewQuestion, VoiceAnswer, InterviewSession
from ..services.ai_service import AIService
from ..services.voice_service import VoiceService

router = APIRouter(prefix="/interview", tags=["interview"])

ai_service = AIService()
voice_service = VoiceService()


@router.get("/questions")
async def get_questions(
    category: Optional[str] = None,
    difficulty: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """获取面试题目列表（从数据库）"""
    try:
        query = db.query(InterviewQuestion).filter(InterviewQuestion.is_active == True)

        if category:
            query = query.filter(InterviewQuestion.category == category)
        if difficulty:
            query = query.filter(InterviewQuestion.difficulty == difficulty)

        questions = query.limit(limit).all()

        questions_list = []
        for q in questions:
            questions_list.append({
                "id": q.id,
                "title": q.title,
                "question": q.content,
                "category": q.category,
                "difficulty": q.difficulty,
                "tags": q.tags if isinstance(q.tags, list) else (eval(q.tags) if q.tags else []),
                "reference_answer": q.reference_answer,
                "key_points": q.key_points if isinstance(q.key_points, list) else (eval(q.key_points) if q.key_points else []),
                "importance": q.importance,
                "frequency": q.frequency,
            })

        return {
            "success": True,
            "questions": questions_list,
            "total": len(questions_list)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取题目失败: {str(e)}")


@router.post("/analyze-answer")
async def analyze_answer(
    question_id: int = Form(...),
    answer_text: str = Form(...),
    audio_file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """分析回答（文字或语音）"""
    try:
        # 查询题目获取参考答案
        question = db.query(InterviewQuestion).filter(InterviewQuestion.id == question_id).first()

        reference_answer = ""
        key_points = []
        if question:
            reference_answer = question.reference_answer or ""
            kp = question.key_points
            if isinstance(kp, list):
                key_points = kp
            elif kp:
                try:
                    key_points = eval(kp)
                except:
                    key_points = []

        # 简单的评分逻辑：基于回答长度和关键词匹配
        answer_len = len(answer_text)
        base_score = min(60 + answer_len // 10, 95)

        # 检查关键词匹配
        matched_points = 0
        for point in key_points:
            if isinstance(point, str) and point.lower() in answer_text.lower():
                matched_points += 1
        
        keyword_bonus = min(matched_points * 5, 20) if key_points else 10
        
        content_score = min(base_score + keyword_bonus, 98)
        logic_score = min(base_score - 2 + keyword_bonus, 95)
        accuracy_score = min(base_score + 5 + keyword_bonus, 98)
        overall_score = round((content_score + logic_score + accuracy_score) / 3, 1)

        # 生成反馈
        strengths = []
        improvements = []
        
        if answer_len > 50:
            strengths.append("回答内容较为详细")
        if answer_len > 100:
            strengths.append("对问题有较深入的理解")
        if matched_points > 0:
            strengths.append(f"涵盖了{matched_points}个关键要点")
        
        if answer_len < 50:
            improvements.append("建议增加回答的详细程度")
        if matched_points < len(key_points) // 2 and key_points:
            improvements.append("建议覆盖更多关键知识点")
        improvements.append("可以通过举例来增强回答的说服力")

        analysis_result = {
            "question_id": question_id,
            "answer_text": answer_text,
            "analysis": {
                "content_score": content_score,
                "logic_score": logic_score,
                "accuracy_score": accuracy_score,
                "overall_score": overall_score,
                "strengths": strengths if strengths else ["回答涵盖了问题的主要方面"],
                "improvements": improvements,
                "detailed_feedback": f"整体评分 {overall_score} 分。" + (
                    f"回答中提及了{matched_points}个关键要点。" if key_points else ""
                ) + "建议在表达时更加结构化，先概括后详述。",
                "key_points_coverage": {
                    "total": len(key_points),
                    "matched": matched_points
                }
            },
            "voice_analysis": None,
            "created_at": datetime.utcnow().isoformat()
        }

        # 保存回答记录到数据库
        voice_answer = VoiceAnswer(
            question_id=question_id,
            transcribed_text=answer_text,
            quality_score=overall_score,
            quality_level="优秀" if overall_score >= 85 else "良好" if overall_score >= 70 else "一般",
            feedback=analysis_result["analysis"]["detailed_feedback"],
        )
        db.add(voice_answer)
        db.commit()

        if audio_file:
            voice_analysis = await voice_service.analyze_speech_quality(audio_file)
            analysis_result["voice_analysis"] = voice_analysis

        return {
            "success": True,
            "analysis": analysis_result
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"分析回答失败: {str(e)}")


@router.get("/statistics")
async def get_interview_statistics(db: Session = Depends(get_db)):
    """获取面试统计信息（从数据库）"""
    try:
        # 总答题数
        total_answered = db.query(VoiceAnswer).count()
        
        # 平均分
        from sqlalchemy import func
        avg_score_result = db.query(func.avg(VoiceAnswer.quality_score)).scalar()
        avg_score = round(float(avg_score_result), 1) if avg_score_result else 0

        # 按分类统计
        questions = db.query(InterviewQuestion).all()
        category_map = {}
        for q in questions:
            cat = q.category
            if cat not in category_map:
                category_map[cat] = {"ids": [], "total": 0}
            category_map[cat]["ids"].append(q.id)
            category_map[cat]["total"] += 1

        category_stats = {}
        for cat, info in category_map.items():
            answered = db.query(VoiceAnswer).filter(
                VoiceAnswer.question_id.in_(info["ids"])
            ).count()
            cat_avg = db.query(func.avg(VoiceAnswer.quality_score)).filter(
                VoiceAnswer.question_id.in_(info["ids"])
            ).scalar()
            category_stats[cat] = {
                "total_questions": info["total"],
                "answered": answered,
                "avg_score": round(float(cat_avg), 1) if cat_avg else 0
            }

        # 最近答题记录
        recent_answers = db.query(VoiceAnswer).order_by(
            VoiceAnswer.created_at.desc()
        ).limit(10).all()

        recent_progress = []
        for a in recent_answers:
            recent_progress.append({
                "question_id": a.question_id,
                "score": a.quality_score,
                "created_at": a.created_at.isoformat() if a.created_at else None
            })

        stats = {
            "total_questions_answered": total_answered,
            "average_score": avg_score,
            "total_practice_time": total_answered * 180,  # 估算
            "category_stats": category_stats,
            "recent_progress": recent_progress,
        }

        return {
            "success": True,
            "statistics": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")


@router.get("/daily-question")
async def get_daily_question(db: Session = Depends(get_db)):
    """获取每日练习题目（从数据库）"""
    try:
        import hashlib
        today = datetime.now().strftime("%Y-%m-%d")
        seed = int(hashlib.md5(today.encode()).hexdigest()[:8], 16)

        total = db.query(InterviewQuestion).filter(InterviewQuestion.is_active == True).count()
        if total == 0:
            raise HTTPException(status_code=404, detail="暂无题目")

        offset = seed % total
        question = db.query(InterviewQuestion).filter(
            InterviewQuestion.is_active == True
        ).offset(offset).first()

        if not question:
            raise HTTPException(status_code=404, detail="暂无每日题目")

        return {
            "success": True,
            "daily_question": {
                "id": question.id,
                "title": question.title,
                "question": question.content,
                "category": question.category,
                "difficulty": question.difficulty,
                "tags": question.tags if isinstance(question.tags, list) else (eval(question.tags) if question.tags else []),
            },
            "date": today
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取每日题目失败: {str(e)}")
