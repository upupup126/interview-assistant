"""
API客户端服务
与后端API进行通信
"""

import requests
from typing import Dict, List, Optional, Any
import json
from pathlib import Path

class APIClient:
    """API客户端类"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """发送HTTP请求的通用方法"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.ConnectionError:
            return {"error": "无法连接到后端服务，请确保后端服务已启动"}
        except requests.exceptions.HTTPError as e:
            return {"error": f"HTTP错误: {e.response.status_code}"}
        except requests.exceptions.RequestException as e:
            return {"error": f"请求错误: {str(e)}"}
        except json.JSONDecodeError:
            return {"error": "响应格式错误"}
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """GET请求"""
        return self._make_request('GET', endpoint, params=params)
    
    def post(self, endpoint: str, data: Optional[Dict] = None, files: Optional[Dict] = None) -> Dict[str, Any]:
        """POST请求"""
        if files:
            # 文件上传时不设置Content-Type，让requests自动设置
            headers = {k: v for k, v in self.session.headers.items() if k.lower() != 'content-type'}
            return self._make_request('POST', endpoint, data=data, files=files, headers=headers)
        else:
            return self._make_request('POST', endpoint, json=data)
    
    def put(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """PUT请求"""
        return self._make_request('PUT', endpoint, json=data)
    
    def delete(self, endpoint: str) -> Dict[str, Any]:
        """DELETE请求"""
        return self._make_request('DELETE', endpoint)
    
    # 健康检查
    def health_check(self) -> Dict[str, Any]:
        """检查后端服务健康状态"""
        return self.get('/health')
    
    # 简历相关API
    def get_resumes(self) -> Dict[str, Any]:
        """获取简历列表"""
        return self.get('/api/v1/resume/')
    
    def create_resume(self, resume_data: Dict) -> Dict[str, Any]:
        """创建新简历"""
        return self.post('/api/v1/resume/', data=resume_data)
    
    def get_resume(self, resume_id: int) -> Dict[str, Any]:
        """获取指定简历"""
        return self.get(f'/api/v1/resume/{resume_id}')
    
    def update_resume(self, resume_id: int, resume_data: Dict) -> Dict[str, Any]:
        """更新简历"""
        return self.put(f'/api/v1/resume/{resume_id}', data=resume_data)
    
    def delete_resume(self, resume_id: int) -> Dict[str, Any]:
        """删除简历"""
        return self.delete(f'/api/v1/resume/{resume_id}')
    
    def optimize_resume(self, resume_id: int, job_description: str) -> Dict[str, Any]:
        """AI优化简历"""
        return self.post(f'/api/v1/resume/{resume_id}/optimize', 
                        data={'job_description': job_description})
    
    # LeetCode相关API
    def get_problems(self, category: Optional[str] = None, difficulty: Optional[str] = None) -> Dict[str, Any]:
        """获取题目列表"""
        params = {}
        if category:
            params['category'] = category
        if difficulty:
            params['difficulty'] = difficulty
        return self.get('/api/v1/leetcode/problems', params=params)
    
    def get_problem(self, problem_id: int) -> Dict[str, Any]:
        """获取题目详情"""
        return self.get(f'/api/v1/leetcode/problems/{problem_id}')
    
    def submit_solution(self, problem_id: int, solution_data: Dict) -> Dict[str, Any]:
        """提交题目解答"""
        return self.post(f'/api/v1/leetcode/problems/{problem_id}/submit', 
                        data=solution_data)
    
    def get_leetcode_progress(self) -> Dict[str, Any]:
        """获取刷题进度"""
        return self.get('/api/v1/leetcode/progress')
    
    def sync_leetcode_problems(self) -> Dict[str, Any]:
        """同步LeetCode题目"""
        return self.post('/api/v1/leetcode/sync')
    
    # 面试相关API
    def get_interview_questions(self, category: Optional[str] = None) -> Dict[str, Any]:
        """获取面试题目列表"""
        params = {'category': category} if category else {}
        return self.get('/api/v1/interview/questions', params=params)
    
    def get_interview_question(self, question_id: int) -> Dict[str, Any]:
        """获取面试题目详情"""
        return self.get(f'/api/v1/interview/questions/{question_id}')
    
    def submit_voice_answer(self, question_id: int, audio_file_path: str) -> Dict[str, Any]:
        """提交语音回答"""
        with open(audio_file_path, 'rb') as f:
            files = {'audio_file': f}
            return self.post(f'/api/v1/interview/questions/{question_id}/answer', files=files)
    
    def get_interview_sessions(self) -> Dict[str, Any]:
        """获取面试记录列表"""
        return self.get('/api/v1/interview/sessions')
    
    def create_interview_session(self, session_data: Dict) -> Dict[str, Any]:
        """创建面试记录"""
        return self.post('/api/v1/interview/sessions', data=session_data)
    
    def get_interview_session(self, session_id: int) -> Dict[str, Any]:
        """获取面试记录详情"""
        return self.get(f'/api/v1/interview/sessions/{session_id}')
    
    # 数据统计API
    def get_analytics_overview(self) -> Dict[str, Any]:
        """获取统计概览"""
        return self.get('/api/v1/analytics/overview')
    
    def get_leetcode_stats(self, days: int = 30) -> Dict[str, Any]:
        """获取LeetCode统计"""
        return self.get('/api/v1/analytics/leetcode-stats', params={'days': days})
    
    def get_interview_stats(self, days: int = 30) -> Dict[str, Any]:
        """获取面试练习统计"""
        return self.get('/api/v1/analytics/interview-stats', params={'days': days})
    
    def get_knowledge_mastery(self) -> Dict[str, Any]:
        """获取知识点掌握度"""
        return self.get('/api/v1/analytics/knowledge-mastery')
    
    def get_progress_trend(self, days: int = 30) -> Dict[str, Any]:
        """获取学习进度趋势"""
        return self.get('/api/v1/analytics/progress-trend', params={'days': days})