import json

import pytest

from tools.replies import MAX_CHARS, check_reply, draft_reply, main


def test_reply_mentions_fix_and_version():
    reply = draft_reply("Scanning a receipt without a date no longer crashes.", "1.4.2")
    assert "no longer crashes" in reply
    assert "1.4.2" in reply
    assert len(reply) <= MAX_CHARS


def test_too_long_reply_is_rejected():
    with pytest.raises(ValueError, match="350"):
        draft_reply("x" * 400, "1.4.2")


def test_reply_with_contact_details_is_rejected():
    with pytest.raises(ValueError, match="email or phone"):
        check_reply("Write to us at help@example.com")


def test_cli_writes_drafts_for_every_review_in_the_card(tmp_path, capsys):
    clusters = tmp_path / "clusters.json"
    clusters.write_text(json.dumps({"cards": [{"card_id": "CARD-1", "review_ids": ["R-aaa111", "R-bbb222"]}]}))
    assert main(["--card", "CARD-1", "--version", "1.4.2", "--summary", "Fixed the crash",
                 "--clusters", str(clusters), "--out", str(tmp_path)]) == 0
    text = (tmp_path / "replies-CARD-1.md").read_text()
    assert "- R-aaa111" in text and "- R-bbb222" in text
    capsys.readouterr()


def test_cli_rejects_unknown_card(tmp_path):
    clusters = tmp_path / "clusters.json"
    clusters.write_text(json.dumps({"cards": []}))
    with pytest.raises(SystemExit):
        main(["--card", "CARD-9", "--version", "1", "--summary", "x", "--clusters", str(clusters), "--out", str(tmp_path)])
