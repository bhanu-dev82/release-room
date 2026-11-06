"""Read a Play Console review export (or the simple sample CSV) into normalised reviews.

Reviewer identities never leave this module. The output has no name column,
emails and phone numbers in review text are masked, and each review gets a
short stable id derived from its content.
"""

from __future__ import annotations

import csv
import hashlib
import io
import re
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

# Our field -> accepted column names (Play Console export first, then sample CSV).
COLUMNS = {
    "app": ("Package Name", "app"),
    "version": ("App Version Name", "version"),
    "language": ("Reviewer Language", "language"),
    "submitted": ("Review Submit Date and Time", "submitted"),
    "stars": ("Star Rating", "stars"),
    "title": ("Review Title", "title"),
    "text": ("Review Text", "text"),
}

_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
_PHONE = re.compile(r"(?<!\d)(?:\+?91[\s-]?)?[6-9]\d{9}(?!\d)")


@dataclass(frozen=True)
class Review:
    review_id: str
    app: str
    version: str
    language: str
    submitted: date
    stars: int
    text: str


def mask_pii(text: str) -> str:
    """Replace emails and Indian mobile numbers with placeholders."""
    return _PHONE.sub("[phone]", _EMAIL.sub("[email]", text))


def _decode(raw: bytes) -> str:
    # Play Console exports have historically been UTF-16; the sample CSV is UTF-8.
    if raw.startswith((b"\xff\xfe", b"\xfe\xff")):
        return raw.decode("utf-16")
    return raw.decode("utf-8-sig")


def _pick(row: dict[str, str], field: str) -> str:
    for name in COLUMNS[field]:
        if name in row and row[name] is not None:
            return row[name].strip()
    return ""


def _parse_date(value: str) -> date:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).date()


def review_id(app: str, submitted: date, text: str) -> str:
    digest = hashlib.sha1(f"{app}|{submitted.isoformat()}|{text}".encode()).hexdigest()
    return f"R-{digest[:6]}"


def parse_reviews(csv_text: str) -> list[Review]:
    """Parse CSV text into reviews. Rating-only rows (no text) are skipped."""
    reviews: list[Review] = []
    for row in csv.DictReader(io.StringIO(csv_text)):
        body = " ".join(p for p in (_pick(row, "title"), _pick(row, "text")) if p)
        if not body:
            continue
        text = mask_pii(body)
        app = _pick(row, "app")
        submitted = _parse_date(_pick(row, "submitted"))
        reviews.append(
            Review(
                review_id=review_id(app, submitted, text),
                app=app,
                version=_pick(row, "version"),
                language=_pick(row, "language"),
                submitted=submitted,
                stars=int(_pick(row, "stars")),
                text=text,
            )
        )
    return reviews


def load_reviews(path: str | Path) -> list[Review]:
    return parse_reviews(_decode(Path(path).read_bytes()))
