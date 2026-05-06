# sololib

一个 Python 工具包（v0.3.7），提供 **语料生成**、**通用工具集** 和 **Nacos 配置中心** 三大功能模块。

## 安装

```bash
pip install sololib
# 或
uv add sololib

# 可选依赖（图像处理）
pip install sololib[image]
# 可选依赖（Windows 窗口管理）
pip install sololib[win32]
```

## 快速开始

### 1. 语料生成 (`sololib.corpus`)

基于 30 个变量池（每池 30 值）和 500+ 中英文问题模板，随机生成对话数据。

```python
from sololib import get_random_conversation

# 生成单轮对话
q, topic = get_random_conversation()
print(f"[{topic}] {q}")

# 批量生成
conversations = get_random_conversation(n=10)

# 批量生成随机问题
from sololib import generate_questions
questions = generate_questions(n=5)

# 生成单个问题
from sololib import generate_single_question
single = generate_single_question()

# 查看语料统计
from sololib import get_corpus_stats
stats = get_corpus_stats()

# 估算模板组合数
from sololib import estimate_combinations
total = estimate_combinations()
```

**概率模型：**
- 中文概率：10%，追问概率：50%，三轮追问条件概率：40%
- 自动中英文分离（通过 Unicode 范围检测）

### 2. 通用工具集 (`sololib.utils`)

```python
# ---- 异步命令执行 ----
from sololib.utils import run_command
import asyncio

result = await run_command("ls -la", timeout=30)
# {"stdout": "...", "stderr": "...", "returncode": 0}

# ---- 重试装饰器（同步/异步自适应）----
from sololib.utils import retry

@retry(max_retries=3, delay=3.0)
def flaky_function():
    ...

@retry(max_retries=5, delay=1.0)
async def async_flaky_function():
    ...

# ---- 递归字典合并 ----
from sololib.utils import merge_dicts
merged = merge_dicts({"a": {"x": 1}}, {"a": {"y": 2}})
# {"a": {"x": 1, "y": 2}}

# ---- 异步 HTTP POST ----
from sololib.utils import post_data
result = await post_data("https://api.example.com/data", {"key": "value"})

# ---- Pydantic 统一响应模型 ----
from sololib.utils import success, error, result, result_page, ResponseModel

resp = success()          # ResponseModel(code=200, message="success")
resp = result({"id": 1})  # ResponseModel(code=200, message="success", data={"id": 1})
resp = error(400, "Bad request")
resp = result_page([{"id": 1}], total=100)

# ---- PyPI 版本检查 ----
from sololib.utils import check_package_update, update_package, get_current_version

needs_update = check_package_update("sololib", "0.3.5")
update_package("sololib", "0.3.5")

# ---- YAML 配置加载 ----
from sololib.utils import load_config
from dataclasses import dataclass

@dataclass
class AppConfig:
    host: str
    port: int

config = load_config("app.yaml", AppConfig)

# ---- 日志（可选依赖 loguru）----
from sololib.utils import setup_logger, get_logger, logger

setup_logger(log_dir="logs", level="INFO")
my_logger = get_logger(__name__)
logger.info("Hello, world!")
```

### 3. Nacos 配置中心 (`sololib.configs`)

基于 nacos-sdk-python v3 全异步 gRPC API，对外暴露同步接口，支持配置热更新。

```python
from sololib.configs import NacosConfig, NacosStore

# 初始化配置（连接 Nacos 并自动拉取所有配置）
nacos_config = NacosConfig(
    server_addresses="127.0.0.1:9848",
    namespace="public",
    username="nacos",
    password="nacos",
    configs=[
        NacosConfig.ConfigItem(data_id="app.yaml", group="DEFAULT_GROUP"),
        NacosConfig.ConfigItem(data_id="db.yaml", group="DEFAULT_GROUP"),
    ],
)

store = NacosStore(nacos_config, is_watcher=True)

# 获取合并后的完整配置
config = store.get_config()

# 手动刷新
store.refresh_config()

# 关闭连接
store.close()
```

## 版本要求

- Python >= 3.11

## License

MIT
