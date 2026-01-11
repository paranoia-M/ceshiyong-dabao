import sys
import random
import math
import time
import hashlib
from datetime import datetime, timedelta

# 严谨导入所有必要的组件
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, 
    QHeaderView, QSplitter, QComboBox, QProgressBar, 
    QScrollArea, QGroupBox, QFormLayout, QStackedWidget, 
    QMessageBox, QAbstractItemView, QSizePolicy, QListWidget, 
    QListWidgetItem, QTabWidget, QToolBar, QMenu, QTextEdit,
    QSlider
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QRect, QPoint, QTimer, QThread
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QLinearGradient, QPolygon

# --- 核心业务逻辑层：版权感知哈希与风险推演引擎 ---

class CopyrightSecurityCore:
    """
    版权安全核心驱动引擎
    核心算法：基于内容感知哈希(pHash)模拟与多维风险扩散模型
    """
    @staticmethod
    def generate_fingerprint_dna(content_name: str):
        """算法：模拟生成数字版权指纹DNA"""
        salt = str(random.random()).encode()
        raw_hash = hashlib.sha256(content_name.encode() + salt).hexdigest()
        # 格式化为符合工业标准的指纹序列
        return f"SIG-{raw_hash[:6]}-{raw_hash[10:16]}-{raw_hash[-6:]}".upper()

    @staticmethod
    def run_risk_matrix_analysis(metrics: dict):
        """
        核心算法：多维权重侵权风险评估 (MWRM)
        维度：全网传播热度(H), 渠道开放性(O), 存证保护等级(P)
        公式：Risk = (H * 0.6 + O * 0.4) * exp(-P / 3.0)
        """
        h = metrics.get('heat', 50)
        o = metrics.get('openness', 50)
        p = metrics.get('prot_level', 3)
        
        # 基础风险值推演
        base_val = (h * 0.55 + o * 0.45)
        # 保护因子的非线性抑制作用
        suppression_factor = math.exp(-p / 2.5)
        
        # 环境扰动系数
        noise = random.uniform(0.9, 1.1)
        
        final_score = base_val * suppression_factor * noise
        return round(min(100, final_score), 2)

# --- 版权资产数据实体 ---

class CopyrightNode:
    """
    版权节点实体模型
    封装了指纹识别码、存证状态及风险因子
    """
    def __init__(self, title, category):
        self.uid = f"CPRT-{int(time.time() % 100000)}-{random.randint(100, 999)}"
        self.title = title
        self.category = category # 文物建模, 艺术影像, 民族音律, 数字档案
        self.fingerprint = CopyrightSecurityCore.generate_fingerprint_dna(self.title)
        self.reg_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # 修复：明确定义 status 属性，防止同步表格时报错
        self.status = "PROTECTED" # 状态：PROTECTED (受保护), ALERT (预警), BREACH (侵权确认)
        
        # 动态推演因子矩阵
        self.factors = {
            'heat': random.randint(20, 95),      # 全网流行热度
            'openness': random.randint(30, 90),  # 渠道分发开放度
            'prot_level': random.randint(1, 5)   # 保护强度等级
        }
        
        self.risk_index = CopyrightSecurityCore.run_risk_matrix_analysis(self.factors)
        self.detected_violations = random.randint(0, 15) # 疑似侵权数
        self.op_history = [f"{self.reg_timestamp} 成功执行链上指纹存证锚定"]

# --- 自定义视觉组件：动态全网扫描仪 ---

class GlobalRadarScanner(QWidget):
    """自定义绘图：模拟全网版权侵权扫描雷达界面"""
    def __init__(self):
        super().__init__()
        self.setMinimumHeight(300)
        self.angle = 0
        # 随机生成的疑似异常节点位置 (x, y)
        self.anomaly_nodes = [(random.randint(-130, 130), random.randint(-130, 130)) for _ in range(10)]
        
        # 驱动扫描动画的定时器
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self._step_animation)
        self.anim_timer.start(45)

    def _step_animation(self):
        self.angle = (self.angle + 5) % 360
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w, h = self.width(), self.height()
        cx, cy = int(w / 2), int(h / 2)
        radius = min(w, h) / 2 - 50
        
        # 1. 绘制雷达深色底座
        p.fillRect(0, 0, w, h, QColor(15, 23, 42))
        
        # 2. 绘制经纬网格线
        p.setPen(QPen(QColor(30, 41, 59), 1))
        p.drawEllipse(QPoint(cx, cy), radius, radius)
        p.drawEllipse(QPoint(cx, cy), int(radius * 0.65), int(radius * 0.65))
        p.drawEllipse(QPoint(cx, cy), int(radius * 0.35), int(radius * 0.35))
        p.drawLine(cx - radius, cy, cx + radius, cy)
        p.drawLine(cx, cy - radius, cx, cy + radius)

        # 3. 绘制扫描旋转扇形 (渐变效果)
        grad = QLinearGradient(cx, cy, 
                               cx + radius * math.cos(math.radians(self.angle)),
                               cy + radius * math.sin(math.radians(self.angle)))
        grad.setColorAt(0, QColor(14, 165, 233, 180)) # 科技蓝
        grad.setColorAt(1, QColor(14, 165, 233, 0))
        
        p.setBrush(QBrush(grad))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawPie(cx - radius, cy - radius, radius * 2, radius * 2, 
                  -self.angle * 16, 60 * 16)

        # 4. 绘制检测到的疑似异常点 (呼吸闪烁效果)
        p.setBrush(QBrush(QColor(244, 63, 94)))
        for nx, ny in self.anomaly_nodes:
            # 模拟只有在扫描线经过附近时才高亮显示的逻辑
            p.drawEllipse(cx + nx, cy + ny, 5, 5)

        # 5. 装饰性文本
        p.setPen(QPen(QColor(56, 189, 248)))
        p.setFont(QFont("Consolas", 10, QFont.Weight.Bold))
        p.drawText(30, 40, "STATUS: GLOBAL PIRACY SCANNING IN PROGRESS...")

# --- 主模块界面实现 ---

class EntryWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.repository = []
        self.focused_node = None
        self._seed_mock_data()
        self._init_main_scaffold()

    def _seed_mock_data(self):
        """初始化注入高仿真的业务数据"""
        titles = ["【莫高窟】数字拓扑资产包", "故宫VR互动场景(正式版)", "《山海经》4K动效采样", "昆曲非遗采样音源"]
        cats = ["文物建模", "艺术影像", "数字音频", "史料文档"]
        for _ in range(15):
            self.repository.append(CopyrightNode(random.choice(titles), random.choice(cats)))

    def _init_main_scaffold(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # 1. 顶部专业指令栏
        self.header = QFrame()
        self.header.setFixedHeight(75)
        self.header.setStyleSheet("background: white; border-bottom: 1px solid #e2e8f0; padding: 10px;")
        h_layout = QHBoxLayout(self.header)
        h_layout.setContentsMargins(25, 0, 25, 0)
        
        title_box = QVBoxLayout()
        title_main = QLabel("数字版权监控中心")
        title_main.setStyleSheet("font-size: 20px; font-weight: 900; color: #0f172a;")
        title_sub = QLabel("DNA FINGERPRINTING & BLOCKCHAIN ANCHORING")
        title_sub.setStyleSheet("font-size: 10px; color: #94a3b8; font-family: 'Consolas'; letter-spacing: 1px;")
        title_box.addStretch(); title_box.addWidget(title_main); title_box.addWidget(title_sub); title_box.addStretch()
        
        btn_action = QPushButton("＋ 发起版权存证")
        btn_action.setFixedSize(160, 42)
        btn_action.setStyleSheet("background: #0f172a; color: white; font-weight: bold; border-radius: 5px;")
        btn_action.clicked.connect(self._handle_create_node)

        h_layout.addLayout(title_box)
        
        # 弹簧占位
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        h_layout.addWidget(spacer)
        
        h_layout.addWidget(btn_action)
        self.main_layout.addWidget(self.header)

        # 2. 视觉看板区域
        self.radar = GlobalRadarScanner()
        self.main_layout.addWidget(self.radar)

        # 3. 核心交互区分割
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setHandleWidth(1)
        
        # --- 左侧：资产列表 (CRUD - Read) ---
        self.list_panel = QFrame()
        self.list_panel.setStyleSheet("background: white;")
        lp_layout = QVBoxLayout(self.list_panel)
        lp_layout.setContentsMargins(0, 0, 0, 0)
        
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["节点UID", "资产名称", "风险指数", "链上状态"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.itemClicked.connect(self._load_inspector_data)
        lp_layout.addWidget(self.table)
        
        self.splitter.addWidget(self.list_panel)

        # --- 右侧：深度推演面板 (CRUD - Update/Delete + Algorithm) ---
        self.inspector = QScrollArea()
        self.inspector.setWidgetResizable(True)
        self.inspector.setStyleSheet("background: white; border-left: 1px solid #e2e8f0;")
        self.ins_inner = QWidget()
        self.ins_layout = QVBoxLayout(self.ins_inner)
        self.ins_layout.setContentsMargins(25, 25, 25, 25)
        
        self.stack = QStackedWidget()
        self.empty_v = QLabel("请在左侧矩阵中选择一个版权节点\n开启数字DNA溯源与风险仿真推演")
        self.empty_v.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_v.setStyleSheet("color: #94a3b8; font-style: italic; line-height: 160%;")
        
        self.editor_v = self._build_editor_view()
        
        self.stack.addWidget(self.empty_v)
        self.stack.addWidget(self.editor_v)
        self.ins_layout.addWidget(self.stack)
        
        self.inspector.setWidget(self.ins_inner)
        self.splitter.addWidget(self.inspector)
        
        self.splitter.setStretchFactor(0, 3)
        self.splitter.setStretchFactor(1, 2)
        self.main_layout.addWidget(self.splitter)
        
        self._sync_global_table()

    def _build_editor_view(self):
        """构建复杂的推演编辑器与分析看板"""
        view = QWidget()
        l = QVBoxLayout(view)
        l.setSpacing(25)

        # A. 身份档案块 (Update 逻辑)
        group_meta = QGroupBox("存证身份档案")
        f = QFormLayout(group_meta)
        f.setSpacing(15)
        self.ui_title = QLineEdit()
        self.ui_uid = QLineEdit(); self.ui_uid.setReadOnly(True); self.ui_uid.setStyleSheet("background: #f8fafc;")
        self.ui_dna = QTextEdit(); self.ui_dna.setFixedHeight(65); self.ui_dna.setReadOnly(True)
        self.ui_dna.setStyleSheet("font-family: 'Consolas'; font-size: 11px; color: #0284c7; background: #f0f9ff;")
        f.addRow("版权主标题:", self.ui_title)
        f.addRow("系统唯一标识:", self.ui_uid)
        f.addRow("指纹DNA序列:", self.ui_dna)
        l.addWidget(group_meta)

        # B. 算法仿真滑块区 (Algorithm Interaction)
        group_algo = QGroupBox("风险因子动态仿真 (Simulation)")
        al = QVBoxLayout(group_algo)
        self.sliders = {}
        for key, name in [('heat', '传播流行热度'), ('openness', '渠道开放程度')]:
            row = QVBoxLayout()
            label_row = QHBoxLayout()
            label_row.addWidget(QLabel(name))
            v_lbl = QLabel("50")
            label_row.addWidget(v_lbl, 0, Qt.AlignmentFlag.AlignRight)
            row.addLayout(label_row)
            
            s = QSlider(Qt.Orientation.Horizontal); s.setRange(0, 100); s.setValue(50)
            s.valueChanged.connect(lambda v, lbl=v_lbl: lbl.setText(str(v)))
            row.addWidget(s)
            self.sliders[key] = s
            al.addLayout(row)
        
        self.btn_run_sim = QPushButton("执行引擎算法实时重估")
        self.btn_run_sim.setFixedHeight(45)
        self.btn_run_sim.setStyleSheet("background: #0f172a; color: white; font-weight: bold; border-radius: 4px;")
        self.btn_run_sim.clicked.connect(self._exec_risk_simulation)
        al.addWidget(self.btn_run_sim)
        l.addWidget(group_algo)

        # C. 诊断报告看板 (Visualization Feedback)
        self.report_box = QFrame()
        self.report_box.setStyleSheet("background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 20px;")
        rl = QVBoxLayout(self.report_box)
        self.lbl_score = QLabel("风险推演值: --")
        self.lbl_score.setStyleSheet("font-size: 22px; font-weight: 900; color: #166534;")
        self.lbl_advice = QLabel("正在分析指纹相似度偏移量...")
        self.lbl_advice.setWordWrap(True)
        rl.addWidget(self.lbl_score); rl.addWidget(self.lbl_advice)
        l.addWidget(self.report_box)

        # D. 操作持久化 (Update/Delete)
        op_row = QHBoxLayout()
        btn_save = QPushButton("💾 提交变更至矩阵"); btn_save.setFixedHeight(48)
        btn_save.setStyleSheet("background: #0ea5e9; color: white; font-weight: 800;")
        btn_save.clicked.connect(self._handle_save_changes)
        
        btn_del = QPushButton("撤销存证")
        btn_del.setFixedWidth(80); btn_del.setFixedHeight(48)
        btn_del.setStyleSheet("color: #ef4444; border: 1px solid #ef4444;")
        btn_del.clicked.connect(self._handle_delete_node)
        
        op_row.addWidget(btn_del); op_row.addWidget(btn_save)
        l.addLayout(op_row)
        
        l.addStretch()
        return view

    # --- 逻辑引擎与交互处理器 ---

    def _sync_global_table(self):
        """同步内存数据库至界面列表"""
        self.table.setRowCount(0)
        for i, node in enumerate(self.repository):
            self.table.insertRow(i)
            self.table.setItem(i, 0, QTableWidgetItem(node.uid))
            self.table.setItem(i, 1, QTableWidgetItem(node.title))
            
            # 风险等级着色
            r_item = QTableWidgetItem(f"{node.risk_index}%")
            if node.risk_index > 70: r_item.setForeground(QColor("#ef4444"))
            elif node.risk_index > 40: r_item.setForeground(QColor("#ca8a04"))
            else: r_item.setForeground(QColor("#10b981"))
            
            self.table.setItem(i, 2, r_item)
            # 修复点：此处不再会报错，因为 CopyrightNode 已定义了 status
            self.table.setItem(i, 3, QTableWidgetItem(node.status))

    def _load_inspector_data(self, item_widget):
        """选中列表项后的数据装载 (Read)"""
        row = item_widget.row()
        uid = self.table.item(row, 0).text()
        node = next((n for n in self.repository if n.uid == uid), None)
        
        if node:
            self.focused_node = node
            self.stack.setCurrentIndex(1)
            # 更新 UI 内容
            self.ui_title.setText(node.title)
            self.ui_uid.setText(node.uid)
            self.ui_dna.setText(node.fingerprint)
            for k, s in self.sliders.items():
                s.setValue(node.factors.get(k, 50))
            self._exec_risk_simulation()

    def _exec_risk_simulation(self):
        """核心业务逻辑：触发风险仿真预测算法"""
        if not self.focused_node: return
        
        # 采集界面仿真参数
        for k, s in self.sliders.items():
            self.focused_node.factors[k] = s.value()
        
        # 调用算法引擎
        new_risk = CopyrightSecurityCore.run_risk_matrix_analysis(self.focused_node.factors)
        self.focused_node.risk_index = new_risk
        
        # 实时 UI 更新
        self.lbl_score.setText(f"风险推演评估: {new_risk}%")
        if new_risk > 70:
            self.lbl_advice.setText("系统预警：该内容全网热度极高且保护机制薄弱。预测存在大规模非法分发风险，建议强制执行链上水印植入。")
            self.report_box.setStyleSheet("background: #fef2f2; border: 1px solid #fecaca; border-radius: 8px; padding: 20px;")
            self.lbl_score.setStyleSheet("font-size: 22px; font-weight: 900; color: #b91c1c;")
        else:
            self.lbl_advice.setText("状态：版权状态稳定。当前存证协议足以覆盖主流分发渠道，未发现指纹DNA被非授权篡改的迹象。")
            self.report_box.setStyleSheet("background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 20px;")
            self.lbl_score.setStyleSheet("font-size: 22px; font-weight: 900; color: #166534;")
        
        self._sync_global_table()

    def _handle_save_changes(self):
        """CRUD - Update 持久化模拟"""
        if self.focused_node:
            self.focused_node.title = self.ui_title.text()
            self.focused_node.op_history.append(f"{datetime.now().strftime('%H:%M')} 人工执行配置校准")
            self._sync_global_table()
            QMessageBox.information(self, "执行成功", f"版权节点 {self.focused_node.uid} 的最新状态已同步至存证矩阵。")

    def _handle_create_node(self):
        """CRUD - Create 新增存证"""
        new_node = CopyrightNode("新内容版权存证项", "艺术影像")
        self.repository.insert(0, new_node)
        self._sync_global_table()
        QMessageBox.information(self, "存证成功", "数字特征指纹已成功写入系统索引，区块链异步同步中...")

    def _handle_delete_node(self):
        """CRUD - Delete 销毁保护"""
        if self.focused_node:
            ans = QMessageBox.question(self, "危险操作确认", f"您确定要彻底注销 [{self.focused_node.title}] 的版权保护吗？\n该操作会导致指纹DNA失效。")
            if ans == QMessageBox.StandardButton.Yes:
                self.repository.remove(self.focused_node)
                self.focused_node = None
                self.stack.setCurrentIndex(0)
                self._sync_global_table()

    def __del__(self):
        pass