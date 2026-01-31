---
name: convert-scala-haskell
description: Convert Scala code to idiomatic Haskell. Use when migrating Scala projects to Haskell, translating Scala patterns to idiomatic Haskell, or refactoring Scala codebases. Extends meta-convert-dev with Scala-to-Haskell specific patterns.
---

# Convert Scala to Haskell

Convert Scala code to idiomatic Haskell. This skill extends `meta-convert-dev` with Scala-to-Haskell specific type mappings, idiom translations, and tooling.

## This Skill Extends

- `meta-convert-dev` - Foundational conversion patterns (APTV workflow, testing strategies)

For general concepts like the Analyze → Plan → Transform → Validate workflow, testing strategies, and common pitfalls, see the meta-skill first.

## This Skill Adds

- **Type mappings**: Scala types → Haskell types
- **Idiom translations**: Scala patterns → idiomatic Haskell
- **Error handling**: Scala Option/Either/Try → Haskell Maybe/Either
- **Async patterns**: Scala Future/IO → Haskell IO/Async
- **Lazy evaluation**: Scala strict by default → Haskell lazy by default
- **Type classes**: Scala implicits/given → Haskell type classes
- **Paradigm shift**: JVM/strict/object-oriented → Pure FP/lazy/functional

## This Skill Does NOT Cover

- General conversion methodology - see `meta-convert-dev`
- Scala language fundamentals - see `lang-scala-dev`
- Haskell language fundamentals - see `lang-haskell-dev`
- Reverse conversion (Haskell → Scala) - see `convert-haskell-scala`

---

## Quick Reference

| Scala | Haskell | Notes |
|-------|---------|-------|
| `String` | `String` | Both are immutable strings |
| `Int` | `Int` | 32-bit integers |
| `BigInt` | `Integer` | Arbitrary precision |
| `Double` | `Double` | Floating point |
| `Boolean` | `Bool` | Boolean values |
| `List[A]` | `[a]` | Linked list |
| `(A, B)` | `(a, b)` | Tuple |
| `Option[A]` | `Maybe a` | Nullable values |
| `Either[A, B]` | `Either a b` | Sum type for errors |
| `Future[A]` / `IO[A]` | `IO a` | Side effects |
| `case class` / `sealed trait` | `data` | ADTs |
| `trait` + `implicit`/`given` | `class` (type class) | Type classes |
| `A => B` | `a -> b` | Function types |
| `Monad[F]` (Cats) | `Monad m` | Monads |

## When Converting Code

1. **Analyze source thoroughly** before writing target
2. **Map types first** - create type equivalence table
3. **Preserve semantics** over syntax similarity
4. **Adopt Haskell idioms** - don't write "Scala code in Haskell syntax"
5. **Handle paradigm shifts** - strict → lazy, JVM → pure FP, objects → data + functions
6. **Test equivalence** - same inputs → same outputs

---

## Type System Mapping

### Primitive Types

| Scala | Haskell | Notes |
|-------|---------|-------|
| `Int` | `Int` | 32-bit signed integer |
| `Long` | `Int64` | 64-bit signed integer |
| `BigInt` | `Integer` | Arbitrary precision integer |
| `Double` | `Double` | 64-bit floating point |
| `Float` | `Float` | 32-bit floating point |
| `Boolean` | `Bool` | Boolean type |
| `Char` | `Char` | Single character |
| `String` | `String` | Immutable string (list of Char in Haskell) |
| `Unit` | `()` | Unit type (void) |

### Collection Types

| Scala | Haskell | Notes |
|-------|---------|-------|
| `List[A]` | `[a]` | Immutable linked list |
| `Vector[A]` | `Vector a` | Indexed sequence (import Data.Vector) |
| `(A, B)` | `(a, b)` | Tuple (Haskell supports larger tuples more naturally) |
| `(A, B, C)` | `(a, b, c)` | 3-tuple |
| `Map[K, V]` | `Map k v` | Immutable map (import Data.Map) |
| `Set[A]` | `Set a` | Immutable set (import Data.Set) |
| `Seq[A]` | `Seq a` | Generic sequence (import Data.Sequence) |
| `Array[A]` | `Array a` | Mutable array (import Data.Array) |

### Composite Types

| Scala | Haskell | Notes |
|-------|---------|-------|
| `sealed trait X; case object A extends X; case object B extends X` | `data X = A \| B` | Sum types |
| `case class X(field: Type)` | `data X = X { field :: Type }` | Product types with named fields |
| `case class X(value: Type) extends AnyVal` | `newtype X = X Type` | Zero-cost wrapper |
| `type X = Y` | `type X = Y` | Type alias |
| `Option[A]` | `Maybe a` | Optional values |
| `Either[A, B]` | `Either a b` | Sum type (Left is error by convention in both) |
| `Try[A]` | `Either SomeException a` | Exception handling |

### Function Types

| Scala | Haskell | Notes |
|-------|---------|-------|
| `A => B` | `a -> b` | Function from A to B |
| `(A, B) => C` | `a -> b -> c` or `(a, b) -> c` | Curried vs uncurried (currying is default in Haskell) |
| `A => B => C` | `a -> b -> c` | Curried function (natural in Haskell) |
| `Future[A]` / `IO[A]` (Cats Effect) | `IO a` | Effectful computation |
| `F[A]` (with Monad[F]) | `m a` (with Monad m) | Higher-kinded types |

---

## Idiom Translation

### Pattern 1: Option/Maybe Handling

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

**Why this translation:**
- `Option` and `Maybe` are semantically equivalent
- Both use pattern matching for explicit handling
- Haskell's `fromMaybe` is more concise than `.getOrElse`
- `maybe` function takes extractor as argument (not method call)

### Pattern 2: Either for Error Handling

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

**Why this translation:**
- Both use Either with Left for errors, Right for success
- Scala's `for-comprehension` maps to Haskell's `do-notation`
- ADT error types work similarly in both languages
- Haskell requires explicit `return` at the end of do-notation
- Scala's pattern matching on Option differs from Haskell's reads

### Pattern 3: For-Comprehension to List Comprehension

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
```

**Haskell:**
```haskell
-- List comprehension
squares = [x^2 | x <- [1..10], even x]

-- With multiple generators
pairs = [(x, y) | x <- [1..3], y <- [1..3], x < y]

-- Nested comprehensions
matrix = [[1..n] | n <- [1..5]]

-- Using map/filter
squares = map (\x -> x^2) $ filter even [1..10]
```

**Why this translation:**
- Both desugar to map/flatMap/filter (or >>=)
- Haskell's list comprehension syntax is more concise
- Guards (filters) use `if` in Scala, just predicates in Haskell
- Haskell comprehensions are natural for lists, Scala works with any monad

### Pattern 4: Pattern Matching on ADTs

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

**Why this translation:**
- Scala uses case classes extending sealed trait, Haskell uses data constructors
- Pattern matching syntax is similar
- Guards use `if` in Scala match, `|` in Haskell function definitions
- Haskell's pattern matching is built into function definitions, not just case expressions

### Pattern 5: Type Classes from Implicits/Given

**Scala (2.x with implicits):**
```scala
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

**Scala (3.x with given/using):**
```scala
trait Show[A] {
  def show(a: A): String
}

given Show[Int] with {
  def show(a: Int): String = a.toString
}

given Show[String] with {
  def show(a: String): String = s"'$a'"
}

def print[A](a: A)(using s: Show[A]): Unit = {
  println(s.show(a))
}
```

**Haskell:**
```haskell
class Show a where
  show :: a -> String

instance Show Int where
  show = Prelude.show  -- Using Prelude's show

instance Show String where
  show s = "'" ++ s ++ "'"

print :: Show a => a -> IO ()
print a = putStrLn (show a)
```

**Why this translation:**
- Scala's implicit/given parameters map to Haskell's type class constraints
- Scala's trait + implicit instances = Haskell's type class + instances
- Haskell's type class syntax is cleaner and more established
- Both resolve instances at compile time
- Haskell's instance resolution is simpler (no implicit scope complexity)

### Pattern 6: Monadic Composition

**Scala:**
```scala
// For-comprehension with Option
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

// With Future
import scala.concurrent.Future
import scala.concurrent.ExecutionContext.Implicits.global

val futureResult = for {
  a <- fetchDataA()
  b <- fetchDataB(a)
  c <- fetchDataC(b)
} yield c
```

**Haskell:**
```haskell
-- Do-notation with Maybe
result = do
  x <- Just 1
  y <- Just 2
  z <- Just 3
  return $ x + y + z

-- Desugars to
result = Just 1 >>= \x ->
         Just 2 >>= \y ->
         Just 3 >>= \z ->
         return (x + y + z)

-- With IO
ioResult :: IO Result
ioResult = do
  a <- fetchDataA
  b <- fetchDataB a
  c <- fetchDataC b
  return c
```

**Why this translation:**
- Scala's `for-comprehension` = Haskell's `do-notation`
- Both desugar to `flatMap`/`>>=` and `map`/`fmap`
- Scala's `yield` = Haskell's `return` (for final value)
- Haskell's do-notation works with any Monad
- No execution context needed in Haskell (purity by default)

### Pattern 7: Lazy Evaluation

**Scala (strict by default):**
```scala
// Eager evaluation
val expensiveValue = computeExpensive()  // Computed immediately

// Lazy val
lazy val lazyValue = computeExpensive()  // Computed on first access

// By-name parameter (re-evaluated each time)
def repeat(n: Int)(action: => Unit): Unit = {
  (1 to n).foreach(_ => action)
}

// Stream (lazy list) - Scala 2.x
val stream = Stream.from(1)
val first10 = stream.take(10).toList

// LazyList - Scala 3.x
val lazyList = LazyList.from(1)
val first10 = lazyList.take(10).toList
```

**Haskell (lazy by default):**
```haskell
-- Lazy evaluation (default)
expensiveValue = computeExpensive  -- Not computed until needed

-- Strict evaluation (with BangPatterns or seq)
strictValue = computeExpensive `seq` value

-- Infinite lists (natural due to laziness)
ones = 1 : ones
naturals = [1..]
fibs = 0 : 1 : zipWith (+) fibs (tail fibs)

-- Take from infinite list
first10 = take 10 naturals  -- [1,2,3,4,5,6,7,8,9,10]
first10Fibs = take 10 fibs  -- [0,1,1,2,3,5,8,13,21,34]
```

**Why this translation:**
- Scala is strict by default, Haskell is lazy by default
- Scala's `lazy val` = Haskell's default behavior
- Scala's `Stream`/`LazyList` = Haskell's regular lists (all lazy)
- Haskell makes infinite data structures natural
- Performance: lazy can avoid unnecessary computation, but can cause space leaks

---

## Paradigm Translation

### Mental Model Shift: JVM/Strict/OOP → Pure FP/Lazy/Functional

| Scala Concept | Haskell Approach | Key Insight |
|---------------|------------------|-------------|
| Class with mutable state | Record + pure functions | Data and behavior separated, no mutation |
| Object (singleton) | Module-level definitions | No special singleton syntax needed |
| Inheritance | Type classes / ADTs | Favor type classes and composition |
| Mutable loops | Recursion / fold / map | Transformation over mutation |
| Side effects (println, etc.) | IO monad | Effects segregated in IO type |
| Strict evaluation | Lazy evaluation | Evaluation delayed until needed |
| var (mutable variable) | Pure functions with recursion | No mutation, thread parameters |
| null | Maybe | Explicit optional values |

### Object-Oriented to Functional

**Scala (OOP style):**
```scala
class BankAccount(private var balance: Double) {
  def deposit(amount: Double): Unit = {
    balance += amount
  }

  def withdraw(amount: Double): Boolean = {
    if (balance >= amount) {
      balance -= amount
      true
    } else {
      false
    }
  }

  def getBalance: Double = balance
}

val account = new BankAccount(100.0)
account.deposit(50.0)
account.withdraw(30.0)
println(account.getBalance)  // 120.0
```

**Haskell (FP style):**
```haskell
data BankAccount = BankAccount { balance :: Double }
  deriving (Show)

deposit :: Double -> BankAccount -> BankAccount
deposit amount account = account { balance = balance account + amount }

withdraw :: Double -> BankAccount -> Maybe BankAccount
withdraw amount account =
  if balance account >= amount
  then Just $ account { balance = balance account - amount }
  else Nothing

-- Usage (threading state)
initialAccount = BankAccount 100.0
afterDeposit = deposit 50.0 initialAccount
afterWithdraw = case withdraw 30.0 afterDeposit of
  Just acc -> acc
  Nothing -> afterDeposit  -- Withdrawal failed, keep previous state
```

**Why this translation:**
- Scala's mutable object → Haskell's immutable data + pure functions
- State changes → new values
- Methods → pure functions taking state as parameter
- Failed operations → Maybe to indicate success/failure
- No side effects in Haskell version (pure)

### Concurrency Mental Model

| Scala Model | Haskell Model | Conceptual Translation |
|-------------|---------------|------------------------|
| Future + ExecutionContext | IO + async | Async computation in IO |
| Promise | MVar / IORef | Mutable reference in IO |
| Akka Actors | STM / async | Message passing → software transactional memory |
| Parallel collections | Par monad / Strategies | Explicit parallelism markers |
| synchronized / locks | STM transactions | Lock-free concurrent updates |

---

## Error Handling

### Scala Error Model → Haskell Error Model

**Scala has three main approaches:**

1. **Option** - Value may be absent (no error context)
2. **Either** - Value or error with context
3. **Try** - Catching exceptions

**Haskell approaches:**

1. **Maybe** - Value may be absent (no error context)
2. **Either** - Value or error with context
3. **ExceptT/MonadError** - Exception-like behavior in pure code

**Mapping:**

| Scala | Haskell | Use Case |
|-------|---------|----------|
| `Option[A]` | `Maybe a` | Nullable values, simple absence |
| `Either[E, A]` | `Either e a` | Errors with context |
| `Try[A]` | `Either SomeException a` | Exception handling |
| `IO[A]` | `IO a` | Side effects (can throw) |
| `Future[A]` | `IO a` / `async` | Async operations |

**Exception handling:**

**Scala:**
```scala
import scala.util.{Try, Success, Failure}

def parseInt(s: String): Try[Int] = Try(s.toInt)

parseInt("123") match {
  case Success(n) => println(s"Parsed: $n")
  case Failure(e) => println(s"Error: ${e.getMessage}")
}

// Converting to Either
val eitherResult: Either[Throwable, Int] = parseInt("123").toEither
```

**Haskell:**
```haskell
import Text.Read (readMaybe)
import Control.Exception (try, SomeException)

-- Pure version with Maybe
parseInt :: String -> Maybe Int
parseInt = readMaybe

case parseInt "123" of
  Just n -> putStrLn $ "Parsed: " ++ show n
  Nothing -> putStrLn "Error: not a valid number"

-- IO version catching exceptions
parseIntIO :: String -> IO (Either SomeException Int)
parseIntIO s = try $ return (read s)
```

**Why this translation:**
- `Try` in Scala ≈ `Maybe` or `Either SomeException` in Haskell
- Haskell prefers pure error handling with Maybe/Either
- IO exceptions are segregated to IO monad
- Use `readMaybe` for safe parsing (pure)
- Use `try` for catching IO exceptions

---

## Concurrency Patterns

### Scala Future → Haskell IO/Async

**Scala:**
```scala
import scala.concurrent.{Future, Await}
import scala.concurrent.duration._
import scala.concurrent.ExecutionContext.Implicits.global

// Creating futures
val future1 = Future { expensiveComputation() }
val future2 = Future { anotherComputation() }

// Combining futures
val combined = for {
  result1 <- future1
  result2 <- future2
} yield result1 + result2

// Blocking (avoid in production)
val result = Await.result(combined, 5.seconds)

// Callbacks
future1.onComplete {
  case Success(value) => println(s"Got: $value")
  case Failure(error) => println(s"Failed: $error")
}
```

**Haskell:**
```haskell
import Control.Concurrent.Async

-- Creating async computations
main = do
  async1 <- async expensiveComputation
  async2 <- async anotherComputation

  -- Waiting for results
  result1 <- wait async1
  result2 <- wait async2

  let combined = result1 + result2
  print combined

-- Or use concurrently
main = do
  (result1, result2) <- concurrently expensiveComputation anotherComputation
  print (result1 + result2)

-- Race (first to complete)
result <- race computation1 computation2
case result of
  Left a -> putStrLn $ "Left won: " ++ show a
  Right b -> putStrLn $ "Right won: " ++ show b
```

**Why this translation:**
- Scala's `Future` ≈ Haskell's `IO` with `async`
- No execution context needed in Haskell (simpler model)
- `for-comprehension` on Future → `do-notation` on IO
- Haskell's `async` library provides similar abstractions
- Haskell's concurrency is lighter weight (green threads)

### Scala Cats Effect IO → Haskell IO

**Scala (Cats Effect):**
```scala
import cats.effect._

val program = for {
  _ <- IO.println("What's your name?")
  name <- IO.readLine
  _ <- IO.println(s"Hello, $name!")
} yield ()

// Parallel execution
import cats.effect.syntax.parallel._

val parallel = (
  fetchUser(1),
  fetchUser(2),
  fetchUser(3)
).parMapN((u1, u2, u3) => List(u1, u2, u3))

// Resource management
def useFile(path: String): IO[String] = {
  Resource.make(
    IO(scala.io.Source.fromFile(path))
  )(source => IO(source.close()))
    .use(source => IO(source.mkString))
}
```

**Haskell:**
```haskell
import System.IO

program :: IO ()
program = do
  putStrLn "What's your name?"
  name <- getLine
  putStrLn $ "Hello, " ++ name ++ "!"

-- Parallel execution with async
import Control.Concurrent.Async

parallel :: IO [User]
parallel = mapConcurrently fetchUser [1, 2, 3]

-- Resource management with bracket
useFile :: FilePath -> IO String
useFile path = bracket
  (openFile path ReadMode)  -- Acquire
  hClose                     -- Release
  hGetContents              -- Use
```

**Why this translation:**
- Cats Effect IO ≈ Haskell's IO monad
- Both provide referentially transparent effects
- Haskell's IO is language-level, not a library
- `Resource.make` → `bracket` for resource safety
- Parallel execution: Cats parMapN → async library

---

## Memory & Ownership

### Scala GC → Haskell GC

Both Scala and Haskell use garbage collection, so memory management translation is relatively straightforward:

| Aspect | Scala (JVM) | Haskell (GHC) |
|--------|-------------|---------------|
| **Memory model** | Heap allocation, GC | Heap allocation, GC |
| **Reference types** | Objects on heap | Thunks and values on heap |
| **Immutability** | Opt-in (`val`, immutable collections) | Default (all values immutable) |
| **Space leaks** | Rare (eager evaluation) | Possible (lazy evaluation, retained thunks) |
| **Optimization** | JVM JIT compilation | GHC strictness analysis, inlining |

**Key differences:**

1. **Laziness can cause space leaks in Haskell:**

**Problem:**
```haskell
-- Space leak: foldl builds large thunk
sum = foldl (+) 0 [1..1000000]  -- BAD: stack overflow

-- Fix: use strict foldl'
import Data.List (foldl')
sum = foldl' (+) 0 [1..1000000]  -- GOOD: tail recursive + strict
```

2. **Scala's strictness is safer for beginners:**

```scala
// No space leak - eager evaluation
val sum = (1 to 1000000).foldLeft(0)(_ + _)
```

**When converting:**
- Watch for space leaks caused by lazy evaluation
- Use strict functions (`foldl'`, `seq`, BangPatterns) when needed
- Profile memory usage for large data processing

---

## Common Pitfalls

1. **Laziness vs. Strictness**
   - **Pitfall:** Scala's strict evaluation → Haskell's lazy evaluation can cause unexpected behavior
   - **Example:** In Scala, `val x = heavyComputation()` runs immediately; in Haskell, `x = heavyComputation` delays until used
   - **Solution:** Understand when evaluation happens; use strictness annotations if needed

2. **Type Class Orphan Instances**
   - **Pitfall:** Scala allows defining implicits anywhere; Haskell forbids orphan instances
   - **Example:** In Scala, you can define `implicit val show: Show[ThirdPartyType]` in any file; Haskell requires instances in the module defining the type or the class
   - **Solution:** Use newtype wrappers for orphan instances in Haskell

3. **Null vs. Maybe**
   - **Pitfall:** Scala can have null values (Java interop); Haskell has no null
   - **Example:** Scala's `Option(nullableValue)` wraps potential null; Haskell has no null concept
   - **Solution:** Always use Maybe for optional values in Haskell; no null checks needed

4. **Mutable State**
   - **Pitfall:** Scala allows `var` and mutable collections; Haskell has no mutation outside IO
   - **Example:** Scala's `var counter = 0; counter += 1`; Haskell needs State monad or IORef
   - **Solution:** Rewrite using recursion, State monad, or IORef for true mutability

5. **Type Inference Differences**
   - **Pitfall:** Scala's type inference is more aggressive; Haskell sometimes needs annotations
   - **Example:** Polymorphic recursion often needs type signatures in Haskell
   - **Solution:** Add type signatures to top-level definitions (good practice anyway)

6. **List Performance**
   - **Pitfall:** Scala's List and Haskell's list have different performance characteristics due to strictness
   - **Example:** Scala's `List(1, 2, 3).last` is O(n); Haskell's `last [1, 2, 3]` is also O(n), but laziness may help in some cases
   - **Solution:** Use appropriate data structures (Vector, Seq) for different access patterns

7. **String Type**
   - **Pitfall:** Scala's String is Java String; Haskell's String is `[Char]` (linked list)
   - **Example:** Haskell String can be slow for large text processing
   - **Solution:** Use Text or ByteString for performance-critical string operations in Haskell

8. **Type Class Constraints**
   - **Pitfall:** Scala's implicit resolution is complex; Haskell's is simpler but more restrictive
   - **Example:** Scala allows multiple implicit parameters of same type; Haskell doesn't
   - **Solution:** Use newtype wrappers to disambiguate type class instances

---

## Limitations

### Coverage Gaps

| Pillar | Source Skill (lang-scala-dev) | Target Skill (lang-haskell-dev) | Mitigation |
|--------|-------------------------------|--------------------------------|------------|
| Module | ~ (package objects) | ✓ (Module System) | Reference lang-haskell-dev |
| Serialization | ✗ (not covered) | ✓ (Serialization) | Reference lang-haskell-dev for Aeson patterns |

### Known Limitations

1. **Module System**: Scala's package objects and imports differ from Haskell's module system. Conversion patterns for module organization may be incomplete.
2. **Serialization**: Scala's serialization patterns (Play JSON, Circe) have limited coverage in lang-scala-dev. Reference Haskell's Aeson library directly.

### External Resources

For areas with limited coverage, consult:
- **Haskell module system:** https://wiki.haskell.org/Module
- **Aeson (JSON):** https://hackage.haskell.org/package/aeson

---

## Tooling

| Tool | Purpose | Notes |
|------|---------|-------|
| **Haskell Language Server (HLS)** | IDE support | Type hints, refactoring, linting |
| **GHC** | Compiler | Glasgow Haskell Compiler |
| **Cabal** | Build tool | Package management, dependencies |
| **Stack** | Build tool | Curated package sets, reproducible builds |
| **Hoogle** | API search | Search by type signature |
| **hlint** | Linter | Suggests idiomatic Haskell improvements |
| **ormolu / brittany** | Formatter | Auto-format Haskell code |
| **ghcid** | File watcher | Fast reload on file changes |

**Scala → Haskell tooling equivalents:**

| Scala Tool | Haskell Equivalent | Notes |
|------------|-------------------|-------|
| sbt | Cabal / Stack | Build and dependency management |
| IntelliJ IDEA | VSCode + HLS | IDE support |
| Scalafmt | Ormolu / Brittany | Code formatting |
| Scalafix | hlint | Linting and refactoring |
| Metals | HLS | Language server |

---

## Examples

### Example 1: Simple - Option/Maybe

**Before (Scala):**
```scala
def findUserById(id: Int, users: List[User]): Option[User] = {
  users.find(_.id == id)
}

val user = findUserById(123, allUsers)
val name = user.map(_.name).getOrElse("Unknown")
println(name)
```

**After (Haskell):**
```haskell
data User = User { userId :: Int, userName :: String }

findUserById :: Int -> [User] -> Maybe User
findUserById targetId users = find (\u -> userId u == targetId) users

main :: IO ()
main = do
  let user = findUserById 123 allUsers
  let name = maybe "Unknown" userName user
  putStrLn name
```

### Example 2: Medium - Either Error Handling with Chaining

**Before (Scala):**
```scala
case class User(email: String, age: Int)

sealed trait ValidationError
case class InvalidEmail(msg: String) extends ValidationError
case class InvalidAge(msg: String) extends ValidationError

def validateEmail(email: String): Either[ValidationError, String] = {
  if (email.contains("@")) Right(email)
  else Left(InvalidEmail("Email must contain @"))
}

def validateAge(age: Int): Either[ValidationError, Int] = {
  if (age >= 0 && age <= 150) Right(age)
  else Left(InvalidAge("Age must be between 0 and 150"))
}

def createUser(email: String, age: Int): Either[ValidationError, User] = {
  for {
    validEmail <- validateEmail(email)
    validAge <- validateAge(age)
  } yield User(validEmail, validAge)
}

// Usage
createUser("alice@example.com", 30) match {
  case Right(user) => println(s"Created user: $user")
  case Left(error) => println(s"Validation failed: $error")
}
```

**After (Haskell):**
```haskell
data User = User { email :: String, age :: Int }
  deriving (Show)

data ValidationError
  = InvalidEmail String
  | InvalidAge String
  deriving (Show)

validateEmail :: String -> Either ValidationError String
validateEmail email =
  if '@' `elem` email
  then Right email
  else Left (InvalidEmail "Email must contain @")

validateAge :: Int -> Either ValidationError Int
validateAge age =
  if age >= 0 && age <= 150
  then Right age
  else Left (InvalidAge "Age must be between 0 and 150")

createUser :: String -> Int -> Either ValidationError User
createUser emailStr ageVal = do
  validEmail <- validateEmail emailStr
  validAge <- validateAge ageVal
  return $ User validEmail validAge

-- Usage
main :: IO ()
main = do
  case createUser "alice@example.com" 30 of
    Right user -> putStrLn $ "Created user: " ++ show user
    Left err -> putStrLn $ "Validation failed: " ++ show err
```

### Example 3: Complex - Async HTTP Client with Error Handling

**Before (Scala):**
```scala
import scala.concurrent.{Future, ExecutionContext}
import scala.concurrent.ExecutionContext.Implicits.global
import scala.util.{Try, Success, Failure}

case class ApiResponse(data: String, statusCode: Int)
case class User(id: Int, name: String, email: String)

sealed trait ApiError
case class NetworkError(msg: String) extends ApiError
case class ParseError(msg: String) extends ApiError
case object NotFound extends ApiError

class HttpClient {
  def get(url: String): Future[ApiResponse] = Future {
    // Simulated HTTP call
    if (url.contains("users/123"))
      ApiResponse("""{"id":123,"name":"Alice","email":"alice@example.com"}""", 200)
    else
      ApiResponse("", 404)
  }
}

def parseUser(response: ApiResponse): Either[ApiError, User] = {
  if (response.statusCode == 404) Left(NotFound)
  else {
    Try {
      // Simplified parsing (in real code, use circe/play-json)
      val pattern = """.*"id":(\d+).*"name":"([^"]+)".*"email":"([^"]+)".*""".r
      response.data match {
        case pattern(id, name, email) => User(id.toInt, name, email)
      }
    }.toEither.left.map(e => ParseError(e.getMessage))
  }
}

def fetchUser(userId: Int)(implicit ec: ExecutionContext): Future[Either[ApiError, User]] = {
  val client = new HttpClient
  client.get(s"https://api.example.com/users/$userId")
    .map(parseUser)
    .recover {
      case e: Exception => Left(NetworkError(e.getMessage))
    }
}

// Usage
def main(args: Array[String]): Unit = {
  import scala.concurrent.Await
  import scala.concurrent.duration._

  val result = Await.result(fetchUser(123), 5.seconds)
  result match {
    case Right(user) => println(s"Found user: ${user.name}")
    case Left(NotFound) => println("User not found")
    case Left(NetworkError(msg)) => println(s"Network error: $msg")
    case Left(ParseError(msg)) => println(s"Parse error: $msg")
  }
}
```

**After (Haskell):**
```haskell
{-# LANGUAGE OverloadedStrings #-}

import Control.Exception (try, SomeException)
import Data.Aeson (FromJSON, parseJSON, withObject, (.:), eitherDecode)
import qualified Data.ByteString.Lazy.Char8 as BL
import Network.HTTP.Simple
  ( httpLBS, getResponseBody, getResponseStatusCode
  , parseRequest, Response )

data User = User
  { userId :: Int
  , userName :: String
  , userEmail :: String
  } deriving (Show)

instance FromJSON User where
  parseJSON = withObject "User" $ \v -> User
    <$> v .: "id"
    <*> v .: "name"
    <*> v .: "email"

data ApiError
  = NetworkError String
  | ParseError String
  | NotFound
  deriving (Show)

-- Fetch user with error handling
fetchUser :: Int -> IO (Either ApiError User)
fetchUser uid = do
  result <- try $ do
    request <- parseRequest $ "https://api.example.com/users/" ++ show uid
    response <- httpLBS request
    let statusCode = getResponseStatusCode response
    let body = getResponseBody response

    if statusCode == 404
      then return $ Left NotFound
      else case eitherDecode body of
        Right user -> return $ Right user
        Left err -> return $ Left (ParseError err)

  case result of
    Left (e :: SomeException) -> return $ Left (NetworkError (show e))
    Right userOrError -> return userOrError

-- Usage
main :: IO ()
main = do
  result <- fetchUser 123
  case result of
    Right user -> putStrLn $ "Found user: " ++ userName user
    Left NotFound -> putStrLn "User not found"
    Left (NetworkError msg) -> putStrLn $ "Network error: " ++ msg
    Left (ParseError msg) -> putStrLn $ "Parse error: " ++ msg
```

**Key translation points:**
- Scala Future → Haskell IO (no execution context needed)
- Scala circe/play-json → Haskell Aeson
- Pattern matching on sealed traits → pattern matching on ADTs
- Exception handling with try/recover → Control.Exception.try
- Both versions segregate IO effects and use Either for domain errors

---

## See Also

For more examples and patterns, see:
- `meta-convert-dev` - Foundational patterns with cross-language examples
- `convert-haskell-scala` - Reverse conversion (Haskell → Scala)
- `lang-scala-dev` - Scala development patterns
- `lang-haskell-dev` - Haskell development patterns

Cross-cutting pattern skills (for areas not fully covered by lang-*-dev):
- `patterns-concurrency-dev` - Async, threads, STM across languages
- `patterns-serialization-dev` - JSON, validation across languages
- `patterns-metaprogramming-dev` - Template Haskell, Scala macros comparison
