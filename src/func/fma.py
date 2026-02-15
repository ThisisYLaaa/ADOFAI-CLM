import re

from src.util.Logger import get_logger
logger = get_logger("信息处理")

class tool_fma:
    @staticmethod
    def remove_unity_rich_text(text: str) -> str:
        """移除 Unity 富文本标签, 例如 <b>, <color=#ff0000>, <size=20> 等
        :param text: 包含 Unity 富文本标签的原始字符串
        :return: 去除所有标签后的纯文本字符串
        """
        # 匹配任何以 < 开头，以 > 结尾的标签，中间不包含 '>' 字符
        # 该模式可以处理标签跨行的情况（因为 [^>] 包含换行符）
        r: str = re.sub(r'<[^>]*>', '', text)
        r = r.replace("\n", "")
        return r.strip()