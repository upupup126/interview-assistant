"""
简历管理API路由 - 使用数据库真实数据
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional
import json
from datetime import datetime

from ..core.database import get_db
from ..models.resume import (
    Resume, PersonalInfo, Education, WorkExperience, Project, Skill,
    ResumeCreate, ResumeUpdate
)
from ..services.ai_service import AIService
from ..utils.pdf_generator import PDFGenerator
from ..utils.file_handler import FileHandler

router = APIRouter(prefix="/resumes", tags=["resumes"])

ai_service = AIService()
pdf_generator = PDFGenerator()
file_handler = FileHandler()


def serialize_resume(resume, db):
    """将Resume ORM对象序列化为字典"""
    personal_info = db.query(PersonalInfo).filter(PersonalInfo.resume_id == resume.id).first()
    educations = db.query(Education).filter(Education.resume_id == resume.id).all()
    experiences = db.query(WorkExperience).filter(WorkExperience.resume_id == resume.id).all()
    projects = db.query(Project).filter(Project.resume_id == resume.id).all()
    skills = db.query(Skill).filter(Skill.resume_id == resume.id).all()

    return {
        "id": resume.id,
        "title": resume.title,
        "template_id": resume.template_id,
        "target_position": resume.target_position,
        "target_company": resume.target_company,
        "is_active": resume.is_active,
        "version": resume.version,
        "personal_info": {
            "name": personal_info.name,
            "email": personal_info.email,
            "phone": personal_info.phone,
            "location": personal_info.location,
            "github": personal_info.github,
            "summary": personal_info.summary,
        } if personal_info else None,
        "educations": [{
            "school": e.school, "degree": e.degree, "major": e.major,
            "start_date": e.start_date.isoformat() if e.start_date else None,
            "end_date": e.end_date.isoformat() if e.end_date else None,
            "gpa": e.gpa, "description": e.description,
        } for e in educations],
        "experiences": [{
            "company": e.company, "position": e.position, "location": e.location,
            "start_date": e.start_date.isoformat() if e.start_date else None,
            "end_date": e.end_date.isoformat() if e.end_date else None,
            "is_current": e.is_current, "description": e.description,
        } for e in experiences],
        "projects": [{
            "name": p.name, "role": p.role, "description": p.description,
            "technologies": p.technologies,
        } for p in projects],
        "skills": [{
            "category": s.category, "name": s.name, "level": s.level,
        } for s in skills],
        "created_at": resume.created_at.isoformat() if resume.created_at else None,
        "updated_at": resume.updated_at.isoformat() if resume.updated_at else None,
    }


@router.get("/")
async def get_resumes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取简历列表"""
    try:
        resumes = db.query(Resume).offset(skip).limit(limit).all()
        result = [serialize_resume(r, db) for r in resumes]
        return {"resumes": result, "total": len(result)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取简历列表失败: {str(e)}")


@router.post("/")
async def create_resume(resume_data: dict, db: Session = Depends(get_db)):
    """创建新简历"""
    try:
        resume = Resume(
            title=resume_data.get("title", "未命名简历"),
            template_id=resume_data.get("template_id", "default"),
            target_position=resume_data.get("target_position"),
            target_company=resume_data.get("target_company"),
            is_active=True,
            version=1,
        )
        db.add(resume)
        db.flush()

        # 创建个人信息
        pi = resume_data.get("personal_info")
        if pi and isinstance(pi, dict):
            personal_info = PersonalInfo(
                resume_id=resume.id,
                name=pi.get("name", ""),
                email=pi.get("email"),
                phone=pi.get("phone"),
                location=pi.get("location"),
                github=pi.get("github"),
                summary=pi.get("summary"),
            )
            db.add(personal_info)

        # 创建教育经历
        for edu in resume_data.get("educations", []):
            if isinstance(edu, dict):
                db.add(Education(
                    resume_id=resume.id,
                    school=edu.get("school", ""),
                    degree=edu.get("degree"),
                    major=edu.get("major"),
                    gpa=edu.get("gpa"),
                    description=edu.get("description"),
                ))

        # 创建工作经历
        for exp in resume_data.get("experiences", []):
            if isinstance(exp, dict):
                db.add(WorkExperience(
                    resume_id=resume.id,
                    company=exp.get("company", ""),
                    position=exp.get("position", ""),
                    location=exp.get("location"),
                    is_current=exp.get("is_current", False),
                    description=exp.get("description"),
                ))

        # 创建项目经历
        for proj in resume_data.get("projects", []):
            if isinstance(proj, dict):
                db.add(Project(
                    resume_id=resume.id,
                    name=proj.get("name", ""),
                    role=proj.get("role"),
                    description=proj.get("description"),
                    technologies=proj.get("technologies"),
                ))

        # 创建技能
        for skill in resume_data.get("skills", []):
            if isinstance(skill, dict):
                db.add(Skill(
                    resume_id=resume.id,
                    category=skill.get("category", ""),
                    name=skill.get("name", ""),
                    level=skill.get("level"),
                ))

        db.commit()
        db.refresh(resume)
        return serialize_resume(resume, db)
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
        return serialize_resume(resume, db)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取简历详情失败: {str(e)}")


@router.put("/{resume_id}")
async def update_resume(resume_id: int, resume_data: dict, db: Session = Depends(get_db)):
    """更新简历"""
    try:
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        if not resume:
            raise HTTPException(status_code=404, detail="简历不存在")

        # 更新基本字段
        for field in ["title", "template_id", "target_position", "target_company", "is_active"]:
            if field in resume_data:
                setattr(resume, field, resume_data[field])

        resume.updated_at = datetime.utcnow()
        resume.version = (resume.version or 1) + 1

        # 更新个人信息
        pi = resume_data.get("personal_info")
        if pi and isinstance(pi, dict):
            personal_info = db.query(PersonalInfo).filter(PersonalInfo.resume_id == resume_id).first()
            if personal_info:
                for k, v in pi.items():
                    if hasattr(personal_info, k):
                        setattr(personal_info, k, v)
            else:
                db.add(PersonalInfo(resume_id=resume_id, name=pi.get("name", ""), **{k: v for k, v in pi.items() if k != "name"}))

        db.commit()
        db.refresh(resume)
        return serialize_resume(resume, db)
    except HTTPException:
        raise
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

        # 删除关联数据
        db.query(PersonalInfo).filter(PersonalInfo.resume_id == resume_id).delete()
        db.query(Education).filter(Education.resume_id == resume_id).delete()
        db.query(WorkExperience).filter(WorkExperience.resume_id == resume_id).delete()
        db.query(Project).filter(Project.resume_id == resume_id).delete()
        db.query(Skill).filter(Skill.resume_id == resume_id).delete()
        db.delete(resume)
        db.commit()

        return {"message": "简历删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"删除简历失败: {str(e)}")


@router.post("/{resume_id}/optimize")
async def optimize_resume(resume_id: int, job_description: str = Form(...), db: Session = Depends(get_db)):
    """AI优化简历"""
    try:
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        if not resume:
            raise HTTPException(status_code=404, detail="简历不存在")

        optimization_result = await ai_service.optimize_resume(resume_id, job_description)
        return {"success": True, "optimization": optimization_result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI优化简历失败: {str(e)}")


@router.post("/{resume_id}/export/pdf")
async def export_resume_pdf(resume_id: int, db: Session = Depends(get_db)):
    """导出简历为PDF"""
    try:
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        if not resume:
            raise HTTPException(status_code=404, detail="简历不存在")

        pdf_path = await pdf_generator.generate_resume_pdf(resume)
        return {"success": True, "pdf_path": pdf_path, "download_url": f"/api/resumes/{resume_id}/download/pdf"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出PDF失败: {str(e)}")


@router.get("/templates/list")
async def get_resume_templates():
    """获取简历模板列表"""
    templates = [
        {"id": 1, "name": "经典模板", "description": "简洁大方的经典简历模板", "category": "经典"},
        {"id": 2, "name": "现代模板", "description": "现代化设计的简历模板", "category": "现代"},
        {"id": 3, "name": "创意模板", "description": "富有创意的简历模板", "category": "创意"},
        {"id": 4, "name": "技术模板", "description": "专为技术人员设计的简历模板", "category": "技术"},
    ]
    return {"templates": templates}


@router.post("/{resume_id}/clone")
async def clone_resume(resume_id: int, new_title: str = Form(...), db: Session = Depends(get_db)):
    """克隆简历"""
    try:
        original = db.query(Resume).filter(Resume.id == resume_id).first()
        if not original:
            raise HTTPException(status_code=404, detail="原简历不存在")

        cloned = Resume(
            title=new_title,
            template_id=original.template_id,
            target_position=original.target_position,
            target_company=original.target_company,
            is_active=True,
            version=1,
        )
        db.add(cloned)
        db.flush()

        # 复制个人信息
        pi = db.query(PersonalInfo).filter(PersonalInfo.resume_id == resume_id).first()
        if pi:
            db.add(PersonalInfo(
                resume_id=cloned.id, name=pi.name, email=pi.email,
                phone=pi.phone, location=pi.location, github=pi.github, summary=pi.summary,
            ))

        db.commit()
        db.refresh(cloned)
        return serialize_resume(cloned, db)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"克隆简历失败: {str(e)}")


@router.get("/{resume_id}/versions")
async def get_resume_versions(resume_id: int, db: Session = Depends(get_db)):
    """获取简历版本历史"""
    try:
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        if not resume:
            raise HTTPException(status_code=404, detail="简历不存在")

        versions = [{
            "version": str(resume.version or 1),
            "created_at": resume.created_at.isoformat() if resume.created_at else None,
            "updated_at": resume.updated_at.isoformat() if resume.updated_at else None,
            "description": f"版本 {resume.version or 1}",
        }]
        return {"versions": versions}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取版本历史失败: {str(e)}")


@router.post("/{resume_id}/preview")
async def preview_resume(resume_id: int, template_id: Optional[int] = None, db: Session = Depends(get_db)):
    """预览简历"""
    try:
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        if not resume:
            raise HTTPException(status_code=404, detail="简历不存在")

        preview_html = await pdf_generator.generate_resume_preview(resume, template_id or resume.template_id)
        return {"success": True, "preview_html": preview_html}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"预览简历失败: {str(e)}")
