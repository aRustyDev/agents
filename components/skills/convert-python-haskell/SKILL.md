---
name: convert-python-haskell
description: Convert Python code to idiomatic Haskell. Use when migrating Python projects to Haskell, translating Python patterns to idiomatic Haskell, or refactoring Python codebases for type safety, pure functional programming, and advanced type system features. Extends meta-convert-dev with Python-to-Haskell specific patterns.
---

# Convert Python to Haskell

Convert Python code to idiomatic Haskell. This skill extends `meta-convert-dev` with Python-to-Haskell specific type mappings, idiom translations, and tooling for transforming imperative, dynamically-typed Python code into pure functional, statically-typed Haskell with advanced type system features.

## This Skill Extends

- `meta-convert-dev` - Foundational conversion patterns (APTV workflow, testing strategies)

For general concepts like the Analyze → Plan → Transform → Validate workflow, testing strategies, and common pitfalls, see the meta-skill first.

## This Skill Adds

- **Type mappings**: Python types → Haskell types (dynamic → static with type inference)
- **Idiom translations**: Python patterns → idiomatic Haskell (imperative → pure functional)
- **Module system**: Python packages → Haskell modules with explicit exports
- **Error handling**: try/except → Maybe/Either monads with do-notation
- **Concurrency**: threading/asyncio → async, STM, par monad, forkIO
- **Metaprogramming**: decorators → Template Haskell, deriving strategies
- **Zero/Default**: None/defaults → Maybe, Default typeclass, smart constructors
- **Serialization**: Pydantic → Aeson with FromJSON/ToJSON, Generic deriving
- **Build/Deps**: pip/poetry → cabal, stack, hpack
- **Testing**: pytest → HSpec, QuickCheck, doctest-haskell
- **Dev Workflow**: Python REPL → GHCi with :reload, :type, :kind
- **FFI**: C extensions → Haskell FFI, inline-c, hsc2hs

## This Skill Does NOT Cover

- General conversion methodology - see `meta-convert-dev`
- Python language fundamentals - see `lang-python-dev`
- Haskell language fundamentals - see `lang-haskell-dev`
- Reverse conversion (Haskell → Python) - see `convert-haskell-python`
- Web frameworks - Django/Flask → Servant/Yesod (see framework-specific guides)

---

## Paradigm Shift Overview

Converting from Python to Haskell requires a fundamental shift in thinking:

| Python Paradigm | Haskell Paradigm | Impact |
|-----------------|------------------|--------|
| Imperative | Pure functional with effects in IO monad | All side effects explicit |
| Dynamic typing | Strong static typing with inference | Errors caught at compile time |
| Mutable state | Immutability, State monad, STRef | No accidental mutation |
| OOP (classes) | Typeclasses, data types, functions | Data and behavior separate |
| Exceptions | Maybe/Either monads | Errors as values |
| Duck typing | Polymorphism via typeclasses | Explicit interfaces |
| Arbitrary precision ints | Integer (unbounded) or Int (bounded) | Choose precision |
| Reference counting GC | Lazy evaluation + GC | Different performance characteristics |
| Runtime flexibility | Compile-time guarantees | Less flexibility, more safety |

**Key Insight**: Haskell forces you to make implicit Python behavior explicit. This initially feels verbose but provides powerful compile-time guarantees.

---

## Quick Reference

| Python | Haskell | Notes |
|--------|---------|-------|
| `int` | `Int`, `Integer` | Int is bounded, Integer is arbitrary precision |
| `float` | `Double`, `Float` | Double preferred |
| `bool` | `Bool` | Direct mapping |
| `str` | `String`, `Text` | String is [Char], Text is efficient |
| `bytes` | `ByteString` | `Data.ByteString` |
| `list[T]` | `[a]` | Linked list |
| `tuple` | `(a, b, ...)` | Fixed-size tuple |
| `dict[K, V]` | `Map k v` | `Data.Map` |
| `set[T]` | `Set a` | `Data.Set` |
| `None` | `Nothing` | From `Maybe a` |
| `Optional[T]` | `Maybe a` | Nullable types |
| `Union[T, U]` | `Either a b` or custom `data` | Tagged unions |
| `Callable[[Args], Ret]` | `(Args) -> Ret` | Function types |
| `async def` | `IO ()` or monadic actions | Side effects in IO monad |
| `@dataclass` | `data` with record syntax | Data types |
| `Exception` | `Either e a`, `ExceptT` | Errors as values |
| `class` | `data` + typeclass instances | Separate data and behavior |

## When Converting Code

1. **Analyze source thoroughly** - understand Python's implicit behavior
2. **Identify side effects** - everything impure goes in IO monad
3. **Map types first** - create comprehensive type table
4. **Embrace purity** - separate pure logic from effects
5. **Use type inference** - let Haskell deduce types where possible
6. **Leverage typeclasses** - replace duck typing with explicit constraints
7. **Handle laziness** - understand evaluation differences
8. **Test equivalence** - QuickCheck for property-based testing

---

## Type System Mapping

### Primitive Types

| Python | Haskell | Notes |
|--------|---------|-------|
| `int` | `Int` | Fixed-size (usually 64-bit), can overflow |
| `int` | `Integer` | **Python default** - arbitrary precision, no overflow |
| `float` | `Double` | IEEE 754 double precision (preferred) |
| `float` | `Float` | Single precision (rarely used) |
| `bool` | `Bool` | `True`, `False` |
| `str` | `String` | List of `Char` - inefficient for large text |
| `str` | `Text` | **Preferred** - efficient Unicode text from `Data.Text` |
| `bytes` | `ByteString` | Efficient byte sequences from `Data.ByteString` |
| `None` | `Nothing` | Part of `Maybe a` type |
| `...` (Ellipsis) | - | No direct equivalent |

**Critical Note on Integers**: Python's `int` has **arbitrary precision** and never overflows. Haskell's `Int` is fixed-size (platform-dependent, usually 64-bit) and **can overflow**. Use `Integer` for Python-like behavior or validate ranges.

### Collection Types

| Python | Haskell | Notes |
|--------|---------|-------|
| `list[T]` | `[a]` | Linked list (prepend O(1), append O(n)) |
| `list[T]` | `Seq a` | Sequence from `Data.Sequence` (better performance) |
| `tuple` | `(a, b, ...)` | Fixed-size, immutable |
| `dict[K, V]` | `Map k v` | `Data.Map` - ordered map |
| `dict[K, V]` | `HashMap k v` | `Data.HashMap.Strict` - hash-based |
| `set[T]` | `Set a` | `Data.Set` - ordered set |
| `set[T]` | `HashSet a` | `Data.HashSet` - hash-based |
| `frozenset[T]` | `Set a` | Immutable by default |
| `collections.deque` | `Seq a` | `Data.Sequence` for double-ended queue |
| `collections.OrderedDict` | `Map k v` | `Data.Map` maintains insertion order conceptually |
| `collections.defaultdict` | `Map k v` with `findWithDefault` | Use smart constructors |
| `collections.Counter` | `Map a Int` | Count occurrences |

### Composite Types

| Python | Haskell | Notes |
|--------|---------|-------|
| `class` (data) | `data` with record syntax | Data containers |
| `class` (behavior) | `typeclass` | Behavior contracts |
| `@dataclass` | `data` with `deriving (Show, Eq, Generic)` | Auto-derive instances |
| `typing.Protocol` | `typeclass` | Structural → nominal typing |
| `typing.TypedDict` | `data` with record syntax | Named fields |
| `typing.NamedTuple` | `data` with positional/record | Prefer record syntax |
| `enum.Enum` | `data` (sum type) | Algebraic data types |
| `typing.Literal["a", "b"]` | `data` with constructors | Literal types |
| `typing.Union[T, U]` | `Either a b` or custom `data` | Tagged union |
| `typing.Optional[T]` | `Maybe a` | Nullable types |
| `typing.Callable[[Args], Ret]` | `(Args) -> Ret` | Function types |
| `typing.Generic[T]` | Polymorphic types | Generic types with type variables |

### Type Annotations → Type Signatures

| Python | Haskell | Notes |
|--------|---------|-------|
| `def f(x: T) -> T` | `f :: a -> a` | Polymorphic type variable |
| `def f(x: Iterable[T])` | `f :: [a] -> ...` or `Foldable t => t a -> ...` | Typeclass constraints |
| `x: Any` | **Avoid** - use type variables | `Any` defeats type safety |
| `x: object` | **Avoid** - use polymorphism | No universal base type |
| `TypeVar('T')` | Type variable `a`, `b`, etc. | Implicit in Haskell |

---

## Module System Translation

### Python Packages → Haskell Modules

**Python:**
```python
# myproject/utils/helpers.py
def greet(name: str) -> str:
    return f"Hello, {name}!"

def farewell(name: str) -> str:
    return f"Goodbye, {name}!"

# __init__.py exposes API
from .helpers import greet

# Usage in another file
from myproject.utils import greet
```

**Haskell:**
```haskell
-- MyProject/Utils/Helpers.hs
module MyProject.Utils.Helpers
    ( greet      -- Explicitly export greet
    , farewell   -- Explicitly export farewell
    ) where

greet :: String -> String
greet name = "Hello, " ++ name ++ "!"

farewell :: String -> String
farewell name = "Goodbye, " ++ name ++ "!"

-- MyProject/Utils.hs (re-exports selected functions)
module MyProject.Utils
    ( greet
    ) where

import MyProject.Utils.Helpers (greet, farewell)

-- Usage in another module
import MyProject.Utils (greet)
```

**Why this translation:**
- Python has implicit exports (everything is public); Haskell requires explicit export lists
- Haskell module names match file paths hierarchically
- No `__init__.py` equivalent - create a module that re-exports
- Haskell's import system is more granular (import specific functions, qualified imports)

### Import Patterns

| Python | Haskell | Notes |
|--------|---------|-------|
| `import module` | `import Module` | Import everything |
| `from module import func` | `import Module (func)` | Import specific |
| `from module import *` | `import Module` | **Discouraged** in Haskell |
| `import module as m` | `import qualified Module as M` | Qualified import |
| `from module import func as f` | `import Module (func)` then alias in code | No direct syntax |

**Haskell Import Best Practices:**
```haskell
-- Explicit import list (preferred)
import Data.Map (Map, empty, insert, lookup)

-- Qualified import for disambiguation
import qualified Data.Map as M
import qualified Data.Set as S

-- Import all but hide specific names
import Data.List hiding (head, tail)

-- Import type only (not constructors)
import Data.Map (Map)
```

---

## Idiom Translation (10 Pillars)

### Pillar 1: Module System & Imports

**Python:**
```python
# myapp/models/user.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    id: int
    name: str
    email: Optional[str] = None

def find_user(user_id: int, users: list[User]) -> Optional[User]:
    return next((u for u in users if u.id == user_id), None)
```

**Haskell:**
```haskell
-- MyApp/Models/User.hs
module MyApp.Models.User
    ( User(..)    -- Export type and all constructors
    , findUser
    ) where

import Data.Maybe (listToMaybe)

data User = User
    { userId :: Int
    , userName :: String
    , userEmail :: Maybe String
    } deriving (Show, Eq)

findUser :: Int -> [User] -> Maybe User
findUser uid = listToMaybe . filter (\u -> userId u == uid)
```

**Why this translation:**
- Python's `@dataclass` becomes `data` with record syntax
- Explicit exports make API boundaries clear
- `Optional[T]` directly maps to `Maybe a`
- Generator expression with `next()` becomes `filter` + `listToMaybe`

---

### Pillar 2: Error Handling (try/except → Maybe/Either)

**Python:**
```python
def parse_age(s: str) -> int:
    """Parse age from string, raising ValueError on invalid input."""
    age = int(s)
    if age < 0:
        raise ValueError("Age must be non-negative")
    return age

def safe_divide(a: float, b: float) -> float:
    if b == 0:
        raise ZeroDivisionError("Cannot divide by zero")
    return a / b

# Usage with try/except
try:
    age = parse_age("25")
    result = safe_divide(10, age)
    print(f"Result: {result}")
except ValueError as e:
    print(f"Value error: {e}")
except ZeroDivisionError as e:
    print(f"Division error: {e}")
```

**Haskell (Maybe):**
```haskell
import Text.Read (readMaybe)

parseAge :: String -> Maybe Int
parseAge s = do
    age <- readMaybe s
    if age >= 0
        then Just age
        else Nothing

safeDivide :: Double -> Double -> Maybe Double
safeDivide _ 0 = Nothing
safeDivide a b = Just (a / b)

-- Usage with do-notation
processAge :: String -> String
processAge input = case parseAge input of
    Nothing -> "Invalid age"
    Just age -> case safeDivide 10 (fromIntegral age) of
        Nothing -> "Cannot divide by zero"
        Just result -> "Result: " ++ show result

-- Or with monadic composition
processAge' :: String -> Maybe Double
processAge' input = do
    age <- parseAge input
    safeDivide 10 (fromIntegral age)
```

**Haskell (Either for detailed errors):**
```haskell
data ParseError = InvalidFormat String | NegativeAge Int
    deriving (Show, Eq)

parseAge :: String -> Either ParseError Int
parseAge s = case readMaybe s of
    Nothing -> Left (InvalidFormat s)
    Just age -> if age >= 0
        then Right age
        else Left (NegativeAge age)

safeDivide :: Double -> Double -> Either String Double
safeDivide _ 0 = Left "Cannot divide by zero"
safeDivide a b = Right (a / b)

-- ExceptT monad transformer for combining error types
import Control.Monad.Except

processAge :: String -> ExceptT String IO ()
processAge input = do
    age <- case parseAge input of
        Left (InvalidFormat s) -> throwError $ "Invalid format: " ++ s
        Left (NegativeAge a) -> throwError $ "Negative age: " ++ show a
        Right a -> return a
    result <- case safeDivide 10 (fromIntegral age) of
        Left err -> throwError err
        Right r -> return r
    liftIO $ putStrLn $ "Result: " ++ show result
```

**Why this translation:**
- Python exceptions become values: `Maybe` for simple success/failure, `Either` for detailed errors
- `do-notation` provides imperative-style sequencing for monadic operations
- Pattern matching replaces try/except blocks
- Error information is preserved in the type system (compile-time checking)

---

### Pillar 3: Concurrency (threading/asyncio → async/STM/par)

**Python (threading):**
```python
import threading
import time
from queue import Queue

def worker(q: Queue, results: list):
    while True:
        item = q.get()
        if item is None:
            break
        # Simulate work
        time.sleep(0.1)
        results.append(item * 2)
        q.task_done()

# Multi-threaded processing
queue = Queue()
results = []
threads = []

for i in range(4):
    t = threading.Thread(target=worker, args=(queue, results))
    t.start()
    threads.append(t)

for item in range(10):
    queue.put(item)

queue.join()

for _ in range(4):
    queue.put(None)

for t in threads:
    t.join()

print(results)
```

**Haskell (forkIO + TVar):**
```haskell
import Control.Concurrent (forkIO, threadDelay)
import Control.Concurrent.STM
import Control.Monad (replicateM_, forM_)

worker :: TQueue Int -> TVar [Int] -> IO ()
worker queue resultsVar = loop
  where
    loop = do
        maybeItem <- atomically $ do
            empty <- isEmptyTQueue queue
            if empty
                then return Nothing
                else Just <$> readTQueue queue
        case maybeItem of
            Nothing -> return ()  -- Queue empty, exit
            Just item -> do
                threadDelay 100000  -- 0.1 seconds
                atomically $ modifyTVar' resultsVar (++ [item * 2])
                loop

main :: IO ()
main = do
    queue <- newTQueueIO
    resultsVar <- newTVarIO []

    -- Spawn 4 worker threads
    workers <- replicateM 4 $ forkIO (worker queue resultsVar)

    -- Enqueue items
    forM_ [0..9] $ \item ->
        atomically $ writeTQueue queue item

    -- Wait for queue to drain (simplified)
    threadDelay 2000000  -- 2 seconds

    results <- readTVarIO resultsVar
    print results
```

**Python (asyncio):**
```python
import asyncio

async def fetch_data(url: str) -> str:
    """Simulate async HTTP request."""
    await asyncio.sleep(0.1)
    return f"Data from {url}"

async def main():
    urls = [f"http://example.com/{i}" for i in range(10)]

    # Concurrent execution
    results = await asyncio.gather(*[fetch_data(url) for url in urls])

    for result in results:
        print(result)

asyncio.run(main())
```

**Haskell (async library):**
```haskell
import Control.Concurrent.Async
import Control.Monad (forM)

fetchData :: String -> IO String
fetchData url = do
    threadDelay 100000  -- 0.1 seconds
    return $ "Data from " ++ url

main :: IO ()
main = do
    let urls = ["http://example.com/" ++ show i | i <- [0..9]]

    -- Concurrent execution with async
    results <- mapConcurrently fetchData urls

    mapM_ putStrLn results

-- Or using async/wait manually
mainManual :: IO ()
mainManual = do
    let urls = ["http://example.com/" ++ show i | i <- [0..9]]

    -- Fork all tasks
    asyncs <- mapM (async . fetchData) urls

    -- Wait for all results
    results <- mapM wait asyncs

    mapM_ putStrLn results
```

**Haskell (STM for shared state):**
```haskell
import Control.Concurrent.STM
import Control.Concurrent (forkIO)
import Control.Monad (replicateM_)

-- Shared counter with STM
incrementCounter :: TVar Int -> Int -> IO ()
incrementCounter counter times = replicateM_ times $ atomically $ do
    current <- readTVar counter
    writeTVar counter (current + 1)

main :: IO ()
main = do
    counter <- newTVarIO 0

    -- 10 threads each incrementing 1000 times
    replicateM_ 10 $ forkIO (incrementCounter counter 1000)

    -- Wait and read final value
    threadDelay 1000000  -- 1 second
    finalValue <- readTVarIO counter
    print finalValue  -- Should be 10000
```

**Why this translation:**
- Python's `threading.Thread` → Haskell's `forkIO` (lightweight threads)
- Python's `Queue` → Haskell's `TQueue` (STM-based, composable)
- Python's `asyncio.gather` → Haskell's `mapConcurrently` from `async` library
- STM (Software Transactional Memory) provides composable, atomic state changes (superior to locks)
- Haskell's green threads are cheap (can spawn millions)

---

### Pillar 4: Metaprogramming (decorators → Template Haskell/deriving)

**Python (decorators):**
```python
from functools import wraps
import time

def timer(func):
    """Decorator to time function execution."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} took {end - start:.4f}s")
        return result
    return wrapper

def memoize(func):
    """Decorator for memoization."""
    cache = {}
    @wraps(func)
    def wrapper(*args):
        if args not in cache:
            cache[args] = func(*args)
        return cache[args]
    return wrapper

@timer
@memoize
def fibonacci(n: int) -> int:
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

# Class decorators
from dataclasses import dataclass

@dataclass
class Point:
    x: float
    y: float
```

**Haskell (deriving strategies):**
```haskell
{-# LANGUAGE DeriveGeneric #-}
{-# LANGUAGE DeriveAnyClass #-}
{-# LANGUAGE DerivingStrategies #-}

import GHC.Generics (Generic)
import Data.Aeson (FromJSON, ToJSON)

-- Deriving common typeclasses
data Point = Point
    { x :: Double
    , y :: Double
    } deriving stock (Show, Eq, Generic)
      deriving anyclass (FromJSON, ToJSON)

-- Multiple deriving strategies
newtype UserId = UserId Int
    deriving stock (Show, Eq, Ord)
    deriving newtype (Num, Enum)
```

**Haskell (Template Haskell for code generation):**
```haskell
{-# LANGUAGE TemplateHaskell #-}

import Language.Haskell.TH

-- Generate lenses (getter/setters) for record fields
import Control.Lens (makeLenses)

data User = User
    { _userId :: Int
    , _userName :: String
    , _userEmail :: Maybe String
    } deriving (Show, Eq)

makeLenses ''User  -- Generates lenses: userId, userName, userEmail
```

**Haskell (manual memoization - no decorator syntax):**
```haskell
import Data.Function.Memoize (memoize)

-- Memoized fibonacci
fibMemo :: Int -> Integer
fibMemo = memoize fib
  where
    fib 0 = 0
    fib 1 = 1
    fib n = fibMemo (n - 1) + fibMemo (n - 2)

-- Manual timing wrapper (no decorator syntax)
timed :: IO a -> IO a
timed action = do
    start <- getCurrentTime
    result <- action
    end <- getCurrentTime
    putStrLn $ "Took: " ++ show (diffUTCTime end start)
    return result

import Data.Time.Clock

-- Usage
main :: IO ()
main = timed $ do
    print $ fibMemo 30
```

**Why this translation:**
- Python decorators → Haskell deriving strategies for common patterns
- `@dataclass` → `data` with `deriving (Show, Eq, Generic)`
- Template Haskell for compile-time code generation (e.g., lenses, JSON instances)
- No decorator syntax for functions - use higher-order functions explicitly
- Memoization via libraries or manual cache management

---

### Pillar 5: Zero/Default Values (None → Maybe, Default typeclass)

**Python (None and default arguments):**
```python
from typing import Optional

def greet(name: Optional[str] = None) -> str:
    """Greet user with optional name."""
    if name is None:
        name = "Guest"
    return f"Hello, {name}!"

def get_config(key: str, default: int = 0) -> int:
    """Get config value with default."""
    config = {"timeout": 30, "retries": 3}
    return config.get(key, default)

# None as sentinel value
def process_data(data: Optional[list[int]] = None) -> list[int]:
    if data is None:
        data = []
    return [x * 2 for x in data]
```

**Haskell (Maybe):**
```haskell
import Data.Maybe (fromMaybe)

greet :: Maybe String -> String
greet maybeName = "Hello, " ++ name ++ "!"
  where
    name = fromMaybe "Guest" maybeName

-- Or with pattern matching
greet' :: Maybe String -> String
greet' Nothing = "Hello, Guest!"
greet' (Just name) = "Hello, " ++ name ++ "!"
```

**Haskell (Default typeclass):**
```haskell
import Data.Default (Default(..))
import qualified Data.Map as M

data Config = Config
    { timeout :: Int
    , retries :: Int
    , maxSize :: Int
    } deriving (Show)

instance Default Config where
    def = Config
        { timeout = 30
        , retries = 3
        , maxSize = 1024
        }

getConfig :: String -> M.Map String Int -> Int
getConfig key configMap = M.findWithDefault 0 key configMap

-- Usage
main :: IO ()
main = do
    let config = def :: Config
    print config  -- Uses default values
```

**Haskell (smart constructors):**
```haskell
-- Smart constructor with defaults
data User = User
    { userName :: String
    , userAge :: Int
    , userRole :: Role
    } deriving (Show)

data Role = Admin | User | Guest
    deriving (Show)

-- Smart constructor
makeUser :: String -> User
makeUser name = User
    { userName = name
    , userAge = 0       -- Default age
    , userRole = Guest  -- Default role
    }

-- Builder pattern for optional fields
data UserBuilder = UserBuilder
    { builderName :: Maybe String
    , builderAge :: Maybe Int
    , builderRole :: Maybe Role
    }

emptyBuilder :: UserBuilder
emptyBuilder = UserBuilder Nothing Nothing Nothing

withName :: String -> UserBuilder -> UserBuilder
withName n builder = builder { builderName = Just n }

withAge :: Int -> UserBuilder -> UserBuilder
withAge a builder = builder { builderAge = Just a }

build :: UserBuilder -> Maybe User
build (UserBuilder (Just name) maybeAge maybeRole) =
    Just $ User name (fromMaybe 0 maybeAge) (fromMaybe Guest maybeRole)
build _ = Nothing
```

**Why this translation:**
- Python's `None` → Haskell's `Nothing` (explicit in type signature)
- Default arguments → smart constructors or `Default` typeclass
- `Maybe` makes nullable values explicit in type system
- Builder pattern for complex defaults

---

### Pillar 6: Serialization (Pydantic → Aeson)

**Python (Pydantic):**
```python
from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional
from datetime import datetime

class User(BaseModel):
    id: int = Field(alias='user_id')
    name: str = Field(min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    age: int = Field(ge=0, le=150)
    created_at: datetime

    @field_validator('name')
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('name cannot be empty')
        return v

# Usage
import json

user_json = '{"user_id": 1, "name": "Alice", "email": "alice@example.com", "age": 30, "created_at": "2024-01-01T00:00:00"}'
user = User.model_validate_json(user_json)
print(user)
```

**Haskell (Aeson with Generic deriving):**
```haskell
{-# LANGUAGE DeriveGeneric #-}
{-# LANGUAGE DeriveAnyClass #-}
{-# LANGUAGE OverloadedStrings #-}

import Data.Aeson
import Data.Time (UTCTime)
import GHC.Generics (Generic)
import Data.Text (Text)
import qualified Data.Text as T

data User = User
    { userId :: Int
    , userName :: Text
    , userEmail :: Maybe Text
    , userAge :: Int
    , userCreatedAt :: UTCTime
    } deriving (Show, Generic)

-- Custom Aeson instances with field name mapping
instance FromJSON User where
    parseJSON = withObject "User" $ \v -> User
        <$> v .: "user_id"
        <*> v .: "name"
        <*> v .:? "email"
        <*> v .: "age"
        <*> v .: "created_at"

instance ToJSON User where
    toJSON (User uid name email age created) = object
        [ "user_id" .= uid
        , "name" .= name
        , "email" .= email
        , "age" .= age
        , "created_at" .= created
        ]

-- Validation
validateUser :: User -> Either String User
validateUser user
    | userAge user < 0 || userAge user > 150 =
        Left "Age must be between 0 and 150"
    | T.null (T.strip (userName user)) =
        Left "Name cannot be empty"
    | otherwise =
        Right user

-- Usage
import Data.Aeson (decode, encode)
import qualified Data.ByteString.Lazy as B

parseUser :: B.ByteString -> Either String User
parseUser json = do
    user <- maybe (Left "Invalid JSON") Right (decode json)
    validateUser user
```

**Haskell (Generic deriving for simple cases):**
```haskell
{-# LANGUAGE DeriveGeneric #-}
{-# LANGUAGE DeriveAnyClass #-}

import Data.Aeson (FromJSON, ToJSON)
import GHC.Generics (Generic)

-- Automatic JSON instances
data Point = Point
    { x :: Double
    , y :: Double
    } deriving (Show, Generic, FromJSON, ToJSON)

-- Custom field naming strategy
import Data.Aeson.TH (deriveJSON, defaultOptions, fieldLabelModifier)
import Data.Char (toLower)

data Config = Config
    { configTimeout :: Int
    , configRetries :: Int
    } deriving (Show, Generic)

-- Drop "config" prefix and lowercase
$(deriveJSON defaultOptions{fieldLabelModifier = \s -> map toLower (drop 6 s)} ''Config)
```

**Why this translation:**
- Pydantic's `BaseModel` → Haskell's `data` + `FromJSON`/`ToJSON` instances
- Field aliases handled in custom JSON instances
- Validation separate from parsing (parse then validate)
- Generic deriving reduces boilerplate for simple cases
- Template Haskell for automatic instance generation with naming strategies

---

### Pillar 7: Build System & Dependencies (pip/poetry → cabal/stack)

**Python (pip/poetry):**
```python
# pyproject.toml (Poetry)
[tool.poetry]
name = "myproject"
version = "0.1.0"
description = "My Python project"

[tool.poetry.dependencies]
python = "^3.11"
requests = "^2.31.0"
pydantic = "^2.0.0"
aiohttp = "^3.9.0"

[tool.poetry.dev-dependencies]
pytest = "^7.4.0"
mypy = "^1.5.0"
black = "^23.0.0"

# requirements.txt (pip)
requests==2.31.0
pydantic==2.0.0
aiohttp==3.9.0
```

**Haskell (Cabal):**
```haskell
-- myproject.cabal
cabal-version:      3.0
name:               myproject
version:            0.1.0.0
synopsis:           My Haskell project
build-type:         Simple

library
    exposed-modules:  MyProject.Core
                    , MyProject.Utils
    build-depends:    base >=4.16
                    , text >=2.0
                    , aeson >=2.1
                    , http-client >=0.7
                    , http-client-tls >=0.3
    hs-source-dirs:   src
    default-language: GHC2021

executable myproject
    main-is:          Main.hs
    build-depends:    base
                    , myproject
    hs-source-dirs:   app
    default-language: GHC2021

test-suite myproject-test
    type:             exitcode-stdio-1.0
    main-is:          Spec.hs
    build-depends:    base
                    , myproject
                    , hspec >=2.10
                    , QuickCheck >=2.14
    hs-source-dirs:   test
    default-language: GHC2021
```

**Haskell (Stack + package.yaml - simplified):**
```yaml
# package.yaml (hpack format)
name: myproject
version: 0.1.0.0
synopsis: My Haskell project

dependencies:
  - base >= 4.16
  - text >= 2.0
  - aeson >= 2.1
  - http-client >= 0.7
  - http-client-tls >= 0.3

library:
  source-dirs: src
  exposed-modules:
    - MyProject.Core
    - MyProject.Utils

executables:
  myproject:
    main: Main.hs
    source-dirs: app
    dependencies:
      - myproject

tests:
  myproject-test:
    main: Spec.hs
    source-dirs: test
    dependencies:
      - myproject
      - hspec
      - QuickCheck
```

**Comparison:**

| Aspect | Python (pip/poetry) | Haskell (cabal/stack) |
|--------|---------------------|----------------------|
| Package definition | `pyproject.toml` or `setup.py` | `.cabal` file or `package.yaml` |
| Lock file | `poetry.lock` or `requirements.txt` | `cabal.project.freeze` or `stack.yaml.lock` |
| Install deps | `poetry install` or `pip install -r requirements.txt` | `cabal build` or `stack build` |
| Virtual env | `poetry shell` or `venv` | Not needed (isolated by default) |
| Version constraints | `^2.0.0` (caret), `~=2.0` (tilde) | `>=2.0 && <3.0` |
| Build tool | `poetry build` | `cabal build` or `stack build` |
| Publish | `poetry publish` | `cabal upload` |

**Why this translation:**
- Cabal is the build system, stack is a build tool wrapping Cabal
- `package.yaml` (hpack) generates `.cabal` files automatically
- Haskell projects are isolated by default (no need for virtual environments)
- Cabal supports multiple libraries/executables/test suites in one project
- Stack uses curated package sets (Stackage) for reproducible builds

---

### Pillar 8: Testing (pytest → HSpec/QuickCheck)

**Python (pytest):**
```python
import pytest
from myproject.utils import add, divide

def test_add():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
    assert add(0, 0) == 0

def test_divide():
    assert divide(10, 2) == 5
    with pytest.raises(ZeroDivisionError):
        divide(10, 0)

@pytest.mark.parametrize("a,b,expected", [
    (2, 3, 5),
    (-1, 1, 0),
    (0, 0, 0),
])
def test_add_parametrized(a, b, expected):
    assert add(a, b) == expected

# Fixtures
@pytest.fixture
def sample_data():
    return [1, 2, 3, 4, 5]

def test_sum_with_fixture(sample_data):
    assert sum(sample_data) == 15
```

**Haskell (HSpec):**
```haskell
-- test/Spec.hs
import Test.Hspec
import MyProject.Utils (add, safeDivide)

main :: IO ()
main = hspec $ do
    describe "add" $ do
        it "adds two positive numbers" $
            add 2 3 `shouldBe` 5

        it "adds negative and positive" $
            add (-1) 1 `shouldBe` 0

        it "adds zeros" $
            add 0 0 `shouldBe` 0

    describe "safeDivide" $ do
        it "divides two numbers" $
            safeDivide 10 2 `shouldBe` Just 5

        it "returns Nothing for division by zero" $
            safeDivide 10 0 `shouldBe` Nothing

        context "when using parametrized tests" $ do
            let testCases = [(2, 3, 5), (-1, 1, 0), (0, 0, 0)]
            mapM_ (\(a, b, expected) ->
                it ("adds " ++ show a ++ " and " ++ show b) $
                    add a b `shouldBe` expected
                ) testCases
```

**Haskell (QuickCheck - property-based testing):**
```haskell
import Test.QuickCheck

-- Properties for add
prop_add_commutative :: Int -> Int -> Bool
prop_add_commutative x y = add x y == add y x

prop_add_associative :: Int -> Int -> Int -> Bool
prop_add_associative x y z = add (add x y) z == add x (add y z)

prop_add_identity :: Int -> Bool
prop_add_identity x = add x 0 == x

-- Properties for safeDivide
prop_divide_multiply_inverse :: Double -> Double -> Property
prop_divide_multiply_inverse x y = y /= 0 ==> case safeDivide x y of
    Nothing -> False
    Just result -> abs (result * y - x) < 0.0001

-- Running QuickCheck tests
main :: IO ()
main = do
    quickCheck prop_add_commutative
    quickCheck prop_add_associative
    quickCheck prop_add_identity
    quickCheck prop_divide_multiply_inverse
```

**Haskell (HSpec + QuickCheck integration):**
```haskell
import Test.Hspec
import Test.QuickCheck

main :: IO ()
main = hspec $ do
    describe "add properties" $ do
        it "is commutative" $ property $
            \x y -> add x y == add (y :: Int) (x :: Int)

        it "has zero as identity" $ property $
            \x -> add x 0 == (x :: Int)

        it "is associative" $ property $
            \x y z -> add (add x y) z == add x (add (y :: Int) (z :: Int))
```

**Why this translation:**
- pytest assertions → HSpec `shouldBe`, `shouldSatisfy`, etc.
- pytest fixtures → HSpec `before` hooks or local definitions
- Parametrized tests → `mapM_` over test cases in HSpec
- QuickCheck adds property-based testing (generates random inputs)
- Properties express laws (commutativity, associativity, etc.)

---

### Pillar 9: Dev Workflow & REPL (Python REPL → GHCi)

**Python REPL:**
```python
$ python
>>> from myproject.utils import add, divide
>>> add(2, 3)
5
>>> divide(10, 2)
5.0
>>> # Reload module after changes
>>> import importlib
>>> import myproject.utils
>>> importlib.reload(myproject.utils)
>>> # Introspection
>>> help(add)
>>> type(add)
<class 'function'>
>>> add.__annotations__
{'a': <class 'int'>, 'b': <class 'int'>, 'return': <class 'int'>}
```

**Haskell GHCi:**
```haskell
$ stack ghci
ghci> :load MyProject.Utils
[1 of 1] Compiling MyProject.Utils
Ok, one module loaded.

ghci> add 2 3
5

ghci> safeDivide 10 2
Just 5.0

-- Type inspection
ghci> :type add
add :: Int -> Int -> Int

ghci> :info add
add :: Int -> Int -> Int
        -- Defined at src/MyProject/Utils.hs:10:1

-- Reload after code changes
ghci> :reload
Ok, one module loaded.

-- Kind inspection (type of types)
ghci> :kind Maybe
Maybe :: * -> *

ghci> :kind Int
Int :: *

-- Browse module exports
ghci> :browse MyProject.Utils
add :: Int -> Int -> Int
safeDivide :: Double -> Double -> Maybe Double

-- Set language extensions
ghci> :set -XOverloadedStrings

-- Multi-line input
ghci> :{
ghci| let factorial 0 = 1
ghci|     factorial n = n * factorial (n - 1)
ghci| :}

ghci> factorial 5
120

-- Debugging
ghci> :break MyProject.Utils.add
Breakpoint 0 activated at src/MyProject/Utils.hs:10:1-15

ghci> :trace add 2 3
Stopped in MyProject.Utils.add, src/MyProject/Utils.hs:10:1-15
_result :: Int = _
[src/MyProject/Utils.hs:10:1-15] ghci> :continue
5
```

**GHCi Commands:**

| Command | Purpose | Example |
|---------|---------|---------|
| `:load` / `:l` | Load module | `:load Main.hs` |
| `:reload` / `:r` | Reload after changes | `:reload` |
| `:type` / `:t` | Show type | `:type map` |
| `:kind` / `:k` | Show kind (type of type) | `:kind Maybe` |
| `:info` / `:i` | Show definition info | `:info Functor` |
| `:browse` / `:b` | List module exports | `:browse Data.List` |
| `:set` | Set options | `:set -XOverloadedStrings` |
| `:quit` / `:q` | Exit GHCi | `:quit` |
| `:{` / `:}` | Multi-line input | `:{...}` |
| `:break` | Set breakpoint | `:break MyModule.myFunc` |
| `:trace` | Trace execution | `:trace myFunc args` |

**Why this translation:**
- GHCi is more powerful for type exploration (`:type`, `:kind`, `:info`)
- `:reload` is faster than Python's `importlib.reload`
- Haskell's static types enable better IDE support (Haskell Language Server)
- GHCi supports debugging with breakpoints and tracing
- Multi-line input requires `:{` / `:}` delimiters

---

### Pillar 10: FFI & Interoperability (C extensions → Haskell FFI)

**Python (C extension via ctypes):**
```python
import ctypes

# Load shared library
libc = ctypes.CDLL("libc.so.6")

# Call C function
libc.printf(b"Hello from C: %d\n", 42)

# Wrapper for type safety
def c_strlen(s: bytes) -> int:
    libc.strlen.argtypes = [ctypes.c_char_p]
    libc.strlen.restype = ctypes.c_size_t
    return libc.strlen(s)

print(c_strlen(b"Hello"))  # 5
```

**Haskell (FFI):**
```haskell
{-# LANGUAGE ForeignFunctionInterface #-}

import Foreign.C.String (CString, withCString, peekCString)
import Foreign.C.Types (CInt(..), CSize(..))

-- Import C function
foreign import ccall "strlen"
    c_strlen :: CString -> IO CSize

-- Wrapper for convenience
strlen :: String -> IO Int
strlen s = withCString s $ \cstr -> do
    len <- c_strlen cstr
    return (fromIntegral len)

main :: IO ()
main = do
    len <- strlen "Hello"
    print len  -- 5

-- Import with unsafe (no callback to Haskell)
foreign import ccall unsafe "strlen"
    c_strlen_unsafe :: CString -> CSize

strlen_pure :: String -> Int
strlen_pure s = fromIntegral $ c_strlen_unsafe (error "null pointer")
```

**Haskell (inline-c for embedding C):**
```haskell
{-# LANGUAGE QuasiQuotes #-}
{-# LANGUAGE TemplateHaskell #-}

import qualified Language.C.Inline as C

C.include "<math.h>"

-- Inline C code
square :: Double -> IO Double
square x = [C.exp| double { pow($(double x), 2) } |]

main :: IO ()
main = do
    result <- square 5.0
    print result  -- 25.0
```

**Haskell (hsc2hs for C headers):**
```haskell
-- File: Time.hsc
{-# LANGUAGE ForeignFunctionInterface #-}

#include <time.h>

import Foreign.C.Types (CTime(..))

type TimeT = CTime

foreign import ccall "time"
    c_time :: Ptr TimeT -> IO TimeT

getCurrentTime :: IO TimeT
getCurrentTime = c_time nullPtr
```

**Comparison:**

| Aspect | Python (ctypes/cffi) | Haskell (FFI) |
|--------|----------------------|---------------|
| Declaration | Runtime (ctypes) | Compile-time (`foreign import`) |
| Type safety | Manual (`argtypes`, `restype`) | Automatic (type signature) |
| Performance | Moderate overhead | Near-zero overhead |
| Inline C | Limited (cffi) | Full support (inline-c, inline-c-cpp) |
| Header parsing | Manual | hsc2hs, c2hs tools |
| Callback support | Yes (`CFUNCTYPE`) | Yes (`foreign export`) |

**Why this translation:**
- Haskell FFI is compile-time checked (safer than ctypes)
- `inline-c` allows embedding C directly in Haskell code
- `hsc2hs` preprocessor extracts constants from C headers
- `foreign export` allows calling Haskell from C
- Performance is better due to compile-time integration

---

## Common Pitfalls

### 1. Forgetting About Laziness

**Problem:**
```haskell
-- Python: Eager evaluation
def process_data(items):
    results = [expensive_func(x) for x in items]
    print(f"Processed {len(results)} items")
    return results

-- Haskell: Lazy evaluation (different behavior!)
processData :: [Int] -> [Int]
processData items = results
  where
    results = map expensiveFunc items  -- NOT evaluated yet!
    -- length results would force evaluation
```

**Solution:**
```haskell
import Control.DeepSeq (force)

-- Force strict evaluation when needed
processData :: [Int] -> [Int]
processData items = force results
  where
    results = map expensiveFunc items

-- Or use strict versions
import qualified Data.Map.Strict as M
```

### 2. Confusion Between String and Text

**Problem:**
```haskell
-- String is [Char] - inefficient!
slowConcat :: String -> String -> String
slowConcat s1 s2 = s1 ++ s2  -- O(n) for each ++

-- Text is efficient
import Data.Text (Text)
import qualified Data.Text as T

fastConcat :: Text -> Text -> Text
fastConcat t1 t2 = t1 <> t2  -- Efficient
```

**Solution:**
```haskell
{-# LANGUAGE OverloadedStrings #-}

import Data.Text (Text)

-- Use Text for production code
processText :: Text -> Text
processText input = T.toUpper input
```

### 3. Not Using Explicit Type Signatures

**Problem:**
```haskell
-- Inferred type might be too general
add x y = x + y  -- Inferred: Num a => a -> a -> a

-- Might cause confusing errors later
result = add 1.5 (add 2 3)  -- Error: ambiguous type
```

**Solution:**
```haskell
-- Always add type signatures for top-level functions
add :: Int -> Int -> Int
add x y = x + y

addDouble :: Double -> Double -> Double
addDouble x y = x + y
```

### 4. Ignoring Functor/Applicative/Monad

**Problem:**
```haskell
-- Imperative style with explicit pattern matching (verbose)
getUserName :: Maybe User -> Maybe String
getUserName maybeUser = case maybeUser of
    Nothing -> Nothing
    Just user -> Just (userName user)
```

**Solution:**
```haskell
-- Use Functor (fmap / <$>)
getUserName :: Maybe User -> Maybe String
getUserName maybeUser = userName <$> maybeUser

-- Or even simpler with point-free style
getUserName :: Maybe User -> Maybe String
getUserName = fmap userName
```

### 5. Misunderstanding IO Monad

**Problem:**
```haskell
-- Trying to "escape" the IO monad
badGetLine :: String
badGetLine = getLine  -- ERROR: getLine :: IO String, not String
```

**Solution:**
```haskell
-- IO is contagious - functions using IO return IO
goodGetLine :: IO String
goodGetLine = getLine

processInput :: IO ()
processInput = do
    line <- getLine  -- Extract value inside IO context
    putStrLn $ "You said: " ++ line
```

### 6. Partial Functions

**Problem:**
```haskell
-- Partial functions can crash at runtime
headUnsafe :: [a] -> a
headUnsafe xs = head xs  -- Crashes on empty list!

result = headUnsafe []  -- Runtime error!
```

**Solution:**
```haskell
-- Use total functions (return Maybe)
headSafe :: [a] -> Maybe a
headSafe [] = Nothing
headSafe (x:_) = Just x

-- Or use Data.List.NonEmpty for non-empty lists
import qualified Data.List.NonEmpty as NE

headNonEmpty :: NE.NonEmpty a -> a
headNonEmpty = NE.head  -- Type system guarantees non-empty
```

### 7. Integer Overflow

**Problem:**
```haskell
-- Python: int has arbitrary precision
# x = 10 ** 100  # Works fine

-- Haskell: Int is bounded
badCompute :: Int
badCompute = 10 ^ 100  -- OVERFLOW! (wraps or crashes)
```

**Solution:**
```haskell
-- Use Integer for arbitrary precision
goodCompute :: Integer
goodCompute = 10 ^ 100  -- Works correctly

-- Or explicitly handle overflow
import Data.Int (Int64)
import GHC.Num.Integer (integerToInt)
```

### 8. Space Leaks from Lazy Evaluation

**Problem:**
```haskell
-- Lazy fold can build up large thunks
sumLazy :: [Integer] -> Integer
sumLazy = foldl (+) 0  -- Space leak! Builds up (+) thunks
```

**Solution:**
```haskell
import Data.List (foldl')

-- Use strict fold
sumStrict :: [Integer] -> Integer
sumStrict = foldl' (+) 0  -- Evaluates eagerly, no leak
```

---

## Tooling

### Code Translation Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| Manual translation | Full control | **Recommended** for production |
| No automatic Python→Haskell transpiler | - | Paradigm shift too large |

### Development Tools

| Python | Haskell | Purpose |
|--------|---------|---------|
| `python` | `ghci` | REPL |
| `mypy` | `ghc` (built-in) | Type checking |
| `pylint` / `flake8` | `hlint` | Linting |
| `black` | `fourmolu` / `ormolu` | Code formatting |
| `isort` | `stylish-haskell` | Import sorting |
| `pdb` | GHCi debugger | Debugging |
| `venv` | Not needed | Isolation built-in |

### Build Tools

| Python | Haskell | Purpose |
|--------|---------|---------|
| `pip` | `cabal` | Package manager |
| `poetry` | `stack` | Build tool + package manager |
| `setuptools` | `cabal` | Build configuration |
| `wheel` | - | Package format (not needed) |

### Testing Frameworks

| Python | Haskell | Purpose |
|--------|---------|---------|
| `pytest` | `hspec` | Unit testing |
| `hypothesis` | `quickcheck` | Property-based testing |
| `unittest.mock` | `hspec-mock` / `HMock` | Mocking |
| `pytest-benchmark` | `criterion` | Benchmarking |
| `coverage.py` | `hpc` | Code coverage |

### Common Library Equivalents

| Python | Haskell | Purpose |
|--------|---------|---------|
| `requests` | `http-client` / `http-conduit` | HTTP client |
| `aiohttp` | `http-client` (async via IO) | Async HTTP |
| `flask` / `django` | `servant` / `yesod` / `scotty` | Web frameworks |
| `pydantic` | `aeson` + validation | JSON + validation |
| `click` / `argparse` | `optparse-applicative` | CLI parsing |
| `logging` | `monad-logger` / `katip` | Logging |
| `datetime` | `time` | Date/time handling |
| `pathlib` | `filepath` | Path manipulation |
| `re` | `regex` | Regular expressions |
| `sqlite3` | `sqlite-simple` | SQLite |
| `sqlalchemy` | `persistent` / `beam` | ORM |
| `asyncio` | `async` / `stm` | Concurrency |

---

## Examples

### Example 1: Simple - List Processing

**Before (Python):**
```python
def process_numbers(numbers: list[int]) -> list[int]:
    """Filter even numbers, square them, and sum."""
    evens = [x for x in numbers if x % 2 == 0]
    squared = [x * x for x in evens]
    return sum(squared)

result = process_numbers([1, 2, 3, 4, 5, 6])
print(result)  # 56 (4 + 16 + 36)
```

**After (Haskell):**
```haskell
processNumbers :: [Int] -> Int
processNumbers numbers =
    sum $ map square $ filter even numbers
  where
    square x = x * x

-- Or with function composition
processNumbers' :: [Int] -> Int
processNumbers' = sum . map (^2) . filter even

-- Or with list comprehension (less idiomatic)
processNumbers'' :: [Int] -> Int
processNumbers'' numbers = sum [x^2 | x <- numbers, even x]

main :: IO ()
main = print $ processNumbers [1, 2, 3, 4, 5, 6]  -- 56
```

**Key changes:**
- List comprehension → `filter` + `map` (more functional)
- Function composition with `.` preferred
- Type signature required
- `sum` works directly on lists

---

### Example 2: Medium - JSON API Client

**Before (Python):**
```python
import requests
from typing import Optional
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str
    email: str

def fetch_user(user_id: int) -> Optional[User]:
    """Fetch user from API."""
    try:
        response = requests.get(f"https://api.example.com/users/{user_id}")
        response.raise_for_status()
        return User(**response.json())
    except requests.HTTPError as e:
        print(f"HTTP error: {e}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

# Usage
if user := fetch_user(123):
    print(f"User: {user.name}")
else:
    print("User not found")
```

**After (Haskell):**
```haskell
{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE DeriveGeneric #-}

import Network.HTTP.Simple
import Data.Aeson (FromJSON, decode)
import GHC.Generics (Generic)
import qualified Data.ByteString.Lazy as BL

data User = User
    { userId :: Int
    , userName :: String
    , userEmail :: String
    } deriving (Show, Generic, FromJSON)

fetchUser :: Int -> IO (Maybe User)
fetchUser userId = do
    let request = setRequestMethod "GET" $
                  setRequestHost "api.example.com" $
                  setRequestPath (fromString $ "/users/" ++ show userId) $
                  setRequestSecure True $
                  setRequestPort 443 $
                  defaultRequest

    response <- httpLBS request
    let body = getResponseBody response
    return $ decode body

-- Or with http-client-tls and aeson
import Network.HTTP.Client
import Network.HTTP.Client.TLS (newTlsManager)

fetchUser' :: Int -> IO (Either String User)
fetchUser' uid = do
    manager <- newTlsManager
    request <- parseRequest $ "https://api.example.com/users/" ++ show uid
    response <- httpLbs request manager
    case decode (responseBody response) of
        Nothing -> return $ Left "Failed to parse JSON"
        Just user -> return $ Right user

main :: IO ()
main = do
    maybeUser <- fetchUser 123
    case maybeUser of
        Nothing -> putStrLn "User not found"
        Just user -> putStrLn $ "User: " ++ userName user
```

**Key changes:**
- Pydantic → Aeson with `FromJSON` deriving
- `requests` → `http-simple` or `http-client`
- Exceptions → `Maybe` or `Either` for error handling
- JSON parsing is type-safe at compile time
- HTTP client requires explicit configuration

---

### Example 3: Complex - Concurrent Web Scraper

**Before (Python):**
```python
import asyncio
import aiohttp
from typing import List
from dataclasses import dataclass

@dataclass
class Article:
    title: str
    url: str

async def fetch_page(session: aiohttp.ClientSession, url: str) -> str:
    async with session.get(url) as response:
        return await response.text()

async def scrape_articles(urls: List[str]) -> List[Article]:
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_page(session, url) for url in urls]
        pages = await asyncio.gather(*tasks)

        articles = []
        for url, page in zip(urls, pages):
            # Simplified parsing
            title = page.split('<title>')[1].split('</title>')[0]
            articles.append(Article(title=title, url=url))

        return articles

# Usage
urls = [f"https://example.com/page{i}" for i in range(10)]
articles = asyncio.run(scrape_articles(urls))
for article in articles:
    print(f"{article.title}: {article.url}")
```

**After (Haskell):**
```haskell
{-# LANGUAGE OverloadedStrings #-}

import Network.HTTP.Simple
import Control.Concurrent.Async (mapConcurrently)
import Data.Text (Text)
import qualified Data.Text as T
import qualified Data.Text.Encoding as TE
import Text.HTML.TagSoup (parseTags, Tag(..))

data Article = Article
    { articleTitle :: Text
    , articleUrl :: Text
    } deriving (Show)

fetchPage :: String -> IO Text
fetchPage url = do
    request <- parseRequest url
    response <- httpBS request
    return $ TE.decodeUtf8 (getResponseBody response)

parseTitle :: Text -> Text
parseTitle html =
    case dropWhile (not . isTitle) tags of
        (TagOpen "title" _:TagText title:_) -> title
        _ -> "No title"
  where
    tags = parseTags html
    isTitle (TagOpen "title" _) = True
    isTitle _ = False

scrapeArticle :: String -> IO Article
scrapeArticle url = do
    page <- fetchPage url
    let title = parseTitle page
    return $ Article title (T.pack url)

scrapeArticles :: [String] -> IO [Article]
scrapeArticles urls = mapConcurrently scrapeArticle urls

main :: IO ()
main = do
    let urls = ["https://example.com/page" ++ show i | i <- [1..10]]
    articles <- scrapeArticles urls
    mapM_ (\article -> putStrLn $ T.unpack (articleTitle article) ++ ": " ++ T.unpack (articleUrl article)) articles
```

**Key changes:**
- `asyncio.gather` → `mapConcurrently` from `async` library
- `aiohttp.ClientSession` → `Network.HTTP.Simple` (stateless)
- HTML parsing with `tagsoup` library
- Concurrency via lightweight threads (forkIO under the hood)
- No need for async/await syntax (IO monad handles effects)

---

## See Also

For more patterns and examples, see:
- `meta-convert-dev` - Foundational conversion patterns (APTV workflow)
- `lang-python-dev` - Python development patterns
- `lang-haskell-dev` - Haskell development patterns
- `patterns-serialization-dev` - Cross-language serialization patterns
- `patterns-concurrency-dev` - Cross-language concurrency patterns
- `patterns-metaprogramming-dev` - Cross-language metaprogramming patterns
