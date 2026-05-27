"""sololib.utils.response_util - 统一响应模型与构造工具

提供 Pydantic 统一的 API 响应格式，支持成功、错误、数据和分页响应。

用法::

    from sololib.utils import success, error, result, result_page, ResponseModel

    success()                        # code=200, message="success"
    result({"id": 1})               # code=200, message="success", data={"id": 1}
    error(400, "Bad request")       # code=400, message="Bad request"
    result_page([...], total=100)   # code=200, message="success", data=[...], total=100
"""
from typing import Any, Optional

from pydantic import BaseModel, model_serializer


class ResponseModel(BaseModel):
    """统一响应模型"""

    code: int
    message: str
    data: Optional[Any] = None
    total: Optional[int] = None

    @model_serializer(mode='wrap')
    def _serialize(self, handler):
        result = handler(self)
        return {k: v for k, v in result.items() if v is not None}


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
