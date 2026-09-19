import { ConfidenceDot } from './Slider'
import type { Statement } from '../lib/types'

export function SpeechBubble({ statement }: { statement: Statement | undefined }) {
  if (!statement) return null
  return (
    <div className="speech-bubble">
      <ConfidenceDot confidence={statement.confidence} />
      <p>{statement.text}</p>
    </div>
  )
}
