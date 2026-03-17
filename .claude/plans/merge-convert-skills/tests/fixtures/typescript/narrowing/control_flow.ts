// Control flow analysis and type narrowing

// Truthiness narrowing
function processMaybeString(value: string | null | undefined): string {
  if (value) {
    return value.toUpperCase() // value is string here
  }
  return 'default'
}

// Equality narrowing
function compare(x: string | number, y: string | boolean): boolean {
  if (x === y) {
    // x and y are both string here
    return x.toLowerCase() === y.toLowerCase()
  }
  return false
}

// Narrowing with in operator
interface Admin {
  name: string
  privileges: string[]
}

interface User {
  name: string
  email: string
}

type Person = Admin | User

function printPersonInfo(person: Person): void {
  console.log(`Name: ${person.name}`)
  if ('privileges' in person) {
    console.log(`Privileges: ${person.privileges.join(', ')}`)
  }
  if ('email' in person) {
    console.log(`Email: ${person.email}`)
  }
}

// Assignment narrowing
function narrowByAssignment(): number {
  let x: number | string
  x = Math.random() < 0.5 ? 10 : 'hello'

  if (typeof x === 'number') {
    return x * 2
  }
  return x.length
}

// Control flow in loops
function processItems(items: (string | number)[]): void {
  for (const item of items) {
    if (typeof item === 'string') {
      console.log(item.toUpperCase())
    } else {
      console.log(item.toFixed(2))
    }
  }
}

// Narrowing with try-catch
function parseJSON(json: string): object | null {
  try {
    const result = JSON.parse(json)
    if (typeof result === 'object' && result !== null) {
      return result
    }
    return null
  } catch {
    return null
  }
}

// Narrowing with optional chaining
interface NestedObject {
  outer?: {
    inner?: {
      value: string
    }
  }
}

function getNestedValue(obj: NestedObject): string | undefined {
  return obj.outer?.inner?.value
}

// Narrowing with nullish coalescing
function getWithDefault(value: string | null | undefined): string {
  return value ?? 'default'
}

// Multiple conditions narrowing
function complexNarrowing(value: string | number | null | undefined): string {
  if (value === null) {
    return 'null'
  }
  if (value === undefined) {
    return 'undefined'
  }
  if (typeof value === 'number') {
    return `number: ${value}`
  }
  // value is now string
  return `string: ${value}`
}

// Never type in unreachable code
function throwError(message: string): never {
  throw new Error(message)
}

function processWithNever(value: string | number): string {
  if (typeof value === 'string') {
    return value
  }
  if (typeof value === 'number') {
    return String(value)
  }
  return throwError('Unexpected type')
}

// Array narrowing
function processFirstElement(arr: string[] | number[]): string | number | undefined {
  if (arr.length === 0) {
    return undefined
  }
  const first = arr[0]
  if (typeof first === 'string') {
    return first.toUpperCase()
  }
  return first * 2
}

export {
  processMaybeString,
  compare,
  type Admin,
  type User,
  type Person,
  printPersonInfo,
  narrowByAssignment,
  processItems,
  parseJSON,
  type NestedObject,
  getNestedValue,
  getWithDefault,
  complexNarrowing,
  throwError,
  processWithNever,
  processFirstElement,
}
