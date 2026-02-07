/**
 * Test fixtures for TypeScript async/await.
 */

// Basic async function
async function fetchData(url: string): Promise<object> {
  const response = await fetch(url)
  return response.json()
}

// Async function with typed return
interface User {
  id: number
  name: string
  email: string
}

async function getUser(id: number): Promise<User> {
  const response = await fetch(`/api/users/${id}`)
  return response.json()
}

// Async function with error handling
async function safeGetUser(id: number): Promise<User | null> {
  try {
    const response = await fetch(`/api/users/${id}`)
    if (!response.ok) {
      return null
    }
    return response.json()
  } catch {
    return null
  }
}

// Async function returning void
async function logMessage(message: string): Promise<void> {
  await new Promise((resolve) => setTimeout(resolve, 100))
  console.log(message)
}

// Async function with multiple awaits
async function processItems<T>(items: T[], processor: (item: T) => Promise<T>): Promise<T[]> {
  const results: T[] = []
  for (const item of items) {
    const processed = await processor(item)
    results.push(processed)
  }
  return results
}

// Parallel async operations
async function fetchAll<T>(urls: string[]): Promise<T[]> {
  const promises = urls.map(async (url) => {
    const response = await fetch(url)
    return response.json() as Promise<T>
  })
  return Promise.all(promises)
}

// Async generator
async function* paginate<T>(
  fetchPage: (page: number) => Promise<T[]>
): AsyncGenerator<T[], void, undefined> {
  let page = 0
  while (true) {
    const items = await fetchPage(page)
    if (items.length === 0) break
    yield items
    page++
  }
}

// Async method in class
class ApiClient {
  private baseUrl: string

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl
  }

  async get<T>(path: string): Promise<T> {
    const response = await fetch(`${this.baseUrl}${path}`)
    return response.json()
  }

  async post<T, R>(path: string, data: T): Promise<R> {
    const response = await fetch(`${this.baseUrl}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    })
    return response.json()
  }

  async delete(path: string): Promise<void> {
    await fetch(`${this.baseUrl}${path}`, { method: 'DELETE' })
  }
}

// Async arrow function
const fetchJson = async <T>(url: string): Promise<T> => {
  const response = await fetch(url)
  return response.json()
}

// Async IIFE
const result = (async () => {
  const data = await fetchData('/api/data')
  return data
})()

// Promise.race and Promise.any
async function raceRequests<T>(urls: string[]): Promise<T> {
  const promises = urls.map((url) => fetchJson<T>(url))
  return Promise.race(promises)
}

async function anyRequest<T>(urls: string[]): Promise<T> {
  const promises = urls.map((url) => fetchJson<T>(url))
  return Promise.any(promises)
}

// Timeout wrapper
async function withTimeout<T>(promise: Promise<T>, timeoutMs: number): Promise<T> {
  const timeout = new Promise<never>((_, reject) =>
    setTimeout(() => reject(new Error('Timeout')), timeoutMs)
  )
  return Promise.race([promise, timeout])
}

// Retry wrapper
async function withRetry<T>(fn: () => Promise<T>, maxRetries: number = 3): Promise<T> {
  let lastError: Error | undefined
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn()
    } catch (error) {
      lastError = error as Error
      await new Promise((resolve) => setTimeout(resolve, 1000 * (i + 1)))
    }
  }
  throw lastError
}

// Exported async function
export async function loadConfig(path: string): Promise<Record<string, unknown>> {
  const response = await fetch(path)
  if (!response.ok) {
    throw new Error(`Failed to load config: ${response.statusText}`)
  }
  return response.json()
}
