"""Nacos 配置中心模块

提供 Nacos 配置加载、监听、热更新能力。
兼容 nacos-sdk-python >= 3.0（全异步 API），对外暴露同步接口。
核心类:
    - NacosConfig: 配置参数模型 (Pydantic)
    - NacosStore: 配置存储与监听管理器 (单例)
"""

from __future__ import annotations

import asyncio
import threading
import weakref
from typing import TYPE_CHECKING, Callable, Optional

import yaml
from pydantic import BaseModel

if TYPE_CHECKING:
    from v2.nacos import ClientConfig, ConfigParam, NacosConfigService, NacosException

try:
    from v2.nacos import (
        ClientConfig,
        ConfigParam,
        NacosConfigService,
        NacosException,
    )
except ImportError:
    ClientConfig = None  # type: ignore[misc,assignment]
    ConfigParam = None  # type: ignore[misc,assignment]
    NacosConfigService = None  # type: ignore[misc,assignment]
    NacosException = Exception  # type: ignore[misc,assignment]

try:
    from nacos.client import logger as _nacos_logger
except ImportError:
    import logging
    _nacos_logger = logging.getLogger(__name__)


class NacosConfigError(Exception):
    """Nacos 配置异常"""
    pass


class NacosConfig(BaseModel):
    """Nacos 连接与配置参数"""

    class ConfigItem(BaseModel):
        """单个配置项"""
        data_id: str
        group: Optional[str] = "DEFAULT_GROUP"
        data_type: Optional[str] = "yaml"

    server_addresses: str
    namespace: Optional[str] = "public"
    username: str
    password: str
    configs: list[ConfigItem]


def _make_client_config(nacos_config: NacosConfig) -> "ClientConfig":
    """构建 v3 ClientConfig 对象"""
    if ClientConfig is None:
        raise NacosConfigError("nacos-sdk-python >= 3.0 未安装")
    return ClientConfig(
        server_addresses=nacos_config.server_addresses,
        namespace_id=nacos_config.namespace or "",
        username=nacos_config.username,
        password=nacos_config.password,
    )


def _resolve_config_info(config_info):
    """统一提取 config_info 的 data_id、group、data_type，兼容对象和字典"""
    if hasattr(config_info, "data_id"):
        return (
            config_info.data_id,
            getattr(config_info, "group", "DEFAULT_GROUP"),
            getattr(config_info, "data_type", "yaml"),
        )
    return (
        config_info["data_id"],
        config_info.get("group", "DEFAULT_GROUP"),
        config_info.get("data_type", "yaml"),
    )


class _AsyncLoop:
    """在后台线程中运行 asyncio event loop，供同步代码调用异步 nacos SDK"""

    def __init__(self):
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None
        self._ready = threading.Event()

    def start(self):
        """启动后台 event loop 线程"""
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        self._ready.wait()

    def _run_loop(self):
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._ready.set()
        self._loop.run_forever()

    def run(self, coro):
        """在后台 event loop 中同步执行协程"""
        if self._loop is None or not self._loop.is_running():
            raise NacosConfigError("后台 event loop 未运行")
        return asyncio.run_coroutine_threadsafe(coro, self._loop).result()

    def schedule(self, coro):
        """在后台 event loop 中调度协程（不等待结果）"""
        if self._loop and self._loop.is_running():
            asyncio.run_coroutine_threadsafe(coro, self._loop)

    async def _ensure_service(self, client_config: ClientConfig) -> "NacosConfigService":
        """创建并启动 NacosConfigService"""
        return await NacosConfigService.create_config_service(client_config)

    def create_service(self, client_config: ClientConfig) -> "NacosConfigService":
        """创建 NacosConfigService（同步入口）"""
        return self.run(self._ensure_service(client_config))

    def stop(self):
        """停止后台 event loop"""
        if self._loop and self._loop.is_running():
            self._loop.call_soon_threadsafe(self._loop.stop)
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5)


class NacosWatcherSingle:
    """Nacos 单一配置文件监听器"""

    def __init__(
        self,
        async_loop: _AsyncLoop,
        config_info,
        update_callback: Callable,
    ):
        self.async_loop = async_loop
        self.config_info = config_info
        self.update_callback = update_callback
        self._listener: Optional[Callable] = None

    def _make_callback(self):
        """生成适配 nacos v3 listener 签名的回调"""
        data_id, _, data_type = _resolve_config_info(self.config_info)

        def listener(content: str):
            _nacos_logger.info(f"接收到来自 {data_id} 的配置更新")
            if content is not None and data_type == "yaml":
                try:
                    parsed = yaml.safe_load(content)
                    self.update_callback(parsed)
                except Exception as e:
                    _nacos_logger.error(f"YAML 解析失败: {e}")
            elif content is None:
                _nacos_logger.warning(f"收到空内容: data_id={data_id}")

        return listener

    def start(self, service: "NacosConfigService"):
        """注册监听器"""
        data_id, group, _ = _resolve_config_info(self.config_info)
        self._listener = self._make_callback()
        _nacos_logger.info(f"为 {data_id} 添加配置监听器")
        self.async_loop.run(service.add_listener(data_id, group, self._listener))
        _nacos_logger.info(f"已为 {data_id} 添加配置监听器")

    def stop(self, service: "NacosConfigService"):
        """移除监听器"""
        if self._listener is None:
            return
        data_id, group, _ = _resolve_config_info(self.config_info)
        try:
            self.async_loop.run(service.remove_listener(data_id, group, self._listener))
        except Exception as e:
            _nacos_logger.warning(f"移除监听器时出错: {e}")
        self._listener = None


class NacosStore:
    """Nacos 配置存储与监听管理器 (单例)

    内部使用后台线程运行 asyncio event loop 以适配 nacos-sdk-python v3 的全异步 API。
    对外暴露同步接口。
    """

    _instance: Optional["NacosStore"] = None
    _lock = threading.Lock()
    _initialized = False
    _finalizers: list = []

    def __new__(cls, *args, **kwargs):
        if ClientConfig is None:
            raise NacosConfigError("nacos-sdk-python >= 3.0 未安装")
        if cls._instance is not None:
            return cls._instance
        with cls._lock:
            if cls._instance is not None:
                return cls._instance
            cls._instance = super().__new__(cls)
            return cls._instance

    def __init__(self, nacos_config: NacosConfig, is_watcher: bool = True):
        if type(self)._initialized:
            return

        with self._lock:
            if type(self)._initialized:
                return

            self._config_lock = threading.Lock()
            self._config: dict = {}
            self.nacos_config = nacos_config
            self.watchers: list[NacosWatcherSingle] = []
            self._is_watcher = is_watcher

            # 启动后台 event loop 并创建 NacosConfigService
            self._async_loop = _AsyncLoop()
            self._async_loop.start()
            client_cfg = _make_client_config(nacos_config)
            self._service = self._async_loop.create_service(client_cfg)

            self._init_all_configs()
            if is_watcher:
                self._start_watchers()

            finalizer = weakref.finalize(self, self._cleanup, self.watchers, self._service, self._async_loop)
            type(self)._finalizers.append(finalizer)
            type(self)._initialized = True

    @staticmethod
    def _cleanup(watchers: list, service, async_loop: _AsyncLoop):
        """程序退出时清理资源（幂等）"""
        _nacos_logger.info("开始清理 Nacos 资源...")
        for watcher in watchers:
            try:
                watcher.stop(service)
            except Exception:
                pass
        watchers.clear()
        coro = service.shutdown()
        try:
            async_loop.run(coro)
        except Exception:
            coro.close()
        try:
            async_loop.stop()
        except Exception:
            pass
        _nacos_logger.info("Nacos 资源清理完成")

    # ---- 配置获取与解析 ----

    def _fetch_config(self, config_info) -> Optional[str]:
        data_id, group, _ = _resolve_config_info(config_info)
        param = ConfigParam(data_id=data_id, group=group)
        try:
            return self._async_loop.run(self._service.get_config(param))
        except NacosException as e:
            _nacos_logger.warning(f"获取配置失败: data_id={data_id}, error={e}")
            return None

    def _parse_config(self, content: Optional[str], data_type: str) -> dict:
        if data_type != "yaml":
            raise NacosConfigError(f"不支持的数据类型: {data_type}")
        if content is None:
            _nacos_logger.warning("尝试解析 None 内容为 YAML")
            return {}
        try:
            return yaml.safe_load(content) or {}
        except Exception as e:
            raise NacosConfigError(f"解析 YAML 失败: {e}")

    def _merge_config(self, new_config: dict):
        """后加载的配置覆盖之前的同名配置（深合并）"""
        def deep_merge(base: dict, override: dict):
            for key, value in override.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    deep_merge(base[key], value)
                else:
                    base[key] = value

        with self._config_lock:
            deep_merge(self._config, new_config)

    # ---- 初始化与监听 ----

    def _init_all_configs(self):
        """按顺序加载所有配置，后面的覆盖前面的同名配置"""
        for config_info in self.nacos_config.configs:
            raw = self._fetch_config(config_info)
            if raw is not None:
                _, _, data_type = _resolve_config_info(config_info)
                parsed = self._parse_config(raw, data_type)
                self._merge_config(parsed)
            else:
                _nacos_logger.warning(f"未能获取到配置: {config_info}")

    def _start_watchers(self):
        for config_info in self.nacos_config.configs:
            watcher = NacosWatcherSingle(
                self._async_loop,
                config_info,
                self._on_config_update,
            )
            watcher.start(self._service)
            self.watchers.append(watcher)

    def _on_config_update(self, new_config: dict):
        """配置变更时全量重拉以保证覆盖链一致"""
        _nacos_logger.info(f"检测到配置更新: {new_config}")
        with self._config_lock:
            self._config = {}
        self._init_all_configs()
        _nacos_logger.info(f"更新后的完整配置: {self._config}")

    # ---- 公共 API ----

    def get_config(self) -> dict:
        """获取当前配置（线程安全）"""
        with self._config_lock:
            return dict(self._config)

    def refresh_config(self):
        """手动全量刷新配置（线程安全）"""
        with self._config_lock:
            self._config = {}
        self._init_all_configs()

    def close(self):
        """关闭所有监听器和客户端连接"""
        if getattr(self, "_closed", False):
            return
        self._closed = True
        _nacos_logger.info("开始关闭 Nacos 连接...")
        for watcher in self.watchers:
            watcher.stop(self._service)
        self.watchers.clear()
        with self._config_lock:
            self._config = {}
        coro = self._service.shutdown()
        try:
            self._async_loop.run(coro)
        except Exception as e:
            _nacos_logger.warning(f"关闭服务时出错: {e}")
            coro.close()
        self._async_loop.stop()
        _nacos_logger.info("Nacos 连接已关闭")

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass
