---
name: sololib-guide
description: Guide for using the sololib Python toolkit — a library for corpus generation (template-based Q&A in Chinese/English), general-purpose utilities (async commands, HTTP, retry decorator, dict merge, Pydantic response models, version checking, YAML config loading, image template matching, Windows window management, loguru logging), and Nacos config center (remote config loading with hot-reload). Use when working with sololib, adding features to it, or integrating it into other projects.
---

# sololib Usage Guide

## Overview

**sololib** is a Python toolkit (v0.3.7.1) with three main modules:

1. **Corpus Generation** (`sololib.corpus`) — Template-based Chinese/English dialogue data generation
2. **General Utilities** (`sololib.utils`) — Async commands, HTTP, retry decorator, dict merge, Pydantic responses, version checking, YAML config, image matching, Windows management, loguru logging
3. **Nacos Config Center** (`sololib.configs`) — Remote config loading with hot-reload via nacos-sdk-python v3

## Corpus Generation

### Basic Usage

Import from the package root:

```python
from sololib import get_random_conversation

q, topic = get_random_conversation()
# Returns: (question_text, topic_name)
```

### Functions

| Function | Signature | Returns | Description |
|---|---|---|---|
| `get_random_conversation` | `(n: int = 1)` | `List[Tuple[str, str]]` | Generate 1–3 round dialogues. When `n=1` returns single list, when `n>1` returns list of lists |
| `generate_single_question` | `()` | `str` | Generate a single random question |
| `generate_questions` | `(n: int = 10)` | `List[str]` | Batch generate random questions |
| `get_corpus_stats` | `()` | `dict` | Get corpus statistics (template counts, variable pools, estimated combinations) |
| `estimate_combinations` | `()` | `int` | Estimate number of unique combinations |

### Probability Model

- Chinese probability: 10%
- Follow-up probability: 50%
- Three-round follow-up conditional probability: 40%

### Data Layer

The corpus data layer (`sololib.corpus.data`) contains:
- Variable pool `V`: `Dict[str, List[str]]` — 30 categories, each with 30 values
- Templates use `{varname}` placeholder syntax, filled by `core._fill()` with random replacement
- Auto language separation via Unicode range `\u4e00-\u9fff` for Q_EN/Q_CN and FU_EN/FU_CN

To add new variables or templates, edit `sololib/corpus/data.py`:
- Add new entries to `V` dict: `V["new_var"] = ["value1", "value2", ...]`
- Add templates to `Q_EN`, `Q_CN`, `FU_EN`, `FU_CN` lists
- Add topic keywords to `_TOPIC_KEYWORDS` dict for topic detection

## General Utilities

Import from `sololib.utils`:

```python
from sololib.utils import retry, run_command, post_data, merge_dicts, ResponseModel
```

### retry Decorator

Adaptive sync/async retry decorator:

```python
from sololib.utils import retry

@retry(max_retries=3, delay=3.0)
def flaky_sync():
    ...

@retry(max_retries=5, delay=1.0)
async def flaky_async():
    ...
```

- Automatically detects sync/async and uses appropriate sleep (`time.sleep` vs `asyncio.sleep`)
- Logs warnings on each attempt
- Raises `RuntimeError` with all attempts failed message after exhaustion

### run_command

Async subprocess command execution:

```python
from sololib.utils import run_command

result = await run_command("ls -la", timeout=30)
# {"stdout": "...", "stderr": "...", "returncode": 0}
```

Parameters:
- `command`: str or list — command to execute
- `input_content`: optional stdin bytes
- `shell`: bool — use shell for pipes/redirects
- `timeout`: optional seconds
- `cwd`: working directory
- `env`: environment variables dict

### post_data

Async HTTP POST JSON:

```python
from sololib.utils import post_data, UnauthorizedError

try:
    result = await post_data("https://api.example.com/data", {"key": "value"})
except UnauthorizedError:
    # Token expired
except SystemError as e:
    # Network or HTTP error
```

- Raises `UnauthorizedError` on 401
- Raises `SystemError` on other HTTP errors, network errors, or JSON parsing errors
- 30s timeout

### merge_dicts

Recursive dictionary merge:

```python
from sololib.utils import merge_dicts

merged = merge_dicts(base, override)
```

### ResponseModel

Pydantic unified API response format:

```python
from sololib.utils import success, error, result, result_page

success()                        # code=200, message="success"
result({"id": 1})               # code=200, message="success", data={"id": 1}
error(400, "Bad request")       # code=400, message="Bad request"
result_page([...], total=100)   # code=200, message="success", data=[...], total=100
```

### Version Checking

```python
from sololib.utils import check_package_update, update_package, get_current_version

needs_update = check_package_update("sololib", "0.3.5")  # True if newer available
update_package("sololib", "0.3.5")  # Update via poetry
```

### YAML Config Loading

```python
from sololib.utils import load_config

config = load_config("config.yaml")
```

### Image Template Matching (optional)

Requires `sololib[image]` (OpenCV + NumPy):

```python
from sololib.utils import resize_template, template_matching

# Resize a template image
resized = resize_template(template_path, target_width, target_height)

# Template matching
result = template_matching(source_image, template_image)
```

### Windows Window/Process Management (optional)

Requires `sololib[win32]` (psutil + pywin32):

```python
from sololib.utils import (
    activate_window_by_pid,
    check_if_already_running,
    check_process_exist,
    fetch_screen_number,
    fetch_screen_size,
    get_all_windows,
    get_hwnd_by_pid,
)
```

### Loguru Logging (optional)

Requires `pip install loguru`:

```python
from sololib.utils import setup_logger, shutdown_logger, logger

setup_logger(level="INFO")
logger.info("message")  # use the global logger
shutdown_logger()       # flush and close handlers
```

## Nacos Config Center

Requires `nacos-sdk-python >= 3.0.4` (included in core dependencies).

```python
from sololib.configs import NacosConfig, NacosStore, NacosWatcherSingle, NacosConfigError

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
config = store.get_config()  # merged dict from all configured files
store.close()
```

### Key Classes

- `NacosConfig` — Pydantic config parameters model (has nested `ConfigItem` class)
- `NacosStore` — Thread-safe singleton, supports multi-config deep merge (later-loaded overwrites earlier)
- `NacosWatcherSingle` — Single file watcher with hot-reload
- `NacosConfigError` — Custom exception

### Design Notes

- Compatible with nacos-sdk-python >= 3.0 (fully async gRPC API), exposes sync interface externally
- Internal `_AsyncLoop` bridges async SDK via background thread running asyncio event loop
- Single file change triggers full re-fetch to ensure coverage chain consistency

## Adding New Modules

When extending sololib:

1. **New utility functions**: Create `sololib/utils/xxx_util.py` with single responsibility
2. **New modules**: Use package structure `sololib/xxx/__init__.py` + implementation file, re-export public API in `__init__.py`
3. **All exported symbols must be declared in `__all__`** of the corresponding `__init__.py`
4. Module files must have a docstring at the top explaining the module's purpose
5. Use type annotations (full `typing` module + PEP 604 `X | Y` syntax)
6. Use `@functools.wraps` for decorators
7. Use `logging.getLogger(__name__)`, avoid `print` for debugging
8. Use custom Exception classes for business errors
9. Chinese docstrings for utility functions (`:param` / `:return` / `:raises` style)
10. Core dependencies go in `dependencies`; platform/feature-specific go in `optional-dependencies`

## Development Commands

```bash
# Install dependencies
uv sync

# Run main module (prints sample conversation for verification)
uv run sololib

# Check version
cat pyproject.toml  # version field
```

- Build system: hatchling
- Python requirement: >=3.11
- CLI entry point: `sololib` command runs `sololib:main`
