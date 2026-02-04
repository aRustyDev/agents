# BEAM/Actor Family

> Languages running on the Erlang VM (BEAM) emphasizing fault tolerance, distribution, and the actor model.

## Overview

The BEAM family includes languages designed for building highly concurrent, fault-tolerant, distributed systems:

- **Actor model** - Lightweight isolated processes communicating via messages
- **Fault tolerance** - "Let it crash" philosophy with supervision trees
- **Hot code reloading** - Update running systems without downtime
- **Distribution** - Built-in support for distributed computing
- **Soft real-time** - Predictable latency through preemptive scheduling

The BEAM VM (Bogdan's Erlang Abstract Machine) provides unique guarantees that don't exist in other runtimes.

## Subtypes

| Subtype | Description | Languages |
|---------|-------------|-----------|
| **core** | Direct BEAM languages with native actor primitives | Erlang, Elixir, Gleam |

All BEAM languages share the same runtime characteristics but differ in syntax and features.

### Language Comparison

| Aspect | Erlang | Elixir | Gleam |
|--------|--------|--------|-------|
| Syntax | Prolog-like | Ruby-like | Rust-like |
| Typing | Dynamic | Dynamic | Static |
| Macros | Limited | Hygienic | None |
| Metaprogramming | Limited | Extensive | None |
| OTP integration | Native | Native (via wrappers) | Native |

## Key Characteristics

- **Lightweight processes** - Millions of processes per VM
- **Process isolation** - No shared memory between processes
- **Message passing** - Async communication via mailboxes
- **Supervision trees** - Hierarchical fault recovery
- **Per-process GC** - No global GC pauses
- **Pattern matching** - Primary control flow mechanism
- **Immutable data** - All data is immutable
- **Binary handling** - Efficient binary pattern matching

## Languages in Family

| Language | Typing | Platform | Notes |
|----------|--------|----------|-------|
| Erlang | dynamic | BEAM | Original language, Prolog-influenced |
| Elixir | dynamic | BEAM | Modern syntax, macros, tooling |
| Gleam | static | BEAM/JS | Type-safe, no runtime errors from types |
| LFE | dynamic | BEAM | Lisp syntax on BEAM |

## Type System

### Erlang/Elixir (Dynamic)

- **Runtime typing** - Checked during execution
- **Dialyzer** - Success typing static analysis
- **Typespecs** - Documentation and analysis annotations
- **Guards** - Runtime type constraints

```erlang
%% Erlang typespec
-spec add(integer(), integer()) -> integer().
add(A, B) -> A + B.
```

```elixir
# Elixir typespec
@spec add(integer(), integer()) :: integer()
def add(a, b), do: a + b
```

### Gleam (Static)

- **Hindley-Milner inference** - Full type inference
- **No runtime type errors** - Types eliminated at compile time
- **Parametric polymorphism** - Generics

```gleam
// Gleam with static types
fn add(a: Int, b: Int) -> Int {
  a + b
}
```

## Memory Model

- **Per-process heap** - Each process has isolated memory
- **Per-process GC** - No global stop-the-world
- **Binary sharing** - Large binaries shared across processes
- **Immutable data** - No in-place mutation
- **Copy on send** - Data copied when sent between processes (except large binaries)

### Memory Characteristics

| Feature | Benefit |
|---------|---------|
| Process isolation | Fault containment |
| Per-process GC | Predictable latency |
| Binary refcounting | Efficient large data |
| ETS tables | Shared mutable storage (carefully) |

## Concurrency Model

### Actor Model (Processes)

```elixir
# Spawn a process
pid = spawn(fn ->
  receive do
    {:hello, sender} -> send(sender, :world)
  end
end)

# Send a message
send(pid, {:hello, self()})

# Receive response
receive do
  :world -> IO.puts("Got world!")
end
```

### OTP Behaviors

| Behavior | Purpose |
|----------|---------|
| GenServer | Generic server (request-response) |
| GenStateMachine | Finite state machines |
| Supervisor | Process supervision |
| Application | Application lifecycle |

### Supervision Trees

```elixir
# Supervisor with restart strategies
children = [
  {Worker, arg1},
  {AnotherWorker, arg2}
]

Supervisor.start_link(children, strategy: :one_for_one)
```

Strategies: `:one_for_one`, `:one_for_all`, `:rest_for_one`

## Common Patterns

### Pattern Matching in Receive

```elixir
def handle_message do
  receive do
    {:add, a, b} -> a + b
    {:multiply, a, b} -> a * b
    :stop -> :ok
    _ -> handle_message()  # Ignore unknown
  end
end
```

### GenServer

```elixir
defmodule Counter do
  use GenServer

  def start_link(initial), do: GenServer.start_link(__MODULE__, initial)
  def increment(pid), do: GenServer.call(pid, :increment)

  @impl true
  def init(count), do: {:ok, count}

  @impl true
  def handle_call(:increment, _from, count), do: {:reply, count + 1, count + 1}
end
```

### Pipeline Operator (Elixir)

```elixir
result = data
  |> parse()
  |> validate()
  |> transform()
  |> persist()
```

## Conversion Considerations

### Converting FROM BEAM

**What's easy to preserve:**

- Pure functional logic
- Pattern matching (many targets support it)
- Immutable data patterns
- Pipeline transformations

**What's hard to translate:**

- Actor model → no direct equivalent in most languages
- Supervision trees → must implement manually
- Hot code reloading → not portable
- Process isolation → thread safety concerns
- Message passing → shared memory or queues
- Per-process state → global or thread-local state

**Common pitfalls:**

- Losing fault isolation guarantees
- Converting processes to threads (different semantics)
- Ignoring backpressure in message conversion

**Semantic gaps:**

- BEAM → ML-FP: 36 gaps (actor model, process state)
- BEAM → any: Loss of fault tolerance model

### Converting TO BEAM

**What maps naturally:**

- Functional code → pure functions
- State machines → GenStateMachine
- Event handlers → GenServer
- Worker pools → process pools

**What requires restructuring:**

- Shared mutable state → process state or ETS
- Threads with locks → actor message passing
- Object methods → GenServer calls
- Global state → application environment or process registry

**Idiomatic patterns to target:**

- Use processes for isolation
- Let it crash (don't over-handle errors)
- Supervision for fault tolerance
- Pattern matching for control flow
- Pipeline operator for data transformation

**Anti-patterns to avoid:**

- Single "god" process doing everything
- Synchronous calls everywhere (use casts)
- Ignoring OTP behaviors
- Manual process linking without supervision

## Cross-References

### Phase 0 Pattern Clusters

- **Universal patterns**: bool, String, int (shared with other families)
- **Family-specific**: Qualified calls (2 patterns), tuple syntax (2 patterns)
- **Gap patterns**: 36 gaps BEAM → ML-FP, 12 gaps LISP → BEAM

### Related convert-* Skills

- convert-elixir-roc (257 patterns)
- convert-python-elixir (227 patterns)
- convert-erlang-roc (179 patterns)
- convert-elixir-erlang (103 patterns)
- convert-clojure-elixir (138 patterns)

## Sources

- [Erlang Documentation](https://www.erlang.org/docs)
- [Elixir Documentation](https://elixir-lang.org/docs.html)
- [Gleam Documentation](https://gleam.run/documentation/)
- [Learn You Some Erlang](https://learnyousomeerlang.com/)
- [Elixir in Action](https://www.manning.com/books/elixir-in-action)

## See Also

- [Actors](actors.md) - Actor model as cross-cutting concern
- [ML-FP](ml-fp.md) - Common conversion target
- [Overview](overview.md) - Cross-family comparison matrices
