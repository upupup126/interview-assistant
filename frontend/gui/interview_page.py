"""
面试练习页面
提供八股文题库、语音录制和AI分析功能
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QTextEdit, QPushButton, QComboBox, QListWidget, 
    QListWidgetItem, QSplitter, QTabWidget, QProgressBar,
    QFrame, QScrollArea, QGroupBox, QSlider, QMessageBox,
    QFileDialog, QSpinBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QUrl
from PyQt6.QtGui import QFont, QPixmap, QIcon
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from ..components.modern_widgets import (
    ModernCard, ModernButton, ModernInput, ModernComboBox,
    LoadingSpinner, ModernProgressBar
)
from ..services.api_client import APIClient


class KnowledgeCategoryWidget(ModernCard):
    """知识分类选择组件"""
    
    category_selected = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.categories = [
            {"id": "algorithms", "name": "算法与数据结构", "icon": "🧮", "color": "#4CAF50"},
            {"id": "os", "name": "操作系统", "icon": "💻", "color": "#2196F3"},
            {"id": "network", "name": "计算机网络", "icon": "🌐", "color": "#FF9800"},
            {"id": "database", "name": "数据库", "icon": "🗄️", "color": "#9C27B0"},
            {"id": "language", "name": "编程语言基础", "icon": "📝", "color": "#F44336"},
            {"id": "system_design", "name": "系统设计", "icon": "🏗️", "color": "#607D8B"},
            {"id": "framework", "name": "框架相关", "icon": "⚙️", "color": "#795548"},
            {"id": "project", "name": "项目经验", "icon": "📋", "color": "#E91E63"}
        ]
        self.selected_category = None
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # 标题
        title = QLabel("知识分类")
        title.setFont(QFont("Microsoft YaHei", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #333; margin-bottom: 15px;")
        layout.addWidget(title)
        
        # 分类网格
        grid_layout = QGridLayout()
        
        for i, category in enumerate(self.categories):
            category_btn = self.create_category_button(category)
            row = i // 2
            col = i % 2
            grid_layout.addWidget(category_btn, row, col)
        
        layout.addLayout(grid_layout)
    
    def create_category_button(self, category: Dict) -> QPushButton:
        """创建分类按钮"""
        btn = QPushButton()
        btn.setFixedHeight(80)
        
        # 设置按钮文本和样式
        btn.setText(f"{category['icon']}\n{category['name']}")
        btn.setFont(QFont("Microsoft YaHei", 12))
        
        # 设置样式
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: white;
                border: 2px solid {category['color']};
                border-radius: 8px;
                color: {category['color']};
                font-weight: bold;
                padding: 10px;
            }}
            QPushButton:hover {{
                background-color: {category['color']};
                color: white;
            }}
            QPushButton:pressed {{
                background-color: {category['color']};
                color: white;
                border: 2px solid {category['color']};
            }}
        """)
        
        # 连接点击事件
        btn.clicked.connect(lambda checked, cat=category: self.select_category(cat))
        
        return btn
    
    def select_category(self, category: Dict):
        """选择分类"""
        self.selected_category = category
        self.category_selected.emit(category['id'])


class QuestionListWidget(QWidget):
    """题目列表组件"""
    
    question_selected = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.questions = []
        self.current_category = None
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # 标题和统计
        header_layout = QHBoxLayout()
        
        self.title_label = QLabel("请选择知识分类")
        self.title_label.setFont(QFont("Microsoft YaHei", 14, QFont.Weight.Bold))
        header_layout.addWidget(self.title_label)
        
        header_layout.addStretch()
        
        self.count_label = QLabel("共 0 题")
        self.count_label.setStyleSheet("color: #666; font-size: 12px;")
        header_layout.addWidget(self.count_label)
        
        layout.addLayout(header_layout)
        
        # 题目列表
        self.question_list = QListWidget()
        self.question_list.setStyleSheet("""
            QListWidget {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #F0F0F0;
                border-radius: 4px;
                margin: 2px;
            }
            QListWidget::item:hover {
                background-color: #F5F5F5;
            }
            QListWidget::item:selected {
                background-color: #E3F2FD;
                color: #1976D2;
            }
        """)
        
        self.question_list.itemClicked.connect(self.on_question_clicked)
        layout.addWidget(self.question_list)
        
        # 操作按钮
        button_layout = QHBoxLayout()
        
        self.random_btn = ModernButton("随机题目", "primary")
        self.random_btn.clicked.connect(self.select_random_question)
        button_layout.addWidget(self.random_btn)
        
        self.refresh_btn = ModernButton("刷新列表", "secondary")
        self.refresh_btn.clicked.connect(self.refresh_questions)
        button_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(button_layout)
    
    def load_questions(self, category_id: str):
        """加载指定分类的题目"""
        self.current_category = category_id
        
        try:
            api_client = APIClient()
            response = api_client.get(f"/interview/questions", {
                "category": category_id
            })
            
            if response and response.get("questions"):
                self.questions = response["questions"]
                self.update_question_list()
            else:
                # 如果没有数据，使用模拟数据
                self.load_mock_questions(category_id)
                
        except Exception as e:
            print(f"加载题目失败: {e}")
            self.load_mock_questions(category_id)
    
    def load_mock_questions(self, category_id: str):
        """加载模拟题目数据"""
        mock_questions = {
            "algorithms": [
                {"id": 1, "question": "请解释时间复杂度和空间复杂度的概念", "difficulty": "中等"},
                {"id": 2, "question": "什么是哈希表？它的优缺点是什么？", "difficulty": "简单"},
                {"id": 3, "question": "请描述快速排序的原理和实现", "difficulty": "中等"},
                {"id": 4, "question": "什么是动态规划？请举例说明", "difficulty": "困难"},
                {"id": 5, "question": "二叉树的遍历方式有哪些？", "difficulty": "简单"}
            ],
            "os": [
                {"id": 6, "question": "进程和线程的区别是什么？", "difficulty": "中等"},
                {"id": 7, "question": "什么是死锁？如何避免死锁？", "difficulty": "困难"},
                {"id": 8, "question": "虚拟内存的作用是什么？", "difficulty": "中等"},
                {"id": 9, "question": "CPU调度算法有哪些？", "difficulty": "中等"},
                {"id": 10, "question": "什么是系统调用？", "difficulty": "简单"}
            ],
            "network": [
                {"id": 11, "question": "TCP和UDP的区别是什么？", "difficulty": "中等"},
                {"id": 12, "question": "HTTP和HTTPS的区别？", "difficulty": "简单"},
                {"id": 13, "question": "什么是三次握手和四次挥手？", "difficulty": "中等"},
                {"id": 14, "question": "OSI七层模型是什么？", "difficulty": "中等"},
                {"id": 15, "question": "什么是DNS？它的工作原理？", "difficulty": "简单"}
            ]
        }
        
        self.questions = mock_questions.get(category_id, [])
        self.update_question_list()
    
    def update_question_list(self):
        """更新题目列表显示"""
        self.question_list.clear()
        
        category_names = {
            "algorithms": "算法与数据结构",
            "os": "操作系统", 
            "network": "计算机网络",
            "database": "数据库",
            "language": "编程语言基础",
            "system_design": "系统设计",
            "framework": "框架相关",
            "project": "项目经验"
        }
        
        category_name = category_names.get(self.current_category, "未知分类")
        self.title_label.setText(f"{category_name} 题目")
        self.count_label.setText(f"共 {len(self.questions)} 题")
        
        for question in self.questions:
            item = QListWidgetItem()
            
            # 设置题目文本
            difficulty_color = {
                "简单": "#4CAF50",
                "中等": "#FF9800", 
                "困难": "#F44336"
            }
            
            difficulty = question.get("difficulty", "中等")
            color = difficulty_color.get(difficulty, "#666")
            
            item_text = f"[{difficulty}] {question['question']}"
            item.setText(item_text)
            
            # 存储题目数据
            item.setData(Qt.ItemDataRole.UserRole, question)
            
            self.question_list.addItem(item)
    
    def on_question_clicked(self, item):
        """题目被点击"""
        question_data = item.data(Qt.ItemDataRole.UserRole)
        if question_data:
            self.question_selected.emit(question_data)
    
    def select_random_question(self):
        """选择随机题目"""
        if self.questions:
            import random
            question = random.choice(self.questions)
            self.question_selected.emit(question)
    
    def refresh_questions(self):
        """刷新题目列表"""
        if self.current_category:
            self.load_questions(self.current_category)


class VoiceRecorderWidget(ModernCard):
    """语音录制组件"""
    
    recording_finished = pyqtSignal(str)  # 录制完成信号，传递音频文件路径
    
    def __init__(self):
        super().__init__()
        self.is_recording = False
        self.audio_file_path = None
        self.recording_timer = QTimer()
        self.recording_duration = 0
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # 标题
        title = QLabel("语音录制")
        title.setFont(QFont("Microsoft YaHei", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #333; margin-bottom: 15px;")
        layout.addWidget(title)
        
        # 录制状态显示
        self.status_label = QLabel("准备录制")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                background-color: #F5F5F5;
                border: 2px dashed #CCC;
                border-radius: 8px;
                padding: 20px;
                font-size: 16px;
                color: #666;
            }
        """)
        layout.addWidget(self.status_label)
        
        # 录制时间显示
        self.time_label = QLabel("00:00")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setFont(QFont("Consolas", 18, QFont.Weight.Bold))
        self.time_label.setStyleSheet("color: #E91E63; margin: 10px;")
        layout.addWidget(self.time_label)
        
        # 控制按钮
        button_layout = QHBoxLayout()
        
        self.record_btn = ModernButton("开始录制", "primary")
        self.record_btn.clicked.connect(self.toggle_recording)
        button_layout.addWidget(self.record_btn)
        
        self.play_btn = ModernButton("播放录音", "secondary")
        self.play_btn.clicked.connect(self.play_recording)
        self.play_btn.setEnabled(False)
        button_layout.addWidget(self.play_btn)
        
        self.save_btn = ModernButton("保存录音", "success")
        self.save_btn.clicked.connect(self.save_recording)
        self.save_btn.setEnabled(False)
        button_layout.addWidget(self.save_btn)
        
        layout.addLayout(button_layout)
        
        # 音量控制
        volume_layout = QHBoxLayout()
        volume_layout.addWidget(QLabel("音量:"))
        
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(70)
        volume_layout.addWidget(self.volume_slider)
        
        self.volume_label = QLabel("70%")
        volume_layout.addWidget(self.volume_label)
        
        layout.addLayout(volume_layout)
    
    def setup_connections(self):
        """设置信号连接"""
        self.recording_timer.timeout.connect(self.update_recording_time)
        self.volume_slider.valueChanged.connect(self.update_volume_label)
    
    def toggle_recording(self):
        """切换录制状态"""
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()
    
    def start_recording(self):
        """开始录制"""
        try:
            self.is_recording = True
            self.recording_duration = 0
            
            # 更新UI状态
            self.record_btn.setText("停止录制")
            self.record_btn.setStyleSheet("""
                QPushButton {
                    background-color: #F44336;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 6px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #D32F2F;
                }
            """)
            
            self.status_label.setText("🎤 正在录制...")
            self.status_label.setStyleSheet("""
                QLabel {
                    background-color: #FFEBEE;
                    border: 2px solid #F44336;
                    border-radius: 8px;
                    padding: 20px;
                    font-size: 16px;
                    color: #F44336;
                }
            """)
            
            self.play_btn.setEnabled(False)
            self.save_btn.setEnabled(False)
            
            # 启动计时器
            self.recording_timer.start(1000)
            
            # 这里应该启动实际的音频录制
            # 为了演示，我们只是模拟录制过程
            print("开始录制音频...")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"开始录制失败: {str(e)}")
    
    def stop_recording(self):
        """停止录制"""
        try:
            self.is_recording = False
            
            # 停止计时器
            self.recording_timer.stop()
            
            # 更新UI状态
            self.record_btn.setText("开始录制")
            self.record_btn.setStyleSheet("")  # 恢复默认样式
            
            self.status_label.setText("✅ 录制完成")
            self.status_label.setStyleSheet("""
                QLabel {
                    background-color: #E8F5E8;
                    border: 2px solid #4CAF50;
                    border-radius: 8px;
                    padding: 20px;
                    font-size: 16px;
                    color: #4CAF50;
                }
            """)
            
            self.play_btn.setEnabled(True)
            self.save_btn.setEnabled(True)
            
            # 生成模拟音频文件路径
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.audio_file_path = f"data/recordings/recording_{timestamp}.wav"
            
            # 这里应该保存实际的音频文件
            print(f"录制完成，文件路径: {self.audio_file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"停止录制失败: {str(e)}")
    
    def play_recording(self):
        """播放录音"""
        if self.audio_file_path:
            # 这里应该使用QMediaPlayer播放音频
            # 为了演示，只是显示消息
            QMessageBox.information(self, "播放", f"播放录音: {self.audio_file_path}")
    
    def save_recording(self):
        """保存录音"""
        if self.audio_file_path:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "保存录音", 
                f"recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav",
                "音频文件 (*.wav *.mp3)"
            )
            
            if file_path:
                # 这里应该复制音频文件到指定位置
                QMessageBox.information(self, "成功", f"录音已保存到: {file_path}")
                self.recording_finished.emit(file_path)
    
    def update_recording_time(self):
        """更新录制时间"""
        self.recording_duration += 1
        minutes = self.recording_duration // 60
        seconds = self.recording_duration % 60
        self.time_label.setText(f"{minutes:02d}:{seconds:02d}")
    
    def update_volume_label(self, value):
        """更新音量标签"""
        self.volume_label.setText(f"{value}%")


class AnswerAnalysisWidget(ModernCard):
    """回答分析组件"""
    
    def __init__(self):
        super().__init__()
        self.current_analysis = None
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # 标题
        title = QLabel("AI 分析结果")
        title.setFont(QFont("Microsoft YaHei", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #333; margin-bottom: 15px;")
        layout.addWidget(title)
        
        # 分析内容
        self.analysis_text = QTextEdit()
        self.analysis_text.setStyleSheet("""
            QTextEdit {
                background-color: #FAFAFA;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                padding: 15px;
                font-size: 14px;
                line-height: 1.6;
            }
        """)
        self.analysis_text.setPlaceholderText("AI分析结果将在此显示...")
        self.analysis_text.setReadOnly(True)
        layout.addWidget(self.analysis_text)
        
        # 评分显示
        score_layout = QHBoxLayout()
        
        score_layout.addWidget(QLabel("综合评分:"))
        
        self.score_bar = ModernProgressBar()
        self.score_bar.setMaximum(100)
        self.score_bar.setValue(0)
        score_layout.addWidget(self.score_bar)
        
        self.score_label = QLabel("0/100")
        self.score_label.setFont(QFont("Microsoft YaHei", 12, QFont.Weight.Bold))
        self.score_label.setStyleSheet("color: #2196F3;")
        score_layout.addWidget(self.score_label)
        
        layout.addLayout(score_layout)
        
        # 操作按钮
        button_layout = QHBoxLayout()
        
        self.analyze_btn = ModernButton("开始分析", "primary")
        self.analyze_btn.clicked.connect(self.start_analysis)
        button_layout.addWidget(self.analyze_btn)
        
        self.export_btn = ModernButton("导出报告", "secondary")
        self.export_btn.clicked.connect(self.export_analysis)
        self.export_btn.setEnabled(False)
        button_layout.addWidget(self.export_btn)
        
        layout.addLayout(button_layout)
    
    def start_analysis(self):
        """开始AI分析"""
        try:
            # 模拟AI分析过程
            self.analyze_btn.setText("分析中...")
            self.analyze_btn.setEnabled(False)
            
            # 使用定时器模拟分析延迟
            QTimer.singleShot(2000, self.show_analysis_result)
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"分析失败: {str(e)}")
            self.analyze_btn.setText("开始分析")
            self.analyze_btn.setEnabled(True)
    
    def show_analysis_result(self):
        """显示分析结果"""
        # 模拟分析结果
        analysis_result = """
📊 语音分析报告

🎯 回答质量评估:
• 内容完整性: 85% - 回答涵盖了问题的主要方面
• 逻辑清晰度: 78% - 表达逻辑较为清晰，但部分地方可以更简洁
• 技术准确性: 92% - 技术概念理解准确，表述专业

🗣️ 语音表现分析:
• 语速适中: 建议保持当前语速
• 发音清晰: 整体发音清晰，个别词汇可以更标准
• 语调变化: 可以增加一些语调变化来增强表达力

💡 改进建议:
1. 可以在开头简要概括要点，让回答更有条理
2. 举例说明可以让技术概念更容易理解
3. 结尾可以简单总结，加深印象

⭐ 综合评分: 85/100
这是一个很好的回答！继续保持，注意改进建议中的要点。
        """
        
        self.analysis_text.setPlainText(analysis_result)
        
        # 更新评分
        score = 85
        self.score_bar.setValue(score)
        self.score_label.setText(f"{score}/100")
        
        # 根据分数设置颜色
        if score >= 90:
            color = "#4CAF50"  # 绿色
        elif score >= 70:
            color = "#FF9800"  # 橙色
        else:
            color = "#F44336"  # 红色
        
        self.score_label.setStyleSheet(f"color: {color}; font-weight: bold;")
        
        # 恢复按钮状态
        self.analyze_btn.setText("重新分析")
        self.analyze_btn.setEnabled(True)
        self.export_btn.setEnabled(True)
        
        self.current_analysis = analysis_result
    
    def export_analysis(self):
        """导出分析报告"""
        if self.current_analysis:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "导出分析报告",
                f"analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                "文本文件 (*.txt)"
            )
            
            if file_path:
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(self.current_analysis)
                    QMessageBox.information(self, "成功", f"分析报告已导出到: {file_path}")
                except Exception as e:
                    QMessageBox.critical(self, "错误", f"导出失败: {str(e)}")


class InterviewPage(QWidget):
    """面试练习主页面"""
    
    def __init__(self):
        super().__init__()
        self.current_question = None
        self.setup_ui()
        self.connect_signals()
    
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setSpacing(20)
        
        # 左侧面板
        left_panel = QVBoxLayout()
        left_panel.setSpacing(15)
        
        # 知识分类选择
        self.category_widget = KnowledgeCategoryWidget()
        left_panel.addWidget(self.category_widget)
        
        # 题目列表
        self.question_list = QuestionListWidget()
        left_panel.addWidget(self.question_list)
        
        # 左侧面板容器
        left_widget = QWidget()
        left_widget.setLayout(left_panel)
        left_widget.setFixedWidth(400)
        
        layout.addWidget(left_widget)
        
        # 右侧主内容区
        right_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # 题目显示区域
        question_card = ModernCard()
        question_layout = QVBoxLayout(question_card)
        
        question_title = QLabel("当前题目")
        question_title.setFont(QFont("Microsoft YaHei", 14, QFont.Weight.Bold))
        question_title.setStyleSheet("color: #333; margin-bottom: 10px;")
        question_layout.addWidget(question_title)
        
        self.question_text = QLabel("请从左侧选择知识分类和题目")
        self.question_text.setWordWrap(True)
        self.question_text.setStyleSheet("""
            QLabel {
                background-color: #F8F9FA;
                border: 1px solid #E9ECEF;
                border-radius: 8px;
                padding: 20px;
                font-size: 16px;
                line-height: 1.6;
            }
        """)
        question_layout.addWidget(self.question_text)
        
        right_splitter.addWidget(question_card)
        
        # 下方功能区域
        bottom_widget = QWidget()
        bottom_layout = QHBoxLayout(bottom_widget)
        bottom_layout.setSpacing(15)
        
        # 语音录制
        self.voice_recorder = VoiceRecorderWidget()
        bottom_layout.addWidget(self.voice_recorder)
        
        # AI分析
        self.answer_analysis = AnswerAnalysisWidget()
        bottom_layout.addWidget(self.answer_analysis)
        
        right_splitter.addWidget(bottom_widget)
        
        # 设置分割比例
        right_splitter.setSizes([200, 400])
        
        layout.addWidget(right_splitter)
    
    def connect_signals(self):
        """连接信号"""
        self.category_widget.category_selected.connect(self.question_list.load_questions)
        self.question_list.question_selected.connect(self.set_current_question)
        self.voice_recorder.recording_finished.connect(self.on_recording_finished)
    
    def set_current_question(self, question: Dict):
        """设置当前题目"""
        self.current_question = question
        
        difficulty_colors = {
            "简单": "#4CAF50",
            "中等": "#FF9800",
            "困难": "#F44336"
        }
        
        difficulty = question.get("difficulty", "中等")
        color = difficulty_colors.get(difficulty, "#666")
        
        question_html = f"""
        <div style="font-size: 16px; line-height: 1.8;">
            <div style="margin-bottom: 15px;">
                <span style="background-color: {color}; color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold;">
                    {difficulty}
                </span>
            </div>
            <div style="font-size: 18px; font-weight: bold; margin-bottom: 15px; color: #333;">
                {question['question']}
            </div>
            <div style="color: #666; font-size: 14px;">
                💡 提示：请仔细思考后用语音回答这个问题，AI将对您的回答进行分析和评分。
            </div>
        </div>
        """
        
        self.question_text.setText(question_html)
        self.question_text.setTextFormat(Qt.TextFormat.RichText)
    
    def on_recording_finished(self, file_path: str):
        """录制完成处理"""
        if self.current_question:
            # 这里可以将录音文件发送给后端进行AI分析
            print(f"录制完成: {file_path}")
            print(f"当前题目: {self.current_question['question']}")
            
            # 自动开始AI分析
            self.answer_analysis.start_analysis()
    
    def refresh_data(self):
        """刷新数据"""
        # 可以在这里添加数据刷新逻辑
        pass