# 关卡管理器（ADOFAI Level Manager）

基于 PySide6 的 **ADOFAI（A Dance of Fire and Ice）关卡管理器**：把散落在各个父目录里的 `.adofai` 关卡扫进一张表，
直接看标题 / 艺术家 / 作者 / 文件名 / 相对路径，双击打开关卡文件夹，一键导出歌单。
在 Windows 11 上跟随系统深浅色套用 Mica 材质与 QTWin11 样式表，非 Win11 或系统关闭透明效果时自动降级为普通窗口。

## 功能

- **多父目录扫描**：递归找出所有直接包含 `.adofai` 的子目录，多个父目录的结果合并展示
- **表格列表**：标题 / 艺术家 / 作者 / 文件名 / 相对路径（标题里的 `<color=#fff>` 之类 Unity 富文本标签会被自动清掉）
- **点击表头排序**：第一次升序，再点同一列切降序，换列后按新列升序
- **双击打开文件夹**：双击「文件路径」列，用资源管理器打开该关卡所在目录
- **.adofai 搜索优先级**：同一关卡目录里有多个 `.adofai` 时按配置挑一个（见「配置说明」）
- **歌单导出**：「生成歌单」按标题排序导出 `歌单.txt`；「生成歌单图片」再导出透明底 `歌单.png`（需要 Pillow）
- **设置窗口**：管理父目录列表、启动时自动重载、`.adofai` 搜索优先级
- **日志**：统一走 `src/util/Logger.py`，带图标与颜色，便于排查解析失败

## 项目结构

```
ADOFAI-CLM/
├── main.py                  # 入口，只负责调用 src.app.run()
├── requirements.txt         # 第三方依赖
├── LICENSE.txt              # MIT
├── QTWin11/                 # Windows 11 风格样式表
│   ├── dark.qss
│   └── light.qss
└── src/
    ├── app.py               # 启动流程：QApplication → 主窗口 → Mica → qss
    ├── UI/                  # GUI 层
    │   ├── main_window.py       # 主窗口：表格、排序、双击打开、歌单导出
    │   ├── settings_window.py   # 设置窗口
    │   └── settings_manager.py  # 设置读写与旧配置迁移（config.yaml）
    ├── func/                # 功能层
    │   ├── file.py              # 关卡目录枚举、音乐文件与 .adofai 定位
    │   ├── qtool.py             # 多进程批量解析关卡
    │   ├── fma.py               # Unity 富文本清洗
    │   └── interact.py          # 命令行交互提示（交互式选文件用）
    └── util/                # 工具层
        ├── Logger.py            # 带图标/颜色的日志
        ├── Parser.py            # 容错读取 .adofai JSON（缺括号、多余逗号等）
        ├── Struction.py         # 关卡数据结构（Level / Settings / Action）
        └── paths.py             # 源码运行与打包运行（PyInstaller）的路径解析
```

包内统一使用 `from src.x import y` 绝对导入。`python main.py` 会把仓库根放进 `sys.path`，
配置与样式表都按「程序目录」定位，所以从任意工作目录启动都能正常读写。

## 安装与运行

### 环境

- Windows 10 / 11
- Python **3.10+**（代码使用了 `X | None` 类型写法；开发环境验证于 3.12）
- 依赖见 `requirements.txt`

### 步骤

```bash
git clone https://github.com/ThisisYLaaa/ADOFAI-CLM.git
cd ADOFAI-CLM
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

首次运行没有 `config.yaml` 也照常启动（用内置默认值），在设置窗口添加父目录并保存后就会生成。

### 快速上手

1. 菜单「设置」→「设置」
2. 点「浏览并添加」选一个**装着关卡文件夹**的父目录（可以添加多个）
3. 需要的话勾选「程序启动时自动重载」
4. 「保存」→ 菜单「重载」→「重载关卡」

## 配置说明

配置**唯一来源**是程序目录下的 `config.yaml`（源码运行时是仓库根目录；PyInstaller 打包后是 exe 所在目录）。
仓库不包含这个文件——它属于本地运行时数据，已被 `.gitignore` 忽略，首次保存设置时自动生成。

### 读取优先级

1. `config.yaml` —— 存在就以它为准，缺的字段用下表默认值补齐
2. 旧版 `settings.yaml` —— 仅当 `config.yaml` 不存在时读取，读到就写出一份 `config.yaml` 并删除旧文件；
   旧的单目录字段 `parent_dir` 会自动转成 `parent_dirs`
3. 代码内 `AppSettings` 默认值（下表「默认」列）

仓库根目录不再有 `settings.py` 这类常量文件：早期版本里那个只有一行 `max_parse_level_threading` 的模块已删除，
同名配置项一律以 `config.yaml` 为准，避免出现「改了一处不生效」的双份来源。

### config.yaml 字段

| 字段 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `parent_dirs` | 字符串列表 | `[]` | 要扫描的父目录，可多个。扫描是递归的，凡是直接包含 `.adofai` 的子目录都算一个关卡目录 |
| `auto_reload` | 布尔 | `false` | 启动时是否立刻扫描一次 |
| `cache_filename` | 字符串 | `cache.json` | 预留的扫描结果缓存文件名（当前版本不落盘，保留配置项以兼容旧配置） |
| `max_parse_level_threading` | 整数 | `5` | 解析关卡时的进程数（`ProcessPoolExecutor(max_workers=…)`） |
| `adofai_search_priorities` | 字符串列表的列表 | `[["vfx"], ["level","main"], ["backup"]]` | 同一关卡目录里有多个 `.adofai` 时的挑选顺序，规则见下 |

`adofai_search_priorities` 规则：

- 按**组序**检查，文件名（不含目录）命中该组任意关键词就归入该组；
- 一组都没命中的文件归入**最后一组**，所以最后一组通常留空关键词当兜底；
- 取文件时从第一组开始，第一个非空组的第一个文件胜出。

示例：

```yaml
parent_dirs:
- C:/Games/AdofaiLevels
auto_reload: false
cache_filename: cache.json
max_parse_level_threading: 5
adofai_search_priorities:
- - vfx
- - level
  - main
- - backup
- []
```

含义：`xxx.vfx.adofai` 优先于 `xxx.level.adofai` / `xxx.main.adofai`，再优先于 `xxx.backup.adofai`，
其余文件由最后的空组兜底。

### 另一个文件：settings.json

早期开发目录里还出现过 `settings.json`（`folderA` / `theme` / `autoload` 三个字段）与扫描结果缓存 `levels.json`。
当前版本**没有任何代码读取它们**，属于历史遗留的运行时数据，仅保留在本机并被 `.gitignore` 忽略；
真正生效的配置只有 `config.yaml`。

## 打包（PyInstaller）

扫描关卡用的是多进程 `ProcessPoolExecutor`，Windows 下子进程会以 spawn 方式**重新导入入口脚本**，
所以打包时有两个硬性要求，本仓库都已满足：

1. `multiprocessing.freeze_support()` 必须在入口尽早调用 —— 位于 `src/app.py` 的 `run()`；
2. 入口必须被 `if __name__ == "__main__":` 保护（`main.py` 已如此），否则子进程会再次拉起整个 GUI。

示例（onedir）：

```bash
pip install pyinstaller
pyinstaller --noconfirm --windowed --name ADOFAI-CLM ^
  --add-data "QTWin11;QTWin11" ^
  --hidden-import win32mica main.py
```

- `--add-data "QTWin11;QTWin11"`：qss 不是 Python 包数据，必须显式带上。onefile 时从 `_MEIPASS` 读，
  onedir 时从 exe 同级目录读，`src/util/paths.py` 已同时处理这两种布局
- `--windowed` 去掉控制台窗口；排查启动问题时先去掉它，日志才能看见
- 产物 `build/`、`dist/`、`*.spec` 已被 `.gitignore` 忽略
- 想要更小的体积，可用 `--exclude-module` 剔除用不到的 Qt 模块

## 常见问题

**表格是空的，日志提示「请先设置父文件夹路径」**
菜单「设置」→「设置」里添加父目录并保存，再「重载」→「重载关卡」。父目录应选**装着关卡文件夹的目录**，程序会递归往下找。

**某个关卡显示为「未知关卡」或标题为空**
`.adofai` 里 `settings.song` 为空时会退化成「同目录音乐文件名 → 关卡文件名」；解析失败会在日志里打 `解析关卡失败: <路径>`。

**一个关卡目录里有好几个 `.adofai`，挑错了**
调整 `config.yaml` 的 `adofai_search_priorities`，或在设置窗口里编辑「.adofai文件搜索优先级」。

**没有 Mica 效果 / 样式不对**
非 Windows 11 或系统关闭了透明效果时会降级成普通窗口，日志里出现「应用Mica效果失败」，不影响功能；
qss 缺失时同理只记一条「加载样式表失败」。打包后出现该提示，多半是忘了 `--add-data QTWin11`。

**「生成歌单图片」提示缺少 Pillow**
`pip install Pillow`（已在 `requirements.txt` 里）。歌单文件输出到程序目录。

**控制台日志中文乱码**
日志走终端输出，Windows 控制台代码页不是 UTF-8 时会乱码；`chcp 65001` 或改用 Windows Terminal 即可，图形界面不受影响。

## 开发说明

- 包内一律 `from src.x import y` 绝对导入；`src/UI/__init__.py` 用惰性导出，避免把 Qt 带进关卡解析子进程
- 配置只经由 `src/UI/settings_manager.py` 读写，不要在别处硬编码配置常量（`get_settings_manager()` 返回进程内共享实例）
- 关卡数据结构在 `src/util/Struction.py`，容错解析在 `src/util/Parser.py`

## 许可

本项目使用 MIT 许可证，详见 [LICENSE.txt](LICENSE.txt)。Copyright (c) 2026 This_is_YL

## 联系方式

- Bilibili：[https://space.bilibili.com/616045770](https://space.bilibili.com/616045770)
- QQ群：132292540
