# Scala

> Multi-paradigm language combining object-oriented and functional programming on the JVM.

## Overview

Scala is a general-purpose programming language created by Martin Odersky, first released in 2004. It combines object-oriented and functional programming paradigms in a statically typed language that runs on the JVM and JavaScript runtimes.

Scala 3 (formerly Dotty) represents a significant evolution, introducing a new type system foundation (DOT calculus), simplified syntax, and improved metaprogramming through inline and macros. The language emphasizes expressiveness and type safety while maintaining Java interoperability.

The language is particularly strong in distributed systems (Akka), big data (Spark), and backend services, with a rich ecosystem of functional programming libraries (Cats, ZIO).

## Family Classification

| Dimension | Classification | Notes |
|-----------|----------------|-------|
| Primary Family | ML-FP | Type inference, ADTs, pattern matching |
| Secondary Family | OOP | Full object orientation, traits |
| Subtype | hybrid | Multi-paradigm by design |

See: [ML-FP Family](../language-families/ml-fp.md)

## Version History

| Version | Release | Key Changes for Conversion |
|---------|---------|---------------------------|
| 2.11 | 2014-04 | Macro paradise, SI-8 fixes |
| 2.12 | 2016-11 | Java 8 lambdas, trait encoding |
| 2.13 | 2019-06 | New collections, literal types |
| 3.0 | 2021-05 | Given/using, enums, union types, export |
| 3.3 LTS | 2023-05 | First LTS release, async/await (experimental) |

## Feature Profile

### Type System

- **Strength:** strong (static, sound)
- **Inference:** bidirectional (Hindley-Milner based, local type inference)
- **Generics:** bounded (variance annotations, type bounds)
- **Nullability:** nullable (Option[T] by convention, explicit null in Scala 3)

### Memory Model

- **Management:** gc (JVM garbage collection)
- **Mutability:** default-immutable (val preferred, var available)
- **Allocation:** heap (JVM semantics)

### Control Flow

- **Structured:** if-else, for-comprehensions, while, try-catch, match
- **Effects:** exceptions (Try, Either for functional), effects systems (ZIO, Cats Effect)
- **Async:** Futures, async/await (experimental), effect systems

### Data Types

- **Primitives:** Int, Long, Float, Double, Boolean, Char, Byte, Short, Unit
- **Composites:** case classes, sealed traits, tuples, enums (Scala 3)
- **Collections:** List, Vector, Set, Map, Seq, immutable by default
- **Abstraction:** traits, abstract classes, objects, packages

### Metaprogramming

- **Macros:** compile-time (inline, macros in Scala 3)
- **Reflection:** runtime (scala.reflect), compile-time (TASTy)
- **Code generation:** inline, derives (type class derivation)

## Ecosystem

| Tool | Name | Notes |
|------|------|-------|
| Package Manager | sbt, Mill, Maven, Gradle | sbt is standard |
| Build System | sbt, Mill | Mill is simpler |
| LSP | Metals | Excellent IDE support |
| Formatter | scalafmt | Highly configurable |
| Linter | scalafix, Wartremover | scalafix for refactoring |
| REPL | scala, Ammonite | Ammonite enhanced |
| Test Framework | ScalaTest, MUnit, specs2 | MUnit is modern |

## Syntax Patterns

```scala
// Function definition
def greet(name: String, times: Int = 1): String =
  s"Hello, $name! " * times

// Generic function
def identity[T](value: T): T = value

// Async function (Scala 3 / Future)
def fetchData(url: String): Future[Response] =
  Http.get(url).map { response =>
    if response.status != 200 then
      throw HttpError(response.status)
    response
  }

// Case class (ADT)
case class User(
  id: String,
  name: String,
  email: Option[String] = None
)

// Sealed trait (sum type)
sealed trait Result[+T, +E]
case class Ok[T](value: T) extends Result[T, Nothing]
case class Err[E](error: E) extends Result[Nothing, E]

// Scala 3 enum
enum Shape:
  case Circle(radius: Double)
  case Rectangle(width: Double, height: Double)

def area(shape: Shape): Double = shape match
  case Shape.Circle(r) => Math.PI * r * r
  case Shape.Rectangle(w, h) => w * h

// Trait with type class pattern
trait Show[T]:
  extension (t: T) def show: String

given Show[Int] with
  extension (i: Int) def show: String = i.toString

// For-comprehension
val users: List[User] = ???
val emails: List[String] = for
  user <- users
  email <- user.email
yield email

// Error handling with Either
def divide(a: Int, b: Int): Either[String, Int] =
  if b == 0 then Left("Division by zero")
  else Right(a / b)

// Higher-order functions
val numbers = List(1, 2, 3, 4, 5)
val doubled = numbers.map(_ * 2)
val evens = numbers.filter(_ % 2 == 0)
val sum = numbers.foldLeft(0)(_ + _)
```

## Semantic Gaps

| Gap | Severity | Workaround |
|-----|----------|------------|
| Null exists despite Option | moderate | Enable strict null checking, avoid null |
| Implicit complexity (Scala 2) | moderate | Migrate to given/using (Scala 3) |
| JVM startup time | minor | GraalVM native-image, Scala Native |
| Two-paradigm tension | minor | Choose FP-first or OOP-first style |
| Scala 2 vs 3 migration | moderate | Use Scala 3 cross-building, scalafix |

## Convert-* Coverage

| Direction | Count | Skills |
|-----------|-------|--------|
| As Source | 0 | — |
| As Target | 8 | python-scala, elixir-scala, clojure-scala, elm-scala, erlang-scala, fsharp-scala, haskell-scala, roc-scala |

**Note:** Most common target language - receives conversions from all major FP languages.

## Idiomatic Patterns

### Case Classes → Records/Structs

```scala
// Scala: case class with copy
case class Point(x: Int, y: Int)
val p2 = p1.copy(x = 10)

// IR equivalent: record with named update
// Point { x: 10, ..p1 }
```

### For-Comprehensions → Monadic Composition

```scala
// Scala: for-comprehension
for
  x <- getX
  y <- getY(x)
yield combine(x, y)

// IR equivalent: flatMap/map chain
// getX.flatMap(x => getY(x).map(y => combine(x, y)))
```

### Given/Using → Type Classes

```scala
// Scala 3: given instance
given Ordering[User] with
  def compare(a: User, b: User) = a.name.compare(b.name)

// IR equivalent: type class instance
// impl Ordering for User { ... }
```

## Related Languages

- **Influenced by:** Java, ML, Haskell, Erlang, Smalltalk
- **Influenced:** Kotlin, Ceylon, Dotty
- **Compiles to:** JVM bytecode, JavaScript (Scala.js), Native (Scala Native)
- **FFI compatible:** Java (native), JavaScript (Scala.js)

## Sources

- [Scala 3 Documentation](https://docs.scala-lang.org/scala3/)
- [Scala 3 Reference](https://docs.scala-lang.org/scala3/reference/)
- [Scala 2.13 Specification](https://www.scala-lang.org/files/archive/spec/2.13/)
- [Scala Tour](https://docs.scala-lang.org/tour/tour-of-scala.html)

## See Also

- [ML-FP Family](../language-families/ml-fp.md)
- [Haskell](haskell.md) - Pure FP comparison
- [Kotlin](kotlin.md) - JVM alternative
- [Java](java.md) - Interop target
