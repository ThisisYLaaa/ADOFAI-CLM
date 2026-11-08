"""GUI 层：主窗口、设置窗口与设置管理。

窗口类用 PEP 562 的模块级 ``__getattr__`` 按需导入：关卡解析跑在
``ProcessPoolExecutor`` 的子进程里，子进程只会用到设置管理器，
不该为了一个配置项把整个 Qt 拉进子进程。
"""
from __future__ import annotations

from importlib import import_module

_LAZY_EXPORTS: dict[str, tuple[str, str]] = {
    "MainWindow": ("src.UI.main_window", "MainWindow"),
    "SettingsWindow": ("src.UI.settings_window", "SettingsWindow"),
    "SettingsManager": ("src.UI.settings_manager", "SettingsManager"),
    "AppSettings": ("src.UI.settings_manager", "AppSettings"),
    "get_settings_manager": ("src.UI.settings_manager", "get_settings_manager"),
}

__all__ = sorted(_LAZY_EXPORTS)


def __getattr__(name: str):
    try:
        module_name, attribute = _LAZY_EXPORTS[name]
    except KeyError as exc:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}") from exc
    value = getattr(import_module(module_name), attribute)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted(__all__)
