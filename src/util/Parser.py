import json, re

from src.util.Logger import get_logger
logger = get_logger("关卡解析")

def get_level_json(file_path: str) -> dict:
    with open(file_path, 'r', encoding='utf-8-sig') as file:
        content: str = file.read()
    
    # 去掉不可打印字符
    try:
        return json.loads(
            "".join(c for c in content if c.isprintable())
        )
    except json.JSONDecodeError as e:
        pass

    rontent: str = re.sub(r',\s*([}\]])', r'\1', content)

    # 修复缺失的右括号
    open_braces: int = rontent.count('{') - rontent.count('}')
    open_brackets: int = rontent.count('[') - rontent.count(']')
    if open_braces > 0:
        rontent += '}' * open_braces
    if open_brackets > 0:
        rontent += ']' * open_brackets
    
    # 统计所有未闭合的结构并补全
    stack: list[tuple[str, int]] = []
    for i, char in enumerate(rontent):
        if char == '{':
            stack.append(('}', i))
        elif char == '[':
            stack.append((']', i))
        elif char == '}' or char == ']':
            if stack and stack[-1][0] == char:
                stack.pop()
    
    # 按逆序补全缺失的右括号
    for char, _ in reversed(stack):
        rontent += char
    
    try:
        return json.loads(rontent)
    except json.JSONDecodeError as e:
        pass
    
    # 前人留下的神秘代码
    # 注意: 这个做法会导致失去空格
    rontent = content.replace('\n', '') \
                .replace(" ", "") \
                .replace("	", "") \
                .replace(',,', ',') \
                .replace(',]', ']') \
                .replace(',}', '}') \
                .replace(']"', '],"')

    try:
        return json.loads(rontent)
    except json.JSONDecodeError as e:
        logger.error(f"[Parser]文件读取失败: {e}")
        return {}
