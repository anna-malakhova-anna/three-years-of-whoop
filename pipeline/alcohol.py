"""Event-window trajectory around drinking nights → public/data/alcohol.json.

Definitions (HANDOVER.md §4):
  - A "drinking night" is a date whose cycle has ``alcohol == True``. WHOOP
    attributes a cycle's recovery/HRV to the sleep that *ends* that
    morning, so day 0 in the trajectory below is the *same row* as the
    drinking night, not the next one — that row's recovery score already
    reflects the night of drinking.
  - "Days to reach a threshold" scans forward by calendar date from the
    drinking night (day 0) through day +5, and records the first day the
    recovery score is at or above the threshold. Events that never cross
    the threshold in that window are censored, not excluded — the % that
    never recovers within 5 days is itself a finding.
"""
from __future__ import annotations

import json
from datetime import timedelta
from pathlib import Path

import pandas as pd

from pipeline.load import build_daily_table

OUT_DIR = Path(__file__).resolve().parent.parent / "public" / "data"

OFFSETS = [-2, -1, 0, 1, 2, 3, 4]
THRESHOLDS = {"mean (67)": None, "sober_median (76)": None, "80": 80}  # filled in at runtime


def build_alcohol_report() -> dict:
    daily, _ = build_daily_table()
    daily = daily.set_index("date")
    by_date = daily[["recovery_pct", "hrv"]]

    drinking_dates = sorted(daily.index[daily["alcohol"] & daily["alcohol_known"]])

    # --- Trajectory ---
    trajectory = []
    for offset in OFFSETS:
        recoveries, hrvs = [], []
        for d in drinking_dates:
            target = d + timedelta(days=offset)
            if target in by_date.index:
                row = by_date.loc[target]
                if pd.notna(row["recovery_pct"]):
                    recoveries.append(row["recovery_pct"])
                if pd.notna(row["hrv"]):
                    hrvs.append(row["hrv"])
        n = len(recoveries)
        pct_ge_80 = round(100 * sum(1 for r in recoveries if r >= 80) / n, 1) if n else None
        trajectory.append({
            "day": offset,
            "n": n,
            "mean_recovery": round(sum(recoveries) / n, 1) if n else None,
            "mean_hrv": round(sum(hrvs) / len(hrvs), 1) if hrvs else None,
            "pct_ge_80": pct_ge_80,
        })

    # --- Base rate: recovery >= 80, sober days vs all days ---
    sober = daily[daily["alcohol_known"] & ~daily["alcohol"]]
    all_known = daily[daily["recovery_pct"].notna()]
    base_rates = {
        "pct_ge_80_sober_days": round(100 * (sober["recovery_pct"] >= 80).mean(), 1) if len(sober) else None,
        "pct_ge_80_all_days": round(100 * (all_known["recovery_pct"] >= 80).mean(), 1) if len(all_known) else None,
        "n_sober_days": int(len(sober)),
        "n_all_days": int(len(all_known)),
    }

    # --- Days to threshold ---
    sober_median_recovery = round(float(sober["recovery_pct"].median()), 0) if len(sober) else None
    mean_recovery = round(float(all_known["recovery_pct"].mean()), 0)
    thresholds = {
        "mean": mean_recovery,
        "sober_median": sober_median_recovery,
        "80": 80,
    }
    days_to_threshold = {}
    for label, thresh in thresholds.items():
        if thresh is None:
            continue
        days_taken = []
        n_never = 0
        for d in drinking_dates:
            found = None
            for offset in range(0, 6):
                target = d + timedelta(days=offset)
                if target in by_date.index and pd.notna(by_date.loc[target, "recovery_pct"]):
                    if by_date.loc[target, "recovery_pct"] >= thresh:
                        found = offset
                        break
            if found is None:
                n_never += 1
            else:
                days_taken.append(found)
        n_events = len(drinking_dates)
        days_to_threshold[label] = {
            "threshold_value": thresh,
            "median_days": (sorted(days_taken)[len(days_taken) // 2] if days_taken else None),
            "pct_never_within_5_days": round(100 * n_never / n_events, 1) if n_events else None,
            "n_events": n_events,
        }

    # --- Consecutive drinking-night run lengths ---
    run_lengths: list[int] = []
    if drinking_dates:
        current_run = 1
        for prev, cur in zip(drinking_dates, drinking_dates[1:]):
            if cur - prev == timedelta(days=1):
                current_run += 1
            else:
                run_lengths.append(current_run)
                current_run = 1
        run_lengths.append(current_run)
    run_counts = {
        "singles": run_lengths.count(1),
        "doubles": run_lengths.count(2),
        "triples": run_lengths.count(3),
        "four_plus": sum(1 for r in run_lengths if r >= 4),
    }

    return {
        "trajectory": trajectory,
        "base_rates": base_rates,
        "days_to_threshold": days_to_threshold,
        "consecutive_drinking_nights": run_counts,
        "n_drinking_nights": len(drinking_dates),
        "notes": [
            "Day 0 is the same cycle as the drinking night, not the day after — "
            "WHOOP attributes a cycle's recovery score to the sleep ending that morning.",
            "Recovery >= 80 is a minority outcome even on sober nights "
            f"({base_rates['pct_ge_80_sober_days']}% of them), so 'days to 80' is "
            "really 'days to get enough rolls of the die', not a recovery process.",
        ],
    }


def main() -> None:
    report = build_alcohol_report()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUT_DIR / "alcohol.json", "w") as f:
        json.dump(report, f, indent=2)
    print(f"wrote {OUT_DIR / 'alcohol.json'}")


if __name__ == "__main__":
    main()
