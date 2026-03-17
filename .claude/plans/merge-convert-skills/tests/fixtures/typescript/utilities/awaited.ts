// Utility types: Awaited, NonNullable in async contexts

// Awaited unwraps Promise types
type BasicPromise = Promise<string>
type UnwrappedBasic = Awaited<BasicPromise>
// Result: string

// Works with nested promises
type NestedPromise = Promise<Promise<number>>
type UnwrappedNested = Awaited<NestedPromise>
// Result: number

// Works with Promise-like objects
interface Thenable<T> {
  then<TResult>(onfulfilled: (value: T) => TResult | PromiseLike<TResult>): PromiseLike<TResult>
}

type ThenableString = Thenable<string>
type UnwrappedThenable = Awaited<ThenableString>
// Result: string

// Practical async function patterns
async function fetchData<T>(url: string): Promise<T> {
  const response = await fetch(url)
  return response.json()
}

type FetchDataResult<T> = Awaited<ReturnType<typeof fetchData<T>>>

// Complex async patterns
interface ApiResponse<T> {
  data: T
  status: number
  message: string
}

async function apiCall<T>(endpoint: string): Promise<ApiResponse<T>> {
  return { data: {} as T, status: 200, message: 'OK' }
}

type ApiCallResult<T> = Awaited<ReturnType<typeof apiCall<T>>>

// Combine with NonNullable
type MaybePromise<T> = T | Promise<T>
type MaybeNull<T> = T | null | undefined

async function fetchOptional<T>(url: string): Promise<MaybeNull<T>> {
  try {
    const response = await fetch(url)
    return response.json()
  } catch {
    return null
  }
}

type FetchOptionalResult<T> = NonNullable<Awaited<ReturnType<typeof fetchOptional<T>>>>

// Promise.all pattern
async function fetchMultiple(): Promise<[string, number, boolean]> {
  return Promise.all([Promise.resolve('hello'), Promise.resolve(42), Promise.resolve(true)])
}

type MultipleResults = Awaited<ReturnType<typeof fetchMultiple>>
// Result: [string, number, boolean]

export {
  type UnwrappedBasic,
  type UnwrappedNested,
  type Thenable,
  type UnwrappedThenable,
  type FetchDataResult,
  type ApiResponse,
  type ApiCallResult,
  type MaybePromise,
  type FetchOptionalResult,
  type MultipleResults,
  fetchData,
  apiCall,
  fetchOptional,
  fetchMultiple,
}
