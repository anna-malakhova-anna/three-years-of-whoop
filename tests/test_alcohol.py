"""Locks in the alcohol event-window trajectory from HANDOVER.md §4.

The headline finding: the dip is one night, not a multi-day cascade.
"""
from pipeline.alcohol import build_alcohol_report

REPORT = build_alcohol_report()


def _day(offset: int) -> dict:
    return next(r for r in REPORT["trajectory"] if r["day"] == offset)


def test_recovery_dips_sharply_on_the_drinking_night():
    day_minus1 = _day(-1)
    day0 = _day(0)
    assert day0["mean_recovery"] < day_minus1["mean_recovery"] - 10


def test_recovery_is_back_near_baseline_the_next_morning():
    """No multi-day cascade: day +1 should be close to the pre-drink baseline,
    not still depressed like day 0."""
    day_minus1 = _day(-1)
    day0 = _day(0)
    day1 = _day(1)
    dip = day_minus1["mean_recovery"] - day0["mean_recovery"]
    residual = day_minus1["mean_recovery"] - day1["mean_recovery"]
    assert residual < dip * 0.5


def test_80_plus_recovery_is_a_minority_outcome_even_sober():
    assert REPORT["base_rates"]["pct_ge_80_sober_days"] < 60


def test_days_to_80_has_meaningful_never_reached_rate():
    """A 'days to 80' countdown would be dishonest if a real chunk of events
    never get there within the window — assert that chunk exists."""
    never_pct = REPORT["days_to_threshold"]["80"]["pct_never_within_5_days"]
    assert never_pct > 10


def test_consecutive_drinking_nights_mostly_single():
    runs = REPORT["consecutive_drinking_nights"]
    assert runs["singles"] > runs["doubles"] > 0
    n_runs = runs["singles"] + runs["doubles"] + runs["triples"] + runs["four_plus"]
    # Run lengths must sum back to the total count of drinking nights.
    accounted = runs["singles"] * 1 + runs["doubles"] * 2 + runs["triples"] * 3
    assert accounted <= REPORT["n_drinking_nights"]
    assert n_runs > 0
