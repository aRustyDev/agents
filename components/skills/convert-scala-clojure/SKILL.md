---
name: convert-scala-clojure
description: Convert Scala code to idiomatic Clojure. Use when migrating Scala projects to Clojure, translating Scala patterns to functional Clojure idioms, or refactoring Scala codebases into Clojure. Extends meta-convert-dev with Scala-to-Clojure specific patterns.
---

# Convert Scala to Clojure

Convert Scala code to idiomatic Clojure. This skill extends `meta-convert-dev` with Scala-to-Clojure specific type mappings, idiom translations, and tooling.

## This Skill Extends

- `meta-convert-dev` - Foundational conversion patterns (APTV workflow, testing strategies)

For general concepts like the Analyze → Plan → Transform → Validate workflow, testing strategies, and common pitfalls, see the meta-skill first.

## This Skill Adds

- **Type mappings**: Scala types → Clojure data structures
- **Idiom translations**: Scala patterns → idiomatic Clojure
- **Error handling**: Scala Try/Either/Option → Clojure error patterns
- **Concurrency patterns**: Scala Futures/Akka → Clojure atoms/agents/core.async
- **Type system**: Static typing → dynamic typing with spec

## This Skill Does NOT Cover

- General conversion methodology - see `meta-convert-dev`
- Scala language fundamentals - see `lang-scala-dev`
- Clojure language fundamentals - see `lang-clojure-dev`
- Reverse conversion (Clojure → Scala) - see `convert-clojure-scala`

---

## Quick Reference

| Scala | Clojure | Notes |
|-------|---------|-------|
| `val x = 42` | `(def x 42)` | Immutable binding |
| `case class User(name: String)` | `(defrecord User [name])` | Data structure |
| `List(1, 2, 3)` | `'(1 2 3)` or `[1 2 3]` | Sequence (prefer vectors) |
| `Vector(1, 2, 3)` | `[1 2 3]` | Indexed collection |
| `Map("a" -> 1)` | `{"a" 1}` | Hash map |
| `Set(1, 2, 3)` | `#{1 2 3}` | Hash set |
| `Option[A]` | `nil` or value | Nullable handling |
| `Either[L, R]` | Return value or throw | Error handling |
| `Try[A]` | `(try ... (catch ...))` | Exception handling |
| `for { x <- xs } yield x` | `(for [x xs] x)` | Comprehension |
| `xs.map(f)` | `(map f xs)` | Transform sequence |
| `xs.filter(p)` | `(filter p xs)` | Filter sequence |

## When Converting Code

1. **Analyze Scala structure** - understand type hierarchy and patterns
2. **Map types to data** - Scala ADTs → Clojure maps/records
3. **Remove type annotations** - trust dynamic typing, add spec where needed
4. **Adopt Clojure idioms** - don't write "Scala code in Clojure syntax"
5. **Embrace simplicity** - leverage Clojure's data-first philosophy
6. **Test thoroughly** - dynamic typing requires comprehensive tests

---

## Type System Mapping

### Primitive Types

| Scala | Clojure | Notes |
|-------|---------|-------|
| `Int` | `Long` | Clojure defaults to Long for integers |
| `Long` | `Long` | Direct mapping |
| `Float` | `Double` | Clojure uses Double for decimals |
| `Double` | `Double` | Direct mapping |
| `Boolean` | `true`/`false` | Lowercase in Clojure |
| `String` | `String` | Both use JVM strings |
| `Char` | `\c` | Character literal with backslash |
| `Unit` | `nil` | No-value representation |
| `Nothing` | - | No equivalent (use exceptions) |

### Collection Types

| Scala | Clojure | Notes |
|-------|---------|-------|
| `List[A]` | `(list ...)` | Linked list (rarely used) |
| `Vector[A]` | `[...]` | Preferred indexed sequence |
| `Seq[A]` | `seq` | Abstract sequence |
| `Array[A]` | `(into-array ...)` | Java array interop |
| `Map[K, V]` | `{k v ...}` | Hash map (default) |
| `Set[A]` | `#{...}` | Hash set |
| `Tuple2[A, B]` | `[a b]` | Vector as tuple |
| `Tuple3[A, B, C]` | `[a b c]` | Vector as tuple |

### Composite Types

| Scala | Clojure | Notes |
|-------|---------|-------|
| `case class` | `defrecord` | Named data structure |
| `sealed trait` | Map with `:type` key | ADT via tagged maps |
| `trait` | Protocol | Interface definition |
| `object` | Namespace vars | Singleton via module |
| `class` | `deftype` | Rarely needed |
| `type alias` | - | No type aliases (use comments) |

---

## Idiom Translation

### Pattern: Case Classes → Records/Maps

**Scala:**
```scala
case class User(id: Int, name: String, email: String)

val user = User(123, "Alice", "alice@example.com")
val updated = user.copy(email = "new@example.com")
```

**Clojure:**
```clojure
;; Option 1: defrecord (typed, field access)
(defrecord User [id name email])

(def user (->User 123 "Alice" "alice@example.com"))
(def updated (assoc user :email "new@example.com"))

;; Option 2: plain map (idiomatic, flexible)
(def user {:id 123 :name "Alice" :email "alice@example.com"})
(def updated (assoc user :email "new@example.com"))
```

**Why this translation:**
- Clojure prefers plain maps for most data
- `defrecord` is for performance-critical code or when protocols are needed
- `assoc` is the universal update mechanism
- Keywords (`:email`) are the idiomatic keys

### Pattern: Option → nil Checks

**Scala:**
```scala
val maybeUser: Option[User] = findUser(id)
val name = maybeUser.map(_.name).getOrElse("Anonymous")
val result = maybeUser.map(process).getOrElse(default)
```

**Clojure:**
```clojure
(let [maybe-user (find-user id)]
  ;; Direct nil check (idiomatic)
  (def name (if maybe-user (:name maybe-user) "Anonymous"))

  ;; Or with threading
  (def name (or (some-> maybe-user :name) "Anonymous"))

  ;; Process or default
  (def result (if maybe-user (process maybe-user) default)))
```

**Why this translation:**
- Clojure uses `nil` as the absence of value
- `if` and `or` handle nil naturally
- `some->` threads through nil-safe operations
- No need for Option wrapper

### Pattern: Either → Error Handling

**Scala:**
```scala
def divide(a: Int, b: Int): Either[String, Int] = {
  if (b == 0) Left("Division by zero")
  else Right(a / b)
}

val result = divide(10, 2) match {
  case Right(value) => s"Result: $value"
  case Left(error) => s"Error: $error"
}
```

**Clojure:**
```clojure
(defn divide [a b]
  (if (zero? b)
    {:error "Division by zero"}
    {:value (/ a b)}))

;; Pattern match on result
(let [result (divide 10 2)]
  (if (:error result)
    (str "Error: " (:error result))
    (str "Result: " (:value result))))

;; Or use exceptions for errors
(defn divide! [a b]
  (when (zero? b)
    (throw (ex-info "Division by zero" {:a a :b b})))
  (/ a b))

(try
  (str "Result: " (divide! 10 2))
  (catch Exception e
    (str "Error: " (.getMessage e))))
```

**Why this translation:**
- Clojure prefers maps with `:error`/`:value` keys
- Or throw exceptions for exceptional cases
- `ex-info` attaches data to exceptions
- No need for Either wrapper

### Pattern: Try → Exception Handling

**Scala:**
```scala
import scala.util.{Try, Success, Failure}

val result = Try {
  parseFile(path)
}.recover {
  case _: FileNotFoundException => "default.txt"
}.toEither
```

**Clojure:**
```clojure
(defn safe-parse-file [path]
  (try
    {:value (parse-file path)}
    (catch java.io.FileNotFoundException e
      {:value "default.txt"})
    (catch Exception e
      {:error (.getMessage e)})))

;; Or use exceptions directly
(defn parse-file-or-default [path]
  (try
    (parse-file path)
    (catch java.io.FileNotFoundException e
      "default.txt")))
```

**Why this translation:**
- `try/catch` is the primary error mechanism
- Return error maps for domain errors
- Throw exceptions for unexpected errors
- Keep it simple - avoid wrapping everything

### Pattern: For-Comprehensions → for

**Scala:**
```scala
val result = for {
  x <- Some(1)
  y <- Some(2)
  z <- Some(3)
} yield x + y + z

val pairs = for {
  x <- List(1, 2, 3)
  y <- List(10, 20)
  if x % 2 == 0
} yield (x, y)
```

**Clojure:**
```clojure
;; Option monad - just use nil checks
(let [x 1
      y 2
      z 3]
  (when (and x y z)
    (+ x y z)))

;; List comprehension - direct translation
(for [x [1 2 3]
      y [10 20]
      :when (even? x)]
  [x y])
;; => ([2 10] [2 20])
```

**Why this translation:**
- Clojure's `for` is list comprehension, not monadic
- Use explicit nil checks instead of Option monad
- `:when` for filtering
- Return vectors `[x y]` instead of tuples

### Pattern: Pattern Matching → cond/case

**Scala:**
```scala
sealed trait Result
case class Success(value: Int) extends Result
case class Failure(error: String) extends Result
case object Pending extends Result

def handle(result: Result): String = result match {
  case Success(value) => s"Got: $value"
  case Failure(error) => s"Error: $error"
  case Pending => "Waiting..."
}
```

**Clojure:**
```clojure
;; Tagged maps for ADTs
(defn make-success [value]
  {:type :success :value value})

(defn make-failure [error]
  {:type :failure :error error})

(def pending {:type :pending})

(defn handle [result]
  (case (:type result)
    :success (str "Got: " (:value result))
    :failure (str "Error: " (:error result))
    :pending "Waiting..."))

;; Or use cond for complex conditions
(defn handle-cond [result]
  (cond
    (= (:type result) :success) (str "Got: " (:value result))
    (= (:type result) :failure) (str "Error: " (:error result))
    :else "Waiting..."))
```

**Why this translation:**
- Use maps with `:type` key for ADT variants
- `case` for simple dispatch on values
- `cond` for complex conditions
- No exhaustiveness checking (rely on tests)

### Pattern: Implicits → Dynamic Vars/Protocols

**Scala:**
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

print(42)      // Uses intShow
print("hello") // Uses stringShow
```

**Clojure:**
```clojure
;; Option 1: Protocols (most similar to type classes)
(defprotocol Show
  (show [this]))

(extend-type Long
  Show
  (show [n] (str n)))

(extend-type String
  Show
  (show [s] (str "'" s "'")))

(println (show 42))      ;; "42"
(println (show "hello")) ;; "'hello'"

;; Option 2: Multimethods (more flexible)
(defmulti show-value class)

(defmethod show-value Long [n]
  (str n))

(defmethod show-value String [s]
  (str "'" s "'"))

(show-value 42)      ;; "42"
(show-value "hello") ;; "'hello'"
```

**Why this translation:**
- Protocols are closest to Scala type classes
- Multimethods provide runtime polymorphism
- No implicit resolution - explicit calls
- Extend existing types without modification

### Pattern: Traits → Protocols

**Scala:**
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

**Clojure:**
```clojure
(defprotocol Logging
  (log [this message]))

(defprotocol Auditing
  (audit [this event]))

(defrecord Service []
  Logging
  (log [_ message]
    (println "[LOG]" message))

  Auditing
  (audit [_ event]
    (println "[AUDIT]" event)))

(def service (->Service))
(log service "Application starting")
(audit service "User login")
```

**Why this translation:**
- Protocols define interfaces
- `defrecord` implements multiple protocols
- Explicit protocol calls
- No mixin linearization complexity

---

## Error Handling

### Scala Error Model → Clojure Error Model

**Scala** provides three main error handling approaches:
- `Option[A]` for potentially absent values
- `Either[E, A]` for domain errors with context
- `Try[A]` for exception wrapping

**Clojure** uses simpler approaches:
- `nil` for absent values
- Exception throwing for errors
- Maps with `:error` keys for domain errors

**Comparison:**

| Scala | Clojure | When to Use |
|-------|---------|-------------|
| `Option[A]` | `nil` or value | Absence of value |
| `Either[E, A]` | `{:error e}` or `{:value a}` | Domain errors with context |
| `Try[A]` | `try/catch` | Exception handling |

**Example conversion:**

**Scala:**
```scala
def findUser(id: Int): Option[User] = {
  users.find(_.id == id)
}

def validateEmail(email: String): Either[String, String] = {
  if (email.contains("@")) Right(email)
  else Left("Invalid email format")
}

def parseConfig(path: String): Try[Config] = Try {
  JSON.parse(readFile(path))
}
```

**Clojure:**
```clojure
(defn find-user [id]
  (first (filter #(= (:id %) id) users)))
;; Returns user or nil

(defn validate-email [email]
  (if (str/includes? email "@")
    {:value email}
    {:error "Invalid email format"}))

(defn parse-config [path]
  (try
    {:value (json/parse-string (slurp path) true)}
    (catch Exception e
      {:error (.getMessage e)})))
```

---

## Concurrency Patterns

### Scala Concurrency → Clojure Concurrency

**Scala** offers multiple concurrency models:
- `Future` for async operations
- Akka actors for message passing
- Cats Effect / ZIO for functional effects

**Clojure** provides:
- Atoms for synchronous state updates
- Refs for coordinated transactions
- Agents for asynchronous updates
- `core.async` for CSP-style concurrency

### Future → Atom Pattern

**Scala:**
```scala
import scala.concurrent.Future
import scala.concurrent.ExecutionContext.Implicits.global

val counter = new AtomicInteger(0)

val future1 = Future {
  counter.incrementAndGet()
}

val future2 = Future {
  counter.incrementAndGet()
}
```

**Clojure:**
```clojure
(def counter (atom 0))

(future
  (swap! counter inc))

(future
  (swap! counter inc))

;; Wait for completion
@counter ;; Reads current value
```

**Why this translation:**
- Atoms provide synchronous, atomic updates
- `swap!` ensures thread-safe modifications
- Futures for async computation
- Simpler than Scala's Future

### Akka Actors → Agents

**Scala:**
```scala
import akka.actor._

class Logger extends Actor {
  var logs: List[String] = List.empty

  def receive = {
    case msg: String =>
      logs = msg :: logs
      println(s"Logged: $msg")
  }
}

val logger = system.actorOf(Props[Logger])
logger ! "Log message 1"
logger ! "Log message 2"
```

**Clojure:**
```clojure
(def logger (agent []))

(send logger conj "Log message 1")
(send logger conj "Log message 2")

;; Wait for completion
(await logger)

@logger ;; Read current state
```

**Why this translation:**
- Agents provide asynchronous state updates
- `send` queues actions for execution
- Simpler than full actor systems
- For complex actor patterns, consider using a library

### core.async Channels

**Scala (using Akka Streams):**
```scala
import akka.stream.scaladsl._

val source = Source(1 to 100)
val sink = Sink.foreach[Int](println)

source
  .filter(_ % 2 == 0)
  .map(_ * 2)
  .runWith(sink)
```

**Clojure:**
```clojure
(require '[clojure.core.async :as async])

(let [ch (async/chan 10)]
  (async/go
    (doseq [n (range 1 101)]
      (async/>! ch n)))

  (async/go-loop []
    (when-let [n (async/<! ch)]
      (when (even? n)
        (println (* n 2)))
      (recur))))
```

**Why this translation:**
- `core.async` provides CSP-style channels
- `go` blocks for lightweight threads
- `>!` to put, `<!` to take
- Compositional pipeline style

---

## Common Pitfalls

### 1. Type Erasure vs Dynamic Typing

**Problem:** Scala relies on compile-time type checking

```scala
def process[A](value: A): String = value match {
  case s: String => s.toUpperCase
  case i: Int => (i * 2).toString
  case _ => "unknown"
}
```

**Clojure Solution:** Use runtime type checks

```clojure
(defn process [value]
  (cond
    (string? value) (str/upper-case value)
    (int? value) (str (* value 2))
    :else "unknown"))
```

**Why this matters:**
- No compile-time type safety
- Must rely on tests
- Runtime errors instead of compile errors

### 2. Null Safety vs nil Everywhere

**Problem:** Scala Option prevents NullPointerException

```scala
val name: Option[String] = Some("Alice")
name.map(_.toUpperCase) // Safe
```

**Clojure Challenge:**

```clojure
(def name "Alice")
(.toUpperCase name) ; Safe if name is never nil

;; Unsafe if name could be nil
(.toUpperCase nil) ; NullPointerException!

;; Must guard explicitly
(when name
  (.toUpperCase name))

;; Or use some->
(some-> name .toUpperCase)
```

**Why this matters:**
- No Option wrapper to prevent NPE
- Must remember to check nil
- More runtime errors possible

### 3. Immutability Default vs Explicit

**Problem:** Scala immutable by default, but mutable exists

```scala
val immutable = List(1, 2, 3)
var mutable = 0 // Explicit mutability
```

**Clojure:**

```clojure
(def data [1 2 3]) ; Immutable
(def counter (atom 0)) ; Mutable state container

;; NO way to have mutable variable
;; Must use atoms/refs/agents
```

**Why this matters:**
- Clojure more strictly immutable
- State changes via reference types only
- Different mental model

### 4. Case Class Pattern Matching vs Maps

**Problem:** Scala sealed traits ensure exhaustive matching

```scala
sealed trait Status
case object Active extends Status
case object Inactive extends Status

def handle(s: Status) = s match {
  case Active => "active"
  case Inactive => "inactive"
  // Compiler ensures all cases covered
}
```

**Clojure:**

```clojure
(defn handle [status]
  (case status
    :active "active"
    :inactive "inactive"
    ;; No compiler check - must test!
    ))

;; Missing case causes runtime error
(handle :pending) ; IllegalArgumentException
```

**Why this matters:**
- No exhaustiveness checking
- Runtime errors for missing cases
- Must have comprehensive tests

### 5. Lazy Collections vs Seq Realization

**Problem:** Scala collections are strict by default

```scala
val result = list.map(expensiveFn) // Evaluated immediately
```

**Clojure:**

```clojure
(def result (map expensive-fn list)) ; LAZY - not evaluated yet!

;; Must realize explicitly
(doall (map expensive-fn list)) ; Force evaluation
(vec (map expensive-fn list))   ; Realize into vector
```

**Why this matters:**
- Unexpected laziness can cause bugs
- Multiple realizations of same lazy seq
- Must understand when to force evaluation

---

## Tooling

| Tool | Scala | Clojure | Notes |
|------|-------|---------|-------|
| **Build** | sbt, Mill | Leiningen, tools.deps | Clojure simpler |
| **REPL** | sbt console, Ammonite | lein repl, clj | Clojure REPL-first |
| **Testing** | ScalaTest, specs2 | clojure.test, Midje | Similar features |
| **Property testing** | ScalaCheck | test.check | Similar approach |
| **Dependency mgmt** | Maven Central | Clojars, Maven Central | Clojure uses both |
| **Type checking** | Scalac | - | No static types in Clojure |
| **Spec validation** | - | clojure.spec | Runtime validation |
| **AST manipulation** | scala.meta | - | Macros instead |
| **Async** | Akka, Cats Effect | core.async | Different models |

---

## Examples

Examples progress from simple to complex, showing real-world conversion patterns.

### Example 1: Simple - Data Classes

**Before (Scala):**
```scala
case class Point(x: Double, y: Double) {
  def distance(other: Point): Double = {
    val dx = x - other.x
    val dy = y - other.y
    math.sqrt(dx * dx + dy * dy)
  }
}

val p1 = Point(0, 0)
val p2 = Point(3, 4)
val dist = p1.distance(p2) // 5.0
```

**After (Clojure):**
```clojure
;; Option 1: Plain map (idiomatic)
(defn make-point [x y]
  {:x x :y y})

(defn distance [p1 p2]
  (let [dx (- (:x p1) (:x p2))
        dy (- (:y p1) (:y p2))]
    (Math/sqrt (+ (* dx dx) (* dy dy)))))

(def p1 (make-point 0 0))
(def p2 (make-point 3 4))
(distance p1 p2) ; 5.0

;; Option 2: defrecord (if needed)
(defrecord Point [x y])

(defn distance [^Point p1 ^Point p2]
  (let [dx (- (.x p1) (.x p2))
        dy (- (.y p1) (.y p2))]
    (Math/sqrt (+ (* dx dx) (* dy dy)))))

(def p1 (->Point 0 0))
(def p2 (->Point 3 4))
(distance p1 p2) ; 5.0
```

### Example 2: Medium - Option/Either Handling

**Before (Scala):**
```scala
case class User(id: Int, name: String, email: Option[String])

def findUser(id: Int): Option[User] = {
  users.find(_.id == id)
}

def validateEmail(email: String): Either[String, String] = {
  if (email.contains("@") && email.length > 3)
    Right(email)
  else
    Left("Invalid email format")
}

def updateEmail(userId: Int, newEmail: String): Either[String, User] = {
  for {
    user <- findUser(userId).toRight("User not found")
    validEmail <- validateEmail(newEmail)
  } yield user.copy(email = Some(validEmail))
}

// Usage
updateEmail(123, "alice@example.com") match {
  case Right(user) => println(s"Updated: ${user.name}")
  case Left(error) => println(s"Error: $error")
}
```

**After (Clojure):**
```clojure
(defn make-user
  ([id name] {:id id :name name})
  ([id name email] {:id id :name name :email email}))

(def users
  [(make-user 123 "Alice" "alice@old.com")
   (make-user 456 "Bob")])

(defn find-user [id]
  (first (filter #(= (:id %) id) users)))

(defn validate-email [email]
  (if (and (str/includes? email "@")
           (> (count email) 3))
    {:value email}
    {:error "Invalid email format"}))

(defn update-email [user-id new-email]
  (if-let [user (find-user user-id)]
    (let [validation (validate-email new-email)]
      (if (:error validation)
        validation
        {:value (assoc user :email (:value validation))}))
    {:error "User not found"}))

;; Usage
(let [result (update-email 123 "alice@example.com")]
  (if (:error result)
    (println "Error:" (:error result))
    (println "Updated:" (:name (:value result)))))
```

### Example 3: Complex - Concurrent Processing

**Before (Scala):**
```scala
import scala.concurrent.{Future, Await}
import scala.concurrent.duration._
import scala.concurrent.ExecutionContext.Implicits.global

case class Record(id: Int, data: String)
case class Result(id: Int, processed: String, timestamp: Long)

object DataProcessor {
  def fetchRecords(source: String): Future[List[Record]] = Future {
    // Simulate fetching from database
    Thread.sleep(100)
    List(
      Record(1, "data1"),
      Record(2, "data2"),
      Record(3, "data3")
    )
  }

  def processRecord(record: Record): Future[Result] = Future {
    // Simulate expensive processing
    Thread.sleep(50)
    Result(
      record.id,
      record.data.toUpperCase,
      System.currentTimeMillis()
    )
  }

  def saveResult(result: Result): Future[Unit] = Future {
    // Simulate saving to database
    Thread.sleep(20)
    println(s"Saved: ${result.id} -> ${result.processed}")
  }

  def pipeline(source: String): Future[List[Unit]] = {
    for {
      records <- fetchRecords(source)
      results <- Future.sequence(records.map(processRecord))
      saved <- Future.sequence(results.map(saveResult))
    } yield saved
  }
}

// Usage
val future = DataProcessor.pipeline("source.db")
Await.result(future, 10.seconds)
```

**After (Clojure):**
```clojure
(ns data-processor
  (:require [clojure.core.async :as async]))

(defn make-record [id data]
  {:id id :data data})

(defn make-result [id processed timestamp]
  {:id id :processed processed :timestamp timestamp})

(defn fetch-records [source]
  (future
    ;; Simulate fetching from database
    (Thread/sleep 100)
    [(make-record 1 "data1")
     (make-record 2 "data2")
     (make-record 3 "data3")]))

(defn process-record [record]
  (future
    ;; Simulate expensive processing
    (Thread/sleep 50)
    (make-result
      (:id record)
      (str/upper-case (:data record))
      (System/currentTimeMillis))))

(defn save-result [result]
  (future
    ;; Simulate saving to database
    (Thread/sleep 20)
    (println (str "Saved: " (:id result) " -> " (:processed result)))))

(defn pipeline [source]
  (let [records @(fetch-records source)
        results (doall (map #(deref (process-record %)) records))
        saved (doall (map #(deref (save-result %)) results))]
    saved))

;; Usage with error handling
(defn safe-pipeline [source]
  (try
    (pipeline source)
    (catch Exception e
      (println "Pipeline error:" (.getMessage e))
      nil)))

(safe-pipeline "source.db")

;; Alternative: Using core.async for more control
(defn async-pipeline [source]
  (let [records-ch (async/chan 10)
        results-ch (async/chan 10)]

    ;; Fetch records
    (async/go
      (let [records @(fetch-records source)]
        (doseq [record records]
          (async/>! records-ch record))
        (async/close! records-ch)))

    ;; Process records
    (async/go-loop []
      (when-let [record (async/<! records-ch)]
        (let [result @(process-record record)]
          (async/>! results-ch result))
        (recur)))

    ;; Save results
    (async/go-loop []
      (when-let [result (async/<! results-ch)]
        @(save-result result)
        (recur)))

    nil))
```

---

## See Also

For more examples and patterns, see:
- `meta-convert-dev` - Foundational patterns with cross-language examples
- `lang-scala-dev` - Scala development patterns
- `lang-clojure-dev` - Clojure development patterns

Cross-cutting pattern skills:
- `patterns-concurrency-dev` - Async, channels, threads across languages
- `patterns-serialization-dev` - JSON, validation, data formats
- `patterns-metaprogramming-dev` - Macros, implicits, code generation
