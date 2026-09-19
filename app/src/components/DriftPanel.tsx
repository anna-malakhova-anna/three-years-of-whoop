import type { DriftReport } from '../lib/types'

function formatPeriod(period: string): string {
  const [year, month] = period.split('-')
  const date = new Date(Number(year), Number(month) - 1, 1)
  return date.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })
}

export function DriftPanel({ drift }: { drift: DriftReport }) {
  const labelA = formatPeriod(drift.period_a)
  const labelB = formatPeriod(drift.period_b)

  return (
    <section className="drift-panel" aria-label="Year-over-year drift">
      <h2>
        {labelA} → {labelB}
      </h2>
      <p className="section-subtitle">
        Same calendar month a year apart, so season is held roughly constant. None of these
        individually reach p&lt;0.05 at this sample size (n≈21–25/month) — call them
        suggestive, not established — but the direction is consistent across every metric
        rather than scattered.
      </p>
      <div className="table-scroll">
        <table className="drift-table">
          <thead>
            <tr>
              <th>Metric</th>
              <th>{labelA}</th>
              <th className="drift-current-col">{labelB} (current)</th>
              <th>Δ</th>
              <th>Significance</th>
            </tr>
          </thead>
          <tbody>
            {drift.metrics.map((m) => {
              const directionClass =
                m.improved === true ? 'drift-improved' : m.improved === false ? 'drift-worsened' : ''
              return (
                <tr key={m.key}>
                  <td>{m.label}</td>
                  <td>
                    {m.a_mean ?? '—'}
                    {m.a_mean != null ? m.unit : ''} <small>(n={m.a_n})</small>
                  </td>
                  <td className={`drift-current-col ${directionClass}`}>
                    {m.b_mean ?? '—'}
                    {m.b_mean != null ? m.unit : ''} <small>(n={m.b_n})</small>
                  </td>
                  <td className="drift-delta">
                    {m.delta != null ? (m.delta > 0 ? `+${m.delta}` : m.delta) : '—'}
                    {m.delta != null ? m.unit : ''}
                  </td>
                  <td className="drift-p">{m.p != null ? `p=${m.p.toFixed(2)}, not significant` : 'n/a'}</td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
      <p className="section-note">
        Alcohol nights: {drift.alcohol.a_n_yes}/{drift.alcohol.a_n_known} known in {labelA} vs{' '}
        {drift.alcohol.b_n_yes}/{drift.alcohol.b_n_known} in {labelB}
        {drift.alcohol.a_n_known === 0 ? ' — the journal wasn’t answered at all that month, so this one can’t be compared.' : '.'}
      </p>
    </section>
  )
}
