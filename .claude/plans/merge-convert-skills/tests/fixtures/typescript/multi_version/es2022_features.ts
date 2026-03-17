// ES2022+ target features

// Top-level await (in modules)
// const response = await fetch('https://api.example.com/data');

// Class fields and private fields
class Counter {
  // Public field with initializer
  count = 0

  // Private field
  #step = 1

  // Static field
  static instances = 0

  // Static private field
  static #totalCounts = 0

  constructor(initialCount = 0, step = 1) {
    this.count = initialCount
    this.#step = step
    Counter.instances++
  }

  increment(): void {
    this.count += this.#step
    Counter.#totalCounts++
  }

  decrement(): void {
    this.count -= this.#step
    Counter.#totalCounts++
  }

  // Private method
  #reset(): void {
    this.count = 0
  }

  clear(): void {
    this.#reset()
  }

  // Static private method
  static #logTotal(): void {
    console.log(`Total operations: ${Counter.#totalCounts}`)
  }

  static report(): void {
    Counter.#logTotal()
  }
}

// Static initialization blocks
class Database {
  static connection: string
  static #config: { host: string; port: number }

  static {
    // Static initialization block
    Database.#config = {
      host: process.env.DB_HOST ?? 'localhost',
      port: parseInt(process.env.DB_PORT ?? '5432'),
    }
    Database.connection = `postgresql://${Database.#config.host}:${Database.#config.port}`
  }

  static getConfig(): { host: string; port: number } {
    return { ...Database.#config }
  }
}

// at() method for arrays
function getLastItem<T>(arr: T[]): T | undefined {
  return arr.at(-1)
}

function getNthFromEnd<T>(arr: T[], n: number): T | undefined {
  return arr.at(-n)
}

// Object.hasOwn()
function safeHasProperty(obj: object, key: string): boolean {
  return Object.hasOwn(obj, key)
}

// Error cause
class ApplicationError extends Error {
  constructor(message: string, options?: { cause?: Error }) {
    super(message, options)
    this.name = 'ApplicationError'
  }
}

function wrapError(originalError: Error): ApplicationError {
  return new ApplicationError('Operation failed', { cause: originalError })
}

// RegExp match indices (d flag)
function findMatchPositions(text: string, pattern: RegExp): number[][] {
  const matches: number[][] = []
  const regex = new RegExp(pattern.source, pattern.flags + 'd')
  let match

  while ((match = regex.exec(text)) !== null) {
    if (match.indices) {
      matches.push([match.indices[0][0], match.indices[0][1]])
    }
    if (!regex.global) break
  }

  return matches
}

// Array.prototype.findLast and findLastIndex
function findLastEven(numbers: number[]): number | undefined {
  return numbers.findLast((n) => n % 2 === 0)
}

function findLastEvenIndex(numbers: number[]): number {
  return numbers.findLastIndex((n) => n % 2 === 0)
}

// WeakRef and FinalizationRegistry
class Cache<K extends object, V> {
  #cache = new Map<K, WeakRef<V & object>>()
  #registry = new FinalizationRegistry<K>((key) => {
    this.#cache.delete(key)
  })

  set(key: K, value: V & object): void {
    const ref = new WeakRef(value)
    this.#cache.set(key, ref)
    this.#registry.register(value, key)
  }

  get(key: K): V | undefined {
    const ref = this.#cache.get(key)
    return ref?.deref() as V | undefined
  }
}

// Logical assignment operators
interface Options {
  timeout?: number
  retries?: number
  debug?: boolean
}

function applyDefaults(options: Options): Required<Options> {
  options.timeout ??= 5000
  options.retries ||= 3
  options.debug &&= process.env.NODE_ENV !== 'production'

  return options as Required<Options>
}

// Numeric separators
const MILLION = 1_000_000
const BILLION = 1_000_000_000
const BYTES_PER_MB = 1_048_576
const HEX_COLOR = 0xff_00_ff
const BINARY = 0b1010_0001_1000_0101

// Promise.any
async function fetchFirst(urls: string[]): Promise<Response> {
  return Promise.any(urls.map((url) => fetch(url)))
}

// String.prototype.replaceAll
function sanitizeInput(input: string): string {
  return input.replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('&', '&amp;')
}

export {
  Counter,
  Database,
  getLastItem,
  getNthFromEnd,
  safeHasProperty,
  ApplicationError,
  wrapError,
  findMatchPositions,
  findLastEven,
  findLastEvenIndex,
  Cache,
  applyDefaults,
  MILLION,
  BILLION,
  BYTES_PER_MB,
  fetchFirst,
  sanitizeInput,
}
