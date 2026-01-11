import sys
import random
import math
import time
from datetime import datetime, timedelta

# 彻底补全所有可能用到的 PyQt6 组件
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, 
    QHeaderView, QSplitter, QComboBox, QProgressBar, 
    QScrollArea, QGroupBox, QFormLayout, QStackedWidget, 
    QMessageBox, QAbstractItemView, QSizePolicy, QListWidget, 
    QListWidgetItem, QTabWidget, QToolBar, QTextEdit, QSlider
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QRect, QPoint, QTimer
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QLinearGradient, QPolygon

# --- 核心业务逻辑层：情感共振分析引擎 ---

class FeedbackIntelligence:
    """
    用户反馈智能分析引擎
    核心算法：基于语义权重的共振归因模型 (SRM)
    """
    # 关键词共振矩阵映射
    RESONANCE_MAP = {
        "艺术审美": ["精美", "画质", "视觉", "构图", "审美", "特效"],
        "历史还原": ["考究", "史实", "严谨", "还原", "致敬", "深度"],
        "交互设计": ["流畅", "体验", "操作", "玩法", "UI", "性能"]
    }

    @staticmethod
    def analyze_feedback(text: str):
        """
        核心推演逻辑：从非结构化文本中提取情感极性与归因维度
        """
        # 1. 模拟情感分析 (0.0 - 1.0)
        # 逻辑：根据文本长度和随机扰动模拟
        sentiment_base = 0.5 + (len(text) % 10) * 0.04
        sentiment_score = round(min(0.98, sentiment_base * random.uniform(0.8, 1.1)), 2)
        
        # 2. 归因推演：匹配共振维度
        dimensions = {"艺术审美": 0, "历史还原": 0, "交互设计": 0}
        for dim, keywords in FeedbackIntelligence.RESONANCE_MAP.items():
            match_count = sum(1 for k in keywords if k in text)
            dimensions[dim] = match_count * 25 + random.randint(0, 20)
        
        # 3. 计算综合共振指数 (CRI)
        # Formula: CRI = Sentiment * (Max_Dimension_Weight * 0.7 + Average_Dimensions * 0.3)
        max_val = max(dimensions.values())
        avg_val = sum(dimensions.values()) / 3
        cri = sentiment_score * (max_val * 0.7 + avg_val * 0.3)
        
        return {
            "sentiment": sentiment_score,
            "dimensions": dimensions,
            "resonance_index": round(min(100, cri), 2),
            "primary_focus": max(dimensions, key=dimensions.get)
        }

# --- 数据模型实体 ---

class UserFeedbackNode:
    """反馈数据实体，封装用户特征与算法推演结果"""
    def __init__(self, user, platform, text):
        self.fid = f"FBK-{int(time.time() % 100000)}-{random.randint(10, 99)}"
        self.user = user
        self.platform = platform # 抖音, B站, 小红书, 系统内测
        self.raw_text = text
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # 触发算法初始化
        self.analysis = FeedbackIntelligence.analyze_feedback(text)
        self.status = "待处理" # 待处理, 已回复, 已归档
        self.op_logs = [f"{self.timestamp} 系统自动执行 NLP 语义提取与共振归因"]

# --- 自定义视觉组件：共振频谱仪 ---

class ResonanceSpectrum(QWidget):
    """自定义绘图：展示用户情感共振的波形频谱"""
    def __init__(self):
        super().__init__()
        self.setMinimumHeight(240)
        self.bars = [random.randint(20, 90) for _ in range(40)]
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._pulse_effect)
        self.timer.start(100)

    def _pulse_effect(self):
        # 模拟数据流脉冲波动
        self.bars.pop(0)
        self.bars.append(random.randint(20, 90))
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w, h = self.width(), self.height()
        p.fillRect(0, 0, w, h, QColor(15, 23, 42)) # 深色背景
        
        # 绘制动态频谱条
        margin = 40
        bar_w = (w - margin * 2) / len(self.bars)
        
        for i, val in enumerate(self.bars):
            x = margin + i * bar_w
            bar_h = (val / 100) * (h - 80)
            
            # 颜色逻辑：根据高度渐变
            color = QColor(56, 189, 248) if val < 70 else QColor(244, 63, 94)
            p.setBrush(QBrush(color))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawRect(int(x), int(h - 40 - bar_h), int(bar_w - 2), int(bar_h))

        p.setPen(QPen(QColor(148, 163, 184), 1))
        p.setFont(QFont("Consolas", 9))
        p.drawText(margin, 30, "LIVE FEEDBACK RESONANCE FLUX / 实时反馈共振能谱")

# --- 主模块界面实现 ---

class EntryWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.feedback_pool = []
        self.active_item = None
        self._seed_mock_data()
        self._init_ui_scaffold()

    def _seed_mock_data(self):
        users = ["数字漫游者", "历史守望者", "VR体验官", "文创爱好者_01"]
        platforms = ["抖音", "B站", "小红书", "系统内测"]
        texts = [
            "这次的故宫模型细节非常严谨，史实还原度极高，必须点赞！",
            "交互操作稍微有一点卡顿，视觉特效很精美但性能优化还需努力。",
            "画面构图很有中国画的审美，希望以后能多出这种高质量内容。",
            "感觉叙事逻辑有点断层，虽然特效拉满了但没看懂核心表达。"
        ]
        for _ in range(10):
            self.feedback_pool.append(UserFeedbackNode(random.choice(users), random.choice(platforms), random.choice(texts)))

    def _init_ui_scaffold(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # 1. 顶部操作矩阵
        self.header = QFrame()
        self.header.setFixedHeight(70)
        self.header.setStyleSheet("background: white; border-bottom: 1px solid #e2e8f0;")
        h_layout = QHBoxLayout(self.header)
        h_layout.setContentsMargins(20, 0, 20, 0)
        
        title_box = QVBoxLayout()
        title_main = QLabel("舆情反馈与共振管理")
        title_main.setStyleSheet("font-size: 18px; font-weight: 900; color: #1e293b;")
        title_sub = QLabel("SENTIMENT ANALYSIS & CULTURAL RESONANCE ENGINE")
        title_sub.setStyleSheet("font-size: 9px; color: #94a3b8; font-family: 'Consolas';")
        title_box.addStretch(); title_box.addWidget(title_main); title_box.addWidget(title_sub); title_box.addStretch()
        
        h_layout.addLayout(title_box)
        
        # 修复 QToolBar addStretch 问题：手动使用 Spacer
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        h_layout.addWidget(spacer)
        
        self.btn_sync = QPushButton("↻ 同步全网舆情")
        self.btn_sync.setFixedSize(140, 40)
        self.btn_sync.setStyleSheet("background: #0f172a; color: white; font-weight: bold; border-radius: 4px;")
        self.btn_sync.clicked.connect(self._handle_sync)
        h_layout.addWidget(self.btn_sync)
        
        self.layout.addWidget(self.header)

        # 2. 视觉监测组件
        self.spectrum = ResonanceSpectrum()
        self.layout.addWidget(self.spectrum)

        # 3. 核心交互视口
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setStyleSheet("QSplitter::handle { background: #e2e8f0; }")
        
        # --- 左侧：反馈队列 (Read) ---
        self.list_panel = QFrame()
        self.list_panel.setStyleSheet("background: white;")
        lp_layout = QVBoxLayout(self.list_panel)
        lp_layout.setContentsMargins(0, 0, 0, 0)
        
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["ID标识", "反馈用户", "来源", "共振指数"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.itemClicked.connect(self._load_detail_to_inspector)
        lp_layout.addWidget(self.table)
        
        self.splitter.addWidget(self.list_panel)

        # --- 右侧：智能处理工作台 (Update/Delete + Algorithm) ---
        self.inspector = QScrollArea()
        self.inspector.setWidgetResizable(True)
        self.inspector.setStyleSheet("background: white; border-left: 1px solid #e2e8f0;")
        
        self.ins_inner = QWidget()
        self.ins_layout = QVBoxLayout(self.ins_inner)
        self.ins_layout.setContentsMargins(25, 25, 25, 25)
        
        self.stack = QStackedWidget()
        self.empty_v = QLabel("请在左侧矩阵中选择一项反馈\n以启动情感共振推演与回复建议")
        self.empty_v.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_v.setStyleSheet("color: #94a3b8; font-style: italic;")
        
        self.work_v = self._build_work_view()
        
        self.stack.addWidget(self.empty_v)
        self.stack.addWidget(self.work_v)
        self.ins_layout.addWidget(self.stack)
        
        self.inspector.setWidget(self.ins_inner)
        self.splitter.addWidget(self.inspector)
        
        self.splitter.setStretchFactor(0, 3)
        self.splitter.setStretchFactor(1, 2)
        self.layout.addWidget(self.splitter)
        
        self._sync_table_view()

    def _build_work_view(self):
        """构建详细的反馈处理界面"""
        view = QWidget()
        l = QVBoxLayout(view)
        l.setSpacing(20)

        # A. 原始数据 (Read Only)
        group_raw = QGroupBox("反馈原始上下文")
        rl = QVBoxLayout(group_raw)
        self.txt_raw = QTextEdit()
        self.txt_raw.setReadOnly(True)
        self.txt_raw.setFixedHeight(80)
        self.txt_raw.setStyleSheet("background: #f8fafc; color: #475569;")
        rl.addWidget(self.txt_raw)
        l.addWidget(group_raw)

        # B. 算法诊断看板 (Algorithm Result Visualization)
        group_algo = QGroupBox("算法诊断与归因分析")
        al = QVBoxLayout(group_algo)
        
        self.prog_res = QProgressBar()
        self.prog_res.setStyleSheet("QProgressBar::chunk { background: #0ea5e9; }")
        al.addWidget(QLabel("综合共振强度 (CRI):"))
        al.addWidget(self.prog_res)
        
        self.lbl_attr = QLabel("核心归因维度: --")
        self.lbl_attr.setStyleSheet("font-weight: bold; color: #0369a1; padding: 5px;")
        al.addWidget(self.lbl_attr)
        l.addWidget(group_algo)

        # C. 响应决策 (Update 逻辑)
        group_action = QGroupBox("系统建议响应策略")
        cl = QVBoxLayout(group_action)
        self.txt_reply = QTextEdit()
        self.txt_reply.setPlaceholderText("根据算法建议，请在此拟写回复...")
        self.txt_reply.setFixedHeight(100)
        cl.addWidget(self.txt_reply)
        l.addWidget(group_action)

        # D. 操作持久化
        op_row = QHBoxLayout()
        btn_apply = QPushButton("💾 提交回复并归档"); btn_apply.setFixedHeight(45)
        btn_apply.setStyleSheet("background: #0ea5e9; color: white; font-weight: bold;")
        btn_apply.clicked.connect(self._handle_commit_feedback)
        
        btn_trash = QPushButton("忽略"); btn_trash.setFixedWidth(70); btn_trash.setFixedHeight(45)
        btn_trash.clicked.connect(self._handle_delete_node)
        
        op_row.addWidget(btn_trash); op_row.addWidget(btn_apply)
        l.addLayout(op_row)
        
        l.addStretch()
        return view

    # --- 交互处理器与逻辑引擎 ---

    def _sync_table_view(self):
        """同步内存数据库至界面表格"""
        self.table.setRowCount(0)
        for i, node in enumerate(self.feedback_pool):
            self.table.insertRow(i)
            self.table.setItem(i, 0, QTableWidgetItem(node.fid))
            self.table.setItem(i, 1, QTableWidgetItem(node.user))
            self.table.setItem(i, 2, QTableWidgetItem(node.platform))
            
            cri_item = QTableWidgetItem(f"{node.analysis['resonance_index']}%")
            # 根据共振强度着色
            if node.analysis['resonance_index'] > 80: cri_item.setForeground(QColor("#ef4444"))
            elif node.analysis['resonance_index'] > 50: cri_item.setForeground(QColor("#0ea5e9"))
            
            self.table.setItem(i, 3, cri_item)

    def _load_detail_to_inspector(self, item_widget):
        """加载选中项的数据至工作台 (Read)"""
        row = item_widget.row()
        fid = self.table.item(row, 0).text()
        node = next((n for n in self.feedback_pool if n.fid == fid), None)
        
        if node:
            self.active_item = node
            self.stack.setCurrentIndex(1)
            # 更新 UI
            self.txt_raw.setText(node.raw_text)
            self.prog_res.setValue(int(node.analysis['resonance_index']))
            self.lbl_attr.setText(f"核心归归因维度: {node.analysis['primary_focus']}")
            
            # 生成模拟回复建议
            suggest = f"感谢您对项目[{node.analysis['primary_focus']}]维度的关注，我们会持续优化相关内容。"
            self.txt_reply.setText(suggest)

    def _handle_commit_feedback(self):
        """CRUD - Update 持久化模拟"""
        if self.active_item:
            self.active_item.status = "已回复"
            self.active_item.op_logs.append(f"{datetime.now().strftime('%H:%M')} 执行回复决策并执行归档")
            QMessageBox.information(self, "执行成功", f"反馈项 {self.active_item.fid} 已处理并进入历史库。")
            self.feedback_pool.remove(self.active_item) # 模拟从待办移出
            self.active_item = None
            self.stack.setCurrentIndex(0)
            self._sync_table_view()

    def _handle_delete_node(self):
        """CRUD - Delete 忽略反馈"""
        if self.active_item:
            self.feedback_pool.remove(self.active_item)
            self.active_item = None
            self.stack.setCurrentIndex(0)
            self._sync_table_view()

    def _handle_sync(self):
        """模拟外部接口同步逻辑"""
        self.btn_sync.setEnabled(False)
        self.btn_sync.setText("同步中...")
        QTimer.singleShot(1500, self._finalize_sync)

    def _finalize_sync(self):
        # 增加新模拟数据 (Create)
        new_node = UserFeedbackNode("外部用户_X", "API接口", "内容非常考究，视觉震撼。")
        self.feedback_pool.insert(0, new_node)
        self._sync_table_view()
        self.btn_sync.setEnabled(True)
        self.btn_sync.setText("↻ 同步全网舆情")
        QMessageBox.information(self, "同步成功", "已从分发链路抓取到新的用户共振数据。")

    def __del__(self):
        pass