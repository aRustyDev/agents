export type LogLevel = 'debug' | 'info' | 'warn' | 'error' | 'fatal'

export interface LogEntry {
  level: LogLevel
  message: string
  context?: Record<string, unknown>
  timestamp?: string
}

export interface LogSink {
  write(entry: LogEntry): void
}

export interface Logger {
  debug(message: string, context?: Record<string, unknown>): void
  info(message: string, context?: Record<string, unknown>): void
  warn(message: string, context?: Record<string, unknown>): void
  error(message: string, context?: Record<string, unknown>): void
  fatal(message: string, context?: Record<string, unknown>): void
}

const LEVEL_ORDER: Record<LogLevel, number> = {
  debug: 0,
  info: 1,
  warn: 2,
  error: 3,
  fatal: 4,
}

const defaultSink: LogSink = {
  write(entry) {
    console.error(JSON.stringify(entry))
  },
}

export function createLogger(opts?: { level?: LogLevel; sink?: LogSink }): Logger {
  const minLevel = LEVEL_ORDER[opts?.level ?? 'info']
  const sink = opts?.sink ?? defaultSink
  function log(level: LogLevel, message: string, context?: Record<string, unknown>) {
    if (LEVEL_ORDER[level] < minLevel) return
    sink.write({ level, message, context, timestamp: new Date().toISOString() })
  }
  return {
    debug: (m, c) => log('debug', m, c),
    info: (m, c) => log('info', m, c),
    warn: (m, c) => log('warn', m, c),
    error: (m, c) => log('error', m, c),
    fatal: (m, c) => log('fatal', m, c),
  }
}
