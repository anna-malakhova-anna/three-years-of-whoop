from pipeline.alcohol import build_alcohol_report
from pipeline.bins import build_bins_report
from pipeline.correlations import build_model_report
from pipeline.quality import build_quality_report
from pipeline.statements import build_statements, confidence_tier

MODEL = build_model_report()
ALCOHOL = build_alcohol_report()
BINS = build_bins_report()
QUALITY = build_quality_report()
RESULT = build_statements(MODEL, ALCOHOL, BINS, QUALITY)


def test_every_statement_has_n_and_confidence():
    for s in RESULT["statements"]:
        assert "n" in s and s["n"] is not None
        assert s["confidence"] in {"high", "medium", "low"}


def test_confidence_tier_boundaries():
    assert confidence_tier(150) == "high"
    assert confidence_tier(100) == "high"
    assert confidence_tier(99) == "medium"
    assert confidence_tier(30) == "medium"
    assert confidence_tier(29) == "low"
    assert confidence_tier(0) == "low"


def test_bins_under_10_are_forced_to_low_confidence():
    for s in RESULT["statements"]:
        if s.get("n", 999) < 10:
            assert s["confidence"] == "low"


def test_consistency_and_strain_statements_are_always_hedged_regardless_of_n():
    hedged_factors = {"prior_day_strain", "sleep_consistency_pct"}
    for s in RESULT["statements"]:
        if s["factor"] in hedged_factors and s.get("n", 0) >= 10:
            assert "loosely" in s["text"] or "hold this" in s["text"]


def test_caffeine_and_screens_and_reading_are_in_insufficient_data_not_statements():
    banned_terms = ["caffeine", "screen", "read in bed"]
    for s in RESULT["statements"]:
        for term in banned_terms:
            assert term not in s["text"].lower()
    insufficient_questions = {row["question"] for row in RESULT["insufficient_data"]}
    assert "Consumed caffeine?" in insufficient_questions
    assert "Viewed a screen device in bed?" in insufficient_questions
    assert "Read (non-screened device) while in bed?" in insufficient_questions


def test_signal_panel_has_rhr_and_respiratory_rate_only():
    ids = {p["id"] for p in RESULT["signal_panel"]}
    assert ids == {"signal_rhr", "signal_resp_rate"}
