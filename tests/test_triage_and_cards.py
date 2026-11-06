import json

from tools import triage
from tools.cards import MAX_LINES
from tools.make_sample import generate, to_csv


def _run(tmp_path, capsys, *extra):
    csv_path = tmp_path / "reviews.csv"
    rows, _ = generate()
    csv_path.write_text(to_csv(rows), encoding="utf-8")
    out = tmp_path / "out"
    assert triage.main(["--csv", str(csv_path), "--out", str(out), *extra]) == 0
    capsys.readouterr()
    return json.loads((out / "clusters.json").read_text()), (out / "cards.md").read_text()


def test_triage_writes_three_ranked_cards(tmp_path, capsys):
    payload, cards = _run(tmp_path, capsys)
    ids = [c["card_id"] for c in payload["cards"]]
    assert ids == ["CARD-1", "CARD-2", "CARD-3"]
    scores = [c["severity"] for c in payload["cards"]]
    assert scores == sorted(scores, reverse=True)
    assert all(f"{i} ·" in cards for i in ids)


def test_crash_cluster_ranks_first(tmp_path, capsys):
    payload, _ = _run(tmp_path, capsys)
    assert {"date", "receipt"} & set(payload["cards"][0]["terms"])


def test_cards_fit_in_eight_lines(tmp_path, capsys):
    _, cards = _run(tmp_path, capsys)
    for card in cards.strip().split("\n\n"):
        assert len(card.splitlines()) <= MAX_LINES


def test_cards_do_not_repeat_a_quote(tmp_path, capsys):
    _, cards = _run(tmp_path, capsys)
    for card in cards.strip().split("\n\n"):
        quote_line = card.splitlines()[2]
        quotes = [q for q in quote_line.split(" · ")]
        assert len(quotes) == len(set(quotes))


def test_top_limits_card_count(tmp_path, capsys):
    payload, _ = _run(tmp_path, capsys, "--top", "1")
    assert len(payload["cards"]) == 1


def test_output_is_reproducible(tmp_path, capsys):
    first, _ = _run(tmp_path, capsys)
    second, _ = _run(tmp_path, capsys)
    assert first == second
