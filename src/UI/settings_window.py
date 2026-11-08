from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QCheckBox, QFileDialog, QListWidget, QListWidgetItem, QInputDialog, QMessageBox
from src.UI.settings_manager import SettingsManager

class SettingsWindow(QDialog):
    def __init__(self, settings_manager: SettingsManager, parent=None):
        super().__init__(parent)
        self.settings_manager = settings_manager
        self.setWindowTitle("设置")
        self.setMinimumSize(500, 350)
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        parent_dirs_label = QLabel("父文件夹路径:")
        main_layout.addWidget(parent_dirs_label)

        self.parent_dirs_list = QListWidget()
        main_layout.addWidget(self.parent_dirs_list)

        parent_dirs_buttons = QHBoxLayout()
        self.add_dir_button = QPushButton("添加目录")
        self.add_dir_button.clicked.connect(self.add_parent_dir)
        self.browse_dir_button = QPushButton("浏览并添加")
        self.browse_dir_button.clicked.connect(self.browse_add_parent_dir)
        self.remove_dir_button = QPushButton("删除目录")
        self.remove_dir_button.clicked.connect(self.remove_parent_dir)
        parent_dirs_buttons.addWidget(self.add_dir_button)
        parent_dirs_buttons.addWidget(self.browse_dir_button)
        parent_dirs_buttons.addWidget(self.remove_dir_button)
        main_layout.addLayout(parent_dirs_buttons)

        auto_reload_layout = QHBoxLayout()
        self.auto_reload_checkbox = QCheckBox("程序启动时自动重载")
        auto_reload_layout.addWidget(self.auto_reload_checkbox)
        main_layout.addLayout(auto_reload_layout)

        cache_filename_layout = QHBoxLayout()
        cache_filename_label = QLabel("缓存文件名称:")
        self.cache_filename_edit = QPushButton("cache.json")
        self.cache_filename_edit.setEnabled(False)
        cache_filename_layout.addWidget(cache_filename_label)
        cache_filename_layout.addWidget(self.cache_filename_edit)
        main_layout.addLayout(cache_filename_layout)

        adofai_priority_layout = QVBoxLayout()
        adofai_priority_label = QLabel(".adofai文件搜索优先级:")
        adofai_priority_layout.addWidget(adofai_priority_label)

        self.priority_list = QListWidget()
        self.priority_list.itemDoubleClicked.connect(self.edit_priority)
        adofai_priority_layout.addWidget(self.priority_list)

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
        settings = self.settings_manager.settings
        self.parent_dirs_list.clear()
        for d in settings.parent_dirs:
            item = QListWidgetItem(d)
            self.parent_dirs_list.addItem(item)
        self.auto_reload_checkbox.setChecked(settings.auto_reload)

        self.priority_list.clear()
        for i, keywords in enumerate(settings.adofai_search_priorities):
            item_text = f"优先级 {i+1}: {', '.join(keywords) if keywords else '(无关键词)'}"
            item = QListWidgetItem(item_text)
            item.setData(1, keywords)
            self.priority_list.addItem(item)

    def add_parent_dir(self):
        dir_path, ok = QInputDialog.getText(self, "添加目录", "请输入父文件夹路径:")
        if ok and dir_path.strip():
            self.parent_dirs_list.addItem(dir_path.strip())

    def browse_add_parent_dir(self):
        dir_path = QFileDialog.getExistingDirectory(
            self, "选择父文件夹", ".",
            QFileDialog.Option.ShowDirsOnly | QFileDialog.Option.DontResolveSymlinks
        )
        if dir_path:
            self.parent_dirs_list.addItem(dir_path)

    def remove_parent_dir(self):
        current_row = self.parent_dirs_list.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "警告", "请先选择要删除的目录")
            return
        self.parent_dirs_list.takeItem(current_row)

    def save_settings(self):
        parent_dirs = []
        for i in range(self.parent_dirs_list.count()):
            item = self.parent_dirs_list.item(i)
            parent_dirs.append(item.text())

        auto_reload = self.auto_reload_checkbox.isChecked()
        cache_filename = self.cache_filename_edit.text()

        priorities = []
        for i in range(self.priority_list.count()):
            item = self.priority_list.item(i)
            keywords = item.data(1)
            priorities.append(keywords)

        self.settings_manager.update_settings(
            parent_dirs=parent_dirs,
            auto_reload=auto_reload,
            cache_filename=cache_filename,
            adofai_search_priorities=priorities
        )
        self.accept()

    def add_priority(self):
        current_row = self.priority_list.currentRow()
        new_index = current_row + 1 if current_row >= 0 else self.priority_list.count()
        new_item = QListWidgetItem(f"优先级 {new_index + 1}: (无关键词)")
        new_item.setData(1, [])
        self.priority_list.insertItem(new_index, new_item)
        self.update_priority_numbers()

    def remove_priority(self):
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
        current_row = self.priority_list.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "警告", "请先选择要编辑的优先级")
            return
        current_item = self.priority_list.item(current_row)
        current_keywords = current_item.data(1)
        current_keywords_str = ", ".join(current_keywords)
        keywords_str, ok = QInputDialog.getText(
            self, "编辑优先级", "请输入关键词，多个关键词用逗号分隔:",
            text=current_keywords_str
        )
        if ok:
            keywords = [k.strip() for k in keywords_str.split(",") if k.strip()]
            current_item.setData(1, keywords)
            current_item.setText(f"优先级 {current_row + 1}: {', '.join(keywords) if keywords else '(无关键词)'}")

    def update_priority_numbers(self):
        for i in range(self.priority_list.count()):
            item = self.priority_list.item(i)
            keywords = item.data(1)
            item.setText(f"优先级 {i + 1}: {', '.join(keywords) if keywords else '(无关键词)'}")
            if i == self.priority_list.count() - 1 and keywords:
                item.setData(1, [])
                item.setText(f"优先级 {i + 1}: (无关键词)")
