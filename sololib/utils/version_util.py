"""sololib.utils.version_util - PyPI 包版本检查与更新工具

用法::

    from sololib.utils import check_package_update, update_package, get_current_version

    current = get_current_version("sololib")
    needs_update = check_package_update("sololib", current)
    update_package("sololib")
"""

from __future__ import annotations

import logging
import subprocess
import sys
from importlib import metadata

import httpx
from packaging import version

from sololib.utils import decorator_util

logger = logging.getLogger(__name__)


def get_current_version(package_name: str) -> str:
    """获取当前环境已安装包版本。"""
    try:
        return metadata.version(package_name)
    except metadata.PackageNotFoundError as exc:
        raise RuntimeError(f"Package '{package_name}' is not installed") from exc


@decorator_util.retry(max_retries=3, delay=3)
def check_package_update(package_name: str, current_version: str | None) -> bool | None:
    """检查 PyPI 是否有更新。"""
    if not current_version:
        logger.warning("未找到 %s", package_name)
        return None

    url = f"https://pypi.org/pypi/{package_name}/json"
    response = httpx.get(url, timeout=10)
    response.raise_for_status()

    latest_version = response.json()["info"]["version"]
    if version.parse(latest_version) > version.parse(current_version):
        logger.info("%s 有更新：%s -> %s", package_name, current_version, latest_version)
        return True

    logger.info("%s 已为最新版本。", package_name)
    return False


@decorator_util.retry(max_retries=3, delay=3)
def update_package(package_name: str, current_version: str | None = None) -> None:
    """使用 pip 升级指定包。"""
    del current_version  # 向后兼容旧签名
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "--upgrade", package_name, "--no-cache-dir"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        logger.error("Error updating package: %s", result.stderr.strip())
        raise RuntimeError(f"Error updating package: {result.stderr.strip()}")
