"""
yaml_util - YAML 配置文件加载工具
"""
from typing import Any, Type, TypeVar

import yaml

T = TypeVar("T")


def load_config(file_path: str, config_class: Type[T]) -> T:
    """
    从 YAML 文件加载配置并返回指定类型的配置对象。

    :param file_path: 配置文件路径
    :param config_class: 配置类（必须支持 **kwargs 构造）
    :return: config_class 实例
    """
    with open(file_path, "r", encoding="utf-8") as file:
        config_data: dict[str, Any] = yaml.safe_load(file)
    return config_class(**config_data)
