"""
logru_util - 基于 loguru 的日志封装

提供开箱即用的日志配置，支持控制台 + 文件输出、按级别/时间轮转、异步安全等。
"""
import sys
from pathlib import Path
from typing import Literal

from loguru import logger


def setup_logger(
    log_dir: str | Path = "logs",
    level: str = "INFO",
    rotation: str = "00:00",
    retention: str = "7 days",
    compression: str = "zip",
    format_: str = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    ),
    sink_file: bool = True,
    sink_console: bool = True,
    console_level: str = "INFO",
    file_level: str = "DEBUG",
    enqueue: bool = True,
    serialize: bool = False,
) -> None:
    """
    配置 loguru 日志器。

    :param log_dir: 日志文件存放目录
    :param level: 全局最低日志级别
    :param rotation: 日志轮转策略（如 "00:00" 每日零点、"500 MB" 按大小）
    :param retention: 日志保留时长（如 "7 days"、"1 month"）
    :param compression: 压缩格式（"zip"、"gz"、None）
    :param format_: 日志输出格式（支持 colorama/ANSI 颜色标签）
    :param sink_file: 是否输出到文件
    :param sink_console: 是否输出到控制台
    :param console_level: 控制台日志级别
    :param file_level: 文件日志级别
    :param enqueue: 是否使用多进程/线程安全队列（异步安全）
    :param serialize: 是否以 JSON 格式序列化日志
    """
    # 移除默认 handler
    logger.remove()

    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    if sink_console:
        logger.add(
            sys.stderr,
            level=console_level,
            format=format_,
            colorize=True,
            enqueue=enqueue,
        )

    if sink_file:
        # 按级别拆分文件：{level}.log
        logger.add(
            log_dir / "{level}.log",
            level=file_level,
            format=format_,
            rotation=rotation,
            retention=retention,
            compression=compression,
            enqueue=enqueue,
            serialize=serialize,
            encoding="utf-8",
        )


def get_logger(name: str | None = None) -> "logger":
    """
    获取 loguru logger 实例。

    :param name: 可选的日志名称（会注入到 {name} 占位符）
    :return: loguru logger 实例

    示例::

        logger = get_logger(__name__)
        logger.info("Hello, world!")
    """
    if name:
        return logger.bind(name=name)
    return logger


__all__ = [
    "get_logger",
    "logger",
    "setup_logger",
]
