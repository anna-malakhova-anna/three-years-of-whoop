# HANDOVER — "What Moves My HRV" (WHOOP interactive)

**For:** Claude Code
**Owner:** Anna
**Status:** Analysis done and verified in a prior session; all open design questions resolved (§9). Numbers below are ground truth — re-derive them in the pipeline, but they should match. If yours differ, the pipeline is wrong, not this doc.

---

## 1. What we're building

A single interactive page, published to GitHub Pages, built on 3 years of Anna's WHOOP export.

**Centre of the screen:** a line-art human figure (see §7).
**Around the figure:** the factors that affect HRV, each rendered as a control — a slider where the factor is continuous (sleep hours, respiratory rate, prior-day strain, sleep consistency), a toggle where it's binary (alcohol last night).
**On interaction:** a speech bubble near the figure updates with a sentence drawn from a statement library, chosen by which factor the user just moved and what value they moved it to. The statements are generated from the real data, not invented.
**The headline number:** predicted HRV (ms), large, always visible, updating live as controls move. HRV is the thing we are trying to maximise. Recovery % shown as a secondary number.

This is a portfolio piece for a pivot from advisory into implementation/solutions work. It has to be defensible under technical questioning, which means the statistical honesty in §5 is not optional garnish — it is the differentiator.

---

## 2. Data

Four CSVs from a WHOOP export, Sep 2023 → Sep 2026.

| File | Rows | Notes |
|---|---|---|
| `physiological_cycles.csv` | 1,027 | one row per day-cycle; the primary table |
| `sleeps.csv` | 1,065 | includes naps (`Nap` bool column) |
| `workouts.csv` | 868 | 19 activity types |
| `journal_entries.csv` | 4,666 | long format: `Question text` / `Answered yes` |

**Join key:** `Cycle start time` normalised to a date. Journal pivots wide on `Question text`.

### Data gotchas — handle these explicitly, they are the interesting part

1. **196 duplicate dates in `physiological_cycles.csv`.** Naps create extra cycles. Naive `reindex` on the date index throws. Dedupe by keeping the row with the non-null / highest `Recovery score %` per day, or filter to non-nap cycles. Document the rule.
2. **57 cycles have no recovery score, HRV, RHR or sleep data** (watch not worn / not charged). 83 missing `Sleep consistency %`, 2 missing strain. Do not impute — drop with a logged count and surface the coverage number in the UI footer.
3. **The journal is 90% unusable.** Answer counts for "yes": alcohol 146, shared bed 19, caffeine 9, screens in bed 8, read in bed **0**. Only alcohol has the power to support a claim. The caffeine rows superficially suggest caffeine *raises* recovery 22 points — that is an n=9 artifact. **Do not put caffeine, screens, or reading in the app.** Add a visible "insufficient data" section listing them with their n. That section is a feature.
4. **Four timezones** (UTC-4/-5 Toronto DST, UTC-6 ~29 days, UTC+2 ~11 days). Parse as naive local time; do not convert to a single zone — local bedtime is the behaviourally meaningful thing.
5. Journal coverage is uneven by year: 2023 n=118, 2024 n=336, 2025 n=67, 2026 n=121. Alcohol-based claims lean on 2024. Note it.

---

## 3. Analysis 1 — what predicts HRV

### Univariate correlations with HRV (Pearson, n≈970)

| Variable | r | Verdict |
|---|---|---|
| Resting heart rate | **−0.897** | **EXCLUDE — see below** |
| Sleep performance % | 0.409 | partly circular (derived from duration ÷ need) |
| Respiratory rate | −0.358 | keep — strong and actionable-adjacent |
| Light sleep hours | 0.352 | keep, but it tracks total sleep |
| **Total sleep hours** | **0.300** | **keep — primary lever** |
| Sleep efficiency % | 0.211 | keep |
| Blood oxygen % | 0.197 | keep as context |
| Deep (SWS) hours | **−0.190** | counterintuitive — see §5 |
| Sleep consistency % | 0.157 | weak |
| Sleep debt | −0.144 | weak |
| Day strain (same day) | 0.139 | wrong causal direction |
| Prior-day strain | −0.117 | keep — correct direction |
| REM hours | −0.020 | **no relationship** |

**RHR must not be a slider.** r = −0.897 looks like the strongest finding in the dataset and is the least useful: HRV and RHR are two readings of the same autonomic state, measured in the same sleep window. Putting an RHR slider in the app would say "lower your resting heart rate to raise your HRV," which is circular and any reviewer will catch it. Put RHR in a **"signal, not lever"** panel with a one-line explanation. **Calling this out in the README is worth more than any chart on the page.**

**Respiratory rate goes in that same panel** (decided — §9.4). It's a strong predictor but not something she can act on, so it's a reading, not a control. It stays inside the fitted model as a covariate; see the model-variants table below for why that matters.

### Multivariate — actionable levers only (OLS, n=603, R² = 0.361)

| Term | Coefficient (ms) | p |
|---|---|---|
| Sleep hours | **+8.17 per hour** | <0.001 |
| Alcohol last night | **−26.93** | <0.001 |
| Respiratory rate | **−19.51 per rpm** | <0.001 |
| Sleep consistency % | +0.12 | 0.13 (n.s.) |
| Prior-day strain | −0.14 | 0.58 (n.s.) |
| Skin temp | −0.37 | 0.87 (n.s.) |

Consistency, strain and skin temp drop out once sleep and alcohol are controlled — their univariate correlations were mostly sleep in disguise. Say this in the UI; it's the kind of finding that survives scrutiny.

Alcohol as a standalone contrast: HRV 86.8 (n=140) vs 121.0 (n=482), Cohen's d = **−1.16**, p = 5.7e-27. That is an enormous effect size for a behavioural variable.

### Model variants (n=476, identical rows — decision recorded in §9.4)

| Model | R² | sleep_h | alcohol | resp rate |
|---|---|---|---|---|
| with respiratory rate | 0.387 | +5.52 | −33.94 | −16.04 |
| without | 0.316 | +4.99 | −38.67 | — |
| sleep + alcohol only | 0.315 | +5.07 | −38.78 | — |

**Respiratory rate partially mediates the alcohol effect.** Drop it and alcohol's coefficient inflates from −34 to −39 — alcohol raises respiratory rate, and without the rpm term that pathway gets re-attributed to the alcohol dummy. Two consequences:

- **Keep respiratory rate in the fitted model as a covariate**, held at her median of **15.9 rpm** when predicting. It isn't a control the user moves; it stops the alcohol coefficient from absorbing variance that isn't its own.
- Report both fits in the README. "I removed a variable and watched a coefficient inflate 15%, so I kept it as a covariate" is exactly the reasoning a technical interviewer is probing for.

**After excluding RHR and respiratory rate as controls, there are only two real levers: sleep duration and alcohol.** That's the honest state of the data — don't pad the radial layout to hide it. Prior-day strain and sleep consistency can appear as spokes, but styled as low-confidence and labelled as not significant in the model; workout type and the RHR/respiratory panel fill out the rest. A page with two strong levers and four honestly-labelled weak ones is better than six that pretend to be equal.

### Binned values — use these for the slider stops

**Sleep duration → HRV / recovery (sober nights only):**

| Sleep | n | HRV | Recovery | % of days ≥80 |
|---|---|---|---|---|
| ≤5h | 7 | 44.7 | 15.1 | 0% |
| 5–6h | 9 | 94.6 | 45.0 | 11% |
| 6–6.5h | 9 | 117.4 | 65.9 | 22% |
| 6.5–7h | 30 | 114.9 | 61.9 | 27% |
| 7–7.5h | 64 | 114.8 | 65.1 | 27% |
| 7.5–8h | 117 | 122.6 | 69.3 | 37% |
| **8–8.5h** | **110** | **127.1** | **74.2** | **46%** |
| 8.5–9h | 65 | 125.3 | 72.8 | 42% |
| 9h+ | 71 | 124.5 | 70.7 | 42% |

Returns flatten hard after 8.5h. The slider should make that visible — this is a plateau, not a line.

**Respiratory rate (sober):** ≤15.0 rpm → HRV 145.0 (n=27) · 15–15.5 → 123.7 · 15.5–16 → 125.6 · 16–17 → 115.1 (n=194) · >17 → 70.8 (n=10).

**Prior-day strain (sober):** 0–6 → 125.6 · 6–9 → 122.4 · 9–12 → 125.9 · 12–15 → 119.8 · 15+ → 116.3. Shallow, monotonic at the top end only.

**Sleep consistency (sober):** <50 → 112.6 · 50–60 → 124.7 · 60–70 → 120.2 · 70–80 → 121.1 · 80–90 → 122.1 · 90–100 → 132.8 (n=13). Noisy; render as a low-confidence factor.

**Workout type → *next* day's HRV** (n≥20 types only; baseline 117.2):
Pilates 134.3 · Yoga 131.4 · HIIT 121.1 · Strength 120.1 · Spin 116.2 · Walking 115.6 · rest day 114.6.
Treat as correlational and label it so — she likely chooses yoga on days she already feels good. Good as a secondary panel, not a lever.

**High-HRV days (top quartile, ≥137ms) vs low (≤91ms):** sleep 8.2h vs 7.7h · respiratory 15.7 vs 16.1 · consistency 71.2 vs 67.6 · alcohol on **8/132** high days vs **78/121** low days. That last ratio is the single most quotable number in the project.

---

## 4. Analysis 2 — the alcohol recovery curve

Question asked: *how many days to get back to 80+?* The honest answer reframes the question.

**Trajectory around all drinking nights (n=122 events, day 0 = the morning after):**

| Day | n | Mean recovery | Mean HRV | % ≥80 |
|---|---|---|---|---|
| −2 | 91 | 64.5 | 113.8 | 33% |
| −1 | 71 | 65.1 | 114.0 | 31% |
| **0** | **117** | **46.4** | **88.4** | **9%** |
| +1 | 86 | 67.2 | 115.7 | 37% |
| +2 | 97 | 65.9 | 114.0 | 36% |
| +3 | 92 | 65.6 | 115.4 | 38% |
| +4 | 91 | 68.6 | 118.1 | 41% |

**The dip is one night.** Recovery drops ~19 points and HRV ~26ms on the morning after, and by the next morning both are back to baseline. There is no multi-day cascade. That is a cleaner, more surprising result than a slow decay curve would have been — lead with it.

**Days to reach a threshold after a drinking night:**

| Threshold | Median days | Never within 5 days |
|---|---|---|
| ≥67 (her mean) | 1 | 6% |
| ≥76 (her sober median) | 2 | 16% |
| **≥80** | **2** | **25%** |

**Critical caveat for the UI:** recovery ≥80 happens on only **36% of sober days** and 29.9% of all days. So "when do I get back to 80+?" has no stable answer — 80+ isn't a baseline she returns to, it's roughly a one-in-three outcome on any good day. Reaching it takes a median of 2 days simply because you need ~2 rolls of that die. **Do not build a "days to 80" countdown** — it would imply a recovery process that the data says isn't there. Show the one-night dip and the 36% base rate side by side instead.

Consecutive drinking nights: 80 singles, 13 doubles, 6 triples. Not enough runs to model a dose or cumulative effect. Say so.

---

## 5. Things that will trip you up

- **Deep sleep correlates *negatively* with HRV (−0.19)**, and high-HRV days have *less* deep sleep (76 min) than low-HRV days (86 min). Almost certainly reverse causation: WHOOP shows rebound SWS after alcohol and hard strain. Include it with that explanation rather than hiding it — an unexplained negative correlation looks like a bug, an explained one looks like judgment.
- **REM has no relationship with HRV at all** (r = −0.02). Worth stating plainly given how much sleep-tracker marketing implies otherwise.
- **`Sleep performance %` is partly circular** — WHOOP computes it from asleep duration ÷ sleep need. Don't put it in the same model as sleep hours (collinearity), and don't present it as an independent lever.
- **Same-day strain correlates *positively* with HRV** (+0.14) because a high-HRV morning is what enables a hard day. Only prior-day strain is causally admissible.
- **Seasonality is noisy and probably not real.** By month, HRV ranges 105 (Nov) to 130.5 (Apr), but n≈70/month across 3 years and May (108.5) sits between April (130.5) and June (123.6), which no seasonal mechanism explains. Leave it out or mark it as unresolved.
- The model R² is 0.39. Roughly three-fifths of day-to-day HRV variance is unexplained by anything in this export. Put that number in the UI. A portfolio piece that states its own ceiling reads as more competent, not less.

---

## 6. The statement library

Statements are **generated from the pipeline output**, not hardcoded. Each is a template filled with computed numbers, plus metadata that decides when it fires.

```json
{
  "id": "sleep_under_6",
  "factor": "sleep_hours",
  "trigger": { "lt": 6 },
  "confidence": "low",
  "n": 16,
  "text": "Under 6 hours, your HRV averages {hrv} ms — about {delta} below your typical night. Only {n} nights though, so hold this loosely.",
  "values": { "hrv": 85.4, "delta": "32 ms", "n": 16 }
}
```

**Rules:**
- Every statement carries its `n` and a `confidence` tier derived from it: `high` ≥100, `medium` 30–99, `low` <30. Render the tier visibly (a dot, a border weight — not just a tooltip).
- Any bin with n < 10 gets a hedged template and a muted style. Never a confident claim.
- Alcohol statements can be assertive (d = −1.16, n = 140). Consistency and strain statements must be hedged — they weren't significant in the multivariate model.
- Statements that combine two factors (low sleep + alcohol) need the joint cell's n checked before firing; most joint cells are thin.

**Seed set to generate (exact wording is yours; these are the claims that the data supports):**

| Factor / state | Claim |
|---|---|
| sleep < 6h | HRV ~85–95, recovery under 45 |
| sleep 7–7.5h | HRV ~115, recovery ~65, 27% chance of an 80+ day |
| sleep 8–8.5h | **best band** — HRV 127, recovery 74, 46% chance of 80+ |
| sleep > 9h | no further gain; HRV 124.5, plateau not penalty |
| alcohol ON | HRV −27ms holding sleep constant; recovery 46 vs 67; only 9% of mornings hit 80 |
| alcohol, next day | fully recovered by the following morning — the cost is one night, not a weekend |
| alcohol, high-HRV days | 8 of her 132 best-HRV days followed a drink; 78 of her 121 worst did |
| prior strain > 15 | HRV −9ms vs an easy day; real but small next to sleep |
| consistency > 90% | HRV 133, n=13 — suggestive only |
| REM | no detectable relationship with her HRV |
| deep sleep | negatively correlated — likely rebound after alcohol/strain, not a cause |
| model ceiling | ~39% of HRV variance explained; the rest is unmeasured |

**"Signal, not lever" panel** — read-only cards, no sliders, each with one line on why it isn't a control:

| Reading | Content |
|---|---|
| Resting heart rate | r = −0.897 with HRV — the strongest number here and the least useful; same autonomic state, same measurement window |
| Respiratory rate | ≤15 rpm → HRV 145 (n=27) · 15.5–16 → 125.6 (n=175) · 16–17 → 115.1 (n=194) · >17 → 70.8 (n=10, usually illness). Held at her median 15.9 in the model; you can't decide to breathe slower |

---

## 7. The figure

**`image.jpeg` is in your working directory.** Read it first and trace the figure from it — match its proportions, line weight and pose. Do not substitute a generic body outline; the reference is the design.

Requirements:
- Inline SVG, not a raster. Single path-based line-art human, front-facing, centred. Trace to paths — don't embed the JPEG.
- Must work in light and dark themes — stroke uses `currentColor` or a CSS custom property, never a hardcoded hex.
- Anchor points on the figure for each factor's connector line: head (sleep), chest (HRV readout), gut (alcohol), limbs (strain, workouts). The signal-not-lever readings sit outside the radial ring, visually separated from the controls.
- Factors arranged radially around it with thin connector lines to their anchor. Connector opacity/weight scales with that factor's effect size, so the strong levers are visually louder.
- Speech bubble positioned near the head, repositioning gracefully at narrow widths (stacks below the figure under ~700px).

---

## 8. Build

**Stack:** Python (pandas, statsmodels, scipy) for the pipeline → static JSON → vanilla TS + D3 or a light React/Vite front end. No backend.

**Data is public — commit the raw CSVs.** Anna has decided to publish her real export, which makes the whole thing reproducible: anyone can clone, run the pipeline and get the same numbers. Two things to do because of that, not instead of it:
- `data/README.md` states plainly that this is the author's own WHOOP export, published deliberately, and that anyone forking should swap in their own.
- Keep the loader export-shaped rather than Anna-shaped, so a fork works with a different WHOOP account without code changes.

```
whoop-hrv/
├── data/raw/              # committed — real export, published deliberately
├── pipeline/
│   ├── load.py            # parse, dedupe (196 dup dates!), join, log dropped rows
│   ├── quality.py         # coverage + completeness report → quality.json
│   ├── correlations.py    # univariate + OLS → model.json
│   ├── alcohol.py         # event-window trajectory → alcohol.json
│   ├── bins.py            # slider stops per factor → bins.json
│   └── statements.py      # renders the statement library → statements.json
├── app/                   # front end
│   └── src/components/Figure.tsx   # ← swap in image.jpeg-derived SVG
├── public/data/*.json     # pipeline output, committed
├── notebooks/analysis.ipynb        # the reasoning, readable on GitHub
└── README.md
```

**Order:**
1. `load.py` + `quality.py` first, with tests for the dedupe rule and the timezone handling. Everything downstream is wrong if this is wrong.
2. `correlations.py` and `alcohol.py`; assert the numbers in §3–§4 in a test file so the findings can't silently drift.
3. `bins.py` → `statements.py`.
4. Front end: static figure + sliders wired to the linear model → speech bubble → confidence styling → polish.

**Definition of done:**
- Every number in the UI traces to a JSON key that traces to a pipeline function.
- Confidence tier visible on every statement.
- RHR and respiratory rate appear as explicitly-excluded controls, each with its reason.
- Both model variants reported, with the alcohol-coefficient inflation explained.
- README leads with the three findings (one-night alcohol cost, 8–8.5h plateau, 39% ceiling) — not with setup instructions.
- `pytest` green in CI on push.

---

## 9. Decisions (all settled — build to these)

1. **Figure:** `image.jpeg` is in the working directory. Trace it to SVG paths. §7.
2. **Prediction:** fitted OLS for the headline HRV number, binned lookup tables for the statement library. State this split in the UI so a reader knows which numbers are modelled and which are observed averages.
3. **Data:** public, real, committed. §8.
4. **Respiratory rate:** not a slider — lives in the "signal, not lever" panel with RHR, but stays in the fitted model as a covariate held at 15.9 rpm. See the model-variants table in §3 for why removing it would be wrong.

Nothing is blocking. Start at §8 build step 1.
