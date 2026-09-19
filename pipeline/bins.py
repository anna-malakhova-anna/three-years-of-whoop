"""Binned lookup tables for slider stops and workout comparisons → public/data/bins.json.

Sleep, respiratory rate, prior-day strain and sleep consistency are all
binned on **sober nights only** (alcohol is such a large confound that
mixing it into these bins would blur the sleep-dose relationship the
sliders are meant to show). Workout type is deliberately *not*
alcohol-filtered — it's presented as correlational, not causal, and
filtering it would just shrink already-thin per-activity samples further.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from pipeline.load import build_daily_table

OUT_DIR = Path(__file__).resolve().parent.parent / "public" / "data"

MIN_WORKOUT_N = 20


def _bin_stats(df: pd.DataFrame, col: str, edges: list[float], labels: list[str]) -> list[dict]:
    sub = df[[col, "hrv", "recovery_pct"]].dropna(subset=[col])
    sub = sub.copy()
    sub["bin"] = pd.cut(sub[col], bins=edges, labels=labels, right=True, include_lowest=True)
    rows = []
    for label in labels:
        cell = sub[sub["bin"] == label]
        n = len(cell)
        has_hrv = cell["hrv"].notna().sum()
        rows.append({
            "bin": label,
            "n": int(n),
            "mean_hrv": round(float(cell["hrv"].mean()), 1) if has_hrv else None,
            "mean_recovery": round(float(cell["recovery_pct"].mean()), 1) if cell["recovery_pct"].notna().any() else None,
            "pct_recovery_ge_80": round(100 * (cell["recovery_pct"] >= 80).mean(), 1) if cell["recovery_pct"].notna().any() else None,
        })
    return rows


def build_bins_report() -> dict:
    daily, _ = build_daily_table()
    sober = daily[daily["alcohol_known"] & ~daily["alcohol"]]

    sleep_edges = [0, 5, 6, 6.5, 7, 7.5, 8, 8.5, 9, 100]
    sleep_labels = ["<=5h", "5-6h", "6-6.5h", "6.5-7h", "7-7.5h", "7.5-8h", "8-8.5h", "8.5-9h", "9h+"]

    resp_edges = [0, 15.0, 15.5, 16.0, 17.0, 100]
    resp_labels = ["<=15.0", "15-15.5", "15.5-16", "16-17", ">17"]

    strain_edges = [-1, 6, 9, 12, 15, 100]
    strain_labels = ["0-6", "6-9", "9-12", "12-15", "15+"]

    consistency_edges = [0, 50, 60, 70, 80, 90, 100]
    consistency_labels = ["<50", "50-60", "60-70", "70-80", "80-90", "90-100"]

    # --- Workout type -> next day's HRV ---
    activity_counts = daily["prior_day_activity"].value_counts()
    valid_activities = activity_counts[activity_counts >= MIN_WORKOUT_N].index.tolist()
    rest_day_mask = daily["prior_day_activity"].isna()
    rest_hrv = daily.loc[rest_day_mask, "hrv"]

    workouts = []
    for activity in valid_activities:
        cell = daily.loc[daily["prior_day_activity"] == activity, "hrv"]
        n = cell.notna().sum()
        workouts.append({
            "activity": activity,
            "n": int(n),
            "mean_next_day_hrv": round(float(cell.mean()), 1) if n else None,
        })
    workouts.append({
        "activity": "Rest day",
        "n": int(rest_hrv.notna().sum()),
        "mean_next_day_hrv": round(float(rest_hrv.mean()), 1) if rest_hrv.notna().any() else None,
    })
    workouts.sort(key=lambda r: -(r["mean_next_day_hrv"] or 0))
    baseline_hrv = round(float(daily["hrv"].mean()), 1)

    return {
        "sleep_hours_sober": _bin_stats(sober, "sleep_hours", sleep_edges, sleep_labels),
        "resp_rate_sober": _bin_stats(sober, "resp_rate", resp_edges, resp_labels),
        "prior_day_strain_sober": _bin_stats(sober, "prior_day_strain", strain_edges, strain_labels),
        "sleep_consistency_sober": _bin_stats(sober, "sleep_consistency_pct", consistency_edges, consistency_labels),
        "workout_next_day_hrv": {
            "baseline_all_days_hrv": baseline_hrv,
            "min_n": MIN_WORKOUT_N,
            "activities": workouts,
            "note": "Correlational, not causal — a day is more likely to be a hard "
                     "workout day if the prior night already recovered well.",
        },
    }


def main() -> None:
    report = build_bins_report()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUT_DIR / "bins.json", "w") as f:
        json.dump(report, f, indent=2)
    print(f"wrote {OUT_DIR / 'bins.json'}")


if __name__ == "__main__":
    main()
