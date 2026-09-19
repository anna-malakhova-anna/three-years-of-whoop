# Data

`raw/` is the author's own real WHOOP export (Sep 2023 → Sep 2026), committed on purpose so
the whole analysis is reproducible: clone this repo, run the pipeline, and you get the same
numbers this project reports.

If you're forking this to build your own version: **replace the four CSVs in `raw/` with your
own WHOOP export** (Settings → Export in the WHOOP app gives you the same four files with the
same column names). The loader in `pipeline/load.py` is written against WHOOP's export shape,
not against anything specific to this dataset — point it at your own export and it should just
work. The 196 duplicate-date rows, missing-data counts, and journal answer counts will all be
different for your data; the pipeline recomputes and reports all of them from whatever CSVs are
in this folder rather than assuming this project's numbers.

## Files

| File | What it is |
|---|---|
| `physiological_cycles.csv` | One row per day-cycle: recovery, HRV, RHR, sleep stages, strain, respiratory rate. The primary table. |
| `sleeps.csv` | Sleep-specific detail, including naps (`Nap` column). |
| `workouts.csv` | Individual workouts with activity type and strain. |
| `journal_entries.csv` | Long-format daily journal answers (alcohol, caffeine, screens, etc.), one row per question per day. |

See `HANDOVER.md` (repo root) §2 for the join key, the dedupe rule for duplicate cycle dates,
and the specific data quality issues this pipeline works around.
