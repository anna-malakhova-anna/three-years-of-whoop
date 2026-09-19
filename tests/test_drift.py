"""Locks in the August 2025 vs August 2026 drift comparison."""
from pipeline.drift import build_drift_report

REPORT = build_drift_report()


def _metric(key: str) -> dict:
    return next(m for m in REPORT["metrics"] if m["key"] == key)


def test_periods_are_the_requested_months():
    assert REPORT["period_a"] == "2025-08"
    assert REPORT["period_b"] == "2026-08"


def test_every_metric_has_a_readable_sample_both_months():
    for m in REPORT["metrics"]:
        assert m["a_n"] >= 20
        assert m["b_n"] >= 20


def test_hrv_and_recovery_move_in_the_same_direction():
    hrv = _metric("hrv")
    recovery = _metric("recovery_pct")
    assert hrv["delta"] > 0
    assert recovery["delta"] > 0


def test_rhr_moves_opposite_to_hrv():
    """Lower RHR alongside higher HRV is the internally consistent direction
    — the two shouldn't independently improve/worsen at random."""
    rhr = _metric("rhr")
    assert rhr["delta"] < 0


def test_no_metric_claims_significance_it_does_not_have():
    """None of these should be reported as p<0.05 — if a future data refresh
    makes one significant, the UI's "suggestive, not established" framing
    needs to change too, so this should fail loudly rather than silently
    drift out of sync with the copy."""
    for m in REPORT["metrics"]:
        assert m["p"] is None or m["p"] >= 0.05


def test_alcohol_coverage_gap_in_earlier_month_is_visible():
    assert REPORT["alcohol"]["a_n_known"] == 0
    assert REPORT["alcohol"]["b_n_known"] > 0


def test_improved_flag_matches_each_metrics_own_good_direction():
    """HRV/recovery/sleep hours/sleep consistency: higher is improved.
    RHR/respiratory rate/day strain: lower is improved. Verifies the sign
    logic directly rather than trusting the pipeline's own arithmetic."""
    higher_is_better = ["hrv", "recovery_pct", "sleep_hours", "sleep_consistency_pct"]
    lower_is_better = ["rhr", "resp_rate", "day_strain"]
    for key in higher_is_better:
        m = _metric(key)
        assert m["improved"] == (m["delta"] > 0)
    for key in lower_is_better:
        m = _metric(key)
        assert m["improved"] == (m["delta"] < 0)


def test_respiratory_rate_is_the_one_metric_that_worsened():
    """Locks in the specific mixed result the UI needs to render both
    colors correctly — not all-green, not all-yellow."""
    assert _metric("resp_rate")["improved"] is False
    others = [m for m in REPORT["metrics"] if m["key"] != "resp_rate"]
    assert all(m["improved"] for m in others)
