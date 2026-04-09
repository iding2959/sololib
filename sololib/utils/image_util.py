"""
image_util - 图像处理工具函数

需要可选依赖：pip install sololib[image]
"""
import logging
from typing import Union

try:
    import cv2
    import numpy as np
except ImportError:
    cv2 = None  # type: ignore[assignment]
    np = None  # type: ignore[assignment]

from sololib.utils.decorator_util import retry

logger = logging.getLogger(__name__)


def _ensure_cv2():
    if cv2 is None:
        raise ImportError(
            "opencv-python and numpy are required for image utilities. "
            "Install with: pip install sololib[image]"
        )


def resize_template(
    template: np.ndarray,
    origin_width: int,
    origin_height: int,
    target_width: int,
    target_height: int,
) -> np.ndarray:
    """
    根据目标分辨率缩放模板图像。

    :param template: 原始模板图像
    :param origin_width: 模板原始宽度
    :param origin_height: 模板原始高度
    :param target_width: 目标宽度
    :param target_height: 目标高度
    :return: 缩放后的模板图像
    """
    _ensure_cv2()
    if origin_height == target_height and origin_width == target_width:
        return template
    # 计算缩放比例
    fx_scale = target_width / origin_width
    fy_scale = target_height / origin_height
    # scale = min(fx_scale, fy_scale)

    # 缩放模板图像
    resized_template = cv2.resize(template, None, fx=fx_scale, fy=fy_scale, interpolation=cv2.INTER_AREA)
    return resized_template


@retry()
def template_matching(
    session,
    template: np.ndarray,
    origin_res: tuple[int, int],
    is_gray: bool = True,
    threshold: float = 0.8,
    save_path: str | None = None,
) -> tuple[int, int, int, int] | None:
    """
    模板匹配, 返回大于阈值的最佳坐标，x1, y1, x2, y2
    """
    _ensure_cv2()
    image = session.screenshot(format='opencv')
    height, width, _ = image.shape
    target_res = (width, height)
    # 缩放模板图像
    resized_template = resize_template(template, origin_res[0], origin_res[1], target_res[0], target_res[1])
    try:
        if is_gray:
            # 转换为灰度图
            gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            gray_template = cv2.cvtColor(resized_template, cv2.COLOR_BGR2GRAY)
        else:
            gray_image = image
            gray_template = template
        # 使用模板匹配算法
        result = cv2.matchTemplate(gray_image, gray_template, cv2.TM_CCOEFF_NORMED)

        # 获取最佳匹配位置
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        logger.debug("max loc: %s, max val: %s", max_loc, max_val)
        if max_val < threshold:
            raise AssertionError(f'match failure max val -> {max_val}')
        top_left = max_loc  # 最佳匹配的左上角坐标
        # 计算匹配区域的右下角坐标
        bottom_right = (top_left[0] + resized_template.shape[1], top_left[1] + resized_template.shape[0])
        if save_path:
            # 在输入图像上绘制矩形框
            cv2.rectangle(image, top_left, bottom_right, (0, 255, 0), 2)
            # # 保存结果
            cv2.imwrite(save_path, image)
        return top_left[0], top_left[1], bottom_right[0], bottom_right[1]
    except Exception as e:
        raise AssertionError(f'match failure -> {e}')
