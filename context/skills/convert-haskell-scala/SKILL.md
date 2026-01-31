---
name: convert-haskell-scala
description: Convert Haskell code to idiomatic Scala. Use when migrating Haskell projects to Scala, translating Haskell patterns to idiomatic Scala, or refactoring Haskell codebases. Extends meta-convert-dev with Haskell-to-Scala specific patterns.
---

# Convert Haskell to Scala

Convert Haskell code to idiomatic Scala. This skill extends `meta-convert-dev` with Haskell-to-Scala specific type mappings, idiom translations, and tooling.

## This Skill Extends

- `meta-convert-dev` - Foundational conversion patterns (APTV workflow, testing strategies)

For general concepts like the Analyze → Plan → Transform → Validate workflow, testing strategies, and common pitfalls, see the meta-skill first.

## This Skill Adds

- **Type mappings**: Haskell types → Scala types
- **Idiom translations**: Haskell patterns → idiomatic Scala
- **Error handling**: Haskell Maybe/Either → Scala Option/Either
- **Async patterns**: Haskell IO/Async → Scala Future/IO
- **Lazy evaluation**: Haskell lazy by default → Scala strict with lazy vals
- **Type classes**: Haskell type classes → Scala implicits/given

## This Skill Does NOT Cover

- General conversion methodology - see `meta-convert-dev`
- Haskell language fundamentals - see `lang-haskell-dev`
- Scala language fundamentals - see `lang-scala-dev`
- Reverse conversion (Scala → Haskell) - see `convert-scala-haskell`

---

## Quick Reference

| Haskell | Scala | Notes |
|---------|-------|-------|
| `String` | `String` | Both are immutable strings |
| `Int` | `Int` | 32-bit integers |
| `Integer` | `BigInt` | Arbitrary precision |
| `Double` | `Double` | Floating point |
| `Bool` | `Boolean` | Boolean values |
| `[a]` | `List[A]` | Linked list |
| `(a, b)` | `(A, B)` | Tuple |
| `Maybe a` | `Option[A]` | Nullable values |
| `Either a b` | `Either[A, B]` | Sum type for errors |
| `IO a` | `IO[A]` (Cats Effect) | Side effects |
| `data` | `case class` / `sealed trait` | ADTs |
| `class` (type class) | `trait` + `implicit`/`given` | Type classes |
| `->` (function type) | `=>` (function type) | Function types |
| `Monad` | `Monad` (Cats) | Requires Cats library |

## When Converting Code

1. **Analyze source thoroughly** before writing target
2. **Map types first** - create type equivalence table
3. **Preserve semantics** over syntax similarity
4. **Adopt Scala idioms** - don't write "Haskell code in Scala syntax"
5. **Handle edge cases** - lazy evaluation, null safety, JVM interop
6. **Test equivalence** - same inputs → same outputs

---

## Type System Mapping

### Primitive Types

| Haskell | Scala | Notes |
|---------|-------|-------|
| `Int` | `Int` | 32-bit signed integer |
| `Integer` | `BigInt` | Arbitrary precision integer |
| `Double` | `Double` | 64-bit floating point |
| `Float` | `Float` | 32-bit floating point |
| `Bool` | `Boolean` | Boolean type |
| `Char` | `Char` | Single character |
| `String` | `String` | Immutable string |
| `()` | `Unit` | Unit type (void) |

### Collection Types

| Haskell | Scala | Notes |
|---------|-------|-------|
| `[a]` | `List[A]` | Immutable linked list |
| `(a, b)` | `(A, B)` | Tuple (up to 22 elements in Scala) |
| `(a, b, c)` | `(A, B, C)` | 3-tuple |
| `Map k v` | `Map[K, V]` | Immutable map |
| `Set a` | `Set[A]` | Immutable set |
| `Vector a` | `Vector[A]` | Indexed sequence |
| `Seq a` | `Seq[A]` | Generic sequence |

### Composite Types

| Haskell | Scala | Notes |
|---------|-------|-------|
| `data X = A \| B` | `sealed trait X; case object A extends X; case object B extends X` | Sum types |
| `data X = X { field :: Type }` | `case class X(field: Type)` | Product types with named fields |
| `newtype X = X Type` | `case class X(value: Type) extends AnyVal` | Zero-cost wrapper |
| `type X = Y` | `type X = Y` | Type alias |
| `Maybe a` | `Option[A]` | Optional values |
| `Either a b` | `Either[A, B]` | Sum type (Left is error by convention in both) |

### Function Types

| Haskell | Scala | Notes |
|---------|-------|-------|
| `a -> b` | `A => B` | Function from A to B |
| `a -> b -> c` | `A => B => C` or `(A, B) => C` | Curried vs uncurried |
| `IO a` | `IO[A]` (Cats Effect) | Effectful computation |
| `Monad m => m a` | `F[A]` (with Monad[F]) | Higher-kinded types |

---

## Idiom Translation

### Pattern 1: Maybe/Option Handling

**Haskell:**
```haskell
findUser :: String -> Maybe User
findUser userId = lookup userId users

-- Pattern matching
case findUser "123" of
  Just user -> processUser user
  Nothing -> putStrLn "User not found"

-- Maybe functions
fromMaybe defaultUser (findUser "123")
maybe "No user" userName (findUser "123")
```

**Scala:**
```scala
def findUser(userId: String): Option[User] =
  users.get(userId)

// Pattern matching
findUser("123") match {
  case Some(user) => processUser(user)
  case None => println("User not found")
}

// Option methods
findUser("123").getOrElse(defaultUser)
findUser("123").map(_.name).getOrElse("No user")
```

**Why this translation:**
- `Maybe` and `Option` are semantically equivalent
- Both use pattern matching for explicit handling
- Scala's `.getOrElse` is more concise than `fromMaybe`
- Method chaining is idiomatic in Scala

### Pattern 2: Either for Error Handling

**Haskell:**
```haskell
data AppError = NotFound | ValidationError String

parseAge :: String -> Either AppError Int
parseAge str =
  case reads str of
    [(n, "")] -> if n >= 0
                 then Right n
                 else Left (ValidationError "Age must be positive")
    _ -> Left (ValidationError "Not a valid number")

-- Chaining with do-notation
validateUser :: String -> String -> Either AppError User
validateUser ageStr emailStr = do
  age <- parseAge ageStr
  email <- validateEmail emailStr
  return $ User email age
```

**Scala:**
```scala
sealed trait AppError
case object NotFound extends AppError
case class ValidationError(message: String) extends AppError

def parseAge(str: String): Either[AppError, Int] = {
  str.toIntOption match {
    case Some(n) if n >= 0 => Right(n)
    case Some(_) => Left(ValidationError("Age must be positive"))
    case None => Left(ValidationError("Not a valid number"))
  }
}

// Chaining with for-comprehension
def validateUser(ageStr: String, emailStr: String): Either[AppError, User] = {
  for {
    age <- parseAge(ageStr)
    email <- validateEmail(emailStr)
  } yield User(email, age)
}
```

**Why this translation:**
- Both use Either with Left for errors, Right for success
- Haskell's `do-notation` maps to Scala's `for-comprehension`
- ADT error types work similarly in both languages
- Scala requires explicit `yield` at the end of for-comprehension

### Pattern 3: List Comprehensions

**Haskell:**
```haskell
-- List comprehension
squares = [x^2 | x <- [1..10], even x]

-- With multiple generators
pairs = [(x, y) | x <- [1..3], y <- [1..3], x < y]

-- Nested comprehensions
matrix = [[1..n] | n <- [1..5]]
```

**Scala:**
```scala
// For-comprehension
val squares = for {
  x <- 1 to 10
  if x % 2 == 0
} yield x * x

// With multiple generators
val pairs = for {
  x <- 1 to 3
  y <- 1 to 3
  if x < y
} yield (x, y)

// Using map/filter (more idiomatic for simple cases)
val squares = (1 to 10).filter(_ % 2 == 0).map(x => x * x)

// Nested
val matrix = (1 to 5).map(n => (1 to n).toList)
```

**Why this translation:**
- Both desugar to map/flatMap/filter
- Scala's for-comprehension requires `yield` keyword
- Guards (filters) use `if` in both
- Scala often prefers method chaining for simple transformations

### Pattern 4: Pattern Matching on ADTs

**Haskell:**
```haskell
data Shape = Circle Double
           | Rectangle Double Double
           | Triangle Double Double Double

area :: Shape -> Double
area (Circle r) = pi * r^2
area (Rectangle w h) = w * h
area (Triangle b h _) = 0.5 * b * h

-- Guards
classify :: Int -> String
classify n
  | n < 0 = "negative"
  | n == 0 = "zero"
  | otherwise = "positive"
```

**Scala:**
```scala
sealed trait Shape
case class Circle(radius: Double) extends Shape
case class Rectangle(width: Double, height: Double) extends Shape
case class Triangle(base: Double, height: Double, side: Double) extends Shape

def area(shape: Shape): Double = shape match {
  case Circle(r) => math.Pi * r * r
  case Rectangle(w, h) => w * h
  case Triangle(b, h, _) => 0.5 * b * h
}

// Guards
def classify(n: Int): String = n match {
  case n if n < 0 => "negative"
  case 0 => "zero"
  case _ => "positive"
}
```

**Why this translation:**
- Haskell uses data constructors, Scala uses case classes
- Pattern matching syntax is similar
- Guards use `if` in Scala match, `|` in Haskell function definitions
- `sealed trait` ensures exhaustiveness checking like Haskell

### Pattern 5: Type Classes to Implicits/Given

**Haskell:**
```haskell
class Show a where
  show :: a -> String

instance Show Int where
  show = Prelude.show

instance Show User where
  show (User name age) = name ++ " (" ++ Prelude.show age ++ ")"

printValue :: Show a => a -> IO ()
printValue x = putStrLn (show x)
```

**Scala 2 (implicits):**
```scala
trait Show[A] {
  def show(a: A): String
}

object Show {
  implicit val intShow: Show[Int] = new Show[Int] {
    def show(a: Int): String = a.toString
  }

  implicit val userShow: Show[User] = new Show[User] {
    def show(user: User): String = s"${user.name} (${user.age})"
  }
}

def printValue[A](x: A)(implicit s: Show[A]): Unit = {
  println(s.show(x))
}
```

**Scala 3 (given/using):**
```scala
trait Show[A] {
  def show(a: A): String
}

given Show[Int] with {
  def show(a: Int): String = a.toString
}

given Show[User] with {
  def show(user: User): String = s"${user.name} (${user.age})"
}

def printValue[A](x: A)(using s: Show[A]): Unit = {
  println(s.show(x))
}
```

**Why this translation:**
- Type classes map to traits with implicit/given instances
- Constraints become implicit/using parameters
- Scala 3 syntax is closer to Haskell's
- Both support type class derivation (Haskell with deriving, Scala with macros)

### Pattern 6: Lazy Evaluation

**Haskell:**
```haskell
-- Infinite lists (lazy by default)
naturals = [1..]
fibs = 0 : 1 : zipWith (+) fibs (tail fibs)

-- Take first 10
take 10 naturals
take 10 fibs

-- Lazy evaluation of expressions
expensiveComputation = trace "Computing..." (sum [1..1000000])
result = if condition then expensiveComputation else 0  -- Only computed if condition is True
```

**Scala:**
```scala
// LazyList (Stream in Scala 2.12)
val naturals = LazyList.from(1)
val fibs: LazyList[Int] = 0 #:: 1 #:: fibs.zip(fibs.tail).map { case (a, b) => a + b }

// Take first 10
naturals.take(10).toList
fibs.take(10).toList

// Lazy val for deferred evaluation
lazy val expensiveComputation = {
  println("Computing...")
  (1 to 1000000).sum
}
val result = if (condition) expensiveComputation else 0  // Only computed if condition is true

// By-name parameters for lazy arguments
def ifThenElse[A](cond: Boolean)(thenBranch: => A)(elseBranch: => A): A = {
  if (cond) thenBranch else elseBranch
}
```

**Why this translation:**
- Haskell is lazy by default, Scala is strict by default
- Use `LazyList` for infinite sequences
- Use `lazy val` for deferred computation
- By-name parameters (`=> A`) for lazy function arguments
- Scala 2.13+ renamed Stream to LazyList

### Pattern 7: Function Composition and Application

**Haskell:**
```haskell
-- Function composition
addThenDouble = (*2) . (+1)
process = filter even . map (*2) . filter (>0)

-- Function application
result = f $ g $ h x  -- Equivalent to f (g (h x))

-- Point-free style
sumOfSquares = sum . map (^2)
```

**Scala:**
```scala
// Function composition
val addThenDouble = ((x: Int) => x + 1) andThen (_ * 2)
val addThenDouble2 = ((x: Int) => x * 2) compose ((x: Int) => x + 1)

// Method chaining (more idiomatic)
def process(list: List[Int]): List[Int] =
  list.filter(_ > 0).map(_ * 2).filter(_ % 2 == 0)

// Infix notation for single-arg methods
val result = f(g(h(x)))  // No special operator needed

// Function style with compose
val sumOfSquares = ((list: List[Int]) => list.map(x => x * x)).andThen(_.sum)

// More idiomatic Scala
def sumOfSquares(list: List[Int]): Int = list.map(x => x * x).sum
```

**Why this translation:**
- Haskell's `.` maps to `compose` (right-to-left) or `andThen` (left-to-right)
- Scala prefers method chaining over function composition
- Haskell's `$` isn't needed in Scala (no precedence issues)
- Point-free style less common in Scala

### Pattern 8: Monadic Composition

**Haskell:**
```haskell
-- Do-notation
computation :: IO ()
computation = do
  putStrLn "What's your name?"
  name <- getLine
  putStrLn $ "Hello, " ++ name

-- Maybe monad
safeDivision :: Maybe Int
safeDivision = do
  a <- Just 10
  b <- Just 2
  result <- Just (div a b)
  return (result * 2)

-- List monad
pairs :: [(Int, Int)]
pairs = do
  x <- [1..3]
  y <- [1..3]
  guard (x < y)
  return (x, y)
```

**Scala:**
```scala
// For-comprehension with IO (Cats Effect)
import cats.effect.IO

val computation: IO[Unit] = for {
  _ <- IO.println("What's your name?")
  name <- IO.readLine
  _ <- IO.println(s"Hello, $name")
} yield ()

// Option monad
val safeDivision: Option[Int] = for {
  a <- Some(10)
  b <- Some(2)
  result <- Some(a / b)
} yield result * 2

// List monad
val pairs: List[(Int, Int)] = for {
  x <- (1 to 3).toList
  y <- (1 to 3).toList
  if x < y
} yield (x, y)
```

**Why this translation:**
- Haskell's `do-notation` maps directly to Scala's `for-comprehension`
- Both desugar to flatMap/map
- Haskell uses `return`, Scala uses `yield`
- `guard` becomes `if` in for-comprehension
- IO monad requires Cats Effect library in Scala

---

## Error Handling

### Haskell Maybe/Either → Scala Option/Either

| Haskell Pattern | Scala Equivalent | Notes |
|----------------|------------------|-------|
| `Nothing` | `None` | Absence of value |
| `Just x` | `Some(x)` | Present value |
| `Left err` | `Left(err)` | Error case |
| `Right val` | `Right(val)` | Success case |
| `fromMaybe default` | `.getOrElse(default)` | Provide default |
| `maybe defaultVal f` | `.map(f).getOrElse(defaultVal)` | Map with default |
| `either errorHandler successHandler` | `.fold(errorHandler, successHandler)` | Fold both cases |

### Exception Handling

**Haskell:**
```haskell
import Control.Exception

readFileSafe :: FilePath -> IO (Either IOException String)
readFileSafe path = try $ readFile path

-- Using try/catch
processFile :: FilePath -> IO ()
processFile path = do
  result <- try (readFile path) :: IO (Either IOException String)
  case result of
    Left ex -> putStrLn $ "Error: " ++ show ex
    Right content -> putStrLn content
```

**Scala:**
```scala
import scala.util.{Try, Success, Failure}
import java.io.IOException

def readFileSafe(path: String): Either[IOException, String] = {
  Try(scala.io.Source.fromFile(path).mkString).toEither match {
    case Right(content) => Right(content)
    case Left(ex: IOException) => Left(ex)
    case Left(ex) => Left(new IOException(ex))
  }
}

// Using Try
def processFile(path: String): Unit = {
  Try(scala.io.Source.fromFile(path).mkString) match {
    case Success(content) => println(content)
    case Failure(ex) => println(s"Error: ${ex.getMessage}")
  }
}
```

**Why this translation:**
- Haskell's `try` from Control.Exception maps to Scala's `Try`
- Both can convert to Either for type-safe error handling
- Scala has nullable types from Java, so be careful with interop
- Use Try for exception handling, Either for domain errors

---

## Concurrency Model

### Haskell IO/Async → Scala Future/IO

| Haskell | Scala | Library |
|---------|-------|---------|
| `IO a` | `Future[A]` | scala.concurrent |
| `IO a` | `IO[A]` | cats-effect |
| `async` | `Future { ... }` | scala.concurrent |
| `forkIO` | `Future { ... }` | scala.concurrent |
| `Async` | `Async[F]` | cats-effect |
| `concurrently` | `Future.sequence` | scala.concurrent |
| `race` | `Future.firstCompletedOf` | scala.concurrent |

### Basic Async Translation

**Haskell:**
```haskell
import Control.Concurrent.Async

fetchData :: IO String
fetchData = do
  threadDelay 1000000
  return "data"

main :: IO ()
main = do
  result <- fetchData
  putStrLn result

-- Concurrent execution
main :: IO ()
main = do
  (data1, data2) <- concurrently fetchData1 fetchData2
  putStrLn $ data1 ++ data2
```

**Scala:**
```scala
import scala.concurrent.{Future, Await}
import scala.concurrent.duration._
import scala.concurrent.ExecutionContext.Implicits.global

def fetchData: Future[String] = Future {
  Thread.sleep(1000)
  "data"
}

def main(): Unit = {
  val result = Await.result(fetchData, 5.seconds)
  println(result)
}

// Concurrent execution
def main(): Unit = {
  val combined = for {
    data1 <- fetchData1
    data2 <- fetchData2
  } yield data1 + data2

  println(Await.result(combined, 5.seconds))
}
```

**Why this translation:**
- Haskell's IO is pure, Scala's Future is eager
- Use Cats Effect IO for pure functional effects in Scala
- `concurrently` maps to for-comprehension with Futures
- Avoid `Await` in production; use callbacks or IO

### Software Transactional Memory

**Haskell:**
```haskell
import Control.Concurrent.STM

type Account = TVar Int

transfer :: Account -> Account -> Int -> STM ()
transfer from to amount = do
  fromBalance <- readTVar from
  when (fromBalance < amount) retry
  modifyTVar from (subtract amount)
  modifyTVar to (+ amount)

main :: IO ()
main = do
  account1 <- newTVarIO 1000
  account2 <- newTVarIO 0
  atomically $ transfer account1 account2 500
```

**Scala:**
```scala
import scala.concurrent.stm._

type Account = Ref[Int]

def transfer(from: Account, to: Account, amount: Int): Unit = {
  atomic { implicit txn =>
    val fromBalance = from()
    if (fromBalance < amount) retry
    from() = fromBalance - amount
    to() = to() + amount
  }
}

def main(): Unit = {
  val account1 = Ref(1000)
  val account2 = Ref(0)
  transfer(account1, account2, 500)
}
```

**Why this translation:**
- Both support STM with similar semantics
- Scala STM requires `scala-stm` library
- `atomic` block replaces `atomically`
- `retry` works the same way

---

## Memory Model

### Haskell Lazy Evaluation → Scala Strict Evaluation

| Concept | Haskell | Scala | Notes |
|---------|---------|-------|-------|
| Default evaluation | Lazy | Strict | Major difference |
| Force evaluation | `seq`, `deepseq` | N/A (already strict) | - |
| Defer evaluation | Default | `lazy val`, `LazyList` | Explicit in Scala |
| Infinite structures | `[1..]` | `LazyList.from(1)` | Requires LazyList |
| Thunks | Automatic | `=> A` (by-name) | Explicit in Scala |

### Space Leaks and Strictness

**Haskell:**
```haskell
-- Potential space leak (lazy accumulation)
badSum :: [Int] -> Int
badSum = foldl (+) 0  -- Builds up thunks

-- Strict version
goodSum :: [Int] -> Int
goodSum = foldl' (+) 0  -- Forces evaluation

-- Bang patterns
data Point = Point !Int !Int  -- Strict fields

-- Forcing evaluation
result = x `seq` y  -- Evaluate x, then return y
```

**Scala:**
```scala
// No space leak (strict by default)
def sum(list: List[Int]): Int =
  list.foldLeft(0)(_ + _)  // Always strict

// Lazy evaluation when needed
lazy val expensiveValue = {
  println("Computing...")
  1 + 1
}

// Strict fields by default
case class Point(x: Int, y: Int)  // Already strict

// All evaluation is forced by default
val result = {
  val _ = x  // x is evaluated
  y          // y is returned
}
```

**Why this matters:**
- Haskell's laziness can cause space leaks
- Scala doesn't have this problem by default
- Use `lazy val` sparingly in Scala
- LazyList for infinite structures

---

## Common Pitfalls

### 1. Assuming Lazy Evaluation

**Problem:** Expecting Scala to be lazy like Haskell.

**Example:**
```scala
// ❌ This will hang in Scala (strict evaluation)
val naturals = (1 to Int.MaxValue).toList  // Tries to build entire list!

// ✓ Use LazyList for infinite sequences
val naturals = LazyList.from(1)
```

**Solution:** Use `LazyList` for potentially infinite sequences, `lazy val` for deferred computation.

### 2. Null Pointer Exceptions

**Problem:** Scala has `null` from Java interop, Haskell doesn't.

**Example:**
```scala
// ❌ Dangerous when calling Java code
val name: String = javaObject.getName  // Could be null!
val length = name.length  // NullPointerException

// ✓ Wrap in Option
val name: Option[String] = Option(javaObject.getName)
val length = name.map(_.length).getOrElse(0)
```

**Solution:** Always use `Option(...)` when calling Java code that might return null.

### 3. Uncurried Functions

**Problem:** Haskell functions are curried by default, Scala's are not.

**Example:**
```scala
// Haskell: add :: Int -> Int -> Int
// Scala: Either curried or uncurried

// ❌ Uncurried (not partial-application friendly)
def add(a: Int, b: Int): Int = a + b
// Can't do: val add5 = add(5, _)  // Requires placeholder

// ✓ Curried (Haskell-style)
def add(a: Int)(b: Int): Int = a + b
val add5 = add(5) _  // Partial application
```

**Solution:** Use curried functions `def f(a: A)(b: B)` when partial application is needed.

### 4. Missing Type Classes

**Problem:** Haskell has many built-in type classes; Scala requires libraries.

**Example:**
```scala
// ❌ No built-in Functor, Monad, etc.
def map[F[_], A, B](fa: F[A])(f: A => B): F[B] = ???  // Can't implement generically

// ✓ Use Cats library
import cats.Functor
import cats.implicits._

def map[F[_]: Functor, A, B](fa: F[A])(f: A => B): F[B] =
  fa.map(f)
```

**Solution:** Use Cats library for functional abstractions (Functor, Monad, Applicative, etc.).

### 5. Pattern Matching Exhaustiveness

**Problem:** Scala allows non-exhaustive matches without warnings by default.

**Example:**
```scala
// ❌ Non-exhaustive match (compiles but warns)
sealed trait Result
case class Success(value: Int) extends Result
case class Failure(error: String) extends Result

def handle(result: Result): String = result match {
  case Success(value) => s"Got $value"
  // Missing Failure case!
}

// ✓ Complete match
def handle(result: Result): String = result match {
  case Success(value) => s"Got $value"
  case Failure(error) => s"Error: $error"
}
```

**Solution:** Use `sealed trait` and enable `-Xfatal-warnings` compiler option to catch non-exhaustive matches.

### 6. Do-Notation vs For-Comprehension Differences

**Problem:** Subtle differences between Haskell do-notation and Scala for-comprehension.

**Example:**
```scala
// Haskell: do { return x }
// Scala: Must use yield

// ❌ Missing yield
val result = for {
  x <- Some(1)
  y <- Some(2)
  x + y  // Does nothing!
}

// ✓ Use yield
val result = for {
  x <- Some(1)
  y <- Some(2)
} yield x + y
```

**Solution:** Always use `yield` at the end of for-comprehensions (equivalent to Haskell's `return`).

### 7. Higher-Kinded Types

**Problem:** Scala 2 requires explicit kind annotation; Scala 3 is better.

**Example:**
```scala
// Haskell: class Functor f where
//           fmap :: (a -> b) -> f a -> f b

// Scala 2: Requires explicit kind
trait Functor[F[_]] {
  def map[A, B](fa: F[A])(f: A => B): F[B]
}

// Usage requires type lambda for partially applied types
// ❌ Can't do: Functor[Either[String, ?]] in Scala 2
// ✓ Scala 2: Need kind-projector plugin
// ✓ Scala 3: Much better support
```

**Solution:** Use Scala 3 for better higher-kinded type support, or use kind-projector plugin in Scala 2.

---

## Tooling

| Category | Haskell | Scala |
|----------|---------|-------|
| Build Tool | Cabal, Stack | sbt, Mill |
| REPL | GHCi | scala, sbt console |
| Formatter | stylish-haskell, brittany | scalafmt |
| Linter | hlint | scalafix, wartremover |
| Testing | HSpec, QuickCheck | ScalaTest, ScalaCheck |
| Type Checker | GHC | scalac |
| Package Registry | Hackage | Maven Central |
| Documentation | Haddock | Scaladoc |

### Helpful Libraries for Haskell Patterns

| Pattern | Haskell | Scala Library |
|---------|---------|---------------|
| Type classes | Prelude, base | cats, scalaz |
| Effects | transformers, mtl | cats-effect, zio |
| Optics | lens | monocle |
| JSON | aeson | circe, play-json |
| Parsing | parsec, megaparsec | cats-parse, fastparse |
| Testing | QuickCheck | scalacheck |
| STM | stm | scala-stm |

---

## Examples

### Example 1: Simple - List Processing

**Before (Haskell):**
```haskell
-- Sum of squares of even numbers
sumOfEvenSquares :: [Int] -> Int
sumOfEvenSquares xs = sum [x^2 | x <- xs, even x]

-- Alternative with functions
sumOfEvenSquares' :: [Int] -> Int
sumOfEvenSquares' = sum . map (^2) . filter even

-- Pattern matching on lists
myLength :: [a] -> Int
myLength [] = 0
myLength (_:xs) = 1 + myLength xs
```

**After (Scala):**
```scala
// Sum of squares of even numbers
def sumOfEvenSquares(xs: List[Int]): Int = {
  (for {
    x <- xs
    if x % 2 == 0
  } yield x * x).sum
}

// Alternative with method chaining (more idiomatic)
def sumOfEvenSquares(xs: List[Int]): Int =
  xs.filter(_ % 2 == 0).map(x => x * x).sum

// Pattern matching on lists
def myLength[A](xs: List[A]): Int = xs match {
  case Nil => 0
  case _ :: tail => 1 + myLength(tail)
}
```

### Example 2: Medium - Type Classes and ADTs

**Before (Haskell):**
```haskell
-- Type class
class Describable a where
  describe :: a -> String

-- ADT
data Shape = Circle Double
           | Rectangle Double Double
           deriving (Show, Eq)

instance Describable Shape where
  describe (Circle r) = "Circle with radius " ++ show r
  describe (Rectangle w h) = "Rectangle " ++ show w ++ "x" ++ show h

-- Using type class
printDescription :: Describable a => a -> IO ()
printDescription x = putStrLn (describe x)

-- Higher-order function with type class
mapDescribe :: Describable a => [a] -> [String]
mapDescribe = map describe
```

**After (Scala):**
```scala
// Type class
trait Describable[A] {
  def describe(a: A): String
}

object Describable {
  def apply[A](implicit d: Describable[A]): Describable[A] = d

  implicit class DescribableOps[A](val a: A) extends AnyVal {
    def describe(implicit d: Describable[A]): String = d.describe(a)
  }
}

// ADT
sealed trait Shape
case class Circle(radius: Double) extends Shape
case class Rectangle(width: Double, height: Double) extends Shape

// Type class instance
object Shape {
  implicit val describableShape: Describable[Shape] = new Describable[Shape] {
    def describe(shape: Shape): String = shape match {
      case Circle(r) => s"Circle with radius $r"
      case Rectangle(w, h) => s"Rectangle ${w}x$h"
    }
  }
}

// Using type class
def printDescription[A: Describable](x: A): Unit = {
  println(Describable[A].describe(x))
}

// Or with extension method
import Describable._
def printDescription[A: Describable](x: A): Unit = {
  println(x.describe)
}

// Higher-order function with type class
def mapDescribe[A: Describable](xs: List[A]): List[String] =
  xs.map(_.describe)
```

### Example 3: Complex - Parser Combinator with Monadic Composition

**Before (Haskell):**
```haskell
import Text.Parsec
import Text.Parsec.String (Parser)

-- Simple expression parser
data Expr = Num Int
          | Add Expr Expr
          | Mul Expr Expr
          deriving (Show, Eq)

number :: Parser Expr
number = Num . read <$> many1 digit

expr :: Parser Expr
expr = term `chainl1` addOp

term :: Parser Expr
term = factor `chainl1` mulOp

factor :: Parser Expr
factor = number <|> parens expr

parens :: Parser a -> Parser a
parens p = char '(' *> p <* char ')'

addOp :: Parser (Expr -> Expr -> Expr)
addOp = Add <$ char '+'

mulOp :: Parser (Expr -> Expr -> Expr)
mulOp = Mul <$ char '*'

-- Evaluator
eval :: Expr -> Int
eval (Num n) = n
eval (Add e1 e2) = eval e1 + eval e2
eval (Mul e1 e2) = eval e1 * eval e2

-- Usage
parseAndEval :: String -> Either ParseError Int
parseAndEval input = do
  expr <- parse expr "" input
  return (eval expr)
```

**After (Scala):**
```scala
import cats.parse.{Parser, Numbers}
import cats.parse.Parser._
import cats.parse.Rfc5234.{char, digit}

// Simple expression parser
sealed trait Expr
case class Num(value: Int) extends Expr
case class Add(left: Expr, right: Expr) extends Expr
case class Mul(left: Expr, right: Expr) extends Expr

object ExprParser {
  val number: Parser[Expr] =
    Numbers.digits.map(s => Num(s.toInt))

  lazy val expr: Parser[Expr] =
    chainl1(term, addOp)

  lazy val term: Parser[Expr] =
    chainl1(factor, mulOp)

  lazy val factor: Parser[Expr] =
    number.orElse(parens(expr))

  def parens[A](p: Parser[A]): Parser[A] =
    (char('(') *> p <* char(')'))

  val addOp: Parser[(Expr, Expr) => Expr] =
    char('+').as((e1: Expr, e2: Expr) => Add(e1, e2))

  val mulOp: Parser[(Expr, Expr) => Expr] =
    char('*').as((e1: Expr, e2: Expr) => Mul(e1, e2))

  // Helper for chainl1 (not built-in)
  def chainl1[A](p: Parser[A], op: Parser[(A, A) => A]): Parser[A] = {
    (p ~ (op ~ p).rep0).map {
      case (initial, ops) =>
        ops.foldLeft(initial) { case (acc, (f, next)) => f(acc, next) }
    }
  }
}

// Evaluator
def eval(expr: Expr): Int = expr match {
  case Num(n) => n
  case Add(e1, e2) => eval(e1) + eval(e2)
  case Mul(e1, e2) => eval(e1) * eval(e2)
}

// Usage
def parseAndEval(input: String): Either[Parser.Error, Int] = {
  ExprParser.expr.parseAll(input).map(eval)
}
```

---

## See Also

For more examples and patterns, see:
- `meta-convert-dev` - Foundational patterns with cross-language examples
- `convert-typescript-rust` - Similar functional programming conversion
- `lang-haskell-dev` - Haskell development patterns
- `lang-scala-dev` - Scala development patterns

Cross-cutting pattern skills:
- `patterns-concurrency-dev` - STM, async patterns across languages
- `patterns-serialization-dev` - JSON, validation patterns
- `patterns-metaprogramming-dev` - Type classes, macros, generics
