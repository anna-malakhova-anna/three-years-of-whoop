import type { HrvBand } from '../lib/figureAnchors'

export function HeadlineNumber({ hrv, recovery, band }: { hrv: number; recovery: number; band: HrvBand }) {
  return (
    <div className="headline-number">
      <div className="hrv-value">
        <span className="hrv-figure">{Math.round(hrv)}</span>
        <span className="hrv-unit">ms HRV</span>
      </div>
      <div className="recovery-value">
        {Math.round(recovery)}% recovery · {band}
      </div>
    </div>
  )
}
