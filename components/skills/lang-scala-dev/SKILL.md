---
name: lang-scala-dev
description: Foundational Scala patterns covering immutability, pattern matching, traits, case classes, for-comprehensions, and functional programming. Use when writing Scala code, understanding the type system, or needing guidance on which specialized Scala skill to use. This is the entry point for Scala development.
---

# Scala Fundamentals

## Overview

This is the **foundational skill** for Scala development. Use this skill when writing Scala code, understanding core language features, or determining which specialized Scala skill to use.

### Skill Hierarchy

```
lang-scala-dev (YOU ARE HERE - Foundational)
├── lang-scala-akka-dev (Akka actors, streams, clustering)
├── lang-scala-cats-dev (Cats FP library, type classes, effects)
├── lang-scala-zio-dev (ZIO effects, fibers, resources)
├── lang-scala-spark-dev (Apache Spark, distributed computing)
├── lang-scala-play-dev (Play Framework web applications)
└── lang-scala-testing-dev (ScalaTest, ScalaCheck, property testing)
```

### When to Use This Skill

- **Writing basic Scala code** - syntax, types, control flow
- **Understanding core language features** - pattern matching, traits, case classes
- **Learning Scala fundamentals** - immutability, functional programming
- **Determining skill routing** - which specialized skill to use
- **Troubleshooting common errors** - compilation issues, type errors

---

## Quick Reference

| Pattern | Syntax | Use Case |
|---------|--------|----------|
| **Immutable val** | `val x = 42` | Default variable declaration |
| **Mutable var** | `var x = 42` | When mutation is necessary |
| **Case class** | `case class User(name: String, age: Int)` | Data containers with pattern matching |
| **Pattern match** | `x match { case ... => ... }` | Destructuring, conditional logic |
| **Option** | `Option[A]`, `Some(value)`, `None` | Nullable value handling |
| **Either** | `Either[L, R]`, `Left(error)`, `Right(value)` | Error handling with context |
| **Try** | `Try { riskyOp }` | Exception handling |
| **For-comprehension** | `for { x <- opt1; y <- opt2 } yield x + y` | Sequential monadic operations |
| **Higher-order fn** | `list.map(f).filter(p)` | Function composition |
| **Trait** | `trait Logging { ... }` | Interface with implementation |
| **Object** | `object Utils { ... }` | Singleton, companion object |
| **Implicit (2.x)** | `implicit val ord: Ordering[A]` | Type class instances |
| **Given/Using (3.x)** | `given Ordering[A] with { ... }` | Scala 3 implicits |

---

## Skill Routing

| Task | Use This Skill | Rationale |
|------|---------------|-----------|
| Akka actors, streams, clustering | `lang-scala-akka-dev` | Specialized actor model patterns |
| Cats library, type classes, MTL | `lang-scala-cats-dev` | Advanced FP abstractions |
| ZIO effects, fibers, layers | `lang-scala-zio-dev` | Effect system patterns |
| Spark jobs, RDDs, DataFrames | `lang-scala-spark-dev` | Distributed computing |
| Play web apps, controllers, routes | `lang-scala-play-dev` | Web framework patterns |
| ScalaTest, ScalaCheck, mocking | `lang-scala-testing-dev` | Testing strategies |
| **Core language features** | **This skill** | Foundational patterns |

---

## Core Language Features

### Val vs Var - Immutability

**Prefer immutable `val` over mutable `var`:**

```scala
// Good - immutable
val name = "Alice"
val age = 30
val user = User(name, age)

// Avoid - mutable
var counter = 0
counter += 1  // Mutation creates complexity

// Better - functional update
val counter = 0
val newCounter = counter + 1
```

**When to use `var`:**

```scala
// Loop counters (prefer for-comprehensions)
var i = 0
while (i < 10) {
  println(i)
  i += 1
}

// Mutable accumulators (prefer foldLeft)
var sum = 0
list.foreach(x => sum += x)

// Better alternatives
(0 until 10).foreach(println)
val sum = list.foldLeft(0)(_ + _)
```

**Immutable collections:**

```scala
// Immutable by default
val list = List(1, 2, 3)
val newList = list :+ 4        // Creates new list
val map = Map("a" -> 1, "b" -> 2)
val newMap = map + ("c" -> 3)  // Creates new map

// Mutable collections (import required)
import scala.collection.mutable

val buffer = mutable.ListBuffer(1, 2, 3)
buffer += 4  // In-place mutation
val mutableMap = mutable.Map("a" -> 1)
mutableMap("b") = 2  // In-place mutation
```

---

### Case Classes and Pattern Matching

**Case classes** provide automatic implementations of `equals`, `hashCode`, `toString`, and `copy`:

```scala
// Case class definition
case class User(name: String, age: Int, email: String)

// Automatic features
val user = User("Alice", 30, "alice@example.com")
println(user)  // User(Alice,30,alice@example.com)

val updated = user.copy(age = 31)  // Immutable update

val User(name, age, email) = user  // Destructuring
```

**Pattern matching:**

```scala
// Match on case classes
def describe(user: User): String = user match {
  case User("Admin", _, _) => "Administrator"
  case User(name, age, _) if age < 18 => s"$name is a minor"
  case User(name, age, _) => s"$name is $age years old"
}

// Match on types
def process(value: Any): String = value match {
  case s: String => s.toUpperCase
  case i: Int => (i * 2).toString
  case d: Double => f"$d%.2f"
  case _ => "Unknown"
}

// Match on collections
def sumFirst(list: List[Int]): Int = list match {
  case Nil => 0
  case head :: Nil => head
  case head :: tail => head + sumFirst(tail)
}

// Guards and alternatives
def classify(n: Int): String = n match {
  case x if x < 0 => "negative"
  case 0 => "zero"
  case x if x % 2 == 0 => "even positive"
  case _ => "odd positive"
}
```

**Sealed traits for ADTs:**

```scala
sealed trait Result[+A]
case class Success[A](value: A) extends Result[A]
case class Failure(error: String) extends Result[Nothing]
case object Pending extends Result[Nothing]

def handle[A](result: Result[A]): String = result match {
  case Success(value) => s"Got: $value"
  case Failure(error) => s"Error: $error"
  case Pending => "Waiting..."
  // Compiler ensures exhaustiveness
}
```

---

### Traits and Mixins

**Traits as interfaces:**

```scala
trait Logging {
  def log(message: String): Unit
}

trait Auditing {
  def audit(event: String): Unit
}

class Service extends Logging with Auditing {
  def log(message: String): Unit = println(s"[LOG] $message")
  def audit(event: String): Unit = println(s"[AUDIT] $event")
}
```

**Traits with implementation:**

```scala
trait Logging {
  def log(message: String): Unit = {
    println(s"${java.time.Instant.now()}: $message")
  }
}

trait ErrorHandling {
  def handleError(error: Throwable): Unit = {
    System.err.println(s"Error: ${error.getMessage}")
  }
}

class Application extends Logging with ErrorHandling {
  def run(): Unit = {
    log("Application starting")
    try {
      // Application logic
    } catch {
      case e: Exception => handleError(e)
    }
  }
}
```

**Self-types for dependency declaration:**

```scala
trait DatabaseAccess {
  def query(sql: String): List[String]
}

trait UserService {
  self: DatabaseAccess =>  // Requires DatabaseAccess

  def getUsers(): List[String] = {
    query("SELECT * FROM users")  // Can use DatabaseAccess methods
  }
}

class Application extends UserService with DatabaseAccess {
  def query(sql: String): List[String] = {
    // Database implementation
    List("user1", "user2")
  }
}
```

**Linearization (method resolution order):**

```scala
trait A { def msg = "A" }
trait B extends A { override def msg = "B" + super.msg }
trait C extends A { override def msg = "C" + super.msg }

class D extends B with C  // Linearization: D -> C -> B -> A
val d = new D
println(d.msg)  // "CBA"
```

---

### For-Comprehensions

**Desugaring to map/flatMap/filter:**

```scala
// For-comprehension
val result = for {
  x <- Some(1)
  y <- Some(2)
  z <- Some(3)
} yield x + y + z

// Desugars to
val result = Some(1).flatMap { x =>
  Some(2).flatMap { y =>
    Some(3).map { z =>
      x + y + z
    }
  }
}
```

**With filters:**

```scala
val result = for {
  x <- List(1, 2, 3, 4, 5)
  if x % 2 == 0
  y <- List(10, 20)
} yield x * y

// Desugars to
val result = List(1, 2, 3, 4, 5)
  .filter(_ % 2 == 0)
  .flatMap(x => List(10, 20).map(y => x * y))
// Result: List(20, 40, 40, 80)
```

**With pattern matching:**

```scala
case class User(name: String, age: Int)

val users = List(User("Alice", 30), User("Bob", 25))

val names = for {
  User(name, age) <- users
  if age >= 30
} yield name.toUpperCase

// Result: List("ALICE")
```

**Combining different monadic types:**

```scala
def findUser(id: Int): Option[User] = ???
def getPermissions(user: User): List[String] = ???

val result = for {
  user <- findUser(123)
  permission <- getPermissions(user)
} yield s"${user.name} has $permission"
// Result type: Option[List[String]]
```

---

### Option, Either, Try

**Option - handling nullable values:**

```scala
// Creating Options
val some: Option[Int] = Some(42)
val none: Option[Int] = None

// From nullable
val maybeValue: Option[String] = Option(nullableString)

// Pattern matching
def describe(opt: Option[Int]): String = opt match {
  case Some(value) => s"Got $value"
  case None => "Nothing"
}

// Combinators
val doubled = some.map(_ * 2)           // Some(84)
val filtered = some.filter(_ > 50)      // None
val orElse = none.orElse(Some(0))       // Some(0)
val getOrElse = none.getOrElse(0)       // 0

// For-comprehensions
val result = for {
  x <- Some(1)
  y <- Some(2)
} yield x + y  // Some(3)
```

**Either - error handling with context:**

```scala
// Right for success, Left for failure
type Result[A] = Either[String, A]

def divide(a: Int, b: Int): Result[Int] = {
  if (b == 0) Left("Division by zero")
  else Right(a / b)
}

// Pattern matching
divide(10, 2) match {
  case Right(value) => println(s"Result: $value")
  case Left(error) => println(s"Error: $error")
}

// Combinators (right-biased)
val result = divide(10, 2)
  .map(_ * 2)                    // Right(10)
  .flatMap(x => divide(x, 5))    // Right(2)

// For-comprehensions
val calculation = for {
  a <- divide(10, 2)
  b <- divide(a, 5)
  c <- divide(b, 1)
} yield c  // Right(1)
```

**Try - exception handling:**

```scala
import scala.util.{Try, Success, Failure}

// Creating Try
val attempt = Try {
  "123".toInt  // Might throw NumberFormatException
}

// Pattern matching
attempt match {
  case Success(value) => println(s"Parsed: $value")
  case Failure(exception) => println(s"Error: ${exception.getMessage}")
}

// Combinators
val result = Try("123".toInt)
  .map(_ * 2)
  .recover { case _: NumberFormatException => 0 }
  .getOrElse(-1)

// Converting to Option or Either
val opt: Option[Int] = attempt.toOption
val either: Either[Throwable, Int] = attempt.toEither
```

**Choosing between Option, Either, Try:**

| Type | Use When | Error Info |
|------|----------|------------|
| `Option[A]` | Value may be absent | No error context |
| `Either[E, A]` | Need error details | Custom error type `E` |
| `Try[A]` | Catching exceptions | `Throwable` exception |

---

### Collections

**Immutable collections (default):**

```scala
// List - linked list
val list = List(1, 2, 3)
val prepended = 0 :: list        // O(1) prepend
val appended = list :+ 4         // O(n) append
val concatenated = list ++ List(4, 5)

// Vector - indexed sequence
val vector = Vector(1, 2, 3)
val updated = vector.updated(1, 42)  // O(log n) update
val accessed = vector(1)             // O(log n) access

// Set - unique elements
val set = Set(1, 2, 3, 2)  // Set(1, 2, 3)
val added = set + 4
val removed = set - 2

// Map - key-value pairs
val map = Map("a" -> 1, "b" -> 2)
val updated = map + ("c" -> 3)
val removed = map - "a"
val value = map.get("a")  // Option[Int]
val valueOrDefault = map.getOrElse("z", 0)
```

**Common operations:**

```scala
val list = List(1, 2, 3, 4, 5)

// Transformations
list.map(_ * 2)                    // List(2, 4, 6, 8, 10)
list.filter(_ % 2 == 0)            // List(2, 4)
list.flatMap(x => List(x, x * 10)) // List(1, 10, 2, 20, ...)

// Reductions
list.foldLeft(0)(_ + _)            // 15
list.foldRight(0)(_ + _)           // 15
list.reduce(_ + _)                 // 15
list.scan(0)(_ + _)                // List(0, 1, 3, 6, 10, 15)

// Grouping
list.groupBy(_ % 2)                // Map(0 -> List(2,4), 1 -> List(1,3,5))
list.partition(_ % 2 == 0)         // (List(2, 4), List(1, 3, 5))

// Searching
list.find(_ > 3)                   // Some(4)
list.exists(_ > 3)                 // true
list.forall(_ > 0)                 // true

// Sorting
list.sorted                        // List(1, 2, 3, 4, 5)
list.sortBy(-_)                    // List(5, 4, 3, 2, 1)
list.sortWith(_ > _)               // List(5, 4, 3, 2, 1)

// Zipping
list.zip(List("a", "b", "c"))      // List((1,a), (2,b), (3,c))
list.zipWithIndex                  // List((1,0), (2,1), (3,2), ...)
```

**Performance characteristics:**

| Collection | Access | Prepend | Append | Update |
|------------|--------|---------|--------|--------|
| List | O(n) | O(1) | O(n) | O(n) |
| Vector | O(log n) | O(log n) | O(log n) | O(log n) |
| Array | O(1) | O(n) | O(n) | O(1) |
| Set | O(log n) | O(log n) | O(log n) | - |
| Map | O(log n) | O(log n) | O(log n) | O(log n) |

---

### Higher-Order Functions

**Functions as values:**

```scala
// Function literals
val add: (Int, Int) => Int = (a, b) => a + b
val square: Int => Int = x => x * x
val greet: String => Unit = name => println(s"Hello, $name")

// Method to function
def multiply(a: Int, b: Int): Int = a * b
val multiplyFn = multiply _  // Eta expansion

// Placeholder syntax
val add1 = (_: Int) + 1
val sum = (_: Int) + (_: Int)
```

**Higher-order functions:**

```scala
// Taking functions as parameters
def applyTwice(f: Int => Int, x: Int): Int = f(f(x))
applyTwice(_ * 2, 3)  // 12

def repeat(n: Int)(action: => Unit): Unit = {
  (1 to n).foreach(_ => action)
}
repeat(3) { println("Hello") }

// Returning functions
def multiplier(factor: Int): Int => Int = {
  x => x * factor
}
val double = multiplier(2)
double(5)  // 10

// Currying
def add(a: Int)(b: Int): Int = a + b
val add5 = add(5) _
add5(3)  // 8

// Partial application
def sum3(a: Int, b: Int, c: Int): Int = a + b + c
val sumWith10 = sum3(10, _: Int, _: Int)
sumWith10(20, 30)  // 60
```

**Common higher-order patterns:**

```scala
// Map, filter, fold
List(1, 2, 3)
  .map(_ * 2)
  .filter(_ > 3)
  .foldLeft(0)(_ + _)

// Composition
val f: Int => Int = _ * 2
val g: Int => Int = _ + 1
val composed = f compose g  // f(g(x))
val andThen = f andThen g   // g(f(x))

composed(5)  // 12 = (5 + 1) * 2
andThen(5)   // 11 = (5 * 2) + 1
```

---

### Implicits and Given/Using

**Scala 2 implicits:**

```scala
// Implicit parameters
def greet(name: String)(implicit greeting: String): String = {
  s"$greeting, $name"
}

implicit val defaultGreeting: String = "Hello"
greet("Alice")  // "Hello, Alice"

// Implicit conversions (use sparingly)
implicit def intToString(x: Int): String = x.toString
val s: String = 42  // Implicit conversion

// Implicit classes (extension methods)
implicit class RichInt(x: Int) {
  def squared: Int = x * x
}
42.squared  // 1764

// Type classes
trait Show[A] {
  def show(a: A): String
}

object Show {
  implicit val intShow: Show[Int] = (a: Int) => a.toString
  implicit val stringShow: Show[String] = (a: String) => s"'$a'"
}

def print[A](a: A)(implicit s: Show[A]): Unit = {
  println(s.show(a))
}

print(42)      // "42"
print("hello") // "'hello'"
```

**Scala 3 given/using:**

```scala
// Given instances
trait Show[A] {
  def show(a: A): String
}

given Show[Int] with {
  def show(a: Int): String = a.toString
}

given Show[String] with {
  def show(a: String): String = s"'$a'"
}

// Using clauses
def print[A](a: A)(using s: Show[A]): Unit = {
  println(s.show(a))
}

print(42)      // "42"
print("hello") // "'hello'"

// Extension methods (Scala 3)
extension (x: Int) {
  def squared: Int = x * x
  def cubed: Int = x * x * x
}

42.squared  // 1764
```

**Implicit resolution rules:**

1. **Local scope** - implicits defined in current scope
2. **Imported scope** - explicitly imported implicits
3. **Companion objects** - companion of type or type class
4. **Implicit scope** - package objects, parent types

```scala
// Resolution example
trait Ordering[A]

object Ordering {
  // Companion object - implicit scope
  implicit val intOrdering: Ordering[Int] = ???
}

class MyClass {
  // Local scope takes precedence
  implicit val localOrdering: Ordering[Int] = ???

  def sort[A](list: List[A])(implicit ord: Ordering[A]): List[A] = ???

  sort(List(3, 1, 2))  // Uses localOrdering
}
```

---

### Type System

**Type variance:**

```scala
// Covariance (+A) - subtyping preserved
trait Producer[+A] {
  def produce(): A
}

class Animal
class Dog extends Animal

val dogProducer: Producer[Dog] = ???
val animalProducer: Producer[Animal] = dogProducer  // OK

// Contravariance (-A) - subtyping reversed
trait Consumer[-A] {
  def consume(a: A): Unit
}

val animalConsumer: Consumer[Animal] = ???
val dogConsumer: Consumer[Dog] = animalConsumer  // OK

// Invariance (A) - no subtyping
trait Box[A] {
  def get: A
  def set(a: A): Unit
}

// List is covariant, Array is invariant
val dogs: List[Dog] = List()
val animals: List[Animal] = dogs  // OK

val dogArray: Array[Dog] = Array()
// val animalArray: Array[Animal] = dogArray  // Compile error
```

**Type bounds:**

```scala
// Upper bound (A <: B) - A must be subtype of B
def findMax[A <: Comparable[A]](list: List[A]): A = {
  list.reduce((a, b) => if (a.compareTo(b) > 0) a else b)
}

// Lower bound (A >: B) - A must be supertype of B
sealed trait Animal
case class Dog(name: String) extends Animal
case class Cat(name: String) extends Animal

def prepend[A, B >: A](elem: B, list: List[A]): List[B] = {
  elem :: list
}

val dogs: List[Dog] = List(Dog("Fido"))
val animals: List[Animal] = prepend(Cat("Whiskers"), dogs)

// Context bounds (requires implicit)
def sort[A: Ordering](list: List[A]): List[A] = {
  list.sorted  // Uses implicit Ordering[A]
}

// Multiple bounds
def process[A <: Animal with Comparable[A]: Show](a: A): String = ???
```

**Type aliases and abstract types:**

```scala
// Type alias
type UserId = Int
type Result[A] = Either[String, A]

val id: UserId = 123
val result: Result[Int] = Right(42)

// Abstract types
trait Container {
  type Element
  def add(e: Element): Unit
  def get(): Element
}

class IntContainer extends Container {
  type Element = Int
  private var value: Int = 0
  def add(e: Int): Unit = value = e
  def get(): Int = value
}

// Path-dependent types
class Outer {
  class Inner
  def process(inner: Inner): Unit = ???
}

val outer1 = new Outer
val outer2 = new Outer

val inner1 = new outer1.Inner
// outer2.process(inner1)  // Compile error - type mismatch
```

---

## Common Patterns

### Builder Pattern

**Using copy method (case classes):**

```scala
case class User(
  name: String,
  age: Int,
  email: String,
  phone: Option[String] = None,
  address: Option[String] = None
)

// Building with copy
val user = User("Alice", 30, "alice@example.com")
  .copy(phone = Some("555-1234"))
  .copy(address = Some("123 Main St"))
```

**Explicit builder:**

```scala
class UserBuilder private (
  private var name: String = "",
  private var age: Int = 0,
  private var email: String = "",
  private var phone: Option[String] = None
) {
  def withName(name: String): UserBuilder = {
    this.name = name
    this
  }

  def withAge(age: Int): UserBuilder = {
    this.age = age
    this
  }

  def withEmail(email: String): UserBuilder = {
    this.email = email
    this
  }

  def withPhone(phone: String): UserBuilder = {
    this.phone = Some(phone)
    this
  }

  def build(): User = {
    require(name.nonEmpty, "Name is required")
    require(email.nonEmpty, "Email is required")
    User(name, age, email, phone, None)
  }
}

object UserBuilder {
  def apply(): UserBuilder = new UserBuilder()
}

// Usage
val user = UserBuilder()
  .withName("Alice")
  .withAge(30)
  .withEmail("alice@example.com")
  .withPhone("555-1234")
  .build()
```

---

### Type Classes

**Definition and implementation:**

```scala
// Type class definition
trait Show[A] {
  def show(a: A): String
}

// Type class instances
object Show {
  // Summoner method
  def apply[A](implicit instance: Show[A]): Show[A] = instance

  // Constructor method
  def instance[A](f: A => String): Show[A] = new Show[A] {
    def show(a: A): String = f(a)
  }

  // Instances
  implicit val intShow: Show[Int] = instance(_.toString)
  implicit val stringShow: Show[String] = instance(s => s"'$s'")
  implicit val boolShow: Show[Boolean] = instance(_.toString)

  // Derived instance
  implicit def listShow[A](implicit sa: Show[A]): Show[List[A]] = {
    instance(list => list.map(sa.show).mkString("[", ", ", "]"))
  }
}

// Extension methods (Scala 2)
implicit class ShowOps[A](val a: A) extends AnyVal {
  def show(implicit s: Show[A]): String = s.show(a)
}

// Usage
42.show                    // "42"
"hello".show               // "'hello'"
List(1, 2, 3).show         // "[1, 2, 3]"
```

**Type class with operations:**

```scala
trait Monoid[A] {
  def empty: A
  def combine(x: A, y: A): A
}

object Monoid {
  def apply[A](implicit instance: Monoid[A]): Monoid[A] = instance

  implicit val intAddMonoid: Monoid[Int] = new Monoid[Int] {
    def empty: Int = 0
    def combine(x: Int, y: Int): Int = x + y
  }

  implicit val stringMonoid: Monoid[String] = new Monoid[String] {
    def empty: String = ""
    def combine(x: String, y: String): String = x + y
  }

  implicit def listMonoid[A]: Monoid[List[A]] = new Monoid[List[A]] {
    def empty: List[A] = Nil
    def combine(x: List[A], y: List[A]): List[A] = x ++ y
  }
}

def combineAll[A](list: List[A])(implicit m: Monoid[A]): A = {
  list.foldLeft(m.empty)(m.combine)
}

combineAll(List(1, 2, 3, 4))           // 10
combineAll(List("a", "b", "c"))        // "abc"
combineAll(List(List(1), List(2, 3))) // List(1, 2, 3)
```

---

### Cake Pattern

**Dependency injection using self-types:**

```scala
// Component definitions
trait UserRepositoryComponent {
  def userRepository: UserRepository

  trait UserRepository {
    def findById(id: Int): Option[User]
    def save(user: User): Unit
  }
}

trait EmailServiceComponent {
  def emailService: EmailService

  trait EmailService {
    def sendEmail(to: String, subject: String, body: String): Unit
  }
}

// Implementations
trait UserRepositoryComponentImpl extends UserRepositoryComponent {
  def userRepository: UserRepository = new UserRepositoryImpl

  class UserRepositoryImpl extends UserRepository {
    def findById(id: Int): Option[User] = {
      // Database access
      Some(User("Alice", 30, "alice@example.com"))
    }

    def save(user: User): Unit = {
      // Database access
      println(s"Saving user: $user")
    }
  }
}

trait EmailServiceComponentImpl extends EmailServiceComponent {
  def emailService: EmailService = new EmailServiceImpl

  class EmailServiceImpl extends EmailService {
    def sendEmail(to: String, subject: String, body: String): Unit = {
      println(s"Sending email to $to: $subject")
    }
  }
}

// Application component with dependencies
trait UserServiceComponent {
  self: UserRepositoryComponent with EmailServiceComponent =>

  def userService: UserService = new UserServiceImpl

  class UserServiceImpl extends UserService {
    def registerUser(user: User): Unit = {
      userRepository.save(user)
      emailService.sendEmail(user.email, "Welcome", "Thanks for registering!")
    }
  }

  trait UserService {
    def registerUser(user: User): Unit
  }
}

// Wiring
object Application extends UserServiceComponent
  with UserRepositoryComponentImpl
  with EmailServiceComponentImpl {

  def main(args: Array[String]): Unit = {
    val user = User("Bob", 25, "bob@example.com")
    userService.registerUser(user)
  }
}
```

---

### Algebraic Data Types (ADTs)

**Sum types (sealed traits):**

```scala
// Enumeration-like ADT
sealed trait Color
case object Red extends Color
case object Green extends Color
case object Blue extends Color

// Pattern matching is exhaustive
def describe(color: Color): String = color match {
  case Red => "red"
  case Green => "green"
  case Blue => "blue"
  // Compiler ensures all cases covered
}

// ADT with data
sealed trait Shape
case class Circle(radius: Double) extends Shape
case class Rectangle(width: Double, height: Double) extends Shape
case class Triangle(base: Double, height: Double) extends Shape

def area(shape: Shape): Double = shape match {
  case Circle(r) => math.Pi * r * r
  case Rectangle(w, h) => w * h
  case Triangle(b, h) => 0.5 * b * h
}
```

**Product types (case classes):**

```scala
// Simple product type
case class Point(x: Double, y: Double)

// Nested product types
case class Address(street: String, city: String, zip: String)
case class Person(name: String, age: Int, address: Address)

// Generic product type
case class Pair[A, B](first: A, second: B)
```

**Combining sum and product types:**

```scala
sealed trait Expression
case class Number(value: Int) extends Expression
case class Add(left: Expression, right: Expression) extends Expression
case class Multiply(left: Expression, right: Expression) extends Expression
case class Divide(left: Expression, right: Expression) extends Expression

def evaluate(expr: Expression): Either[String, Int] = expr match {
  case Number(value) => Right(value)
  case Add(left, right) =>
    for {
      l <- evaluate(left)
      r <- evaluate(right)
    } yield l + r
  case Multiply(left, right) =>
    for {
      l <- evaluate(left)
      r <- evaluate(right)
    } yield l * r
  case Divide(left, right) =>
    for {
      l <- evaluate(left)
      r <- evaluate(right)
      result <- if (r != 0) Right(l / r) else Left("Division by zero")
    } yield result
}

// Usage
val expr = Divide(Add(Number(10), Number(5)), Number(3))
evaluate(expr)  // Right(5)
```

**Recursive ADTs:**

```scala
sealed trait List[+A]
case object Nil extends List[Nothing]
case class Cons[A](head: A, tail: List[A]) extends List[A]

def sum(list: List[Int]): Int = list match {
  case Nil => 0
  case Cons(head, tail) => head + sum(tail)
}

// Binary tree
sealed trait Tree[+A]
case object Empty extends Tree[Nothing]
case class Node[A](value: A, left: Tree[A], right: Tree[A]) extends Tree[A]

def size[A](tree: Tree[A]): Int = tree match {
  case Empty => 0
  case Node(_, left, right) => 1 + size(left) + size(right)
}
```

---

## Troubleshooting

### Common Compilation Errors

**Type mismatch:**

```scala
// Error: type mismatch
val x: String = 42

// Fix: convert types
val x: String = 42.toString

// Error: cannot prove that A =:= B
def process[A](a: A): String = a.toString  // Fine
def process[A](a: A): A = "string"         // Error

// Fix: specify correct return type
def process[A](a: A): String = "string"
```

**Missing implicit parameter:**

```scala
// Error: could not find implicit value
def sort[A](list: List[A])(implicit ord: Ordering[A]): List[A] = {
  list.sorted
}

sort(List(1, 2, 3))  // OK - Ordering[Int] exists
// sort(List(Person("Alice", 30)))  // Error - no Ordering[Person]

// Fix: provide implicit
implicit val personOrdering: Ordering[Person] = Ordering.by(_.name)
sort(List(Person("Alice", 30)))  // OK now
```

**Pattern match not exhaustive:**

```scala
sealed trait Result
case class Success(value: Int) extends Result
case class Failure(error: String) extends Result

// Warning: match may not be exhaustive
def handle(result: Result): String = result match {
  case Success(value) => s"Got $value"
  // Missing Failure case
}

// Fix: add all cases
def handle(result: Result): String = result match {
  case Success(value) => s"Got $value"
  case Failure(error) => s"Error: $error"
}
```

**Recursive value needs type:**

```scala
// Error: recursive value x needs type
val x = x + 1

// Fix: specify type
val x: Int = {
  def helper: Int = helper + 1
  helper
}

// Or avoid recursion
val x = 1
```

**Variance errors:**

```scala
// Error: covariant type A occurs in contravariant position
trait Producer[+A] {
  def produce(): A           // OK - covariant position
  // def consume(a: A): Unit // Error - contravariant position
}

// Fix: use lower bound
trait Producer[+A] {
  def produce(): A
  def consume[B >: A](b: B): Unit  // OK
}
```

### Runtime Issues

**NullPointerException:**

```scala
// Dangerous - nullable
val name: String = null
// name.toUpperCase  // NullPointerException

// Better - use Option
val name: Option[String] = None
name.map(_.toUpperCase)  // Safe
```

**StackOverflowError in recursion:**

```scala
// Not tail recursive
def factorial(n: Int): Int = {
  if (n <= 1) 1
  else n * factorial(n - 1)  // Not in tail position
}

// factorial(10000)  // StackOverflowError

// Fix: use tail recursion
@scala.annotation.tailrec
def factorial(n: Int, acc: Int = 1): Int = {
  if (n <= 1) acc
  else factorial(n - 1, n * acc)  // Tail call
}

factorial(10000)  // OK
```

**ClassCastException:**

```scala
// Dangerous - type erasure
def castList(list: Any): List[Int] = list.asInstanceOf[List[Int]]

val stringList = List("a", "b", "c")
val intList = castList(stringList)  // No error yet
// intList.head + 1  // ClassCastException at runtime

// Better - use pattern matching
def safeToIntList(value: Any): Option[List[Int]] = value match {
  case list: List[_] if list.forall(_.isInstanceOf[Int]) =>
    Some(list.asInstanceOf[List[Int]])
  case _ => None
}
```

---

## Performance Tips

**Prefer immutable collections:**

```scala
// Immutable operations create new instances
val list = List(1, 2, 3)
val newList = list :+ 4  // Structural sharing, efficient

// For building, use builders
val builder = List.newBuilder[Int]
(1 to 1000).foreach(builder += _)
val result = builder.result()
```

**Use tail recursion:**

```scala
// Stack-safe tail recursion
@scala.annotation.tailrec
def sum(list: List[Int], acc: Int = 0): Int = list match {
  case Nil => acc
  case head :: tail => sum(tail, acc + head)
}
```

**Avoid unnecessary Option wrapping:**

```scala
// Inefficient
val result = Some(value).map(transform).getOrElse(default)

// Better
val result = if (condition) transform(value) else default
```

**Use views for large collections:**

```scala
// Eager evaluation - multiple passes
val result = list.map(_ * 2).filter(_ > 10).take(5)

// Lazy evaluation - single pass
val result = list.view.map(_ * 2).filter(_ > 10).take(5).toList
```

---

## Best Practices

### Code Organization

1. **Use package objects for package-level definitions:**

```scala
package com.example

package object utils {
  type UserId = Int
  type Result[A] = Either[String, A]

  implicit class StringOps(s: String) {
    def toUserId: UserId = s.toInt
  }
}
```

2. **Companion objects for factory methods:**

```scala
case class User private (name: String, age: Int)

object User {
  def create(name: String, age: Int): Either[String, User] = {
    if (age < 0) Left("Age must be positive")
    else if (name.isEmpty) Left("Name cannot be empty")
    else Right(new User(name, age))
  }
}
```

3. **Sealed traits in same file:**

```scala
// All implementations must be in this file
sealed trait Result[+A]
case class Success[A](value: A) extends Result[A]
case class Failure(error: String) extends Result[Nothing]
case object Pending extends Result[Nothing]
```

### Naming Conventions

- **Classes/Traits:** PascalCase (`UserService`, `HttpClient`)
- **Objects:** PascalCase (`DatabaseConfig`)
- **Methods/Values:** camelCase (`findUser`, `maxRetries`)
- **Type parameters:** Single uppercase letter (`A`, `B`, `T`)
- **Implicits:** Descriptive names (`userOrdering`, `jsonEncoder`)

### Error Handling

**Prefer typed errors over exceptions:**

```scala
// Good
sealed trait UserError
case object UserNotFound extends UserError
case object InvalidEmail extends UserError

def findUser(id: Int): Either[UserError, User] = ???

// Avoid
def findUser(id: Int): User = {
  throw new UserNotFoundException(s"User $id not found")
}
```

---

## Concurrency

Scala provides multiple concurrency models: Futures for simple async operations, Akka actors for complex concurrent systems, and modern effect systems like Cats Effect and ZIO.

### Futures - Basic Async

**Creating and using Futures:**

```scala
import scala.concurrent.{Future, Await}
import scala.concurrent.duration._
import scala.concurrent.ExecutionContext.Implicits.global

// Create Future
val future = Future {
  Thread.sleep(1000)
  42
}

// Transform with map
val doubled = future.map(_ * 2)

// Chain with flatMap
val chained = future.flatMap { value =>
  Future(value + 10)
}

// For-comprehension
val result = for {
  a <- Future(10)
  b <- Future(20)
  c <- Future(30)
} yield a + b + c

// Blocking (avoid in production)
val value = Await.result(future, 5.seconds)
```

**Combining Futures:**

```scala
// Sequence - converts List[Future[A]] to Future[List[A]]
val futures = List(Future(1), Future(2), Future(3))
val combined: Future[List[Int]] = Future.sequence(futures)

// Traverse - map then sequence
val ids = List(1, 2, 3)
val users: Future[List[User]] = Future.traverse(ids)(id => fetchUser(id))

// First completed
val fastest = Future.firstCompletedOf(List(
  fetchFromPrimary(),
  fetchFromBackup()
))

// Recover from failures
val safe = future.recover {
  case _: TimeoutException => 0
  case _: Exception => -1
}

val safeWith = future.recoverWith {
  case _: Exception => fetchFromCache()
}
```

**Promise - explicit completion:**

```scala
import scala.concurrent.Promise

val promise = Promise[Int]()
val future = promise.future

// Complete in another thread
Future {
  Thread.sleep(1000)
  promise.success(42)
}

// Or fail
promise.failure(new Exception("Failed"))

// Try complete (doesn't throw if already completed)
promise.trySuccess(100)
```

### Akka Actors - Message Passing

**Typed actors (Akka Typed):**

```scala
import akka.actor.typed._
import akka.actor.typed.scaladsl.Behaviors

// Define protocol
sealed trait CounterMessage
case object Increment extends CounterMessage
case object Decrement extends CounterMessage
case class GetCount(replyTo: ActorRef[Int]) extends CounterMessage

// Define behavior
def counter(count: Int): Behavior[CounterMessage] = Behaviors.receive { (context, message) =>
  message match {
    case Increment =>
      counter(count + 1)
    case Decrement =>
      counter(count - 1)
    case GetCount(replyTo) =>
      replyTo ! count
      Behaviors.same
  }
}

// Create actor system
val system = ActorSystem(counter(0), "counter-system")

// Send messages
system ! Increment
system ! Increment
```

**Actor patterns:**

```scala
// Ask pattern (request-response)
import akka.actor.typed.scaladsl.AskPattern._
import akka.util.Timeout
import scala.concurrent.duration._

implicit val timeout: Timeout = 3.seconds

val futureCount: Future[Int] = system.ask(ref => GetCount(ref))

// Supervision
def supervisedBehavior(): Behavior[String] = {
  Behaviors.supervise {
    Behaviors.receive[String] { (context, message) =>
      if (message == "fail") throw new Exception("Failed!")
      else Behaviors.same
    }
  }.onFailure[Exception](SupervisorStrategy.restart)
}
```

### Cats Effect - Functional Effects

**IO monad for side effects:**

```scala
import cats.effect._

// Create IO
val printHello: IO[Unit] = IO.println("Hello")
val readLine: IO[String] = IO.readLine

// Compose with for-comprehension
val program = for {
  _ <- IO.println("What's your name?")
  name <- IO.readLine
  _ <- IO.println(s"Hello, $name!")
} yield ()

// Parallel execution
import cats.effect.syntax.parallel._
import cats.syntax.apply._

val parallel = (
  fetchUser(1),
  fetchUser(2),
  fetchUser(3)
).parMapN((u1, u2, u3) => List(u1, u2, u3))

// Resource management
def useFile(path: String): IO[String] = {
  Resource.make(
    IO(scala.io.Source.fromFile(path))  // Acquire
  )(source => IO(source.close()))        // Release
    .use(source => IO(source.mkString))  // Use
}

// Error handling
val safeIO = IO.raiseError(new Exception("Error"))
  .handleErrorWith(_ => IO.pure(0))
  .attempt  // Returns IO[Either[Throwable, Int]]
```

**Fibers - lightweight threads:**

```scala
import cats.effect.IO

def task(n: Int): IO[Unit] = IO.sleep(1.second) >> IO.println(s"Task $n")

val program = for {
  fiber1 <- task(1).start  // Start fiber
  fiber2 <- task(2).start
  _ <- fiber1.join         // Wait for completion
  _ <- fiber2.join
} yield ()

// Cancellation
val cancelable = for {
  fiber <- IO.sleep(10.seconds).start
  _ <- IO.sleep(1.second)
  _ <- fiber.cancel  // Cancel after 1 second
} yield ()
```

### ZIO - Effect System

**ZIO basics:**

```scala
import zio._

// Create ZIO
val hello: ZIO[Any, Nothing, Unit] = ZIO.succeed(println("Hello"))
val readLine: ZIO[Any, IOException, String] = ZIO.attempt(scala.io.StdIn.readLine())

// Composition
val program = for {
  _ <- Console.printLine("What's your name?")
  name <- Console.readLine
  _ <- Console.printLine(s"Hello, $name!")
} yield ()

// Parallel execution
val parallel = ZIO.collectAllPar(List(
  fetchUser(1),
  fetchUser(2),
  fetchUser(3)
))

// Racing
val raced = fetchFromPrimary() race fetchFromBackup()

// Timeout
val withTimeout = fetchData().timeout(5.seconds)
```

**ZIO Layers - dependency injection:**

```scala
trait UserService {
  def getUser(id: Int): ZIO[Any, Throwable, User]
}

case class UserServiceLive(database: Database) extends UserService {
  def getUser(id: Int): ZIO[Any, Throwable, User] =
    ZIO.attempt(database.query(s"SELECT * FROM users WHERE id = $id"))
}

object UserServiceLive {
  val layer: ZLayer[Database, Nothing, UserService] =
    ZLayer.fromFunction(UserServiceLive.apply _)
}

// Use the service
val program = for {
  user <- ZIO.serviceWithZIO[UserService](_.getUser(123))
  _ <- Console.printLine(s"User: $user")
} yield ()

// Provide dependencies
program.provide(UserServiceLive.layer, DatabaseLive.layer)
```

**See also:** `patterns-concurrency-dev` for cross-language concurrency comparison

---

## Build and Dependencies

Scala uses sbt (Simple Build Tool) as the primary build tool, with Mill as a modern alternative. Dependencies are published to Maven Central and Sonatype.

### sbt - Simple Build Tool

**build.sbt basics:**

```scala
// Project metadata
name := "my-project"
version := "0.1.0"
scalaVersion := "3.3.1"

// Organization (for publishing)
organization := "com.example"

// Dependencies
libraryDependencies ++= Seq(
  "org.typelevel" %% "cats-core" % "2.10.0",
  "org.typelevel" %% "cats-effect" % "3.5.2",
  "com.lihaoyi" %% "upickle" % "3.1.3",

  // Test dependencies
  "org.scalatest" %% "scalatest" % "3.2.17" % Test,
  "org.scalatestplus" %% "mockito-4-11" % "3.2.17.0" % Test
)

// Compiler options (Scala 3)
scalacOptions ++= Seq(
  "-deprecation",
  "-feature",
  "-unchecked",
  "-Xfatal-warnings"
)

// Resolvers (if needed)
resolvers += "Sonatype OSS Snapshots" at "https://oss.sonatype.org/content/repositories/snapshots"
```

**Dependency syntax:**

```scala
// %% - Scala version appended automatically
"org.typelevel" %% "cats-core" % "2.10.0"
// Resolves to: org.typelevel:cats-core_3:2.10.0

// % - Exact artifact name (Java libraries)
"com.google.guava" % "guava" % "32.1.3-jre"

// Cross-version dependencies
"org.scala-lang" % "scala-reflect" % scalaVersion.value

// Test scope
"org.scalatest" %% "scalatest" % "3.2.17" % Test

// Provided scope (available at compile, not packaged)
"javax.servlet" % "javax.servlet-api" % "4.0.1" % Provided
```

**Multi-module projects:**

```scala
// build.sbt root project
lazy val root = (project in file("."))
  .aggregate(core, api, client)
  .settings(
    name := "my-project"
  )

lazy val core = (project in file("core"))
  .settings(
    name := "my-project-core",
    libraryDependencies ++= coreDeps
  )

lazy val api = (project in file("api"))
  .dependsOn(core)
  .settings(
    name := "my-project-api",
    libraryDependencies ++= apiDeps
  )

lazy val client = (project in file("client"))
  .dependsOn(core)
  .settings(
    name := "my-project-client"
  )
```

**Common sbt tasks:**

```bash
# Compile
sbt compile

# Run application
sbt run

# Run tests
sbt test

# Interactive mode
sbt
> compile
> test
> ~test  # Watch mode - rerun on file change

# Package JAR
sbt package

# Create fat JAR (with dependencies)
sbt assembly  # Requires sbt-assembly plugin

# Show dependency tree
sbt dependencyTree

# Update dependencies
sbt update

# Clean build
sbt clean

# Publish to local Ivy repository
sbt publishLocal

# Publish to Maven Central
sbt publishSigned
```

**project/plugins.sbt - sbt plugins:**

```scala
// Assembly - fat JAR
addSbtPlugin("com.eed3si9n" % "sbt-assembly" % "2.1.5")

// Coverage
addSbtPlugin("org.scoverage" % "sbt-scoverage" % "2.0.9")

// Publishing
addSbtPlugin("com.github.sbt" % "sbt-pgp" % "2.2.1")
addSbtPlugin("org.xerial.sbt" % "sbt-sonatype" % "3.9.21")

// Formatting
addSbtPlugin("org.scalameta" % "sbt-scalafmt" % "2.5.2")

// Native compilation
addSbtPlugin("org.scala-native" % "sbt-scala-native" % "0.4.16")
```

### Mill - Modern Build Tool

**build.sc (Mill build file):**

```scala
import mill._
import mill.scalalib._

object core extends ScalaModule {
  def scalaVersion = "3.3.1"

  def ivyDeps = Agg(
    ivy"org.typelevel::cats-core:2.10.0",
    ivy"org.typelevel::cats-effect:3.5.2"
  )

  object test extends Tests with TestModule.ScalaTest {
    def ivyDeps = Agg(
      ivy"org.scalatest::scalatest:3.2.17"
    )
  }
}

object api extends ScalaModule {
  def scalaVersion = "3.3.1"
  def moduleDeps = Seq(core)
}
```

**Mill commands:**

```bash
# Compile
mill core.compile

# Run tests
mill core.test

# Run application
mill core.run

# Assembly (fat JAR)
mill core.assembly

# Watch mode
mill -w core.test
```

### Cross-Compilation

**Building for multiple Scala versions:**

```scala
// build.sbt
lazy val core = (project in file("core"))
  .settings(
    name := "my-library",
    crossScalaVersions := Seq("2.12.18", "2.13.12", "3.3.1"),
    scalaVersion := "3.3.1"  // Default
  )
```

```bash
# Compile for all versions
sbt +compile

# Test all versions
sbt +test

# Publish all versions
sbt +publish
```

**Version-specific code:**

```scala
// src/main/scala-2.13/compat.scala
object Compat {
  def collect[A](list: List[Option[A]]): List[A] = list.flatten
}

// src/main/scala-3/compat.scala
object Compat {
  def collect[A](list: List[Option[A]]): List[A] = list.flatten
}
```

### Publishing to Maven Central

**build.sbt publishing configuration:**

```scala
// Metadata
organization := "io.github.username"
homepage := Some(url("https://github.com/username/project"))
scmInfo := Some(
  ScmInfo(
    url("https://github.com/username/project"),
    "scm:git@github.com:username/project.git"
  )
)
developers := List(
  Developer(
    id = "username",
    name = "Your Name",
    email = "you@example.com",
    url = url("https://github.com/username")
  )
)
licenses := Seq("Apache-2.0" -> url("http://www.apache.org/licenses/LICENSE-2.0"))

// Publishing
publishMavenStyle := true
publishTo := {
  val nexus = "https://oss.sonatype.org/"
  if (isSnapshot.value)
    Some("snapshots" at nexus + "content/repositories/snapshots")
  else
    Some("releases" at nexus + "service/local/staging/deploy/maven2")
}

// PGP signing
usePgpKeyHex("YOUR_KEY_ID")
```

---

## Testing

Scala has multiple testing frameworks: ScalaTest (most popular), MUnit (lightweight), specs2 (BDD-style), and ScalaCheck for property-based testing.

### ScalaTest - Comprehensive Testing

**Basic test suites:**

```scala
import org.scalatest.flatspec.AnyFlatSpec
import org.scalatest.matchers.should.Matchers

class CalculatorSpec extends AnyFlatSpec with Matchers {

  "A Calculator" should "add two numbers" in {
    val calc = new Calculator
    calc.add(2, 3) shouldBe 5
  }

  it should "subtract two numbers" in {
    val calc = new Calculator
    calc.subtract(5, 3) shouldBe 2
  }

  it should "throw on division by zero" in {
    val calc = new Calculator
    assertThrows[ArithmeticException] {
      calc.divide(10, 0)
    }
  }
}
```

**Test styles:**

```scala
// FlatSpec - flat, BDD-style
class UserServiceFlatSpec extends AnyFlatSpec with Matchers {
  "UserService" should "find user by id" in {
    // test
  }
}

// FunSpec - nested describe/it
class UserServiceFunSpec extends AnyFunSpec with Matchers {
  describe("UserService") {
    describe("findById") {
      it("should return user when found") {
        // test
      }
      it("should return None when not found") {
        // test
      }
    }
  }
}

// WordSpec - BDD "should" style
class UserServiceWordSpec extends AnyWordSpec with Matchers {
  "UserService" should {
    "find user by id" in {
      // test
    }
    "handle missing users" in {
      // test
    }
  }
}

// FeatureSpec - acceptance testing
class UserFeatureSpec extends AnyFeatureSpec with GivenWhenThen {
  Feature("User management") {
    Scenario("Creating a new user") {
      Given("a user registration form")
      When("the user submits valid data")
      Then("a new user is created")
    }
  }
}
```

**Matchers:**

```scala
// Equality
result shouldBe 42
result should equal(42)
result shouldEqual 42

// Comparison
value should be > 10
value should be <= 100

// Collections
list should contain(42)
list should have size 5
list shouldBe empty
list should contain allOf (1, 2, 3)
list should contain oneOf (1, 2, 3)

// Options
option shouldBe defined
option shouldBe empty
option should contain(42)

// Strings
string should startWith("Hello")
string should endWith("World")
string should include("middle")
string should fullyMatch regex "\\d+".r

// Exceptions
the [IllegalArgumentException] thrownBy {
  service.process(null)
} should have message "Input cannot be null"

// Custom matchers
val beEven = be >= 0 and (x => x % 2 == 0)
value should beEven
```

**Fixtures and lifecycle:**

```scala
class DatabaseSpec extends AnyFlatSpec with Matchers with BeforeAndAfter {
  var db: Database = _

  before {
    db = Database.connect()
    db.migrate()
  }

  after {
    db.close()
  }

  "Database" should "insert records" in {
    db.insert(Record("test"))
    db.count() shouldBe 1
  }
}

// Or use BeforeAndAfterEach
class ServiceSpec extends AnyFlatSpec with BeforeAndAfterEach {
  override def beforeEach(): Unit = {
    // Setup before each test
  }

  override def afterEach(): Unit = {
    // Cleanup after each test
  }
}
```

### MUnit - Lightweight Testing

**MUnit basics:**

```scala
import munit.FunSuite

class CalculatorSuite extends FunSuite {
  test("addition works") {
    assertEquals(2 + 3, 5)
  }

  test("division by zero fails") {
    intercept[ArithmeticException] {
      10 / 0
    }
  }

  test("async operation".tag(new Tag("async"))) {
    Future(42).map { result =>
      assertEquals(result, 42)
    }
  }
}
```

**Fixtures:**

```scala
class DatabaseSuite extends FunSuite {
  val db = FunFixture[Database](
    setup = { _ => Database.connect() },
    teardown = { db => db.close() }
  )

  db.test("insert works") { db =>
    db.insert(Record("test"))
    assertEquals(db.count(), 1)
  }
}
```

### specs2 - BDD Style

**specs2 basics:**

```scala
import org.specs2.mutable.Specification

class CalculatorSpec extends Specification {
  "Calculator" should {
    "add two numbers" in {
      val calc = new Calculator
      calc.add(2, 3) must_== 5
    }

    "handle division by zero" in {
      val calc = new Calculator
      calc.divide(10, 0) must throwA[ArithmeticException]
    }
  }
}
```

### ScalaCheck - Property-Based Testing

**Property testing basics:**

```scala
import org.scalacheck.Properties
import org.scalacheck.Prop.forAll

object StringProperties extends Properties("String") {

  property("reverse twice is identity") = forAll { (s: String) =>
    s.reverse.reverse == s
  }

  property("length of concatenation") = forAll { (s1: String, s2: String) =>
    (s1 + s2).length == s1.length + s2.length
  }

  property("startsWith") = forAll { (s: String, prefix: String) =>
    (prefix + s).startsWith(prefix)
  }
}
```

**Custom generators:**

```scala
import org.scalacheck.Gen
import org.scalacheck.Arbitrary

case class User(name: String, age: Int)

val genUser: Gen[User] = for {
  name <- Gen.alphaStr
  age <- Gen.choose(0, 120)
} yield User(name, age)

implicit val arbUser: Arbitrary[User] = Arbitrary(genUser)

property("user age is valid") = forAll { (user: User) =>
  user.age >= 0 && user.age <= 120
}
```

**Integration with ScalaTest:**

```scala
import org.scalatest.flatspec.AnyFlatSpec
import org.scalatest.matchers.should.Matchers
import org.scalatestplus.scalacheck.ScalaCheckPropertyChecks

class ListPropertiesSpec extends AnyFlatSpec with Matchers with ScalaCheckPropertyChecks {

  "List" should "maintain length on reverse" in {
    forAll { (list: List[Int]) =>
      list.reverse.length shouldBe list.length
    }
  }

  it should "preserve elements on sort" in {
    forAll { (list: List[Int]) =>
      list.sorted.toSet shouldBe list.toSet
    }
  }
}
```

### Mocking

**Using Mockito with ScalaTest:**

```scala
import org.scalatestplus.mockito.MockitoSugar
import org.mockito.Mockito._
import org.mockito.ArgumentMatchers._

class UserServiceSpec extends AnyFlatSpec with MockitoSugar with Matchers {

  "UserService" should "fetch user from repository" in {
    val repo = mock[UserRepository]
    val service = new UserService(repo)

    val user = User("Alice", 30)
    when(repo.findById(123)).thenReturn(Some(user))

    val result = service.getUser(123)

    result shouldBe Some(user)
    verify(repo).findById(123)
  }

  it should "handle repository failures" in {
    val repo = mock[UserRepository]
    val service = new UserService(repo)

    when(repo.findById(anyInt())).thenThrow(new DatabaseException("Connection failed"))

    assertThrows[DatabaseException] {
      service.getUser(123)
    }
  }
}
```

**Using ScalaMock:**

```scala
import org.scalamock.scalatest.MockFactory

class EmailServiceSpec extends AnyFlatSpec with MockFactory with Matchers {

  "EmailService" should "send email via SMTP" in {
    val smtp = mock[SmtpClient]
    val service = new EmailService(smtp)

    (smtp.send _)
      .expects("alice@example.com", "Hello", "Message body")
      .returning(true)
      .once()

    service.sendEmail("alice@example.com", "Hello", "Message body") shouldBe true
  }
}
```

### Async Testing

**Testing Futures:**

```scala
import org.scalatest.concurrent.ScalaFutures
import org.scalatest.time.{Seconds, Span}

class AsyncServiceSpec extends AnyFlatSpec with ScalaFutures with Matchers {
  implicit val patience = PatienceConfig(timeout = Span(5, Seconds))

  "AsyncService" should "fetch data asynchronously" in {
    val future = service.fetchData()

    whenReady(future) { result =>
      result shouldBe "data"
    }
  }

  it should "handle failures" in {
    val future = service.fetchInvalid()

    whenReady(future.failed) { exception =>
      exception shouldBe a [NotFoundException]
    }
  }
}
```

**Testing Cats Effect IO:**

```scala
import cats.effect.testing.scalatest.AsyncIOSpec

class IOServiceSpec extends AsyncIOSpec with Matchers {

  "IOService" should "process data" in {
    service.processData().asserting { result =>
      result shouldBe "processed"
    }
  }

  it should "handle errors" in {
    service.processInvalid().assertThrows[ValidationError]
  }
}
```

---

## Cross-Cutting Patterns

For cross-language comparison and translation patterns, see:

- `patterns-concurrency-dev` - Futures, actors, effects comparison across languages
- `patterns-serialization-dev` - JSON handling, schema validation patterns
- `patterns-metaprogramming-dev` - Macros, implicits, type classes vs other languages

---

## References

### Official Documentation

- **Scala Documentation:** https://docs.scala-lang.org/
- **Scala 3 Book:** https://docs.scala-lang.org/scala3/book/introduction.html
- **API Docs:** https://www.scala-lang.org/api/current/

### Books

- **Programming in Scala (Odersky, Spoon, Venners)**
- **Functional Programming in Scala (Chiusano, Bjarnason)**
- **Scala with Cats (Underscore)**

### Community Resources

- **Scala Center:** https://scala.epfl.ch/
- **Scala Users Forum:** https://users.scala-lang.org/
- **ScalaDex (package index):** https://index.scala-lang.org/

### Build Tools

- **sbt:** https://www.scala-sbt.org/
- **Mill:** https://mill-build.org/
- **Maven:** https://maven.apache.org/
- **Gradle:** https://gradle.org/

### Testing

- **ScalaTest:** https://www.scalatest.org/
- **Specs2:** https://etorreborre.github.io/specs2/
- **MUnit:** https://scalameta.org/munit/
- **ScalaCheck:** https://scalacheck.org/

### Related Skills

When you need specialized functionality:

- **Akka (actors, streams):** Use `lang-scala-akka-dev`
- **Cats (FP library):** Use `lang-scala-cats-dev`
- **ZIO (effects):** Use `lang-scala-zio-dev`
- **Spark (distributed):** Use `lang-scala-spark-dev`
- **Play Framework:** Use `lang-scala-play-dev`
- **Testing:** Use `lang-scala-testing-dev`

---

## Summary

This skill covers **foundational Scala development**:

- Immutability - val vs var, immutable collections
- Pattern matching - case classes, sealed traits, ADTs
- Traits - interfaces with implementation, mixins
- For-comprehensions - monadic composition
- Error handling - Option, Either, Try
- Collections - List, Vector, Set, Map operations
- Higher-order functions - map, filter, fold, composition
- Type system - variance, bounds, type classes
- Common patterns - builder, type classes, cake, ADTs

For specialized topics, route to the appropriate skill from the hierarchy.
