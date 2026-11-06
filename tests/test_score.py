from datetime import date, timedelta

from tools.ingest import Review
from tools.score import severity

TODAY = date(2026, 11, 6)


def _review(stars: int, days_ago: int) -> Review:
    return Review("R-x", "Keepary", "1.4.1", "en", TODAY - timedelta(days=days_ago), stars, "text")


def test_empty_cluster_scores_zero():
    assert severity([], TODAY) == 0.0


def test_fresh_one_star_reviews():
    assert severity([_review(1, 0)] * 4, TODAY) == 20.0  # 4 × (6 − 1) × 1


def test_unhappier_scores_higher():
    assert severity([_review(1, 0)] * 3, TODAY) > severity([_review(3, 0)] * 3, TODAY)


def test_more_reviews_score_higher():
    assert severity([_review(2, 0)] * 6, TODAY) > severity([_review(2, 0)] * 3, TODAY)


def test_older_reviews_decay_by_half_life():
    assert severity([_review(1, 14)], TODAY) == 2.5  # 1 × 5 × 0.5


def test_future_dates_do_not_inflate():
    assert severity([_review(1, -5)], TODAY) == 5.0
