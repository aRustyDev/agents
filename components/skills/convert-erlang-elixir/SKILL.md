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
| `?FUNCTION_NAME` | `__ENV__.function` | Function introspection |

---

## When Converting Code

1. **Analyze source thoroughly** before writing Elixir - understand OTP structure
2. **Map types first** - create type equivalence table for domain models
3. **Preserve semantics** over syntax similarity - embrace Elixir idioms
4. **Modernize syntax** - leverage Elixir's expressive features
5. **Adopt Elixir conventions** - snake_case, do/end blocks, pipe operator
6. **Test equivalence** - same inputs → same outputs, same supervision trees
7. **Leverage tooling** - Use Mix, ExUnit, and Elixir's metaprogramming

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
| `port` | `port` | Same on BEAM |
| `fun` | `function` | Anonymous functions |

### Collection Types

| Erlang | Elixir | Notes |
|--------|--------|-------|
| `[H\|T]` | `[h \| t]` | Linked lists, same structure |
| `[]` | `[]` | Empty list |
| `{a, b, c}` | `{:a, :b, :c}` | Tuples identical, atoms need `:` |
| `#{}` | `%{}` | Maps (Erlang 17+) |
| `#{key => value}` | `%{key: value}` | Atom keys shorthand in Elixir |
| `#{key := value}` | `%{key: value}` | Pattern matching syntax differs |
| `orddict` | `Map` or `Keyword` | Use Elixir's Map module |
| `gb_trees` | `Map` | Maps are optimized on BEAM |
| `sets` | `MapSet` | Elixir's set implementation |
| `queue` | `:queue` | Use Erlang's queue module |

### Composite Types

| Erlang | Elixir | Notes |
|--------|--------|-------|
| `-record(user, {name, age}).` | `defstruct [:name, :age]` | Records → Structs |
| `#user{name=N, age=A}` | `%User{name: n, age: a}` | Record instance → Struct |
| `-type name() :: type().` | `@type name :: type` | Type specifications |
| `-spec func(type) -> type.` | `@spec func(type) :: type` | Function specs |
| `-opaque type() :: impl.` | `@opaque type :: impl` | Opaque types |
| `-callback func(type) -> type.` | `@callback func(type) :: type` | Behavior callbacks |
| `{ok, Value} \| {error, Reason}` | `{:ok, value} \| {:error, reason}` | Tagged tuples |
| Custom guard | Custom guard macro | Use `defguard` |

---

## Idiom Translation

### Pattern: Module Definition

Erlang uses module attributes. Elixir uses nested module syntax with modern conventions.

**Erlang:**
```erlang
-module(my_module).
-export([public_function/1]).
-export_type([my_type/0]).

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

  @doc """
  Public function documentation.
  """
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
- Elixir uses `defmodule` with do/end blocks (more readable)
- Functions are public by default unless `defp` (private)
- `@moduledoc` and `@doc` for documentation (built-in)
- `@spec` replaces `-spec` with cleaner syntax
- CamelCase for module names, snake_case for functions

---

### Pattern: Function Clauses and Pattern Matching

Both languages use pattern matching, but Elixir has cleaner syntax and guards.

**Erlang:**
```erlang
factorial(0) -> 1;
factorial(N) when N > 0 -> N * factorial(N - 1).

process_result({ok, Data}) ->
    {success, Data};
process_result({error, Reason}) ->
    {failure, Reason};
process_result(_Unknown) ->
    {failure, unknown}.

map_over_list([], _Fun) -> [];
map_over_list([H|T], Fun) -> [Fun(H) | map_over_list(T, Fun)].
```

**Elixir:**
```elixir
def factorial(0), do: 1
def factorial(n) when n > 0, do: n * factorial(n - 1)

def process_result({:ok, data}), do: {:success, data}
def process_result({:error, reason}), do: {:failure, reason}
def process_result(_unknown), do: {:failure, :unknown}

def map_over_list([], _fun), do: []
def map_over_list([h | t], fun), do: [fun.(h) | map_over_list(t, fun)]

# But prefer Elixir's Enum module
def map_over_list(list, fun), do: Enum.map(list, fun)
```

**Why this translation:**
- Multiple function clauses work the same way
- Elixir uses `:` prefix for atoms
- `do:` for single-line functions, `do/end` for multi-line
- Guards work identically with `when`
- Prefer Elixir's standard library (Enum, Stream) over manual recursion

---

### Pattern: Records to Structs

Erlang records are compile-time constructs. Elixir structs are maps with compile-time guarantees.

**Erlang:**
```erlang
-record(user, {
    id :: integer(),
    name :: binary(),
    email :: binary(),
    age :: integer()
}).

create_user(Id, Name, Email, Age) ->
    #user{id=Id, name=Name, email=Email, age=Age}.

get_user_name(#user{name=Name}) ->
    Name.

update_user_age(User, NewAge) ->
    User#user{age=NewAge}.
```

**Elixir:**
```elixir
defmodule User do
  @enforce_keys [:id, :name, :email]
  defstruct [:id, :name, :email, age: 0]

  @type t :: %__MODULE__{
    id: integer(),
    name: String.t(),
    email: String.t(),
    age: integer()
  }

  @spec new(integer(), String.t(), String.t(), integer()) :: t()
  def new(id, name, email, age) do
    %User{id: id, name: name, email: email, age: age}
  end

  @spec get_name(t()) :: String.t()
  def get_name(%User{name: name}), do: name

  @spec update_age(t(), integer()) :: t()
  def update_age(user, new_age) do
    %User{user | age: new_age}
  end
end
```

**Why this translation:**
- Structs are modules with `defstruct`
- `@enforce_keys` ensures required fields
- Pattern matching on structs works similarly
- Update syntax: `%User{user | field: value}`
- Structs are maps underneath, so Map functions work
- Type specs use module-scoped `t()` type

---

### Pattern: gen_server to GenServer

OTP behaviors translate directly, but with Elixir's cleaner syntax.

**Erlang:**
```erlang
-module(counter_server).
-behaviour(gen_server).

-export([start_link/0, increment/0, get_count/0]).
-export([init/1, handle_call/3, handle_cast/2, terminate/2]).

-record(state, {count = 0 :: integer()}).

start_link() ->
    gen_server:start_link({local, ?MODULE}, ?MODULE, [], []).

increment() ->
    gen_server:cast(?MODULE, increment).

get_count() ->
    gen_server:call(?MODULE, get_count).

init([]) ->
    {ok, #state{count=0}}.

handle_call(get_count, _From, State = #state{count=Count}) ->
    {reply, Count, State};
handle_call(_Request, _From, State) ->
    {reply, {error, unknown_call}, State}.

handle_cast(increment, State = #state{count=Count}) ->
    {noreply, State#state{count=Count+1}};
handle_cast(_Msg, State) ->
    {noreply, State}.

terminate(_Reason, _State) ->
    ok.
```

**Elixir:**
```elixir
defmodule CounterServer do
  use GenServer

  # Client API

  @spec start_link(keyword()) :: GenServer.on_start()
  def start_link(opts \\ []) do
    GenServer.start_link(__MODULE__, :ok, opts ++ [name: __MODULE__])
  end

  @spec increment() :: :ok
  def increment do
    GenServer.cast(__MODULE__, :increment)
  end

  @spec get_count() :: integer()
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

  @impl true
  def terminate(_reason, _state) do
    :ok
  end
end
```

**Why this translation:**
- `use GenServer` imports behavior
- `@impl true` marks callback implementations
- State is a map instead of record
- `__MODULE__` replaces `?MODULE`
- Client API and callbacks clearly separated
- Pattern matching on atoms uses `:` prefix
- Maps update with `%{map | key: value}` syntax

---

### Pattern: Supervisor Trees

Supervisors translate almost 1:1, with cleaner child specification syntax.

**Erlang:**
```erlang
-module(my_supervisor).
-behaviour(supervisor).

-export([start_link/0]).
-export([init/1]).

start_link() ->
    supervisor:start_link({local, ?MODULE}, ?MODULE, []).

init([]) ->
    Children = [
        {counter_server,
         {counter_server, start_link, []},
         permanent,
         5000,
         worker,
         [counter_server]},
        {worker_pool,
         {worker_pool, start_link, [10]},
         permanent,
         infinity,
         supervisor,
         [worker_pool]}
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
      # Supervised worker
      {CounterServer, []},

      # With custom options
      %{
        id: WorkerPool,
        start: {WorkerPool, :start_link, [10]},
        restart: :permanent,
        shutdown: :infinity,
        type: :supervisor
      }
    ]

    # Strategy: :one_for_one, :one_for_all, :rest_for_one
    Supervisor.init(children, strategy: :one_for_one, max_restarts: 5, max_seconds: 10)
  end
end

# Alternative: using child_spec/1
defmodule CounterServer do
  use GenServer

  def child_spec(opts) do
    %{
      id: __MODULE__,
      start: {__MODULE__, :start_link, [opts]},
      restart: :permanent,
      shutdown: 5000,
      type: :worker
    }
  end

  # ... rest of GenServer implementation
end
```

**Why this translation:**
- `use Supervisor` imports behavior
- Child specs can be tuples `{Module, args}` or maps
- Maps are more readable than Erlang tuples
- `Supervisor.init/2` with keyword options
- Strategies: `:one_for_one`, `:one_for_all`, `:rest_for_one`
- `child_spec/1` callback for custom child specs

---

### Pattern: Message Passing and Processes

Process primitives are identical, but Elixir provides nicer syntax.

**Erlang:**
```erlang
% Spawn process
Pid = spawn(fun() -> loop(0) end),

% Send message
Pid ! {self(), increment},

% Receive messages
loop(Count) ->
    receive
        {From, increment} ->
            From ! {ok, Count + 1},
            loop(Count + 1);
        {From, get_count} ->
            From ! {ok, Count},
            loop(Count);
        stop ->
            ok
    after 5000 ->
        io:format("Timeout~n"),
        loop(Count)
    end.

% Monitor and link
Ref = monitor(process, Pid),
link(Pid).
```

**Elixir:**
```elixir
# Spawn process
pid = spawn(fn -> loop(0) end)

# Send message
send(pid, {self(), :increment})

# Receive messages
def loop(count) do
  receive do
    {from, :increment} ->
      send(from, {:ok, count + 1})
      loop(count + 1)

    {from, :get_count} ->
      send(from, {:ok, count})
      loop(count)

    :stop ->
      :ok
  after
    5000 ->
      IO.puts("Timeout")
      loop(count)
  end
end

# Monitor and link
ref = Process.monitor(pid)
Process.link(pid)

# Task module for common patterns
Task.async(fn -> do_work() end)
Task.await(task)
```

**Why this translation:**
- `send/2` is more explicit than `!` operator
- `receive do/end` instead of `receive/end`
- Atoms need `:` prefix
- `Process` module for process operations
- `Task` module for async/await patterns
- Same timeout syntax with `after`

---

### Pattern: Error Handling and "Let It Crash"

Both follow the same philosophy, but Elixir has additional constructs.

**Erlang:**
```erlang
% Erlang style
safe_divide(A, B) when B =/= 0 ->
    {ok, A / B};
safe_divide(_A, 0) ->
    {error, division_by_zero}.

% Let it crash
divide(A, B) ->
    A / B.  % Crashes on division by zero

% Try-catch
handle_file(File) ->
    try
        {ok, Content} = file:read_file(File),
        process(Content)
    catch
        error:Reason -> {error, Reason};
        exit:Reason -> {exit, Reason}
    end.
```

**Elixir:**
```elixir
# Tagged tuples
def safe_divide(a, b) when b != 0, do: {:ok, a / b}
def safe_divide(_a, 0), do: {:error, :division_by_zero}

# Let it crash
def divide(a, b), do: a / b  # Crashes on division by zero

# Try-rescue-catch
def handle_file(file) do
  try do
    {:ok, content} = File.read!(file)
    process(content)
  rescue
    e in File.Error -> {:error, e.reason}
  catch
    :exit, reason -> {:exit, reason}
  end
end

# With construct for error handling
def handle_file_with(file) do
  with {:ok, content} <- File.read(file),
       {:ok, processed} <- process(content) do
    {:ok, processed}
  else
    {:error, reason} -> {:error, reason}
  end
end
```

**Why this translation:**
- Same "let it crash" philosophy
- `rescue` for exceptions, `catch` for throws/exits
- `with` construct for cleaner error pipelines
- Pattern matching works the same
- Guards use `!=` instead of `=/=`

---

### Pattern: Macros and Metaprogramming

Elixir has powerful metaprogramming through macros. Erlang has parse transforms (less common).

**Erlang:**
```erlang
% Erlang uses parse transforms (compile-time)
% or preprocessor macros

-define(LOG(Msg), io:format("[LOG] ~p~n", [Msg])).

log_example() ->
    ?LOG({info, "Starting process"}).

% Parse transforms require custom modules
% and are rarely used in application code
```

**Elixir:**
```elixir
# Elixir macros are first-class
defmodule Logger.Macro do
  defmacro log(level, message) do
    quote do
      IO.puts("[#{unquote(level)}] #{unquote(message)}")
    end
  end
end

defmodule MyApp do
  require Logger.Macro

  def log_example do
    Logger.Macro.log(:info, "Starting process")
  end
end

# Use built-in Logger
require Logger
Logger.info("Starting process")

# Metaprogramming with use and __using__
defmodule MyBehaviour do
  defmacro __using__(opts) do
    quote do
      @behaviour MyBehaviour

      def default_function do
        "Default implementation"
      end

      defoverridable default_function: 0
    end
  end
end

defmodule MyModule do
  use MyBehaviour

  # Can override default_function if needed
end
```

**Why this translation:**
- Elixir macros are more powerful and easier to write
- `quote` and `unquote` for AST manipulation
- `use` and `__using__` for code injection
- Prefer built-in libraries (Logger) over custom macros
- Macros enable DSLs (like Phoenix routers, Ecto schemas)

---

## OTP Behavior Translation

### gen_server → GenServer

Complete mapping of gen_server callbacks:

| Erlang callback | Elixir callback | Notes |
|-----------------|-----------------|-------|
| `init/1` | `init/1` | Same signature |
| `handle_call/3` | `handle_call/3` | Synchronous requests |
| `handle_cast/2` | `handle_cast/2` | Asynchronous messages |
| `handle_info/2` | `handle_info/2` | Non-OTP messages |
| `terminate/2` | `terminate/2` | Cleanup |
| `code_change/3` | `code_change/3` | Hot code reload |
| `format_status/2` | `format_status/2` | Status formatting |

Return values are identical between languages.

### supervisor → Supervisor

| Erlang | Elixir | Notes |
|--------|--------|-------|
| `init/1` | `init/1` | Return child specs |
| `one_for_one` | `:one_for_one` | Restart strategy |
| `one_for_all` | `:one_for_all` | Restart strategy |
| `rest_for_one` | `:rest_for_one` | Restart strategy |
| `simple_one_for_one` | `:simple_one_for_one` | Dynamic children (deprecated in Elixir, use DynamicSupervisor) |

### gen_statem → GenStateMachine (library)

Elixir doesn't have built-in gen_statem, but there's a library:

```elixir
# Add to mix.exs
{:gen_state_machine, "~> 3.0"}

# Usage similar to Erlang gen_statem
defmodule MyStateMachine do
  use GenStateMachine

  def init(args) do
    {:ok, :initial_state, %{data: args}}
  end

  def handle_event({:call, from}, :get_state, state, data) do
    {:keep_state_and_data, [{:reply, from, state}]}
  end
end
```

---

## Syntax Modernization

### Lists and Comprehensions

**Erlang:**
```erlang
% List comprehension
[X*2 || X <- Lists:seq(1, 10), X rem 2 =:= 0].

% Multiple generators
[{X, Y} || X <- [1,2,3], Y <- [a,b,c]].

% Binary comprehension
<< <<C>> || <<C>> <= <<"hello">>, C =/= $o >>.
```

**Elixir:**
```elixir
# List comprehension
for x <- 1..10, rem(x, 2) == 0, do: x * 2

# Multiple generators
for x <- [1, 2, 3], y <- [:a, :b, :c], do: {x, y}

# Into option for different collections
for x <- 1..5, into: %{}, do: {x, x * x}

# Binary comprehension (for construct)
for <<c <- "hello">>, c != ?o, into: "", do: <<c>>
```

### Pipe Operator

Elixir's pipe operator (`|>`) has no Erlang equivalent but dramatically improves readability.

**Erlang:**
```erlang
% Nested function calls
Result = process(transform(filter(validate(Input)))).

% Or with intermediate variables
Valid = validate(Input),
Filtered = filter(Valid),
Transformed = transform(Filtered),
Result = process(Transformed).
```

**Elixir:**
```elixir
# Pipe operator
result =
  input
  |> validate()
  |> filter()
  |> transform()
  |> process()

# First argument is piped
result =
  input
  |> String.upcase()
  |> String.split(",")
  |> Enum.map(&String.trim/1)
```

### Keyword Lists and Options

**Erlang:**
```erlang
% Proplists for options
start_link(Name, Options) ->
    Port = proplists:get_value(port, Options, 8080),
    Host = proplists:get_value(host, Options, "localhost"),
    gen_server:start_link({local, Name}, ?MODULE, {Host, Port}, []).
```

**Elixir:**
```elixir
# Keyword lists (syntactic sugar for lists of 2-tuples)
def start_link(name, opts \\ []) do
  port = Keyword.get(opts, :port, 8080)
  host = Keyword.get(opts, :host, "localhost")
  GenServer.start_link(__MODULE__, {host, port}, name: name)
end

# Usage
MyServer.start_link(:my_server, port: 3000, host: "0.0.0.0")
```

---

## Common Pitfalls

### 1. Atom Syntax Confusion

**Problem:** Forgetting `:` prefix for atoms in Elixir.

```erlang
% Erlang
case Result of
    ok -> success;
    error -> failure
end.
```

```elixir
# Elixir - WRONG
case result do
  ok -> :success
  error -> :failure
end

# Elixir - CORRECT
case result do
  :ok -> :success
  :error -> :failure
end
```

**Solution:** All atoms in Elixir need `:` prefix except booleans (`true`, `false`, `nil`).

### 2. Variable Rebinding

**Problem:** Erlang has single assignment. Elixir allows rebinding.

```erlang
% Erlang - ERROR
X = 1,
X = 2.  % ** exception error: no match of right hand side value 2
```

```elixir
# Elixir - ALLOWED
x = 1
x = 2  # Rebinding allowed, x is now 2

# Use pin operator to match instead of rebind
x = 1
^x = 1  # Match - OK
^x = 2  # Match error
```

**Solution:** Use pin operator `^` in Elixir when you want Erlang's matching behavior.

### 3. String vs Charlist Confusion

**Problem:** Erlang uses charlists by default. Elixir uses binaries (UTF-8 strings).

```erlang
% Erlang
String = "hello".  % Charlist [104, 101, 108, 108, 111]
Binary = <<"hello">>.  % Binary
```

```elixir
# Elixir
string = "hello"  # Binary (UTF-8 string)
charlist = 'hello'  # Charlist [104, 101, 108, 108, 111]

# Convert between them
String.to_charlist("hello")  # 'hello'
List.to_string('hello')      # "hello"
```

**Solution:** Remember Elixir strings are binaries. Use charlists only when interfacing with Erlang libraries that expect them.

### 4. Record to Struct Module Requirement

**Problem:** Erlang records are compile-time. Elixir structs require modules.

```erlang
% Erlang - records can be defined inline
-record(user, {name, age}).
```

```elixir
# Elixir - WRONG: can't define struct inline
defstruct [:name, :age]  # Where's the module?

# Elixir - CORRECT: struct needs module
defmodule User do
  defstruct [:name, :age]
end
```

**Solution:** Always wrap Elixir structs in a module.

### 5. Function Call Syntax

**Problem:** Elixir requires `()` or `.` for function calls in certain contexts.

```erlang
% Erlang
lists:map(fun(X) -> X * 2 end, List).
```

```elixir
# Elixir - module function call
Enum.map(list, fn x -> x * 2 end)
# or with capture syntax
Enum.map(list, &(&1 * 2))

# WRONG: calling anonymous function
fun = fn x -> x * 2 end
fun(5)  # Correct
fun 5   # Wrong - syntax error

# Local function vs variable
my_function()  # Call function
my_function    # Reference variable/function
```

**Solution:** Use `()` for anonymous function calls. Module functions use `.`. Local functions can omit `()` in some contexts.

### 6. Tuple Element Access

**Problem:** Erlang uses `element/2`. Elixir uses `elem/2` and pattern matching.

```erlang
% Erlang
Tuple = {a, b, c},
First = element(1, Tuple).  % 1-indexed!
```

```elixir
# Elixir
tuple = {:a, :b, :c}
first = elem(tuple, 0)  # 0-indexed!

# Better: pattern match
{first, _second, _third} = tuple
```

**Solution:** Remember Elixir is 0-indexed. Prefer pattern matching over `elem/2`.

### 7. Operator Differences

**Problem:** Some operators differ between Erlang and Elixir.

| Operation | Erlang | Elixir |
|-----------|--------|--------|
| Not equal | `=/=` | `!=` |
| Strict equality | `=:=` | `===` |
| Not strict equal | `=/=` | `!==` |
| Boolean and | `andalso` | `&&` or `and` |
| Boolean or | `orelse` | `\|\|` or `or` |
| Boolean not | `not` | `!` or `not` |
| String concat | `++` (lists) | `<>` (binaries) |

---

## Tooling

| Tool | Purpose | Notes |
|------|---------|-------|
| **rebar3** | Erlang build tool | Use for Erlang projects |
| **Mix** | Elixir build tool | Replaces rebar3 for Elixir |
| **erlc** | Erlang compiler | Direct compilation |
| **elixirc** | Elixir compiler | Direct compilation |
| **EUnit** | Erlang testing | Unit tests for Erlang |
| **ExUnit** | Elixir testing | Built-in, more features |
| **Dialyzer** | Type checker | Works for both languages |
| **Credo** | Elixir linter | Code quality, style |
| **ExDoc** | Documentation | Generates docs from `@doc` |
| **erlang.mk** | Alternative build | Makefile-based |
| **hex.pm** | Package manager | Elixir packages (and Erlang) |
| **Observer** | Runtime inspector | BEAM VM observer (both) |
| **:recon** | Production debugging | Erlang library, works in Elixir |
| **IEx** | Elixir REPL | Interactive shell |
| **erl** | Erlang shell | Interactive shell |

### Migration Workflow

1. **Setup Elixir project**:
```bash
mix new my_app
cd my_app
```

2. **Add Erlang dependencies** (if needed):
```elixir
# mix.exs
defp deps do
  [
    {:erlang_lib, "~> 1.0"}  # Erlang dependency
  ]
end
```

3. **Call Erlang from Elixir**:
```elixir
# Erlang module :my_module
:my_module.function(args)

# Erlang application :my_app
Application.ensure_all_started(:my_app)
```

4. **Gradual migration**: Keep Erlang modules in `src/` directory:
```
my_app/
  lib/           # Elixir code
  src/           # Erlang code (auto-compiled by Mix)
  test/
  mix.exs
```

---

## Examples

### Example 1: Simple - Factorial Function

**Before (Erlang):**
```erlang
-module(math_utils).
-export([factorial/1]).

-spec factorial(non_neg_integer()) -> pos_integer().
factorial(0) -> 1;
factorial(N) when N > 0 -> N * factorial(N - 1).
```

**After (Elixir):**
```elixir
defmodule MathUtils do
  @doc """
  Calculates the factorial of a non-negative integer.
  """
  @spec factorial(non_neg_integer()) :: pos_integer()
  def factorial(0), do: 1
  def factorial(n) when n > 0, do: n * factorial(n - 1)
end
```

---

### Example 2: Medium - Key-Value Store with gen_server

**Before (Erlang):**
```erlang
-module(kv_store).
-behaviour(gen_server).

-export([start_link/0, put/2, get/1, delete/1]).
-export([init/1, handle_call/3, handle_cast/2, terminate/2]).

-record(state, {store = #{} :: map()}).

start_link() ->
    gen_server:start_link({local, ?MODULE}, ?MODULE, [], []).

put(Key, Value) ->
    gen_server:cast(?MODULE, {put, Key, Value}).

get(Key) ->
    gen_server:call(?MODULE, {get, Key}).

delete(Key) ->
    gen_server:cast(?MODULE, {delete, Key}).

init([]) ->
    {ok, #state{store=#{}}}.

handle_call({get, Key}, _From, State = #state{store=Store}) ->
    Reply = maps:get(Key, Store, undefined),
    {reply, Reply, State};
handle_call(_Request, _From, State) ->
    {reply, {error, unknown_request}, State}.

handle_cast({put, Key, Value}, State = #state{store=Store}) ->
    NewStore = maps:put(Key, Value, Store),
    {noreply, State#state{store=NewStore}};
handle_cast({delete, Key}, State = #state{store=Store}) ->
    NewStore = maps:remove(Key, Store),
    {noreply, State#state{store=NewStore}};
handle_cast(_Msg, State) ->
    {noreply, State}.

terminate(_Reason, _State) ->
    ok.
```

**After (Elixir):**
```elixir
defmodule KVStore do
  use GenServer

  # Client API

  @doc """
  Starts the key-value store.
  """
  @spec start_link(keyword()) :: GenServer.on_start()
  def start_link(opts \\ []) do
    GenServer.start_link(__MODULE__, :ok, opts ++ [name: __MODULE__])
  end

  @doc """
  Stores a value under a key.
  """
  @spec put(term(), term()) :: :ok
  def put(key, value) do
    GenServer.cast(__MODULE__, {:put, key, value})
  end

  @doc """
  Retrieves a value by key.
  """
  @spec get(term()) :: term() | nil
  def get(key) do
    GenServer.call(__MODULE__, {:get, key})
  end

  @doc """
  Deletes a key from the store.
  """
  @spec delete(term()) :: :ok
  def delete(key) do
    GenServer.cast(__MODULE__, {:delete, key})
  end

  # Server Callbacks

  @impl true
  def init(:ok) do
    {:ok, %{}}
  end

  @impl true
  def handle_call({:get, key}, _from, state) do
    {:reply, Map.get(state, key), state}
  end

  @impl true
  def handle_cast({:put, key, value}, state) do
    {:noreply, Map.put(state, key, value)}
  end

  @impl true
  def handle_cast({:delete, key}, state) do
    {:noreply, Map.delete(state, key)}
  end

  @impl true
  def terminate(_reason, _state) do
    :ok
  end
end
```

---

### Example 3: Complex - Supervision Tree with Worker Pool

**Before (Erlang):**
```erlang
%% Supervisor
-module(app_supervisor).
-behaviour(supervisor).

-export([start_link/0]).
-export([init/1]).

start_link() ->
    supervisor:start_link({local, ?MODULE}, ?MODULE, []).

init([]) ->
    KVStore = {kv_store,
               {kv_store, start_link, []},
               permanent,
               5000,
               worker,
               [kv_store]},

    WorkerSup = {worker_supervisor,
                 {worker_supervisor, start_link, [5]},
                 permanent,
                 infinity,
                 supervisor,
                 [worker_supervisor]},

    Children = [KVStore, WorkerSup],
    {ok, {{one_for_one, 5, 10}, Children}}.

%% Worker Supervisor
-module(worker_supervisor).
-behaviour(supervisor).

-export([start_link/1, start_worker/1]).
-export([init/1]).

start_link(MaxWorkers) ->
    supervisor:start_link({local, ?MODULE}, ?MODULE, MaxWorkers).

start_worker(Args) ->
    supervisor:start_child(?MODULE, [Args]).

init(MaxWorkers) ->
    Worker = {worker,
              {worker, start_link, []},
              temporary,
              5000,
              worker,
              [worker]},

    {ok, {{simple_one_for_one, 10, 60}, [Worker]}}.

%% Worker
-module(worker).
-behaviour(gen_server).

-export([start_link/1, process/2]).
-export([init/1, handle_call/3, handle_cast/2, terminate/2]).

start_link(Args) ->
    gen_server:start_link(?MODULE, Args, []).

process(Pid, Data) ->
    gen_server:call(Pid, {process, Data}).

init(Args) ->
    {ok, Args}.

handle_call({process, Data}, _From, State) ->
    Result = do_work(Data),
    {reply, {ok, Result}, State}.

handle_cast(_Msg, State) ->
    {noreply, State}.

terminate(_Reason, _State) ->
    ok.

do_work(Data) ->
    % Simulate work
    timer:sleep(100),
    {processed, Data}.
```

**After (Elixir):**
```elixir
# Supervisor
defmodule AppSupervisor do
  use Supervisor

  def start_link(init_arg) do
    Supervisor.start_link(__MODULE__, init_arg, name: __MODULE__)
  end

  @impl true
  def init(_init_arg) do
    children = [
      # KV Store worker
      KVStore,

      # Worker pool supervisor
      {WorkerSupervisor, max_workers: 5}
    ]

    Supervisor.init(children, strategy: :one_for_one, max_restarts: 5, max_seconds: 10)
  end
end

# Worker Supervisor (using DynamicSupervisor for dynamic children)
defmodule WorkerSupervisor do
  use DynamicSupervisor

  def start_link(opts) do
    max_workers = Keyword.get(opts, :max_workers, 10)
    DynamicSupervisor.start_link(__MODULE__, max_workers, name: __MODULE__)
  end

  def start_worker(args) do
    spec = {Worker, args}
    DynamicSupervisor.start_child(__MODULE__, spec)
  end

  @impl true
  def init(max_workers) do
    DynamicSupervisor.init(
      strategy: :one_for_one,
      max_children: max_workers,
      max_restarts: 10,
      max_seconds: 60
    )
  end
end

# Worker
defmodule Worker do
  use GenServer

  # Client API

  def start_link(args) do
    GenServer.start_link(__MODULE__, args)
  end

  def process(pid, data) do
    GenServer.call(pid, {:process, data})
  end

  # Server Callbacks

  @impl true
  def init(args) do
    {:ok, args}
  end

  @impl true
  def handle_call({:process, data}, _from, state) do
    result = do_work(data)
    {:reply, {:ok, result}, state}
  end

  @impl true
  def terminate(_reason, _state) do
    :ok
  end

  # Private Functions

  defp do_work(data) do
    # Simulate work
    Process.sleep(100)
    {:processed, data}
  end
end

# Usage
{:ok, _supervisor} = AppSupervisor.start_link([])
{:ok, worker} = WorkerSupervisor.start_worker([])
{:ok, result} = Worker.process(worker, %{task: "example"})
```

---

## See Also

For more examples and patterns, see:
- `meta-convert-dev` - Foundational patterns with cross-language examples
- `convert-elixir-erlang` - Reverse conversion (Elixir → Erlang)
- `lang-erlang-dev` - Erlang development patterns
- `lang-elixir-dev` - Elixir development patterns
- `lang-elixir-phoenix-dev` - Phoenix framework patterns
- `lang-elixir-ecto-dev` - Database patterns with Ecto

Cross-cutting pattern skills:
- `patterns-concurrency-dev` - Concurrency patterns across languages
- `patterns-supervision-dev` - Supervision tree patterns (if exists)
- `patterns-otp-dev` - OTP design patterns (if exists)
