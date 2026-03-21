/**
 * Test fixtures for TypeScript access modifiers.
 */

// Public, private, protected
class Person {
  public name: string
  private ssn: string
  protected birthDate: Date

  constructor(name: string, ssn: string, birthDate: Date) {
    this.name = name
    this.ssn = ssn
    this.birthDate = birthDate
  }

  public greet(): string {
    return `Hello, I'm ${this.name}`
  }

  private getSSN(): string {
    return this.ssn
  }

  protected getAge(): number {
    const today = new Date()
    const age = today.getFullYear() - this.birthDate.getFullYear()
    return age
  }
}

// Readonly modifier
class Configuration {
  readonly apiUrl: string
  readonly maxRetries: number
  readonly timeout: number

  constructor(apiUrl: string, maxRetries: number = 3, timeout: number = 5000) {
    this.apiUrl = apiUrl
    this.maxRetries = maxRetries
    this.timeout = timeout
  }
}

// Static members
class MathUtils {
  static readonly PI = 3.14159
  static readonly E = 2.71828

  private static instance: MathUtils | null = null

  static getInstance(): MathUtils {
    if (!MathUtils.instance) {
      MathUtils.instance = new MathUtils()
    }
    return MathUtils.instance
  }

  static add(a: number, b: number): number {
    return a + b
  }

  static multiply(a: number, b: number): number {
    return a * b
  }
}

// Parameter properties (shorthand)
class Point {
  constructor(
    public x: number,
    public y: number,
    public readonly z: number = 0
  ) {}

  distanceTo(other: Point): number {
    return Math.sqrt((this.x - other.x) ** 2 + (this.y - other.y) ** 2 + (this.z - other.z) ** 2)
  }
}

// Private fields (ES2022 #private)
class BankAccount {
  #balance: number
  #accountNumber: string

  constructor(accountNumber: string, initialBalance: number = 0) {
    this.#accountNumber = accountNumber
    this.#balance = initialBalance
  }

  deposit(amount: number): void {
    if (amount > 0) {
      this.#balance += amount
    }
  }

  withdraw(amount: number): boolean {
    if (amount > 0 && amount <= this.#balance) {
      this.#balance -= amount
      return true
    }
    return false
  }

  getBalance(): number {
    return this.#balance
  }

  #validateTransaction(amount: number): boolean {
    return amount > 0 && amount <= this.#balance
  }
}

// Abstract with access modifiers
abstract class Repository<T> {
  protected abstract items: Map<string, T>

  public abstract find(id: string): T | undefined
  protected abstract validate(item: T): boolean

  public add(id: string, item: T): boolean {
    if (this.validate(item)) {
      this.items.set(id, item)
      return true
    }
    return false
  }
}

// Getters and setters
class Temperature {
  private _celsius: number = 0

  get celsius(): number {
    return this._celsius
  }

  set celsius(value: number) {
    this._celsius = value
  }

  get fahrenheit(): number {
    return (this._celsius * 9) / 5 + 32
  }

  set fahrenheit(value: number) {
    this._celsius = ((value - 32) * 5) / 9
  }

  get kelvin(): number {
    return this._celsius + 273.15
  }

  set kelvin(value: number) {
    this._celsius = value - 273.15
  }
}

// Combined modifiers
class SecureDocument {
  public readonly id: string
  static #counter: number = 0
  protected readonly createdAt: Date
  private _content: string = ''

  constructor() {
    this.id = `doc-${++SecureDocument.#counter}`
    this.createdAt = new Date()
  }

  public get content(): string {
    return this._content
  }

  protected set content(value: string) {
    this._content = value
  }

  public static getDocumentCount(): number {
    return SecureDocument.#counter
  }
}

// Exported class with modifiers
export class UserAccount {
  public readonly id: string
  private email: string
  protected role: 'admin' | 'user' | 'guest'

  constructor(id: string, email: string, role: 'admin' | 'user' | 'guest' = 'user') {
    this.id = id
    this.email = email
    this.role = role
  }

  public getEmail(): string {
    return this.email
  }

  public setEmail(email: string): void {
    if (this.validateEmail(email)) {
      this.email = email
    }
  }

  private validateEmail(email: string): boolean {
    return email.includes('@')
  }

  protected isAdmin(): boolean {
    return this.role === 'admin'
  }
}
