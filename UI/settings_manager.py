import os
import yaml
from dataclasses import dataclass, field

@dataclass
class AppSettings:
    """应用设置类"""
    parent_dir: str = ""
    auto_reload: bool = False
    cache_filename: str = "cache.json"

class SettingsManager:
    """设置管理器"""
    def __init__(self, settings_file: str = "settings.yaml"):
        self.settings_file = settings_file
        self.settings = self.load_settings()

    def load_settings(self) -> AppSettings:
        """加载设置
        :return: AppSettings实例
        """
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    if data:
                        return AppSettings(**data)
            except Exception as e:
                print(f"加载设置失败: {e}")
        return AppSettings()

    def save_settings(self) -> bool:
        """保存设置
        :return: 是否保存成功
        """
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                yaml.dump(
                    {
                        'parent_dir': self.settings.parent_dir,
                        'auto_reload': self.settings.auto_reload,
                        'cache_filename': self.settings.cache_filename
                    },
                    f,
                    default_flow_style=False,
                    allow_unicode=True
                )
            return True
        except Exception as e:
            print(f"保存设置失败: {e}")
            return False

    def update_settings(self, parent_dir: str = None, auto_reload: bool = None, cache_filename: str = None):  # pyright: ignore[reportArgumentType]
        """更新设置
        :param parent_dir: 父文件夹路径
        :param auto_reload: 是否自动重载
        :param cache_filename: 缓存文件名
        """
        if parent_dir is not None:
            self.settings.parent_dir = parent_dir
        if auto_reload is not None:
            self.settings.auto_reload = auto_reload
        if cache_filename is not None:
            self.settings.cache_filename = cache_filename
        self.save_settings()
