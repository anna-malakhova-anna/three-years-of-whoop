export function HeadlineNumber({ hrv, recovery }: { hrv: number; recovery: number }) {
  return (
    <div className="headline-number">
      <div className="hrv-value">
        <span className="hrv-figure">{Math.round(hrv)}</span>
        <span className="hrv-unit">ms HRV</span>
      </div>
      <div className="recovery-value">{Math.round(recovery)}% recovery</div>
    </div>
  )
}
