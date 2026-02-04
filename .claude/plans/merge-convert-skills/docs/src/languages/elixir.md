# Elixir

> Dynamic, functional language on the Erlang VM designed for building scalable and maintainable applications.

## Overview

Elixir is a dynamic, functional programming language created by Jose Valim and first released in 2011. It runs on the Erlang VM (BEAM), leveraging decades of battle-tested infrastructure for building distributed, fault-tolerant systems with low-latency and high availability.

Elixir adds modern language features to the BEAM ecosystem: a Ruby-inspired syntax, powerful metaprogramming through macros, first-class documentation, and comprehensive tooling. It maintains full interoperability with Erlang and its OTP library.

The language excels in real-time systems, web applications (Phoenix), embedded systems (Nerves), and anywhere high concurrency and fault tolerance are needed.

## Family Classification

| Dimension | Classification | Notes |
|-----------|----------------|-------|
| Primary Family | BEAM | Erlang VM, actor model |
| Secondary Family | FP | Functional with immutable data |
| Subtype | macro-enabled | Powerful metaprogramming |

See: [BEAM Family](../language-families/beam.md)

## Version History

| Version | Release | Key Changes for Conversion |
|---------|---------|---------------------------|
| 1.0 | 2014-09 | Initial stable release |
| 1.6 | 2018-01 | Formatter, dynamic supervisor |
| 1.9 | 2019-06 | Releases, config providers |
| 1.12 | 2021-05 | Mix.install, scripting improvements |
| 1.14 | 2022-09 | Debugging improvements, PartitionSupervisor |
| 1.15 | 2023-06 | Exception stack traces, compilation improvements |

## Feature Profile

### Type System

- **Strength:** dynamic (runtime typing)
- **Inference:** none (optional typespecs for documentation/dialyzer)
- **Generics:** runtime (duck typing, protocols)
- **Nullability:** nullable (nil as value)

### Memory Model

- **Management:** gc (per-process garbage collection)
- **Mutability:** immutable (all data immutable)
- **Allocation:** heap (per-process heaps)
- **Process isolation:** complete (share-nothing)

### Control Flow

- **Structured:** if-else, case, cond, with
- **Effects:** pattern matching on tagged tuples ({:ok, value}, {:error, reason})
- **Async:** processes, Task, GenServer (actor model)

### Data Types

- **Primitives:** integers (arbitrary precision), floats, atoms, booleans
- **Composites:** tuples, lists, maps, structs, keyword lists
- **Collections:** List, Map, MapSet, Range
- **Abstraction:** modules, protocols, behaviours

### Metaprogramming

- **Macros:** hygienic (quote/unquote, AST manipulation)
- **Reflection:** runtime (Code module, __MODULE__)
- **Code generation:** macros, use callbacks

## Ecosystem

| Tool | Name | Notes |
|------|------|-------|
| Package Manager | Mix/Hex | Built-in with Mix |
| Build System | Mix | Built-in |
| LSP | ElixirLS, lexical | ElixirLS is established |
| Formatter | mix format | Built-in, opinionated |
| Linter | Credo | Comprehensive |
| REPL | IEx | Excellent, built-in |
| Test Framework | ExUnit | Built-in |

## Syntax Patterns

```elixir
# Function definition
def greet(name, times \\ 1) do
  String.duplicate("Hello, #{name}! ", times)
end

# Pattern matching in function heads
def process({:ok, value}), do: {:success, value}
def process({:error, reason}), do: {:failure, reason}
def process(_), do: {:failure, :unknown}

# Anonymous function
greet = fn name -> "Hello, #{name}!" end
greet.("World")

# Capture operator
double = &(&1 * 2)

# Module and struct
defmodule User do
  defstruct [:id, :name, email: nil]

  def new(id, name) do
    %User{id: id, name: name}
  end

  def set_email(%User{} = user, email) do
    %{user | email: email}
  end
end

# Protocol (type class equivalent)
defprotocol Stringify do
  @doc "Converts a value to string"
  def to_string(value)
end

defimpl Stringify, for: User do
  def to_string(user), do: "User(#{user.name})"
end

# Pattern matching with case
def area(shape) do
  case shape do
    {:circle, radius} -> :math.pi() * radius * radius
    {:rectangle, width, height} -> width * height
    _ -> {:error, :unknown_shape}
  end
end

# With expression for happy path
def create_order(params) do
  with {:ok, user} <- fetch_user(params.user_id),
       {:ok, product} <- fetch_product(params.product_id),
       {:ok, order} <- Order.create(user, product) do
    {:ok, order}
  else
    {:error, reason} -> {:error, reason}
  end
end

# Pipeline operator
def process_data(data) do
  data
  |> Enum.filter(&(&1 > 0))
  |> Enum.map(&(&1 * 2))
  |> Enum.sum()
end

# GenServer (actor)
defmodule Counter do
  use GenServer

  def start_link(initial) do
    GenServer.start_link(__MODULE__, initial)
  end

  def increment(pid) do
    GenServer.cast(pid, :increment)
  end

  def get(pid) do
    GenServer.call(pid, :get)
  end

  # Callbacks
  @impl true
  def init(initial), do: {:ok, initial}

  @impl true
  def handle_cast(:increment, count), do: {:noreply, count + 1}

  @impl true
  def handle_call(:get, _from, count), do: {:reply, count, count}
end

# Supervision tree
defmodule MyApp.Application do
  use Application

  def start(_type, _args) do
    children = [
      {Counter, 0},
      MyApp.Worker,
      {Task.Supervisor, name: MyApp.TaskSupervisor}
    ]

    Supervisor.start_link(children, strategy: :one_for_one)
  end
end

# Comprehension
for x <- 1..10, rem(x, 2) == 0, do: x * x

# Macro definition
defmacro debug(expr) do
  quote do
    result = unquote(expr)
    IO.puts("#{unquote(Macro.to_string(expr))} = #{inspect(result)}")
    result
  end
end
```

## Semantic Gaps

| Gap | Severity | Workaround |
|-----|----------|------------|
| No static types | moderate | Use Dialyzer, typespecs |
| Immutable only (no local mutation) | minor | Use recursion, comprehensions |
| Pattern matching can be verbose | minor | Use with, custom macros |
| OTP learning curve | moderate | Start with Task, GenServer basics |
| No lazy evaluation (by default) | minor | Use Stream module |

## Convert-* Coverage

| Direction | Count | Skills |
|-----------|-------|--------|
| As Source | 6 | elixir-elm, elixir-erlang, elixir-fsharp, elixir-haskell, elixir-roc, elixir-scala |
| As Target | 2 | python-elixir, clojure-elixir |

**Note:** Common source for FP conversions. Process-based concurrency requires mapping to target paradigms.

## Idiomatic Patterns

### Tagged Tuples → Result/Either

```elixir
# Elixir: tagged tuple
{:ok, value}
{:error, reason}

# IR equivalent: Result type
# Ok(value) | Err(reason)
```

### Protocols → Type Classes

```elixir
# Elixir: protocol
defprotocol Size do
  def size(data)
end

# IR equivalent: type class
# trait Size { fn size(&self) -> usize }
```

### GenServer → Actor/State Machine

```elixir
# Elixir: GenServer
def handle_call(:get, _from, state) do
  {:reply, state, state}
end

# IR equivalent: actor receive
# receive { Get(reply_to) => reply_to.send(state) }
```

### Pipeline → Method Chain/Composition

```elixir
# Elixir: pipeline
data |> transform() |> validate() |> save()

# IR equivalent: method chain or composition
# save(validate(transform(data)))
# OR data.transform().validate().save()
```

## Related Languages

- **Influenced by:** Erlang, Ruby, Clojure
- **Influenced:** Gleam, LFE
- **Compiles to:** BEAM bytecode
- **FFI compatible:** Erlang (native), C (NIFs)

## Sources

- [Elixir Documentation](https://hexdocs.pm/elixir/)
- [Elixir Getting Started](https://elixir-lang.org/getting-started/)
- [Elixir School](https://elixirschool.com/)
- [Hex Package Manager](https://hex.pm/)

## See Also

- [BEAM Family](../language-families/beam.md)
- [Erlang](erlang.md) - VM foundation
- [Gleam](gleam.md) - Typed BEAM
- [Phoenix Framework](https://www.phoenixframework.org/)
