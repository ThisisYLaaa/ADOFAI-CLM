import os
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QTableWidget, QTableWidgetItem, QHeaderView
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt
from src.UI.settings_manager import SettingsManager
from src.UI.settings_window import SettingsWindow
from src.func.qtool import tool_quick
from src.func.fma import tool_fma
from src.util import Level

class MainWindow(QMainWindow):
    """主窗口"""
    def __init__(self, settings_manager: SettingsManager):
        super().__init__()
        self.settings_manager = settings_manager
        self.setWindowTitle("关卡管理器")
        self.setMinimumSize(1000, 600)
        self.init_ui()
        if self.settings_manager.settings.auto_reload:
            self.reload_levels()

    def init_ui(self):
        """初始化UI"""
        # 创建菜单栏
        menubar = self.menuBar()
        
        # 设置菜单
        settings_menu = menubar.addMenu("设置")  # pyright: ignore[reportOptionalMemberAccess]
        settings_action = QAction("设置", self)
        settings_action.triggered.connect(self.open_settings)
        settings_menu.addAction(settings_action)  # pyright: ignore[reportOptionalMemberAccess]
        
        # 重载菜单
        reload_menu = menubar.addMenu("重载")  # pyright: ignore[reportOptionalMemberAccess]
        reload_action = QAction("重载关卡", self)
        reload_action.triggered.connect(self.reload_levels)
        reload_menu.addAction(reload_action)  # pyright: ignore[reportOptionalMemberAccess]

        # 主widget
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 创建关卡列表
        self.level_table = QTableWidget()
        self.level_table.setColumnCount(5)
        self.level_table.setHorizontalHeaderLabels(["关卡名称", "艺术家", "作者", "文件名", "文件路径"])
        
        # 设置表头样式
        header = self.level_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)  # pyright: ignore[reportOptionalMemberAccess]
        
        # 设置鼠标滚轮滚动行为
        self.level_table.setVerticalScrollMode(QTableWidget.ScrollMode.ScrollPerPixel)
        
        # 设置表格为只读
        self.level_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        # 连接双击信号
        self.level_table.itemDoubleClicked.connect(self.on_item_double_clicked)
        
        # 连接表头点击信号，实现排序功能
        header = self.level_table.horizontalHeader()
        header.sectionClicked.connect(self.on_header_clicked)
        
        # 存储当前排序状态
        self.current_sort_column = -1
        self.current_sort_order = Qt.SortOrder.AscendingOrder
        
        main_layout.addWidget(self.level_table)

    def open_settings(self):
        """打开设置窗口"""
        settings_window = SettingsWindow(self.settings_manager, self)
        if settings_window.exec():
            # 设置已保存
            pass

    def reload_levels(self):
        """重载关卡"""
        parent_dir = self.settings_manager.settings.parent_dir
        if not parent_dir:
            print("请先设置父文件夹路径")
            return
        
        try:
            levels, unknown_levels = tool_quick.get_elevel_from_parent_dir(parent_dir, console_log=True)
            self.update_level_table(levels, unknown_levels, parent_dir)
        except Exception as e:
            print(f"重载关卡失败: {e}")

    def update_level_table(self, levels: dict[str, tuple[Level, str]], unknown_levels: list[tuple[Level, str]], parent_dir: str):
        """更新关卡列表
        :param levels: 关卡字典，值为(关卡对象, 文件路径)元组
        :param unknown_levels: 未知关卡列表，元素为(关卡对象, 文件路径)元组
        :param parent_dir: 父文件夹路径
        """
        # 清空表格
        self.level_table.setRowCount(0)
        
        # 添加已知关卡
        for song_name, (level, file_path) in levels.items():
            # 获取关卡文件夹路径
            level_dir = os.path.dirname(file_path)
            # 计算相对于父文件夹的路径
            try:
                relative_path = os.path.relpath(level_dir, parent_dir)
            except Exception:
                relative_path = level_dir
            
            row_position = self.level_table.rowCount()
            self.level_table.insertRow(row_position)
            
            # 关卡名称（移除Unity富文本标签）
            clean_song_name = tool_fma.remove_unity_rich_text(song_name)
            self.level_table.setItem(row_position, 0, QTableWidgetItem(clean_song_name))
            # 艺术家（移除Unity富文本标签）
            clean_artist = tool_fma.remove_unity_rich_text(level.settings.artist)
            self.level_table.setItem(row_position, 1, QTableWidgetItem(clean_artist))
            # 作者（移除Unity富文本标签）
            clean_author = tool_fma.remove_unity_rich_text(level.settings.author)
            self.level_table.setItem(row_position, 2, QTableWidgetItem(clean_author))
            # 文件名
            self.level_table.setItem(row_position, 3, QTableWidgetItem(os.path.basename(file_path)))
            # 文件路径
            path_item = QTableWidgetItem(relative_path)
            # 存储完整路径，用于双击打开
            path_item.setData(Qt.ItemDataRole.UserRole, level_dir)
            self.level_table.setItem(row_position, 4, path_item)
        
        # 添加未知关卡
        for level, file_path in unknown_levels:
            # 获取关卡文件夹路径
            level_dir = os.path.dirname(file_path)
            # 计算相对于父文件夹的路径
            try:
                relative_path = os.path.relpath(level_dir, parent_dir)
            except Exception:
                relative_path = level_dir
            
            row_position = self.level_table.rowCount()
            self.level_table.insertRow(row_position)
            
            # 关卡名称
            self.level_table.setItem(row_position, 0, QTableWidgetItem("未知关卡"))
            # 艺术家（移除Unity富文本标签）
            clean_artist = tool_fma.remove_unity_rich_text(level.settings.artist)
            self.level_table.setItem(row_position, 1, QTableWidgetItem(clean_artist))
            # 作者（移除Unity富文本标签）
            clean_author = tool_fma.remove_unity_rich_text(level.settings.author)
            self.level_table.setItem(row_position, 2, QTableWidgetItem(clean_author))
            # 文件名
            self.level_table.setItem(row_position, 3, QTableWidgetItem(os.path.basename(file_path)))
            # 文件路径
            path_item = QTableWidgetItem(relative_path)
            # 存储完整路径，用于双击打开
            path_item.setData(Qt.ItemDataRole.UserRole, level_dir)
            self.level_table.setItem(row_position, 4, path_item)

    def on_item_double_clicked(self, item):
        """处理表格项双击事件
        :param item: 被双击的表格项
        """
        # 只有双击文件路径列时才打开文件夹
        if item.column() == 4:
            # 获取存储的完整路径
            path = item.data(Qt.ItemDataRole.UserRole)
            if path and os.path.exists(path):
                # 打开文件夹
                os.startfile(path)

    def wheelEvent(self, event):  # pyright: ignore[reportIncompatibleMethodOverride]
        """处理鼠标滚轮事件
        :param event: 鼠标滚轮事件
        """
        # 计算滚动距离（一次滚动三行）
        delta = event.angleDelta().y()
        # 每行的高度大约为30像素，三行就是90像素
        scroll_distance = int(delta * 0.3)  # 调整滚动速度
        
        # 使用scrollContentsBy方法滚动表格内容
        self.level_table.scrollContentsBy(0, -scroll_distance)
    
    def on_header_clicked(self, logicalIndex):
        """处理表头点击事件，实现排序功能
        :param logicalIndex: 点击的列索引
        """
        # 如果点击的是当前排序列，则切换排序顺序
        if logicalIndex == self.current_sort_column:
            self.current_sort_order = Qt.SortOrder.DescendingOrder if self.current_sort_order == Qt.SortOrder.AscendingOrder else Qt.SortOrder.AscendingOrder
        else:
            # 否则，设置新的排序列和默认的排序顺序
            self.current_sort_column = logicalIndex
            self.current_sort_order = Qt.SortOrder.AscendingOrder
        
        # 执行排序
        self.level_table.sortItems(logicalIndex, self.current_sort_order)
