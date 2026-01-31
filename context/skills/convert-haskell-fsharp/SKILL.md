---
name: convert-haskell-fsharp
description: Convert Haskell code to idiomatic F#. Use when migrating Haskell projects to F#, translating Haskell patterns to idiomatic F#, or refactoring Haskell codebases. Extends meta-convert-dev with Haskell-to-F# specific patterns.
---

# Convert Haskell to F#

Convert Haskell code to idiomatic F#. This skill extends `meta-convert-dev` with Haskell-to-F# specific type mappings, idiom translations, and tooling.

## This Skill Extends

- `meta-convert-dev` - Foundational conversion patterns (APTV workflow, testing strategies)

For general concepts like the Analyze → Plan → Transform → Validate workflow, testing strategies, and common pitfalls, see the meta-skill first.

## This Skill Adds

- **Type mappings**: Haskell types → F# types
- **Idiom translations**: Haskell patterns → idiomatic F#
- **Error handling**: Haskell Maybe/Either → F# Option/Result
- **Type classes**: Haskell type classes → F# interfaces/traits
- **Evaluation**: Lazy evaluation → eager evaluation with seq
- **Ecosystem**: GHC/Cabal/Stack → .NET/NuGet/dotnet CLI

## This Skill Does NOT Cover

- General conversion methodology - see `meta-convert-dev`
- Haskell language fundamentals - see `lang-haskell-dev`
- F# language fundamentals - see `lang-fsharp-dev`
- Reverse conversion (F# → Haskell) - see `convert-fsharp-haskell`

---

## Quick Reference

| Haskell | F# | Notes |
|---------|-----|-------|
| `String` | `string` | Direct mapping |
| `Int` | `int` | 32-bit signed integer |
| `Integer` | `bigint` | Arbitrary precision |
| `Float`/`Double` | `float` | 64-bit floating point |
| `Bool` | `bool` | Direct mapping |
| `Char` | `char` | Direct mapping |
| `[a]` | `list<'a>` | Immutable linked list |
| `Maybe a` | `option<'a>` | Optional values |
| `Either a b` | `Result<'b,'a>` | Note: order swapped |
| `(a, b)` | `'a * 'b` | Tuple (different syntax) |
| `data X = ...` | `type X = ...` | Discriminated union |
| `type X = ...` | `type X = ...` | Type alias |
| `newtype X = ...` | `type X = X of ...` | Single-case union |
| `class C a where` | `type I = interface` | Type class → interface |
| `IO a` | `Async<'a>` or `Task<'a>` | Side effects |

## When Converting Code

1. **Analyze source thoroughly** before writing target
2. **Map types first** - create type equivalence table
3. **Handle laziness** - Haskell is lazy by default, F# is eager
4. **Adopt F# idioms** - don't write "Haskell code in F# syntax"
5. **Replace type classes** - use interfaces or module functions
6. **Handle edge cases** - pattern matching, infinite lists, laziness
7. **Test equivalence** - same inputs → same outputs

---

## Type System Mapping

### Primitive Types

| Haskell | F# | Notes |
|---------|-----|-------|
| `Int` | `int` | 32-bit signed integer |
| `Integer` | `bigint` | Arbitrary precision (System.Numerics.BigInteger) |
| `Float` | `float32` / `single` | 32-bit floating point |
| `Double` | `float` / `double` | 64-bit floating point (default) |
| `Bool` | `bool` | Direct mapping |
| `Char` | `char` | Unicode character |
| `String` | `string` | Unicode string |
| `()` | `unit` | Unit type |

### Collection Types

| Haskell | F# | Notes |
|---------|-----|-------|
| `[a]` | `'a list` | Immutable linked list |
| `[a]` (infinite) | `seq<'a>` | Use sequences for lazy evaluation |
| `(a, b)` | `'a * 'b` | Tuple (note: `*` syntax in types) |
| `(a, b, c)` | `'a * 'b * 'c` | Tuple with 3+ elements |
| `Map k v` | `Map<'k,'v>` | Immutable map |
| `Set a` | `Set<'a>` | Immutable set |
| `Array a` | `'a[]` or `array<'a>` | Mutable array |
| `Vector a` | `'a[]` | Arrays are more common in F# |

### Composite Types

| Haskell | F# | Notes |
|---------|-----|-------|
| `data X = C1 \| C2` | `type X = C1 \| C2` | Discriminated union |
| `data X = C a b` | `type X = C of 'a * 'b` | Union with data |
| `data X = C { f :: a }` | `type X = { F: 'a }` | Record type |
| `newtype X = X a` | `type X = X of 'a` | Single-case discriminated union |
| `type X = a` | `type X = 'a` | Type alias |

### Option and Result Types

| Haskell | F# | Notes |
|---------|-----|-------|
| `Maybe a` | `'a option` | Some/None instead of Just/Nothing |
| `Just x` | `Some x` | Present value |
| `Nothing` | `None` | Absent value |
| `Either a b` | `Result<'b,'a>` | **Note: parameter order is swapped!** |
| `Left err` | `Error err` | Error case |
| `Right val` | `Ok val` | Success case |

### Type Classes → Interfaces/Modules

| Haskell | F# | Strategy |
|---------|-----|----------|
| `class Eq a where` | `interface IEquatable<'a>` or `=` operator | Built-in equality |
| `class Ord a where` | `interface IComparable<'a>` or `compare` | Built-in comparison |
| `class Show a where` | Override `ToString()` or use `sprintf` | String representation |
| `class Functor f where` | Module with `map` function | No direct equivalent |
| `class Applicative f where` | Module with combinators | No direct equivalent |
| `class Monad m where` | Computation expressions | Use `let!` and `return` |

---

## Idiom Translation

### Pattern 1: Maybe/Either → Option/Result

**Haskell:**
```haskell
findUser :: String -> Maybe User
findUser userId = case lookup userId users of
    Just user -> Just user
    Nothing -> Nothing

validateAge :: Int -> Either String Int
validateAge age
    | age < 0 = Left "Age cannot be negative"
    | age > 150 = Left "Age too high"
    | otherwise = Right age
```

**F#:**
```fsharp
let findUser (userId: string) : User option =
    users |> Map.tryFind userId

let validateAge (age: int) : Result<int, string> =
    if age < 0 then
        Error "Age cannot be negative"
    elif age > 150 then
        Error "Age too high"
    else
        Ok age
```

**Why this translation:**
- F#'s `Option` maps directly to Haskell's `Maybe`
- F#'s `Result<'T,'Error>` maps to Haskell's `Either`, but **parameter order is swapped**
- F# uses `Some`/`None` instead of `Just`/`Nothing`
- F# uses `Ok`/`Error` instead of `Right`/`Left`
- Pattern matching syntax is similar but uses `match ... with`

### Pattern 2: List Comprehensions

**Haskell:**
```haskell
squares :: [Int]
squares = [x^2 | x <- [1..10]]

pythagoras :: [(Int, Int, Int)]
pythagoras = [(a,b,c) | a <- [1..20],
                        b <- [a..20],
                        c <- [b..20],
                        a^2 + b^2 == c^2]
```

**F#:**
```fsharp
let squares: int list =
    [ for x in 1..10 -> x * x ]

let pythagoras: (int * int * int) list =
    [ for a in 1..20 do
      for b in a..20 do
      for c in b..20 do
      if a*a + b*b = c*c then
        yield (a, b, c) ]
```

**Why this translation:**
- F# uses `[ for x in ... ]` instead of Haskell's `[ x | ... ]`
- F# uses `->` for simple projections, `yield` for conditional yields
- F# requires `do` for multiple generators
- F# uses `=` for equality instead of `==`

### Pattern 3: Higher-Order Functions

**Haskell:**
```haskell
result :: [Int] -> Int
result = sum . map (*2) . filter even

addThenDouble :: Int -> Int
addThenDouble = (*2) . (+1)
```

**F#:**
```fsharp
let result (xs: int list) : int =
    xs
    |> List.filter (fun x -> x % 2 = 0)
    |> List.map (fun x -> x * 2)
    |> List.sum

let addThenDouble: int -> int =
    (+) 1 >> (*) 2
```

**Why this translation:**
- F# uses `|>` (pipe forward) instead of `.` (compose)
- F# reads left-to-right with `|>`, Haskell reads right-to-left with `.`
- F# uses `>>` for function composition (same direction as Haskell's `.`)
- F# requires explicit lambda syntax `fun x -> ...` more often

### Pattern 4: Pattern Matching and Guards

**Haskell:**
```haskell
classify :: Int -> String
classify n
    | n < 0     = "negative"
    | n == 0    = "zero"
    | n < 10    = "small"
    | otherwise = "large"

describeList :: [a] -> String
describeList [] = "empty"
describeList [x] = "singleton"
describeList xs = "longer"
```

**F#:**
```fsharp
let classify (n: int) : string =
    match n with
    | n when n < 0 -> "negative"
    | 0 -> "zero"
    | n when n < 10 -> "small"
    | _ -> "large"

let describeList (xs: 'a list) : string =
    match xs with
    | [] -> "empty"
    | [x] -> "singleton"
    | _ -> "longer"
```

**Why this translation:**
- Haskell uses guards (`|`) in function definitions
- F# uses `match ... with` expression with `when` guards
- F# can match literals directly without guards
- Both support pattern matching on list structure

### Pattern 5: Recursive Functions

**Haskell:**
```haskell
factorial :: Integer -> Integer
factorial 0 = 1
factorial n = n * factorial (n - 1)

-- Tail-recursive
factorial' :: Integer -> Integer
factorial' n = go n 1
  where
    go 0 acc = acc
    go n acc = go (n - 1) (acc * n)
```

**F#:**
```fsharp
let rec factorial (n: bigint) : bigint =
    if n = 0I then 1I
    else n * factorial (n - 1I)

// Tail-recursive
let factorial' (n: bigint) : bigint =
    let rec loop n acc =
        if n = 0I then acc
        else loop (n - 1I) (acc * n)
    loop n 1I
```

**Why this translation:**
- F# requires explicit `rec` keyword for recursive functions
- F# uses `let ... in` for local definitions instead of `where`
- F# can use pattern matching in function parameters, but if/match is more common
- Tail recursion optimization works similarly in both languages

### Pattern 6: Typeclasses → Interfaces/Modules

**Haskell:**
```haskell
class Eq a where
    (==) :: a -> a -> Bool
    (/=) :: a -> a -> Bool

data Color = Red | Green | Blue

instance Eq Color where
    Red == Red = True
    Green == Green = True
    Blue == Blue = True
    _ == _ = False
    x /= y = not (x == y)
```

**F#:**
```fsharp
type Color =
    | Red
    | Green
    | Blue

// F# generates equality automatically for discriminated unions
// Manual implementation:
type Color with
    static member op_Equality(a: Color, b: Color) =
        match a, b with
        | Red, Red -> true
        | Green, Green -> true
        | Blue, Blue -> true
        | _ -> false

// Or use structural equality (automatic for DUs)
let color1 = Red
let color2 = Red
let isEqual = (color1 = color2)  // true
```

**Why this translation:**
- F# doesn't have type classes
- F# discriminated unions have automatic structural equality
- Custom equality requires overriding `Equals` or operator overloading
- For polymorphic behavior, use interfaces or module functions

### Pattern 7: Functors and Monads → Computation Expressions

**Haskell:**
```haskell
-- Functor usage
result = fmap (+1) (Just 5)  -- Just 6

-- Monad usage (do-notation)
process :: Maybe Int
process = do
    x <- Just 10
    y <- Just 20
    return (x + y)

-- Either monad
validate :: Either String Int
validate = do
    age <- validateAge 25
    score <- validateScore 85
    return (age + score)
```

**F#:**
```fsharp
// Functor-like usage
let result = Option.map (fun x -> x + 1) (Some 5)  // Some 6

// Computation expression (option)
let process: int option =
    option {
        let! x = Some 10
        let! y = Some 20
        return x + y
    }

// Result computation expression
let validate: Result<int, string> =
    result {
        let! age = validateAge 25
        let! score = validateScore 85
        return age + score
    }
```

**Why this translation:**
- F# computation expressions are similar to Haskell's do-notation
- `let!` in F# ≈ `<-` in Haskell
- `return` works the same way
- F# requires explicit computation expression builders (`option`, `result`, `async`)
- Some builders are built-in, others need to be defined or imported

### Pattern 8: Lazy Evaluation → Sequences

**Haskell:**
```haskell
-- Infinite list (lazy by default)
naturals :: [Integer]
naturals = [1..]

fibs :: [Integer]
fibs = 0 : 1 : zipWith (+) fibs (tail fibs)

takeFirst10 :: [Integer]
takeFirst10 = take 10 fibs
```

**F#:**
```fsharp
// Lazy sequence (must be explicit)
let naturals: seq<bigint> =
    Seq.initInfinite (fun i -> bigint i + 1I)

let fibs: seq<bigint> =
    (0I, 1I)
    |> Seq.unfold (fun (a, b) -> Some(a, (b, a + b)))

let takeFirst10: bigint list =
    fibs |> Seq.take 10 |> Seq.toList
```

**Why this translation:**
- Haskell lists are lazy by default
- F# lists are eager, sequences (`seq<'a>`) are lazy
- F# `Seq.unfold` replaces recursive definitions
- Must explicitly convert sequences to lists with `Seq.toList`
- F# doesn't support infinite lists natively, use sequences

### Pattern 9: Type Families → Generic Types

**Haskell:**
```haskell
class Container c where
    type Elem c :: *
    empty :: c
    insert :: Elem c -> c -> c

instance Container [a] where
    type Elem [a] = a
    empty = []
    insert = (:)
```

**F#:**
```fsharp
type IContainer<'c, 'elem> =
    abstract member Empty: 'c
    abstract member Insert: 'elem -> 'c -> 'c

type ListContainer<'a>() =
    interface IContainer<'a list, 'a> with
        member _.Empty = []
        member _.Insert elem container = elem :: container
```

**Why this translation:**
- Haskell type families → F# generic interfaces
- No direct equivalent to associated types
- Use explicit type parameters
- Requires more verbose interface definitions

### Pattern 10: Module System

**Haskell:**
```haskell
-- MyApp/User.hs
module MyApp.User
    ( User(..)
    , createUser
    , validateEmail
    ) where

import Data.Text (Text)
import qualified Data.Map as M

data User = User
    { name :: Text
    , email :: Text
    }

createUser :: Text -> Text -> User
createUser n e = User n e
```

**F#:**
```fsharp
// User.fs
module MyApp.User

type User = {
    Name: string
    Email: string
}

let createUser (name: string) (email: string) : User =
    { Name = name; Email = email }

let validateEmail (email: string) : bool =
    email.Contains("@")
```

**Why this translation:**
- F# modules are file-based (one module per file by default)
- F# uses `module Name` at top of file
- No explicit export list in F#; everything is public by default
- Use `internal` or `private` for visibility control
- F# records use `{ Field: Type }` syntax instead of Haskell's `{ field :: Type }`

---

## Error Handling

### Haskell Maybe/Either → F# Option/Result

Haskell uses `Maybe` for optional values and `Either` for computations that can fail. F# uses `Option` and `Result` respectively.

| Haskell | F# | Notes |
|---------|-----|-------|
| `Maybe a` | `'a option` | Optional values |
| `Just x` | `Some x` | Present value |
| `Nothing` | `None` | Absent value |
| `Either a b` | `Result<'b,'a>` | **Parameters swapped!** |
| `Left err` | `Error err` | Error case |
| `Right val` | `Ok val` | Success case |
| `fromMaybe` | `defaultArg` or `Option.defaultValue` | Provide default |
| `maybe` | `Option.fold` | Fold over option |

### Basic Error Translation

**Haskell:**
```haskell
safeDivide :: Double -> Double -> Maybe Double
safeDivide _ 0 = Nothing
safeDivide x y = Just (x / y)

parseAge :: String -> Either String Int
parseAge str =
    case reads str of
        [(n, "")] -> if n >= 0
                     then Right n
                     else Left "Age must be positive"
        _ -> Left "Not a valid number"
```

**F#:**
```fsharp
let safeDivide (x: float) (y: float) : float option =
    if y = 0.0 then None
    else Some (x / y)

let parseAge (str: string) : Result<int, string> =
    match System.Int32.TryParse(str) with
    | true, n when n >= 0 -> Ok n
    | true, _ -> Error "Age must be positive"
    | false, _ -> Error "Not a valid number"
```

### Chaining Operations

**Haskell:**
```haskell
-- Option chaining
getUserEmail :: UserId -> Maybe Email
getUserEmail userId = do
    user <- findUser userId
    return (email user)

-- Or with bind
getUserEmail' :: UserId -> Maybe Email
getUserEmail' userId =
    findUser userId >>= return . email

-- Either chaining
validateUser :: String -> String -> Either String User
validateUser ageStr emailStr = do
    age <- parseAge ageStr
    email <- validateEmail emailStr
    return $ User email age
```

**F#:**
```fsharp
// Option chaining with computation expression
let getUserEmail (userId: UserId) : Email option =
    option {
        let! user = findUser userId
        return user.Email
    }

// Or with bind
let getUserEmail' (userId: UserId) : Email option =
    findUser userId
    |> Option.map (fun user -> user.Email)

// Result chaining
let validateUser (ageStr: string) (emailStr: string) : Result<User, string> =
    result {
        let! age = parseAge ageStr
        let! email = validateEmail emailStr
        return { Email = email; Age = age }
    }
```

---

## Evaluation Strategy

### Lazy vs Eager Evaluation

Haskell is lazy by default, while F# is eager by default. This is one of the most significant differences.

| Haskell | F# | Strategy |
|---------|-----|----------|
| Lazy by default | Eager by default | Use `seq` for laziness |
| `[1..]` | `Seq.initInfinite` | Infinite sequences |
| `take 10 [1..]` | `Seq.take 10 (Seq.initInfinite id)` | Take from infinite |
| `let x = expr` | `let x = lazy expr` | Explicit lazy values |
| `x` | `x.Force()` | Force lazy evaluation |

### Converting Lazy Code

**Haskell:**
```haskell
-- Infinite list of fibonacci numbers
fibs :: [Integer]
fibs = 0 : 1 : zipWith (+) fibs (tail fibs)

-- Take first 10
first10 :: [Integer]
first10 = take 10 fibs

-- Infinite list of primes (conceptual)
primes :: [Integer]
primes = sieve [2..]
  where
    sieve (p:xs) = p : sieve [x | x <- xs, x `mod` p /= 0]
```

**F#:**
```fsharp
// Lazy sequence of fibonacci numbers
let fibs: seq<bigint> =
    (0I, 1I)
    |> Seq.unfold (fun (a, b) ->
        Some(a, (b, a + b)))

// Take first 10
let first10: bigint list =
    fibs |> Seq.take 10 |> Seq.toList

// Lazy sequence of primes
let primes: seq<bigint> =
    let rec sieve (nums: seq<bigint>) : seq<bigint> = seq {
        let p = Seq.head nums
        yield p
        yield! sieve (nums |> Seq.filter (fun x -> x % p <> 0I))
    }
    sieve (Seq.initInfinite (fun i -> bigint i + 2I))
```

### Explicit Lazy Values

**Haskell:**
```haskell
-- Everything is lazy
expensiveComputation :: Int
expensiveComputation = sum [1..1000000]

-- Used like any value
result :: Int
result = if condition then expensiveComputation else 0
```

**F#:**
```fsharp
// Must explicitly mark as lazy
let expensiveComputation: Lazy<int> =
    lazy (
        List.sum [1..1000000]
    )

// Must force evaluation
let result: int =
    if condition then expensiveComputation.Force()
    else 0
```

---

## Concurrency Patterns

### Haskell Concurrency → F# Async

Haskell uses lightweight threads and STM, while F# uses async workflows and Task-based async.

| Haskell | F# | Notes |
|---------|-----|-------|
| `forkIO` | `Async.Start` | Spawn concurrent computation |
| `MVar` | `MailboxProcessor` | Message-passing concurrency |
| `STM` | No direct equivalent | Use agents or locks |
| `async` library | `async { }` | Async computations |
| `Async a` | `Async<'a>` | Async type |

### Basic Async Translation

**Haskell:**
```haskell
import Control.Concurrent.Async

fetchData :: String -> IO String
fetchData url = do
    threadDelay 1000000
    return $ "Data from " ++ url

main :: IO ()
main = do
    result1 <- async (fetchData "url1")
    result2 <- async (fetchData "url2")
    data1 <- wait result1
    data2 <- wait result2
    putStrLn $ data1 ++ ", " ++ data2
```

**F#:**
```fsharp
open System

let fetchData (url: string) : Async<string> = async {
    do! Async.Sleep 1000
    return $"Data from {url}"
}

[<EntryPoint>]
let main argv =
    let result =
        async {
            let! data1 = fetchData "url1"
            let! data2 = fetchData "url2"
            return $"{data1}, {data2}"
        }
        |> Async.RunSynchronously

    printfn "%s" result
    0
```

### Parallel Execution

**Haskell:**
```haskell
import Control.Concurrent.Async

fetchAll :: IO ([User], [Order])
fetchAll = do
    (users, orders) <- concurrently fetchUsers fetchOrders
    return (users, orders)
```

**F#:**
```fsharp
let fetchAll: Async<User list * Order list> = async {
    let! users, orders =
        Async.Parallel [
            fetchUsers() |> Async.map (fun x -> Choice1Of2 x)
            fetchOrders() |> Async.map (fun x -> Choice2Of2 x)
        ]
        |> Async.map (fun results ->
            // Handle results...
            ([], [])  // Simplified
        )
    return users, orders
}

// Or simpler with tuple:
let fetchAll': Async<User list * Order list> = async {
    let! results =
        (fetchUsers(), fetchOrders())
        ||> Async.Parallel2
    return results
}
```

---

## Common Pitfalls

### 1. Confusing Result Parameter Order

**Problem:** Haskell's `Either a b` has error first, F#'s `Result<'T,'E>` has success first.

**Example:**
```haskell
-- Haskell: Either ErrorType SuccessType
parseConfig :: String -> Either String Config
parseConfig str = Right config  -- Success is Right
```

```fsharp
// F#: Result<SuccessType, ErrorType>
let parseConfig (str: string) : Result<Config, string> =
    Ok config  // Success is Ok
```

**Solution:** Remember F# swaps the order. When converting:
- Haskell `Either e a` → F# `Result<a, e>`
- Haskell `Left err` → F# `Error err`
- Haskell `Right val` → F# `Ok val`

### 2. Forgetting Lazy vs Eager Evaluation

**Problem:** Infinite lists work in Haskell but cause infinite loops in F#.

**Example:**
```haskell
-- Haskell: works fine (lazy)
allNumbers = [1..]
firstTen = take 10 allNumbers
```

```fsharp
// F#: This will hang! (eager)
// let allNumbers = [1..] // Doesn't compile

// Correct: use sequences
let allNumbers = Seq.initInfinite ((+) 1)
let firstTen = allNumbers |> Seq.take 10 |> Seq.toList
```

**Solution:** Use `seq<'a>` for lazy evaluation in F#, not lists.

### 3. Type Class Constraints Not Translating

**Problem:** Haskell type class constraints don't have direct F# equivalents.

**Example:**
```haskell
-- Haskell: polymorphic with type class
sumAll :: (Num a) => [a] -> a
sumAll = foldr (+) 0
```

```fsharp
// F#: must be specific or use inline
let sumAll (xs: int list) : int =
    List.fold (+) 0 xs

// Or use inline for polymorphism
let inline sumAll xs =
    List.fold (+) LanguagePrimitives.GenericZero xs
```

**Solution:** Use `inline` functions or make types concrete.

### 4. Pattern Matching Syntax Differences

**Problem:** Haskell allows pattern matching in function definitions, F# requires `match`.

**Example:**
```haskell
-- Haskell: patterns in function definition
factorial 0 = 1
factorial n = n * factorial (n - 1)
```

```fsharp
// F#: must use match or if
let rec factorial (n: int) : int =
    match n with
    | 0 -> 1
    | n -> n * factorial (n - 1)

// Or with if
let rec factorial' (n: int) : int =
    if n = 0 then 1
    else n * factorial' (n - 1)
```

**Solution:** Use `match ... with` for pattern matching in F#.

### 5. Module Import Differences

**Problem:** Haskell's qualified imports don't translate directly.

**Example:**
```haskell
-- Haskell
import qualified Data.Map as M
import Data.List (sort, nub)

result = M.lookup "key" map
```

```fsharp
// F#: different syntax
open System.Collections.Generic

// For modules, open at top
// No "qualified" keyword

// Use full paths for disambiguation
let result = Map.tryFind "key" map
```

**Solution:** F# uses `open` for imports, use full module paths for disambiguation.

### 6. Tuple Syntax Confusion

**Problem:** Tuple constructor vs type syntax differs.

**Example:**
```haskell
-- Haskell: consistent syntax
value :: (Int, String)
value = (42, "hello")
```

```fsharp
// F#: different syntax for type vs value
let value: int * string =  // Type uses *
    (42, "hello")          // Value uses ,
```

**Solution:** Remember F# uses `*` in types, `,` in values.

### 7. No Automatic Currying in All Contexts

**Problem:** F# functions are curried, but some .NET APIs are not.

**Example:**
```haskell
-- Haskell: currying everywhere
add x y = x + y
add5 = add 5  -- Partial application
```

```fsharp
// F#: currying works for F# functions
let add x y = x + y
let add5 = add 5  // Works

// But .NET methods are not curried
// Math.Max(1, 2)  // Must provide all args
let max1 = Math.Max(1)  // Error!

// Wrap in F# function for currying
let max a b = Math.Max(a, b)
let max1' = max 1  // Works
```

**Solution:** Wrap .NET methods in F# functions for partial application.

### 8. String Type Differences

**Problem:** Haskell `String` is `[Char]`, F# `string` is `System.String`.

**Example:**
```haskell
-- Haskell: String is a list
reverse :: String -> String
reverse = reverse  -- List reverse works on strings

head :: String -> Char
head (c:_) = c
```

**F#:**
```fsharp
// F#: string is not a list
let reverse (s: string) : string =
    s.ToCharArray()
    |> Array.rev
    |> System.String

let head (s: string) : char =
    s.[0]  // Index, not pattern matching
```

**Solution:** Use string methods and array operations in F#, not list operations.

---

## Tooling

| Category | Haskell | F# Equivalent |
|----------|---------|---------------|
| Compiler | GHC | F# compiler (fsc) |
| Build Tool | Cabal, Stack | dotnet CLI |
| Package Manager | Cabal, Stack | NuGet |
| REPL | GHCi | FSI (F# Interactive) |
| Formatter | stylish-haskell, ormolu | fantomas |
| Linter | HLint | FSharpLint |
| IDE | VS Code + HLS, IntelliJ IDEA | VS Code, Visual Studio, Rider |
| Documentation | Haddock | XML docs / FSharp.Formatting |
| Testing | HSpec, QuickCheck | Expecto, FsCheck |

### Package Ecosystem Mapping

| Purpose | Haskell | F# |
|---------|---------|-----|
| JSON | aeson | FSharp.Json, System.Text.Json |
| HTTP Client | http-client, req | FSharp.Data, HttpClient |
| Parsing | parsec, megaparsec | FParsec |
| CLI | optparse-applicative | Argu |
| Async | async | Built-in async |
| Testing | QuickCheck | FsCheck |
| Web Framework | Servant, Scotty, Yesod | Giraffe, Saturn, Suave |

---

## Examples

### Example 1: Simple - List Processing

**Before (Haskell):**
```haskell
module ListUtils where

-- Filter and map in one pass
processNumbers :: [Int] -> [Int]
processNumbers = map (*2) . filter even

-- Find first match
findFirst :: (a -> Bool) -> [a] -> Maybe a
findFirst pred [] = Nothing
findFirst pred (x:xs)
    | pred x = Just x
    | otherwise = findFirst pred xs

-- Remove duplicates
unique :: Eq a => [a] -> [a]
unique [] = []
unique (x:xs) = x : unique (filter (/= x) xs)
```

**After (F#):**
```fsharp
module ListUtils

// Filter and map in one pass
let processNumbers (xs: int list) : int list =
    xs
    |> List.filter (fun x -> x % 2 = 0)
    |> List.map (fun x -> x * 2)

// Find first match
let findFirst (pred: 'a -> bool) (xs: 'a list) : 'a option =
    List.tryFind pred xs

// Remove duplicates
let unique (xs: 'a list) : 'a list =
    xs |> List.distinct
```

### Example 2: Medium - Tree Data Structure with Traversal

**Before (Haskell):**
```haskell
module Tree where

data Tree a = Leaf a
            | Node a (Tree a) (Tree a)
            deriving (Show, Eq)

-- Insert into binary search tree
insert :: Ord a => a -> Tree a -> Tree a
insert x (Leaf y)
    | x < y = Node y (Leaf x) (Leaf y)
    | otherwise = Node y (Leaf y) (Leaf x)
insert x (Node y left right)
    | x < y = Node y (insert x left) right
    | otherwise = Node y left (insert x right)

-- Map over tree
instance Functor Tree where
    fmap f (Leaf x) = Leaf (f x)
    fmap f (Node x left right) =
        Node (f x) (fmap f left) (fmap f right)

-- Fold tree
foldTree :: (a -> b -> b -> b) -> (a -> b) -> Tree a -> b
foldTree node leaf (Leaf x) = leaf x
foldTree node leaf (Node x left right) =
    node x (foldTree node leaf left) (foldTree node leaf right)

-- Inorder traversal
inorder :: Tree a -> [a]
inorder (Leaf x) = [x]
inorder (Node x left right) =
    inorder left ++ [x] ++ inorder right
```

**After (F#):**
```fsharp
module Tree

type Tree<'a> =
    | Leaf of 'a
    | Node of 'a * Tree<'a> * Tree<'a>

// Insert into binary search tree
let rec insert (x: 'a) (tree: Tree<'a>) : Tree<'a> =
    match tree with
    | Leaf y ->
        if x < y then Node(y, Leaf x, Leaf y)
        else Node(y, Leaf y, Leaf x)
    | Node(y, left, right) ->
        if x < y then Node(y, insert x left, right)
        else Node(y, left, insert x right)

// Map over tree
let rec map (f: 'a -> 'b) (tree: Tree<'a>) : Tree<'b> =
    match tree with
    | Leaf x -> Leaf (f x)
    | Node(x, left, right) ->
        Node(f x, map f left, map f right)

// Fold tree
let rec fold (nodeF: 'a -> 'b -> 'b -> 'b) (leafF: 'a -> 'b) (tree: Tree<'a>) : 'b =
    match tree with
    | Leaf x -> leafF x
    | Node(x, left, right) ->
        nodeF x (fold nodeF leafF left) (fold nodeF leafF right)

// Inorder traversal
let rec inorder (tree: Tree<'a>) : 'a list =
    match tree with
    | Leaf x -> [x]
    | Node(x, left, right) ->
        inorder left @ [x] @ inorder right
```

### Example 3: Complex - Parser Combinator

**Before (Haskell):**
```haskell
{-# LANGUAGE ApplicativeDo #-}

module Parser where

import Control.Applicative
import Data.Char

newtype Parser a = Parser { runParser :: String -> Maybe (a, String) }

instance Functor Parser where
    fmap f (Parser p) = Parser $ \input -> do
        (x, rest) <- p input
        return (f x, rest)

instance Applicative Parser where
    pure x = Parser $ \input -> Just (x, input)
    Parser pf <*> Parser px = Parser $ \input -> do
        (f, rest1) <- pf input
        (x, rest2) <- px rest1
        return (f x, rest2)

instance Alternative Parser where
    empty = Parser $ const Nothing
    Parser p1 <|> Parser p2 = Parser $ \input ->
        p1 input <|> p2 input

-- Basic parsers
satisfy :: (Char -> Bool) -> Parser Char
satisfy pred = Parser $ \input ->
    case input of
        [] -> Nothing
        (x:xs) -> if pred x then Just (x, xs) else Nothing

char :: Char -> Parser Char
char c = satisfy (== c)

string :: String -> Parser String
string [] = pure []
string (c:cs) = do
    char c
    string cs
    pure (c:cs)

-- JSON-like parser
data Value = VNull
           | VBool Bool
           | VNumber Double
           | VString String
           | VArray [Value]
           deriving (Show, Eq)

parseNull :: Parser Value
parseNull = string "null" *> pure VNull

parseBool :: Parser Value
parseBool = (string "true" *> pure (VBool True))
        <|> (string "false" *> pure (VBool False))

parseNumber :: Parser Value
parseNumber = VNumber . read <$> some (satisfy isDigit)

parseString :: Parser Value
parseString = VString <$> (char '"' *> many (satisfy (/= '"')) <* char '"')

parseValue :: Parser Value
parseValue = parseNull <|> parseBool <|> parseNumber <|> parseString
```

**After (F#):**
```fsharp
module Parser

type Parser<'a> = Parser of (string -> ('a * string) option)

let runParser (Parser p) input = p input

// Functor (map)
let map (f: 'a -> 'b) (Parser p: Parser<'a>) : Parser<'b> =
    Parser (fun input ->
        match p input with
        | Some(x, rest) -> Some(f x, rest)
        | None -> None)

// Applicative (pure and apply)
let pure' (x: 'a) : Parser<'a> =
    Parser (fun input -> Some(x, input))

let apply (Parser pf: Parser<'a -> 'b>) (Parser px: Parser<'a>) : Parser<'b> =
    Parser (fun input ->
        match pf input with
        | Some(f, rest1) ->
            match px rest1 with
            | Some(x, rest2) -> Some(f x, rest2)
            | None -> None
        | None -> None)

// Alternative (empty and or)
let empty<'a> : Parser<'a> =
    Parser (fun _ -> None)

let orElse (Parser p1: Parser<'a>) (Parser p2: Parser<'a>) : Parser<'a> =
    Parser (fun input ->
        match p1 input with
        | Some result -> Some result
        | None -> p2 input)

// Basic parsers
let satisfy (pred: char -> bool) : Parser<char> =
    Parser (fun input ->
        match Seq.tryHead input with
        | Some c when pred c ->
            Some(c, input.Substring(1))
        | _ -> None)

let char' (c: char) : Parser<char> =
    satisfy ((=) c)

let rec string' (s: string) : Parser<string> =
    if s.Length = 0 then
        pure' ""
    else
        Parser (fun input ->
            if input.StartsWith(s) then
                Some(s, input.Substring(s.Length))
            else
                None)

// JSON-like parser
type Value =
    | VNull
    | VBool of bool
    | VNumber of float
    | VString of string
    | VArray of Value list

let parseNull: Parser<Value> =
    string' "null"
    |> map (fun _ -> VNull)

let parseBool: Parser<Value> =
    orElse
        (string' "true" |> map (fun _ -> VBool true))
        (string' "false" |> map (fun _ -> VBool false))

let parseNumber: Parser<Value> =
    Parser (fun input ->
        let digits = input |> Seq.takeWhile System.Char.IsDigit |> Seq.toArray
        if digits.Length > 0 then
            let numStr = System.String(digits)
            let num = float numStr
            Some(VNumber num, input.Substring(digits.Length))
        else
            None)

let parseString: Parser<Value> =
    Parser (fun input ->
        if input.StartsWith("\"") then
            let endIndex = input.IndexOf('"', 1)
            if endIndex > 0 then
                let content = input.Substring(1, endIndex - 1)
                Some(VString content, input.Substring(endIndex + 1))
            else
                None
        else
            None)

let parseValue: Parser<Value> =
    parseNull
    |> orElse parseBool
    |> orElse parseNumber
    |> orElse parseString
```

---

## See Also

For more examples and patterns, see:
- `meta-convert-dev` - Foundational conversion patterns (APTV workflow, testing strategies)
- `lang-haskell-dev` - Haskell development patterns
- `lang-fsharp-dev` - F# development patterns
- `patterns-concurrency-dev` - Async, threads, STM across languages
- `patterns-serialization-dev` - JSON, validation across languages
- `patterns-metaprogramming-dev` - Template Haskell → Type Providers
