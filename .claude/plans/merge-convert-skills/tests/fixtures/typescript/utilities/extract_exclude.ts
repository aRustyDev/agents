// Utility types: Extract, Exclude, NonNullable

// Union type to work with
type AllTypes = string | number | boolean | null | undefined | object

// Extract types that are assignable to a condition
type Primitives = Extract<AllTypes, string | number | boolean>
// Result: string | number | boolean

// Exclude types that are assignable to a condition
type NonPrimitives = Exclude<AllTypes, string | number | boolean>
// Result: null | undefined | object

// NonNullable removes null and undefined
type Defined = NonNullable<AllTypes>
// Result: string | number | boolean | object

// Practical examples
type HttpStatus = 200 | 201 | 400 | 401 | 403 | 404 | 500
type SuccessStatus = Extract<HttpStatus, 200 | 201>
type ErrorStatus = Exclude<HttpStatus, 200 | 201>

// Extract with unions
type Animal = { type: 'cat'; meow: () => void } | { type: 'dog'; bark: () => void }
type Cat = Extract<Animal, { type: 'cat' }>
type Dog = Extract<Animal, { type: 'dog' }>

// Function with NonNullable
function processValue<T>(value: T): NonNullable<T> | null {
  if (value === null || value === undefined) {
    return null
  }
  return value as NonNullable<T>
}

// Extract function types from union
type MixedTypes = string | (() => void) | number | ((x: number) => number)
type FunctionTypes = Extract<MixedTypes, (...args: unknown[]) => unknown>

// Exclude function types
type NonFunctionTypes = Exclude<MixedTypes, (...args: unknown[]) => unknown>

// Practical filter function
function filterNullish<T>(arr: (T | null | undefined)[]): NonNullable<T>[] {
  return arr.filter((item): item is NonNullable<T> => item != null)
}

export {
  type AllTypes,
  type Primitives,
  type NonPrimitives,
  type Defined,
  type SuccessStatus,
  type ErrorStatus,
  type Cat,
  type Dog,
  type FunctionTypes,
  type NonFunctionTypes,
  processValue,
  filterNullish,
}
