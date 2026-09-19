import type { HrvBand } from './figureAnchors'

export { bandForHRV, HRV_BANDS } from './figureAnchors'
export type { HrvBand } from './figureAnchors'

export type Theme = 'dark' | 'light'

// STYLE.md §4 — fill hex for large areas/dots/thick strokes, text hex for
// text and strokes under 2px. Dark-theme values are the spec's originals,
// validated against --ground #141312. Light-theme values are re-derived,
// same-hue-family, each independently verified to clear the same
// thresholds (>=3:1 fill, >=4.5:1 text) against the light ground #F2EDE4 —
// the spec only validated the dark ground and several bands (mid yellow
// especially) fail outright on light without this.
const DARK: Record<HrvBand, { fill: string; text: string }> = {
  high: { fill: '#1F8F45', text: '#35C066' },
  good: { fill: '#5CCB3E', text: '#5CCB3E' },
  mid: { fill: '#FFD400', text: '#FFD400' },
  low: { fill: '#F4761B', text: '#F4761B' },
  poor: { fill: '#CC2222', text: '#E85C50' },
}

const LIGHT: Record<HrvBand, { fill: string; text: string }> = {
  high: { fill: '#1E9045', text: '#1A7B3B' },
  good: { fill: '#3B9C21', text: '#2E7A1A' },
  mid: { fill: '#9E8300', text: '#806A00' },
  low: { fill: '#E0640B', text: '#B04F08' },
  poor: { fill: '#CC2222', text: '#CC2222' },
}

const LABELS: Record<HrvBand, string> = { high: 'high', good: 'good', mid: 'mid', low: 'low', poor: 'poor' }

export function bandColors(theme: Theme): Record<HrvBand, { fill: string; text: string; label: string }> {
  const palette = theme === 'light' ? LIGHT : DARK
  return Object.fromEntries(
    Object.entries(palette).map(([band, colors]) => [band, { ...colors, label: LABELS[band as HrvBand] }]),
  ) as Record<HrvBand, { fill: string; text: string; label: string }>
}

// Back-compat default (dark) for any call site that hasn't threaded theme
// through yet.
export const BAND_COLORS = bandColors('dark')
