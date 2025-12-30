---
name: convert-elixir-erlang
description: Convert Elixir code to idiomatic Erlang. Use when migrating Elixir projects to Erlang, translating Elixir patterns to Erlang idioms, or refactoring Elixir codebases to Erlang. Both run on the BEAM VM with the same OTP framework, making this conversion primarily syntactic with semantic preservation. Extends meta-convert-dev with Elixir-to-Erlang specific patterns.
---

# Convert Elixir to Erlang

Convert Elixir code to idiomatic Erlang. Both languages run on the BEAM VM and share OTP foundations, making this conversion primarily about syntax translation while preserving the same underlying semantics and runtime behavior.

## This Skill Extends

- `meta-convert-dev` - Foundational conversion patterns (APTV workflow, testing strategies)

For general concepts like the Analyze → Plan → Transform → Validate workflow, testing strategies, and common pitfalls, see the meta-skill first.

## This Skill Adds

- **Syntax mappings**: Elixir syntax → Erlang syntax (mostly 1:1)
- **Module translations**: Elixir modules → Erlang modules (naming conventions)
- **OTP patterns**: GenServer, Supervisor, Application (nearly identical semantics)
- **Tooling differences**: Mix → Rebar3, Hex → Hex.pm Erlang packages
- **Build system**: mix.exs → rebar.config translation
- **Macro expansion**: Elixir macros → Erlang equivalents (parse transforms or manual expansion)

## This Skill Does NOT Cover

- General conversion methodology - see `meta-convert-dev`
- Elixir language fundamentals - see `lang-elixir-dev`
- Erlang language fundamentals - see `lang-erlang-dev`
- Reverse conversion (Erlang → Elixir) - see `convert-erlang-elixir`
- Phoenix-specific conversions - requires framework expertise

---

## Quick Reference

| Elixir | Erlang | Notes |
|--------|--------|-------|
| `def` | Function clause | No keyword, just pattern matching |
| `defp` | Unexported function | Not in `-export()` list |
| `defmodule MyApp.User` | `-module(my_app_user).` | Nested modules → underscores |
| `@moduledoc "text"` | Module comments | No direct equivalent, use comments |
| `@doc "text"` | Function comments | `-spec` for types, comments for docs |
| `@type` | `-type` | Type specifications (same) |
| `@spec` | `-spec` | Function specs (same) |
| `use GenServer` | `-behaviour(gen_server).` | Behavior vs behaviour spelling |
| `alias MyApp.User` | Qualified calls | No aliasing, use full module names |
| `import Enum` | Qualified calls | No import, use `lists:`, `maps:`, etc. |
| `|>` (pipe) | Nested calls or intermediate vars | No pipe operator |
| `do: expr` | `expr.` | Block syntax vs expression |
| `do ... end` | `begin ... end` or intermediate vars | Multi-line blocks |
| `{:ok, value}` | `{ok, Value}` | Same tuple convention |
| `%{key: value}` | `#{key => value}` | Maps (Erlang 17+) |
| `[h \| t]` | `[H \| T]` | List pattern (same semantics) |
| `"string"` | `<<"binary">>` or `"list"` | Elixir strings are binaries |
| `'charlist'` | `"string"` | Elixir charlists are Erlang strings |

---

## When Converting Code

1. **Understand module structure** - Elixir modules nest; Erlang uses flat names
2. **Expand macros** - `use`, `import`, `alias` expand at compile time
3. **Translate pipe chains** - Convert to nested calls or temporary variables
4. **Map string types** - Elixir strings → Erlang binaries
5. **Preserve OTP semantics** - GenServer, Supervisor, Application are nearly identical
6. **Convert build config** - mix.exs → rebar.config
7. **Test equivalence** - Same inputs → same outputs

---

## Type System Mapping

Both Elixir and Erlang share the same type system (BEAM types). The only differences are syntax.

### Primitive Types

| Elixir | Erlang | Notes |
|--------|--------|-------|
| `1` | `1` | Integers (arbitrary precision) |
| `1.0` | `1.0` | Floats (64-bit) |
| `:atom` | `atom` | Atoms (no `:` prefix in Erlang) |
| `true` | `true` | Boolean (atom) |
| `false` | `false` | Boolean (atom) |
| `nil` | `undefined` | Convention: `nil` → `undefined` or `[]` |
| `"string"` | `<<"string">>` | Elixir strings are UTF-8 binaries |
| `'charlist'` | `"charlist"` | Elixir charlists are Erlang strings |

### Collection Types

| Elixir | Erlang | Notes |
|--------|--------|-------|
| `[1, 2, 3]` | `[1, 2, 3]` | Lists (identical) |
| `{1, 2, 3}` | `{1, 2, 3}` | Tuples (identical) |
| `%{a: 1, b: 2}` | `#{a => 1, b => 2}` | Maps (atom keys) |
| `%{"a" => 1}` | `#{"a" => 1}` | Maps (string keys) |
| `[a: 1, b: 2]` | `[{a, 1}, {b, 2}]` | Keyword lists are proplists |

### Composite Types

| Elixir | Erlang | Notes |
|--------|--------|-------|
| `%User{name: "Alice"}` | `#user{name="Alice"}` | Structs are records |
| `{:ok, value}` | `{ok, Value}` | Tagged tuples (same) |
| `{:error, reason}` | `{error, Reason}` | Error tuples (same) |

---

## Idiom Translation

### Pattern: Module Definition

**Elixir:**
```elixir
defmodule MyApp.User do
  @moduledoc "User module for managing users"

  defstruct [:id, :name, :email]

  @type t :: %__MODULE__{
    id: integer(),
    name: String.t(),
    email: String.t()
  }
end
```

**Erlang:**
```erlang
-module(my_app_user).

%% User module for managing users

-record(user, {
    id :: integer(),
    name :: binary(),
    email :: binary()
}).

-type user() :: #user{}.

-export_type([user/0]).
```

**Why this translation:**
- Nested module names (`MyApp.User`) become underscore-separated (`my_app_user`)
- Structs map directly to records with same field names
- `@moduledoc` becomes regular comments
- Type definitions are nearly identical

---

### Pattern: Function Definition

**Elixir:**
```elixir
defmodule Calculator do
  @doc "Adds two numbers"
  @spec add(number(), number()) :: number()
  def add(a, b), do: a + b

  @doc "Divides two numbers"
  @spec divide(number(), number()) :: {:ok, float()} | {:error, atom()}
  def divide(_a, 0), do: {:error, :division_by_zero}
  def divide(a, b), do: {:ok, a / b}

  # Private function
  defp validate(x) when is_number(x), do: :ok
  defp validate(_), do: :error
end
```

**Erlang:**
```erlang
-module(calculator).

-export([add/2, divide/2]).

%% @doc Adds two numbers
-spec add(number(), number()) -> number().
add(A, B) -> A + B.

%% @doc Divides two numbers
-spec divide(number(), number()) -> {ok, float()} | {error, atom()}.
divide(_A, 0) -> {error, division_by_zero};
divide(A, B) -> {ok, A / B}.

%% Private function (not exported)
validate(X) when is_number(X) -> ok;
validate(_) -> error.
```

**Why this translation:**
- Function clauses separated by `;` in Erlang vs separate `def` in Elixir
- Private functions are just non-exported in Erlang
- Specs use `->` instead of `::`
- One-liner syntax `do: expr` becomes `-> expr.`

---

### Pattern: Pipe Operator

**Elixir:**
```elixir
def process_data(input) do
  input
  |> String.trim()
  |> String.downcase()
  |> String.split(",")
  |> Enum.map(&String.trim/1)
  |> Enum.reject(&(&1 == ""))
end
```

**Erlang (Option 1: Nested calls):**
```erlang
process_data(Input) ->
    lists:filter(
        fun(X) -> X =/= <<>> end,
        lists:map(
            fun(X) -> string:trim(X) end,
            string:split(
                string:lowercase(
                    string:trim(Input)
                ),
                ",",
                all
            )
        )
    ).
```

**Erlang (Option 2: Intermediate variables):**
```erlang
process_data(Input) ->
    Trimmed = string:trim(Input),
    Lowercased = string:lowercase(Trimmed),
    Split = string:split(Lowercased, ",", all),
    Mapped = lists:map(fun(X) -> string:trim(X) end, Split),
    Filtered = lists:filter(fun(X) -> X =/= <<>> end, Mapped),
    Filtered.
```

**Why this translation:**
- Erlang has no pipe operator
- Option 1 (nested) is more compact but harder to read
- Option 2 (intermediate variables) is clearer, closer to Elixir's intent
- Prefer Option 2 for multi-step transformations

---

### Pattern: Pattern Matching and Guards

**Elixir:**
```elixir
defmodule Greeter do
  def greet(:morning), do: "Good morning!"
  def greet(:afternoon), do: "Good afternoon!"
  def greet(:evening), do: "Good evening!"
  def greet(_), do: "Hello!"

  def positive?(x) when is_number(x) and x > 0, do: true
  def positive?(_), do: false
end
```

**Erlang:**
```erlang
-module(greeter).

-export([greet/1, positive/1]).

greet(morning) -> "Good morning!";
greet(afternoon) -> "Good afternoon!";
greet(evening) -> "Good evening!";
greet(_) -> "Hello!".

positive(X) when is_number(X), X > 0 -> true;
positive(_) -> false.
```

**Why this translation:**
- Atoms lose `:` prefix in Erlang
- `and` becomes `,` in guards
- Function clauses separated by `;` instead of separate `def`
- Trailing `.` ends the function definition

---

### Pattern: Anonymous Functions

**Elixir:**
```elixir
# Basic anonymous function
double = fn x -> x * 2 end
double.(5)  # 10

# Shorthand with capture
doubled = Enum.map([1, 2, 3], &(&1 * 2))

# Multiple clauses
handle = fn
  {:ok, result} -> result
  {:error, _} -> nil
end
```

**Erlang:**
```erlang
% Basic anonymous function
Double = fun(X) -> X * 2 end,
Double(5).  % 10

% Map with anonymous function
Doubled = lists:map(fun(X) -> X * 2 end, [1, 2, 3]).

% Multiple clauses
Handle = fun
    ({ok, Result}) -> Result;
    ({error, _}) -> undefined
end.
```

**Why this translation:**
- `fn ... end` becomes `fun ... end`
- No dot-call syntax in Erlang (just `FunName(Args)`)
- Elixir's `&()` capture has no Erlang equivalent
- Multiple clauses separated by `;` in both

---

### Pattern: Enum vs lists/maps

**Elixir:**
```elixir
# List operations
Enum.map([1, 2, 3], &(&1 * 2))
Enum.filter([1, 2, 3, 4], &(rem(&1, 2) == 0))
Enum.reduce([1, 2, 3], 0, &(&1 + &2))
Enum.any?([1, 2, 3], &(&1 > 2))

# Map operations
Map.put(%{a: 1}, :b, 2)
Map.get(%{a: 1}, :a)
Map.keys(%{a: 1, b: 2})
```

**Erlang:**
```erlang
% List operations
lists:map(fun(X) -> X * 2 end, [1, 2, 3]).
lists:filter(fun(X) -> X rem 2 == 0 end, [1, 2, 3, 4]).
lists:foldl(fun(X, Acc) -> X + Acc end, 0, [1, 2, 3]).
lists:any(fun(X) -> X > 2 end, [1, 2, 3]).

% Map operations
maps:put(b, 2, #{a => 1}).
maps:get(a, #{a => 1}).
maps:keys(#{a => 1, b => 2}).
```

**Why this translation:**
- `Enum` → `lists` for list operations
- `Map` → `maps` for map operations
- Function arguments order may differ slightly
- Erlang often puts function/predicate first, data last

---

### Pattern: with Statement

**Elixir:**
```elixir
def create_user(params) do
  with {:ok, validated} <- validate_params(params),
       {:ok, user} <- insert_user(validated),
       {:ok, email} <- send_welcome_email(user) do
    {:ok, user}
  else
    {:error, reason} -> {:error, reason}
  end
end
```

**Erlang:**
```erlang
create_user(Params) ->
    case validate_params(Params) of
        {ok, Validated} ->
            case insert_user(Validated) of
                {ok, User} ->
                    case send_welcome_email(User) of
                        {ok, _Email} ->
                            {ok, User};
                        {error, Reason} ->
                            {error, Reason}
                    end;
                {error, Reason} ->
                    {error, Reason}
            end;
        {error, Reason} ->
            {error, Reason}
    end.
```

**Why this translation:**
- Erlang has no `with`; use nested `case` statements
- Alternative: use a helper function with multiple clauses
- More verbose but same semantics

---

## Error Handling

Both Elixir and Erlang use the same error handling philosophies on the BEAM:
- **Let it crash** for unexpected errors
- **Tagged tuples** (`{:ok, value}` / `{:error, reason}`) for expected failures
- **Supervision trees** for fault tolerance

### Error Model Comparison

| Elixir | Erlang | Notes |
|--------|--------|-------|
| `raise "error"` | `error(Reason)` | Raises exception |
| `throw :value` | `throw(Value)` | Throws value |
| `exit :normal` | `exit(normal)` | Exits process |
| `try ... rescue` | `try ... catch error:...` | Catching errors |
| `try ... catch` | `try ... catch throw:...` | Catching throws |
| `{:ok, value}` | `{ok, Value}` | Success tuple (same) |
| `{:error, reason}` | `{error, Reason}` | Error tuple (same) |

### Exception Handling

**Elixir:**
```elixir
defmodule FileReader do
  def read_file(path) do
    try do
      File.read!(path)
    rescue
      e in File.Error -> {:error, e.reason}
    end
  end

  def divide(a, b) do
    try do
      {:ok, a / b}
    rescue
      ArithmeticError -> {:error, :division_by_zero}
    end
  end
end
```

**Erlang:**
```erlang
-module(file_reader).

-export([read_file/1, divide/2]).

read_file(Path) ->
    try
        {ok, Binary} = file:read_file(Path),
        {ok, Binary}
    catch
        error:{badmatch, {error, Reason}} ->
            {error, Reason}
    end.

divide(A, B) ->
    try
        {ok, A / B}
    catch
        error:badarith ->
            {error, division_by_zero}
    end.
```

**Why this translation:**
- `rescue` → `catch error:Pattern`
- Exception types map to error patterns
- Prefer idiomatic result tuples over exceptions

---

## Concurrency Patterns

Since both languages run on BEAM, concurrency patterns are nearly identical.

### Spawning Processes

**Elixir:**
```elixir
# Spawn process
pid = spawn(fn -> loop() end)

# Spawn with module/function/args
pid = spawn(MyModule, :my_function, [arg1, arg2])

# Spawn linked
pid = spawn_link(fn -> worker() end)
```

**Erlang:**
```erlang
% Spawn process
Pid = spawn(fun() -> loop() end).

% Spawn with module/function/args
Pid = spawn(my_module, my_function, [Arg1, Arg2]).

% Spawn linked
Pid = spawn_link(fun() -> worker() end).
```

**Why this translation:**
- Identical semantics, slightly different syntax
- Elixir atoms (`:atom`) become Erlang atoms (`atom`)

---

### Message Passing

**Elixir:**
```elixir
# Send message
send(pid, {:hello, "world"})

# Receive message
receive do
  {:hello, msg} -> IO.puts("Received: #{msg}")
  :stop -> :ok
after
  5000 -> :timeout
end
```

**Erlang:**
```erlang
% Send message
Pid ! {hello, "world"}.

% Receive message
receive
    {hello, Msg} ->
        io:format("Received: ~s~n", [Msg]);
    stop ->
        ok
after 5000 ->
    timeout
end.
```

**Why this translation:**
- `send(pid, msg)` → `Pid ! Msg`
- `receive do ... end` → `receive ... end`
- Same timeout syntax

---

### GenServer

**Elixir:**
```elixir
defmodule Counter do
  use GenServer

  # Client API
  def start_link(initial_value) do
    GenServer.start_link(__MODULE__, initial_value, name: __MODULE__)
  end

  def increment do
    GenServer.cast(__MODULE__, :increment)
  end

  def get do
    GenServer.call(__MODULE__, :get)
  end

  # Server Callbacks
  @impl true
  def init(initial_value) do
    {:ok, initial_value}
  end

  @impl true
  def handle_call(:get, _from, state) do
    {:reply, state, state}
  end

  @impl true
  def handle_cast(:increment, state) do
    {:noreply, state + 1}
  end
end
```

**Erlang:**
```erlang
-module(counter).
-behaviour(gen_server).

%% API
-export([start_link/1, increment/0, get/0]).

%% gen_server callbacks
-export([init/1, handle_call/3, handle_cast/2, handle_info/2, terminate/2, code_change/3]).

-define(SERVER, ?MODULE).

%%% API Functions

start_link(InitialValue) ->
    gen_server:start_link({local, ?SERVER}, ?MODULE, InitialValue, []).

increment() ->
    gen_server:cast(?SERVER, increment).

get() ->
    gen_server:call(?SERVER, get).

%%% gen_server Callbacks

init(InitialValue) ->
    {ok, InitialValue}.

handle_call(get, _From, State) ->
    {reply, State, State}.

handle_cast(increment, State) ->
    {noreply, State + 1}.

handle_info(_Info, State) ->
    {noreply, State}.

terminate(_Reason, _State) ->
    ok.

code_change(_OldVsn, State, _Extra) ->
    {ok, State}.
```

**Why this translation:**
- `use GenServer` → `-behaviour(gen_server).` + exports
- `@impl true` annotations are optional in Erlang
- Callback signatures identical
- Atoms lose `:` prefix

---

### Supervisor

**Elixir:**
```elixir
defmodule MyApp.Supervisor do
  use Supervisor

  def start_link(init_arg) do
    Supervisor.start_link(__MODULE__, init_arg, name: __MODULE__)
  end

  @impl true
  def init(_init_arg) do
    children = [
      {Counter, 0},
      {Worker, []}
    ]

    Supervisor.init(children, strategy: :one_for_one)
  end
end
```

**Erlang:**
```erlang
-module(my_app_supervisor).
-behaviour(supervisor).

-export([start_link/1, init/1]).

start_link(InitArg) ->
    supervisor:start_link({local, ?MODULE}, ?MODULE, InitArg).

init(_InitArg) ->
    SupFlags = #{
        strategy => one_for_one,
        intensity => 5,
        period => 60
    },

    ChildSpecs = [
        #{
            id => counter,
            start => {counter, start_link, [0]},
            restart => permanent,
            shutdown => 5000,
            type => worker,
            modules => [counter]
        },
        #{
            id => worker,
            start => {worker, start_link, []},
            restart => permanent,
            shutdown => 5000,
            type => worker,
            modules => [worker]
        }
    ],

    {ok, {SupFlags, ChildSpecs}}.
```

**Why this translation:**
- `use Supervisor` → `-behaviour(supervisor).`
- Elixir's shorthand child specs expand to full maps in Erlang
- Supervisor flags more explicit in Erlang

---

## Module System Translation

### Aliases and Imports

**Elixir:**
```elixir
defmodule MyApp.User do
  alias MyApp.Repo
  import Ecto.Changeset

  def create(params) do
    %__MODULE__{}
    |> cast(params, [:name, :email])
    |> validate_required([:name, :email])
    |> Repo.insert()
  end
end
```

**Erlang:**
```erlang
-module(my_app_user).

-export([create/1]).

create(Params) ->
    Changeset = ecto_changeset:cast(#{}, Params, [name, email]),
    Validated = ecto_changeset:validate_required(Changeset, [name, email]),
    my_app_repo:insert(Validated).
```

**Why this translation:**
- Erlang has no `alias` or `import`; always use qualified module names
- `MyApp.Repo` → `my_app_repo`
- Nested modules become flat with underscores

---

### Module Attributes

**Elixir:**
```elixir
defmodule Config do
  @pi 3.14159
  @timeout 5000

  def circle_area(radius), do: @pi * radius * radius
  def get_timeout, do: @timeout
end
```

**Erlang:**
```erlang
-module(config).

-export([circle_area/1, get_timeout/0]).

-define(PI, 3.14159).
-define(TIMEOUT, 5000).

circle_area(Radius) ->
    ?PI * Radius * Radius.

get_timeout() ->
    ?TIMEOUT.
```

**Why this translation:**
- Module attributes (`@attr`) → Macros (`-define()`)
- Access with `?MACRO` instead of `@attr`

---

## Tooling

### Build System

| Elixir (Mix) | Erlang (Rebar3) | Notes |
|--------------|-----------------|-------|
| `mix.exs` | `rebar.config` | Project configuration |
| `mix compile` | `rebar3 compile` | Compile project |
| `mix test` | `rebar3 eunit` or `rebar3 ct` | Run tests |
| `mix deps.get` | `rebar3 deps` | Fetch dependencies |
| `iex -S mix` | `rebar3 shell` | Interactive shell |
| `mix release` | `rebar3 release` | Build release |

### Dependency Management

**Elixir (mix.exs):**
```elixir
defp deps do
  [
    {:phoenix, "~> 1.7"},
    {:ecto_sql, "~> 3.10"},
    {:jason, "~> 1.4"}
  ]
end
```

**Erlang (rebar.config):**
```erlang
{deps, [
    {cowboy, "2.10.0"},
    {jsx, "3.1.0"},
    {epgsql, "4.7.0"}
]}.
```

---

## Common Pitfalls

### 1. String vs Binary Confusion

**Problem:** Elixir strings are UTF-8 binaries; Erlang strings are charlists.

```elixir
# Elixir
name = "Alice"  # Binary: <<"Alice">>
charlist = 'Alice'  # List: [65, 108, 105, 99, 101]
```

```erlang
% Erlang
Name = <<"Alice">>.  % Binary (Elixir string equivalent)
Charlist = "Alice".  % List (Erlang string, Elixir charlist equivalent)
```

**Solution:** Always translate Elixir `"strings"` to Erlang binaries `<<"strings">>`.

---

### 2. Atom Prefixes

**Problem:** Elixir atoms have `:` prefix; Erlang atoms don't.

```elixir
# Elixir
:ok
:error
:atom_name
```

```erlang
% Erlang
ok.
error.
atom_name.
```

**Solution:** Remove `:` prefix when converting.

---

### 3. Pipe Operator

**Problem:** Erlang has no pipe operator.

```elixir
# Elixir
result = data
  |> transform()
  |> validate()
  |> save()
```

```erlang
% Erlang (nested)
Result = save(validate(transform(Data))).

% OR (intermediate variables - preferred)
Transformed = transform(Data),
Validated = validate(Transformed),
Result = save(Validated).
```

**Solution:** Use intermediate variables for clarity.

---

### 4. Macro Expansion

**Problem:** Elixir macros (`use`, `import`, `alias`) must be manually expanded.

```elixir
# Elixir
use GenServer  # Expands to imports, aliases, default implementations
```

```erlang
% Erlang
-behaviour(gen_server).
-export([init/1, handle_call/3, handle_cast/2, ...]).
% Must implement all callbacks manually
```

**Solution:** Check Elixir macro documentation and expand manually.

---

### 5. Function Naming Conventions

**Problem:** Elixir uses `?` and `!` suffixes; Erlang doesn't.

```elixir
# Elixir
def valid?(x), do: ...
def fetch!(key), do: ...
```

```erlang
% Erlang
is_valid(X) -> ...
fetch_or_error(Key) -> ...
```

**Solution:**
- `predicate?` → `is_predicate` or `predicate`
- `function!` → `function_or_error` or just `function`

---

## Examples

### Example 1: Simple - Module with Functions

**Before (Elixir):**
```elixir
defmodule Math do
  @moduledoc "Basic math operations"

  @doc "Adds two numbers"
  @spec add(number(), number()) :: number()
  def add(a, b), do: a + b

  @doc "Multiplies two numbers"
  @spec multiply(number(), number()) :: number()
  def multiply(a, b), do: a * b

  defp validate(x) when is_number(x), do: :ok
  defp validate(_), do: :error
end
```

**After (Erlang):**
```erlang
-module(math).

%% Basic math operations

-export([add/2, multiply/2]).

%% @doc Adds two numbers
-spec add(number(), number()) -> number().
add(A, B) -> A + B.

%% @doc Multiplies two numbers
-spec multiply(number(), number()) -> number().
multiply(A, B) -> A * B.

%% Private function (not exported)
validate(X) when is_number(X) -> ok;
validate(_) -> error.
```

---

### Example 2: Medium - GenServer with State

**Before (Elixir):**
```elixir
defmodule UserCache do
  use GenServer

  # Client API
  def start_link(_opts) do
    GenServer.start_link(__MODULE__, %{}, name: __MODULE__)
  end

  def put(id, user) do
    GenServer.cast(__MODULE__, {:put, id, user})
  end

  def get(id) do
    GenServer.call(__MODULE__, {:get, id})
  end

  # Server Callbacks
  @impl true
  def init(_) do
    {:ok, %{}}
  end

  @impl true
  def handle_call({:get, id}, _from, state) do
    {:reply, Map.get(state, id), state}
  end

  @impl true
  def handle_cast({:put, id, user}, state) do
    {:noreply, Map.put(state, id, user)}
  end
end
```

**After (Erlang):**
```erlang
-module(user_cache).
-behaviour(gen_server).

%% API
-export([start_link/1, put/2, get/1]).

%% gen_server callbacks
-export([init/1, handle_call/3, handle_cast/2, handle_info/2, terminate/2, code_change/3]).

-define(SERVER, ?MODULE).

%%% API Functions

start_link(_Opts) ->
    gen_server:start_link({local, ?SERVER}, ?MODULE, [], []).

put(Id, User) ->
    gen_server:cast(?SERVER, {put, Id, User}).

get(Id) ->
    gen_server:call(?SERVER, {get, Id}).

%%% gen_server Callbacks

init(_) ->
    {ok, #{}}.

handle_call({get, Id}, _From, State) ->
    {reply, maps:get(Id, State, undefined), State}.

handle_cast({put, Id, User}, State) ->
    {noreply, maps:put(Id, User, State)}.

handle_info(_Info, State) ->
    {noreply, State}.

terminate(_Reason, _State) ->
    ok.

code_change(_OldVsn, State, _Extra) ->
    {ok, State}.
```

---

### Example 3: Complex - Pipeline with Error Handling

**Before (Elixir):**
```elixir
defmodule UserService do
  @moduledoc "User management service"

  alias MyApp.{Repo, User, Mailer}

  def create_user(params) do
    with {:ok, validated} <- validate_params(params),
         {:ok, user} <- insert_user(validated),
         {:ok, _email} <- send_welcome_email(user) do
      {:ok, user}
    else
      {:error, :invalid_email} -> {:error, "Email format is invalid"}
      {:error, :duplicate_email} -> {:error, "Email already exists"}
      {:error, reason} -> {:error, reason}
    end
  end

  defp validate_params(%{email: email, name: name})
    when is_binary(email) and is_binary(name) do
    if String.contains?(email, "@") do
      {:ok, %{email: email, name: name}}
    else
      {:error, :invalid_email}
    end
  end
  defp validate_params(_), do: {:error, :invalid_params}

  defp insert_user(params) do
    case Repo.insert(%User{email: params.email, name: params.name}) do
      {:ok, user} -> {:ok, user}
      {:error, changeset} ->
        if changeset.errors[:email] == {"has already been taken", []} do
          {:error, :duplicate_email}
        else
          {:error, :database_error}
        end
    end
  end

  defp send_welcome_email(user) do
    Mailer.send_email(user.email, "Welcome!", "Welcome to our service!")
  end
end
```

**After (Erlang):**
```erlang
-module(user_service).

%% User management service

-export([create_user/1]).

-record(user, {
    email :: binary(),
    name :: binary()
}).

create_user(Params) ->
    case validate_params(Params) of
        {ok, Validated} ->
            case insert_user(Validated) of
                {ok, User} ->
                    case send_welcome_email(User) of
                        {ok, _Email} ->
                            {ok, User};
                        {error, Reason} ->
                            {error, Reason}
                    end;
                {error, duplicate_email} ->
                    {error, <<"Email already exists">>};
                {error, Reason} ->
                    {error, Reason}
            end;
        {error, invalid_email} ->
            {error, <<"Email format is invalid">>};
        {error, Reason} ->
            {error, Reason}
    end.

%% Private functions

validate_params(#{email := Email, name := Name})
    when is_binary(Email), is_binary(Name) ->
    case binary:match(Email, <<"@">>) of
        {_Pos, _Len} ->
            {ok, #{email => Email, name => Name}};
        nomatch ->
            {error, invalid_email}
    end;
validate_params(_) ->
    {error, invalid_params}.

insert_user(#{email := Email, name := Name}) ->
    User = #user{email = Email, name = Name},
    case my_app_repo:insert(User) of
        {ok, InsertedUser} ->
            {ok, InsertedUser};
        {error, Changeset} ->
            case check_duplicate_email(Changeset) of
                true -> {error, duplicate_email};
                false -> {error, database_error}
            end
    end.

send_welcome_email(#user{email = Email}) ->
    mailer:send_email(Email, <<"Welcome!">>, <<"Welcome to our service!">>).

check_duplicate_email(Changeset) ->
    %% Check changeset for duplicate email error
    %% Implementation depends on repo library
    false.
```

---

## See Also

For more examples and patterns, see:
- `meta-convert-dev` - Foundational patterns with cross-language examples
- `convert-erlang-elixir` - Reverse conversion (Erlang → Elixir)
- `lang-elixir-dev` - Elixir development patterns
- `lang-erlang-dev` - Erlang development patterns

Cross-cutting pattern skills:
- `patterns-concurrency-dev` - Process patterns, GenServer, Supervisor across languages
- `patterns-serialization-dev` - JSON, ETF, protocol buffers across languages
- `patterns-metaprogramming-dev` - Macros, parse transforms, behaviors across languages
