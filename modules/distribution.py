import sys
import json
import random
import math
import time
from datetime import datetime

# 彻底检查并补全所有组件导入
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, 
    QHeaderView, QSplitter, QComboBox, QCheckBox, 
    QProgressBar, QScrollArea, QFileDialog, QMenu,
    QGridLayout, QToolBar, QStatusBar, QDialog, QFormLayout,
    QGroupBox, QTabWidget, QTextEdit, QListWidget, QListWidgetItem,
    QAbstractItemView, QSpinBox, QSlider, QStackedWidget,
    QMessageBox, QSizePolicy
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QRect, QPoint, QTimer
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QLinearGradient, QPolygon

# --- 核心业务逻辑：多维传播扩散仿真引擎 ---

class DistributionMatrixEngine:
    """
    分发矩阵传播仿真算法
    逻辑：基于非线性衰减模型预测内容在跨平台组合下的覆盖能力
    """
    PLATFORM_DATA = {
        "微信公众号": {"reach": 0.45, "depth": 0.90, "viral": 1.1},
        "抖音/视频号": {"reach": 0.98, "depth": 0.30, "viral": 2.8},
        "Bilibili": {"reach": 0.70, "depth": 0.75, "viral": 1.9},
        "小红书": {"reach": 0.85, "depth": 0.55, "viral": 1.6},
        "知乎专栏": {"reach": 0.35, "depth": 0.85, "viral": 1.2}
    }

    @staticmethod
    def run_projection(platform, budget, content_score):
        """
        核心推演算法
        算法因子：预算(B), 内容评分(Q), 平台覆盖系数(R), 病毒传播指数(V)
        Result = (B^0.8) * R * (Q^1.6) * V
        """
        cfg = DistributionMatrixEngine.PLATFORM_DATA.get(platform, {"reach": 0.5, "depth": 0.5, "viral": 1.0})
        
        # 模拟预算投入的边际递减效应
        investment_power = math.pow(max(1, budget), 0.78)
        # 内容质量作为传播的加速计
        quality_multiplier = math.pow(content_score / 50.0, 1.7)
        
        raw_reach = investment_power * cfg['reach'] * quality_multiplier * cfg['viral'] * 120
        # 计算预估互动量 (基于内容深度系数)
        engagement = raw_reach * cfg['depth'] * random.uniform(0.1, 0.2)
        
        return {
            "reach": round(raw_reach, 0),
            "engagement": round(engagement, 0),
            "roi": round((raw_reach * 0.45) / max(1, budget), 2),
            "viral_score": round(cfg['viral'] * (content_score / 100) * 10, 1)
        }

# --- 数据实体模型 ---

class ChannelNode:
    """分发渠道节点实体"""
    def __init__(self, platform, account):
        self.uid = f"NODE-{int(time.time() % 100000)}-{random.randint(10, 99)}"
        self.platform = platform
        self.account = account
        self.health_index = random.randint(70, 98) # 渠道健康度
        self.status = "ACTIVE"
        self.last_sync = datetime.now().strftime("%Y-%m-%d")
        self.total_impact = random.randint(10000, 1000000) # 历史累计影响
        self.audit_history = [f"{self.last_sync} 节点成功接入数字文化分发总仓"]

# --- 自定义可视化组件 ---

class EfficiencyRadar(QWidget):
    """自定义雷达图组件：展示分发效能维度"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(300)
        self.data_points = [60, 60, 60, 60, 60]
        self.dim_labels = ["覆盖范围", "内容深度", "互动强度", "转化效率", "传播速度"]

    def update_data(self, new_points):
        self.data_points = new_points
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w, h = self.width(), self.height()
        cx, cy = int(w / 2), int(h / 2)
        radius = min(w, h) / 2 - 60
        
        # 1. 绘制背景蛛网
        p.setPen(QPen(QColor(226, 232, 240), 1))
        for level in range(1, 5):
            r = radius * (level / 4)
            poly = QPolygon()
            for i in range(5):
                angle = i * 72 - 90
                x = cx + r * math.cos(math.radians(angle))
                y = cy + r * math.sin(math.radians(angle))
                poly.append(QPoint(int(x), int(y)))
            p.drawPolygon(poly)

        # 2. 绘制数据遮罩
        data_poly = QPolygon()
        for i, val in enumerate(self.data_points):
            r = radius * (val / 100)
            angle = i * 72 - 90
            x = cx + r * math.cos(math.radians(angle))
            y = cy + r * math.sin(math.radians(angle))
            data_poly.append(QPoint(int(x), int(y)))
        
        p.setBrush(QBrush(QColor(14, 165, 233, 160)))
        p.setPen(QPen(QColor(14, 165, 233), 2))
        p.drawPolygon(data_poly)
        
        # 3. 绘制文字标签
        p.setPen(QPen(QColor(30, 41, 59)))
        p.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        for i, label in enumerate(self.dim_labels):
            angle = i * 72 - 90
            tx = cx + (radius + 35) * math.cos(math.radians(angle)) - 25
            ty = cy + (radius + 35) * math.sin(math.radians(angle)) + 5
            p.drawText(int(tx), int(ty), label)

# --- 主入口视窗 ---

class EntryWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.nodes = []
        self.current_focus = None
        self._seed_mock_data()
        self._init_ui_scaffold()

    def _seed_mock_data(self):
        platforms = list(DistributionMatrixEngine.PLATFORM_DATA.keys())
        accounts = ["官方文化号", "内容工作室A", "矩阵矩阵_01", "数字传播枢纽"]
        for p in platforms:
            self.nodes.append(ChannelNode(p, random.choice(accounts)))

    def _init_ui_scaffold(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # 1. 顶部专业工具栏 (解决布局重叠问题)
        self.header = QFrame()
        self.header.setFixedHeight(85)
        self.header.setStyleSheet("background: white; border-bottom: 1px solid #e2e8f0;")
        h_layout = QHBoxLayout(self.header)
        h_layout.setContentsMargins(25, 0, 25, 0)
        
        title_box = QVBoxLayout()
        title_main = QLabel("全网分发矩阵管理中心")
        title_main.setStyleSheet("font-size: 20px; font-weight: 900; color: #0f172a;")
        title_sub = QLabel("")
        title_sub.setStyleSheet("font-size: 10px; color: #64748b; letter-spacing: 1.5px;")
        title_box.addStretch()
        title_box.addWidget(title_main)
        title_box.addWidget(title_sub)
        title_box.addStretch()
        
        btn_add = QPushButton("＋ 接入新分发终端")
        btn_add.setFixedSize(160, 42)
        btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_add.setStyleSheet("""
            QPushButton {
                background-color: #0ea5e9;
                color: white;
                font-weight: bold;
                border-radius: 6px;
            }
            QPushButton:hover { background-color: #0284c7; }
        """)
        btn_add.clicked.connect(self._add_node_flow)

        h_layout.addLayout(title_box)
        h_layout.addStretch()
        h_layout.addWidget(btn_add)
        
        self.layout.addWidget(self.header)

        # 2. 核心工作视口
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setHandleWidth(1)
        self.splitter.setStyleSheet("QSplitter::handle { background: #e2e8f0; }")
        
        # --- 左侧：资产列表 ---
        self.list_view = QFrame()
        self.list_view.setStyleSheet("background: #f8fafc;")
        lv_layout = QVBoxLayout(self.list_view)
        lv_layout.setContentsMargins(15, 15, 15, 15)
        
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["ID标识", "平台", "账号名称", "健康指数"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("QTableWidget { border-radius: 8px; background: white; }")
        self.table.itemClicked.connect(self._select_node)
        lv_layout.addWidget(self.table)
        
        self.splitter.addWidget(self.list_view)

        # --- 右侧：智能编辑器 ---
        self.inspector_scroll = QScrollArea()
        self.inspector_scroll.setWidgetResizable(True)
        self.inspector_scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        self.inspector_inner = QWidget()
        self.ins_layout = QVBoxLayout(self.inspector_inner)
        self.ins_layout.setContentsMargins(25, 25, 25, 25)
        self.ins_layout.setSpacing(20)
        
        self._setup_inspector_stack()
        
        self.inspector_scroll.setWidget(self.inspector_inner)
        self.splitter.addWidget(self.inspector_scroll)
        
        self.splitter.setStretchFactor(0, 3)
        self.splitter.setStretchFactor(1, 2)
        self.layout.addWidget(self.splitter)
        
        self._sync_table()

    def _setup_inspector_stack(self):
        self.stack = QStackedWidget()
        
        # 空状态
        self.empty_page = QLabel("请从左侧选择一个分发端\n启动多维扩散仿真推演")
        self.empty_page.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_page.setStyleSheet("color: #94a3b8; font-style: italic; line-height: 150%;")
        
        # 编辑页
        self.edit_page = QWidget()
        ep_layout = QVBoxLayout(self.edit_page)
        ep_layout.setSpacing(25)

        # 1. 属性组
        group_meta = QGroupBox("分发终端配置")
        fl = QFormLayout(group_meta)
        fl.setSpacing(15)
        self.ui_platform = QComboBox()
        self.ui_platform.addItems(list(DistributionMatrixEngine.PLATFORM_DATA.keys()))
        self.ui_account = QLineEdit()
        self.ui_uid = QLineEdit(); self.ui_uid.setReadOnly(True)
        fl.addRow("分发目标平台:", self.ui_platform)
        fl.addRow("终端挂载账号:", self.ui_account)
        fl.addRow("系统唯一标识:", self.ui_uid)
        ep_layout.addWidget(group_meta)

        # 2. 仿真控制
        group_sim = QGroupBox("传播扩散仿真控制")
        sl = QVBoxLayout(group_sim)
        
        row_b = QHBoxLayout()
        row_b.addWidget(QLabel("投入预算(￥):"))
        self.sld_b = QSlider(Qt.Orientation.Horizontal)
        self.sld_b.setRange(500, 100000)
        self.sld_b.setValue(5000)
        self.lbl_b = QLabel("5000")
        self.sld_b.valueChanged.connect(lambda v: self.lbl_b.setText(f"{v}"))
        row_b.addWidget(self.sld_b); row_b.addWidget(self.lbl_b)
        
        row_q = QHBoxLayout()
        row_q.addWidget(QLabel("内容质量分:"))
        self.sld_q = QSlider(Qt.Orientation.Horizontal)
        self.sld_q.setRange(1, 100)
        self.sld_q.setValue(85)
        self.lbl_q = QLabel("85")
        self.sld_q.valueChanged.connect(lambda v: self.lbl_q.setText(f"{v}"))
        row_q.addWidget(self.sld_q); row_q.addWidget(self.lbl_q)
        
        sl.addLayout(row_b); sl.addLayout(row_q)
        self.btn_run = QPushButton("执行引擎推演")
        self.btn_run.setFixedHeight(45)
        self.btn_run.setStyleSheet("background: #0f172a; color: white; font-weight: bold; border-radius: 4px;")
        self.btn_run.clicked.connect(self._run_engine)
        sl.addWidget(self.btn_run)
        ep_layout.addWidget(group_sim)

        # 3. 可视化看板
        self.radar = EfficiencyRadar()
        ep_layout.addWidget(QLabel("推演效能矩阵:"))
        ep_layout.addWidget(self.radar)

        self.lbl_res = QLabel("等待执行推演算法...")
        self.lbl_res.setStyleSheet("background: #f0fdf4; color: #166534; padding: 20px; border-radius: 8px; font-weight: bold;")
        ep_layout.addWidget(self.lbl_res)

        # 4. 操作
        op_row = QHBoxLayout()
        btn_save = QPushButton("💾 保存配置"); btn_save.setFixedHeight(40)
        btn_save.clicked.connect(self._save_node)
        btn_del = QPushButton("销毁链接"); btn_del.setFixedWidth(80)
        btn_del.clicked.connect(self._delete_node)
        op_row.addWidget(btn_del); op_row.addWidget(btn_save)
        ep_layout.addLayout(op_row)
        ep_layout.addStretch()

        self.stack.addWidget(self.empty_page)
        self.stack.addWidget(self.edit_page)
        self.ins_layout.addWidget(self.stack)

    def _sync_table(self):
        self.table.setRowCount(0)
        for i, node in enumerate(self.nodes):
            self.table.insertRow(i)
            self.table.setItem(i, 0, QTableWidgetItem(node.uid))
            self.table.setItem(i, 1, QTableWidgetItem(node.platform))
            self.table.setItem(i, 2, QTableWidgetItem(node.account))
            
            h_item = QTableWidgetItem(f"{node.health_index}%")
            if node.health_index > 85: h_item.setForeground(QColor("#10b981"))
            self.table.setItem(i, 3, h_item)

    def _select_node(self, item):
        row = item.row()
        uid = self.table.item(row, 0).text()
        self.current_focus = next((n for n in self.nodes if n.uid == uid), None)
        
        if self.current_focus:
            self.stack.setCurrentIndex(1)
            self.ui_platform.setCurrentText(self.current_focus.platform)
            self.ui_account.setText(self.current_focus.account)
            self.ui_uid.setText(self.current_focus.uid)
            self._run_engine()

    def _run_engine(self):
        if not self.current_focus: return
        
        res = DistributionMatrixEngine.run_projection(
            self.ui_platform.currentText(),
            self.sld_b.value(),
            self.sld_q.value()
        )
        
        self.lbl_res.setText(f"预估总覆盖: {res['reach']:,}\n预估总互动: {res['engagement']:,}\n系统 ROI: {res['roi']}")
        
        # 映射雷达图得分
        scores = [
            min(100, res['reach'] / 400),
            70 + random.randint(-10, 20),
            min(100, res['engagement'] / 50),
            min(100, res['roi'] * 12),
            random.randint(60, 95)
        ]
        self.radar.update_data(scores)

    def _save_node(self):
        if self.current_focus:
            self.current_focus.platform = self.ui_platform.currentText()
            self.current_focus.account = self.ui_account.text()
            self._sync_table()
            QMessageBox.information(self, "成功", "分发端配置已持久化。")

    def _add_node_flow(self):
        new_node = ChannelNode("微信公众号", "新分发节点")
        self.nodes.insert(0, new_node)
        self._sync_table()
        QMessageBox.information(self, "提示", "新分发链路已建立。")

    def _delete_node(self):
        if self.current_focus:
            ans = QMessageBox.question(self, "危险操作", f"确定注销分发节点 {self.current_focus.uid} 吗？")
            if ans == QMessageBox.StandardButton.Yes:
                self.nodes.remove(self.current_focus)
                self.current_focus = None
                self.stack.setCurrentIndex(0)
                self._sync_table()