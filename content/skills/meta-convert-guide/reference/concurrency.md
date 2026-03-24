# Concurrency Reference

Comprehensive reference for concurrency model translation.

---

## Model Comparison

| Language   | Async Model             | Threading                  | Channels                |
|------------|-------------------------|----------------------------|-------------------------|
| TypeScript | `async/await`, Promises | Web Workers (limited)      | -                       |
| Python     | `async/await`, asyncio  | Threading, multiprocessing | Queue                   |
| Go         | Goroutines              | Built-in                   | `chan` (first-class)    |
| Rust       | `async/await`, Futures  | std::thread                | mpsc, crossbeam         |
| Erlang     | Processes (lightweight) | BEAM scheduler             | Mailboxes (first-class) |
| Elixir     | Tasks, GenServer        | BEAM scheduler             | Mailboxes, Agent        |
| Clojure    | core.async, Agents      | JVM threads                | CSP channels            |
| Haskell    | async, STM              | forkIO, threads            | MVar, TVar, Chan        |

---

## Async Runtime Comparison

| Aspect       | JS/TS           | Python                 | Go                   | Rust               |
|--------------|-----------------|------------------------|----------------------|-------------------|
| Runtime      | V8 event loop   | asyncio event loop     | Go scheduler         | tokio/async-std    |
| Default      | Single-threaded | Single-threaded        | Multi-threaded       | Multi-threaded     |
| Blocking     | Never block!    | Never block!           | Goroutines can block | Use spawn_blocking |
| Cancellation | AbortController | asyncio.CancelledError | Context              | Drop / select!     |

---

## Pattern Mappings

### Basic Async

| Pattern | TypeScript | Rust | Go | Python |
|---------|------------|------|-----|--------|
| Define async | `async function f()` | `async fn f()` | `go func()` | `async def f()` |
| Await | `await promise` | `future.await` | Channel receive | `await coro` |
| Create task | - | `tokio::spawn()` | `go func()` | `asyncio.create_task()` |
| Parallel | `Promise.all()` | `tokio::join!()` | WaitGroup | `asyncio.gather()` |
| Race | `Promise.race()` | `tokio::select!` | `select {}` | `asyncio.wait(..., FIRST_COMPLETED)` |

### Channel Patterns

| Pattern | Go | Rust | Elixir | Clojure |
|---------|-----|------|--------|---------|
| Create | `make(chan T)` | `mpsc::channel()` | Process mailbox | `(chan)` |
| Send | `ch <- val` | `tx.send(val)` | `send(pid, msg)` | `(>! ch val)` |
| Receive | `<-ch` | `rx.recv()` | `receive do` | `(<! ch)` |
| Buffered | `make(chan T, n)` | `mpsc::channel(n)` | N/A | `(chan n)` |
| Close | `close(ch)` | Drop sender | N/A | `(close! ch)` |

---

## Process-Based Concurrency (BEAM)

### GenServer Pattern

```elixir
defmodule Counter do
  use GenServer

  # Client API
  def start_link(initial), do: GenServer.start_link(__MODULE__, initial, name: __MODULE__)
  def increment, do: GenServer.cast(__MODULE__, :increment)
  def get, do: GenServer.call(__MODULE__, :get)

  # Server Callbacks
  @impl true
  def init(initial), do: {:ok, initial}

  @impl true
  def handle_cast(:increment, count), do: {:noreply, count + 1}

  @impl true
  def handle_call(:get, _from, count), do: {:reply, count, count}
end
```

### Translation to Other Languages

| GenServer Concept | Rust | Go | Clojure |
|-------------------|------|-----|---------|
| Process | Actor (actix) | Goroutine | core.async go block |
| State | Arc<Mutex<T>> | Struct + mutex | Atom/Agent |
| Call (sync) | Channel + response | Channel pair | (async/<!! ...) |
| Cast (async) | Channel (no response) | Channel | (go (>! ...)) |
| Supervision | Manual restart logic | errgroup | component |

---

## Synchronization Primitives

| Primitive | Rust | Go | Python | Purpose |
|-----------|------|-----|--------|---------|
| Mutex | `Mutex<T>` | `sync.Mutex` | `threading.Lock` | Exclusive access |
| RWLock | `RwLock<T>` | `sync.RWMutex` | `threading.RLock` | Read-heavy workloads |
| Semaphore | `tokio::sync::Semaphore` | `chan struct{}` | `asyncio.Semaphore` | Limit concurrency |
| Barrier | `std::sync::Barrier` | `sync.WaitGroup` | `threading.Barrier` | Wait for all |
| Once | `std::sync::Once` | `sync.Once` | - | One-time init |
| Condition | `std::sync::Condvar` | `sync.Cond` | `threading.Condition` | Wait for condition |

---

## Shared State Strategies

### Single-Threaded (No Sync Needed)

| Language | Pattern |
|----------|---------|
| TypeScript | Regular objects (event loop is single-threaded) |
| Python (asyncio) | Regular objects (await points are cooperative) |

### Multi-Threaded

| Pattern | Rust | Go |
|---------|------|-----|
| Shared immutable | `Arc<T>` | Pointer to immutable |
| Shared mutable | `Arc<Mutex<T>>` | Pointer + `sync.Mutex` |
| Per-thread | `thread_local!` | goroutine-local |
| Message passing | Channels | Channels |

---

## Parallel Execution Patterns

### Map-Reduce Style

| Language | Pattern |
|----------|---------|
| Rust | `rayon::par_iter().map().reduce()` |
| Go | Goroutines + channels + WaitGroup |
| Python | `concurrent.futures.ProcessPoolExecutor` |
| Elixir | `Task.async_stream()` |

### Worker Pool

| Language | Pattern |
|----------|---------|
| TypeScript | `p-limit` library |
| Rust | `buffer_unordered(n)` on stream |
| Go | Buffered channel as semaphore |
| Python | `asyncio.Semaphore` |
| Elixir | `Task.async_stream(..., max_concurrency: n)` |

---

## Cancellation Strategies

| Language | Mechanism | Scope |
|----------|-----------|-------|
| TypeScript | `AbortController` | Per-request |
| Python | `asyncio.CancelledError` | Per-task |
| Go | `context.Context` | Request tree |
| Rust | Drop + `select!` | Per-future |
| Elixir | `Task.shutdown/2` | Per-task |

### Go Context Propagation

```go
func handler(w http.ResponseWriter, r *http.Request) {
    ctx := r.Context()

    // Pass context down
    result, err := doWork(ctx)
    if err == context.Canceled {
        return // Client disconnected
    }
}

func doWork(ctx context.Context) (Result, error) {
    select {
    case <-ctx.Done():
        return Result{}, ctx.Err()
    case result := <-workChan:
        return result, nil
    }
}
```

### Rust Select

```rust
tokio::select! {
    result = do_work() => {
        handle_result(result)
    }
    _ = shutdown_signal.recv() => {
        // Graceful shutdown
        return;
    }
}
```

---

## Async Streams

| Language | Type | Create | Consume |
|----------|------|--------|---------|
| TypeScript | `AsyncIterable<T>` | `async function*` | `for await` |
| Rust | `Stream<Item=T>` | `stream::unfold` | `while let Some(x) = s.next().await` |
| Python | `AsyncIterator` | `async def` with `yield` | `async for` |
| Go | `<-chan T` | Goroutine + channel | `for v := range ch` |

---

## Common Pitfalls

| Issue | Symptom | Solution |
|-------|---------|----------|
| Deadlock | Program hangs | Consistent lock ordering, timeouts |
| Data race | Inconsistent data | Use proper synchronization |
| Starvation | Some tasks never run | Fair scheduling, priorities |
| Blocking in async | Poor throughput | `spawn_blocking`, separate threads |
| Channel leak | Memory growth | Ensure senders close channels |
