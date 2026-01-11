import importlib
import sys
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

class ModuleManager:
    """模块动态加载与注入中心"""
    def __init__(self, container):
        self.container = container
        self.active_module = None

    def switch_module(self, module_name):
        try:
            # 强制重新加载模块以实现热更新
            full_module_path = f"modules.{module_name}"
            if full_module_path in sys.modules:
                importlib.reload(sys.modules[full_module_path])
            
            mod = importlib.import_module(full_module_path)
            
            # 约定：每个模块必须包含一个 EntryWidget 类
            new_widget = mod.EntryWidget()
            
            # 清理旧视图
            if self.active_module:
                self.container.layout().removeWidget(self.active_module)
                self.active_module.deleteLater()
            
            self.container.layout().addWidget(new_widget)
            self.active_module = new_widget
            
        except Exception as e:
            print(f"Module Load Error [{module_name}]: {e}")