import sys
import os
from PySide6.QtWidgets import QApplication
from darkdetect import isDark
import win32mica
from src.UI.settings_manager import SettingsManager
from src.UI.main_window import MainWindow

if __name__ == "__main__":
    # 创建Qt应用程序
    app = QApplication(sys.argv)
    
    # 初始化设置管理器
    settings_manager = SettingsManager()
    
    # 创建主窗口
    main_window = MainWindow(settings_manager)
    
    # 应用Mica效果
    try:
        win32mica.ApplyMica(main_window.winId(), win32mica.MicaTheme.DARK if isDark() else win32mica.MicaTheme.LIGHT)  # pyright: ignore[reportArgumentType]
    except Exception as e:
        print(f"应用Mica效果失败: {e}")
    
    # 加载QTWin11样式表
    try:
        qss_path = os.path.join("QTWin11", "dark.qss" if isDark() else "light.qss")
        with open(qss_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    except Exception as e:
        print(f"加载样式表失败: {e}")
    
    main_window.show()
    
    # 运行应用程序
    sys.exit(app.exec())
