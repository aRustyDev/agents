// ES2015 (ES6) target features

// Arrow functions
const add = (a: number, b: number): number => a + b
const greet = (name: string): string => `Hello, ${name}!`

// Classes
class Animal {
  constructor(public name: string) {}

  speak(): string {
    return `${this.name} makes a sound`
  }
}

class Dog extends Animal {
  constructor(
    name: string,
    public breed: string
  ) {
    super(name)
  }

  override speak(): string {
    return `${this.name} barks`
  }
}

// Template literals
function formatMessage(user: string, action: string): string {
  return `User ${user} performed action: ${action}`
}

// Destructuring
interface Config {
  host: string
  port: number
  ssl: boolean
}

function parseConfig({ host, port, ssl }: Config): string {
  return `${ssl ? 'https' : 'http'}://${host}:${port}`
}

// Array destructuring
function getFirstTwo<T>(arr: T[]): [T | undefined, T | undefined] {
  const [first, second] = arr
  return [first, second]
}

// Spread operator
function mergeArrays<T>(...arrays: T[][]): T[] {
  return arrays.reduce((acc, arr) => [...acc, ...arr], [])
}

function mergeObjects<T extends object>(base: T, ...overrides: Partial<T>[]): T {
  return Object.assign({}, base, ...overrides)
}

// Default parameters
function createUser(
  name: string,
  role: string = 'user',
  active: boolean = true
): { name: string; role: string; active: boolean } {
  return { name, role, active }
}

// Rest parameters
function sum(...numbers: number[]): number {
  return numbers.reduce((acc, n) => acc + n, 0)
}

// Shorthand property names
function createPoint(x: number, y: number): { x: number; y: number } {
  return { x, y }
}

// Computed property names
type PropName = 'name' | 'value'

function createDynamicObject<T>(key: PropName, value: T): { [K in PropName]?: T } {
  return { [key]: value }
}

// for...of loops
function* range(start: number, end: number): Generator<number> {
  for (let i = start; i < end; i++) {
    yield i
  }
}

function sumRange(start: number, end: number): number {
  let total = 0
  for (const n of range(start, end)) {
    total += n
  }
  return total
}

// Map and Set
function countOccurrences<T>(items: T[]): Map<T, number> {
  const counts = new Map<T, number>()
  for (const item of items) {
    counts.set(item, (counts.get(item) ?? 0) + 1)
  }
  return counts
}

function uniqueItems<T>(items: T[]): T[] {
  return [...new Set(items)]
}

// Symbol
const privateKey = Symbol('private')

interface WithPrivate {
  [privateKey]: string
  public: string
}

function createWithPrivate(pub: string, priv: string): WithPrivate {
  return {
    public: pub,
    [privateKey]: priv,
  }
}

// Promise (basic)
function delay(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

async function fetchWithTimeout(url: string, timeoutMs: number): Promise<Response> {
  return Promise.race([
    fetch(url),
    delay(timeoutMs).then(() => {
      throw new Error('Request timed out')
    }),
  ])
}

export {
  add,
  greet,
  Animal,
  Dog,
  formatMessage,
  parseConfig,
  getFirstTwo,
  mergeArrays,
  mergeObjects,
  createUser,
  sum,
  createPoint,
  createDynamicObject,
  range,
  sumRange,
  countOccurrences,
  uniqueItems,
  privateKey,
  createWithPrivate,
  delay,
  fetchWithTimeout,
}
