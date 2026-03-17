// JSDoc type annotations in TypeScript

/**
 * A user in the system.
 * @typedef {Object} User
 * @property {number} id - Unique identifier
 * @property {string} name - User's display name
 * @property {string} [email] - Optional email address
 */
interface User {
  id: number
  name: string
  email?: string
}

/**
 * Greets a user by name.
 * @param {string} name - The name to greet
 * @returns {string} The greeting message
 */
function greet(name: string): string {
  return `Hello, ${name}!`
}

/**
 * Calculates the sum of two numbers.
 * @param {number} a - First number
 * @param {number} b - Second number
 * @returns {number} The sum of a and b
 * @example
 * const result = add(2, 3);
 * console.log(result); // 5
 */
function add(a: number, b: number): number {
  return a + b
}

/**
 * A generic container class.
 * @template T - The type of value contained
 */
class Container<T> {
  /**
   * Creates a new container.
   * @param {T} value - The initial value
   */
  constructor(private value: T) {}

  /**
   * Gets the contained value.
   * @returns {T} The contained value
   */
  get(): T {
    return this.value
  }

  /**
   * Sets a new value.
   * @param {T} value - The new value
   * @returns {void}
   */
  set(value: T): void {
    this.value = value
  }
}

/**
 * @callback CompareFunction
 * @param {T} a - First item
 * @param {T} b - Second item
 * @returns {number} Negative if a < b, positive if a > b, zero if equal
 * @template T
 */
type CompareFunction<T> = (a: T, b: T) => number

/**
 * Sorts an array using a comparison function.
 * @param {T[]} arr - Array to sort
 * @param {CompareFunction<T>} compare - Comparison function
 * @returns {T[]} Sorted array
 * @template T
 */
function sortArray<T>(arr: T[], compare: CompareFunction<T>): T[] {
  return [...arr].sort(compare)
}

/**
 * HTTP response status.
 * @readonly
 * @enum {number}
 */
const HttpStatus = {
  OK: 200,
  CREATED: 201,
  BAD_REQUEST: 400,
  NOT_FOUND: 404,
  SERVER_ERROR: 500,
} as const

type HttpStatusType = (typeof HttpStatus)[keyof typeof HttpStatus]

/**
 * Makes an API request.
 * @async
 * @param {string} url - The URL to fetch
 * @param {RequestInit} [options] - Fetch options
 * @returns {Promise<Response>} The fetch response
 * @throws {Error} If the network request fails
 */
async function apiRequest(url: string, options?: RequestInit): Promise<Response> {
  const response = await fetch(url, options)
  if (!response.ok) {
    throw new Error(`HTTP error: ${response.status}`)
  }
  return response
}

/**
 * @type {Record<string, number>}
 */
const scores: Record<string, number> = {
  alice: 100,
  bob: 85,
  charlie: 92,
}

/**
 * Configuration options.
 * @typedef {Object} Config
 * @property {string} apiUrl - API base URL
 * @property {number} timeout - Request timeout in ms
 * @property {boolean} [debug=false] - Enable debug mode
 */
interface Config {
  apiUrl: string
  timeout: number
  debug?: boolean
}

/**
 * Creates a configured client.
 * @param {Config} config - Configuration options
 * @returns {{ request: (path: string) => Promise<unknown> }} Configured client
 */
function createClient(config: Config): { request: (path: string) => Promise<unknown> } {
  return {
    async request(path: string): Promise<unknown> {
      const response = await fetch(`${config.apiUrl}${path}`)
      return response.json()
    },
  }
}

export {
  type User,
  greet,
  add,
  Container,
  type CompareFunction,
  sortArray,
  HttpStatus,
  type HttpStatusType,
  apiRequest,
  scores,
  type Config,
  createClient,
}
