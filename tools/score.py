"""Severity: how many people, how unhappy, how recent."""

from __future__ import annotations

from datetime import date

from tools.ingest import Review


def severity(members: list[Review] | tuple[Review, ...], as_of: date, half_life_days: float = 14.0) -> float:
    """count × (6 − mean stars) × mean recency weight.

    Recency weight halves every `half_life_days`, so a cluster of old complaints
    ranks below a fresh one of the same size. Pass `as_of` explicitly so the
    score is reproducible.
    """
    if not members:
        return 0.0
    count = len(members)
    mean_stars = sum(r.stars for r in members) / count
    recency = sum(0.5 ** (max((as_of - r.submitted).days, 0) / half_life_days) for r in members) / count
    return round(count * (6 - mean_stars) * recency, 1)
