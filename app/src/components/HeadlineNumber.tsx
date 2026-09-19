import type { HrvBand } from '../lib/bands'

// 9 dots, arranged as a heart (x%, y% within the swatch box). Same count as
// the swatch's old tiled grid — just a shape instead of a lattice.
const HEART_DOTS: [number, number][] = [
  [28, 16],
  [72, 16],
  [10, 38],
  [50, 32],
  [90, 38],
  [25, 58],
  [75, 58],
  [50, 72],
  [50, 90],
]

export function HeadlineNumber({ hrv, recovery, band }: { hrv: number; recovery: number; band: HrvBand }) {
  return (
    <div className="headline-number">
      {/* Dot density is the non-color channel for the band (STYLE.md §4) —
          kept as its own swatch rather than behind the number text, since
          the dense bands' dots nearly touch and would wreck text contrast
          if the number sat on top of them. */}
      <div className="band-swatch" aria-hidden="true">
        {HEART_DOTS.map(([x, y], i) => (
          <span key={i} className="heart-dot" style={{ left: `${x}%`, top: `${y}%` }} />
        ))}
      </div>
      <div className="headline-text">
        <div className="hrv-value">
          <span className="hrv-figure">{Math.round(hrv)}</span>
          <span className="hrv-unit">ms HRV</span>
        </div>
        <div className="recovery-value">
          {Math.round(recovery)}% recovery · {band}
        </div>
      </div>
    </div>
  )
}
