---
name: convert-fsharp-elixir
description: Convert F# code to idiomatic Elixir. Use when migrating F# projects to Elixir, translating F# patterns to idiomatic Elixir, or refactoring F# codebases. Extends meta-convert-dev with F#-to-Elixir specific patterns.
---

# Convert F# to Elixir

Convert F# code to idiomatic Elixir. This skill extends `meta-convert-dev` with F#-to-Elixir specific type mappings, idiom translations, and tooling.

## This Skill Extends

- `meta-convert-dev` - Foundational conversion patterns (APTV workflow, testing strategies)

For general concepts like the Analyze → Plan → Transform → Validate workflow, testing strategies, and common pitfalls, see the meta-skill first.

## This Skill Adds

- **Type mappings**: F# types → Elixir types (static → dynamic with specs)
- **Idiom translations**: F# patterns → idiomatic Elixir
- **Error handling**: F# Result/Option → Elixir tagged tuples
- **Concurrency**: F# async/Task → Elixir processes/GenServer
- **Platform shift**: .NET/CLR → BEAM/OTP actor model

## This Skill Does NOT Cover

- General conversion methodology - see `meta-convert-dev`
- F# language fundamentals - see `lang-fsharp-dev`
- Elixir language fundamentals - see `lang-elixir-dev`
- Reverse conversion (Elixir → F#) - see `convert-elixir-fsharp`

---

## Quick Reference

| F# | Elixir | Notes |
|-----|--------|-------|
| `string` | `String.t()` | UTF-8 binaries |
| `int` | `integer()` | Arbitrary precision in Elixir |
| `float` | `float()` | 64-bit double precision |
| `bool` | `boolean()` | `:true` / `:false` atoms |
| `'T list` | `list(t)` | Linked lists in both |
| `'T[]` | `list(t)` | Arrays → lists (Elixir rarely uses arrays) |
| `Map<'K,'V>` | `%{key => value}` | Maps in both |
| `Option<'T>` | `value \| nil` or `{:ok, value} \| nil` | nil for None, value for Some |
| `Result<'T,'E>` | `{:ok, value} \| {:error, reason}` | Tagged tuples |
| `async<'T>` | `GenServer` / `Task` | Processes for concurrency |
| `type Record = { ... }` | `defstruct` | Record → struct |
| `type Union = A \| B` | Pattern matching atoms/tuples | Discriminated unions → atoms |

## When Converting Code

1. **Analyze source thoroughly** before writing target
2. **Map types first** - create type equivalence table, understand static → dynamic shift
3. **Preserve semantics** over syntax similarity
4. **Adopt Elixir idioms** - don't write "F# code in Elixir syntax"
5. **Embrace immutability** - both languages are immutable-first
6. **Shift to actor model** - F# async → Elixir processes
7. **Test equivalence** - same inputs → same outputs

---

## Type System Mapping

### Primitive Types

| F# | Elixir | Notes |
|----|--------|-------|
| `string` | `String.t()` | UTF-8 in both; Elixir strings are binaries |
| `int` | `integer()` | F# is 32-bit by default; Elixir is arbitrary precision |
| `int64` | `integer()` | Elixir integers grow as needed |
| `float` | `float()` | 64-bit double precision in both |
| `bool` | `boolean()` | F# true/false → Elixir :true/:false atoms |
| `char` | `charlist()` | F# char → Elixir single-char string or charlist |
| `unit` | `nil` or `{:ok}` | F# () → Elixir nil or :ok atom |
| `obj` | `any()` | F# obj → Elixir any(), lose type safety |

### Collection Types

| F# | Elixir | Notes |
|----|--------|-------|
| `'T list` | `list(t)` | Linked lists in both; same performance characteristics |
| `'T[]` | `list(t)` or `tuple()` | F# arrays → Elixir lists (usually) or tuples (fixed size) |
| `'T seq` | `Enum.t()` / `Stream.t()` | F# sequences → Elixir streams (lazy) |
| `Map<'K,'V>` | `%{key => value}` | Hash maps in both |
| `Set<'T>` | `MapSet.t()` | Sets in both |
| `('T * 'U)` | `{t, u}` | Tuples in both |
| `('T * 'U * 'V)` | `{t, u, v}` | N-ary tuples supported |

### Composite Types

| F# | Elixir | Notes |
|----|--------|-------|
| `type Record = { Field: 'T }` | `defstruct field: t` | Records → structs |
| `type Union = A \| B of 'T` | Atoms + pattern matching | Discriminated unions → atoms or tagged tuples |
| `Option<'T>` | `value \| nil` | Some x → value, None → nil |
| `Result<'T,'E>` | `{:ok, value} \| {:error, reason}` | Result → tagged tuples |
| `async<'T>` | `Task.t()` | F# async → Elixir Task or GenServer |
| Single-case union | `@type t :: {atom(), value}` | F# newtype → Elixir tagged tuple or typespec alias |

### Type Definitions

| F# | Elixir | Notes |
|----|--------|-------|
| `type Alias = 'T` | `@type alias :: t` | Type aliases |
| `type Generic<'T>` | `@type t(x) :: x` | Generic type parameters |
| `[<Measure>] type kg` | Unit comments in specs | No units of measure; document in specs |
| `interface I` | `@callback` behavior | Interfaces → behaviors |

---

## Idiom Translation

### Pattern 1: Option/None Handling

**F#:**
```fsharp
let findUser (id: string) : User option =
    users |> List.tryFind (fun u -> u.Id = id)

let name =
    match findUser "123" with
    | Some user -> user.Name
    | None -> "Anonymous"

// Or with Option module
let name' =
    findUser "123"
    |> Option.map (fun u -> u.Name)
    |> Option.defaultValue "Anonymous"
```

**Elixir:**
```elixir
@spec find_user(String.t()) :: User.t() | nil
def find_user(id) do
  Enum.find(users(), fn u -> u.id == id end)
end

name =
  case find_user("123") do
    %User{name: name} -> name
    nil -> "Anonymous"
  end

# Or with pattern matching
name =
  find_user("123")
  |> case do
    %User{name: name} -> name
    nil -> "Anonymous"
  end

# Or more idiomatically
name =
  case find_user("123") do
    user when not is_nil(user) -> user.name
    _ -> "Anonymous"
  end
```

**Why this translation:**
- F#'s `Option<'T>` explicitly wraps values; Elixir uses `nil` for absence
- F# has `Option` module combinators; Elixir uses pattern matching
- Elixir pattern matching on nil is more direct than Option wrapping

### Pattern 2: Result Type Error Handling

**F#:**
```fsharp
type Error =
    | NotFound
    | InvalidInput of string
    | DatabaseError of string

let divide x y =
    if y = 0 then
        Error (InvalidInput "Division by zero")
    else
        Ok (x / y)

let processResult =
    result {
        let! a = divide 10 2
        let! b = divide 20 4
        let! c = divide a b
        return c
    }
```

**Elixir:**
```elixir
@type error :: :not_found | {:invalid_input, String.t()} | {:database_error, String.t()}

@spec divide(number(), number()) :: {:ok, float()} | {:error, error()}
def divide(_x, 0), do: {:error, {:invalid_input, "Division by zero"}}
def divide(x, y), do: {:ok, x / y}

def process_result do
  with {:ok, a} <- divide(10, 2),
       {:ok, b} <- divide(20, 4),
       {:ok, c} <- divide(a, b) do
    {:ok, c}
  end
end
```

**Why this translation:**
- F# `Result<'T,'E>` → Elixir `{:ok, value} | {:error, reason}` tagged tuples
- F# computation expressions → Elixir `with` statement
- F# discriminated unions for errors → Elixir atoms or tagged tuples
- Both chain operations that can fail, but syntax differs

### Pattern 3: List/Collection Operations

**F#:**
```fsharp
let numbers = [1; 2; 3; 4; 5]

let result =
    numbers
    |> List.filter (fun x -> x % 2 = 0)
    |> List.map (fun x -> x * 2)
    |> List.reduce (+)
```

**Elixir:**
```elixir
numbers = [1, 2, 3, 4, 5]

result =
  numbers
  |> Enum.filter(fn x -> rem(x, 2) == 0 end)
  |> Enum.map(fn x -> x * 2 end)
  |> Enum.sum()

# Or with capture syntax
result =
  numbers
  |> Enum.filter(&(rem(&1, 2) == 0))
  |> Enum.map(&(&1 * 2))
  |> Enum.sum()
```

**Why this translation:**
- Both use pipe operator for chaining
- F# `List.` → Elixir `Enum.` (eager) or `Stream.` (lazy)
- F# `List.reduce` → Elixir `Enum.sum()` for sum operations
- Elixir capture syntax `&(&1)` similar to F# function shorthand

### Pattern 4: Pattern Matching on Discriminated Unions

**F#:**
```fsharp
type PaymentMethod =
    | Cash
    | CreditCard of cardNumber: string
    | DebitCard of cardNumber: string * pin: int

let processPayment method =
    match method with
    | Cash -> "Processing cash payment"
    | CreditCard cardNumber -> $"Processing credit card {cardNumber}"
    | DebitCard (cardNumber, _) -> $"Processing debit card {cardNumber}"
```

**Elixir:**
```elixir
# Elixir doesn't have discriminated unions, use atoms and tagged tuples
@type payment_method :: :cash | {:credit_card, String.t()} | {:debit_card, String.t(), integer()}

@spec process_payment(payment_method()) :: String.t()
def process_payment(:cash), do: "Processing cash payment"
def process_payment({:credit_card, card_number}), do: "Processing credit card #{card_number}"
def process_payment({:debit_card, card_number, _pin}), do: "Processing debit card #{card_number}"
```

**Why this translation:**
- F# discriminated unions → Elixir atoms (for simple cases) or tagged tuples (for data)
- F# pattern matching in `match` → Elixir pattern matching in function heads
- Elixir favors multiple function clauses over single match expression

### Pattern 5: Records and Structs

**F#:**
```fsharp
type Person = {
    FirstName: string
    LastName: string
    Age: int
}

let person = { FirstName = "Alice"; LastName = "Smith"; Age = 30 }

// Copy-and-update
let olderPerson = { person with Age = 31 }

// Pattern matching
let getFullName { FirstName = f; LastName = l } = $"{f} {l}"
```

**Elixir:**
```elixir
defmodule Person do
  defstruct [:first_name, :last_name, :age]

  @type t :: %__MODULE__{
    first_name: String.t(),
    last_name: String.t(),
    age: integer()
  }
end

person = %Person{first_name: "Alice", last_name: "Smith", age: 30}

# Update (creates new struct)
older_person = %{person | age: 31}

# Pattern matching
def get_full_name(%Person{first_name: f, last_name: l}), do: "#{f} #{l}"
```

**Why this translation:**
- F# records → Elixir structs (both immutable)
- F# copy-and-update `{ record with ... }` → Elixir `%{struct | ...}`
- Both support pattern matching on fields
- Elixir requires `defmodule` wrapper; F# records are standalone types

### Pattern 6: Active Patterns → Function Guards

**F#:**
```fsharp
let (|Even|Odd|) n =
    if n % 2 = 0 then Even else Odd

let describe n =
    match n with
    | Even -> "even"
    | Odd -> "odd"
```

**Elixir:**
```elixir
defguardp is_even(n) when rem(n, 2) == 0

def describe(n) when is_even(n), do: "even"
def describe(_n), do: "odd"

# Or without guards, using pattern matching
def describe(n) do
  case rem(n, 2) do
    0 -> "even"
    _ -> "odd"
  end
end
```

**Why this translation:**
- F# active patterns → Elixir guard clauses or helper functions
- Elixir guards are more limited than active patterns
- For complex patterns, use helper functions + case statements

---

## Paradigm Translation

### Mental Model Shift: Static Types → Dynamic Types with Specs

| F# Concept | Elixir Approach | Key Insight |
|------------|-----------------|-------------|
| Compile-time type checking | Runtime + dialyzer static analysis | Elixir uses specs for documentation and dialyzer for warnings |
| Type inference | Pattern matching + guards | Types inferred from patterns, not declared |
| Discriminated unions | Atoms + tagged tuples | Union types → atoms for simple cases, tuples for data |
| Generic type parameters | Typespec parameters | `'T` → `t()` in specs |
| Units of measure | Comments in specs | No type-level units; document in @type or @spec |

### Concurrency Mental Model

| F# Model | Elixir Model | Conceptual Translation |
|----------|--------------|------------------------|
| `async { }` / `Task` | `Task.async` / `GenServer` | Async computation → lightweight process |
| `Async.Parallel` | `Task.async_stream` | Parallel execution → concurrent tasks |
| Mailbox processor | `GenServer` | Stateful async → process with message loop |
| Thread safety via immutability | Process isolation | Shared immutable state → isolated process state |

---

## Error Handling

### F# Result → Elixir Tagged Tuples

**F# Pattern:**
```fsharp
type Result<'T,'E> =
    | Ok of 'T
    | Error of 'E

let validateEmail email =
    if email.Contains("@") then
        Ok email
    else
        Error "Invalid email"

let validateAge age =
    if age >= 0 && age <= 120 then
        Ok age
    else
        Error "Invalid age"

let createUser email age =
    result {
        let! validEmail = validateEmail email
        let! validAge = validateAge age
        return { Email = validEmail; Age = validAge }
    }
```

**Elixir Pattern:**
```elixir
@spec validate_email(String.t()) :: {:ok, String.t()} | {:error, String.t()}
def validate_email(email) do
  if String.contains?(email, "@") do
    {:ok, email}
  else
    {:error, "Invalid email"}
  end
end

@spec validate_age(integer()) :: {:ok, integer()} | {:error, String.t()}
def validate_age(age) when age >= 0 and age <= 120, do: {:ok, age}
def validate_age(_age), do: {:error, "Invalid age"}

@spec create_user(String.t(), integer()) :: {:ok, map()} | {:error, String.t()}
def create_user(email, age) do
  with {:ok, valid_email} <- validate_email(email),
       {:ok, valid_age} <- validate_age(age) do
    {:ok, %{email: valid_email, age: valid_age}}
  end
end
```

**Translation notes:**
- F# `Result<'T,'E>` → Elixir `{:ok, value} | {:error, reason}`
- F# computation expressions `result { }` → Elixir `with` statement
- F# explicit error types → Elixir atoms or strings for errors
- Both avoid exceptions for control flow

### Exception Handling (Use Sparingly in Elixir)

**F#:**
```fsharp
try
    let result = dangerousOperation()
    Ok result
with
| :? ArgumentException as ex -> Error ex.Message
| ex -> Error (ex.ToString())
```

**Elixir:**
```elixir
# Elixir prefers tagged tuples, but try/rescue available
try do
  result = dangerous_operation()
  {:ok, result}
rescue
  e in ArgumentError -> {:error, Exception.message(e)}
  e -> {:error, Exception.message(e)}
end

# Better: Have dangerous_operation/0 return tagged tuples
case dangerous_operation() do
  {:ok, result} -> {:ok, result}
  {:error, reason} -> {:error, reason}
end
```

**Translation notes:**
- Exceptions are expensive in both languages
- Elixir culture strongly prefers tagged tuples over exceptions
- Use `try/rescue` only for truly exceptional cases (FFI, external libraries)

---

## Concurrency Patterns

### F# Async → Elixir Task

**F# Pattern:**
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

let urls = ["url1"; "url2"; "url3"]
processUrls urls |> Async.RunSynchronously
```

**Elixir Pattern:**
```elixir
def fetch_data(url) do
  IO.puts("Fetching #{url}...")
  Process.sleep(1000)
  "Data from #{url}"
end

def process_urls(urls) do
  urls
  |> Enum.map(&Task.async(fn -> fetch_data(&1) end))
  |> Enum.map(&Task.await/1)
end

urls = ["url1", "url2", "url3"]
process_urls(urls)

# Or more idiomatically with Task.async_stream
def process_urls_stream(urls) do
  urls
  |> Task.async_stream(&fetch_data/1)
  |> Enum.map(fn {:ok, result} -> result end)
end
```

**Why this translation:**
- F# `async { }` → Elixir `Task.async` or anonymous function
- F# `Async.Parallel` → Elixir `Task.async_stream` or manual Task.async + await
- F# `Async.Sleep` → Elixir `Process.sleep`
- Elixir tasks are lightweight processes; F# async uses thread pool

### F# MailboxProcessor → Elixir GenServer

**F# Pattern:**
```fsharp
type Message =
    | Increment
    | Get of AsyncReplyChannel<int>

let counter = MailboxProcessor.Start(fun inbox ->
    let rec loop count = async {
        let! msg = inbox.Receive()
        match msg with
        | Increment ->
            return! loop (count + 1)
        | Get replyChannel ->
            replyChannel.Reply(count)
            return! loop count
    }
    loop 0)

counter.Post(Increment)
let count = counter.PostAndReply(Get)
```

**Elixir Pattern:**
```elixir
defmodule Counter do
  use GenServer

  # Client API
  def start_link(initial \\ 0) do
    GenServer.start_link(__MODULE__, initial, name: __MODULE__)
  end

  def increment do
    GenServer.cast(__MODULE__, :increment)
  end

  def get do
    GenServer.call(__MODULE__, :get)
  end

  # Server callbacks
  @impl true
  def init(initial), do: {:ok, initial}

  @impl true
  def handle_cast(:increment, count), do: {:noreply, count + 1}

  @impl true
  def handle_call(:get, _from, count), do: {:reply, count, count}
end

{:ok, _pid} = Counter.start_link(0)
Counter.increment()
count = Counter.get()
```

**Why this translation:**
- F# MailboxProcessor → Elixir GenServer (both message-based state machines)
- F# `Post` → Elixir `GenServer.cast` (async)
- F# `PostAndReply` → Elixir `GenServer.call` (sync)
- Elixir GenServer is OTP standard; F# MailboxProcessor is library

---

## Testing Strategy

### F# Expecto → Elixir ExUnit

**F# (Expecto):**
```fsharp
module Tests

open Expecto

let mathTests =
    testList "Math operations" [
        testCase "addition" <| fun () ->
            Expect.equal (2 + 2) 4 "2 + 2 = 4"

        testCase "division" <| fun () ->
            Expect.equal (divide 10 2) (Ok 5) "10 / 2 = 5"

        testCase "division by zero" <| fun () ->
            Expect.equal (divide 10 0) (Error "Division by zero") "should error"
    ]

[<EntryPoint>]
let main args =
    runTestsWithCLIArgs [] args mathTests
```

**Elixir (ExUnit):**
```elixir
defmodule MathTest do
  use ExUnit.Case

  test "addition" do
    assert 2 + 2 == 4
  end

  test "division" do
    assert Math.divide(10, 2) == {:ok, 5}
  end

  test "division by zero" do
    assert Math.divide(10, 0) == {:error, "Division by zero"}
  end
end
```

**Translation notes:**
- F# `testCase` → Elixir `test`
- F# `Expect.equal` → Elixir `assert ... ==`
- F# `testList` → Elixir `describe` (for organization)
- Both support pattern matching in assertions

### Property-Based Testing

**F# (FsCheck):**
```fsharp
open FsCheck
open Expecto

let propertyTests =
    testList "Property tests" [
        testProperty "reverse twice equals original" <| fun (xs: int list) ->
            List.rev (List.rev xs) = xs

        testProperty "list append length" <| fun (xs: int list) (ys: int list) ->
            List.length (xs @ ys) = List.length xs + List.length ys
    ]
```

**Elixir (StreamData):**
```elixir
defmodule PropertyTest do
  use ExUnit.Case
  use ExUnitProperties

  property "reverse twice equals original" do
    check all list <- list_of(integer()) do
      assert Enum.reverse(Enum.reverse(list)) == list
    end
  end

  property "list concatenation length" do
    check all list1 <- list_of(integer()),
              list2 <- list_of(integer()) do
      assert length(list1 ++ list2) == length(list1) + length(list2)
    end
  end
end
```

**Translation notes:**
- F# FsCheck → Elixir StreamData
- F# `testProperty` → Elixir `property` with `check all`
- Both generate random test cases
- Elixir requires explicit generator syntax (`list_of(integer())`)

---

## Common Pitfalls

1. **Type System Assumptions**
   - F# has compile-time type safety; Elixir has runtime types
   - Don't assume type errors will be caught at compile time
   - Use dialyzer and typespecs to catch type issues statically
   - F# `'T` generic → Elixir `t()` or `any()` in specs

2. **Discriminated Unions → Atoms**
   - F# discriminated unions have named cases; Elixir uses atoms
   - F# `Some x` → Elixir `x` (not `{:some, x}`)
   - F# `None` → Elixir `nil` (not `:none`)
   - For data-carrying cases, use tagged tuples: `{:credit_card, "1234"}`

3. **Concurrency Model Differences**
   - F# async is cooperative; Elixir processes are preemptive
   - F# shares memory (immutable); Elixir isolates memory per process
   - Don't translate F# `Task.Run` directly to Elixir `Task.async` without understanding process model
   - Elixir processes are cheaper than F# tasks; spawn liberally

4. **Null vs nil**
   - F# uses `Option<'T>` to avoid null; Elixir has `nil` as a value
   - F# `Some value` → Elixir `value` (unwrapped)
   - F# `None` → Elixir `nil`
   - Elixir nil checks: `is_nil(x)`, pattern match on nil

5. **Pattern Matching Syntax**
   - F# `match x with | pattern -> ...` → Elixir `case x do pattern -> ... end`
   - F# uses `|` separator; Elixir uses newlines
   - F# allows `function | pattern -> ...`; Elixir uses multiple function heads
   - Both support guards, but Elixir guards are more restricted

6. **Module System**
   - F# has file-order dependencies; Elixir modules are independent
   - F# `open Module` → Elixir `import Module` or `alias Module`
   - F# functions are module members; Elixir functions must be in `defmodule`
   - Elixir requires `def`/`defp` for public/private; F# uses access modifiers

7. **Computation Expressions → with/case**
   - F# computation expressions are powerful; Elixir has limited equivalents
   - F# `result { }` → Elixir `with` for chaining
   - F# `async { }` → Elixir `Task.async` or GenServer
   - For custom monadic workflows, use Elixir libraries or explicit functions

8. **Exceptions Are Expensive**
   - Both languages discourage exceptions for control flow
   - F# `Result<'T,'E>` → Elixir `{:ok, value} | {:error, reason}`
   - Elixir "let it crash" philosophy: use supervisors, not defensive code
   - F# has more structured exception handling; Elixir has exit signals

---

## Tooling

| Tool | Purpose | Notes |
|------|---------|-------|
| dialyzer | Static analysis | Type checking from specs; catches type errors |
| mix format | Code formatting | Standard formatter; equivalent to Fantomas for F# |
| ExUnit | Testing framework | Built-in; equivalent to Expecto/xUnit |
| StreamData | Property testing | Equivalent to FsCheck |
| Credo | Linting | Code quality suggestions |
| mix test | Test runner | Built-in test runner |
| iex | REPL | Interactive Elixir shell; equivalent to F# Interactive |
| Observer | Process monitoring | Visualize processes, supervision trees |

---

## Examples

### Example 1: Simple - Option to nil

**Before (F#):**
```fsharp
let findUserById (id: string) (users: User list) : User option =
    users |> List.tryFind (fun u -> u.Id = id)

let getUserName id users =
    match findUserById id users with
    | Some user -> user.Name
    | None -> "Unknown"
```

**After (Elixir):**
```elixir
@spec find_user_by_id(String.t(), [User.t()]) :: User.t() | nil
def find_user_by_id(id, users) do
  Enum.find(users, fn u -> u.id == id end)
end

@spec get_user_name(String.t(), [User.t()]) :: String.t()
def get_user_name(id, users) do
  case find_user_by_id(id, users) do
    %User{name: name} -> name
    nil -> "Unknown"
  end
end
```

### Example 2: Medium - Result Type Chaining

**Before (F#):**
```fsharp
type ValidationError =
    | EmptyEmail
    | InvalidFormat
    | AgeTooLow
    | AgeTooHigh

let validateEmail email =
    if String.IsNullOrWhiteSpace(email) then
        Error EmptyEmail
    elif not (email.Contains("@")) then
        Error InvalidFormat
    else
        Ok email

let validateAge age =
    if age < 0 then Error AgeTooLow
    elif age > 120 then Error AgeTooHigh
    else Ok age

let createUser email age =
    result {
        let! validEmail = validateEmail email
        let! validAge = validateAge age
        return { Email = validEmail; Age = validAge }
    }

// Usage
match createUser "test@example.com" 30 with
| Ok user -> printfn $"Created user: {user.Email}"
| Error EmptyEmail -> printfn "Email cannot be empty"
| Error InvalidFormat -> printfn "Invalid email format"
| Error AgeTooLow -> printfn "Age too low"
| Error AgeTooHigh -> printfn "Age too high"
```

**After (Elixir):**
```elixir
@type validation_error ::
  :empty_email
  | :invalid_format
  | :age_too_low
  | :age_too_high

@spec validate_email(String.t()) :: {:ok, String.t()} | {:error, validation_error()}
def validate_email(email) do
  cond do
    String.trim(email) == "" -> {:error, :empty_email}
    not String.contains?(email, "@") -> {:error, :invalid_format}
    true -> {:ok, email}
  end
end

@spec validate_age(integer()) :: {:ok, integer()} | {:error, validation_error()}
def validate_age(age) when age < 0, do: {:error, :age_too_low}
def validate_age(age) when age > 120, do: {:error, :age_too_high}
def validate_age(age), do: {:ok, age}

@spec create_user(String.t(), integer()) :: {:ok, map()} | {:error, validation_error()}
def create_user(email, age) do
  with {:ok, valid_email} <- validate_email(email),
       {:ok, valid_age} <- validate_age(age) do
    {:ok, %{email: valid_email, age: valid_age}}
  end
end

# Usage
case create_user("test@example.com", 30) do
  {:ok, user} -> IO.puts("Created user: #{user.email}")
  {:error, :empty_email} -> IO.puts("Email cannot be empty")
  {:error, :invalid_format} -> IO.puts("Invalid email format")
  {:error, :age_too_low} -> IO.puts("Age too low")
  {:error, :age_too_high} -> IO.puts("Age too high")
end
```

### Example 3: Complex - Concurrent Data Processing with State

**Before (F#):**
```fsharp
type Message =
    | AddData of string
    | GetResults of AsyncReplyChannel<string list>
    | Process

type DataProcessor() =
    let processor = MailboxProcessor.Start(fun inbox ->
        let rec loop (data: string list) = async {
            let! msg = inbox.Receive()
            match msg with
            | AddData item ->
                return! loop (item :: data)
            | GetResults replyChannel ->
                replyChannel.Reply(data)
                return! loop data
            | Process ->
                let! processed =
                    data
                    |> List.map (fun item -> async {
                        do! Async.Sleep 100  // Simulate work
                        return item.ToUpper()
                    })
                    |> Async.Parallel
                let processedList = processed |> Array.toList
                return! loop processedList
        }
        loop [])

    member _.AddData(item) = processor.Post(AddData item)
    member _.Process() = processor.Post(Process)
    member _.GetResults() = processor.PostAndReply(GetResults)

// Usage
let dp = DataProcessor()
dp.AddData("hello")
dp.AddData("world")
dp.Process()
Async.Sleep(500) |> Async.RunSynchronously
let results = dp.GetResults()
printfn $"Results: {results}"  // ["HELLO"; "WORLD"]
```

**After (Elixir):**
```elixir
defmodule DataProcessor do
  use GenServer

  # Client API

  def start_link(opts \\ []) do
    GenServer.start_link(__MODULE__, [], opts)
  end

  def add_data(pid, item) do
    GenServer.cast(pid, {:add_data, item})
  end

  def process(pid) do
    GenServer.cast(pid, :process)
  end

  def get_results(pid) do
    GenServer.call(pid, :get_results)
  end

  # Server Callbacks

  @impl true
  def init(_opts) do
    {:ok, []}
  end

  @impl true
  def handle_cast({:add_data, item}, data) do
    {:noreply, [item | data]}
  end

  @impl true
  def handle_cast(:process, data) do
    processed =
      data
      |> Task.async_stream(fn item ->
        Process.sleep(100)  # Simulate work
        String.upcase(item)
      end)
      |> Enum.map(fn {:ok, result} -> result end)

    {:noreply, processed}
  end

  @impl true
  def handle_call(:get_results, _from, data) do
    {:reply, data, data}
  end
end

# Usage
{:ok, pid} = DataProcessor.start_link()
DataProcessor.add_data(pid, "hello")
DataProcessor.add_data(pid, "world")
DataProcessor.process(pid)
Process.sleep(500)
results = DataProcessor.get_results(pid)
IO.inspect(results)  # ["HELLO", "WORLD"]
```

**Key translation points:**
- F# MailboxProcessor → Elixir GenServer for stateful message processing
- F# `Post` → Elixir `GenServer.cast` (async messages)
- F# `PostAndReply` → Elixir `GenServer.call` (sync request-reply)
- F# `Async.Parallel` → Elixir `Task.async_stream` for concurrent processing
- Both use message passing for concurrency, but Elixir's GenServer is OTP standard
- Elixir processes are isolated; F# mailbox processor shares memory (immutably)

---

## See Also

For more examples and patterns, see:
- `meta-convert-dev` - Foundational patterns with cross-language examples
- `convert-elixir-fsharp` - Reverse conversion (Elixir → F#)
- `lang-fsharp-dev` - F# development patterns
- `lang-elixir-dev` - Elixir development patterns

Cross-cutting pattern skills:
- `patterns-concurrency-dev` - Process models, GenServer patterns, supervision
- `patterns-serialization-dev` - JSON handling, validation patterns
- `patterns-metaprogramming-dev` - Macros, compile-time code generation
