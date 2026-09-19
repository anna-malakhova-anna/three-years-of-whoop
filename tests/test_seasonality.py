"""Locks in the seasonality check against HANDOVER.md §5's claim.

The claim: month-to-month HRV swings look noisy, not seasonal. These tests
assert both halves of that — a real (significant) monthly effect exists,
but it doesn't trace a smooth annual curve.
"""
from pipeline.seasonality import build_seasonality_report

REPORT = build_seasonality_report()


def test_all_twelve_months_present_with_a_readable_sample():
    months = [m["month"] for m in REPORT["monthly"]]
    assert months == ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    for m in REPORT["monthly"]:
        assert m["hrv_n"] >= 40


def test_monthly_anova_is_significant_but_small():
    anova = REPORT["anova"]
    assert anova["hrv_p"] < 0.01
    # Small effect size — significance here is a large-n artifact, not a
    # strong seasonal driver. If eta^2 climbs well past this, the "small
    # effect" framing in the UI copy needs to change too.
    assert anova["hrv_eta_squared"] < 0.15


def test_annual_sine_curve_does_not_fit():
    """A real seasonal effect should trace a smooth annual cycle. Assert it
    doesn't — R^2 stays low and the sine term isn't independently significant."""
    fit = REPORT["annual_cycle_fit"]
    assert fit["r_squared"] < 0.05
    assert fit["sin_p"] > 0.05


def test_april_to_june_zigzag_matches_handover():
    """The specific anomaly HANDOVER.md §5 calls out: April high, May drops
    sharply, June rebounds — not a monotonic seasonal slide."""
    by_month = {m["month"]: m["hrv_mean"] for m in REPORT["monthly"]}
    assert by_month["May"] < by_month["Apr"]
    assert by_month["Jun"] > by_month["May"]


def test_best_and_worst_month_are_internally_consistent():
    months = {m["month"]: m["hrv_mean"] for m in REPORT["monthly"]}
    assert REPORT["best_month"]["hrv_mean"] == max(months.values())
    assert REPORT["worst_month"]["hrv_mean"] == min(months.values())


def test_sleep_hours_has_a_reading_every_month():
    for m in REPORT["monthly"]:
        assert m["sleep_hours_mean"] is not None
        assert 4 < m["sleep_hours_mean"] < 12


def test_sleep_hours_anova_is_significant_but_small():
    """Same shape as HRV: real, but not a meaningful seasonal swing."""
    anova = REPORT["anova"]
    assert anova["sleep_hours_p"] < 0.05
    assert anova["sleep_hours_eta_squared"] < 0.15


def test_workout_logging_rate_does_not_vary_by_month():
    """Whether a workout got logged at all should show no monthly pattern —
    if a future data refresh makes this significant, the "no seasonal
    training pattern" copy in the UI needs to change too."""
    assert REPORT["workout_chi_square"]["p"] > 0.05


def test_workout_pct_is_a_real_percentage_every_month():
    for m in REPORT["monthly"]:
        assert m["workout_pct"] is not None
        assert 0 <= m["workout_pct"] <= 100
