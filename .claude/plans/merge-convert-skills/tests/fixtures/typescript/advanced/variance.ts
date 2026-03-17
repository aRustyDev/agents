// Type variance: covariance, contravariance, invariance

// Covariance (out) - subtypes flow in the same direction
// Arrays are covariant in their element type (for reading)
interface Animal {
  name: string
}

interface Dog extends Animal {
  breed: string
}

interface Cat extends Animal {
  indoor: boolean
}

// Covariant: Dog[] is assignable to Animal[]
const dogs: Dog[] = [{ name: 'Rex', breed: 'German Shepherd' }]
const animals: readonly Animal[] = dogs // OK - covariant

// Contravariance (in) - subtypes flow in opposite direction
// Function parameters are contravariant
type AnimalHandler = (animal: Animal) => void
type DogHandler = (dog: Dog) => void

// Contravariant: AnimalHandler is assignable to DogHandler
const handleAnimal: AnimalHandler = (animal) => console.log(animal.name)
const handleDog: DogHandler = handleAnimal // OK - contravariant

// Invariance - neither covariant nor contravariant
// Mutable arrays are invariant
interface MutableBox<T> {
  value: T
  setValue(value: T): void
}

// Invariant: MutableBox<Dog> is NOT assignable to MutableBox<Animal>
// Because setValue is contravariant while value is covariant

// Bivariance - both covariant and contravariant (TypeScript methods)
interface EventHandler {
  // Methods are bivariant in TypeScript (for compatibility)
  handle(event: Event): void
}

// Explicit variance annotations (TypeScript 4.7+)
interface Producer<out T> {
  produce(): T
}

interface Consumer<in T> {
  consume(value: T): void
}

interface Transformer<in T, out U> {
  transform(input: T): U
}

// Producer is covariant in T
const dogProducer: Producer<Dog> = {
  produce: () => ({ name: 'Rex', breed: 'Poodle' }),
}
const animalProducer: Producer<Animal> = dogProducer // OK

// Consumer is contravariant in T
const animalConsumer: Consumer<Animal> = {
  consume: (animal) => console.log(animal.name),
}
const dogConsumer: Consumer<Dog> = animalConsumer // OK

// Practical example: event system
interface Event {
  timestamp: number
}

interface MouseEvent extends Event {
  x: number
  y: number
}

interface KeyboardEvent extends Event {
  key: string
}

// Covariant event emitter (produces events)
interface EventEmitter<out T extends Event> {
  listen(callback: (event: T) => void): void
}

// Contravariant event handler (consumes events)
interface EventListener<in T extends Event> {
  handle(event: T): void
}

// Function type variance
type Comparator<T> = (a: T, b: T) => number

// Comparator<Animal> can be used where Comparator<Dog> is expected
const animalComparator: Comparator<Animal> = (a, b) => a.name.localeCompare(b.name)
const dogComparator: Comparator<Dog> = animalComparator

// Return type covariance
interface Factory<T> {
  create(): T
}

class DogFactory implements Factory<Dog> {
  create(): Dog {
    return { name: 'Buddy', breed: 'Labrador' }
  }
}

const factory: Factory<Animal> = new DogFactory() // OK - covariant return

// Complex variance in generic classes
class Repository<T> {
  private items: T[] = []

  // Covariant usage (return)
  getAll(): T[] {
    return [...this.items]
  }

  // Contravariant usage (parameter)
  add(item: T): void {
    this.items.push(item)
  }

  // This makes Repository invariant in T
}

export {
  type Animal,
  type Dog,
  type Cat,
  type AnimalHandler,
  type DogHandler,
  type MutableBox,
  type Producer,
  type Consumer,
  type Transformer,
  type EventEmitter,
  type EventListener,
  type Comparator,
  type Factory,
  DogFactory,
  Repository,
  handleAnimal,
  handleDog,
  dogProducer,
  animalProducer,
  animalConsumer,
  dogConsumer,
  animalComparator,
  dogComparator,
}
