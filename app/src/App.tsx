import { useEffect, useMemo, useState } from 'react'
import { Figure } from './components/Figure'
import type { ConnectorWeights } from './lib/figureAnchors'
import { Footer } from './components/Footer'
import { HeadlineNumber } from './components/HeadlineNumber'
import { InsufficientData } from './components/InsufficientData'
import { SignalPanel } from './components/SignalPanel'
import { Slider } from './components/Slider'
import { SpeechBubble } from './components/SpeechBubble'
import { Toggle } from './components/Toggle'
import { WorkoutPanel } from './components/WorkoutPanel'
import { bandColors, bandForHRV } from './lib/bands'
import { binLabelFor, CONSISTENCY_EDGES, CONSISTENCY_LABELS, SLEEP_HOURS_EDGES, SLEEP_HOURS_LABELS, STRAIN_EDGES, STRAIN_LABELS } from './lib/bins'
import { predictHRV, predictRecovery, type Controls } from './lib/predict'
import { selectStatement, type FactorId } from './lib/selectStatement'
import { usePipelineData } from './lib/useData'
import type { BinRow, Confidence, PipelineData } from './lib/types'

function useThemeToggle() {
  const [theme, setTheme] = useState<'dark' | 'light'>(() => {
    try {
      return (localStorage.getItem('theme') as 'dark' | 'light') ?? 'dark'
    } catch {
      return 'dark'
    }
  })
  useEffect(() => {
    document.documentElement.dataset.theme = theme
    try {
      localStorage.setItem('theme', theme)
    } catch {
      /* private browsing / blocked storage — theme just won't persist */
    }
  }, [theme])
  return [theme, setTheme] as const
}

function confidenceForBin(bins: BinRow[], label: string): Confidence {
  const row = bins.find((b) => b.bin === label)
  const n = row?.n ?? 0
  if (n < 10) return 'low'
  if (n >= 100) return 'high'
  if (n >= 30) return 'medium'
  return 'low'
}

export default function App() {
  const state = usePipelineData()
  const [lastMoved, setLastMoved] = useState<FactorId>(null)
  const [theme, setTheme] = useThemeToggle()

  if (state.status === 'loading') {
    return (
      <div className="loading-screen">
        <p>Loading three years of HRV data…</p>
      </div>
    )
  }
  if (state.status === 'error') {
    return (
      <div className="loading-screen">
        <p>Couldn't load the data: {state.error}</p>
      </div>
    )
  }

  return (
    <Loaded
      data={state.data}
      lastMoved={lastMoved}
      setLastMoved={setLastMoved}
      theme={theme}
      setTheme={setTheme}
    />
  )
}

function Loaded({
  data,
  lastMoved,
  setLastMoved,
  theme,
  setTheme,
}: {
  data: PipelineData
  lastMoved: FactorId
  setLastMoved: (f: FactorId) => void
  theme: 'dark' | 'light'
  setTheme: (t: 'dark' | 'light') => void
}) {
  const { model, alcohol, bins, statements, quality } = data
  const { control_defaults } = model

  const [controls, setControls] = useState<Controls>({
    sleepHours: control_defaults.sleep_hours,
    priorDayStrain: control_defaults.prior_day_strain,
    sleepConsistencyPct: control_defaults.sleep_consistency_pct,
    alcohol: false,
  })

  const hrv = useMemo(() => predictHRV(model, controls), [model, controls])
  const recovery = useMemo(() => predictRecovery(model, hrv), [model, hrv])
  const band = useMemo(() => bandForHRV(hrv), [hrv])
  const statement = useMemo(
    () => selectStatement(statements, lastMoved, controls),
    [statements, lastMoved, controls],
  )

  // STYLE.md §5: one attribute on <body> drives every accent color via CSS —
  // no imperative color-setting elsewhere.
  useEffect(() => {
    document.body.dataset.band = band
  }, [band])

  function update<K extends keyof Controls>(key: K, value: Controls[K], factor: FactorId) {
    setControls((c) => ({ ...c, [key]: value }))
    setLastMoved(factor)
  }

  const connectorWeights: ConnectorWeights = useMemo(() => {
    const c = model.primary_model.coefficients
    const mags = {
      sleep_hours: Math.abs(c.sleep_hours.coef_ms),
      alcohol: Math.abs(c.alcohol.coef_ms),
      prior_day_strain: Math.abs(c.prior_day_strain.coef_ms),
      sleep_consistency_pct: Math.abs(c.sleep_consistency_pct.coef_ms),
    }
    const max = Math.max(...Object.values(mags))
    return {
      sleep_hours: mags.sleep_hours / max,
      alcohol: mags.alcohol / max,
      prior_day_strain: mags.prior_day_strain / max,
      sleep_consistency_pct: mags.sleep_consistency_pct / max,
    }
  }, [model])

  const colors = bandColors(theme)
  const sleepBin = binLabelFor(controls.sleepHours, SLEEP_HOURS_EDGES, SLEEP_HOURS_LABELS)
  const strainBin = binLabelFor(controls.priorDayStrain, STRAIN_EDGES, STRAIN_LABELS)
  const consistencyBin = binLabelFor(controls.sleepConsistencyPct, CONSISTENCY_EDGES, CONSISTENCY_LABELS)

  return (
    <div className="app-shell">
      <header className="app-header">
        <button
          type="button"
          className="theme-toggle"
          onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
        >
          {theme === 'dark' ? 'light mode' : 'dark mode'}
        </button>
        <h1>What moves my HRV</h1>
        <p>
          Three years of one person's real WHOOP data. Move a control, see what actually
          happened on nights like that — with the confidence level shown, not hidden.
        </p>
      </header>

      <div className="layout">
        <div className="controls-left">
          <Slider
            id="sleep-hours"
            label="Sleep hours"
            value={controls.sleepHours}
            min={4}
            max={10.5}
            step={0.1}
            unit="h"
            confidence={confidenceForBin(bins.sleep_hours_sober, sleepBin)}
            onChange={(v) => update('sleepHours', Math.round(v * 10) / 10, 'sleep_hours')}
          />
          <Slider
            id="sleep-consistency"
            label="Sleep consistency"
            value={controls.sleepConsistencyPct}
            min={20}
            max={100}
            step={1}
            unit="%"
            confidence={confidenceForBin(bins.sleep_consistency_sober, consistencyBin)}
            onChange={(v) => update('sleepConsistencyPct', v, 'sleep_consistency_pct')}
          />
          <WorkoutPanel workouts={bins.workout_next_day_hrv} theme={theme} />
        </div>

        <div className="figure-column">
          <div className="figure-wrapper">
            <Figure weights={connectorWeights} />
            <div className="headline-anchor">
              <HeadlineNumber hrv={hrv} recovery={recovery} band={band} />
            </div>
            <div className="speech-anchor">
              <SpeechBubble statement={statement} />
            </div>
          </div>
        </div>

        <div className="controls-right">
          <Slider
            id="prior-day-strain"
            label="Prior-day strain"
            value={controls.priorDayStrain}
            min={0}
            max={21}
            step={0.5}
            unit=""
            confidence={confidenceForBin(bins.prior_day_strain_sober, strainBin)}
            onChange={(v) => update('priorDayStrain', v, 'prior_day_strain')}
          />
          <Toggle
            id="alcohol"
            label="Alcohol last night"
            checked={controls.alcohol}
            confidence="high"
            onChange={(v) => update('alcohol', v, 'alcohol')}
          />
          <SignalPanel cards={statements.signal_panel} />
        </div>
      </div>

      <section className="alcohol-section" aria-label="The alcohol recovery curve">
        <h2>The one-night cost of alcohol</h2>
        <p className="section-subtitle">
          Recovery around every drinking night in the export, day 0 = the same cycle as the
          drink.
        </p>
        <div className="trajectory-chart">
          {alcohol.trajectory.map((row) => {
            const rowBand = row.mean_hrv != null ? bandForHRV(row.mean_hrv) : 'good'
            return (
              <div className="trajectory-bar" key={row.day}>
                <div
                  className="bar"
                  style={{
                    height: `${row.mean_recovery ?? 0}%`,
                    background: colors[rowBand].fill,
                  }}
                  title={`day ${row.day}: recovery ${row.mean_recovery}%, HRV ${row.mean_hrv}ms, n=${row.n}`}
                />
                <span className="bar-label">
                  {row.day === 0 ? '0 (drink)' : row.day > 0 ? `+${row.day}` : row.day}
                </span>
              </div>
            )
          })}
        </div>
        <p className="section-note">
          80+ recovery happens on {alcohol.base_rates.pct_ge_80_sober_days}% of sober days — it
          isn't a baseline she returns to, it's roughly a one-in-three outcome on any good day.
        </p>
      </section>

      <InsufficientData items={statements.insufficient_data} />
      <Footer quality={quality} model={model} />
    </div>
  )
}
