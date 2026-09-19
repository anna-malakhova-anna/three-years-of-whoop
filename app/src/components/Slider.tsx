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

export function ConfidenceDot({ confidence }: { confidence: Confidence }) {
  return <span className={`confidence-dot confidence-${confidence}`} title={`${confidence} confidence`} />
}

export function Slider({ id, label, value, min, max, step, unit, confidence, onChange }: SliderProps) {
  return (
    <div className={`control-card confidence-border-${confidence}`}>
      <div className="control-card-header">
        <label htmlFor={id}>{label}</label>
        <ConfidenceDot confidence={confidence} />
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
