"""关卡目录里的文件定位：音乐文件、.adofai 文件与关卡目录枚举。"""
from __future__ import annotations

import os
from collections.abc import Sequence

from src.func.interact import tool_interact
from src.UI.settings_manager import get_settings_manager
from src.util.Logger import get_logger

logger = get_logger("文件工具")

MUSIC_SUFFIXES: tuple[str, ...] = (".wav", ".ogg")
LEVEL_SUFFIX: str = ".adofai"


def _list_music_files(level_dir: str) -> list[str]:
    """目录下所有音乐文件（.wav/.ogg）的完整路径。"""
    return [
        os.path.join(level_dir, name)
        for name in os.listdir(level_dir)
        if name.endswith(MUSIC_SUFFIXES)
    ]


def _level_files(level_dir: str) -> list[str]:
    """目录下所有 .adofai 文件的完整路径。"""
    try:
        names = os.listdir(level_dir)
    except OSError as e:  # 无权限或目录已被删除时不让整次扫描崩掉
        logger.warning(f"无法读取目录 {level_dir}: {e}")
        return []
    return [os.path.join(level_dir, name) for name in names if name.endswith(LEVEL_SUFFIX)]


def _group_level_files(level_dir: str, priorities: Sequence[Sequence[str]]) -> list[list[str]]:
    """按 adofai_search_priorities 把同目录下的 .adofai 分组。

    命中最靠前的关键词组就进该组；一个关键词都没命中的文件放进最后一组
    （末组通常配成空关键词做兜底）。组序即优先级，找文件时从头取第一个非空组。
    """
    groups: list[list[str]] = [[] for _ in priorities]
    files = _level_files(level_dir)
    if not groups:
        return [files]

    for file_path in files:
        file_name = os.path.basename(file_path)
        index = next(
            (
                i
                for i, keywords in enumerate(priorities)
                if keywords and any(keyword in file_name for keyword in keywords)
            ),
            len(groups) - 1,
        )
        groups[index].append(file_path)
    return groups


class tool_file:
    """关卡目录文件工具，保持原有的静态方法接口。"""

    @staticmethod
    def get_music_filepath_from_leveldir_auto(level_dir: str, console_log: bool = True) -> str:
        """从关卡目录获取音乐文件路径，没有则返回空串。"""
        music_files = _list_music_files(level_dir)
        if music_files:
            return music_files[0]
        if console_log:
            logger.error(f"未找到音乐文件: {level_dir}")
        return ""

    @staticmethod
    def get_adofai_filepath_from_leveldir_auto(level_dir: str, console_log: bool = True) -> str:
        """按搜索优先级从关卡目录获取 .adofai 文件路径，没有则返回空串。"""
        priorities = get_settings_manager().settings.adofai_search_priorities
        for group in _group_level_files(level_dir, priorities):
            if group:
                return group[0]
        if console_log:
            logger.error(f"未找到adofai文件: {level_dir}")
        return ""

    @staticmethod
    def get_music_filepath_from_leveldir(level_dir: str, console_log: bool = True) -> str:
        """交互式获取音乐文件路径：目录里不止一个时让用户选。"""
        music_files = _list_music_files(level_dir)
        if len(music_files) == 1:
            return music_files[0]
        if music_files:
            index = tool_interact.list_ask_index("请选择音乐文件", music_files)
            return music_files[index]
        if console_log:
            logger.error(f"未找到音乐文件: {level_dir}")
        return ""

    @staticmethod
    def get_adofai_filepath_from_leveldir(level_dir: str, console_log: bool = True) -> str:
        """交互式获取 .adofai 文件路径：同一优先级里不止一个时让用户选。"""
        priorities = get_settings_manager().settings.adofai_search_priorities
        for group in _group_level_files(level_dir, priorities):
            if len(group) == 1:
                return group[0]
            if group:
                index = tool_interact.list_ask_index("请选择adofai文件", group)
                return group[index]
        if console_log:
            logger.error(f"未找到adofai文件: {level_dir}")
        return ""

    @staticmethod
    def get_leveldirs_from_parent_dir_auto(parent_dir: str, console_log: bool = True) -> list[str]:
        """递归找出所有直接包含 .adofai 的子目录。"""
        level_dirs: list[str] = []
        for root, dirs, _files in os.walk(parent_dir):
            for dir_name in dirs:
                sub_dir = os.path.join(root, dir_name)
                if _level_files(sub_dir):
                    level_dirs.append(sub_dir)

        if not level_dirs:
            if console_log:
                logger.error(f"未找到adofai文件: {parent_dir}")
            return []
        return level_dirs
