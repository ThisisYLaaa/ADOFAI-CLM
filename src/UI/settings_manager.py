import os
import yaml
from dataclasses import dataclass, field

@dataclass
class AppSettings:
    parent_dirs: list[str] = field(default_factory=list)
    auto_reload: bool = False
    cache_filename: str = "cache.json"
    max_parse_level_threading: int = 5
    adofai_search_priorities: list[list[str]] = field(default_factory=lambda: [["vfx"], ["level", "main"], ["backup"]])


class SettingsManager:
    def __init__(self, settings_file: str = "config.yaml"):
        self.settings_file = settings_file
        self.settings = self.load_settings()

    def load_settings(self) -> AppSettings:
        if not os.path.exists(self.settings_file):
            old_file = "settings.yaml"
            if os.path.exists(old_file):
                try:
                    with open(old_file, 'r', encoding='utf-8') as f:
                        data = yaml.safe_load(f)
                        if data:
                            self._migrate_old_data(data)
                            settings = AppSettings(**data)
                            self._migrate_and_cleanup(old_file)
                            return settings
                except Exception:
                    pass
            return AppSettings()

        try:
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                if data:
                    self._migrate_old_data(data)
                    return AppSettings(**data)
        except Exception as e:
            print(f"加载设置失败: {e}")
        return AppSettings()

    def _migrate_old_data(self, data: dict):
        if 'parent_dir' in data and 'parent_dirs' not in data:
            if data['parent_dir']:
                data['parent_dirs'] = [data['parent_dir']]
            del data['parent_dir']

    def _migrate_and_cleanup(self, old_file: str):
        self.save_settings()
        try:
            os.remove(old_file)
        except Exception:
            pass

    def save_settings(self) -> bool:
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                yaml.dump(
                    {
                        'parent_dirs': self.settings.parent_dirs,
                        'auto_reload': self.settings.auto_reload,
                        'cache_filename': self.settings.cache_filename,
                        'max_parse_level_threading': self.settings.max_parse_level_threading,
                        'adofai_search_priorities': self.settings.adofai_search_priorities,
                    },
                    f,
                    default_flow_style=False,
                    allow_unicode=True,
                    sort_keys=False,
                )
            return True
        except Exception as e:
            print(f"保存设置失败: {e}")
            return False

    def update_settings(self, parent_dirs: list[str]|None = None, auto_reload: bool|None = None,
                        cache_filename: str|None = None,
                        max_parse_level_threading: int|None = None,
                        adofai_search_priorities: list[list[str]]|None = None):
        if parent_dirs is not None:
            self.settings.parent_dirs = parent_dirs
        if auto_reload is not None:
            self.settings.auto_reload = auto_reload
        if cache_filename is not None:
            self.settings.cache_filename = cache_filename
        if max_parse_level_threading is not None:
            self.settings.max_parse_level_threading = max_parse_level_threading
        if adofai_search_priorities is not None:
            self.settings.adofai_search_priorities = adofai_search_priorities
        self.save_settings()
