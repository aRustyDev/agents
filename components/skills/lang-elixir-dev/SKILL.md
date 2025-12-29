---
name: lang-elixir-dev
description: Foundational Elixir patterns covering modules, pattern matching, processes, OTP behaviors (GenServer, Supervisor), Phoenix framework basics, and functional programming idioms. Use when writing Elixir code, building concurrent systems, working with Phoenix, or needing guidance on Elixir development patterns. This is the entry point for Elixir development.
---

# Elixir Fundamentals

Foundational Elixir patterns and core language features. This skill serves as both a reference for common patterns and an index to specialized Elixir skills.

## Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Elixir Skill Hierarchy                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│                  ┌───────────────────┐                          │
│                  │ lang-elixir-dev   │ ◄── You are here         │
│                  │   (foundation)    │                          │
│                  └─────────┬─────────┘                          │
│                            │                                    │
│       ┌────────────────────┼────────────────────┐               │
│       │                    │                    │               │
│       ▼                    ▼                    ▼               │
│  ┌─────────┐        ┌──────────┐        ┌──────────┐           │
│  │ phoenix │        │   otp    │        │  ecto    │           │
│  │  -dev   │        │  -dev    │        │  -dev    │           │
│  └─────────┘        └──────────┘        └──────────┘           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**This skill covers:**
- Core syntax (modules, functions, pattern matching)
- Data types and immutability
- Pattern matching and guards
- Processes and message passing
- OTP basics (GenServer, Supervisor)
- Mix project structure
- Common functional programming idioms
- Phoenix framework fundamentals

**This skill does NOT cover (see specialized skills):**
- Advanced Phoenix features → `lang-elixir-phoenix-dev`
- Advanced OTP patterns → `lang-elixir-otp-dev`
- Database patterns with Ecto → `lang-elixir-ecto-dev`
- Deployment and releases → `lang-elixir-deploy-dev`
- Testing patterns → `lang-elixir-testing-dev`

---

## Quick Reference

| Task | Pattern |
|------|---------|
| Define module | `defmodule MyModule do ... end` |
| Define function | `def function_name(args), do: result` |
| Private function | `defp private_function(args), do: result` |
| Pattern match | `{:ok, value} = result` |
| Pipe operator | `value \|> function1() \|> function2()` |
| Spawn process | `spawn(fn -> ... end)` |
| Send message | `send(pid, message)` |
| Receive message | `receive do pattern -> ... end` |
| GenServer call | `GenServer.call(pid, message)` |
| Supervisor start | `Supervisor.start_link(children, opts)` |

---

## Skill Routing

Use this table to find the right specialized skill:

| When you need to... | Use this skill |
|---------------------|----------------|
| Build web applications with Phoenix | `lang-elixir-phoenix-dev` |
| Design advanced OTP architectures | `lang-elixir-otp-dev` |
| Work with databases using Ecto | `lang-elixir-ecto-dev` |
| Deploy applications, create releases | `lang-elixir-deploy-dev` |
| Write tests with ExUnit | `lang-elixir-testing-dev` |

---

## Core Data Types

### Atoms

```elixir
# Atoms are constants where name is the value
:ok
:error
:atom_name
:"atom with spaces"

# Boolean atoms
true  # Same as :true
false # Same as :false
nil   # Same as :nil

# Module names are atoms
IO      # Same as :"Elixir.IO"
String  # Same as :"Elixir.String"
```

### Numbers

```elixir
# Integers (arbitrary precision)
42
1_000_000
0x1F  # Hexadecimal
0o777 # Octal
0b1010 # Binary

# Floats (64-bit double precision)
3.14
1.0e-10
```

### Strings and Charlists

```elixir
# Strings (UTF-8 binaries)
"hello"
"hello #{name}"  # Interpolation
"multi
line
string"

# String operations
String.upcase("hello")      # "HELLO"
String.length("hello")      # 5
String.split("a,b,c", ",")  # ["a", "b", "c"]
String.replace("hello", "l", "x")  # "hexxo"

# Charlists (lists of integers)
'hello'  # [104, 101, 108, 108, 111]
'hello' ++ ' world'  # 'hello world'
```

### Lists

```elixir
# Lists (linked lists)
[1, 2, 3]
[head | tail] = [1, 2, 3]  # head = 1, tail = [2, 3]

# List operations
[1, 2] ++ [3, 4]     # [1, 2, 3, 4] (concatenation)
[1, 2, 3] -- [2]     # [1, 3] (difference)
hd([1, 2, 3])        # 1 (head)
tl([1, 2, 3])        # [2, 3] (tail)
length([1, 2, 3])    # 3

# List module
Enum.map([1, 2, 3], fn x -> x * 2 end)  # [2, 4, 6]
Enum.filter([1, 2, 3], fn x -> rem(x, 2) == 0 end)  # [2]
Enum.reduce([1, 2, 3], 0, fn x, acc -> x + acc end)  # 6
```

### Tuples

```elixir
# Tuples (contiguous memory)
{:ok, "value"}
{:error, :not_found}
{1, 2, 3}

# Common pattern: tagged tuples
def divide(a, b) when b != 0, do: {:ok, a / b}
def divide(_, 0), do: {:error, :division_by_zero}

# Tuple operations
elem({:ok, 42}, 0)           # :ok
put_elem({:a, :b}, 1, :c)    # {:a, :c}
tuple_size({:a, :b, :c})     # 3
```

### Maps

```elixir
# Maps (key-value stores)
%{:name => "Alice", :age => 30}
%{name: "Alice", age: 30}  # Shorthand for atom keys

# Accessing values
map = %{name: "Alice", age: 30}
map[:name]       # "Alice"
map.name         # "Alice" (only for atom keys)

# Updating maps
%{map | age: 31}  # Update existing key
Map.put(map, :city, "NYC")  # Add new key
Map.delete(map, :age)  # Remove key

# Pattern matching
%{name: name} = %{name: "Alice", age: 30}  # name = "Alice"

# Map operations
Map.keys(map)       # [:name, :age]
Map.values(map)     # ["Alice", 30]
Map.merge(map1, map2)  # Merge maps
```

### Keyword Lists

```elixir
# Keyword lists (lists of 2-tuples with atom keys)
[name: "Alice", age: 30]
# Same as: [{:name, "Alice"}, {:age, 30}]

# Common in function options
String.split("a,b,c", ",", trim: true)

# Accessing values
list = [name: "Alice", age: 30]
list[:name]  # "Alice"
Keyword.get(list, :name)  # "Alice"

# Can have duplicate keys
[a: 1, a: 2, a: 3]
```

---

## Pattern Matching

### Basic Patterns

```elixir
# Match operator
{a, b, c} = {1, 2, 3}  # a=1, b=2, c=3

# List matching
[head | tail] = [1, 2, 3]  # head=1, tail=[2,3]
[first, second | rest] = [1, 2, 3, 4]  # first=1, second=2, rest=[3,4]

# Tuple matching
{:ok, result} = {:ok, 42}  # result=42
{:error, reason} = {:error, :not_found}  # reason=:not_found

# Map matching
%{name: name} = %{name: "Alice", age: 30}  # name="Alice"
%{name: name, age: age} = %{name: "Alice", age: 30}

# Pin operator (match against value)
x = 1
^x = 1  # OK
^x = 2  # MatchError
```

### Function Pattern Matching

```elixir
# Multiple function clauses
def greet(:morning), do: "Good morning!"
def greet(:afternoon), do: "Good afternoon!"
def greet(:evening), do: "Good evening!"

# Pattern match on structure
def handle_response({:ok, data}), do: process(data)
def handle_response({:error, reason}), do: handle_error(reason)

# Pattern match on lists
def sum([]), do: 0
def sum([head | tail]), do: head + sum(tail)

# Ignore values with underscore
def process({:ok, _}), do: :success
def process({:error, reason}), do: {:failed, reason}
```

### Guards

```elixir
# Guard clauses
def positive?(x) when x > 0, do: true
def positive?(_), do: false

# Multiple guards (AND)
def adult?(age) when is_integer(age) and age >= 18, do: true
def adult?(_), do: false

# Multiple guards (OR)
def number?(x) when is_integer(x) or is_float(x), do: true
def number?(_), do: false

# Common guard functions
is_atom(x)
is_binary(x)
is_boolean(x)
is_list(x)
is_map(x)
is_number(x)
is_tuple(x)
is_nil(x)
```

---

## Modules and Functions

### Module Definition

```elixir
defmodule Math do
  # Module attribute (compile-time constant)
  @pi 3.14159

  # Public function
  def circle_area(radius) do
    @pi * radius * radius
  end

  # Private function
  defp validate_radius(radius) when radius > 0, do: :ok
  defp validate_radius(_), do: :error

  # One-line function
  def double(x), do: x * 2

  # Function with multiple clauses
  def factorial(0), do: 1
  def factorial(n) when n > 0, do: n * factorial(n - 1)

  # Function with default arguments
  def greet(name, greeting \\ "Hello") do
    "#{greeting}, #{name}!"
  end
end
```

### Anonymous Functions

```elixir
# Define anonymous function
add = fn a, b -> a + b end
add.(1, 2)  # 3 (note the dot)

# Shorthand syntax
add = &(&1 + &2)
add.(1, 2)  # 3

# Capture operator with named functions
doubled = Enum.map([1, 2, 3], &(&1 * 2))
lengths = Enum.map(["a", "ab", "abc"], &String.length/1)

# Multiple clauses
handle = fn
  {:ok, result} -> result
  {:error, _} -> nil
end
```

### Function Composition

```elixir
# Pipe operator
"hello"
|> String.upcase()
|> String.reverse()
# "OLLEH"

# Function capture
numbers = [1, 2, 3, 4, 5]
evens = Enum.filter(numbers, &(rem(&1, 2) == 0))

# Composition example
def process_data(data) do
  data
  |> String.trim()
  |> String.downcase()
  |> String.split(",")
  |> Enum.map(&String.trim/1)
  |> Enum.reject(&(&1 == ""))
end
```

---

## Processes and Concurrency

### Spawning Processes

```elixir
# Spawn a process
pid = spawn(fn ->
  receive do
    {:hello, sender} -> send(sender, {:ok, "Hello back!"})
  end
end)

# Send message
send(pid, {:hello, self()})

# Receive message
receive do
  {:ok, message} -> IO.puts(message)
after
  1000 -> IO.puts("Timeout!")
end
```

### Process Links and Monitoring

```elixir
# Spawn linked process (failures propagate)
pid = spawn_link(fn -> raise "Error!" end)

# Trap exits to handle linked process failures
Process.flag(:trap_exit, true)
receive do
  {:EXIT, pid, reason} -> IO.puts("Process died: #{inspect(reason)}")
end

# Monitor process (doesn't link)
{:ok, pid} = some_process()
ref = Process.monitor(pid)
receive do
  {:DOWN, ^ref, :process, ^pid, reason} ->
    IO.puts("Process down: #{inspect(reason)}")
end
```

### Process State with Recursion

```elixir
# Counter process
defmodule Counter do
  def start(initial_value) do
    spawn(fn -> loop(initial_value) end)
  end

  defp loop(value) do
    receive do
      {:increment, caller} ->
        send(caller, {:ok, value + 1})
        loop(value + 1)

      {:get, caller} ->
        send(caller, {:ok, value})
        loop(value)

      :stop ->
        :ok
    end
  end
end

# Usage
counter = Counter.start(0)
send(counter, {:increment, self()})
receive do
  {:ok, new_value} -> IO.puts("New value: #{new_value}")
end
```

---

## OTP Basics

### GenServer

```elixir
defmodule Stack do
  use GenServer

  # Client API

  def start_link(initial_stack) do
    GenServer.start_link(__MODULE__, initial_stack, name: __MODULE__)
  end

  def push(item) do
    GenServer.cast(__MODULE__, {:push, item})
  end

  def pop do
    GenServer.call(__MODULE__, :pop)
  end

  # Server Callbacks

  @impl true
  def init(initial_stack) do
    {:ok, initial_stack}
  end

  @impl true
  def handle_call(:pop, _from, [head | tail]) do
    {:reply, head, tail}
  end

  def handle_call(:pop, _from, []) do
    {:reply, nil, []}
  end

  @impl true
  def handle_cast({:push, item}, state) do
    {:noreply, [item | state]}
  end
end

# Usage
{:ok, _pid} = Stack.start_link([])
Stack.push(1)
Stack.push(2)
Stack.pop()  # 2
```

### Supervisor

```elixir
defmodule MyApp.Application do
  use Application

  @impl true
  def start(_type, _args) do
    children = [
      # Worker
      {Stack, []},
      # Worker with custom config
      {MyWorker, name: MyWorker, restart: :transient},
      # Supervisor
      {Registry, keys: :unique, name: MyApp.Registry}
    ]

    opts = [strategy: :one_for_one, name: MyApp.Supervisor]
    Supervisor.start_link(children, opts)
  end
end

# Restart strategies:
# :one_for_one - restart only failed child
# :one_for_all - restart all children if one fails
# :rest_for_one - restart failed child and those started after it
```

### GenServer with State Management

```elixir
defmodule Counter do
  use GenServer

  # Client

  def start_link(initial_value \\ 0) do
    GenServer.start_link(__MODULE__, initial_value, name: __MODULE__)
  end

  def increment do
    GenServer.call(__MODULE__, :increment)
  end

  def get do
    GenServer.call(__MODULE__, :get)
  end

  def async_increment do
    GenServer.cast(__MODULE__, :increment)
  end

  # Server

  @impl true
  def init(initial_value) do
    {:ok, initial_value}
  end

  @impl true
  def handle_call(:increment, _from, state) do
    {:reply, state + 1, state + 1}
  end

  def handle_call(:get, _from, state) do
    {:reply, state, state}
  end

  @impl true
  def handle_cast(:increment, state) do
    {:noreply, state + 1}
  end
end
```

---

## Mix Project Structure

### Creating a New Project

```bash
# Create new project
mix new my_app

# Create new supervised application
mix new my_app --sup

# Project structure:
# my_app/
# ├── lib/
# │   ├── my_app.ex
# │   └── my_app/
# │       └── application.ex
# ├── test/
# │   ├── my_app_test.exs
# │   └── test_helper.exs
# ├── mix.exs
# └── README.md
```

### mix.exs Configuration

```elixir
defmodule MyApp.MixProject do
  use Mix.Project

  def project do
    [
      app: :my_app,
      version: "0.1.0",
      elixir: "~> 1.14",
      start_permanent: Mix.env() == :prod,
      deps: deps()
    ]
  end

  def application do
    [
      extra_applications: [:logger],
      mod: {MyApp.Application, []}
    ]
  end

  defp deps do
    [
      {:phoenix, "~> 1.7"},
      {:ecto_sql, "~> 3.10"},
      {:postgrex, ">= 0.0.0"},
      {:jason, "~> 1.4"},
      {:plug_cowboy, "~> 2.6"}
    ]
  end
end
```

### Common Mix Tasks

```bash
# Compile project
mix compile

# Run tests
mix test

# Run application
mix run --no-halt

# Interactive shell
iex -S mix

# Get dependencies
mix deps.get

# Format code
mix format

# Create new module
mix phx.gen.context Accounts User users name:string email:string
```

---

## Phoenix Framework Basics

### Phoenix Project Structure

```
my_app/
├── assets/           # Frontend assets
├── config/           # Configuration
├── lib/
│   ├── my_app/       # Business logic
│   ├── my_app_web/   # Web interface
│   │   ├── controllers/
│   │   ├── views/
│   │   ├── templates/
│   │   └── router.ex
│   └── my_app.ex
├── priv/             # Database migrations, static files
└── test/
```

### Router

```elixir
defmodule MyAppWeb.Router do
  use MyAppWeb, :router

  pipeline :browser do
    plug :accepts, ["html"]
    plug :fetch_session
    plug :fetch_flash
    plug :protect_from_forgery
    plug :put_secure_browser_headers
  end

  pipeline :api do
    plug :accepts, ["json"]
  end

  scope "/", MyAppWeb do
    pipe_through :browser

    get "/", PageController, :index
    resources "/users", UserController
  end

  scope "/api", MyAppWeb do
    pipe_through :api

    resources "/posts", PostController, except: [:new, :edit]
  end
end
```

### Controller

```elixir
defmodule MyAppWeb.UserController do
  use MyAppWeb, :controller

  alias MyApp.Accounts
  alias MyApp.Accounts.User

  def index(conn, _params) do
    users = Accounts.list_users()
    render(conn, "index.html", users: users)
  end

  def show(conn, %{"id" => id}) do
    user = Accounts.get_user!(id)
    render(conn, "show.html", user: user)
  end

  def create(conn, %{"user" => user_params}) do
    case Accounts.create_user(user_params) do
      {:ok, user} ->
        conn
        |> put_flash(:info, "User created successfully.")
        |> redirect(to: ~p"/users/#{user}")

      {:error, %Ecto.Changeset{} = changeset} ->
        render(conn, "new.html", changeset: changeset)
    end
  end
end
```

### LiveView Basics

```elixir
defmodule MyAppWeb.CounterLive do
  use MyAppWeb, :live_view

  @impl true
  def mount(_params, _session, socket) do
    {:ok, assign(socket, count: 0)}
  end

  @impl true
  def handle_event("increment", _params, socket) do
    {:noreply, update(socket, :count, &(&1 + 1))}
  end

  def handle_event("decrement", _params, socket) do
    {:noreply, update(socket, :count, &(&1 - 1))}
  end

  @impl true
  def render(assigns) do
    ~H"""
    <div>
      <h1>Count: <%= @count %></h1>
      <button phx-click="increment">+</button>
      <button phx-click="decrement">-</button>
    </div>
    """
  end
end
```

---

## Common Patterns and Idioms

### With Statement

```elixir
# Chain operations that can fail
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

### Case Statement

```elixir
case File.read("config.json") do
  {:ok, contents} ->
    Jason.decode(contents)

  {:error, :enoent} ->
    {:error, "File not found"}

  {:error, reason} ->
    {:error, "Read error: #{inspect(reason)}"}
end
```

### Cond Statement

```elixir
cond do
  age < 13 -> "child"
  age < 20 -> "teenager"
  age < 60 -> "adult"
  true -> "senior"
end
```

### Using Structs

```elixir
defmodule User do
  defstruct [:name, :email, age: 0, active: true]

  def new(name, email) do
    %User{name: name, email: email}
  end

  def activate(%User{} = user) do
    %{user | active: true}
  end
end

# Usage
user = %User{name: "Alice", email: "alice@example.com"}
user = User.activate(user)

# Pattern matching
def greet(%User{name: name}), do: "Hello, #{name}!"
```

### Protocols

```elixir
# Define protocol
defprotocol Serializable do
  def serialize(data)
end

# Implement for different types
defimpl Serializable, for: Map do
  def serialize(map), do: Jason.encode!(map)
end

defimpl Serializable, for: List do
  def serialize(list), do: Jason.encode!(list)
end

# Usage
Serializable.serialize(%{name: "Alice"})
Serializable.serialize([1, 2, 3])
```

### Use Directive

```elixir
# Define reusable behavior
defmodule MyMacro do
  defmacro __using__(opts) do
    quote do
      import MyMacro
      @opts unquote(opts)

      def common_function do
        "This is common"
      end
    end
  end
end

# Use it
defmodule MyModule do
  use MyMacro, option: :value
end
```

---

## Enum and Stream

### Enum Module (Eager)

```elixir
# Map
Enum.map([1, 2, 3], fn x -> x * 2 end)  # [2, 4, 6]

# Filter
Enum.filter([1, 2, 3, 4], fn x -> rem(x, 2) == 0 end)  # [2, 4]

# Reduce
Enum.reduce([1, 2, 3], 0, fn x, acc -> x + acc end)  # 6

# Find
Enum.find([1, 2, 3], fn x -> x > 2 end)  # 3

# Chaining
[1, 2, 3, 4, 5]
|> Enum.filter(&(rem(&1, 2) == 0))
|> Enum.map(&(&1 * 2))
# [4, 8]

# Common functions
Enum.any?([1, 2, 3], &(&1 > 2))      # true
Enum.all?([1, 2, 3], &(&1 > 0))      # true
Enum.count([1, 2, 3])                # 3
Enum.sum([1, 2, 3])                  # 6
Enum.max([1, 2, 3])                  # 3
Enum.min([1, 2, 3])                  # 1
Enum.sort([3, 1, 2])                 # [1, 2, 3]
Enum.uniq([1, 2, 2, 3])              # [1, 2, 3]
Enum.zip([1, 2], [:a, :b])           # [{1, :a}, {2, :b}]
```

### Stream Module (Lazy)

```elixir
# Lazy operations (only computed when needed)
stream = Stream.map([1, 2, 3], fn x -> x * 2 end)
Enum.to_list(stream)  # [2, 4, 6]

# Infinite streams
Stream.iterate(0, &(&1 + 1))
|> Stream.take(5)
|> Enum.to_list()
# [0, 1, 2, 3, 4]

# File streaming (memory efficient)
File.stream!("large_file.txt")
|> Stream.map(&String.trim/1)
|> Stream.filter(&(&1 != ""))
|> Enum.count()
```

---

## Error Handling

### Try-Rescue

```elixir
try do
  raise "Error!"
rescue
  e in RuntimeError -> "Caught runtime error: #{e.message}"
  e -> "Caught: #{inspect(e)}"
after
  cleanup()
end
```

### Try-Catch

```elixir
try do
  throw(:error)
catch
  :error -> "Caught thrown value"
  :exit, _ -> "Caught exit"
end
```

### Result Tuples

```elixir
# Preferred pattern in Elixir
def divide(a, b) when b != 0, do: {:ok, a / b}
def divide(_, 0), do: {:error, :division_by_zero}

# Usage
case divide(10, 2) do
  {:ok, result} -> "Result: #{result}"
  {:error, reason} -> "Error: #{reason}"
end

# With pattern matching
{:ok, result} = divide(10, 2)  # Raises if not :ok
```

---

## Troubleshooting

### Match Error

**Problem:** `MatchError: no match of right hand side value`

```elixir
# Cause: Pattern doesn't match
{:ok, value} = {:error, :not_found}  # MatchError!

# Fix: Use case or handle both patterns
case result do
  {:ok, value} -> value
  {:error, reason} -> handle_error(reason)
end
```

### Undefined Function

**Problem:** `UndefinedFunctionError`

```elixir
# Cause: Function not defined or not imported
String.upcase("hello")  # OK
upcase("hello")         # UndefinedFunctionError

# Fix: Import or use full module name
import String
upcase("hello")  # OK
```

### Process Crashes

**Problem:** Process dies unexpectedly

```elixir
# Use supervisors to restart failed processes
children = [
  {MyWorker, restart: :permanent}
]

Supervisor.start_link(children, strategy: :one_for_one)
```

### Genserver Timeout

**Problem:** GenServer call times out

```elixir
# Default timeout is 5 seconds
GenServer.call(server, :slow_operation)  # May timeout

# Increase timeout
GenServer.call(server, :slow_operation, 30_000)  # 30 seconds

# Or use cast for async operations
GenServer.cast(server, :slow_operation)
```

---

## References

- [Elixir Language](https://elixir-lang.org/)
- [Elixir School](https://elixirschool.com/)
- [Phoenix Framework](https://www.phoenixframework.org/)
- [Hex Package Manager](https://hex.pm/)
- [Elixir Forum](https://elixirforum.com/)
- Specialized skills: `lang-elixir-phoenix-dev`, `lang-elixir-otp-dev`, `lang-elixir-ecto-dev`
