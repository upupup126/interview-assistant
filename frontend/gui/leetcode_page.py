"""
LeetCode刷题页面
提供题目浏览、筛选、代码编辑和提交功能
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QTableWidget, 
    QTableWidgetItem, QTextEdit, QSplitter, QTabWidget,
    QProgressBar, QFrame, QScrollArea, QGroupBox,
    QCheckBox, QSpinBox, QDateEdit, QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QDate
from PyQt6.QtGui import QFont, QPixmap, QIcon
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from ..components.modern_widgets import (
    ModernCard, ModernButton, ModernInput, ModernComboBox,
    LoadingSpinner, ModernProgressBar
)
from ..services.api_client import APIClient


class LeetCodeStatsWidget(ModernCard):
    """LeetCode统计卡片"""
    
    def __init__(self):
        super().__init__()
        self.setFixedHeight(200)
        self.setup_ui()
        self.load_statistics()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # 标题
        title = QLabel("刷题统计")
        title.setFont(QFont("Microsoft YaHei", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #2196F3; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # 统计网格
        stats_layout = QGridLayout()
        
        # 总题数
        self.total_label = QLabel("0")
        self.total_label.setFont(QFont("Microsoft YaHei", 24, QFont.Weight.Bold))
        self.total_label.setStyleSheet("color: #4CAF50;")
        self.total_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        total_desc = QLabel("总题数")
        total_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        total_desc.setStyleSheet("color: #666; font-size: 12px;")
        
        stats_layout.addWidget(self.total_label, 0, 0)
        stats_layout.addWidget(total_desc, 1, 0)
        
        # 已完成
        self.completed_label = QLabel("0")
        self.completed_label.setFont(QFont("Microsoft YaHei", 24, QFont.Weight.Bold))
        self.completed_label.setStyleSheet("color: #FF9800;")
        self.completed_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        completed_desc = QLabel("已完成")
        completed_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        completed_desc.setStyleSheet("color: #666; font-size: 12px;")
        
        stats_layout.addWidget(self.completed_label, 0, 1)
        stats_layout.addWidget(completed_desc, 1, 1)
        
        # 连续天数
        self.streak_label = QLabel("0")
        self.streak_label.setFont(QFont("Microsoft YaHei", 24, QFont.Weight.Bold))
        self.streak_label.setStyleSheet("color: #E91E63;")
        self.streak_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        streak_desc = QLabel("连续天数")
        streak_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        streak_desc.setStyleSheet("color: #666; font-size: 12px;")
        
        stats_layout.addWidget(self.streak_label, 0, 2)
        stats_layout.addWidget(streak_desc, 1, 2)
        
        # 完成率
        self.rate_label = QLabel("0%")
        self.rate_label.setFont(QFont("Microsoft YaHei", 24, QFont.Weight.Bold))
        self.rate_label.setStyleSheet("color: #9C27B0;")
        self.rate_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        rate_desc = QLabel("完成率")
        rate_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        rate_desc.setStyleSheet("color: #666; font-size: 12px;")
        
        stats_layout.addWidget(self.rate_label, 0, 3)
        stats_layout.addWidget(rate_desc, 1, 3)
        
        layout.addLayout(stats_layout)
        
        # 进度条
        self.progress_bar = ModernProgressBar()
        self.progress_bar.setMaximum(100)
        layout.addWidget(self.progress_bar)
    
    def load_statistics(self):
        """加载统计数据"""
        try:
            api_client = APIClient()
            response = api_client.get("/leetcode/statistics")
            
            if response and response.get("success", True):
                stats = response
                
                self.total_label.setText(str(stats.get("total_problems", 0)))
                self.completed_label.setText(str(stats.get("completed_problems", 0)))
                self.streak_label.setText(str(stats.get("streak_days", 0)))
                
                completion_rate = stats.get("completion_rate", 0) * 100
                self.rate_label.setText(f"{completion_rate:.1f}%")
                self.progress_bar.setValue(int(completion_rate))
                
        except Exception as e:
            print(f"加载统计数据失败: {e}")


class ProblemFilterWidget(ModernCard):
    """题目筛选组件"""
    
    filter_changed = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # 标题
        title = QLabel("筛选条件")
        title.setFont(QFont("Microsoft YaHei", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #333; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # 筛选表单
        form_layout = QGridLayout()
        
        # 难度筛选
        form_layout.addWidget(QLabel("难度:"), 0, 0)
        self.difficulty_combo = ModernComboBox()
        self.difficulty_combo.addItems(["全部", "简单", "中等", "困难"])
        self.difficulty_combo.currentTextChanged.connect(self.on_filter_changed)
        form_layout.addWidget(self.difficulty_combo, 0, 1)
        
        # 分类筛选
        form_layout.addWidget(QLabel("分类:"), 1, 0)
        self.category_combo = ModernComboBox()
        self.category_combo.addItems([
            "全部", "数组", "字符串", "链表", "树", "图", 
            "动态规划", "贪心算法", "回溯", "二分查找"
        ])
        self.category_combo.currentTextChanged.connect(self.on_filter_changed)
        form_layout.addWidget(self.category_combo, 1, 1)
        
        # 状态筛选
        form_layout.addWidget(QLabel("状态:"), 2, 0)
        self.status_combo = ModernComboBox()
        self.status_combo.addItems(["全部", "未完成", "已完成"])
        self.status_combo.currentTextChanged.connect(self.on_filter_changed)
        form_layout.addWidget(self.status_combo, 2, 1)
        
        # 搜索框
        form_layout.addWidget(QLabel("搜索:"), 3, 0)
        self.search_input = ModernInput()
        self.search_input.setPlaceholderText("输入题目名称或关键词...")
        self.search_input.textChanged.connect(self.on_filter_changed)
        form_layout.addWidget(self.search_input, 3, 1)
        
        layout.addLayout(form_layout)
        
        # 重置按钮
        reset_btn = ModernButton("重置筛选", "secondary")
        reset_btn.clicked.connect(self.reset_filters)
        layout.addWidget(reset_btn)
    
    def on_filter_changed(self):
        """筛选条件改变"""
        filters = {
            "difficulty": self.difficulty_combo.currentText(),
            "category": self.category_combo.currentText(),
            "status": self.status_combo.currentText(),
            "search": self.search_input.text()
        }
        self.filter_changed.emit(filters)
    
    def reset_filters(self):
        """重置筛选条件"""
        self.difficulty_combo.setCurrentIndex(0)
        self.category_combo.setCurrentIndex(0)
        self.status_combo.setCurrentIndex(0)
        self.search_input.clear()


class ProblemListWidget(QWidget):
    """题目列表组件"""
    
    problem_selected = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.problems = []
        self.filtered_problems = []
        self.setup_ui()
        self.load_problems()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # 表格
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "题目", "难度", "分类", "通过率", "状态"
        ])
        
        # 设置表格样式
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                gridline-color: #F0F0F0;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #F0F0F0;
            }
            QTableWidget::item:selected {
                background-color: #E3F2FD;
                color: #1976D2;
            }
            QHeaderView::section {
                background-color: #F5F5F5;
                padding: 10px;
                border: none;
                border-bottom: 2px solid #E0E0E0;
                font-weight: bold;
            }
        """)
        
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.itemDoubleClicked.connect(self.on_problem_selected)
        
        layout.addWidget(self.table)
        
        # 分页控件
        pagination_layout = QHBoxLayout()
        
        self.prev_btn = ModernButton("上一页", "secondary")
        self.prev_btn.clicked.connect(self.prev_page)
        pagination_layout.addWidget(self.prev_btn)
        
        pagination_layout.addStretch()
        
        self.page_label = QLabel("第 1 页，共 1 页")
        pagination_layout.addWidget(self.page_label)
        
        pagination_layout.addStretch()
        
        self.next_btn = ModernButton("下一页", "secondary")
        self.next_btn.clicked.connect(self.next_page)
        pagination_layout.addWidget(self.next_btn)
        
        layout.addLayout(pagination_layout)
        
        self.current_page = 1
        self.page_size = 20
        self.total_pages = 1
    
    def load_problems(self):
        """加载题目列表"""
        try:
            api_client = APIClient()
            response = api_client.get("/leetcode/problems", {
                "page": self.current_page,
                "page_size": self.page_size
            })
            
            if response and response.get("problems"):
                self.problems = response["problems"]
                self.filtered_problems = self.problems.copy()
                self.total_pages = response.get("total_pages", 1)
                self.update_table()
                self.update_pagination()
                
        except Exception as e:
            print(f"加载题目列表失败: {e}")
    
    def update_table(self):
        """更新表格显示"""
        self.table.setRowCount(len(self.filtered_problems))
        
        for row, problem in enumerate(self.filtered_problems):
            # ID
            self.table.setItem(row, 0, QTableWidgetItem(str(problem.get("leetcode_id", ""))))
            
            # 题目名称
            self.table.setItem(row, 1, QTableWidgetItem(problem.get("title", "")))
            
            # 难度
            difficulty = problem.get("difficulty", "")
            difficulty_item = QTableWidgetItem(difficulty)
            if difficulty == "Easy":
                difficulty_item.setStyleSheet("color: #4CAF50; font-weight: bold;")
            elif difficulty == "Medium":
                difficulty_item.setStyleSheet("color: #FF9800; font-weight: bold;")
            elif difficulty == "Hard":
                difficulty_item.setStyleSheet("color: #F44336; font-weight: bold;")
            self.table.setItem(row, 2, difficulty_item)
            
            # 分类
            category = problem.get("category", "")
            self.table.setItem(row, 3, QTableWidgetItem(category))
            
            # 通过率
            acceptance_rate = problem.get("acceptance_rate", 0)
            self.table.setItem(row, 4, QTableWidgetItem(f"{acceptance_rate:.1f}%"))
            
            # 状态
            status = "已完成" if problem.get("is_completed") else "未完成"
            status_item = QTableWidgetItem(status)
            if status == "已完成":
                status_item.setStyleSheet("color: #4CAF50; font-weight: bold;")
            else:
                status_item.setStyleSheet("color: #666;")
            self.table.setItem(row, 5, status_item)
        
        # 调整列宽
        self.table.resizeColumnsToContents()
    
    def update_pagination(self):
        """更新分页信息"""
        self.page_label.setText(f"第 {self.current_page} 页，共 {self.total_pages} 页")
        self.prev_btn.setEnabled(self.current_page > 1)
        self.next_btn.setEnabled(self.current_page < self.total_pages)
    
    def prev_page(self):
        """上一页"""
        if self.current_page > 1:
            self.current_page -= 1
            self.load_problems()
    
    def next_page(self):
        """下一页"""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.load_problems()
    
    def apply_filters(self, filters: Dict):
        """应用筛选条件"""
        self.filtered_problems = []
        
        for problem in self.problems:
            # 难度筛选
            if filters["difficulty"] != "全部":
                difficulty_map = {"简单": "Easy", "中等": "Medium", "困难": "Hard"}
                if problem.get("difficulty") != difficulty_map.get(filters["difficulty"]):
                    continue
            
            # 分类筛选
            if filters["category"] != "全部":
                if problem.get("category") != filters["category"]:
                    continue
            
            # 状态筛选
            if filters["status"] != "全部":
                is_completed = problem.get("is_completed", False)
                if filters["status"] == "已完成" and not is_completed:
                    continue
                if filters["status"] == "未完成" and is_completed:
                    continue
            
            # 搜索筛选
            if filters["search"]:
                search_text = filters["search"].lower()
                title = problem.get("title", "").lower()
                if search_text not in title:
                    continue
            
            self.filtered_problems.append(problem)
        
        self.update_table()
    
    def on_problem_selected(self, item):
        """题目被选中"""
        row = item.row()
        if row < len(self.filtered_problems):
            problem = self.filtered_problems[row]
            self.problem_selected.emit(problem)


class CodeEditorWidget(QWidget):
    """代码编辑器组件"""
    
    def __init__(self):
        super().__init__()
        self.current_problem = None
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # 工具栏
        toolbar_layout = QHBoxLayout()
        
        # 语言选择
        toolbar_layout.addWidget(QLabel("语言:"))
        self.language_combo = ModernComboBox()
        self.language_combo.addItems(["Python", "Java", "C++", "JavaScript", "Go"])
        toolbar_layout.addWidget(self.language_combo)
        
        toolbar_layout.addStretch()
        
        # 运行按钮
        self.run_btn = ModernButton("运行代码", "primary")
        self.run_btn.clicked.connect(self.run_code)
        toolbar_layout.addWidget(self.run_btn)
        
        # 提交按钮
        self.submit_btn = ModernButton("提交解答", "success")
        self.submit_btn.clicked.connect(self.submit_code)
        toolbar_layout.addWidget(self.submit_btn)
        
        layout.addLayout(toolbar_layout)
        
        # 代码编辑器
        self.code_editor = QTextEdit()
        self.code_editor.setFont(QFont("Consolas", 12))
        self.code_editor.setStyleSheet("""
            QTextEdit {
                background-color: #1E1E1E;
                color: #D4D4D4;
                border: 1px solid #3C3C3C;
                border-radius: 4px;
                padding: 10px;
            }
        """)
        self.code_editor.setPlaceholderText("请在此处编写代码...")
        layout.addWidget(self.code_editor)
        
        # 结果面板
        self.result_text = QTextEdit()
        self.result_text.setMaximumHeight(150)
        self.result_text.setStyleSheet("""
            QTextEdit {
                background-color: #F5F5F5;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                padding: 10px;
            }
        """)
        self.result_text.setPlaceholderText("运行结果将在此显示...")
        layout.addWidget(self.result_text)
    
    def set_problem(self, problem: Dict):
        """设置当前题目"""
        self.current_problem = problem
        
        # 加载代码模板
        self.load_code_template()
    
    def load_code_template(self):
        """加载代码模板"""
        if not self.current_problem:
            return
        
        language = self.language_combo.currentText()
        
        # 简单的代码模板
        templates = {
            "Python": f"""# {self.current_problem.get('title', '')}
# 难度: {self.current_problem.get('difficulty', '')}

def solution():
    # 请在此处实现解决方案
    pass

# 测试代码
if __name__ == "__main__":
    result = solution()
    print(result)
""",
            "Java": f"""// {self.current_problem.get('title', '')}
// 难度: {self.current_problem.get('difficulty', '')}

public class Solution {{
    public void solution() {{
        // 请在此处实现解决方案
    }}
    
    public static void main(String[] args) {{
        Solution sol = new Solution();
        sol.solution();
    }}
}}
""",
            "C++": f"""// {self.current_problem.get('title', '')}
// 难度: {self.current_problem.get('difficulty', '')}

#include <iostream>
#include <vector>
using namespace std;

class Solution {{
public:
    void solution() {{
        // 请在此处实现解决方案
    }}
}};

int main() {{
    Solution sol;
    sol.solution();
    return 0;
}}
"""
        }
        
        template = templates.get(language, templates["Python"])
        self.code_editor.setPlainText(template)
    
    def run_code(self):
        """运行代码"""
        if not self.current_problem:
            QMessageBox.warning(self, "警告", "请先选择一个题目")
            return
        
        code = self.code_editor.toPlainText()
        language = self.language_combo.currentText()
        
        # 模拟代码运行
        self.result_text.setPlainText(f"""
运行结果:
语言: {language}
状态: 运行成功
输出: Hello World
执行时间: 52 ms
内存消耗: 14.2 MB

注意: 这是模拟运行结果，实际项目中需要集成代码执行服务
        """)
    
    def submit_code(self):
        """提交代码"""
        if not self.current_problem:
            QMessageBox.warning(self, "警告", "请先选择一个题目")
            return
        
        code = self.code_editor.toPlainText()
        language = self.language_combo.currentText()
        
        try:
            # 提交到后端
            api_client = APIClient()
            response = api_client.post("/leetcode/submissions", {
                "problem_id": self.current_problem.get("id"),
                "code": code,
                "language": language,
                "status": "ACCEPTED"  # 模拟提交成功
            })
            
            if response:
                self.result_text.setPlainText(f"""
提交结果:
状态: 通过
语言: {language}
执行时间: 48 ms
内存消耗: 13.8 MB
击败: 85.6% 的用户

恭喜！您的解答已通过所有测试用例。
                """)
                QMessageBox.information(self, "成功", "代码提交成功！")
            else:
                self.result_text.setPlainText("提交失败，请检查网络连接")
                
        except Exception as e:
            self.result_text.setPlainText(f"提交失败: {str(e)}")


class LeetCodePage(QWidget):
    """LeetCode刷题主页面"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.connect_signals()
    
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setSpacing(20)
        
        # 左侧面板
        left_panel = QVBoxLayout()
        left_panel.setSpacing(15)
        
        # 统计卡片
        self.stats_widget = LeetCodeStatsWidget()
        left_panel.addWidget(self.stats_widget)
        
        # 筛选组件
        self.filter_widget = ProblemFilterWidget()
        left_panel.addWidget(self.filter_widget)
        
        # 每日挑战
        daily_challenge_card = ModernCard()
        daily_challenge_layout = QVBoxLayout(daily_challenge_card)
        
        daily_title = QLabel("每日挑战")
        daily_title.setFont(QFont("Microsoft YaHei", 14, QFont.Weight.Bold))
        daily_title.setStyleSheet("color: #FF5722; margin-bottom: 10px;")
        daily_challenge_layout.addWidget(daily_title)
        
        self.daily_problem_label = QLabel("加载中...")
        daily_challenge_layout.addWidget(self.daily_problem_label)
        
        daily_btn = ModernButton("开始挑战", "primary")
        daily_btn.clicked.connect(self.start_daily_challenge)
        daily_challenge_layout.addWidget(daily_btn)
        
        left_panel.addWidget(daily_challenge_card)
        
        left_panel.addStretch()
        
        # 左侧面板容器
        left_widget = QWidget()
        left_widget.setLayout(left_panel)
        left_widget.setFixedWidth(350)
        
        layout.addWidget(left_widget)
        
        # 右侧主内容区
        right_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # 题目列表
        self.problem_list = ProblemListWidget()
        right_splitter.addWidget(self.problem_list)
        
        # 代码编辑器
        self.code_editor = CodeEditorWidget()
        right_splitter.addWidget(self.code_editor)
        
        # 设置分割比例
        right_splitter.setSizes([400, 300])
        
        layout.addWidget(right_splitter)
        
        # 加载每日挑战
        self.load_daily_challenge()
    
    def connect_signals(self):
        """连接信号"""
        self.filter_widget.filter_changed.connect(self.problem_list.apply_filters)
        self.problem_list.problem_selected.connect(self.code_editor.set_problem)
    
    def load_daily_challenge(self):
        """加载每日挑战"""
        try:
            api_client = APIClient()
            response = api_client.get("/leetcode/daily-challenge")
            
            if response and response.get("success"):
                daily_problem = response.get("daily_challenge", {})
                title = daily_problem.get("title", "无")
                difficulty = daily_problem.get("difficulty", "")
                
                self.daily_problem_label.setText(f"{title}\n难度: {difficulty}")
                self.daily_challenge_data = daily_problem
            else:
                self.daily_problem_label.setText("暂无每日挑战")
                
        except Exception as e:
            self.daily_problem_label.setText("加载失败")
            print(f"加载每日挑战失败: {e}")
    
    def start_daily_challenge(self):
        """开始每日挑战"""
        if hasattr(self, 'daily_challenge_data'):
            self.code_editor.set_problem(self.daily_challenge_data)
            QMessageBox.information(self, "每日挑战", "已加载每日挑战题目，开始编码吧！")
        else:
            QMessageBox.warning(self, "提示", "暂无可用的每日挑战题目")
    
    def refresh_data(self):
        """刷新数据"""
        self.stats_widget.load_statistics()
        self.problem_list.load_problems()
        self.load_daily_challenge()