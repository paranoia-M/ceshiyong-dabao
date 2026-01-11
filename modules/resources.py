import sys
import random
import os
import json
import time
import math  # 用于算法推演
from datetime import datetime, timedelta

# 一次性完整导入所有需要的组件，防止 NameError
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, 
    QHeaderView, QSplitter, QComboBox, QCheckBox, 
    QProgressBar, QScrollArea, QFileDialog, QMenu,
    QGridLayout, QToolBar, QStatusBar, QDialog, QFormLayout,
    QGroupBox, QTabWidget, QTextEdit, QListWidget, QListWidgetItem,
    QAbstractItemView, QSpinBox, QSlider, QStackedWidget,
    QMessageBox, QSizePolicy # 修复：加入 QSizePolicy 用于处理布局占位
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QRect, QPoint, QTimer, QThread
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QPixmap, QAction, QIcon, QPolygon

# --- 核心业务逻辑层：数字文化资产全生命周期价值矩阵 ---

class ResourceEngine:
    """
    文化数字资产价值评估引擎
    基于：动态加权线性回归与对数增长模型
    """
    @staticmethod
    def evaluate_node(attributes: dict):
        # 核心维度：文化稀缺度(S), 采样技术精度(T), 历史文物权重(H), 衍生潜力(P)
        weights = {'S': 0.45, 'T': 0.20, 'H': 0.25, 'P': 0.10}
        
        # 基础分值推演
        raw_score = (
            attributes.get('scarcity', 50) * weights['S'] +
            attributes.get('technical', 50) * weights['T'] +
            attributes.get('heritage', 50) * weights['H'] +
            attributes.get('potential', 50) * weights['P']
        )
        
        # 引入时间价值增益逻辑：存储时间越长，经过多重备份校对，其资产可靠性与价值越高
        # 修正：之前报错的 math 已在此文件顶部导入
        months = attributes.get('duration_months', 1)
        time_boost = 1 + (math.log1p(months / 12.0) * 0.22)
        
        # 引入随机环境扰动因子（模拟全网文化热度波动）
        market_fluctuation = random.uniform(0.97, 1.03)
        
        final_index = raw_score * time_boost * market_fluctuation
        return round(min(100, final_index), 2)

# --- 资产实体模型 ---

class DigitalAssetEntity:
    """资产核心数据实体，支持元数据与操作日志序列化"""
    def __init__(self, name, group_type):
        self.asset_id = f"RESOURCE-IDX-{int(time.time())}-{random.randint(100, 999)}"
        self.name = name
        self.group_type = group_type # 文物3D, 采样音频, 视觉素材, 文献扫描
        self.extension = random.choice(['.GLB', '.WAV', '.TIFF', '.MP4', '.FBX'])
        self.file_size = random.randint(200, 10240) # MB
        
        # 原始特征数据
        self.gene_metrics = {
            'scarcity': random.randint(35, 98),
            'technical': random.randint(60, 99),
            'heritage': random.randint(30, 95),
            'potential': random.randint(40, 90),
            'duration_months': random.randint(0, 72)
        }
        
        # 初始化价值计算
        self.valuation = ResourceEngine.evaluate_node(self.gene_metrics)
        self.is_encrypted = True
        self.tags = ["核心归档", "数字化转存"]
        self.logs = [f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} 原始节点挂载成功"]

# --- 视觉组件层 ---

class ResourceVisualCard(QFrame):
    """自定义资产卡片，包含高精度视觉反馈"""
    triggered = pyqtSignal(object)

    def __init__(self, entity, parent=None):
        super().__init__(parent)
        self.entity = entity
        self.setFixedSize(180, 225)
        self._build_style()

    def _build_style(self):
        self.setObjectName("ResourceCard")
        # 逻辑：分值越高，边框越具有“科技蓝”质感
        border_hue = "#0ea5e9" if self.entity.valuation > 85 else "#cbd5e1"
        self.setStyleSheet(f"""
            #ResourceCard {{
                background-color: #ffffff;
                border: 1px solid {border_hue};
                border-radius: 8px;
            }}
            #ResourceCard:hover {{
                border: 2px solid #0284c7;
                background-color: #f8fafc;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        
        # 预览区
        self.media_placeholder = QFrame()
        self.media_placeholder.setFixedHeight(110)
        # 根据类型分配色块颜色
        palette = {"文物3D": "#1e293b", "采样音频": "#1e3a8a", "视觉素材": "#064e3b", "文献扫描": "#3f6212"}
        bg_color = palette.get(self.entity.group_type, "#1e293b")
        self.media_placeholder.setStyleSheet(f"background-color: {bg_color}; border-radius: 4px;")
        
        name_lbl = QLabel(self.entity.name)
        name_lbl.setStyleSheet("font-weight: 700; color: #1e293b; font-size: 11px;")
        name_lbl.setWordWrap(True)
        
        # 价值雷达条
        self.v_indicator = QProgressBar()
        self.v_indicator.setFixedHeight(4)
        self.v_indicator.setTextVisible(False)
        self.v_indicator.setValue(int(self.entity.valuation))
        self.v_indicator.setStyleSheet("QProgressBar::chunk { background-color: #38bdf8; }")
        
        layout.addWidget(self.media_placeholder)
        layout.addWidget(name_lbl)
        layout.addStretch()
        layout.addWidget(self.v_indicator)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.triggered.emit(self.entity)

# --- 主模块：资产管理核心工作台 ---

class EntryWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.db_snapshot = []
        self.current_active = None
        self._seed_data()
        self._init_core_ui()

    def _seed_data(self):
        """填充仿真业务数据集"""
        types = ["文物3D", "采样音频", "视觉素材", "文献扫描"]
        samples = ["莫高窟北魏壁画采集", "古琴散音长采样", "故宫建筑拓扑模型", "永乐大典残卷扫描", "皮影动作捕捉包"]
        for i in range(35):
            self.db_snapshot.append(DigitalAssetEntity(f"{random.choice(samples)}-{i:03d}", random.choice(types)))

    def _init_core_ui(self):
        self.root_layout = QVBoxLayout(self)
        self.root_layout.setContentsMargins(0, 0, 0, 0)
        self.root_layout.setSpacing(0)

        # 1. 顶部操作矩阵 (解决 QToolBar 不支持 addStretch 的问题)
        self.top_control = QToolBar()
        self.top_control.setStyleSheet("background: white; border-bottom: 1px solid #e2e8f0; padding: 12px;")
        
        self.query_field = QLineEdit()
        self.query_field.setPlaceholderText("检索资产唯一识别码或语义标签...")
        self.query_field.setFixedWidth(350)
        self.query_field.textChanged.connect(self._exec_query)
        
        self.type_selector = QComboBox()
        self.type_selector.addItems(["全部资产领域", "文物3D", "采样音频", "视觉素材", "文献扫描"])
        self.type_selector.currentTextChanged.connect(self._exec_query)

        btn_import = QPushButton("＋ 资源接入")
        btn_import.setObjectName("ActionBtn")
        btn_import.clicked.connect(self._handle_create_flow)

        self.top_control.addWidget(QLabel(" 筛选器: "))
        self.top_control.addWidget(self.type_selector)
        self.top_control.addSeparator()
        self.top_control.addWidget(self.query_field)
        
        # 修复报错点：QToolBar 不支持 addStretch，必须手动添加一个 Expanding 的 Widget
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.top_control.addWidget(spacer)
        
        self.top_control.addWidget(btn_import)
        self.root_layout.addWidget(self.top_control)

        # 2. 核心分割工作台
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # --- 左侧：资产网格导航流 ---
        self.scroll_view = QScrollArea()
        self.scroll_view.setWidgetResizable(True)
        self.scroll_view.setStyleSheet("background-color: #f1f5f9; border: none;")
        
        self.grid_wrapper = QWidget()
        self.grid_layout = QGridLayout(self.grid_wrapper)
        self.grid_layout.setSpacing(25)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.scroll_view.setWidget(self.grid_wrapper)
        
        self.splitter.addWidget(self.scroll_view)

        # --- 右侧：高阶属性分析面板 (CRUD + 算法控制) ---
        self.inspector = QFrame()
        self.inspector.setFixedWidth(460)
        self.inspector.setStyleSheet("background: white; border-left: 1px solid #e2e8f0;")
        self.ins_layout = QVBoxLayout(self.inspector)
        
        self._build_inspector_ui()
        
        self.splitter.addWidget(self.inspector)
        self.splitter.setStretchFactor(0, 3)
        self.splitter.setStretchFactor(1, 1)
        
        self.root_layout.addWidget(self.splitter)
        
        # 初始化渲染
        self._refresh_matrix(self.db_snapshot)

    def _build_inspector_ui(self):
        """构建详细审查逻辑堆栈"""
        self.stack = QStackedWidget()
        
        # 空白页
        self.empty_v = QLabel("请在左侧矩阵中\n定位一个数字资产以开启推演面板")
        self.empty_v.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_v.setStyleSheet("color: #94a3b8; font-style: italic;")
        
        # 工作台页
        self.editor_v = QWidget()
        ev_layout = QVBoxLayout(self.editor_v)
        
        self.tabs = QTabWidget()
        
        # Tab 1: 核心元数据 (Update 逻辑)
        self.meta_tab = QWidget()
        form = QFormLayout(self.meta_tab)
        self.in_name = QLineEdit()
        self.in_id = QLineEdit(); self.in_id.setReadOnly(True); self.in_id.setStyleSheet("background: #f8fafc;")
        self.in_type = QComboBox(); self.in_type.addItems(["文物3D", "采样音频", "视觉素材", "文献扫描"])
        self.in_tags = QLineEdit()
        form.addRow("资产标记名称:", self.in_name)
        form.addRow("系统溯源ID:", self.in_id)
        form.addRow("业务逻辑分类:", self.in_type)
        form.addRow("关联描述标签:", self.in_tags)
        self.tabs.addTab(self.meta_tab, "元数据视图")
        
        # Tab 2: 价值推演引擎 (算法深度交互)
        self.algo_tab = QWidget()
        al_layout = QVBoxLayout(self.algo_tab)
        self.sliders = {}
        for key, text in [('scarcity', '文化稀缺度'), ('technical', '技术规格指标'), 
                          ('heritage', '文物底蕴分值'), ('potential', '二次开发潜力')]:
            row = QVBoxLayout()
            row.addWidget(QLabel(f"{text}:"))
            s = QSlider(Qt.Orientation.Horizontal)
            s.setRange(0, 100)
            row.addWidget(s)
            al_layout.addLayout(row)
            self.sliders[key] = s
            
        self.btn_run_eval = QPushButton("启动引擎同步推演")
        self.btn_run_eval.setStyleSheet("background: #0f172a; color: white; font-weight: bold; padding: 10px;")
        self.btn_run_eval.clicked.connect(self._run_valuation_update)
        al_layout.addWidget(self.btn_run_eval)
        self.tabs.addTab(self.algo_tab, "价值算法矩阵")
        
        # Tab 3: 操作日志快照
        self.log_list = QListWidget()
        self.tabs.addTab(self.log_list, "审计日志流")
        
        ev_layout.addWidget(self.tabs)
        
        # 全局动作
        action_row = QHBoxLayout()
        btn_save = QPushButton("💾 提交变更至矩阵库")
        btn_save.setFixedHeight(45)
        btn_save.setStyleSheet("background: #0284c7; color: white; font-weight: 800; border-radius: 4px;")
        btn_save.clicked.connect(self._commit_update)
        
        btn_del = QPushButton("销毁")
        btn_del.setFixedWidth(70)
        btn_del.setFixedHeight(45)
        btn_del.setStyleSheet("background: #fee2e2; color: #b91c1c;")
        btn_del.clicked.connect(self._handle_delete_sequence)
        
        action_row.addWidget(btn_del)
        action_row.addWidget(btn_save)
        ev_layout.addLayout(action_row)

        self.stack.addWidget(self.empty_v)
        self.stack.addWidget(self.editor_v)
        self.ins_layout.addWidget(self.stack)

    # --- 核心交互流水线 ---

    def _deep_clear_layout(self, layout):
        """修复逻辑：递归清理布局项，安全检查 widget 对象"""
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                w = item.widget()
                if w is not None:
                    w.deleteLater()
                else:
                    sub = item.layout()
                    if sub:
                        self._deep_clear_layout(sub)

    def _refresh_matrix(self, dataset):
        """网格矩阵渲染逻辑"""
        self._deep_clear_layout(self.grid_layout)
        # 响应式列数计算
        cols = max(1, (self.scroll_view.width() - 40) // 200)
        for i, entity in enumerate(dataset):
            card = ResourceVisualCard(entity)
            card.triggered.connect(self._activate_inspector)
            self.grid_layout.addWidget(card, i // cols, i % cols)

    def _activate_inspector(self, entity):
        self.current_active = entity
        self.stack.setCurrentIndex(1)
        
        # 加载元数据
        self.in_name.setText(entity.name)
        self.in_id.setText(entity.asset_id)
        self.in_type.setCurrentText(entity.group_type)
        self.in_tags.setText(", ".join(entity.tags))
        
        # 同步算法滑块
        for k, slider in self.sliders.items():
            slider.setValue(entity.gene_metrics.get(k, 50))
            
        # 载入日志
        self.log_list.clear()
        self.log_list.addItems(reversed(entity.logs))

    def _exec_query(self):
        """复合查询处理流水线"""
        kw = self.query_field.text().lower()
        cat = self.type_selector.currentText()
        
        output = [
            e for e in self.db_snapshot if 
            (kw in e.name.lower() or kw in e.asset_id.lower()) and
            (cat == "全部资产领域" or e.group_type == cat)
        ]
        self._refresh_matrix(output)

    def _run_valuation_update(self):
        """核心业务逻辑：触发价值评估算法更新"""
        if not self.current_active: return
        
        # 采集滑块数据
        for k, slider in self.sliders.items():
            self.current_active.gene_metrics[k] = slider.value()
            
        # 重新执行引擎计算
        new_val = ResourceEngine.evaluate_node(self.current_active.gene_metrics)
        self.current_active.valuation = new_val
        self.current_active.logs.append(f"{datetime.now().strftime('%H:%M:%S')} [算法中心] 价值重估分值: {new_val}")
        
        # 更新显示
        self._activate_inspector(self.current_active)
        self._exec_query()

    def _commit_update(self):
        """CRUD - Update 持久化逻辑"""
        if not self.current_active: return
        
        target_name = self.in_name.text().strip()
        if not target_name:
            QMessageBox.critical(self, "数据校验", "资源名称不能为空。")
            return
            
        self.current_active.name = target_name
        self.current_active.group_type = self.in_type.currentText()
        self.current_active.tags = [t.strip() for t in self.in_tags.text().split(",") if t.strip()]
        self.current_active.logs.append(f"{datetime.now().strftime('%H:%M:%S')} [人工校准] 元数据同步完成")
        
        QMessageBox.information(self, "同步成功", f"资产标识 {self.current_active.asset_id} 的变更已持久化。")
        self._exec_query()

    def _handle_create_flow(self):
        """CRUD - Create 接入逻辑"""
        file_path, _ = QFileDialog.getOpenFileName(self, "选择素材接入流...", "", "Digital Assets (*.glb *.wav *.tiff *.mp4)")
        if file_path:
            f_name = os.path.basename(file_path)
            new_item = DigitalAssetEntity(f_name, "文献扫描")
            self.db_snapshot.insert(0, new_item)
            self._exec_query()
            QMessageBox.information(self, "入库完成", f"新资产 {f_name} 已成功挂载。")

    def _handle_delete_sequence(self):
        """CRUD - Delete 销毁逻辑"""
        if not self.current_active: return
        
        reply = QMessageBox.question(
            self, "销毁确认", 
            f"您正在执行高危删除操作。\n资源 [{self.current_active.name}] 将从矩阵中彻底注销。\n确认继续？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.db_snapshot.remove(self.current_active)
            self.current_active = None
            self.stack.setCurrentIndex(0)
            self._exec_query()

    def resizeEvent(self, event):
        """响应式适配：根据视口宽度实时调整网格列数"""
        super().resizeEvent(event)
        QTimer.singleShot(150, self._exec_query)

    def __del__(self):
        # 系统资源释放
        pass