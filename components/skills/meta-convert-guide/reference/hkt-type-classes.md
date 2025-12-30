# Higher-Kinded Types & Type Classes Reference

Advanced type system features and their translation across languages.

---

## Higher-Kinded Types (HKTs)

### What Are HKTs?

HKTs are types that take other type constructors as parameters.

```haskell
-- Haskell: f is a type constructor (like [], Maybe, IO)
class Functor f where
  fmap :: (a -> b) -> f a -> f b

-- f is higher-kinded: it takes a type and produces a type
-- [] :: * -> *
-- Maybe :: * -> *
```

### Language Support

| Language   | HKT Support                | Alternative            |
|------------|----------------------------|------------------------|
| Haskell    | Full (`Functor`, `Monad`)  | N/A                    |
| Scala      | Full (with kind-projector) | N/A                    |
| Rust       | No (use GATs or traits)    | Associated types, GATs |
| TypeScript | No                         | Mapped types, generics |
| Go         | No                         | Code generation        |

---

## Functor Pattern

### Haskell (Native)

```haskell
class Functor f where
  fmap :: (a -> b) -> f a -> f b

instance Functor [] where
  fmap = map

instance Functor Maybe where
  fmap _ Nothing = Nothing
  fmap f (Just x) = Just (f x)
```

### Rust (Trait per Container)

```rust
// Can't abstract over container, so define per-type
trait Mappable {
    type Item;
    type Output<U>;

    fn map<U, F: FnMut(Self::Item) -> U>(self, f: F) -> Self::Output<U>;
}

impl<T> Mappable for Vec<T> {
    type Item = T;
    type Output<U> = Vec<U>;

    fn map<U, F: FnMut(T) -> U>(self, f: F) -> Vec<U> {
        self.into_iter().map(f).collect()
    }
}

impl<T> Mappable for Option<T> {
    type Item = T;
    type Output<U> = Option<U>;

    fn map<U, F: FnMut(T) -> U>(self, f: F) -> Option<U> {
        self.map(f)
    }
}
```

### TypeScript (Per-Type Methods)

```typescript
// No abstraction - each type has its own map
const arr = [1, 2, 3].map((x) => x * 2);
const opt = someOption.map((x) => x * 2);  // If using Option library
```

---

## Monad Pattern

### Haskell (Native)

```haskell
class Monad m where
  return :: a -> m a
  (>>=) :: m a -> (a -> m b) -> m b

-- Do notation is sugar for >>=
result <- computation
-- desugars to:
computation >>= \result -> ...
```

### Rust (? Operator)

```rust
// The ? operator is like monadic bind for Result/Option
fn process() -> Result<Output, Error> {
    let a = step_a()?;  // Like: step_a >>= \a ->
    let b = step_b(a)?;
    Ok(b)
}

// For Option
fn find_user_email(id: &str) -> Option<String> {
    let user = users.get(id)?;
    let profile = user.profile.as_ref()?;
    Some(profile.email.clone())
}
```

### Go (Error Returns)

```go
// Manual chaining
func process() (Output, error) {
    a, err := stepA()
    if err != nil {
        return Output{}, err
    }

    b, err := stepB(a)
    if err != nil {
        return Output{}, err
    }

    return b, nil
}
```

---

## Type Classes

### Common Type Classes

| Haskell | Scala | Rust | Purpose |
|---------|-------|------|---------|
| `Eq` | - | `PartialEq`, `Eq` | Equality |
| `Ord` | `Ordered` | `PartialOrd`, `Ord` | Ordering |
| `Show` | - | `Display`, `Debug` | String representation |
| `Functor` | `Functor` | Per-type `.map()` | Mappable |
| `Applicative` | `Applicative` | - | Apply functions in context |
| `Monad` | `Monad` | `?` operator | Sequential computation |
| `Monoid` | `Monoid` | - | Combine with identity |
| `Foldable` | `Foldable` | `.fold()` | Reduce to single value |

### Scala Type Class Pattern

```scala
// Scala: Type class pattern
trait Show[A] {
  def show(a: A): String
}

object Show {
  implicit val intShow: Show[Int] = (a: Int) => a.toString

  def apply[A](implicit sh: Show[A]): Show[A] = sh
}

def print[A: Show](a: A): Unit =
  println(implicitly[Show[A]].show(a))
```

### Rust Trait (Similar to Type Class)

```rust
trait Show {
    fn show(&self) -> String;
}

impl Show for i32 {
    fn show(&self) -> String { self.to_string() }
}

fn print<T: Show>(a: &T) {
    println!("{}", a.show());
}
```

---

## Applicative Pattern

### Haskell

```haskell
class Functor f => Applicative f where
  pure :: a -> f a
  (<*>) :: f (a -> b) -> f a -> f b

-- Example: Apply function to multiple Options
liftA2 :: Applicative f => (a -> b -> c) -> f a -> f b -> f c
liftA2 f a b = f <$> a <*> b

-- Usage
liftA2 (+) (Just 1) (Just 2)  -- Just 3
liftA2 (+) Nothing (Just 2)   -- Nothing
```

### Rust (Manual)

```rust
// Rust: Manual implementation
fn lift_a2<A, B, C, F>(f: F, a: Option<A>, b: Option<B>) -> Option<C>
where
    F: FnOnce(A, B) -> C,
{
    Some(f(a?, b?))
}

// Usage
lift_a2(|x, y| x + y, Some(1), Some(2))  // Some(3)
lift_a2(|x, y| x + y, None, Some(2))     // None
```

---

## Monoid Pattern

### Haskell

```haskell
class Monoid m where
  mempty :: m              -- Identity element
  mappend :: m -> m -> m   -- Combine (also <>)

instance Monoid [a] where
  mempty = []
  mappend = (++)

-- Fold a list of monoids
mconcat :: Monoid m => [m] -> m
mconcat = foldr mappend mempty
```

### Rust (Default + Add)

```rust
// Rust: Use Default + std::ops::Add or custom trait
trait Monoid: Default {
    fn combine(self, other: Self) -> Self;
}

impl Monoid for String {
    fn combine(self, other: Self) -> Self {
        self + &other
    }
}

fn mconcat<T: Monoid>(items: impl IntoIterator<Item = T>) -> T {
    items.into_iter().fold(T::default(), |acc, x| acc.combine(x))
}
```

---

## Translating HKT Code

### When Converting FROM Haskell/Scala

1. **Identify which HKT abstractions are used**
   - Functor → `.map()` methods
   - Monad → `?` operator (Rust), explicit chaining (Go)
   - Applicative → Manual lifting functions

2. **Accept loss of abstraction**
   - Code will be less generic
   - May need to duplicate logic per container type

3. **Use traits/interfaces for specific behaviors**
   - Can still share behavior, just not container-abstractly

### Example: Generic Validation

```haskell
-- Haskell: Applicative validation
validateUser :: String -> String -> Validation [Error] User
validateUser name email =
  User <$> validateName name <*> validateEmail email
```

```rust
// Rust: Explicit handling (no HKT abstraction)
fn validate_user(name: &str, email: &str) -> Result<User, Vec<Error>> {
    let name_result = validate_name(name);
    let email_result = validate_email(email);

    match (name_result, email_result) {
        (Ok(name), Ok(email)) => Ok(User { name, email }),
        _ => {
            let mut errors = Vec::new();
            if let Err(e) = name_result { errors.extend(e); }
            if let Err(e) = email_result { errors.extend(e); }
            Err(errors)
        }
    }
}
```

---

## GATs (Generic Associated Types) in Rust

Rust's GATs provide some HKT-like capabilities:

```rust
trait Container {
    type Item;
    type Mapped<U>;  // GAT: associated type with generic

    fn map<U, F: FnMut(Self::Item) -> U>(self, f: F) -> Self::Mapped<U>;
}

impl<T> Container for Vec<T> {
    type Item = T;
    type Mapped<U> = Vec<U>;

    fn map<U, F: FnMut(T) -> U>(self, f: F) -> Vec<U> {
        self.into_iter().map(f).collect()
    }
}
```

This allows more abstraction than pre-GAT Rust, but still not full HKT.
