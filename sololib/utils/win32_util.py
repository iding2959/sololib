"""sololib.utils.win32_util - Windows 平台窗口与进程管理工具

需要可选依赖：``pip install sololib[win32]``（psutil + pywin32）

仅在 Windows 环境下可用。

用法::

    from sololib.utils import activate_window_by_pid, get_all_windows, check_process_exist

    hwnds = get_all_windows()  # [(hwnd, pid, title), ...]
    activated = activate_window_by_pid(pid)
    exists = check_process_exist("python.exe")
"""
import time
import tkinter as tk

import psutil
import win32gui
import win32process
from win32.lib import win32con


def activate_window_by_pid(t_pid: int) -> bool:
    """
    通过进程 ID 激活对应窗口。

    :param t_pid: 目标进程 ID
    :return: 是否成功激活
    """
    hwnd = None
    start_time = time.time()
    timeout = 30
    while True:
        if time.time() - start_time > timeout:
            return False
        hwnd = get_hwnd_by_pid(t_pid)
        if hwnd:
            break
        time.sleep(0.5)

    if not hwnd:
        return False

    for _ in range(5):
        try:
            win32gui.ShowWindow(hwnd, win32con.SW_SHOWNORMAL)
            time.sleep(0.1)
            win32gui.ShowWindow(hwnd, win32con.SW_FORCEMINIMIZE)
            time.sleep(0.1)
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            time.sleep(0.1)
            win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
            time.sleep(0.1)
            win32gui.SetActiveWindow(hwnd)
            return True
        except Exception:
            time.sleep(0.5)
    return False


def _enum_windows_callback(hwnd: int, windows: list) -> None:
    if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        windows.append((hwnd, pid, win32gui.GetWindowText(hwnd)))


def get_all_windows() -> list[tuple[int, int, str]]:
    """
    获取所有可见窗口列表。

    :return: [(hwnd, pid, title), ...]
    """
    windows: list = []
    win32gui.EnumWindows(_enum_windows_callback, windows)
    return windows


def get_hwnd_by_pid(t_pid: int) -> int | None:
    """
    通过进程 ID 获取窗口句柄。

    :param t_pid: 进程 ID
    :return: hwnd 或 None
    """
    for ahwnd, pid, title in get_all_windows():
        try:
            if pid == t_pid:
                return ahwnd
        except psutil.NoSuchProcess:
            pass
    return None


def check_process_exist(process_name: str) -> bool:
    """
    检查指定名称的进程是否存在。

    :param process_name: 进程名（如 "python.exe"）
    """
    for proc in psutil.process_iter(["pid", "name"]):
        if proc.name() == process_name:
            return True
    return False


def check_if_already_running() -> tuple[bool, psutil.Process | None]:
    """
    检查当前程序是否已有其他实例在运行。

    :return: (is_running, other_process)
    """
    current = psutil.Process()
    for proc in psutil.process_iter(["pid", "name"]):
        if proc.pid != current.pid and proc.name() == current.name():
            return True, proc
    return False, None


def fetch_screen_size() -> tuple[int, int]:
    """
    获取主屏幕分辨率。

    :return: (width, height)
    """
    root = tk.Tk()
    w, h = root.winfo_screenwidth(), root.winfo_screenheight()
    root.destroy()
    return w, h


def fetch_screen_number() -> tuple[int, int, list[tuple[int, int]]]:
    """
    获取屏幕数量、各屏位置及主程序所在屏幕索引。

    :return: (screen_count, main_screen_index, screen_positions)
    """
    root = tk.Tk()
    win_x, win_y = root.winfo_screenwidth(), root.winfo_screenheight()

    screen_count = root.tk.call("tk", "windowingsystem", "window", "list")
    positions: list[tuple[int, int]] = [
        (root.winfo_x(), root.winfo_y()) for _ in range(len(screen_count))
    ]

    main_index = 0
    for i, (x, y) in enumerate(positions):
        if x <= win_x < x + root.winfo_screenwidth() and y <= win_y < y + root.winfo_screenheight():
            main_index = i
            break

    root.destroy()
    return len(screen_count), main_index, positions
