"""Reviews in, ranked cards out.

    python -m tools.triage --csv data/reviews.synthetic.csv --top 3

Writes data/out/clusters.json (for the agents and tools) and data/out/cards.md
(what the triage agent posts), and prints the cards.
"""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

from tools.cards import Card, render
from tools.cluster import cluster_reviews
from tools.ingest import load_reviews
from tools.score import severity


def build_cards(reviews, as_of: date, top: int, max_stars: int = 3) -> list[Card]:
    """Cluster complaints (reviews at or below `max_stars`) and rank them by severity."""
    complaints = [r for r in reviews if r.stars <= max_stars]
    scored = [(severity(c.members, as_of), c) for c in cluster_reviews(complaints)]
    scored.sort(key=lambda pair: (-pair[0], pair[1].terms))
    return [Card(f"CARD-{i}", i, score, c) for i, (score, c) in enumerate(scored[:top], start=1)]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--csv", required=True)
    parser.add_argument("--out", default="data/out")
    parser.add_argument("--top", type=int, default=3)
    parser.add_argument("--max-stars", type=int, default=3, help="only reviews at or below this rating are triaged")
    parser.add_argument("--as-of", type=date.fromisoformat, help="scoring date (default: newest review)")
    args = parser.parse_args(argv)

    reviews = load_reviews(args.csv)
    if not reviews:
        parser.error(f"no reviews with text in {args.csv}")
    as_of = args.as_of or max(r.submitted for r in reviews)
    cards = build_cards(reviews, as_of, args.top, args.max_stars)

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    payload = {
        "as_of": as_of.isoformat(),
        "reviews_read": len(reviews),
        "cards": [
            {
                "card_id": card.card_id,
                "severity": card.severity,
                "terms": list(card.cluster.terms),
                "review_ids": [r.review_id for r in card.cluster.members],
            }
            for card in cards
        ],
    }
    (out / "clusters.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    text = "\n\n".join(render(card) for card in cards)
    (out / "cards.md").write_text(text + "\n")
    print(f"{len(reviews)} reviews · {len(cards)} cards (as of {as_of})\n")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
