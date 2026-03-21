---
name: convert-python-elixir
description: Convert Python code to Elixir. Use when migrating Python projects to Elixir, translating Python patterns to idiomatic Elixir, refactoring Python codebases into BEAM/OTP, or building Elixir services from Python prototypes. Extends meta-convert-dev with Python-to-Elixir specific patterns covering all 10 pillars including FFI and Dev Workflow.
---

# Convert Python to Elixir

Convert Python code to idiomatic Elixir. This skill extends `meta-convert-dev` with Python-to-Elixir specific type mappings, idiom translations, OTP/BEAM concurrency patterns, and comprehensive coverage of all 10 conversion pillars.

## This Skill Extends

- `meta-convert-dev` - Foundational conversion patterns (APTV workflow, testing strategies)

## This Skill Adds

- **Type mappings**: Python types → Elixir types (dynamic → dynamic with pattern matching)
- **Idiom translations**: Python patterns → idiomatic Elixir functional patterns
- **Error handling**: try/except → with/case, {:ok, _}/{:error, _} tuples
- **Concurrency**: threading/asyncio → GenServer, Task, Agent, OTP supervision
- **Module system**: packages/modules → nested Elixir modules
- **Metaprogramming**: decorators → macros, behaviours
- **Serialization**: Pydantic/dataclasses → Ecto schemas, Jason
- **Build/Deps**: pip/poetry → mix, hex
- **Dev Workflow**: Python REPL → IEx, Mix tasks, hot code reloading
- **FFI/Interop**: C extensions/ctypes → NIFs, Ports, Rustler

## When to Use This Conversion

- **Migrating to BEAM** for fault tolerance and soft real-time capabilities
- **Scaling concurrent systems** - Python GIL limitations → true parallelism
- **Building distributed systems** - Leveraging Erlang/OTP battle-tested patterns
- **Hot code reloading** - Production systems requiring zero-downtime updates
- **Functional refactoring** - Moving from OOP/imperative to functional paradigm
- **Phoenix web apps** - Python web services → Phoenix framework
- **Low-latency systems** - Predictable performance without GC pauses

## When NOT to Use This Conversion

- **Data science pipelines** - Python ecosystem (NumPy, Pandas, scikit-learn) is unmatched
- **Machine learning** - Keep Python for TensorFlow, PyTorch, etc.
- **Quick prototypes** - Python is faster for throwaway scripts
- **Heavy C integration** - Python's C API is more mature than NIFs
- **Team expertise** - Team unfamiliar with functional programming or Erlang VM

---

## Quick Reference

| Python | Elixir | Notes |
|--------|--------|-------|
| `None` | `nil` | Both falsy, but Elixir has explicit pattern matching |
| `True`/`False` | `true`/`false` | Atoms in Elixir |
| `dict` | `%{}` (map) | Immutable in Elixir |
| `list` | `[]` (list) | Immutable, linked list in Elixir |
| `tuple` | `{}` (tuple) | Immutable in both |
| `set` | `MapSet` | Module-based in Elixir |
| `def function():` | `def function do ... end` | Elixir uses `do/end` blocks |
| `class MyClass:` | `defmodule MyModule do` | Modules instead of classes |
| `try/except` | `try/rescue` or `with/case` | Prefer pattern matching |
| `@decorator` | `@behaviour` or macros | Different metaprogramming model |
| `threading.Thread` | `Task` or `spawn` | Lightweight BEAM processes |
| `asyncio` | `Task.async` or GenServer | Actor model, not event loop |
| `if __name__ == "__main__":` | Mix tasks | Build tool integration |

---

## APTV Workflow for Python → Elixir

Every Python-to-Elixir conversion follows: **Analyze → Plan → Transform → Validate**

### 1. ANALYZE Phase

**Understand the Python codebase:**

```python
# Analyze Python structure
project/
├── src/
│   ├── __init__.py
│   ├── models.py       # Dataclasses, Pydantic models
│   ├── services.py     # Business logic
│   ├── api.py          # Flask/FastAPI endpoints
│   └── utils.py        # Helper functions
├── tests/
│   └── test_services.py
├── requirements.txt
└── pyproject.toml
```

**Key analysis points:**

1. **Identify concurrency patterns** - threading, asyncio, multiprocessing
2. **Map class hierarchies** - OOP → functional decomposition
3. **Note mutable state** - Global variables, class attributes
4. **Find decorators** - @property, @staticmethod, custom decorators
5. **Catalog dependencies** - requests, pydantic, sqlalchemy, etc.
6. **Error handling style** - Exception hierarchy, custom errors
7. **Entry points** - CLI scripts, web servers, workers

### 2. PLAN Phase

**Design Elixir architecture:**

```elixir
# Planned Elixir structure
my_app/
├── lib/
│   ├── my_app/
│   │   ├── models/       # Ecto schemas
│   │   ├── services/     # Business logic modules
│   │   ├── api/          # Phoenix controllers
│   │   └── utils.ex      # Helper modules
│   ├── my_app.ex         # Application entry point
│   └── my_app_web/       # Phoenix web layer
├── test/
│   └── my_app/
│       └── services_test.exs
├── mix.exs
└── config/
```

**Create mapping tables:**

| Python Component | Elixir Component | Strategy |
|------------------|------------------|----------|
| Pydantic models | Ecto schemas | Validation → changeset |
| Flask routes | Phoenix routes | Controllers + views |
| threading.Thread | Task.async | Supervised tasks |
| SQLAlchemy | Ecto | Query DSL, schemas |
| pytest fixtures | ExUnit setup callbacks | Test context |
| @decorator | Macro or behaviour | Context-dependent |
| Global state | GenServer or Agent | Process-based state |

### 3. TRANSFORM Phase

**Convert systematically:**

1. **Module structure first** - Create Elixir module hierarchy
2. **Data types** - Pydantic/dataclasses → Ecto schemas or structs
3. **Pure functions** - Easiest conversions, no side effects
4. **Stateful components** - Classes → GenServers or Agents
5. **Concurrency** - async/threading → Task/GenServer/Supervisor
6. **Error handling** - Exceptions → tagged tuples and pattern matching
7. **Tests** - pytest → ExUnit with doctests

**Golden Rule**: Write **idiomatic Elixir**, not "Python in Elixir syntax"

### 4. VALIDATE Phase

1. **Functional equivalence** - Same inputs → same outputs
2. **Property-based tests** - Use StreamData for edge cases
3. **Concurrent behavior** - Test supervision trees, process isolation
4. **Performance** - Benchmark against Python (expect gains in concurrency)
5. **Integration tests** - External dependencies (databases, APIs)

---

## 10 Pillars of Python → Elixir Conversion

## Pillar 1: Module System

### Python Package Structure

```python
# my_package/__init__.py
from .models import User, Order
from .services import UserService

__all__ = ['User', 'Order', 'UserService']

# my_package/models.py
class User:
    def __init__(self, name: str, email: str):
        self.name = name
        self.email = email

# my_package/services.py
from .models import User

class UserService:
    def create_user(self, name: str, email: str) -> User:
        return User(name, email)
```

### Elixir Module Structure

```elixir
# lib/my_app/models/user.ex
defmodule MyApp.Models.User do
  defstruct [:name, :email]

  @type t :: %__MODULE__{
    name: String.t(),
    email: String.t()
  }
end

# lib/my_app/models/order.ex
defmodule MyApp.Models.Order do
  defstruct [:id, :user_id, :total]
end

# lib/my_app/services/user_service.ex
defmodule MyApp.Services.UserService do
  alias MyApp.Models.User

  @spec create_user(String.t(), String.t()) :: User.t()
  def create_user(name, email) do
    %User{name: name, email: email}
  end
end

# lib/my_app.ex (Application entry point)
defmodule MyApp do
  @moduledoc """
  MyApp application entry point.
  """

  alias MyApp.Models.{User, Order}
  alias MyApp.Services.UserService

  # Re-export commonly used modules
  defdelegate create_user(name, email), to: UserService
end
```

**Key Differences:**

| Python | Elixir | Notes |
|--------|--------|-------|
| `__init__.py` re-exports | Main module with `alias` and `defdelegate` | Explicit module structure |
| `import` statement | `alias`, `import`, `require` | Elixir distinguishes module vs macro import |
| Relative imports | Fully qualified names | `MyApp.Models.User` is explicit |
| `__all__` | Module docs + public functions | Only `def` is public, `defp` is private |

### Import Patterns

```python
# Python imports
from my_package.models import User
from my_package.services import UserService
import my_package.utils as utils
```

```elixir
# Elixir aliases
alias MyApp.Models.User
alias MyApp.Services.UserService
alias MyApp.Utils, as: Utils

# Or group aliases
alias MyApp.{Models.User, Services.UserService}
```

---

## Pillar 2: Error Handling

### Python Exception Model

```python
# Python: Exception-based
class UserNotFoundError(Exception):
    def __init__(self, user_id: int):
        self.user_id = user_id
        super().__init__(f"User {user_id} not found")

def get_user(user_id: int) -> dict:
    try:
        user = database.find_user(user_id)
        if user is None:
            raise UserNotFoundError(user_id)
        return user
    except DatabaseError as e:
        logger.error(f"Database error: {e}")
        raise
    finally:
        database.close()
```

### Elixir Tagged Tuple Model

```elixir
# Elixir: Tagged tuples with pattern matching
defmodule MyApp.Users do
  @type user :: %{id: integer(), name: String.t()}
  @type error_reason :: :not_found | :database_error | :invalid_id

  @spec get_user(integer()) :: {:ok, user()} | {:error, error_reason()}
  def get_user(user_id) when is_integer(user_id) and user_id > 0 do
    case Database.find_user(user_id) do
      {:ok, nil} ->
        {:error, :not_found}

      {:ok, user} ->
        {:ok, user}

      {:error, reason} ->
        Logger.error("Database error: #{inspect(reason)}")
        {:error, :database_error}
    end
  end

  def get_user(_invalid_id), do: {:error, :invalid_id}
end
```

### Using `with` for Error Chains

```python
# Python: nested try/except
def process_order(order_id: int) -> dict:
    try:
        order = get_order(order_id)
        user = get_user(order['user_id'])
        payment = process_payment(order['total'])
        return {'order': order, 'user': user, 'payment': payment}
    except UserNotFoundError:
        raise OrderProcessingError("User not found")
    except PaymentError:
        raise OrderProcessingError("Payment failed")
```

```elixir
# Elixir: with construct for happy path
defmodule MyApp.Orders do
  def process_order(order_id) do
    with {:ok, order} <- get_order(order_id),
         {:ok, user} <- get_user(order.user_id),
         {:ok, payment} <- process_payment(order.total) do
      {:ok, %{order: order, user: user, payment: payment}}
    else
      {:error, :not_found} ->
        {:error, :user_not_found}

      {:error, :payment_failed} = error ->
        Logger.error("Payment failed for order #{order_id}")
        error

      error ->
        {:error, {:processing_failed, error}}
    end
  end
end
```

### Error Translation Table

| Python Pattern | Elixir Pattern | Use Case |
|----------------|----------------|----------|
| `raise ValueError` | `{:error, :invalid_value}` | Input validation |
| `raise CustomError` | `{:error, :custom_reason}` | Domain errors |
| `try/except/finally` | `try/rescue/after` (rare) | Only for exceptional cases |
| `assert condition` | `unless condition, do: {:error, :assertion_failed}` | Guards or pattern matching |
| `if error: return None` | `{:error, reason}` tuple | Explicit error return |
| Exception hierarchy | Atom taxonomy | `:db_error`, `:db_connection_error` |

### When to Use Exceptions in Elixir

```elixir
# Rare: Use raise for programmer errors (bugs)
def divide(_a, 0), do: raise ArgumentError, "cannot divide by zero"
def divide(a, b), do: a / b

# Preferred: Use tagged tuples for expected errors
def safe_divide(_a, 0), do: {:error, :division_by_zero}
def safe_divide(a, b), do: {:ok, a / b}

# Pattern matching at call site
case safe_divide(10, 2) do
  {:ok, result} -> IO.puts("Result: #{result}")
  {:error, :division_by_zero} -> IO.puts("Cannot divide by zero")
end
```

---

## Pillar 3: Concurrency Patterns

### Python Threading/Asyncio

```python
# Python: Threading
import threading
from queue import Queue

class Worker:
    def __init__(self):
        self.queue = Queue()
        self.thread = threading.Thread(target=self._run)
        self.running = True
        self.thread.start()

    def _run(self):
        while self.running:
            item = self.queue.get()
            self.process(item)
            self.queue.task_done()

    def process(self, item):
        print(f"Processing {item}")

    def submit(self, item):
        self.queue.put(item)

    def stop(self):
        self.running = False
        self.thread.join()

# Python: Asyncio
import asyncio

async def fetch_data(url: str) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

async def main():
    results = await asyncio.gather(
        fetch_data("http://api1.com"),
        fetch_data("http://api2.com"),
        fetch_data("http://api3.com")
    )
    return results

# Run
asyncio.run(main())
```

### Elixir GenServer + Task

```elixir
# Elixir: GenServer for stateful worker
defmodule MyApp.Worker do
  use GenServer

  # Client API
  def start_link(opts \\ []) do
    GenServer.start_link(__MODULE__, :ok, opts)
  end

  def submit(pid, item) do
    GenServer.cast(pid, {:process, item})
  end

  def stop(pid) do
    GenServer.stop(pid)
  end

  # Server callbacks
  @impl true
  def init(:ok) do
    {:ok, %{processed: 0}}
  end

  @impl true
  def handle_cast({:process, item}, state) do
    IO.puts("Processing #{inspect(item)}")
    {:noreply, %{state | processed: state.processed + 1}}
  end
end

# Elixir: Task for async operations
defmodule MyApp.Fetcher do
  def fetch_data(url) do
    # HTTPoison or Req for HTTP
    case HTTPoison.get(url) do
      {:ok, %{body: body}} -> Jason.decode(body)
      error -> error
    end
  end

  def fetch_all(urls) do
    urls
    |> Enum.map(&Task.async(fn -> fetch_data(&1) end))
    |> Enum.map(&Task.await/1)
  end
end

# Usage
urls = ["http://api1.com", "http://api2.com", "http://api3.com"]
results = MyApp.Fetcher.fetch_all(urls)
```

### Supervision Trees

```python
# Python: Manual process management
import signal
import sys

workers = []

def shutdown_handler(signum, frame):
    for worker in workers:
        worker.stop()
    sys.exit(0)

signal.signal(signal.SIGTERM, shutdown_handler)
signal.signal(signal.SIGINT, shutdown_handler)

# Start workers
for i in range(5):
    worker = Worker()
    workers.append(worker)
```

```elixir
# Elixir: Supervisor with automatic restart
defmodule MyApp.Application do
  use Application

  @impl true
  def start(_type, _args) do
    children = [
      # Workers are supervised - they restart on crash
      {MyApp.Worker, name: Worker1},
      {MyApp.Worker, name: Worker2},
      {MyApp.Worker, name: Worker3},

      # Dynamic supervisor for on-demand workers
      {DynamicSupervisor, name: MyApp.DynamicWorkers, strategy: :one_for_one}
    ]

    opts = [strategy: :one_for_one, name: MyApp.Supervisor]
    Supervisor.start_link(children, opts)
  end
end

# Dynamically start workers
{:ok, pid} = DynamicSupervisor.start_child(
  MyApp.DynamicWorkers,
  {MyApp.Worker, []}
)
```

### Concurrency Comparison

| Python Pattern | Elixir Pattern | Notes |
|----------------|----------------|-------|
| `threading.Thread(target=fn)` | `spawn(fn)` or `Task.start` | Elixir processes are lightweight |
| `threading.Lock` | GenServer state | Message passing eliminates locks |
| `queue.Queue` | GenServer or Agent | Built-in message queues per process |
| `asyncio.gather()` | `Task.async_stream` | Parallel execution with backpressure |
| `concurrent.futures.ThreadPoolExecutor` | `Task.Supervisor` | Supervised task pools |
| Global `threading.local()` | Process dictionary | `Process.put/get` (use sparingly) |
| `multiprocessing.Process` | Node-level distribution | BEAM distribution across nodes |

---

## Pillar 4: Metaprogramming

### Python Decorators

```python
# Python: Decorator pattern
from functools import wraps
import time

def timeit(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        print(f"{func.__name__} took {duration:.2f}s")
        return result
    return wrapper

@timeit
def expensive_operation(n: int) -> int:
    time.sleep(n)
    return n * 2

# Python: Class decorators
def singleton(cls):
    instances = {}
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return get_instance

@singleton
class Database:
    def __init__(self):
        self.connection = "connected"
```

### Elixir Macros

```elixir
# Elixir: Macro for compile-time code generation
defmodule MyApp.Macros do
  defmacro timeit(do: block) do
    quote do
      start = System.monotonic_time(:millisecond)
      result = unquote(block)
      duration = System.monotonic_time(:millisecond) - start
      IO.puts("Operation took #{duration}ms")
      result
    end
  end
end

# Usage
defmodule MyApp.Example do
  require MyApp.Macros
  import MyApp.Macros

  def expensive_operation(n) do
    timeit do
      Process.sleep(n * 1000)
      n * 2
    end
  end
end
```

### Behaviours (Interface Pattern)

```python
# Python: Abstract base class
from abc import ABC, abstractmethod

class Storage(ABC):
    @abstractmethod
    def save(self, key: str, value: any) -> None:
        pass

    @abstractmethod
    def load(self, key: str) -> any:
        pass

class FileStorage(Storage):
    def save(self, key: str, value: any) -> None:
        with open(f"{key}.txt", "w") as f:
            f.write(str(value))

    def load(self, key: str) -> any:
        with open(f"{key}.txt", "r") as f:
            return f.read()
```

```elixir
# Elixir: Behaviour (compile-time contract)
defmodule MyApp.Storage do
  @callback save(key :: String.t(), value :: term()) :: :ok | {:error, term()}
  @callback load(key :: String.t()) :: {:ok, term()} | {:error, term()}
end

defmodule MyApp.FileStorage do
  @behaviour MyApp.Storage

  @impl true
  def save(key, value) do
    case File.write("#{key}.txt", inspect(value)) do
      :ok -> :ok
      error -> error
    end
  end

  @impl true
  def load(key) do
    case File.read("#{key}.txt") do
      {:ok, content} -> {:ok, content}
      error -> error
    end
  end
end

# Compile-time check: warns if callbacks not implemented
```

### Metaprogramming Comparison

| Python Pattern | Elixir Pattern | Use Case |
|----------------|----------------|----------|
| `@decorator` | Macro with `do` block | Code transformation |
| `@property` | `defstruct` with defaults | Data access |
| `@staticmethod` | Module function | Stateless operations |
| `@classmethod` | Module function with pattern matching | Factory patterns |
| Abstract base class | `@behaviour` | Interface contracts |
| Metaclass | Macro generating modules | DSL creation |
| `__getattr__` | `Access` behaviour | Dynamic attribute access |

---

## Pillar 5: Zero Values and Defaults

### Python None and Mutable Defaults

```python
# Python: None as sentinel
def find_user(user_id: int) -> dict | None:
    user = db.query(user_id)
    return user if user else None

# Python: Mutable default arguments (anti-pattern!)
def add_item(item: str, items: list = []):  # WRONG!
    items.append(item)
    return items

# Correct version
def add_item(item: str, items: list | None = None) -> list:
    if items is None:
        items = []
    items.append(item)
    return items

# Python: Dataclass defaults
from dataclasses import dataclass, field

@dataclass
class User:
    name: str
    email: str
    active: bool = True
    tags: list[str] = field(default_factory=list)  # Avoid mutable default
```

### Elixir nil and Immutable Defaults

```elixir
# Elixir: nil in pattern matching
defmodule MyApp.Users do
  def find_user(user_id) do
    case Repo.get(User, user_id) do
      nil -> {:error, :not_found}
      user -> {:ok, user}
    end
  end

  # Alternative: use Option-like pattern
  def find_user_option(user_id) do
    user = Repo.get(User, user_id)
    if user, do: {:ok, user}, else: {:error, :not_found}
  end
end

# Elixir: Struct defaults (immutable)
defmodule MyApp.User do
  defstruct name: nil,
            email: nil,
            active: true,
            tags: []  # Safe: lists are immutable

  @type t :: %__MODULE__{
    name: String.t() | nil,
    email: String.t() | nil,
    active: boolean(),
    tags: [String.t()]
  }
end

# Usage
user = %MyApp.User{name: "Alice", email: "alice@example.com"}
# user.tags is [] by default, new instance each time

# Function defaults with keyword lists
defmodule MyApp.Query do
  def search(term, opts \\ []) do
    limit = Keyword.get(opts, :limit, 10)
    offset = Keyword.get(opts, :offset, 0)
    # ...
  end
end

# Usage
MyApp.Query.search("elixir")
MyApp.Query.search("elixir", limit: 20)
MyApp.Query.search("elixir", limit: 20, offset: 10)
```

### Default Value Patterns

| Python Pattern | Elixir Pattern | Notes |
|----------------|----------------|-------|
| `value = None` | `value = nil` | Both represent absence |
| `if value is None:` | `if is_nil(value)` or pattern match | Explicit nil check |
| `value or default` | `value \|\| default` | Falsy semantics differ |
| `value if value else default` | `value \|\| default` | Same as above |
| `dict.get(key, default)` | `Map.get(map, key, default)` | Dict/Map retrieval |
| `list.append(x)` mutates | `[x \| list]` or `list ++ [x]` | Immutable prepend/append |
| Mutable default args | Keyword list defaults | No mutable defaults issue |

---

## Pillar 6: Serialization and Validation

### Python Pydantic

```python
# Python: Pydantic models with validation
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime

class Address(BaseModel):
    street: str
    city: str
    zip_code: str = Field(pattern=r'^\d{5}$')

class User(BaseModel):
    id: int
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    age: int = Field(ge=0, le=150)
    address: Optional[Address] = None
    created_at: datetime = Field(default_factory=datetime.now)

    @field_validator('age')
    @classmethod
    def check_adult(cls, v: int) -> int:
        if v < 18:
            raise ValueError('Must be 18 or older')
        return v

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# Usage
user_data = {
    "id": 1,
    "name": "Alice",
    "email": "alice@example.com",
    "age": 25,
    "address": {
        "street": "123 Main St",
        "city": "NYC",
        "zip_code": "10001"
    }
}

user = User(**user_data)
json_str = user.model_dump_json()
```

### Elixir Ecto Schemas

```elixir
# Elixir: Ecto schemas with changesets
defmodule MyApp.Address do
  use Ecto.Schema
  import Ecto.Changeset

  embedded_schema do
    field :street, :string
    field :city, :string
    field :zip_code, :string
  end

  def changeset(address, attrs) do
    address
    |> cast(attrs, [:street, :city, :zip_code])
    |> validate_required([:street, :city, :zip_code])
    |> validate_format(:zip_code, ~r/^\d{5}$/)
  end
end

defmodule MyApp.User do
  use Ecto.Schema
  import Ecto.Changeset

  schema "users" do
    field :name, :string
    field :email, :string
    field :age, :integer
    embeds_one :address, MyApp.Address

    timestamps()  # created_at, updated_at
  end

  def changeset(user, attrs) do
    user
    |> cast(attrs, [:name, :email, :age])
    |> cast_embed(:address)
    |> validate_required([:name, :email, :age])
    |> validate_length(:name, min: 1, max: 100)
    |> validate_format(:email, ~r/@/)
    |> validate_number(:age, greater_than_or_equal_to: 0, less_than_or_equal_to: 150)
    |> validate_adult()
  end

  defp validate_adult(changeset) do
    validate_change(changeset, :age, fn :age, age ->
      if age < 18 do
        [age: "must be 18 or older"]
      else
        []
      end
    end)
  end
end

# Usage
user_attrs = %{
  "name" => "Alice",
  "email" => "alice@example.com",
  "age" => 25,
  "address" => %{
    "street" => "123 Main St",
    "city" => "NYC",
    "zip_code" => "10001"
  }
}

changeset = MyApp.User.changeset(%MyApp.User{}, user_attrs)

case changeset do
  %{valid?: true} ->
    # Insert into database
    Repo.insert(changeset)

  %{valid?: false} ->
    # Get errors
    errors = Ecto.Changeset.traverse_errors(changeset, fn {msg, _opts} -> msg end)
end

# JSON encoding (with Jason)
user = %MyApp.User{name: "Alice", email: "alice@example.com", age: 25}
json = Jason.encode!(user)
```

### JSON Serialization Without Ecto

```elixir
# Elixir: Plain structs with Jason
defmodule MyApp.User do
  @derive {Jason.Encoder, only: [:name, :email, :age]}
  defstruct [:name, :email, :age, :internal_field]
end

user = %MyApp.User{name: "Alice", email: "alice@example.com", age: 25}
Jason.encode!(user)
# => {"name":"Alice","email":"alice@example.com","age":25}

# Custom encoding
defimpl Jason.Encoder, for: MyApp.User do
  def encode(user, opts) do
    Jason.Encode.map(%{
      name: user.name,
      email: user.email,
      age: user.age,
      is_adult: user.age >= 18
    }, opts)
  end
end
```

### Serialization Comparison

| Python | Elixir | Notes |
|--------|--------|-------|
| Pydantic `BaseModel` | Ecto schema + changeset | Validation via changesets |
| `@field_validator` | `validate_change/3` | Custom validation |
| `Field(pattern=...)` | `validate_format/3` | Regex validation |
| `model_dump()` | `Jason.encode!()` | JSON serialization |
| `model_validate()` | `changeset.valid?` | Validation check |
| `EmailStr` type | `validate_format(:email, ~r/@/)` | Email validation |
| Dataclass `field(default_factory=...)` | Ecto `timestamps()` | Auto fields |

---

## Pillar 7: Build System and Dependencies

### Python Package Management

```python
# pyproject.toml (Poetry)
[tool.poetry]
name = "my-app"
version = "0.1.0"
description = "My Python application"
authors = ["Your Name <you@example.com>"]

[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.104.0"
pydantic = "^2.5.0"
sqlalchemy = "^2.0.0"
requests = "^2.31.0"

[tool.poetry.dev-dependencies]
pytest = "^7.4.0"
black = "^23.11.0"
mypy = "^1.7.0"

# requirements.txt (pip)
fastapi==0.104.0
pydantic==2.5.0
sqlalchemy==2.0.0
requests==2.31.0

# setup.py
from setuptools import setup, find_packages

setup(
    name="my-app",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.104.0",
        "pydantic>=2.5.0",
    ],
)
```

### Elixir Mix Configuration

```elixir
# mix.exs
defmodule MyApp.MixProject do
  use Mix.Project

  def project do
    [
      app: :my_app,
      version: "0.1.0",
      elixir: "~> 1.15",
      start_permanent: Mix.env() == :prod,
      deps: deps(),

      # Aliases for common tasks
      aliases: aliases()
    ]
  end

  # Run "mix help compile.app" to learn about applications.
  def application do
    [
      extra_applications: [:logger],
      mod: {MyApp.Application, []}
    ]
  end

  # Run "mix help deps" to learn about dependencies.
  defp deps do
    [
      {:phoenix, "~> 1.7.0"},
      {:ecto_sql, "~> 3.10"},
      {:postgrex, ">= 0.0.0"},
      {:jason, "~> 1.4"},
      {:httpoison, "~> 2.2"},

      # Dev/test dependencies
      {:ex_doc, "~> 0.30", only: :dev, runtime: false},
      {:credo, "~> 1.7", only: [:dev, :test], runtime: false},
      {:dialyxir, "~> 1.4", only: [:dev], runtime: false}
    ]
  end

  defp aliases do
    [
      setup: ["deps.get", "ecto.setup"],
      "ecto.setup": ["ecto.create", "ecto.migrate", "run priv/repo/seeds.exs"],
      "ecto.reset": ["ecto.drop", "ecto.setup"],
      test: ["ecto.create --quiet", "ecto.migrate --quiet", "test"]
    ]
  end
end
```

### Dependency Management Comparison

| Python | Elixir | Notes |
|--------|--------|-------|
| `pip install package` | `mix deps.get` | Install dependencies |
| `poetry add package` | Edit `mix.exs`, run `mix deps.get` | Add dependency |
| `requirements.txt` | `mix.lock` | Lock file |
| `pyproject.toml` | `mix.exs` | Project config |
| `python -m venv` | N/A (not needed) | No virtual environments |
| `pip freeze` | `mix deps.tree` | Show dependency tree |
| PyPI | Hex.pm | Package registry |
| `python setup.py install` | `mix compile` | Build project |
| `python -m my_app` | `mix run` or `iex -S mix` | Run application |

### Common Package Mappings

| Python Package | Elixir Package | Purpose |
|----------------|----------------|---------|
| `requests` | `httpoison` or `req` | HTTP client |
| `flask` / `fastapi` | `phoenix` | Web framework |
| `sqlalchemy` | `ecto` | Database ORM |
| `pydantic` | `ecto` changesets | Validation |
| `pytest` | `ex_unit` | Testing |
| `celery` | GenServer + Task | Background jobs |
| `redis-py` | `redix` | Redis client |
| `psycopg2` | `postgrex` | PostgreSQL driver |
| `black` | `mix format` | Code formatter |
| `mypy` | `dialyzer` | Type checking |

---

## Pillar 8: Testing Strategy

### Python pytest

```python
# tests/test_users.py
import pytest
from my_app.services import UserService
from my_app.models import User

@pytest.fixture
def user_service():
    return UserService()

@pytest.fixture
def sample_user():
    return User(name="Alice", email="alice@example.com", age=25)

class TestUserService:
    def test_create_user(self, user_service):
        user = user_service.create_user("Bob", "bob@example.com")
        assert user.name == "Bob"
        assert user.email == "bob@example.com"

    def test_get_user_not_found(self, user_service):
        with pytest.raises(UserNotFoundError):
            user_service.get_user(999)

    @pytest.mark.parametrize("age,expected", [
        (17, False),
        (18, True),
        (25, True),
    ])
    def test_is_adult(self, age, expected):
        user = User(name="Test", email="test@example.com", age=age)
        assert user.is_adult() == expected
```

### Elixir ExUnit

```elixir
# test/my_app/services/user_service_test.exs
defmodule MyApp.Services.UserServiceTest do
  use ExUnit.Case, async: true

  alias MyApp.Services.UserService
  alias MyApp.Models.User

  # Setup runs before each test
  setup do
    user = %User{name: "Alice", email: "alice@example.com", age: 25}
    {:ok, user: user}
  end

  describe "create_user/2" do
    test "creates user with valid data" do
      user = UserService.create_user("Bob", "bob@example.com")
      assert user.name == "Bob"
      assert user.email == "bob@example.com"
    end

    test "returns error with invalid data" do
      assert {:error, _} = UserService.create_user("", "invalid")
    end
  end

  describe "get_user/1" do
    test "returns error when user not found" do
      assert {:error, :not_found} = UserService.get_user(999)
    end
  end

  # Doctest (tests in documentation)
  doctest MyApp.Services.UserService
end

# test/support/factory.ex (test data factory)
defmodule MyApp.Factory do
  def user_attrs(attrs \\ %{}) do
    Map.merge(%{
      name: "Test User",
      email: "test@example.com",
      age: 25
    }, attrs)
  end

  def build(:user, attrs \\ %{}) do
    struct(MyApp.User, user_attrs(attrs))
  end
end
```

### Property-Based Testing

```python
# Python: Hypothesis
from hypothesis import given, strategies as st

@given(st.integers(min_value=0, max_value=150))
def test_age_validation(age):
    user = User(name="Test", email="test@example.com", age=age)
    assert user.age >= 0
    assert user.age <= 150
```

```elixir
# Elixir: StreamData
defmodule MyApp.UserPropertyTest do
  use ExUnit.Case
  use ExUnitProperties

  property "age is always within valid range" do
    check all age <- integer(0..150),
              name <- string(:alphanumeric, min_length: 1),
              email <- string(:alphanumeric, min_length: 3) do
      user = %MyApp.User{name: name, email: email <> "@test.com", age: age}
      assert user.age >= 0
      assert user.age <= 150
    end
  end
end
```

### Testing Comparison

| Python | Elixir | Notes |
|--------|--------|-------|
| `@pytest.fixture` | `setup/1` callback | Test setup |
| `assert x == y` | `assert x == y` | Same syntax! |
| `pytest.raises(Error)` | `assert_raise Error, fn -> ... end` | Exception testing |
| `@pytest.mark.parametrize` | Multiple test functions or generators | Parameterized tests |
| `unittest.mock.patch` | `Mox` library | Mocking |
| Hypothesis | `StreamData` | Property-based testing |
| `pytest -k test_name` | `mix test test/path/file_test.exs:10` | Run specific test |
| `pytest --cov` | `mix test --cover` | Code coverage |

---

## Pillar 9: Dev Workflow and REPL

### Python REPL and Development

```python
# Python REPL
$ python
>>> from my_app.models import User
>>> user = User(name="Alice", email="alice@example.com", age=25)
>>> user.name
'Alice'
>>> dir(user)  # Introspection
[...list of attributes...]

# IPython for better REPL
$ ipython
In [1]: from my_app.services import UserService
In [2]: svc = UserService()
In [3]: svc.  # Tab completion

# Python scripts and entry points
# setup.py
entry_points={
    'console_scripts': [
        'my-app=my_app.cli:main',
    ],
}

# Running scripts
$ python -m my_appcli.migrate
```

### Elixir IEx and Development

```elixir
# Elixir IEx (Interactive Elixir)
$ iex -S mix
Erlang/OTP 26 [erts-14.1.1] ...

iex(1)> alias MyApp.Models.User
MyApp.Models.User

iex(2)> user = %User{name: "Alice", email: "alice@example.com", age: 25}
%MyApp.Models.User{name: "Alice", email: "alice@example.com", age: 25}

iex(3)> user.name
"Alice"

# IEx helpers
iex(4)> h Enum.map  # Documentation
iex(5)> i user      # Introspection
iex(6)> exports User  # List exported functions

# Recompile code without restarting IEx
iex(7)> recompile()

# IEx.pry for breakpoints
defmodule MyApp.Debug do
  def example(x) do
    require IEx
    IEx.pry()  # Breakpoint - drops into IEx
    x * 2
  end
end
```

### Mix Tasks (CLI Scripts)

```elixir
# lib/mix/tasks/migrate_users.ex
defmodule Mix.Tasks.MigrateUsers do
  use Mix.Task

  @shortdoc "Migrates users from old format to new"
  def run(args) do
    # Start the application
    Mix.Task.run("app.start")

    # Parse args
    {opts, _, _} = OptionParser.parse(args, switches: [dry_run: :boolean])

    if opts[:dry_run] do
      IO.puts("DRY RUN: No changes will be made")
    end

    # Run migration
    MyApp.UserMigration.run(opts)
  end
end

# Usage
$ mix migrate_users
$ mix migrate_users --dry-run
```

### Hot Code Reloading (Production!)

```elixir
# Elixir: Hot code reload in production
# 1. Build new release
$ mix release

# 2. Deploy new version to running system
$ bin/my_app upgrade 0.2.0

# The system upgrades WITHOUT downtime!
# Running processes automatically migrate to new code
```

### Dev Workflow Comparison

| Python | Elixir | Notes |
|--------|--------|-------|
| `python` REPL | `iex` REPL | Interactive shell |
| `ipython` | `iex` (built-in rich features) | Enhanced REPL |
| `dir(obj)` | `i(obj)` or `exports Module` | Introspection |
| `help(func)` | `h func` | Documentation |
| Import module, test | IEx + `recompile()` | Fast feedback loop |
| `python -m module` | `mix run -e "Module.func()"` | Run one-off code |
| `if __name__ == "__main__":` | Mix tasks | CLI entry points |
| Restart process for code changes | `recompile()` in IEx | Hot reload |
| Blue-green deploy | `mix release upgrade` | Zero-downtime deploy |
| Print debugging | `IO.inspect()` with labels | Debugging |
| `pdb.set_trace()` | `IEx.pry()` | Breakpoints |

---

## Pillar 10: FFI and Interoperability

### When to Use FFI for Gradual Migration

Python → Elixir migrations can be **incremental** using FFI:

1. **Keep Python code** that's working well (especially data science, ML)
2. **Migrate critical services** to Elixir (concurrency, fault tolerance)
3. **Use Ports or NIFs** to call Python from Elixir during transition

### Python C Extensions → Elixir NIFs/Ports

```python
# Python: C extension or ctypes
from ctypes import CDLL, c_int

lib = CDLL('./libmylib.so')
result = lib.my_function(c_int(42))
```

```elixir
# Elixir: NIF (Native Implemented Function)
defmodule MyApp.NIF do
  @on_load :load_nif

  def load_nif do
    :erlang.load_nif('./priv/mylib', 0)
  end

  # Stub - replaced by NIF implementation
  def my_function(_arg), do: raise "NIF not loaded"
end

# Usage
MyApp.NIF.my_function(42)
```

### Calling Python from Elixir (Ports)

```elixir
# Elixir: Call Python script via Port
defmodule MyApp.PythonBridge do
  def call_python(script, args) do
    port = Port.open({:spawn, "python3 #{script}"}, [:binary, :exit_status])

    send(port, {self(), {:command, Jason.encode!(args)}})

    receive do
      {^port, {:data, data}} ->
        Jason.decode!(data)

      {^port, {:exit_status, status}} when status != 0 ->
        {:error, :python_error}
    after
      5000 -> {:error, :timeout}
    end
  end
end

# Python script: my_script.py
import sys
import json

def main():
    args = json.loads(sys.stdin.read())
    result = process(args)
    print(json.dumps(result))

if __name__ == "__main__":
    main()

# Usage
MyApp.PythonBridge.call_python("my_script.py", %{data: [1, 2, 3]})
```

### Elixir ↔ Rust via Rustler (Recommended for Performance)

Instead of calling Python C extensions, rewrite in Rust and use Rustler:

```elixir
# mix.exs
defp deps do
  [
    {:rustler, "~> 0.30.0"}
  ]
end

# lib/my_app/native.ex
defmodule MyApp.Native do
  use Rustler, otp_app: :my_app, crate: "mynative"

  # Stubs - replaced by Rust implementation
  def add(_a, _b), do: :erlang.nif_error(:nif_not_loaded)
  def process_data(_data), do: :erlang.nif_error(:nif_not_loaded)
end
```

```rust
// native/mynative/src/lib.rs
#[rustler::nif]
fn add(a: i64, b: i64) -> i64 {
    a + b
}

#[rustler::nif]
fn process_data(data: Vec<i64>) -> Vec<i64> {
    data.iter().map(|x| x * 2).collect()
}

rustler::init!("Elixir.MyApp.Native", [add, process_data]);
```

### Gradual Migration Strategy with FFI

```
┌─────────────────────────────────────────────────────────────┐
│              GRADUAL PYTHON → ELIXIR MIGRATION              │
├─────────────────────────────────────────────────────────────┤
│  Phase 1: IDENTIFY BOUNDARIES                                │
│  • API layer: Migrate to Phoenix                             │
│  • Worker pools: Migrate to GenServer + Supervisor           │
│  • Keep: Data science, ML models in Python                   │
├─────────────────────────────────────────────────────────────┤
│  Phase 2: BUILD BRIDGE                                       │
│  • Expose Python as HTTP service or Port                     │
│  • Elixir calls Python for complex computation               │
│  • Test integration thoroughly                               │
├─────────────────────────────────────────────────────────────┤
│  Phase 3: MIGRATE INCREMENTALLY                              │
│  • Convert one module at a time                              │
│  • Run both Python and Elixir in parallel                    │
│  • Verify equivalence before switching                       │
├─────────────────────────────────────────────────────────────┤
│  Phase 4: OPTIMIZE                                           │
│  • Rewrite critical Python code in Rust (via Rustler)        │
│  • Remove Python dependencies as Elixir versions stabilize   │
│  • Keep Python for truly Python-specific tasks (ML, etc.)    │
└─────────────────────────────────────────────────────────────┘
```

### FFI Comparison

| Python Approach | Elixir Approach | Use Case |
|-----------------|-----------------|----------|
| ctypes | NIF (via Rustler preferred) | Call C/Rust code |
| C extension | Rustler (Rust NIF) | Performance-critical code |
| subprocess.run() | Port | Call external programs |
| Shared library | NIF or Port | Reuse existing C code |
| multiprocessing | BEAM distribution | Cross-node communication |

---

## Idiom Translation Patterns

### Pattern 1: List Comprehensions

```python
# Python
squares = [x**2 for x in range(10)]
evens = [x for x in range(10) if x % 2 == 0]
matrix = [[i+j for j in range(3)] for i in range(3)]
```

```elixir
# Elixir
squares = for x <- 0..9, do: x * x
evens = for x <- 0..9, rem(x, 2) == 0, do: x
matrix = for i <- 0..2, do: (for j <- 0..2, do: i + j)

# Or with Enum
squares = Enum.map(0..9, &(&1 * &1))
evens = Enum.filter(0..9, &(rem(&1, 2) == 0))
```

### Pattern 2: Dictionary Comprehensions

```python
# Python
word_lengths = {word: len(word) for word in ["hello", "world"]}
inverted = {v: k for k, v in original.items()}
```

```elixir
# Elixir
word_lengths = for word <- ["hello", "world"], into: %{}, do: {word, String.length(word)}

# Or with Enum
word_lengths = Map.new(["hello", "world"], fn word -> {word, String.length(word)} end)

inverted = Map.new(original, fn {k, v} -> {v, k} end)
```

### Pattern 3: Context Managers (with statement)

```python
# Python
with open("file.txt", "r") as f:
    content = f.read()
# File automatically closed

# Database transaction
with database.transaction():
    database.insert(record)
    database.update(other)
# Auto commit or rollback
```

```elixir
# Elixir: File is auto-closed
{:ok, content} = File.read("file.txt")

# Ecto transaction
Repo.transaction(fn ->
  Repo.insert(record)
  Repo.update(other)
end)
# Auto commit or rollback on error
```

### Pattern 4: Property Decorators

```python
# Python
class Circle:
    def __init__(self, radius):
        self._radius = radius

    @property
    def area(self):
        return 3.14159 * self._radius ** 2

    @property
    def diameter(self):
        return self._radius * 2
```

```elixir
# Elixir: Use structs with functions
defmodule Circle do
  defstruct [:radius]

  def area(%Circle{radius: r}), do: 3.14159 * r * r
  def diameter(%Circle{radius: r}), do: r * 2
end

# Usage
circle = %Circle{radius: 5}
Circle.area(circle)
Circle.diameter(circle)
```

### Pattern 5: Iteration with Index

```python
# Python
for i, value in enumerate(["a", "b", "c"]):
    print(f"{i}: {value}")

for name, age in zip(names, ages):
    print(f"{name} is {age}")
```

```elixir
# Elixir
["a", "b", "c"]
|> Enum.with_index()
|> Enum.each(fn {value, i} -> IO.puts("#{i}: #{value}") end)

Enum.zip(names, ages)
|> Enum.each(fn {name, age} -> IO.puts("#{name} is #{age}") end)
```

### Pattern 6: Default Arguments and Keyword Arguments

```python
# Python
def greet(name, greeting="Hello", punctuation="!"):
    return f"{greeting}, {name}{punctuation}"

greet("Alice")
greet("Bob", greeting="Hi")
greet("Charlie", punctuation=".")
```

```elixir
# Elixir
defmodule Greeter do
  def greet(name, opts \\ []) do
    greeting = Keyword.get(opts, :greeting, "Hello")
    punctuation = Keyword.get(opts, :punctuation, "!")
    "#{greeting}, #{name}#{punctuation}"
  end
end

Greeter.greet("Alice")
Greeter.greet("Bob", greeting: "Hi")
Greeter.greet("Charlie", punctuation: ".")
```

### Pattern 7: Error Propagation

```python
# Python
def process_data(file_path: str) -> dict:
    try:
        data = read_file(file_path)
        parsed = parse_data(data)
        validated = validate_data(parsed)
        return transform_data(validated)
    except FileNotFoundError:
        raise DataProcessingError("File not found")
    except ParseError as e:
        raise DataProcessingError(f"Parse failed: {e}")
```

```elixir
# Elixir: with construct
defmodule DataProcessor do
  def process_data(file_path) do
    with {:ok, data} <- read_file(file_path),
         {:ok, parsed} <- parse_data(data),
         {:ok, validated} <- validate_data(parsed),
         {:ok, transformed} <- transform_data(validated) do
      {:ok, transformed}
    else
      {:error, :enoent} ->
        {:error, :file_not_found}

      {:error, {:parse_error, reason}} ->
        {:error, {:parse_failed, reason}}

      error ->
        {:error, {:processing_failed, error}}
    end
  end
end
```

### Pattern 8: Class Methods and Static Methods

```python
# Python
class User:
    @classmethod
    def from_dict(cls, data: dict) -> "User":
        return cls(name=data['name'], email=data['email'])

    @staticmethod
    def validate_email(email: str) -> bool:
        return '@' in email
```

```elixir
# Elixir: All functions in modules
defmodule User do
  defstruct [:name, :email]

  # Factory function (like @classmethod)
  def from_map(data) do
    %User{
      name: Map.get(data, "name"),
      email: Map.get(data, "email")
    }
  end

  # Module function (like @staticmethod)
  def validate_email(email) do
    String.contains?(email, "@")
  end
end
```

---

## Common Pitfalls

### 1. Expecting Mutable State

```python
# Python: Mutable data
users = []
users.append({"name": "Alice"})
users[0]["age"] = 25  # Mutates in place
```

```elixir
# ❌ Can't mutate in Elixir
users = []
users = users ++ [%{name: "Alice"}]
# users = [%{name: "Alice"}]

# Can't do: users[0]["age"] = 25

# ✓ Create new version
users = List.update_at(users, 0, fn user -> Map.put(user, :age, 25) end)
```

### 2. Using Classes for Everything

```python
# Python: OOP pattern
class UserRepository:
    def __init__(self, db):
        self.db = db

    def find(self, id):
        return self.db.query(id)
```

```elixir
# ❌ Don't translate classes directly
defmodule UserRepository do
  defstruct [:db]

  def new(db), do: %UserRepository{db: db}
  def find(%UserRepository{db: db}, id), do: db.query(id)
end

# ✓ Use modules with dependency injection
defmodule UserRepository do
  def find(db, id), do: db.query(id)
end

# Or use GenServer for stateful repositories
defmodule UserRepository do
  use GenServer

  def start_link(db), do: GenServer.start_link(__MODULE__, db, name: __MODULE__)
  def find(id), do: GenServer.call(__MODULE__, {:find, id})

  def handle_call({:find, id}, _from, db) do
    {:reply, db.query(id), db}
  end
end
```

### 3. Blocking Operations in GenServer

```elixir
# ❌ Blocking GenServer with slow operation
defmodule SlowWorker do
  use GenServer

  def handle_call(:work, _from, state) do
    # Blocks GenServer for 10 seconds!
    Process.sleep(10_000)
    {:reply, :done, state}
  end
end

# ✓ Spawn task for slow work
defmodule FastWorker do
  use GenServer

  def handle_call(:work, from, state) do
    Task.start(fn ->
      Process.sleep(10_000)
      GenServer.reply(from, :done)
    end)
    {:noreply, state}
  end
end
```

### 4. Forgetting to Start Supervision Tree

```python
# Python: Direct instantiation
worker = Worker()
worker.start()
```

```elixir
# ❌ Spawning without supervision
pid = spawn(fn -> Worker.run() end)

# ✓ Use supervision
defmodule MyApp.Application do
  use Application

  def start(_type, _args) do
    children = [
      {MyApp.Worker, []}
    ]

    Supervisor.start_link(children, strategy: :one_for_one)
  end
end
```

### 5. Not Leveraging Pattern Matching

```python
# Python: Conditional logic
def handle_response(response):
    if response['status'] == 'ok':
        return response['data']
    elif response['status'] == 'error':
        raise Exception(response['message'])
    else:
        return None
```

```elixir
# ❌ Transliterated conditionally
def handle_response(response) do
  cond do
    response.status == :ok -> response.data
    response.status == :error -> raise response.message
    true -> nil
  end
end

# ✓ Use pattern matching
def handle_response({:ok, data}), do: data
def handle_response({:error, message}), do: raise message
def handle_response(_), do: nil
```

---

## Complete Example: Python → Elixir

### Python: Simple User Service

```python
# models.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    id: int
    name: str
    email: str
    active: bool = True

# repository.py
from typing import Optional, List

class UserRepository:
    def __init__(self):
        self.users: dict[int, User] = {}
        self.next_id = 1

    def create(self, name: str, email: str) -> User:
        user = User(id=self.next_id, name=name, email=email)
        self.users[self.next_id] = user
        self.next_id += 1
        return user

    def find(self, user_id: int) -> Optional[User]:
        return self.users.get(user_id)

    def all(self) -> List[User]:
        return list(self.users.values())

# service.py
class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def register_user(self, name: str, email: str) -> User:
        if not self.validate_email(email):
            raise ValueError("Invalid email")
        return self.repository.create(name, email)

    def get_user(self, user_id: int) -> User:
        user = self.repository.find(user_id)
        if user is None:
            raise UserNotFoundError(f"User {user_id} not found")
        return user

    @staticmethod
    def validate_email(email: str) -> bool:
        return '@' in email
```

### Elixir: Equivalent Service

```elixir
# lib/my_app/models/user.ex
defmodule MyApp.Models.User do
  @enforce_keys [:id, :name, :email]
  defstruct [:id, :name, :email, active: true]

  @type t :: %__MODULE__{
    id: pos_integer(),
    name: String.t(),
    email: String.t(),
    active: boolean()
  }
end

# lib/my_app/repositories/user_repository.ex
defmodule MyApp.Repositories.UserRepository do
  use GenServer
  alias MyApp.Models.User

  # Client API
  def start_link(opts \\ []) do
    GenServer.start_link(__MODULE__, :ok, Keyword.put_new(opts, :name, __MODULE__))
  end

  def create(name, email) do
    GenServer.call(__MODULE__, {:create, name, email})
  end

  def find(user_id) do
    GenServer.call(__MODULE__, {:find, user_id})
  end

  def all do
    GenServer.call(__MODULE__, :all)
  end

  # Server callbacks
  @impl true
  def init(:ok) do
    {:ok, %{users: %{}, next_id: 1}}
  end

  @impl true
  def handle_call({:create, name, email}, _from, %{users: users, next_id: id} = state) do
    user = %User{id: id, name: name, email: email}
    new_state = %{users: Map.put(users, id, user), next_id: id + 1}
    {:reply, {:ok, user}, new_state}
  end

  @impl true
  def handle_call({:find, user_id}, _from, %{users: users} = state) do
    result = case Map.get(users, user_id) do
      nil -> {:error, :not_found}
      user -> {:ok, user}
    end
    {:reply, result, state}
  end

  @impl true
  def handle_call(:all, _from, %{users: users} = state) do
    {:reply, Map.values(users), state}
  end
end

# lib/my_app/services/user_service.ex
defmodule MyApp.Services.UserService do
  alias MyApp.Repositories.UserRepository
  alias MyApp.Models.User

  @spec register_user(String.t(), String.t()) :: {:ok, User.t()} | {:error, atom()}
  def register_user(name, email) do
    with :ok <- validate_email(email),
         {:ok, user} <- UserRepository.create(name, email) do
      {:ok, user}
    else
      {:error, :invalid_email} -> {:error, :invalid_email}
      error -> error
    end
  end

  @spec get_user(pos_integer()) :: {:ok, User.t()} | {:error, atom()}
  def get_user(user_id) do
    UserRepository.find(user_id)
  end

  @spec validate_email(String.t()) :: :ok | {:error, :invalid_email}
  defp validate_email(email) do
    if String.contains?(email, "@") do
      :ok
    else
      {:error, :invalid_email}
    end
  end
end

# lib/my_app/application.ex
defmodule MyApp.Application do
  use Application

  @impl true
  def start(_type, _args) do
    children = [
      MyApp.Repositories.UserRepository
    ]

    opts = [strategy: :one_for_one, name: MyApp.Supervisor]
    Supervisor.start_link(children, opts)
  end
end
```

---

## Tooling and Resources

### Code Formatters

| Python | Elixir |
|--------|--------|
| `black` | `mix format` (built-in) |
| Configuration in `pyproject.toml` | Configuration in `.formatter.exs` |

### Static Analysis

| Python | Elixir |
|--------|--------|
| `mypy` (type checking) | `dialyzer` (type checking) |
| `pylint` | `credo` (code quality) |
| `flake8` | `mix compile --warnings-as-errors` |

### Documentation

| Python | Elixir |
|--------|--------|
| Docstrings | `@moduledoc` and `@doc` |
| Sphinx | ExDoc (built-in) |
| `"""triple quotes"""` | `"""triple quotes"""` (same!) |

### REPL/Interactive Development

| Python | Elixir |
|--------|--------|
| `python` or `ipython` | `iex` |
| `import module; reload(module)` | `recompile()` |
| `dir(obj)` | `i(obj)` |
| `help(func)` | `h func` |

---

## References

### Skills That Extend This Skill

- `convert-python-rust` - Python → Rust (different concurrency model)
- `convert-python-golang` - Python → Go (simpler than Elixir)

### Related Skills

- `lang-python-dev` - Python fundamentals
- `lang-elixir-dev` - Elixir fundamentals
- `patterns-concurrency-dev` - Cross-language concurrency patterns
- `patterns-serialization-dev` - Cross-language serialization
- `meta-convert-dev` - General conversion methodology

### External Resources

- [Elixir School](https://elixirschool.com/) - Comprehensive Elixir tutorials
- [Phoenix Framework Guides](https://hexdocs.pm/phoenix/) - Web development
- [Ecto Documentation](https://hexdocs.pm/ecto/) - Database layer
- [Programming Elixir](https://pragprog.com/titles/elixir16/) - Dave Thomas book
- [Designing Elixir Systems with OTP](https://pragprog.com/titles/jgotp/) - OTP patterns
