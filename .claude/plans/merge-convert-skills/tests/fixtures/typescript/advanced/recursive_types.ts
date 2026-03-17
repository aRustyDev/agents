// Recursive type definitions

// Basic recursive type - linked list
interface ListNode<T> {
  value: T
  next: ListNode<T> | null
}

function createList<T>(...values: T[]): ListNode<T> | null {
  if (values.length === 0) return null
  const [first, ...rest] = values
  return { value: first, next: createList(...rest) }
}

// Tree structure
interface TreeNode<T> {
  value: T
  children: TreeNode<T>[]
}

function traverseTree<T>(node: TreeNode<T>, visit: (value: T) => void): void {
  visit(node.value)
  for (const child of node.children) {
    traverseTree(child, visit)
  }
}

// JSON-like recursive type
type JSONValue = string | number | boolean | null | JSONValue[] | { [key: string]: JSONValue }

const jsonData: JSONValue = {
  name: 'John',
  age: 30,
  active: true,
  tags: ['user', 'admin'],
  metadata: {
    created: '2024-01-01',
    nested: {
      deep: [1, 2, { deeper: true }],
    },
  },
}

// Deep partial (recursive)
type DeepPartial<T> = T extends object ? { [P in keyof T]?: DeepPartial<T[P]> } : T

interface Config {
  server: {
    host: string
    port: number
    ssl: {
      enabled: boolean
      cert: string
    }
  }
  database: {
    url: string
  }
}

type PartialConfig = DeepPartial<Config>

// Deep required (recursive)
type DeepRequired<T> = T extends object ? { [P in keyof T]-?: DeepRequired<T[P]> } : T

// Deep readonly (recursive)
type DeepReadonly<T> = T extends object ? { readonly [P in keyof T]: DeepReadonly<T[P]> } : T

type ImmutableConfig = DeepReadonly<Config>

// Flatten nested arrays
type Flatten<T> = T extends Array<infer U> ? Flatten<U> : T

type NestedArray = number[][][]
type FlattenedArray = Flatten<NestedArray> // number

// Path types for nested objects
type Path<T, Key extends keyof T = keyof T> = Key extends string
  ? T[Key] extends object
    ? Key | `${Key}.${Path<T[Key]>}`
    : Key
  : never

interface User {
  name: string
  address: {
    city: string
    country: {
      name: string
      code: string
    }
  }
}

type UserPaths = Path<User>
// "name" | "address" | "address.city" | "address.country" | "address.country.name" | "address.country.code"

// Recursive tuple operations
type Reverse<T extends unknown[]> = T extends [infer First, ...infer Rest]
  ? [...Reverse<Rest>, First]
  : []

type Original = [1, 2, 3, 4]
type Reversed = Reverse<Original> // [4, 3, 2, 1]

// Expression AST
type Expression =
  | { type: 'number'; value: number }
  | { type: 'string'; value: string }
  | { type: 'binary'; op: '+' | '-' | '*' | '/'; left: Expression; right: Expression }
  | { type: 'unary'; op: '-' | '!'; operand: Expression }

function evaluate(expr: Expression): number | string {
  switch (expr.type) {
    case 'number':
      return expr.value
    case 'string':
      return expr.value
    case 'binary': {
      const left = evaluate(expr.left)
      const right = evaluate(expr.right)
      if (typeof left === 'number' && typeof right === 'number') {
        switch (expr.op) {
          case '+':
            return left + right
          case '-':
            return left - right
          case '*':
            return left * right
          case '/':
            return left / right
        }
      }
      return `${left}${right}`
    }
    case 'unary': {
      const operand = evaluate(expr.operand)
      if (expr.op === '-' && typeof operand === 'number') {
        return -operand
      }
      return operand
    }
  }
}

export {
  type ListNode,
  createList,
  type TreeNode,
  traverseTree,
  type JSONValue,
  jsonData,
  type DeepPartial,
  type DeepRequired,
  type DeepReadonly,
  type PartialConfig,
  type ImmutableConfig,
  type Flatten,
  type Path,
  type UserPaths,
  type Reverse,
  type Expression,
  evaluate,
}
