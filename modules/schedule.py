import sys
import random
import time
import math
from datetime import datetime, timedelta

# 严谨导入所有必要的组件，彻底解决 NameError
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, 
    QHeaderView, QSplitter, QComboBox, QProgressBar, 
    QScrollArea, QTimeEdit, QCalendarWidget, QGroupBox, 
    QFormLayout, QStackedWidget, QMessageBox, QAbstractItemView,
    QSizePolicy, QListWidget, QListWidgetItem, QTabWidget, QSlider
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QRect, QPoint, QTimer, QTime, QDate
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QLinearGradient, QPolygon

# --- 核心调度逻辑引擎：流量脉冲同步 (CPS) ---

class ChronosPulseEngine:
    """
    内容排期与流量对齐引擎
    核心算法：基于高斯分布的多峰流量共振模型
    """
    def __init__(self):
        # 预设不同分发平台的 24 小时流量波峰中心 (小时)
        self.peak_matrix = {
            "抖音/TikTok": [12.5, 18.0, 21.5, 23.5],
            "Bilibili": [12.0, 19.5, 22.0],
            "WeChat/朋友圈": [8.5, 12.0, 17.0, 21.0],
            "小红书/RED": [10.0, 18.5, 22.5]
        }

    def calculate_resonance(self, platform, qtime_obj: QTime):
        """
        算法核心：计算特定时间点与平台流量峰值的拟合程度
        逻辑：f(t) = exp(-(t - peak)^2 / 2σ^2)
        """
        # 修复：直接使用 qtime_obj.hour() 和 minute()，不使用不存在的 .time 属性
        hour_float = qtime_obj.hour() + qtime_obj.minute() / 60.0
        peaks = self.peak_matrix.get(platform, [12.0, 20.0])
        
        sigma = 1.25  # 流量衰减系数 (小时)
        max_fit = 0.0
        
        for p in peaks:
            # 计算最短循环距离 (处理 23:59 与 00:01 的临近性)
            dist = abs(hour_float - p)
            if dist > 12: dist = 24 - dist
            
            # 高斯共振反馈
            resonance = math.exp(-(dist**2) / (2 * sigma**2))
            max_fit = max(max_fit, resonance)
            
        return round(max_fit * 100, 2)

    def detect_collision_risk(self, target_node, pool):
        """
        逻辑：检测同一平台内多个排期任务的时序竞争风险
        标准：间距小于 90 分钟则视为高干扰
        """
        warnings = []
        t_val = target_node.exec_time.hour() + target_node.exec_time.minute() / 60.0
        
        for item in pool:
            if item.uid == target_node.uid: continue
            if item.platform == target_node.platform:
                item_val = item.exec_time.hour() + item.exec_time.minute() / 60.0
                diff = abs(t_val - item_val)
                if diff < 1.5:
                    warnings.append(f"时序过近：与 [{item.title}] 间隔仅 {round(diff*60)} 分钟")
        return warnings

# --- 排期节点实体 ---

class ScheduleNode:
    """封装单一排期条目的完整元数据与状态日志"""
    def __init__(self, title, platform, exec_time):
        self.uid = f"SCH-{int(time.time() % 100000)}-{random.randint(10, 99)}"
        self.title = title
        self.platform = platform
        self.exec_time = exec_time # QTime
        self.resonance_index = 0.0
        self.priority = random.choice(["核心/P0", "常规/P1", "补位/P2"])
        self.audit_logs = [f"{datetime.now().strftime('%H:%M:%S')} 节点排期初始建模"]

# --- 自定义视觉组件：脉冲监测波形 ---

class PulseWaveCanvas(QWidget):
    """自定义绘图：24小时流量波形仿真与实时排期点映射"""
    def __init__(self):
        super().__init__()
        self.setMinimumHeight(240)
        self.nodes_data = [] # 存储 (hour_float, score)

    def update_node_mapping(self, data):
        self.nodes_data = data
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w, h = self.width(), self.height()
        m_left, m_right = 60, 60
        canvas_w = w - m_left - m_right
        base_y = h - 60
        
        # 1. 绘制流量背景曲面 (模拟全网热度趋势)
        p.setPen(QPen(QColor(226, 232, 240), 2))
        path = QPolygon()
        for x in range(int(canvas_w)):
            hr = (x / canvas_w) * 24
            # 复合波形函数模拟真实的早中晚流量波峰
            y_offset = 30 * math.sin(hr * 0.25) + 25 * math.cos(hr * 0.5 - 2.5) + 60
            path.append(QPoint(int(m_left + x), int(base_y - y_offset)))
        p.drawPolyline(path)

        # 2. 时间轴刻度绘制
        p.setPen(QPen(QColor(148, 163, 184), 1))
        for tick in range(0, 25, 3):
            x = m_left + (tick / 24) * canvas_w
            p.drawLine(int(x), base_y, int(x), base_y + 8)
            p.drawText(int(x - 15), base_y + 25, f"{tick:02d}:00")

        # 3. 实时排期共振点映射
        for hr, score in self.nodes_data:
            x = m_left + (hr / 24) * canvas_w
            # 计算波形线上的 Y 轴位置保持视觉一致
            y_on_curve = 30 * math.sin(hr * 0.25) + 25 * math.cos(hr * 0.5 - 2.5) + 60
            
            # 视觉逻辑：高分蓝点，风险红点
            color = QColor(14, 165, 233) if score > 75 else QColor(244, 63, 94)
            p.setBrush(QBrush(color))
            p.setPen(QPen(Qt.GlobalColor.white, 2))
            p.drawEllipse(QPoint(int(x), int(base_y - y_on_curve)), 8, 8)
            
            p.setPen(QPen(color))
            p.drawText(int(x - 10), int(base_y - y_on_curve - 15), f"{int(score)}")

# --- 主模块：数字排期工作站 ---

class EntryWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.engine = ChronosPulseEngine()
        self.node_pool = []
        self.active_item = None
        self._seed_mock_repository()
        self._init_main_view()

    def _seed_mock_repository(self):
        """注入高仿真的业务初始数据"""
        plans = ["故宫数字创意大赛发布", "二十四节气：清明特辑", "三星堆3D文物修复记录", "非遗手工艺直播：苏绣"]
        platforms = ["抖音/TikTok", "Bilibili", "WeChat/朋友圈", "小红书/RED"]
        for _ in range(5):
            t = QTime(random.randint(9, 22), random.choice([0, 30]))
            n = ScheduleNode(random.choice(plans), random.choice(platforms), t)
            n.resonance_index = self.engine.calculate_resonance(n.platform, t)
            self.node_pool.append(n)

    def _init_main_view(self):
        self.root_layout = QVBoxLayout(self)
        self.root_layout.setContentsMargins(0, 0, 0, 0)
        self.root_layout.setSpacing(0)

        # 1. 顶部控制栏
        self.header = QFrame()
        self.header.setFixedHeight(75)
        self.header.setStyleSheet("background: white; border-bottom: 1px solid #e2e8f0; padding: 10px;")
        h_layout = QHBoxLayout(self.header)
        
        title_box = QVBoxLayout()
        m_title = QLabel("数字化排期调度矩阵 / Scheduling Matrix")
        m_title.setStyleSheet("font-size: 18px; font-weight: 900; color: #1e293b;")
        s_title = QLabel("SYSTEM CORE: PULSE SYNC ENGINE v1.2")
        s_title.setStyleSheet("font-size: 10px; color: #94a3b8; font-family: 'Consolas';")
        title_box.addWidget(m_title); title_box.addWidget(s_title)
        
        h_layout.addLayout(title_box)
        
        # 弹簧布局
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        h_layout.addWidget(spacer)
        
        self.btn_create = QPushButton("＋ 接入排期节点")
        self.btn_create.setFixedSize(150, 40)
        self.btn_create.setStyleSheet("background: #0ea5e9; color: white; font-weight: bold; border-radius: 4px;")
        self.btn_create.clicked.connect(self._handle_create_node)
        h_layout.addWidget(self.btn_create)
        
        self.root_layout.addWidget(self.header)

        # 2. 视觉监测看板
        self.pulse_canvas = PulseWaveCanvas()
        self.root_layout.addWidget(self.pulse_canvas)

        # 3. 核心交互视口
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setHandleWidth(1)
        
        # --- 左侧：排期列表队列 (CRUD - Read) ---
        self.list_panel = QFrame()
        self.list_panel.setStyleSheet("background: #f8fafc;")
        lp_layout = QVBoxLayout(self.list_panel)
        
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["节点ID", "内容方案", "目标平台", "时序位置", "共振指数"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.itemClicked.connect(self._load_node_to_inspector)
        lp_layout.addWidget(self.table)
        
        self.splitter.addWidget(self.list_panel)

        # --- 右侧：配置与算法推演面板 (CRUD - Update/Delete + Algorithm) ---
        self.inspector_scroll = QScrollArea()
        self.inspector_scroll.setWidgetResizable(True)
        self.inspector_inner = QWidget()
        self.ins_layout = QVBoxLayout(self.inspector_inner)
        self.ins_layout.setContentsMargins(25, 25, 25, 25)
        
        self.stack = QStackedWidget()
        self.empty_view = QLabel("请在左侧矩阵中定位一个节点\n以开启时序仿真与冲突扫描模式")
        self.empty_view.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_view.setStyleSheet("color: #94a3b8; font-style: italic;")
        
        self.detail_editor = self._build_detail_editor()
        
        self.stack.addWidget(self.empty_view)
        self.stack.addWidget(self.detail_editor)
        self.ins_layout.addWidget(self.stack)
        
        self.inspector_scroll.setWidget(self.inspector_inner)
        self.splitter.addWidget(self.inspector_scroll)
        
        self.splitter.setStretchFactor(0, 3)
        self.splitter.setStretchFactor(1, 2)
        self.root_layout.addWidget(self.splitter)
        
        self._sync_global_views()

    def _build_detail_editor(self):
        """构建复杂的排期分析编辑器组件"""
        w = QWidget()
        l = QVBoxLayout(w)
        l.setSpacing(20)

        # A. 基础属性编辑
        group_base = QGroupBox("节点排期校准")
        f = QFormLayout(group_base)
        f.setSpacing(15)
        self.ui_title = QLineEdit() # 修复：已包含导入
        self.ui_platform = QComboBox()
        self.ui_platform.addItems(["抖音/TikTok", "Bilibili", "WeChat/朋友圈", "小红书/RED"])
        self.ui_time = QTimeEdit()
        self.ui_time.timeChanged.connect(self._run_live_analysis) # 联动实时算法
        
        f.addRow("方案标题:", self.ui_title)
        f.addRow("分发渠道:", self.ui_platform)
        f.addRow("发布时间:", self.ui_time)
        l.addWidget(group_base)

        # B. 冲突预警矩阵
        self.collision_box = QFrame()
        self.collision_box.setStyleSheet("background: #fff1f2; border-radius: 8px; border: 1px solid #fda4af; padding: 15px;")
        cl = QVBoxLayout(self.collision_box)
        self.lbl_collision = QLabel("✅ 时序健康：未检测到明显平台冲突")
        self.lbl_collision.setStyleSheet("color: #be123c; font-weight: bold; font-size: 11px;")
        self.lbl_collision.setWordWrap(True)
        cl.addWidget(self.lbl_collision)
        l.addWidget(self.collision_box)

        # C. 拟合度仿真报告
        self.report_box = QGroupBox("CPS 引擎推演报告")
        rl = QVBoxLayout(self.report_box)
        self.lbl_score = QLabel("流量共振指数: -- %")
        self.lbl_score.setStyleSheet("font-size: 20px; font-weight: 800; color: #0369a1;")
        self.lbl_advice = QLabel("正在分析时序窗口...")
        self.lbl_advice.setWordWrap(True)
        self.lbl_advice.setStyleSheet("color: #475569; font-size: 12px; line-height: 150%;")
        rl.addWidget(self.lbl_score)
        rl.addWidget(self.lbl_advice)
        l.addWidget(self.report_box)

        # D. 持久化控制
        op_row = QHBoxLayout()
        btn_save = QPushButton("💾 提交排期校准")
        btn_save.setFixedHeight(45)
        btn_save.setStyleSheet("background: #0f172a; color: white; font-weight: bold;")
        btn_save.clicked.connect(self._handle_save_node)
        
        btn_del = QPushButton("撤销节点")
        btn_del.setFixedWidth(80); btn_del.setFixedHeight(45)
        btn_del.clicked.connect(self._handle_delete_node)
        
        op_row.addWidget(btn_del); op_row.addWidget(btn_save)
        l.addLayout(op_row)
        
        l.addStretch()
        return w

    # --- 交互处理器与逻辑流水线 ---

    def _sync_global_views(self):
        """同步全局数据至列表与绘图引擎"""
        self.table.setRowCount(0)
        canvas_points = []
        
        for i, node in enumerate(self.node_pool):
            self.table.insertRow(i)
            self.table.setItem(i, 0, QTableWidgetItem(node.uid))
            self.table.setItem(i, 1, QTableWidgetItem(node.title))
            self.table.setItem(i, 2, QTableWidgetItem(node.platform))
            self.table.setItem(i, 3, QTableWidgetItem(node.exec_time.toString("HH:mm")))
            
            # 拟合度着色逻辑
            s_item = QTableWidgetItem(f"{node.resonance_index}%")
            if node.resonance_index > 80: s_item.setForeground(QColor("#10b981"))
            self.table.setItem(i, 4, s_item)
            
            # 为画布准备数据点
            hr_float = node.exec_time.hour() + node.exec_time.minute() / 60.0
            canvas_points.append((hr_float, node.resonance_index))
            
        self.pulse_canvas.update_node_mapping(canvas_points)

    def _load_node_to_inspector(self, item):
        row = item.row()
        uid = self.table.item(row, 0).text()
        self.active_item = next((n for n in self.node_pool if n.uid == uid), None)
        
        if self.active_item:
            self.stack.setCurrentIndex(1)
            self.ui_title.setText(self.active_item.title)
            self.ui_platform.setCurrentText(self.active_item.platform)
            self.ui_time.setTime(self.active_item.exec_time)
            self._run_live_analysis()

    def _run_live_analysis(self):
        """业务核心：实时冲突检测与算法仿真推演"""
        if not self.active_item: return
        
        p = self.ui_platform.currentText()
        t = self.ui_time.time()
        
        # 1. 执行 CPS 引擎共振算法
        score = self.engine.calculate_resonance(p, t)
        self.lbl_score.setText(f"流量共振指数: {score} %")
        
        # 2. 实时扫描冲突矩阵
        dummy = ScheduleNode(self.ui_title.text(), p, t)
        dummy.uid = self.active_item.uid # 排除自身
        conflicts = self.engine.detect_collision_risk(dummy, self.node_pool)
        
        if conflicts:
            self.lbl_collision.setText("⚠️ 风险预警：\n" + "\n".join(conflicts))
            self.collision_box.setVisible(True)
        else:
            self.lbl_collision.setText("✅ 时序健康：当前发布窗口未检测到内部冲突")
            self.collision_box.setVisible(False)

        # 3. 动态建议生成
        if score > 85:
            self.lbl_advice.setText("智能排期建议：当前处于该平台流量爆发核心区。预计可获得最高权重的算法推荐位，建议立即锁定。")
        elif score > 65:
            self.lbl_advice.setText("智能排期建议：时序表现尚可。若能避开竞品高峰，可利用长尾流量实现稳定转化。")
        else:
            self.lbl_advice.setText("系统预警：当前时位处于平台流量洼地。建议延后至最近的脉冲峰值区（如 12:00 或 21:00）。")

    def _handle_save_node(self):
        """CRUD - Update: 数据同步与持久化"""
        if self.active_item:
            self.active_item.title = self.ui_title.text()
            self.active_item.platform = self.ui_platform.currentText()
            self.active_item.exec_time = self.ui_time.time()
            # 重新校准算法指数
            self.active_item.resonance_index = self.engine.calculate_resonance(
                self.active_item.platform, self.active_item.exec_time)
            
            self._sync_global_views()
            QMessageBox.information(self, "操作成功", f"排期节点 {self.active_item.uid} 的时序变更已同步至矩阵。")

    def _handle_create_node(self):
        """CRUD - Create: 接入新排期任务"""
        new_node = ScheduleNode("新数字化内容发布方案", "抖音/TikTok", QTime(12, 0))
        self.node_pool.insert(0, new_node)
        self._sync_global_views()
        QMessageBox.information(self, "执行成功", "新排期节点已成功挂载至调度矩阵。")

    def _handle_delete_node(self):
        """CRUD - Delete: 撤销排期任务"""
        if self.active_item:
            res = QMessageBox.question(self, "撤销确认", f"确定撤销排期任务 [{self.active_item.title}] 吗？\n撤销后该时位将被释放。")
            if res == QMessageBox.StandardButton.Yes:
                self.node_pool.remove(self.active_item)
                self.active_item = None
                self.stack.setCurrentIndex(0)
                self._sync_global_views()

    def resizeEvent(self, event):
        """响应式：窗口缩放后重新渲染脉冲画布"""
        super().resizeEvent(event)
        QTimer.singleShot(150, self._sync_global_views)

    def __del__(self):
        pass