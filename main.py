import sys
import os
import traceback
import math
import time
from datetime import datetime

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QPushButton, QLineEdit, QLabel, 
    QFrame, QStackedWidget, QMessageBox, QGraphicsDropShadowEffect,
    QSizePolicy
)
from PyQt6.QtCore import Qt, QSize, QTimer, QPoint
from PyQt6.QtGui import QFont, QColor, QIcon, QLinearGradient

# --- [核心补丁：打包路径兼容逻辑] ---

def resource_path(relative_path):
    """ 获取资源的绝对路径，兼容开发环境与 PyInstaller 打包后的单文件环境 """
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller 打包后的解压临时目录
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# 将解压后的根目录加入系统路径，确保 importlib 能加载 modules 下的文件
if hasattr(sys, '_MEIPASS'):
    sys.path.append(sys._MEIPASS)

# 尝试导入核心层逻辑
try:
    from manager import ModuleManager
    from core.auth import SessionProvider
except ImportError:
    # 紧急容错逻辑 (若核心组件缺失则定义占位)
    class SessionProvider:
        @staticmethod
        def verify_credential(u, p):
            return (True, "DEBUG_MODE") if u == "admin" and p == "123456" else (False, "AUTH_ERR")
    class ModuleManager:
        def __init__(self, c): self.c = c
        def switch_module(self, m): print(f"Switching to {m}")

# --- [UI 逻辑层：高阶科技感鉴权门户] ---

class LoginWindow(QWidget):
    """
    数字文化系统 - 硬核工业风格准入终端
    特性：非透明、高对比度色块、模拟系统自检
    """
    def __init__(self, success_callback):
        super().__init__()
        self.success_callback = success_callback
        # 移除系统边框
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setFixedSize(900, 560)
        
        self.m_drag = False
        self.m_DragPosition = QPoint()

        self._init_layout()
        self._apply_qss()

    def _init_layout(self):
        self.root_layout = QHBoxLayout(self)
        self.root_layout.setContentsMargins(0, 0, 0, 0)
        self.root_layout.setSpacing(0)

        # --- 左侧：核心品牌与状态监视 ---
        self.left_panel = QFrame()
        self.left_panel.setObjectName("LeftPanel")
        left_layout = QVBoxLayout(self.left_panel)
        left_layout.setContentsMargins(45, 60, 45, 60)

        # 品牌区
        brand_row = QHBoxLayout()
        icon_label = QLabel("⌬")
        icon_label.setStyleSheet("font-size: 40px; color: #00f2ff; border: 2px solid #00f2ff; padding: 10px; background: #1a2233;")
        
        title_stack = QVBoxLayout()
        t_main = QLabel("MATRIX")
        t_main.setStyleSheet("font-size: 32px; font-weight: 900; color: #ffffff; letter-spacing: 5px;")
        t_sub = QLabel("CULTURE CONTENT ENGINE")
        t_sub.setStyleSheet("font-size: 10px; color: #00f2ff; letter-spacing: 1px;")
        title_stack.addWidget(t_main); title_stack.addWidget(t_sub)
        
        brand_row.addWidget(icon_label); brand_row.addLayout(title_stack); brand_row.addStretch()

        # 系统扫描状态模拟
        self.terminal = QLabel(
            "> BOOT_SEQUENCE: COMPLETED\n"
            "> NODES_ACTIVE: 12/12\n"
            "> DATABASE: ENCRYPTED_LINK\n"
            "> AUTH_SERVICE: READY"
        )
        self.terminal.setStyleSheet("""
            font-family: 'Consolas', 'Monaco', monospace;
            color: #4ade80; font-size: 11px; background: #000000;
            padding: 20px; border-left: 4px solid #4ade80;
        """)

        left_layout.addLayout(brand_row)
        left_layout.addSpacing(70)
        left_layout.addWidget(self.terminal)
        left_layout.addStretch()
        
        ver_info = QLabel("MATRIX_CORE_STABLE_V1.0.8")
        ver_info.setStyleSheet("color: #475569; font-size: 9px; font-family: 'Consolas';")
        left_layout.addWidget(ver_info)

        # --- 右侧：鉴权表单 ---
        self.right_panel = QFrame()
        self.right_panel.setObjectName("RightPanel")
        right_layout = QVBoxLayout(self.right_panel)
        right_layout.setContentsMargins(70, 50, 70, 50)

        # 退出按钮区
        top_ctrl = QHBoxLayout()
        top_ctrl.addStretch()
        exit_btn = QPushButton("EXIT_OS")
        exit_btn.setStyleSheet("""
            QPushButton { background: transparent; color: #ef4444; border: 1px solid #ef4444; 
            font-family: 'Consolas'; font-size: 10px; padding: 5px 12px; }
            QPushButton:hover { background: #ef4444; color: white; }
        """)
        exit_btn.clicked.connect(QApplication.instance().quit)
        top_ctrl.addWidget(exit_btn)

        # 表单标题
        auth_head = QLabel("AUTHENTICATION")
        auth_head.setStyleSheet("color: white; font-size: 24px; font-weight: 800; letter-spacing: 3px; border-left: 5px solid #38bdf8; padding-left: 20px;")

        self.u_input = QLineEdit(); self.u_input.setPlaceholderText("ID / 用户名")
        self.u_input.setText("admin") # 预填
        self.p_input = QLineEdit(); self.p_input.setPlaceholderText("ACCESS KEY")
        self.p_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.p_input.setText("123456") # 预填

        self.msg_label = QLabel("STATUS: AWAITING_INPUT")
        self.msg_label.setStyleSheet("color: #64748b; font-family: 'Consolas'; font-size: 10px;")

        self.login_btn = QPushButton("INITIALIZE_SYSTEM")
        self.login_btn.setStyleSheet("""
            QPushButton { background: #38bdf8; color: #020617; font-weight: 900; 
            font-size: 15px; letter-spacing: 2px; padding: 15px; border-radius: 2px; }
            QPushButton:hover { background: #7dd3fc; }
            QPushButton:disabled { background: #1e293b; color: #475569; }
        """)
        self.login_btn.clicked.connect(self.execute_auth)

        right_layout.addLayout(top_ctrl)
        right_layout.addStretch()
        right_layout.addWidget(auth_head)
        right_layout.addSpacing(40)
        right_layout.addWidget(self.u_input)
        right_layout.addSpacing(20)
        right_layout.addWidget(self.p_input)
        right_layout.addWidget(self.msg_label)
        right_layout.addSpacing(40)
        right_layout.addWidget(self.login_btn)
        right_layout.addStretch()

        self.root_layout.addWidget(self.left_panel, 4)
        self.root_layout.addWidget(self.right_panel, 5)

    def _apply_qss(self):
        """ 应用样式表，优先读取外部 QSS，否则使用内联兜底 """
        self.setStyleSheet("""
            #LeftPanel { background-color: #0f172a; border-right: 1px solid #1e293b; }
            #RightPanel { background-color: #020617; }
            QLineEdit { background-color: #1e293b; border: 1px solid #334155; color: #38bdf8; 
                        padding: 12px; border-radius: 2px; font-family: 'Consolas'; font-size: 14px; }
            QLineEdit:focus { border: 1px solid #00f2ff; background-color: #0f172a; }
        """)

    def execute_auth(self):
        self.login_btn.setEnabled(False)
        self.msg_label.setText(">> ATTEMPTING HANDSHAKE WITH CORE ENGINE...")
        self.msg_label.setStyleSheet("color: #38bdf8; font-size: 10px;")
        
        # 模拟 1.2s 的高科技扫描延迟
        QTimer.singleShot(1200, self._finalize_auth)

    def _finalize_auth(self):
        u, p = self.u_input.text(), self.p_input.text()
        success, msg = SessionProvider.verify_credential(u, p)
        if success:
            self.success_callback()
        else:
            self.msg_label.setText(f">> ACCESS_DENIED: {msg.upper()}")
            self.msg_label.setStyleSheet("color: #f43f5e; font-size: 10px;")
            self.login_btn.setEnabled(True)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.m_drag = True
            self.m_DragPosition = event.globalPosition().toPoint() - self.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        if Qt.MouseButton.LeftButton and self.m_drag:
            self.move(event.globalPosition().toPoint() - self.m_DragPosition)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.m_drag = False

# --- [主架构层：业务调度中心] ---

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("数字文化内容策划与发布管理系统 v1.0")
        self.resize(1300, 850)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.root_layout = QHBoxLayout(self.central_widget)
        self.root_layout.setContentsMargins(0, 0, 0, 0)
        self.root_layout.setSpacing(0)
        
        self._init_sidebar()
        self._init_viewport()

    def _init_sidebar(self):
        self.sidebar = QFrame()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setFixedWidth(250)
        self.sidebar.setStyleSheet("""
            QFrame#Sidebar { background-color: #1e293b; border-right: 1px solid #0f172a; }
            QPushButton { color: #94a3b8; border: none; padding: 18px 25px; 
                          text-align: left; font-size: 14px; background: transparent; }
            QPushButton:hover { background-color: #334155; color: #f8fafc; }
            QPushButton#Active { background-color: #38bdf8; color: #020617; font-weight: bold; border-left: 5px solid #00f2ff; }
        """)
        
        sb_layout = QVBoxLayout(self.sidebar)
        sb_layout.setContentsMargins(0, 20, 0, 20)
        
        logo_lbl = QLabel("MATRIX ENGINE")
        logo_lbl.setStyleSheet("color: #38bdf8; font-weight: 900; font-size: 18px; padding: 25px; letter-spacing: 2px;")
        sb_layout.addWidget(logo_lbl)

        # 九大核心矩阵菜单
        self.menus = [
            ("控制面板", "dashboard"), ("内容策划", "planning"), ("资产总库", "resources"),
            ("流程审批", "workflow"), ("分发矩阵", "distribution"), ("排期中心", "schedule"),
            ("数据归因", "analytics"), ("版权监控", "copyright"), ("反馈治理", "feedback")
        ]
        
        self.nav_btns = {}
        for text, mid in self.menus:
            btn = QPushButton(text)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, a=mid: self.switch_view(a))
            sb_layout.addWidget(btn)
            self.nav_btns[mid] = btn
            
        sb_layout.addStretch()
        self.root_layout.addWidget(self.sidebar)

    def _init_viewport(self):
        self.viewport = QWidget()
        self.viewport.setStyleSheet("background-color: #f8fafc;")
        self.view_layout = QVBoxLayout(self.viewport)
        self.root_layout.addWidget(self.viewport, 1)
        
        # 实例化动态调度器
        self.manager = ModuleManager(self.viewport)
        
        # 初始默认视图
        self.switch_view("dashboard")

    def switch_view(self, mid):
        # 样式切换逻辑
        for k, b in self.nav_btns.items():
            b.setObjectName("Active" if k == mid else "")
        self.sidebar.setStyleSheet(self.sidebar.styleSheet())
        
        # 动态加载模块 (Manager 内部含 importlib 逻辑)
        self.manager.switch_module(mid)

def main():
    """ 引擎入口：集成全局异常监控与路径注入 """
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # 全局字体优化
    font_family = "PingFang SC" if sys.platform == "darwin" else "Microsoft YaHei"
    app.setFont(QFont(font_family, 10))

    main_win = MainWindow()
    
    def on_launch():
        login_ui.close()
        main_win.show()

    login_ui = LoginWindow(success_callback=on_launch)
    login_ui.show()

    try:
        print(">>> 数字化系统内核已就绪，正在监听指令流...")
        sys.exit(app.exec())
    except Exception:
        print("--- 系统发生致命崩溃，正在生成报告 ---")
        traceback.print_exc()

if __name__ == "__main__":
    main()