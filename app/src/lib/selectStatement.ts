import { binLabelFor, CONSISTENCY_EDGES, CONSISTENCY_LABELS, SLEEP_HOURS_EDGES, SLEEP_HOURS_LABELS, STRAIN_EDGES, STRAIN_LABELS } from './bins'
import type { Controls } from './predict'
import type { Statement, StatementsReport } from './types'

export type FactorId = 'sleep_hours' | 'prior_day_strain' | 'sleep_consistency_pct' | 'alcohol' | null

export function selectStatement(
  report: StatementsReport,
  lastMoved: FactorId,
  controls: Controls,
): Statement | undefined {
  const { statements } = report

  if (lastMoved === 'sleep_hours') {
    const bin = binLabelFor(controls.sleepHours, SLEEP_HOURS_EDGES, SLEEP_HOURS_LABELS)
    return statements.find((s) => s.factor === 'sleep_hours' && s.trigger.bin === bin)
  }
  if (lastMoved === 'prior_day_strain') {
    const bin = binLabelFor(controls.priorDayStrain, STRAIN_EDGES, STRAIN_LABELS)
    return statements.find((s) => s.factor === 'prior_day_strain' && s.trigger.bin === bin)
  }
  if (lastMoved === 'sleep_consistency_pct') {
    const bin = binLabelFor(controls.sleepConsistencyPct, CONSISTENCY_EDGES, CONSISTENCY_LABELS)
    return statements.find((s) => s.factor === 'sleep_consistency_pct' && s.trigger.bin === bin)
  }
  if (lastMoved === 'alcohol') {
    return statements.find((s) => s.id === (controls.alcohol ? 'alcohol_on' : 'alcohol_off'))
  }
  // Idle / first paint: lead with the honesty statement.
  return statements.find((s) => s.id === 'model_ceiling')
}
