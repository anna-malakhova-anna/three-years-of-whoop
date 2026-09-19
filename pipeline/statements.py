"""Render the statement library from pipeline outputs → public/data/statements.json.

Every statement is a template filled with numbers computed elsewhere in the
pipeline (model.py, alcohol.py, bins.py, quality.py) — nothing here is a
hardcoded number. See HANDOVER.md §6 for the rules this file implements:

  - every statement carries n and a confidence tier (high >= 100, medium
    30-99, low < 30), rendered visibly by the front end, not just in a
    tooltip;
  - any bin with n < 10 is hedged, never asserted confidently;
  - alcohol statements may be assertive (large, well-powered effect);
    consistency and prior-day-strain statements are always hedged, because
    they weren't significant in the multivariate model regardless of n.
"""
from __future__ import annotations

import json
from pathlib import Path

from pipeline.alcohol import build_alcohol_report
from pipeline.bins import build_bins_report
from pipeline.correlations import build_model_report
from pipeline.quality import build_quality_report

OUT_DIR = Path(__file__).resolve().parent.parent / "public" / "data"

ALWAYS_HEDGED_FACTORS = {"prior_day_strain", "sleep_consistency_pct"}


def confidence_tier(n: int) -> str:
    if n >= 100:
        return "high"
    if n >= 30:
        return "medium"
    return "low"


def _bin_statement(factor: str, row: dict, unit_label: str, extra_hedge: bool) -> dict:
    n = row["n"]
    tier = confidence_tier(n)
    hedge = extra_hedge or n < 10
    recovery = row["mean_recovery"]
    hrv = row["mean_hrv"]
    pct80 = row["pct_recovery_ge_80"]

    if hrv is None or n == 0:
        text = f"No days recorded in the {row['bin']} {unit_label} range."
    elif hedge:
        text = (
            f"In the {row['bin']} {unit_label} range, HRV averages {hrv} ms and "
            f"recovery {recovery}% — but that's only {n} day{'s' if n != 1 else ''}, "
            f"so hold this loosely."
        )
    else:
        text = (
            f"In the {row['bin']} {unit_label} range, HRV averages {hrv} ms and "
            f"recovery {recovery}%, with {pct80}% of those days hitting 80+ recovery "
            f"(n={n})."
        )

    return {
        "id": f"{factor}_{row['bin']}",
        "factor": factor,
        "trigger": {"bin": row["bin"]},
        "confidence": "low" if hedge else tier,
        "n": n,
        "text": text,
        "values": {"hrv": hrv, "recovery": recovery, "pct_ge_80": pct80, "n": n},
    }


def build_statements(model: dict, alcohol: dict, bins: dict, quality: dict) -> dict:
    statements: list[dict] = []

    # --- Sleep hours (primary lever; can speak assertively where n is healthy) ---
    sleep_bins = bins["sleep_hours_sober"]
    for row in sleep_bins:
        statements.append(_bin_statement("sleep_hours", row, "hour", extra_hedge=False))
    best = max((r for r in sleep_bins if r["mean_hrv"] is not None), key=lambda r: r["mean_hrv"])
    statements.append({
        "id": "sleep_hours_best_band",
        "factor": "sleep_hours",
        "trigger": {"best_band": True},
        "confidence": confidence_tier(best["n"]),
        "n": best["n"],
        "text": f"Her best-recovery sleep band is {best['bin']} — HRV {best['mean_hrv']} ms, "
                f"recovery {best['mean_recovery']}%, {best['pct_recovery_ge_80']}% of days at 80+ "
                f"(n={best['n']}). More sleep past this band doesn't add HRV — it's a plateau, not a penalty.",
        "values": best,
    })

    # --- Respiratory rate (signal, not a slider — rendered in the read-only panel) ---
    resp_bins = bins["resp_rate_sober"]
    for row in resp_bins:
        statements.append(_bin_statement("resp_rate", row, "rpm", extra_hedge=False))

    # --- Prior-day strain (always hedged) ---
    for row in bins["prior_day_strain_sober"]:
        statements.append(_bin_statement("prior_day_strain", row, "strain", extra_hedge=True))

    # --- Sleep consistency (always hedged) ---
    for row in bins["sleep_consistency_sober"]:
        statements.append(_bin_statement("sleep_consistency_pct", row, "%", extra_hedge=True))

    # --- Alcohol: on/off toggle ---
    contrast = model["alcohol_contrast"]
    statements.append({
        "id": "alcohol_on",
        "factor": "alcohol",
        "trigger": {"value": True},
        "confidence": confidence_tier(contrast["n_alcohol"]),
        "n": contrast["n_alcohol"],
        "text": f"On nights with alcohol, HRV averages {contrast['hrv_alcohol']} ms vs "
                f"{contrast['hrv_sober']} ms sober — a difference of "
                f"{round(contrast['hrv_sober'] - contrast['hrv_alcohol'], 1)} ms "
                f"(Cohen's d = {contrast['cohens_d']}, n={contrast['n_alcohol']} vs {contrast['n_sober']}).",
        "values": contrast,
    })
    statements.append({
        "id": "alcohol_off",
        "factor": "alcohol",
        "trigger": {"value": False},
        "confidence": confidence_tier(contrast["n_sober"]),
        "n": contrast["n_sober"],
        "text": f"Sober nights: HRV averages {contrast['hrv_sober']} ms (n={contrast['n_sober']}) — "
                f"her baseline before any other factor moves.",
        "values": contrast,
    })
    day0 = next(r for r in alcohol["trajectory"] if r["day"] == 0)
    day1 = next(r for r in alcohol["trajectory"] if r["day"] == 1)
    statements.append({
        "id": "alcohol_next_day",
        "factor": "alcohol",
        "trigger": {"value": True, "context": "next_day"},
        "confidence": confidence_tier(min(day0["n"], day1["n"])),
        "n": day0["n"],
        "text": f"The cost is one night, not a weekend: recovery drops to {day0['mean_recovery']}% "
                f"the morning after (only {day0['pct_ge_80']}% of those mornings hit 80+), "
                f"then is back near baseline by the next morning ({day1['mean_recovery']}%, "
                f"{day1['pct_ge_80']}% at 80+).",
        "values": {"day0": day0, "day1": day1},
    })
    q = model["hrv_quartile_comparison"]
    statements.append({
        "id": "alcohol_high_hrv_days",
        "factor": "alcohol",
        "trigger": {"context": "quartile"},
        "confidence": confidence_tier(q["high"]["alcohol_known_n"]),
        "n": q["high"]["alcohol_known_n"],
        "text": f"{q['high']['alcohol_n']} of her {q['high']['n']} best-HRV days followed a drink, "
                f"versus {q['low']['alcohol_n']} of her {q['low']['n']} worst-HRV days.",
        "values": q,
    })
    statements.append({
        "id": "alcohol_recovery_base_rate",
        "factor": "alcohol",
        "trigger": {"context": "base_rate"},
        "confidence": "high",
        "n": alcohol["base_rates"]["n_sober_days"],
        "text": f"80+ recovery isn't a baseline she returns to — it happens on "
                f"{alcohol['base_rates']['pct_ge_80_sober_days']}% of sober days and "
                f"{alcohol['base_rates']['pct_ge_80_all_days']}% of all days. Reaching it after "
                f"a drink takes a median of "
                f"{alcohol['days_to_threshold']['80']['median_days']} days simply because that's "
                f"how many rolls of the die it takes on a good week "
                f"({alcohol['days_to_threshold']['80']['pct_never_within_5_days']}% never get there "
                f"within 5 days).",
        "values": alcohol["days_to_threshold"]["80"],
    })

    # --- Model ceiling ---
    primary = model["primary_model"]
    statements.append({
        "id": "model_ceiling",
        "factor": "meta",
        "trigger": {"always": True},
        "confidence": "high",
        "n": primary["n"],
        "text": f"This model explains {round(primary['r_squared'] * 100)}% of day-to-day HRV "
                f"variance (R²={primary['r_squared']}, n={primary['n']}). The rest is unmeasured — "
                f"stress, illness, travel, things this export doesn't capture.",
        "values": {"r_squared": primary["r_squared"], "n": primary["n"]},
    })

    # --- REM / deep sleep asides ---
    rem = next(v for v in model["univariate_correlations"] if v["variable"] == "rem_sleep_hours")
    statements.append({
        "id": "rem_no_relationship",
        "factor": "meta",
        "trigger": {"always": True},
        "confidence": "high",
        "n": rem["n"],
        "text": f"REM sleep has no detectable relationship with her HRV (r={rem['r']}, "
                f"p={rem['p']:.2f}) — despite what sleep-tracker marketing implies.",
        "values": rem,
    })
    deep = next(v for v in model["univariate_correlations"] if v["variable"] == "deep_sleep_hours")
    statements.append({
        "id": "deep_sleep_inverse",
        "factor": "meta",
        "trigger": {"always": True},
        "confidence": "high",
        "n": deep["n"],
        "text": f"Deep sleep correlates negatively with HRV (r={deep['r']}) — almost certainly "
                f"rebound SWS after alcohol or hard strain, not a cause of lower HRV.",
        "values": deep,
    })

    # --- Workout type (correlational panel) ---
    workouts = bins["workout_next_day_hrv"]
    statements.append({
        "id": "workout_next_day",
        "factor": "workout",
        "trigger": {"always": True},
        "confidence": "medium",
        "n": workouts["min_n"],
        "text": "Workout type and next-day HRV: " + ", ".join(
            f"{a['activity']} {a['mean_next_day_hrv']}" for a in workouts["activities"]
        ) + f". Baseline across all days is {workouts['baseline_all_days_hrv']} ms. " + workouts["note"],
        "values": workouts,
    })

    # --- Signal-not-lever panel: RHR + respiratory rate ---
    rhr = next(v for v in model["univariate_correlations"] if v["variable"] == "rhr")
    resp = next(v for v in model["univariate_correlations"] if v["variable"] == "resp_rate")
    signal_panel = [
        {
            "id": "signal_rhr",
            "label": "Resting heart rate",
            "text": f"r = {rhr['r']} with HRV (n={rhr['n']}) — the strongest number in this whole "
                    f"dataset, and the least useful. RHR and HRV are two readings of the same "
                    f"autonomic state, taken in the same sleep window. A slider here would say "
                    f"'lower your resting heart rate to raise your HRV' — circular, not actionable.",
            "values": rhr,
        },
        {
            "id": "signal_resp_rate",
            "label": "Respiratory rate",
            "text": f"r = {resp['r']} with HRV (n={resp['n']}). Strong predictor, but not something "
                    f"you decide to change — it stays in the fitted model as a covariate, held at "
                    f"her median of {model['primary_model']['resp_rate_held_at']} rpm, because "
                    f"removing it inflates the alcohol coefficient "
                    f"(see model variants: {model['model_variants']['without_respiratory_rate']['coefficients']['alcohol']['coef_ms']} "
                    f"vs {model['model_variants']['with_respiratory_rate']['coefficients']['alcohol']['coef_ms']} ms).",
            "values": resp,
        },
    ]

    # --- Insufficient-data section, straight from quality.json ---
    insufficient = [
        {
            "question": q_row["question"],
            "n_yes": q_row["n_yes"],
            "n_answered": q_row["n_answered"],
        }
        for q_row in quality["journal"]["questions"]
        if not q_row["sufficient"]
    ]

    return {
        "statements": statements,
        "signal_panel": signal_panel,
        "insufficient_data": insufficient,
        "model_ceiling": {"r_squared": primary["r_squared"], "n": primary["n"]},
    }


def main() -> None:
    model = build_model_report()
    alcohol = build_alcohol_report()
    bins = build_bins_report()
    quality = build_quality_report()

    result = build_statements(model, alcohol, bins, quality)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUT_DIR / "statements.json", "w") as f:
        json.dump(result, f, indent=2)
    print(f"wrote {OUT_DIR / 'statements.json'} ({len(result['statements'])} statements)")


if __name__ == "__main__":
    main()
