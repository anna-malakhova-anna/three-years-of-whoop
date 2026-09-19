import type { HrvBand } from '../lib/bands'

export function HeadlineNumber({ hrv, recovery, band }: { hrv: number; recovery: number; band: HrvBand }) {
  return (
    <div className="headline-number">
      {/* Dot density is the non-color channel for the band (STYLE.md §4) —
          kept as its own swatch rather than behind the number text, since
          the dense bands' dots nearly touch and would wreck text contrast
          if the number sat on top of them. */}
      <div className="band-swatch" aria-hidden="true" />
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
