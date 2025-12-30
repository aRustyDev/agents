---
name: convert-erlang-elixir
description: Convert Erlang code to idiomatic Elixir. Use when migrating Erlang/OTP applications to Elixir, translating gen_server behaviors to GenServer, or refactoring BEAM VM code to leverage Elixir's modern syntax and tooling. Extends meta-convert-dev with Erlang-to-Elixir specific patterns.
---

# Convert Erlang to Elixir

Convert Erlang code to idiomatic Elixir. This skill extends `meta-convert-dev` with Erlang-to-Elixir specific type mappings, idiom translations, and tooling for translating between these two languages that share the BEAM VM runtime.

## This Skill Extends

- `meta-convert-dev` - Foundational conversion patterns (APTV workflow, testing strategies)

For general concepts like the Analyze → Plan → Transform → Validate workflow, testing strategies, and common pitfalls, see the meta-skill first.

## This Skill Adds

- **Type mappings**: Erlang types → Elixir types with modern syntax
- **Idiom translations**: Erlang patterns → idiomatic Elixir
- **OTP behaviors**: gen_server → GenServer, supervisor → Supervisor
- **Syntax modernization**: Records → Structs, -spec → @spec
- **Module system**: Erlang modules → Elixir modules with metaprogramming
- **Build tools**: rebar3 → Mix project structure

## This Skill Does NOT Cover

- General conversion methodology - see `meta-convert-dev`
- Erlang language fundamentals - see `lang-erlang-dev`
- Elixir language fundamentals - see `lang-elixir-dev`
- Reverse conversion (Elixir → Erlang) - see `convert-elixir-erlang`
- Phoenix framework specifics - see `lang-elixir-phoenix-dev`

---

## Quick Reference

| Erlang | Elixir | Notes |
|--------|--------|-------|
| `atom` | `:atom` | Atoms prefixed with `:` |
| `{ok, Value}` | `{:ok, value}` | Atoms and snake_case |
| `<<"binary">>` | `"binary"` | Strings are binaries |
| `[H\|T]` | `[h \| t]` | Same list syntax |
| `#{}` (map) | `%{}` | Map syntax similar |
| `#record{}` | `%Struct{}` | Records → Structs |
| `-module(name).` | `defmodule Name do` | Module definition |
| `-export([f/1]).` | `def f(arg)` | Public functions |
| `fun(X) -> X end` | `fn x -> x end` | Anonymous functions |
| `receive ... end` | `receive do ... end` | Message receiving |
| `gen_server` | `GenServer` | OTP behavior |
| `supervisor` | `Supervisor` | OTP supervisor |
| `?MODULE` | `__MODULE__` | Module reference |

---

## Type System Mapping

### Primitive Types

| Erlang | Elixir | Notes |
|--------|--------|-------|
| `atom` | `:atom` | Atoms require `:` prefix in Elixir |
| `integer` | `integer` | Arbitrary precision in both |
| `float` | `float` | 64-bit double precision |
| `binary` / `<<"string">>` | `"string"` | Elixir strings are UTF-8 binaries |
| `list` / `'charlist'` | `'charlist'` | Lists of integers |
| `true` / `false` | `true` / `false` | Boolean atoms |
| `undefined` | `nil` | Elixir uses `nil` atom |
| `pid` | `pid` | Process identifiers identical |
| `reference` | `reference` | Same on BEAM |

### Collection Types

| Erlang | Elixir | Notes |
|--------|--------|-------|
| `[H\|T]` | `[h \| t]` | Linked lists, same structure |
| `[]` | `[]` | Empty list |
| `{a, b, c}` | `{:a, :b, :c}` | Tuples identical, atoms need `:` |
| `#{}` | `%{}` | Maps (Erlang 17+) |
| `#{key => value}` | `%{key: value}` | Atom keys shorthand in Elixir |
| `orddict` | `Map` or `Keyword` | Use Elixir's Map module |
| `sets` | `MapSet` | Elixir's set implementation |

### Composite Types

| Erlang | Elixir | Notes |
|--------|--------|-------|
| `-record(user, {name, age}).` | `defstruct [:name, :age]` | Records → Structs |
| `#user{name=N, age=A}` | `%User{name: n, age: a}` | Record instance → Struct |
| `-type name() :: type().` | `@type name :: type` | Type specifications |
| `-spec func(type) -> type.` | `@spec func(type) :: type` | Function specs |
| `-callback func(type) -> type.` | `@callback func(type) :: type` | Behavior callbacks |

---

## Idiom Translation

### Pattern: Module Definition

**Erlang:**
```erlang
-module(my_module).
-export([public_function/1]).

-type my_type() :: atom() | binary().

public_function(Arg) ->
    private_function(Arg).

private_function(Arg) ->
    {ok, Arg}.
```

**Elixir:**
```elixir
defmodule MyModule do
  @moduledoc """
  Module documentation goes here.
  """

  @type my_type :: atom() | binary()

  @spec public_function(term()) :: {:ok, term()}
  def public_function(arg) do
    private_function(arg)
  end

  defp private_function(arg) do
    {:ok, arg}
  end
end
```

**Why this translation:**
- Elixir uses `defmodule` with do/end blocks
- Functions are public by default unless `defp` (private)
- `@moduledoc` and `@doc` for documentation
- CamelCase for module names, snake_case for functions

---

### Pattern: Function Clauses and Pattern Matching

**Erlang:**
```erlang
factorial(0) -> 1;
factorial(N) when N > 0 -> N * factorial(N - 1).

process_result({ok, Data}) ->
    {success, Data};
process_result({error, Reason}) ->
    {failure, Reason}.
```

**Elixir:**
```elixir
def factorial(0), do: 1
def factorial(n) when n > 0, do: n * factorial(n - 1)

def process_result({:ok, data}), do: {:success, data}
def process_result({:error, reason}), do: {:failure, reason}
```

**Why this translation:**
- Multiple function clauses work the same way
- Elixir uses `:` prefix for atoms
- `do:` for single-line functions, `do/end` for multi-line
- Guards work identically with `when`

---

### Pattern: Records to Structs

**Erlang:**
```erlang
-record(user, {
    id :: integer(),
    name :: binary(),
    email :: binary()
}).

create_user(Id, Name, Email) ->
    #user{id=Id, name=Name, email=Email}.

get_user_name(#user{name=Name}) ->
    Name.
```

**Elixir:**
```elixir
defmodule User do
  @enforce_keys [:id, :name, :email]
  defstruct [:id, :name, :email]

  @type t :: %__MODULE__{
    id: integer(),
    name: String.t(),
    email: String.t()
  }

  def new(id, name, email) do
    %User{id: id, name: name, email: email}
  end

  def get_name(%User{name: name}), do: name
end
```

---

### Pattern: gen_server to GenServer

**Erlang:**
```erlang
-module(counter_server).
-behaviour(gen_server).

-export([start_link/0, increment/0, get_count/0]).
-export([init/1, handle_call/3, handle_cast/2]).

start_link() ->
    gen_server:start_link({local, ?MODULE}, ?MODULE, [], []).

increment() ->
    gen_server:cast(?MODULE, increment).

get_count() ->
    gen_server:call(?MODULE, get_count).

init([]) ->
    {ok, #{count => 0}}.

handle_call(get_count, _From, State = #{count := Count}) ->
    {reply, Count, State}.

handle_cast(increment, State = #{count := Count}) ->
    {noreply, State#{count := Count+1}}.
```

**Elixir:**
```elixir
defmodule CounterServer do
  use GenServer

  # Client API

  def start_link(opts \\ []) do
    GenServer.start_link(__MODULE__, :ok, opts ++ [name: __MODULE__])
  end

  def increment do
    GenServer.cast(__MODULE__, :increment)
  end

  def get_count do
    GenServer.call(__MODULE__, :get_count)
  end

  # Server Callbacks

  @impl true
  def init(:ok) do
    {:ok, %{count: 0}}
  end

  @impl true
  def handle_call(:get_count, _from, state) do
    {:reply, state.count, state}
  end

  @impl true
  def handle_cast(:increment, state) do
    {:noreply, %{state | count: state.count + 1}}
  end
end
```

**Why this translation:**
- `use GenServer` imports behavior
- `@impl true` marks callback implementations
- `__MODULE__` replaces `?MODULE`
- Maps update with `%{map | key: value}` syntax

---

### Pattern: Supervisor Trees

**Erlang:**
```erlang
-module(my_supervisor).
-behaviour(supervisor).

init([]) ->
    Children = [
        {counter_server,
         {counter_server, start_link, []},
         permanent, 5000, worker, [counter_server]}
    ],
    {ok, {{one_for_one, 5, 10}, Children}}.
```

**Elixir:**
```elixir
defmodule MySupervisor do
  use Supervisor

  def start_link(init_arg) do
    Supervisor.start_link(__MODULE__, init_arg, name: __MODULE__)
  end

  @impl true
  def init(_init_arg) do
    children = [
      {CounterServer, []}
    ]

    Supervisor.init(children, strategy: :one_for_one)
  end
end
```

---

### Pattern: Message Passing

**Erlang:**
```erlang
Pid = spawn(fun() -> loop(0) end),
Pid ! {self(), increment},
receive
    {reply, Msg} -> io:format("Got: ~p~n", [Msg])
after 5000 ->
    io:format("Timeout~n")
end.
```

**Elixir:**
```elixir
pid = spawn(fn -> loop(0) end)
send(pid, {self(), :increment})

receive do
  {:reply, msg} -> IO.puts("Got: #{inspect(msg)}")
after
  5000 -> IO.puts("Timeout")
end
```

---

### Pattern: Error Handling

**Erlang:**
```erlang
safe_divide(_, 0) -> {error, division_by_zero};
safe_divide(A, B) -> {ok, A / B}.

handle_file(File) ->
    try
        {ok, Content} = file:read_file(File),
        process(Content)
    catch
        error:Reason -> {error, Reason}
    end.
```

**Elixir:**
```elixir
def safe_divide(_a, 0), do: {:error, :division_by_zero}
def safe_divide(a, b), do: {:ok, a / b}

def handle_file(file) do
  try do
    {:ok, content} = File.read!(file)
    process(content)
  rescue
    e in File.Error -> {:error, e.reason}
  end
end

# With construct for error handling
def handle_file_with(file) do
  with {:ok, content} <- File.read(file),
       {:ok, processed} <- process(content) do
    {:ok, processed}
  end
end
```

---

## OTP Behavior Translation

| Erlang callback | Elixir callback | Notes |
|-----------------|-----------------|-------|
| `init/1` | `init/1` | Same signature |
| `handle_call/3` | `handle_call/3` | Synchronous requests |
| `handle_cast/2` | `handle_cast/2` | Asynchronous messages |
| `handle_info/2` | `handle_info/2` | Non-OTP messages |
| `terminate/2` | `terminate/2` | Cleanup |

---

## Syntax Modernization

### Pipe Operator

**Erlang:**
```erlang
Result = process(transform(filter(validate(Input)))).
```

**Elixir:**
```elixir
result =
  input
  |> validate()
  |> filter()
  |> transform()
  |> process()
```

### List Comprehensions

**Erlang:**
```erlang
[X*2 || X <- lists:seq(1, 10), X rem 2 =:= 0].
```

**Elixir:**
```elixir
for x <- 1..10, rem(x, 2) == 0, do: x * 2
```

---

## Common Pitfalls

### 1. Atom Syntax Confusion

```elixir
# WRONG
case result do
  ok -> :success
end

# CORRECT
case result do
  :ok -> :success
end
```

### 2. Variable Rebinding

```elixir
# Elixir allows rebinding
x = 1
x = 2  # OK

# Use pin operator to match
^x = 2  # Match error if x != 2
```

### 3. String vs Charlist

```elixir
string = "hello"   # Binary (UTF-8)
charlist = 'hello' # Charlist

# Convert between them
String.to_charlist("hello")
List.to_string('hello')
```

---

## Tooling

| Erlang | Elixir | Purpose |
|--------|--------|---------|
| `rebar3` | `Mix` | Build tool |
| `EUnit` | `ExUnit` | Testing |
| `Dialyzer` | `Dialyzer` | Type checker |
| `erlc` | `elixirc` | Compiler |
| `erl` | `IEx` | REPL |

### Migration Workflow

1. **Setup Elixir project**: `mix new my_app`
2. **Add Erlang dependencies** in `mix.exs`
3. **Call Erlang from Elixir**: `:erlang_module.function(args)`
4. **Gradual migration**: Keep Erlang in `src/` (auto-compiled by Mix)

---

## See Also

- `meta-convert-dev` - Foundational patterns
- `convert-elixir-erlang` - Reverse conversion
- `lang-erlang-dev` - Erlang patterns
- `lang-elixir-dev` - Elixir patterns
