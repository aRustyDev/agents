/**
 * Test fixtures for TypeScript class inheritance.
 */

// Base class
class Animal {
  protected name: string
  protected age: number

  constructor(name: string, age: number) {
    this.name = name
    this.age = age
  }

  speak(): void {
    console.log(`${this.name} makes a sound`)
  }

  getInfo(): string {
    return `${this.name} is ${this.age} years old`
  }
}

// Simple inheritance
class Dog extends Animal {
  private breed: string

  constructor(name: string, age: number, breed: string) {
    super(name, age)
    this.breed = breed
  }

  speak(): void {
    console.log(`${this.name} barks`)
  }

  fetch(): void {
    console.log(`${this.name} fetches the ball`)
  }

  getBreed(): string {
    return this.breed
  }
}

class Cat extends Animal {
  private indoor: boolean

  constructor(name: string, age: number, indoor: boolean = true) {
    super(name, age)
    this.indoor = indoor
  }

  speak(): void {
    console.log(`${this.name} meows`)
  }

  isIndoor(): boolean {
    return this.indoor
  }
}

// Abstract class
abstract class Shape {
  abstract area(): number
  abstract perimeter(): number

  describe(): string {
    return `This shape has area ${this.area()} and perimeter ${this.perimeter()}`
  }
}

class Rectangle extends Shape {
  constructor(
    private width: number,
    private height: number
  ) {
    super()
  }

  area(): number {
    return this.width * this.height
  }

  perimeter(): number {
    return 2 * (this.width + this.height)
  }
}

class Circle extends Shape {
  constructor(private radius: number) {
    super()
  }

  area(): number {
    return Math.PI * this.radius ** 2
  }

  perimeter(): number {
    return 2 * Math.PI * this.radius
  }
}

// Interface implementation
interface Printable {
  print(): void
}

interface Serializable {
  serialize(): string
  deserialize(data: string): void
}

class Document implements Printable, Serializable {
  private content: string = ''

  print(): void {
    console.log(this.content)
  }

  serialize(): string {
    return JSON.stringify({ content: this.content })
  }

  deserialize(data: string): void {
    const parsed = JSON.parse(data)
    this.content = parsed.content
  }
}

// Multi-level inheritance
class Vehicle {
  protected speed: number = 0

  accelerate(amount: number): void {
    this.speed += amount
  }

  brake(amount: number): void {
    this.speed = Math.max(0, this.speed - amount)
  }

  getSpeed(): number {
    return this.speed
  }
}

class Car extends Vehicle {
  protected wheels: number = 4

  honk(): void {
    console.log('Beep beep!')
  }
}

class SportsCar extends Car {
  private turbo: boolean = false

  enableTurbo(): void {
    this.turbo = true
  }

  accelerate(amount: number): void {
    const boost = this.turbo ? 2 : 1
    super.accelerate(amount * boost)
  }
}

// Generic class inheritance
class BaseRepository<T> {
  protected items: T[] = []

  add(item: T): void {
    this.items.push(item)
  }

  getAll(): T[] {
    return [...this.items]
  }
}

interface Entity {
  id: number
}

class EntityRepository<T extends Entity> extends BaseRepository<T> {
  findById(id: number): T | undefined {
    return this.items.find((item) => item.id === id)
  }

  removeById(id: number): boolean {
    const index = this.items.findIndex((item) => item.id === id)
    if (index !== -1) {
      this.items.splice(index, 1)
      return true
    }
    return false
  }
}

// Mixin pattern
type Constructor<T = object> = new (...args: unknown[]) => T

function Timestamped<TBase extends Constructor>(Base: TBase) {
  return class extends Base {
    createdAt = new Date()
    updatedAt = new Date()

    touch() {
      this.updatedAt = new Date()
    }
  }
}

function Tagged<TBase extends Constructor>(Base: TBase) {
  return class extends Base {
    tags: string[] = []

    addTag(tag: string) {
      this.tags.push(tag)
    }
  }
}

class BaseItem {
  name: string = ''
}

const TimestampedTaggedItem = Tagged(Timestamped(BaseItem))

// Exported classes
export abstract class BaseService<T> {
  abstract find(id: number): Promise<T | null>
  abstract save(entity: T): Promise<T>
  abstract delete(id: number): Promise<boolean>
}

export class UserService extends BaseService<{ id: number; name: string }> {
  async find(id: number): Promise<{ id: number; name: string } | null> {
    return { id, name: 'User' }
  }

  async save(entity: { id: number; name: string }): Promise<{ id: number; name: string }> {
    return entity
  }

  async delete(_id: number): Promise<boolean> {
    return true
  }
}
