# Concurrency Examples

Code examples showing concurrency pattern translation between languages.

---

## Promise/Future Translation

### TypeScript Promise → Multiple Languages

```typescript
// TypeScript: Promise-based
async function fetchUser(id: string): Promise<User> {
  const response = await fetch(`/users/${id}`);
  return response.json();
}
```

```rust
// Rust: Future-based (with tokio)
async fn fetch_user(id: &str) -> Result<User, reqwest::Error> {
    let user = reqwest::get(format!("/users/{}", id))
        .await?
        .json::<User>()
        .await?;
    Ok(user)
}
```

```go
// Go: goroutine with channel
func fetchUser(id string) <-chan UserResult {
    ch := make(chan UserResult, 1)
    go func() {
        resp, err := http.Get(fmt.Sprintf("/users/%s", id))
        if err != nil {
            ch <- UserResult{Err: err}
            return
        }
        defer resp.Body.Close()
        var user User
        json.NewDecoder(resp.Body).Decode(&user)
        ch <- UserResult{User: user}
    }()
    return ch
}
```

```python
# Python: asyncio
async def fetch_user(id: str) -> User:
    async with aiohttp.ClientSession() as session:
        async with session.get(f"/users/{id}") as response:
            return await response.json()
```

```elixir
# Elixir: Task-based async
def fetch_user(id) do
  Task.async(fn ->
    case HTTPoison.get("http://api/users/#{id}") do
      {:ok, %{status_code: 200, body: body}} ->
        {:ok, Jason.decode!(body)}
      {:error, reason} ->
        {:error, reason}
    end
  end)
  |> Task.await(5000)
end
```

```erlang
%% Erlang: spawned process with message passing
fetch_user(Id) ->
    Self = self(),
    spawn(fun() ->
        case httpc:request(get, {"http://api/users/" ++ Id, []}, [], []) of
            {ok, {{_, 200, _}, _, Body}} ->
                Self ! {user, jsx:decode(Body)};
            {error, Reason} ->
                Self ! {error, Reason}
        end
    end),
    receive
        {user, User} -> {ok, User};
        {error, Reason} -> {error, Reason}
    after 5000 ->
        {error, timeout}
    end.
```

---

## Parallel Execution

### Promise.all Equivalent

```typescript
// TypeScript: Promise.all
const [users, orders] = await Promise.all([fetchUsers(), fetchOrders()]);
```

```rust
// Rust: tokio::join!
let (users, orders) = tokio::join!(
    fetch_users(),
    fetch_orders()
);

// Or with try_join! for Result types
let (users, orders) = tokio::try_join!(
    fetch_users(),
    fetch_orders()
)?;
```

```go
// Go: goroutines with WaitGroup
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

if usersErr != nil || ordersErr != nil {
    // handle errors
}
```

```python
# Python: asyncio.gather
users, orders = await asyncio.gather(
    fetch_users(),
    fetch_orders()
)
```

```elixir
# Elixir: Task.async_stream or parallel tasks
tasks = [
  Task.async(fn -> fetch_users() end),
  Task.async(fn -> fetch_orders() end)
]

[users, orders] = Task.await_many(tasks)
```

---

## Racing / First to Complete

```typescript
// TypeScript: Promise.race
const result = await Promise.race([
  fetchFromPrimary(),
  fetchFromBackup(),
  timeout(5000),
]);
```

```rust
// Rust: tokio::select!
let result = tokio::select! {
    r = fetch_from_primary() => r,
    r = fetch_from_backup() => r,
    _ = tokio::time::sleep(Duration::from_secs(5)) => {
        Err(Error::Timeout)
    }
};
```

```go
// Go: select with channels
select {
case result := <-primaryChan:
    return result, nil
case result := <-backupChan:
    return result, nil
case <-time.After(5 * time.Second):
    return nil, errors.New("timeout")
}
```

```elixir
# Elixir: Task with timeout
task = Task.async(fn -> fetch_data() end)
case Task.yield(task, 5000) || Task.shutdown(task) do
  {:ok, result} -> {:ok, result}
  nil -> {:error, :timeout}
end
```

---

## Channel Patterns

### Producer-Consumer

```go
// Go: channel-based producer-consumer
func producer(ch chan<- int) {
    for i := 0; i < 100; i++ {
        ch <- i
    }
    close(ch)
}

func consumer(ch <-chan int) {
    for value := range ch {
        process(value)
    }
}

func main() {
    ch := make(chan int, 10)
    go producer(ch)
    consumer(ch)
}
```

```rust
// Rust: tokio mpsc channel
use tokio::sync::mpsc;

async fn producer(tx: mpsc::Sender<i32>) {
    for i in 0..100 {
        tx.send(i).await.unwrap();
    }
}

async fn consumer(mut rx: mpsc::Receiver<i32>) {
    while let Some(value) = rx.recv().await {
        process(value).await;
    }
}

#[tokio::main]
async fn main() {
    let (tx, rx) = mpsc::channel(10);
    tokio::spawn(producer(tx));
    consumer(rx).await;
}
```

```elixir
# Elixir: GenServer as producer-consumer
defmodule Producer do
  use GenServer

  def start_link(_), do: GenServer.start_link(__MODULE__, [], name: __MODULE__)
  def produce(item), do: GenServer.cast(__MODULE__, {:produce, item})

  @impl true
  def init(_), do: {:ok, :queue.new()}

  @impl true
  def handle_cast({:produce, item}, queue) do
    {:noreply, :queue.in(item, queue)}
  end

  @impl true
  def handle_call(:consume, _from, queue) do
    case :queue.out(queue) do
      {{:value, item}, new_queue} -> {:reply, {:ok, item}, new_queue}
      {:empty, queue} -> {:reply, :empty, queue}
    end
  end
end
```

---

## Mutex / Locking

### Shared State Protection

```typescript
// TypeScript: no native mutex, use locks library or avoid
import { Mutex } from "async-mutex";

const mutex = new Mutex();
let counter = 0;

async function increment() {
  const release = await mutex.acquire();
  try {
    counter++;
  } finally {
    release();
  }
}
```

```rust
// Rust: Mutex
use std::sync::{Arc, Mutex};

let counter = Arc::new(Mutex::new(0));

// In each thread/task
let counter = Arc::clone(&counter);
tokio::spawn(async move {
    let mut guard = counter.lock().unwrap();
    *guard += 1;
});
```

```go
// Go: sync.Mutex
var mu sync.Mutex
var counter int

func increment() {
    mu.Lock()
    defer mu.Unlock()
    counter++
}
```

```python
# Python: asyncio.Lock
import asyncio

lock = asyncio.Lock()
counter = 0

async def increment():
    global counter
    async with lock:
        counter += 1
```

```elixir
# Elixir: Agent for simple state
{:ok, counter} = Agent.start_link(fn -> 0 end)

Agent.update(counter, &(&1 + 1))
Agent.get(counter, & &1)
```

---

## Worker Pool

```typescript
// TypeScript: p-limit for concurrency control
import pLimit from "p-limit";

const limit = pLimit(5); // 5 concurrent workers

const results = await Promise.all(
  items.map((item) => limit(() => processItem(item))),
);
```

```rust
// Rust: tokio semaphore or buffer_unordered
use futures::stream::{self, StreamExt};

let results: Vec<_> = stream::iter(items)
    .map(|item| process_item(item))
    .buffer_unordered(5)  // 5 concurrent
    .collect()
    .await;
```

```go
// Go: worker pool with semaphore
sem := make(chan struct{}, 5)  // 5 workers
results := make(chan Result, len(items))

for _, item := range items {
    sem <- struct{}{}  // acquire
    go func(item Item) {
        defer func() { <-sem }()  // release
        results <- processItem(item)
    }(item)
}

// Collect results
for i := 0; i < len(items); i++ {
    result := <-results
    // handle result
}
```

```elixir
# Elixir: Task.async_stream with max_concurrency
items
|> Task.async_stream(&process_item/1, max_concurrency: 5)
|> Enum.to_list()
```

---

## Cancellation

```typescript
// TypeScript: AbortController
async function fetchWithTimeout(url: string, ms: number): Promise<Response> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), ms);
  try {
    return await fetch(url, { signal: controller.signal });
  } finally {
    clearTimeout(timeout);
  }
}
```

```rust
// Rust: tokio select for cancellation
use tokio::time::{timeout, Duration};

async fn fetch_with_timeout(url: &str, ms: u64) -> Result<Response, Error> {
    timeout(Duration::from_millis(ms), reqwest::get(url))
        .await
        .map_err(|_| Error::Timeout)?
        .map_err(Error::Request)
}

// Or explicit select
tokio::select! {
    result = fetch(url) => result,
    _ = tokio::time::sleep(duration) => Err(Error::Timeout),
}
```

```go
// Go: Context for cancellation
func fetchWithTimeout(url string, timeout time.Duration) (*http.Response, error) {
    ctx, cancel := context.WithTimeout(context.Background(), timeout)
    defer cancel()

    req, _ := http.NewRequestWithContext(ctx, "GET", url, nil)
    return http.DefaultClient.Do(req)
}
```

```python
# Python: asyncio.wait_for
async def fetch_with_timeout(url: str, timeout: float):
    try:
        return await asyncio.wait_for(fetch(url), timeout=timeout)
    except asyncio.TimeoutError:
        raise TimeoutError(f"Request to {url} timed out")
```

```elixir
# Elixir: Task with timeout
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
