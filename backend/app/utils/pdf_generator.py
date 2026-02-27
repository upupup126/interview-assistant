"""
PDF生成工具
用于生成简历PDF文件和预览HTML
"""

import os
import json
from typing import Dict, Any, Optional
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, Template


class PDFGenerator:
    """PDF生成器"""
    
    def __init__(self):
        self.templates_dir = "data/templates"
        self.exports_dir = "data/exports"
        self.static_dir = "data/static"
        
        # 确保目录存在
        os.makedirs(self.templates_dir, exist_ok=True)
        os.makedirs(self.exports_dir, exist_ok=True)
        os.makedirs(self.static_dir, exist_ok=True)
        
        # 初始化Jinja2环境
        self.jinja_env = Environment(
            loader=FileSystemLoader(self.templates_dir),
            autoescape=True
        )
        
        # 模板映射
        self.template_mapping = {
            1: "classic_template.html",
            2: "modern_template.html", 
            3: "creative_template.html",
            4: "tech_template.html"
        }
        
        # 创建默认模板
        self._create_default_templates()
    
    def _create_default_templates(self):
        """创建默认简历模板"""
        # 经典模板
        classic_template = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ resume.title }}</title>
    <style>
        body {
            font-family: 'SimSun', serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            color: #333;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        .header {
            text-align: center;
            border-bottom: 2px solid #333;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }
        .name {
            font-size: 28px;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .contact-info {
            font-size: 14px;
            color: #666;
        }
        .section {
            margin-bottom: 30px;
        }
        .section-title {
            font-size: 18px;
            font-weight: bold;
            border-bottom: 1px solid #ccc;
            padding-bottom: 5px;
            margin-bottom: 15px;
        }
        .item {
            margin-bottom: 15px;
        }
        .item-title {
            font-weight: bold;
            font-size: 16px;
        }
        .item-subtitle {
            color: #666;
            font-size: 14px;
            margin-bottom: 5px;
        }
        .item-description {
            font-size: 14px;
            line-height: 1.5;
        }
        .skills-list {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }
        .skill-tag {
            background: #f0f0f0;
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="name">{{ personal_info.name }}</div>
            <div class="contact-info">
                {% if personal_info.phone %}电话: {{ personal_info.phone }} | {% endif %}
                {% if personal_info.email %}邮箱: {{ personal_info.email }} | {% endif %}
                {% if personal_info.location %}地址: {{ personal_info.location }}{% endif %}
            </div>
        </div>
        
        {% if personal_info.summary %}
        <div class="section">
            <div class="section-title">个人简介</div>
            <div class="item-description">{{ personal_info.summary }}</div>
        </div>
        {% endif %}
        
        {% if education %}
        <div class="section">
            <div class="section-title">教育背景</div>
            {% for edu in education %}
            <div class="item">
                <div class="item-title">{{ edu.school }}</div>
                <div class="item-subtitle">{{ edu.degree }} - {{ edu.major }} ({{ edu.start_date }} - {{ edu.end_date }})</div>
                {% if edu.gpa %}<div class="item-description">GPA: {{ edu.gpa }}</div>{% endif %}
            </div>
            {% endfor %}
        </div>
        {% endif %}
        
        {% if work_experience %}
        <div class="section">
            <div class="section-title">工作经历</div>
            {% for exp in work_experience %}
            <div class="item">
                <div class="item-title">{{ exp.position }} - {{ exp.company }}</div>
                <div class="item-subtitle">{{ exp.start_date }} - {{ exp.end_date }}</div>
                <div class="item-description">{{ exp.description }}</div>
            </div>
            {% endfor %}
        </div>
        {% endif %}
        
        {% if projects %}
        <div class="section">
            <div class="section-title">项目经历</div>
            {% for project in projects %}
            <div class="item">
                <div class="item-title">{{ project.name }}</div>
                <div class="item-subtitle">{{ project.role }} ({{ project.start_date }} - {{ project.end_date }})</div>
                <div class="item-description">{{ project.description }}</div>
                {% if project.technologies %}
                <div class="item-description"><strong>技术栈:</strong> {{ project.technologies }}</div>
                {% endif %}
            </div>
            {% endfor %}
        </div>
        {% endif %}
        
        {% if skills %}
        <div class="section">
            <div class="section-title">技能特长</div>
            <div class="skills-list">
                {% for skill in skills %}
                <span class="skill-tag">{{ skill.name }} ({{ skill.level }})</span>
                {% endfor %}
            </div>
        </div>
        {% endif %}
    </div>
</body>
</html>
        """
        
        # 保存经典模板
        classic_path = os.path.join(self.templates_dir, "classic_template.html")
        if not os.path.exists(classic_path):
            with open(classic_path, 'w', encoding='utf-8') as f:
                f.write(classic_template)
        
        # 现代模板（简化版，实际项目中可以有更多样式）
        modern_template = classic_template.replace(
            "font-family: 'SimSun', serif;",
            "font-family: 'Microsoft YaHei', sans-serif;"
        ).replace(
            "border-bottom: 2px solid #333;",
            "border-bottom: 3px solid #007acc;"
        )
        
        modern_path = os.path.join(self.templates_dir, "modern_template.html")
        if not os.path.exists(modern_path):
            with open(modern_path, 'w', encoding='utf-8') as f:
                f.write(modern_template)
        
        # 创意模板和技术模板（使用相同的基础模板）
        for template_name in ["creative_template.html", "tech_template.html"]:
            template_path = os.path.join(self.templates_dir, template_name)
            if not os.path.exists(template_path):
                with open(template_path, 'w', encoding='utf-8') as f:
                    f.write(modern_template)
    
    async def generate_resume_pdf(self, resume, template_id: Optional[int] = None) -> str:
        """生成简历PDF文件"""
        try:
            # 获取模板
            template_id = template_id or resume.template_id or 1
            template_file = self.template_mapping.get(template_id, "classic_template.html")
            
            # 准备数据
            resume_data = self._prepare_resume_data(resume)
            
            # 渲染HTML
            template = self.jinja_env.get_template(template_file)
            html_content = template.render(**resume_data)
            
            # 生成PDF文件路径
            pdf_filename = f"resume_{resume.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            pdf_path = os.path.join(self.exports_dir, pdf_filename)
            
            # 这里应该使用真正的PDF生成库，如weasyprint或reportlab
            # 为了演示，我们先保存HTML文件
            html_path = pdf_path.replace('.pdf', '.html')
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # 模拟PDF生成（实际项目中应该使用专业的PDF库）
            try:
                # 尝试使用weasyprint（如果安装了的话）
                import weasyprint
                weasyprint.HTML(string=html_content).write_pdf(pdf_path)
            except ImportError:
                # 如果没有安装weasyprint，返回HTML路径
                return html_path
            
            return pdf_path
            
        except Exception as e:
            raise Exception(f"生成PDF失败: {str(e)}")
    
    async def generate_resume_preview(self, resume, template_id: Optional[int] = None) -> str:
        """生成简历预览HTML"""
        try:
            # 获取模板
            template_id = template_id or resume.template_id or 1
            template_file = self.template_mapping.get(template_id, "classic_template.html")
            
            # 准备数据
            resume_data = self._prepare_resume_data(resume)
            
            # 渲染HTML
            template = self.jinja_env.get_template(template_file)
            html_content = template.render(**resume_data)
            
            return html_content
            
        except Exception as e:
            raise Exception(f"生成预览失败: {str(e)}")
    
    def _prepare_resume_data(self, resume) -> Dict[str, Any]:
        """准备简历数据用于模板渲染"""
        try:
            # 解析JSON字段
            education = json.loads(resume.education) if resume.education else []
            work_experience = json.loads(resume.work_experience) if resume.work_experience else []
            projects = json.loads(resume.projects) if resume.projects else []
            skills = json.loads(resume.skills) if resume.skills else []
            
            return {
                "resume": resume,
                "personal_info": resume.personal_info,
                "education": education,
                "work_experience": work_experience,
                "projects": projects,
                "skills": skills
            }
        except Exception as e:
            raise Exception(f"准备简历数据失败: {str(e)}")
    
    def get_available_templates(self) -> list:
        """获取可用的模板列表"""
        templates = []
        for template_id, template_file in self.template_mapping.items():
            template_path = os.path.join(self.templates_dir, template_file)
            if os.path.exists(template_path):
                templates.append({
                    "id": template_id,
                    "name": template_file.replace("_template.html", "").replace("_", " ").title(),
                    "file": template_file
                })
        return templates
    
    def validate_template(self, template_id: int) -> bool:
        """验证模板是否存在"""
        template_file = self.template_mapping.get(template_id)
        if not template_file:
            return False
        
        template_path = os.path.join(self.templates_dir, template_file)
        return os.path.exists(template_path)