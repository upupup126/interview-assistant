"""
简历管理API路由
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import json
import os
from datetime import datetime

from ..core.database import get_db
from ..models.resume import (
    Resume, ResumeCreate, ResumeUpdate, PersonalInfo, 
    Education, WorkExperience, Project, Skill
)
from ..services.ai_service import AIService
from ..utils.pdf_generator import PDFGenerator
from ..utils.file_handler import FileHandler

router = APIRouter(prefix="/resumes", tags=["resumes"])

# 服务实例
ai_service = AIService()
pdf_generator = PDFGenerator()
file_handler = FileHandler()


@router.get("/")
async def get_resumes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取简历列表"""
    try:
        resumes = db.query(Resume).offset(skip).limit(limit).all()
        return {"resumes": resumes, "total": len(resumes)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取简历列表失败: {str(e)}")


@router.post("/", response_model=Resume)
async def create_resume(
    resume_data: ResumeCreate,
    db: Session = Depends(get_db)
):
    """创建新简历"""
    try:
        # 创建简历记录
        resume = Resume(
            title=resume_data.title,
            template_id=resume_data.template_id,
            personal_info=resume_data.personal_info.dict(),
            education=json.dumps([edu.dict() for edu in resume_data.education], ensure_ascii=False),
            work_experience=json.dumps([exp.dict() for exp in resume_data.work_experience], ensure_ascii=False),
            projects=json.dumps([proj.dict() for proj in resume_data.projects], ensure_ascii=False),
            skills=json.dumps([skill.dict() for skill in resume_data.skills], ensure_ascii=False),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(resume)
        db.commit()
        db.refresh(resume)
        
        return resume
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"创建简历失败: {str(e)}")


@router.get("/{resume_id}")
async def get_resume(resume_id: int, db: Session = Depends(get_db)):
    """获取指定简历详情"""
    try:
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        if not resume:
            raise HTTPException(status_code=404, detail="简历不存在")
        
        # 解析JSON字段
        resume_dict = {
            "id": resume.id,
            "title": resume.title,
            "template_id": resume.template_id,
            "personal_info": resume.personal_info,
            "education": json.loads(resume.education) if resume.education else [],
            "work_experience": json.loads(resume.work_experience) if resume.work_experience else [],
            "projects": json.loads(resume.projects) if resume.projects else [],
            "skills": json.loads(resume.skills) if resume.skills else [],
            "created_at": resume.created_at,
            "updated_at": resume.updated_at
        }
        
        return resume_dict
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取简历详情失败: {str(e)}")


@router.put("/{resume_id}")
async def update_resume(
    resume_id: int,
    resume_data: ResumeUpdate,
    db: Session = Depends(get_db)
):
    """更新简历"""
    try:
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        if not resume:
            raise HTTPException(status_code=404, detail="简历不存在")
        
        # 更新字段
        update_data = resume_data.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            if field in ["education", "work_experience", "projects", "skills"]:
                # JSON字段需要序列化
                if value is not None:
                    setattr(resume, field, json.dumps([item.dict() if hasattr(item, 'dict') else item for item in value], ensure_ascii=False))
            elif field == "personal_info":
                if value is not None:
                    setattr(resume, field, value.dict() if hasattr(value, 'dict') else value)
            else:
                setattr(resume, field, value)
        
        resume.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(resume)
        
        return resume
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"更新简历失败: {str(e)}")


@router.delete("/{resume_id}")
async def delete_resume(resume_id: int, db: Session = Depends(get_db)):
    """删除简历"""
    try:
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        if not resume:
            raise HTTPException(status_code=404, detail="简历不存在")
        
        db.delete(resume)
        db.commit()
        
        return {"message": "简历删除成功"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"删除简历失败: {str(e)}")


@router.post("/{resume_id}/optimize")
async def optimize_resume(
    resume_id: int,
    job_description: str = Form(...),
    db: Session = Depends(get_db)
):
    """AI优化简历"""
    try:
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        if not resume:
            raise HTTPException(status_code=404, detail="简历不存在")
        
        # 使用AI服务优化简历
        optimization_result = await ai_service.optimize_resume(resume_id, job_description)
        
        return {
            "success": True,
            "optimization": optimization_result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI优化简历失败: {str(e)}")


@router.post("/{resume_id}/export/pdf")
async def export_resume_pdf(
    resume_id: int,
    db: Session = Depends(get_db)
):
    """导出简历为PDF"""
    try:
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        if not resume:
            raise HTTPException(status_code=404, detail="简历不存在")
        
        # 生成PDF
        pdf_path = await pdf_generator.generate_resume_pdf(resume)
        
        return {
            "success": True,
            "pdf_path": pdf_path,
            "download_url": f"/api/resumes/{resume_id}/download/pdf"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出PDF失败: {str(e)}")


@router.get("/{resume_id}/download/pdf")
async def download_resume_pdf(
    resume_id: int,
    db: Session = Depends(get_db)
):
    """下载简历PDF"""
    try:
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        if not resume:
            raise HTTPException(status_code=404, detail="简历不存在")
        
        # 获取PDF文件路径
        pdf_path = f"data/exports/resume_{resume_id}.pdf"
        
        if not os.path.exists(pdf_path):
            # 如果PDF不存在，重新生成
            pdf_path = await pdf_generator.generate_resume_pdf(resume)
        
        from fastapi.responses import FileResponse
        return FileResponse(
            path=pdf_path,
            filename=f"{resume.title}.pdf",
            media_type="application/pdf"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"下载PDF失败: {str(e)}")


@router.get("/templates")
async def get_resume_templates():
    """获取简历模板列表"""
    try:
        templates = [
            {
                "id": 1,
                "name": "经典模板",
                "description": "简洁大方的经典简历模板",
                "preview_image": "/static/templates/classic_preview.png",
                "category": "经典"
            },
            {
                "id": 2,
                "name": "现代模板",
                "description": "现代化设计的简历模板",
                "preview_image": "/static/templates/modern_preview.png",
                "category": "现代"
            },
            {
                "id": 3,
                "name": "创意模板",
                "description": "富有创意的简历模板",
                "preview_image": "/static/templates/creative_preview.png",
                "category": "创意"
            },
            {
                "id": 4,
                "name": "技术模板",
                "description": "专为技术人员设计的简历模板",
                "preview_image": "/static/templates/tech_preview.png",
                "category": "技术"
            }
        ]
        
        return {"templates": templates}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取模板列表失败: {str(e)}")


@router.post("/{resume_id}/clone")
async def clone_resume(
    resume_id: int,
    new_title: str = Form(...),
    db: Session = Depends(get_db)
):
    """克隆简历"""
    try:
        original_resume = db.query(Resume).filter(Resume.id == resume_id).first()
        if not original_resume:
            raise HTTPException(status_code=404, detail="原简历不存在")
        
        # 创建新简历
        cloned_resume = Resume(
            title=new_title,
            template_id=original_resume.template_id,
            personal_info=original_resume.personal_info,
            education=original_resume.education,
            work_experience=original_resume.work_experience,
            projects=original_resume.projects,
            skills=original_resume.skills,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(cloned_resume)
        db.commit()
        db.refresh(cloned_resume)
        
        return cloned_resume
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"克隆简历失败: {str(e)}")


@router.post("/import")
async def import_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """导入简历文件"""
    try:
        # 检查文件类型
        allowed_types = ["application/pdf", "application/msword", 
                        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
        
        if file.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="不支持的文件类型")
        
        # 保存上传的文件
        file_path = await file_handler.save_uploaded_file(file, "imports")
        
        # 解析简历内容（这里可以集成OCR或文档解析服务）
        parsed_content = await file_handler.parse_resume_file(file_path)
        
        return {
            "success": True,
            "parsed_content": parsed_content,
            "message": "简历导入成功，请检查并完善信息"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导入简历失败: {str(e)}")


@router.get("/{resume_id}/versions")
async def get_resume_versions(
    resume_id: int,
    db: Session = Depends(get_db)
):
    """获取简历版本历史"""
    try:
        # 这里可以实现版本控制功能
        # 暂时返回模拟数据
        versions = [
            {
                "version": "1.0",
                "created_at": "2024-01-01T10:00:00",
                "description": "初始版本",
                "changes": ["创建简历"]
            },
            {
                "version": "1.1",
                "created_at": "2024-01-02T15:30:00",
                "description": "更新工作经历",
                "changes": ["添加新的工作经历", "更新技能列表"]
            }
        ]
        
        return {"versions": versions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取版本历史失败: {str(e)}")


@router.post("/{resume_id}/preview")
async def preview_resume(
    resume_id: int,
    template_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """预览简历"""
    try:
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        if not resume:
            raise HTTPException(status_code=404, detail="简历不存在")
        
        # 使用指定模板或当前模板生成预览
        preview_template_id = template_id or resume.template_id
        
        # 生成预览HTML
        preview_html = await pdf_generator.generate_resume_preview(resume, preview_template_id)
        
        return {
            "success": True,
            "preview_html": preview_html
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"预览简历失败: {str(e)}")