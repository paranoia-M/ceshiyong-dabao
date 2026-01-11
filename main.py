import sys
import os
import traceback
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLineEdit, QLabel, 
                             QFrame, QStackedWidget, QMessageBox, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, QSize, QTimer, QPoint
from PyQt6.QtGui import QFont, QColor, QIcon

# 确保核心调度器与鉴权服务可被加载
try:
    from manager import ModuleManager
    from core.auth import SessionProvider
except ImportError:
    # 这里的占位逻辑是为了防止你还没创建对应文件导致主程序直接崩掉
    class SessionProvider:
        @staticmethod
        def verify_credential(u, p):
            return (True, "OK") if u == "admin" and p == "123456" else (False, "ERR")
    class ModuleManager:
        def __init__(self, c): self.c = c
        def switch_module(self, m): print(f"Switching to {m}")

class LoginWindow(QWidget):
    """
    数字文化系统 - 安全准入门户
    设计语言：实色块、高对比度、工业科技感
    """
    def __init__(self, success_callback):
        super().__init__()
        self.success_callback = success_callback
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setFixedSize(900, 560)
        
        self.m_drag = False
        self.m_DragPosition = QPoint()

        self._init_layout()
        self._setup_styles()

    def _init_layout(self):
        # 消除外边距，确保背景色充满整个窗口
        self.root_layout = QHBoxLayout(self)
        self.root_layout.setContentsMargins(0, 0, 0, 0)
        self.root_layout.setSpacing(0)

        # --- 左侧：系统引擎视觉区 ---
        self.left_panel = QFrame()
        self.left_panel.setObjectName("LeftPanel")
        left_layout = QVBoxLayout(self.left_panel)
        left_layout.setContentsMargins(45, 60, 45, 60)

        # 品牌标识
        brand_box = QHBoxLayout()
        icon_label = QLabel("⚡")
        icon_label.setObjectName("TechIcon")
        
        brand_text_layout = QVBoxLayout()
        main_title = QLabel("")
        main_title.setStyleSheet("font-size: 32px; font-weight: 900; color: #ffffff; letter-spacing: 5px;")
        sub_title = QLabel("")
        sub_title.setStyleSheet("font-size: 10px; color: #00f2ff; letter-spacing: 1px;")
        brand_text_layout.addWidget(main_title)
        brand_text_layout.addWidget(sub_title)
        
        brand_box.addWidget(icon_label)
        brand_box.addLayout(brand_text_layout)
        brand_box.addStretch()

        # 核心逻辑扫描显示
        self.terminal_box = QLabel(
            "> INITIALIZING SECURITY PROTOCOL...\n"
            "> CORE_DB: CONNECTED\n"
            "> ENCRYPTION_LEVEL: AES_256_GCM\n"
            "> NODES: 12 ACTIVE"
        )
        self.terminal_box.setObjectName("TerminalBox")

        left_layout.addLayout(brand_box)
        left_layout.addSpacing(70)
        left_layout.addWidget(self.terminal_box)
        left_layout.addStretch()
        
        footer_tag = QLabel("")
        footer_tag.setStyleSheet("color: #475569; font-size: 9px; font-family: 'Consolas';")
        left_layout.addWidget(footer_tag)

        # --- 右侧：鉴权控制区 ---
        self.right_panel = QFrame()
        self.right_panel.setObjectName("RightPanel")
        right_layout = QVBoxLayout(self.right_panel)
        right_layout.setContentsMargins(70, 50, 70, 50)

        # 顶部操作条
        top_bar = QHBoxLayout()
        top_bar.addStretch()
        exit_btn = QPushButton("EXIT_SYSTEM")
        exit_btn.setObjectName("ExitBtn")
        exit_btn.clicked.connect(QApplication.instance().quit)
        top_bar.addWidget(exit_btn)

        # 登录表单
        auth_header = QLabel("数字文化内容策划\n与发布管理系统")
        auth_header.setObjectName("AuthHeader")

        self.u_input = QLineEdit()
        self.u_input.setPlaceholderText("ID / 用户名")
        self.u_input.setText("admin") # 默认值

        self.p_input = QLineEdit()
        self.p_input.setPlaceholderText("KEY / 访问密钥")
        self.p_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.p_input.setText("123456") # 默认值

        self.status_label = QLabel("STATUS: SYSTEM_READY")
        self.status_label.setObjectName("StatusLabel")

        self.login_btn = QPushButton("进入系统")
        self.login_btn.setObjectName("LoginBtn")
        self.login_btn.clicked.connect(self.process_login)

        right_layout.addLayout(top_bar)
        right_layout.addStretch()
        right_layout.addWidget(auth_header)
        right_layout.addSpacing(40)
        right_layout.addWidget(self.u_input)
        right_layout.addSpacing(20)
        right_layout.addWidget(self.p_input)
        right_layout.addWidget(self.status_label)
        right_layout.addSpacing(40)
        right_layout.addWidget(self.login_btn)
        right_layout.addStretch()

        self.root_layout.addWidget(self.left_panel, 4)
        self.root_layout.addWidget(self.right_panel, 5)

    def _setup_styles(self):
        # 采用实色块QSS，彻底杜绝背景穿透
        self.setStyleSheet("""
            #LeftPanel {
                background-color: #0f172a;
                border-right: 1px solid #1e293b;
            }
            #RightPanel {
                background-color: #020617;
            }
            #TechIcon {
                font-size: 38px; 
                color: #00f2ff; 
                background: #1a2233; 
                padding: 12px; 
                border: 2px solid #00f2ff;
            }
            #TerminalBox {
                font-family: 'Consolas', 'Monaco', monospace; 
                color: #4ade80; 
                font-size: 11px; 
                background: #000000; 
                padding: 20px; 
                border-left: 4px solid #4ade80;
            }
            #AuthHeader {
                color: #f8fafc;
                font-size: 24px;
                font-weight: 800;
                letter-spacing: 3px;
                border-left: 5px solid #38bdf8;
                padding-left: 20px;
                margin-bottom: 10px;
            }
            QLineEdit {
                background-color: #1e293b;
                border: 1px solid #334155;
                color: #38bdf8;
                padding: 12px;
                border-radius: 2px;
                font-family: 'Consolas';
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #00f2ff;
                background-color: #0f172a;
            }
            #StatusLabel {
                color: #64748b;
                font-family: 'Consolas';
                font-size: 10px;
                margin-top: 8px;
            }
            #LoginBtn {
                background-color: #38bdf8;
                color: #020617;
                border: none;
                font-weight: 900;
                font-size: 15px;
                letter-spacing: 2px;
                padding: 15px;
                border-radius: 2px;
            }
            #LoginBtn:hover {
                background-color: #7dd3fc;
            }
            #LoginBtn:disabled {
                background-color: #334155;
                color: #475569;
            }
            #ExitBtn {
                background: transparent;
                color: #ef4444;
                border: 1px solid #ef4444;
                font-family: 'Consolas';
                font-size: 10px;
                padding: 6px 12px;
            }
            #ExitBtn:hover {
                background: #ef4444;
                color: #ffffff;
            }
        """)

    def process_login(self):
        self.login_btn.setEnabled(False)
        self.status_label.setText(">> CALLING AUTH_PROVIDER... PLEASE WAIT")
        self.status_label.setStyleSheet("color: #38bdf8;")
        # 增加科技感等待反馈
        QTimer.singleShot(1200, self._exec_auth)

    def _exec_auth(self):
        u = self.u_input.text()
        p = self.p_input.text()
        valid, msg = SessionProvider.verify_credential(u, p)
        
        if valid:
            self.success_callback()
        else:
            self.status_label.setText(f">> ACCESS_DENIED: {msg.upper()}")
            self.status_label.setStyleSheet("color: #f43f5e;")
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

class MainWindow(QMainWindow):
    """
    业务调度主视窗
    包含侧边导航栏及九大业务模块占位视口
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("数字文化内容策划与发布管理系统 v1.0")
        self.resize(1280, 800)
        # 基础框架
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QHBoxLayout(self.central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        self._init_sidebar()
        self._init_viewport()

    def _init_sidebar(self):
        self.sidebar = QFrame()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setFixedWidth(240)
        self.sidebar.setStyleSheet("""
            QFrame#Sidebar { background-color: #1e293b; border-right: 1px solid #0f172a; }
            QPushButton { 
                color: #94a3b8; border: none; padding: 18px 25px; 
                text-align: left; font-size: 14px; background: transparent;
            }
            QPushButton:hover { background-color: #334155; color: #f8fafc; }
            QPushButton#Active { 
                background-color: #38bdf8; color: #020617; font-weight: bold; 
                border-left: 4px solid #00f2ff;
            }
        """)
        
        sb_layout = QVBoxLayout(self.sidebar)
        sb_layout.setContentsMargins(0, 20, 0, 20)
        
        logo = QLabel("")
        logo.setStyleSheet("color: #38bdf8; font-weight: 900; font-size: 18px; padding: 20px; letter-spacing: 2px;")
        sb_layout.addWidget(logo)

        # 定义九大模块
        self.menu_configs = [
            ("控制面板", "dashboard"),
            ("内容策划", "planning"),
            ("资产库", "resources"),
            ("流程审批", "workflow"),
            ("发布渠道", "distribution"),
            ("排期计划", "schedule"),
            ("数据透视", "analytics"),
            ("版权卫士", "copyright"),
            ("反馈管理", "feedback")
        ]
        
        self.buttons = {}
        for text, mid in self.menu_configs:
            btn = QPushButton(text)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, a=mid: self.switch_module(a))
            sb_layout.addWidget(btn)
            self.buttons[mid] = btn
            
        sb_layout.addStretch()
        self.layout.addWidget(self.sidebar)

    def _init_viewport(self):
        self.viewport = QWidget()
        self.viewport.setStyleSheet("background-color: #f8fafc;")
        self.vp_layout = QVBoxLayout(self.viewport)
        self.layout.addWidget(self.viewport, 1)
        
        # 初始化模块管理器
        self.module_manager = ModuleManager(self.viewport)
        
        # 默认加载
        self.switch_module("dashboard")

    def switch_module(self, mid):
        for k, b in self.buttons.items():
            b.setObjectName("Active" if k == mid else "")
        self.sidebar.setStyleSheet(self.sidebar.styleSheet()) # 刷新样式
        
        self.module_manager.switch_module(mid)

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # 字体优化
    f = QFont("PingFang SC", 10) if sys.platform == "darwin" else QFont("Microsoft YaHei", 10)
    app.setFont(f)

    main_win = MainWindow()
    
    def on_success():
        login_ui.close()
        main_win.show()

    login_ui = LoginWindow(success_callback=on_success)
    login_ui.show()

    try:
        print(">>> 数字化文化系统核心就绪...")
        sys.exit(app.exec())
    except Exception:
        traceback.print_exc()

if __name__ == "__main__":
    main()