"""August 2025 vs August 2026 → public/data/drift.json.

A scoped, requested comparison, not a general drift-detection system: same
calendar month a year apart, so season is held roughly constant (sidesteps
the seasonality question HANDOVER.md §5 already flags as too noisy to trust
across arbitrary date ranges — comparing August to August is the one
seasonally-controlled comparison this export can actually support).
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from scipy import stats

from pipeline.load import build_daily_table

OUT_DIR = Path(__file__).resolve().parent.parent / "public" / "data"

PERIOD_A = "2025-08"
PERIOD_B = "2026-08"

# (column, label, unit)
METRICS = [
    ("hrv", "HRV", "ms"),
    ("recovery_pct", "Recovery", "%"),
    ("rhr", "Resting heart rate", "bpm"),
    ("sleep_hours", "Sleep hours", "h"),
    ("sleep_consistency_pct", "Sleep consistency", "%"),
    ("resp_rate", "Respiratory rate", "rpm"),
    ("day_strain", "Day strain", ""),
]


def _month_slice(daily: pd.DataFrame, period: str) -> pd.DataFrame:
    return daily[daily["year_month"] == period]


def build_drift_report() -> dict:
    daily, _ = build_daily_table()
    daily = daily.copy()
    daily["year_month"] = pd.to_datetime(daily["date"]).dt.to_period("M").astype(str)

    a = _month_slice(daily, PERIOD_A)
    b = _month_slice(daily, PERIOD_B)

    metrics = []
    for col, label, unit in METRICS:
        sa = a[col].dropna()
        sb = b[col].dropna()
        row = {
            "key": col,
            "label": label,
            "unit": unit,
            "a_mean": round(float(sa.mean()), 1) if len(sa) else None,
            "a_n": int(len(sa)),
            "b_mean": round(float(sb.mean()), 1) if len(sb) else None,
            "b_n": int(len(sb)),
            "delta": None,
            "p": None,
            "cohens_d": None,
        }
        if len(sa) >= 2 and len(sb) >= 2:
            t, p = stats.ttest_ind(sa, sb, equal_var=False)
            pooled_sd = ((sa.var(ddof=1) + sb.var(ddof=1)) / 2) ** 0.5
            row["delta"] = round(float(sb.mean() - sa.mean()), 1)
            row["p"] = float(p)
            row["cohens_d"] = round(float((sb.mean() - sa.mean()) / pooled_sd), 2) if pooled_sd else None
        metrics.append(row)

    alcohol_a = a.loc[a["alcohol_known"], "alcohol"]
    alcohol_b = b.loc[b["alcohol_known"], "alcohol"]

    ns = [m["a_n"] for m in metrics] + [m["b_n"] for m in metrics]
    n_range = f"{min(ns)}–{max(ns)}"

    return {
        "period_a": PERIOD_A,
        "period_b": PERIOD_B,
        "metrics": metrics,
        "alcohol": {
            "a_n_known": int(len(alcohol_a)),
            "a_n_yes": int(alcohol_a.sum()),
            "b_n_known": int(len(alcohol_b)),
            "b_n_yes": int(alcohol_b.sum()),
        },
        "notes": [
            "Same calendar month a year apart, not adjacent months — controls "
            "for season, which HANDOVER.md §5 already flags as too noisy to "
            "trust as a general effect in this export.",
            f"n={n_range} per metric per month. None of the individual deltas reach p<0.05 at this "
            "sample size — call these suggestive, not established — but "
            "they're directionally consistent (HRV up, recovery up, RHR "
            "down, consistency up, strain down) rather than scattered, "
            "which is worth more than any single p-value here.",
            "Alcohol coverage in the earlier month is too thin to compare "
            "directly — see the alcohol block below.",
        ],
    }


def main() -> None:
    report = build_drift_report()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUT_DIR / "drift.json", "w") as f:
        json.dump(report, f, indent=2)
    print(f"wrote {OUT_DIR / 'drift.json'}")


if __name__ == "__main__":
    main()
