"""Load and join the four WHOOP export CSVs into one daily table.

Join key throughout: ``Cycle start time`` normalised to a naive local date
(no timezone conversion — see the docstring on ``_to_local_date``).

Dedupe rule (physiological_cycles.csv has one row per *cycle*, and naps
create a second same-day cycle): for each date, keep the row with the
highest ``Recovery score %`` (non-null values always beat null). This is a
deterministic, order-independent rule — the "main" overnight cycle almost
always carries the recovery score; a nap cycle's recovery field is usually
null and always loses the sort.

journal_entries.csv is matched to the *same* retained cycle by exact
``Cycle start time`` (not just date), so a duplicate-cycle day's journal
answers are attributed consistently with the physio dedupe rather than
silently double counted or arbitrarily first/last-picked.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"


def _to_local_date(series: pd.Series) -> pd.Series:
    """Parse a WHOOP timestamp column as naive local time and return the date.

    WHOOP timestamps have no UTC offset in the CSV; they are already local
    time for whatever timezone the watch was in that day. The export spans
    four different timezones (Toronto DST changes plus travel). We do NOT
    convert to a single timezone — local bedtime is the behaviourally
    meaningful quantity (an 11pm bedtime in Toronto and an 11pm bedtime in
    Europe are the same behaviour, different UTC instants).
    """
    return pd.to_datetime(series, errors="coerce").dt.date


@dataclass
class LoadReport:
    """Counts of what got dropped/deduped, for quality.py and the UI footer."""
    physio_rows_raw: int = 0
    physio_dup_dates: int = 0
    physio_rows_deduped: int = 0
    physio_missing_core: int = 0
    physio_missing_consistency: int = 0
    physio_missing_strain: int = 0
    journal_rows_raw: int = 0
    journal_rows_no_date: int = 0
    journal_unmatched_to_cycle: int = 0
    notes: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "physio_rows_raw": self.physio_rows_raw,
            "physio_dup_dates": self.physio_dup_dates,
            "physio_rows_deduped": self.physio_rows_deduped,
            "physio_missing_core": self.physio_missing_core,
            "physio_missing_consistency": self.physio_missing_consistency,
            "physio_missing_strain": self.physio_missing_strain,
            "journal_rows_raw": self.journal_rows_raw,
            "journal_rows_no_date": self.journal_rows_no_date,
            "journal_unmatched_to_cycle": self.journal_unmatched_to_cycle,
            "notes": self.notes,
        }


def load_physio(path: Path = DATA_DIR / "physiological_cycles.csv", report: LoadReport | None = None) -> pd.DataFrame:
    df = pd.read_csv(path)
    report = report if report is not None else LoadReport()
    report.physio_rows_raw = len(df)

    df["date"] = _to_local_date(df["Cycle start time"])
    df = df.dropna(subset=["date"])

    n_unique = df["date"].nunique()
    report.physio_dup_dates = len(df) - n_unique

    # Dedupe: highest Recovery score % wins; NaN sorts last.
    df = df.sort_values("Recovery score %", ascending=False, na_position="last")
    df = df.drop_duplicates(subset="date", keep="first").sort_values("date").reset_index(drop=True)
    report.physio_rows_deduped = len(df)

    report.physio_missing_core = int(df["Recovery score %"].isna().sum())
    report.physio_missing_consistency = int(df["Sleep consistency %"].isna().sum())
    report.physio_missing_strain = int(df["Day Strain"].isna().sum())

    df["sleep_hours"] = df["Asleep duration (min)"] / 60.0
    df["light_sleep_hours"] = df["Light sleep duration (min)"] / 60.0
    df["deep_sleep_hours"] = df["Deep (SWS) duration (min)"] / 60.0
    df["rem_sleep_hours"] = df["REM duration (min)"] / 60.0

    df = df.rename(columns={
        "Recovery score %": "recovery_pct",
        "Resting heart rate (bpm)": "rhr",
        "Heart rate variability (ms)": "hrv",
        "Skin temp (celsius)": "skin_temp_c",
        "Blood oxygen %": "spo2_pct",
        "Day Strain": "day_strain",
        "Sleep performance %": "sleep_performance_pct",
        "Respiratory rate (rpm)": "resp_rate",
        "Sleep efficiency %": "sleep_efficiency_pct",
        "Sleep consistency %": "sleep_consistency_pct",
        "Sleep debt (min)": "sleep_debt_min",
    })

    keep = [
        "date", "Cycle start time", "recovery_pct", "rhr", "hrv", "skin_temp_c",
        "spo2_pct", "day_strain", "sleep_performance_pct", "resp_rate",
        "sleep_hours", "light_sleep_hours", "deep_sleep_hours", "rem_sleep_hours",
        "sleep_efficiency_pct", "sleep_consistency_pct", "sleep_debt_min",
    ]
    return df[keep]


def load_journal(
    physio_kept_cycles: pd.DataFrame,
    path: Path = DATA_DIR / "journal_entries.csv",
    report: LoadReport | None = None,
) -> pd.DataFrame:
    """Return one row per date with one boolean column per journal question.

    Matched to the exact ``Cycle start time`` that ``load_physio`` retained
    for that date, so this table's dedupe is consistent with the physio
    table's rather than an independent (and possibly conflicting) rule.
    """
    report = report if report is not None else LoadReport()
    je = pd.read_csv(path)
    report.journal_rows_raw = len(je)

    no_date = je["Cycle start time"].isna().sum()
    report.journal_rows_no_date = int(no_date)
    je = je.dropna(subset=["Cycle start time"])

    kept_starts = set(physio_kept_cycles["Cycle start time"])
    matched = je[je["Cycle start time"].isin(kept_starts)].copy()
    report.journal_unmatched_to_cycle = int(len(je) - len(matched))

    matched["date"] = _to_local_date(matched["Cycle start time"])
    # Guard against any remaining (question, date) duplicates: OR them together.
    wide = (
        matched.groupby(["date", "Question text"])["Answered yes"]
        .max()
        .unstack("Question text")
    )
    wide.columns = [str(c) for c in wide.columns]
    return wide.reset_index()


def load_workouts(path: Path = DATA_DIR / "workouts.csv") -> pd.DataFrame:
    df = pd.read_csv(path)
    df["date"] = _to_local_date(df["Cycle start time"])
    df = df.dropna(subset=["date"])
    return df.rename(columns={"Activity name": "activity", "Activity Strain": "activity_strain"})


def build_daily_table(data_dir: Path = DATA_DIR) -> tuple[pd.DataFrame, LoadReport]:
    """The primary joined table: one row per date, physio + journal + prior-day strain."""
    report = LoadReport()
    physio = load_physio(data_dir / "physiological_cycles.csv", report)
    journal = load_journal(physio, data_dir / "journal_entries.csv", report)
    workouts = load_workouts(data_dir / "workouts.csv")

    daily = physio.merge(journal, on="date", how="left")

    daily = daily.sort_values("date").reset_index(drop=True)
    daily["prior_day_strain"] = daily["day_strain"].shift(1)

    # Workout type for *that* day, used to look at the *next* day's HRV.
    # A day can have multiple workouts; keep the highest-strain one as "the" workout.
    workouts_primary = (
        workouts.sort_values("activity_strain", ascending=False)
        .drop_duplicates(subset="date", keep="first")[["date", "activity"]]
    )
    daily = daily.merge(workouts_primary, on="date", how="left")
    daily["prior_day_activity"] = daily["activity"].shift(1)

    alcohol_col = "Have any alcoholic drinks?"
    if alcohol_col in daily.columns:
        daily["alcohol_known"] = daily[alcohol_col].notna()
        daily["alcohol"] = daily[alcohol_col].eq(True)
    else:
        daily["alcohol_known"] = False
        daily["alcohol"] = False

    report.notes.append(
        "physio dedupe: highest Recovery score % per date wins (NaN loses)."
    )
    report.notes.append(
        "journal matched to the exact retained cycle's Cycle start time, "
        "then (date, question) collapsed with OR (max) as a final safety net."
    )
    return daily, report


if __name__ == "__main__":
    daily, report = build_daily_table()
    print(daily.shape)
    print(report.as_dict())
