"""面向生产项目的 Loguru 日志初始化模块。

设计目标：
- 直接使用 Loguru（不使用 logging）
- 保持 logger 原生 API（不封装 log_info/log_error 等方法）
- 仅提供配置、初始化与规范增强
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Literal

from loguru import logger

_ENV = Literal["dev", "prod"]


# 本地/开发环境下的人类可读格式。
_TEXT_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level:<8}</level> | "
    "pid={process.id} tid={thread.id} | "
    "<cyan>{module}</cyan>:<cyan>{line}</cyan> | "
    "rid={extra[request_id]} uid={extra[user_id]} | "
    "<level>{message}</level>"
)


# 幂等标记：便于排查与识别初始化状态。
_IS_CONFIGURED = False


def _patch_record(record: dict) -> None:
    """保证上下文字段存在，避免格式化占位符报错。"""
    record["extra"].setdefault("request_id", "-")
    record["extra"].setdefault("user_id", "-")


def _install_excepthook() -> None:
    """接管未捕获异常并写入 Loguru。"""
    original_hook = sys.excepthook

    def _hook(exc_type, exc_value, exc_traceback):  # type: ignore[no-untyped-def]
        if issubclass(exc_type, KeyboardInterrupt):
            original_hook(exc_type, exc_value, exc_traceback)
            return

        # 未捕获异常记录：这里显式传入异常三元组。
        # 在普通 except 代码块中，必须使用 logger.exception(...)。
        logger.opt(exception=(exc_type, exc_value, exc_traceback)).error("未捕获异常")

    sys.excepthook = _hook


def setup_logger(
    *,
    env: _ENV = "dev",
    log_dir: str | Path = "logs",
    level: str = "INFO",
    rotation: str = "00:00",
    retention: str = "7 days",
    compression: str = "zip",
    enable_json: bool = False,
    add_error_file: bool = True,
    catch_unhandled: bool = True,
) -> None:
    """初始化 Loguru 的控制台与文件输出。

    可重复调用且安全：
    - 每次先清理已有 handler（`logger.remove()`）
    - 再重建一套一致的输出配置

    参数：
        env: 环境类型，`dev` 或 `prod`。
        log_dir: 日志目录。
        level: 控制台最低日志级别。
        rotation: 轮转策略，默认每天零点切割。
        retention: 保留策略，默认保留 7 天。
        compression: 压缩格式（如 `zip`、`gz`）。
        enable_json: 是否输出 JSON 结构化日志（建议生产环境开启）。
        add_error_file: 是否额外输出 `logs/error.log`（仅 ERROR 及以上）。
        catch_unhandled: 是否安装 `sys.excepthook` 捕获未处理异常。
    """
    global _IS_CONFIGURED

    # 清理全部 handler，避免重复初始化导致重复输出。
    logger.remove()

    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    logger.configure(patcher=_patch_record)

    is_dev = env == "dev"
    use_color = is_dev and not enable_json

    # 控制台输出
    logger.add(
        sys.stderr,
        level=level,
        format=_TEXT_FORMAT,
        colorize=use_color,
        enqueue=True,
        serialize=enable_json,
        backtrace=is_dev,
        diagnose=is_dev,
    )

    # 主业务日志文件：INFO 及以上
    logger.add(
        log_path / "app.log",
        level="INFO",
        format=_TEXT_FORMAT,
        rotation=rotation,
        retention=retention,
        compression=compression,
        enqueue=True,
        serialize=enable_json,
        encoding="utf-8",
        backtrace=is_dev,
        diagnose=is_dev,
    )

    # 可选错误日志文件：ERROR 及以上
    if add_error_file:
        logger.add(
            log_path / "error.log",
            level="ERROR",
            format=_TEXT_FORMAT,
            rotation=rotation,
            retention=retention,
            compression=compression,
            enqueue=True,
            serialize=enable_json,
            encoding="utf-8",
            backtrace=is_dev,
            diagnose=is_dev,
        )

    if catch_unhandled:
        _install_excepthook()

    _IS_CONFIGURED = True


__all__ = ["logger", "setup_logger"]


# =========================
# 使用示例（必须）
# =========================
# from sololib.utils.logru_util import logger, setup_logger
#
# setup_logger(env="dev", enable_json=False)
#
# 1) 正常日志
# logger.info("服务启动完成")
#
# 2) 警告日志
# logger.warning("缓存未命中，key={}", "user:42")
#
# 3) 业务错误（非异常）
# logger.error("支付失败：order_id={} reason={}", "A1001", "余额不足")
#
# 4) 捕获异常（except 中）
# try:
#     1 / 0
# except Exception:
#     # 重要规范：
#     # 1. 在 except 中必须使用 logger.exception(...)
#     # 2. 严禁使用 logger.error(e)
#     logger.exception("处理请求时出现未预期异常")
#
# 5) bind 上下文
# req_logger = logger.bind(request_id="req-123", user_id="u-42")
# req_logger.info("请求已受理")
