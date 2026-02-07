/**
 * Test fixtures for TypeScript type aliases.
 */

// Primitive type aliases
type ID = string
type Count = number
type Flag = boolean

// Object type aliases
type Point = {
  x: number
  y: number
}

type Rectangle = {
  topLeft: Point
  bottomRight: Point
}

// Function type aliases
type Callback = () => void
type Handler<T> = (event: T) => void
type Predicate<T> = (value: T) => boolean
type Comparator<T> = (a: T, b: T) => number

// Async function type alias
type AsyncFetcher<T> = (url: string) => Promise<T>

// Generic type aliases
type Nullable<T> = T | null
type Optional<T> = T | undefined
type Maybe<T> = T | null | undefined

type Pair<T, U> = [T, U]
type Triple<T, U, V> = [T, U, V]

// Record type aliases
type Dictionary<T> = Record<string, T>
type Lookup<K extends string, V> = Record<K, V>

// Utility type aliases
type ReadonlyPoint = Readonly<Point>
type PartialConfig = Partial<{ host: string; port: number }>
type RequiredConfig = Required<{ host?: string; port?: number }>

// Pick and Omit
type UserName = Pick<{ id: number; name: string; email: string }, 'name'>
type UserWithoutId = Omit<{ id: number; name: string }, 'id'>

// Extract and Exclude
type Numbers = Extract<string | number | boolean, number>
type NoNumbers = Exclude<string | number | boolean, number>

// Return type extraction
type MyReturnType<T extends (...args: unknown[]) => unknown> = T extends (
  ...args: unknown[]
) => infer R
  ? R
  : never

// Parameters extraction
type MyParameters<T extends (...args: unknown[]) => unknown> = T extends (
  ...args: infer P
) => unknown
  ? P
  : never

// Exported type alias
export type PublicType = {
  value: string
  metadata: Record<string, unknown>
}
