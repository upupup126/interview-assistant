"""
文件处理工具
用于处理文件上传、解析和管理
"""

import os
import shutil
import uuid
from typing import Dict, Any, Optional
from datetime import datetime
from fastapi import UploadFile
import mimetypes


class FileHandler:
    """文件处理器"""
    
    def __init__(self):
        self.upload_dir = "data/uploads"
        self.temp_dir = "data/temp"
        self.allowed_extensions = {
            'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp'],
            'document': ['.pdf', '.doc', '.docx', '.txt', '.rtf'],
            'archive': ['.zip', '.rar', '.7z']
        }
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        
        # 确保目录存在
        os.makedirs(self.upload_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)
    
    async def save_uploaded_file(self, file: UploadFile, subfolder: str = "") -> str:
        """保存上传的文件"""
        try:
            # 验证文件
            self._validate_file(file)
            
            # 生成唯一文件名
            file_extension = os.path.splitext(file.filename)[1].lower()
            unique_filename = f"{uuid.uuid4().hex}{file_extension}"
            
            # 创建保存路径
            save_dir = os.path.join(self.upload_dir, subfolder)
            os.makedirs(save_dir, exist_ok=True)
            
            file_path = os.path.join(save_dir, unique_filename)
            
            # 保存文件
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            return file_path
            
        except Exception as e:
            raise Exception(f"保存文件失败: {str(e)}")
    
    def _validate_file(self, file: UploadFile):
        """验证文件"""
        # 检查文件大小
        if hasattr(file, 'size') and file.size > self.max_file_size:
            raise ValueError(f"文件大小超过限制 ({self.max_file_size / 1024 / 1024}MB)")
        
        # 检查文件扩展名
        if file.filename:
            file_extension = os.path.splitext(file.filename)[1].lower()
            
            allowed_extensions = []
            for ext_list in self.allowed_extensions.values():
                allowed_extensions.extend(ext_list)
            
            if file_extension not in allowed_extensions:
                raise ValueError(f"不支持的文件类型: {file_extension}")
        
        # 检查MIME类型
        if file.content_type:
            allowed_mime_types = [
                'image/jpeg', 'image/png', 'image/gif', 'image/bmp',
                'application/pdf', 'application/msword',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'text/plain', 'application/rtf',
                'application/zip', 'application/x-rar-compressed'
            ]
            
            if file.content_type not in allowed_mime_types:
                raise ValueError(f"不支持的MIME类型: {file.content_type}")
    
    async def parse_resume_file(self, file_path: str) -> Dict[str, Any]:
        """解析简历文件内容"""
        try:
            file_extension = os.path.splitext(file_path)[1].lower()
            
            if file_extension == '.pdf':
                return await self._parse_pdf_resume(file_path)
            elif file_extension in ['.doc', '.docx']:
                return await self._parse_word_resume(file_path)
            elif file_extension == '.txt':
                return await self._parse_text_resume(file_path)
            else:
                raise ValueError(f"不支持解析的文件类型: {file_extension}")
                
        except Exception as e:
            raise Exception(f"解析简历文件失败: {str(e)}")
    
    async def _parse_pdf_resume(self, file_path: str) -> Dict[str, Any]:
        """解析PDF简历"""
        try:
            # 这里应该使用PDF解析库，如PyPDF2或pdfplumber
            # 为了演示，返回模拟数据
            
            parsed_content = {
                "personal_info": {
                    "name": "从PDF解析的姓名",
                    "email": "example@email.com",
                    "phone": "138****8888",
                    "location": "北京市",
                    "summary": "从PDF文件中提取的个人简介..."
                },
                "education": [
                    {
                        "school": "某某大学",
                        "degree": "本科",
                        "major": "计算机科学与技术",
                        "start_date": "2018-09",
                        "end_date": "2022-06",
                        "gpa": "3.8"
                    }
                ],
                "work_experience": [
                    {
                        "company": "某某科技公司",
                        "position": "软件工程师",
                        "start_date": "2022-07",
                        "end_date": "至今",
                        "description": "从PDF中提取的工作描述..."
                    }
                ],
                "projects": [],
                "skills": [
                    {"name": "Python", "level": "熟练"},
                    {"name": "Java", "level": "熟练"},
                    {"name": "JavaScript", "level": "一般"}
                ],
                "parse_method": "PDF解析",
                "confidence": 0.8
            }
            
            return parsed_content
            
        except Exception as e:
            raise Exception(f"解析PDF文件失败: {str(e)}")
    
    async def _parse_word_resume(self, file_path: str) -> Dict[str, Any]:
        """解析Word简历"""
        try:
            # 这里应该使用python-docx库解析Word文档
            # 为了演示，返回模拟数据
            
            parsed_content = {
                "personal_info": {
                    "name": "从Word解析的姓名",
                    "email": "word@email.com",
                    "phone": "139****9999",
                    "location": "上海市",
                    "summary": "从Word文档中提取的个人简介..."
                },
                "education": [
                    {
                        "school": "某某大学",
                        "degree": "硕士",
                        "major": "软件工程",
                        "start_date": "2020-09",
                        "end_date": "2023-06",
                        "gpa": "3.9"
                    }
                ],
                "work_experience": [
                    {
                        "company": "某某互联网公司",
                        "position": "高级软件工程师",
                        "start_date": "2023-07",
                        "end_date": "至今",
                        "description": "从Word中提取的工作描述..."
                    }
                ],
                "projects": [
                    {
                        "name": "某某项目",
                        "role": "技术负责人",
                        "start_date": "2023-08",
                        "end_date": "2024-01",
                        "description": "项目描述...",
                        "technologies": "Python, Django, Redis"
                    }
                ],
                "skills": [
                    {"name": "Python", "level": "精通"},
                    {"name": "Django", "level": "熟练"},
                    {"name": "Redis", "level": "熟练"}
                ],
                "parse_method": "Word解析",
                "confidence": 0.85
            }
            
            return parsed_content
            
        except Exception as e:
            raise Exception(f"解析Word文件失败: {str(e)}")
    
    async def _parse_text_resume(self, file_path: str) -> Dict[str, Any]:
        """解析文本简历"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 简单的文本解析逻辑
            lines = content.split('\n')
            
            parsed_content = {
                "personal_info": {
                    "name": "从文本解析的姓名",
                    "email": "",
                    "phone": "",
                    "location": "",
                    "summary": content[:200] + "..." if len(content) > 200 else content
                },
                "education": [],
                "work_experience": [],
                "projects": [],
                "skills": [],
                "raw_content": content,
                "parse_method": "文本解析",
                "confidence": 0.6
            }
            
            # 简单的邮箱和电话提取
            import re
            
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            phone_pattern = r'1[3-9]\d{9}'
            
            emails = re.findall(email_pattern, content)
            phones = re.findall(phone_pattern, content)
            
            if emails:
                parsed_content["personal_info"]["email"] = emails[0]
            if phones:
                parsed_content["personal_info"]["phone"] = phones[0]
            
            return parsed_content
            
        except Exception as e:
            raise Exception(f"解析文本文件失败: {str(e)}")
    
    def delete_file(self, file_path: str) -> bool:
        """删除文件"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            print(f"删除文件失败: {str(e)}")
            return False
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """获取文件信息"""
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError("文件不存在")
            
            stat = os.stat(file_path)
            
            return {
                "path": file_path,
                "name": os.path.basename(file_path),
                "size": stat.st_size,
                "created_time": datetime.fromtimestamp(stat.st_ctime),
                "modified_time": datetime.fromtimestamp(stat.st_mtime),
                "mime_type": mimetypes.guess_type(file_path)[0]
            }
        except Exception as e:
            raise Exception(f"获取文件信息失败: {str(e)}")
    
    def cleanup_temp_files(self, older_than_hours: int = 24):
        """清理临时文件"""
        try:
            current_time = datetime.now()
            
            for filename in os.listdir(self.temp_dir):
                file_path = os.path.join(self.temp_dir, filename)
                
                if os.path.isfile(file_path):
                    file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                    
                    if (current_time - file_time).total_seconds() > older_than_hours * 3600:
                        os.remove(file_path)
                        
        except Exception as e:
            print(f"清理临时文件失败: {str(e)}")
    
    def create_backup(self, source_path: str, backup_dir: str = None) -> str:
        """创建文件备份"""
        try:
            if not backup_dir:
                backup_dir = os.path.join(self.upload_dir, "backups")
            
            os.makedirs(backup_dir, exist_ok=True)
            
            filename = os.path.basename(source_path)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"{timestamp}_{filename}"
            backup_path = os.path.join(backup_dir, backup_filename)
            
            shutil.copy2(source_path, backup_path)
            
            return backup_path
            
        except Exception as e:
            raise Exception(f"创建备份失败: {str(e)}")
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """获取存储统计信息"""
        try:
            def get_dir_size(path):
                total_size = 0
                file_count = 0
                
                if os.path.exists(path):
                    for dirpath, dirnames, filenames in os.walk(path):
                        for filename in filenames:
                            file_path = os.path.join(dirpath, filename)
                            total_size += os.path.getsize(file_path)
                            file_count += 1
                
                return total_size, file_count
            
            upload_size, upload_count = get_dir_size(self.upload_dir)
            temp_size, temp_count = get_dir_size(self.temp_dir)
            
            return {
                "upload_directory": {
                    "size_bytes": upload_size,
                    "size_mb": round(upload_size / 1024 / 1024, 2),
                    "file_count": upload_count
                },
                "temp_directory": {
                    "size_bytes": temp_size,
                    "size_mb": round(temp_size / 1024 / 1024, 2),
                    "file_count": temp_count
                },
                "total": {
                    "size_bytes": upload_size + temp_size,
                    "size_mb": round((upload_size + temp_size) / 1024 / 1024, 2),
                    "file_count": upload_count + temp_count
                }
            }
            
        except Exception as e:
            raise Exception(f"获取存储统计失败: {str(e)}")