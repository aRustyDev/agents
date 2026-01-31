---
name: convert-elixir-scala
description: Convert Elixir code to idiomatic Scala. Use when migrating Elixir/Phoenix applications to Scala, translating BEAM OTP patterns to Akka actors, or refactoring dynamic concurrency to statically-typed JVM patterns. Extends meta-convert-dev with Elixir-to-Scala specific patterns.
---

# Convert Elixir to Scala

Convert Elixir code to idiomatic Scala. This skill extends `meta-convert-dev` with Elixir-to-Scala specific type mappings, idiom translations, and tooling for translating between BEAM VM's dynamic actors and JVM's statically-typed Akka actors.

## This Skill Extends

- `meta-convert-dev` - Foundational conversion patterns (APTV workflow, testing strategies)

For general concepts like the Analyze → Plan → Transform → Validate workflow, testing strategies, and common pitfalls, see the meta-skill first.

## This Skill Adds

- **Type mappings**: Elixir types (dynamic) → Scala types (static)
- **Idiom translations**: Elixir patterns → idiomatic Scala with type safety
- **Runtime transition**: BEAM VM (lightweight processes) → JVM (Akka actors/Futures)
- **Concurrency models**: GenServer/Supervisor → Akka actors with typed protocols
- **OTP patterns**: Supervision trees → Akka supervision hierarchies
- **Data structures**: Elixir maps/structs → Scala case classes
- **Error handling**: {:ok/:error} tuples → Either/Try monads
- **Build tools**: Mix → sbt/Mill

## This Skill Does NOT Cover

- General conversion methodology - see `meta-convert-dev`
- Elixir language fundamentals - see `lang-elixir-dev`
- Scala language fundamentals - see `lang-scala-dev`
- Reverse conversion (Scala → Elixir) - see `convert-scala-elixir`
- Phoenix framework specifics - see `lang-scala-play-dev` for web frameworks

---

## Quick Reference

| Elixir | Scala | Notes |
|--------|-------|-------|
| `:atom` | Symbol / sealed trait | Atoms → sealed traits for exhaustiveness |
| `{:ok, value}` | `Right(value)` | Result tuples → Either/Try |
| `{:error, reason}` | `Left(reason)` | Error tuples → Either |
| `%{key: value}` | `Map("key" -> value)` | Maps require type parameters |
| `[1, 2, 3]` | `List(1, 2, 3)` | Lists immutable by default |
| `defmodule Module` | `object Module` | Module → singleton object |
| `def func(x)` | `def func(x: Type): ReturnType` | Functions require type signatures |
| `fn x -> x end` | `(x: Type) => x` | Anonymous functions |
| `\|>` (pipe) | `.map().flatMap()` | Pipe → method chaining |
| `GenServer` | `Actor[Protocol]` | Typed actors in Akka |
| `Supervisor` | `ActorSystem` / `Behaviors.supervise` | Supervision strategies |
| `Task.async` | `Future { }` | Async execution |
| Pattern matching | `match/case` | Similar but with static types |

---

## 8 Pillars Validation

### Elixir Coverage

| Pillar | Coverage | Status |
|--------|----------|--------|
| Module System | ✓ | defmodule, alias, import, use |
| Error Handling | ✓ | {:ok/:error} tuples, pattern matching, try/rescue |
| Concurrency Model | ✓ | Processes, GenServer, Supervisor, Task |
| Metaprogramming | ✓ | Macros, use directive, compile-time generation |
| Zero/Default Values | ✓ | nil, pattern matching with defaults |
| Serialization | ✓ | Phoenix params, Jason/Poison, Ecto |
| Build/Deps | ✓ | Mix, hex.pm, deps management |
| Testing Idioms | ✓ | ExUnit, doctests, Mox for mocking |

**Score: 8/8 (Green)**

### Scala Coverage

| Pillar | Coverage | Status |
|--------|----------|--------|
| Module System | ✓ | Packages, objects, imports, traits |
| Error Handling | ✓ | Either, Try, Option, exceptions |
| Concurrency Model | ✓ | Futures, Akka actors, Cats Effect IO |
| Metaprogramming | ✓ | Macros (Scala 2), inline/metaprogramming (Scala 3) |
| Zero/Default Values | ✓ | Option, default parameters, null (avoid) |
| Serialization | ✓ | Play JSON, Circe, uPickle, case classes |
| Build/Deps | ✓ | sbt, Mill, Maven Central |
| Testing Idioms | ✓ | ScalaTest, ScalaCheck, MUnit, specs2 |

**Score: 8/8 (Green)**

**Validation Status:** ✅ Both languages have comprehensive coverage. Conversion can proceed with confidence.

**Key Challenge:** Elixir's dynamic typing to Scala's static typing requires careful type inference and explicit type annotations.

---

## Type System Mapping

### Primitive Types

| Elixir | Scala | Notes |
|--------|-------|-------|
| `:atom` | `Symbol` / sealed trait | Use sealed traits for ADTs |
| `integer` | `Int` / `Long` / `BigInt` | Choose based on range needs |
| `float` | `Double` | 64-bit floating point |
| `true` / `false` | `Boolean` | Direct mapping |
| `nil` | `None` / `null` (avoid) | Prefer Option[T] |
| `"string"` | `String` | Immutable strings |
| `'charlist'` | `List[Char]` | Less common in Scala |

### Collection Types

| Elixir | Scala | Notes |
|--------|-------|-------|
| `[1, 2, 3]` | `List(1, 2, 3)` | Immutable linked lists |
| `{:ok, value}` | `Right(value): Either[Error, Value]` | Tagged tuples → Either |
| `{a, b, c}` | `(a, b, c): (A, B, C)` | Tuples map directly |
| `%{a: 1, b: 2}` | `Map("a" -> 1, "b" -> 2)` | Immutable maps |
| `MapSet.new([1, 2])` | `Set(1, 2)` | Immutable sets |
| Keyword list | `List[(Symbol, A)]` | Less common in Scala |
| Range `1..10` | `Range(1, 11)` | Inclusive → exclusive end |

### Composite Types

| Elixir | Scala | Notes |
|--------|-------|-------|
| `defstruct [:name, :age]` | `case class User(name: String, age: Int)` | Structs → case classes |
| `%User{name: "Alice"}` | `User("Alice", 30)` | Constructor syntax |
| `@type user :: %{name: String.t()}` | `type User = Map[String, Any]` | Type aliases |
| `@spec func(integer) :: String.t()` | `def func(x: Int): String` | Function signatures required |
| Protocol | Trait | Polymorphism via traits |

---

## Idiom Translation

### Pattern: Module Definition

**Elixir:**
```elixir
defmodule MyApp.Users do
  @moduledoc """
  Handles user-related operations.
  """

  alias MyApp.Repo
  import Ecto.Query

  @type user :: %{id: integer, name: String.t()}

  @spec get_user(integer) :: {:ok, user} | {:error, :not_found}
  def get_user(id) do
    case Repo.get(User, id) do
      nil -> {:error, :not_found}
      user -> {:ok, user}
    end
  end

  defp build_query(filters) do
    from u in User, where: ^filters
  end
end
```

**Scala:**
```scala
package myapp

/**
 * Handles user-related operations.
 */
object Users {
  import myapp.repo.Repo
  import myapp.models.User

  type UserId = Int
  type UserResult = Either[UserError, User]

  sealed trait UserError
  case object NotFound extends UserError

  def getUser(id: UserId): UserResult = {
    Repo.get[User](id) match {
      case Some(user) => Right(user)
      case None => Left(NotFound)
    }
  }

  private def buildQuery(filters: Map[String, Any]): Query = {
    Query.from[User].where(filters)
  }
}
```

**Why this translation:**
- `defmodule` → `object` (singleton)
- `@moduledoc` → Scaladoc `/** */`
- `@type` → `type` alias with explicit types
- `@spec` → method signature with types
- `{:ok/:error}` tuples → `Either[Error, Value]`
- Pattern matching on nil → `Option.match`
- CamelCase modules → package + object structure

---

### Pattern: Pattern Matching to Case Classes

**Elixir:**
```elixir
def process_response({:ok, %{"data" => data, "meta" => meta}}) do
  {:success, data, meta}
end

def process_response({:error, reason}) do
  {:failure, reason}
end

def handle_user(%User{name: name, age: age}) when age >= 18 do
  "Adult: #{name}"
end
```

**Scala:**
```scala
sealed trait Response
case class Success(data: String, meta: Map[String, Any]) extends Response
case class Error(reason: String) extends Response

def processResponse(response: Response): Result = response match {
  case Success(data, meta) =>
    SuccessResult(data, meta)
  case Error(reason) =>
    FailureResult(reason)
}

case class User(name: String, age: Int)

def handleUser(user: User): Option[String] = user match {
  case User(name, age) if age >= 18 =>
    Some(s"Adult: $name")
  case _ =>
    None
}
```

**Why this translation:**
- Multiple function clauses → sealed trait with case classes
- Guards → pattern guards with `if` in match
- Struct pattern matching → case class pattern matching
- Tag tuples → sealed trait hierarchy for type safety
- Exhaustiveness checking enforced by compiler

---

### Pattern: Pipelines to Method Chaining

**Elixir:**
```elixir
def process_data(input) do
  input
  |> String.trim()
  |> String.downcase()
  |> String.split(",")
  |> Enum.map(&String.trim/1)
  |> Enum.reject(&(&1 == ""))
  |> Enum.join(";")
end
```

**Scala:**
```scala
def processData(input: String): String = {
  input
    .trim
    .toLowerCase
    .split(",")
    .map(_.trim)
    .filterNot(_.isEmpty)
    .mkString(";")
}

// Or with explicit types for clarity
def processData(input: String): String = {
  val trimmed: String = input.trim
  val lowercased: String = trimmed.toLowerCase
  val parts: Array[String] = lowercased.split(",")
  val cleaned: Array[String] = parts.map(_.trim).filterNot(_.isEmpty)
  cleaned.mkString(";")
}
```

**Why this translation:**
- `|>` → method chaining (`.`)
- Enum functions → collection methods
- Capture operator `&func/arity` → anonymous functions `_`
- `Enum.reject` → `filterNot`
- `Enum.join` → `mkString`

---

### Pattern: GenServer to Akka Typed Actor

**Elixir:**
```elixir
defmodule UserCache do
  use GenServer

  # Client API

  def start_link(opts) do
    GenServer.start_link(__MODULE__, opts, name: __MODULE__)
  end

  def get(key) do
    GenServer.call(__MODULE__, {:get, key})
  end

  def put(key, value) do
    GenServer.cast(__MODULE__, {:put, key, value})
  end

  # Server Callbacks

  @impl true
  def init(_opts) do
    {:ok, %{}}
  end

  @impl true
  def handle_call({:get, key}, _from, state) do
    {:reply, Map.get(state, key), state}
  end

  @impl true
  def handle_cast({:put, key, value}, state) do
    {:noreply, Map.put(state, key, value)}
  end
end
```

**Scala (Akka Typed):**
```scala
import akka.actor.typed._
import akka.actor.typed.scaladsl.Behaviors

object UserCache {
  // Protocol
  sealed trait Command
  final case class Get(key: String, replyTo: ActorRef[Option[String]])
    extends Command
  final case class Put(key: String, value: String)
    extends Command

  // Behavior
  def apply(): Behavior[Command] = {
    behavior(Map.empty[String, String])
  }

  private def behavior(cache: Map[String, String]): Behavior[Command] = {
    Behaviors.receive { (context, message) =>
      message match {
        case Get(key, replyTo) =>
          replyTo ! cache.get(key)
          Behaviors.same

        case Put(key, value) =>
          behavior(cache + (key -> value))
      }
    }
  }
}

// Usage
val system: ActorSystem[UserCache.Command] =
  ActorSystem(UserCache(), "user-cache-system")

implicit val timeout: Timeout = 3.seconds
val futureResult: Future[Option[String]] =
  system.ask(ref => UserCache.Get("key", ref))
```

**Why this translation:**
- `GenServer` → Akka Typed `Actor[Protocol]`
- Message tuples → sealed trait protocol
- `handle_call` → synchronous message handling with `ask` pattern
- `handle_cast` → asynchronous message handling
- State recursion → immutable state updates
- Type safety enforced at compile time

---

### Pattern: Supervisor to Akka Supervision

**Elixir:**
```elixir
defmodule MyApp.Application do
  use Application

  @impl true
  def start(_type, _args) do
    children = [
      {UserCache, []},
      {MyWorker, name: MyWorker, restart: :transient},
      {Registry, keys: :unique, name: MyApp.Registry}
    ]

    opts = [strategy: :one_for_one, name: MyApp.Supervisor]
    Supervisor.start_link(children, opts)
  end
end
```

**Scala (Akka Typed):**
```scala
import akka.actor.typed._
import akka.actor.typed.scaladsl._

object MyApp {
  sealed trait RootCommand

  def apply(): Behavior[RootCommand] = {
    Behaviors.setup { context =>
      // Spawn supervised children
      val userCache = context.spawn(
        UserCache(),
        "user-cache"
      )

      val worker = context.spawn(
        Behaviors.supervise(MyWorker())
          .onFailure[Exception](SupervisorStrategy.restart),
        "my-worker"
      )

      // Root behavior
      Behaviors.receiveMessage { message =>
        Behaviors.same
      }
    }
  }
}

// Starting the system
val system = ActorSystem(MyApp(), "my-app-system")
```

**Why this translation:**
- Supervision tree → `Behaviors.setup` with spawned children
- `:one_for_one` → individual supervision per actor
- `:transient` restart → `SupervisorStrategy.restart.withLimit`
- Named processes → named actors via `spawn`
- Declarative children list → imperative spawn calls

---

## Error Handling

### Elixir Error Model → Scala Error Model

**Elixir uses tagged tuples:**

```elixir
def divide(a, b) when b != 0, do: {:ok, a / b}
def divide(_, 0), do: {:error, :division_by_zero}

# Usage
case divide(10, 2) do
  {:ok, result} -> "Result: #{result}"
  {:error, reason} -> "Error: #{reason}"
end

# Or with pattern matching
{:ok, result} = divide(10, 2)
```

**Scala uses Either/Try monads:**

```scala
sealed trait MathError
case object DivisionByZero extends MathError

def divide(a: Double, b: Double): Either[MathError, Double] = {
  if (b != 0) Right(a / b)
  else Left(DivisionByZero)
}

// Usage with pattern matching
divide(10, 2) match {
  case Right(result) => s"Result: $result"
  case Left(error) => s"Error: $error"
}

// Or with for-comprehension
val result = for {
  x <- divide(10, 2)
  y <- divide(x, 5)
} yield y

// Or with Try for exceptions
import scala.util.{Try, Success, Failure}

def divideWithTry(a: Double, b: Double): Try[Double] = {
  Try(a / b)
}

divideWithTry(10, 0) match {
  case Success(value) => s"Result: $value"
  case Failure(exception) => s"Error: ${exception.getMessage}"
}
```

**Translation strategy:**
1. `{:ok, value}` → `Right(value): Either[Error, Value]`
2. `{:error, reason}` → `Left(reason): Either[Error, Value]`
3. Define error ADT with sealed trait
4. Use for-comprehensions for chaining operations
5. Consider `Try` for exception-based code

---

## Concurrency Patterns

### Elixir Async → Scala Async

**Elixir Task-based async:**

```elixir
def fetch_user_data(user_id) do
  task1 = Task.async(fn -> fetch_profile(user_id) end)
  task2 = Task.async(fn -> fetch_orders(user_id) end)
  task3 = Task.async(fn -> fetch_preferences(user_id) end)

  profile = Task.await(task1)
  orders = Task.await(task2)
  preferences = Task.await(task3)

  %{profile: profile, orders: orders, preferences: preferences}
end
```

**Scala Future-based async:**

```scala
import scala.concurrent.{Future, Await}
import scala.concurrent.duration._
import scala.concurrent.ExecutionContext.Implicits.global

def fetchUserData(userId: Int): Future[UserData] = {
  val profileF = Future { fetchProfile(userId) }
  val ordersF = Future { fetchOrders(userId) }
  val preferencesF = Future { fetchPreferences(userId) }

  for {
    profile <- profileF
    orders <- ordersF
    preferences <- preferencesF
  } yield UserData(profile, orders, preferences)
}

// Or with Applicative for parallel execution
import cats.implicits._

def fetchUserDataParallel(userId: Int): Future[UserData] = {
  (
    Future { fetchProfile(userId) },
    Future { fetchOrders(userId) },
    Future { fetchPreferences(userId) }
  ).mapN(UserData.apply)
}
```

**Why this translation:**
- `Task.async` → `Future { }`
- `Task.await` → `Await.result` (avoid) or for-comprehension
- Parallel execution → spawn all Futures immediately
- Sequential composition → for-comprehension
- Use Cats for applicative parallel composition

---

### Process Message Passing → Actor Tell/Ask

**Elixir:**

```elixir
defmodule Counter do
  def start do
    spawn(fn -> loop(0) end)
  end

  defp loop(count) do
    receive do
      {:increment, caller} ->
        send(caller, {:ok, count + 1})
        loop(count + 1)

      {:get, caller} ->
        send(caller, {:ok, count})
        loop(count)

      :stop ->
        :ok
    end
  end
end

# Usage
counter = Counter.start()
send(counter, {:increment, self()})
receive do
  {:ok, new_value} -> IO.puts("New value: #{new_value}")
end
```

**Scala (Akka Typed):**

```scala
object Counter {
  sealed trait Command
  case class Increment(replyTo: ActorRef[Response]) extends Command
  case class Get(replyTo: ActorRef[Response]) extends Command
  case object Stop extends Command

  sealed trait Response
  case class Value(count: Int) extends Response

  def apply(initialCount: Int): Behavior[Command] = {
    counter(initialCount)
  }

  private def counter(count: Int): Behavior[Command] = {
    Behaviors.receive { (context, message) =>
      message match {
        case Increment(replyTo) =>
          replyTo ! Value(count + 1)
          counter(count + 1)

        case Get(replyTo) =>
          replyTo ! Value(count)
          Behaviors.same

        case Stop =>
          Behaviors.stopped
      }
    }
  }
}

// Usage
val system = ActorSystem(Counter(0), "counter-system")
implicit val timeout: Timeout = 3.seconds

val futureCount: Future[Counter.Value] =
  system.ask(ref => Counter.Get(ref))
```

**Why this translation:**
- `spawn` → `ActorSystem` / `context.spawn`
- `send` → actor `!` (tell) operator
- `receive` → `Behaviors.receive` pattern matching
- Message tuples → sealed trait protocol
- Tail recursion → return new behavior

---

## Common Pitfalls

### 1. Dynamic Typing → Static Typing

**Problem:** Elixir allows dynamic typing; Scala requires explicit types.

```elixir
# Elixir - dynamic
def process(data) do
  case data do
    x when is_integer(x) -> x * 2
    x when is_binary(x) -> String.length(x)
    x when is_list(x) -> length(x)
  end
end
```

**Solution:** Use sealed trait ADT for type safety.

```scala
sealed trait Data
case class IntData(value: Int) extends Data
case class StringData(value: String) extends Data
case class ListData[A](values: List[A]) extends Data

def process(data: Data): Int = data match {
  case IntData(x) => x * 2
  case StringData(x) => x.length
  case ListData(xs) => xs.length
}
```

---

### 2. Pattern Match Exhaustiveness

**Problem:** Elixir warns on non-exhaustive matches; Scala errors.

```elixir
# Elixir - warning only
def handle({:ok, value}), do: value
# Missing {:error, _} case
```

**Solution:** Always handle all cases or use sealed traits.

```scala
sealed trait Result[+A]
case class Success[A](value: A) extends Result[A]
case class Failure(error: String) extends Result[Nothing]

def handle[A](result: Result[A]): A = result match {
  case Success(value) => value
  case Failure(error) => throw new Exception(error)
  // Compiler enforces exhaustiveness
}
```

---

### 3. Nil Safety

**Problem:** Elixir has `nil`; Scala should use `Option`.

```elixir
# Elixir
user = Repo.get(User, id)  # Can be nil
name = user.name           # Runtime error if nil
```

**Solution:** Use Option type.

```scala
val user: Option[User] = Repo.get[User](id)
val name: Option[String] = user.map(_.name)

// Or with for-comprehension
val name = for {
  u <- user
} yield u.name
```

---

### 4. Immutability by Convention → Enforced

**Problem:** Elixir immutability is by convention; Scala enforces it.

```elixir
# Elixir - creates new map
map = %{a: 1}
new_map = Map.put(map, :b, 2)
```

**Solution:** Use `val` and immutable collections.

```scala
val map = Map("a" -> 1)
val newMap = map + ("b" -> 2)  // Creates new map

// Avoid var and mutable collections
var mutableMap = scala.collection.mutable.Map("a" -> 1)  // Avoid
```

---

### 5. Process Supervision → Actor Supervision

**Problem:** Different restart semantics and error handling.

**Elixir:**
```elixir
# Let it crash - supervisor restarts
def handle_call(:dangerous, _from, state) do
  result = do_dangerous_operation()  # Might crash
  {:reply, result, state}
end
```

**Scala:**
```scala
// Must handle errors explicitly or define supervision strategy
Behaviors.supervise {
  Behaviors.receiveMessage {
    case Dangerous =>
      try {
        val result = doDangerousOperation()
        Behaviors.same
      } catch {
        case e: Exception =>
          throw e  // Supervisor handles via strategy
      }
  }
}.onFailure[Exception](SupervisorStrategy.restart)
```

---

## Tooling

| Category | Elixir | Scala | Notes |
|----------|--------|-------|-------|
| **Build Tool** | Mix | sbt, Mill | Mill is more modern |
| **Package Manager** | Hex | Maven Central | sbt resolves dependencies |
| **REPL** | iex | scala / ammonite | Ammonite more feature-rich |
| **Formatter** | mix format | scalafmt | Both auto-format |
| **Linter** | Credo | scalafix, Wartremover | Scala has multiple |
| **Testing** | ExUnit | ScalaTest, MUnit | Multiple test frameworks |
| **Property Testing** | StreamData | ScalaCheck | Similar concepts |
| **Actor System** | OTP | Akka | Akka Typed recommended |
| **Web Framework** | Phoenix | Play, Http4s, Akka HTTP | Play most similar |
| **DB** | Ecto | Slick, Doobie, Quill | Different approaches |
| **JSON** | Jason, Poison | Circe, Play JSON, uPickle | Macro-based derivation |
| **HTTP Client** | HTTPoison, Tesla | sttp, http4s-client | Functional HTTP clients |

---

## Examples

### Example 1: Simple - Data Transformation

**Before (Elixir):**
```elixir
defmodule DataProcessor do
  def transform_user(%{name: name, age: age}) do
    %{
      display_name: String.upcase(name),
      is_adult: age >= 18,
      category: categorize_age(age)
    }
  end

  defp categorize_age(age) when age < 13, do: :child
  defp categorize_age(age) when age < 20, do: :teenager
  defp categorize_age(_), do: :adult
end
```

**After (Scala):**
```scala
object DataProcessor {
  case class User(name: String, age: Int)

  sealed trait AgeCategory
  case object Child extends AgeCategory
  case object Teenager extends AgeCategory
  case object Adult extends AgeCategory

  case class TransformedUser(
    displayName: String,
    isAdult: Boolean,
    category: AgeCategory
  )

  def transformUser(user: User): TransformedUser = {
    TransformedUser(
      displayName = user.name.toUpperCase,
      isAdult = user.age >= 18,
      category = categorizeAge(user.age)
    )
  }

  private def categorizeAge(age: Int): AgeCategory = age match {
    case a if a < 13 => Child
    case a if a < 20 => Teenager
    case _ => Adult
  }
}
```

---

### Example 2: Medium - Error Handling Pipeline

**Before (Elixir):**
```elixir
defmodule UserRegistration do
  def register(params) do
    with {:ok, validated} <- validate_params(params),
         {:ok, user} <- create_user(validated),
         {:ok, _email} <- send_welcome_email(user) do
      {:ok, user}
    else
      {:error, :invalid_email} -> {:error, "Email is invalid"}
      {:error, :user_exists} -> {:error, "User already exists"}
      {:error, reason} -> {:error, "Registration failed: #{reason}"}
    end
  end

  defp validate_params(%{email: email, password: password})
    when byte_size(password) >= 8 do
    if valid_email?(email) do
      {:ok, %{email: email, password: password}}
    else
      {:error, :invalid_email}
    end
  end
  defp validate_params(_), do: {:error, :invalid_params}
end
```

**After (Scala):**
```scala
object UserRegistration {
  case class UserParams(email: String, password: String)
  case class User(id: Int, email: String)

  sealed trait RegistrationError
  case object InvalidEmail extends RegistrationError
  case object UserExists extends RegistrationError
  case class GeneralError(message: String) extends RegistrationError

  type RegistrationResult = Either[RegistrationError, User]

  def register(params: UserParams): RegistrationResult = {
    for {
      validated <- validateParams(params)
      user <- createUser(validated)
      _ <- sendWelcomeEmail(user)
    } yield user
  }

  private def validateParams(
    params: UserParams
  ): Either[RegistrationError, UserParams] = {
    if (params.password.length < 8) {
      Left(GeneralError("Password too short"))
    } else if (!validEmail(params.email)) {
      Left(InvalidEmail)
    } else {
      Right(params)
    }
  }

  private def createUser(
    params: UserParams
  ): Either[RegistrationError, User] = {
    // Database logic
    Right(User(1, params.email))
  }

  private def sendWelcomeEmail(
    user: User
  ): Either[RegistrationError, Unit] = {
    // Email logic
    Right(())
  }

  private def validEmail(email: String): Boolean = {
    email.contains("@")
  }
}
```

---

### Example 3: Complex - GenServer to Akka Actor with State

**Before (Elixir):**
```elixir
defmodule RateLimiter do
  use GenServer
  require Logger

  defstruct requests: %{}, window_ms: 60_000, max_requests: 100

  # Client API

  def start_link(opts) do
    GenServer.start_link(__MODULE__, opts, name: __MODULE__)
  end

  def check_rate(user_id) do
    GenServer.call(__MODULE__, {:check_rate, user_id})
  end

  def reset(user_id) do
    GenServer.cast(__MODULE__, {:reset, user_id})
  end

  # Server Callbacks

  @impl true
  def init(opts) do
    state = %__MODULE__{
      window_ms: Keyword.get(opts, :window_ms, 60_000),
      max_requests: Keyword.get(opts, :max_requests, 100)
    }
    {:ok, state}
  end

  @impl true
  def handle_call({:check_rate, user_id}, _from, state) do
    now = System.system_time(:millisecond)
    requests = Map.get(state.requests, user_id, [])

    # Filter out expired requests
    valid_requests =
      Enum.filter(requests, fn ts ->
        now - ts < state.window_ms
      end)

    count = length(valid_requests)

    if count < state.max_requests do
      new_requests = [now | valid_requests]
      new_state = put_in(state.requests[user_id], new_requests)
      {:reply, {:ok, state.max_requests - count - 1}, new_state}
    else
      {:reply, {:error, :rate_limit_exceeded}, state}
    end
  end

  @impl true
  def handle_cast({:reset, user_id}, state) do
    new_state = put_in(state.requests[user_id], [])
    {:noreply, new_state}
  end

  @impl true
  def handle_info(:cleanup, state) do
    now = System.system_time(:millisecond)

    new_requests =
      state.requests
      |> Enum.map(fn {user_id, requests} ->
        valid = Enum.filter(requests, fn ts ->
          now - ts < state.window_ms
        end)
        {user_id, valid}
      end)
      |> Enum.into(%{})

    Process.send_after(self(), :cleanup, 60_000)
    {:noreply, %{state | requests: new_requests}}
  end
end
```

**After (Scala with Akka Typed):**
```scala
import akka.actor.typed._
import akka.actor.typed.scaladsl._
import scala.concurrent.duration._

object RateLimiter {
  // Protocol
  sealed trait Command
  final case class CheckRate(
    userId: String,
    replyTo: ActorRef[RateResponse]
  ) extends Command
  final case class Reset(userId: String) extends Command
  private case object Cleanup extends Command

  // Responses
  sealed trait RateResponse
  final case class Allowed(remaining: Int) extends RateResponse
  case object RateLimitExceeded extends RateResponse

  // Configuration
  case class Config(
    windowMs: Long = 60000,
    maxRequests: Int = 100
  )

  // State
  private case class State(
    requests: Map[String, List[Long]],
    config: Config
  )

  def apply(config: Config = Config()): Behavior[Command] = {
    Behaviors.setup { context =>
      Behaviors.withTimers { timers =>
        timers.startTimerWithFixedDelay(Cleanup, 60.seconds)
        active(State(Map.empty, config), context)
      }
    }
  }

  private def active(
    state: State,
    context: ActorContext[Command]
  ): Behavior[Command] = {
    Behaviors.receiveMessage {
      case CheckRate(userId, replyTo) =>
        val now = System.currentTimeMillis()
        val requests = state.requests.getOrElse(userId, List.empty)

        // Filter expired requests
        val validRequests = requests.filter { ts =>
          now - ts < state.config.windowMs
        }

        val count = validRequests.length

        if (count < state.config.maxRequests) {
          val newRequests = now :: validRequests
          val newState = state.copy(
            requests = state.requests + (userId -> newRequests)
          )
          replyTo ! Allowed(state.config.maxRequests - count - 1)
          active(newState, context)
        } else {
          replyTo ! RateLimitExceeded
          Behaviors.same
        }

      case Reset(userId) =>
        val newState = state.copy(
          requests = state.requests - userId
        )
        active(newState, context)

      case Cleanup =>
        val now = System.currentTimeMillis()
        val cleaned = state.requests.map { case (userId, requests) =>
          val valid = requests.filter { ts =>
            now - ts < state.config.windowMs
          }
          userId -> valid
        }.filter(_._2.nonEmpty)

        active(state.copy(requests = cleaned), context)
    }
  }
}

// Usage
val system: ActorSystem[RateLimiter.Command] =
  ActorSystem(RateLimiter(RateLimiter.Config()), "rate-limiter")

implicit val timeout: Timeout = 3.seconds
val futureResponse: Future[RateLimiter.RateResponse] =
  system.ask(ref => RateLimiter.CheckRate("user123", ref))
```

---

## See Also

For more examples and patterns, see:

- `meta-convert-dev` - Foundational patterns with cross-language examples
- `convert-scala-elixir` - Reverse conversion (Scala → Elixir)
- `lang-elixir-dev` - Elixir development patterns
- `lang-scala-dev` - Scala development patterns
- `lang-scala-akka-dev` - Advanced Akka patterns

Cross-cutting pattern skills:

- `patterns-concurrency-dev` - Async, actors, processes across languages
- `patterns-serialization-dev` - JSON, validation across languages
- `patterns-metaprogramming-dev` - Macros, code generation across languages
