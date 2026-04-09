"""
response_util - 统一响应模型与构造工具
"""
from typing import Any, Optional

from pydantic import BaseModel


class ResponseModel(BaseModel):
    """统一响应模型"""

    code: int
    message: str
    data: Optional[Any] = None
    total: Optional[int] = None


def success() -> ResponseModel:
    """返回成功响应（无数据）"""
    return ResponseModel(code=200, message="success")


def error(error_code: int, message: str) -> ResponseModel:
    """返回错误响应"""
    return ResponseModel(code=error_code, message=message)


def result(data: Any) -> ResponseModel:
    """返回带数据的成功响应"""
    return ResponseModel(code=200, message="success", data=data)


def result_page(data: Any, total: int) -> ResponseModel:
    """返回分页数据响应"""
    return ResponseModel(code=200, message="success", data=data, total=total)
