// The 'infer' keyword in conditional types

// Basic infer usage - extract return type
type MyReturnType<T> = T extends (...args: unknown[]) => infer R ? R : never

function greet(name: string): string {
  return `Hello, ${name}!`
}

type GreetReturn = MyReturnType<typeof greet> // string

// Extract parameter types
type MyParameters<T> = T extends (...args: infer P) => unknown ? P : never

type GreetParams = MyParameters<typeof greet> // [name: string]

// Extract first parameter
type FirstParam<T> = T extends (first: infer F, ...rest: unknown[]) => unknown ? F : never

function add(a: number, b: number): number {
  return a + b
}

type FirstOfAdd = FirstParam<typeof add> // number

// Extract array element type
type ArrayElement<T> = T extends (infer E)[] ? E : never

type StringArrayElement = ArrayElement<string[]> // string

// Extract Promise resolved type
type Unpromise<T> = T extends Promise<infer U> ? U : T

type ResolvedString = Unpromise<Promise<string>> // string
type NotPromise = Unpromise<number> // number

// Deeply unwrap nested promises
type DeepUnpromise<T> = T extends Promise<infer U> ? DeepUnpromise<U> : T

type DeeplyNested = Promise<Promise<Promise<string>>>
type Unwrapped = DeepUnpromise<DeeplyNested> // string

// Extract object property types
type PropertyType<T, K extends keyof T> = T extends { [P in K]: infer V } ? V : never

interface Person {
  name: string
  age: number
}

type NameType = PropertyType<Person, 'name'> // string

// Infer from tuple
type First<T extends unknown[]> = T extends [infer F, ...unknown[]] ? F : never
type Last<T extends unknown[]> = T extends [...unknown[], infer L] ? L : never
type Rest<T extends unknown[]> = T extends [unknown, ...infer R] ? R : never

type Tuple = [string, number, boolean]
type TupleFirst = First<Tuple> // string
type TupleLast = Last<Tuple> // boolean
type TupleRest = Rest<Tuple> // [number, boolean]

// Infer function this type
type ThisType<T> = T extends (this: infer U, ...args: unknown[]) => unknown ? U : never

function withContext(this: { name: string }): string {
  return this.name
}

type ContextType = ThisType<typeof withContext> // { name: string }

// Infer constructor instance type
type ConstructorInstance<T> = T extends new (...args: unknown[]) => infer I ? I : never

class MyClass {
  value: number = 0
}

type MyClassInstance = ConstructorInstance<typeof MyClass> // MyClass

// Complex inference - extract route params
type ExtractRouteParams<T extends string> = T extends `${string}:${infer Param}/${infer Rest}`
  ? { [K in Param | keyof ExtractRouteParams<Rest>]: string }
  : T extends `${string}:${infer Param}`
    ? { [K in Param]: string }
    : Record<string, never>

type Params = ExtractRouteParams<'/users/:userId/posts/:postId'>
// { userId: string; postId: string }

// Infer with constraints
type InferWithConstraint<T> = T extends Array<infer E extends number> ? E : never

type NumbersOnly = InferWithConstraint<number[]> // number
type StringsFail = InferWithConstraint<string[]> // never

// Multiple infer in same conditional
type Split<T> = T extends `${infer A}-${infer B}` ? [A, B] : never

type SplitResult = Split<'hello-world'> // ["hello", "world"]

export {
  type MyReturnType,
  type MyParameters,
  type FirstParam,
  type ArrayElement,
  type Unpromise,
  type DeepUnpromise,
  type PropertyType,
  type First,
  type Last,
  type Rest,
  type ThisType,
  type ConstructorInstance,
  type ExtractRouteParams,
  type InferWithConstraint,
  type Split,
  greet,
  add,
  withContext,
  MyClass,
}
