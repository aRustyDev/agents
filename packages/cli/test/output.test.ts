import { describe, expect, test } from 'bun:test'
import type { OutputFormatter, SpinnerHandle } from '@agents/core/output'
import { createOutput } from '@agents/core/output'

// ---------------------------------------------------------------------------
// Capture helper
// ---------------------------------------------------------------------------

function captureOutput(fn: () => void): { stdout: string; stderr: string } {
  const originalLog = console.log
  const originalError = console.error
  let stdout = ''
  let stderr = ''
  console.log = (...args: unknown[]) => {
    stdout += args.map(String).join(' ') + '\n'
  }
  console.error = (...args: unknown[]) => {
    stderr += args.map(String).join(' ') + '\n'
  }
  try {
    fn()
  } finally {
    console.log = originalLog
    console.error = originalError
  }
  return { stdout, stderr }
}

// ---------------------------------------------------------------------------
// JSON mode
// ---------------------------------------------------------------------------

describe('JSON mode', () => {
  let out: OutputFormatter

  test('success produces valid JSON with status field', () => {
    out = createOutput({ json: true, quiet: false })
    const { stdout } = captureOutput(() => out.success('all good'))
    const parsed = JSON.parse(stdout.trim())
    expect(parsed).toEqual({ status: 'success', message: 'all good' })
  })

  test('success includes data when provided', () => {
    out = createOutput({ json: true, quiet: false })
    const { stdout } = captureOutput(() => out.success('done', { count: 42 }))
    const parsed = JSON.parse(stdout.trim())
    expect(parsed).toEqual({ status: 'success', message: 'done', data: { count: 42 } })
  })

  test('error produces valid JSON with status "error"', () => {
    out = createOutput({ json: true, quiet: false })
    const { stderr } = captureOutput(() => out.error('something broke'))
    const parsed = JSON.parse(stderr.trim())
    expect(parsed).toEqual({ status: 'error', message: 'something broke' })
  })

  test('error includes data when provided', () => {
    out = createOutput({ json: true, quiet: false })
    const { stderr } = captureOutput(() => out.error('fail', { code: 'E001' }))
    const parsed = JSON.parse(stderr.trim())
    expect(parsed).toEqual({ status: 'error', message: 'fail', data: { code: 'E001' } })
  })

  test('warn produces valid JSON with status "warning" on stderr', () => {
    out = createOutput({ json: true, quiet: false })
    const { stderr } = captureOutput(() => out.warn('careful'))
    const parsed = JSON.parse(stderr.trim())
    expect(parsed).toEqual({ status: 'warning', message: 'careful' })
  })

  test('info produces valid JSON with status "info" on stdout', () => {
    out = createOutput({ json: true, quiet: false })
    const { stdout } = captureOutput(() => out.info('fyi'))
    const parsed = JSON.parse(stdout.trim())
    expect(parsed).toEqual({ status: 'info', message: 'fyi' })
  })

  test('table produces a JSON array', () => {
    out = createOutput({ json: true, quiet: false })
    const data = [
      { name: 'alice', age: 30 },
      { name: 'bob', age: 25 },
    ]
    const { stdout } = captureOutput(() => out.table(data))
    const parsed = JSON.parse(stdout.trim())
    expect(parsed).toEqual(data)
  })

  test('table with columns filters to specified columns', () => {
    out = createOutput({ json: true, quiet: false })
    const data = [
      { name: 'alice', age: 30, email: 'a@b.com' },
      { name: 'bob', age: 25, email: 'b@c.com' },
    ]
    const { stdout } = captureOutput(() => out.table(data, ['name', 'age']))
    const parsed = JSON.parse(stdout.trim())
    expect(parsed).toEqual([
      { name: 'alice', age: 30 },
      { name: 'bob', age: 25 },
    ])
  })

  test('tree produces nested JSON structure', () => {
    out = createOutput({ json: true, quiet: false })
    const children = [
      { label: 'child-a', children: [{ label: 'grandchild' }] },
      { label: 'child-b' },
    ]
    const { stdout } = captureOutput(() => out.tree('root', children))
    const parsed = JSON.parse(stdout.trim())
    expect(parsed).toEqual({ label: 'root', children })
  })

  test('ndjson produces one line per call without pretty-printing', () => {
    out = createOutput({ json: true, quiet: false })
    const { stdout } = captureOutput(() => {
      out.ndjson({ id: 1, name: 'first' })
      out.ndjson({ id: 2, name: 'second' })
    })
    const lines = stdout.trim().split('\n')
    expect(lines).toHaveLength(2)
    expect(JSON.parse(lines[0]!)).toEqual({ id: 1, name: 'first' })
    expect(JSON.parse(lines[1]!)).toEqual({ id: 2, name: 'second' })
    // Verify no pretty-printing (no indentation)
    expect(lines[0]).not.toContain('\n')
    expect(lines[0]).not.toContain('  ')
  })

  test('raw produces JSON output', () => {
    out = createOutput({ json: true, quiet: false })
    const { stdout } = captureOutput(() => out.raw({ key: 'value' }))
    const parsed = JSON.parse(stdout.trim())
    expect(parsed).toEqual({ key: 'value' })
  })

  test('spinner returns a no-op handle', () => {
    out = createOutput({ json: true, quiet: false })
    const { stdout, stderr } = captureOutput(() => {
      const handle = out.spinner('loading...')
      handle.update({ text: 'still loading...' })
      handle.success({ text: 'done!' })
    })
    // Should produce no output
    expect(stdout).toBe('')
    expect(stderr).toBe('')
  })
})

// ---------------------------------------------------------------------------
// Human mode
// ---------------------------------------------------------------------------

describe('Human mode', () => {
  let out: OutputFormatter

  test('success contains [ok] prefix on stdout', () => {
    out = createOutput({ json: false, quiet: false })
    const { stdout } = captureOutput(() => out.success('completed'))
    expect(stdout).toContain('[ok]')
    expect(stdout).toContain('completed')
  })

  test('error contains [error] prefix on stderr', () => {
    out = createOutput({ json: false, quiet: false })
    const { stderr } = captureOutput(() => out.error('failed'))
    expect(stderr).toContain('[error]')
    expect(stderr).toContain('failed')
  })

  test('warn contains [warn] prefix on stderr', () => {
    out = createOutput({ json: false, quiet: false })
    const { stderr } = captureOutput(() => out.warn('watch out'))
    expect(stderr).toContain('[warn]')
    expect(stderr).toContain('watch out')
  })

  test('info contains [info] prefix on stdout', () => {
    out = createOutput({ json: false, quiet: false })
    const { stdout } = captureOutput(() => out.info('note'))
    expect(stdout).toContain('[info]')
    expect(stdout).toContain('note')
  })

  test('error goes to stderr, not stdout', () => {
    out = createOutput({ json: false, quiet: false })
    const { stdout, stderr } = captureOutput(() => out.error('bad'))
    expect(stderr).toContain('bad')
    expect(stdout).toBe('')
  })

  test('warn goes to stderr, not stdout', () => {
    out = createOutput({ json: false, quiet: false })
    const { stdout, stderr } = captureOutput(() => out.warn('caution'))
    expect(stderr).toContain('caution')
    expect(stdout).toBe('')
  })

  test('success goes to stdout, not stderr', () => {
    out = createOutput({ json: false, quiet: false })
    const { stdout, stderr } = captureOutput(() => out.success('ok'))
    expect(stdout).toContain('ok')
    expect(stderr).toBe('')
  })

  test('info goes to stdout, not stderr', () => {
    out = createOutput({ json: false, quiet: false })
    const { stdout, stderr } = captureOutput(() => out.info('fyi'))
    expect(stdout).toContain('fyi')
    expect(stderr).toBe('')
  })

  test('tree renders label in output', () => {
    out = createOutput({ json: false, quiet: false })
    const { stdout } = captureOutput(() =>
      out.tree('my-tree', [
        { label: 'branch-a', children: [{ label: 'leaf-1' }] },
        { label: 'branch-b' },
      ])
    )
    expect(stdout).toContain('my-tree')
    expect(stdout).toContain('branch-a')
    expect(stdout).toContain('leaf-1')
    expect(stdout).toContain('branch-b')
  })

  test('tree uses box-drawing characters', () => {
    out = createOutput({ json: false, quiet: false })
    const { stdout } = captureOutput(() =>
      out.tree('root', [{ label: 'first' }, { label: 'last' }])
    )
    // Non-last children use ├──, last child uses └──
    expect(stdout).toContain('\u251c\u2500\u2500')
    expect(stdout).toContain('\u2514\u2500\u2500')
  })

  test('ndjson is a no-op', () => {
    out = createOutput({ json: false, quiet: false })
    const { stdout, stderr } = captureOutput(() => out.ndjson({ id: 1 }))
    expect(stdout).toBe('')
    expect(stderr).toBe('')
  })

  test('raw outputs data directly', () => {
    out = createOutput({ json: false, quiet: false })
    const { stdout } = captureOutput(() => out.raw('hello world'))
    expect(stdout).toContain('hello world')
  })

  test('table does not throw', () => {
    out = createOutput({ json: false, quiet: false })
    expect(() => {
      captureOutput(() => out.table([{ name: 'test', value: 1 }]))
    }).not.toThrow()
  })
})

// ---------------------------------------------------------------------------
// Quiet mode
// ---------------------------------------------------------------------------

describe('Quiet mode', () => {
  let out: OutputFormatter

  test('success is suppressed in human mode', () => {
    out = createOutput({ json: false, quiet: true })
    const { stdout, stderr } = captureOutput(() => out.success('should not appear'))
    expect(stdout).toBe('')
    expect(stderr).toBe('')
  })

  test('info is suppressed in human mode', () => {
    out = createOutput({ json: false, quiet: true })
    const { stdout, stderr } = captureOutput(() => out.info('should not appear'))
    expect(stdout).toBe('')
    expect(stderr).toBe('')
  })

  test('error is NOT suppressed in quiet mode', () => {
    out = createOutput({ json: false, quiet: true })
    const { stderr } = captureOutput(() => out.error('still visible'))
    expect(stderr).toContain('still visible')
  })

  test('warn is NOT suppressed in quiet mode', () => {
    out = createOutput({ json: false, quiet: true })
    const { stderr } = captureOutput(() => out.warn('still visible'))
    expect(stderr).toContain('still visible')
  })

  test('spinner returns no-op handle', () => {
    out = createOutput({ json: false, quiet: true })
    const handle: SpinnerHandle = out.spinner('loading')
    expect(() => {
      handle.update({ text: 'updating' })
      handle.success({ text: 'done' })
    }).not.toThrow()
  })

  test('spinner error method does not throw', () => {
    out = createOutput({ json: false, quiet: true })
    const handle = out.spinner('working')
    expect(() => handle.error({ text: 'failed' })).not.toThrow()
  })
})

// ---------------------------------------------------------------------------
// Spinner handle contract
// ---------------------------------------------------------------------------

describe('Spinner handle', () => {
  test('JSON mode spinner has success/error/update methods', () => {
    const out = createOutput({ json: true, quiet: false })
    const handle = out.spinner('test')
    expect(typeof handle.success).toBe('function')
    expect(typeof handle.error).toBe('function')
    expect(typeof handle.update).toBe('function')
  })

  test('calling spinner methods without options does not throw', () => {
    const out = createOutput({ json: true, quiet: false })
    const handle = out.spinner('test')
    expect(() => {
      handle.success()
      handle.error()
      handle.update({ text: 'x' })
    }).not.toThrow()
  })
})
