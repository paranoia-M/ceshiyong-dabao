import sys
import random
import math
import time
from datetime import datetime, timedelta

# 严谨导入所有组件，确保无 NameError
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, 
    QHeaderView, QSplitter, QComboBox, QProgressBar, 
    QScrollArea, QGroupBox, QFormLayout, QStackedWidget, 
    QMessageBox, QAbstractItemView, QSizePolicy, QListWidget, 
    QListWidgetItem, QTabWidget, QToolBar
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QRect, QPoint, QTimer
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QLinearGradient, QPolygon

# --- 核心算法引擎：文化影响力归因模型 ---

class InsightEngine:
    """
    文化数据归因与情感分析引擎
    核心算法：基于加权扰动矩阵的影响力归因 (Influence Attribution Matrix)
    """
    @staticmethod
    def run_attribution_analysis(raw_metrics: dict):
        # 基础因子：浏览(V), 互动(E), 情感(S), 文化权重(C)
        v = raw_metrics.get('views', 1000)
        e = raw_metrics.get('engagement', 50)
        s = raw_metrics.get('sentiment', 0.6) # 0.0 - 1.0
        c = raw_metrics.get('culture_depth', 50) # 0 - 100

        # 算法逻辑：
        # 1. 计算传播质量指数 (QI)
        quality_index = (e / max(1, v)) * 100 * (1 + s)
        
        # 2. 归因计算：推算文化内核贡献度 vs 渠道营销贡献度
        # 逻辑：如果情感值高且互动率高，则文化内核驱动力强
        culture_drive = (s * 0.6 + (c / 100) * 0.4) * 100
        channel_drive = 100 - culture_drive
        
        # 3. 预测未来 24H 衰减后的残余影响力
        # 采用对数衰减：Impact_next = QI * ln(1 + e/v)
        potential = quality_index * math.log1p(e / max(1, v) * 10)
        
        return {
            "quality_index": round(quality_index, 2),
            "culture_drive": round(culture_drive, 1),
            "channel_drive": round(channel_drive, 1),
            "momentum_score": round(min(100, potential * 10), 2)
        }

# --- 数据模型与记录实体 ---

class AnalyticsReport:
    """封装单一内容的数据透视报告"""
    def __init__(self, title, category):
        self.report_id = f"ANL-{int(time.time() % 100000)}-{random.randint(10, 99)}"
        self.title = title
        self.category = category
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # 仿真原始数据
        self.raw_data = {
            'views': random.randint(5000, 100000),
            'engagement': random.randint(200, 8000),
            'sentiment': random.uniform(0.3, 0.95),
            'culture_depth': random.randint(40, 95)
        }
        
        # 初始算法分析结果
        self.results = InsightEngine.run_attribution_analysis(self.raw_data)
        self.audit_log = [f"系统于 {self.timestamp} 自动捕获全网传播特征并执行归因推演"]

# --- 自定义视觉组件：情感波动光谱图 ---

class SentimentSpectrumCanvas(QWidget):
    """自定义绘图：情感波动与传播动量频谱"""
    def __init__(self):
        super().__init__()
        self.setMinimumHeight(260)
        self.data_stream = [random.randint(20, 80) for _ in range(30)]

    def update_stream(self, val):
        self.data_stream.append(val)
        if len(self.data_stream) > 50: self.data_stream.pop(0)
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w, h = self.width(), self.height()
        margin = 40
        canvas_w = w - margin * 2
        canvas_h = h - margin * 2
        
        # 背景装饰
        p.fillRect(0, 0, w, h, QColor(15, 23, 42)) # 深色背景
        
        # 绘制扫描网格
        p.setPen(QPen(QColor(30, 41, 59), 1))
        for i in range(1, 10):
            x = margin + i * (canvas_w / 10)
            p.drawLine(int(x), margin, int(x), h - margin)
            y = margin + i * (canvas_h / 10)
            p.drawLine(margin, int(y), w - margin, int(y))

        # 绘制情感流路径 (使用渐变光束)
        if len(self.data_stream) > 1:
            path_pen = QPen(QColor(56, 189, 248), 2)
            p.setPen(path_pen)
            
            x_step = canvas_w / 49
            poly = QPolygon()
            for i, val in enumerate(self.data_stream):
                x = margin + i * x_step
                y = (h - margin) - (val / 100 * canvas_h)
                poly.append(QPoint(int(x), int(y)))
            
            p.drawPolyline(poly)
            
            # 绘制发光端点
            p.setBrush(QBrush(QColor(56, 189, 248)))
            p.drawEllipse(poly.point(poly.count()-1), 5, 5)

        # 标题提示
        p.setPen(QPen(QColor(148, 163, 184)))
        p.setFont(QFont("Consolas", 9))
        p.drawText(margin, margin - 15, "LIVE SENTIMENT FLUX MONITORING / 实时情感涨落监测")

# --- 主模块界面实现 ---

class EntryWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.engine = InsightEngine()
        self.reports_db = []
        self.active_report = None
        self._seed_mock_database()
        self._init_ui_structure()

    def _seed_mock_database(self):
        """注入高仿真文化传播数据集"""
        titles = ["故宫雪景专题归因", "《山海经》插画情感报告", "非遗传承纪录片效能", "敦煌AR展厅传播分析"]
        cats = ["视觉艺术", "数字非遗", "历史解构", "交互体验"]
        for _ in range(8):
            self.reports_db.append(AnalyticsReport(random.choice(titles), random.choice(cats)))

    def _init_ui_structure(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # 1. 顶部控制矩阵
        self.toolbar = QToolBar()
        self.toolbar.setStyleSheet("background: white; border-bottom: 1px solid #e2e8f0; padding: 10px;")
        
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("检索报告ID、内容标题或传播特征...")
        self.search_box.setFixedWidth(350)
        self.search_box.textChanged.connect(self._run_filter_pipeline)

        self.cat_filter = QComboBox()
        self.cat_filter.addItems(["全部维度", "视觉艺术", "数字非遗", "历史解构", "交互体验"])
        self.cat_filter.currentTextChanged.connect(self._run_filter_pipeline)

        btn_recalc = QPushButton("↻ 全局算法重校准")
        btn_recalc.setStyleSheet("background: #0f172a; color: white; padding: 8px 15px; font-weight: bold; border-radius: 4px;")
        btn_recalc.clicked.connect(self._recalc_global)

        self.toolbar.addWidget(QLabel(" 过滤引擎: "))
        self.toolbar.addWidget(self.cat_filter)
        self.toolbar.addSeparator()
        self.toolbar.addWidget(self.search_box)
        
        # 弹簧布局
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.toolbar.addWidget(spacer)
        self.toolbar.addWidget(btn_recalc)
        
        self.layout.addWidget(self.toolbar)

        # 2. 实时频谱看板
        self.spectrum = SentimentSpectrumCanvas()
        self.layout.addWidget(self.spectrum)

        # 3. 核心分割工作台
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setHandleWidth(1)
        
        # --- A: 报告索引列表 (CRUD - Read) ---
        self.list_panel = QFrame()
        self.list_panel.setStyleSheet("background: #f8fafc;")
        lp_layout = QVBoxLayout(self.list_panel)
        
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["报告UID", "内容标题", "动量得分", "主驱动力"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.itemClicked.connect(self._load_detail_report)
        lp_layout.addWidget(self.table)
        
        self.splitter.addWidget(self.list_panel)

        # --- B: 深度透视面板 (CRUD - Update/Algorithm) ---
        self.inspector = QScrollArea()
        self.inspector.setWidgetResizable(True)
        self.inspector.setStyleSheet("background: white; border-left: 1px solid #e2e8f0;")
        self.ins_inner = QWidget()
        self.ins_layout = QVBoxLayout(self.ins_inner)
        self.ins_layout.setContentsMargins(25, 25, 25, 25)
        
        self.stack = QStackedWidget()
        self.empty_v = QLabel("请在左侧索引中定位一份分析报告\n以开启文化归因推演")
        self.empty_v.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_v.setStyleSheet("color: #94a3b8; font-style: italic;")
        
        self.detail_v = self._build_detail_report_ui()
        
        self.stack.addWidget(self.empty_v)
        self.stack.addWidget(self.detail_v)
        self.ins_layout.addWidget(self.stack)
        
        self.inspector.setWidget(self.ins_inner)
        self.splitter.addWidget(self.inspector)
        
        self.splitter.setStretchFactor(0, 3)
        self.splitter.setStretchFactor(1, 2)
        self.layout.addWidget(self.splitter)
        
        self._sync_table_view()

    def _build_detail_report_ui(self):
        """构建复杂的报告深度透视界面"""
        w = QWidget()
        l = QVBoxLayout(w)
        l.setSpacing(22)

        # 头部标题
        self.lbl_report_title = QLabel("---")
        self.lbl_report_title.setStyleSheet("font-size: 20px; font-weight: 800; color: #1e293b;")
        l.addWidget(self.lbl_report_title)

        # 数据卡片组
        metrics_row = QHBoxLayout()
        self.box_views = self._create_mini_card("核心曝光", "0", "#38bdf8")
        self.box_eng = self._create_mini_card("互动总量", "0", "#4ade80")
        metrics_row.addWidget(self.box_views); metrics_row.addWidget(self.box_eng)
        l.addLayout(metrics_row)

        # 归因推演结果
        group_attr = QGroupBox("影响力归因推演")
        al = QVBoxLayout(group_attr)
        
        self.prog_culture = QProgressBar()
        self.prog_culture.setStyleSheet("QProgressBar::chunk { background: #6366f1; }")
        self.prog_channel = QProgressBar()
        self.prog_channel.setStyleSheet("QProgressBar::chunk { background: #f43f5e; }")
        
        al.addWidget(QLabel("文化内核驱动贡献度:"))
        al.addWidget(self.prog_culture)
        al.addWidget(QLabel("分发渠道营销贡献度:"))
        al.addWidget(self.prog_channel)
        l.addWidget(group_attr)

        # 预测报告面板
        self.report_frame = QFrame()
        self.report_frame.setStyleSheet("background: #f0f9ff; border-radius: 8px; border: 1px solid #bae6fd; padding: 15px;")
        rl = QVBoxLayout(self.report_frame)
        self.lbl_momentum = QLabel("动量得分: --")
        self.lbl_momentum.setStyleSheet("font-size: 18px; font-weight: 900; color: #0369a1;")
        self.txt_summary = QLabel("正在分析传播轨迹...")
        self.txt_summary.setWordWrap(True)
        rl.addWidget(self.lbl_momentum); rl.addWidget(self.txt_summary)
        l.addWidget(self.report_frame)

        # 操作
        btn_row = QHBoxLayout()
        btn_export = QPushButton("📤 导出分析报告")
        btn_export.setFixedHeight(45)
        btn_export.setStyleSheet("background: #0f172a; color: white; font-weight: bold;")
        btn_export.clicked.connect(self._handle_export)
        
        btn_del = QPushButton("销毁")
        btn_del.setFixedWidth(70); btn_del.setFixedHeight(45)
        btn_del.clicked.connect(self._handle_delete_report)
        
        btn_row.addWidget(btn_del); btn_row.addWidget(btn_export)
        l.addLayout(btn_row)
        l.addStretch()
        return w

    def _create_mini_card(self, title, val, color):
        f = QFrame()
        f.setStyleSheet(f"background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 10px;")
        l = QVBoxLayout(f)
        t = QLabel(title); t.setStyleSheet("color: #64748b; font-size: 11px;")
        v = QLabel(val); v.setStyleSheet(f"color: {color}; font-size: 18px; font-weight: 800;")
        l.addWidget(t); l.addWidget(v)
        f.find_label = v # 引用以便更新
        return f

    # --- 交互处理器与逻辑引擎 ---

    def _sync_table_view(self):
        """逻辑：同步内存数据至列表矩阵"""
        self.table.setRowCount(0)
        for i, rep in enumerate(self.reports_db):
            self.table.insertRow(i)
            self.table.setItem(i, 0, QTableWidgetItem(rep.report_id))
            self.table.setItem(i, 1, QTableWidgetItem(rep.title))
            
            m_item = QTableWidgetItem(f"{rep.results['momentum_score']}")
            if rep.results['momentum_score'] > 70: m_item.setForeground(QColor("#10b981"))
            self.table.setItem(i, 2, m_item)
            
            drive_text = "文化导向" if rep.results['culture_drive'] > 50 else "营销导向"
            self.table.setItem(i, 3, QTableWidgetItem(drive_text))

    def _load_detail_report(self, item_widget):
        row = item_widget.row()
        uid = self.table.item(row, 0).text()
        report = next((r for r in self.reports_db if r.report_id == uid), None)
        
        if report:
            self.active_report = report
            self.stack.setCurrentIndex(1)
            self.lbl_report_title.setText(report.title)
            
            # 更新 mini 卡片 (通过之前保存的引用)
            self.box_views.find_label.setText(f"{report.raw_data['views']:,}")
            self.box_eng.find_label.setText(f"{report.raw_data['engagement']:,}")
            
            # 更新进度条
            self.prog_culture.setValue(int(report.results['culture_drive']))
            self.prog_channel.setValue(int(report.results['channel_drive']))
            
            # 更新总结
            self.lbl_momentum.setText(f"动量得分: {report.results['momentum_score']}")
            msg = (f"基于算法推演，该内容在 {report.category} 领域表现出强劲的 "
                   f"{'文化内聚力' if report.results['culture_drive'] > 50 else '渠道渗透力'}。")
            self.txt_summary.setText(msg)

    def _run_filter_pipeline(self):
        """逻辑：复合筛选流水线"""
        kw = self.search_box.text().lower()
        cat = self.cat_filter.currentText()
        
        # 实时同步绘图波动
        self.spectrum.update_stream(random.randint(40, 90))
        
        # 过滤数据
        filtered = [r for r in self.reports_db if 
                    (kw in r.title.lower() or kw in r.report_id.lower()) and
                    (cat == "全部维度" or r.category == cat)]
        
        self.table.setRowCount(0)
        # 手动重刷（不复用 _sync 以保持过滤状态）
        for i, rep in enumerate(filtered):
            self.table.insertRow(i)
            self.table.setItem(i, 0, QTableWidgetItem(rep.report_id))
            self.table.setItem(i, 1, QTableWidgetItem(rep.title))
            self.table.setItem(i, 2, QTableWidgetItem(str(rep.results['momentum_score'])))
            self.table.setItem(i, 3, QTableWidgetItem("Ready"))

    def _recalc_global(self):
        """逻辑：批量重算算法模型数据"""
        for r in self.reports_db:
            # 模拟数据更新
            r.raw_data['views'] += random.randint(100, 1000)
            r.results = InsightEngine.run_attribution_analysis(r.raw_data)
        self._sync_table_view()
        QMessageBox.information(self, "算法中心", "全局传播模型已完成非线性校准。")

    def _handle_export(self):
        if self.active_report:
            QMessageBox.information(self, "导出成功", f"报告 {self.active_report.report_id} 已生成 PDF 归档。")

    def _handle_delete_report(self):
        if self.active_report:
            self.reports_db.remove(self.active_report)
            self.active_report = None
            self.stack.setCurrentIndex(0)
            self._sync_table_view()

    def __del__(self):
        pass