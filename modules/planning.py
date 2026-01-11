import json
import math
import random
import os
from datetime import datetime
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
                             QLineEdit, QTextEdit, QSlider, QComboBox, QPushButton, 
                             QTableWidget, QTableWidgetItem, QHeaderView, QSplitter,
                             QScrollArea, QGroupBox, QFormLayout, QMessageBox, QListWidget,
                             QFileDialog, QProgressBar, QTabWidget, QSpinBox, QDoubleSpinBox)
from PyQt6.QtCore import Qt, pyqtSignal, QRect, QPoint, QSize, QTimer
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QPolygonF, QLinearGradient

# --- 核心业务逻辑与数据模型 ---

class PlanDataModel:
    """策划案核心数据对象"""
    def __init__(self, title="新策划案"):
        self.id = f"PLN-{int(datetime.now().timestamp())}"
        self.title = title
        self.category = "视觉艺术"
        self.genes = {"depth": 50, "narrative": 50, "visual": 50, "interact": 50, "trend": 50}
        self.beats = [] # 叙事节奏节点
        self.budget_limit = 50000.0
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class PlanningLogicEngine:
    """高级策划推演引擎"""
    
    @staticmethod
    def calculate_budget_fit(genes, base_cost=10000):
        """算法：基于基因复杂度的动态成本预估"""
        # 深度和视觉对成本影响最大，交互次之
        multiplier = (genes['depth'] * 1.5 + genes['visual'] * 2.0 + genes['interact'] * 1.2) / 100
        complexity_score = sum(genes.values()) / 500
        total_est = base_cost * multiplier * (1 + complexity_score)
        return round(total_est, 2)

    @staticmethod
    def evaluate_risk(genes):
        """算法：推演策划案的执行风险系数"""
        # 如果趋势过高而深度不足，则视为“浮躁风险”
        if genes['trend'] > 80 and genes['depth'] < 30:
            return "极高：内容空洞化风险"
        if genes['interact'] > 85:
            return "中高：技术实现难度风险"
        return "低：执行稳健"

# --- 自定义高端 UI 组件 ---

class HeatmapVisualizer(QWidget):
    """自定义组件：分布匹配热力图"""
    def __init__(self):
        super().__init__()
        self.setMinimumHeight(200)
        self.scores = [0] * 5
        self.channels = ["短视频", "长视频", "虚拟展厅", "社交矩阵", "线下特展"]

    def update_scores(self, new_scores):
        self.scores = new_scores
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w, h = self.width(), self.height()
        cell_w = (w - 100) / 5
        
        for i, score in enumerate(self.scores):
            x = 80 + i * cell_w
            # 计算颜色：得分越高越绿，越低越红
            green = int(min(255, score * 2.5))
            red = int(min(255, (100 - score) * 2.5))
            color = QColor(red, green, 100, 180)
            
            p.setBrush(QBrush(color))
            p.setPen(QPen(QColor(255, 255, 255, 100), 1))
            rect = QRect(int(x), 20, int(cell_w - 5), h - 60)
            p.drawRoundedRect(rect, 4, 4)
            
            # 绘制数值
            p.setPen(QPen(Qt.GlobalColor.white))
            p.drawText(rect, Qt.AlignmentFlag.AlignCenter, f"{int(score)}%")
            
            # 绘制下方标签
            p.setPen(QPen(QColor(100, 116, 139)))
            p.drawText(int(x), h - 10, self.channels[i])

# --- 主入口视窗 ---

class EntryWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.current_plan = PlanDataModel()
        self.snapshot_manager = [] # 模拟快照逻辑
        self.storage_path = "data_planning.json"
        
        self._init_ui()
        self._load_local_data()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 顶部工具栏
        self.toolbar = QFrame()
        self.toolbar.setFixedHeight(50)
        self.toolbar.setStyleSheet("background: #ffffff; border-bottom: 1px solid #e2e8f0;")
        tb_layout = QHBoxLayout(self.toolbar)
        
        self.id_label = QLabel(f"当前工单: {self.current_plan.id}")
        self.id_label.setStyleSheet("font-family: 'Consolas'; color: #64748b;")
        
        btn_save = QPushButton("💾 导出方案")
        btn_save.clicked.connect(self._handle_save_action)
        btn_import = QPushButton("📂 导入历史")
        btn_import.clicked.connect(self._handle_import_action)
        
        tb_layout.addWidget(self.id_label)
        tb_layout.addStretch()
        tb_layout.addWidget(btn_import)
        tb_layout.addWidget(btn_save)
        
        layout.addWidget(self.toolbar)

        # 主内容区分割
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 1. 左侧：编辑器
        self.editor_tabs = QTabWidget()
        self.editor_tabs.addTab(self._create_gene_tab(), "文化基因配置")
        self.editor_tabs.addTab(self._create_narrative_tab(), "叙事节奏编排")
        self.editor_tabs.addTab(self._create_resource_tab(), "成本与资源预测")
        
        # 2. 右侧：智能看板
        self.dashboard_panel = self._create_dashboard_panel()
        
        self.splitter.addWidget(self.editor_tabs)
        self.splitter.addWidget(self.dashboard_panel)
        self.splitter.setStretchFactor(0, 3)
        self.splitter.setStretchFactor(1, 2)
        
        layout.addWidget(self.splitter)

    def _create_gene_tab(self):
        container = QScrollArea()
        container.setWidgetResizable(True)
        w = QWidget()
        l = QVBoxLayout(w)
        
        # 基本信息
        group_base = QGroupBox("核心元数据")
        f_layout = QFormLayout(group_base)
        self.ui_title = QLineEdit(self.current_plan.title)
        self.ui_cat = QComboBox()
        self.ui_cat.addItems(["视觉艺术", "数字非遗", "历史解构", "互动展演", "元宇宙内容"])
        f_layout.addRow("项目主标题:", self.ui_title)
        f_layout.addRow("文化领域:", self.ui_cat)
        l.addWidget(group_base)

        # 基因控制
        group_gene = QGroupBox("特征向量建模")
        g_layout = QVBoxLayout(group_gene)
        self.gene_sliders = {}
        for key, name in [("depth", "文化深度"), ("narrative", "叙事强度"), 
                          ("visual", "视觉张力"), ("interact", "交互频率"), ("trend", "流行适配")]:
            row = QHBoxLayout()
            lbl = QLabel(name)
            lbl.setFixedWidth(80)
            sld = QSlider(Qt.Orientation.Horizontal)
            sld.setRange(0, 100)
            sld.setValue(50)
            val = QLabel("50")
            sld.valueChanged.connect(lambda v, lv=val: lv.setText(str(v)))
            sld.valueChanged.connect(self._recalculate_all)
            row.addWidget(lbl)
            row.addWidget(sld)
            row.addWidget(val)
            g_layout.addLayout(row)
            self.gene_sliders[key] = sld
        l.addWidget(group_gene)
        
        l.addStretch()
        container.setWidget(w)
        return container

    def _create_narrative_tab(self):
        """叙事节奏编辑器（节点 CRUD 逻辑）"""
        w = QWidget()
        l = QVBoxLayout(w)
        
        header = QHBoxLayout()
        header.addWidget(QLabel("叙事节点列表"))
        btn_add_node = QPushButton("+ 添加关键帧")
        btn_add_node.clicked.connect(self._add_narrative_node)
        header.addWidget(btn_add_node)
        l.addLayout(header)
        
        self.node_table = QTableWidget(0, 3)
        self.node_table.setHorizontalHeaderLabels(["序号", "内容概要", "情感极性"])
        self.node_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        l.addWidget(self.node_table)
        
        btn_clear = QPushButton("清空所有节点")
        btn_clear.clicked.connect(lambda: self.node_table.setRowCount(0))
        l.addWidget(btn_clear)
        return w

    def _create_resource_tab(self):
        w = QWidget()
        l = QVBoxLayout(w)
        
        group = QGroupBox("成本控制矩阵")
        fl = QFormLayout(group)
        self.ui_budget_limit = QDoubleSpinBox()
        self.ui_budget_limit.setRange(1000, 1000000)
        self.ui_budget_limit.setValue(50000)
        self.ui_budget_limit.setPrefix("￥ ")
        fl.addRow("预算红线:", self.ui_budget_limit)
        
        self.ui_team_size = QSpinBox()
        self.ui_team_size.setRange(1, 50)
        fl.addRow("预估投入人力:", self.ui_team_size)
        
        l.addWidget(group)
        
        self.cost_report = QTextEdit()
        self.cost_report.setReadOnly(True)
        self.cost_report.setStyleSheet("background: #f8fafc; font-family: 'Consolas';")
        l.addWidget(QLabel("智能成本推演报告:"))
        l.addWidget(self.cost_report)
        l.addStretch()
        return w

    def _create_dashboard_panel(self):
        w = QFrame()
        w.setStyleSheet("background: #ffffff; border-left: 1px solid #e2e8f0;")
        l = QVBoxLayout(w)
        
        l.addWidget(QLabel("智能看板分析"))
        
        # 1. 热力图
        self.heatmap = HeatmapVisualizer()
        l.addWidget(self.heatmap)
        
        # 2. 风险预警区
        self.risk_box = QFrame()
        self.risk_box.setFixedHeight(80)
        self.risk_box.setStyleSheet("background: #fff1f2; border-radius: 8px; border: 1px solid #fda4af;")
        rb_layout = QVBoxLayout(self.risk_box)
        self.risk_label = QLabel("风险评估中...")
        self.risk_label.setStyleSheet("color: #be123c; font-weight: bold;")
        rb_layout.addWidget(self.risk_label)
        l.addWidget(self.risk_box)
        
        # 3. 实时评估指标
        l.addWidget(QLabel("关键性能推演 (KPIs):"))
        self.prog_influence = QProgressBar()
        self.prog_interact = QProgressBar()
        l.addWidget(QLabel("传播潜力"))
        l.addWidget(self.prog_influence)
        l.addWidget(QLabel("技术实现可行性"))
        l.addWidget(self.prog_interact)
        
        l.addStretch()
        
        # 4. 快照记录
        l.addWidget(QLabel("最近快照"))
        self.snapshot_list = QListWidget()
        self.snapshot_list.setFixedHeight(120)
        l.addWidget(self.snapshot_list)
        
        return w

    # --- 核心交互逻辑 ---

    def _recalculate_all(self):
        """核心推演算法联动"""
        genes = {k: s.value() for k, s in self.gene_sliders.items()}
        
        # 更新预算推演
        est_cost = PlanningLogicEngine.calculate_budget_fit(genes)
        limit = self.ui_budget_limit.value()
        status = "正常" if est_cost <= limit else "超支风险"
        
        report = (
            f">> 成本推演引擎启动...\n"
            f">> 基础复杂度: {sum(genes.values())/5:.1f}%\n"
            f">> 预估执行成本: ￥{est_cost:,}\n"
            f">> 预算状态: {status}\n"
            f">> 建议资源配比: 开发40%, 内容35%, 营销25%"
        )
        self.cost_report.setText(report)
        
        # 更新热力图得分
        base_score = sum(genes.values()) / 5
        scores = [
            min(100, base_score + random.randint(-10, 20)),
            min(100, base_score + random.randint(-5, 15)),
            min(100, base_score + random.randint(10, 30)),
            min(100, base_score + random.randint(-20, 10)),
            min(100, base_score + random.randint(5, 25))
        ]
        self.heatmap.update_scores(scores)
        
        # 更新进度条
        self.prog_influence.setValue(int(base_score * 1.1))
        self.prog_interact.setValue(100 - genes['interact'] // 2)
        
        # 更新风险评估
        self.risk_label.setText(f"状态: {PlanningLogicEngine.evaluate_risk(genes)}")

    def _add_narrative_node(self):
        row = self.node_table.rowCount()
        self.node_table.insertRow(row)
        self.node_table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
        self.node_table.setItem(row, 1, QTableWidgetItem("新叙事片段..."))
        self.node_table.setItem(row, 2, QTableWidgetItem("中性"))

    def _handle_save_action(self):
        """CRUD - Create/Update 逻辑"""
        plan_dict = {
            "id": self.current_plan.id,
            "title": self.ui_title.text(),
            "genes": {k: s.value() for k, s in self.gene_sliders.items()},
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }
        
        # 更新快照
        snap_name = f"V{len(self.snapshot_manager)+1} - {plan_dict['timestamp']}"
        self.snapshot_list.insertItem(0, snap_name)
        self.snapshot_manager.append(plan_dict)
        
        # 保存到本地文件 (模拟数据库)
        try:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(self.snapshot_manager, f, ensure_ascii=False, indent=4)
            QMessageBox.information(self, "存盘成功", f"策划案已作为快照 [{snap_name}] 持久化。")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法写入磁盘: {e}")

    def _handle_import_action(self):
        """CRUD - Read 逻辑"""
        if not os.path.exists(self.storage_path):
            QMessageBox.warning(self, "提示", "未找到历史存储数据。")
            return
            
        with open(self.storage_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if data:
                last = data[-1]
                self.ui_title.setText(last['title'])
                for k, v in last['genes'].items():
                    self.gene_sliders[k].setValue(v)
                QMessageBox.information(self, "载入成功", f"已还原至最近快照: {last['title']}")

    def _load_local_data(self):
        """初始化加载"""
        QTimer.singleShot(500, self._recalculate_all)

    def __del__(self):
        pass