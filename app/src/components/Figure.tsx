// Original line-art figure — a running, forward-leaning pose inspired by
// image3.jpg's proportions and stance (front leg driving forward with a
// raised knee, trailing back leg, front arm bent toward the chin, back arm
// trailing). Generic stock-illustration reference, not a traced 1:1 copy —
// hand-built paths in the same spirit.
//
// viewBox is -40 -40 520 600 — see lib/figureAnchors.ts for anchor points
// in that same coordinate space.
import type { ConnectorWeights } from '../lib/figureAnchors'

// Ben-Day dot fill per HRV band — STYLE.md §4 diameter/pitch, but with hexes
// re-derived from the table's originals. The dots sit on the figure's own
// cream panel (--bubble-fill, constant in both themes — see the backdrop
// rect below), not on --ground, so STYLE.md's fill hexes (validated only
// against the dark ground, e.g. mid yellow at 1.2:1 here) don't apply
// as-is. These are darkened, same-hue versions, each re-verified to clear
// 3:1 against #F2EDE4.
const DOT_BANDS: { id: string; fill: string; diameter: number; pitch: number }[] = [
  { id: 'dot-high', fill: '#1E9045', diameter: 2, pitch: 14 },
  { id: 'dot-good', fill: '#3B9C21', diameter: 3, pitch: 12 },
  { id: 'dot-mid', fill: '#9E8300', diameter: 4, pitch: 10 },
  { id: 'dot-low', fill: '#E0640B', diameter: 5, pitch: 8 },
  { id: 'dot-poor', fill: '#CC2222', diameter: 6, pitch: 6 },
]

function Connector({ x1, y1, x2, y2, weight }: { x1: number; y1: number; x2: number; y2: number; weight: number }) {
  const w = Math.max(weight, 0.05)
  const blackWidth = 2 + w * 3.5
  const accentWidth = 1 + w * 1.6
  return (
    <g>
      <line x1={x1} y1={y1} x2={x2} y2={y2} stroke="var(--ink)" strokeWidth={blackWidth} strokeLinecap="round" />
      <line
        x1={x1}
        y1={y1}
        x2={x2}
        y2={y2}
        stroke="var(--accent-text)"
        strokeWidth={accentWidth}
        strokeLinecap="round"
      />
    </g>
  )
}

export function Figure({ weights }: { weights?: ConnectorWeights }) {
  return (
    <svg
      viewBox="-40 -40 520 600"
      className="figure-svg"
      role="img"
      aria-label="Line-art figure of a runner, mid-stride, used as anchors for the surrounding controls"
    >
      <defs>
        {DOT_BANDS.map((band) => (
          <pattern
            key={band.id}
            id={band.id}
            width={band.pitch}
            height={band.pitch}
            patternUnits="userSpaceOnUse"
          >
            <circle cx={band.pitch / 2} cy={band.pitch / 2} r={band.diameter / 2} fill={band.fill} />
          </pattern>
        ))}
      </defs>

      {/* The figure gets its own light comic-panel backdrop — black contour
          lines stay black per spec, which only reads on a light ground.
          The dark page ground is the gutter; this panel is "raised" on it,
          same as every other panel on the page (STYLE.md §2.1). */}
      <rect x={62} y={28} width={340} height={448} rx={8} fill="var(--bubble-fill)" stroke="var(--rule)" strokeWidth={4} />

      {weights && (
        <g>
          <Connector x1={320} y1={54} x2={230} y2={-20} weight={weights.sleep_hours} />
          <Connector x1={135} y1={222} x2={20} y2={260} weight={weights.sleep_consistency_pct} />
          <Connector x1={334} y1={70} x2={430} y2={-10} weight={weights.prior_day_strain} />
          <Connector x1={288} y1={292} x2={420} y2={310} weight={weights.alcohol} />
        </g>
      )}

      <g fill="none" stroke="var(--ink)" strokeWidth={7} strokeLinecap="round" strokeLinejoin="round">
        <circle cx={320} cy={80} r={30} fill="var(--bubble-fill)" />
        <path d="M300,106 L284,132" />
        <path
          className="figure-torso"
          d="M284,132
             C260,150 236,175 220,212
             C206,246 202,282 210,312
             L262,322
             C282,290 292,252 288,214
             C284,178 282,152 284,132 Z"
          stroke="var(--ink)"
        />
        {/* front arm: bent up near chin */}
        <path d="M278,148 C306,136 326,112 328,84" />
        <circle cx={328} cy={84} r={7} fill="var(--ink)" stroke="none" />
        {/* back arm: trailing down and back */}
        <path d="M230,178 C196,186 164,196 145,218" />
        <circle cx={145} cy={218} r={7} fill="var(--ink)" stroke="none" />
        {/* front leg: thigh drives forward, shin bends back under */}
        <path d="M245,312 C288,320 330,328 355,332 C372,320 368,286 340,262 C328,252 314,248 304,250" />
        <circle cx={304} cy={250} r={7} fill="var(--ink)" stroke="none" />
        {/* back leg: extends back and down, trailing */}
        <path d="M215,315 C190,345 168,378 152,412 C143,430 140,445 148,455" />
        <circle cx={148} cy={455} r={7} fill="var(--ink)" stroke="none" />
      </g>
    </svg>
  )
}
