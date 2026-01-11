import sys
import random
import json
import time
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
    QTableWidget, QTableWidgetItem, QHeaderView, QSplitter,
    QPushButton, QProgressBar, QTextEdit, QListWidget,
    QListWidgetItem, QStackedWidget, QGroupBox, QFormLayout,
    QComboBox, QMessageBox, QTabWidget, QScrollArea, QSlider,
    QSizePolicy, QAbstractItemView, QMenu
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QRect, QPoint, QTimer, QThread
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QPolygon, QLinearGradient

# --- 核心业务引擎：多维决策矩阵 ---

class DecisionEngine:
    """
    加权共识决策引擎 (Weighted Consensus Engine)
    核心算法：基于信誉权重的多方决策融合
    """
    def __init__(self):
        # 定义不同角色的决策权重系数
        self.role_weights = {
            "AI合规引擎": 0.15,
            "法务部负责人": 0.35,
            "总编审": 0.50
        }

    def calculate_confidence(self, scores: dict):
        """
        计算发布置信度 (Release Confidence Index)
        scores: {role: score_0_100}
        """
        weighted_sum = sum(scores.get(r, 50) * w for r, w in self.role_weights.items())
        # 引入离散度惩罚 (如果两个评审意见分歧过大，则扣减置信度)
        vals = list(scores.values())
        if len(vals) > 1:
            variance = max(vals) - min(vals)
            penalty = (variance ** 2) / 1000 # 离散度越高，惩罚越大
            weighted_sum -= penalty
            
        return round(max(0, min(100, weighted_sum)), 2)

# --- 数据模型实体 ---

class WorkflowTask:
    """审批任务实体，封装状态流转及决策轨迹"""
    def __init__(self, title, requester):
        self.task_id = f"WF-T-{int(time.time())}-{random.randint(100, 999)}"
        self.title = title
        self.requester = requester
        self.submit_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # 流程阶段：0-初审, 1-合规, 2-终审, 3-闭环
        self.current_stage = 1
        self.status = "审批中"
        
        # 实时评分矩阵
        self.reviews = {
            "AI合规引擎": random.randint(60, 95),
            "法务部负责人": 0,
            "总编审": 0
        }
        self.logs = [f"{self.submit_time} 由 {requester} 发起内容发布申请"]
        self.priority = random.choice(["紧急", "常规", "次要"])

# --- 自定义视觉组件 ---

class FlowMapWidget(QWidget):
    """自定义绘图：展示审批流拓扑节点与动态连接"""
    def __init__(self):
        super().__init__()
        self.setMinimumHeight(240)
        self.active_node = 1 # 0, 1, 2, 3
        self.nodes = ["内容送审", "合规风控", "终审决策", "分发入库"]

    def set_active_node(self, index):
        self.active_node = index
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w, h = self.width(), self.height()
        gap = (w - 100) / 3
        y_mid = h // 2
        
        # 绘制连接线
        p.setPen(QPen(QColor(226, 232, 240), 3, Qt.PenStyle.DashLine))
        p.drawLine(50, y_mid, w - 50, y_mid)
        
        # 绘制节点
        for i, name in enumerate(self.nodes):
            x = 50 + i * gap
            
            # 状态颜色逻辑
            if i < self.active_node:
                color = QColor(16, 185, 129) # 已完成 - 绿
            elif i == self.active_node:
                color = QColor(14, 165, 233) # 当前 - 蓝
            else:
                color = QColor(203, 213, 225) # 待处理 - 灰
                
            p.setBrush(QBrush(color))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(QPoint(int(x), y_mid), 15, 15)
            
            # 绘制文字
            p.setPen(QPen(QColor(71, 85, 105)))
            font = QFont("Arial", 10, QFont.Weight.Bold if i == self.active_node else QFont.Weight.Normal)
            p.setFont(font)
            p.drawText(int(x - 30), y_mid + 40, name)

# --- 主模块：审批工作台实现 ---

class EntryWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.engine = DecisionEngine()
        self.task_pool = []
        self.current_task = None
        self._seed_tasks()
        self._init_ui()

    def _seed_tasks(self):
        """注入仿真工作流数据"""
        titles = ["故宫数字资产授权申请", "《山海经》AR互动方案初稿", "丝绸之路微纪录片剪辑版", "非遗手工艺4K素材库发布"]
        users = ["内容组-陈某", "运营部-李某", "技术部-王某"]
        for t in titles:
            self.task_pool.append(WorkflowTask(t, random.choice(users)))

    def _init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # 1. 顶部状态概览
        self.status_bar = QFrame()
        self.status_bar.setFixedHeight(60)
        self.status_bar.setStyleSheet("background: white; border-bottom: 1px solid #e2e8f0; padding: 10px;")
        sb_layout = QHBoxLayout(self.status_bar)
        
        self.lbl_count = QLabel(f"待处理任务: {len([t for t in self.task_pool if t.status == '审批中'])}")
        self.lbl_count.setStyleSheet("font-weight: bold; color: #0f172a;")
        
        btn_refresh = QPushButton("同步远程队列")
        btn_refresh.setFixedWidth(120)
        btn_refresh.clicked.connect(self._refresh_all)
        
        sb_layout.addWidget(self.lbl_count)
        sb_layout.addStretch()
        sb_layout.addWidget(btn_refresh)
        self.main_layout.addWidget(self.status_bar)

        # 2. 核心分割视口
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # --- A: 任务列表区 ---
        self.queue_container = QFrame()
        self.queue_container.setStyleSheet("background: #f8fafc;")
        queue_layout = QVBoxLayout(self.queue_container)
        
        self.task_list = QListWidget()
        self.task_list.setSpacing(5)
        self.task_list.setStyleSheet("border: none; background: transparent;")
        self.task_list.itemClicked.connect(self._load_task_detail)
        queue_layout.addWidget(self.task_list)
        
        self.splitter.addWidget(self.queue_container)

        # --- B: 交互决策面板 ---
        self.inspector = QScrollArea()
        self.inspector.setWidgetResizable(True)
        self.inspector.setStyleSheet("background: white; border-left: 1px solid #e2e8f0;")
        
        self.ins_inner = QWidget()
        self.ins_layout = QVBoxLayout(self.ins_inner)
        self.ins_layout.setContentsMargins(30, 30, 30, 30)
        
        self._build_inspector_ui()
        self.inspector.setWidget(self.ins_inner)
        
        self.splitter.addWidget(self.inspector)
        self.splitter.setStretchFactor(0, 2)
        self.splitter.setStretchFactor(1, 3)
        
        self.main_layout.addWidget(self.splitter)
        
        self._refresh_all()

    def _build_inspector_ui(self):
        """构建详细的审批交互逻辑组件"""
        self.ins_stack = QStackedWidget()
        
        # 状态 0: 空态引导
        self.empty_v = QLabel("请在左侧队列中选择待审项目\n以启动共识决策引擎")
        self.empty_v.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_v.setStyleSheet("color: #94a3b8; font-style: italic;")
        
        # 状态 1: 复杂详情页
        self.work_v = QWidget()
        wv_layout = QVBoxLayout(self.work_v)
        wv_layout.setSpacing(25)

        # 任务头
        self.lbl_title = QLabel("---")
        self.lbl_title.setStyleSheet("font-size: 22px; font-weight: 800; color: #1e293b;")
        wv_layout.addWidget(self.lbl_title)
        
        # 动态流程图
        self.flow_map = FlowMapWidget()
        wv_layout.addWidget(self.flow_map)

        # 数据面板
        info_row = QHBoxLayout()
        self.group_info = QGroupBox("基础上下文")
        f_layout = QFormLayout(self.group_info)
        self.ui_id = QLabel(); self.ui_req = QLabel(); self.ui_pri = QLabel()
        f_layout.addRow("任务编号:", self.ui_id)
        f_layout.addRow("申请人员:", self.ui_req)
        f_layout.addRow("紧急程度:", self.ui_pri)
        info_row.addWidget(self.group_info, 1)
        
        self.group_ai = QGroupBox("AI 智能风险扫描")
        ai_layout = QVBoxLayout(self.group_ai)
        self.ai_prog = QProgressBar()
        self.ai_prog.setStyleSheet("QProgressBar::chunk { background: #10b981; }")
        ai_layout.addWidget(QLabel("合规度分值:"))
        ai_layout.addWidget(self.ai_prog)
        ai_layout.addWidget(QLabel("风险项: [0] 安全"))
        info_row.addWidget(self.group_ai, 1)
        wv_layout.addLayout(info_row)

        # 核心决策逻辑区
        self.tabs = QTabWidget()
        
        # Tab 1: 专家打分
        self.score_tab = QWidget()
        st_layout = QVBoxLayout(self.score_tab)
        st_layout.addWidget(QLabel("请针对该内容进行多维打分 (0-100):"))
        self.sld_legal = QSlider(Qt.Orientation.Horizontal)
        self.sld_legal.setRange(0, 100)
        self.sld_boss = QSlider(Qt.Orientation.Horizontal)
        self.sld_boss.setRange(0, 100)
        
        st_layout.addWidget(QLabel("法务合规分:"))
        st_layout.addWidget(self.sld_legal)
        st_layout.addWidget(QLabel("总编终审分:"))
        st_layout.addWidget(self.sld_boss)
        
        self.btn_calc = QPushButton("执行引擎推演分析")
        self.btn_calc.setStyleSheet("background: #0f172a; color: white; padding: 12px; font-weight: bold;")
        self.btn_calc.clicked.connect(self._run_consensus_algo)
        st_layout.addWidget(self.btn_calc)
        self.tabs.addTab(self.score_tab, "决策权重输入")
        
        # Tab 2: 审计追踪
        self.log_list = QListWidget()
        self.tabs.addTab(self.log_list, "全生命周期日志")
        
        wv_layout.addWidget(self.tabs)

        # 结论展示
        self.res_frame = QFrame()
        self.res_frame.setStyleSheet("background: #f0f9ff; border-radius: 8px; border: 1px solid #bae6fd;")
        res_l = QVBoxLayout(self.res_frame)
        self.lbl_conf = QLabel("发布置信度指数: --")
        self.lbl_conf.setStyleSheet("font-size: 18px; font-weight: bold; color: #0369a1;")
        res_l.addWidget(self.lbl_conf)
        wv_layout.addWidget(self.res_frame)

        # 操作
        btn_row = QHBoxLayout()
        btn_pass = QPushButton("准予发布 (Final Pass)")
        btn_pass.setStyleSheet("background: #16a34a; color: white; font-weight: bold; height: 45px;")
        btn_pass.clicked.connect(lambda: self._finalize_decision(True))
        
        btn_back = QPushButton("退回修订 (Return)")
        btn_back.setStyleSheet("background: #dc2626; color: white; font-weight: bold; height: 45px;")
        btn_back.clicked.connect(lambda: self._finalize_decision(False))
        
        btn_row.addWidget(btn_back)
        btn_row.addWidget(btn_pass)
        wv_layout.addLayout(btn_row)

        self.ins_stack.addWidget(self.empty_v)
        self.ins_stack.addWidget(self.work_v)
        self.ins_layout.addWidget(self.ins_stack)

    # --- 交互处理器与逻辑引擎 ---

    def _refresh_all(self):
        """同步队列数据"""
        self.task_list.clear()
        for t in self.task_pool:
            item = QListWidgetItem()
            item.setSizeHint(QSize(0, 80))
            
            # 自定义 Item 内容展示
            container = QFrame()
            container.setStyleSheet("background: white; border-radius: 6px; border: 1px solid #e2e8f0;")
            l = QVBoxLayout(container)
            l.addWidget(QLabel(f"ID: {t.task_id}"))
            title = QLabel(t.title)
            title.setStyleSheet("font-weight: bold; color: #1e293b;")
            l.addWidget(title)
            
            self.task_list.addItem(item)
            self.task_list.setItemWidget(item, container)
            item.setData(Qt.ItemDataRole.UserRole, t)

    def _load_task_detail(self, item):
        task = item.data(Qt.ItemDataRole.UserRole)
        self.current_task = task
        self.ins_stack.setCurrentIndex(1)
        
        # 渲染 UI
        self.lbl_title.setText(task.title)
        self.ui_id.setText(task.task_id)
        self.ui_req.setText(task.requester)
        self.ui_pri.setText(task.priority)
        self.ai_prog.setValue(task.reviews["AI合规引擎"])
        
        self.flow_map.set_active_node(task.current_stage)
        self.log_list.clear()
        self.log_list.addItems(task.logs)
        
        # 重置决策滑块
        self.sld_legal.setValue(task.reviews.get("法务部负责人", 0))
        self.sld_boss.setValue(task.reviews.get("总编审", 0))
        self.lbl_conf.setText("发布置信度指数: --")

    def _run_consensus_algo(self):
        """核心逻辑：执行决策推演算法"""
        if not self.current_task: return
        
        scores = {
            "AI合规引擎": self.current_task.reviews["AI合规引擎"],
            "法务部负责人": self.sld_legal.value(),
            "总编审": self.sld_boss.value()
        }
        
        conf_index = self.engine.calculate_confidence(scores)
        self.lbl_conf.setText(f"发布置信度指数: {conf_index}%")
        
        # 反馈颜色逻辑
        color = "#16a34a" if conf_index > 80 else "#ca8a04" if conf_index > 50 else "#dc2626"
        self.lbl_conf.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {color};")
        
        self.current_task.logs.append(f"{datetime.now().strftime('%H:%M')} 算法执行推演，当前置信度: {conf_index}%")
        self.log_list.clear()
        self.log_list.addItems(self.current_task.logs)

    def _finalize_decision(self, is_pass):
        """CRUD - Update: 提交决策结果"""
        if not self.current_task: return
        
        res_str = "通过" if is_pass else "驳回"
        msg = f"您确定要执行 [{res_str}] 决策吗？\n该操作将记录在区块链存证日志中且不可更改。"
        
        ans = QMessageBox.question(self, "最终决策确认", msg)
        if ans == QMessageBox.StandardButton.Yes:
            self.current_task.status = "已闭环" if is_pass else "已驳回"
            self.current_task.current_stage = 3 if is_pass else 1
            self.current_task.logs.append(f"{datetime.now().strftime('%H:%M')} 最终决策: {res_str}")
            
            QMessageBox.information(self, "操作成功", "审批流状态已更新。")
            self.ins_stack.setCurrentIndex(0)
            self._refresh_all()

    def __del__(self):
        pass