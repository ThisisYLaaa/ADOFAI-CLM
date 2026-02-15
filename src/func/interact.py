from src.util.Logger import get_logger
logger = get_logger("交互")

class tool_interact:
    @staticmethod
    def ask_yes_no(question: str) -> bool:
        """询问用户是否确认执行某个操作
        :param question: 确认操作的问题
        :return: 用户是否确认执行操作
        """
        while True:
            logger.info(question)
            ans: str = input("(y/n) ")
            if ans.lower() == "y":
                return True
            elif ans.lower() == "n":
                return False
            else:
                logger.error("请输入y或n")
    
    @staticmethod
    def list_ask_index(question: str, lst: list[str]) -> int:
        """询问用户从列表中选择一个索引
        :param question: 选择索引的问题
        :param lst: 可选择的索引列表
        :return: 用户选择的索引
        """
        while True:
            logger.info(question)
            for i, item in enumerate(lst):
                logger.info(f"{i}: {item}")
            ans: str = input("请输入索引: ")
            if ans.isdigit() and 0 <= int(ans) < len(lst):
                return int(ans)
            else:
                logger.error("请输入一个有效的索引")