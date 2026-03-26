export interface Counter {
  inc(value?: number): void
}
export interface Histogram {
  observe(value: number): void
}

export interface Metrics {
  counter(name: string, tags?: Record<string, string>): Counter
  histogram(name: string, tags?: Record<string, string>): Histogram
}

const noopCounter: Counter = { inc() {} }
const noopHistogram: Histogram = { observe() {} }

export function createNoopMetrics(): Metrics {
  return { counter: () => noopCounter, histogram: () => noopHistogram }
}
