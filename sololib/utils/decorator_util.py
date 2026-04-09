"""
decorator_util - 通用装饰器
"""
import asyncio
import functools
import logging
import time

logger = logging.getLogger(__name__)


def retry(max_retries: int = 3, delay: float = 3.0):
    """
    重试装饰器，支持同步和异步方法。

    :param max_retries: 最大重试次数
    :param delay: 每次重试之间的延迟（秒）
    :return: 装饰后的函数
    """

    def decorator(func):
        if asyncio.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                last_exception = None
                for attempt in range(max_retries):
                    try:
                        return await func(*args, **kwargs)
                    except Exception as e:
                        last_exception = e
                        logger.warning("Attempt %s/%s failed: %s", attempt + 1, max_retries, e)
                        if attempt < max_retries - 1:
                            await asyncio.sleep(delay)
                raise Exception(f"All {max_retries} attempts failed. Last error: {last_exception}")

            return async_wrapper

        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                last_exception = None
                for attempt in range(max_retries):
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        last_exception = e
                        logger.warning("Attempt %s/%s failed: %s", attempt + 1, max_retries, e)
                        if attempt < max_retries - 1:
                            time.sleep(delay)
                raise Exception(f"All {max_retries} attempts failed. Last error: {last_exception}")

            return sync_wrapper

    return decorator
