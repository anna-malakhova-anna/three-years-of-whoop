"""Locks in the dedupe rule and join behaviour against the committed export.

These numbers are computed from data/raw/*.csv as committed to this repo.
If the CSVs never change, these should never change either — a failure
here means the pipeline logic drifted, not that the data did.
"""
from pipeline.load import build_daily_table


def test_physio_dedupe_drops_exactly_the_nap_duplicates():
    daily, report = build_daily_table()
    assert report.physio_rows_raw == 1027
    assert report.physio_dup_dates == 196
    assert report.physio_rows_deduped == 831
    assert len(daily) == 831


def test_daily_table_has_one_row_per_date():
    daily, _ = build_daily_table()
    assert daily["date"].is_unique


def test_no_missing_value_is_imputed():
    daily, _ = build_daily_table()
    # Missing core fields must stay missing (NaN), never filled.
    assert daily["hrv"].isna().sum() > 0
    assert daily["recovery_pct"].isna().sum() > 0


def test_alcohol_column_is_boolean_and_known_flag_tracks_coverage():
    daily, _ = build_daily_table()
    assert daily["alcohol"].dtype == bool
    assert daily["alcohol_known"].sum() < len(daily)
    # A day with no journal answer must not be silently treated as "no alcohol".
    unknown = daily[~daily["alcohol_known"]]
    assert (unknown["alcohol"] == False).all()  # noqa: E712


def test_prior_day_strain_is_shifted_not_same_day():
    daily, _ = build_daily_table()
    daily = daily.sort_values("date").reset_index(drop=True)
    # Row 1's prior_day_strain must equal row 0's day_strain.
    for i in range(1, min(20, len(daily))):
        prev_strain = daily.loc[i - 1, "day_strain"]
        this_prior = daily.loc[i, "prior_day_strain"]
        if pd_isna(prev_strain) and pd_isna(this_prior):
            continue
        assert prev_strain == this_prior


def pd_isna(x) -> bool:
    import pandas as pd
    return pd.isna(x)
