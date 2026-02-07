// Variance in Scala
//
// Demonstrates covariance (+T), contravariance (-T), and invariance.

package examples.types

// Covariant container (producer)
trait Producer[+T] {
  def produce: T
}

// Contravariant container (consumer)
trait Consumer[-T] {
  def consume(t: T): Unit
}

// Invariant container (both producer and consumer)
trait Processor[T] {
  def process(t: T): T
}

// Examples of covariance
sealed trait MyOption[+A] {
  def map[B](f: A => B): MyOption[B]
  def flatMap[B](f: A => MyOption[B]): MyOption[B]
  def getOrElse[B >: A](default: => B): B
}

case class MySome[+A](value: A) extends MyOption[A] {
  def map[B](f: A => B): MyOption[B] = MySome(f(value))
  def flatMap[B](f: A => MyOption[B]): MyOption[B] = f(value)
  def getOrElse[B >: A](default: => B): B = value
}

case object MyNone extends MyOption[Nothing] {
  def map[B](f: Nothing => B): MyOption[B] = MyNone
  def flatMap[B](f: Nothing => MyOption[B]): MyOption[B] = MyNone
  def getOrElse[B >: Nothing](default: => B): B = default
}

// Contravariance example: ordering
trait Ordering[-T] {
  def compare(x: T, y: T): Int

  // Contravariant on returns a new Ordering with the same comparison
  def on[U](f: U => T): Ordering[U] = (x: U, y: U) => compare(f(x), f(y))
}

object Ordering {
  implicit val intOrdering: Ordering[Int] = (x: Int, y: Int) => x - y
  implicit val stringOrdering: Ordering[String] = (x: String, y: String) => x.compareTo(y)

  // Person ordering by age (contravariant usage)
  case class Person(name: String, age: Int)
  val personByAge: Ordering[Person] = intOrdering.on(_.age)
}

// Function variance: Function1[-A, +B]
object FunctionVariance {
  // Covariant in return type (B)
  // If Dog <: Animal, then () => Dog <: () => Animal
  trait Animal
  class Dog extends Animal
  class Cat extends Animal

  val dogProducer: () => Dog = () => new Dog
  val animalProducer: () => Animal = dogProducer  // OK: covariant

  // Contravariant in argument type (A)
  // If Dog <: Animal, then Animal => Unit <: Dog => Unit
  val animalConsumer: Animal => Unit = (a: Animal) => println(a)
  val dogConsumer: Dog => Unit = animalConsumer  // OK: contravariant
}

// Covariant collection
trait ImmutableList[+A] {
  def head: A
  def tail: ImmutableList[A]
  def prepend[B >: A](elem: B): ImmutableList[B]  // Note: B >: A
}

// Mutable collection must be invariant
trait MutableList[A] {
  def head: A
  def tail: MutableList[A]
  def add(elem: A): Unit
  def update(index: Int, elem: A): Unit
}

// Combining variance with bounds
trait Container[+A] {
  def value: A
  def map[B](f: A => B): Container[B]
  def flatMap[B](f: A => Container[B]): Container[B]
}

case class Wrapper[+A](value: A) extends Container[A] {
  def map[B](f: A => B): Container[B] = Wrapper(f(value))
  def flatMap[B](f: A => Container[B]): Container[B] = f(value)
}

// Lower bound with contravariance
trait Sink[-A] {
  def write(a: A): Unit
  def contramap[B](f: B => A): Sink[B] = (b: B) => write(f(b))
}

// Phantom types (neither covariant nor contravariant in type param)
sealed trait State
trait Open extends State
trait Closed extends State

class Door[S <: State] private () {
  def open(implicit ev: S =:= Closed): Door[Open] = new Door[Open]
  def close(implicit ev: S =:= Open): Door[Closed] = new Door[Closed]
}

object Door {
  def closed: Door[Closed] = new Door[Closed]
}

// Variance inference in type aliases
object VarianceAliases {
  type StringProducer = Producer[String]
  type AnyConsumer = Consumer[Any]

  // These compile because of variance
  val sp: Producer[Any] = new Producer[String] { def produce = "hello" }
  val sc: Consumer[String] = new Consumer[Any] { def consume(a: Any) = () }
}
