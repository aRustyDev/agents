import { describe, expect, it } from 'bun:test'
import { createLogger, type LogEntry, type LogSink } from '../../src/util/logger'

function collectingSink(): LogSink & { entries: LogEntry[] } {
  const entries: LogEntry[] = []
  return {
    entries,
    write(entry) {
      entries.push(entry)
    },
  }
}

describe('createLogger', () => {
  it('logs at info level by default', () => {
    const sink = collectingSink()
    const logger = createLogger({ sink })

    logger.info('hello')

    expect(sink.entries).toHaveLength(1)
    expect(sink.entries[0].level).toBe('info')
    expect(sink.entries[0].message).toBe('hello')
  })

  it('respects log level filter — debug filtered when level=info', () => {
    const sink = collectingSink()
    const logger = createLogger({ level: 'info', sink })

    logger.debug('should be filtered')
    logger.info('should appear')

    expect(sink.entries).toHaveLength(1)
    expect(sink.entries[0].message).toBe('should appear')
  })

  it('respects log level filter — debug and info filtered when level=warn', () => {
    const sink = collectingSink()
    const logger = createLogger({ level: 'warn', sink })

    logger.debug('no')
    logger.info('no')
    logger.warn('yes')
    logger.error('yes')

    expect(sink.entries).toHaveLength(2)
    expect(sink.entries[0].level).toBe('warn')
    expect(sink.entries[1].level).toBe('error')
  })

  it('auto-fills timestamp', () => {
    const sink = collectingSink()
    const logger = createLogger({ sink })

    logger.info('timestamped')

    expect(sink.entries[0].timestamp).toBeDefined()
    // ISO 8601 format check
    expect(sink.entries[0].timestamp).toMatch(/^\d{4}-\d{2}-\d{2}T/)
  })

  it('fatal level works', () => {
    const sink = collectingSink()
    const logger = createLogger({ sink })

    logger.fatal('catastrophe', { exitCode: 1 })

    expect(sink.entries).toHaveLength(1)
    expect(sink.entries[0].level).toBe('fatal')
    expect(sink.entries[0].message).toBe('catastrophe')
    expect(sink.entries[0].context).toEqual({ exitCode: 1 })
  })

  it('custom sink receives entries with context', () => {
    const sink = collectingSink()
    const logger = createLogger({ sink })

    logger.info('with context', { key: 'value', count: 42 })

    expect(sink.entries).toHaveLength(1)
    expect(sink.entries[0].context).toEqual({ key: 'value', count: 42 })
  })

  it('default sink does not crash', () => {
    const logger = createLogger()
    // Should not throw — default sink writes to console.error
    expect(() => logger.info('hello')).not.toThrow()
  })
})
