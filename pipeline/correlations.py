"""Univariate correlations + multivariate OLS → public/data/model.json.

Two analyses, matching HANDOVER.md §3:
  1. Univariate Pearson r of everything against HRV, over all days with both
     values present. This is a scan, not a claim — several of these
     (RHR, same-day strain) are excluded from the app *because* of what
     causal reasoning about them reveals, not because the r is small.
  2. Multivariate OLS using only the variables that survive as actionable
     levers, run three ways (with/without respiratory rate, sleep+alcohol
     only) on an identical row set so the coefficient drift is attributable
     to the model, not to which rows happened to have which fields.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

from pipeline.load import build_daily_table

OUT_DIR = Path(__file__).resolve().parent.parent / "public" / "data"

# variable -> (column, human label, editorial verdict)
# The verdict is a judgment call about causal/actionable status, not a
# statistic — see HANDOVER.md §3 and §5 for the reasoning behind each one.
UNIVARIATE_VARS = [
    ("rhr", "Resting heart rate", "exclude", "Same autonomic state as HRV, same measurement window — putting this in the app would say 'lower your RHR to raise your HRV', which is circular."),
    ("sleep_performance_pct", "Sleep performance %", "keep_context", "Partly circular — WHOOP computes it from asleep duration ÷ sleep need, so it overlaps with sleep hours."),
    ("resp_rate", "Respiratory rate", "signal_not_lever", "Strong predictor, not something you can decide to change. Held fixed as a covariate in the model; see model variants."),
    ("light_sleep_hours", "Light sleep hours", "keep_context", "Tracks total sleep hours closely; not an independent lever."),
    ("sleep_hours", "Total sleep hours", "primary_lever", "The strongest actionable lever in the dataset."),
    ("sleep_efficiency_pct", "Sleep efficiency %", "keep_context", "Modest independent signal."),
    ("spo2_pct", "Blood oxygen %", "keep_context", "Contextual reading, not a control."),
    ("deep_sleep_hours", "Deep (SWS) hours", "counterintuitive", "Negative correlation — almost certainly reverse causation (rebound deep sleep after alcohol/strain), not a cause of low HRV."),
    ("sleep_consistency_pct", "Sleep consistency %", "weak_lever", "Weak univariately and drops to non-significant once sleep hours and alcohol are controlled."),
    ("sleep_debt_min", "Sleep debt", "weak_context", "Weak; overlaps with sleep hours."),
    ("day_strain", "Day strain (same day)", "wrong_direction", "Positive correlation, but the causal arrow runs the other way: a high-HRV morning is what enables a hard day."),
    ("prior_day_strain", "Prior-day strain", "secondary_lever", "Correct causal direction, small effect."),
    ("rem_sleep_hours", "REM hours", "no_relationship", "No detectable relationship with HRV, despite tracker marketing implying otherwise."),
]

# Actionable-levers-only multivariate model, per HANDOVER §3.
FULL_MODEL_TERMS = ["sleep_hours", "alcohol", "resp_rate", "sleep_consistency_pct", "prior_day_strain", "skin_temp_c"]
NO_RESP_TERMS = ["sleep_hours", "alcohol", "sleep_consistency_pct", "prior_day_strain", "skin_temp_c"]
MINIMAL_TERMS = ["sleep_hours", "alcohol"]


def _pearson(df: pd.DataFrame, col: str, target: str = "hrv") -> dict | None:
    sub = df[[col, target]].dropna()
    if len(sub) < 3:
        return None
    r, p = stats.pearsonr(sub[col], sub[target])
    return {"r": round(float(r), 3), "p": float(p), "n": int(len(sub))}


def _fit_ols(df: pd.DataFrame, terms: list[str], target: str = "hrv") -> dict:
    sub = df[[target] + terms].dropna().copy()
    if "alcohol" in sub.columns:
        sub["alcohol"] = sub["alcohol"].astype(int)
    X = sm.add_constant(sub[terms].astype(float))
    y = sub[target].astype(float)
    fit = sm.OLS(y, X).fit()
    coefs = {
        term: {
            "coef_ms": round(float(fit.params[term]), 2),
            "p": float(fit.pvalues[term]),
            "significant": bool(fit.pvalues[term] < 0.05),
        }
        for term in terms
    }
    return {
        "n": int(fit.nobs),
        "r_squared": round(float(fit.rsquared), 3),
        "intercept": round(float(fit.params["const"]), 2),
        "coefficients": coefs,
    }


def build_model_report() -> dict:
    daily, _ = build_daily_table()

    univariate = []
    for col, label, verdict, why in UNIVARIATE_VARS:
        stat = _pearson(daily, col)
        if stat is None:
            continue
        univariate.append({
            "variable": col,
            "label": label,
            "verdict": verdict,
            "why": why,
            **stat,
        })
    univariate.sort(key=lambda r: -abs(r["r"]))

    # Model variants share an identical row set: the rows complete for the
    # richest model (FULL_MODEL_TERMS), so R² differences are purely about
    # which terms are in the model, not which rows are in the sample.
    common_rows = daily[["hrv"] + FULL_MODEL_TERMS].dropna().index
    common = daily.loc[common_rows]

    variants = {
        "with_respiratory_rate": _fit_ols(common, FULL_MODEL_TERMS),
        "without_respiratory_rate": _fit_ols(common, NO_RESP_TERMS),
        "sleep_and_alcohol_only": _fit_ols(common, MINIMAL_TERMS),
    }

    # Primary model for the app's live prediction: full-row-count OLS
    # (not restricted to the common-row subset used for the variants
    # comparison above — the app should use every day that has the data
    # a given fit needs).
    primary = _fit_ols(daily, FULL_MODEL_TERMS)

    resp_median = round(float(daily["resp_rate"].median()), 1)
    skin_temp_median = round(float(daily["skin_temp_c"].median()), 2)

    # Alcohol standalone contrast (Cohen's d), holding nothing else constant.
    alc = daily.loc[daily["alcohol_known"], ["hrv", "alcohol"]].dropna()
    yes = alc.loc[alc["alcohol"], "hrv"]
    no = alc.loc[~alc["alcohol"], "hrv"]
    pooled_sd = np.sqrt(((len(yes) - 1) * yes.var(ddof=1) + (len(no) - 1) * no.var(ddof=1)) / (len(yes) + len(no) - 2))
    cohens_d = (yes.mean() - no.mean()) / pooled_sd
    t, p = stats.ttest_ind(yes, no, equal_var=False)
    alcohol_contrast = {
        "hrv_alcohol": round(float(yes.mean()), 1),
        "n_alcohol": int(len(yes)),
        "hrv_sober": round(float(no.mean()), 1),
        "n_sober": int(len(no)),
        "cohens_d": round(float(cohens_d), 2),
        "p": float(p),
    }

    # High vs low HRV quartile comparison.
    valid = daily.dropna(subset=["hrv"])
    q75, q25 = valid["hrv"].quantile(0.75), valid["hrv"].quantile(0.25)
    high = valid[valid["hrv"] >= q75]
    low = valid[valid["hrv"] <= q25]
    quartile_comparison = {
        "high_hrv_threshold": round(float(q75), 1),
        "low_hrv_threshold": round(float(q25), 1),
        "high": {
            "n": int(len(high)),
            "sleep_hours": round(float(high["sleep_hours"].mean()), 1),
            "resp_rate": round(float(high["resp_rate"].mean()), 1),
            "sleep_consistency_pct": round(float(high["sleep_consistency_pct"].mean()), 1),
            "alcohol_n": int(high["alcohol"].sum()),
            "alcohol_known_n": int(high["alcohol_known"].sum()),
        },
        "low": {
            "n": int(len(low)),
            "sleep_hours": round(float(low["sleep_hours"].mean()), 1),
            "resp_rate": round(float(low["resp_rate"].mean()), 1),
            "sleep_consistency_pct": round(float(low["sleep_consistency_pct"].mean()), 1),
            "alcohol_n": int(low["alcohol"].sum()),
            "alcohol_known_n": int(low["alcohol_known"].sum()),
        },
    }

    # Recovery % isn't modelled independently — the app derives its secondary
    # "Recovery" readout from a simple linear fit of recovery on HRV, since
    # the two are tightly coupled in this dataset. This keeps the split from
    # HANDOVER.md §9.2 explicit: HRV is the fitted quantity, recovery is a
    # one-line derived readout of it, not a second independent model.
    rec_sub = daily[["hrv", "recovery_pct"]].dropna()
    rec_fit = sm.OLS(rec_sub["recovery_pct"].astype(float), sm.add_constant(rec_sub["hrv"].astype(float))).fit()
    recovery_from_hrv = {
        "slope": round(float(rec_fit.params["hrv"]), 3),
        "intercept": round(float(rec_fit.params["const"]), 2),
        "r_squared": round(float(rec_fit.rsquared), 3),
        "n": int(rec_fit.nobs),
    }

    control_defaults = {
        "sleep_hours": round(float(daily["sleep_hours"].median()), 1),
        "prior_day_strain": round(float(daily["prior_day_strain"].median()), 1),
        "sleep_consistency_pct": round(float(daily["sleep_consistency_pct"].median()), 0),
    }

    return {
        "univariate_correlations": univariate,
        "control_defaults": control_defaults,
        "primary_model": {
            **primary,
            "resp_rate_held_at": resp_median,
            "skin_temp_held_at": skin_temp_median,
            "terms": FULL_MODEL_TERMS,
            "description": "OLS on actionable-lever variables plus respiratory rate as a "
                            "covariate. Used for the app's live headline HRV prediction; "
                            "respiratory rate and skin temperature are held at the values "
                            "above, not user-controlled.",
        },
        "recovery_from_hrv": recovery_from_hrv,
        "model_variants": {
            "description": "Same row set (n={}) fit three ways, to show respiratory rate's "
                            "mediation of the alcohol coefficient.".format(variants["with_respiratory_rate"]["n"]),
            **variants,
        },
        "alcohol_contrast": alcohol_contrast,
        "hrv_quartile_comparison": quartile_comparison,
    }


def main() -> None:
    report = build_model_report()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUT_DIR / "model.json", "w") as f:
        json.dump(report, f, indent=2)
    print(f"wrote {OUT_DIR / 'model.json'}")


if __name__ == "__main__":
    main()
