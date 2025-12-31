# Numeric Type Edge Cases Reference

Numeric type conversion is deceptively complex. This reference covers edge cases and translation patterns for numeric types across languages.

## Numeric Type Landscape

| Category | Languages | Characteristics |
|----------|-----------|-----------------|
| **Arbitrary precision** | Python, Clojure, Haskell (Integer) | Unlimited size, slower operations |
| **Fixed-size integers** | Rust, Go, C, Java | Fast, can overflow |
| **Auto-promotion** | Python, Clojure | Automatically upgrade on overflow |
| **Checked arithmetic** | Rust (debug), Swift | Panic/crash on overflow |
| **Wrapping arithmetic** | C, Rust (release) | Wrap around on overflow |
| **Saturating arithmetic** | Rust (explicit) | Clamp to min/max |

## Integer Type Mapping

### Size Comparison

| Python | Clojure | Rust | Go | Java | F# | Elixir |
|--------|---------|------|------|------|-------|--------|
| `int` (arbitrary) | `Long`/`BigInt` | `i8`-`i128` | `int8`-`int64` | `byte`-`long` | `int8`-`int64` | integer (arbitrary) |
| - | - | `u8`-`u128` | `uint8`-`uint64` | - | `uint8`-`uint64` | - |

### Arbitrary Precision → Fixed Size

**Problem:** Source language has arbitrary precision; target has fixed size.

**Python:**
```python
big_number = 10 ** 100  # Works fine
result = big_number * 2  # Still works
```

**Rust:**
```rust
// Option 1: Use largest fixed type + panic on overflow
let big_number: i128 = 10_i128.pow(38); // Max ~170 digits
// 10^100 would overflow!

// Option 2: Use big integer library
use num_bigint::BigInt;
let big_number = BigInt::from(10).pow(100);
let result = &big_number * 2;

// Option 3: Checked arithmetic with explicit handling
let a: i64 = 1_000_000_000;
let b: i64 = 1_000_000_000;
match a.checked_mul(b) {
    Some(result) => println!("Result: {}", result),
    None => println!("Overflow!"),
}
```

**Translation Strategy:**
1. Analyze source code for maximum expected values
2. Choose smallest fixed type that fits
3. Add overflow handling for edge cases
4. Use big integer library if arbitrary precision required

### Overflow Handling Patterns

| Language | Default Behavior | Alternative |
|----------|------------------|-------------|
| Python | Auto-promote to bigint | N/A |
| Rust (debug) | Panic | `wrapping_*`, `saturating_*`, `checked_*` |
| Rust (release) | Wrap | Same as debug |
| Go | Wrap silently | `math/big` for big integers |
| Java | Wrap silently | `BigInteger` |
| C | Undefined (signed) | Use unsigned or check manually |
| Elixir | Auto-promote | N/A |

**Example - Checked Arithmetic Translation:**

```python
# Python: implicit overflow handling
def factorial(n):
    result = 1
    for i in range(1, n + 1):
        result *= i
    return result

factorial(100)  # Works: huge number
```

```rust
// Rust: must handle explicitly
fn factorial_checked(n: u32) -> Option<u128> {
    let mut result: u128 = 1;
    for i in 1..=n {
        result = result.checked_mul(i as u128)?;
    }
    Some(result)
}

// Or use big integers
use num_bigint::BigUint;
fn factorial_big(n: u32) -> BigUint {
    (1..=n).map(BigUint::from).product()
}
```

## Division Behavior

Division semantics vary significantly across languages.

### Integer Division

| Language | `7 / 2` | `-7 / 2` | Notes |
|----------|---------|----------|-------|
| Python 3 | `3.5` | `-3.5` | `/` is true division |
| Python 3 | `3` (floor) | `-4` (floor) | `//` is floor division |
| Rust | `3` | `-3` | Truncates toward zero |
| Go | `3` | `-3` | Truncates toward zero |
| Java | `3` | `-3` | Truncates toward zero |
| Clojure | `7/2` (ratio) | `-7/2` (ratio) | Exact rationals |
| Elixir | `3` | `-4` | Floor division via `div/2` |

**Translation Considerations:**

```python
# Python floor division
result = -7 // 2  # -4 (floor toward -∞)
```

```rust
// Rust truncates toward zero
let result = -7 / 2;  // -3

// To match Python floor division:
fn floor_div(a: i32, b: i32) -> i32 {
    let d = a / b;
    let r = a % b;
    if (r > 0 && b < 0) || (r < 0 && b > 0) {
        d - 1
    } else {
        d
    }
}
```

### Modulo vs Remainder

| Language | `-7 % 3` | Notes |
|----------|----------|-------|
| Python | `2` | Modulo (same sign as divisor) |
| Rust | `-1` | Remainder (same sign as dividend) |
| Go | `-1` | Remainder |
| Java | `-1` | Remainder |
| Elixir | `2` | Modulo via `rem/2` and `Integer.mod/2` |

**Translation:**

```python
# Python modulo
result = -7 % 3  # 2 (always positive when divisor positive)
```

```rust
// Rust remainder
let result = -7 % 3;  // -1

// To match Python modulo:
fn modulo(a: i32, b: i32) -> i32 {
    ((a % b) + b) % b
}
```

### Rational Numbers

Some languages have built-in rational number support:

| Language | Support | Example |
|----------|---------|---------|
| Clojure | Native | `(/ 7 2)` → `7/2` |
| Haskell | Native | `7 % 2` → `7 % 2` (Ratio) |
| Python | Library | `Fraction(7, 2)` |
| Rust | Library | `num_rational::Ratio::new(7, 2)` |
| F# | None | Use `decimal` or library |

## Floating Point Edge Cases

### Float Type Mapping

| Language | Default Float | Double | Notes |
|----------|---------------|--------|-------|
| Python | `float` (64-bit) | Same | Only one float type |
| Rust | - | `f32`, `f64` | Explicit choice |
| Go | - | `float32`, `float64` | Explicit choice |
| Java | `float` | `double` | `double` preferred |
| F# | `float32` | `float` | `float` is 64-bit |

### Special Values

| Value | Python | Rust | Go | Notes |
|-------|--------|------|------|-------|
| +Infinity | `float('inf')` | `f64::INFINITY` | `math.Inf(1)` | |
| -Infinity | `float('-inf')` | `f64::NEG_INFINITY` | `math.Inf(-1)` | |
| NaN | `float('nan')` | `f64::NAN` | `math.NaN()` | |
| Check NaN | `math.isnan(x)` | `x.is_nan()` | `math.IsNaN(x)` | |
| Check Inf | `math.isinf(x)` | `x.is_infinite()` | `math.IsInf(x, 0)` | |

**NaN Comparison Gotcha:**

```python
# Python
nan = float('nan')
nan == nan  # False! NaN is not equal to itself
```

```rust
// Rust - same behavior
let nan = f64::NAN;
nan == nan  // false

// Use is_nan() for checking
nan.is_nan()  // true
```

### Decimal/Fixed-Point Types

For financial calculations, avoid float:

| Language | Decimal Type | Notes |
|----------|--------------|-------|
| Python | `decimal.Decimal` | Configurable precision |
| Rust | `rust_decimal::Decimal` | 96-bit integer + scale |
| Go | `shopspring/decimal` | Third-party library |
| Java | `BigDecimal` | Arbitrary precision |
| F# | `decimal` | .NET 128-bit decimal |
| Elixir | `Decimal` | Third-party library |

**Translation for Financial Code:**

```python
# Python
from decimal import Decimal
price = Decimal('19.99')
qty = Decimal('3')
total = price * qty  # Decimal('59.97')
```

```rust
use rust_decimal::Decimal;
use rust_decimal_macros::dec;

let price = dec!(19.99);
let qty = dec!(3);
let total = price * qty;  // Decimal 59.97
```

## Type Coercion Patterns

### Implicit vs Explicit

| Language | Implicit Coercion | Notes |
|----------|-------------------|-------|
| Python | Extensive | int → float, etc. |
| JavaScript | Extensive (too much) | "2" + 2 = "22" |
| Rust | None | All explicit |
| Go | Minimal | Only int ↔ float forbidden |
| Haskell | None | Type classes for overloading |

**Python (implicit):**
```python
result = 5 + 3.14  # int + float = float (5.0 + 3.14)
text = "value: " + str(42)  # explicit string conversion
```

**Rust (explicit):**
```rust
let result = 5_f64 + 3.14;  // both must be f64
// or
let result = 5 as f64 + 3.14;

let text = format!("value: {}", 42);  // or
let text = "value: ".to_string() + &42.to_string();
```

### Conversion Functions

| Operation | Python | Rust | Go | Elixir |
|-----------|--------|------|------|--------|
| int → float | `float(x)` | `x as f64` | `float64(x)` | `x / 1.0` or `x * 1.0` |
| float → int | `int(x)` (truncate) | `x as i64` | `int(x)` | `trunc(x)` |
| string → int | `int("42")` | `"42".parse::<i32>()` | `strconv.Atoi("42")` | `String.to_integer("42")` |
| int → string | `str(42)` | `42.to_string()` | `strconv.Itoa(42)` | `Integer.to_string(42)` |

## Numeric Literal Syntax

| Feature | Python | Rust | Go | Elixir |
|---------|--------|------|------|--------|
| Underscore separator | `1_000_000` | `1_000_000` | ❌ | `1_000_000` |
| Binary | `0b1010` | `0b1010` | ❌ | `0b1010` |
| Octal | `0o755` | `0o755` | `0755` | `0o755` |
| Hex | `0xFF` | `0xFF` | `0xFF` | `0xFF` |
| Scientific | `1e10` | `1e10` | `1e10` | `1.0e10` |
| Type suffix | ❌ | `42_i64` | ❌ | ❌ |

## Common Translation Pitfalls

### 1. Assuming Overflow Behavior

```python
# Python: works fine
x = 2 ** 1000  # huge number, no problem
```

```rust
// Rust: will panic in debug, wrap in release
let x = 2_i64.pow(1000);  // PANIC!

// Solution: use big integers or checked arithmetic
```

### 2. Division Semantics

```python
# Python 3
-7 // 2  # -4 (floor division)
```

```go
// Go
-7 / 2  // -3 (truncation!)
// Must implement floor division manually
```

### 3. Float Comparison

```python
# Python
0.1 + 0.2 == 0.3  # False! (0.30000000000000004)
```

```rust
// Solution: epsilon comparison
fn approx_eq(a: f64, b: f64) -> bool {
    (a - b).abs() < f64::EPSILON * 10.0
}
```

### 4. Integer Range Assumptions

```python
# Python: integers can be arbitrarily large
sum(range(1, 1_000_000_000))  # Works (slowly)
```

```rust
// Rust: i64 max is ~9.2 × 10^18
// Sum of 1..1_000_000_000 is ~5 × 10^17, so it fits
// But must be explicit about type!
let sum: i128 = (1..1_000_000_000_i128).sum();
```

---

## Quick Reference Tables

### Safe Integer Ranges

| Type | Min | Max | Digits |
|------|-----|-----|--------|
| `i8` | -128 | 127 | 3 |
| `i16` | -32,768 | 32,767 | 5 |
| `i32` | -2.1×10⁹ | 2.1×10⁹ | 10 |
| `i64` | -9.2×10¹⁸ | 9.2×10¹⁸ | 19 |
| `i128` | -1.7×10³⁸ | 1.7×10³⁸ | 39 |

### Float Precision

| Type | Significant Digits | Range |
|------|--------------------|-------|
| `f32` | ~7 | ±3.4×10³⁸ |
| `f64` | ~15 | ±1.8×10³⁰⁸ |

---

## Cross-References

- [Type System Mapping](../../meta-convert-guide/reference/) - General type mapping strategies
- [Platform Ecosystem](platform-ecosystem.md) - Platform-specific numeric handling
- [Stdlib Mapping](stdlib-mapping.md) - Math function equivalents
