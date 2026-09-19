import { useState } from 'react'
import { FlipCard } from './FlipCard'
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
      {cards.map((card) => (
        <div className="signal-card" key={card.id}>
          <FlipCard
            label={card.label}
            backText={card.text}
            ariaContext="this is not a control"
            isFlipped={flipped.has(card.id)}
            onToggle={() => toggle(card.id)}
          />
        </div>
      ))}
    </section>
  )
}
