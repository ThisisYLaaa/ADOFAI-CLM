from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QCheckBox, QFileDialog
from UI.settings_manager import SettingsManager

class SettingsWindow(QDialog):
    """设置窗口"""
    def __init__(self, settings_manager: SettingsManager, parent=None):
        super().__init__(parent)
        self.settings_manager = settings_manager
        self.setWindowTitle("设置")
        self.setMinimumSize(500, 200)
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        """初始化UI"""
        # 主布局
        main_layout = QVBoxLayout(self)

        # 父文件夹路径设置
        parent_dir_layout = QHBoxLayout()
        parent_dir_label = QLabel("父文件夹路径:")
        self.parent_dir_edit = QLineEdit()
        self.browse_button = QPushButton("浏览")
        self.browse_button.clicked.connect(self.browse_parent_dir)
        parent_dir_layout.addWidget(parent_dir_label)
        parent_dir_layout.addWidget(self.parent_dir_edit)
        parent_dir_layout.addWidget(self.browse_button)
        main_layout.addLayout(parent_dir_layout)

        # 自动重载设置
        auto_reload_layout = QHBoxLayout()
        self.auto_reload_checkbox = QCheckBox("程序启动时自动重载")
        auto_reload_layout.addWidget(self.auto_reload_checkbox)
        main_layout.addLayout(auto_reload_layout)

        # 缓存文件名称设置
        cache_filename_layout = QHBoxLayout()
        cache_filename_label = QLabel("缓存文件名称:")
        self.cache_filename_edit = QLineEdit()
        cache_filename_layout.addWidget(cache_filename_label)
        cache_filename_layout.addWidget(self.cache_filename_edit)
        main_layout.addLayout(cache_filename_layout)

        # 按钮布局
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("保存")
        self.save_button.clicked.connect(self.save_settings)
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addStretch()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        main_layout.addLayout(button_layout)

    def load_settings(self):
        """加载设置"""
        settings = self.settings_manager.settings
        self.parent_dir_edit.setText(settings.parent_dir)
        self.auto_reload_checkbox.setChecked(settings.auto_reload)
        self.cache_filename_edit.setText(settings.cache_filename)

    def browse_parent_dir(self):
        """浏览父文件夹"""
        dir_path = QFileDialog.getExistingDirectory(
            self,
            "选择父文件夹",
            self.parent_dir_edit.text() or ".",
            QFileDialog.Option.ShowDirsOnly | QFileDialog.Option.DontResolveSymlinks
        )
        if dir_path:
            self.parent_dir_edit.setText(dir_path)

    def save_settings(self):
        """保存设置"""
        parent_dir = self.parent_dir_edit.text()
        auto_reload = self.auto_reload_checkbox.isChecked()
        cache_filename = self.cache_filename_edit.text()

        self.settings_manager.update_settings(
            parent_dir=parent_dir,
            auto_reload=auto_reload,
            cache_filename=cache_filename
        )
        self.accept()
