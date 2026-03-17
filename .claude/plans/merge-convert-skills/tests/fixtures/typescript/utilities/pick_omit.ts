// Utility types: Pick, Omit, Partial, Required

interface User {
  id: number
  name: string
  email: string
  age?: number
  role: 'admin' | 'user'
}

// Pick specific properties
type UserCredentials = Pick<User, 'email' | 'name'>

// Omit properties
type PublicUser = Omit<User, 'email' | 'role'>

// Make all properties optional
type PartialUser = Partial<User>

// Make all properties required
type RequiredUser = Required<User>

// Combine utilities
type EditableUser = Partial<Pick<User, 'name' | 'email' | 'age'>>

// Deep partial (custom)
type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P]
}

interface Company {
  name: string
  address: {
    street: string
    city: string
    country: string
  }
}

type PartialCompany = DeepPartial<Company>

// Function using utility types
function updateUser(id: number, updates: Partial<User>): User {
  const user: User = { id, name: '', email: '', role: 'user' }
  return { ...user, ...updates }
}

function createCredentials(user: User): UserCredentials {
  return { name: user.name, email: user.email }
}

export {
  type User,
  type UserCredentials,
  type PublicUser,
  type PartialUser,
  type RequiredUser,
  type EditableUser,
  type DeepPartial,
  type PartialCompany,
  updateUser,
  createCredentials,
}
