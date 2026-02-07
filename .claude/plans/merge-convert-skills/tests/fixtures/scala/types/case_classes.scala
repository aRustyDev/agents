// Case Classes in Scala
//
// Demonstrates case class patterns - immutable data containers.

package examples.types

// Simple case class
case class Point(x: Int, y: Int)

// Case class with type parameters
case class Pair[A, B](first: A, second: B)

// Case class with default values
case class Config(
  host: String = "localhost",
  port: Int = 8080,
  timeout: Long = 30000
)

// Nested case classes
case class Address(
  street: String,
  city: String,
  zipCode: String
)

case class Person(
  name: String,
  age: Int,
  address: Address
)

// Case class with private fields
case class User(
  id: Long,
  username: String,
  private val passwordHash: String
) {
  def checkPassword(password: String): Boolean =
    password.hashCode.toString == passwordHash
}

// Case class with methods
case class Rectangle(width: Double, height: Double) {
  def area: Double = width * height
  def perimeter: Double = 2 * (width + height)
  def scale(factor: Double): Rectangle = Rectangle(width * factor, height * factor)
}

// Case class with copy examples
object CaseClassExamples {
  val original = Point(1, 2)
  val modified = original.copy(x = 10)

  val config = Config()
  val customConfig = config.copy(port = 9000)

  // Pattern matching with case classes
  def describe(point: Point): String = point match {
    case Point(0, 0) => "origin"
    case Point(0, y) => s"on y-axis at $y"
    case Point(x, 0) => s"on x-axis at $x"
    case Point(x, y) => s"at ($x, $y)"
  }

  // Extractors
  def extractPair[A, B](pair: Pair[A, B]): (A, B) = pair match {
    case Pair(a, b) => (a, b)
  }
}

// Case class with validation
case class Email private(value: String)

object Email {
  def apply(value: String): Either[String, Email] =
    if (value.contains("@")) Right(new Email(value))
    else Left("Invalid email format")
}

// Case class with variance
case class Box[+A](value: A) {
  def map[B](f: A => B): Box[B] = Box(f(value))
}

// Case class extending trait
sealed trait Shape
case class Circle(radius: Double) extends Shape
case class Square(side: Double) extends Shape
case class Triangle(a: Double, b: Double, c: Double) extends Shape
