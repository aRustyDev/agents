# Quick Reference Tables

Condensed lookup tables for common conversion patterns.

---

## Type Mapping Quick Reference

### Primitives

| Concept   | Python  | TypeScript       | Rust        | Go        | Elixir     |
| --------- | ------- | ---------------- | ----------- | --------- | ---------- |
| Integer   | `int`   | `number`         | `i32/i64`   | `int`     | `integer`  |
| Float     | `float` | `number`         | `f64`       | `float64` | `float`    |
| Boolean   | `bool`  | `boolean`        | `bool`      | `bool`    | `boolean`  |
| String    | `str`   | `string`         | `String`    | `string`  | `String.t` |
| Char      | -       | -                | `char`      | `rune`    | -          |
| Byte      | `bytes` | `Uint8Array`     | `u8`        | `byte`    | `binary`   |
| None/Null | `None`  | `null/undefined` | `Option<T>` | `nil`     | `nil`      |

### Collections

| Concept       | Python  | TypeScript | Rust           | Go               | Elixir   |
| ------------- | ------- | ---------- | -------------- | ---------------- | -------- |
| Dynamic array | `list`  | `Array<T>` | `Vec<T>`       | `[]T`            | `list`   |
| Fixed array   | -       | `T[]`      | `[T; N]`       | `[N]T`           | `tuple`  |
| Hash map      | `dict`  | `Map<K,V>` | `HashMap<K,V>` | `map[K]V`        | `%{}`    |
| Set           | `set`   | `Set<T>`   | `HashSet<T>`   | `map[T]struct{}` | `MapSet` |
| Tuple         | `tuple` | `[A, B]`   | `(A, B)`       | -                | `{a, b}` |
| Queue         | `deque` | -          | `VecDeque<T>`  | -                | `:queue` |

---

## Error Handling Quick Reference

| Pattern      | Python          | TypeScript      | Rust               | Go              |
| ------------ | --------------- | --------------- | ------------------ | --------------- |
| Throw/Raise  | `raise`         | `throw`         | `panic!`           | `panic`         |
| Try/Catch    | `try/except`    | `try/catch`     | -                  | `recover`       |
| Return error | -               | -               | `Result<T,E>`      | `error` return  |
| Propagate    | `raise`         | `throw`         | `?`                | `if err != nil` |
| Wrap context | -               | -               | `.context()`       | `fmt.Errorf`    |
| Custom error | `class MyError` | `class MyError` | `#[derive(Error)]` | `errors.New`    |

---

## Async Quick Reference

| Pattern      | TypeScript        | Python             | Rust        | Go           |
| ------------ | ----------------- | ------------------ | ----------- | ------------ |
| Define async | `async function`  | `async def`        | `async fn`  | `go func()`  |
| Await        | `await`           | `await`            | `.await`    | channel recv |
| Parallel     | `Promise.all()`   | `gather()`         | `join!`     | WaitGroup    |
| Race         | `Promise.race()`  | `wait(..., FIRST)` | `select!`   | `select`     |
| Channel      | -                 | `asyncio.Queue`    | `mpsc`      | `chan`       |
| Timeout      | `AbortController` | `wait_for()`       | `timeout()` | `context`    |
| Spawn        | -                 | `create_task()`    | `spawn()`   | `go`         |

---

## Memory/Ownership Quick Reference

| Pattern             | GC Languages      | Rust                      |
| ------------------- | ----------------- | ------------------------- |
| Share read-only     | Just pass         | `&T`                      |
| Share mutable       | Just mutate       | `&mut T`                  |
| Transfer ownership  | Implicit copy     | `T` (move)                |
| Keep copy           | Automatic         | `.clone()`                |
| Reference count     | GC handles        | `Rc<T>` / `Arc<T>`        |
| Interior mutability | N/A               | `RefCell<T>` / `Mutex<T>` |
| Weak reference      | Usually automatic | `Weak<T>`                 |

---

## String Operations

| Operation | Python            | JavaScript        | Rust                    |
| --------- | ----------------- | ----------------- | ----------------------- |
| Length    | `len(s)`          | `s.length`        | `s.len()`               |
| Concat    | `a + b`           | `a + b`           | `format!("{}{}", a, b)` |
| Split     | `s.split(",")`    | `s.split(",")`    | `s.split(",")`          |
| Join      | `",".join(lst)`   | `arr.join(",")`   | `v.join(",")`           |
| Trim      | `s.strip()`       | `s.trim()`        | `s.trim()`              |
| Contains  | `x in s`          | `s.includes(x)`   | `s.contains(x)`         |
| Replace   | `s.replace(a, b)` | `s.replace(a, b)` | `s.replace(a, b)`       |
| Uppercase | `s.upper()`       | `s.toUpperCase()` | `s.to_uppercase()`      |
| Slice     | `s[1:4]`          | `s.slice(1, 4)`   | `&s[1..4]`              |

---

## Iterator/Collection Methods

| Operation | Python                | JavaScript     | Rust                    |
| --------- | --------------------- | -------------- | ----------------------- |
| Map       | `map(f, lst)`         | `.map(f)`      | `.iter().map(f)`        |
| Filter    | `filter(f, lst)`      | `.filter(f)`   | `.iter().filter(f)`     |
| Reduce    | `reduce(f, lst)`      | `.reduce(f)`   | `.iter().fold(init, f)` |
| Find      | next(filter(...))     | `.find(f)`     | `.iter().find(f)`       |
| Any       | `any(...)`            | `.some(f)`     | `.iter().any(f)`        |
| All       | `all(...)`            | `.every(f)`    | `.iter().all(f)`        |
| Count     | `len(list(...))`      | `.length`      | `.count()`              |
| Take      | `islice(it, n)`       | `.slice(0, n)` | `.take(n)`              |
| Skip      | `islice(it, n, None)` | `.slice(n)`    | `.skip(n)`              |
| Enumerate | `enumerate(it)`       | `.entries()`   | `.enumerate()`          |
| Zip       | `zip(a, b)`           | -              | `.zip(other)`           |
| Flatten   | `chain.from_iterable` | `.flat()`      | `.flatten()`            |
| Collect   | `list(it)`            | `[...it]`      | `.collect()`            |

---

## Pattern Matching

| Pattern   | Python 3.10+           | Rust                    |
| --------- | ---------------------- | ----------------------- |
| Literal   | `case 1:`              | `1 =>`                  |
| Variable  | `case x:`              | `x =>`                  |
| Wildcard  | `case _:`              | `_ =>`                  |
| OR        | `case 1 \| 2:`         | `1 \| 2 =>`             |
| Guard     | `case x if x > 0:`     | `x if x > 0 =>`         |
| Tuple     | `case (a, b):`         | `(a, b) =>`             |
| Struct    | `case Point(x, y):`    | `Point { x, y } =>`     |
| List head | `case [first, *rest]:` | `[first, rest @ ..] =>` |
| Range     | -                      | `1..=10 =>`             |

---

## Testing Frameworks

| Language   | Framework   | Assert              | Mock            |
| ---------- | ----------- | ------------------- | --------------- |
| Python     | pytest      | `assert x == y`     | `unittest.mock` |
| TypeScript | Jest/Vitest | `expect(x).toBe(y)` | `jest.fn()`     |
| Rust       | built-in    | `assert_eq!(x, y)`  | mockall         |
| Go         | testing     | `if got != want`    | gomock          |
| Elixir     | ExUnit      | `assert x == y`     | Mox             |

---

## Build/Package Commands

| Task         | npm/yarn        | cargo          | go                | mix            |
| ------------ | --------------- | -------------- | ----------------- | -------------- |
| Init         | `npm init`      | `cargo new`    | `go mod init`     | `mix new`      |
| Install deps | `npm install`   | `cargo build`  | `go mod download` | `mix deps.get` |
| Add dep      | `npm install x` | `cargo add x`  | `go get x`        | add to mix.exs |
| Build        | `npm run build` | `cargo build`  | `go build`        | `mix compile`  |
| Test         | `npm test`      | `cargo test`   | `go test`         | `mix test`     |
| Run          | `npm start`     | `cargo run`    | `go run .`        | `mix run`      |
| Format       | `prettier`      | `cargo fmt`    | `gofmt`           | `mix format`   |
| Lint         | `eslint`        | `cargo clippy` | `golint`          | `mix credo`    |

---

## Common Library Equivalents

| Category    | Python         | TypeScript  | Rust        | Go            |
| ----------- | -------------- | ----------- | ----------- | ------------- |
| HTTP Client | requests       | axios/fetch | reqwest     | net/http      |
| JSON        | json           | built-in    | serde_json  | encoding/json |
| CLI         | argparse/click | commander   | clap        | cobra/flag    |
| Logging     | logging        | winston     | tracing     | log/slog      |
| Date/Time   | datetime       | date-fns    | chrono      | time          |
| ORM         | sqlalchemy     | prisma      | diesel/sqlx | gorm          |
| Validation  | pydantic       | zod         | validator   | validator     |
| Async       | asyncio        | built-in    | tokio       | goroutines    |
| Testing     | pytest         | jest        | built-in    | testing       |
| Env vars    | dotenv         | dotenv      | dotenvy     | godotenv      |

---

## Null/None Handling Cheatsheet

| Operation           | TypeScript       | Rust                                        |
| ------------------- | ---------------- | ------------------------------------------- |
| Check exists        | `x !== null`     | `x.is_some()`                               |
| Default             | `x ?? default`   | `x.unwrap_or(default)`                      |
| Default lazy        | `x ?? compute()` | `x.unwrap_or_else(\|\| compute())`          |
| Map if exists       | `x?.method()`    | `x.map(\|v\| v.method())`                   |
| Chain               | `a?.b?.c`        | `a.and_then(\|a\| a.b).and_then(\|b\| b.c)` |
| Panic if none       | `x!`             | `x.unwrap()`                                |
| Expect with msg     | -                | `x.expect("msg")`                           |
| Convert null→Option | -                | `Option::from(nullable)`                    |
| Option→null         | -                | `opt.unwrap_or(null)`                       |

---

## Lifetime Cheatsheet (Rust)

| Annotation | Meaning           | Use When                         |
| ---------- | ----------------- | -------------------------------- |
| `'a`       | Generic lifetime  | Multiple refs with same lifetime |
| `'static`  | Lives forever     | String literals, leaked data     |
| `'_`       | Elided lifetime   | Compiler can infer               |
| `&T`       | Shared reference  | Read-only access                 |
| `&mut T`   | Mutable reference | Exclusive write access           |
| `T`        | Owned             | Transfer ownership               |

### Common Patterns

```rust
// Return reference from single input
fn first(s: &str) -> &str

// Return reference tied to self
fn get(&self) -> &T

// Return reference tied to specific input
fn longer<'a>(a: &'a str, b: &'a str) -> &'a str

// Struct holding reference
struct Holder<'a> { data: &'a str }
```
