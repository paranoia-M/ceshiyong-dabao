import random
import math
import time
from datetime import datetime
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFrame, QGridLayout, QProgressBar, QScrollArea, 
                             QTableWidget, QTableWidgetItem, QHeaderView, QPushButton)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QRect, QPoint, QSize
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QLinearGradient, QPolygon

# --- 核心算法层 ---

class MatrixAnalyticsEngine:
    """
    文化内容传播影响力评估算法引擎
    算法逻辑：多维加权衰减模型 (Multi-dimensional Weighted Decay Model)
    """
    @staticmethod
    def calculate_influence(metrics: dict):
        # 权重定义
        w_depth = 0.35    # 内容深度
        w_novelty = 0.25  # 创新度
        w_reach = 0.20    # 覆盖范围
        w_interact = 0.20 # 交互率
        
        # 基础分
        base_score = (metrics['depth'] * w_depth + 
                      metrics['novelty'] * w_novelty + 
                      metrics['reach'] * w_reach + 
                      metrics['interact'] * w_interact)
        
        # 引入时间衰减因子 (模拟发布后随着时间推移的传播衰减)
        t = metrics.get('hours_passed', 1)
        decay = math.exp(-0.02 * t)
        
        # 引入波动噪声模拟真实环境
        noise = random.uniform(0.95, 1.05)
        
        return round(base_score * decay * noise * 10, 2)

# --- 自定义可视化组件 ---

class InfluenceRadarWidget(QWidget):
    """自定义雷达图：展示内容指标分布"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(300, 300)
        self.data = [80, 70, 90, 65, 85] # 深度, 创新, 覆盖, 互动, 品牌
        self.labels = ["Depth", "Novelty", "Reach", "Interaction", "Brand"]

    def update_data(self, new_data):
        self.data = new_data
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        center = QPoint(self.width() // 2, self.height() // 2)
        radius = min(self.width(), self.height()) // 2 - 40
        
        # 绘制背景网格
        painter.setPen(QPen(QColor(51, 65, 85, 100), 1))
        for i in range(1, 5):
            r = radius * i // 4
            painter.drawEllipse(center, r, r)
            
        # 绘制轴线
        angles = [i * 72 - 90 for i in range(5)]
        for angle in angles:
            rad = math.radians(angle)
            end_point = QPoint(
                int(center.x() + radius * math.cos(rad)),
                int(center.y() + radius * math.sin(rad))
            )
            painter.drawLine(center, end_point)

        # 绘制数据区域
        polygon = QPolygon()
        for i, val in enumerate(self.data):
            rad = math.radians(angles[i])
            dist = radius * val // 100
            p = QPoint(
                int(center.x() + dist * math.cos(rad)),
                int(center.y() + dist * math.sin(rad))
            )
            polygon.append(p)
            
        painter.setPen(QPen(QColor(56, 189, 248), 2))
        painter.setBrush(QBrush(QColor(56, 189, 248, 80)))
        painter.drawPolygon(polygon)

class LiveTrendThread(QThread):
    """后台模拟数据流接入线程"""
    data_received = pyqtSignal(dict)

    def run(self):
        while True:
            # 模拟系统抓取到的全网热点波动
            stats = {
                'active_users': random.randint(1000, 5000),
                'system_load': random.randint(20, 45),
                'influence_index': random.uniform(70, 95),
                'timestamp': datetime.now().strftime("%H:%M:%S")
            }
            self.data_received.emit(stats)
            time.sleep(2)

# --- 主界面入口 ---

class EntryWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("DashboardModule")
        self.init_ui()
        self.start_engine()

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(25)

        # 1. 顶部指标栏
        header_layout = QHBoxLayout()
        self.cards = {
            "Total_Influence": self._create_stat_card("全网核心影响力指数", "0.00", "#38bdf8"),
            "Active_Projects": self._create_stat_card("活跃内容策划案", "24", "#4ade80"),
            "Asset_Valuation": self._create_stat_card("数字资产估值 (￥)", "1.2M", "#fbbf24"),
            "System_Uptime": self._create_stat_card("引擎运行时间", "724h", "#f43f5e")
        }
        for card in self.cards.values():
            header_layout.addWidget(card)
        self.main_layout.addLayout(header_layout)

        # 2. 中间混合展示区 (可视化 + 列表)
        middle_layout = QHBoxLayout()
        
        # 左侧：数据可视化容器
        viz_frame = QFrame()
        viz_frame.setStyleSheet("background: #ffffff; border-radius: 12px; border: 1px solid #e2e8f0;")
        viz_layout = QVBoxLayout(viz_frame)
        
        viz_header = QLabel("内容维度分析矩阵")
        viz_header.setStyleSheet("font-weight: bold; font-size: 16px; color: #1e293b;")
        viz_layout.addWidget(viz_header)
        
        self.radar = InfluenceRadarWidget()
        viz_layout.addWidget(self.radar, 1, Qt.AlignmentFlag.AlignCenter)
        
        middle_layout.addWidget(viz_frame, 2)

        # 右侧：核心任务监控
        task_frame = QFrame()
        task_frame.setStyleSheet("background: #ffffff; border-radius: 12px; border: 1px solid #e2e8f0;")
        task_layout = QVBoxLayout(task_frame)
        
        task_header = QHBoxLayout()
        th_label = QLabel("高优先级分发计划")
        th_label.setStyleSheet("font-weight: bold; font-size: 16px; color: #1e293b;")
        th_btn = QPushButton("管理全案")
        th_btn.setFixedWidth(80)
        th_btn.setStyleSheet("background: #f1f5f9; font-size: 11px; border-radius: 4px;")
        task_header.addWidget(th_label)
        task_header.addWidget(th_btn)
        task_layout.addLayout(task_header)

        self.task_table = QTableWidget(10, 3)
        self.task_table.setHorizontalHeaderLabels(["策划案名称", "影响力预估", "状态"])
        self.task_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.task_table.setFrameShape(QFrame.Shape.NoFrame)
        self.task_table.verticalHeader().setVisible(False)
        self._populate_tasks()
        
        task_layout.addWidget(self.task_table)
        middle_layout.addWidget(task_frame, 3)

        self.main_layout.addLayout(middle_layout, 3)

        # 3. 底部实时志与系统资源
        bottom_layout = QHBoxLayout()
        
        self.log_area = QScrollArea()
        self.log_area.setWidgetResizable(True)
        self.log_area.setMinimumHeight(150)
        self.log_area.setStyleSheet("background: #0f172a; border-radius: 8px;")
        
        self.log_container = QWidget()
        self.log_vbox = QVBoxLayout(self.log_container)
        self.log_vbox.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.log_area.setWidget(self.log_container)
        
        bottom_layout.addWidget(self.log_area, 3)
        
        # 引擎负载监控
        load_frame = QFrame()
        load_frame.setFixedWidth(300)
        load_frame.setStyleSheet("background: white; border-radius: 8px; border: 1px solid #e2e8f0;")
        load_layout = QVBoxLayout(load_frame)
        load_layout.addWidget(QLabel("引擎负载"))
        self.load_bar = QProgressBar()
        self.load_bar.setStyleSheet("QProgressBar::chunk { background-color: #38bdf8; }")
        load_layout.addWidget(self.load_bar)
        load_layout.addStretch()
        
        bottom_layout.addWidget(load_frame, 1)
        
        self.main_layout.addLayout(bottom_layout, 1)

    def _create_stat_card(self, title, value, color):
        card = QFrame()
        card.setObjectName("StatCard")
        card.setStyleSheet(f"""
            QFrame#StatCard {{
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
                padding: 15px;
            }}
        """)
        l = QVBoxLayout(card)
        t = QLabel(title)
        t.setStyleSheet("color: #64748b; font-size: 13px; font-weight: 500;")
        v = QLabel(value)
        v.setStyleSheet(f"color: {color}; font-size: 28px; font-weight: 800; margin-top: 5px;")
        l.addWidget(t)
        l.addWidget(v)
        return card

    def _populate_tasks(self):
        projects = [
            ("丝绸之路数字展览", 92.5), ("三星堆VR体验", 88.0), 
            ("唐风美学短视频", 76.4), ("故宫节气画册", 82.1),
            ("莫高窟壁画数字化", 95.8)
        ]
        for i, (name, score) in enumerate(projects):
            self.task_table.setItem(i, 0, QTableWidgetItem(name))
            self.task_table.setItem(i, 1, QTableWidgetItem(f"{score} pts"))
            status = QTableWidgetItem("执行中")
            status.setForeground(QColor("#059669"))
            self.task_table.setItem(i, 2, status)

    def start_engine(self):
        """开启异步监控引擎"""
        self.thread = LiveTrendThread()
        self.thread.data_received.connect(self.update_dashboard)
        self.thread.start()

    def update_dashboard(self, stats):
        """实时更新界面数据逻辑"""
        # 更新核心指数（带算法计算）
        influence = MatrixAnalyticsEngine.calculate_influence({
            'depth': 90, 'novelty': 85, 'reach': stats['active_users']/50, 'interact': 75
        })
        
        # 查找对应卡片里的标签并更新
        # 注意：card布局结构是 [title, value]
        val_label = self.cards["Total_Influence"].findChildren(QLabel)[1]
        val_label.setText(str(influence))
        
        # 更新进度条
        self.load_bar.setValue(stats['system_load'])
        
        # 刷新雷达图
        new_data = [random.randint(60, 95) for _ in range(5)]
        self.radar.update_data(new_data)
        
        # 打印日志
        log_item = QLabel(f"[{stats['timestamp']}] 接入外部节点信号: 用户增量 {random.randint(5, 50)} | 数据校验通过")
        log_item.setStyleSheet("color: #10b981; font-family: 'Consolas'; font-size: 11px;")
        self.log_vbox.insertWidget(0, log_item)
        
        # 限制日志显示数量防止内存溢出
        if self.log_vbox.count() > 30:
            item = self.log_vbox.takeAt(self.log_vbox.count() - 1)
            if item.widget(): item.widget().deleteLater()

    def __del__(self):
        if hasattr(self, 'thread'):
            self.thread.terminate()
            self.thread.wait()