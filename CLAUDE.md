# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概览

**sololib** 是一个 Python 工具包（v0.3.5），提供三大功能模块：
1. **语料生成** (`sololib.corpus`) — 基于模板变量填充的中英文对话数据生成
2. **通用工具集** (`sololib.utils`) — HTTP、图像处理、装饰器、配置加载等实用函数
3. **Nacos 配置中心** (`sololib.configs`) — 基于 nacos-sdk-python v3 的远程配置加载与热更新

## 开发命令

```bash
# 安装依赖
uv sync

# 运行测试（直接运行主模块）
uv run sololib

# 查看当前版本
cat pyproject.toml  # version 字段
```

- 构建系统: **hatchling** (`[build-system] requires = ["hatchling"]`)
- Python 要求: `>=3.11`
- **无测试框架** — 目前没有测试文件，`uv run sololib` 通过打印示例对话验证功能

## 架构结构

```
sololib/
├── __init__.py          # 包入口：greet(), main()，从 corpus 子模块 re-export 5 个函数
├── corpus/              # 语料生成模块
│   ├── __init__.py      # re-export core.py 中的 5 个公共函数
│   ├── core.py          # 生成逻辑：_fill(), _detect_topic(), 对话组装
│   └── data.py          # 数据层：变量池 V (30 个 key, 各 30 值)，Q/FU 模板列表
├── configs/             # Nacos 配置中心模块
│   ├── __init__.py      # 导出 NacosConfig, NacosConfigError, NacosStore, NacosWatcherSingle
│   └── nacos_center.py  # 配置加载、监听、热更新（适配 nacos-sdk-python v3 异步 API）
└── utils/               # 通用工具模块（9 个子模块）
    ├── __init__.py      # 统一导出所有工具函数
    ├── cmd_util.py      # 异步子进程命令执行
    ├── decorator_util.py # retry 装饰器（同步/异步自适应）
    ├── dict_util.py     # 递归字典合并
    ├── httpx_util.py    # 异步 POST 请求 + UnauthorizedError
    ├── image_util.py    # OpenCV 模板匹配（resize_template, template_matching）
    ├── response_util.py # Pydantic 统一响应模型（ResponseModel）
    ├── version_util.py  # PyPI 版本检查与 poetry 更新
    ├── win32_util.py    # Windows 窗口/进程管理（可选导入）
    └── yaml_util.py     # YAML 配置加载为 typed object
```

### 导入约定

- **包级导出统一在 `__init__.py` 中管理**，使用 `from ... import ...` + `__all__`
- 子模块间通过 `sololib.utils.xxx` 绝对路径交叉引用（如 `version_util` import `cmd_util` 和 `decorator_util`）
- `win32_util` 使用 `try/except ImportError` 安全导入，非 Windows 环境静默跳过
- `nacos_center.py` 对 nacos-sdk-python 使用分离的 try/except 安全导入（v3 包路径 `v2.nacos`，旧版 `nacos.client`）

### Nacos 配置中心设计 (`configs/nacos_center.py`)

- 兼容 **nacos-sdk-python >= 3.0**（全异步 gRPC API），对外暴露同步接口
- 内部通过 `_AsyncLoop`（后台线程运行 asyncio event loop）桥接异步 SDK
- **`NacosStore`** 为线程安全单例，支持多配置文件深合并（后加载覆盖先加载）
- 支持配置监听（watcher），单文件变更时全量重拉保证覆盖链一致
- 依赖声明: `nacos-sdk-python >= 3.0.4` 放在核心 `dependencies`

### 语料数据层设计 (`corpus/data.py`)

- 变量池 `V`: `Dict[str, List[str]]`，30 个分类池，每池 30 个值
- 模板使用 `{varname}` 占位符语法，由 `core._fill()` 随机替换
- 自动中英文分离：通过 Unicode 范围 `\u4e00-\u9fff` 区分 Q_EN/Q_CN 和 FU_EN/FU_CN
- 中文概率: 10%，追问概率: 50%，三轮追问条件概率: 40%

## 代码规范

### 模块补充规范

- **新增工具函数**：在 `sololib/utils/` 下创建独立文件（如 `xxx_util.py`），单文件职责单一
- **新增模块**：使用包结构 `sololib/xxx/__init__.py` + 实现文件，`__init__.py` 中 re-export 公共 API
- **所有新导出的符号必须在对应 `__init__.py` 的 `__all__` 中声明**
- 模块文件顶部必须有文档字符串，说明该模块用途

### 编码风格

- **类型注解**：函数签名使用完整类型注解（`typing` 模块 + PEP 604 `X | Y` 语法）
- **装饰器**：使用 `@functools.wraps` 保持函数元信息
- **日志**：使用 `logging.getLogger(__name__)`，避免 `print` 调试
- **异常**：业务异常使用自定义 Exception 类（如 `UnauthorizedError`），不要裸抛 `Exception`
- **中文 docstring**：工具函数 docstring 使用中文（`:param` / `:return` / `:raises` 风格）
- **依赖声明**：核心依赖放在 `dependencies`；平台/功能专用依赖放在 `optional-dependencies` 对应分组中；使用 `try/except ImportError` 对可选模块进行安全导入
