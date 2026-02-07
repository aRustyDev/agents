/**
 * Test fixtures for TypeScript namespaces.
 */

// Basic namespace
namespace Shapes {
  export interface Point {
    x: number
    y: number
  }

  export class Circle {
    constructor(
      public center: Point,
      public radius: number
    ) {}

    area(): number {
      return Math.PI * this.radius ** 2
    }
  }

  export class Rectangle {
    constructor(
      public topLeft: Point,
      public width: number,
      public height: number
    ) {}

    area(): number {
      return this.width * this.height
    }
  }

  export function distance(p1: Point, p2: Point): number {
    return Math.sqrt((p2.x - p1.x) ** 2 + (p2.y - p1.y) ** 2)
  }
}

// Using namespace members
const circle = new Shapes.Circle({ x: 0, y: 0 }, 5)
const rect = new Shapes.Rectangle({ x: 0, y: 0 }, 10, 20)
const dist = Shapes.distance({ x: 0, y: 0 }, { x: 3, y: 4 })

// Nested namespaces
namespace App {
  export namespace Models {
    export interface User {
      id: number
      name: string
    }

    export interface Product {
      id: number
      name: string
      price: number
    }
  }

  export namespace Services {
    export class UserService {
      getUser(id: number): Models.User | null {
        return { id, name: 'User' }
      }
    }

    export class ProductService {
      getProduct(id: number): Models.Product | null {
        return { id, name: 'Product', price: 100 }
      }
    }
  }

  export namespace Utils {
    export function formatCurrency(amount: number): string {
      return `$${amount.toFixed(2)}`
    }

    export function formatDate(date: Date): string {
      return date.toISOString().split('T')[0]
    }
  }
}

// Namespace alias
import Models = App.Models
import Services = App.Services

const user: Models.User = { id: 1, name: 'John' }
const userService = new Services.UserService()

// Namespace merging
namespace Validation {
  export interface StringValidator {
    isValid(s: string): boolean
  }
}

namespace Validation {
  export class EmailValidator implements StringValidator {
    isValid(s: string): boolean {
      return s.includes('@')
    }
  }
}

namespace Validation {
  export class PhoneValidator implements StringValidator {
    isValid(s: string): boolean {
      return /^\d{10}$/.test(s)
    }
  }
}

// Using merged namespace
const emailValidator = new Validation.EmailValidator()
const phoneValidator = new Validation.PhoneValidator()

// Namespace with constants
namespace Constants {
  export const API_VERSION = 'v1'
  export const BASE_URL = 'https://api.example.com'
  export const TIMEOUT = 5000

  export enum HttpStatus {
    OK = 200,
    Created = 201,
    BadRequest = 400,
    Unauthorized = 401,
    NotFound = 404,
    InternalError = 500,
  }
}

// Ambient namespace declaration
declare namespace ExternalLib {
  interface Config {
    apiKey: string
    timeout?: number
  }

  function init(config: Config): void
  function fetch<T>(endpoint: string): Promise<T>

  class Client {
    constructor(config: Config)
    request<T>(method: string, path: string): Promise<T>
  }
}

// Global augmentation
declare global {
  interface Array<T> {
    customMethod(): T[]
  }

  namespace NodeJS {
    interface ProcessEnv {
      NODE_ENV: 'development' | 'production' | 'test'
      API_KEY: string
    }
  }
}

// Exported namespace
export namespace PublicApi {
  export interface Request {
    method: string
    path: string
    body?: unknown
  }

  export interface Response<T> {
    status: number
    data: T
    error?: string
  }

  export function createRequest(method: string, path: string, body?: unknown): Request {
    return { method, path, body }
  }

  export async function send<T>(request: Request): Promise<Response<T>> {
    // Implementation
    return { status: 200, data: {} as T }
  }
}
