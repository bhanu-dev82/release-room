from collections import Counter

from tools.cluster import cluster_reviews
from tools.ingest import parse_reviews
from tools.make_sample import generate, to_csv


def _labelled_complaints():
    rows, labels = generate()
    reviews = parse_reviews(to_csv(rows))
    return [(r, l) for r, l in zip(reviews, labels) if r.stars <= 3]


def test_sample_complaints_form_exactly_the_three_bug_clusters():
    pairs = _labelled_complaints()
    label_of = {r.review_id: l for r, l in pairs}
    clusters = cluster_reviews([r for r, _ in pairs])
    majority = [Counter(label_of[r.review_id] for r in c.members).most_common(1)[0][0] for c in clusters]
    assert sorted(majority) == ["B1", "B2", "B3"]


def test_clusters_are_pure():
    pairs = _labelled_complaints()
    label_of = {r.review_id: l for r, l in pairs}
    for c in cluster_reviews([r for r, _ in pairs]):
        labels = Counter(label_of[r.review_id] for r in c.members)
        assert labels.most_common(1)[0][1] / len(c.members) >= 0.9, labels


def test_clustering_is_deterministic():
    reviews = [r for r, _ in _labelled_complaints()]
    first = [[m.review_id for m in c.members] for c in cluster_reviews(reviews)]
    second = [[m.review_id for m in c.members] for c in cluster_reviews(reviews)]
    assert first == second


def test_small_groups_are_dropped():
    rows, _ = generate()
    reviews = parse_reviews(to_csv(rows))[:2]
    assert cluster_reviews(reviews) == []
