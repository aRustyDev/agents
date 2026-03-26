import { describe, expect, it } from 'bun:test'
import { SdkError } from '../../src/util/errors'

describe('SdkError', () => {
  it('extends Error', () => {
    const err = new SdkError('boom', 'E_PROVIDER_UNAVAILABLE')
    expect(err).toBeInstanceOf(Error)
    expect(err).toBeInstanceOf(SdkError)
  })

  it('has code and detail', () => {
    const err = new SdkError('not found', 'E_COMPONENT_NOT_FOUND', 'skill/foo')
    expect(err.code).toBe('E_COMPONENT_NOT_FOUND')
    expect(err.detail).toBe('skill/foo')
    expect(err.name).toBe('SdkError')
    expect(err.message).toBe('not found')
  })

  it('display() includes detail when present', () => {
    const err = new SdkError('parse error', 'E_PARSE_FRONTMATTER', 'line 5')
    expect(err.display()).toBe('parse error: line 5')
  })

  it('display() works without detail', () => {
    const err = new SdkError('timeout', 'E_PROVIDER_TIMEOUT')
    expect(err.display()).toBe('timeout')
    expect(err.detail).toBeUndefined()
  })
})
