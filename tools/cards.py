"""Render a cluster as a short card for the chat room (8 lines or fewer)."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from tools.cluster import Cluster

MAX_LINES = 8
QUOTE_CHARS = 70
MARKERS = ("🟥", "🟧", "🟨")


@dataclass(frozen=True)
class Card:
    card_id: str
    rank: int
    severity: float
    cluster: Cluster


def _quote(text: str) -> str:
    text = " ".join(text.split())
    return f'"{text}"' if len(text) <= QUOTE_CHARS else f'"{text[: QUOTE_CHARS - 1].rstrip()}…"'


def render(card: Card) -> str:
    members = card.cluster.members
    count = len(members)
    mean_stars = sum(r.stars for r in members) / count
    versions = Counter(r.version for r in members).most_common()
    app = Counter(r.app for r in members).most_common(1)[0][0]
    marker = MARKERS[min(card.rank - 1, len(MARKERS) - 1)]
    lines = [
        f"{marker} {card.card_id} · {app} {versions[0][0]} · {count} reviews · "
        f"avg {mean_stars:.1f}★ · severity {card.severity:g}",
        "Themes: " + ", ".join(card.cluster.terms),
        " · ".join(_quote(t) for t in list(dict.fromkeys(r.text for r in members))[:2]),
        "Versions: " + ", ".join(f"{v} ({n})" for v, n in versions[:3]),
        "Suspected: (triage agent fills this in after reading the code)",
        "Proposed: (triage agent fills this in) · effort ?",
        "Owner: @fixer once a human assigns it",
    ]
    assert len(lines) <= MAX_LINES
    return "\n".join(lines)
