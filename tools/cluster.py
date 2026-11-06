"""Group reviews about the same problem. Deterministic: same input, same clusters."""

from __future__ import annotations

import re
from dataclasses import dataclass

import numpy as np
from sklearn.cluster import AgglomerativeClustering
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer

from tools.ingest import Review

# Common Hinglish function words, so clusters form around content words.
HINGLISH_STOP_WORDS = {
    "aur", "bhai", "bhi", "hai", "hain", "hi", "ho", "hota", "hoti", "jab", "jata",
    "jati", "ka", "kar", "ke", "ki", "ko", "kya", "me", "mein", "nahi", "nhi", "pe",
    "par", "raha", "rahi", "se", "woh", "ye", "yeh",
}
# Review filler: words that appear in every kind of complaint, plus contraction
# fragments the tokenizer leaves behind ("don't" -> "don").
REVIEW_STOP_WORDS = {
    "app", "please", "every", "time", "like", "use", "very", "keeps",
    "don", "doesn", "didn", "isn", "won", "t", "s",
}
STOP_WORDS = sorted(ENGLISH_STOP_WORDS | HINGLISH_STOP_WORDS | REVIEW_STOP_WORDS)


@dataclass(frozen=True)
class Cluster:
    members: tuple[Review, ...]  # ordered: most representative first
    terms: tuple[str, ...]       # top terms, for the card title


def _preprocess(text: str) -> str:
    # Digits ("100,000", "1.4.1") carry no topic signal and split clusters.
    return re.sub(r"\d+", " ", text.lower())


def cluster_reviews(
    reviews: list[Review], distance_threshold: float = 0.9, min_size: int = 3
) -> list[Cluster]:
    """Return clusters with at least `min_size` reviews, largest first."""
    if len(reviews) < 2:
        return []
    vectorizer = TfidfVectorizer(
        preprocessor=_preprocess,
        stop_words=STOP_WORDS,
        ngram_range=(1, 2),
        sublinear_tf=True,
        min_df=2,
    )
    matrix = vectorizer.fit_transform([r.text for r in reviews]).toarray()
    has_terms = np.flatnonzero(matrix.sum(axis=1) > 0)
    if len(has_terms) < 2:
        return []

    labels = AgglomerativeClustering(
        n_clusters=None,
        distance_threshold=distance_threshold,
        metric="cosine",
        linkage="average",
    ).fit_predict(matrix[has_terms])

    vocab = vectorizer.get_feature_names_out()
    clusters: list[Cluster] = []
    for label in sorted(set(labels)):
        rows = has_terms[labels == label]
        if len(rows) < min_size:
            continue
        vectors = matrix[rows]
        centroid = vectors.mean(axis=0)
        norms = np.linalg.norm(vectors, axis=1) * (np.linalg.norm(centroid) or 1.0)
        similarity = vectors @ centroid / np.where(norms == 0, 1.0, norms)
        order = [int(rows[i]) for i in np.argsort(-similarity, kind="stable")]
        top_terms = [str(vocab[i]) for i in np.argsort(-centroid, kind="stable")[:3]]
        clusters.append(Cluster(tuple(reviews[i] for i in order), tuple(top_terms)))

    clusters.sort(key=lambda c: (-len(c.members), c.terms))
    return clusters
