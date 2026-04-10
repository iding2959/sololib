"""sololib.configs - Nacos 配置中心模块

提供 Nacos 配置加载、监听、热更新能力。
兼容 nacos-sdk-python >= 3.0（全异步 API），对外暴露同步接口。

核心类::
    NacosConfig       配置参数模型 (Pydantic)
    NacosStore        配置存储与监听管理器 (单例)
    NacosWatcherSingle 单一文件监听器
    NacosConfigError  配置异常

用法::

    from sololib.configs import NacosConfig, NacosStore

    nacos_config = NacosConfig(
        server_addresses="127.0.0.1:9848",
        namespace="public",
        username="nacos",
        password="nacos",
        configs=[
            NacosConfig.ConfigItem(data_id="app.yaml", group="DEFAULT_GROUP"),
        ],
    )
    store = NacosStore(nacos_config, is_watcher=True)
    config = store.get_config()
    store.close()
"""

from sololib.configs.nacos_center import (
    NacosConfig,
    NacosConfigError,
    NacosStore,
    NacosWatcherSingle,
)

__all__ = [
    "NacosConfig",
    "NacosConfigError",
    "NacosStore",
    "NacosWatcherSingle",
]
