import math


def precision_at_k(ranked_keys: list[str], relevant_keys: set[str], k: int) -> float:
    top_k = ranked_keys[:k]
    if not top_k:
        return 0.0
    hits = sum(1 for key in top_k if key in relevant_keys)
    return hits / len(top_k)


def recall_at_k(ranked_keys: list[str], relevant_keys: set[str], k: int) -> float:
    if not relevant_keys:
        return 0.0
    top_k = ranked_keys[:k]
    hits = sum(1 for key in top_k if key in relevant_keys)
    return hits / len(relevant_keys)


def _dcg_at_k(ranked_keys: list[str], relevance_grades: dict[str, float], k: int) -> float:
    dcg = 0.0
    for i, key in enumerate(ranked_keys[:k], start=1):
        grade = relevance_grades.get(key, 0.0)
        dcg += grade / math.log2(i + 1)
    return dcg


def ndcg_at_k(ranked_keys: list[str], relevance_grades: dict[str, float], k: int) -> float:
    """
    relevance_grades: key -> grado (0, 1 o 2), típicamente el output del
    pooling de evals/relevance_judgments.py.
    """
    dcg = _dcg_at_k(ranked_keys, relevance_grades, k)

    ideal_order = sorted(relevance_grades.values(), reverse=True)[:k]
    idcg = sum(grade / math.log2(i + 1) for i, grade in enumerate(ideal_order, start=1))

    if idcg == 0:
        return 0.0

    return dcg / idcg
