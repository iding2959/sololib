"""
dict_util - 字典操作工具
"""


def merge_dicts(dict1: dict, dict2: dict) -> dict:
    """
    递归合并两个字典。

    - 若对应值为嵌套 dict，递归合并
    - 否则 dict2 的值覆盖 dict1 的值

    :param dict1: 基础字典
    :param dict2: 待合并字典
    :return: 合并后的新字典
    """
    merged = dict1.copy()
    for key, value in dict2.items():
        if key not in merged:
            merged[key] = value
        elif isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = merge_dicts(merged[key], value)
        else:
            merged[key] = value
    return merged
