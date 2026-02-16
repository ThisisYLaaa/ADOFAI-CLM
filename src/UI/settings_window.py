from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QCheckBox, QFileDialog, QListWidget, QListWidgetItem, QInputDialog, QMessageBox
from src.UI.settings_manager import SettingsManager

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

        # .adofai文件搜索优先级设置
        adofai_priority_layout = QVBoxLayout()
        adofai_priority_label = QLabel(".adofai文件搜索优先级:")
        adofai_priority_layout.addWidget(adofai_priority_label)
        
        # 优先级列表
        self.priority_list = QListWidget()
        self.priority_list.itemDoubleClicked.connect(self.edit_priority)
        adofai_priority_layout.addWidget(self.priority_list)
        
        # 优先级操作按钮
        priority_buttons_layout = QHBoxLayout()
        self.add_priority_button = QPushButton("添加优先级")
        self.add_priority_button.clicked.connect(self.add_priority)
        self.remove_priority_button = QPushButton("删除优先级")
        self.remove_priority_button.clicked.connect(self.remove_priority)
        self.edit_priority_button = QPushButton("编辑优先级")
        self.edit_priority_button.clicked.connect(self.edit_priority)
        priority_buttons_layout.addWidget(self.add_priority_button)
        priority_buttons_layout.addWidget(self.remove_priority_button)
        priority_buttons_layout.addWidget(self.edit_priority_button)
        adofai_priority_layout.addLayout(priority_buttons_layout)
        
        main_layout.addLayout(adofai_priority_layout)

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
        
        # 加载优先级设置
        self.priority_list.clear()
        for i, keywords in enumerate(settings.adofai_search_priorities):
            item_text = f"优先级 {i+1}: {', '.join(keywords) if keywords else '(无关键词)'}"
            item = QListWidgetItem(item_text)
            item.setData(1, keywords)  # 存储关键词数据
            self.priority_list.addItem(item)

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
        
        # 收集优先级设置
        priorities = []
        for i in range(self.priority_list.count()):
            item = self.priority_list.item(i)
            keywords = item.data(1)
            priorities.append(keywords)
        
        # 确保最后一个优先级无关键词
        # if priorities and priorities[-1]:
        #     priorities[-1] = []
        #     item = self.priority_list.item(self.priority_list.count() - 1)
        #     item.setText(f"优先级 {self.priority_list.count()}: (无关键词)")
        #     item.setData(1, [])

        self.settings_manager.update_settings(
            parent_dir=parent_dir,
            auto_reload=auto_reload,
            cache_filename=cache_filename,
            adofai_search_priorities=priorities
        )
        self.accept()
    
    def add_priority(self):
        """添加优先级"""
        # 在当前选中项之后添加，默认无关键词
        current_row = self.priority_list.currentRow()
        new_index = current_row + 1 if current_row >= 0 else self.priority_list.count()
        
        # 创建新优先级项
        new_item = QListWidgetItem(f"优先级 {new_index + 1}: (无关键词)")
        new_item.setData(1, [])
        
        # 插入新项
        self.priority_list.insertItem(new_index, new_item)
        
        # 更新所有项的序号
        self.update_priority_numbers()
    
    def remove_priority(self):
        """删除优先级"""
        if self.priority_list.count() <= 1:
            QMessageBox.warning(self, "警告", "至少需要保留一个优先级")
            return
        
        current_row = self.priority_list.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "警告", "请先选择要删除的优先级")
            return
        
        self.priority_list.takeItem(current_row)
        self.update_priority_numbers()
    
    def edit_priority(self):
        """编辑优先级"""
        current_row = self.priority_list.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "警告", "请先选择要编辑的优先级")
            return
        
        # 最后一个优先级不能有关键词
        # if current_row == self.priority_list.count() - 1:
        #     QMessageBox.warning(self, "警告", "最后一个优先级不能设置关键词")
        #     return
        
        current_item = self.priority_list.item(current_row)
        current_keywords = current_item.data(1)
        current_keywords_str = ", ".join(current_keywords)
        
        # 弹出输入对话框
        keywords_str, ok = QInputDialog.getText(
            self, "编辑优先级", "请输入关键词，多个关键词用逗号分隔:", 
            text=current_keywords_str
        )
        
        if ok:
            # 处理输入的关键词
            keywords = [k.strip() for k in keywords_str.split(",") if k.strip()]
            current_item.setData(1, keywords)
            current_item.setText(f"优先级 {current_row + 1}: {', '.join(keywords) if keywords else '(无关键词)'}")
    
    def update_priority_numbers(self):
        """更新优先级序号"""
        for i in range(self.priority_list.count()):
            item = self.priority_list.item(i)
            keywords = item.data(1)
            item.setText(f"优先级 {i + 1}: {', '.join(keywords) if keywords else '(无关键词)'}")
            # 确保最后一个优先级无关键词
            if i == self.priority_list.count() - 1 and keywords:
                item.setData(1, [])
                item.setText(f"优先级 {i + 1}: (无关键词)")
