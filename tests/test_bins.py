from pipeline.bins import build_bins_report

BINS = build_bins_report()


def test_sleep_bins_cover_the_full_range_with_no_gaps():
    labels = [r["bin"] for r in BINS["sleep_hours_sober"]]
    assert labels == ["<=5h", "5-6h", "6-6.5h", "6.5-7h", "7-7.5h", "7.5-8h", "8-8.5h", "8.5-9h", "9h+"]


def test_sleep_returns_flatten_past_the_best_band():
    """The best HRV band should not be the longest-sleep band — this is
    what makes it a plateau rather than a straight line."""
    rows = {r["bin"]: r["mean_hrv"] for r in BINS["sleep_hours_sober"] if r["mean_hrv"] is not None}
    best_bin = max(rows, key=rows.get)
    assert best_bin != "9h+"


def test_workout_types_meet_the_minimum_n():
    for row in BINS["workout_next_day_hrv"]["activities"]:
        if row["activity"] != "Rest day":
            assert row["n"] >= BINS["workout_next_day_hrv"]["min_n"]


def test_respiratory_rate_high_bin_has_lowest_hrv():
    rows = {r["bin"]: r["mean_hrv"] for r in BINS["resp_rate_sober"] if r["mean_hrv"] is not None}
    assert rows[">17"] == min(rows.values())
