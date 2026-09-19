// Original line-art figure. Proportions and the raised-arm, wide-stance
// pose are inspired by the working directory's image.jpg reference (per
// project decision: pose/proportions only — no costume, hair, weapon, or
// other character-identifying details were traced).
//
// viewBox is -80 -60 480 700 — see lib/figureAnchors.ts for anchor points
// in that same coordinate space.
import type { ConnectorWeights } from '../lib/figureAnchors'

function Connector({ x1, y1, x2, y2, weight }: { x1: number; y1: number; x2: number; y2: number; weight: number }) {
  const w = Math.max(weight, 0.05)
  return (
    <line
      x1={x1}
      y1={y1}
      x2={x2}
      y2={y2}
      stroke="var(--connector)"
      strokeWidth={1 + w * 4.5}
      strokeOpacity={0.22 + w * 0.68}
      strokeLinecap="round"
      strokeDasharray="1 7"
    />
  )
}

export function Figure({ weights }: { weights?: ConnectorWeights }) {
  return (
    <svg
      viewBox="-80 -60 480 700"
      className="figure-svg"
      role="img"
      aria-label="Line-art human figure, arms and legs used as anchors for the surrounding controls"
    >
      {weights && (
        <g>
          <Connector x1={163} y1={24} x2={90} y2={-40} weight={weights.sleep_hours} />
          <Connector x1={60} y1={196} x2={-60} y2={240} weight={weights.sleep_consistency_pct} />
          <Connector x1={244} y1={18} x2={340} y2={-44} weight={weights.prior_day_strain} />
          <Connector x1={202} y1={205} x2={320} y2={205} weight={weights.alcohol} />
        </g>
      )}
      <g
        fill="none"
        stroke="currentColor"
        strokeWidth={5}
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        <ellipse cx={163} cy={50} rx={22} ry={26} />
        <path d="M163,76 L163,92" />
        <path
          d="M118,98
             C106,128 114,158 132,180
             C122,202 120,224 126,242
             L200,242
             C206,224 204,202 194,180
             C212,158 220,128 208,98
             C192,90 134,90 118,98 Z"
        />
        <path d="M204,102 C226,88 234,62 226,26" />
        <circle cx={226} cy={26} r={6} fill="currentColor" stroke="none" />
        <path d="M122,102 C96,120 82,148 82,182" />
        <circle cx={82} cy={182} r={6} fill="currentColor" stroke="none" />
        <path d="M132,242 C112,290 96,340 88,398 C85,414 85,428 88,438 L124,438" />
        <circle cx={124} cy={438} r={6} fill="currentColor" stroke="none" />
        <path d="M194,242 C214,286 232,332 244,388 C248,406 246,422 238,434 L274,440" />
        <circle cx={274} cy={440} r={6} fill="currentColor" stroke="none" />
      </g>
    </svg>
  )
}
