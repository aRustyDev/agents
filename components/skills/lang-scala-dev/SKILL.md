---
name: lang-scala-dev
description: Foundational Scala patterns covering core syntax, type system, pattern matching, collections, functional operations, and common idioms. Use when writing Scala code, understanding functional and object-oriented paradigms, or needing guidance on which specialized Scala skill to use. This is the entry point for Scala development.
---

# Scala Fundamentals

Foundational Scala patterns and core language features. This skill serves as both a reference for common patterns and an index to specialized Scala skills.

## Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     Scala Skill Hierarchy                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│                   ┌────────────────────┐                        │
│                   │  lang-scala-dev    │ ◄── You are here       │
│                   │   (foundation)     │                        │
│                   └──────────┬─────────┘                        │
│                              │                                  │
│            ┌─────────────────┴─────────────────┐               │
│            │                                   │               │
│            ▼                                   ▼               │
│   ┌─────────────────┐                ┌─────────────────┐       │
│   │    patterns     │                │     library     │       │
│   │      -dev       │                │       -dev      │       │
│   └─────────────────┘                └─────────────────┘       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**This skill covers:**
- Classes, traits, objects, and case classes
- Pattern matching and sealed hierarchies
- Type system fundamentals
- Collections and functional operations
- Implicits and type classes
- For-comprehensions and monadic operations
- Try, Either, and Option for error handling

**This skill does NOT cover (see specialized skills):**
- sbt configuration and dependencies → `lang-scala-patterns-dev`
- Best practices and advanced patterns → `lang-scala-patterns-dev`
- Library/package publishing → `lang-scala-library-dev`
- Cats, ZIO, or other effect libraries → ecosystem-specific skills
- Spark, Akka/Pekko → framework-specific skills

---

## Quick Reference

| Task | Syntax |
|------|--------|
| Define class | `class Name(val x: Int)` |
| Define trait | `trait Name { def method: Type }` |
| Define object | `object Name { ... }` |
| Case class | `case class Name(x: Int, y: String)` |
| Pattern match | `x match { case Pattern => expr }` |
| Option type | `Option[T]`, `Some(x)`, `None` |
| Either type | `Either[L, R]`, `Left(x)`, `Right(y)` |
| Try type | `Try[T]`, `Success(x)`, `Failure(e)` |
| Function literal | `(x: Int) => x * 2` |
| For-comprehension | `for { x <- opt } yield x * 2` |

---

## Skill Routing

Use this table to find the right specialized skill:

| When you need to... | Use this skill |
|---------------------|----------------|
| Configure sbt, add dependencies | `lang-scala-patterns-dev` |
| Advanced type-level programming | `lang-scala-patterns-dev` |
| Publish libraries to Maven/Sonatype | `lang-scala-library-dev` |
| Work with Cats/ZIO effect systems | Effect library-specific skills |
| Build Spark applications | `lang-scala-spark-dev` |
| Work with Akka/Pekko actors | `lang-scala-akka-dev` |

---

## Classes and Objects

### Basic Classes

```scala
// Primary constructor in class definition
class Person(val name: String, val age: Int) {
  // Secondary constructor
  def this(name: String) = this(name, 0)

  // Method
  def greet(): String = s"Hello, I'm $name"

  // Computed property
  def description: String = s"$name is $age years old"
}

// Creating instances
val alice = new Person("Alice", 30)
println(alice.greet())
```

### Case Classes

```scala
// Automatically generates:
// - apply method (no 'new' needed)
// - unapply (for pattern matching)
// - toString, equals, hashCode
// - copy method
case class User(id: Int, name: String, email: String)

// Creating instances (no 'new')
val user = User(1, "Alice", "alice@example.com")

// Copy with modifications
val updated = user.copy(email = "newemail@example.com")

// Pattern matching
user match {
  case User(id, name, _) => println(s"User $id: $name")
}
```

### Objects (Singletons)

```scala
// Companion object (same name as class)
object User {
  def fromString(s: String): Option[User] = {
    s.split(",") match {
      case Array(id, name, email) =>
        Some(User(id.toInt, name, email))
      case _ => None
    }
  }
}

// Standalone object
object Config {
  val MaxRetries = 3
  val Timeout = 5000
}

// Usage
val user = User.fromString("1,Alice,alice@example.com")
val timeout = Config.Timeout
```

### Traits (Interfaces)

```scala
// Basic trait
trait Greeter {
  def greet(): String
}

// Trait with implementation
trait Logger {
  def log(msg: String): Unit = println(s"[LOG] $msg")
}

// Trait with abstract and concrete members
trait Timestamped {
  val timestamp: Long

  def isOlderThan(other: Timestamped): Boolean =
    this.timestamp < other.timestamp
}

// Class implementing traits
class Person(val name: String) extends Greeter with Logger {
  def greet(): String = s"Hello, I'm $name"
}

// Mixing in traits
val person = new Person("Alice") with Timestamped {
  val timestamp = System.currentTimeMillis()
}
```

---

## Pattern Matching

### Basic Pattern Matching

```scala
val x = 5

x match {
  case 1 => "one"
  case 2 => "two"
  case n if n > 10 => s"greater than ten: $n"
  case _ => "something else"
}

// Type patterns
def describe(x: Any): String = x match {
  case s: String => s"String: $s"
  case i: Int => s"Int: $i"
  case _: Boolean => "Boolean"
  case _ => "Unknown"
}
```

### Destructuring

```scala
// Tuple destructuring
val pair = (1, "Alice")
val (id, name) = pair

pair match {
  case (1, n) => s"ID is 1, name is $n"
  case (id, "Alice") => s"Alice with ID $id"
  case (id, name) => s"$name with ID $id"
}

// Case class destructuring
case class Point(x: Int, y: Int)

val point = Point(3, 4)
point match {
  case Point(0, 0) => "origin"
  case Point(x, 0) => s"on x-axis at $x"
  case Point(0, y) => s"on y-axis at $y"
  case Point(x, y) => s"at ($x, $y)"
}

// Nested patterns
case class Address(city: String, zip: String)
case class User(name: String, address: Address)

val user = User("Alice", Address("NYC", "10001"))
user match {
  case User(name, Address("NYC", zip)) =>
    s"$name lives in NYC, zip: $zip"
  case User(name, Address(city, _)) =>
    s"$name lives in $city"
}
```

### Guards and Patterns

```scala
// Pattern guards
def classify(x: Int): String = x match {
  case n if n < 0 => "negative"
  case 0 => "zero"
  case n if n % 2 == 0 => "positive even"
  case _ => "positive odd"
}

// @ binding (capture and match)
def processValue(opt: Option[Int]): String = opt match {
  case some @ Some(x) if x > 10 =>
    s"Large value: $some"
  case Some(x) =>
    s"Small value: $x"
  case None =>
    "No value"
}
```

### Sealed Traits (Exhaustive Matching)

```scala
// Sealed trait - all implementations must be in same file
sealed trait Shape
case class Circle(radius: Double) extends Shape
case class Rectangle(width: Double, height: Double) extends Shape
case class Triangle(base: Double, height: Double) extends Shape

// Compiler warns if not exhaustive
def area(shape: Shape): Double = shape match {
  case Circle(r) => Math.PI * r * r
  case Rectangle(w, h) => w * h
  case Triangle(b, h) => 0.5 * b * h
  // If we forgot a case, compiler would warn
}
```

---

## Type System

### Basic Types

```scala
// Primitive types
val int: Int = 42
val long: Long = 42L
val double: Double = 3.14
val float: Float = 3.14f
val boolean: Boolean = true
val char: Char = 'A'
val string: String = "hello"

// Unit (like void)
def sideEffect(): Unit = println("hello")

// Nothing (bottom type - never returns)
def fail(msg: String): Nothing = throw new Exception(msg)

// Any (top type - supertype of all types)
val anything: Any = "could be anything"

// AnyVal (supertype of all value types)
// AnyRef (supertype of all reference types)
```

### Type Parameters (Generics)

```scala
// Generic class
class Box[T](val value: T) {
  def map[U](f: T => U): Box[U] = new Box(f(value))
}

val intBox = new Box(42)
val stringBox = intBox.map(_.toString)

// Generic method
def identity[T](x: T): T = x

// Multiple type parameters
def pair[A, B](a: A, b: B): (A, B) = (a, b)
```

### Variance

```scala
// Covariance (+)
// If A <: B, then Box[A] <: Box[B]
class Box[+T](val value: T)

// Box[String] can be used as Box[Any]
val stringBox: Box[String] = new Box("hello")
val anyBox: Box[Any] = stringBox  // OK

// Contravariance (-)
// If A <: B, then Processor[B] <: Processor[A]
trait Processor[-T] {
  def process(value: T): Unit
}

// Invariance (no annotation)
class Container[T](var value: T)
```

### Type Bounds

```scala
// Upper bound (T must be a subtype of Number)
def max[T <: Comparable[T]](a: T, b: T): T =
  if (a.compareTo(b) > 0) a else b

// Lower bound (T must be a supertype of A)
class Animal
class Dog extends Animal

def addDog[T >: Dog](list: List[T], dog: Dog): List[T] =
  dog :: list

// View bounds (implicit conversion)
def sorted[T <% Ordered[T]](list: List[T]): List[T] =
  list.sorted

// Context bounds (implicit parameter)
def show[T: Ordering](list: List[T]): String =
  list.sorted.mkString(", ")
```

### Type Aliases

```scala
// Simple type alias
type UserId = Int
type UserMap = Map[UserId, String]

// Type alias with parameters
type Result[T] = Either[String, T]

// Structural types
type Closeable = { def close(): Unit }

def useResource(r: Closeable): Unit = {
  try {
    // use resource
  } finally {
    r.close()
  }
}
```

---

## Collections

### Immutable Collections

```scala
// List (linked list)
val numbers = List(1, 2, 3, 4, 5)
val extended = 0 :: numbers  // prepend
val head = numbers.head       // 1
val tail = numbers.tail       // List(2, 3, 4, 5)

// Vector (indexed sequence)
val vec = Vector(1, 2, 3, 4, 5)
val updated = vec.updated(2, 10)  // Vector(1, 2, 10, 4, 5)

// Set
val set = Set(1, 2, 3, 3, 2)  // Set(1, 2, 3)
val added = set + 4            // Set(1, 2, 3, 4)
val removed = set - 2          // Set(1, 3)

// Map
val map = Map("a" -> 1, "b" -> 2)
val withC = map + ("c" -> 3)
val withoutA = map - "a"
val valueOpt = map.get("a")    // Option[Int]
```

### Mutable Collections

```scala
import scala.collection.mutable

// Mutable List (ArrayBuffer)
val buffer = mutable.ArrayBuffer(1, 2, 3)
buffer += 4              // append
buffer.append(5, 6)      // append multiple
buffer -= 2              // remove

// Mutable Set
val mutableSet = mutable.Set(1, 2, 3)
mutableSet.add(4)
mutableSet.remove(1)

// Mutable Map
val mutableMap = mutable.Map("a" -> 1)
mutableMap("b") = 2      // add/update
mutableMap += ("c" -> 3)
mutableMap -= "a"
```

### Collection Operations

```scala
val numbers = List(1, 2, 3, 4, 5)

// Transformation
numbers.map(_ * 2)                    // List(2, 4, 6, 8, 10)
numbers.flatMap(n => List(n, n * 10)) // List(1, 10, 2, 20, ...)
numbers.filter(_ % 2 == 0)            // List(2, 4)
numbers.filterNot(_ % 2 == 0)         // List(1, 3, 5)

// Folding/Reducing
numbers.foldLeft(0)(_ + _)            // 15
numbers.foldRight(0)(_ + _)           // 15
numbers.reduce(_ + _)                 // 15
numbers.sum                           // 15

// Grouping
numbers.groupBy(_ % 2)                // Map(1 -> List(1,3,5), 0 -> List(2,4))
numbers.partition(_ % 2 == 0)         // (List(2,4), List(1,3,5))

// Taking/Dropping
numbers.take(3)                       // List(1, 2, 3)
numbers.drop(2)                       // List(3, 4, 5)
numbers.takeWhile(_ < 4)              // List(1, 2, 3)
numbers.dropWhile(_ < 4)              // List(4, 5)

// Searching
numbers.find(_ > 3)                   // Some(4)
numbers.exists(_ > 3)                 // true
numbers.forall(_ > 0)                 // true

// Zipping
val letters = List("a", "b", "c")
numbers.zip(letters)                  // List((1,"a"), (2,"b"), (3,"c"))
```

---

## Functional Programming

### Functions as Values

```scala
// Function literal
val double = (x: Int) => x * 2

// Multi-parameter function
val add = (x: Int, y: Int) => x + y

// Function type annotation
val greet: String => String = name => s"Hello, $name"

// Multi-line function
val complex: Int => String = { n =>
  val doubled = n * 2
  val squared = doubled * doubled
  s"Result: $squared"
}

// Partially applied functions
def multiply(x: Int, y: Int): Int = x * y
val double2 = multiply(2, _: Int)  // Int => Int
double2(5)  // 10
```

### Higher-Order Functions

```scala
// Function that takes a function
def twice(f: Int => Int, x: Int): Int = f(f(x))

twice(_ + 1, 5)  // 7

// Function that returns a function
def multiplier(factor: Int): Int => Int =
  (x: Int) => x * factor

val triple = multiplier(3)
triple(5)  // 15

// Currying
def add(x: Int)(y: Int): Int = x + y
val add5 = add(5) _
add5(3)  // 8
```

### Method vs Function

```scala
// Method (belongs to class/object)
def methodDouble(x: Int): Int = x * 2

// Convert method to function
val funcDouble = methodDouble _

// Method with multiple parameter lists
def curriedAdd(x: Int)(y: Int): Int = x + y

// Partially apply
val add5 = curriedAdd(5) _
```

---

## Option, Either, and Try

### Option

```scala
// Creating Options
val some: Option[Int] = Some(42)
val none: Option[Int] = None

// Safe operations
def findUser(id: Int): Option[String] =
  if (id == 1) Some("Alice") else None

// Pattern matching
findUser(1) match {
  case Some(name) => println(s"Found: $name")
  case None => println("Not found")
}

// Functional operations
val result = findUser(1)
  .map(_.toUpperCase)
  .filter(_.startsWith("A"))
  .getOrElse("Unknown")

// Chaining
val user = for {
  name <- findUser(1)
  email <- findEmail(name)
} yield s"$name <$email>"

// Common methods
some.isDefined         // true
none.isEmpty          // true
some.get              // 42 (unsafe - can throw)
some.getOrElse(0)     // 42
none.getOrElse(0)     // 0
some.fold(0)(_ * 2)   // 84
```

### Either

```scala
// Left represents error, Right represents success
type Result[T] = Either[String, T]

def divide(a: Int, b: Int): Result[Int] =
  if (b == 0) Left("Division by zero")
  else Right(a / b)

// Pattern matching
divide(10, 2) match {
  case Right(result) => println(s"Result: $result")
  case Left(error) => println(s"Error: $error")
}

// Functional operations (right-biased)
val result = divide(10, 2)
  .map(_ * 2)           // only applies to Right
  .getOrElse(0)

// For-comprehension
val computation = for {
  a <- divide(10, 2)    // Right(5)
  b <- divide(20, 4)    // Right(5)
} yield a + b           // Right(10)

// Converting
val opt: Option[Int] = Right(42).toOption
val either: Either[String, Int] = Some(42).toRight("Error")
```

### Try

```scala
import scala.util.{Try, Success, Failure}

// Wraps operations that might throw
def parseNumber(s: String): Try[Int] = Try(s.toInt)

parseNumber("42") match {
  case Success(n) => println(s"Parsed: $n")
  case Failure(e) => println(s"Error: ${e.getMessage}")
}

// Functional operations
val result = Try(readFile("config.json"))
  .map(parseJson)
  .map(_.validate)
  .getOrElse(defaultConfig)

// Recovering from failures
val recovered = Try(dangerousOperation())
  .recover {
    case _: IOException => fallbackValue
  }
  .recoverWith {
    case _: TimeoutException => Try(alternativeOperation())
  }

// Converting
val opt: Option[Int] = Try(42).toOption
val either: Either[Throwable, Int] = Try(42).toEither
```

---

## For-Comprehensions

### Basic For-Comprehension

```scala
// Desugars to flatMap and map
val result = for {
  x <- Some(1)
  y <- Some(2)
  z <- Some(3)
} yield x + y + z  // Some(6)

// Equivalent to:
Some(1).flatMap { x =>
  Some(2).flatMap { y =>
    Some(3).map { z =>
      x + y + z
    }
  }
}
```

### Guards and Filters

```scala
// With if guard
val evens = for {
  x <- List(1, 2, 3, 4, 5)
  if x % 2 == 0
} yield x * 2  // List(4, 8)

// Multiple generators
val pairs = for {
  x <- List(1, 2, 3)
  y <- List("a", "b")
} yield (x, y)  // List((1,a), (1,b), (2,a), (2,b), (3,a), (3,b))

// Pattern matching in generator
case class User(name: String, age: Int)
val users = List(User("Alice", 30), User("Bob", 25))

val names = for {
  User(name, age) <- users
  if age >= 30
} yield name  // List("Alice")
```

### Error Handling with For

```scala
// Chaining Options
def findUser(id: Int): Option[User] = ???
def findAddress(user: User): Option[Address] = ???
def findZip(address: Address): Option[String] = ???

val zip = for {
  user <- findUser(1)
  address <- findAddress(user)
  zip <- findZip(address)
} yield zip  // Option[String]

// Chaining Either
def validateName(name: String): Either[String, String] = ???
def validateEmail(email: String): Either[String, String] = ???

val validated = for {
  name <- validateName("Alice")
  email <- validateEmail("alice@example.com")
} yield User(name, email)  // Either[String, User]

// Chaining Try
def readConfig(): Try[Config] = ???
def parseConfig(raw: Config): Try[ParsedConfig] = ???
def validateConfig(parsed: ParsedConfig): Try[ValidConfig] = ???

val config = for {
  raw <- readConfig()
  parsed <- parseConfig(raw)
  valid <- validateConfig(parsed)
} yield valid  // Try[ValidConfig]
```

---

## Implicits

### Implicit Parameters

```scala
// Define implicit value
implicit val timeout: Int = 5000

// Function with implicit parameter
def fetchData(url: String)(implicit timeout: Int): String = {
  s"Fetching $url with timeout $timeout"
}

// Call without explicit parameter
fetchData("http://example.com")  // Uses implicit timeout

// Context bounds (syntactic sugar)
def show[T: Ordering](list: List[T]): String = {
  // Equivalent to: def show[T](list: List[T])(implicit ord: Ordering[T])
  list.sorted.mkString(", ")
}
```

### Implicit Conversions

```scala
// Implicit conversion (use sparingly)
implicit def stringToInt(s: String): Int = s.toInt

val x: Int = "42"  // Automatically converts

// Extension methods via implicit class
implicit class RichString(val s: String) extends AnyVal {
  def shout: String = s.toUpperCase + "!"
  def repeat(n: Int): String = s * n
}

"hello".shout      // "HELLO!"
"hi".repeat(3)     // "hihihi"
```

### Type Classes

```scala
// Define type class
trait Show[T] {
  def show(value: T): String
}

// Provide instances
object Show {
  implicit val intShow: Show[Int] = new Show[Int] {
    def show(value: Int): String = value.toString
  }

  implicit val stringShow: Show[String] = new Show[String] {
    def show(value: String): String = s"\"$value\""
  }

  // Generic instance
  implicit def listShow[T](implicit showT: Show[T]): Show[List[T]] =
    new Show[List[T]] {
      def show(list: List[T]): String =
        list.map(showT.show).mkString("[", ", ", "]")
    }
}

// Use type class
def print[T](value: T)(implicit show: Show[T]): Unit =
  println(show.show(value))

// Or with context bound
def print2[T: Show](value: T): Unit = {
  val show = implicitly[Show[T]]
  println(show.show(value))
}

print(42)              // "42"
print("hello")         // "\"hello\""
print(List(1, 2, 3))   // "[1, 2, 3]"
```

---

## Common Patterns

### Companion Object Pattern

```scala
case class User(id: Int, name: String, email: String)

object User {
  // Factory methods
  def create(name: String, email: String): User =
    User(nextId(), name, email)

  // Validation
  def validate(user: User): Either[String, User] =
    if (user.email.contains("@")) Right(user)
    else Left("Invalid email")

  // Type class instances
  implicit val ordering: Ordering[User] =
    Ordering.by(_.name)

  private var counter = 0
  private def nextId(): Int = {
    counter += 1
    counter
  }
}
```

### Builder Pattern

```scala
case class HttpRequest(
  url: String,
  method: String = "GET",
  headers: Map[String, String] = Map.empty,
  body: Option[String] = None
)

class RequestBuilder private (request: HttpRequest) {
  def withMethod(method: String): RequestBuilder =
    new RequestBuilder(request.copy(method = method))

  def withHeader(key: String, value: String): RequestBuilder =
    new RequestBuilder(request.copy(
      headers = request.headers + (key -> value)
    ))

  def withBody(body: String): RequestBuilder =
    new RequestBuilder(request.copy(body = Some(body)))

  def build(): HttpRequest = request
}

object RequestBuilder {
  def apply(url: String): RequestBuilder =
    new RequestBuilder(HttpRequest(url))
}

// Usage
val request = RequestBuilder("https://api.example.com")
  .withMethod("POST")
  .withHeader("Content-Type", "application/json")
  .withBody("""{"name": "Alice"}""")
  .build()
```

### Smart Constructor Pattern

```scala
// Ensure invariants at construction time
class Email private (val value: String)

object Email {
  def apply(s: String): Either[String, Email] =
    if (s.contains("@")) Right(new Email(s))
    else Left("Invalid email format")

  def unsafe(s: String): Email =
    apply(s).getOrElse(throw new IllegalArgumentException("Invalid email"))
}

// Usage
val email = Email("alice@example.com")  // Either[String, Email]
email match {
  case Right(e) => println(s"Valid: ${e.value}")
  case Left(err) => println(s"Error: $err")
}
```

### Loan Pattern (Resource Management)

```scala
import scala.util.{Try, Using}

// Manual loan pattern
def withResource[R <: AutoCloseable, T](resource: => R)(f: R => T): Try[T] =
  Try {
    val r = resource
    try f(r)
    finally r.close()
  }

// Usage
withResource(new FileInputStream("file.txt")) { stream =>
  // Use stream
  stream.read()
}

// Scala 2.13+ Using
Using(new FileInputStream("file.txt")) { stream =>
  stream.read()
}

// Multiple resources
Using.Manager { use =>
  val in = use(new FileInputStream("in.txt"))
  val out = use(new FileOutputStream("out.txt"))
  // Use both streams
}
```

---

## Troubleshooting

### Type Mismatch Errors

```scala
// Problem: Type mismatch
val x: Int = "42"  // Error: String is not Int

// Fix: Explicit conversion
val x: Int = "42".toInt

// Problem: Missing implicit
def sort[T](list: List[T]): List[T] = list.sorted
// Error: No implicit Ordering[T]

// Fix: Add context bound
def sort[T: Ordering](list: List[T]): List[T] = list.sorted
```

### NullPointerException

```scala
// Problem: Null values
val name: String = null
name.toUpperCase  // NullPointerException

// Fix: Use Option
val name: Option[String] = None
name.map(_.toUpperCase)  // Safe

// Converting from Java
val javaValue: String = getFromJava()
val safeValue: Option[String] = Option(javaValue)
```

### Match Not Exhaustive

```scala
// Problem: Non-exhaustive match
sealed trait Status
case object Pending extends Status
case object Approved extends Status

def handle(s: Status): String = s match {
  case Pending => "pending"
  // Warning: match may not be exhaustive
}

// Fix: Add all cases or wildcard
def handle(s: Status): String = s match {
  case Pending => "pending"
  case Approved => "approved"
}
```

### Implicit Resolution Issues

```scala
// Problem: Ambiguous implicits
implicit val x: Int = 1
implicit val y: Int = 2

def useImplicit(implicit n: Int): Int = n
// Error: Ambiguous implicit values

// Fix: Be more specific or rename
implicit val defaultTimeout: Int = 1
implicit val maxRetries: Int = 2

def fetch(implicit timeout: Int): Unit = ???
```

### Value Discarding

```scala
// Problem: Non-Unit value discarded
def compute(): Int = 42

compute()  // Warning: value discarded

// Fix: Use result or explicitly ignore
val _ = compute()
```

---

## References

- [Scala Documentation](https://docs.scala-lang.org/)
- [Scala Book](https://docs.scala-lang.org/scala3/book/introduction.html)
- [Scala Standard Library](https://www.scala-lang.org/api/current/)
- Specialized skills: `lang-scala-patterns-dev`, `lang-scala-library-dev`
