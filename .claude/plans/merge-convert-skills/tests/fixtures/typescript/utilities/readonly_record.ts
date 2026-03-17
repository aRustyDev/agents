// Utility types: Readonly, Record, ReadonlyArray

// Readonly makes all properties readonly
interface Config {
  apiUrl: string
  timeout: number
  retries: number
}

type ImmutableConfig = Readonly<Config>

const config: ImmutableConfig = {
  apiUrl: 'https://api.example.com',
  timeout: 5000,
  retries: 3,
}

// Record creates an object type with keys and values
type UserRoles = 'admin' | 'editor' | 'viewer'
type RolePermissions = Record<UserRoles, string[]>

const permissions: RolePermissions = {
  admin: ['read', 'write', 'delete', 'manage'],
  editor: ['read', 'write'],
  viewer: ['read'],
}

// Readonly arrays
type ImmutableNumbers = ReadonlyArray<number>
type AnotherImmutable = readonly number[]

const numbers: ImmutableNumbers = [1, 2, 3, 4, 5]

// Nested readonly
type DeepReadonly<T> = {
  readonly [P in keyof T]: T[P] extends object ? DeepReadonly<T[P]> : T[P]
}

interface MutableState {
  user: {
    name: string
    settings: {
      theme: string
    }
  }
}

type ImmutableState = DeepReadonly<MutableState>

// Record with computed keys
type HttpMethod = 'GET' | 'POST' | 'PUT' | 'DELETE'
type EndpointConfig = Record<HttpMethod, { url: string; auth: boolean }>

const endpoints: EndpointConfig = {
  GET: { url: '/api/items', auth: false },
  POST: { url: '/api/items', auth: true },
  PUT: { url: '/api/items/:id', auth: true },
  DELETE: { url: '/api/items/:id', auth: true },
}

export {
  type Config,
  type ImmutableConfig,
  type RolePermissions,
  type ImmutableNumbers,
  type DeepReadonly,
  type ImmutableState,
  type EndpointConfig,
  config,
  permissions,
  numbers,
  endpoints,
}
