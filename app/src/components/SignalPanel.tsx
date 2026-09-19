import { useState } from 'react'
import type { SignalPanelCard } from '../lib/types'

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
      {cards.map((card) => {
        const isFlipped = flipped.has(card.id)
        return (
          <div className="signal-card" key={card.id}>
            <div className="flip-card">
              <button
                type="button"
                className={`flip-card-inner ${isFlipped ? 'flipped' : ''}`}
                onClick={() => toggle(card.id)}
                aria-pressed={isFlipped}
                aria-label={`${card.label}: ${isFlipped ? 'showing explanation, click to hide' : 'click to see why this is not a control'}`}
              >
                <div className="flip-card-face flip-card-front">
                  <h3>{card.label}</h3>
                  <span className="flip-card-hint">click to see why →</span>
                </div>
                <div className="flip-card-face flip-card-back">
                  <span className="flip-card-back-label">{card.label}</span>
                  <p>{card.text}</p>
                </div>
              </button>
            </div>
          </div>
        )
      })}
    </section>
  )
}
