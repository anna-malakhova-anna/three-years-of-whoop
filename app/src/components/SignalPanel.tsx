import { useLayoutEffect, useRef, useState } from 'react'
import type { SignalPanelCard } from '../lib/types'

function FlipCard({
  card,
  isFlipped,
  onToggle,
}: {
  card: SignalPanelCard
  isFlipped: boolean
  onToggle: () => void
}) {
  const frontRef = useRef<HTMLDivElement>(null)
  const backRef = useRef<HTMLDivElement>(null)
  const [frontHeight, setFrontHeight] = useState<number>()
  const [backHeight, setBackHeight] = useState<number>()

  useLayoutEffect(() => {
    function measure() {
      // scrollHeight reads the content's natural height even though both
      // faces are position:absolute/inset:0 (stacked, so they'd otherwise
      // just report the parent's current height back at us).
      if (frontRef.current) setFrontHeight(frontRef.current.scrollHeight)
      if (backRef.current) setBackHeight(backRef.current.scrollHeight)
    }
    measure()
    window.addEventListener('resize', measure)
    return () => window.removeEventListener('resize', measure)
  }, [card.text])

  const height = isFlipped ? backHeight : frontHeight

  return (
    <div className="flip-card">
      <button
        type="button"
        className={`flip-card-inner ${isFlipped ? 'flipped' : ''}`}
        style={height ? { height } : undefined}
        onClick={onToggle}
        aria-pressed={isFlipped}
        aria-label={`${card.label}: ${isFlipped ? 'showing explanation, click to hide' : 'click to see why this is not a control'}`}
      >
        <div className="flip-card-face flip-card-front" ref={frontRef}>
          <h3>{card.label}</h3>
          <span className="flip-card-hint">click to see why →</span>
        </div>
        <div className="flip-card-face flip-card-back" ref={backRef}>
          <span className="flip-card-back-label">{card.label}</span>
          <p>{card.text}</p>
        </div>
      </button>
    </div>
  )
}

export function SignalPanel({ cards }: { cards: SignalPanelCard[] }) {
  const [flipped, setFlipped] = useState<Set<string>>(new Set())

  function toggle(id: string) {
    setFlipped((prev) => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }

  return (
    <section className="signal-panel" aria-label="Signal, not lever">
      <h2>Signal, not lever</h2>
      <p className="section-subtitle">
        Strong predictors that aren't controls here — you can't decide to lower your resting
        heart rate any more than you can decide to breathe slower. Read-only. Click a title to
        see why.
      </p>
      {cards.map((card) => (
        <div className="signal-card" key={card.id}>
          <FlipCard card={card} isFlipped={flipped.has(card.id)} onToggle={() => toggle(card.id)} />
        </div>
      ))}
    </section>
  )
}
