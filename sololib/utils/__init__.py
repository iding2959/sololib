"""sololib.utils - 通用工具函数集

各子模块::

    cmd_util        异步命令执行 (run_command)
    decorator_util  通用装饰器 (retry)
    dict_util       字典操作 (merge_dicts)
    httpx_util      异步 HTTP 请求 (post_data, UnauthorizedError)
    image_util      图像处理 (resize_template, template_matching) [可选: sololib[image]]
    logru_util      日志配置 (setup_logger, shutdown_logger, logger) [可选: loguru]
    response_util   统一响应模型 (success, error, result, result_page, ResponseModel)
    version_util    包版本检查与更新 (check_package_update, update_package, get_current_version)
    win32_util      Windows 窗口/进程管理 [可选: sololib[win32]]
    yaml_util       YAML 配置加载 (load_config)

安装可选依赖::

    pip install sololib[image]   # OpenCV + NumPy 图像处理
    pip install sololib[win32]   # psutil + pywin32 Windows 管理
    pip install loguru           # loguru 日志（可选）
"""

from sololib.utils.cmd_util import run_command
from sololib.utils.decorator_util import retry
from sololib.utils.dict_util import merge_dicts
from sololib.utils.httpx_util import UnauthorizedError, post_data
# logru（可选依赖）
try:
    from sololib.utils.logru_util import logger, setup_logger, shutdown_logger
except ImportError:
    pass
# image（可选依赖）
try:
    from sololib.utils.image_util import resize_template, template_matching
except (ImportError, AttributeError):
    pass
from sololib.utils.response_util import ResponseModel, error, result, result_page, success
from sololib.utils.version_util import check_package_update, get_current_version, update_package
from sololib.utils.yaml_util import load_config

# Windows 专用，导入失败时静默跳过
try:
    from sololib.utils.win32_util import (
        activate_window_by_pid,
        check_if_already_running,
        check_process_exist,
        fetch_screen_number,
        fetch_screen_size,
        get_all_windows,
        get_hwnd_by_pid,
    )
except ImportError:
    # 非 Windows 环境
    pass

__all__ = [
    # cmd
    "run_command",
    # decorator
    "retry",
    # dict
    "merge_dicts",
    # httpx
    "UnauthorizedError",
    "post_data",
    # logru
    "shutdown_logger",
    "logger",
    "setup_logger",
    # image
    "resize_template",
    "template_matching",
    # response
    "ResponseModel",
    "success",
    "error",
    "result",
    "result_page",
    # version
    "get_current_version",
    "check_package_update",
    "update_package",
    # yaml
    "load_config",
    # win32（可选）
    "activate_window_by_pid",
    "check_if_already_running",
    "check_process_exist",
    "fetch_screen_number",
    "fetch_screen_size",
    "get_all_windows",
    "get_hwnd_by_pid",
]
