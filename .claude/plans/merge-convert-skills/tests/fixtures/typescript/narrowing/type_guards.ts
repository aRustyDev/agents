// Type guards and user-defined type predicates

// Basic type guards with typeof
function processValue(value: string | number | boolean): string {
  if (typeof value === 'string') {
    return value.toUpperCase()
  } else if (typeof value === 'number') {
    return value.toFixed(2)
  } else {
    return value ? 'yes' : 'no'
  }
}

// instanceof type guard
class Dog {
  bark(): string {
    return 'Woof!'
  }
}

class Cat {
  meow(): string {
    return 'Meow!'
  }
}

function makeSound(animal: Dog | Cat): string {
  if (animal instanceof Dog) {
    return animal.bark()
  } else {
    return animal.meow()
  }
}

// User-defined type guard (type predicate)
interface Fish {
  swim: () => void
}

interface Bird {
  fly: () => void
}

function isFish(pet: Fish | Bird): pet is Fish {
  return (pet as Fish).swim !== undefined
}

function move(pet: Fish | Bird): void {
  if (isFish(pet)) {
    pet.swim()
  } else {
    pet.fly()
  }
}

// Type guard with assertion function
function assertIsString(value: unknown): asserts value is string {
  if (typeof value !== 'string') {
    throw new Error('Value must be a string')
  }
}

function processUnknown(value: unknown): string {
  assertIsString(value)
  return value.toUpperCase() // value is now string
}

// Generic type guard
function isNotNull<T>(value: T | null | undefined): value is T {
  return value != null
}

function processArray<T>(items: (T | null)[]): T[] {
  return items.filter(isNotNull)
}

// Type guard for object shapes
interface SuccessResponse {
  status: 'success'
  data: unknown
}

interface ErrorResponse {
  status: 'error'
  message: string
}

type ApiResponse = SuccessResponse | ErrorResponse

function isSuccess(response: ApiResponse): response is SuccessResponse {
  return response.status === 'success'
}

function handleResponse(response: ApiResponse): unknown {
  if (isSuccess(response)) {
    return response.data
  } else {
    throw new Error(response.message)
  }
}

// Array type guard
function isStringArray(value: unknown): value is string[] {
  return Array.isArray(value) && value.every((item) => typeof item === 'string')
}

export {
  processValue,
  Dog,
  Cat,
  makeSound,
  type Fish,
  type Bird,
  isFish,
  move,
  assertIsString,
  processUnknown,
  isNotNull,
  processArray,
  type SuccessResponse,
  type ErrorResponse,
  type ApiResponse,
  isSuccess,
  handleResponse,
  isStringArray,
}
