---
name: convert-scala-elixir
description: Convert Scala code to idiomatic Elixir. Use when migrating Scala/JVM applications to Elixir/BEAM, translating Akka actor systems to OTP, or refactoring functional Scala patterns to BEAM-native concurrency. Extends meta-convert-dev with Scala-to-Elixir specific patterns.
---

# Convert Scala to Elixir

Convert Scala code to idiomatic Elixir. This skill extends `meta-convert-dev` with Scala-to-Elixir specific type mappings, idiom translations, and tooling for translating between JVM and BEAM ecosystems.

## This Skill Extends

- `meta-convert-dev` - Foundational conversion patterns (APTV workflow, testing strategies)

For general concepts like the Analyze → Plan → Transform → Validate workflow, testing strategies, and common pitfalls, see the meta-skill first.

## This Skill Adds

- **Type mappings**: Scala types → Elixir types with dynamic runtime
- **Idiom translations**: Case classes → Structs, Traits → Protocols
- **Error handling**: Try/Either → {:ok, result} tuples and with construct
- **Concurrency**: Futures/Akka actors → Processes and GenServer
- **Paradigm shift**: JVM OOP+FP → BEAM pure FP with immutability
- **Build tools**: sbt → Mix project structure
- **REPL workflow**: Scala REPL/Ammonite → IEx with hot reload

## This Skill Does NOT Cover

- General conversion methodology - see `meta-convert-dev`
- Scala language fundamentals - see `lang-scala-dev`
- Elixir language fundamentals - see `lang-elixir-dev`
- Reverse conversion (Elixir → Scala) - see `convert-elixir-scala`
- Advanced Akka patterns - see `lang-scala-akka-dev` for source patterns
- Advanced Phoenix patterns - see `lang-elixir-phoenix-dev` for target patterns

---

## Quick Reference

| Scala | Elixir | Notes |
|-------|--------|-------|
| `val x = 42` | `x = 42` | Immutable by default in both |
| `Option[A]` | `{:ok, a} \| nil` | Optional values |
| `Either[L, R]` | `{:ok, r} \| {:error, l}` | Error handling |
| `case class User(name: String)` | `defstruct [:name]` | Data containers |
| `sealed trait` | `@type t ::` sum type | ADT definition |
| `trait Logger` | `defprotocol Logger` | Interface/protocol |
| `List[A]` | `[a]` | Immutable lists |
| `Map[K, V]` | `%{k => v}` | Hash maps |
| `Future[A]` | `Task` | Async computations |
| `for { x <- ... } yield` | `for x <- ..., do:` | Comprehensions |
| `implicit val` | `@spec` + callbacks | Type classes → protocols |
| `object Utils` | `defmodule Utils` | Singleton → module |

---

## When Converting Code

1. **Analyze source thoroughly** - Understand JVM semantics before BEAM translation
2. **Map types first** - Create type equivalence table, handle nullable → nil
3. **Preserve semantics** over syntax similarity
4. **Adopt Elixir idioms** - Don't write "Scala code in Elixir syntax"
5. **Embrace the actor model** - Threads/Futures → lightweight processes
6. **Handle supervision** - Convert error handling to OTP supervision trees
7. **Test equivalence** - Same inputs → same outputs across platforms

---

## Type System Mapping

### Primitive Types

| Scala | Elixir | Notes |
|-------|--------|-------|
| `Int` | `integer` | 32-bit signed → arbitrary precision |
| `Long` | `integer` | 64-bit signed → arbitrary precision |
| `Double` | `float` | 64-bit IEEE 754 in both |
| `Float` | `float` | Elixir only has `float` (64-bit) |
| `Boolean` | `boolean` (`:true`/`:false`) | Boolean atoms in Elixir |
| `Char` | `integer` (codepoint) | Unicode codepoint |
| `String` | `String.t()` (binary) | UTF-8 binary strings |
| `Unit` | `:ok` atom | Represents "no value" |
| `Nothing` | n/a | Bottom type (no equivalent) |

**Key difference**: Elixir integers are arbitrary precision by default, unlike JVM's fixed-width integers.

### Collection Types

| Scala | Elixir | Notes |
|-------|--------|-------|
| `List[A]` | `[a]` | Immutable linked lists |
| `Vector[A]` | `[a]` | Use lists (persistent) |
| `Array[A]` | `tuple` or `:array` module | Tuples for fixed size, `:array` for large collections |
| `Set[A]` | `MapSet.t(a)` | Immutable sets |
| `Map[K, V]` | `%{k => v}` | Hash maps |
| `Seq[A]` | `[a]` or `Stream` | Lists or lazy streams |
| `Stream[A]` | `Stream.t(a)` | Lazy sequences |
| `Option[A]` | `a \| nil` or `{:ok, a}` | Nullable handling |
| `(A, B)` | `{a, b}` | Tuples |
| `(A, B, C)` | `{a, b, c}` | Tuples (up to any size) |

### Composite Types

| Scala | Elixir | Notes |
|-------|--------|-------|
| `case class User(name: String, age: Int)` | `defstruct [:name, :age]` | Product types |
| `sealed trait` + `case class` | `@type t ::` union | Sum types (ADTs) |
| `trait Logger` | `defprotocol Logger` | Interfaces |
| `object Utils` | `defmodule Utils` | Singleton as module |
| `class MyClass` | `defmodule` + struct | OOP → module + data |
| `type alias` | `@type` | Type aliases |
| `implicit class` | Functions + pipe `\|>` | Extension methods |

### Error Handling Types

| Scala | Elixir | Notes |
|-------|--------|-------|
| `Try[A]` | `{:ok, a} \| {:error, reason}` | Exception → tuple |
| `Either[L, R]` | `{:ok, r} \| {:error, l}` | Error with context |
| `Success(value)` | `{:ok, value}` | Success case |
| `Failure(exception)` | `{:error, reason}` | Error case |
| `Option[A]` | `{:ok, a} \| nil` | Optional with nil |

---

## Idiom Translation

### Pattern: Case Class to Struct

**Scala:**
```scala
case class User(
  id: Int,
  name: String,
  email: String,
  age: Option[Int] = None
)

object User {
  def create(name: String, email: String): User =
    User(id = 0, name = name, email = email)
}

val user = User.create("Alice", "alice@example.com")
val updated = user.copy(age = Some(30))
```

**Elixir:**
```elixir
defmodule User do
  @enforce_keys [:id, :name, :email]
  defstruct [:id, :name, :email, :age]

  @type t :: %__MODULE__{
    id: integer(),
    name: String.t(),
    email: String.t(),
    age: integer() | nil
  }

  @spec create(String.t(), String.t()) :: t()
  def create(name, email) do
    %User{id: 0, name: name, email: email, age: nil}
  end
end

user = User.create("Alice", "alice@example.com")
updated = %{user | age: 30}
```

**Why this translation:**
- Structs in Elixir are named maps with compile-time guarantees
- `@enforce_keys` ensures required fields at construction
- Update syntax `%{struct | key: value}` replaces `copy`
- Nil is idiomatic for optional fields

---

### Pattern: Sealed Trait (ADT) to Sum Type

**Scala:**
```scala
sealed trait Result[+A]
case class Success[A](value: A) extends Result[A]
case class Failure(error: String) extends Result[Nothing]

def processResult[A](result: Result[A]): String = result match {
  case Success(value) => s"Got: $value"
  case Failure(error) => s"Error: $error"
}
```

**Elixir:**
```elixir
@type result(a) :: {:ok, a} | {:error, String.t()}

@spec process_result(result(term())) :: String.t()
def process_result(result) do
  case result do
    {:ok, value} -> "Got: #{inspect(value)}"
    {:error, error} -> "Error: #{error}"
  end
end
```

**Why this translation:**
- Elixir uses tuples with atom tags for sum types
- Pattern matching works similarly but with tuples
- Type specs describe union types with `|`
- `{:ok, value}` / `{:error, reason}` is the idiomatic convention

---

### Pattern: For-Comprehension to For-Comprehension

**Scala:**
```scala
def getUserData(userId: Int): Option[User] = ???
def getOrders(user: User): Option[List[Order]] = ???
def calculateTotal(orders: List[Order]): Double = ???

val total: Option[Double] = for {
  user <- getUserData(123)
  orders <- getOrders(user)
} yield calculateTotal(orders)
```

**Elixir:**
```elixir
def get_user_data(user_id), do: # returns {:ok, user} | {:error, reason}
def get_orders(user), do: # returns {:ok, orders} | {:error, reason}
def calculate_total(orders), do: # returns float

# Using with construct (preferred for error handling)
def get_total(user_id) do
  with {:ok, user} <- get_user_data(user_id),
       {:ok, orders} <- get_orders(user) do
    {:ok, calculate_total(orders)}
  end
end

# Or using for comprehension
def get_total_for(user_id) do
  for {:ok, user} <- [get_user_data(user_id)],
      {:ok, orders} <- [get_orders(user)] do
    calculate_total(orders)
  end
end
```

**Why this translation:**
- Elixir's `with` construct is more idiomatic for chaining {:ok, _} results
- `for` works but is less common for this pattern
- `with` automatically propagates errors (no explicit error handling needed)

---

### Pattern: Trait to Protocol

**Scala:**
```scala
trait Serializable[A] {
  def toJson(value: A): String
}

object Serializable {
  implicit val intSerializable: Serializable[Int] = new Serializable[Int] {
    def toJson(value: Int): String = value.toString
  }

  implicit val stringSerializable: Serializable[String] = new Serializable[String] {
    def toJson(value: String): String = s""""$value""""
  }
}

def serialize[A](value: A)(implicit s: Serializable[A]): String =
  s.toJson(value)

serialize(42)        // "42"
serialize("hello")   // "\"hello\""
```

**Elixir:**
```elixir
defprotocol Serializable do
  @spec to_json(t) :: String.t()
  def to_json(value)
end

defimpl Serializable, for: Integer do
  def to_json(value), do: Integer.to_string(value)
end

defimpl Serializable, for: BitString do
  def to_json(value), do: ~s("#{value}")
end

# Usage
Serializable.to_json(42)       # "42"
Serializable.to_json("hello")  # "\"hello\""
```

**Why this translation:**
- Protocols in Elixir provide similar polymorphism to Scala type classes
- `defimpl` replaces implicit instances
- No implicit resolution - explicit protocol calls
- Protocols are open (can be extended for any type)

---

### Pattern: Future to Task/Process

**Scala:**
```scala
import scala.concurrent.{Future, ExecutionContext}
import scala.concurrent.ExecutionContext.Implicits.global

def fetchUser(id: Int): Future[User] = Future {
  // Blocking database call
  Database.findUser(id)
}

def fetchOrders(user: User): Future[List[Order]] = Future {
  Database.findOrders(user.id)
}

val result: Future[(User, List[Order])] = for {
  user <- fetchUser(123)
  orders <- fetchOrders(user)
} yield (user, orders)

result.foreach { case (user, orders) =>
  println(s"User ${user.name} has ${orders.size} orders")
}
```

**Elixir:**
```elixir
def fetch_user(id) do
  Task.async(fn ->
    # Database call
    Database.find_user(id)
  end)
end

def fetch_orders(user_id) do
  Task.async(fn ->
    Database.find_orders(user_id)
  end)
end

# Parallel execution
user_task = fetch_user(123)
user = Task.await(user_task)

orders_task = fetch_orders(user.id)
orders = Task.await(orders_task)

IO.puts("User #{user.name} has #{length(orders)} orders")

# Or using Task.async_stream for collections
user_ids = [1, 2, 3, 4, 5]
results =
  user_ids
  |> Task.async_stream(&fetch_user/1, max_concurrency: 10)
  |> Enum.to_list()
```

**Why this translation:**
- `Task` in Elixir is similar to `Future` but built on lightweight processes
- `Task.async` + `Task.await` for async/await pattern
- `Task.async_stream` for parallel collection processing
- No need for ExecutionContext - BEAM scheduler handles it

---

### Pattern: Akka Actor to GenServer

**Scala:**
```scala
import akka.actor.{Actor, ActorRef, Props}

case class Increment()
case class GetCount()
case class SetCount(value: Int)

class CounterActor extends Actor {
  var count: Int = 0

  def receive: Receive = {
    case Increment() =>
      count += 1
    case GetCount() =>
      sender() ! count
    case SetCount(value) =>
      count = value
  }
}

object CounterActor {
  def props(): Props = Props(new CounterActor)
}

// Usage
val counter = system.actorOf(CounterActor.props(), "counter")
counter ! Increment()
counter ! GetCount()
```

**Elixir:**
```elixir
defmodule CounterServer do
  use GenServer

  # Client API

  def start_link(opts \\ []) do
    GenServer.start_link(__MODULE__, :ok, opts ++ [name: __MODULE__])
  end

  def increment do
    GenServer.cast(__MODULE__, :increment)
  end

  def get_count do
    GenServer.call(__MODULE__, :get_count)
  end

  def set_count(value) do
    GenServer.cast(__MODULE__, {:set_count, value})
  end

  # Server Callbacks

  @impl true
  def init(:ok) do
    {:ok, %{count: 0}}
  end

  @impl true
  def handle_cast(:increment, state) do
    {:noreply, %{state | count: state.count + 1}}
  end

  @impl true
  def handle_cast({:set_count, value}, state) do
    {:noreply, %{state | count: value}}
  end

  @impl true
  def handle_call(:get_count, _from, state) do
    {:reply, state.count, state}
  end
end

# Usage
{:ok, _pid} = CounterServer.start_link()
CounterServer.increment()
count = CounterServer.get_count()
```

**Why this translation:**
- `GenServer` is Elixir's equivalent to Akka's typed actor pattern
- `use GenServer` imports behavior
- `handle_cast` for async messages (fire-and-forget)
- `handle_call` for sync messages (request-reply)
- State is immutable - return new state from handlers

---

### Pattern: Pattern Matching

**Scala:**
```scala
sealed trait HttpResponse
case class Ok(body: String) extends HttpResponse
case class NotFound(path: String) extends HttpResponse
case class ServerError(message: String) extends HttpResponse

def handleResponse(response: HttpResponse): String = response match {
  case Ok(body) => s"Success: $body"
  case NotFound(path) => s"Not found: $path"
  case ServerError(msg) => s"Error: $msg"
}

// List pattern matching
def sum(list: List[Int]): Int = list match {
  case Nil => 0
  case head :: tail => head + sum(tail)
}
```

**Elixir:**
```elixir
@type http_response ::
  {:ok, String.t()}
  | {:not_found, String.t()}
  | {:server_error, String.t()}

@spec handle_response(http_response()) :: String.t()
def handle_response(response) do
  case response do
    {:ok, body} -> "Success: #{body}"
    {:not_found, path} -> "Not found: #{path}"
    {:server_error, msg} -> "Error: #{msg}"
  end
end

# List pattern matching
def sum([]), do: 0
def sum([head | tail]), do: head + sum(tail)
```

**Why this translation:**
- Elixir uses tuples with atom tags for ADTs
- Pattern matching works directly in function heads (multi-clause functions)
- List syntax `[head | tail]` similar to Scala's `head :: tail`
- `case` expressions work identically

---

## Paradigm Translation

### Mental Model Shift: JVM OOP+FP → BEAM Pure FP

| Scala Concept | Elixir Approach | Key Insight |
|---------------|-----------------|-------------|
| Class with state | Struct + GenServer | Separate data from behavior |
| Inheritance | Protocol implementation | Favor protocols over hierarchies |
| Mutable var | Immutable + recursion | All data immutable |
| Thread pool | Process pool (lightweight) | Millions of processes possible |
| ExecutionContext | BEAM scheduler | Scheduler is always available |
| synchronized block | GenServer serialization | Message-based synchronization |
| Exception handling | {:ok, _} / {:error, _} tuples | Errors as values |

### Concurrency Mental Model

| Scala Model | Elixir Model | Conceptual Translation |
|-------------|--------------|------------------------|
| Future[A] | Task | Async computation |
| Akka Actor | GenServer / Process | Stateful concurrent entity |
| ExecutionContext | BEAM Scheduler | Work distribution |
| Ask pattern | GenServer.call | Synchronous request |
| Tell pattern | GenServer.cast | Asynchronous message |
| Supervision | Supervisor | Fault tolerance |
| Thread | Process (lightweight) | Concurrent execution unit |

---

## Error Handling

### Scala Try/Either → Elixir Tuples

**Scala:**
```scala
import scala.util.{Try, Success, Failure}

def parseNumber(s: String): Try[Int] =
  Try(s.toInt)

def divide(a: Int, b: Int): Either[String, Int] =
  if (b == 0) Left("Division by zero")
  else Right(a / b)

// Chaining with for-comprehension
def calculate(x: String, y: String): Either[String, Int] = {
  for {
    a <- parseNumber(x).toEither.left.map(_ => "Invalid x")
    b <- parseNumber(y).toEither.left.map(_ => "Invalid y")
    result <- divide(a, b)
  } yield result
}
```

**Elixir:**
```elixir
@spec parse_number(String.t()) :: {:ok, integer()} | {:error, :invalid}
def parse_number(s) do
  case Integer.parse(s) do
    {num, ""} -> {:ok, num}
    _ -> {:error, :invalid}
  end
end

@spec divide(integer(), integer()) :: {:ok, integer()} | {:error, :division_by_zero}
def divide(_a, 0), do: {:error, :division_by_zero}
def divide(a, b), do: {:ok, div(a, b)}

# Chaining with `with` construct
@spec calculate(String.t(), String.t()) :: {:ok, integer()} | {:error, atom()}
def calculate(x, y) do
  with {:ok, a} <- parse_number(x),
       {:ok, b} <- parse_number(y),
       {:ok, result} <- divide(a, b) do
    {:ok, result}
  else
    {:error, :invalid} -> {:error, :invalid_input}
    {:error, reason} -> {:error, reason}
  end
end
```

**Why this translation:**
- `{:ok, value}` / `{:error, reason}` is idiomatic Elixir
- `with` construct chains operations, short-circuits on first error
- Explicit error handling with pattern matching
- No exceptions thrown for expected errors

### Exception Handling

**Scala:**
```scala
def readFile(path: String): Try[String] = Try {
  scala.io.Source.fromFile(path).mkString
}

// With explicit exception handling
def safeDivide(a: Int, b: Int): Try[Int] = {
  try {
    Success(a / b)
  } catch {
    case _: ArithmeticException => Failure(new Exception("Division by zero"))
    case e: Exception => Failure(e)
  }
}
```

**Elixir:**
```elixir
@spec read_file(String.t()) :: {:ok, String.t()} | {:error, File.posix()}
def read_file(path) do
  File.read(path)
end

# With explicit exception handling (rare - prefer tuples)
def safe_divide(a, b) do
  try do
    {:ok, div(a, b)}
  rescue
    ArithmeticError -> {:error, :division_by_zero}
    e in [File.Error, RuntimeError] -> {:error, e.message}
  end
end

# Better: use guards
def safe_divide(_a, 0), do: {:error, :division_by_zero}
def safe_divide(a, b), do: {:ok, div(a, b)}
```

**Why this translation:**
- Elixir uses `try/rescue` for exceptions, but prefers tuples
- `rescue` is like Scala's `catch`
- Pattern match on error types
- Guards prevent errors at function head

---

## Concurrency Patterns

### Scala Future → Elixir Task

**Scala:**
```scala
import scala.concurrent.Future
import scala.concurrent.ExecutionContext.Implicits.global

val users: Future[List[User]] = Future {
  Database.findAllUsers()
}

val enriched: Future[List[EnrichedUser]] = users.flatMap { userList =>
  Future.traverse(userList) { user =>
    Future {
      enrichWithOrders(user)
    }
  }
}

enriched.foreach { result =>
  println(s"Processed ${result.size} users")
}
```

**Elixir:**
```elixir
# Simple async task
task = Task.async(fn ->
  Database.find_all_users()
end)

users = Task.await(task, 5000)  # 5 second timeout

# Parallel processing of list
enriched =
  users
  |> Task.async_stream(&enrich_with_orders/1, max_concurrency: 10, timeout: 5000)
  |> Enum.map(fn {:ok, result} -> result end)

IO.puts("Processed #{length(enriched)} users")

# Or using processes directly
users
|> Enum.each(fn user ->
  Task.start(fn ->
    process_user(user)
  end)
end)
```

**Why this translation:**
- `Task.async` + `Task.await` mirrors Future semantics
- `Task.async_stream` for concurrent collection processing
- Built-in timeout support (no need for Await.result)
- Lightweight processes instead of thread pools

### Akka Stream → Elixir Stream/Flow

**Scala:**
```scala
import akka.stream.scaladsl._

val source = Source(1 to 1000)
  .map(_ * 2)
  .filter(_ % 3 == 0)
  .grouped(10)
  .mapAsync(4)(batch => Future {
    processBatch(batch)
  })
  .runFold(0)(_ + _)
```

**Elixir:**
```elixir
# Using Stream (lazy)
result =
  1..1000
  |> Stream.map(&(&1 * 2))
  |> Stream.filter(&(rem(&1, 3) == 0))
  |> Stream.chunk_every(10)
  |> Task.async_stream(&process_batch/1, max_concurrency: 4)
  |> Enum.reduce(0, fn {:ok, val}, acc -> acc + val end)

# Using Flow (parallel + lazy)
alias Experimental.Flow

result =
  1..1000
  |> Flow.from_enumerable()
  |> Flow.map(&(&1 * 2))
  |> Flow.filter(&(rem(&1, 3) == 0))
  |> Flow.partition()
  |> Flow.reduce(fn -> 0 end, &(&1 + &2))
  |> Enum.sum()
```

**Why this translation:**
- `Stream` provides lazy evaluation like Akka Source
- `Task.async_stream` for concurrent processing
- `Flow` library for advanced parallel stream processing
- No need for explicit materialization

---

## Memory & Ownership

### JVM GC → BEAM GC

| JVM (Scala) | BEAM (Elixir) | Key Difference |
|-------------|---------------|----------------|
| Shared heap | Per-process heap | Each process has isolated memory |
| Stop-the-world GC | Per-process GC | GC pauses isolated to single process |
| Object references | Immutable data copying | Data copied between processes |
| Memory leaks possible | Leaks die with process | Process death frees all memory |

**Key insights:**
- Elixir processes have tiny isolated heaps (measured in KB)
- No stop-the-world pauses - each process GCs independently
- Immutability + copying prevents shared state bugs
- Process crash = automatic memory reclamation

---

## Build and Dependencies

### sbt → Mix

**Scala (build.sbt):**
```scala
name := "my-app"
version := "0.1.0"
scalaVersion := "3.3.1"

libraryDependencies ++= Seq(
  "com.typesafe.akka" %% "akka-actor-typed" % "2.8.5",
  "org.typelevel" %% "cats-core" % "2.10.0",
  "io.circe" %% "circe-core" % "0.14.6"
)
```

**Elixir (mix.exs):**
```elixir
defmodule MyApp.MixProject do
  use Mix.Project

  def project do
    [
      app: :my_app,
      version: "0.1.0",
      elixir: "~> 1.15",
      deps: deps()
    ]
  end

  def application do
    [
      extra_applications: [:logger],
      mod: {MyApp.Application, []}
    ]
  end

  defp deps do
    [
      {:phoenix, "~> 1.7"},
      {:jason, "~> 1.4"},
      {:httpoison, "~> 2.0"}
    ]
  end
end
```

### Common Task Mapping

| sbt | Mix | Purpose |
|-----|-----|---------|
| `sbt compile` | `mix compile` | Compile project |
| `sbt run` | `mix run` | Run application |
| `sbt test` | `mix test` | Run tests |
| `sbt console` | `iex -S mix` | Interactive REPL |
| `sbt clean` | `mix clean` | Clean build |
| `sbt ~compile` | `mix compile --watch` | Watch mode |
| `sbt assembly` | `mix release` | Build deployable artifact |

---

## Testing Strategy

### ScalaTest → ExUnit

**Scala:**
```scala
import org.scalatest.flatspec.AnyFlatSpec
import org.scalatest.matchers.should.Matchers

class UserSpec extends AnyFlatSpec with Matchers {
  "User" should "have valid email" in {
    val user = User("Alice", "alice@example.com")
    user.email should include("@")
  }

  it should "handle optional age" in {
    val user = User("Bob", "bob@example.com", Some(30))
    user.age shouldBe Some(30)
  }
}
```

**Elixir:**
```elixir
defmodule UserTest do
  use ExUnit.Case, async: true

  describe "User" do
    test "has valid email" do
      user = %User{name: "Alice", email: "alice@example.com"}
      assert String.contains?(user.email, "@")
    end

    test "handles optional age" do
      user = %User{name: "Bob", email: "bob@example.com", age: 30}
      assert user.age == 30
    end

    test "handles nil age" do
      user = %User{name: "Charlie", email: "charlie@example.com", age: nil}
      assert is_nil(user.age)
    end
  end
end
```

---

## REPL Workflow

### Scala REPL/Ammonite → IEx

Both Scala and Elixir are REPL-centric languages with strong interactive development workflows.

**Scala (Ammonite):**
```scala
// Start REPL
$ amm

// Load file
@ import $file.MyModule

// Hot reload
@ import $ivy.`com.lihaoyi::requests:0.8.0`

// Inspect types
scala> :type myVariable
```

**Elixir (IEx):**
```elixir
# Start REPL with project
$ iex -S mix

# Recompile after changes
iex> recompile()

# Load module
iex> c "lib/my_module.ex"

# Introspection
iex> h Enum.map
iex> i my_variable

# Hot code reloading in production
iex> :code.purge(MyModule)
iex> :code.load_file(MyModule)
```

**Key differences:**
- IEx supports hot code reloading in production (BEAM feature)
- Scala REPL is faster at compile-edit-test cycle for type checking
- Elixir's observer for live system inspection: `:observer.start()`

---

## Common Pitfalls

### 1. Forgetting Elixir is Dynamically Typed

```elixir
# WRONG - Type errors caught at runtime, not compile time
def add(a, b), do: a + b
add("hello", 5)  # Runtime error

# BETTER - Use guards
def add(a, b) when is_integer(a) and is_integer(b), do: a + b

# BEST - Use Dialyzer typespecs
@spec add(integer(), integer()) :: integer()
def add(a, b), do: a + b
```

### 2. Null vs Nil Confusion

```scala
// Scala
val x: Option[Int] = None
val y: Int = x.getOrElse(0)
```

```elixir
# Elixir - nil is just an atom
x = nil
y = x || 0  # Short-circuit evaluation

# Pattern matching on nil
case x do
  nil -> 0
  value -> value
end
```

### 3. String vs Charlist

```elixir
# WRONG
string = 'hello'  # This is a charlist!
String.upcase(string)  # Error

# CORRECT
string = "hello"  # Binary string
String.upcase(string)  # "HELLO"

# Charlist (for Erlang interop)
charlist = 'hello'
:string.uppercase(charlist)  # 'HELLO'
```

### 4. Immutability in Both Languages

```scala
// Scala - val is immutable
val list = List(1, 2, 3)
list = list :+ 4  // Compile error
```

```elixir
# Elixir - rebinding is allowed
list = [1, 2, 3]
list = list ++ [4]  # OK - creates new list

# Use pin operator to prevent rebinding
^list = [1, 2, 3, 4]  # Match error if list != [1,2,3,4]
```

### 5. Process Isolation

```elixir
# WRONG - Trying to share mutable state
defmodule Counter do
  @count 0  # Module attribute, not mutable

  def increment do
    @count = @count + 1  # Compile error
  end
end

# CORRECT - Use GenServer for stateful processes
defmodule Counter do
  use GenServer

  def init(_), do: {:ok, 0}

  def handle_call(:increment, _from, count) do
    {:reply, count + 1, count + 1}
  end
end
```

### 6. Akka Ask Pattern Timeout

```scala
// Scala Akka
implicit val timeout = Timeout(5.seconds)
val future = actor ? GetCount
```

```elixir
# Elixir GenServer
count = GenServer.call(CounterServer, :get_count, 5000)  # 5 second timeout
```

---

## Tooling

| Scala | Elixir | Purpose |
|-------|--------|---------|
| sbt | Mix | Build tool |
| Ammonite | IEx | Enhanced REPL |
| ScalaTest | ExUnit | Testing framework |
| ScalaCheck | StreamData | Property-based testing |
| Akka | OTP | Concurrency framework |
| Cats/Scalaz | (built-in) | FP abstractions |
| Circe | Jason/Poison | JSON library |
| Scala CLI | Mix scripts | Scripting |
| Metals | ElixirLS | Language server |
| Scalafmt | mix format | Code formatter |

---

## Examples

### Example 1: Simple - Option Handling

**Before (Scala):**
```scala
def findUser(id: Int): Option[User] = {
  if (id > 0) Some(User(id, "Alice"))
  else None
}

val result = findUser(1) match {
  case Some(user) => s"Found: ${user.name}"
  case None => "Not found"
}
```

**After (Elixir):**
```elixir
def find_user(id) when id > 0, do: {:ok, %User{id: id, name: "Alice"}}
def find_user(_id), do: {:error, :not_found}

result = case find_user(1) do
  {:ok, user} -> "Found: #{user.name}"
  {:error, :not_found} -> "Not found"
end
```

---

### Example 2: Medium - Error Handling Chain

**Before (Scala):**
```scala
import scala.util.{Try, Success, Failure}

def validateEmail(email: String): Either[String, String] =
  if (email.contains("@")) Right(email)
  else Left("Invalid email")

def createUser(name: String, email: String): Either[String, User] = {
  for {
    validEmail <- validateEmail(email)
  } yield User(name = name, email = validEmail)
}

def saveUser(user: User): Try[User] = Try {
  // Database save
  user
}

def registerUser(name: String, email: String): Either[String, User] = {
  createUser(name, email) match {
    case Right(user) =>
      saveUser(user) match {
        case Success(saved) => Right(saved)
        case Failure(ex) => Left(s"DB error: ${ex.getMessage}")
      }
    case Left(error) => Left(error)
  }
}
```

**After (Elixir):**
```elixir
def validate_email(email) do
  if String.contains?(email, "@") do
    {:ok, email}
  else
    {:error, :invalid_email}
  end
end

def create_user(name, email) do
  with {:ok, valid_email} <- validate_email(email) do
    {:ok, %User{name: name, email: valid_email}}
  end
end

def save_user(user) do
  # Database save
  {:ok, user}
rescue
  e -> {:error, "DB error: #{inspect(e)}"}
end

def register_user(name, email) do
  with {:ok, user} <- create_user(name, email),
       {:ok, saved} <- save_user(user) do
    {:ok, saved}
  end
end
```

---

### Example 3: Complex - Concurrent Data Processing

**Before (Scala):**
```scala
import scala.concurrent.{Future, ExecutionContext}
import scala.concurrent.duration._
import akka.actor.ActorSystem
import akka.stream.scaladsl._

implicit val system: ActorSystem = ActorSystem("processor")
implicit val ec: ExecutionContext = system.dispatcher

case class Order(id: Int, userId: Int, total: Double)
case class EnrichedOrder(order: Order, userName: String)

def fetchOrders(): Future[List[Order]] = Future {
  // Database call
  (1 to 100).map(i => Order(i, i % 10, i * 10.0)).toList
}

def fetchUserName(userId: Int): Future[String] = Future {
  s"User-$userId"
}

def enrichOrder(order: Order): Future[EnrichedOrder] = {
  fetchUserName(order.userId).map { userName =>
    EnrichedOrder(order, userName)
  }
}

def processOrders(): Future[List[EnrichedOrder]] = {
  for {
    orders <- fetchOrders()
    enriched <- Future.traverse(orders)(enrichOrder)
  } yield enriched
}

// Using Akka Streams for backpressure
def processOrdersStream(): Future[List[EnrichedOrder]] = {
  Source.future(fetchOrders())
    .mapConcat(identity)
    .mapAsync(10)(enrichOrder)
    .runWith(Sink.seq)
    .map(_.toList)
}
```

**After (Elixir):**
```elixir
defmodule OrderProcessor do
  @moduledoc """
  Concurrent order processing with Task.async_stream
  """

  defmodule Order do
    defstruct [:id, :user_id, :total]
  end

  defmodule EnrichedOrder do
    defstruct [:order, :user_name]
  end

  def fetch_orders do
    # Database call
    orders = for i <- 1..100 do
      %Order{id: i, user_id: rem(i, 10), total: i * 10.0}
    end
    {:ok, orders}
  end

  def fetch_user_name(user_id) do
    # Simulate async call
    Process.sleep(10)
    "User-#{user_id}"
  end

  def enrich_order(%Order{} = order) do
    user_name = fetch_user_name(order.user_id)
    %EnrichedOrder{order: order, user_name: user_name}
  end

  # Using Task.async_stream for concurrent processing
  def process_orders do
    with {:ok, orders} <- fetch_orders() do
      enriched =
        orders
        |> Task.async_stream(&enrich_order/1,
             max_concurrency: 10,
             timeout: 5000)
        |> Enum.map(fn {:ok, result} -> result end)

      {:ok, enriched}
    end
  end

  # Using Flow for advanced parallel processing
  def process_orders_flow do
    alias Experimental.Flow

    with {:ok, orders} <- fetch_orders() do
      enriched =
        orders
        |> Flow.from_enumerable(max_demand: 10)
        |> Flow.map(&enrich_order/1)
        |> Enum.to_list()

      {:ok, enriched}
    end
  end

  # Using GenStage for backpressure (like Akka Streams)
  defmodule OrderProducer do
    use GenStage

    def start_link(orders) do
      GenStage.start_link(__MODULE__, orders)
    end

    def init(orders) do
      {:producer, orders}
    end

    def handle_demand(demand, orders) do
      {to_send, remaining} = Enum.split(orders, demand)
      {:noreply, to_send, remaining}
    end
  end

  defmodule OrderProcessor do
    use GenStage

    def start_link() do
      GenStage.start_link(__MODULE__, :ok)
    end

    def init(:ok) do
      {:producer_consumer, :ok}
    end

    def handle_events(orders, _from, state) do
      enriched = Enum.map(orders, &enrich_order/1)
      {:noreply, enriched, state}
    end
  end
end
```

**Key differences:**
- Elixir uses `Task.async_stream` for simple concurrent collection processing
- `Flow` library provides parallel streaming similar to Akka Streams
- `GenStage` for advanced backpressure and producer-consumer patterns
- No need for ExecutionContext - BEAM scheduler handles everything
- Timeout built into Task functions
- Simpler error handling with `{:ok, _}` tuples

---

## See Also

For more examples and patterns, see:
- `meta-convert-dev` - Foundational patterns with cross-language examples
- `convert-erlang-elixir` - Related BEAM conversion (Erlang → Elixir)
- `convert-elixir-scala` - Reverse conversion (Elixir → Scala)
- `lang-scala-dev` - Scala development patterns
- `lang-scala-akka-dev` - Akka-specific patterns
- `lang-elixir-dev` - Elixir development patterns
- `lang-elixir-otp-dev` - Advanced OTP patterns

Cross-cutting pattern skills:
- `patterns-concurrency-dev` - Async, actors, processes across languages
- `patterns-serialization-dev` - JSON, validation across languages
