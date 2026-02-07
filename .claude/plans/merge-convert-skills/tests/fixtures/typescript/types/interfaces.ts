/**
 * Test fixtures for TypeScript interfaces.
 */

// Basic interface
interface User {
  id: number
  name: string
  email: string
}

// Interface with optional properties
interface Config {
  host: string
  port: number
  ssl?: boolean
  timeout?: number
}

// Interface with readonly properties
interface Immutable {
  readonly id: string
  readonly createdAt: Date
  readonly data: ReadonlyArray<number>
}

// Interface extending other interfaces
interface Named {
  name: string
}

interface Aged {
  age: number
}

interface Person extends Named, Aged {
  email: string
}

// Interface with methods
interface Calculator {
  add(a: number, b: number): number
  subtract(a: number, b: number): number
  multiply(a: number, b: number): number
  divide(a: number, b: number): number
}

// Interface with index signature
interface StringMap {
  [key: string]: string
}

interface NumberMap {
  [key: string]: number
  length: number // Specific property alongside index
}

// Interface with call signature
type Callable = (x: number) => number

// Interface with multiple call signatures (overloads)
interface Overloaded {
  (x: number): number
  (x: string): string
  (x: number, y: number): number
}

// Interface with construct signature
interface Constructable {
  new (name: string): object
}

// Generic interface
interface Container<T> {
  value: T
  getValue(): T
  setValue(value: T): void
}

// Generic interface with constraints
interface Repository<T extends { id: number }> {
  findById(id: number): T | null
  save(entity: T): T
  delete(id: number): boolean
}

// Exported interface
export interface PublicApi {
  version: string
  call(method: string, params: unknown[]): Promise<unknown>
}
