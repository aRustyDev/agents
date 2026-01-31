---
name: convert-scala-fsharp
description: Convert Scala code to idiomatic F#. Use when migrating Scala projects to F#, translating JVM functional/OOP patterns to .NET functional-first programming, or refactoring Scala codebases to F#. Extends meta-convert-dev with Scala-to-F# specific patterns for case classes, sealed traits, and functional programming idioms.
---

# Convert Scala to F#

Convert Scala code to idiomatic F#. This skill extends `meta-convert-dev` with Scala-to-F# specific type mappings, idiom translations, and tooling for translating JVM functional/OOP hybrid code to .NET functional-first programming.

## This Skill Extends

- `meta-convert-dev` - Foundational conversion patterns (APTV workflow, testing strategies)

For general concepts like the Analyze → Plan → Transform → Validate workflow, testing strategies, and common pitfalls, see the meta-skill first.

## This Skill Adds

- **Type mappings**: Scala types → F# types (case classes, sealed traits, Option/Either)
- **Idiom translations**: Scala patterns → idiomatic F# (for-comprehensions, pattern matching, implicits)
- **Error handling**: Scala Option/Either/Try → F# Option/Result
- **Async patterns**: Scala Future/IO → F# async workflows
- **Paradigm translation**: JVM functional/OOP hybrid → .NET functional-first

## This Skill Does NOT Cover

- General conversion methodology - see `meta-convert-dev`
- Scala language fundamentals - see `lang-scala-dev`
- F# language fundamentals - see `lang-fsharp-dev`
- Reverse conversion (F# → Scala) - see `convert-fsharp-scala`
- Advanced Scala 3 features (union types, match types) - requires manual translation

---

## Quick Reference

| Scala | F# | Notes |
|-------|-----|-------|
| `case class Person(name: String, age: Int)` | `type Person = { Name: string; Age: int }` | Case classes → records |
| `sealed trait Result[T]` | `type Result<'T,'E> = Ok of 'T \| Error of 'E` | Sealed traits → discriminated unions |
| `Option[T]` | `Option<'T>` | Direct mapping |
| `Either[L, R]` | `Result<'R,'L>` | Either → Result (note order reversal) |
| `Try[T]` | `Result<'T, exn>` | Try → Result with exception |
| `List[T]` | `list<'T>` or `'T list` | Direct mapping (immutable) |
| `Vector[T]` | `array<'T>` or `ResizeArray<'T>` | Indexed collections |
| `Array[T]` | `'T []` or `array<'T>` | Arrays |
| `Future { ... }` | `async { ... }` | Future → async workflow |
| `for { x <- ... } yield ...` | `let! x = ... return ...` | For-comprehensions → computation expressions |
| `def method(): Unit` | `member _.Method() = ()` | Methods in classes/traits |
| `.method()` chaining | `\|>` pipe operator | Method chaining → piping |
| `andThen` | `>>` | Function composition |
| `@annotation` | `[<Attribute>]` | Annotations → attributes |
| `implicit val` | `let inline` or type providers | Implicits → inline or compile-time features |

## When Converting Code

1. **Analyze source thoroughly** before writing target - understand Scala idioms
2. **Map types first** - create type equivalence table for domain models
3. **Preserve semantics** over syntax similarity - embrace F#'s functional-first approach
4. **Adopt target idioms** - don't write "Scala code in F# syntax"
5. **Handle edge cases** - null safety, error paths, resource cleanup
6. **Test equivalence** - same inputs → same outputs
7. **Consider platform differences** - JVM stdlib → .NET BCL

---

## Type System Mapping

### Primitive Types

| Scala | F# | Notes |
|-------|-----|-------|
| `String` | `string` | Direct mapping |
| `Int` | `int` | 32-bit signed integer |
| `Long` | `int64` | 64-bit signed integer |
| `Double` | `float` or `double` | 64-bit floating point (F# `float` is `Double`) |
| `Float` | `float32` or `single` | 32-bit floating point |
| `Boolean` | `bool` | Direct mapping |
| `Char` | `char` | Direct mapping |
| `Byte` | `byte` | 8-bit (Scala: signed, F#: unsigned) |
| `Unit` | `unit` | Unit type |
| `Any` / `AnyRef` | `obj` | Base object type |
| `BigDecimal` | `decimal` | Arbitrary precision decimal |
| `BigInt` | `bigint` | Arbitrary precision integer |

**Note on Byte:** Scala `Byte` is signed (-128-127), F# `byte` is unsigned (0-255). Use `sbyte` in F# for signed semantics.

### Collection Types

| Scala | F# | Notes |
|-------|-----|-------|
| `List[T]` | `list<'T>` or `'T list` | Immutable linked list |
| `Vector[T]` | `array<'T>` or `'T []` | Immutable indexed (use F# array) |
| `Array[T]` | `'T []` or `array<'T>` | Mutable array |
| `LazyList[T]` | `seq<'T>` | Lazy evaluation |
| `Iterator[T]` | `seq<'T>` | One-time iteration |
| `Set[T]` | `Set<'T>` | Immutable set |
| `Map[K, V]` | `Map<'K,'V>` | Immutable map |
| `mutable.ListBuffer[T]` | `ResizeArray<'T>` | Mutable list |
| `(T, U)` | `'T * 'U` | Tuple syntax |
| `(T, U, V)` | `'T * 'U * 'V` | Multi-element tuple |

### Composite Types

| Scala Pattern | F# Pattern | Notes |
|---------------|------------|-------|
| `case class Person(name: String, age: Int)` | `type Person = { Name: string; Age: int }` | Case classes → records |
| `type UserId = Int` | `type UserId = int` | Type alias |
| `sealed trait Color; case object Red extends Color` | `type Color = Red \| Green \| Blue` | Sealed traits with objects → simple unions |
| `sealed trait Result[T]; case class Success[T](value: T) extends Result[T]` | `type Result<'T> = Success of 'T \| Failure of string` | Sealed traits → discriminated unions |
| `Option[T]` | `Option<'T>` | Built-in in both |
| `case class EmailAddress(value: String) extends AnyVal` | `type EmailAddress = EmailAddress of string` | Value classes → single-case unions |
| `trait Logger` | `type ILogger = abstract member Log : string -> unit` | Traits → interfaces |
| `trait Logger { def log(message: String): Unit }` | `type ILogger = abstract member Log : string -> unit` | Abstract members |

### Generic Type Mappings

| Scala | F# | Notes |
|-------|-----|-------|
| `T` or `A` | `'T` | Generic type parameter |
| `List[T]` | `list<'T>` | Generic collections |
| `T: Ordering` | `'T when 'T : comparison` | Constrained generics |
| `T <: BaseType` | `'T when 'T :> BaseType` | Upper bound |
| Type classes via implicits | SRTP or type providers | Static member constraints |

---

## Idiom Translation

### Pattern 1: Case Classes to Records

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

**Why this translation:**
- F# records provide automatic structural equality, copy-and-update
- F# uses PascalCase for field names (Scala uses camelCase)
- Copy-and-update syntax similar: `copy` in Scala, `with` in F#
- String interpolation: Scala uses `s""`, F# uses `$""`
- F# records are more lightweight than case classes

### Pattern 2: Sealed Traits to Discriminated Unions

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

**Why this translation:**
- F# discriminated unions are more concise than sealed traits
- F# case constructors can have named fields for clarity
- Pattern matching syntax similar but F# more lightweight
- Both enforce exhaustiveness checking
- F# unions are a first-class language feature vs Scala's trait + case class pattern

### Pattern 3: Option Type Handling

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

**Why this translation:**
- Both have built-in Option types with Some/None
- Scala `.map` → F# `Option.map` (module function)
- Scala `.getOrElse` → F# `Option.defaultValue`
- Scala method chaining → F# pipe operator `|>`
- Pattern matching syntax nearly identical
- F# uses `=` for equality (not `==`)

### Pattern 4: Either/Try to Result

**Scala:**
```scala
// Using Either (right-biased)
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

// Or with computation expression (requires custom builder)
let workflow2 = result {
    let! x = divide 10 2
    let! y = divide x 5
    return y * 2
}
```

**Why this translation:**
- Scala Either → F# Result type (note: error on left, success on right)
- Scala `Left` → F# `Error`, Scala `Right` → F# `Ok`
- Scala `.flatMap` → F# `Result.bind`
- Scala `.map` → F# `Result.map`
- F# computation expressions replace for-comprehensions
- Scala for-comprehensions work with any monad, F# needs custom builders

### Pattern 5: Futures to Async Workflows

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

**Why this translation:**
- Scala `Future { }` → F# `async { }`
- Scala implicit execution context → F# async built-in
- Scala `Thread.sleep` → F# `Async.Sleep` (non-blocking)
- Scala `Future.sequence` → F# `Async.Parallel`
- Scala `Await.result` → F# `Async.RunSynchronously`
- F# async is more lightweight and built into the language
- F# async uses cooperative cancellation via CancellationToken

### Pattern 6: For-Comprehensions to Computation Expressions

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

**F#:**
```fsharp
// Option computation expression (requires option {} builder or direct pattern matching)
let validateAge age =
    if age >= 0 && age <= 120 then Some age
    else None

let validateName name =
    if String.IsNullOrWhiteSpace(name) then None
    else Some name

// Using explicit bind/map
let createPerson name age =
    validateName name
    |> Option.bind (fun validName ->
        validateAge age
        |> Option.map (fun validAge ->
            { FirstName = validName; LastName = ""; Age = validAge }))

// Or with option computation expression (if defined)
let createPerson' name age = option {
    let! validName = validateName name
    let! validAge = validateAge age
    return { FirstName = validName; LastName = ""; Age = validAge }
}
```

**Why this translation:**
- Scala for-comprehensions → F# computation expressions (when builder exists)
- Scala `<-` → F# `let!` (bind/flatMap)
- Scala `yield` → F# `return` (map)
- Both desugar to bind/map chains
- F# requires explicit computation expression builders (not always built-in)
- F# pipe operator often preferred over comprehensions for simple cases

### Pattern 7: Pattern Matching with Guards

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

**F#:**
```fsharp
let classify n =
    match n with
    | x when x < 0 -> "negative"
    | 0 -> "zero"
    | x when x % 2 = 0 -> "even positive"
    | _ -> "odd positive"

// List pattern matching
let rec sumFirst list =
    match list with
    | [] -> 0
    | [x] -> x
    | x :: xs -> x + sumFirst xs
```

**Why this translation:**
- Both use `when` for guards (F#) and `if` for guards (Scala)
- Scala `Nil` → F# `[]`
- Scala `x :: xs` → F# `x :: xs` (same cons operator)
- Both support deep pattern matching
- F# requires `rec` keyword for recursive functions
- F# uses `=` for equality, Scala uses `==`

### Pattern 8: Custom Extractors to Active Patterns

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

**Why this translation:**
- Scala custom extractors (`unapply`) → F# active patterns
- Scala objects with `unapply` → F# parameterless active patterns
- Scala partial `unapply` returning `Option` → F# partial active patterns `(|X|_|)`
- F# active patterns are more concise and first-class
- F# syntax `(|Pattern|)` for complete, `(|Pattern|_|)` for partial
- Both enable extensible pattern matching

### Pattern 9: Opaque Types / Value Classes to Units of Measure or Single-Case Unions

**Scala (Value Classes):**
```scala
// Value classes (zero runtime overhead)
case class Kilograms(value: Double) extends AnyVal
case class Meters(value: Double) extends AnyVal
case class Seconds(value: Double) extends AnyVal

val distance = Meters(100.0)
val time = Seconds(10.0)
// No compile-time prevention of mixing units
```

**Scala 3 (Opaque Types):**
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

**F# (Units of Measure):**
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

**F# (Single-Case Unions - alternative):**
```fsharp
type Kilograms = Kilograms of float
type Meters = Meters of float
type Seconds = Seconds of float

let distance = Meters 100.0
let time = Seconds 10.0
// Type-safe but requires unwrapping
```

**Why this translation:**
- Scala value classes → F# single-case unions (zero overhead with `[<Struct>]`)
- Scala 3 opaque types → F# units of measure (F# is more powerful)
- F# units of measure provide compile-time dimensional analysis
- F# units disappear at runtime (zero overhead)
- For domain types without arithmetic, use single-case unions
- F# has better type safety for numeric units

### Pattern 10: Implicits to Inline Functions or Type Providers

**Scala (Implicit Parameters):**
```scala
trait Show[A] {
  def show(a: A): String
}

object Show {
  implicit val intShow: Show[Int] = (i: Int) => i.toString
  implicit val stringShow: Show[String] = (s: String) => s"\"$s\""
}

def display[A](value: A)(implicit shower: Show[A]): String = {
  shower.show(value)
}

display(42)        // Uses intShow
display("hello")   // Uses stringShow
```

**F# (Inline with Static Member Constraints - SRTP):**
```fsharp
// Using inline and static member constraints
type Show =
    static member inline Show(x: int) = x.ToString()
    static member inline Show(x: string) = $"\"{x}\""

let inline display x =
    (^T : (static member Show : ^T -> string) x)

display 42        // Uses Show(int)
display "hello"   // Uses Show(string)

// Or use explicit type class pattern with inline
type IShow<'T> =
    abstract member Show : 'T -> string

let inline show (shower: ^S when ^S :> IShow< ^T>) (value: ^T) =
    shower.Show(value)
```

**Why this translation:**
- Scala implicits → F# inline functions with static member constraints (SRTP)
- F# SRTP resolved at compile-time (similar to Scala implicits)
- F# inline more explicit than Scala's implicit resolution
- Type providers can also fill similar roles for compile-time code generation
- F# doesn't have implicit parameter passing, requires explicit passing or SRTP
- For simple cases, explicit dictionary passing is more idiomatic in F#

---

## Paradigm Translation

### Mental Model Shift: JVM Functional/OOP Hybrid → .NET Functional-First

| Scala Concept | F# Approach | Key Insight |
|---------------|-------------|-------------|
| Case class | Record type | Data structures are lightweight records |
| Sealed trait | Discriminated union | Algebraic data types are first-class |
| Trait with implementation | Module with functions | Behavior in modules, not objects |
| Implicit parameters | Inline or explicit passing | Explicitness over magic |
| For-comprehension | Computation expression | Custom builders required |
| Companion object | Module with same name | Modules replace objects |
| Method chaining `.method()` | Pipe operator `\|>` | Data flows left-to-right |

### Concurrency Mental Model

| Scala Model | F# Model | Conceptual Translation |
|-------------|----------|------------------------|
| Future + ExecutionContext | Async workflow | Futures → async (built-in, lightweight) |
| Akka actors | MailboxProcessor | Actors → lightweight agents |
| Parallel collections | Async.Parallel | Parallel operations → async composition |
| Cats Effect IO | Async or task expressions | Effect systems → async workflows |

---

## Error Handling

### Scala Error Model → F# Error Model

| Scala | F# | Migration Strategy |
|-------|-----|-------------------|
| `Option[T]` | `Option<'T>` | Direct mapping, same semantics |
| `Either[L, R]` | `Result<'R,'L>` | Map Left→Error, Right→Ok (note order) |
| `Try[T]` | `Result<'T, exn>` | Success→Ok, Failure→Error with exception |
| Exception throwing | `Result` or `Option` | Replace exceptions with Result type |
| `.getOrElse` | `Option.defaultValue` | Safe default value extraction |
| `.flatMap` | `Result.bind` or `Option.bind` | Monadic composition |
| `.map` | `Result.map` or `Option.map` | Functor mapping |

**Example: Exception to Result**

**Scala:**
```scala
def parseInt(s: String): Try[Int] = Try(s.toInt)

val result: Try[Int] = parseInt("42")
result match {
  case Success(n) => println(s"Parsed: $n")
  case Failure(ex) => println(s"Error: ${ex.getMessage}")
}
```

**F#:**
```fsharp
let parseInt (s: string) : Result<int, exn> =
    try
        Ok (System.Int32.Parse(s))
    with
    | ex -> Error ex

let result = parseInt "42"
match result with
| Ok n -> printfn $"Parsed: {n}"
| Error ex -> printfn $"Error: {ex.Message}"
```

---

## Concurrency Patterns

### Scala Async → F# Async

| Scala Pattern | F# Pattern | Notes |
|---------------|------------|-------|
| `Future { block }` | `async { block }` | Deferred computation |
| `Await.result(future, duration)` | `Async.RunSynchronously(async)` | Blocking wait |
| `Future.sequence(list)` | `Async.Parallel(array)` then `Array.toList` | Sequential composition |
| `Future.successful(value)` | `async.Return(value)` | Wrap value in async |
| `future.map(f)` | `async { let! x = ... return f x }` | Map over async |
| `future.flatMap(f)` | `async { let! x = ... return! f x }` | Bind async operations |
| `ExecutionContext` | Built-in thread pool | F# async uses default scheduler |

**Example: Parallel HTTP Requests**

**Scala:**
```scala
import scala.concurrent._
import scala.concurrent.duration._
import ExecutionContext.Implicits.global

def fetchUrl(url: String): Future[String] = Future {
  // HTTP request
  s"Content from $url"
}

val urls = List("url1", "url2", "url3")
val futures = urls.map(fetchUrl)
val combined: Future[List[String]] = Future.sequence(futures)

val results = Await.result(combined, 10.seconds)
```

**F#:**
```fsharp
let fetchUrl url = async {
    // HTTP request
    return $"Content from {url}"
}

let urls = ["url1"; "url2"; "url3"]
let asyncOps = urls |> List.map fetchUrl |> List.toArray
let combined = Async.Parallel asyncOps

let results = combined |> Async.RunSynchronously |> Array.toList
```

---

## Memory & Ownership

### JVM GC → .NET GC with Functional Emphasis

Both Scala and F# run on garbage-collected platforms (JVM and .NET respectively), so memory management is mostly similar. However, there are some differences:

| Aspect | Scala (JVM) | F# (.NET) | Translation Notes |
|--------|-------------|-----------|-------------------|
| Memory model | JVM heap + stack | CLR heap + stack | Similar GC-based model |
| Value types | AnyVal (limited) | Struct types | F# structs more flexible |
| Immutability | Encouraged, not enforced | Encouraged, not enforced | Both support immutable collections |
| Resource cleanup | try-with-resources | `use` binding / `using` | F# `use` for IDisposable |
| Lazy evaluation | `lazy val` | `lazy` keyword | Similar lazy evaluation |

**Resource Management Example**

**Scala:**
```scala
import scala.util.Using

Using(scala.io.Source.fromFile("file.txt")) { source =>
  source.getLines().foreach(println)
}
```

**F#:**
```fsharp
use file = System.IO.File.OpenText("file.txt")
while not file.EndOfStream do
    printfn "%s" (file.ReadLine())
// file automatically disposed at end of scope
```

---

## Common Pitfalls

1. **Naming Conventions**: Scala uses camelCase, F# uses PascalCase for types and members
   - Scala: `case class userAccount(userId: Int)`
   - F#: `type UserAccount = { UserId: int }`

2. **Equality Operators**: Scala uses `==` and `!=`, F# uses `=` and `<>`
   - Scala: `if (x == 0)`
   - F#: `if x = 0`

3. **Method vs Function Syntax**: Scala prefers methods on objects, F# prefers module functions
   - Scala: `list.map(f).filter(p)`
   - F#: `list |> List.map f |> List.filter p`

4. **For-Comprehension vs Computation Expression**: Scala's for works with any monad, F# requires custom builders
   - Don't assume all types have computation expressions in F#
   - Use explicit bind/map or define custom builders

5. **Implicit Resolution**: Scala's implicits don't translate directly
   - F# requires explicit passing or inline SRTP
   - Consider using modules for organizing instances

6. **Variance Annotations**: Scala has `+T` (covariant) and `-T` (contravariant), F# has limited variance
   - F# arrays are not covariant (unlike Scala)
   - Use interfaces for covariance where needed

7. **Pattern Matching Exhaustiveness**: Both check exhaustiveness, but differently
   - Scala checks sealed traits
   - F# checks discriminated unions
   - Both warn on incomplete matches

8. **Tuple Access**: Different syntax for accessing tuple elements
   - Scala: `tuple._1`, `tuple._2`
   - F#: `fst tuple`, `snd tuple` (for pairs), or pattern match `let (a, b, c) = tuple`

9. **Unit Type**: Both have Unit, but syntax differs
   - Scala: `def method(): Unit = ()`
   - F#: `let method () = ()` or `member _.Method() = ()`

10. **Mutable vs Immutable Default**: Both default to immutable, but syntax differs
    - Scala: `var` (mutable) vs `val` (immutable)
    - F#: `mutable` annotation required for mutable fields in records

---

## Tooling

| Tool | Purpose | Notes |
|------|---------|-------|
| **Ionide** | F# IDE support (VS Code) | Primary F# development environment |
| **Rider** | JetBrains IDE | Supports both Scala and F# |
| **dotnet CLI** | Build and run F# | F# standard build tool |
| **Paket** | Dependency management | Alternative to NuGet |
| **FAKE** | Build automation | F# Make, similar to SBT |
| **Expecto** | Testing framework | F#-friendly testing |
| **FsCheck** | Property-based testing | F# equivalent of ScalaCheck |
| **Fantomas** | Code formatter | F# equivalent of Scalafmt |

---

## Examples

### Example 1: Simple - Option Handling

**Before (Scala):**
```scala
case class User(id: Int, name: String)

def findUser(id: Int): Option[User] = {
  if (id == 1) Some(User(1, "Alice"))
  else None
}

val userName = findUser(1)
  .map(_.name)
  .getOrElse("Unknown")

println(userName)  // Alice
```

**After (F#):**
```fsharp
type User = { Id: int; Name: string }

let findUser id =
    if id = 1 then Some { Id = 1; Name = "Alice" }
    else None

let userName =
    findUser 1
    |> Option.map (fun u -> u.Name)
    |> Option.defaultValue "Unknown"

printfn "%s" userName  // Alice
```

### Example 2: Medium - Discriminated Union with Pattern Matching

**Before (Scala):**
```scala
sealed trait Response[+T]
case class Success[T](data: T) extends Response[T]
case class Failure(error: String) extends Response[Nothing]
case object Loading extends Response[Nothing]

def handleResponse[T](response: Response[T]): String = response match {
  case Success(data) => s"Got data: $data"
  case Failure(error) => s"Error: $error"
  case Loading => "Loading..."
}

val response: Response[Int] = Success(42)
println(handleResponse(response))  // Got data: 42
```

**After (F#):**
```fsharp
type Response<'T> =
    | Success of data: 'T
    | Failure of error: string
    | Loading

let handleResponse response =
    match response with
    | Success data -> $"Got data: {data}"
    | Failure error -> $"Error: {error}"
    | Loading -> "Loading..."

let response = Success 42
printfn "%s" (handleResponse response)  // Got data: 42
```

### Example 3: Complex - Async Pipeline with Error Handling

**Before (Scala):**
```scala
import scala.concurrent._
import scala.concurrent.duration._
import ExecutionContext.Implicits.global
import scala.util.{Try, Success, Failure}

case class User(id: Int, name: String, email: String)
case class Profile(userId: Int, bio: String)

def fetchUser(id: Int): Future[Either[String, User]] = Future {
  if (id > 0) Right(User(id, "Alice", "alice@example.com"))
  else Left("Invalid ID")
}

def fetchProfile(userId: Int): Future[Either[String, Profile]] = Future {
  Right(Profile(userId, "Software developer"))
}

def getUserProfile(id: Int): Future[Either[String, (User, Profile)]] = {
  val result = for {
    user <- fetchUser(id)
    profile <- fetchProfile(user.id)
  } yield (user, profile)

  result.map {
    case Right((u, p)) => Right((u, p))
    case Left(err) => Left(err)
  }
}

// Note: Scala Either is right-biased, so for-comprehension works
val workflow: Future[Either[String, String]] = for {
  userProfile <- getUserProfile(1)
} yield userProfile match {
  case Right((user, profile)) => s"${user.name}: ${profile.bio}"
  case Left(error) => s"Error: $error"
}

val result = Await.result(workflow, 5.seconds)
println(result)
```

**After (F#):**
```fsharp
type User = { Id: int; Name: string; Email: string }
type Profile = { UserId: int; Bio: string }

let fetchUser id = async {
    return
        if id > 0 then Ok { Id = id; Name = "Alice"; Email = "alice@example.com" }
        else Error "Invalid ID"
}

let fetchProfile userId = async {
    return Ok { UserId = userId; Bio = "Software developer" }
}

let getUserProfile id = async {
    let! userResult = fetchUser id
    match userResult with
    | Ok user ->
        let! profileResult = fetchProfile user.Id
        match profileResult with
        | Ok profile -> return Ok (user, profile)
        | Error err -> return Error err
    | Error err -> return Error err
}

// Or with a result computation expression builder
let getUserProfile' id = async {
    let! userResult = fetchUser id
    let! profileResult =
        match userResult with
        | Ok user -> fetchProfile user.Id
        | Error err -> async { return Error err }

    return
        match userResult, profileResult with
        | Ok user, Ok profile -> Ok (user, profile)
        | Error err, _ -> Error err
        | _, Error err -> Error err
}

let workflow = async {
    let! userProfile = getUserProfile 1
    return
        match userProfile with
        | Ok (user, profile) -> $"{user.Name}: {profile.Bio}"
        | Error error -> $"Error: {error}"
}

let result = workflow |> Async.RunSynchronously
printfn "%s" result
```

---

## See Also

For more examples and patterns, see:
- `meta-convert-dev` - Foundational patterns with cross-language examples
- `convert-fsharp-scala` - Reverse conversion (F# → Scala)
- `lang-scala-dev` - Scala development patterns
- `lang-fsharp-dev` - F# development patterns

Cross-cutting pattern skills:
- `patterns-concurrency-dev` - Async, parallel processing across languages
- `patterns-serialization-dev` - JSON, validation across languages
- `patterns-metaprogramming-dev` - Code generation, macros across languages
