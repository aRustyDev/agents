---
name: convert-elixir-haskell
description: Convert Elixir code to idiomatic Haskell. Use when migrating Elixir projects to Haskell, translating BEAM actor patterns to pure functional programming with IO monad, or refactoring dynamic OTP behaviors to static typed equivalents. Extends meta-convert-dev with Elixir-to-Haskell specific patterns.
---

# Convert Elixir to Haskell

Convert Elixir code to idiomatic Haskell. This skill extends `meta-convert-dev` with Elixir-to-Haskell specific type mappings, idiom translations, and transformation strategies for moving from BEAM's actor model to pure functional programming with strong static types.

## This Skill Extends

- `meta-convert-dev` - Foundational conversion patterns (APTV workflow, testing strategies)

For general concepts like the Analyze → Plan → Transform → Validate workflow, testing strategies, and common pitfalls, see the meta-skill first.

## This Skill Adds

- **Type mappings**: Elixir dynamic types → Haskell static types (Hindley-Milner)
- **Idiom translations**: Actors/OTP → STM/async, pattern matching nuances, pipe vs composition
- **Error handling**: Tagged tuples → Maybe/Either, supervision → explicit error handling
- **Async patterns**: GenServer/Tasks → IO monad, async library, STM
- **Evaluation strategy**: Strict (Elixir) → Lazy (Haskell) translation
- **Effects**: Effects anywhere → IO monad boundary, pure core

## This Skill Does NOT Cover

- General conversion methodology - see `meta-convert-dev`
- Elixir language fundamentals - see `lang-elixir-dev`
- Haskell language fundamentals - see `lang-haskell-dev`
- Reverse conversion (Haskell → Elixir) - see `convert-haskell-elixir`

---

## Quick Reference

| Elixir | Haskell | Notes |
|--------|---------|-------|
| `{:ok, value}` | `Right value` | Either monad for results |
| `{:error, reason}` | `Left reason` | Either monad for errors |
| `nil` | `Nothing` | Maybe monad |
| `value` | `Just value` | Maybe monad |
| `Enum.map/2` | `fmap` or `map` | Functor/list operations |
| `\|>` | `$` or `&` or `.` | Function application/composition |
| `def func(arg)` | `func :: Type -> Type`<br>`func arg = ...` | Function with type signature |
| `GenServer` | `TVar` + `STM` | Actor → transactional memory |
| `Task.async/1` | `async` | Concurrent execution |
| `receive do ... end` | Pattern match on `Chan` | Message passing |
| `Map.t()` | `Map k v` | Hash map |
| `%{key: value}` | `Map.fromList [("key", value)]` | Map construction |

---

## When Converting Code

1. **Analyze effects first** - Identify where side effects occur in Elixir
2. **Map types explicitly** - Create complete type mapping table from dynamic to static
3. **Separate pure from impure** - Pure core with IO boundary
4. **Translate actors to alternatives** - GenServer → STM, supervision → error handling
5. **Handle laziness** - Elixir strict, Haskell lazy by default
6. **Test equivalence** - Property-based testing for invariants

---

## Type System Mapping

### Primitive Types

| Elixir | Haskell | Notes |
|--------|---------|-------|
| `integer()` | `Int` / `Integer` | `Int` fixed-width, `Integer` arbitrary precision |
| `float()` | `Double` | 64-bit float |
| `boolean()` | `Bool` | `True` / `False` |
| `atom()` | Custom ADT | `:ok`, `:error` → data constructors |
| `binary()` / `String.t()` | `Text` / `ByteString` | Use `Data.Text` for UTF-8 |
| `charlist()` | `String` | `String` is `[Char]` in Haskell |
| `pid()` | `ThreadId` / `Async` | Process identifiers |
| `reference()` | `MVar` / `TVar` | Reference types |

### Collection Types

| Elixir | Haskell | Notes |
|--------|---------|-------|
| `list()` | `[a]` | Linked list |
| `tuple()` | `(a, b, ...)` | Fixed-size tuple |
| `%{}` (map) | `Map k v` | Requires `Data.Map` |
| `MapSet.t()` | `Set a` | Requires `Data.Set` |
| Keyword list | `[(Text, a)]` | List of pairs |
| Range | `[a..b]` | List comprehension range |

### Composite Types

| Elixir | Haskell | Notes |
|--------|---------|-------|
| Struct | `data Type = Type { ... }` | Record syntax |
| `{:ok, value}` | `Right value` | `Either String a` |
| `{:error, reason}` | `Left reason` | `Either String a` |
| `nil` | `Nothing` | `Maybe a` |
| Value | `Just value` | `Maybe a` |
| Union types (spec) | `data Type = A \| B` | Sum type (ADT) |
| GenServer state | `TVar s` | Shared mutable state |
| Protocol | Type class | Polymorphism |

### Function Types

| Elixir | Haskell | Notes |
|--------|---------|-------|
| `(arg1, arg2 -> return)` | `arg1 -> arg2 -> return` | Curried by default |
| `(() -> return)` | `IO return` | Side-effecting function |
| `(a -> b)` | `a -> b` | Pure function |
| Anonymous fn | Lambda `\x -> ...` | Lambda syntax |

---

## Idiom Translation

### Pattern: Tagged Tuples → Either/Maybe

**Elixir:**
```elixir
def divide(a, b) when b != 0, do: {:ok, a / b}
def divide(_, 0), do: {:error, :division_by_zero}

case divide(10, 2) do
  {:ok, result} -> IO.puts("Result: #{result}")
  {:error, reason} -> IO.puts("Error: #{reason}")
end
```

**Haskell:**
```haskell
divide :: Float -> Float -> Either String Float
divide a 0 = Left "division by zero"
divide a b = Right (a / b)

case divide 10 2 of
  Right result -> putStrLn $ "Result: " ++ show result
  Left reason -> putStrLn $ "Error: " ++ reason

-- Or with do-notation (Either monad)
calculation :: Either String Float
calculation = do
  a <- divide 10 2
  b <- divide a 5
  return (b * 2)
```

**Why this translation:**
- Elixir uses tagged tuples `{:ok, value}` / `{:error, reason}` idiomatically
- Haskell's `Either` type encodes the same semantics with stronger type safety
- Pattern matching works similarly in both
- Haskell's `Either` monad allows chaining with `do`-notation

### Pattern: Pipe Operator → Function Composition

**Elixir:**
```elixir
result =
  [1, 2, 3, 4]
  |> Enum.filter(&(rem(&1, 2) == 0))
  |> Enum.map(&(&1 * 2))
  |> Enum.sum()
```

**Haskell:**
```haskell
-- Point-free with composition
result = sum . map (*2) . filter even $ [1, 2, 3, 4]

-- Or with ($) for clarity
result = sum $ map (*2) $ filter even [1, 2, 3, 4]

-- Or with (&) for left-to-right (Data.Function)
import Data.Function ((&))

result = [1, 2, 3, 4]
       & filter even
       & map (*2)
       & sum
```

**Why this translation:**
- Elixir's `|>` passes result forward (left-to-right)
- Haskell's `.` composes right-to-left: `(f . g) x = f (g x)`
- Use `$` for right-to-left with clarity, or `&` for left-to-right
- Point-free style is idiomatic Haskell

### Pattern: Pattern Matching with Guards

**Elixir:**
```elixir
def classify(n) when n < 0, do: :negative
def classify(0), do: :zero
def classify(n) when n < 10, do: :small
def classify(_), do: :large
```

**Haskell:**
```haskell
-- Using guards
classify :: Int -> String
classify n
  | n < 0     = "negative"
  | n == 0    = "zero"
  | n < 10    = "small"
  | otherwise = "large"

-- Or with case
classify' :: Int -> String
classify' n = case n of
  0 -> "zero"
  _ | n < 0   -> "negative"
    | n < 10  -> "small"
    | otherwise -> "large"
```

**Why this translation:**
- Both languages support guard clauses
- Haskell uses `|` for guards instead of `when`
- `otherwise` is the catch-all (equivalent to Elixir's `_`)
- Pattern matching on literals comes before guards in Haskell

### Pattern: Enum Comprehensions → List Comprehensions

**Elixir:**
```elixir
result = for x <- [1, 2, 3, 4, 5],
             y <- [1, 2, 3],
             x * y > 5,
             do: {x, y}
```

**Haskell:**
```haskell
result = [(x, y) | x <- [1..5], y <- [1..3], x * y > 5]
```

**Why this translation:**
- Syntax is nearly identical
- Haskell's list comprehensions are more concise
- Filters come after generators in both
- Multiple generators work the same way

### Pattern: Recursive List Processing

**Elixir:**
```elixir
def sum([]), do: 0
def sum([head | tail]), do: head + sum(tail)

def map([], _func), do: []
def map([head | tail], func), do: [func.(head) | map(tail, func)]
```

**Haskell:**
```haskell
sum' :: [Int] -> Int
sum' [] = 0
sum' (x:xs) = x + sum' xs

map' :: (a -> b) -> [a] -> [b]
map' _ [] = []
map' f (x:xs) = f x : map' f xs
```

**Why this translation:**
- Both use head/tail pattern matching (`[head | tail]` vs `(x:xs)`)
- Base case (empty list) first in both
- Haskell requires type signatures (recommended in Elixir)
- Haskell's cons operator `:` is infix

### Pattern: With Statement → Do-Notation

**Elixir:**
```elixir
def create_user(params) do
  with {:ok, validated} <- validate_params(params),
       {:ok, user} <- insert_user(validated),
       {:ok, email_sent} <- send_email(user) do
    {:ok, user}
  else
    {:error, reason} -> {:error, reason}
  end
end
```

**Haskell:**
```haskell
createUser :: Params -> IO (Either String User)
createUser params = runExceptT $ do
  validated <- ExceptT $ return $ validateParams params
  user <- ExceptT $ insertUser validated
  emailSent <- ExceptT $ sendEmail user
  return user

-- Or with Either monad directly
createUser' :: Params -> Either String User
createUser' params = do
  validated <- validateParams params
  user <- insertUser validated
  emailSent <- sendEmail user
  return user
```

**Why this translation:**
- Elixir's `with` chains operations that can fail
- Haskell's `do`-notation for `Either` monad achieves the same
- `ExceptT` transformer for mixing `IO` with `Either`
- Short-circuits on first `Left` (error) automatically

---

## Error Handling

### Elixir Error Model → Haskell Error Model

| Elixir Pattern | Haskell Pattern | Notes |
|----------------|-----------------|-------|
| `{:ok, value}` | `Right value` | Success case |
| `{:error, reason}` | `Left reason` | Error case |
| `nil` | `Nothing` | Absence of value |
| `value` | `Just value` | Presence of value |
| `raise Exception` | `error "message"` | Runtime exception (avoid) |
| Supervisor restart | Explicit error handling | No supervision trees |
| `try...rescue` | `catch` / `try` | Exception handling (rare) |

### Pattern: Supervision → Explicit Error Handling

**Elixir:**
```elixir
# Supervisor restarts failed processes
defmodule MyApp.Supervisor do
  use Supervisor

  def start_link(_) do
    Supervisor.start_link(__MODULE__, :ok, name: __MODULE__)
  end

  def init(:ok) do
    children = [
      {Worker, []}
    ]
    Supervisor.init(children, strategy: :one_for_one)
  end
end
```

**Haskell:**
```haskell
-- Explicit retry logic with error handling
import Control.Exception (try, SomeException)
import Control.Concurrent (threadDelay)

retryWithBackoff :: Int -> IO a -> IO (Either SomeException a)
retryWithBackoff 0 action = try action
retryWithBackoff n action = do
  result <- try action
  case result of
    Right val -> return $ Right val
    Left _ -> do
      threadDelay (1000000 * 2^(5-n))  -- Exponential backoff
      retryWithBackoff (n-1) action

-- Worker that can fail and be retried
worker :: IO ()
worker = do
  result <- retryWithBackoff 5 dangerousOperation
  case result of
    Right val -> processSuccess val
    Left err -> logError err
```

**Why this translation:**
- Elixir: "Let it crash" philosophy with supervisor restart
- Haskell: Explicit error handling with retry logic
- No built-in supervision trees in Haskell
- Must handle failures explicitly or use exception handling

### Pattern: Result Propagation

**Elixir:**
```elixir
def process_pipeline(input) do
  with {:ok, validated} <- validate(input),
       {:ok, transformed} <- transform(validated),
       {:ok, result} <- store(transformed) do
    {:ok, result}
  end
end
```

**Haskell:**
```haskell
processPipeline :: Input -> Either String Result
processPipeline input = do
  validated <- validate input
  transformed <- transform validated
  result <- store transformed
  return result

-- Or with applicative for independent operations
processPipeline' input =
  validate input >>= transform >>= store
```

**Why this translation:**
- Both short-circuit on first error
- Haskell's `Either` monad provides same chaining
- `>>=` (bind) chains dependent operations
- More concise than nested `case` statements

---

## Concurrency Patterns

### Elixir Concurrency → Haskell Concurrency

| Elixir | Haskell | Notes |
|--------|---------|-------|
| Process (lightweight) | `ThreadId` | Haskell threads are OS threads |
| `spawn/1` | `forkIO` | Spawn concurrent thread |
| `Task.async/1` | `async` | Async computation |
| `Task.await/1` | `wait` | Wait for async result |
| `send/2` | `writeChan` | Send to channel |
| `receive do ... end` | `readChan` | Receive from channel |
| `GenServer` | `TVar` + STM | Stateful server |
| `Agent` | `MVar` / `TVar` | Shared mutable state |
| Supervisor | Manual retry logic | No built-in supervision |

### Pattern: GenServer → STM

**Elixir:**
```elixir
defmodule Counter do
  use GenServer

  def start_link(initial) do
    GenServer.start_link(__MODULE__, initial, name: __MODULE__)
  end

  def increment do
    GenServer.call(__MODULE__, :increment)
  end

  def get do
    GenServer.call(__MODULE__, :get)
  end

  # Callbacks
  def init(initial), do: {:ok, initial}

  def handle_call(:increment, _from, state) do
    {:reply, state + 1, state + 1}
  end

  def handle_call(:get, _from, state) do
    {:reply, state, state}
  end
end
```

**Haskell:**
```haskell
import Control.Concurrent.STM

type Counter = TVar Int

createCounter :: Int -> IO Counter
createCounter initial = newTVarIO initial

increment :: Counter -> IO Int
increment counter = atomically $ do
  current <- readTVar counter
  let new = current + 1
  writeTVar counter new
  return new

getCount :: Counter -> IO Int
getCount counter = readTVarIO counter

-- Usage
main = do
  counter <- createCounter 0
  result1 <- increment counter
  result2 <- increment counter
  final <- getCount counter
  print final  -- 2
```

**Why this translation:**
- GenServer: Message-passing actor with state
- STM: Software Transactional Memory for safe concurrent mutations
- Both provide atomicity and state isolation
- STM is compositional (can combine transactions)
- No message queues in STM (direct state access)

### Pattern: Task.async → Async

**Elixir:**
```elixir
task1 = Task.async(fn -> fetch_user(1) end)
task2 = Task.async(fn -> fetch_user(2) end)

user1 = Task.await(task1)
user2 = Task.await(task2)
```

**Haskell:**
```haskell
import Control.Concurrent.Async

main = do
  task1 <- async $ fetchUser 1
  task2 <- async $ fetchUser 2

  user1 <- wait task1
  user2 <- wait task2

-- Or concurrently
main = do
  (user1, user2) <- concurrently (fetchUser 1) (fetchUser 2)

-- Map concurrently over list
users <- mapConcurrently fetchUser [1..10]
```

**Why this translation:**
- `Task.async` spawns concurrent computation, returns handle
- `async` library provides same semantics
- `wait` blocks until result available
- `concurrently` helper for pairs
- Similar error propagation (async throws exceptions)

### Pattern: Message Passing → Channels

**Elixir:**
```elixir
pid = spawn(fn ->
  receive do
    {:msg, value} -> IO.puts("Received: #{value}")
  end
end)

send(pid, {:msg, "hello"})
```

**Haskell:**
```haskell
import Control.Concurrent
import Control.Concurrent.Chan

main = do
  chan <- newChan

  forkIO $ do
    msg <- readChan chan
    putStrLn $ "Received: " ++ msg

  writeChan chan "hello"
  threadDelay 100000  -- Wait for thread
```

**Why this translation:**
- Elixir: Process mailbox with pattern matching
- Haskell: Typed channels (Chan a)
- No pattern matching on messages (type-safe)
- Must use explicit channel types
- `MVar` for single-value handoff, `Chan` for queues

---

## Evaluation Strategy Translation

### Strict → Lazy Conversion Patterns

Elixir evaluates strictly (arguments evaluated before function call). Haskell evaluates lazily (arguments evaluated only when needed).

**Elixir (strict):**
```elixir
# All elements processed immediately
list = Enum.map([1, 2, 3, 4, 5], fn x -> expensive_computation(x) end)
result = Enum.take(list, 2)  # But we only need 2!
```

**Haskell (lazy):**
```haskell
-- Only first 2 elements computed
list = map expensiveComputation [1, 2, 3, 4, 5]
result = take 2 list  -- Lazy: only computes first 2
```

**Key Differences:**

| Aspect | Elixir (Strict) | Haskell (Lazy) |
|--------|----------------|----------------|
| Evaluation | Immediate | On-demand |
| Infinite lists | Not possible | Natural |
| Side effects | Predictable order | Deferred (use IO) |
| Performance | Eager memory use | Space leaks possible |

### Pattern: Forcing Strictness in Haskell

**When you need strict evaluation:**

```haskell
-- Lazy fold can cause stack overflow
badSum = foldl (+) 0 [1..1000000]  -- Builds thunks

-- Strict fold
import Data.List (foldl')
goodSum = foldl' (+) 0 [1..1000000]  -- Forces evaluation

-- Bang patterns
{-# LANGUAGE BangPatterns #-}
strictFunc !x = x + 1  -- x evaluated immediately
```

### Pattern: Streams in Elixir → Lazy Lists in Haskell

**Elixir:**
```elixir
# Stream for lazy evaluation
Stream.iterate(0, &(&1 + 1))
|> Stream.map(&(&1 * 2))
|> Stream.filter(&(rem(&1, 2) == 0))
|> Enum.take(10)
```

**Haskell:**
```haskell
-- Lists are lazy by default
result = take 10
       $ filter even
       $ map (*2)
       $ iterate (+1) 0
```

**Why this translation:**
- Elixir: Explicit `Stream` for laziness
- Haskell: All lists are lazy
- Both use similar pipeline patterns
- Haskell infinite lists are natural

---

## Effects and IO Boundary

### Separating Pure from Impure

**Elixir (effects anywhere):**
```elixir
def process_user(id) do
  # Mix of pure and impure
  user = Repo.get(User, id)  # IO: Database
  name = String.upcase(user.name)  # Pure
  Logger.info("Processing #{name}")  # IO: Logging
  %{user | name: name}  # Pure
end
```

**Haskell (pure core with IO boundary):**
```haskell
-- Pure functions
uppercaseName :: User -> User
uppercaseName user = user { userName = T.toUpper (userName user) }

-- IO boundary
processUser :: Int -> IO User
processUser userId = do
  user <- getUser userId  -- IO: Database
  let updated = uppercaseName user  -- Pure
  logInfo $ "Processing " <> userName updated  -- IO: Logging
  return updated

-- Type signature shows effects
-- :: Int -> User  (pure)
-- :: Int -> IO User  (has IO effects)
```

**Why this translation:**
- Elixir: Effects can appear anywhere
- Haskell: Type system tracks effects (`IO` type)
- Pure functions don't use `IO` type
- Easier to reason about effects in Haskell
- Must explicitly lift pure values into `IO` with `return`

### Pattern: Database Queries

**Elixir (Ecto):**
```elixir
def get_active_users do
  from(u in User, where: u.active == true)
  |> Repo.all()
end
```

**Haskell (persistent or esqueleto):**
```haskell
import Database.Persist
import Database.Persist.Sql

getActiveUsers :: SqlPersistM [Entity User]
getActiveUsers = selectList [UserActive ==. True] []

-- In IO context
main :: IO ()
main = runSqlite "database.db" $ do
  users <- getActiveUsers
  liftIO $ mapM_ print users
```

**Why this translation:**
- Both use type-safe query builders
- Haskell: Explicit monad for database operations
- `SqlPersistM` is the DB monad
- `liftIO` to perform IO in DB context

---

## Common Pitfalls

1. **Forgetting Lazy Evaluation**: Haskell lists are lazy. Use strict functions (`foldl'`) when needed to avoid space leaks.

2. **Mixing IO and Pure**: In Haskell, functions must declare `IO` in type signature. Can't perform IO in pure functions.

3. **Pattern Match Exhaustiveness**: Haskell compiler warns about non-exhaustive patterns. Elixir allows partial patterns.

4. **Trying to Mutate State**: No mutation in Haskell. Use STM/MVar for shared state or pass new state explicitly.

5. **Ignoring Type Inference Limitations**: Haskell can't always infer types. Add explicit type signatures at module boundaries.

6. **Translating Supervision Literally**: No supervision trees. Use explicit retry logic, exception handling, or libraries like `retry`.

7. **Assuming Strict Evaluation**: List operations are lazy. `map` doesn't execute until values are forced.

---

## Tooling

| Tool | Purpose | Notes |
|------|---------|-------|
| `stack` / `cabal` | Build tool | Project structure and dependencies |
| `ghc` | Compiler | Glasgow Haskell Compiler |
| `ghci` | REPL | Interactive development |
| `hlint` | Linter | Suggests improvements |
| `hspec` | Testing | BDD-style testing framework |
| `QuickCheck` | Property testing | Equivalent to StreamData |
| `async` | Concurrency | Task-like async operations |
| `stm` | STM | Transactional memory for concurrency |
| `aeson` | JSON | JSON encoding/decoding |

---

## Examples

### Example 1: Simple - Function with Pattern Matching

**Before (Elixir):**
```elixir
defmodule Math do
  def factorial(0), do: 1
  def factorial(n) when n > 0, do: n * factorial(n - 1)
end

result = Math.factorial(5)  # 120
```

**After (Haskell):**
```haskell
module Math where

factorial :: Int -> Int
factorial 0 = 1
factorial n | n > 0 = n * factorial (n - 1)

-- Usage
result = factorial 5  -- 120
```

### Example 2: Medium - Result Types and Error Handling

**Before (Elixir):**
```elixir
defmodule UserService do
  def create_user(email, age) do
    with {:ok, valid_email} <- validate_email(email),
         {:ok, valid_age} <- validate_age(age) do
      {:ok, %User{email: valid_email, age: valid_age}}
    end
  end

  defp validate_email(email) do
    if String.contains?(email, "@") do
      {:ok, email}
    else
      {:error, :invalid_email}
    end
  end

  defp validate_age(age) do
    if age >= 18 do
      {:ok, age}
    else
      {:error, :too_young}
    end
  end
end
```

**After (Haskell):**
```haskell
module UserService where

import Data.Text (Text)
import qualified Data.Text as T

data User = User
  { userEmail :: Text
  , userAge :: Int
  } deriving (Show)

data UserError
  = InvalidEmail
  | TooYoung
  deriving (Show)

createUser :: Text -> Int -> Either UserError User
createUser email age = do
  validEmail <- validateEmail email
  validAge <- validateAge age
  return $ User validEmail validAge

validateEmail :: Text -> Either UserError Text
validateEmail email
  | "@" `T.isInfixOf` email = Right email
  | otherwise = Left InvalidEmail

validateAge :: Int -> Either UserError Int
validateAge age
  | age >= 18 = Right age
  | otherwise = Left TooYoung
```

### Example 3: Complex - GenServer to STM with Concurrent Access

**Before (Elixir):**
```elixir
defmodule BankAccount do
  use GenServer

  # Client API
  def start_link(initial_balance) do
    GenServer.start_link(__MODULE__, initial_balance)
  end

  def deposit(pid, amount) do
    GenServer.call(pid, {:deposit, amount})
  end

  def withdraw(pid, amount) do
    GenServer.call(pid, {:withdraw, amount})
  end

  def balance(pid) do
    GenServer.call(pid, :balance)
  end

  # Server Callbacks
  def init(initial_balance), do: {:ok, initial_balance}

  def handle_call({:deposit, amount}, _from, balance) do
    new_balance = balance + amount
    {:reply, {:ok, new_balance}, new_balance}
  end

  def handle_call({:withdraw, amount}, _from, balance) do
    if balance >= amount do
      new_balance = balance - amount
      {:reply, {:ok, new_balance}, new_balance}
    else
      {:reply, {:error, :insufficient_funds}, balance}
    end
  end

  def handle_call(:balance, _from, balance) do
    {:reply, balance, balance}
  end
end

# Usage
{:ok, account} = BankAccount.start_link(1000)
{:ok, new_balance} = BankAccount.deposit(account, 500)
{:ok, after_withdrawal} = BankAccount.withdraw(account, 200)
balance = BankAccount.balance(account)
```

**After (Haskell):**
```haskell
module BankAccount where

import Control.Concurrent.STM
import Control.Monad (when)

type Balance = Int
type Account = TVar Balance

data BankError
  = InsufficientFunds
  deriving (Show, Eq)

createAccount :: Balance -> IO Account
createAccount initial = newTVarIO initial

deposit :: Account -> Balance -> IO Balance
deposit account amount = atomically $ do
  current <- readTVar account
  let newBalance = current + amount
  writeTVar account newBalance
  return newBalance

withdraw :: Account -> Balance -> IO (Either BankError Balance)
withdraw account amount = atomically $ do
  current <- readTVar account
  if current >= amount
    then do
      let newBalance = current - amount
      writeTVar account newBalance
      return $ Right newBalance
    else
      return $ Left InsufficientFunds

getBalance :: Account -> IO Balance
getBalance = readTVarIO

-- Atomic transfer between accounts
transfer :: Account -> Account -> Balance -> STM (Either BankError ())
transfer from to amount = do
  fromBalance <- readTVar from
  if fromBalance >= amount
    then do
      modifyTVar from (subtract amount)
      modifyTVar to (+ amount)
      return $ Right ()
    else
      return $ Left InsufficientFunds

-- Usage
main :: IO ()
main = do
  account <- createAccount 1000
  newBalance <- deposit account 500
  withdrawResult <- withdraw account 200
  balance <- getBalance account

  print balance  -- 1300

  -- Multiple accounts with atomic transfer
  account1 <- createAccount 1000
  account2 <- createAccount 0
  result <- atomically $ transfer account1 account2 500
  case result of
    Right _ -> putStrLn "Transfer successful"
    Left InsufficientFunds -> putStrLn "Insufficient funds"
```

---

## See Also

For more examples and patterns, see:
- `meta-convert-dev` - Foundational patterns with cross-language examples
- `convert-clojure-haskell` - Similar dynamic→static, practical→pure transition
- `convert-erlang-haskell` - BEAM→native, actors→STM
- `lang-elixir-dev` - Elixir development patterns
- `lang-haskell-dev` - Haskell development patterns

Cross-cutting pattern skills:
- `patterns-concurrency-dev` - Actors, STM, async patterns across languages
- `patterns-serialization-dev` - JSON, validation across languages
- `patterns-metaprogramming-dev` - Macros (Elixir) vs Template Haskell
