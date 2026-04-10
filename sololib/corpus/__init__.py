"""
sololib.corpus - 语料数据生成模块

基于 30 个变量池（每池 30 值）和 500+ 中英文问题模板，通过变量填充生成多样化对话数据。
支持中英文混合，自动检测语义并选择对应模板。

用法::

    from sololib import get_random_conversation
    q, topic = get_random_conversation()  # 单轮
    conversations = get_random_conversation(n=10)  # 批量

    from sololib import generate_questions, get_corpus_stats
    questions = generate_questions(n=5)
    stats = get_corpus_stats()

概率模型::
    中文概率: 10%
    追问概率: 50%
    三轮追问条件概率: 40%
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