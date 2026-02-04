---
name: convert-clojure-scala
description: Bidirectional conversion between Clojure and Scala. Use when migrating projects between these languages in either direction. Extends meta-convert-dev with Clojure↔Scala specific patterns. Use when migrating Clojure projects to Scala, translating Clojure patterns to idiomatic Scala, or refactoring Clojure codebases. Extends meta-convert-dev with Clojure-to-Scala specific patterns.
---

# Clojure ↔ Scala Conversion

Bidirectional conversion between Clojure and Scala. This skill extends `meta-convert-dev` with Clojure↔Scala specific type mappings, idiom translations, and tooling for converting functional code between dynamic Lisp and statically-typed hybrid FP/OOP.

## This Skill Extends

- `meta-convert-dev` - Foundational conversion patterns (APTV workflow, testing strategies)

For general concepts like the Analyze → Plan → Transform → Validate workflow, testing strategies, and common pitfalls, see the meta-skill first.

## This Skill Adds

- **Type mappings**: Clojure dynamic types → Scala static types with inference
- **Idiom translations**: Clojure Lisp-style → idiomatic Scala hybrid FP/OOP
- **Error handling**: Clojure exceptions/maps → Scala Option/Either/Try
- **Async patterns**: Clojure core.async/futures → Scala Futures/Akka/Cats Effect
- **Concurrency models**: STM/agents → actors/STM alternatives
- **Platform translation**: JVM (Clojure) → JVM (Scala) with better performance

## This Skill Does NOT Cover

- General conversion methodology - see `meta-convert-dev`
- Clojure language fundamentals - see `lang-clojure-dev`
- Scala language fundamentals - see `lang-scala-dev`

---

## Quick Reference

| Clojure | Scala | Notes |
|---------|-------|-------|
| `String` | `String` | Direct mapping (both JVM) |
| `Long` (default int) | `Int` / `Long` | Scala Int more common; Long for large |
| `Double` (default decimal) | `Double` | Direct mapping |
| `Boolean` | `Boolean` | `true`/`false` in both |
| `nil` | `None` / `null` | Prefer Option[A] over null |
| `'(...)` list | `List[A]` | Immutable linked list |
| `[...]` vector | `Vector[A]` / `List[A]` | Vector for indexed, List for sequential |
| `{...}` map | `Map[K, V]` | Immutable map |
| `#{...}` set | `Set[A]` | Immutable set |
| `(fn [x] ...)` | `(x: A) => B` | Lambda/anonymous function |
| `defn` | `def name(...)` | Named function |
| `defrecord` | `case class` | Data structure with methods |
| Multimethod | Trait + pattern matching | Polymorphic dispatch |
| Protocol | Trait | Behavior contract |
| Atom | `AtomicReference` / `Ref` | Mutable reference |
| Agent | Akka actor / `Future` | Async computation |
| core.async channel | Akka Stream / FS2 | Stream processing |
| Macro | Inline / macro (limited) | Compile-time metaprogramming |
| `->>` thread-last | `.map().filter()` | Method chaining |

## When Converting Code

1. **Analyze source thoroughly** before writing target - understand Clojure semantics
2. **Map types first** - create explicit type mapping table (dynamic → static)
3. **Preserve semantics** over syntax similarity
4. **Adopt Scala idioms** - don't write "Clojure code in Scala syntax"
5. **Handle edge cases** - nil-safety, lazy evaluation, type erasure
6. **Test equivalence** - same inputs → same outputs
7. **Embrace static typing** - leverage compiler for correctness
8. **Consider performance** - Scala can be more performant with proper types

---

## Type System Mapping

### Primitive Types

| Clojure | Scala | Notes |
|---------|-------|-------|
| `Boolean` (true/false) | `Boolean` | Direct mapping |
| `Long` (default integer) | `Int` | Scala Int (32-bit) is more common |
| `Long` (large integers) | `Long` | Use Long for 64-bit integers |
| `BigInt` | `BigInt` | Arbitrary precision integers |
| `Double` (default decimal) | `Double` | Direct mapping |
| `BigDecimal` | `BigDecimal` | Arbitrary precision decimals |
| `Character` | `Char` | Single character |
| `String` | `String` | Immutable strings (JVM) |
| `nil` | `null` / `None` | Prefer `Option[A]` over null |
| Keyword `:key` | `Symbol('key)` / String | Use sealed traits or enums for tagged types |
| Symbol `'sym` | No direct equivalent | Use case objects or sealed traits |
| Ratio `1/3` | No direct equivalent | Use `Rational` library or `Double` |

### Collection Types

| Clojure | Scala | Notes |
|---------|-------|-------|
| `'(1 2 3)` list | `List(1, 2, 3)` | Immutable singly-linked list |
| `[1 2 3]` vector | `Vector(1, 2, 3)` | Indexed immutable sequence |
| `{:a 1 :b 2}` map | `Map("a" -> 1, "b" -> 2)` | Immutable hash map |
| `#{1 2 3}` set | `Set(1, 2, 3)` | Immutable hash set |
| Lazy seq | `LazyList` / `Iterator` | Lazy evaluation |
| Transient | Mutable collections | Use `scala.collection.mutable` temporarily |
| Persistent | Immutable collections | Default in Scala |
| Java array | `Array[A]` | Mutable, fixed-size |

### Composite Types

| Clojure | Scala | Notes |
|---------|-------|-------|
| Plain map `{:name "Alice"}` | `case class User(name: String)` | Prefer case classes for structured data |
| Plain map (open) | `Map[String, Any]` | When structure is truly dynamic |
| `defrecord` | `case class` | Data structure with protocol implementations |
| Tagged map `{:type :circle}` | `sealed trait` + case classes | ADT with pattern matching |
| Multimethod dispatch | Pattern matching | Type-based dispatch |
| Protocol | Trait | Interface with possible default implementations |
| `deftype` | `class` + trait | Low-level performance-critical types |
| Namespace | `object` (singleton) | Module-level functions/values |

### Function Types

| Clojure | Scala | Notes |
|---------|-------|-------|
| `(fn [x] body)` | `(x: A) => B` | Anonymous function |
| `(fn [x y] body)` | `(x: A, y: B) => C` | Multi-parameter function |
| `#(+ % 1)` | `_ + 1` | Placeholder syntax |
| Variadic `[& args]` | `args: A*` | Variable arguments |
| Multi-arity fn | Overloaded methods | Multiple parameter lists |
| Curried (manual) | Curried `def f(x: A)(y: B)` | Automatic currying in Scala |

### Nil/Null Handling

| Clojure | Scala | Notes |
|---------|-------|-------|
| `nil` | `None` | Absence of value |
| Value | `Some(value)` | Present value |
| Check `(nil? x)` | `x.isEmpty` | Pattern matching preferred |
| `(some? x)` | `x.isDefined` | Check for presence |
| `(or x default)` | `x.getOrElse(default)` | Default value |
| `(when-let [x ...] ...)` | `for { x <- opt } yield ...` | For-comprehension |
| `(some-> x f g)` | `x.map(f).map(g)` | Chained operations |

---

## Idiom Translation

### Pattern 1: nil → Option Type

**Clojure:**
```clojure
(defn get-user [id]
  ;; Returns nil if not found
  (get @users-db id))

(defn get-user-email [id]
  (when-let [user (get-user id)]
    (:email user)))

;; With default
(defn get-user-name [id]
  (if-let [user (get-user id)]
    (:name user)
    "Unknown"))
```

**Scala:**
```scala
def getUser(id: Int): Option[User] = {
  usersDb.get(id)
}

def getUserEmail(id: Int): Option[String] = {
  getUser(id).map(_.email)
}

// With default
def getUserName(id: Int): String = {
  getUser(id).map(_.name).getOrElse("Unknown")
}

// Pattern matching
def getUserNameMatch(id: Int): String = getUser(id) match {
  case Some(user) => user.name
  case None => "Unknown"
}
```

**Why this translation:**
- Clojure `nil` → Scala `None` (explicit absence)
- Clojure `when-let` → Scala `.map()` combinator
- Clojure `if-let` with default → Scala `.getOrElse()`
- Pattern matching is more idiomatic in Scala than if/else chains
- Compiler enforces handling of both Some and None cases

### Pattern 2: Maps → Case Classes

**Clojure:**
```clojure
(def user {:name "Alice" :age 30 :email "alice@example.com"})

(defn greet [user]
  (str "Hello, " (:name user)))

(defn is-adult? [user]
  (>= (:age user) 18))

;; Update
(def updated-user (assoc user :age 31))
```

**Scala:**
```scala
case class User(name: String, age: Int, email: String)

val user = User("Alice", 30, "alice@example.com")

def greet(user: User): String = {
  s"Hello, ${user.name}"
}

def isAdult(user: User): Boolean = {
  user.age >= 18
}

// Update (immutable copy)
val updatedUser = user.copy(age = 31)
```

**Why this translation:**
- Clojure maps → Scala case classes for structured data
- Keyword access `:key` → Field access `.field`
- Clojure `assoc` → Scala `.copy()` method
- Case classes provide:
  - Compile-time field checking
  - Pattern matching support
  - Automatic `equals`, `hashCode`, `toString`
  - Better IDE support and refactoring

### Pattern 3: Threading Macros → Method Chaining

**Clojure:**
```clojure
(defn process-items [items]
  (->> items
       (filter :active)
       (map :value)
       (filter #(> % 10))
       (reduce +)))

;; Thread-first
(defn transform-user [user]
  (-> user
      (assoc :normalized-name (clojure.string/lower-case (:name user)))
      (update :age inc)
      (dissoc :temp-field)))
```

**Scala:**
```scala
def processItems(items: List[Item]): Int = {
  items
    .filter(_.active)
    .map(_.value)
    .filter(_ > 10)
    .sum
}

// Or with for-comprehension
def processItemsFor(items: List[Item]): Int = {
  (for {
    item <- items if item.active
    value = item.value if value > 10
  } yield value).sum
}

// Thread-first style
def transformUser(user: User): User = {
  user
    .copy(normalizedName = user.name.toLowerCase)
    .copy(age = user.age + 1)
}
```

**Why this translation:**
- Clojure `->>` (thread-last) → Scala method chaining (data flows left-to-right)
- Clojure `->` (thread-first) → Scala `.copy()` chaining for updates
- Scala for-comprehensions are alternative for complex filter/map chains
- Method chaining is more natural in Scala due to OOP foundation
- Both styles maintain immutability

### Pattern 4: Multimethods → Pattern Matching / Type Classes

**Clojure:**
```clojure
(defmulti area :type)

(defmethod area :circle [{:keys [radius]}]
  (* Math/PI radius radius))

(defmethod area :rectangle [{:keys [width height]}]
  (* width height))

(defmethod area :triangle [{:keys [base height]}]
  (* 0.5 base height))

;; Usage
(area {:type :circle :radius 5})
```

**Scala:**
```scala
// Approach 1: Sealed trait + pattern matching (most idiomatic)
sealed trait Shape
case class Circle(radius: Double) extends Shape
case class Rectangle(width: Double, height: Double) extends Shape
case class Triangle(base: Double, height: Double) extends Shape

def area(shape: Shape): Double = shape match {
  case Circle(r) => math.Pi * r * r
  case Rectangle(w, h) => w * h
  case Triangle(b, h) => 0.5 * b * h
}

// Approach 2: Polymorphic method (OOP style)
sealed trait Shape {
  def area: Double
}

case class Circle(radius: Double) extends Shape {
  def area: Double = math.Pi * radius * radius
}

case class Rectangle(width: Double, height: Double) extends Shape {
  def area: Double = width * height
}

case class Triangle(base: Double, height: Double) extends Shape {
  def area: Double = 0.5 * base * height
}

// Usage
val circle = Circle(5)
area(circle)  // Approach 1
circle.area   // Approach 2
```

**Why this translation:**
- Clojure multimethods → Scala sealed traits + pattern matching (type-safe dispatch)
- Clojure `:type` key → Scala case class type (compiler-checked)
- Pattern matching exhaustiveness checked at compile time
- Alternative: polymorphic methods for OOP-style dispatch
- Sealed traits ensure all cases are known at compile time

### Pattern 5: Atoms → AtomicReference / Ref

**Clojure:**
```clojure
(def counter (atom 0))

(swap! counter inc)
(swap! counter + 5)
(reset! counter 0)

@counter  ;; Deref

;; With validation
(def validated-atom
  (atom 0
    :validator #(>= % 0)))
```

**Scala:**
```scala
import java.util.concurrent.atomic.AtomicReference

val counter = new AtomicReference(0)

counter.updateAndGet(_ + 1)
counter.updateAndGet(_ + 5)
counter.set(0)

counter.get()  // Deref

// With Cats STM
import cats.effect.IO
import cats.effect.std.Ref

val program = for {
  counter <- Ref[IO].of(0)
  _ <- counter.update(_ + 1)
  _ <- counter.update(_ + 5)
  _ <- counter.set(0)
  value <- counter.get
} yield value

// Or use synchronized for simple cases
class Counter {
  private var count = 0

  def increment(): Int = synchronized {
    count += 1
    count
  }

  def get: Int = synchronized(count)
}
```

**Why this translation:**
- Clojure `atom` → Scala `AtomicReference` for thread-safe mutable state
- Clojure `swap!` → Scala `.updateAndGet()`
- Clojure `reset!` → Scala `.set()`
- Clojure `@atom` → Scala `.get()`
- For functional effects, use Cats Effect `Ref[IO]`
- Validation can be added through wrapper methods

### Pattern 6: core.async Channels → Akka Streams / FS2

**Clojure:**
```clojure
(require '[clojure.core.async :as async :refer [go <! >! chan]])

(defn process-messages []
  (let [ch (chan 10)]
    (go
      (loop []
        (when-let [msg (<! ch)]
          (println "Processing:" msg)
          (recur))))
    ch))

(def ch (process-messages))
(go (>! ch "Hello"))
```

**Scala:**
```scala
// Approach 1: Akka Streams
import akka.stream._
import akka.stream.scaladsl._
import akka.actor.ActorSystem

implicit val system = ActorSystem()
implicit val materializer = ActorMaterializer()

val source = Source.queue[String](bufferSize = 10, OverflowStrategy.backpressure)

val (queue, _) = source
  .map { msg =>
    println(s"Processing: $msg")
    msg
  }
  .toMat(Sink.ignore)(Keep.both)
  .run()

queue.offer("Hello")

// Approach 2: FS2 (functional streams)
import cats.effect.IO
import fs2._

val stream = Stream.eval(IO(println("Processing: Hello")))
stream.compile.drain.unsafeRunSync()

// Approach 3: Simple Future-based
import scala.concurrent.Future
import scala.concurrent.ExecutionContext.Implicits.global

def processMessages(): String => Future[Unit] = { msg =>
  Future {
    println(s"Processing: $msg")
  }
}

val processor = processMessages()
processor("Hello")
```

**Why this translation:**
- Clojure core.async channels → Akka Streams for back-pressure and complex flows
- Clojure go blocks → Scala Futures or FS2 streams
- Akka Streams provide more structure and operators
- FS2 integrates with Cats Effect for pure FP
- Choose based on complexity: Futures (simple), Akka (complex), FS2 (pure FP)

### Pattern 7: Macros → Inline Methods / Compile-Time

**Clojure:**
```clojure
(defmacro unless [condition & body]
  `(if (not ~condition)
     (do ~@body)))

(unless false
  (println "This runs")
  "result")

;; Infix macro
(defmacro infix [a op b]
  `(~op ~a ~b))

(infix 3 + 5)  ;; => 8
```

**Scala:**
```scala
// Scala 3: Inline methods (simpler than macros)
inline def unless(condition: Boolean)(body: => Unit): Unit = {
  if (!condition) body
}

unless(false) {
  println("This runs")
  "result"
}

// Scala 2: By-name parameters
def unless2(condition: Boolean)(body: => Unit): Unit = {
  if (!condition) body
}

// For infix, use operators
extension (a: Int) {
  infix def plus(b: Int): Int = a + b
}

3 plus 5  // => 8

// Scala 3 macros (for complex metaprogramming)
import scala.quoted.*

inline def debug(inline expr: Any): Any = ${
  debugImpl('expr)
}

def debugImpl(expr: Expr[Any])(using Quotes): Expr[Any] = {
  import quotes.reflect.*
  val tree = expr.asTerm
  val code = tree.show
  '{
    println(s"$code => ${$expr}")
    $expr
  }
}
```

**Why this translation:**
- Clojure macros → Scala inline methods (Scala 3) for simple cases
- Complex metaprogramming → Scala 3 macros (quote/splice)
- By-name parameters `=> A` for lazy evaluation (similar to macro delay)
- Extension methods for DSL-like syntax
- Scala macros are more restrictive but type-safe
- Prefer higher-order functions over macros when possible

### Pattern 8: Protocols → Traits

**Clojure:**
```clojure
(defprotocol Drawable
  (draw [this]))

(defrecord Circle [radius]
  Drawable
  (draw [this]
    (str "Drawing circle with radius " radius)))

(defrecord Rectangle [width height]
  Drawable
  (draw [this]
    (str "Drawing rectangle " width "x" height)))

;; Extend to existing types
(extend-type String
  Drawable
  (draw [this]
    (str "Drawing text: " this)))
```

**Scala:**
```scala
trait Drawable {
  def draw: String
}

case class Circle(radius: Double) extends Drawable {
  def draw: String = s"Drawing circle with radius $radius"
}

case class Rectangle(width: Double, height: Double) extends Drawable {
  def draw: String = s"Drawing rectangle ${width}x${height}"
}

// Extension methods for existing types (Scala 3)
extension (s: String) {
  def draw: String = s"Drawing text: $s"
}

// Or implicit class (Scala 2)
implicit class DrawableString(s: String) extends Drawable {
  def draw: String = s"Drawing text: $s"
}

// Usage
val circle: Drawable = Circle(5)
circle.draw

"Hello".draw  // Extension method
```

**Why this translation:**
- Clojure protocols → Scala traits (interfaces with implementations)
- Clojure `defrecord` with protocol → Scala case class extending trait
- Clojure `extend-type` → Scala extension methods or implicit classes
- Scala traits support default implementations
- Extension methods don't require wrapper types
- Traits can have type parameters and self-types

---

## Error Handling

### Clojure Error Model → Scala Error Model

Clojure primarily uses exceptions with ex-info for structured errors. Scala offers typed error handling with Option, Either, and Try.

**Clojure exception pattern:**
```clojure
(defn divide [a b]
  (if (zero? b)
    (throw (ex-info "Division by zero" {:numerator a}))
    (/ a b)))

(defn safe-divide [a b]
  (try
    {:ok (divide a b)}
    (catch Exception e
      {:error (.getMessage e) :data (ex-data e)})))
```

**Scala typed error pattern:**
```scala
// Option for simple presence/absence
def divide(a: Int, b: Int): Option[Int] = {
  if (b == 0) None
  else Some(a / b)
}

// Either for error details
def divideEither(a: Int, b: Int): Either[String, Int] = {
  if (b == 0) Left("Division by zero")
  else Right(a / b)
}

// Try for exception handling
import scala.util.{Try, Success, Failure}

def divideTry(a: Int, b: Int): Try[Int] = Try {
  if (b == 0) throw new ArithmeticException("Division by zero")
  a / b
}

// Custom error type (recommended for domain errors)
sealed trait DivisionError
case object DivisionByZero extends DivisionError
case class InvalidInput(msg: String) extends DivisionError

def divideTyped(a: Int, b: Int): Either[DivisionError, Int] = {
  if (b == 0) Left(DivisionByZero)
  else Right(a / b)
}
```

**Error propagation:**

| Clojure | Scala | Notes |
|---------|-------|-------|
| `try/catch` | `try/catch` | For exceptions |
| `{:ok/:error}` maps | `Either[L, R]` | Typed error handling |
| Nil for absence | `Option[A]` | Safe nullability |
| `ex-info` with data | Custom case classes | Structured errors |
| Error threading | `.map()`, `.flatMap()` | Monadic composition |

**For-comprehension error handling:**
```scala
def compute(a: Int, b: Int, c: Int): Either[String, Int] = {
  for {
    x <- divideEither(a, b)
    y <- divideEither(x, c)
    z <- divideEither(y, 2)
  } yield z
}

// Equivalent to nested flatMap/map
divideEither(a, b)
  .flatMap(x => divideEither(x, c))
  .flatMap(y => divideEither(y, 2))
```

---

## Concurrency Patterns

### STM (Software Transactional Memory)

**Clojure:**
```clojure
(def account-a (ref 1000))
(def account-b (ref 2000))

(dosync
  (alter account-a - 100)
  (alter account-b + 100))
```

**Scala:**
```scala
// Scala STM (stm library)
import scala.concurrent.stm._

val accountA = Ref(1000)
val accountB = Ref(2000)

atomic { implicit txn =>
  accountA -= 100
  accountB += 100
}

// Or Cats Effect STM
import cats.effect.IO
import cats.effect.std.{Ref => CatsRef}

val program = for {
  accountA <- CatsRef[IO].of(1000)
  accountB <- CatsRef[IO].of(2000)
  _ <- (
    accountA.update(_ - 100),
    accountB.update(_ + 100)
  ).parTupled
} yield ()
```

### Agents → Akka Actors

**Clojure:**
```clojure
(def logger (agent []))

(send logger conj "Log entry 1")
(send logger conj "Log entry 2")

(await logger)
@logger  ;; => ["Log entry 1" "Log entry 2"]
```

**Scala:**
```scala
// Akka Typed Actors
import akka.actor.typed._
import akka.actor.typed.scaladsl.Behaviors

sealed trait LogMessage
case class AddEntry(entry: String) extends LogMessage
case class GetEntries(replyTo: ActorRef[List[String]]) extends LogMessage

def logger(entries: List[String]): Behavior[LogMessage] = {
  Behaviors.receive { (context, message) =>
    message match {
      case AddEntry(entry) =>
        logger(entries :+ entry)
      case GetEntries(replyTo) =>
        replyTo ! entries
        Behaviors.same
    }
  }
}

val system = ActorSystem(logger(List.empty), "logger")
system ! AddEntry("Log entry 1")
system ! AddEntry("Log entry 2")
```

### Futures

**Clojure:**
```clojure
(def result (future
              (Thread/sleep 1000)
              42))

@result  ;; Blocks until complete
```

**Scala:**
```scala
import scala.concurrent.Future
import scala.concurrent.ExecutionContext.Implicits.global

val result = Future {
  Thread.sleep(1000)
  42
}

// Await (blocking)
import scala.concurrent.Await
import scala.concurrent.duration._

Await.result(result, 2.seconds)

// Or use callbacks (non-blocking)
result.foreach(println)

// Or for-comprehension
val combined = for {
  a <- Future(10)
  b <- Future(20)
} yield a + b
```

---

## Platform & Performance

### JVM Optimization

Both Clojure and Scala run on JVM, but Scala can be more performant with proper type usage:

**Performance considerations:**

| Aspect | Clojure | Scala | Notes |
|--------|---------|-------|-------|
| Boxing overhead | Higher (dynamic) | Lower (primitives) | Scala specialization reduces boxing |
| Method dispatch | Dynamic (slower) | Static or dynamic | Scala pattern matching is faster than multimethods |
| Collection operations | Generic | Specialized | Scala collections can be optimized per type |
| Lazy evaluation | Lazy sequences | Streams/LazyList | Both are lazy, similar performance |
| Type erasure | N/A (dynamic) | Yes (generics) | Both have JVM type erasure |

**Optimization patterns:**

```scala
// Use specialized collections for primitives
val ints: Array[Int] = Array(1, 2, 3)  // No boxing
val doubles: Vector[Double] = Vector(1.0, 2.0)  // Specialized

// Use @specialized for generic code
def sum[@specialized(Int, Long, Double) A: Numeric](list: List[A]): A = {
  list.sum
}

// Use tail recursion
@scala.annotation.tailrec
def factorial(n: Int, acc: Int = 1): Int = {
  if (n <= 1) acc
  else factorial(n - 1, n * acc)
}

// Use views for lazy evaluation
val result = (1 to 1000000).view
  .map(_ * 2)
  .filter(_ > 100)
  .take(10)
  .toList  // Only 10 elements processed
```

---

## Common Pitfalls

1. **Treating Everything as Maps**
   - Clojure: Maps everywhere
   - Scala mistake: Using `Map[String, Any]` instead of case classes
   - Fix: Use case classes for structured data, sealed traits for variants

2. **Ignoring Static Types**
   - Clojure: Dynamic typing
   - Scala mistake: Avoiding types with excessive `Any`
   - Fix: Embrace Scala's type system; let compiler help

3. **Missing nil vs. None**
   - Clojure: `nil` is pervasive and safe
   - Scala mistake: Using `null` instead of `Option`
   - Fix: Always use `Option[A]` for nullable values

4. **Over-using Mutable Collections**
   - Clojure: Immutable by default
   - Scala mistake: Using mutable collections from `scala.collection.mutable`
   - Fix: Prefer immutable collections; use mutable only for performance-critical code

5. **Threading Macros → Complex Chains**
   - Clojure: `->>` for elegant pipelines
   - Scala mistake: Creating unreadable method chains
   - Fix: Break chains into intermediate vals; use for-comprehensions

6. **Macros Everywhere**
   - Clojure: Macros are common
   - Scala mistake: Trying to replicate with complex macros
   - Fix: Use higher-order functions, inline methods, or accept language differences

7. **Keyword Keys → String Keys**
   - Clojure: Keywords `:key` are optimized and fast
   - Scala mistake: Using strings for map keys in structured data
   - Fix: Use case classes or sealed traits for structured types

8. **Lazy Sequences → Streams Without Forcing**
   - Clojure: Lazy seqs can cause holding onto head
   - Scala: Similar with LazyList
   - Fix: Force realization when needed or use strict collections

9. **Multimethod Dispatch → Pattern Matching**
   - Clojure: Multimethods are open and extensible
   - Scala: Sealed traits are closed
   - Fix: Accept trade-off (extensibility vs. exhaustiveness checking)

10. **REPL-Driven → Compile-Driven**
    - Clojure: REPL-first development
    - Scala: More emphasis on compilation and types
    - Fix: Use sbt `~compile` for fast feedback; leverage Metals or IntelliJ

---

## Tooling

| Tool | Purpose | Notes |
|------|---------|-------|
| **sbt** | Build tool | Standard Scala build tool |
| **Mill** | Build tool | Modern alternative to sbt |
| **IntelliJ IDEA** | IDE | Best Scala IDE with refactoring support |
| **Metals** | Language server | For VS Code, Emacs, Vim |
| **Scalafmt** | Formatter | Code formatting |
| **Scalafix** | Linter | Automated refactoring and linting |
| **ScalaTest** | Testing | Most popular test framework |
| **ScalaCheck** | Property testing | Like Clojure test.check |
| **Wartremover** | Linter | Detect unsafe patterns |
| **Akka** | Concurrency | Actor model for concurrency |
| **Cats / Cats Effect** | FP library | Functional programming abstractions |
| **FS2** | Streaming | Functional streams (replaces core.async) |

---

## Examples

### Example 1: Simple - List Processing

**Before (Clojure):**
```clojure
(def numbers [1 2 3 4 5])

(defn process [nums]
  (->> nums
       (filter even?)
       (map #(* % 2))
       (reduce +)))

(process numbers)  ;; => 12
```

**After (Scala):**
```scala
val numbers = List(1, 2, 3, 4, 5)

def process(nums: List[Int]): Int = {
  nums
    .filter(_ % 2 == 0)
    .map(_ * 2)
    .sum
}

process(numbers)  // => 12
```

### Example 2: Medium - Error Handling with Either

**Before (Clojure):**
```clojure
(defn parse-int [s]
  (try
    {:ok (Integer/parseInt s)}
    (catch NumberFormatException e
      {:error "Invalid number"})))

(defn divide [a b]
  (if (zero? b)
    {:error "Division by zero"}
    {:ok (/ a b)}))

(defn compute [a-str b-str]
  (let [a-result (parse-int a-str)]
    (if (:error a-result)
      a-result
      (let [b-result (parse-int b-str)]
        (if (:error b-result)
          b-result
          (let [a (:ok a-result)
                b (:ok b-result)]
            (divide a b)))))))

(compute "10" "2")  ;; => {:ok 5}
(compute "10" "0")  ;; => {:error "Division by zero"}
(compute "abc" "2") ;; => {:error "Invalid number"}
```

**After (Scala):**
```scala
def parseInt(s: String): Either[String, Int] = {
  try {
    Right(s.toInt)
  } catch {
    case _: NumberFormatException => Left("Invalid number")
  }
}

def divide(a: Int, b: Int): Either[String, Int] = {
  if (b == 0) Left("Division by zero")
  else Right(a / b)
}

def compute(aStr: String, bStr: String): Either[String, Int] = {
  for {
    a <- parseInt(aStr)
    b <- parseInt(bStr)
    result <- divide(a, b)
  } yield result
}

compute("10", "2")   // => Right(5)
compute("10", "0")   // => Left("Division by zero")
compute("abc", "2")  // => Left("Invalid number")
```

### Example 3: Complex - ADT with Pattern Matching

**Before (Clojure):**
```clojure
;; Tagged map representation
(defn circle [radius]
  {:type :circle :radius radius})

(defn rectangle [width height]
  {:type :rectangle :width width :height height})

(defn triangle [base height]
  {:type :triangle :base base :height height})

;; Multimethod dispatch
(defmulti area :type)

(defmethod area :circle [{:keys [radius]}]
  (* Math/PI radius radius))

(defmethod area :rectangle [{:keys [width height]}]
  (* width height))

(defmethod area :triangle [{:keys [base height]}]
  (* 0.5 base height))

(defmulti perimeter :type)

(defmethod perimeter :circle [{:keys [radius]}]
  (* 2 Math/PI radius))

(defmethod perimeter :rectangle [{:keys [width height]}]
  (* 2 (+ width height)))

(defmethod perimeter :triangle [{:keys [base height]}]
  ;; Simplified - assuming right triangle
  (+ base height (Math/sqrt (+ (* base base) (* height height)))))

;; Usage
(def shapes
  [(circle 5)
   (rectangle 4 6)
   (triangle 3 4)])

(defn total-area [shapes]
  (reduce + (map area shapes)))

(defn describe-shape [shape]
  (let [a (area shape)
        p (perimeter shape)]
    (str "Area: " (format "%.2f" a)
         ", Perimeter: " (format "%.2f" p))))

;; Results
(total-area shapes)  ;; => ~113.54
(map describe-shape shapes)
;; => ("Area: 78.54, Perimeter: 31.42"
;;     "Area: 24.00, Perimeter: 20.00"
;;     "Area: 6.00, Perimeter: 12.00")
```

**After (Scala):**
```scala
sealed trait Shape {
  def area: Double
  def perimeter: Double
}

case class Circle(radius: Double) extends Shape {
  def area: Double = math.Pi * radius * radius
  def perimeter: Double = 2 * math.Pi * radius
}

case class Rectangle(width: Double, height: Double) extends Shape {
  def area: Double = width * height
  def perimeter: Double = 2 * (width + height)
}

case class Triangle(base: Double, height: Double) extends Shape {
  def area: Double = 0.5 * base * height
  def perimeter: Double = {
    // Simplified - assuming right triangle
    base + height + math.sqrt(base * base + height * height)
  }
}

// Usage
val shapes = List(
  Circle(5),
  Rectangle(4, 6),
  Triangle(3, 4)
)

def totalArea(shapes: List[Shape]): Double = {
  shapes.map(_.area).sum
}

def describeShape(shape: Shape): String = {
  val a = shape.area
  val p = shape.perimeter
  f"Area: $a%.2f, Perimeter: $p%.2f"
}

// Results
totalArea(shapes)  // => 113.53981633974483
shapes.map(describeShape)
// => List(
//      "Area: 78.54, Perimeter: 31.42",
//      "Area: 24.00, Perimeter: 20.00",
//      "Area: 6.00, Perimeter: 12.00"
//    )

// Pattern matching variant
def describeShapeMatch(shape: Shape): String = shape match {
  case Circle(r) =>
    s"Circle with radius $r"
  case Rectangle(w, h) =>
    s"Rectangle ${w}x$h"
  case Triangle(b, h) =>
    s"Triangle with base $b and height $h"
}
```

---

## See Also

For more examples and patterns, see:
- `meta-convert-dev` - Foundational patterns with cross-language examples
- `convert-python-scala` - Similar dynamic → static conversion
- `convert-typescript-scala` - Another typed target language
- `lang-clojure-dev` - Clojure development patterns
- `lang-scala-dev` - Scala development patterns

Cross-cutting pattern skills:
- `patterns-concurrency-dev` - Async, channels, threads across languages
- `patterns-serialization-dev` - JSON, validation across languages
- `patterns-metaprogramming-dev` - Macros, compile-time code generation
