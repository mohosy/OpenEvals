from __future__ import annotations

from typing import Iterable


def normalize_judge_score(score_raw: int) -> float:
    score_clamped = min(max(score_raw, 1), 5)
    return (score_clamped - 1) / 4


def weighted_average(values: Iterable[tuple[float, float]]) -> float | None:
    pairs = list(values)
    if not pairs:
        return None
    total_weight = sum(weight for _, weight in pairs)
    if total_weight <= 0:
        return None
    return sum(value * weight for value, weight in pairs) / total_weight

