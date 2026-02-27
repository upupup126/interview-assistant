"""
数据统计分析页面
提供多维度的学习进度跟踪和可视化图表
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QComboBox, QDateEdit, QScrollArea,
    QFrame, QGroupBox, QTabWidget, QTableWidget, QTableWidgetItem,
    QProgressBar, QSpinBox, QCheckBox
)
from PyQt6.QtCore import Qt, QDate, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QPainter, QPen, QBrush, QColor
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

from ..components.modern_widgets import (
    ModernCard, ModernButton, ModernInput, ModernComboBox,
    LoadingSpinner, ModernProgressBar
)
from ..services.api_client import APIClient


class StatisticsCard(ModernCard):
    """统计卡片组件"""
    
    def __init__(self, title: str, value: str, subtitle: str = "", color: str = "#2196F3"):
        super().__init__()
        self.setFixedHeight(120)
        self.setup_ui(title, value, subtitle, color)
    
    def setup_ui(self, title: str, value: str, subtitle: str, color: str):
        layout = QVBoxLayout(self)
        
        # 标题
        title_label = QLabel(title)
        title_label.setFont(QFont("Microsoft YaHei", 12))
        title_label.setStyleSheet("color: #666; margin-bottom: 5px;")
        layout.addWidget(title_label)
        
        # 数值
        value_label = QLabel(value)
        value_label.setFont(QFont("Microsoft YaHei", 28, QFont.Weight.Bold))
        value_label.setStyleSheet(f"color: {color}; margin-bottom: 5px;")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(value_label)
        
        # 副标题
        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setFont(QFont("Microsoft YaHei", 10))
            subtitle_label.setStyleSheet("color: #999;")
            subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(subtitle_label)
    
    def update_value(self, value: str, subtitle: str = ""):
        """更新数值"""
        # 找到数值标签并更新
        for i in range(self.layout().count()):
            widget = self.layout().itemAt(i).widget()
            if isinstance(widget, QLabel) and widget.font().pointSize() == 28:
                widget.setText(value)
                break


class ChartWidget(QWidget):
    """图表组件基类"""
    
    def __init__(self, title: str = ""):
        super().__init__()
        self.title = title
        self.figure = Figure(figsize=(8, 6), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        if self.title:
            title_label = QLabel(self.title)
            title_label.setFont(QFont("Microsoft YaHei", 14, QFont.Weight.Bold))
            title_label.setStyleSheet("color: #333; margin-bottom: 10px;")
            layout.addWidget(title_label)
        
        layout.addWidget(self.canvas)
        
        # 设置图表样式
        self.figure.patch.set_facecolor('white')
        plt.style.use('default')


class ProgressTrendChart(ChartWidget):
    """进度趋势图表"""
    
    def __init__(self):
        super().__init__("学习进度趋势")
        self.load_data()
    
    def load_data(self):
        """加载数据并绘制图表"""
        try:
            # 模拟数据
            dates = []
            leetcode_progress = []
            interview_progress = []
            
            # 生成最近30天的数据
            for i in range(30):
                date = datetime.now() - timedelta(days=29-i)
                dates.append(date.strftime("%m-%d"))
                
                # 模拟进度数据
                leetcode_progress.append(min(100, 20 + i * 2.5 + np.random.randint(-5, 6)))
                interview_progress.append(min(100, 15 + i * 2.8 + np.random.randint(-4, 5)))
            
            # 清除之前的图表
            self.figure.clear()
            
            # 创建子图
            ax = self.figure.add_subplot(111)
            
            # 绘制线图
            ax.plot(dates, leetcode_progress, 'o-', color='#4CAF50', linewidth=2, 
                   markersize=4, label='LeetCode刷题')
            ax.plot(dates, interview_progress, 's-', color='#2196F3', linewidth=2, 
                   markersize=4, label='面试练习')
            
            # 设置图表样式
            ax.set_xlabel('日期', fontsize=10)
            ax.set_ylabel('完成题目数', fontsize=10)
            ax.set_title('最近30天学习趋势', fontsize=12, fontweight='bold')
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            # 设置x轴标签旋转
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
            
            # 调整布局
            self.figure.tight_layout()
            
            # 刷新画布
            self.canvas.draw()
            
        except Exception as e:
            print(f"加载进度趋势数据失败: {e}")


class CategoryDistributionChart(ChartWidget):
    """分类分布饼图"""
    
    def __init__(self):
        super().__init__("知识点分布")
        self.load_data()
    
    def load_data(self):
        """加载数据并绘制饼图"""
        try:
            # 模拟数据
            categories = ['算法与数据结构', '操作系统', '计算机网络', '数据库', '编程语言', '系统设计', '其他']
            values = [25, 18, 15, 12, 10, 8, 12]
            colors = ['#4CAF50', '#2196F3', '#FF9800', '#9C27B0', '#F44336', '#607D8B', '#795548']
            
            # 清除之前的图表
            self.figure.clear()
            
            # 创建子图
            ax = self.figure.add_subplot(111)
            
            # 绘制饼图
            wedges, texts, autotexts = ax.pie(values, labels=categories, colors=colors, 
                                            autopct='%1.1f%%', startangle=90)
            
            # 设置文本样式
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
            
            ax.set_title('已完成题目分类分布', fontsize=12, fontweight='bold')
            
            # 调整布局
            self.figure.tight_layout()
            
            # 刷新画布
            self.canvas.draw()
            
        except Exception as e:
            print(f"加载分类分布数据失败: {e}")


class ScoreDistributionChart(ChartWidget):
    """分数分布柱状图"""
    
    def __init__(self):
        super().__init__("分数分布统计")
        self.load_data()
    
    def load_data(self):
        """加载数据并绘制柱状图"""
        try:
            # 模拟数据
            score_ranges = ['0-60', '60-70', '70-80', '80-90', '90-100']
            counts = [2, 8, 15, 25, 12]
            colors = ['#F44336', '#FF9800', '#FFC107', '#4CAF50', '#2196F3']
            
            # 清除之前的图表
            self.figure.clear()
            
            # 创建子图
            ax = self.figure.add_subplot(111)
            
            # 绘制柱状图
            bars = ax.bar(score_ranges, counts, color=colors, alpha=0.8)
            
            # 在柱子上显示数值
            for bar, count in zip(bars, counts):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                       f'{count}', ha='center', va='bottom', fontweight='bold')
            
            ax.set_xlabel('分数区间', fontsize=10)
            ax.set_ylabel('题目数量', fontsize=10)
            ax.set_title('面试题目分数分布', fontsize=12, fontweight='bold')
            ax.grid(True, alpha=0.3, axis='y')
            
            # 调整布局
            self.figure.tight_layout()
            
            # 刷新画布
            self.canvas.draw()
            
        except Exception as e:
            print(f"加载分数分布数据失败: {e}")


class WeeklyHeatmapChart(ChartWidget):
    """周热力图"""
    
    def __init__(self):
        super().__init__("学习活跃度热力图")
        self.load_data()
    
    def load_data(self):
        """加载数据并绘制热力图"""
        try:
            # 模拟数据 - 7天 x 24小时
            days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
            hours = list(range(24))
            
            # 生成随机活跃度数据
            np.random.seed(42)
            data = np.random.randint(0, 10, size=(7, 24))
            
            # 模拟真实的学习模式（白天更活跃）
            for i in range(7):
                for j in range(24):
                    if 9 <= j <= 22:  # 白天时间
                        data[i][j] = max(data[i][j], np.random.randint(3, 8))
                    else:  # 夜晚时间
                        data[i][j] = min(data[i][j], np.random.randint(0, 3))
            
            # 清除之前的图表
            self.figure.clear()
            
            # 创建子图
            ax = self.figure.add_subplot(111)
            
            # 绘制热力图
            im = ax.imshow(data, cmap='YlOrRd', aspect='auto')
            
            # 设置坐标轴
            ax.set_xticks(range(0, 24, 2))
            ax.set_xticklabels([f'{h}:00' for h in range(0, 24, 2)])
            ax.set_yticks(range(7))
            ax.set_yticklabels(days)
            
            ax.set_xlabel('时间', fontsize=10)
            ax.set_ylabel('星期', fontsize=10)
            ax.set_title('一周学习活跃度分布', fontsize=12, fontweight='bold')
            
            # 添加颜色条
            cbar = self.figure.colorbar(im, ax=ax)
            cbar.set_label('活跃度', rotation=270, labelpad=15)
            
            # 调整布局
            self.figure.tight_layout()
            
            # 刷新画布
            self.canvas.draw()
            
        except Exception as e:
            print(f"加载热力图数据失败: {e}")


class DetailedStatsTable(QWidget):
    """详细统计表格"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # 标题
        title = QLabel("详细统计数据")
        title.setFont(QFont("Microsoft YaHei", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #333; margin-bottom: 15px;")
        layout.addWidget(title)
        
        # 表格
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "分类", "总题数", "已完成", "完成率", "平均分", "最高分"
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
        
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)
    
    def load_data(self):
        """加载表格数据"""
        try:
            # 模拟数据
            data = [
                ["算法与数据结构", 50, 35, 70.0, 82.5, 95],
                ["操作系统", 30, 22, 73.3, 78.2, 92],
                ["计算机网络", 25, 18, 72.0, 80.1, 88],
                ["数据库", 20, 12, 60.0, 75.8, 90],
                ["编程语言基础", 35, 28, 80.0, 85.3, 98],
                ["系统设计", 15, 8, 53.3, 72.5, 85],
                ["框架相关", 25, 15, 60.0, 77.9, 89],
                ["项目经验", 20, 16, 80.0, 88.2, 95]
            ]
            
            self.table.setRowCount(len(data))
            
            for row, row_data in enumerate(data):
                for col, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value))
                    
                    # 设置数值格式
                    if col == 3:  # 完成率
                        item.setText(f"{value}%")
                        # 根据完成率设置颜色
                        if value >= 80:
                            item.setBackground(QColor("#E8F5E8"))
                        elif value >= 60:
                            item.setBackground(QColor("#FFF3E0"))
                        else:
                            item.setBackground(QColor("#FFEBEE"))
                    elif col in [4, 5]:  # 平均分、最高分
                        item.setText(f"{value}")
                        if value >= 90:
                            item.setForeground(QColor("#4CAF50"))
                        elif value >= 80:
                            item.setForeground(QColor("#FF9800"))
                        else:
                            item.setForeground(QColor("#F44336"))
                    
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.table.setItem(row, col, item)
            
            # 调整列宽
            self.table.resizeColumnsToContents()
            
        except Exception as e:
            print(f"加载表格数据失败: {e}")


class AnalyticsPage(QWidget):
    """数据统计分析主页面"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.load_statistics()
        
        # 设置定时器定期刷新数据
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.refresh_timer.start(300000)  # 5分钟刷新一次
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # 顶部统计卡片
        self.setup_stats_cards(layout)
        
        # 主要内容区域
        content_layout = QHBoxLayout()
        
        # 左侧图表区域
        left_panel = QVBoxLayout()
        
        # 图表标签页
        self.chart_tabs = QTabWidget()
        self.chart_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #F5F5F5;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #2196F3;
            }
        """)
        
        # 添加图表页面
        self.progress_chart = ProgressTrendChart()
        self.chart_tabs.addTab(self.progress_chart, "进度趋势")
        
        self.category_chart = CategoryDistributionChart()
        self.chart_tabs.addTab(self.category_chart, "分类分布")
        
        self.score_chart = ScoreDistributionChart()
        self.chart_tabs.addTab(self.score_chart, "分数分布")
        
        self.heatmap_chart = WeeklyHeatmapChart()
        self.chart_tabs.addTab(self.heatmap_chart, "活跃度热力图")
        
        left_panel.addWidget(self.chart_tabs)
        
        # 右侧详细统计
        right_panel = QVBoxLayout()
        
        # 详细统计表格
        self.stats_table = DetailedStatsTable()
        right_panel.addWidget(self.stats_table)
        
        # 操作按钮
        button_layout = QHBoxLayout()
        
        self.export_btn = ModernButton("导出报告", "primary")
        self.export_btn.clicked.connect(self.export_report)
        button_layout.addWidget(self.export_btn)
        
        self.refresh_btn = ModernButton("刷新数据", "secondary")
        self.refresh_btn.clicked.connect(self.refresh_data)
        button_layout.addWidget(self.refresh_btn)
        
        button_layout.addStretch()
        
        # 时间范围选择
        button_layout.addWidget(QLabel("时间范围:"))
        self.time_range_combo = ModernComboBox()
        self.time_range_combo.addItems(["最近7天", "最近30天", "最近3个月", "最近1年"])
        self.time_range_combo.setCurrentText("最近30天")
        self.time_range_combo.currentTextChanged.connect(self.on_time_range_changed)
        button_layout.addWidget(self.time_range_combo)
        
        right_panel.addLayout(button_layout)
        
        # 设置布局比例
        content_layout.addLayout(left_panel, 2)
        content_layout.addLayout(right_panel, 1)
        
        layout.addLayout(content_layout)
    
    def setup_stats_cards(self, layout):
        """设置统计卡片"""
        cards_layout = QHBoxLayout()
        
        # 总学习时间
        self.time_card = StatisticsCard("总学习时间", "0小时", "本月增加 0小时", "#4CAF50")
        cards_layout.addWidget(self.time_card)
        
        # 完成题目数
        self.problems_card = StatisticsCard("完成题目", "0题", "本周完成 0题", "#2196F3")
        cards_layout.addWidget(self.problems_card)
        
        # 平均分数
        self.score_card = StatisticsCard("平均分数", "0分", "较上周 +0分", "#FF9800")
        cards_layout.addWidget(self.score_card)
        
        # 连续学习天数
        self.streak_card = StatisticsCard("连续学习", "0天", "保持良好习惯", "#9C27B0")
        cards_layout.addWidget(self.streak_card)
        
        layout.addLayout(cards_layout)
    
    def load_statistics(self):
        """加载统计数据"""
        try:
            # 这里应该从API获取真实数据
            # 为了演示，使用模拟数据
            
            # 更新统计卡片
            self.time_card.update_value("45小时", "本月增加 12小时")
            self.problems_card.update_value("128题", "本周完成 15题")
            self.score_card.update_value("82.5分", "较上周 +3.2分")
            self.streak_card.update_value("12天", "保持良好习惯")
            
        except Exception as e:
            print(f"加载统计数据失败: {e}")
    
    def refresh_data(self):
        """刷新所有数据"""
        try:
            # 刷新统计卡片
            self.load_statistics()
            
            # 刷新图表
            self.progress_chart.load_data()
            self.category_chart.load_data()
            self.score_chart.load_data()
            self.heatmap_chart.load_data()
            
            # 刷新表格
            self.stats_table.load_data()
            
            print("数据刷新完成")
            
        except Exception as e:
            print(f"刷新数据失败: {e}")
    
    def on_time_range_changed(self, time_range: str):
        """时间范围改变处理"""
        print(f"时间范围改变为: {time_range}")
        # 这里可以根据时间范围重新加载数据
        self.refresh_data()
    
    def export_report(self):
        """导出统计报告"""
        try:
            from PyQt6.QtWidgets import QFileDialog, QMessageBox
            
            file_path, _ = QFileDialog.getSaveFileName(
                self, "导出统计报告",
                f"analytics_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                "PDF文件 (*.pdf);;Excel文件 (*.xlsx);;文本文件 (*.txt)"
            )
            
            if file_path:
                # 这里应该生成实际的报告文件
                # 为了演示，只是显示成功消息
                QMessageBox.information(self, "成功", f"统计报告已导出到:\n{file_path}")
                
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "错误", f"导出报告失败: {str(e)}")
    
    def closeEvent(self, event):
        """页面关闭事件"""
        if hasattr(self, 'refresh_timer'):
            self.refresh_timer.stop()
        event.accept()