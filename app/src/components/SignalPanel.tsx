import type { SignalPanelCard } from '../lib/types'

export function SignalPanel({ cards }: { cards: SignalPanelCard[] }) {
  return (
    <section className="signal-panel" aria-label="Signal, not lever">
      <h2>Signal, not lever</h2>
      <p className="section-subtitle">
        Strong predictors that aren't controls here — you can't decide to lower your resting
        heart rate any more than you can decide to breathe slower. Read-only.
      </p>
      {cards.map((card) => (
        <div className="signal-card" key={card.id}>
          <h3>{card.label}</h3>
          <p>{card.text}</p>
        </div>
      ))}
    </section>
  )
}
