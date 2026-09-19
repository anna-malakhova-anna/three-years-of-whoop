import type { ModelReport, QualityReport } from '../lib/types'

export function Footer({ quality, model }: { quality: QualityReport; model: ModelReport }) {
  return (
    <footer className="app-footer">
      <p>
        {quality.date_range.start} → {quality.date_range.end} · {quality.n_days_in_range} days ·{' '}
        {quality.dedupe.physio_dup_dates_collapsed} nap-duplicate cycles collapsed ·{' '}
        {quality.missing_core.recovery_pct.n_missing} days with no recovery/HRV reading
        (watch not worn) · model explains {Math.round(model.primary_model.r_squared * 100)}% of
        HRV variance (R²={model.primary_model.r_squared}, n={model.primary_model.n}).
      </p>
      <p>
        Data is the author's own real WHOOP export, published deliberately. Nothing here is
        imputed — missing values are dropped and counted, not filled in.
      </p>
    </footer>
  )
}
