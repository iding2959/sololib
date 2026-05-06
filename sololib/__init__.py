"""sololib - Python 工具包

提供三大功能模块：
1. **语料生成** (sololib.corpus) — 基于模板变量填充的中英文对话数据生成
2. **通用工具集** (sololib.utils) — HTTP、装饰器、字典操作、日志、版本检查等
3. **Nacos 配置中心** (sololib.configs) — 基于 nacos-sdk-python v3 的远程配置加载与热更新

安装::

    pip install sololib
    pip install sololib[image]  # 可选：图像处理
    pip install sololib[win32]  # 可选：Windows 窗口管理

语料生成示例::

    from sololib import get_random_conversation
    q, topic = get_random_conversation()

    from sololib import generate_questions
    questions = generate_questions(n=5)

工具集示例::

    from sololib.utils import retry, merge_dicts, run_command

    @retry(max_retries=3)
    def flaky(): ...

Nacos 配置中心示例::

    from sololib.configs import NacosConfig, NacosStore
    store = NacosConfig(...)
    config = store.get_config()
"""

from sololib.corpus import (
    estimate_combinations,
    generate_questions,
    generate_single_question,
    get_corpus_stats,
    get_random_conversation,
)

__version__ = "0.3.7"

__all__ = [
    "greet",
    "main",
    "get_random_conversation",
    "estimate_combinations",
    "generate_single_question",
    "generate_questions",
    "get_corpus_stats",
]

from sololib.corpus import (
    estimate_combinations,
    generate_questions,
    generate_single_question,
    get_corpus_stats,
    get_random_conversation,
)


def greet(name: str) -> str:
    """Return a greeting message.

    Args:
        name: The name to greet.

    Returns:
        A greeting string.
    """
    return f"Hello, {name}!"


def main():
    print(greet("World"))
    print(f"\n语料库统计:")
    stats = get_corpus_stats()
    print(f"  英文问题模板: {stats['question_templates']['en']}")
    print(f"  中文问题模板: {stats['question_templates']['cn']}")
    print(f"  追问模板: {stats['followup_templates']['total']}")
    print(f"  估计组合数: {stats['estimated_combinations']:,}")
    print(f"\n示例对话:")
    conv = get_random_conversation()
    for q, t in conv:
        print(f"  [{t}] {q}")


if __name__ == "__main__":
    main()