"""
语料库模块 - 对话数据生成工具

提供大量可组合的对话模板，用于生成多样化的对话数据。
"""
from sololib.corpus.core import (
    estimate_combinations,
    generate_single_question,
    generate_questions,
    get_corpus_stats,
    get_random_conversation,
)

__all__ = [
    "get_random_conversation",
    "estimate_combinations",
    "generate_single_question",
    "generate_questions",
    "get_corpus_stats",
]