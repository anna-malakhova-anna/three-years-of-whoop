"""Coverage + completeness report → public/data/quality.json.

This is the honesty layer: the UI footer and the README's data-quality
section both read straight from this file. Nothing here is invented —
every number is a count over the joined daily table produced by load.py.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from pipeline.load import build_daily_table

OUT_DIR = Path(__file__).resolve().parent.parent / "public" / "data"

# Questions with enough "yes" answers to plausibly support a claim vs not.
# Threshold is judgment, not a magic number: below ~30 yes-answers a bin
# split further by another factor gets too thin to say anything with a
# straight face (see bins.py MIN_N).
INSUFFICIENT_DATA_THRESHOLD = 30


def build_quality_report() -> dict:
    daily, report = build_daily_table()

    n_days = len(daily)
    date_min = str(daily["date"].min())
    date_max = str(daily["date"].max())

    core_cols = {
        "recovery_pct": "Recovery score",
        "hrv": "HRV",
        "rhr": "Resting heart rate",
    }
    missing_core = {}
    for col, label in core_cols.items():
        n_missing = int(daily[col].isna().sum())
        missing_core[col] = {
            "label": label,
            "n_missing": n_missing,
            "pct_missing": round(100 * n_missing / n_days, 1),
        }

    missing_consistency = int(daily["sleep_consistency_pct"].isna().sum())
    missing_strain = int(daily["day_strain"].isna().sum())

    # Journal question coverage — this is what makes §2 gotcha 3 visible.
    question_cols = [c for c in daily.columns if c.endswith("?")]
    journal_questions = []
    for q in question_cols:
        answered = daily[q].notna()
        n_answered = int(answered.sum())
        n_yes = int(daily.loc[answered, q].sum())
        journal_questions.append({
            "question": q,
            "n_answered": n_answered,
            "n_yes": n_yes,
            "sufficient": n_yes >= INSUFFICIENT_DATA_THRESHOLD,
        })
    journal_questions.sort(key=lambda r: -r["n_yes"])

    # Journal coverage by year (alcohol question, since that's the one we use).
    alcohol_col = "Have any alcoholic drinks?"
    by_year = []
    if alcohol_col in daily.columns:
        years = pd.to_datetime(daily["date"]).dt.year
        for year in sorted(years.unique()):
            mask = years == year
            n = int(daily.loc[mask, alcohol_col].notna().sum())
            by_year.append({"year": int(year), "n_answered": n})

    quality = {
        "date_range": {"start": date_min, "end": date_max},
        "n_days_in_range": n_days,
        "dedupe": {
            "physio_rows_raw": report.physio_rows_raw,
            "physio_dup_dates_collapsed": report.physio_dup_dates,
            "physio_rows_after_dedupe": report.physio_rows_deduped,
            "rule": "Per date, keep the row with the highest Recovery score % "
                    "(non-null beats null). Naps create the duplicate cycles.",
        },
        "missing_core": missing_core,
        "missing_sleep_consistency": missing_consistency,
        "missing_day_strain": missing_strain,
        "journal": {
            "rows_raw": report.journal_rows_raw,
            "rows_no_date": report.journal_rows_no_date,
            "rows_not_matched_to_kept_cycle": report.journal_unmatched_to_cycle,
            "questions": journal_questions,
            "alcohol_coverage_by_year": by_year,
            "insufficient_data_threshold": INSUFFICIENT_DATA_THRESHOLD,
        },
        "notes": report.notes + [
            "Journal coverage is uneven across the export; do not treat a thin "
            "year as equivalent evidence to a well-covered one.",
            "No missing value in this pipeline is ever imputed. Rows missing a "
            "field are dropped from analyses that need that field, and the "
            "drop is counted here.",
        ],
    }
    return quality


def main() -> None:
    quality = build_quality_report()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUT_DIR / "quality.json", "w") as f:
        json.dump(quality, f, indent=2)
    print(f"wrote {OUT_DIR / 'quality.json'}")


if __name__ == "__main__":
    main()
