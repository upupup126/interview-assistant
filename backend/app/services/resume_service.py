"""
简历服务
处理简历相关的业务逻辑
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.models.resume import (
    Resume, PersonalInfo, Education, WorkExperience, Project, Skill,
    ResumeCreate, ResumeUpdate, ResumeResponse
)
from app.core.database import get_db

class ResumeService:
    """简历服务类"""
    
    @staticmethod
    async def create_resume(db: AsyncSession, resume_data: ResumeCreate) -> Resume:
        """创建新简历"""
        # 创建简历主记录
        resume = Resume(
            title=resume_data.title,
            template_id=resume_data.template_id,
            target_position=resume_data.target_position,
            target_company=resume_data.target_company,
            is_active=resume_data.is_active,
            version=resume_data.version
        )
        
        db.add(resume)
        await db.flush()  # 获取resume.id
        
        # 创建个人信息
        if resume_data.personal_info:
            personal_info = PersonalInfo(
                resume_id=resume.id,
                **resume_data.personal_info.model_dump()
            )
            db.add(personal_info)
        
        # 创建教育经历
        for edu_data in resume_data.educations:
            education = Education(
                resume_id=resume.id,
                **edu_data.model_dump()
            )
            db.add(education)
        
        # 创建工作经历
        for exp_data in resume_data.experiences:
            experience = WorkExperience(
                resume_id=resume.id,
                **exp_data.model_dump()
            )
            db.add(experience)
        
        # 创建项目经历
        for proj_data in resume_data.projects:
            project = Project(
                resume_id=resume.id,
                **proj_data.model_dump()
            )
            db.add(project)
        
        # 创建技能
        for skill_data in resume_data.skills:
            skill = Skill(
                resume_id=resume.id,
                **skill_data.model_dump()
            )
            db.add(skill)
        
        await db.commit()
        await db.refresh(resume)
        return resume
    
    @staticmethod
    async def get_resume(db: AsyncSession, resume_id: int) -> Optional[Resume]:
        """获取指定简历"""
        stmt = select(Resume).options(
            selectinload(Resume.personal_info),
            selectinload(Resume.educations),
            selectinload(Resume.experiences),
            selectinload(Resume.projects),
            selectinload(Resume.skills)
        ).where(Resume.id == resume_id)
        
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_resumes(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None
    ) -> List[Resume]:
        """获取简历列表"""
        stmt = select(Resume).options(
            selectinload(Resume.personal_info)
        )
        
        if is_active is not None:
            stmt = stmt.where(Resume.is_active == is_active)
        
        stmt = stmt.offset(skip).limit(limit).order_by(Resume.updated_at.desc())
        
        result = await db.execute(stmt)
        return result.scalars().all()
    
    @staticmethod
    async def update_resume(
        db: AsyncSession,
        resume_id: int,
        resume_data: ResumeUpdate
    ) -> Optional[Resume]:
        """更新简历"""
        # 更新简历基本信息
        update_data = resume_data.model_dump(exclude_unset=True)
        if update_data:
            stmt = update(Resume).where(Resume.id == resume_id).values(**update_data)
            await db.execute(stmt)
        
        await db.commit()
        return await ResumeService.get_resume(db, resume_id)
    
    @staticmethod
    async def delete_resume(db: AsyncSession, resume_id: int) -> bool:
        """删除简历"""
        # 软删除：设置is_active为False
        stmt = update(Resume).where(Resume.id == resume_id).values(is_active=False)
        result = await db.execute(stmt)
        await db.commit()
        return result.rowcount > 0
    
    @staticmethod
    async def duplicate_resume(db: AsyncSession, resume_id: int, new_title: str) -> Optional[Resume]:
        """复制简历"""
        original_resume = await ResumeService.get_resume(db, resume_id)
        if not original_resume:
            return None
        
        # 创建新简历
        new_resume = Resume(
            title=new_title,
            template_id=original_resume.template_id,
            target_position=original_resume.target_position,
            target_company=original_resume.target_company,
            version=1
        )
        
        db.add(new_resume)
        await db.flush()
        
        # 复制个人信息
        if original_resume.personal_info:
            new_personal_info = PersonalInfo(
                resume_id=new_resume.id,
                name=original_resume.personal_info.name,
                email=original_resume.personal_info.email,
                phone=original_resume.personal_info.phone,
                location=original_resume.personal_info.location,
                github=original_resume.personal_info.github,
                linkedin=original_resume.personal_info.linkedin,
                website=original_resume.personal_info.website,
                summary=original_resume.personal_info.summary
            )
            db.add(new_personal_info)
        
        # 复制教育经历
        for edu in original_resume.educations:
            new_education = Education(
                resume_id=new_resume.id,
                school=edu.school,
                degree=edu.degree,
                major=edu.major,
                start_date=edu.start_date,
                end_date=edu.end_date,
                gpa=edu.gpa,
                description=edu.description,
                order_index=edu.order_index
            )
            db.add(new_education)
        
        # 复制工作经历
        for exp in original_resume.experiences:
            new_experience = WorkExperience(
                resume_id=new_resume.id,
                company=exp.company,
                position=exp.position,
                location=exp.location,
                start_date=exp.start_date,
                end_date=exp.end_date,
                is_current=exp.is_current,
                description=exp.description,
                achievements=exp.achievements,
                order_index=exp.order_index
            )
            db.add(new_experience)
        
        # 复制项目经历
        for proj in original_resume.projects:
            new_project = Project(
                resume_id=new_resume.id,
                name=proj.name,
                role=proj.role,
                start_date=proj.start_date,
                end_date=proj.end_date,
                description=proj.description,
                technologies=proj.technologies,
                github_url=proj.github_url,
                demo_url=proj.demo_url,
                achievements=proj.achievements,
                order_index=proj.order_index
            )
            db.add(new_project)
        
        # 复制技能
        for skill in original_resume.skills:
            new_skill = Skill(
                resume_id=new_resume.id,
                category=skill.category,
                name=skill.name,
                level=skill.level,
                description=skill.description,
                order_index=skill.order_index
            )
            db.add(new_skill)
        
        await db.commit()
        await db.refresh(new_resume)
        return new_resume
    
    @staticmethod
    async def get_resume_versions(db: AsyncSession, base_title: str) -> List[Resume]:
        """获取简历的所有版本"""
        stmt = select(Resume).where(
            Resume.title.like(f"{base_title}%")
        ).order_by(Resume.version.desc())
        
        result = await db.execute(stmt)
        return result.scalars().all()
    
    @staticmethod
    async def update_personal_info(
        db: AsyncSession,
        resume_id: int,
        personal_info_data: Dict[str, Any]
    ) -> Optional[PersonalInfo]:
        """更新个人信息"""
        stmt = select(PersonalInfo).where(PersonalInfo.resume_id == resume_id)
        result = await db.execute(stmt)
        personal_info = result.scalar_one_or_none()
        
        if personal_info:
            # 更新现有记录
            for key, value in personal_info_data.items():
                if hasattr(personal_info, key):
                    setattr(personal_info, key, value)
        else:
            # 创建新记录
            personal_info = PersonalInfo(
                resume_id=resume_id,
                **personal_info_data
            )
            db.add(personal_info)
        
        await db.commit()
        await db.refresh(personal_info)
        return personal_info
    
    @staticmethod
    async def add_education(
        db: AsyncSession,
        resume_id: int,
        education_data: Dict[str, Any]
    ) -> Education:
        """添加教育经历"""
        education = Education(
            resume_id=resume_id,
            **education_data
        )
        db.add(education)
        await db.commit()
        await db.refresh(education)
        return education
    
    @staticmethod
    async def update_education(
        db: AsyncSession,
        education_id: int,
        education_data: Dict[str, Any]
    ) -> Optional[Education]:
        """更新教育经历"""
        stmt = update(Education).where(Education.id == education_id).values(**education_data)
        await db.execute(stmt)
        await db.commit()
        
        # 返回更新后的记录
        result = await db.execute(select(Education).where(Education.id == education_id))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def delete_education(db: AsyncSession, education_id: int) -> bool:
        """删除教育经历"""
        stmt = delete(Education).where(Education.id == education_id)
        result = await db.execute(stmt)
        await db.commit()
        return result.rowcount > 0