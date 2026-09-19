// Anchor points on the Figure's line art, in its viewBox coordinate space
// (-80 -60 480 700). Kept separate from the component so Fast Refresh only
// sees a component export in Figure.tsx.
export const ANCHORS = {
  head: { x: 163, y: 50 }, // sleep hours
  chest: { x: 163, y: 140 }, // HRV / recovery readout
  gut: { x: 163, y: 205 }, // alcohol
  handRaised: { x: 226, y: 26 }, // prior-day strain
  handLow: { x: 82, y: 182 }, // sleep consistency
  footForward: { x: 124, y: 438 },
  footBack: { x: 274, y: 440 },
} as const

export interface ConnectorWeights {
  sleep_hours: number
  alcohol: number
  prior_day_strain: number
  sleep_consistency_pct: number
}
