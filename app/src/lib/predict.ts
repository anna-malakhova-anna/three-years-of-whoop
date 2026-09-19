import type { ModelReport } from './types'

export interface Controls {
  sleepHours: number
  priorDayStrain: number
  sleepConsistencyPct: number
  alcohol: boolean
}

/** Live headline HRV number: the fitted OLS from model.json, terms taken
 * straight from primary_model.coefficients. Respiratory rate and skin
 * temperature are not user controls — they're held at the model's fixed
 * values (see HANDOVER.md §9.4 on why respiratory rate stays in the fit). */
export function predictHRV(model: ModelReport, controls: Controls): number {
  const { intercept, coefficients, resp_rate_held_at, skin_temp_held_at } = model.primary_model
  const hrv =
    intercept +
    coefficients.sleep_hours.coef_ms * controls.sleepHours +
    coefficients.alcohol.coef_ms * (controls.alcohol ? 1 : 0) +
    coefficients.resp_rate.coef_ms * resp_rate_held_at +
    coefficients.sleep_consistency_pct.coef_ms * controls.sleepConsistencyPct +
    coefficients.prior_day_strain.coef_ms * controls.priorDayStrain +
    coefficients.skin_temp_c.coef_ms * skin_temp_held_at
  return Math.max(0, hrv)
}

/** Recovery % isn't independently modelled — it's a linear readout of the
 * predicted HRV (see recovery_from_hrv in model.json / correlations.py). */
export function predictRecovery(model: ModelReport, hrv: number): number {
  const { slope, intercept } = model.recovery_from_hrv
  const recovery = intercept + slope * hrv
  return Math.min(100, Math.max(0, recovery))
}
