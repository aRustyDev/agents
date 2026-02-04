---
name: convert-fsharp-scala
description: Bidirectional conversion between Fsharp and Scala. Use when migrating projects between these languages in either direction. Extends meta-convert-dev with Fsharp↔Scala specific patterns.
---

# Convert F# to Scala

Convert F# code to idiomatic Scala. This skill extends `meta-convert-dev` with F#-to-Scala specific type mappings, idiom translations, and tooling for translating functional-first .NET code to JVM functional programming.

## This Skill Extends

- `meta-convert-dev` - Foundational conversion patterns (APTV workflow, testing strategies)

For general concepts like the Analyze → Plan → Transform → Validate workflow, testing strategies, and common pitfalls, see the meta-skill first.

## This Skill Adds

- **Type mappings**: F# types → Scala types (discriminated unions, records, options)
- **Idiom translations**: F# patterns → idiomatic Scala (computation expressions, pattern matching, type providers)
- **Error handling**: F# Result/Option → Scala Option/Either/Try
- **Async patterns**: F# async workflows → Scala Future/Cats Effect/ZIO
- **Paradigm translation**: .NET functional-first → JVM functional/OOP hybrid

## This Skill Does NOT Cover

- General conversion methodology - see `meta-convert-dev`
- F# language fundamentals - see `lang-fsharp-dev`
- Scala language fundamentals - see `lang-scala-dev`
- Type provider advanced patterns - requires manual translation strategy

---

## Quick Reference

| F# | Scala | Notes |
|----|-------|-------|
| `type Person = { Name: string; Age: int }` | `case class Person(name: String, age: Int)` | Records → case classes |
| `type Result<'T,'E> = Ok of 'T \| Error of 'E` | `Either[E, T]` or custom sealed trait | Discriminated unions → sealed traits |
| `Option<'T>` | `Option[T]` | Direct mapping |
| `Result<'T,'E>` | `Either[E, T]` or `Try[T]` | Result → Either (preferred) |
| `List<'T>` | `List[T]` | Direct mapping (immutable) |
| `Array<'T>` | `Array[T]` or `Vector[T]` | Arrays or vectors |
| `'T []` | `Array[T]` | Array syntax |
| `async { ... }` | `Future { ... }` or IO monad | Async → Future or effect systems |
| `seq { ... }` | `LazyList` or `Iterator` | Lazy sequences |
| `let! x = ...` | `for { x <- ... } yield ...` | Computation expressions → for-comprehensions |
| `member _.Method()` | `def method(): Unit` | Methods in classes/traits |
| `\|> ` | `.pipe(_)` or method chaining | Pipe operator → method chaining |
| `>>` | `andThen` | Function composition |
| `[<Attribute>]` | `@annotation` | Attributes → annotations |

## When Converting Code

1. **Analyze source thoroughly** before writing target - understand F# idioms
2. **Map types first** - create type equivalence table for domain models
3. **Preserve semantics** over syntax similarity - embrace Scala's hybrid nature
4. **Adopt target idioms** - don't write "F# code in Scala syntax"
5. **Handle edge cases** - null safety, error paths, resource cleanup
6. **Test equivalence** - same inputs → same outputs
7. **Consider platform differences** - .NET BCL → JVM stdlib/libraries

---

## Type System Mapping

### Primitive Types

| F# | Scala | Notes |
|----|-------|-------|
| `string` | `String` | Direct mapping |
| `int` | `Int` | 32-bit signed integer |
| `int64` | `Long` | 64-bit signed integer |
| `float` / `double` | `Double` | 64-bit floating point |
| `float32` / `single` | `Float` | 32-bit floating point |
| `bool` | `Boolean` | Direct mapping |
| `char` | `Char` | Direct mapping |
| `byte` | `Byte` | 8-bit unsigned (Scala: signed) |
| `unit` | `Unit` | Unit type |
| `obj` | `Any` or `AnyRef` | Base object type |
| `decimal` | `BigDecimal` | Arbitrary precision decimal |
| `bigint` | `BigInt` | Arbitrary precision integer |

**Note on byte:** F# `byte` is unsigned (0-255), Scala `Byte` is signed (-128-127). Use `Int` if unsigned semantics are critical.

### Collection Types

| F# | Scala | Notes |
|----|-------|-------|
| `list<'T>` / `'T list` | `List[T]` | Immutable linked list |
| `array<'T>` / `'T []` | `Array[T]` | Mutable array |
| `array<'T>` / `'T []` | `Vector[T]` | Immutable indexed sequence (preferred) |
| `seq<'T>` | `LazyList[T]` (Scala 2.13+) | Lazy evaluation |
| `seq<'T>` | `Iterator[T]` | One-time iteration |
| `Set<'T>` | `Set[T]` | Immutable set |
| `Map<'K,'V>` | `Map[K, V]` | Immutable map |
| `ResizeArray<'T>` | `mutable.ListBuffer[T]` or `mutable.ArrayBuffer[T]` | Mutable list |
| `'T * 'U` (tuple) | `(T, U)` | Tuple syntax |
| `'T * 'U * 'V` | `(T, U, V)` | Multi-element tuple |

### Composite Types

| F# Pattern | Scala Pattern | Notes |
|------------|---------------|-------|
| `type Person = { Name: string; Age: int }` | `case class Person(name: String, age: Int)` | Records → case classes |
| `type alias UserId = int` | `type UserId = Int` | Type alias |
| `type Color = Red \| Green \| Blue` | `sealed trait Color; case object Red extends Color; ...` | Simple unions → sealed traits with objects |
| `type Result<'T> = Success of 'T \| Failure of string` | `sealed trait Result[T]; case class Success[T](value: T) extends Result[T]; case class Failure[T](error: String) extends Result[T]` | Discriminated unions → sealed traits |
| `type Option<'T> = Some of 'T \| None` | `Option[T]` (built-in) | Built-in in both |
| Single-case union: `type EmailAddress = EmailAddress of string` | `case class EmailAddress(value: String)` or Scala 3 opaque types | Wrapper types |
| `interface ILogger` | `trait Logger` | Interface → trait |
| `type ILogger with member Log : string -> unit` | `trait Logger { def log(message: String): Unit }` | Abstract members |
| `[<Struct>] type Point = { X: float; Y: float }` | Value classes or case classes | Struct types → value classes (limited) |

### Generic Type Mappings

| F# | Scala | Notes |
|----|-------|-------|
| `'T` | `T` or `A` | Generic type parameter |
| `list<'T>` | `List[T]` | Generic collections |
| `'T when 'T : comparison` | `T: Ordering` (type class) | Constrained generics |
| `'T when 'T :> IDisposable` | `T <: AutoCloseable` | Upper bound |
| `^T when ^T : (static member Parse : string -> ^T)` | Type classes via implicits | SRTP → type classes |

---

## Idiom Translation

### Pattern 1: Records to Case Classes

**F#:**
```fsharp
type Person = {
    FirstName: string
    LastName: string
    Age: int
}

let person = { FirstName = "Alice"; LastName = "Smith"; Age = 30 }
let older = { person with Age = 31 }

let fullName person = $"{person.FirstName} {person.LastName}"
```

**Scala:**
```scala
case class Person(
  firstName: String,
  lastName: String,
  age: Int
)

val person = Person("Alice", "Smith", 30)
val older = person.copy(age = 31)

def fullName(person: Person): String = s"${person.firstName} ${person.lastName}"
```

**Why this translation:**
- Case classes provide automatic `copy`, `equals`, `hashCode`, `toString`
- Scala uses camelCase for field names (F# uses PascalCase)
- Copy-and-update syntax is similar: `with` in F#, `copy` in Scala
- String interpolation: F# uses `$""`, Scala uses `s""`

### Pattern 2: Discriminated Unions to Sealed Traits

**F#:**
```fsharp
type PaymentMethod =
    | Cash
    | CreditCard of cardNumber: string
    | DebitCard of cardNumber: string * pin: int

let processPayment method =
    match method with
    | Cash -> "Processing cash"
    | CreditCard cardNumber -> $"Processing card {cardNumber}"
    | DebitCard (cardNumber, _) -> $"Processing debit {cardNumber}"
```

**Scala:**
```scala
sealed trait PaymentMethod
case object Cash extends PaymentMethod
case class CreditCard(cardNumber: String) extends PaymentMethod
case class DebitCard(cardNumber: String, pin: Int) extends PaymentMethod

def processPayment(method: PaymentMethod): String = method match {
  case Cash => "Processing cash"
  case CreditCard(cardNumber) => s"Processing card $cardNumber"
  case DebitCard(cardNumber, _) => s"Processing debit $cardNumber"
}
```

**Why this translation:**
- Sealed traits ensure exhaustive pattern matching like F# discriminated unions
- Case objects for parameterless variants
- Case classes for variants with data
- Pattern matching syntax is similar but Scala uses `match`/`case`
- Compiler enforces exhaustiveness in both languages

### Pattern 3: Option Type Handling

**F#:**
```fsharp
let findUser id =
    if id = 1 then
        Some { FirstName = "Alice"; LastName = "Smith"; Age = 30 }
    else
        None

// Pattern matching
let greet user =
    match user with
    | Some u -> $"Hello, {u.FirstName}"
    | None -> "Hello, stranger"

// Option combinators
let name =
    findUser 1
    |> Option.map (fun u -> u.FirstName)
    |> Option.defaultValue "Anonymous"
```

**Scala:**
```scala
def findUser(id: Int): Option[Person] = {
  if (id == 1)
    Some(Person("Alice", "Smith", 30))
  else
    None
}

// Pattern matching
def greet(user: Option[Person]): String = user match {
  case Some(u) => s"Hello, ${u.firstName}"
  case None => "Hello, stranger"
}

// Option combinators
val name = findUser(1)
  .map(_.firstName)
  .getOrElse("Anonymous")
```

**Why this translation:**
- Both have built-in Option types with Some/None
- F# uses `Option.map`, Scala uses `.map` (method)
- F# `Option.defaultValue` → Scala `.getOrElse`
- F# pipe `|>` → Scala method chaining `.`
- Pattern matching syntax nearly identical

### Pattern 4: Result Type to Either

**F#:**
```fsharp
type Result<'T,'E> =
    | Ok of 'T
    | Error of 'E

let divide x y =
    if y = 0 then
        Error "Division by zero"
    else
        Ok (x / y)

// Railway-oriented programming
let workflow =
    divide 10 2
    |> Result.bind (fun x -> divide x 5)
    |> Result.map (fun x -> x * 2)
```

**Scala:**
```scala
// Use Either[E, T] (right-biased)
def divide(x: Int, y: Int): Either[String, Int] = {
  if (y == 0)
    Left("Division by zero")
  else
    Right(x / y)
}

// Railway-oriented programming
val workflow = for {
  x <- divide(10, 2)
  y <- divide(x, 5)
} yield y * 2

// Or with explicit flatMap/map
val workflow2 = divide(10, 2)
  .flatMap(x => divide(x, 5))
  .map(x => x * 2)
```

**Why this translation:**
- F# Result → Scala Either (right-biased in Scala 2.12+)
- F# `Ok` → Scala `Right`, F# `Error` → Scala `Left`
- F# `Result.bind` → Scala `.flatMap`
- F# `Result.map` → Scala `.map`
- For-comprehensions replace chained bind/map calls

### Pattern 5: Async Workflows to Futures

**F#:**
```fsharp
let fetchData url = async {
    printfn $"Fetching {url}..."
    do! Async.Sleep 1000
    return $"Data from {url}"
}

let processUrls urls = async {
    let! results =
        urls
        |> List.map fetchData
        |> Async.Parallel

    return results |> Array.toList
}

// Run async
let urls = ["url1"; "url2"; "url3"]
processUrls urls |> Async.RunSynchronously
```

**Scala (with Futures):**
```scala
import scala.concurrent.{Future, Await}
import scala.concurrent.duration._
import scala.concurrent.ExecutionContext.Implicits.global

def fetchData(url: String): Future[String] = Future {
  println(s"Fetching $url...")
  Thread.sleep(1000)
  s"Data from $url"
}

def processUrls(urls: List[String]): Future[List[String]] = {
  Future.sequence(urls.map(fetchData))
}

// Run async
val urls = List("url1", "url2", "url3")
val result = Await.result(processUrls(urls), 10.seconds)
```

**Scala (with Cats Effect IO):**
```scala
import cats.effect.{IO, unsafe}
import cats.syntax.parallel._
import scala.concurrent.duration._

def fetchData(url: String): IO[String] = for {
  _ <- IO.println(s"Fetching $url...")
  _ <- IO.sleep(1.second)
} yield s"Data from $url"

def processUrls(urls: List[String]): IO[List[String]] = {
  urls.traverse(fetchData)  // Or urls.parTraverse for parallel
}

// Run IO
val urls = List("url1", "url2", "url3")
processUrls(urls).unsafeRunSync()
```

**Why this translation:**
- F# `async { }` → Scala `Future { }` or `IO { }`
- F# `do!` → Scala `_<-` in for-comprehension
- F# `let!` → Scala `x <-` in for-comprehension
- F# `Async.Parallel` → Scala `Future.sequence` or `traverse`
- F# `Async.RunSynchronously` → Scala `Await.result` (Future) or `unsafeRunSync()` (IO)

### Pattern 6: Computation Expressions to For-Comprehensions

**F#:**
```fsharp
// Option computation expression
let validateAge age =
    if age >= 0 && age <= 120 then Some age
    else None

let validateName name =
    if String.IsNullOrWhiteSpace(name) then None
    else Some name

let createPerson name age = option {
    let! validName = validateName name
    let! validAge = validateAge age
    return { FirstName = validName; LastName = ""; Age = validAge }
}
```

**Scala:**
```scala
// Option for-comprehension
def validateAge(age: Int): Option[Int] = {
  if (age >= 0 && age <= 120) Some(age)
  else None
}

def validateName(name: String): Option[String] = {
  if (name == null || name.trim.isEmpty) None
  else Some(name)
}

def createPerson(name: String, age: Int): Option[Person] = for {
  validName <- validateName(name)
  validAge <- validateAge(age)
} yield Person(validName, "", validAge)
```

**Why this translation:**
- F# computation expressions → Scala for-comprehensions
- F# `let!` → Scala `<-` (bind/flatMap)
- F# `return` → Scala `yield` (map)
- Both desugar to flatMap/map chains
- Scala for-comprehensions work with any type that has flatMap/map

### Pattern 7: Pattern Matching with Guards

**F#:**
```fsharp
let classify n =
    match n with
    | x when x < 0 -> "negative"
    | 0 -> "zero"
    | x when x % 2 = 0 -> "even positive"
    | _ -> "odd positive"

// List pattern matching
let sumFirst list =
    match list with
    | [] -> 0
    | [x] -> x
    | x :: xs -> x + sumFirst xs
```

**Scala:**
```scala
def classify(n: Int): String = n match {
  case x if x < 0 => "negative"
  case 0 => "zero"
  case x if x % 2 == 0 => "even positive"
  case _ => "odd positive"
}

// List pattern matching
def sumFirst(list: List[Int]): Int = list match {
  case Nil => 0
  case x :: Nil => x
  case x :: xs => x + sumFirst(xs)
}
```

**Why this translation:**
- F# `when` guards → Scala `if` guards
- F# `[]` → Scala `Nil`
- F# `x :: xs` → Scala `x :: xs` (same cons operator)
- Both support deep pattern matching
- Scala enforces exhaustiveness on sealed types

### Pattern 8: Active Patterns to Custom Extractors

**F#:**
```fsharp
// Active pattern for even/odd
let (|Even|Odd|) n =
    if n % 2 = 0 then Even else Odd

match 42 with
| Even -> "even"
| Odd -> "odd"

// Partial active pattern
let (|Integer|_|) (str: string) =
    match System.Int32.TryParse(str) with
    | true, value -> Some value
    | false, _ -> None

match "123" with
| Integer n -> $"Number: {n}"
| _ -> "Not a number"
```

**Scala:**
```scala
// Custom extractor for even/odd
object Even {
  def unapply(n: Int): Option[Int] = if (n % 2 == 0) Some(n) else None
}

object Odd {
  def unapply(n: Int): Option[Int] = if (n % 2 != 0) Some(n) else None
}

42 match {
  case Even(n) => "even"
  case Odd(n) => "odd"
}

// Partial extractor
object IntegerString {
  def unapply(str: String): Option[Int] = {
    try {
      Some(str.toInt)
    } catch {
      case _: NumberFormatException => None
    }
  }
}

"123" match {
  case IntegerString(n) => s"Number: $n"
  case _ => "Not a number"
}
```

**Why this translation:**
- F# active patterns → Scala custom extractors (`unapply`)
- F# parameterless active patterns → Scala objects with `unapply`
- F# partial active patterns returning `Option` → Scala `unapply` returning `Option`
- Both enable extensible pattern matching
- Scala extractors are more verbose but more flexible

### Pattern 9: Units of Measure to Tagged Types

**F#:**
```fsharp
[<Measure>] type kg
[<Measure>] type m
[<Measure>] type s

let distance = 100.0<m>
let time = 10.0<s>
let speed = distance / time  // Type: float<m/s>

// Prevents mixing units
let mass = 50.0<kg>
// let invalid = distance + mass  // Compile error!
```

**Scala (with Tagged Types):**
```scala
// Using shapeless tagged types (library)
import shapeless.tag._
import shapeless.tag

trait Kg
trait M
trait S

type Kilograms = Double @@ Kg
type Meters = Double @@ M
type Seconds = Double @@ S

val distance: Meters = tag[M](100.0)
val time: Seconds = tag[S](10.0)
// val speed = distance / time  // Would need custom operators

// Or use value classes (zero runtime overhead)
case class Kilograms(value: Double) extends AnyVal
case class Meters(value: Double) extends AnyVal
case class Seconds(value: Double) extends AnyVal

val distance = Meters(100.0)
val time = Seconds(10.0)
// val invalid = distance.value + Kilograms(50.0).value  // No type safety at operation level
```

**Scala 3 (with Opaque Types):**
```scala
object Units {
  opaque type Kilograms = Double
  opaque type Meters = Double
  opaque type Seconds = Double

  object Kilograms {
    def apply(value: Double): Kilograms = value
    extension (kg: Kilograms) def value: Double = kg
  }

  object Meters {
    def apply(value: Double): Meters = value
    extension (m: Meters) def value: Double = m
  }

  object Seconds {
    def apply(value: Double): Seconds = value
    extension (s: Seconds) def value: Double = s
  }
}

import Units._
val distance = Meters(100.0)
val time = Seconds(10.0)
```

**Why this translation:**
- F# units of measure have no direct Scala equivalent
- Scala 2: Use tagged types (shapeless) or value classes
- Scala 3: Opaque types provide zero-cost abstraction
- F# provides compile-time dimension checking, Scala only type checking
- Trade-off: F# has better unit inference, Scala requires more manual work

### Pattern 10: Type Providers to Code Generation

**F#:**
```fsharp
open FSharp.Data

// Type provider infers schema from JSON sample
type Weather = JsonProvider<"""
{
    "temperature": 72.5,
    "condition": "sunny",
    "humidity": 65
}
""">

let weather = Weather.Load("weather.json")
printfn $"Temperature: {weather.Temperature}°F"
```

**Scala:**
```scala
// No direct equivalent - use code generation or libraries

// Option 1: Manual case classes
case class Weather(
  temperature: Double,
  condition: String,
  humidity: Int
)

// Option 2: Use circe for JSON (runtime decoding)
import io.circe._
import io.circe.generic.semiauto._

case class Weather(temperature: Double, condition: String, humidity: Int)
implicit val weatherDecoder: Decoder[Weather] = deriveDecoder[Weather]

val json = """{"temperature":72.5,"condition":"sunny","humidity":65}"""
val weather = parser.decode[Weather](json)

// Option 3: Use sbt-swagger-codegen plugin for OpenAPI
// Generates case classes from OpenAPI/Swagger specs at compile time

// Option 4: Scala 3 macros (advanced)
// Can generate types at compile time from external sources
```

**Why this translation:**
- F# type providers have no direct Scala equivalent
- Scala alternatives:
  1. **Manual case classes** - most common, explicit
  2. **Runtime JSON libraries** - circe, play-json, upickle
  3. **Code generation plugins** - sbt plugins for OpenAPI, Protobuf, etc.
  4. **Scala 3 macros** - can achieve similar results but more complex
- F# advantage: compile-time type safety from external data sources
- Scala advantage: more explicit, easier to debug, better tooling support

---

## Error Handling

### F# Result/Option → Scala Option/Either/Try

F# uses Result and Option types for error handling. Scala has Option, Either, and Try.

| F# | Scala | Use Case |
|----|-------|----------|
| `Option<'T>` | `Option[T]` | Value may be absent |
| `Result<'T,'E>` | `Either[E, T]` | Typed errors (preferred) |
| `Result<'T,exn>` | `Try[T]` | Exception wrapping |

**F# Result translation:**
```fsharp
type Result<'T,'E> =
    | Ok of 'T
    | Error of 'E

let divide x y =
    if y = 0 then
        Error "Division by zero"
    else
        Ok (x / y)

// Railway-oriented programming
let calculation =
    divide 10 2
    |> Result.bind (fun x -> divide x 5)
    |> Result.map (fun x -> x * 2)
```

**Scala Either (preferred):**
```scala
type Result[T] = Either[String, T]

def divide(x: Int, y: Int): Either[String, Int] = {
  if (y == 0)
    Left("Division by zero")
  else
    Right(x / y)
}

// Railway-oriented programming
val calculation = for {
  x <- divide(10, 2)
  y <- divide(x, 5)
} yield y * 2

// Or explicit flatMap/map
val calculation2 = divide(10, 2)
  .flatMap(x => divide(x, 5))
  .map(x => x * 2)
```

**Scala Try (for exception wrapping):**
```scala
import scala.util.{Try, Success, Failure}

def divide(x: Int, y: Int): Try[Int] = Try {
  if (y == 0) throw new ArithmeticException("Division by zero")
  x / y
}

divide(10, 2) match {
  case Success(value) => println(s"Result: $value")
  case Failure(exception) => println(s"Error: ${exception.getMessage}")
}
```

**Custom error types:**
```fsharp
// F#
type ValidationError =
    | EmptyString
    | InvalidFormat
    | OutOfRange

let validateAge age : Result<int, ValidationError> =
    if age < 0 || age > 120 then
        Error OutOfRange
    else
        Ok age
```

```scala
// Scala
sealed trait ValidationError
case object EmptyString extends ValidationError
case object InvalidFormat extends ValidationError
case object OutOfRange extends ValidationError

def validateAge(age: Int): Either[ValidationError, Int] = {
  if (age < 0 || age > 120)
    Left(OutOfRange)
  else
    Right(age)
}
```

---

## Concurrency Patterns

### F# Async Workflows → Scala Futures/Effects

F# uses async workflows and Async module. Scala has multiple options: Futures (simple), Cats Effect (functional), ZIO (full effect system).

| F# | Scala (Future) | Scala (Cats Effect) | Scala (ZIO) |
|----|----------------|---------------------|-------------|
| `async { }` | `Future { }` | `IO { }` | `ZIO.attempt { }` |
| `do!` | `_ <- future` | `_ <- io` | `_ <- zio` |
| `let!` | `x <- future` | `x <- io` | `x <- zio` |
| `return` | `x` (last expression) | `IO.pure(x)` | `ZIO.succeed(x)` |
| `Async.Parallel` | `Future.sequence` | `traverse` / `parTraverse` | `ZIO.collectAllPar` |
| `Async.RunSynchronously` | `Await.result` | `unsafeRunSync()` | `Unsafe.run` |

**Example: Parallel execution**

**F#:**
```fsharp
let fetchUser id = async {
    do! Async.Sleep 100
    return $"User {id}"
}

let fetchAll ids = async {
    let! users =
        ids
        |> List.map fetchUser
        |> Async.Parallel
    return users |> Array.toList
}

fetchAll [1; 2; 3] |> Async.RunSynchronously
```

**Scala (Future):**
```scala
import scala.concurrent.{Future, Await}
import scala.concurrent.ExecutionContext.Implicits.global
import scala.concurrent.duration._

def fetchUser(id: Int): Future[String] = Future {
  Thread.sleep(100)
  s"User $id"
}

def fetchAll(ids: List[Int]): Future[List[String]] = {
  Future.sequence(ids.map(fetchUser))
}

Await.result(fetchAll(List(1, 2, 3)), 10.seconds)
```

**Scala (Cats Effect IO):**
```scala
import cats.effect.IO
import cats.syntax.parallel._
import scala.concurrent.duration._

def fetchUser(id: Int): IO[String] = for {
  _ <- IO.sleep(100.millis)
} yield s"User $id"

def fetchAll(ids: List[Int]): IO[List[String]] = {
  ids.parTraverse(fetchUser)  // Parallel
  // or ids.traverse(fetchUser) for sequential
}

fetchAll(List(1, 2, 3)).unsafeRunSync()
```

**Key differences:**
- F# async is cold (doesn't run until explicitly started)
- Scala Future is hot (starts immediately upon creation)
- Cats Effect IO is cold (like F# async)
- Use IO/ZIO for resource-safe, referentially transparent effects

---

## Common Pitfalls

### 1. PascalCase vs camelCase

**Problem:** F# uses PascalCase for everything, Scala uses camelCase for members.

```fsharp
// F# style
type Person = {
    FirstName: string
    LastName: string
}

let GetFullName person = $"{person.FirstName} {person.LastName}"
```

**Fix:** Follow Scala conventions

```scala
// Scala style
case class Person(
  firstName: String,  // camelCase
  lastName: String
)

def getFullName(person: Person): String = s"${person.firstName} ${person.lastName}"
```

### 2. Pipe Operator Overuse

**Problem:** Trying to replicate F# pipe operator (`|>`) everywhere.

```scala
// ❌ Bad: Non-idiomatic
def |>[A, B](a: A, f: A => B): B = f(a)

val result = 5 |> (x => x + 1) |> (x => x * 2)
```

**Fix:** Use Scala's method chaining

```scala
// ✓ Good: Idiomatic Scala
val result = 5
  .pipe(x => x + 1)
  .pipe(x => x * 2)

// Or even better with direct chaining
val result = List(1, 2, 3)
  .map(_ + 1)
  .filter(_ > 2)
  .sum
```

### 3. Result Type Confusion

**Problem:** F# Result has Ok/Error, Scala Either has Right/Left (right-biased).

```scala
// ❌ Bad: Using Either like F# Result
def divide(x: Int, y: Int): Either[Int, String] = {
  if (y == 0)
    Right("Division by zero")  // Wrong: should be Left
  else
    Left(x / y)  // Wrong: should be Right
}
```

**Fix:** Remember Either is right-biased (Right for success)

```scala
// ✓ Good: Correct Either usage
def divide(x: Int, y: Int): Either[String, Int] = {
  if (y == 0)
    Left("Division by zero")  // Error on Left
  else
    Right(x / y)  // Success on Right
}
```

### 4. Discriminated Union Translation

**Problem:** Trying to use case classes like F# union cases.

```scala
// ❌ Bad: Single case class hierarchy without sealed trait
case class Success(value: Int)
case class Failure(error: String)

def handle(result: Any): String = result match {
  case Success(v) => s"Got $v"
  case Failure(e) => s"Error: $e"
  // Missing: no exhaustiveness checking
}
```

**Fix:** Use sealed traits for exhaustiveness

```scala
// ✓ Good: Sealed trait for ADT
sealed trait Result
case class Success(value: Int) extends Result
case class Failure(error: String) extends Result

def handle(result: Result): String = result match {
  case Success(v) => s"Got $v"
  case Failure(e) => s"Error: $e"
  // Compiler ensures exhaustiveness
}
```

### 5. Computation Expression to For-Comprehension Mismatch

**Problem:** F# computation expressions have custom builders, Scala for-comprehensions require flatMap/map.

```fsharp
// F# custom computation expression
type MaybeBuilder() =
    member _.Bind(x, f) = Option.bind f x
    member _.Return(x) = Some x
    member _.ReturnFrom(x) = x
    member _.Zero() = None

let maybe = MaybeBuilder()

let result = maybe {
    let! x = Some 10
    let! y = Some 20
    return x + y
}
```

```scala
// Scala: Can only use types that have flatMap/map
// Option already has these, so for-comprehension works

val result = for {
  x <- Some(10)
  y <- Some(20)
} yield x + y

// For custom types, must implement flatMap/map
class Maybe[A](value: Option[A]) {
  def flatMap[B](f: A => Maybe[B]): Maybe[B] = {
    value match {
      case Some(v) => f(v)
      case None => new Maybe(None)
    }
  }

  def map[B](f: A => B): Maybe[B] = {
    new Maybe(value.map(f))
  }
}
```

### 6. Async Workflow Startup Semantics

**Problem:** F# async is cold (lazy), Scala Future is hot (eager).

```scala
// ❌ Bad: Assuming Future is lazy like F# async
val future = Future {
  println("Running expensive operation")
  expensiveComputation()
}
// Prints immediately! Future started as soon as it's created

// Later in code...
future.map(result => process(result))  // Operation already running
```

**Fix:** Use Cats Effect IO or ZIO for lazy async (or accept Future's eager semantics)

```scala
// ✓ Good: Using IO for lazy async (like F# async)
import cats.effect.IO

val io = IO {
  println("Running expensive operation")
  expensiveComputation()
}
// Nothing printed yet - IO is lazy

// Later in code...
io.map(result => process(result))  // Still not running

// Must explicitly run
io.unsafeRunSync()  // Now it runs
```

### 7. Type Provider Expectations

**Problem:** Expecting Scala to have type providers like F#.

```fsharp
// F# has compile-time type generation
open FSharp.Data
type Users = JsonProvider<"users.json">
let users = Users.Load("users.json")
users.Items.[0].Name  // Full IntelliSense!
```

**Fix:** Use appropriate Scala alternatives

```scala
// Scala: Define types manually or use code generation

// Option 1: Manual (most common)
case class User(name: String, age: Int, email: String)

import io.circe.generic.auto._
import io.circe.parser._

val json = """[{"name":"Alice","age":30,"email":"alice@example.com"}]"""
val users = decode[List[User]](json)

// Option 2: Use sbt plugins for code generation
// plugins.sbt:
// addSbtPlugin("io.swagger" % "sbt-swagger-codegen" % "0.1.0")
```

### 8. Railway-Oriented Programming Style

**Problem:** Overusing F#-style railway-oriented programming without leveraging Scala's for-comprehensions.

```scala
// ❌ Bad: Transliterating F# style
val result = divide(10, 2)
  .flatMap(x => divide(x, 5))
  .flatMap(x => divide(x, 1))
  .map(x => x * 2)
```

**Fix:** Use for-comprehensions for readability

```scala
// ✓ Good: Idiomatic Scala
val result = for {
  x <- divide(10, 2)
  y <- divide(x, 5)
  z <- divide(y, 1)
} yield z * 2
```

---

## Tooling

### Build Tools

| F# | Scala | Notes |
|----|-------|-------|
| .NET CLI (`dotnet`) | sbt | Primary build tool |
| .fsproj | build.sbt | Project configuration |
| Paket | Coursier | Dependency resolution |
| FAKE | Mill | Alternative build tool |
| NuGet | Maven Central | Package repository |

**Build comparison:**

```bash
# F#
dotnet build
dotnet test
dotnet run

# Scala
sbt compile
sbt test
sbt run
```

### IDE Support

| Feature | F# | Scala |
|---------|-----|-------|
| Visual Studio | ✓ | - |
| Visual Studio Code | ✓ (Ionide) | ✓ (Metals) |
| JetBrains | Rider | IntelliJ IDEA |
| Vim/Neovim | ✓ (coc.nvim) | ✓ (coc-metals) |

### Testing Frameworks

| F# | Scala | Notes |
|----|-------|-------|
| Expecto | ScalaTest | BDD-style testing |
| xUnit.net | MUnit | xUnit-style testing |
| FsUnit | specs2 | Fluent assertions |
| FsCheck | ScalaCheck | Property-based testing |

### Code Formatting

| F# | Scala | Command |
|----|-------|---------|
| Fantomas | Scalafmt | Auto-formatting |

```bash
# F#
dotnet fantomas .

# Scala
sbt scalafmt
```

### Useful Libraries

| Purpose | F# | Scala |
|---------|-----|-------|
| JSON | FSharp.Data, Thoth.Json | circe, play-json, upickle |
| HTTP client | FsHttp | http4s, sttp, requests-scala |
| Effect system | - (built-in async) | Cats Effect, ZIO |
| Validation | FsToolkit.ErrorHandling | Cats Validated, ZIO Prelude |
| Testing | Expecto, FsCheck | ScalaTest, ScalaCheck, MUnit |
| Collections | FSharpPlus | Cats, Scalaz |
| Parsing | FParsec | fastparse, cats-parse |

---

## Paradigm Translation

### Functional-First (.NET) → Functional/OOP Hybrid (JVM)

F# is functional-first on .NET, Scala is a hybrid functional/OOP language on JVM.

**Mental model shifts:**

| F# Approach | Scala Approach | Key Insight |
|-------------|----------------|-------------|
| Modules with functions | Objects with methods or traits | Data and behavior can be separate or combined |
| Computation expressions | For-comprehensions or effect systems | Monadic composition is built-in to language |
| Type providers | Manual types or code generation | More explicit, less magic |
| Units of measure | Tagged types or value classes | Less type safety, more verbosity |
| Active patterns | Custom extractors | More boilerplate, more flexibility |
| Discriminated unions | Sealed traits + case classes/objects | More verbose but more powerful |
| Records | Case classes | Similar functionality, different syntax |

**Object-oriented integration:**

F# prefers module functions, Scala embraces both styles:

```fsharp
// F# module style (preferred)
module UserService =
    let findById id = // ...
    let save user = // ...
```

```scala
// Scala: can use either style

// Functional style (similar to F#)
object UserService {
  def findById(id: Int): Option[User] = ???
  def save(user: User): Unit = ???
}

// OOP style (Scala-specific)
trait UserService {
  def findById(id: Int): Option[User]
  def save(user: User): Unit
}

class UserServiceImpl extends UserService {
  def findById(id: Int): Option[User] = ???
  def save(user: User): Unit = ???
}
```

**When to use OOP in Scala:**
- Dependency injection (traits as interfaces)
- Plugin architecture (trait hierarchies)
- State management (classes with mutable state)
- Java interop (Java expects classes/interfaces)

**When to use FP in Scala:**
- Pure transformations (map, filter, fold)
- Immutable data structures
- Error handling (Option, Either, Try)
- Effect management (IO, ZIO)

---

## Examples

### Example 1: Simple - Domain Model Translation

Convert a simple F# domain model to Scala.

**Before (F#):**
```fsharp
type EmailAddress = EmailAddress of string

module EmailAddress =
    let create email =
        if email.Contains("@") then
            Ok (EmailAddress email)
        else
            Error "Invalid email format"

    let value (EmailAddress email) = email

type Person = {
    Name: string
    Email: EmailAddress
    Age: int
}

let createPerson name email age =
    match EmailAddress.create email with
    | Ok validEmail ->
        Ok { Name = name; Email = validEmail; Age = age }
    | Error msg ->
        Error msg
```

**After (Scala):**
```scala
case class EmailAddress private (value: String)

object EmailAddress {
  def create(email: String): Either[String, EmailAddress] = {
    if (email.contains("@"))
      Right(EmailAddress(email))
    else
      Left("Invalid email format")
  }
}

case class Person(
  name: String,
  email: EmailAddress,
  age: Int
)

def createPerson(name: String, email: String, age: Int): Either[String, Person] = {
  EmailAddress.create(email).map(validEmail =>
    Person(name, validEmail, age)
  )
}

// Or with for-comprehension
def createPerson2(name: String, email: String, age: Int): Either[String, Person] = for {
  validEmail <- EmailAddress.create(email)
} yield Person(name, validEmail, age)
```

---

### Example 2: Medium - Result-Based Validation

Convert F# railway-oriented validation to Scala.

**Before (F#):**
```fsharp
type ValidationError =
    | EmptyName
    | InvalidAge
    | InvalidEmail

type ValidatedPerson = {
    Name: string
    Email: string
    Age: int
}

let validateName name =
    if String.IsNullOrWhiteSpace(name) then
        Error EmptyName
    else
        Ok name

let validateAge age =
    if age < 0 || age > 120 then
        Error InvalidAge
    else
        Ok age

let validateEmail email =
    if email.Contains("@") then
        Ok email
    else
        Error InvalidEmail

let validatePerson name email age =
    result {
        let! validName = validateName name
        let! validEmail = validateEmail email
        let! validAge = validateAge age
        return {
            Name = validName
            Email = validEmail
            Age = validAge
        }
    }

// Usage
match validatePerson "Alice" "alice@example.com" 30 with
| Ok person -> printfn $"Valid: {person.Name}"
| Error EmptyName -> printfn "Name is empty"
| Error InvalidAge -> printfn "Age is invalid"
| Error InvalidEmail -> printfn "Email is invalid"
```

**After (Scala):**
```scala
sealed trait ValidationError
case object EmptyName extends ValidationError
case object InvalidAge extends ValidationError
case object InvalidEmail extends ValidationError

case class ValidatedPerson(
  name: String,
  email: String,
  age: Int
)

def validateName(name: String): Either[ValidationError, String] = {
  if (name == null || name.trim.isEmpty)
    Left(EmptyName)
  else
    Right(name)
}

def validateAge(age: Int): Either[ValidationError, Int] = {
  if (age < 0 || age > 120)
    Left(InvalidAge)
  else
    Right(age)
}

def validateEmail(email: String): Either[ValidationError, String] = {
  if (email.contains("@"))
    Right(email)
  else
    Left(InvalidEmail)
}

def validatePerson(name: String, email: String, age: Int): Either[ValidationError, ValidatedPerson] = for {
  validName <- validateName(name)
  validEmail <- validateEmail(email)
  validAge <- validateAge(age)
} yield ValidatedPerson(validName, validEmail, validAge)

// Usage
validatePerson("Alice", "alice@example.com", 30) match {
  case Right(person) => println(s"Valid: ${person.name}")
  case Left(EmptyName) => println("Name is empty")
  case Left(InvalidAge) => println("Age is invalid")
  case Left(InvalidEmail) => println("Email is invalid")
}
```

---

### Example 3: Complex - Async Workflow with Error Handling

Convert a complete F# async application with error handling to Scala.

**Before (F#):**
```fsharp
open System

type ApiError =
    | NetworkError of message: string
    | NotFound
    | InvalidResponse of message: string

type User = {
    Id: int
    Name: string
    Email: string
}

type UserRepository =
    abstract member FindById: int -> Async<Result<User, ApiError>>
    abstract member Save: User -> Async<Result<unit, ApiError>>

type HttpClient =
    abstract member Get: string -> Async<Result<string, ApiError>>
    abstract member Post: string -> string -> Async<Result<string, ApiError>>

let parseUserJson (json: string) : Result<User, ApiError> =
    try
        // Simplified JSON parsing
        let user = {
            Id = 1
            Name = "Alice"
            Email = "alice@example.com"
        }
        Ok user
    with
    | ex -> Error (InvalidResponse ex.Message)

let fetchAndUpdateUser (client: HttpClient) (repo: UserRepository) userId = async {
    // Fetch user from repository
    let! userResult = repo.FindById userId

    match userResult with
    | Error err -> return Error err
    | Ok user ->
        // Fetch additional data from API
        let! apiResult = client.Get $"https://api.example.com/users/{userId}"

        match apiResult with
        | Error err -> return Error err
        | Ok json ->
            match parseUserJson json with
            | Error err -> return Error err
            | Ok apiUser ->
                // Update and save
                let updated = { user with Email = apiUser.Email }
                let! saveResult = repo.Save updated

                match saveResult with
                | Error err -> return Error err
                | Ok () -> return Ok updated
}

// Better with computation expression
let fetchAndUpdateUserCE (client: HttpClient) (repo: UserRepository) userId = async {
    let! userResult = repo.FindById userId

    return!
        match userResult with
        | Error err -> async { return Error err }
        | Ok user -> async {
            let! apiResult = client.Get $"https://api.example.com/users/{userId}"

            return!
                match apiResult with
                | Error err -> async { return Error err }
                | Ok json ->
                    match parseUserJson json with
                    | Error err -> async { return Error err }
                    | Ok apiUser ->
                        let updated = { user with Email = apiUser.Email }
                        let! saveResult = repo.Save updated

                        return
                            match saveResult with
                            | Error err -> Error err
                            | Ok () -> Ok updated
        }
}
```

**After (Scala with Cats Effect):**
```scala
import cats.effect.IO
import cats.syntax.either._
import cats.syntax.flatMap._
import cats.syntax.functor._

sealed trait ApiError
case class NetworkError(message: String) extends ApiError
case object NotFound extends ApiError
case class InvalidResponse(message: String) extends ApiError

case class User(
  id: Int,
  name: String,
  email: String
)

trait UserRepository {
  def findById(id: Int): IO[Either[ApiError, User]]
  def save(user: User): IO[Either[ApiError, Unit]]
}

trait HttpClient {
  def get(url: String): IO[Either[ApiError, String]]
  def post(url: String, body: String): IO[Either[ApiError, String]]
}

def parseUserJson(json: String): Either[ApiError, User] = {
  try {
    // Simplified JSON parsing
    val user = User(1, "Alice", "alice@example.com")
    Right(user)
  } catch {
    case ex: Exception => Left(InvalidResponse(ex.getMessage))
  }
}

def fetchAndUpdateUser(
  client: HttpClient,
  repo: UserRepository,
  userId: Int
): IO[Either[ApiError, User]] = {
  for {
    userResult <- repo.findById(userId)
    result <- userResult match {
      case Left(err) => IO.pure(Left(err))
      case Right(user) =>
        for {
          apiResult <- client.get(s"https://api.example.com/users/$userId")
          finalResult <- apiResult match {
            case Left(err) => IO.pure(Left(err))
            case Right(json) =>
              parseUserJson(json) match {
                case Left(err) => IO.pure(Left(err))
                case Right(apiUser) =>
                  val updated = user.copy(email = apiUser.email)
                  repo.save(updated).map(_.map(_ => updated))
              }
          }
        } yield finalResult
    }
  } yield result
}

// Better with EitherT (monad transformer)
import cats.data.EitherT

def fetchAndUpdateUserET(
  client: HttpClient,
  repo: UserRepository,
  userId: Int
): IO[Either[ApiError, User]] = {
  val result = for {
    user <- EitherT(repo.findById(userId))
    json <- EitherT(client.get(s"https://api.example.com/users/$userId"))
    apiUser <- EitherT.fromEither[IO](parseUserJson(json))
    updated = user.copy(email = apiUser.email)
    _ <- EitherT(repo.save(updated))
  } yield updated

  result.value
}

// Or with Cats Effect's built-in error handling
def fetchAndUpdateUserSimple(
  client: HttpClient,
  repo: UserRepository,
  userId: Int
): IO[User] = {
  for {
    user <- repo.findById(userId).flatMap(IO.fromEither)
    json <- client.get(s"https://api.example.com/users/$userId").flatMap(IO.fromEither)
    apiUser <- IO.fromEither(parseUserJson(json))
    updated = user.copy(email = apiUser.email)
    _ <- repo.save(updated).flatMap(IO.fromEither)
  } yield updated
}
```

**Scala (with ZIO):**
```scala
import zio._

sealed trait ApiError
case class NetworkError(message: String) extends ApiError
case object NotFound extends ApiError
case class InvalidResponse(message: String) extends ApiError

case class User(id: Int, name: String, email: String)

trait UserRepository {
  def findById(id: Int): IO[ApiError, User]
  def save(user: User): IO[ApiError, Unit]
}

trait HttpClient {
  def get(url: String): IO[ApiError, String]
  def post(url: String, body: String): IO[ApiError, String]
}

def parseUserJson(json: String): IO[ApiError, User] = ZIO.attempt {
  User(1, "Alice", "alice@example.com")
}.mapError(ex => InvalidResponse(ex.getMessage))

def fetchAndUpdateUser(
  client: HttpClient,
  repo: UserRepository,
  userId: Int
): IO[ApiError, User] = for {
  user <- repo.findById(userId)
  json <- client.get(s"https://api.example.com/users/$userId")
  apiUser <- parseUserJson(json)
  updated = user.copy(email = apiUser.email)
  _ <- repo.save(updated)
} yield updated

// ZIO automatically handles error propagation with IO[E, A]
// No need for Either wrapping or EitherT
```

---

## See Also

For more examples and patterns, see:
- `meta-convert-dev` - Foundational patterns with cross-language examples
- `lang-fsharp-dev` - F# development patterns
- `lang-scala-dev` - Scala development patterns

Cross-cutting pattern skills:
- `patterns-concurrency-dev` - Async workflows, actors, effects across languages
- `patterns-serialization-dev` - JSON, validation patterns across languages
- `patterns-metaprogramming-dev` - Type providers, macros, type classes comparison
