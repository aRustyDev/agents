/**
 * Test fixtures for TypeScript conditional types.
 */

// Basic conditional type
type IsString<T> = T extends string ? true : false
type IsNumber<T> = T extends number ? true : false
type IsArray<T> = T extends unknown[] ? true : false

// Conditional with infer
type GetReturnType<T> = T extends (...args: unknown[]) => infer R ? R : never
type GetFirstArg<T> = T extends (first: infer F, ...args: unknown[]) => unknown ? F : never
type GetArrayElementType<T> = T extends (infer U)[] ? U : never

// Conditional type distribution
type ToArray<T> = T extends unknown ? T[] : never
type Distributive = ToArray<string | number> // string[] | number[]

// Non-distributive conditional
type NonDistributive<T> = [T] extends [unknown] ? T[] : never

// Exclude and Extract reimplemented
type MyExclude<T, U> = T extends U ? never : T
type MyExtract<T, U> = T extends U ? T : never

// NonNullable reimplemented
type MyNonNullable<T> = T extends null | undefined ? never : T

// Promise unwrapping
type Awaited2<T> = T extends Promise<infer U> ? Awaited2<U> : T

// Function manipulation
type Parameters2<T extends (...args: unknown[]) => unknown> = T extends (
  ...args: infer P
) => unknown
  ? P
  : never

type ReturnType2<T extends (...args: unknown[]) => unknown> = T extends (
  ...args: unknown[]
) => infer R
  ? R
  : never

// Constructor types
type InstanceType2<T extends new (...args: unknown[]) => unknown> = T extends new (
  ...args: unknown[]
) => infer R
  ? R
  : never

type ConstructorParameters2<T extends new (...args: unknown[]) => unknown> = T extends new (
  ...args: infer P
) => unknown
  ? P
  : never

// Tuple manipulation
type First<T extends unknown[]> = T extends [infer F, ...unknown[]] ? F : never
type Last<T extends unknown[]> = T extends [...unknown[], infer L] ? L : never
type Tail<T extends unknown[]> = T extends [unknown, ...infer R] ? R : never
type Init<T extends unknown[]> = T extends [...infer I, unknown] ? I : never

// Length of tuple
type Length<T extends unknown[]> = T['length']

// Append to tuple
type Append<T extends unknown[], U> = [...T, U]
type Prepend<T extends unknown[], U> = [U, ...T]

// Flatten one level
type FlattenOnce<T> = T extends (infer U)[] ? U : T

// Deep flatten
type DeepFlatten<T> = T extends (infer U)[] ? DeepFlatten<U> : T

// Object key manipulation
type KeysOfType<T, V> = {
  [K in keyof T]: T[K] extends V ? K : never
}[keyof T]

type PickByType<T, V> = {
  [K in KeysOfType<T, V>]: T[K]
}

// Optional keys
type OptionalKeys<T> = {
  [K in keyof T]-?: undefined extends T[K] ? K : never
}[keyof T]

type RequiredKeys<T> = {
  [K in keyof T]-?: undefined extends T[K] ? never : K
}[keyof T]

// Mutable
type Mutable<T> = {
  -readonly [P in keyof T]: T[P]
}

// String manipulation
type Uppercase2<S extends string> = Uppercase<S>
type Lowercase2<S extends string> = Lowercase<S>
type Capitalize2<S extends string> = Capitalize<S>
type Uncapitalize2<S extends string> = Uncapitalize<S>

// Template literal types
type EventName<T extends string> = `on${Capitalize<T>}`
type Getters<T extends string> = `get${Capitalize<T>}`
type Setters<T extends string> = `set${Capitalize<T>}`

// Exported conditional type
export type UnwrapPromise<T> = T extends Promise<infer U> ? UnwrapPromise<U> : T
