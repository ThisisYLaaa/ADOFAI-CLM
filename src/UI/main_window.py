import os
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt
from src.util.Logger import get_logger
from src.UI.settings_manager import SettingsManager
from src.UI.settings_window import SettingsWindow
from src.func.qtool import tool_quick
from src.func.fma import tool_fma
from src.util import Level

logger = get_logger("主窗口")

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

        # 按钮栏
        button_layout = QHBoxLayout()
        self.export_button = QPushButton("生成歌单")
        self.export_button.clicked.connect(self.export_playlist)
        self.export_image_button = QPushButton("生成歌单图片")
        self.export_image_button.clicked.connect(self.export_playlist_image)
        button_layout.addWidget(self.export_button)
        button_layout.addWidget(self.export_image_button)
        button_layout.addStretch()
        main_layout.addLayout(button_layout)

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
        parent_dirs = self.settings_manager.settings.parent_dirs
        if not parent_dirs:
            logger.warning("请先设置父文件夹路径")
            return

        all_levels: dict[str, tuple[Level, str]] = {}
        all_unknown: list[tuple[Level, str]] = []
        for parent_dir in parent_dirs:
            try:
                levels, unknown_levels = tool_quick.get_elevel_from_parent_dir(parent_dir, console_log=True)
                all_levels.update(levels)
                all_unknown.extend(unknown_levels)
            except Exception as e:
                logger.error(f"加载目录 {parent_dir} 失败: {e}")

        self.update_level_table(all_levels, all_unknown, parent_dirs)

    def update_level_table(self, levels: dict[str, tuple[Level, str]], unknown_levels: list[tuple[Level, str]], parent_dirs: list[str]):
        """更新关卡列表
        :param levels: 关卡字典，值为(关卡对象, 文件路径)元组
        :param unknown_levels: 未知关卡列表，元素为(关卡对象, 文件路径)元组
        :param parent_dirs: 父文件夹路径列表
        """
        self._levels_data = levels
        self._unknown_levels_data = unknown_levels
        self._parent_dirs = parent_dirs

        # 清空表格
        self.level_table.setRowCount(0)
        
        # 添加已知关卡
        for song_name, (level, file_path) in levels.items():
            level_dir = os.path.dirname(file_path)
            relative_path = self._get_relative_path(level_dir, parent_dirs)
            
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
            level_dir = os.path.dirname(file_path)
            relative_path = self._get_relative_path(level_dir, parent_dirs)
            
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

    def _get_relative_path(self, level_dir: str, parent_dirs: list[str]) -> str:
        for parent_dir in parent_dirs:
            try:
                return os.path.relpath(level_dir, parent_dir)
            except Exception:
                continue
        return level_dir

    def _get_sorted_song_names(self) -> list[str] | None:
        if not hasattr(self, '_levels_data') or not self._levels_data:
            logger.warning("请先加载关卡数据")
            return None

        song_names = []
        for song_name in self._levels_data:
            clean_name = tool_fma.remove_unity_rich_text(song_name)
            if clean_name:
                song_names.append(clean_name)

        song_names.sort(key=lambda s: s.upper())
        return song_names

    def export_playlist(self):
        """生成歌单：将当前加载的关卡名称保存到txt文件"""
        song_names = self._get_sorted_song_names()
        if song_names is None:
            return

        file_path = os.path.join(os.getcwd(), "歌单.txt")
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("\n".join(song_names))
            logger.info(f"歌单已生成: {file_path} (共 {len(song_names)} 首)")
        except Exception as e:
            logger.error(f"生成歌单失败: {e}")

    def export_playlist_image(self):
        """生成歌单图片：将当前加载的关卡名称保存为透明底PNG图片"""
        song_names = self._get_sorted_song_names()
        if song_names is None:
            return

        try:
            from PIL import Image, ImageDraw, ImageFont
        except ImportError:
            logger.error("生成图片需要 Pillow 库，请安装: pip install Pillow")
            return

        try:
            margin = 40
            font_size = 28

            font = None
            for font_name in ["msyh.ttc", "Microsoft YaHei UI", "simhei.ttf", "arial.ttf"]:
                try:
                    font = ImageFont.truetype(font_name, font_size)
                    break
                except Exception:
                    continue
            if font is None:
                font = ImageFont.load_default()

            line_spacing = font_size + 8
            img_width = 800
            img_height = margin * 2 + len(song_names) * line_spacing
            img = Image.new("RGBA", (img_width, img_height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)

            y = margin
            for name in song_names:
                draw.text((margin + 2, y + 2), name, fill=(0, 0, 0, 80), font=font)
                draw.text((margin, y), name, fill=(255, 255, 255, 255), font=font)
                y += line_spacing

            file_path = os.path.join(os.getcwd(), "歌单.png")
            img.save(file_path, "PNG")
            logger.info(f"歌单图片已生成: {file_path} (共 {len(song_names)} 首)")
        except Exception as e:
            logger.error(f"生成歌单图片失败: {e}")

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
