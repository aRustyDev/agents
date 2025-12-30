---
name: convert-haskell-elixir
description: Convert Haskell code to idiomatic Elixir. Use when migrating Haskell projects to Elixir/BEAM, translating pure functional patterns to practical functional Elixir with OTP, or refactoring Haskell codebases for fault-tolerant distributed systems. Extends meta-convert-dev with Haskell-to-Elixir specific patterns covering static→dynamic types, lazy→strict evaluation, IO monad→effects, and type classes→protocols/behaviours.
---

# Convert Haskell to Elixir

Convert Haskell code to idiomatic Elixir. This skill extends `meta-convert-dev` with Haskell-to-Elixir specific type mappings, idiom translations, and patterns for migrating from pure lazy functional programming to practical strict functional programming on the BEAM.

## This Skill Extends

- `meta-convert-dev` - Foundational conversion patterns (APTV workflow, testing strategies)

For general concepts like the Analyze → Plan → Transform → Validate workflow, testing strategies, and common pitfalls, see the meta-skill first.

## This Skill Adds

- **Type mappings**: Haskell types → Elixir types (static → dynamic with pattern matching)
- **Idiom translations**: Haskell patterns → idiomatic Elixir functional patterns
- **Error handling**: Maybe/Either/IO → with/case, {:ok, _}/{:error, _} tuples
- **Lazy evaluation**: Default lazy → explicit Stream, generators
- **Concurrency**: STM/async → GenServer, Task, Agent, OTP supervision
- **Type classes**: Functor/Monad/Applicative → protocols, behaviours
- **IO monad**: Pure/impure separation → pragmatic effects
- **Purity philosophy**: Haskell purity → Elixir practical FP

## This Skill Does NOT Cover

- General conversion methodology - see `meta-convert-dev`
- Haskell language fundamentals - see `lang-haskell-dev`
- Elixir language fundamentals - see `lang-elixir-dev`
- Reverse conversion (Elixir → Haskell) - see `convert-elixir-haskell`
- GHC-specific extensions (GADTs, Type Families) - no direct Elixir equivalent

---

## Quick Reference

| Haskell | Elixir | Notes |
|---------|--------|-------|
| `String` | `String.t()` or `binary()` | UTF-8 binaries in Elixir |
| `Int` | `integer()` | Arbitrary precision in Elixir |
| `Integer` | `integer()` | Same representation |
| `Float`/`Double` | `float()` | 64-bit floats |
| `Bool` | `boolean()` | `true`/`false` atoms |
| `Maybe a` | `nil` or `{:ok, val}` | Pattern match on nil, use tuples for explicit optionality |
| `Either e a` | `{:ok, val}` / `{:error, reason}` | Tagged tuples for error handling |
| `[a]` | `[a]` | Lists (linked lists in both) |
| `(a, b)` | `{a, b}` | Tuples |
| `Map k v` | `%{key => value}` | Hash maps |
| `Set a` | `MapSet.t()` | Set implementation |
| `data User = User Text Int` | `defstruct name: "", age: 0` | Structs for product types |
| `IO a` | Side effects allowed anywhere | No purity enforcement |
| `fmap` / `<$>` | `Enum.map` / `Stream.map` | Functor-like operations |
| `>>=` (bind) | Pipe `\|>` with pattern matching | Monadic chaining |
| `class Typeclass` | `defprotocol` or `@behaviour` | Polymorphism mechanisms |

## When Converting Code

1. **Analyze source thoroughly** - Understand Haskell's lazy evaluation and purity before writing Elixir
2. **Map types first** - Haskell's static types need runtime pattern matching in Elixir
3. **Preserve semantics** over syntax similarity
4. **Embrace dynamic typing** - Use pattern matching and guards for type safety
5. **Handle infinite structures** - Lazy lists → Stream for infinite sequences
6. **Adapt IO monad** - Pure/impure separation → pragmatic functional style
7. **Test equivalence** - Same inputs → same outputs, property-based tests

---

## Type System Mapping

### Primitive Types

| Haskell | Elixir | Notes |
|---------|--------|-------|
| `Char` | Single-char string or integer | `"a"` or `?a` (codepoint) |
| `String` | `String.t()` | UTF-8 binary |
| `Int` | `integer()` | Arbitrary precision |
| `Integer` | `integer()` | Same as Int in Elixir |
| `Float` | `float()` | 64-bit IEEE 754 |
| `Double` | `float()` | Same as Float in Elixir |
| `Bool` | `boolean()` | `:true` / `:false` atoms |
| `()` (unit) | `:ok` or `nil` | Unit type → atom |

### Collection Types

| Haskell | Elixir | Notes |
|---------|--------|-------|
| `[a]` | `[a]` | Linked lists (lazy in Haskell, strict in Elixir) |
| `(a, b)` | `{a, b}` | Tuples (strict in both) |
| `(a, b, c)` | `{a, b, c}` | N-tuples |
| `Map k v` | `%{k => v}` | Hash maps |
| `Set a` | `MapSet.t(a)` | Set backed by map |
| `Array a` | No direct equivalent | Use `:array` module or lists |
| `Vector a` | No direct equivalent | Lists or tuples depending on use |
| `ByteString` | `binary()` | Raw bytes |
| `Text` | `String.t()` | UTF-8 text |

### Composite Types (ADTs)

| Haskell | Elixir | Notes |
|---------|--------|-------|
| `data Maybe a = Nothing \| Just a` | `nil` or value, or `{:ok, val}` / `nil` | Use pattern matching |
| `data Either e a = Left e \| Right a` | `{:error, reason}` / `{:ok, val}` | Tagged tuples |
| `data User = User Text Int` | `defstruct name: "", age: 0` | Structs for records |
| `newtype UserId = UserId Int` | Module-wrapped type or just use integer | No zero-cost newtypes |
| Sum types (enums) | Atoms or tagged tuples | `data Color = Red \| Green` → `:red`, `:green` |
| Records with fields | Structs with named fields | `%User{name: "Alice", age: 30}` |

### Type Classes → Protocols/Behaviours

| Haskell | Elixir | Notes |
|---------|--------|-------|
| `class Eq a where (==) :: a -> a -> Bool` | Built-in `==` or `defprotocol` | No explicit type classes |
| `class Ord a where compare :: a -> a -> Ordering` | Built-in comparison or protocol | Use guards for constraints |
| `class Show a where show :: a -> String` | `String.Chars` protocol | `to_string/1` |
| `class Functor f where fmap :: (a -> b) -> f a -> f b` | `Enum` module or `Stream` | No Higher-Kinded Types |
| `class Applicative f` | No direct equivalent | Use pipelines and combinators |
| `class Monad m` | No direct equivalent | Use `with`, pipelines, GenServer for effects |
| `instance Show User` | `defimpl String.Chars, for: User` | Protocol implementation |

---

## Idiom Translation

### Pattern 1: Maybe/Optional Handling

**Haskell:**
```haskell
-- Using Maybe
findUser :: Int -> [User] -> Maybe User
findUser userId = find (\u -> userId == userId u)

-- Pattern matching
case findUser 1 users of
  Nothing -> putStrLn "Not found"
  Just user -> putStrLn $ "Found: " ++ name user

-- Using maybe function
maybe "default" name (findUser 1 users)

-- Functor operations
fmap name (findUser 1 users)  -- Maybe String
```

**Elixir:**
```elixir
# Using nil
def find_user(user_id, users) do
  Enum.find(users, fn u -> u.id == user_id end)
end

# Pattern matching with case
case find_user(1, users) do
  nil -> IO.puts("Not found")
  user -> IO.puts("Found: #{user.name}")
end

# Using pattern matching with default
user = find_user(1, users) || %User{name: "default"}

# Or with explicit optional tuple
def find_user_safe(user_id, users) do
  case Enum.find(users, fn u -> u.id == user_id end) do
    nil -> {:error, :not_found}
    user -> {:ok, user}
  end
end

# With pattern
case find_user_safe(1, users) do
  {:ok, user} -> user.name
  {:error, _} -> "default"
end
```

**Why this translation:**
- Haskell's Maybe makes optionality explicit in types
- Elixir uses nil for absent values, no compile-time checking
- For explicit error handling, use `{:ok, value}` / `{:error, reason}` tuples
- Pattern matching provides runtime safety in both languages

### Pattern 2: Either/Error Handling

**Haskell:**
```haskell
-- Either for error handling
divide :: Float -> Float -> Either String Float
divide _ 0 = Left "Division by zero"
divide x y = Right (x / y)

-- Pattern matching
case divide 10 2 of
  Left err -> putStrLn $ "Error: " ++ err
  Right result -> print result

-- Functor/Monad operations
fmap (*2) (divide 10 2)  -- Either String Float

-- Chaining with bind
divide 10 2 >>= \x -> divide x 2 >>= \y -> Right (x + y)

-- Or with do-notation
calculation :: Either String Float
calculation = do
  x <- divide 10 2
  y <- divide x 2
  return (x + y)
```

**Elixir:**
```elixir
# Tagged tuples for error handling
def divide(_, 0), do: {:error, :division_by_zero}
def divide(x, y), do: {:ok, x / y}

# Pattern matching
case divide(10, 2) do
  {:ok, result} -> IO.puts("Result: #{result}")
  {:error, reason} -> IO.puts("Error: #{reason}")
end

# Transformation on success
case divide(10, 2) do
  {:ok, value} -> {:ok, value * 2}
  error -> error
end

# Chaining with 'with' (like do-notation)
def calculation do
  with {:ok, x} <- divide(10, 2),
       {:ok, y} <- divide(x, 2) do
    {:ok, x + y}
  else
    {:error, reason} -> {:error, reason}
  end
end

# Or using pipelines (assuming functions return tagged tuples)
def calculation_pipeline do
  divide(10, 2)
  |> bind(&divide(&1, 2))
  |> bind(&{:ok, &1 * 2})
end

defp bind({:ok, value}, func), do: func.(value)
defp bind(error, _), do: error
```

**Why this translation:**
- Haskell Either → Elixir `{:ok, value}` / `{:error, reason}` tuples
- `with` expression provides similar chaining to do-notation
- Pattern matching on tuples replaces type-directed case analysis
- No automatic propagation—must handle errors explicitly

### Pattern 3: Lazy Evaluation → Streams

**Haskell:**
```haskell
-- Infinite lazy list
naturals :: [Integer]
naturals = [1..]

-- Take first 10
take 10 naturals  -- [1,2,3,4,5,6,7,8,9,10]

-- Lazy Fibonacci
fibs :: [Integer]
fibs = 0 : 1 : zipWith (+) fibs (tail fibs)

take 10 fibs  -- [0,1,1,2,3,5,8,13,21,34]

-- Lazy operations (only evaluated as needed)
result :: Integer
result = head $ filter (> 1000) $ map (^2) naturals
-- Efficient: stops after finding first match
```

**Elixir:**
```elixir
# Infinite stream
naturals = Stream.iterate(1, &(&1 + 1))

# Take first 10
Enum.take(naturals, 10)  # [1,2,3,4,5,6,7,8,9,10]

# Lazy Fibonacci using Stream
defmodule Fib do
  def stream do
    Stream.unfold({0, 1}, fn {a, b} -> {a, {b, a + b}} end)
  end
end

Enum.take(Fib.stream(), 10)  # [0,1,1,2,3,5,8,13,21,34]

# Lazy operations (only evaluated when consumed)
result =
  naturals
  |> Stream.map(&(&1 * &1))
  |> Stream.filter(&(&1 > 1000))
  |> Enum.take(1)
  |> hd()
# Efficient: stops after finding first match
```

**Why this translation:**
- Haskell lists are lazy by default; Elixir lists are strict
- Use `Stream` module for lazy operations in Elixir
- Stream operations compose without intermediate lists
- Must call `Enum.*` to materialize stream results

### Pattern 4: Function Composition

**Haskell:**
```haskell
-- Function composition (right to left)
processData :: String -> [String]
processData = sort . filter (not . null) . map trim . lines

-- Or with function application
processData' text = sort $ filter (not . null) $ map trim $ lines text

-- Point-free style
double :: Int -> Int
double = (*2)

addThenDouble :: Int -> Int
addThenDouble = (*2) . (+1)
```

**Elixir:**
```elixir
# Pipe operator (left to right)
def process_data(text) do
  text
  |> String.split("\n")
  |> Enum.map(&String.trim/1)
  |> Enum.filter(&(&1 != ""))
  |> Enum.sort()
end

# Function capture
double = &(&1 * 2)
double.(5)  # 10

# Composing with anonymous functions
add_then_double = fn x -> (x + 1) * 2 end
add_then_double.(5)  # 12

# Or using pipelines
def add_then_double(x) do
  x
  |> Kernel.+(1)
  |> Kernel.*(2)
end
```

**Why this translation:**
- Haskell `.` composes right-to-left; Elixir `|>` pipes left-to-right
- Elixir pipes are more readable for step-by-step transformations
- Function capture `&` provides some point-free style
- Elixir prefers named functions over anonymous composition

### Pattern 5: Type Classes → Protocols

**Haskell:**
```haskell
-- Define type class
class Serializable a where
  serialize :: a -> String
  deserialize :: String -> Maybe a

-- Implement for type
data User = User { name :: String, age :: Int }

instance Serializable User where
  serialize (User n a) = n ++ "," ++ show a
  deserialize str = case split ',' str of
    [n, a] -> Just $ User n (read a)
    _ -> Nothing

-- Use polymorphically
saveToFile :: Serializable a => a -> IO ()
saveToFile obj = writeFile "data.txt" (serialize obj)
```

**Elixir:**
```elixir
# Define protocol
defprotocol Serializable do
  @doc "Serialize value to string"
  def serialize(value)

  @doc "Deserialize string to value"
  def deserialize(string)
end

# Implement for struct
defmodule User do
  defstruct [:name, :age]
end

defimpl Serializable, for: User do
  def serialize(%User{name: name, age: age}) do
    "#{name},#{age}"
  end

  def deserialize(string) do
    case String.split(string, ",") do
      [name, age_str] ->
        case Integer.parse(age_str) do
          {age, _} -> {:ok, %User{name: name, age: age}}
          :error -> {:error, :invalid_age}
        end
      _ ->
        {:error, :invalid_format}
    end
  end
end

# Use with any type implementing protocol
def save_to_file(obj) do
  File.write("data.txt", Serializable.serialize(obj))
end
```

**Why this translation:**
- Type classes → Protocols for polymorphism
- Haskell has compile-time dispatch; Elixir has runtime dispatch
- Protocols can be implemented for existing types (open extension)
- No type constraints at call site—runtime protocol check

---

## Concurrency Patterns

### Haskell STM → Elixir GenServer/Agent

**Haskell:**
```haskell
import Control.Concurrent.STM

type Account = TVar Int

transfer :: Account -> Account -> Int -> STM ()
transfer from to amount = do
  fromBalance <- readTVar from
  when (fromBalance < amount) retry  -- Blocks until condition met
  modifyTVar from (subtract amount)
  modifyTVar to (+ amount)

main :: IO ()
main = do
  account1 <- newTVarIO 1000
  account2 <- newTVarIO 0

  atomically $ transfer account1 account2 500

  balances <- atomically $ do
    b1 <- readTVar account1
    b2 <- readTVar account2
    return (b1, b2)

  print balances  -- (500, 500)
```

**Elixir:**
```elixir
# Using Agent for simple state
defmodule Account do
  use Agent

  def start_link(initial_balance) do
    Agent.start_link(fn -> initial_balance end)
  end

  def balance(pid) do
    Agent.get(pid, & &1)
  end

  def transfer(from_pid, to_pid, amount) do
    # Not atomic across agents - need GenServer or ETS for that
    from_balance = Agent.get(from_pid, & &1)

    if from_balance >= amount do
      Agent.update(from_pid, &(&1 - amount))
      Agent.update(to_pid, &(&1 + amount))
      :ok
    else
      {:error, :insufficient_funds}
    end
  end
end

# Usage
{:ok, account1} = Account.start_link(1000)
{:ok, account2} = Account.start_link(0)

Account.transfer(account1, account2, 500)

{Account.balance(account1), Account.balance(account2)}  # {500, 500}

# For true atomic transfers, use GenServer:
defmodule Bank do
  use GenServer

  def start_link(_) do
    GenServer.start_link(__MODULE__, %{}, name: __MODULE__)
  end

  def transfer(from_id, to_id, amount) do
    GenServer.call(__MODULE__, {:transfer, from_id, to_id, amount})
  end

  @impl true
  def init(_) do
    {:ok, %{}}
  end

  @impl true
  def handle_call({:transfer, from_id, to_id, amount}, _from, accounts) do
    from_balance = Map.get(accounts, from_id, 0)

    if from_balance >= amount do
      accounts =
        accounts
        |> Map.update(from_id, 0, &(&1 - amount))
        |> Map.update(to_id, 0, &(&1 + amount))
      {:reply, :ok, accounts}
    else
      {:reply, {:error, :insufficient_funds}, accounts}
    end
  end
end
```

**Why this translation:**
- Haskell STM provides composable atomic transactions
- Elixir uses processes (Agent/GenServer) for state isolation
- Agent for simple get/update; GenServer for complex logic
- No built-in retry semantics—must implement manually
- OTP supervision provides fault tolerance STM doesn't

### Haskell Async → Elixir Task

**Haskell:**
```haskell
import Control.Concurrent.Async

main :: IO ()
main = do
  -- Run two actions concurrently
  (result1, result2) <- concurrently
    (fetchUrl "http://example.com/1")
    (fetchUrl "http://example.com/2")

  print (result1, result2)

-- Race: first to complete wins
winner <- race
  (fetchFromServer1 key)
  (fetchFromServer2 key)

-- Map concurrently
results <- mapConcurrently fetchUrl urls
```

**Elixir:**
```elixir
# Run two actions concurrently
def main do
  task1 = Task.async(fn -> fetch_url("http://example.com/1") end)
  task2 = Task.async(fn -> fetch_url("http://example.com/2") end)

  result1 = Task.await(task1)
  result2 = Task.await(task2)

  IO.inspect({result1, result2})
end

# Or using Task.async_stream for multiple URLs
def fetch_all(urls) do
  urls
  |> Task.async_stream(&fetch_url/1, max_concurrency: 10)
  |> Enum.map(fn {:ok, result} -> result end)
end

# Race pattern (not built-in, use yield_many)
def race(func1, func2) do
  task1 = Task.async(func1)
  task2 = Task.async(func2)

  case Task.yield_many([task1, task2], :infinity) do
    [{task, {:ok, result}} | _] ->
      # First one done
      Task.shutdown(other_task(task, task1, task2))
      result
    _ ->
      :no_result
  end
end
```

**Why this translation:**
- `concurrently` → spawn multiple Tasks, await all
- `race` → yield_many and take first result
- `mapConcurrently` → Task.async_stream with max_concurrency
- Task provides supervision tree integration

---

## IO Monad → Pragmatic Effects

### Haskell Pure/Impure Separation

**Haskell:**
```haskell
-- Pure function
calculateTotal :: [Item] -> Double
calculateTotal items = sum $ map price items

-- Impure function (IO monad)
readConfig :: FilePath -> IO Config
readConfig path = do
  contents <- readFile path
  pure (parseConfig contents)

-- Cannot mix pure and IO without explicit lifting
main :: IO ()
main = do
  config <- readConfig "config.json"
  let total = calculateTotal (items config)
  putStrLn $ "Total: " ++ show total
```

**Elixir:**
```elixir
# Pure function (by convention)
def calculate_total(items) do
  Enum.reduce(items, 0, fn item, acc -> acc + item.price end)
end

# Impure function (allowed anywhere, no marker)
def read_config(path) do
  case File.read(path) do
    {:ok, contents} -> parse_config(contents)
    {:error, reason} -> {:error, reason}
  end
end

# Mix freely
def main do
  case read_config("config.json") do
    {:ok, config} ->
      total = calculate_total(config.items)
      IO.puts("Total: #{total}")
    {:error, reason} ->
      IO.puts("Error: #{reason}")
  end
end
```

**Why this translation:**
- Haskell enforces purity with IO type
- Elixir has no such enforcement—convention only
- Use naming conventions: `read_*`, `write_*`, `send_*` for side effects
- Pattern match on `{:ok, _}` / `{:error, _}` for explicit error handling
- Loss: No compile-time guarantee of purity

---

## Error Handling Translation

### Haskell Exceptions vs Elixir "Let It Crash"

**Haskell:**
```haskell
import Control.Exception

-- Catching exceptions
readFileSafe :: FilePath -> IO (Maybe String)
readFileSafe path = do
  result <- try (readFile path) :: IO (Either SomeException String)
  case result of
    Left _ -> return Nothing
    Right contents -> return (Just contents)

-- Or with catch
readFileSafe' :: FilePath -> IO (Maybe String)
readFileSafe' path =
  (Just <$> readFile path) `catch` \(_ :: SomeException) -> return Nothing
```

**Elixir:**
```elixir
# Error tuples (preferred)
def read_file_safe(path) do
  case File.read(path) do
    {:ok, contents} -> {:ok, contents}
    {:error, reason} -> {:error, reason}
  end
end

# Try/rescue (avoid for control flow)
def read_file_with_rescue(path) do
  try do
    {:ok, File.read!(path)}
  rescue
    e in File.Error -> {:error, e.reason}
  end
end

# "Let it crash" philosophy - don't catch, supervise
defmodule FileReader do
  use GenServer

  def start_link(opts) do
    GenServer.start_link(__MODULE__, opts)
  end

  def read(pid, path) do
    GenServer.call(pid, {:read, path})
  end

  @impl true
  def handle_call({:read, path}, _from, state) do
    # If this crashes, supervisor restarts it
    contents = File.read!(path)
    {:reply, {:ok, contents}, state}
  end
end

# Supervisor ensures restart on crash
children = [
  {FileReader, []}
]

Supervisor.start_link(children, strategy: :one_for_one)
```

**Why this translation:**
- Haskell: Catch exceptions, handle explicitly
- Elixir: Let processes crash, supervisor restarts
- Use tagged tuples `{:ok, _}` / `{:error, _}` for expected failures
- Use `try/rescue` only for unexpected exceptions (rare)
- Supervision trees provide fault isolation

---

## Module System Translation

### Haskell Modules

**Haskell:**
```haskell
-- File: src/MyApp/User.hs
module MyApp.User
  ( User(..)          -- Export type with all constructors
  , createUser        -- Export function
  , validateEmail     -- Export function
  ) where

import Data.Text (Text)
import qualified Data.Map as M

data User = User
  { name :: Text
  , email :: Text
  } deriving (Show, Eq)

createUser :: Text -> Text -> User
createUser n e = User n e

validateEmail :: Text -> Bool
validateEmail = undefined  -- implementation
```

**Elixir:**
```elixir
# File: lib/my_app/user.ex
defmodule MyApp.User do
  @moduledoc """
  User module for managing user data.
  """

  defstruct [:name, :email]

  @type t :: %__MODULE__{
    name: String.t(),
    email: String.t()
  }

  @doc """
  Creates a new user.
  """
  @spec create_user(String.t(), String.t()) :: t()
  def create_user(name, email) do
    %__MODULE__{name: name, email: email}
  end

  @doc """
  Validates an email address.
  """
  @spec validate_email(String.t()) :: boolean()
  def validate_email(email) do
    # implementation
    String.contains?(email, "@")
  end

  # Private function (not exported)
  defp internal_helper do
    # ...
  end
end
```

**Why this translation:**
- Haskell explicit exports → Elixir `def` (public) / `defp` (private)
- Type signatures → `@spec` (optional, via Dialyzer)
- Haskell type synonyms → Elixir `@type`
- Module documentation → `@moduledoc` and `@doc`

---

## Build System Translation

### Haskell (Cabal/Stack) → Elixir (Mix)

**Haskell (package.yaml for Stack):**
```yaml
name: my-app
version: 0.1.0.0

dependencies:
  - base >= 4.14 && < 5
  - text
  - aeson
  - containers

library:
  source-dirs: src

executables:
  my-app:
    main: Main.hs
    source-dirs: app
    dependencies:
      - my-app

tests:
  my-app-test:
    main: Spec.hs
    source-dirs: test
    dependencies:
      - my-app
      - hspec
      - QuickCheck
```

**Elixir (mix.exs):**
```elixir
defmodule MyApp.MixProject do
  use Mix.Project

  def project do
    [
      app: :my_app,
      version: "0.1.0",
      elixir: "~> 1.14",
      start_permanent: Mix.env() == :prod,
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
      {:jason, "~> 1.4"},      # Like aeson for JSON
      {:plug_cowboy, "~> 2.6"} # HTTP server
    ]
  end
end
```

**Common commands:**

| Haskell | Elixir | Purpose |
|---------|--------|---------|
| `stack build` | `mix compile` | Build project |
| `stack run` | `mix run` | Run application |
| `stack test` | `mix test` | Run tests |
| `stack ghci` | `iex -S mix` | Interactive shell |
| `cabal install` | `mix deps.get` | Get dependencies |
| `cabal repl` | `iex -S mix` | REPL with project |

---

## Testing Translation

### Haskell HSpec/QuickCheck → Elixir ExUnit/StreamData

**Haskell (HSpec + QuickCheck):**
```haskell
module MyApp.UserSpec where

import Test.Hspec
import Test.QuickCheck
import MyApp.User

spec :: Spec
spec = do
  describe "createUser" $ do
    it "creates a user with given name" $ do
      let user = createUser "Alice" "alice@example.com"
      name user `shouldBe` "Alice"

  describe "validateEmail" $ do
    it "returns True for valid email" $ do
      validateEmail "user@example.com" `shouldBe` True

    it "returns False for invalid email" $ do
      validateEmail "invalid" `shouldBe` False

  describe "property: reversing twice" $ do
    it "returns original" $ property $ \xs ->
      reverse (reverse xs) == (xs :: [Int])
```

**Elixir (ExUnit + StreamData):**
```elixir
defmodule MyApp.UserTest do
  use ExUnit.Case
  use ExUnitProperties

  alias MyApp.User

  describe "create_user/2" do
    test "creates a user with given name" do
      user = User.create_user("Alice", "alice@example.com")
      assert user.name == "Alice"
    end
  end

  describe "validate_email/1" do
    test "returns true for valid email" do
      assert User.validate_email("user@example.com")
    end

    test "returns false for invalid email" do
      refute User.validate_email("invalid")
    end
  end

  describe "property: reversing twice" do
    property "returns original" do
      check all list <- list_of(integer()) do
        assert Enum.reverse(Enum.reverse(list)) == list
      end
    end
  end
end
```

**Why this translation:**
- HSpec → ExUnit (both BDD-style)
- QuickCheck → StreamData (property-based testing)
- `shouldBe` → `assert`
- `property` → `check all`

---

## Common Pitfalls

### 1. Expecting Compile-Time Type Safety

**Problem:** Elixir won't catch type errors at compile time

```elixir
# No compile error, but runtime crash
def add_numbers(a, b), do: a + b

add_numbers(1, "hello")  # Runtime error: ArithmeticError
```

**Fix:** Use guards, pattern matching, and Dialyzer specs

```elixir
@spec add_numbers(number(), number()) :: number()
def add_numbers(a, b) when is_number(a) and is_number(b) do
  a + b
end

# Dialyzer will warn if called incorrectly in other modules
```

### 2. Forgetting Lazy → Strict Evaluation

**Problem:** Infinite lists won't work without Stream

```elixir
# This will never finish!
naturals = Enum.map(1..999_999_999_999, & &1)
```

**Fix:** Use Stream for lazy evaluation

```elixir
naturals = Stream.iterate(1, &(&1 + 1))
Enum.take(naturals, 10)  # Only computes first 10
```

### 3. Missing IO Monad Discipline

**Problem:** No compile-time separation of pure/impure

```elixir
# Looks pure, but has side effect
def calculate(x) do
  IO.puts("Calculating...")  # Side effect!
  x * 2
end
```

**Fix:** Use naming conventions and separate concerns

```elixir
# Pure function
def calculate(x), do: x * 2

# Separate logging
def calculate_with_logging(x) do
  IO.puts("Calculating...")
  calculate(x)
end
```

### 4. Not Leveraging OTP for Concurrency

**Problem:** Trying to replicate STM with manual locking

```elixir
# Bad: complex manual state management
def transfer(from, to, amount) do
  # Race conditions, no supervision
end
```

**Fix:** Use GenServer, Agent, or supervised processes

```elixir
# Good: OTP handles state and supervision
defmodule Bank do
  use GenServer
  # ... (see Concurrency section)
end
```

### 5. Ignoring "Let It Crash" Philosophy

**Problem:** Catching every error

```elixir
# Overly defensive
def process(data) do
  try do
    parse(data)
  rescue
    _ -> {:error, :parse_error}
  end
end
```

**Fix:** Let expected errors return tuples, unexpected errors crash

```elixir
# Good: expected errors are tuples
def parse(data) do
  case Jason.decode(data) do
    {:ok, parsed} -> {:ok, parsed}
    {:error, reason} -> {:error, reason}
  end
end

# Supervise processes that might crash
children = [
  {Worker, []}
]
Supervisor.start_link(children, strategy: :one_for_one)
```

---

## Examples

### Example 1: Simple - Maybe to Optional Tuple

**Before (Haskell):**
```haskell
findUser :: Int -> [User] -> Maybe User
findUser userId = find (\u -> userId == userId u)

main :: IO ()
main = do
  let users = [User "Alice" 1, User "Bob" 2]
  case findUser 1 users of
    Nothing -> putStrLn "User not found"
    Just user -> putStrLn $ "Found: " ++ name user
```

**After (Elixir):**
```elixir
def find_user(user_id, users) do
  case Enum.find(users, fn u -> u.id == user_id end) do
    nil -> {:error, :not_found}
    user -> {:ok, user}
  end
end

def main do
  users = [%User{name: "Alice", id: 1}, %User{name: "Bob", id: 2}]

  case find_user(1, users) do
    {:error, :not_found} -> IO.puts("User not found")
    {:ok, user} -> IO.puts("Found: #{user.name}")
  end
end
```

### Example 2: Medium - Functor/Monad to Pipeline

**Before (Haskell):**
```haskell
processUsers :: [User] -> IO [String]
processUsers users = do
  let activeUsers = filter isActive users
  let names = map name activeUsers
  let uppercased = map (map toUpper) names
  return $ sort uppercased

-- Or with function composition
processUsers' :: [User] -> IO [String]
processUsers' = return . sort . map (map toUpper) . map name . filter isActive
```

**After (Elixir):**
```elixir
def process_users(users) do
  users
  |> Enum.filter(&is_active?/1)
  |> Enum.map(& &1.name)
  |> Enum.map(&String.upcase/1)
  |> Enum.sort()
end

# Or more concise
def process_users(users) do
  users
  |> Enum.filter(&is_active?/1)
  |> Enum.map(&(&1.name |> String.upcase()))
  |> Enum.sort()
end
```

### Example 3: Complex - STM Transaction to GenServer

**Before (Haskell):**
```haskell
import Control.Concurrent.STM
import Control.Concurrent.Async

data BankState = BankState
  { accounts :: TVar (Map AccountId Int)
  , transactions :: TVar [Transaction]
  }

transfer :: BankState -> AccountId -> AccountId -> Int -> STM Bool
transfer state fromId toId amount = do
  accts <- readTVar (accounts state)
  txns <- readTVar (transactions state)

  case (Map.lookup fromId accts, Map.lookup toId accts) of
    (Just fromBal, Just toBal) | fromBal >= amount -> do
      let accts' = Map.insert fromId (fromBal - amount) $
                   Map.insert toId (toBal + amount) accts
      writeTVar (accounts state) accts'
      writeTVar (transactions state) (Transaction fromId toId amount : txns)
      return True
    _ -> return False

main :: IO ()
main = do
  state <- BankState <$> newTVarIO (Map.fromList [(1, 1000), (2, 500)])
                     <*> newTVarIO []

  success <- atomically $ transfer state 1 2 300
  if success
    then putStrLn "Transfer successful"
    else putStrLn "Transfer failed"
```

**After (Elixir):**
```elixir
defmodule Bank do
  use GenServer

  # Client API

  def start_link(initial_accounts) do
    GenServer.start_link(__MODULE__, initial_accounts, name: __MODULE__)
  end

  def transfer(from_id, to_id, amount) do
    GenServer.call(__MODULE__, {:transfer, from_id, to_id, amount})
  end

  def get_balance(account_id) do
    GenServer.call(__MODULE__, {:get_balance, account_id})
  end

  # Server Callbacks

  @impl true
  def init(accounts) do
    {:ok, %{accounts: accounts, transactions: []}}
  end

  @impl true
  def handle_call({:transfer, from_id, to_id, amount}, _from, state) do
    from_balance = Map.get(state.accounts, from_id, 0)
    to_balance = Map.get(state.accounts, to_id, 0)

    if from_balance >= amount do
      accounts =
        state.accounts
        |> Map.put(from_id, from_balance - amount)
        |> Map.put(to_id, to_balance + amount)

      transaction = %{from: from_id, to: to_id, amount: amount}
      transactions = [transaction | state.transactions]

      {:reply, :ok, %{state | accounts: accounts, transactions: transactions}}
    else
      {:reply, {:error, :insufficient_funds}, state}
    end
  end

  @impl true
  def handle_call({:get_balance, account_id}, _from, state) do
    balance = Map.get(state.accounts, account_id, 0)
    {:reply, balance, state}
  end
end

# Usage
defmodule Main do
  def run do
    {:ok, _pid} = Bank.start_link(%{1 => 1000, 2 => 500})

    case Bank.transfer(1, 2, 300) do
      :ok -> IO.puts("Transfer successful")
      {:error, reason} -> IO.puts("Transfer failed: #{reason}")
    end

    IO.puts("Account 1: #{Bank.get_balance(1)}")  # 700
    IO.puts("Account 2: #{Bank.get_balance(2)}")  # 800
  end
end
```

---

## See Also

For more examples and patterns, see:

- `meta-convert-dev` - Foundational patterns with cross-language examples
- `convert-clojure-elixir` - Similar dynamic FP on JVM → BEAM
- `convert-erlang-elixir` - Native BEAM language conversions
- `lang-haskell-dev` - Haskell development patterns
- `lang-elixir-dev` - Elixir development patterns

Cross-cutting pattern skills:

- `patterns-concurrency-dev` - STM, async, GenServer across languages
- `patterns-serialization-dev` - Aeson, Jason, validation patterns
- `patterns-metaprogramming-dev` - Template Haskell, Elixir macros
