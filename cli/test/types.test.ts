import { describe, expect, test } from 'bun:test'
import { CliError, err, ok, type Result, tryAsync } from '../lib/types'

describe('Result', () => {
  test('ok() creates success result', () => {
    const result = ok(42)
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value).toBe(42)
    }
  })

  test('err() creates failure result', () => {
    const error = new CliError('failed', 'E_TEST')
    const result = err(error)
    expect(result.ok).toBe(false)
    if (!result.ok) {
      expect(result.error.code).toBe('E_TEST')
    }
  })

  test('type narrowing works after ok check', () => {
    const result: Result<string> = ok('hello')
    if (result.ok) {
      // TypeScript narrows to { ok: true, value: string }
      const val: string = result.value
      expect(val).toBe('hello')
    }
  })

  test('type narrowing works after not-ok check', () => {
    const result: Result<string> = err(new CliError('bad', 'E_BAD'))
    if (!result.ok) {
      // TypeScript narrows to { ok: false, error: CliError }
      const e: CliError = result.error
      expect(e.message).toBe('bad')
    }
  })
})

describe('CliError', () => {
  test('display() formats error with code', () => {
    const e = new CliError('Something broke', 'E_BROKEN')
    expect(e.display()).toBe('error[E_BROKEN]: Something broke')
  })

  test('display() includes hint when present', () => {
    const e = new CliError('File not found', 'E_NOT_FOUND', 'Check the path exists')
    expect(e.display()).toBe('error[E_NOT_FOUND]: File not found\n  hint: Check the path exists')
  })

  test('display() omits hint when absent', () => {
    const e = new CliError('Oops', 'E_OOPS')
    expect(e.display()).not.toContain('hint')
  })

  test('preserves cause', () => {
    const cause = new Error('original')
    const e = new CliError('Wrapped', 'E_WRAP', undefined, cause)
    expect(e.cause).toBe(cause)
  })
})

describe('tryAsync', () => {
  test('wraps successful async into ok()', async () => {
    const result = await tryAsync(
      async () => 'success',
      (e) => new CliError('fail', 'E_FAIL')
    )
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value).toBe('success')
    }
  })

  test('wraps thrown error into err()', async () => {
    const result = await tryAsync(
      async () => {
        throw new Error('boom')
      },
      (e) => new CliError(`caught: ${e}`, 'E_CAUGHT')
    )
    expect(result.ok).toBe(false)
    if (!result.ok) {
      expect(result.error.code).toBe('E_CAUGHT')
      expect(result.error.message).toContain('boom')
    }
  })

  test('passes thrown value to mapError', async () => {
    const original = new Error('original message')
    const result = await tryAsync(
      async () => {
        throw original
      },
      (e) => new CliError('mapped', 'E_MAP', undefined, e)
    )
    expect(result.ok).toBe(false)
    if (!result.ok) {
      expect(result.error.cause).toBe(original)
    }
  })
})
