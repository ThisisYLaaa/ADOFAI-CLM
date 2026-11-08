"""应用启动流程：建 QApplication、主窗口，并套上 Mica 效果与 QTWin11 样式表。

``main.py`` 只负责调用 :func:`run`，所有启动细节都在这里，
方便单独测试（:func:`create_app` 不进入事件循环）以及被其它入口复用。
"""
from __future__ import annotations

import multiprocessing
import sys
from collections.abc import Sequence

import win32mica
from darkdetect import isDark
from PySide6.QtWidgets import QApplication

from src.UI.main_window import MainWindow
from src.UI.settings_manager import get_settings_manager
from src.util.Logger import get_logger
from src.util.paths import resource_path

logger = get_logger("启动")

STYLESHEET_DIR = "QTWin11"


def _apply_mica(window: MainWindow) -> None:
    """给窗口套上 Windows 11 Mica 材质；失败只记日志，不影响启动。"""
    try:
        theme = win32mica.MicaTheme.DARK if isDark() else win32mica.MicaTheme.LIGHT
        win32mica.ApplyMica(window.winId(), theme)  # pyright: ignore[reportArgumentType]
    except Exception as e:  # 非 Win11 / 缺少 dwm 接口时降级为普通窗口
        logger.warning(f"应用Mica效果失败: {e}")


def _apply_stylesheet(app: QApplication) -> None:
    """加载 QTWin11 深浅色样式表；找不到文件时只记日志。"""
    qss_name = "dark.qss" if isDark() else "light.qss"
    qss_path = resource_path(f"{STYLESHEET_DIR}/{qss_name}")
    try:
        app.setStyleSheet(qss_path.read_text(encoding="utf-8"))
    except Exception as e:
        logger.warning(f"加载样式表失败（{qss_path}）: {e}")


def create_app(argv: Sequence[str] | None = None) -> tuple[QApplication, MainWindow]:
    """创建 QApplication 与主窗口，但不进入事件循环。"""
    app = QApplication(list(sys.argv if argv is None else argv))
    window = MainWindow(get_settings_manager())
    _apply_mica(window)
    _apply_stylesheet(app)
    return app, window


def run(argv: Sequence[str] | None = None) -> int:
    """程序主流程，返回进程退出码。"""
    # 支持PyInstaller打包：多进程解析关卡时需要
    multiprocessing.freeze_support()

    app, window = create_app(argv)
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(run())
