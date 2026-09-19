import { BAND_COLORS, bandForHRV } from '../lib/bands'
import type { SeasonalityMonth, SeasonalityReport } from '../lib/types'

function MonthChart({
  monthly,
  getValue,
  getFill,
  tooltip,
  chartClassName,
}: {
  monthly: SeasonalityMonth[]
  getValue: (m: SeasonalityMonth) => number | null
  getFill: (m: SeasonalityMonth) => string
  tooltip: (m: SeasonalityMonth) => string
  chartClassName?: string
}) {
  const values = monthly.map((m) => getValue(m) ?? 0)
  const axisMin = Math.min(...values) * 0.85
  const axisMax = Math.max(...values) * 1.08

  return (
    <div className={`trajectory-chart seasonality-chart ${chartClassName ?? ''}`}>
      {monthly.map((m) => {
        const value = getValue(m)
        const heightPct = value != null ? ((value - axisMin) / (axisMax - axisMin)) * 100 : 0
        return (
          <div className="trajectory-bar" key={m.month}>
            <div
              className="bar"
              style={{ height: `${Math.max(heightPct, 2)}%`, background: getFill(m) }}
              title={tooltip(m)}
            />
            <span className="bar-label">{m.month}</span>
          </div>
        )
      })}
    </div>
  )
}

export function SeasonalityPanel({ seasonality }: { seasonality: SeasonalityReport }) {
  const { anova, annual_cycle_fit: cycle, workout_chi_square: workoutTest } = seasonality

  return (
    <section className="seasonality-panel" aria-label="Seasonality check">
      <h2>Does season matter?</h2>
      <p className="section-subtitle">
        Pooling all three years by calendar month. Month-of-year is statistically significant for
        HRV (ANOVA p={anova.hrv_p < 0.0001 ? '<0.0001' : anova.hrv_p.toFixed(4)}) but explains only
        about {Math.round(anova.hrv_eta_squared * 100)}% of day-to-day variance. A smooth annual
        cycle — the shape a real seasonal effect would trace — explains under{' '}
        {Math.round(cycle.r_squared * 1000) / 10}% and isn't significant on its own (p=
        {cycle.sin_p.toFixed(2)}). Real month-to-month variation, not season.
      </p>

      <h3 className="seasonality-subheading">HRV by month</h3>
      <MonthChart
        monthly={seasonality.monthly}
        getValue={(m) => m.hrv_mean}
        getFill={(m) => BAND_COLORS[m.hrv_mean != null ? bandForHRV(m.hrv_mean) : 'good'].fill}
        tooltip={(m) => `${m.month}: HRV ${m.hrv_mean}ms, recovery ${m.recovery_mean}%, n=${m.hrv_n}`}
      />
      <p className="section-note">
        Best: {seasonality.best_month.month} ({seasonality.best_month.hrv_mean}ms) · Worst:{' '}
        {seasonality.worst_month.month} ({seasonality.worst_month.hrv_mean}ms) · April drops
        sharply into May then rebounds in June — a zigzag no seasonal mechanism produces
        (HANDOVER.md §5).
      </p>

      <h3 className="seasonality-subheading">Workouts logged by month</h3>
      <MonthChart
        monthly={seasonality.monthly}
        getValue={(m) => m.workout_pct}
        getFill={() => 'var(--benday-blue)'}
        tooltip={(m) => `${m.month}: workout logged on ${m.workout_pct}% of days, n=${m.n_days}`}
      />
      <p className="section-note">
        Whether a workout got logged at all does <em>not</em> vary by month (chi-square test, p=
        {workoutTest.p.toFixed(2)}) — no seasonal training pattern in this export, at least not in
        how often something got logged.
      </p>
    </section>
  )
}
