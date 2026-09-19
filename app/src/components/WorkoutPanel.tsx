import type { BinsReport } from '../lib/types'

export function WorkoutPanel({ workouts }: { workouts: BinsReport['workout_next_day_hrv'] }) {
  const max = Math.max(...workouts.activities.map((a) => a.mean_next_day_hrv ?? 0))
  return (
    <section className="workout-panel" aria-label="Workout type and next-day HRV">
      <h2>Workout type → next day's HRV</h2>
      <p className="section-subtitle">
        Correlational, not causal — she likely picks yoga on days she already feels good.
        Baseline across all days: {workouts.baseline_all_days_hrv} ms.
      </p>
      <ul className="workout-bars">
        {workouts.activities.map((a) => (
          <li key={a.activity}>
            <span className="workout-label">{a.activity}</span>
            <span className="workout-bar-track">
              <span
                className="workout-bar-fill"
                style={{ width: `${((a.mean_next_day_hrv ?? 0) / max) * 100}%` }}
              />
            </span>
            <span className="workout-value">
              {a.mean_next_day_hrv} ms <small>(n={a.n})</small>
            </span>
          </li>
        ))}
      </ul>
    </section>
  )
}
