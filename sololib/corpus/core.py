"""sololib.corpus.core - 语料生成核心逻辑

提供对话生成、模板填充、话题检测等核心函数。
所有公共 API 均通过 ``sololib.corpus.__init__`` 和 ``sololib.__init__`` re-export。

主要函数::
    get_random_conversation(n=1) -> 生成 1-3 轮随机对话
    generate_questions(n=10) -> 批量生成随机问题
    generate_single_question() -> 生成单个随机问题
    get_corpus_stats() -> 获取语料库统计信息
    estimate_combinations() -> 估算不重复组合数
"""
import random
import re
from typing import List, Tuple

from sololib.corpus.data import (
    FU,
    FU_CN,
    FU_EN,
    Q,
    Q_CN,
    Q_EN,
    V,
    _TOPIC_KEYWORDS,
)


def _detect_topic(text: str) -> str:
    """从问题内容推断话题名"""
    text_lower = text.lower()
    for topic, keywords in _TOPIC_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            return topic
    # 回退：提取第一个变量值作为话题
    match = re.search(r"\{(\w+)\}", text)
    if match:
        var_name = match.group(1)
        pool = V.get(var_name)
        if pool:
            return random.choice(pool).lower()
    return "general"


def _fill(template: str) -> str:
    """替换模板中所有 {var}"""
    def _repl(m):
        key = m.group(1)
        pool = V.get(key)
        return random.choice(pool) if pool else m.group(0)
    return re.sub(r"\{(\w+)\}", _repl, template)


def get_random_conversation(n: int = 1) -> List[Tuple[str, str]]:
    """
    生成 1-3 轮随机对话 [(question, topic_name), ...]

    Args:
        n: 生成多少组对话，默认 1

    Returns:
        对话列表，每组是一个多轮对话
    """
    results = []
    for _ in range(n):
        # 10% 概率中文，90% 英文
        is_cn = random.random() < 0.10 and Q_CN
        q_pool = Q_CN if is_cn else Q_EN
        fu_pool = FU_CN if is_cn else FU_EN

        q = _fill(random.choice(q_pool))
        topic = _detect_topic(q)
        rounds = [(q, topic)]

        if random.random() < 0.50 and fu_pool:
            fq = _fill(random.choice(fu_pool))
            rounds.append((fq, topic))
            if random.random() < 0.40 and len(fu_pool) > 1:
                fq2 = _fill(random.choice(fu_pool))
                rounds.append((fq2, topic))

        results.append(rounds)
    return results if n > 1 else results[0]


def estimate_combinations() -> int:
    """估算不重复组合数"""
    total = 0
    for tmpl in Q + FU:
        slots = list(set(re.findall(r"\{(\w+)\}", tmpl)))
        combo = 1
        for s in slots:
            combo *= len(V.get(s, [1]))
        total += combo
    return total


def generate_single_question() -> str:
    """生成单个随机问题"""
    is_cn = random.random() < 0.10 and Q_CN
    q_pool = Q_CN if is_cn else Q_EN
    return _fill(random.choice(q_pool))


def generate_questions(n: int = 10) -> List[str]:
    """批量生成随机问题"""
    is_cn = random.random() < 0.10 and Q_CN
    q_pool = Q_CN if is_cn else Q_EN
    return [_fill(random.choice(q_pool)) for _ in range(n)]


def get_corpus_stats() -> dict:
    """获取语料库统计信息"""
    return {
        "question_templates": {
            "en": len(Q_EN),
            "cn": len(Q_CN),
            "total": len(Q),
        },
        "followup_templates": {
            "en": len(FU_EN),
            "cn": len(FU_CN),
            "total": len(FU),
        },
        "estimated_combinations": estimate_combinations(),
        "variable_pools": {k: len(v) for k, v in V.items()},
    }