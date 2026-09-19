import { ConfidenceDot } from './Slider'
import type { Confidence } from '../lib/types'

interface ToggleProps {
  id: string
  label: string
  checked: boolean
  confidence: Confidence
  onChange: (value: boolean) => void
}

export function Toggle({ id, label, checked, confidence, onChange }: ToggleProps) {
  return (
    <div className={`control-card confidence-border-${confidence}`}>
      <div className="control-card-header">
        <label htmlFor={id}>{label}</label>
        <ConfidenceDot confidence={confidence} />
      </div>
      <button
        id={id}
        type="button"
        role="switch"
        aria-checked={checked}
        className={`toggle-switch ${checked ? 'on' : 'off'}`}
        onClick={() => onChange(!checked)}
      >
        <span className="toggle-thumb" />
      </button>
      <div className="control-value">{checked ? 'Yes' : 'No'}</div>
    </div>
  )
}
