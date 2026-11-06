"""Draft replies to the users behind a card, after its fix ships.

Drafts only: a human approves them in the room before anything is posted.
Google Play limits developer replies to 350 characters.

    python -m tools.replies --card CARD-1 --version 1.4.2 \
        --summary "Scanning a receipt without a date no longer crashes"
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from tools.ingest import mask_pii

MAX_CHARS = 350
TEMPLATE = (
    "Thanks for reporting this. {summary}. The fix is in Keepary {version}. "
    "Please update, and reply here if it still happens."
)


def draft_reply(summary: str, version: str) -> str:
    reply = TEMPLATE.format(summary=summary.strip().rstrip("."), version=version.strip())
    check_reply(reply)
    return reply


def check_reply(reply: str) -> None:
    if len(reply) > MAX_CHARS:
        raise ValueError(f"reply is {len(reply)} characters; Play allows {MAX_CHARS}")
    if mask_pii(reply) != reply:
        raise ValueError("reply contains an email or phone number")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--card", required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--summary", required=True, help="one sentence: what is fixed")
    parser.add_argument("--clusters", default="data/out/clusters.json")
    parser.add_argument("--out", default="data/out")
    args = parser.parse_args(argv)

    cards = {c["card_id"]: c for c in json.loads(Path(args.clusters).read_text())["cards"]}
    if args.card not in cards:
        parser.error(f"unknown card {args.card}; run `make triage` first")
    reply = draft_reply(args.summary, args.version)
    review_ids = cards[args.card]["review_ids"]

    lines = [f"## Reply drafts for {args.card} ({len(review_ids)} reviews)", "", reply, "", "Send to:"]
    lines += [f"- {rid}" for rid in review_ids]
    out = Path(args.out) / f"replies-{args.card}.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
