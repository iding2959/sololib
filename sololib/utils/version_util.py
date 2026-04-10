"""sololib.utils.version_util - PyPI 包版本检查与更新工具

用法::

    from sololib.utils import check_package_update, update_package, get_current_version

    needs_update = check_package_update("sololib", "0.3.5")  # True if newer version available
    update_package("sololib", "0.3.5")  # Updates via poetry
"""
import asyncio
import logging
import subprocess
from typing import Optional

import httpx
from packaging import version

from sololib.utils import cmd_util, decorator_util

logger = logging.getLogger(__name__)


def get_current_version(package_name):
    current_version_cmd = f'poetry show {package_name}'
    result = asyncio.run(cmd_util.run_command(current_version_cmd))
    # result = subprocess.run(["poetry", "show", package_name], capture_output=True, text=True)
    if result.get('returncode') == 0:
        return result.get('stdout').splitlines()[1].split()[2]
    raise RuntimeError(f"Error checking package version: {result.get('stderr')}")


@decorator_util.retry(max_retries=3, delay=3)
def check_package_update(package_name, current_version):
    if not current_version:
        logger.warning("未找到 %s", package_name)
        return None
    url = f"https://pypi.org/pypi/{package_name}/json"
    response = httpx.get(url, timeout=10)
    try:
        if response.status_code == 200:
            latest_version = response.json()["info"]["version"]
            if version.parse(latest_version) > version.parse(current_version):
                logger.info("%s 有更新：%s -> %s", package_name, current_version, latest_version)
                return True
            else:
                logger.info("%s 已为最新版本。", package_name)
                return False
        return False
    except Exception as e:
        logger.error("检查 %s 版本时出错：%s", package_name, e)
        raise RuntimeError(f"Error checking package version: {e}")


@decorator_util.retry(max_retries=3, delay=3)
def update_package(package_name, current_version):
    # result = subprocess.run(
    #     ["poetry", "cache", "clear", f"pypi:{package_name}:{current_version}", " --no-interaction"],
    #     input="\n",  # 发送回车确认
    #     text=True,
    #     capture_output=True,
    #     shell=True  # Windows 需要 shell=True
    # )
    # if result.stderr:
    #     print("Cache clear Error:", result.stderr)
    #     raise RuntimeError(f"Error clearing cache: {result.stderr}")
    result = subprocess.run(["poetry", "update", package_name, " --no-cache "], capture_output=True, text=True)
    if result.returncode != 0:
        logger.error("Error updating package: %s", result.stderr)
        raise RuntimeError(f"Error updating package: {result.stderr}")
