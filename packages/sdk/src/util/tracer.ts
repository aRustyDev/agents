export interface Span {
  setAttribute(key: string, value: unknown): void
  end(): void
}

export interface Tracer {
  startSpan(name: string, attrs?: Record<string, unknown>): Span
}

const noopSpan: Span = { setAttribute() {}, end() {} }

export function createNoopTracer(): Tracer {
  return { startSpan: () => noopSpan }
}
