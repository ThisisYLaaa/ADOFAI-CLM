# quick tool
import os
from concurrent.futures import ProcessPoolExecutor, as_completed

import settings
from src.util.Logger import get_logger
logger = get_logger("快速工具")
from src.func import tool_file
from src.func import tool_fma
from src.util import Level
from src.util import get_level_json

class tool_quick:
    @staticmethod
    def _parse_level(adofai_filepath: str, console_log: bool = True) -> tuple[str, Level, str]:
        """解析adofai文件, 获取歌曲名和关卡对象
        :param adofai_filepath: adofai文件路径
        :return: 歌曲名、关卡对象和文件路径
        """
        adofai_json: dict = get_level_json(adofai_filepath)
        level: Level = Level(adofai_json)
        song_name: str = level.settings.song
        if level.settings.song == "":
            # 尝试获取同文件下的音乐文件名
            song_name = tool_file.get_music_filepath_from_leveldir_auto(os.path.dirname(adofai_filepath), console_log=False)
            song_name = os.path.splitext(os.path.basename(song_name))[0]
            if song_name == "": song_name = os.path.splitext(os.path.basename(adofai_filepath))[0]
            if song_name == "" and console_log: logger.warning(f"未找到标题: {adofai_filepath}")
        return song_name, level, adofai_filepath

    @staticmethod
    def get_elevel_from_parent_dir(parent_dir: str, console_log: bool = True) -> tuple[dict[str, tuple[Level, str]], list[tuple[Level, str]]]:
        """从父目录获取所有关卡
        :param parent_dir: 父目录路径
        :return: 关卡字典, 键为歌曲名, 值为(关卡对象, 文件路径)元组; 未解析的关卡列表, 元素为(关卡对象, 文件路径)元组
        """
        level_dirs: list[str] = tool_file.get_leveldirs_from_parent_dir_auto(parent_dir, console_log)
        adofai_filepaths: list[str] = []
        for level_dir in level_dirs:
            adofai_filepaths.append(tool_file.get_adofai_filepath_from_leveldir_auto(level_dir))
        
        result: dict[str, tuple[Level, str]] = {}
        unknown_result: list[tuple[Level, str]] = []
        with ProcessPoolExecutor(max_workers=settings.max_parse_level_threading) as executor:
            future_to_path = {executor.submit(tool_quick._parse_level, path, False): path for path in adofai_filepaths}
            for future in as_completed(future_to_path):
                path = future_to_path[future]
                try:
                    song_name, level, file_path = future.result()
                    if not song_name:
                        if console_log: logger.warning(f"发现未知关卡: {path}")
                        unknown_result.append((level, file_path))
                        continue
                    result[song_name] = (level, file_path)
                    if console_log: logger.info(f"发现关卡: {tool_fma.remove_unity_rich_text(song_name)}")
                except Exception as e:
                    logger.error(f"解析关卡失败: {path}, 错误: {e}")
        
        if console_log: logger.info(f"加载完成! 发现{len(result)}个关卡, {len(unknown_result)}个未知关卡")
        return result, unknown_result