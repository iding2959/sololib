"""
httpx_util - 基于 httpx 的异步 HTTP 请求工具
"""
import httpx


class UnauthorizedError(Exception):
    """401 Unauthorized 错误（Token 可能已过期）"""
    pass


async def post_data(url: str, data: dict, headers: dict | None = None) -> dict:
    """
    异步 POST JSON 数据。

    :param url: 请求地址
    :param data: 请求体（dict，将序列化为 JSON）
    :param headers: 可选请求头
    :return: 响应 JSON（dict）
    :raises UnauthorizedError: 401 认证失败
    :raises SystemError: 其他 HTTP / 网络 / 解析错误
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=data, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise UnauthorizedError("Unauthorized: Token may be expired")
            raise SystemError(f"HTTP error: {e}")
        except httpx.HTTPError as e:
            raise SystemError(f"Network error: {e}")
        except ValueError as e:
            raise SystemError(f"JSON parsing error: {e}")
        except Exception as e:
            raise SystemError(f"Unexpected error: {e}")
