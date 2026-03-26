import { afterEach, beforeEach, describe, expect, it, mock } from 'bun:test'
import {
  createCliRenderer,
  createJsonRenderer,
  createOutput,
  createRenderer,
  createSilentRenderer,
} from '../../src/ui/index'
import type { Renderer } from '../../src/ui/interface'

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const RENDERER_METHODS: (keyof Renderer)[] = [
  'table',
  'tree',
  'success',
  'error',
  'warn',
  'info',
  'ndjson',
  'progress',
  'raw',
]

// ---------------------------------------------------------------------------
// createRenderer factory
// ---------------------------------------------------------------------------

describe('createRenderer', () => {
  it('defaults to cli mode', () => {
    const r = createRenderer()
    expect(r).toBeDefined()
    // CLI renderer has all Renderer methods
    for (const m of RENDERER_METHODS) {
      expect(typeof r[m]).toBe('function')
    }
  })

  it('returns JsonRenderer for mode=json', () => {
    const r = createRenderer({ mode: 'json' })
    expect(r).toBeDefined()
    for (const m of RENDERER_METHODS) {
      expect(typeof r[m]).toBe('function')
    }
  })

  it('returns SilentRenderer for mode=silent', () => {
    const r = createRenderer({ mode: 'silent' })
    expect(r).toBeDefined()
    for (const m of RENDERER_METHODS) {
      expect(typeof r[m]).toBe('function')
    }
  })
})

// ---------------------------------------------------------------------------
// SilentRenderer
// ---------------------------------------------------------------------------

describe('SilentRenderer', () => {
  it('methods do not throw', () => {
    const r = createSilentRenderer()
    expect(() => r.table([{ a: 1 }])).not.toThrow()
    expect(() => r.tree('root', [{ label: 'child' }])).not.toThrow()
    expect(() => r.success('ok')).not.toThrow()
    expect(() => r.error('fail')).not.toThrow()
    expect(() => r.warn('caution')).not.toThrow()
    expect(() => r.info('fyi')).not.toThrow()
    expect(() => r.ndjson({ x: 1 })).not.toThrow()
    expect(() => r.raw('hello')).not.toThrow()
  })

  it('progress handle works without throwing', () => {
    const r = createSilentRenderer()
    const h = r.progress('loading...')
    expect(h).toBeDefined()
    expect(() => h.update({ text: 'still loading' })).not.toThrow()
    expect(() => h.success({ text: 'done' })).not.toThrow()
    expect(() => h.error({ text: 'oops' })).not.toThrow()
  })
})

// ---------------------------------------------------------------------------
// JsonRenderer
// ---------------------------------------------------------------------------

describe('JsonRenderer', () => {
  let logSpy: ReturnType<typeof mock>
  let errorSpy: ReturnType<typeof mock>

  beforeEach(() => {
    logSpy = mock(() => {})
    errorSpy = mock(() => {})
    console.log = logSpy as unknown as typeof console.log
    console.error = errorSpy as unknown as typeof console.error
  })

  afterEach(() => {
    // Restore originals (Bun resets between files anyway)
  })

  it('table outputs JSON to stdout', () => {
    const r = createJsonRenderer()
    r.table([{ a: 1 }])
    expect(logSpy).toHaveBeenCalledWith(JSON.stringify([{ a: 1 }]))
  })

  it('error outputs to stderr', () => {
    const r = createJsonRenderer()
    r.error('bad thing')
    expect(errorSpy).toHaveBeenCalledTimes(1)
    const arg = (errorSpy as ReturnType<typeof mock>).mock.calls[0][0]
    const parsed = JSON.parse(arg)
    expect(parsed.error).toBe('bad thing')
  })

  it('success with data outputs data to stdout', () => {
    const r = createJsonRenderer()
    r.success('done', { count: 42 })
    expect(logSpy).toHaveBeenCalledWith(JSON.stringify({ count: 42 }))
  })

  it('success without data outputs nothing', () => {
    const r = createJsonRenderer()
    r.success('done')
    expect(logSpy).not.toHaveBeenCalled()
  })

  it('ndjson outputs stringified line', () => {
    const r = createJsonRenderer()
    r.ndjson({ id: 1, name: 'test' })
    expect(logSpy).toHaveBeenCalledWith(JSON.stringify({ id: 1, name: 'test' }))
  })

  it('raw outputs stringified data', () => {
    const r = createJsonRenderer()
    r.raw({ hello: 'world' })
    expect(logSpy).toHaveBeenCalledWith(JSON.stringify({ hello: 'world' }))
  })

  it('progress returns noop handle', () => {
    const r = createJsonRenderer()
    const h = r.progress('loading')
    expect(h).toBeDefined()
    expect(() => h.update({ text: 'x' })).not.toThrow()
    expect(() => h.success()).not.toThrow()
    expect(() => h.error()).not.toThrow()
  })
})

// ---------------------------------------------------------------------------
// CliRenderer
// ---------------------------------------------------------------------------

describe('CliRenderer', () => {
  it('has progress method (renamed from spinner)', () => {
    const r = createCliRenderer({ quiet: true })
    expect(typeof r.progress).toBe('function')
    const h = r.progress('loading')
    expect(h).toBeDefined()
    expect(typeof h.update).toBe('function')
    expect(typeof h.success).toBe('function')
    expect(typeof h.error).toBe('function')
  })

  it('implements full Renderer interface', () => {
    const r = createCliRenderer()
    for (const m of RENDERER_METHODS) {
      expect(typeof r[m]).toBe('function')
    }
  })
})

// ---------------------------------------------------------------------------
// Backward compat
// ---------------------------------------------------------------------------

describe('backward compatibility', () => {
  it('createOutput is exported as alias', () => {
    expect(typeof createOutput).toBe('function')
  })

  it('createOutput returns renderer with spinner alias', () => {
    const o = createOutput({ json: false, quiet: true })
    expect(typeof o.spinner).toBe('function')
    expect(typeof o.progress).toBe('function')
    // spinner and progress should both work
    const h = o.spinner('test')
    expect(h).toBeDefined()
  })
})

// ---------------------------------------------------------------------------
// All renderers implement full interface
// ---------------------------------------------------------------------------

describe('interface compliance', () => {
  it.each([
    ['cli', () => createCliRenderer()],
    ['json', () => createJsonRenderer()],
    ['silent', () => createSilentRenderer()],
  ] as const)('%s renderer has all Renderer methods', (_name, factory) => {
    const r = factory()
    for (const m of RENDERER_METHODS) {
      expect(typeof r[m]).toBe('function')
    }
  })
})
