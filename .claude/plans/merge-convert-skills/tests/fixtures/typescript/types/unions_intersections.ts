/**
 * Test fixtures for TypeScript union and intersection types.
 */

// Simple union types
type StringOrNumber = string | number
type Primitive = string | number | boolean | null | undefined

// Literal union types
type Direction = 'north' | 'south' | 'east' | 'west'
type HttpMethod = 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH'
type StatusCode = 200 | 201 | 400 | 401 | 403 | 404 | 500

// Boolean literal union
type Bit = 0 | 1
type Toggle = 'on' | 'off'

// Discriminated union types
type Success<T> = {
  success: true
  data: T
}

type Failure = {
  success: false
  error: string
}

type Result<T> = Success<T> | Failure

// Tagged union (discriminated by 'kind')
type Circle = {
  kind: 'circle'
  radius: number
}

type Square = {
  kind: 'square'
  size: number
}

type Triangle = {
  kind: 'triangle'
  base: number
  height: number
}

type Shape = Circle | Square | Triangle

// Intersection types
type Named = { name: string }
type Aged = { age: number }
type Person = Named & Aged

// More complex intersection
type WithId = { id: number }
type WithTimestamps = { createdAt: Date; updatedAt: Date }
type Entity = WithId & WithTimestamps

type User = Entity & {
  email: string
  role: 'admin' | 'user'
}

// Intersection with generics
type WithMetadata<T> = T & { metadata: Record<string, unknown> }

// Union of intersections
type Admin = Named & { role: 'admin'; permissions: string[] }
type Guest = Named & { role: 'guest' }
type Account = Admin | Guest

// Nullable types
type NullableString = string | null
type OptionalNumber = number | undefined
type MaybeUser = User | null | undefined

// Array union types
type StringOrNumberArray = string[] | number[]
type MixedArray = (string | number)[]

// Function union types
type StringProcessor = (s: string) => string
type NumberProcessor = (n: number) => number
type Processor = StringProcessor | NumberProcessor

// Conditional in union
type ExtractArrayType<T> = T extends (infer U)[] ? U : never
type ArrayElement = ExtractArrayType<string[] | number[]>

// Exported union type
export type ApiResponse<T> =
  | { status: 'success'; data: T }
  | { status: 'error'; message: string }
  | { status: 'loading' }
