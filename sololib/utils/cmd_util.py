"""sololib.utils.cmd_util - 异步命令执行工具

用法::

    from sololib.utils import run_command
    result = await run_command("ls -la", timeout=30)
    # {"stdout": "...", "stderr": "...", "returncode": 0}
"""
import asyncio
import shlex
from typing import Any, BinaryIO, Dict, List, Optional, Union


async def run_command(
    command: Union[str, List[str]],
    input_content: Optional[bytes] = None,
    shell: bool = False,
    timeout: Optional[int] = None,
    cwd: Optional[str] = None,
    env: Optional[Dict[str, str]] = None,
) -> Dict[str, Union[str, int]]:
    """
    异步执行命令并返回结果。

    :param command: 命令字符串或列表
    :param input_content: 可选标准输入（bytes）
    :param shell: 是否使用 shell 执行（支持管道和重定向）
    :param timeout: 超时时间（秒），None 表示不限
    :param cwd: 工作目录
    :param env: 环境变量字典
    :return: {"stdout": str, "stderr": str, "returncode": int}
    :raises TimeoutError: 命令执行超时
    """
    if isinstance(command, str):
        cmd = command if shell else shlex.split(command)
    else:
        cmd = command

    if shell:
        process = await asyncio.create_subprocess_shell(
            cmd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd,
            env=env,
        )
    else:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd,
            env=env,
        )

    try:
        stdout, stderr = await asyncio.wait_for(
            process.communicate(input=input_content), timeout=timeout
        )
    except asyncio.TimeoutError:
        process.kill()
        await process.wait()
        raise TimeoutError(f"Command '{command}' timed out after {timeout}s")

    return {
        "stdout": stdout.decode().strip(),
        "stderr": stderr.decode().strip(),
        "returncode": process.returncode,
    }
