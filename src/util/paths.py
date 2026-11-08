"""运行期路径解析。

源码运行与 PyInstaller 冻结后的目录布局不同，差异集中在这里判断：

- :func:`app_dir`：可写目录，``config.yaml`` 等用户数据放这里；
- :func:`resource_path`：只读资源（``QTWin11/*.qss``）的定位。

这样程序不再依赖「从仓库根目录执行」这一隐含约定。
"""
from __future__ import annotations

import sys
from pathlib import Path


def is_frozen() -> bool:
    """是否运行在 PyInstaller 等冻结环境中。"""
    return bool(getattr(sys, "frozen", False))


def app_dir() -> Path:
    """程序目录：源码运行时是仓库根目录，冻结后是可执行文件所在目录。"""
    if is_frozen():
        return Path(sys.executable).resolve().parent
    # <repo>/src/util/paths.py -> <repo>
    return Path(__file__).resolve().parents[2]


def resource_path(relative: str | Path) -> Path:
    """只读资源路径：onefile 打包时从临时解包目录取，否则从程序目录取。"""
    bundle_dir = getattr(sys, "_MEIPASS", None)
    base = Path(bundle_dir) if bundle_dir else app_dir()
    return base / relative
