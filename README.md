# What moves my HRV

An interactive figure built on three years of one person's real WHOOP export (Sep 2023 → Sep
2026, 831 days). Move a control, watch a predicted HRV number respond, and read a sentence
generated from the actual data for that value — not a hardcoded copy line.

_Not yet deployed._

## Three findings, before anything else

**1. The cost of a drinking night is one night, not a weekend.** Recovery drops from a
baseline around 65% to 46.8% the morning after (n=119), and HRV drops from ~114 ms to 88.3 ms.
By the next morning, both are back near baseline (recovery 68.1%, HRV 116.9 ms, n=88). There is
no multi-day cascade — the dip is real and large, and it's over in one sleep.

**2. Sleep has a clear plateau, not a straight line, at 8–8.5 hours.** HRV rises with sleep
duration up to the 8–8.5h band (130.9 ms average, n=94, 48.9% of those days hit 80+ recovery),
then flattens — more sleep past that point doesn't buy more HRV. Fitting a straight line across
the whole range would hide this; the app renders it as a plateau because that's what the data
shows.

**3. This model explains about a quarter of day-to-day HRV variance, and says so.** R² = 0.258
(n=775) for the fitted model (sleep hours, alcohol, respiratory rate as a covariate, sleep
consistency, prior-day strain, skin temperature). The other ~74% is stress, illness, travel,
and everything else this export doesn't capture. The app states this ceiling in the UI instead
of implying more precision than the data supports.

A supporting number worth keeping in your head: on her best-HRV days, only 7 of 210 (via the
quartile comparison; roughly one in thirty) followed a drinking night. On her worst-HRV days, it
was 78 of 209 — better than one in three.

## What's honestly excluded, and why

- **Resting heart rate is not a slider.** r = −0.888 with HRV — the strongest correlation in
  the whole dataset, and the least actionable one. RHR and HRV are two readings of the same
  autonomic state in the same sleep window; a slider here would just say "lower your resting
  heart rate to raise your HRV."
- **Respiratory rate is not a slider either**, for a related but distinct reason: it's a real,
  strong predictor, but not something you decide to change. It stays inside the fitted model as
  a covariate (held at her median, 15.9 rpm) because dropping it from the model inflates the
  alcohol coefficient by about 16% (−27.72 ms → −32.25 ms) — respiratory rate partially mediates
  the alcohol effect, and removing it re-attributes that pathway to the alcohol dummy. Both
  model fits are reported in `public/data/model.json`.
- **Caffeine, screens-in-bed, and reading-in-bed are not in the app at all.** They're tracked in
  the journal, but the "yes" counts are too thin to support a claim (n=9, n=5, n=0 in the
  current export) — caffeine's raw correlation even *suggests* it raises recovery, which is an
  n=9 artifact, not a finding. These show up in the app's "insufficient data" section instead
  of a chart, with their real n visible.
- **Workout type is a read-only panel, not a control.** Pilates/yoga days precede higher next-day
  HRV than spin/rest days in this data, but the likely direction is reversed causality — she
  probably picks a gentle workout on a day she already feels good, not the other way around.

## Data quality, dealt with explicitly

- 196 of 1,027 raw physio-cycle rows are duplicate dates (naps create a second same-day cycle).
  The dedupe rule — keep the highest `Recovery score %` per date — is implemented once in
  `pipeline/load.py` and reused everywhere downstream.
- 32 days in the deduped table have no recovery/HRV/RHR reading at all (watch not worn or not
  charged). Nothing is imputed; every pipeline function drops what it can't compute and reports
  the drop count in `public/data/quality.json`, which also drives the footer in the UI.
- Four timezones appear across the export (Toronto DST plus travel). Timestamps are parsed as
  naive local time and never converted to a single zone, since local bedtime — not UTC instant —
  is the behaviourally meaningful quantity.

## How the numbers flow

```
data/raw/*.csv  →  pipeline/*.py  →  public/data/*.json  →  app/ (React + D3, static)
```

Every number the UI shows traces to a JSON key that traces to a pipeline function — there is no
number in `app/` that was typed in by hand. `pipeline/statements.py` renders the speech-bubble
statement library from templates filled with computed values, not hardcoded sentences.

The split: **HRV** is a fitted OLS prediction (`model.json → primary_model`) so it responds
smoothly as a slider moves. **Recovery %**, shown as the secondary number, is not modelled
independently — it's a linear readout of the predicted HRV (`model.json → recovery_from_hrv`),
since the two are tightly coupled in this data and a second independent fit would just add
noise without adding honesty. Everything else in the statement library (the bin breakdowns, the
alcohol trajectory, the quartile comparison) is an observed average over real days, not a model
output — the UI is explicit about which numbers are modelled and which are observed.

## Running it yourself

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt   # pandas, numpy, scipy, statsmodels, pytest
python -m pipeline.run_all        # writes public/data/*.json
pytest                            # 30 tests lock in the findings above

cd app
npm install
npm run dev                       # http://localhost:5173
```

`pipeline/run_all.py` runs `quality → correlations → alcohol → bins → statements` in the order
each one's output depends on the last. `app/vite.config.ts` serves `../public` as the app's
public directory, so the pipeline's JSON output is what the dev server and the production build
both read — there's no copy step.

## Deploying

`.github/workflows/deploy.yml` runs the pipeline, the tests, and the app build on every push to
`main`, then publishes `app/dist` to GitHub Pages. It needs **Settings → Pages → Source: GitHub
Actions** enabled once on the repo; after that, every push to `main` redeploys automatically.

## Repo layout

```
data/raw/              committed real WHOOP export (see data/README.md)
pipeline/               load → quality → correlations → alcohol → bins → statements
tests/                  pytest, asserts the findings above against the committed data
public/data/*.json      pipeline output, committed, served by the app
app/                    React + TypeScript + D3, static, no backend
notebooks/analysis.ipynb   the reasoning behind the pipeline, readable on GitHub
```

## Stack

Python (pandas, statsmodels, scipy) for the analysis pipeline. Vanilla React + TypeScript +
D3-adjacent hand-rolled SVG for the front end — no backend, no database; `public/data/*.json` is
the entire API surface, and it's committed to the repo.
