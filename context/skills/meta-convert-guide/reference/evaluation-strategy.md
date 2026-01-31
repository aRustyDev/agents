# Evaluation Strategy Reference

Guide for translating between lazy and eager evaluation strategies.

---

## Evaluation Strategy Overview

| Language   | Default Strategy | Lazy Support                           | Eager Support                   |
|------------|------------------|----------------------------------------|---------------------------------|
| Haskell    | Lazy             | Built-in                               | `seq`, `deepseq`, bang patterns |
| Scala      | Eager            | `lazy val`, by-name params, `LazyList` | Default                         |
| Clojure    | Eager            | Lazy seqs, `delay`/`force`             | Default                         |
| Erlang     | Eager            | Manual thunks                          | Default                         |
| Elixir     | Eager            | Streams, lazy enums                    | Default                         |
| F#         | Eager            | `Lazy<T>`, `seq { }`                   | Default                         |
| Rust       | Eager            | Iterators (lazy), `Lazy<T>`            | Default                         |
| Python     | Eager            | Generators, itertools                  | Default                         |
| JavaScript | Eager            | Generators                             | Default                         |

---

## Key Differences

| Aspect | Lazy Evaluation | Eager Evaluation |
|--------|-----------------|------------------|
| When computed | On demand | Immediately |
| Infinite data | Works fine | Stack overflow / hang |
| Memory | Can have space leaks | Predictable |
| Side effects | Deferred (surprising!) | Immediate |
| Debugging | Non-obvious order | Sequential |
| Performance | Thunk overhead | Direct computation |

---

## Lazy → Eager Conversion

### Infinite Structures → Generators

```haskell
-- Haskell: Infinite list (lazy by default)
fibs :: [Integer]
fibs = 0 : 1 : zipWith (+) fibs (tail fibs)

take 10 fibs  -- Only computes first 10
```

```python
# Python: Must explicitly use generators
def fibs():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

from itertools import islice
list(islice(fibs(), 10))  # Take first 10
```

```rust
// Rust: Iterators are lazy, collections are eager
fn fibs() -> impl Iterator<Item = u64> {
    let mut state = (0, 1);
    std::iter::from_fn(move || {
        let next = state.0;
        state = (state.1, state.0 + state.1);
        Some(next)
    })
}

fibs().take(10).collect::<Vec<_>>()
```

```elixir
# Elixir: Stream for laziness
fibs = Stream.unfold({0, 1}, fn {a, b} -> {a, {b, a + b}} end)

Enum.take(fibs, 10)
```

```erlang
%% Erlang: Manual thunks for laziness
fib_stream() ->
    fib_stream(0, 1).

fib_stream(A, B) ->
    fun() -> {A, fib_stream(B, A + B)} end.

take(0, _Stream) -> [];
take(N, Stream) ->
    {Value, Next} = Stream(),
    [Value | take(N - 1, Next)].
```

---

## Eager → Lazy Conversion

### Avoiding Unnecessary Computation

```python
# Python: Eager - computes all before filtering
def process(items):
    result = []
    for item in items:
        transformed = expensive_transform(item)  # Called for ALL items
        if is_valid(transformed):
            result.append(transformed)
    return result[:10]  # Only needed first 10!
```

```haskell
-- Haskell: Lazy - only transforms what's needed
process :: [Item] -> [Item]
process items =
    take 10 $ filter isValid $ map expensiveTransform items
-- Only transforms until 10 valid items found
```

### Adding Laziness to Eager Languages

```python
# Python: Use generators for laziness
def process(items):
    for item in items:
        transformed = expensive_transform(item)
        if is_valid(transformed):
            yield transformed

list(islice(process(items), 10))  # Only compute first 10
```

```elixir
# Elixir: Use Stream instead of Enum
items
|> Stream.map(&expensive_transform/1)
|> Stream.filter(&is_valid/1)
|> Enum.take(10)
```

---

## Side Effects with Laziness

### The Problem

```haskell
-- Haskell: Side effects are deferred!
let xs = map (\x -> trace ("processing " ++ show x) x) [1..10]
-- Nothing printed yet!

head xs  -- "processing 1" printed now
```

### The Solution

```haskell
-- Haskell: Use IO for controlled effects
processWithLogging :: [Int] -> IO [Int]
processWithLogging xs = forM xs $ \x -> do
    putStrLn $ "processing " ++ show x
    return x

-- Or use strict evaluation
import Control.DeepSeq
let !xs = force $ map process items  -- Evaluate now
```

---

## Space Leaks

### The Problem

```haskell
-- Haskell: Space leak - holds reference to entire list
mean :: [Double] -> Double
mean xs = sum xs / fromIntegral (length xs)
-- Traverses list twice, holding it in memory
```

### The Solution

```haskell
-- Haskell: Fold once, strict accumulator
mean :: [Double] -> Double
mean xs = s / fromIntegral n
  where
    (s, n) = foldl' (\(!s, !n) x -> (s + x, n + 1)) (0, 0) xs
```

---

## Iterator Patterns (Lazy in Eager Languages)

### Rust Iterators

```rust
// Lazy operations
let iter = vec![1, 2, 3, 4, 5]
    .into_iter()
    .map(|x| x * 2)      // Not computed yet
    .filter(|x| x > 4);  // Still not computed

// Only computed when consumed
let result: Vec<_> = iter.collect();
```

### Python Generators

```python
# Generator expression (lazy)
squares = (x * x for x in range(1000000))

# List comprehension (eager)
squares = [x * x for x in range(1000000)]
```

### Elixir Stream vs Enum

```elixir
# Enum: Eager - creates intermediate lists
1..1_000_000
|> Enum.map(&(&1 * 2))     # Creates full list
|> Enum.filter(&(&1 > 10)) # Creates another list
|> Enum.take(10)

# Stream: Lazy - processes one at a time
1..1_000_000
|> Stream.map(&(&1 * 2))     # No computation
|> Stream.filter(&(&1 > 10)) # Still no computation
|> Enum.take(10)             # Computes just what's needed
```

---

## Conversion Guidelines

### Lazy → Eager

1. Replace infinite structures with generators/iterators
2. Ensure side effects are in IO/effect monads
3. Watch for space leaks becoming eager memory usage
4. Add explicit limits (`take`, `limit`) before consuming
5. Consider strictness annotations for performance

### Eager → Lazy

1. Remove explicit iteration limits (laziness handles it)
2. Be careful with side effects - they'll be deferred
3. Use `seq`/strict annotations for performance-critical paths
4. Consider space leaks with retained references
5. Test that work isn't duplicated on multiple traversals

---

## Quick Reference

| Pattern | Lazy Language | Eager Language |
|---------|---------------|----------------|
| Infinite list | `[1..]` | Generator/Stream |
| Transform | `map f xs` | `iter().map()` |
| Filter | `filter p xs` | `iter().filter()` |
| Take n | `take n xs` | `.take(n)` |
| Force eval | `seq`, `!` | Default |
| Defer eval | Default | `lazy`, generator |
