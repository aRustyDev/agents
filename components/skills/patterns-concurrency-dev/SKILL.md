---
name: patterns-concurrency-dev
description: Cross-cutting patterns for concurrency and async programming across languages. Use when translating async/await between languages, converting goroutines to tokio tasks, mapping channel patterns, or designing concurrent code for language conversions.
---

# Concurrency Patterns

Cross-language reference for concurrency mechanisms including async/await, goroutines, channels, threads, and synchronization primitives. This skill helps translate concurrent code between languages during code conversion.

## Overview

**This skill covers:**
- Async/await pattern comparison
- Goroutines, tasks, and green threads
- Channel and message passing patterns
- Synchronization primitives
- Cancellation and timeout patterns

**This skill does NOT cover:**
- Building applications with async frameworks (see `lang-*-dev` skills)
- Distributed systems patterns (see dedicated skills)
- Database connection pooling (see database skills)

---

## Concurrency Model Comparison

| Language | Primary Model | Runtime | Threading | Channels |
|----------|---------------|---------|-----------|----------|
| TypeScript | async/await | V8 event loop | Workers (limited) | N/A |
| Python | async/await | asyncio | threading/multiprocessing | Queue |
| Rust | async/await | tokio/async-std | std::thread | mpsc, crossbeam |
| Go | Goroutines | Go scheduler | Built-in | `chan` (first-class) |
| Java | Virtual Threads | JVM | Thread, ExecutorService | BlockingQueue |
| Elixir | Processes | BEAM | N/A (processes) | Built-in messaging |

### Model Characteristics

```
Event Loop (JS/TS, Python asyncio)
├── Single-threaded by default
├── Non-blocking I/O
├── Cooperative scheduling
└── Cannot utilize multiple cores directly

Goroutines (Go)
├── Multiplexed onto OS threads
├── Preemptive scheduling
├── Built-in channel communication
└── Automatic multi-core utilization

Tokio/async-std (Rust)
├── Multi-threaded runtime
├── Work-stealing scheduler
├── Zero-cost futures
└── Explicit spawning for parallelism

BEAM Processes (Elixir/Erlang)
├── Lightweight isolated processes
├── Message passing only
├── Preemptive scheduling
└── Fault tolerance built-in
```

---

## Async/Await Translation

### Basic Async Function

**TypeScript:**
```typescript
async function fetchUser(id: string): Promise<User> {
  const response = await fetch(`/users/${id}`);
  return response.json();
}
```

**Python:**
```python
async def fetch_user(id: str) -> User:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"/users/{id}")
        return User(**response.json())
```

**Rust:**
```rust
async fn fetch_user(id: &str) -> Result<User, Error> {
    let response = reqwest::get(format!("/users/{}", id)).await?;
    let user: User = response.json().await?;
    Ok(user)
}
```

**Go:**
```go
// Go doesn't have async/await - use goroutines + channels
func fetchUser(id string) (*User, error) {
    resp, err := http.Get(fmt.Sprintf("/users/%s", id))
    if err != nil {
        return nil, err
    }
    defer resp.Body.Close()

    var user User
    err = json.NewDecoder(resp.Body).Decode(&user)
    return &user, err
}
```

---

## Parallel Execution

### Promise.all / join!

**TypeScript:**
```typescript
const [users, orders] = await Promise.all([
  fetchUsers(),
  fetchOrders()
]);
```

**Python:**
```python
import asyncio

users, orders = await asyncio.gather(
    fetch_users(),
    fetch_orders()
)
```

**Rust:**
```rust
let (users, orders) = tokio::join!(
    fetch_users(),
    fetch_orders()
);

// Or with try_join for Result types
let (users, orders) = tokio::try_join!(
    fetch_users(),
    fetch_orders()
)?;
```

**Go:**
```go
var wg sync.WaitGroup
var users []User
var orders []Order
var usersErr, ordersErr error

wg.Add(2)
go func() {
    defer wg.Done()
    users, usersErr = fetchUsers()
}()
go func() {
    defer wg.Done()
    orders, ordersErr = fetchOrders()
}()
wg.Wait()
```

### Race / select

**TypeScript:**
```typescript
const result = await Promise.race([
  fetchFromPrimary(),
  fetchFromBackup()
]);
```

**Python:**
```python
done, pending = await asyncio.wait(
    [fetch_from_primary(), fetch_from_backup()],
    return_when=asyncio.FIRST_COMPLETED
)
result = done.pop().result()
for task in pending:
    task.cancel()
```

**Rust:**
```rust
tokio::select! {
    result = fetch_from_primary() => result,
    result = fetch_from_backup() => result,
}
```

**Go:**
```go
select {
case result := <-primaryCh:
    return result
case result := <-backupCh:
    return result
}
```

---

## Channel Patterns

### Basic Channel Usage

**Go (native channels):**
```go
// Unbuffered channel
ch := make(chan int)

// Send
go func() {
    ch <- 42
}()

// Receive
value := <-ch

// Buffered channel
buffered := make(chan int, 10)
```

**Rust (mpsc):**
```rust
use tokio::sync::mpsc;

// Create channel
let (tx, mut rx) = mpsc::channel(32);

// Send
tokio::spawn(async move {
    tx.send(42).await.unwrap();
});

// Receive
while let Some(value) = rx.recv().await {
    println!("Received: {}", value);
}
```

**Python (asyncio.Queue):**
```python
import asyncio

queue = asyncio.Queue()

# Send
await queue.put(42)

# Receive
value = await queue.get()
```

**TypeScript (no native channels):**
```typescript
// Use a library or implement with EventEmitter/streams
import { Channel } from './channel';

const ch = new Channel<number>();
await ch.send(42);
const value = await ch.receive();
```

### Fan-out / Fan-in

**Go:**
```go
func fanOut(input <-chan int, workers int) []<-chan int {
    outputs := make([]<-chan int, workers)
    for i := 0; i < workers; i++ {
        outputs[i] = worker(input)
    }
    return outputs
}

func fanIn(inputs ...<-chan int) <-chan int {
    output := make(chan int)
    var wg sync.WaitGroup

    for _, input := range inputs {
        wg.Add(1)
        go func(ch <-chan int) {
            defer wg.Done()
            for v := range ch {
                output <- v
            }
        }(input)
    }

    go func() {
        wg.Wait()
        close(output)
    }()

    return output
}
```

**Rust:**
```rust
use tokio::sync::mpsc;
use futures::stream::{self, StreamExt};

async fn fan_out<T: Send + 'static>(
    mut input: mpsc::Receiver<T>,
    workers: usize,
) -> Vec<mpsc::Receiver<T>> {
    // Implementation using multiple channels
}
```

---

## Cancellation Patterns

### Timeout

**TypeScript:**
```typescript
const controller = new AbortController();
const timeout = setTimeout(() => controller.abort(), 5000);

try {
  const result = await fetch(url, { signal: controller.signal });
  clearTimeout(timeout);
  return result;
} catch (err) {
  if (err.name === 'AbortError') {
    throw new Error('Request timed out');
  }
  throw err;
}
```

**Python:**
```python
import asyncio

try:
    result = await asyncio.wait_for(fetch_data(), timeout=5.0)
except asyncio.TimeoutError:
    raise Exception("Request timed out")
```

**Rust:**
```rust
use tokio::time::{timeout, Duration};

match timeout(Duration::from_secs(5), fetch_data()).await {
    Ok(result) => result?,
    Err(_) => return Err(Error::Timeout),
}
```

**Go:**
```go
ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
defer cancel()

result, err := fetchData(ctx)
if err == context.DeadlineExceeded {
    return nil, errors.New("request timed out")
}
```

### Cancellation Token / Context

**Go (Context):**
```go
func worker(ctx context.Context) error {
    for {
        select {
        case <-ctx.Done():
            return ctx.Err()
        default:
            // Do work
        }
    }
}

// Usage
ctx, cancel := context.WithCancel(context.Background())
go worker(ctx)
// Later...
cancel()
```

**Rust (CancellationToken):**
```rust
use tokio_util::sync::CancellationToken;

async fn worker(token: CancellationToken) {
    loop {
        tokio::select! {
            _ = token.cancelled() => {
                return;
            }
            _ = do_work() => {}
        }
    }
}

// Usage
let token = CancellationToken::new();
tokio::spawn(worker(token.clone()));
// Later...
token.cancel();
```

**TypeScript (AbortController):**
```typescript
async function worker(signal: AbortSignal): Promise<void> {
  while (!signal.aborted) {
    await doWork();
  }
}

// Usage
const controller = new AbortController();
worker(controller.signal);
// Later...
controller.abort();
```

---

## Synchronization Primitives

### Mutex

| Language | Type | Usage |
|----------|------|-------|
| TypeScript | N/A (single-threaded) | Use for async coordination |
| Python | `asyncio.Lock` | `async with lock:` |
| Rust | `tokio::sync::Mutex` | `let guard = mutex.lock().await` |
| Go | `sync.Mutex` | `mu.Lock(); defer mu.Unlock()` |

**Rust (async mutex):**
```rust
use tokio::sync::Mutex;
use std::sync::Arc;

let data = Arc::new(Mutex::new(0));

let data_clone = data.clone();
tokio::spawn(async move {
    let mut guard = data_clone.lock().await;
    *guard += 1;
});
```

**Go:**
```go
var mu sync.Mutex
var count int

go func() {
    mu.Lock()
    defer mu.Unlock()
    count++
}()
```

### Semaphore

**Rust:**
```rust
use tokio::sync::Semaphore;
use std::sync::Arc;

let semaphore = Arc::new(Semaphore::new(10)); // Max 10 concurrent

async fn limited_task(sem: Arc<Semaphore>) {
    let _permit = sem.acquire().await.unwrap();
    // Do work - permit released on drop
}
```

**Go:**
```go
// Using buffered channel as semaphore
sem := make(chan struct{}, 10)

func limitedTask() {
    sem <- struct{}{}        // Acquire
    defer func() { <-sem }() // Release
    // Do work
}
```

**Python:**
```python
import asyncio

semaphore = asyncio.Semaphore(10)

async def limited_task():
    async with semaphore:
        # Do work
        pass
```

---

## Translation Patterns

### Goroutine → Tokio Task

```go
// Go
go func() {
    result := doWork()
    resultCh <- result
}()
```

```rust
// Rust
tokio::spawn(async move {
    let result = do_work().await;
    tx.send(result).await.unwrap();
});
```

### Promise → Future

```typescript
// TypeScript
function fetchData(): Promise<Data> {
  return new Promise((resolve, reject) => {
    // ...
  });
}
```

```rust
// Rust
async fn fetch_data() -> Result<Data, Error> {
    // async fn returns impl Future automatically
}

// Or explicitly
fn fetch_data() -> impl Future<Output = Result<Data, Error>> {
    async {
        // ...
    }
}
```

### Callback → Async/Await

```javascript
// JavaScript callback
function fetchData(callback) {
  http.get(url, (res) => {
    callback(null, res);
  }).on('error', callback);
}
```

```typescript
// TypeScript async
async function fetchData(): Promise<Response> {
  return new Promise((resolve, reject) => {
    http.get(url, resolve).on('error', reject);
  });
}
```

---

## Common Pitfalls

### 1. Blocking in Async Context

```rust
// ❌ Blocks the async runtime
async fn bad() {
    std::thread::sleep(Duration::from_secs(1)); // Blocks!
}

// ✓ Use async sleep
async fn good() {
    tokio::time::sleep(Duration::from_secs(1)).await;
}

// ✓ Or spawn_blocking for CPU-bound work
async fn cpu_bound() {
    tokio::task::spawn_blocking(|| {
        heavy_computation()
    }).await.unwrap();
}
```

### 2. Deadlock with Channels

```go
// ❌ Deadlock - unbuffered channel, same goroutine
ch := make(chan int)
ch <- 42    // Blocks forever - no receiver
val := <-ch

// ✓ Use goroutine
ch := make(chan int)
go func() { ch <- 42 }()
val := <-ch
```

### 3. Forgetting to Close Channels

```go
// ❌ Receiver blocks forever
ch := make(chan int)
go func() {
    for i := 0; i < 10; i++ {
        ch <- i
    }
    // Forgot to close!
}()

for v := range ch { // Blocks after 10 values
    fmt.Println(v)
}

// ✓ Close when done
go func() {
    defer close(ch)
    for i := 0; i < 10; i++ {
        ch <- i
    }
}()
```

### 4. Shared State Without Synchronization

```rust
// ❌ Data race
let mut data = vec![];
for i in 0..10 {
    tokio::spawn(async move {
        data.push(i); // Cannot borrow mutably!
    });
}

// ✓ Use Arc<Mutex<T>>
let data = Arc::new(Mutex::new(vec![]));
for i in 0..10 {
    let data = data.clone();
    tokio::spawn(async move {
        data.lock().await.push(i);
    });
}
```

---

## Best Practices

1. **Prefer message passing** over shared state when possible
2. **Use structured concurrency** - parent tasks own child tasks
3. **Always handle cancellation** - provide clean shutdown paths
4. **Avoid blocking** in async contexts
5. **Limit concurrency** with semaphores for resource-intensive operations
6. **Close channels** when done sending
7. **Use timeouts** for all external operations
8. **Test concurrent code** with race detectors (`go test -race`, ThreadSanitizer)

---

## Related Skills

- `meta-convert-dev` - Code conversion patterns
- `patterns-metaprogramming-dev` - Async decorators/macros
- `lang-*-dev` skills - Language-specific concurrency details
