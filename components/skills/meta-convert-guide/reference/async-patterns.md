# Async Pattern Reference (Deep Dive)

Advanced async patterns including cancellation, streams, and structured concurrency.

---

## Runtime Comparison

| Aspect       | JS/TS           | Python                 | Go                   | Rust               |
|--------------|-----------------|------------------------|----------------------|--------------------|
| Runtime      | V8 event loop   | asyncio event loop     | Go scheduler         | tokio/async-std    |
| Default      | Single-threaded | Single-threaded        | Multi-threaded       | Multi-threaded     |
| Blocking     | Never block!    | Never block!           | Goroutines can block | Use spawn_blocking |
| Cancellation | AbortController | asyncio.CancelledError | Context              | Drop / select!     |

---

## Cancellation Patterns

### TypeScript: AbortController

```typescript
async function fetchWithTimeout(url: string, ms: number): Promise<Response> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), ms);
  try {
    return await fetch(url, { signal: controller.signal });
  } finally {
    clearTimeout(timeout);
  }
}

// Manual cancellation
const controller = new AbortController();
startFetch(controller.signal);
// Later:
controller.abort();  // Cancels the fetch
```

### Rust: tokio select!

```rust
use tokio::time::{timeout, Duration};

// Timeout wrapper
async fn fetch_with_timeout(url: &str, ms: u64) -> Result<Response, Error> {
    timeout(Duration::from_millis(ms), reqwest::get(url))
        .await
        .map_err(|_| Error::Timeout)?
        .map_err(Error::Request)
}

// Explicit select for multiple cancellation sources
async fn fetch_cancellable(
    url: &str,
    cancel: tokio::sync::oneshot::Receiver<()>
) -> Result<Response, Error> {
    tokio::select! {
        result = reqwest::get(url) => result.map_err(Error::Request),
        _ = cancel => Err(Error::Cancelled),
    }
}
```

### Go: Context

```go
func fetchWithTimeout(url string, timeout time.Duration) (*http.Response, error) {
    ctx, cancel := context.WithTimeout(context.Background(), timeout)
    defer cancel()

    req, err := http.NewRequestWithContext(ctx, "GET", url, nil)
    if err != nil {
        return nil, err
    }
    return http.DefaultClient.Do(req)
}

// Propagate cancellation
func handler(ctx context.Context) error {
    // Pass context to all operations
    result, err := doWork(ctx)
    if err == context.Canceled {
        return nil  // Clean shutdown
    }
    return err
}
```

### Python: asyncio cancellation

```python
import asyncio

async def fetch_with_timeout(url: str, timeout: float):
    try:
        return await asyncio.wait_for(fetch(url), timeout=timeout)
    except asyncio.TimeoutError:
        raise TimeoutError(f"Request to {url} timed out")

# Manual cancellation
task = asyncio.create_task(long_running())
# Later:
task.cancel()
try:
    await task
except asyncio.CancelledError:
    print("Task was cancelled")
```

### Elixir: Task shutdown

```elixir
def fetch_with_timeout(url, timeout_ms) do
  task = Task.async(fn -> fetch(url) end)
  case Task.yield(task, timeout_ms) do
    {:ok, result} -> {:ok, result}
    nil ->
      Task.shutdown(task, :brutal_kill)
      {:error, :timeout}
  end
end
```

---

## Stream / Async Iterator Patterns

### TypeScript: AsyncIterable

```typescript
async function* fetchPages(baseUrl: string): AsyncIterable<Page> {
  let page = 1;
  while (true) {
    const response = await fetch(`${baseUrl}?page=${page}`);
    if (!response.ok) break;
    yield await response.json();
    page++;
  }
}

// Consuming
for await (const page of fetchPages(url)) {
  process(page);
}
```

### Rust: Stream

```rust
use futures::stream::{self, Stream, StreamExt};

fn fetch_pages(base_url: &str) -> impl Stream<Item = Page> {
    stream::unfold(1, move |page| async move {
        let url = format!("{}?page={}", base_url, page);
        match reqwest::get(&url).await {
            Ok(resp) if resp.status().is_success() => {
                let data: Page = resp.json().await.ok()?;
                Some((data, page + 1))
            }
            _ => None,
        }
    })
}

// Consuming
let mut pages = fetch_pages(url);
while let Some(page) = pages.next().await {
    process(page);
}

// Or with stream combinators
fetch_pages(url)
    .filter(|p| async { p.has_content() })
    .take(10)
    .for_each(|p| async { process(p) })
    .await;
```

### Python: Async Generator

```python
async def fetch_pages(base_url: str):
    page = 1
    while True:
        response = await fetch(f"{base_url}?page={page}")
        if not response.ok:
            break
        yield await response.json()
        page += 1

# Consuming
async for page in fetch_pages(url):
    process(page)
```

### Go: Channel-based Stream

```go
func fetchPages(baseUrl string) <-chan Page {
    ch := make(chan Page)
    go func() {
        defer close(ch)
        page := 1
        for {
            resp, err := http.Get(fmt.Sprintf("%s?page=%d", baseUrl, page))
            if err != nil || resp.StatusCode != 200 {
                return
            }
            var p Page
            json.NewDecoder(resp.Body).Decode(&p)
            resp.Body.Close()
            ch <- p
            page++
        }
    }()
    return ch
}

// Consuming
for page := range fetchPages(url) {
    process(page)
}
```

---

## Structured Concurrency

### Concept

All spawned tasks complete before parent completes. No orphaned tasks.

### Go: errgroup

```go
import "golang.org/x/sync/errgroup"

func processAll(ctx context.Context, items []Item) error {
    g, ctx := errgroup.WithContext(ctx)

    for _, item := range items {
        item := item  // Capture for closure
        g.Go(func() error {
            return process(ctx, item)
        })
    }

    return g.Wait()  // Waits for all, returns first error
}
```

### Rust: tokio JoinSet

```rust
use tokio::task::JoinSet;

async fn process_all(items: Vec<Item>) -> Result<Vec<Output>, Error> {
    let mut set = JoinSet::new();

    for item in items {
        set.spawn(async move { process(item).await });
    }

    let mut results = Vec::new();
    while let Some(result) = set.join_next().await {
        results.push(result??);
    }
    Ok(results)
}
```

### Python: TaskGroup (3.11+)

```python
async def process_all(items: list[Item]) -> list[Output]:
    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(process(item)) for item in items]
    return [task.result() for task in tasks]
```

---

## Backpressure Patterns

### Bounded Channels

```rust
// Rust: Bounded channel
let (tx, rx) = tokio::sync::mpsc::channel(100);  // Max 100 buffered

// Sender blocks when buffer full
tx.send(item).await?;  // Waits if buffer full
```

```go
// Go: Buffered channel
ch := make(chan Item, 100)  // Max 100 buffered

// Sender blocks when buffer full
ch <- item  // Blocks if buffer full
```

### Rate Limiting

```rust
// Rust: Rate limiting with governor
use governor::{Quota, RateLimiter};

let limiter = RateLimiter::direct(Quota::per_second(10));

for item in items {
    limiter.until_ready().await;  // Wait for permit
    process(item).await;
}
```

---

## Parallel vs Concurrent

| Pattern | Use Case | TypeScript | Rust | Go |
|---------|----------|------------|------|-----|
| Concurrent | I/O bound | `Promise.all` | `join!` | Goroutines |
| Parallel | CPU bound | Web Workers | `rayon` | Goroutines |

### CPU-Bound Parallelism

```rust
// Rust: rayon for CPU-bound parallel work
use rayon::prelude::*;

let results: Vec<_> = items
    .par_iter()
    .map(|item| cpu_intensive_work(item))
    .collect();
```

```go
// Go: Goroutines work for both
var wg sync.WaitGroup
results := make([]Result, len(items))

for i, item := range items {
    wg.Add(1)
    go func(i int, item Item) {
        defer wg.Done()
        results[i] = cpuIntensiveWork(item)
    }(i, item)
}
wg.Wait()
```

---

## Error Handling in Async

### Collecting All Errors

```rust
// Rust: Collect successes, log failures
let results: Vec<_> = futures::future::join_all(
    items.into_iter().map(|item| async move {
        process(item).await
    })
).await;

let (successes, failures): (Vec<_>, Vec<_>) = results
    .into_iter()
    .partition(Result::is_ok);

let successes: Vec<_> = successes.into_iter()
    .filter_map(Result::ok)
    .collect();

for err in failures.into_iter().filter_map(Result::err) {
    log::error!("Failed: {}", err);
}
```

### Fail Fast

```rust
// Rust: Stop on first error
use futures::TryStreamExt;

let results = futures::stream::iter(items)
    .map(|item| process(item))
    .buffer_unordered(10)
    .try_collect::<Vec<_>>()
    .await?;  // Returns first error
```

```go
// Go: errgroup fails fast
g, ctx := errgroup.WithContext(ctx)
for _, item := range items {
    item := item
    g.Go(func() error {
        return process(ctx, item)  // Context cancelled on first error
    })
}
return g.Wait()  // Returns first error
```
