# 面试助手 API 接口文档

> **Base URL**: `http://<host>:8000`  
> **API 文档**: `http://<host>:8000/docs` (Swagger UI) | `http://<host>:8000/redoc` (ReDoc)  
> **框架**: FastAPI  
> **版本**: v1

---

## 目录

- [通用说明](#通用说明)
- [1. 基础接口](#1-基础接口)
- [2. 简历管理 API](#2-简历管理-api)
- [3. LeetCode 刷题 API](#3-leetcode-刷题-api)
- [4. 面试练习 API](#4-面试练习-api)
- [5. 数据统计分析 API](#5-数据统计分析-api)
- [数据模型定义](#数据模型定义)

---

## 通用说明

### 请求格式

- Content-Type: `application/json`（除文件上传接口外）
- 文件上传接口使用 `multipart/form-data`

### 响应格式

所有接口统一返回 JSON 格式，通用结构：

```json
{
  "success": true,
  "data": {},
  "message": "操作成功"
}
```

### 错误码

| HTTP 状态码 | 说明 |
|------------|------|
| 200 | 请求成功 |
| 404 | 资源不存在 |
| 422 | 请求参数验证失败 |
| 500 | 服务器内部错误 |

---

## 1. 基础接口

### 1.1 根路径

```
GET /
```

**响应示例**:
```json
{
  "message": "面试助手 API 服务",
  "version": "1.0.0",
  "docs": "/docs"
}
```

---

### 1.2 健康检查

```
GET /health
```

**响应示例**:
```json
{
  "status": "healthy",
  "service": "interview-assistant-api"
}
```

---

## 2. 简历管理 API

**前缀**: `/api/v1/resume/resumes`

### 2.1 获取简历列表

```
GET /api/v1/resume/resumes/
```

**Query 参数**:

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| skip | int | 否 | 0 | 跳过条数 |
| limit | int | 否 | 100 | 返回条数上限 |

**响应示例**:
```json
{
  "resumes": [
    {
      "id": 1,
      "title": "后端工程师简历",
      "template_id": 1,
      "target_position": "后端开发",
      "target_company": "字节跳动",
      "is_active": true,
      "created_at": "2026-01-01T00:00:00",
      "updated_at": "2026-01-15T00:00:00"
    }
  ],
  "total": 1
}
```

---

### 2.2 创建简历

```
POST /api/v1/resume/resumes/
```

**请求体** (JSON):

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| title | string | 是 | 简历标题 |
| template_id | int | 否 | 模板ID |
| target_position | string | 否 | 目标岗位 |
| target_company | string | 否 | 目标公司 |
| personal_info | PersonalInfoCreate | 否 | 个人信息 |
| educations | EducationCreate[] | 否 | 教育经历 |
| experiences | WorkExperienceCreate[] | 否 | 工作经历 |
| projects | ProjectCreate[] | 否 | 项目经历 |
| skills | SkillCreate[] | 否 | 技能列表 |

**响应**: 返回创建的 Resume 对象。

---

### 2.3 获取简历详情

```
GET /api/v1/resume/resumes/{resume_id}
```

**路径参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| resume_id | int | 简历ID |

**响应示例**:
```json
{
  "id": 1,
  "title": "后端工程师简历",
  "template_id": 1,
  "personal_info": {
    "name": "张三",
    "email": "zhangsan@example.com",
    "phone": "13800138000",
    "location": "北京",
    "github": "https://github.com/zhangsan",
    "summary": "3年后端开发经验..."
  },
  "education": [...],
  "work_experience": [...],
  "projects": [...],
  "skills": [...],
  "created_at": "2026-01-01T00:00:00",
  "updated_at": "2026-01-15T00:00:00"
}
```

---

### 2.4 更新简历

```
PUT /api/v1/resume/resumes/{resume_id}
```

**路径参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| resume_id | int | 简历ID |

**请求体** (JSON):

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| title | string | 否 | 简历标题 |
| template_id | int | 否 | 模板ID |
| target_position | string | 否 | 目标岗位 |
| target_company | string | 否 | 目标公司 |
| is_active | bool | 否 | 是否激活 |

**响应**: 返回更新后的 Resume 对象。

---

### 2.5 删除简历

```
DELETE /api/v1/resume/resumes/{resume_id}
```

**路径参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| resume_id | int | 简历ID |

**响应示例**:
```json
{
  "message": "简历删除成功"
}
```

---

### 2.6 AI 优化简历

```
POST /api/v1/resume/resumes/{resume_id}/optimize
```

**路径参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| resume_id | int | 简历ID |

**请求体** (Form):

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| job_description | string | 是 | 职位描述 |

**响应示例**:
```json
{
  "success": true,
  "optimization": {
    "suggestions": [...],
    "optimized_sections": {...}
  }
}
```

---

### 2.7 导出简历 PDF

```
POST /api/v1/resume/resumes/{resume_id}/export/pdf
```

**路径参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| resume_id | int | 简历ID |

**响应示例**:
```json
{
  "success": true,
  "pdf_path": "/exports/resume_1.pdf",
  "download_url": "/api/v1/resume/resumes/1/download/pdf"
}
```

---

### 2.8 下载简历 PDF

```
GET /api/v1/resume/resumes/{resume_id}/download/pdf
```

**路径参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| resume_id | int | 简历ID |

**响应**: 返回 PDF 文件 (`application/pdf`)。

---

### 2.9 获取简历模板列表

```
GET /api/v1/resume/resumes/templates
```

**响应示例**:
```json
{
  "templates": [
    {
      "id": 1,
      "name": "经典模板",
      "description": "简洁大方的经典简历模板",
      "preview_image": "/static/templates/classic.png",
      "category": "professional"
    }
  ]
}
```

---

### 2.10 克隆简历

```
POST /api/v1/resume/resumes/{resume_id}/clone
```

**路径参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| resume_id | int | 简历ID |

**请求体** (Form):

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| new_title | string | 是 | 新简历标题 |

**响应**: 返回克隆后的 Resume 对象。

---

### 2.11 导入简历文件

```
POST /api/v1/resume/resumes/import
```

**请求体** (multipart/form-data):

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| file | File | 是 | 简历文件（支持 PDF/DOC/DOCX） |

**响应示例**:
```json
{
  "success": true,
  "parsed_content": {
    "name": "张三",
    "education": [...],
    "experience": [...]
  },
  "message": "简历解析成功"
}
```

---

### 2.12 获取简历版本历史

```
GET /api/v1/resume/resumes/{resume_id}/versions
```

**路径参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| resume_id | int | 简历ID |

**响应示例**:
```json
{
  "versions": [
    {
      "version": 1,
      "created_at": "2026-01-01T00:00:00",
      "description": "初始版本",
      "changes": ["创建简历"]
    }
  ]
}
```

---

### 2.13 预览简历

```
POST /api/v1/resume/resumes/{resume_id}/preview
```

**路径参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| resume_id | int | 简历ID |

**Query 参数**:

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| template_id | int | 否 | - | 指定预览模板 |

**响应示例**:
```json
{
  "success": true,
  "preview_html": "<html>...</html>"
}
```

---

## 3. LeetCode 刷题 API

**前缀**: `/api/v1/leetcode/leetcode`

### 3.1 获取题目列表

```
GET /api/v1/leetcode/leetcode/problems
```

**Query 参数**:

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| difficulty | string | 否 | - | 难度筛选: `Easy` / `Medium` / `Hard` |
| category | string | 否 | - | 分类筛选 |
| is_completed | bool | 否 | - | 是否已完成 |
| search_keyword | string | 否 | - | 搜索关键词 |
| page | int | 否 | 1 | 页码 |
| page_size | int | 否 | 20 | 每页条数 |

**响应**: 返回分页的题目列表。

---

### 3.2 获取题目详情

```
GET /api/v1/leetcode/leetcode/problems/{problem_id}
```

**路径参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| problem_id | int | 题目ID |

**响应**: 返回题目详情对象。

---

### 3.3 同步 LeetCode 题目

```
POST /api/v1/leetcode/leetcode/sync
```

> 后台异步任务，调用后立即返回。

**Query 参数**:

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| max_problems | int | 否 | - | 最大同步题目数 |
| batch_size | int | 否 | 50 | 批次大小 |

**响应示例**:
```json
{
  "success": true,
  "message": "题目同步任务已启动，将在后台执行..."
}
```

---

### 3.4 获取用户统计

```
GET /api/v1/leetcode/leetcode/statistics
```

**响应**: 返回 LeetCode 刷题统计数据。

---

### 3.5 获取每日挑战

```
GET /api/v1/leetcode/leetcode/daily-challenge
```

**响应示例**:
```json
{
  "date": "2026-02-27",
  "leetcode_id": 1,
  "title": "两数之和",
  "title_slug": "two-sum",
  "difficulty": "Easy",
  "is_premium": false,
  "tags": ["数组", "哈希表"]
}
```

---

### 3.6 获取推荐题目

```
GET /api/v1/leetcode/leetcode/recommendations
```

**Query 参数**:

| 参数 | 类型 | 必填 | 默认值 | 范围 | 说明 |
|------|------|------|--------|------|------|
| count | int | 否 | 5 | 1-20 | 推荐数量 |

**响应示例**:
```json
{
  "problems": [...]
}
```

---

### 3.7 创建提交记录

```
POST /api/v1/leetcode/leetcode/submissions
```

**请求体** (JSON):

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| problem_id | int | 是 | 题目ID |
| language | string | 是 | 编程语言 |
| code | string | 是 | 提交代码 |
| status | string | 是 | 提交状态 |
| runtime | string | 否 | 运行时间 |
| memory | string | 否 | 内存占用 |
| notes | string | 否 | 备注 |
| approach | string | 否 | 解题思路 |
| time_complexity | string | 否 | 时间复杂度 |
| space_complexity | string | 否 | 空间复杂度 |
| is_accepted | bool | 否 | 是否通过 |
| attempt_count | int | 否 | 尝试次数 |

**响应**: 返回提交记录对象。

---

### 3.8 获取提交记录

```
GET /api/v1/leetcode/leetcode/submissions
```

**Query 参数**:

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| problem_id | int | 否 | - | 按题目筛选 |
| status | string | 否 | - | 按状态筛选 |
| limit | int | 否 | 50 | 返回条数上限 |

**响应示例**:
```json
{
  "submissions": [...]
}
```

---

### 3.9 搜索题目

```
GET /api/v1/leetcode/leetcode/search
```

**Query 参数**:

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| keyword | string | 是 | - | 搜索关键词 |
| limit | int | 否 | 20 | 返回条数上限 |

**响应**: 返回搜索匹配的题目列表。

---

### 3.10 爬虫健康检查

```
GET /api/v1/leetcode/leetcode/crawler/health
```

**响应**: 返回爬虫服务健康状态。

---

### 3.11 获取爬虫统计

```
GET /api/v1/leetcode/leetcode/crawler/stats
```

**响应**: 返回爬虫运行统计信息。

---

## 4. 面试练习 API

**前缀**: `/api/v1/interview/interview`

### 4.1 获取面试题目列表

```
GET /api/v1/interview/interview/questions
```

**Query 参数**:

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| category | string | 否 | - | 题目分类: `algorithms` / `os` / `network` |
| difficulty | string | 否 | - | 难度: `初级` / `中级` / `高级` |
| limit | int | 否 | 50 | 返回条数上限 |

**响应示例**:
```json
{
  "success": true,
  "questions": [
    {
      "id": 1,
      "question": "请解释快速排序的原理和时间复杂度",
      "category": "algorithms",
      "difficulty": "中级",
      "tags": ["排序", "分治"],
      "reference_answer": "快速排序是..."
    }
  ],
  "total": 15
}
```

---

### 4.2 分析面试回答

```
POST /api/v1/interview/interview/analyze-answer
```

**请求体** (multipart/form-data):

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| question_id | int | 是 | 题目ID |
| answer_text | string | 是 | 回答文本 |
| audio_file | File | 否 | 语音文件 |

**响应示例**:
```json
{
  "success": true,
  "analysis": {
    "question_id": 1,
    "answer_text": "快速排序通过选取基准元素...",
    "analysis": {
      "content_score": 85,
      "logic_score": 90,
      "accuracy_score": 88,
      "overall_score": 87,
      "strengths": ["逻辑清晰", "表达流畅"],
      "improvements": ["可补充空间复杂度分析"],
      "detailed_feedback": "..."
    },
    "voice_analysis": null,
    "created_at": "2026-02-27T10:00:00"
  }
}
```

---

### 4.3 获取面试统计

```
GET /api/v1/interview/interview/statistics
```

**响应示例**:
```json
{
  "success": true,
  "statistics": {
    "total_questions_answered": 42,
    "average_score": 78.5,
    "total_practice_time": 1200,
    "category_stats": {
      "algorithms": {"count": 20, "avg_score": 82},
      "os": {"count": 12, "avg_score": 75},
      "network": {"count": 10, "avg_score": 76}
    },
    "recent_progress": [...],
    "improvement_areas": ["操作系统", "计算机网络"]
  }
}
```

---

### 4.4 获取每日练习题目

```
GET /api/v1/interview/interview/daily-question
```

**响应示例**:
```json
{
  "success": true,
  "daily_question": {
    "id": 5,
    "question": "请解释 TCP 三次握手的过程",
    "category": "network",
    "difficulty": "中级"
  },
  "date": "2026-02-27"
}
```

---

## 5. 数据统计分析 API

**前缀**: `/api/v1/analytics/analytics`

### 5.1 概览统计数据

```
GET /api/v1/analytics/analytics/overview
```

**响应示例**:
```json
{
  "success": true,
  "overview": {
    "total_study_time": 3600,
    "total_problems_solved": 120,
    "average_score": 82.5,
    "streak_days": 15,
    "weekly_progress": {...},
    "monthly_progress": {...}
  }
}
```

---

### 5.2 进度趋势数据

```
GET /api/v1/analytics/analytics/progress-trend
```

**Query 参数**:

| 参数 | 类型 | 必填 | 默认值 | 范围 | 说明 |
|------|------|------|--------|------|------|
| days | int | 否 | 30 | 7-365 | 统计天数 |

**响应示例**:
```json
{
  "success": true,
  "trend_data": [
    {
      "date": "2026-02-27",
      "leetcode_problems": 3,
      "interview_questions": 2,
      "total_time": 120,
      "average_score": 85
    }
  ],
  "period": "30 days"
}
```

---

### 5.3 分类分布数据

```
GET /api/v1/analytics/analytics/category-distribution
```

**响应示例**:
```json
{
  "success": true,
  "distribution": {
    "leetcode": {
      "Easy": 40,
      "Medium": 55,
      "Hard": 25
    },
    "interview": {
      "algorithms": 20,
      "os": 12,
      "network": 10
    }
  }
}
```

---

### 5.4 分数分析数据

```
GET /api/v1/analytics/analytics/score-analysis
```

**响应示例**:
```json
{
  "success": true,
  "analysis": {
    "score_distribution": {...},
    "difficulty_performance": {...},
    "improvement_trend": {...},
    "weak_areas": [...]
  }
}
```

---

### 5.5 时间分析数据

```
GET /api/v1/analytics/analytics/time-analysis
```

**响应示例**:
```json
{
  "success": true,
  "analysis": {
    "daily_pattern": {...},
    "weekly_pattern": {...},
    "session_duration": {...},
    "productivity_metrics": {...}
  }
}
```

---

### 5.6 学习洞察

```
GET /api/v1/analytics/analytics/learning-insights
```

**响应示例**:
```json
{
  "success": true,
  "insights": {
    "strengths": ["算法基础扎实", "代码风格良好"],
    "improvement_areas": ["系统设计", "并发编程"],
    "learning_recommendations": ["建议多练习中等难度系统设计题"],
    "next_milestones": ["完成 150 道 LeetCode"]
  }
}
```

---

### 5.7 对比数据

```
GET /api/v1/analytics/analytics/comparison
```

**Query 参数**:

| 参数 | 类型 | 必填 | 默认值 | 可选值 | 说明 |
|------|------|------|--------|--------|------|
| period | string | 否 | month | week / month / quarter | 对比周期 |

**响应示例**:
```json
{
  "success": true,
  "comparison": {
    "current_period": "2026-02",
    "previous_period": "2026-01",
    "metrics": {
      "problems_solved": {"current": 45, "previous": 38, "change": "+18.4%"},
      "study_time": {"current": 1800, "previous": 1500, "change": "+20%"},
      "average_score": {"current": 85, "previous": 80, "change": "+6.25%"},
      "new_topics": {"current": 3, "previous": 2, "change": "+50%"}
    }
  }
}
```

---

### 5.8 导出分析报告

```
POST /api/v1/analytics/analytics/export-report
```

**Query 参数**:

| 参数 | 类型 | 必填 | 默认值 | 可选值 | 说明 |
|------|------|------|--------|--------|------|
| format | string | 否 | pdf | pdf / excel / json | 导出格式 |
| period | string | 否 | month | - | 统计周期 |
| include_charts | bool | 否 | true | - | 是否包含图表 |

**响应示例**:
```json
{
  "success": true,
  "report_data": {...},
  "download_url": "/exports/report_202602.pdf",
  "filename": "学习报告_2026年2月.pdf"
}
```

---

### 5.9 获取学习目标

```
GET /api/v1/analytics/analytics/goals
```

**响应示例**:
```json
{
  "success": true,
  "goals": {
    "active_goals": [
      {"id": 1, "title": "每周刷 10 道 LeetCode", "progress": 70}
    ],
    "completed_goals": [...],
    "suggested_goals": [...]
  }
}
```

---

### 5.10 获取成就系统

```
GET /api/v1/analytics/analytics/achievements
```

**响应示例**:
```json
{
  "success": true,
  "achievements": {
    "unlocked": [
      {"id": 1, "title": "初出茅庐", "description": "完成第一道题目", "unlocked_at": "2026-01-01"}
    ],
    "locked": [...],
    "statistics": {
      "total": 20,
      "unlocked_count": 8,
      "completion_rate": 0.4
    }
  }
}
```

---

## 数据模型定义

### PersonalInfoCreate

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 是 | 姓名 |
| email | string | 否 | 邮箱 |
| phone | string | 否 | 电话 |
| location | string | 否 | 所在城市 |
| github | string | 否 | GitHub 主页 |
| linkedin | string | 否 | LinkedIn 主页 |
| website | string | 否 | 个人网站 |
| summary | string | 否 | 个人简介 |

### EducationCreate

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| school | string | 是 | 学校名称 |
| degree | string | 否 | 学位 |
| major | string | 否 | 专业 |
| start_date | string | 否 | 开始日期 |
| end_date | string | 否 | 结束日期 |
| gpa | string | 否 | GPA |
| description | string | 否 | 描述 |
| order_index | int | 否 | 排序序号 |

### WorkExperienceCreate

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| company | string | 是 | 公司名称 |
| position | string | 是 | 职位 |
| location | string | 否 | 工作地点 |
| start_date | string | 否 | 开始日期 |
| end_date | string | 否 | 结束日期 |
| is_current | bool | 否 | 是否在职 |
| description | string | 否 | 工作描述 |
| achievements | string[] | 否 | 工作成就 |
| order_index | int | 否 | 排序序号 |

### ProjectCreate

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 是 | 项目名称 |
| role | string | 否 | 担任角色 |
| start_date | string | 否 | 开始日期 |
| end_date | string | 否 | 结束日期 |
| description | string | 否 | 项目描述 |
| technologies | string[] | 否 | 技术栈 |
| github_url | string | 否 | GitHub 地址 |
| demo_url | string | 否 | 演示地址 |
| achievements | string[] | 否 | 项目成果 |
| order_index | int | 否 | 排序序号 |

### SkillCreate

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| category | string | 是 | 技能分类 |
| name | string | 是 | 技能名称 |
| level | string | 否 | 熟练程度 |
| description | string | 否 | 描述 |
| order_index | int | 否 | 排序序号 |

### LeetCodeProblemCreate

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| leetcode_id | int | 是 | LeetCode 题号 |
| title | string | 是 | 题目标题 |
| title_slug | string | 是 | URL slug |
| difficulty | enum | 否 | 难度: `Easy` / `Medium` / `Hard` |
| category | string | 否 | 分类 |
| tags | string[] | 否 | 标签 |
| content | string | 否 | 题目内容 |
| hints | string[] | 否 | 提示 |
| similar_questions | string[] | 否 | 相似题目 |
| acceptance_rate | float | 否 | 通过率 |
| frequency | float | 否 | 出现频率 |
| is_premium | bool | 否 | 是否会员题 |
| is_active | bool | 否 | 是否激活 |

### ProblemSubmissionCreate

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| problem_id | int | 是 | 题目ID |
| language | string | 是 | 编程语言 |
| code | string | 是 | 提交代码 |
| status | string | 是 | 提交状态 |
| runtime | string | 否 | 运行时间 |
| memory | string | 否 | 内存占用 |
| notes | string | 否 | 备注 |
| approach | string | 否 | 解题思路 |
| time_complexity | string | 否 | 时间复杂度 |
| space_complexity | string | 否 | 空间复杂度 |
| is_accepted | bool | 否 | 是否通过 |
| attempt_count | int | 否 | 尝试次数 |

### 枚举类型

**DifficultyEnum** (LeetCode):
- `Easy` - 简单
- `Medium` - 中等
- `Hard` - 困难

**StatusEnum** (LeetCode):
- `not_started` - 未开始
- `in_progress` - 进行中
- `solved` - 已解决
- `reviewed` - 已复习

**QuestionCategoryEnum** (面试):
- `算法与数据结构`
- `操作系统`
- `计算机网络`
- `数据库`
- `编程语言基础`
- `系统设计`
- `框架相关`
- `项目经验`

**DifficultyEnum** (面试):
- `初级`
- `中级`
- `高级`

**AnswerQualityEnum** (面试):
- `优秀`
- `良好`
- `一般`
- `较差`
