import type { Confidence } from '../lib/types'

interface SliderProps {
  id: string
  label: string
  value: number
  min: number
  max: number
  step: number
  unit: string
  confidence: Confidence
  onChange: (value: number) => void
}

const BADGE_TEXT: Record<Confidence, string> = { high: 'high', medium: 'med', low: 'low' }
const BORDER_CLASS: Record<Confidence, string> = {
  high: '',
  medium: 'confidence-dashed',
  low: 'confidence-dotted',
}

export function ConfidenceBadge({ confidence }: { confidence: Confidence }) {
  return (
    <span className={`confidence-badge confidence-${confidence}`} title={`${confidence} confidence`}>
      {BADGE_TEXT[confidence]}
    </span>
  )
}

export function confidenceBorderClass(confidence: Confidence): string {
  return BORDER_CLASS[confidence]
}

export function Slider({ id, label, value, min, max, step, unit, confidence, onChange }: SliderProps) {
  return (
    <div className={`control-card ${confidenceBorderClass(confidence)}`}>
      <div className="control-card-header">
        <label htmlFor={id}>{label}</label>
        <ConfidenceBadge confidence={confidence} />
      </div>
      <input
        id={id}
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
      />
      <div className="control-value">
        {value}
        {unit}
      </div>
    </div>
  )
}
