# 程序员面试助手

一个综合性的跨平台面试准备应用，帮助程序员全方位提升面试竞争力。

## 功能特性

- 📝 **简历整理**：AI优化建议、模板选择、JD定制、多版本管理
- 💻 **LeetCode刷题**：自动爬取题目、进度跟踪、代码提交记录
- 🎯 **八股文练习**：语音录制、AI分析、知识点分类
- 📊 **面试总结**：问题记录、回答分析、改进建议
- 📈 **数据统计**：多维度进度跟踪、可视化图表

## 技术架构

- **后端**：FastAPI + SQLite + Ollama AI
- **桌面端**：PyQt6 + Material Design
- **未来移动端**：Flutter + 云端API

## 项目结构

```
interview_assistant/
├── backend/          # FastAPI后端服务
├── frontend/         # PyQt6桌面客户端
├── shared/           # 共享数据和配置
└── docs/            # 项目文档
```

## 快速开始

### 后端服务

```bash
cd backend
pip install -r requirements.txt
python main.py
```

### 桌面客户端

```bash
cd frontend
pip install -r requirements.txt
python main.py
```

## 开发环境

- Python 3.8+
- PyQt6
- FastAPI
- SQLite
- Ollama

## 许可证

MIT License