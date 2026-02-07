// Traits and Objects in Scala
//
// Demonstrates trait-based composition and companion objects.

package examples.oop_fp

// Basic trait
trait Greeting {
  def greet(name: String): String
}

// Trait with implementation
trait Logger {
  def log(message: String): Unit = println(s"[LOG] $message")
  def warn(message: String): Unit = println(s"[WARN] $message")
  def error(message: String): Unit = println(s"[ERROR] $message")
}

// Trait with abstract and concrete members
trait Identifiable {
  def id: String  // Abstract
  def shortId: String = id.take(8)  // Concrete
}

// Trait inheritance
trait Persistable extends Identifiable {
  def save(): Unit
  def delete(): Unit
}

// Self-type annotation
trait Service {
  self: Logger =>  // Must be mixed with Logger

  def perform(): Unit = {
    log("Starting service")
    doWork()
    log("Service completed")
  }

  protected def doWork(): Unit
}

// Mixin composition
trait Timed {
  def timed[A](name: String)(block: => A): A = {
    val start = System.currentTimeMillis()
    val result = block
    val elapsed = System.currentTimeMillis() - start
    println(s"$name took ${elapsed}ms")
    result
  }
}

trait Retryable {
  def retry[A](times: Int)(block: => A): A = {
    var attempts = 0
    var lastError: Throwable = null
    while (attempts < times) {
      try {
        return block
      } catch {
        case e: Exception =>
          lastError = e
          attempts += 1
      }
    }
    throw lastError
  }
}

// Companion object
class Counter private (private var count: Int) {
  def increment(): Unit = count += 1
  def decrement(): Unit = count -= 1
  def value: Int = count
}

object Counter {
  def apply(): Counter = new Counter(0)
  def apply(initial: Int): Counter = new Counter(initial)

  // Factory methods
  def zero: Counter = Counter(0)
  def fromString(s: String): Option[Counter] =
    s.toIntOption.map(Counter(_))
}

// Object as module
object MathUtils {
  val Pi: Double = 3.14159
  val E: Double = 2.71828

  def square(x: Double): Double = x * x
  def cube(x: Double): Double = x * x * x
  def factorial(n: Int): Long = (1L to n).product
}

// Object with trait implementation
trait Serializer[A] {
  def serialize(a: A): String
  def deserialize(s: String): Option[A]
}

object IntSerializer extends Serializer[Int] {
  def serialize(a: Int): String = a.toString
  def deserialize(s: String): Option[Int] = s.toIntOption
}

object StringSerializer extends Serializer[String] {
  def serialize(a: String): String = s""""$a""""
  def deserialize(s: String): Option[String] =
    if (s.startsWith("\"") && s.endsWith("\""))
      Some(s.drop(1).dropRight(1))
    else None
}

// Sealed trait with companion objects
sealed trait Result[+A]
case class Success[A](value: A) extends Result[A]
case class Failure(error: String) extends Result[Nothing]

object Result {
  def success[A](value: A): Result[A] = Success(value)
  def failure(error: String): Result[Nothing] = Failure(error)

  def fromOption[A](opt: Option[A], error: String): Result[A] =
    opt.map(Success(_)).getOrElse(Failure(error))

  def fromTry[A](t: scala.util.Try[A]): Result[A] = t match {
    case scala.util.Success(value) => Success(value)
    case scala.util.Failure(ex) => Failure(ex.getMessage)
  }
}

// Abstract class with companion
abstract class Animal(val name: String) {
  def speak: String
  def move: String
}

object Animal {
  def dog(name: String): Animal = new Animal(name) {
    def speak: String = "Woof!"
    def move: String = "Running"
  }

  def cat(name: String): Animal = new Animal(name) {
    def speak: String = "Meow!"
    def move: String = "Sneaking"
  }
}

// Stackable modifications using traits
trait Queue[A] {
  def get(): A
  def put(a: A): Unit
}

class BasicQueue[A] extends Queue[A] {
  private val items = scala.collection.mutable.ListBuffer[A]()

  def get(): A = items.remove(0)
  def put(a: A): Unit = items += a
}

trait Doubling extends Queue[Int] {
  abstract override def put(a: Int): Unit = super.put(a * 2)
}

trait Incrementing extends Queue[Int] {
  abstract override def put(a: Int): Unit = super.put(a + 1)
}

trait Filtering extends Queue[Int] {
  abstract override def put(a: Int): Unit =
    if (a >= 0) super.put(a)
}

// Usage: new BasicQueue[Int] with Doubling with Filtering
// Linearization determines order of trait application

// Type class instance in companion
case class Person(name: String, age: Int)

object Person {
  // Type class instances in companion object
  implicit val ordering: Ordering[Person] =
    Ordering.by(p => (p.name, p.age))

  implicit val show: Show[Person] = new Show[Person] {
    def show(p: Person): String = s"${p.name} (${p.age})"
  }
}

trait Show[A] {
  def show(a: A): String
}

object Show {
  def apply[A](implicit s: Show[A]): Show[A] = s
}
