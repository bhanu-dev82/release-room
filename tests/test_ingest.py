from datetime import date

from tools.ingest import load_reviews, mask_pii, parse_reviews

PLAY_HEADER = (
    "Package Name,App Version Code,App Version Name,Reviewer Language,Device,"
    "Review Submit Date and Time,Review Submit Millis Since Epoch,Star Rating,Review Title,Review Text\n"
)


def test_reads_play_console_columns():
    csv_text = PLAY_HEADER + "com.keepary,141,1.4.1,en,pixel,2026-11-05T10:00:00Z,0,1,,App crashes on scan\n"
    [review] = parse_reviews(csv_text)
    assert review.app == "com.keepary"
    assert review.version == "1.4.1"
    assert review.stars == 1
    assert review.submitted == date(2026, 11, 5)
    assert review.text == "App crashes on scan"


def test_title_and_text_are_joined():
    csv_text = PLAY_HEADER + "com.keepary,141,1.4.1,en,pixel,2026-11-05T10:00:00Z,0,2,Broken,Total missing\n"
    assert parse_reviews(csv_text)[0].text == "Broken Total missing"


def test_rating_only_rows_are_skipped():
    csv_text = PLAY_HEADER + "com.keepary,141,1.4.1,en,pixel,2026-11-05T10:00:00Z,0,5,,\n"
    assert parse_reviews(csv_text) == []


def test_output_has_no_reviewer_identity():
    csv_text = "app,version,language,submitted,stars,title,text,Reviewer Name\n" \
               "Keepary,1.4.1,en,2026-11-05T10:00:00Z,1,,crash,Asha Rao\n"
    review = parse_reviews(csv_text)[0]
    assert "Asha" not in repr(review)
    assert review.review_id.startswith("R-")


def test_mask_pii_hides_email_and_mobile():
    assert mask_pii("mail me at asha.r@example.com") == "mail me at [email]"
    assert mask_pii("call 9876543210 or +91 9876543210") == "call [phone] or [phone]"
    assert mask_pii("total 1,00,000 on 2026-11-05") == "total 1,00,000 on 2026-11-05"


def test_review_id_is_stable():
    csv_text = "app,version,language,submitted,stars,title,text\nKeepary,1.4.1,en,2026-11-05T10:00:00Z,1,,crash\n"
    assert parse_reviews(csv_text)[0].review_id == parse_reviews(csv_text)[0].review_id


def test_utf16_export_is_decoded(tmp_path):
    path = tmp_path / "reviews.csv"
    path.write_bytes((PLAY_HEADER + "com.keepary,141,1.4.1,hi,pixel,2026-11-05T10:00:00Z,0,1,,कुल नहीं दिखता\n").encode("utf-16"))
    assert load_reviews(path)[0].text == "कुल नहीं दिखता"
