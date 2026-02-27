"""
面试练习API路由
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional, List
import json
from datetime import datetime

from ..services.ai_service import AIService
from ..services.voice_service import VoiceService
from ..models.interview import (
    InterviewQuestion, InterviewSession, VoiceAnswer,
    QuestionCategory, AnalysisResult
)

router = APIRouter(prefix="/interview", tags=["interview"])

# 服务实例
ai_service = AIService()
voice_service = VoiceService()


@router.get("/questions")
async def get_questions(
    category: Optional[QuestionCategory] = None,
    difficulty: Optional[str] = None,
    limit: int = 50
):
    """获取面试题目列表"""
    try:
        # 模拟题目数据
        mock_questions = {
            "algorithms": [
                {
                    "id": 1,
                    "question": "请解释时间复杂度和空间复杂度的概念，并举例说明",
                    "category": "algorithms",
                    "difficulty": "中等",
                    "tags": ["算法基础", "复杂度分析"],
                    "reference_answer": "时间复杂度描述算法执行时间与输入规模的关系..."
                },
                {
                    "id": 2,
                    "question": "什么是哈希表？它的优缺点是什么？",
                    "category": "algorithms",
                    "difficulty": "简单",
                    "tags": ["数据结构", "哈希表"],
                    "reference_answer": "哈希表是一种根据关键码值直接进行访问的数据结构..."
                },
                {
                    "id": 3,
                    "question": "请描述快速排序的原理和实现，分析其时间复杂度",
                    "category": "algorithms",
                    "difficulty": "中等",
                    "tags": ["排序算法", "分治法"],
                    "reference_answer": "快速排序是一种分治算法，基本思想是选择一个基准元素..."
                },
                {
                    "id": 4,
                    "question": "什么是动态规划？请举例说明动态规划的应用",
                    "category": "algorithms",
                    "difficulty": "困难",
                    "tags": ["动态规划", "算法设计"],
                    "reference_answer": "动态规划是一种算法设计技术，用于解决具有重叠子问题的优化问题..."
                },
                {
                    "id": 5,
                    "question": "二叉树的遍历方式有哪些？请分别说明其特点",
                    "category": "algorithms",
                    "difficulty": "简单",
                    "tags": ["二叉树", "遍历算法"],
                    "reference_answer": "二叉树的遍历主要有前序、中序、后序和层序遍历..."
                }
            ],
            "os": [
                {
                    "id": 6,
                    "question": "进程和线程的区别是什么？各自的优缺点？",
                    "category": "os",
                    "difficulty": "中等",
                    "tags": ["进程", "线程", "并发"],
                    "reference_answer": "进程是系统进行资源分配和调度的基本单位..."
                },
                {
                    "id": 7,
                    "question": "什么是死锁？产生死锁的条件是什么？如何避免死锁？",
                    "category": "os",
                    "difficulty": "困难",
                    "tags": ["死锁", "同步", "资源管理"],
                    "reference_answer": "死锁是指两个或多个进程在执行过程中因争夺资源而造成的相互等待现象..."
                },
                {
                    "id": 8,
                    "question": "虚拟内存的作用是什么？它是如何工作的？",
                    "category": "os",
                    "difficulty": "中等",
                    "tags": ["内存管理", "虚拟内存"],
                    "reference_answer": "虚拟内存是计算机系统内存管理的一种技术..."
                },
                {
                    "id": 9,
                    "question": "CPU调度算法有哪些？请比较它们的优缺点",
                    "category": "os",
                    "difficulty": "中等",
                    "tags": ["CPU调度", "调度算法"],
                    "reference_answer": "常见的CPU调度算法包括先来先服务、短作业优先..."
                },
                {
                    "id": 10,
                    "question": "什么是系统调用？它的作用和实现原理是什么？",
                    "category": "os",
                    "difficulty": "简单",
                    "tags": ["系统调用", "内核"],
                    "reference_answer": "系统调用是操作系统提供给应用程序的编程接口..."
                }
            ],
            "network": [
                {
                    "id": 11,
                    "question": "TCP和UDP的区别是什么？分别适用于什么场景？",
                    "category": "network",
                    "difficulty": "中等",
                    "tags": ["TCP", "UDP", "传输层"],
                    "reference_answer": "TCP是面向连接的可靠传输协议，UDP是无连接的不可靠传输协议..."
                },
                {
                    "id": 12,
                    "question": "HTTP和HTTPS的区别？HTTPS的工作原理是什么？",
                    "category": "network",
                    "difficulty": "简单",
                    "tags": ["HTTP", "HTTPS", "安全"],
                    "reference_answer": "HTTP是超文本传输协议，HTTPS是HTTP的安全版本..."
                },
                {
                    "id": 13,
                    "question": "什么是三次握手和四次挥手？为什么需要这样设计？",
                    "category": "network",
                    "difficulty": "中等",
                    "tags": ["TCP", "连接管理"],
                    "reference_answer": "三次握手是TCP建立连接的过程，四次挥手是TCP断开连接的过程..."
                },
                {
                    "id": 14,
                    "question": "OSI七层模型是什么？每层的主要功能是什么？",
                    "category": "network",
                    "difficulty": "中等",
                    "tags": ["OSI模型", "网络分层"],
                    "reference_answer": "OSI七层模型是网络通信的理论模型，从下到上分别是..."
                },
                {
                    "id": 15,
                    "question": "什么是DNS？它的工作原理和解析过程是什么？",
                    "category": "network",
                    "difficulty": "简单",
                    "tags": ["DNS", "域名解析"],
                    "reference_answer": "DNS是域名系统，用于将域名转换为IP地址..."
                }
            ]
        }
        
        # 根据分类筛选题目
        if category:
            questions = mock_questions.get(category.value, [])
        else:
            questions = []
            for cat_questions in mock_questions.values():
                questions.extend(cat_questions)
        
        # 根据难度筛选
        if difficulty:
            questions = [q for q in questions if q["difficulty"] == difficulty]
        
        # 限制数量
        questions = questions[:limit]
        
        return {
            "success": True,
            "questions": questions,
            "total": len(questions)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取题目失败: {str(e)}")


@router.post("/analyze-answer")
async def analyze_answer(
    question_id: int = Form(...),
    answer_text: str = Form(...),
    audio_file: Optional[UploadFile] = File(None)
):
    """分析回答（文字或语音）"""
    try:
        analysis_result = {
            "question_id": question_id,
            "answer_text": answer_text,
            "analysis": {
                "content_score": 85,
                "logic_score": 78,
                "accuracy_score": 92,
                "overall_score": 85,
                "strengths": [
                    "回答涵盖了问题的主要方面",
                    "技术概念理解准确",
                    "表述专业"
                ],
                "improvements": [
                    "可以在开头简要概括要点",
                    "举例说明可以让概念更容易理解",
                    "结尾可以简单总结"
                ],
                "detailed_feedback": "这是一个很好的回答！回答展现了对相关技术概念的深入理解。建议在表达时可以更加结构化，先概括后详述，这样会让回答更有条理。"
            },
            "voice_analysis": None,
            "created_at": datetime.utcnow().isoformat()
        }
        
        # 如果有音频文件，进行语音分析
        if audio_file:
            voice_analysis = await voice_service.analyze_speech_quality(audio_file)
            analysis_result["voice_analysis"] = voice_analysis
        
        return {
            "success": True,
            "analysis": analysis_result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析回答失败: {str(e)}")


@router.get("/statistics")
async def get_interview_statistics():
    """获取面试统计信息"""
    try:
        stats = {
            "total_questions_answered": 45,
            "average_score": 82.3,
            "total_practice_time": 3600,  # 秒
            "category_stats": {
                "algorithms": {"answered": 15, "avg_score": 85.2},
                "os": {"answered": 12, "avg_score": 78.5},
                "network": {"answered": 10, "avg_score": 83.1},
                "database": {"answered": 8, "avg_score": 80.7}
            },
            "recent_progress": [
                {"date": "2024-01-15", "questions": 5, "avg_score": 85},
                {"date": "2024-01-14", "questions": 3, "avg_score": 78},
                {"date": "2024-01-13", "questions": 4, "avg_score": 82},
                {"date": "2024-01-12", "questions": 2, "avg_score": 88},
                {"date": "2024-01-11", "questions": 6, "avg_score": 79}
            ],
            "improvement_areas": [
                {"category": "system_design", "score": 65, "priority": "high"},
                {"category": "database", "score": 72, "priority": "medium"},
                {"category": "network", "score": 78, "priority": "low"}
            ]
        }
        
        return {
            "success": True,
            "statistics": stats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")


@router.get("/daily-question")
async def get_daily_question():
    """获取每日练习题目"""
    try:
        # 根据日期选择题目
        import hashlib
        today = datetime.now().strftime("%Y-%m-%d")
        seed = int(hashlib.md5(today.encode()).hexdigest()[:8], 16)
        
        questions = [
            {
                "id": 1,
                "question": "请解释时间复杂度和空间复杂度的概念",
                "category": "algorithms",
                "difficulty": "中等"
            },
            {
                "id": 6,
                "question": "进程和线程的区别是什么？",
                "category": "os",
                "difficulty": "中等"
            },
            {
                "id": 11,
                "question": "TCP和UDP的区别是什么？",
                "category": "network",
                "difficulty": "中等"
            }
        ]
        
        daily_question = questions[seed % len(questions)]
        
        return {
            "success": True,
            "daily_question": daily_question,
            "date": today
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取每日题目失败: {str(e)}")