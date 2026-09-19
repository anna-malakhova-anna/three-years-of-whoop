import { useEffect, useState } from 'react'
import type { PipelineData } from './types'

type LoadState =
  | { status: 'loading' }
  | { status: 'error'; error: string }
  | { status: 'ready'; data: PipelineData }

const FILES = ['quality', 'model', 'alcohol', 'bins', 'statements', 'drift', 'seasonality'] as const

export function usePipelineData(): LoadState {
  const [state, setState] = useState<LoadState>({ status: 'loading' })

  useEffect(() => {
    let cancelled = false
    const base = import.meta.env.BASE_URL

    Promise.all(
      FILES.map((name) =>
        fetch(`${base}data/${name}.json`).then((res) => {
          if (!res.ok) throw new Error(`${name}.json: HTTP ${res.status}`)
          return res.json()
        }),
      ),
    )
      .then(([quality, model, alcohol, bins, statements, drift, seasonality]) => {
        if (cancelled) return
        setState({ status: 'ready', data: { quality, model, alcohol, bins, statements, drift, seasonality } })
      })
      .catch((err: Error) => {
        if (cancelled) return
        setState({ status: 'error', error: err.message })
      })

    return () => {
      cancelled = true
    }
  }, [])

  return state
}
