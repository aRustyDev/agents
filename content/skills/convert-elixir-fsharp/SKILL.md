---
name: convert-elixir-fsharp
description: Bidirectional conversion between Elixir and Fsharp. Use when migrating projects between these languages in either direction. Extends meta-convert-dev with Elixir↔Fsharp specific patterns.
---

# Convert Elixir to F#

Convert Elixir code to idiomatic F#. This skill extends `meta-convert-dev` with Elixir-to-F# specific type mappings, idiom translations, and tooling for transforming dynamic, actor-based Elixir code into functional-first, statically-typed F# on the .NET platform.

## This Skill Extends

- `meta-convert-dev` - Foundational conversion patterns (APTV workflow, testing strategies)

For general concepts like the Analyze → Plan → Transform → Validate workflow, testing strategies, and common pitfalls, see the meta-skill first.

## This Skill Adds

- **Type mappings**: Elixir dynamic types → F# static types with inference
- **Idiom translations**: Elixir pipelines/pattern matching → F# functional patterns
- **Error handling**: Tagged tuples {:ok, value} → Result<'T,'E>/Option<'T>
- **Concurrency patterns**: GenServer/processes → MailboxProcessor/async workflows
- **Runtime translation**: BEAM VM → .NET CLR with async/await
- **Collection patterns**: Elixir lists/maps → F# immutable collections

## This Skill Does NOT Cover

- General conversion methodology - see `meta-convert-dev`
- Elixir language fundamentals - see `lang-elixir-dev`
- F# language fundamentals - see `lang-fsharp-dev`
- OTP distributed systems - requires architectural redesign for .NET

---

## Quick Reference

| Elixir | F# | Notes |
|--------|------|-------|
| `atom()` | Discriminated union or `string` | :ok → Ok case, :error → Error case |
| `integer()` | `int`, `int64`, `bigint` | F# int is 32-bit |
| `float()` | `float` | 64-bit double precision |
| `binary()` | `string` or `byte[]` | UTF-8 binary → UTF-16 string |
| `list()` | `List<'T>` | Both immutable, F# is singly-linked |
| `tuple()` | `'T * 'U * ...` | Direct mapping |
| `map()` | `Map<'K, 'V>` | Immutable maps |
| `keyword list` | `List<'K * 'V>` | List of tuples |
| `pid()` | `MailboxProcessor<'T>` | Actor-style processing |
| `GenServer` | `MailboxProcessor` + state loop | Actor pattern with message handling |
| `Task` | `Async<'T>` or `Task<'T>` | Async computations |
| `Stream` | `Seq<'T>` | Lazy sequences |
| `{:ok, value}` | `Ok value` (Result type) | Success case |
| `{:error, reason}` | `Error reason` (Result type) | Error case |
| `nil` | `None` (Option type) | Explicit nullable |

---

## When Converting Code

1. **Analyze source thoroughly** before writing target
2. **Map types first** - create type equivalence table, especially for atoms
3. **Preserve functional semantics** - both languages are functional-first
4. **Translate actor patterns carefully** - GenServer → MailboxProcessor requires state management
5. **Use F# type inference** - let compiler infer types when possible
6. **Railway-oriented programming** - translate {:ok, _}/{:error, _} to Result<'T,'E>
7. **Leverage pipe operator** - Elixir |> maps directly to F# |>
8. **Test equivalence** - same inputs → same outputs

---

## Type System Mapping

### Primitive Types

| Elixir | F# | Notes |
|--------|------|-------|
| `integer()` (small) | `int` | 32-bit signed integer |
| `integer()` (large) | `int64` | 64-bit signed integer |
| `integer()` (arbitrary) | `bigint` | Arbitrary precision |
| `float()` | `float` | 64-bit IEEE 754 |
| `boolean()` | `bool` | true/false |
| `atom()` | Discriminated union | :ok, :error, etc. → DU cases |
| `binary()` (text) | `string` | UTF-8 → UTF-16 |
| `binary()` (bytes) | `byte[]` | Raw bytes |
| `bitstring()` | Custom type | No direct equivalent |
| `nil` | `None` in `Option<'T>` | Must be wrapped |
| `reference()` | - | No direct equivalent |
| `port()` | - | BEAM-specific |

**Critical Note on Atoms**: Elixir atoms are compile-time constants used extensively for tagging (`:ok`, `:error`, `:atom_name`). In F#, translate to:
- **Discriminated unions** for fixed sets (`:ok`/`:error` → `Result` type)
- **Strings** for dynamic/user-defined atoms
- **Enums** for simple value sets

### Collection Types

| Elixir | F# | Notes |
|--------|------|-------|
| `list()` | `List<'T>` | Both immutable, singly-linked |
| `[h \| t]` pattern | `head :: tail` pattern | List destructuring |
| `tuple()` | `'T * 'U * ...` | Fixed-size product types |
| `map()` | `Map<'K, 'V>` | Immutable tree-based map |
| `%{atom_key: value}` | Record type `{ AtomKey: 'T }` | Atom-keyed maps → records |
| `%{string_key => value}` | `Map<string, 'T>` | String-keyed maps |
| `keyword list` | `List<string * 'T>` | `[key: value]` → list of tuples |
| `MapSet` | `Set<'T>` | Immutable set |
| `Range` | `seq { start..end }` | Lazy range |
| `Stream` | `Seq<'T>` | Lazy sequences |

### Composite Types

| Elixir | F# | Notes |
|--------|------|-------|
| `struct` | `type Record = { }` | Elixir structs → F# records |
| `@type` | `type` alias | Type aliases |
| Tagged tuple | Discriminated union | `{:ok, value}` → `Ok value` |
| `@callback` | Interface | Module behaviors → interfaces |
| `defprotocol` | Interface or type class | Protocol → interface |
| `defimpl` | Interface implementation | Implementation |

---

## Idiom Translation

### Pattern 1: Pipe Operator (Direct Translation)

**Elixir:**
```elixir
# Pipeline processing
"hello world"
|> String.upcase()
|> String.reverse()
|> String.split("")
|> Enum.join("-")
```

**F#:**
```fsharp
// Direct translation - pipe works the same!
"hello world"
|> String.toUpper
|> String.rev
|> Seq.toArray
|> String.concat "-"

// Or with built-in functions
"hello world"
|> (fun s -> s.ToUpper())
|> Seq.rev
|> String.concat "-"
```

**Why this translation:**
- Both languages use `|>` for left-to-right function chaining
- F# and Elixir share functional pipeline philosophy
- Minor differences in standard library function names

### Pattern 2: Pattern Matching on Tagged Tuples

**Elixir:**
```elixir
# Pattern matching on result tuples
case File.read("config.json") do
  {:ok, contents} ->
    Jason.decode(contents)
  {:error, :enoent} ->
    {:error, "File not found"}
  {:error, reason} ->
    {:error, "Read error: #{inspect(reason)}"}
end
```

**F#:**
```fsharp
// Using Result type with pattern matching
match System.IO.File.ReadAllText("config.json") |> tryRead with
| Ok contents ->
    Json.decode contents
| Error FileNotFound ->
    Error "File not found"
| Error (ReadError reason) ->
    Error $"Read error: {reason}"

// Helper to convert exceptions to Result
let tryRead path =
    try
        Ok (System.IO.File.ReadAllText(path))
    with
    | :? System.IO.FileNotFoundException -> Error FileNotFound
    | ex -> Error (ReadError ex.Message)
```

**Why this translation:**
- Elixir's `{:ok, value}` / `{:error, reason}` maps directly to F#'s `Result<'T, 'E>`
- Pattern matching syntax is similar in both languages
- F# requires explicit error type definition

### Pattern 3: with Statement → Result Computation Expression

**Elixir:**
```elixir
# Chain operations that can fail
def create_user(params) do
  with {:ok, validated} <- validate_params(params),
       {:ok, user} <- insert_user(validated),
       {:ok, email} <- send_welcome_email(user) do
    {:ok, user}
  else
    {:error, reason} -> {:error, reason}
  end
end
```

**F#:**
```fsharp
// Result computation expression
type ResultBuilder() =
    member _.Bind(x, f) = Result.bind f x
    member _.Return(x) = Ok x
    member _.ReturnFrom(x) = x

let result = ResultBuilder()

let createUser params =
    result {
        let! validated = validateParams params
        let! user = insertUser validated
        let! email = sendWelcomeEmail user
        return user
    }

// Or using built-in Result.bind (more verbose)
let createUser params =
    validateParams params
    |> Result.bind insertUser
    |> Result.bind (fun user ->
        sendWelcomeEmail user
        |> Result.map (fun _ -> user))
```

**Why this translation:**
- Elixir's `with` statement is railway-oriented programming
- F# computation expressions provide the same short-circuiting behavior
- `let!` in F# unwraps Result like `<-` unwraps tuples in Elixir

### Pattern 4: GenServer → MailboxProcessor

**Elixir:**
```elixir
defmodule Counter do
  use GenServer

  # Client API
  def start_link(initial_value) do
    GenServer.start_link(__MODULE__, initial_value, name: __MODULE__)
  end

  def increment do
    GenServer.call(__MODULE__, :increment)
  end

  def get do
    GenServer.call(__MODULE__, :get)
  end

  # Server Callbacks
  @impl true
  def init(initial_value) do
    {:ok, initial_value}
  end

  @impl true
  def handle_call(:increment, _from, state) do
    {:reply, state + 1, state + 1}
  end

  def handle_call(:get, _from, state) do
    {:reply, state, state}
  end
end
```

**F#:**
```fsharp
module Counter =
    // Message types (discriminated union)
    type Message =
        | Increment of AsyncReplyChannel<int>
        | Get of AsyncReplyChannel<int>

    // Agent wrapping MailboxProcessor
    type CounterAgent(initialValue: int) =
        let agent = MailboxProcessor.Start(fun inbox ->
            let rec loop state = async {
                let! msg = inbox.Receive()
                match msg with
                | Increment reply ->
                    let newState = state + 1
                    reply.Reply(newState)
                    return! loop newState
                | Get reply ->
                    reply.Reply(state)
                    return! loop state
            }
            loop initialValue
        )

        member _.Increment() = agent.PostAndReply(Increment)
        member _.Get() = agent.PostAndReply(Get)

    // Client API
    let start initialValue = CounterAgent(initialValue)
```

**Why this translation:**
- Both GenServer and MailboxProcessor implement the actor pattern
- F# uses discriminated unions for message types (typed vs Elixir's atoms)
- `AsyncReplyChannel` in F# replaces Elixir's `from` parameter for synchronous calls
- Recursive `loop` function maintains state like Elixir's callback chain

### Pattern 5: Enum Functions → List/Seq Functions

**Elixir:**
```elixir
# Enum operations
numbers = [1, 2, 3, 4, 5]

doubled = Enum.map(numbers, fn x -> x * 2 end)
evens = Enum.filter(numbers, fn x -> rem(x, 2) == 0 end)
sum = Enum.reduce(numbers, 0, fn x, acc -> x + acc end)

# With pipe operator
result =
  [1, 2, 3, 4, 5]
  |> Enum.filter(&(rem(&1, 2) == 0))
  |> Enum.map(&(&1 * 2))
  |> Enum.sum()
```

**F#:**
```fsharp
// List operations
let numbers = [1; 2; 3; 4; 5]

let doubled = numbers |> List.map (fun x -> x * 2)
let evens = numbers |> List.filter (fun x -> x % 2 = 0)
let sum = numbers |> List.fold (+) 0

// With pipe operator (idiomatic F#)
let result =
    [1; 2; 3; 4; 5]
    |> List.filter (fun x -> x % 2 = 0)
    |> List.map (fun x -> x * 2)
    |> List.sum

// Using Seq for lazy evaluation (like Elixir Stream)
let lazyResult =
    seq { 1..5 }
    |> Seq.filter (fun x -> x % 2 = 0)
    |> Seq.map (fun x -> x * 2)
    |> Seq.sum
```

**Why this translation:**
- Elixir `Enum` → F# `List` for eager evaluation
- Elixir `Stream` → F# `Seq` for lazy evaluation
- Function names are similar: `map`, `filter`, `reduce`/`fold`
- Both languages use pipe operator idiomatically

### Pattern 6: Structs → Records

**Elixir:**
```elixir
defmodule User do
  defstruct [:name, :email, age: 0, active: true]

  def new(name, email) do
    %User{name: name, email: email}
  end

  def activate(%User{} = user) do
    %{user | active: true}
  end
end

# Usage
user = %User{name: "Alice", email: "alice@example.com"}
user = User.activate(user)
```

**F#:**
```fsharp
module User =
    // Record type (immutable by default)
    type User = {
        Name: string
        Email: string
        Age: int
        Active: bool
    }

    // Constructor with defaults
    let create name email =
        { Name = name
          Email = email
          Age = 0
          Active = true }

    // Update function (returns new record)
    let activate user =
        { user with Active = true }

// Usage
let user = User.create "Alice" "alice@example.com"
let activeUser = User.activate user
```

**Why this translation:**
- Elixir structs and F# records are both immutable by default
- Copy-and-update syntax is similar: `%{user | ...}` vs `{ user with ... }`
- F# records have structural equality automatically (like Elixir structs)

---

## Error Handling

### Elixir Tagged Tuples → F# Result Type

**Elixir's error model:**
```elixir
# Return tagged tuples
def divide(a, b) when b != 0, do: {:ok, a / b}
def divide(_, 0), do: {:error, :division_by_zero}

# Pattern match on result
case divide(10, 2) do
  {:ok, result} -> "Result: #{result}"
  {:error, :division_by_zero} -> "Cannot divide by zero"
end

# With operator for chaining
with {:ok, a} <- divide(10, 2),
     {:ok, b} <- divide(20, 4),
     {:ok, c} <- divide(a, b) do
  {:ok, c}
else
  {:error, reason} -> {:error, reason}
end
```

**F# Result type (idiomatic):**
```fsharp
// Define error type
type MathError =
    | DivisionByZero

// Function returns Result<'T, 'E>
let divide a b =
    if b = 0.0 then
        Error DivisionByZero
    else
        Ok (a / b)

// Pattern match on result
let message =
    match divide 10.0 2.0 with
    | Ok result -> $"Result: {result}"
    | Error DivisionByZero -> "Cannot divide by zero"

// Result computation expression for chaining
let result =
    result {
        let! a = divide 10.0 2.0
        let! b = divide 20.0 4.0
        let! c = divide a b
        return c
    }
```

**Translation guidelines:**
- `{:ok, value}` → `Ok value`
- `{:error, reason}` → `Error reason`
- Atom errors (`:not_found`, `:timeout`) → discriminated union cases
- String errors remain strings or become union cases with data
- `with` statement → `result { }` computation expression

### Option Type for Nullable Values

**Elixir:**
```elixir
# nil represents absence
def find_user(id) do
  case Repo.get(User, id) do
    nil -> nil
    user -> user
  end
end

# Pattern matching on nil
case find_user(123) do
  nil -> "User not found"
  user -> "Found: #{user.name}"
end
```

**F#:**
```fsharp
// Option type for nullable
let findUser id =
    match Repo.get<User> id with
    | null -> None
    | user -> Some user

// Pattern matching on Option
match findUser 123 with
| None -> "User not found"
| Some user -> $"Found: {user.Name}"

// Or with Option.map
findUser 123
|> Option.map (fun user -> $"Found: {user.Name}")
|> Option.defaultValue "User not found"
```

**Translation guidelines:**
- `nil` → `None` (but wrapped in `Option<'T>`)
- Present value → `Some value`
- Pattern match or use `Option` module functions

---

## Concurrency Patterns

### Elixir Processes → F# MailboxProcessor

**Elixir process communication:**
```elixir
# Spawn process
pid = spawn(fn ->
  receive do
    {:hello, sender} -> send(sender, {:ok, "Hello back!"})
  end
end)

# Send message
send(pid, {:hello, self()})

# Receive response
receive do
  {:ok, message} -> IO.puts(message)
after
  1000 -> IO.puts("Timeout!")
end
```

**F# MailboxProcessor:**
```fsharp
// Message type
type Message =
    | Hello of AsyncReplyChannel<string>

// Create mailbox processor
let processor = MailboxProcessor.Start(fun inbox ->
    async {
        let! msg = inbox.Receive()
        match msg with
        | Hello reply ->
            reply.Reply("Hello back!")
    }
)

// Send and receive (synchronous)
let message = processor.PostAndReply(Hello)
printfn "%s" message

// Or asynchronous with timeout
let! result = processor.PostAndAsyncReply(Hello, timeout = 1000)
match result with
| Some message -> printfn "%s" message
| None -> printfn "Timeout!"
```

**Translation guidelines:**
- `spawn(fn -> ... end)` → `MailboxProcessor.Start(fun inbox -> async { ... })`
- `receive do ... end` → `let! msg = inbox.Receive()`
- `send(pid, msg)` → `processor.Post(msg)` (async) or `PostAndReply` (sync)
- Elixir atoms for message tags → F# discriminated union cases

### Task/async-await Pattern

**Elixir:**
```elixir
# Async task
task1 = Task.async(fn -> fetch_data("url1") end)
task2 = Task.async(fn -> fetch_data("url2") end)

# Await results
result1 = Task.await(task1)
result2 = Task.await(task2)

# Parallel map
results =
  ["url1", "url2", "url3"]
  |> Task.async_stream(&fetch_data/1)
  |> Enum.to_list()
```

**F#:**
```fsharp
// Async computation
let task1 = async { return fetchData "url1" }
let task2 = async { return fetchData "url2" }

// Await results
let! result1 = task1
let! result2 = task2

// Parallel execution
let results =
    ["url1"; "url2"; "url3"]
    |> List.map (fun url -> async { return fetchData url })
    |> Async.Parallel
    |> Async.RunSynchronously

// Or with Task<'T> (closer to .NET idioms)
let task1 = Task.Run(fun () -> fetchData "url1")
let task2 = Task.Run(fun () -> fetchData "url2")

let results = Task.WaitAll([| task1; task2 |])
```

**Translation guidelines:**
- `Task.async(fn -> ... end)` → `async { ... }` or `Task.Run`
- `Task.await(task)` → `let! result = task` (in async block)
- `Task.async_stream` → `Async.Parallel` or parallel LINQ
- Elixir Task is eager; F# `Async<'T>` is lazy (runs when awaited)

### Supervision Pattern

**Elixir:**
```elixir
defmodule MyApp.Application do
  use Application

  def start(_type, _args) do
    children = [
      {Stack, []},
      {MyWorker, name: MyWorker, restart: :transient}
    ]

    opts = [strategy: :one_for_one, name: MyApp.Supervisor]
    Supervisor.start_link(children, opts)
  end
end
```

**F# (using Akka.NET or custom supervision):**
```fsharp
// Custom supervision with restart logic
module Supervisor =
    type SupervisedAgent<'State, 'Msg>(
        initialState: 'State,
        handler: MailboxProcessor<'Msg> -> 'State -> 'Msg -> Async<'State>) =

        let mutable agent = None

        let rec start() =
            let a = MailboxProcessor.Start(fun inbox ->
                let rec loop state = async {
                    try
                        let! msg = inbox.Receive()
                        let! newState = handler inbox state msg
                        return! loop newState
                    with
                    | ex ->
                        printfn "Agent crashed: %s" ex.Message
                        // Restart with initial state
                        return! loop initialState
                }
                loop initialState
            )
            agent <- Some a
            a

        member _.Agent = agent |> Option.defaultWith start

// Or use Akka.NET for production OTP-like supervision
open Akka.Actor
open Akka.FSharp

let system = System.create "my-system" (Configuration.load())

let supervisor = spawn system "supervisor" (fun mailbox ->
    // Akka.NET provides OTP-like supervision strategies
    actorOf2 (fun mailbox ->
        actor {
            // Actor logic
        })
)
```

**Translation guidelines:**
- Simple supervision: custom restart logic with MailboxProcessor
- Complex supervision: use Akka.NET (F#-friendly OTP alternative)
- Restart strategies map: `:one_for_one`, `:one_for_all`, `:rest_for_one`
- F# lacks built-in supervision; requires libraries or custom implementation

---

## Common Pitfalls

1. **Atom explosion**: Elixir atoms are lightweight; F# strings are not. Use discriminated unions for fixed sets of atoms to get compile-time safety.

2. **Dynamic typing assumptions**: Elixir's dynamic typing allows `%{id: 1, name: "Alice"}` and `%{id: 2, age: 30}` in the same list. F# requires consistent types—use discriminated unions for heterogeneous data.

3. **Process registry**: Elixir's process registry (named processes) doesn't have a direct F# equivalent. Use dependency injection or singleton patterns for named services.

4. **Hot code swapping**: BEAM's hot code swapping is not available on .NET. Plan for deployment downtime or use blue-green deployment strategies.

5. **String encoding**: Elixir binaries are UTF-8; .NET strings are UTF-16. Be careful with string/binary conversion, especially for protocols.

6. **Pattern matching on strings**: Elixir can pattern match on binary structure (`<<a, b, rest::binary>>`). F# requires imperative slicing or active patterns.

7. **Lazy evaluation differences**: Elixir `Stream` is pull-based lazy; F# `Seq` is also lazy but behaves slightly differently with side effects.

8. **Async cancellation**: Elixir processes can be killed easily; F# async requires CancellationToken propagation.

---

## Tooling

| Tool | Purpose | Notes |
|------|---------|-------|
| **dotnet CLI** | Build, run, test F# projects | `dotnet build`, `dotnet run` |
| **Ionide** | VS Code F# extension | Provides IntelliSense, linting |
| **Paket** | Alternative package manager | Deterministic dependency resolution |
| **FAKE** | Build automation | F# Make (like Mix tasks) |
| **Expecto** | Testing framework | Similar to ExUnit |
| **FsCheck** | Property-based testing | Like Elixir's StreamData |
| **Akka.NET** | Actor framework | OTP-like supervision and distribution |
| **Giraffe** | Web framework | Functional HTTP (like Phoenix) |

---

## Examples

### Example 1: Simple - Pattern Matching and Recursion

**Before (Elixir):**
```elixir
defmodule Math do
  # Factorial using pattern matching
  def factorial(0), do: 1
  def factorial(n) when n > 0, do: n * factorial(n - 1)

  # FizzBuzz with pattern matching
  def fizzbuzz(n) do
    case {rem(n, 3), rem(n, 5)} do
      {0, 0} -> "FizzBuzz"
      {0, _} -> "Fizz"
      {_, 0} -> "Buzz"
      _ -> to_string(n)
    end
  end
end
```

**After (F#):**
```fsharp
module Math =
    // Factorial using pattern matching
    let rec factorial n =
        match n with
        | 0 -> 1
        | n when n > 0 -> n * factorial (n - 1)
        | _ -> failwith "Negative input not allowed"

    // FizzBuzz with pattern matching
    let fizzbuzz n =
        match (n % 3, n % 5) with
        | (0, 0) -> "FizzBuzz"
        | (0, _) -> "Fizz"
        | (_, 0) -> "Buzz"
        | _ -> string n
```

### Example 2: Medium - Error Handling with Result

**Before (Elixir):**
```elixir
defmodule UserService do
  def register_user(params) do
    with {:ok, email} <- validate_email(params["email"]),
         {:ok, password} <- validate_password(params["password"]),
         {:ok, user} <- create_user(email, password),
         {:ok, _} <- send_welcome_email(user) do
      {:ok, user}
    else
      {:error, :invalid_email} -> {:error, "Invalid email format"}
      {:error, :weak_password} -> {:error, "Password too weak"}
      {:error, :email_taken} -> {:error, "Email already registered"}
      {:error, reason} -> {:error, "Registration failed: #{reason}"}
    end
  end

  defp validate_email(email) when is_binary(email) do
    if String.contains?(email, "@") do
      {:ok, email}
    else
      {:error, :invalid_email}
    end
  end

  defp validate_password(password) when byte_size(password) >= 8 do
    {:ok, password}
  end
  defp validate_password(_), do: {:error, :weak_password}

  defp create_user(email, password) do
    # Simulate database insert
    if email == "taken@example.com" do
      {:error, :email_taken}
    else
      {:ok, %{id: 1, email: email, password_hash: hash_password(password)}}
    end
  end

  defp send_welcome_email(user) do
    # Simulate email sending
    {:ok, user}
  end

  defp hash_password(password), do: :crypto.hash(:sha256, password)
end
```

**After (F#):**
```fsharp
module UserService =
    // Error type
    type RegistrationError =
        | InvalidEmail
        | WeakPassword
        | EmailTaken
        | RegistrationFailed of string

    // User type
    type User = {
        Id: int
        Email: string
        PasswordHash: byte[]
    }

    // Result computation expression
    type ResultBuilder() =
        member _.Bind(x, f) = Result.bind f x
        member _.Return(x) = Ok x
        member _.ReturnFrom(x) = x

    let result = ResultBuilder()

    // Validation functions
    let validateEmail email =
        if String.contains email "@" then
            Ok email
        else
            Error InvalidEmail

    let validatePassword password =
        if String.length password >= 8 then
            Ok password
        else
            Error WeakPassword

    let hashPassword password =
        use sha256 = System.Security.Cryptography.SHA256.Create()
        Text.Encoding.UTF8.GetBytes(password)
        |> sha256.ComputeHash

    let createUser email password =
        // Simulate database insert
        if email = "taken@example.com" then
            Error EmailTaken
        else
            Ok { Id = 1; Email = email; PasswordHash = hashPassword password }

    let sendWelcomeEmail user =
        // Simulate email sending
        Ok user

    // Main registration function
    let registerUser params =
        result {
            let! email = Map.tryFind "email" params |> Option.toResult InvalidEmail
            let! validEmail = validateEmail email

            let! password = Map.tryFind "password" params |> Option.toResult WeakPassword
            let! validPassword = validatePassword password

            let! user = createUser validEmail validPassword
            let! _ = sendWelcomeEmail user
            return user
        }
        |> Result.mapError (fun error ->
            match error with
            | InvalidEmail -> "Invalid email format"
            | WeakPassword -> "Password too weak"
            | EmailTaken -> "Email already registered"
            | RegistrationFailed reason -> $"Registration failed: {reason}"
        )

    // Helper extension
    module Option =
        let toResult error option =
            match option with
            | Some value -> Ok value
            | None -> Error error
```

### Example 3: Complex - GenServer to MailboxProcessor

**Before (Elixir):**
```elixir
defmodule ChatRoom do
  use GenServer

  # Client API

  def start_link(room_name) do
    GenServer.start_link(__MODULE__, room_name, name: via_tuple(room_name))
  end

  def join(room_name, user_name) do
    GenServer.call(via_tuple(room_name), {:join, user_name})
  end

  def leave(room_name, user_name) do
    GenServer.cast(via_tuple(room_name), {:leave, user_name})
  end

  def send_message(room_name, user_name, message) do
    GenServer.cast(via_tuple(room_name), {:message, user_name, message})
  end

  def get_users(room_name) do
    GenServer.call(via_tuple(room_name), :get_users)
  end

  # Server Callbacks

  @impl true
  def init(room_name) do
    state = %{
      room_name: room_name,
      users: MapSet.new(),
      messages: []
    }
    {:ok, state}
  end

  @impl true
  def handle_call({:join, user_name}, _from, state) do
    if MapSet.member?(state.users, user_name) do
      {:reply, {:error, :already_joined}, state}
    else
      new_state = %{state | users: MapSet.put(state.users, user_name)}
      broadcast_message(new_state, "#{user_name} joined the room")
      {:reply, {:ok, :joined}, new_state}
    end
  end

  def handle_call(:get_users, _from, state) do
    {:reply, MapSet.to_list(state.users), state}
  end

  @impl true
  def handle_cast({:leave, user_name}, state) do
    new_state = %{state | users: MapSet.delete(state.users, user_name)}
    broadcast_message(new_state, "#{user_name} left the room")
    {:noreply, new_state}
  end

  def handle_cast({:message, user_name, message}, state) do
    formatted = "#{user_name}: #{message}"
    new_state = %{state | messages: [formatted | state.messages]}
    broadcast_message(new_state, formatted)
    {:noreply, new_state}
  end

  # Private Helpers

  defp via_tuple(room_name) do
    {:via, Registry, {ChatRegistry, room_name}}
  end

  defp broadcast_message(state, message) do
    # In real app, would use PubSub
    IO.puts("[#{state.room_name}] #{message}")
  end
end
```

**After (F#):**
```fsharp
module ChatRoom =
    // Types
    type User = string
    type Message = string

    type State = {
        RoomName: string
        Users: Set<User>
        Messages: Message list
    }

    // Message types
    type ChatMessage =
        | Join of user: User * AsyncReplyChannel<Result<unit, string>>
        | Leave of user: User
        | SendMessage of user: User * message: Message
        | GetUsers of AsyncReplyChannel<User list>

    // Chat room agent
    type ChatRoomAgent(roomName: string) =
        let agent = MailboxProcessor.Start(fun inbox ->
            let broadcastMessage state message =
                printfn "[%s] %s" state.RoomName message

            let rec loop state = async {
                let! msg = inbox.Receive()

                match msg with
                | Join (user, reply) ->
                    if Set.contains user state.Users then
                        reply.Reply(Error "Already joined")
                        return! loop state
                    else
                        let newState = { state with Users = Set.add user state.Users }
                        broadcastMessage newState $"{user} joined the room"
                        reply.Reply(Ok ())
                        return! loop newState

                | Leave user ->
                    let newState = { state with Users = Set.remove user state.Users }
                    broadcastMessage newState $"{user} left the room"
                    return! loop newState

                | SendMessage (user, message) ->
                    let formatted = $"{user}: {message}"
                    let newState = { state with Messages = formatted :: state.Messages }
                    broadcastMessage newState formatted
                    return! loop newState

                | GetUsers reply ->
                    reply.Reply(Set.toList state.Users)
                    return! loop state
            }

            let initialState = {
                RoomName = roomName
                Users = Set.empty
                Messages = []
            }

            loop initialState
        )

        // Client API
        member _.Join(user) =
            agent.PostAndReply(fun ch -> Join(user, ch))

        member _.Leave(user) =
            agent.Post(Leave user)

        member _.SendMessage(user, message) =
            agent.Post(SendMessage(user, message))

        member _.GetUsers() =
            agent.PostAndReply(GetUsers)

    // Room registry (simple dictionary-based)
    module Registry =
        open System.Collections.Concurrent

        let private rooms = ConcurrentDictionary<string, ChatRoomAgent>()

        let getOrCreate roomName =
            rooms.GetOrAdd(roomName, fun name -> ChatRoomAgent(name))

        let tryGet roomName =
            match rooms.TryGetValue(roomName) with
            | true, room -> Some room
            | false, _ -> None

// Usage example
let room = ChatRoom.Registry.getOrCreate "lobby"

match room.Join("Alice") with
| Ok () -> printfn "Alice joined successfully"
| Error msg -> printfn "Join failed: %s" msg

room.SendMessage("Alice", "Hello everyone!")

let users = room.GetUsers()
printfn "Current users: %A" users

room.Leave("Alice")
```

---

## See Also

For more examples and patterns, see:
- `meta-convert-dev` - Foundational patterns with cross-language examples
- `convert-erlang-fsharp` - Similar BEAM → .NET conversion (Elixir's foundation)
- `lang-elixir-dev` - Elixir development patterns
- `lang-fsharp-dev` - F# development patterns

Cross-cutting pattern skills:
- `patterns-concurrency-dev` - Actor patterns, async workflows across languages
- `patterns-serialization-dev` - JSON handling, validation across languages
- `patterns-metaprogramming-dev` - Compile-time code generation patterns
