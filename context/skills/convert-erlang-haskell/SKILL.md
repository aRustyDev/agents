---
name: convert-erlang-haskell
description: Translates Erlang concurrent functional code to Haskell pure functional code. Use when migrating BEAM-based systems, modernizing telecom infrastructure, or adopting stronger type systems. Extends meta-convert-dev with Erlang-to-Haskell specific patterns.
---

# Erlang ↔ Haskell Conversion

Bidirectional conversion between Erlang and Haskell. This skill extends `meta-convert-dev` with Erlang↔Haskell specific type mappings, idiom translations, and concurrency patterns for translating between these functional languages with fundamentally different type systems and runtime models.

## This Skill Extends

- `meta-convert-dev` - Foundational conversion patterns (APTV workflow, testing strategies)

For general concepts like the Analyze → Plan → Transform → Validate workflow, testing strategies, and common pitfalls, see the meta-skill first.

## This Skill Adds

- **Type mappings**: Erlang dynamic types → Haskell static types
- **Idiom translations**: Erlang patterns → idiomatic Haskell
- **Concurrency models**: OTP behaviors → STM/async patterns
- **Error handling**: let-it-crash → Maybe/Either types
- **Message passing**: Process mailboxes → Channels/TQueue
- **Supervision**: Supervisor trees → immortal/distributed-process

## This Skill Does NOT Cover

- General conversion methodology - see `meta-convert-dev`
- Erlang language fundamentals - see `lang-erlang-dev`
- Haskell language fundamentals - see `lang-haskell-dev`
- Elixir conversions - see `convert-elixir-haskell`

---

## Quick Reference

| Erlang | Haskell | Notes |
|--------|---------|-------|
| `atom()` | `Data.Text` or custom sum type | Atoms → Text or algebraic types |
| `integer()` | `Integer` or `Int` | Unbounded vs. bounded |
| `float()` | `Double` or `Float` | Precision choice |
| `binary()` | `ByteString` | `Data.ByteString.Strict` or `.Lazy` |
| `list()` | `[a]` | Homogeneous lists |
| `tuple()` | `(a, b, ...)` or custom product type | Fixed-size tuples or records |
| `map()` | `Map k v` | `Data.Map.Strict` |
| `pid()` | `ThreadId` or `Async a` | Process identifiers |
| `reference()` | `IORef` or `TVar` | Mutable references |
| `fun()` | `a -> b` | First-class functions |
| `ok \| {error, Reason}` | `Either Error a` or `Maybe a` | Error handling |

---

## Type System Mapping

### Primitives

| Erlang | Haskell | Example Conversion |
|--------|---------|-------------------|
| `42` | `42 :: Integer` | Integer literals |
| `3.14` | `3.14 :: Double` | Floating point |
| `true` | `True :: Bool` | Boolean |
| `undefined` | `Nothing :: Maybe a` | Absence of value |
| `<<"hello">>` | `"hello" :: ByteString` | Binary strings |
| `'atom'` | `"atom" :: Text` or `Atom` ADT | Symbolic constants |

### Collections

| Erlang | Haskell | Notes |
|--------|---------|-------|
| `[1, 2, 3]` | `[1, 2, 3] :: [Int]` | Linked lists |
| `{ok, Value}` | `Right Value :: Either Error a` | Success tuple |
| `#{key => value}` | `Map.fromList [(key, value)]` | Key-value maps |
| `[H\|T]` | `(h:t)` | List pattern matching |

### Composite Types

| Erlang | Haskell | Example |
|--------|---------|---------|
| `-record(user, {name, age}).` | `data User = User { userName :: Text, userAge :: Int }` | Records |
| `-type result() :: ok \| {error, term()}.` | `data Result = Ok \| Error String` | Sum types |
| `-spec add(integer(), integer()) -> integer().` | `add :: Int -> Int -> Int` | Function signatures |
| `-opaque handle().` | `newtype Handle = Handle Int` | Opaque types |

### Process Types

| Erlang Concept | Haskell Equivalent | Library |
|----------------|-------------------|---------|
| `pid()` | `Async a` | `async` package |
| `gen_server` | Custom type class + `TVar` | `stm`, `async` |
| `supervisor` | `Supervisor` | `immortal`, `distributed-process` |
| Message passing | `Chan`, `TQueue`, `STM` | `stm`, `unagi-chan` |

---

## Idiom Translation

### Pattern: Pattern Matching

**Erlang:**
```erlang
handle_result(ok) -> success;
handle_result({error, Reason}) -> {failure, Reason};
handle_result(Other) -> {unknown, Other}.
```

**Haskell:**
```haskell
data Result = Ok | Error String
data Response = Success | Failure String | Unknown String

handleResult :: Result -> Response
handleResult Ok = Success
handleResult (Error reason) = Failure reason
```

**Why this translation**: Haskell's pattern matching is structurally similar but requires explicit type constructors in algebraic data types.

---

### Pattern: Message Passing (gen_server)

**Erlang:**
```erlang
-module(counter).
-behaviour(gen_server).

handle_call(increment, _From, State) ->
    {reply, ok, State + 1};
handle_call(get, _From, State) ->
    {reply, State, State}.
```

**Haskell:**
```haskell
module Counter where

import Control.Concurrent.STM

data CounterMsg = Increment | Get (TMVar Int)

counter :: TVar Int -> CounterMsg -> STM ()
counter state Increment = modifyTVar' state (+1)
counter state (Get reply) = readTVar state >>= putTMVar reply
```

**Why this translation**: Haskell uses Software Transactional Memory (STM) instead of actor message passing. `TVar` provides lock-free mutable state.

---

### Pattern: Supervision Trees

**Erlang:**
```erlang
init([]) ->
    Children = [
        {worker1, {worker, start_link, []}, permanent, 5000, worker, [worker]}
    ],
    {ok, {{one_for_one, 5, 10}, Children}}.
```

**Haskell:**
```haskell
import Control.Immortal

runSupervised :: IO ()
runSupervised = do
    thread <- createWithLabel "worker1" $ \_ -> worker
    onUnexpectedFinish thread $ \_ -> print "Worker crashed, restarting"
```

**Why this translation**: `immortal` library provides automatic restart semantics. For full OTP-style supervision, use `distributed-process` or `cloud-haskell`.

---

### Pattern: Spawn and Message Send

**Erlang:**
```erlang
Pid = spawn(fun() -> loop() end),
Pid ! {hello, self()},
receive
    {reply, Msg} -> io:format("Got: ~p~n", [Msg])
end.
```

**Haskell:**
```haskell
import Control.Concurrent
import Control.Concurrent.Chan

spawnWorker :: IO ()
spawnWorker = do
    chan <- newChan
    replyChan <- newChan
    _ <- forkIO $ worker chan
    writeChan chan (Hello, replyChan)
    reply <- readChan replyChan
    putStrLn $ "Got: " ++ show reply
```

**Why this translation**: Haskell's `Chan` provides FIFO message queues. Use `async` for lightweight process management.

---

### Pattern: List Comprehensions

**Erlang:**
```erlang
Doubles = [X*2 || X <- [1,2,3,4], X rem 2 =:= 0].
```

**Haskell:**
```haskell
doubles :: [Int]
doubles = [x*2 | x <- [1,2,3,4], even x]
```

**Why this translation**: Syntax is nearly identical. Haskell's comprehensions support multiple generators and guards.

---

### Pattern: Error Handling

**Erlang:**
```erlang
case file:read_file("data.txt") of
    {ok, Data} -> process(Data);
    {error, Reason} -> handle_error(Reason)
end.
```

**Haskell:**
```haskell
import qualified Data.ByteString as BS
import Control.Exception

readAndProcess :: IO ()
readAndProcess = do
    result <- try (BS.readFile "data.txt") :: IO (Either IOError BS.ByteString)
    case result of
        Right dat -> process dat
        Left err -> handleError err
```

**Why this translation**: Haskell uses exception handling via `try`/`catch` or the `Either` monad. For pure code, prefer `ExceptT` transformer.

---

### Pattern: Higher-Order Functions

**Erlang:**
```erlang
lists:map(fun(X) -> X * 2 end, [1,2,3]).
lists:foldl(fun(X, Acc) -> X + Acc end, 0, [1,2,3]).
```

**Haskell:**
```haskell
map (*2) [1,2,3]
foldl (+) 0 [1,2,3]
```

**Why this translation**: Haskell's curried functions eliminate need for explicit lambdas. Point-free style is idiomatic.

---

### Pattern: Binary Pattern Matching

**Erlang:**
```erlang
<<Version:8, Type:8, Payload/binary>> = Packet.
```

**Haskell:**
```haskell
import qualified Data.Binary.Get as Get
import Data.ByteString.Lazy (ByteString)
import Data.Word (Word8)

parsePacket :: ByteString -> (Word8, Word8, ByteString)
parsePacket = Get.runGet $ do
    version <- Get.getWord8
    typ <- Get.getWord8
    payload <- Get.getRemainingLazyByteString
    return (version, typ, payload)
```

**Why this translation**: Haskell's `binary` package provides parsing combinators. `cereal` and `attoparsec` are alternatives.

---

### Pattern: Guards

**Erlang:**
```erlang
abs(X) when X < 0 -> -X;
abs(X) -> X.
```

**Haskell:**
```haskell
abs' :: (Ord a, Num a) => a -> a
abs' x | x < 0     = -x
       | otherwise = x
```

**Why this translation**: Syntax nearly identical. Haskell guards use `|` instead of `when`.

---

### Pattern: ETS Tables

**Erlang:**
```erlang
Table = ets:new(cache, [set, public]),
ets:insert(Table, {key, value}),
[{key, Value}] = ets:lookup(Table, key).
```

**Haskell:**
```haskell
import qualified Data.HashTable.IO as HT

type HashTable k v = HT.BasicHashTable k v

useCache :: IO ()
useCache = do
    table <- HT.new :: IO (HashTable String String)
    HT.insert table "key" "value"
    value <- HT.lookup table "key"
    print value
```

**Why this translation**: Mutable hash tables via `hashtables` package. For pure code, use `Data.Map`.

---

## Error Handling

### Philosophy Shift

**Erlang**: "Let it crash" - processes fail, supervisors restart them.
**Haskell**: "Make illegal states unrepresentable" - type system prevents errors at compile time.

### Practical Translation

**Erlang:**
```erlang
-spec divide(number(), number()) -> {ok, number()} | {error, divide_by_zero}.
divide(_, 0) -> {error, divide_by_zero};
divide(X, Y) -> {ok, X / Y}.
```

**Haskell:**
```haskell
data DivideError = DivideByZero

divide :: Double -> Double -> Either DivideError Double
divide _ 0 = Left DivideByZero
divide x y = Right (x / y)

-- Or using Maybe for simpler errors
divide' :: Double -> Double -> Maybe Double
divide' _ 0 = Nothing
divide' x y = Just (x / y)
```

### Exception Handling

**Erlang:**
```erlang
try
    risky_operation()
catch
    error:Reason -> {error, Reason}
end.
```

**Haskell:**
```haskell
import Control.Exception

safeRisky :: IO (Either SomeException Result)
safeRisky = try riskyOperation
```

---

## Concurrency Patterns

### 1. Lightweight Processes

**Erlang:**
```erlang
spawn(fun worker/0)
```

**Haskell:**
```haskell
import Control.Concurrent.Async

async worker  -- Returns Async a
```

**Pattern**: Use `async` for fire-and-forget, `race` for first-to-finish, `concurrently` for parallel composition.

---

### 2. Message Channels

**Erlang:**
```erlang
Pid ! Message,
receive Pattern -> handle(Pattern) end.
```

**Haskell:**
```haskell
import Control.Concurrent.Chan

writeChan chan message
msg <- readChan chan
```

**Alternatives**:
- `TQueue` (STM-based, composable)
- `unagi-chan` (high-performance bounded channels)

---

### 3. Select-Style Multiplexing

**Erlang:**
```erlang
receive
    {msg1, Data} -> handle_msg1(Data);
    {msg2, Data} -> handle_msg2(Data)
after 1000 ->
    timeout
end.
```

**Haskell:**
```haskell
import Control.Concurrent.STM

selectMessage :: TQueue Msg1 -> TQueue Msg2 -> IO Response
selectMessage q1 q2 = atomically $
    (handleMsg1 <$> readTQueue q1) `orElse`
    (handleMsg2 <$> readTQueue q2)
```

**Pattern**: `orElse` provides non-deterministic choice. For timeouts, use `registerDelay`.

---

### 4. GenServer Equivalent

**Erlang:**
```erlang
-module(kv_store).
-behaviour(gen_server).

-export([start_link/0, put/2, get/1]).
-export([init/1, handle_call/3, handle_cast/2]).

start_link() -> gen_server:start_link(?MODULE, [], []).
init([]) -> {ok, #{}}.

put(Pid, Key, Value) -> gen_server:cast(Pid, {put, Key, Value}).
get(Pid, Key) -> gen_server:call(Pid, {get, Key}).

handle_cast({put, Key, Value}, State) ->
    {noreply, State#{Key => Value}}.

handle_call({get, Key}, _From, State) ->
    {reply, maps:get(Key, State, undefined), State}.
```

**Haskell:**
```haskell
module KVStore where

import Control.Concurrent.STM
import qualified Data.Map.Strict as Map

data KVStore k v = KVStore (TVar (Map.Map k v))

newKVStore :: STM (KVStore k v)
newKVStore = KVStore <$> newTVar Map.empty

put :: Ord k => KVStore k v -> k -> v -> STM ()
put (KVStore store) key value = modifyTVar' store (Map.insert key value)

get :: Ord k => KVStore k v -> k -> STM (Maybe v)
get (KVStore store) key = Map.lookup key <$> readTVar store

-- Usage:
-- store <- atomically newKVStore
-- atomically $ put store "key" "value"
-- value <- atomically $ get store "key"
```

---

### 5. Distributed Computing

**Erlang:**
```erlang
{server, 'node@host'} ! Message.
```

**Haskell (Cloud Haskell):**
```haskell
import Control.Distributed.Process

send serverId message
```

**Libraries**:
- `distributed-process`: Erlang-style distributed computing
- `network-transport-tcp`: Network backend
- `cloud-haskell`: Full framework

---

## Memory & Ownership

### Garbage Collection

**Both Erlang and Haskell use GC**, but differently:

| Aspect | Erlang | Haskell |
|--------|--------|---------|
| **GC Strategy** | Per-process generational | Generational for whole heap |
| **Latency** | Microsecond pauses per process | Millisecond pauses (tunable) |
| **Memory Model** | Process-local heaps | Shared heap with immutability |
| **Tuning** | `spawn_opt` flags | GHC RTS options (`-H`, `-A`) |

### Mutable State

**Erlang:**
```erlang
% Processes hold mutable state via recursion
loop(State) ->
    receive
        {update, NewState} -> loop(NewState)
    end.
```

**Haskell:**
```haskell
-- Explicit mutability via IORef or TVar
import Data.IORef

updateState :: IORef Int -> IO ()
updateState ref = modifyIORef' ref (+1)
```

**Philosophy**: Haskell makes mutation explicit in types (`IO`, `STM`). Pure functions remain referentially transparent.

---

## Common Pitfalls

### 1. Forgetting Type Signatures

**Problem**: Haskell infers types, but polymorphism can cause ambiguity.

**Solution**: Always write top-level type signatures.

```haskell
-- Bad: Type defaulting may surprise you
divide x y = x / y

-- Good: Explicit constraints
divide :: Double -> Double -> Double
divide x y = x / y
```

---

### 2. Overusing Exceptions in Pure Code

**Problem**: `error`, `undefined` break referential transparency.

**Solution**: Use `Maybe`, `Either`, or `ExceptT`.

```haskell
-- Bad: Exception in pure code
head' [] = error "Empty list"

-- Good: Explicit failure
head' :: [a] -> Maybe a
head' [] = Nothing
head' (x:_) = Just x
```

---

### 3. Ignoring Laziness

**Problem**: Erlang is strict; Haskell is lazy. Space leaks possible.

**Solution**: Use strict data structures and functions when needed.

```haskell
import qualified Data.Map.Strict as Map  -- Not Data.Map
import Data.List (foldl')                -- Not foldl

sum' :: [Int] -> Int
sum' = foldl' (+) 0  -- Strict accumulator
```

---

### 4. Blocking in STM

**Problem**: `atomically` blocks can cause deadlocks if misused.

**Solution**: Keep STM transactions short and pure.

```haskell
-- Bad: IO inside STM (won't compile)
atomically $ do
    x <- readTVar var
    putStrLn "Debug"  -- ERROR!

-- Good: IO outside STM
x <- atomically $ readTVar var
putStrLn $ "Value: " ++ show x
```

---

### 5. Misunderstanding Monads

**Problem**: Treating `IO` like synchronous Erlang code.

**Solution**: Embrace do-notation and functors.

```haskell
-- Haskell idiomatic
contents <- readFile "file.txt"
process contents
```

---

### 6. Not Using Newtype

**Problem**: Primitive obsession (using `String`, `Int` everywhere).

**Solution**: Wrap primitives for type safety.

```haskell
-- Bad
type UserId = Int

-- Good
newtype UserId = UserId Int
```

---

### 7. Channel Deadlocks

**Problem**: Mixing `Chan` with synchronous expectations.

**Solution**: Use `async` for structured concurrency.

```haskell
-- Prefer this over manual channel management
result <- async computation
wait result
```

---

### 8. Forgetting Stack/Cabal Configuration

**Problem**: Erlang's rebar3 manages deps; Haskell needs explicit config.

**Solution**: Use Stack or Cabal with curated package sets (Stackage).

```yaml
# stack.yaml
resolver: lts-22.0
packages:
  - .
extra-deps: []
```

---

## Tooling

### Ecosystem Equivalents

| Erlang Tool | Haskell Equivalent | Purpose |
|-------------|-------------------|---------|
| `rebar3` | `stack` or `cabal` | Build system |
| `dialyzer` | `ghc -Wall -Werror` | Static analysis |
| `eunit` | `hspec` or `tasty` | Unit testing |
| `common_test` | `hspec` + `QuickCheck` | Property testing |
| `observer` | `threadscope`, `eventlog2html` | Profiling |
| `recon` | `ekg` | Runtime monitoring |
| `relx` | `docker` + static binaries | Release management |
| `hex` | `hackage` / `stackage` | Package registry |

### Development Workflow

```bash
# Erlang
rebar3 new app myapp
rebar3 compile
rebar3 shell

# Haskell
stack new myapp
stack build
stack ghci
```

---

## Migration Strategy

### Step 1: Identify OTP Boundaries
- Map `gen_server`, `gen_statem`, `supervisor` to Haskell equivalents
- Document message protocols

### Step 2: Translate Core Logic
- Start with pure functions (easiest to translate)
- Convert `-spec` to type signatures
- Port pattern matching and guards

### Step 3: Replace Concurrency Primitives
- `spawn` → `async`
- `receive` → `Chan` or `STM`
- Supervision → `immortal` or `distributed-process`

### Step 4: Handle Binary Protocols
- Use `binary`, `cereal`, or `attoparsec`
- Preserve wire format compatibility if needed

### Step 5: Testing
- Port EUnit tests to Hspec
- Use QuickCheck for property-based testing
- Add type-driven tests (e.g., `should-not-typecheck`)

### Step 6: Performance Tuning
- Profile with `+RTS -p`
- Use strict data structures
- Consider `deepseq` for forcing evaluation

### Step 7: Deployment
- Build static binaries with `stack --docker`
- Use multi-stage Docker builds
- Consider GHC runtime flags (`-N`, `-H`, `-A`)

---

## Examples

### Example 1: Simple HTTP Client

**Erlang:**
```erlang
-module(http_client).
-export([fetch/1]).

fetch(Url) ->
    inets:start(),
    case httpc:request(get, {Url, []}, [], []) of
        {ok, {{_, 200, _}, _, Body}} -> {ok, Body};
        {ok, {{_, Code, _}, _, _}} -> {error, Code};
        {error, Reason} -> {error, Reason}
    end.
```

**Haskell:**
```haskell
module HttpClient where

import Network.HTTP.Simple
import qualified Data.ByteString.Lazy.Char8 as L8

fetch :: String -> IO (Either String String)
fetch url = do
    response <- httpLBS (parseRequest_ url)
    let status = getResponseStatusCode response
    return $ if status == 200
        then Right (L8.unpack $ getResponseBody response)
        else Left ("HTTP " ++ show status)
```

---

### Example 2: Concurrent File Processing

**Erlang:**
```erlang
process_files(Files) ->
    Parent = self(),
    [spawn(fun() ->
        {ok, Data} = file:read_file(F),
        Parent ! {done, F, process(Data)}
     end) || F <- Files],
    collect(length(Files), []).

collect(0, Acc) -> Acc;
collect(N, Acc) ->
    receive {done, File, Result} -> collect(N-1, [{File, Result}|Acc]) end.
```

**Haskell:**
```haskell
import Control.Concurrent.Async
import qualified Data.ByteString as BS

processFiles :: [FilePath] -> IO [(FilePath, Result)]
processFiles files =
    forConcurrently files $ \file -> do
        dat <- BS.readFile file
        let result = process dat
        return (file, result)
```

---

### Example 3: GenServer-Style State Machine

**Erlang:**
```erlang
-module(door).
-behaviour(gen_statem).

locked(cast, {button, Code}, #{code := Code} = Data) ->
    {next_state, unlocked, Data};
locked(cast, {button, _}, Data) ->
    {keep_state, Data}.

unlocked(cast, lock, Data) ->
    {next_state, locked, Data}.
```

**Haskell:**
```haskell
{-# LANGUAGE LambdaCase #-}

module Door where

import Control.Concurrent.STM

data State = Locked | Unlocked
data Event = Button Int | Lock

doorFSM :: TVar State -> Int -> Event -> STM ()
doorFSM state correctCode = \case
    Button code | code == correctCode -> writeTVar state Unlocked
    Button _ -> return ()
    Lock -> writeTVar state Locked
```

---

## See Also

- `lang-erlang-dev`: Erlang development patterns and OTP design
- `lang-haskell-dev`: Haskell idioms, type-level programming, monad transformers
- `meta-convert-dev`: General principles for language translation
- `convert-elixir-haskell`: Similar conversion for Elixir (BEAM) to Haskell
