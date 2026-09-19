import { useLayoutEffect, useRef, useState } from 'react'

export function FlipCard({
  label,
  backLabel,
  backText,
  hint = 'click to see why →',
  ariaContext = 'this',
  isFlipped,
  onToggle,
}: {
  label: string
  backLabel?: string
  backText: string
  hint?: string
  ariaContext?: string
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
  }, [backText])

  const height = isFlipped ? backHeight : frontHeight

  return (
    <div className="flip-card">
      <button
        type="button"
        className={`flip-card-inner ${isFlipped ? 'flipped' : ''}`}
        style={height ? { height } : undefined}
        onClick={onToggle}
        aria-pressed={isFlipped}
        aria-label={`${label}: ${isFlipped ? 'showing explanation, click to hide' : `click to see why ${ariaContext}`}`}
      >
        <div className="flip-card-face flip-card-front" ref={frontRef}>
          <h3>{label}</h3>
          <span className="flip-card-hint">{hint}</span>
        </div>
        <div className="flip-card-face flip-card-back" ref={backRef}>
          <span className="flip-card-back-label">{backLabel ?? label}</span>
          <p>{backText}</p>
        </div>
      </button>
    </div>
  )
}
