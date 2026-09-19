// Mirrors the JSON shapes written by pipeline/*.py. Every field here should
// trace back to a pipeline function — see HANDOVER.md "Definition of done".

export interface QualityReport {
  date_range: { start: string; end: string }
  n_days_in_range: number
  dedupe: {
    physio_rows_raw: number
    physio_dup_dates_collapsed: number
    physio_rows_after_dedupe: number
    rule: string
  }
  missing_core: Record<string, { label: string; n_missing: number; pct_missing: number }>
  missing_sleep_consistency: number
  missing_day_strain: number
  journal: {
    rows_raw: number
    rows_no_date: number
    rows_not_matched_to_kept_cycle: number
    questions: { question: string; n_answered: number; n_yes: number; sufficient: boolean }[]
    alcohol_coverage_by_year: { year: number; n_answered: number }[]
    insufficient_data_threshold: number
  }
  notes: string[]
}

export interface UnivariateCorrelation {
  variable: string
  label: string
  verdict: string
  why: string
  r: number
  p: number
  n: number
}

export interface ModelCoefficient {
  coef_ms: number
  p: number
  significant: boolean
}

export interface ModelFit {
  n: number
  r_squared: number
  intercept: number
  coefficients: Record<string, ModelCoefficient>
}

export interface ModelReport {
  univariate_correlations: UnivariateCorrelation[]
  control_defaults: { sleep_hours: number; prior_day_strain: number; sleep_consistency_pct: number }
  primary_model: ModelFit & {
    resp_rate_held_at: number
    skin_temp_held_at: number
    terms: string[]
    description: string
  }
  recovery_from_hrv: { slope: number; intercept: number; r_squared: number; n: number }
  model_variants: {
    description: string
    with_respiratory_rate: ModelFit
    without_respiratory_rate: ModelFit
    sleep_and_alcohol_only: ModelFit
  }
  alcohol_contrast: {
    hrv_alcohol: number
    n_alcohol: number
    hrv_sober: number
    n_sober: number
    cohens_d: number
    p: number
  }
  hrv_quartile_comparison: {
    high_hrv_threshold: number
    low_hrv_threshold: number
    high: QuartileCell
    low: QuartileCell
  }
}

interface QuartileCell {
  n: number
  sleep_hours: number
  resp_rate: number
  sleep_consistency_pct: number
  alcohol_n: number
  alcohol_known_n: number
}

export interface AlcoholReport {
  trajectory: { day: number; n: number; mean_recovery: number | null; mean_hrv: number | null; pct_ge_80: number | null }[]
  base_rates: {
    pct_ge_80_sober_days: number
    pct_ge_80_all_days: number
    n_sober_days: number
    n_all_days: number
  }
  days_to_threshold: Record<string, { threshold_value: number; median_days: number | null; pct_never_within_5_days: number; n_events: number }>
  consecutive_drinking_nights: { singles: number; doubles: number; triples: number; four_plus: number }
  n_drinking_nights: number
  notes: string[]
}

export interface BinRow {
  bin: string
  n: number
  mean_hrv: number | null
  mean_recovery: number | null
  pct_recovery_ge_80: number | null
}

export interface BinsReport {
  sleep_hours_sober: BinRow[]
  resp_rate_sober: BinRow[]
  prior_day_strain_sober: BinRow[]
  sleep_consistency_sober: BinRow[]
  workout_next_day_hrv: {
    baseline_all_days_hrv: number
    min_n: number
    activities: { activity: string; n: number; mean_next_day_hrv: number | null }[]
    note: string
  }
}

export type Confidence = 'high' | 'medium' | 'low'

export interface Statement {
  id: string
  factor: string
  trigger: Record<string, unknown>
  confidence: Confidence
  n: number
  text: string
  values: Record<string, unknown>
}

export interface SignalPanelCard {
  id: string
  label: string
  text: string
  values: UnivariateCorrelation
}

export interface StatementsReport {
  statements: Statement[]
  signal_panel: SignalPanelCard[]
  insufficient_data: { question: string; n_yes: number; n_answered: number }[]
  model_ceiling: { r_squared: number; n: number }
}

export interface DriftMetric {
  key: string
  label: string
  unit: string
  a_mean: number | null
  a_n: number
  b_mean: number | null
  b_n: number
  delta: number | null
  p: number | null
  cohens_d: number | null
}

export interface DriftReport {
  period_a: string
  period_b: string
  metrics: DriftMetric[]
  alcohol: { a_n_known: number; a_n_yes: number; b_n_known: number; b_n_yes: number }
  notes: string[]
}

export interface PipelineData {
  quality: QualityReport
  model: ModelReport
  alcohol: AlcoholReport
  bins: BinsReport
  statements: StatementsReport
  drift: DriftReport
}
