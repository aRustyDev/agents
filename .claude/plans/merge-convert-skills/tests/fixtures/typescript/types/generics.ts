/**
 * Test fixtures for TypeScript generics.
 */

// Basic generic interface
interface Box<T> {
  value: T
}

// Generic with default
interface Container<T = string> {
  contents: T
}

// Generic with constraint
interface Lengthwise {
  length: number
}

interface LengthBox<T extends Lengthwise> {
  value: T
  getLength(): number
}

// Multiple type parameters
interface Pair<K, V> {
  key: K
  value: V
}

interface Triple<A, B, C> {
  first: A
  second: B
  third: C
}

// Generic with keyof constraint
interface PropertyAccessor<T, K extends keyof T> {
  get(obj: T): T[K]
  set(obj: T, value: T[K]): void
}

// Generic function types
type Mapper<T, U> = (item: T) => U
type Reducer<T, U> = (accumulator: U, item: T) => U
type Filter<T> = (item: T) => boolean

// Generic class
class Stack<T> {
  private items: T[] = []

  push(item: T): void {
    this.items.push(item)
  }

  pop(): T | undefined {
    return this.items.pop()
  }

  peek(): T | undefined {
    return this.items[this.items.length - 1]
  }

  isEmpty(): boolean {
    return this.items.length === 0
  }
}

// Generic class with constraint
class Repository<T extends { id: number }> {
  private items: Map<number, T> = new Map()

  save(item: T): void {
    this.items.set(item.id, item)
  }

  findById(id: number): T | undefined {
    return this.items.get(id)
  }

  delete(id: number): boolean {
    return this.items.delete(id)
  }

  findAll(): T[] {
    return Array.from(this.items.values())
  }
}

// Generic function
function identity<T>(value: T): T {
  return value
}

function first<T>(array: T[]): T | undefined {
  return array[0]
}

function last<T>(array: T[]): T | undefined {
  return array[array.length - 1]
}

// Generic function with multiple type parameters
function map<T, U>(array: T[], fn: (item: T) => U): U[] {
  return array.map(fn)
}

function zip<T, U>(a: T[], b: U[]): [T, U][] {
  return a.map((item, index) => [item, b[index]])
}

// Generic with conditional type
type Flatten<T> = T extends (infer U)[] ? U : T

type ArrayType<T> = T extends Array<infer U> ? U : never

// Generic with mapped type
type Readonly2<T> = {
  readonly [P in keyof T]: T[P]
}

type Optional2<T> = {
  [P in keyof T]?: T[P]
}

type Nullable2<T> = {
  [P in keyof T]: T[P] | null
}

// Recursive generic
type DeepReadonly<T> = {
  readonly [P in keyof T]: T[P] extends object ? DeepReadonly<T[P]> : T[P]
}

type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P]
}

// Exported generic
export interface AsyncResult<T, E = Error> {
  data: T | null
  error: E | null
  loading: boolean
}
