/**
 * Test fixtures for TypeScript arrow functions.
 */

// Basic arrow functions
const add = (a: number, b: number): number => a + b
const subtract = (a: number, b: number): number => a - b
const multiply = (a: number, b: number): number => a * b

// Arrow function with no parameters
const getTimestamp = (): number => Date.now()
const createId = (): string => Math.random().toString(36).slice(2)

// Arrow function with single parameter (no parens needed in JS)
const double = (x: number): number => x * 2
const stringify = (x: unknown): string => String(x)
const negate = (x: boolean): boolean => !x

// Arrow function returning object (wrapped in parens)
const createPoint = (x: number, y: number): { x: number; y: number } => ({
  x,
  y,
})

const createUser = (name: string, email: string): { name: string; email: string; id: string } => ({
  name,
  email,
  id: createId(),
})

// Arrow function with block body
const factorial = (n: number): number => {
  if (n <= 1) return 1
  return n * factorial(n - 1)
}

const fibonacci = (n: number): number => {
  if (n <= 1) return n
  return fibonacci(n - 1) + fibonacci(n - 2)
}

// Generic arrow functions
const identity = <T>(x: T): T => x
const pair = <T, U>(a: T, b: U): [T, U] => [a, b]
const wrap = <T>(value: T): { value: T } => ({ value })

// Arrow function with default parameters
const greet = (name: string, greeting: string = 'Hello'): string => `${greeting}, ${name}!`

// Arrow function with rest parameters
const sum = (...numbers: number[]): number => numbers.reduce((a, b) => a + b, 0)

const join = (separator: string, ...items: string[]): string => items.join(separator)

// Arrow function with optional parameters
const format = (value: number, precision?: number): string =>
  precision !== undefined ? value.toFixed(precision) : String(value)

// Higher-order arrow functions
const curry =
  <T, U, R>(fn: (a: T, b: U) => R) =>
  (a: T) =>
  (b: U): R =>
    fn(a, b)

const compose =
  <T, U, R>(f: (x: U) => R, g: (x: T) => U) =>
  (x: T): R =>
    f(g(x))

const pipe =
  <T, U, R>(f: (x: T) => U, g: (x: U) => R) =>
  (x: T): R =>
    g(f(x))

// Array methods with arrow functions
const numbers = [1, 2, 3, 4, 5]
const doubled = numbers.map((x) => x * 2)
const evens = numbers.filter((x) => x % 2 === 0)
const total = numbers.reduce((acc, x) => acc + x, 0)

// Arrow function type annotations
type NumberToString = (n: number) => string
type Predicate<T> = (item: T) => boolean
type Mapper<T, U> = (item: T) => U
type Reducer<T, U> = (acc: U, item: T) => U

// Using arrow function types
const toString: NumberToString = (n) => String(n)
const isEven: Predicate<number> = (n) => n % 2 === 0
const doubleMapper: Mapper<number, number> = (n) => n * 2
const sumReducer: Reducer<number, number> = (acc, n) => acc + n

// Arrow function in object
const mathOps = {
  add: (a: number, b: number): number => a + b,
  subtract: (a: number, b: number): number => a - b,
  multiply: (a: number, b: number): number => a * b,
  divide: (a: number, b: number): number => a / b,
}

// Arrow function as class property
class Counter {
  private count = 0

  increment = (): number => ++this.count
  decrement = (): number => --this.count
  getCount = (): number => this.count
  reset = (): void => {
    this.count = 0
  }
}

// Immediately invoked arrow function
const config = ((env: string) => ({
  debug: env === 'development',
  apiUrl: env === 'production' ? 'https://api.prod.com' : 'http://localhost:3000',
}))(process.env.NODE_ENV || 'development')

// Exported arrow functions
export const capitalize = (s: string): string => s.charAt(0).toUpperCase() + s.slice(1)

export const truncate = (s: string, maxLength: number): string =>
  s.length > maxLength ? s.slice(0, maxLength) + '...' : s
