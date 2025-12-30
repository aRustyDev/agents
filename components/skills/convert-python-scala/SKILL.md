---
name: convert-python-scala
description: Convert Python code to idiomatic Scala. Use when migrating Python projects to Scala, translating Python patterns to Scala's hybrid OOP+FP paradigm, or refactoring Python codebases for type safety, JVM integration, and functional programming. Extends meta-convert-dev with Python-to-Scala specific patterns.
---

# Convert Python to Scala

Convert Python code to idiomatic Scala. This skill extends `meta-convert-dev` with Python-to-Scala specific type mappings, idiom translations, and tooling for transforming dynamic Python code into Scala's powerful hybrid OOP+FP paradigm on the JVM.

## This Skill Extends

- `meta-convert-dev` - Foundational conversion patterns (APTV workflow, testing strategies)

For general concepts like the Analyze → Plan → Transform → Validate workflow, testing strategies, and common pitfalls, see the meta-skill first.

## This Skill Adds

- **Type mappings**: Python types → Scala types (dynamic → static with inference)
- **Paradigm shift**: Imperative/OOP → Hybrid OOP+FP
- **Error handling**: Exceptions → Option/Either/Try pattern matching
- **Concurrency**: threading/asyncio → Futures/Akka actors
- **Metaprogramming**: Decorators → Scala 3 macros, implicit conversions
- **Serialization**: Pydantic → circe, upickle, case class derivation
- **Module system**: Python packages → Scala packages, objects, imports
- **Build/Deps**: pip/poetry → sbt, mill, build.sbt
- **Testing**: pytest → ScalaTest, MUnit, ScalaCheck
- **Dev Workflow**: Python REPL → Scala REPL, Ammonite, sbt console
- **FFI**: C extensions → JNI, JNA, Scala Native C interop

## This Skill Does NOT Cover

- General conversion methodology - see `meta-convert-dev`
- Python language fundamentals - see `lang-python-dev`
- Scala language fundamentals - see `lang-scala-dev`
- Reverse conversion (Scala → Python) - see `convert-scala-python`
- Advanced Scala libraries (Akka, Cats, ZIO) - see specialized skills

---

## Quick Reference

| Python | Scala | Notes |
|--------|-------|-------|
| `int` | `Int`, `Long`, `BigInt` | Fixed size or arbitrary precision |
| `float` | `Double` | Default floating point |
| `bool` | `Boolean` | Direct mapping |
| `str` | `String` | Java String |
| `list[T]` | `List[T]`, `Vector[T]` | Immutable by default |
| `tuple` | `(T, U, ...)` | Tuple types |
| `dict[K, V]` | `Map[K, V]` | Immutable by default |
| `set[T]` | `Set[T]` | Immutable by default |
| `None` | `Option[T]` / `None` | Explicit optional |
| `Union[T, U]` | `Either[T, U]` | Type-safe union |
| `@dataclass` | `case class` | Data classes with pattern matching |
| `def func()` | `def func(): Unit` | Functions |
| `class` | `class` / `trait` / `case class` | OOP + traits |
| Exception | `Try[T]`, `Either[L, R]` | Functional error handling |
| `async def` | `Future[T]`, `IO[T]` | Async/effect handling |

## When Converting Code

1. **Analyze Python semantics** - understand duck typing, mutable state, exceptions
2. **Embrace immutability** - prefer `val` over `var`, immutable collections
3. **Use case classes** for data - automatic equals, hashCode, copy, pattern matching
4. **Pattern match** instead of type checks and isinstance
5. **Option, Try, Either** for null/error handling, not exceptions
6. **For-comprehensions** for sequential operations (flatMap chains)
7. **Traits and mixins** for composition, not deep inheritance
8. **Type inference** - let compiler infer types where clear
9. **Test equivalence** - same inputs → same outputs
10. **Leverage JVM ecosystem** - vast library support

---

## Type System Mapping

### Primitive Types

| Python | Scala | Notes |
|--------|-------|-------|
| `int` | `Int` | 32-bit signed integer |
| `int` | `Long` | 64-bit signed integer |
| `int` | `BigInt` | Arbitrary precision (like Python) |
| `float` | `Double` | 64-bit IEEE 754 |
| `bool` | `Boolean` | true/false |
| `str` | `String` | Immutable UTF-16 (Java String) |
| `bytes` | `Array[Byte]` | Mutable byte array |
| `bytearray` | `Array[Byte]` | Mutable byte array |
| `None` | `None` (Option) | Type-safe null |

**Integer Precision Note**: Python's `int` has arbitrary precision and never overflows. Scala's `Int` and `Long` are fixed-size. Use `BigInt` for Python-like behavior:

```scala
// Python arbitrary precision
val pythonLike: BigInt = BigInt(10).pow(100)

// Scala fixed-size (can overflow)
val scalaInt: Int = 1000000000  // OK
val overflow: Int = Int.MaxValue + 1  // Wraps around!
```

### Collection Types

| Python | Scala | Mutability | Notes |
|--------|-------|-----------|-------|
| `list[T]` | `List[T]` | Immutable | Linked list, O(1) prepend |
| `list[T]` | `Vector[T]` | Immutable | Better random access |
| `list[T]` | `ArrayBuffer[T]` | Mutable | Like Python list |
| `tuple` | `(T, U, V)` | Immutable | Fixed-size tuples |
| `dict[K, V]` | `Map[K, V]` | Immutable | Hash map |
| `dict[K, V]` | `mutable.Map[K, V]` | Mutable | Like Python dict |
| `set[T]` | `Set[T]` | Immutable | Hash set |
| `set[T]` | `mutable.Set[T]` | Mutable | Like Python set |
| `frozenset[T]` | `Set[T]` | Immutable | Default is immutable |
| `deque` | `Queue[T]` | Mutable | Double-ended queue |

**Collection Philosophy Difference**:

```python
# Python: Mutable by default
my_list = [1, 2, 3]
my_list.append(4)  # In-place mutation
```

```scala
// Scala: Immutable by default
val myList = List(1, 2, 3)
val newList = myList :+ 4  // Creates new list

// Mutable collections require explicit import
import scala.collection.mutable
val buffer = mutable.ArrayBuffer(1, 2, 3)
buffer += 4  // In-place mutation
```

### Composite Types

| Python | Scala | Notes |
|--------|-------|-------|
| `@dataclass` | `case class` | Immutable data with pattern matching |
| `class` | `class` | Mutable objects |
| `class` | `trait` | Interface with implementation |
| `typing.Protocol` | `trait` | Structural types |
| `typing.TypedDict` | `case class` | Named fields with types |
| `typing.NamedTuple` | `case class` | Named tuples |
| `enum.Enum` | `sealed trait` + case objects | ADTs |
| `typing.Literal` | `sealed trait` | Literal types |
| `typing.Union[T, U]` | `Either[T, U]` | Type-safe union |
| `typing.Optional[T]` | `Option[T]` | Nullable handling |
| `typing.Callable` | `Function1[A, B]` | Function types |
| `typing.Generic[T]` | Type parameters `[T]` | Generic types |

### Type Annotations → Type Parameters + Bounds

| Python | Scala | Notes |
|--------|-------|-------|
| `def f(x: T) -> T` | `def f[T](x: T): T` | Generic function |
| `x: Iterable[T]` | `x: Iterable[T]` | Scala has Iterable |
| `x: Sequence[T]` | `x: Seq[T]` | Sequence trait |
| `x: Any` | `x: Any` | Top type (avoid) |
| `x: object` | `x: AnyRef` | Reference types |
| `T extends Base` | `T <: Base` | Upper type bound |
| `T` (unconstrained) | `T` | Type parameter |

---

## APTV Workflow for Python → Scala

### 1. Analyze Phase

Before converting, understand Python-specific features:

```python
# Analyze this Python code
class UserService:
    def __init__(self, db):
        self.db = db
        self.cache = {}  # Mutable state

    def get_user(self, user_id):
        if user_id in self.cache:
            return self.cache[user_id]

        user = self.db.query(f"SELECT * FROM users WHERE id={user_id}")
        if user is None:
            raise UserNotFoundError(f"User {user_id} not found")

        self.cache[user_id] = user
        return user
```

**Key observations**:
- Mutable instance state (`self.cache`)
- None checking
- Exception-based error handling
- String interpolation
- Duck typing (db assumed to have .query())

### 2. Plan Phase

Design Scala equivalent:

```scala
// Type mappings
// Python dict -> Map[Int, User]
// Python None -> Option[User]
// Exception -> Either[UserError, User] or Try[User]

// Architecture decisions:
// - Immutable service with explicit cache parameter
// - Or use functional cache (State monad, cats.effect.Ref)
// - Database interface as trait
// - Error as ADT (sealed trait)
```

### 3. Transform Phase

Idiomatic Scala implementation:

```scala
// Define error ADT
sealed trait UserError
case class UserNotFound(userId: Int) extends UserError
case class DatabaseError(message: String) extends UserError

// Database trait (replaces duck typing)
trait Database {
  def query(sql: String): Option[User]
}

// Immutable service
class UserService(db: Database) {
  // Cache as parameter for immutability
  def getUser(userId: Int, cache: Map[Int, User]): Either[UserError, (User, Map[Int, User])] = {
    cache.get(userId) match {
      case Some(user) =>
        Right((user, cache))

      case None =>
        db.query(s"SELECT * FROM users WHERE id=$userId") match {
          case Some(user) =>
            Right((user, cache + (userId -> user)))

          case None =>
            Left(UserNotFound(userId))
        }
    }
  }
}

// Or with functional effects (cats-effect)
import cats.effect.IO
import cats.effect.Ref

class UserServiceF(db: Database, cache: Ref[IO, Map[Int, User]]) {
  def getUser(userId: Int): IO[Either[UserError, User]] = {
    for {
      cachedUser <- cache.get.map(_.get(userId))
      result <- cachedUser match {
        case Some(user) =>
          IO.pure(Right(user))

        case None =>
          db.query(s"SELECT * FROM users WHERE id=$userId") match {
            case Some(user) =>
              cache.update(_ + (userId -> user)).as(Right(user))
            case None =>
              IO.pure(Left(UserNotFound(userId)))
          }
      }
    } yield result
  }
}
```

### 4. Validate Phase

Test equivalence:

```scala
import org.scalatest.flatspec.AnyFlatSpec
import org.scalatest.matchers.should.Matchers

class UserServiceSpec extends AnyFlatSpec with Matchers {
  "UserService" should "return cached user" in {
    val mockDb = new Database {
      def query(sql: String): Option[User] = None
    }

    val service = new UserService(mockDb)
    val user = User(1, "Alice")
    val cache = Map(1 -> user)

    val Right((result, _)) = service.getUser(1, cache)
    result should be(user)
  }

  it should "query database when not cached" in {
    val user = User(2, "Bob")
    val mockDb = new Database {
      def query(sql: String): Option[User] = Some(user)
    }

    val service = new UserService(mockDb)
    val Right((result, newCache)) = service.getUser(2, Map.empty)

    result should be(user)
    newCache should contain key 2
  }

  it should "return error when user not found" in {
    val mockDb = new Database {
      def query(sql: String): Option[User] = None
    }

    val service = new UserService(mockDb)
    val Left(error) = service.getUser(999, Map.empty)

    error should be(UserNotFound(999))
  }
}
```

---

## Idiom Translation Patterns

### Pattern 1: None/Null Handling → Option

**Python:**
```python
# Optional chaining
user = get_user(user_id)
name = user.name if user else "Anonymous"

# Or with walrus operator
if user := get_user(user_id):
    process(user)
else:
    log_error("User not found")

# get with default
config_value = config.get("timeout", 30)
```

**Scala:**
```scala
// Option combinators
val name = getUser(userId)
  .map(_.name)
  .getOrElse("Anonymous")

// Pattern matching
getUser(userId) match {
  case Some(user) => process(user)
  case None => logError("User not found")
}

// For-comprehension (flatMap chain)
val fullName = for {
  user <- getUser(userId)
  profile <- user.profile
} yield s"${profile.firstName} ${profile.lastName}"

// getOrElse with default
val configValue = config.get("timeout").getOrElse(30)
```

**Why this translation:**
- Python uses truthiness and None; Scala uses explicit Option[T]
- Scala's Option provides safe combinators (map, flatMap, getOrElse, fold)
- Pattern matching makes intent explicit
- For-comprehensions chain multiple Option operations elegantly

### Pattern 2: List Comprehensions → For-Comprehensions

**Python:**
```python
# List comprehension
squared_evens = [x * x for x in numbers if x % 2 == 0]

# Nested comprehension
pairs = [(x, y) for x in xs for y in ys if x + y > 10]

# Generator expression
total = sum(x * x for x in numbers if x % 2 == 0)
```

**Scala:**
```scala
// For-comprehension with yield
val squaredEvens = for {
  x <- numbers
  if x % 2 == 0
} yield x * x

// Nested for-comprehension
val pairs = for {
  x <- xs
  y <- ys
  if x + y > 10
} yield (x, y)

// Method chaining (more idiomatic for simple cases)
val total = numbers.filter(_ % 2 == 0).map(x => x * x).sum

// Lazy evaluation with View
val lazyResult = numbers.view
  .filter(_ % 2 == 0)
  .map(x => x * x)
  .force  // Materialize
```

**Why this translation:**
- Python comprehensions are eager; Scala for-comprehensions desugar to map/flatMap
- Scala provides both for-comprehension and method chaining styles
- View provides lazy evaluation similar to Python generators
- For-comprehensions work with any type supporting map/flatMap (monads)

### Pattern 3: Dictionary Operations → Map Operations

**Python:**
```python
# Dictionary creation
user_ages = {user.name: user.age for user in users}

# Get with default
timeout = config.get("timeout", 30)

# Update (mutation)
cache[key] = value

# Merge dictionaries
combined = {**dict1, **dict2}
```

**Scala:**
```scala
// Map creation
val userAges = users.map(user => user.name -> user.age).toMap
// Or with for-comprehension
val userAges = (for {
  user <- users
} yield user.name -> user.age).toMap

// Get with default
val timeout = config.getOrElse("timeout", 30)

// Immutable update (creates new Map)
val newCache = cache + (key -> value)

// Mutable update
import scala.collection.mutable
val mutableCache = mutable.Map[String, Int]()
mutableCache(key) = value

// Merge maps
val combined = dict1 ++ dict2  // Right side wins on conflicts
```

**Why this translation:**
- Scala Map is immutable by default (Python dict is mutable)
- `+` operator for adding entries creates new Map
- `++` operator merges Maps
- Mutable Map available but requires explicit import
- getOrElse instead of .get() with default

### Pattern 4: Exception Handling → Try/Either/Option

**Python:**
```python
# Try-except
try:
    result = risky_operation()
except ValueError as e:
    logger.error(f"Invalid value: {e}")
    result = default_value

# Exception chaining
try:
    data = fetch_data(url)
except NetworkError as e:
    raise ProcessingError(f"Failed to fetch {url}") from e
```

**Scala:**
```scala
// Try monad
import scala.util.{Try, Success, Failure}

val result: Try[Result] = Try {
  riskyOperation()
}.recover {
  case e: IllegalArgumentException =>
    logger.error(s"Invalid value: $e")
    defaultValue
}

// Pattern matching on Try
Try(riskyOperation()) match {
  case Success(value) => processSuccess(value)
  case Failure(exception) => handleError(exception)
}

// Either for domain errors
def fetchData(url: String): Either[ProcessingError, Data] = {
  // Returns Left for error, Right for success
  fetchNetwork(url).left.map { networkError =>
    ProcessingError(s"Failed to fetch $url", networkError)
  }
}

// For-comprehension with Either
val result: Either[Error, Result] = for {
  data <- fetchData(url)
  parsed <- parseData(data)
  validated <- validateData(parsed)
} yield validated
// Short-circuits on first Left (error)
```

**Why this translation:**
- Python uses exceptions for control flow; Scala prefers functional error handling
- Try wraps code that might throw exceptions
- Either provides left/right semantics (Left = error, Right = success)
- For-comprehensions with Try/Either short-circuit on failure
- Scala still supports exceptions but discourages them for expected errors

### Pattern 5: Duck Typing → Traits and Structural Types

**Python:**
```python
# Duck typing - if it quacks like a duck...
def process_file_like(file_like):
    data = file_like.read()  # Any object with .read()
    return parse(data)

# Works with files, StringIO, BytesIO, custom objects
```

**Scala:**
```scala
// Trait-based (nominal typing)
trait Readable {
  def read(): String
}

def processFilelike(readable: Readable): ParsedData = {
  val data = readable.read()
  parse(data)
}

// Structural typing (duck typing in Scala)
import scala.language.reflectiveCalls

type FilelikeType = {
  def read(): String
}

def processFilelikeStructural(fileLike: FilelikeType): ParsedData = {
  val data = fileLike.read()  // Calls via reflection
  parse(data)
}

// Type class pattern (more idiomatic)
trait Readable[T] {
  def read(t: T): String
}

def processFilelikeTC[T](t: T)(implicit readable: Readable[T]): ParsedData = {
  val data = readable.read(t)
  parse(data)
}

// Implicit instances
implicit val fileReadable: Readable[File] = new Readable[File] {
  def read(f: File): String = scala.io.Source.fromFile(f).mkString
}
```

**Why this translation:**
- Python uses runtime duck typing; Scala uses compile-time traits
- Structural types exist but use reflection (slower)
- Type classes provide extensibility without modifying original types
- Traits are the idiomatic Scala approach

### Pattern 6: Decorators → Macros and Implicit Conversions

**Python:**
```python
# Function decorator
@cache
@log_calls
def expensive_function(x):
    return compute(x)

# Class decorator
@dataclass
class Point:
    x: int
    y: int

# Property decorator
class Circle:
    @property
    def area(self):
        return 3.14 * self.radius ** 2
```

**Scala:**
```scala
// Macros for compile-time code generation (Scala 3)
import scala.annotation.experimental
import scala.quoted.*

// Annotation-based (similar to decorators)
@cached
@logged
def expensiveFunction(x: Int): Int = compute(x)

// Case class (similar to @dataclass)
case class Point(x: Int, y: Int)
// Automatically provides: equals, hashCode, toString, copy, pattern matching

// Property-like access (no decorator needed)
class Circle(val radius: Double) {
  def area: Double = Math.PI * radius * radius
  // Called as circle.area (no parens)
}

// Transparent inline for inlining (Scala 3)
transparent inline def logged[T](inline expr: T): T = {
  println(s"Calling function")
  expr
}

// Or use higher-order functions
def withLogging[T](name: String)(f: => T): T = {
  println(s"Calling $name")
  val result = f
  println(s"Finished $name")
  result
}

// Usage
val result = withLogging("expensive") {
  expensiveFunction(42)
}
```

**Why this translation:**
- Python decorators are runtime; Scala 3 inline/macros are compile-time
- Case classes provide dataclass-like functionality built-in
- Properties in Scala are methods without side effects (no parens)
- Higher-order functions can replace many decorator patterns
- Scala 2 macros are complex; Scala 3 improves this significantly

### Pattern 7: Async/Await → Futures and Effect Systems

**Python:**
```python
import asyncio

# Async function
async def fetch_user(user_id):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"/users/{user_id}")
        return User(**response.json())

# Gather multiple async operations
async def fetch_all():
    users, orders = await asyncio.gather(
        fetch_users(),
        fetch_orders()
    )
    return users, orders
```

**Scala:**
```scala
import scala.concurrent.{Future, ExecutionContext}
import scala.concurrent.ExecutionContext.Implicits.global

// Future-based (standard library)
def fetchUser(userId: Int)(implicit ec: ExecutionContext): Future[User] = {
  val client = HttpClient()
  client.get(s"/users/$userId").map { response =>
    parseUser(response.json())
  }
}

// Combine multiple Futures
def fetchAll()(implicit ec: ExecutionContext): Future[(List[User], List[Order])] = {
  for {
    users <- fetchUsers()
    orders <- fetchOrders()
  } yield (users, orders)
}

// Or with Future.sequence
val futures = List(fetchUser(1), fetchUser(2), fetchUser(3))
val combined: Future[List[User]] = Future.sequence(futures)

// With Cats Effect IO (more powerful)
import cats.effect.IO
import cats.implicits._

def fetchUserIO(userId: Int): IO[User] = {
  for {
    response <- httpClient.get(s"/users/$userId")
    user <- IO.fromEither(parseUser(response.json()))
  } yield user
}

// Parallel execution
import cats.syntax.parallel._

val usersIO: IO[List[User]] = List(1, 2, 3).parTraverse(fetchUserIO)
```

**Why this translation:**
- Python's asyncio is cooperative; Scala Futures run on thread pools
- Futures are eager (start immediately); cats-effect IO is lazy
- For-comprehensions sequence async operations
- Cats-effect provides more control over parallelism and resource safety

### Pattern 8: Multiple Inheritance → Traits and Mixins

**Python:**
```python
class Loggable:
    def log(self, message):
        print(f"[LOG] {message}")

class Cacheable:
    def __init__(self):
        self.cache = {}

    def get_cached(self, key):
        return self.cache.get(key)

class UserService(Loggable, Cacheable):
    def __init__(self):
        super().__init__()

    def process(self):
        self.log("Processing")
        return self.get_cached("data")
```

**Scala:**
```scala
// Traits with implementation
trait Loggable {
  def log(message: String): Unit = {
    println(s"[LOG] $message")
  }
}

trait Cacheable {
  private var cache: Map[String, Any] = Map.empty

  def getCached(key: String): Option[Any] = cache.get(key)

  def putCached(key: String, value: Any): Unit = {
    cache = cache + (key -> value)
  }
}

// Mix in traits
class UserService extends Loggable with Cacheable {
  def process(): Option[Any] = {
    log("Processing")
    getCached("data")
  }
}

// Trait linearization
trait A {
  def msg = "A"
}

trait B extends A {
  override def msg = "B" + super.msg
}

trait C extends A {
  override def msg = "C" + super.msg
}

// Linearization: D -> C -> B -> A
class D extends B with C
val d = new D
println(d.msg)  // "CBA"
```

**Why this translation:**
- Python's multiple inheritance can be complex (MRO)
- Scala traits provide cleaner composition with linearization
- Traits can have state (unlike Java interfaces)
- Mixin composition is more explicit and predictable
- Self-types enforce dependencies between traits

### Pattern 9: Dynamic Attributes → Sealed Traits or Maps

**Python:**
```python
# Dynamic attribute access
class DynamicObject:
    def __init__(self):
        self.attrs = {}

    def __getattr__(self, name):
        return self.attrs.get(name)

    def __setattr__(self, name, value):
        if name == 'attrs':
            super().__setattr__(name, value)
        else:
            self.attrs[name] = value

obj = DynamicObject()
obj.custom_field = "value"  # Dynamic!
```

**Scala:**
```scala
// Static approach with sealed trait
sealed trait Field
case class StringField(value: String) extends Field
case class IntField(value: Int) extends Field
case class BoolField(value: Boolean) extends Field

class StaticObject {
  private var fields: Map[String, Field] = Map.empty

  def get(name: String): Option[Field] = fields.get(name)

  def set(name: String, field: Field): Unit = {
    fields = fields + (name -> field)
  }
}

// Dynamic approach with Map
class DynamicObject {
  private var attrs: Map[String, Any] = Map.empty

  def apply(name: String): Option[Any] = attrs.get(name)

  def update(name: String, value: Any): Unit = {
    attrs = attrs + (name -> value)
  }
}

val obj = new DynamicObject
obj("customField") = "value"
println(obj("customField"))  // Some(value)

// Or use Dynamic trait (compile-time rewriting)
import scala.language.dynamics

class FlexibleObject extends Dynamic {
  private var fields: Map[String, Any] = Map.empty

  def selectDynamic(name: String): Any = fields(name)

  def updateDynamic(name: String)(value: Any): Unit = {
    fields = fields + (name -> value)
  }
}

// Usage looks dynamic but is compile-time checked
val flex = new FlexibleObject
flex.customField = "value"  // Translates to updateDynamic
println(flex.customField)   // Translates to selectDynamic
```

**Why this translation:**
- Python allows true runtime attribute creation
- Scala prefers static typing with sealed traits for known variants
- Map-based approach for truly dynamic data
- Dynamic trait provides syntax similar to Python but with compile-time checking
- Trade flexibility for type safety and performance

### Pattern 10: Context Managers → Try-with-resources / Loan Pattern

**Python:**
```python
# Context manager protocol
with open("data.txt") as f:
    data = f.read()
# File automatically closed

# Custom context manager
from contextlib import contextmanager

@contextmanager
def database_transaction(conn):
    conn.begin()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise

with database_transaction(conn) as tx:
    tx.execute("INSERT ...")
```

**Scala:**
```scala
// Try-with-resources (Scala 2.13+)
import scala.util.Using

val result: Try[String] = Using(Source.fromFile("data.txt")) { source =>
  source.mkString
}
// Source automatically closed

// Loan pattern (functional resource management)
def withResource[R <: AutoCloseable, T](resource: => R)(f: R => T): T = {
  var res: R = null.asInstanceOf[R]
  try {
    res = resource
    f(res)
  } finally {
    if (res != null) res.close()
  }
}

// Usage
val data = withResource(Source.fromFile("data.txt")) { source =>
  source.mkString
}

// Custom resource management
def withTransaction[T](conn: Connection)(f: Connection => T): Try[T] = Try {
  conn.setAutoCommit(false)
  try {
    val result = f(conn)
    conn.commit()
    result
  } catch {
    case e: Exception =>
      conn.rollback()
      throw e
  }
}

withTransaction(conn) { implicit tx =>
  executeQuery("INSERT ...")
}

// With cats-effect Resource
import cats.effect.{IO, Resource}

def acquireConnection: IO[Connection] = IO(/* ... */)
def releaseConnection(conn: Connection): IO[Unit] = IO(conn.close())

val connectionResource: Resource[IO, Connection] = Resource.make(
  acquire = acquireConnection
)(release = releaseConnection)

val program: IO[Result] = connectionResource.use { conn =>
  IO {
    conn.executeQuery("SELECT ...")
  }
}
```

**Why this translation:**
- Python's `with` statement uses `__enter__`/`__exit__` protocol
- Scala uses try-finally, Using, or functional patterns
- Loan pattern captures the context manager pattern functionally
- cats-effect Resource provides composable resource management
- Scala's type system ensures resources are properly released

---

## Module System Translation

### Python Package Structure

```python
# Python package layout
myproject/
├── mypackage/
│   ├── __init__.py
│   ├── module1.py
│   ├── module2.py
│   └── subpackage/
│       ├── __init__.py
│       └── module3.py
└── setup.py

# Imports
from mypackage import module1
from mypackage.subpackage import module3
from mypackage.module1 import SomeClass
```

### Scala Package Structure

```scala
// Scala package layout
myproject/
├── src/main/scala/
│   └── com/mycompany/myproject/
│       ├── Module1.scala
│       ├── Module2.scala
│       └── subpackage/
│           └── Module3.scala
└── build.sbt

// Package declarations (Module1.scala)
package com.mycompany.myproject

class SomeClass {
  // ...
}

// Imports
import com.mycompany.myproject.Module1
import com.mycompany.myproject.subpackage.Module3
import com.mycompany.myproject.Module1.SomeClass

// Wildcard import
import com.mycompany.myproject._  // Like Python's *

// Selective imports
import com.mycompany.myproject.{Module1, Module2}

// Rename on import
import com.mycompany.myproject.{Module1 => M1}
```

**Key Differences**:

| Python | Scala | Notes |
|--------|-------|-------|
| `__init__.py` required | No init file needed | Package defined by directory |
| Relative imports common | Absolute imports preferred | Explicit package paths |
| `from X import *` | `import X._` | Wildcard imports |
| `import X as Y` | `import X as Y` (2.x) or `import X as Y` (3.x) | Import aliasing |

### Scala Objects as Module Singletons

```python
# Python module-level functions and constants
# mymodule.py
DEFAULT_TIMEOUT = 30

def connect(host, port):
    return Connection(host, port)

# Usage
import mymodule
conn = mymodule.connect("localhost", 8080)
```

```scala
// Scala object for singleton module
package com.mycompany.myproject

object MyModule {
  val DefaultTimeout: Int = 30

  def connect(host: String, port: Int): Connection = {
    new Connection(host, port)
  }
}

// Usage
import com.mycompany.myproject.MyModule
val conn = MyModule.connect("localhost", 8080)

// Or with wildcard import
import com.mycompany.myproject.MyModule._
val conn = connect("localhost", 8080)
```

---

## Error Handling Translation

### Exception Hierarchy → ADTs

**Python:**
```python
class AppError(Exception):
    pass

class NotFoundError(AppError):
    def __init__(self, resource, resource_id):
        self.resource = resource
        self.resource_id = resource_id
        super().__init__(f"{resource} {resource_id} not found")

class ValidationError(AppError):
    def __init__(self, field, message):
        self.field = field
        super().__init__(f"{field}: {message}")

# Usage
def get_user(user_id):
    user = db.find(user_id)
    if not user:
        raise NotFoundError("User", user_id)
    return user

try:
    user = get_user(123)
except NotFoundError as e:
    print(f"Error: {e}")
```

**Scala:**
```scala
// Sealed trait for error ADT
sealed trait AppError
case class NotFoundError(resource: String, resourceId: Int) extends AppError
case class ValidationError(field: String, message: String) extends AppError
case class DatabaseError(cause: Throwable) extends AppError

// Either-based error handling
def getUser(userId: Int): Either[AppError, User] = {
  db.find(userId) match {
    case Some(user) => Right(user)
    case None => Left(NotFoundError("User", userId))
  }
}

// Pattern matching on errors
getUser(123) match {
  case Right(user) => println(s"Found: $user")
  case Left(NotFoundError(resource, id)) =>
    println(s"Error: $resource $id not found")
  case Left(ValidationError(field, msg)) =>
    println(s"Error: $field: $msg")
  case Left(err) =>
    println(s"Error: $err")
}

// For-comprehension error chaining
val result: Either[AppError, Result] = for {
  user <- getUser(userId)
  profile <- getProfile(user.profileId)
  settings <- getSettings(user.settingsId)
} yield Result(user, profile, settings)
// Short-circuits on first Left
```

**Why this translation:**
- Python exception hierarchies → Scala sealed trait ADTs
- Exceptions for control flow → Either/Try for expected errors
- Pattern matching provides exhaustive error handling
- Compiler ensures all error cases are handled
- For-comprehensions elegantly chain error-producing operations

---

## Serialization Patterns

### Pydantic → Case Classes with Circe

**Python (Pydantic):**
```python
from pydantic import BaseModel, Field, field_validator
from typing import Optional

class User(BaseModel):
    id: int
    name: str = Field(min_length=1, max_length=100)
    email: Optional[str] = None
    age: int = Field(ge=0, le=150)

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if v and '@' not in v:
            raise ValueError('Invalid email')
        return v

# Serialization
user = User(id=1, name="Alice", age=30)
json_str = user.model_dump_json()

# Deserialization with validation
user = User.model_validate_json(json_str)
```

**Scala (Circe):**
```scala
import io.circe._
import io.circe.generic.semiauto._
import io.circe.syntax._

// Case class definition
case class User(
  id: Int,
  name: String,
  email: Option[String],
  age: Int
)

// Validation separate from data structure
object User {
  def validate(user: User): Either[List[String], User] = {
    val errors = List.newBuilder[String]

    if (user.name.length < 1 || user.name.length > 100)
      errors += "name must be between 1 and 100 characters"

    if (user.age < 0 || user.age > 150)
      errors += "age must be between 0 and 150"

    user.email.foreach { email =>
      if (!email.contains('@'))
        errors += "invalid email"
    }

    val errorList = errors.result()
    if (errorList.isEmpty) Right(user)
    else Left(errorList)
  }
}

// Automatic codec derivation
implicit val userDecoder: Decoder[User] = deriveDecoder
implicit val userEncoder: Encoder[User] = deriveEncoder

// Serialization
val user = User(1, "Alice", None, 30)
val json: Json = user.asJson
val jsonString: String = json.noSpaces

// Deserialization
val decoded: Either[Error, User] = decode[User](jsonString)

// With validation
val validated: Either[List[String], User] = decoded.flatMap(User.validate)

// Or use refined types for compile-time validation
import eu.timepit.refined._
import eu.timepit.refined.api.Refined
import eu.timepit.refined.numeric._
import eu.timepit.refined.string._
import eu.timepit.refined.collection._

type NameType = String Refined (MinSize[1] And MaxSize[100])
type AgeType = Int Refined Interval.Closed[0, 150]
type EmailType = String Refined MatchesRegex["^.+@.+$"]

case class ValidatedUser(
  id: Int,
  name: NameType,
  email: Option[EmailType],
  age: AgeType
)
```

**Why this translation:**
- Pydantic combines data structure and validation; Scala separates concerns
- Circe provides automatic codec derivation for case classes
- Refined types provide compile-time validation
- Scala validation is more verbose but more flexible
- Libraries like cats-validation provide more sophisticated validation

---

## Concurrency Patterns

### Threading/Asyncio → Futures/Akka

**Python (asyncio):**
```python
import asyncio

async def fetch_data(url):
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()

async def process_all(urls):
    tasks = [fetch_data(url) for url in urls]
    results = await asyncio.gather(*tasks)
    return results

# Run
results = asyncio.run(process_all(urls))
```

**Scala (Futures):**
```scala
import scala.concurrent.{Future, ExecutionContext}
import scala.concurrent.ExecutionContext.Implicits.global

def fetchData(url: String)(implicit ec: ExecutionContext): Future[Json] = {
  httpClient.get(url).map(_.json)
}

def processAll(urls: List[String])(implicit ec: ExecutionContext): Future[List[Json]] = {
  val futures = urls.map(fetchData)
  Future.sequence(futures)
}

// Run
import scala.concurrent.Await
import scala.concurrent.duration._

val results = Await.result(processAll(urls), 30.seconds)
```

**Scala (Akka Actors):**
```scala
import akka.actor.{Actor, ActorSystem, Props}

// Actor for handling requests
class FetchActor extends Actor {
  def receive: Receive = {
    case FetchData(url) =>
      val result = fetchDataSync(url)
      sender() ! DataResult(result)
  }
}

case class FetchData(url: String)
case class DataResult(data: Json)

// Create actor system
val system = ActorSystem("FetchSystem")
val fetchActor = system.actorOf(Props[FetchActor], "fetchActor")

// Send messages
import akka.pattern.ask
import akka.util.Timeout
import scala.concurrent.duration._

implicit val timeout: Timeout = Timeout(30.seconds)

val results: Future[List[DataResult]] = Future.sequence(
  urls.map { url =>
    (fetchActor ? FetchData(url)).mapTo[DataResult]
  }
)
```

**Why this translation:**
- Python's asyncio is single-threaded; Scala Futures use thread pools
- Futures are eager and composable via map/flatMap
- Akka actors provide message-based concurrency with fault tolerance
- Actors isolate state and communicate via messages (like Erlang)

---

## Build System & Dependencies

### pip/poetry → sbt/mill

**Python (pyproject.toml):**
```toml
[tool.poetry]
name = "myproject"
version = "0.1.0"
description = "My Python project"

[tool.poetry.dependencies]
python = "^3.11"
pydantic = "^2.0"
httpx = "^0.25"

[tool.poetry.dev-dependencies]
pytest = "^7.0"
mypy = "^1.0"
```

**Scala (build.sbt):**
```scala
name := "myproject"
version := "0.1.0"
scalaVersion := "3.3.1"

// Dependencies
libraryDependencies ++= Seq(
  "io.circe" %% "circe-core" % "0.14.6",
  "io.circe" %% "circe-generic" % "0.14.6",
  "io.circe" %% "circe-parser" % "0.14.6",
  "com.softwaremill.sttp.client3" %% "core" % "3.9.1",

  // Test dependencies
  "org.scalatest" %% "scalatest" % "3.2.17" % Test,
  "org.scalatestplus" %% "scalacheck-1-17" % "3.2.17.0" % Test
)

// Compiler options
scalacOptions ++= Seq(
  "-deprecation",
  "-feature",
  "-unchecked",
  "-Xfatal-warnings"
)
```

**Dependency Translation Table:**

| Python Package | Scala Equivalent | Purpose |
|----------------|------------------|---------|
| `requests`, `httpx` | `sttp`, `akka-http` | HTTP clients |
| `pydantic` | `circe`, `upickle` | JSON serialization |
| `fastapi` | `http4s`, `akka-http` | Web frameworks |
| `pytest` | `scalatest`, `munit` | Testing |
| `mypy` | `scalac` (built-in) | Type checking |
| `black` | `scalafmt` | Code formatting |
| `pylint` | `scalafix`, `wartremover` | Linting |
| `click` | `decline`, `scopt` | CLI parsing |

---

## Testing Strategy

### pytest → ScalaTest/ScalaCheck

**Python (pytest):**
```python
import pytest
from myapp import UserService

@pytest.fixture
def user_service():
    return UserService(db=MockDatabase())

def test_get_existing_user(user_service):
    user = user_service.get_user(1)
    assert user is not None
    assert user.name == "Alice"

def test_get_missing_user(user_service):
    with pytest.raises(NotFoundError):
        user_service.get_user(999)

@pytest.mark.parametrize("user_id,expected_name", [
    (1, "Alice"),
    (2, "Bob"),
    (3, "Charlie"),
])
def test_multiple_users(user_service, user_id, expected_name):
    user = user_service.get_user(user_id)
    assert user.name == expected_name

# Property-based testing
from hypothesis import given
import hypothesis.strategies as st

@given(st.integers(min_value=1, max_value=1000))
def test_user_id_valid_range(user_id):
    # Property: all valid IDs should not raise exception
    try:
        get_user(user_id)
    except NotFoundError:
        pass  # OK if not found
    except Exception as e:
        pytest.fail(f"Unexpected exception: {e}")
```

**Scala (ScalaTest + ScalaCheck):**
```scala
import org.scalatest.flatspec.AnyFlatSpec
import org.scalatest.matchers.should.Matchers
import org.scalatestplus.scalacheck.ScalaCheckPropertyChecks

class UserServiceSpec extends AnyFlatSpec with Matchers with ScalaCheckPropertyChecks {

  // Fixture
  def userService: UserService = new UserService(new MockDatabase())

  "UserService" should "return existing user" in {
    val service = userService
    val user = service.getUser(1)

    user should not be empty
    user.get.name shouldBe "Alice"
  }

  it should "return None for missing user" in {
    val service = userService
    val user = service.getUser(999)

    user shouldBe None
  }

  // Or with Either/Try
  it should "return Left for missing user" in {
    val service = userService
    val result = service.getUserEither(999)

    result shouldBe a[Left[_, _]]
    result.left.get shouldBe NotFoundError("User", 999)
  }

  // Table-driven tests
  it should "return correct names for multiple users" in {
    val service = userService
    val testCases = Table(
      ("userId", "expectedName"),
      (1, "Alice"),
      (2, "Bob"),
      (3, "Charlie")
    )

    forAll(testCases) { (userId, expectedName) =>
      val user = service.getUser(userId)
      user.get.name shouldBe expectedName
    }
  }

  // Property-based testing with ScalaCheck
  it should "handle all valid user IDs without exception" in {
    forAll(Gen.choose(1, 1000)) { userId =>
      val service = userService
      noException should be thrownBy {
        service.getUser(userId)
      }
    }
  }

  // Property: round-trip serialization
  it should "round-trip serialize users" in {
    forAll(genUser) { user =>
      val json = user.asJson
      val decoded = decode[User](json.noSpaces)

      decoded shouldBe Right(user)
    }
  }
}

// Custom generators
object UserGenerators {
  import org.scalacheck.Gen

  val genUser: Gen[User] = for {
    id <- Gen.posNum[Int]
    name <- Gen.alphaNumStr.suchThat(_.nonEmpty)
    age <- Gen.choose(0, 150)
    email <- Gen.option(genEmail)
  } yield User(id, name, email, age)

  val genEmail: Gen[String] = for {
    user <- Gen.alphaNumStr.suchThat(_.nonEmpty)
    domain <- Gen.alphaNumStr.suchThat(_.nonEmpty)
  } yield s"$user@$domain.com"
}
```

**Why this translation:**
- pytest fixtures → ScalaTest traits or def methods
- pytest.raises → should/shouldBe matchers
- pytest.mark.parametrize → Table-driven tests
- Hypothesis → ScalaCheck for property-based testing
- Scala's type system catches more errors at compile time

---

## Dev Workflow & REPL

### Python REPL → Scala REPL/Ammonite

**Python REPL:**
```python
$ python
>>> from myapp import User
>>> user = User(id=1, name="Alice", age=30)
>>> user.greet()
'Hello, Alice!'
>>> user.age += 1
>>> user.age
31
```

**Scala REPL:**
```scala
$ scala
scala> import com.mycompany.myapp.User
scala> val user = User(id=1, name="Alice", age=30)
val user: User = User(1,Alice,None,30)

scala> user.greet()
val res0: String = Hello, Alice!

scala> val olderUser = user.copy(age = user.age + 1)
val olderUser: User = User(1,Alice,None,31)

scala> olderUser.age
val res1: Int = 31
```

**sbt console:**
```scala
$ sbt console
[info] Starting scala interpreter...

scala> import com.mycompany.myapp._
scala> // Full project classpath available
```

**Ammonite (enhanced REPL):**
```scala
$ amm
@ import $ivy.`io.circe::circe-core:0.14.6`
@ import io.circe._, io.circe.syntax._
@ case class User(id: Int, name: String)
@ val user = User(1, "Alice")
@ user.asJson
res: Json = {"id": 1, "name": "Alice"}

// Script files with dependencies
// user-service.sc
import $ivy.`com.softwaremill.sttp.client3::core:3.9.1`

case class User(id: Int, name: String)

def fetchUser(id: Int): User = {
  // Implementation
}
```

**Scala Notebooks:**
```scala
// Almond (Jupyter kernel for Scala)
// Can use in Jupyter notebooks for data exploration

// Scala CLI for quick scripts
$ scala-cli run script.scala
```

**Key Differences**:

| Python | Scala | Notes |
|--------|-------|-------|
| `python` REPL | `scala` REPL | Basic REPL |
| IPython | Ammonite | Enhanced REPL |
| Jupyter | Almond (Jupyter) | Notebooks |
| `python -m` | sbt console | Project context |
| Scripts run directly | Need compilation or scala-cli | Compilation step |

---

## FFI & Interoperability

### Python C Extensions → JNI/JNA/Scala Native

**Python (ctypes):**
```python
from ctypes import CDLL, c_int, c_char_p

# Load C library
lib = CDLL('./mylib.so')

# Define function signature
lib.process_data.argtypes = [c_char_p, c_int]
lib.process_data.restype = c_int

# Call C function
result = lib.process_data(b"data", 100)
```

**Scala (JNA):**
```scala
import com.sun.jna.{Library, Native}

// Define interface matching C library
trait MyLib extends Library {
  def process_data(data: String, size: Int): Int
}

// Load library
val lib = Native.load("mylib", classOf[MyLib])

// Call function
val result = lib.process_data("data", 100)
```

**Scala Native (direct C interop):**
```scala
import scala.scalanative.unsafe._
import scala.scalanative.unsigned._

@extern
object MyLib {
  def process_data(data: CString, size: CInt): CInt = extern
}

// Usage
Zone { implicit z =>
  val result = MyLib.process_data(c"data", 100)
}
```

**Python → Scala Gradual Migration:**

1. **Phase 1**: Identify Python modules to convert
2. **Phase 2**: Create Scala equivalents
3. **Phase 3**: Use Py4J or Jython for interop during migration
4. **Phase 4**: Complete migration, remove Python dependencies

**Py4J (Python calling Scala/JVM):**

```python
# Python side
from py4j.java_gateway import JavaGateway

gateway = JavaGateway()
user_service = gateway.entry_point.getUserService()
user = user_service.getUser(1)
print(user.getName())
```

```scala
// Scala side
import py4j.GatewayServer

object Main extends App {
  val gateway = new GatewayServer(new MyApp())
  gateway.start()
}

class MyApp {
  def getUserService(): UserService = new UserService()
}
```

---

## Common Pitfalls

### 1. Mutability Assumptions

```python
# Python: Default mutable
my_list = [1, 2, 3]
my_list.append(4)  # Mutates in place
```

```scala
// ❌ Assuming mutability
val myList = List(1, 2, 3)
myList.append(4)  // COMPILE ERROR - List is immutable

// ✓ Immutable update
val myList = List(1, 2, 3)
val newList = myList :+ 4
```

### 2. None Handling

```python
# Python: None is falsy
user = get_user(id)
if user:  # Implicit None check
    process(user)
```

```scala
// ❌ Treating Option as boolean
val user: Option[User] = getUser(id)
if (user)  // COMPILE ERROR - Option is not Boolean
  process(user)

// ✓ Pattern match or isDefined
user match {
  case Some(u) => process(u)
  case None => // handle missing
}

// Or
if (user.isDefined) {
  process(user.get)
}

// Better: use map/foreach
user.foreach(process)
```

### 3. Trying to Translate Exceptions Directly

```python
# Python: Exceptions for control flow
def get_user(id):
    if not exists(id):
        raise UserNotFoundError(id)
    return fetch(id)
```

```scala
// ❌ Using exceptions like Python
def getUser(id: Int): User = {
  if (!exists(id))
    throw new UserNotFoundException(id)
  fetch(id)
}

// ✓ Use Option/Either/Try
def getUser(id: Int): Option[User] = {
  if (exists(id)) Some(fetch(id))
  else None
}

// Or Either for error details
def getUser(id: Int): Either[UserError, User] = {
  if (exists(id)) Right(fetch(id))
  else Left(UserNotFound(id))
}
```

### 4. Dynamic Typing Assumptions

```python
# Python: Dynamic typing
def process(value):
    if isinstance(value, str):
        return value.upper()
    elif isinstance(value, int):
        return value * 2
    else:
        return None
```

```scala
// ❌ Trying to replicate with Any
def process(value: Any): Any = value match {
  case s: String => s.toUpperCase
  case i: Int => i * 2
  case _ => null  // Avoid null!
}

// ✓ Use sealed trait for known types
sealed trait Value
case class StringValue(s: String) extends Value
case class IntValue(i: Int) extends Value

def process(value: Value): String = value match {
  case StringValue(s) => s.toUpperCase
  case IntValue(i) => (i * 2).toString
}
```

### 5. List Comprehension Translation

```python
# Python: Nested comprehensions
result = [[x * y for y in ys] for x in xs]
```

```scala
// ❌ Trying to nest for-comprehensions incorrectly
val result = for {
  x <- xs
  y <- ys  // This flattens!
} yield x * y  // Wrong shape

// ✓ Nested maps
val result = xs.map { x =>
  ys.map { y =>
    x * y
  }
}

// Or explicit nesting in for-comp
val result = for {
  x <- xs
} yield for {
  y <- ys
} yield x * y
```

---

## Best Practices

1. **Embrace immutability** - use `val` and immutable collections by default
2. **Pattern match extensively** - case classes and sealed traits enable exhaustive matching
3. **Use Option/Either/Try** instead of null and exceptions for expected errors
4. **Leverage type inference** - but use explicit types for public APIs
5. **Composition over inheritance** - use traits for mixins, avoid deep hierarchies
6. **For-comprehensions** for sequential monadic operations
7. **Prefer expression-oriented** code - everything returns a value
8. **Use case classes** for data - they're cheap and provide lots of functionality
9. **Separate pure and impure** code - keep side effects at the edges
10. **Test with property-based testing** - ScalaCheck for generative tests

---

## Tooling Recommendations

### Code Quality

| Purpose | Python | Scala |
|---------|--------|-------|
| Formatter | black, ruff | scalafmt |
| Linter | pylint, ruff | scalafix, wartremover |
| Type checker | mypy | scalac (built-in) |
| Dependency check | safety | dependency-check |
| Build tool | pip, poetry | sbt, mill, gradle |

### IDE Support

| IDE | Python | Scala |
|-----|--------|-------|
| IntelliJ IDEA | Python plugin | Scala plugin (excellent) |
| VS Code | Pylance | Metals |
| Vim/Neovim | python-lsp | metals-vim |
| Emacs | elpy | metals-emacs |

### Testing Tools

```scala
// ScalaTest - flexible, multiple styles
class MySpec extends AnyFlatSpec with Matchers {
  "A Stack" should "pop values in LIFO order" in {
    val stack = Stack[Int]()
    stack.push(1)
    stack.push(2)
    stack.pop() shouldBe 2
  }
}

// MUnit - lightweight, fast
class MyTests extends munit.FunSuite {
  test("basic assertion") {
    assertEquals(add(2, 3), 5)
  }
}

// ScalaCheck - property-based testing
import org.scalacheck.Properties
import org.scalacheck.Prop.forAll

object StringSpecification extends Properties("String") {
  property("concatenation") = forAll { (a: String, b: String) =>
    (a + b).length == a.length + b.length
  }
}
```

---

## Library Mapping Reference

| Python Library | Scala Equivalent | Use Case |
|----------------|------------------|----------|
| requests | sttp, akka-http | HTTP client |
| fastapi | http4s, akka-http, play | Web framework |
| pydantic | circe, upickle, jsoniter-scala | JSON (de)serialization |
| sqlalchemy | doobie, slick, quill | Database ORM/query |
| celery | akka, zio | Task queue |
| pandas | spark, frameless | Dataframes |
| numpy | breeze, nd4s | Numerical computing |
| pytest | scalatest, munit | Testing |
| hypothesis | scalacheck | Property testing |
| click | decline, scopt | CLI parsing |
| asyncio | Future, cats-effect IO, zio | Async/effects |
| typing | Built-in type system | Static types |

---

## Examples: End-to-End Conversion

### Example 1: REST API Service

**Python (FastAPI):**
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

class User(BaseModel):
    id: int
    name: str
    email: Optional[str] = None

users_db = {}

@app.post("/users", response_model=User)
async def create_user(user: User):
    if user.id in users_db:
        raise HTTPException(status_code=400, detail="User exists")
    users_db[user.id] = user
    return user

@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: int):
    user = users_db.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

**Scala (http4s):**
```scala
import cats.effect.IO
import io.circe.generic.auto._
import org.http4s._
import org.http4s.dsl.io._
import org.http4s.circe.CirceEntityCodec._
import scala.collection.concurrent.TrieMap

case class User(id: Int, name: String, email: Option[String])

class UserService {
  private val usersDb = TrieMap[Int, User]()

  val routes: HttpRoutes[IO] = HttpRoutes.of[IO] {
    case req @ POST -> Root / "users" =>
      for {
        user <- req.as[User]
        response <- if (usersDb.contains(user.id)) {
          BadRequest("User exists")
        } else {
          usersDb.put(user.id, user)
          Ok(user)
        }
      } yield response

    case GET -> Root / "users" / IntVar(userId) =>
      usersDb.get(userId) match {
        case Some(user) => Ok(user)
        case None => NotFound("User not found")
      }
  }
}
```

### Example 2: Data Processing Pipeline

**Python:**
```python
from typing import List
import pandas as pd

def process_sales_data(data: List[dict]) -> dict:
    df = pd.DataFrame(data)

    # Filter
    recent = df[df['year'] >= 2020]

    # Group and aggregate
    by_region = recent.groupby('region')['sales'].sum()

    # Transform
    result = {
        'total': recent['sales'].sum(),
        'by_region': by_region.to_dict(),
        'avg_sale': recent['sales'].mean()
    }

    return result
```

**Scala:**
```scala
case class SaleRecord(year: Int, region: String, sales: Double)
case class SalesReport(total: Double, byRegion: Map[String, Double], avgSale: Double)

def processSalesData(data: List[SaleRecord]): SalesReport = {
  // Filter
  val recent = data.filter(_.year >= 2020)

  // Group and aggregate
  val byRegion = recent
    .groupBy(_.region)
    .view
    .mapValues(_.map(_.sales).sum)
    .toMap

  // Transform
  val total = recent.map(_.sales).sum
  val avgSale = total / recent.size

  SalesReport(total, byRegion, avgSale)
}

// Or with Spark for large datasets
import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions._

def processSalesDataSpark(spark: SparkSession, data: DataFrame): SalesReport = {
  val recent = data.filter($"year" >= 2020)

  val byRegion = recent
    .groupBy("region")
    .agg(sum("sales").as("total"))
    .collect()
    .map(row => row.getString(0) -> row.getDouble(1))
    .toMap

  val total = recent.agg(sum("sales")).as[Double].first()
  val avgSale = recent.agg(avg("sales")).as[Double].first()

  SalesReport(total, byRegion, avgSale)
}
```

---

## Related Skills

- `meta-convert-dev` - General conversion methodology
- `lang-python-dev` - Python fundamentals
- `lang-scala-dev` - Scala fundamentals
- `lang-scala-akka-dev` - Akka patterns for concurrency
- `lang-scala-cats-dev` - Cats FP library patterns
- `patterns-serialization-dev` - Cross-language serialization
- `patterns-concurrency-dev` - Cross-language concurrency
- `patterns-metaprogramming-dev` - Cross-language metaprogramming

---

## Feedback for Skill Gaps

Based on this conversion skill development:

**Gaps in lang-python-dev**:
1. More coverage of Python's memory model and GC behavior
2. Detailed asyncio patterns beyond basics
3. Python metaprogramming (descriptors, metaclasses) for deeper conversions
4. More on Python's data model (__dunder__ methods)

**Gaps in lang-scala-dev**:
1. More detailed coverage of variance in type parameters
2. Path-dependent types explanation
3. Scala 3 specific features (union types, opaque types, etc.)
4. More on implicit resolution and type class patterns

**Patterns that were challenging to document**:
1. Python's dynamic attribute access → Scala's static typing (requires architectural changes)
2. Python decorators → Scala macros (compile-time vs runtime complexity)
3. Python's mutable-by-default → Scala's immutable-by-default (paradigm shift)
4. Python's duck typing → Scala's structural types (performance tradeoffs)
5. Exception-based control flow → monadic error handling (mental model shift)

**What worked well**:
1. APTV workflow from meta-convert-dev provided clear structure
2. Pattern-by-pattern translation with examples
3. Emphasis on hybrid OOP+FP paradigm unique to Scala
4. Clear mapping of Python idioms to Scala equivalents
5. JVM ecosystem integration guidance
