import type { Statement } from '../lib/types'

export function SpeechBubble({ statement }: { statement: Statement | undefined }) {
  if (!statement) return null
  const lowConfidence = statement.confidence === 'low'
  return (
    <div
      key={statement.id}
      className={`speech-bubble speech-bubble-enter ${lowConfidence ? 'low-confidence' : ''}`}
    >
      <p>{statement.text}</p>
      <div className="speech-bubble-footer">
        n={statement.n} · {statement.confidence} confidence
      </div>
    </div>
  )
}
