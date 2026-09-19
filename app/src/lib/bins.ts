// Mirrors the bin edges in pipeline/bins.py exactly. Kept here (not derived
// from bins.json) because bins.json carries the computed stats per bin, not
// the edges themselves — the edges are the one piece of binning logic that
// has to be duplicated between Python and TS. If you change the edges in
// bins.py, change them here too.

export const SLEEP_HOURS_EDGES = [0, 5, 6, 6.5, 7, 7.5, 8, 8.5, 9, 100]
export const SLEEP_HOURS_LABELS = ['<=5h', '5-6h', '6-6.5h', '6.5-7h', '7-7.5h', '7.5-8h', '8-8.5h', '8.5-9h', '9h+']

export const STRAIN_EDGES = [-1, 6, 9, 12, 15, 100]
export const STRAIN_LABELS = ['0-6', '6-9', '9-12', '12-15', '15+']

export const CONSISTENCY_EDGES = [0, 50, 60, 70, 80, 90, 100]
export const CONSISTENCY_LABELS = ['<50', '50-60', '60-70', '70-80', '80-90', '90-100']

/** Right-inclusive bin lookup, matching pandas.cut(right=True, include_lowest=True). */
export function binLabelFor(value: number, edges: number[], labels: string[]): string {
  for (let i = 0; i < labels.length; i++) {
    const lower = edges[i]
    const upper = edges[i + 1]
    if (value <= upper && (value > lower || i === 0)) return labels[i]
  }
  return labels[labels.length - 1]
}
