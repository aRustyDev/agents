---
name: lang-haskell-dev
description: Foundational Haskell patterns covering pure functional programming, type system, type classes, monads, and common idioms. Use when writing Haskell code, understanding pure functions, working with Maybe/Either, leveraging the type system, or needing guidance on functional programming patterns. This is the entry point for Haskell development.
---

# Haskell Fundamentals

Foundational Haskell patterns and core language features for pure functional programming. This skill serves as both a reference for common patterns and foundation for advanced Haskell development.

## Overview

**This skill covers:**
- Pure functions and immutability
- Type system and type inference
- Type classes (Functor, Applicative, Monad)
- Pattern matching and guards
- List comprehensions and recursion
- Common monads (Maybe, Either, IO, State)
- Function composition and higher-order functions
- Lazy evaluation fundamentals

**This skill does NOT cover:**
- Advanced type system features (GADTs, Type Families, DataKinds)
- Lens and optics
- Concurrency and parallelism (STM, async)
- Template Haskell and metaprogramming
- Specific frameworks (Yesod, Servant, Scotty)
- Build tools (Cabal, Stack) - see language-specific tooling skills

---

## Quick Reference

| Task | Pattern |
|------|---------|
| Define function | `name :: Type -> Type`<br>`name x = expression` |
| Pattern match | `case x of Pattern -> expr` |
| List comprehension | `[x * 2 \| x <- [1..10], x > 5]` |
| Lambda | `\x -> x + 1` |
| Function composition | `(f . g) x` equals `f (g x)` |
| Type class constraint | `func :: (Show a) => a -> String` |
| Monadic bind | `x >>= f` or `do { y <- x; ... }` |
| Functor map | `fmap f x` or `f <$> x` |
| Applicative apply | `f <*> x` |

---

## Core Concepts

### Pure Functions

```haskell
-- Pure function: same input always produces same output
add :: Int -> Int -> Int
add x y = x + y

-- No side effects - this is NOT valid pure code:
-- impureAdd x y = do
--     print "Adding..."  -- Side effect!
--     return (x + y)

-- Referential transparency: can replace call with result
result1 = add 2 3        -- Always 5
result2 = add 2 3        -- Always 5 (same)
```

### Immutability

```haskell
-- Values cannot be changed
x = 5
-- x = 6  -- Error: multiple declarations

-- "Update" by creating new values
data User = User { name :: String, age :: Int }

updateAge :: Int -> User -> User
updateAge newAge user = user { age = newAge }

-- Original unchanged
user1 = User "Alice" 25
user2 = updateAge 26 user1
-- user1 still has age 25
```

---

## Type System

### Type Inference

```haskell
-- Explicit type signature (recommended)
double :: Int -> Int
double x = x * 2

-- Type inference (compiler deduces type)
triple x = x * 3  -- Inferred: Num a => a -> a

-- Polymorphic types
identity :: a -> a
identity x = x
-- Works for any type: identity 5, identity "hello", etc.
```

### Algebraic Data Types

```haskell
-- Sum types (OR)
data Shape = Circle Float
           | Rectangle Float Float
           | Triangle Float Float Float

-- Product types (AND)
data Point = Point Float Float

-- Record syntax
data Person = Person
    { firstName :: String
    , lastName  :: String
    , age       :: Int
    } deriving (Show, Eq)

-- Using records
person = Person "Alice" "Smith" 30
name = firstName person  -- "Alice"
older = person { age = 31 }  -- Update syntax
```

### Type Aliases

```haskell
-- Simple alias
type Name = String
type Age = Int

-- Parameterized alias
type Pair a = (a, a)
type AssocList k v = [(k, v)]

-- Usage
getName :: Person -> Name
getName p = firstName p
```

### Newtype

```haskell
-- Zero-cost wrapper (compile-time only)
newtype UserId = UserId Int deriving (Show, Eq)
newtype Email = Email String deriving (Show, Eq)

-- Type safety: can't mix UserId and Email
processUser :: UserId -> String
processUser (UserId id) = "User " ++ show id

-- Can't accidentally pass wrong type
userId = UserId 42
-- processUser 42  -- Error!
processUser userId  -- Ok
```

---

## Pattern Matching

### Basic Patterns

```haskell
-- Match literals
isZero :: Int -> Bool
isZero 0 = True
isZero _ = False

-- Match constructors
describeShape :: Shape -> String
describeShape (Circle r) = "Circle with radius " ++ show r
describeShape (Rectangle w h) = "Rectangle " ++ show w ++ "x" ++ show h
describeShape (Triangle a b c) = "Triangle with sides " ++ show a ++ "," ++ show b ++ "," ++ show c

-- Match lists
listLength :: [a] -> Int
listLength [] = 0
listLength (_:xs) = 1 + listLength xs

-- First element pattern
head' :: [a] -> Maybe a
head' [] = Nothing
head' (x:_) = Just x
```

### Case Expressions

```haskell
-- Case in expression
describe :: Maybe Int -> String
describe m = case m of
    Nothing -> "No value"
    Just x  -> "Value: " ++ show x

-- Nested patterns
evalExpr :: Expr -> Int
evalExpr expr = case expr of
    Lit n -> n
    Add e1 e2 -> evalExpr e1 + evalExpr e2
    Mul e1 e2 -> evalExpr e1 * evalExpr e2
```

### Guards

```haskell
-- Boolean conditions
classify :: Int -> String
classify n
    | n < 0     = "negative"
    | n == 0    = "zero"
    | n < 10    = "small"
    | otherwise = "large"

-- Pattern guards
processUser :: Maybe User -> String
processUser mu
    | Nothing <- mu = "No user"
    | Just u <- mu, age u >= 18 = "Adult: " ++ name u
    | Just u <- mu = "Minor: " ++ name u
```

---

## Type Classes

### Common Type Classes

```haskell
-- Eq: Equality
data Color = Red | Green | Blue deriving (Eq)
result = Red == Green  -- False

-- Ord: Ordering
data Priority = Low | Medium | High deriving (Eq, Ord)
result = High > Low  -- True

-- Show: String representation
data Point = Point Int Int deriving (Show)
p = Point 3 4
str = show p  -- "Point 3 4"

-- Read: Parse from string
value = read "42" :: Int
```

### Functor

```haskell
-- fmap: Apply function inside context
-- fmap :: Functor f => (a -> b) -> f a -> f b

-- Maybe Functor
result1 = fmap (*2) (Just 5)     -- Just 10
result2 = fmap (*2) Nothing      -- Nothing

-- List Functor
result3 = fmap (*2) [1,2,3]      -- [2,4,6]

-- Operator form: <$>
result4 = (*2) <$> Just 5        -- Just 10
result5 = (*2) <$> [1,2,3]       -- [2,4,6]

-- Function composition in Functor
result6 = (+1) <$> (*2) <$> Just 5  -- Just 11
```

### Applicative

```haskell
-- <*>: Apply function in context to value in context
-- pure: Lift value into context

-- Maybe Applicative
result1 = pure (+) <*> Just 3 <*> Just 4     -- Just 7
result2 = pure (+) <*> Nothing <*> Just 4    -- Nothing

-- Applicative style
result3 = (+) <$> Just 3 <*> Just 4          -- Just 7

-- Multiple arguments
data User = User String Int
createUser = User <$> Just "Alice" <*> Just 30  -- Just (User "Alice" 30)

-- List Applicative (Cartesian product)
result4 = (*) <$> [1,2] <*> [3,4]  -- [3,4,6,8]
```

### Monad

```haskell
-- >>= (bind): Chain operations that return monadic values
-- return: Lift value into monad (same as pure)

-- Maybe Monad
safeDivide :: Float -> Float -> Maybe Float
safeDivide _ 0 = Nothing
safeDivide x y = Just (x / y)

calculation :: Maybe Float
calculation = do
    a <- Just 10
    b <- Just 2
    result <- safeDivide a b
    return (result * 2)  -- Just 10.0

-- Same with bind operator
calculation' = Just 10 >>= \a ->
               Just 2  >>= \b ->
               safeDivide a b >>= \result ->
               return (result * 2)

-- Either Monad (for error handling)
type Error = String

validateAge :: Int -> Either Error Int
validateAge age
    | age < 0 = Left "Age cannot be negative"
    | age > 150 = Left "Age too high"
    | otherwise = Right age

validateEmail :: String -> Either Error String
validateEmail email
    | '@' `elem` email = Right email
    | otherwise = Left "Invalid email"

createUser :: Int -> String -> Either Error User
createUser age email = do
    validAge <- validateAge age
    validEmail <- validateEmail email
    return $ User validEmail validAge
```

---

## Lists and Recursion

### List Comprehensions

```haskell
-- Basic comprehension
squares = [x^2 | x <- [1..10]]

-- With filter
evenSquares = [x^2 | x <- [1..10], even x]

-- Multiple generators
pairs = [(x,y) | x <- [1..3], y <- [1..3]]
-- [(1,1),(1,2),(1,3),(2,1),(2,2),(2,3),(3,1),(3,2),(3,3)]

-- Dependent generators
orderedPairs = [(x,y) | x <- [1..5], y <- [x..5]]
-- [(1,1),(1,2),...,(5,5)]

-- Multiple filters
pythagoras = [(a,b,c) | a <- [1..20],
                        b <- [a..20],
                        c <- [b..20],
                        a^2 + b^2 == c^2]
```

### Recursive Functions

```haskell
-- Sum of list
sum' :: [Int] -> Int
sum' [] = 0
sum' (x:xs) = x + sum' xs

-- Filter
filter' :: (a -> Bool) -> [a] -> [a]
filter' _ [] = []
filter' p (x:xs)
    | p x       = x : filter' p xs
    | otherwise = filter' p xs

-- Map
map' :: (a -> b) -> [a] -> [b]
map' _ [] = []
map' f (x:xs) = f x : map' f xs

-- Fold (right)
foldr' :: (a -> b -> b) -> b -> [a] -> b
foldr' _ acc [] = acc
foldr' f acc (x:xs) = f x (foldr' f acc xs)

-- Fibonacci
fib :: Int -> Int
fib 0 = 0
fib 1 = 1
fib n = fib (n-1) + fib (n-2)
```

### Common List Functions

```haskell
-- Construction and access
list = 1 : 2 : 3 : []        -- [1,2,3]
first = head [1,2,3]         -- 1
rest = tail [1,2,3]          -- [2,3]

-- Transformation
doubled = map (*2) [1,2,3]                    -- [2,4,6]
evens = filter even [1,2,3,4]                 -- [2,4]
sum = foldr (+) 0 [1,2,3,4]                   -- 10
reversed = reverse [1,2,3]                    -- [3,2,1]

-- Combination
combined = concat [[1,2], [3,4]]              -- [1,2,3,4]
flattened = concatMap (\x -> [x,x]) [1,2,3]   -- [1,1,2,2,3,3]
zipped = zip [1,2,3] ['a','b','c']            -- [(1,'a'),(2,'b'),(3,'c')]

-- Selection
taken = take 3 [1..10]      -- [1,2,3]
dropped = drop 3 [1..10]    -- [4,5,6,7,8,9,10]
split = splitAt 3 [1..10]   -- ([1,2,3],[4,5,6,7,8,9,10])
```

---

## Higher-Order Functions

### Function Composition

```haskell
-- Compose: (f . g) x = f (g x)
addThenDouble = (*2) . (+1)
result = addThenDouble 5  -- 12

-- Chain multiple functions
process = filter even . map (*2) . filter (>0)
result = process [-2,-1,0,1,2,3]  -- [2,4,6]

-- Point-free style
-- Instead of: f x = g (h x)
-- Write: f = g . h
sumOfSquares :: [Int] -> Int
sumOfSquares = sum . map (^2)
```

### Partial Application

```haskell
-- Functions are curried by default
add :: Int -> Int -> Int
add x y = x + y

-- Partial application
add5 :: Int -> Int
add5 = add 5

result = add5 10  -- 15

-- Common pattern
doubleAll = map (*2)
filterPositive = filter (>0)

result = doubleAll [1,2,3]     -- [2,4,6]
result = filterPositive [-1,0,1,2]  -- [1,2]
```

### Common Higher-Order Patterns

```haskell
-- Apply function n times
applyN :: Int -> (a -> a) -> a -> a
applyN 0 _ x = x
applyN n f x = applyN (n-1) f (f x)

result = applyN 3 (*2) 5  -- 40 (5*2*2*2)

-- Flip arguments
flip' :: (a -> b -> c) -> (b -> a -> c)
flip' f x y = f y x

-- Use with sections
subtractFrom10 = flip (-) 10
result = subtractFrom10 3  -- 7 (10 - 3)
```

---

## Common Monads

### Maybe

```haskell
-- Represent optional values
findUser :: Int -> Maybe User
findUser 1 = Just (User "Alice" 30)
findUser _ = Nothing

-- Chain operations
getUserEmail :: Int -> Maybe String
getUserEmail userId = do
    user <- findUser userId
    return (email user)

-- Handle Nothing
getEmailOrDefault :: Int -> String
getEmailOrDefault userId =
    case findUser userId of
        Just user -> email user
        Nothing -> "no-email@example.com"

-- Maybe functions
result1 = fromMaybe "default" (Just "value")  -- "value"
result2 = fromMaybe "default" Nothing         -- "default"
result3 = maybe "none" show (Just 42)         -- "42"
```

### Either

```haskell
-- Represent computations that can fail
parseAge :: String -> Either String Int
parseAge str =
    case reads str of
        [(n, "")] -> if n >= 0
                     then Right n
                     else Left "Age must be positive"
        _ -> Left "Not a valid number"

-- Chain Either operations
validateUser :: String -> String -> Either String User
validateUser ageStr emailStr = do
    age <- parseAge ageStr
    email <- validateEmail emailStr
    return $ User email age

-- Either functions
result1 = either show (*2) (Right 5)  -- 10
result2 = either show (*2) (Left "error")  -- "error"
```

### IO

```haskell
-- IO actions are first-class values
greeting :: IO ()
greeting = do
    putStrLn "What is your name?"
    name <- getLine
    putStrLn $ "Hello, " ++ name

-- Read file
readConfig :: FilePath -> IO String
readConfig path = do
    contents <- readFile path
    return contents

-- Write file
writeLog :: String -> IO ()
writeLog message = do
    appendFile "log.txt" (message ++ "\n")

-- Sequence IO actions
main :: IO ()
main = do
    putStrLn "Starting..."
    result <- computation
    putStrLn $ "Result: " ++ show result
    putStrLn "Done"
```

### State

```haskell
import Control.Monad.State

-- Stateful computation
type Counter a = State Int a

-- Increment counter
increment :: Counter ()
increment = modify (+1)

-- Get current count
getCount :: Counter Int
getCount = get

-- Stateful computation
computation :: Counter Int
computation = do
    increment
    increment
    increment
    count <- getCount
    return count

-- Run state
result = runState computation 0  -- (3, 3)
finalState = execState computation 0  -- 3
finalValue = evalState computation 0  -- 3
```

---

## Lazy Evaluation

### Infinite Lists

```haskell
-- Infinite list of naturals
naturals = [1..]

-- Take first 10
first10 = take 10 naturals  -- [1,2,3,4,5,6,7,8,9,10]

-- Infinite Fibonacci
fibs = 0 : 1 : zipWith (+) fibs (tail fibs)
first10Fibs = take 10 fibs  -- [0,1,1,2,3,5,8,13,21,34]

-- Infinite repeat
ones = repeat 1
cycle123 = cycle [1,2,3]  -- [1,2,3,1,2,3,1,2,3,...]
```

### Strictness

```haskell
-- Lazy by default
lazySum xs = if null xs then 0 else head xs + lazySum (tail xs)

-- Force strict evaluation with $!
strictSum xs = if null xs then 0 else head xs $! strictSum (tail xs)

-- seq: Force evaluation
forceEval x y = x `seq` y

-- BangPatterns extension
{-# LANGUAGE BangPatterns #-}
strictFunc !x = x + 1  -- x evaluated immediately
```

---

## Common Idioms

### Pipeline Style

```haskell
-- Use $ to avoid parentheses
result = show $ sum $ map (*2) [1,2,3]

-- Use & for left-to-right flow (Data.Function)
import Data.Function ((&))
result = [1,2,3]
       & map (*2)
       & sum
       & show
```

### Where vs Let

```haskell
-- where: Definitions after expression
circleArea r = pi * r^2
  where pi = 3.14159

-- let: Definitions before expression
circleArea' r =
  let pi = 3.14159
  in pi * r^2

-- let in do-notation
computation = do
    let x = 5
        y = 10
    return (x + y)
```

### Operator Sections

```haskell
-- Partially apply operators
add5 = (+5)      -- Add 5 to argument
half = (/2)      -- Divide argument by 2
double = (*2)    -- Multiply argument by 2

-- Use with map
doubled = map (*2) [1,2,3]  -- [2,4,6]
```

---

## Troubleshooting

### Type Errors

**Problem:** Type mismatch

```haskell
-- Error: Couldn't match expected type 'Int' with actual type '[Int]'
badFunc :: Int -> Int
badFunc x = [x]  -- Returns list, not Int
```

**Fix:** Match return type:
```haskell
goodFunc :: Int -> [Int]
goodFunc x = [x]
```

### Infinite Loops

**Problem:** Non-terminating recursion

```haskell
-- Never terminates!
badLength xs = 1 + badLength xs
```

**Fix:** Add base case:
```haskell
goodLength [] = 0
goodLength (_:xs) = 1 + goodLength xs
```

### Monad Type Errors

**Problem:** Couldn't match type 'Maybe a' with 'a'

```haskell
-- Error: findUser returns Maybe User, not User
badCode = name (findUser 1)
```

**Fix:** Extract with bind or pattern match:
```haskell
goodCode = do
    user <- findUser 1
    return (name user)

-- Or:
goodCode = case findUser 1 of
    Just user -> name user
    Nothing -> "Unknown"
```

### Lazy Evaluation Issues

**Problem:** Stack overflow on large list

```haskell
-- Lazy accumulation builds up thunks
badSum = foldl (+) 0 [1..1000000]
```

**Fix:** Use strict fold:
```haskell
import Data.List (foldl')
goodSum = foldl' (+) 0 [1..1000000]
```

---

## References

- [Learn You a Haskell](http://learnyouahaskell.com/)
- [Haskell Wiki](https://wiki.haskell.org/)
- [Hoogle (API Search)](https://hoogle.haskell.org/)
- [Real World Haskell](http://book.realworldhaskell.org/)
- [GHC User Guide](https://downloads.haskell.org/ghc/latest/docs/users_guide/)
