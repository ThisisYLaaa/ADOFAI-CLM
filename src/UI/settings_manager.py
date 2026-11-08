"""应用设置的读取、迁移与持久化。

配置唯一来源是程序目录下的 ``config.yaml``（位置见 :func:`src.util.paths.app_dir`）。
读取优先级：``config.yaml`` > 旧版 ``settings.yaml``（读到即迁移成 config.yaml 并删除）
> :class:`AppSettings` 里的代码默认值。
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field, fields
from pathlib import Path
from typing import Any

import yaml

from src.util.Logger import get_logger
from src.util.paths import app_dir

logger = get_logger("设置")

CONFIG_FILENAME = "config.yaml"
LEGACY_CONFIG_FILENAME = "settings.yaml"


@dataclass
class AppSettings:
    """程序设置，字段名与 config.yaml 的键一一对应。"""

    parent_dirs: list[str] = field(default_factory=list)
    auto_reload: bool = False
    cache_filename: str = "cache.json"
    max_parse_level_threading: int = 5
    adofai_search_priorities: list[list[str]] = field(
        default_factory=lambda: [["vfx"], ["level", "main"], ["backup"]]
    )


class SettingsManager:
    """负责 config.yaml 的读写；不传路径时使用程序目录下的 config.yaml。"""

    def __init__(self, settings_file: str | os.PathLike[str] | None = None):
        self.settings_file = Path(settings_file) if settings_file else app_dir() / CONFIG_FILENAME
        self.settings = self.load_settings()

    def load_settings(self) -> AppSettings:
        """读取配置；config.yaml 不存在时尝试迁移旧版 settings.yaml。"""
        if not self.settings_file.exists():
            return self._migrate_legacy_file() or AppSettings()

        try:
            with open(self.settings_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
        except Exception as e:
            logger.error(f"加载设置失败: {e}")
            return AppSettings()

        return self._build_settings(data)

    def _migrate_legacy_file(self) -> AppSettings | None:
        """把同目录下的旧 settings.yaml 迁移成 config.yaml，成功后删除旧文件。"""
        legacy_file = self.settings_file.parent / LEGACY_CONFIG_FILENAME
        if not legacy_file.exists():
            return None
        try:
            with open(legacy_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
        except Exception as e:
            logger.warning(f"读取旧配置 {legacy_file.name} 失败: {e}")
            return None

        settings = self._build_settings(data)
        self.settings = settings
        if not self.save_settings():
            return settings
        try:
            legacy_file.unlink()
            logger.info(f"已将 {legacy_file.name} 迁移为 {self.settings_file.name}")
        except OSError as e:
            logger.warning(f"旧配置 {legacy_file.name} 删除失败: {e}")
        return settings

    @staticmethod
    def _build_settings(data: dict[str, Any]) -> AppSettings:
        """按字段白名单构造 AppSettings，并把旧版 parent_dir 兼容成 parent_dirs。"""
        data = dict(data)
        if "parent_dir" in data and "parent_dirs" not in data:
            old_value = data.pop("parent_dir")
            data["parent_dirs"] = [old_value] if old_value else []
        else:
            data.pop("parent_dir", None)

        known_fields = {f.name for f in fields(AppSettings)}
        unknown_fields = sorted(set(data) - known_fields)
        if unknown_fields:
            logger.warning(f"config.yaml 中有未识别的配置项，已忽略: {', '.join(unknown_fields)}")
        return AppSettings(**{k: v for k, v in data.items() if k in known_fields})

    def save_settings(self) -> bool:
        """把当前设置写回 config.yaml，返回是否成功。"""
        payload = {
            "parent_dirs": self.settings.parent_dirs,
            "auto_reload": self.settings.auto_reload,
            "cache_filename": self.settings.cache_filename,
            "max_parse_level_threading": self.settings.max_parse_level_threading,
            "adofai_search_priorities": self.settings.adofai_search_priorities,
        }
        try:
            with open(self.settings_file, "w", encoding="utf-8") as f:
                yaml.dump(
                    payload,
                    f,
                    default_flow_style=False,
                    allow_unicode=True,
                    sort_keys=False,
                )
            return True
        except Exception as e:
            logger.error(f"保存设置失败: {e}")
            return False

    def update_settings(
        self,
        parent_dirs: list[str] | None = None,
        auto_reload: bool | None = None,
        cache_filename: str | None = None,
        max_parse_level_threading: int | None = None,
        adofai_search_priorities: list[list[str]] | None = None,
    ) -> bool:
        """就地更新若干字段并落盘；传 None 表示该项保持不变。"""
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
        return self.save_settings()


_default_manager: SettingsManager | None = None


def get_settings_manager() -> SettingsManager:
    """返回进程内共享的设置管理器（首次调用时读取 config.yaml）。"""
    global _default_manager
    if _default_manager is None:
        _default_manager = SettingsManager()
    return _default_manager


def reset_settings_manager() -> None:
    """丢弃共享实例，下次 :func:`get_settings_manager` 重新读取配置（测试用）。"""
    global _default_manager
    _default_manager = None
