import os

from src.util.Logger import get_logger
logger = get_logger("文件工具")
from src.func.interact import tool_interact
from src.UI.settings_manager import SettingsManager
settings_manager = SettingsManager()

class tool_file:
    @staticmethod
    def get_music_filepath_from_leveldir_auto(level_dir: str, console_log: bool = True) -> str:
        """从关卡目录获取音乐文件路径
        :param level_dir: 关卡目录路径
        :return: 音乐文件路径
        """
        fs: list[str] = os.listdir(level_dir)
        mfp: list[str] = []
        for f in fs:
            if f.endswith(".wav") or f.endswith(".ogg"):
                mfp.append(os.path.join(level_dir, f))
        if len(mfp)>0: return mfp[0]
        else:
            if console_log: logger.error(f"未找到音乐文件: {level_dir}")
            return ""

    @staticmethod
    def get_adofai_filepath_from_leveldir_auto(level_dir: str, console_log: bool = True) -> str:
        """从关卡目录获取adofai文件路径
        :param level_dir: 关卡目录路径
        :return: adofai文件路径
        """
        fs: list[str] = os.listdir(level_dir)
        priorities = settings_manager.settings.adofai_search_priorities
        afp_list: list[list[str]] = [[] for _ in priorities]
        
        for f in fs:
            if f.endswith(".adofai"):
                for i, keywords in enumerate(priorities):
                    if not keywords:
                        if "backup" in f: continue  # 没有指定关键词，且文件名包含backup，跳过
                        afp_list[i].append(os.path.join(level_dir, f))
                        break
                    if any([keyword in f for keyword in keywords]):
                        afp_list[i].append(os.path.join(level_dir, f))
                        break
        
        for i, afp in enumerate(afp_list):
            if len(afp) > 0:
                return afp[0]
        if console_log: logger.error(f"未找到adofai文件: {level_dir}")
        return ""
    
    @staticmethod
    def get_music_filepath_from_leveldir(level_dir: str, console_log: bool = True) -> str:
        """从关卡目录获取音乐文件路径
        :param level_dir: 关卡目录路径
        :return: 音乐文件路径
        """
        fs: list[str] = os.listdir(level_dir)
        mfp: list[str] = []
        for f in fs:
            if f.endswith(".wav") or f.endswith(".ogg"):
                mfp.append(os.path.join(level_dir, f))
        if len(mfp) == 0: return mfp[0]
        elif len(mfp) > 0:
            i: int = tool_interact.list_ask_index("请选择音乐文件", mfp)
            return mfp[i]
        else:
            if console_log: logger.error(f"未找到音乐文件: {level_dir}")
            return ""

    @staticmethod
    def get_adofai_filepath_from_leveldir(level_dir: str, console_log: bool = True) -> str:
        """从关卡目录获取adofai文件路径
        :param level_dir: 关卡目录路径
        :return: adofai文件路径
        """
        fs: list[str] = os.listdir(level_dir)
        priorities = settings_manager.settings.adofai_search_priorities
        afp_list: list[list[str]] = [[] for _ in priorities]
        
        for f in fs:
            if f.endswith(".adofai"):
                for i, keywords in enumerate(priorities):
                    if not keywords:
                        afp_list[i].append(os.path.join(level_dir, f))
                        break
                    if any([keyword in f for keyword in keywords]):
                        afp_list[i].append(os.path.join(level_dir, f))
                        break
        
        for afp in afp_list:
            if len(afp) == 1: return afp[0]
            elif len(afp) > 0:
                i: int = tool_interact.list_ask_index("请选择adofai文件", afp)
                return afp[i]
        if console_log: logger.error(f"未找到adofai文件: {level_dir}")
        return ""
    
    @staticmethod
    def get_leveldirs_from_parent_dir_auto(parent_dir: str, console_log: bool = True) -> list[str]:
        """从父目录获取关卡目录
        :param parent_dir: 父目录路径
        :return: 关卡目录列表
        """
        level_dirs: list[str] = []
        for root, dirs, files in os.walk(parent_dir):
            for dir in dirs:
                if any([f.endswith(".adofai") for f in os.listdir(os.path.join(root, dir))]):
                    level_dirs.append(os.path.join(root, dir))

        if len(level_dirs) == 0:
            if console_log: logger.error(f"未找到adofai文件: {parent_dir}")
            return []
        else:
            return level_dirs
