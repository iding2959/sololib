"""sololib - A simple Python library."""

__version__ = "0.1.0"

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