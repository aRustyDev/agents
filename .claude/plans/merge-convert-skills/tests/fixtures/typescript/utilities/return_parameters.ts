// Utility types: ReturnType, Parameters, ConstructorParameters, InstanceType

// Sample functions
function greet(name: string, age: number): string {
  return `Hello, ${name}! You are ${age} years old.`
}

async function fetchUser(id: number): Promise<{ id: number; name: string }> {
  return { id, name: 'User' }
}

// ReturnType extracts the return type
type GreetReturn = ReturnType<typeof greet>
// Result: string

type FetchUserReturn = ReturnType<typeof fetchUser>
// Result: Promise<{ id: number; name: string }>

// Awaited + ReturnType for async functions
type AwaitedFetchUser = Awaited<ReturnType<typeof fetchUser>>
// Result: { id: number; name: string }

// Parameters extracts function parameters as tuple
type GreetParams = Parameters<typeof greet>
// Result: [name: string, age: number]

type FetchUserParams = Parameters<typeof fetchUser>
// Result: [id: number]

// ConstructorParameters for classes
class Person {
  constructor(
    public name: string,
    public age: number,
    public email?: string
  ) {}
}

type PersonConstructorParams = ConstructorParameters<typeof Person>
// Result: [name: string, age: number, email?: string]

// InstanceType gets the instance type of a constructor
type PersonInstance = InstanceType<typeof Person>
// Result: Person

// Practical usage: creating wrapper functions
function wrapFunction<T extends (...args: unknown[]) => unknown>(
  fn: T
): (...args: Parameters<T>) => ReturnType<T> {
  return (...args: Parameters<T>) => {
    console.log('Calling function with:', args)
    return fn(...args) as ReturnType<T>
  }
}

// ThisParameterType and OmitThisParameter
function getFullName(this: { firstName: string; lastName: string }): string {
  return `${this.firstName} ${this.lastName}`
}

type GetFullNameThis = ThisParameterType<typeof getFullName>
type GetFullNameWithoutThis = OmitThisParameter<typeof getFullName>

export {
  greet,
  fetchUser,
  type GreetReturn,
  type FetchUserReturn,
  type AwaitedFetchUser,
  type GreetParams,
  type FetchUserParams,
  Person,
  type PersonConstructorParams,
  type PersonInstance,
  wrapFunction,
  getFullName,
  type GetFullNameThis,
  type GetFullNameWithoutThis,
}
