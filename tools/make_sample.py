"""Generate the synthetic review set (fixed seed, so the file is reproducible).

The reviews are written by us and labelled synthetic. They describe the three
seeded bugs in release-room-demo-app, plus unrelated noise.

    python -m tools.make_sample --out data/reviews.synthetic.csv
"""

from __future__ import annotations

import argparse
import csv
import io
import random
from datetime import date, timedelta
from pathlib import Path

APP = "Keepary"
AS_OF = date(2026, 11, 6)

# label -> (review texts, star range, versions with weights, count)
GROUPS: dict[str, tuple[list[str], tuple[int, int], dict[str, int], int]] = {
    "B1": (
        [
            "App crashes when I scan a receipt without a date",
            "Crashes every time I scan an old receipt with no date on it",
            "Scanned a receipt that has no date and the app crashed",
            "Keeps crashing on receipts that don't show a date",
            "App crash ho jata hai jab receipt pe date nahi hoti",
            "Receipt without a printed date makes the app crash instantly",
            "Crash on scan if the receipt date is missing. Very annoying",
            "Petrol pump receipt has no date and the app crashes every time",
        ],
        (1, 2),
        {"1.4.1": 4, "1.4.0": 1},
        22,
    ),
    "B2": (
        [
            "Amounts show as 100,000 instead of 1,00,000. Please use lakh format",
            "Indian number format is wrong, it shows 250,000 not 2,50,000",
            "Please use the lakh format for amounts like every Indian app",
            "Comma in the wrong place in amounts, lakh format is wrong",
            "Amount format galat hai, 1,00,000 likha hona chahiye lakh format mein",
            "Big amounts are hard to read, use Indian lakh format please",
            "Expense amounts use western commas, I want lakh format",
        ],
        (2, 3),
        {"1.4.1": 3, "1.4.0": 2},
        18,
    ),
    "B3": (
        [
            "Hindi bills don't read the total",
            "Total is blank for bills printed in Hindi",
            "Bills with Hindi numbers, the total is not detected",
            "Hindi bill ka total nahi padhta, khali aata hai",
            "Kirana bill in Hindi, total amount not read at all",
            "Total stays empty when the bill is in Hindi",
        ],
        (1, 3),
        {"1.4.1": 1},
        14,
    ),
    "noise": (
        [
            "Love this app, very useful for tracking my expenses",
            "Please add a dark mode",
            "Sync with Google Drive would be great",
            "Works perfectly on my phone, thank you",
            "Can you add export to Excel",
            "Ads are too frequent",
            "Nice simple design",
            "Would like a widget on the home screen",
            "Best receipt app I have used",
            "Please support multiple currencies for travel",
            "Login with phone number please",
            "Good app but the icon could be better",
        ],
        (3, 5),
        {"1.4.1": 3, "1.4.0": 2},
        12,
    ),
}

FIELDS = ["app", "version", "language", "submitted", "stars", "title", "text"]


def generate(seed: int = 42) -> tuple[list[dict[str, str]], list[str]]:
    """Return (rows, labels). Labels are kept out of the CSV; tests use them."""
    rng = random.Random(seed)
    rows: list[dict[str, str]] = []
    labels: list[str] = []
    for label, (texts, (lo, hi), versions, count) in GROUPS.items():
        version_pool = [v for v, w in versions.items() for _ in range(w)]
        for i in range(count):
            text = texts[i % len(texts)] if label == "noise" else rng.choice(texts)
            submitted = AS_OF - timedelta(days=rng.randint(0, 20), hours=rng.randint(0, 23))
            rows.append(
                {
                    "app": APP,
                    "version": rng.choice(version_pool),
                    "language": "hi" if any(w in text for w in (" hai", " nahi", " ka ", "galat")) else "en",
                    "submitted": f"{submitted.isoformat()}T{rng.randint(0, 23):02d}:{rng.randint(0, 59):02d}:00Z",
                    "stars": str(rng.randint(lo, hi)),
                    "title": "",
                    "text": text,
                }
            )
            labels.append(label)
    order = list(range(len(rows)))
    rng.shuffle(order)
    return [rows[i] for i in order], [labels[i] for i in order]


def to_csv(rows: list[dict[str, str]]) -> str:
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", default="data/reviews.synthetic.csv")
    args = parser.parse_args(argv)
    rows, _ = generate()
    Path(args.out).write_text(to_csv(rows), encoding="utf-8")
    print(f"wrote {len(rows)} synthetic reviews to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
