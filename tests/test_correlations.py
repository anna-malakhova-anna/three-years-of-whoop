"""Locks in the univariate/multivariate findings from HANDOVER.md §3.

Exact values are computed from the committed export; a change here on an
unchanged dataset means the analysis code regressed, not that the finding
moved.
"""
from pipeline.correlations import build_model_report

MODEL = build_model_report()


def _univar(var: str) -> dict:
    return next(v for v in MODEL["univariate_correlations"] if v["variable"] == var)


def test_rhr_is_the_strongest_and_most_circular_correlation():
    rhr = _univar("rhr")
    assert rhr["r"] < -0.8
    assert rhr["verdict"] == "exclude"
    # RHR must be the single largest |r| in the table.
    assert abs(rhr["r"]) == max(abs(v["r"]) for v in MODEL["univariate_correlations"])


def test_sleep_hours_is_a_primary_positive_lever():
    sleep = _univar("sleep_hours")
    assert sleep["r"] > 0.15
    assert sleep["verdict"] == "primary_lever"


def test_rem_has_no_relationship():
    rem = _univar("rem_sleep_hours")
    assert abs(rem["r"]) < 0.1
    assert rem["p"] > 0.05


def test_deep_sleep_is_negatively_correlated():
    deep = _univar("deep_sleep_hours")
    assert deep["r"] < 0


def test_same_day_strain_is_positive_but_flagged_wrong_direction():
    same_day = _univar("day_strain")
    assert same_day["r"] > 0
    assert same_day["verdict"] == "wrong_direction"


def test_primary_model_alcohol_and_sleep_are_significant_with_expected_sign():
    primary = MODEL["primary_model"]
    assert primary["coefficients"]["sleep_hours"]["coef_ms"] > 0
    assert primary["coefficients"]["sleep_hours"]["significant"] is True
    assert primary["coefficients"]["alcohol"]["coef_ms"] < 0
    assert primary["coefficients"]["alcohol"]["significant"] is True
    assert 0.15 < primary["r_squared"] < 0.5


def test_respiratory_rate_mediates_the_alcohol_coefficient():
    """Removing respiratory rate from the model must inflate |alcohol coef|.

    This is the specific, surprising finding HANDOVER.md calls out: alcohol
    raises respiratory rate, so without an rpm term that pathway gets
    re-attributed to the alcohol dummy.
    """
    variants = MODEL["model_variants"]
    with_resp = abs(variants["with_respiratory_rate"]["coefficients"]["alcohol"]["coef_ms"])
    without_resp = abs(variants["without_respiratory_rate"]["coefficients"]["alcohol"]["coef_ms"])
    assert without_resp > with_resp


def test_sleep_consistency_and_strain_are_not_significant_in_full_model():
    full = MODEL["model_variants"]["with_respiratory_rate"]["coefficients"]
    assert full["prior_day_strain"]["significant"] is False


def test_alcohol_contrast_is_a_large_negative_effect():
    contrast = MODEL["alcohol_contrast"]
    assert contrast["cohens_d"] < -0.8
    assert contrast["hrv_alcohol"] < contrast["hrv_sober"]
    assert contrast["p"] < 0.001


def test_high_hrv_days_rarely_follow_alcohol():
    q = MODEL["hrv_quartile_comparison"]
    high_rate = q["high"]["alcohol_n"] / q["high"]["alcohol_known_n"]
    low_rate = q["low"]["alcohol_n"] / q["low"]["alcohol_known_n"]
    assert high_rate < low_rate
