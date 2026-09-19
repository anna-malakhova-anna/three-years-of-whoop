// Anchor points on the Figure's line art, in its viewBox coordinate space
// (-40 -40 520 600). Kept separate from the component so Fast Refresh only
// sees a component export in Figure.tsx.
export const ANCHORS = {
  head: { x: 320, y: 80 }, // sleep hours
  chest: { x: 255, y: 200 }, // HRV / recovery readout
  gut: { x: 230, y: 290 }, // alcohol
  handRaised: { x: 328, y: 84 }, // prior-day strain (front arm, near head)
  handLow: { x: 145, y: 218 }, // sleep consistency (back arm, trailing)
  footForward: { x: 304, y: 250 },
  footBack: { x: 148, y: 455 },
} as const

export interface ConnectorWeights {
  sleep_hours: number
  alcohol: number
  prior_day_strain: number
  sleep_consistency_pct: number
}

export const HRV_BANDS = ['high', 'good', 'mid', 'low', 'poor'] as const
export type HrvBand = (typeof HRV_BANDS)[number]

/** Anna's bands (STYLE.md §4). Ordered high to low; first match wins. */
export function bandForHRV(hrv: number): HrvBand {
  if (hrv >= 130) return 'high'
  if (hrv >= 110) return 'good'
  if (hrv >= 90) return 'mid'
  if (hrv >= 70) return 'low'
  return 'poor'
}
